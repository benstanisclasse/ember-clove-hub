"""Product model v1 on the core Kalodata dataset (research/kalodata/CORE_DATASET_PLAN_2026-10-25.md).

Panel: one row per product per month (Oct 2025 - Sep 2026, 28 US categories) from the core top-500 (by sales) and
top-200 riser (by growth) lists. Two questions, each 1 and 3 months ahead:
  holders   products in their category's top 500: still in the top 500 and selling at least as much next month (h=1);
            still in the top 500 three months later (h=3)
  breakouts risers outside the top 500: in the top 500 next month (h=1) / within three months (h=3)
Tested forward in time: trained on earlier months, scored on later months it never saw.
Also: whether creator and video counts (1,003-row detail sample) add signal; scores for September 2026 products.
Run: python -I scripts/train_product_model.py --out research/kalodata/model_v1_rerun_<date>
Pinned (Market Engine B0, 2026-10-28): riser rows are selected by pull kind 'risers' (pages 1-2, positions 1-200), so the
deep Sep 2026 pages (kind 'risers_deep') can't change what v1 trains on, and outputs go to a new folder: the script
refuses to write into an existing one (model_v1_2026-10-25 is never overwritten). Superseded by scripts/market_eval.py.
"""
import json
import sqlite3
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HUB = Path(__file__).resolve().parent.parent
DB = HUB / "research" / "kalodata" / "kalodata.db"
OUT = HUB / "research" / "kalodata" / "model_v1_2026-10-25"  # v1 outputs: read-only reference, never written
MONTHS = [f"{y}-{m:02d}" for y, m in [(2025, 10), (2025, 11), (2025, 12)] + [(2026, i) for i in range(1, 10)]]
MI = {m: i for i, m in enumerate(MONTHS)}
NUM = ["revenue", "sales_volumn", "unit_price", "revenue_growth_rate", "commission_rate", "live_revenue",
       "video_revenue", "showcase_revenue", "sku_count"]
FEATURES = ["log_sales", "log_units", "unit_price", "growth_slog", "commission_rate", "video_share", "live_share",
            "shop_share", "age_days", "log_sku", "rank_pos", "in_risers", "riser_pos", "seller_n_top500",
            "seller_share_cat", "cat_growth", "months_seen_before", "prev_ratio", "was_top500_prev", "price_vs_cat"]
HGB = dict(max_depth=6, learning_rate=0.05, max_iter=400, min_samples_leaf=50, l2_regularization=1.0, random_state=7)


def load():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    df = pd.read_sql("SELECT u.name, p.position, p.product_id, p.product_name, p.launch_date, p.seller_id, "
                     + ", ".join(f"p.{c}" for c in NUM) +
                     " FROM products p JOIN pulls u ON p.pull_id = u.pull_id "
                     "WHERE u.name LIKE 'core_products_%' OR (u.name LIKE 'core_risers_%' AND u.kind = 'risers')", con)
    cats = dict(con.execute("SELECT c.category_id, c.category_name FROM categories c JOIN pulls u ON c.pull_id = "
                            "u.pull_id WHERE u.name LIKE 'core_categories_l1_last365Day%'").fetchall())
    det = pd.read_sql("SELECT u.name, d.product_id, d.creator_number, d.video_number, d.live_number, d.min_price, "
                      "d.max_price FROM product_details d JOIN pulls u ON d.pull_id = u.pull_id "
                      "WHERE u.name LIKE 'core_detail_%'", con)
    con.close()
    parts = df["name"].str.split("_")
    df["list"], df["month"], df["cat"] = parts.str[1], parts.str[2], parts.str[3]
    df["pos"] = (parts.str[4].str[1:].astype(int) - 1) * 100 + df["position"]
    df[NUM] = df[NUM].apply(pd.to_numeric, errors="coerce")
    det["month"] = det["name"].str.split("_").str[2]
    return df, cats, det


