# Stage D: Competitive landscape for the "demand-signal" tool

Prepared 2026-11-01 for an independent viability assessment. Public web pages only. Nothing was signed up for, trialled, submitted or downloaded. Some pricing pages render prices only with JavaScript; those were read in a browser pane without logging in, and the only clicks were on the Monthly/Annual toggles. Every claim carries a source number from the list at the end. All sources were accessed 2026-11-01.

**Proposed product:** (1) flag TikTok Shop products showing early demand, using sales-estimate data such as Kalodata's; (2) match each to a CJ Dropshipping supplier; (3) show per-product margin and break-even ad cost after supplier price and shipping.

**Labels used below**
- **V** = vendor-documented: the vendor's own page, help centre, app-store listing or press release.
- **T** = third-party: a review site, directory or competitor blog. Many "reviews" in this space are written by competing vendors, and those are flagged.
- **NV** = not verified.

---

## 1. Summary

1. **The proposed bundle already exists in parts, and two dropshipping suites come close to the whole thing.**
   - **Sell The Trend** has the most of it:
     - a TikTok Shop Explorer, launched June 2026, that claims to find products "before they go viral";
     - a built-in CJdropshipping integration and CJ trend explorer;
     - an AI Supplier Finder;
     - a "Profit Margin" figure on each product card. [17][18][19][20][21]
   - **AutoDS** sells a Product Finding Hub add-on for $14.97/mo. It includes:
     - a TikTok Analytics tab of US TikTok Shop best-sellers with GMV;
     - "Import & Start Sourcing" into AutoDS's own China sourcing;
     - an estimated profit per sale on its "Trending Products" list. [23][24][25]
   - **Dropship.io** pairs three things:
     - a TikTok Shop Product Library "with real sales and revenue data";
     - "access to AliExpress and Alibaba suppliers";
     - a per-product "breakdown on the numbers". [26][27]
   - **What none of them document** is the specific chain: a TikTok Shop product matched automatically to a CJ SKU, then CJ landed cost to the buyer's country, then a stated break-even CPA or ROAS. None of them publish how the margin figure is calculated.
2. **"Early" or "before viral" claims are everywhere, and evidence is nowhere.** At least 11 vendors make such claims. I found no backtest, hit rate, precision/recall, or independent audit from any of them, and no third-party validation study of "winning product" tools either [44].
   - **Kalodata** explicitly warns not to use its data where high precision is required [1].
   - **A third-party review** (by a competitor) cites user reports of Kalodata figures not matching real shop data [5].
3. **Price bands** (more detail in section 5c):
   - TikTok Shop intelligence: about $10–$180/mo for self-serve tiers, with API and enterprise tiers custom or $450–$900/mo.
   - Dropshipping product research: about $20–$100/mo for core tiers, up to $200–$300/mo for top tiers.
   - Supplier platforms (CJ): free to use; revenue comes from product and shipping margin.
4. **Free and near-free substitutes cap willingness to pay.**
   - EchoTik's self-serve tiers are listed at $9.9–$22.7/mo [7].
   - FindNiche says its new product is "now free" [36].
   - CJ's own app is free and recommends trending products daily [28].
5. **The most defensible gap is evidence and transparency, not features.** Nobody publishes how their "early" flags perform after the fact, or how their margin numbers are built. Incumbents could ship the feature bundle; Sell The Trend and AutoDS are one integration step away.

---

## 2. Comparison table

Key: Y = yes, P = partial, N = not found. V / T / NV as above. Prices are list prices in USD seen 2026-11-01 unless noted.

