# HOOK_AND_ARCHETYPE_LIBRARY

**Checkpoint B, Phase 4 (4.0 hooks, 4.1 structures, 4.2 archetypes).** Ember & Clove, prepared 2026-10-25.
Builds on `ATTENTION_PSYCHOLOGY_PLAYBOOK.md` (cited **PB §x**), `TIKTOK_ALGORITHM_INTELLIGENCE.md` (**AI §x**),
`HIGH_PERFORMING_AD_PATTERNS.md` (**HP §x**), the 78-record Top Ads database `ads/creative_database_all.json`
(**DB**), and the ICP reports `reports/icp_P01_…md` / `reports/icp_P02_…md` (**ICP-P01 / ICP-P02**, sections E, F, H).
Nothing in this phase created, published or spent anything. Short version: `HOOK_AND_ARCHETYPE_LIBRARY_summary.md`.

**Evidence categories (Phase 9).** **A** TikTok-documented (often commissioned, method rarely published) ·
**B** peer-reviewed or credible experiment · **C** industry-observed, **including our own Top Ads database** ·
**D** hypothesis or our own arithmetic or judgment. C and D are never stated as fact. Every hook, structure and
archetype below is a **testable proposal (D)** built on the mechanism evidence cited with it.

---

## 0. How to read this library

### 0.1 What the database can and cannot tell us about hooks

- **Sample.** 78 records from TikTok Creative Center Top Ads (US, Women's Clothing, last 180 days, observed
  2026-10-25). One video appears twice under two advertisers (7562141018129399825 = 7565804992105955346, flagged via
  `duplicate_of`). **The only performance signal is CTR rank** (top X%, lower = better). No spend, retention,
  conversion or sales data. Curated winners only (survivorship).
- **Splits used here.** The lead researcher's comparison (HP §2) uses 76 unique ads split at the median CTR rank
  (38 ranked top 1–9%, 38 ranked top 10–51%) and, within the Conversions objective, 18 vs 18. For per-hook tallies I
  keep one copy of the duplicate pair (7565804992105955346) and use the same cut: **better = rank ≤ 0.09, worse =
  rank ≥ 0.10**. Per-category n is 1–11, so **every tally below is C-category, directional, and mostly not
  statistically distinguishable from chance**.
- **Objective confound.** TikTok Shop `product_sales` creator posts make up 25/38 of the better half vs 9/38 of the
  worse half. A hook category that "wins" overall may simply be a TikTok Shop habit. Where it matters I give the
  within-Conversions picture (the objective we will run).
- **Hook coding.** Each ad has one primary `hook_category` and an optional secondary; coding was done by reviewers
  from transcripts and frame sheets (subjective). "Problem identification", "mistake avoidance" and "story-based
  opening" barely occur as primary codes, so for those categories the database is close to silent.

### 0.2 Database tally by hook category (primary code; C, directional)

| Hook category (DB code) | n | Better half (≤0.09) | Median CTR rank | Within Conversions (better/n) | Notes |
|---|---|---|---|---|---|
| Callout of audience | 9 | 6 | 0.07 | 3/5 | Broad situations rank well; narrow problem/body callouts rank low (§2.13) |
| Direct benefit | 9 | 5 | 0.07 | 0/2 | All 5 better-half ones are TikTok Shop posts |
| Social proof | 7 | 5 | 0.07 | 1/2 | **Not usable by us** (no testimonials, no reviews yet) |
| Offer/price | 6 | 4 | 0.055 | 2/4 | Best two are "double discount, ends tonight" scripts: **urgency, banned for us** |
| Curiosity gap | 7 | 3 | 0.12 | 1/5 | Weaker within Conversions |
| Creator discovery | 6 | 3 | 0.105 | 1/1 | All first-person purchase/discovery: must be adapted (§2.11) |
| Visual transformation | 5 | 2 | 0.11 | 0/2 | Mostly shapewear body before/after: **body claims banned for us** |
| Contrarian | 5 | 2 | 0.11 | 1/2 | |
| Trend/sound | 7 | 2 | 0.17 | 0/3 | Needs music: **not available** (owner rule) |
| "Other" (silent look-book / aesthetic try-on) | 11 | 3 | 0.17 | 1/8 | Silent formats cluster low |
| Comparison | 2 | 1 | 0.105 | 0/1 | |
| Unexpected demo / unexpected outcome / problem identification | 1 each | 1 each | 0.05–0.07 | — | n = 1: anecdote only |
| Relatable frustration / mistake avoidance / story | 0 primary | — | — | — | Secondary codes only (see each category) |

Two cross-cutting DB observations that shape the whole library (both C):
- **Dresses rank low and our format is nearly absent.** 8 records are dresses (incl. a two-piece set, an abaya, a
  prom gown); 7 of 8 sit in the worse half, and the exception is a reach-objective prom look-book
  (7593517732454137863, 0.01). Only one dress ad has spoken creator talk (7383349441418870801, 0.12). Only **6 of the
  50 talking ads are ≤ 20 s** (median rank 0.115, vs 0.08 for the 44 longer talking ads). **There is no
  short, spoken, AI-presenter dress ad in the sample**, so nothing here validates or rules out our exact format.
- **Proof on the body and garment numbers recur in better-ranked ads.** Physical tests (squat, stretch, scratch,
  under-outfit) appear in 7/38 better vs 4/38 worse; stated numbers (inseam, length, size, price) in 7/38 vs 3/38
  (e.g., 7553529201560600577, 7446589468725674000, 7532713502415814657). For an **AI presenter, numbers must be
  garment facts** (P02 ≈ 27–28 in long; P01 midi ≈ 44–47 in), never the presenter's height or size, which would be
  invented.

### 0.3 Rules every example line obeys (current owner rules + ICP compliance)

- **Format:** AI-generated video (Seedance 2.5 reference-to-video), AI presenter labelled AI-generated on the
  organic post (AI §1.7), spoken lines + visuals only; **no post-added captions, text, end cards or music.**
- **First spoken line names the buyer by situation**, never by body or health traits. Target ≤ ~8–9 words
  (≈ 3–3.5 s at ~2.5 words/s, D arithmetic; PB §3 rule 2). Where a line runs longer it is marked.
- **Never:** testimonials; "I bought / I've worn it / I own"; fabricated reviews or ratings; urgency, scarcity,
  countdowns; guarantees; "warm"; "100% wool"; before/after **body** claims; "flattering on every body"; "looks
  expensive"; "best seller". **P02 also:** no "soft", no "not itchy", no "up to 3X" / size-range bragging (garment
  bust tops out at 48 in).
- **Allowed product facts.** **P01 cable knit mock-neck midi:** cable knit, mock neck, long sleeves, fitted through
  the hip, ribbed waist, front slit ("easy to move in"), midi (~44–47 in), acrylic-blend knit, $52.99, S–XL, 7 colors
  (Black, Heather Gray, Dark Blue, Caramel, Red, Green, Berry). **P02 slouchy turtleneck rib-knit dress:** folded
  slouchy turtleneck, loose fit, dropped shoulders, chunky rib, mini ~27–28 in (made for tights and boots),
  acrylic/polyester with an angora blend, "cozy" (page wording), $44.99, 7 colors (Gray, White, Khaki, Black, Navy,
  Burgundy, Sky Blue). **Store:** free US shipping on orders over $70 (two P01 = $105.98, two P02 = $89.98), ships in
  about 2–3 weeks (stating this is information, not urgency), 7-day returns (state only as "seven-day returns"; do not
  say "free" or "easy" returns).
- **P01 is fitted.** Do **not** give P01 "doesn't cling / skims" lines. ICP-P01 F4 lists cling-averse shoppers as a
  negative ICP for P01, so the PB §4.1 example line "it skims instead of clinging" (written for the cable midi)
  should be dropped; the "hangs, doesn't cling" idea belongs to **P02 only** (ICP-P02 A3), and even there it must be
  shown, not promised.
- **Every claim must match the live product page and the real garment** (verify fabric, length and colors before
  generation; reject any clip that alters the garment).

### 0.4 Production and cost facts used throughout (D arithmetic)

Seedance 2.5 reference-to-video, 4–30 s per generation, ~$0.324/s at the owner's current discount; 15 s is the
current house length. **6 s ≈ $1.94 · 10 s ≈ $3.24 · 15 s ≈ $4.86 · 20 s ≈ $6.48 · 25 s ≈ $8.10 · 30 s ≈ $9.72.**
Anything over 30 s needs two or more generations joined (45 s ≈ $14.58 before re-rolls), which conflicts with the
"used exactly as delivered" practice and adds presenter/garment continuity risk. Every rejected clip costs the full
price again. Hook tests currently mean regenerating the whole video, so shots 2–4 also change between arms; keep
prompts, references and settings identical outside the opening to limit that confound (§3.6).

---

## 1. Hook library at a glance (34 hooks, 13 categories)

P01 = cable knit midi; P02 = turtleneck sweater dress. Segment codes from ICP-P01/ICP-P02 section E.
★ = in the first-test priority list (summary file).

