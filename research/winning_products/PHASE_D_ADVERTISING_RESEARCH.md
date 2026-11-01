# Phase D: TikTok video and advertising research (2026-11-01)

**Evidence label: descriptive / exploratory.**
- Every video list is ranked by revenue, so we only see successful videos: correlations are range-restricted and the
  shares are not population rates.
- Kalodata's ad fields (ROAS, ad share) are **estimates**.
- **Kalodata's ROAS and CPA are TikTok Shop figures, not our Shopify CAC.** Nothing here measures what our ads would cost.

Plan (frozen first): `registry/PHASE_D_PLAN.md` (EXP-D-000). Results: EXP-D-001, `_work/phase_d_results.json`. Script:
`scripts/phase_d.py`. Data: 100,666 top-300 video-months (28 categories × 12 months), 188 product video sets
(2026-09), and the random product-detail sample (536 usable rows). No credits spent.

The creative-feature sample (185 videos, 91 pairs) was **already tested** in the 2026-10 video study. It is not re-tested
here, to avoid repeated testing; that study's results stand. Of 152 tests, only "the winning video was a paid ad" survived
correction.

## 1. Ad fields: what they are and how far to trust them (D1)

- **Ads dominate the top lists:** 76-83% of top-300 videos are ads in every full month, 85% at the median category
  (p10-p90: 62-91%). They carry **89% of top-video revenue**.
- **ROAS** exists only for ad videos: 0 organic videos carry one, and 0 ads lack one. Median 2.56 (p10-p90: 1.85-3.35).
  Category medians run 1.72-3.06, a narrow band that is plausibly model-smoothed.
- **The ad share of revenue is capped at 80%.** 41% of ad videos sit exactly at the cap, so "how much of this video's
  revenue came from ads" can't be separated above 80%.
- **The AI flag** is 0 before 2026-06 (unknown), then 4.0% → 5.8% of top videos.

## 2. Engagement is a weak proxy for sales; views are moderate (D2, H-C1)

Spearman ρ with video revenue, within each of 336 category-months:

| Metric | Median ρ | IQR | Verdict (registered) |
|---|---|---|---|
| Views | **0.46** | 0.39-0.51 | moderate |
| Shares | 0.25 | 0.19-0.32 | weak |
| Comments | 0.22 | 0.18-0.29 | weak |
| Likes | 0.22 | 0.16-0.28 | weak |
| Engagement rate (likes+comments+shares per view) | **−0.08** | −0.13 to −0.03 | weak (slightly negative) |
| Revenue per 1k views vs engagement rate | −0.04 | −0.14 to +0.06 | none |

- **Likes, comments and engagement don't tell you which videos sell.** Highly "engaging" videos convert no better per view.
- Caveat: likes are lifetime counts and views are monthly, so the ratio mixes windows.
- Revenue per 1,000 views varies 12× (p10 $6.49, median $21.28, p90 $81.79).

## 3. Ads buy reach, not conversion (D3, H-C4)

Within the same category-month **and** the same views decile (1,475 cells with ≥ 5 ad and ≥ 5 organic videos):
- Ad videos earn **the same revenue per 1,000 views** as organic videos. The median ratio is 1.00, and ads are higher in
  only 51% of cells.
- Pooled medians: ads $20.85, organic $23.30 per 1k views.
- **H-C4 is not supported.**

Read together with the 2026-10 study ("winners are paid", 84% vs 41%): **paid video wins by buying views, not by selling
better per view.** For us this means:
- the creative has to convert on its own;
- a TikTok Shop video's ROAS says little about whether paid traffic to *our* store would convert.

## 4. Creators: broad, new, and rotating (D4)

Per category-month, top-300 videos (p10 / median / p90):

| Measure | p10 | Median | p90 |
|---|---|---|---|
| Distinct creators | 180 | 230 | 253 |
| Revenue share of the top 10 creators | 16% | 21% | 36% |
| Revenue share from creators who debuted ≤ 90 days earlier | 5% | 13% | 25% |
| Share of this month's top creators also in next month's top 300 | 34% | 42% | 53% |

- Category-level video sales are **not** owned by a few creators.
- More than half of each month's top creators drop out of the next month's list.
- New creators take about an eighth of revenue.

## 5. Products backed by more creators keep selling (D5, H-C2: supported)

Random detail sample, top-500 products, m ≤ 2026-08. Logit on next-month retention, controlling for rank, revenue vs
cutoff and category. Odds ratios per 1 SD of log(1 + count):

