# CJ Dropshipping Open API 2.0: documentation notes

Retrieved 2026-10-31, from the public docs at developers.cjdropshipping.com only. I did not call any CJ endpoint or CJ MCP tool and did not use any key.
The machine-readable companion is `cj_endpoints_raw.json` in this folder: 185 endpoint rows, a `global` block, 2,872 response-field rows and 1,114 request-parameter rows.

## 1. Docs structure and what loaded

- The site is built with VuePress 1.9.10 and rendered on the server, so plain HTTP GET returns the full content. I did not need a headless browser. All 36 linked pages returned HTTP 200 and **no page failed to load**.
- **Getting started (`/en/api/start/…`):** Introduction (update announcements), Development, How to Get API Key, Get Access-token, Practical Tool (Postman), Orders Synchronization Processing, Products Synchronization Processing, Webhook (payload reference), Sandbox, and Interface Call Restrictions (`limit.html`).
- **API V2.0 (`/en/api/api2/`):** an index table listing only 26 "core" interfaces, then one page per module:
  - `auth`, `setting`, `product`, `storage`, `shopping`, `logistic`, `dispute`, `webhook`, `shop`, `ticket`, `listed` and `aidata`.
  - Supporting pages: MCP Integration, Points Resource Rules, Interface Definition, Interface Field Definition, Appendix 1 Global Error Codes, Appendix 2 Country Codes, Appendix 3 Platforms, and Appendix 4 Product Logistics Property.
- **Headings and anchors:** one module page holds every endpoint as a numbered heading such as `### 1.2 Product List V2(GET)`. The deep links in `doc_url` are those heading anchors.
- **Endpoint formats:** most endpoints have a URL line, a curl example, a parameter table, a JSON response example and a field table. Newer sections (private inventory, makeup, COGS 4.3 and 4.4, outbound) use a short `URL:` or `` `POST /api2.0/v1/...` `` line and prose.
- **Nesting:** shown in four ways, so dotted paths were rebuilt from the JSON examples:
  - captioned sub-tables, such as "Product object in productList:";
  - `-` prefixes;
  - explicit `data.x[].y` names;
  - flat tables that rely on the JSON example.
  - Each field row records its evidence in `source`: `table+example`, `table (path inferred…)`, `table (nesting from "-" prefix)`, or `response example only` (with `documented: false`).
- **Gaps between the index and the module pages.** The index lists 4 interfaces that have no section on any module page:
  - `/authentication/getAffiliateAccessToken`
  - `/shopping/order/createOrder` (v1)
  - `/logistic/getTrackInfo` (marked Deprecated)
  - `/setting/account/set` (appears only as the worked PATCH example on "Interface Definition")
  - I also found mentioned-only paths: `/setting/account/get` (as a quotaUrl in an example), `/product/listed/getReceiverCountryInfo`, `/product/listed/queryVendors`, `/product/listed/getPlatformCategoryTree` and `/shop/location/queryList` (in the listing prerequisites). All of these are included as `verification: "partially documented"` stubs.

## 2. Endpoint counts per module (JSON `module` field)

