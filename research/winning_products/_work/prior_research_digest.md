# Prior research digest: Kalodata US TikTok Shop (Oct 2025 – Sep 2026)

Date: 2026-10-31. Purpose: starting point for the "winning product" research programme on
`research/kalodata/kalodata.db`. Read-only: no file, database or API was touched to build this (DB opened with
`mode=ro`). Citations are `path:line` relative to the Hub root (`C:\Users\Administrator\Documents\EmberClove-Hub`).
"[digest]" marks an inference made in this digest, not a claim found in a source.

---

## 1. Known data-quality issues

### 1.1 What the core dataset is (and is not)
- Core pulls per category-month: top 500 by revenue (5 pages), top 200 "risers" sorted by Kalodata's growth field
  (2 pages), top 300 videos (3 pages), ~3 product details; 28 usable categories × 12 months
  (docs/MARKET_DATA_QUALITY_REPORT.md:108-116). Sep 2026 only also has "deep risers" positions 201–1,000
  (docs/MARKET_DATA_QUALITY_REPORT.md:112) and full video lists for 100 products (:115).
- Download is complete as a download: every page full, revenue = units × price, channel revenues sum to total, sort
  order holds (docs/MARKET_DATA_QUALITY_REPORT.md:15-19, 316-321). Not a missing-rows problem; a meaning/timing problem.
- History starts ~Oct 2025; Apr 2025 / Oct 2024 probes return "not found" (research/kalodata/FULL_DATASET_PLAN_2026-10-25.md:7-9).
  Ranks page past 1,000 (page 11 works, ~$44–48K/month in Womenswear) (FULL_DATASET_PLAN_2026-10-25.md:10-11), but
  nothing beyond top-500 sales rank was pulled for any month.

### 1.2 Selection / ranking depth
- **Survivorship:** a product is visible only in months it made a list; "not in next month's top 500" ≠ "not
  observed" for features (docs/MARKET_DATA_QUALITY_REPORT.md:417-420). Labels are fine because top-500 lists are
  complete (docs/MARKET_MODEL_VALIDATION_AUDIT.md:70-72) but features like `months_seen_before` / `prev_ratio` only count
  captured lists (:73-76).
- **"Top 500" means very different floors by category:** rank 500 in Sep 2026 = $97,796 Beauty, $80,416 Womenswear vs
  $1,360 Pre-Owned and $359 Muslim Fashion (docs/MARKET_DATA_QUALITY_REPORT.md:200-205).
- **Riser lists exclude brand-new launches by construction** (growth placeholder 100 is below the ~1,000% needed to
  reach position 200) (docs/MARKET_DATA_QUALITY_REPORT.md:338-340). Riser population: median $480/month, 4.5% of floor
  (docs/MARKET_MODEL_VALIDATION_AUDIT.md:143-147).
- **Most top-500 entrants are invisible to riser-based models:** only 1.7–5.7% (median 4.0%) of products entering a
  category top 500 were on that category's riser top 200 the month before
  (docs/MARKET_MODEL_VALIDATION_AUDIT.md:157-160; research/kalodata/audit/model_audit_results.json `entrant_coverage`).
- **Deep risers (201–1,000) exist only for Sep 2026** and are a different distribution (median $226, 1.6% of floor,
  +477% growth) (docs/MARKET_MODEL_VALIDATION_AUDIT.md:147-152). They share the `core_risers_` name prefix
  (docs/MARKET_DATA_QUALITY_REPORT.md:118-120); now separated by `pulls.kind = 'risers_deep'`
  (scripts/market_data.py:43-45; docs/MARKET_ENGINE_V2_ROADMAP.md:233-234).
- Thin categories: Pre-Owned, Muslim Fashion (riser and video lists run out; placeholder/zero tails)
  (docs/MARKET_DATA_QUALITY_REPORT.md:200-203); the v2 snapshot also flags Kids' Fashion by the "$2,000 500th place"
  rule (docs/MARKET_ENGINE_V2_ROADMAP.md:232-233). Virtual Products: no data any month (:199).

### 1.3 Retrospective pulls / revisions / timing
- All 12 months collected in one ~4-hour window, 2026-10-25 19:22–23:19 ET; each month is a look-back, not what was
  visible at the time; no collection timestamp stored (docs/MARKET_DATA_QUALITY_REPORT.md:25-27, 399-403). Gap from
  month end to collection: ~358 days (Oct 2025) to ~24 days (Sep 2026) (:179-190).
- **Revisions cannot be measured:** no second vintage of any month; pilot vs core re-pull 5 h apart matched exactly
  (docs/MARKET_DATA_QUALITY_REPORT.md:43-45, 288-296). Live scoring will see first estimates; training sees settled
  values (:413-414).
- **October 2025 is a partial month (~1 week):** same-product Oct÷Nov revenue median 0.24; top-500 revenue 0.29 of
  the 2026 average; every Oct growth value = 100; Oct riser list order is arbitrary; Nov growth/lag features inflated
  (median Nov top-500 growth +62%) (docs/MARKET_DATA_QUALITY_REPORT.md:20-24, 220-244).
- Revenue, units, channel split, ad flag/ROAS are Kalodata **estimates** (method not published); ROAS capped at 20,
  ad-revenue ratio capped at 80% (46% of ad videos at the cap) (docs/MARKET_DATA_QUALITY_REPORT.md:349-350, 366-381).
- 1-month forecasts are about a month already under way at decision time (Kalodata month data arrive early t+1; the
  Sep scores were made when Oct was 80% over) (docs/MARKET_MODEL_VALIDATION_AUDIT.md:78-80).

### 1.4 Current-value ("snapshot") fields = look-ahead leaks
- Product name, seller, launch date, SKU count, commission rate are identical in every month for all 34,718
  multi-month products; review count is current (docs/MARKET_DATA_QUALITY_REPORT.md:28-31, 405-412). Used as
  historical features in v1, pilot and breakout scorer (:409-411). v2 never uses them as features
  (research/kalodata/snapshots/pit_2026-09_v1/manifest.json `current_value_fields_never_features`;
  docs/MARKET_ENGINE_V2_ROADMAP.md:238-240).
- `unit_price` is revenue ÷ units per month (average realised price, not list price) (docs/MARKET_DATA_QUALITY_REPORT.md:319).

### 1.5 Growth-rate definition
- `revenue_growth_rate` is **not** month-on-month: matches our own MoM within 0.5 pts for 0.7% of 99,736 pairs;
  4,169 rows are −100% with positive revenue; 100 = "no earlier period" placeholder (collides with real +100%)
  (docs/MARKET_DATA_QUALITY_REPORT.md:32-35, 326-340). Video growth field unusable (97% below −100%) (:336-337).
- v2 keeps it only as a labelled feature `kalo_growth_slog`, placeholder → missing (7,765 rows), and adds our own
  `mom_growth` (scripts/market_data.py:82; docs/MARKET_ENGINE_V2_ROADMAP.md:231-237).

### 1.6 Duplicates and category assignment
- Womenswear Aug + Sep top 500 stored twice (pilot + core): 1,000 duplicate rows; any query not filtered to core pulls
  double-counts them (docs/MARKET_DATA_QUALITY_REPORT.md:139-150).
