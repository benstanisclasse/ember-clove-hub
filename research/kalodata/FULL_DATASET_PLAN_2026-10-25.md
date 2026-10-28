# Full Kalodata dataset: what to pull, what it costs (2026-10-25)

Goal (owner): one complete dataset to train on and answer many different questions without going back. Money is not
the constraint. US, all 29 top-level categories, spread evenly.

## What the probes showed (0.2 credits; failed calls are free)
- **History starts around October 2025.** Monthly product rankings for Apr 2025 and Oct 2024 return "not found";
  Oct 2025 works. So the full history is about **12 months** (Oct 2025 – Sep 2026, plus Oct 2026 once it ends).
  The first run will find the exact first month.
- **Rankings go deeper than 500.** Page 11 (products 1,001–1,100 in Womenswear, Sep 2026) works and reaches about
  $44–48K a month, half the old top-500 floor.
- **Product details for a past month return that month's figures.** The Athena maxi in Jun 2026: $89K sales, 357
  videos, 205 creators (now: $255K, 1,055, 476). The review count is today's total, not June's. So creator and video
  counts per month can be rebuilt for any product: the breadth signals the pilot model was missing.

## The dataset (12 months back, every category)
| # | What | Per month | Credits for 12 months |
|---|---|---|---|
| A | Category rankings, levels 1–2 | ≈ 1 | 12 |
| B | Top 1,000 products per category by sales | 29 | 348 |
| C | Top 500 fastest-growing products per category | 14.5 | 174 |
| D | Top 300 new launches (last 90 days) per category | 8.7 | 104 |
| E | Top 1,000 videos per category by sales | 29 | 348 |
| F | Top 500 AI videos per category | 14.5 | 174 |
| G | Top 500 creators per category | 14.5 | 174 |
| H | Top 300 shops per category | 8.7 | 104 |
| I | **Monthly product panel:** creators, videos and lives for 2,000 products tracked every month | 200 | 2,400 |
| J | Every video for 500 products (hit rates by category and price) | – | 250 |
| K | Buyer-comment insights for 300 products (sizing, quality, return risk) | – | 300 |
| L | Video details for 1,000 winning videos | – | 100 |
| M | Weekly snapshots for the last 13 weeks (top 500 products per category) | – | 189 |
| | **Backfill total** | | **≈ 4,700 credits ≈ $470** |

**Keeping it current:** about 380 credits (about $38) a month: B–H, the product panel, and weekly scans.

## Pack choice (Kalodata prices 2026-10-25)
| Pack | Price | Covers |
|---|---|---|
| 3,000 | $284.70 | Not enough for the backfill |
| 3,000 × 2 | $569.40 | Backfill plus about 3 months of updates and ad-hoc questions |
| **10,000** | **$949 (5% off)** | **Backfill plus about a year of monthly updates** |
| 30,000 | $2,547 (15% off) | More than this plan can use |

Check before buying 10,000: whether Kalodata credits expire.

## Questions this answers
Which products keep selling 1, 2 and 3 months out, in every category. What price, channel and breadth (creators,
videos) predict that. Which categories are seasonal. How many videos a product needs before it sells, by category.
AI vs human video hit rates by category. Which creators and shops win repeatedly. Return risk from buyer comments.
How fast products rise and fade week to week.

## What no Kalodata pack gives
Anything before about Oct 2025; our own conversion rates and actual ad spend (Kalodata ROAS is an estimate); audience
demographics; exact sales (all Kalodata sales figures are estimates).

## Running it
About 47,000 calls. At the API's rate limit that's about 13–14 hours, run in the background over one or two nights,
resumable, capped at the approved credits. Raw files about 5–10 GB; this machine has 92 GB free.
