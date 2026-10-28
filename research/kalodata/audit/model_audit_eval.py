"""Model validation audit: read-only re-analysis of the Kalodata product models (Phase A, 2026-10-28).

Reuses load()/build()/TASKS/subset() from scripts/train_product_model.py (read-only DB access), then:
  1. replicates the reported single-split AUCs;
  2. rolling-origin evaluation with an h-month embargo (train only on rows whose label had matured by the
     test month) comparing the GBM with simple baselines, month by month;
  3. product-cluster and month-block bootstrap CIs; reliability tables; rank/sales-band breakdowns;
  4. leakage probes (current-value features, no embargo, partial Oct 2025, a "clean" variant without both),
     category results, leave-one-category-out, out-of-range probe for deeper riser positions, entrant coverage,
     commission bands.
Nothing is written except the results JSON (default: next to this script). Seeds fixed; ~8 minutes on 8 cores.
Run from the Hub folder: python -I research/kalodata/audit/model_audit_eval.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HUB = Path.cwd()
sys.path.insert(0, str(HUB / "scripts"))
import train_product_model as tp  # noqa: E402

FEATURES, HGB, MONTHS = tp.FEATURES, tp.HGB, tp.MONTHS
NORISER = [f for f in FEATURES if f not in ("riser_pos", "rank_pos", "in_risers")]
SNAPSHOT = ["commission_rate", "log_sku"]  # identical for a product in every month = values as of the Oct 2026 pull
NOSNAP = [f for f in FEATURES if f not in SNAPSHOT]
CLEAN = [f for f in FEATURES if f not in SNAPSHOT + ["age_days"]]  # also drop age from the current launch_date
RNG = np.random.default_rng(20261027)
N_BOOT = 200
OUTFILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("model_audit_results.json")
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)


# ---------------------------------------------------------------- data
def panel():
    df, cats, _ = tp.load()
    deep = (df["list"] == "risers") & (df["month"] == "2026-09") & (df["pos"] > 200)
    deep_rows = int(deep.sum())
    p = tp.build(df[~deep].copy())          # history-consistent panel: risers 1-200 in every month
    pdeep = tp.build(df)                     # as the scripts see the DB today (Sep risers 1-1,000)
    t = p[p["in_top500"]]
    floor = t.groupby(["cat", "month"])["revenue"].min()
    for q in (p, pdeep):
        q["floor"] = q.set_index(["cat", "month"]).index.map(floor).values
        q["log_vs_floor"] = np.log10(q["revenue"].clip(lower=1) / q["floor"])
        q["cat_rel_growth"] = q.groupby(["cat", "month"])["growth_slog"].rank(pct=True)
    return p, pdeep, cats, deep_rows


def task_frame(p, name):
    which, label, h = tp.TASKS[name]
    d = tp.subset(p, which, h)
    d["y"] = label(d).values
    return d, h


# ---------------------------------------------------------------- models and baselines
def gbm(tr, te, feats):
    return HistGradientBoostingClassifier(**HGB).fit(tr[feats], tr["y"]).predict_proba(te[feats])[:, 1]


def logit(tr, te, feats):
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))
    m.fit(tp.filled(tr[feats], tr[feats]), tr["y"])
    return m.predict_proba(tp.filled(te[feats], tr[feats]))[:, 1]


def baselines(te, kind):
    b = {"growth": te["growth_slog"].fillna(0).values,
         "cat_rel_growth": te["cat_rel_growth"].fillna(0.5).values,
         "momentum_prev_ratio": np.log(te["prev_ratio"].fillna(0) + 1e-3).values,
         "persistence_months_seen": te["months_seen_before"].fillna(0).values,
         "sales": te["log_sales"].values}
    if kind == "breakouts":
        b["sales_vs_floor"] = te["log_vs_floor"].values
        b["riser_rank"] = -te["riser_pos"].values
    else:
        b["rank"] = -te["rank_pos"].values
    return b


# ---------------------------------------------------------------- metrics
def prec_at_k(y, s, k):
    k = min(k, len(y))
    return float(y[np.argsort(-s, kind="stable")[:k]].mean())


def month_metrics(y, s, prob):
    r = {"n": int(len(y)), "pos": int(y.sum()), "base": float(y.mean())}
    if 0 < y.sum() < len(y):
        r["auc"] = roc_auc_score(y, s)
        r["ap"] = average_precision_score(y, s)
    for k in (10, 20, 50):
        r[f"p@{k}"] = prec_at_k(y, s, k)
        r[f"lift@{k}"] = r[f"p@{k}"] / r["base"] if r["base"] else np.nan
    r["p@10pct"] = prec_at_k(y, s, max(1, len(y) // 10))
    if prob:
        r["brier"] = brier_score_loss(y, s)
        r["brier_climatology"] = float(y.mean() * (1 - y.mean()))
    return r


def per_cat_top10(te, s):
    d = te[["cat", "month", "y"]].assign(s=s)
    return float(d.sort_values("s", ascending=False).groupby(["cat", "month"]).head(10)["y"].mean())


def cluster_boot(y, scores, groups, probs, n=N_BOOT, ref="gbm"):
    """Product-cluster bootstrap: resample products with replacement, rows weighted by draw count."""
    codes, uniq = pd.factorize(groups)
    out = {k: {"auc": [], "ap": [], "brier": [], "d_auc": []} for k in scores}
    for _ in range(n):
        w = np.bincount(RNG.integers(0, len(uniq), len(uniq)), minlength=len(uniq))[codes].astype(float)
        keep = w > 0
        yy, ww = y[keep], w[keep]
        a_ref = roc_auc_score(yy, scores[ref][keep], sample_weight=ww)
        for k, s in scores.items():
            a = roc_auc_score(yy, s[keep], sample_weight=ww)
            out[k]["auc"].append(a)
            out[k]["ap"].append(average_precision_score(yy, s[keep], sample_weight=ww))
            out[k]["d_auc"].append(a_ref - a)
            if k in probs:
                out[k]["brier"].append(brier_score_loss(yy, s[keep], sample_weight=ww))
    ci = lambda v: [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)] if v else None  # noqa
    return {k: {m: ci(v) for m, v in d.items()} for k, d in out.items()}


def month_boot(month_tab, metric, models, n=2000):
    months = sorted(month_tab)
    res = {}
    for k in models:
        vals = np.array([month_tab[m][k].get(metric, np.nan) for m in months])
        draws = [np.nanmean(vals[RNG.integers(0, len(vals), len(vals))]) for _ in range(n)]
        res[k] = [round(float(np.nanmean(vals)), 3), round(float(np.percentile(draws, 2.5)), 3),
                  round(float(np.percentile(draws, 97.5)), 3)]
    return res


def reliability(y, s, bins=(0, .02, .05, .1, .2, .3, .5, .7, 1.0001)):
    c = pd.cut(s, bins=bins, right=False)
    t = pd.DataFrame({"y": y, "s": s, "b": c}).groupby("b", observed=True).agg(n=("y", "size"), mean_pred=("s", "mean"),
                                                                                observed=("y", "mean"))
    return [{"bin": str(i), "n": int(r.n), "mean_pred": round(float(r.mean_pred), 3), "observed": round(float(r.observed), 3)}
            for i, r in t.iterrows()]


def r3(x):
    if isinstance(x, dict):
        return {k: r3(v) for k, v in x.items()}
    if isinstance(x, list):
        return [r3(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if np.isnan(x) else round(float(x), 3)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


# ---------------------------------------------------------------- 1. replication of the reported split
def replicate(p):
    out = {}
    for name in tp.TASKS:
        d, h = task_frame(p, name)
        last = d["mi"].max()
        tm = [last - 2, last - 1, last]
        tr, te = d[~d["mi"].isin(tm)], d[d["mi"].isin(tm)]
        s = gbm(tr, te, FEATURES)
        r = {"test_months": [MONTHS[i] for i in tm], "auc_gbm": roc_auc_score(te["y"], s),
             "base": float(te["y"].mean())}
        if name.startswith("breakouts"):
            r["auc_gbm_noriser_score_breakouts_split"] = roc_auc_score(te["y"], gbm(tr, te, NORISER))
        tr_e = d[d["mi"] <= tm[0] - h]  # same test rows, training limited to labels mature at the first test month
        r["auc_gbm_embargoed_same_test"] = roc_auc_score(te["y"], gbm(tr_e, te, FEATURES))
        out[name] = r
        log("replicate", name, r3(r))
    return out


# ---------------------------------------------------------------- 2. rolling origin
def rolling(p, name, test_months, variants=True, drop_oct=False):
    d, h = task_frame(p, name)
    kind = name.split("_")[0]
    rows, month_tab = [], {}
    for t in test_months:
        tr = d[(d["mi"] <= t - h)]
        if drop_oct:
            tr = tr[tr["mi"] > 0]
        te = d[d["mi"] == t].copy()
        sc = {"gbm": gbm(tr, te, FEATURES), "logistic": logit(tr, te, FEATURES)}
        two = ["log_vs_floor", "growth_slog"] if kind == "breakouts" else ["rank_pos", "growth_slog"]
        sc["logistic_2feat"] = logit(tr, te, two)
        if variants:
            sc["gbm_no_snapshot"] = gbm(tr, te, NOSNAP)
            # "clean": no current-value features, no Oct 2025 rows and no Nov rows (their lag features use Oct)
            tr_c = tr[tr["mi"] >= 2]
            sc["gbm_clean"] = gbm(tr_c, te, CLEAN) if len(tr_c) else np.full(len(te), np.nan)
            if kind == "breakouts":
                sc["gbm_no_riser_pos"] = gbm(tr, te, NORISER)
            if h > 1:
                sc["gbm_no_embargo"] = gbm(d[d["mi"] < t], te, FEATURES)
        sc.update(baselines(te, kind))
        y = te["y"].values
        probs = {k for k in sc if k.startswith(("gbm", "logistic"))}
        month_tab[MONTHS[t]] = {k: month_metrics(y, s, k in probs) for k, s in sc.items()}
        for k, s in sc.items():
            month_tab[MONTHS[t]][k]["top10_per_cat_month"] = per_cat_top10(te, s)
        keep = te[["product_id", "cat", "month", "y", "log_vs_floor", "rank_pos", "riser_pos", "log_sales",
                   "commission_rate"]].copy()
        for k, s in sc.items():
            keep[f"s_{k}"] = s
        keep["n_train"] = len(tr)
        rows.append(keep)
        log(name, MONTHS[t], "train", len(tr), "test", len(te), "AUC gbm",
            round(month_tab[MONTHS[t]]["gbm"].get("auc", np.nan), 3), "clean",
            round(month_tab[MONTHS[t]].get("gbm_clean", {}).get("auc", np.nan), 3))
    return pd.concat(rows), month_tab


def summarize(oos, month_tab, boot=True):
    y = oos["y"].values
    models = [c[2:] for c in oos.columns if c.startswith("s_")]
    scores = {k: oos[f"s_{k}"].values for k in models}
    probs = {k for k in models if k.startswith(("gbm", "logistic"))}
    pooled = {k: month_metrics(y, scores[k], k in probs) for k in models}
    res = {"pooled": pooled, "by_month": month_tab,
           "month_mean_auc_ci": month_boot(month_tab, "auc", models),
           "month_mean_p@20_ci": month_boot(month_tab, "p@20", models),
           "month_mean_lift@20_ci": month_boot(month_tab, "lift@20", models),
           "month_mean_top10_per_cat_ci": month_boot(month_tab, "top10_per_cat_month", models)}
    if boot:
        key = ["gbm", "logistic", "logistic_2feat", "growth", "cat_rel_growth", "sales", "sales_vs_floor", "rank",
               "riser_rank", "gbm_no_embargo", "gbm_no_snapshot"]
        res["product_cluster_ci"] = cluster_boot(y, {k: scores[k] for k in key if k in scores},
                                                 oos["product_id"].values, probs)
    res["reliability_gbm"] = reliability(y, scores["gbm"])
    res["reliability_logistic"] = reliability(y, scores["logistic"])
    hi = scores["gbm"] >= 0.5
    res["gbm_ge_50pct"] = {"n": int(hi.sum()), "hit_rate": float(y[hi].mean()) if hi.any() else None}
    return res


def bands(oos, kind):
    if kind == "breakouts":
        cuts = [-np.inf, np.log10(0.10), np.log10(0.25), np.log10(0.5), np.log10(0.75), np.inf]
        labels = ["<10% of floor", "10-25%", "25-50%", "50-75%", ">=75% of floor"]
        b = pd.cut(oos["log_vs_floor"], cuts, labels=labels)
    else:
        b = pd.cut(oos["rank_pos"], [0, 100, 250, 400, 450, 500], labels=["1-100", "101-250", "251-400", "401-450",
                                                                           "451-500"])
    out = []
    comp = ["gbm", "logistic", "growth", "sales_vs_floor" if kind == "breakouts" else "rank"]
    for lab, g in oos.groupby(b, observed=True):
        r = {"band": str(lab), "n": len(g), "positives": int(g["y"].sum()), "base": float(g["y"].mean()),
             "share_of_all_positives": float(g["y"].sum() / oos["y"].sum())}
        if 0 < g["y"].sum() < len(g):
            for k in comp:
                r[f"auc_{k}"] = roc_auc_score(g["y"], g[f"s_{k}"])
        out.append(r)
    return out


def by_category(oos, cats, n=100):
    out = []
    for c, g in oos.groupby("cat"):
        r = {"cat": cats.get(c, c), "n": len(g), "pos": int(g["y"].sum()), "base": float(g["y"].mean())}
        if g["y"].sum() >= 5 and g["y"].sum() < len(g):
            r["auc_gbm"] = roc_auc_score(g["y"], g["s_gbm"])
            r["auc_growth"] = roc_auc_score(g["y"], g["s_growth"])
            alt = "s_sales_vs_floor" if "s_sales_vs_floor" in g else "s_rank"
            r["auc_simple_size"] = roc_auc_score(g["y"], g[alt])
            codes, uniq = pd.factorize(g["product_id"])
            v = []
            for _ in range(n):
                w = np.bincount(RNG.integers(0, len(uniq), len(uniq)), minlength=len(uniq))[codes].astype(float)
                k = w > 0
                if 0 < g["y"].values[k].sum() < k.sum():
                    v.append(roc_auc_score(g["y"].values[k], g["s_gbm"].values[k], sample_weight=w[k]))
            r["auc_gbm_ci"] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
            top = g.sort_values("s_gbm", ascending=False).groupby("month").head(10)
            r["top10_per_month_hit"] = float(top["y"].mean())
        out.append(r)
    return sorted(out, key=lambda r: -r["n"])


# ---------------------------------------------------------------- other probes
def loco(p, cats, name="breakouts_3m"):
    """Leave-one-category-out on the reported test months: does the model transfer to an unseen category?"""
    d, h = task_frame(p, name)
    last = d["mi"].max()
    tm = [last - 2, last - 1, last]
    tr_all, te_all = d[d["mi"] <= tm[0] - h], d[d["mi"].isin(tm)]
    te_all = te_all.assign(s_in=gbm(tr_all, te_all, FEATURES))
    rows = []
    for c in sorted(d["cat"].unique()):
        te = te_all[te_all["cat"] == c]
        if te["y"].sum() < 5:
            continue
        s_out = gbm(tr_all[tr_all["cat"] != c], te, FEATURES)
        rows.append({"cat": cats.get(c, c), "n": len(te), "pos": int(te["y"].sum()),
                     "auc_in_category_training": roc_auc_score(te["y"], te["s_in"]),
                     "auc_category_held_out": roc_auc_score(te["y"], s_out)})
    return rows


def out_of_range_probe(p, name="breakouts_3m"):
    """Proxy for scoring risers 201-1,000 with a model trained on 1-200: train on riser positions 1-100 only
    (without riser features), score positions 101-200, compare with in-range scoring."""
    d, h = task_frame(p, name)
    allr = []
    for t in sorted(d["mi"].unique()):
        tr = d[(d["mi"] <= t - h)]
        if tr["mi"].nunique() < 3:
            continue
        te = d[d["mi"] == t]
        lo, hi = te[te["riser_pos"] <= 100], te[te["riser_pos"] > 100]
        trl = tr[tr["riser_pos"] <= 100]
        allr.append(pd.DataFrame({"y": hi["y"].values, "s_from_1_100": gbm(trl, hi, NORISER),
                                  "s_from_1_200": gbm(tr, hi, NORISER)}))
        allr.append(pd.DataFrame({"y": lo["y"].values, "s_in_range": gbm(trl, lo, NORISER)}))
    z = pd.concat(allr)
    a, b = z.dropna(subset=["s_from_1_100"]), z.dropna(subset=["s_in_range"])
    ge = a["s_from_1_100"] >= .5
    return {"in_range_pos_1_100": {"n": len(b), "base": float(b["y"].mean()), "auc": roc_auc_score(b["y"], b["s_in_range"]),
                                   "mean_pred": float(b["s_in_range"].mean()),
                                   "reliability": reliability(b["y"].values, b["s_in_range"].values)},
            "out_of_range_pos_101_200": {"n": len(a), "base": float(a["y"].mean()),
                                         "auc": roc_auc_score(a["y"], a["s_from_1_100"]),
                                         "mean_pred": float(a["s_from_1_100"].mean()),
                                         "reliability": reliability(a["y"].values, a["s_from_1_100"].values),
                                         "ge_50pct": {"n": int(ge.sum()), "hit": float(a.loc[ge, "y"].mean()) if ge.any()
                                                      else None}},
            "same_rows_model_trained_1_200": {"auc": roc_auc_score(a["y"], a["s_from_1_200"]),
                                              "mean_pred": float(a["s_from_1_200"].mean())}}


def deep_shift(pdeep):
    cur = pdeep[(pdeep["month"] == "2026-09") & (~pdeep["in_top500"]) & (pdeep["in_risers"] == 1)]
    hist = pdeep[(pdeep["mi"] <= 8) & (~pdeep["in_top500"]) & (pdeep["in_risers"] == 1)]
    out = {}
    for lab, g in (("train_risers_1_200_Oct_Jun", hist), ("sep_risers_1_200", cur[cur["riser_pos"] <= 200]),
                   ("sep_risers_201_1000", cur[cur["riser_pos"] > 200])):
        out[lab] = {"n": len(g), "median_sales": float(g["revenue"].median()),
                    "median_pct_of_floor": float((10 ** g["log_vs_floor"]).median() * 100),
                    "share_ge_50pct_of_floor": float((g["log_vs_floor"] >= np.log10(.5)).mean()),
                    "median_growth_pct": float(g["revenue_growth_rate"].median()),
                    "share_seen_before": float((g["months_seen_before"].fillna(0) > 0).mean())}
    return out


def entrant_coverage(p):
    """Of products entering a category top 500 (not top 500 the month before), how many were in that category's
    riser top 200 the month before (i.e. inside the breakout model's population)?"""
    key = {(a, m): (r, t) for a, m, r, t in zip(p["product_id"], p["mi"], p["in_risers"], p["in_top500"])}
    rows = []
    for mi in range(1, len(MONTHS)):
        ent = p[(p["mi"] == mi) & p["in_top500"]]
        n_new, n_cov = 0, 0
        for a in ent["product_id"]:
            prev = key.get((a, mi - 1))
            if prev and prev[1]:
                continue
            n_new += 1
            n_cov += int(prev is not None and prev[0] == 1)
        rows.append({"month": MONTHS[mi], "entrants": n_new, "in_riser_list_prev_month": n_cov,
                     "share": n_cov / n_new if n_new else None})
    return rows


def commission_bands(p, name="breakouts_3m"):
    d, _ = task_frame(p, name)
    b = pd.cut(d["commission_rate"], [-0.01, 0.0001, 5, 10, 15, 100], labels=["0%", "0-5%", "5-10%", "10-15%", ">15%"])
    out = []
    for lab, g in d.groupby(b, observed=True):
        codes, uniq = pd.factorize(g["product_id"])
        yy = g["y"].values
        v = []
        for _ in range(300):
            w = np.bincount(RNG.integers(0, len(uniq), len(uniq)), minlength=len(uniq))[codes]
            v.append((yy * w).sum() / w.sum())
        out.append({"band": str(lab), "n": len(g), "products": len(uniq), "rate": float(yy.mean()),
                    "ci": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]})
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p, pdeep, cats, deep_rows = panel()
    log("panel", len(p), "rows; deep Sep riser rows excluded from history panel:", deep_rows)
    R = {"meta": {"sklearn": __import__("sklearn").__version__, "pandas": pd.__version__, "numpy": np.__version__,
                  "n_boot": N_BOOT, "panel_rows": len(p), "panel_rows_incl_deep": len(pdeep),
                  "deep_rows_excluded": deep_rows}}
    t5 = p[p["in_top500"]]
    R["meta"]["top500_median_sales_by_month"] = {m: float(v) for m, v in t5.groupby("month")["revenue"].median().items()}
    R["replication"] = replicate(p)
    plan = {"holders_1m": range(3, 11), "breakouts_1m": range(3, 11), "breakouts_3m": range(5, 9),
            "holders_3m": range(5, 9)}
    R["rolling"], oos_all = {}, {}
    for name, months in plan.items():
        oos, tab = rolling(p, name, list(months))
        oos_all[name] = oos
        R["rolling"][name] = summarize(oos, tab, boot=name in ("holders_1m", "breakouts_3m", "breakouts_1m"))
        R["rolling"][name]["bands"] = bands(oos, name.split("_")[0])
        log("summarized", name)
    for name in ("holders_1m", "breakouts_3m"):
        R["rolling"][name]["by_category"] = by_category(oos_all[name], cats)
    R["drop_oct2025"] = {}
    for name, months in (("breakouts_3m", range(6, 9)), ("holders_1m", range(4, 11))):
        oos, _ = rolling(p, name, list(months), variants=False, drop_oct=True)
        base_oos = oos_all[name][oos_all[name]["month"].isin([MONTHS[i] for i in months])]
        R["drop_oct2025"][name] = {"auc_gbm_with_oct": roc_auc_score(base_oos["y"], base_oos["s_gbm"]),
                                   "auc_gbm_without_oct": roc_auc_score(oos["y"], oos["s_gbm"])}
    log("drop oct done")
    R["loco_breakouts_3m"] = loco(p, cats)
    log("loco done")
    R["out_of_range_probe"] = out_of_range_probe(p)
    R["deep_list_shift"] = deep_shift(pdeep)
    R["entrant_coverage"] = entrant_coverage(p)
    R["commission_bands_breakouts_3m"] = commission_bands(p)
    R["runtime_s"] = time.time() - T0
    OUTFILE.write_text(json.dumps(r3(R), indent=1), encoding="utf-8")
    log("saved", OUTFILE)


if __name__ == "__main__":
    main()
