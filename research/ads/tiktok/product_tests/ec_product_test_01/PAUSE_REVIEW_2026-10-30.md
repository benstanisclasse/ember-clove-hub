# Round 1: was pausing on 2026-10-30 justified?

Owner, 2026-10-30: "yes i paused it i problaby shouldnt have but the cost was runnning to high for now results. can you
do that profitablity anaysis to tell me if i wa justified." The owner paused EC_TT_ProductTest01 at about 02:39 ET on
10-30, after $246.96 of spend over about 1.5 days. Data: TikTok API lifetime per-ad report, read 2026-10-30.

## Result by product, against the stop rules in PHASE_B_EXPERIMENT_PLAN.md §5
Stop rules: stop at 1× break-even CPA with no add-to-cart, or at 2× with no purchase. TikTok-added re-cuts are counted
under the product they promote.

| Product | Spend | Clicks | Page views | Add to cart | Break-even CPA | Spend ÷ BE | Cost per click | Share of clicks that must buy to break even | Rule says |
|---|---|---|---|---|---|---|---|---|---|
| P001 Mock neck mini dress ($170) | $19.11 | 18 | 6 | 0 | $69.49 | 0.28 | $1.06 | 1.5% | keep |
| P005 Long coat ($100) | $90.01 | 39 | 26 | 1 | $40.54 | 2.22 | $2.31 | 5.7% | **stop** (2×, no sale) |
| P006 Chunky cardigan ($63) | $40.15 | 13 | 9 | 0 | $33.72 | 1.19 | $3.09 | 9.2% | **stop** (1×, no add) |
| P012 Knee boots ($91) | $40.28 | 24 | 19 | 0 | $29.90 | 1.35 | $1.68 | 5.6% | **stop** (1×, no add) |
| P013 Cable knit midi dress ($53) | $57.26 | 58 | 41 | 6 | $30.25 | 1.89 | $0.99 | 3.3% | keep (close to 2×) |
| **Total** | **$246.81** | 152 | 101 | 7 | | | $1.62 | | |

0 checkouts started and 0 purchases on TikTok; Shopify 0 orders.

## Verdict
1. **The stop rules alone support stopping 3 of 5 products.** The long coat, cardigan and boots had passed their limits.
   They would need 5.6–9.2% of clicks to buy just to break even; 1–3% is typical for a store's first visitors.
2. **They do not support stopping the whole campaign.** The cable knit dress was the only product with a signal: 6 of
   the 7 add-to-carts and $0.99 clicks. It was still inside its limit. The mini dress had spent only 0.28× its
   break-even. All 15 ads sat in one ad group (needed for the rebate), so products could not be paused one at a time.
3. **The rebate makes the pause the costly choice.** The terms said credit = (10 − purchases) ÷ 10 × spend over 7 days,
   with no pausing or edits. With 0 purchases the full 7 days (about $842) would have come back as ad credit, so more
   spend cost almost nothing. Pausing most likely forfeits the credit on the $247 already spent, plus about $600 of
   test data at no cost. This is TikTok ad credit, not cash. Caps and whether TikTok has already disqualified the
   campaign are not confirmed: check the rebate panel in Ads Manager.
4. **Zero sales after 101 page views is weak evidence on its own.** At a true 2% conversion rate, 0 sales from 101
   visitors happens about 13% of the time.
5. **Worth checking: 7 add-to-carts and 0 checkouts.** If about 40% of carts usually start checkout, 0 of 7 has about
   a 3% chance. Shopify did record 2 checkout sessions on 10-29 that TikTok shows as 0, so the checkout pixel event may
   not be reaching TikTok. Or something in the cart (price, shipping) stops people.

**Overall:** the instinct was right for three products, but pausing the whole campaign during the rebate trial was not
justified on the money. The cable knit dress lost its test, and the rebate credit is most likely gone.

Caveat: the break-even CPAs come from the 10-28 plan, which assumed customers paid $8 shipping. Free shipping started
on 10-29 at 09:30 ET.

## Correction (2026-10-30, after the owner asked for the cable knit dress economics)
With free shipping, the cable knit dress keeps **$22.48** per order, not $30.25:

| | Amount |
|---|---|
| Price | $52.99 |
| CJ cost | −$10.97 |
| Shipping | −$15.05 |
| Fees | −$1.84 |
| 5% refunds | −$2.65 |
| **Kept per order** | **$22.48** |

- **Break-even:** ROAS 2.36. At $0.99 per click, 4.4% of clicks must buy.
- **Stop rule:** its $57.26 of spend is 2.55× break-even, past the 2× stop rule ($44.97). So by the rules it was also a
  stop.
- **What that changes:** the money case for pausing rests on the rebate alone (point 3), not on the cable knit dress.
- **Its real signal is strong interest:** 6 add-to-carts from 41 page views (14.6%; 5–10% is typical) at $0.99 clicks.
  But the cart lost everyone.
- **What it would take to profit:**
  - A higher price: $59.99 keeps $28.93 and needs 3.4% of clicks to buy.
  - Cheaper shipping than the $15.05 estimate.
  - Or fixing whatever stops carts reaching checkout.

## For the necklace campaign (owner: let it run a week)
- No rebate this time, so a week at $100/day is about $700 of real money.
- PLAN.md break-even is about $47 CPA. Its stop rule would fire at about $47 with no add-to-cart, or about $94 with no
  purchase, which is 1–2 days of spend.
- Running the full week means accepting about $600 more spend than the rule allows, in exchange for TikTok leaving the
  learning phase with more data.
