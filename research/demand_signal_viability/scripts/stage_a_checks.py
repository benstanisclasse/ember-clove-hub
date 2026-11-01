"""Stage A checks for the Demand Signal Intelligence viability assessment. Read-only on research/kalodata/kalodata.db.
1. When each month's lists were actually collected (point-in-time question).
2. Revisions: the same product-month seen in pulls collected on different days.
3. model_v2 (four tasks): adopted model vs the simplest rules, per category top-10, from the saved evaluation files.
Writes research/demand_signal_viability/_work/stage_a_checks.json.
Run: python -I research/demand_signal_viability/scripts/stage_a_checks.py
"""
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
HUB = Path(__file__).resolve().parents[3]
DB = HUB / "research" / "kalodata" / "kalodata.db"
OUT = HUB / "research" / "demand_signal_viability" / "_work" / "stage_a_checks.json"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
R = {}

q = pd.read_sql_query("""select kind, month, substr(collected_at,1,10) day from pulls
    where month is not null and success=1""", con)
R["collection_dates_by_kind"] = q.groupby("kind")["day"].agg(["min", "max"]).to_dict("index")
R["months_covered"] = sorted(q["month"].unique().tolist())

P = pd.read_sql_query("""select p.product_id pid, q.category_id cat, q.month, substr(q.collected_at,1,10) day, p.revenue
    from products p join pulls q using(pull_id)
    where q.month is not null and q.success=1 and q.kind in ('top','top_deep','risers','risers_deep')""", con)
P["revenue"] = P["revenue"].astype(float)
x = P.groupby(["pid", "cat", "month", "day"])["revenue"].first().reset_index()
multi = x.groupby(["pid", "cat", "month"])["day"].transform("nunique") > 1
y = x[multi].sort_values("day")
first, last = y.groupby(["pid", "cat", "month"]).first(), y.groupby(["pid", "cat", "month"]).last()
chg = (last["revenue"] / first["revenue"].replace(0, np.nan) - 1)
lag = (pd.to_datetime(last["day"]) - pd.to_datetime(first["day"])).dt.days
D = pd.DataFrame({"chg": chg, "lag": lag}).reset_index()
D = D[D["month"] != "2025-10"]  # partial first month (date windows differ between pulls)
R["revisions_same_product_month_same_category"] = {
    "pairs": len(D), "lag_days_range": [int(D["lag"].min()), int(D["lag"].max())] if len(D) else None,
    "share_identical": round(float((D["chg"] == 0).mean()), 4),
    "median_abs_change": round(float(D["chg"].abs().median()), 4),
    "p95_abs_change": round(float(D["chg"].abs().quantile(0.95)), 4),
    "note": "pulls 1-7 days apart, all 3-12 months after the month ended; says nothing about revisions in the first weeks"}

ev = json.loads((HUB / "research" / "kalodata" / "evals" / "20261028-005841_final.json").read_text(encoding="utf-8"))
mv2 = {}
for t, v in ev["tasks"].items():
    s = v["summary_all_months"]
    rules = {k: s[k]["p_cat@10"][0] for k in ("floor_ratio", "sales", "rank", "momentum", "kalodata_growth", "persistence")}
    best = max(rules, key=rules.get)
    mv2[t] = {"question": v["definition"]["question"], "adopted": v["decision"]["adopted"],
              "adopted_p_cat@10": round(s[v["decision"]["adopted"]]["p_cat@10"][0], 4),
              "best_rule": best, "best_rule_p_cat@10": round(rules[best], 4),
              "gain_pts": round(100 * (s[v["decision"]["adopted"]]["p_cat@10"][0] - rules[best]), 1),
              "base_rate": v["summary_all_months"].get("random", {}).get("p_cat@10", [None])[0]}
R["model_v2_vs_best_rule"] = mv2
OUT.write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps(R, indent=1, default=str))
