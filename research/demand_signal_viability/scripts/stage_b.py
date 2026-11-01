"""Stage B: demand-signal validation (registry/STAGE_B_PLAN.md, frozen before this ran). Read-only on kalodata.db.
Universe: products outside their category top 500 but visible in ranks 501-1,000 or on Kalodata's riser list (1-200).
Writes _work/stage_b_results.json, _work/stage_b_signal_inventory.csv, _work/stage_b_lead_time.csv.
Run: python -I research/demand_signal_viability/scripts/stage_b.py
"""
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

HUB = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HUB / "research" / "winning_products" / "scripts"))
import panel  # noqa: E402
import phase_c as C  # noqa: E402

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
W = HUB / "research" / "demand_signal_viability" / "_work"
SEED, BOOT = 20261101, 2000
RNG = np.random.default_rng(SEED)
M = panel.MIDX
LAST = M["2026-09"]
S1_TEST = [M[f"2026-{i:02d}"] for i in range(1, 9)]
# Deviation (DSI-B-001): plan said 2026-01..06, but S2 training needs months <= t-3 and the universe starts 2025-11;
# like Phase C T4, testing starts once 2 training months exist.
S2_TEST = [M[f"2026-{i:02d}"] for i in range(3, 7)]
SEL = S1_TEST[:4]
R = {"plan": "registry/STAGE_B_PLAN.md"}

# ------------------------------------------------------------------ build the universe
top, _ = panel.build()
cats = set(top["cat"])
raw = panel._load()
raw = raw[raw["cat"].isin(cats)]
raw["mi"] = raw["month"].map(M)
deep = raw[(raw["kind"] == "top_deep") & raw["page"].between(6, 10)].sort_values("rank").drop_duplicates(["pid", "cat", "mi"])
ris = raw[(raw["kind"] == "risers") & raw["page"].between(1, 2)].sort_values("rank").drop_duplicates(["pid", "cat", "mi"])
topk = set(zip(top["pid"], top["cat"], top["mi"]))
rev_any = {}
for df in (ris, deep, top):  # later sources overwrite earlier (top wins); values agree where both exist (Stage A)
    rev_any.update({(p, c, m): (r, a) for p, c, m, r, a in zip(df["pid"], df["cat"], df["mi"], df["revenue"].astype(float),
                                                                    df["asp"].astype(float))})
ris_key = set(zip(ris["pid"], ris["cat"], ris["mi"]))
cut = top.groupby(["cat", "mi"])["revenue"].min().to_dict()
asp_med = top.groupby(["cat", "mi"])["asp"].median().to_dict()
cat_rev = top.groupby(["cat", "mi"])["revenue"].sum().to_dict()

cols = ["pid", "cat", "mi", "month", "rank", "revenue", "units", "asp", "video_revenue", "live_revenue", "launch_date", "kalo_g"]
U = pd.concat([deep[cols].assign(src="band"), ris[cols].assign(src="riser")])
U = U[~pd.Series([k in topk for k in zip(U["pid"], U["cat"], U["mi"])], index=U.index)]
band_rank = {(p, c, m): r for p, c, m, r in zip(deep["pid"], deep["cat"], deep["mi"], deep["rank"])}
ris_rank = {(p, c, m): r for p, c, m, r in zip(ris["pid"], ris["cat"], ris["mi"], ris["rank"])}
U = U.sort_values("src").drop_duplicates(["pid", "cat", "mi"])  # 'band' sorts first: keep the band row's values
U = U[(U["mi"] >= M["2025-11"])].reset_index(drop=True)
for c in ("revenue", "units", "asp", "video_revenue", "live_revenue", "kalo_g"):
    U[c] = pd.to_numeric(U[c], errors="coerce")
