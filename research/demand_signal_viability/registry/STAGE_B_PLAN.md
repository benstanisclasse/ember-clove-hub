# Stage B plan: demand-signal validation (frozen 2026-11-01, before any Stage B computation)

**Labels:**
- Everything is **predictive and exploratory**. Every month was already used by earlier research (Stage A §3).
- The clean test is the forward one (Stage E plan).

**Cost:** no credits, no CJ calls. Read-only on `kalodata.db`.

**Probes done before writing this plan (descriptive, no outcomes looked at):**
- Monthly top-video lists carry **no product id**, so per-product video and creator signals can't be built from them.
- The product-detail sample has ~84 products a month, with only 16 products in more than one month. So creator and
  video counts have **no per-product history**.
- **Result:** video, creator, review and supplier signals are **inventoried but not testable as leading indicators** here.

## B1. Universe ("could have been discovered early")

**Who is in it:** at each month m, every product that is **not in its category's top 500** but is visible in either:
- (a) the category's ranks 501-1,000 (`top_deep` pages 6-10), or
- (b) Kalodata's riser list, positions 1-200 (`risers`).

**Coverage:**
- **Categories:** all 28, Virtual Products excluded.
- **Months:** m = 2025-11 … 2026-09. Features need m−1, and October 2025 is never a growth base (Phase A).

**Coverage measure, also reported:** the share of all next-month top-500 entrants that were in this universe at m. The
rest were invisible, and **are not counted as misses of any method**. They are reported as the data's ceiling.

## B2. Outcomes

The top-500 lists are complete (5 full pages), so absence means "not in the top 500".

| | Outcome | Test months |
|---|---|---|
| **S1** | in the category top 500 at m+1 | 2026-01 … 2026-08 |
| **S2** | in the category top 500 at m+1, m+2 **and** m+3 | 2026-01 … 2026-06 |

## B3. Signals, each computed only from data at ≤ m

| Family | Signal | Definition |
|---|---|---|
| Transaction level | `log_rev_cut` | log(revenue / category 500th-place revenue) |
| | `log_units` | log units |
| | `band_rank_pct` | (rank − 500)/500; missing for risers outside the band, with an `in_band` flag |
| Momentum | `mom_g` | ln(rev_m / rev_m−1) if seen in any list at m−1, else 0, with `seen_p1` |
| | `accel` | mom_g − previous mom_g, needs m−2; with a missing flag |
| | `up2` | positive growth in each of the last 2 months |
| | `kalo_g` | Kalodata growth rate, signed log |
| Kalodata riser list | `riser_pos` | position 1-200; missing means "not a riser" (flag) |
| | `prev_riser` | was a riser at m−1 |
| Channel | `video_sh`, `live_sh` | video and live revenue share (showcase = remainder) |
| Price | `log_asp`, `asp_rel` | log ASP; ASP relative to the category top-500 median |
| | `asp_chg` | ln(ASP_m / ASP_m−1), with a missing flag |
| Lifecycle | `age` | months since launch, capped at 36 |
| | `was_top_p1` | in the top 500 at m−1 (a fallen product) |
| Category | `cat_growth` | category top-500 revenue m / m−1 |

**Not testable here, inventoried only:**
- video counts, creator counts and creator concentration;
- reviews and complaint themes;
- attributes;
- CJ supply, cost and stock.

## B4. Discovery methods

Each method gives a score at m; higher means flagged first.

| Method | Score |
|---|---|
| **A Revenue** | `log_rev_cut` |
| **B Growth** | `mom_g` among products seen at m−1; unseen products ranked last |
| **C Kalodata fast-risers** | riser-list order (`−riser_pos`); non-risers ranked last, then by revenue |
| **D Momentum** | z(`log_rev_cut`) + z(`mom_g`), with z-scores taken within category-month |
| **E Existing model** | the break-in model spec unchanged (`phase_c_band.BF` features, L2 logit C = 0.5), trained on this universe |
| **F Demand-signal engine** | all B3 signals: (i) L2 logit (C = 0.5) and (ii) HistGradientBoosting (same settings as Phase C M2). **F = whichever of (i)/(ii) has the higher mean catP@20 on S1 in the first 4 test months (2026-01..04)**; the reported comparison is on all test months, and on 2026-05..08 separately (less selection-affected) |
| **G Ablations** | F's logit with one family removed at a time: transaction level, momentum, riser list, channel, price, lifecycle, category |

All models are walk-forward: train on months ≤ t−h, where h = 1 for S1 and h = 3 for S2.

