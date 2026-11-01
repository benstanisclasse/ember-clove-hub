# Phase B analysis plan (frozen 2026-10-31, before any group or outcome was computed)

This file implements `DEFINITIONS_v1.md` §3 (groups) and hypothesis H-A1. It resolves the ambiguous wording in those
rules. It does not change any threshold.

## Operationalisation of the groups

- **Unit:** product × L1 category (top-500 lists, kind `top`, dedupe per v1 §1). **Window:** 2025-11 … 2026-09
  (11 months). Oct-2025 membership is used only to decide whether a product *entered* in 2025-11 (v1 §6a).
- **Observed months:** months the product is in that category's top 500. **Run:** a maximal stretch of consecutive
  observed months. **Edge:** 2025-11 (left) or 2026-09 (right).
- **Entry month e:** the first month of the product's first run whose previous month was observed absent. For e = 2025-11
  that means absent in Oct-2025.
- **F Inconclusive:** observed months = 1, or (observed months < 3 and the product is present in 2025-11 or 2026-09).
- **A:** longest run ≥ 6 and median rank over that run ≤ 200.
- **E:** longest run ≥ 6, not A, and coefficient of variation (sd/mean) of monthly revenue over that run ≤ 0.5.
- **C:** has an entry month e. The peak (highest-revenue observed month) is in e..e+2. Either peak revenue ≥ 3 × revenue
  at e, or peak rank ≤ 100. The run containing the peak ends at the peak month or the month after, and the absence must
  be observable: the month after the run's end must be ≤ 2026-09. Total observed months ≤ 4.
- **B:** has an entry month e. Within e..e+3, the minimum rank is ≤ rank(e) − 200 or ≤ 100. "Still present" is read as:
  in the top 500 at min(e+3, 2026-09), the end of its 3-month window. This is the reading that separates emerging
  winners from spikes; the literal "present at its last observed month" is always true.
- **D:** observed months ≥ 3, the OLS slope of log revenue over the last 3 observed months is < 0, and the last observed
  month is < 2026-09.
- **Order:** F → A → E → C → B → D → Unclassified. The first matching rule wins.

## H-A1 (registered in `hypotheses.csv`)

- **Comparison set:** A vs C, products with an observed entry e in 2025-11..2026-04, so both groups are reachable (A needs
  e+5 ≤ 2026-09). Secondary: B vs D with an observed entry in the same cohorts.
- **Primary features (entry month e only, so not mechanically tied to the group rules):**
  - rank percentile within the category
  - log(revenue / category cutoff at e)
  - log ASP and ASP relative to the category median at e
  - product age at e (months since launch_date)
  - video, live and showcase revenue shares
  - shop strength (number of the shop's products in the category's top 500 at e)
  - whether the product was in any list at e−1 (riser or deep)
  - Kalodata momentum at e (signed log)
- **Mechanical (reported, excluded from the support decision):** growth e → e+1, because C requires a peak within 2
  months and A requires persistence.
- **Excluded:** commission (current value only, v1 §6a).
- **Statistics:**
  - Standardised mean difference (SMD), with the sign checked in each entry cohort (2025-11..2026-04, 6 cohorts).
  - Logit A = 1 vs C = 0 on standardised primary features + category and cohort fixed effects; odds ratios with 95% CI.
  - A depth-3 decision tree for readable splits. Leave-one-cohort-out AUC (exploratory) for the logit, the tree, and
    entry-rank alone.
- **Support criterion (registered):** |SMD| ≥ 0.2 **and** the same sign in ≥ 4 of 6 cohorts (≥ 2/3), for each feature
  separately. Holm adjustment over the logit coefficients (11 features).
- **Labels:** every result is **descriptive/exploratory**. The groups use future months by construction, and no
  untouched holdout exists (Phase A §5).

## Niche-only additions (Tier 2 data; descriptive)

- For niche entrants, whether they sat in ranks 501-1,000 at e−1 (pre-entry visibility).
- Shop type (BRAND / RETAILER) and the shop's monthly rank, from the monthly shop ranks.
- Creator, video and live counts at e from the random detail sample, where the sample hits. Small n; reported only.