key = list(zip(U["pid"], U["cat"], U["mi"]))
U["band_rank_pct"] = [(band_rank[k] - 500) / 500 if k in band_rank else np.nan for k in key]
U["in_band"] = U["band_rank_pct"].notna().astype(float)
U["riser_pos"] = [ris_rank.get(k, np.nan) for k in key]
U["is_riser"] = U["riser_pos"].notna().astype(float)
U["log_rev_cut"] = np.log(U["revenue"].clip(lower=1) / [cut[(c, m)] for c, m in zip(U["cat"], U["mi"])])
U["log_units"] = np.log1p(U["units"].clip(lower=0))
p1 = [rev_any.get((p, c, m - 1)) if m - 1 >= 1 else None for p, c, m in key]
p2 = [rev_any.get((p, c, m - 2)) if m - 2 >= 1 else None for p, c, m in key]
U["seen_p1"] = [float(v is not None) for v in p1]
U["mom_g"] = [float(np.clip(math.log(max(r, 1) / max(v[0], 1)), -3, 3)) if v else 0.0 for r, v in zip(U["revenue"], p1)]
g_prev = [float(np.clip(math.log(max(a[0], 1) / max(b[0], 1)), -3, 3)) if a and b else None for a, b in zip(p1, p2)]
U["accel_missing"] = [float(g is None) for g in g_prev]
U["accel"] = [mg - g if g is not None else 0.0 for mg, g in zip(U["mom_g"], g_prev)]
U["up2"] = [float(mg > 0 and g is not None and g > 0) for mg, g in zip(U["mom_g"], g_prev)]
U["kalo_g"] = np.sign(U["kalo_g"].fillna(0)) * np.log1p(U["kalo_g"].fillna(0).abs())
U["video_sh"] = (U["video_revenue"] / U["revenue"].replace(0, np.nan)).clip(0, 1).fillna(0)
U["live_sh"] = (U["live_revenue"] / U["revenue"].replace(0, np.nan)).clip(0, 1).fillna(0)
U["log_asp"] = np.log(U["asp"].clip(lower=0.01))
U["asp_rel"] = np.log(U["asp"].clip(lower=0.01) / np.array([asp_med[(c, m)] for c, m in zip(U["cat"], U["mi"])]).clip(0.01))
U["asp_chg_missing"] = [float(v is None) for v in p1]
U["asp_chg"] = [math.log(max(a, 0.01) / max(v[1], 0.01)) if v and v[1] == v[1] else 0.0 for a, v in zip(U["asp"], p1)]
U["age"] = (U["month"].map(lambda s: int(s[:4]) * 12 + int(s[5:7]))
            - U["launch_date"].map(lambda s: int(str(s)[:4]) * 12 + int(str(s)[5:7]) if isinstance(s, str) and len(s) >= 7 else np.nan)).clip(0, 36)
U["age_missing"] = U["age"].isna().astype(float)
U["age"] = U["age"].fillna(12)
U["was_top_p1"] = [float((p, c, m - 1) in topk) for p, c, m in key]
U["prev_riser"] = [float((p, c, m - 1) in ris_key) for p, c, m in key]
U["cat_growth"] = [math.log(cat_rev[(c, m)] / cat_rev[(c, m - 1)]) if m - 1 >= 1 else 0.0 for c, m in zip(U["cat"], U["mi"])]
U["S1"] = [float((p, c, m + 1) in topk) if m + 1 <= LAST else np.nan for p, c, m in key]
U["S2"] = [float(all((p, c, m + k) in topk for k in (1, 2, 3))) if m + 3 <= LAST else np.nan for p, c, m in key]
# fills for linear models
U["band_rank_fill"] = U["band_rank_pct"].fillna(1.0)          # outside the band = beyond rank 1,000
U["riser_fill"] = U["riser_pos"].fillna(201) / 200
R["universe"] = {"rows": len(U), "per_month": U.groupby("month").size().to_dict(),
                 "band_only": int(((U["in_band"] == 1) & (U["is_riser"] == 0)).sum()),
                 "riser_only": int(((U["in_band"] == 0) & (U["is_riser"] == 1)).sum()), "both": int(((U["in_band"] == 1) & (U["is_riser"] == 1)).sum())}

