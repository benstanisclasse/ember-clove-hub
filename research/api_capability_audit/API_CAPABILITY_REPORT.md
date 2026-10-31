# Kalodata + CJ Dropshipping: API capability discovery and data intelligence audit

Date: 2026-10-31. Scope: read-only discovery, documentation and architecture. No product recommendations.

## What was spent and what was changed

- **Kalodata:** 0 credits. Two free account calls only: `credit/balance` and `credit/logs`.
- **CJ:** 25 read-only MCP calls, 0 money. No orders, payments, listings, webhooks, connections or settings were touched.
- **Databases:** none modified. `kalodata.db` was opened read-only.

## Files in this folder

| File | What |
|---|---|
| `API_CAPABILITY_REPORT.md` | This report |
| `kalodata_endpoints.json` / `cj_endpoints.json` | Machine-readable catalogues: every endpoint, parameter, nested response field, cost, rate limit, safety class, access status and evidence |
| `kalodata_fields.csv` (635 rows) / `cj_fields.csv` (3,973 rows) | One row per request parameter and response field (dotted paths for nested objects). Kalodata rows also say whether each field was **observed in our own responses** and **where we store it** |
| `api_costs.csv` | Per-endpoint cost, unit, rate limit, pagination, billing conditions, confidence |
| `capability_matrix.md` / `.csv` | The Phase 24 matrix: 206 rows, one per endpoint |
| `existing_kalodata_db_fields.csv` | Field-level dictionary of `kalodata.db`: meaning, source endpoint, API vs derived, completeness, last observation, relationships |
| `existing_data_gap_analysis.md` | What we hold vs what the APIs offer |
| `integration_architecture.md` | Proposed unified database (DDL sketch), matching process, landed-cost rules |
| `automation_opportunities.md` | Costed automations for approval |
| `implementation_roadmap.md` | Priorities and the owner decisions needed |
| `sources/` | Kalodata's official OpenAPI spec and pricing JSON as retrieved |
| `_work/` | Agent working notes, MCP tool catalogue and response samples, DB inventory, credit-log summary |
| `build_catalog.py`, `build_existing_inventory.py` | Regenerate the JSON/CSV outputs from `_work/` (no API calls) |

Verification vocabulary:
- **confirmed_available**: a call with our credentials succeeded.
- **documented_not_access_tested**: in the official docs, never called.
- **requires_additional_permissions**, **requires_account_upgrade**, **deprecated**, **unavailable**, **unknown**: as named.
- Field rows say **documented / undocumented / in spec without description**, and for Kalodata, **observed yes/no / never called**.

---

## Stage A: current integrations

