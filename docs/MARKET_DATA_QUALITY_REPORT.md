# Kalodata Research Database — Data Quality Audit (Market Intelligence Engine 2.0, Phase A)

Date: 2026-10-28. Scope: `research/kalodata/kalodata.db` (397 MB), the raw API responses in
`research/kalodata/raw/` (5,153 files), the loader `scripts/kalodata_db.py` and the downloader
`scripts/kalodata_core.py`. Method: read-only SQLite queries (`mode=ro`), pandas checks, and reading raw JSON files.
**No API calls were made. The database, raw files, scripts, models and reports were not changed.** The only data file
written is the coverage matrix (section 4).

Tags: **[V]** = verified by a query or file shown here; **[I]** = inferred from the evidence, not proven.

---

## 1. Summary

The core dataset is **complete as a download.** Every page the downloader asked for in the 28 usable categories came
back full (5/5 top-500 pages, 2/2 riser pages and 3/3 video pages for all 336 category-months), and the numbers are
internally consistent (revenue = units × price, channel revenues sum to the total, sort order holds). The problems
are about **what the numbers mean and when they were measured**, not missing rows:

1. **October 2025 is a partial month, about one week long.** For the same product, October revenue is a median 24%
   of its November revenue (August vs September for comparison: 109%). Top-500 revenue in October is 29% of the
   2026 monthly average. Videos in the October list were mostly published 20–28 October. Every October growth rate
   is exactly 100 (a placeholder for "no earlier period"), so **the October riser list is in no particular order.**
   November growth figures are measured against this partial month. [V numbers, I "one week"]
2. **Everything was collected in a single 4-hour window** (2026-10-25 19:22 → 23:19 Eastern). No collection time is
   stored in the database or the raw files; only the file modified time records it. Each month is a look back from
   25 October 2026, not what anyone could have seen at the time. [V]
3. **Several product fields are today's values, repeated for every month:** product name, seller, launch date,
   SKU count and commission rate are identical in every month for all 34,718 products seen in more than one month.
   Review count in product detail is also current. Using commission or SKU count as a historical feature leaks
   October 2026 information into earlier months. [V]
4. **`revenue_growth_rate` is not a simple month-on-month change.** It matches our own consecutive-month revenue
   within 0.5 points for only 0.7% of 99,736 product pairs. 4,169 rows show −100% with positive revenue. For videos,
   97% of growth values are below −100%. The value 100 means "no earlier period" (all of October; 74% of the other
   100s are products launched that month). [V]
5. **The AI flag is 0, not empty, before June 2026.** All 67,200 top-300 video rows for Oct–May have `ai_video = 0`.
   This is missing data stored as "not AI". [V]
6. **Small problems:** Virtual Products returned nothing for any month (29 categories requested, 28 usable).
   Womenswear Aug+Sep top-500 is stored twice (1,000 duplicate rows from the pilot). 159 product-months appear in two
   categories with different revenue (each category gets its own share). Video lists repeat some videos (129 rows in
   top-300 lists, 3,397 in full-product lists). 40 of the 100 full-video-list products hit the 5-page cap. The loader
   kept 6 failed comment-insight pulls that were later retried successfully. [V]
7. **Revisions cannot be measured.** The only repeated queries (pilot Womenswear Aug/Sep, 1,000 rows) were re-pulled
   5 hours later and match exactly. There is no earlier copy of any month, so we cannot tell how much Kalodata
   revises figures after the fact. [V]

**Recommended exclusions for training:** October 2025 (all lists) as features and as the "previous month" for
November; Virtual Products (no data); Pre-Owned and Muslim Fashion flagged as thin (their top-500 cut-offs are
$1,360 and $359 a month); AI flag before June 2026; commission rate, SKU count and review count as historical
features. Details in section 9.

---

## 2. Schema and counts

### 2.1 Tables (row counts verified 2026-10-28) [V]

| Table | Rows | What one row is | Notes |
|---|---:|---|---|
| `pulls` | 5,153 | one saved API response (one raw file) | 1:1 with the 5,153 raw files |
| `products` | 259,418 | one product on one rank page | 257,600 from core pulls + 1,818 from pilots/probes/keyword pulls |
| `videos` | 135,653 | one video on one video-rank page | 132,961 core + 2,692 other |
| `product_details` | 1,036 | one product-detail response | 1,003 core (988 distinct products) + 33 other |
| `categories` | 807 | one category on a category ranking | windows `last30Day` / `last90Day` / `last365Day` only |
| `comment_insights` | 18 | one comment summary | raw folder holds 24 successful ones (see 5.6) |
| `video_features` | 185 | derived (video study) | `created_at` stored |
| `video_elements` | 184 | derived (element tags) | `created_at` stored |
| `video_audio` | 185 | derived (music study) | `at` stored |