# coverage: next-month top-500 entrants that were in the universe at m
ukey = set(key)
cov = []
for m in range(M["2025-11"], LAST):
    ent = top[(top["mi"] == m + 1)]
    ent = ent[[(p, c, m) not in topk for p, c in zip(ent["pid"], ent["cat"])]]
    inu = np.mean([(p, c, m) in ukey for p, c in zip(ent["pid"], ent["cat"])])
    cov.append({"entry_month": panel.MONTHS[m + 1], "entrants": len(ent), "in_universe_at_m": round(float(inu), 3)})
R["coverage"] = {"by_month": cov, "mean_in_universe": round(float(np.mean([c["in_universe_at_m"] for c in cov])), 3)}

FAM = {"transaction": ["log_rev_cut", "log_units", "band_rank_fill", "in_band"],
       "momentum": ["mom_g", "seen_p1", "accel", "accel_missing", "up2", "kalo_g"],
       "riser": ["riser_fill", "is_riser", "prev_riser"],
       "channel": ["video_sh", "live_sh"],
       "price": ["log_asp", "asp_rel", "asp_chg", "asp_chg_missing"],
       "lifecycle": ["age", "age_missing", "was_top_p1"],
       "category": ["cat_growth"]}
ALL = [f for fs in FAM.values() for f in fs]
BF = ["band_rank_fill", "log_rev_cut", "seen_p1", "was_top_p1", "mom_g", "kalo_g", "log_asp", "asp_rel", "age", "video_sh",
      "live_sh", "prev_riser"]  # phase_c_band.BF with band_rank_pct filled for riser-only rows
HGB_RAW = ["log_rev_cut", "log_units", "band_rank_pct", "riser_pos", "mom_g", "seen_p1", "accel", "up2", "kalo_g", "prev_riser",
           "video_sh", "live_sh", "log_asp", "asp_rel", "asp_chg", "age", "was_top_p1", "cat_growth"]


def z_within(df, col):
    g = df.groupby(["cat", "mi"])[col]
    return (df[col] - g.transform("mean")) / g.transform("std").replace(0, 1)


def rule_scores(te):
    growth = np.where(te["seen_p1"] == 1, te["mom_g"], -9 + 0.001 * te["log_rev_cut"])
    riser = np.where(te["is_riser"] == 1, -te["riser_pos"].fillna(999), -999 + 0.001 * te["log_rev_cut"])
    return {"A Revenue": te["log_rev_cut"].values, "B Growth": growth, "C Kalodata risers": riser,
            "D Momentum": (z_within(te, "log_rev_cut") + z_within(te, "mom_g")).values}


def catp(te, score, y, k):
    s = pd.Series(score, index=te.index)
    vals = [te.loc[s[g.index].sort_values(ascending=False).index[:k], y].mean() for _, g in te.groupby("cat")]
    return float(np.mean(vals))


def flagged(te, score, k):
    s = pd.Series(score, index=te.index)
    return pd.Index(np.concatenate([s[g.index].sort_values(ascending=False).index[:k].to_numpy() for _, g in te.groupby("cat")]))


def metrics(te, score, y):
    out = {"catP@10": catp(te, score, y, 10), "catP@20": catp(te, score, y, 20)}
    s = pd.Series(score, index=te.index)
    out["P@100"] = float(te.loc[s.sort_values(ascending=False).index[:100], y].mean())
    f20 = flagged(te, score, 20)
    tp = te.loc[f20, y].sum()
    out["recall@20"] = float(tp / te[y].sum()) if te[y].sum() else np.nan
    out["FP_per_TP@20"] = float((len(f20) - tp) / tp) if tp else np.nan
    out["AUC"] = float(roc_auc_score(te[y], s)) if te[y].nunique() > 1 else np.nan
    out["PR_AUC"] = float(average_precision_score(te[y], s)) if te[y].nunique() > 1 else np.nan
    out["base"] = float(te[y].mean())
    return out


def model_scores(tr, te, y):
    return {"E Existing model": C.fit_logit(tr, te, BF, y), "F logit": C.fit_logit(tr, te, ALL, y),
            "F hgb": C.fit_hgb(tr, te, HGB_RAW, y)}