- 159 product-months in two category lists with **different** revenue (each category holds its share); product totals
  must be summed (docs/MARKET_DATA_QUALITY_REPORT.md:246-254). v1 kept the first row; v2 sums (150 summed; 9 were in Oct)
  (docs/MARKET_ENGINE_V2_ROADMAP.md:230-231).
- Rank rows carry **no category field**: category exists only as the request filter in the pull name; subcategory
  only for the 1,003 detail rows (docs/MARKET_DATA_QUALITY_REPORT.md:193-195); 20 detail rows have a primary category
  different from the list they came from (:362). The EASY_WINS screen filtered by product name because "the category
  ids are unreliable" (research/kalodata/EASY_WINS_2026-10-31.md:10-11).
- Product-type analyses use keyword matching on product names (approximate)
  (research/kalodata/CATEGORY_SEASONALITY_2026-10-26.md:78; research/kalodata/INSIGHTS_2026-10-28.md:11-12).
- Near-duplicate listings / relists: 825 same-seller same-title groups in a month (1,776 IDs); 779 seller+title pairs
  map to >1 ID across months; a relist looks brand-new (docs/MARKET_DATA_QUALITY_REPORT.md:277-286).
- Video duplicates: 129 rows within top-300 lists (tied $0 rows paginate unstably), 3,397 in full-product lists; 40 of
  100 full lists truncated at 5 pages (docs/MARKET_DATA_QUALITY_REPORT.md:263-275).

### 1.7 Missing / degraded fields
- AI video flag is 0 (not NULL) for every row Oct 2025–May 2026; valid only from Jun 2026 (4.0% → 5.8%)
  (docs/MARKET_DATA_QUALITY_REPORT.md:36-37, 347).
- `revenue_trend` null in all detail rows; `master_image_url` always null (docs/MARKET_DATA_QUALITY_REPORT.md:80-81, 359).
- Views are monthly while likes look lifetime (2,168 rows views < likes) (docs/MARKET_DATA_QUALITY_REPORT.md:351).
- Loader kept 6 failed comment-insight pulls that later succeeded (docs/MARKET_DATA_QUALITY_REPORT.md:298-303).
- Recommended exclusions list: docs/MARKET_DATA_QUALITY_REPORT.md:424-441.

### 1.8 Inconsistency to check [digest]
- INSIGHTS says "Aug-Sep 2026 category totals are about double earlier months while the median top-500 product
  didn't change" (research/kalodata/INSIGHTS_2026-10-28.md:9-10). The data-quality table shows Aug/Sep top-500 totals of
  $855M/$836M vs a 2026 average of ~$827M (docs/MARKET_DATA_QUALITY_REPORT.md:188-190). Most likely the INSIGHTS
  query picked up the duplicated Womenswear Aug/Sep pilot pages (1.6) [digest, unverified]. Treat INSIGHTS
  Aug–Sep totals with caution.

---

## 2. Every prior model / study

Month index used below: Oct25 = 2025-10 … Sep26 = 2026-09.

### 2.1 Pilot model (2026-10-25) — superseded
- Question: will an Aug Womenswear top-500 product still sell at least as much in Sep?
  (research/kalodata/PILOT_MODEL_2026-10-25.md:11-13).
- Target: in Sep top 500 AND Sep sales ≥ Aug sales; 172/500 won (34%) (PILOT_MODEL:12-13; scripts/pilot_model.py:42).
- Universe: Womenswear (601152) top 500, Aug 2026, from `pilot_womenswear_*` pulls (PILOT_MODEL:8-10; scripts/pilot_model.py:36).
- Features (12): sales, units, price, growth vs July (Kalodata field), commission, video/live/shop share, age, SKU count,
  rank, seller top-500 count (PILOT_MODEL:14-15) — includes current-value leaks.
- Split: 5-fold shuffled stratified CV on one month (PILOT_MODEL:16-17; scripts/pilot_model.py:67). **No holdout.**
  Uses Aug (features) and Sep (labels).
- Metrics: logistic AUC 0.70 (top 25/50/100 hit 48/54/56% vs 34% random); growth alone 0.69; biggest sellers 0.55;
  HGB 0.68 (PILOT_MODEL:21-28). Growth bands: down >20% → 14% won; up 25–75% → 55% (PILOT_MODEL:39-45).
- Conclusion: pipeline test only; momentum is the baseline to beat (PILOT_MODEL:3-5, 65-69).

### 2.2 Product model v1 (2026-10-25) — corrected, superseded by v2
- Code: scripts/train_product_model.py; outputs research/kalodata/model_v1_2026-10-25/ (MODEL_V1_2026-10-25.md:16-18).
- Panel: 230,052 product-months, 115,702 products, Oct25–Sep26, top 500 + risers 1–200 (MODEL_V1:16-17;
  scripts/train_product_model.py:34, 44-49, 64-68).
- Targets (scripts/train_product_model.py:127-132; docs/MARKET_MODEL_VALIDATION_AUDIT.md:61-66):
  - holders_1m: top-500 at t → in top 500 at t+1 AND revenue(t+1) ≥ revenue(t)
  - holders_3m: top-500 at t → in top 500 at exactly t+3
  - breakouts_1m: riser 1–200 not in top 500 at t → in top 500 at t+1
  - breakouts_3m: same → in top 500 at t+1, t+2 or t+3
- Features (20): log_sales, log_units, unit_price, growth_slog (Kalodata), commission_rate, video/live/shop share,
  age_days, log_sku, rank_pos, in_risers, riser_pos, seller_n_top500, seller_share_cat, cat_growth,
  months_seen_before, prev_ratio, was_top500_prev, price_vs_cat (scripts/train_product_model.py:38-40). Leaks:
  commission, SKU, age; Oct25 partial included (docs/MARKET_MODEL_VALIDATION_AUDIT.md:90-109).
