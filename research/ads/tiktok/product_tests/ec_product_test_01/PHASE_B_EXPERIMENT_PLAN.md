# TikTok image-ad test 01 — Phase B: experiment design

Date: 2026-10-28. Status: **design for owner review; nothing generated beyond the one cost probe, nothing published
or spent.** Matrix (30 rows): `creative_matrix.csv`. Per-product hypotheses and copy: section 7.

## 1. Owner decisions applied (2026-10-28)

| Decision | Owner answer | How it is applied |
|---|---|---|
| Product list | Swap P002, P004, P008, P010 for in-season products | P002/P004/P008/P010 retired (reasons kept in Phase A); added P011 Snap Collar Faux Leather Jacket, P012 Snap Button Fold-Over Knee Boots, P013 Cable Knit Mock Neck Midi Dress, P014 Striped Polo Collar Knit Sweater |
| Text on images | "yes you can add words" | Short headline on slide 1, optional short line on slides 2–3, added by us after generation (never baked in by the AI model) |
| Buyer research | Use today's research briefs | No new ICP reports; briefs in `CREATIVE_RESEARCH_BRIEFS.md` |
| AI models | OK in paid ads | AI people allowed; every ad labelled AI-generated (TikTok AIGC label on the Spark post + "#aigenerated" in the caption) |
| Picture cost | One test picture first | Done: see section 8 |
| Budget | Set at the end | Section 5 gives the structure and the formula; amounts left blank |

## 2. The test product list (10)

| ID | Product | Price | Break-even CPA | Kept at $20 CPA | Role |
|---|---|---|---|---|---|
| P001 | Mock Neck Side-Pleat Mini Dress | $170.16 | $69.49 | $49.49 | Holiday-party pair (time-boxed) |
| P003 | 3D Rose Blazer Mini Dress | $122.32 | $50.59 | $30.59 | Holiday-party pair (time-boxed) |
| P005 | Two-Button Notch Lapel Long Coat | $100.04 | $40.54 | $20.54 | Season core |
| P006 | Stand Collar Chunky Knit Cardigan | $62.56 | $33.72 | $13.72 | Season core |
| P007 | Notch Lapel Faux Suede Blazer | $60.90 | $33.71 | $13.71 | Layering |
| P009 | Fleece-Lined Hooded Zip Jacket | $66.30 | $33.53 | $13.53 | Season core (relaxed/oversized cut stated honestly) |
| P011 | Snap Collar Faux Leather Jacket | $60.42 | $31.50 | $11.50 | Layering |
| P012 | Snap Button Fold-Over Knee Boots | $91.16 | $29.90 | $9.90 | Season core (boots rise Nov–Dec) |
| P013 | Cable Knit Mock Neck Midi Dress | $52.99 | $30.25 | $10.25 | Season core (brand hero category) |
| P014 | Striped Polo Collar Knit Sweater | $53.99 | $30.48 | $10.48 | Season core |

Economics are estimates (see Phase A). Break-even CPA = contribution before ads.

## 3. What this test can and cannot answer

- **Product question (primary):** which products reach purchases at a cost below their break-even CPA. Answered
  per product, ad group by ad group, with equal budgets.
- **Creative question (secondary):** which of three treatments (A product-first, B lifestyle, C feature/benefit)
  works better *for a given product*. Within one ad group TikTok shifts delivery toward the ad it predicts best, so
  stage 1 gives only a directional read; a fair creative comparison needs stage 2 (section 5).
- Each concept differs in several visual details at once. Results compare **creative treatments**, not single
  elements (model vs no model, text vs no text). Any single-element question needs its own follow-up test.
- Pooled "A vs B vs C across products" patterns are descriptive only: product mix and uneven delivery confound them.

## 4. Controlled variables (held constant within each product)

