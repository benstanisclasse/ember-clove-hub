# One year of Kalodata data: what's worth downloading and what it costs (2026-10-25)

Pricing (Kalodata Open Center, 2026-10-25): 1 credit ≈ $0.10. Rank lists cost 0.1 credit per 100 rows; a product
or video detail costs 0.1; buyer-comment insight costs 1; video download URL costs 0.5; balance is free.
History check: monthly pulls for **Oct 2025** returned data for products and videos, so 12 months back is available.
All pulls load automatically into `research/kalodata/kalodata.db` (script: `scripts/kalodata_db.py`).

## Worth downloading (monthly snapshots, Nov 2025 – Oct 2026)
*Revised 2026-10-25 at the owner's request: spread evenly across all 29 top-level categories, no extra weight on
women's apparel.*

| # | What | Filters | Why | Credits / year | ≈ $ |
|---|---|---|---|---|---|
| A | Category rankings, levels 1–2 | none | Category size, growth, seasonality, how concentrated each is | ≈ 5 | $0.50 |
| B | Top 500 products in each of the 29 categories | sort by sales | Who wins, at what price, with what channel mix | 174 | $17.40 |
| C | Top 100 fastest-growing products per category | sort by growth, sales > $1K | Catches risers before they top the charts (B alone only sees current leaders) | ≈ 35 | $3.50 |
| D | Top 500 videos in each of the 29 categories | sort by sales | Which ads and formats sell, by category | 174 | $17.40 |
| E | Product details for about 2,000 products, spread across categories (winners + a comparison sample) | – | Creator count, video count, reviews, category path, daily sales trend: the "breadth" signals | 200 | $20 |
| F | Every video for about 200 winning products, spread across categories | product filter | How concentrated sales are, hit rates, AI vs human by product | ≈ 100 | $10 |
| G | Buyer-comment insights for shortlisted products | – | Return risk: sizing, "not like photos", quality | ≈ 20 | $2 |

**Full package (A–G): ≈ 710 credits ≈ $71.** Ongoing ≈ 60 credits ≈ $6 per month.
**Lean package** (A; B at top 300; C; D at top 100; E at 1,000): ≈ 280 credits ≈ $28. Ongoing ≈ 23 credits ≈ $2.30
per month.

## Fields that matter (all come back in the calls above)
- **Products:** sales, units, unit price, growth rate, launch date, commission rate, video vs live vs shop-page
  sales, seller, SKU count.
- **Product details:** creators, videos, lives, review count, min/max price, cross-border or local delivery,
  category path, daily sales trend.
- **Videos:** sales, views, estimated ad ROAS, ad or organic, AI flag, publish date, creator, likes, shares, comments,
  ad share of sales and views.
- **Categories:** sales, units, growth, top-3 shop share, average sales per shop.

Useful filters to vary: `date_range` (month), `category_ids`, `sort_field` (sales or growth), `unit_price_range`
(price bands that fit our margin), `delivery_type` (local vs cross-border, like EPROLO), `launch_date` (new products),
`is_ai_video`, `ads_roas`.

## Not worth it for now
- **Livestream, shop and creator rankings:** we don't sell through lives or recruit creators yet. Add creator
  rankings if we go the affiliate or TikTok Shop route.
- **Bulk video download URLs** (0.5 each): only for the few winning videos we want to break down shot by shot.
- **Product images:** not needed for the model.

## Still to verify (cheaply) before a big pull
- That rank lists page deeper than 5 pages (500 rows); we've only gone 5 deep so far.
- That product details for a *past* month return that month's creator and video counts, not today's.
- Run time: about 7,000 calls at the API's rate limit ≈ 2–3 hours, which is fine to run in the background.
