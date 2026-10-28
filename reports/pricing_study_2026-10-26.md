# Pricing study (2026-10-26)

Question from the owner: does **price = $20 CPA + shipping + item cost** make sense?

Data: every active product (92: 81 Ember & Clove listings, 11 not yet tidied), live prices, EPROLO unit costs and
weights from a Shopify export today. Each product is priced on its most expensive variant to source. EPROLO
shipping uses the real quotes we have (3 products) and the YANWEN fit ($4.85 + $15.45/kg) for the rest. Full table:
`data/pricing_study_2026-10-26.csv` (script `scripts/pricing_study.py`). **No prices were changed.**

## Short answer
The formula is the right starting point (cost-plus, built from what an order really costs), but as written it
prices every product to **break even, not to profit**:

- It leaves out **card fees** (2.9% + $0.30) and **refunds/returns** (we allow 5% of price).
- It has **no profit line**: the $20 CPA is the whole margin, and it all goes to TikTok.
- It happens to make **$2–5 per order on items under $70**, only because the customer also pays our $8 shipping
  fee. Above $70 shipping is free, and the formula **loses $6–9 per order** (rose blazer dress, mock-neck dress,
  long coat, metal-toe mules, fold-over knee boots).

## Suggested formula
```
price = (item cost + EPROLO shipping + $20 CPA + $10 profit + $0.30 − shipping the customer pays × 0.971)
        ÷ (1 − 2.9% − 5%)            then round up to the next $X.99
```
In plain words: cost + shipping + CPA + profit, then add about 8% for card fees and refunds. With $8 customer
shipping on orders under $70, that comes out to roughly **cost + shipping + $24**, and over $70 roughly
**(cost + shipping + $30) ÷ 0.92**. Every product then keeps about **$10 per order after a $20 CPA**.

## What it would change
| | Now | Suggested formula |
|---|---|---|
| Products that **lose money** at a $20 CPA | **14** | 0 |
| Products that make **under $3** | 12 | 0 |
| Average kept per order after a $20 CPA | $5.85 | ≈ $10.40 |
| Prices going **up** / **down** / same | | 67 / 11 / 3 |

Biggest problems now (current price → suggested):
- **Flat sandals and slides**: $20.99–$32.99 lose $1–5 per order (e.g. Double Band Buckle Flat Sandals $20.99 → $37.99).
- **Sunglasses**: $12.56–$17.52 lose $6–9 (→ $32.99–$35.99).
- **New jewelry** (not yet tidied): $10–19 lose $6–9 (→ $31.99–$36.99).

Prices that would come **down** (they're above what the formula needs): Mock Neck Side-Pleat Mini Dress
$170.16 → $127.99, 3D Rose Blazer Mini Dress $122.32 → $99.99, Metal Toe Cap Wedge Mules $113.68 → $93.99, Long
Coat $100.04 → $88.99, plus a few dresses and the fringe/buckle boots.

## Where the formula needs judgment
1. **Cheap add-ons.** Cost-plus with a full $20 CPA turns a $1–4 necklace or sunglasses into a $32–36 item, which is
   high for the category. The ad cost is paid **once per order**, not per item. An add-on that rides along in a
   dress order doesn't need its own $20. Option: price "hero" items (the ones we advertise) with the CPA, and price
   add-ons (jewelry, sunglasses, flat slides) at cost + shipping + fees + a smaller profit, e.g. $15–25.
2. **The $70 free-shipping line.** Several formula prices land just under $70, where the customer still pays $8.
   Prices just over $70 lose that $8. Worth checking item by item near the line.
3. **$20 CPA is an assumption.** We have no TikTok purchase data yet. If real CPA comes in at $30, every price needs
   about $10 more, or bigger baskets.
4. **Shipping is estimated** for all but 3 products (YANWEN fit). Heavy shoes and boots carry $16–30 of shipping;
   real EPROLO quotes could move those prices by several dollars.
5. **Perceived value.** A formula price is a floor. A $43.99 crop top or a $91.99 boot should still be checked
   against what similar items sell for on TikTok Shop.

## Not done
No prices changed (needs your approval per product or group). Shipping quotes for shoes/boots and jewelry would
make the boot and jewelry prices firmer.
