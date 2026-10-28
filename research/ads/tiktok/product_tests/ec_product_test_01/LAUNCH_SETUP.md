# TikTok test 01 — Stage 1 launch setup (build in TikTok Ads Manager, switched off)

Date: 2026-10-28. Owner decisions: approve all 30 ideas; 2 pictures per ad; first week = 5 products; Claude picks music;
build switched off, owner reviews before anything spends. The TikTok connector cannot create campaigns, ad groups, ads
or upload images for this ad account until December ("IN_ROLL_OUT"), so the build is done in Ads Manager.

Picture files: `data/media_generated/tiktok_test_01/final/` (1080×1920 JPG, `<ad name>_s1.jpg` then `_s2.jpg`).

## Campaign

| Setting | Value |
|---|---|
| Name | EC_TT_ProductTest01 |
| Objective | Sales → Website (website conversions); manual campaign, not Smart+ |
| Campaign budget optimisation | **Off** (budgets set per ad group, so each product gets equal spend) |
| Status | **Off** until the owner switches it on |

## Ad groups (one per product, same settings)

| Setting | Value |
|---|---|
| Optimisation location | Website · Pixel: TikTok Pixel for Shopify (XXX) · Event: **Complete payment (Purchase)** |
| Placement | **TikTok only** (select placement) |
| Audience | United States · Women · Age 25–34 and 35–44 · broad (no interests) |
| Budget | Daily **$20** (TikTok minimum) · Schedule: start when switched on, run ≥ 7 days |
| Bidding | Maximum delivery (no bid cap) · Billing oCPM · Pacing standard |
| Identity | **Ember & Clove (@emberandclove)** — Spark Ads, ads-only. Never the "FlowFit" identity |

| Ad group name | Product | Landing page |
|---|---|---|
| EC_TT_P001 | Mock Neck Side-Pleat Mini Dress | product page (each ad has its own tracked link below) |
| EC_TT_P005 | Two-Button Notch Lapel Long Coat | product page (each ad has its own tracked link below) |
| EC_TT_P006 | Stand Collar Chunky Knit Cardigan | product page (each ad has its own tracked link below) |
| EC_TT_P012 | Snap Button Fold-Over Knee Boots | product page (each ad has its own tracked link below) |
| EC_TT_P013 | Cable Knit Mock Neck Midi Dress | product page (each ad has its own tracked link below) |

## Ads (3 per ad group: Image carousel, 2 pictures, same settings)

Format **Carousel**, pictures in order slide 1 → slide 2 · Music: **Cozy Autumn Morning — Brian Streicher** (TikTok Commercial Music Library; same for all 15) · CTA **Shop now** · Turn on TikTok's **"AI-generated content"** label if Ads Manager offers it for these ads; otherwise add the text disclaimer **"Images in this ad are AI-generated."** (TikTok requires disclosure; no hashtag in the caption, no text on pictures — owner rules).

