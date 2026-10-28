"""Standard evaluation harness for the market engine (Market Engine 2.0 Phase B, 2026-10-28).

Reads a point-in-time snapshot from scripts/market_data.py and evaluates four tasks with rolling origins:
for each test month t the model trains only on rows whose label had matured by t (row month + horizon <= t, i.e. an
embargo equal to the horizon), expanding window, at least 2 training months. The last fully labelled month of each
task is the frozen final holdout: `select` never touches it; `final` evaluates it once, applies the decision rule,
marks the holdout spent in the research_runs registry (research/kalodata/kalodata.db) and saves the adopted rankers
to research/kalodata/model_v2_<date>/ (refuses an existing folder).

Candidate: HistGradientBoosting on the cleaned point-in-time features. Baselines, always alongside: random, distance
to the category's 500th-place sales (floor ratio), rank, momentum (our month-on-month growth), Kalodata growth, sales,
persistence (months already listed), logistic regression on the same features.
Metrics per month: ROC-AUC, PR-AUC, precision / recall / lift at 10, 20, 50 (top K across all categories), hit rate of
each category's top 3 / 10 / 20 / 50 (pooled), Brier and reliability for probability models; month-block bootstrap
95% CIs (2,000 draws). Calibration (isotonic and Platt, fitted on a held-out month: a model trained on rows matured by
month t-h predicts month t-h) is kept only if it lowers the next-month Brier score.

Decision rule (roadmap Phase B item 6): the model is adopted for a task only if it beats the best baseline on the
category top-10 hit rate or on lift@20 overall, with a month-block bootstrap CI of the monthly difference that excludes
zero, and does not lose on the holdout month. Otherwise the adopted ranker is the best transparent baseline (chosen
on the selection months).

Usage (run from the Hub folder; ~5-10 minutes):
  python -I scripts/market_eval.py select [--tasks all] [--snapshot NAME]    selection months only, registered
  python -I scripts/market_eval.py final  [--tasks all] [--snapshot NAME]    holdout once, decision, model_v2 folder
"""
import argparse
import datetime as dt
import json
import sqlite3
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
import market_data as md  # noqa: E402

HUB = md.HUB
DB = md.DB
EVALS = HUB / "research" / "kalodata" / "evals"
MODELS_ROOT = HUB / "research" / "kalodata"
SEED = 20261028
HGB = dict(max_depth=6, learning_rate=0.05, max_iter=400, min_samples_leaf=50, l2_regularization=1.0, random_state=7)
MIN_TRAIN_MONTHS = 2
N_BOOT = 2000
K_ALL = (10, 20, 50)
K_CAT = (3, 10, 20, 50)
CANDIDATE = "hgb"
BASELINES = ["random", "floor_ratio", "rank", "momentum", "kalodata_growth", "sales", "persistence", "logistic"]
TRANSPARENT = ["floor_ratio", "rank", "momentum", "kalodata_growth", "sales", "persistence"]
PRIMARY = ("p_cat@10", "lift@20")

TASKS = {
    "holders_1m": {"population": ["top500"], "h": 1, "y": "y_holders_1m",
                   "question": "Will a product in its category's top 500 this month still be in a top 500 next month "
                               "and sell at least as much?"},
    "holders_3m": {"population": ["top500"], "h": 3, "y": "y_holders_3m",
                   "question": "Will a product in its category's top 500 this month be in a top 500 three months on?"},
    "breakout_1m": {"population": ["risers"], "h": 1, "y": "y_breakout_1m",
                    "question": "Will a product on its category's riser list (positions 1-200) and outside the top 500 "
                                "enter a top 500 next month?"},
    "breakout_3m": {"population": ["risers"], "h": 3, "y": "y_breakout_3m",
                    "question": "Will a product on its category's riser list (positions 1-200) and outside the top 500 "
                                "enter a top 500 within three months?"},
}
RANKERS = {  # transparent baselines: higher score = ranked first; fill = value for missing inputs
    "floor_ratio": {"feature": "log_vs_floor", "sign": 1, "fill": -9.0,
                    "label": "sales as a share of the category's 500th-place sales"},
    "momentum": {"feature": "mom_growth", "sign": 1, "fill": 0.0,
                 "label": "our month-on-month sales growth (0 when not listed last month)"},
    "kalodata_growth": {"feature": "kalo_growth_slog", "sign": 1, "fill": 0.0, "label": "Kalodata's growth field"},
    "sales": {"feature": "log_sales", "sign": 1, "fill": 0.0, "label": "monthly sales"},
    "persistence": {"feature": "months_seen_before", "sign": 1, "fill": 0.0, "label": "months already on our lists"},
}
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:5.0f}s]", *a, flush=True)