- Split: single forward split, test = last 3 labelled months (scripts/train_product_model.py:156-158):
  1m tasks train Oct25–May26, **test Jun–Aug 2026**; 3m tasks train Oct25–Mar26, **test Apr–Jun 2026**, no embargo
  (Mar rows' labels need Jun) (docs/MARKET_MODEL_VALIDATION_AUDIT.md:172-173). Final models refit on all labelled
  months (scripts/train_product_model.py:186). Feature choices were made while looking at these same test months:
  "no untouched holdout" (docs/MARKET_MODEL_VALIDATION_AUDIT.md:172).
- Metrics (research/kalodata/model_v1_2026-10-25/results.json; MODEL_V1:24-29):

  | Task | Test months | Base | AUC HGB | AUC logistic | AUC growth | AUC sales | Top 10% | Top 10/cat |
  |---|---|---|---|---|---|---|---|---|
  | holders_1m | Jun–Aug | 29.6% | 0.685 | 0.678 | 0.651 | 0.503 | 49.7% | 57.1% |
  | holders_3m | Apr–Jun | 46.7% | 0.797 | 0.787 | 0.529 | 0.650 | 91.1% | 93.7% |
  | breakouts_1m | Jun–Aug | 3.2% | 0.890 | 0.868 | 0.511 | 0.809 | 18.5% | 24.3% |
  | breakouts_3m | Apr–Jun | 5.2% | 0.880 | 0.862 | 0.523 | 0.795 | 27.4% | 33.1% |

  `auc_sales_only` 0.81/0.80 was omitted from the report table (docs/MARKET_MODEL_VALIDATION_AUDIT.md:34-35).
- Breadth test: creators/videos on 649 sampled product-months, **shuffled 5-fold CV** (not forward): AUC 0.677 → 0.690
  (MODEL_V1:55-58; scripts/train_product_model.py:194-213; docs/MARKET_MODEL_VALIDATION_AUDIT.md:113-114).
- Win-rate profiles (holders_1m, all months): growth <−20% 14% → >75% 44%; age <2 mo 22% vs >1 yr 35%; video share <50%
  25% vs 50–80% 35% (MODEL_V1:46-53).
- Conclusion as corrected: holders real but modest; breakout AUC ≈ distance to floor; leaks; scores not probabilities
  (MODEL_V1:3-13). Holdout: none (test months doubled as selection months).

### 2.3 Breakout scorer without riser position + deep list + explanations (2026-10-25) — corrected
- scripts/score_breakouts.py: HGB without riser_pos/rank_pos/in_risers (:23), test = last 3 labelled months
  (:39 → Jun–Aug 1m, Apr–Jun 3m), final fit on all labelled months (:44), scores Sep 2026 risers incl. deep 201–1,000
  (log.md:167; :1-5 docstring). Forward AUC 0.876 (1m) / 0.865 (3m); top 10% hit 18% / 25.4%
  (research/kalodata/model_v1_2026-10-25/breakout_deep_check.json). 26,790 Sep candidates, 291 scored ≥50%
  (238 from the deep list) (log.md:167).
- Explanations: drivers = current sales (dominant), video share, moderate growth, price vs category, variants
  (research/kalodata/BREAKOUT_EXPLAINED_2026-10-25.md:18-25). Corrected: mostly distance to floor; commission is
  today's value; percentages not calibrated (BREAKOUT_EXPLAINED:3-10). Per-product reasons for 10 hand-picked
  products (BREAKOUT_EXPLAINED:45-56) are post hoc (docs/MARKET_MODEL_VALIDATION_AUDIT.md:333-337).
- Weekly breakout report 10-26: scored Sep risers with the cached 3-month breakout model, ≥50% threshold + filters
  (log.md:171); 10 picks logged in research/kalodata/weekly/history.csv (dated 2026-10-26).

### 2.4 Ad-hoc analyses with no script (log only)
- Commission (log.md:168): 0% commission holds 1m 24% vs ~33%; breakouts 3m 2.8% vs 6–11%; all months, observational.
  Audit re-check with product-cluster CIs: ordering clear but commission is the Oct-2026 value and confounded
  (docs/MARKET_MODEL_VALIDATION_AUDIT.md:338-343).
- Small-to-big (log.md:169): of 52,334 products seen under $5K/month in riser lists (Oct25–Jun26), later peak ≥$10K
  6.3%, ≥$100K 0.37% (196), within 3 months ≥$100K 0.21%; outcomes looked up through Sep 2026. No CIs, no script
  (docs/MARKET_MODEL_VALIDATION_AUDIT.md:370-371).

### 2.5 Phase A model validation audit (2026-10-28 ~00:15) — research/kalodata/audit/
- Script research/kalodata/audit/model_audit_eval.py reuses v1 `load/build/TASKS` (:3, 29-31), excludes Sep deep risers
  (:49-51). Rolling origin, expanding window, embargo = horizon (:192-212). **Test months: Jan–Aug 2026 for 1m tasks,
  Mar–Jun 2026 for 3m** (:407-408; MONTHS index 3–10 and 5–8). Variants: no-snapshot, "clean" (drop Oct/Nov rows,
  commission, SKU, age), no-riser-pos, no-embargo, 2-feature logistic, baselines (:201-213). Extra probes: drop-Oct
  (Apr–Jun 3m, Feb–Aug 1m) (:419-423); leave-one-category-out on Apr–Jun (:298-314); out-of-range probe train riser
  1–100 → score 101–200, all months with ≥3 training months (:317-345); entrant coverage Nov25–Sep26 (:362-378).
- Results (docs/MARKET_MODEL_VALIDATION_AUDIT.md:196-273):
  - breakouts_3m (Mar–Jun, 20,714 rows, base 5.3%): GBM AUC 0.872 [0.864–0.880], top10/cat 34.1%; one-number floor
    rule AUC 0.877, top10/cat 32.9%; 2-feature logistic 0.878; Kalodata growth 0.521 (:198-212).
  - breakouts_1m (Jan–Aug, 41,620 rows, base 3.7%): GBM 0.886, floor rule 0.896 (significantly better, Δ −0.016 to
    −0.005), top10/cat 27.2% vs 27.1% (:214-227).
  - Within distance-to-floor bands GBM AUC only 0.60–0.68; 68% of risers are <10% of floor (:229-242).
  - holders_1m (Jan–Aug, 111,900 rows, base 30.3%): GBM 0.682 [0.674–0.690], top10/cat 54.5% vs growth 41.1%;
    +0.030–0.036 AUC over growth (:244-258).
  - holders_3m (Mar–Jun, 55,953 rows, base 46.5%): GBM embargoed 0.793, top10/cat 92.4%; months-on-lists 0.724;
    rank 0.707 / 82.8% (:260-273).
  - Calibration: overconfident above ~20%; ≥50% scores hit 42% (b3m), 40% (b1m), 49% (h1m); out-of-range ≥50% → 32%
    (:277-299, 153-156).
  - Leakage cost 0.003–0.026 AUC (:117-134). LOCO: 25/28 categories within ±0.02 (:307-309). Womenswear weak: GBM
    below floor rule, 4 of 40 top-10 picks broke in (:315, 324-326).
- Holdout: none reserved; it evaluated every month that later became the Phase B holdout (Aug for 1m, Jun for 3m).

### 2.6 Phase B: point-in-time snapshot + rolling evaluation + model_v2 (2026-10-28 00:56–00:59)
- Snapshot `pit_2026-09_v1` (scripts/market_data.py): 232,467 product-months, 127,048 products, Nov25–Sep26; Oct25
  excluded (19,600 rows); Nov lag features missing (18,938); split product-months summed; dedup; growth placeholder
  missing; Sep deep risers separate population (docs/MARKET_ENGINE_V2_ROADMAP.md:228-234;
  research/kalodata/snapshots/pit_2026-09_v1/manifest.json).
- 18 features: log_sales, log_units, unit_price, video/live/shop share, log_vs_floor, price_vs_cat, mom_growth,
  listed_prev, was_top500_prev, months_seen_before, kalo_growth_slog, rank_pos, riser_pos, seller_n_top500,
  seller_share_cat, cat_growth (scripts/market_data.py:63; manifest `features`). Never: commission, SKU, launch
  date/age, review count, names (docs/MARKET_ENGINE_V2_ROADMAP.md:236-240).
- Tasks: same four questions; labels = membership of **any** category top 500 (manifest `labels`;
  scripts/market_data.py:91-97); breakout population = risers 1–200 outside every top 500 (scripts/market_eval.py:69-75, 92-101).
- Design: rolling origin, expanding window, embargo = horizon, ≥2 training months; last fully labelled month = frozen
  holdout; `select` uses selection months only, `final` evaluates holdout once and marks it spent
  (scripts/market_eval.py:3-8, 113-124, 329-335, 514-517). Candidate HGB vs 8 baselines incl. logistic; primary metrics
  category top-10 hit rate (p_cat@10) and lift@20; month-block bootstrap 2,000 draws (scripts/market_eval.py:52-61).
- Months: **1m tasks selection Jan–Jul 2026, holdout Aug 2026; 3m tasks selection Mar–May 2026, holdout Jun 2026**
  (research_runs.eval_design; docs/MARKET_ENGINE_V2_ROADMAP.md:244-246). Earliest training rows Nov–Dec 2025 (min 2
  months). Final rankers refit on every matured row: 1m tasks trained Nov25–Aug26 (labels to Sep26), 3m tasks
  Nov25–Jun26 (labels to Sep26) (scripts/market_eval.py:576-583; model_v2_2026-10-28/manifest.json `trained_months`).
- Results (all evaluated months incl. holdout; docs/MARKET_ENGINE_V2_ROADMAP.md:254-295):

  | Task | Logistic (adopted) top10/cat | Best single rule | HGB | Holdout month: logistic / rule / HGB |
  |---|---|---|---|---|
  | breakout_3m (base 5.3%) | 34.7% [32.7–37.7], AUC 0.885 | floor ratio 32.9% | 33.4% | Jun: 32.9% / 30.4% / 30.4% |
  | breakout_1m (base 3.7%) | 28.3% [26.0–30.4], AUC 0.905 | floor ratio 27.1% | 28.4% | Aug: 22.9% / 21.8% / 23.6% |
  | holders_1m (base 30.3%) | 53.7% [48.3–58.0], AUC 0.667 | Kalodata growth 41.1% | 51.4% | Aug: 55.0% / 40.7% / 51.8% |
  | holders_3m (base 46.5%) | 89.7% [88.9–90.8], AUC 0.787 | floor ratio = rank 82.4% | 89.7% | Jun: 91.4% / 83.2% / 88.2% |

- Decision: logistic adopted for all four via a "ladder" interpretation (rule → logistic → HGB) flagged "for the owner
  to confirm"; under the literal rule the floor ratio / Kalodata growth would be adopted
  (docs/MARKET_ENGINE_V2_ROADMAP.md:206-207, 329-336). No calibration kept (:307-311). Womenswear breakout rankers weak:
  floor 17.5%, logistic 15%, HGB 12.5% top-10 (40 picks each, base 2.8%) (:313-315).
- **Holdout used: yes, and spent** (Aug 2026 for 1m, Jun 2026 for 3m) (:327, 385). Disclosure: an identical final run
  was executed once on a scratch registry before the registered run, so holdouts were seen twice
  (docs/MARKET_ENGINE_V2_ROADMAP.md:342-345).
- Weekly research shortlist 10-28 (offline, Sep 2026 data): ranks by adopted breakout_3m ranker, no probabilities,
  10 picks logged in weekly/history.csv (docs/MARKET_ENGINE_V2_ROADMAP.md:355-372).

### 2.7 research_runs registry (all 8 rows, read via `mode=ro`)
Common to all 8 rows:
- `data_snapshot` = `pit_2026-09_v1`; `data_cutoff` = `2026-09`; `seed` = 20261028;
  `code_commit` = `777234625b1b1cfabd4c990163525c5d9f060736`.
- `features` (all rows identical): ["log_sales", "log_units", "unit_price", "video_share", "live_share", "shop_share",
  "log_vs_floor", "price_vs_cat", "mom_growth", "listed_prev", "was_top500_prev", "months_seen_before",
  "kalo_growth_slog", "rank_pos", "riser_pos", "seller_n_top500", "seller_share_cat", "cat_growth"].
- `params` (identical): {"hgb": {"max_depth": 6, "learning_rate": 0.05, "max_iter": 400, "min_samples_leaf": 50,
  "l2_regularization": 1.0, "random_state": 7}, "logistic": "StandardScaler + LogisticRegression(max_iter=3000), median fill"}.
- `eval_design` common part: {"design": "rolling origin, expanding window, embargo = horizon (train rows with month + h
  <= test month)", "min_train_months": 2, "bootstrap": "month-block, 2000 draws", "primary_metrics": ["p_cat@10",
  "lift@20"], "k_overall": [10, 20, 50], "k_per_category": [3, 10, 20, 50], "candidate": "hgb", "baselines": ["random",
  "floor_ratio", "rank", "momentum", "kalodata_growth", "sales", "persistence", "logistic"], "transparent":
  ["floor_ratio", "rank", "momentum", "kalodata_growth", "sales", "persistence"], "decision_rule": "Owner's rule: the
  model (HGB) is adopted only if it beats the best baseline (logistic included) on the category top-10 hit rate or
  lift@20 overall, with a month-block bootstrap CI of the monthly difference above zero, and does not lose on the
  holdout month. Otherwise the simplest ranker that is not beaten is adopted: logistic regression (a linear,
  inspectable ranker) only if it passes the same test against the best single-rule baseline; else the best
  single-rule baseline by selection-month category top-10 hit rate (ties go to the earlier rule in the list)."}
  Results files: select rows → `research\kalodata\evals\20261028-005716_select.json`; final rows →
  `research\kalodata\evals\20261028-005841_final.json`.

