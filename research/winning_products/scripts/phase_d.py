"""Phase D: video and advertising research (registry/PHASE_D_PLAN.md, frozen before this ran). Read-only on kalodata.db.

Writes _work/phase_d_results.json and the D6 forward-test file registry/forward_test_video_conc_2026-09.csv (once).
Run: python -I research/winning_products/scripts/phase_d.py
"""
import hashlib
import json
import math
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features as F  # noqa: E402
import panel  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = panel.HUB / "research" / "winning_products"
con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
R = {"plan": "registry/PHASE_D_PLAN.md"}
V = pd.read_sql_query("""select v.video_id, q.month, q.category_id cat, q.kind, v.product_filter pid, v.belonged_creator_id creator,
        v.revenue, v.views, v.digg_count likes, v.share_count shares, v.comment_count comments, v.ad, v.ads_roas roas,
        v.ai_video ai, v.ad_revenue_ratio ad_rev_ratio, v.ad_view_ratio ad_view_ratio, v.publish_date,
        json_extract(v.raw_json, '$.creator_debut') creator_debut
    from videos v join pulls q using(pull_id) where q.month is not null and q.success = 1""", con)
T = V[V["kind"] == "top_videos"].drop_duplicates(["video_id", "month", "cat"]).copy()
T = T[T["cat"] != "834312"]
T["rpm"] = T["revenue"] / T["views"] * 1000
T["eng"] = (T["likes"] + T["comments"] + T["shares"]) / T["views"]

# ------------------------------------------------------------------ D1 ad-field audit
ads, org = T[T["ad"] == 1], T[T["ad"] == 0]
R["D1"] = {
    "rows": len(T), "ad_share_by_month": T.groupby("month")["ad"].mean().round(3).to_dict(),
    "ad_share_by_category_p10_p50_p90": [round(float(T.groupby("cat")["ad"].mean().quantile(q)), 3) for q in (.1, .5, .9)],
    "roas_when_ad_p10_p50_p90": [round(float(ads["roas"].quantile(q)), 2) for q in (.1, .5, .9)],
    "roas_nonzero_when_organic": int((org["roas"].fillna(0) != 0).sum()),
    "roas_zero_when_ad": int((ads["roas"].fillna(0) == 0).sum()),
    "ad_rev_ratio_range": [float(T["ad_rev_ratio"].min()), float(T["ad_rev_ratio"].max())],
    "ad_rev_ratio_at_cap_80_share_of_ads": round(float((ads["ad_rev_ratio"] >= 79.99).mean()), 3),
    "ad_view_ratio_range": [float(T["ad_view_ratio"].min()), float(T["ad_view_ratio"].max())],
    "organic_with_ad_rev_ratio_gt0": int((org["ad_rev_ratio"] > 0).sum()),
    "ai_share_by_month": T.groupby("month")["ai"].mean().round(3).to_dict(),
    "roas_by_category_median": T[T["ad"] == 1].groupby("cat")["roas"].median().round(2).describe()[["min", "50%", "max"]].to_dict()}

# ------------------------------------------------------------------ D2 engagement vs revenue (within category-month)
cells = []
for (c, m), g in T.groupby(["cat", "month"]):
    if len(g) < 50:
        continue
    row = {"cat": c, "month": m, "n": len(g)}
    for f in ("views", "likes", "shares", "comments", "eng"):
        row[f] = spearmanr(g["revenue"], g[f]).correlation
    row["rpm_vs_eng"] = spearmanr(g["rpm"], g["eng"]).correlation
    cells.append(row)
cd = pd.DataFrame(cells)
R["D2"] = {"cells": len(cd), **{f: {"median_rho": round(float(cd[f].median()), 3), "iqr": [round(float(cd[f].quantile(.25)), 3),
                                                                                   round(float(cd[f].quantile(.75)), 3)]}
                               for f in ("views", "likes", "shares", "comments", "eng", "rpm_vs_eng")}}
R["D2"]["verdict"] = {f: ("weak (<0.3)" if R["D2"][f]["median_rho"] < 0.3 else "strong (>0.6)" if R["D2"][f]["median_rho"] > 0.6
                          else "moderate") for f in ("views", "likes", "shares", "comments", "eng")}
R["D2"]["rpm_p10_p50_p90"] = [round(float(T["rpm"].quantile(q)), 2) for q in (.1, .5, .9)]

# ------------------------------------------------------------------ D3 ad vs organic revenue per 1k views, within views deciles
T["vdec"] = T.groupby(["cat", "month"])["views"].transform(lambda s: pd.qcut(s.rank(method="first"), 10, labels=False))
wins, ratios, both = 0, [], 0
for _, g in T.groupby(["cat", "month", "vdec"]):
    a, o = g[g["ad"] == 1]["rpm"], g[g["ad"] == 0]["rpm"]
    if len(a) >= 5 and len(o) >= 5:
        both += 1
        wins += a.median() > o.median()
        ratios.append(a.median() / o.median())
R["D3"] = {"cells_with_both": both, "cells_ad_higher": wins, "share_ad_higher": round(wins / both, 3) if both else None,
           "median_ratio_ad_over_organic": round(float(np.median(ratios)), 3) if ratios else None,
           "supported": bool(both and wins / both >= 2 / 3),
           "pooled_rpm_median": {"ad": round(float(ads["rpm"].median()), 2), "organic": round(float(org["rpm"].median()), 2)},
           "revenue_share_from_ad_videos": round(float(ads["revenue"].sum() / T["revenue"].sum()), 3)}

