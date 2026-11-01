# Phase F: Kalodata × CJ sourcing and contribution economics (2026-11-01)

**Evidence label:** descriptive, current snapshot.
- CJ prices, stock and freight were read on 2026-11-01. CJ keeps no price history, so nothing here describes past margins.
- **No CAC is measured.** Break-even and target CAC/ROAS show what the economics *allow* ads to cost, not what ads *would* cost.
- Kalodata ROAS (Phase D) is TikTok Shop data, not our Shopify CAC.

**Sources:**
- Plan, frozen before any candidate data was pulled: `registry/PHASE_F_PLAN.md` (EXP-F-000).
- Results: EXP-F-001.
- Scripts: `scripts/phase_f_candidates.py`, `phase_f_economics.py`, `phase_f_verify.py`.
- Data:
  - per-candidate CJ files: `_work/cj/F01..F72.json`
  - collection protocol: `_work/cj/COLLECTION_PROTOCOL.md`
  - variant economics: `_work/phase_f_variants.csv`
  - product table: `_work/phase_f_products.csv`
  - summary: `_work/phase_f_results.json`
  - transcription check: `_work/phase_f_verify.json`

**Cost and safety:**
- About 8,600 CJ API points, worked out from the documented per-call rates for 100 searches, 131 detail lookups, 31
  variant and 31 inventory calls, 138 freight quotes, and the probe and verification calls. That is against a free
  quota of 50,000 a day. The connector doesn't report a daily total.
- No Kalodata credits, no money.
- Nothing was ordered, carted, saved, listed, connected or changed on CJ. Image search was not used.

## The short answer

**Only 2 of the 72 strongest demand candidates (3%, 95% CI 1-10%) can be sourced from CJ at the observed TikTok price
with room for ads. Another 5 (7%) are marginal.**

| Class (pre-registered) | n | Share | 95% CI |
|---|---|---|---|
| **Feasible**: match ≥ 2, stock ≥ Medium, break-even ROAS ≤ 2.0, target CAC > 0 | **2** | 2.8% | 0.8-9.6% |
| **Marginal**: break-even ROAS 2.0-3.0 | **5** | 6.9% | 3.0-15.2% |
| **Not viable**: break-even ROAS > 3.0, or no contribution | 19 | 26.4% | 17.6-37.6% |
| **Not sourceable**: no close CJ match, or stock Low | 44 | 61.1% | 49.6-71.5% |
| Ineligible: ingestible supplements (see deviations) | 2 | 2.8% | |

**H-F1** ("what share of high-scoring Kalodata products can be matched to CJ at a viable contribution margin?"): **about
3%, or 10% if marginal ones are counted.** Demand evidence alone almost never turns into a sourceable, advertisable
product. That is the main finding.

The ROAS thresholds are planning heuristics, not measured CAC. For scale, the median Kalodata ad-video ROAS is 2.56
(Phase D), and that is a TikTok Shop estimate.

## Why candidates failed

### 1. Most top products aren't on CJ in a form we could sell (39 of 70 collected)

- **36** had only a substitute (score 1). **20** of those were capped because the TikTok item is a brand's own design,
  a licensed product or a patented mechanism: SHOKZ headphones, Baby Trend travel systems, Vans, Naturalizer, Meta
  glasses, a Mercedes-licensed ride-on car, Skillmatics kits, Rinseroo.
- **The other 16** had generic substitutes that differ materially: plug-in not solar, single not 5-pack, 3 L not 2.1 L,
  or a lower quality tier.
- **3** had nothing at all on CJ: a Bambu Lab 3D printer, a $720 crystal livestream lot, Jordan 4 sneakers resold via StockX.

**What this means:** the models in Phase C pick products whose demand *lasts*. Lasting demand on TikTok Shop is
largely **brand-owned demand**, which a dropshipper can't buy into by selling a lookalike.

### 2. CJ's US-warehouse stock for these products is supplier-shipped and priced at or above the TikTok price (13 matches)

Every matched product with US stock was a CJ **supplier-shipped** listing. That means a third-party US supplier (VEVOR,
for example) ships the order, the free-shipping flag is set, and the US-to-US freight quotes are **$0.00** because
postage is inside the price.

| Matched products (score 2) | n | CJ cost ÷ TikTok ASP (median) | Freight (median) | TikTok ASP (median) |
|---|---|---|---|---|
| Supplier-shipped (US) | 13 | **113%** | $0 | $104 |
| Shipped from China | 18 | **28%** | $11.57 | $32 |

- **Supplier-shipped:** these are the same brand-style products at roughly retail price. **0 of 13 were feasible.**
  Examples: a washing machine, a stair stepper, a leaf blower, cookware.
- **China-shipped:** the product is cheap, but **freight eats 38% of the price** at the median ASP. That is why a
  $20-35 item rarely works as a single-unit order with free shipping.

