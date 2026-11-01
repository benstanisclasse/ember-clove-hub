"""Phase H, H1 (H-H2): do break-in picks from ranks 501-1,000 last? Same band frame and model as phase_c_band.py.
registry/PHASE_H_PLAN.md, frozen before this ran. Read-only. Writes _work/phase_h_backtest.json.
Run: python -I research/winning_products/scripts/phase_h_backtest.py
"""
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import panel  # noqa: E402
import phase_c as C  # noqa: E402
import phase_c_band as PB  # noqa: E402

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
W = panel.HUB / "research" / "winning_products" / "_work"
RNG = np.random.default_rng(20261101)
TEST = [panel.MIDX[m] for m in ("2026-02", "2026-03", "2026-04", "2026-05", "2026-06")]
LAST = panel.MIDX["2026-09"]

cats = sorted(set(C.CATS) - {"834312"})
B, _, _ = PB.band_frame(cats)
top, _ = panel.build()
tk = set(zip(top["pid"], top["cat"], top["mi"]))
B["hold3"] = [float(all((p, c, m + k) in tk for k in (1, 2, 3))) if m + 3 <= LAST else np.nan
              for p, c, m in zip(B["pid"], B["cat"], B["mi"])]
BL = B[B["enter"].notna()]


def picks(te, score, k=20):
    s = pd.Series(score, index=te.index)
    return [s[g.index].sort_values(ascending=False).index[:k] for _, g in te.groupby("cat")]


def catp(te, idx, y):
    return float(np.mean([te.loc[i, y].mean() for i in idx]))


per, young = [], []
for t in TEST:
    tr, te = BL[BL["mi"] <= t - 1], BL[BL["mi"] == t].copy()
    p = C.fit_logit(tr, te, PB.BF, "enter")
    im, ib = picks(te, p), picks(te, te["log_rev_cut"].values)
    allm = pd.Index(np.concatenate([np.asarray(i) for i in im]))
    sel = te.loc[allm]
    per.append({"month": panel.MONTHS[t], "n_band": len(te), "n_cats": int(te["cat"].nunique()),
                "base_enter": float(te["enter"].mean()), "base_hold3": float(te["hold3"].mean()),
                "M1_enter": catp(te, im, "enter"), "B1_enter": catp(te, ib, "enter"),
                "M1_hold3": catp(te, im, "hold3"), "B1_hold3": catp(te, ib, "hold3"),
                "M1_hold3_given_enter": float(sel.loc[sel["enter"] == 1, "hold3"].mean()) if (sel["enter"] == 1).any() else None,
                "picks_share_age_le3": float((sel["age"] <= 3).mean())})
    for grp, g in (("age<=3", sel[sel["age"] <= 3]), ("age>3", sel[sel["age"] > 3])):
        young.append({"month": panel.MONTHS[t], "group": grp, "n": len(g), "enter": float(g["enter"].mean()) if len(g) else None,
                      "hold3": float(g["hold3"].mean()) if len(g) else None})
pf = pd.DataFrame(per)
d = (pf["M1_hold3"] - pf["B1_hold3"]).to_numpy()
bs = np.array([RNG.choice(d, len(d)).mean() for _ in range(2000)])
ci = [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]
ahead = int((d > 0).sum())
ratio = float(pf["M1_hold3"].mean() / pf["base_hold3"].mean())
Y = pd.DataFrame(young)
R = {"plan": "registry/PHASE_H_PLAN.md", "categories": len(cats), "band_rows": len(B), "per_month": per,
     "mean": pf.drop(columns="month").mean().round(4).to_dict(),
     "H-H2": {"M1_minus_B1_hold3": round(float(d.mean()), 4), "ci95": ci, "months_ahead": f"{ahead}/{len(d)}",
              "M1_over_base_hold3": round(ratio, 2), "supported": bool(ratio >= 2 and ci[0] > 0 and ahead >= 4)},
     "sub_lane_age": Y.groupby("group").apply(lambda g: pd.Series({"n": int(g["n"].sum()),
                                                                   "enter": round(float(np.average(g["enter"].fillna(0), weights=g["n"])), 4),
                                                                   "hold3": round(float(np.average(g["hold3"].fillna(0), weights=g["n"])), 4)})).to_dict("index")}
(W / "phase_h_backtest.json").write_text(json.dumps(R, indent=1), encoding="utf-8")
print(pf.round(3).to_string(index=False))
print(json.dumps({k: R[k] for k in ("mean", "H-H2", "sub_lane_age")}, indent=1))
