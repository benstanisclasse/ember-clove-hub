# Phase A: historical data integrity (2026-10-31)

Scope: `research/kalodata/kalodata.db` (opened read-only), the API capability audit (`research/api_capability_audit/`),
and all earlier Kalodata research (digest: `_work/prior_research_digest.md`). No API calls and no credits. Every number
below comes from `scripts/phase_a_integrity.py`, whose output is `_work/phase_a_results.json` and `_work/phase_a_coverage.csv`.
The exceptions are the four checks in §4.4, which were run as one-off queries and quoted here.

## Verdict

**Ready for Phase B, with two hard constraints:**

1. **No untouched holdout.** Every month 2025-10..2026-09 has already been used for training, selection, holdouts or
   pattern-finding. Retrospective results in this programme are **exploratory**. The only clean test is the **forward
   test**: freeze predictions on the 2026-09 universe now and score them against Oct-Dec 2026 lists. Those lists need
   paid pulls, about 30 credits/month within the existing D1 budget, and still need the owner's go-ahead.
2. **Kalodata is a ranked sample, not a census.** The 29 top-500 lists are complete enumerations, so absence from a list
   is informative. Outside those lists we see almost nothing: about 95% of top-500 entrants were in none of our lists the
   month before.

---

## 1. What the database is

| Collection | Design (per L1 category × month, 29 categories, 2025-10..2026-09) | Rows |
|---|---|---|
| Top sellers | `product/rank`, sorted by revenue, ranks 1-500 (Virtual Products 1-100) | 169,808 |
| Risers | `product/rank`, sorted by Kalodata `revenue_growth_rate`, ranks 1-200; 201-1,000 for 2026-09 only | 89,610 |
| Top videos | `video/rank`, sorted by revenue, ranks 1-300, **no product id** | 101,320 |
| Product → videos | `video/rank` filtered by product, 2026-09 only, 99-125 products | 34,632 |
| Product detail | `product/detail` for that month: a **seeded random sample** of 3 per category-month (1 from the top 100, 1 from ranks 101-500, 1 riser; `kalodata_core.py:140-156`, seed 7) | 1,004 product-months |
| Categories | `category/rank`, rolling windows only (last30/90/365Day as of 2026-10-25/26) | 807 |
| Comment insights | 24 products, generated 2025-07..2026-10 | 24 |
| Derived video analysis | 185 videos (92 winners, 93 comparisons; 94 products, 25 categories) | 185 |

Panel after dedupe: **251,752 product-months, 135,983 products.**

## 2. Timing: everything is a look back from 25 October 2026

- All monthly lists for 12 months were collected on **2026-10-25 between 15:57 and 21:47** (one 2026-03 page on 10-26).
  The values are Kalodata's **current estimates of past months**, not what was visible at the time.
- **Revisions can't be measured.** Only 10 product-months were pulled on two different days, and all 10 agree within 1%.
- **Survivorship can't be measured.** If Kalodata drops deleted products from historical rankings, the lists are refilled
  by others and we can't tell. It would favour durable products in history-based studies.
- **2025-10 is a partial month.** Top-500 revenue is $240M against $716M-$1,085M for other months, so Kalodata's history
  starts around late October 2025. Nov-Dec 2025 ($1,085M, $1,004M) carry the holiday peak, and we have **one** of each
  calendar month, so seasonality and trend can't be separated.

## 3. Coverage and selection bias

- **Top-500 lists are complete.** Membership and rank are fully observed for ranks 1-500 in each L1 category. Absence
  means rank > 500, and revenue below that list's minimum (the "cutoff").
- **The cutoff varies hugely by category:** the 500th product sold $1,791 (p10), $13,555 (median) and $39,585 (p90)
  per month across the 336 full category-months. Targets must be **category-relative**. The same revenue means very
  different things in Pre-Owned and in Beauty.