def build(df):
    top = df[df["list"] == "products"].drop_duplicates(["product_id", "month"])
    ris = df[df["list"] == "risers"].drop_duplicates(["product_id", "month"])
    p = pd.concat([top, ris[~ris.set_index(["product_id", "month"]).index.isin(top.set_index(["product_id", "month"]).index)]])
    p = p.drop_duplicates(["product_id", "month"]).copy()
    key = lambda d: set(zip(d["product_id"], d["month"]))  # noqa: E731
    top_k, ris_pos = key(top), dict(zip(zip(ris["product_id"], ris["month"]), ris["pos"]))
    top_pos = dict(zip(zip(top["product_id"], top["month"]), top["pos"]))
    sales = dict(zip(zip(p["product_id"], p["month"]), p["revenue"]))
    p["mi"] = p["month"].map(MI)
    p["in_top500"] = [(a, b) in top_k for a, b in zip(p["product_id"], p["month"])]
    p["rank_pos"] = [top_pos.get((a, b), np.nan) for a, b in zip(p["product_id"], p["month"])]
    p["in_risers"] = [(a, b) in ris_pos for a, b in zip(p["product_id"], p["month"])]
    p["riser_pos"] = [ris_pos.get((a, b), np.nan) for a, b in zip(p["product_id"], p["month"])]

    def at(offset, what):
        out = []
        for a, i in zip(p["product_id"], p["mi"]):
            j = i + offset
            if j < 0 or j >= len(MONTHS):
                out.append(np.nan)
                continue
            k = (a, MONTHS[j])
            out.append(sales.get(k, np.nan) if what == "sales" else float(k in top_k))
        return np.array(out)

    p["sales_next"], p["top_next"], p["top_3"] = at(1, "sales"), at(1, "top"), at(3, "top")
    p["top_any3"] = np.fmax(np.fmax(at(1, "top"), at(2, "top")), at(3, "top"))
    p["prev_sales"], p["was_top500_prev"] = at(-1, "sales"), at(-1, "top")
    p["prev_ratio"] = np.clip(p["revenue"] / p["prev_sales"], 0, 20)
    p["months_seen_before"] = p.groupby("product_id")["mi"].rank(method="first") - 1
    p.loc[p["mi"] == 0, "months_seen_before"] = np.nan  # nothing observed before Oct 2025
    p["log_sales"] = np.log10(p["revenue"].clip(lower=1))
    p["log_units"] = np.log10(p["sales_volumn"].clip(lower=1))
    g = p["revenue_growth_rate"].fillna(0)
    p["growth_slog"] = np.sign(g) * np.log1p(g.abs())
    for col, src in (("video_share", "video_revenue"), ("live_share", "live_revenue"), ("shop_share", "showcase_revenue")):
        p[col] = (p[src] / p["revenue"]).clip(0, 1)
    month_end = pd.to_datetime(p["month"] + "-01") + pd.offsets.MonthEnd(0)
    p["age_days"] = (month_end - pd.to_datetime(p["launch_date"], errors="coerce")).dt.days
    p["log_sku"] = np.log10(p["sku_count"].clip(lower=1))
    t = p[p["in_top500"]]
    p["seller_n_top500"] = p.set_index(["seller_id", "month", "cat"]).index.map(
        t.groupby(["seller_id", "month", "cat"]).size()).fillna(0).values
    cat_sales = t.groupby(["cat", "month"])["revenue"].sum()
    p["seller_share_cat"] = p.set_index(["seller_id", "month", "cat"]).index.map(
        t.groupby(["seller_id", "month", "cat"])["revenue"].sum()).fillna(0).values / \
        p.set_index(["cat", "month"]).index.map(cat_sales).values
    prev_cat = {(c, MONTHS[MI[m] + 1]): v for (c, m), v in cat_sales.items() if MI[m] + 1 < len(MONTHS)}
    p["cat_growth"] = p.set_index(["cat", "month"]).index.map(cat_sales).values / \
        np.array([prev_cat.get((c, m), np.nan) for c, m in zip(p["cat"], p["month"])])
    med_price = t.groupby(["cat", "month"])["unit_price"].median()
    p["price_vs_cat"] = p["unit_price"] / p.set_index(["cat", "month"]).index.map(med_price).values
    p["in_risers"] = p["in_risers"].astype(float)
    p[FEATURES] = p[FEATURES].replace([np.inf, -np.inf], np.nan)
    return p


def filled(X, ref):
    """Logistic regression can't take gaps: fill with the training median, or 0 for columns empty in training."""
    return X.fillna(ref.median()).fillna(0)


TASKS = {
    "holders_1m": ("in_top500", lambda d: ((d["top_next"] == 1) & (d["sales_next"] >= d["revenue"])).astype(int), 1),
    "holders_3m": ("in_top500", lambda d: (d["top_3"] == 1).astype(int), 3),
    "breakouts_1m": ("riser_only", lambda d: (d["top_next"] == 1).astype(int), 1),
    "breakouts_3m": ("riser_only", lambda d: (d["top_any3"] == 1).astype(int), 3),
}


def subset(p, which, h):
    d = p[p["in_top500"]] if which == "in_top500" else p[(~p["in_top500"]) & (p["in_risers"] == 1)]
    return d[d["mi"] + h <= len(MONTHS) - 1].copy()


