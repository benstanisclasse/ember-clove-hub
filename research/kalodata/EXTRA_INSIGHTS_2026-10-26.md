# Extra insights from the core data (2026-10-26)

> **Correction (2026-10-28, Market Engine Phase A audits).**
>
> - October 2025 covers about one week, so any Oct-based growth or "Nov vs earlier" comparison is overstated
>   (docs/MARKET_DATA_QUALITY_REPORT.md).
> - Seasonality here is one observed year, not a validated recurring pattern (docs/MARKET_CREATIVE_COMPETITIVE_AUDIT.md).
> - Commission figures are today's values applied to past months.


From the 12-month core download (top 500 products per category per month). No new credits.

## 1. The holidays are the biggest months, and we're two weeks away
Total top-500 sales: **Nov 2025 $1,083M, Dec $1,003M**, then Jan $741M, Feb $715M; Mar–Sep $810–920M.
November vs the Jan–Sep average, by category:

| Biggest lift | Nov | Dec | | Fashion | Nov | Dec |
|---|---|---|---|---|---|---|
| Toys & Hobbies | 3.0× | 3.1× | | Kids' Fashion | 1.5× | 1.7× |
| Phones & Electronics | 1.7× | 1.6× | | Shoes | 1.3× | 1.1× |
| Kitchenware | 1.7× | 1.6× | | Menswear | 1.2× | 1.2× |
| Computers & Office | 1.6× | 1.8× | | Womenswear | 1.2× | 1.1× |
| Automotive | 1.6× | 1.6× | | Jewelry | 1.1× | 1.3× |
| Home Supplies | 1.6× | 1.4× | | Fashion Accessories | 1.1× | 1.1× |

Last holiday's breakouts were **giftable, often branded and higher-priced**: Harman Kardon speaker ($100,
$3.5M in Nov), Beats headphones ($142), Ninja air oven ($380) and knife set ($300), Shark FlexStyle ($380–400),
a $55 skincare gift set, Wavytalk curler ($24), e.l.f. lip oil ($10). Holiday shoppers pay more for gifts.

## 2. Fashion churns fastest: you need a steady pipeline of products
Share of top-500 products still in the top 500 three months later:
Health 68% · Food 57% · Baby 56% · Pet 55% · Beauty 54% … Womenswear 42% · Shoes 37% · Menswear 34% ·
Kids' Fashion 32% · Toys 34% · Collectibles 24%.
In fashion, most winners fade within a quarter, so plan on replacing products, not riding one for a year.

## 3. Where sales come from (videos vs lives vs shop page)
Videos dominate most categories: Books 90%, Menswear 88%, Baby 87%, Womenswear 85%, Beauty 85%.
**Lives** matter in Collectibles (66%), Pre-Owned (34%), Jewelry (27%), Home Improvement (26%), Muslim Fashion (26%).
For a video-only strategy (affiliate or our own ads), avoid live-driven categories.

## 4. Data warning: October 2025 looks incomplete
October 2025's median top-500 product sold $8K against $37K in November: likely partial Kalodata coverage for
the first month, not a real 4.6× jump. October→November changes in the model's training data are therefore
inflated. The model was tested on Apr–Sep, so its reported accuracy holds, but the next retrain should drop
October 2025 (or treat it as partial).
