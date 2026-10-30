# TikTok test 03 — Chunky Lug Sole Loafers: ad material

Owner, 2026-10-30: "can you make the ad material?" for the loafer added to Shopify that day (draft, $57.99). This is
ad material only. No campaign is built, nothing is uploaded to TikTok, and nothing is published or spent.

## Why this product
It comes from the October opportunity report (`research/opportunity/2026-10/REPORT.md`, candidate #2).
- **Demand:** the Clarks Westlynn Ayla loafer made $204k on TikTok in September, up 85% on August.
- **Competition on CJ:** the same design (CJNS3043308) is listed by only 5 CJ stores.
- **Supplier match:** the photo check matched the shape. The CJ shoe has a metal plate where Clarks has a croc strap.

## What the top TikTok videos for the Clarks loafer do (Kalodata, pulled 2026-10-30, 0.2 credits)
Files: `research/kalodata/loafer_clarks_videos_2026-10-30.json` (detail and top 100 videos) and
`loafer_clarks_top_videos_2026-10-30.csv` (top 20 with links).

**Demand is fading.**
- Last 30 days: $61.8k revenue and 1,023 units at $68.95, from 274 videos by 150 creators.
- September was $204k, so the last 30 days are about 70% lower.
- 15 of the top 20 videos were posted in August–September.

**The seller is QVC, and the hook is "Clarks leather loafers, restocked / on a deal".**
- Captions tag @QVC and #clarks.
- The pull comes from the brand, real leather and a deal. A generic, non-leather loafer can't use any of those.

**The format:**
- Real creators doing try-ons and hauls, not AI and not slideshows. 0 of the top 20 are AI.
- 17 of the top 20 were paid-boosted, at ad ROAS 1.2–2.65.
- Paid videos made 74% of the top-100 revenue.

**Concentrated:**
- The top 20 videos made 93% of the top-100 revenue.
- Two creators made 69% of it: kelseyyyshops 40%, travel.bestie1 29% (all their videos in the top 100).

**What we can use:**
- The format: a try-on, a styling tip ("cute to style for fall"), and fall outfits.

**What we can't use:**
- The Clarks name, "leather", restock or deal hooks, and the creators' footage.

**What this means.** The September sales came from one brand-and-deal moment. That makes this product a weaker bet
than the opportunity report suggested. Read it before spending.

## What the ads copy from round 1 (TikTok lifetime report, 2026-10-29)
- **Styling tips won.** The top ad was a styling tip in a real street (1.74% CTR). That gives angles A (three outfits)
  and F (socks).
- **The seasonal moment came second** (1.17% CTR). That gives angle C (fall).
- **No plain product-only shots.** Benefit ads beat lifestyle ads, which beat product-only ads. Every ad shows the shoe
  worn, in a real place.
- **The first frame decides.** About 75% of viewers are gone by 2 seconds, so the loafers are large and sharp in the
  first slide of every ad.

## Ads (`launch_set.json`)

| Ad | Angle | Slides | Colour |
|---|---|---|---|
| EC_TT_LF_A_THREEWAYS | One pair, three outfits (mirror selfie: jeans, mini skirt, trousers) | 3 | black |
| EC_TT_LF_B_OFFICE | Desk to dinner (sidewalk commute, wine bar) | 2 | black |
| EC_TT_LF_C_FALL | The fall uniform (feet in autumn leaves, park walk) | 2 | brown |
| EC_TT_LF_D_SOLE | That chunky sole (wet cobblestones, held up to a shop window) | 2 | black |
| EC_TT_LF_E_TWOCOLOURS | Black or brown? (both pairs on a bedroom floor, putting them on) | 2 | both |
| EC_TT_LF_F_SOCKS | Loafers and socks (mini skirt, white knee socks; reuses A's skirt slide) | 2 | black |

- **Captions:** 3 per ad, 18 in total. All pass `studio/bible/rules.yaml`: no prices, delivery, discounts, testimonials,
  or comfort or material claims.
- **Pictures:** Higgsfield Flare 4K (2160x3840). References are CJ's own product photos. Prompts are in `jobs_4k.json`.
  The people are fictional and AI-made, so turn the AI-generated label on in TikTok.
- **Videos:** built by `scripts/slideshow.py`: 1080x1920, silent, 3.6 s per slide, crossfades. Pick the music in Ads
  Manager.

## Economics at $57.99 (pre-registered formula)
- Each order keeps about $35.19 after CJ $6.60, freight $11.32, fees and 5% refunds.
- Break-even CAC is $35.19 (ROAS 1.65). Target CAC is $23.59 (ROAS 2.46).
- At about $1 per click, about 2.8% of clicks must buy to break even, and 4.2% to hit the target.
- **Suggested stop rule:** stop at about $35 spent with no add-to-cart, or about $70 with no purchase.

## Before any of this can run (owner)
1. **Set the product live.** It is a DRAFT, so the ad link would 404. Also add it to the TikTok sales channel and catalog.
2. **Link it to CJ for fulfilment.** CJ has to sync the product first, then the size mapping gets confirmed.
3. **Order a sample.** The US size labels come from a standard EU chart, not measurements. The sample also confirms the
   finish.
4. **Decide on the design.** The twist-plate hardware looks like a designer loafer's. Decide whether that is acceptable
   to advertise.
5. **Fund the TikTok balance.** It is shared with rounds 1 and 2. Approve the budget and publish.

## Made 2026-10-30
- **12 pictures** at 2160x3840 in `data/media_generated/tiktok_test_03_loafer/out/` (not in git). Contact sheet:
  `data/media_generated/share_2026-10-30/loafer_ad_pictures.jpg`.
- **Remade once:** ad_F_socks_s1 was flagged by the image filter with a mini skirt and knee socks. It was reworded to a
  knee-length skirt with crew socks.
- **Checked against CJ's photos:** every picture shows the moc-toe loafer, the silver twist plate and the black lug
  sole, with no logos or text.
- **Known difference:** ad_D_sole_s2 shows a shinier, patent-like upper than CJ's semi-matte photos. Keep or drop it
  once a sample shows the real finish.
- **6 videos** in `.../final_video/`: EC_TT_LF_A–F. 1080x1920 H.264, silent; A runs 11.2 s, the others 7.6 s.
  Nothing has been uploaded to TikTok.
