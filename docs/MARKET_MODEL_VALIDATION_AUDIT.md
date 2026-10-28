# Market Intelligence Engine 2.0: Model Validation Audit (Phase A)

Date: 2026-10-28. Scope: the Kalodata product-prediction models: `scripts/train_product_model.py`,
`scripts/score_breakouts.py`, `scripts/explain_breakouts.py`, `scripts/weekly_breakout_report.py` (and the
superseded `scripts/pilot_model.py`), and their reported results in `research/kalodata/MODEL_V1_2026-10-25.md`,
`BREAKOUT_EXPLAINED_2026-10-25.md` and `log.md` (2026-10-25/26 entries). Method: code read-through, read-only
queries against `research/kalodata/kalodata.db`, and a local re-analysis
(`research/kalodata/audit/model_audit_eval.py`, results in `model_audit_results.json`, about 8 minutes on this PC).
**No model, report, script or database was changed. No paid or external calls were made.**
Companion reports: `docs/MARKET_DATA_QUALITY_REPORT.md` (data quality; several findings are used here).

---

## 1. Summary verdict

**The reported numbers reproduce exactly, but the breakout models' headline AUCs mostly measure one simple fact.**
The fact is how close a product already is to its category's top-500 sales floor.

| Reported | Reproduced? | Honest reading |
|---|---|---|
| Holders 1m AUC **0.69** | Yes (0.685). Rolling forward test, 8 months: **0.681** [0.674–0.690] | **Real but modest.** It beats the best simple baseline (Kalodata growth, 0.645) by +0.03 AUC. Its top 10 per category hold at 55% vs 41% for growth alone, on a 30% base rate. This is the model's genuine contribution. |
| Holders 3m AUC **0.80** | Yes (0.797). Rolling with embargo: **0.792** [0.788–0.797] | **Real, but about obvious products.** Months already listed alone gives 0.72 and rank gives 0.71. "94% of top 10 per category stay" is 92% for the model vs 83% for "pick the 10 best sellers". Slightly inflated (+0.01) by the missing embargo. |
| Breakouts 1m AUC **0.89** | Yes (0.890). Rolling: **0.886** [0.876–0.895] | **Inflated as evidence of skill.** One number, *sales ÷ the category's 500th-place sales*, scores **0.896**. A 2-feature logistic scores 0.897. The GBM is significantly *worse* than the one-line rule in AUC (Δ −0.016 to −0.005). It ties on top-10-per-category hits (27.2% vs 27.1%). |
| Breakouts 3m AUC **0.88** | Yes (0.880; 0.874 with embargo). Rolling: **0.871** [0.864–0.880] | **Same.** Distance to floor alone scores 0.878. GBM top 10 per category hit 34.1% vs 32.9% for "the 10 highest-selling risers". Inside a sales band the AUC drops to 0.60–0.70. |
| Deep-list retrain **0.876 / 0.865** | Yes, exactly | Measured on risers 1–200 only. It says nothing about positions 201–1,000, which are what it was used to score. |
| "≥50% chance" (weekly report) | n/a | **Not a real probability.** Historically, products scored ≥50% broke in **42%** of the time (3m). A probe of deeper-list scoring gives **32%**. |

**What this means for the business:** the breakout shortlist is in effect "risers that already sell close to the
top-500 floor", filtered by price, commission and steadiness. That is a sensible screen, but a spreadsheet sort
reproduces it. The model adds no proven extra edge, and its percentages read about 1.3–1.6× too high.
The holder models do add real, if modest, information beyond momentum.

**Main problems, in order:**
1. **No honest baseline was reported.** The report compared against "growth alone" (0.51–0.52), a deliberately weak
   baseline for breakouts. `results.json` even holds `auc_sales_only` 0.81 / 0.80, which was left out of the table.
2. **Population mismatch.** Breakout models learn from riser positions 1–200 but score 1–1,000. Only **~4%** of
   products that enter a top 500 came from the previous month's riser list, so most real breakouts are outside the
   population the model can see.
3. **Overconfident probabilities**, used with hard thresholds (≥50%) in the weekly report.
4. **Point-in-time violations.** `commission_rate`, `sku_count` and `launch_date` are *current* (Oct 2026) values
   repeated into every past month. Oct 2025 is a partial week. The 3-month tasks train on labels that had not yet
   matured. Removing all of these lowers AUC by 0.003–0.026, partly because of the smaller training set. The leaks
also make commission findings untrustworthy.
5. **Reproducibility gaps.** The deep Sep riser pull now silently changes what `train_product_model.py` produces.
   No data cutoff, data hash or package versions are recorded. The commission and "small-to-big" analyses have no script.

**What is genuinely solid:** the forward-in-time framing, fixed seeds and exact reproduction. The labels avoid the
"absent = zero sales" trap (see §2). Results are stable month to month (AUC range ≤0.05) and transfer across
categories (leave-one-category-out within ±0.02 for 25 of 28). Holder 1m picks really beat momentum.

---

## 2. Task definitions as implemented