| ID | Category | Product · segment | Opening line (spoken) |
|---|---|---|---|
| HK-01 ★ | Problem identification | P01 · S1 boot-season | "Own tall boots, but only wear them with jeans?" |
| HK-02 | Problem identification | P02 · S3 holiday eater | "Holiday dinners coming up, and every dress has a waistband?" |
| HK-03 ★ | Problem identification | P02 · S2 pajamas-that-pass | "Living in leggings, but want to look dressed?" |
| HK-04 ★ | Unexpected demonstration | P01 · S1 | "Tall-boot owners, watch what the slit does." |
| HK-05 | Unexpected demonstration | P01 · S1/S3 | "Taking the subway in a fitted midi? Watch this." |
| HK-06 | Unexpected demonstration | P02 · S1 outfit formula | "Getting dressed in two minutes tomorrow? Watch." |
| HK-07 ★ | Visual transformation | P02 · S2 | "Spending Saturday in loungewear? Here's the version that passes." |
| HK-08 | Visual transformation | P01 · S1 | "Got tall boots? Three pieces, one outfit. Watch." |
| HK-09 | Visual transformation | P02 · S1 | "Shopping sweater dresses online? Here's hanger versus worn." |
| HK-10 | Curiosity gap | P01 · S1 | "Tall-boot owners: one detail decides if a midi works." |
| HK-11 | Curiosity gap | P02 · S1 | "Tights this winter? This dress is short on purpose." |
| HK-12 | Contrarian | P01 · S1 | "Own tall boots? Skip the mini sweater dress." |
| HK-13 | Contrarian | P02 · S1 | "Tights season? A sweater dress should be short." |
| HK-14 | Contrarian | P01 · S2 holiday | "Holiday party coming? You don't need a sequin dress." |
| HK-15 | Relatable frustration | P01 · S1/S3 | "Tired of tiny steps in fitted midi dresses?" |
| HK-16 | Relatable frustration | P02 · S2 | "Cold morning, school run, and nothing to throw on?" |
| HK-17 ★ | Direct benefit | P02 · S1 | "Black tights, tall boots, and this. That's the whole outfit." |
| HK-18 | Direct benefit | P01 · S1 | "For tall-boot season: mock neck, midi length, front slit." |
| HK-19 ★ | Direct benefit | P01 · S2 | "Holiday party coming? This is the whole outfit." |
| HK-20 | Product comparison | P01 + P02 · S1 | "Tall boots this winter? Mini or midi, here's both." |
| HK-21 | Product comparison | P02 · S1/S2 | "Errands or dinner out? Same dress, two ways." |
| HK-22 | Mistake avoidance | P01 · S1 | "Wearing a midi with tall boots? Check where the hem lands." |
| HK-23 ★ | Mistake avoidance | P02 · S1/S2 | "Ordering a short sweater dress? Check the length first." |
| HK-24 | Mistake avoidance | P01/P02 · holiday | "Ordering a holiday dress online? Check the ship time first." |
| HK-25 | Unexpected outcome | P02 · S2 | "If turtlenecks feel too formal for weekends, watch this." |
| HK-26 | Unexpected outcome | P02 · S2 | "Saturday errands in a sweater dress? Yes, with sneakers." |
| HK-27 | Creator discovery (adapted) | P01 · S1 | "If you own tall boots, this one's worth a look." |
| HK-28 | Creator discovery (adapted) | P02 · S1 | "Tights-and-boots season, and this is new at Ember & Clove." |
| HK-29 | Story-based opening | P01 · S2 | "First cold Friday, holiday party at eight." |
| HK-30 | Story-based opening | P02 · S2 | "School pickup at three, dinner at seven, one outfit." |
| HK-31 ★ | Callout of audience | P01 · S1 | "Own knee-high boots? This dress is for you." |
| HK-32 | Callout of audience | P02 · S3 | "Hosting a holiday dinner this year? Look at this." |
| HK-33 | Callout of audience | P01 · S3 covered-but-shapely | "Winter date night, and you're done with minis?" |
| HK-34 | Callout of audience | P02 · S4 cling-averse | "Sweater dresses always cling on you? Watch this one hang." |

Categories deliberately **not** used: **social proof** (no reviews exist; fabricated proof banned),
**offer/urgency** (no discount; urgency banned; price and free-shipping facts are used in CTAs instead),
**trend/sound** (needs music; banned). Social proof becomes available only once real, verifiable reviews exist.

---

## 2. Hook library in detail

Field order for each hook: first-frame visual · ideal product characteristics · retention strategy · potential
downside · conversion relevance · testable hypothesis · database examples. Mechanism and evidence are given once per
category. Primary metric names follow AI §6: **stop rate** = 2-s views ÷ impressions; **hold** = 100% views ÷ 2-s
views; **per-second curve** (API); **destination CTR**; **CVR (clicks)** = purchases ÷ destination clicks;
**ATC/1k** = add-to-carts per 1,000 impressions.

### 2.1 Problem identification

**Mechanism.** Self-relevance and problem recognition: self-referenced information is processed more deeply
(**B**, Symons & Johnson 1997), and personal relevance makes viewers judge on argument quality, so the proof that
follows must be strong (**B**, Petty, Cacioppo & Goldman 1981; Burnkrant & Unnava 1995). PB §1 finding 2; PB §2.1
"Self-relevance" row; PB §2.4 "ELM split". Situation-specific problem openers on TikTok are **D**.
**Database.** Only one primary code: 7650512237645168647 (0.05, Conversions) "If your boobs are flat like me…",
which is a **body-trait** opener we cannot copy. In batch 02, an explicit problem was stated or implied in 5 of the
best 8 vs 1 of the worst 8 (7650512237645168647, 7624686771482411016, 7556265760357629968, 7555436904498888705,
7565804992105955346 vs 7559443459519430673). C, n = 16.

**HK-01 ★ "Own tall boots, but only wear them with jeans?"** (P01 · S1 · 9 words ≈ 3.6 s)
- *First frame:* presenter already in the P01 midi with knee-high boots, mid-step toward camera (motion onset), full
  length, plain wall; a folded pair of jeans on a chair edge is the only prop.
- *Ideal product:* a garment that solves a styling problem the viewer already has and can be seen solving it in one
  shot (P01 slit + boots).
- *Retention:* the question opens a small gap that shot 2 closes visually: the slit opening over the boot shaft
  (PB §2.2 "open loops / anticipated payoff", deliver by ~8 s).
- *Downside:* viewers without tall boots swipe (narrower stop rate); the jeans prop can read as the product if it is
  too prominent (PB §2.3 scene complexity).
- *Conversion relevance:* high: maps to the strongest P01 search behaviour ("sweater dress with boots", ICP-P01 H A1,
  evidence Strong).
- *Hypothesis:* HK-01 gives a lower stop rate but higher destination CTR and CVR (clicks) than the generic approved
  opener "Okay, you need to see this sweater dress." (same body, same shots 2–4).
- *DB:* problem-stated pattern above; no boots-specific example. Closest visual: 7441225809438670856 (0.07) opens on
  legs in tights and knee boots.

**HK-02 "Holiday dinners coming up, and every dress has a waistband?"** (P02 · S3 · 10 words ≈ 4 s, slightly long)
- *First frame:* presenter in burgundy P02 with black tights, standing at a set dinner table, mid-turn.
- *Ideal product:* loose, no waist seam (P02).
- *Retention:* shot 2 shows the loose drape from shoulder to hem while she sits down at the table.
- *Downside:* edges toward body talk; keep it about the **garment** (waistbands), never the stomach or eating
  "too much". Time-boxed: Thanksgiving wording only until ~Nov 1–2, "holiday dinners" until ~late Nov (ICP-P02 F3).
- *Conversion relevance:* moderate; dated-event buyers convert if delivery fits (ICP-P02 A4).
- *Hypothesis:* during Nov, HK-02 yields higher CVR (clicks) than HK-17 for the same audience.
- *DB:* none (no holiday-dinner ad in the sample).

**HK-03 ★ "Living in leggings, but want to look dressed?"** (P02 · S2 · 8 words ≈ 3.2 s)
- *First frame:* presenter in P02 (sky blue or khaki), sitting cross-legged on a couch, then standing (motion onset
  at ~0.5 s); leggings visible folded on the couch arm.
- *Ideal product:* loungewear-level ease that reads as an outfit (loose fit, folded turtleneck).
- *Retention:* stand-up reveals the slouch and dropped shoulders; next shot adds boots and coat at the door.
- *Downside:* "comfort" is subjective; do not substitute "soft" or "not itchy" (banned) when the comfort claim needs
  support; let the loose drape carry it.
- *Conversion relevance:* moderate–strong (ICP-P02 A1, repeated forum language).
- *Hypothesis:* HK-03 beats HK-17 on CVR (clicks) among the same broad audience (tests comfort vs outfit framing,
  ICP-P02 A1 vs A2).
