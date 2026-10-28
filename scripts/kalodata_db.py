"""Local Kalodata database: every raw API response in research/kalodata/raw/ loaded into one SQLite file.

Each response becomes one row in `pulls` (date pulled, endpoint, filters, date range) plus its records in a typed
table (products, videos, product_details, categories, comment_insights). Every record also keeps its full JSON in
`raw_json`, so fields we don't have columns for aren't lost. Loading is idempotent: each file's SHA-256 is stored,
an unchanged file is skipped and a changed file (e.g. a failed call later re-pulled under the same name) is reloaded.

Every pull also gets columns read from its request, not its file name: kind (top / risers / risers_deep /
top_videos / product_videos / detail / comments / category / other), month (YYYY-MM, or NULL for rolling windows such
as last30Day), category_id, page, and collected_at (the raw file's modified time; Kalodata gives no timestamp).
Buyer identities in comment responses (`review_user`) are dropped before anything is stored (owner, 2026-10-28).

Usage:
  python -I scripts/kalodata_db.py load        load new or changed raw files, fill metadata for old pulls
  python -I scripts/kalodata_db.py redact-raw  remove buyer identities from raw comment files (one-off, idempotent)
  python -I scripts/kalodata_db.py stats       row counts per table and pull kind
DB: research/kalodata/kalodata.db
"""
import datetime as dt
import hashlib
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
PULL_META = {"sha256": "TEXT", "collected_at": "TEXT", "kind": "TEXT", "month": "TEXT", "category_id": "TEXT",
             "page": "INTEGER"}
PRIVATE_KEYS = {"review_user"}  # buyer name and user id in comment responses
RISER_PAGES = 2  # risers 1-200; later pages (201-1,000, pulled once for Sep 2026) are kind risers_deep


def scrub(o):
    """Copy of a parsed response with buyer identities removed."""
    if isinstance(o, dict):
        return {k: scrub(v) for k, v in o.items() if k not in PRIVATE_KEYS}
    if isinstance(o, list):
        return [scrub(v) for v in o]
    return o


def pull_meta(endpoint, req):
    """kind, month, category_id, page from the request itself (file names are not reliable)."""
    date_range = str(req.get("date_range") or "")
    month = date_range if len(date_range) == 7 and date_range[4] == "-" else None
    cats = req.get("category_ids") or []
    category = str(cats[0]) if cats else (str(req["category_id"]) if req.get("category_id") else None)
    page = req.get("page_number")
    sort = (req.get("sort_field") or {}).get("field")
    if endpoint == "tiktok/product/rank":
        kind = "top" if sort in (None, "revenue") else (
            "risers" if (page or 1) <= RISER_PAGES else "risers_deep") if sort == "revenue_growth_rate" else "other"
    elif endpoint == "tiktok/video/rank":
        kind = "product_videos" if req.get("product_id") else "top_videos"
    else:
        kind = {"tiktok/product/detail": "detail", "tiktok/product/comment/insight": "comments",
                "tiktok/category/rank": "category"}.get(endpoint, "other")
    return kind, month, category, page


def _collected_at(path):
    return dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")


def connect():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS pulls (
        pull_id INTEGER PRIMARY KEY, file TEXT UNIQUE, pulled_on TEXT, name TEXT, endpoint TEXT,
        region TEXT, date_range TEXT, filters TEXT, http_status INTEGER, success INTEGER, n_records INTEGER)""")
    have = {r[1] for r in con.execute("PRAGMA table_info(pulls)")}
    for col, typ in PULL_META.items():
        if col not in have:
            con.execute(f"ALTER TABLE pulls ADD COLUMN {col} {typ}")
    con.execute("CREATE INDEX IF NOT EXISTS ix_pulls_kind ON pulls(kind, month, category_id)")
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


def _drop_pull(con, pull_id):
    for table in TABLES:
        con.execute(f"DELETE FROM {table} WHERE pull_id = ?", (pull_id,))
    con.execute("DELETE FROM pulls WHERE pull_id = ?", (pull_id,))


def ingest_file(path, con=None):
    """Load one raw file. Returns 1 if loaded or reloaded, 0 if already current."""
    path = Path(path)
    own = con is None
    con = con or connect()
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    doc = scrub(json.loads(raw.decode("utf-8")))
    req, body = doc.get("request") or {}, doc.get("response") or {}
    endpoint = doc.get("path") or next((e for p, e in PREFIX_ENDPOINT if path.stem.startswith(p)), "unknown")
    data = body.get("data")
    records = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
    table = ENDPOINT_TABLE.get(endpoint)
    meta = pull_meta(endpoint, req)
    old = con.execute("SELECT pull_id, sha256, success, n_records FROM pulls WHERE file = ?", (rel,)).fetchone()
    if old:
        if old[1] == digest:
            return 0
        same = old[2] == int(bool(body.get("success"))) and old[3] == (len(records) if table else 0)
        if old[1] is None and same:  # loaded before checksums existed and still matches: just fill the metadata
            con.execute("UPDATE pulls SET sha256=?, collected_at=?, kind=?, month=?, category_id=?, page=? "
                        "WHERE pull_id=?", (digest, _collected_at(path), *meta, old[0]))
            return 0
        _drop_pull(con, old[0])  # the file changed: replace the pull and its records
    filters = {k: v for k, v in req.items() if k not in ("region", "language", "currency", "date_range")}
    cur = con.execute("INSERT INTO pulls (file, pulled_on, name, endpoint, region, date_range, filters, http_status,"
                      " success, n_records, sha256, collected_at, kind, month, category_id, page)"
                      " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (rel, path.parent.name, path.stem, endpoint, req.get("region") or req.get("country_code"),
                       req.get("date_range"), json.dumps(filters, ensure_ascii=False), doc.get("status"),
                       int(bool(body.get("success"))), len(records) if table else 0,
                       digest, _collected_at(path), *meta))
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
    # records stored before scrubbing existed: drop buyer identities from their raw_json too
    for rowid, rj in con.execute("SELECT rowid, raw_json FROM comment_insights WHERE raw_json LIKE '%review_user%'"
                                 ).fetchall():
        con.execute("UPDATE comment_insights SET raw_json = ? WHERE rowid = ?",
                    (json.dumps(scrub(json.loads(rj)), ensure_ascii=False), rowid))
    con.commit()
    con.close()
    return n


def redact_raw():
    """Rewrite raw comment files without buyer identities. Keeps the file's modified time (it is collected_at)."""
    import os
    n = 0
    for p in sorted((ROOT / "raw").glob("*/*.json")):
        text = p.read_text(encoding="utf-8")
        if '"review_user"' not in text:
            continue
        st = p.stat()
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(scrub(json.loads(text)), ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, p)
        os.utime(p, (st.st_atime, st.st_mtime))
        n += 1
    return n


def stats():
    con = connect()
    for t in ["pulls"] + list(TABLES):
        print(f"  {t:17} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>6} rows")
    for row in con.execute("SELECT kind, endpoint, COUNT(*), SUM(n_records), SUM(success = 0) FROM pulls "
                           "GROUP BY 1, 2 ORDER BY 1"):
        print("  ", row)
    con.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "redact-raw":
        print(f"Removed buyer identities from {redact_raw()} raw files")
    if cmd == "load":
        print(f"Loaded {load_all()} new or changed raw files into {DB}")
    stats()
