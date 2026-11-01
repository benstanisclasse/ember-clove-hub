# Data acquisition (Tier 1 + Tier 2), approved 2026-10-31

Owner approval, quoted: **"do both tiers"**. This covers Tier 1 (access tests, then the Oct, Nov and Dec 2026 monthly pulls
for the forward test) and Tier 2 (niche gap-filling). The plan as approved:

| Tier | Item | Planned credits |
|---|---|---|
| 1 | Access tests: detail `need_extra`/`need_image`, rank `need_image`, shop/creator rank, comments, analysis | ~0.4 |
| 1 | Oct 2026 core monthly pull, then Nov and Dec (sealed, forward test) | ~29 per month |
| 2 | Niche ranks 501-1,000 × 12 months | 24 |
| 2 | Monthly shop + creator ranks, niche, 12 months | 9.6 |
| 2 | Raw reviews, 500 products × ≤ 2 pages | 10 |
| 2 | Product attributes, 200 products | 20 |
| 2 | Product images, 300 products | 3 |
| 2 | Product → videos (top 100), 100 products, Sep 2026 | 10 |

Niche = Womenswear & Underwear (601152), Shoes (601352), Fashion Accessories (605248), Jewelry Accessories & Derivatives (953224).
Script: `scripts/kalodata_gaps.py` (resumable; saved responses are reused; hard credit cap per run).

## Access tests (2026-10-31): all passed

| Test | Result |
|---|---|
| `product/detail` + `need_extra`, `need_image=1` | **`revenue_trend` returns a daily series** (30 values for 2026-09). `master_image_url` filled. Cost unchanged (0.1) |
| `product/rank` + `need_image=1` | `master_image_url` **and** `pri/sec/ter_category` objects returned |
| `shop/rank` (monthly `date_range`) | works: shop GMV, type, affiliate/self/mall split, on-sale product count |
| `creator/rank` | works once `category_id_list` is sent as a **string** (an array gives a JSON parse error) |
| `product/comments` | works: review_id, rating, text, timestamp, SKU, source, country; **no reviewer identity fields** |
| `product/analysis` | works: attributes and highlights |

Code fixed along the way:
- `kalodata_core.get` compared the API's error `code` (a string, `"501"`) with the number 501, so invalid-parameter and
  "not found" errors were retried up to 5 times. Each retry may be billed. It now stops on those errors.
- `kalodata_db` labels revenue-sorted pages beyond 5 as `top_deep`. Before, Womenswear 2026-09 ranks 1,001-1,100 from an
  old probe sat inside `top`. `market_data.py` already cut at page 5. `kalo_cj_pick.py` and Phase A did not, and Phase A
  has been re-run.
- `kalodata.call(..., ingest=False)` saves raw files without loading them into the database (for sealed pulls).

## Sample for reviews, images, attributes and videos (no outcome peeking)

Seed 20261031. From each niche category's **2026-09 top-500** (information available at the end of September):
- 50 products at random from ranks 1-100 and 75 from ranks 101-500, giving 500 products for reviews
- nested subsets: images 60%, attributes 40%, product-video pulls 20% (excluding products whose videos were already pulled)

The list is in `_work/tier2_sample.csv`.

**Leakage note:** reviews carry timestamps up to the pull date (2026-10-31). Any feature for month m uses only reviews dated
on or before the end of m.

## Forward pulls (sealed)

- `python -I scripts/kalodata_gaps.py forward --month 2026-10 --max-credits 30` refuses to run before 2026-11-02.
  It writes to `research/kalodata/sealed/2026-10/` (git-ignored, backed up by the research mirror) and **never loads
  into kalodata.db**.
- The sealed files are loaded only after the Phase C predictions on the 2026-09 universe are frozen and hashed
  (`registry/DEFINITIONS_v1.md` §7). Nov and Dec follow the same way.
- **Kalodata's month-end latency is unknown.** If 2026-10 looks incomplete on 11-02 (e.g. top-500 revenue far below
  other months), the pull should be redone a few days later.

## Not in the approved tiers (Tier 3, not pulled)

- Weekly windows
- Ranks 501-1,000 for all categories
- Multi-month product-video pulls
- **Daily trends for ~200 products:** now confirmed to work at 0.1 per product-month, so this is the cheapest way to get
  sub-monthly history

## Results (Tier 2 run, 2026-10-31 evening ET)

**Spend.** `credit/logs` shows 1,867 charges, 643 × 0.1 and 1,224 × 0.01, displayed total **76.54 credits**. The
balance fell from **470.9 to 405.29 (−65.61)**. The gap suggests review and image calls really cost about 0.001 and
the log rounds them up to 0.01. Summary: `_work/kalodata_credit_logs_tier2_2026-10-31.json`.

| Pull | Files | Outcome |
|---|---|---|
| Niche ranks 501-1,000, 12 months | 240 | All succeeded: 24,000 rows (`top_deep`) |
| Monthly shop and creator ranks | 96 | **All failed and were billed (9.6 credits).** `need_category` was sent as `true`, but the API wants an integer. Fixed (`need_category=1`); **not re-pulled yet**: re-pulling costs ~9.6 credits more than the approved ~77, so it awaits the owner's OK. Failed responses are kept in `raw/gaps_tier2_failed/` |
| Raw reviews | 921 pages, 499 products | 83,156 reviews. 12 products have none, and **357 hit the 200-review cap** |
| Product attributes | 200 | 196 with data (median 13 attributes, plus highlights). **4 "file not found" calls were billed anyway** |
| Product images | 299 | All succeeded (median 9 images per product). The URLs expire, so store hashes, not files |
| Product → videos (Sep 2026) | 99 | 93 with videos (8,603 rows). **6 "video not found" calls were billed** |

**Billing facts learned (they contradict or go beyond the docs):**
- Failed calls are billed, including parameter errors.
- "No data" results are billed, including `product/analysis`, which the pricing page says charges only when data exists.
- Plan every pull with a small test page first.

**Reviews:**
- Timestamps are **Unix seconds**, not milliseconds.
- Pages come back **newest first**, so for busy products the 200-review cap covers only recent months: p10/p50/p90 dates
  are 2026-07-21 / 2026-09-18 / 2026-10-16, and the overall range is 2024-12-07..2026-10-30.
- 30% are dated after 2026-09-30 and must be excluded from any feature for month ≤ 2026-09.
- Ratings: 5★ 80%, 4★ 8%, 3★ 4%, 2★ 2%, 1★ 6%.
