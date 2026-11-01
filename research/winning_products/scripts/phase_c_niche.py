"""Phase C, value of the niche Tier 2 data (registry/PHASE_C_PLAN.md §5: H-N1, H-N2, H-N3, expansion rule). Read-only.
Writes _work/phase_c_niche.json. Run: python -I research/winning_products/scripts/phase_c_niche.py
"""
import glob
import json
import math
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features as F  # noqa: E402
import panel  # noqa: E402
import phase_c as C  # noqa: E402  (reuses its fitted helpers; importing runs phase_c's all-category analysis)

warnings.filterwarnings("ignore")
NICHE = ["601152", "601352", "605248", "953224"]
TEST = C.H1_TEST
D = C.D
R = {}


def walk_compare(U, y, base_feats, extra_feats, k=20):
    """Per test month: M1 with and without extra features; returns per-month metrics and P@k differences."""
    rows = []
    for t in TEST:
        tr, te = U[U["mi"] <= t - 1], U[U["mi"] == t]
        if te.empty or tr[y].nunique() < 2:
            continue
        pf = C.fit_logit(tr, te, base_feats + extra_feats, y)
        pb = C.fit_logit(tr, te, base_feats, y)
        mf, mb = C.metrics(te, pf, y), C.metrics(te, pb, y)
        rows.append({"month": panel.MONTHS[t], "with": mf, "without": mb, "d": mf[f"P@{k}"] - mb[f"P@{k}"],
                     "dAUC": mf["AUC"] - mb["AUC"]})
    d = [r["d"] for r in rows]
    ci, p = C.boot_ci(d)
    pos = sum(x > 0 for x in d)
    return {"per_month": rows, f"dP@{k}_mean": round(float(np.mean(d)), 4), "ci95": ci, "p_boot": round(p, 4),
            "months_positive": f"{pos}/{len(d)}", "dAUC_mean": round(float(np.mean([r["dAUC"] for r in rows])), 4),
            "supported": bool(ci[0] > 0 and pos >= math.ceil(2 * len(d) / 3))}


# ------------------------------------------------------------------ deep rows (ranks 501-1,000), full fields
con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
deep = pd.read_sql_query(f"""select p.product_id pid, q.category_id cat, q.month, p.position + (q.page-1)*100 rank, p.revenue,
        p.unit_price asp, p.video_revenue, p.live_revenue, p.launch_date, p.revenue_growth_rate kalo_g, p.seller_id
    from products p join pulls q using(pull_id)
    where q.kind='top_deep' and q.category_id in ({",".join("?" * 4)}) and q.page between 6 and 10 and q.success=1""",
                         con, params=NICHE).drop_duplicates(["pid", "cat", "month"])
deep["mi"] = deep["month"].map(panel.MIDX)
R["deep_rows"] = len(deep)
deep_key = {(p, c, m): (r, rv) for p, c, m, r, rv in zip(deep["pid"], deep["cat"], deep["mi"], deep["rank"], deep["revenue"])}

# ------------------------------------------------------------------ H-N1: deep visibility in niche T1
N = D[D["cat"].isin(NICHE) & D["rank"].between(101, 500) & D["T1"].notna()].copy()
N["in_deep_p1"] = [float((p, c, m - 1) in deep_key) for p, c, m in zip(N["pid"], N["cat"], N["mi"])]
N["deep_g"] = [float(np.clip(math.log(rv / deep_key[(p, c, m - 1)][1]), -3, 3)) if (ne == 1 and (p, c, m - 1) in deep_key and m - 1 >= 1) else 0.0
               for p, c, m, rv, ne in zip(N["pid"], N["cat"], N["mi"], N["revenue"], N["new_entrant"])]
R["H-N1"] = walk_compare(N, "T1", F.NUM, ["in_deep_p1", "deep_g"])
R["H-N1"]["share_new_entrants_seen_in_deep"] = round(float(N.loc[N["new_entrant"] == 1, "in_deep_p1"].mean()), 3)

# ------------------------------------------------------------------ H-N3: shop in the category's top-100 shops at m
shops = {}
for f in glob.glob(str(panel.HUB / "research" / "kalodata" / "raw" / "gaps_tier2" / "shops_*.json")):
    name = Path(f).stem.split("_")  # shops_<month>_<cat>
    doc = json.load(open(f, encoding="utf-8"))["response"]
    for s in doc.get("data") or []:
        shops[(str(s.get("shop_id")), name[2], panel.MIDX[name[1]])] = s.get("rank") or 0
N["shop_top100"] = [float((str(s), c, m) in shops) for s, c, m in zip(N["seller_id"], N["cat"], N["mi"])]
N["shop_rank_pct"] = [shops.get((str(s), c, m), 150) / 100 for s, c, m in zip(N["seller_id"], N["cat"], N["mi"])]
R["H-N3"] = walk_compare(N, "T1", F.NUM, ["shop_top100", "shop_rank_pct"])
R["H-N3"]["share_products_in_top100_shops"] = round(float(N["shop_top100"].mean()), 3)

# ------------------------------------------------------------------ H-N2: can the 501-1,000 band be ranked for break-in?
top, lists = panel.build()
top_key = set(zip(top["pid"], top["cat"], top["mi"]))
top_rev = {(p, c, m): r for p, c, m, r in zip(top["pid"], top["cat"], top["mi"], top["revenue"])}
cut = top.groupby(["cat", "mi"])["revenue"].min().to_dict()
asp_med = top.groupby(["cat", "mi"])["asp"].median().to_dict()
ris = set(zip(*[lists.loc[lists["kind"] == "risers", c] for c in ("pid", "cat")],
              lists.loc[lists["kind"] == "risers", "month"].map(panel.MIDX)))
