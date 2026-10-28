# Ad platforms: Google Ads, Meta, TikTok

All three are behind one interface (`app/integrations/ads/base.py`):

| Reads (hourly, no approval needed) | Writes (always gated) |
|---|---|
| `get_account`, `list_structure` / `list_campaigns`, `get_daily_metrics` | `create_campaign`, `create_ad`, `upload_video`, `upload_image`, `update_budget`, `set_status` |

**Writes are blocked while `read_only` is on (the default) or the kill switch is on.** Every
attempt is logged to `actions_log`: blocked, succeeded, or failed. Campaigns, ad sets and ads
the hub creates always start **PAUSED**. Phase 5 adds approvals in front of these writes, and
Phase 6 adds the spend and budget-change limits.

Each platform switches itself on once its keys are in `.env`. Until then its sync job skips, and
`app.cli health` shows `ads: none configured`.

```bash
docker compose exec api python -m app.cli ads status          # connection + timezone/currency check
docker compose exec api python -m app.cli ads sync meta --days 30   # first import / backfill
```

The scheduler then runs each platform hourly, re-reading the last 3 days, and once nightly over
the last 7 days, because platforms keep revising conversions. Each sync is structure, then
metrics, then re-matching recent Shopify orders to ads that were new in that sync.

API versions are pinned in `.env`: `GOOGLE_ADS_API_VERSION=v25`, `META_API_VERSION=v26.0`,
`TIKTOK_API_VERSION=v1.3`. Bump them deliberately after reading each changelog.

---

## Google Ads

**What you need:** a Google Ads **manager account (MCC)** that contains your ad account, a
**developer token**, and an **OAuth client** plus refresh token.

1. **Manager account**: create one at ads.google.com/home/tools/manager-accounts (free), then link
   your ad account to it.
