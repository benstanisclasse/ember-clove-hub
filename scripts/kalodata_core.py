"""Core Kalodata dataset download (research/kalodata/CORE_DATASET_PLAN_2026-10-25.md). Owner approved 520 credits.

US, all 29 level-1 categories, Oct 2025 - Sep 2026. Phases:
  products  top 500 products per category-month by sales (5 pages)
  risers    top 200 per category-month by growth (2 pages)
  videos    top 300 videos per category-month by sales (3 pages)
  categories  level-1 and level-2 rankings (the API only allows last7Day..last365Day here, not past months)
  details   product detail for that month, 1,000-row sample (about 3 per category-month)
  allvideos every video for 100 products in Sep 2026 (paged until the list runs out, max 5 pages)
Resumable: every response is saved under research/kalodata/raw/core/<name>.json and a saved successful response is
reused instead of paying again. Stops before going over --max-credits.
Run: python -I scripts/kalodata_core.py --max-credits 520 [--months 2026-09] [--cats 601152] [--phases products,risers]
"""
import argparse
import json
import random
import sqlite3
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kalodata as k  # noqa: E402
import kalodata_db  # noqa: E402

MONTHS = [f"{y}-{m:02d}" for y, m in [(2025, 10), (2025, 11), (2025, 12)] + [(2026, i) for i in range(1, 10)]]
PHASES = ["products", "risers", "videos", "categories", "details", "allvideos"]
k.RAW = k.OUT / "raw" / "core"  # one folder for the whole run, so a resume after midnight still finds its files
COUNT = {"calls": 0, "cached": 0}


def cached(name):
    path = k.RAW / f"{name}.json"
    if not path.exists():
        return None
    doc = json.loads(path.read_text(encoding="utf-8"))
    body = doc.get("response") or {}
    if doc.get("status") == 200 and body.get("success"):
        return body.get("data") if body.get("data") is not None else []
    return None


def get(path, payload, name, budget, credits):
    """Saved response if we have one, else a paid call (retried twice on failure)."""
    data = cached(name)
    if data is not None:
        COUNT["cached"] += 1
        return data
    for attempt in range(5):
        try:
            data = k.call(path, payload, name, budget, credits)
        except requests.RequestException as e:  # dropped connection: wait and retry; a rerun fills any gap left
            print(f"  {name}: {type(e).__name__}, retrying", flush=True)
            time.sleep(15 * (attempt + 1))
            continue
        COUNT["calls"] += 1
        if COUNT["calls"] % 100 == 0:
            print(f"  ... {COUNT['calls']} calls, {budget.spent:.1f} credits", flush=True)
        if data is not None:
            return data
        body = (json.loads((k.RAW / f"{name}.json").read_text(encoding="utf-8")).get("response") or {})
        msg = str(body.get("message") or "").lower()
        if str(body.get("code")) == "501" or any(s in msg for s in ("parse error", "invalid parameter", "not found",
                                                                    "no enough")):
            return []  # invalid parameter or "not found": retrying won't help (the API sends code as a string)
        time.sleep(5 * (attempt + 1))
    return []


def rank_pages(kind, base, budget, pages, **filters):
    rows = []
    for page in range(1, pages + 1):
        payload = dict(k.COMMON, date_range=filters.get("date_range"),
                       sort_field={"field": filters.get("sort", "revenue"), "type": "DESC"},
                       page_size=100, page_number=page,
                       **{f: v for f, v in filters.items() if f not in ("date_range", "sort")})
        data = get(f"tiktok/{kind}/rank", payload, f"{base}_p{page}", budget, 0.1) or []
        rows += data
        if len(data) < 100:
            break
    return rows


def level1_ids():
    con = sqlite3.connect(kalodata_db.DB)
    ids = [r[0] for r in con.execute("SELECT DISTINCT category_id FROM categories WHERE category_level = 1")]
    con.close()
    return sorted(ids)


