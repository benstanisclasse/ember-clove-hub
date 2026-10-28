"""Kalodata Open API client and the TikTok Shop US research pull (product selection + video research).

Uses the key in the KALODATA_API_KEY user environment variable (via hub_env). Never prints the key.
Docs: https://www.kalodata.com/open-center/docs. Billing (2026-10-25): detail calls 0.1 credit, rank calls
0.1 x ceil(rows/100), comment insight 1 credit, balance free; 1 credit ~ $0.10.

Usage:
  python -I scripts/kalodata.py balance
  python -I scripts/kalodata.py research --max-credits 30
Raw responses: research/kalodata/raw/<date>/<name>.json. Summaries: research/kalodata/*.csv.
"""
import argparse
import csv
import datetime as dt
import json
import math
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hub_env  # noqa: E402
import kalodata_db  # noqa: E402

BASE = "https://www.kalodata.com/openapi/v1"
COMMON = {"region": "US", "language": "en-US", "currency": "USD"}
OUT = hub_env.HUB_ROOT / "research" / "kalodata"
RAW = OUT / "raw" / dt.date.today().isoformat()


class Budget:
    def __init__(self, max_credits):
        self.max, self.spent = max_credits, 0.0

    def charge(self, credits, name):
        if self.spent + credits > self.max + 1e-9:
            raise SystemExit(f"Stopping before '{name}': it would take spend to {self.spent + credits:.1f} "
                             f"credits, over the approved {self.max}.")
        self.spent += credits


