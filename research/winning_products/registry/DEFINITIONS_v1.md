# Pre-registered definitions v1 (frozen 2026-10-31, before any Phase B/C outcome was examined)

Changing anything here needs a new version file (`DEFINITIONS_v2.md`) with the reason. Results computed under v1 stay
in the registry as they are.

## 1. Observation unit and panel

- **Unit:** product × L1 category × month, taken from the `top` product-rank lists (sort = revenue, ranks 1-500) of the
  29 L1 categories, months 2025-10 … 2026-09. Virtual Products has only ranks 1-100 and is excluded from rank-based
  targets.
- **Dedupe:** one row per product-month. Prefer kind `top`, then `risers`, then `risers_deep`; within a kind, the earliest
  `collected_at`. (`phase_a_integrity.py` shows duplicate rows in the same list never differ in value.)
- **Category:** the L1 category of the list the product was found in. Products listed in two L1 lists in the same month
  (174 product-months) keep both rows for category-level work and the higher-revenue row for product-level work.
- **Rank** `r(p,c,m)`: position in the revenue-sorted top-500 list. An absent product has `r > 500`. Its revenue is
  **censored**: below the list's lowest revenue `cut(c,m)`.
- **Revenue, units, ASP:** Kalodata estimates for the calendar month. **Month-over-month growth is computed by us**
  (`rev_m / rev_{m-1} − 1`). Kalodata's `revenue_growth_rate` field is **not** month-over-month (Phase A §4) and is used
  only as an undocumented "Kalodata momentum" feature.

## 2. Prediction targets (horizons h = 1, 2, 3 months ≈ 30/60/90 days; no sub-monthly targets)

| Id | Target | Definition | Observability |
|---|---|---|---|
| T1 | Retain | `r(p,c,m+h) ≤ 500` | Full (the top-500 list is a complete enumeration) |
| T2 | Climb | `r(p,c,m) > 100` and `r(p,c,m+h) ≤ 100` | Full |
| T3 | Grow 50% | `rev(m+h) ≥ 1.5·rev(m)`. If absent at m+h: 0 when `cut(c,m+h) < 1.5·rev(m)`, otherwise **censored (excluded)** | Partial; the censored share is reported |
| T4 | Sustain | in the top 500 at m+1, m+2 **and** m+3 | Full (needs m ≤ 2026-06) |
| T5 | No collapse | `rev(m+1) ≥ 0.5·rev(m)`. If absent: 0 when `cut < 0.5·rev(m)`, otherwise censored | Partial |
| T6 | Break-in | product **not** in the top 500 at m but in the riser list at m → `r ≤ 500` at m+1 (or within m+1..m+3) | Only for riser-list products (the observable "early" universe) |

The primary target for model comparison is **T1 for products ranked 101-500 at m**, plus **T2**, because both are fully
observable. T3 and T5 are secondary. T6 is reported, but its universe is small and selected by Kalodata's undocumented
growth sort.

## 3. Trajectory groups for Project A (descriptive; computed on the full 12 months)

Computed per product × category on top-500 membership and revenue. Months 2025-10 and 2026-09 are window edges, so
trajectories touching them are **censored** and flagged.

| Group | Rule (applied in this order) |
|---|---|
| F Inconclusive | Fewer than 3 observed top-500 months **and** the trajectory touches a window edge, or only 1 observed month |
| A Sustained winner | ≥ 6 consecutive top-500 months **and** median rank ≤ 200 over those months |
| E Stable seller | ≥ 6 consecutive top-500 months, not A, and the coefficient of variation of monthly revenue ≤ 0.5 |
| C Temporary viral | Enters (not present the month before), reaches its peak revenue within 2 months of entry, peak ≥ 3× its first observed month **or** peak rank ≤ 100, then absent within 2 months after the peak, and total top-500 months ≤ 4 |
| B Emerging winner | Enters after 2025-10 and improves rank by ≥ 200 places, or reaches rank ≤ 100, within 3 months of entry; still present at its last observed month or at 2026-09 |
| D Declining | ≥ 3 top-500 months, with a negative slope of log revenue over the last 3 observed months and exit before 2026-09 |
| (other) Unclassified | Everything else (reported as its own count) |

## 4. Baselines (every model must beat these on the same candidate universe)

- **B0** random ordering (expected precision = base rate)
- **B1** current revenue
- **B2** current rank-in-category (equivalent to B1 within category)
- **B3** computed MoM growth (needs m−1 observed, else ranked last)
- **B4** Kalodata momentum field
- **B5** 3-month momentum (months present + slope of log revenue)
- **B6** previously registered Hub models (from `research_runs` / `model_v2`), refit only on the allowed training months

## 5. Metrics

- **Ranking metrics:** precision@10/20/50 within each month's frozen candidate universe (and per category where n allows),
  lift over B0 and over the best baseline, average precision, and AUC.
- **Calibration:** Brier score and reliability for probability models.
- **Uncertainty:** month-block bootstrap (resampling months), 95% intervals.
- **Comparisons:** Holm correction across the pre-listed model-vs-baseline comparisons. A model is "better" only if the
  interval of its precision@50 lift over the best baseline excludes 0 **and** it beats that baseline in ≥ 2/3 of
  evaluation months.

## 6a. Data rules from Phase A (added 2026-10-31, still before any outcome was examined)

- **2025-10 is a partial month** (top-500 revenue $240M vs $716M-$1,085M in other months). It can be used for
  membership only. It is never used as a growth base month (`rev_{2025-10}`), and trajectories start at 2025-11.
- **Commission rate, launch date, SKU count and product name are current values** repeated in every month (0 of 20,038
  multi-month products show any commission change). Commission and SKU count are **not valid historical features**:
  H-B9 is downgraded to "not testable historically". Launch date is fixed by nature and stays valid.
- **The AI-video flag is 0 for every video before 2026-06**, which means unknown, not "not AI". AI analyses use 2026-06..09 only.
- **Duplicated Womenswear pulls** (2026-08/09) are removed by the dedupe rule (identical values).
- **No month is an untouched holdout** (`_work/prior_research_digest.md` §3). All of 2025-11..2026-09 is treated as
  research data. Confirmatory claims require the **forward test** (§7).

## 7. Forward-validation policy (the only clean test available)

Before any October 2026 data exists in the database, the chosen model(s) and baselines score the 2026-09 candidate
universe. The predictions are written to `registry/forward_test_2026-09.csv` with a SHA-256 hash recorded in
`registry/experiments.jsonl`. They are evaluated only after the 2026-10, 11 and 12 monthly pulls arrive (paid; owner
approval needed). Nothing is refit between freezing and evaluating.

## 6. Leakage rules

- Features for cutoff m use only rows with `month ≤ m`. Static fields are restricted to those fixed at listing time
  (launch_date, seller_id). Anything from the 2026-10-25..30 detail/video pulls of the *current* state (not month-scoped) is
  never used for m < 2026-09.
- Candidate universe at m = products present in any list at m (or, for T6, the riser list at m).
- Category thresholds (e.g. cutoff revenue) at m are allowed (known at m). Thresholds at m+h are used only to label
  censored outcomes, never as features.
