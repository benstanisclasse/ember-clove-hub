# Profitability: costs, break-even CPA/ROAS and targets (2026-10-25, revised with EPROLO quotes)

Data: live Shopify prices and EPROLO unit costs for all 36 active products (re-checked today, unchanged). Shipping
uses **real EPROLO quotes** (EPROLO app › My Products › product detail, US, cheapest method) for P01, P02 and the
Ruched Mesh Wrap Top. For the other products it uses a rate fitted to those quotes (YANWEN Clothing Line ≈ $4.85 +
$15.45/kg), which predicts the third quote within $0.12. Full table: `data/profitability_2026-10-25.csv`
(script: `scripts/profitability_model.py`).

> Revision note: the first version used an estimated $3.50 + $10/kg. Real EPROLO shipping is **$3–5 higher per
> item**, so every break-even CPA dropped by about that much.

## How one order makes money (before ads)
```
  what the customer pays   product price + $8 shipping (orders under $70; $70+ ships free)
− product cost             EPROLO unit cost
− EPROLO shipping          real quote (P01 $15.05, P02 $13.35; YANWEN Clothing Line, 8–15 days)
− card fees                2.9% + $0.30 (Shopify Payments, Basic plan)
− refunds                  5% of price allowance
= contribution             the most you can pay TikTok for that sale and still break even (break-even CPA)
```

## The two test products
| | P01 Cable Knit Midi | P02 Turtleneck Sweater Dress |
|---|---|---|
| Customer pays | $60.99 | $52.99 |
| Product cost | $10.97 | $8.77 |
| EPROLO shipping (quote) | **$15.05** | **$13.35** |
| Fees + refund allowance | $4.72 | $4.09 |
| **Break-even CPA** | **$30.25** | **$26.78** |
| **Target CPA** (70% of break-even) | **$21.18** | **$18.75** |
| **Break-even ROAS** | **2.02** | **1.98** |
| **Target ROAS** | **2.88** | **2.83** |
| Profit per order at target | $9.08 | $8.04 |
| Margin before ads | 50% | 51% |

Store rule of thumb: **break-even ROAS ≈ 2.0, target ROAS ≈ 2.8–2.9.**

## Bigger orders
| Basket | Customer pays | Break-even CPA (one parcel) | If EPROLO ships separately |
|---|---|---|---|
| 1 × P02 | $52.99 | $26.78 | – |
| 2 × P02 (ships free) | $89.98 | $43.18 | $38.33 |
| P01 + P02 (ships free) | $97.98 | $46.65 | $41.80 |
| P02 + Long Pleated Knit Skirt | $91.98 | $43.68 | $38.83 |

A second item adds **$11–17** of room per sale. It's still the strongest lever.

## Funnel
CPA = CPM ÷ (1,000 × CTR × click-to-purchase rate). At a $10 CPM and 1.2% CTR (cost per click about $0.83),
breaking even needs about **2.7% (P01) / 3.1% (P02)** of clicks to buy, and hitting target needs about 4%.
CPM and CTR are assumptions until our own ads have data.

Target cost per add-to-cart, assuming 30% of carts buy: **≈ $6.35 (P01), ≈ $5.63 (P02)**.

## Fixed monthly costs
| Cost | $/month | Status |
|---|---|---|
| Shopify Basic | $39.00 | Confirmed |
| EPROLO | $0 | Confirmed Free plan |
| Domain | ~$1.50 | Estimate |
| New ad videos (~8 × $4.85) | ~$38.80 | Owner-approved pace |
| Other apps | ? | Check Shopify Settings › Billing |
| **Known total** | **≈ $79** | ≈ 9–10 orders/month at target cover it |

## The 14-day test
About $700 of spend needs **≈ 25 purchases to break even** and ≈ 35 to hit target. Pause an ad after about
$30 (P01) or $27 (P02) of spend with no purchase.

## Product-level takeaways
| Group | Break-even CPA range |
|---|---|
| Dresses (5) | $26.78–31.19 |
| Skirts (4) | $27.28–28.05 |
| Knitwear (3) | $24.87–30.48 |
| Tops & bodysuits (4) | $22.35–28.89 |
| Sandals (20) | $14.61–31.28 (16 of 20 under $25) |

Shoes are heavy, so EPROLO shipping eats most of their margin. Treat sandals as add-ons only.

## What would move the numbers
1. **AOV:** a second item adds $11–17 of break-even.
2. **Price:** +$5 on P01/P02 adds about $4.60 to break-even (needs your approval).
3. **Ask EPROLO whether multi-item orders ship as one parcel.** That's worth about $5 per 2-item order.
4. Confirm checkout uses Shopify Payments (a third-party gateway adds a 2% Shopify fee).