Per-row fields:

| run_id | created_at | task / horizon | question | selection_months | holdout_month | holdout_used | decision (verbatim) |
|---|---|---|---|---|---|---|---|
| 20261028-005716-select-holders_1m | 2026-10-28T00:57:16 | holders_1m / 1 | Will a product in its category's top 500 this month still be in a top 500 next month and sell at least as much? | 2026-01…2026-07 | 2026-08 | 0 | PROVISIONAL (holdout not used): logistic (model). hgb did not beat the best baseline with a CI excluding zero (and no holdout loss); logistic beats the best single-rule baseline with a CI above zero on p_cat@10 and lift@20 |
| 20261028-005716-select-holders_3m | 2026-10-28T00:57:16 | holders_3m / 3 | Will a product in its category's top 500 this month be in a top 500 three months on? | 2026-03, 04, 05 | 2026-06 | 0 | PROVISIONAL (holdout not used): hgb (model). hgb beats the best baseline with a CI above zero on p_cat@10 |
| 20261028-005716-select-breakout_1m | 2026-10-28T00:57:16 | breakout_1m / 1 | Will a product on its category's riser list (positions 1-200) and outside the top 500 enter a top 500 next month? | 2026-01…2026-07 | 2026-08 | 0 | PROVISIONAL (holdout not used): logistic (model). hgb did not beat the best baseline with a CI excluding zero (and no holdout loss); logistic beats the best single-rule baseline with a CI above zero on p_cat@10 and lift@20 |
| 20261028-005716-select-breakout_3m | 2026-10-28T00:57:16 | breakout_3m / 3 | Will a product on its category's riser list (positions 1-200) and outside the top 500 enter a top 500 within three months? | 2026-03, 04, 05 | 2026-06 | 0 | PROVISIONAL (holdout not used): logistic (model). hgb did not beat the best baseline with a CI excluding zero (and no holdout loss); logistic beats the best single-rule baseline with a CI above zero on p_cat@10 |
| 20261028-005841-final-holders_1m | 2026-10-28T00:58:41 | holders_1m / 1 | (as above) | 2026-01…2026-07 | 2026-08 | **1** | ADOPT logistic (model). hgb did not beat the best baseline with a CI excluding zero (and no holdout loss); logistic beats the best single-rule baseline with a CI above zero on p_cat@10 and lift@20 |
| 20261028-005841-final-holders_3m | 2026-10-28T00:58:41 | holders_3m / 3 | (as above) | 2026-03, 04, 05 | 2026-06 | **1** | ADOPT logistic (model). hgb did not beat the best baseline with a CI excluding zero (and no holdout loss); logistic beats the best single-rule baseline with a CI above zero on p_cat@10 and lift@20 |
| 20261028-005841-final-breakout_1m | 2026-10-28T00:58:41 | breakout_1m / 1 | (as above) | 2026-01…2026-07 | 2026-08 | **1** | ADOPT logistic (model). hgb did not beat the best baseline with a CI excluding zero (and no holdout loss); logistic beats the best single-rule baseline with a CI above zero on p_cat@10 and lift@20 |
| 20261028-005841-final-breakout_3m | 2026-10-28T00:58:41 | breakout_3m / 3 | (as above) | 2026-03, 04, 05 | 2026-06 | **1** | ADOPT logistic (model). hgb did not beat the best baseline with a CI excluding zero (and no holdout loss); logistic beats the best single-rule baseline with a CI above zero on p_cat@10 |

