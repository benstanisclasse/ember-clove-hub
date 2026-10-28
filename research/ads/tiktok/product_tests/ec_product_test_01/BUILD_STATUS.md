# TikTok test 01 — Ads Manager build status

Owner, 2026-10-28: "cna you keep track in hub ig". Updated as each ad is finished and checked. Nothing is published.

## Campaign (draft XXX) — done
- EC_TT_ProductTest01 · Sales → Website · **campaign budget $90/day** (rebate tier: 10 conversions in 7 days) · Maximum results
- One ad group only (TikTok: a second ad group disqualifies the rebate). Owner: "Keep the rebate: put all 15 ads (5 products x 3) in the one ad group, each ad promoting its own product."

## Ad group EC_TT_ProductTest01_AllProducts — done
- Conversion · Purchase · TikTok Pixel for Shopify · attribution 7-day click / 1-day view · no target cost · continuous, all day
- Automatic targeting: US only, no age/gender limit, no suggestions
- Rebate panel: 7 of 7 criteria met

## Ads (each: own slideshow video, 5 captions, tracked link, Shop now, AI label, Music refresh only, add-ons off, Shopping Assistant off, catalog creatives off, product cards 0/4 info)

| Ad | Promoted product | utm_content | Status |
|---|---|---|---|
| EC_TT_P001_A_PRODUCT | Brown/L 51285015003375 | p001_a | done |
| EC_TT_P001_B_LIFESTYLE | Brown/L 51285015003375 | p001_b | done |
| EC_TT_P001_C_BENEFIT | Brown/L 51285015003375 | p001_c | done |
| EC_TT_P005_A_PRODUCT | Burgundy/M 51285661614319 | p005_a | done |
| EC_TT_P005_B_LIFESTYLE | Burgundy/M 51285661614319 | p005_b | done |
| EC_TT_P005_C_BENEFIT | Burgundy/M 51285661614319 | p005_c | done |
| EC_TT_P006_A_PRODUCT | Off-White/M 51284656947439 | p006_a | done |
| EC_TT_P006_B_LIFESTYLE | Off-White/M 51284656947439 | p006_b | done |
| EC_TT_P006_C_BENEFIT | Off-White/M 51284656947439 | p006_c | done |
| EC_TT_P012_A_PRODUCT | Beige/US 7 51286174892271 | p012_a | done |
| EC_TT_P012_B_LIFESTYLE | Beige/US 7 51286174892271 | p012_b | done |
| EC_TT_P012_C_BENEFIT | Beige/US 7 51286174892271 | p012_c | done |
| EC_TT_P013_A_PRODUCT | Caramel/M 51263562154223 | p013_a | done |
| EC_TT_P013_B_LIFESTYLE | Caramel/M 51263562154223 | p013_b | done |
| EC_TT_P013_C_BENEFIT | Caramel/M 51263562154223 | p013_c | done |

## Before publishing (owner)
- Add a payment method / balance (rebate requires enough balance all 7 days).
- Optional: one test order to confirm the Purchase event fires.
- After launch: no edits and no pausing for 7 days, or the rebate is lost.

## Final check (2026-10-28, ~13:40 CT)
All 15 ads re-opened after saving: name, own slideshow video, product-page link with utm_content, 5/5 captions (all 4 new ones present), AI label (1 asset), Music refresh only, add-ons 0/2, product cards 0/4 info, Shop now, catalog creatives off. Spot-check: P006_C promotes only Off-White/M. Rebate panel: 7 of 7 criteria met. Not published.

## Published 2026-10-28 ~13:04 CT
- Campaign XXX live; ad group under TikTok review; 15 ads delivery OK. Balance $1,000.
- Live differences: budget **$120.34/day** (not $90) and **auto-add creatives ON** on all 15 ads. Left unchanged pending the owner's decision (editing during the 7-day trial cancels the rebate).
- 7-day trial: no edits, no pausing. Max spend at $120.34/day = ~$842.- Owner decision: "Keep the rebate: leave the $120.34 budget and auto-add on, and check daily which videos TikTok adds." Daily check: DAILY_CHECKS.md.