| Count at month m | Registered model | Sensitivity (+ months held, new entrant, growth, Kalodata momentum) |
|---|---|---|
| **Creators** promoting the product | **OR 1.78 [1.21, 2.62]**, p = 0.004 | **1.64 [1.07, 2.50]**, p = 0.02 |
| **Videos** promoting the product | **OR 1.96 [1.33, 2.88]**, p < 0.001 | **1.80 [1.18, 2.74]**, p = 0.006 |
| Livestreams | 1.23 [0.91, 1.66], p = 0.18 | — |

Base retention 70%, n = 536. The sensitivity check was added after the registered result and doesn't replace it.

**Read:** at the same rank and history, products sold by many creators and videos are more likely to hold. Demand spread
across many sellers is sturdier than demand carried by a few. This matches Phase B (video-driven demand lasts, spikes
fade).
- **Practical:** `creator_number` and `video_number` come from `product/detail` (0.1 credit), so they can be checked for
  any shortlisted product.
- **Caveats:**
  - correlation, not cause (popular products attract creators);
  - n = 536;
  - exploratory months.

## 6. How dependent is a product on one video or creator? (D6, H-C3)

188 products ranked in the September 2026 top 500 (their top-100 videos):

| Measure | p10 | Median | p90 |
|---|---|---|---|
| Creators | 19 | 50 | 70 |
| Top single video's share of video revenue | 11% | 23% | 49% |
| Top creator's share | 16% | **33%** | 70% |
| Top-3 creators' share | 37% | **65%** | 92% |
| Ad share of video revenue | 62% | 87% | 99% |

For the typical product, three creators bring two-thirds of its video revenue, and for 1 in 10, one creator brings
70%. Whether concentration predicts decline **can't be tested yet**, because these sets exist only for September. The
metrics are frozen as a forward test:
- File: `registry/forward_test_video_conc_2026-09.csv`, SHA-256 `7cb79a18…5fb7`.
- Registered test: Spearman(top-creator share, still in the Oct-2026 top 500) < 0, for products ranked 101-500.

## 7. What a proper creative study would need (D7, H-C5)

The 2026-10 study (91 pairs) was too small for creative effects to survive correction. A confirmatory paired design
needs, at α = 0.005 per test (10 pre-chosen features) and power 0.8:

| Discordant pairs (where winner and comparison differ on the feature) | Effect: 2:1 | Effect: 3:1 |
|---|---|---|
| 20% of pairs | 596 pairs | 264 |
| 30% | 397 | 175 |
| 50% | 237 | 104 |

**About 250-400 pairs**, i.e. 500-800 videos. Two caveats:
- Kalodata's video URL costs 0.5 credit and fails for low-view videos (those come from public links).
- The pairs must be **matched on paid status and video age**, the two confounders the last study missed.

At about 400 credits for the videos alone, this is an owner decision, and **not worth it before the cheaper commercial
phases (F, G)**.

## 8. AI-generated videos (summary of the 2026-10-26 study, not re-tested)

- AI videos are 4.7% of top-300 videos (June-September).
- Once in a top list, they sell about the same as human videos, with higher revenue per view.
- They're weak in Womenswear and Shoes, and better in Books, Menswear, Tools and Health.
- Four months of an estimated flag only.

## 9. What this means for product selection and our ads

1. **Judge a product's video demand by views and by how many creators and videos sell it, not by likes or engagement.**
2. **Prefer products sold by many creators** (`creator_number` and `video_number` from product/detail). It's the
   strongest video-level retention signal we found.
3. **Paid reach is how TikTok Shop videos win, and ads don't convert better.** Our own creative must earn its conversion.
   Kalodata ROAS (~2.5) is not a CAC benchmark for Shopify.
4. **Treat a product whose top creator brings over half its video revenue as fragile** (to be confirmed by the forward test).
5. **Creative research:** existing evidence supports only "paid boosting". Anything else is unproven until a 250-400-pair matched study.

## 10. Checkpoint

- **Saved:** report, plan, EXP-D-000/001, script, results, and the D6 forward file.
- **Unresolved:**
  - concentration → decline (forward test);
  - whether Kalodata ROAS estimates mean anything for independent-store ads (needs our own ad data, Level 3).
- **Phase E (competition and consumer behaviour) is ready.** It uses the shop and creator monthly ranks, shop
  concentration in the top 500, the 83,156 raw reviews and the 196 attribute sets.
