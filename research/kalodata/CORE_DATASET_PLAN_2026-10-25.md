# Core Kalodata dataset: enough to predict winners and answer most questions (2026-10-25)

Owner's brief: not the full dataset. Enough to (1) predict what a winning product looks like and (2) answer a wide
range of questions, then download more only when a question needs it. US, all 29 top-level categories,
Oct 2025 – Sep 2026 (the 12 months Kalodata has).

## Core download
| # | What | Why | Credits |
|---|---|---|---|
| 1 | Top 500 products per category, every month, sorted by sales | The backbone. Each product's month is a row; whether it is still selling 1–3 months later is the label | 174 |
| 2 | Top 200 fastest-growing products per category, every month | Risers below the top 500, closer to where a new store's products sit | 70 |
| 3 | Product details (creators, videos, lives for that month) for a 1,000-row sample: winners, losers and risers across categories and months | Tests whether breadth (how many creators and videos) improves prediction. If it does, buy more | 100 |
| 4 | Top 300 videos per category, every month | Which formats, AI vs human and ads vs organic sell, by category and season | 104 |
| 5 | Every video for 100 products across categories | Video hit rates by category and price, not just for dresses | 50 |
| 6 | Category rankings, levels 1–2, every month | Category size, growth and seasonality | 12 |
| | **Total** | | **≈ 510 credits ≈ $51** |

Training size: about 14,000 products a month across 12 months, so roughly 150,000 product-months, with 11
one-month and 9 three-month steps to test on. Enough to train and test fairly; the pilot used 500.

**Keeping it current** (items 1, 2, 4 and 6 each month): about 30 credits, about $3 a month.

## Questions the core answers without new downloads
What a winning product looks like by category, price band and channel mix. Which categories and products are
seasonal. How fast products rise and fade. New launches vs established products. AI vs human and ad vs organic video
performance by category. How many videos a product needs before it sells. Which sellers win repeatedly.

## Download on demand (when a question needs it)
| Question needs | Pull | Cost |
|---|---|---|
| Breadth for a specific product or month | Product detail | 0.1 each |
| Buyer complaints and return risk for a product | Comment insight | 1 each |
| Every video for a product | Video list by product | about 0.5 each |
| Products deeper than the top 500 in a category | Rank page | 0.1 per 100 |
| Creators or shops in a category | Creator or shop ranking | 0.1 per 100 |
| Weekly movement | Weekly ranking | 0.1 per 100 |

## Pack
Buy the **1,000-credit pack ($99.90)**: core ≈ 510, leaving ≈ 490 for on-demand questions and about a year of
monthly updates. Two 300 packs ($59.94) cover the core only. Check first whether credits expire.

## Before the big run
Ask Kalodata in writing whether storing the data and training our own models on it is allowed.
