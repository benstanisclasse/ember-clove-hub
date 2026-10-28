# Why the breakout model picks what it picks (2026-10-25)

Model: chance that a rising product outside its category's top 500 enters the top 500 within 3 months
(`scripts/score_breakouts.py`; explanations `scripts/explain_breakouts.py` →
`model_v1_2026-10-25/breakout_explanations_2026-09.json`). It sees only sales patterns from Kalodata: not how the
product looks, its quality, reviews or trends outside TikTok.

## What drives it overall (importance on months it never saw)
1. **How much it already sells** (by far the biggest)
2. Share of sales from videos
3. Growth vs last month (moderate beats explosive)
4. Price vs the category median
5. Number of variants (sizes, colours)
6. Months already on our riser lists; units; the seller's strength (products already in the top 500, category share)
7. Commission, age, shop-page and live share: minor

## How the chance moves with each signal (average across risers)
| Signal | Low → high |
|---|---|
| Monthly sales | $30: 1.9% · $480: 3.7% · $2.2K: 6.5% · $8.6K: **12.2%** |
| Share of sales from videos | 0%: 3.4% · 25%: 6.2% · 79–100%: **7.0%** |
| Growth vs last month | +100%: **11.4%** · +760%: 7.9% · +1,800%: 5.9% · +11,700%: 4.5% |
| Price vs category median | 0.1×: 4.0% · 0.5×: 5.5% · 1×: 7.0% · 2.2×: **8.9%** |
| Variants | 1: 4.4% · 6: 5.9% · 65: **8.4%** |
| Product age | 1–3 months: about 6.7% · 1 year: 5.3% · 2 years: 4.2% |
| Commission | 0%: 5.0% · 5–11%: **6.2%** · 17%: 5.3% |

In plain words: the model looks for products that **already sell real volume** (thousands a month, not hundreds),
**sell through videos**, are **growing steadily rather than exploding from nothing**, are **priced at or above the
category norm**, come in **many sizes or colours**, and have **kept showing up** month after month.

## Each recommended product (effect = how much that signal adds to its chance vs a typical riser)
A typical riser sells about $480 a month, gets 0% from videos and 77% from the shop page, and grew about 1,800%.

| Product | Chance | Main reasons |
|---|---|---|
| Pacsun Zoe low-rise girlfriend jeans | 75% | $47K sales (+0.37); 100% video sales and none from the shop page (+0.23); already on our lists |
| Vans La Costa slide | 75% | $19K sales (+0.36); 97% video sales (+0.20); Vans already holds 3% of Shoes (+0.12) |
| Faux-fur short booties | 75% | $9K sales (+0.30); on our lists 4 months running (+0.26); steady growth, +391% (+0.11) |
| MAELREG graffiti fleece hoodie | 69% | $12.8K sales (+0.42); 97% video sales (+0.29); 120 variants (+0.10) |
| SHOWITTY fleece-lined leggings | 65% | $30K sales (+0.53); on our lists 2 months (+0.18); 90% video sales (+0.14) |
| Potaroma pet puzzle feeder | 65% | $7.3K sales (+0.35); on our lists 6 months (+0.30); 93% video sales (+0.29) |
| PAVOI letter pendant necklace | 64% | Seller strength: PAVOI has 121 products in the Jewelry top 500 and 28% of the category (+0.33); steady growth (+0.54); 66 variants (+0.23); held back by tiny sales, $351 (−0.12). Treat with caution |
| Cushionaire cloud clogs | 61% | $16K sales (+0.32); 90% video sales (+0.27); held back by age, 22 months (−0.17) |
| BEDLORE mattress protector | 61% | On our lists 4 months (+0.36); 43% video sales (+0.29); $7.1K sales (+0.26) |
| HSIA longline strapless bra | 35% | $35K sales (+0.15) but explosive growth, +7,229% (−0.21). **Correction:** earlier quoted 61% from the first model; the retrained model gives 35% |

## Why these were on the shortlist
The model ranks; the shortlist adds business filters: breakout chance ≥ 50%, commission ≥ 10% (0% pays an
affiliate nothing), price $15–60. Brands (Vans, Pacsun, PAVOI) suit affiliate videos only; for our own store we'd
look for unbranded versions of the same trend (winter booties, fleece leggings, clogs).

## Limits
- Correlation in Kalodata estimates, one year of history. The model can't judge fashion appeal or quality.
- Deep-list products (positions 201–1,000) are outside its training range.
- October data (early November) will show how many actually broke in.
