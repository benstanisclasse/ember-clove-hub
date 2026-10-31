# Existing data vs available API capability: gap analysis (2026-10-31)

Sources:
- `existing_kalodata_db_fields.csv`: every stored column and every raw_json path, with completeness.
- `kalodata_fields.csv`: every spec field, marked whether it was observed in our responses and whether it is stored.
- `_work/kalodata_db_inventory.json`
- `_work/cj_mcp_notes.md`
- `data/kalo_cj/*.jsonl` and `data/cj_compare/*.jsonl`

## 1. Kalodata: what we hold

`research/kalodata/kalodata.db` (415 MB, read-only inspection) holds 5,165 pulls loaded from raw files, collected
2026-10-25 to 2026-10-30.

| Table | Rows | Distinct | From | Coverage |
|---|---|---|---|---|
| products | 259,418 | 136,291 products, 42,800 shops | `product/rank` | 12 months (2025-10 → 2026-09) × 31 categories. Top sellers 5 pages (500) per category-month, risers 2 pages, risers to 1,000 for 2026-09. |
| videos | 135,953 | 98,772 videos, 34,773 creators | `video/rank` | Top videos 3 pages per category-month (12 months), plus 1-5 pages for each of 125 products (2026-09) |
| product_details | 1,039 | 1,023 products | `product/detail` | ~84 products × 12 months, plus 35 last30Day lookups. **Never with `need_extra` or `need_image`.** |
| categories | 807 | 261 (29 L1, 232 L2) | `category/rank` | last30/90/365Day snapshots of 2026-10-25/26. No level 3. |
| comment_insights | 24 | 24 products | `product/comment/insight` | One snapshot. `cached_at` back to 2025-08. |
| video_features / video_elements / video_audio | 185 / 184 / 185 | — | **Hub-derived** | whisper transcripts, cut counts, vision-LLM tags, audio classifier. Not Kalodata data. |
| research_runs | 8 | — | Hub model registry | — |

Latest data month: **2026-09**. Latest call: 2026-10-30. Nothing for October 2026 yet.

### Fields we receive but don't break out
These are in `raw_json` only, with no column. They need a column or a child table to be usable.
- `product/detail.product_description[]`: the full rich-text description (text blocks and image URIs), in 100% of detail rows.
  This is the best text for matching against CJ.
- `video/rank.creator_debut`: the creator's first-seen date, in 100% of rows. It identifies new creators.
- `comment/insight.original_comments[]`: **raw reviews** (review id, rating, text, SKU spec, date, verified-purchase flag,
  review images). They are stored as JSON blobs, not as rows.
- `comment/insight.cached_at`: insight freshness. Several insights are over a year old.
- `pain_points[].key_review_id` / `id_list`: links each AI point to the review that supports it.
- `product_detail.product_region`.

### Fields the API documents but our responses never contain
- `product/rank.pri_category / sec_category / ter_category` (category id and name per product). Missing from all 2,617 rank
  responses, even with `need_extra`. Possibly needs `need_category` or a newer API version. We derive category from the request filter instead.
- `product/detail.revenue_trend` and `master_image_url`: always null, because we never sent `need_extra` / `need_image`.
  This is the **cheapest gap to close**: same 0.1 per call, which needs one test call to verify.
- `credit/balance.subRemain`: not returned. Not important.

### Endpoints never used (documented, not access-tested)
| Endpoint | What it would add | Cost |
|---|---|---|
| `shop/rank`, `shop/detail` | Shop GMV, growth, channel split (affiliate / self / mall), product count, top-3 products, BRAND vs RETAILER | 0.1 / page, 0.1 / shop |
| `creator/rank`, `creator/detail` | Creator GMV, followers, new followers, GPM, video/live counts, top products, creator type, engagement tier | 0.1 / page, 0.1 / creator |
| `livestream/rank`, `livestream/detail` | Live GMV, viewers, duration, top-3 products | 0.1 / page, 0.1 / live |
| `category/detail` | Shop count, active product count, channel split, revenue trend | 0.1 / category |
| `product/comments` | Raw reviews page by page (rating, text, SKU, date) | **0.01 / page** |
| `product/analysis` | Structured attributes (key/value) and selling-point highlights | 0.1 |
| `product/images` | Product image URLs (expire) | 0.01 |
| `creator/avatar-images` | Avatar URLs | 0.1 |
| `credit/logs` | Per-charge spend history (now used once, free) | free |

