"""Unit economics for the current apparel/shoe catalog and test-product shortlist (2026-10-24).

Contribution per single-item order, before ads:
  price + customer shipping (free on every order since 2026-10-29; was $8 if price < $70)
  - unit cost (Shopify unitCost, from EPROLO)
  - estimated EPROLO shipping (weight-based estimate; EPROLO's real rate is not on record)
  - card fees 2.9% of (price + customer shipping) + $0.30
  - refund allowance 5% of price
Break-even CPA = contribution. Run: python -I scripts/test_product_economics.py
"""
import csv
import os

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FREE_SHIP_AT = 70.0
# Standard shipping is free on every order since 2026-10-29 (was $8 under $70). Express ($5, US only) is
# optional and left out; it covers only part of EPROLO's USPS surcharge (~$9 on a 660 g dress).
CUSTOMER_SHIPPING = 0.0
FEE_PCT, FEE_FIXED, REFUND_PCT = 0.029, 0.30, 0.05
# EPROLO China->US standard line, rough: base + per-kg. Mid is used for ranking; high is the stress case.
SHIP_MID = (3.50, 10.0)
SHIP_HIGH = (4.50, 13.0)

# title, handle, collection, price, unit_cost, grams, total_inventory
PRODUCTS = [
    ("Ruffle Hem Mesh Mini Dress", "resort-tiered-long-sleeve-high-waist-mesh-elegant-dress", "dresses", 55.99, 17.77, 380, 1400),
    ("Belted Collared Midi Shirt Dress", "loose-fitting-waist-belt-dress", "dresses", 46.99, 11.40, 460, 2187),
    ("Turtleneck Rib Knit Sweater Dress", "high-neck-loose-woolen-dress", "dresses", 44.99, 8.77, 550, 164500),
    ("Henley Tie-Waist Rib Maxi Dress", "long-sleeve-v-neck-shawl-button-slim-fit-waist-cinching-womens-knit-long-dress", "dresses", 58.99, 14.48, 730, 4499),
    ("Long Pleated Knit Skirt", "casual-high-waist-pleated-knitted-long-skirt-for-women", "skirts", 46.99, 8.11, 680, 6500),
    ("Cable Knit Mock Neck Midi Dress", "half-high-collar-knee-length-slim-fit-woolen-dress", "dresses", 52.99, 10.97, 660, 53000),
    ("Ruffle Slit Knit Midi Skirt", "elegant-commuter-knitted-high-waist-a-line-irregular-ruffle-midi-skirt", "skirts", 46.99, 8.77, 630, 6000),
    ("Asymmetric Faux Suede Midi Skirt", "eco-friendly-suede-asymmetrical-hem-slimming-long-skirt", "skirts", 46.99, 12.58, 380, 4441),
    ("Pinstripe Pleated Mini Skirt", "preppy-tailored-stripe-pleated-a-line-button-womens-skirt", "skirts", 48.99, 13.82, 380, 4499),
    ("Malibu Beach Graphic Sweatshirt", "loose-velvet-sweatshirt", "knitwear", 41.99, 6.84, 620, 7000),
    ("Ruched Mesh Wrap V-Neck Top", "ruffled-long-sleeve-v-neck-womens-top", "tops", 34.99, 9.21, 220, 5997),
    ("Floral Rib Knit Bodysuit", "floral-knitted-long-sleeve-round-neck-slim-fit-stretchy-one-piece", "tops", 49.99, 13.90, 380, 2000),
    ("Diagonal Rib Mock Neck Bodysuit", "herringbone-texture-long-sleeve-mock-neck-knit-bodysuit-women-slim-fit-base-layer", "tops", 48.99, 13.90, 340, 2500),
    ("Textured Rib Mock Neck Bodysuit", "womens-knit-mock-neck-bodycon-jumpsuit", "tops", 45.99, 13.46, 280, 1998),
    ("Pheasant Print Crewneck Fleece Sweatshirt", "grassland-turkey-pattern-printed-round-neck-fleece-hoodie", "knitwear", 41.99, 6.84, 620, 7000),
    ("Striped Polo Collar Knit Sweater", "elegant-contrast-stripe-knit-cardigan-womens-top-with-lapel-collar-slimming-fit", "knitwear", 53.99, 12.13, 630, 16500),
    ("Paris Knit Band Flat Slides", "paris-letter-open-toe-flat-sandals", "shoes", 20.99, 3.34, 250, 3230),
    ("Toe Loop Faux Leather Slides", "toe-loop-pu-leather-flats-sandals", "shoes", 29.99, 4.51, 490, 1420),
    ("Metallic Square Toe Heeled Mules", "womens-sandals-luxury-designer-fashion-gold-chunky-sandals-elegant-square-toe-low-block-heel-sandals", "shoes", 49.99, 11.69, 900, 4243),
    ("Studded Wood-Look Block Heel Sandals", "peep-toe-block-heel-sandals", "shoes", 40.99, 5.33, 933, 3759),
    ("Rhinestone H-Band Flat Slides", "rhinestone-open-toe-flat-sandals", "shoes", 31.99, 5.69, 500, 38000),
    ("Double Band Buckle Flat Sandals", "open-toe-buckle-flat-sandals", "shoes", 20.99, 3.01, 280, 49000),
    ("Rose Accent Strappy Stiletto Sandals", "open-toe-ankle-strap-sandals", "shoes", 50.99, 10.04, 730, 44000),
    ("Double Buckle Platform Slingback Sandals", "buckle-open-toe-platform-sandals", "shoes", 41.99, 6.02, 930, 863),
    ("Pointed Peep Toe Stiletto Mules", "womens-fashion-sandals-cross-border-pointed-thin-heel-sandals-shoes", "shoes", 86.99, 30.56, 850, 37713),
    ("Butterfly Rhinestone Slingback Flats", "rhinestone-butterfly-flat-sandals", "shoes", 25.99, 4.01, 410, 48000),
    ("Clear Strap Platform Wedge Slides", "open-toe-wedge-sandals", "shoes", 32.99, 4.51, 700, 1265),
    ("Shimmer Band Platform Wedge Slides", "open-toe-wedge-sandals-1", "shoes", 28.99, 4.01, 500, 3108),
    ("Embroidered Band Espadrille Platform Slides", "open-toe-platform-sandals", "shoes", 32.99, 3.85, 750, 130000),
    ("Mesh Knit Chunky Sole Sandals", "fish-mouth-sandals-for-women-breathable-beach-sandals", "shoes", 36.99, 6.02, 460, 78500),
    ("Closed Toe Slingback Espadrille Wedges", "round-toe-wedge-sandals", "shoes", 34.99, 5.02, 470, 158000),
    ("Croc-Embossed Slingback Stiletto Sandals", "open-toe-stiletto-sandals", "shoes", 50.99, 10.04, 730, 71000),
    ("T-Strap Buckle Platform Sandals", "open-toe-platform-sandals-1", "shoes", 28.99, 4.51, 470, 44000),
    ("Braided Cord Strappy Flat Sandals", "woven-sandals-womens-flat-toe-sandals", "shoes", 33.99, 3.96, 520, 39717),
    ("Textured Peep Toe Slip-On Flats", "womens-sandals-sleeve-sandals-lightweight-shoes", "shoes", 46.99, 11.34, 653, 54955),
    ("Crisscross Stretch Strap Flat Sandals", "open-toe-flats-sandals", "shoes", 21.99, 3.51, 280, 1890),
]