def task_definition(name):
    t = TASKS[name]
    pop = {"top500": "products in a category top 500 at month t",
           "risers": "products on a category riser list (Kalodata growth sort, positions 1-200) and not in any top "
                     "500 at month t; deep riser positions 201-1,000 are a different population and never scored "
                     "here"}[t["population"][0]]
    return {"task": name, "question": t["question"], "eligible_population": pop,
            "observation_date": "end of calendar month t (Kalodata month data arrive early in t+1)",
            "horizon_months": t["h"], "outcome": md.LABEL_DEFS[t["y"]], "absence": md.LABEL_DEFS["absence"],
            "excluded": "Oct 2025 rows; Virtual Products; rows whose label months are not all present"}


# ---------------------------------------------------------------- data
def task_frame(panel, name):
    t = TASKS[name]
    d = panel[panel["population"].isin(t["population"]) & panel[t["y"]].notna()].copy()
    d["y"] = d[t["y"]].astype(int)
    d["mo"] = d["mo"].astype(int)
    return d


def origins(d, h, min_train=MIN_TRAIN_MONTHS):
    """Test months with at least `min_train` matured training months; the last is the frozen holdout."""
    months = sorted(d["mo"].unique())
    out = [t for t in months if len([m for m in months if m <= t - h]) >= min_train]
    return out[:-1], (out[-1] if out else None)


def split(d, t, h):
    """Rolling origin with embargo = horizon: train rows whose label matured by t; test rows of month t."""
    tr = d[d["mo"] <= t - h]
    assert tr.empty or tr["mo"].max() + h <= t
    return tr, d[d["mo"] == t]


# ---------------------------------------------------------------- scores
def filled(X, ref):
    return X.fillna(ref.median()).fillna(0)


def fit_hgb(tr):
    return HistGradientBoostingClassifier(**HGB).fit(tr[md.FEATURES], tr["y"])


def fit_logistic(tr):
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))
    m.fit(filled(tr[md.FEATURES], tr[md.FEATURES]), tr["y"])
    return m


def ranker_score(df, name, kind):
    if name == "rank":
        col = "rank_pos" if kind == "holders" else "riser_pos"
        return -df[col].fillna(10_000).values
    r = RANKERS[name]
    return r["sign"] * df[r["feature"]].fillna(r["fill"]).values


def platt(p_cal, y_cal):
    z = np.log(np.clip(p_cal, 1e-6, 1 - 1e-6) / (1 - np.clip(p_cal, 1e-6, 1 - 1e-6)))
    lr = LogisticRegression(C=1e6, max_iter=1000).fit(z.reshape(-1, 1), y_cal)
    return lambda p: lr.predict_proba(np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
                                      .reshape(-1, 1))[:, 1]


def score_origin(d, t, h, kind, rng):
    tr, te = split(d, t, h)
    sc, prob = {}, {}
    m = fit_hgb(tr)
    sc["hgb"] = prob["hgb"] = m.predict_proba(te[md.FEATURES])[:, 1]
    lg = fit_logistic(tr)
    sc["logistic"] = prob["logistic"] = lg.predict_proba(filled(te[md.FEATURES], tr[md.FEATURES]))[:, 1]
    sc["random"] = rng.random(len(te))
    for b in ("floor_ratio", "rank", "momentum", "kalodata_growth", "sales", "persistence"):
        sc[b] = ranker_score(te, b, kind)
    # calibration on a held-out month: inner model trained on rows matured by m* = t-h predicts month m*
    cal = None
    ms = t - h
    inner_tr, cal_rows = d[d["mo"] <= ms - h], d[d["mo"] == ms]
    if inner_tr["mo"].nunique() >= 1 and len(cal_rows) and 0 < cal_rows["y"].sum() < len(cal_rows):
        p_cal = fit_hgb(inner_tr).predict_proba(cal_rows[md.FEATURES])[:, 1]
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(p_cal, cal_rows["y"])
        prob["hgb_isotonic"] = iso.predict(sc["hgb"])
        prob["hgb_platt"] = platt(p_cal, cal_rows["y"].values)(sc["hgb"])
        cal = md._mstr(ms)
    return tr, te, sc, prob, cal