`results_json` keys: select rows {selection, decision_tests, decision_tests_logistic_vs_rules, best_rule,
calibration_kept}; final rows add `holdout`. `calibration_kept` = null in all 8. `best_rule`: holders_1m
kalodata_growth; holders_3m floor_ratio; breakout_1m floor_ratio; breakout_3m floor_ratio.

Selection-month means [mean, 95% CI] (identical in select and final rows):

| Task | Ranker | AUC | p_cat@10 | lift@20 | p@20 | Brier |
|---|---|---|---|---|---|---|
| holders_1m | hgb | 0.671 [0.659, 0.684] | 0.513 [0.463, 0.560] | 1.86 [1.42, 2.24] | 0.557 | 0.199 |
| holders_1m | logistic | 0.666 [0.648, 0.683] | 0.535 [0.477, 0.584] | 1.92 [1.68, 2.16] | 0.586 | 0.201 |
| holders_1m | kalodata_growth | 0.651 [0.639, 0.663] | 0.411 [0.368, 0.457] | 1.47 [1.24, 1.68] | 0.450 | – |
| holders_1m | persistence / floor_ratio / random | 0.563 / 0.509 / 0.501 | 0.370 / 0.274 / 0.307 | 1.11 / 0.68 / 0.98 | | |
| holders_3m | hgb | 0.787 [0.780, 0.792] | 0.902 [0.896, 0.907] | 2.04 | 0.950 | 0.189 |
| holders_3m | logistic | 0.781 [0.776, 0.790] | 0.892 [0.889, 0.896] | 2.00 | 0.933 | 0.202 |
| holders_3m | floor_ratio (= rank = sales within cat) | 0.722 | 0.821 [0.807, 0.829] | 1.61 | 0.750 | – |
| holders_3m | persistence / random | 0.715 / 0.499 | 0.724 / 0.474 | 1.57 / 1.07 | | |
| breakout_1m | hgb | 0.899 [0.894, 0.905] | 0.291 [0.266, 0.317] | 11.63 [9.81, 14.11] | 0.436 | 0.0315 |
| breakout_1m | logistic | 0.904 [0.898, 0.910] | 0.291 [0.272, 0.309] | 14.36 [11.65, 16.90] | 0.536 | 0.0310 |
| breakout_1m | floor_ratio | 0.894 [0.887, 0.899] | 0.279 [0.264, 0.292] | 9.84 | 0.371 | – |
| breakout_1m | persistence / kalodata_growth / random | 0.563 / 0.530 / 0.494 | 0.099 / 0.108 / 0.043 | 9.96 / 3.89 / 0.89 | | |
| breakout_3m | hgb | 0.886 [0.874, 0.903] | 0.344 [0.321, 0.375] | 10.08 | 0.550 | 0.0430 |
| breakout_3m | logistic | 0.892 [0.888, 0.901] | 0.354 [0.325, 0.393] | 10.48 | 0.567 | 0.0425 |
| breakout_3m | floor_ratio | 0.881 [0.870, 0.891] | 0.337 [0.318, 0.371] | 7.61 | 0.417 | – |
| breakout_3m | persistence / kalodata_growth / random | 0.553 / 0.522 / 0.485 | 0.132 / 0.138 / 0.046 | 8.57 / 2.73 / 0.88 | | |

Decision tests (diff_mean_ci = [mean, lo, hi] over evaluated months; select = selection months only, final = + holdout):

| Task | Test | Select run | Final run (holdout_diff, passed) |
|---|---|---|---|
| holders_1m | HGB vs logistic p_cat@10 | −0.021 [−0.049, −0.002], fail | −0.023 [−0.047, −0.005], holdout −0.032, fail |
| holders_1m | logistic vs kalodata_growth p_cat@10 | +0.124 [+0.099, +0.149], pass | +0.126 [+0.104, +0.148], holdout +0.143, pass |
| holders_3m | HGB vs logistic p_cat@10 | +0.011 [+0.007, +0.018], **pass** | 0.000 [−0.022, +0.015], holdout −0.032, **fail** |
| holders_3m | logistic vs floor_ratio p_cat@10 | +0.070 [+0.061, +0.082], pass | +0.073 [+0.063, +0.082], holdout +0.082, pass |
| breakout_1m | HGB vs logistic lift@20 | −2.73 [−4.33, −1.22], fail | −2.62 [−4.08, −1.24], holdout −1.85, fail |
| breakout_1m | logistic vs floor_ratio p_cat@10 | +0.012 [+0.002, +0.021], pass | +0.012 [+0.003, +0.021], holdout +0.011, pass |
| breakout_3m | HGB vs logistic p_cat@10 | −0.010 [−0.018, −0.004], fail | −0.013 [−0.021, −0.005], holdout −0.025, fail |
| breakout_3m | logistic vs floor_ratio p_cat@10 | +0.017 [+0.007, +0.021], pass | +0.019 [+0.011, +0.024], holdout +0.025, pass |
| breakout_3m | logistic vs persistence lift@20 | +1.91 [0.00, 3.08], fail | +0.67 [−1.61, +2.86], holdout −3.03, fail |

Holdout block (final rows, complete for the key rankers; base = holdout base rate):

