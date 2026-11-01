"""Stage B post-hoc checks, added after the registered results (DSI-B-001 records them as post-hoc). Read-only.
P1. Where does the engine's S1 precision come from: products that were in the top 500 in some earlier month (re-entrants)
    vs genuinely first-time entrants? Same walk-forward scores as stage_b.py, recomputed here.
P2. Leakage check on Kalodata's revenue_growth_rate (kalo_g), the only signal that adds information beyond revenue:
    is it a per-month value, and does it track the month's own growth (past) or the next month's growth (future)?
Writes _work/stage_b_posthoc.json. Run: python -I research/demand_signal_viability/scripts/stage_b_posthoc.py
"""
import json
import runpy
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HUB = Path(__file__).resolve().parents[3]
sys.stdout.reconfigure(encoding="utf-8")
W = HUB / "research" / "demand_signal_viability" / "_work"
G = runpy.run_path(str(Path(__file__).with_name("stage_b.py")), run_name="stage_b_import")  # reuses universe and scores
U, top, M, panel, scores, flagged, FNAME, S1_TEST, LAST = (G[k] for k in ("U", "top", "M", "panel", "scores_by_month", "flagged",
                                                                         "FNAME", "S1_TEST", "LAST"))
R = {}
ever = {}
for p, c, m in zip(top["pid"], top["cat"], top["mi"]):
    ever.setdefault((p, c), []).append(m)
L = U[U["S1"].notna()]
rows = []
for t in S1_TEST:
    te = L[L["mi"] == t]
    prev_top = np.array([any(x < t for x in ever.get((p, c), [])) for p, c in zip(te["pid"], te["cat"])])
    for n in ("A Revenue", "B Growth", "D Momentum", "E Existing model", FNAME):
        f = flagged(te, scores[t][n].values, 20)
        sel = te.loc[f]
        pt = prev_top[te.index.get_indexer(f)]
        rows.append({"month": panel.MONTHS[t], "method": n, "flags": len(sel), "flags_prev_top_share": float(pt.mean()),
                     "hits": int(sel["S1"].sum()), "hits_first_time": int(sel["S1"][~pt].sum()), "hits_reentry": int(sel["S1"][pt].sum()),
                     "flags_first_time": int((~pt).sum())})
    R.setdefault("universe_prev_top_share", {})[panel.MONTHS[t]] = round(float(prev_top.mean()), 3)
D = pd.DataFrame(rows)
S = D.groupby("method")[["flags", "hits", "hits_first_time", "hits_reentry", "flags_first_time"]].sum()
S["precision_all"] = S["hits"] / S["flags"]
S["share_of_hits_reentry"] = S["hits_reentry"] / S["hits"]
S["precision_first_time_flags"] = S["hits_first_time"] / S["flags_first_time"].replace(0, np.nan)
S["first_time_hits_per_month"] = S["hits_first_time"] / len(S1_TEST)
R["P1_precision_source_top20"] = S.round(4).to_dict("index")

# P2: kalo_g leakage check, on products visible in consecutive months (any list) with our own month-over-month growth
raw = G["raw"]
x = raw.sort_values("rank").drop_duplicates(["pid", "cat", "mi"])[["pid", "cat", "mi", "revenue", "kalo_g"]].copy()
x["revenue"] = pd.to_numeric(x["revenue"], errors="coerce")
x["kalo_g"] = pd.to_numeric(x["kalo_g"], errors="coerce")
x = x[x["mi"] >= 1]
k = {(p, c, m): (r, g) for p, c, m, r, g in zip(x["pid"], x["cat"], x["mi"], x["revenue"], x["kalo_g"])}
past, fut, kg = [], [], []
for (p, c, m), (r, g) in k.items():
    a, b = k.get((p, c, m - 1)), k.get((p, c, m + 1))
    if a and b and m - 1 >= 1 and r > 0 and a[0] > 0 and b[0] > 0 and g == g and g != 100:
        past.append(np.log(r / a[0]))
        fut.append(np.log(b[0] / r))
        kg.append(g)
past, fut, kg = map(np.array, (past, fut, kg))
multi = x.groupby(["pid", "cat"])["kalo_g"].agg(["nunique", "size"])
multi = multi[multi["size"] >= 3]
R["P2_kalo_g"] = {"n_triples": len(kg),
                  "rho_with_own_month_growth_(m-1->m)": round(float(spearmanr(kg, past).correlation), 3),
                  "rho_with_next_month_growth_(m->m+1)": round(float(spearmanr(kg, fut).correlation), 3),
                  "rho_partial_next_given_own": round(float(spearmanr(kg - np.polyval(np.polyfit(past, kg, 1), past), fut).correlation), 3),
                  "products_with_3plus_months": len(multi), "share_with_kalo_g_constant_across_months": round(float((multi["nunique"] == 1).mean()), 4),
                  "share_value_100": round(float((x["kalo_g"] == 100).mean()), 4)}
(W / "stage_b_posthoc.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps(R, indent=1, default=str))