# ---------------------------------------------------------------- metrics
def order_index(s, tb):
    return np.lexsort((tb, -np.asarray(s, dtype=float)))


def month_metrics(te, s, tb, p=None):
    y = te["y"].values
    n, pos = len(y), int(y.sum())
    r = {"n": n, "pos": pos, "base": pos / n if n else np.nan}
    if 0 < pos < n:
        r["auc"] = roc_auc_score(y, s)
        r["ap"] = average_precision_score(y, s)
    o = order_index(s, tb)
    for k in K_ALL:
        hits = int(y[o[:k]].sum())
        r[f"p@{k}"] = hits / min(k, n)
        r[f"recall@{k}"] = hits / pos if pos else np.nan
        r[f"lift@{k}"] = r[f"p@{k}"] / r["base"] if r["base"] else np.nan
    cat_rank = cat_ranks(te["cat"].values, s, tb)
    for k in K_CAT:
        sel = cat_rank <= k
        r[f"hits_cat@{k}"], r[f"picks_cat@{k}"] = int(y[sel].sum()), int(sel.sum())
        r[f"p_cat@{k}"] = r[f"hits_cat@{k}"] / r[f"picks_cat@{k}"] if sel.any() else np.nan
    if p is not None:
        r["brier"] = brier_score_loss(y, p)
        r["brier_climatology"] = r["base"] * (1 - r["base"])
    return r


def cat_ranks(cats, s, tb):
    """1-based rank of each row within its category (ties broken by tb)."""
    o = np.lexsort((tb, -np.asarray(s, dtype=float), cats))
    rank = np.empty(len(s), dtype=int)
    cs = cats[o]
    start = np.r_[0, np.flatnonzero(cs[1:] != cs[:-1]) + 1]
    seg = np.zeros(len(s), dtype=int)
    seg[start] = 1
    grp_start = np.maximum.accumulate(np.where(seg == 1, np.arange(len(s)), 0))
    rank[o] = np.arange(len(s)) - grp_start + 1
    return rank


def boot_mean(vals, n=N_BOOT, seed=SEED):
    v = np.asarray([x for x in vals if x is not None and not np.isnan(x)], dtype=float)
    if not len(v):
        return [None, None, None]
    rng = np.random.default_rng(seed)
    draws = v[rng.integers(0, len(v), (n, len(v)))].mean(axis=1)
    return [float(v.mean()), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]


def reliability(y, p, bins=(0, .02, .05, .1, .2, .3, .5, .7, 1.0001)):
    t = pd.DataFrame({"y": y, "p": p, "b": pd.cut(p, bins=bins, right=False)})
    g = t.groupby("b", observed=True).agg(n=("y", "size"), mean_pred=("p", "mean"), observed=("y", "mean"))
    return [{"bin": str(i), "n": int(r.n), "mean_pred": float(r.mean_pred), "observed": float(r.observed)}
            for i, r in g.iterrows()]


def summarize_months(by_month, months, models, metrics):
    return {m: {k: boot_mean([by_month[mo][m].get(k, np.nan) for mo in months]) for k in metrics} for m in models}


def per_category(oos, models, names):
    out = {}
    for m in models:
        rows = {}
        for c, g in oos.groupby("cat"):
            r = {"name": names.get(c, c), "n": int(len(g)), "pos": int(g["y"].sum()), "base": float(g["y"].mean())}
            for k in K_CAT:
                sel = g[f"rk_{m}"] <= k
                r[f"p_cat@{k}"] = float(g.loc[sel, "y"].mean()) if sel.any() else None
                r[f"picks@{k}"] = int(sel.sum())
            if 5 <= g["y"].sum() < len(g):
                r["auc"] = float(roc_auc_score(g["y"], g[f"s_{m}"]))
            rows[c] = r
        out[m] = rows
    return out


