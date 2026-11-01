"""Phase H, H4-H5: gates and scores for the early-stage pool, using Phase G's scoring (scoring.py, R5 replaced by the pre-CJ
units >= 100 floor) on the Phase F economics run with --phase h. registry/PHASE_H_PLAN.md. Read-only.
Writes _work/phase_h_shortlist.csv and _work/phase_h_results.json.
Run (after phase_f_economics.py --phase h): python -I research/winning_products/scripts/phase_h_shortlist.py
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scoring  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "_work"

cand = pd.read_csv(W / "phase_h_candidates.csv", dtype={"pid": str, "cat": str}).assign(pool="H")
prod = pd.read_csv(W / "phase_h_products.csv", dtype={"kalo_pid": str, "cj_pid": str})
band = pd.read_csv(ROOT / "registry" / "forward_test_band_2026-09.csv", dtype={"pid": str, "cat": str})
pct = band.set_index(["pid", "cat"])["enter_M1"].rank(pct=True)
S = cand.merge(prod.drop(columns=["pool", "cat_name", "name", "rank", "score", "asp"]), on="cand", how="left")
S["mo_pct"] = [pct.get((p, c)) for p, c in zip(S["pid"], S["cat"])]
G = scoring.score(S, r5=False)
G = G.merge(cand[["cand", "pid", "cat", "rank", "enter_M1", "seller", "launch_date"]], on="cand", how="left")
G.to_csv(W / "phase_h_shortlist.csv", index=False)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


ok = G[G["commercial_readiness"] != "Rejected"]
n = len(G)
R = {"plan": "registry/PHASE_H_PLAN.md", "n_candidates": n,
     "phase_f_class": {k: int(v) for k, v in prod["class"].value_counts().items()},
     "match_scores": prod["match_score"].value_counts(dropna=False).rename(index=str).to_dict(),
     "gate_counts": {g: int(G["gates_failed"].str.contains(g).sum()) for g in ("R1", "R2", "R3", "R4", "R6", "R7")},
     "passed_gates": {"n": len(ok), "share": round(len(ok) / n, 3), "wilson95": wilson(len(ok), n), "cands": ok["cand"].tolist()},
     "ad_suitability_of_passed": ok["ad_suitability"].value_counts().to_dict(),
     "forward_test": {"rule": "share of shortlist in Oct-2026 top 500 vs share of all candidates (descriptive)",
                      "shortlist": [f"{p}|{c}" for p, c in zip(ok["pid"], ok["cat"])],
                      "all_candidates": [f"{p}|{c}" for p, c in zip(G["pid"], G["cat"])]}}
(W / "phase_h_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: v for k, v in R.items() if k != "forward_test"}, indent=1))
cols = ["cand", "cat_name", "rank", "enter_M1", "asp", "units_sep", "be_roas", "be_roas_stress", "video_sh", "ad_suitability",
        "gates_failed", "risk_flags", "name"]
print(G[cols].assign(name=G["name"].str[:45]).to_string(index=False))