Panel (`train_product_model.build`, lines 61–116): one row per (product, month) from the monthly
`core_products_<month>_<cat>_pN` (top 500 by revenue, 5 pages) and `core_risers_<month>_<cat>_pN` (top by
`revenue_growth_rate`) pulls, Oct 2025–Sep 2026, 28 categories. Top-500 rows win over riser rows when both exist.
Duplicates by (product, month) are dropped (first kept). The Womenswear Aug/Sep double load and the 159 split-category
product-months are dropped silently this way.

| Task | Eligible population (row at month *t*) | Observation / info cutoff | Horizon | Label = 1 when | Code |
|---|---|---|---|---|---|
| holders_1m | in its category's top 500 at *t* | all of calendar month *t* (available early *t*+1) | 1 month | in the top 500 at *t*+1 **and** revenue(*t*+1) ≥ revenue(*t*) | lines 125, 87 |
| holders_3m | same | same | 3 months | in the top 500 at exactly *t*+3 (not *t*+1 or *t*+2) | line 126 |
| breakouts_1m | in the category's riser list (positions 1–200) and **not** in its top 500 at *t* | same | 1 month | in the top 500 at *t*+1 | lines 127, 133 |
| breakouts_3m | same | same | 1–3 months | in the top 500 at *t*+1, *t*+2 or *t*+3 | lines 128, 88 |

Rows are kept only if *t*+*h* ≤ Sep 2026 (`subset`, line 134).

**Absence ≠ zero sales.** The labels handle this correctly. Every non-virtual top-500 page has exactly 100 rows
(2,576 of 2,576), so "not in next month's top 500" really means "below the 500th product", not "unknown". `sales_next`
is used only when the product is in the next top 500. Absence does leak into **features**, though:
- `prev_ratio` is missing whenever the product was not in last month's lists.
- `months_seen_before` counts only appearances in the captured lists (top 500 + risers 1–200). A product selling
  $20K at rank 600 is "unseen".
- The logistic model fills missing `prev_ratio` with the training *median*, which treats "not listed" as typical.

**Practical timing issue.** Month *t* data arrives in early *t*+1, so a "1-month" forecast is about a month that is
already under way. The Sep 2026 scores were produced on 25–26 Oct, when the 1-month target month (Oct) was 80%
over. Only the 3-month horizon is genuinely forward-looking at decision time.

---

## 3. Leakage: feature by feature

All 12 months were pulled in one ~4-hour window on 25 Oct 2026 (`pulls.pulled_on` = "core"; no timestamps). Any
product-level field that Kalodata returns as a *current* attribute is therefore an Oct-2026 value.
Test used: for the 34,718 products seen in 2+ months, does the field ever change across months?

| # | Feature | Source / computation | Point-in-time? | Verdict |
|---|---|---|---|---|
| 1 | log_sales | revenue for month *t* | yes (varies by month) | OK. Kalodata estimates may have been revised after the fact; cannot test |
| 2 | log_units | units for month *t* | yes | OK |
| 3 | unit_price | per-month value (98.5% of products vary) | yes | OK |
| 4 | growth_slog | Kalodata `revenue_growth_rate` for *t* | mostly | **Not plain month-on-month** (data-quality audit: matches our own MoM for 0.7% of rows; 4,169 rows show −100% with positive revenue). **All Oct 2025 values are a placeholder 100.** Semantics unknown, so "moderate growth beats explosive" cannot be read literally |
| 5 | commission_rate | product field | **no: identical in every month for 100% of multi-month products** | **Leak (current value).** Products that later succeeded may have added affiliate commission. Removing it with log_sku costs only 0.002–0.006 AUC, but every commission conclusion is about Oct-2026 commission, not the commission at the time |
| 6–8 | video_share, live_share, shop_share | month-*t* revenue split | yes | OK |
| 9 | age_days | month end − `launch_date` | `launch_date` is constant per product (current); never after month end (0 rows) | Low risk. A relisted product would get a later date; cannot detect |
| 10 | log_sku | `sku_count` | **no: constant across months** | **Leak (current value)**, same as commission. Winners add variants |
| 11 | rank_pos | top-500 position at *t* | yes | OK. Always missing for breakout rows (no information there) |
| 12 | in_risers | riser membership at *t* | yes | OK but useless: constant 1 for every breakout row, near-constant for holders (importance 0.000–0.002) |
| 13 | riser_pos | riser position at *t* (not the label month) | yes | OK in history. **Out of range** when scoring Sep positions 201–1,000 (see §4) |
| 14 | seller_n_top500 | seller's products in the top 500, same cat-month | yes (seller_id is current but static) | OK |
| 15 | seller_share_cat | seller share of top-500 revenue, same cat-month | yes | OK |
| 16 | cat_growth | top-500 revenue sum *t* ÷ *t*−1 | yes (past only) | OK, but **Nov 2025 is inflated ~4×** by partial Oct |
| 17 | months_seen_before | count of earlier appearances (rank within product) | yes (past only) | OK. Counts appearances in the captured lists only |
| 18 | prev_ratio | revenue *t* ÷ *t*−1, when listed both months | yes | OK, but Nov 2025 is inflated by partial Oct. Missing = "not listed" |
| 19 | was_top500_prev | in the top 500 at *t*−1 | yes | OK |
| 20 | price_vs_cat | price ÷ median top-500 price, same cat-month | yes | OK |

