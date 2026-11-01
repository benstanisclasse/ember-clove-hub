# Phase H: early-stage commercial shortlist and implementation plan (2026-11-01)

**Owner direction:** the shortlist is built around **products that aren't yet validated**:

> "well dropshippers are looking for opportunity that isnt already validated"
>
> "Yes, early-stage lane"

**Lane:** products ranked **501-1,000** in their category in September 2026, just below the top 500, ranked by the
break-in model (Phase C, H-N2, replicated in H-N2b).

**Evidence labels:**

| Part | Label |
|---|---|
| H1 back-test | predictive, exploratory |
| Sourcing and economics | current-snapshot CJ data (2026-11-01) |
| Shortlist | rule-based |

**Nothing here predicts profit.** There are no ad or store results to test against.

**Sources:**
- Plan: `registry/PHASE_H_PLAN.md`, frozen before computing (EXP-H-000).
- Results: EXP-H-001.
- Scripts: `phase_h_backtest.py`, `phase_h_candidates.py`, `phase_h_shortlist.py`, and the Phase F/G code reused unchanged
  (`phase_f_economics.py --phase h`, `scoring.py`).
- CJ files: `_work/cj/H01..H73.json`.
- Outputs: `_work/phase_h_*`.

**Cost:** about 9,300 CJ API points (free quota; worked out from documented per-call rates), no Kalodata credits, no money. Nothing was ordered, saved, listed or
changed on CJ.

## The short answer

**Five early-stage products pass every check:**
- an AI sticker printer for kids;
- a carbon-fibre steering-wheel cover;
- a cubic-zirconia eternity ring;
- a soft baby carrier;
- a zip-front gym bodysuit.

**None is ready to sell.** Each still needs a photo match, a sample and a compliance check, and two are children's products.

The early-stage lane works about as well as the validated lane: **5 of 92 candidates (5.4%, 95% CI 2.3-12.1%)** pass,
against 3 of 72 in the validated lane.

**Most early-stage picks don't become lasting sellers.** The model is about 3× better than chance at finding the ones
that do (H1).

## H1. Do break-in picks last? (H-H2: supported)

**Data:** all 28 categories with band data, Feb-Jun 2026, with walk-forward testing. "Top picks" are the model's 20 per category.

| Measure (average over categories, 5 test months) | Base rate | Revenue rule (top 20) | **Model (top 20)** |
|---|---|---|---|
| Enters the top 500 next month | 14.1% | 27.8% | **38.5%** |
| Enters **and stays** 3 months | 4.5% | 9.8% | **14.3%** |
| Stays 3 months, given it entered | — | — | 36.9% |

- **Model − revenue rule** on "enters and stays": +4.5 pts, 95% CI [+3.4, +5.6]. The model was ahead in **5 of 5 months**.
  It runs at 3.2× the base rate.
- **Young picks vs older picks:** picks launched ≤ 3 months earlier (31% of picks) last about as long as older ones:
  13.8% vs 14.4% stay 3 months.

**What it means:**
- Early-stage picks are **cheap, fast tests, not safe bets.**
- About 4 in 10 break into the top 500, and about 1 in 7 is still there 3 months later.
- For comparison, picks that are already in the top 500 last 3 months about 93% of the time (Phase G).
- So this lane is a trade: **less competition and earlier entry, in exchange for far more misses.** Test several
  products cheaply and drop the misses fast.

## H2-H4. Sourcing the early-stage pool

### The candidate pool

**Selection:** the top 4 per category by break-in score, across 24 eligible categories. Food, books, pre-owned and
collectibles were excluded, along with ingestible products, items under $15, and items selling under 100 units a month.

**92 candidates:**
- 19 already collected in Phase F;
- 71 new CJ collections;
- 2 Health items marked ineligible: an ingestible "cutting jelly" and a peptide, both missed by the term list (see deviations).

### What happened to the 92

| Outcome | n |
|---|---|
| No close CJ match (score 0-1) | **59**: 57 substitutes only and 2 with nothing at all. 24 of the 59 are branded or licensed designs CJ only imitates (Crocs, Vans, NOBULL, SanDisk, Shark, Halara, Disney…) |
| Close match but CJ stock confidence Low | 6 |
| Close match, but no contribution or break-even ROAS > 3.0 at the market price | 19 |
| CJ listing uses the TikTok brand's name | 2 (overlaps with the rows above) |
| CJ US listing priced ≥ 90% of the TikTok price | 9 (overlaps) |
| Ingestible (ineligible) | 2 |
| **Passes every gate** | **5** |

### Patterns repeated from Phase F

- **US-warehouse matches are supplier-shipped at about the TikTok price.** 16 of the 31 close matches were supplier-shipped
  US listings with $0 freight, at a **median 100% of the TikTok price**. One exception passed: the steering-wheel cover
  (H52), at 39% of the TikTok price.
- **China-shipped matches cost about 31% of the price, but freight averages $14.74** at a median price of $29.
- The early-stage lane is **just as brand-heavy** as the validated one. Branded items are probably less common than in
  the top 500, but still frequent.

