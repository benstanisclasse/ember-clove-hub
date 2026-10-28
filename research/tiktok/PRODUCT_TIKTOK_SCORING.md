# PRODUCT_TIKTOK_SCORING

**Checkpoint C, Phase 6.2.** Ember & Clove (emberandclove.com), 2026-10-25.
All 36 active Shopify products scored for profitable TikTok acquisition under our actual production format
(15 s AI-presenter try-on videos made with Seedance reference-to-video from face-free crops of store photos,
labelled AI, no reviews, no sales history).

> **Existing performance data: none.** No product has sales, reviews, ad results or customer data. Every score is
> either built on documented inputs (economics model, ICP reports, our Top Ads database, the store's own photos and
> product pages) or is a preliminary judgement. Nothing below is a performance result.

---

## 1. Method

### 1.1 Inputs

| Input | Used for |
|---|---|
| `data/product_economics_2026-10-24.csv` (live Shopify prices, EPROLO unit costs, weights, **estimated** shipping) | Margin, advertising economics, season and inventory heuristics |
| Shopify Admin API, read-only (2026-10-25): titles, product types, options, inventory, descriptions, all image URLs | Product facts, sizes, lengths, fabric |
| Store images: 2–11 per product downloaded at 360 px and viewed (all images for P01, P02 and both knit skirts; 4–6 for every other apparel item; 3–6 for every shoe) | Visual demonstration potential, production feasibility, image problems (text, brand labels, mannequins) |
| `data/creatives.csv`, `reports/creative_plan_cycle1_2026-10-24.md` | Whether a Seedance try-on has already been generated and approved for the product |
| `reports/icp_P01_*.md`, `reports/icp_P02_*.md` (executive summaries) | Problem, hook, differentiation, credibility and objections for P01/P02 |
| `research/tiktok/HIGH_PERFORMING_AD_PATTERNS.md` | Category C patterns from 76 US Women's Clothing Top Ads (problem-solving garments dominate; proof on the body; dresses under-represented) |
| `research/tiktok/ATTENTION_PSYCHOLOGY_PLAYBOOK.md` §1, §4 | First-frame rule, relevant surprise, callout + proof, AI-presenter risk |
| `research/tiktok/TIKTOK_ALGORITHM_INTELLIGENCE.md` §1, §9 | Budget/optimization realities (purchase optimization volatile at ~$25/day; ATC as first event) |
| `reports/test_products_2026-10-24.md` | Economics model and the owner's existing choices |

### 1.2 Scores

Eleven Phase 6.2 criteria, each 1–5 (5 = best), unweighted; maximum total 55.

| Code | Criterion | 5 means |
|---|---|---|
| VD | Visual demonstration potential | Key benefit is visible on a body in motion |
| PS | Problem-solution clarity | A real, recognisable need the product visibly answers |
| HK | Strength of the initial hook | A broad situational callout or relevant visual surprise that lands in ≤3 s |
| QV | Ability to demonstrate value quickly | Value understood in one frame |
| DF | Differentiation | Hard to find cheaper/faster elsewhere |
| CB | Credibility of customer benefits | Every benefit can be *shown*, none needs a claim we cannot support |
| OB | Likely objections | 5 = few objections |
| PR | Available proof | 5 = strong. **No product has reviews, so the ceiling is 2** (2 = realistic on-body photos of the actual item; 1 = flat lay, hanger, mannequin or product-only shots) |
| MG | Profit margin | From CSV `margin_pct`: ≥60% = 5, 57–59 = 4, 53–56 = 3, 50–52 = 2, <50 = 1 |
| AE | Advertising economics | Break-even CPA vs a plausible TikTok CPA (below) |
| CP | Creative production feasibility | Face-free, full-length, on-body photos exist and a Seedance try-on has already been approved |

**Evidence marking.** Each score carries a letter: **E** = evidence-based (source named in §1.3 or in the
product notes) and **J** = preliminary judgement. AE scores are E for the break-even figure but rest on a
category-D CPA assumption.

**Advertising-economics assumption (category D, hypothesis).** A new store with no pixel history, cold broad
audiences, AI creative and ~$25/day is assumed to pay **$25–45 per purchase, central estimate $35**. This is not
measured; the earlier test-products report's "$20–50" range is itself unsourced practitioner lore (C/D), and TikTok
documents only that purchase-optimized delivery stays volatile below ~25 results (A). Scale: break-even CPA
≥ $35 = 4 (survives the central estimate); $31–35 = 3 (survives only the better half of the range); $25–31 = 2;
< $25 = 1 (needs a CPA below anything we should expect). No product reaches 5 (≥ $45). Stress-case shipping lowers
every break-even by $2–4 (CSV `break_even_cpa_high_ship`).

