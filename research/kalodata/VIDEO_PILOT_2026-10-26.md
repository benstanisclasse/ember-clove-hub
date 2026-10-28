# Video extraction pilot (2026-10-26)

Script: `scripts/video_pilot.py`. Files per video: `research/kalodata/videos/<video_id>/` (video.mp4, transcript.json,
sheet.jpg, tags.json). Results: table `video_features` in kalodata.db.

## What worked (3 videos, all the way through)
| Video | Sales / views | Length, cuts | Hook (first 3 s, from the transcript) | Tags |
|---|---|---|---|---|
| Womenswear: BELKINET bra | $40,082 / 2.0M | 27.8 s, 2 cuts, 4.0 words/s | "If you have bottom heavy boobs, you want a BELKINET bra." | problem hook · try-on · worn from 0 s · spoken CTA "I'll link these below…" |
| Menswear: sherpa-lined jacket | $40,011 / 5.0M | 16.4 s, 2 cuts, 1.3 words/s | "Here…" | no spoken hook · styling · mostly visual |
| Shoes: suede knee-high boots | $19,869 / 707K | 46.7 s, 1 cut, 4.1 words/s | "The boots that are gonna go with anything this fall are…" + on-screen "Cute comfy boots!" | bold claim · styling · worn from 0 s · spoken CTA |

- **Download:** Kalodata's "Get video URL" (0.5 credits, link valid 5 minutes) worked for all 3 best-sellers.
- **Transcripts:** accurate on all 3 (checked against the frames).
- **Tags:** mostly right. One clear error in 3: the jacket video opens with the jacket **held up**, not worn; the
  model tagged "worn". Cut detection was made more sensitive after review; still unverified frame by frame.
- **Tagging cost:** fractions of a cent per video (Gemini 2.5 Flash Lite via OpenRouter).

## What didn't
- **Kalodata refused every low-view comparison video** (10 of 10, HTTP 403) and still charged 0.5 credits each.
  It seems to keep copies of popular videos only. Pilot cost: 7 credits, 5 of them on refused files.

## What we learned about the data
Within one product, **sales per view are about the same for every video** (for example, the bra: about $20 per
1,000 views from its biggest video down). Winners don't convert better: they **get far more views**. So the hook's
job is to earn reach, and the study should compare high-reach vs low-reach videos of the same product.

## Options for the comparison videos
1. **Mid-tier videos Kalodata does hold** (for example 10K–50K views): test which view level it keeps (≈ 1 credit).
2. **Low-view videos from their TikTok links** (free, but against TikTok's terms; owner's call).
3. **Compare within best-sellers only:** top-300 videos range from about $3K to $100K+ a month in each category;
   relate hook and format to sales and views across them. Everything should download, but the contrast is weaker.

## Mid-tier test (1 credit)
- ~50K views ($496 sales): served, but the file is **audio only** (60 s, no picture). Likely a photo-slideshow post,
  or Kalodata kept only the sound. Not usable for visuals.
- ~12K views ($1,681 sales): **refused** (403), charged 0.5.
- So Kalodata isn't a reliable source for non-top videos: availability isn't just about views. Best-sellers did
  download (3 of 3).

## Full pilot: 5 pairs (2026-10-26)
Winners from Kalodata (best-seller of each product); comparisons from their public TikTok links with yt-dlp
(owner's decision; 5 videos, spaced out, analysis only). Each pair is the same product and month.

| Category | Winner (sales / views) | Comparison | What differs |
|---|---|---|---|
| Womenswear (bra) | $40,082 / 2.0M · 27.8 s · spoken problem hook while wearing it: "If you have bottom heavy boobs, you want a BELKINET bra." · spoken CTA | $51 / 913 · 8.6 s · almost the same hook as on-screen text over a bra laid flat, music, no person, no CTA | Same words; a person wearing it and saying it vs text on a flat-lay |
| Health (breast pump) | $15,647 / 593K · 23.5 s · text before/after hook "Pumping looked like this… until I switched to this", silent, product in use from 0 s | $0 / 775 · 7.8 s · meme caption unrelated to the product, product appears flat at 3 s, no CTA | Before/after with the product in use vs off-topic meme |
| Tools (gadget) | $23,758 / 156K · 32.9 s · bold claim "Who would actually believe this?" · 13 cuts, voice-over, polished, spoken CTA | $40 / 505 · 18.7 s · similar bold claim, 5 cuts, phone footage, no CTA | Pace and polish, CTA |
| Shoes (boots) | $19,869 / 707K · 46.7 s · "The boots that are gonna go with anything this fall are…" + on-screen "Cute comfy boots!" · spoken CTA | $29 / 962 · 18.6 s · generic "Outfit from TikTok Shop", spoken CTA | Specific seasonal claim vs generic intro |
| Menswear (jacket) | $40,011 / 5.0M · 16.4 s · almost no talking, jacket held up then worn, turning to show it | $62 / 4,089 · 24.4 s · skit dialogue "Bro, that's a tough jacket…", spoken CTA | Simple visual showcase beat a skit |

Common to the winners (5 pairs, so hints only): the product is on screen at 0 s with a person using or wearing it;
they run longer (16–47 s vs 8–24 s); 4 of 5 have a spoken call to action (comparisons: 1 of 5); a clear claim or
problem in the first 3 s. The bra pair shows execution matters more than the words: the same hook failed as text on
a flat-lay.

## Tag reliability
- Improved instructions (speech share passed in; judge "worn" from the 0 s frame) fixed the flat-lay bra (now
  no person, laid flat) for both models.
- Claude Haiku 5.5 also fixed the silent pump video ("on camera, silent"); Gemini Flash Lite still said "speaking".
- Still wrong in both: the jacket at 0 s is held up, tagged "worn".
- Subjective fields disagree between models (hook type: "bold claim" vs "you need to see this"; format: "styling" vs
  "try-on"). For the study: tighter definitions, Haiku as the tagger, and a hand check of a sample.
- Objective measures (speech, words per second, cuts, length, on-screen text) are reliable.

## Costs
Kalodata ≈ 9 credits for the whole pilot (balance 477.0), 5 of them on refused files. OpenRouter tagging ≈ $0.02.
Haiku tagging ≈ $0.0008 per video, so a 200-video study is about $0.20 of tagging plus ≈ 50 credits for 100 winners.
Video files are kept for now for checking; delete after the study, keeping only the extracted notes.
