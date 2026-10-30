# PRODUCT OPPORTUNITY DISCOVERY REPORT — OCTOBER 2026

Written 2026-10-30 (ET). Code: `scripts/opportunity_discovery.py` (`backtest`, `screen`, `outputs`). Pre-registration:
`PREREGISTRATION.json`, committed in e0769bd **before** any result was computed. Every number here comes from
Ember & Clove's saved data. Nothing was bought, published or spent.

**Integrity notes**
- Kalodata was read only (sqlite `mode=ro`). No downloads and no credits used.
- CJ was used only for free read-only searches, variants and freight. No orders, sourcing requests or product links.
- No product, ad or budget was changed.

## 1. Answer first

| # | Product (TikTok reference) | Evidence tier | Price | Contribution* | Break-even CAC | Biggest unknown |
|---|---|---|---|---|---|---|
| 1 | **April Satin Pant**: high-waist satin wide-leg pant | **Strongest. Clears every gate we can check from here.** | $61.36 | $37.26 | $37.26 (ROAS 1.65) | Sample quality (acetate satin), black variant, size chart |
| 2 | **Chunky lug-sole penny loafer**, generic version of "Clarks Westlynn Ayla" | Strong market, photo-matched; IP condition | $65.63 ($45.94 generic) | $42.22 ($24.09 generic) | $24 at generic price | Our generic price, shoe fit and returns, no Clarks name or photos |
| 3 | **Travel hoodie with eye-mask hood**, generic version of "Comfrt VIP Airplane Mode" | Strong new demand, concept-matched only | $62.56 ($43.79 generic) | $33.93 ($16.65 generic) | $17 at generic price | The CJ item is a pullover, not a zip-up; check for a design patent on the hood |
| 4 | **One-shoulder satin high-split maxi dress** (OYS) | Photo-matched, holiday party demand; thin margin | $44.82 | $18.65 | $18.65 (ROAS 2.40) | Needs ~5.4% click-to-buy at $1 CPC just to break even |
| 5 | **Bold cat-eye sunglasses** (WMP Astra style) | Stable demand, best unit margin; partial photo match | $45.42 | $34.80 | $34.80 (ROAS 1.31) | CJ frame is a sharper cat-eye in a lighter tortoise; winter season |

\*Contribution is the pre-registered formula at the TikTok September unit price, using CJ costs saved on 2026-10-29:
price − CJ cost − CJ freight − (2.9% + $0.30) − 5% refund reserve. It is before ad spend.

**Only #1 is a clean controlled-test candidate today, and only after a sample arrives.**
- #2 and #3 work only as unbranded generics, priced lower than the brand.
- #4 has demand and a verified supplier, but its margin leaves almost no room for ad cost.
- #5 is a partial photo match.
- The barbed wire choker (contribution $53.34 at the $70.31 reference price) is not counted here because it is already
  in a test. Round 2 is drafted, unpublished. Its results are the next real evidence.

**Why these five beat the higher-ranked products.** Of the top 50 by market evidence alone:
- **No supplier.** 32 have no checked supplier, or CJ has no matching item. Live CJ checks found nothing for the
  Everyday Cloud tote, Cefiro envelope bag, Angel Kiss hobo, Cider tulle dress and Songling sherpa.
- **Intimates or claims.** 8 are intimates or claims-heavy (sticky bras, shapewear, push-up bras): returns, hygiene and
  ad-policy risk.
- **Rejected.** 4 are rejected:
  - Dream Pairs Mary Janes and PU low-heel boots lose money at the TikTok price with CJ costs.
  - The CurvySweet gown and Ettika studs failed the photo check.
- **Also rejected below the top 50.** HEYDUDE, Crocs fur clogs, the FDR embroidered hoodie, Magic ONESO jeans and the
  Chouyatou coat failed either the photo check or the economics. The combat boots had 0 stock.

The five above are the only products where market demand, a supplier photo check, and positive economics with room for
ad cost all exist together.