### Data quality

- **Transcription check (pre-registered):** 5 new close matches (H10, H38, H44, H50, H55, seed 20261102) were
  re-queried by an independent agent. **5/5 passed**: prices, weights and freight exact, stock within ±5%.
- **Three freight quotes were re-collected by the main session** after the collectors' call and retry both hit the CJ
  rate limit (H34 Los Angeles, H43 Chicago, H47 New York). They are recorded in each file.
- **H51** stays "no match": the only lookup that failed was for an unrelated household hook.

## H5. The shortlist

**Ordering:** Advertising Suitability, then break-even ROAS, then the break-in percentile.

**What the rows mean:**
- **Prices:** the market price is the Kalodata Sep-2026 average selling price.
- **Costs:** CJ costs are today's, for the median in-stock variant.
- **Shipping:** the mean CJ quote to New York, Chicago and Los Angeles, using the cheapest method delivering in ≤ 12 days.
- **Duties are not included.** The quotes are DDU and showed $0 tax.
- **Target CAC** assumes a $10 profit per order.

| | **F62** | **H52** | **H73** | **H34** | **H38** |
|---|---|---|---|---|---|
| **Product** | Kids' AI voice sticker printer (Lumolands StickerPOP) | Carbon-fibre + leather steering-wheel cover | Cubic-zirconia eternity ring, gold-tone (PAVOI) | Ergonomic soft baby carrier, 7-35 lb (Ava & Oliver) | Women's short-sleeve zip-front gym bodysuit (Nvwaurban) |
| Kalodata ID | 1732575479740404246 | 1732547703168733686 | 1731359821791728136 | 1732025511881838835 | 1732287060618416321 |
| Category | Toys & Hobbies | Automotive & Motorcycle | Jewelry Accessories | Baby & Maternity | Sports & Outdoor |
| Sep rank / revenue / units | 512 / $13.8k / 159 | 529 / $15.1k / 569 | 509 / $4.3k / 224 | 501 / $6.3k / 103 | 549 / $39.8k / 1,517 |
| **Stage** | **new:** launched 2026-09-03 | **new:** launched 2026-08-11 | **fading:** in the top 500 Oct-Aug, peak rank 108 (Jan), down to the cut-off | new to the lists (launched 2025-12) | **stuck:** ranks 549-629 since May, flat at ~$40-45k |
| Break-in probability (percentile in the Sep band) | 0.48 (99.6th) | 0.46 (99.3rd) | 0.39 (97.5th) | 0.48 (99.6th) | 0.41 (98.3rd) |
| Video share of revenue | 96% | 98% | 41% | 100% | 99% |
| Category context (Phase E): share of newcomers still in the top 500 2 months later | 27% (competitive) | 37% (emerging, +10%) | 36% (concentrated) | 40% (concentrated, +28%) | 31% (competitive) |
| CJ pid | 2107718788478218242 | 1941421726383755265 | 59BD3B8E-D6FF-4A79-BEDA-8DE59523E8C4 | 1391003662800785408 | 2604200841181608300 |
| Variants | 1 | 1 | 15 (ring sizes) | 5 | 20 |
| CJ cost | $16.78 | $10.35 | $1.22-3.56 | $11.01 | $4.34 |
| Shipping (days) | $12.17 from China (5-11) | **$0**, US supplier-shipped (3-5) | $5.13 from China (5-11) | $14.71 from China (4-9) | $8.28 from China (4-9) |
| Market price | $86.66 | $26.49 | $19.38 | $61.58 | $26.20 |
| **Contribution before ads** | **$50.56** | $13.75 | $10.30 | $30.69 | $11.21 |
| Break-even ROAS (stress) | **1.71** (1.90) | 1.93 (1.93) | 1.88 (2.01); worst size 2.19 | 2.01 (2.31) | 2.34 (2.72) |
| Target CAC ($10 profit) | $40.56 | $3.75 | **$0.30** | $20.69 | $1.21 |
| Price for break-even ROAS 2.0 | $69.48 (below market) | $25.30 (below market) | $17.93 (below market) | $61.81 (at market) | $30.69 (+17%) |
| Fulfilment | Medium (factory stock) | **High** (460 units, supplier) | Medium (factory) | Medium (factory) | Medium (factory) |
| CJ listings (`listedNum`) | 4 | 47 | 33 | 22 | 1 |
| Advertising Suitability | **Strong** | **Strong** | Moderate | Moderate | Moderate |
| **Open risks** | children's product: CPSIA certificate; battery line; close copy of a new brand product | lowest-risk item; supplier-shipped means a third party ships | **not early-stage: a fading ex-winner**; almost no room after a $10 profit | **soft infant carriers fall under a mandatory US safety standard** (16 CFR 1226: third-party lab test and certificate); children's product | sizing; CJ listing used once; needs a price above market for ROAS 2 |

### Reading it honestly

