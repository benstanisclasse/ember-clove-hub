# Kalodata Open API: documentation notes

Retrieved 2026-10-31. Read-only: no API endpoint was called, no key was read, nothing was signed in to or submitted.
Structured data for every endpoint is in `kalodata_endpoints_raw.json` (same folder): 20 endpoints, 177 request
params and 383 response fields, flattened to dotted paths.

## 1. How the docs are built and where the data came from

- `https://www.kalodata.com/open-center/docs` is a JavaScript single-page app. WebFetch got HTTP 403 (Cloudflare).
  In the built-in browser the page rendered, and its network log showed where the content comes from:
  - **`GET https://www.kalodata.com/api/open-center/api-docs/public`**: a complete **OpenAPI 3.0.1** document
    ("Kalodata OpenAPI" v1.0.0, 243,623 bytes, 20 paths, 235 component schemas). It downloads without login, and the
    docs UI renders every endpoint page from it. This is the primary source.
  - **`GET https://www.kalodata.com/api/open-center/api-pricing`**: JSON behind the Pricing page that maps each
    endpoint URI to its credit cost group.
- Other open-center pages read: `/open-center/home`, `/open-center/pricing`, `/open-center/skill` (two tabs). The site
  nav has only Home, API, Skill and Pricing. There is **no changelog, error-code page, rate-limit page or status page**.
- Deep links work: `https://www.kalodata.com/open-center/docs?endpoint=<URL-encoded path>`, for example
  `...docs?endpoint=%2Fopenapi%2Fv1%2Ftiktok%2Fcategory%2Frank`. Each JSON entry has its own `doc_url`.
- Each endpoint page shows: summary, description, method + full URL, a fixed "Integration Method" paragraph, "API
  Rate Limit: Max N Requests /10 Second" (from the spec's `x-permits`), request and response parameter tables
  (field, type, description, example, required), a fixed debug request and a mock response. Mock responses show
  `"success": false`; they are generated placeholders, not real data.
- Secondary source: the official Skill page links to `github.com/sailtonight/kalodata-skill` (MIT, Python CLI
  `kalo` + stdio MCP server). I read its README and parts of its client code only to cross-check the auth header and
  error handling. Anything taken from it is marked as secondary and is not API documentation.

## 2. Endpoint inventory (all documented, all under https://www.kalodata.com)

| Module | Method + path | Rate limit (req/10 s) | Credits |
|---|---|---|---|
| video | POST /openapi/v1/tiktok/video/rank | 10 | 0.1 x ceil(rows/100) |
| video | POST /openapi/v1/tiktok/video/detail | 100 | 0.1 |
| video | POST /openapi/v1/tiktok/video/url | 10 | 0.5 |
| product | POST /openapi/v1/tiktok/product/rank | 10 | 0.1 x ceil(rows/100) |
| product | POST /openapi/v1/tiktok/product/detail | 100 | 0.1 |
| product | POST /openapi/v1/tiktok/product/images | 10 | 0.01 |
| product | POST /openapi/v1/tiktok/product/analysis (selling points + attributes) | 100 | 0.1, only when data exists |
| review | POST /openapi/v1/tiktok/product/comments (raw reviews) | 10 | 0.01 |
| review | POST /openapi/v1/tiktok/product/comment/insight | 100 | 1, only on first fetch or after a data refresh |
| creator | POST /openapi/v1/tiktok/creator/rank | 10 | 0.1 x ceil(rows/100) |
| creator | POST /openapi/v1/tiktok/creator/detail | 500 | 0.1 |
| creator | POST /openapi/v1/tiktok/creator/avatar-images (up to 100 IDs) | 10 | 0.1 |
| shop | POST /openapi/v1/tiktok/shop/rank | 10 | 0.1 x ceil(rows/100) |
| shop | POST /openapi/v1/tiktok/shop/detail | 100 | 0.1 |
| livestream | POST /openapi/v1/tiktok/livestream/rank | 10 | 0.1 x ceil(rows/100) |
| livestream | POST /openapi/v1/tiktok/livestream/detail | 100 | 0.1 |
| category | POST /openapi/v1/tiktok/category/rank | 10 | 0.1 x ceil(rows/100) |
| category | POST /openapi/v1/tiktok/category/detail | 100 | 0.1 |
| account | GET /openapi/v1/credit/balance | 10 | free |
| account | POST /openapi/v1/credit/logs | 10 | free |

