# TikTok test 01 — Ads Manager build status

Owner, 2026-10-28: "cna you keep track in hub ig". Updated as each ad is finished and checked. Nothing is published.

## Campaign (draft XXX) — done
- EC_TT_ProductTest01 · Sales → Website · **campaign budget $90/day** (rebate tier: 10 conversions in 7 days) · Maximum results
- One ad group only (TikTok: a second ad group disqualifies the rebate). Owner: "Keep the rebate: put all 15 ads (5 products x 3) in the one ad group, each ad promoting its own product."

## Ad group — done
- Conversion · Purchase · TikTok Pixel for Shopify · attribution 7-day click / 1-day view · no target cost · continuous, all day
- Automatic targeting: US only, no age/gender limit, no suggestions
- Rebate panel: 7 of 7 criteria met

## Ads (each: own slideshow video, 5 captions, tracked link, Shop now, AI label, Music refresh only, add-ons off, Shopping Assistant off, catalog creatives off, product cards 0/4 info)

| Ad | Promoted product | utm_content | Status |
|---|---|---|---|
| EC_TT_P001_A_PRODUCT | Brown/L 51285015003375 | p001_a | done |
| EC_TT_P001_B_LIFESTYLE | Brown/L 51285015003375 | p001_b | done |
| EC_TT_P001_C_BENEFIT | Brown/L 51285015003375 | p001_c | done |
| EC_TT_P005_A_PRODUCT | Burgundy/M 51285661614319 | p005_a | to do |
| EC_TT_P005_B_LIFESTYLE | Burgundy/M 51285661614319 | p005_b | to do |
| EC_TT_P005_C_BENEFIT | Burgundy/M 51285661614319 | p005_c | to do |
| EC_TT_P006_A_PRODUCT | Off-White/M 51284656947439 | p006_a | to do |
| EC_TT_P006_B_LIFESTYLE | Off-White/M 51284656947439 | p006_b | to do |
| EC_TT_P006_C_BENEFIT | Off-White/M 51284656947439 | p006_c | to do |
| EC_TT_P012_A_PRODUCT | Beige/US 7 51286174892271 | p012_a | to do |
| EC_TT_P012_B_LIFESTYLE | Beige/US 7 51286174892271 | p012_b | to do |
| EC_TT_P012_C_BENEFIT | Beige/US 7 51286174892271 | p012_c | to do |
| EC_TT_P013_A_PRODUCT | Caramel/M 51263562154223 | p013_a | to do |
| EC_TT_P013_B_LIFESTYLE | Caramel/M 51263562154223 | p013_b | to do |
| EC_TT_P013_C_BENEFIT | Caramel/M 51263562154223 | p013_c | to do |

## Before publishing (owner)
- Add a payment method / balance (rebate requires enough balance all 7 days).
- Optional: one test order to confirm the Purchase event fires.
- After launch: no edits and no pausing for 7 days, or the rebate is lost.