B = deep[deep["mi"] >= F.FIRST_CUTOFF].copy()
B["band_rank_pct"] = (B["rank"] - 500) / 500
B["log_rev_cut"] = np.log(B["revenue"] / [cut[(c, m)] for c, m in zip(B["cat"], B["mi"])])
prev_rev = [top_rev.get((p, c, m - 1)) or (deep_key.get((p, c, m - 1)) or (None, None))[1] for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
B["seen_p1"] = [float(v is not None) for v in prev_rev]
B["was_top_p1"] = [float((p, c, m - 1) in top_key) for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
B["mom_g"] = [float(np.clip(math.log(r / v), -3, 3)) if v else 0.0 for r, v in zip(B["revenue"], prev_rev)]
B["kalo_g"] = np.sign(B["kalo_g"]) * np.log1p(B["kalo_g"].abs())
B["log_asp"] = np.log(B["asp"].clip(lower=0.01))
B["asp_rel"] = np.log(B["asp"].clip(lower=0.01) / np.array([asp_med[(c, m)] for c, m in zip(B["cat"], B["mi"])]).clip(0.01))
B["age"] = (B["month"].map(F._ym) - B["launch_date"].map(F._ym)).clip(0, 36)
B["video_sh"], B["live_sh"] = B["video_revenue"] / B["revenue"], B["live_revenue"] / B["revenue"]
B["prev_riser"] = [float((p, c, m - 1) in ris) for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
B["enter"] = [float((p, c, m + 1) in top_key) if m + 1 <= panel.MIDX["2026-09"] else np.nan for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
BF = ["band_rank_pct", "log_rev_cut", "seen_p1", "was_top_p1", "mom_g", "kalo_g", "log_asp", "asp_rel", "age", "video_sh",
      "live_sh", "prev_riser"]
BL = B[B["enter"].notna()]
per = []
for t in TEST:
    tr, te = BL[BL["mi"] <= t - 1], BL[BL["mi"] == t]
    p = C.fit_logit(tr, te, BF, "enter")
    def catp(score, k=20):
        s = pd.Series(score, index=te.index)
        return float(np.mean([te.loc[s[g.index].sort_values(ascending=False).index[:k], "enter"].mean() for _, g in te.groupby("cat")]))
    per.append({"month": panel.MONTHS[t], "base": float(te["enter"].mean()), "M1_catP@20": catp(p),
                "B1_revenue_catP@20": catp(te["log_rev_cut"].values), "B3_growth_catP@20": catp(te["mom_g"].values),
                "AUC_M1": float(C.roc_auc_score(te["enter"], p))})
pf = pd.DataFrame(per)
d = (pf["M1_catP@20"] - pf["B1_revenue_catP@20"]).tolist()
ci, pb = C.boot_ci(d)
cov = []
for t in range(F.FIRST_CUTOFF, panel.MIDX["2026-09"]):  # entrants at t+1 (niche), where were they at t?
    ent = D[D["cat"].isin(NICHE) & (D["mi"] == t + 1) & (D["new_entrant"] == 1)]
    if ent.empty:
        continue
    in_deep = np.mean([(p, c, t) in deep_key for p, c in zip(ent["pid"], ent["cat"])])
    in_ris = np.mean([(p, c, t) in ris for p, c in zip(ent["pid"], ent["cat"])])
    either = np.mean([((p, c, t) in deep_key) or ((p, c, t) in ris) for p, c in zip(ent["pid"], ent["cat"])])
    cov.append({"entry_month": panel.MONTHS[t + 1], "entrants": len(ent), "in_501_1000_prev": round(float(in_deep), 3),
                "in_riser_prev": round(float(in_ris), 3), "in_either": round(float(either), 3)})
cv = pd.DataFrame(cov)
R["H-N2"] = {"per_month": per, "mean": pf.drop(columns="month").mean().round(4).to_dict(),
             "M1_vs_B1_dcatP@20": round(float(np.mean(d)), 4), "ci95": ci, "p_boot": round(pb, 4),
             "coverage_by_month": cov, "coverage_mean": cv[["in_501_1000_prev", "in_riser_prev", "in_either"]].mean().round(3).to_dict(),
             "M1_over_base_ratio": round(float(pf["M1_catP@20"].mean() / pf["base"].mean()), 2)}
cov_ok = R["H-N2"]["coverage_mean"]["in_501_1000_prev"] >= 0.30
prec_ok = R["H-N2"]["M1_over_base_ratio"] >= 2.0
R["expansion_rule"] = {"H-N2_coverage>=30%": bool(cov_ok), "H-N2_P@20>=2x_base": bool(prec_ok),
                       "H-N1_supported": R["H-N1"]["supported"], "H-N3_supported": R["H-N3"]["supported"],
                       "recommend_deep_band_all_categories": bool((cov_ok and prec_ok) or R["H-N1"]["supported"]),
                       "recommend_shop_ranks_all_categories": R["H-N3"]["supported"]}
(panel.HUB / "research" / "winning_products" / "_work" / "phase_c_niche.json").write_text(json.dumps(R, indent=1, default=float), encoding="utf-8")
for k in ("H-N1", "H-N3"):
    print(k, {x: R[k][x] for x in R[k] if x != "per_month"})
print("H-N2", {x: R["H-N2"][x] for x in R["H-N2"] if x not in ("per_month", "coverage_by_month")})
print(pd.DataFrame(per).round(3).to_string(index=False))
print(cv.to_string(index=False))
print("RULE", R["expansion_rule"])