- **Top-500 share of category revenue** (Sep-2026 top-500 sum vs Kalodata's last-30-days category revenue on 10-25; the
  windows don't match exactly, so this is approximate): 27% (Womenswear) to 91% (Pre-Owned), mostly 33-66%. **The long
  tail, half or more of category revenue, is not in the data.**
- **Entrants come from outside our view.** Each month about 4,800-6,100 products enter some top-500. Only 101-294 per
  month (2-6%) were in *any* of our lists the month before, and the share that ever appeared earlier rises from 2% to
  about 35% by mid-2026 (`top500_entrant_sources`). **Early-warning prediction from below the top 500 is mostly impossible
  with this data.** The riser lists rarely contain future entrants.
- **Riser lists are dominated by tiny products:** median revenue $579, 62% under $1,000. They're sorted by an undocumented
  field (§4.2), so the riser universe is shaped by that field, not by our choice.
- **Top-500 retention** month to month is 57-66% (stable through the year). Months in the top 500 per product:
  28,951 products appear once, 1,801 in all 12 months.
- **Videos:**
  - The lists are the top 300 by revenue per category-month, so they are range-restricted (successful videos only).
  - They carry **no product id**. Video-to-product links exist for 99 products in 2026-09 only.
  - Per-product creator and video counts over time exist only in the random detail sample (§1), about 84 products a month.
- **The 185-video feature sample** pairs winners with comparison videos of the same products. It is useful for paired
  contrasts, not for population rates.

## 4. Field quality

### 4.1 Arithmetic consistency: excellent

- `live + video + showcase` revenue equals `revenue` in 100% of product-months.
- `unit_price × units` equals `revenue` within 2% in 100% of product-months. So **unit_price is a derived average selling
  price**, not a list price.
- There are no zero or negative revenues or units.
- Product detail revenue matches rank revenue for the same month in 964 of 1,004 pairs (96%), all pulled the same day.

### 4.2 `revenue_growth_rate` is not month-over-month growth

- It agrees with our computed MoM revenue change (within 2% or 1 point) in only **1.5%** of 99,967 checkable pairs. The rank
  correlation is only 0.29 (and 0.29 with unit growth).
- The implied previous revenue (`rev / (1 + g)`) is 0.48×-3.4× the observed previous month (p10-p90).
- 11.5% of top-list rows are exactly **+100** (a placeholder, probably meaning "no base"), and 2.2% are exactly −100.
- The spec defines it only as "Product revenue growth rate". **Rule:** compute MoM growth ourselves. Keep Kalodata's field
  as an undocumented momentum signal (hypothesis H-B2). The riser lists are selected on this field.

### 4.3 Fields that are today's values, not historical

- Commission rate, launch date and product name are identical in every month for all 20,038 products seen in 3 or more
  months. SKU count changes for 39 of them.
- **Commission and SKU count can't be used as historical features.** H-B9 (commission) is downgraded to not testable.
- Launch date is a fixed fact, so it stays valid (never after the observed month; range 2023-07-21..2026-09-28). It is
  probably Kalodata's first-seen date for the listing.
- 33% of product-months have commission 0. That could mean "no open plan", but it isn't documented.

### 4.4 Other

- **AI-video flag:** 0 for every video before 2026-06 (4.0-5.8% from June). Before June it means *unknown*.
- **Ad flag:** 63-83% of top videos per month are ads. `ads_roas` is set if and only if `ad = 1` (p10/p50/p90 =
  1.61/2.48/3.36; 1,195 distinct values). `ad_revenue_ratio` is capped at 80 in our data.
- **Duplicates:** 1,020 repeated product-list keys, all with identical values. Womenswear Aug/Sep was pulled twice.
  174 product-months sit in two L1 lists, and 161 product-months disagree by more than 1% across lists. Handled by the
  dedupe rule.
- **Missing values:** `seller_id` (110 rows) and `sku_count` (125 rows).
- **Video freshness:** videos in the top lists are young (publish age p50 = 1 month, p90 = 4). Only 7 were "published after" their month.
- **Comment insights:** generated between 2025-07 and 2026-10, so some predate the panel. With n = 24, no statistics.

## 5. Earlier models and the holdout ledger (from the digest, with citations there)

- **Breakouts** (enter a strong position next month): one feature, sales relative to the category's 500th-place sales,
  does nearly all the work (AUC ≈ 0.88-0.90, top-10-per-category hit rate 27-33%). The adopted logistic model adds 1-2
  points, and the boosted tree was never adopted.
- **Holders, 1 month:** logistic top-10 hit rate ≈ 54% vs 41% for Kalodata growth, against a 30% base rate. **Holders,
  3 months:** mostly established best-sellers staying (≈ 90% vs 82% for rank).
- **Calibration:** scores are overconfident above about 20%.
- **Refuted or weak:**
  - the "≥ 50% chance" wording
  - commission effects (and commission isn't historical anyway)
  - "moderate growth beats explosive"
  - the breadth test
  - riser positions 201-1,000
  - single-year seasonal peaks
- **Video pair study:** only paid boosting survived correction for 152 tests (84% of winners vs 41% of comparisons).
  Video age was not matched (37 vs 17 days).
- **Holdout ledger:** no month is untouched. The Phase B "frozen" holdouts (Jun 2026 for 3 months, Aug 2026 for 1 month)
  were already contaminated before they were spent, and one of them changed a model decision.

## 6. What can be tested with data we already have

| Project | Testable now | Partly / small n | Not testable without new data |
|---|---|---|---|
| A Anatomy of winners | Trajectory groups from top-500 membership and revenue; price, age, channel mix, shop | Creator and video counts (random detail sample, ~1,000 rows) | Commission (not historical) |
| B Early prediction | T1 retain, T2 climb, T4 sustain (fully observed); T3/T5 with censoring; horizons 1-3 months | T6 break-in from riser lists (small, biased universe) | 7-day horizon (no daily data; `revenue_trend` null) |
| C Video | Engagement vs revenue, ad vs organic (range-restricted), AI share from June | Creative features (185-video paired sample, exploratory) | Per-product video concentration over time (links for 99 products in one month) |
| D Saturation | Our own category aggregates per month: top-500 revenue, shop concentration (top-3 share, HHI), entrant rates, ASP | Saturation by product family (needs title clustering) | Kalodata category or shop history (only one rolling snapshot) |
| E Consumer | — | Attribute annotation of titles and descriptions (local, needs an inter-rater protocol) | Review-based statistics (24 insights) |
| F Sourcing | Existing 145 CJ matches (current prices only) | New CJ lookups (free points, 1 req/s logistics) | Historical margins (no CJ price history) |
| G Ad suitability | — | — | Our own ad outcomes (2-4 tested products; TikTok ad account closed 10-31) |
| H Bundles | — | — | Co-promotion data (needs paid creator/video-filtered pulls) |

## 7. Rules adopted for later phases

Frozen in `registry/DEFINITIONS_v1.md` before any outcome was examined:
- the observation unit and dedupe rule
- category-relative targets T1-T6 with explicit censoring
- trajectory groups A-F
- baselines B0-B6 and metrics (precision@k, Holm-adjusted month-block bootstrap)
- leakage rules
- the Phase A data rules (Oct-2025 partial; commission and SKU count not historical; AI flag from June only)
- the **forward-validation policy**

25 hypotheses with their testability are in `registry/hypotheses.csv`. Results go to `registry/experiments.jsonl`
(append-only).

## 8. Unresolved questions

1. What does `revenue_growth_rate` measure, and what are Kalodata's freshness and revision policies? (Ask Kalodata;
   contact in the audit.)
2. Does Kalodata drop deleted or banned products from historical ranks (survivorship)?
3. Is commission 0 "no affiliate plan" or "unknown"?
4. Would `need_extra` give daily `revenue_trend`? It is needed for any sub-monthly work (0.1-credit test awaiting approval).
5. Forward data: approving the Oct-2026 monthly pull (≈ 30 credits, within budget D1) is what turns this programme's
   models from exploratory into validated.

## 9. Next phase

**Phase B (winner characteristics) is ready.** It uses only local data:
- trajectory groups per DEFINITIONS_v1 §3
- group comparisons on price, age, channel mix, shop strength and category concentration, with category and month
  controls
- creator and video counts from the random detail sample

All results are labelled **descriptive/exploratory** under the holdout ledger above.

---

## Correction (2026-10-31, after the Tier 2 download)

The loader used to label every revenue-sorted page "top". One old probe page (Womenswear 2026-09, ranks 1,001-1,100) was
therefore inside the top-500 panel. Pages beyond 5 are now labelled `top_deep` (`scripts/kalodata_db.py`, `TOP_PAGES`),
and `phase_a_integrity.py` was re-run (`_work/phase_a_results.json`, EXP-A-002). The changes are small, and no conclusion
changes:

| Figure | Before | Corrected |
|---|---|---|
| Panel product-months | 251,752 | 251,654 |
| Products seen in the top 500 once | 28,951 | 28,886 |
| 2026-09 top-500 entrants (in any list the month before) | 4,986 (146) | 4,892 (142) |

The figures above in this report are kept as first written. The corrected values supersede them.
