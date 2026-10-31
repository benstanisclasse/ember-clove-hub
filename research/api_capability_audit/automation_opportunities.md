# Automation opportunities (proposal for approval, 2026-10-31)

**Nothing here is scheduled.** Each item needs the owner's go-ahead. Kalodata items also need a credit budget: the
standing budget is D1, ~30 credits/month (`config/hub.json` → `kalodata.monthly_credit_budget`). The balance on
2026-10-31 is **470.9 credits**.

Costs use Kalodata's pricing page, checked against our own credit log (`credit/logs`, free):
- Rank pages cost 0.1 per page of up to 100 rows. A 10-row page still costs 0.1.
- Detail calls cost 0.1.
- Comments cost 0.01 per page.
- An insight costs 1 the first time, then nothing until Kalodata refreshes it (about every 2 weeks).
- 1 credit ≈ $0.10.

CJ API calls carry no per-call charge. The limits that matter there:
- 100 QPS for the account.
- 1 request/second on logistics endpoints, as observed.
- A quota of 1,000 per endpoint (the period is not stated).

## A. Market monitoring (Kalodata)

| # | Automation | Endpoints and fields | Cadence | Credits / run | Credits / month | Storage | Limits |
|---|---|---|---|---|---|---|---|
| A1 | **Monthly core refresh** (already designed: top sellers, risers and top videos for 29-31 categories) | `product/rank` (sort revenue, revenue_growth_rate), `video/rank` | monthly, after the 1st | ~30 | 30 | ~10 MB | Already the D1 budget. Rank date windows are capped at 30 days. |
| A2 | **New-product radar**: launched in the last 7 days and already selling | `product/rank` with `launch_date` `<7` and `date_range` last7Day, per niche category (Womenswear, Shoes, Accessories, Jewelry = 4 cats × 1 page) | weekly | 0.4 | 1.6 | <1 MB | `launch_date` accepts only `<3`, `<7`, `>30`. Small samples, so treat as leads, not proof. |
| A3 | **Category growth monitor**: emerging vs declining subcategories, concentration | `category/rank` level 2+3 (`revenue_growth_rate`, `top3_shop_revenue_ratio`, `average_revenue`), 3 pages; `category/detail` for ~20 niche subcats (`shop_number`, `active_product_number`, channel split, `revenue_trend`) | monthly | 0.3 + 2.0 | 2.3 | <1 MB | Category endpoints accept only rolling windows (last7/30/90/180/365Day), **not months**. To build a month-by-month history, snapshot on a fixed day each month. |
| A4 | **Fast-growing shops** in our niche | `shop/rank` sorted by `revenue_growth_rate`, plus `revenue_range` floor, 4 cats × 1 page; `shop/detail` for the top 10 (`top3_product_ids`, `affiliate_revenue` vs self vs mall) | monthly | 0.4 + 1.0 | 1.4 | <1 MB | Not access-tested yet. |
| A5 | **Successful creators** in our niche (content-style benchmarks, future affiliates) | `creator/rank` 4 cats × 1 page; `creator/detail` (no contact fields stored) for the top 10 | monthly | 0.4 + 1.0 | 1.4 | <1 MB | `creator/detail` returns contact emails/phones. Don't store them without an approved purpose. |
| A6 | **Watchlist deep-dive**: daily sales trend + video list for products we are testing or considering (~20) | `product/detail` with `need_extra` (to verify that `revenue_trend` fills), `video/rank` filtered by `product_id` (1 page) | weekly | 20 × 0.2 = 4 | 16 | ~2 MB | Detail windows ≤ 30 days. Verify `need_extra` with 1 test call (0.1) first. |
| A7 | **Review mining** for watchlist and candidate products | `product/comments` (raw reviews, rating, SKU, date), 1-2 pages; `product/comment/insight` (AI summary) | per new candidate; insight re-fetch free until refreshed | 0.02 + 1.0 | ~5 for 5 new products | ~1 MB | Comments supported for US/SG/ID/TH/VN/PH/MY. The insight `cached_at` can be over a year old: check it. |
| A8 | **Product attributes & images for matching** | `product/analysis` (attributes, highlights), `product/images` | per candidate | 0.1 + 0.01 | ~1.1 for 10 candidates | images: hashes only | Image URLs expire. Store a perceptual hash/thumbnail, not the file, under the 30-day media rule. |
| A9 | **Spend reconciliation** | `credit/logs`, `credit/balance` (free) | after every run | 0 | 0 | tiny | The log has no endpoint field, so match by time and amount. |