def boot(d):
    d = np.asarray(d, float)
    b = np.array([RNG.choice(d, len(d)).mean() for _ in range(BOOT)])
    return [round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)], min(1.0, 2 * float(min((b <= 0).mean(), (b >= 0).mean())))


# ------------------------------------------------------------------ B4/B5 discovery comparison
per = {"S1": {}, "S2": {}}
scores_by_month = {}  # S1 walk-forward scores for lead time / stability, keyed by month index
for y, months, h in (("S1", S1_TEST, 1), ("S2", S2_TEST, 3)):
    L = U[U[y].notna()]
    for t in months:
        tr, te = L[L["mi"] <= t - h], L[L["mi"] == t].copy()
        sc = {**rule_scores(te), **model_scores(tr, te, y)}
        per[y][panel.MONTHS[t]] = {n: metrics(te, s, y) for n, s in sc.items()}
        if y == "S1":
            scores_by_month[t] = pd.DataFrame({n: s for n, s in sc.items()}, index=te.index)
sel = {n: np.mean([per["S1"][panel.MONTHS[t]][n]["catP@20"] for t in SEL]) for n in ("F logit", "F hgb")}
FNAME = max(sel, key=sel.get)
R["F_selection"] = {"rule": "higher mean S1 catP@20 in 2026-01..04", "means": {k: round(v, 4) for k, v in sel.items()}, "chosen": FNAME}
METHODS = ["A Revenue", "B Growth", "C Kalodata risers", "D Momentum", "E Existing model", FNAME]


def summarise(y, months_lbl):
    P = per[y]
    ms = [m for m in P if m in months_lbl]
    mean = {n: {k: round(float(np.nanmean([P[m][n][k] for m in ms])), 4) for k in P[ms[0]][n]} for n in P[ms[0]]}
    simple = ["A Revenue", "B Growth", "C Kalodata risers", "D Momentum"]
    best = max(simple, key=lambda n: mean[n]["catP@20"])
    comp, pv = {}, {}
    for n in ["A Revenue", "B Growth", "C Kalodata risers", "D Momentum", "E Existing model"]:
        d = [P[m][FNAME]["catP@20"] - P[m][n]["catP@20"] for m in ms]
        ci, p = boot(d)
        comp[n] = {"mean_diff": round(float(np.mean(d)), 4), "ci95": ci, "p": round(p, 4), "months_ahead": f"{sum(x > 0 for x in d)}/{len(d)}"}
        pv[n] = p
    order, run = sorted(pv, key=pv.get), 0.0
    for i, n in enumerate(order):
        run = max(run, min(1.0, pv[n] * (len(order) - i)))
        c = comp[n]
        c["p_holm"] = round(run, 4)
        c["beats"] = bool((c["ci95"][0] > 0) and int(c["months_ahead"].split("/")[0]) >= math.ceil(2 * len(ms) / 3) and run < 0.05)
    lift = comp[best]["mean_diff"]
    thr = 0.05 if y == "S1" else 0.02
    return {"months": ms, "mean": mean, "best_simple_rule": best, "F_vs": comp, "lift_vs_best_simple": lift,
            "material": bool(comp[best]["beats"] and lift >= thr), "materiality_threshold": thr}


lbl1 = [panel.MONTHS[t] for t in S1_TEST]
R["S1_all"] = summarise("S1", lbl1)
R["S1_late"] = summarise("S1", lbl1[4:])
R["S2_all"] = summarise("S2", [panel.MONTHS[t] for t in S2_TEST])
R["per_month"] = per

# ablations (F logit, S1)
abl = {}
L = U[U["S1"].notna()]
base_auc, base_p = {}, {}
for t in S1_TEST:
    tr, te = L[L["mi"] <= t - 1], L[L["mi"] == t]
    full = C.fit_logit(tr, te, ALL, "S1")
    base_auc[t], base_p[t] = roc_auc_score(te["S1"], full), catp(te, full, "S1", 20)
    for fam, fs in FAM.items():
        red = C.fit_logit(tr, te, [f for f in ALL if f not in fs], "S1")
        abl.setdefault(fam, {"dAUC": [], "dP20": []})
        abl[fam]["dAUC"].append(base_auc[t] - roc_auc_score(te["S1"], red))
        abl[fam]["dP20"].append(base_p[t] - catp(te, red, "S1", 20))
