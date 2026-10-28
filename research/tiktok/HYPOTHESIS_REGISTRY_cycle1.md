# HYPOTHESIS_REGISTRY — cycle 1 (Phase 7.1)

Ember & Clove, 2026-10-25. Registered **before** any creative is generated or launched. Concepts, hooks and scripts:
`EMBER_CLOVE_CREATIVE_CONCEPTS.md`; generator specs for round 1: `scripts/concept_specs_cycle1.py`. Every hypothesis
here is category **D** (plausible, unverified); the evidence behind each is cited in the concepts file and the
Checkpoint B library. Results at this budget will be **directional**, and are reported as exploratory unless stated.

Pre-registered priority (owner decision 2026-10-25, relayed by the lead researcher): **(a)** callout vs demo-first
opening → **(b)** TikTok auto-captions on vs off → **(c)** later, 15 s vs 25–30 s of the winner. One variable per
controlled comparison; concept-level (angle/motive) comparisons are exploratory because whole videos differ.

---

## 1. Open owner decisions that set the budget (not decided here)

1. **Optimization event and daily budget** (AI §9 rec 1, A + D): (i) Add to Cart at ≥ $30/day per ad group (TikTok's
   new-store advice), moving winners to Purchase later; (ii) fewer ad groups with more budget; (iii) Purchase
   optimization accepted as directional only. `reports/campaign_structure_2026-10-24.md` currently plans $25/day per
   product, Add to Cart, then a Purchase "Winners" group at $30–40/day from day 8, inside a ~$600 test budget.
2. **How test (a) is run** (media options; generation cost is the same, $19.44 for both pairs):

| Option | Set-up | Media for (a), 7 days | Read quality |
|---|---|---|---|
| M1 (current plan) | Both arms + 2 other concepts in one screening ad group per product, $25/day, ATC | ≈ $175 per product (shared with the other ads) | Weakest: TikTok allocates spend unevenly between ads, so arms get different volumes and audiences |
| M2 | TikTok split test per product: two ad groups, one arm each, $30/day each, ATC | ≈ $420 per product (≈ $840 both; above the ~$600 budget) | Cleanest available |
| M2b | Split test on one product only (P01 or P02); the other product runs M1 | ≈ $420 + ≈ $175 | Clean on one product, directional on the other |
| M3 | One ad group per product at $30/day with 4 ads (TikTok ≥ $30 advice), ATC | ≈ $210 per product (≈ $420 both), leaves ≈ $180 of ~$600 for (b) in week 2 | Directional; read (a) on per-impression metrics |

3. Whether the legacy approved ads run at all (EC-P01-A03 as a benchmark; **EC-P02-A03 should not run** because it says
   "sizes small to 3X").
4. Generation spend: round 1 = 8 × ≈ $4.86 = **$38.88** (+ re-roll reserve, cap ≈ $48.60). Round 2 (c) ≈ $8.10–9.72
   per product.

## 2. Standard definitions used in the rows

**Metrics (AI §6, A definitions; formulas stated because some are not TikTok columns):**
- *Stop rate* = 2-s video views ÷ impressions. *Retention at s3* = per-second retain curve at second 3 (API, our
  account). *Hold* = 100% views ÷ 2-s views. Never plain 6-s views or average play time (inflated by interactions/loops).
- *CTR (dest.)* = destination clicks ÷ impressions. *CVR (clicks)* = ATC (or purchases) ÷ destination clicks (not
  TikTok's default conversions ÷ impressions). *ATC/1k* = add-to-carts per 1,000 impressions (= CTR × CVR; the
  "qualified attention" metric). Report TikTok-attributed and Shopify numbers side by side.
- **SEC-std (secondary set):** stop rate, retention at s3 and the per-second curve, hold, CTR (dest.), CVR (clicks),
  landing-page views ÷ clicks, cost per ATC, purchases (Shopify) when any.

**Sample-size arithmetic (D; inputs are assumptions, not measurements from our account):** at $30/day and an assumed
$8 CPM, an ad group buys ≈ 3,750 impressions/day (≈ 26,000 in 7 days), shared unevenly by its ads.
- With ≥ 5,000 impressions per arm, a 5-point stop-rate gap (25% vs 30%) is ≈ 5.6 standard errors: readable.
- A CTR gap of 0.8% vs 1.2% at 5,000 impressions each is ≈ 2 standard errors: borderline.
- At an assumed 1% CTR and 6% ATC per click (≈ 0.6 ATC/1k), 5,000 impressions ≈ 3 ATC per arm: **not readable**.
  Detecting a 2× ATC/1k difference with ~80% power needs roughly 25 ATC in the weaker arm (Poisson log-ratio
  approximation), i.e. ≈ 40,000 impressions (≈ $330 at the assumed CPM) per arm.