| Task (holdout) | base | hgb AUC / p_cat@10 / lift@20 / p@20 / Brier | logistic | floor_ratio | kalodata_growth | persistence | sales | rank | momentum | random |
|---|---|---|---|---|---|---|---|---|---|---|
| holders_1m (Aug) | 0.263 | 0.688 / 0.518 / 2.09 / 0.55 / 0.183 | 0.676 / 0.550 / 1.71 / 0.45 / 0.185 | 0.494 / 0.236 / 0.76 / 0.20 | 0.668 / 0.407 / 1.71 / 0.45 | 0.548 / 0.300 / 1.90 / 0.50 | 0.513 / 0.236 / 0.57 / 0.15 | 0.492 / 0.236 / 0.76 / 0.20 | 0.499 / 0.243 / 0.38 / 0.10 | 0.501 / 0.246 / 1.33 / 0.35 |
| holders_3m (Jun) | 0.459 | 0.798 / 0.882 / 2.18 / 1.00 / 0.184 | 0.804 / 0.914 / 2.07 / 0.95 / 0.188 | 0.706 / 0.832 / 1.96 / 0.90 | 0.581 / 0.275 / 0.44 / 0.20 | 0.751 / 0.796 / 1.74 / 0.80 | 0.636 / 0.832 / 2.07 / 0.95 | 0.686 / 0.832 / 1.85 / 0.85 | 0.517 / 0.521 / 0.44 / 0.20 | 0.489 / 0.457 / 0.65 / 0.30 |
| breakout_1m (Aug) | 0.027 | 0.916 / 0.236 / 11.08 / 0.30 / 0.0231 | 0.916 / 0.229 / 12.93 / 0.35 / 0.0236 | 0.911 / 0.218 / **16.62** / 0.45 | 0.576 / 0.104 / 5.54 / 0.15 | 0.566 / 0.068 / 3.69 / 0.10 | 0.815 / 0.218 / 12.93 / 0.35 | 0.661 / 0.104 / 7.39 / 0.20 | 0.480 / 0.021 / 0.00 / 0.00 | 0.560 / 0.064 / 1.85 / 0.05 |
| breakout_3m (Jun) | 0.050 | 0.874 / 0.304 / 6.06 / 0.30 / 0.0415 | 0.865 / 0.329 / 12.12 / 0.60 / 0.0404 | 0.868 / 0.304 / 8.08 / 0.40 | 0.518 / 0.150 / 3.03 / 0.15 | 0.588 / 0.168 / **15.16** / 0.75 | 0.794 / 0.304 / 5.05 / 0.25 | 0.594 / 0.150 / 5.05 / 0.25 | 0.483 / 0.061 / 0.00 / 0.00 | 0.529 / 0.050 / 1.01 / 0.05 |

Observations from the registry [digest]:
- **The holdout changed a decision.** holders_3m was provisionally HGB on selection months (passed +0.011), but the
  final run's inclusion of the Jun holdout (−0.032) flipped it to logistic. Under the design rule the holdout is part
  of model choice ("does not lose on the holdout month"), so these holdouts were used for selection, not only for
  final evaluation.
- On the breakout_1m holdout the plain floor ratio beat logistic on lift@20 (16.6 vs 12.9); on breakout_3m holdout
  persistence beat logistic on lift@20 (15.2 vs 12.1). The adopted logistic still won on p_cat@10.

### 2.8 Descriptive / screening studies (no model, no holdout)
- EXTRA_INSIGHTS (2026-10-26): Nov/Dec biggest months; 3-month staying power by category (Health 68% … Womenswear 42%,
  Collectibles 24%); channel mix by category (research/kalodata/EXTRA_INSIGHTS_2026-10-26.md:13-39). Uses all months.
- CATEGORY_SEASONALITY (2026-10-26): quarterly category totals, 232 subcategories' 30/90/365-day "heat", product-type
  seasonality (research/kalodata/CATEGORY_SEASONALITY_2026-10-26.md:16-86). Uses Nov25–Sep26 + rolling windows.
- INSIGHTS (2026-10-28): Womenswear Nov–Dec vs Jan–Jul type mix, price bands, top-video traits, Sep risers
  (research/kalodata/INSIGHTS_2026-10-28.md:6-73). Uses Nov25–Sep26.
- EASY_WINS (2026-10-31): Jul–Sep 2026 top/riser lists screened by name (Sep revenue ≥$35K, ≥70% video revenue), Nov–Dec
  2025 as Q4 check, CJ costing, hand-weighted 0–100 score (research/kalodata/EASY_WINS_2026-10-31.md:8-41). Verification:
  none of the top 3 CJ matches is the TikTok bestseller (:240-242, 301-307). Not a validated predictor.

---

## 3. Holdout ledger (2025-10 … 2026-09)

Roles: **T** = training rows (features+labels); **S** = model-selection / test month evaluated while choices were
being made; **H** = registered final holdout; **L** = used as an outcome (label) source for an evaluated month;
**D** = descriptive/EDA or live scoring looked at it. Sources: v1 (scripts/train_product_model.py:156-158, 186), pilot
(scripts/pilot_model.py:36), score_breakouts (scripts/score_breakouts.py:39, 44), Phase A audit
(research/kalodata/audit/model_audit_eval.py:407-408, 419, 298-303, 317-326), Phase B (research_runs; scripts/market_eval.py:113-124,
576-583; model_v2 manifest `trained_months`).

| Month | v1 / score_breakouts (10-25) | Pilot | Phase A audit (10-28 00:15) | Phase B select/final + model_v2 (10-28 00:57/00:58) | Descriptive / live | Untouched? |
|---|---|---|---|---|---|---|
| 2025-10 | T (all tasks; partial month) | – | T (except "clean"/drop-Oct probes) | **excluded** | DQ audit; Q4-25 totals | No (and unusable) |
| 2025-11 | T; L for Oct rows | – | T; L | T (first train month, lag features missing) | seasonality, INSIGHTS, EASY_WINS Q4 check | No |
| 2025-12 | T; L | – | T; L | T | same | No |
| 2026-01 | T; L | – | S (1m); T for later origins | S (1m selection); T for later origins | yes | No |
| 2026-02 | T; L | – | S (1m) | S (1m) | yes | No |
| 2026-03 | T (3m train end) | – | S (1m, 3m) | S (1m, 3m) | yes | No |
| 2026-04 | S (3m test); T (1m) | – | S; LOCO test | S (1m, 3m) | yes | No |
| 2026-05 | S (3m test); T (1m) | – | S; LOCO test | S (1m, 3m) | yes | No |
| 2026-06 | S (1m and 3m test) | – | S; LOCO test | S (1m); **H (3m, spent)**; T in v2 final rankers | AI-flag era starts | No |
| 2026-07 | S (1m test); L (3m) | – | S (1m); L | S (1m); L for Jun 3m holdout; T in v2 1m rankers | EASY_WINS screen | No |
| 2026-08 | S (1m test); L | features (Aug) | S (1m); L | **H (1m, spent)**; L for Jun 3m holdout; T in v2 1m rankers | EASY_WINS screen | No |
| 2026-09 | L for Aug 1m test and Jun–Aug 3m test; scored (live) incl. deep risers | labels (Sep) | L; deep-list shift; entrant coverage | **L for both holdouts** (Aug 1m labels; Jun 3m labels Jul–Sep, holders_3m label = exactly Sep); scored by v2 shortlist | video study (Sep videos), AI-by-category, INSIGHTS risers, EASY_WINS, weekly picks 10-26/10-28 | No as data; **yes only as an *observation month never evaluated*** (its labels need Oct–Dec 2026, which are not in the DB) |

Plain statement:
- **No month from 2025-10 to 2026-09 can be called untouched.** Every month has been used for training, model
  selection, final holdout evaluation, outcome labelling, or descriptive pattern-finding.
