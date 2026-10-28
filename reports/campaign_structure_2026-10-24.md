# TikTok campaign structure — test cycle 1 (designed 2026-10-24)

## Built 2026-10-25 as a DRAFT in Ads Manager (owner request; nothing published or spent)
The Marketing API's campaign/create is "rolling out, expected December" for this account, so it was built in the
Ads Manager UI (unified Manual/Smart+ flow). TikTok only saves a campaign once it has ads, so it is a **draft**
until the first videos are posted from @emberandclove and attached.

| Level | Setting |
|---|---|
| Campaign "EC \| Sales \| Test C1" | Sales → Website; **catalog campaign OFF**; **ad-group budgets** (no campaign budget); no special ad category; TikTok rebate offer **not** taken (needs campaign budget, $30+/day and Purchase optimization, and its terms) |
| Ad group "EC \| P01 Cable Knit Midi \| Screen \| ATC" | Optimization location Website · goal Conversion · pixel "TikTok Pixel for Shopify 1792800281" · **event Add to cart** · **Maximum results** · **$25/day** (TikTok may spend up to $31.25 some days; avg $25; ≤$175/week) · run continuously · US · **minimum age 18** · languages all · automatic targeting with age suggestions 18–55+, all genders |
| Ad group "EC \| P02 Turtleneck Sweater Dress \| Screen \| ATC" | Exact duplicate of P01 settings |
| Placements | TikTok (incl. search, Lemon8, PineDrama) **and TikTok Ad Network**: this flow offered no TikTok-only choice. Placement locks at publish; check placement breakdown in reporting. |
| Owner choices (2026-10-25) | Optimize Add to Cart; $25/day per ad group; US 18+ all genders |

### Ads built 2026-10-25 (draft, not published)
One ad per video. The videos were uploaded to the Creative Library and the ads run as the Ember & Clove account with
"Only show as ads" (locked on), so nothing is posted to the profile. The "post first, then Spark" plan was not used.

| Ad group | Ad name | Video | Ad text | Promoted product (card) |
|---|---|---|---|---|
| P01 | EC-P01-A03-H01-V01 \| try-on | EC-P01-A03-H01-V01.mp4 | Cable knit midi with a front slit. Mock neck, sizes S-XL, 7 colors. AI-generated video. | Cable Knit Mock Neck Midi (SKU 51263562416367) |
| P01 | EC-P01-A05-H01-V02 \| boots | EC-P01-A05-H01-V02.mp4 | Cable knit midi with a slit that opens over tall boots. Sizes S-XL. AI-generated video. | same |
| P01 | EC-P01-A06-H01-V02 \| holiday red | EC-P01-A06-H01-V02.mp4 | Red cable knit midi for December plans. Mock neck, front slit. AI-generated video. | same |
| P02 | EC-P02-A05-H01-V02 \| tights boots | EC-P02-A05-H01-V02.mp4 | Black tights, tall boots, slouchy turtleneck sweater dress. 7 colors. AI-generated video. | Turtleneck Rib Knit Sweater Dress, burgundy (SKU 51263560417519) |
| P02 | EC-P02-A06-H01-V02 \| comfort | EC-P02-A06-H01-V02.mp4 | Loose turtleneck sweater dress to wear over leggings and boots. AI-generated video. | same |
| P02 | EC-P02-A03-H01-V01 \| try-on | EC-P02-A03-H01-V01.mp4 | Slouchy turtleneck sweater dress for tights and boots. 7 colors. AI-generated video. | same |

