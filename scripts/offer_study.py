"""Offer study (2026-10-29): which sales offer keeps every order profitable after the ad cost?

Tests percentage, second-item, spend-threshold and tiered offers on every 1-, 2- and 3-item order from the active
products (same product more than once included; every order weighted equally), with the per-order model from
scripts/bundle_study.py: cost, EPROLO shipping in one parcel, 2.9% + $0.30, 5% refunds on what was paid, one
$20 CPA, free standard shipping.
Two price scenarios:
  live   today's prices (analytics.db sync)
  floor  each product raised (never lowered) to the lowest $X.99 where a 1-item order keeps at least $0 after
         the CPA. A draft for comparison only.
Writes data/offer_study_2026-10-29.csv. Changes nothing in the store.
Run: python -I scripts/offer_study.py
"""
import csv
import itertools
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bundle_study import kept, products  # noqa: E402

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HUB, "data", "offer_study_2026-10-29.csv")


def pct_off_qty(pct, qty):
    return lambda items: sum(i["price"] for i in items) * pct / 100 if len(items) >= qty else 0.0


def cheapest_pct(pct):
    return lambda items: min(i["price"] for i in items) * pct / 100 if len(items) >= 2 else 0.0


def dollars_over(off, spend):
    return lambda items: off if sum(i["price"] for i in items) >= spend else 0.0


def pct_over(pct, spend):
    return lambda items: sum(i["price"] for i in items) * pct / 100 if sum(i["price"] for i in items) >= spend else 0.0


def tiered(p2, p3):
    def f(items):
        pct = p3 if len(items) >= 3 else p2 if len(items) == 2 else 0
        return sum(i["price"] for i in items) * pct / 100
    return f


OFFERS = [("No offer", lambda items: 0.0)]
OFFERS += [(f"2nd item {p}% off (cheaper)", cheapest_pct(p)) for p in (20, 30, 40, 50)]
OFFERS += [(f"{p}% off 2+ items", pct_off_qty(p, 2)) for p in (10, 15, 20, 25)]
OFFERS += [(f"{p}% off 3+ items", pct_off_qty(p, 3)) for p in (20, 25, 30)]
OFFERS += [("10% off 2 / 20% off 3+", tiered(10, 20)), ("15% off 2 / 25% off 3+", tiered(15, 25))]
OFFERS += [(f"${o} off ${s}+", dollars_over(o, s)) for o, s in ((10, 75), (10, 100), (15, 100), (20, 120), (25, 150))]
OFFERS += [(f"{p}% off ${s}+", pct_over(p, s)) for p, s in ((15, 100), (20, 120))]


def floor_price(p):
    """Lowest $X.99 at or above the live price where a 1-item order keeps >= $0 after the CPA."""
    q = dict(p)
    while kept([q], 0) < 0:
        q["price"] = math.floor(q["price"]) + 0.99 if q["price"] % 1 < 0.985 else q["price"] + 1
    return q


def main():
    synced, live = products()
    scenarios = {"live": live, "floor": [floor_price(p) for p in live]}
    raised = [(a, b) for a, b in zip(live, scenarios["floor"]) if b["price"] > a["price"]]
    print(f"synced {synced}; {len(live)} products; floor raises {len(raised)} of them, "
          f"avg +${statistics.mean(b['price'] - a['price'] for a, b in raised):.2f}")
    out = []
    for name, ps in scenarios.items():
        orders = {n: list(itertools.combinations_with_replacement(ps, n)) for n in (1, 2, 3)}
        print(f"\n== {name} prices ==  (avg kept after $20 CPA; % of orders losing; worst order)")
        print(f"{'offer':<28}{'1 item':>22}{'2 items':>22}{'3 items':>22}")
        for label, offer in OFFERS:
            cells, row = [], dict(prices=name, offer=label)
            for n, os_ in orders.items():
                ks = [kept(list(o), offer(list(o))) for o in os_]
                lose = sum(k < 0 for k in ks) / len(ks)
                cells.append(f"{statistics.mean(ks):7.2f} {lose:5.1%} {min(ks):7.2f}")
                row.update({f"avg_{n}": f"{statistics.mean(ks):.2f}", f"losing_{n}": f"{lose:.4f}",
                            f"worst_{n}": f"{min(ks):.2f}"})
            print(f"{label:<28}" + "".join(f"{c:>22}" for c in cells))
            out.append(row)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("\nfloor price changes (live -> floor):")
    for a, b in sorted(raised, key=lambda ab: ab[1]["price"] - ab[0]["price"], reverse=True):
        print(f"  {a['title'][:44]:<44} {a['price']:7.2f} -> {b['price']:7.2f}")
    print("->", OUT)


if __name__ == "__main__":
    main()
