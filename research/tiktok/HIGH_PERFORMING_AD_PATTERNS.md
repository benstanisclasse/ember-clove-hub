# HIGH_PERFORMING_AD_PATTERNS

**Checkpoint B, Phase 3.** Ember & Clove, 2026-10-25.
Database: `TIKTOK_AD_CREATIVE_INTELLIGENCE_DATABASE.csv` (one row per ad, Phase 3.2 framework), full records in
`ads/creative_database_all.json`, batch notes in `ads/analysis/breakdowns_0*_summary.md`, per-ad transcripts and
frame sheets in `ads/analysis/`.

## 1. The sample and what it can and cannot show

| Item | Value |
|---|---|
| Source | TikTok Creative Center **Top Ads**, region US, industry Women's Clothing, last 180 days, observed 2026-10-25 (signed in) |
| Ads | 78 collected; **76 unique** (2 are the same video from two advertisers); 56 with English speech; 6 with Spanish/Arabic/Russian/German/Malay text or speech |
| Categories | Mostly bras, shapewear, leggings/joggers, jeans, tops; **only 4 dresses** |
| Objectives | Conversions 36, Product sales (TikTok Shop) 34, other 6 |
| Performance data | **CTR rank only** (TikTok's "Top X% CTR"); likes; budget level. **No spend, conversions, retention or sales** |
| Method | Every ad downloaded (owner-approved), transcribed (faster-whisper base.en), frame-sampled (0, 0.5, 1, 1.5, 2, 3 s, then every 2 s), scene cuts detected (calibrated by eye), then broken down by reviewers who looked at every frame sheet |

**Limits that matter:**
- **Curated, survivorship-biased sample.** Every ad is a TikTok-chosen "top ad". We compare better- and
  worse-*ranked* top ads, not winners against failures. Nothing here proves a tactic *caused* performance.
- **CTR is not purchases.** A high CTR rank can come from curiosity or offers that don't convert (playbook §2.4).
- **Confounders:** objective (TikTok Shop "product sales" posts dominate the better half), budget level, category,
  language and creator account. Where possible I compare **within the Conversions objective** (n = 36), which is
  the objective we will run.
- Statistics are Fisher exact / Mann-Whitney on small groups. Treat p-values as a guide to which patterns are worth
  testing, not as confirmation. Evidence category for every finding below: **C (industry-observed, our own
  observational sample)**.

## 2. What separates better- from worse-ranked ads

Split at the median CTR rank (top 9.5%). "Better" = 38 ads ranked top 1–9.5%; "worse" = 38 ranked top 10–51%.

| Pattern | Better half | Worse half | Within Conversions only (18 vs 18) | Strength |
|---|---|---|---|---|
| Objective = TikTok Shop product sales | 25/38 | 9/38 | n/a | **Big confounder** |
| Creator/UGC formats (talking, try-on, haul, demo) | 31/38 | 18/38 (p≈0.004) | 12/18 vs 7/18 (p≈0.18) | Weakens once objective is held |
| **Spoken narration** (creator talk or voiceover) | 28/38 | 22/38 | **14/18 vs 8/18 (p≈0.09)** | Directional, consistent across batches |
| **Product clearly visible within 1 s** | 36/38 | 30/38 (p≈0.09) | — | Directional |
| **Cut pace** (median cuts per 10 s) | **1.7** | 2.7 (p≈0.04) | **1.6 vs 2.6** | Directional, holds within objective |
| Duration (median) | 36.8 s | 23.6 s | **35.9 s vs 16.9 s** | Directional; tied to talking formats |
| Brand/studio look-books and slideshows | 1/38 | 6/38 | 1/18 vs 3/18 | Directional |
| Silent outfit edits (transitions, colourways, posing, memes) | rare | 5 of the worst 8 in one batch | — | Directional |
| Audience callout in the hook | 9/38 | 8/38 | — | **No difference** (see §3) |
| On-screen text (full or partial) | 23/38 | 17/38 | 12/18 vs 9/18 | Small; full captions rare (~10%) in both |
| Offer or price in the video | 11/38 | 7/38 | — | Small; best two ads were offers, but a 65%-off ad ranked low |
| Likes | — | — | — | **Do not track CTR rank** (841 likes at top 1%; 120k likes at top 22%) |
| AI-generated presenter | 0 | 0 | — | No AI ads identifiable in the sample |

## 3. Patterns worth acting on (with the caveats)

1. **Show the garment on a body from the first frame.** Every best-8 ad in two of three batches shows the product
   at 0 s; the slowest reveals (15 s after a talking intro) rank near the bottom. Matches TikTok's own guidance
   that most recall impact lands in the first 6 s (A, Creative Codes PDF) and the playbook's first-frame rule.
   **Our try-on ads already do this from shot 1** (the cable knit ad opens on the dress held up; the new
   "boots" script opens on her already wearing it). Keep it.
2. **A person talking beats a silent montage.** Spoken creator narration is more common in better-ranked
   conversion ads (14/18 vs 8/18), and silent "outfit edits" cluster in the worse half. **Our format (presenter
   speaking to camera) fits this.**
3. **Slower pacing ranked better.** Better-ranked ads cut about 1.6–1.7 times per 10 s versus 2.6–2.7; four of the
   best 8 in one batch were single takes. This matches the playbook (no evidence for "reset every N seconds";
   fast cutting can lower engagement). **Our 4 shots in 15 s ≈ 2 cuts per 10 s is within range**; don't add cuts.
4. **Proof on the body, not claims.** Better-ranked ads show something physical: squat/see-through tests, fitting
   into jeans, a stretch, a before/after of fit. Worse-ranked ones lean on brand voice, feature lists and end cards.
   For us the equivalent is **showing** the slit while walking, the length with boots, the slouch of the
   turtleneck. Claims we can't show stay out (no "warm", no body-shaping).
5. **Callouts: broad situations, not narrow problems.** Callout hooks don't move CTR rank on average (9 vs 8), but
   the pattern inside them is clear: broad situational callouts (nurses, uniform wearers) sat at top 7%, while
   narrow problem callouts (scoliosis/back-brace, big-bust strapless) sat in the worst 8. **Our callouts (own tall
   boots, holiday party, live in leggings) are broad situations, which is the safer kind.** The owner rule stands;
   the data doesn't show it lifts CTR by itself, so we should test it (callout vs. statement hook).
6. **Longer talking ads ranked better within conversions (≈36 s vs ≈17 s).** This is probably the talking-UGC
   effect rather than length itself, and CTR rank says nothing about cost per purchase. Still, it is the one
   finding that questions our fixed 15 s length. A 25–30 s Seedance generation costs ~$8–10. **Worth one test
   later, not a change now.**
7. **Dresses are under-represented and ranked low here (4 ads).** Functional "problem-solving" garments (shapewear,
   bras, leggings, jeans with fit issues) dominate the top. That is a warning: a knit dress has a weaker built-in
   problem than shapewear, so **the angle (boots outfit, holiday outfit, comfort that looks dressed) has to supply
   the reason to buy.** That supports the ICP-driven angles.
8. **Offers help some ads, not reliably.** The two best-ranked ads were "double discount, ends tonight" scripts,
   but we can't use fake urgency, and a 65%-off ad ranked low. **No change; we have no discount to promote.**

## 4. What we cannot conclude

- Whether any pattern **causes** a higher CTR, and whether higher CTR means **cheaper purchases**.
- Anything about **retention curves** (Creative Center analytics pages wouldn't open for these ads).
- How **AI presenters** perform: none in the sample. Our ads are an untested format against this benchmark.
- Anything specific to **knit dresses** (4 dress ads only).
- Effects of **music** (audio not classified reliably) or **sound-off viewing**.

## 5. Implications for the first Ember & Clove tests

- Keep: product on body from frame 1, presenter speaking, 3–4 shots per 15 s, physical demonstration of the
  dress's real features, broad situational callouts.
- Test, don't assume: callout vs. statement opening; a 25–30 s version of the best performer; 3–5 words of
  on-screen text vs. none (owner currently says no text; see playbook H-AP-01).
- Measure with our own per-second retention curve and CTR (destination), and judge on cost per add-to-cart and
  purchase, not likes (likes don't track CTR rank, let alone sales).