2. **Developer token**: in the manager account, go to *Admin > API Center* and apply. New tokens start
   at a limited access level. Apply for **Basic access** with a short description ("internal tool that
   reports performance and manages budgets for our own account"). Approval usually takes a few
   business days. Basic access is plenty for one store.
3. **Google Cloud project** (console.cloud.google.com):
   * Enable **Google Ads API**, and **YouTube Data API v3** for video ads.
   * *OAuth consent screen*: User type External, then **publish it ("In production")**. While it's in
     "Testing", Google expires refresh tokens after 7 days and the sync stops.
   * *Credentials > Create OAuth client ID > Desktop app*. That gives `GOOGLE_ADS_CLIENT_ID` / `_SECRET`.
4. **Refresh token** (scope `https://www.googleapis.com/auth/adwords`): sign in as a user with access to
   the ad account, using Google's `generate_user_credentials.py` example from the google-ads-python repo,
   or the OAuth Playground with "use your own OAuth credentials". That gives `GOOGLE_ADS_REFRESH_TOKEN`.
5. `GOOGLE_ADS_CUSTOMER_ID` is the ad account id, and `GOOGLE_ADS_LOGIN_CUSTOMER_ID` is the manager
   account id (dashes are fine). Set `GOOGLE_ADS_BUSINESS_NAME` (max 25 characters) for video ads.
6. **YouTube (video ads only)**: get a second refresh token with scope
   `https://www.googleapis.com/auth/youtube.upload`, signing in as the Google account that owns your
   brand's YouTube channel. Put it in `YOUTUBE_REFRESH_TOKEN`. Uploads are **unlisted**. YouTube's default
   quota allows only a handful of uploads per day (about 1,600 of 10,000 units each); request more in
   Cloud Console if needed.

Notes: Performance Max campaigns have no individual ads, so their spend lands on a campaign-level row
(external id `c<campaign id>`). Google has no 3-second-view metric, so `video_3s_views` is 0 for Google.
Video ads are created as **Demand Gen** video ads, which is the video format the API can create.

## Meta (Facebook / Instagram)

**What you need:** a **Business Manager** that owns the ad account, Facebook Page and Pixel; an app;
and a **system user** token.

1. business.facebook.com > *Business settings*: confirm the ad account, Page and Pixel (dataset) belong to
   your business.
2. developers.facebook.com > *Create app* > type **Business**, connected to your Business Manager.
   Add the **Marketing API** product. Copy the App ID and App Secret into `META_APP_ID` / `META_APP_SECRET`.
   The secret is used to sign every call (`appsecret_proof`).
3. *Business settings > Users > System users > Add*, with role **Admin**. *Assign assets*: the ad account
   (manage campaigns), the Page and the Pixel. Then **Generate token** for your app with the permissions
   `ads_management`, `ads_read`, `business_management`, `pages_read_engagement`, `pages_manage_ads`,
   and expiry **Never**. Put it in `META_SYSTEM_USER_TOKEN`.
4. `META_AD_ACCOUNT_ID` (with or without `act_`), `META_PAGE_ID`, `META_PIXEL_ID`.

App Review: for **your own** business's assets through a system user, standard access is enough, so no
App Review is needed. Advanced access (App Review plus Business Verification) is only required to manage
other businesses' accounts, or to get higher rate limits. The client backs off automatically on Meta's
rate-limit codes. A rejected token (code 190) fails immediately with a clear message, and the watchdog alerts.

## TikTok

**What you need:** a **TikTok for Business developer** account, an app, an advertiser authorization,
an **identity** for ads, and a **Pixel**.

1. business-api.tiktok.com > *Become a developer*. This is reviewed, typically in a few business days.
2. *My apps > Create app*, with these permission scopes: Ad Account Management, Ads Management, Reporting,
   Creative Management, Pixel Management (plus Measurement > Report Pixel Event for conversions). Tick each
   top-level box so every sub-permission is included: the Smart+ endpoints sit under Ads Management, and
   the dynamic-CTA endpoints under Creative Management > Creative Recommendation. Set the redirect URL to `https://hub.my-domain.com/oauth/tiktok`
   (any HTTPS URL you control works; you only need the `auth_code` from it). App review can take days to weeks.
3. Put the app's id and secret in `TIKTOK_APP_ID` / `TIKTOK_APP_SECRET`. Open the app's **advertiser
   authorization URL**, sign in, and pick your ad account. The browser lands on your redirect URL.
   The page itself doesn't matter; copy `auth_code=...` from the address bar and exchange it within 1 hour:
   ```bash
   docker compose exec api python -m app.cli ads tiktok-token <AUTH_CODE>
   ```
   It prints the `TIKTOK_ACCESS_TOKEN` and `TIKTOK_ADVERTISER_ID` lines to paste into `.env`.
4. **Identity**: Ads Manager > *Assets > Identities*. Link the store's TikTok account, then copy its id
   into `TIKTOK_IDENTITY_ID`. Set `TIKTOK_IDENTITY_TYPE` to `TT_USER`, or to `BC_AUTH_TT` for an account
   linked through Business Center (then also set `TIKTOK_IDENTITY_AUTHORIZED_BC_ID`). Ads run as
   **Spark Ads**: the uploaded video is posted to that account in ads-only mode. TikTok retired
   custom identities (`CUSTOMIZED_USER`) for the TikTok placement, so the hub refuses them.
5. **Pixel**: *Assets > Events > Web events*. Copy the pixel id into `TIKTOK_PIXEL_ID`.
6. **Call to action** (optional): Spark Ads in Smart+ campaigns need a *dynamic CTA* portfolio. If
   `TIKTOK_CTA_PORTFOLIO_ID` is empty, the hub builds one from TikTok's recommended CTAs on the first
   ad and logs `tiktok_cta_portfolio_created` with its id. Put that id in `.env` to reuse it.

**Campaign type.** The hub creates **Upgraded Smart+ Sales (website) campaigns** through the
`smart_plus/...` endpoints, because from 2027-01-01 TikTok's legacy `campaign/create`, `adgroup/create`
and `ad/create` stop creating Sales, App Promotion and Lead Generation campaigns. Each campaign has
CBO off and one ad group that optimises for Complete Payment on your pixel, on Automatic Placement.
Without an age range, targeting is automatic (locations only); an age range switches to custom
targeting. The `AdSpec.call_to_action` value is ignored on TikTok: the dynamic CTA picks the button.

**Budgets.** Smart+ ad groups have no fixed daily budget, only a *dynamic daily* one. It averages
over the week, so a single day can spend up to **125%** of the number the hub sets. The guardrail
limits compare against the number you set, not that daily peak.

**Ids.** Reads still use `campaign/get`, `adgroup/get` and `ad/get`, which also return Smart+
campaigns and ad groups. TikTok's `ad/get` lists a Smart+ ad once per creative, so the hub reads
Smart+ ads from `smart_plus/ad/get` instead. Reports are keyed by `ad_id_v2`: a manual ad's id, or
a Smart+ ad's id. Budget and status changes check each target's `campaign_automation_type` first
and call the `smart_plus/...` endpoint for Smart+ entities and the legacy one for older ones.

Notes: TikTok has no 3-second-view metric, so its **2-second** views are stored in `video_3s_views`.
Compare hook rates within one platform, not across platforms. Targeting uses TikTok location ids:
US, CA, GB, AU, NZ and IE are mapped in `tiktok.py` (`LOCATION_IDS`). Add others there.

---

## Attribution: make sure ads carry ids

Ad-level profit only works if each ad's URL carries its ids. Use the UTM templates in
[docs/shopify.md](shopify.md#5-utm-templates-needed-for-ad-level-attribution). Orders from ads that
didn't exist yet locally are re-matched automatically after each sync.