### 2.2 Columns that matter for quality [V]

- `pulls`: `pull_id, file (UNIQUE), pulled_on, name, endpoint, region, date_range, filters, http_status, success,
  n_records`. **Not stored:** collection timestamp, credit cost, currency/language (stripped from `filters`; all
  rank and detail requests used `US`/`USD` per the raw files: 5,107 of 5,153 files say `"currency": "USD"`, the rest
  are balance, comment and video-URL calls).
- `pulled_on` is the raw **folder name**, so it is `core` for 4,986 of 5,153 pulls. It is not a date.
- Typed tables store `position` **within the page (1–100)**, not the rank. Rank must be rebuilt from the pull name
  (`(page−1)×100 + position`). Category, month and list type exist **only in the pull name** (`core_<phase>_<month>_<cat>_p<n>`).
- Columns are untyped (`revenue`, `sku_count` etc. have no declared type); `sku_count` arrives as a string.
- Every record keeps its full JSON in `raw_json`. Fields not given their own column: `master_image_url` (always
  null), `creator_debut` (videos), `product_region` and `product_description` (details), `cached_at` (comments).

### 2.3 Indexes [V]

`pulls.file` (unique autoindex); `ix_<table>_pull` on `pull_id` for all five typed tables; `ix_products_key`
(`product_id`), `ix_videos_key` (`video_id`), `ix_product_details_key` (`product_id`); primary keys on the three
derived video tables. There is **no index on `pulls.name`**, although every analysis filters by `name LIKE 'core_…'`.

---

## 3. Pull inventory

### 3.1 By folder and endpoint [V]

| Folder | Endpoint | Pulls | Successful | Records |
|---|---|---:|---:|---:|
| core | product/rank | 2,600 | 2,576 | 257,600 |
| core | video/rank | 1,379 | 1,364 | 132,961 |
| core | product/detail | 1,003 | 1,003 | 1,003 |
| core | category/rank | 4 | 4 | 74 |
| 2026-10-25 (pilots, probes) | product/rank, video/rank, detail, comments, category | 79 | 74 | 4,379 |
| weekly_2026-10-26 | detail, video/rank, comments, balance | 55 | 47 | 208 |
| subcats_2026-10-26 | category/rank, product/rank | 10 | 10 | 706 |
| pilot_videos, 2026-10-26 | video url/detail/download, balance | 23 | 22 | 1 |

### 3.2 Core pulls by phase [V]

| Phase (pull name) | Pulls | OK | Rows | Months | Shape |
|---|---:|---:|---:|---|---|
| `core_products` | 1,692 | 1,680 | 168,000 | Oct 2025–Sep 2026 | 29 cats × 12 months × 5 pages (Virtual Products 1 failed page each month) |
| `core_risers` pages 1–2 | 684 | 672 | 67,200 | Oct 2025–Sep 2026 | 29 × 12 × 2 |
| `core_risers` pages 3–10 ("deep risers") | 224 | 224 | 22,400 | Sep 2026 only | 28 × 8 pages, positions 201–1,000 |
| `core_videos` | 1,020 | 1,008 | 100,800 | Oct 2025–Sep 2026 | 29 × 12 × 3 |
| `core_detail` | 1,003 | 1,003 | 1,003 | Oct 2025–Sep 2026 | 3 per category-month (327), 2 (8), 6 (1: Womenswear Sep, incl. 3 from a test run) |
| `core_allvideos` | 359 | 356 | 32,161 | Sep 2026 | 100 products, up to 5 pages each |
| `core_categories` | 4 | 4 | 74 | last30Day, last365Day | level 1 and level 2 |

The deep-riser pages use the **same name prefix as ordinary risers** (`core_risers_2026-09_<cat>_p3…p10`). Any code
that treats `core_risers_*` as "top 200 risers" silently mixes in 22,400 rows from positions 201–1,000 for September
only. `scripts/train_product_model.py` loads all `core_risers_%`. [V]

### 3.3 Failed, empty and partial pulls [V]

53 pulls have `success = 0` (52 with HTTP 200, 1 with HTTP 404):

- **Virtual Products (834312):** 36 — page 1 of products, risers and videos for all 12 months, message
  `"product not found"` / `"video not found"`. The category's last-30-day revenue equals its last-365-day revenue
  ($855,212), so it appears to have existed only recently. [V numbers, I reason]
- **Full video lists:** 3 — page 1 for product 1731959041020235925 (Muslim Fashion, so no videos at all), and
  pages 4 and 5 that ran past the end of the list (normal end-of-list).