Other leakage checks:
- **Labels.** No label uses information from the observation month or earlier. No product_details or review counts
  enter the 20-feature models. The breadth test (`breadth_test`, lines 191–212) uses month-specific creator/video
  counts but **shuffled 5-fold CV**, not a forward split. Its +0.013 AUC is not a forward estimate.
- **Survivorship.** History was pulled retrospectively. If Kalodata drops delisted products from past rankings,
  history is survivor-biased. This cannot be tested from our data.
- **Measured size of the leaks** (rolling, same test rows):

| Variant | Holders 1m | Holders 3m | Breakouts 1m | Breakouts 3m |
|---|---|---|---|---|
| GBM as built (20 features, Oct included, embargoed) | 0.681 | 0.792 | 0.886 | 0.871 |
| without commission_rate, log_sku | 0.679 | 0.789 | 0.883 | 0.866 |
| "clean": also without age_days; no Oct/Nov 2025 training rows | 0.678 | 0.787 | 0.868 | 0.845* |
| training without Oct 2025 only | 0.681 (vs 0.682) | n/a | n/a | 0.876 (vs 0.876) |
| **without embargo** (as originally built) | n/a | **0.804** | n/a | **0.878** |

\* The clean variant also loses two training months, so the Mar 2026 3-month fold trains on Dec only (0.808). The
Apr–Jun folds lose 0.010–0.017. Clean top-10-per-category hit rates: breakouts 3m 29.9% (vs 34.1% as built, and
32.9% for the one-number floor rule); holders 1m 53.3% (vs 54.5%).

Leakage inflates the AUCs only slightly, 0.003–0.026, and part of that comes from the smaller training set. Once the
current-value features and the partial month are removed, the clean breakout GBM falls further *below* the
one-number floor rule (0.845–0.868 vs 0.878–0.896). The bigger problem is interpretation: commission, variant count
and age are not what the product looked like at the time.

---

## 4. Population and selection bias

**Who the breakout probabilities apply to:** products in a category's riser list positions 1–200 (sorted by
Kalodata's growth field) that are outside its top 500. This is a narrow, growth-selected slice:

| Population | Rows | Median monthly sales | Median % of top-500 floor | Share ≥50% of floor | Median growth | Seen in an earlier list |
|---|---|---|---|---|---|---|
| Training: risers 1–200, Oct–Jun | 46,459 | $480 | 4.5% | 6.9% | +1,834% | 3.8% |
| Sep risers 1–200 | 5,188 | $650 | 4.8% | 7.1% | +1,640% | 8.3% |
| **Sep risers 201–1,000 (scored)** | **21,602** | **$226** | **1.6%** | **3.0%** | **+477%** | 6.4% |

- **The deep list is outside the training distribution.** It has lower sales, much lower growth and is further from
  the floor. Because the riser list is chosen by growth rank, growth and base size are negatively correlated inside
  it. "Moderate growth looks good" is partly a selection artifact, and deep-list products have moderate growth by
  construction. Of the 291 Sep products scored ≥50%, 238 came from the deep list.
- **Probe of out-of-range scoring.** We trained on riser positions 1–100 only, without riser features, and scored
  positions 101–200 (rolling, 3m). The AUC stayed fine (0.85), but the mean prediction was 7.1% vs 3.9% actual, and
  ≥50% scores hit only **32%** (207 rows). In-range scoring hit 30–41% in the same bins. Expect deep-list
  percentages to be roughly **2× too high**.
- **Most breakouts are invisible to the model.** Of the ~5,000 products entering a category top 500 each month,
  only **1.7–5.7% (median 4.0%)** were in that category's riser top 200 the month before (e.g. Aug: 193 of 4,784).
  The rest came from sales positions 501+ (never downloaded) or returned from earlier months. The weekly report's
  "breakout" universe is therefore a small corner of where new top-500 products come from.
- **Holders** apply to top-500 products only (14,000 a month). That population is complete and consistent over time.
- **`--scan` mode** (`weekly_breakout_report.py` lines 62–93, 434–439) labels a rolling last-30-days pull as the
  current calendar month and pulls 10 riser pages by default (positions 1–1,000). Both are outside what the models
  were trained on. Lag features then compare overlapping windows (for example, 30 days to 26 Oct vs calendar Sep).

---

## 5. Validation design