| Tool | TikTok Shop sales data | Early / "winning" claim | Supplier link | Margin / profit calc | History depth | Alerts / monitoring | Methodology disclosed | List price (monthly / annual-equiv.) |
|---|---|---|---|---|---|---|---|---|
| Kalodata | Y (V) [2] | Weak; homepage says "trending product analysis" (V) [1] | N found [1][2] | N found (V); review suggests adding it (T) [5] | "1000 Days" (V) [1] | Favourites / tracking (T) [6] | Partial: public collection plus AI models; warns of variations (V) [1] | Web pricing behind sign-up. App Store in-app: Starter $49.99, Professional $99.99 / $179.99, US Standard $119.99 (V) [3]. Third-party: $38–$159 (T, conflicting) [4][5][6] |
| FastMoss | Y (V) [8] | "one step ahead" (V) [9] | N found [8][9] | N found | 28 / 90 / 180 days by tier (V) [8] | Video and LIVE monitor credits (V) [8] | No; data-source FAQ answer not shown (V) [9] | Basic $49, Pro $89, Ultimate $139 (monthly; first month discounted). Annual $47 / $72 / $91 per month (V) [8] |
| EchoTik | Y (V) [10] | "explore potential hot products" (V) [10] | N found | Generic "Calculator" listed (V) [7] | 30 / 90 days / "all historical" (V) [7]; API to 1,000 days [10] | Product monitor 20 / 200 / 1,000 (V) [7] | No | Basic $9.9, Pro $14.9, Enterprise $22.7 per user per month (V) [7] |
| Shoplus | Y (V) [12] | "Find & track winning products" (V) [12] | N found | N found | Not stated | Influencer monitoring (V) [12] | No | Basic $39, Premium $49, Professional $79 per month (V) [11]. Annual: Premium $588/yr, Professional $948/yr (T) [13] |
| Tabcut | Y (V) [14] | "Three-Day Potential List", "Yesterday's Emerging List" (V) [14] | N found | N found | Monthly rankings, past year on premium (V) [14] | Influencer monitor (V) [14] | Partial: claims >90% coverage, daily refresh (V) [14] | Pricing behind login (V). Third-party: from $39–$48 up to $172/mo (T, competitor-written) [15][16] |
| PiPiADS | P: TikTok Shop rankings within an ad-spy tool (V) [22] | Ad spy, "winning" in testimonials only | N found | N found | NV | Ad Tracker 2 / 10 / 100 (V) [22] | No | Monthly: Basic $49, Advanced $99, Flexible $180, Enterprise $900. Annual (Q4 promo): $294 / $594 / $1,080 / $5,400 per year (V) [22] |
| ShopShark (AutoDS) | Y, US only (V) [33][23] | "identify trends early" (V) [33] | N on its own | Cost and commission in $ (V) [33] | NV | NV | Partial: labels which numbers are estimates (V) [33] | Explorer $26.90, Pro $39.90, Premium $66.90 per month; annual $19.90 / $29.90 / $49.90 per month (V) [33] |
| Chuhaijiang (出海匠) | Y (V) [34] | "before they peak" (V) [34] | P: "sourcing due-diligence report"; 1688 not named (V) [34] | Y: "profit & break-even read", break-even ROAS (V) [34] | 90 / 180 / 365 days (V) [35] | NV | No | CNY: Standard ¥199/mo; Pro ¥3,599/yr; Enterprise ¥5,599/yr (page inconsistent) (V) [35] |
| **Sell The Trend** | Y: TikTok Shop Explorer, Pro and Pro+ only (V) [17][18] | "Before They Go Viral" (V) [18] | **Y: CJ and AliExpress integrated, AI Supplier Finder (V)** [17][20][21] | **P: "Profit Margin" on cards, formula undisclosed (V)** [18] | NV | Monitor Products & Stores 100 / 250 / 500 (V) [17] | No (V) [18] | Essential $49.97, Pro $99.97, Pro+ $299.97 per month; annual $32.97 / $66.64 / $199.97 per month (V) [17] |
| **AutoDS** (Product Finding Hub) | Y: US TikTok Shop, GMV (V) [24] | "Spot trends before they go viral" (V) [23] | **P: TikTok imports use TikTok as supplier; sourcing request to AutoDS China warehouse (V)** [24] | **P: estimated profit on Trending and Hand-Picked lists, not on TikTok Analytics (V)** [24] | NV | Price and stock monitoring (V) [25] | No | Import $26.90, Starter $39.90, Advanced $66.90 per month; annual $19.90 / $29.90 / $49.90 per month; Product Finding Hub add-on +$14.97/mo (V) [25] |
| **Dropship.io** | Y: TikTok Shop Product Library (V) [26][27] | "Spot breakouts early" (V) [26] | P: AliExpress / Alibaba on Portfolio picks (V) [26] | P: "Numbers breakdown" on Portfolio; free BEROAS calculator (V) [26] | "real-time and historical" (V) [27] | Sales Tracker 25 / 50 / 100 products (V) [26] | No | Basic $39, Standard $59, Premium $99 per month; annual $26 / $34 / $49 per month (V) [26] |
| Minea | P: navigation link only; TikTok Shop data reportedly on Premium (T) [30][31] | "Spot trending ads before anyone else" (V) [30] | P: "find the exact AliExpress supplier" (V) [32] | N found | NV | Notifications (V) [29] | No (V) [32] | Starter $49, Premium $99, Business $199 per month; quarterly $39 / $79 / $158 per month (V) [29] |
| Winning Hunter | Y: TikTok Shop on all plans (V) [37] | "spot breakout winners before they go mainstream" (V) [37] | N found | Separate free calculator (V) [37] | NV | Brand tracking 2 / 30 / 300 (V) [37] | No | Billed yearly: Basic $30, Standard $49, Enterprise $150 per month (V) [37] |
| TrendTrack | N: ads and stores, not TikTok Shop GMV (V) [38] | "see market shifts before they happen" (V) [38] | N found | Free calculators only (V) [38] | NV | Brandtracker (V) [38] | No | Billed yearly: Starter $34, Pro $62, Business $111 per month (V) [38] |
| Zendrop | N | "Top Winning Products" (V) [39] | Y: own fulfilment, US and China 3PL (V) [39] | Y: profit margin calculator (V) [39] | NV | NV | No | Free; Pro $49/mo ($399/yr); Plus $79/mo ($549/yr) (V) [39] |
| Ecomhunt | N | Testimonial claims only (V) [40] | P: AliExpress info (V) [40] | N found | 2-year winning-products database (V) [40] | Alerts 5 / 10 / 50, SMS and email (V) [40] | No | Basic $23, Pro $39, Suite $49 per month; $279 / $468 / $588 per year (savings maths inconsistent) (V) [40] |
| Koala Inspector | N: Shopify stores (V) [41] | No "winning" claim (V) [41] | **Y: "Find Suppliers" with landed cost (V)** [41] | **Y: profit and margin at your price; excludes ad spend (V)** [41] | NV | Shop tracking 50 (V) [41] | Partial: names the cost components (V) [41] | Free; Premium $22/mo (V) [41] |
| FindNiche | Y (V) [36] | "early growth signals" (V, vendor blog) [42] | AliExpress product and store data (V) [36] | Rough "estimate margins" (V) [42] | NV | N found | No | "now free" (V) [36] |
| CJ Dropshipping | N | "Source and Sell Winning Products" (V) [43] | Is the supplier; 1688 / Taobao / AliExpress import (V) [28] | Shipping-cost calculator; no profit calculator found (V) [28][43] | n/a | n/a | No | Free app; fees are product and shipping (V) [28] |