- **Probes:** 6 expected failures (history before Oct 2025, level-3 categories, invalid `revenue_range` filter,
  video download 404).
- **Weekly comment insights:** 8 recorded as failed; 6 of them were retried successfully later (raw file now says
  `success: true`), but the database still holds the failure because the loader never re-reads a file it has
  already loaded (section 5.6).

No successful core page was short: every product, riser and video page has exactly 100 records. [V]

### 3.4 Duplicate pulls of the same query [V]

12 query keys (endpoint + date range + filters, ignoring `need_extra`) were pulled twice:

- `pilot_womenswear_2026-08_p1…p5` and `pilot_womenswear_2026-09_p1…p5` duplicate the core Womenswear Aug and Sep
  top-500 pages: **1,000 duplicate product rows.** Values are identical (revenue, units, price, growth, commission,
  channel revenues, SKU count and rank all match for 1,000/1,000).
- Two category-ranking pulls (`category_l1`, `category_l2_womens`) duplicate core category pulls.

Effect: any query on `products` that does not filter to `core_%` pull names counts Womenswear Aug/Sep twice and also
picks up keyword, price-band and `last30Day` pulls that are not monthly. The model scripts do filter by name; ad-hoc
queries may not.

### 3.5 What is and isn't stored per pull [V]

| Item | Stored? | Where |
|---|---|---|
| Endpoint | yes | `pulls.endpoint` (from raw `path`; inferred from file prefix for the first files) |
| Request parameters | mostly | `pulls.filters` (region separate; language/currency dropped, kept in raw) |
| Date range (event period) | yes | `pulls.date_range` (`YYYY-MM` or `lastNDay`) |
| HTTP status / success | yes | `http_status`, `success`; error message only in raw |
| Records returned | yes | `n_records` |
| Credit cost | **no** | only script constants (0.1 per call) and log totals (478.2 charged by script) |
| Collection timestamp | **no** | neither raw envelope nor DB; only file mtime |

---

## 4. Coverage matrix

Full matrix: **`research/kalodata/audit/coverage_matrix_2026-10-28.csv`** — 348 rows (29 categories × 12 months),
44 columns: pages expected/ok per list, failed pulls, top-500 rows/distinct/total/median/rank-500 revenue,
growth-placeholder share, riser and deep-riser rows, cross-category products, same-seller-same-title duplicate IDs,
video rows/distinct/duplicates/zero-revenue rows/ad and AI shares, AI-flag populated, detail rows and distinct
subcategories, full-video-list products, missing pages, first/last collection time (UTC), days from month end to
collection, revenue vs the category's 2026 average, and a `quality_flags` column.

### 4.1 By month (all 29 categories) [V]

| Month | Top-500 rows | Riser rows | Deep riser rows | Video rows | Details | Missing pages | Top-500 revenue | Rev. vs 2026 avg | Collected (days after month end) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-10 | 14,000 | 5,600 | 0 | 8,400 | 82 | 10 | $236.7M | **0.29** | ~358 |
| 2025-11 | 14,000 | 5,600 | 0 | 8,400 | 83 | 10 | $1,084.6M | 1.31 | ~329 |
| 2025-12 | 14,000 | 5,600 | 0 | 8,400 | 84 | 10 | $1,004.1M | 1.21 | ~298 |
| 2026-01 | 14,000 | 5,600 | 0 | 8,400 | 84 | 10 | $743.3M | 0.90 | ~267 |
| 2026-02 | 14,000 | 5,600 | 0 | 8,400 | 84 | 10 | $715.8M | 0.86 | ~239 |
| 2026-03 | 14,000 | 5,600 | 0 | 8,400 | 83 | 10 | $922.4M | 1.11 | ~208 |
| 2026-04 | 14,000 | 5,600 | 0 | 8,400 | 84 | 10 | $810.7M | 0.98 | ~178 |
| 2026-05 | 14,000 | 5,600 | 0 | 8,400 | 84 | 10 | $811.1M | 0.98 | ~147 |
| 2026-06 | 14,000 | 5,600 | 0 | 8,400 | 85 | 10 | $895.2M | 1.08 | ~117 |
| 2026-07 | 14,000 | 5,600 | 0 | 8,400 | 83 | 10 | $868.7M | 1.05 | ~86 |
| 2026-08 | 14,000 | 5,600 | 0 | 8,400 | 82 | 10 | $855.2M | 1.03 | ~55 |
| 2026-09 | 14,000 | 5,600 | 22,400 | 8,400 | 86 | 18 | $835.7M | 1.01 | ~24 |

