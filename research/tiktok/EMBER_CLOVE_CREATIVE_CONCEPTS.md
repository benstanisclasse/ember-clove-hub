> **Owner rule 2026-10-25:** no prices or delivery times in spoken lines or post captions, so an ad keeps working if the price or shipping changes. Scripts and captions below were updated; the 4 videos already made still say them (see CHECKPOINT_C_REPORT).

# EMBER_CLOVE_CREATIVE_CONCEPTS

**Checkpoint C, Phase 6.3.** Ember & Clove, 2026-10-25. Nothing generated, launched or spent.
Companion files: `HYPOTHESIS_REGISTRY_cycle1.md` (Phase 7.1) and `scripts/concept_specs_cycle1.py` (generator specs for
the shortlisted videos, in the `make_tryon.py` SPECS format).

Inputs: `reports/icp_P01_cable-knit-midi_2026-10-24.md` (ICP-P01), `reports/icp_P02_turtleneck-sweater-dress_2026-10-24.md`
(ICP-P02), `HOOK_AND_ARCHETYPE_LIBRARY.md` (HK-xx, AR-xx), `ATTENTION_PSYCHOLOGY_PLAYBOOK.md` (PB),
`HIGH_PERFORMING_AD_PATTERNS.md` (HP), `TIKTOK_ALGORITHM_INTELLIGENCE.md` (AI §6, §9), `scripts/make_tryon.py`.
Evidence categories follow Phase 9 (A official, B empirical, C industry-observed, D hypothesis). **Every concept below
is a D-category test proposal**; the evidence cited explains why it is worth testing, not that it will work.

---

## 0. Ground rules for this round

### 0.1 Fixed vs test variables (owner decision 2026-10-25, relayed by the lead researcher)

| Fixed in every video (support or compliance) | Now a **test variable** (one per comparison) |
|---|---|
| Dress on the presenter's body in frame 1 (HP §3.1: 36/38 vs 30/38, C; PB rule 1, B) | **On-screen text**: only TikTok's own auto-captions (or its native text tool) switched on at posting, never added by us; default off |
| Talking AI presenter, labelled AI-generated on TikTok (AI §9 rec 7, A) | **Opening type**: situation callout (≤ ~9 words, situation visible) vs demo-first opening with no buyer callout |
| ~2 cuts per 10 s (4 shots in 15 s; HP §3.3, C) | **Length**: 15 s vs a 25–30 s version of a 15 s winner (later) |
| No fabricated claims, no banned words, facts from the product pages only | |
| Generated video used exactly as delivered: no overlays, end cards, music or edits by us | |

Priority of what round 1 must answer: **(a)** callout vs demo-first opening, same video otherwise (needs 2
generations per product); **(b)** TikTok auto-captions on vs off on the same video (no generation); **(c)** later,
15 s vs 25–30 s of the winner (one longer generation per product). Concepts are written so the base version (H01)
complies with the old strict rules; arms that use a test variable are marked **TEST ARM**.

### 0.2 Facts the ads may use (product pages + store policy; nothing else)

- **P01 Cable Knit Mock Neck Midi Dress** ($52.99; `gid://shopify/Product/9751656071407`): cable knit (skirt), mock
  neck, front slit "that keeps it easy to move in", "soft acrylic-blend knit" (we say "acrylic-blend knit"), ribbed
  waist, fitted through the hip, long sleeves, midi about 44–47 in, sizes S–XL, colors Black, Heather Gray, Dark Blue,
  Caramel, Red, Green, Berry ("cozy" is page wording).
- **P02 Turtleneck Rib Knit Sweater Dress** ($44.99; `gid://shopify/Product/9751655809263`): slouchy, folded
  turtleneck, loose fit, dropped shoulders, chunky rib, long sleeves, mini about 27–28 in, "easy over tights and
  boots", acrylic and polyester with an angora wool blend, "cozy" (page wording), colors Gray, White, Khaki, Black,
  Navy, Burgundy, Sky Blue. **No size range in any P02 ad or caption** (3XL garment bust is 48 in; ICP-P02 finding 1).
- **Store:** free US shipping over $70 (two P01 = $105.98, two P02 = $89.98); delivery about 2–3 weeks; 7-day returns
  (say only "seven-day returns", never "free" or "easy").
- **Never:** "I bought / I own / I've worn it", testimonials, reviews, ratings, urgency, scarcity, countdowns,
  guarantees, "warm", "100% wool", "wool dress", "soft" (P02), "not itchy", body-shaping or before/after body claims,
  "best seller", "flattering on every body", "looks expensive", "up to 3X" / size-range bragging, "skims / doesn't
  cling" for P01 (it is fitted).
- **Check before every generation:** the live Shopify price and colors (the 2026-10-24 inbox export still showed
  older prices $52.04 / $44.24; the brief says $52.99 / $44.99). A spoken price that no longer matches = do not run.

### 0.3 Production defaults (all concepts)

- **Generator:** Seedance 2.5 reference-to-video via `make_tryon.py` (15 s, 720p, 9:16, `generate_audio=True`),
  ~$0.324/s → **≈ $4.86 per 15 s**, ≈ $8.10 (25 s), ≈ $9.72 (30 s). Every rejected clip costs the full price again.
- **STYLE string** (from `make_tryon.py`): UGC phone look, four cuts, warm apartment, AI-generated presenter, "no
  background music, no on-screen text, no logos"; a `setting` key swaps the apartment for another room.
- **Presenter:** one fictional adult woman, described the same way in every spec to reduce presenter variance between
  test arms: *shoulder-length wavy dark-brown hair, small gold hoop earrings*. Never framed as a customer.
