"""Stack study (2026-10-29): which two offers can run together and still keep every order profitable?

Shopify (non-Plus) applies at most one product discount per item, so a pair is one product offer (2nd item off,
% off 2+ items, tiered) plus one order offer ($ off or % off over a spend), both set to combine. Order discounts
apply after product discounts; the spend threshold is checked on the subtotal before the product discount (the
worst case: more orders qualify). Same orders and model as scripts/offer_study.py (every 1-, 2- and 3-item order,
$20 CPA, one parcel, free shipping), at live and floor prices.
Writes data/stack_study_2026-10-29.csv. Changes nothing in the store.
Run: python -I scripts/stack_study.py
"""
import csv
import itertools
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bundle_study import kept, products  # noqa: E402
from offer_study import cheapest_pct, floor_price, pct_off_qty, tiered  # noqa: E402

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HUB, "data", "stack_study_2026-10-29.csv")

PRODUCT = [(f"2nd item {p}% off", cheapest_pct(p)) for p in (20, 30, 40)]
PRODUCT += [(f"{p}% off 2+ items", pct_off_qty(p, 2)) for p in (10, 15, 20)]
PRODUCT += [("10% off 2 / 20% off 3+", tiered(10, 20)), ("15% off 2 / 25% off 3+", tiered(15, 25))]
# (label, spend threshold, dollars off, percent off)
ORDER = [("$10 off $75+", 75, 10, 0), ("$10 off $100+", 100, 10, 0), ("$15 off $100+", 100, 15, 0),
         ("$20 off $120+", 120, 20, 0), ("$25 off $150+", 150, 25, 0), ("15% off $100+", 100, 0, 15),
         ("20% off $120+", 120, 0, 20)]


def main():
    synced, live = products()
    scenarios = {"live": live, "floor": [floor_price(p) for p in live]}
    rows = []
    for name, ps in scenarios.items():
        orders = [list(o) for n in (1, 2, 3) for o in itertools.combinations_with_replacement(ps, n)]
        for (plabel, poff), (olabel, spend, dollars, pct) in itertools.product(PRODUCT, ORDER):
            singles, multi = [], []
            for o in orders:
                sub = sum(i["price"] for i in o)
                d = poff(o)
                if sub >= spend:
                    d += dollars + (sub - d) * pct / 100
                (multi if len(o) > 1 else singles).append(kept(o, d))
            rows.append(dict(prices=name, product_offer=plabel, order_offer=olabel,
                             single_losing=sum(k < 0 for k in singles) / len(singles), worst_single=min(singles),
                             worst_multi=min(multi), avg_multi=statistics.mean(multi)))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()} for r in rows)
    print(f"synced {synced}; {len(rows)} stacks; avg/worst over 2- and 3-item orders, after a $20 CPA")
    for name in scenarios:
        print(f"\n== {name} prices: stacks where no 2- or 3-item order loses money (best average first) ==")
        ok = sorted((r for r in rows if r["prices"] == name and r["worst_multi"] >= 0), key=lambda r: -r["avg_multi"])
        for r in ok:
            print(f"  {r['product_offer']:<24} + {r['order_offer']:<15} avg ${r['avg_multi']:6.2f}  worst ${r['worst_multi']:6.2f}"
                  f"  1-item orders losing {r['single_losing']:.1%} (worst ${r['worst_single']:.2f})")
        bad = [r for r in rows if r["prices"] == name and r["worst_multi"] < 0]
        print(f"  ({len(bad)} other stacks lose money on some 2- or 3-item orders)")
    print("->", OUT)


if __name__ == "__main__":
    main()