"Missing pages" = the 10 Virtual Products pages each month (+8 deep-riser pages for Virtual Products in September).
Each list really has 500 / 200 / 300 rows in all 28 usable categories (no short pages, no duplicate product IDs
within a list). Subcategory is available only for the 1,003 detail rows (`sec_cate_id`); rank rows carry no
category field at all, only the category used as a filter.

### 4.2 Category notes [V]

- **Virtual Products:** no data for any month (flag `no_data`, 12 rows).
- **Thin categories:** Muslim Fashion (Sep top-500 total $0.92M; rank-500 product sells $359/month; riser median
  $175) and Pre-Owned ($1.36M; rank 500 = $1,360). Pre-Owned's top-300 video lists run out of selling videos: 1,413
  zero-revenue video rows across 9 months, and the riser lists in both categories run out of growing products
  (1,897 Pre-Owned and 120 Muslim Fashion riser rows carry the growth placeholder 100).
- For comparison, rank 500 in Sep 2026 is $97,796 in Beauty and $80,416 in Womenswear. "Top 500" means very
  different things across categories.
- `quality_flags` counts: ok 104; ai_flag_unpopulated 156; partial_month (Oct 2025) 28; growth_vs_partial_prior
  (Nov 2025) 28; thin_category 24; video_list_tail_zero 9; no_data 12 (flags combine).

### 4.3 Latest month (Sep 2026) [V]

Complete and in line with August (top-500 revenue $835.7M vs $855.2M; median product $31.6K vs $33.2K; 64.8% of
September's top 500 were in August's top 500, against 56–66% for other months). It was collected 24–25 days after
month end, the shortest gap in the set. Only 7 of 32,161 full-list video rows have a publish date after the month
(2026-10-01 before 01:23), which looks like a time-zone edge, not leakage. [V; I for the time-zone reading]

---

## 5. Integrity issues

### 5.1 October 2025 is a partial month [V numbers, I cause]

| Check | Oct 2025 | Reference |
|---|---|---|
| Top-500 revenue, all categories | $236.7M | Nov $1,084.6M; 2026 average $827M (ratio 0.29) |
| Median top-500 product | $7,982 | Nov $37,182 (4.7×) |
| Median rank-500 product | $3,695 | Nov $16,650 |
| Same product, Oct ÷ Nov revenue (n = 8,120) | median 0.24 (IQR 0.16–0.36) | Aug ÷ Sep (n = 9,076): median 1.09 |
| Median top-300 video views | 108K | Nov 725K |
| Riser median revenue | $66 | Nov $1,371 |
| Top-300 video revenue | $30.4M | Nov $257.1M |
| Growth rate = 100 (placeholder) | 100% of rows, all lists | 2.5–5.7% in other months |
| Ad-flagged share of top-300 videos | 63% | 76–83% in other months |

Every category is affected (Oct ÷ 2026 average ranges from 0.18 Furniture to 0.65 Toys). Publish dates of in-month
videos in the October list peak on 20–28 October (e.g. 351 on the 24th vs 77 on the 1st), while November's are flat.
A same-product ratio of 0.24 is about 7 days of a 30-day month: Kalodata's monthly history appears to start around
22–24 October 2025 (the 2025-04 and 2024-10 probes return "not found"). Consequences:

- October revenue, units, views and video revenue are on a different scale from every other month.
- The October riser list is sorted by a constant (all growth = 100), so its order is arbitrary: revenue rises
  and falls along the list in equal measure (2,692 up-steps, 2,755 down-steps in 5,600 rows), and only 7.1% of
  October risers are also in October's top 500.
- November growth and any "previous month" feature built from October are inflated (median top-500 growth in
  November is +62%).

### 5.2 Same product in two categories in one month [V]

159 product-months (156 in top-500 lists, 3 in risers) appear in two category lists in the same month. In **all 159**
the revenue and units differ between the two rows (e.g. a Costway washing machine, Feb 2026: $67,899 in Home Supplies,
$13,999 in Home Improvement). Commission is the same. So a category-filtered rank reports the revenue earned **in
that category** [I: probably products moved category during the month]. Summing within a category is correct;
product-level monthly totals must **sum across categories**. `train_product_model.py` keeps the first row per
product-month (`drop_duplicates(["product_id","month"])`), so these 159 product-months carry only part of their
revenue.

Related: in 40 of 1,003 detail rows the detail endpoint reports more revenue than the rank row for the same
product-month-category (median +14%, max 2.0×); 95% match exactly. Only 1 of the 40 has a different primary category
and none appear in a second category list, so the extra revenue is probably earned in categories where the product
is outside the top 500. [V counts, I reason]

### 5.3 Duplicate rows [V]