# ---------------------------------------------------------------- decision rule
def beats(by_month, selection, holdout, candidate, pool, n_boot=N_BOOT, seed=SEED):
    """Does `candidate` beat the best of `pool` (best chosen on the selection months; ties go to the earlier pool
    entry) on either primary metric, with a month-block bootstrap CI of the monthly difference above zero over all
    evaluated months and no loss on the holdout month?"""
    def sel_mean(model, metric):
        v = [by_month[m][model].get(metric, np.nan) for m in selection]
        return float(np.nanmean(v)) if len(v) else np.nan

    months = list(selection) + ([holdout] if holdout is not None else [])
    tests = {}
    for metric in PRIMARY:
        best = max(pool, key=lambda b: (np.nan_to_num(sel_mean(b, metric), nan=-np.inf), -pool.index(b)))
        diffs = [by_month[m][candidate].get(metric, np.nan) - by_month[m][best].get(metric, np.nan) for m in months]
        ci = boot_mean(diffs, n_boot, seed)
        hold = diffs[-1] if holdout is not None else None
        tests[metric] = {"best_baseline": best, "candidate_selection_mean": sel_mean(candidate, metric),
                         "baseline_selection_mean": sel_mean(best, metric), "monthly_diff": diffs,
                         "diff_mean_ci": ci, "holdout_diff": hold,
                         "passed": bool(ci[1] is not None and ci[1] > 0 and hold is not None and hold >= 0
                                        if holdout is not None else ci[1] is not None and ci[1] > 0)}
    return tests, sel_mean


def decide(by_month, selection, holdout, candidate=CANDIDATE, baselines=BASELINES, transparent=TRANSPARENT,
           middle="logistic", n_boot=N_BOOT, seed=SEED):
    """Owner's rule: the model (HGB) is adopted only if it beats the best baseline (logistic included) on the category
    top-10 hit rate or lift@20 overall, with a month-block bootstrap CI of the monthly difference above zero, and does
    not lose on the holdout month. Otherwise the simplest ranker that is not beaten is adopted: logistic regression
    (a linear, inspectable ranker) only if it passes the same test against the best single-rule baseline; else the best
    single-rule baseline by selection-month category top-10 hit rate (ties go to the earlier rule in the list)."""
    model_tests, sel_mean = beats(by_month, selection, holdout, candidate, list(baselines), n_boot, seed)
    rules = [b for b in transparent]
    best_rule = max(rules, key=lambda b: (np.nan_to_num(sel_mean(b, "p_cat@10"), nan=-np.inf), -rules.index(b)))
    mid_tests = None
    if middle:
        mid_tests, _ = beats(by_month, selection, holdout, middle, ["random"] + rules, n_boot, seed)
    if any(t["passed"] for t in model_tests.values()):
        adopted, kind = candidate, "model"
        why = f"{candidate} beats the best baseline with a CI above zero on " + " and ".join(
            k for k, t in model_tests.items() if t["passed"])
    elif mid_tests and any(t["passed"] for t in mid_tests.values()):
        adopted, kind = middle, "model"
        why = (f"{candidate} did not beat the best baseline with a CI excluding zero (and no holdout loss); {middle} "
               "beats the best single-rule baseline with a CI above zero on "
               + " and ".join(k for k, t in mid_tests.items() if t["passed"]))
    else:
        adopted, kind = best_rule, "baseline"
        why = (f"{candidate} did not beat the best baseline with a CI excluding zero (and no holdout loss) on either "
               f"primary metric" + (f", nor did {middle} beat the best single rule" if middle else "")
               + f"; adopted the best transparent baseline '{best_rule}' (selection-month category top-10 hit rate "
               f"{sel_mean(best_rule, 'p_cat@10'):.3f})")
    months = list(selection) + ([holdout] if holdout is not None else [])
    return {"adopted": adopted, "adopted_type": kind, "tests": model_tests, "tests_middle": mid_tests,
            "best_rule": best_rule, "reason": why, "months": [str(m) for m in months], "final": holdout is not None}