| Item | As built | Issue |
|---|---|---|
| Split | One split: train on all months before the last 3 labelled months, test on those 3 (`evaluate`, lines 153–155) | Forward in time: good. But only one origin, and the same 3 test months were looked at while choosing features and settings (no untouched holdout) |
| 3-month labels | Train rows up to Mar 2026 when testing from Apr. The Mar row's label needs Jun data | **Not mature at the first test month**: a model deployed in April could not have known it. No purge/embargo. Effect +0.006–0.012 AUC |
| Same products in train and test | Yes (a product appears in many months) | Acceptable for a forward test, but CIs must be clustered by product or month, not by row |
| Early stopping | HGB `early_stopping='auto'` uses a random 10% row split inside the training months | Validation rows share products and months with training. Minor |
| Final models | Retrained on all labelled months (line 183, `score_breakouts` line 39) | Fine, but the reported AUC is for a different (smaller) model |
| Score threshold | ≥0.5 in the weekly report | No calibration step (§7) |
| Metrics | AUC, top-10% hit, top 10 per category-month | No PR-AUC, Brier, calibration or CIs. Top-10% is pooled across 3 months and all categories |

**Re-analysis protocol used here** (`model_audit_eval.py`):
- Expanding-window **rolling origin**. For each test month *t*, train only on rows with *t*′ + *h* ≤ *t* (labels
  matured), using the same HGB settings.
- Test months: Jan–Aug 2026 for 1-month tasks (8 origins); Mar–Jun 2026 for 3-month tasks (4 origins).
- The riser panel is restricted to positions 1–200 in every month, so the deep Sep pull doesn't change history.
- CIs come from (a) a **product-cluster bootstrap** of pooled predictions (200 reps) and (b) a **month-block
  bootstrap** of month-level metrics (2,000 reps). The month bootstrap is the more honest one for "next month".

---

## 6. Re-analysis results

Precision@K uses the top K products across all categories in one month, averaged over months. "Top 10/cat" is the
hit rate of each category's 10 highest-scored products per month, the closest to how picks are used. Brier is
compared with climatology (always predicting the base rate). [brackets] = 95% CI.

### 6.1 Breakouts, 3 months (Mar–Jun 2026; 20,714 rows; 1,100 positives; base 5.3%)

| Model | AUC (month mean) [month CI] | AUC pooled [product CI] | PR-AUC | Prec@20 | Lift@20 | Top 10/cat | Top 10% | Brier (clim. 0.050) |
|---|---|---|---|---|---|---|---|---|
| **GBM, 20 features (as built)** | **0.872** [0.864–0.880] | 0.871 [0.861–0.880] | 0.285 | 0.49 | 9.3× | **34.1%** | 27.4% | 0.043 |
| Logistic, 20 features | 0.863 [0.854–0.870] | 0.863 [0.854–0.872] | 0.276 | 0.50 | 9.5× | 34.1% | 26.8% | 0.044 |
| Logistic, 2 features (sales vs floor + growth) | **0.878** [0.871–0.886] | 0.878 [0.867–0.886] | 0.281 | 0.43 | 8.0× | 33.1% | 27.9% | 0.043 |
| **Sales ÷ category's 500th-place sales (one number)** | **0.877** [0.869–0.886] | 0.878 [0.867–0.886] | 0.275 | 0.41 | 7.8× | 32.9% | 27.7% | n/a |
| Sales ($) | 0.788 | 0.788 [0.774–0.801] | 0.182 | 0.25 | 4.7× | 32.9% | 21.4% | n/a |
| Months already on lists (persistence) | 0.569 | 0.569 | 0.099 | 0.53 | 9.9× | 14.8% | 12.2% | n/a |
| Riser position | 0.614 | 0.614 | 0.094 | 0.19 | 3.5× | 14.0% | 12.3% | n/a |
| Category-relative growth | 0.607 | 0.607 | 0.094 | 0.23 | 4.2× | 14.0% | 12.2% | n/a |
| Growth (the baseline that was reported) | 0.521 | 0.520 | 0.068 | 0.15 | 2.8× | 14.0% | 8.5% | n/a |
| Momentum (list-to-list sales ratio) | 0.526 | 0.526 | 0.061 | 0.13 | 2.4× | 7.7% | 8.4% | n/a |

GBM − one-number rule, AUC: **−0.013 to +0.001** (product CI). No difference. Top-10/cat: 34.1% [31.5–37.2] vs
32.9% [30.8–35.8] (month-block CIs overlap). By month the GBM ranges 0.860 (Mar) to 0.884 (Apr); the one-number rule ranges 0.868–0.890.

### 6.2 Breakouts, 1 month (Jan–Aug 2026; 41,620 rows; 1,520 positives; base 3.7%)