| Where | Count | Cause |
|---|---:|---|
| Product appears twice in one list (month × category × list) | **0** | — |
| Womenswear Aug/Sep top 500 (pilot + core) | 1,000 rows | duplicate pulls, identical values |
| Product in both top-500 and top-200 risers, same month and category | 4,982 | expected overlap; values identical in all fields |
| Deep risers also in top 500 | 798 of 22,400 | expected; identical values; 0 overlap with risers 1–200 |
| Video repeated in a top-300 list | 129 rows | Pre-Owned 127, Muslim Fashion 2: ties at $0 revenue paginate unstably, so the same video lands on two pages (and others are skipped) |
| Same video twice on the same page with different views | seen (e.g. 7468739609820761387, views 248 and 154) | [I] the video list is per video × product link |
| Video in two categories in one month | 48 of 100,618 | revenue and views differ per category (same rule as products) |
| Video repeated in full-product lists | 3,397 rows (32,161 rows, 28,764 distinct) | unstable ordering of $0 / tied rows across pages |

40 of the 100 full-video-list products filled all 5 pages (500 rows), so their lists are **truncated**; the
"all videos for 100 products" set is complete for only 60 products. [V]

### 5.4 Product ID changes and near-duplicate listings [V counts, I interpretation]

- No product ID ever changes title or seller across months (0 of 135,918) — but that is because those fields are
  current values (section 7), not evidence of stability.
- **Same seller + same normalised title, different product ID, same month and category:** 825 groups, 1,776 IDs
  (47–101 groups per month). Examples: Hotel Collection diffuser kit (two IDs at ranks 38 and 424, Oct 2025);
  "NADIA BOX 3 throw blanket" listed twice by one seller a day apart. Loosening to seller + first 60 title
  characters: 1,738 groups, 3,772 IDs, 1.5% of product-month rows. Same title across any seller: 1,583 groups.
- Across months, 779 seller + title pairs map to more than one ID — candidates for relisted products whose history is
  split across IDs. A breakout model sees a relisted product as a brand-new one.

### 5.5 Historical revisions [V]

- Within the core run, a product that appears in two lists (top 500 and risers) has identical values in every field
  (4,982 + 798 pairs): no inconsistency inside one snapshot.
- Pilot pulls at 16:11 Eastern vs core pulls of the same pages ~5 hours later: 1,000/1,000 rows identical,
  including rank. The October probe (10 rows, 15:57 Eastern) and growth-sort probe (10 rows) also match.
- **There is no second vintage of any month.** We cannot say whether Kalodata revises past months (late orders,
  refunds, model updates). Training data are the values as settled by 25 Oct 2026; live scoring will see first
  estimates of the most recent period. This gap is untested.

### 5.6 Loader defects [V]

- `ingest_file` skips any file already in `pulls`. When a failed call is retried, the raw file is overwritten with
  the success, but the DB keeps the old failure. Six weekly comment-insight pulls (pull_ids 5068, 5071, 5086, 5092,
  5112, 5115) are `success = 0` in the DB but `success: true` with data in raw. `comment_insights` has 18 rows;
  it should have 24.
- `pulled_on` = folder name, so it records "core" rather than a date (section 3.5).
- Page-relative `position` and name-encoded category/month/list (section 2.2) push rank reconstruction into
  every script; the deep-riser naming collision (3.2) follows from this.

---

## 6. Metric sanity

### 6.1 Products (257,600 core rows) [V]

| Check | Result |
|---|---|
| Nulls | none in revenue, units, price, growth, commission, channel revenues, launch date, seller; `sku_count` null in 21 rows; 161 empty `seller_name`, 2 empty `product_name` |
| Negative values | none in any numeric field |
| Zero values | revenue 0, units 0, price 0; commission 0 in 84,370 rows (unbranded/no affiliate); live 0 in 90,403; video 0 in 67,487 |
| Revenue vs units × unit_price | 100% within 1% (1st–99th percentile ratio 0.999–1.001). `unit_price` is revenue ÷ units (average realised price, 2 decimals), not a list price |
| Live + video + showcase vs revenue | sums exactly (0 rows off by >1%) |
| Sort order | 0 revenue-order violations in top-500 lists; 0 growth-order violations in riser lists |
| Extremes | revenue max $6.80M/month (Mar 2026); units max 281,306; unit price $0.10–$4,999 (3,113 rows > $1,000, 76 < $1); commission up to 79% (28 rows > 50%) |
| Launch date | 2023-07-21 → 2026-09-28; 0 rows launched after the month they are reported in |
| Currency | all monthly pulls requested `USD`, region `US` |

### 6.2 Growth rate definition [V]

- Values range −100 to +2,512,415. Median: top-500 +11.8%, risers +1,880%, deep risers +467%.
- `100` exactly = no earlier period: 100% of October rows; elsewhere 5,432 top-500 rows, 74% launched in the
  reported month. It collides with genuine +100% growth.
