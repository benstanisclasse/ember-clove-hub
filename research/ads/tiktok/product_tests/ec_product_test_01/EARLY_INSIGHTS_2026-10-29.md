# TikTok test 01 — early insights (2026-10-29, ~16 h of delivery)

Owner, 2026-10-29: "we need to record these insights because we are 'buying' this data the pixel is always training so
these earlier insights are key for round 2".

- Window: launch 2026-10-28 13:04 CDT to 2026-10-29 ~05:00 ET. Campaign EC_TT_ProductTest01 (XXX),
  one ad group, 15 two-picture slideshow ads (5 products x A Product / B Lifestyle / C Benefit), US, TikTok feed only.
- Raw numbers frozen in `early_insights_2026-10-29.json` (age x gender, device, watch drop-off and Shopify page data are
  not in analytics.db; daily spend/clicks and single age, gender and placement splits are, via ads-dashboard-refresh).
- Ad pictures with results: `review/tiktok_test01_ad_pictures.jpg` (Hub root).
- Scale: $184 spent, 14,716 impressions, 100 clicks, 65 landing page views, 3 add-to-carts (Shopify), 0 checkouts,
  0 purchases. **Directional only.** Re-check each point at the trial end (2026-11-04 12:04 CST) before acting.

## Insights

1. **Cable knit midi dress (P013, $52.99) leads on every measure.** Click rate 1.10% (test average 0.68%), $1.07 per
   click, 39% still watching at 25% of the video (others 23–27%), 11 of 16 likes, and on the store the only page with
   real dwell (~20 s) plus 2 of 3 add-to-carts. It is also the cheapest product and has the most photos (11) and the
   longest description.
2. **Chunky cardigan (P006, $62.56) is the weakest:** 0.35% click rate, $4.25 per click; its product-only ad had 532
   views and 0 clicks.
3. **TikTok's spend split does not yet follow the winners.** Long coat got 32% of impressions at a 0.54% click rate;
   the midi got 18%. The ad group optimizes for purchases and has none, so delivery is still exploratory.
4. **The first picture decides.** About 75% of viewers drop before 25% of the 7.6 s video (~2 s). Best holds:
   P013_C 42% ("The slit makes boots work", street), P013_B 37.5% (holiday table), P001_B 35% (holiday party).
5. **Plain studio (A Product) is weakest:** 0.56% click rate vs ~0.7% for Lifestyle (B) and Benefit (C).
6. **Audience is older than the models.** Every model looks ~25–32. Of clicks from women, 27 of 35 came from 35+;
   women 45+ took $75 of the ~$141 broken down. Men got ~a quarter of impressions and 8 clicks (broad targeting).
   Hypothesis for round 2: models who look 40–50 lift click rate with this audience.
7. **Pleat mini (P001, $170.16) loses people between click and page:** 14 clicks but 4 landing page views (others
   80–100%). Page speed checked fine (server ~0.2 s, page ready ~0.5 s), so likely accidental taps or price shock.
8. **Device:** ~80% of impressions on iPhone (0.52% click rate) vs Android 1.07%. Small sample; watch only.
9. **Cost:** CPM fell from $19.61 on day 1 to $5.29 on day 2 as delivery settled.
10. **No organic pull yet:** 0 comments, 0 shares, 0 follows.
11. **TikTok auto-added 14 creatives** (AI-generated / music refresh / text-sticker variants of P005_A): 61 impressions,
    $0.86 total, so far irrelevant.
12. **Measurement notes:** Shopify logged ~357 TikTok sessions vs 100 ad clicks; the extra ~290 came in bursts (107 in
    the launch hour) from TikTok review/preview traffic, so Shopify bounce rate and session duration for TikTok are not
    usable. Shopify shows 0 s for any one-page visit. Use TikTok clicks / landing page views for the top of the funnel.

## Round 2 inputs (after 2026-11-04; confirm against the full 7-day data first)

- Lead with P013-style items: knit dresses in the ~$50–60 range, lifestyle/benefit framing, real settings.
- Test model age as the only variable: remake P013_C and P005_B with a model who looks 40–50, same outfit and scene,
  against the originals.
- Drop the cardigan and the plain studio (A) versions; keep the coat only if an older-model lifestyle version lifts its
  click rate.
- Invest in the first frame; the second picture is seen by about a quarter of viewers.
- Consider narrowing to women (and possibly 35+) once purchase data exists; for now the data says men rarely click.

Not changed: nothing in the campaign (rebate trial, no edits until 2026-11-04 12:04 CST).

## Added 2026-10-29 afternoon (owner: "are there any other insights")

13. **Two thirds of all spend went in one hour.** Ads cleared review and started serving properly at 7 p.m. ET on
    launch day; that hour alone spent $121.64 (66% of the $184 total) at a $20.83 CPM for 28 clicks ($4.34 each). The
    day's budget was gone by ~9 p.m., so delivery stalled until midnight. **Since that burst: $62 for 72 clicks, about
    $0.87 per click**, half the blended $1.84. Round 2: expect a launch burst; start with a lower budget or launch in
    the morning, and judge cost per click on the days after launch, not the blended number.
14. **Older viewers cost far more to reach.** CPM by age: 18–24 $5, 25–34 $10, 35–44 $16, 45–54 $23, 55+ $35. Click
    rate rises with age (0.10% → 0.87%), but not enough: cost per click 25–34 $1.71, 35–44 $2.66, 45–54 $3.70,
    55+ $4.01. Whether older buyers are worth it depends on who actually purchases. Recheck once purchases exist.
    18–24 is near-dead: 1,046 views, 1 click (only $5 spent, so not costly yet).
15. **Product appeal by age (clicks / views):** the cable knit midi drew clicks evenly from 25–34, 45–54 and 55+.
    Boots clicked steadily at every age from 25 up. The cardigan drew no clicks under 35. The pleat mini drew clicks
    only from 35+ (7 of 7).
16. **Men:** ~22% of views; their few clicks went to lifestyle ads (boots B 3, cardigan B 2, coat B/C, midi C 1 each),
    possibly gift-shoppers. Too few to act on; keep women-only as a round-2 option, not a decision.

Raw numbers for 13–16 added to `early_insights_2026-10-29.json` under "added_2026-10-29_14ET".
