"""Phase C, all 28 categories: walk-forward models vs baselines, feature ablations, growth deciles
(registry/PHASE_C_PLAN.md §1-4). Read-only. Writes _work/phase_c_results.json.
Run: python -I research/winning_products/scripts/phase_c.py
"""
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features as F  # noqa: E402
import panel  # noqa: E402

warnings.filterwarnings("ignore")
SEED, BOOT = 20261031, 2000
WORK = panel.HUB / "research" / "winning_products" / "_work"
RNG = np.random.default_rng(SEED)
D = F.build_features()
CATS = sorted(D["cat"].unique())


def design(train, test, feats):
    mu, sd = train[feats].mean(), train[feats].std().replace(0, 1)
    def mk(x):
        z = (x[feats] - mu) / sd
        dummies = pd.get_dummies(pd.Categorical(x["cat"], categories=CATS), prefix="c", drop_first=True).astype(float)
        dummies.index = x.index
        return pd.concat([z, dummies], axis=1).values
    return mk(train), mk(test)


def fit_logit(train, test, feats, y):
    Xtr, Xte = design(train, test, feats)
    m = LogisticRegression(C=0.5, max_iter=3000).fit(Xtr, train[y])
    return m.predict_proba(Xte)[:, 1]


def fit_hgb(train, test, feats, y):
    cols = feats + ["cat_code"]
    tr, te = train.assign(cat_code=train["cat"].map({c: i for i, c in enumerate(CATS)})), \
        test.assign(cat_code=test["cat"].map({c: i for i, c in enumerate(CATS)}))
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, l2_regularization=1.0,
                                       categorical_features=[len(feats)], random_state=SEED)
    m.fit(tr[cols].values, tr[y])
    return m.predict_proba(te[cols].values)[:, 1]


BASELINES = {
    "B0 random": lambda x: RNG.random(len(x)),
    "B1 revenue vs cutoff": lambda x: x["log_rev_cut"].values,
    "B2 rank": lambda x: -x["rank_pct"].values,
    "B3 MoM growth": lambda x: np.where(x["new_entrant"] == 1, -9, x["mom_g"]),
    "B4 Kalodata momentum": lambda x: x["kalo_g"].values,
    "B5 3-month momentum": lambda x: x["months_top_last3"].values + 0.5 * x["mom_g"].values,
}


def metrics(test, score, y):
    s = pd.Series(score, index=test.index)
    lab = test[y]
    top50 = lab.loc[s.sort_values(ascending=False).index[:50]].mean()
    top20 = lab.loc[s.sort_values(ascending=False).index[:20]].mean()
    catp = np.mean([lab.loc[s[g.index].sort_values(ascending=False).index[:10]].mean() for _, g in test.groupby("cat")])
    return {"P@50": float(top50), "P@20": float(top20), "catP@10": float(catp),
            "AUC": float(roc_auc_score(lab, s)) if lab.nunique() > 1 else np.nan, "base": float(lab.mean())}


def boot_ci(diff):
    diff = np.asarray(diff, float)
    b = [RNG.choice(diff, len(diff)).mean() for _ in range(BOOT)]
    return [round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)], float(np.mean(np.array(b) <= 0))


def walk(y, universe, test_months, h):
    U = D[universe(D) & D[y].notna()]
    per = {}
    for t in test_months:
        tr, te = U[U["mi"] <= t - h], U[U["mi"] == t]
        if te.empty or tr.empty:
            continue
        res = {name: metrics(te, f(te), y) for name, f in BASELINES.items()}
        p1 = fit_logit(tr, te, F.NUM, y)
        p2 = fit_hgb(tr, te, F.NUM, y)
        res["M1 logit"] = dict(metrics(te, p1, y), Brier=float(brier_score_loss(te[y], p1)))
        res["M2 boosted trees"] = dict(metrics(te, p2, y), Brier=float(brier_score_loss(te[y], p2)))
        per[panel.MONTHS[t]] = res
    return per


def summarise(per):
    names = list(next(iter(per.values())))
    mean = {n: {k: round(float(np.nanmean([per[m][n][k] for m in per])), 4) for k in per[next(iter(per))][n]} for n in names}
    base_names = [n for n in names if n.startswith("B") and n != "B0 random"]
    best = max(base_names, key=lambda n: mean[n]["P@50"])
    verdict = {}
    for mname in ("M1 logit", "M2 boosted trees"):
        diff = [per[m][mname]["P@50"] - per[m][best]["P@50"] for m in per]
        ci, p = boot_ci(diff)
        ahead = sum(1 for d in diff if d > 0)
        verdict[mname] = {"vs": best, "mean_lift_P@50": round(float(np.mean(diff)), 4), "ci95": ci, "p_boot": round(p, 4),
                          "months_ahead": f"{ahead}/{len(diff)}",
                          "beats_best_baseline": bool(ci[0] > 0 and ahead >= math.ceil(2 * len(diff) / 3))}
    return {"mean_by_model": mean, "best_baseline": best, "verdict": verdict}


