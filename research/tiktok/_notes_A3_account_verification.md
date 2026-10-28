# A3 — What our own TikTok ad account supports (verified 2026-10-24/25 via the TikTok Marketing API, read-only)

Advertiser XXX ("DeskConnect IT LLC_adv"), BC XXX. All checks below are
category **A (observed in our account)**. Nothing was created, changed or spent.

| Check | Result | What it means for us |
|---|---|---|
| Account status | `STATUS_ENABLE`, type `AUCTION`, country US, currency USD | Account is usable for auction ads. |
| Balance | **$0** (no payment method yet) | Nothing can deliver until the owner adds payment. |
| Time zone | Reporting `Etc/GMT+5` (fixed UTC-5, no daylight saving); display `America/New_York` | After Nov 1 (DST ends) the account day is UTC-5 = EST, matching; before that, reporting days run one hour off Eastern daylight time. Use the account's day boundaries when comparing with Shopify. |
| Active ad-group quota | 50 (0 used) | Plenty of room for the planned structure. |
| Pixel `XXX` | Active, Shopify partner integration, setup mode DEVELOPER, first-party cookies on, **expanded data sharing on**, automatic advanced matching on (email, phone, name, address, external_id) | Good match-quality setup. Server-side events via the Shopify app are likely but not confirmed through this API; check Events Manager → event source → connection method. |
| Optimization events available on the pixel | `ON_WEB_DETAIL` (ViewContent), `ON_WEB_CART` (AddToCart), `INITIATE_ORDER` (InitiateCheckout), `ADD_BILLING` (AddPaymentInfo), `SHOPPING` (CompletePayment/Purchase), `ON_WEB_SEARCH` (Search), `LANDING_PAGE_VIEW` | We can optimize for Purchase directly, or for a higher-funnel event (AddToCart / InitiateCheckout) while purchase volume is low. |
| Value-based optimization (Web Conversions, Purchase, TikTok placement) | `vo_status: NO_VALUE`, min-ROAS and highest-value `NO_VALUE` / `NOT_SUPPORT` | **Value/ROAS bidding is not available yet**: the pixel has no purchase-value history. Start with cost-per-result (lowest cost or cost cap). Re-check after purchases accumulate. |
| Split testing | `split_test_create` available at ad-group level (creative, targeting, or bidding variable; even budget split; key metrics include cost per conversion, CVR, CTR, cost per focused view, landing-page view rate). Campaign-level split tests are allowlist-only. | A built-in A/B tool exists for clean creative tests between two ad groups. |
| Per-second retention | `report_video_performance_get` (VIDEO) returns per-second `retain` and `drop_off` for the first 60 s, plus clicks/conversions/CTR/CVR (1-hour latency) | We can see exactly which second viewers leave in each ad, the key diagnostic for hooks. |
| Benchmarks | `report_ad_benchmark_get` compares our ads with others by location/category/placement once an ad has ≥1,000 impressions in the window (30–48 h latency) | Gives a reference for 2 s/6 s view rates, CTR and CVR without guessing industry averages. |
| Reporting metric names (API) | e.g. `video_play_actions`, `average_video_play`, `video_views_p25/p50/p75/p100`, `engaged_view`, `ctr`, `total_landing_page_view`, `onsite_on_web_cart`, `complete_payment`, `cost_per_complete_payment`, `complete_payment_roas`, `profile_visits`, `likes`, `comments`, `shares`, `follows`, `frequency`, `reach`; benchmark adds `video_watched_2s`, `video_watched_6s` | Matches the metrics in the measurement plan; definitions come from the A2 notes. |
| Campaign types exposed | Manual campaigns, Smart+ (`smart_plus_*`), Upgraded Smart+ (`campaign_automation_type`), GMV Max (TikTok Shop only, not applicable: we have no TikTok Shop), catalog (bound catalog XXX) | Both manual and Smart+ structures are available to test. |
| Automated rules | `optimizer_rule_*` available | Stop-loss rules (e.g. pause an ad at spend ≥ break-even CPA with 0 purchases) can be set up once the owner approves. |
