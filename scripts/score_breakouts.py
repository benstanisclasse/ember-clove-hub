"""Breakout candidates from the latest month's deep riser list (top 1,000 by growth per category).

History only has risers ranked 1-200, so the riser position is left out of these models (deeper positions would be
outside anything they learned). Trained on all labelled months, checked forward on the last three, then used to score
every latest-month riser outside its category's top 500.
Run: python -I scripts/score_breakouts.py
"""
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_product_model import FEATURES, HGB, MONTHS, OUT, TASKS, build, load, prec_at, subset  # noqa: E402

FEATS = [f for f in FEATURES if f not in ("riser_pos", "rank_pos", "in_risers")]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    df, cats, _ = load()
    p = build(df)
    last = MONTHS[-1]
    cur = p[(p["month"] == last) & (~p["in_top500"]) & (p["in_risers"] == 1)].copy()
    cur["category"] = cur["cat"].map(cats)
    checks = {}
    for name in ("breakouts_1m", "breakouts_3m"):
        which, label, h = TASKS[name]
        d = subset(p, which, h)
        d["y"] = label(d)
        test = d["mi"].max() - 2
        tr, te = d[d["mi"] < test], d[d["mi"] >= test]
        s = HistGradientBoostingClassifier(**HGB).fit(tr[FEATS], tr["y"]).predict_proba(te[FEATS])[:, 1]
        checks[name] = {"auc": round(roc_auc_score(te["y"], s), 3), "base_rate": round(float(te["y"].mean()), 3),
                        "top10pct_hit_rate": round(prec_at(te["y"].values, s, 0.10), 3)}
        model = HistGradientBoostingClassifier(**HGB).fit(d[FEATS], d["y"])
        cur[f"p_{name}"] = model.predict_proba(cur[FEATS])[:, 1]
        print(f"{name} without riser position: AUC {checks[name]['auc']}, top 10% hit "
              f"{checks[name]['top10pct_hit_rate']:.0%} vs base {checks[name]['base_rate']:.0%}")
    cols = ["category", "product_id", "product_name", "unit_price", "revenue", "revenue_growth_rate",
            "commission_rate", "age_days", "video_share", "riser_pos", "p_breakouts_1m", "p_breakouts_3m"]
    out = cur.sort_values("p_breakouts_3m", ascending=False)[cols]
    out.to_csv(OUT / f"breakout_candidates_{last}_deep.csv", index=False)
    (OUT / "breakout_deep_check.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    deep = out["riser_pos"] > 200
    print(f"{len(out):,} candidates ({deep.sum():,} from positions 201-1,000); "
          f"p_3m >= 0.5: {(out['p_breakouts_3m'] >= 0.5).sum():,}, of which deep: {((out['p_breakouts_3m'] >= 0.5) & deep).sum():,}")


if __name__ == "__main__":
    main()
