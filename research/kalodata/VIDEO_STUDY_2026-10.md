# Video study: what separates winning videos (2026-10)

> **Correction (2026-10-28, Market Engine Phase A audits).**
>
> Audit docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md re-checked this study:
> - **Survives:** paid boosting (84% of winners vs 41% of comparisons, 43:4 pairs) is the only result that survives
>   correction for the 152 tests run (Holm and Benjamini-Hochberg).
> - **Does not survive:** person with product in the first frame, length, talking speed, speech share, text hook and
>   close-ups. Within pairs with the same paid status (44 pairs) "person at 0 s" is 52% vs 50%; adjusted for paid status
>   its odds ratio is 1.34 (95% CI 0.66-2.72).
> - **Not matched:** video age (winners median 37 days vs 17), so newer comparisons had less time to sell.
> - **Tags not hand-checked:** the "looks AI" tag caught 8 of 17 videos Kalodata flags as AI.
> - Production gates built from this (2.9-3.8 words/s, 70% speech share) are defaults, not proven rules (owner decision
>   D3, 2026-10-28). The stored videos were moved to the Recycle Bin on 2026-10-28; transcripts, tags and frame sheets kept.


91 pairs (182 videos), 25 categories. Each pair: a product's best-selling September video vs a typical video of the same product that got some views and stalled. Product and month are the same, so differences are about the video. Small p (under 0.05) = unlikely to be chance.

## Measurements

| measure | winners (median) | comparisons (median) | winner higher | p |
|---|---|---|---|---|
| duration_s | 34.4 | 24.4 | 55/89 | 0.033 |
| cuts_per_10s | 1.36 | 1.29 | 34/84 | 0.101 |
| words_per_s | 3.68 | 3.11 | 52/86 | 0.066 |
| speech_share | 0.88 | 0.82 | 52/85 | 0.05 |
| product_first_seen_s | 0.0 | 0.0 | 19/44 | 0.451 |

## Signals

| signal | winners | comparisons | pairs winner-only | pairs comparison-only | p |
|---|---|---|---|---|---|
| person_at_0s | 73% | 53% | 32 | 14 | 0.011 |
| product_at_0s | 81% | 68% | 23 | 11 | 0.058 |
| has_text_hook | 74% | 60% | 24 | 12 | 0.065 |
| spoken_hook | 80% | 82% | 10 | 12 | 0.832 |
| has_cta | 58% | 55% | 20 | 17 | 0.743 |
| detail_closeups | 76% | 65% | 19 | 9 | 0.087 |
| presenter_looks_ai_generated | 2% | 8% | 0 | 5 | 0.062 |
| ai_video=1 | 7% | 10% | 2 | 5 | 0.453 |
| ad=1 | 84% | 41% | 43 | 4 | 0.0 |
| production=polished | 7% | 8% | 5 | 6 | 1.0 |
| presenter=on_camera_speaking | 57% | 49% | 26 | 19 | 0.371 |
| presenter=no_person | 7% | 9% | 4 | 6 | 0.754 |

## Hook type, format and opening (share of videos)