### 1.3 What "E" cites, by criterion

- **VD, CP:** the store photos as viewed on 2026-10-25 (on-body vs flat lay, motion, face crops, text/labels), plus
  approved generations in `data/creatives.csv` (EC-P01-A03-H01-V01 and EC-P02-A03-H01-V01, both APPROVED by the owner).
- **PS, HK, DF, CB, OB for P01/P02:** the ICP reports (search evidence, competitor price tables, VoC objections).
  For every other product these are **J** — no ICP research exists for them, which is the single biggest bias in
  this table (see §6).
- **PR:** the fact of zero reviews (store is new) plus the observed photo type.
- **MG, AE:** economics CSV. **OB** for shoes and lightweight items also uses the CSV `season` heuristic and the
  product pages' size/length facts.

### 1.4 Seasonality gate (not scored)

Delivery takes 2–3 weeks, so anything ordered from an ad today arrives roughly Nov 8–15; orders placed after about
Dec 1–4 risk missing Christmas. Products must suit late-November-to-December use in the US.

- **Pass:** cold-weather or year-round layering item.
- **Conditional:** usable only in a narrow December situation (indoor holiday party, worn with tights or layers).
  Not suitable for a first test; at most a timed December test.
- **Fail:** sandals, slides and summer shoes (CSV `season` = 0.4). Excluded from recommendations regardless of score.

---

## 2. Full score table (all 36, sorted by total; ties broken by break-even CPA)

