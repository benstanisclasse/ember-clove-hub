# Products that look like the loafer, by the numbers (2026-10-30)

Owner: "given what you has seen for these products can you find me a product that looks similar metric wise to this
doesnt have to be the same prodoct also show me what you are measuring".

Read only. No Kalodata credits were used. CJ was used for free searches, details and freight only.

## What is measured (the loafer's numbers are the yardstick)

| # | Measure | Source | Loafer | Pass mark |
|---|---|---|---|---|
| 1 | TikTok demand: September revenue | Kalodata panel | $204k | ≥ $75k |
| 2 | Momentum: August → September change | Kalodata | +85% | ≥ +20%, or new with ≥ $150k |
| 3 | Staying power: months in a category top 500, Jul–Sep | Kalodata | 2 of 3 | more is better (the backtest's best predictor) |
| 4 | Price buyers pay on TikTok | Kalodata revenue ÷ units | $65.63 | $35–90 |
| 5 | Room in the market: the seller's share of the category | Kalodata | 4.5% | lower is better |
| 6 | Brand dependence (lesson from the loafer) | product title and seller | Clarks, via QVC | small or no-name brand only |
| 7 | CJ supply: does CJ's photo match the TikTok photo? | TikTok main image vs CJ images | match | match |
| 8 | CJ saturation: how many CJ stores list the item | CJ listedNum | 5 | low (median of the 50 saved items is 43) |
| 9 | Money kept per order before ads, at the TikTok price | price − CJ cost − freight − 2.9% − $0.30 − 5% refunds | $42.23 | ≥ $20 |
| 10 | Ad budget per sale while keeping 20% of price (target CAC) | #9 − 20% of price | $29.10 | higher is better |
| 11 | Model rank score (M4) | backtested ranking, not a probability | 0.93 | higher is better |

**Not measured.** Two things hurt the loafer, but checking them costs Kalodata credits:
- October sales (the loafer fell about 70% after September).
- Creator concentration (two creators made about two-thirds of the loafer's sales).

The October check costs 0.1 credit per product.

## How the search ran
1. **Screen.** September products in our categories, priced $35–90, with ≥ $75k revenue and growing. Excluded:
   intimates, claims-heavy items, men's, kids and wigs, plus about 60 famous brands (Clarks, Crocs, UGG, SKIMS, Dr.
   Scholl's, Gap, Yeezy and others).
   - **57 products passed.**
2. **Shortlist.** 20 of them, leaning to shoes, bags and outerwear (loafer-like prices). Left out: jeans (sizing),
   wool coats (material claims) and items already rejected in the October report.
3. **CJ search.** Generic keywords, never brand names (`cj_candidates.json`).
4. **Photo check.** Each TikTok main image next to CJ's images (sheets in `data/opportunity_2026-10/lookalike_photos/`,
   not in git). Pairs: `data/media_generated/share_2026-10-30/loafer_lookalikes.jpg`.
5. **Score.** Everything goes into `scorecard.csv`.

## Results

| Product (TikTok) | Sep revenue | Change | Top-500 months | Price | Photo | CJ stores | CJ cost + freight | Kept per order | Target CAC |
|---|---|---|---|---|---|---|---|---|---|
| **Reference: chunky loafer** | $204k | +85% | 2/3 | $65.63 | match | 5 | $6.60 + $11.32 | $42.23 | $29.10 |
| **Buckle suede clog** (Cushionaire Hobby) | $187k | +369% | 3/3 | $57.02 | **match** | 12 | $8.00 + $11.32 | **$32.89** | $21.49 |
| Long hooded puffer vest (Imily Bela) | $161k | new | 1/3 | $37.91 | match | 2 | $9.54 + $9.80 | $15.27 | $7.69 |
| Split-toe "tabi" flat (Cushionaire Maki) | $90k | +263% | 3/3 | $51.18 | match | 3 | $11.35 + $16.63 | $18.86 | $8.62 |
| Bowling bag (NEWBELLA Gia) | $84k | +540% | 2/3 | $89.07 | partial: no quilting | 14 | $6.72 + $10.26 | $64.75 | $46.94 |
| Slouchy fold-over knee boots | $89k | +234% | 2/3 | $45.25 | partial | 27 | $10.20 + $11.32 | $19.85 | $10.80 |
| Black knee-high block-heel boots | $100k | +87% | 3/3 | $45.55 | partial: CJ wine-red patent | 31 | $10.00 + $11.32 | $20.33 | $11.22 |
| Collared zip jacket | $205k | +118% | 2/3 | $36.96 | partial: CJ is corduroy | 1 | $7.47 + $9.65 | $16.62 | $9.23 |

**Ruled out:**
- **CJ had no matching item (11):** leopard and suede loafer mules, two faux-leather jackets, the off-shoulder dress,
  slingback mules, the studded hobo, the knit and satin set, the square-toe platform boots, the fur-lined clog slipper,
  and the pink lounge set.
- **Lose money at the TikTok price (2):** embroidered cowboy boots (CJ $18.85 + $19.07 freight) and knee-high platform
  boots ($31.54 freight).

## Answer: the closest loafer-like product is the buckle suede clog
It matches the loafer on every measured point, and beats it on three.

**Demand**
- Nearly the same September revenue: $187k vs $204k.
- Much faster growth: +369% vs +85%.
- In a top 500 all three months (the loafer managed 2), so it is not a one-month spike.
- Model score 0.96 vs 0.93.

**Supply and cost**
- CJ has the same design: a suede closed-toe clog with a buckle strap.
- Only 12 CJ stores list it.
- It costs $8.00 + $11.32 freight.

**Margin.** It keeps $32.89 per order at TikTok's $57 price. To break even, about 1 click in 30 has to buy at $1 per
click.

**Not brand-led.** The seller is Cushionaire, a small brand. Its clog is itself a lookalike of a famous clog, so the
demand is for the design, not the name.

**What to check before going further**
- **Range:** CJ offers brown only, EU 36–40 (about US 5.5–8.5). That is a narrower size range than the loafer.
- **Material:** the TikTok one says genuine leather or suede with a cork footbed. CJ doesn't state the material or a
  cork footbed.
- **Freight:** CJ lists 500 g, which is light for clogs. If the real weight is higher, freight goes up.
- **Look:** it looks like the Birkenstock Boston clog. Cushionaire sells the same lookalike openly, but decide if
  that's acceptable.
- **October sales** are unknown: 0.1 Kalodata credit to check.

**Runner-up: the bowling bag**, for margin rather than match. At $89 it keeps $64.75 per order, but CJ's bag isn't
quilted. Worth a second CJ search for a quilted version.

## October check: the clog (Kalodata, 2026-10-30, 0.1 credit)
File: `research/kalodata/clog_cushionaire_detail_2026-10-30.json`.

**Still growing:**
- Last 30 days: $212.9k from 3,608 pairs at an average $59.00 (list price $69.99).
- That is up about 14% on September's $187.3k. The loafer fell about 70% over the same window.

**Sold mostly through video.** $207.3k came from videos, $5.4k from live and $0.2k from the shop page.

**A broad creator base.** 349 videos by 225 creators, against the loafer's 274 by 150. Creator concentration was not
pulled; it would take the video ranking at 0.1 credit.

**Established and well reviewed.** Listed since December 2024, 1,049 reviews, 10% commission.