**What must be verified before risking ad money** (section 8 has details):
1. Order and inspect a sample of the exact variant.
2. Re-pull the current CJ price, freight and stock. The 2026-10-29 quotes are historical.
3. Confirm the generic designs don't copy a brand (#2, #3, #5), and use no brand names or brand photos.
4. Set our selling price, and recompute the break-even CAC at that price.
5. Get a real conversion rate. Round 1 has spent about $290 with 0 purchases, so our own click-to-purchase rate is 0 so
   far. The five candidates need roughly 2.7–6.0% click-to-purchase at $1/click just to break even.

## 2. Database audit

| Source | What exists | Limits that matter |
|---|---|---|
| Kalodata point-in-time panel (`pit_2026-09_v1/panel.parquet`) | 232,467 product-month rows, Nov 2025 – Sep 2026: top 500 per category, risers 1–200, deep risers 201–1,000 (Sep only) | Top-500 lists are complete, so absence from a list means "below 500th", never zero sales. The AI-content flag is unknown before June. Current-value fields are never used as features. |
| Per-product videos | 120 eligible-month products, Sep 2026 only | Too few, and too late, to backtest strategies C or D |
| Top videos | Video rows without product_id | Can't be joined to products |
| product_details / comment_insights | ~84 / 24 products per month | Too sparse for features |
| Product images | None in Kalodata | Read live from TikTok's og:image for the photo checks |
| CJ saved quotes (`data/kalo_cj/picking_sheet_2026-10-29.csv`) | 50 products (47 eligible), cost, freight, stock, sizes | A historical snapshot from 2026-10-29. US stock is 0 for all, so everything ships from China (5–11 days). CJ reviews are mostly 0. |
| Co-purchase / bundle data | None | Strategy F can only be described, not tested |
| Ad cost per product | None | We use our own round-1 CPC (~$0.96–$1.07 on the best ads) |
| Return rates | None | A flat 5% refund reserve, 10% in the sensitivity test |

The previous model scores (model_v2) are rankings, not probabilities. The reliability check showed they overpredict. No
number in this report is a calibrated probability of success.

## 3. Historical validation (pre-registered)

**Outcome.** S3_sustained: a product listed at month t is in a category top 500 in at least 2 of months t+1..t+3.

**Setup.**
- Test months: 2026-03 to 2026-06.
- Models are retrained on a rolling, expanding window with a 3-month embargo.
- Base rate is about 40% of listed products.
- 95% intervals come from a month-block bootstrap.

| Ranker | p@10 | p@50 | p_cat@10 | p@10 in store-fit categories | p_cat@10 vs B3 consistency (95% CI) |
|---|---|---|---|---|---|
| B1 sales | 0.85 | 0.88 | 0.88 | 1.00 | −0.055 to −0.029 (worse) |
| B2 growth | 0.40 | 0.44 | 0.61 | 0.48 | −0.34 to −0.29 (worse, no better than chance) |
| **B3 consistency** (months listed) | 0.88 | 0.92 | **0.93** | 1.00 | the best baseline |
| A emerging | 0.63 | 0.63 | 0.73 | 0.58 | −0.22 to −0.18 (worse) |
| B underserved | 0.53 | 0.48 | 0.81 | 0.95 | −0.14 to −0.08 (worse) |
| M4 logistic (18 model_v2 features) | 0.95 | 0.94 | 0.93 | 0.93 | −0.012 to +0.020 (**no difference**) |
| M5 equal-weight composite | 0.88 | 0.92 | 0.93 | 0.95 | −0.005 to +0.012 (no difference) |

**What this means**
- For lasting demand, products that are already selling and keep selling (incumbency) are the signal. Our model is no
  better than simply counting months on the list.
- Ranking by growth is close to useless for this outcome. Chasing the fastest risers mostly picks spikes.
- **Exploratory, not pre-registered** (same test months, so treat it as a lead, not a result): inside the risers that
  were not in a top 500, M4 hit 35% at p@20 against a 2.3% base rate. B3 hit 22.5% and growth 7.5%. In ranks 201–500,
  M4 also led (p@50 0.86 vs 0.80). Because of this, M4 is used as the growth component of the score. That choice was
  made after seeing these results.
- Strategies C (repeatable video), D (organic vs paid), E (margin) and F (bundles) **could not be backtested**. The data
  exists for one month only, or not at all.