**Suggested envelope.** A1 + A2 + A3 + A9 = **~34 credits/month**, about the current budget. Adding A4-A6 brings it to
**~53**, and A7/A8 add about 5-10 per batch of candidates. The full set is **~60-65 credits/month (≈ $6-7)**. The 470.9
credits on hand would last about 7 months at that rate.

## B. Supplier monitoring (CJ, free but rate-limited)

| # | Automation | Endpoints (MCP tool) and fields | Cadence | Calls / run | Limits |
|---|---|---|---|---|---|
| B1 | **Cost tracking** for matched variants (~150) | product detail / variant query (`get_product_variants`): `variantSellPrice` | weekly | ~60 products | CJ gives current prices only, so price history exists only if we snapshot. Ignore "suggested sell price" (the two tools disagree). |
| B2 | **Stock and availability** per variant and warehouse | `get_product_inventory`: country, sub-warehouse, `cjInventory` vs `factoryInventory`; product status | weekly (daily for live products) | ~60 | Search-level stock disagrees with inventory-level stock (95,350 vs 78,214), so use the inventory endpoint. Factory stock is not CJ-verified. |
| B3 | **Freight monitoring** CN→US (and US warehouse where stock exists) | `calculate_freight` / `calculate_freight_tip`: carrier, total, days, markup | monthly, or when weight/price changes | ~150 quotes at ≤1/s ≈ 3 min | Logistics endpoints: 1 request/second. Quotes are DDU: no duties. |
| B4 | **Event-driven updates** instead of polling | CJ webhooks: product, stock, order, logistic (all currently off) | push | n/a | Needs a public HTTPS receiver, and turning webhooks on is an account setting that **requires owner approval**. |
| B5 | **Delivery-time reality check** | tracking (`get_tracking_info`) once orders exist | per order | n/a | No orders yet. |

## C. Commercial analysis (local, no API cost)

| # | Automation | Inputs | Cadence |
|---|---|---|---|
| C1 | **Landed cost per variant** = latest CJ price + chosen freight (+ Hub fee model) | B1 + B3 + `config/hub.json` economics | after each B1/B3 |
| C2 | **Margin compression alert**: landed cost up or TikTok ASP down by more than X% | C1 + `kd_product_period.unit_price` | weekly |
| C3 | **Demand vs sourcing table**: Kalodata revenue/growth next to landed cost, price headroom (`vs_tiktok_pct`) | A1/A6 + C1 | monthly (replaces the hand-built `picking_sheet`) |
| C4 | **Bundle finder**: products co-promoted by the same creators or videos | `video/rank` by product, `product/rank` filtered by `video_id` / `creator_id` | on request; ~0.1/product |
| C5 | **Prediction ledger**: store every opportunity score, then fill outcomes next month | `opportunity_score`, `prediction` tables | monthly |

## D. Prerequisites before any schedule

1. Owner approves the credit envelope and which of A1-A9 to run.
2. Spend a single 0.1-credit test to confirm `need_extra` on `product/detail` fills `revenue_trend` and `master_image_url`.
   Maybe 1-2 more tests (0.1 each) for `shop/rank` and `creator/rank` access, since per-API enablement may be needed.
3. CJ: decide whether to keep the MCP connector (its token is embedded in the URL and silently expires) or add a direct
   CJ API key (Hub secret in a user environment variable, like the other keys).
4. Every job records a `sync_runs` entry, so Ops/Health shows freshness, following the existing analytics.db pattern.
