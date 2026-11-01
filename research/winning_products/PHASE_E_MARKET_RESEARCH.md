# Phase E: competition, saturation and consumer behaviour (2026-11-01)

**Evidence label:** descriptive / exploratory. The review analysis covers the 499-product niche sample, drawn from the
Sep-2026 top 500. Its link to future sales is a **forward test**, frozen below.

- Plan, frozen first: `registry/PHASE_E_PLAN.md` (EXP-E-000).
- Results: EXP-E-001, `_work/phase_e_market.json`, `_work/phase_e_consumer.json`.
- Scripts: `scripts/phase_e_market.py`, `phase_e_consumer.py`.
- Cost: no credits.

## Part A: market structure (all 28 categories)

### A1. Category classes (pre-registered rules; terciles across 27 categories, Pre-Owned excluded)

Growth = top-500 revenue, Jun-Sep vs Feb-May 2026. Concentration = the 3 biggest shops' share of top-500 revenue.
Entrant survival = share of new top-500 entrants still there 2 months later.

| Class | Categories (growth / top-3 shop share / entrant survival) |
|---|---|
| **Potentially underserved** (entrants survive well, few dominant shops) | **Fashion Accessories** (0% / 12% / 37%), **Food & Beverages** (−4% / 14% / 39%) |
| **Attractive emerging** (growing ≥ 10%, entrants survive ≥ median) | **Automotive & Motorcycle** (+10% / 16% / 37%) |
| **Established but competitive** (flat, entrants rarely last) | Home Supplies (+8% / 10% / 29%), Sports & Outdoor (+2% / 21% / 31%), Toys & Hobbies (−2% / 13% / 27%) |
| **Highly concentrated** (top-3 shops ≥ 23.5%) | Shoes (37%), Jewelry (35%), Household Appliances (33%), Textiles (30%), Muslim Fashion (29%), Kids' Fashion (28%), Beauty (26%), Tools (24%), Baby & Maternity (24%) |
| **Mixed** | Health (entrant survival 46%, the best, but −10% growth), Pet Supplies (43%), Phones & Electronics (+23%), Menswear (+44%), Computers (+16%), Kitchenware (+10%), Womenswear, Luggage, Books, Home Improvement, Furniture, Collectibles |
| **Insufficient evidence** | Pre-Owned (single items) |

Full profiles, including ASP and its trend, are in `phase_e_market.json` → `E1`. Notes:
- Several "concentrated" categories still grew fast: Kids' Fashion +47%, Textiles +33%, Tools +28%, Baby +28%.
  Concentration here means **big shops take a large share**, not that the category is closed.
- **Beauty prices fell 11%** (Jun-Sep vs Feb-May) while revenue held, which suggests price competition.

### A2. Do fragmented markets let newcomers survive? (E2, H-D2): **No, not supported**

- Across categories, concentration and entrant survival are **not** negatively related: ρ = +0.16, p = 0.43.
- Within single months the sign was negative in only 2 of 8.
- In this data, a market dominated by a few big shops does not make it harder for a new product to hold a top-500
  place. The *entrant survival* rate is the more direct "can a newcomer last here" measure, so use it, not concentration.

### A3. Saturation of near-identical products (E3, H-D3): **not supported, and the measure was the wrong one**

- **What the clustering found:** product titles were clustered (TF-IDF, cosine ≥ 0.70) into 3,029 multi-product "families"
  covering 8,415 of 59,865 products. **The quality check showed most families are the same seller's own variants**
  (1/2/3-packs, "Mom"/"Dad" editions, relisted copies), not different sellers competing on one item.
- **Results:**
  - Adding family features to the Phase C retention model changed AUC by +0.00004, 95% CI [−0.0000, +0.0001] (6/7 months positive but negligible).
  - Growth in a family's shops didn't predict its next-month price (ρ = −0.004).
- **Read:** title text can't detect "many dropshippers selling the same thing", because they write different titles.
  **Image matching is the way to measure saturation.** Kalodata product images cost 0.01 per product, so ~60,000 products
  ≈ 600 credits for everything, or ~15 credits for a 1,500-product shortlist. Perceptual hashing is free once the images
  are in hand. That's a roadmap item, not run.

## Part B: consumers (niche sample: Womenswear, Shoes, Fashion Accessories, Jewelry)

### B1. Reviews are overwhelmingly positive

- **Volume:** 83,156 reviews, 487 products.
- **Ratings:** 5★ 80.4%, 4★ 7.7%, 3★ 3.9%, 2★ 2.3%, 1★ 5.7%. Only **8% are complaints** (1-2★).
- **Ordering:** the API returns the newest 200 per product, so these are recent reviews.

### B2. What people complain about and praise

Rates are the share of 1-2★ reviews (complaints) or 4-5★ reviews (praise) that mention each theme.

**Caveat:** the pre-registered dictionary catches only **35% of complaints**. The unmatched ones mostly use plain words it
lacked: "size", "small", "color", "wrong"/"sent" (wrong item), "length", "refund"/"return". Read the rates as **lower bounds**.