| Module | Rows | Notes |
|---|---|---|
| Authentication | 4 | 3 documented plus the affiliate token (index only) |
| Setting | 4 | Get Settings, Query API Call Logs, plus 2 stubs (`account/set`, `account/get`) |
| Product | 23 | Category, list V2, global warehouse list, list (deprecated), details, my products, packaging, product detail (POST), individualization, **image search**, size chart, variants ×2, stock ×3, **reviews**, sourcing ×3, **videos** |
| Storage / Private Inventory | 7 | Warehouse detail, 5 private-inventory queries, warehouse order pictures |
| Shopping | 62 | Orders (19), payment and wallet (5), shipping info (3), COGS (4), merge order (6), address (3), private-inventory orders (10), outbound (8), makeup (3), plus the `createOrder` v1 stub. `payBalanceV2` appears twice: 2.3 and 7.9 are documented separately. |
| Logistic | 8 | `freightCalculate`, `freightCalculateTip`, `unavailableShippingMethods`, `getAvailableLogistics`, `getReachableCountry`, `trackInfo`, `getOrderTrackHistory`, plus the `getTrackInfo` stub |
| Dispute | 9 | |
| Webhook | 4 | `set`, subscribe, unsubscribe, subscribed list |
| Shop | 13 | Shops, store products, product connections (GET/POST/DELETE on the same path), connection logs, packaging connections |
| Ticket | 13 | |
| Listing (Publish) | 34 | 30 `/listed/*` endpoints plus 4 mentioned-only prerequisites |
| AI Data | 4 | `nlSql`, `nlSql/explain`, `kb/artifact`, `kb/fields` |
| **Total** | **185** | 166 "documented", 19 "partially documented" |

**Safety classes:**
- `read_only`: 124
- `account_modifying`: 39
- `creates_order`: 12
- `auth`: 4
- `financial`: 3
- `publishes_listing`: 3

Caveats on the classes:
- **`createOrderV2` and `createOrderV3` can also spend money.** They are classed `creates_order`, but with `payType=2` the documented behaviour runs add-to-cart, confirmation **and balance deduction** in one call. Treat them as financial when `payType=2`.
- **`financial`** covers `/shopping/pay/payBalance` and `/shopping/pay/payBalanceV2`. The latter has 2 rows: Payment 2.3 and Private Inventory 7.9.
- **`/shopping/makeup/createPayOrder`** only generates a payment order (payId). The payment itself happens elsewhere.
- **`/disputes/disputeConfirmInfo`** ("Confirm the dispute") returns refundable amounts before a dispute is created, so I classed it `read_only`.

## 3. Authentication and tokens

- **Flow:**
  1. Create the API key in My CJ: Apps → install the "API" app → `my.html#/authorize/API` → Add API, Type = API Key. Installing the app does not create a key.
  2. `POST /authentication/getAccessToken {"apiKey"}` returns `openId`, `accessToken`, `accessTokenExpiryDate`, `refreshToken`, `refreshTokenExpiryDate` and `createDate`.
  3. Send the `CJ-Access-Token` header on every business call.
  4. On error `1600001`, call `POST /authentication/refreshAccessToken {"refreshToken"}`. If that returns `1600003`, call `getAccessToken` again.
  5. `POST /authentication/logout` invalidates the token.
- **Lifetimes:** the access token and refresh token are **both 180 days**.
  - Server-side cache: repeated `getAccessToken` and `refreshAccessToken` calls within **24 h** return the same tokens. After 24 h or after logout, a new token is issued.
  - `getAccessToken` is limited to **QPS = 1**.
- Tokens must stay on the backend.
- `openId` is also the **webhook HMAC secret**, so treat it as a secret.
- **Optional `platformToken` header:** used on Create Order V2 and V3. The docs say it is "obtained the same way as the CJ Access Token" and may be empty. Error `1600031` means an invalid platform token.
- **CJ MCP is a separate access path.** It runs either as a local stdio build from github.com/CJ-dropshipping/api-mcp or remotely at `developers.cjdropshipping.com/mcp/<MCP token>`. Local mode logs in with CJ **email and password** (the `verify_credentials` tool). That is a different credential path from the REST API key.

## 4. Rate limits, account tiers and points (API "points" are not money)

- **Base frequency:**
  - At most 10 requests/s per IP.
  - Non-login interfaces: 30 requests/s.
  - **One IP can serve at most 3 CJ users.** Beyond that the error reads "one ip limit 3 users".