Objective (Sales, website, purchase event), landing page (the product page), variant shown (one colour per product,
section 7), price and offer (none in ads), audience (US women 25–45, broad, same for all products), placement
(TikTok), attribution window (TikTok default, recorded at launch), CTA button ("Shop now"), identity
(@emberandclove Spark Push, ads-only posts), music (one Commercial Music Library track per product, same for A/B/C),
caption structure (one sentence + #aigenerated), launch date and measurement window.

## 5. Campaign structure and testing sequence (proposal; budget amounts set by owner at the end)

- **Campaign:** `EC_TT_ProductTest01` — Sales, website, optimise for Complete Payment (purchase). The pixel has no
  purchase history; if TikTok cannot exit learning (~25 results / 7 days), the fallback is to optimise for
  Initiate Checkout in a *separate* campaign, labelled as a proxy. Not Traffic or engagement.
- **Ad groups:** one per product (`EC_TT_P005_LongCoat`), **ad-group budgets, not CBO**, so every product gets equal
  spend. TikTok minimum $20/day per ad group, $50/day per campaign.
- **Ads:** three per ad group, named `EC_TT_P005_A_PRODUCT`, `EC_TT_P005_B_LIFESTYLE`, `EC_TT_P005_C_BENEFIT`.
- **Stage 1 — product screening** (≥ 7 days): all products with A/B/C each. Reads products; creative read is
  directional. Budget = products × daily ad-group budget × days (e.g. 10 × $20 × 7 = $1,400 at the minimum).
  Option to halve: screen 5 products in week 1 and 5 in week 2 (same structure).
- **Stage 2 — creative test** for the 2–3 products whose stage-1 cost per purchase is under break-even: one ad group
  per concept (or TikTok Split Test for two concepts, ≥ 7 days, no CBO), equal budgets.
- **Stage 3 — validation:** the winning product × concept at a higher budget against a fresh control; then video.
- **Holiday pair (P001, P003):** party orders need about 2–3 weeks to arrive, so they are only worth testing if
  stage 1 starts by about Nov 5; otherwise hold them to January (New Year's events) or drop.
- **Decision rules** (in money, not CTR): stop an ad group when spend reaches 1× break-even CPA with no add-to-cart,
  or 2× break-even CPA with no purchase; call a product **promising** at ≥ 1 purchase with CPA ≤ break-even, and a
  **winner** only at ≥ 3 store-tracked purchases with CPA ≤ break-even (hub.json `winner_min_purchases`). Anything
  in between is **inconclusive**. CTR and CPC are diagnostics, never the deciding metric.

## 6. Tracking plan

- **URL per ad:** product page + `utm_source=tiktok&utm_medium=paid_social&utm_campaign=ec_product_test_01&utm_content=p005_a`
  (fixed values, not macros: earlier TikTok preview clicks arrived with an unfilled `__CAMPAIGN_NAME__`). Built with
  `scripts/attribution.py tag_link(url, "tiktok_ads", "ec_product_test_01", "p005_a")`.
- **IDs:** test `ec_product_test_01`; product `P0xx`; concept `A|B|C`; ad name `EC_TT_P0xx_X_TYPE`;
  experiment id `T01-P0xx-X` (30 rows go into `data/experiments.csv` when the creative is approved).
- **Events:** TikTok pixel (Shopify partner integration, server-side events included) — ViewContent, AddToCart,
  InitiateCheckout, AddPaymentInfo, CompletePayment. No extra pixel or Events API setup, so no duplicate purchases.
- **Truth source:** Shopify orders matched by utm_content (dashboard store attribution), kept separate from
  TikTok-claimed purchases. Contribution per order from the profit engine.
- **Metrics:** spend, impressions, clicks, CTR, CPC, CPM, landing-page views, add-to-cart, checkout, purchases
  (platform and store), CPA, conversion value, ROAS, contribution after ad cost.

## 7. Per-product hypotheses, visuals and copy

Shared hypotheses: **A product-first** - the product's own look, shown large on a plain studio backdrop, creates purchase interest without a setting or story. **B lifestyle** - the product worn in a believable, desirable real-life moment lifts intent over a product-first image. **C feature/benefit** - one concrete, verified feature or styling advantage, shown as proof, gives a clearer reason to buy than look or mood alone. Each product's angles come from its brief. Copy follows the brand guide: no prices, dates, urgency, reviews or claims beyond the product page; never wool, leather (only faux leather/PU), warm, slimming or waterproof. Variant colours must be checked against real photos in Phase C (Camel cardigan and Berry dress had photo mismatches). Studio backdrops are warm cream (brand palette); all people are fictional AI models with natural poses, uncrossed legs and November settings.

### P001 Mock Neck Side-Pleat Mini Dress (variant shown: Brown)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P001_A_PRODUCT | Visual attraction | Sculpted pleats, clean lines | 1 Model in the brown dress, studio cream backdrop, dress fills frame | 2 Side profile: mock neck and fitted bodice | 3 Pleats flaring at the hip, mid-step | Mock neck, fitted bodice and pleats that flare from metal rings at the hip. #aigenerated | Can a premium dress sell on silhouette alone? |
| EC_TT_P001_B_LIFESTYLE | Occasion need | Holiday party, one piece | 1 Evening holiday dinner, warm lights, dress with sheer black tights and knee boots | 2 At the table with friends, dress visible | 3 Leaving with a long coat over the dress | One dress for the holiday party. Add tights and boots and you are ready. #aigenerated | Does a party occasion beat the dress shown on its own? |
| EC_TT_P001_C_BENEFIT | Differentiation | The detail: metal ring pleats | 1 Macro of the metal ring and pleat fan | 2 Mid-shot of the bodice and mock neck | 3 Full look, walking, pleats moving | The detail that makes it: pleats fanned out from metal ring hardware. #aigenerated | Does calling out the signature detail beat mood and occasion? |

### P003 3D Rose Blazer Mini Dress (variant shown: Black)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P003_A_PRODUCT | Visual attraction | A blazer dress with roses | 1 Model in the dress, plain warm backdrop, roses fully visible | 2 Three-quarter view: puffed shoulders and lapels | 3 Back view of the tailored fit | Black blazer dress with red 3D roses on long green stems. #aigenerated | Is the statement look enough on its own? |
| EC_TT_P003_B_LIFESTYLE | Occasion need | The office party dress | 1 Office holiday party, warm evening light, dress with sheer tights and heels | 2 Toasting with colleagues | 3 Walking out with a clutch | The office holiday party dress: tailored, long-sleeved, roses up front. #aigenerated | Does the office-party setting lift purchase intent? |
| EC_TT_P003_C_BENEFIT | Outfit completion | Blazer and dress in one | 1 Macro of the 3D roses on the black suiting | 2 Lapels, buttons and flap pockets | 3 Full look: no extra layer needed | Blazer and dress in one piece. Nothing else to plan. #aigenerated | Does 'outfit done' beat the look and the occasion? |

### P005 Two-Button Notch Lapel Long Coat (variant shown: Burgundy)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P005_A_PRODUCT | Visual attraction | The long burgundy coat | 1 Full-length coat on a model, studio cream backdrop | 2 Wide notch lapel and brushed texture close-up | 3 Back view: dropped shoulders, below-knee length | Long burgundy coat with wide notch lapels and dropped shoulders. #aigenerated | Does the coat's color and length sell it alone? |
| EC_TT_P005_B_LIFESTYLE | Seasonal relevance | Made for cold-week walks | 1 November city sidewalk, coat open over a cream turtleneck (cost-probe picture) | 2 Crossing the street, coat moving | 3 Arriving at a doorway, hands in pockets | The long coat for November city days, over your favorite knit. #aigenerated | Does a real cold-season setting lift intent? |
| EC_TT_P005_C_BENEFIT | Versatility | Cut roomy to layer | 1 Coat over a cable-knit midi dress and boots | 2 Same coat over jeans and a sweater | 3 Same coat over black trousers for work | Cut roomy and long to layer over knits, dresses and work clothes. #aigenerated | Does the layering benefit beat the look? |

### P006 Stand Collar Chunky Knit Cardigan (variant shown: Off-White)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P006_A_PRODUCT | Visual attraction | Chunky rib, high collar | 1 Model in the off-white cardigan, studio, rib texture filling frame | 2 Stand collar and off-center buttons close-up | 3 Shoulder button tabs detail | Chunky rib knit with a high stand collar and button-tab shoulders. #aigenerated | Does the knit texture alone create interest? |
| EC_TT_P006_B_LIFESTYLE | Seasonal relevance | Your weekend knit | 1 Saturday farmers market, cardigan over jeans | 2 Browsing a bookshop | 3 Walking home, collar up | The cardigan for slow weekends: chunky rib, easy fit. #aigenerated | Does a cozy weekend scene beat the knit on its own? |
| EC_TT_P006_C_BENEFIT | Practical value | Button it up like a jacket | 1 Collar buttoned up, worn as an outer layer outdoors | 2 Worn open over a dress | 3 Full button front close-up | Button the stand collar up and wear it like a jacket. #aigenerated | Does a 'two ways to wear it' benefit beat texture and mood? |

### P007 Notch Lapel Faux Suede Blazer (variant shown: Camel)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P007_A_PRODUCT | Visual attraction | Soft faux suede, notch lapels | 1 Model in the camel blazer, studio, suede texture visible | 2 Yoke seam and lapels close-up | 3 Flap pockets and three-button front | Relaxed faux suede blazer with notch lapels and a yoke seam. #aigenerated | Does the suede look sell itself? |
| EC_TT_P007_B_LIFESTYLE | Identity | Weekend in the city | 1 Late-autumn city street, blazer over a turtleneck and jeans | 2 Window table in a cafe (no mug in hand) | 3 Walking past shop fronts | Faux suede over a turtleneck and jeans: the easy city look. #aigenerated | Does a lifestyle scene lift intent over the product? |
| EC_TT_P007_C_BENEFIT | Outfit completion | Turtleneck + jeans + this | 1 The three pieces shown as an outfit formula | 2 Same blazer over a striped polo sweater | 3 Same blazer with trousers for work | Turtleneck, jeans and this blazer: an outfit in three pieces. #aigenerated | Does an outfit formula beat the look and mood? |

### P009 Fleece-Lined Hooded Zip Jacket (variant shown: Camel)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P009_A_PRODUCT | Visual attraction | Plush-lined hood, utility zip | 1 Model in the camel jacket, studio, hood lining visible | 2 Contrast collar and zip chest pocket close-up | 3 Back view of the relaxed, oversized fit | Utility zip jacket with a plush-lined hood and contrast collar. #aigenerated | Does the utility look sell on its own? |
| EC_TT_P009_B_LIFESTYLE | Practical value | Cold-morning errands | 1 Frosty morning walking a dog in a park, hood down | 2 Loading a grocery bag into a car | 3 Hood up against the wind | The easy top layer for cold mornings and quick errands. #aigenerated | Does an everyday cold-weather moment beat the product shot? |
| EC_TT_P009_C_BENEFIT | Practical value | Lined where it counts | 1 Hood turned out to show the plush lining | 2 Inside front showing the fleece lining | 3 Zipped up over a knit, oversized fit | Plush fleece lining in the hood and body, oversized over your knits. #aigenerated | Does showing the lining (a concrete feature) beat look and mood? |

### P011 Snap Collar Faux Leather Jacket (variant shown: Black)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P011_A_PRODUCT | Visual attraction | Black moto, polished collar | 1 Model in the zipped black jacket, studio | 2 Snap-tab stand collar close-up | 3 Zip pockets and shaped waist seams | Fitted faux leather moto jacket with a snap-tab stand collar. #aigenerated | Does the jacket's look alone create interest? |
| EC_TT_P011_B_LIFESTYLE | Identity | Dinner downtown | 1 Evening street, jacket over a knit dress and knee boots | 2 At a restaurant door | 3 Walking with a friend, city lights | A black moto over your knit dress for dinner downtown. #aigenerated | Does an evening lifestyle scene lift intent? |
| EC_TT_P011_C_BENEFIT | Versatility | One jacket, three outfits | 1 Over a cable-knit midi dress with boots | 2 Over a sweater and jeans | 3 Over a black mini with tights | One black jacket, three outfits: dresses, jeans and minis. #aigenerated | Does showing versatility beat look and mood? |

### P012 Snap Button Fold-Over Knee Boots (variant shown: Beige)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P012_A_PRODUCT | Visual attraction | Fold-over cuff, brass snaps | 1 Boots worn, knees down, studio backdrop, snaps and cuff in focus | 2 Side view of the 2.8 in block heel | 3 The pair standing side by side | Knee-high boots with a fold-over cuff, brass snaps and a block heel. #aigenerated | Do the boots sell on their design? |
| EC_TT_P012_B_LIFESTYLE | Outfit completion | Boots for every dress | 1 Walking in a caramel cable-knit midi dress and the boots | 2 Sitting on a step, slit showing the shaft | 3 Climbing stairs, hem and boots in frame | The knee boots your sweater dresses have been waiting for. #aigenerated | Does a styled outfit moment beat the product shot? |
| EC_TT_P012_C_BENEFIT | Versatility | One pair, three outfits | 1 With a midi knit dress | 2 With a mini skirt and tights | 3 With straight jeans over the shaft | One pair, three outfits: midi dress, mini and jeans. #aigenerated | Does versatility beat the design and the outfit moment? |

### P013 Cable Knit Mock Neck Midi Dress (variant shown: Caramel)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P013_A_PRODUCT | Visual attraction | Cable knit, mock neck, midi | 1 Model in the caramel dress, studio, full length | 2 Cable knit and mock neck close-up | 3 Back view of the fitted shape | Cable knit sweater dress with a mock neck, long sleeves and midi length. #aigenerated | Does the dress sell on its look alone? |
| EC_TT_P013_B_LIFESTYLE | Occasion need | Holiday plans, one dress | 1 Family holiday dinner, warm light, dress with knee boots | 2 Greeting guests at the door | 3 By a window during a toast | One dress for every holiday plan: dinners, visits and photos. #aigenerated | Does a holiday occasion beat the plain look? |
| EC_TT_P013_C_BENEFIT | Outfit completion | The slit makes boots work | 1 Mid-stride, front slit opening over tall boots | 2 Slit and boot shaft close-up | 3 Full look, seated | A front slit that shows off tall boots and keeps you moving. #aigenerated | Does the boots-and-slit benefit beat look and occasion? |

### P014 Striped Polo Collar Knit Sweater (variant shown: Navy & Green Color Block)

| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |
|---|---|---|---|---|---|
| EC_TT_P014_A_PRODUCT | Visual attraction | Stripes with a polo collar | 1 Model in the sweater, studio, stripes and collar fill frame | 2 Open polo collar close-up | 3 Ribbed cuffs and hem | Bold stripes and a soft open polo collar in a relaxed knit. #aigenerated | Does the striped look sell alone? |
| EC_TT_P014_B_LIFESTYLE | Identity | Easy weekend, put-together | 1 Weekend brunch walk, sweater with jeans and loafers | 2 Choosing flowers at a market stall | 3 Laughing on a bench | Stripes and a polo collar: weekend easy, still put-together. #aigenerated | Does a weekend scene lift intent over the product? |
| EC_TT_P014_C_BENEFIT | Versatility | Jeans to skirt to office | 1 With straight jeans | 2 Tucked into a midi skirt | 3 Under a faux suede blazer for work | One sweater, three outfits: jeans, a skirt or under a blazer. #aigenerated | Does versatility beat look and mood? |

## 8. Production plan and cost

- **Cost probe (2026-10-28):** one 9:16 coat picture via Higgsfield `marketing-studio/image/flare` (3 product
  references, quality high): 752×1344 (meets 720×1280), 30 s, passed first-filter checks (product match, anatomy,
  November setting). Higgsfield prices flare per token ($30 per 1M image-output tokens, $8 per 1M image-input
  tokens, $5 per 1M text tokens) and reports no per-request cost or balance through the API; the connected
  Higgsfield app balance (0.82 credits) did not change, so the API key bills a separate account. **Estimated
  ≈ $0.20–0.30 per picture** (unverified: the real charge is visible only in the Higgsfield console).
- **Phase C (30 hero prototypes):** ≈ $6–9 plus remakes (budget ~$15). **Phase E (60 more slides for approved
  concepts):** ≈ $12–18. Text overlays are added locally (no generation cost).
- **Slide system (all concepts):** 9:16, 1080×1920 export (upscaled from ~752×1344 with a check for softness) or
  native size if upscaling softens detail; Georgia headline in cream (#F4E9DA) or ink (#2B2522), ≤ 6 words, inside
  the upper-middle safe zone (TikTok UI covers the bottom ~20% and the right edge); no prices, dates, urgency or
  claims beyond the product page (brand guide p.5).