| signal | winners | comparisons | pairs winner-only | pairs comparison-only | p |
|---|---|---|---|---|---|
| hook_type=bold_claim | 32% | 27% | 17 | 13 | 0.585 |
| hook_type=problem_pain | 19% | 19% | 12 | 12 | 1.0 |
| hook_type=question | 15% | 12% | 13 | 10 | 0.678 |
| hook_type=none | 12% | 9% | 10 | 7 | 0.629 |
| hook_type=demonstration | 7% | 10% | 5 | 8 | 0.581 |
| hook_type=offer_discount | 4% | 9% | 2 | 6 | 0.289 |
| hook_type=you_need_to_see_this | 5% | 5% | 5 | 5 | 1.0 |
| hook_type=humour_skit | 3% | 8% | 2 | 6 | 0.289 |
| format=demo | 41% | 42% | 14 | 15 | 1.0 |
| format=talking_review | 25% | 15% | 16 | 7 | 0.093 |
| format=try_on | 14% | 10% | 6 | 2 | 0.289 |
| format=other | 2% | 14% | 1 | 12 | 0.003 |
| format=lifestyle | 9% | 3% | 8 | 3 | 0.227 |
| format=unboxing | 3% | 7% | 2 | 5 | 0.453 |
| format=skit | 3% | 5% | 2 | 4 | 0.688 |
| format=styling | 1% | 2% | 1 | 2 | 1.0 |
| first_frame=person_with_product | 63% | 40% | 36 | 15 | 0.005 |
| first_frame=product_alone | 11% | 25% | 8 | 21 | 0.024 |
| first_frame=scene_without_product | 14% | 20% | 10 | 15 | 0.424 |
| first_frame=face | 10% | 13% | 6 | 9 | 0.607 |
| first_frame=other | 2% | 2% | 2 | 2 | 1.0 |
| product_shown_as_0s=not_shown | 25% | 34% | 12 | 20 | 0.215 |
| product_shown_as_0s=held | 34% | 23% | 23 | 13 | 0.132 |
| product_shown_as_0s=in_use | 20% | 11% | 14 | 6 | 0.115 |
| product_shown_as_0s=flat_or_packshot | 9% | 20% | 6 | 16 | 0.052 |
| product_shown_as_0s=worn | 12% | 12% | 3 | 3 | 1.0 |

## Elements: room, look, jewelry, styling, props, lighting, camera (90 pairs)

