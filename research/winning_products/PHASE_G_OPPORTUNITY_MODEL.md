# Phase G: product opportunity model (2026-11-01)

**Evidence labels:**

| Part | Label |
|---|---|
| G1 strategy back-test, G2 calibration | predictive, **exploratory** (no historical month is untouched) |
| G3 | a summary of Phases B-F |
| G4 | **rule-based**: no score is validated against our own ad or Shopify results, because none exist yet |
| G5 | the clean test: a forward freeze |

**Sources:**
- Plan: `registry/PHASE_G_PLAN.md`, frozen before computing (EXP-G-000). EXP-G-000b is a label fix made before
  computing: the strategy test is H-G2, because H-G1 already meant "ad score vs our own ad results", which is not testable.
- Results: EXP-G-001.
- Script: `scripts/phase_g.py`.
- Outputs: `_work/phase_g_results.json`, `_work/phase_g_scores.csv`, `registry/forward_test_strategies_2026-09.csv`.

**Cost:** no credits, no CJ calls, no money.

## The model in one paragraph

**The model is four separate scores plus seven rejection gates, not one blended number.** The brief warns against
"arbitrary weights called predictive", and only one of the four scores can be checked against history.

| Score | What it is | Validated? |
|---|---|---|
| **Market Opportunity** (Kalodata) | Phase C's probability that a product stays in its category's top 500 for 3 more months. For products ranked 501-1,000: the break-in probability. | **Yes:** walk-forward, and calibrated (G2) |
| **Supplier Viability** (CJ) | Phase F's match score and stock confidence | No outcome to check against |
| **Advertising Suitability** | Headroom (break-even ROAS) and video-driven demand. Creator breadth would belong here but isn't pulled. | Components were supported earlier; the combination isn't validated |
| **Commercial Readiness** | Passes every gate, and the open checks are listed | Rule |

The candidates that pass are ordered by Advertising Suitability, then headroom, then Market Opportunity.

## G1. Discovery strategies, back-tested (H-G2)

**Set-up:**
- **Universe:** ranks 101-500, all 28 categories.
- **Outcome:** still in the top 500 for each of the next 3 months.
- **Test months:** 2026-03 to 2026-06.
- **Training:** each model is trained only on months ending at least 3 months before the test month.
- **Ranking:** within each strategy's eligible pool, by the Phase C model.
- **Strategies E (high contribution) and G (bundles)** can't be back-tested: CJ has no price history.

| Strategy | Who is eligible | Eligible per month | Base rate | **Top-20 hit rate** | vs the simple revenue rule in the same pool | vs F (no filter) |
|---|---|---|---|---|---|---|
| **A Emerging** | launched ≤ 3 months ago | 3,042 | 18% | **74%** | **+45 pts** [+33, +65], 4/4 months | **−19 pts** [−23, −15], 4/4 months: **supported (worse)**, Holm p < 0.001 |
| **B Proven** | in the top 500 for each of the last 3 months | 3,570 | 53% | 94% | +24 pts [+13, +41] | +1 pt [0, +4], 1/4 months: no difference |
| **C Underexploited** | categories with high newcomer survival and no dominant shops (decided month by month) | 2,200 | 42% | 93% | +14 pts [−1, +25] | 0 pts [−4, +4]: no difference |
| **D Creative-driven** | ≥ 70% of revenue from videos | 7,140 | 36% | 94% | +28 pts [+15, +45] | +1 pt [0, +4]: no difference |
| **F Sustainable** | everyone (reference) | 11,200 | 32% | **93%** | +41 pts [+33, +50] | — |

**Reading the table:**
1. **The model is what does the work. The filters don't add to it.**
   - The Phase C model's top 20 already hold 93% of the time.
   - Restricting to proven, underexploited or video-driven products changes that by 0-1 points. The top-20 hit rate
     is near its ceiling, so this test can't separate them.
   - Inside every pool, the model beats a plain revenue ranking by 14-45 points.
2. **Emerging products are a different bet.**
   - Picking the best new launches gives 74% durable products, against 93% for the best of everyone.
   - **Still worth having:** among new launches, the model is 45 points better than revenue, and new products are
     where a small store isn't up against years of reviews.
   - **The cost** is about one more fade in five picks. Treat emerging picks as higher-risk tests, not as proven demand.
