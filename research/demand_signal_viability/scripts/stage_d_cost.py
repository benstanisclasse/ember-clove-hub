"""Stage D cost model (registry/STAGE_D_PLAN.md D4). Pure arithmetic on documented price lists plus labelled assumptions.
Writes _work/stage_d_cost_model.json. Run: python -I research/demand_signal_viability/scripts/stage_d_cost.py

Documented inputs:
- Kalodata credits: rank 0.1 per 100-row page; product detail 0.1; product images 0.01 (pricing JSON saved 2026-10-31).
- USD per Kalodata credit: $0.10, our observed rate (564.1 credits ~ $56, API capability audit). Not re-verified.
- CJ API points: free, 50,000/day per account; ~124 points per candidate (Stage C). Licence for multi-user use: Stage D.
- Claude list prices per million tokens (claude-api skill, cached 2026-10-06): Opus 5.5 $4/$20, Sonnet 5.5 $2/$10,
  Haiku 5.5 $0.10/$0.50; Batch API 50% off.
Assumptions are marked ASSUMPTION.
"""
import json
from itertools import product
from pathlib import Path

W = Path(__file__).resolve().parents[1] / "_work"
USD_PER_CREDIT = 0.10
CATS = 28
PAGES = {"product rank 1-1,000": 10, "risers 1-200": 2, "top videos 1-300": 3}
REFRESH_PER_MONTH = {"monthly": 1, "weekly": 4.33, "daily": 30}
ENRICH_N = {"300": 300, "1000": 1000}                 # candidates enriched (detail + images) per refresh
DETAIL, IMAGES = 0.1, 0.01
NEW_SHARE = 0.9                                     # ASSUMPTION from Stage B stability: only 2-9% of flags repeat month to month
LLM = {  # $ per matched candidate
    "agent (as run, Opus-class, ~60k tokens: 50k in / 10k out)": (50_000 * 4 + 10_000 * 20) / 1e6,
    "structured matcher, Sonnet 5.5 (~6k in / 2k out)": (6_000 * 2 + 2_000 * 10) / 1e6,
    "structured matcher, Haiku 5.5 batch (~6k in / 2k out, 50% off)": 0.5 * (6_000 * 0.10 + 2_000 * 0.50) / 1e6,
}
WATCH = {  # per-customer watchlist refreshes via product/detail (0.1 credit), ASSUMPTION on usage
    "low (20 items, weekly)": 20 * 4.33 * DETAIL,
    "mid (50 items, weekly)": 50 * 4.33 * DETAIL,
    "high (100 items, daily)": 100 * 30 * DETAIL,
}
WATCH_OVERLAP = 0.5                                 # ASSUMPTION: half of watchlist refreshes are shared (cached) across customers
FIXED = {100: 150, 1000: 600, 10000: 3000}          # ASSUMPTION: hosting, database, monitoring, $/month
SUPPORT_PER_CUSTOMER = 2.5                          # ASSUMPTION: ~6 min/customer-month at $25/h
PAYMENT_FEE = 0.03                                  # ASSUMPTION: card/payment processing share of price
TARGET_GM = 0.70

shared_rank_credits = CATS * sum(PAGES.values()) * 0.1
rows = []
for (freq, k), (n_lbl, n), (llm_lbl, llm), (w_lbl, w), cust in product(REFRESH_PER_MONTH.items(), ENRICH_N.items(), LLM.items(),
                                                                    WATCH.items(), FIXED):
    per_refresh_credits = shared_rank_credits + n * (DETAIL + IMAGES)
    shared_data = per_refresh_credits * k * USD_PER_CREDIT
    matching = n * NEW_SHARE * k * llm
    cj_points_per_day = n * NEW_SHARE * k / 30 * 124
    watch = cust * w * (1 - WATCH_OVERLAP) * USD_PER_CREDIT
    variable = shared_data + matching + watch + cust * SUPPORT_PER_CUSTOMER
    total = variable + FIXED[cust]
    per_cust = total / cust
    price = per_cust / (1 - TARGET_GM - PAYMENT_FEE)
    rows.append({"refresh": freq, "enriched_per_refresh": n_lbl, "matcher": llm_lbl, "watchlist": w_lbl, "customers": cust,
                 "shared_kalodata_usd": round(shared_data, 2), "matching_usd": round(matching, 2), "watchlist_usd": round(watch, 2),
                 "support_usd": cust * SUPPORT_PER_CUSTOMER, "fixed_usd": FIXED[cust], "total_usd_month": round(total, 2),
                 "cost_per_customer": round(per_cust, 2), "price_for_70pct_gm": round(price, 2),
                 "cj_points_per_day": round(cj_points_per_day), "cj_quota_ok_single_account": cj_points_per_day <= 50_000})
R = {"inputs": {"usd_per_credit": USD_PER_CREDIT, "shared_rank_credits_per_refresh": round(shared_rank_credits, 1),
                "pages_per_category": PAGES, "llm_cost_per_match": {k: round(v, 4) for k, v in LLM.items()},
                "watchlist_credits_per_customer_month": {k: round(v, 1) for k, v in WATCH.items()},
                "assumptions": {"new_share": NEW_SHARE, "watch_overlap": WATCH_OVERLAP, "fixed": FIXED,
                                "support_per_customer": SUPPORT_PER_CUSTOMER, "payment_fee": PAYMENT_FEE, "target_gm": TARGET_GM}},
     "scenarios": rows}
# headline scenarios
pick = lambda f, n, m, w: [r for r in rows if r["refresh"] == f and r["enriched_per_refresh"] == n and r["matcher"].startswith(m) and r["watchlist"].startswith(w)]  # noqa: E731
R["headline"] = {"lean (weekly, 300 enriched, Haiku batch matcher, low watchlist)": pick("weekly", "300", "structured matcher, Haiku", "low"),
                 "mid (weekly, 1000 enriched, Sonnet matcher, mid watchlist)": pick("weekly", "1000", "structured matcher, Sonnet", "mid"),
                 "heavy (daily, 1000 enriched, agent matcher, high watchlist)": pick("daily", "1000", "agent", "high")}
(W / "stage_d_cost_model.json").write_text(json.dumps(R, indent=1), encoding="utf-8")
print(json.dumps(R["inputs"], indent=1))
for k, v in R["headline"].items():
    print("==", k)
    for r in v:
        print(f"  {r['customers']:>6} customers: ${r['total_usd_month']:>10,.0f}/mo  (data {r['shared_kalodata_usd']:,.0f}, match {r['matching_usd']:,.0f}, watch {r['watchlist_usd']:,.0f})"
              f"  per customer ${r['cost_per_customer']:.2f}  price for 70% GM ${r['price_for_70pct_gm']:.2f}  CJ pts/day {r['cj_points_per_day']:,}")
