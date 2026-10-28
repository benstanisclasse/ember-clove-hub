"""Pilot product-outcome model on Kalodata data (2026-10-25).

Inputs: Womenswear & Underwear (category 601152) top 500 products for Aug 2026 (features) and Sep 2026 (outcome),
from research/kalodata/kalodata.db. Label: "won" = still in Sep top 500 and Sep sales >= Aug sales.
One month-to-month transition only, so evaluation is 5-fold cross-validation, not a forward test.
Run: python -I scripts/pilot_model.py
"""
import sqlite3
import sys
from pathlib import Path

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
OUT = HUB / "research" / "kalodata" / "pilot_model_2026-10-25"
FEATURES = ["log_sales", "log_units", "unit_price", "growth_signed_log", "commission_rate", "video_share",
            "live_share", "shop_page_share", "age_days", "log_sku_count", "rank_position", "seller_products_in_top500"]


def load(con, month):
    return pd.read_sql("SELECT p.*, p.position + (CAST(substr(u.name, -1) AS INTEGER) - 1) * 100 AS rank_pos "
                       "FROM products p JOIN pulls u ON p.pull_id = u.pull_id "
                       f"WHERE u.name LIKE 'pilot_womenswear_{month}_p%'", con)


def build():
    con = sqlite3.connect(HUB / "research" / "kalodata" / "kalodata.db")
    aug, sep = load(con, "2026-08"), load(con, "2026-09")
    num = ["revenue", "sales_volumn", "unit_price", "revenue_growth_rate", "commission_rate", "live_revenue",
           "video_revenue", "showcase_revenue", "sku_count"]
    aug[num] = aug[num].apply(pd.to_numeric, errors="coerce")
    sep["revenue"] = pd.to_numeric(sep["revenue"], errors="coerce")
    df = aug.merge(sep[["product_id", "revenue"]].rename(columns={"revenue": "sep_sales"}), on="product_id", how="left")
    df["won"] = ((df.sep_sales.notna()) & (df.sep_sales >= df.revenue)).astype(int)
    df["log_sales"] = np.log10(df.revenue)
    df["log_units"] = np.log10(df.sales_volumn.clip(lower=1))
    g = df.revenue_growth_rate.fillna(0)
    df["growth_signed_log"] = np.sign(g) * np.log1p(g.abs())
    for col, src in (("video_share", "video_revenue"), ("live_share", "live_revenue"), ("shop_page_share", "showcase_revenue")):
        df[col] = (df[src] / df.revenue).clip(0, 1)
    df["age_days"] = (pd.Timestamp("2026-08-31") - pd.to_datetime(df.launch_date, errors="coerce")).dt.days
    df["log_sku_count"] = np.log10(df.sku_count.clip(lower=1))
    df["rank_position"] = df.rank_pos
    df["seller_products_in_top500"] = df.groupby("seller_id").product_id.transform("count")
    return df


def precision_at(y, p, k):
    return y[np.argsort(-p)[:k]].mean()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    df = build()
    X, y = df[FEATURES], df.won.values
    base = y.mean()
    print(f"{len(df)} products, {y.sum()} won ({base:.0%} base rate)")
    cv = StratifiedKFold(5, shuffle=True, random_state=7)
    models = {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "boosted_trees": HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                        min_samples_leaf=20, random_state=7),
    }
    lines = []
    Xf = X.fillna(X.median())
    for name, m in models.items():
        p = cross_val_predict(m, Xf, y, cv=cv, method="predict_proba")[:, 1]
        df[f"p_{name}"] = p
        res = (f"{name}: AUC {roc_auc_score(y, p):.2f} | top 25 hit rate {precision_at(y, p, 25):.0%} | "
               f"top 50 {precision_at(y, p, 50):.0%} | top 100 {precision_at(y, p, 100):.0%} (random {base:.0%})")
        print(res)
        lines.append(res)
    lr = models["logistic"].fit(Xf, y)
    coefs = pd.Series(lr[-1].coef_[0], index=FEATURES).sort_values()
    gbm = models["boosted_trees"].fit(Xf, y)
    pi = permutation_importance(gbm, Xf, y, n_repeats=30, random_state=7, scoring="roc_auc")
    imp = pd.Series(pi.importances_mean, index=FEATURES).sort_values(ascending=False)
    print("\nLogistic coefficients (standardised; + = more likely to win):\n" + coefs.round(2).to_string())
    print("\nBoosted-tree permutation importance (AUC drop):\n" + imp.round(3).to_string())

    def bucket(col, bins, labels):
        t = df.groupby(pd.cut(df[col], bins=bins, labels=labels), observed=True).won.agg(["mean", "count"])
        return t.assign(mean=lambda s: (s["mean"] * 100).round(0)).rename(columns={"mean": "won %", "count": "n"})

    tables = {
        "August growth vs July": bucket("revenue_growth_rate", [-101, -20, 0, 25, 75, 1e9], ["< -20%", "-20–0%", "0–25%", "25–75%", "> 75%"]),
        "Product age at end of August": bucket("age_days", [-1, 60, 180, 365, 5000], ["< 2 months", "2–6 months", "6–12 months", "> 1 year"]),
        "Price": bucket("unit_price", [0, 20, 30, 45, 1000], ["< $20", "$20–30", "$30–45", "> $45"]),
        "Share of sales from videos": bucket("video_share", [-0.01, 0.5, 0.8, 0.95, 1.01], ["< 50%", "50–80%", "80–95%", "> 95%"]),
        "Sales rank in August": bucket("rank_position", [0, 50, 150, 300, 500], ["1–50", "51–150", "151–300", "301–500"]),
    }
    for t, tab in tables.items():
        print(f"\n{t}\n{tab.to_string()}")
    df.drop(columns=["raw_json"]).to_csv(OUT / "feature_table.csv", index=False)
    with open(OUT / "results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n\n" + coefs.round(3).to_string() + "\n\n" + imp.round(4).to_string() + "\n")
        for t, tab in tables.items():
            f.write(f"\n{t}\n{tab.to_string()}\n")
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