| | Kalodata | CJ Dropshipping |
|---|---|---|
| Access method | **Official REST API, called directly** by our own client `scripts/kalodata.py`. No MCP: Kalodata's MCP is "coming soon". A third-party GitHub skill (`sailtonight/kalodata-skill`) bundles a local one, but we don't use it. | **CJ MCP connector** in Claude (70 tools). It runs in "URL direct token" mode, which matches CJ's documented remote MCP. Agents used it for the 2026-10-29 match batches. No direct REST client and no CJ key in the Hub. |
| Credential | `KALODATA_API_KEY` user env var via `hub_env` (works: balance 470.9 credits on 2026-10-31). The header `secret-key` works; the spec says `X-API-Key`. | A token embedded in the MCP connector URL. CJ access and refresh tokens last 180 days, and **the connector stops when it expires**. GENERAL (non-sandbox) account. |
| Permissions seen | 9 endpoints used successfully. The other 11 documented endpoints are untested; docs hint at per-API enablement. | 20 read tools worked. The Shopify-type shop is **status 4 "please reauthorize"**, so listing lookups fail. Image search needs Level 3+. |
| Request history | 5,317 charged calls on 2026-10-25..30 (Kalodata's own log); 5,165 raw responses loaded in `kalodata.db` | No raw responses kept; 145 summarised match records in `data/kalo_cj/`, `data/cj_compare/` |
| Rate-limit handling | `time.sleep(1.1)` after every call (fits rank 10/10 s). No retry. Per-run credit cap (`Budget`) | MCP limiter 10 reads/s; upstream logistics 1/s (hit during the audit) |
| Caching | Raw files are the record. Manual "check raw/ and the DB first" rule. Kalodata re-serves an unchanged comment insight free | None |
| Kalodata ↔ CJ ↔ Shopify | `scripts/kalo_cj_pick.py` joins Kalodata winners to agent-found CJ matches → picking sheet. `scripts/cj_compare.py` compares CJ with EPROLO for our 92 Shopify products. CJ has a Shopify-type shop connected but unauthorized, 0 product connections, 10 "My Products". | |

---

## Question 1: what can the Kalodata API provide?

The official spec (`sources/kalodata_openapi_2026-10-31.json`) documents **20 endpoints**: 18 data endpoints plus 2
account endpoints, with **177 request parameters** and **383 response fields**. Every endpoint is POST JSON except
`credit/balance` (GET).

| Area | Endpoints | Data (directly from the API) |
|---|---|---|
| **Products** | `product/rank`, `product/detail`, `product/images`, `product/analysis` | id, name, shop, L1-3 category, min/max/avg price, **estimated GMV and units**, growth %, revenue by channel (video / live / showcase-mall), commission %, launch date, SKU count, creator/video/live counts, review count, delivery type (local/cross-border), rich description, images (signed URLs), daily `revenue_trend` (with `need_extra`, unverified), structured **attributes** (key/value) and selling-point **highlights** |
| **Videos** | `video/rank`, `video/detail`, `video/url` | id, caption, creator, publish time, views, likes, shares, comments, **video GMV and units**, growth, **ad flag, ad ROAS, ad share of GMV and views, ad views, ad CPA, ad period**, **AI-generated flag**, GPM, duration, product count, creator debut date, **playable MP4 URL** (5-min expiry, 0.5 credit) |
| **Creators** | `creator/rank`, `creator/detail`, `creator/avatar-images` | id, handle, nickname, region, status, type (seller-owned vs independent), followers, new followers, GMV, units, video/live GMV, views, GPM, counts of videos, lives, shops and products, top-3 products, categories, engagement tier. **Contact fields** (email, WhatsApp, Instagram, etc.) |
| **Shops** | `shop/rank`, `shop/detail` | id, name, type (BRAND/RETAILER), GMV, units, growth, ASP, on-sale product count, **GMV split affiliate / self-promotion / mall**, creator/video/live/product counts, top-3 products, categories, trend |
| **Livestreams** | `livestream/rank`, `livestream/detail` | id, title, creator, start/end/duration, GMV, ASP, views, viewers, GPM, product count, top-3 products |
| **Categories** | `category/rank`, `category/detail` | id, name, level, GMV, units, growth, **top-3-shop share (concentration)**, average revenue, shop count, active product count, GMV by channel, trend |
| **Reviews** | `product/comments`, `product/comment/insight` | Raw reviews (rating, text, SKU, date, source, country) at 0.01/page. **AI** summary, pain points, positives and usage scenarios, each linked to key review ids, plus the raw reviews behind them (undocumented but returned). `cached_at` gives freshness |
| **Account** | `credit/balance`, `credit/logs` | remaining credits; every charge with timestamp, type and amount (free) |

### Search and filter capabilities

- **Rank endpoints:** `keyword`, `category_ids`, `revenue_range`, `sort_field` (per-endpoint allowed fields), page size up to 100, page number. Rank responses carry no total count.
- **Product rank also filters by:**
  - `shop_id`, `creator_id`, `video_id`, `livestream_id` (all relationships)
  - `unit_price_range`, `commission_rate`, `is_affiliate`, `is_tts_product`
  - `delivery_type`
  - `launch_date` (`<3`, `<7`, `>30` days)
  - `need_all` (include zero-sale products)
- **Video rank also filters by:** `product_id`, `shop_id`, `creator_id`, `ads_roas`, `followers_range`, `views_range`, `publish_date_range`, `is_ai_video`.
- **Creator rank also filters by:** `creator_type`, `followers_range`, `engagement_rate` (LOW/MEDIUM/HIGH), `shop_id`, `product_id`.
- **Shop rank also filters by:** `shop_type`, `unit_price_range`.
- **Regions:** 24 in the enum; 15 marketed; comments support only 7 (incl. US).
- **Currencies:** 16. **Languages:** 18.

### History

- Rank endpoints take a ≤30-day window: `lastDay`, `last7Day`, `last30Day`, a custom `yyyy-MM-dd~yyyy-MM-dd`, or a month `yyyy-MM`.
- **About 12 months back** (tested: 2024-10 and 2025-04 returned "product not found").
- Category endpoints accept **only rolling windows** (last7/30/90/180/365Day). Month requests are rejected with 501.
- There is no dedicated history or time-series endpoint. Trends exist only as `revenue_trend` inside detail responses.

### Not provided by Kalodata

- Transcripts, captions or subtitles
- Structured hashtags or music
- Sentiment scores
- Paid-vs-organic **revenue** in currency (only ratios)
- Data timezone and freshness (undocumented)

We derive transcripts, cuts and tags ourselves (`video_features`, `video_elements`, `video_audio`, 185 videos).

## Question 2: what can the CJ Dropshipping API provide?

The official API 2.0 docs (36 pages, all loaded) document **185 endpoint rows in 12 modules**:

| Module | Rows |
|---|---|
| Authentication | 4 |
| Setting | 4 |
| Product | 23 |
| Storage / private inventory | 7 |
| Shopping | 62 |
| Logistic | 8 |
| Dispute | 9 |
| Webhook | 4 |
| Shop | 13 |
| Ticket | 13 |
| Listing | 34 |
| AI Data | 4 |

They define **1,114 request parameters** and **2,872 response fields**. Safety classes:

| Class | Rows |
|---|---|
| read-only | 124 |
| account-modifying | 39 |
| creates orders | 12 |
| auth | 4 |
| financial | 3 |
| publishes listings | 3 |

`createOrderV2`/`V3` with `payType=2` also **pays from balance**, so treat them as financial.

- **Catalogue:**
  - Keyword/category search with many filters (`/product/listV2`), product detail (customs code and name, material, packing, logistics properties, description, images, delivery cycle), all variants (vid, SKU, attributes, dimensions, weight, image, price), size charts, packaging.
  - **Image search:** Level 3+ accounts only; 1,000 points per call.
  - **Videos** (URL, cover, duration, **copyright price**).
  - **Reviews** (text, images, score, country, date) and rating summaries.
  - **No price history:** current prices only.
- **Inventory:** per country and per sub-warehouse, split into **CJ-owned vs factory** stock. Also verified-warehouse flag, private inventory, and a global warehouse list (20 countries incl. US).
- **Logistics:**
  - Freight for every method: carrier, total USD (+ CNY), delivery days as a "min-max" string, clearance fee, tax/tariff fields, CJ markup (in the "tip" variant), and per-carrier address rules.
  - Available methods per SKU, reachable countries, tracking.
  - Quotes are **DDU** (buyer pays duties), and the docs contradict each other on whether duty is included.
- **Account side:** orders, order logs, proof of delivery, COGS, balance and wallet history, merge orders, disputes, tickets, shop products and product connections, listing to Shopify/eBay/WooCommerce etc., webhooks (8 topics, HMAC-signed, no retries), sandbox, and a read-only **SQL endpoint over your own CJ data**.
- **Deprecated:** `GET /product/list` → `listV2`; `POST /product/sourcing/query` → `GET /product/sourcing/queryList`; `/logistic/getTrackInfo` → `/logistic/trackInfo`; plus several deprecated fields.

## Question 3: what is available with our current integrations and credentials?

- **Kalodata: 9 endpoints confirmed.**
  - `product/rank`, `product/detail`, `video/rank`, `video/detail`, `video/url`, `category/rank`, `product/comment/insight`, `credit/balance`, `credit/logs`.
  - `tiktok/video/download` (called once by our pilot) is **not in the docs** and returned 404: unavailable.
- **CJ: 17 REST endpoints confirmed** through the MCP:
  - settings, category tree, global warehouses
  - product list V2, product detail, my products, variants, inventory by pid, reviews
  - private-inventory SPU page and SKU-by-SKU
  - order list, freight calculate, freight calculate tip, dispute list, shop list, product connection list
  - Also MCP-only tools: login status, rate-limit status, pay-order list.
  - 2 listing lookups fail (shop needs reauthorizing).
  - 1 unknown: warehouse detail failed on a factory sub-warehouse id.

## Question 4: documented capabilities our tools don't expose

- **Kalodata:** 11 documented endpoints never used: `shop/rank`, `shop/detail`, `creator/rank`, `creator/detail`, `creator/avatar-images`, `livestream/rank`, `livestream/detail`, `category/detail`, `product/comments`, `product/analysis`, `product/images`.
  - **Our client can reach all of them** (it's a generic REST caller), but it has no commands for them.
  - Unused options on endpoints we do use: `need_extra` on detail, `need_image`, relationship filters on rank (`video_id`, `creator_id`, `shop_id`, `livestream_id`), `launch_date`, custom date windows.
- **CJ:** the MCP has no tool for these documented endpoints:
  - `queryProductsByImage`, `queryVideosByProductId`, `productDetail/query` (ratings summary)
  - `stock/queryBySku`, `variant/queryByVid`, `sizeChart/query`
  - `getAvailableLogistics`, `getReachableCountry`, `getOrderTrackHistory`
  - `sourcing/queryList`, `apiCallLog/queryPage`, wallet billing and balance history, `webhook/product/subscribe` (+ list)
  - all of AI Data (`nlSql`), all of Ticket, COGS, `createOrderV3`
  - most private-inventory order and outbound calls
  - A direct CJ API key would expose all of them.

## Question 5: what data are we failing to collect?

Full detail: `existing_data_gap_analysis.md`. The material gaps:
1. **Fields we receive but bury in `raw_json`:** raw reviews inside comment insights; full product descriptions; `creator_debut`; insight `cached_at`.
2. **Fields left null by our requests:** `revenue_trend` (daily series) and `master_image_url` on product detail. We never sent `need_extra`/`need_image`.
3. **No shop, creator, livestream or category-detail data at all**, and only one category snapshot. Category history can only be built by snapshotting, because months are refused.
4. **No time resolution below a month**, and no October 2026 data yet. Latest month: 2026-09.
5. **CJ:**
   - no raw responses
   - no variant-level rows (only the dearest variant's cost and the heaviest weight)
   - no warehouse split or CJ-vs-factory stock
   - only 1-2 of ~29 freight options
   - no customs code or logistics properties
   - no price or stock history
   - no videos
   - no ratings summary

## Question 6: which additional data would most improve finding profitable products?

In order of value per cost:
1. **Per-variant CJ landed cost with snapshots.** Price + freight per variant, over time. Margin is decided at variant level, and history doesn't exist unless we record it. *Free (points).*
2. **Daily sales trend for watchlist products** (`need_extra`, if confirmed). It separates a spike from steady demand and shows acceleration. *0.1/product.*
3. **Raw reviews + AI insight per candidate** (`product/comments` 0.01/page, insight 1). Sizing, quality and "not like the photo" complaints are the main risk signals we already act on. *Cheap.*
4. **Category concentration and shop counts** (`category/detail`, `shop/rank`). Tells fragmented niches (enterable) from top-3-dominated ones. *~3 credits/month.*
5. **New-product radar** (`launch_date <7`). Earliest signal for fast-rising items. *~1.6 credits/month.*
6. **Product attributes + images for matching** (`product/analysis`, `product/images`), plus CJ image search if our account level allows. Better match quality means fewer wrong-supplier mistakes.
7. **Creator and video-by-product data** to judge how creator-dependent a product's sales are (`creator_number`, video concentration).

## Question 7: what would retrieving more Kalodata data cost?

Price list from the pricing page, checked against our own `credit/logs` (5,317 charges: 5,266 × 0.1, 27 × 0.5, 24 × 1.0 = **564.1 credits ≈ $56** spent on 2026-10-25..30):

| Endpoint | Credits | Rate limit (per 10 s) | Confidence |
|---|---|---|---|
| `product/rank`, `video/rank`, `shop/rank`, `creator/rank`, `livestream/rank`, `category/rank` | 0.1 per page (≤100 rows, rounded up; 10-row pages still 0.1) | 10 | verified (log) for product, video and category; documented for the rest |
| `product/detail`, `video/detail`, `shop/detail`, `creator/detail`, `livestream/detail`, `category/detail` | 0.1 | 100 (creator/detail 500) | verified for product and video detail |
| `product/analysis` | 0.1, only when data exists | 100 | documented |
| `creator/avatar-images` | 0.1 | 10 | documented |
| `video/url` | 0.5 | 10 | verified |
| `product/images`, `product/comments` | 0.01 | 10 | documented |
| `product/comment/insight` | 1.0 on first fetch or after refresh (~2-weekly); unchanged re-fetch and failures free | 100 | verified |
| `credit/balance`, `credit/logs` | free | 10 | verified |

- Failed rank and detail calls appear to be billed: there are ~150 more 0.1 charges than successful responses.
- Monthly rebate: 20% on spend between 3k and 30k credits, 50% above. Credit purchase prices are behind login.
- **Scenario costs** (`automation_opportunities.md`):
  - current core refresh: ~30/month
  - plus category, new-product, shop, creator, watchlist and review work: **~60-65/month (≈ $6-7)**
  - a one-off pass of all 11 unused endpoints on our niche: about 5-10 credits
  - 470.9 credits on hand.

## Question 8: restrictions and limitations to consider

- **Kalodata:**
  - Rate limits: rank 10 req/10 s; detail 100 (creator/detail 500).
  - Windows ≤30 days on ranks. Category endpoints accept rolling windows only. About 12 months of history.
  - Rank responses carry no totals.
  - Spec and server disagree on the auth header (`secret-key` works).
  - Undocumented: error codes, freshness, timezone.
  - Keyword search is loose (returns unrelated items).
  - Estimates, not audited sales.
  - Media URLs expire in 5 minutes, and Kalodata doesn't hold every video.
  - Comment insights can be over a year old (`cached_at` back to 2025-08).
  - `creator/detail` returns personal contact data: privacy rule needed.
  - Terms on storing data and training models have not been checked.
- **CJ:**
  - Rate limits: QPS 1-6 by account level in the docs, but our settings show `qpsLimit` 100. 10/s per IP, max 3 CJ users per IP, logistics 1/s in practice.
  - **Points quota:** 50,000/day free + 100 per $ of the top monthly spend. listV2 costs 50, image search 1,000, most lookups 10, listing calls 10 even when they fail.
  - **API suspended after 30 days with no CJ transactions.**
  - Tokens last 180 days, and the MCP URL token silently expires.
  - No price history.
  - Search stock and inventory stock disagree. Factory stock is unverified.
  - "Suggested sell price" is inconsistent between endpoints.
  - Freight is DDU, and the docs are contradictory on duty inclusion.
  - Reviews are sparse.
  - Image search needs Level 3+.
  - Webhooks have no retries and don't push price-only changes.
  - Docs examples are partly invalid JSON (~590 fields known only from examples).

## Question 9: how to structure a unified Kalodata + CJ database?

See `integration_architecture.md`:
- A new, **rebuildable** `research/intel/intel.db` loaded from raw files, so no migration of `kalodata.db`.
- Entity tables plus **append-only period/snapshot tables**: products, shops, creators, videos, lives and categories on the Kalodata side; CJ products, variants, prices, inventory and freight quotes on the other.
- Explicit **`match_candidate`** links (evidence, confidence, accept/reject reason) instead of a shared id.
- A `landed_cost` table that states what it excludes (duties under DDU, returns, ads).
- Research tables (scores, predictions, experiments).
- API operations: endpoint catalogue, call log with request hash and cost, credit ledger from `credit/logs`, refresh policy and a freshness view.
- Personal data (buyer identities, creator contacts, CJ addresses) stays out.

## Question 10: what to implement first?

See `implementation_roadmap.md`. In short:
1. **Free:** break out the fields already paid for (reviews, descriptions, creator debut, insight freshness); keep raw CJ responses; reconcile credits with `credit/logs`; one cost table in code.
2. **~0.5 credits, approval needed:** verify `need_extra`/`need_image` on detail, and test access to shop, creator and comments endpoints.
3. Build the rebuildable intel store, seed `match_candidate` from the 145 existing matches, and start free weekly CJ snapshots.
4. Then expand Kalodata collection within an approved monthly envelope.

### Owner decisions needed

- Credit envelope (30 → ~60/month?).
- The ~0.5-credit tests.
- Direct CJ API key vs MCP only.
- The CJ Shopify shop reauthorization.
- The CJ 30-day-inactivity suspension risk.
- Webhooks.
- Excluding creator contact data.

## Things that remain unverified

- Whether `need_extra` fills `revenue_trend`, and whether the 11 unused Kalodata endpoints are enabled for our key.
- Kalodata freshness, timezone, earliest date, and billing of zero-row or failed calls (the log suggests failed calls are billed).
- CJ duty treatment in the charged total, real QPS for our account, and our account level for image search.
- The MCP-to-REST mapping (inferred from tool names).
- Review item fields (our test product had none), and order, dispute and connection item fields (we have no such records).
- Correction to `_work/cj_mcp_notes.md`: it says we hold no sourcing ids. A sourcing request was in fact filed earlier on
  2026-10-31 (CJSPU960448013, id 2610311523094492602; see `log.md`). `query_sourcing` failed only because the audit call
  passed no id.