- The Phase B "frozen" holdouts (Aug 2026 for 1m, Jun 2026 for 3m) were **not clean even before they were spent**:
  v1 tested on Jun–Aug / Apr–Jun (research/kalodata/model_v1_2026-10-25/results.json `test_months`), the Phase A audit
  evaluated Jan–Aug / Mar–Jun ~40 minutes before Phase B (audit file mtimes 00:15 vs research_runs 00:57; 
  docs/MARKET_MODEL_VALIDATION_AUDIT.md:183), the v2 feature set (e.g. `log_vs_floor`) was designed from those audit
  findings, a scratch final run saw them (docs/MARKET_ENGINE_V2_ROADMAP.md:342-345), and the holdout result flipped the
  holders_3m decision (section 2.7). The registry marks them spent (:327, 385).
- Sep 2026 has been used heavily as an outcome month (it labels both spent holdouts) and looked at descriptively; only
  "Sep 2026 features → Oct/Nov/Dec 2026 outcomes" remains unevaluated, and that requires new pulls (no Oct 2026 monthly
  data exist: pull date ranges stop at 2026-09 plus rolling last30/90/365-day windows; DB query 2026-10-31).
- The only genuinely untouched test left is **future data** (Oct 2026 lists onward), which the roadmap names as the
  next honest test: Sep 2026 for 1m tasks once October exists, and the live picks in weekly/history.csv (10-26, 10-28)
  (docs/MARKET_ENGINE_V2_ROADMAP.md:385-386, 395-398; docs/MARKET_MODEL_VALIDATION_AUDIT.md:435-439).
- Practical implication for the new programme [digest]: any retrospective evaluation on this DB is at best a
  "re-used holdout" and should be reported as such; a pre-registered, forward evaluation on Oct 2026+ lists is the only
  clean test. Rolling-origin estimates remain useful for *relative* comparisons but are optimistic for absolute claims.

---

## 4. Established findings worth reusing (with evidence strength) and weak/refuted ones

### 4.1 Reusable
| Finding | Evidence | Strength |
|---|---|---|
| Breakout signal is mostly **distance to the category's 500th-place sales** (floor ratio); one number gets AUC ~0.88–0.90 and ~27–33% top-10/cat | v1 `auc_sales_only` 0.81/0.80 (model_v1 results.json); audit 0.896/0.877 (docs/MARKET_MODEL_VALIDATION_AUDIT.md:203, 222); v2 floor ratio 27.1%/32.9% (docs/MARKET_ENGINE_V2_ROADMAP.md:260, 272); LOCO transfer (docs/MARKET_MODEL_VALIDATION_AUDIT.md:307-309) | Strong, repeated across 3 evaluations (same months though) |
| Logistic on 18 clean features adds only ~1–2 pts top-10/cat over the floor ratio for breakouts | docs/MARKET_ENGINE_V2_ROADMAP.md:301-303, 338-340 | Moderate (CI above 0, small effect, holdout reused) |
| Within a floor band, extra signal is modest (GBM AUC 0.60–0.68) | docs/MARKET_MODEL_VALIDATION_AUDIT.md:231-242 | Moderate |
| Holders 1m: Kalodata growth is the best single rule (~41% top-10/cat vs 30% base); logistic ~54% | docs/MARKET_ENGINE_V2_ROADMAP.md:276-284, 304; audit :244-258; pilot growth bands (PILOT_MODEL:39-45) | Moderate–strong (consistent across pilot, v1, audit, v2), but growth field semantics unknown |
| Holders 3m is mostly "big established sellers stay": rank/floor 82%, persistence 72–74%, logistic ~90% | docs/MARKET_ENGINE_V2_ROADMAP.md:289-295; audit :260-273 | Strong but low business value |
| Only ~4% of new top-500 entrants were on the previous month's riser top 200 | docs/MARKET_MODEL_VALIDATION_AUDIT.md:157-160 | Strong (descriptive, 11 months) |
| Scores are overconfident above ~20%; ≥50% → ~40–49% realised; out-of-range ~32% | docs/MARKET_MODEL_VALIDATION_AUDIT.md:279-299; roadmap :307-311 | Strong |
| Category churn: 3-month top-500 retention Health 68% … Womenswear 42%, Menswear 34%, Collectibles 24% | EXTRA_INSIGHTS:30-34; audit rates it more robust than seasonal peaks (docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:277) | Moderate (one year, ~8 start months) |
| Small-to-big is rare: <$5K risers → ≥$100K later 0.37%, within 3 months 0.21% | log.md:169 | Weak–moderate (no script, no CI) |
| Within a product, sales per 1,000 views roughly constant; winners win on reach (~$22–24 per 1K views) | VIDEO_PILOT:23-26; INSIGHTS:56-57; docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:119-128 | Moderate |
| Paid boosting is common among top videos (76–83% of top-300 after Oct; 90% in Womenswear) and the only video-study result surviving correction | docs/MARKET_DATA_QUALITY_REPORT.md:232, INSIGHTS:54-55; creative audit :24-26 | Strong as association; causal direction unknown |
| Newness matters most at holidays: launches <90 days made 19% of Nov / 17% of Dec revenue vs 9–11% spring/summer | INSIGHTS:33-35 | Weak–moderate (one season; launch date is a current value) |

### 4.2 Weak, overstated or refuted
| Claim | Status | Evidence |
|---|---|---|
| Breakout GBM AUC 0.89/0.88 = skill | Refuted as skill: floor rule ties/beats it; HGB never adopted | docs/MARKET_MODEL_VALIDATION_AUDIT.md:23-24; roadmap :329-331 |
| "≥50% chance" breakout picks | Refuted: 42% (3m), 32% out of range | docs/MARKET_MODEL_VALIDATION_AUDIT.md:26, 292-296 |
| "94% of top 10 per category stay 3 months" | True but trivial (83% for top-10 sellers) | docs/MARKET_MODEL_VALIDATION_AUDIT.md:22 |
| v1 "growth alone" baseline (0.51–0.52) | Deliberately weak baseline | docs/MARKET_MODEL_VALIDATION_AUDIT.md:34-35 |
| "Moderate growth beats explosive", "priced above category norm", "many variants" | Descriptive of one model on a growth-selected sample; variants = current SKU (leak) | docs/MARKET_MODEL_VALIDATION_AUDIT.md:149-152, 333-337 |
| Commission effects (0% rarely breaks out) | Ordering clear, but Oct-2026 commission, confounded; "not evidence for any commission policy" | docs/MARKET_MODEL_VALIDATION_AUDIT.md:338-343 |
| Breadth (creators/videos) +0.013 AUC | 649 rows, shuffled CV, not forward | MODEL_V1:55-58; audit :113-114 |
| Deep-list (201–1,000) breakout scores | Unvalidated, out of distribution (~2× too high) | docs/MARKET_MODEL_VALIDATION_AUDIT.md:147-156 |
| Seasonal peaks (boots Nov, dresses May, etc.) | Observed once; "sweater dresses peak in spring" overstated; "heating up" includes ~11% market growth | docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:262-282; CATEGORY_SEASONALITY:3-8 |
| Weekly report post-model filters (price, sales ≥$3K, steady, commission) | Never validated | docs/MARKET_MODEL_VALIDATION_AUDIT.md:344-345; roadmap :364, 382 |
| Video creative findings (person at 0 s, length, words/s, speech share, text hook, close-ups) | Do not survive correction; vanish within same-paid-status pairs | docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:24-36, 160-198 |
| "25% of videos are AI" (10-25 findings) | Came from keyword searches, not top videos; ~1% in top Womenswear videos | INSIGHTS:63-65 |
| AI ≥$1K hit odds "1 in 84" | Corrected to ~1 in 193 | VIDEO_HIT_RATES:26-32 |
| "Womenswear 0 of 61 AI videos made $1K" | Mostly product mix (expected ~4.1 hits; Poisson p≈0.02) | docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:286-289 |
| EASY_WINS top picks | CJ matches are different products from the TikTok bestsellers | EASY_WINS:240-242, 301-307 |

