# Barbed wire necklace — what the winning TikTok videos do (2026-10-29)

Owner: "You should study the winning ads from kalodata to build the ads".
Source: Kalodata top videos for the barbed wire choker (`research/kalodata/barbwire_choker_top_videos_2026-10-29.csv`),
the top 5 by 30-day revenue, downloaded 2026-10-29 (`research/kalodata/videos/barbwire_2026-10-29/`, not in git, delete
by 2026-11-28). Transcripts (faster-whisper), cut detection and frame sheets: `.../study/`. All 5 are paid-boosted
creator videos for another seller's choker (The M Jewelers). **Studied for format only; their footage, faces and words are
not reused.**

| # | Creator | 30-day revenue | Views | Length | Cuts | Speech | Opening | On-screen text |
|---|---|---|---|---|---|---|---|---|
| 1 | bonemeeal | $12,462 | 687k | 8.5 s | 0 | sound only ("They're gonna eat me alive") | chin-to-chest, fingers on the chain, dim room with LED light | "barbwire necklace fire" |
| 2 | marissaglesinger7 | $7,370 | 394k | 12.0 s | 0 | none (music) | car selfie, hand lifting the chain, head tilt | "Badass barbed wire choker necklace" |
| 3 | alyssareneeltts | $5,092 | 362k | 20.1 s | 1 | talking, 4 words/s | at home, pointing at the necklace | "Barbwire choker 🖤" |
| 4 | yourpassportpal | $5,092 | 277k | 32.3 s | 1 | two-person chat | cafe patio, friend points at it | none |
| 5 | omg_its_emy | $4,824 | 275k | 19.9 s | 2 | talking, 4 words/s | necklace dangled right across the lens | none |

## The pattern

1. **One handheld selfie take, not a slideshow.** 0–2 cuts in every winner. The camera moves a little, the person moves.
2. **The necklace is worn and touched from the first frame.** A fingertip lifts, traces or points at the chain in every
   video. Framing is chin-to-chest, close enough to see the barbs.
3. **The two biggest earners are short, silent vibe clips:** 8.5 s and 12 s, music or a sound, no talking, and one short
   lowercase text label naming the product. Together they made more than #3–#5 combined.
4. **A real, ordinary place:** a dark bedroom with LED light, a parked car, home, a cafe patio. Casual tees.
5. **Layered** with other chains in 4 of 5.
6. **Hook moves:** the necklace swung across the lens (#5); a friend reaching for it, "is that barbed wire?" (#4).
7. **What the talkers say** (#3–#5): edgy but dainty/feminine; it doesn't poke; adjustable / has an extender; wears it
   in the shower and to sleep; won't tarnish; "most asked about". These are first-person product claims.

## What we can and can't copy

- **Copy:** the format (one continuous selfie take, chin-to-chest, finger on the chain, real place, layering, short
  text label, music), the length (8–12 s), the dangle hook.
- **Can't copy:** testimonials ("I got this three weeks ago", "I never take it off") break the owner rule. Claims
  about our necklace (doesn't hurt, shower-safe, won't tarnish, adjustable) are unverified until a sample arrives. The
  "edgy but dainty" idea is a style description, so it's fine.
- **Our people are AI and labelled as AI** (fictional, from our own pictures). Talking-head versions wait until a sample
  confirms what can be said.

## Ads built from this (V-series)

10-second vertical AI clips (Higgsfield Seedance 2.5 reference-to-video via `scripts/hf_video_batch.py`, prompts in
`jobs_video_winners.json`, references = our own fictional model pictures + the clean necklace photo), one continuous take
each, silent (music is picked in TikTok Ads Manager). `scripts/text_label.py` makes a 1080x1920 clean version and a
version with a short white label near the top. **Adding the label is an edit, so the label versions need the owner's OK.**

| Ad | Copies the format of | Person / place | Label | Status |
|---|---|---|---|---|
| EC_TT_BW_V1_CAR | #2 car selfie | our car-selfie woman | barbed wire necklace | made, checked: barbs and curb chain match the reference |
| EC_TT_BW_V2_NIGHT | #1 dark room, LED light | same woman, night | edgy but dainty | made, checked: opens chin-to-chest, pulls back to her face |
| EC_TT_BW_V3_DANGLE | #5 dangle hook | our bedroom woman | wait for it | **not made**: Higgsfield API balance too low |
| EC_TT_BW_V4_PATIO | #4 patio, pointing | our patio woman | is that barbed wire? | **not made**: Higgsfield API balance too low |

Rerun after a top-up (skips what exists):
`python -I scripts/hf_video_batch.py research/ads/tiktok/product_tests/ec_product_test_02_barbed_wire/jobs_video_winners.json data/media_generated/tiktok_test_02_barbed_wire/video_winners`