### Filters we have never used (on endpoints we do use)
- `product/rank`:
  - `shop_id`, `creator_id`, `video_id`, `livestream_id` (relationships)
  - `launch_date` (`<3`, `<7`, `>30`)
  - `delivery_type` (used once)
  - `is_affiliate`, `commission_rate`, `is_tts_product`, `revenue_range`
  - `need_all` (include zero-sale products)
  - `need_image`
  - sort by `launch_date`, `video_revenue`, `live_revenue`, `commission_rate`
- `video/rank`:
  - `shop_id`, `creator_id`, `ads_roas`, `followers_range`, `views_range`
  - `publish_date_range` (`<3`, `<7`, `<30`)
  - `is_ai_video` (used once)
  - sort by `views`, `ads_roas`
- Date windows:
  - Custom windows `yyyy-MM-dd~yyyy-MM-dd` (≤ 30 days on rank endpoints), e.g. weekly windows, are unused.
  - `lastDay` / `last7Day` are unused. We only use months and last30Day.

### Historical gaps
- **Depth:** ~12 months. Requests for 2024-10 and 2025-04 returned "product not found". Older history isn't available, and
  the docs don't say how far back data goes.
- **Category history:** category endpoints refuse months, so month-by-month category trends can only be built by
  snapshotting on a schedule. We have one snapshot.
- **Shop / creator / live history:** none stored.
- **Daily series:** none (`revenue_trend` null). Our time resolution is monthly.
- **Video lifetime:** only per-month views/revenue. No per-video daily curve.

### Data that requires our own processing (not provided by Kalodata)
- Transcripts, spoken hooks, cut rate, music/speech: the video file via `video/url` (0.5) → whisper / OpenCV / audio
  model (done for 185 videos).
- Scene and element tags: vision LLM (done for 184).
- Hashtags: inside `video_title` text only. No structured hashtag or music fields are documented.
- Captions/subtitles: not provided.
- Video duration: `video/detail.duration` (API), or from the file.
- Sales velocity, product age, concentration indices, growth acceleration: computed from stored periods.

## 2. CJ: what we hold

| File | Records | Fields kept |
|---|---|---|
| `data/kalo_cj/cj_batch_*.jsonl` + `cj_fixes.jsonl` | 53 | match level and note, pid, name, SPU code (`cj_sku`), URL, ship-from, dearest variant cost, weight, sizes_ok, listed count, total and US stock, review count and rating, cheapest and ≤15-day freight (name, price, days) |
| `data/cj_compare/batch_*.jsonl` | 92 | same idea, for our own 92 products (no stock or reviews) |
| `picking_sheet_2026-10-29.csv/.xlsx`, `cj_vs_eprolo_2026-10-29.csv` | derived | landed cost, kept per order, price for $10 |

- **No raw CJ responses were saved.** Agents read the MCP output and wrote 18-25 summary fields per product.
- The API returns far more:
  - every variant (id, SKU, attributes, dimensions, weight, image, barcode, price)
  - per-country, per-sub-warehouse stock split into CJ-owned vs factory
  - customs code and name, material, packing, logistics properties
  - description HTML and image lists
  - all 29 freight options with markup, clearance fee and per-carrier address rules
- **Variant level is lost.** Only the dearest variant's cost and the heaviest weight survive, so per-variant margin can't be recomputed.
- **Freshness:** every CJ value dates from 2026-10-29. CJ has no history endpoints, so price and stock history begins only
  when we start snapshotting.
