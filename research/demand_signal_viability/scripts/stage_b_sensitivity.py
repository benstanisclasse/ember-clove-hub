"""Stage B sensitivity, post-hoc (DSI-B-001): the engine and the existing model WITHOUT Kalodata's revenue_growth_rate
(kalo_g), whose comparison window is undocumented and which tracks next-month growth more than its own month's growth
(stage_b_posthoc.json P2). Same universe, months, walk-forward scheme and metrics as stage_b.py. Read-only.
Writes _work/stage_b_sensitivity.json. Run: python -I research/demand_signal_viability/scripts/stage_b_sensitivity.py
"""
import json
import runpy
import sys
from pathlib import Path

import numpy as np

HUB = Path(__file__).resolve().parents[3]
sys.stdout.reconfigure(encoding="utf-8")
W = HUB / "research" / "demand_signal_viability" / "_work"
G = runpy.run_path(str(Path(__file__).with_name("stage_b.py")), run_name="stage_b_import")
U, C, catp, flagged, boot, top, panel = (G[k] for k in ("U", "C", "catp", "flagged", "boot", "top", "panel"))
ALL, BF, S1_TEST, S2_TEST = G["ALL"], G["BF"], G["S1_TEST"], G["S2_TEST"]
NOK_ALL = [f for f in ALL if f != "kalo_g"]
NOK_BF = [f for f in BF if f != "kalo_g"]
ever = {}
for p, c, m in zip(top["pid"], top["cat"], top["mi"]):
    ever.setdefault((p, c), []).append(m)
R = {}
for y, months, h in (("S1", S1_TEST, 1), ("S2", S2_TEST, 3)):
    L = U[U[y].notna()]
    rows = {k: [] for k in ("A Revenue", "E no kalo_g", "F logit no kalo_g", "F logit (with)")}
    first = {k: 0 for k in rows}
    for t in months:
        tr, te = L[L["mi"] <= t - h], L[L["mi"] == t]
        sc = {"A Revenue": te["log_rev_cut"].values, "E no kalo_g": C.fit_logit(tr, te, NOK_BF, y),
              "F logit no kalo_g": C.fit_logit(tr, te, NOK_ALL, y), "F logit (with)": C.fit_logit(tr, te, ALL, y)}
        prev = np.array([any(x < t for x in ever.get((p, c), [])) for p, c in zip(te["pid"], te["cat"])])
        for n, s in sc.items():
            rows[n].append(catp(te, s, y, 20))
            f = flagged(te, s, 20)
            first[n] += int(te.loc[f, y][~prev[te.index.get_indexer(f)]].sum())
    out = {n: {"catP@20": round(float(np.mean(v)), 4), "first_time_hits_per_month": round(first[n] / len(months), 1)} for n, v in rows.items()}
    d = [a - b for a, b in zip(rows["F logit no kalo_g"], rows["A Revenue"])]
    out["F_no_kalo_minus_revenue"] = {"mean": round(float(np.mean(d)), 4), "ci95": boot(d)[0], "months_ahead": f"{sum(x > 0 for x in d)}/{len(d)}"}
    d2 = [a - b for a, b in zip(rows["F logit (with)"], rows["F logit no kalo_g"])]
    out["kalo_g_contribution"] = {"mean": round(float(np.mean(d2)), 4), "ci95": boot(d2)[0]}
    R[y] = out
(W / "stage_b_sensitivity.json").write_text(json.dumps(R, indent=1), encoding="utf-8")
print(json.dumps(R, indent=1))
