# Market Intelligence 2.0: creative and competitive research audit (Phase A)

Date: 2026-10-28. Scope: the creative research (Kalodata video study and related Kalodata studies), seasonality
claims, Meta Ad Library data, TikTok Creative Center Top Ads, rights and retention of the stored material, and how
research findings flow into the Content Studio. Engineering, data quality and the product model are covered by
other auditors.

Method: read the reports, scripts and logs. Re-analysed `video_features`, `video_elements`, `video_audio` and
`videos` in `research/kalodata/kalodata.db` with read-only connections (`mode=ro`). Rebuilt the candidate selection
from `scripts/video_pilot.py` and matched it against `video_study.log`, `video_study_2.log` and `video_pilot.log`.
Profiled the Meta and TikTok CSVs. **No API calls, downloads or web access. No database, script, report or media
file was changed.** Scratch scripts were deleted afterwards. The queries are summarised in Appendix B so anyone can
re-run them.

Labels: **[V]** = verified in this audit (recomputed or read directly from code/data). **[I]** = inference.

---

## 1. Summary

The video study is a sensible design (same product, same month, winner vs stalled video), cheap and well logged. Its
headline creative findings, though, do **not** survive scrutiny as stated:

1. **Only one result survives multiple-testing correction: paid boosting** (84% of winners vs 41% of comparisons,
   43:4 discordant pairs). 152 tests were run on 91 pairs; 9 had p < 0.05 where about 7.6 would by chance. After
   Holm or Benjamini-Hochberg across all 152, only `ad=1` is significant. [V]
2. **"Person with the product in the first frame" is confounded with paid boosting.** In the 44 pairs where both
   videos had the same paid status, it is 52% vs 50% (13:12 pairs, p = 1.0). The whole effect sits in the 43 pairs
   where only the winner was boosted (74% vs 28%, 22:2). In a paired logistic model with `ad`, its odds ratio drops
   from 2.40 to 1.34 (95% CI 0.66–2.72, p = 0.43). [V]
3. **Longer videos, faster talking, more speech, text hooks and close-ups** are all non-significant after
   correction, and none differ within same-paid-status pairs (e.g. duration 23 vs 20 pairs, p = 0.76). [V]
4. **Video age was not controlled.** Winners were a median 37 days old at the end of September, comparisons 17;
   the winner is older in 81 of 91 pairs; 29 comparisons were posted in the last 10 days of the month. [V]
5. **No human check of the AI tags exists.** The tagger agreed with Kalodata's AI flag on only 8 of 17 AI videos.
   [V]
6. **Some study results have already become production rules** (talking-speed band 2.9–3.8 words/s and speech share
   ≥ 70% in `studio/bible/rules.yaml`, a rebuilt ad "from the 91-pair study", and the cycle-1 ad ranking) although
   the underlying differences are not significant, and in apparel pairs talking speed shows nothing (10 of 20
   pairs). [V for the rules and the ad; I that the band comes from the study]
7. **Seasonality**: every pattern is one observed year (Nov 2025 – Sep 2026, October 2025 incomplete). None is a
   validated recurring pattern yet. One applied claim is wrong in kind: "our sweater dresses fall in a type that
   peaks in May". The "dresses" bucket is mostly spring and summer dresses. [V/I]
8. **Meta**: no impressions, spend or results are observed for US commercial ads. The "100 ads, longest-running
   first" list is actually the newest ads: median 0.1 days (about 2.4 hours) running. "Current winners" and "spend
   signals" are inferences the source cannot support. [V]
9. **TikTok Top Ads**: well caveated in its own report (curated sample, CTR rank only). Keep the caveats attached
   wherever the findings are reused. [V]
10. **Rights**: 1.6 GB of third-party videos are still stored (1.2 GB study + 416 MB Top Ads), although three
    documents said they would be deleted. 6,106 TikTok Shop review records with reviewer names and user IDs sit in
    raw JSON. `research/` is in neither git nor the nightly backup. [V]

What should be kept: the paired design, the exact sign tests, the extraction pipeline, the failure logging, the
honest music null result, the TikTok research's evidence grades and pre-registered hypothesis registry, and the
evidence levels in `learnings.md` (section 12).

### Key facts found during the audit

| Area | Finding | Evidence |
|---|---|---|
| Study size | 91 complete pairs, 182 videos, 25 categories (Womenswear 4 pairs, apparel group 22) | `video_features` (185 rows, 3 orphans) [V] |
| Paid strata | 43 winner-only paid, 33 both paid, 11 both organic, 4 comparison-only paid | `ad` flag per pair [V] |
| Survives correction | `ad=1` only (Holm p < 0.001) | 152-test family, Appendix A [V] |
| Person with product at 0 s | +23 pts (95% CI +9 to +37) overall; +2 pts in same-status pairs | bootstrap over pairs; strata table [V] |
| Outcome metric | Total September sales (winner) vs views band (comparison); per-1,000-views can be computed | `revenue`, `views` [V] |
| Sales per 1,000 views | Winners $23.76 median, comparisons $3.12; 44 of 91 comparisons sold $0 | recomputed [V] |
| Video age | Winners 37 days, comparisons 17 days median at Sep 30; winner older in 81/91 pairs | `videos.publish_date` [V] |
| Download failures | 20 candidate videos failed (16 slideshows, 4 link/403) and were replaced or the slot was dropped | logs vs rebuilt candidate lists [V] |
| Tag checks | No hand check; AI-look tag matched Kalodata's AI flag on 8/17 | `video_features` vs `videos.ai_video` [V] |
| Meta sample age | 100-ad list: median 0.1 days running, 75th percentile 0.2, max 5.3 | `ad_library_100_2026-10-27.csv` [V] |
| Stored third-party media | 205 study folders (1.2 GB) + 78 Top Ads (416 MB) + 162 analysis files (18 MB) | `du` [V] |

---

## 2. Video study: design and selection

### 2.1 How pairs were chosen [V: `scripts/kalodata_core.py` 158–172, `scripts/video_pilot.py` `pick_pairs`]

- **Products**: 100 products with full September 2026 video lists. In each category, the products nearest to
  positions 1, 50, 200 and 450 of that category's September top 500. Lists were paged by revenue (descending) and
  capped at 5 × 100 videos. 4 of the 99 products in the table hit the 500 cap, so their low-revenue tail (the pool
  for the median used below) is cut off.
- **Winner**: the product's top-revenue September video with ≥ 5,000 views. The #2 and #3 videos were backups.
  The #1 video was used in 88 of 91 pairs.
- **Comparison**: another video of the same product with ≥ 500 views and ≤ 10% of the winner's views, nearest
  to the product's median log-views. Four backups. The 94 eligible products had a median of 184 eligible
  comparison videos each.
- **Download**: public TikTok links via yt-dlp first, for winners and comparisons alike. Kalodata's paid URL was
  only a backup for winners (1.5 credits = 3 videos in the study run). The pilot's Kalodata attempt for comparisons
  failed 10 of 10 (HTTP 403). Note: the brief's description "winners downloaded via Kalodata" applies to the pilot,
  not the study.

### 2.2 What was and wasn't held fixed

