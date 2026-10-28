"""Per-product unit economics: contribution before ads, break-even CPA, loss limit.

Usage:
  python economics.py --import data/inbox/shopify_products_<date>.json   load/refresh products from a Shopify pull
  python economics.py                                                     recompute from products.csv and print
"""
import argparse
import sys

import hubdata as hd

APPAREL_TYPES = {"hoodies", "t-shirt", "sweat shirt", "sweatshirt", "tee"}


def compute(row, econ):
    price = hd.num(row["price_min"], 0.0)
    cost = hd.num(row["unit_cost_min"])
    shipping = hd.num(row.get("shipping_cost"))
    if shipping is None:
        shipping = hd.num(econ.get("default_shipping_cost"))
    shipping_known = shipping is not None
    shipping = shipping or 0.0

    fees = price * econ["payment_fee_pct"] + econ["payment_fee_fixed"]
    refunds = price * econ["refund_rate"]
    notes = []
    if cost is None:
        row.update(contribution="", break_even_cpa="", advertisable="unknown",
                   notes="Unit cost missing in Shopify")
        return row

    contribution = price - cost - shipping - fees - refunds
    break_even = max(contribution, 0.0)
    target = break_even * econ["target_cpa_ratio"]
    max_loss = max(econ["min_max_loss"], break_even * econ["max_loss_multiple"])
    keep = 1 - econ["payment_fee_pct"] - econ["refund_rate"]
    desired = econ["desired_break_even_cpa"]
    price_for_desired = (desired + cost + shipping + econ["payment_fee_fixed"]) / keep

    if not shipping_known:
        notes.append("shipping cost unknown (assumed $0)")
    if int(hd.num(row.get("inventory"), 0)) <= 0:
        notes.append("out of stock")
    if break_even < 10:
        advertisable = "no"
        notes.append(f"break-even CPA ${break_even:.2f} too low for paid ads")
    elif break_even < desired:
        advertisable = "marginal"
    else:
        advertisable = "yes"

    row.update(
        shipping_cost=f"{shipping:.2f}", shipping_known="yes" if shipping_known else "no",
        payment_fees=f"{fees:.2f}", refund_allowance=f"{refunds:.2f}",
        contribution=f"{contribution:.2f}", margin_pct=f"{(contribution / price * 100 if price else 0):.1f}",
        break_even_cpa=f"{break_even:.2f}", target_cpa=f"{target:.2f}", max_loss=f"{max_loss:.2f}",
        price_for_desired_cpa=f"{price_for_desired:.2f}", advertisable=advertisable,
        notes="; ".join(notes), updated_at=hd.now(),
    )
    return row


def import_products(path):
    pulled = hd.load_json(path)["products"]
    existing = {r["product_id"]: r for r in hd.read("products")}
    rows = []
    for p in pulled:
        row = existing.get(p["id"], {})
        row.update(
            product_id=p["id"], title=p["title"], vendor=p["vendor"], product_type=p["product_type"],
            handle=p["handle"], url=f"https://nkpfvz-ra.myshopify.com/products/{p['handle']}",
            group="apparel" if p["product_type"].lower() in APPAREL_TYPES else "wellness",
            inventory=p["inventory"], in_stock="yes" if p["inventory"] > 0 else "no",
            price_min=p["price_min"], price_max=p["price_max"],
            unit_cost_min=p["unit_cost_min"], unit_cost_max=p["unit_cost_max"],
            cost_source="shopify unitCost",
        )
        rows.append(row)
    hd.write("products", rows)
    hd.log(f"Imported {len(rows)} products from {path}")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--import", dest="import_path")
    args = parser.parse_args()
    econ = hd.config()["economics"]

    rows = import_products(args.import_path) if args.import_path else hd.read("products")
    if not rows:
        sys.exit("No products. Run with --import first.")
    rows = [compute(r, econ) for r in rows]
    hd.write("products", rows)

    print(f"{'Product':45} {'Price':>7} {'Cost':>7} {'Profit':>7} {'Margin':>7} {'BE CPA':>7}  {'Ads?':9} {'Price for $' + str(econ['desired_break_even_cpa']) + ' BE':>14}")
    for r in sorted(rows, key=lambda r: -hd.num(r.get("contribution"), -999)):
        print(f"{r['title'][:45]:45} {hd.num(r['price_min']):7.2f} {hd.num(r['unit_cost_min']):7.2f} "
              f"{hd.num(r['contribution']):7.2f} {r['margin_pct']:>6}% {hd.num(r['break_even_cpa']):7.2f}  "
              f"{r['advertisable']:9} {hd.num(r['price_for_desired_cpa']):14.2f}")


if __name__ == "__main__":
    main()