def prec_at(y, s, frac):
    k = max(1, int(len(y) * frac))
    return float(y[np.argsort(-s)[:k]].mean())


def per_cat_top10(d, s, ycol="y"):
    d = d.assign(s=s)
    top = d.sort_values("s", ascending=False).groupby(["cat", "month"]).head(10)
    return float(top[ycol].mean())


def evaluate(p):
    results, models = {}, {}
    for name, (which, label, h) in TASKS.items():
        d = subset(p, which, h)
        d["y"] = label(d)
        last = d["mi"].max()
        test_months = [last - 2, last - 1, last]
        tr, te = d[~d["mi"].isin(test_months)], d[d["mi"].isin(test_months)]
        m = HistGradientBoostingClassifier(**HGB).fit(tr[FEATURES], tr["y"])
        s = m.predict_proba(te[FEATURES])[:, 1]
        lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(
            filled(tr[FEATURES], tr[FEATURES]), tr["y"])
        s_lr = lr.predict_proba(filled(te[FEATURES], tr[FEATURES]))[:, 1]
        y = te["y"].values
        base_growth = te["growth_slog"].fillna(0).values
        base_size = te["log_sales"].values
        r = {"rows_train": int(len(tr)), "rows_test": int(len(te)), "test_months": [MONTHS[i] for i in test_months],
             "base_rate": round(float(y.mean()), 3),
             "auc_boosted": round(roc_auc_score(y, s), 3), "auc_logistic": round(roc_auc_score(y, s_lr), 3),
             "auc_growth_only": round(roc_auc_score(y, base_growth), 3),
             "auc_sales_only": round(roc_auc_score(y, base_size), 3),
             "top10pct_hit_rate": round(prec_at(y, s, 0.10), 3),
             "top10pct_hit_rate_growth_only": round(prec_at(y, base_growth, 0.10), 3),
             "top10_per_category_month_hit_rate": round(per_cat_top10(te, s), 3)}
        by_month = {}
        for mi_ in test_months:
            mask = te["mi"].values == mi_
            if mask.sum() and len(set(y[mask])) > 1:
                by_month[MONTHS[mi_]] = round(roc_auc_score(y[mask], s[mask]), 3)
        r["auc_by_test_month"] = by_month
        pi = permutation_importance(m, te[FEATURES], y, n_repeats=5, random_state=7, scoring="roc_auc",
                                    n_jobs=-1, max_samples=min(20000, len(te)))
        r["importance"] = {f: round(float(v), 4) for f, v in
                           sorted(zip(FEATURES, pi.importances_mean), key=lambda x: -x[1])}
        results[name] = r
        models[name] = HistGradientBoostingClassifier(**HGB).fit(d[FEATURES], d["y"])  # final model: all labelled months
        print(f"{name}: train {len(tr):,} test {len(te):,} base {r['base_rate']:.0%} | AUC boosted {r['auc_boosted']} "
              f"logistic {r['auc_logistic']} growth-only {r['auc_growth_only']} sales-only {r['auc_sales_only']} | "
              f"top 10% hit {r['top10pct_hit_rate']:.0%} (growth-only {r['top10pct_hit_rate_growth_only']:.0%})",
              flush=True)
    return results, models


