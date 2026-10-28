# Conversions and pixels

The hub runs your ad tracking itself, so **don't also install the official Facebook & Instagram,
TikTok or Google & YouTube Shopify apps.** Doing both double-counts events.

```
Storefront ──(hub web pixel, no PII)──> /collect/pixel ──batched every minute──> Meta CAPI, TikTok Events API
                    checkout_completed ──> browser signals kept 7 days in Redis ─┐
Shopify order webhook ──> order synced ──(2 min later)──> ONE purchase per platform ─┴─> Meta, TikTok, Google
```

| Event | Meta | TikTok | Google |
|---|---|---|---|
| PageView | browser | (TikTok tracks its own) | — |
| ViewContent / AddToCart / InitiateCheckout | browser | browser | — |
| Purchase | server, once | server, once (`CompletePayment`) | server click conversion (orders with a gclid/gbraid) |

**Guarantees**
* A purchase is reported **at most once per platform**: a unique row in `conversion_events`, however
  many retries, sweeps or re-syncs happen. A sweep every 15 minutes picks up orders whose webhook
  was missed.
* Test and cancelled orders are never reported. Orders older than a platform accepts are recorded as
  `skipped` (Meta and TikTok: 7 days; Google: 90 days).
* **PII:** the browser pixel sends none. When `conversions_hashed_pii` is on (the default), the order's
  email and phone are fetched from Shopify while the purchase is sent, normalized and SHA-256 hashed.
  Only the hash leaves the hub, and nothing is stored. Visitor IP and user agent exist only in Redis
  (7 days at most), because the platforms need them to match events.
* **Consent:** Shopify only runs the web pixel when the shopper allows analytics and marketing tracking,
  and stops it after an opt-out of data sale. For server purchases, list countries you must not report
  in `conversions_exclude_countries` (e.g. EU countries if you don't collect consent there).
* Everything is **off** until you turn it on. The kill switch stops it too.

## Setup

Most of this can be run for you over SSH. Steps marked **(you)** need your login or a click.

1. **Shopify app scopes (you).** The hub's Dev Dashboard app gets two extra scopes, `write_pixels` and
   `read_customer_events`. They're added automatically by step 4, and Shopify asks you to approve the update.
   For hashed email and phone, also enable **Protected customer data access**, with the *Email* and *Phone*
   fields, in the app's Dev Dashboard settings. Without it, purchases still go out, just without those hashes.
2. **Pixels:** if you don't have them yet, the hub can create them (read-only must be off for this one step):
   ```bash
   docker compose exec api python -m app.cli settings set read_only false
   docker compose exec api python -m app.cli conversions create-pixels meta tiktok google
   docker compose exec api python -m app.cli settings set read_only true
   ```
   Copy the printed `META_PIXEL_ID`, `TIKTOK_PIXEL_ID` / `TIKTOK_PIXEL_CODE` and `GOOGLE_ADS_CONVERSION_ACTION`
   into `.env`. If you already have pixels, enter their ids instead.
3. **Platform access (you, once):**
   * Meta: Business settings > Data sources > your pixel > *Assign* the hub's system user.
   * TikTok: Events Manager > your pixel > Settings > **Events API > Generate access token**, then put it in
     `TIKTOK_EVENTS_ACCESS_TOKEN`.
4. **Deploy the web pixel** (needs `PUBLIC_BASE_URL` on the Cloudflare Tunnel):
   ```bash
   scripts/deploy-web-pixel.sh
   ```
   The first run prints a Shopify sign-in link and code **(you: open it and approve)**. The session is kept,
   so later deploys need nothing. Set `SHOPIFY_CLI_PARTNERS_TOKEN` to skip the sign-in entirely.
   The script then connects the pixel to the store. Check Shopify admin > Settings > Customer events:
   it should show **Store Hub: Connected**.
5. **Verify without affecting your data:** set `META_CAPI_TEST_EVENT_CODE` / `TIKTOK_TEST_EVENT_CODE` from the
   platforms' *Test events* screens, deploy, then:
   ```bash
   docker compose exec api python -m app.cli conversions test-event meta
   docker compose exec api python -m app.cli conversions test-event tiktok
   ```
   The events show up in each platform's test console. Then clear the test codes.
6. **Turn it on:**
   ```bash
   docker compose exec api python -m app.cli settings set conversions_enabled true
   docker compose exec api python -m app.cli conversions status
   ```

## Checking it keeps working

```bash
docker compose exec api python -m app.cli conversions check --days 7
```
This compares Shopify orders with purchases reported to each platform, and shows storefront event
volume as received by the hub and as sent to each platform. The watchdog runs the same check every
5 minutes and alerts Slack if, for example, Meta got fewer than 90% of orders, or no storefront events
arrived (pixel disconnected after a theme or app change).

## Known limits

* Google gets purchases only from orders with a Google click id. Browser-side Google tags aren't sent.
  Click conversions are what Google's bidding uses.
* `wbraid` click ids are stored in the same column as gclid, and the hub tells gbraid apart by its `0A`
  prefix. An order with a wbraid is uploaded as a gclid and Google will reject that one.
* The exact placement of `contents` in TikTok's Events API payload differs between TikTok's integration
  partners' docs. Check it with `test-event tiktok` and a real test purchase.
* Refunds aren't sent back to the platforms. Profit math uses Shopify refunds either way.
