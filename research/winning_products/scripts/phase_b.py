"""Phase B: trajectory groups and H-A1 (registry/PHASE_B_PLAN.md, frozen before this ran). Read-only on kalodata.db.

Writes _work/phase_b_results.json (all numbers in the report), _work/phase_b_tables.md (readable tables) and
_work/cache/phase_b_groups.pkl (one row per product x category; git-ignored).
Run: python -I research/winning_products/scripts/phase_b.py
"""
import glob
import json
import math
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier, export_text

sys.path.insert(0, str(Path(__file__).resolve().parent))
import panel  # noqa: E402

warnings.filterwarnings("ignore")
HUB = panel.HUB
WORK = HUB / "research" / "winning_products" / "_work"
NICHE = ["601152", "601352", "605248", "953224"]
SEED = 20261031
R = {"plan": "registry/PHASE_B_PLAN.md"}

top, lists = panel.build()
cat_names = dict(sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True).execute(
    "select category_id, category_name from categories"))
top["asp_med"] = top.groupby(["cat", "month"])["asp"].transform("median")
top["shop_n"] = top.groupby(["cat", "month", "seller_id"])["pid"].transform("size")
LAST = len(panel.MONTHS) - 1  # 11 = 2026-09; window = 1..11 (Oct-2025 is index 0, membership only)


def slope(y):
    x = np.arange(len(y))
    return np.polyfit(x, y, 1)[0]


# ------------------------------------------------------------------ 1. classify trajectories
recs = []
for (pid, cat), g in top.groupby(["pid", "cat"], sort=False):
    g = g.set_index("mi").sort_index()
    S = set(g.index)
    W = sorted(m for m in S if 1 <= m <= LAST)
    if not W:
        continue
    runs, cur = [], [W[0]]
    for m in W[1:]:
        if m == cur[-1] + 1:
            cur.append(m)
        else:
            runs.append(cur)
            cur = [m]
    runs.append(cur)
    longest = max(runs, key=len)
    e = runs[0][0] if (runs[0][0] - 1) not in S else None
    rev, rank = g["revenue"], g["rank"]
    grp = None
    if len(W) == 1 or (len(W) < 3 and (1 in W or LAST in W)):
        grp = "F"
    elif len(longest) >= 6 and rank.loc[longest].median() <= 200:
        grp = "A"
    elif len(longest) >= 6 and rev.loc[longest].std(ddof=0) / rev.loc[longest].mean() <= 0.5:
        grp = "E"
    if grp is None and e is not None:
        p = rev.loc[W].idxmax()
        prun = next(r for r in runs if p in r)
        if (e <= p <= e + 2 and (rev[p] >= 3 * rev[e] or rank[p] <= 100) and prun[-1] <= p + 1
                and prun[-1] + 1 <= LAST and len(W) <= 4):
            grp = "C"
    if grp is None and e is not None:
        end = min(e + 3, LAST)
        win = [m for m in W if e <= m <= end]
        if (rank.loc[win].min() <= rank[e] - 200 or rank.loc[win].min() <= 100) and end in S:
            grp = "B"
    if grp is None and len(W) >= 3:
        last3 = W[-3:]
        if slope(np.log(rev.loc[last3].values)) < 0 and W[-1] < LAST:
            grp = "D"
    grp = grp or "U"
    first = e if e is not None else W[0]
    row = g.loc[first]
    lm = int(str(row["launch_date"])[:4]) * 12 + int(str(row["launch_date"])[5:7]) if row["launch_date"] else None
    fm = int(panel.MONTHS[first][:4]) * 12 + int(panel.MONTHS[first][5:])
    recs.append(dict(
        pid=pid, cat=cat, group=grp, entry=e, first=first, n_obs=len(W), longest=len(longest),
        left_censored=1 in W and 0 in S, right_censored=LAST in W,
        med_rank=float(rank.loc[W].median()), med_rev=float(rev.loc[W].median()), peak_rev=float(rev.loc[W].max()),
        # features at the first observed (= entry, when there is one) month
        rank_pct=row["rank"] / 500, log_rev_cut=math.log(row["revenue"] / row["cutoff"]), log_asp=math.log(max(row["asp"], 0.01)),
        asp_rel=math.log(max(row["asp"], 0.01) / max(row["asp_med"], 0.01)), age=(fm - lm) if lm else np.nan,
        video_sh=row["video_revenue"] / row["revenue"], live_sh=row["live_revenue"] / row["revenue"],
        showcase_sh=row["showcase_revenue"] / row["revenue"], shop_n=float(row["shop_n"]),
        kalo_g=float(np.sign(row["kalo_g"]) * math.log1p(abs(row["kalo_g"]))) if pd.notna(row["kalo_g"]) else np.nan,
        growth_next=(math.log(rev[first + 1] / rev[first]) if (first + 1) in S else np.nan),  # mechanical for A/C
        seller_id=row["seller_id"]))
G = pd.DataFrame(recs)

