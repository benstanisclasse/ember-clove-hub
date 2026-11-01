"""Kalodata gap-filling pulls for the winning-product research (owner approved 2026-10-31: "do both tiers").

Plan and costs: research/winning_products/DATA_ACQUISITION_2026-10-31.md. Niche = Womenswear, Shoes, Fashion
Accessories, Jewelry. Every call goes through kalodata.call (raw file first, credit cap) and kalodata_core.get
(saved responses are reused, so reruns cost nothing).

  tests     one call per untested endpoint/option (~0.5 credits)          -> raw/gaps_tests/
  deep      ranks 501-1,000 for other categories (owner, 2026-11-01: extend if the niche test shows value)
  ranks     monthly shop + creator ranks only (re-pull after the need_category fix; --months/--cats to limit)
  tier2     niche ranks 501-1,000 x 12 months, monthly shop + creator ranks, reviews, attributes, images and
            product videos for a seeded rank-stratified sample of Sep-2026 niche products (~77 credits) -> raw/gaps_tier2/
  forward   one month of the core design (top 500, risers 200, top videos 300, 29 categories, ~29 credits),
            written to research/kalodata/sealed/<month>/ and NOT loaded into kalodata.db until the forward-test
            predictions are frozen (research/winning_products/registry/DEFINITIONS_v1.md §7)

Run: python -I scripts/kalodata_gaps.py tests --max-credits 0.6
     python -I scripts/kalodata_gaps.py tier2 --max-credits 80
     python -I scripts/kalodata_gaps.py forward --month 2026-10 --max-credits 30   (only after the month has ended)
"""
import argparse
import csv
import datetime as dt
import random
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kalodata as k  # noqa: E402
import kalodata_core as core  # noqa: E402  (sets k.RAW to raw/core on import; each phase sets its own folder)

NICHE = {"601152": "Womenswear & Underwear", "601352": "Shoes", "605248": "Fashion Accessories",
         "953224": "Jewelry Accessories & Derivatives"}
MONTHS = core.MONTHS
SAMPLE_MONTH, SEED = "2026-09", 20261031
WORK = Path(__file__).resolve().parent.parent / "research" / "winning_products" / "_work"


def rank_payload(month, page, sort="revenue", page_size=100, **extra):
    return dict(k.COMMON, date_range=month, sort_field={"field": sort, "type": "DESC"}, page_size=page_size,
                page_number=page, **extra)


def tests(budget):
    k.RAW = k.OUT / "raw" / "gaps_tests"
    con = sqlite3.connect(f"file:{k.OUT / 'kalodata.db'}?mode=ro", uri=True)
    pid = con.execute("""select p.product_id from products p join pulls q using(pull_id) where q.kind='top'
        and q.month=? and q.category_id='601152' order by p.revenue desc limit 1""", (SAMPLE_MONTH,)).fetchone()[0]
    out = {}
    out["detail_need_extra"] = core.get("tiktok/product/detail", dict(k.COMMON, date_range=SAMPLE_MONTH, product_id=pid,
                                        need_extra=True, need_image=1), "test_detail_need_extra", budget, 0.1)
    out["rank_need_image"] = core.get("tiktok/product/rank", rank_payload(SAMPLE_MONTH, 1, page_size=10,
                                      category_ids=["601152"], need_extra=True, need_image=1), "test_rank_need_image", budget, 0.1)
    out["shop_rank"] = core.get("tiktok/shop/rank", rank_payload(SAMPLE_MONTH, 1, page_size=10, category_ids=["601152"]),
                                "test_shop_rank", budget, 0.1)
    out["creator_rank"] = core.get("tiktok/creator/rank", rank_payload(SAMPLE_MONTH, 1, page_size=10,
                                   category_id_list="601152"), "test_creator_rank", budget, 0.1)
    out["comments"] = core.get("tiktok/product/comments", {"product_id": pid, "region": "US", "page_number": 1,
                               "page_size": 100}, "test_comments", budget, 0.01)
    out["analysis"] = core.get("tiktok/product/analysis", {"product_id": pid, "region": "US", "language": "en-US"},
                               "test_analysis", budget, 0.1)
    for name, data in out.items():
        if data is None:
            print(f"  {name}: FAILED")
        elif isinstance(data, list):
            print(f"  {name}: {len(data)} rows; keys: {sorted(data[0])[:30] if data else []}")
        else:
            trend = data.get("revenue_trend")
            print(f"  {name}: keys {sorted(data)[:40]}" + (f"; revenue_trend points: {len(trend) if isinstance(trend, list) else trend!r}"
                                                         if "revenue_trend" in data else ""))
    print(f"Spent (estimated): {budget.spent:.2f}")