- Purchase-level conclusions are out of reach in cycle 1 (≈ 5 purchases/week at best, PB §4.5). Conversion-side
  results are directional; decisions use the per-impression diagnostics plus ATC direction.
- About 12 comparisons are registered for round 1–2; treat anything beyond the pre-registered (a) as exploratory, and
  if formal tests are run, apply a Holm correction across the round.

**STOP-std (stop conditions for every row):**
- S1 Days 1–3: no judging (learning); only S2/S3 apply.
- S2 Loss limit: an ad that spends $25 with no ATC → recommend pause; owner approves (campaign structure).
- S3 Compliance: policy rejection, a comment pattern saying the ad misrepresents the dress, or a claim found
  inaccurate → pause at once and review.
- S4 End of test: 7 days, or each arm ≥ 5,000 impressions and ≥ 50 destination clicks, whichever is later; hard stop
  at 14 days.
- S5 No edits, duplicates, budget changes or pauses inside a running comparison except S2/S3 (AI §9 rec 5).
- S6 Time box (occasion concepts): stop at the stated date even if mid-test.

**CONF-std (confounders for every row):**
- K1 Regeneration: each arm is a separate Seedance generation, so presenter, room and shots 2–4 render differently
  even with identical prompts.
- K2 Delivery allocation inside a shared ad group (different volumes and audience pockets per ad).
- K3 Learning phase and day-of-week; Q4 CPM drift (holiday season).
- K4 Attribution: view-through / engaged-view credit (B: Gordon et al. 2019).
- K5 Organic engagement on Spark posts accumulates differently (comments, likes visible to viewers).
- K6 Site changes mid-test (theme publish, size chart, prices) and pixel/Events API match quality.
- K7 AI label and synthetic presenter are constant, so findings may not transfer to human footage.

---

## 3. Round-1 registry (shortlisted videos, plus test (b))

| ID | Product | Audience (ICP) | Concept / creative IDs | Variable tested | Expected mechanism | Primary metric | Secondary | Gen. cost · proposed media | Sample-size note | Stop conditions | Confounders |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **HC1-01 (a)** | P01 | Broad US women 18+; message aimed at S1 boot-season builders | A05 "Tall boots, finished": **EC-P01-A05-H01-V02** (HK-31 callout) vs **EC-P01-A05-H02-V02** (HK-35 demo-first) | Opening type: spoken line 1 only (frame-1 action, refs, shots 2–4 prompts identical) | Callout → self-relevance: fewer but more qualified stops (ELM; Matz 2017, B). Demo-first → motion + "watch" curiosity closed by the product: more stops, less qualified (PB H-AP-05) | **ATC/1k** (directional) | SEC-std, esp. stop rate and retention at s3 (the readable part) | $9.72 · M1/M2/M2b/M3 (owner) | Stop rate/s3 readable at ≥ 5k impr./arm; ATC/1k not (≈ 3 ATC/arm) | STOP-std | CONF-std; K1 is the main threat (two renders) |
| **HC1-02 (a)** | P02 | Broad; message aimed at S1 outfit-formula seekers | A05 "Whole outfit": **EC-P02-A05-H01-V02** (HK-39 callout) vs **EC-P02-A05-H02-V02** (HK-17 demo-first) | Opening type: spoken line 1 only | As HC1-01; HK-17 also front-loads the formula (decision ease) | **ATC/1k** (directional) | SEC-std | $9.72 · as HC1-01 | As HC1-01 | STOP-std | CONF-std; HK-17 runs 10 words vs 9 (length differs slightly) |
| HC1-03 | P01 | S1 | **A05 concept** (boots + stride demo, AR-04) vs the P01 group's other concepts and, if run, legacy EC-P01-A03 | Angle/motive (whole video) | Attaching the dress to the top search pairing ("with boots") and showing the slit in stride gives relevant proof (B demo/ELM) | Cost per ATC | SEC-std | Included in HC1-01 · same group | Exploratory; whole videos differ | STOP-std | CONF-std; legacy A03 differs in format and frame 1 |
| HC1-04 | P01 | S2 holiday-gathering dressers | **EC-P01-A06-H01-V02** (AR-15, red, HK-19) vs A05-H01 | Motive: dated event + honest delivery line | Dated-goal relevance (B self-relevance); delivery line pre-qualifies (D) | CVR (clicks) | SEC-std; later: delivery complaints per order | $4.86 · same group as A05 | Exploratory; ≈ 2 weeks of window only | STOP-std + **S6: stop ~Nov 15–20** | CONF-std; color (red vs caramel); seasonality rises over the window |
| HC1-05 | P01 | S1 comparison shoppers / ad-store skeptics | **EC-P01-A09-H01-V01** (AR-14, HK-36) vs A05-H01 | Persuasion route: transparency (length, fabric, delivery up front) vs outfit/demo | Pre-empting objections raises CVR among clickers while lowering CTR (D; argument quality, B) | Cost per ATC | SEC-std; later: refund/length complaints per order | $4.86 · same group | Exploratory | STOP-std | CONF-std; 36-word script is denser (pace) |
| HC1-06 | P02 | S1 | **A05 concept** (outfit build, AR-05) vs the P02 group's other concepts | Angle/motive | Decision ease of a stated formula (ICP-P02 A2, evidence Strong) | Cost per ATC | SEC-std | Included in HC1-02 | Exploratory | STOP-std | CONF-std; legacy P02-A03 excluded (3X line) |
| HC1-07 | P02 | S2 comfort-first | **EC-P02-A06-H01-V02** (AR-06 adapted, HK-03) vs A05-H01 | Motive: comfort that reads as dressed vs outfit formula | Comfort is the deeper motive and less generic than "with boots" (ICP-P02 A1 hypothesis) | CVR (clicks) | SEC-std | $4.86 · same group | Exploratory; the key P02 motive question, needs round 2 to confirm | STOP-std | CONF-std; leggings vs tights styling |
| HC1-08 | P02 | S3 holiday-season eaters | **EC-P02-A07-H01-V01** (AR-15, HK-32) vs A05-H01 | Motive: occasion + comfort at the table + delivery line | Dated-goal relevance (B); comfort framing (R evidence in ICP) | CVR (clicks) | SEC-std | $4.86 · same group | Exploratory | STOP-std + **S6: stop ~Nov 20–25** | CONF-std; setting change (dining room) |
| **HC1-09 (b)** | P01 | Same as the (a) winner | Same video posted twice as Spark posts: **auto-captions ON vs OFF** (default video: HC1-01 winner, else A05-H01) | TikTok auto-captions | Same-language text aids muted viewers and recall (B Brasel & Gips 2014; A TikTok guidance) | CTR (dest.) | Stop rate, retention at s3, ATC/1k | **$0** generation · week 2, ~$25–30/day, owner decision | CTR gap of ~0.4 pt borderline at 5k impr./arm | STOP-std | K2–K6; **prerequisite: verify** captions show on Spark Ads and a second post of the same video is eligible |
| **HC1-10 (b)** | P02 | Same | As HC1-09 with the HC1-02 winner (else A05-H01) | TikTok auto-captions | As HC1-09 | CTR (dest.) | As HC1-09 | **$0** · week 2 | As HC1-09 | STOP-std | As HC1-09 |