def core_products(months, cats):
    """Products from the core rank pulls, for sampling: (month, category, position, product_id, source)."""
    con = sqlite3.connect(kalodata_db.DB)
    rows = con.execute("SELECT u.name, p.position, p.product_id FROM products p JOIN pulls u ON p.pull_id = u.pull_id "
                       "WHERE u.name LIKE 'core_products_%' OR u.name LIKE 'core_risers_%'").fetchall()
    con.close()
    out = []
    for name, pos, pid in rows:
        parts = name.split("_")  # core_<phase>_<month>_<cat>_p<n>
        month, cat, page = parts[2], parts[3], int(parts[4][1:])
        if month in months and cat in cats:
            out.append((month, cat, (page - 1) * 100 + pos, pid, parts[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-credits", type=float, required=True)
    ap.add_argument("--months", default=",".join(MONTHS))
    ap.add_argument("--cats", default="")
    ap.add_argument("--phases", default=",".join(PHASES))
    ap.add_argument("--riser-pages", type=int, default=2, help="pages of 100 risers per category-month (core: 2)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    k.RAW.mkdir(parents=True, exist_ok=True)
    budget = k.Budget(args.max_credits)
    months = args.months.split(",")
    cats = args.cats.split(",") if args.cats else level1_ids()
    phases = args.phases.split(",")
    print(f"Core download: {len(months)} months x {len(cats)} categories, phases {phases}, cap {args.max_credits}")

    for m in months:
        for c in cats:
            if "products" in phases:
                rank_pages("product", f"core_products_{m}_{c}", budget, 5, date_range=m, category_ids=[c], need_extra=True)
            if "risers" in phases:
                rank_pages("product", f"core_risers_{m}_{c}", budget, args.riser_pages, date_range=m, category_ids=[c],
                           sort="revenue_growth_rate", need_extra=True)
            if "videos" in phases:
                rank_pages("video", f"core_videos_{m}_{c}", budget, 3, date_range=m, category_ids=[c])
        print(f"{m} done: {COUNT['calls']} calls, {COUNT['cached']} reused, {budget.spent:.1f} credits", flush=True)

    if "categories" in phases:
        for dr in ("last30Day", "last365Day"):
            rank_pages("category", f"core_categories_l1_{dr}", budget, 1, date_range=dr, category_level=1)
            rank_pages("category", f"core_categories_l2_{dr}", budget, 5, date_range=dr, category_level=2,
                       category_ids=cats)
        print(f"categories done: {budget.spent:.1f} credits", flush=True)

    if "details" in phases:
        rng = random.Random(7)
        pool = core_products(months, cats)
        sample = []
        for m in months:  # about 3 per category-month: one top-100, one from 101-500, one riser
            for c in cats:
                here = [r for r in pool if r[0] == m and r[1] == c]
                for pick in ([r for r in here if r[4] == "products" and r[2] <= 100],
                             [r for r in here if r[4] == "products" and r[2] > 100],
                             [r for r in here if r[4] == "risers"]):
                    if pick:
                        sample.append(rng.choice(pick))
        rng.shuffle(sample)
        for m, c, pos, pid, src in sample[:1000]:
            get("tiktok/product/detail", dict(k.COMMON, date_range=m, product_id=pid),
                f"core_detail_{m}_{c}_{pid}", budget, 0.1)
        print(f"details done ({min(len(sample), 1000)} products): {budget.spent:.1f} credits", flush=True)

    if "allvideos" in phases:
        last = months[-1]
        pool = [r for r in core_products([last], cats) if r[4] == "products"]
        picks = []
        for c in cats:  # spread across categories and ranks: positions near 1, 50, 200, 450
            here = sorted([r for r in pool if r[1] == c], key=lambda r: r[2])
            for target in (1, 50, 200, 450):
                if here:
                    picks.append(min(here, key=lambda r: abs(r[2] - target)))
        for m, c, pos, pid, src in list(dict.fromkeys(picks))[:100]:
            for page in range(1, 6):
                payload = dict(k.COMMON, date_range=m, sort_field={"field": "revenue", "type": "DESC"},
                               page_size=100, page_number=page, product_id=pid)
                data = get("tiktok/video/rank", payload, f"core_allvideos_{m}_{c}_{pid}_p{page}", budget, 0.1)
                if len(data or []) < 100:
                    break
        print(f"allvideos done: {budget.spent:.1f} credits", flush=True)

    print(f"Finished: {COUNT['calls']} paid calls, {COUNT['cached']} reused, {budget.spent:.1f} credits charged "
          f"(failed calls are free, so the real spend can be lower; check 'balance').")


if __name__ == "__main__":
    main()
