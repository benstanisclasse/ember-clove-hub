"""Phase G: discovery-strategy back-test (G1, H-G2), calibration (G2), scoring of the Phase F candidates (G4) and the
Sep-2026 strategy forward freeze (G5). registry/PHASE_G_PLAN.md, frozen before this ran. Read-only on kalodata.db.
Writes _work/phase_g_results.json, _work/phase_g_scores.csv and, once, registry/forward_test_strategies_2026-09.csv.
Run: python -I research/winning_products/scripts/phase_g.py
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features as F  # noqa: E402
import panel  # noqa: E402
import phase_c as C  # noqa: E402
import scoring  # noqa: E402

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
ROOT = panel.HUB / "research" / "winning_products"
W = ROOT / "_work"
SEED, BOOT, K = 20261101, 2000, 20
RNG = np.random.default_rng(SEED)
PRE_OWNED = "856720"
STRATS = ["A Emerging", "B Proven", "C Underexploited", "D Creative-driven", "F Sustainable"]
R = {"plan": "registry/PHASE_G_PLAN.md"}

top, _ = panel.build()
D = C.D
pres = set(zip(top["pid"], top["cat"], top["mi"]))


def underexploited(t):
    """Categories (27, Pre-Owned excluded) in the top tercile of entrant 2-month survival (entries m with m+2 <= t) and
    not in the top tercile of top-3 shop share at t."""
    rows = []
    for c, g in top.groupby("cat"):
        if c == PRE_OWNED:
            continue
        ent = kept = 0
        for m in range(2, t - 1):
            new = [p for p in g.loc[g["mi"] == m, "pid"] if (p, c, m - 1) not in pres]
            ent += len(new)
            kept += sum((p, c, m + 2) in pres for p in new)
        gt = g[g["mi"] == t]
        sh = gt.groupby("seller_id")["revenue"].sum() / gt["revenue"].sum()
        rows.append({"cat": c, "surv": kept / ent if ent else np.nan, "top3": sh.sort_values(ascending=False).head(3).sum()})
    Q = pd.DataFrame(rows)
    hi_s, hi_c = Q["surv"].quantile(2 / 3), Q["top3"].quantile(2 / 3)
    return set(Q.loc[(Q["surv"] >= hi_s) & (Q["top3"] < hi_c), "cat"])


def eligible(df, t, under):
    return {"A Emerging": df["age"] <= 3, "B Proven": df["months_top_last3"] == 3, "C Underexploited": df["cat"].isin(under),
            "D Creative-driven": df["video_sh"] >= 0.70, "F Sustainable": pd.Series(True, index=df.index)}


def boot(diff):
    diff = np.asarray(diff, float)
    b = np.array([RNG.choice(diff, len(diff)).mean() for _ in range(BOOT)])
    return [round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)], min(1.0, float(min(np.mean(b <= 0), np.mean(b >= 0)) * 2))


# ------------------------------------------------------------------ G1 strategy back-test
U = D[C.mid(D) & D["T4"].notna()]
per, pooled, unders = {}, [], {}
for t in C.T4_TEST:
    tr, te = U[U["mi"] <= t - 3], U[U["mi"] == t].copy()
    te["p"] = C.fit_logit(tr, te, F.NUM, "T4")
    pooled.append(te[["p", "T4"]])
    under = underexploited(t)
    unders[panel.MONTHS[t]] = sorted(under)
    el = eligible(te, t, under)
    res = {}
    for s in STRATS:
        e = te[el[s].fillna(False)]
        r = {"n_eligible": len(e), "base": float(e["T4"].mean()) if len(e) else None}
        if len(e) >= K:
            r["P@20"] = float(e.sort_values("p", ascending=False)["T4"].head(K).mean())
            r["B1@20"] = float(e.sort_values("log_rev_cut", ascending=False)["T4"].head(K).mean())
        res[s] = r
    per[panel.MONTHS[t]] = res
R["G1_per_month"] = per
R["G1_underexploited_categories"] = unders

summ, pv = {}, {}
for s in STRATS:
    ms = [m for m in per if "P@20" in per[m][s]]
    p20 = [per[m][s]["P@20"] for m in ms]
    d_base = [per[m][s]["P@20"] - per[m][s]["base"] for m in ms]
    d_b1 = [per[m][s]["P@20"] - per[m][s]["B1@20"] for m in ms]
    row = {"months_tested": len(ms), "mean_n_eligible": round(float(np.mean([per[m][s]["n_eligible"] for m in per])), 1),
           "mean_base": round(float(np.mean([per[m][s]["base"] for m in per if per[m][s]["base"] is not None])), 4),
           "mean_P@20": round(float(np.mean(p20)), 4) if p20 else None}
    if ms:
        row["vs_base"] = {"mean": round(float(np.mean(d_base)), 4), "ci95": boot(d_base)[0]}
        row["vs_B1"] = {"mean": round(float(np.mean(d_b1)), 4), "ci95": boot(d_b1)[0], "months_ahead": f"{sum(d > 0 for d in d_b1)}/{len(d_b1)}"}
    if s != "F Sustainable" and ms:
        d_f = [per[m][s]["P@20"] - per[m]["F Sustainable"]["P@20"] for m in ms]
        ci, p = boot(d_f)
        same = max(sum(d > 0 for d in d_f), sum(d < 0 for d in d_f))
        row["vs_F"] = {"mean": round(float(np.mean(d_f)), 4), "ci95": ci, "p_boot": round(p, 4), "same_sign_months": f"{same}/{len(d_f)}"}
        pv[s] = p
    summ[s] = row
order, running = sorted(pv, key=pv.get), 0.0
for i, s in enumerate(order):
    running = max(running, min(1.0, pv[s] * (len(order) - i)))
    v = summ[s]["vs_F"]
    same = int(v["same_sign_months"].split("/")[0])
    v["p_holm"] = round(running, 4)
    v["supported"] = bool((v["ci95"][0] > 0 or v["ci95"][1] < 0) and same >= 3 and running < 0.05)
R["G1_summary"] = summ

# ------------------------------------------------------------------ G2 calibration (pooled test-month M1 T4 predictions)
P = pd.concat(pooled)
P["p"] = P["p"].clip(1e-4, 1 - 1e-4)
brier = float(((P["p"] - P["T4"]) ** 2).mean())
brier0 = float(((P["T4"].mean() - P["T4"]) ** 2).mean())
lg = sm.Logit(P["T4"], sm.add_constant(np.log(P["p"] / (1 - P["p"])))).fit(disp=0)
P["dec"] = pd.qcut(P["p"].rank(method="first"), 10, labels=False) + 1
R["G2"] = {"n": len(P), "brier": round(brier, 4), "brier_base_rate": round(brier0, 4), "skill": round(1 - brier / brier0, 4),
           "slope": round(float(lg.params.iloc[1]), 3), "intercept": round(float(lg.params.iloc[0]), 3),
           "reliability": P.groupby("dec").agg(pred=("p", "mean"), obs=("T4", "mean"), n=("T4", "size")).round(3).reset_index().to_dict("records")}
R["G2"]["report_as"] = "probability" if 0.8 <= R["G2"]["slope"] <= 1.2 else "within-pool percentile"

# ------------------------------------------------------------------ G5 forward freeze (frozen T4_M1, no refit)
SEP = panel.MIDX["2026-09"]
fw = pd.read_csv(ROOT / "registry" / "forward_test_2026-09.csv", dtype={"pid": str, "cat": str}).query("primary_universe == 1")
sepf = D[D["mi"] == SEP][["pid", "cat", "age", "months_top_last3", "video_sh", "log_rev_cut"]]
fs = fw.merge(sepf, on=["pid", "cat"], how="left")
under_sep = underexploited(SEP)
el = eligible(fs, SEP, under_sep)
frz = []
for s in STRATS:
    e = fs[el[s].fillna(False)].sort_values("T4_M1", ascending=False).head(K)
    frz.append(e.assign(strategy=s)[["strategy", "pid", "cat", "rank", "revenue", "T4_M1", "age", "months_top_last3", "video_sh"]])
frz = pd.concat(frz)
ff = ROOT / "registry" / "forward_test_strategies_2026-09.csv"
if not ff.exists():
    frz.to_csv(ff, index=False)
R["G5"] = {"file": "registry/forward_test_strategies_2026-09.csv", "rows": len(frz), "underexploited_sep": sorted(under_sep),
           "sha256": hashlib.sha256(ff.read_bytes()).hexdigest(),
           "tests": ["(i) T1 P@20 per strategy (Oct-2026 top 500)", "(ii) T4 P@20 per strategy (Oct-Dec 2026 top 500)", "each vs F, descriptive"]}

# ------------------------------------------------------------------ G4 scoring the Phase F candidates
con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
cand = pd.read_csv(W / "phase_f_candidates.csv", dtype={"pid": str, "cat": str})
prod = pd.read_csv(W / "phase_f_products.csv", dtype={"kalo_pid": str, "cj_pid": str})
vs = pd.read_sql_query("""select p.product_id pid, q.category_id cat, p.video_revenue, p.revenue from products p
    join pulls q using(pull_id) where q.month='2026-09' and q.kind in ('top','top_deep')""", con).drop_duplicates(["pid", "cat"])
vs["video_sh"] = vs["video_revenue"].astype(float) / vs["revenue"].astype(float)
band = pd.read_csv(ROOT / "registry" / "forward_test_band_2026-09.csv", dtype={"pid": str, "cat": str})
pct = {"A": fw.set_index(["pid", "cat"])["T4_M1"].rank(pct=True), "B": band.set_index(["pid", "cat"])["enter_M1"].rank(pct=True)}
S = cand.merge(prod.drop(columns=["pool", "cat_name", "name", "rank", "score", "asp"]), on="cand", how="left") \
        .merge(vs[["pid", "cat", "video_sh"]], on=["pid", "cat"], how="left")
S["mo_pct"] = [pct[p].get((i, c)) for p, i, c in zip(S["pool"], S["pid"], S["cat"])]
G = scoring.score(S, r5=True)
G.to_csv(W / "phase_g_scores.csv", index=False)
gate_counts = {g: int(G["gates_failed"].str.contains(g).sum()) for g in ("R1", "R2", "R3", "R4", "R5", "R6", "R7")}
R["G4"] = {"n": len(G), "not_rejected": G.loc[G["commercial_readiness"] != "Rejected", "cand"].tolist(),
           "gate_counts": gate_counts, "readiness": G["commercial_readiness"].value_counts().to_dict(),
           "rejected_only_by": {g: G.loc[G["gates_failed"] == g, "cand"].tolist() for g in gate_counts}}

(W / "phase_g_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps(R["G1_summary"], indent=1))
print("G2", {k: v for k, v in R["G2"].items() if k != "reliability"})
print("G5", R["G5"]["rows"], R["G5"]["underexploited_sep"])
print("G4", json.dumps(R["G4"], indent=0))
print(G[G["phase_f_class"].isin(["Feasible", "Marginal"])][["cand", "name", "mo_pct", "be_roas", "video_sh", "ad_suitability",
      "gates_failed", "brand_tokens_in_cj_name", "risk_flags", "commercial_readiness"]].assign(name=lambda x: x["name"].str[:40]).to_string(index=False))