# ------------------------------------------------------------------ D4 creator structure
d4 = []
months = sorted(T["month"].unique())
for (c, m), g in T.groupby(["cat", "month"]):
    by = g.groupby("creator")["revenue"].sum().sort_values(ascending=False)
    mdate = pd.Timestamp(m + "-01")
    deb = pd.to_datetime(g["creator_debut"], errors="coerce")
    new = g[(mdate - deb).dt.days <= 90]
    nxt = months[months.index(m) + 1] if months.index(m) + 1 < len(months) else None
    persist = None
    if nxt:
        nx = set(T[(T["cat"] == c) & (T["month"] == nxt)]["creator"])
        persist = len(set(g["creator"]) & nx) / max(1, g["creator"].nunique())
    d4.append({"cat": c, "month": m, "creators": g["creator"].nunique(), "videos": len(g),
               "top10_creator_share": by.head(10).sum() / by.sum(), "new_creator_rev_share": new["revenue"].sum() / g["revenue"].sum(),
               "creator_persistence_next_month": persist})
d4 = pd.DataFrame(d4)
R["D4"] = {k: [round(float(d4[k].quantile(q)), 3) for q in (.1, .5, .9)] for k in
           ("creators", "top10_creator_share", "new_creator_rev_share", "creator_persistence_next_month")}
R["D4"]["note"] = "p10/p50/p90 across category-months (top-300 videos)"

# ------------------------------------------------------------------ D5 (H-C2): detail-sample creators/videos -> T1
Fd = F.build_features()
det = pd.read_sql_query("""select d.product_id pid, q.month, d.creator_number, d.video_number, d.live_number
    from product_details d join pulls q using(pull_id) where q.month is not null and q.kind='detail'""", con)
x = Fd.merge(det, on=["pid", "month"]).dropna(subset=["T1"])
x = x[x["mi"] <= panel.MIDX["2026-08"]]
out5 = {"n": len(x), "base_T1": round(float(x["T1"].mean()), 3)}
for var in ("creator_number", "video_number", "live_number"):
    z = np.log1p(x[var])
    zs = (z - z.mean()) / z.std()
    X = pd.concat([zs.rename(var), x[["rank_pct", "log_rev_cut"]], pd.get_dummies(x["cat"], prefix="c", drop_first=True).astype(float)], axis=1)
    try:
        m = sm.Logit(x["T1"], sm.add_constant(X)).fit(disp=0, method="newton", maxiter=200)
        ci = m.conf_int().loc[var]
        out5[var] = {"OR_per_sd": round(float(np.exp(m.params[var])), 3), "ci95": [round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)],
                     "p": round(float(m.pvalues[var]), 4), "supported": bool(np.exp(ci[0]) > 1)}
    except Exception as ex:
        out5[var] = {"error": repr(ex)}
R["D5_H-C2"] = out5

# ------------------------------------------------------------------ D6 (H-C3): concentration for Sep products, frozen for the forward test
P = V[(V["kind"] == "product_videos") & (V["month"] == "2026-09") & V["pid"].notna()].drop_duplicates(["pid", "video_id"])
P = P.sort_values("revenue", ascending=False).groupby("pid").head(100)
rows = []
for pid, g in P.groupby("pid"):
    tot = g["revenue"].sum()
    if tot <= 0:
        continue
    byc = g.groupby("creator")["revenue"].sum().sort_values(ascending=False)
    rows.append({"pid": pid, "videos": len(g), "creators": g["creator"].nunique(), "top_video_share": g["revenue"].max() / tot,
                 "top_creator_share": byc.iloc[0] / tot, "top3_creator_share": byc.head(3).sum() / tot,
                 "ad_share_of_video_rev": g.loc[g["ad"] == 1, "revenue"].sum() / tot})
conc = pd.DataFrame(rows)
top9 = Fd[Fd["month"] == "2026-09"][["pid", "cat", "rank"]]
conc = conc.merge(top9.sort_values("rank").drop_duplicates("pid"), on="pid", how="left")
R["D6"] = {"products": len(conc), "in_top500_sep": int(conc["rank"].notna().sum()),
           **{k: [round(float(conc[k].quantile(q)), 3) for q in (.1, .5, .9)] for k in
              ("videos", "creators", "top_video_share", "top_creator_share", "top3_creator_share", "ad_share_of_video_rev")}}
fw = ROOT / "registry" / "forward_test_video_conc_2026-09.csv"
if not fw.exists():
    conc.to_csv(fw, index=False)
    sha = hashlib.sha256(fw.read_bytes()).hexdigest()
    R["D6"]["forward_file"] = {"file": str(fw.relative_to(ROOT)), "sha256": sha,
                               "test": "Spearman(top_creator_share, in Oct-2026 top 500) < 0 among products ranked 101-500 in Sep"}

# ------------------------------------------------------------------ D7 (H-C5): sample size for a confirmatory paired creative study
alpha, power, k = 0.05, 0.8, 10
za, zb = norm.ppf(1 - alpha / k / 2), norm.ppf(power)
sizes = []
for pd_ in (0.2, 0.3, 0.5):
    for ratio in (2.0, 3.0):
        p10 = pd_ * ratio / (1 + ratio)
        p01 = pd_ - p10
        delta = p10 - p01
        n = (za * math.sqrt(pd_) + zb * math.sqrt(pd_ - delta ** 2)) ** 2 / delta ** 2
        sizes.append({"discordant_share": pd_, "discordant_ratio": ratio, "pairs_needed": math.ceil(n)})
R["D7"] = {"alpha_per_test": alpha / k, "power": power, "scenarios": sizes,
           "prior_study": "91 pairs (VIDEO_STUDY_2026-10.md); only ad=1 survived 152 tests"}

(ROOT / "_work" / "phase_d_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
for k_ in ("D1", "D2", "D3", "D4", "D5_H-C2", "D6", "D7"):
    print(k_, json.dumps(R[k_], default=str)[:1500])