| Factor | Controlled? | Evidence |
|---|---|---|
| Product, seller, category, listing | Yes (same product ID) [V] | TikTok Shop product IDs are seller-specific [I] |
| Month of outcome | Yes, September 2026 revenue and views [V] | pull `date_range = 2026-09` |
| Price | Same listing; price changes during the month unknown [I] | no price-history field |
| **Paid boosting** | **No.** 47 of 91 pairs differ in paid status [V] | `ad` flag |
| **Video age / exposure time** | **No.** Winners 37 days old at Sep 30 (31 posted before August), comparisons 17 days (79 of 93 posted in September, 29 in the last 10 days, 10 in the last 3) [V] | `publish_date` |
| Creator | No. Only 2 pairs share a creator. Creator account age 552 vs 460 days median. Follower counts aren't in the data [V] | `belonged_creator_handle`, `creator_debut` |
| Format | Partly. Slideshow/photo posts were excluded (no picture), so findings don't cover photo carousels [V] | `has_picture()` |
| Language | No. Whisper is forced to English; at least 6 transcripts contain Spanish words [V] | `transcribe(..., language="en")` |

Exposure matters because a comparison posted on 28 September had 2–3 days to collect September views. Comparison
views by age: 672 (≤ 7 days old), 635 (8–14), 879 (15–30), 4,585 (31–60), 12,390 (> 60). Part of "stalled" is
"new". [V]

"Winner" is relative: 1 winner sold $0 (Computers & Office, 11,965 views) and 3 sold under $1K. Median winner sales
$12,105 on 553K views. Median comparison sales $11 on 879 views. [V]

### 2.3 Outcome metric: sales or sales per view?

The selection uses **revenue for the winner and a views band for the comparison**, so the study compares
high-reach with low-reach videos. Sales per 1,000 views **can** be computed from the stored `revenue` and `views`
[V]:

| | Winners | Comparisons |
|---|---|---|
| Median $ per 1,000 views, all 91 pairs | 23.76 | 3.12 |
| Pairs where winner's $/1K is higher / lower | 61 / 29 | |
| Comparisons with $0 sales | | 44 of 91 |
| Median $/1K, the 47 pairs where the comparison sold anything | 23.43 | 27.98 |

So where comparisons sold anything they converted views about as well as winners. That supports the pilot's
"winners win on reach". But at ~900 views and ~$24 per 1,000, a comparison is expected to make about one sale, so
$0 is normal noise. Conversion per view can't be judged for half the comparisons. [V numbers, I interpretation]

### 2.4 Selection bias from download availability

The database has **no attempts table**: failures exist only in the logs. Reconstruction (rebuilt candidate lists
matched to the logs) [V]:

| | Winner candidates | Comparison candidates |
|---|---|---|
| Processed | 92 (88 first choice, 4 backup #2) | 93 (88 first choice, 5 backup #2) |
| Failed: no picture (slideshow/photo post) | 8 | 8 |
| Failed: yt-dlp error | 1 | 1 |
| Failed: yt-dlp error, then Kalodata 403 | 2 | 0 |
| Median views / sales, processed | 523K / $11.9K | 874 / $11 |
| Median views / sales, failed | 409K / $5.8K | 515 / $0 |

- Slots with no usable video: Muslim Fashion winner (2 products), Books winner, Menswear comparison. That leaves
  3 orphan rows, and Luggage & Bags had no comparison candidate at all. 5 products had no video ≥ 5,000 views.
- The slideshow exclusion removed real winners, including a $160.8K / 13.7M-view video, plus all 3 candidates for
  one Muslim Fashion product. The study says nothing about photo posts. [V]
- Failed comparisons were slightly lower-view than processed ones (515 vs 874 median). Failed winners were
  slightly smaller. The bias looks small, but it can only be assessed because the logs happened to be kept. [V/I]

---

## 3. Paid vs organic re-analysis

Kalodata's `ad` flag marks videos that had paid traffic in the period. Among paid videos, `ad_view_ratio` (share of
views from ads) is a median of 20% for winners and 52% for comparisons. `ad_revenue_ratio` is **exactly 80.0** for
54% of paid winners and 68% of paid comparisons, which looks like a Kalodata cap or model estimate, not a
measurement. Treat it as modelled. [V]

### 3.1 Within-stratum paired results (exact sign test on discordant pairs) [V]

| Feature | All 91 | Both paid (33) | Both organic (11) | Same status (44) | Winner-only paid (43) |
|---|---|---|---|---|---|
| First frame = person with product | 63% vs 40%, 36:15, p=0.005 | 55% vs 39%, 12:7, p=0.36 | 45% vs 82%, 1:5, p=0.22 | 52% vs 50%, 13:12, p=1.0 | 74% vs 28%, 22:2, p<0.001 |
| Person at 0 s (face or with product) | 73% vs 53%, 32:14, p=0.011 | 64% vs 58%, 9:7, p=0.80 | 45% vs 91%, 0:5, p=0.06 | 59% vs 66%, 9:12, p=0.66 | 84% vs 37%, 22:2, p<0.001 |
| On-screen text hook | 74% vs 60%, 24:12, p=0.065 | 73% vs 64%, 8:5, p=0.58 | 73% vs 73%, 2:2 | 73% vs 66%, 10:7, p=0.63 | 72% vs 58%, 11:5, p=0.21 |
| Detail close-ups | 76% vs 65%, 19:9, p=0.087 | 67% vs 67%, 5:5 | 73% vs 64%, 2:1 | 68% vs 66%, 7:6, p=1.0 | 84% vs 65%, 11:3, p=0.057 |
| First frame = product alone | 11% vs 25%, 8:21, p=0.024 | 6% vs 18%, 2:6, p=0.29 | 36% vs 0%, 4:0, p=0.13 | 14% vs 14%, 6:6 | 9% vs 40%, 2:15, p=0.002 |
| Duration (median s; pairs winner longer:shorter) | 34.4 vs 24.4, 55:34, p=0.033 | 37.4 vs 30.8, 19:14, p=0.49 | 17.2 vs 27.6, 4:6, p=0.75 | 37.2 vs 30.2, 23:20, p=0.76 | 31.2 vs 20.4, 29:13, p=0.020 |
| Words per second | 3.68 vs 3.11, 52:34, p=0.066 | 3.85 vs 3.17, 21:12, p=0.16 | 2.44 vs 3.26, 6:4, p=0.75 | 3.84 vs 3.19, 27:16, p=0.13 | 3.42 vs 3.07, 21:18, p=0.75 |
| Speech share | 0.88 vs 0.82, 52:33, p=0.050 | 0.91 vs 0.85, 20:12, p=0.22 | 0.77 vs 0.82, 5:5 | 0.88 vs 0.84, 25:17, p=0.28 | 0.84 vs 0.82, 24:15, p=0.20 |

Apparel only (22 pairs): 10 winner-only paid, 8 both paid, 2 both organic, 2 comparison-only paid. Person-at-0 s
discordant pairs: 5:0 in winner-only-paid, 3:1 in both-paid, 0:1 in both-organic. Too few to read. All 4 Womenswear
winners were paid; 3 of 4 comparisons were organic. [V]

### 3.2 Paired (conditional) logistic regression, winner vs comparison within pair [V]

| Model | Paid boost OR (95% CI) | Person-with-product OR (95% CI) |
|---|---|---|
| Paid only | 10.75 (3.86–29.94) | — |
| Person only | — | 2.40 (1.31–4.38), p=0.004 |
| Both | 9.63 (3.36–27.61) | **1.34 (0.66–2.72), p=0.43** |
| Both + log duration, text hook, close-ups | 9.75 (3.27–29.01) | 1.27 (0.60–2.69); text hook 2.22 (0.89–5.57), p=0.09; duration 1.44 (0.79–2.63); close-ups 1.61 (0.59–4.37) |

Unpaired check (different products, so weaker): among the 113 paid videos, person-with-product at 0 s is 66% of
winners vs 41% of comparisons (Fisher p = 0.015). Among organic videos, the winners are too few (15). [V]