| # | Product | Gate | VD | PS | HK | QV | DF | CB | OB | PR | MG | AE | CP | **Total /55** | BE CPA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Cable Knit Mock Neck Midi Dress (P01)** | Pass | 5E | 4E | 4E | 5E | 2E | 4E | 3E | 2E | 4E | 4E | 5E | **42** | $35.20 |
| 2 | Long Pleated Knit Skirt | Pass | 5E | 3J | 4J | 4J | 2J | 4J | 3J | 2E | 4E | 3E | 3J | **37** | $32.34 |
| 3 | **Ruffle Slit Knit Midi Skirt (backup)** | Pass | 4E | 3J | 3J | 4J | 3J | 4J | 3J | 2E | 4E | 3E | 4E | **37** | $32.18 |
| 4 | **Turtleneck Rib Knit Sweater Dress (P02)** | Pass | 4E | 4E | 4E | 4J | 1E | 3E | 2E | 2E | 4E | 3E | 4E | **35** | $31.13 |
| 5 | Henley Tie-Waist Rib Maxi Dress | Pass | 3J | 3J | 3J | 3J | 3J | 3J | 3J | 1E | 3E | 4E | 1E | **30** | $36.52 |
| 6 | Striped Polo Collar Knit Sweater | Pass | 3J | 2J | 3J | 3J | 3J | 3J | 3J | 1E | 4E | 4E | 1E | **30** | $35.26 |
| 7 | Rose Accent Strappy Stiletto Sandals | Conditional | 3E | 1J | 3J | 3J | 3J | 3J | 2J | 1E | 4E | 3E | 2E | **28** | $33.59 |
| 8 | Pinstripe Pleated Mini Skirt | Conditional | 3J | 2J | 3J | 3J | 3J | 3J | 3J | 1E | 3E | 3E | 1E | **28** | $31.47 |
| 9 | Belted Collared Midi Shirt Dress | Conditional | 3J | 3J | 2J | 3J | 2J | 3J | 3J | 1E | 4E | 3E | 1E | **28** | $31.25 |
| 10 | Ruffle Hem Mesh Mini Dress | Conditional | 3J | 3J | 3J | 3J | 2J | 2J | 2J | 1E | 3E | 3E | 2E | **27** | $33.96 |
| 11 | Croc-Embossed Slingback Stiletto Sandals | Conditional | 3E | 1J | 3J | 3J | 2J | 3J | 2J | 1E | 4E | 3E | 2E | **27** | $33.59 |
| 12 | Floral Rib Knit Bodysuit | Pass | 3J | 3J | 3J | 3J | 2J | 3J | 2J | 1E | 3E | 3E | 1E | **27** | $32.31 |
| 13 | Diagonal Rib Mock Neck Bodysuit | Pass | 3J | 3J | 3J | 3J | 2J | 3J | 2J | 1E | 3E | 3E | 1E | **27** | $31.79 |
| 14 | Asymmetric Faux Suede Midi Skirt | Pass | 3J | 2J | 3J | 3J | 3J | 3J | 3J | 1E | 3E | 2E | 1E | **27** | $30.87 |
| 15 | Textured Rib Mock Neck Bodysuit | Pass | 3J | 3J | 3J | 3J | 2J | 3J | 2J | 1E | 3E | 2E | 1E | **26** | $30.06 |
| 16 | Pheasant Print Crewneck Fleece Sweatshirt | Pass | 2J | 1J | 3J | 3J | 2J | 3J | 3J | 1E | 4E | 2E | 2E | **26** | $29.60 |
| 17 | Mesh Knit Chunky Sole Sandals | Fail | 2E | 2J | 2J | 3J | 2J | 3J | 2J | 1E | 5E | 2E | 2E | **26** | $27.42 |
| 18 | Closed Toe Slingback Espadrille Wedges | Fail | 2E | 2J | 2J | 3J | 2J | 3J | 2J | 1E | 5E | 2E | 2E | **26** | $26.47 |
| 19 | Braided Cord Strappy Flat Sandals | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 5E | 2E | 2E | **25** | $26.11 |
| 20 | Butterfly Rhinestone Slingback Flats | Fail | 2E | 1J | 3J | 3J | 3J | 3J | 2J | 1E | 4E | 1E | 2E | **25** | $19.79 |
| 21 | Crisscross Stretch Strap Flat Sandals | Fail | 2E | 2J | 2J | 3J | 2J | 3J | 2J | 1E | 5E | 1E | 2E | **25** | $17.91 |
| 22 | Malibu Beach Graphic Sweatshirt | Pass | 2J | 1J | 2J | 3J | 1J | 3J | 3J | 1E | 4E | 2E | 2E | **24** | $29.60 |
| 23 | Textured Peep Toe Slip-On Flats | Fail | 2E | 2J | 2J | 3J | 2J | 3J | 2J | 1E | 3E | 2E | 2E | **24** | $29.38 |
| 24 | Ruched Mesh Wrap V-Neck Top | Conditional | 2J | 2J | 2J | 3J | 2J | 3J | 3J | 1E | 4E | 1E | 1E | **24** | $24.78 |
| 25 | Double Band Buckle Flat Sandals | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 5E | 1E | 2E | **24** | $17.49 |
| 26 | Pointed Peep Toe Stiletto Mules | Conditional | 2E | 1J | 3J | 3J | 2J | 3J | 2J | 1E | 1E | 4E | 1E | **23** | $37.26 |
| 27 | Double Buckle Platform Slingback Sandals | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 3E | 2E | 2E | **23** | $27.32 |
| 28 | Studded Wood-Look Block Heel Sandals | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 3E | 2E | 2E | **23** | $27.06 |
| 29 | Toe Loop Faux Leather Slides | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 4E | 1E | 2E | **23** | $22.18 |
| 30 | Shimmer Band Platform Wedge Slides | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 4E | 1E | 2E | **23** | $21.66 |
| 31 | T-Strap Buckle Platform Sandals | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 4E | 1E | 2E | **23** | $21.46 |
| 32 | Paris Knit Band Flat Slides | Fail | 2E | 1J | 2J | 3J | 2J | 2J | 2J | 1E | 5E | 1E | 2E | **23** | $17.46 |
| 33 | Embroidered Band Espadrille Platform Slides | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 3E | 1E | 2E | **22** | $23.00 |
| 34 | Clear Strap Platform Wedge Slides | Fail | 2E | 1J | 2J | 3J | 2J | 3J | 2J | 1E | 3E | 1E | 2E | **22** | $22.84 |
| 35 | Rhinestone H-Band Flat Slides | Fail | 2E | 1J | 2J | 3J | 2J | 2J | 2J | 1E | 4E | 1E | 2E | **22** | $22.74 |
| 36 | Metallic Square Toe Heeled Mules | Fail | 2E | 1J | 2J | 3J | 2J | 2J | 2J | 1E | 2E | 2E | 1E | **20** | $29.32 |

**Reading the table.** Totals within ~2 points of each other are not meaningfully different: most non-economic
scores outside P01/P02 are judgement. The robust findings are the *bands*: four knit pieces with real on-body
photos (35–42), then a cluster of flat-lay or mannequin apparel (26–30) that would need new footage, then
out-of-season shoes (20–28).