Same on every ad (checked on each one after the last edit):
- CTA: Shop now only.
- Creative enhancements 0/3: Translate and dub, Music refresh and Video quality all off.
- Add-on enhancements 0/2: Product highlights and Generate ad card both off.
- Catalog creatives: Video, Image and Videos-from-URL all off, so only our video runs and no store photos are mixed in.
- "This ad contains AI-generated content" is ticked, with the ad's video selected.
- TikTok Shopping Assistant is off. It is an AI chat that answers shopper questions and could make claims we haven't checked.
- Product card shows the live price only. Strikethrough, Discount and Free shipping are off (unverified claims); catalog carousels are off.
- Additional destination: P01 `/products/half-high-collar-knee-length-slim-fit-woolen-dress`, P02 `/products/high-neck-loose-woolen-dress` (TikTok's 4 UTM parameters added).
- Recommended / newly generated asset auto-add: both toggles were seen off on the boots ad, but not rechecked on the other five.

Notes:
- TikTok adds the store catalog to every new or duplicated ad ("Promoted products"). With no product selected it pulls in
  catalog photos of other items, such as sandals or the Henley maxi, and drops our video. So each ad promotes one matching
  product, and catalog creatives are switched off.
- The P01 card thumbnail is the catalog's first cable-knit variant image (green), not caramel or red. The
  catalog search box wouldn't take typing, so a per-colour SKU couldn't be picked.
- Ticking the AI label re-enabled enhancements on some ads; they were switched off again afterwards.
- These settings are easy to undo in the UI. Recheck them if any ad is duplicated or edited.

Still to do before launch: payment method (owner) → final review → owner approval to click Publish.

---

Two phases over 14 days, sized to the ~$600 test budget.

## Structure
```text
CAMPAIGN  EC | Sales | Test          Sales -> Website · no campaign budget (set per ad group)
│
├─ AD GROUP  EC | P01 | Screen        $25/day · optimize: Add to Cart
│    ├─ AD  EC-P01-A01-H01-V01        hook 1
│    ├─ AD  EC-P01-A01-H02-V01        hook 2
│    ├─ AD  EC-P01-A02-H01-V01        hook 3 (different angle)
│    └─ AD  EC-P01-A02-H02-V01        hook 4
│
├─ AD GROUP  EC | P02 | Screen        $25/day · optimize: Add to Cart
│    └─ 4 ads, same pattern
│
└─ AD GROUP  EC | Winners | Purchase  $30–40/day · optimize: Purchase
     └─ best 2–3 ads from screening   (opens day 8)

LATER:  CAMPAIGN  EC | Sales | Scale  proven winners only, often as Spark Ads
```
Ad names match experiment IDs in `data/experiments.csv`.

## Settings for every ad group
| Setting | Choice |
|---|---|
| Location | United States |
| Age / gender | 18+, all |
| Placement | TikTok only |
| Optimize for | Add to Cart while screening; Purchase for Winners |
| Bidding | Lowest cost |
| Budget | Daily, per ad group (min $20) |
| Identity | @emberandclove (never FlowFit) |
| Link | Product page with UTM tags |
| Status at creation | Paused until owner approves |

## 14-day run
| Days | What happens | Daily spend |
|---|---|---|
| 1–3 | All 8 ads run; no judging (learning). Only loss limit applies. | ~$50 |
| 4–7 | Screen on 2s/6s view rate, CTR, CPC, add-to-carts. Pause clear losers (with approval); optionally swap in 1–2 new hooks. | ~$50 |
| 8 | Copy best 2–3 ads into Winners (Purchase). | — |
| 8–14 | Purchase test vs break-even CPA; shift budget from screening to Winners. | ~$40–50 |
| 15 | Review, log learnings, plan cycle 2. | — |

## Ad movement rules
- Hits loss limit (e.g. $25) with no sale -> paused, owner notified.
- Poor attention after day 3 -> recommend pause, owner approves.
- Strong attention / add-to-carts -> promoted to Winners on day 8.
- Sells at or below break-even in Winners -> winner candidate (one-change duplicates next cycle, later Scale).
- Good signs, too little data -> "promising", more budget or retest.

## Prerequisites (status 2026-10-24 evening)
| Item | Status |
|---|---|
| TikTok ad account approved | Done (STATUS_ENABLE) |
| @emberandclove identity connected | Done |
| Pixel live + Shopify catalog synced/bound | Done (match rate catching up; recheck 10-26) |
| Payment method in TikTok Ads | **Not done** (balance $0) — owner adds |
| emberandclove.com live over https | **Done** (verified 2026-10-24 ~8:13 PM ET) |
| Theme 'Ember & Clove – cart fix' published | **Pending** owner publish |
| P01/P02 chosen with current unit economics | **Done** (owner, 2026-10-24): P01 Cable Knit Mock Neck Midi Dress, P02 Turtleneck Rib Knit Sweater Dress; backup Ruffle Slit Knit Midi Skirt (reports/test_products_2026-10-24.md) |
| First 8 videos (4 per product) | **In progress** — EC-P01-A03-H01-V01 try-on ad APPROVED ($5.89); EC-P01-A02 walking base made ($1.60, needs ad text); P02 none yet |
| Build campaign paused + owner approval to launch | Not started |
