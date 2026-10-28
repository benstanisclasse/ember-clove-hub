# Shopify setup

The hub reads products, orders, refunds and customer ids from the Shopify Admin GraphQL API
(version pinned in `SHOPIFY_API_VERSION`, currently `2026-07`), receives webhooks for real-time
updates, and uses Shopify orders as the source of truth for revenue and profit.

Everything is built and tested already. Until the keys below are in `.env`, Shopify jobs
skip themselves and `app.cli health` shows `shopify: not configured`.

## 1. Create the app (Dev Dashboard)

Since January 1, 2026, Shopify no longer allows creating custom apps in the store admin. Store-owned
apps are made in the **Dev Dashboard** and authenticate with the *client credentials grant*.
The hub gets a 24-hour token and renews it automatically.

1. Go to **dev.shopify.com** and sign in with the account that owns the store. Click **Create app**,
   then **Start from Dev Dashboard**, and name it `Store Hub` (app names can't contain "Shopify").
2. Under **Versions**, create a version with these **Admin API access scopes**:
   `read_products`, `read_inventory`, `read_orders`, `read_customers`, plus the two pixel scopes
   `write_pixels` and `read_customer_events` (see conversions.md), so one version covers everything.
   * `read_inventory` gives the variant cost ("Cost per item"), which COGS depends on.
   * `read_all_orders` (orders older than 60 days) is rejected for Dev Dashboard apps unless Shopify
     approves it, so the hub sees the last 60 days of orders. Keep `SHOPIFY_BACKFILL_DAYS=60`.
   * The only write scope is `write_pixels`, which installs the tracking pixel. The hub never changes
     products, orders or customers.
3. **Release** the version, then **Install** the app on your store.
4. Open **Settings** and copy the **Client ID** and **Client secret** into `~/shopify-hub/.env`:
   ```
   SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
   SHOPIFY_CLIENT_ID=...
   SHOPIFY_CLIENT_SECRET=...
   STORE_TIMEZONE=America/New_York      # must match the store's timezone (status warns if not)
   STORE_CURRENCY=USD
   ```
   Client credentials only work when the app and the store belong to the same Shopify organization.
5. Deploy and check:
   ```bash
   cd ~/shopify-hub && scripts/deploy.sh
   docker compose exec api python -m app.cli shopify status
   ```

## 2. Import history

```bash
docker compose exec api python -m app.cli shopify backfill all            # products, customers, orders (SHOPIFY_BACKFILL_DAYS)
docker compose exec api python -m app.cli shopify backfill orders --days 90
```
It's safe to re-run: everything upserts on Shopify ids. Large stores take a while, because the client
paces itself to Shopify's query-cost limit. After that, the scheduler keeps things current:
* every 15 min: orders updated since the last cursor (a safety net for missed webhooks)
* nightly: all products and variant costs (cost edits send no webhook)

## 3. Webhooks (after the Cloudflare Tunnel is up)

```bash
docker compose exec api python -m app.cli shopify register-webhooks
```
This registers `orders/create`, `orders/updated`, `orders/cancelled`, `refunds/create`, and
`products/create`/`update`/`delete` to `PUBLIC_BASE_URL/webhooks/shopify`.

Each delivery is checked against `X-Shopify-Hmac-Sha256`, using the client secret, and against
the shop domain, then de-duplicated by `X-Shopify-Webhook-Id`. The payload itself is never stored,
since order webhooks contain customer emails and addresses. The worker re-fetches the order by id
through the API instead.

## 4. Costs: what makes profit correct

| Cost | Where it comes from | How to set it |
|---|---|---|
| COGS per unit | Variant **Cost per item** in Shopify | Shopify admin > Products > variant > *Cost per item* |
| COGS fallback | `products.unit_cost` | for products without a Shopify cost (SQL for now) |
| Your shipping cost per unit | `product_variants.shipping_cost` / `products.shipping_cost` | SQL for now |
| Payment fees | Exact for Shopify Payments; otherwise `PAYMENT_FEE_FALLBACK_PCT` + `_FIXED` | `.env` |

Each order line snapshots its unit cost the first time it's synced, so later cost changes
don't rewrite past profit. `v_order_profit.units_missing_cost` shows orders with uncosted items.

## 5. UTM templates (needed for ad-level attribution)

Put ids, not names, in your ads' URL parameters. Then the hub can match an order to the exact ad:

| Platform | URL parameters |
|---|---|
| Meta | `utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.id}}&utm_content={{ad.id}}` |
| TikTok | `utm_source=tiktok&utm_medium=paid&utm_campaign=__CAMPAIGN_ID__&utm_content=__CID__` |
| Google | Final URL suffix: `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={creative}` |

Click ids (`gclid`/`gbraid`/`wbraid`, `fbclid`, `ttclid`) are captured too and credit the platform even
without UTMs. Attribution is last-touch: Shopify's last visit, then the first visit, then cart
attributes. After an ad sync (Phase 3), re-match orders whose ad didn't exist yet:
`docker compose exec api python -m app.cli shopify reattribute`.