## 4. The six strategies, September 2026 screen

**Universe.**
- 19,172 listed products in September.
- 7,391 are in our five store-fit categories: Womenswear, Shoes, Fashion Accessories, Jewelry, Luggage & Bags.
- **2,239 are eligible:** price $15–$120 and September revenue ≥ $5k.

Files are `strategy_*.csv`.

- **A — Emerging.** 868 eligible products are "emerging" (newly listed) and 157 are "accelerating". The backtest says
  growth alone doesn't predict lasting demand, so emerging products enter the score through M4, not raw growth. The
  model's top emerging store-fit products are mostly branded or have no CJ data: BOSTANTEN handbag, Miusse luggage set,
  LOVEVOOK totes, Yeokou velvet blouse and 2-pack fleece-lined sweatpants (`strategy_A_emerging_model.csv`).
- **B — Underserved categories.** Jun→Sep growth in top-500 revenue:

  | Category | Growth | Seller concentration (HHI) |
  |---|---|---|
  | Jewelry | ×1.23 | 0.094, the most concentrated of the five |
  | Shoes | ×1.19 | 0.048 |
  | Womenswear | ×1.05 | 0.011, the most fragmented: easiest to enter, but crowded |
  | Fashion Accessories | ×0.98 | — |
  | Luggage | ×0.96 | — |

  The "underserved" ranker did worse than incumbency in the backtest, so category growth is context, not a selector.
- **C — Repeatable video.** Only 20 store-fit products have creator data. The broadest creator bases (many creators, no
  single one dominant) are:
  - Wetkiss knee-high cowboy boots: 151 creators, top creator 13% of sales.
  - Cider knit maxi dress: 110 creators, top creator 15%.
  - CurvySweet Athena gown: 142 creators, 19%.
  - Double-sided fleece robe: 165 creators, 19%.

  Wide creator bases suggest the sale doesn't depend on one viral video. Wetkiss and Cider have no CJ match checked yet.
- **D — Organic vs paid.** Of 91 products with video data, only 8 sell mainly organically (ads under 50% of revenue).
  None of those is a store-fit candidate we could source. For store-fit products, 73–99% of video revenue is
  ad-boosted. **Assume every test is a paid test.**
- **E — High margin.**
  - 47 eligible products have saved CJ quotes.
  - 4 have negative contribution: Dream Pairs Mary Janes, PU low-heel boots, Magic ONESO jeans and the Chouyatou coat.
  - The highest contributions belong to the products in section 1 plus the Crocs/HEYDUDE items. Those failed the photo
    check or carry brand IP.
- **F — Bundles.** 15.3% of eligible products have bundle words (pack, set, pcs). They have lower median revenue ($23k vs
  $35k) and lower price ($29.8 vs $37.1). There is no co-purchase data, so **there is no evidence that bundles do
  better**. Not pursued.

## 5. Scoring

The weights were fixed in advance: demand 15, growth 20, creative 20, profitability 25, competition 10, fulfillment 10.

- **Market score** reweights the four market components (demand, growth, creative, competition), because those exist for
  every product.
- **Commercial score** adds profitability and fulfillment. It is given only where supplier economics exist.
- Missing data is never scored as bad.

**Limits of the components**
- The creative component barely separates products: video share of sales is about 99% for almost everyone.
- Competition uses seller share of category and category HHI.

**Changes made after seeing results.** These are disclosed, and the unfiltered files are kept.
1. Wig/hair (326 eligible) and men's items (110) are excluded from the commercial ranking, because they aren't our range.
   They had crowded the top. The unfiltered ranking is `screen_eligible_scored.csv`.
2. M4 was chosen for the growth component after the exploratory segment results (section 3).
3. The action rules and the brand list for IP flags (`BRANDS` in the script) were written after looking at candidates.
   The pre-registered "brand in name" flag was too broad: 1,472 of 2,239 products. It is reported but not used to reject.
4. The sensitivity scenarios follow the brief. They are not pre-registered.

## 6. Top 50 (`top50.csv`; full filtered ranking `ranking_full_filtered.csv`, 1,803 products)

Recommendations in the top 50:

