# Test products for cycle 1 (2026-10-24)

Source: live Shopify prices, unit costs (EPROLO) and weights for all 36 active products.
Full table: `data/product_economics_2026-10-24.csv` (script: `scripts/test_product_economics.py`).

## How profit per order is calculated (single-item order, before ads)
price + $8 customer shipping (orders under $70)
− product cost − **estimated** EPROLO shipping (≈ $3.50 + $10/kg; stress case $4.50 + $13/kg)
− card fees 2.9% + $0.30 − 5% refund allowance
= **break-even ad cost per purchase (BE CPA)**. Target CPA = 70% of that.

> EPROLO's real shipping charge is not on record. Check one order's shipping in EPROLO; if it's higher than the estimate, rerun the script.

## Recommendation
| Slot | Product | Price | Cost | Est. ship | BE CPA | BE (high ship) | Target CPA | Why |
|---|---|---|---|---|---|---|---|---|
| **P01** | **Cable Knit Mock Neck Midi Dress** | $52.99 | $10.97 | $10.10 | **$35.20** | $32.22 | $24.64 | Best overall: highest affordable margin among in-season items; strong on-model street photos (already the homepage hero); 3 colors; 53,000 in stock |
| **P02** | **Turtleneck Rib Knit Sweater Dress** | $44.99 | $8.77 | $9.00 | **$31.13** | $28.48 | $21.79 | Owner's pick (2026-10-24) over the Long Pleated Knit Skirt. Clean on-model studio photos in many colors (burgundy, camel, gray, light blue); relaxed oversized fit contrasts with P01's fitted street look |
| Backup | Ruffle Slit Knit Midi Skirt | $46.99 | $8.77 | $9.80 | $32.18 | $29.29 | $22.53 | Only remaining top-ranked item with real on-model lifestyle photos (5 colors). Note: similar casual at-home styling to the pleated skirt the owner passed on |
| Not chosen | Long Pleated Knit Skirt | $46.99 | $8.11 | $10.30 | $32.34 | $29.30 | $22.64 | Owner didn't like it; one gallery photo also has Chinese text printed on it |

## Why not the others
- **Sandals and slides (ranks 16–36):** out of season for most of the US in November, and the cheaper pairs ($20–33) leave only $17–23 to spend per sale.
- **Pointed Peep Toe Stiletto Mules ($86.99):** highest dollar profit, but niche, out of season and over the $70 free-shipping line (no $8 shipping income).
- **Henley maxi dress / Striped polo sweater:** good margins ($36.52 / $35.26 break-even) but every photo is a flat lay or hanger shot, so they'd need new footage before they can carry video ads.

## What it means for the ad test
- Each sale can absorb roughly **$32–35** of ad spend before losing money; aim for **$22–25** per purchase.
- New fashion stores on TikTok often see $20–50 per purchase early on, so this is workable but tight. Expect the first 14 days to be about learning, not profit.
- Loss limit per ad: about $25–35 without a sale (the higher of $20 or one break-even CPA).