# visible the month before entry (any list in the same category; deep lists only exist for the niche)
vis = lists.assign(mi=lists["month"].map(panel.MIDX))
for kind, col in (("risers", "prev_riser"), ("risers_deep", "prev_riser_deep"), ("top_deep", "prev_top_deep")):
    s = set(zip(vis.loc[vis["kind"] == kind, "pid"], vis.loc[vis["kind"] == kind, "cat"], vis.loc[vis["kind"] == kind, "mi"]))
    G[col] = [((p, c, e - 1) in s) if pd.notna(e) else np.nan for p, c, e in zip(G["pid"], G["cat"], G["entry"])]
G["prev_visible"] = G[["prev_riser", "prev_riser_deep", "prev_top_deep"]].max(axis=1)
G.to_pickle(panel.CACHE / "phase_b_groups.pkl")

# ------------------------------------------------------------------ 2. group profiles
R["group_counts"] = G["group"].value_counts().to_dict()
R["group_counts_with_entry"] = G[G["entry"].notna()]["group"].value_counts().to_dict()
prof = G.groupby("group").agg(n=("pid", "size"), n_obs_med=("n_obs", "median"), med_rank=("med_rank", "median"),
                              med_rev=("med_rev", "median"), peak_rev=("peak_rev", "median"),
                              asp=("log_asp", lambda x: float(np.exp(x.median()))), age_first=("age", "median"),
                              video_sh=("video_sh", "mean"), live_sh=("live_sh", "mean"), showcase_sh=("showcase_sh", "mean"),
                              shop_n=("shop_n", "median"), left_cens=("left_censored", "mean"), right_cens=("right_censored", "mean"))
R["group_profiles"] = prof.round(3).reset_index().to_dict("records")
bycat = pd.crosstab(G["cat"].map(cat_names), G["group"], normalize="index").round(3)
R["group_share_by_category"] = bycat.reset_index().to_dict("records")
R["age_at_entry_by_group"] = G[G["entry"].notna()].groupby("group")["age"].describe(percentiles=[.1, .5, .9]).round(1).reset_index().to_dict("records")

# ------------------------------------------------------------------ 3. H-A1 and B vs D
FEATS = ["rank_pct", "log_rev_cut", "log_asp", "asp_rel", "age", "video_sh", "live_sh", "showcase_sh", "shop_n",
         "prev_visible", "kalo_g"]
FEATS[FEATS.index("shop_n")] = "log_shop_n"
G["log_shop_n"] = np.log(G["shop_n"])
G["prev_visible"] = G["prev_visible"].astype(float)


def compare(pos, neg, label):
    d = G[(G["group"].isin([pos, neg])) & G["entry"].between(1, 6)].dropna(subset=FEATS).copy()
    d["y"] = (d["group"] == pos).astype(int)
    out = {"n": {pos: int(d["y"].sum()), neg: int((1 - d["y"]).sum())}, "features": {}}
    for f in FEATS + ["growth_next"]:
        a, b = d.loc[d.y == 1, f].dropna(), d.loc[d.y == 0, f].dropna()
        smd = (a.mean() - b.mean()) / math.sqrt((a.var() + b.var()) / 2) if len(a) > 1 and len(b) > 1 else np.nan
        signs, cohorts = [], 0
        for c, dc in d.groupby("entry"):
            a2, b2 = dc.loc[dc.y == 1, f].dropna(), dc.loc[dc.y == 0, f].dropna()
            if len(a2) >= 5 and len(b2) >= 5:
                cohorts += 1
                s2 = (a2.mean() - b2.mean()) / math.sqrt((a2.var() + b2.var()) / 2 + 1e-12)
                signs.append(np.sign(s2))
        same = sum(1 for s in signs if s == np.sign(smd)) if not np.isnan(smd) else 0
        out["features"][f] = {"mean_pos": round(float(a.mean()), 4), "mean_neg": round(float(b.mean()), 4),
                              "smd": round(float(smd), 3), "cohorts_eligible": cohorts, "cohorts_same_sign": same,
                              "supported": bool(abs(smd) >= 0.2 and same >= 4) if f != "growth_next" else "mechanical"}
    # logit with category and cohort fixed effects, standardised features
    X = d[FEATS].astype(float)
    LF = [f for f in FEATS if f != "showcase_sh"]  # shares sum to 1: drop one from the logit (deviation, EXP-B-001)
    mu, sd = X[LF].mean(), X[LF].std().replace(0, 1)
    Z = (X[LF] - mu) / sd
    fe = pd.get_dummies(d[["cat"]].astype(str).assign(coh=d["entry"].astype(int).astype(str)), drop_first=True).astype(float)
    Xl = sm.add_constant(pd.concat([Z, fe], axis=1))
    try:
        m = sm.Logit(d["y"], Xl).fit(disp=0, method="newton", maxiter=200)
        pv = m.pvalues[LF]
        order = pv.sort_values().index
        holm, k = {}, len(LF)
        running = 0
        for i, f in enumerate(order):
            running = max(running, min(1, pv[f] * (k - i)))
            holm[f] = running
        ci = m.conf_int().loc[LF]
        out["logit"] = {f: {"odds_ratio_per_sd": round(float(np.exp(m.params[f])), 3),
                            "ci95": [round(float(np.exp(ci.loc[f, 0])), 3), round(float(np.exp(ci.loc[f, 1])), 3)],
                            "p_holm": round(float(holm[f]), 4)} for f in LF}
        out["logit_n_params"] = int(len(m.params)); out["logit_converged"] = bool(m.mle_retvals.get("converged"))
        out["logit_pseudo_r2"] = round(float(m.prsquared), 3)
    except Exception as ex:  # record the failure, never hide it
        out["logit_error"] = repr(ex)
    # leave-one-cohort-out AUC: logit (features + category), depth-3 tree, entry rank alone
    aucs = {"logit": [], "tree": [], "rank_only": []}
    catd = pd.get_dummies(d["cat"].astype(str), drop_first=True).astype(float)
    for c in sorted(d["entry"].unique()):
        tr, te = d["entry"] != c, d["entry"] == c
        if d.loc[te, "y"].nunique() < 2:
            continue
        Xa = pd.concat([Z, catd], axis=1)
        lr = LogisticRegression(max_iter=2000, C=1.0).fit(Xa[tr], d.loc[tr, "y"])
        aucs["logit"].append(roc_auc_score(d.loc[te, "y"], lr.predict_proba(Xa[te])[:, 1]))
        tr3 = DecisionTreeClassifier(max_depth=3, min_samples_leaf=50, random_state=SEED).fit(X[tr], d.loc[tr, "y"])
        aucs["tree"].append(roc_auc_score(d.loc[te, "y"], tr3.predict_proba(X[te])[:, 1]))
        aucs["rank_only"].append(roc_auc_score(d.loc[te, "y"], -d.loc[te, "rank_pct"]))
    out["loco_auc_mean"] = {k: round(float(np.mean(v)), 3) for k, v in aucs.items() if v}
    out["loco_auc_by_cohort"] = {k: [round(float(x), 3) for x in v] for k, v in aucs.items()}
    tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=50, random_state=SEED).fit(X, d["y"])
    out["tree_rules"] = export_text(tree, feature_names=FEATS, decimals=3)
    out["note"] = f"positive class = {pos}; descriptive/exploratory (groups defined with future months)"
    R[label] = out
    return d