- **Per-user QPS by level:**

  | Account | Requests/s |
  |---|---|
  | Free, or sales level 0–1 | 1 |
  | Plus, or level 2 | 2 |
  | Prime, or level 3 | 4 |
  | Advanced, or level 4–5 | 6 |

  Going over returns HTTP 429 with code `1600200`. Get Settings returns `setting.qpsLimit` and `setting.quotaLimits[]` (quotaUrl, quotaLimit, quotaType).
- **Endpoint-specific limits:**
  - Listing `publishAsync`, `publishSync` and `republish`: 2 requests/s per account.
  - `queryProductsByImage`: **account Level 3+ only** (below that, `401`).
  - Dispute `uploadFile`: 10 MB per file, plus a daily upload cap (`1607020`).
  - Legacy note on `/product/list`: free or v1 users capped at 1,000 requests/day (2024-09-30).
- **Points model.** This replaced "daily call counts". It took effect on 2026-06-01 for new users and **2026-07-01** for existing users.
  - Daily total = **50,000 base points** (reset 00:00 UTC) + **order conversion** (the highest transaction amount among the last 3 months × 100 points per USD). Base points are spent first.
  - Points are replenished every minute at total ÷ 1,440. Every response carries `pointsInfo {usedToday, remaining, total}`.
  - Running out returns HTTP 429, "Insufficient API points". The global table also lists `16900500`.
- **Points are a quota, not money.** You cannot buy them directly. They grow with CJ order spend.
- **Per-call costs:**
  - `/product/queryProductsByImage`: **1000**
  - `/product/listV2` and `/product/list`: **50**
  - Most other catalogue, stock, freight, private-inventory, webhook-subscribe and wallet-history calls: **10**
  - `/apiCallLog/queryPage`, `/product/conn/connectionLog/queryPage` and `/disputes/uploadFile`: **20**
  - **Every `/listed/*` call: 10, billed even on failure.** Poll `queryPublishStatus` no more than once every 5 s.
  - Endpoints not in the table (orders, tracking, settings and so on) cost 0 points but still count against QPS.
  - The full map is in `global.quotas.points_per_endpoint`.
- **Suspension:** **zero CJ transactions for 30 consecutive days suspends API access.** A reminder email goes out after 7 days. While suspended, every call returns `1600014`. You reactivate on the My CJ API page.
- Success rule: HTTP 200 and `code` is 200 or 0 (or absent). Do not use `message` to decide success.

## 5. Webhooks

- **Register** with `POST /webhook/set`. Topics: `product`, `stock`, `order`, `logistics`, `makeup`, `privateOrder`, `dispute` and `wallet`. Each takes `{type: ENABLE|CANCEL, callbackUrls: [one public HTTPS URL]}`.
- **Receiver requirements:** HTTPS, POST, JSON, and an HTTP 200 reply within **3 s**. No localhost.
- **Signature:** the header `sign` = Base64(HMAC-SHA256(key = `String(openId)`, message = raw body)).
- **No retries.** A failed delivery is lost. Sustained failures auto-close the webhook, and you must re-register.
- **Message types:**
  - `PRODUCT` and `VARIANT`: INSERT, UPDATE or DELETE. **Sell-price-only changes are not pushed.**
  - `STOCK`: INCREASE or REDUCE, with per-warehouse `storageNum`.
  - `ORDER`: INSERT (private-inventory outbound orders only), UPDATE or ORDER_CONNNECTED. **Regular orders are not pushed on creation, and deletions are not pushed.**
  - Order splitting.
  - Sourcing result.
  - `LOGISTICS`.
  - `MAKEUP`.
  - `PRIVATE_ORDER`.
  - `WALLET`.
  - `DISPUTE_INFO`: only for disputes on store-resolvable orders, and not triggered by CJ support replies.
- **Batching:** pushes are merged over a delay of about 2 min for product and variant, and about 5 min for stock and logistics.
- **Subscription change:** product, variant and stock pushes are filtered by the product subscription (`/webhook/product/subscribe`). **After July 2026, `subscribeAll=true` is no longer available.**
- `global.webhooks.topics_payloads` holds each sample payload's paths and field table. The API page's trigger tables and status codes are in `api_page_tables`.