## 4. Round 2 (after a 15 s winner exists)

| ID | Product | Audience | Concept / creative IDs | Variable tested | Expected mechanism | Primary metric | Secondary | Gen. cost · proposed media | Sample-size note | Stop conditions | Confounders |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **HC1-11 (c)** | P01 | Winner's segment | Winner (15 s) vs 25–30 s version, same opening (outline in concepts file) | Length | More proof time (length, fabric, AOV line) vs more drop-off; better-ranked conversion ads ran ~36 s (HP §2, C, confounded) | Cost per ATC | Hold, per-second curve, CTR, CVR (clicks) | $8.10–9.72 (+ re-rolls) · owner decision | Same limits as round 1 | STOP-std | CONF-std; the longer script adds facts, so length and content co-vary |
| **HC1-12 (c)** | P02 | Winner's segment | As HC1-11 (or EC-P02-A08 "Three honest things" at its natural 25 s) | Length | As HC1-11 | Cost per ATC | As HC1-11 | $8.10–9.72 | As above | STOP-std | As HC1-11 |

## 5. Backlog registry (one row per remaining concept/hook test; not scheduled)

Defaults unless stated: primary = ATC/1k for hook tests, cost per ATC for concept tests; secondary = SEC-std;
generation $4.86 per arm (15 s); media = later round, owner decision; sample-size = as §2 (directional);
stop = STOP-std; confounders = CONF-std. "Comparator" = the arm it is tested against.

