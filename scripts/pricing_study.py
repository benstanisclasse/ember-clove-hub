"""Pricing study (2026-10-26): the owner's formula (price = $20 CPA + shipping + item cost) against current prices
and against a formula that also covers card fees, refunds and a profit.

Reads the Shopify bulk export data/inbox/pricing_export_2026-10-26.jsonl (every active product and variant with
price, EPROLO unit cost and weight). Per product it uses the most expensive variant to source (highest cost, then
heaviest), so the price covers every size. Shipping, fees and refunds come from the profitability model.
Writes data/pricing_study_2026-10-26.csv. Changes nothing in the store.
Run: python -I scripts/pricing_study.py
"""
import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profitability_model import ship  # noqa: E402
from test_product_economics import CUSTOMER_SHIPPING, FEE_FIXED, FEE_PCT, FREE_SHIP_AT, REFUND_PCT  # noqa: E402

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(HUB, "data", "inbox", "pricing_export_2026-10-26.jsonl")
OUT = os.path.join(HUB, "data", "pricing_study_2026-10-26.csv")
CPA = 20.0
PROFIT = 10.0  # profit kept per order after the $20 CPA in the suggested formula


def grams(m):
    w = (m or {}).get("weight") or {}
    v, unit = w.get("value") or 0, w.get("unit", "GRAMS")
    return v * {"GRAMS": 1, "KILOGRAMS": 1000, "POUNDS": 453.6, "OUNCES": 28.35}[unit]


def kept(price, cost, shipping):
    """What one order leaves after product, EPROLO shipping, card fees, refund allowance and the $20 CPA."""
    rev = price + (CUSTOMER_SHIPPING if price < FREE_SHIP_AT else 0.0)
    return rev - cost - shipping - (rev * FEE_PCT + FEE_FIXED) - price * REFUND_PCT - CPA


def charm(x):
    """Round up to the next $X.99."""
    return math.ceil(x + 0.01) - 0.01


def suggested(cost, shipping):
    """Lowest .99 price that keeps PROFIT after CPA, fees and refunds (checks both sides of the $70 free-ship line)."""
    p = 9.99
    while kept(p, cost, shipping) < PROFIT:
        p += 1.0
    return p


def main():
    products, variants = {}, {}
    for line in open(EXPORT, encoding="utf-8"):
        o = json.loads(line)
        if "__parentId" in o:
            variants.setdefault(o["__parentId"], []).append(o)
        else:
            products[o["id"]] = o
    rows = []
    for pid, p in products.items():
        vs = variants.get(pid, [])
        if not vs:
            continue
        def key(v):
            c = float(((v["inventoryItem"] or {}).get("unitCost") or {}).get("amount") or 0)
            return (c, grams((v["inventoryItem"] or {}).get("measurement")))
        top = max(vs, key=key)
        cost, g = key(top)
        prices = sorted(float(v["price"]) for v in vs)
        price = prices[len(prices) // 2]
        shp = ship(p["title"], g)
        owner = round(CPA + shp + cost, 2)
        sug = suggested(cost, shp)
        rows.append(dict(
            title=p["title"][:60], vendor=p["vendor"], type=p["productType"] or "(none)",
            unit_cost=f"{cost:.2f}", grams=f"{g:.0f}", eprolo_ship=f"{shp:.2f}",
            current_price=f"{price:.2f}", price_range=f"{prices[0]:.2f}-{prices[-1]:.2f}",
            kept_now=f"{kept(price, cost, shp):.2f}",
            owner_formula=f"{owner:.2f}", kept_owner=f"{kept(owner, cost, shp):.2f}",
            suggested=f"{sug:.2f}", kept_suggested=f"{kept(sug, cost, shp):.2f}",
            change_vs_now=f"{sug - price:+.2f}"))
    rows.sort(key=lambda r: (r["type"], r["title"]))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} products -> {OUT}")
    for r in rows:
        print("\t".join(r[k] for k in ("type", "title", "unit_cost", "eprolo_ship", "current_price", "kept_now",
                                         "owner_formula", "kept_owner", "suggested", "kept_suggested")))


if __name__ == "__main__":
    main()