## 6. Deprecations

| Deprecated | Replacement | Source |
|---|---|---|
| `GET /product/list` (Product List) | `GET /product/listV2` | "This endpoint is deprecated. Use 1.2 Product List V2" |
| `POST /product/sourcing/query` | `GET /product/sourcing/queryList` | "This endpoint is deprecated. Use 5.3 Query Sourcing List" (still online) |
| `/logistic/getTrackInfo` | `GET /logistic/trackInfo` | Index table only: "Track Query (Deprecated)" |
| "Daily Call Limit" mechanism | Points model | Interface Call Restrictions page |

Deprecated fields and options:
- `cjPayUrl` and `payType=1` page payment on Create Order V2 and V3: "no longer maintained".
- `addMarkStatus` → `isFreeShipping` on `/product/list`.
- `storageNum` → `totalInventoryNum` on stock-by-vid.
- Webhook `orderNum` → `orderNumber`.
- Listing brand `value` → `brandName`.
- `/shopping/order/createOrder` (v1) appears in the index but has no documentation. Treat it as legacy.

## 7. Capability questions

- **Reviews: yes.**
  - `GET /product/productComments` (pid, score filter, pageNum/pageSize) returns `commentId`, `comment`, `commentUrls` (images), `commentUser`, `score`, `countryCode`, `commentDate` and `flagIconUrl`. It costs 0 points.
  - `POST /product/productDetail/query` also returns aggregate `score`, `comprehensiveScore`, `logisticScore`, `serviceScore` and `commentCount`.
  - WooCommerce listing (`publishAsync`) accepts `scoreList` to import CJ reviews by rating.
- **Image search: yes.** `POST /product/queryProductsByImage {imageUrl}` needs account Level 3+ and costs 1,000 points per call. It returns on-sale product summaries only, without variants.
- **Video: yes.**
  - `POST /product/queryVideosByProductId` returns `videoUrl`, `coverURL`, `duration`, width and height, plus copyright and price fields: `notCopyrightPrice` (temporary use), `copyrightPrice` (permanent), `isFree`, `isBuy` and `copyrightBuyType`. Some videos are paid.
  - Downloads **need the header `Referer: https://developers.cjdropshipping.com/`**. CJ asks users to cache videos rather than hotlink them.
  - List V2 returns `videoList` (IDs, with `features=enable_video`), and Product Details returns `productVideo` IDs.
  - Nothing documented lets you buy video copyright through the API.
- **Stock by warehouse: yes.**
  - `/product/stock/getInventoryByPid` gives per-area inventory plus per sub-warehouse `stock[]` (added 2025-11-19).
  - `/product/stock/queryByVid`, `/product/stock/queryBySku`, and `/product/variant/queryByVid` with `features=enable_inventory` also return stock.
  - Each inventory figure is split into CJ-warehouse and factory stock.
  - Also: `verifiedWarehouse`, and `/warehouse/detail` for warehouse information.
- **Freight and delivery-time estimates: yes.**
  - `freightCalculate` returns `logisticPrice` (USD and CNY), `logisticAging` (a string such as "2-5"), `logisticName`, `taxesFee`, `clearanceOperationFee` and `totalPostageFee`.
  - `freightCalculateTip` is the "more accurate" version. It adds `arrivalTime`, `postage`, `discountFee`, `remoteFee`, `wrapPostage`, `taxesFee` ("US taxes fee, **not included in postage**"), `tariff` ("EU tariff, **not included in postage**") and `clearanceOperationFee`. Here `totalPostageFee` = wrapPostage (or discountFee) + taxesFee + clearanceOperationFee + tariff.
  - Rule tips list address requirements (dutyNo, IOSS and so on).
  - Products carry `deliveryCycle` (days); `/product/list` adds `deliveryTime` of 24, 48 or 72 h (shipping lead time).
  - Order detail can return `logisticsTimeliness` when `features=LOGISTICS_TIMELINESS`.
  - The MCP tool `get_logistics_timeliness` has no matching REST section.
