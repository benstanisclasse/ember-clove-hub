"""Store profitability model (2026-10-25): break-even CPA/ROAS per product, basket effects, funnel targets, fixed costs.

Reuses the per-order model in test_product_economics.py (prices, EPROLO unit costs and weights re-checked
against Shopify on 2026-10-25: unchanged). ROAS is computed on what the customer pays before tax
(product price + shipping charged), which is what the Shopify pixel normally reports as purchase value.
Run: python -I scripts/profitability_model.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_product_economics import (  # noqa: E402
    CUSTOMER_SHIPPING, FEE_FIXED, FEE_PCT, FREE_SHIP_AT, PRODUCTS, REFUND_PCT,
)

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_RATIO = 0.7  # aim for ads to take 70% of the break-even, leaving ~30% of contribution as profit

# EPROLO shipping to the US, cheapest method, read from the EPROLO app product pages on 2026-10-25
# (same for every variant of a product).
EPROLO_ACTUAL = {
    "Cable Knit Mock Neck Midi Dress": 15.05,  # YANWEN Clothing Line, 8-15 days, 660 g
    "Turtleneck Rib Knit Sweater Dress": 13.35,  # YANWEN Clothing Line, 8-15 days, 550 g
    "Ruched Mesh Wrap V-Neck Top": 8.13,  # CNE Standard, 8-15 days, 220 g
}
# Other products: YANWEN Clothing Line fitted to the two dress quotes ($4.85 + $15.45/kg); it predicts the
# 220 g top within $0.12. High case adds 10%.
SHIP_FIT = (4.85, 15.45)
SHIP_HIGH_FACTOR = 1.10


def ship(title, grams, high=False):
    cost = EPROLO_ACTUAL.get(title, SHIP_FIT[0] + SHIP_FIT[1] * grams / 1000.0)
    return cost * (SHIP_HIGH_FACTOR if high and title not in EPROLO_ACTUAL else 1.0)


def contribution(title, price, cost, grams, high=False):
    rev = revenue(price)
    return rev - cost - ship(title, grams, high) - (rev * FEE_PCT + FEE_FIXED) - price * REFUND_PCT

# Monthly fixed costs. Only the Shopify plan is confirmed (Basic, from the Admin API); the rest are placeholders.
FIXED = [
    ("Shopify Basic plan (monthly billing)", 39.00, "confirmed plan; $29 if billed yearly"),
    ("Domain emberandclove.com", 1.50, "estimate, ~$18/yr"),
    ("EPROLO plan", 0.00, "confirmed Free plan (2026-10-25)"),
    ("Other apps (reviews, email, etc.)", 0.00, "UNKNOWN: fill in from Shopify Settings > Billing"),
    ("New ad videos (Higgsfield, ~8 per month at $4.85)", 38.80, "owner-approved pace; change if more/less"),
]


def revenue(price):
    return price + (CUSTOMER_SHIPPING if price < FREE_SHIP_AT else 0.0)


def basket(items, combined):
    """Contribution for one order holding several items. combined=True assumes EPROLO ships them in one parcel
    (one base fee); combined=False charges each item's own shipping (worst case)."""
    subtotal = sum(p for _, p, _, _ in items)
    cust_ship = CUSTOMER_SHIPPING if subtotal < FREE_SHIP_AT else 0.0
    rev = subtotal + cust_ship
    cost = sum(c for _, _, c, _ in items)
    if combined:
        eprolo = SHIP_FIT[0] + sum(ship(t, g) - SHIP_FIT[0] for t, _, _, g in items)
    else:
        eprolo = sum(ship(t, g) for t, _, _, g in items)
    fees = rev * FEE_PCT + FEE_FIXED
    return rev, rev - cost - eprolo - fees - subtotal * REFUND_PCT


def main():
    rows = []
    for title, handle, coll, price, cost, grams, inv in PRODUCTS:
        rev = revenue(price)
        be = contribution(title, price, cost, grams)
        be_hi = contribution(title, price, cost, grams, high=True)
        rows.append(dict(
            title=title, collection=coll, price=f"{price:.2f}", customer_pays=f"{rev:.2f}", unit_cost=f"{cost:.2f}",
            eprolo_ship=f"{ship(title, grams):.2f}", ship_source="EPROLO quote" if title in EPROLO_ACTUAL else "fitted",
            fees=f"{rev * FEE_PCT + FEE_FIXED:.2f}",
            refund_allowance=f"{price * REFUND_PCT:.2f}",
            gross_margin_pct=f"{be / rev * 100:.0f}", break_even_cpa=f"{be:.2f}", break_even_cpa_high_ship=f"{be_hi:.2f}",
            target_cpa=f"{be * TARGET_RATIO:.2f}", break_even_roas=f"{rev / be:.2f}" if be > 0 else "n/a",
            target_roas=f"{rev / (be * TARGET_RATIO):.2f}" if be > 0 else "n/a",
            profit_at_target=f"{be * (1 - TARGET_RATIO):.2f}",
        ))
    rows.sort(key=lambda r: -float(r["break_even_cpa"]))
    out = os.path.join(HUB, "data", "profitability_2026-10-25.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"{'Product':42} {'Pays':>6} {'Cost':>6} {'Ship':>6} {'BE CPA':>7} {'BE hi':>6} {'Tgt':>6} {'BE ROAS':>7} {'Tgt ROAS':>8}")
    for r in rows:
        print(f"{r['title'][:42]:42} {r['customer_pays']:>6} {r['unit_cost']:>6} {r['eprolo_ship']:>6} "
              f"{r['break_even_cpa']:>7} {r['break_even_cpa_high_ship']:>6} {r['target_cpa']:>6} "
              f"{r['break_even_roas']:>7} {r['target_roas']:>8}")

    by = {t: (t, p, c, g) for t, _, _, p, c, g, _ in PRODUCTS}
    p01, p02 = by["Cable Knit Mock Neck Midi Dress"], by["Turtleneck Rib Knit Sweater Dress"]
    print("\nBaskets (one parcel / shipped separately):")
    for name, items in [("1x P01", [p01]), ("1x P02", [p02]), ("2x P02 (free shipping)", [p02, p02]),
                        ("P01 + P02 (free shipping)", [p01, p02]), ("P02 + Long Pleated Knit Skirt", [p02, by["Long Pleated Knit Skirt"]])]:
        rev, one = basket(items, combined=True)
        _, sep = basket(items, combined=False)
        print(f"  {name:32} pays ${rev:6.2f}  BE CPA ${one:6.2f} (separate parcels ${sep:6.2f})  BE ROAS {rev / one:4.2f}")

    print("\nClick-to-purchase rate needed to hit a CPA (CPA = CPM / (1000 x CTR x CVR)):")
    for cpm in (6, 10, 14):
        for ctr in (0.008, 0.012):
            cpc = cpm / (1000 * ctr)
            need = "  ".join(f"CPA ${cpa}: {cpc / cpa * 100:4.1f}%" for cpa in (22, 25, 31, 35))
            print(f"  CPM ${cpm:>2}  CTR {ctr * 100:.1f}%  CPC ${cpc:4.2f}  ->  {need}")

    fixed = sum(v for _, v, _ in FIXED)
    print(f"\nKnown fixed costs: ${fixed:.2f}/month (apps not included)")
    for label, p in [("P01 at target CPA", p01), ("P02 at target CPA", p02)]:
        per_order = contribution(*p) * (1 - TARGET_RATIO)
        print(f"  {label}: ${per_order:.2f} profit/order -> {fixed / per_order:.0f} orders/month to cover fixed costs")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