# Late-October US demand: knits/dresses/skirts in season; open sandals out of season.
SEASON = {"dresses": 1.0, "skirts": 1.0, "knitwear": 1.0, "tops": 0.8, "shoes": 0.4}
# Owner-reviewed photo quality for ad video sources (on-model, lifestyle, multiple colors) — 2026-10-24 image review.
VIDEO_READY = {
    "half-high-collar-knee-length-slim-fit-woolen-dress": 1.0,
    "high-neck-loose-woolen-dress": 1.0,
    "casual-high-waist-pleated-knitted-long-skirt-for-women": 0.9,
    "elegant-commuter-knitted-high-waist-a-line-irregular-ruffle-midi-skirt": 0.9,
    "long-sleeve-v-neck-shawl-button-slim-fit-waist-cinching-womens-knit-long-dress": 0.6,
    "elegant-contrast-stripe-knit-cardigan-womens-top-with-lapel-collar-slimming-fit": 0.5,
}


def ship(grams, rate):
    return rate[0] + rate[1] * grams / 1000.0


def contribution(price, cost, grams, rate):
    cust_ship = CUSTOMER_SHIPPING if price < FREE_SHIP_AT else 0.0
    revenue = price + cust_ship
    fees = revenue * FEE_PCT + FEE_FIXED
    return revenue - cost - ship(grams, rate) - fees - price * REFUND_PCT


def main():
    rows = []
    for title, handle, coll, price, cost, grams, inv in PRODUCTS:
        be_mid = contribution(price, cost, grams, SHIP_MID)
        be_high = contribution(price, cost, grams, SHIP_HIGH)
        season = SEASON[coll]
        video = VIDEO_READY.get(handle, 0.4)
        # Score: room to learn (break-even vs $25 target), in-season demand, ready-made on-model footage.
        score = min(be_mid / 25.0, 1.4) * 0.45 + season * 0.35 + video * 0.20
        rows.append(dict(
            title=title, handle=handle, collection=coll, price=f"{price:.2f}", unit_cost=f"{cost:.2f}",
            weight_g=grams, est_eprolo_ship=f"{ship(grams, SHIP_MID):.2f}",
            break_even_cpa=f"{be_mid:.2f}", break_even_cpa_high_ship=f"{be_high:.2f}",
            margin_pct=f"{be_mid / (price + (CUSTOMER_SHIPPING if price < FREE_SHIP_AT else 0)) * 100:.0f}",
            target_cpa=f"{be_mid * 0.7:.2f}", loss_limit=f"{max(20.0, be_mid * 1.0):.2f}",
            season=season, video_ready=video, score=f"{score:.3f}", inventory=inv,
            url=f"https://emberandclove.com/products/{handle}",
        ))
    rows.sort(key=lambda r: -float(r["score"]))
    out = os.path.join(HUB, "data", "product_economics_2026-10-24.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{'#':>2} {'Product':42} {'Price':>6} {'Cost':>6} {'Ship~':>6} {'BE CPA':>7} {'BE hi':>6} {'Mgn':>4} {'Score':>6}")
    for i, r in enumerate(rows, 1):
        print(f"{i:>2} {r['title'][:42]:42} {r['price']:>6} {r['unit_cost']:>6} {r['est_eprolo_ship']:>6} "
              f"{r['break_even_cpa']:>7} {r['break_even_cpa_high_ship']:>6} {r['margin_pct']:>3}% {r['score']:>6}")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