3. **The categories chosen as "underexploited" depend on the month.** Pet, Baby, Automotive, Health, Food and Books
   come and go. The rule here (top-third newcomer survival, not top-third concentration) is looser than Phase E's class.
4. **H-G2:**
   - **Supported for A only**, and in the negative direction: emerging picks last less long.
   - **Not supported for B, C or D:** they select no differently from the unfiltered model.

## G2. Is the Market Opportunity probability honest? (calibration)

Pooled test-month predictions, 44,800 product-months:

| | Value |
|---|---|
| Brier score | **0.173**, against 0.217 for always predicting the base rate (20% skill) |
| Calibration slope | **0.84** (pre-registered acceptable range 0.8-1.2): reported as a probability |
| Intercept | −0.21 |

Reliability by predicted-probability decile:

| Decile | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Predicted | 3% | 8% | 13% | 19% | 25% | 33% | 42% | 52% | 65% | **81%** |
| Observed | 3% | 10% | 15% | 19% | 25% | 30% | 38% | 46% | 58% | **74%** |

**The model is somewhat over-confident at the top.** "81%" means about 74% in practice. Read Market Opportunity as a
ranking with roughly right probabilities, discounted by about 7-8 points in the top two deciles. No recalibration is fitted.

## G3. Which evidence enters the scores (from Phases B-F)

| Dimension (brief) | Evidence | Verdict | Used in |
|---|---|---|---|
| Demand strength | rank, revenue vs category cutoff | strongest single signals (C) | Market Opportunity (inside the model) |
| Demand trajectory | month-over-month growth, Kalodata momentum, acceleration | small added value: momentum +0.031 AUC; deciles monotonic (C) | inside the model only; no separate weight |
| Prediction quality | retention model | P@50 92% vs 62% for rank (C); calibrated (G2) | **Market Opportunity** |
| Video repeatability | video share of revenue | video-driven entries last, showcase/live-driven fade (B) | Advertising Suitability (b) |
| | creator and video counts | **supported**: OR 1.64-1.96 for retention (D5) | Advertising Suitability (c): **not pulled for these products** |
| | dependence on the top creator | forward test pending (D6) | not used |
| Engagement | likes, comments, engagement rate | weak or ~0 vs sales (D2) | **excluded** |
| Ad metrics | Kalodata ROAS and ad share | TikTok Shop estimates; ads buy reach, not conversion (D3) | **excluded** |
| Competitive opportunity | shop concentration | doesn't reduce newcomer survival (E2) | **excluded** as a gate |
| | newcomer survival in the category | descriptive (E1) | strategy C; context |
| | copycat saturation (title families) | invalid as measured (E3) | **excluded**; needs image matching |
| Consumer | star ratings, complaint rates | don't separate durable winners (E4) | **excluded** |
| | the category's typical complaint | descriptive (E4) | risk flag ("sizing") |
| Supplier viability | match score, stock confidence | descriptive (F) | **Supplier Viability**; gates R2, R3 |
| Contribution economics | break-even ROAS at the market price | direct economics (F) | **Advertising Suitability (a)**; gate R4 |
| Operational risk | children's, battery, safety-critical, unproven listing, factory stock only | rules | risk flags |

## G4. The 72 Phase F candidates, scored

### Rejection gates

Pre-registered; any one gate rejects the candidate. The table counts every failed gate, so most candidates appear more than once.

| Gate | Rule | Candidates failing |
|---|---|---|
| R1 | ingestible or ineligible | 2 |
| R2 | CJ match below "close substitute" | 41 |
| R3 | CJ stock confidence Low | 5 |
| R4 | no contribution, or break-even ROAS > 3.0 at the market price | 19 |
| R5 | thin demand: Sep revenue < $10,000 **or** < 300 units | 28 |
| R6 | the CJ listing uses the TikTok brand's own name | 3: FallSweet, VEVOR, and one false positive ("safe", on F02, which also fails R3 and R7) |
| R7 | US supplier-shipped listing priced ≥ 90% of the TikTok price | 9 |