---

## 3. Per-tool notes

### A. TikTok Shop intelligence tools

**Kalodata** (Kalowave Technology Co., Limited)
- **Discovery and data (V) [1][2]**
  - Category, shop, creator, product, video and ad, and livestream explorers.
  - The public product-list view shows these filters and columns: Revenue, Revenue Growth Rate, Item Sold, Launch Date, Shipping Fee, Commission Rate, Creator Count and Creator Conversion Rate.
  - Homepage claims "1000 Days Historical Data" and "200M+ Product Data".
- **Methodology (V) [1]**
  - Data comes from "public channels", refined with "advanced AI models".
  - It warns that "transaction amounts and ad spending, might have small variations".
  - It says not to use the data where "high precision" is needed.
  - This is the most candid disclaimer in the set.
- **Supplier and margin:** none found on Kalodata pages [1][2]. A review by Winning Hunter (a competitor) recommends Kalodata *add* margin estimation and clearer revenue methodology. It also scores database accuracy 5/10, citing a Reddit user whose own shop data did not match (T) [5].
- **Pricing**
  - The web pricing page redirects to sign-up (V) [1].
  - US App Store in-app purchases (V) [3]: Starter (Monthly) $49.99; Professional (Monthly) $99.99 and $179.99 (two listings); US Standard $119.99; United States Basic $59.99; Global Standard $61.99; credit packs.
  - Third-party figures conflict and are NV: $38.3 / $83.2 [5]; $79 / $159 / $299 [4], from a group-buy reseller and unreliable; $33.1 / $55.4 [42], from a competitor blog.
- **"Early" claim:** none on its own pages. A competitor rates its early detection "Limited (trend-following)" (T, biased) [42].
- **Target customer:** TikTok Shop sellers, brands, creators and affiliates (V) [1]. Not dropshippers specifically.
- **Not verified:** current web prices; alerts; any supplier feature behind login.

**FastMoss** (Beijing-based; US office in Culver City)
- **Discovery (V) [8][9]**
  - Product research, Market Pulse category trends, ads, LIVE and video monitors, creator outreach.
  - AI review analysis and script tools.
  - Claims 620M+ products and 4.7M+ users.
- **History (V) [8]:** detail pages cover the last 28 days, the last 90 days, or up to 180 days with flexible dates, depending on tier. Video and LIVE monitor credits are 10 / 200 / 600 per month.
- **Claims (V) [9]:** "Spot top-selling items and rising trends on TikTok Shop one step ahead". Also says it has "the largest, most accurate TikTok Shop data", with no methodology shown.
- **Supplier and margin:** none found [8][9].
- **Pricing (V) [8]**
  - Monthly list: Basic $49, Pro $89, Ultimate $139. The page renders this oddly as "$31 / $55 / $98 for the 1st month, then $588 / $1,068 / $1,668"; those are 12× the monthly price, so the label is probably wrong.
  - Annual: $47 / $72 / $91 per month, billed $558 / $854 / $1,084.
  - Enterprise API: contact sales.
  - A third-party breakdown dated Sept 2026 matches (T) [45].
- **Not verified:** a dedicated "new / rising products" ranking.

**EchoTik**
- **Discovery (V) [10]:** product, shop, creator and live leaderboards; "Category GMV trend"; Data API that tracks "up to 1,000 days back".
- **Tiers (V) [7]**
  - History: 30 days / 90 days / "all historical data".
  - Product monitor quotas: 20 / 200 / 1,000.
  - A "Calculator" is listed under Tools without description. A TikTok Shop pricing-calculator page returned HTTP 410.
- **Claims (V) [10]:** "explore potential hot products". Some homepage figures are marked as display-only data.
- **Supplier:** none found.
- **Pricing (V) [7]:** Free $0; Basic $9.9; Pro $14.9 ("Original price $348"); Enterprise $22.7 per user per month as shown, with a monthly/quarterly/annual toggle. **These are unusually low; treat them as possibly promotional.**
- **Methodology:** none.