| Recommendation | Count |
|---|---|
| Test (controlled, after sample) | 1 |
| Investigate (photo + sample) | 5 |
| Investigate (supplier) | 32 |
| Monitor (intimates / claims) | 8 |
| Reject | 4 |

Every row has: revenue, growth, trend, video evidence, competition, M4 rank score, supplier status, economics, market
and commercial score, confidence, main risk and recommendation.

**Top 20 by market evidence.** M4 is a ranking score, not a probability. "Growth" is change from August.

| Rank | Product | Category | Price | Sep revenue | Growth | Supplier | Main risk | Action |
|---|---|---|---|---|---|---|---|---|
| 1 | April Satin Pant | Womenswear | $61 | $425k | +2% (stable) | CJ photo match | ad competition | Test after sample |
| 2 | Eleplus 3-pack wireless bras | Womenswear | $30 | $459k | +44% | not checked | intimates, sizing | Investigate |
| 3 | Everyday Cloud quilted tote | Bags | $33 | $115k | +173% | CJ: no match | needs another source | Investigate |
| 4 | PUFF sticky bra | Womenswear | $22 | $536k | +14% | — | claims/intimate | Monitor |
| 5 | INLYRIC plunge bra | Womenswear | $28 | $391k | +21% | not checked | intimates, sizing | Investigate |
| 6 | Luggage connector straps 2-pack | Bags | $22 | $72k | +2% | not checked | low price | Investigate |
| 7 | naom tank top | Womenswear | $23 | $277k | −13% | CJ saved, photo not checked | $10 contribution | Investigate |
| 8 | CozyLoucia quilted puffer tote | Bags | $26 | $83k | −49% | not checked | falling | Investigate |
| 9 | BOOMBA sticky inserts | Womenswear | $39 | $476k | −13% | — | patented | Investigate |
| 10 | Angel Kiss retro crossbody | Bags | $37 | $174k | +13% | not checked | — | Investigate |
| 11 | CurvySweet Athena knit gown | Womenswear | $60 | $398k | +50% | CJ photo **no** | — | Reject |
| 12 | Shewin oversized knit sweater | Womenswear | $21 | $322k | +5% | CJ saved, not checked | $5 contribution | Investigate |
| 13 | GORISGARMO LED-mirror cosmetic bag | Bags | $28 | $173k | +1% | not checked | — | Investigate |
| 14 | INNERSY cotton panties 5-pack | Womenswear | $19 | $256k | +10% | not checked | intimates | Investigate |
| 15 | Dream Pairs platform Mary Janes | Shoes | $35 | $290k | +50% | CJ saved | **−$1.84 contribution** | Reject |
| 16 | Angel Kiss faux-leather hobo | Bags | $41 | $65k | +83% | CJ: no match | — | Investigate |
| 17 | AnotherChill micro mini skort | Womenswear | $31 | $146k | −37% | not checked | falling | Investigate |
| 18 | Angel Kiss soft PU crossbody | Bags | $40 | $99k | +494% | not checked | spike? | Investigate |
| 19 | CRZ YOGA scrunch leggings | Womenswear | $32 | $232k | +79% | not checked | brand, body claims | Investigate |
| 20 | Curveshe lace-up thong bodysuit | Womenswear | $40 | $190k | +28% | not checked | intimates | Investigate |

**What the top 20 shows.** The highest market evidence sits with products we can't yet source or shouldn't sell:
intimates, patented items, and bags with no CJ equivalent. That is why market rank alone is not a buy signal. Of the
five candidates, only the April Satin Pant is in the top 20. The others rank lower on market evidence:

| Candidate | Market rank |
|---|---|
| OYS satin dress | 58 |
| Penny loafer | 118 |
| Barbed wire choker | 188 |
| Cat-eye sunglasses | 363 |
| Eye-mask hoodie | 385 |

The eye-mask hoodie ranks low only because it is new: there is no August row, so the history-based components have
little to work with.

## 7. Supplier validation (`supplier_validation.csv`, `live_cj_verdicts.json`)

**Method.**
- Compare the TikTok main image with the CJ main images.
- Check that the variant exists: colour and size range (`sizes_ok`).
- Compute freight to the US with CJ's cheapest tracked method.