| ID | Product | Audience | Creative (hook) | Comparator | Variable tested | Expected mechanism | Specific notes (refs, stops, confounders) |
|---|---|---|---|---|---|---|---|
| HC1-B01 | P01 | S1 | A05-H03 (HK-01 problem + situation) | A05-H01 | Problem question vs plain callout | Problem recognition adds relevance for "jeans on repeat" viewers | Jeans prop in frame 1 adds clutter |
| HC1-B02 | P01 | S2 | A06-H02 (HK-24 "check the delivery time first") | A06-H01 | Mistake-avoidance opener vs occasion callout | Honest pre-qualifier: lower CTR, higher CVR (D) | 10-word line; S6 ~Nov 15–20 |
| HC1-B03 | P01 | S2 | A06-H03 (HK-29 story) — TEST ARM | A06-H01 | Story opening (no callout) vs callout | Narrative transportation (B) | S6; story may overshadow the dress |
| HC1-B04 | P01 | S3 | A07-H01 (HK-33) concept | A05-H01 | Motive: going out, covered vs boots outfit | Emotional self-presentation (ICP-P01 A3) | **Needs black crops**; watch fit-return requests |
| HC1-B05 | P01 | S3 | A07-H02 (HK-18 adapted, demo-first) — TEST ARM | A07-H01 | Opening type | As HC1-01 | Needs black crops |
| HC1-B06 | P01 | S3/S1 | A07-H03 (HK-15 frustration) | A07-H01 | Frustration vs callout | Relatable frustration → relevance | Needs black crops |
| HC1-B07 | P01 | S1 solution-aware | A08-H01 (HK-22) concept | A05-H01 | Education vs demo/callout | Education that sells (B argument quality) | **Needs green crops**; primary hold, then CTR |
| HC1-B08 | P01 | S1 | A08-H02 (HK-10 curiosity) | A08-H01 | Curiosity vs mistake-avoidance | Curiosity gap closed by product (B) | Library: curiosity ranked weaker within Conversions (C) |
| HC1-B09 | P01 | S1 | A08-H03 (HK-08 build) | A08-H01 | Build/visual transformation vs mistake-avoidance | Progression credibility (B Cian 2020) | Needs green crops |
| HC1-B10 | P01 | Skeptics | A09-H02 (HK-37 "exactly how long", demo-first) — TEST ARM | A09-H01 | Opening type within transparency | As HC1-01 | Replicates (a) in a second concept |
| HC1-B11 | P01 | Comparison shoppers | A09-H03 (HK-38 "comparing … tonight?") | A09-H01 | Comparison-shopper callout vs "before you order" | Self-relevance of the comparing moment | Good retargeting candidate |
| HC1-B12 | P02 | S1 | A05-H03 (HK-06 "two minutes") | A05-H01 | Time-saving situation vs callout | Decision ease made concrete | "Two minutes" is a situation, not a product claim; review wording |
| HC1-B13 | P02 | S2 | A06-H02 (HK-07 "version that passes") | A06-H01 | Swap framing vs problem question | Contrast without a body before/after (B Cian 2020) | 10-word line |
| HC1-B14 | P02 | S2 | A06-H03 (HK-16 school run) | A06-H01 | Frustration morning vs problem question | Relatable frustration | No child in frame |
| HC1-B15 | P02 | S3 | A07-H02 (HK-02 waistband) | A07-H01 | Problem vs hosting callout | Problem recognition | S6 ~Nov 20–25 |
| HC1-B16 | P02 | S3 | A07-H03 (HK-40 demo-first) — TEST ARM | A07-H01 | Opening type | As HC1-01 | S6; seated frame 1 hides the hem briefly |
| HC1-B17 | P02 | Skeptics | A08-H01 (HK-41) concept, 15 s or 25 s | A05-H01 | Transparency vs outfit formula | Pre-empting objections (ICP-P02 A8) | Natural length 25 s ($8.10); length then co-varies |
| HC1-B18 | P02 | S1/S2 | A08-H02 (HK-23 "check the length first") | A08-H01 | Mistake-avoidance vs "three honest things" | Pre-qualifier on the biggest product risk (length) | Watch length-return requests |
| HC1-B19 | P02 | S1/S2 | A08-H03 (HK-42 "exactly how short", demo-first) — TEST ARM | A08-H01 | Opening type | As HC1-01 | — |
| HC1-B20 | P02 | S2/S1 | A09-H01 (HK-21 two ways) concept | A05-H01 | Versatility vs formula | Use-occasion expansion (D) | **Needs khaki crops**; two-scene drift |
| HC1-B21 | P02 | S2 | A09-H02 (HK-26 sneakers) | A09-H01 | Unexpected use vs two-ways | Relevant surprise (B) | Needs khaki crops |
| HC1-B22 | P02 | S1 | A09-H03 (HK-13 contrarian) | A09-H01 | Contrarian vs two-ways | Expectation violation tied to a product fact (B) | Needs khaki crops |

## 6. What each result would change (decision rules, pre-registered)

- **(a)** If one opening type wins on stop rate and retention at s3 **and** is not worse on ATC/1k in both products,
  adopt it as the default first line for round 2 and test the other type only as a challenger. If the products
  disagree, keep both types and re-test in a second concept (HC1-B10/B16/B19). Report as directional.
- **(b)** If captions-on is not worse on CTR and ATC/1k, switch auto-captions on by default (zero cost). If worse,
  keep off.
- **(c)** Only run once a 15 s ad beats the others on cost per ATC; adopt 25–30 s if its cost per ATC is lower after
  S4 and its hold is not collapsing before the CTA.
- **Concept rows** feed round 2 angle choice; no concept is declared a winner on purchases in cycle 1.