**Shoplus**
- **Features (V) [12]:** "hourly-updated data of product sales on TikTok"; "Find & track winning products"; "find products with high commission". No supplier or profit features.
- **Pricing**
  - Monthly (V) [11]: Basic $39 (Top100 lists, 100 detail views per day); Premium $49 (Top300, 2 sub-accounts); Professional $79 (unlimited, 5 sub-accounts).
  - Yearly prices did not render on the vendor page. Third-party: Premium $588/yr, Professional $948/yr (T) [13].
- **Methodology:** none.

**Tabcut**
- **Discovery (V) [14]**
  - Daily, weekly and monthly product rankings.
  - Early-stage lists: "Yesterday's Emerging List", "Three-Day Potential List", "Seven-Day Bestsellers List".
- **Methodology (V) [14]**
  - Claims it mirrors ">90% of TikTok Shop's market data", refreshed every 24 hours.
  - Disclaimer: "unofficial", with "All data is collected from public sources".
- **Supplier and margin:** none found.
- **Pricing**
  - `/user/pricing` redirects to the login workbench (V).
  - Third-party, competitor-written and NV: "From $39/mo" [16]; "48$/mois" to "172$/mois" [15].

**PiPiADS** ("PiPiSpy" was not found as a current separate product; searches resolve to PiPiADS) [22][46]
- **What it is:** primarily a TikTok and Facebook ad-spy tool.
- **Credit system (V) [22]:** the 2.0 membership is credit-based: 1 credit per list item, 20 per detail view. Rankings include "Top Products / New Products / Top Stores", plus "TikTok Shop" and "TikTok Made Me Buy It" sections.
- **Supplier and margin:** none.
- **Pricing (V) [22]**
  - Monthly: Basic $49 (crossed-out $69); Advanced $99 ($159); Flexible $180; Enterprise $900 ($1,999).
  - Annual (Q4 50%-off promo to Dec 31): Basic $294/yr; Advanced $594/yr; Flexible $1,080/yr; Enterprise $5,400/yr.
  - Extra credits are sold as one-off packs.
- **Third-party note:** Trustpilot is reportedly around 2.1/5, mostly over billing complaints (T, NV) [46].

