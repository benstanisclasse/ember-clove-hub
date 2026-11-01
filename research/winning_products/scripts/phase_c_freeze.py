"""Freeze the forward-test predictions on the 2026-09 universe (registry/PHASE_C_PLAN.md §6, DEFINITIONS_v1 §7).

Refuses to run if kalodata.db holds any month after 2026-09 (the sealed October pull must not be loaded first).
Trains M1/M2 on all labelled cutoffs (ranks 101-500), scores every 2026-09 top-500 product (all 28 categories) for
T1, T2 and T4 with the models and baselines, writes registry/forward_test_2026-09.csv and appends EXP-C-002 with its
SHA-256 and the declared primary model. Run once: python -I research/winning_products/scripts/phase_c_freeze.py
"""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features as F  # noqa: E402
import panel  # noqa: E402
import phase_c as C  # noqa: E402

ROOT = panel.HUB / "research" / "winning_products"
OUT = ROOT / "registry" / "forward_test_2026-09.csv"
if OUT.exists():
    raise SystemExit(f"{OUT} already exists: the freeze is done once and never overwritten.")
latest = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True).execute(
    "select max(month) from pulls where month is not null and month < '2099'").fetchone()[0]
if latest > "2026-09":
    raise SystemExit(f"kalodata.db already holds {latest}: forward test would be contaminated.")

D = C.D
SEP = panel.MIDX["2026-09"]
score_set = D[D["mi"] == SEP].copy()
out = score_set[["pid", "cat", "month", "rank", "revenue"]].copy()
out["primary_universe"] = score_set["rank"].between(101, 500).astype(int)
for y, last_cut in (("T1", SEP - 1), ("T2", SEP - 1), ("T4", SEP - 3)):
    tr = D[C.mid(D) & D[y].notna() & (D["mi"] <= last_cut)]
    out[f"{y}_M1"] = C.fit_logit(tr, score_set, F.NUM, y)
    out[f"{y}_M2"] = C.fit_hgb(tr, score_set, F.NUM, y)
for name, f in C.BASELINES.items():
    if name != "B0 random":
        out["base_" + name.split()[0]] = f(score_set)
out.to_csv(OUT, index=False)
sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
rec = {"id": "EXP-C-002", "phase": "C", "at": "2026-11-01", "kind": "FORWARD TEST FREEZE (2026-09 universe)",
       "file": "registry/forward_test_2026-09.csv", "sha256": sha, "rows": len(out),
       "primary_universe_rows": int(out["primary_universe"].sum()), "db_latest_month_at_freeze": latest,
       "trained_on": {"T1/T2": "cutoffs 2025-12..2026-08", "T4": "cutoffs 2025-12..2026-06"},
       "declared_primary": {"target": "T1 (in top 500 in 2026-10)", "model": "T1_M1 (L2 logit)",
                            "reason": "simplest model that beat the best baseline in walk-forward (M2 not clearly better)",
                            "comparator": "base_B1 (revenue vs cutoff), the best walk-forward baseline for T1",
                            "metric": "global P@50 on primary_universe; also catP@10, AUC",
                            "success": "M1 P@50 > B1 P@50 on 2026-10 outcomes (single forward month; report the difference and a "
                                       "bootstrap-over-products 95% CI)"},
       "secondary": {"T2": "T2_M1 vs base_B2 (rank)", "T4": "T4_M1 vs base_B2, outcome needs 2026-10..12"},
       "rules": "No refit, no feature change. Outcomes come only from the sealed pulls (research/kalodata/sealed/2026-10..12).",
       "scripts": {s: hashlib.sha256((ROOT / "scripts" / s).read_bytes()).hexdigest()[:16] for s in
                   ("features.py", "phase_c.py", "panel.py", "phase_c_freeze.py")}}
with open(ROOT / "registry" / "experiments.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps({k: rec[k] for k in ("file", "sha256", "rows", "primary_universe_rows", "db_latest_month_at_freeze")}, indent=1))
print(out.sort_values("T1_M1", ascending=False).head(5)[["pid", "cat", "rank", "T1_M1", "T1_M2"]])