The brand check only runs on close matches (score 2). Its first version also read the second title word as a brand,
which matched "deep" in "Wingslove Deep V" and wrongly rejected F10. That implementation bug was fixed before
reporting, and the fix is recorded in EXP-G-001.

**Result: 3 candidates pass every gate. All 3 are "Needs verification"; none is "Ready".**

| Order | Product | Market Opportunity (3-month hold, percentile) | Supplier Viability | Break-even ROAS (base / stress) | Video share of revenue | Advertising Suitability | Open risks |
|---|---|---|---|---|---|---|---|
| 1 | **F10** Wingslove-style deep-V push-up bra, $27.24, CJ 2608140308171601800 | 96th percentile | Provisional | **1.93** / 2.39 | 99.6% | **Strong** | sizing (40 variants); CJ listing listed only twice; factory stock only |
| 2 | **F14** square-toe buckle biker boot, $51.39, CJ 2502111246321626600 | 96th | Provisional | 2.58 / 3.68 | 98% | Weak (headroom) | sizing; factory stock only; $18 shipping per pair |
| 3 | **F05** foldable gel seat cushion, $33.89, CJ 2610140816361623600 | 99th | Provisional | 2.62 / 2.97 | 95% | Weak (headroom) | CJ listing never listed (`listedNum` 0); factory stock only |

**Rejected only by the thin-demand gate (R5):**
- **F62** kids' AI sticker printer: break-even ROAS 1.71, Strong. Rejected because it sold 159 units ($13.8k).
- **F36** trailer hitch: rejected on 262 units ($42.7k).
- **F54** abaya: rejected on 6 units ($357).

**Rejected by the brand-name gate (R6):** F09, the FallSweet bra (the CJ listing carries the brand name).

**Post-hoc sensitivity, not pre-registered:**
- If R5 used revenue only (≥ $10,000), F62 and F36 would also pass, and **F62 would rank first** (Strong, ROAS 1.71).
- F62 still carries risk flags that need work before any listing: children's product (safety certification),
  battery/electrical, unproven listing.

## G5. Forward test frozen

- **File:** `registry/forward_test_strategies_2026-09.csv`, SHA-256 `b51d30cf…9067`.
- **Contents:** the top 20 September-2026 products for each strategy A, B, C, D and F, using the **already-frozen**
  Phase C scores (no refit).
- **Registered tests:** each strategy's hit rate on the October list (T1) and on October-December (T4), compared with F.
- **Caveat:** B, C and D share 14-20 of their 20 picks with F, so the forward test can really only separate
  **emerging (A) from the rest**. A shares 0 picks with the others.

## What this means for finding products

1. **Use the Phase C model to rank demand, and skip extra market filters.** "Proven", "underexploited" and "video-driven"
   filters didn't improve on it.
2. **Run two lanes:**
   - **established demand:** about 93% of top-20 picks hold 3 months, historically;
   - **emerging launches:** about 74% hold, but the model is far better than revenue there.
3. **Reject before ranking.** The gates removed 69 of 72, and the binding gate is sourceability, not demand: 41 had no
   close CJ match.
4. **Three products pass, none is ready.** Each still needs:
   - a photo-verified match (Kalodata images, ~0.01 credit each);
   - a sample order;
   - a duty check;
   - creator and video counts (0.1 credit each);
   - a decision on the sizing risk (F10, F14).

## Checkpoint

- **Saved:**
  - this report, the plan, its amendment and EXP-G-001;
  - the script, results and score table;
  - the strategy forward file.
- **Unresolved:**
  - **H-G1** (does Advertising Suitability predict our own ad results?): untestable until we run ads on scored products;
  - creator breadth for the shortlist;
  - photo verification and samples;
  - whether R5 should count revenue only (an owner call: it decides F62);
  - bundles (strategy G), not built.
- **Phase H (final commercial shortlist and implementation plan) is ready.**
  - It can be written from local data.
  - The verification steps it will recommend all need approval: about 0.07 credits for images and 0.3 for creator
    counts on the 3 passing products (0.5 for all 5 if F62 and F36 are added), plus sample orders.