| signal | winners | comparisons | pairs winner-only | pairs comparison-only | p |
|---|---|---|---|---|---|
| el_hair_length=unclear | 10% | 2% | 8 | 1 | 0.039 |
| el_jewelry__none | 46% | 60% | 12 | 25 | 0.047 |
| el_camera_style=selfie_handheld | 26% | 14% | 16 | 6 | 0.052 |
| el_presenter_presents_as=none | 26% | 36% | 11 | 20 | 0.15 |
| el_presenter_presents_as=man | 20% | 12% | 13 | 6 | 0.167 |
| el_hair_color=none | 28% | 38% | 14 | 23 | 0.188 |
| el_actions__hand_detail | 72% | 62% | 23 | 14 | 0.188 |
| el_hair_length=none | 28% | 38% | 14 | 23 | 0.188 |
| el_jewelry__watch | 20% | 12% | 15 | 8 | 0.21 |
| el_age_group=none | 26% | 34% | 12 | 20 | 0.215 |
| el_actions__turning_twirling | 8% | 3% | 5 | 1 | 0.219 |
| el_camera_movement=lots | 27% | 19% | 17 | 10 | 0.248 |
| el_props__pet | 7% | 3% | 3 | 0 | 0.25 |
| el_props__none | 42% | 33% | 23 | 15 | 0.256 |
| el_room=store | 3% | 8% | 2 | 6 | 0.289 |
| el_camera_movement=slight | 67% | 74% | 13 | 20 | 0.296 |
| el_actions__putting_on_product | 12% | 7% | 10 | 5 | 0.302 |
| el_room=living_room | 19% | 13% | 10 | 5 | 0.302 |
| el_hair_length=shoulder | 14% | 21% | 10 | 16 | 0.327 |
| el_props__packaging_box | 14% | 20% | 6 | 11 | 0.332 |
| el_room=outdoors_street | 7% | 3% | 4 | 1 | 0.375 |
| el_lighting=ring_or_studio_light | 1% | 4% | 1 | 4 | 0.375 |
| el_camera_style=filmed_by_someone_handheld | 43% | 50% | 13 | 19 | 0.377 |
| el_jewelry__rings | 26% | 19% | 19 | 13 | 0.377 |
| el_hair_length=long | 21% | 16% | 14 | 9 | 0.405 |
| el_age_group=unclear | 43% | 37% | 21 | 15 | 0.405 |
| el_worn_with__jeans | 8% | 4% | 5 | 2 | 0.453 |
| el_camera_style=tripod_static | 11% | 16% | 6 | 10 | 0.454 |
| el_lighting=warm_indoor_lamps | 23% | 18% | 17 | 12 | 0.458 |
| el_makeup=unclear | 0% | 2% | 0 | 2 | 0.5 |
| el_hair_color=black | 14% | 19% | 8 | 12 | 0.503 |
| el_hair_length=covered | 10% | 7% | 6 | 3 | 0.508 |
| el_actions__talking_to_camera | 33% | 28% | 21 | 16 | 0.511 |
| el_makeup=not_visible | 61% | 56% | 21 | 16 | 0.511 |
| el_props__mug_or_drink | 6% | 9% | 4 | 7 | 0.549 |
| el_age_group=25_40 | 24% | 20% | 15 | 11 | 0.557 |
| el_color_palette=bright_bold | 12% | 9% | 8 | 5 | 0.581 |
| el_makeup=natural_or_none | 23% | 28% | 16 | 20 | 0.618 |
| el_props__furniture_in_use | 7% | 4% | 3 | 1 | 0.625 |
| el_hair_color=not_visible | 4% | 7% | 1 | 3 | 0.625 |
| el_age_group=over_40 | 2% | 4% | 1 | 3 | 0.625 |
| el_worn_with__none | 78% | 74% | 10 | 7 | 0.629 |
| el_jewelry__bracelet | 18% | 14% | 15 | 12 | 0.701 |
| el_main_shot_distance=close_up | 33% | 37% | 12 | 15 | 0.701 |
| el_props__product_alternatives | 17% | 20% | 13 | 16 | 0.711 |
| el_lighting=mixed | 23% | 20% | 16 | 13 | 0.711 |
| el_hair_color=covered | 9% | 7% | 5 | 3 | 0.727 |
| el_props__food | 6% | 8% | 3 | 5 | 0.727 |
| el_glasses | 9% | 7% | 6 | 4 | 0.754 |
| el_lighting=natural_daylight | 52% | 56% | 24 | 27 | 0.78 |
| el_hair_length=short | 12% | 10% | 8 | 6 | 0.791 |
| el_props__plants | 9% | 11% | 8 | 10 | 0.815 |
| el_main_shot_distance=medium | 22% | 20% | 14 | 12 | 0.845 |
| el_visual_quality=average | 22% | 20% | 16 | 14 | 0.856 |
| el_actions__using_product | 32% | 30% | 17 | 15 | 0.86 |
| el_presenter_presents_as=woman | 46% | 43% | 20 | 18 | 0.871 |
| el_jewelry__stud_earrings | 6% | 7% | 5 | 6 | 1.0 |
| el_jewelry__necklace | 13% | 13% | 9 | 9 | 1.0 |
| el_worn_with__sandals | 6% | 6% | 2 | 2 | 1.0 |
| el_actions__walking | 10% | 11% | 7 | 8 | 1.0 |
| el_worn_with__sneakers | 4% | 6% | 2 | 3 | 1.0 |
| el_nails_done | 28% | 29% | 17 | 18 | 1.0 |
| el_room=other | 26% | 26% | 14 | 14 | 1.0 |
| el_color_palette=pastel | 3% | 4% | 2 | 3 | 1.0 |
| el_visual_quality=dark_or_blurry | 0% | 1% | 0 | 1 | 1.0 |
| el_room=kitchen | 16% | 17% | 3 | 4 | 1.0 |
| el_room=bedroom | 16% | 16% | 7 | 7 | 1.0 |
| el_lighting=unclear | 0% | 1% | 0 | 1 | 1.0 |
| el_lighting=night_or_dim | 0% | 1% | 0 | 1 | 1.0 |
| el_presenter_presents_as=unclear | 8% | 8% | 6 | 6 | 1.0 |
| el_presenter_presents_as=mixed_group | 1% | 1% | 1 | 1 | 1.0 |
| el_age_group=under_25 | 4% | 4% | 4 | 4 | 1.0 |
| el_hair_color=brown | 19% | 18% | 13 | 12 | 1.0 |
| el_hair_color=blonde | 12% | 11% | 8 | 7 | 1.0 |
| el_makeup=moderate | 16% | 14% | 10 | 9 | 1.0 |
| el_color_palette=mixed | 42% | 42% | 21 | 21 | 1.0 |
| el_color_palette=neutral_earth | 37% | 38% | 15 | 16 | 1.0 |
| el_color_palette=black_white | 6% | 7% | 5 | 6 | 1.0 |
| el_camera_style=mixed | 18% | 19% | 11 | 12 | 1.0 |
| el_camera_style=mirror_selfie | 2% | 1% | 2 | 1 | 1.0 |
| el_main_shot_distance=mixed | 37% | 37% | 15 | 15 | 1.0 |
| el_main_shot_distance=full_length | 8% | 7% | 3 | 2 | 1.0 |
| el_camera_movement=static | 7% | 7% | 4 | 4 | 1.0 |
| el_visual_quality=sharp_well_lit | 78% | 79% | 14 | 15 | 1.0 |
| el_actions__posing | 20% | 20% | 11 | 11 | 1.0 |
| el_background_people | 7% | 7% | 4 | 4 | 1.0 |

