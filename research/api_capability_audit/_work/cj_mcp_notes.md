# CJ Dropshipping MCP server: read-only access test (2026-10-31)

Server tool prefix: `mcp__d080152b-e4e5-4731-9af2-18cef266c850__`. Full catalogue: `cj_mcp_tools.json` (70 tools).
Non-personal response samples: `cj_mcp_samples/`. Account, shop, order and dispute values are redacted everywhere.
No order, cart, payment, dispute, listing, webhook, connection or sourcing tool was called. Neither was any `open_*` or `show_*` tool, nor `get_account_balance`.

## Tool count by safety class (70)
| class | n | tools |
|---|---|---|
| read_only | 41 | lookups and quotes (25 called, see below) |
| account_modifying | 10 | add_to_cart, cancel_dispute, configure_webhook, create_dispute, create_product_connection, create_sourcing, delete_order, disconnect_product, merge_orders (conservative), save_product_to_shop |
| creates_order | 4 | create_order (payType=2 also pays from balance), submit_order_to_cart, confirm_cart_and_pay, generate_payment_link |
| financial | 3 | confirm_order, pay_by_balance, pay_by_balance_v2 |
| publishes_listing | 3 | publish_product_async, publish_product_sync, republish_product |
| ui_widget | 8 | open_listing_page, open_order_page, open_product_connect_page, open_shopping_cart, show_order_detail, show_order_list, show_product_detail, show_product_list |
| auth | 1 | get_authorize_url |

Classification notes:
- `confirm_dispute` is classed read_only because its description says it only returns reasons and refund limits ("step 2"). It was still not called.
- `merge_orders` is described as matching mergeable groups. It is paired with an async merge task (`get_merge_progress`), so it is treated as modifying.
- Few tools name an endpoint. `diagnose_shipping_methods` states POST /logistic/unavailableShippingMethods. `search_products` mentions the listV2 API. The order and payment tools name internal steps: addCart, addCartConfirm, saveGenerateParentOrder, payBalance, payBalanceV2 and createOrderV2.

## Login, account level, QPS, quota
- `check_login_status`: logged in through **"URL direct token" mode**, which is stateless with no server storage. The CJ token is embedded in the connector URL. The tool warns that the URL must be updated when the token expires, so the connector will silently stop working at token expiry.
- `get_rate_limit_status` shows the MCP server's own limiter. The tiers are read 10/s, write 2/s, auth 1/s and global 20/s, with a concurrency of 5 (1 active, 0 queued). Its description promises daily-quota used and remaining figures, but **none were returned**.
- `get_account_settings` shows the account-side config:
  - `root` = GENERAL, `isSandbox` = false, `qpsLimit` = 100.
  - `quotaLimits` has 74 per-endpoint entries, each with `quotaLimit` 1000, `quotaType` 0 (period not stated) and `requestedNum` 0 when called.
  - All four webhook types (product, stock, order, logistic) are CANCEL with no URLs.
  - Identity fields (openId, userNum, openName, openEmail) are present but redacted here. The email comes back already partly masked.