mid = lambda x: x["rank"].between(101, 500)  # noqa: E731
H1_TEST = [panel.MIDX[m] for m in ("2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08")]
T4_TEST = [panel.MIDX[m] for m in ("2026-03", "2026-04", "2026-05", "2026-06")]


def main():
    R = {"plan": "registry/PHASE_C_PLAN.md", "n_rows": len(D)}
    for y, months, h in (("T1", H1_TEST, 1), ("T2", H1_TEST, 1), ("T4", T4_TEST, 3)):
        per = walk(y, mid, months, h)
        R[y] = {"per_month": per, **summarise(per)}
        print(y, json.dumps(R[y]["verdict"]), "best baseline:", R[y]["best_baseline"])
        for n, v in R[y]["mean_by_model"].items():
            print(f"   {n:24} " + " ".join(f"{k}={v[k]}" for k in v))

    # ------------------------------------------------------------------ ablations (H-B*, H-D*) on T1
    U = D[mid(D) & D["T1"].notna()]
    abl = {g: [] for g in F.GROUPS}
    abl_auc = {g: [] for g in F.GROUPS}
    for t in H1_TEST:
        tr, te = U[U["mi"] <= t - 1], U[U["mi"] == t]
        full = fit_logit(tr, te, F.NUM, "T1")
        mf = metrics(te, full, "T1")
        for g, cols in F.GROUPS.items():
            red = fit_logit(tr, te, [c for c in F.NUM if c not in cols], "T1")
            mr = metrics(te, red, "T1")
            abl[g].append(mf["P@50"] - mr["P@50"])
            abl_auc[g].append(mf["AUC"] - mr["AUC"])
    out, ps = {}, {}
    for g in F.GROUPS:
        ci, p = boot_ci(abl[g])
        ps[g] = p
        out[g] = {"dP@50_mean": round(float(np.mean(abl[g])), 4), "ci95": ci, "months_positive": f"{sum(d > 0 for d in abl[g])}/{len(abl[g])}",
                  "dAUC_mean": round(float(np.mean(abl_auc[g])), 5), "dAUC_ci95": boot_ci(abl_auc[g])[0], "p_boot": round(p, 4)}
    order, running = sorted(ps, key=ps.get), 0
    for i, g in enumerate(order):
        running = max(running, min(1.0, ps[g] * (len(order) - i)))
        out[g]["p_holm"] = round(running, 4)
        pos = sum(d > 0 for d in abl[g])
        out[g]["supported"] = bool(out[g]["ci95"][0] > 0 and pos >= math.ceil(2 * len(abl[g]) / 3) and running < 0.05)
    R["ablations_T1"] = out
    print("\nAblations (T1, M1):")
    for g, v in out.items():
        print(f"   {g:26} {v}")

    # ------------------------------------------------------------------ H-B4: retention by growth decile (pooled, labelled cutoffs)
    G = U[U["new_entrant"] == 0].copy()
    G["dec"] = pd.qcut(G["mom_g"].rank(method="first"), 10, labels=False) + 1
    rows = []
    for d_, g in G.groupby("dec"):
        n, k = len(g), g["T1"].sum()
        p = k / n
        z = 1.96
        den = 1 + z * z / n
        c = (p + z * z / (2 * n)) / den
        hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        rows.append({"decile": int(d_), "mom_g_min": round(float(g["mom_g"].min()), 3), "mom_g_max": round(float(g["mom_g"].max()), 3),
                     "n": n, "T1": round(p, 4), "ci95": [round(c - hw, 4), round(c + hw, 4)]})
    R["H-B4_growth_deciles"] = rows
    mid_hi = min(r["ci95"][0] for r in rows if 6 <= r["decile"] <= 9)
    R["H-B4_supported"] = bool(rows[-1]["ci95"][1] < mid_hi)
    ne = U[U["new_entrant"] == 1]
    R["new_entrant_T1"] = {"n": len(ne), "T1": round(float(ne["T1"].mean()), 4)}
    print("\nH-B4 deciles:", [(r["decile"], r["T1"]) for r in rows], "supported:", R["H-B4_supported"], "new entrants:", R["new_entrant_T1"])
    (WORK / "phase_c_results.json").write_text(json.dumps(R, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