## Apparel, shoes, bags and accessories (22 pairs)

| measure | winners (median) | comparisons (median) | winner higher | p |
|---|---|---|---|---|
| duration_s | 20.45 | 16.4 | 14/22 | 0.286 |
| cuts_per_10s | 0.3 | 1.15 | 6/19 | 0.167 |
| words_per_s | 3.63 | 2.54 | 10/20 | 1.0 |
| speech_share | 0.86 | 0.79 | 12/19 | 0.359 |
| product_first_seen_s | 0.0 | 0.0 | 3/6 | 1.0 |

| signal | winners | comparisons | pairs winner-only | pairs comparison-only | p |
|---|---|---|---|---|---|
| person_at_0s | 91% | 59% | 9 | 2 | 0.065 |
| product_at_0s | 95% | 91% | 2 | 1 | 1.0 |
| has_text_hook | 64% | 50% | 7 | 4 | 0.549 |
| spoken_hook | 73% | 73% | 3 | 3 | 1.0 |
| has_cta | 50% | 50% | 4 | 4 | 1.0 |
| detail_closeups | 82% | 73% | 3 | 1 | 0.625 |

## Everything else (69 pairs)

| measure | winners (median) | comparisons (median) | winner higher | p |
|---|---|---|---|---|
| duration_s | 39.7 | 28.5 | 41/67 | 0.086 |
| cuts_per_10s | 1.68 | 1.35 | 28/65 | 0.321 |
| words_per_s | 3.68 | 3.16 | 42/66 | 0.036 |
| speech_share | 0.88 | 0.83 | 40/66 | 0.109 |
| product_first_seen_s | 0.0 | 0.0 | 16/38 | 0.418 |

| signal | winners | comparisons | pairs winner-only | pairs comparison-only | p |
|---|---|---|---|---|---|
| person_at_0s | 67% | 51% | 23 | 12 | 0.09 |
| product_at_0s | 77% | 61% | 21 | 10 | 0.071 |
| has_text_hook | 77% | 64% | 17 | 8 | 0.108 |
| spoken_hook | 83% | 86% | 7 | 9 | 0.804 |
| has_cta | 61% | 57% | 16 | 13 | 0.711 |
| detail_closeups | 74% | 62% | 16 | 8 | 0.152 |

## Winning hooks (first 3 s, spoken or on screen)

