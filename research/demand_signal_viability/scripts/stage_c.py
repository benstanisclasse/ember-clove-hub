"""Stage C: commercial feasibility of Kalodata x CJ (registry/STAGE_C_PLAN.md, frozen before this ran). Read-only on the
saved Phase F/H outputs. Modes:
  python -I research/demand_signal_viability/scripts/stage_c.py            funnel, effort, demand-vs-sourcing, rescore sample
  python -I research/demand_signal_viability/scripts/stage_c.py --kappa    agreement once _work/stage_c_rescore_blind.json exists
Writes _work/stage_c_results.json, _work/stage_c_funnel.csv, _work/stage_c_rescore_sample.json (+ answer key).
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8")
HUB = Path(__file__).resolve().parents[3]
WP = HUB / "research" / "winning_products" / "_work"
W = HUB / "research" / "demand_signal_viability" / "_work"
CJ = WP / "cj"
SEED = 20261103


def wilson(k, n, z=1.96):
    if not n:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def load_files():
    out = {}
    for f in CJ.glob("[FH][0-9][0-9].json"):
        out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return out


if "--kappa" in sys.argv:
    key = json.loads((W / "stage_c_rescore_key.json").read_text(encoding="utf-8"))
    blind = {r["id"]: r for r in json.loads((W / "stage_c_rescore_blind.json").read_text(encoding="utf-8"))}
    pairs = [(key[i]["collector_score"], blind[i]["score"], i) for i in key if i in blind]
    a = np.array([p[0] for p in pairs])
    b = np.array([p[1] for p in pairs])
    cats = [0, 1, 2]
    n = len(a)
    po = float((a == b).mean())
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    kappa = (po - pe) / (1 - pe) if pe < 1 else None
    w = lambda i, j: 1 - abs(i - j) / 2  # noqa: E731
    pow_ = np.mean([w(x, y) for x, y in zip(a, b)])
    pew = sum((a == i).mean() * (b == j).mean() * w(i, j) for i in cats for j in cats)
    kw = (pow_ - pew) / (1 - pew)
    conf = pd.crosstab(pd.Series(a, name="collector"), pd.Series(b, name="blind")).to_dict()
    dis = [{"id": i, "cand": key[i]["cand"], "collector": int(x), "blind": int(y), "blind_reason": blind[i].get("reason")}
           for x, y, i in pairs if x != y]
    verdict = "reliable enough to automate" if kappa >= 0.60 else "moderate: needs human review" if kappa >= 0.40 else "unreliable"
    R = json.loads((W / "stage_c_results.json").read_text(encoding="utf-8"))
    R["C3_match_reliability"] = {"n": n, "percent_agreement": round(po, 3), "kappa": round(kappa, 3), "kappa_linear_weighted": round(kw, 3),
                                 "confusion_collector_x_blind": {str(k): {str(kk): int(vv) for kk, vv in v.items()} for k, v in conf.items()},
                                 "verdict": verdict, "blind_scored_0": int((b == 0).sum()), "disagreements": dis}
    (W / "stage_c_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
    print(json.dumps(R["C3_match_reliability"], indent=1))
    sys.exit()

files = load_files()
cf = pd.read_csv(WP / "phase_f_candidates.csv", dtype={"pid": str, "cat": str})
ch = pd.read_csv(WP / "phase_h_candidates.csv", dtype={"pid": str, "cat": str})
pf = pd.read_csv(WP / "phase_f_products.csv", dtype={"kalo_pid": str, "cj_pid": str})
ph = pd.read_csv(WP / "phase_h_products.csv", dtype={"kalo_pid": str, "cj_pid": str})
gg = pd.read_csv(WP / "phase_g_scores.csv")
gh = pd.read_csv(WP / "phase_h_shortlist.csv")

# one row per unique candidate, lane-appropriate gates and demand percentile
rows = []
for _, r in pf.iterrows():
    lane = "validated" if r["pool"] == "A" else "early-stage"
    src = gh if (lane == "early-stage" and r["cand"] in set(gh["cand"])) else gg
    g = src.set_index("cand").loc[r["cand"]]
    c = cf.set_index("cand").loc[r["cand"]]
    rows.append({**r.to_dict(), "lane": lane, "gates_failed": g["gates_failed"], "passes_gates": g["commercial_readiness"] != "Rejected",
                 "mo_pct": g["mo_pct"], "revenue": c["revenue"], "units": c["units"]})
for _, r in ph[ph["cand"].str.startswith("H")].iterrows():
    g = gh.set_index("cand").loc[r["cand"]]
    c = ch.set_index("cand").loc[r["cand"]]
    rows.append({**r.to_dict(), "lane": "early-stage", "gates_failed": g["gates_failed"], "passes_gates": g["commercial_readiness"] != "Rejected",
                 "mo_pct": g["mo_pct"], "revenue": c["revenue"], "units": c["units"]})
D = pd.DataFrame(rows)
D["ineligible"] = D["class"] == "Ineligible"
X = D[~D["ineligible"]].copy()
X["F1"] = X["match_score"] >= 1
X["F2"] = X["match_score"] == 2
X["F3"] = X["F2"] & (X["n_in_stock"].fillna(0) > 0) & X["fulfilment"].isin(["High", "Medium"])
X["F4"] = X["F3"] & X["med_ship_base"].notna() & (X["med_slow"] == False)  # noqa: E712
X["F5"] = X["F4"] & (X["med_b_cba"] > 0)
X["F6"] = X["F5"] & (X["med_b_be_roas"] <= 3.0)
X["F7"] = X["F6"] & X["passes_gates"].astype(bool)
X["F8"] = X["F7"] & (X["med_b_be_roas"] <= 2.0) & (X["med_b_target_cac"] > 0)
X["F9"] = False
STAGES = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]
fun = []
for lane, g in [("all", X)] + list(X.groupby("lane")):
    n = len(g)
    fun.append({"lane": lane, "n": n, **{s: int(g[s].sum()) for s in STAGES},
                **{f"{s}_share": round(float(g[s].mean()), 3) for s in STAGES}, **{f"{s}_wilson": wilson(int(g[s].sum()), n) for s in STAGES}})
FUN = pd.DataFrame(fun)
FUN.to_csv(W / "stage_c_funnel.csv", index=False)
R = {"plan": "registry/STAGE_C_PLAN.md", "unique_candidates": len(D), "ineligible": int(D["ineligible"].sum()), "collected": len(X),
     "funnel": FUN.to_dict("records"), "categories": int(X["cat_name"].nunique())}
M2 = X[X["F2"]]
R["matched_profile"] = {"n": len(M2), "us_stock_share": round(float(M2["has_us_stock"].astype(bool).mean()), 3),
                        "supplier_shipped_share": round(float(M2["supplier_shipped"].astype(str).eq("True").mean()), 3),
                        "cost_pct_of_price_median": round(float((M2["cost_max"] / M2["asp"]).median()), 3),
                        "freight_pct_of_price_median_cn": round(float((M2.loc[M2["med_origin"] == "CN", "med_ship_base"] / M2.loc[M2["med_origin"] == "CN", "asp"]).median()), 3),
                        "median_contribution": round(float(M2["med_b_cba"].median()), 2),
                        "median_breakeven_cac": round(float(M2["med_b_cba"].clip(lower=0).median()), 2),
                        "median_target_cac_positive_share": round(float((M2["med_b_target_cac"] > 0).mean()), 3),
                        "branded_cap_share_of_score1": round(float(X.loc[X["match_score"] == 1, "branded_cap"].astype(str).eq("True").mean()), 3)}

# C4 demand rank vs sourceability
assoc = {}
for lane, g in X.groupby("lane"):
    g = g[g["mo_pct"].notna()]
    out = {"n": len(g)}
    for y in ("F2", "F7"):
        out[f"spearman_mo_pct_vs_{y}"] = round(float(spearmanr(g["mo_pct"], g[y].astype(int)).correlation), 3)
    out["spearman_mo_pct_vs_branded"] = round(float(spearmanr(g["mo_pct"], g["branded_cap"].astype(str).eq("True").astype(int)).correlation), 3)
    t = pd.qcut(g["revenue"].rank(method="first"), 3, labels=["low", "mid", "high"])
    out["by_revenue_tercile"] = {str(k): {"n": len(v), "F2": round(float(v["F2"].mean()), 3), "F7": round(float(v["F7"].mean()), 3),
                                          "branded": round(float(v["branded_cap"].astype(str).eq("True").mean()), 3),
                                          "revenue_range": [round(float(v["revenue"].min())), round(float(v["revenue"].max()))]}
                                 for k, v in g.groupby(t, observed=True)}
    assoc[lane] = out
R["C4_demand_vs_sourcing"] = assoc

# C5 effort
calls = []
for cand, d in files.items():
    if cand not in set(X["cand"]):
        continue
    s, det = len(d.get("searches") or []), len(d.get("considered") or [])
    v, i, fr = int(bool(d.get("variants"))), int(bool(d.get("inventory"))), len(d.get("freight") or [])
    calls.append({"cand": cand, "searches": s, "details": det, "variants": v, "inventory": i, "freight": fr,
                  "calls": s + det + v + i + fr, "points": 50 * s + 10 * (det + v + i + fr)})
CL = pd.DataFrame(calls)
# agent run records (task notifications): tokens, tool uses, wall seconds per collector batch
AGENTS = {"F": [(652419, 72, 1005692), (698653, 89, 1113258), (804863, 87, 1143895), (675223, 148, 1401749), (850667, 120, 1477912), (896973, 157, 1662090)],
          "H": [(579541, 112, 885820), (727086, 135, 990609), (662533, 109, 1005702), (654738, 142, 1020280), (721085, 167, 1202417), (835483, 141, 1323474)]}
n_cand = {"F": 70, "H": 71}
eff = {k: {"collectors": len(v), "candidates": n_cand[k], "tokens_per_candidate": round(sum(a for a, _, _ in v) / n_cand[k]),
           "tool_calls_per_candidate": round(sum(b for _, b, _ in v) / n_cand[k], 1),
           "wall_seconds_per_candidate_per_collector": round(sum(c for _, _, c in v) / 1000 / n_cand[k], 1),
           "elapsed_minutes_6_parallel": round(max(c for _, _, c in v) / 60000, 1)} for k, v in AGENTS.items()}
f7, f8 = int(X["F7"].sum()), int(X["F8"].sum())
R["C5_effort"] = {"cj_calls_per_candidate_mean": round(float(CL["calls"].mean()), 1), "cj_calls_by_type_mean": CL[["searches", "details", "variants", "inventory", "freight"]].mean().round(2).to_dict(),
                  "cj_points_per_candidate_mean": round(float(CL["points"].mean())), "agents": eff,
                  "candidates_per_gate_pass": round(len(X) / max(f7, 1), 1), "candidates_per_feasible": round(len(X) / max(f8, 1), 1),
                  "note": "human research time not measured; no user did this research by hand"}

# C3 sample for the blind re-score (no collector score, note or reasons; no variant lists, which exist only for score-2)
elig = X[X["match_score"].isin([1, 2]) & X["cj_pid"].notna()]
rng = np.random.default_rng(SEED)
pick = []
for s in (1, 2):
    ids = sorted(elig.loc[elig["match_score"] == s, "cand"])
    pick += list(rng.choice(ids, size=min(20, len(ids)), replace=False))
pick = list(rng.permutation(pick))
packets, key = [], {}
for j, cand in enumerate(pick):
    d = files[cand]
    det = d.get("detail") or {}
    src = cf if cand.startswith("F") else ch
    c = src.set_index("cand").loc[cand]
    pid = f"R{j + 1:02d}"
    packets.append({"id": pid, "tiktok_product_title": c["name"], "tiktok_category": c["cat_name"], "tiktok_price_usd": float(c["asp"]),
                    "cj_product_name": det.get("productNameEn") or (d.get("match") or {}).get("cj_name"),
                    "cj_category": det.get("categoryName"), "cj_material": det.get("material"), "cj_packing": det.get("packing"),
                    "cj_sell_price": det.get("sellPrice"), "cj_description_excerpt": det.get("description_excerpt")})
    key[pid] = {"cand": cand, "collector_score": int(d["match"]["score"]), "collector_branded_cap": d["match"].get("branded_cap")}
(W / "stage_c_rescore_sample.json").write_text(json.dumps(packets, indent=1, ensure_ascii=False), encoding="utf-8")
(W / "stage_c_rescore_key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
R["C3_sample"] = {"n": len(packets), "by_collector_score": {str(s): int(sum(v["collector_score"] == s for v in key.values())) for s in (1, 2)},
                  "fields_shown": list(packets[0].keys()), "deviation": "variant keys withheld: they exist only for score-2 files and would reveal the stratum"}
(W / "stage_c_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: R[k] for k in ("unique_candidates", "ineligible", "collected", "categories")}))
print(FUN[["lane", "n"] + STAGES].to_string(index=False))
print(json.dumps(R["matched_profile"]), "\n", json.dumps(R["C4_demand_vs_sourcing"], indent=1), "\n", json.dumps(R["C5_effort"], indent=1))
print(R["C3_sample"])
