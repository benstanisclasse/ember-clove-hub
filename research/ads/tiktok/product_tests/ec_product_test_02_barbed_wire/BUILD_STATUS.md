# TikTok test 02 — Barbed wire necklace: Ads Manager build status

Owner, 2026-10-29 ~20:00 ET: "Can you set up set up a new ad campagin on tiktok for hte necklace but i need you to make more
angle can you take what is working in the currecnt campagin and us it here". Nothing is published or spending.

## What round 1 says now (TikTok lifetime report, 2026-10-29 ~21:00 ET, $290 spent, 0 purchases)

| Signal | Number | Used here as |
|---|---|---|
| Top ad: P013_C "The slit makes boots work" (styling tip, real street) | CTR 1.74%, $1.07/click, 49% still watching at 25% | Styling-tip angles: E stack, I three-ways, M2 stack |
| Seasonal moment: P013_B holiday table | CTR 1.17%, $0.96/click | H gift, M4 "holiday gift for the man who wears black" |
| By concept (all 5 products) | Benefit 0.97% > Lifestyle 0.82% > Product 0.71% CTR | No plain product-only ad; every ad is worn, in a real place |
| First frame decides (~75% gone by 2 s) | Best holds 49% / 38% / 36% | Necklace large and sharp in frame 1 of every ad |
| TikTok's auto-added creatives | ~$30, few clicks | Leave auto-add off if offered |
| Kalodata: the top TikTok videos for this necklace are creator selfies | car / bedroom / patio, finger on the chain | J selfie clip, K getting ready, L weekend |
| Men ~22% of views, clicks only on lifestyle ads | small sample | M1–M4 (4 men's ads) in the same broad ad group; TikTok decides who sees what |

## Campaign draft (draft id XXX) — done, unpublished
- **EC_TT_BarbedWire01** · Sales → Website · Catalog campaign **off** · ad group budget · no split test
- No rebate offer was shown for this campaign, so it is not limited to one ad group.

## Ad group EC_TT_BarbedWire01_All (draft XXX) — done
- Website · Conversion · TikTok Pixel for Shopify 1792800281 · **Purchase** · **Maximum results** (no target cost)
- **$30/day** (TikTok: up to $37.50 some days, max $210/week) · run continuously, **starts Nov 5, 2026 09:15 ET**
  (after round 1's rebate trial ends Nov 4 12:04 CST; nothing can deliver before that even if published)
- Automatic targeting, US, no age limit, no suggestions (owner's round-1 choice: "TikTok decides entirely on its own")
- Placements: automatic (TikTok + TikTok Ad Network), as round 1

## Ads — blocked
TikTok's new unified flow attaches catalog products to every ad ("Promoted products", default *All products*), even with
Catalog campaign off. The necklace is **not in the TikTok catalog** (nkpfvz-ra.myshopify.com-shopify1, 83 products):
in Shopify it is published only on the Online Store channel. With *All products*, tapping a product card would open
other items, so no ads were saved. To fix: publish the necklace to the TikTok sales channel in Shopify (owner OK
needed: store change), wait for the catalog sync, then pick only the necklace as the promoted product.

## Videos — in the TikTok Creative library (uploaded 2026-10-29)
13 videos, 1080x1920, silent, AI pictures (Higgsfield Flare 4K) + one AI clip. Built by `scripts/slideshow.py` from
`launch_set.json` (slides, captions, links). Files: `data/media_generated/tiktok_test_02_barbed_wire/final_video/`.

| Ad | Angle | Length | utm_content |
|---|---|---|---|
| EC_TT_BW_D_SOFTEDGE | Soft knit, sharp necklace | 7.6 s | bw_d |
| EC_TT_BW_E_STACK | Stack it | 7.6 s | bw_e |
| EC_TT_BW_F_NIGHTOUT | Night out | 7.6 s | bw_f |
| EC_TT_BW_G_GROWNUP | Weekend to Monday | 7.6 s | bw_g |
| EC_TT_BW_H_GIFT | For the friend with an edge | 7.6 s | bw_h |
| EC_TT_BW_I_THREEWAYS | One necklace, three outfits (new) | 11.2 s | bw_i |
| EC_TT_BW_J_SELFIE | Car selfie clip + close-up (new) | 8.6 s | bw_j |
| EC_TT_BW_K_GETREADY | Getting ready at home (new) | 7.6 s | bw_k |
| EC_TT_BW_L_WEEKEND | Sunny weekend (new) | 7.6 s | bw_l |
| EC_TT_BW_M1_HIM_NIGHTOUT | Him: night out (new) | 7.6 s | bw_m1 |
| EC_TT_BW_M2_HIM_STACK | Him: stacked chains (new) | 7.6 s | bw_m2 |
| EC_TT_BW_M3_HIM_KNIT | Him: soft knit (new) | 7.6 s | bw_m3 |
| EC_TT_BW_M4_HIM_SHARP | Him: open collar (new) | 7.6 s | bw_m4 |

Each ad, when built: own video, 3 captions from `launch_set.json` (checked against `studio/bible/rules.yaml`: no
prices, delivery, discounts or testimonials), link `…/products/silver-barbed-wire-necklace?utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_tt_barbedwire_01&utm_content=<above>`,
Shop now, AI-generated label, product card price/discount/shipping info off, auto-add creatives off where offered.

## Winner-style clips (WINNER_STUDY.md) — in the TikTok Creative library (uploaded 2026-10-29)
| Ad | Video used | Label | Captions |
|---|---|---|---|
| EC_TT_BW_V1_CAR | EC_TT_BW_V1_CAR_LABEL.mp4 (10 s) | barbed wire necklace | see launch_set.json |
| EC_TT_BW_V2_NIGHT | EC_TT_BW_V2_NIGHT_LABEL.mp4 (10 s) | edgy but dainty | see launch_set.json |
Owner, 2026-10-29: "Yes, use the text-label versions of the winner-style clips." V3 dangle and V4 patio wait for a
Higgsfield API top-up. With these, the draft will have 15 ads.

## Before it can go live (owner)
1. OK to publish the necklace to the TikTok sales channel in Shopify (so the ads can promote it).
2. CJ balance is $0.00: orders are linked to CJ but won't ship until the CJ order is paid or the balance is funded.
3. Approve the 13 ads, $30/day and the Nov 5 start, then publish (TikTok balance is shared with round 1).
4. Stop rule (from PLAN.md): stop at ~$47 spent with no add-to-cart, or ~$94 with no purchase.