- **Linkable to Kalodata:** all 50 `kalo_cj` records carry the Kalodata product id via `winners_2026-09.csv` (`k` →
  `kalo_id`). The 92 `cj_compare` records link to our Shopify products instead (`n`, handle).
- **Reviews:** `review_count` is 0 for every record checked, and the product tested on 2026-10-31 had 0 reviews. CJ review
  coverage looks sparse, so it is not a reliable quality signal.

## 3. CJ: what the API offers that we don't capture

Access path today: **CJ MCP connector only.** Its token is embedded in the connector URL and stops working silently when
it expires. The Hub has no CJ REST API key. On 2026-10-31, 17 REST endpoints were confirmed reachable through MCP tools
(mapping inferred from tool names; see `cj_endpoints.json` → `mcp_tools[].rest_endpoint_inferred`).

| Capability | Endpoint | Status | We capture? | Gap |
|---|---|---|---|---|
| Keyword search with filters (category, price, warehouse country, has-video, verified warehouse, listed count…) | `GET /product/listV2` (50 pts) | confirmed | partly (top match only) | Store all candidates, not one: needed for `match_candidate` |
| Product detail (customs code and name, material, packing, logistics props, description HTML, images, `deliveryCycle`) | `GET /product/query` (10) | confirmed | ~6 fields | Customs code/name and `productProEnSet` (needed for accurate freight), material, image list |
| Ratings summary (`score`, `logisticScore`, `serviceScore`, `commentCount`) | `POST /product/productDetail/query` (0) | not tested | no | Cheap quality signal, if populated |
| Variants (vid, SKU, attributes, dimensions, weights, image, price) | `GET /product/variant/query` (10) | confirmed | dearest variant cost + heaviest weight | **Per-variant rows** |
| Inventory by country and sub-warehouse, CJ-owned vs factory | `GET /product/stock/getInventoryByPid` (10) | confirmed | total + US total | Split CJ vs factory (factory stock is unverified) and per warehouse |
| Reviews (text, images, score, country, date) | `GET /product/productComments` (0) | confirmed (empty for test product) | count + avg only | Raw reviews. Sparse on CJ, so treat absence as unknown, not bad |
| Product videos (URL, cover, duration, **copyright price**) | `POST /product/queryVideosByProductId` (0) | not tested | no | Supplier video for ads, but check `isFree`/copyright before any use |
| Image search | `POST /product/queryProductsByImage` (1,000) | **needs account Level 3+** | no | Would make Kalodata→CJ matching much better; check our level |
| Freight: all methods, days, carrier, markup, clearance, tax/tariff fields, address rules | `POST /logistic/freightCalculate`, `freightCalculateTip` (10) | confirmed | cheapest + ≤15-day option | All options and per-variant/qty quotes; markup and clearance |
| Methods available per SKU / countries per method | `POST /logistic/getAvailableLogistics`, `getReachableCountry` (10) | not tested | no | Low priority |
| Price change history | none: current price only | — | no | **Must snapshot ourselves** |
| Webhooks: product, stock, order, logistics… | `POST /webhook/set`, `/webhook/product/subscribe` | not enabled (all CANCEL) | no | Push updates. Needs a public HTTPS receiver and owner approval. No retries; price-only changes not pushed |
| Own-account analytics (SQL over orders, inventory, disputes) | `POST /aiData/nlSql` (10) | not tested | no | Useful once we have orders |
| API call log | `POST /apiCallLog/queryPage` (20) | not tested | no | Points/usage audit |
| Listing platform lookups (categories, brands) | `/listed/*` | **failed: the Shopify-type shop needs reauthorizing in CJ** | no | Store setting: owner decision |

**Risks found:**
- CJ docs say **30 days with no CJ transactions suspends API access** (`1600014`). We have no CJ orders.
- The REST rate tiers (1-6 req/s by level) differ from what `get_account_settings` returned (`qpsLimit` 100), so the real limit is unknown.
- Logistics calls hit a 1/s limit in practice.