| Ad name | Pictures | Ad text (caption) | Destination URL |
|---|---|---|---|
| EC_TT_P001_A_PRODUCT | EC_TT_P001_A_PRODUCT_s1.jpg, EC_TT_P001_A_PRODUCT_s2.jpg | Mock neck, fitted bodice and a skirt that flares out from metal rings at the hip. | https://emberandclove.com/products/metal-buckle-symmetrical-pleated-sleeveless-short-skirt-with-waist-cinching-dress?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p001_a |
| EC_TT_P001_B_LIFESTYLE | EC_TT_P001_B_LIFESTYLE_s1.jpg, EC_TT_P001_B_LIFESTYLE_s2.jpg | One dress for the holiday party. Add tights and boots and you are ready. | https://emberandclove.com/products/metal-buckle-symmetrical-pleated-sleeveless-short-skirt-with-waist-cinching-dress?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p001_b |
| EC_TT_P001_C_BENEFIT | EC_TT_P001_C_BENEFIT_s1.jpg, EC_TT_P001_C_BENEFIT_s2.jpg | The detail that makes it: a full flare fanned out from metal ring hardware. | https://emberandclove.com/products/metal-buckle-symmetrical-pleated-sleeveless-short-skirt-with-waist-cinching-dress?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p001_c |
| EC_TT_P005_A_PRODUCT | EC_TT_P005_A_PRODUCT_s1.jpg, EC_TT_P005_A_PRODUCT_s2.jpg | Long burgundy coat with wide notch lapels and dropped shoulders. | https://emberandclove.com/products/long-coat?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p005_a |
| EC_TT_P005_B_LIFESTYLE | EC_TT_P005_B_LIFESTYLE_s1.jpg, EC_TT_P005_B_LIFESTYLE_s2.jpg | The long coat for November city days, over your favorite knit. | https://emberandclove.com/products/long-coat?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p005_b |
| EC_TT_P005_C_BENEFIT | EC_TT_P005_C_BENEFIT_s1.jpg, EC_TT_P005_C_BENEFIT_s2.jpg | Cut roomy and long to layer over knits, dresses and work clothes. | https://emberandclove.com/products/long-coat?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p005_c |
| EC_TT_P006_A_PRODUCT | EC_TT_P006_A_PRODUCT_s1.jpg, EC_TT_P006_A_PRODUCT_s2.jpg | Chunky rib knit with a high stand collar and button-tab shoulders. | https://emberandclove.com/products/british-commuter-style-chunky-knit-high-neck-open-front-cardigan?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p006_a |
| EC_TT_P006_B_LIFESTYLE | EC_TT_P006_B_LIFESTYLE_s1.jpg, EC_TT_P006_B_LIFESTYLE_s2.jpg | The cardigan for slow weekends: chunky rib, easy fit. | https://emberandclove.com/products/british-commuter-style-chunky-knit-high-neck-open-front-cardigan?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p006_b |
| EC_TT_P006_C_BENEFIT | EC_TT_P006_C_BENEFIT_s1.jpg, EC_TT_P006_C_BENEFIT_s2.jpg | Button the stand collar up and wear it like a jacket. | https://emberandclove.com/products/british-commuter-style-chunky-knit-high-neck-open-front-cardigan?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p006_c |
| EC_TT_P012_A_PRODUCT | EC_TT_P012_A_PRODUCT_s1.jpg, EC_TT_P012_A_PRODUCT_s2.jpg | Knee-high boots with a fold-over cuff, brass snaps and a block heel. | https://emberandclove.com/products/autumn-and-winter-high-heels-thick-heels-one-foot-stomping-warehouse-tube-high-pass-boots-for-women?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p012_a |
| EC_TT_P012_B_LIFESTYLE | EC_TT_P012_B_LIFESTYLE_s1.jpg, EC_TT_P012_B_LIFESTYLE_s2.jpg | The knee boots your sweater dresses have been waiting for. | https://emberandclove.com/products/autumn-and-winter-high-heels-thick-heels-one-foot-stomping-warehouse-tube-high-pass-boots-for-women?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p012_b |
| EC_TT_P012_C_BENEFIT | EC_TT_P012_C_BENEFIT_s1.jpg, EC_TT_P012_C_BENEFIT_s2.jpg | One pair, three outfits: midi dress, mini and jeans. | https://emberandclove.com/products/autumn-and-winter-high-heels-thick-heels-one-foot-stomping-warehouse-tube-high-pass-boots-for-women?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p012_c |
| EC_TT_P013_A_PRODUCT | EC_TT_P013_A_PRODUCT_s1.jpg, EC_TT_P013_A_PRODUCT_s2.jpg | Cable knit sweater dress with a mock neck, long sleeves and midi length. | https://emberandclove.com/products/half-high-collar-knee-length-slim-fit-woolen-dress?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p013_a |
| EC_TT_P013_B_LIFESTYLE | EC_TT_P013_B_LIFESTYLE_s1.jpg, EC_TT_P013_B_LIFESTYLE_s2.jpg | One dress for every holiday plan: dinners, visits and photos. | https://emberandclove.com/products/half-high-collar-knee-length-slim-fit-woolen-dress?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p013_b |
| EC_TT_P013_C_BENEFIT | EC_TT_P013_C_BENEFIT_s1.jpg, EC_TT_P013_C_BENEFIT_s2.jpg | A front slit that shows off tall boots and keeps you moving. | https://emberandclove.com/products/half-high-collar-knee-length-slim-fit-woolen-dress?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p013_c |

## Before switching on
- Preview each ad: pictures in the right order, caption, link opens the right product page.
- Payment method set on the ad account (balance shows $0).
- Total at the minimum: 5 ad groups × $20/day = **$100/day** (~$700 for 7 days). Owner approves the amount and the switch-on.
- Decision rules after launch (PHASE_B_EXPERIMENT_PLAN.md §5): stop an ad group at 1× break-even CPA with no add-to-cart or 2× with no purchase; winner only at ≥ 3 store-tracked purchases under break-even.