# ---------------------------------------------------------------- registry
REGISTRY_SQL = """CREATE TABLE IF NOT EXISTS research_runs (
    run_id TEXT PRIMARY KEY, created_at TEXT, question TEXT, task TEXT, data_snapshot TEXT, data_cutoff TEXT,
    features TEXT, params TEXT, seed INTEGER, code_commit TEXT, eval_design TEXT, results_json TEXT, decision TEXT,
    holdout_used INTEGER)"""


def registry(db=None):
    con = sqlite3.connect(Path(db or DB))
    con.execute(REGISTRY_SQL)
    return con


def holdout_spent(con, task, holdout_month=None):
    q = "SELECT run_id, eval_design FROM research_runs WHERE task = ? AND holdout_used = 1"
    for run_id, design in con.execute(q, (task,)).fetchall():
        if holdout_month is None or json.loads(design or "{}").get("holdout_month") == holdout_month:
            return run_id
    return None


def register(con, row):
    cols = ["run_id", "created_at", "question", "task", "data_snapshot", "data_cutoff", "features", "params", "seed",
            "code_commit", "eval_design", "results_json", "decision", "holdout_used"]
    con.execute(f"INSERT INTO research_runs ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
                [row.get(c) for c in cols])
    con.commit()


# ---------------------------------------------------------------- one task
def evaluate(panel, name, months, names):
    kind = name.split("_")[0]
    h = TASKS[name]["h"]
    d = task_frame(panel, name)
    rng = np.random.default_rng(SEED)
    by_month, frames, cal_months = {}, [], {}
    for t in months:
        tr, te, sc, prob, cal = score_origin(d, t, h, kind, rng)
        tb = rng.random(len(te))
        ms = md._mstr(t)
        by_month[ms] = {k: month_metrics(te, s, tb, prob.get(k)) for k, s in sc.items()}
        for k in ("hgb_isotonic", "hgb_platt"):
            if k in prob:
                by_month[ms][k] = {"brier": brier_score_loss(te["y"], prob[k]), "n": len(te)}
        cal_months[ms] = cal
        keep = te[["product_id", "cat", "month", "y", "log_vs_floor", "riser_pos", "rank_pos"]].copy()
        keep["n_train"], keep["train_months"] = len(tr), tr["mo"].nunique()
        for k, s in sc.items():
            keep[f"s_{k}"] = s
            keep[f"rk_{k}"] = cat_ranks(te["cat"].values, s, tb)
        for k, p in prob.items():
            keep[f"p_{k}"] = p
        frames.append(keep)
        log(name, ms, f"train {len(tr):,} ({tr['mo'].nunique()} months) test {len(te):,} pos {int(te['y'].sum())}",
            "| p_cat@10 hgb", round(by_month[ms]["hgb"]["p_cat@10"], 3), "floor",
            round(by_month[ms]["floor_ratio"]["p_cat@10"], 3), "| AUC hgb", round(by_month[ms]["hgb"].get("auc", 0), 3))
    oos = pd.concat(frames, ignore_index=True)
    return d, by_month, oos, cal_months


def calibration_summary(by_month, oos, months, cal_months):
    usable = [m for m in months if cal_months.get(m)]
    res = {"scheme": "isotonic and Platt fitted on a held-out month: an inner HGB trained on rows matured by t-h "
                     "predicts month t-h; the calibrator is applied to the outer model's month-t predictions",
           "months_evaluated": usable, "calibration_month_by_test_month": {m: cal_months.get(m) for m in months}}
    if usable:
        for k in ("hgb", "hgb_isotonic", "hgb_platt"):
            res[f"brier_{k}"] = boot_mean([by_month[m][k]["brier"] for m in usable])
        res["brier_climatology"] = float(np.mean([by_month[m]["hgb"]["brier_climatology"] for m in usable]))
        raw = res["brier_hgb"][0]
        best = min(("hgb_isotonic", "hgb_platt"), key=lambda k: res[f"brier_{k}"][0])
        res["kept"] = best.replace("hgb_", "") if res[f"brier_{best}"][0] < raw else None
        sub = oos[oos["month"].isin(usable)]
        for k in ("hgb", "hgb_isotonic", "hgb_platt"):
            res[f"reliability_{k}"] = reliability(sub["y"].values, sub[f"p_{k}"].values)
    else:
        res["kept"] = None
    res["reliability_hgb_all_months"] = reliability(oos["y"].values, oos["p_hgb"].values)
    res["reliability_logistic_all_months"] = reliability(oos["y"].values, oos["p_logistic"].values)
    return res


