# Ember & Clove — TikTok analytics API setup

One-time setup so `tiktok_insights.py` can pull followers, views, watch time, traffic sources and audience data for @emberandclove.

Endpoints used (TikTok API for Business v1.3): `/tt_user/oauth2/token/`, `/tt_user/oauth2/refresh_token/`, `/business/get/`, `/business/video/list/`.

## 1. Prepare the TikTok account (in the TikTok app, signed in as Ember & Clove)

1. Switch it to a **Business Account**: Profile → ☰ → Settings and privacy → Account → *Switch to Business Account*. Free, takes a minute.
2. Post at least one video, then open **Analytics** in the app and tap **Turn on**. TikTok returns no analytics through the API until this is done.

## 2. Create a developer app (business-api.tiktok.com)

1. Sign in at https://business-api.tiktok.com with the TikTok for Business login that owns the DeskConnect IT Business Center, and register as a developer if asked.
2. **Fill in the Accounts API Access Application Form first.** Since March 20, 2026 TikTok requires it before any app that asks for the "TikTok Accounts" scope. Describe the use honestly: *"Read analytics for our own brand account @emberandclove to report on content performance."*
3. Create the app. Under permissions, select the **TikTok Accounts** scopes for account info, account media/video list and insights.
4. Set the **TikTok account holder redirect URL**. Any HTTPS address you control works, for example your website plus `/tiktok-callback`. The page doesn't need to exist; you only copy the address TikTok sends you to.
5. Submit for review. Approval usually takes a few days.

## 3. Connect the script

1. Run `python tiktok_insights.py report` once. It creates `tiktok_config.json` and stops.
2. Open `tiktok_config.json` and paste in the app's **App ID**, **Secret** and the exact **redirect URL** from step 2.4.
   Keep this file private, and don't paste the secret into a chat.
3. In the developer portal, open your app and copy its **TikTok account authorization URL**. Open it in a browser, sign in as **Ember & Clove**, and approve every permission.
4. You'll land on your redirect URL. Within 10 minutes, run `python tiktok_insights.py auth` and paste that full address when asked.
   It saves `tiktok_tokens.json`. Tokens refresh automatically for a year.

## 4. Pull the data

    python tiktok_insights.py report

This writes to `reports/`:

| File | What's in it |
|---|---|
| `emberandclove-report.md` | Profile, follower demographics, 60-day totals, every post ranked by views |
| `emberandclove-posts.csv` | Every post with all fields: views, reach, likes, comments, shares, saves, watch time, completion rate, new followers, retention curve, traffic sources, viewer countries |
| `emberandclove-daily.csv` | Day-by-day followers gained/lost, views, profile views, likes, comments, shares |
| `emberandclove-raw.json` | The untouched API responses |

Run it again any time for fresh numbers. Use `--days 30` for a shorter window; TikTok keeps 60 days of daily data, while per-post totals are lifetime.

## Limits to expect

- Follower demographics (age, gender, country, city, active hours) only appear once the account has **100+ followers**.
- Daily numbers lag 24–48 hours.
- A missing scope makes the API return an error naming the problem. The `auth` step warns you which scopes weren't granted. If any are missing, re-open the authorization URL, approve everything, and run `auth` again.
