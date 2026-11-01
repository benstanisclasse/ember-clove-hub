"""Break-in from ranks 501-1,000 (H-N2 spec, unchanged) as a function, for the H-N2b replication and the band freeze.

  python -I research/winning_products/scripts/phase_c_band.py check        niche cats: must reproduce H-N2 exactly
  python -I research/winning_products/scripts/phase_c_band.py replicate    24 non-niche cats (H-N2b, registered)
  python -I research/winning_products/scripts/phase_c_band.py freeze       all 28 cats: score the 2026-09 band once
Read-only on kalodata.db. Results: _work/phase_c_band_<mode>.json; freeze: registry/forward_test_band_2026-09.csv.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features as F  # noqa: E402
import panel  # noqa: E402
import phase_c as C  # noqa: E402

warnings.filterwarnings("ignore")
NICHE = ["601152", "601352", "605248", "953224"]
BF = ["band_rank_pct", "log_rev_cut", "seen_p1", "was_top_p1", "mom_g", "kalo_g", "log_asp", "asp_rel", "age", "video_sh",
      "live_sh", "prev_riser"]
ROOT = panel.HUB / "research" / "winning_products"


def band_frame(cats):
    con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
    deep = pd.read_sql_query(f"""select p.product_id pid, q.category_id cat, q.month, p.position + (q.page-1)*100 rank,
            p.revenue, p.unit_price asp, p.video_revenue, p.live_revenue, p.launch_date, p.revenue_growth_rate kalo_g
        from products p join pulls q using(pull_id)
        where q.kind='top_deep' and q.category_id in ({",".join("?" * len(cats))}) and q.page between 6 and 10
              and q.success=1""", con, params=cats).drop_duplicates(["pid", "cat", "month"])
    deep["mi"] = deep["month"].map(panel.MIDX)
    deep_key = {(p, c, m): rv for p, c, m, rv in zip(deep["pid"], deep["cat"], deep["mi"], deep["revenue"])}
    top, lists = panel.build()
    top_key = set(zip(top["pid"], top["cat"], top["mi"]))
    top_rev = {(p, c, m): r for p, c, m, r in zip(top["pid"], top["cat"], top["mi"], top["revenue"])}
    cut = top.groupby(["cat", "mi"])["revenue"].min().to_dict()
    asp_med = top.groupby(["cat", "mi"])["asp"].median().to_dict()
    rl = lists[lists["kind"] == "risers"]
    ris = set(zip(rl["pid"], rl["cat"], rl["month"].map(panel.MIDX)))
    B = deep[deep["mi"] >= F.FIRST_CUTOFF].copy()
    B["band_rank_pct"] = (B["rank"] - 500) / 500
    B["log_rev_cut"] = np.log(B["revenue"] / [cut[(c, m)] for c, m in zip(B["cat"], B["mi"])])
    prev_rev = [top_rev.get((p, c, m - 1)) or deep_key.get((p, c, m - 1)) for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
    B["seen_p1"] = [float(v is not None) for v in prev_rev]
    B["was_top_p1"] = [float((p, c, m - 1) in top_key) for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
    B["mom_g"] = [float(np.clip(math.log(r / v), -3, 3)) if v else 0.0 for r, v in zip(B["revenue"], prev_rev)]
    B["kalo_g"] = np.sign(B["kalo_g"]) * np.log1p(B["kalo_g"].abs())
    B["log_asp"] = np.log(B["asp"].clip(lower=0.01))
    B["asp_rel"] = np.log(B["asp"].clip(lower=0.01) / np.array([asp_med[(c, m)] for c, m in zip(B["cat"], B["mi"])]).clip(0.01))
    B["age"] = (B["month"].map(F._ym) - B["launch_date"].map(F._ym)).clip(0, 36)
    B["video_sh"], B["live_sh"] = B["video_revenue"] / B["revenue"], B["live_revenue"] / B["revenue"]
    B["prev_riser"] = [float((p, c, m - 1) in ris) for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
    B["enter"] = [float((p, c, m + 1) in top_key) if m + 1 <= panel.MIDX["2026-09"] else np.nan
                  for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
    return B, deep_key, ris


def catp(te, score, k=20):
    s = pd.Series(score, index=te.index)
    return float(np.mean([te.loc[s[g.index].sort_values(ascending=False).index[:k], "enter"].mean() for _, g in te.groupby("cat")]))


def evaluate(cats):
    B, deep_key, ris = band_frame(cats)
    BL = B[B["enter"].notna()]
    per = []
    for t in C.H1_TEST:
        tr, te = BL[BL["mi"] <= t - 1], BL[BL["mi"] == t]
        p = C.fit_logit(tr, te, BF, "enter")
        per.append({"month": panel.MONTHS[t], "base": float(te["enter"].mean()), "M1_catP@20": catp(te, p),
                    "B1_revenue_catP@20": catp(te, te["log_rev_cut"].values), "B3_growth_catP@20": catp(te, te["mom_g"].values),
                    "AUC_M1": float(C.roc_auc_score(te["enter"], p))})
    pf = pd.DataFrame(per)
    d = (pf["M1_catP@20"] - pf["B1_revenue_catP@20"]).tolist()
    ci, pb = C.boot_ci(d)
    D = C.D
    cov = []
    for t in range(F.FIRST_CUTOFF, panel.MIDX["2026-09"]):
        ent = D[D["cat"].isin(cats) & (D["mi"] == t + 1) & (D["new_entrant"] == 1)]
        if ent.empty:
            continue
        cov.append({"entry_month": panel.MONTHS[t + 1], "entrants": len(ent),
                    "in_501_1000_prev": round(float(np.mean([(p, c, t) in deep_key for p, c in zip(ent["pid"], ent["cat"])])), 3),
                    "in_riser_prev": round(float(np.mean([(p, c, t) in ris for p, c in zip(ent["pid"], ent["cat"])])), 3)})
    cv = pd.DataFrame(cov)
    res = {"categories": cats, "band_rows": len(B), "per_month": per, "mean": pf.drop(columns="month").mean().round(4).to_dict(),
           "M1_vs_B1_dcatP@20": round(float(np.mean(d)), 4), "ci95": ci, "p_boot": round(pb, 4),
           "months_M1_ahead": f"{sum(x > 0 for x in d)}/{len(d)}", "coverage_by_month": cov,
           "coverage_mean": cv[["in_501_1000_prev", "in_riser_prev"]].mean().round(3).to_dict(),
           "M1_over_base_ratio": round(float(pf["M1_catP@20"].mean() / pf["base"].mean()), 2)}
    res["replicates"] = bool(res["coverage_mean"]["in_501_1000_prev"] >= 0.30 and res["M1_over_base_ratio"] >= 2.0 and ci[0] > 0)
    by_cat = []
    for c, g in BL[BL["mi"].isin(C.H1_TEST)].groupby("cat"):
        by_cat.append({"cat": c, "rows": len(g), "base": round(float(g["enter"].mean()), 3)})
    res["base_rate_by_category"] = by_cat
    return res


def freeze(cats):
    out_csv = ROOT / "registry" / "forward_test_band_2026-09.csv"
    if out_csv.exists():
        raise SystemExit("band freeze already exists")
    latest = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True).execute(
        "select max(month) from pulls where month is not null").fetchone()[0]
    if latest > "2026-09":
        raise SystemExit(f"kalodata.db already holds {latest}")
    B, _, _ = band_frame(cats)
    tr, te = B[B["enter"].notna()], B[B["mi"] == panel.MIDX["2026-09"]].copy()
    te["enter_M1"] = C.fit_logit(tr, te, BF, "enter")
    te["base_B1"] = te["log_rev_cut"]
    te[["pid", "cat", "month", "rank", "revenue", "enter_M1", "base_B1"]].to_csv(out_csv, index=False)
    sha = hashlib.sha256(out_csv.read_bytes()).hexdigest()
    rec = {"id": "EXP-C-004", "phase": "C", "at": "2026-11-01", "kind": "FORWARD TEST FREEZE (2026-09 ranks 501-1,000, 28 categories)",
           "file": "registry/forward_test_band_2026-09.csv", "sha256": sha, "rows": len(te), "db_latest_month_at_freeze": latest,
           "declared_primary": {"target": "enters the top 500 in 2026-10", "model": "enter_M1", "comparator": "base_B1",
                                "metric": "within-category P@20, averaged over categories"},
           "rules": "No refit. Outcomes from the sealed 2026-10 pull only."}
    with open(ROOT / "registry" / "experiments.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    print(rec)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "freeze":
        others = sorted(set(C.CATS) - {"834312"})
        freeze(others)
        sys.exit()
    cats = NICHE if mode == "check" else sorted(set(C.CATS) - set(NICHE) - {"834312"})
    r = evaluate(cats)
    (ROOT / "_work" / f"phase_c_band_{mode}.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
    print({k: r[k] for k in ("band_rows", "mean", "M1_vs_B1_dcatP@20", "ci95", "months_M1_ahead", "coverage_mean", "M1_over_base_ratio", "replicates")})
