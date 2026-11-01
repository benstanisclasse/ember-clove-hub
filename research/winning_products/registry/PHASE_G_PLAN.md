# Phase G analysis plan: product opportunity model (frozen 2026-11-01, before any Phase G computation)

**Labels:**
- **G1-G2 (strategy back-tests, calibration): predictive, exploratory.** Every historical month was already used by
  Phases B-E, so no untouched holdout exists.
- **G3 (component evidence): summary of earlier phases.** Nothing is re-tested.
- **G4 (scoring the Phase F candidates): rule-based.** The supplier and advertising parts can't be validated against
  outcomes: there is no Shopify or ad data yet (Level 3).
- **G5 (forward freeze): the clean test.** The Sep-2026 strategy picks are frozen and scored later on the sealed Oct-Dec pulls.

**Cost:** no Kalodata credits, no CJ calls, no money. Inputs:
- `kalodata.db` (read-only)
- Phase C features and models (`features.py`, `phase_c.py`)
- the frozen forward files
- the Phase F results

**Hypotheses:**
- **H-G2 (new, registered with this plan):** "Do separate discovery strategies select products with different durable-demand rates?"
- **H-G1** (does an advertising-suitability score predict our own ad results?) stays **not testable**: there are no ad outcomes.
- **Amendment, made before any computation:** the first registration (EXP-G-000) mislabelled the strategy test as H-G1.

**No weighted sum.** The brief warns against "arbitrary weights called predictive". So the four scores are **kept
separate**, rejection rules are **mandatory gates**, and the final order is an explicit sort, not a blended number.

## G1. Discovery strategies: historical back-test (H-G2)

**Common set-up:**
- **Universe:** the top-500 panel, ranks 101-500.
- **Outcome T4:** still in the category's top 500 at m+1, m+2 and m+3. This is the "durable demand" target; Phase C's
  M1 beat rank on it.
- **Test months:** 2026-03, 04, 05, 06.
- **Training:** each test month's model is trained on months ≤ t−3 only. Same M1 spec (L2 logit, C = 0.5, `features.NUM`
  + category dummies), with no tuning.
- **Strategy-level features** are computed only from data observable at t (see C).

| Strategy | Eligibility at month t | Ranking within eligible |
|---|---|---|
| **A Emerging** | product age ≤ 3 months (launch date to t) | M1 T4 score |
| **B Proven** | in the top 500 in each of the 3 previous months (`months_top_last3` = 3) | M1 T4 score |
| **C Underexploited** | category in the top tercile of entrant 2-month survival **and** not in the top tercile of top-3-shop share. Both are computed from entries m with m+2 ≤ t (entrant survival) and from month t (concentration), over the 27 categories excluding Pre-Owned | M1 T4 score |
| **D Creative-driven** | video share of revenue ≥ 0.70 | M1 T4 score |
| **F Sustainable** | all (reference) | M1 T4 score |
| **E High-contribution** | not back-testable: CJ has no price history | (prospective only; G4) |
| **G Bundles** | not back-testable, and not built in this phase | (roadmap) |

**Metrics, per test month:**
- **P@20:** T4 rate among the strategy's top 20, pooled across categories.
- **The eligible pool's base T4 rate.**
- **The within-pool rank baseline:** B1, revenue vs cutoff, top 20.

**Comparisons**, using a month-block bootstrap (2,000 draws, seed 20261101):
1. Strategy P@20 − its own base rate: *does ranking add value inside the strategy?*
2. Strategy P@20 − B1 within the same pool: *does the model beat a simple rule there?*
3. Strategy P@20 − F's P@20: *does the eligibility filter itself select more durable products than the plain model?*

**H-G2 support rule:**
- A strategy "adds selection value" if its comparison-3 CI excludes 0, in either direction, **and** the sign holds in
  ≥ 3 of 4 months.
- Holm correction across the 4 filtered strategies (A-D).
- Strategies with fewer than 20 eligible products in a month are reported but not tested for that month.

## G2. Calibration of the market-opportunity probability

- **Data:** pool the M1 T4 test-month predictions from G1.
- **Reported:**
  - Brier score vs a base-rate forecast
  - a reliability table (deciles of predicted probability: mean predicted vs observed)
  - calibration slope and intercept (logit of observed on logit of predicted)