## B5. Metrics

**Equal alert budgets.** Every method flags its **top 10 and top 20 per category per month**, plus a global top 100 per month.

**Per method:**
- **Precision:** catP@10, catP@20 (mean over categories), P@100.
- **Recall at budget:** the share of S1/S2 successes inside the universe that were flagged. Also reported against
  **all** next-month entrants, the coverage-limited recall.
- **False positives per true positive** at catP@20.
- **PR-AUC and ROC-AUC** within the universe.
- **Calibration** (F only): Brier score vs base rate; slope.
- **Stability:** top-20 overlap between consecutive months (products present in both), and Spearman of consecutive scores.
- **Category and temporal generalisation:** per category and per month, F minus the best baseline.

**Primary comparison:** F vs the best of A-D on catP@20, for S1 and S2.
- Month-block bootstrap (2,000 draws, seed 20261101), Holm across A-E.
- **F "beats" a method** if the CI of the monthly difference excludes 0 **and** F is ahead in ≥ 2/3 of months.
- **Materiality rule:** the advantage is called **material** only if the lift over the best simple rule (A-D) is
  **≥ 5 points of catP@20 on S1 and ≥ 2 points on S2** (about 20% relative at these base rates).
  Smaller significant lifts are reported as "statistically detectable, commercially minor".

**Ablations:** ΔcatP@20 and ΔAUC (S1) for each family removed, with CIs. A family is "contributing" if its ΔAUC CI excludes 0.

## B6. Leading / coincident / lagging classification (per signal)

1. **Leading:**
   - **Test:** adding the signal to a reference logit (`log_rev_cut`, `band_rank_pct`/`in_band`, category dummies)
     raises walk-forward ΔAUC on S1.
   - **Criteria:** CI excludes 0, and positive in ≥ 2/3 of months.
   - The same test on S2 is reported too.
2. **Coincident:**
   - **When it applies:** the signal fails the leading test, but moves with same-month growth.
   - **Measure:** |Spearman(signal, `mom_g`)| ≥ 0.3 at m.
   - **Meaning:** it describes growth already visible, with nothing extra about next month.
3. **Lagging:**
   - **Applies to:** a time-varying signal whose change from m to m+1 is predicted by growth at m, and which itself
     fails the leading test.
   - **Test:** Spearman(`mom_g`_m, Δsignal_m→m+1) ≥ 0.2.
   - **Signals tested:** `video_sh`, `live_sh`, `asp`, `kalo_g`, riser membership.
4. **Unknown:** any signal not testable here (B3, "not testable").

## B7. Lead time (Part 8)

- **Successes:** products whose **first** top-500 appearance in a category (no top-500 presence in any earlier month of
  the data) is at month e, for e = 2026-02 … 2026-09.
- **Conventional discovery date:** e, the month it shows up in the bestseller list.
- **For each method at the same budget** (top 10 and top 20 per category per month), the **first flag month**
  f = the earliest t < e at which the product was in that method's flagged set. Scores are walk-forward (S1 model for E/F).
- **Lead** = e − f, in months (1 month ≈ 30 days).
- **Reported:** the share of successes flagged ≥ 1 and ≥ 2 months before e; the median and mean lead among flagged;
  the share never flagged (missed); flags per success (alert burden). Each figure is given both:
  - **(a) over successes visible at e−1 or earlier**;
  - **(b) over all successes.**
- **Comparisons:** F vs B (basic growth filter), C (Kalodata risers) and A (revenue), at an equal budget.
- **Limit:** the earliest possible flag is 2025-11, so leads are capped by the 11-month window.

## B8. Promotion vs demand (Part 10), with the signals available

1. **Price-cut growth:**
   - **Groups:** among S1 successes, products whose growth at m came with an ASP cut ≤ −10% vs those that didn't.
   - **Outcome:** S2 rate given S1, as a 2×2 with a Wilson CI.
2. **Channel of growth:** S2 rate given S1, by `video_sh` tercile, and by `live_sh` ≥ 0.5 vs < 0.5.
3. **Kalodata growth vs our growth:** whether `kalo_g` (Kalodata's own growth figure, which drives its riser list) adds
   to `mom_g`. This comes from the ablations and the leading test.

Creator and video promotion signals: not testable (no history).

## Outputs

- `_work/stage_b_results.json`
- `_work/stage_b_signal_inventory.csv`
- `_work/stage_b_lead_time.csv`
- Report: `B_DEMAND_SIGNAL_VALIDATION.md`