### 3. The price is fixed by the market, and most products need a premium we can't justify

**24 of 26** matched-and-stocked products would need a price **more than 10% above** the TikTok ASP to reach break-even
ROAS 2.0. 8 have no contribution at all at the market price.

## The 7 products that cleared or nearly cleared

**How to read this table:**
- Market price is the Kalodata Sep-2026 average selling price.
- Costs are for the median in-stock variant (the cheapest and dearest variants barely differ; see Q4).
- Shipping is the mean CJ quote to New York, Chicago and Los Angeles, using the cheapest method delivering in ≤ 12 days.
- **Not fully landed:** the quotes are DDU, and all 2,237 quoted methods showed `taxesFee` 0. Duties may still apply.

| | F62 | F10 | F09 | F54 | F14 | F05 | F36 |
|---|---|---|---|---|---|---|---|
| **Kalodata product** | Lumolands StickerPOP AI voice sticker printer (kids) | Wingslove deep-V push-up T-shirt bra | FallSweet "Add Two Cups" push-up bra | Women's open winter abaya | Dream Pairs square-toe biker boot | ComfiLife gel travel seat cushion | Rhino USA adjustable aluminium hitch |
| Category, pool | Toys, B (rank 512) | Womenswear, A (147) | Womenswear, A (116) | Muslim Fashion, B (501) | Shoes, A (187) | Textiles, A (125) | Automotive, A (163) |
| Sep revenue / units | $13.8k / 159 | $166k / 6,105 | $185k / 8,525 | **$357 / 6** | $56k / 1,095 | $46k / 1,357 | $43k / 262 |
| Prediction | break-in 0.48 | 3-month hold 0.74 | 0.76 | break-in 0.55 | 0.75 | 0.84 | 0.85 |
| CJ pid | 2107718788478218242 | 2608140308171601800 | 40D75741-13EF-4AA7-BE52-A5357B6B96A7 | 2406210635271602900 | 2502111246321626600 | 2610140816361623600 | 2096588152652988417 |
| Variants | 1 | 40 | 12 | 15 | 16 | 1 | 1 |
| Market price | $86.66 | $27.24 | $21.66 | $59.50 | $51.39 | $33.89 | $162.79 |
| CJ cost | $16.78 | $4.04 | $3.96-4.08 | $16.48 | $7.89-8.89 | $3.51 | $87.97 |
| Shipping (days) | $12.17 (5-11) | $6.60 (4-9) | $7.18 (4-9) | $14.61 (4-9) | $18.22 (4-9) | $14.45 (4-9) | $0, supplier-shipped (3-5) |
| **Contribution before ads** | **$50.56** | **$14.14** | $8.51 | $23.41 | $19.92 | $12.96 | $61.66 |
| Break-even ROAS | **1.71** | **1.93** | 2.54 | 2.54 | 2.58 | 2.62 | 2.64 |
| Target CAC ($10 profit) | $40.56 | $4.14 | **−$1.49** | $13.41 | $9.92 | $2.96 | $51.66 |
| Price for break-even ROAS 2.0 | $69.48 | $25.99 | $27.17 | $74.55 | $65.10 | $43.37 | $209.67 |
| Stress case: break-even ROAS | 1.90 | 2.39 | 3.59 | 3.97 | 3.68 | 2.97 | 2.64 |
| Fulfilment | Medium (factory stock only) | Medium (factory only) | Medium (factory only) | Medium (factory only) | Medium (1 unit CJ-owned) | Medium (factory only) | High (460 units, supplier) |
| CJ listings (`listedNum`) | 4 | **2** | 162 | 220 | 81 | 0 | 4 |
| **Class** | **Feasible** | **Feasible** | Marginal | Marginal | Marginal | Marginal | Marginal |

The stress case uses the dearest zip, 10% returns for apparel and shoes, and +30% duty on China-origin product cost.

### Risks that the economics don't capture

These feed into Phase G.

- **F62 sticker printer:** the best economics, but it's a **children's electronic product**. That brings children's product
  safety certification and a battery-shipping line ("Super Pure Electricity"). It is also a close imitation of a
  newly launched brand product (Lumolands, launched 2026-09-03). The collector judged it generic, since several
  identical kids' AI printers are on CJ, but **this is a judgement call**. Demand is new and small ($13.8k).
- **F10 plunge bra:** a real margin at the market price. Bras are, however, the size-and-fit category (Phase E sizing
  complaints), it comes in 40 size/colour variants, and the CJ listing has only been listed twice: unproven supplier.
- **F09 FallSweet bra:** the CJ listing **uses the FallSweet brand name**, which is a trademark risk. Its target CAC is
  negative at $21.66.
- **F54 abaya:** the demand evidence is too thin to act on: 6 units in September.
- **F36 hitch:** towing equipment is safety-critical (liability), at a $163 price, sold through a supplier-shipped
  listing. Rhino USA's design is copied by several CJ suppliers. That is also a judgement call.
