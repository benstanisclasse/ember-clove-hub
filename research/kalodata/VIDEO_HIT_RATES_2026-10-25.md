# How many videos does it take to get one that sells? (Kalodata, US, last 30 days, 2026-10-25)

Method: for 5 dresses, Kalodata's product detail gives the total number of videos promoting the product in the last
30 days. The video ranking filtered to that product lists them by sales, down into the zero-sales videos, so every
selling video is counted. Raw: `research/kalodata/raw/2026-10-25/videos_<product>_p*.json`.
Cost: 2.6 credits (2.0 left). The capped run missed a sixth product (Cider tulle mini) and Athena's last page;
both runs were already past their selling videos, so no hits were missed.

## Per product
| Product | Price | Videos | Any sales | ≥ $1K sales | Videos making 50% of sales | Top 10 share | AI share of revenue |
|---|---|---|---|---|---|---|---|
| CurvySweet Athena knitted maxi | $58 | 1,055 | 281 (27%) | 46 (4.4%) | 11 | 50% | 3% |
| Cider knit high-neck maxi | $49.56 | 1,023 | 192 (19%) | 16 (1.6%) | 8 | 58% | 0% |
| Cable-knit bodycon (P01 look-alike) | $20.40 | 732 | 135 (18%) | 4 (0.5%) | 5 | 70% | 44% |
| Fitted turtleneck knit mini | $31.99 | 402 | 111 (28%) | 5 (1.2%) | 4 | 72% | 38% |
| Oversized ribbed turtleneck mini (P02 look-alike) | $34.16 | 187 | 27 (14%) | 3 (1.6%) | 2 | 90% | 94% |

## All 5 together (3,399 videos, $390K of video sales)
| A video that made… | Count | Odds |
|---|---|---|
| any sale | 746 | 1 in 5 |
| ≥ $100 | 271 | 1 in 13 |
| ≥ $1,000 | 74 | **1 in 46** |
| ≥ $5,000 | 17 | **1 in 200** |

AI-flagged videos only (588 listed): ≥ $1K = 7 (**1 in 84**), ≥ $5K = 1 (1 in 588). This is a slight overestimate,
because AI videos in the unlisted zero-sales tail aren't counted.

**Correction (2026-10-25, later):** counting the unlisted zero-sales videos as AI in the same share as the listed
zero-sales ones (45%) gives about 1,353 AI videos. The odds become: any sale 1 in 9, ≥ $100 1 in 31,
**≥ $1K 1 in 193**, ≥ $5K 1 in 1,353. Use these for planning; "1 in 84" was too optimistic. Videos needed for one
≥ $1K AI hit: 134 (50% chance), 310 (80%), 577 (95%).

## Videos needed for a decent chance of one hit
Chance of at least one hit after n videos = 1 − (1 − p)^n.

| Hit = | Odds per video | 50% chance | 80% chance | 95% chance |
|---|---|---|---|---|
| ≥ $1K sales, any creator | 1 in 46 | 32 videos | 73 | 137 |
| ≥ $1K sales, AI videos | 1 in 84 | 58 | 135 | 250 |
| ≥ $5K sales, any creator | 1 in 200 | 139 | 321 | 598 |

At $4.85 per Higgsfield video (15 s Seedance): 135 AI videos ≈ $655, and 321 videos ≈ $1,557.

## What a hit is worth
| Model | $1K-sales video | $5K-sales video |
|---|---|---|
| Affiliate, 9% median commission | $90 | $450 |
| Own product in a TikTok Shop, no affiliate fee (P01: ≈ $20 profit per $52.99 sale) | ≈ $380 | ≈ $1,890 |

## Caveats
- **These are successful products, chosen because they sell.** For an average product the odds are worse.
- **The videos come from creators with existing followers.** A new account starts with less reach, so expect lower
  odds at first.
- **Hits aren't random.** The winners share patterns (fit and flattery shown on the body, real sizes, seasonal hooks).
  Copying proven formats from Kalodata should beat these base rates. We'll only know by measuring our own.
- Kalodata's revenue figures are estimates.

## How long videos keep selling (added 2026-10-25)
From the same pulls: 1,178 videos with sales in the last 30 days ($668K), grouped by age at 2026-10-25.

| Video age | Share of selling videos | Share of sales | Median sales per video |
|---|---|---|---|
| 0–7 days | 18% | 4% | $56 |
| 8–30 days | 64% | 39% | $58 |
| 31–60 days | 12% | 38% | $271 |
| 61–90 days | 2% | 9% | $1,624 |
| 91–180 days | 2% | 8% | $1,704 |
| 181–365 days | 2% | 2% | $600 |

- **Most videos sell for about 2–4 weeks and stop.** 82% of the videos selling anything are a month old or less.
- **Winners keep going for 2–3 months, and some for 6+.** Half of all sales came from videos older than 30 days. A
  quarter of the $1K+ videos were over 60 days old (median age 33 days).
- Videos boosted as paid ads last longer: 60% of their sales came from videos over 30 days old, against 47% for
  organic videos.
- AI and non-AI videos have a similar life (sales-weighted median age 31 vs 34 days).
- **For the affiliate model:** keep "months each video keeps selling" at 1. The 30-day averages already include sales
  from older videos that are still selling, so setting it higher counts that tail twice.
- Limits: one snapshot, not the same videos tracked over time, and older videos only show up if they're still
  selling. Kalodata's per-video growth field reads below −100%, so its meaning is unclear and it isn't used here.
  The monthly video pulls in the 6-month plan let us track the same videos month to month.