| Model | AUC (month mean) [CI] | AUC pooled [product CI] | PR-AUC | Prec@20 | Top 10/cat | Top 10% | Brier (clim. 0.035) |
|---|---|---|---|---|---|---|---|
| GBM, 20 features | 0.886 [0.876–0.895] | 0.886 [0.879–0.892] | 0.240 | 0.41 | 27.2% | 20.9% | 0.031 |
| GBM without riser position (the deep-list model) | 0.867 [0.848–0.880] | 0.866 | 0.202 | 0.39 | 26.3% | 18.9% | 0.032 |
| Logistic, 20 features | 0.874 | 0.874 [0.866–0.880] | 0.220 | 0.39 | 27.3% | 20.5% | 0.032 |
| Logistic, 2 features | **0.898** [0.892–0.904] | 0.897 [0.891–0.905] | 0.242 | 0.38 | 27.2% | 21.7% | 0.031 |
| **Sales ÷ category floor** | **0.896** [0.888–0.902] | 0.896 [0.889–0.903] | 0.229 | 0.38 | 27.1% | 21.5% | n/a |
| Sales ($) | 0.807 | 0.805 | 0.150 | 0.23 | 27.1% | 16.5% | n/a |
| Riser position / cat-rel. growth / growth / momentum | 0.626 / 0.621 / 0.536 / 0.524 | | ≤0.071 | ≤0.19 | ≤10.7% | ≤8.7% | n/a |

GBM − one-number rule, AUC: **−0.016 to −0.005** (product CI). The rule is significantly better at ranking. The GBM
is marginally better at the very top (Prec@20 0.41 vs 0.38, overlapping CIs).

### 6.3 Where the breakout AUC comes from: by distance to the floor (3m, pooled)

| Sales as % of the category's 500th product | Rows | Positives | Base rate | Share of all positives | AUC GBM | AUC growth | AUC sales-vs-floor |
|---|---|---|---|---|---|---|---|
| < 10% | 14,102 | 123 | 0.9% | 11% | 0.78 | 0.49 | 0.77 |
| 10–25% | 3,402 | 234 | 6.9% | 21% | 0.68 | 0.55 | 0.60 |
| 25–50% | 1,845 | 330 | 17.9% | 30% | 0.66 | 0.53 | 0.60 |
| 50–75% | 823 | 214 | 26.0% | 20% | 0.60 | 0.54 | 0.56 |
| ≥ 75% | 542 | 199 | 36.7% | 18% | 0.68 | 0.59 | 0.54 |

68% of all risers sit below 10% of the floor and almost never break in. Separating them from the near-floor products
produces most of the 0.87. **Within a band the GBM's AUC is 0.60–0.68.** It adds real but modest ordering (+0.05
to +0.14 over the floor rule within bands), and that is the part worth keeping. The 1-month table looks the same
(within-band GBM AUC 0.63–0.70; 0.78 below 10%).

### 6.4 Holders, 1 month (Jan–Aug 2026; 111,900 rows; base 30.3%)

| Model | AUC (month mean) [CI] | AUC pooled [product CI] | PR-AUC | Prec@20 [month CI] | Top 10/cat | Top 10% | Brier (clim. 0.211) |
|---|---|---|---|---|---|---|---|
| **GBM, 20 features** | **0.682** [0.674–0.690] | 0.681 [0.677–0.684] | 0.442 | **0.63** [0.53–0.69] | **54.5%** | 50.3% | 0.195 |
| Logistic, 20 features | 0.671 | 0.671 [0.666–0.674] | 0.433 | 0.43 | 48.1% | 49.2% | 0.198 |
| Logistic, 2 features (rank + growth) | 0.635 | 0.635 | 0.389 | 0.36 | 41.0% | 40.6% | 0.203 |
| Growth | 0.644 [0.633–0.655] | 0.648 [0.644–0.651] | 0.394 | 0.46 [0.39–0.52] | 41.1% | 41.7% | n/a |
| Category-relative growth | 0.640 | 0.638 | 0.386 | 0.43 | 41.1% | 37.6% | n/a |
| Persistence / momentum | 0.565 / 0.526 | | ≤0.34 | ≤0.34 | ≤36% | ≤38% | n/a |
| Sales rank / sales | 0.498 / 0.516 | | ~0.30 | ≤0.28 | 27% | ~29% | n/a |

GBM − growth, AUC: **+0.030 to +0.036** (product CI); month-level AUCs 0.661–0.704. Rank bands show no trivial
cases: within-band AUC is 0.67–0.69 for every band from 1–100 to 451–500, and the base rate is flat at 29–31%.
**This is the model's most honest win**, though in absolute terms it is a weak predictor: half of its top 10% fail.

### 6.5 Holders, 3 months (Mar–Jun 2026; 55,953 rows; base 46.5%)

| Model | AUC (month mean) [CI] | PR-AUC | Prec@20 | Top 10/cat | Top 10% | Brier (clim. 0.249) |
|---|---|---|---|---|---|---|
| GBM (embargoed) | **0.793** [0.788–0.797] | 0.772 | 0.98 | **92.4%** | 90.3% | 0.187 |
| GBM without embargo (as built) | 0.804 [0.799–0.808] | 0.787 | 1.00 | 93.6% | 91.9% | 0.180 |
| Logistic, 20 features | 0.778 | 0.742 | 0.93 | 90.6% | 86.7% | 0.207 |
| Months already on lists | 0.724 | 0.664 | 0.94 | 70.0% | 79.3% | n/a |
| Sales rank | 0.707 | 0.666 | 0.83 | 82.8% | 77.6% | n/a |
| Momentum / sales / growth | 0.665 / 0.655 / 0.534 | | | | | n/a |