### 2.1 Product notes behind the scores (observations from images and pages, 2026-10-25)

**Apparel**
- **P01 Cable Knit Midi:** 11 images, one model, street backdrop, full-length, **knee-high boots visible through the
  slit**, 7 colours; 5 colour shots are already cropped at the mouth (face-free). A wall sign/logo sits in the
  background of the street shots (crop it out). Owner-approved Seedance try-on exists (EC-P01-A03-H01-V01).
  ICP: boots outfit is the #1 "sweater dress" search modifier; price higher than Amazon/Walmart/SHEIN/Old Navy
  alternatives; acrylic blend; S–XL only; fitted, so cling-averse shoppers are a negative ICP.
- **Long Pleated Knit Skirt:** 10 lifestyle images, faces already cropped, pleats flaring mid-step and on stairs
  (description: pleats "sway as you walk"). One image has Chinese text and one has an English caption ("TEXTURE T
  SHIRT") printed on it. One size, elastic waist "24 in". Styled with fuzzy slides and clogs (boots would have to be
  generated). Owner rejected it on 2026-10-24. CP lowered to 3: fine knife pleats in motion are high-frequency
  detail that AI video may render with flicker (J, untested).
- **Ruffle Slit Knit Midi Skirt:** 9 lifestyle images, mostly face-free, ruffle-trimmed curved slit visible when
  stepping and sitting; styled with socks and fluffy house slides; one image has a caption strip. One size, elastic
  waist 24–39 in (a real, showable objection-handler). No Seedance generation yet.
- **P02 Turtleneck Sweater Dress:** 11 clean studio images, consistent model, static hand-on-hip poses, **bare legs
  in every photo** (the ICP says it must always be shown over tights with boots, so those must be generated), faces
  visible in all, so chin-level crops are needed next to a high turtleneck. Owner-approved Seedance try-on exists
  (EC-P02-A03-H01-V01). ICP: near-identical items at $5–20 (AliExpress/SHEIN) and ~$46 on Amazon with Prime and
  longer length; 27–28 in length is shorter than every comparable; "S–3XL" is misleading (48 in max garment bust).
- **Henley Tie-Waist Rib Maxi:** flat lays and a hanger close-up only; S–L. Best economics of the in-season set.
- **Striped Polo Collar Sweater:** flat lays only; a visible **third-party brand label ("BBWM")** on the collar in
  most images; colour names are long combinations.
- **Ruffle Hem Mesh Mini Dress:** gold mannequin only (exaggerated curvy form, cables visible); tangerine and
  peacock blue; close-fitting mesh. Could be a December party piece, but nothing shows it on a body.
- **Pinstripe Pleated Mini (13 in), Belted Shirt Dress (polyester shirting), Faux Suede Skirt:** flat lays only.
- **Bodysuits (3):** flat lays; two show a third-party woven label at the neck. Functional benefit (stays tucked)
  matches the "problem-solving garment" pattern in our Top Ads database (C), but nothing can be shown from the photos.
- **Sweatshirts (2):** hanger shots on wood with "Sweatshirt Only" text overlaid; commodity print-on-demand
  graphics; "Malibu Beach" is a summer theme.
- **Ruched Mesh Top:** flat lays; cropped, sheer sleeves.

**Shoes (all Shopify product type "Sandals")**
- Most have close on-foot crops (face-free by nature) but no full-body shots, so a try-on video must generate the
  shoe on a walking presenter; shoes are the hardest item for faithful generation (brief).
- **Croc-Embossed Slingback** is styled with disco balls, and **Rose Accent** is a strappy metallic/red stiletto:
  genuine holiday-party footwear, hence "Conditional". **Pointed Peep Toe Mules** are product-only shots and priced
  above the $70 free-shipping line (no shipping income; lowest margin, 43%).
- **Metallic Square Toe Mules:** product-only studio shots in a style resembling a high-street retailer's catalogue
  (J); single colour (orange).
- **Rhinestone H-Band** and **Paris Knit Band** slides resemble designer motifs (J; CB lowered for dupe/IP risk).

---

## 3. Top 5