- *DB:* 7553529201560600577 (0.05) "These are the kind of joggers I want to live in all fall" (comfort framing,
  TikTok Shop, first-person, which we can't copy).

### 2.2 Unexpected product demonstration

**Mechanism.** Orienting to motion onset (**B**, Abrams & Christ 2003) plus relevant surprise: unexpected relevant
information improves attitudes, irrelevant surprise hurts (**B**, Lee & Mason 1999; Teixeira, Wedel & Pieters 2012);
seeing the product in use triggers mental simulation (**B**, Elder & Krishna 2012). PB §1 findings 3–4; PB §2.1
"Orienting" and "Pattern interruption" rows; PB §2.2 "Visual demonstration".
**Database.** Physical tests are a recurring better-half feature (C): squat/stretch test 7364141843464781840
(0.03), scratch and scissors test 7441225809438670856 (0.07), Sharpie lift test 7565804992105955346 (0.07; duplicate
7562141018129399825 at 0.09), hold-up-then-wear 7272762760945041409 (0.04). All are on functional garments.

**HK-04 ★ "Tall-boot owners, watch what the slit does."** (P01 · S1 · 7 words ≈ 2.8 s)
- *First frame:* low-angle full length, presenter mid-stride in P01 + knee-high boots; the front slit is already
  opening over the boot shaft at 0 s.
- *Ideal product:* a feature that only reveals itself in motion (slit, drape, stretch).
- *Retention:* repeat the stride from a second angle (side) at ~4 s, then a close-up of slit + boot at ~8 s; each cut
  adds information (PB §3 rule 4).
- *Downside:* AI cloth physics may render the slit wrong or too high (truth risk: slit height is an ICP objection);
  reject any clip where the slit differs from the real garment.
- *Conversion relevance:* high; the slit is the stated reason the midi works with boots (ICP-P01 A1/A5).
- *Hypothesis:* a demonstration-first opener (HK-04) raises stop rate and second-3 retention versus the callout-first
  HK-31 (PB H-AP-03/H-AP-06 logic).
- *DB:* physical-test examples above.

**HK-05 "Taking the subway in a fitted midi? Watch this."** (P01 · S1/S3 · 9 words ≈ 3.6 s)
- *First frame:* presenter stepping up a staircase (subway or apartment stairs) in P01 + boots, full stride.
- *Ideal product:* fitted garments with a movement fix (P01 front slit).
- *Retention:* stairs → walk → sit, each one a "can it do this" beat.
- *Downside:* stairs and sitting are hard for AI motion (limb and hem errors); "subway" narrows to urban viewers.
- *Conversion relevance:* moderate; answers the "tiny steps" objection (ICP-P01 A5) but is a proof beat more than a
  lead reason (ICP-P01 notes A5 works best mid-video).
- *Hypothesis:* HK-05 lifts hold (100% ÷ 2-s) versus HK-04 but not destination CTR.
- *DB:* none specific.

**HK-06 "Getting dressed in two minutes tomorrow? Watch."** (P02 · S1 · 7 words ≈ 2.8 s)
- *First frame:* presenter already in black tights, pulling P02 over her head (dress visible at 0 s), single take.
- *Ideal product:* one-piece outfit that goes on in one move (P02).
- *Retention:* one continuous take: dress on → fold the turtleneck → step into boots → coat; the viewer waits for
  the finished look (anticipated payoff).
- *Downside:* "two minutes" is a time claim; it is a styling illustration, not a measured fact, so keep it loose or
  say "tomorrow morning" instead. Pulling a garment over the head is a known hard case for video models.
- *Conversion relevance:* moderate–strong (outfit-formula, ICP-P02 A2).
- *Hypothesis:* a single-take dressing demo (0 cuts) holds viewers as well as the 4-shot version (tests HP §3.3
  slow-cutting pattern).
- *DB:* single-take ads in the better half: 7553529201560600577 (0.05, 0 cuts), 7513237149484351489 (0.02, 0 cuts),
  7544583507542163457 (0.06, 0 cuts).

### 2.3 Visual transformation

**Mechanism.** Contrast makes change visible; progression (step-by-step) visuals were more credible than
before/after for skeptical consumers, while before/after works when a fast, realistic result is the point
(**B**, Cian, Longoni & Krishna 2020, non-apparel). PB §2.1 "Contrast and immediate transformation" row; PB §2.2
"Progressive revelation" and "Before/after"; PB H-AP-07.
**Database.** 5 primary: 7272762760945041409 (0.04), 7494632329088876561 (0.06), 7242174026750885890 (0.11),
7512394875825913872 (0.11), 7555964643937910800 (0.26); 0 of 2 within Conversions in the better half. Almost all are
**shapewear or bra body before/afters, which we may not make**. Our transformations change the **outfit**, never the
body (same presenter, same lighting, same framing).

**HK-07 ★ "Spending Saturday in loungewear? Here's the version that passes."** (P02 · S2 · 9 words ≈ 3.6 s)
- *First frame:* presenter in grey loungewear holding P02 up to camera (product visible at 0 s); hard cut at ~2 s to
  her in P02 + tights in the same spot and pose.
- *Ideal product:* one-piece items whose "after" is obviously more dressed but equally relaxed (P02).
- *Retention:* the cut is the payoff; shots 3–4 add boots/coat and the door ("passes" outside).
- *Downside:* reads as before/after; it must be an honest outfit swap (no body change, no slimming). Identity drift
  between the two generations/shots is an AI risk; use the same presenter reference.
- *Conversion relevance:* moderate–strong (ICP-P02 A1).
- *Hypothesis:* the outfit-swap version of the comfort angle (HK-07) beats the no-swap version (HK-03) on stop rate
  and CTR.
- *DB:* transformation examples above (as format only).

**HK-08 "Got tall boots? Three pieces, one outfit. Watch."** (P01 · S1 · 8 words ≈ 3.2 s)
- *First frame:* presenter in P01 (caramel), boots in hand, about to step in.
- *Ideal product:* garments that are the centre of a formula (P01 + boots + coat).
- *Retention:* progression: dress → boots → coat, one step per shot (PB §2.2), each step announced in ≤ 5 words.
- *Downside:* three outfit states in 15 s is dense; the coat is a second product we don't sell (keep it neutral and
  brief, or drop it).
- *Conversion relevance:* high for S1 (ICP-P01 A1).
- *Hypothesis:* progression (HK-08) beats a single swap cut on CTR (PB H-AP-07).
- *DB:* none (no outfit-build progression ad in the sample).

**HK-09 "Shopping sweater dresses online? Here's hanger versus worn."** (P02 · S1 · 9 words ≈ 3.6 s)
- *First frame:* P02 on a hanger held at arm's length (flat, shapeless), then the cut to worn with tights at ~2 s.
- *Ideal product:* knits that look flat on a hanger and come alive on a body (P02 slouch).
- *Retention:* the "worn" shot answers the implicit "what does it actually look like?"
- *Downside:* the hanger shot may lower stop rate (static, less salient); PB §2.1 favours on-body first frames.
- *Conversion relevance:* moderate; addresses "looks different on a real body" anxiety.
- *Hypothesis:* HK-09 has a lower stop rate than HK-17 but similar CVR (clicks).
- *DB:* hold-up-then-wear openings: 7272762760945041409 (0.04), 7295590434121449474 (0.12), 7369124804521115666
  (0.19). Mixed ranks.

### 2.4 Curiosity gap