R["ablations_S1_logit"] = {f: {"dAUC_mean": round(float(np.mean(v["dAUC"])), 4), "dAUC_ci95": boot(v["dAUC"])[0],
                               "dcatP@20_mean": round(float(np.mean(v["dP20"])), 4), "dcatP@20_ci95": boot(v["dP20"])[0],
                               "contributing": bool(boot(v["dAUC"])[0][0] > 0)} for f, v in abl.items()}

# calibration and stability of F (S1)
cal = []
for t in S1_TEST:
    te = L[L["mi"] == t]
    cal.append(pd.DataFrame({"p": scores_by_month[t][FNAME].clip(1e-4, 1 - 1e-4), "y": te["S1"]}))
cal = pd.concat(cal)
import statsmodels.api as sm  # noqa: E402
lg = sm.Logit(cal["y"], sm.add_constant(np.log(cal["p"] / (1 - cal["p"])))).fit(disp=0)
R["F_calibration_S1"] = {"brier": round(float(brier_score_loss(cal["y"], cal["p"])), 4),
                         "brier_base": round(float(brier_score_loss(cal["y"], np.full(len(cal), cal["y"].mean()))), 4),
                         "slope": round(float(lg.params.iloc[1]), 3), "intercept": round(float(lg.params.iloc[0]), 3)}
stab = []
for t in S1_TEST[:-1]:
    a, b = L[L["mi"] == t], L[L["mi"] == t + 1]
    sa = pd.Series(scores_by_month[t][FNAME].values, index=list(zip(a["pid"], a["cat"])))
    sb = pd.Series(scores_by_month[t + 1][FNAME].values, index=list(zip(b["pid"], b["cat"])))
    both = sa.index.intersection(sb.index)
    fa = flagged(a, scores_by_month[t][FNAME].values, 20)
    fa_keys = set(zip(a.loc[fa, "pid"], a.loc[fa, "cat"]))
    fb = flagged(b, scores_by_month[t + 1][FNAME].values, 20)
    fb_keys = set(zip(b.loc[fb, "pid"], b.loc[fb, "cat"]))
    still = [k for k in fa_keys if k in set(both)]
    stab.append({"month": panel.MONTHS[t], "spearman_consecutive": round(float(spearmanr(sa[both], sb[both]).correlation), 3),
                 "top20_still_in_universe": len(still), "top20_reflagged_share": round(len([k for k in still if k in fb_keys]) / max(len(still), 1), 3)})
R["F_stability"] = stab

# category and temporal generalisation (S1, F vs best simple rule)
best1 = R["S1_all"]["best_simple_rule"]
bycat = {}
for t in S1_TEST:
    te = L[L["mi"] == t]
    sF, sB = pd.Series(scores_by_month[t][FNAME].values, index=te.index), pd.Series(scores_by_month[t][best1].values, index=te.index)
    for c, g in te.groupby("cat"):
        pf = g.loc[sF[g.index].sort_values(ascending=False).index[:20], "S1"].mean()
        pb = g.loc[sB[g.index].sort_values(ascending=False).index[:20], "S1"].mean()
        bycat.setdefault(c, []).append(pf - pb)
R["S1_by_category_F_minus_best_rule"] = {c: round(float(np.mean(v)), 4) for c, v in bycat.items()}
R["S1_categories_F_ahead"] = f"{sum(np.mean(v) > 0 for v in bycat.values())}/{len(bycat)}"
R["S1_by_month_F_minus_best_rule"] = {m: round(per["S1"][m][FNAME]["catP@20"] - per["S1"][m][best1]["catP@20"], 4) for m in lbl1}