def call(path, payload, name, budget=None, credits=0.0, method="POST"):
    if budget:
        budget.charge(credits, name)
    headers = {"secret-key": hub_env.get_secret("kalodata_api"), "content-type": "application/json;charset=UTF-8"}
    if method == "GET":
        resp = requests.get(f"{BASE}/{path}", headers=headers, params=payload, timeout=60)
    else:
        resp = requests.post(f"{BASE}/{path}", headers=headers, json=payload, timeout=60)
    body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text[:500]}
    RAW.mkdir(parents=True, exist_ok=True)
    raw_file = RAW / f"{name}.json"
    raw_file.write_text(json.dumps({"path": path, "request": payload, "status": resp.status_code, "response": body},
                                   indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        kalodata_db.ingest_file(raw_file)  # keep the local database in step with every pull
    except Exception as e:  # the raw file is the record; a DB hiccup must not lose a paid call
        print(f"  (database load skipped for {name}: {e})")
    if resp.status_code != 200 or not body.get("success", False):
        print(f"  {name}: HTTP {resp.status_code} code={body.get('code')} message={body.get('message')}")
        return None
    time.sleep(1.1)  # rank endpoints allow 10 requests per 10 s
    return body.get("data")


def rank(kind, name, budget, page_size=100, page=1, **filters):
    payload = dict(COMMON, date_range=filters.pop("date_range", "last30Day"),
                   sort_field={"field": filters.pop("sort", "revenue"), "type": "DESC"},
                   page_size=page_size, page_number=page, **filters)
    return call(f"tiktok/{kind}/rank", payload, name, budget, 0.1 * math.ceil(page_size / 100)) or []


def write_csv(name, rows):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"  saved {name}.csv ({len(rows)} rows)")


def find_categories(budget):
    """Walk the category tree to the women's clothing branches (names vary, so match loosely)."""
    top = rank("category", "category_l1", budget, category_level=1)
    womens = [c for c in top if "women" in c.get("category_name", "").lower()]
    print("  level-1 women's categories:", [(c["category_id"], c["category_name"]) for c in womens])
    ids = [c["category_id"] for c in womens]
    leaves = []
    if ids:
        for level in (2, 3):
            rows = rank("category", f"category_l{level}_womens", budget, category_ids=ids, category_level=level)
            for r in rows:
                r["level"] = level
            leaves += rows
    write_csv("categories_womens", womens + leaves)
    return leaves


def research(max_credits):
    OUT.mkdir(parents=True, exist_ok=True)
    budget = Budget(max_credits)
    print("Categories")
    leaves = find_categories(budget)
    wanted = [c for c in leaves if any(w in c.get("category_name", "").lower()
                                       for w in ("dress", "knit", "sweater", "skirt"))]
    print("  matched:", [(c["category_id"], c["category_name"], c.get("level")) for c in wanted])

    print("Products")
    prods = []
    for kw in ("sweater dress", "cable knit dress", "turtleneck dress", "knit midi skirt"):
        for r in rank("product", f"products_kw_{kw.replace(' ', '_')}", budget, keyword=kw, need_extra=True):
            prods.append(dict(r, query=f"keyword:{kw}"))
    for c in wanted[:6]:
        for band in ("40-80", "20-40"):
            for r in rank("product", f"products_cat_{c['category_id']}_{band}", budget,
                          category_ids=[c["category_id"]], unit_price_range=band, need_extra=True):
                prods.append(dict(r, query=f"cat:{c['category_name']} ${band}"))
    for r in rank("product", "products_global_40_80", budget, keyword="dress", delivery_type="global",
                  unit_price_range="40-80"):
        prods.append(dict(r, query="cross-border dress $40-80"))
    write_csv("products", prods)

    print("Videos")
    vids = []
    for kw in ("sweater dress", "knit dress", "turtleneck dress", "cable knit"):
        for r in rank("video", f"videos_kw_{kw.replace(' ', '_')}", budget, keyword=kw):
            vids.append(dict(r, query=f"keyword:{kw}"))
    for r in rank("video", "videos_ai_dress", budget, keyword="dress", is_ai_video=1):
        vids.append(dict(r, query="AI videos: dress"))
    write_csv("videos", vids)

    print("Product deep-dives")
    seen, top = set(), []
    # Keyword search is loose (it returns coats, shavers...), so keep only apparel names we care about.
    relevant = ("dress", "skirt", "sweater", "knit")
    for p in sorted(prods, key=lambda r: -(r.get("revenue") or 0)):
        name = (p.get("product_name") or "").lower()
        if (p["product_id"] not in seen and 35 <= (p.get("unit_price") or 0) <= 90
                and any(w in name for w in relevant)):
            seen.add(p["product_id"])
            top.append(p)
        if len(top) == 10:
            break
    details, insights = [], []
    for p in top:
        d = call("tiktok/product/detail", dict(COMMON, date_range="last30Day", product_id=p["product_id"]),
                 f"detail_{p['product_id']}", budget, 0.1)
        if d:
            d.pop("product_description", None)
            details.append(d)
    for p in top[:5]:
        i = call("tiktok/product/comment/insight", {"product_id": p["product_id"], "country_code": "us"},
                 f"comments_{p['product_id']}", budget, 1.0)
        if i:
            insights.append({"product_id": p["product_id"], "product_name": p.get("product_name"),
                             "pain_points": json.dumps(i.get("pain_points"), ensure_ascii=False),
                             "positive_points": json.dumps(i.get("positive_points"), ensure_ascii=False),
                             "usage_scenarios": json.dumps(i.get("usage_scenarios"), ensure_ascii=False)})
    write_csv("product_details", details)
    write_csv("comment_insights", insights)
    print(f"Done. Estimated credits used: {budget.spent:.1f} of {max_credits} (check 'balance' for the real figure).")


def product_videos(product_ids, max_pages, budget):
    """Product detail (total videos promoting it) + its video ranking, paged until the list runs out."""
    OUT.mkdir(parents=True, exist_ok=True)
    summary, rows = [], []
    for pid in product_ids:
        d = call("tiktok/product/detail", dict(COMMON, date_range="last30Day", product_id=pid),
                 f"detail_{pid}", budget, 0.1) or {}
        got = []
        for page in range(1, max_pages + 1):
            payload = dict(COMMON, date_range="last30Day", sort_field={"field": "revenue", "type": "DESC"},
                           page_size=100, page_number=page, product_id=pid)
            data = call("tiktok/video/rank", payload, f"videos_{pid}_p{page}", budget, 0.1) or []
            got += [dict(r, product_id=pid) for r in data]
            if len(data) < 100:
                break
        rows += got
        summary.append({"product_id": pid, "product_name": d.get("product_name"), "unit_price": d.get("unit_price"),
                        "revenue": d.get("revenue"), "video_revenue": d.get("video_revenue"),
                        "video_number": d.get("video_number"), "creator_number": d.get("creator_number"),
                        "videos_listed": len(got)})
        print(f"  {pid}: {d.get('video_number')} videos promoting it, {len(got)} listed")
    write_csv("product_videos", rows)
    write_csv("product_videos_summary", summary)
    print(f"Estimated credits used: {budget.spent:.1f}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("balance")
    r = sub.add_parser("research")
    r.add_argument("--max-credits", type=float, required=True)
    v = sub.add_parser("product-videos", help="every selling video for given products, to measure hit rates")
    v.add_argument("product_ids", nargs="+")
    v.add_argument("--max-pages", type=int, default=5)
    v.add_argument("--max-credits", type=float, required=True)
    c = sub.add_parser("comments", help="buyer comment insights for given product IDs (1 credit each)")
    c.add_argument("product_ids", nargs="+")
    c.add_argument("--max-credits", type=float, required=True)
    args = ap.parse_args()
    if args.cmd == "balance":
        print(json.dumps(call("credit/balance", {}, "balance", method="GET"), indent=2))
    elif args.cmd == "product-videos":
        product_videos(args.product_ids, args.max_pages, Budget(args.max_credits))
    elif args.cmd == "comments":
        budget, rows = Budget(args.max_credits), []
        for pid in args.product_ids:
            i = call("tiktok/product/comment/insight", {"product_id": pid, "country_code": "us"},
                     f"comments_{pid}", budget, 1.0)
            if i:
                rows.append({"product_id": pid, **{k: json.dumps(i.get(k), ensure_ascii=False)
                                                   for k in ("pain_points", "positive_points", "usage_scenarios")}})
        OUT.mkdir(parents=True, exist_ok=True)
        write_csv("comment_insights_lookalikes", rows)
    else:
        research(args.max_credits)


if __name__ == "__main__":
    main()