**Mechanism.** Curiosity as a felt information gap (**B**, Loewenstein 1994); curiosity raises memory for the answer
(**B**, Kang et al. 2009) and for incidental material shown during it (**B**, Gruber et al. 2014); moderate gaps work
best (**B**, Menon & Soman 2002; Park et al. 2015). Clickbait framing did not reliably raise clicks and lowers
credibility (**B**, Penn State studies). PB §1 finding 4; PB §2.1 "Curiosity" row.
**Database.** 7 primary; 3 in the better half, median 0.12; within Conversions only 1 of 5 better
(7548014767798845448, 0.07, "why are these called jelly bras?"). Worse: 7416283009659371536 (0.12, "I bought three
of these… let me tell you why", banned phrasing), 7618493078241230856 (0.14), 7545142337405714440 (0.18),
7441503397314805768 (0.22). C: curiosity looks **weaker** once objective is held.

**HK-10 "Tall-boot owners: one detail decides if a midi works."** (P01 · S1 · 9 words ≈ 3.6 s)
- *First frame:* P01 + boots, walking; the camera already framed hem-to-boot.
- *Ideal product:* a product whose answer to the gap is a visible feature (slit position, hem over boot).
- *Retention:* the gap is closed at ~5–7 s ("it's the slit: it opens right where the boot starts"), then shown again
  from the side. Gruber: dress on screen during the gap.
- *Downside:* if the reveal is late or vague it is bait; "decides if a midi works" is opinion and must stay styling
  advice.
- *Conversion relevance:* moderate; the answer is a reason to buy only if the slit/boot payoff is clear.
- *Hypothesis:* HK-10 raises 100% view rate versus HK-31 but **not** destination CTR (curiosity = entertainment
  unless the answer sells; PB §2.1 test column).
- *DB:* curiosity examples above.

**HK-11 "Tights this winter? This dress is short on purpose."** (P02 · S1 · 9 words ≈ 3.6 s)
- *First frame:* full length, P02 over black tights, boots; hem clearly mid-thigh.
- *Ideal product:* products with an apparent drawback that is actually the design (short length).
- *Retention:* "why on purpose?" → "it's made to go over tights and boots" → show the three-piece look.
- *Downside:* draws attention to shortness for people who wanted a longer dress (that is also honest pre-qualifying;
  ICP-P02 A8).
- *Conversion relevance:* moderate; reduces length-based returns (D).
- *Hypothesis:* HK-11 lowers CTR slightly but raises CVR (clicks) versus HK-17 (pre-qualifying effect).
- *DB:* none specific.

### 2.5 Contrarian statement

**Mechanism.** Expectation violation draws attention (**B**, Itti & Baldi 2009; Teixeira et al. 2012), but only
**relevant** surprise helps attitudes (**B**, Lee & Mason 1999). Contrarian claims about other products need to be
true and non-disparaging (D, compliance). PB §2.1 "Pattern interruption" row.
**Database.** 5 primary; 2 better (7441225809438670856, 0.07, "Don't be fooled by other brands…"; 7437867036929851408,
0.08, "3 compelling reasons to ditch your office pants"), 3 worse (7406218796128632833 0.11, 7380329994080534544 0.15
"Goodbye skinny jeans", 7559443459519430673 0.15). Median 0.11. The better two pair the contrarian line with a
physical test or a listicle of reasons.

**HK-12 "Own tall boots? Skip the mini sweater dress."** (P01 · S1 · 8 words ≈ 3.2 s)
- *First frame:* P01 midi + knee-high boots, mid-stride; slit open.
- *Ideal product:* a product that is the alternative to a common default (midi vs mini with tall boots).
- *Retention:* the "why" follows at once: "a midi with a slit shows the boot and covers the rest."
- *Downside:* **cannibalises P02** (our mini). Use only in P01-only ad groups or replace with HK-20 (both products).
  Opinion, not a factual claim about other products.
- *Conversion relevance:* moderate–high for S1.
- *Hypothesis:* HK-12 beats HK-31 on stop rate with equal CTR.
- *DB:* contrarian examples above.

**HK-13 "Tights season? A sweater dress should be short."** (P02 · S1 · 8 words ≈ 3.2 s)
- *First frame:* P02 with black tights and boots, mid-turn.
- *Ideal product:* same logic as HK-11, phrased as a stance.
- *Retention:* "Here's why: tights, boots, and a short slouchy knit. Done."
- *Downside:* cannibalises P01 in mixed ad groups (mirror of HK-12).
- *Conversion relevance:* moderate.
- *Hypothesis:* HK-13 ≈ HK-11 on CTR (stance vs explanation framing of the same idea).
- *DB:* as above.

**HK-14 "Holiday party coming? You don't need a sequin dress."** (P01 · S2 · 9 words ≈ 3.6 s)
- *First frame:* P01 in Red or Berry, doorway with simple holiday lights, coat over arm.
- *Ideal product:* festive-but-covered alternative to party dresses.
- *Retention:* mock neck, long sleeves, cable texture close-up, walk out the door.
- *Downside:* "is it too casual?" is the S2 objection; this line raises it. Time-boxed (~mid-Nov, ICP-P01 A2).
- *Conversion relevance:* moderate–strong in season.
- *Hypothesis:* HK-14 beats HK-19 on stop rate during Nov.
- *DB:* none (no holiday ad in the sample).

### 2.6 Relatable frustration

**Mechanism.** Shared negative experience creates identification and self-relevance (**B** for self-relevance;
PB §2.1). Caution: emotion that comes **before** the product did not lift purchase intent (**B**, Teixeira, Picard &
el Kaliouby 2014), so the frustration must be about the garment problem and the dress must be on screen from frame 1.
PB §1 finding 3; PB §2.4.
**Database.** No primary code; secondary "relatable" codes are all in the worse half: 7242174026750885890 (0.11),
7408075217421844481 (0.10), 7199572939681972225 (0.17), 7594524368035315729 (0.26). C, n = 4, weak signal
**against** meme-style frustration.

**HK-15 "Tired of tiny steps in fitted midi dresses?"** (P01 · S1/S3 · 8 words ≈ 3.2 s)
- *First frame:* P01 mid-stride, slit open, full length.
- *Ideal product:* a product that removes a known physical annoyance (slit).
- *Retention:* pay off within 3 s with a long stride; then boots and texture.
- *Downside:* names a problem most scrollers aren't thinking about (ICP-P01 notes A5 is better as a proof beat).
- *Conversion relevance:* moderate.
- *Hypothesis:* HK-15 < HK-04 on stop rate (problem framing vs demo framing of the same visual).
- *DB:* none direct.

**HK-16 "Cold morning, school run, and nothing to throw on?"** (P02 · S2 · 9 words ≈ 3.6 s)
- *First frame:* presenter grabbing keys at a front door already in P02 + tights + boots.
- *Ideal product:* one-piece, low-effort outfits.
- *Retention:* rewind-style second shot (pulling it on), then out the door.
- *Downside:* "cold" is fine as a situation, but never imply the dress is warm (banned claim).
- *Conversion relevance:* moderate.
- *Hypothesis:* HK-16 ≈ HK-03 on CVR (clicks); tests situation wording within the comfort angle.
- *DB:* none direct.

### 2.7 Direct benefit

**Mechanism.** Early, clear value proposition: TikTok advises the proposition in the first 3 s (**A**, Jun 2025)
and reports most ad impact in the first 2–6 s (**A**, 2023, no method); strong arguments persuade high-relevance
viewers (**B**, ELM). PB §1 finding 1; PB §2.1 platform facts; PB §3 rules 1 and 7.
**Database.** 9 primary; 5 better, median 0.07, **but all five better ones are TikTok Shop posts**; within
Conversions 0 of 2 better (7610109647022653447 0.10, 7338465339167490050 0.15); the brand-voice launch line
7444641956200693768 ("Meet our newest…", 0.33) is the lowest-ranked English ad. C: first-person/creator-voice
benefits rank well; brand-voice benefits rank low.

**HK-17 ★ "Black tights, tall boots, and this. That's the whole outfit."** (P02 · S1 · 10 words ≈ 4 s)
- *First frame:* presenter holding black tights and boots up beside the P02 she is wearing (ICP-P02 A2 creative).
- *Ideal product:* the centre piece of a formula; the formula items are props.
- *Retention:* pull-on/step-in shots; side profile showing hem over tights; CTA with price.
- *Downside:* the situation is implied by the items rather than stated ("if you wear tights and boots…"); **owner to
  confirm it satisfies the callout rule**. 10 words: trim to "Black tights, tall boots, this. Whole outfit." if
  second-3 retention drops.
- *Conversion relevance:* high (ICP-P02 A2, evidence Strong, the P02 lead angle).
- *Hypothesis:* HK-17 gives lower cost per ATC than HK-03 (outfit vs comfort framing).
- *DB:* direct-benefit creator lines 7497887208898347009 (0.02), 7553529201560600577 (0.05), 7446589468725674000
  (0.06) (all TikTok Shop).

**HK-18 "For tall-boot season: mock neck, midi length, front slit."** (P01 · S1 · 9 words ≈ 3.6 s)
- *First frame:* P01 full length, slow turn, boots on.
- *Ideal product:* products whose spec list is itself the pitch.
- *Retention:* one shot per feature (neck close-up, length with boots, slit in stride).
- *Downside:* feature lists read as brand voice, which ranks low in the DB; keep it conversational.
- *Conversion relevance:* moderate (argument quality for high-relevance viewers).
- *Hypothesis:* HK-18 < HK-01 on destination CTR (spec framing vs problem framing).
- *DB:* brand-voice examples ranked low: 7444641956200693768 (0.33), 7338465339167490050 (0.15).

**HK-19 ★ "Holiday party coming? This is the whole outfit."** (P01 · S2 · 8 words ≈ 3.2 s)
- *First frame:* P01 in Red, presenter putting on an earring at a mirror with simple holiday lights, boots on.
- *Ideal product:* festive colour, covered silhouette, one piece.
- *Retention:* mock neck/sleeves close-up → walk to the door with the slit opening → CTA with honest ship time.
- *Downside:* time-boxed (run until ~Nov 15–20); must not imply fast delivery.
- *Conversion relevance:* moderate–strong in season (ICP-P01 A2).
- *Hypothesis:* in the first half of Nov, HK-19 achieves CVR (clicks) ≥ HK-01.
- *DB:* none (no holiday ad).

### 2.8 Product comparison

**Mechanism.** Side-by-side contrast makes attributes easier to judge. **No comparison-specific source was reviewed
in Checkpoint B** (D); nearest playbook support is the contrast row (**B**, Cian et al. 2020) and relevant-surprise
logic (PB §2.1). Comparisons against named competitors carry claim and trademark risk (D, compliance); we compare our
own products or styling choices only.
**Database.** 2 primary: 7470799387607334928 (0.06, dupe vs a named brand jacket), 7610788623265071120 (0.15,
"take your pick" slides); secondary comparisons 7441225809438670856 (0.07), 7437867036929851408 (0.08); price
comparison 7397326487299719185 (0.08, "$80 vs ~$30"). C, n small.

**HK-20 "Tall boots this winter? Mini or midi, here's both."** (P01 + P02 · S1 · 9 words ≈ 3.6 s)
- *First frame:* presenter in P01 midi + boots; hard cut at ~2.5 s to P02 mini + tights + same boots.
- *Ideal product:* two of our own products serving one situation.
- *Retention:* alternate twice; finish on "pick your length".
- *Downside:* two garments double the AI fidelity risk; split interest may lower CVR; the landing page must make both
  easy to reach (collection page rather than one PDP).
- *Conversion relevance:* moderate; may raise AOV via the free-shipping threshold (D).
- *Hypothesis:* HK-20 raises CTR versus either single-product boots hook but lowers CVR (clicks) per product page.
- *DB:* comparison examples above.

**HK-21 "Errands or dinner out? Same dress, two ways."** (P02 · S1/S2 · 7 words ≈ 2.8 s)
- *First frame:* P02 with sneakers on a sidewalk; cut to P02 with tall boots and a coat at a restaurant door.
- *Ideal product:* versatile items; styling-range proof.
- *Retention:* the second look is the payoff; optional third look.
- *Downside:* more scenes = more generation risk; drifts toward "styling content" without a reason to buy.
- *Conversion relevance:* moderate (cost-per-wear logic, D).
- *Hypothesis:* HK-21 increases hold but not CTR versus HK-17.
- *DB:* styling listicle 7295590434121449474 (0.12).

### 2.9 Mistake avoidance

**Mechanism.** Loss/regret framing draws attention to a costly error. **Loss-framing literature was not reviewed in
Checkpoint B** (D); supported indirectly by ELM (high-relevance viewers process the argument, **B**) and by the
ICP evidence that length, fit and delivery are the top regrets (ICP-P02 A8; ICP-P01 G1).
**Database.** One secondary code: 7406218796128632833 (0.11, "If your leggings claim to… but you don't have to do
all these movements"). Near-silent.

**HK-22 "Wearing a midi with tall boots? Check where the hem lands."** (P01 · S1 · 10 words ≈ 4 s, slightly long)
- *First frame:* tight shot of hem and boot shaft while walking.
- *Ideal product:* products where a styling detail is the purchase decision (midi length vs boot height).
- *Retention:* explain in one line, show it from two angles.
- *Downside:* the AI's hem position is simulated; if the real length on a given height differs, the "proof" misleads.
  Pair with the real length (~44–47 in) on the page and avoid promising it hits a particular point on every body.
- *Conversion relevance:* moderate; pre-qualifies on length.
- *Hypothesis:* HK-22 lowers CTR but improves CVR (clicks) versus HK-31.
- *DB:* none.

**HK-23 ★ "Ordering a short sweater dress? Check the length first."** (P02 · S1/S2 · 9 words ≈ 3.6 s)
- *First frame:* presenter holding P02 against herself at full length, hem at mid-thigh, tights on.
- *Ideal product:* products with a common return reason that can be disclosed up front.
- *Retention:* "It's about twenty-seven inches, so it's a tights-and-boots dress" → pull on → walk.
- *Downside:* honest disclosure may lower CTR (ICP-P02 A8 objection). A tape-measure shot is risky with AI (numbers
  on the tape will be garbled); state the number in speech instead.
- *Conversion relevance:* moderate; likely fewer length returns (D).
- *Hypothesis:* HK-23 gives CPA no worse than HK-17 and fewer length-related return requests per order (ICP-P02 A8).
- *DB:* garment numbers appear in better-ranked ads (§0.2): 7553529201560600577, 7446589468725674000.

**HK-24 "Ordering a holiday dress online? Check the ship time first."** (P01 or P02 · holiday · 10 words ≈ 4 s)
- *First frame:* presenter in P01 Red at a doorway with a wrapped gift box on a side table (prop only).
- *Ideal product:* dated-occasion buys with a long delivery window.
- *Retention:* "This one ships in about two to three weeks, so order with time to spare" → festive styling.
- *Downside:* must remain **information, not urgency**: no "before it's too late", "last chance" or dates that imply
  a guarantee (ICP-P02 A4 CTA note). Expect lower CTR; it is a trust test.
- *Conversion relevance:* moderate; may cut "where is my order" refunds (ICP-P01 A2).
- *Hypothesis:* adding the honest ship-time line costs little CTR but lowers "where is my order" refund and
  chargeback requests per order (D; needs order-level tracking).
- *DB:* none.

### 2.10 Unexpected outcome

**Mechanism.** Violated expectation (**B**, Teixeira et al. 2012; Itti & Baldi 2009), helpful only when the outcome
is about the product (**B**, Lee & Mason 1999). PB §1 finding 4.
**Database.** 7380169202270552065 (0.06, "This bodysuit erased my waist", **body claim, not transferable**);
secondary 7569577101978140689 (0.07, "so cheap… feels expensive", **the "looks expensive" angle is banned**,
ICP-P01 A10). The category's examples in the DB are mostly ones we cannot use.

**HK-25 "If turtlenecks feel too formal for weekends, watch this."** (P02 · S2 · 9 words ≈ 3.6 s)
- *First frame:* P02 with sneakers, presenter slumping onto a couch arm, folded turtleneck visible.
- *Ideal product:* items that break a category stereotype (turtleneck = stiff).
- *Retention:* show the fold and slouch close-up, then out the door.
- *Downside:* the stereotype may not be widely held; weak if the viewer has no turtleneck opinion.
- *Conversion relevance:* low–moderate.
- *Hypothesis:* HK-25 < HK-03 on CTR.
- *DB:* see above.

**HK-26 "Saturday errands in a sweater dress? Yes, with sneakers."** (P02 · S2 · 9 words ≈ 3.6 s)
- *First frame:* P02 + tights + white sneakers, walking out of a grocery store.
- *Ideal product:* items that stretch beyond their obvious occasion.
- *Retention:* sneakers → swap to boots for evening (second look).
- *Downside:* weakens the strongest angle (boots formula); styling content risk.
- *Conversion relevance:* low–moderate; possible new-use expansion.
- *Hypothesis:* HK-26 raises hold but not CTR versus HK-17.
- *DB:* none.

### 2.11 Creator discovery (adapted for a labelled AI presenter)

**Mechanism.** Source cues and peer discovery: for lower-involvement viewers, likable, relatable sources persuade
through cues (**B**, ELM; Petty et al. 1983). TikTok's creator lifts (+70% CTR, direct-address and "you" lifts) were
measured on **human** creators (**A**, no method; PB §5 rows) and may not transfer to a labelled AI presenter
(PB §6 open question 2; NIQ 2024 AI-ad memory finding, **C**). PB §1 finding 9.
**Database.** 6 primary; 3 better, median 0.105; every one is a first-person purchase or discovery ("just came in
the mail", "I may have just discovered…", "I also got this dress on the TikTok shop"): 7534113546473488385 (0.07),
7511731759499804689 (0.08), 7343186537940090882 (0.09), 7295590434121449474 (0.12), 7383349441418870801 (0.12),
7559443428460691457 (0.12). **That framing is banned for us** (fabricated experience). The adaptation is
"show-and-tell" by a presenter who never claims to have bought or worn the dress.

**HK-27 "If you own tall boots, this one's worth a look."** (P01 · S1 · 10 words ≈ 4 s)
- *First frame:* presenter in P01 + boots stepping into frame, eye contact, light smile.
- *Ideal product:* items that benefit from a casual, peer-like recommendation tone.
- *Retention:* conversational tour (neck, length, slit) at a relaxed pace, few cuts.
- *Downside:* without a real purchase story, the "discovery" lift may not exist; risk of sounding like an endorsement
  by a person who does not exist (keep the AI label visible; never "I found", "I got", "my favorite").
- *Conversion relevance:* unknown for AI presenters (D).
- *Hypothesis:* HK-27 performs no better than HK-31 on CTR (tests whether discovery tone adds anything without a real
  creator).
- *DB:* discovery examples above (format reference only).

**HK-28 "Tights-and-boots season, and this is new at Ember & Clove."** (P02 · S1 · 10 words ≈ 4 s)
- *First frame:* P02 + tights + boots, walking toward camera.
- *Ideal product:* new arrivals; a young store needing brand recall.
- *Retention:* brand said at 0–3 s, then the outfit demo.
- *Downside:* brand early raised skips in Google's analysis (**C**, 2015) and TikTok advises subtle branding in the
  hook (**A**, 2023); brand-voice openers rank low in the DB (7444641956200693768, 0.33).
- *Conversion relevance:* low–moderate short-term; may help branded search later (D).
- *Hypothesis:* brand in the first line lowers second-3 retention versus brand at ~8 s (PB H-AP-08).
- *DB:* 7444641956200693768 (0.33), 7338465339167490050 (0.15).

### 2.12 Story-based opening

**Mechanism.** Narrative transportation reduces counter-arguing (**B**, Green & Brock 2000); identifiable characters,
an imaginable plot and verisimilitude drive it (**B**, van Laer et al. 2014 meta-analysis). TikTok reports "story"
ads gain watch time (+16%, **A**, no method). In 15 s only a micro-story fits (PB §2.2 "Story").
**Database.** No ad coded as story-based. Nearest: the sceptical-buyer story 7427043163971387399 (0.27) and the
explainer 7441491158156541969 (0.08). Silent.

**HK-29 "First cold Friday, holiday party at eight."** (P01 · S2 · 7 words ≈ 2.8 s)
- *First frame:* presenter at a mirror in P01 Red, boots on, fastening an earring; clock or window dusk light.
- *Ideal product:* items tied to a moment the viewer can picture.
- *Retention:* micro-plot: getting ready → coat → out the door, the slit opening on the stride; narration in present
  tense.
- *Downside:* the scenario must be clearly a scenario, not presented as the AI presenter's real life or a customer's
  experience; no "last year I wore…".
- *Conversion relevance:* moderate in season; strong recall if the brand is spoken mid-ad (PB §3 rule 9).
- *Hypothesis:* HK-29 raises hold versus HK-19 with equal CTR.
- *DB:* none.

**HK-30 "School pickup at three, dinner at seven, one outfit."** (P02 · S2 · 9 words ≈ 3.6 s)
- *First frame:* presenter in P02 + tights + sneakers at a car door (daylight).
- *Ideal product:* versatile one-piece outfits.
- *Retention:* time-skip to evening: same dress, boots and coat, restaurant door.
- *Downside:* two settings and lighting states (AI continuity risk); assumes a parent viewer.
- *Conversion relevance:* moderate (comfort + versatility).
- *Hypothesis:* HK-30 ≈ HK-03 on CVR (clicks), higher hold.
- *DB:* none.

### 2.13 Callout of audience (the owner's current rule)

**Mechanism.** Self-relevance captures attention and deepens processing (**B**, Symons & Johnson 1997; own-name
capture is real but partial, ~a third of people, Moray 1959 / Wood & Cowan 1995); matched messages lifted clicks and
purchases in large Facebook field tests (**B**, Matz et al. 2017, baseline disputed); a creator saying "you" in the
first 5 s linked to higher purchase intent (**A**, 2023, no method). Situation callouts on TikTok specifically are
**D**. Extreme self-referencing can backfire (**B**, Meyers-Levy & Peracchio 1996). PB §1 finding 2; PB §2.1
"Self-relevance" row; PB §4.2; PB H-AP-02 and H-AP-05.
**Database.** Callout present in the hook: **9/38 better vs 8/38 worse (Fisher p = 1.0): no overall difference**
(HP §2). Within Conversions (18 vs 18): 7 vs 3 (p ≈ 0.26, not significant). The pattern inside is consistent (HP §3.5):
**broad situational callouts rank well** (nurses 7458213187293741072, 0.07; uniform wearers 7532513869211664391, 0.07;
school staff 7397326487299719185, 0.08; "basic t-shirts for leggings" 7555436904498888705, 0.06); **narrow
problem or body/health callouts rank low** (back brace / scoliosis 7503897804079890433, 0.20; big-bust strapless
7527583394600878096, 0.20; back conditions 7441503397314805768, 0.22). The owner's "situation, never body or health"
rule matches the better-ranked kind. First spoken lines were not short in either half (median ≈ 13 words better vs
≈ 12 worse, from transcripts), so the DB does not show that short openers win; that remains PB H-AP-02.

**HK-31 ★ "Own knee-high boots? This dress is for you."** (P01 · S1 · 8 words ≈ 3.2 s)
- *First frame:* P01 + knee-high boots, mid-step, full length, direct gaze (PB §4.1 shot 1).
- *Ideal product:* products with a clear "who it's for" situation.
- *Retention:* hand-off to proof at 3 s (texture, slit in stride, length with boots); strong arguments must follow
  (ELM).
- *Downside:* narrows the audience; muted viewers miss the words unless the boots are visible (they are).
- *Conversion relevance:* high in theory (qualified traffic), unproven (DB shows no CTR difference).
- *Hypothesis:* the 8-word version keeps more viewers at second 3 than the 11-word original "If you own knee-high
  boots, this dress is for you." (PB H-AP-02). Also the **control arm** for most hook tests.
- *DB:* broad situational examples above.

**HK-32 "Hosting a holiday dinner this year? Look at this."** (P02 · S3 · 9 words ≈ 3.6 s)
- *First frame:* presenter setting plates at a holiday table in burgundy P02 + black tights.
- *Ideal product:* occasion-fit pieces.
- *Retention:* sits, reaches across the table, stands: loose drape throughout.
- *Downside:* time-boxed; hosts may want dressier options.
- *Conversion relevance:* moderate in season.
- *Hypothesis:* HK-32 ≈ HK-02 on CVR; tests "hosting" vs "attending" situation.
- *DB:* none.

**HK-33 "Winter date night, and you're done with minis?"** (P01 · S3 · 8 words ≈ 3.2 s)
- *First frame:* evening light, presenter in P01 Black turning to show the side profile; slit on the stride.
- *Ideal product:* covered-but-shapely silhouette (P01).
- *Retention:* side turn → mock neck close-up → walk with slit.
- *Downside:* "shows your shape" proof is body-centred; keep lines about the **dress** ("fitted through the hip"),
  never about the viewer's body. Cling-averse viewers should (and will) swipe.
- *Conversion relevance:* moderate (ICP-P01 A3, counter-evidence noted).
- *Hypothesis:* HK-33 has lower CTR than HK-31 but similar CVR (clicks) among women it stops.
- *DB:* none.

**HK-34 "Sweater dresses always cling on you? Watch this one hang."** (P02 · S4 · 10 words ≈ 4 s)
- *First frame:* side profile, presenter mid-turn in P02; fabric visibly falling away from the body.
- *Ideal product:* loose, dropped-shoulder knits (P02 only, never P01).
- *Retention:* turn, walk, pinch the fabric away from the waist (ICP-P02 A3).
- *Downside:* borderline with the body-trait rule (it describes a garment experience, not a body; **owner to
  confirm**). One AI body type cannot prove fit across bodies; the AI may render drape that the real garment doesn't
  have. Never "hides your tummy" or "flattering on everyone".
- *Conversion relevance:* moderate; strong pain, unverified product fit (ICP-P02 F4, rank 2–3).
- *Hypothesis:* HK-34 gives the highest stop rate among cling-averse viewers but returns must be watched (fit
  returns per order).
- *DB:* narrow fit-problem callouts ranked low (7527583394600878096, 0.20); treat as higher-risk.

---

## 3. Video structure library (4.1)

**All durations are experimental categories (D), not optimal lengths.** Segment timings are proposals built on PB §3
(rules), PB §4.1 (default 15 s timeline) and the DB patterns in HP §2–3. Word budgets assume ~2.5 words/s (D).

### 3.1 What the database says about length and pacing (C, directional)

| Finding (HP §2) | Better half | Worse half | Within Conversions |
|---|---|---|---|
| Median duration | 36.8 s | 23.6 s | 35.9 s vs 16.9 s |
| Median cuts per 10 s | 1.67 | 2.65 (p ≈ 0.04) | 1.6 vs 2.6 |
| Spoken narration | — | — | 14/18 vs 8/18 (p ≈ 0.09) |
| Product clearly visible by 1 s | 36/38 | 30/38 (p ≈ 0.09) | — |

**What it does imply for our 15 s format.**
1. **Don't cut faster.** Better-ranked ads cut *less* (≈1.6 per 10 s); four of one batch's best 8 were single takes.
   Our 4 shots in 15 s (3 cuts, ≈2 per 10 s) is inside the range; 3 shots or a single take are also defensible.
   Consistent with PB §1 finding 5 (no "reset every N s" evidence; B- evidence that higher cut frequency reduced
   engagement).
2. **Keep the presenter talking and the dress on the body from frame 1.** Both are directional DB patterns and match
   A/B evidence (PB §1 findings 1, 3).
3. **Use the time for proof, not for more scenes.** Longer better-ranked ads spend their time on demonstrations,
   Q&A and garment numbers, not on extra outfits.

**What it does not imply.**
1. **It does not show that longer causes higher CTR.** Length is entangled with talking-UGC formats: only 6 of 50
   talking ads are ≤ 20 s, while the short ads in the worse half are mostly **silent** look-books, trend edits and
   memes (e.g., 7468263629185155090 10.1 s, 7555964643937910800 12.1 s, 7570021374824644628 10.7 s,
   7582977430706765825 14.5 s). Our ads are short **and** talking, a combination the sample barely contains.
2. **CTR rank is not cost per purchase.** Longer ads may click better and still cost more per sale; the DB has no
   sales data (PB §2.4).
3. **Completion rates fall with length** (more seconds to drop off), and TikTok's organic audits weight full and
   repeated watches (AI §1.2, B). For a Sales objective the optimisation event decides delivery (AI §1.3, A), so
   completion is a diagnostic, not the goal.
4. **AI-specific risks grow with length (D):** presenter and garment drift, more spoken claims to verify, more chance
   of a hand, hem or slit artefact.

**Cost of testing longer (D arithmetic).** A 25 s generation ≈ $8.10 and 30 s ≈ $9.72 versus $4.86 for 15 s, i.e.
**+$3.24 to +$4.86 per attempt**, doubled or tripled by re-rolls. That is small next to the media spend needed to read
any test (≈ $25/day per ad group, AI §1.4), so **generation cost is not the reason to avoid one longer test; the
reasons to wait are learning value and continuity risk.** Recommendation (D): after a 15 s winner exists, make one
25–30 s version of it (same angle, same opening) and compare cost per ATC. Over 30 s needs joined generations, which
conflicts with "used exactly as delivered".

### 3.2 6-second ads

Use: stop-rate probes, retargeting reminders, cheapest hook tests ($1.94). TikTok-commissioned lab work found
exposures ≤ 6 s still gave 38% of the recall of 20 s+ exposures (**A**, MediaScience 2021, n = 343).
DB: three very short ads rank well, all **silent** on-body clips (7564324162404941832 6.8 s 0.02;
7272762760945041409 6.9 s 0.04; 7535245334970204177 7.8 s 0.07, all with partial text or none) (C).

| Segment | What happens | Why |
|---|---|---|
| 0–2.5 s | Dress on body in motion (stride with slit / pull-on over tights); spoken callout ≤ 6 words | Product = hook; motion onset (PB §2.1, B) |
| 2.5–5 s | One proof shot (slit over boot, hem over tights) with ≤ 6 words | One idea per shot (PB §3 rule 4) |
| 5–6 s | Price or "link's right here" | Minimal CTA |

Limits: ~12–15 words total; no room for brand + price + proof; without on-screen text a muted viewer gets the
visual only (PB §4.3). Best for P02 HK-17 or P01 HK-04 as a reminder to people who already saw the 15 s.

### 3.3 10–15-second ads (house format)

Use: first-round angle and hook tests. PB §4.1 timeline, refined with DB pacing:

| Segment | What happens | Why |
|---|---|---|
| 0–3 s | Shot 1: dress worn, in motion, the callout situation visible (boots/tights/table); spoken situation callout ≤ 8–9 words; direct gaze | Proposition in first 3 s (A); self-relevance (B); muted viewers see the situation |
| 3–7.5 s | Shot 2: the strongest proof (slit opening in stride; loose drape when sitting; texture close-up); gaze and hands on the dress | Relevant demonstration builds purchase intent (B); gaze cues attention to product (B) |
| 7.5–11.5 s | Shot 3: payoff of the hook's promise (finished outfit, walk to camera); **"Ember & Clove" spoken once** | Brand pulse mid-ad, the only brand cue without text (B, PB §1 finding 8) |
| 11.5–15 s | Shot 4: price and CTA ("It's forty-four ninety-nine. Seven colors, link's right here."); optional honest ship-time line instead of price for holiday angles | Price matches Shopify; CTA |

~30–38 words. Variants: **3 shots** (merge 2 and 3) or **single take** (AR-16) for the cut-pace test; **10 s** = drop
shot 3 and say the brand in the CTA. Cost $3.24–4.86.

### 3.4 20–30-second ads

Use: angles that need explanation or objection handling (transparency, education, outfit build), and the
"longer version of the winner" test. One generation up to 30 s ($6.48–9.72).

| Segment | What happens | Why |
|---|---|---|
| 0–3 s | Same opening as the 15 s version (keeps the hook comparable) | Isolates length as the variable |
| 3–10 s | Demonstration 1 (movement: stride/sit/turn) with one spoken fact per shot | Mental simulation (B) |
| 10–17 s | Demonstration 2 or objection answer: length stated in inches, fabric stated plainly, ship time | Argument quality for high-relevance viewers (B); pre-qualifies (D) |
| 17–24 s | Styling payoff (boots/coat; second colour if consistent) + brand spoken | Payoff + brand pulse |
| 24–30 s | Price, free shipping over $70 (two dresses), CTA | AOV lever is a real policy (ICP-P01 A8) |

~50–75 words. Keep ≤ 2 cuts per 10 s (≈ 4–6 shots). Main risk: garment drift across a longer clip; check every
shot against the real dress.

### 3.5 30–45-second ads

Use: talking explainers and Q&A, the length most better-ranked Conversions ads ran (~36 s median, C). **Requires
joining two generations** (e.g., 2 × ~20 s ≈ $12.96; 30 + 15 s ≈ $14.58) or a future model limit increase.

| Segment | What happens | Why |
|---|---|---|
| 0–3 s | Situation callout with dress on body | As above |
| 3–12 s | "Here's what it is": three spoken facts, each with its own visual (neck, length with boots, slit) | Strong arguments (B) |
| 12–25 s | Movement and styling: walk, sit, add boots/coat; spoken styling tip (educational frame) | Education that sells (PB §2.2) |
| 25–35 s | Honest fine print: length in inches, fabric, ship time, seven-day returns | Trust; return reduction (D) |
| 35–45 s | Brand + price + CTA | |

Feasible only if the owner accepts joining clips; continuity of presenter, room and garment between generations is
the main failure mode (D). Low priority until a 25–30 s test shows a length benefit.

### 3.6 Longer explanatory creative (45–90 s)

Justified only for (a) a sizing/length explainer that answers many objections at once, or (b) a "three ways to wear
it" styling video for warm audiences. DB precedents are all human creators talking: 7441491158156541969 (76 s, 0.08),
7397326487299719185 (91 s, 0.08), 7618493078241230856 (86 s, 0.14), 7565804992105955346 (102 s, 0.07). For us this
means ≥ 3 joined generations (~$15–30 before re-rolls), heavy continuity risk, and a long monologue from a synthetic
presenter (NIQ found AI ads weaker on memory, C). **Not recommended now; reconsider only with real footage** (Phase 5).

**Hook-test hygiene (applies to all lengths, D).** Because each hook variant is a full regeneration, shots 2–4 change
too. Keep the reference images, scene prompt, seed (if exposed) and shot list identical across arms and change only
the opening line and first-shot action; log both prompts with the ad ID. If the owner ever allows joining clips,
generating one body and several separate openings would give a cleaner hook test.

---

## 4. Creative archetypes (4.2)

18 archetypes. "Feasibility with AI generation" is our judgment (D): **Feasible** = one Seedance generation can
plausibly show it truthfully; **Feasible with limits** = possible but with named fidelity or compliance risks;
**Not feasible without real footage** = the persuasive element depends on something an AI clip cannot truthfully
show. Metrics per AI §6.

### AR-01 Immediate product payoff

| Field | Content |
|---|---|
| Customer mindset | Solution-aware scroller; already likes sweater-dress outfits; decides on looks in a second |
| Opening hook | HK-04 or HK-17: the finished look at 0 s, line names the situation |
| Visual structure | Shot 1 finished outfit in motion → shot 2 detail → shot 3 walk to camera → shot 4 CTA (or 6 s version) |
| Narration structure | Situation (≤ 8 words) → one feature line → brand → price/CTA |
| Product reveal | 0 s, worn, full length |
| Persuasion mechanism | Visual salience + mental simulation (B); "that's my outfit" relevance |
| CTA | "Seven colors, link's right here." |
| Most important metric | Stop rate, then destination CTR |
| Likely failure mode | Looks like every other try-on; no reason to choose this one over a cheaper look-alike (ICP-P01 C6) |
| AI feasibility | **Feasible** |
| ICP fit | P01-S1, P02-S1 |

### AR-02 Situation callout + proof (owner's control format)

| Field | Content |
|---|---|
| Customer mindset | Problem- or situation-aware: owns tall boots / lives in leggings / has a party date |
| Opening hook | HK-31, HK-01, HK-03, HK-32 |
| Visual structure | PB §4.1 four-shot timeline; situation visible in shot 1 (boots, tights, table) |
| Narration structure | Callout → proof claims tied to visuals → payoff → brand → price/CTA |
| Product reveal | 0 s, worn |
| Persuasion mechanism | Self-relevance raises scrutiny, so concrete, checkable proof follows (ELM, B) |
| CTA | "Pick your color on the page." |
| Most important metric | CVR (clicks) and ATC/1k (qualified traffic), stop rate as diagnostic |
| Likely failure mode | Callout runs past 3 s; proof is vague ("so cute") so the raised scrutiny hurts |
| AI feasibility | **Feasible** |
| ICP fit | All priority segments (one segment per ad) |

### AR-03 Problem → frustration → solution

| Field | Content |
|---|---|
| Customer mindset | Problem-aware: jeans-and-boots on repeat; waistband dread at holiday dinners |
| Opening hook | HK-01, HK-02, HK-15 |
| Visual structure | Dress on from frame 1 (never a long "problem" scene first) → problem named in words → solution shown in motion |
| Narration structure | Problem question (≤ 9 words) → "Here's the fix" → 2 proofs → CTA |
| Product reveal | 0 s visually; verbally at ~3 s |
| Persuasion mechanism | Problem recognition + relevance (B); emotion only after the product is on screen (B, Teixeira 2014) |
| CTA | "Link's right here." |
| Most important metric | Destination CTR |
| Likely failure mode | Leading with the problem visually (product late) — the DB's slowest reveals ranked low (HP §3.1) |
| AI feasibility | **Feasible** (problem stays verbal; no "before" body scene) |
| ICP fit | P01-S1, P02-S3, P02-S2 |

### AR-04 Real-life product demonstration

| Field | Content |
|---|---|
| Customer mindset | Evaluating: "can I walk/sit/move in it?", "where does the slit open?" |
| Opening hook | HK-04, HK-05, HK-15 |
| Visual structure | Movement tests: stride, stairs, sit-and-stand, turn; each shot one test |
| Narration structure | "Watch what it does" → name each test as it happens → result line → CTA |
| Product reveal | 0 s in motion |
| Persuasion mechanism | Relevant demonstration and mental simulation (B); physical proof recurs in better-ranked DB ads (C) |
| CTA | "Seven colors on the page." |
| Most important metric | Destination CTR; per-second curve around each test |
| Likely failure mode | AI renders the physics wrong (slit too high, hem riding up, impossible drape), which is both unconvincing and untruthful |
| AI feasibility | **Feasible with limits**: simple strides are fine; sitting, stairs and fabric tugs need careful review; any "test" must reflect the real garment, so verify against a physical sample before claiming a result |
| ICP fit | P01-S1, P01-S3 |

### AR-05 Outfit build / progression

| Field | Content |
|---|---|
| Customer mindset | Outfit-formula seeker: wants a decided look |
| Opening hook | HK-08, HK-17, HK-06 |
| Visual structure | Dress → tights/boots → coat, one step per shot; ends on the full look walking |
| Narration structure | Formula stated up front ("Black tights, tall boots, and this.") → each piece named as added → "That's the outfit" → CTA |
| Product reveal | 0 s (dress already on or held) |
| Persuasion mechanism | Progression is more credible than a single before/after for skeptics (B, Cian 2020); decision ease |
| CTA | "It's forty-four ninety-nine. Pick your color." |
| Most important metric | Cost per ATC |
| Likely failure mode | Too many states for 15 s; boots/coat steal attention (props we don't sell) |
| AI feasibility | **Feasible with limits**: dressing actions (pulling on, stepping into boots) are hard for video models; cut between states rather than showing the whole action |
| ICP fit | P02-S1 (lead), P01-S1 |

### AR-06 Honest outfit swap ("pajamas that pass")

| Field | Content |
|---|---|
| Customer mindset | Comfort-first; wants to look dressed without effort |
| Opening hook | HK-07, HK-03 |
| Visual structure | Loungewear (holding the dress) → hard cut to the same person in the dress, same spot → out the door |
| Narration structure | Situation → "Here's the version that passes" → loose fit, folded turtleneck → CTA |
| Product reveal | 0 s in hand; worn at ~2 s |
| Persuasion mechanism | Contrast / before-after of the outfit when the result is fast and realistic (B, Cian 2020) |
| CTA | "Seven colors, link's right here." |
| Most important metric | Stop rate and destination CTR |
| Likely failure mode | Reads as a body before/after (compliance) or the presenter's face/body changes between shots |
| AI feasibility | **Feasible with limits**: identity consistency across the cut; must be same body, lighting, framing |
| ICP fit | P02-S2 |

### AR-07 Common mistake correction

| Field | Content |
|---|---|
| Customer mindset | About to buy something like this; worried about getting length or timing wrong |
| Opening hook | HK-22, HK-23, HK-24 |
| Visual structure | Mistake named over the dress worn → the correct choice shown (hem/boot line, hem over tights) → fact stated → CTA |
| Narration structure | "Check X first" → the fact (length in inches / ship time) → why it matters → CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Loss/regret framing (D in this review) + strong argument quality (B) |
| CTA | "Length and sizes are on the page." |
| Most important metric | CVR (clicks); return requests per order (later) |
| Likely failure mode | Sounds like a warning about our own product and lowers CTR more than it raises CVR |
| AI feasibility | **Feasible** if the facts are spoken; a tape-measure close-up is **not feasible without real footage** (AI garbles numbers and can't prove the real length) |
| ICP fit | P02-S1/S2, P01-S2 (timing) |

### AR-08 Comparison challenge

| Field | Content |
|---|---|
| Customer mindset | Choosing between two looks |
| Opening hook | HK-20, HK-21 |
| Visual structure | Look A → look B → A → B, alternating; same presenter and location |
| Narration structure | Question → one difference per cut → "pick your length/style" CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Side-by-side contrast (D; nearest B Cian 2020); choice between our own options rather than whether to buy |
| CTA | "Both are on the page." |
| Most important metric | Destination CTR and AOV |
| Likely failure mode | Split attention; viewer chooses neither; double the garment-fidelity risk |
| AI feasibility | **Feasible with limits** for our own two products; comparison against competitor products is **not feasible without real footage** (and carries claim risk) |
| ICP fit | P01-S1 + P02-S1 |

### AR-09 Unexpected use case

| Field | Content |
|---|---|
| Customer mindset | Likes the look but thinks "where would I wear it?" |
| Opening hook | HK-26, HK-25 |
| Visual structure | Unexpected setting first (sneakers, errands) → expected setting (boots, evening) |
| Narration structure | "Yes, with sneakers" → why it works → second look → CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Relevant surprise (B); expanding use occasions (D) |
| CTA | "Seven colors on the page." |
| Most important metric | Hold, then destination CTR |
| Likely failure mode | Entertaining styling content with no buying reason; dilutes the boots angle |
| AI feasibility | **Feasible** (two settings raise continuity risk; keep to one location if possible) |
| ICP fit | P02-S2 |

### AR-10 Mini-story

| Field | Content |
|---|---|
| Customer mindset | Has an upcoming moment (party, pickup-then-dinner) |
| Opening hook | HK-29, HK-30 |
| Visual structure | Getting ready → leaving → arriving (three beats) |
| Narration structure | Present-tense scene-setting line → two short beats → brand → CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Narrative transportation, believable situation (B) |
| CTA | "Link's right here." |
| Most important metric | Hold (100% ÷ 2-s) and CTR |
| Likely failure mode | Story overshadows the dress; or it is mistaken for a real person's experience (must be plainly a scenario) |
| AI feasibility | **Feasible with limits**: multiple scenes and lighting changes in one 15 s generation are prone to drift |
| ICP fit | P01-S2, P02-S2 |

### AR-11 Educational demonstration

| Field | Content |
|---|---|
| Customer mindset | Wants to learn how to wear a midi with tall boots / how to style a short sweater dress |
| Opening hook | HK-10, HK-22, HK-11 |
| Visual structure | Tip stated → shown on the dress → second tip → full look |
| Narration structure | "Here's the trick" → tip 1 → tip 2 → brand → CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Education that sells: strong arguments for high-relevance viewers (B); curiosity closed by the product (B) |
| CTA | "The dress is on the page." |
| Most important metric | Hold and destination CTR |
| Likely failure mode | Generic styling advice that sells boots more than the dress |
| AI feasibility | **Feasible** |
| ICP fit | P01-S1, P02-S1 |

### AR-12 Reaction-driven demonstration

| Field | Content |
|---|---|
| Customer mindset | Persuaded by other people's reactions |
| Opening hook | Reveal to a second person ("Getting ready for dinner? Here's the reaction test.") |
| Visual structure | Presenter walks out in the dress → second person reacts → close-up of the dress |
| Narration structure | Set-up → reaction → product facts → CTA |
| Product reveal | ~1–2 s |
| Persuasion mechanism | Social proof via reaction (C; DB comedy/partner-reaction ad 7545142337405714440 ranked 0.18) |
| CTA | "Link's right here." |
| Most important metric | Stop rate |
| Likely failure mode | A synthetic person's reaction is fabricated social proof (close to a fake testimonial); viewers distrust it |
| AI feasibility | **Not feasible without real footage** (a scripted reaction from a generated person is fabricated social proof) |
| ICP fit | — (do not run under current rules) |

### AR-13 Creator discovery (AI-adapted show-and-tell)

| Field | Content |
|---|---|
| Customer mindset | Browsing; responds to peer recommendations |
| Opening hook | HK-27, HK-28 |
| Visual structure | Relaxed tour of the dress, few cuts (single take or 2 shots) |
| Narration structure | "Worth a look if…" → three features → brand → CTA; no "I found / I got / my favorite" |
| Product reveal | 0 s |
| Persuasion mechanism | Source likability cues for low-involvement viewers (B, ELM); human-creator lifts may not transfer (A measured on humans; NIQ C) |
| CTA | "Seven colors, link's right here." |
| Most important metric | Destination CTR vs AR-02 |
| Likely failure mode | Without a real person's experience the discovery tone is empty; or the line slips into implied ownership (banned) |
| AI feasibility | **Feasible with limits** (compliance wording) |
| ICP fit | P01-S1, P02-S1 |

### AR-14 Three honest things (transparency)

| Field | Content |
|---|---|
| Customer mindset | Skeptical of ad stores and AI ads (ICP-P02 A8, D7) |
| Opening hook | "Before you order this sweater dress, three honest things." (ICP-P02 A8; also HK-23) |
| Visual structure | One shot per fact (length on body, fabric close-up, presenter at the door), then the full look |
| Narration structure | "One: it's short, about twenty-seven inches, so it's a tights-and-boots dress. Two: it's an acrylic and polyester knit with an angora blend. Three: it ships in about two to three weeks." → "Still want it? Seven colors." |
| Product reveal | 0 s |
| Persuasion mechanism | Pre-empting objections; honesty as differentiation (D; pain evidence R in ICP) |
| CTA | "Seven colors, forty-four ninety-nine." |
| Most important metric | CVR (clicks) and refunds/returns per order |
| Likely failure mode | Lower CTR without a CVR gain; the "angora" mention invites itch questions (do not answer with "not itchy") |
| AI feasibility | **Feasible** (facts are spoken; visuals only illustrate). Needs ~20–25 s to say naturally (≈ $6.48–8.10) |
| ICP fit | P02-S1/S2 (also adaptable to P01: length, fabric, slit height, ship time) |

### AR-15 Occasion outfit (holiday, time-boxed)

| Field | Content |
|---|---|
| Customer mindset | Has a dated event; worried about arrival and dress code |
| Opening hook | HK-19, HK-14, HK-32, HK-02 |
| Visual structure | Getting ready with simple holiday cues → walk/sit at table → door |
| Narration structure | Occasion callout → festive colour + covered silhouette (P01) or nothing tight at the waist (P02) → honest ship time → CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Dated-goal relevance (B self-relevance; ICP evidence moderate–strong) |
| CTA | "It ships in about two to three weeks, so order with time to spare. Link's right here." |
| Most important metric | CVR (clicks) within the window |
| Likely failure mode | Runs too late (delivery misses the event → refunds); "is it dressy enough?" not answered |
| AI feasibility | **Feasible** (keep set dressing simple; Red/Berry/Burgundy colour fidelity must be checked) |
| ICP fit | P01-S2 (until ~Nov 15–20), P02-S3 (Thanksgiving wording until ~Nov 1–2) |

### AR-16 Single-take walk-and-talk

| Field | Content |
|---|---|
| Customer mindset | Any; tests pacing rather than message |
| Opening hook | Any AR-02 callout |
| Visual structure | One continuous shot: presenter walks toward camera, turns, gestures at details; 0 cuts |
| Narration structure | Same script as the 4-shot control |
| Product reveal | 0 s |
| Persuasion mechanism | Lower load, natural UGC feel; DB: better-ranked ads cut less, several were single takes (C) |
| CTA | Same as control |
| Most important metric | Per-second curve and hold vs the 4-shot control |
| Likely failure mode | Details (texture, slit) too small without a close-up; monotony after ~8 s |
| AI feasibility | **Feasible** (arguably easier for the model than multi-shot) |
| ICP fit | Any (P01-S1 first, since stride and slit read well in one take) |

### AR-17 One dress, three ways (styling listicle)

| Field | Content |
|---|---|
| Customer mindset | Wants value per piece; plans several occasions |
| Opening hook | HK-21 ("Same dress, two ways") or "Three plans this week, one dress." |
| Visual structure | Look 1 → 2 → 3 (sneakers / boots / boots + coat) |
| Narration structure | Count-up structure ("One… two… three…") → CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Versatility / cost-per-wear (D); listicle structure (DB 7295590434121449474, 0.12; 7437867036929851408, 0.08) |
| CTA | "Seven colors on the page." |
| Most important metric | Hold and CTR |
| Likely failure mode | Each look gets ~4 s, too little proof; three scenes in one generation drift |
| AI feasibility | **Feasible with limits** (prefer 20–30 s; or one location with accessory swaps) |
| ICP fit | P02-S1/S2 |

### AR-18 Question answered (search-question explainer)

| Field | Content |
|---|---|
| Customer mindset | Has a specific question people actually search ("is a sweater dress OK for a Christmas party?", "how long should a sweater dress be with boots?", ICP-P01 D1 / ICP-P02 D8 autocomplete) |
| Opening hook | "Wondering if a sweater dress works for a holiday party?" (situation + question) |
| Visual structure | Question over the dress worn → answer demonstrated → full look |
| Narration structure | Question → direct answer → two supporting facts → CTA |
| Product reveal | 0 s |
| Persuasion mechanism | Curiosity closed by the product (B); relevance from real search demand ([V] in ICP) |
| CTA | "Link's right here." |
| Most important metric | Destination CTR |
| Likely failure mode | Faking a "reply to comment" sticker (would need post-added text and a real comment; both unavailable) |
| AI feasibility | **Feasible** (spoken question only; never imply a real viewer asked unless one did) |
| ICP fit | P01-S2, P01-S1 |

### 4.1 Archetype feasibility summary

| Feasibility | Archetypes |
|---|---|
| Feasible | AR-01, AR-02, AR-03, AR-07 (spoken facts), AR-09, AR-11, AR-14, AR-15, AR-16, AR-18 |
| Feasible with limits | AR-04 (physics), AR-05 (dressing actions), AR-06 (identity across cut), AR-08 (two garments), AR-10 (multi-scene), AR-13 (wording), AR-17 (multi-look) |
| Not feasible without real footage | AR-12 (reaction = fabricated social proof); the measured-length element of AR-07; competitor comparisons in AR-08 |

---

## 5. Uncertainties and next steps

1. **Nothing here is validated for our format.** The DB has no AI-presenter ads, almost no short talking ads, and only
   8 dresses (§0.2). Our first tests are the evidence.
2. **Hook categories overlap.** A callout can also be a problem statement or a demo; tests should vary one feature
   at a time (opening type, length, or cut count), not whole hook categories at once.
3. **CTR rank ≠ sales.** Judge hooks on CVR (clicks), cost per ATC and, when volume allows, cost per purchase
   alongside Shopify orders (AI §6, §9).
4. **Rule questions for the owner** (callout-first for every ad, no on-screen text, 15 s cap) are listed as options
   in the summary file.
5. **Next (Checkpoint C/D):** turn the priority hooks and archetypes into concrete scripts and Seedance prompts per
   product (Phase 6.3) and register each comparison as a hypothesis (Phase 7.1).