**Live checks on 2026-10-30.** Eight products were checked:

| Verdict | Products |
|---|---|
| Match | OYS satin dress |
| Partial | Dream Pairs bow flats (EU 36–40 only, $6.47 contribution) |
| Partial, rejected | CELNEPHO combat boots (0 stock in every size, implausible weight) |
| No match (5) | Everyday Cloud tote, Cefiro envelope bag, Angel Kiss hobo, Cider tulle dress, Songling sherpa |

**Next 10 to send to supplier validation.** These are the highest-ranked products without a verified supplier. Intimates,
claims-heavy, patented and falling products are excluded.

| Rank | Product | What's needed |
|---|---|---|
| 3 | Everyday Cloud quilted tote (+173%) | CJ has no match. A CJ sourcing request (a CJ action, owner OK first) or another supplier. |
| 10 | Angel Kiss retro crossbody | CJ search + photo check |
| 13 | GORISGARMO LED-mirror cosmetic bag | CJ search + photo check |
| 18 | Angel Kiss soft PU crossbody (+494%, could be a spike) | CJ search; recheck the trend next month |
| 24 | Cefiro-style envelope bag ($68, +60%) | CJ has no match: sourcing request or another supplier |
| 30 | Cider-style bow ballet Mary Jane flats (+99%) | CJ search; check US sizes (the Dream Pairs match was EU only) |
| 31 | Lefame-style garment duffle | CJ search + photo check |
| 32 | FDR-style big-hood zip hoodie (+42%) | Saved CJ CJWY2423586 ($21.90 contribution) still needs its photo check. The same SKU failed for the embroidered FDR hoodie. |
| 34 | TOLACCEA-style expandable travel backpack ($76) | CJ search + photo check |
| 37 | Satin two-piece wedding-guest gown ($104) | CJ search; high price leaves room for ad cost |

Also, before the C-strategy leads can be used:
- Wetkiss-style knee-high cowboy boots (151 creators) need a CJ search.
- Cider-style knit A-line maxi dress (110 creators) needs a CJ search.

## 8. Economics and sensitivity for the candidates (`sensitivity.csv`)

**How to read it.** Each column changes one input. "All adverse" applies all four changes together: freight +25%,
price −15%, refunds 10%, CJ cost +20%. Values are contribution per order before ads.

| Product | Base | Freight +25% | Price −15% | Refunds 10% | Cost +20% | Generic price −30% | All adverse |
|---|---|---|---|---|---|---|---|
| April Satin Pant | $37.3 | $34.9 | $28.8 | $34.2 | $35.4 | $20.3 | $21.9 |
| Penny loafer (Clarks-style) | $42.2 | $39.4 | $33.2 | $38.9 | $40.9 | $24.1 | $26.2 |
| Eye-mask travel hoodie (Comfrt-style) | $33.9 | $31.4 | $25.3 | $30.8 | $31.2 | $16.6 | $17.5 |
| OYS one-shoulder satin dress | $18.7 | $16.3 | $12.5 | $16.4 | $16.1 | $6.3 | $5.6 |
| Cat-eye sunglasses (WMP-style) | $34.8 | $33.5 | $28.5 | $32.5 | $34.5 | $22.2 | $25.0 |
| Barbed wire choker (in test) | $53.3 | $52.1 | $43.6 | $49.8 | $52.1 | $33.9 | $38.2 |
| Comfrt-style plain hoodie (partial) | $24.7 | $21.8 | $18.2 | $22.3 | $23.3 | $11.7 | $12.0 |
| Dream Pairs-style bow flats (partial) | $6.5 | $3.6 | $2.5 | $5.0 | $4.8 | −$1.5 | −$3.3 |

**The conversion rate each one needs.** This uses a $1.00 cost per click, round 1's best ads. Break-even CAC = contribution.
Target CAC keeps 20% of the price as profit.