**Reading [I]:** the creative differences show up almost only where the winner was boosted and the comparison
wasn't. The data cannot tell apart three explanations:
- sellers and affiliates boost videos that already show the product on a person, perhaps because those performed
  early;
- boosted videos come from more professional creators who also film this way;
- boosting plus format work together.

The direction in both-paid pairs (12:7) is consistent with a real but smaller effect. Detecting it would need
roughly 4× as many same-status pairs. Adjusting for `ad` may over-correct if boosting is a *result* of a good
opening, so the honest label is **"promising, unproven"**, not "rule".

---

## 4. Statistics and multiple testing

- **Tests used** [V `analyze_video_study.py`]: exact binomial sign test on discordant pairs for yes/no signals
  (paired, the exact form of McNemar's test: appropriate). For measures, a sign test on which video is higher
  (paired, but it ignores size and loses power). No effect sizes, confidence intervals or multiplicity correction
  were reported. The report's own guide, "Small p (under 0.05) = unlikely to be chance", is misleading with 152
  tests.
- **Family size**: 152 tests. That is 5 measures, 12 signals, 26 hook/format/opening values, 86 element values,
  22 apparel/non-apparel repeats and 1 music test. 9 raw p < 0.05, against 7.6 expected by chance. [V]
- **Overlap**: `first_frame=person_with_product`, `person_at_0s`, `first_frame=product_alone`,
  `product_shown_as_0s=flat_or_packshot` and `format=other` largely code the **same contrast**: product on a person
  vs product alone. 14 of the 16 `format=other` tags are comparisons, mostly flat-lays (from the tag summaries).
  They are not independent confirmations. [V]
- **Peeking**: the 73-pair interim reported close-ups p = 0.04 and duration p = 0.04 as findings. At 91 pairs
  close-ups became p = 0.09. [V log.md 10-26]
- **Survivors**: Holm across all 152: only `ad=1`. BH (FDR 5%) across all 152: only `ad=1`. BH within the 43
  "primary" tests (measures + signals + hook/format/opening): only `ad=1`. The next best are
  `first_frame=person_with_product` and `format=other` at q = 0.066. Dropping `ad` from the creative family moves
  person-with-product to q ≈ 0.10. [V]
- **Effect sizes**, paired difference in share of videos, 95% bootstrap CI over pairs (5,000 resamples) [V]:

| Feature | Difference (winners − comparisons) | 95% CI | Discordant pairs | Pair odds ratio |
|---|---|---|---|---|
| Paid boost | +43 pts | +31 to +55 | 43:4 | 10.8 |
| First frame person with product | +23 pts | +9 to +37 | 36:15 | 2.4 |
| Person at 0 s | +20 pts | +5 to +33 | 32:14 | 2.3 |
| On-screen text hook | +13 pts | +1 to +25 | 24:12 | 2.0 |
| Detail close-ups | +11 pts | 0 to +22 | 19:9 | 2.1 |
| Flat/packshot at 0 s | −11 pts | −21 to −1 | 6:16 | 0.38 |
| First frame product alone | −14 pts | −25 to −3 | 8:21 | 0.38 |
| Presenter looks AI | −5 pts | −11 to −1 | 0:5 | 0 |
| Duration | median paired difference +2.8 s | +0.2 to +9.3 | | |
| Words per second | median paired difference +0.21 | 0.00 to +0.78 | | |
| Speech share | median paired difference +0.03 | 0.00 to +0.06 | | |

Note how small the duration effect is as a *paired* difference (+2.8 s): the report's "34 s vs 24 s" compares
group medians. Every test, with raw and adjusted p, is in **Appendix A**.

---

## 5. Tag reliability

| Check | Result | Status |
|---|---|---|
| Human hand check of study tags | **None found.** The pilot planned "a hand check of a sample"; nothing in `research/`, `reports/`, `log.md` | [V] |
| Pilot accuracy (3 videos, Gemini Flash Lite) | 1 clear error (held vs worn). Haiku better on 5 pairs; subjective fields (hook type, format) disagree between models | [V VIDEO_PILOT] |
| Which model tagged each row | `tag_model` stores the *requested* model constant. OpenRouter may fall back to two Gemini models and the actual responder isn't saved | [V code] |
| AI-look tag vs Kalodata AI flag | Of 17 Kalodata-flagged AI videos the tagger called 8 "looks AI"; 2 of 168 non-AI flagged | [V] |
| Internal contradictions (185 rows) | `first_frame=product_alone` but shown worn/held: 3. `person_with_product` but not shown/flat: 4. `presenter=on_camera` but elements say no presenter: 6. `hook_type=none` despite on-screen text or ≥ 3 spoken words: 15. `try_on` in non-apparel: 3 | [V] |
| Cut detection | Histogram threshold; pilot: "still unverified frame by frame" | [V] |
| Transcripts | English forced; Spanish/other-language videos give wrong words/s | [V code, I impact] |
| Element tags (86 tests) | Perceived age, hair, makeup etc. from frame sheets; no checks; race deliberately not tagged (good) | [V] |

Consequences:
- "AI-looking presenter 2% vs 8%" (0:5 pairs) rests on a tag that misses half the known AI videos.
- The cycle-1 review claim "the AI presenter passes as real" uses the same tag. That matches the existing memory
  note: the owner's viewing, not machine tags, decides realism. [V/I]

---

## 6. Seasonality claims: observed vs validated

Data: monthly top-500 products per category, **Nov 2025 – Sep 2026** (October 2025 incomplete: median product $8K
vs $37K in November). That is one cycle, 11 usable months, and October itself is missing. Nothing below has been
seen twice, so **no claim is a validated recurring pattern.** [V]

| Claim (source) | Status | Note |
|---|---|---|
| Beauty, Womenswear, Health are the top 3 every month (CATEGORY_SEASONALITY §1) | Observed, 11 months | Ranking, not seasonality; fine |
| Toys Q4 2–3× any other quarter; Nov/Dec biggest months overall (EXTRA_INSIGHTS §1) | Observed once | Direction consistent with general retail knowledge (external prior, not our data). Q4-25 includes partial October |
| Boots peak Nov (12.8 vs 1.9 $M/mo in Q2), leggings Nov, hoodies Dec, coats Dec, sandals Q2 | Observed once | Keyword matching on top-500 product names; one November |
| **"Dresses peak May" → "our P01/P02 sweater dresses fall in a type that peaks in spring"** | **Overstated** | The "dresses" bucket is dominated by spring and summer dresses. Nothing in the data isolates sweater dresses, and sweaters/cardigans peak Sep and Nov–Dec [I] |
| "Heating up now": Women's Shoes 1.5×, Tops 1.4×, Men's tops 1.3× (last 30 days vs average month) | Observed once, includes trend | Sales-weighted heat for **all** 232 subcategories is 1.11, so about a tenth of every "heat" figure is market growth or general season. Relative to the market: Shoes ≈ 1.35×, Tops ≈ 1.26× [V] |
| Seasonality index CSV (1.00 = category's average month) | Observed once | Average excludes October and mixes platform growth with season. Small categories (Pre-Owned $1.1M/mo, swing 3.6) are noisy |
| Q2→Q3 growth Kids' Fashion +51% etc. | Observed once | Back-to-school likely [I]; one year |
| 3-month staying power Health 68% vs Womenswear 42% | Repeated across ~8 start months, one year | More robust than the peaks; still one market year |
| "Kalodata API has no monthly subcategory history" | Superseded | Same day's log: level-2 IDs work with monthly ranges (0.1 credit/subgroup-month) |

Validation path: compare Nov–Dec 2026 against Nov–Dec 2025 as they arrive (first check early December). Optionally
use a provider's claimed 2–4 years of history (untested, PROVIDER_COMPARISON). Label every peak "2025–26 observed"
until then.

### Other Kalodata claims, briefly [V]

- **"Womenswear: 0 of 61 AI videos made $1K vs 15% human"** (AI_VIDEO_BY_CATEGORY): the 61 AI videos come from 4
  products, 29 of them from one product where only 4% of all videos made $1K. Using each product's own hit rate,
  about 4.1 AI hits would be expected, so 0 is still unusual (Poisson p ≈ 0.02). But the gap is mostly product mix,
  not 0% vs 15%.
- Commission, lifespan and boosting analyses in `log.md` already say "observational, not causal". Keep that label.

---

## 7. Meta Ad Library data

### 7.1 What is observed vs derived vs inferred [V: `scripts/meta_ad_library_list.py`, both CSVs, md notes]

| Field | Source | Status |
|---|---|---|
| ad_id, page_id, page_name, headline (link title), created time, delivery start, currency | Meta connector `ads_library_search` | Observed |
| found_by_search | Our query | Observed (sampling frame) |
| days_running, ads_from_page_in_list, copies_same_headline | Computed by script from the above | Derived |
| active_ads_count, rank within store by "total impressions" sort, low-impression flag (< 100), multiple versions, started running, total active time (shown only under 1 day), format, button, domain, price shown | Ad Library website, read by a helper agent in Chrome | Observed by an agent; transcription not checked |
| body_summary, hook_type | Helper agent's classification | Inferred (AI-coded) |
| Impressions, reach, spend, CTR, results, conversions | **Not available** for US commercial ads | Not observed |

### 7.2 Claims the source can't support

- **"Longest-running first"** (CSV description and first-5 note). The list is sorted by days running, but the pool
  is the newest ads. Days running: median 0.1 (about 2.4 hours), 75th percentile 0.2, max 5.3. These are mostly
  untested launches, the opposite of proven ads. [V]
- **"Its top two ... carry no low-impression flag, so those are its current winners"** (Nurestia). A missing flag
  means ≥ 100 impressions. The impressions sort mixes budget and age. All 14 Nurestia versions started the same
  day. "Winner" is not supported. [V/I]
- **"Ad count + run time are the spend signals"** (log 10-27). This is an inference: long-running ads can be
  low-budget evergreen ads, and a store's ad count reflects testing style. Use survival over repeated snapshots
  instead (fix F7). [I]
- No profitability claim was made from the data (good). Keep it that way: nothing in the source measures sales.

### 7.3 Coverage and sampling [V]

- 6 keyword searches. 83 of 100 rows came from "cardigan knit" (43) and "boutique sweater" (40). Rows were
  hand-filtered to clothing/shoe sellers.
- 61 pages, mostly small US boutiques plus some established brands (Coldwater Creek, Buck Mason, Z SUPPLY, SYRN).
  This is not a sample of dropship competitors, and 43 pages appear with only one ad.
- Top-by-impressions file: 175 rows for the same 61 stores. 33 of those "top" ads started on Oct 27 itself, and 14
  carry the low-impression flag.
- Quality nits: 24 of 100 headlines are blank. `price_shown` has both "no" and "no " (11 rows).

The creative ideas drawn from it (occasion headlines, catalog carousel, local weather angle) are reasonable **as
ideas to test**, evidence category D.

---

## 8. TikTok Creative Center Top Ads

- **Sample**: TikTok-curated Top Ads, US, Women's Clothing, last 180 days, observed 2026-10-25. 78 ads (76 unique),
  only 4 dresses. This is a survivorship sample. It compares better- and worse-*ranked* top ads, never winners vs
  failures. The report states this clearly (HIGH_PERFORMING_AD_PATTERNS §1). [V]
- **Platform-provided**: CTR rank ("top X%", 1–51%), likes, budget level (0–2; 63 of 78 at level 2), objective
  (conversion 38, product sales 34, other 6). **Not provided**: spend, impressions, conversions, retention. [V]
- **Measured locally**: duration, cuts per 10 s, transcript (faster-whisper base.en).
- **Coded by reviewers**: hook category, emotional appeal, curiosity gap, proof, interpretation, confidence (45
  high / 32 medium / 1 low). The reviewers are not identified (likely AI agents [I]), and no agreement check is
  recorded.
- **Statistics**: median split (38 vs 38), within-objective 18 vs 18, Fisher/Mann-Whitney. At least 12 patterns
  compared, no correction. The report correctly calls them "a guide to which patterns are worth testing".
- **Cross-source agreement** [V/I]:
  - Spoken narration, product visible early and longer talking ads lean the same way in the Top Ads and the video
    study. That is convergent but confounded support.
  - Cut pace disagrees: Top Ads favour slower cutting (1.7 vs 2.7 per 10 s); in the video study winners cut
    slightly more (1.36 vs 1.29, p = 0.10).
  - Neither source supports a callout-hook rule: no difference in Top Ads (9 vs 8), and `problem_pain` hooks are
    19% vs 19% in the study.

---

## 9. Rights, retention and personal data

| Item | Location | Size | Notes |
|---|---|---|---|
| Study videos (mp4 + frame sheet + transcript + tags) | `research/kalodata/videos/<video_id>/` | 1.2 GB, 205 folders | From public TikTok links via yt-dlp (pilot report: "against TikTok's terms; owner's call") plus 3 via Kalodata [V] |
| Top Ads videos | `research/tiktok/ads/videos/` | 416 MB, 78 mp4 | Creative Center, owner-approved download [V] |
| Top Ads frame sheets and JSON | `research/tiktok/ads/analysis/` | 18 MB, 162 files | [V] |
| Kalodata raw pulls | `research/kalodata/raw/` | 304 MB | [V] |
| Kalodata DB | `research/kalodata/kalodata.db` | 397 MB | Paid data (~$50 of credits) [V] |

- **Retention promises not kept**:
  - VIDEO_EXTRACTION_DESIGN: videos "deleted after extraction and the features kept".
  - VIDEO_PILOT: "delete after the study".
  - CHECKPOINT_B: Top Ads videos "can be deleted once Checkpoint C is done" (Checkpoint C report exists).
  - All files are still present; log 10-26 says "kept for checks". [V]
- **Personal data** [V]:
  - Creator handles on 135,653 `videos` rows, and 68,971 rows in `video_links_core.csv` with profile-derived URLs
    and captions.
  - Transcripts of 185 creators' speech (some contain first names).
  - Frame sheets show faces. `video_elements` holds perceived age group, hair and gender of identifiable creators.
  - **24 raw review files (6,106 records) contain `review_user` and `user_id` of TikTok Shop buyers.**
    `comment_insights.csv` keeps only review IDs.
- **Terms**: Kalodata's terms on storing or reuse are "Not yet checked" (PROVIDER_COMPARISON). [V]
- **Governance gap**: `.gitignore` excludes all of `research/`, and `scripts/backup_hub.py` backs up neither
  `research/` nor `kalodata.db`. The paid dataset and every research report have no version history and no
  backup. [V]
- **Use**: videos are used for analysis only ("never reposted or copied"). No reuse was found [V for the code paths
  read; I overall]. Keeping the derived features (tags, transcripts, numbers) is proportionate for research. Keeping
  full videos and reviewer names is not needed for any current purpose. [I]

---

## 10. How research flows into creative work today

[V unless marked]

1. The study goes into a `log.md` headline, then `reports/ad_review_cycle1_2026-10-26.md`, which scores and **ranks
   the 6 ads on the study's signals** ("Person with the product at 0 s (63% vs 40%)", "Talking speed (3.7 vs 3.1
   words/s): slow").
2. Then `EC-P01-A05-H01-V03` is "rebuilt from the 91-pair video study": wearing at 0 s, close-ups, pace 3.65
   words/s to match winners' 3.68.
3. Then `studio/bible/rules.yaml` gets `script.words_per_second_min: 2.9`, `max: 3.8` and `qa.speech_share_min:
   0.70`, enforced on every episode by `gates.py` and `production.py`. That these bands came from the study is
   [I]: the values bracket the study's 3.11–3.68 and appeared the same day. But words/s was p = 0.066 overall, 27:16
   in same-status pairs (p = 0.13) and **10:10 in apparel pairs**.
4. Cycle-1 advice "15 s is short (winners 34 s)" rests on a paired difference of +2.8 s, which is null in
   same-status pairs (23:20) and in apparel (14:8, p = 0.29).

**What is done well**:
- `learnings.md` has evidence levels (controlled / repeated / tentative / contradicted) and lists *no* "what works"
  yet. Research was not copied into it as rules.
- `scripts/patterns.py` says "confirm with a one-change duplicate before acting".
- `research/tiktok/HYPOTHESIS_REGISTRY_cycle1.md` pre-registers hypotheses with metrics, sample-size arithmetic and
  a Holm correction.
- The owner has already put unsupported rules "in question" (log 10-25).

**Gaps**:
- There is no place where an external research claim lives with its evidence grade, so the claim travels as prose
  and hardens into rules and recipes.
- Three tag vocabularies don't line up, so our posts can't be compared with the study:
  - the study's (`first_frame`, `hook_type` = bold_claim/problem_pain/...);
  - `config/hub.json tags` (callout, demo-first, product-on-body-walk...);
  - `studio.db content_features` (22 automatic features: `hook_type`, `duration_s`, `words`...). These have no
    `first_frame`, `person_at_0s`, text-hook or close-up feature.
- The experiments and knowledge tables designed in `docs/CONTENT_STUDIO_ARCHITECTURE_V2.md` §2.4 (`experiments`,
  `experiment_items`, `findings`, `knowledge`) don't exist in `studio.db`. `metrics` has 0 rows and `content_marks`
  has 3.

### 10.1 How a pattern library and research → hypothesis → experiment loop should plug in (no parallel system)

1. **Pattern library = the planned `knowledge` table.** One row per research claim:
   - `type='observed_result'` (external research) or `ai_interpretation`;
   - `evidence` JSON {source file, query, n pairs, effect, 95% CI, adjusted p, confounds, sample frame, grade A–D};
   - `status='proposed'`.
   Seed it with the ~10 claims in this audit, graded honestly (e.g. paid boosting: A for association; person at
   0 s: C, confounded). `knowledge` never edits the bible, as the architecture doc already says.
2. **Hypothesis = an `experiments` row** whose `variable` is a `content_features` key, with `primary_metric`,
   `min_sample` and `design`, so cycle-1's registry moves from markdown into the table.
3. **One vocabulary.** Extend `content.derive_features` with the study's objective tags: `first_frame`,
   `person_at_0s`, `words_per_s`, `speech_share`, `duration_s`, `on_screen_text`, `detail_closeups`. Reuse
   `video_pilot.structure()` and `video_elements.py --ours`. Then our posts and the external study share the same
   columns.
4. **Results** come from `content_marks` (24 h / 48 h / 7 d) and ads data. A finding then changes a `knowledge`
   row's status. The owner approves, and only then does a rule enter `rules.yaml` through `bible-approve`. That
   gate already exists.
5. `kalodata.db` stays the raw evidence store. The Studio only holds graded claims and our own experiments.

---

## 11. Rules currently resting on unvalidated research

| Rule / practice | Where | Evidence behind it | Suggested status |
|---|---|---|---|
| Talking speed 2.9–3.8 words/s (gate) | `rules.yaml script` | Not significant; null in apparel pairs | Production default (TTS pacing), not evidence-based; owner to decide |
| Speech share ≥ 70% (QA gate) | `rules.yaml qa` | Speech share p = 0.05 raw, q = 0.24; null in same-status pairs | Same |
| Person wearing the product at 0 s | recipes, ad review "Keep" | Confounded with paid boost; supported directionally by Top Ads | Keep as default (cheap, plausible), log as hypothesis |
| Ad ranking by study signals | `reports/ad_review_cycle1_2026-10-26.md` | Treats non-significant signals as predictive | Re-label as judgement |
| "AI presenter passes as real" | same report | Tag misses half of known AI videos | Withdraw; owner judges realism |
| "Sweater dresses peak in spring" | CATEGORY_SEASONALITY "What this means" | Wrong bucket | Correct the text |

---

## 12. What is solid and should be kept

- The **paired same-product, same-month design** and exact sign tests. With paid status and video age added to the
  matching, it is the right study shape. [V]
- The **extraction pipeline** (`video_pilot.structure/frame_sheet/transcribe`, `video_elements.py`,
  `video_audio.py`): cheap (≈ $0.10 tagging for 185 videos), local, reusable on our own creatives. [V]
- **Failure logging** in the run logs, which made section 2.4 possible. [V]
- **Read-only DB access** in `analyze_video_study.py`. **Race not tagged** by design. [V]
- **Paid boosting is strongly associated with winning** (OR ≈ 10). That is useful for the affiliate and boosting
  economics already in the log. [V]
- The **music null result** (14:19, p = 0.49), reported as "no difference", is honest. [V]
- The TikTok research's **evidence grades, stated limits and pre-registered hypothesis registry** with Holm and
  power arithmetic. [V]
- `learnings.md` evidence levels, the `patterns.py` disclaimer, and the owner's "rules without data are in
  question" stance. [V]
- The Meta scan's honest statement that the API "returns ... no ad images, body text, spend or results". [V]

---

## 13. Prioritised fixes

| # | Fix | Evidence | Effort |
|---|---|---|---|
| F1 | Add a correction block to the top of `VIDEO_STUDY_2026-10.md`: adjusted p, paid strata, video-age imbalance, CIs; state that only paid boosting survives and that person-at-0 s is "promising, confounded" | §3, §4, App. A | S |
| F2 | Owner decision: relabel the words/s band and speech-share gate in `rules.yaml` as production defaults (not research), or widen them. Correct the cycle-1 ad review's "AI passes as real" and the sweater-dress seasonality line | §10, §11 | S (owner approval needed; never changed without it) |
| F3 | Retention: delete the 1.6 GB of third-party mp4s (after F4 if wanted). Strip `review_user`/`user_id` from the 24 raw review files. Write a 10-line `research/README` with a retention rule (media ≤ 30 days, derived features kept) | §9 | S |
| F4 | Hand-check 20 pairs (40 videos) for `first_frame`, `product_shown_as_0s`, text hook, close-ups, AI look. Report agreement per tag. Store the actual responding model per row | §5 | S (≈ 1 h human time) |
| F5 | Version and back up research outputs: allow `research/**/*.md` and scripts in git; add `kalodata.db` (online backup) to `backup_hub.py` | §9 | S |
| F6 | Study v2 design before any new creative rule: match on paid status (both organic and both paid strata) and publish week. Outcome = views or $/1K over a fixed window after posting. Womenswear/apparel-heavy. ≥ 150 same-status pairs. Pre-register ≤ 5 primary features with Holm. Keep an attempts table (candidate, rank, outcome, reason, views, sales). Language-aware transcription | §2–4 | M |
| F7 | Meta: fix the "longest-running" wording. Take weekly snapshots of the same stores and measure **ad survival** (still active after 14/30 days) as the only defensible performance proxy. Label `hook_type`/`body_summary` as AI-coded. Normalise `price_shown` | §7 | S–M |
| F8 | Seasonality: label all peaks "2025–26 observed". Report heat relative to the market (÷ 1.11). Split sweater dresses from dresses with level-2 monthly pulls (0.1 credit each; owner approval for spend). Re-check against Nov–Dec 2026 | §6 | S–M |
| F9 | Content Studio: create the `experiments` / `knowledge` / `findings` tables already designed. Seed `knowledge` with graded claims from this audit. Add the study's objective tags to `content_features` so our posts and research share one vocabulary | §10.1 | M |
| F10 | AI-video-by-category: report product-adjusted expectations (e.g. 4.1 expected vs 0 observed) instead of raw 0% vs 15% | §6 | S |

---

## Appendix A: every tested feature in the video study

152 tests replicated from `scripts/analyze_video_study.py` (same functions, read-only) plus the music test.
"Winners"/"comparisons" are medians for measures and shares of videos for signals. Raw p = exact two-sided sign test
on discordant pairs (measures: pairs where the winner is higher vs lower). Holm and BH are across all 152; "BH q
(primary 43)" is within measures + signals + hook/format/opening. **Survives** = Holm < 0.05 across all 152.

| # | section | feature | winners | comparisons | raw p | Holm (all 152) | BH q (all 152) | BH q (primary 43) | survives? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | measures | duration_s | 34.4 | 24.4 | 0.033 | 1.000 | 0.591 | 0.237 | no |
| 2 | measures | speech_share | 0.88 | 0.82 | 0.050 | 1.000 | 0.591 | 0.237 | no |
| 3 | measures | words_per_s | 3.68 | 3.11 | 0.066 | 1.000 | 0.591 | 0.237 | no |
| 4 | measures | cuts_per_10s | 1.36 | 1.29 | 0.101 | 1.000 | 0.662 | 0.290 | no |
| 5 | measures | product_first_seen_s | 0.0 | 0.0 | 0.451 | 1.000 | 1.000 | 0.722 | no |
| 6 | signals | ad=1 | 84% | 41% | <0.001 | <0.001 | <0.001 | <0.001 | yes |
| 7 | signals | person_at_0s | 73% | 53% | 0.011 | 1.000 | 0.431 | 0.122 | no |
| 8 | signals | product_at_0s | 81% | 68% | 0.058 | 1.000 | 0.591 | 0.237 | no |
| 9 | signals | presenter_looks_ai_generated | 2% | 8% | 0.062 | 1.000 | 0.591 | 0.237 | no |
| 10 | signals | has_text_hook | 74% | 60% | 0.065 | 1.000 | 0.591 | 0.237 | no |
| 11 | signals | detail_closeups | 76% | 65% | 0.087 | 1.000 | 0.644 | 0.286 | no |
| 12 | signals | presenter=on_camera_speaking | 57% | 49% | 0.371 | 1.000 | 0.971 | 0.694 | no |
| 13 | signals | ai_video=1 | 7% | 10% | 0.453 | 1.000 | 1.000 | 0.722 | no |
| 14 | signals | has_cta | 58% | 55% | 0.743 | 1.000 | 1.000 | 0.926 | no |
| 15 | signals | presenter=no_person | 7% | 9% | 0.754 | 1.000 | 1.000 | 0.926 | no |
| 16 | signals | spoken_hook | 80% | 82% | 0.832 | 1.000 | 1.000 | 0.994 | no |
| 17 | signals | production=polished | 7% | 8% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| 18 | hook/format/opening | format=other | 2% | 14% | 0.003 | 0.516 | 0.233 | 0.066 | no |
| 19 | hook/format/opening | first_frame=person_with_product | 63% | 40% | 0.005 | 0.690 | 0.233 | 0.066 | no |
| 20 | hook/format/opening | first_frame=product_alone | 11% | 25% | 0.024 | 1.000 | 0.591 | 0.207 | no |
| 21 | hook/format/opening | product_shown_as_0s=flat_or_packshot | 9% | 20% | 0.052 | 1.000 | 0.591 | 0.237 | no |
| 22 | hook/format/opening | format=talking_review | 25% | 15% | 0.093 | 1.000 | 0.644 | 0.286 | no |
| 23 | hook/format/opening | product_shown_as_0s=in_use | 20% | 11% | 0.115 | 1.000 | 0.674 | 0.310 | no |
| 24 | hook/format/opening | product_shown_as_0s=held | 34% | 23% | 0.132 | 1.000 | 0.746 | 0.335 | no |
| 25 | hook/format/opening | product_shown_as_0s=not_shown | 25% | 34% | 0.215 | 1.000 | 0.875 | 0.513 | no |
| 26 | hook/format/opening | format=lifestyle | 9% | 3% | 0.227 | 1.000 | 0.883 | 0.513 | no |
| 27 | hook/format/opening | hook_type=offer_discount | 4% | 9% | 0.289 | 1.000 | 0.917 | 0.565 | no |
| 28 | hook/format/opening | hook_type=humour_skit | 3% | 8% | 0.289 | 1.000 | 0.917 | 0.565 | no |
| 29 | hook/format/opening | format=try_on | 14% | 10% | 0.289 | 1.000 | 0.917 | 0.565 | no |
| 30 | hook/format/opening | first_frame=scene_without_product | 14% | 20% | 0.424 | 1.000 | 1.000 | 0.722 | no |
| 31 | hook/format/opening | format=unboxing | 3% | 7% | 0.453 | 1.000 | 1.000 | 0.722 | no |
| 32 | hook/format/opening | hook_type=demonstration | 7% | 10% | 0.581 | 1.000 | 1.000 | 0.867 | no |
| 33 | hook/format/opening | hook_type=bold_claim | 32% | 27% | 0.585 | 1.000 | 1.000 | 0.867 | no |
| 34 | hook/format/opening | first_frame=face | 10% | 13% | 0.607 | 1.000 | 1.000 | 0.870 | no |
| 35 | hook/format/opening | hook_type=none | 12% | 9% | 0.629 | 1.000 | 1.000 | 0.873 | no |
| 36 | hook/format/opening | hook_type=question | 15% | 12% | 0.678 | 1.000 | 1.000 | 0.896 | no |
| 37 | hook/format/opening | format=skit | 3% | 5% | 0.688 | 1.000 | 1.000 | 0.896 | no |
| 38 | hook/format/opening | hook_type=problem_pain | 19% | 19% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| 39 | hook/format/opening | hook_type=you_need_to_see_this | 5% | 5% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| 40 | hook/format/opening | format=demo | 41% | 42% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| 41 | hook/format/opening | format=styling | 1% | 2% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| 42 | hook/format/opening | first_frame=other | 2% | 2% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| 43 | hook/format/opening | product_shown_as_0s=worn | 12% | 12% | 1.000 | 1.000 | 1.000 | 1.000 | no |
| 44 | apparel | person_at_0s | 91% | 59% | 0.065 | 1.000 | 0.591 |  | no |
| 45 | apparel | cuts_per_10s | 0.3 | 1.15 | 0.167 | 1.000 | 0.819 |  | no |
| 46 | apparel | duration_s | 20.45 | 16.4 | 0.286 | 1.000 | 0.917 |  | no |
| 47 | apparel | speech_share | 0.86 | 0.79 | 0.359 | 1.000 | 0.971 |  | no |
| 48 | apparel | has_text_hook | 64% | 50% | 0.549 | 1.000 | 1.000 |  | no |
| 49 | apparel | detail_closeups | 82% | 73% | 0.625 | 1.000 | 1.000 |  | no |
| 50 | apparel | words_per_s | 3.63 | 2.54 | 1.000 | 1.000 | 1.000 |  | no |
| 51 | apparel | product_first_seen_s | 0.0 | 0.0 | 1.000 | 1.000 | 1.000 |  | no |
| 52 | apparel | product_at_0s | 95% | 91% | 1.000 | 1.000 | 1.000 |  | no |
| 53 | apparel | spoken_hook | 73% | 73% | 1.000 | 1.000 | 1.000 |  | no |
| 54 | apparel | has_cta | 50% | 50% | 1.000 | 1.000 | 1.000 |  | no |
| 55 | non-apparel | words_per_s | 3.68 | 3.16 | 0.036 | 1.000 | 0.591 |  | no |
| 56 | non-apparel | product_at_0s | 77% | 61% | 0.071 | 1.000 | 0.597 |  | no |
| 57 | non-apparel | duration_s | 39.7 | 28.5 | 0.086 | 1.000 | 0.644 |  | no |
| 58 | non-apparel | person_at_0s | 67% | 51% | 0.090 | 1.000 | 0.644 |  | no |
| 59 | non-apparel | has_text_hook | 77% | 64% | 0.108 | 1.000 | 0.662 |  | no |
| 60 | non-apparel | speech_share | 0.88 | 0.83 | 0.109 | 1.000 | 0.662 |  | no |
| 61 | non-apparel | detail_closeups | 74% | 62% | 0.152 | 1.000 | 0.795 |  | no |
| 62 | non-apparel | cuts_per_10s | 1.68 | 1.35 | 0.321 | 1.000 | 0.953 |  | no |
| 63 | non-apparel | product_first_seen_s | 0.0 | 0.0 | 0.418 | 1.000 | 1.000 |  | no |
| 64 | non-apparel | has_cta | 61% | 57% | 0.711 | 1.000 | 1.000 |  | no |
| 65 | non-apparel | spoken_hook | 83% | 86% | 0.804 | 1.000 | 1.000 |  | no |
| 66 | audio | any_background_music | 33% | 38% | 0.487 | 1.000 | 1.000 |  | no |
| 67 | elements | el_hair_length=unclear | 10% | 2% | 0.039 | 1.000 | 0.591 |  | no |
| 68 | elements | el_jewelry__none | 46% | 60% | 0.047 | 1.000 | 0.591 |  | no |
| 69 | elements | el_camera_style=selfie_handheld | 26% | 14% | 0.052 | 1.000 | 0.591 |  | no |
| 70 | elements | el_presenter_presents_as=none | 26% | 36% | 0.150 | 1.000 | 0.795 |  | no |
| 71 | elements | el_presenter_presents_as=man | 20% | 12% | 0.167 | 1.000 | 0.819 |  | no |
| 72 | elements | el_hair_color=none | 28% | 38% | 0.188 | 1.000 | 0.839 |  | no |
| 73 | elements | el_hair_length=none | 28% | 38% | 0.188 | 1.000 | 0.839 |  | no |
| 74 | elements | el_actions__hand_detail | 72% | 62% | 0.188 | 1.000 | 0.839 |  | no |
| 75 | elements | el_jewelry__watch | 20% | 12% | 0.210 | 1.000 | 0.875 |  | no |
| 76 | elements | el_age_group=none | 26% | 34% | 0.215 | 1.000 | 0.875 |  | no |
| 77 | elements | el_actions__turning_twirling | 8% | 3% | 0.219 | 1.000 | 0.875 |  | no |
| 78 | elements | el_camera_movement=lots | 27% | 19% | 0.248 | 1.000 | 0.917 |  | no |
| 79 | elements | el_props__pet | 7% | 3% | 0.250 | 1.000 | 0.917 |  | no |
| 80 | elements | el_props__none | 42% | 33% | 0.256 | 1.000 | 0.917 |  | no |
| 81 | elements | el_room=store | 3% | 8% | 0.289 | 1.000 | 0.917 |  | no |
| 82 | elements | el_camera_movement=slight | 67% | 74% | 0.296 | 1.000 | 0.917 |  | no |
| 83 | elements | el_room=living_room | 19% | 13% | 0.302 | 1.000 | 0.917 |  | no |
| 84 | elements | el_actions__putting_on_product | 12% | 7% | 0.302 | 1.000 | 0.917 |  | no |
| 85 | elements | el_hair_length=shoulder | 14% | 21% | 0.327 | 1.000 | 0.953 |  | no |
| 86 | elements | el_props__packaging_box | 14% | 20% | 0.332 | 1.000 | 0.953 |  | no |
| 87 | elements | el_room=outdoors_street | 7% | 3% | 0.375 | 1.000 | 0.971 |  | no |
| 88 | elements | el_lighting=ring_or_studio_light | 1% | 4% | 0.375 | 1.000 | 0.971 |  | no |
| 89 | elements | el_camera_style=filmed_by_someone_handheld | 43% | 50% | 0.377 | 1.000 | 0.971 |  | no |
| 90 | elements | el_jewelry__rings | 26% | 19% | 0.377 | 1.000 | 0.971 |  | no |
| 91 | elements | el_hair_length=long | 21% | 16% | 0.405 | 1.000 | 1.000 |  | no |
| 92 | elements | el_age_group=unclear | 43% | 37% | 0.405 | 1.000 | 1.000 |  | no |
| 93 | elements | el_worn_with__jeans | 8% | 4% | 0.453 | 1.000 | 1.000 |  | no |
| 94 | elements | el_camera_style=tripod_static | 11% | 16% | 0.454 | 1.000 | 1.000 |  | no |
| 95 | elements | el_lighting=warm_indoor_lamps | 23% | 18% | 0.458 | 1.000 | 1.000 |  | no |
| 96 | elements | el_makeup=unclear | 0% | 2% | 0.500 | 1.000 | 1.000 |  | no |
| 97 | elements | el_hair_color=black | 14% | 19% | 0.503 | 1.000 | 1.000 |  | no |
| 98 | elements | el_hair_length=covered | 10% | 7% | 0.508 | 1.000 | 1.000 |  | no |
| 99 | elements | el_makeup=not_visible | 61% | 56% | 0.511 | 1.000 | 1.000 |  | no |
| 100 | elements | el_actions__talking_to_camera | 33% | 28% | 0.511 | 1.000 | 1.000 |  | no |
| 101 | elements | el_props__mug_or_drink | 6% | 9% | 0.549 | 1.000 | 1.000 |  | no |
| 102 | elements | el_age_group=25_40 | 24% | 20% | 0.557 | 1.000 | 1.000 |  | no |
| 103 | elements | el_color_palette=bright_bold | 12% | 9% | 0.581 | 1.000 | 1.000 |  | no |
| 104 | elements | el_makeup=natural_or_none | 23% | 28% | 0.618 | 1.000 | 1.000 |  | no |
| 105 | elements | el_age_group=over_40 | 2% | 4% | 0.625 | 1.000 | 1.000 |  | no |
| 106 | elements | el_hair_color=not_visible | 4% | 7% | 0.625 | 1.000 | 1.000 |  | no |
| 107 | elements | el_props__furniture_in_use | 7% | 4% | 0.625 | 1.000 | 1.000 |  | no |
| 108 | elements | el_worn_with__none | 78% | 74% | 0.629 | 1.000 | 1.000 |  | no |
| 109 | elements | el_main_shot_distance=close_up | 33% | 37% | 0.701 | 1.000 | 1.000 |  | no |
| 110 | elements | el_jewelry__bracelet | 18% | 14% | 0.701 | 1.000 | 1.000 |  | no |
| 111 | elements | el_lighting=mixed | 23% | 20% | 0.711 | 1.000 | 1.000 |  | no |
| 112 | elements | el_props__product_alternatives | 17% | 20% | 0.711 | 1.000 | 1.000 |  | no |
| 113 | elements | el_hair_color=covered | 9% | 7% | 0.727 | 1.000 | 1.000 |  | no |
| 114 | elements | el_props__food | 6% | 8% | 0.727 | 1.000 | 1.000 |  | no |
| 115 | elements | el_glasses | 9% | 7% | 0.754 | 1.000 | 1.000 |  | no |
| 116 | elements | el_lighting=natural_daylight | 52% | 56% | 0.780 | 1.000 | 1.000 |  | no |
| 117 | elements | el_hair_length=short | 12% | 10% | 0.791 | 1.000 | 1.000 |  | no |
| 118 | elements | el_props__plants | 9% | 11% | 0.815 | 1.000 | 1.000 |  | no |
| 119 | elements | el_main_shot_distance=medium | 22% | 20% | 0.845 | 1.000 | 1.000 |  | no |
| 120 | elements | el_visual_quality=average | 22% | 20% | 0.856 | 1.000 | 1.000 |  | no |
| 121 | elements | el_actions__using_product | 32% | 30% | 0.860 | 1.000 | 1.000 |  | no |
| 122 | elements | el_presenter_presents_as=woman | 46% | 43% | 0.871 | 1.000 | 1.000 |  | no |
| 123 | elements | el_room=other | 26% | 26% | 1.000 | 1.000 | 1.000 |  | no |
| 124 | elements | el_room=kitchen | 16% | 17% | 1.000 | 1.000 | 1.000 |  | no |
| 125 | elements | el_room=bedroom | 16% | 16% | 1.000 | 1.000 | 1.000 |  | no |
| 126 | elements | el_lighting=unclear | 0% | 1% | 1.000 | 1.000 | 1.000 |  | no |
| 127 | elements | el_lighting=night_or_dim | 0% | 1% | 1.000 | 1.000 | 1.000 |  | no |
| 128 | elements | el_presenter_presents_as=unclear | 8% | 8% | 1.000 | 1.000 | 1.000 |  | no |
| 129 | elements | el_presenter_presents_as=mixed_group | 1% | 1% | 1.000 | 1.000 | 1.000 |  | no |
| 130 | elements | el_age_group=under_25 | 4% | 4% | 1.000 | 1.000 | 1.000 |  | no |
| 131 | elements | el_hair_color=brown | 19% | 18% | 1.000 | 1.000 | 1.000 |  | no |
| 132 | elements | el_hair_color=blonde | 12% | 11% | 1.000 | 1.000 | 1.000 |  | no |
| 133 | elements | el_makeup=moderate | 16% | 14% | 1.000 | 1.000 | 1.000 |  | no |
| 134 | elements | el_color_palette=mixed | 42% | 42% | 1.000 | 1.000 | 1.000 |  | no |
| 135 | elements | el_color_palette=neutral_earth | 37% | 38% | 1.000 | 1.000 | 1.000 |  | no |
| 136 | elements | el_color_palette=black_white | 6% | 7% | 1.000 | 1.000 | 1.000 |  | no |
| 137 | elements | el_color_palette=pastel | 3% | 4% | 1.000 | 1.000 | 1.000 |  | no |
| 138 | elements | el_camera_style=mixed | 18% | 19% | 1.000 | 1.000 | 1.000 |  | no |
| 139 | elements | el_camera_style=mirror_selfie | 2% | 1% | 1.000 | 1.000 | 1.000 |  | no |
| 140 | elements | el_main_shot_distance=mixed | 37% | 37% | 1.000 | 1.000 | 1.000 |  | no |
| 141 | elements | el_main_shot_distance=full_length | 8% | 7% | 1.000 | 1.000 | 1.000 |  | no |
| 142 | elements | el_camera_movement=static | 7% | 7% | 1.000 | 1.000 | 1.000 |  | no |
| 143 | elements | el_visual_quality=sharp_well_lit | 78% | 79% | 1.000 | 1.000 | 1.000 |  | no |
| 144 | elements | el_visual_quality=dark_or_blurry | 0% | 1% | 1.000 | 1.000 | 1.000 |  | no |
| 145 | elements | el_actions__posing | 20% | 20% | 1.000 | 1.000 | 1.000 |  | no |
| 146 | elements | el_actions__walking | 10% | 11% | 1.000 | 1.000 | 1.000 |  | no |
| 147 | elements | el_jewelry__necklace | 13% | 13% | 1.000 | 1.000 | 1.000 |  | no |
| 148 | elements | el_jewelry__stud_earrings | 6% | 7% | 1.000 | 1.000 | 1.000 |  | no |
| 149 | elements | el_worn_with__sandals | 6% | 6% | 1.000 | 1.000 | 1.000 |  | no |
| 150 | elements | el_worn_with__sneakers | 4% | 6% | 1.000 | 1.000 | 1.000 |  | no |
| 151 | elements | el_nails_done | 28% | 29% | 1.000 | 1.000 | 1.000 |  | no |
| 152 | elements | el_background_people | 7% | 7% | 1.000 | 1.000 | 1.000 |  | no |

## Appendix B: how the numbers were produced

All with `sqlite3.connect('file:research/kalodata/kalodata.db?mode=ro', uri=True)`, run from the Hub folder.

- Pairs and tags: `analyze_video_study.load()` (imported, read-only). The paired tables come from its
  `binary_table` / `numeric_table`. Holm and BH via `statsmodels.stats.multitest.multipletests`.
- Video metadata:
  `SELECT v.video_id, v.publish_date, v.ad_view_ratio, v.ad_revenue_ratio, v.raw_json FROM videos v JOIN pulls u ON
  v.pull_id = u.pull_id WHERE u.name LIKE 'core_allvideos_%'`. Age = 2026-09-30 minus `publish_date`;
  `creator_debut` from `raw_json`.
- Strata: per pair, the winner's and comparison's `ad` flags. Sign tests per stratum.
  `statsmodels ConditionalLogit(y=winner, X=[ad, person_with_product, log duration, text hook, close-ups],
  groups=pair)`.
- CIs: 5,000 bootstrap resamples of pairs (seed 7).
- Selection: `pick_pairs` logic re-implemented without downloads (top 3 winners ≥ 5K views; 4 comparisons with
  500 ≤ views ≤ 10% of the winner, nearest median log-views). Failed IDs parsed from `video_study.log`,
  `video_study_2.log` and `video_pilot.log` by regex on "link download failed", "no picture in the file" and
  "video file refused".
- Tag checks: crosstab of `video_features.ai_video` vs the `presenter_looks_ai_generated` tag; contradiction counts
  across `tags_json` and `video_elements.elements_json`.
- Market heat: `subcategories_2026-10-26.csv`, Σ `sales_30d_M` × 12 / Σ `sales_12m_M` = 1.11.
- Meta and TikTok: pandas profiles of the CSVs named in §7–8.
