"""Phase A (2026-10-31): data-integrity checks on research/kalodata/kalodata.db for the winning-product research.

Read only (the database is opened with mode=ro). Writes research/winning_products/_work/phase_a_results.json and
phase_a_coverage.csv. Every number quoted in PHASE_A_DATA_INTEGRITY.md comes from this file's output.
Run: python -I research/winning_products/scripts/phase_a_integrity.py
"""
import collections
import csv
import json
import math
import sqlite3
import statistics as st
from pathlib import Path

HUB = Path(__file__).resolve().parents[3]
DB = HUB / "research" / "kalodata" / "kalodata.db"
OUT = HUB / "research" / "winning_products" / "_work"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
R = {}
MONTHS = [f"{y}-{m:02d}" for y, m in [(2025, 10), (2025, 11), (2025, 12)] + [(2026, i) for i in range(1, 10)]]


def prev_month(m):
    y, mm = int(m[:4]), int(m[5:])
    return f"{y - 1}-12" if mm == 1 else f"{y}-{mm - 1:02d}"


def q(p, xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


# ---------------------------------------------------------------- 1. product observations (core panel)
obs = con.execute("""
    select p.product_id, q.month, q.kind, q.category_id, q.page, p.position, q.collected_at, q.pulled_on, q.pull_id,
           p.revenue, p.sales_volumn units, p.unit_price, p.revenue_growth_rate g, p.commission_rate,
           p.live_revenue, p.video_revenue, p.showcase_revenue, p.launch_date, p.seller_id, p.sku_count
    from products p join pulls q using(pull_id)
    where q.month is not null and q.kind in ('top','risers','risers_deep') and q.category_id is not null""").fetchall()
R["n_observation_rows"] = len(obs)
cats = {r[0]: r[1] for r in con.execute("select category_id, category_name from categories")}

# duplicates: same product, month, kind, category seen in more than one row
key_rows = collections.defaultdict(list)
for o in obs:
    key_rows[(o["product_id"], o["month"], o["kind"], o["category_id"])].append(o)
dups = {k: v for k, v in key_rows.items() if len(v) > 1}
diff_vals = 0
diff_examples = []
for k, v in dups.items():
    revs = {round(x["revenue"], 2) for x in v}
    if len(revs) > 1:
        diff_vals += 1
        if len(diff_examples) < 5:
            diff_examples.append({"key": k, "revenues": sorted(revs), "pulls": [(x["pulled_on"], x["collected_at"]) for x in v]})
R["duplicates_same_list"] = {"keys_with_multiple_rows": len(dups), "of_which_values_differ": diff_vals,
                             "examples_differing": diff_examples}

# same product-month seen in different lists (top vs risers, or two categories): are values consistent?
pm = collections.defaultdict(list)
for o in obs:
    pm[(o["product_id"], o["month"])].append(o)
multi_cat = sum(1 for v in pm.values() if len({x["category_id"] for x in v}) > 1)
incons = []
for k, v in pm.items():
    revs = [x["revenue"] for x in v]
    if max(revs) > 0 and (max(revs) - min(revs)) / max(revs) > 0.01:
        incons.append(k)
R["product_month"] = {"distinct_product_months": len(pm), "products": len({k[0] for k in pm}),
                      "product_months_in_more_than_one_category": multi_cat,
                      "product_months_with_revenue_disagreeing_over_1pct": len(incons),
                      "examples": [(k, [(x["kind"], x["pulled_on"], x["revenue"]) for x in pm[k]]) for k in incons[:5]]}

# collection timing: every month was pulled retrospectively
R["collection_window"] = con.execute("""select min(collected_at), max(collected_at) from pulls
    where kind in ('top','risers','risers_deep','top_videos','detail')""").fetchone()[:]
R["collection_by_month"] = {m: con.execute("""select min(collected_at), max(collected_at), count(*) from pulls
    where month=? and kind in ('top','risers','top_videos')""", (m,)).fetchone()[:] for m in MONTHS}

# ---------------------------------------------------------------- 2. one value per product-month (dedupe rule)
# rule: prefer kind=top, then risers, then risers_deep; within that, the earliest collected row
order = {"top": 0, "risers": 1, "risers_deep": 2}
panel = {}
for k, v in pm.items():
    panel[k] = sorted(v, key=lambda x: (order[x["kind"]], x["collected_at"] or ""))[0]
R["panel"] = {"product_months": len(panel)}

# ---------------------------------------------------------------- 3. growth-rate definition
# Kalodata revenue_growth_rate vs our computed (rev_m / rev_{m-1} - 1) when both months are observed
pairs, agree = [], 0
for (pid, m), o in panel.items():
    prev = panel.get((pid, prev_month(m)))
    if prev and prev["revenue"] > 0 and o["g"] is not None:
        mine = (o["revenue"] / prev["revenue"] - 1) * 100
        pairs.append((mine, o["g"]))
        if abs(mine - o["g"]) <= max(1.0, 0.02 * abs(mine)):
            agree += 1
R["growth_rate_check"] = {"pairs": len(pairs), "agree_within_2pct_or_1pt": agree,
                          "share": round(agree / len(pairs), 4) if pairs else None,
                          "sample_disagreements": [p for p in pairs if abs(p[0] - p[1]) > max(1.0, 0.02 * abs(p[0]))][:8]}
gs = [o["g"] for o in panel.values() if o["g"] is not None]
R["growth_rate_values"] = {"n": len(gs), "eq_-100": sum(1 for g in gs if g == -100), "lt_-100": sum(1 for g in gs if g < -100),
                           "p01": q(0.01, gs), "p50": q(0.5, gs), "p99": q(0.99, gs), "max": max(gs)}

# ---------------------------------------------------------------- 4. field consistency
vals = list(panel.values())
chan_ratio = [(o["live_revenue"] + o["video_revenue"] + o["showcase_revenue"]) / o["revenue"] for o in vals if o["revenue"] > 0]
asp_ratio = [o["unit_price"] * o["units"] / o["revenue"] for o in vals if o["revenue"] > 0 and o["units"]]
R["field_checks"] = {
    "revenue_le_0": sum(1 for o in vals if o["revenue"] <= 0),
    "units_le_0": sum(1 for o in vals if not o["units"] or o["units"] <= 0),
    "channel_sum_over_revenue": {"p01": q(.01, chan_ratio), "p50": q(.5, chan_ratio), "p99": q(.99, chan_ratio),
                                 "share_within_1pct": round(sum(1 for r in chan_ratio if abs(r - 1) <= .01) / len(chan_ratio), 4)},
    "asp_x_units_over_revenue": {"p01": q(.01, asp_ratio), "p50": q(.5, asp_ratio), "p99": q(.99, asp_ratio),
                                 "share_within_2pct": round(sum(1 for r in asp_ratio if abs(r - 1) <= .02) / len(asp_ratio), 4)},
    "commission_values": dict(collections.Counter(round(o["commission_rate"] or 0) for o in vals).most_common(8)),
    "commission_zero_share": round(sum(1 for o in vals if not o["commission_rate"]) / len(vals), 4),
    "seller_missing": sum(1 for o in vals if not o["seller_id"]),
    "sku_count_missing": sum(1 for o in vals if not o["sku_count"]),
}
# launch dates vs observation month
late, missing, ages = 0, 0, []
for (pid, m), o in panel.items():
    ld = o["launch_date"]
    if not ld:
        missing += 1
        continue
    month_end = m + "-31"
    if ld[:7] > m:
        late += 1
    else:
        y, mm = int(m[:4]), int(m[5:])
        ly, lm = int(ld[:4]), int(ld[5:7])
        ages.append((y - ly) * 12 + mm - lm)
lds = [o["launch_date"] for o in vals if o["launch_date"]]
R["launch_date"] = {"missing": missing, "launch_after_observed_month": late, "min": min(lds), "max": max(lds),
                    "age_months_p10_p50_p90": [q(.1, ages), q(.5, ages), q(.9, ages)],
                    "distinct_launch_dates_per_product_max": max(len({x["launch_date"] for x in v}) for v in pm.values())}

# ---------------------------------------------------------------- 5. rank depth and truncation
cov_rows = []
for cid, m, kind, n, minrev, maxpos in con.execute("""
        select q.category_id, q.month, q.kind, count(*), min(p.revenue), max(p.position + (q.page-1)*100)
        from products p join pulls q using(pull_id)
        where q.month is not null and q.kind in ('top','risers','risers_deep') and q.category_id is not null
        group by 1,2,3""").fetchall():
    cov_rows.append({"category_id": cid, "category": cats.get(cid), "month": m, "kind": kind, "rows": n,
                     "min_revenue_in_list": round(minrev, 2), "deepest_rank": maxpos})
with open(OUT / "phase_a_coverage.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(cov_rows[0]))
    w.writeheader()
    w.writerows(sorted(cov_rows, key=lambda r: (r["category"] or "", r["month"], r["kind"])))
top_cut = [r["min_revenue_in_list"] for r in cov_rows if r["kind"] == "top" and r["rows"] >= 450]
R["top500_cutoff_revenue"] = {"n_cat_months": len(top_cut), "p10": q(.1, top_cut), "p50": q(.5, top_cut), "p90": q(.9, top_cut)}
short = [r for r in cov_rows if r["kind"] == "top" and r["rows"] < 450]
R["short_top_lists"] = [(r["category"], r["month"], r["rows"]) for r in short]

# risers: how small are they?
rr = [o["revenue"] for o in obs if o["kind"] == "risers"]
R["risers_revenue"] = {"n": len(rr), "p10": q(.1, rr), "p50": q(.5, rr), "p90": q(.9, rr),
                       "share_below_1000usd": round(sum(1 for x in rr if x < 1000) / len(rr), 4)}
rg = [o["g"] for o in obs if o["kind"] == "risers" and o["g"] is not None]
R["risers_growth"] = {"p10": q(.1, rg), "p50": q(.5, rg), "p90": q(.9, rg)}

# top-500 share of category revenue (Sep 2026 top-500 sum vs category/rank last30Day as of 2026-10-25/26)
cat30 = {r[0]: r[1] for r in con.execute("""select c.category_id, c.revenue from categories c join pulls q using(pull_id)
        where q.date_range='last30Day' and c.category_level=1""")}
sep = collections.defaultdict(float)
for (pid, m), o in panel.items():
    if m == "2026-09" and o["kind"] == "top":
        sep[o["category_id"]] += o["revenue"]
R["top500_share_of_category_approx"] = {cats.get(c): round(sep[c] / cat30[c], 3) for c in sep if cat30.get(c)}

# ---------------------------------------------------------------- 6. panel continuity (top lists only)
top_months = collections.defaultdict(set)
for (pid, m), o in panel.items():
    if o["kind"] == "top":
        top_months[pid].add(m)
cnt = collections.Counter(len(v) for v in top_months.values())
R["top500_months_per_product"] = dict(sorted(cnt.items()))
# month-to-month retention in top500 within the same category
ret = {}
for m in MONTHS[1:]:
    prev = {pid for pid, ms in top_months.items() if prev_month(m) in ms}
    now = {pid for pid, ms in top_months.items() if m in ms}
    ret[m] = {"prev_top": len(prev), "still_top": len(prev & now), "rate": round(len(prev & now) / len(prev), 3) if prev else None,
              "new_entrants": len(now - prev)}
R["top500_retention"] = ret
# where did new entrants come from: seen in previous month's riser list, or never seen before?
seen_before = collections.defaultdict(set)
for (pid, m), o in panel.items():
    seen_before[pid].add(m)
src = {}
for m in MONTHS[1:]:
    now = {pid for pid, ms in top_months.items() if m in ms and prev_month(m) not in ms}
    prev_any = sum(1 for pid in now if prev_month(m) in seen_before[pid])
    earlier = sum(1 for pid in now if any(x < m for x in seen_before[pid]))
    src[m] = {"entrants": len(now), "in_any_list_prev_month": prev_any, "in_any_list_any_earlier_month": earlier}
R["top500_entrant_sources"] = src

# ---------------------------------------------------------------- 7. product_details: are monthly counts truly historical?
det = con.execute("""select d.product_id, q.month, d.creator_number, d.video_number, d.live_number, d.product_review_count,
                            d.revenue, d.unit_price, d.launch_date
                     from product_details d join pulls q using(pull_id) where q.month is not null""").fetchall()
byp = collections.defaultdict(list)
for d in det:
    byp[d["product_id"]].append(d)
varies = {f: sum(1 for v in byp.values() if len(v) > 1 and len({x[f] for x in v}) > 1) for f in
          ("creator_number", "video_number", "live_number", "product_review_count", "revenue", "launch_date")}
R["detail_history"] = {"products_with_monthly_details": len(byp), "months_per_product_p50": q(.5, [len(v) for v in byp.values()]),
                       "products_where_field_varies_by_month": varies}
# does detail revenue for a month match the rank revenue for the same month?
match = tot = 0
for d in det:
    o = panel.get((d["product_id"], d["month"]))
    if o and o["revenue"] > 0:
        tot += 1
        match += abs(d["revenue"] - o["revenue"]) / o["revenue"] <= 0.01
R["detail_vs_rank_revenue_same_month"] = {"pairs": tot, "match_within_1pct": match}

# ---------------------------------------------------------------- 8. videos
vid = con.execute("""select v.video_id, q.month, q.kind, q.category_id, v.revenue, v.views, v.ad, v.ads_roas, v.ai_video,
                            v.ad_revenue_ratio, v.ad_view_ratio, v.publish_date, v.digg_count, v.product_filter,
                            v.belonged_creator_id
                     from videos v join pulls q using(pull_id) where q.month is not null""").fetchall()
vp = collections.defaultdict(list)
for v in vid:
    vp[(v["video_id"], v["month"], v["kind"], v["category_id"] or v["product_filter"])].append(v)
pub_after = sum(1 for v in vid if v["publish_date"] and v["publish_date"][:7].replace("/", "-") > v["month"])
pub_age = []
for v in vid:
    if v["publish_date"]:
        pm_ = v["publish_date"][:7].replace("/", "-")
        pub_age.append((int(v["month"][:4]) - int(pm_[:4])) * 12 + int(v["month"][5:]) - int(pm_[5:]))
ads = [v for v in vid if v["ad"] == 1]
nonads = [v for v in vid if v["ad"] == 0]
R["videos"] = {
    "rows": len(vid), "distinct_video_months": len({(v["video_id"], v["month"]) for v in vid}),
    "dup_keys": sum(1 for x in vp.values() if len(x) > 1),
    "published_after_observed_month": pub_after,
    "publish_age_months_p10_p50_p90": [q(.1, pub_age), q(.5, pub_age), q(.9, pub_age)],
    "ad_share": round(len(ads) / len(vid), 3), "ai_share": round(sum(1 for v in vid if v["ai_video"]) / len(vid), 3),
    "ads_roas_zero_when_ad": round(sum(1 for v in ads if not v["ads_roas"]) / max(1, len(ads)), 3),
    "ads_roas_nonzero_when_not_ad": round(sum(1 for v in nonads if v["ads_roas"]) / max(1, len(nonads)), 3),
    "ads_roas_distinct_values": len({v["ads_roas"] for v in ads}),
    "ads_roas_p10_p50_p90_when_ad": [q(.1, [v["ads_roas"] for v in ads]), q(.5, [v["ads_roas"] for v in ads]), q(.9, [v["ads_roas"] for v in ads])],
    "ad_revenue_ratio_range": [min(v["ad_revenue_ratio"] or 0 for v in vid), max(v["ad_revenue_ratio"] or 0 for v in vid)],
    "zero_view_rows": sum(1 for v in vid if not v["views"]),
    "rows_with_product_link": sum(1 for v in vid if v["product_filter"]),
    "products_with_video_link": len({v["product_filter"] for v in vid if v["product_filter"]}),
    "months_with_product_link": sorted({v["month"] for v in vid if v["product_filter"]}),
}
# revenue vs views relationship (Spearman) on top-video rows
def spearman(x, y):
    def rank(a):
        o = sorted(range(len(a)), key=lambda i: a[i]); r = [0] * len(a)
        for i, j in enumerate(o):
            r[j] = i
        return r
    rx, ry = rank(x), rank(y)
    n = len(x); mx = (n - 1) / 2
    num = sum((a - mx) * (b - mx) for a, b in zip(rx, ry)); den = sum((a - mx) ** 2 for a in rx)
    return num / den
tv = [v for v in vid if v["kind"] == "top_videos" and v["views"] and v["revenue"]]
R["videos"]["spearman_revenue_views_topvideos"] = round(spearman([v["revenue"] for v in tv], [v["views"] for v in tv]), 3)
R["videos"]["spearman_revenue_likes_topvideos"] = round(spearman([v["revenue"] for v in tv], [v["digg_count"] or 0 for v in tv]), 3)

# ---------------------------------------------------------------- 9. small tables
R["comment_insights"] = con.execute("select count(*), min(json_extract(raw_json,'$.cached_at')), max(json_extract(raw_json,'$.cached_at')) from comment_insights").fetchone()[:]
R["video_features"] = con.execute("select count(*), sum(role='winner'), count(distinct product_id), count(distinct category) from video_features").fetchone()[:]
R["categories_snapshots"] = con.execute("""select q.date_range, c.category_level, count(*), min(q.collected_at)
    from categories c join pulls q using(pull_id) group by 1,2""").fetchall()
R["categories_snapshots"] = [tuple(r) for r in R["categories_snapshots"]]

(OUT / "phase_a_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps(R, indent=1, default=str)[:12000])