# ------------------------------------------------------------------ B6 leading / coincident / lagging
REF = ["log_rev_cut", "band_rank_fill", "in_band"]
SIG = {"log_units": ["log_units"], "mom_g": ["mom_g", "seen_p1"], "accel": ["accel", "accel_missing"], "up2": ["up2"],
       "kalo_g": ["kalo_g"], "riser_list": ["riser_fill", "is_riser"], "prev_riser": ["prev_riser"], "video_sh": ["video_sh"],
       "live_sh": ["live_sh"], "log_asp": ["log_asp"], "asp_rel": ["asp_rel"], "asp_chg": ["asp_chg", "asp_chg_missing"],
       "age": ["age", "age_missing"], "was_top_p1": ["was_top_p1"], "cat_growth": ["cat_growth"]}
inv = []
nxt = {(p, c, m): (r, a) for (p, c, m), (r, a) in rev_any.items()}
vid_any = {}
for df in (ris, deep, top):
    vr = pd.to_numeric(df["video_revenue"], errors="coerce") / pd.to_numeric(df["revenue"], errors="coerce").replace(0, np.nan)
    lr = pd.to_numeric(df["live_revenue"], errors="coerce") / pd.to_numeric(df["revenue"], errors="coerce").replace(0, np.nan)
    kg = pd.to_numeric(df["kalo_g"], errors="coerce")
    vid_any.update({(p, c, m): (v, l, k) for p, c, m, v, l, k in zip(df["pid"], df["cat"], df["mi"], vr, lr, kg)})
for name, fs in SIG.items():
    row = {"signal": name, "features": "+".join(fs)}
    for y, months, h in (("S1", S1_TEST, 1), ("S2", S2_TEST, 3)):
        Ly = U[U[y].notna()]
        d = []
        for t in months:
            tr, te = Ly[Ly["mi"] <= t - h], Ly[Ly["mi"] == t]
            d.append(roc_auc_score(te[y], C.fit_logit(tr, te, REF + fs, y)) - roc_auc_score(te[y], C.fit_logit(tr, te, REF, y)))
        ci = boot(d)[0]
        row[f"{y}_dAUC"] = round(float(np.mean(d)), 4)
        row[f"{y}_dAUC_ci95"] = ci
        row[f"{y}_months_pos"] = f"{sum(x > 0 for x in d)}/{len(d)}"
        row[f"{y}_leading"] = bool(ci[0] > 0 and sum(x > 0 for x in d) >= math.ceil(2 * len(d) / 3))
    seen = U[U["seen_p1"] == 1]
    row["rho_with_same_month_growth"] = round(float(spearmanr(seen[fs[0]], seen["mom_g"]).correlation), 3) if fs[0] != "mom_g" else 1.0
    row["lag_rho"] = None
    if name in ("video_sh", "live_sh", "log_asp", "kalo_g", "riser_list"):
        a, b = [], []
        for (p, c, m), g in zip(key, U["mom_g"]):
            if (p, c, m + 1) not in nxt or m + 1 > LAST:
                continue
            if name == "riser_list":
                cur, fut = float((p, c, m) in ris_key), float((p, c, m + 1) in ris_key)
            elif name == "log_asp":
                cur, fut = math.log(max(rev_any[(p, c, m)][1], 0.01)), math.log(max(nxt[(p, c, m + 1)][1], 0.01))
            else:
                ix = {"video_sh": 0, "live_sh": 1, "kalo_g": 2}[name]
                cur, fut = vid_any.get((p, c, m), (np.nan,) * 3)[ix], vid_any.get((p, c, m + 1), (np.nan,) * 3)[ix]
            if cur == cur and fut == fut:
                a.append(g)
                b.append(fut - cur)
        row["lag_rho"] = round(float(spearmanr(a, b).correlation), 3) if len(a) > 50 else None
    lead = row["S1_leading"]
    if lead:
        cls = "leading"
    elif row["lag_rho"] is not None and row["lag_rho"] >= 0.2:
        cls = "lagging"
    elif abs(row["rho_with_same_month_growth"]) >= 0.3:
        cls = "coincident"
    else:
        cls = "no detectable lead (not coincident)"
    row["classification"] = cls
    inv.append(row)