**ShopShark** (AutoDS's TikTok research tool [23])
- **What it covers:** US-focused TikTok Shop analytics. Daily product and video updates, "45+" data points, cost and commission in dollars (V) [33].
- **Methodology:** it marks which data points are estimates, and notes that matching a sales spike to videos shows overlap, not cause (V) [33]. This is relatively transparent.
- **Claim:** "identify trends early" (V) [33].
- **Supplier and margin:** none.
- **Pricing (V) [33]:** Explorer $26.90, Pro $39.90, Premium $66.90 per month; annual $19.90 / $29.90 / $49.90 per month; 3-day trial.

**Chuhaijiang / 出海匠** (Chinese cross-border tool)
- **Features (V) [34]**
  - TikTok Shop, Google demand and Shopify data.
  - A "Sourcing due-diligence report" that takes a product link or image and returns demand, competition, margins and a sourcing verdict.
  - A "Profit & break-even read" with break-even ROAS.
  - **This is the closest feature-level match to the "margin + break-even" part of the proposal**, but no CJ link was found and 1688 is not named on the page.
- **Claim:** "Find winning TikTok Shop products before they peak" (V) [34].
- **Pricing (V) [35]**
  - Standard ¥199/mo; Pro ¥3,599/yr; Enterprise ¥5,599/yr (the page also shows ¥7,199, so it is inconsistent).
  - History by tier: 90 / 180 / 365 days.
  - The pricing page does not say which tier includes the sourcing report.

### B. Dropshipping product-research tools

**Sell The Trend: the closest overall match**
- **TikTok Shop Explorer (V) [18][19]**
  - Press release dated 2026-06-16 [19].
  - The page claims "Real-time TikTok Shop sales tracking", "Predictive product discovery" and "Saturation risk detection".
  - Product cards show "Profit Margin" and "POT Revenue". Neither is defined; the cards are dated "Updated November 1, 2026".
- **FAQ on how it works (V) [18]:** the FAQ explains detection only in general terms: it tracks "engagement growth, and product momentum". It gives no thresholds, data source, or accuracy figures.
- **Plans (V) [17]**
  - TikTok Shop products and TikTok viral-ads finders are on Pro and Pro+ only.
  - "AliExpress and CJDropshipping Trend Explorers" are on all plans.
  - Product imports: 500 / 1,000 / 5,000.
- **CJ integration (V, vendor blog updated 2026-03-26) [20]:** CJ is "fully integrated", the CJ Explorer "updates every 24 hours", and orders are fulfilled with one click.
- **AI Supplier Finder (V, help article 2025-04-24) [21]:** for products with no supplier in the system, it generates a list of suppliers selling a similar product.
- **Not verified**
  - Whether a TikTok Shop Explorer product is matched *automatically* to a CJ SKU.
  - What the "Profit Margin" includes: shipping? fees? ad cost?
  - Whether any break-even ad-cost output exists.
- **Pricing (V) [17]:** Essential $49.97, Pro $99.97, Pro+ $299.97 per month; yearly $32.97 / $66.64 / $199.97 per month; 14-day trial.

**AutoDS**
- **Plans (V) [25]:** priced by product count: Import $26.90, Starter $39.90, Advanced $66.90 per month; annual (25% off) $19.90 / $29.90 / $49.90 per month; Enterprise custom.
- **Product Finding Hub add-on, $14.97/mo (V) [24][25]**
  - **TikTok Analytics:** "top-selling TikTok Shop products in the United States" with sales, GMV and commission; updated daily; US only. No profit figure is shown.
    - Imports use **TikTok as the supplier**, so orders are fulfilled manually.
    - "Import & Start Sourcing" sends a sourcing request to AutoDS's China warehouse. It costs 1 credit and needs the Order Processor add-on.
  - **Trending Products:** shows an "estimated profit per sale" based on supplier cost and selling price.
  - **Hand-Picked Products:** suppliers are AliExpress, Amazon, the AutoDS warehouse and private suppliers; shows "Potential profit".
- **Claims:** "Explore verified winning products" (V) [25]; "Spot trends before they go viral" in the ads-spy menu (V) [23].
- **Assessment:** demand signal and supplier are joined through a manual sourcing request, not automatic matching. Margin is shown for curated lists, not for TikTok Analytics rows.

**Dropship.io**
- **Product Library (V) [26][27]:** "Explore millions of TikTok Shop products with real sales and revenue data", with daily sales and trend charts. Sales Tracker covers 25 / 50 / 100 products.
- **Portfolio (V) [26]**
  - 20 / 30 / 40 curated products per week.
  - "Access to AliExpress and Alibaba suppliers that can source the product for you."
  - "a complete breakdown on the numbers for the product".
  - Free tools include CPA, ROAS and BEROAS calculators.
- **Inference (NV):** the pricing page lists the supplier access and numbers breakdown under Portfolio, which suggests they apply to curated picks, not to every TikTok Shop library product.
- **Claims (V) [26]:** "Spot breakouts early"; "quickly identify rising winners".
- **Accuracy:** a competitor review reports user complaints about accuracy (T, biased) [47].
- **Pricing (V) [26]:** Basic $39, Standard $59, Premium $99 per month; yearly $26 / $34 / $49 per month.

**Minea**
- **Pricing page (V) [29]**
  - Starter $49, Premium $99, Business $199 per month; quarterly $39 / $79 / $158 per month; no annual price shown.
  - The page still says TikTok ads are "coming soon", so it looks stale; the homepage lists Meta and TikTok ads [30].
- **Supplier (V) [32]:** "find the exact AliExpress supplier behind" advertised products. No matching method is given. Supplier scores use shipping, response rate and reviews, with no formula.
- **Claims (V) [29][30]:** "Winning products updated daily"; "Spot trending ads before anyone else"; "you won't miss any winning product".
- **Third-party:** TikTok Shop data reportedly needs Premium (T) [31].
- **Profit calculator:** none found.

**Winning Hunter** (V) [37]
- **What it is:** ad library (Meta, TikTok, Pinterest), a store database of 2M+, and TikTok Shop data on all plans.
- **Claim:** "spot breakout winners before they go mainstream" (V) [37], with no methodology.
- **Pricing:** billed yearly: Basic $30, Standard $49, Enterprise $150 per month; up to 40% off versus monthly billing. Monthly prices were not shown.

**TrendTrack** (V) [38]
- **What it is:** a store and ads intelligence tool, not TikTok Shop GMV. Claims "2 to 3 million new ads indexed every 24 hours".
- **Claims:** "see market shifts before they happen"; free tool: "Discover ten winning products every day".
- **Pricing:** billed yearly: Starter $34, Pro $62, Business $111 per month; Enterprise custom. Monthly prices did not render.

**Zendrop** (V) [39]
- **What it is:** a supplier and fulfilment platform with product research. Includes a "Top Winning Products" list and a Profit Margin Calculator. TikTok Shop is supported as a sales channel, not as a demand-data source.
- **Pricing:** Free; Pro $49/mo ($399/yr); Plus $79/mo ($549/yr).

**Ecomhunt** (V) [40]
- **What it is:** a curated "winning products" database (2 years), AliExpress info, and alerts by SMS and email. No TikTok Shop data.
- **Pricing:** Basic $23, Pro $39, Suite $49 per month; $279 / $468 / $588 per year. The page's own savings figures don't add up.

**Koala Inspector** (V) [41]
- **What it is:** a Chrome extension for Shopify stores.
- **"Find Suppliers":** lists suppliers of the same item with **landed cost (item, shipping, duty)** and **profit and margin at your price**. It explicitly excludes ad spend and fees. The supplier platforms are not named.
- **Pricing:** Free (15 tokens); Premium $22/mo (220 tokens).
- **Note:** this is the best-documented margin method among those reviewed, but it applies to Shopify stores, not TikTok Shop.

**FindNiche** (V) [36][42]
- **What it is:** TikTok products and shops plus AliExpress and Shopify research. Claims "early growth signals" in its own comparison blog. Margins are only loosely estimated.
- **Pricing:** homepage says "The new FindNiche is now free".

### C. Supplier platforms with discovery

**CJ Dropshipping**
- **Shopify app (V) [28]**
  - Free to install; 4.9 rating from 2,936 reviews.
  - "Trending products recommendation with CJ's big-data powered system" and "Daily trending products" captions.
  - Shipping-cost calculation; import from 1688, Taobao and AliExpress via an extension.
  - Some reviews complain that supplier prices and stock were stale (V, merchant reviews on the listing).
- **Homepage (V) [43]**
  - "View top selling products on CJ APP"; a shipping-cost and delivery-time calculator; a sourcing-request hub.
  - "Source and Sell Winning Products" is a process step, not a data claim.
- **Gaps:** no TikTok Shop demand data and no profit calculator found.
- **Implication:** a tool built on CJ's catalogue competes with CJ's own free "trending" lists. Any CJ-side price or stock staleness passes straight into the margin numbers.

**Tools that already link TikTok-trend products to suppliers:**
- Sell The Trend: CJ and AliExpress, plus AI Supplier Finder [17][20][21].
- AutoDS: TikTok Analytics to "Import & Start Sourcing" with its China warehouse [24].
- Dropship.io: Portfolio with AliExpress and Alibaba suppliers [26].
- Minea: ad to "exact AliExpress supplier" [32].

**Not found:** a "find supplier" or 1688 feature on Kalodata, FastMoss, EchoTik, Shoplus or Tabcut public pages [1][8][10][12][14]. Chinese-language searches found workflow guides (TikTok data, then 1688 same-style search) but no built-in feature (T) [48].

**Alibaba Accio** is adjacent. It is an AI sourcing agent that advertises a "Trend Analysis, then Product Discovery, then Supplier Matching" workflow (T, NV) [49]. No TikTok Shop sales data and no margin output were found.

---

## 4. Answers

### (a) Does any tool already combine TikTok Shop demand signals + supplier matching + margin calculation?

**Partly, yes. Three tools have all three pieces in some form; none documents the exact chain the proposal describes.**

| Tool | Demand signal | Supplier matching | Margin | Completeness |
|---|---|---|---|---|
| **Sell The Trend** | TikTok Shop Explorer (Pro+) [17][18] | CJ and AliExpress integrated; AI Supplier Finder for similar products [20][21] | "Profit Margin" $ on product cards, formula undisclosed [18] | **Highest.** Not verified: automatic TikTok-product-to-CJ-SKU matching, shipping-to-country in margin, break-even ad cost. |
| **AutoDS** (+ Product Finding Hub) | US TikTok Shop best-sellers with GMV [24] | Manual "Import & Start Sourcing" request to AutoDS China warehouse (paid credit); default import uses TikTok as supplier [24] | Estimated profit on Trending and Hand-Picked lists, **not** on TikTok Analytics rows [24] | **Medium.** The pieces sit in separate tabs. |
| **Dropship.io** | TikTok Shop Product Library [26][27] | AliExpress and Alibaba, apparently on curated Portfolio products [26] | "Numbers breakdown" on Portfolio; standalone BEROAS calculator [26] | **Medium.** The join is probably limited to weekly curated picks (NV). |

Other partial matches:
- **Chuhaijiang** has TikTok Shop data, a sourcing report and break-even ROAS, but no CJ link and it is aimed at Chinese sellers [34].
- **Koala Inspector** has supplier landed cost and profit, but on Shopify stores [41].

**What no one documents:**
- per-product break-even CPA or ROAS computed from **CJ price + CJ shipping to the buyer's country + TikTok or Shopify fees**;
- a match-confidence score;
- a stated formula.

The proposal's differentiation would rest on doing this transparently and at SKU level, not on being first to combine the three ideas.

### (b) Which tools claim "early" or "before it goes viral" detection, and do any publish evidence?

Exact wording, each under 15 words:

| Tool | Claim |
|---|---|
| Sell The Trend | "Discover TikTok Shop Winning Products Before They Go Viral" [18] and "identify winning products before trends peak" [19] |
| AutoDS | "Spot trends before they go viral" (ads-spy menu) [23] |
| Winning Hunter | "spot breakout winners before they go mainstream" [37] |
| Dropship.io | "Spot breakouts early" [26] |
| Minea | "Spot trending ads before anyone else" [30] |
| FastMoss | "rising trends on TikTok Shop one step ahead" [9] |
| Chuhaijiang | "Find winning TikTok Shop products before they peak" [34] |
| TrendTrack | "see market shifts before they happen" [38] |
| ShopShark | "identify trends early" [33] |
| FindNiche | "early growth signals" [42] |
| Tabcut | "Three-Day Potential List" and "Yesterday's Emerging List" [14] |

**Evidence: none.**
- No vendor reviewed publishes a backtest, hit rate, lead time, precision/recall, or before/after cohort.
- Evidence offered is limited to testimonials, which are unverifiable and in Sell The Trend's case include revenue claims [18].
- A targeted search found no independent validation study of "winning product" tools [44].
- The only quantitative accuracy figure found was an unsourced "70% accuracy" on a directory listing for a different tool [44].
- On the data side, Kalodata itself disclaims precision [1], and FastMoss's data-source answer is not shown publicly [9].
- **This is the clearest, testable gap.**

### (c) Typical price bands (list prices seen 2026-11-01, USD)

| Category | Entry tier | Mid tier | Top self-serve | Enterprise / API |
|---|---|---|---|---|
| TikTok Shop intelligence (Kalodata, FastMoss, EchoTik, Shoplus, Tabcut, ShopShark) | $10–$50/mo (EchoTik $9.9 is the outlier [7]; FastMoss $49 [8]; Shoplus $39 [11]; ShopShark $26.90 [33]; Kalodata App Store $49.99 [3]) | $60–$120/mo | $80–$180/mo | Custom (FastMoss, Kalodata, EchoTik API) |
| TikTok ad-spy with TikTok Shop data (PiPiADS) | $49/mo; about $25/mo annual promo [22] | $99/mo | $180/mo | $900/mo [22] |
| Dropshipping product research (Minea, Sell The Trend, Dropship.io, Winning Hunter, TrendTrack, Ecomhunt, Koala) | $22–$50/mo (annual about $19–$34/mo) | $59–$100/mo | $111–$300/mo | Custom (TrendTrack) |
| Dropship automation + research add-on (AutoDS) | $26.90/mo + $14.97 hub [25] | $39.90 + $14.97 | $66.90 + $14.97 | Custom |
| Supplier platforms (CJ, Zendrop) | CJ free [28]; Zendrop free | Zendrop $49/mo [39] | Zendrop $79/mo [39] | n/a |

Annual billing typically cuts 25–50% off monthly prices. Many vendors run constant "promo" pricing, so list prices are soft.

### (d) Gaps none of them seem to fill

1. **Published evidence for "early" flags.**
   - Nobody publishes a timestamped log of past flags with outcomes, such as "flagged on day X; 30-day GMV after flag; how many faded".
   - A public, honest scorecard, including misses, would be unique. It is also the main risk: it may show that early signals are weak.
2. **Transparent margin maths at SKU level.**
   - No tool states its margin formula for TikTok-sourced products.
   - None was found to combine CJ variant price, CJ shipping to a chosen country, platform fees and returns into a **break-even CPA/ROAS**.
   - Koala comes closest on landed cost, but only for Shopify [41]. Chuhaijiang has break-even ROAS but no CJ link [34].
3. **Match-quality disclosure.**
   - Supplier matching is described ("exact AliExpress supplier" [32], "similar product" [21]) but never scored.
   - Nobody exposes a match confidence or flags "similar, not identical".
4. **Uncertainty on sales estimates.**
   - Every TikTok Shop data vendor reports point estimates. None shows error bands or source agreement.
   - Nobody cross-checks, for example, Kalodata against FastMoss.
5. **Combined alerting.**
   - Monitors exist: FastMoss video and LIVE credits [8], EchoTik product monitors [7], Ecomhunt SMS and email alerts [40].
   - None found that triggers on demand acceleration **and** margin above a threshold together.

**Skeptical caveats on these gaps**
- Gaps 2–5 are features that Sell The Trend, AutoDS or Dropship.io could add quickly, since they already hold the supplier integrations.
- The proposal's demand input would be bought from a TikTok Shop data vendor that is also a potential competitor. I did not review those vendors' API or redistribution terms (NV).
- CJ's own free "trending" lists and EchoTik's very low prices put a ceiling on pricing.

---

## 5. What could not be verified

- Kalodata's and Tabcut's current web prices: both pages need sign-up or login. Kalodata's App Store prices are a proxy and include App Store pricing.
- Shoplus, Minea, Winning Hunter and TrendTrack: either monthly or annual prices did not render.
- Sell The Trend: whether TikTok Shop Explorer products map automatically to CJ SKUs, and what its "Profit Margin" includes.
- Dropship.io: whether supplier access and the numbers breakdown apply beyond curated Portfolio products. The help article URL returned 404.
- CJ Dropshipping: the current names and contents of its trending lists. Its in-app pages need login.
- Whether EchoTik's $9.9–$22.7 prices are permanent or promotional.
- Any vendor's data-licensing or API terms.
- All accuracy claims, both for and against: the only accuracy critiques found come from competitor-written reviews.

---

## 6. Sources (all accessed 2026-11-01)

1. Kalodata homepage and FAQ (methodology, "1000 Days"). The pricing link redirects to sign-up. https://www.kalodata.com/ and https://www.kalodata.com/pricing
2. Kalodata public product explorer (filters and columns). https://www.kalodata.com/product
3. Kalodata on the US App Store (in-app purchase prices). https://apps.apple.com/us/app/kalodata/id6670308912
4. Toolsurf, "Kalodata Pricing 2026" (group-buy reseller; unreliable). https://www.toolsurf.com/kalodata-pricing/
5. Winning Hunter, "Kalodata review" (competitor; dated Feb 17 / Oct 31, 2026). https://winninghunter.com/insights/kalodata-review
6. Search summary of Kalodata third-party pricing (G2 says no vendor pricing). https://g2.com/products/kalodata/pricing
7. EchoTik pricing. https://www.echotik.live/pricing (also https://echotik.live/pricing)
8. FastMoss pricing (read in browser; monthly and annual toggles). https://www.fastmoss.com/pricing
9. FastMoss homepage. https://www.fastmoss.com/
10. EchoTik homepage. https://echotik.live/
11. Shoplus pricing. https://www.shoplus.net/pricing
12. Shoplus homepage. https://www.shoplus.net/
13. iTechGuides, Shoplus listing (annual prices). https://www.itechguides.com/products/shoplus/
14. Tabcut homepage and workbench (pricing redirects to login). https://www.tabcut.com/ and https://www.tabcut.com/user/pricing
15. Copyfy, "5 best Tabcut alternatives" (competitor). https://www.copyfy.io/alternatives/5-best-tabcut-alternatives
16. Virlo, "Virlo vs Tabcut" (competitor). https://virlo.ai/compare/virlo-vs-tabcut
17. Sell The Trend pricing. https://www.sellthetrend.com/pricing
18. Sell The Trend, TikTok Shop Explorer page and FAQ (read in browser). https://www.sellthetrend.com/tiktok-shop-explorer
19. Press release, "Sell The Trend Introduces TikTok Shop Explorer" (2026-06-16). https://newsroom.xpr.media/?p=164435
20. Sell The Trend blog, CJdropshipping integration (updated 2026-03-26). https://www.sellthetrend.com/blog/cjdropshipping
21. Sell The Trend help, "How do I add a supplier if none are available" (2025-04-24). https://sellthetrend.freshdesk.com/support/solutions/articles/150000003910-how-do-i-add-a-supplier-if-none-are-available-for-a-product-
22. PiPiADS pricing (read in browser; monthly and annual). https://www.pipiads.com/pricing
23. AutoDS, "Editions Q2 2026 update" (2026-08-03). https://www.autods.com/blog/autods-editions-q2-2026-update/
24. AutoDS help, "Product Finding Hub" tools. https://intercom.help/autods---new/en/articles/12700452-autods-product-finding-hub-3-tools-to-find-profitable-products-faster
25. AutoDS pricing (read in browser; monthly and annual). https://www.autods.com/pricing/
26. Dropship.io pricing. https://www.dropship.io/pricing
27. Dropship.io Product Library / database page. https://www.dropship.io/product-database
28. CJdropshipping Shopify app listing. https://apps.shopify.com/cucheng
29. Minea pricing (read in browser). https://www.minea.com/pricing
30. Minea homepage. https://www.minea.com/
31. Dropsprint, "Minea review" (third-party). https://dropsprint-com.pages.dev/blog/minea-review
32. Minea, "Best AliExpress products". https://www.minea.com/best-aliexpress-products
33. ShopShark help centre, platform overview. https://help.shopshark.com/en/articles/14060692-shopshark-analytics-and-research-platform-for-tiktok-shop
34. Chuhaijiang, TikTok Shop product research tool. https://www.chuhaijiang.com/en/tiktok-shop-product-research-tool
35. Chuhaijiang pricing. https://www.chuhaijiang.com/en/pricing
36. FindNiche homepage. https://findniche.com/
37. Winning Hunter pricing. https://winninghunter.com/pricing
38. TrendTrack pricing. https://www.trendtrack.io/pricing
39. Zendrop pricing. https://www.zendrop.com/pricing/
40. Ecomhunt pricing. https://www.ecomhunt.com/pricing
41. Koala Inspector pricing and product-research pages. https://koala-apps.io/pricing/ and https://koala-apps.io/dropshipping/product-research/
42. FindNiche blog, "Kalodata vs FindNiche" (vendor; 2026-01-08). https://findniche.com/blog/kalodata-vs-findniche
43. CJdropshipping homepage. https://cjdropshipping.com/
44. Search for independent validation of "winning product" tools. No study found; the "70% accuracy" claim is on https://www.toolbit.ai/ai-tool/testmadesimple. Also https://thunderbit.com/blog/best-tools-finding-winning-shopify-dropshipping-products
45. Delzonic, "FastMoss Pricing 2026" (third-party; checked Sept 2026). https://delzonic.com/blogs/fastmoss-pricing-2026/
46. PiPiADS third-party reviews (Trustpilot note; old Starter/VIP/Pro prices). https://affmaven.com/pipiads-review/ and https://www.trendtrack.io/blog-post/pipiads-review
47. Dropship.io review, accuracy complaints (competitor). https://www.trendtrack.io/de/blog-post/dropship-io-review-preis-funktionen-vergleich
48. Chinese-language search: FastMoss / 1688 same-style sourcing workflows (no built-in feature found). https://www.amz123.com/ask/AMCde3HG
49. Alibaba Accio Work / sourcing toolkit coverage. https://www.digitalcommerce360.com/2026/07/24/alibaba-accio-work-agentic-ai-b2b-sourcing/