- Compared with our own month-on-month change for the same product (99,736 pairs, single-category products):
  within 0.5 points 0.7%, within 2 points 2.9%; implied-prior ÷ actual-prior ratio has an IQR of 0.53–1.39.
  Day-count adjustment and units-based growth do no better. Kalodata's growth uses a different comparison window
  or base, not documented anywhere in the Hub. [I: likely a different comparison window]
- 4,169 product rows are exactly −100% while revenue is positive.
- Videos: 97.2% of `revenue_growth_rate` values are below −100% (median −198%, min −65,500%). The video field
  cannot be a percentage change of reported revenue.
- **Risk:** the model's strongest signal family is growth (`growth_slog` and riser lists sorted by this field).
  Riser lists exclude brand-new launches by construction: their growth is the placeholder 100, below the ~1,000%
  needed to reach position 200 (rank-200 growth median 917–1,455% by month). [V numbers, I effect]

### 6.3 Videos (100,800 top-300 rows + 32,161 full-list rows) [V]

| Check | Result |
|---|---|
| Nulls | none in any column |
| AI flag | 0 in every row Oct 2025–May 2026 (67,200 rows); 1 in 4.0% (Jun) → 5.8% (Sep). Before June, 0 means unknown |
| Ad flag | 63% in Oct 2025, 76–83% after; ad = 1 ⇔ ROAS > 0 ⇔ ad-revenue ratio > 0 in all rows (perfectly consistent) |
| ROAS | 0 for all 39,996 organic rows; max exactly **20.0** (169 rows at the cap) |
| Ad-revenue ratio | max exactly **80.0%**; 42,683 rows (46% of ad videos) sit at the 80% cap — a model output with a ceiling |
| Views vs likes | 2,168 rows have fewer views than likes [I: views are counted for the month, likes are lifetime] |
| Zero revenue | 16,423 rows (mostly full-product lists; 1,413 in Pre-Owned top-300 lists) |
| Publish date | format `YYYY/MM/DD HH:MM:SS`, all parse; 7 rows after month end (Sep, 1 Oct before 01:23) |
| In-month share | 32–43% of top-300 videos are published in the reported month (Oct 2025: 62%, consistent with a short window) |

### 6.4 Product details (1,003 core) [V]

- No nulls; revenue = video + live + mall exactly; delivery type local 791 / global 211 / unknown 1.
- `revenue_trend` is null in all 1,036 rows (no daily series available).
- `product_review_count` is identical across months for all 15 products detailed in more than one month: it is the
  count on the collection date.
- 20 detail rows have a primary category different from the category list they were sampled from.

---

## 7. Estimated vs observed

No response contains a methodology note, confidence value or "estimated" field name. The envelope is only
`success, data, message, cached, code` (`cached` is always null in rank responses). What the evidence shows:

| Field family | Status | Evidence |
|---|---|---|
| Revenue, units, channel split (video/live/showcase/mall) | **Estimate** (Kalodata model; method not published) | exact arithmetic identities (units × price, channel sums) show a modelled decomposition, not raw transactions; earlier Hub notes call these estimates (`KALODATA_FINDINGS`, `FULL_DATASET_PLAN`, `PROVIDER_COMPARISON`: "method not published") [V identities, I nature] |
| `unit_price` | Derived (revenue ÷ units) | 100% within 0.1% [V] |
| `revenue_growth_rate` | Derived, undocumented definition | does not reproduce (6.2) [V] |
| Ad flag, ROAS, ad-revenue ratio, ad-view ratio | **Estimate** with hard caps (ROAS 20, ad share 80%) | caps visible in data [V] |
| AI flag | Kalodata classifier, Jun 2026 onward only | 0 before June [V]; own estimate per `AI_VIDEO_BY_CATEGORY` |
| Views, likes, shares, comments, publish date, creator | Observed platform counts (scraped) [I] | integer counts; window differs between views and likes [I] |
| Name, seller, launch date, SKU count, commission, review count | Observed, **current at collection** | identical across months (section 8) [V] |
| Category ranks (`last30Day`/`last365Day`) | Estimate, rolling window ending at pull date | not month-aligned |
| Comment insights | AI summary, cached by Kalodata | `cached_at` from 2025-07-08 to 2026-10-26 [V] |

---

## 8. Timestamps and look-ahead risk

### 8.1 What exists [V]

