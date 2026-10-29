"""CJ vs EPROLO (2026-10-29): would sourcing each current product from CJ Dropshipping keep more per order?

Reads data/cj_compare/products.csv (our 92 active products: price, EPROLO unit cost, weight, modelled EPROLO
shipping) and data/cj_compare/batch_*.jsonl (closest CJ match per product: CJ cost of the dearest variant and
real CJ freight quotes to the US for one item of the heaviest variant). Per order, same model as
scripts/pricing_study.py: price - cost - shipping - 2.9% - $0.30 - 5% refunds - $20 CPA, free shipping to the
customer, at today's price. CJ shipping = cheapest option delivering within 15 days.
Writes data/cj_compare/cj_vs_eprolo_2026-10-29.csv. Changes nothing anywhere.
Run: python -I scripts/cj_compare.py
"""
import csv
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pricing_study import kept  # noqa: E402

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(HUB, "data", "cj_compare")
OUT = os.path.join(DIR, "cj_vs_eprolo_2026-10-29.csv")


def main():
    ours = {int(r["n"]): r for r in csv.DictReader(open(os.path.join(DIR, "products.csv"), encoding="utf-8"))}
    cj = {}
    for path in sorted(glob.glob(os.path.join(DIR, "batch_*.jsonl"))):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                o = json.loads(line)
                cj[int(o["n"])] = o  # last row for a product wins (an agent may have retried)
    rows = []
    for n, r in sorted(ours.items()):
        price, cost, ship = float(r["price"]), float(r["unit_cost"]), float(r["eprolo_ship"])
        now = kept(price, cost, ship)
        o = cj.get(n, {})
        cj_cost, cj_ship = o.get("cj_cost_max"), o.get("ship15_price") or o.get("cheapest_price")
        usable = o.get("match") in ("high", "medium") and cj_cost and cj_ship
        alt = kept(price, float(cj_cost), float(cj_ship)) if usable else None
        rows.append(dict(
            n=n, product=r["title"], type=r["type"], price=price,
            eprolo_cost=cost, eprolo_ship=ship, eprolo_landed=round(cost + ship, 2), kept_eprolo=round(now, 2),
            match=o.get("match", "not checked"), cj_name=o.get("cj_name"), cj_url=o.get("cj_url"),
            ship_from=o.get("ship_from"), cj_cost=cj_cost, cj_ship=cj_ship,
            cj_ship_method=o.get("ship15_name") or o.get("cheapest_name"),
            cj_days=o.get("ship15_days") or o.get("cheapest_days"),
            cj_landed=round(float(cj_cost) + float(cj_ship), 2) if usable else None,
            kept_cj=round(alt, 2) if alt is not None else None,
            gain=round(alt - now, 2) if alt is not None else None,
            note=o.get("match_note") or o.get("error")))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    checked = [r for r in rows if r["match"] != "not checked"]
    usable = [r for r in rows if r["kept_cj"] is not None]
    print(f"{len(rows)} products, {len(checked)} checked on CJ, {len(usable)} with a high/medium match")
    for level in ("high", "medium", "low", "none", "not checked"):
        print(f"  {level:<12} {sum(r['match'] == level for r in rows)}")
    if not usable:
        return
    better = [r for r in usable if r["gain"] > 0.5]
    print(f"\nCJ keeps more on {len(better)} of {len(usable)} matched products "
          f"(avg gain ${statistics.mean(r['gain'] for r in usable):.2f} per order over all matched)")
    losing_now = [r for r in usable if r["kept_eprolo"] < 0]
    fixed = [r for r in losing_now if r["kept_cj"] >= 0]
    print(f"money-losers with a match: {len(losing_now)}; CJ turns {len(fixed)} of them profitable at today's price")
    print(f"\n{'product':<44}{'match':<8}{'EPROLO':>8}{'CJ':>8}{'gain':>8}  CJ landed (cost+ship, days, from)")
    for r in sorted(usable, key=lambda r: -r["gain"]):
        print(f"{r['product'][:43]:<44}{r['match']:<8}{r['kept_eprolo']:>8.2f}{r['kept_cj']:>8.2f}{r['gain']:>8.2f}"
              f"  ${r['cj_cost']}+${r['cj_ship']} ({r['cj_days']} d, {r['ship_from']}) vs ${r['eprolo_landed']}")
    print("->", OUT)


if __name__ == "__main__":
    main()