INV = pd.DataFrame(inv)
untestable = ["video_count", "creator_count", "creator_concentration", "new_creator_share", "views_per_video", "ad_share_of_video_revenue",
              "review_rating", "complaint_themes", "attributes", "cj_availability", "cj_cost", "cj_stock", "contribution_margin"]
INV = pd.concat([INV, pd.DataFrame([{"signal": s, "classification": "unknown (no per-product monthly history)"} for s in untestable])])
INV.to_csv(W / "stage_b_signal_inventory.csv", index=False)
R["signal_classification"] = INV.set_index("signal")["classification"].to_dict()

# ------------------------------------------------------------------ B7 lead time
first_top = top.groupby(["pid", "cat"])["mi"].min()
succ = first_top[(first_top >= M["2026-02"])].rename("e").reset_index()
held = set(zip(top["pid"], top["cat"], top["mi"]))
succ["held3"] = [all((p, c, e + k) in held for k in (0, 1, 2)) if e + 2 <= LAST else np.nan for p, c, e in zip(succ["pid"], succ["cat"], succ["e"])]
vis_before = {}
for (p, c, m) in ukey:
    vis_before.setdefault((p, c), []).append(m)
flag_months = {}
for k in (10, 20):
    for t, S in scores_by_month.items():
        te = L[L["mi"] == t]
        for n in METHODS:
            f = flagged(te, S[n].values, k)
            for p, c in zip(te.loc[f, "pid"], te.loc[f, "cat"]):
                flag_months.setdefault((k, n, p, c), []).append(t)
lt_rows = []
for _, s in succ.iterrows():
    pc = (s["pid"], s["cat"])
    vis = [m for m in vis_before.get(pc, []) if M["2026-01"] <= m < s["e"]]
    for k in (10, 20):
        for n in METHODS:
            fl = [t for t in flag_months.get((k, n) + pc, []) if t < s["e"]]
            lt_rows.append({"pid": s["pid"], "cat": s["cat"], "e": panel.MONTHS[s["e"]], "held3": s["held3"], "visible_before": bool(vis),
                            "k": k, "method": n, "first_flag": panel.MONTHS[min(fl)] if fl else None, "lead": s["e"] - min(fl) if fl else 0})
LT = pd.DataFrame(lt_rows)
LT.to_csv(W / "stage_b_lead_time.csv", index=False)
lt = {}
for k in (10, 20):
    for n in METHODS:
        for subset, mask in (("all_successes", slice(None)), ("visible_before", "vis"), ("held3_all", "held")):
            g = LT[(LT["k"] == k) & (LT["method"] == n)]
            if mask == "vis":
                g = g[g["visible_before"]]
            elif mask == "held":
                g = g[g["held3"] == True]  # noqa: E712
            fl = g[g["lead"] > 0]
            lt.setdefault(f"top{k}", {}).setdefault(n, {})[subset] = {
                "n": len(g), "share_flagged_>=1m": round(float((g["lead"] >= 1).mean()), 4), "share_>=2m": round(float((g["lead"] >= 2).mean()), 4),
                "median_lead_flagged": float(fl["lead"].median()) if len(fl) else None, "mean_lead_flagged": round(float(fl["lead"].mean()), 2) if len(fl) else None}
# alert burden: flags issued per success caught (over the flag window 2026-01..08)
for k in (10, 20):
    for n in METHODS:
        caught = LT[(LT["k"] == k) & (LT["method"] == n) & (LT["lead"] > 0)]
        n_flags = sum(len(v) for (kk, nn, _, _), v in flag_months.items() if kk == k and nn == n)
        lt[f"top{k}"][n]["flags_issued"] = n_flags
        lt[f"top{k}"][n]["flags_per_success_caught"] = round(n_flags / max(len(caught), 1), 1)
