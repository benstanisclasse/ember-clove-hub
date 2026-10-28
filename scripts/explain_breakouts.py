"""Explain the 3-month breakout model: what drives it overall, and why each recommended product scored as it did.

Overall: permutation importance on the forward test months, and how the predicted chance moves with each main signal
(partial dependence). Per product: each signal is reset to a typical riser's value (the training median) and the drop
in the product's score is that signal's contribution.
Run: python -I scripts/explain_breakouts.py --out research/kalodata/explain_v1_rerun_<date>
Outputs go to a new folder (an existing one is refused; v1 outputs are never overwritten). The audit found these
per-product "reasons" are one model fit's descriptive patterns, not findings (docs/MARKET_MODEL_VALIDATION_AUDIT.md).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_breakouts import FEATS  # noqa: E402
from train_product_model import HGB, MONTHS, TASKS, build, load, out_arg, prepare_out, subset  # noqa: E402

PICKS = ["La Costa Slide", "Cushionaire Fable", "MAELREG Men", "Potaroma Pet Brain", "BEDLORE", "Zoe Low Rise",
         "Faux Fur Short Booties", "SHOWITTY Womens High Waisted", "HSIA Seamless Iris", "PAVOI 14K Gold Plated Letter"]
LABEL = {"log_sales": "Sept sales", "log_units": "units sold", "unit_price": "price", "growth_slog": "growth vs August",
         "commission_rate": "commission", "video_share": "share of sales from videos", "live_share": "share from lives",
         "shop_share": "share from shop page", "age_days": "product age", "log_sku": "number of variants",
         "seller_n_top500": "seller's products already in the top 500", "seller_share_cat": "seller's share of category",
         "cat_growth": "category growth vs August", "months_seen_before": "months already on our lists",
         "prev_ratio": "sales vs its previous listed month", "was_top500_prev": "was top 500 last month",
         "price_vs_cat": "price vs category median"}


def show(f, v):
    if pd.isna(v):
        return "unknown"
    if f == "log_sales":
        return f"${10 ** v:,.0f}"
    if f == "log_units":
        return f"{10 ** v:,.0f}"
    if f == "growth_slog":
        return f"{np.sign(v) * np.expm1(abs(v)):+,.0f}%"
    if f in ("video_share", "live_share", "shop_share", "seller_share_cat"):
        return f"{v:.0%}"
    if f == "unit_price":
        return f"${v:,.2f}"
    if f == "age_days":
        return f"{v / 30:.0f} months"
    if f == "log_sku":
        return f"{10 ** v:,.0f}"
    if f in ("price_vs_cat", "cat_growth", "prev_ratio"):
        return f"{v:.2f}x"
    if f == "commission_rate":
        return f"{v:.0f}%"
    return f"{v:,.0f}"


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    out_dir = prepare_out(out_arg(argv, "explain_v1_rerun"))
    df, cats, _ = load()
    p = build(df)
    which, label, h = TASKS["breakouts_3m"]
    d = subset(p, which, h)
    d["y"] = label(d)
    test = d["mi"].max() - 2
    tr, te = d[d["mi"] < test], d[d["mi"] >= test]
    m_test = HistGradientBoostingClassifier(**HGB).fit(tr[FEATS], tr["y"])
    pi = permutation_importance(m_test, te[FEATS], te["y"], n_repeats=5, random_state=7, scoring="roc_auc", n_jobs=-1)
    importance = {LABEL[f]: round(float(v), 4) for f, v in sorted(zip(FEATS, pi.importances_mean), key=lambda x: -x[1])}
    model = HistGradientBoostingClassifier(**HGB).fit(d[FEATS], d["y"])
    ref = d[FEATS].median()

    curves = {}
    sample = d[FEATS].sample(min(20000, len(d)), random_state=7)
    for f in ["log_sales", "growth_slog", "price_vs_cat", "video_share", "age_days", "seller_n_top500", "log_sku",
              "commission_rate"]:
        grid = sample[f].quantile([0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95]).unique()
        avg = []
        for g in grid:  # average predicted chance if every riser had this value
            alt = sample.copy()
            alt[f] = g
            avg.append(float(model.predict_proba(alt)[:, 1].mean()))
        curves[LABEL[f]] = [(show(f, g), round(v, 3)) for g, v in zip(grid, avg)]

    cur = p[(p["month"] == MONTHS[-1]) & (~p["in_top500"]) & (p["in_risers"] == 1)].copy()
    cur["category"] = cur["cat"].map(cats)
    explained = []
    for key in PICKS:
        hit = cur[cur["product_name"].str.contains(key, case=False, regex=False, na=False)]
        if hit.empty:
            continue
        scores = model.predict_proba(hit[FEATS])[:, 1]  # several listings can share a name: explain the top-scored one
        row = hit.iloc[[int(np.argmax(scores))]]
        base = float(scores.max())
        contrib = {}
        for f in FEATS:
            alt = row[FEATS].copy()
            alt[f] = ref[f]
            contrib[f] = base - float(model.predict_proba(alt)[:, 1][0])
        top = sorted(contrib.items(), key=lambda x: -abs(x[1]))[:5]
        explained.append({
            "product": str(row["product_name"].iloc[0])[:80], "category": row["category"].iloc[0],
            "chance_3m": round(base, 2),
            "drivers": [{"signal": LABEL[f], "value": show(f, row[f].iloc[0]), "typical": show(f, ref[f]),
                         "effect": round(c, 2)} for f, c in top]})
    out = {"model": "breakouts_3m without riser position", "typical_riser": {LABEL[f]: show(f, ref[f]) for f in FEATS},
           "importance": importance, "curves": curves, "products": explained}
    (out_dir / f"breakout_explanations_{MONTHS[-1]}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                                           encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