def sample():
    """Seeded rank-stratified sample of Sep-2026 niche top-500 products. Nested: videos ⊂ attributes ⊂ images ⊂ reviews."""
    con = sqlite3.connect(f"file:{k.OUT / 'kalodata.db'}?mode=ro", uri=True)
    rng = random.Random(SEED)
    rows = []
    for cid in NICHE:
        ranked = [r[0] for r in con.execute("""select p.product_id from products p join pulls q using(pull_id)
            where q.kind='top' and q.month=? and q.category_id=? group by p.product_id order by max(p.revenue) desc""",
                                             (SAMPLE_MONTH, cid))]
        linked = {r[0] for r in con.execute("select distinct product_filter from videos where product_filter is not null")}
        for stratum, pool, n in (("rank_1_100", ranked[:100], 50), ("rank_101_500", ranked[100:500], 75)):
            pick = rng.sample(pool, min(n, len(pool)))
            for i, pid in enumerate(pick):
                rows.append({"product_id": pid, "category_id": cid, "stratum": stratum,
                             "rank": ranked.index(pid) + 1, "reviews": 1, "images": int(i < n * 3 // 5),
                             "attributes": int(i < n * 2 // 5),
                             "videos": int(i < n // 5 and pid not in linked)})
    WORK.mkdir(parents=True, exist_ok=True)
    with open(WORK / "tier2_sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


def deep_ranks(budget, months, cats, folder="gaps_tier2"):
    """Ranks 501-1,000 (pages 6-10) per category-month; pages already held are skipped."""
    k.RAW = k.OUT / "raw" / folder
    con = sqlite3.connect(f"file:{k.OUT / 'kalodata.db'}?mode=ro", uri=True)
    print(f"Ranks 501-1,000: {len(cats)} categories x {len(months)} months", flush=True)
    for m in months:
        for cid in cats:
            have = {r[0] for r in con.execute("select page from pulls where month=? and category_id=? and "
                                              "kind in ('top','top_deep') and success=1", (m, cid))}
            for page in range(6, 11):
                if page not in have:
                    core.get("tiktok/product/rank", rank_payload(m, page, category_ids=[cid], need_extra=True),
                             f"deep_{m}_{cid}_p{page}", budget, 0.1)
    print(f"  {budget.spent:.1f} credits", flush=True)


def other_l1():
    """The 24 L1 categories outside the niche (Virtual Products excluded: its lists stop at rank 100)."""
    con = sqlite3.connect(f"file:{k.OUT / 'kalodata.db'}?mode=ro", uri=True)
    cats = [r[0] for r in con.execute("""select category_id from pulls where kind='top' and month is not null
            group by category_id having count(distinct month) = 12""")]
    return sorted(c for c in cats if c not in NICHE and c != "834312")


def tier2(budget):
    deep_ranks(budget, MONTHS, list(NICHE))
    shop_creator_ranks(budget, MONTHS, list(NICHE))
    rows = sample()
    print(f"Sample: {len(rows)} products (research/winning_products/_work/tier2_sample.csv)", flush=True)
    for r in rows:
        pid = r["product_id"]
        for page in (1, 2):
            data = core.get("tiktok/product/comments", {"product_id": pid, "region": "US", "page_number": page,
                                                         "page_size": 100}, f"reviews_{pid}_p{page}", budget, 0.01)
            if not data or len(data) < 100:
                break
        if r["images"]:
            core.get("tiktok/product/images", {"product_id": pid}, f"images_{pid}", budget, 0.01)
        if r["attributes"]:
            core.get("tiktok/product/analysis", {"product_id": pid, "region": "US", "language": "en-US"},
                     f"analysis_{pid}", budget, 0.1)
        if r["videos"]:
            core.get("tiktok/video/rank", rank_payload(SAMPLE_MONTH, 1, product_id=pid), f"pvideos_{SAMPLE_MONTH}_{pid}",
                     budget, 0.1)
    print(f"Done: {budget.spent:.2f} credits (estimated); calls {core.COUNT}", flush=True)


def shop_creator_ranks(budget, months, cats):
    """Top 100 shops and creators per niche category-month (need_category must be an integer, not a boolean)."""
    k.RAW = k.OUT / "raw" / "gaps_tier2"
    print("Monthly shop and creator ranks", flush=True)
    for m in months:
        for cid in cats:
            core.get("tiktok/shop/rank", rank_payload(m, 1, category_ids=[cid], need_category=1),
                     f"shops_{m}_{cid}", budget, 0.1)
            core.get("tiktok/creator/rank", rank_payload(m, 1, category_id_list=cid, need_category=1),
                     f"creators_{m}_{cid}", budget, 0.1)
    print(f"  {budget.spent:.1f} credits", flush=True)


def forward(month, budget):
    first_of_next = (dt.date.fromisoformat(month + "-01") + dt.timedelta(days=32)).replace(day=1)
    if dt.date.today() < first_of_next + dt.timedelta(days=1):
        raise SystemExit(f"{month} has not ended yet (run on or after {first_of_next + dt.timedelta(days=1)}).")
    k.RAW = k.OUT / "sealed" / month
    cats = [r[0] for r in sqlite3.connect(f"file:{k.OUT / 'kalodata.db'}?mode=ro", uri=True).execute(
        "select distinct category_id from pulls where kind='top' and month='2026-09'")]
    real_call = k.call

    def sealed_call(*a, **kw):  # never load sealed files into kalodata.db
        kw["ingest"] = False
        return real_call(*a, **kw)
    k.call = sealed_call
    for cid in sorted(cats):
        pages = 1 if cid == "834312" else 5
        for p in range(1, pages + 1):
            core.get("tiktok/product/rank", rank_payload(month, p, category_ids=[cid], need_extra=True),
                     f"fwd_top_{month}_{cid}_p{p}", budget, 0.1)
        for p in range(1, (1 if cid == "834312" else 2) + 1):
            core.get("tiktok/product/rank", rank_payload(month, p, sort="revenue_growth_rate", category_ids=[cid],
                                                         need_extra=True), f"fwd_risers_{month}_{cid}_p{p}", budget, 0.1)
        for p in range(1, (1 if cid == "834312" else 3) + 1):
            core.get("tiktok/video/rank", rank_payload(month, p, category_ids=[cid]), f"fwd_videos_{month}_{cid}_p{p}",
                     budget, 0.1)
    print(f"Sealed {month}: {budget.spent:.1f} credits; files in {k.RAW}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["tests", "tier2", "ranks", "deep", "forward"])
    ap.add_argument("--max-credits", type=float, required=True)
    ap.add_argument("--month")
    ap.add_argument("--months", help="ranks: comma-separated months (default: all 12)")
    ap.add_argument("--cats", help="ranks: comma-separated category ids (default: the 4 niche categories)")
    a = ap.parse_args()
    budget = k.Budget(a.max_credits)
    if a.cmd == "tests":
        tests(budget)
    elif a.cmd == "tier2":
        tier2(budget)
    elif a.cmd == "deep":  # ranks 501-1,000; default: the 24 non-niche L1 categories, all 12 months
        deep_ranks(budget, a.months.split(",") if a.months else MONTHS,
                   a.cats.split(",") if a.cats else other_l1(), folder="gaps_deep_all")
    elif a.cmd == "ranks":
        shop_creator_ranks(budget, a.months.split(",") if a.months else MONTHS,
                           a.cats.split(",") if a.cats else list(NICHE))
    else:
        forward(a.month, budget)


if __name__ == "__main__":
    main()