# paired: F earlier than growth filter / Kalodata risers, among successes both flagged
for k in (10, 20):
    piv = LT[LT["k"] == k].pivot_table(index=["pid", "cat", "e"], columns="method", values="lead")
    for b in ("B Growth", "C Kalodata risers", "A Revenue"):
        both = piv[(piv[FNAME] > 0) & (piv[b] > 0)]
        only_f, only_b = int(((piv[FNAME] > 0) & (piv[b] == 0)).sum()), int(((piv[FNAME] == 0) & (piv[b] > 0)).sum())
        lt[f"top{k}"][f"F_vs_{b}"] = {"both_flagged": len(both), "F_earlier": int((both[FNAME] > both[b]).sum()),
                                     "same_month": int((both[FNAME] == both[b]).sum()), "F_later": int((both[FNAME] < both[b]).sum()),
                                     "only_F": only_f, "only_baseline": only_b,
                                     "mean_extra_lead_months_when_both": round(float((both[FNAME] - both[b]).mean()), 3) if len(both) else None}
R["lead_time"] = lt
R["lead_time_successes"] = {"n": len(succ), "held3_known": int(succ["held3"].notna().sum()), "held3": int((succ["held3"] == True).sum()),  # noqa: E712
                            "visible_before_share": round(float(LT[(LT["k"] == 20) & (LT["method"] == FNAME)]["visible_before"].mean()), 4),
                            "flag_window": "2026-01..2026-08 (walk-forward S1 test months)"}

# ------------------------------------------------------------------ B8 promotion vs demand
E = U[(U["S1"] == 1) & U["S2"].notna()].copy()


def rate(g):
    k, n = int(g["S2"].sum()), len(g)
    p = k / n if n else np.nan
    zz = 1.96
    d = 1 + zz * zz / n
    c = (p + zz * zz / (2 * n)) / d
    hw = zz * math.sqrt(p * (1 - p) / n + zz * zz / (4 * n * n)) / d
    return {"n": n, "S2_given_S1": round(p, 4), "wilson95": [round(c - hw, 4), round(c + hw, 4)]}


obs = E[E["asp_chg_missing"] == 0]
R["B8_price_cut"] = {"asp_cut_le_10pct": rate(obs[obs["asp_chg"] <= math.log(0.9)]), "no_cut": rate(obs[obs["asp_chg"] > math.log(0.9)])}
E["vt"] = pd.qcut(E["video_sh"].rank(method="first"), 3, labels=["low", "mid", "high"])
R["B8_video_share_tercile"] = {str(k): rate(g) for k, g in E.groupby("vt", observed=True)}
R["B8_live_share"] = {"live>=0.5": rate(E[E["live_sh"] >= 0.5]), "live<0.5": rate(E[E["live_sh"] < 0.5])}

(W / "stage_b_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: R[k] for k in ("universe", "coverage", "F_selection")}, indent=1, default=str)[:2500])
for s in ("S1_all", "S1_late", "S2_all"):
    print(s, "best simple:", R[s]["best_simple_rule"], "lift:", R[s]["lift_vs_best_simple"], "material:", R[s]["material"])
    for n in METHODS:
        print("   ", f"{n:20}", {k: R[s]["mean"][n][k] for k in ("catP@10", "catP@20", "P@100", "recall@20", "FP_per_TP@20", "AUC", "PR_AUC", "base")})
    print("   F vs:", json.dumps(R[s]["F_vs"]))
print("ablations", json.dumps(R["ablations_S1_logit"]))
print("calibration", R["F_calibration_S1"], "\nstability", R["F_stability"])
print("by category ahead", R["S1_categories_F_ahead"], R["S1_by_month_F_minus_best_rule"])
print(INV[["signal", "S1_dAUC", "S1_dAUC_ci95", "S1_months_pos", "S2_dAUC", "rho_with_same_month_growth", "lag_rho", "classification"]].to_string(index=False))
print(json.dumps(R["lead_time"], indent=0)[:6000])
print(R["lead_time_successes"])
print("B8", json.dumps({k: R[k] for k in ("B8_price_cut", "B8_video_share_tercile", "B8_live_share")}))
