# Phase H analysis plan: early-stage commercial shortlist (frozen 2026-11-01, before any Phase H computation)

**Owner direction:** build the final shortlist around **products that aren't yet validated**:

> "well dropshippers are looking for opportunity that isnt already validated"
>
> answer to "Build Phase H around not-yet-validated products?": "Yes, early-stage lane"

The lane is **ranks 501-1,000** (just below each category's top 500), ranked by the break-in model (H-N2, replicated
in H-N2b). Launches ≤ 3 months old are reported as a sub-lane.

**Labels:**
- **H1: predictive, exploratory.** The months were used in Phase C.
- **H2-H4: descriptive, current-snapshot sourcing.** Same CJ method as Phase F.
- **H5: rule-based shortlist.** **No ad or Shopify outcome exists**, so nothing here predicts profit.

**Cost:**
- CJ API points only (free quota). Same read-only tools and safety rules as Phase F.
- No Kalodata credits, no money.

**Probe note:** before writing this plan I checked, on Phase F's existing results, whether a "seller name appears in
the title" brand screen would help. It flags 54 of 72, including every product that cleared, so it is **not used**.
No Phase H candidate data has been looked at.

## H1. Do break-in picks last? (back-test, H-H2)

- **Data:** the band frame, built exactly as in `phase_c_band.band_frame`, for all categories with band data
  (Virtual Products excluded).
- **Model and training:** the same model (`BF` features, L2 logit, C = 0.5, trained on `enter` for months ≤ t−1).
- **Test months:** t = 2026-02 … 2026-06 (so that m+3 ≤ 2026-09).
- **Outcomes**, for a band product at month m:

  | Outcome | Definition |
  |---|---|
  | `enter` | in the top 500 at m+1 |
  | `hold3` | in the top 500 at m+1, m+2 **and** m+3 |

- **Metrics:**
  - within-category P@20, averaged over categories, for `enter` and `hold3`: model vs B1 (revenue vs cutoff) vs the base rate;
  - month-block bootstrap 95% CI for model − B1 on `hold3` (2,000 draws, seed 20261101).
- **Sub-lane:** among the model's picks, the share launched ≤ 3 months before m, and the `hold3` rate of young (age ≤ 3)
  vs older picks. Descriptive.
- **H-H2 supported if:** the model's `hold3` catP@20 ≥ 2× the `hold3` base rate **and** the model − B1 CI excludes 0
  **and** the model is ahead in ≥ 4 of 5 months.

## H2. Early-stage candidate pool

**Source:** the frozen Sep-2026 band predictions (`forward_test_band_2026-09.csv`, `enter_M1`). No refit.

**Rules, applied in this order:**
1. **Excluded categories:** Food & Beverages, Books/Magazines/Audio, Pre-Owned, Collectibles (as in Phase F).
2. **Excluded titles**, case-insensitive. It's the Phase F list plus the gaps Phase F exposed:
   - Phase F list: supplement, capsule, gummies, gummy, vitamin, probiotic, creatine, protein powder, collagen, tea,
     coffee, drink, oral, tablet, medicine, cbd, nicotine, vape, ozempic;
   - added: softgel, testosterone, powder, enzyme, prebiotic, electrolyte, keto, detox, nmn, ashwagandha, sea moss,
     shilajit, melatonin, edible.
3. **ASP ≥ $15.**
4. **Early-stage demand floor:** Sep units ≥ 100. This **replaces** Phase G's R5 (≥ 300 units / $10k), which was built
   for validated products. 100 units keeps out near-zero listings such as F54, with its 6 units.
5. **Top 4 per category by `enter_M1`.** In each category, rank 1 is the Phase F pool-B candidate, already collected.
   Its CJ file is reused, not re-collected.

**Expected size:** about 24 × 4 = 96, of which about 72 are new collections. Saved as `_work/phase_h_candidates.csv`
before any CJ call.

## H3. CJ collection

- **Method:** identical to Phase F (`_work/cj/COLLECTION_PROTOCOL.md`), covering match score 0-2, variants,
  inventory and freight to 10001, 60601 and 90001.
- **Files:** `_work/cj/H###.json`.
- **Collectors:** at most 6 at once, one call at a time each. On a rate-limit error a collector does another step before its single retry.

**Transcription check:**
- 10% of new score-2 files, at least 5, seed 20261102.
- Re-queried by an independent agent; same pass rule as Phase F.

## H4. Economics and gates

- **Economics:** Phase F's frozen rules F5-F7. That means:
  - the market price is the Kalodata Sep ASP;
  - the shipping method is the cheapest that delivers in ≤ 12 days, using the mean of the three zips;
  - the same fees, returns, duty stress and $10 target profit;
  - the median in-stock variant.
- **Gates:** Phase G's R1-R4, R6 and R7, as implemented in `phase_g.py`, including the brand-check fix. R5 is replaced by H2 rule 4.
- **Advertising Suitability:** Phase G's levels (Strong / Moderate / Weak).
- **Market Opportunity:** the `enter_M1` percentile within the Sep band.

## H5. Shortlist and implementation plan

- **Shortlist:** every early-stage candidate passing all gates, ordered as in Phase G:
  1. Advertising Suitability level
  2. then break-even ROAS
  3. then the `enter_M1` percentile
- **Also listed:** the three validated-lane survivors from Phase G (F10, F14, F05), labelled as such, for comparison
  only. They are not part of the early-stage ranking.
- **Each shortlisted product gets:**
  - the brief's "Report 6" fields;
  - its risk flags;
  - an explicit list of open verification steps, with costs:
    - Kalodata images for a photo match;
    - `product/detail` creator and video counts;
    - a CJ sample order;
    - a duty and compliance check.
- **Implementation plan:** the order of verification and the go/no-go rules before any listing or ad spend. It
  contains **no** store-specific benchmarks: the shop is closed.

## Forward

- **Already in place:** the shortlist's `enter_M1` scores are frozen in `forward_test_band_2026-09.csv`.
- **New registered test:** in the Oct-2026 sealed pull, the share of the H5 shortlist that entered the top 500,
  against the share of all H2-eligible candidates. Descriptive: one month, small n.