- **Every China-shipped item** relies on **factory-reported stock**. None has meaningful CJ-owned stock, so fulfilment
  confidence is Medium at best. Phase F does not treat high factory stock as proof that orders will ship.

### Sensitivity to the judgement-call scores (added after the results; not pre-registered)

If F36 and F62 are treated as a brand's own designs (score 1), the result is **1 feasible (F10) and 4 marginal**. The
headline doesn't change.

## Descriptive questions (pre-registered; small n, no significance claims)

| | Finding |
|---|---|
| **Q1. Does feasibility rise with price?** | Not clearly, among the 26 matched-and-stocked products. Spearman ASP vs contribution ρ = +0.09. The feasible share by ASP tercile ($18-32, $32-57, $57-163) is 11%, 0%, 11%. Higher-ASP products matched more often to supplier-shipped listings, priced near retail, so the extra price did not become margin. |
| **Q2. Retainers (pool A) vs break-ins (pool B)** | A: 1 feasible + 4 marginal of 48. B: 1 + 1 of 24. No meaningful difference. |
| **Q3. Are cheap supplier products poorer matches?** | **Not testable as designed.** CJ variant costs were collected only for score-2 matches, so cost can't be compared across match scores. |
| **Q4. Product-level vs variant-level price** | Variants of one CJ product are almost always priced the same: the median contribution spread across variants is $0. The cheapest variant overstated the median by more than $2 in only 1 of 26 products. This is unlike the October picking sheet's dearest-variant shortcut, which was conservative and right. |
| **Q5. US warehouse vs China** | 9 of 26 matched-and-stocked products used US stock (3-5 days, $0 freight because supplier-shipped). The other 17 shipped from China (4-11 days, median $11.41 per order). |

## Data quality

- **Transcription check (pre-registered):**
  - **Sample:** 7 of the 31 score-2 products, chosen with seed 20261101: F07, F14, F25, F26, F31, F49, F66.
  - **Method:** an independent agent re-queried them, working only from their ids. A script compared the results with the collector files.
  - **Result: 7/7 passed.** Every variant price and weight matched exactly, every method and fee in the matched freight
    quote matched exactly, and stock was within ±5%.
- **Two CJ endpoints disagree on the "suggested sell price"** for the same variants. `get_product_variants` returns the
  cost, while `get_product_detail` gives a much higher number: for the hitch, $831.32 against a cost of $87.97.
  **Neither "suggested" price was used.** We price at the TikTok market ASP.
- **Rate limits:** with six collectors running, 12 of the 70 candidate files logged hits on the CJ limit ("Too Many
  Requests, QPS limit is 1 time/1second").
  - All but two recovered on the one allowed retry.
  - F34's search needed a third attempt, which breaks the one-retry rule.
  - For F01, one alternative's detail failed twice and was skipped.
  - **The account's practical limit is 1 request per second for all calls**, not only freight. Future collection should use one collector at a time, or a direct API client
  with a rate limiter.

## What this means for finding products

1. **Start from demand, but filter for "sourceable as the same product" immediately.** Most durable TikTok demand is brand-owned.
2. **Generic, unbranded, light products shipped from China are the only group that cleared.** Their weak point is
   freight: about $6-15 per single order, which needs an ASP of roughly $25 or more.
3. **Ignore CJ's US-warehouse supplier-shipped listings** for products that already sell on TikTok Shop. They are
   priced at or above the TikTok price.
4. **Multi-unit and bundle offers are the obvious lever** for the "marginal" China-shipped items. Freight per unit
   falls with quantity, and the cheap unit cost leaves room. This wasn't tested here (single-unit only, per the plan).
5. **Supplier reliability is unverified for every candidate.** Factory stock only, low listed counts, and photos not compared.
   - Before anything is listed: a photo comparison (Kalodata images, about 0.07 credit for the 7) and a **sample order**.
   - Both need owner approval.

## Checkpoint

- **Saved:**
  - this report and the plan (EXP-F-000);
  - EXP-F-001 with deviations;
  - the candidate list, the 70 CJ files and the 7 verification files;
  - variant and product economics, and the scripts.
- **Unresolved:**
  - **duties** on China-origin parcels (all quotes show 0, but the quotes are DDU);
  - **photo verification** of the 7 shortlisted matches (score 3 is impossible without it);
  - **supplier reliability** (sample orders);
  - **bundle economics**;
  - **our real CAC**, which needs our own ad results (Level 3).
- **Phase G (advertising suitability model) is ready.**
  - **Inputs:** the 7 products that cleared or nearly cleared, plus the Phase C-E evidence: creator breadth (D5),
    category entrant survival (E1), complaint themes (E4).
  - **Cost:** it can run on local data. Creator and video counts for the 7 would cost about 0.7 Kalodata credits
    (product/detail), which needs approval.