- **If the slope is outside 0.8-1.2:** the market-opportunity score is reported as a **within-pool percentile**, not a
  probability.
- No recalibration is fitted in this phase.

## G3. Component evidence (summary of earlier phases)

- Each candidate dimension in the brief is listed with its verdict from Phases B-F and whether it enters G4.
- **Rule:** a component enters a score only if it was supported by an earlier test, or if it is a direct economic
  quantity (cost, freight, contribution).
- Components that failed (engagement rate, title-family saturation, review stars) **are excluded**, not down-weighted.

## G4. Scoring the Phase F candidates (72)

### Mandatory rejection gates

Any one gate rejects the candidate.

| Gate | Rule |
|---|---|
| R1 | Ineligible category or ingestible (Phase F) |
| R2 | CJ match score < 2 |
| R3 | Fulfilment confidence Low |
| R4 | Contribution before ads ≤ 0, or break-even ROAS > 3.0 at the market price (median in-stock variant, base case) |
| R5 | Demand too thin: Sep-2026 revenue < $10,000 **or** units < 300 |
| R6 | The CJ listing uses the Kalodata brand's own name (trademark risk) |
| R7 | The CJ match is a supplier-shipped US listing priced ≥ 90% of the TikTok ASP. A reseller at retail price is not an opportunity |

### Four separate scores

None of them is a weighted blend.

**1. Market Opportunity (Kalodata).**
- The frozen Sep-2026 probability: `T4_M1` for pool A, `enter_M1` for pool B.
- Shown as a percentile within its pool's full Sep universe. Pools aren't comparable: one is retention, the other break-in.
- Context only: the category's entrant survival (E1) and growth.

**2. Supplier Viability (CJ).**

| Level | Rule |
|---|---|
| Verified | photo-verified match (score 3) **and** a sample order. **Nobody qualifies yet.** |
| Provisional | match 2 and fulfilment High or Medium |
| Weak | otherwise |

Also shown: `listedNum`, CJ-owned vs factory stock, origin, delivery days.

**3. Advertising Suitability.** Components:
- **(a) headroom:** break-even ROAS at the market price, base and stress;
- **(b) video-driven demand:** Sep video share of revenue (Phase B: video-driven entries last);
- **(c) creator and video breadth:** `creator_number`/`video_number` (Phase D5, supported). **Missing** for these
  products (would cost 0.1 credit each), so it is shown as "unknown", **never imputed**.

| Level | Rule |
|---|---|
| Strong | break-even ROAS ≤ 2.0 **and** video share ≥ 0.5 |
| Moderate | break-even ROAS ≤ 2.5, or ≤ 2.0 with video share < 0.5 |
| Weak | otherwise |

**4. Commercial Readiness.**

| Level | Rule |
|---|---|
| Ready | passes all gates and Supplier Viability is Verified, duties checked, compliance checked |
| Needs verification | passes all gates, but something on that list is open |
| Rejected | fails a gate |

**Risk flags**, shown but not gates:
- children's product (safety certification)
- battery or electrical line
- safety-critical use
- sizing category (apparel/shoes; Phase E)
- unproven CJ listing (`listedNum` < 10)
- factory stock only

**Final order of non-rejected candidates:**
1. Advertising Suitability level
2. then break-even ROAS, ascending
3. then the Market Opportunity percentile

The order is a reading aid, not a prediction of profit.

## G5. Forward freeze

- **File:** `registry/forward_test_strategies_2026-09.csv`.
- **Contents:** the top 20 Sep-2026 products per strategy (A, B, C, D, F), using:
  - the **already-frozen** `T4_M1` scores in `forward_test_2026-09.csv` (no refit);
  - eligibility computed from data up to 2026-09.
- **Registered tests** (scored once the Oct-Dec 2026 pulls exist):
  - **(i)** T1 (in the Oct top 500) P@20 per strategy;
  - **(ii)** T4 (in the Oct, Nov and Dec top 500) P@20 per strategy;
  - each compared with F, as in G1, but descriptive (one month).