| Product | Price used | Break-even CAC | Click-to-purchase needed to break even | Needed to hit target | All adverse: needed to break even |
|---|---|---|---|---|---|
| April Satin Pant | $61.36 | $37.26 | 2.7% | 4.0% | 4.6% |
| Penny loafer at generic $45.94 | $45.94 | $24.09 | 4.2% | 6.7% | — |
| Eye-mask hoodie at generic $43.79 | $43.79 | $16.65 | 6.0% | 12.7% | — |
| OYS satin dress | $44.82 | $18.65 | 5.4% | 10.3% | 17.8% |
| Cat-eye sunglasses | $45.42 | $34.80 | 2.9% | 3.9% | 4.0% |
| Barbed wire choker (reference price) | $70.31 | $53.34 | 1.9% | 2.5% | 2.6% |

**Reading this.**
- The April Satin Pant and the sunglasses stay positive in every scenario, and need the lowest conversion rates.
- The OYS dress fails the target in the adverse case. It only makes sense at a higher price than TikTok's $44.82, or at
  much cheaper clicks.
- The hoodie and the loafer depend heavily on the generic price we set.

**Assumptions.**
- Storefront: free standard shipping, as the store runs now.
- CJ freight is the LuWei Ordinary US line, 5–11 days, quoted 2026-10-29.
- Spoken lines and captions may not mention delivery times or prices (owner rule).

## 9. What must be verified before risking advertising capital

Each item below is needed for every candidate. None of it can be done from data alone.

1. **Sample order of the exact variant**
   - April Satin Pant: black, two sizes.
   - Loafer: black.
   - Hoodie.
   - Dress: the colour we'd sell.
   - Sunglasses.

   Check fabric and finish against the TikTok winner, sizing against the CJ chart, packaging, and real delivery days. It
   is a spend, so the owner decides. The samples also give us real product footage for our AI-labelled ads.
2. **Fresh CJ quote.** Current cost, freight and stock for that exact SKU and variant. The 2026-10-29 numbers are a
   snapshot, and CJ US stock was 0 for all.
3. **IP and design check (#2, #3, #5, and the choker)**
   - No brand names in titles, ads or tags. No brand photos; the CJ choker photo shows an "ORNAMENTUS" tag, so don't use it.
   - For the eye-mask hood, check whether Comfrt holds a design patent. This needs an owner or legal check.
4. **Our price, and the CAC math redone at that price.** The figures above use TikTok's reference price, not ours.
5. **A real conversion rate.** Round 1 has had no purchase from about $290. Round 2's necklace results will be the first
   evidence for our store. A controlled test should have a stop rule set before launch, like PLAN.md's: about one
   break-even CAC spent with no add-to-cart, about two with no purchase.
6. **Policy and claims review of the ad copy.** Use the AI presenter, labelled as AI. No testimonials. No fit, comfort,
   "won't tarnish" or "shower-safe" claims until a sample confirms them.

## 10. Limitations

- **Thin, single-month evidence for C, D, E and F.** Video, supplier and margin data cover one month (Sep 2026) and a
  few dozen products. Strategies C–F are descriptive, not validated.
- **Sustained demand ≠ profit.** The backtest outcome is sustained demand at the category level. It is not our
  conversion rate, CAC or profit. A product can keep selling for an incumbent and still fail for a new store.
- **Saved supplier data is historical.** Photo matching is a visual judgement on main images. A "match" means the same
  design, not the same factory or quality.
- **Kalodata prices are revenue ÷ units.** They include discounts and may not equal the list price.
- **Exploratory picks.** Some choices were made after seeing results (section 5). The M4 segment advantage was found on
  the test months.
- **No calibrated probabilities.** No probability of success is claimed anywhere.

## 11. Next actions (owner decisions marked)

1. **Owner:** approve sample orders for #1 (and #4/#5 if wanted). This is a CJ spend; CJ balance is $0.
2. Re-pull CJ quotes and stock for the chosen variants on the day of ordering. Free.
3. Run the next-10 supplier checks (section 7). Free CJ searches. A CJ sourcing request for the Everyday Cloud tote or
   Cefiro bag needs the owner's OK.
4. Let necklace round 2 run (after the owner publishes it) and read its click-to-purchase rate. Then re-score the
   candidates' break-even conversion rates against it.
5. Re-run in late November with the October Kalodata month (`backtest` → `screen` → `outputs`). Add the result to
   `../registry.jsonl`, and don't edit earlier entries.