- **Beauty & Personal Care** · $328,823 · none / talking_review: "She thought it was a mistake. She actually sent me a message and said, I thought it was"
- **Household Appliances** · $246,523 · bold_claim / demo: "Oh, you're never gonna go back to cleaning up stains the old way"
- **Automotive & Motorcycle** · $246,248 · bold_claim / demo: "I recommend this to everyone. No matter what your budget is right now, I'd"
- **Tools & Hardware** · $245,481 · bold_claim / demo: "When it was $140, you passed on it. Fair"
- **Kitchenware** · $199,880 · question / talking_review: "So you think you're better than me because you have hexagons? No, I know I'm better"
- **Sports & Outdoor** · $144,709 · question / lifestyle: "How are you recording? You're so sweaty."
- **Furniture** · $137,095 · bold_claim / demo: "I actually did not expect this to feel like a luxury hotel bed."
- **Computers & Office Equipment** · $112,569 · question / demo: "If you put $100 each week to this book,"
- **Shoes** · $107,163 · offer_discount / try_on: "Crocs just put these on a major clearance price and"
- **Health** · $104,460 · question / talking_review: "People are always asking me, Vanessa, how do you look this good at 50? And I'm like, dude,"
- **Womenswear & Underwear** · $101,539 · bold_claim / try_on: "you have to do is scoop, clasp, clip, and boom instant"
- **Phones & Electronics** · $96,819 · humour_skit / skit: "Are you back at home in the show? Yeah. Did"
- **Toys & Hobbies** · $81,672 · you_need_to_see_this / unboxing: "(visual only)"
- **Pet Supplies** · $79,877 · bold_claim / talking_review: "You think you're better because you're stainless steel. I know I'm"
- **Textiles & Soft Furnishings** · $65,481 · demonstration / demo: "This is a medium size dreamer. This is a large dreamer. This is"
- **Baby & Maternity** · $52,923 · problem_pain / demo: "If you're pregnant rn, check out rn & thank me later 🤍"
- **Luggage & Bags** · $51,487 · bold_claim / demo: "this is one of the new wallet models it's so compact it has card"
- **Health** · $50,850 · problem_pain / talking_review: "Cortisol, alto, cortisol, alto, cortisol,"
- **Food & Beverages** · $47,246 · bold_claim / lifestyle: "ballerina farm's bone broth hot cocoa FINALLY got restocked and yes...it's as good as everyone says ☕🤎"
- **Home Supplies** · $42,721 · bold_claim / talking_review: "I'm calling it now, but Autumn Sunrise will become R &W"
- **Books, Magazines & Audio** · $40,153 · humour_skit / skit: "Quédate con el cambio no"
- **Womenswear & Underwear** · $40,082 · problem_pain / try_on: "If you have bottom heavy boobs, you want a BELKINET bra."
- **Menswear & Underwear** · $40,011 · none / try_on: "(visual only)"
- **Kids' Fashion** · $39,712 · bold_claim / styling: "My boy mamas, are you joking? This"
- **Food & Beverages** · $39,394 · problem_pain / demo: "If you've ever wanted an espresso, now's your chance. Because HSN"

## Limits

- Tags come from a vision model (Claude Haiku 5.5): objective measures are reliable, hook type and format are judgement calls (pilot showed some disagreement between models).
- One month (September), one winner and one comparison per product; about 4 products per category.
- Comparisons came from public TikTok links; winners from links with Kalodata as backup.

## Background music (added 2026-10-26)

Tagged with `scripts/video_audio.py`: MIT's AST AudioSet classifier run locally on 5 s windows (music when the "Music"
score is at least 0.25 in 20%+ of windows), plus loudness of pauses vs speech from the transcript timings. 185 videos,
91 complete pairs; results in table `video_audio`.

| | Winners | Stalled |
|---|---|---|
| Any background music | 33% | 38% |
| Music under speech ("clear") | 13 | 15 |
| Music-led (little speech) | 17 | 19 |
| No music | 61 | 56 |

- Pairs where only one video had music: winner 14, stalled 19 (sign test p = 0.49): **no difference**.
- When both had music (9 pairs) the winner's music was a little louder relative to the voice in 6 (p = 0.51): too few to read.
- Paid-boosted winners 33% vs 42%; organic winners 33% vs 20% (15 pairs only).
- Takeaway: music neither helps nor hurts on its own here; talking to camera (speech share 88% vs 82%) and a person
  with the product in the first second matter more. Music remains a free choice, not a lever.