Counts: product 4, video 3, creator 3, review 2, shop 2, livestream 2, category 2, account 2 = **20**.
No endpoint is marked deprecated. One parameter is deprecated: `creator/rank.category_ids`, replaced by
`category_id_list`.

### Not in the docs (correcting our client notes)
- **`tiktok/video/download` is not documented.** `tiktok/video/url` is documented: a CloudFront signed URL that
  expires after 5 minutes, at 0.5 credit per call.
- No documented history, trend or time-series endpoints. Trends exist only as fields inside detail responses:
  `revenue_trend` is an array of numbers, one per day, with no date attached (video, shop, product, creator and
  category detail).
- No documented endpoints for ads, keywords, hashtags, music, creator search by handle, a category list or tree,
  brands, Amazon, Shopee, exports or favourites. The spec does contain schemas for many of these (see section 7), but
  no path uses them.

## 3. Common request conventions

- Body is JSON (`requestBody` required) on every POST. `credit/balance` is a GET with no parameters. The docs UI
  text says "All endpoints use HTTP POST", which is wrong for `credit/balance`.
- Every analytics endpoint except product/images, product/comments, product/comment/insight, video/url,
  creator/avatar-images and credit/* **requires** `region`, `language`, `currency` and `date_range`.
  `product/analysis` requires `region` and `language` but takes no currency or date_range. `product/comments` takes
  `region` with a narrower enum. `comment/insight` takes `country_code` instead of `region`, and the spec example
  is lowercase `us`.
- **Regions (enum, 24):** US, BR, MX, ID, JP, MY, PH, SG, TH, VN, GB, ES, DE, FR, IT, PL, NL, BE, CZ, AT, GR, PT,
  HU, IE. The Home page says "15 TikTok Shop Markets". The Skill page lists US, GB, ID, TH, VN, PH, MY, SG, JP, MX,
  DE, IT, FR, ES, BR. Data coverage for the other nine enum values is not stated. `product/comments` supports only
  US, SG, ID, TH, VN, PH, MY ("first-phase countries").
- **Languages (18):** zh-CN, en-US, id-ID, th-TH, vi-VN, es-ES, ja-JP, pt-BR, ko-KR, fr-FR, de-DE, pl-PL, nl-NL,
  cs-CZ, el-GR, hu-HU, pt-PT, it-IT.
- **Currencies (16):** CNY, USD, IDR, VND, THB, MYR, JPY, PHP, GBP, SGD, MXN, EUR, BRL, PLN, CZK, HUF.
- **date_range:**
  - Generic description: named `lastDay, last7Day, last30Day, last60Day, last90Day, last180Day, last365Day`,
    natural `yyyy-MM-dd~yyyy-MM-dd`, or natural month `yyyy-MM`. "Some endpoints restrict this set."
  - video, shop, product, livestream and creator **rank**: window capped at **30 days**. Allowed values are
    `lastDay`, `last7Day`, `last30Day`, a natural range spanning 30 days or less, or a natural month.
  - category **rank and detail**: only `last7Day, last30Day, last90Day, last180Day, last365Day`. Natural ranges and
    months are not accepted.
  - video, shop, product, creator and livestream **detail**: no restriction is stated, so whether last60Day through
    last365Day are accepted there is unverified.
  - Earliest available date, data latency and refresh time: **undocumented**. Isolated field notes say "commission
    rate updated daily for top products", "follower count updated daily" and "creator bio updated daily for top
    creators". Comment statistics are "expected to update every two weeks".
- **Sorting (rank endpoints):** `sort_field` is **required** (`{field, type: ASC|DESC}`), default
  `{"field":"revenue","type":"DESC"}`. The field-level text says "any numeric field from the response". Each
  endpoint description lists the allowed fields:
  - video: revenue, views, revenue_growth_rate, ads_roas, video_id, video_title, belonged_creator_id,
    belonged_creator_handle
  - shop: revenue, sales_volumn, revenue_growth_rate, unit_price, shop_type, affiliate_revenue,
    self_promotion_revenue, shopping_mall_revenue, on_sell_product_count, rank, shop_id, shop_name
  - product: revenue, commission_rate, revenue_growth_rate, sales_volumn, unit_price, launch_date, live_revenue,
    video_revenue, showcase_revenue, product_id, product_name
  - livestream: revenue, unit_price, views, livestream_start_time, livestream_end_time, livestream_duration,
    livestream_id, livestream_title, creator_id, creator_handle
  - creator: revenue, revenue_growth_rate, content_views, creator_followers, sales_volumn, video_revenue,
    live_revenue, creator_id, creator_nickname, creator_handle
  - category: revenue, revenue_growth_rate, top3_shop_revenue_ratio, average_revenue, rank, category_id,
    category_name

  The legacy `rank_field` and `asc` params still exist and are ignored when `sort_field` is set. Note the spelling
  `sales_volumn`, which is the API's own.
- **Pagination:** `page_size` max 100, default 10. `page_number` starts at 1. product/comments defaults to and caps at
  100. credit/logs uses `pageNo` and `pageSize` (max 100) and returns `total` and `hasNext`. **Rank responses have no
  total count**: `data` is a bare array.
- **Filters by endpoint** (full detail in the JSON):
  - product/rank: category_ids, shop_id, creator_id, video_id, livestream_id, revenue_range, is_affiliate (0/1),
    commission_rate (range), is_tts_product (0/1), unit_price_range, need_all, delivery_type (local/global),
    launch_date (<3, <7, >30), need_image (0/1/2), keyword, need_extra. **There is no `category_level` and no
    `is_ai_video` on product/rank**, though our client notes list both as common params.
  - video/rank: category_ids, shop_id, creator_id, product_id, revenue_range, followers_range, ads_roas, keyword,
    is_ai_video, views_range, publish_date_range (<3, <7, <30).
  - shop/rank: category_ids, revenue_range, shop_type (BRAND/RETAILER), keyword, need_image, need_category,
    unit_price_range.
  - creator/rank: category_ids (deprecated, int64), category_id_list (comma string), shop_id, product_id,
    revenue_range, creator_type (BELONGED_TO_SELLER/INDEPENDENT), followers_range, engagement_rate (LOW <8%,
    MEDIUM 8-20%, HIGH >20%), keyword, need_image, need_category, need_ter_category.
  - livestream/rank: category_ids, shop_id, creator_id, product_id, followers_range, keyword.
  - category/rank: category_ids (includes sub-categories), category_level (1/2/3), revenue_range.
  - Range syntax: `a-b`, `<x`, `>x` (commission_rate also accepts `>=30`).
- `need_image`: 0 = none (default), 1 = official URL, 2 = "kalo_data image URL (paid service required)". The price of
  option 2 is undocumented.

## 4. Authentication: conflicting statements

- The OpenAPI `securitySchemes.apiKeyAuth` is an apiKey **in header `X-API-Key`**, and the spec info text says "Add
  your API key in the `X-API-Key` header".
- The docs UI paragraph on every endpoint says "secret-key authentication in headers". The Home page curl example
  uses `-H "secret-key: YOUR_API_KEY"`. The official-linked skill client also sends `secret-key`, plus
  `source-type: SKILL` and `skill-version`.
- Our client uses `secret-key`. The docs do not settle whether the server also accepts `X-API-Key`.
- Getting a key: the spec says email kalodata_us@kalowave.com. The UI says "Go to Account to create/manage your API
  key" and that the key is "one-time" and shown once on generation. Support contact: customerservice@kalodata.com.

## 5. Billing and credits (Pricing page and pricing JSON)

- "Detail APIs cost 0.1 Credit per call; rank APIs cost 0.1 x Ceiling(returned rows/100) per call." Example given:
  101 rows costs 0.2. Since page_size max is 100, a normal rank page costs 0.1. Whether a 0-row result costs 0 is
  undocumented.
- Pricing groups (from the pricing JSON):
  - **0.1 per call (Detail API):** video/shop/product/creator/livestream/category detail, **product/analysis**
    (listed as "Get Product Specification"), **creator/avatar-images** (listed as "Get Creator Avatar").
  - **Rank API, 0.1 x ceil(rows/100):** video/shop/product/livestream/category/creator rank.
  - **1 credit:** product/comment/insight ("Get Product Comment Statistics"). Costs 1 on the first retrieval or after
    the statistics update; re-retrieval without an update is free. The endpoint description adds that it charges
    only when insight data exists and `cached_at` is newer than the last charge for this user and product, and that
    failures and timeouts are not charged.
  - **0.5:** video/url.
  - **0.01:** product/images and product/comments. product/comments costs 0.01 per call (per page of up to 100
    reviews), not per row.
  - **Free:** credit/balance and credit/logs.
- product/analysis: on a cache miss the server starts generation asynchronously and returns a failure, which is not
  charged. A charge happens only when analysis data exists.
- Credit value: "For reference, 1 point is approximately equivalent to 0.1 USD. The actual value is determined by
  point purchase rules." Purchase prices and packages are not shown publicly; buying requires login.
- **Monthly rebate:** 0-3,000 credits consumed: 0%. 3,000-30,000: 20% of that portion. Above 30,000: 50% of that
  portion. Worked example: 1.5M calls is 150,000 credits, with a 65,400 rebate (about a 40% discount). How and when
  the rebate is credited is "at month-end"; mechanics beyond that are undocumented.
- General rules for failed, errored, empty or repeated calls on the other endpoints are **undocumented**. Every
  response wrapper has a `cached` boolean, but its billing effect is not stated.
- The Home page also says "Purchase API Items: Select the target API in pricing", which suggests per-API
  enablement or purchase. The mechanics are not documented publicly.
- Skill billing, which is separate from the raw API: the TikTok Data Query Skill costs 0.2-0.4 credits per basic
  query and 1-2 per analysis scenario. The E-commerce Data Analysis skill ("kalopilot") is billed per conversation
  by tokens, about 2-5 points for simple and 10-15 for complex, and needs a purchased country data package.

## 6. Rate limits

- Per endpoint, from the spec's `x-permits`, which the UI shows as "Max N Requests /10 Second":
  - 10: all rank endpoints, video/url, product/images, product/comments, creator/avatar-images, credit/balance,
    credit/logs
  - 100: video/shop/product/livestream/category detail, product/comment/insight, product/analysis
  - **500: creator/detail**
- "Rate limits are per API key/user account. Contact support if you need higher limits."
- What happens when the limit is exceeded (HTTP 429, an error code, queueing) is **undocumented**.

## 7. Response envelope, errors, and schemas with no documented path

- Every response wraps its payload as `{success: boolean, data: ..., message: string, debug: object, cached:
  boolean, code: string}`. None of the wrapper fields has a description. Only HTTP 200 is declared.
- **Error codes: undocumented.** Secondary source only (skill client `api.py`): HTTP 200 with `code` "501" and a
  message starting "The key ..." means a rejected key, and the same code is used for missing parameters. "2000" or
  "acquire connection timeout" is retryable. "2016" means a parameter error or a membership/quota limit. "not found"
  in the message means an empty result.
- The spec ships **171 component schemas that no documented path references** (full list in
  `global.notes.schemas_without_documented_paths`). Families: Amazon (product list/batch/history trend, category
  list), Shopee (product/shop/creator/keyword/topic/category lists, details and opportunities), Brand (list, detail,
  daily revenue, products/videos/livestreams/creators), Focus/collection lists (shop/product/creator),
  ExportTask (`exportType` LIST_PRODUCT/LIST_CREATOR/LIST_SHOP/LIST_LIVES with `taskId` polling),
  FilterConfiguration, CategoryOverview, CategorySearchByKeyword, CreatorDetailByHandle, CreatorImageReq,
  ProductPicSearchRank, KeywordProduct, PriceInfo (recharges/memberships) and ApiBenefit (quota records with
  total/remain/start/end). The spec info text also says the API covers "TikTok, Amazon, and Shopee". These look like
  unreleased or private endpoints, but **their paths, prices and limits are not documented, so they are not in
  `endpoints[]`**.
- The skill CLI calls `/tiktok/category/searchByKeyword` (body includes `keyword`), which matches the orphan
  `CategorySearchByKeywordReq` and `CategorySearchRes {id, name}` schemas. It is not in the public docs, and it is
  recorded only in `global.notes`.

## 8. Website-only vs API, and MCP/CLI

- The Home page says "API/Skill is available now; MCP is coming soon." There is no official hosted MCP server. The
  GitHub skill bundles a local stdio MCP server with 20 query tools and a `kalo` CLI with nouns product, shop,
  creator, video, live, category, plus credit and config.
- Website features without a documented API: ads/creative library, keyword and hashtag analytics, brand pages,
  Amazon and Shopee data, exports, favourites/monitoring, history trends with dates, creator lookup by handle, and
  the category tree or search. Schemas hint that several of these exist server-side.
- Several website-style filters are mirrored ("Same syntax as the website" for views_range and publish_date_range).

## 9. Field-level quirks worth knowing

- Response types are inconsistent:
  - livestream/rank `revenue` and `unit_price` are **strings**; creator/rank `content_views` and `creator_followers`
    are strings; creator/detail `creator_followers` is a string; product/rank `sku_count` is a string.
  - Timestamps differ by endpoint: livestream start and end are epoch ms, review_timestamp is epoch s, credit-log
    gmtCreated is epoch ms, and video/rank `publish_date` is `yyyy/MM/dd HH:mm:ss` in the region's timezone.
  - product/detail `commission_rate` is in percentage points (1.0 = 1%). Units for commission_rate and growth rates
    elsewhere are not stated.
- product/detail `product_description[]` items have no schema. The example shows `{type:"image",url}` and
  `{type:"text",content}`. These were added to the JSON with `documented: false`.
- comment/insight sub-objects (`comment_summary`, `original_comments[]`, `pain_points[]`, `positive_points[]`,
  `usage_scenarios[]`) are untyped maps, so their inner keys are undocumented.
- Category IDs:
  - creator/rank and creator/detail type `category_ids` items as int64; other endpoints use strings.
  - shop/rank `category_info_list[]` uses colon-separated `level1:level2:level3` IDs and names.
  - product/rank's pri/sec/ter_category objects share a schema whose text says "Level-3" for all three.
- product/detail returns pri/sec/ter_cate_id but no category names. shop/detail returns `top3_product_ids`.
- `need_extra` is documented only as "Need Extra Info" (product/rank: "such as seller name, SKU quantity"). Which
  fields depend on it elsewhere, and whether it costs extra, is undocumented.

## 10. Verification against our earlier notes (2026-10-25)

| Our note | Docs say |
|---|---|
| Base `https://www.kalodata.com/openapi/v1` | Correct (servers = https://www.kalodata.com, and paths start with /openapi/v1). |
| Header `secret-key` | Matches the UI and Home example. The spec says `X-API-Key`; see section 4. |
| Detail 0.1, rank 0.1 x ceil(rows/100), comment insight 1, balance free | Correct. Also: video/url 0.5, product/images 0.01, product/comments 0.01, analysis 0.1, avatar-images 0.1, credit/logs free. |
| ~1 credit = $0.10 | Correct ("approximately"; purchase rules decide). |
| Rank 10 req/10 s | Correct. Detail endpoints are 100/10 s; creator/detail is 500/10 s. |
| tiktok/video/download | **Not documented.** |
| category_level, is_ai_video as common params | category_level exists only on category/rank. is_ai_video exists only on video/rank. |
| unit_price_range "40-80", delivery_type "global" | Documented on product/rank (delivery_type enum local/global). unit_price_range is also on shop/rank. |

## 11. Explicit uncertainties

1. Which auth header the server actually accepts (`X-API-Key` per spec vs `secret-key` per UI and example), or both.
2. Error codes, HTTP statuses and rate-limit-exceeded behaviour: undocumented. The 501/2000/2016 codes come only from
   the skill client.
3. Data freshness, update time, timezone of "lastDay", earliest historical date: undocumented. Also unknown whether
   detail endpoints accept last60Day through last365Day or ranges over 30 days.
4. Whether the nine enum regions beyond the 15 marketed markets (PL, NL, BE, CZ, AT, GR, PT, HU, IE) return data.
5. Billing for zero-row rank results, failed calls (except insight and analysis), `cached` responses, `need_image=2`
   and `need_extra`.
6. Purchase prices, credit packages, and the "Purchase API Items" per-API enablement step: behind login.
7. Inner structure of comment insight objects and product_description blocks.
8. Status of the 171 schemas with no documented path (Amazon, Shopee, Brand, Export, category search, creator by
   handle, and others): possibly private or upcoming. Not callable from documentation alone.
9. `revenue_trend` arrays carry no dates; the alignment of points to days is implied ("day-by-day series") but the
   start date is not given.
10. The mock responses in the docs UI are placeholders (`success: false`, `message: "string"`) and should not be read
    as real examples of failure.

## Sources
- https://www.kalodata.com/open-center/docs (SPA; per-endpoint `?endpoint=` deep links)
- https://www.kalodata.com/api/open-center/api-docs/public (OpenAPI JSON, primary)
- https://www.kalodata.com/open-center/pricing and https://www.kalodata.com/api/open-center/api-pricing
- https://www.kalodata.com/open-center/home
- https://www.kalodata.com/open-center/skill
- https://github.com/sailtonight/kalodata-skill (secondary: auth header and error handling cross-check only)