- **References:** face-free crops only (the supplier model's face never enters the prompt).
- **Sound design (every concept):** generated on-camera speech only, natural pace (~2.3–2.6 words/s), light room tone
  and incidental sounds (footsteps on wood, a mug set down, keys). **No music, no sound effects stingers, no
  voice-over from an unseen narrator.** Reject a clip with any music bed.
- **Spoken numbers** are written out in words in the prompt ("fifty-two ninety-nine", "forty-four to forty-seven
  inches") so the model says them; a garbled number or price = reject.
- **Shared rejection criteria (every clip):** any visible text, captions, logo or watermark; music; garment changes
  (color, knit pattern, neckline, length, slit position/height); bare legs on P02; a second outfit layered over the
  dress that hides it for more than ~1 s; hand/finger artefacts touching the dress; lip-sync drift that is noticeable;
  mispronounced "Ember and Clove" or price; a line not in the script (models sometimes improvise "I love this", "I
  got this", which would be an ownership claim); a presenter who looks like a real, recognisable person; any child in
  frame.
- **Posting (every ad):** post from @emberandclove; switch on TikTok's **"AI-generated content"** disclosure and confirm
  the label shows in the Spark Ad preview (AI §9 rec 7); keep "AI-generated video." in the caption text as well.
  **Auto-captions OFF** unless the ad is the captions arm of test (b). TikTok's AI asset auto-add set to off or
  approval-only (AI §9 rec 8). Link to the product page with UTM tags; ad name = creative ID.
- **Post caption rules:** ≤ 150 characters, plain facts from §0.2, at most one hashtag, no banned claims.

### 0.4 What this file supersedes (all four were drafts, never generated, $0 spent)

| Draft in `make_tryon.py` | Superseded by | Why |
|---|---|---|
| EC-P01-A05-H01-V01 (boots, seated boot-zip opener, 11-word callout, "sizes small to XL") | **EC-P01-A05-H01-V02 / H02-V02** | Seated boot-zipping is a hard dressing action for the model and hides the slit and length in frame 1; callout shortened to 8 words (HK-31, PB H-AP-02); size line dropped from speech |
| EC-P01-A06-H01-V01 (holiday, red, hanger opener) | **EC-P01-A06-H01-V02** | Frame 1 showed the dress on a hanger (now must be on body); 11-word callout → 8 (HK-19); "so order early" reworded as a plain delivery fact |
| EC-P02-A05-H01-V01 (outfit formula, holding boots, seated pull-on) | **EC-P02-A05-H01-V02 / H02-V02** | 11-word callout → 9; seated boot pull-on removed (AR-05 feasibility); hem-over-tights proof and price added |
| EC-P02-A06-H01-V01 (comfort, opens in leggings + hoodie) | **EC-P02-A06-H01-V02** | Frame 1 had no dress on body; the "swap" becomes couch-to-door in the same dress (AR-06 adapted) |

**Legacy approved ads (controls so far):** EC-P01-A03-H01-V01 ("Okay, you need to see this sweater dress.", caramel)
and EC-P02-A03-H01-V01 ("Okay, this sweater dress is so cozy.", burgundy) both open on a hanger (dress not on body
in frame 1) with a curiosity/statement line. They are **benchmarks, not arms** of any controlled comparison below.
**EC-P02-A03 should not run as is**: it says "sizes small to 3X". EC-P01-A03 may run as a legacy benchmark only if the
owner wants it in the screening group (it would take a share of a small budget).

### 0.5 Compliance check run on every concept

| # | Check |
|---|---|
| C1 | AI presenter; no ownership, purchase, wear-over-time, testimonial, review or rating language |
| C2 | No banned word or claim (§0.2 "Never" list), incl. urgency and guarantees |
| C3 | Every product statement traceable to §0.2 (page or store policy) |
| C4 | First line ≤ ~9 words and names the buyer by situation (or is a labelled TEST ARM) |
| C5 | Dress on body in frame 1; the named situation is visible in frame 1 |
| C6 | No body or health trait, no body before/after, no "shape" claims about the viewer |
| C7 | P02: no size range; P01: sizes only as the page states (S–XL), captions only |
| C8 | No text, music or end card in the video; generated speech + room tone only |
| C9 | Price, shipping, delivery and returns wording matches store facts |
| C10 | Caption ≤ 150 chars, ≤ 1 hashtag, "AI-generated video." present, AI disclosure toggle instructed |

Character counts of the captions below were checked with a script (2026-10-25).

---

## 1. P01 Cable Knit Mock Neck Midi Dress — five concepts

Shared P01 demonstration requirements (all concepts): plain-knit fitted top; **cable knit on the skirt only**; ribbed
waistband at the natural waist; mock neck; long sleeves with ribbed cuffs; diagonal wrap seam ending in the **front
slit, never higher than in the references** (opens around/just above the knee in stride); **midi hem at mid-calf**,
overlapping the top of knee-high boots; fitted through the hip but no exaggerated body proportions. Reject if the
skirt shortens to the knee, the slit becomes thigh-high, cables appear on the bodice, or the color shifts.

### EC-P01-A05 — "Tall boots, finished" (lead; round 1, test (a))

| Field | Content |
|---|---|
| ICP segment | P01 S1 Boot-Season Outfit Builder (ICP-P01 F1, priority 1) |
| Archetype | **AR-04 Real-life demonstration** (stride test) inside the AR-02 callout-and-proof frame |
| Persuasion angle | Outfit completion + physical proof: "your boots + this dress = the outfit" (ICP-P01 A1, with A5 as proof beat) |
| Buyer motive | Wants a finished, styled cold-weather look with boots she already owns |
| Color / refs | Caramel — `assets/EC-P01-A02-H01-V01/ref1_dress_neck_down.jpg`, `ref2_cable_slit_closeup.jpg` (exist) |
| Hypothesis | Showing the slit opening over knee-high boots from frame 1 ties the dress to the most-searched pairing ("sweater dress with boots", ICP-P01 D1 [V]) and yields more add-to-carts per 1,000 impressions than the other P01 concepts. **Within the concept (test a):** a situation callout (H01) produces fewer 2-s stops but higher CVR on clicks than a demo-first line (H02), with ATC per 1,000 impressions as the tie-breaker (PB H-AP-05) |

**Hooks**

| Hook | HK | Opening line (words, ≈ s) | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-31 | "Own knee-high boots? This dress is for you." (8, ≈3.2 s) | Full length, already in the caramel dress + black knee-high boots, two steps toward camera, slit opening over the boots, direct gaze | Base (callout) — **round 1** |
| H02 | HK-35 (new; HK-04 with the callout removed) | "Watch what this slit does with every step." (8, ≈3.2 s) | **Identical** to H01 (same stride, framing, boots) so only the spoken opening differs | **TEST ARM (a): demo-first** — **round 1** |
| H03 | HK-01 | "Own tall boots, but only wear them with jeans?" (9, ≈3.6 s) | Same outfit; as she steps forward she tosses a folded pair of jeans onto an armchair | Base (problem + situation) — backlog |

**Storyboard (15 s, 4 shots, 3 cuts)** — shots 2–4 identical across H01/H02/H03.

| Shot | Time | Camera | Action / setting | Wardrobe & styling | Dress must visibly… | Line |
|---|---|---|---|---|---|---|
| 1 | 0–3 s | Phone at chest height, full length, static | See hook table; warm apartment, wood floor, arched mirror, daylight | Caramel P01, black knee-high leather boots (low heel), gold hoops, hair down; no coat, no bag | Hem overlapping boot tops; slit open on the step | Hook line |
| 2 | 3–7 s | Mid-shot (chest to mid-thigh), slight push-in | Hands run down the cable skirt, smooth the ribbed waistband, touch the mock neck; eyes on her hands | Same | Vertical cables on skirt only; ribbed waistband; mock neck | "Cable knit, mock neck, fitted through the hips." |
| 3 | 7–11 s | Full length, side-front, handheld follow | Walks past the arched mirror; slit opens over the boot shaft each step | Same | Slit height as reference; midi length; natural stride | "The slit opens over your boots, so walking's easy." |
| 4 | 11–15 s | Walk-in to chest-up close-up | Smiles to camera | Same | Mock neck and cable texture readable | "It's Ember and Clove, fifty-two ninety-nine. Link's right here." |

**Narration scripts**
- **H01 (34 words):** "Own knee-high boots? This dress is for you. / Cable knit, mock neck, fitted through the hips. / The slit opens
  over your boots, so walking's easy. / It's Ember and Clove, fifty-two ninety-nine. Link's right here."
- **H02 (34 words):** "Watch what this slit does with every step. / Cable knit, mock neck, fitted through the hips. / The slit opens over
  your boots, so walking's easy. / It's Ember and Clove, fifty-two ninety-nine. Link's right here."
- **H03 (35 words):** "Own tall boots, but only wear them with jeans? / Cable knit, mock neck, fitted through the hips. / The slit opens
  over your boots, so walking's easy. / It's Ember and Clove, fifty-two ninety-nine. Link's right here."

**Sound design:** §0.3; footsteps on the wood floor in shots 1 and 3 help the stride read.
**Demonstration requirements / rejection:** shared P01 list; plus reject if the slit does not visibly open in shot 1
(H01/H02 depend on it) or if boots read as part of the product (they are styling props; never say they are included).
**CTA:** "It's Ember and Clove, fifty-two ninety-nine. Link's right here."
**Post caption (128 chars):** "Cable knit midi with a front slit that opens over tall boots. Mock neck, sizes S–XL, 7 colors. AI-generated video. #sweaterdress"
**Optional 25–30 s version (test c, after a 15 s winner; ≈ $8.10–9.72):** 0–3 s same opening as the winning hook ·
3–8 s waist/cable close-up (shot 2 line) · 8–14 s stride past the mirror + a turn showing the fitted hip and ribbed
waist ("Fitted through the hips, ribbed at the waist.") · 14–20 s low shot of hem meeting the boot ("It's a midi, about
forty-four to forty-seven inches, and it's an acrylic-blend knit.") · 20–26 s close-up CTA with the AOV fact ("Fifty-two
ninety-nine, and two dresses ship free. Link's right here."). ≈ 60 words.
**Compliance check:** C1 ✓ (no ownership; "your boots" refers to the viewer's boots) · C2 ✓ · C3 ✓ (cable knit, mock
neck, fitted hip, slit "easy to move in", price) · C4 ✓ H01/H03; H02 = TEST ARM · C5 ✓ (boots visible, dress on body) ·
C6 ✓ ("fitted through the hips" is a garment fact) · C7 ✓ (S–XL in caption only) · C8 ✓ · C9 ✓ · C10 ✓.

### EC-P01-A06 — "Holiday plans, one dress" (round 1, time-boxed)

| Field | Content |
|---|---|
| ICP segment | P01 S2 Holiday-Gathering Dresser (ICP-P01 F2) |
| Archetype | **AR-15 Occasion outfit** |
| Persuasion angle | Dated-event relevance + honest delivery time (ICP-P01 A2) |
| Buyer motive | Has a December party/family dinner; wants a festive, covered outfit without effort |
| Color / refs | Red — `assets/EC-P01-A06-H01-V01/ref1_red_dress_neck_down.jpg`, `ref2_red_cable_slit_closeup.jpg` (exist). The reference red is a bright coral-red: reject crimson/burgundy drift |
| Time box | Launch by ~Nov 5; stop party wording ~Nov 15–20 (delivery about 2–3 weeks; ICP-P01 F2 timing) |
| Hypothesis | Among the same broad audience, an occasion frame plus an honest delivery line gives a higher CVR on clicks than the boots frame (A05) during the window, because visitors who click already have a dated reason to buy and know the timing |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-19 | "Holiday party coming? This is the whole outfit." (8, ≈3.2 s) | Full length by the front door framed with string lights, red dress + black knee-high boots, she fastens an earring then turns to camera | Base (callout) — **round 1** |
| H02 | HK-24 | "Ordering a holiday dress online? Check the delivery time first." (10, ≈4 s, long) | Same doorway; she holds a small wrapped gift box, looks at camera | Base (situation + mistake avoidance) — backlog |
| H03 | HK-29 | "First cold Friday, holiday party at eight." (7, ≈2.8 s) | Same doorway, evening; she lifts a coat off a hook (keeps it over her arm, dress fully visible) | **TEST ARM (a): story opening, no buyer callout** — backlog |

**Storyboard** (setting: the apartment in the evening with warm string lights around the door and a small wreath)

| Shot | Time | Camera | Action | Wardrobe | Dress must visibly… | Line |
|---|---|---|---|---|---|---|
| 1 | 0–3 s | Full length, static | Hook visual | Red P01, black knee-high boots, small gold earrings; coat (H03) carried, never worn | Red matches reference; hem over boots | Hook |
| 2 | 3–7 s | Mid-shot under the lights | Turns slightly to show mock neck, sleeves, cable skirt | Same | Mock neck, long sleeves, cable skirt | "Ember and Clove's red cable knit, mock neck, long sleeves." |
| 3 | 7–11 s | Full length, handheld | Walks across the room; slit opens over boots | Same | Slit in stride, midi length | "Fitted through the hips, with a slit to move in." |
| 4 | 11–15 s | Walk-in close-up | Friendly smile | Same | Texture | "Delivery's about two to three weeks. Link's right here." |

**Narration scripts**
- **H01 (37):** "Holiday party coming? This is the whole outfit. / Ember and Clove's red cable knit, mock neck, long sleeves. /
  Fitted through the hips, with a slit to move in. / Delivery's about two to three weeks. Link's right here."
- **H02 (39, shot 4 shortened):** "Ordering a holiday dress online? Check the delivery time first. / Ember and Clove's red
  cable knit, mock neck, long sleeves. / Fitted through the hips, with a slit to move in. / This one's about two to three
  weeks. Link's here."
- **H03 (36):** "First cold Friday, holiday party at eight. / Ember and Clove's red cable knit, mock neck, long sleeves. /
  Fitted through the hips, with a slit to move in. / Delivery's about two to three weeks. Link's right here."

**Sound design:** §0.3; soft room tone, no festive music (rule), the faint click of an earring or coat hanger is fine.
**Demonstration requirements / rejection:** shared P01 list + red fidelity; reject any line or image implying arrival
by a date ("in time for Christmas"); no Santa/brand-like holiday characters; décor stays simple (string lights, wreath).
**CTA:** "Delivery's about two to three weeks. Link's right here." (information, not urgency; no "order now", no "before it's too late").
**Post caption (122 chars):** "Red cable knit midi for December plans: mock neck, long sleeves, front slit. Sizes S–XL. AI-generated video."
**Optional 25 s:** add a seated shot at a set table (shows the dress sitting, covered silhouette) and "Seven colors,
including green" — only with green refs. Low priority (window closes).
**Compliance check:** C1 ✓ · C2 ✓ (delivery stated as fact; no countdown) · C3 ✓ · C4 ✓ H01/H02 (H02 runs 10 words,
marked long); H03 = TEST ARM · C5 ✓ (holiday door, dress on body) · C6 ✓ · C7 ✓ · C8 ✓ (no music) · C9 ✓ ("about two to
three weeks") · C10 ✓.

### EC-P01-A07 — "Covered, still going out" (backlog; needs new refs)

| Field | Content |
|---|---|
| ICP segment | P01 S3 Covered-but-Shapely Going-Out Dresser (ICP-P01 F3) |
| Archetype | **AR-01 Immediate product payoff** (finished evening look at 0 s, side profile) |
| Persuasion angle | Emotional/self-presentation: covered (mock neck, sleeves, midi) and still going-out ready (fitted, slit) — ICP-P01 A3, spoken as **garment facts only** |
| Buyer motive | Wants to feel attractive on a cold date or night out without a mini |
| Color / refs | Black — **new crops needed** from `assets/EC-P01-A02-H01-V01/src_F2DBBAD28F9480BDB2430849E31F14A6.jpg` (black street shot, store image `F2DBBAD28F9480BDB2430849E31F14A6.jpg`): neck-down crop + cable/slit close-up, face excluded |
| Hypothesis | A going-out frame has lower CTR than the boots frame (A05) but similar or higher CVR on clicks among women it stops, with fit-return requests to watch (cling-averse viewers should self-select out) |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-33 | "Winter date night, and you're done with minis?" (8) | Evening lamp light, full length, black dress + black knee-high boots, she turns from the mirror into a side profile mid-step | Base (callout) |
| H02 | HK-18 (adapted) | "Mock neck, long sleeves, midi, and a front slit." (9) | Slow camera tilt from the boots up the cable skirt to the mock neck as she walks | **TEST ARM (a): demo-first** |
| H03 | HK-15 | "Tired of tiny steps in fitted midi dresses?" (8) | Full length, one long stride; slit opens | Base (frustration; situation) |

**Storyboard** (setting: the apartment at night, warm lamp light, hallway to the door)

| Shot | Time | Camera | Action | Wardrobe | Dress must visibly… | Line |
|---|---|---|---|---|---|---|
| 1 | 0–3 s | Full length | Hook visual | Black P01, black knee-high boots, gold hoops, small clutch | Mock neck, midi, slit | Hook |
| 2 | 3–7 s | Mid-shot, eye level (no low angles) | Hands on the ribbed waist, quarter turn | Same | Ribbed waistband, fitted hip (garment, not body emphasis) | "It's fitted through the hips, with a ribbed waist." |
| 3 | 7–11 s | Full length, hallway | Walks toward camera, slit opens | Same | Slit height as reference | "The slit gives you an easy stride, and a little leg." |
| 4 | 11–15 s | Close-up | Smiles, picks up clutch | Same | Cable texture visible on black (lighting must show it) | "It's Ember and Clove, fifty-two ninety-nine. Link's right here." |

**Narration scripts** — H01 (37): "Winter date night, and you're done with minis? / It's fitted through the hips, with a
ribbed waist. / The slit gives you an easy stride, and a little leg. / It's Ember and Clove, fifty-two ninety-nine.
Link's right here." · H02 (38): same with "Mock neck, long sleeves, midi, and a front slit." · H03 (37): same with "Tired of
tiny steps in fitted midi dresses?"
**Sound design:** §0.3, quiet evening room tone.
**Demonstration / rejection:** shared P01 list; black must still show the cable texture (reject a flat black blob);
styling tasteful (no lingering on the body, no low angles); reject any exaggerated body proportions.
**CTA:** "It's Ember and Clove, fifty-two ninety-nine. Link's right here."
**Post caption (120 chars):** "Mock neck, long sleeves, midi length and a front slit, in black. Fitted through the hip. Sizes S–XL. AI-generated video."
**Compliance check:** C1 ✓ · C2 ✓ · C3 ✓ · C4 ✓ H01/H03, H02 TEST ARM · C5 ✓ (evening setting) · C6 ⚠ resolved: no
"shows your shape" (ICP hook rejected); only "fitted through the hips" (page) and "a little leg" (what the slit shows)
· C7 ✓ · C8 ✓ · C9 ✓ · C10 ✓. **OPTIONAL — owner to confirm** that "a little leg" is acceptable; fallback line:
"The front slit makes walking easy."

### EC-P01-A08 — "Where the hem meets the boot" (backlog; needs new refs)

| Field | Content |
|---|---|
| ICP segment | P01 S1, solution-aware (already searches "midi sweater dress with boots") |
| Archetype | **AR-11 Educational demonstration** |
| Persuasion angle | Education that sells: a styling rule closed by the product (PB §2.2; ICP-P01 I solution-aware row) |
| Buyer motive | Wants to know *how* to wear a midi with tall boots before buying one |
| Color / refs | Green ("green sweater dress … boots" is an autocomplete pattern, ICP-P01 D1) — **new crops needed** from store image `30F9328D3C4BBDAAF666DAD820067D27.jpg` (identified as green in ICP-P01 B1; confirm color before cropping) |
| Hypothesis | A how-to frame holds viewers longer (higher hold = 100% ÷ 2-s views) than a callout frame and earns similar CTR; risk: it sells boots more than the dress |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-22 (shortened) | "Midi with tall boots? Check where the hem lands." (9) | Full length, green dress + knee-high boots; she points down at where the hem overlaps the boot top | Base (situation + mistake avoidance) |
| H02 | HK-10 | "Tall-boot owners: one detail decides if a midi works." (9) | Same frame, she lifts the hem slightly, then lets it fall over the boot | Base (curiosity; library says curiosity "waits") |
| H03 | HK-08 | "Got tall boots? Three pieces, one outfit. Watch." (8) | Same frame; boots and dress, she adds small earrings (third piece) | Base (callout + build) |

(The library's contrarian HK-12 "Skip the mini sweater dress" is **not used**: it would argue against our own P02.)

**Storyboard**

| Shot | Time | Camera | Action | Dress must visibly… | Line |
|---|---|---|---|---|---|
| 1 | 0–3 s | Full length | Hook visual | Hem overlapping boot top | Hook |
| 2 | 3–7 s | Low framing, knee to floor | Shifts weight; the hem stays over the boot shaft | Mid-calf midi hem over the boot | "See how the hem overlaps the boot? No gap." |
| 3 | 7–11 s | Full length, walking | Slit opens over the boot | Slit in stride | "The slit opens over the boot when you walk." |
| 4 | 11–15 s | Close-up | Smiles | Cable texture | "Ember and Clove, about forty-four to forty-seven inches. Link's here." |

**Narration scripts** — H01 (37): "Midi with tall boots? Check where the hem lands. / See how the hem overlaps the
boot? No gap. / The slit opens over the boot when you walk. / Ember and Clove, about forty-four to
forty-seven inches. Link's here." · H02 (37) and H03 (36) swap only line 1.
**Accuracy note:** where the hem lands depends on the wearer's height and boot height; the line only describes what is
on screen, and the spoken length gives the fact. Never state the presenter's height (it would be invented).
**Sound design:** §0.3. **CTA:** as shot 4.
**Post caption (124 chars):** "How a midi meets tall boots: hem over the boot, slit for walking. Green cable knit, about 44–47 in long. AI-generated video."
**Compliance check:** C1 ✓ · C2 ✓ · C3 ✓ (length, slit) · C4 ✓ (all three name the situation) · C5 ✓ · C6 ✓ · C7 ✓ ·
C8 ✓ · C9 ✓ · C10 ✓.

### EC-P01-A09 — "Three honest things" (round 1)

| Field | Content |
|---|---|
| ICP segment | P01 S1 comparison shoppers / product-aware; skeptical of ad stores and AI ads (ICP-P01 J: "is this store legit?", "AI ad") |
| Archetype | **AR-14 Three honest things (transparency)** |
| Persuasion angle | Risk reduction and honesty as differentiation: length, fabric and delivery stated up front |
| Buyer motive | Avoid a regretted order from an unknown store |
| Color / refs | Caramel — existing `assets/EC-P01-A02-H01-V01/ref1_dress_neck_down.jpg`, `ref2_cable_slit_closeup.jpg` |
| Hypothesis | Stating length, fabric and delivery up front lowers CTR vs A05 but raises CVR on clicks enough to give an equal or lower cost per ATC, and fewer "where is my order"/length complaints per order (tracked later) |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-36 (new) | "Before you order this midi, three honest things." (8) | Full length, caramel dress + black knee-high boots, walking toward camera, holding up three fingers | Base (situation: about to order) — **round 1** |
| H02 | HK-37 (new) | "Here's exactly how long this midi is." (7) | Full length; she runs one hand from the waistband down to the hem at mid-calf over the boot | **TEST ARM (a): demo-first** — backlog |
| H03 | HK-38 (new) | "Comparing sweater dresses tonight? Here are the facts." (8) | She stands up from the arm of a sofa (dress fully in frame), faces camera | Base (situation callout) — backlog |

**Storyboard**

| Shot | Time | Camera | Action | Dress must visibly… | Line |
|---|---|---|---|---|---|
| 1 | 0–3 s | Full length | Hook visual | Hem over boots; whole dress | Hook |
| 2 | 3–7 s | Full length | Hand from waistband down to the hem at mid-calf | Midi length | "One: it's a midi, about forty-four to forty-seven inches." |
| 3 | 7–11 s | Close on hand on the cable skirt, rising to her face | Touches the knit | Cable texture, ribbed waist | "Two: acrylic-blend knit. Three: delivery's about two to three weeks." |
| 4 | 11–15 s | Mid-shot | Steps back, smiles | Whole dress | "It's Ember and Clove, fifty-two ninety-nine. Link's right here." |

**Narration scripts**
- **H01 (36):** "Before you order this midi, three honest things. / One: it's a midi, about forty-four to forty-seven inches. /
  Two: acrylic-blend knit. Three: delivery's about two to three weeks. / It's Ember and Clove, fifty-two ninety-nine.
  Link's right here."
- **H02 (36):** "Here's exactly how long this midi is. / About forty-four to forty-seven inches, shown here with tall boots. /
  It's an acrylic-blend knit, and delivery's about two to three weeks. / Ember and Clove, fifty-two ninety-nine. Link's
  right here."
- **H03 (34):** "Comparing sweater dresses tonight? Here are the facts. / It's a midi, about forty-four to forty-seven inches.
  / Acrylic-blend knit, and delivery's about two to three weeks. / It's Ember and Clove, fifty-two ninety-nine. Link's
  right here."

**Sound design:** §0.3; calm, matter-of-fact delivery (the STYLE string says "excited"; acceptable, but reject an
over-hyped read that undercuts the honest tone).
**Demonstration / rejection:** shared P01 list; reject if the three-finger gesture renders with wrong finger counts or
if any number is garbled.
**CTA:** "It's Ember and Clove, fifty-two ninety-nine. Link's right here."
**Post caption (127 chars):** "The fine print, up front: about 44–47 in long, acrylic-blend knit, sizes S–XL, 7-day returns. AI-generated video."
**Optional 25 s version (natural length for this archetype; test c candidate, ≈ $8.10):** add "Four: seven-day
returns." and "Sizes small to extra large; the size chart's on the page." (P01 sizes are a page fact; only once a size
chart is live) and "Two dresses ship free." ≈ 55 words.
**Compliance check:** C1 ✓ · C2 ✓ · C3 ✓ (length, acrylic blend, delivery, price) · C4 ✓ H01/H03, H02 TEST ARM · C5 ✓ ·
C6 ✓ · C7 ✓ · C8 ✓ · C9 ✓ ("seven-day returns" caption only; no "free"/"easy") · C10 ✓.

---

## 2. P02 Turtleneck Rib Knit Sweater Dress — five concepts

Shared P02 demonstration requirements: chunky vertical rib; **folded turtleneck**; dropped shoulders; long full sleeves
with ribbed cuffs; loose fit hanging straight from the shoulders, no waist seam or belt; ribbed hem at **upper-to-mid
thigh, always over opaque tights or leggings (never bare legs)**. Reject if the model lengthens it toward the knee
(that would misrepresent a 27–28 in garment), adds a waist, renders it fitted/bodycon, or drifts color (burgundy must
not turn red or purple). Never show it as a stand-alone dress.

### EC-P02-A05 — "Whole outfit, three pieces" (lead; round 1, test (a))

| Field | Content |
|---|---|
| ICP segment | P02 S1 Outfit-formula seeker (ICP-P02 F1, priority 1) |
| Archetype | **AR-05 Outfit build / progression** (dress + tights + boots → turtleneck fold → bag → out) |
| Persuasion angle | Decision ease: a pre-decided formula ("tights, boots, this") — ICP-P02 A2, evidence Strong |
| Buyer motive | Wants to look styled in one step on cold days |
| Color / refs | Burgundy — `assets/EC-P02-A03-H01-V01/ref1_dress_neck_down.jpg`, `ref2_turtleneck_knit_closeup.jpg` (exist) |
| Hypothesis | Framing the dress as a complete tights-and-boots outfit gives a lower cost per ATC than the comfort frame (A06) for the same audience (ICP-P02 A2 hypothesis). **Within the concept (test a):** a callout question (H01) vs a demo-first line that narrates the visible formula (H02), everything else identical |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-39 (new; callout form of HK-17) | "Tights and boots all winter? This is your dress." (9, ≈3.6 s) | Full length by the arched mirror, burgundy dress over opaque black tights + black knee-high boots; she turns from the mirror to the camera | Base (callout) — **round 1** |
| H02 | HK-17 | "Black tights, tall boots, and this. That's the whole outfit." (10, ≈4 s, long) | **Identical** to H01 | **TEST ARM (a): demo-first** (narrates the formula on screen, no buyer callout) — **round 1** |
| H03 | HK-06 | "Getting dressed in two minutes tomorrow? Watch." (7) | Same outfit at the front door, she lifts a tote onto her shoulder | Base (situation) — backlog |

**Storyboard** — shots 2–4 identical across hooks.

| Shot | Time | Camera | Action / setting | Wardrobe & styling | Dress must visibly… | Line |
|---|---|---|---|---|---|---|
| 1 | 0–3 s | Full length, static, mirror in frame | Hook visual; warm apartment | Burgundy P02, opaque black tights, black knee-high boots, gold hoops | Hem at mid-thigh over tights; loose straight hang | Hook |
| 2 | 3–7 s | Mid-shot | Folds the turtleneck down once, pushes up the slouchy sleeves; eyes on the knit | Same | Folded turtleneck, dropped shoulder seam, chunky rib | "Slouchy turtleneck, dropped shoulders, loose fit." |
| 3 | 7–11 s | Full length, side view | Picks up a small crossbody bag and walks; hem over tights | Same + crossbody bag | Short length over tights (side profile) | "It's a short one, easy over tights and boots." |
| 4 | 11–15 s | Walk-in close-up | Smiles | Same | Rib texture | "It's Ember and Clove, forty-four ninety-nine. Link's right here." |

**Narration scripts**
- **H01 (33):** "Tights and boots all winter? This is your dress. / Slouchy turtleneck, dropped shoulders, loose fit. / It's a
  short one, easy over tights and boots. / It's Ember and Clove, forty-four ninety-nine. Link's right here."
- **H02 (34):** "Black tights, tall boots, and this. That's the whole outfit. / Slouchy turtleneck, dropped shoulders, loose
  fit. / It's a short one, easy over tights and boots. / It's Ember and Clove, forty-four ninety-nine. Link's right here."
- **H03 (31):** "Getting dressed in two minutes tomorrow? Watch. / Slouchy turtleneck, dropped shoulders, loose fit. / It's a
  short one, easy over tights and boots. / It's Ember and Clove, forty-four ninety-nine. Link's right here."

**Sound design:** §0.3.
**Demonstration / rejection:** shared P02 list; the side profile in shot 3 must show the hem over tights (it is the
honest length proof); reject if the bag hides the hem.
**CTA:** "It's Ember and Clove, forty-four ninety-nine. Link's right here."
**Post caption (132 chars):** "Black tights, tall boots, slouchy turtleneck sweater dress. Mini length, about 27–28 in. 7 colors. AI-generated video. #sweaterdress"
**Optional 25–30 s version (test c, ≈ $8.10–9.72):** same opening · turtleneck fold close-up · side profile walk with
the length fact ("It's about twenty-seven inches, so tights are part of the look.") · fabric fact ("Acrylic and
polyester, with an angora blend.") · AOV CTA ("Forty-four ninety-nine; two ship free. Link's right here."). ≈ 60 words.
**Compliance check:** C1 ✓ · C2 ✓ (no "soft", "warm") · C3 ✓ (slouchy, turtleneck, dropped shoulders, loose fit, "easy
over tights and boots", price) · C4 ✓ H01/H03; H02 TEST ARM · C5 ✓ (tights and boots visible) · C6 ✓ · C7 ✓ (no sizes;
caption gives length, not size range) · C8 ✓ · C9 ✓ · C10 ✓.

### EC-P02-A06 — "Pajamas that pass" (round 1)

| Field | Content |
|---|---|
| ICP segment | P02 S2 Comfort-first "pajamas that pass" dresser (ICP-P02 F2) |
| Archetype | **AR-06 Honest outfit swap, adapted** ("couch to door" in the same dress; the loungewear-first shot is dropped because the dress must be on the body in frame 1) |
| Persuasion angle | Comfort that still reads as dressed (ICP-P02 A1) — the competing motive to A05's outfit formula |
| Buyer motive | Lives in leggings; wants to leave the house looking put together with no effort |
| Color / refs | Burgundy — existing P02 refs |
| Hypothesis | Comfort framing beats outfit framing (A05) on CVR on clicks because comfort is the deeper motive (ICP-P02 A1 hypothesis); A05 vs A06 tells us which motive sells |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-03 | "Living in leggings, but want to look dressed?" (8) | On the couch cross-legged in the dress over opaque black leggings, holding a mug, looks up at camera | Base (problem + situation) — **round 1** |
| H02 | HK-07 | "Spending Saturday in loungewear? Here's the version that passes." (10, long) | Same couch; she stands up from it in one motion (motion onset) | Base (situation) — backlog |
| H03 | HK-16 | "Cold morning, school run, and nothing to throw on?" (9) | Morning at the front door, dress over leggings, she grabs keys and a travel mug (no child in frame) | Base (frustration; situation) — backlog |

**Storyboard**

| Shot | Time | Camera | Action | Wardrobe | Dress must visibly… | Line |
|---|---|---|---|---|---|---|
| 1 | 0–3 s | Mid-wide, eye level | Hook visual; living room | Burgundy P02, opaque black leggings, socks; hair loosely tied back | Loose knit, turtleneck, length over leggings | Hook |
| 2 | 3–7 s | Mid-shot, standing | Pushes up sleeves; the knit falls straight from the shoulders | Same | Loose hang, dropped shoulders | "It's a loose, slouchy sweater dress with a folded turtleneck." |
| 3 | 7–11 s | Full length at the front door | Already in black ankle boots; grabs keys and a tote | + ankle boots, tote | Short length over leggings | "Add leggings and boots, and you're out the door dressed." |
| 4 | 11–15 s | Walk-in close-up | Smiles | Same | Rib texture | "It's Ember and Clove, forty-four ninety-nine. Link's right here." |

**Narration scripts**
- **H01 (37):** "Living in leggings, but want to look dressed? / It's a loose, slouchy sweater dress with a folded turtleneck. /
  Add leggings and boots, and you're out the door dressed. / It's Ember and Clove, forty-four ninety-nine. Link's right
  here."
- **H02 (37):** "Spending Saturday in loungewear? Here's the version that passes. / It's a loose, slouchy
  sweater dress with a folded turtleneck. / Add leggings and boots, and you're out the door dressed. / Ember and Clove,
  forty-four ninety-nine. Link's right here."
- **H03 (37):** "Cold morning, school run, and nothing to throw on? / It's a loose, slouchy sweater dress with a folded
  turtleneck. / Add leggings and boots, and you're out the door dressed. / Ember and Clove, forty-four ninety-nine.
  Link's right here."

**Sound design:** §0.3; the mug set down and keys picked up are welcome incidental sounds.
**Demonstration / rejection:** shared P02 list; presenter and dress must stay identical between couch and door (AR-06
identity risk); reject anything that reads as a body before/after.
**CTA:** "It's Ember and Clove, forty-four ninety-nine. Link's right here."
**Post caption (121 chars):** "Loose, slouchy turtleneck sweater dress to wear over leggings and boots. Mini length, about 27–28 in. AI-generated video."
**Optional 25 s:** add a seated cross-legged shot and "It's cozy, and it's an acrylic and polyester knit with an angora
blend." ("cozy" is page wording; never "soft"). ≈ 50 words.
**Compliance check:** C1 ✓ · C2 ✓ ("cozy" only in the optional version; no "soft", no "not itchy", no "feels like
pajamas" material claim) · C3 ✓ · C4 ✓ · C5 ✓ (loungewear situation: couch, leggings, mug) · C6 ✓ · C7 ✓ · C8 ✓ · C9 ✓ ·
C10 ✓.

### EC-P02-A07 — "Holiday dinner, nothing tight at the waist" (round 1, time-boxed)

| Field | Content |
|---|---|
| ICP segment | P02 S3 Holiday-season eater (ICP-P02 F3) |
| Archetype | **AR-15 Occasion outfit** |
| Persuasion angle | Occasion + comfort at the table, with an honest delivery line (ICP-P02 A4) |
| Buyer motive | Wants to look dressed for family dinners and stay comfortable through the meal |
| Color / refs | Burgundy — existing P02 refs |
| Time box | **No "Thanksgiving" wording** (its window closes ~Nov 1–2 and this can't launch before ~Oct 28). "Holiday dinner" wording until ~Nov 20–25 |
| Hypothesis | An occasion frame lifts CVR on clicks vs A05 during November–December (ICP-P02 A4) |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-32 | "Hosting a holiday dinner this year? Look at this." (9) | Full-length side view setting plates on a holiday table, burgundy dress over black tights + knee-high boots, then looks at camera | Base (callout) — **round 1** |
| H02 | HK-02 | "Holiday dinners coming up, and every dress has a waistband?" (10, long) | Same table; she pulls out a chair | Base (problem + situation) — backlog |
| H03 | HK-40 (new; ICP-P02 A4 hook) | "Holiday dinner dress, nothing tight at the waist." (8) | She sits at the table and leans to reach a dish; loose knit hangs away | **TEST ARM (a): demo-first** — backlog |

**Storyboard** (setting: warm dining room in the evening, table set for a holiday dinner, candles, simple greenery)

| Shot | Time | Camera | Action | Dress must visibly… | Line |
|---|---|---|---|---|---|
| 1 | 0–3 s | Full length, side | Hook visual | Whole dress over tights; table must not hide the hem | Hook |
| 2 | 3–7 s | Mid-shot, seated | Sits, reaches across the table for a dish | Loose hang at the waist when seated | "Loose fit, nothing tight at the waist." |
| 3 | 7–11 s | Full length | Stands beside the table | Hem at mid-thigh over tights | "Burgundy, slouchy turtleneck, with tights and boots." |
| 4 | 11–15 s | Walk-in close-up | Friendly smile | Turtleneck, rib | "It's Ember and Clove. Delivery's about two to three weeks. Link's right here." |

**Narration scripts**
- **H01 (36):** "Hosting a holiday dinner this year? Look at this. / Loose fit, nothing tight at the waist. / Burgundy, slouchy
  turtleneck, with tights and boots. / It's Ember and Clove. Delivery's about two to three weeks. Link's right here."
- **H02 (35):** "Holiday dinners coming up, and every dress has a waistband? / Loose fit, nothing tight at the waist. /
  Burgundy, slouchy turtleneck, with tights and boots. / Ember and Clove. Delivery's about two to three weeks. Link's
  here."
- **H03 (35):** "Holiday dinner dress, nothing tight at the waist. / It's a loose fit, with a folded turtleneck. / Burgundy,
  slouchy, with tights and boots. / It's Ember and Clove. Delivery's about two to three weeks. Link's right here."

**Sound design:** §0.3; cutlery and plates are fine; no music.
**Demonstration / rejection:** shared P02 list; no food close-ups or eating; reject any "after the meal" body framing.
"Nothing tight at the waist" describes the loose fit and the absence of a waist seam seen in the store photos;
**verify on a physical sample** before scaling.
**CTA:** "It's Ember and Clove. Delivery's about two to three weeks. Link's right here."
**Post caption (121 chars):** "Holiday dinner outfit: loose turtleneck sweater dress, black tights, boots. 7 colors. AI-generated video."
**Compliance check:** C1 ✓ · C2 ✓ (no urgency; no arrival promise) · C3 ✓ (loose fit; no waist seam per photos — flagged
for sample check) · C4 ✓ H01/H02; H03 TEST ARM · C5 ✓ (holiday table) · C6 ✓ (no tummy/eating-body claims) · C7 ✓ ·
C8 ✓ · C9 ✓ · C10 ✓.

### EC-P02-A08 — "Three honest things" (backlog; best as 25 s)

| Field | Content |
|---|---|
| ICP segment | P02 S1/S2 shoppers who distrust social-ad stores and AI ads (ICP-P02 D7, A8) |
| Archetype | **AR-14 Three honest things (transparency)** |
| Persuasion angle | Pre-empt the top objections (length, fiber, delivery) |
| Buyer motive | Avoid a regretted purchase |
| Color / refs | Burgundy — existing P02 refs |
| Hypothesis | Transparency gives a cost per ATC no worse than A05 and fewer length/delivery complaints per order (ICP-P02 A8) |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-41 (new; AR-14 opener) | "Before you order this sweater dress, three honest things." (9) | Full length, dress over black tights + boots, holding up three fingers | Base (situation: about to order) |
| H02 | HK-23 | "Ordering a short sweater dress? Check the length first." (9) | Full length; she places a hand at the hem at mid-thigh | Base (situation + mistake avoidance) |
| H03 | HK-42 (new) | "Here's exactly how short this sweater dress is." (8) | Side profile, hem over tights, hand marking it | **TEST ARM (a): demo-first** |

**Storyboard (15 s)**

| Shot | Time | Action | Dress must visibly… | Line |
|---|---|---|---|---|
| 1 | 0–3 s | Hook visual | Whole dress over tights | Hook |
| 2 | 3–7 s | Side profile, hand at hem | Hem at mid-thigh | "One: it's short, about twenty-seven inches. Wear tights." |
| 3 | 7–11 s | Close-up of rib and turtleneck | Chunky rib | "Two: acrylic and polyester, with an angora blend." |
| 4 | 11–15 s | Mid-shot, smile | — | "Three: delivery's about two to three weeks. Link's here." |

**Narration scripts** — H01 (34): "Before you order this sweater dress, three honest things. / One: it's short, about
twenty-seven inches. Wear tights. / Two: acrylic and polyester, with an angora blend. / Three: delivery's about two to
three weeks. Link's here." · H02 (32): "Ordering a short sweater dress? Check the length first. / It's about twenty-seven
inches, so wear tights. / It's acrylic and polyester, with an angora blend. / Delivery's about two to three weeks.
Link's here." · H03 (31): "Here's exactly how short this sweater dress is. / About twenty-seven inches, so it's a tights
dress. / Acrylic and polyester, with an angora blend. / Delivery's about two to three weeks. Link's here."
**Note:** no price or brand fits in 15 s; the **25 s version is the recommended format** for this archetype (test c
variable, ≈ $8.10): add "It's Ember and Clove, forty-four ninety-nine, and two ship free." and "Seven-day returns."
**Sound design:** §0.3, calm delivery. **CTA:** "Link's here." (15 s) / price + brand (25 s).
**Post caption (124 chars):** "Before you order: about 27–28 in long, acrylic/polyester with an angora blend, 7-day returns. AI-generated video."
**Compliance check:** C1 ✓ · C2 ✓ (fiber stated; never "not itchy"; if comments ask about itch, reply with the fiber
facts only) · C3 ✓ · C4 ✓ H01/H02; H03 TEST ARM · C5 ✓ · C6 ✓ · C7 ✓ · C8 ✓ · C9 ✓ · C10 ✓.

### EC-P02-A09 — "Errands or dinner: same dress, two ways" (backlog; needs new refs)

| Field | Content |
|---|---|
| ICP segment | P02 S2 (with S1 overlap): wants value per piece across casual and evening plans |
| Archetype | **AR-17 One dress, several ways** (two-look version to limit drift) |
| Persuasion angle | Versatility / use-occasion expansion (AR-09/AR-17 mechanism, D) |
| Buyer motive | Justify the purchase by wearing it for more than one kind of day |
| Color / refs | Khaki — **new crops needed** from `assets/EC-P02-A03-H01-V01/src_1A1043B235C30627DFD80E2CD435A129.jpg` (store image `1A1043B235C30627DFD80E2CD435A129.jpg`, khaki with a coffee cup): neck-down crop + rib/turtleneck close-up, face excluded. Bare legs in the photo: the prompt must add leggings/tights |
| Hypothesis | Showing two plans in one video raises hold and CTR vs a single-look ad; risk: two scenes in one generation drift (presenter, dress) |

**Hooks**

| Hook | HK | Opening line | First-frame visual | Status |
|---|---|---|---|---|
| H01 | HK-21 | "Errands or dinner out? Same dress, two ways." (8) | Full length, khaki dress over black leggings + white sneakers, tote and coffee cup | Base (situation) |
| H02 | HK-26 | "Saturday errands in a sweater dress? Yes, with sneakers." (9) | Same, walking toward camera | Base (situation) |
| H03 | HK-13 | "Tights season? A sweater dress should be short." (8) | Same, side profile showing the short hem | Base (contrarian; situation) |

**Storyboard** — 1 (0–3 s) day look, hook · 2 (3–7 s) close-up of folded turtleneck and rib: "Slouchy turtleneck,
chunky rib, loose fit." · 3 (7–11 s) cut to the same room in evening light, same dress over black tights + knee-high
boots, gold earrings: "Tights and tall boots, and it's dinner." · 4 (11–15 s) close-up: "It's Ember and Clove,
forty-four ninety-nine. Link's right here."
**Narration scripts** — H01 (30): "Errands or dinner out? Same dress, two ways. / Slouchy turtleneck, chunky rib, loose fit.
/ Tights and tall boots, and it's dinner. / It's Ember and Clove, forty-four ninety-nine. Link's right here." · H02 (31)
and H03 (30) swap line 1.
**Sound design:** §0.3. **Rejection:** dress or presenter changes between looks; khaki drifting to gray/camel; bare legs.
**Post caption (117 chars):** "One sweater dress, two ways: sneakers and leggings for errands, tights and tall boots for dinner. AI-generated video."
**Compliance check:** C1 ✓ · C2 ✓ · C3 ✓ · C4 ✓ · C5 ✓ (errands props) · C6 ✓ · C7 ✓ · C8 ✓ · C9 ✓ · C10 ✓.
**OPTIONAL — owner approval:** a three-look 25–30 s version (sneakers / ankle boots / tall boots + coat) — higher drift risk.

---

## 3. First-round shortlist (generate first) and test design

### 3.1 Videos to generate (8 × 15 s)

| # | Creative ID | Concept / hook | Why first | Refs | Est. cost |
|---|---|---|---|---|---|
| 1 | EC-P01-A05-H01-V02 | Tall boots, HK-31 callout | P01's strongest angle (ICP-P01 A1, Strong); control arm of test (a) | exist | $4.86 |
| 2 | EC-P01-A05-H02-V02 | Tall boots, HK-35 demo-first | Test (a) arm; identical prompt except the first line | exist | $4.86 |
| 3 | EC-P01-A06-H01-V02 | Holiday, HK-19 | Time-boxed (launch by ~Nov 5); different motive (dated event) | exist (red) | $4.86 |
| 4 | EC-P01-A09-H01-V01 | Three honest things, HK-36 | Different persuasion route (transparency) for a trust-heavy store | exist | $4.86 |
| 5 | EC-P02-A05-H01-V02 | Whole outfit, HK-39 callout | P02's strongest angle (ICP-P02 A2, Strong); control arm of test (a) | exist | $4.86 |
| 6 | EC-P02-A05-H02-V02 | Whole outfit, HK-17 demo-first | Test (a) arm | exist | $4.86 |
| 7 | EC-P02-A06-H01-V02 | Pajamas that pass, HK-03 | The competing motive (comfort vs formula), ICP-P02 round-1 pair | exist | $4.86 |
| 8 | EC-P02-A07-H01-V01 | Holiday dinner, HK-32 | Time-boxed (until ~Nov 20–25); third motive | exist | $4.86 |

**Total: 8 × $4.86 = $38.88** (estimate at $0.324/s; confirm against billing after the first run). Budget a re-roll
reserve of about two clips (+$9.72 → **$48.60 cap**). The API balance was $52.65 on 2026-10-24 before the $4.85 P02-A03
run, so check the current balance first; a top-up may be needed if more than one re-roll is required.

Not shortlisted: P01-A07 and P01-A08 (need new black/green crops), P02-A09 (needs khaki crops), P02-A08 (natural
length is 25 s; better as a round-2 length test), all H03 hooks and the non-pair H02 hooks (backlog; see the registry).

### 3.2 How the round answers (a), (b), (c)

| Question | Arms | Generation cost | How it runs (media budget = owner decision, see registry §1) |
|---|---|---|---|
| **(a)** Callout vs demo-first opening | P01: A05-H01 vs A05-H02 · P02: A05-H01 vs A05-H02 (prompts identical except line 1; same refs, presenter description, settings) | $9.72 per product ($19.44 both) | Both arms in the same ad group (cheap, directional) or as a TikTok split test (cleaner, ~2× media). Remaining confound: each arm is a separate generation, so shots 2–4 render differently |
| **(b)** Auto-captions on vs off | The same video posted twice as two Spark posts: one with TikTok auto-captions enabled, one without (start with the (a) winner, or A05-H01 by default) | **$0** | Week 2, after (a) has a direction. **Verify first** in the app that auto-captions display on Spark Ads and that a second post of the same video is eligible (TikTok originality rules, AI §9 rec 9) |
| **(c)** 15 s vs 25–30 s | The (a)/(b) winner per product vs a 25–30 s version with the same opening (outlines above) | $8.10–9.72 per product (+ re-rolls) | Round 2, only after a 15 s winner exists |

---

## 4. Optional variants that still need the owner's approval

1. **TikTok native text tool** (3–5 key words in the first 3 s, added at posting, not by us; PB H-AP-01) — a separate
   variable from auto-captions; test only after (b).
2. **Three-look P02-A09** (25–30 s) and any multi-scene version with more than two locations (drift risk).
3. **P01-A07 line "and a little leg"** (fallback line provided).
4. **Cling-averse P02 hook HK-34** ("Sweater dresses always cling on you? Watch this one hang.") — not used here: it sits
   on the body-trait boundary (library §2.13) and one AI body can't prove fit across bodies.
5. **Re-running the legacy P02-A03** without "sizes small to 3X" (would need a new generation, $4.86).

## 5. Open items before generation

- Confirm live price/colors on Shopify (§0.2) and that the Berry P01 variant has an image (no Berry ad until it does).
- New reference crops for Black (P01), Green (P01), Khaki (P02) before A07, A08, A09 can be specified.
- Physical sample checks still pending: P01 slit height and length on a body; P02 hem length and "no waist seam".
- `make_tryon.py` logs `setting="living-room"` in the recipe even when a spec has a `setting` key; the prompt is
  correct, but the recipe tag will be wrong for A06 (P01) and A07 (P02) unless corrected by hand.
