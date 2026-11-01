"""Phase B additions: rank-band transitions and post-entry retention (descriptive). Read-only.

Writes _work/phase_b_extra.json. Uses the cached panel (scripts/panel.py) and phase_b_groups.pkl.
Run after phase_b.py: python -I research/winning_products/scripts/phase_b_extra.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import panel  # noqa: E402

top, lists = panel.build()
G = pd.read_pickle(panel.CACHE / "phase_b_groups.pkl")
out = {}
BANDS = [(1, 100, "1-100"), (101, 250, "101-250"), (251, 500, "251-500")]


def band(r):
    return next(lbl for lo, hi, lbl in BANDS if lo <= r <= hi)


# 1. month-to-month transitions between rank bands (and "out" = rank > 500), 2025-11 -> 2026-09
t = top[top["mi"] >= 1][["pid", "cat", "mi", "rank"]].copy()
t["band"] = t["rank"].map(band)
nxt = t.assign(mi=t["mi"] - 1).rename(columns={"band": "band_next"})[["pid", "cat", "mi", "band_next"]]
m = t[t["mi"] < panel.MIDX["2026-09"]].merge(nxt, on=["pid", "cat", "mi"], how="left").fillna({"band_next": "out (>500)"})
mat = pd.crosstab(m["band"], m["band_next"], normalize="index").round(3)
out["transition_matrix"] = mat.reset_index().to_dict("records")
out["transition_n"] = m["band"].value_counts().to_dict()
# by month, to show stability
out["stay_top100_by_month"] = (m[m["band"] == "1-100"].groupby("mi")["band_next"]
                               .apply(lambda s: round(float((s == "1-100").mean()), 3))
                               .rename(index=lambda i: panel.MONTHS[i]).to_dict())

# 2. retention after entry: share still in the top 500 k months after entering, by entry band
E = G[G["entry"].notna()][["pid", "cat", "entry"]].astype({"entry": int})
rank_at = dict(zip(zip(top["pid"], top["cat"], top["mi"]), top["rank"]))
pres = set(rank_at)
rows = []
for pid, cat, e in E.itertuples(index=False):
    rk = rank_at.get((pid, cat, e))
    if rk is None:
        continue
    for k in range(1, 7):
        if e + k <= panel.MIDX["2026-09"]:
            rows.append({"entry_band": band(int(rk)), "k": k, "present": (pid, cat, e + k) in pres})
ret = pd.DataFrame(rows)
out["retention_after_entry"] = (ret.groupby(["entry_band", "k"])["present"].agg(["mean", "size"]).round(3)
                                .reset_index().to_dict("records"))
# re-entry: products that leave and come back (seasonal or relaunch)
out["re_entry_share_of_products_with_gaps"] = round(float((G["n_obs"] > G["longest"]).mean()), 3)
(Path(panel.CACHE).parent / "phase_b_extra.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(pd.DataFrame(out["transition_matrix"]).to_string(index=False))
print(out["transition_n"], out["stay_top100_by_month"])
print(pd.DataFrame(out["retention_after_entry"]).pivot(index="entry_band", columns="k", values="mean"))
print("re-entry share:", out["re_entry_share_of_products_with_gaps"])
