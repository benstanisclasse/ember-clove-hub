# Meta Ad Library scan — women's clothing, US, active ads (2026-10-27)

> **Correction (2026-10-28, Market Engine Phase A audits).**
>
> - US commercial ads in the Meta Ad Library show **no impressions, spend or results**. Run time, ad count and the
>   low-impression flag are the only signals; "current winners" or "spend signal" are inferences, not observations
>   (docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md).


Owner request: "Research: search Meta's Ad Library to see what ads other clothing stores are running right now."
Tool: Meta Ads connector `ads_library_search` (active ads, US). It returns page name, headline/link title, start time and a
snapshot link only — no ad images, body text, spend or results. Open the snapshot links to see the creative.

Searches (estimated active matches): "sweater dress" 7,798 · "cozy knit" 9,901 · "women's fall outfits" 17,722 ·
"boutique new arrivals cardigan" 93 · "follow us for outfit ideas" 1,127 (mostly not clothing). Broad searches also pull
in unrelated ads (dating, drama apps, supplements).

## What clothing stores are running
1. **Live-sale ads (small boutiques)**: "Live Sale!" (Char Lee, Ellie Clothing), "We're LIVE and the outfits are 🔥!"
   (Mainstream Boutique Omaha), "Live @ Five: All New Fall Arrivals!" (Mainstream Boutique Morgan Hill),
   "Live Sale with Lisa!" (Just Lovelee). Ads that push people into a Facebook Live try-on/shopping stream.
2. **Multi-product / catalog carousels**: headlines are lists of product names — Dahlia's Downtown Boutique (cable knit
   zip cardigan, ribbed sweater, mauve sweater, leopard sweater), IdPearl Boutique (cardigans, cable vest, cashmere),
   Wildfire Hygge (jacket, cardigan), Festève (holiday dresses with prices).
3. **Occasion hooks**: "sweater dresses for thanksgiving dinner" (Cart Ritual), holiday/Christmas shop ads already live.
4. **Feeling/benefit headlines**: "Cozy From Every Angle", "Fall's Coziest Pair Of Boots" (Nurestia), "Cozy Without The
   Bulk", "The Only Long Sleeve Worth Wearing" (Cuts), "The Knit Top Is Back" (Anna Kayte's), "Fall Looks Good on You"
   (TravisMathew Women's), "The New Is Here" (The Rowe), "Your New Favorite Boutique" (Whilden).
5. **Discounts and urgency** (common, but off-limits for us: no prices/urgency): "15% Off with Code" (Urban Revivo),
   "Buy 2, Get 1 Free Ends Soon!" (Venaroco), "Early Fall Sale Ends Soon" (Madison Lane), "Back In Stock" (vici).
6. **Local angle**: "Made in Minnesota" (Pine Kids Co, several ads) — locality used as the hook.

Almost no clothing store ads ask for Page follows; nearly all send people to products, a sale or a live stream.

## Fits for Ember & Clove (within our rules: no price, delivery, urgency, fake reviews)
- Occasion headlines for the next 4 weeks: "Sweater dresses for Thanksgiving dinner", "What to wear to Friendsgiving",
  "Office holiday party, sorted". Turtleneck sweater dress and cable-knit midi dress fit.
- Short cozy/benefit headlines like the ones above instead of a generic "Ember & Clove" headline.
- A catalog carousel of 4–6 knits/coats (catalog already connected) for a store-visit campaign after Test F2.
- Minneapolis/Minnesota weather angle (Ember's world) as a local hook — no "made in" claims (products aren't).
- Live selling is the boutiques' main format; not a fit while there is no person on camera (Ember is AI).

## Example snapshot links
- Cart Ritual, sweater dresses for Thanksgiving: https://www.facebook.com/ads/library/?id=2251472722064093
- Nurestia, "Cozy From Every Angle": https://www.facebook.com/ads/library/?id=29316677711258577
- Dahlia's Downtown Boutique, cardigan carousel: https://www.facebook.com/ads/library/?id=2351416272339658
- IdPearl Boutique, fall arrivals carousel: https://www.facebook.com/ads/library/?id=1418067733270037
- Mainstream Boutique Omaha, live sale: https://www.facebook.com/ads/library/?id=1812828756588864
- Cuts, "The Only Long Sleeve Worth Wearing": https://www.facebook.com/ads/library/?id=1869360707391712