By rank band the base rate falls from 73% (1–100) to 21% (451–500), and within-band GBM AUC falls from 0.80 to 0.62.
High hit rates at the top are mostly "established best-sellers stay best-sellers". That's true and mildly useful, but
these are not products a small store can enter.

---

## 7. Calibration: are "≥50% chance" thresholds meaningful?

Reliability of the out-of-sample GBM predictions (rolling, embargoed):

| Predicted band | Breakouts 3m: n / mean pred / observed | Breakouts 1m: n / pred / obs | Holders 1m: n / pred / obs |
|---|---|---|---|
| 0–2% | 10,891 / 0.7% / 0.5% | 27,926 / 0.5% / 0.5% | 3,121 / 1.1% / 1.8% |
| 2–5% | 3,704 / 3.2% / 2.9% | 5,552 / 3.2% / 3.5% | 4,320 / 3.5% / 5.4% |
| 5–10% | 2,264 / 7.1% / 6.7% | 3,038 / 7.1% / 7.4% | 6,856 / 7.6% / 11.4% |
| 10–20% | 1,879 / 14.3% / 12.4% | 2,678 / 14.2% / 13.2% | 17,154 / 15.3% / 17.8% |
| 20–30% | 935 / 24.6% / 20.5% | 1,273 / 24.5% / 19.2% | 21,781 / 25.1% / 26.6% |
| 30–50% | 802 / 37.9% / 32.3% | 919 / 37.8% / 29.6% | 42,650 / 39.4% / 38.0% |
| **50–70%** | **217 / 57.3% / 41.0%** | **218 / 56.6% / 38.1%** | 15,035 / 56.7% / 48.8% |
| 70–100% | 22 / 74.8% / 54.5% | 16 / 74.8% / 62.5% | 983 / 74.7% / 52.6% |

- Low and middle scores are well calibrated. **Every model is overconfident above ~20%**, which is exactly where
  decisions are made. Scores ≥50% came true **42%** (breakouts 3m, n=239), **40%** (1m, n=234) and **49%**
  (holders 1m).
- On the deep list it is worse: the out-of-range probe's ≥50% scores hit **32%** (§4), and the weekly report's
  `--min-sales 3000` filter does not fix this.
- The weekly PDF's "61% chance to break into the top 500" should read "historically about 1 in 3 to 2 in 5
  products scored like this broke in." A calibration step (isotonic regression fitted on rolling out-of-sample
  predictions) is cheap and should come before any threshold.
- Brier scores beat climatology on every task (e.g. 0.043 vs 0.050), so the scores carry information. They just
  aren't probabilities at the top.

---

## 8. Categories, class imbalance and multiple testing

**Category generalization.** Leave-one-category-out (breakouts 3m, Apr–Jun test, train without that category):
25 of 28 categories move by ≤0.02 AUC. Pre-Owned drops 0.78 → 0.72; Muslim Fashion rises 0.76 → 0.83. The model
transfers because its main signal, distance to the floor, is universal, not category knowledge.

**Category performance, breakouts 3m (rolling, pooled; positives are few per category, so CIs are wide):**

| Category | Rows | Positives | AUC GBM [product CI] | AUC sales-vs-floor | Top 10/month hit |
|---|---|---|---|---|---|
| **Womenswear & Underwear** | 793 | 22 | **0.81** [0.75–0.86] | **0.87** | **10%** (base 2.8%) |
| Shoes | 740 | 41 | 0.88 [0.83–0.93] | 0.89 | 35% |
| Fashion Accessories | 783 | 29 | 0.87 [0.78–0.92] | 0.87 | 25% |
| Menswear & Underwear | 756 | 41 | 0.89 [0.85–0.92] | 0.89 | 35% |
| Kids' Fashion | 714 | 56 | 0.83 [0.76–0.88] | 0.84 | 38% |
| Muslim Fashion | 616 | 83 | 0.73 [0.68–0.79] | 0.77 | 40% |
| Pre-Owned (worst) | 512 | 40 | 0.73 [0.66–0.80] | 0.60 | 23% |
| Best: Food & Bev / Computers | ~760 | ~35 | 0.93 | 0.93 | 38–45% |

In **Womenswear**, our own category, the GBM is *below* the one-number rule. Only 4 of its 40 monthly top-10 picks
broke in. Holders 1m by category: GBM AUC 0.62–0.82. In Womenswear (0.666 vs growth 0.679) and Health (0.624 vs
0.671), the GBM is *worse than growth alone*. Its gain is an average across categories, not a per-category guarantee.

**Class imbalance.** Breakouts are 3–5% positive. No weighting or resampling is used, which is correct for keeping
scores probability-like. The AUC (0.87–0.89) hides that PR-AUC is only 0.24–0.29, and fewer than half of the
top-20 picks per month come true. Reports should lead with precision at K and lift, not AUC.