- **H52 (steering-wheel cover) is the cleanest candidate.**
  - New (launched in August).
  - A category that lets newcomers survive.
  - US stock with 3-5 day delivery.
  - Break-even ROAS 1.93.
  - No compliance flags.
  - **Weakness:** at $26 the margin is thin. A $10 profit leaves only $3.75 for ads per order, so it suits bundles or two-packs.
- **F62 (sticker printer) has the best economics by far:** $50 per order before ads. It is a children's electronic
  product, though, so it needs a Children's Product Certificate and lab testing before it could be sold legally in the
  US. And it is a near-copy of a brand launched in September.
- **H34 (baby carrier):** good economics, but the mandatory carrier standard makes it a **poor dropshipping candidate**
  unless the CJ supplier can show a valid test report.
- **H73 (ring):** passed the gates, but it isn't an early-stage opportunity. It is a former top-500 product on its way out.
- **H38 (bodysuit):** has been stuck just below the top 500 for months. Thin margin; sizing risk.

**On the validated lane (Phase G: plunge bra, biker boot, gel cushion):**
- The plunge bra (break-even ROAS 1.93) is still the strongest of those three.
- They are kept for comparison only, not in this ranking.

## Implementation plan: before any listing or ad spend

The steps are in order, and each stage has a go/no-go rule. Costs are shown. **Every step that spends money or credits
needs the owner's approval.**

| Step | What | Cost | Go if | Stop if |
|---|---|---|---|---|
| **0. Forward check** (already approved) | Run the sealed October pull on or after 2026-11-02 (`kalodata_gaps.py forward --month 2026-10`). Score the frozen forecasts, including whether these 5 broke into the October top 500 | ~30 credits (approved monthly pull) | the product entered the top 500 or rose within ranks 501-1,000 | it fell below rank 1,000 |
| **1. Desk checks** | Kalodata product images (photo match against the CJ listing), `product/detail` creator and video counts plus the daily revenue trend, and 2 pages of reviews per product | ~0.7 credits for all 5 | photo match = same product (score 3); ≥ 5 creators selling it; no complaint theme above 20% | different product in the photo; one creator carries over half the sales |
| **2. Compliance** | **F62** and **H34**: ask the CJ supplier for test reports (CPSIA / Children's Product Certificate; 16 CFR 1226 for the carrier). Everything else: check materials and labels | free (CJ messages need the owner) | valid reports supplied | no reports: drop the product |
| **3. Samples** | One CJ sample of each survivor, to a US address | about **$86** for all 5 at today's prices (F62 $28.95, H52 $10.35, H73 ~$8.69, H34 $25.72, H38 $12.62), excluding any duties | matches the photos, acceptable quality, delivered within the quoted days | quality or "not as pictured" problems |
| **4. Offer** | Price at or below the TikTok market price. Use bundles or two-packs where the margin is thin (H52, H73, H38) | free | break-even ROAS ≤ 2.0 at the offer price | needs more than 10% above market |
| **5. Small paid test** | For each product, a hard spend cap of **one break-even CAC × 3** before the first sale (for example ~$41 for H52, ~$152 for F62), using several creatives | owner's budget | first sales at or below break-even CAC | cap reached without a sale |

**The research doesn't decide:**
- **whether** to reopen a store or run tests at all;
- **which channel** (TikTok Shop itself vs a website);
- **the test budget.**

Those are the owner's calls.

## What the whole programme found (Phases A-H)

1. **Demand prediction works; supplier economics are the bottleneck.**
   - The models rank products well:
     - top-500 retention: P@50 97% vs 85% for rank;
     - break-ins: 2.8-3.2× the base rate.
   - But only about 5% of strong candidates can be bought on CJ and sold at the market price with room for ads.
2. **Most proven TikTok demand is brand-owned.** More than half of the collected candidates had no close CJ match (56% in the validated lane, 66% early-stage), and
   a large share of those were brand designs.
3. **Early-stage picks miss far more often.** About 1 in 7 lasts 3 months, against about 9 in 10 for the best established
   products, so test cheaply and stop fast.
4. **Signals that didn't hold up:** engagement (likes, comments), Kalodata's ROAS, star ratings and shop concentration.
   **Signals that did:** revenue and rank, video-driven sales, and the number of creators selling a product.

## Checkpoint

- **Saved:** this report, the plan (EXP-H-000) and EXP-H-001; scripts; 71 new CJ files and 5 verification files; the
  shortlist and results.
- **Forward tests now frozen**, to score after the sealed October pull (≥ 2026-11-02):
  - Phase C retention and break-in;
  - Phase D creator concentration;
  - Phase E reviews;
  - Phase G strategies;
  - Phase H shortlist vs all early-stage candidates.
- **Unresolved:**
  - our real CAC (no ad data);
  - duties on China parcels;
  - photo verification;
  - supplier test reports;
  - bundles (H-H1, not built).
- **The research programme (Phases A-H) is complete.** The next step is Step 0 above, then Step 1 if the owner approves.
