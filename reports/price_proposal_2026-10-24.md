# Draft price proposal — 2026-10-24 (NOT APPLIED)

Status: **draft, awaiting approval.** Nothing has been changed in Shopify.
Data: `data/price_proposal_2026-10-24.csv` (one row per price tier).

## Goal
Each sale should leave **~$20** to pay for advertising (break-even CPA ≈ $20).

## Assumptions
- Unit costs from Shopify (`inventoryItem.unitCost`), pulled 2026-10-24.
- Payment fees 2.9% + $0.30; 5% refund allowance.
- Shipping: customers pay $8 standard under $70; orders ≥ $70 ship free, so the store absorbs ~$8 on those.
- Prices rounded up to .99.

## Proposed single-item prices

| Product | Now | Cost | Proposed | Profit now → new | × cost | Change |
|---|---|---|---|---|---|---|
| Cinnamon Pulling Oil 4 oz | $17.98 | $16.20 | **$39.99** | $0.06 → $20.33 | 2.47× | +122% |
| Cinnamon Pulling Oil 8 oz | $31.30 | $28.20 | **$52.99** | $0.33 → $20.30 | 1.88× | +69% |
| Ukiyo Gratitude Aromatherapy Blend | $28.86 | $26.00 | **$50.99** | $0.28 → $20.66 | 1.96× | +77% |
| Complete Wellness Tea Set (out of stock) | $55.23 | $49.75 | **$84.99** | $0.82 → $20.23 | 1.71× | +54% |
| Vitamin E Massage & Body Oil | $15.54 | $14.00 | **$37.99** | $0.01 → $20.69 | 2.71× | +144% |
| Pagua Bay Scent Coin | $11.10 | $10.00 | **$32.99** | −$0.08 → $20.08 | 3.30× | +197% |
| Essential Oil Diffuser – Ash | $79.02 | $71.19 | **$108.99** | **−$6.71** → $20.89 | 1.53× | +38% |
| DORSAL hoodies (both) | $52.02 | $46.87 | **$81.99** | $0.74 → $20.34 | 1.75× | +58% |
| Sweatshirts S–XL (both) | $29.96 | $27.00 | **$51.99** | $0.29 → $20.58 | 1.93× | +74% |
| Sweatshirts 2XL–3XL | $31.07 | $28.00 | **$52.99** | $0.32 → $20.50 | 1.89× | +71% |
| Tees S–XL (all three) | $16.09 | $14.49 | **$37.99** | $0.03 → $20.20 | 2.62× | +136% |
| Tees 2XL–3XL | $17.20 | $15.49 | **$38.99** | $0.05 → $20.12 | 2.52× | +127% |

## Proposed bundles (raise order value instead of single-item price)

| Bundle | Combined cost | Price | Profit |
|---|---|---|---|
| Morning Ritual — Pulling Oil 4 oz + Scent Coin | $26.20 | $50.99 | $20.46 |
| Self-Care Night — Massage Oil + Aromatherapy Blend | $40.00 | $65.99 | $20.48 |
| Calm Home — Diffuser + Aromatherapy Blend | $97.19 | $136.99 | $20.68 |
| Tee 2-pack (S–XL) | $28.98 | $53.99 | $20.44 |

## Risks to check before approving
1. **Market price.** Not yet compared with what similar products sell for elsewhere. Tees at ~$38 and the scent coin at ~$33 are likely above typical retail.
2. **Supplier apps may overwrite prices.** Syncee (and possibly the POD apps) can sync prices from a markup rule. Change the markup rule in the supplier app, or turn off price sync, or manual Shopify changes may be reverted.
3. **Diffuser currently loses money on every sale** ($79.02 crosses the $70 free-shipping line).
4. Supplier costs could be wrong (e.g., a retail price saved as cost). Spot-check one product in Syncee.