- **Upstream logistics endpoints have a much tighter limit than the MCP limiter suggests.** `get_logistics_timeliness` failed with "Too Many Requests, QPS limit is 1 time/1second". It was sent in the same instant as `calculate_freight` and `calculate_freight_tip`, so freight and timeliness calls must be serialised at 1 per second or less.
- Some endpoints in the quota list have no obvious MCP tool. These are just names in the quota config, not verified capabilities:
  - /product/queryProductsByImage
  - /product/sourcing/queryList. This contradicts query_sourcing's claim that listing is unsupported upstream.
  - /aiData/nlSql and /aiData/kb/*
  - /apiCallLog/queryPage
  - /shopping/wallet/balanceHistory and billingHistory
  - /shopping/order/createOrderV3
  - /logistic/getAvailableLogistics, getReachableCountry, partnerFreightCalculate and getOrderTrackHistory
  - /disputes/getDisputeMessages and /disputes/reply
  - /webhook/product/subscribe and unsubscribe
  - /storehouseCenterWeb/syncStorehouseVideoRequests
  - /product/listed/queryDeliveryProfiles and queryVendors
  - /product/conn/connectionLog/queryPage
  - /shopping/makeup/historyList
  - /shopping/order/queryStoreCogsCount and queryStoreProductCostDetailPage

  The REST-docs agent should confirm these.

## Calls made (25) and results
| tool | result |
|---|---|
| check_login_status | ok |
| get_rate_limit_status | ok |
| get_account_settings | ok (identity redacted) |
| get_warehouses | ok: 20 regions. US 2, CN 1, MX 12, CA 11, GB 17, DE 4, BR 40, FR 19, IT 32, AU 9, AE 30, ES 31, PH 26, VN 25, RO 23, MY 18, JP 10, TH 3, PL 35, NG 64. The `id` field holds the Indonesian country name, not an id. |
| get_category_tree | ok: the full tree in one call (about 94 KB), with 14 top-level, 89 second-level and 578 third-level categories |
| search_products | ok (keyword "barbed wire necklace", pageSize 1). totalRecords is 6000, which looks like a cap. |
| get_product_detail | ok (pid 1537624790973034496, features=enable_video) |
| get_product_variants | ok (2 variants) |
| get_product_inventory | ok |
| query_sku_detail_by_sku | ok, empty array. This is a private-inventory lookup and we hold no private stock. CJLX1504225 is the SPU code, not a variant SKU. |
| get_product_reviews | ok, total 0 |
| calculate_freight | ok: 29 options, CN to US, variant 1537624791082086400, quantity 1, no ZIP needed |
| calculate_freight_tip | ok: 29 options (same carriers and totals) with more detail |
| get_logistics_timeliness | **error**: upstream QPS limit of 1/s (see above). Not retried, because the brief allows a retry only for a parameter mistake. |
| get_storage_info | **error**: "Warehouse info not found" for factory sub-warehouse stockId 6709CCD7-0DC7-43B1-B310-17AB499E9B0A. The inventory tool hints to prefer CJ-owned stockIds (cjInventory > 0); this product has none. |
| list_shops | ok: 2 shops, one `shopify`-type (status 4) and one `api`-type (status 1). Names and ids are redacted. |
| get_my_products | ok: 10 saved products |
| list_product_connections | ok, 0 |
| get_order_list | ok, 0 |
| get_pay_order_list | ok, 0 |
| list_disputes | ok, 0 |
| query_private_inventory | ok, 0 |
| query_sourcing | **error**: sourceIds is required, and the MCP refuses an empty list ("upstream does not support listing all"). We have no sourcing ids. |
| get_platform_child_categories | **error** on the Shopify-type shop: "Store not found or Authorization Failed. Please reauthorize your store before syncing again." |
| query_platform_brands | **error**, same reauthorize message on the same shop |

Read-only tools not needed and not called: diagnose_shipping_methods, get_dispute_detail, get_dispute_products, get_merge_progress, get_order_detail, get_platform_category_attributes, get_tracking_info, query_cj_inventory, query_cogs, query_publish_status, query_shop_publish_info, query_sku_detail_page, query_sku_details and query_warehouse_order_pictures. Most need an order, dispute, listing or shop id that does not exist yet.

## Freight quotes (CN to US, 1 x 45cm variant, 24 g)
- **Delivery days: yes.** `calculate_freight.logisticAging` and `calculate_freight_tip.arrivalTime` hold "min-max" strings such as "5-11"; no unit is given. In `calculate_freight_tip`, `option.arrivalTime` is a separate, generic channel range that is often much longer, e.g. 15-35 against 5-11 for CJPacket Sensitive Pro. Use the top-level value for the route.
- **Carrier: yes.** `logisticName` (calculate_freight) and `option.enName` (tip) give names such as CJPacket Ordinary, YunExpress Ordinary, LuWei Ordinary US, USPS, DHL Official and CJPacket Sea. The tip also exposes internal channel names (`channel.cnName`/`enName`, both in Chinese) plus `optionId` and `channelId`.
- **Currency: no explicit field.** Prices are USD by convention (`logisticPrice`, `totalPostageFee`, `discountFee`) with a CNY twin (`logisticPriceCn`, `discountFeeCNY`), an implied rate of about 6.19 CNY/USD.
- **Tax and duty: only partly.**
  - `calculate_freight` returns `taxesFee` 0 on every row and `clearanceOperationFee` on two lines. That fee is 0.46 on CJPacket Eub Special Line and 0.20 on CJPacket Eub, and it is included in `totalPostageFee`.
  - `calculate_freight_tip` returns `taxesFee` and `tariff` as null.
  - Several `message` texts say the terms are DDU, with the buyer responsible for duties if customs inspects. No duty estimate is given.
- **The tip reveals CJ's markup.** `postage` is a base rate and `priceIncreases` is a percentage, so `discountFee` is roughly postage × priceIncreases/100: 3.94 × 1.30 = 5.13, and 4.19 × 1.15 = 4.82. Markups range from 105 to 130%.
- The tip also returns per-carrier `ruleTips` listing the address fields each carrier requires, with validation regexes. Types seen: zip, phone, email, houseNumber, province, recipientName and recipientAddress. Messages include warnings such as "Delivery to PO Box addresses in the United States is not available".
- Selected quotes (totalPostageFee USD / days):

| carrier | USD | days | note |
|---|---|---|---|
| CJPacket Super Pure Electricity | 4.82 | 5-11 | cheapest |
| CJPacket Pure Electricity | 5.01 | 7-14 | |
| CJPacket Sensitive Pro | 5.13 | 5-11 | |
| CJPacket Postal | 5.15 | 5-9 | |
| LuWei Ordinary US | 5.27 | 5-11 | price-priority recommendation |
| CJPacket Ordinary | 5.36 | 4-9 | the "shopMethod" saved on our My Products entry |
| YunExpress Ordinary | 5.74 | 4-7 | time-priority and composite recommendation |
| CJPacket Fast Ordinary | 6.15 | 4-6 | |
| USPS | 7.67 | 4-9 | |
| DHL Official | 30.92 | 3-7 | |
| CJPacket Sea | 82.98 | 25-30 | |

  The recommendations come from `recommendLogisticsTypeList` and the `*PrioritySort` fields.

## Product, inventory, reviews, video
- **Product detail** includes:
  - customs code `entryCode` 7117190000 and `entryNameEn` "Women's alloy necklace"
  - material, packing, product weight 20-29 g and packing weight 24-35 g
  - logistics property `productProEnSet` ["COMMON"], which `calculate_freight_tip` and `get_logistics_timeliness` need
  - per-variant dimensions 110×110×50 (unit not stated), weight, barcode, cost `variantSellPrice` (6.29 / 8.29), `listedNum` 70 and the description HTML
  - Chinese and English names
- **Surprise:** `variantSugSellPrice` is 90.01 / 118.63 in `get_product_detail` (with `suggestSellPrice` "90.01 - 118.63") but 6.29 / 8.29 (equal to cost) in `get_product_variants`. The two tools disagree, so do not trust "suggested sell price".
- **Inventory is broken down by country and by sub-warehouse.**
  - `get_product_inventory` gives a product-level `inventories[]` (per country, with a `stock[]` list of sub-warehouse `stockId`s) and a per-variant `variantInventories[].inventory[].stock[]`.
  - Each entry splits CJ-owned (`cjInventory`) from factory stock (`factoryInventory`).
  - For this necklace, all 78,214 units are factory stock in CN across 5 sub-warehouses. `cjInventory` is 0, `verifiedWarehouse` is 2 (pending verification, per the search filter's definition) and there is no US stock.
  - Search shows `warehouseInventoryNum` 95,350, which does not match 78,214.
  - One stockId comes back with curly braces in the product-level block but without them in the variant block.
- **Reviews:** the tool works, but this product has 0 reviews, so the review-item schema could not be observed.
- **Video:** the fields exist, but this product has no video URL.
  - `search_products` returns `isVideo`/`isVedio` 0 and `videoList` [].
  - `get_product_detail` with `features=enable_video` returns `productVideo` null.
  - `search_products` can filter to products with video (`productFlag`=2), and `features` has `enable_video`, which returns video ids.

## Other surprises
- **The Shopify-type shop appears unauthorized on the CJ side.** It has status 4, and platform category and brand lookups return "Store not found or Authorization Failed. Please reauthorize your store". The api-type shop has status 1. Publishing and product-connection tools would likely fail on the Shopify shop until it is reauthorized in CJ. That would change a store setting, which needs owner approval.
- No orders, pay orders, disputes, product connections or private inventory exist yet. Those endpoints answered with empty pages, so access works but their item fields could not be observed.
- The barbed wire necklace shows `myProduct: true` in search. The account has 10 products saved in My Products, none listed to a shop (`listedShopNum` "0").
- `get_category_tree` without `parentId` returns the entire 3-level tree, not just top level as the description implies.
- Several tools prefix their JSON with Chinese and English text banners, e.g. "Found 6000 products total." Parsers must strip the banner before reading the JSON.
- `create_order` has an `isSandbox` flag (simulated payment, no charge), which may be useful for a future supervised end-to-end test. That test needs owner approval.
