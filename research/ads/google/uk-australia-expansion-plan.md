# Selling to the UK and Australia: plan (2026-10-28)

Owner: "you can expand to english speaking contries , UK australia, america", then "Plan selling to the UK and
Australia: what has to change in Shopify, shipping and Merchant Center first, without changing anything yet."
Nothing has been changed. Every step below that touches the store, Merchant Center or Google Ads needs the
owner's OK first.

## Where the store is today (read 2026-10-28)

- Shopify: one market, "United States"; one shipping zone, "Domestic" (US); store currency USD; only USD is
  enabled for shoppers; prices exclude tax. 92 active products, 0 orders.
- Products ship from EPROLO's warehouses in China (YANWEN / CNE lines). Known US rates are $8–15 per item;
  rates to the UK and Australia are **not known**.
- Policies: returns within **7 days** of delivery, customer pays return postage. The shipping policy says
  "We currently ship to the United States only", and US delivery is 2–3 weeks.
- Merchant Center XXX: US shipping and returns only. Google Ads Performance Max-1 is US-only and paused.

## Before anything else: two owner decisions

1. **UK VAT.** Overseas sellers shipping parcels worth £135 or less straight to UK shoppers must register for
   UK VAT and charge 20% VAT at checkout, starting with the first sale (no threshold for non-UK businesses).
   Selling to the UK means registering with HMRC first, then filing VAT returns.
   → Owner/accountant decision. Without registration, don't sell to the UK.
2. **Australian GST.** Overseas sellers must register and charge 10% GST only once their Australian sales
   reach A$75,000 a year. Below that there's no registration, so Australia can start sooner.
   (Both points are general rules; confirm with an accountant before launch.)

Also worth weighing:
- **Seasons.** Australia goes into summer in December, so knits, coats and boots won't sell there until about
  April–May. Dresses, skirts, sandals and sunglasses would. The UK is in the same season as the US.
- **UK returns law.** UK shoppers who buy online can cancel within **14 days** of delivery, and the refund must
  include the original standard delivery charge. Our 7-day policy can't apply to UK orders; they need a
  14-day UK section (the customer can still pay return postage if the policy says so).
  Australia has no change-of-mind right, but faulty items must be refunded or replaced.

## Step by step (each step waits for the owner's OK)

### 1. Supplier and costs
- Get EPROLO's real shipping prices and delivery times to the UK and Australia for 3–4 typical items
  (a 220 g top, a 550–660 g knit dress, a pair of boots), from the EPROLO app product pages.
- Run those costs through `scripts/profitability_model.py` (today it has US shipping only) to check every
  product still makes money with the shipping charge and the free-shipping threshold we'd set.
- Decide where UK/AU returns are sent, and whether returning items to China is even practical.
  (It may be cheaper to refund without asking for the item back.)

### 2. Shopify
- **Markets**: add "United Kingdom" and "Australia" (Settings > Markets), with local currency (GBP, AUD) and
  rounded prices (e.g. .99 endings), and prices **including** VAT/GST, which is what UK/AU shoppers expect.
  Check Shopify Payments supports GBP/AUD payouts on this account (the API can't read that; check in admin).
- **Taxes**: UK, only after the VAT number exists: add it in Settings > Taxes and duties > United Kingdom
  so checkout charges VAT. AU: no GST collection until the A$75k threshold.
- **Shipping** (Settings > Shipping and delivery, General profile): new zones "United Kingdom" and "Australia"
  with a standard rate and a free-shipping threshold in local money, based on step 1's costs.
- **Policies and pages**:
  - Shipping policy: drop "United States only" and add UK/AU delivery times.
  - Refund policy: add the UK 14-day cancellation section.
  - Product page "Shipping" and "Returns" blocks plus the announcement bar say "$70" and US times; make them
    market-specific or neutral.
- **Sizes**: clothing is mostly S–XL (fine). Shoes list US and EU sizes; UK shoes are about US minus 2,
  so add a size note or chart. Australia mostly uses US shoe sizes and UK-style dress sizes.
- **Domains**: Markets can serve /en-gb and /en-au on emberandclove.com, so Google sees local prices.

### 3. Merchant Center (via the Shopify Google & YouTube app)
- In the app's settings, add the United Kingdom and Australia as target countries, so the feed sends
  GBP/AUD prices from Markets.
- Shipping settings for each country: cost, free threshold, handling 2–5 days plus real transit time.
- Return policy for each country: UK 14 days; AU per the owner's choice.
- Wait for the new country listings to be reviewed. US listings are still "Available soon" too.

### 4. Google Ads (account XXX-XXX-XXXX)
- Prefer **one campaign per country** (copies of Performance Max-1 with their own budgets), so the US budget
  isn't pulled abroad and results are readable per country. Start with about $10/day each, Purchases goal,
  location = that country (presence). The ad rules stay: no price, no delivery times, no AI-disclosure text.
- The account stays in USD. Google converts GBP/AUD purchase values.
- Turn each campaign on only after its products are approved and one test checkout in that market works.

### 5. Tracking and the Hub
- Check a test checkout for each market reaches Google Ads, Meta and TikTok with the right currency.
- The Hub dashboard and profit model assume USD and US shipping; add currency conversion and per-country
  shipping before reading UK/AU profit.

## Suggested order

1. Owner decides on UK VAT (accountant) and the UK 14-day returns.
2. EPROLO UK/AU shipping quotes → profit check.
3. Australia first, if the owner wants a start without VAT registration. Push the warm-weather products, and
   the knits from about April.
4. The UK once the VAT number exists. It's the better fit for the current autumn/winter range.
5. Merchant Center countries → Google Ads campaign per country, paused until listings are approved.