| Timestamp | Meaning | Available for |
|---|---|---|
| `pulls.date_range` | event period (calendar month, or rolling `lastNDay`) | all pulls |
| `videos.publish_date` | event time of the video | all videos |
| `launch_date` | product listing date (static) | products, details |
| `creator_debut` (raw only) | creator's first date | videos |
| `comment_insights.cached_at` (raw only) | when Kalodata generated the summary | 18 rows (as old as 15 months) |
| Derived tables `created_at` / `at` | when we computed features | video study tables |
| **Collection time** | **not stored** | only raw file mtime |

Raw file mtimes put the whole core run at **2026-10-25 23:22:49 → 2026-10-26 03:19:33 UTC** (19:22–23:19 Eastern,
25 Oct). Months were fetched in order, ~12 minutes each; the deep-riser pages at 03:13–03:19 UTC. Files in
`raw/2026-10-25/` (research, pilots, probes) carry mtimes from 14:43 Eastern on 25 Oct onward; the pilot Womenswear
pages are from 16:11 Eastern. Mtimes change if files are copied or restored (the nightly backup
or a git checkout could reset them), so they are a weak record. [V]

### 8.2 Look-ahead risks for model training [V facts, I impact]

1. **Snapshot attributes.** For all 34,718 products seen in more than one month, product name, seller, launch date,
   SKU count and commission rate have exactly one value. Unit price varies (34,204 of 34,718) because it is
   computed per month. Commission rate and SKU count as of Oct 2026 are used as features for months back to
   Oct 2025 in `train_product_model.py`, `pilot_model.py` and the breakout scorer. A product that later raised
   commission or added variants because it was selling well leaks its future into its past.
2. **Review count** in details is current, not as of the detail month.
3. **Retrospective vintage.** All months were measured on one day. If Kalodata revises past figures, training sees
   settled values while live weekly scoring (`last30Day`, pulled fresh) sees first estimates.
4. **Rolling windows.** Category rankings and weekly pulls use `last30Day`/`last365Day` ending on the pull date. The
   `last365Day` window (Oct 2025–Oct 2026) includes October 2026, which is outside the monthly set; `train_product_model.py`
   uses only its category names, which is safe.
5. **Survivorship in lists.** A product is visible only in months it made a list. "Not in the top 500 next month"
   cannot be told apart from "not observed"; deep risers (201–1,000) exist only for September, so riser features at
   scoring time cover five times the depth seen in training.

---

## 9. Recommended exclusions and flags for training

| What | Action | Reason (evidence) |
|---|---|---|
| **Oct 2025, all lists** | exclude as training rows and as a feature source | partial month (~1 week): 0.24 same-product ratio, 0.29 of 2026 revenue, growth all = 100 (5.1) |
| **Oct 2025 risers** | exclude entirely | list sorted by a constant: order arbitrary (5.1) |
| **Nov 2025 "previous month" features and growth** | set to missing / flag `growth_vs_partial_prior` | prior month partial; median growth +62% (5.1) |
| **Virtual Products** | drop | no data in any month (3.3) |
| **Pre-Owned, Muslim Fashion** | flag `thin_category`; exclude from pooled top-500 labels or use per-category thresholds | top-500 cut-off $1,360 / $359; riser and video lists run out (4.2) |
| **AI flag Oct 2025–May 2026** | treat as NULL, not 0 | 0 in 100% of rows (6.3) |
| **Commission rate, SKU count, review count** | drop from historical features or accept and document the leak | current values repeated for all months (8.2) |
| **`revenue_growth_rate` = 100** | treat as missing ("no prior period") | placeholder (6.2) |
| **`revenue_growth_rate` generally** | prefer our own month-on-month change where both months exist; keep Kalodata's only as a separately named feature until defined | does not reproduce (6.2) |
| **Video `revenue_growth_rate`** | do not use | 97% below −100% (6.2) |
| **Deep risers (Sep p3–p10)** | keep separate from risers 1–200 (own list type) | different depth only in Sep (3.2) |
| **Non-core product pulls** | exclude (pilot duplicates, keyword, price-band, `last30Day`) | double counting and non-monthly windows (3.4) |
| **Cross-category product-months (159)** | sum revenue/units across categories for product-level features | each category row holds a share (5.2) |
| **Truncated full video lists (40 products)** | flag; don't treat as "all videos" | hit the 5-page cap (5.3) |

---

## 10. Proposed per-record quality flags (design only — nothing written to the DB)

Proposed as columns of a derived view or table (e.g. `v_product_month_quality`), one row per product × month ×
category × list, rebuilt from `pulls` + `products`:

