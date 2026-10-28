# Google Ads setup — Ember & Clove

Started 2026-10-28. Read-only discovery first; nothing changed in any Google account.

## What exists (checked 2026-10-28)

**Shopify** (Admin API): 92 active products; 87 published to the Google & YouTube channel (the 5 eprolo
supplier products are excluded, as logged 2026-10-27); 0 orders. Primary domain emberandclove.com, USD.

**Storefront tags** (emberandclove.com HTML, `webPixelsConfigList`):
- Google & YouTube app pixel (app XXX, pixel XXX): tag IDs `XXX` (GA4) and `XXX`.
  Events go to GA4 (search, view_item, add_to_cart, begin_checkout, add_shipping_info, add_payment_info,
  purchase, ...) and to Merchant Center `XXX` (page_view, view_item, purchase).
- **No `AW-` Google Ads conversion ID anywhere**: the Google & YouTube app has no Google Ads account linked,
  so no Google Ads conversion tracking exists yet.
- Also present: Facebook pixel XXX, TikTok pixel XXX.

**Merchant Center XXX** (Chrome, owner's login):
- 1.59K items (variants): 0 approved, 1,585 Limited ("Available soon"), 1 not approved (product page unavailable).
  "Available soon" = items waiting on Google's review; none can show in ads or free listings yet.
- Linked Google Ads account: **XXX-XXX-XXXX** ("None of your ads are running").
- Suggestions: 243 Shirts & Tops missing details; automatic image improvements (off); customer-service details.

**Google Ads** (Chrome, XXX):
- XXX-XXX-XXXX — the BridgeMark Services account. Two paused **Smart** campaigns for the other business
  ("Cut Your Company Expenses" $20/day, "Business to Business Experts" $17.50/day). Goals are lead goals
  (Submit lead form, Phone call lead, Contact, Get directions); **no sales/purchase goal**.
- XXX-XXX-XXXX — "BridgeMark Services" manager account (MCC).
- No Ember & Clove campaign, no purchase conversion action.

**Connectors**: the Google Ads and Google Analytics MCP connectors both fail with
"Reauthentication is needed. Please run `gcloud auth application-default login`" — owner sign-in needed.
The `get_accounts`/`get_campaigns` tools in this session belong to the (removed) Microsoft Ads connector.

**Hub history**: no earlier Google Ads work besides the 2026-10-27 Google readiness check and Merchant Center
shipping/returns fixes in `log.md`. An archived 2026-10-19 server project has a Google Ads API client
(backups only; not in use).

## Owner decisions (2026-10-28)

- Account: owner knows of no Ember & Clove Ads account besides Merchant Center ("if you dont see the ads
  account we need to make a new one"). XXX-XXX-XXXX is BridgeMark's; the gmail login
  (XXX) only has an unfinished manager account XXX-XXX-XXXX; the BridgeMark manager
  XXX-XXX-XXXX has no client accounts. → **New Ember & Clove account; the owner creates it** (Claude does not
  create accounts or enter billing), via Shopify > Google & YouTube > Google Ads > Get started, signed in as
  the Google login that owns Merchant Center XXX.
- Tracking: approved — link the Ads account in Shopify's Google & YouTube app (done by the app when the
  account is created there).
- Campaign: approved — Performance Max, about $15/day, built paused; enabled only after products are
  approved in Merchant Center and the purchase conversion exists.

## Status

- [ ] Owner creates the Ember & Clove Ads account in the Shopify Google & YouTube app (and billing)
- [ ] Verify: `AW-` ID in the storefront `webPixelsConfigList`; "Purchase" conversion action primary
- [ ] Merchant Center linked to the new account (XXX-XXX-XXXX link left alone unless the owner asks)
- [ ] PMax built paused, $15/day, US; ad text checked against the rules
- [ ] Products approved in Merchant Center → owner turns the campaign on

## Proposed plan (as first written)

1. Account — a separate Ember & Clove Google Ads account under the BridgeMark manager (XXX-XXX-XXXX),
   USD, time zone Eastern. Owner creates it and adds billing. Reason: XXX-XXX-XXXX carries BridgeMark's
   name, lead goals and B2B history; a clothing store's ads, verification and conversion data belong apart.
2. Merchant Center — link MC XXX to the new account (and unlink XXX-XXX-XXXX if the owner wants).
   Wait for the 1,585 "Available soon" items to be approved; fix the 1 unavailable page.
3. Purchase tracking — connect the new Ads account in Shopify's Google & YouTube app (Settings > Google Ads),
   which adds the `AW-` tag and purchase / add-to-cart / begin-checkout conversions through the existing
   app pixel, with enhanced conversions. Verify: AW- ID in `webPixelsConfigList`, conversion action
   "Purchase" set as primary, status changes from "No recent conversions"/"Unverified" after the first order.
4. First campaign — Performance Max (retail, feed from MC), US, Maximize conversion value without a target,
   about $15/day, built **paused**; enable only after products are approved and the purchase conversion
   is in place. Ad text follows the rules: no price, no shipping/delivery times, no AI-disclosure text.
