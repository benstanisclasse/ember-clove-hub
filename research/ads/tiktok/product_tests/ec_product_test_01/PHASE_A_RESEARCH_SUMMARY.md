# TikTok image-ad test 01 — Phase A: inspection and research

Date: 2026-10-28. Brief: owner's "Ember & Clove — TikTok Product Advertising System, Phase 1" master prompt.
Status: **Phase A done.** Owner decisions received 2026-10-28 (P002/P004/P008/P010 swapped for P011–P014; see PHASE_B_EXPERIMENT_PLAN.md). Nothing generated, published, spent or edited
on the store. Product snapshot (live Shopify + economics): `products.json` in this folder.

Selection used: the 10 products with the most profit left after a $20 CPA (owner's question earlier on 2026-10-28;
there was no saved "selected ten" list in the Hub).

## 1. Verdict in one table

| ID | Product | Price | Break-even CPA | Kept at $20 CPA | Season fit (Nov) | Listing state | Phase A verdict |
|---|---|---|---|---|---|---|---|
| P001 | Mock Neck Side-Pleat Mini Dress | $170.16 | $69.49 | $49.49 | Holiday party; sleeveless | Clean | Test (holiday pair) |
| P002 | Rhinestone halter mini dress | $123.18 | $50.96 | $30.96 | Holiday/NYE | **Raw supplier listing; owner hold 10-26 (designer look-alike, monogram bag in photos)** | **Do not advertise** |
| P003 | 3D Rose Blazer Mini Dress | $122.32 | $50.59 | $30.59 | Holiday/office party | Clean; supplier watermark in a photo | Test (holiday pair) |
| P004 | Metal Toe Cap Wedge Mules | $113.68 | $48.24 | $28.24 | **Off-season** (backless; sandals bottom out Nov–Dec) | Clean; handle says "genuine leather" (it's faux) | Hold for spring |
| P005 | Two-Button Notch Lapel Long Coat | $100.04 | $40.54 | $20.54 | **Strong** (long coats peak Nov–Dec) | Clean; no on-model photos | Test (priority) |
| P006 | Stand Collar Chunky Knit Cardigan | $62.56 | $33.72 | $13.72 | Strong | Clean; brand label in some photos; Camel/Brown photo mismatch | Test (priority) |
| P007 | Notch Lapel Faux Suede Blazer | $60.90 | $33.71 | $13.71 | Good | Clean; on-model photos look like a creator's own posts | Test (flats/AI only) |
| P008 | Retro Character Graphic Sweatshirt | $63.54 | $33.71 | $13.71 | Good category | **Raw listing, titled "Men's"; owner said 10-26 "skip the men's items"** | **Do not advertise** |
| P009 | Fleece-Lined Hooded Zip Jacket | $66.30 | $33.53 | $13.53 | Strong | Clean; men's cut (bust 43–57 in); "LITB" watermark on variant images | Test after fit check |
| P010 | Floral Satin Blazer Mini Set | $61.46 | $32.67 | $12.67 | **Off-season** (pastel satin, sets peak May–Jun) | Clean; bottom is a skort | Hold for spring |

All 10: ACTIVE, every variant available, pages return 200 in ~0.3 s on mobile, show "Free shipping over $70" and the
7-day return window. Economics are estimates (shipping fitted from weight for most; max-cost variant; 2.9% + $0.30
fees; 5% refunds). Break-even ROAS 2.0–2.5. No product loses money at $20; at $30 CPA, P006–P010 keep ~$3.

**Proposed in-season replacements** for P002, P004, P008, P010 (kept after $20 CPA): Snap Collar Faux Leather Jacket
($11.50), Snap Button Fold-Over Knee Boots ($9.90; boots rise Nov–Dec), Cable Knit Mock Neck Midi Dress ($10.25; has an
ICP report), Striped Polo Collar Knit Sweater ($10.48); also Turtleneck Rib Knit Sweater Dress (has an ICP report).
Lower profit per sale, but in season and clean.

## 2. Research findings that apply to image ads (all observational: hypotheses, not rules)

- **No research we hold studies static image ads.** The Kalodata video study excluded photo posts; TikTok Top Ads
  are all video. Everything below is transferred from video or from general attention research.
- **Paid delivery beats any creative feature** (strong; the only video-study result surviving correction).
- **Garment on a body, clearly visible in the first card** (weak–moderate). "Person at 0 s" did not survive correction.
- **Detail close-ups as proof** (weak; 76% vs 65%, not significant). Suits Ad C.
- **Short key-word text helps silent viewing** (B, TV/lab studies). In a carousel the only verbal channel is the ad
  text and any on-image text — see decision D3.
- **Face looking at the product steers attention to it** (B, eye-tracking). Transfers well to stills.
- **AI imagery is a trust risk**: Womenswear is the weakest AI-video category (0 of 61 AI videos made $1K in Sep);
  a survey found 53% less likely to buy from brands using AI in social content. The top complaint on a comparable
  dropship dress is "looks different from the photos" (17 mentions). Pictures must match the garment exactly.
- **Price gap**: our prices are 1.2–5× TikTok Shop analogs (e.g. long coats median $42.50 vs our $100; cardigans $29
  vs $62.56; dresses top-500 median $29, none ≥ $100) and price can't appear in ads (owner rule), so the price shock
  lands on the product page. Expect high click-to-purchase drop-off; it is the main commercial risk of the test.
- **Season** (one observed year): coats, hoodies/sweatshirts, cardigans and boots rise into Nov–Dec; sandals and
  sets bottom out. Holiday-party angles need orders by about Nov 15–20 given 2–3 week delivery (not statable in ads).
- **Meta Ad Library**: boutiques run cardigan benefit headlines and occasion single-images; frequency only (no US
  spend data), not performance evidence.
- **No ICP report exists for any of the 10** (only P01 cable-knit midi and P02 turtleneck dress have one). Owner rule:
  run the ICP master prompt per product before final angles — see decision D4.

Full per-product briefs (motivations, objections, competitors, three candidate angles, evidence level):
`CREATIVE_RESEARCH_BRIEFS.md` in this folder.

## 3. Infrastructure checked

- **Shopify**: Hub connector works (read). `read_publications` scope is missing (can't confirm sales-channel
  publication via API; storefront pages load, so they are published online).
- **TikTok Ads account** XXX "DeskConnect IT LLC_adv": STATUS_ENABLE, US, USD, balance $0
  (payment method not checked). No campaign has ever spent; "EC | Sales | Test C1" is an unpublished draft.
- **TikTok pixel** XXX (Shopify partner integration, active, advanced matching on): ViewContent,
  AddToCart, InitiateCheckout, AddPaymentInfo, PlaceOrder/CompletePayment ("SHOPPING"), Search, PageView,
  LandingPageView. Zero purchase history, so purchase optimisation starts cold. Earlier TikTok ad preview clicks
  reached the store with an unfilled `__CAMPAIGN_NAME__` macro (dashboard tag issue) — use fixed UTMs per ad.
- **Image pipeline**: `scripts/hf_image_batch.py` (Higgsfield `marketing-studio/image/flare`, up to 16 reference
  images, aspect ratio per job, 1k). 3:4 outputs are 880×1168; 9:16 at 1k should be ~768×1365 (≥ 720×1280; verify on
  the first image). Every job is recorded in studio.db. **Higgsfield does not report a cost per image**, and the
  connected Higgsfield app shows 0.82 credits on the free plan (the API key may bill a different balance). Cost per
  prototype is unknown until checked — see decision D6.
- **Dashboard**: ads refresh (Meta + TikTok, every 3 h), attribution by utm_content, profit engine with per-product
  break-even CPA. The "Creative Testing Lab" waits for the campaign (owner, 2026-10-28: build the Tests page once
  TikTok is published); experiments.csv / decide.py exist but have never held data.
- **Store trust**: the Contact policy lists XXX (a different business name). Returns:
  7 days, buyer pays return shipping. Both are conversion and ad-review risks worth fixing (owner's call).

## 4. TikTok image-ad requirements (checked 2026-10-28, official TikTok help/API pages)

- **Format: Standard Carousel is the only image ad on the TikTok placement.** Single-image ads run only on Pangle /
  Global App Bundle. Carousels work with the Sales (web) objective. Source: ads.tiktok.com/help/article/carousel-ads (Sep 2026).
- **Must run as a Spark Ad from our TikTok account.** Since Jan 2026 new ad accounts can't use a custom identity on
  the TikTok placement. Spark Ads Push: we upload the images and they post under @emberandclove (identity
  BC_AUTH_TT in hub.json), with an "ads only" option that keeps them off the public profile.
- **Specs:** 2–35 images (up to 20 shown); 9:16 at 720×1280 recommended (API max 1242×2340, JPG/PNG, < 50 MB; help
  page suggests ≤ 100 KB — conflicting); **music is required** (Commercial Music Library or our own upload); one
  caption (**100 characters max**, Spark Push), one CTA, one URL per carousel; display name must match the landing
  page brand. Same ratio for every image: not documented (keep all 9:16).
- **AI disclosure:** AI-generated or significantly edited images must be disclosed or the ad is rejected/restricted.
  The Ads Manager AI toggle works only for non-Spark ads, so ours would need the creator AI label on the Spark post
  or our own caption/on-image disclaimer. Note: TikTok already flagged one of our organic AI videos under
  "Edited Media and AIGC" (log 10-27), so AI people on @emberandclove carry an account risk.
- **Policy:** price/promo must match the landing page; no fake UI, before/after or "No. 1" claims; ads must show the
  product the page sells, as it looks; After-Conversion policy requires delivery as promised and clear refunds
  (violations can suspend the account). Review usually within 24 h.
- **Budget mechanics:** ad group minimum **$20/day**, campaign minimum $50/day. Campaign Budget Optimization moves
  spend to predicted winners (uneven product exposure); ad-group budgets keep it even. Split Test compares only two
  groups, needs ≥ 7 days, and doesn't run with CBO. Learning settles after ~25 results or 7 days. TikTok suggests
  ~10× CPA per ad group for purchase goals.
  **Consequence:** 10 products in separate ad groups = at least $200/day ($1,400/week) before any result; 30 ads
  can't each get readable delivery at a small budget.
- **API:** carousel drafts can be created disabled via `smart_plus/ad/create` (the old `/ad/create/` stops creating
  manual Sales campaigns on 2027-01-01). Manual and Smart+ are now one "Upgraded Smart+" flow, possibly not yet live
  in our account.

## 5. Decisions needed before Phase B

- **D1 Product list.** Drop P002 (IP hold) and P008 (men's), hold P004 and P010 for spring, and replace them with
  in-season products (section 1)? Or keep the list as is?
- **D2 Listing fixes** (needs owner OK): P009 men's-cut check; watermark/brand-label photos (P003, P006, P009) kept off
  ads; contact email; optionally clean titles. No changes made.
- **D3 On-image text.** Standing rule: no custom overlays/edits (in question; text hooks were 74% of video winners vs
  60%, p≈0.07). Options: (a) no text on images, copy only in the ad text; (b) text as one test arm only.
- **D4 ICP research.** Run the owner's ICP master prompt for each product before Phase B angles (10 reports, ~2
  sessions of work, no paid calls), or use the research briefs as a lighter substitute for this test.
- **D5 Budget reality.** With no purchase history and break-even CPAs of $33–69, even ~5 purchases per product needs
  roughly $150–350 per product. 30 ads × 10 products is not readable at a small budget; Phase B will propose a staged
  design (product screening first, creative test only on survivors) and a budget for the owner to set.
- **D6 Generation spend.** Approve checking the real cost of one 9:16 prototype, then a cap for 30 prototypes.
- **D7 AI imagery.** Lifestyle/model images would be AI-generated (most supplier photos have rights or watermark
  issues). Confirm the owner accepts AI people in paid Spark ads on @emberandclove, labelled as AI on each post, given
  the trust risk and the earlier AIGC flag.
- **D8 Music.** Carousels require music: TikTok Commercial Music Library track (licensed for ads) — pick per ad or
  one track for all (keeps it constant across A/B/C).