### 1. Cable Knit Mock Neck Midi Dress (P01) — 42/55, gate Pass
**Why.** It is the only product that is strong on both halves of the problem: the economics (break-even $35.20,
just above the $35 central CPA assumption, E/D) and the creative (the store photos already *are* the ad: full-length,
on-body, mid-stride, boots through the slit, face-free crops, and an owner-approved Seedance try-on, E). The ICP
found the clearest need in the catalogue: "what do I wear with my tall boots?" is the leading sweater-dress search
modifier (E, ICP P01), which turns a "dress with a weak built-in problem" (Top Ads database §3.7, C) into a
problem-solution outfit. **Main risk:** differentiation and price. It costs $60.99 delivered with 2–3 week
shipping and no reviews against cheaper, faster look-alikes (E, ICP P01). If real CPA lands at $40+, it loses money.
Its fitted cut also excludes cling-averse buyers (E). **Best angle:** "The dress your tall boots need": a broad
situational callout ("Own knee-high boots? This dress is for you.", ≤8 words, playbook §4.1–4.2) on a frame-1
motion shot of dress + boots, followed by proof on the body (hem-to-boot line, slit while walking; database §3.4,
playbook finding 2). December holiday events are the second angle; Thanksgiving delivery is already at risk.

### 2. Long Pleated Knit Skirt — 37/55, gate Pass
**Why.** It has the strongest built-in motion of any product: knife pleats that flare when she walks or climbs a
step, already photographed on a body mid-step and face-free (E). That gives a *relevant* visual surprise in frame 1
(playbook finding 4) without a gimmick. **Main risk:** the owner already rejected it, and most of its score is
judgement (no ICP research). One photo has Chinese text, the one-size "24 in" elastic waist leaves fit range unclear,
the photos are styled with slides and clogs, and fine pleats may flicker in AI video (J). **Best angle (D):** a
motion-first outfit formula: "chunky sweater, boots, this skirt" with a walking or stair-step swing as the proof
shot. This borrows the boots/outfit-formula search pattern found for sweater dresses (an inference, not verified for
skirts).

### 3. Ruffle Slit Knit Midi Skirt (backup) — 37/55, gate Pass
**Why.** It has real lifestyle photos on a body, mostly face-free, with a distinctive ruffle-trimmed curved slit
that shows as soon as she steps or sits (E). One size with a 24–39 in elastic waist is a factual, showable answer to
the sizing objection that hurts P01 and P02 (E, product page). **Main risk:** no ICP research, so PS, HK, DF and OB
are judgement. Every photo is styled in a cosy-at-home Korean street look (socks, fluffy slides), so a US "boots"
outfit must be generated, and boots add shoe-fidelity risk. No Seedance test has been run yet. **Best angle (D):**
"the ruffle slit reveal": open mid-step on the slit and ruffle (first-frame motion, H-AP-03), then a sit-down shot
showing the knit staying comfortable, then the elastic waist. Pair it with tall boots so it competes in the same
boot-season search space as P01.

### 4. Turtleneck Rib Knit Sweater Dress (P02) — 35/55, gate Pass
**Why.** It has documented demand (sweater dress + tights + boots is the dominant cold-weather outfit search; comfort
that "reads as dressed" is a repeated VoC theme; E, ICP P02), seven colours, an owner-approved Seedance try-on, and
164,500 units in stock. **Main risk:** it is the most commoditised product in the top tier (DF 1: near-identical
dresses at $5–46 elsewhere, E). Its length (27–28 in) makes it a tunic that must always be shown over tights.
"S–3XL" overpromises (E, ICP P02). It also has the lowest break-even in the chosen trio ($31.13, $28.48 stress
case), so it needs a better-than-central CPA to profit. **Best angle:** the ICP's first test, "Black tights, tall
boots, and this. That's the whole outfit." (outfit formula; tights and boots in frame 1), with "pajama-comfortable,
still looks dressed" as the backup. Do not say "to 3X".

### 5. Henley Tie-Waist Rib Maxi Dress — 30/55, gate Pass
**Why.** It has the best economics of any in-season product (break-even $36.52, E). The tie-waist and front slit are
demonstrable features on a body in motion ("one knot gives it a waist"), and a henley maxi is less commodity than
a turtleneck mini (J). **Main risk:** every image is a flat lay or hanger shot, and the sizes stop at L. An AI try-on
would have to *invent* how it fits and drapes (CP 1, PR 1, E), which risks misrepresentation and a returns problem
under the buyer-pays return policy. It needs a real on-body reference (an ordered sample, or AI model stills checked
carefully against the flat lay) before any video. **Best angle (D):** a waist-tie demonstration: she ties the sash on
camera and the silhouette changes. This is the relevant-surprise and process-simulation idea (playbook H-AP-07),
styled with boots for December.