def breadth_test(p, det):
    d = det.merge(p, on=["product_id", "month"], how="inner")
    d = d[d["in_top500"] & (d["mi"] + 1 <= len(MONTHS) - 1)].copy()
    d["y"] = ((d["top_next"] == 1) & (d["sales_next"] >= d["revenue"])).astype(int)
    for c in ("creator_number", "video_number", "live_number"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["log_creators"] = np.log10(d["creator_number"].clip(lower=0) + 1)
    d["log_videos"] = np.log10(d["video_number"].clip(lower=0) + 1)
    d["videos_per_creator"] = d["video_number"] / d["creator_number"].replace(0, np.nan)
    d["sales_per_video"] = d["revenue"] / d["video_number"].replace(0, np.nan)
    extra = ["log_creators", "log_videos", "videos_per_creator", "sales_per_video"]
    cv = StratifiedKFold(5, shuffle=True, random_state=7)
    small = dict(max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=20, random_state=7)
    out = {"rows": int(len(d)), "base_rate": round(float(d["y"].mean()), 3)}
    for label, feats in (("without_breadth", FEATURES), ("with_breadth", FEATURES + extra)):
        s = cross_val_predict(HistGradientBoostingClassifier(**small), d[feats], d["y"], cv=cv, method="predict_proba")[:, 1]
        out[f"auc_{label}"] = round(roc_auc_score(d["y"], s), 3)
    for f in extra:
        out[f"auc_{f}_alone"] = round(roc_auc_score(d["y"], d[f].fillna(d[f].median())), 3)
    print(f"breadth test ({out['rows']} rows): AUC without {out['auc_without_breadth']} with {out['auc_with_breadth']}",
          flush=True)
    return out


def profile(p):
    d = subset(p, "in_top500", 1)
    d["y"] = TASKS["holders_1m"][1](d)
    tabs = {}
    for col, bins, labels in (
            ("revenue_growth_rate", [-101, -20, 0, 25, 75, 1e12], ["< -20%", "-20-0%", "0-25%", "25-75%", "> 75%"]),
            ("unit_price", [0, 15, 25, 40, 60, 1e9], ["< $15", "$15-25", "$25-40", "$40-60", "> $60"]),
            ("age_days", [-1, 60, 180, 365, 1e6], ["< 2 mo", "2-6 mo", "6-12 mo", "> 1 yr"]),
            ("video_share", [-0.01, 0.5, 0.8, 0.95, 1.01], ["< 50%", "50-80%", "80-95%", "> 95%"]),
            ("commission_rate", [-1, 5, 10, 15, 100], ["< 5%", "5-10%", "10-15%", "> 15%"]),
            ("prev_ratio", [0, 0.8, 1.0, 1.25, 2, 100], ["fell > 20%", "fell 0-20%", "up 0-25%", "up 25-100%", "doubled+"])):
        t = d.groupby(pd.cut(d[col], bins=bins, labels=labels), observed=True)["y"].agg(["mean", "count"])
        tabs[col] = {str(k): {"win_rate": round(float(v["mean"]), 3), "n": int(v["count"])} for k, v in t.iterrows()}
    return tabs


def prepare_out(path):
    """Versioned output folder: refuse an existing one so a rerun can never overwrite earlier outputs."""
    path = Path(path)
    if path.exists():
        raise SystemExit(f"Refusing to write into existing folder {path}: pass a new --out")
    path.mkdir(parents=True)
    return path


def out_arg(argv, default_name):
    import argparse
    import datetime as dt
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HUB / "research" / "kalodata" / f"{default_name}_{dt.date.today()}"),
                    help="new output folder (must not exist)")
    return Path(ap.parse_args(argv).out)


def score_latest(p, models, cats, out):
    last = MONTHS[-1]
    cur = p[p["month"] == last].copy()
    hold, brk = cur[cur["in_top500"]].copy(), cur[(~cur["in_top500"]) & (cur["in_risers"] == 1)].copy()
    hold["p_hold_1m"] = models["holders_1m"].predict_proba(hold[FEATURES])[:, 1]
    hold["p_hold_3m"] = models["holders_3m"].predict_proba(hold[FEATURES])[:, 1]
    brk["p_break_1m"] = models["breakouts_1m"].predict_proba(brk[FEATURES])[:, 1]
    brk["p_break_3m"] = models["breakouts_3m"].predict_proba(brk[FEATURES])[:, 1]
    cols = ["category", "product_id", "product_name", "unit_price", "revenue", "revenue_growth_rate", "commission_rate",
            "age_days", "video_share"]
    for d in (hold, brk):
        d["category"] = d["cat"].map(cats)
    hold.sort_values("p_hold_3m", ascending=False)[cols + ["rank_pos", "p_hold_1m", "p_hold_3m"]].to_csv(
        out / f"scores_holders_{last}.csv", index=False)
    brk.sort_values("p_break_3m", ascending=False)[cols + ["riser_pos", "p_break_1m", "p_break_3m"]].to_csv(
        out / f"scores_breakouts_{last}.csv", index=False)
    return len(hold), len(brk)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    out = prepare_out(out_arg(argv, "model_v1_rerun"))
    df, cats, det = load()
    p = build(df)
    print(f"panel: {len(p):,} product-months, {p['product_id'].nunique():,} products, {p['cat'].nunique()} categories")
    results, models = evaluate(p)
    results["breadth_test"] = breadth_test(p, det)
    results["profile_holders_1m"] = profile(p)
    n_hold, n_brk = score_latest(p, models, cats, out)
    results["scored_latest"] = {"month": MONTHS[-1], "holders": n_hold, "breakout_candidates": n_brk}
    (out / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    joblib.dump({"features": FEATURES, "models": models}, out / "models.joblib")
    p.drop(columns=["name"]).to_csv(out / "panel.csv.gz", index=False, compression="gzip")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