| Category | Top complaints | Top praise |
|---|---|---|
| Womenswear | **size/fit 15%**, quality 13%, comfort 6% | comfort 17% |
| Shoes | **size/fit 16%**, quality 12%, comfort 11% | **comfort 22%** |
| Fashion Accessories | **quality 21%**, size/fit 4%, not as pictured 3% | comfort 12%, quality 6% |
| Jewelry | **quality 16%**, shipping 7%, size/fit 5% | quality 3%, compliments 2% |

- **Apparel and shoes fail on fit; accessories and jewelry fail on quality.** "Not as pictured" is rare in the wording
  people use (1.7% of complaints), though "wrong item sent" shows up among the unmatched words.
- **The 24 older comment insights** agree. Of their 149 AI-extracted pain points, 20 are about shipping or damage on
  arrival, 15 about quality, 13 about size or fit, and only 2 about "not as pictured".

### B3. Do reviews separate durable products from the rest? (descriptive)

Sustained winners (group A, 156 products) vs other sample products (344), from their recent reviews:

| Measure | Sustained A | Others | 95% CI of difference |
|---|---|---|---|
| Mean rating | 4.55 | 4.56 | [−0.06, +0.04] |
| Share 1-2★ | 8.1% | 7.7% | [−0.6, +1.4 pts] |
| Size/fit complaints | 8.3% | 10.1% | [−4.0, +0.3] |
| Quality complaints | 15.7% | 17.0% | [−4.2, +1.8] |
| "Not as pictured" | 1.2% | 1.8% | [−1.6, +0.3] |
| Comfort praise | 11.4% | 14.1% | [−5.0, −0.4] |

**No meaningful difference.** One of 8 comparisons crosses zero, which is what chance would produce. Among products that
are already in the top 500, star ratings and complaint themes don't tell durable from fading. The cleaner test is the
forward one: these review features, using only reviews dated up to 30 Sep, against October retention.
- File: `registry/forward_test_reviews_2026-09.csv`, 285 products, SHA-256 `97f4d493…3e67`.
- Registered tests:
  - R1: share of low-star reviews vs retention (negative expected)
  - R2: "not as pictured" rate vs retention (negative expected)

### B4. Product attributes and selling points (196 products)

- **Most common attribute keys:**
  - Womenswear: Brand, Style, Material, Fit, Washing, Design, Season, Size Type
  - Shoes: Brand, Style, Gender, Upper Material, Toe Shape, Heel Type
  - Accessories: Brand, Material, Gender, Pack Quantity, Hair Type, Length
  - Jewelry: Brand, Material, Origin, Occasion, Style
- **Selling-point highlights:**
  - comfort claims 56% overall (Shoes 86%, Womenswear 78%)
  - convenience 44% (Accessories 60%)
  - aesthetic 35% (**Jewelry 56%**)
  - problem-solving 27% (Shoes 42%, Womenswear 36%, Jewelry 2%)
- These flags join the forward-test file as covariates.
- **Testing whether attributes predict success (H-E2) needs a proper annotation protocol.** Proposed:
  1. Two independent annotators (two LLM passes with different prompts, or LLM + human) score each product on 8
     attributes: demonstrability, problem severity, complexity, novelty, urgency, perceived value, differentiation,
     repeat potential.
  2. Measure agreement (Cohen's κ ≥ 0.6) on 100 products before scoring the rest.
  3. Test against outcomes with category and price controls.
- **Cost:** about 1,500 products × 2 passes on a small model ≈ a few dollars on OpenRouter. That needs owner approval
  because it's a paid API.

## What this means for finding products

1. **Check entrant survival in the category, not concentration.**
   - Health, Pet Supplies, Baby, Beauty, Food and Fashion Accessories let 37-46% of newcomers hold for 2 months.
   - Toys, Home Supplies, Menswear, Muslim Fashion and Collectibles only 21-29%.
2. **Big-shop dominance didn't block newcomers** in this data.
3. **Saturation by copycat sellers is still unmeasured.** Use image matching (cheap) before claiming a product is "not yet saturated".
4. **Plan for the category's typical complaint:**
   - Apparel and shoes → sizing (size charts, fit notes, a "size up" prompt).
   - Accessories and jewelry → build quality and material (sample before listing; describe the material honestly).
   - This matches what the store has already learned (P01 size chart; necklace "sample first").
5. **Stars are not a selection signal.** Almost everything that sells on TikTok Shop is rated 4.5+.

## Checkpoint

- **Saved:** this report, plan, EXP-E-000/001, scripts, results, and the review forward file.
- **Unresolved:**
  - a real saturation measure (images)
  - a better complaint classifier (dictionary v2 or LLM, registered separately)
  - attribute annotation (needs approval)
  - forward tests R1/R2
- **Phase F (Kalodata × CJ sourcing and profitability) is ready.** It uses free CJ API points and the 1 req/s logistics
  limit, needs no money and no store changes, and starts from the Phase C band and retention shortlists across all categories.