def run_task(panel, name, names, final):
    d = task_frame(panel, name)
    sel, hold = origins(d, TASKS[name]["h"])
    months = sel + ([hold] if final else [])
    d, by_month, oos, cal_months = evaluate(panel, name, months, names)
    sel_s, hold_s = [md._mstr(m) for m in sel], md._mstr(hold)
    models = [CANDIDATE] + BASELINES
    metrics = ["auc", "ap", "p@10", "p@20", "p@50", "recall@10", "recall@20", "recall@50", "lift@10", "lift@20",
               "lift@50", "p_cat@3", "p_cat@10", "p_cat@20", "p_cat@50", "brier", "base"]
    res = {"definition": task_definition(name), "selection_months": sel_s, "holdout_month": hold_s,
           "holdout_evaluated": final, "by_month": by_month,
           "summary_selection": summarize_months(by_month, sel_s, models, metrics)}
    dec = decide(by_month, sel_s, hold_s if final else None)
    res["decision"] = dec
    if final:
        res["summary_all_months"] = summarize_months(by_month, sel_s + [hold_s], models, metrics)
        res["holdout"] = {m: by_month[hold_s][m] for m in models}
        hold_rows = oos[oos["month"] == hold_s]
        res["holdout_category_block_ci"] = cat_block_ci(hold_rows, CANDIDATE,
                                                        [dec["tests"][k]["best_baseline"] for k in PRIMARY])
    show = sorted({CANDIDATE, "logistic", dec["adopted"], dec["best_rule"], "floor_ratio"}
                  | {dec["tests"][k]["best_baseline"] for k in PRIMARY})
    res["per_category"] = per_category(oos, show, names)
    res["calibration"] = calibration_summary(by_month, oos, sel_s, cal_months)
    res["n_rows_evaluated"], res["n_pos_evaluated"] = int(len(oos)), int(oos["y"].sum())
    return res, d, oos


def cat_block_ci(rows, cand, bases, n=N_BOOT, seed=SEED):
    """Holdout month only: bootstrap over categories of the category top-10 hit-rate difference."""
    rng = np.random.default_rng(seed)
    cats = rows["cat"].unique()
    agg = {m: rows.assign(h=(rows[f"rk_{m}"] <= 10) & (rows["y"] == 1), p=rows[f"rk_{m}"] <= 10)
           .groupby("cat")[["h", "p"]].sum().reindex(cats) for m in {cand, *bases}}
    out = {}
    for b in set(bases):
        diffs = []
        for _ in range(n):
            s = cats[rng.integers(0, len(cats), len(cats))]
            a, c = agg[cand].loc[s].sum(), agg[b].loc[s].sum()
            diffs.append(a["h"] / a["p"] - c["h"] / c["p"])
        base_d = agg[cand]["h"].sum() / agg[cand]["p"].sum() - agg[b]["h"].sum() / agg[b]["p"].sum()
        out[f"{cand}_minus_{b}_p_cat@10"] = [float(base_d), float(np.percentile(diffs, 2.5)),
                                             float(np.percentile(diffs, 97.5))]
    return out


# ---------------------------------------------------------------- adopted rankers
def ranker_spec(name, kind):
    if name == "rank":
        col = "rank_pos" if kind == "holders" else "riser_pos"
        return {"type": "baseline", "name": "rank", "feature": col, "sign": -1, "fill": 10_000,
                "label": "sales rank" if kind == "holders" else "riser-list position"}
    if name in RANKERS:
        return dict(RANKERS[name], type="baseline", name=name)
    return {"type": "model", "name": name}


def score_with(spec, df, model_dir=None):
    """Score rows with an adopted ranker spec from a model_v2 manifest (higher = ranked first)."""
    if spec["type"] == "baseline":
        return spec["sign"] * df[spec["feature"]].fillna(spec["fill"]).values
    bundle = joblib.load(Path(model_dir) / spec["file"])
    X = df[bundle["features"]]
    if bundle.get("fill") is not None:
        X = X.fillna(pd.Series(bundle["fill"])).fillna(0)
    return bundle["model"].predict_proba(X)[:, 1]