---

## 5. Video research findings

| Study | Sample | What was concluded | Status |
|---|---|---|---|
| Video hit rates (2026-10-25) | 5 successful dresses, 3,399 videos, $390K, last 30 days to 10-25 | ≥$1K: 1 in 46; ≥$5K: 1 in 200; AI ≥$1K corrected to ~1 in 193; top-10 videos take 50–90% of a product's sales (research/kalodata/VIDEO_HIT_RATES_2026-10-25.md:9-32) | Selected successful products only; odds worse for average products (:51-56) |
| Video lifespan (same pulls) | 1,178 selling videos ($668K) | 82% of selling videos ≤30 days old; half of sales from videos >30 days; paid videos last longer (VIDEO_HIT_RATES:59-80) | One snapshot, not tracked over time (:79-81) |
| Video pilot (2026-10-26) | 3 winners end-to-end, then 5 winner/comparison pairs | Winners show product on a person at 0 s, longer, 4/5 spoken CTA; within a product, sales per view ~constant → winners win on reach; Kalodata refuses low-view downloads (403, still charged) (research/kalodata/VIDEO_PILOT_2026-10-26.md:7-56) | "Hints only" (:53) |
| Video study (Sep 2026) | 91 pairs / 182 videos, 25 categories (Womenswear 4, apparel 22), 152 tests | Raw p<0.05: person at 0 s, first frame person+product, duration; only `ad=1` (84% vs 41%, 43:4) survives Holm/BH; person-with-product OR 2.40 → 1.34 (0.66–2.72) after adjusting for paid; video age unmatched (37 vs 17 days); tags not hand-checked (AI tag 8/17) (research/kalodata/VIDEO_STUDY_2026-10.md:3-17, 21-43; docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:24-36, 57-71) | Creative effects "promising, unproven"; `rules.yaml` gates (2.9–3.8 words/s, 70% speech) are defaults, not proven (owner D3) (VIDEO_STUDY:13-14; roadmap :202-203) |
| Background music | 185 videos, 91 pairs | No difference (14 vs 19 discordant, p=0.49) (VIDEO_STUDY:240-257) | Honest null |
| AI video by category (2026-10-26) | Top-300 Jun–Sep (4,800 videos/category); full lists ~4 products/category Sep | AI 4.7% of top-300 videos (4.0% → 5.8%); AI sells ~same as human once in top list, higher $/view; weak in Womenswear/Shoes, better in Books/Menswear/Tools/Health (research/kalodata/AI_VIDEO_BY_CATEGORY_2026-10-26.md:6-50) | 4 months of a Kalodata-estimated flag; view 2 small samples (:51-52); Womenswear 0/61 is mostly product mix |
| Top-video traits, Womenswear (INSIGHTS) | 3,300 video-months | 90% boosted; ~$22/1K views; views track revenue (ρ 0.43) far more than likes (0.18–0.23); median top video 36 days old; 1,221 creators, top 10% of videos 23% of revenue (research/kalodata/INSIGHTS_2026-10-28.md:53-67) | Descriptive |

Data caveats specific to videos: AI flag NULL before Jun 2026; ROAS/ad share capped estimates; video growth field
unusable; views monthly vs likes lifetime; 40 of 100 full lists truncated; slideshow posts excluded from the study
(docs/MARKET_DATA_QUALITY_REPORT.md:342-354; docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:101-103, 144-147).

---

## 6. Open questions and caveats prior work left

1. **No clean holdout remains** (section 3). Oct 2026 monthly lists are needed to mature Sep-observation labels and to
   score the logged 10-26 / 10-28 picks; pulling them costs credits (~1.5/category) and needs owner approval
   (docs/MARKET_ENGINE_V2_ROADMAP.md:120-121, 395-398).
2. **Kalodata `revenue_growth_rate` definition** is unknown, yet it is the best single rule for holders_1m
   (docs/MARKET_DATA_QUALITY_REPORT.md:331-334, 495).
3. **Revisions / vintage**: unmeasured; proposed monthly re-pull log (docs/MARKET_DATA_QUALITY_REPORT.md:494).
4. **Population gap**: ~96% of top-500 entrants come from outside risers 1–200; widening to sales ranks 501–1,000
   (D6) was deferred (docs/MARKET_MODEL_VALIDATION_AUDIT.md:401; roadmap :199, 204, 378-379).
5. **Deep-list (201–1,000) scores unvalidated** (docs/MARKET_MODEL_VALIDATION_AUDIT.md:399-400).
6. **Seasonality untested**: one year; no Nov–Dec observation month has a forward test; 3m tasks have only 4 origins
   (docs/MARKET_MODEL_VALIDATION_AUDIT.md:355-357; roadmap :376-377). First check Nov–Dec 2026 vs 2025
   (docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md:280-282).
7. **Decision-rule interpretation** (ladder vs literal) awaits owner confirmation (docs/MARKET_ENGINE_V2_ROADMAP.md:332-336).
8. **Relist / listing identity clusters** not built; relisted products look new (docs/MARKET_DATA_QUALITY_REPORT.md:284-286, 493;
   roadmap :392-394).
9. **Point-in-time attributes**: no dated history of commission, SKU, reviews, launch date; only current values
   (docs/MARKET_MODEL_VALIDATION_AUDIT.md:411-413).
10. **Per-category reliability**: gains are averages; Womenswear breakout rankers weak (12.5–17.5% top-10 vs 2.8% base;
    40 picks) (docs/MARKET_ENGINE_V2_ROADMAP.md:313-315).
11. **`seller_id` assumed static** (untested) (docs/MARKET_ENGINE_V2_ROADMAP.md:381).
12. **Weekly filters and `--scan` path unvalidated**; scan windows (last 30 days) mislabelled as calendar months
    (docs/MARKET_ENGINE_V2_ROADMAP.md:382-384; docs/MARKET_MODEL_VALIDATION_AUDIT.md:162-164).
13. **Ad-hoc analyses without scripts** (commission, small-to-big, seasonality CSVs) are not reproducible
    (docs/MARKET_ENGINE_AUDIT.md:53-55; docs/MARKET_MODEL_VALIDATION_AUDIT.md:370-371).
14. **Video study redesign** needed: match on paid status and posting week, attempts table, hand-check tags
    (docs/MARKET_ENGINE_V2_ROADMAP.md:140-147).
15. **Market ≠ our results**: Kalodata estimates in-app TikTok Shop demand; our store's conversion, delivery time and
    price position differ (INSIGHTS:7-8, 49-51; MODEL_V1:67). Closed-loop validation is Phase I (roadmap :169-172).
16. **INSIGHTS Aug–Sep "double" totals** inconsistent with the data-quality table (section 1.8).
17. Loader stale-failure defect fixed in B0 per commit 8c598e9 message (git log), but the data-quality report's
    `comment_insights` count (18 vs 24) predates that fix [digest: not re-checked].
