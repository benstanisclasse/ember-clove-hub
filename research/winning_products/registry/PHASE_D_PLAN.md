# Phase D analysis plan: video and advertising (frozen 2026-11-01, before any Phase D computation)

**Label:** descriptive and exploratory. Every video list is ranked by revenue, so it shows successful videos only: range
is restricted and the results are not population rates. The creative-feature data (185 videos) was already tested by the
2026-10 video study. **It is not re-tested here**, to avoid repeated testing; its results are summarised.

## Data

- **Top-300 videos:** per L1 category × month, 2025-10..2026-09, 100,820 rows, no product id. Views are the month's views.
  Likes, shares and comments are probably **lifetime** counts (MARKET_DATA_QUALITY_REPORT), so "per view" ratios mix
  windows and are labelled as such.
- **Product → video sets:** 2026-09 (core: 99 products up to 5 pages; Tier 2: 93 products × top 100). For comparability,
  every product's set is cut to its **top 100 videos by revenue**.
- **Random product-detail sample:** about 1,000 product-months with month-specific `creator_number`, `video_number` and `live_number`.

## Analyses

| Id | Question | Method | Decision rule |
|---|---|---|---|
| D1 | How complete and reliable are the ad fields? | Completeness by month and category: ad share, `ads_roas` distribution, ROAS when ad=0, `ad_revenue_ratio` and `ad_view_ratio` ranges. Consistency check: is revenue-from-ads (ratio × revenue) ≤ revenue | descriptive |
| D2 (H-C1) | Are views, likes, shares and comments weak proxies for video revenue? | Spearman ρ within each category-month, summarised by median and IQR across the 336 cells, for views, likes, shares, comments and engagement (likes+comments+shares)/views. Also ρ(revenue per 1k views, engagement per view) | "weak proxy" if the median ρ < 0.3; "strong" if > 0.6 |
| D3 (H-C4) | Do ad videos earn more per view than organic ones? | Within category-month × views-decile cells: median RPM (revenue per 1k views) for ad vs organic; pooled ratio of medians, and the share of cells where ad > organic | ad RPM higher in ≥ 2/3 of cells with both types (≥ 5 each) |
| D4 | How concentrated is video revenue among creators, and how new are the creators? | Per category-month: distinct creators in the top 300; top-10-creator revenue share; share of revenue from creators who debuted ≤ 90 days before the month (`creator_debut`); creator persistence (share of a month's top-300 creators also present the next month) | descriptive |
| D5 (H-C2) | Do products backed by more creators/videos at m retain better at m+1? | Detail sample rows in the top 500 at m (ranks 1-500, m ≤ 2026-08). Logit T1 ~ log(1+creators) + rank_pct + log_rev_cut + category FE. Second model: log(1+videos). Odds ratio per SD with 95% CI | supported if the CI excludes 1 (registered criterion), positive direction |
| D6 (H-C3) | How dependent are products on one video or creator? | For the ~190 Sep-2026 products: top-video share, top-creator share and top-3-creator share of the product's top-100 video revenue; creators; ad share of video revenue. **Forward test:** registered now. Spearman(top-creator share, retained in the Oct-2026 top 500) < 0 among products ranked 101-500 in Sep. Evaluated on the sealed October pull | descriptive now; forward later |
| D7 (H-C5) | What sample would a confirmatory creative study need? | Power for a paired (McNemar) design at α = 0.05/10 (10 pre-chosen creative features), power 0.8, using the discordance rates seen in the 2026-10 study | report n |

AI videos: summarised from `AI_VIDEO_BY_CATEGORY_2026-10-26.md`, not re-tested.

## Output

`PHASE_D_ADVERTISING_RESEARCH.md`; `_work/phase_d_results.json`; D6 metrics frozen in `registry/forward_test_video_conc_2026-09.csv`.
