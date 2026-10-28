# Video hook and script extraction: design (2026-10-25)

Goal: learn which hooks, scripts and formats go with sales, from the videos in `video_links_core.csv`, and use it for
our own AI videos. Videos are used for analysis only: never reposted, re-uploaded or copied shot for shot.

## Pipeline
| Step | What | Tool | Cost |
|---|---|---|---|
| 1. Pick | Winners vs comparison videos (below) | Kalodata data already downloaded | Free |
| 2. Download | MP4 for each picked video | Kalodata video download (0.5 credits each, endpoint to confirm) | ≈ $0.05 per video |
| 3. Speech | Full transcript with timestamps; the hook = words in the first 3 s | faster-whisper (installed, runs locally on CPU) | Free |
| 4. Structure | Length, number of cuts and cuts per second (scene detection), speech pace (words per second), music vs voice share | OpenCV + ffmpeg (installed) | Free |
| 5. Look | Frames at 0, 1, 2, 3 s and every few seconds after → one frame sheet per video | ffmpeg | Free |
| 6. Tag | A vision model reads the frame sheet and transcript and fills a fixed form (below) | Cheap vision model via OpenRouter | ≈ $0.001–0.005 per video |
| 7. Store | One row per video in a `video_features` table in kalodata.db, joined to its Kalodata sales, views and flags | SQLite | Free |
| 8. Analyse | What separates winners from comparison videos, by category, AI vs human, ad vs organic | pandas / scikit-learn | Free |

Files: MP4s and frame sheets under `research/kalodata/videos/<video_id>/` (about 5–15 MB per video). Videos can be
deleted after extraction and the features kept.

## The tag form (step 6)
- **Hook (first 3 s):** spoken words; on-screen text; hook type (question, problem/pain, bold claim, "you need to see
  this", reveal, demonstration, comparison, humour, trend sound, none); what's on screen at 0 s (face, product, body
  in garment, text, scene).
- **Format:** try-on, demo, review/talking head, unboxing, before/after, styling/outfit, lifestyle, slideshow, other.
- **Presenter:** person on camera (yes/no), speaking to camera, voice-over, AI-looking.
- **Product:** seconds until the product first appears; shown worn vs held vs flat; close-ups of detail (fabric,
  fit, feature).
- **Script beats:** problem → product → proof → offer → CTA (which are present, in what order).
- **Claims and offers:** price said, discount/urgency, sizing, comfort, quality claims.
- **CTA:** spoken, on-screen, none; wording.
- **Setting and style:** home, studio, outdoors, store; phone-camera vs polished.

## Sample
Comparison is the point: a hook only "works" if winners use it more than similar videos that didn't sell.
- **Winners:** videos in a category's top 300 for 2+ months, or top sellers per month.
- **Comparison videos:** same category and month, similar views, low sales per view.
- **Pilot:** 10 videos (5 winners, 5 comparison) to test the whole pipeline: ≈ 5 credits + a few cents.
- **Study:** 200 videos (100 + 100) across categories, plus an AI-only slice: ≈ 100 credits (≈ $10) + ≈ $1 of tagging.
- **Larger later if useful:** 1,000 videos ≈ 500 credits (≈ $50).

## Unknowns to settle in the pilot
- The exact Kalodata API endpoint for video downloads, and whether it returns a file or a link that expires.
- How many videos are no longer available.
- Whether the vision model tags reliably (check 10 by hand).
