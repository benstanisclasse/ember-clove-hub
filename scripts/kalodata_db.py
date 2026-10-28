"""Local Kalodata database: every raw API response in research/kalodata/raw/ loaded into one SQLite file.

Each response becomes one row in `pulls` (date pulled, endpoint, filters, date range) plus its records in a typed
table (products, videos, product_details, categories, comment_insights). Every record also keeps its full JSON in
`raw_json`, so fields we don't have columns for aren't lost. Loading is idempotent: a file is only loaded once.

Usage:
  python -I scripts/kalodata_db.py load      load any raw files not yet in the database
  python -I scripts/kalodata_db.py stats     row counts per table and pull date
DB: research/kalodata/kalodata.db
"""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hub_env  # noqa: E402

ROOT = hub_env.HUB_ROOT / "research" / "kalodata"
DB = ROOT / "kalodata.db"

TABLES = {
    "products": ["product_id", "product_name", "revenue", "sales_volumn", "unit_price", "revenue_growth_rate",
                 "commission_rate", "live_revenue", "video_revenue", "showcase_revenue", "launch_date",
                 "seller_id", "seller_name", "sku_count"],
    "videos": ["video_id", "video_title", "belonged_creator_id", "belonged_creator_handle", "revenue", "views",
               "revenue_growth_rate", "ads_roas", "ad", "ai_video", "digg_count", "share_count", "comment_count",
               "ad_revenue_ratio", "ad_view_ratio", "publish_date"],
    "product_details": ["product_id", "product_name", "product_shop_id", "pri_cate_id", "sec_cate_id", "ter_cate_id",
                        "min_price", "max_price", "unit_price", "revenue", "video_revenue", "live_revenue",
                        "shopping_mall_revenue", "sales_volumn", "creator_number", "video_number", "live_number",
                        "product_review_count", "commission_rate", "delivery_type", "launch_date", "revenue_trend"],
    "categories": ["category_id", "category_name", "rank", "revenue", "sale", "revenue_growth_rate",
                   "top3_shop_revenue_ratio", "average_revenue"],
    "comment_insights": ["product_id", "comment_summary", "pain_points", "positive_points", "usage_scenarios"],
}
# Raw files written before the endpoint path was stored: infer it from the file name.
PREFIX_ENDPOINT = [("category_", "tiktok/category/rank"), ("products_", "tiktok/product/rank"),
                   ("videos_", "tiktok/video/rank"), ("detail_", "tiktok/product/detail"),
                   ("comments_", "tiktok/product/comment/insight"), ("balance", "credit/balance")]
ENDPOINT_TABLE = {"tiktok/product/rank": "products", "tiktok/video/rank": "videos",
                  "tiktok/product/detail": "product_details", "tiktok/category/rank": "categories",
                  "tiktok/product/comment/insight": "comment_insights", "tiktok/video/detail": "videos"}


def connect():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS pulls (
        pull_id INTEGER PRIMARY KEY, file TEXT UNIQUE, pulled_on TEXT, name TEXT, endpoint TEXT,
        region TEXT, date_range TEXT, filters TEXT, http_status INTEGER, success INTEGER, n_records INTEGER)""")
    for table, cols in TABLES.items():
        extra = ", category_level INTEGER" if table == "categories" else ""
        extra += ", product_filter TEXT" if table == "videos" else ""
        con.execute(f"CREATE TABLE IF NOT EXISTS {table} (pull_id INTEGER, position INTEGER, "
                    + ", ".join(f"{c}" for c in cols) + extra + ", raw_json TEXT)")
        con.execute(f"CREATE INDEX IF NOT EXISTS ix_{table}_pull ON {table}(pull_id)")
    for table, key in (("products", "product_id"), ("videos", "video_id"), ("product_details", "product_id")):
        con.execute(f"CREATE INDEX IF NOT EXISTS ix_{table}_key ON {table}({key})")
    return con


def _cell(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v


def ingest_file(path, con=None):
    path = Path(path)
    own = con is None
    con = con or connect()
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if con.execute("SELECT 1 FROM pulls WHERE file = ?", (rel,)).fetchone():
        return 0
    doc = json.loads(path.read_text(encoding="utf-8"))
    req, body = doc.get("request") or {}, doc.get("response") or {}
    endpoint = doc.get("path") or next((e for p, e in PREFIX_ENDPOINT if path.stem.startswith(p)), "unknown")
    data = body.get("data")
    records = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
    table = ENDPOINT_TABLE.get(endpoint)
    filters = {k: v for k, v in req.items() if k not in ("region", "language", "currency", "date_range")}
    cur = con.execute("INSERT INTO pulls (file, pulled_on, name, endpoint, region, date_range, filters, http_status,"
                      " success, n_records) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (rel, path.parent.name, path.stem, endpoint, req.get("region") or req.get("country_code"),
                       req.get("date_range"), json.dumps(filters, ensure_ascii=False), doc.get("status"),
                       int(bool(body.get("success"))), len(records) if table else 0))
    pull_id = cur.lastrowid
    if table and body.get("success"):
        cols = TABLES[table]
        extra = {}
        if table == "categories":
            extra["category_level"] = req.get("category_level")
        if table == "videos":
            extra["product_filter"] = req.get("product_id")
        if table == "comment_insights":
            extra_pid = req.get("product_id")
        names = ["pull_id", "position"] + cols + list(extra) + ["raw_json"]
        for i, r in enumerate(records, 1):
            if table == "comment_insights":
                r = dict(r, product_id=r.get("product_id") or extra_pid)
            vals = [pull_id, i] + [_cell(r.get(c)) for c in cols] + list(extra.values()) + [json.dumps(r, ensure_ascii=False)]
            con.execute(f"INSERT INTO {table} ({', '.join(names)}) VALUES ({', '.join('?' * len(names))})", vals)
    if own:
        con.commit()
        con.close()
    return 1


def load_all():
    con = connect()
    n = sum(ingest_file(p, con) for p in sorted((ROOT / "raw").glob("*/*.json")))
    con.commit()
    con.close()
    return n


def stats():
    con = connect()
    for t in ["pulls"] + list(TABLES):
        print(f"  {t:17} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>6} rows")
    for row in con.execute("SELECT pulled_on, endpoint, COUNT(*), SUM(n_records) FROM pulls GROUP BY 1, 2"):
        print("  ", row)
    con.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "load":
        print(f"Loaded {load_all()} new raw files into {DB}")
    stats()