| Flag | Values | Rule |
|---|---|---|
| `list_type` | `top500`, `riser200`, `deep_riser`, `other` | from pull name phase + page (fixes the naming collision) |
| `rank` | 1–1,000 | `(page−1)×100 + position` |
| `q_complete` | 0/1 | all expected pages for that category-month-list succeeded and were full |
| `q_partial_period` | 0/1 | month = 2025-10 (extend if new partial months appear: same-product ratio vs next month < 0.5) |
| `q_prior_partial` | 0/1 | month = 2025-11 |
| `q_thin_category` | 0/1 | rank-500 revenue in that category-month < $2,000, or list contains placeholder/zero tails |
| `q_growth_placeholder` | 0/1 | `revenue_growth_rate` = 100 |
| `q_growth_unverified` | 0/1 | always 1 until Kalodata's definition is confirmed |
| `q_multi_category` | count | number of categories the product appears in that month (> 1 = partial revenue per row) |
| `q_relist_risk` | cluster size | same seller + normalised title IDs in the same month (or across months) |
| `q_duplicate_pull` | 0/1 | the same query key exists in another pull |
| `q_snapshot_fields` | constant text | names fields that are collection-date values (name, seller, launch, SKU, commission, review count) |
| `collected_at` | UTC timestamp | raw mtime today; a stored timestamp once the downloader records one |
| `freshness_days` | integer | `collected_at` − end of event month (24–358 in this set) |
| `vintage` | `retrospective` / `live` | retrospective when collected > 35 days after month end |
| `q_consistency` | 0/1 | revenue ≈ units × price within 1% and channel sum within 1% (all pass today; guards future pulls) |

For videos: `q_ai_flag_valid` (month ≥ 2026-06), `q_dup_in_list` (video ID repeated in the same list),
`q_zero_tail` (revenue = 0 in a revenue-sorted list), `q_ad_share_capped` (ad-revenue ratio = 80),
`q_roas_capped` (ROAS = 20), `q_truncated_list` (full-product list hit the page cap).

A record is "training-grade" when `q_complete = 1`, `q_partial_period = 0`, `q_thin_category = 0`, and its features
avoid the snapshot fields; everything else is kept but flagged.

---

## 11. Prioritised fixes

| # | Fix | Evidence | Effort |
|---|---|---|---|
| 1 | Drop Oct 2025 rows and Oct-based "previous month" features; re-run model validation without them | 5.1 | S |
| 2 | Remove commission rate, SKU count (and review count) from historical features, or retrain both ways and report the difference | 8.2 | S |
| 3 | Treat growth = 100 as missing; add own month-on-month growth feature; stop relying on Kalodata's growth until defined | 6.2 | S |
| 4 | Sum product revenue/units across categories before product-level features | 5.2 | S |
| 5 | Give deep risers their own list type; never mix with risers 1–200 | 3.2 | S |
| 6 | Set AI flag to NULL before Jun 2026 in every analysis | 6.3 | S |
| 7 | Build a canonical read-only view (`core` monthly pulls only, rank, list type, month, category, flags from section 10) and point scripts at it | 2.2, 3.4 | M |
| 8 | Fix the loader to reload a raw file when its contents change (hash or mtime check); recovers 6 comment insights | 5.6 | S |
| 9 | Downloader: write `collected_at` (UTC) and credit cost into each raw envelope and into `pulls`; store real date in `pulled_on` | 3.5, 8.1 | S |
| 10 | Exclude or separately threshold Pre-Owned and Muslim Fashion; drop Virtual Products | 4.2 | S |
| 11 | Deduplicate videos within lists; flag the 40 truncated full lists | 5.3 | S |
| 12 | Cluster near-duplicate listings (seller + normalised title) and link relisted IDs before computing "new product" features | 5.4 | M |
| 13 | Start a vintage log: each month, re-pull last month's top-500 page 1 for a few categories and compare with the first pull, to measure Kalodata revisions (needs credits — owner approval) | 5.5 | M |
| 14 | Ask Kalodata (or test with a few paid calls, owner approval) how `revenue_growth_rate` is computed for products and videos | 6.2 | M |
| 15 | Add an index on `pulls(name)` (when the DB is next rebuilt; after a backup) | 2.3 | S |

---

## Appendix: how the checks were run

All queries ran read-only (`sqlite3.connect('file:…kalodata.db?mode=ro', uri=True)`) from scratch scripts in
`tmp_market_audit/data/` (deleted after the audit). Main steps: schema dump from `sqlite_master`; row counts per
table; pull inventory grouped by folder/endpoint/phase/month with file mtimes; pull names parsed into
phase/month/category/page; product rows joined to parsed pulls (257,600 core rows) for duplicate, overlap,
consistency, growth, null and extremes checks; video rows likewise (132,961); detail rows matched to rank rows on
month + category + product; pilot pulls matched to core pulls for revision checks; raw files re-read to compare
`success` and record counts with `pulls` (5,153 files; 6 mismatches, 0 record-count mismatches).