---

## 4. Bottom line

**Does the scoring agree with the owner's first test?**

- **P01: yes, clearly.** It ranks first by 5 points and is the strongest on both economics and production. Keep it as
  the lead test.
- **P02: only partly.** It ranks 4th, behind both knit skirts, because of three documented weaknesses: commoditisation
  (DF 1), objections (length, the 3XL claim, price anchoring) and the lowest break-even of the four. It remains a
  defensible second test for three reasons. Its weaknesses are *known and manageable* (show tights and boots; drop
  "to 3X"). Its ICP research and an approved generation already exist. And it leads the next tier (30) by 5 points.
  The skirts' 2-point lead is mostly judgement, scored without the scrutiny P02 received, so it is within noise.
  Honest caveat: if P02's first ads show cost per add-to-cart well above P01's, the evidence already points to the
  skirts as the next swap, not another sweater dress.
- **Backup Ruffle Slit Knit Midi Skirt: yes.** It is in the top tier (37, tied 2nd), and its one-size elastic waist
  is a real advantage. The Long Pleated Knit Skirt scores the same 37 and edges ahead only on the tie-break. The
  difference is noise, and the owner's veto plus the text-marked photo are fair reasons to prefer the ruffle skirt.

**Next two products to prepare (ICP research, face-free reference crops, one Seedance test each):**
1. **Long Pleated Knit Skirt.** It is the highest-scoring product not in the test. Ask the owner to reconsider
   on the evidence (motion demonstration, on-body photos). If the veto stands, skip to #2 and take the Striped Polo
   Collar Knit Sweater as the second (30; good economics; needs on-body references, and the "BBWM" label must never
   appear in an ad).
2. **Henley Tie-Waist Rib Maxi Dress.** It has the best in-season economics, but it is "prepare", not "test": first
   get a true on-body reference (sample order, or AI stills checked against the flat lay), then ICP research.

**Not now:** all 17 open sandals and slides (fail the gate; most also have break-even CPAs at or below $27). The
evening stilettos (Rose Accent, Croc Slingback) and the Mesh Mini Dress are possible *timed* December party tests
only after the knit products have produced data. Orders must arrive before mid-to-late December, so any such test
would have to run by about Dec 1.

**Budget reality.** At ~$25/day, purchase-level winners cannot be identified (TikTok's guidance: volatility falls
after ~25 results, A). Compare products on cost per add-to-cart and destination CTR first (algorithm report §9,
recommendation 1; playbook §4.5).

---

## 5. Data gaps (and how each would change the scores)

1. **Real CPA.** The AE column rests on an assumed $25–45 (D). One week of P01/P02 data replaces it. If CPA is
   ≥ $35, only P01, the Henley, the Polo and the Pointed Mules break even.
2. **EPROLO's real shipping charge** is estimated (≈ $3.50 + $10/kg). The stress case cuts every break-even by $2–4
   and would push P02 ($28.48) and both skirts (~$29.3) below the CPA range.
3. **No ICP research for anything except P01/P02.** The skirts' and Henley's PS/HK/DF/CB/OB scores are judgement and
   probably optimistic (unresearched products have undocumented weaknesses). Run an ICP study before committing ad
   spend to them.
4. **No reviews, sales or return data** for any product, so PR is capped at 2 for every product. The first orders and
   returns are the first real proof.
5. **Garment measurements unverified**, except P02's supplier chart (whose 3XL problem shows charts can mislead).
   The skirts' one-size elastic ranges especially need a sample check.
6. **AI generation fidelity is untested** for pleats, ruffles, boots and tie sashes; only P01 and P02 have approved
   Seedance outputs. One test generation per new product settles CP.
7. **Image rights and marks.** The supplier photos carry third-party labels (BBWM, bodysuit neck labels), printed text
   (pleated skirt, sweatshirts) and a background sign (P01). Confirm usage rights and crop or avoid these in references.
8. **AI-presenter performance:** our Top Ads sample contained no AI ads, so how labelled AI try-ons convert is unknown (C).
9. **Delivery-time reality:** "2–3 weeks" is the store's stated estimate. Actual transit times decide how long the
   holiday angles can run.
10. **Inventory figures** are supplier-side counts (e.g., 164,500), not stock we hold. They are useful only to show
    nothing is near sell-out.