def latest_model_dir():
    dirs = sorted(d for d in MODELS_ROOT.glob("model_v2_*") if (d / "manifest.json").exists())
    if not dirs:
        raise SystemExit("No model_v2_<date> folder yet: run python -I scripts/market_eval.py final")
    return dirs[-1]


def hit_rates(oos, adopted, res, months):
    sub = oos[oos["month"].isin(months)]
    out = {"months": months, "rows": int(len(sub)), "positives": int(sub["y"].sum()), "base_rate": float(sub["y"].mean())}
    for k in K_CAT:
        sel = sub[f"rk_{adopted}"] <= k
        out[f"p_cat@{k}"] = {"hit_rate": float(sub.loc[sel, "y"].mean()), "picks": int(sel.sum()),
                             "hits": int(sub.loc[sel, "y"].sum())}
    out["by_category_p_cat@10"] = {c: {"name": r["name"], "hit_rate": r["p_cat@10"], "picks": r["picks@10"]}
                                   for c, r in res["per_category"][adopted].items()}
    out["by_category_p_cat@3"] = {c: {"hit_rate": r["p_cat@3"], "picks": r["picks@3"]}
                                  for c, r in res["per_category"][adopted].items()}
    for k in K_ALL:
        v = [res["by_month"][m][adopted][f"p@{k}"] for m in months]
        out[f"p@{k}_month_mean"] = float(np.mean(v))
    return out


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description="Market engine evaluation harness")
    ap.add_argument("mode", choices=["select", "final"])
    ap.add_argument("--tasks", default="all")
    ap.add_argument("--snapshot", help="snapshot folder name (default: newest)")
    ap.add_argument("--db", default=str(DB), help="database holding the research_runs registry")
    ap.add_argument("--models-root", default=str(MODELS_ROOT))
    ap.add_argument("--evals-dir", default=str(EVALS))
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="model_v2_<date> folder name")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    tasks = list(TASKS) if a.tasks == "all" else a.tasks.split(",")
    final = a.mode == "final"
    model_dir = Path(a.models_root) / f"model_v2_{a.date}"
    if final and model_dir.exists():
        raise SystemExit(f"Refusing: {model_dir} already exists (model folders are never overwritten)")
    panel, _, man = md.read_snapshot(a.snapshot)
    names = man.get("categories", {})
    con = registry(a.db)
    if final:
        for name in tasks:
            d = task_frame(panel, name)
            hold = md._mstr(origins(d, TASKS[name]["h"])[1])
            spent = holdout_spent(con, name, hold)
            if spent:
                raise SystemExit(f"Refusing: the {name} holdout ({hold}) was already spent by run {spent}")
    stamp = dt.datetime.now()
    out_dir = Path(a.evals_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{stamp:%Y%m%d-%H%M%S}_{a.mode}.json"
    commit = md.git_commit()
    design_base = {"design": "rolling origin, expanding window, embargo = horizon (train rows with month + h <= test "
                             "month)", "min_train_months": MIN_TRAIN_MONTHS, "bootstrap": f"month-block, {N_BOOT} draws",
                   "primary_metrics": list(PRIMARY), "k_overall": list(K_ALL), "k_per_category": list(K_CAT),
                   "candidate": CANDIDATE, "baselines": BASELINES, "transparent": TRANSPARENT,
                   "decision_rule": decide.__doc__.strip()}
    all_res, manifest_tasks, saved = {}, {}, {}
    for name in tasks:
        res, d, oos = run_task(panel, name, names, final)
        all_res[name] = res
        dec = res["decision"]
        run_id = f"{stamp:%Y%m%d-%H%M%S}-{a.mode}-{name}"
        design = dict(design_base, task=name, horizon=TASKS[name]["h"], selection_months=res["selection_months"],
                      holdout_month=res["holdout_month"], results_file=str(out_file.relative_to(HUB))
                      if out_file.is_relative_to(HUB) else str(out_file))
        summary = {"selection": {m: {k: res["summary_selection"][m][k] for k in ("auc", "p_cat@10", "lift@20",
                                                                                 "p@20", "brier")}
                                 for m in res["summary_selection"]},
                   "decision_tests": dec["tests"], "decision_tests_logistic_vs_rules": dec["tests_middle"],
                   "best_rule": dec["best_rule"], "calibration_kept": res["calibration"]["kept"]}
        if final:
            summary["holdout"] = {m: {k: res["holdout"][m].get(k) for k in ("auc", "p_cat@10", "lift@20", "p@20",
                                                                            "brier", "base")}
                                  for m in res["holdout"]}
        decision_txt = (("ADOPT " if final else "PROVISIONAL (holdout not used): ") + f"{dec['adopted']} "
                        f"({dec['adopted_type']}). {dec['reason']}")
        register(con, {"run_id": run_id, "created_at": stamp.isoformat(timespec="seconds"),
                       "question": TASKS[name]["question"], "task": name, "data_snapshot": man["name"],
                       "data_cutoff": man["data_cutoff"], "features": json.dumps(md.FEATURES),
                       "params": json.dumps({"hgb": HGB, "logistic": "StandardScaler + LogisticRegression(max_iter="
                                                                     "3000), median fill"}),
                       "seed": SEED, "code_commit": commit, "eval_design": json.dumps(design),
                       "results_json": json.dumps(r3(summary)), "decision": decision_txt,
                       "holdout_used": int(final)})
        log("registered", run_id, "->", decision_txt[:160])
        if final:
            kind = name.split("_")[0]
            spec = ranker_spec(dec["adopted"], kind)
            months_all = res["selection_months"] + [res["holdout_month"]]
            if spec["type"] == "model":
                saved[name] = (spec, d, res, oos)
            manifest_tasks[name] = {"definition": res["definition"], "registry_run_id": run_id, "ranker": spec,
                                    "decision": dec["reason"], "hit_rates_all_evaluated_months":
                                        hit_rates(oos, dec["adopted"], res, months_all),
                                    "hit_rates_holdout_month": hit_rates(oos, dec["adopted"], res,
                                                                         [res["holdout_month"]]),
                                    "calibration_kept": res["calibration"]["kept"]}
    payload = {"created_at": stamp.isoformat(timespec="seconds"), "mode": a.mode, "snapshot": man["name"],
               "data_cutoff": man["data_cutoff"], "code_commit": commit, "features": md.FEATURES,
               "feature_definitions": md.FEATURE_DEFS, "eval_design": design_base, "tasks": all_res}
    out_file.write_text(json.dumps(r3(payload), indent=1, ensure_ascii=False), encoding="utf-8")
    log("results", out_file)
    if final:
        model_dir.mkdir(parents=True)  # raises if it appeared meanwhile
        for name, (spec, d, res, oos) in saved.items():
            # trained on every row whose label has matured in the snapshot
            if spec["name"] == "hgb":
                m, fill, params = fit_hgb(d), None, HGB
            else:
                m, fill, params = fit_logistic(d), d[md.FEATURES].median().to_dict(), "StandardScaler + LogisticRegression"
            spec["file"] = f"{name}_{spec['name']}.joblib"
            spec["trained_rows"], spec["trained_months"] = int(len(d)), sorted(d["month"].unique().tolist())
            spec["note"] = "score is a ranking score; it is not presented as a probability"
            joblib.dump({"model": m, "features": md.FEATURES, "fill": fill, "params": params,
                         "snapshot": man["name"]}, model_dir / spec["file"])
            manifest_tasks[name]["ranker"] = spec
        (model_dir / "manifest.json").write_text(json.dumps(r3({
            "created_at": stamp.isoformat(timespec="seconds"), "snapshot": man["name"],
            "data_cutoff": man["data_cutoff"], "code_commit": commit, "results_file": str(out_file.relative_to(HUB))
            if out_file.is_relative_to(HUB) else str(out_file),
            "note": "Rankers, not probabilities. Hit rates are historical (rolling-origin, embargoed) and apply only "
                    "to the population in each task definition.", "features": md.FEATURES, "tasks": manifest_tasks}),
            indent=1, ensure_ascii=False), encoding="utf-8")
        log("saved", model_dir)
    con.close()
    return payload


def r3(x):
    if isinstance(x, dict):
        return {str(k): r3(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r3(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if np.isnan(x) else round(float(x), 4)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


if __name__ == "__main__":
    main()