- **Landed cost and duties: partial.**
  - Freight quotes expose taxes, tariff and clearance fees as separate fields. They are **not** a full landed cost: there is no import VAT estimate for non-IOSS destinations and no de-minimis logic.
  - The COGS and order docs say "Duty and clearance handling are already part of freight: do not add them again". That **contradicts** the "not included in postage" labels in freightCalculateTip; see the uncertainties.
  - Orders return `iossAmount`, `iossTaxHandlingFee`, `iossTaxes`, `tariff` and `logisticsClearanceOperationFee`.
  - `iossType` options: 1 = no IOSS (the recipient pays VAT), 2 = your own IOSS, 3 = CJ IOSS.
  - Create order returns `productAmount`, `postageAmount`, discounts and `actualPayment`.
- **Prices:** all amounts are USD (BigDecimal 18,2); some freight fields are also given in CNY. Products return `sellPrice`, `nowPrice`, `discountPrice` and `suggestSellPrice`; variants return `variantSellPrice` and `variantSugSellPrice`.
- **Sandbox:** `isSandbox=1` creates an order with simulated payment and no fulfilment. The `/shopping/sandbox/*` endpoints simulate pay, status changes and tracking numbers.
- **AI Data:** a read-only SQL gateway over your own My CJ data (orders, disputes, inventory and so on). It accepts a single `SELECT` (10 points; refunded on failure). `explain`, `kb/artifact` and `kb/fields` are free.

## 8. Uncertainties and caveats

1. **Index-only endpoints.** `getAffiliateAccessToken`, `createOrder` v1 and `getTrackInfo` have no parameters or response documented. `setting/account/set` and `get` appear only in examples. Whether any of them still works is unknown.
2. **How the field paths were built.** About 500 response rows and about 470 request rows had their dotted paths inferred, either because the JSON example was missing or invalid or because the table was flat. The JSON records the evidence for each row in `source` / `path_source`. Several doc examples are not valid JSON (missing commas, a full-width colon, a stray quote). Two blocks could not be parsed at all: Query Sourcing List and one Shipping-info example.
3. **Example-only fields.** About 590 response rows exist only in the JSON examples, with no field-table row (`documented: false`). Their types are inferred from the example values.
4. **Freight versus duty.** freightCalculateTip says taxes and tariff are "not included in postage" but are included in `totalPostageFee`. The order and COGS notes say duty and clearance are "already part of freight". Which total is charged at payment needs testing, preferably in the sandbox.
5. **Change Order Warehouse method.** The heading gives no HTTP method; the curl example implies POST, and that curl points at `http://localhost:8081` (a docs artifact).
6. **Webhook INSERT triggers.** For product and variant there are both "INSERT" triggers and a statement that DELETE means "no longer sellable". Stock messageType values (INCREASE or REDUCE) do not give the direction of the change.
7. **Missing rate-limit text.** "Get Shop List" says only "no explicit annotation; gateway default". "Create Product Connection" has an empty Rate Limit heading.
8. **Account level versus membership.** The QPS tiers mix membership names (Free, Plus, Prime, Advanced) with "sales level". The image-search rule ("Level 3") does not say which scale it uses.
9. **Points that change over time.** Points depend on transaction history. The doc's 2026 dates (effective dates; `subscribeAll` removal "after July 2026") are already in force as of the retrieval date.
10. **Safety classes are my reading of the docs.** The ones most likely to be wrong are the async merge-order calls, private-inventory confirmation calls, `addCategory` (writes to the live sales channel), and `outbound/product/batch-refresh` (classed read-only).
11. **Docs only, nothing executed.** Nothing was verified by a live call.