dA = compare("A", "C", "H-A1_A_vs_C")
dB = compare("B", "D", "secondary_B_vs_D")

# ------------------------------------------------------------------ 4. niche-only evidence
N = G[G["cat"].isin(NICHE) & G["entry"].between(1, 6)].copy()
R["niche_prev_visibility_by_group"] = (N.groupby("group")[["prev_top_deep", "prev_riser", "prev_visible"]]
                                       .apply(lambda x: x.astype(float).mean()).round(3).reset_index().to_dict("records"))
R["niche_n_by_group"] = N["group"].value_counts().to_dict()
shop_type = {}
for f in glob.glob(str(HUB / "research" / "kalodata" / "raw" / "gaps_tier2" / "shops_*.json")):
    for s in (json.load(open(f, encoding="utf-8"))["response"].get("data") or []):
        shop_type[str(s.get("shop_id"))] = s.get("shop_type")
NN = G[G["cat"].isin(NICHE)].copy()
NN["shop_type"] = NN["seller_id"].astype(str).map(shop_type)
R["niche_shop_type_by_group"] = {
    "coverage": round(float(NN["shop_type"].notna().mean()), 3),
    "brand_share_where_known": NN.dropna(subset=["shop_type"]).groupby("group")["shop_type"]
    .apply(lambda s: round(float((s == "BRAND").mean()), 3)).to_dict(),
    "n_known": NN.dropna(subset=["shop_type"])["group"].value_counts().to_dict()}
con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
det = pd.read_sql_query("""select d.product_id pid, q.month, d.creator_number, d.video_number, d.live_number
    from product_details d join pulls q using(pull_id) where q.month is not null and q.kind='detail'""", con)
det["mi"] = det["month"].map(panel.MIDX)
m = G.merge(det, left_on=["pid", "first"], right_on=["pid", "mi"])
R["detail_sample_at_first_month"] = {
    "n": len(m), "by_group": m.groupby("group")[["creator_number", "video_number", "live_number"]]
    .median().round(1).reset_index().to_dict("records"),
    "n_by_group": m["group"].value_counts().to_dict()}

(WORK / "phase_b_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: R[k] for k in ("group_counts", "group_counts_with_entry")}, indent=1))
for lab in ("H-A1_A_vs_C", "secondary_B_vs_D"):
    o = R[lab]
    print("\n==", lab, o["n"], "LOCO AUC", o.get("loco_auc_mean"), "pseudoR2", o.get("logit_pseudo_r2"), o.get("logit_error", ""))
    for f, v in o["features"].items():
        lg = o.get("logit", {}).get(f, {})
        print(f"  {f:12} {v['mean_pos']:>9} {v['mean_neg']:>9} smd {v['smd']:>7} same {v['cohorts_same_sign']}/{v['cohorts_eligible']} "
              f"sup {v['supported']!s:10} OR {lg.get('odds_ratio_per_sd')} {lg.get('ci95')} pHolm {lg.get('p_holm')}")
    print(o["tree_rules"])