**Multiple testing and over-reading:**
- `explain_breakouts.py` reports 17 importances, 8 partial-dependence curves and per-product "reasons" from one
  model fit and one test split, with no uncertainty. The per-product effects reset one feature at a time to the
  median, so they ignore interactions. The 10 explained products were picked *after* scoring, by name.
  Statements like "moderate growth beats explosive" and "priced above category norm" are descriptive patterns of one
  fitted model on a growth-selected sample, not findings.
- **Commission analysis** (log 2026-10-25; no script) compared 5+ bands × 2 tasks × within-category cuts with no CIs.
  With product-cluster CIs (breakouts 3m): 0% → 2.8% [2.6–3.1], 0–5% → 11.3% [10.2–12.4], 5–10% → 9.0%
  [8.5–9.6], 10–15% → 6.7% [6.1–7.3], >15% → 6.4% [5.6–7.4]. The ordering is statistically clear. But commission is
  the **Oct-2026 value**, and it is confounded with category and brand. "0% commission products rarely break out"
  may partly mean "products that broke out later turned commission on". This is not evidence for any commission
  policy.
- The weekly report applies 6+ filters after the model (price, sales ≥$3K, steady, not fallen, ≤3 per category,
  commission/branding). None were validated. Their combined hit rate is unknown until October actuals arrive.

---

## 9. Uncertainty (summary)

- **Product-cluster CIs are narrow** (±0.004–0.01 AUC) because most rows are distinct products: 21,119 products in
  21,568 breakout-3m rows.
- **Month-to-month variation is the real uncertainty.** Month-block CIs are ±0.008–0.016 AUC, and precision@20 ranges
  widely. For example, holders 1m GBM Prec@20 is 0.63 [0.53–0.69], and individual months span 0.30–0.75.
- With only 4 test months for 3-month tasks and one year of history, **seasonality is untested**. No Nov–Dec
  observation month has a forward test, and the scored Sep → Oct–Dec window is exactly the holiday season, where
  breakouts are "giftable, branded, higher-priced" (`EXTRA_INSIGHTS_2026-10-26.md`).

---

## 10. Reproducibility

| Item | Status |
|---|---|
| Seeds | Fixed (`random_state=7`). Re-running reproduced every reported AUC to 3 decimals (0.685, 0.797, 0.890, 0.880; deep 0.876, 0.865) |
| Package versions | Not recorded. This PC: Python 3.13.0, scikit-learn 1.7.0, pandas 2.2.3, numpy 2.1.3. Joblib models load only with a compatible scikit-learn |
| Data cutoff / snapshot | Not recorded in `results.json` or the joblib files. The DB has no hash or version |
| **Silent input drift** | The Sep deep riser pages share the `core_risers_` name, so `load()` now returns 251,654 product-months instead of 230,052. Re-running `train_product_model.py` today would write a `scores_breakouts_2026-09.csv` with ~26,790 rows instead of 5,188 and overwrite v1 outputs in place (same `OUT` folder) |
| Model cache | `breakout_models.joblib` is keyed on the month list and feature names only. A DB change within the same months (dropping Oct, de-duplicating) would not trigger a retrain |
| Feature definitions | In code only (`build`). `panel.csv.gz` saves the built features (good) |
| Untracked analyses | Commission analysis, "small-to-big" check and seasonality notes are in `log.md` with no script |
| Version control | Hub became a git repo on 10-27, after these models were built. The model folder is outside git (databases and outputs are ignored) |

---

## 11. What to keep

- **Holders 1m model.** Modest but real edge over momentum (+0.03 AUC; top 10/cat 55% vs 41%), stable across months.
- **Forward-in-time evaluation.** Clean label definitions that use complete top-500 lists, so absence is a valid
  negative. Fixed seeds.
- **Distance to the top-500 floor** as the core breakout signal. It is simple, explainable and transfers across
  categories. Make it explicit (a "% of floor" column already exists in the weekly report) and rank by it.
- **The GBM's within-band ordering** (AUC 0.60–0.68 among products at similar distance from the floor). This is the
  only part of the breakout model that adds anything beyond a sort.
- `panel.csv.gz`, the per-pick explanation layout and the weekly `history.csv` log of picks (which make a true live
  holdout possible).

---

## 12. Prioritized fixes

