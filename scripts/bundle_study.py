"""Bundle study (2026-10-29): what a "50% off when you buy any 2 items" offer does to profit per order.

Two readings of the offer:
  A. 50% off the whole order once it holds 2 items (both items half price).
  B. 50% off the cheaper item (buy one, get the second half price; how Shopify's Buy X Get Y discounts work).
Every pair of active products is one 2-item order (same product twice included, e.g. two colours), weighted
equally. Per order: product cost, EPROLO shipping (one parcel: base fee once; or separate parcels, worst case),
card fees 2.9% + $0.30 once, refunds 5% of what was paid, and one $20 CPA. Standard shipping is free on every
order. Prices, unit costs and weights from studio/analytics.db (15-min Shopify sync); per product the most
expensive variant to source and the median price, as in scripts/pricing_study.py.
Writes data/bundle_study_2026-10-29.csv (per pair). Changes nothing in the store.
Run: python -I scripts/bundle_study.py
"""
import csv
import itertools
import os
import sqlite3
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profitability_model import SHIP_FIT, ship  # noqa: E402
from test_product_economics import FEE_FIXED, FEE_PCT, REFUND_PCT  # noqa: E402

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HUB, "studio", "analytics.db")
OUT = os.path.join(HUB, "data", "bundle_study_2026-10-29.csv")
CPA = 20.0


def products():
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    synced = db.execute("select max(fetched_at) from products").fetchone()[0]
    out = []
    for pid, title in db.execute("select product_id, title from products where status='ACTIVE'").fetchall():
        vs = db.execute("select price, unit_cost, grams from variants where product_id=?", (pid,)).fetchall()
        if not vs:
            continue
        cost, g = max(((v[1] or 0), (v[2] or 0)) for v in vs)
        prices = sorted(v[0] for v in vs)
        out.append(dict(title=title, price=prices[len(prices) // 2], cost=cost, ship=ship(title, g)))
    return synced, out


def kept(items, discount, combined=True):
    """What one order keeps after the CPA. items: product dicts; discount: dollars off the order."""
    paid = sum(i["price"] for i in items) - discount
    if combined:
        eprolo = SHIP_FIT[0] + sum(i["ship"] - SHIP_FIT[0] for i in items)
    else:
        eprolo = sum(i["ship"] for i in items)
    return paid - sum(i["cost"] for i in items) - eprolo - (paid * FEE_PCT + FEE_FIXED) - paid * REFUND_PCT - CPA


def summary(xs):
    return (f"avg ${statistics.mean(xs):7.2f}  median ${statistics.median(xs):7.2f}  "
            f"losing {sum(x < 0 for x in xs) / len(xs):6.1%}")


def main():
    synced, ps = products()
    singles = [kept([p], 0) for p in ps]
    pairs = list(itertools.combinations_with_replacement(ps, 2))
    rows = []
    for a, b in pairs:
        both = a["price"] + b["price"]
        cheap = min(a["price"], b["price"])
        rows.append(dict(
            item_1=a["title"], item_2=b["title"], subtotal=both,
            full=kept([a, b], 0), half_order=kept([a, b], both / 2), half_cheaper=kept([a, b], cheap / 2),
            half_order_sep=kept([a, b], both / 2, False), half_cheaper_sep=kept([a, b], cheap / 2, False)))

    print(f"synced {synced}; {len(ps)} active products, {len(pairs)} two-item orders; all after a ${CPA:.0f} CPA")
    print(f"{'1 item, full price':<34}", summary(singles))
    print(f"{'2 items, full price':<34}", summary([r['full'] for r in rows]))
    print(f"{'A. 2 items, both half price':<34}", summary([r['half_order'] for r in rows]))
    print(f"{'   (separate parcels)':<34}", summary([r['half_order_sep'] for r in rows]))
    print(f"{'B. 2 items, cheaper one half off':<34}", summary([r['half_cheaper'] for r in rows]))
    print(f"{'   (separate parcels)':<34}", summary([r['half_cheaper_sep'] for r in rows]))
    print(f"before ads (break-even CPA): 1 item ${statistics.mean(singles) + CPA:.2f}, "
          f"A ${statistics.mean(r['half_order'] for r in rows) + CPA:.2f}, "
          f"B ${statistics.mean(r['half_cheaper'] for r in rows) + CPA:.2f}")
    print(f"avg discount given: A ${statistics.mean(r['subtotal'] / 2 for r in rows):.2f}, "
          f"B ${statistics.mean(min(a['price'], b['price']) / 2 for a, b in pairs):.2f}")

    # Largest % off a 2-item order that still keeps at least what a 1-item full-price order keeps.
    base = statistics.mean(singles)
    print("\n% off the whole 2-item order -> avg kept, share losing")
    for pct in (10, 15, 20, 25, 30, 40, 50):
        xs = [kept([a, b], (a["price"] + b["price"]) * pct / 100) for a, b in pairs]
        print(f"  {pct:>2}%  {summary(xs)}{'   <- still beats a 1-item order' if statistics.mean(xs) >= base else ''}")

    rows.sort(key=lambda r: r["half_cheaper"])
    print("\nB, worst 5 pairs:")
    for r in rows[:5]:
        print(f"  {r['item_1'][:34]} + {r['item_2'][:34]}  ${r['half_cheaper']:.2f}")
    print("B, best 5 pairs:")
    for r in rows[-5:]:
        print(f"  {r['item_1'][:34]} + {r['item_2'][:34]}  ${r['half_cheaper']:.2f}")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.2f}" if isinstance(v, float) else v) for k, v in r.items()})
    print("->", OUT)


if __name__ == "__main__":
    main()
