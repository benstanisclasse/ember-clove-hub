"""Phase C features and labels (registry/PHASE_C_PLAN.md §1-2). Every feature at cutoff m uses months <= m only.

build_features() -> one row per product x category x cutoff month (2025-12..2026-09) from the top-500 panel, with labels
T1 (in top 500 at m+1), T2 (rank <= 100 at m+1), T4 (in top 500 at m+1..m+3); labels are NaN where not yet observable.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import panel  # noqa: E402

NUM = ["rank_pct", "log_rev_cut", "log_rev", "new_entrant", "mom_g", "accel", "accel_missing", "months_top_last3",
       "kalo_g", "log_asp", "asp_rel", "asp_chg", "asp_chg_missing", "age", "video_sh", "live_sh", "log_shop_n",
       "prev_riser", "cat_growth"]
GROUPS = {"H-B1 growth": ["mom_g"], "H-B2 Kalodata momentum": ["kalo_g"], "H-B3 acceleration": ["accel", "accel_missing"],
          "H-B5 age": ["age"], "H-B7 price": ["log_asp", "asp_rel", "asp_chg", "asp_chg_missing"],
          "H-B8 channels": ["video_sh", "live_sh"], "H-D1 category growth": ["cat_growth"], "H-D4 shop strength": ["log_shop_n"]}
FIRST_CUTOFF = panel.MIDX["2025-12"]


def _ym(s):
    s = str(s)
    return int(s[:4]) * 12 + int(s[5:7])


def build_features():
    top, lists = panel.build()
    t = top.copy()
    t["asp_med"] = t.groupby(["cat", "mi"])["asp"].transform("median")
    t["shop_n"] = t.groupby(["cat", "mi", "seller_id"])["pid"].transform("size")
    key = ["pid", "cat"]
    base = t[key + ["mi", "revenue", "asp", "rank"]]
    prev = base.assign(mi=base["mi"] + 1).rename(columns={"revenue": "rev_p1", "asp": "asp_p1", "rank": "rank_p1"})
    prev2 = base.assign(mi=base["mi"] + 2)[key + ["mi", "revenue"]].rename(columns={"revenue": "rev_p2"})
    pres = t[key + ["mi"]].assign(one=1)
    d = t[t["mi"] >= FIRST_CUTOFF].merge(prev, on=key + ["mi"], how="left").merge(prev2, on=key + ["mi"], how="left")
    for k in (1, 2, 3):  # membership m-k (Oct-2025 membership counts; it is never a growth base)
        d = d.merge(pres.assign(mi=pres["mi"] + k).rename(columns={"one": f"in_p{k}"}), on=key + ["mi"], how="left")
    d[["in_p1", "in_p2", "in_p3"]] = d[["in_p1", "in_p2", "in_p3"]].fillna(0)
    d["rank_pct"] = d["rank"] / 500
    d["log_rev_cut"] = np.log(d["revenue"] / d["cutoff"])
    d["log_rev"] = np.log(d["revenue"])
    d["new_entrant"] = (d["in_p1"] == 0).astype(float)
    valid_p1 = d["rev_p1"].notna() & (d["mi"] - 1 >= 1)  # m-1 must be a full month (not Oct-2025)
    d["mom_g"] = np.where(valid_p1, np.clip(np.log(d["revenue"] / d["rev_p1"]), -3, 3), 0.0)
    valid_p2 = valid_p1 & d["rev_p2"].notna() & (d["mi"] - 2 >= 1)
    g_prev = np.clip(np.log(d["rev_p1"] / d["rev_p2"]), -3, 3)
    d["accel"] = np.where(valid_p2, d["mom_g"] - g_prev, 0.0)
    d["accel_missing"] = (~valid_p2).astype(float)
    d["months_top_last3"] = d["in_p1"] + d["in_p2"] + d["in_p3"]
    d["kalo_g"] = np.sign(d["kalo_g"]) * np.log1p(d["kalo_g"].abs())
    d["log_asp"] = np.log(d["asp"].clip(lower=0.01))
    d["asp_rel"] = np.log(d["asp"].clip(lower=0.01) / d["asp_med"].clip(lower=0.01))
    d["asp_chg"] = np.where(valid_p1, np.log(d["asp"].clip(lower=0.01) / d["asp_p1"].clip(lower=0.01)), 0.0)
    d["asp_chg_missing"] = (~valid_p1).astype(float)
    month_ym = d["month"].map(_ym)
    d["age"] = (month_ym - d["launch_date"].map(_ym)).clip(0, 36)
    d["video_sh"] = d["video_revenue"] / d["revenue"]
    d["live_sh"] = d["live_revenue"] / d["revenue"]
    d["log_shop_n"] = np.log(d["shop_n"])
    ris = lists[lists["kind"] == "risers"].assign(mi=lambda x: x["month"].map(panel.MIDX) + 1)[key + ["mi"]].drop_duplicates()
    d = d.merge(ris.assign(prev_riser=1.0), on=key + ["mi"], how="left").fillna({"prev_riser": 0.0})
    cat_rev = t.groupby(["cat", "mi"])["revenue"].sum()
    d["cat_growth"] = [np.log(cat_rev[(c, m)] / cat_rev[(c, m - 1)]) if m - 1 >= 1 else 0.0 for c, m in zip(d["cat"], d["mi"])]
    # labels
    nxt = base.assign(mi=base["mi"] - 1)[key + ["mi", "rank"]].rename(columns={"rank": "rank_n1"})
    d = d.merge(nxt, on=key + ["mi"], how="left")
    for k in (1, 2, 3):
        d = d.merge(pres.assign(mi=pres["mi"] - k).rename(columns={"one": f"in_n{k}"}), on=key + ["mi"], how="left")
    last = panel.MIDX["2026-09"]
    d["T1"] = np.where(d["mi"] + 1 <= last, d["in_n1"].notna().astype(float), np.nan)
    d["T2"] = np.where(d["mi"] + 1 <= last, (d["rank_n1"] <= 100).astype(float), np.nan)
    d["T4"] = np.where(d["mi"] + 3 <= last, (d["in_n1"].notna() & d["in_n2"].notna() & d["in_n3"].notna()).astype(float), np.nan)
    return d.drop(columns=[c for c in d.columns if c.startswith(("in_n", "rev_p", "asp_p"))])


if __name__ == "__main__":
    f = build_features()
    print(f.shape, f.groupby("month")[["T1", "T2", "T4"]].mean().round(3))
    print(f[NUM].describe().T[["mean", "min", "max"]].round(3))