| # | Fix | Evidence | Effort |
|---|---|---|---|
| 1 | **Restate the results.** Add "sales ÷ category floor" and "persistence" baselines to every report. Lead with precision@K / top-10-per-category and lift. Say plainly that breakout AUC ≈ distance to floor | §6.1–6.3 | S |
| 2 | **Calibrate before thresholding.** Fit isotonic regression on rolling out-of-sample predictions, show "historical hit rate for scores like this" in the weekly PDF, and replace "≥50% chance" | §7 | S |
| 3 | **Stop the silent drift.** Filter `pos <= 200` for risers in `load()`, or rename deep pulls `deep_risers_…`. Write outputs to versioned folders (`model_v2_<date>/`), never in place | §10 | S |
| 4 | **Drop current-value features** (`commission_rate`, `log_sku`, `age_days` from current `launch_date`) from training, or keep them only as post-model filters labelled "as of pull date". Exclude Oct 2025 and Nov lag features. Measured cost 0.003–0.026 AUC, partly from fewer training months | §3 | S |
| 5 | **Embargo and rolling origin** as the standard evaluation (protocol below) | §5 | S |
| 6 | **Validate the deep list before using it.** Free option: when Oct 2026 top-500 lists are pulled (needed anyway), check the candidates scored on 25 Oct (from Sep data) against them and publish hit rates by riser band (1–200 vs 201–1,000) and by score band. Until then, label deep-list scores "unvalidated" | §4 | S (after Oct data) |
| 7 | **Point-in-time dataset builder** (below) | §3, §10 | M |
| 8 | **Widen the breakout population.** ~96% of top-500 entrants come from outside the riser list. Sales positions 501–1,000 per category-month (5 pages; Kalodata ranks past 1,000) would capture the near-floor population directly. **Costs credits: owner decision** | §4 | M |
| 9 | **Script the ad-hoc analyses** (commission, small-to-big, seasonality) with CIs. Mark commission findings "Oct-2026 commission, observational" | §8 | S |
| 10 | **Fix `--scan`:** treat last-30-days as its own window type (no calendar-month lag features), or score only completed calendar months. Default `--riser-pages 2` until the deep list is validated | §4 | S |
| 11 | **Better targets** (later): a sales-level or rank-change target from deeper sales lists. Split holders 1m ("stays" vs "grows") into two questions | §2 | L |

### Proposed point-in-time dataset builder (fix 7)
- **Tables** (new SQLite file, e.g. `research/kalodata/pit.db`; `kalodata.db` stays the raw store):
  - `observations(product_id, cat, month, as_of_date, source_pull_id, list, pos, revenue, units, price, growth_raw,
    video/live/shop revenue)`: only values Kalodata reports *for that month*.
  - `attributes_snapshot(product_id, field, value, observed_on)`: commission, sku_count, launch_date, seller,
    name, reviews. These are dated by when we pulled them and never back-filled into earlier months.
  - `labels(product_id, cat, month, task, horizon, y, matured_on)`, where `matured_on` = end of month *t*+*h* + the
    data-availability lag (≈5 days).
  - `features(product_id, month, feature_version, …)`, built only from `observations` with month ≤ *t* and
    `attributes_snapshot.observed_on` ≤ as-of date.
  - `manifest(run_id, created_at, git_commit, db_sha256, pull_ids, data_cutoff, package_versions, feature_version)`.
- **Rules:**
  - Each month's population is defined by a fixed list spec (top 500; risers 1–200), whatever was pulled later.
  - Partial months are flagged (`coverage < 0.9` vs neighbours) and excluded.
  - Duplicate and split-category rows are resolved explicitly, not by `drop_duplicates` order.
  - Going forward, weekly/monthly pulls record `pulled_on`, so attribute history accumulates with real dates.

### Proposed rolling-origin protocol and holdout policy (fix 5)
1. **Origins.** Every month with ≥3 matured training months. Train on rows with *t*′ + *h* ≤ *t* (embargo = horizon).
   Expanding window; optionally a 12-month sliding window once there are 2+ years.
2. **Fixed baselines** every run: sales-vs-floor (breakouts), growth (holders 1m), rank and persistence (holders 3m),
   2-feature logistic. A new model ships only if it beats the best baseline on the **primary metric**
   (top-10-per-category hit rate, month-mean) with a month-block bootstrap CI excluding 0. It must not lose on Brier
   after calibration.
3. **Report per month and per category.** Show PR-AUC, precision@10/20/50, lift, Brier and a reliability table.
   Use month-block and product-cluster CIs, not row-level ones.
4. **Calibration** is fitted on the out-of-sample predictions of earlier origins only, then applied forward.
5. **Holdout policy.**
   - (a) **Retrospective:** freeze now. Model selection may use origins up to Apr 2026 (1m) / Mar 2026 (3m). The last
     4 origins (May–Aug 1m, Apr–Jun 3m) are evaluated **once**, after all choices are fixed, and reported as-is.
   - (b) **Live:** every weekly/monthly score is appended to `weekly/history.csv` with model version and timestamp
     *before* outcomes exist. Oct 2026 onward is the true holdout, evaluated when labels mature (Oct lists for 1m
     in early Nov; 3m in early Jan 2027).
   - No retraining on a month until its predictions have been logged.
6. **Out-of-range guard.** Score only populations represented in training (same list spec and position range). Any
   new population (deep risers, 501–1,000 sales ranks, `--scan` windows) needs its own back-test before its scores
   appear in a report.

---

## Appendix: how to reproduce

```
cd C:\Users\Administrator\Documents\EmberClove-Hub
python -I research/kalodata/audit/model_audit_eval.py      # ~8 min, read-only DB, writes model_audit_results.json
```
The script imports `load()`, `build()`, `TASKS` and `subset()` from `scripts/train_product_model.py` unchanged. It
excludes Sep riser positions 201–1,000 from the history panel and uses fixed seeds (HGB 7, bootstrap 20261027).
