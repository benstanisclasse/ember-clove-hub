# Subscription Operations and Category-Brand Retention Economics (US Shopify DTC, as of Oct 2026)

Research date: 2026-10-19. Builds on Checkpoint 1: no AutoDS docs on subscription orders; Recharge "~3x orders"; unverified churn benchmarks; FTC click-to-cancel vacated July 2025; FTC ANPRM March 2026; CA AB 2863 effective July 1, 2025.

Source-quality legend: [PRIMARY] = vendor's own pricing page, regulator, statute, or the vendor's own report. [VENDOR-CLAIM] = a vendor's marketing claim about its own product or the market. [3P-BLOG] = third-party blog or comparison site, often written by a competitor or affiliate. [LAW-FIRM] = law-firm client alert.

---

## 1. Shopify subscription app landscape 2026 (pricing, features, fit for a small brand)

### Takeaway
At launch, a small brand can run optional subscribe-and-save on $0 to $25/month: Shopify Subscriptions is free, Seal has a free tier and 0% transaction fees, and Appstle has a free tier. The premium apps add a large fixed cost plus a cut of every subscription order: Recharge $99/month + 1.49% + 19¢, Skio $499 to $599/month + 1% + 20¢, and Stay AI reportedly ~$499/month. They only make sense once subscription GMV is in the tens of thousands of dollars per month. Shopify's native app is free but has weak swap and billing-date controls, rated 3.7/5.

### Cited Findings
**Shopify Subscriptions (native)**
- Price is "Free". It offers weekly, monthly, or yearly auto-billed subscriptions with discounts; "Subscribe and save, Fixed pricing, and Custom pricing"; customer cancel, skip, and pause; email templates; analytics; and migration of existing contracts. Launched Jan 31, 2024. Rated 3.7/5 from 866 reviews, of which 19% are 1-star. [PRIMARY] — [Shopify App Store: Shopify Subscriptions](https://apps.shopify.com/shopify-subscriptions)
- Reviews on the listing say merchants cannot change a subscription's billing date or swap products within a subscription (one wine club had customers cancel and resubscribe). The listing does not mention prepaid, bundles, or swap. [PRIMARY, user reviews] — [Shopify App Store: Shopify Subscriptions](https://apps.shopify.com/shopify-subscriptions)
- A third-party roundup says the native app does not combine bundles with subscriptions. [3P-BLOG] — [Recurpay pricing comparison 2026](https://www.recurpay.com/blog/shopify-subscription-app-pricing-comparison-2026). Recurpay ranks itself first in this comparison.

**Recharge** [PRIMARY pricing page, fetched Oct 2026]
- Starter: $99/month + 1.49% + 19¢ per transaction. Includes the widget, customer portal, upsell and cross-sell, "Smart Cancellation Prevention", Failed Payment Recovery, Win Back, workflows, gifting, and analytics with benchmarks. Excludes the JS SDK and Storefront API, and Loyalty Rewards and Referrals. 60-day free trial. — [Recharge pricing](https://getrecharge.com/pricing/)
- Plus: $499/month + 1.34% + 19¢, on a 12-month term. Adds "Customizable bundles and tiered discounts", Concierge SMS ($0.03 per US segment), loyalty, and SDK/API access. Custom tier is volume-priced. — [Recharge pricing](https://getrecharge.com/pricing/)
- Third parties report a $25/month entry tier capped at 50 subscribers, open only to net-new merchants who installed on or after Feb 9, 2026. It was not shown on the pricing page I fetched. [3P-BLOG] — [Swell: Recharge pricing teardown](https://www.swell.is/content/recharge-pricing); [Loop blog](https://www.loopwork.co/blog/best-shopify-subscription-apps)
- Kanal flags a discrepancy as of Oct 7, 2026: Recharge's Help Center billing article said 1.25%, while the pricing page and App Store said 1.49%. Kanal advises treating the merchant-portal billing terms as binding. [3P-BLOG] — [Kanal: Recharge pricing](https://getkanal.com/blog/recharge-pricing)

**Skio (now owned by Recharge)**
- Scale plan: $499/month billed annually ($5,988/yr) or $599 month-to-month, + 1% + 20¢ on every order containing a subscription. The fee applies to "the entire order total", including one-time items, shipping, and tax. Annual prepay, auto-renew, 30-day notice. Swell estimates the variable fee overtakes the platform fee at ~$36k/month subscription GMV at a $50 AOV. [3P-BLOG, competitor teardown dated Sept 16, 2026; not verified against skio.com] — [Swell: Skio pricing](https://www.swell.is/content/skio-pricing)
- Recharge announced its acquisition of Skio on Apr 30, 2026. TechCrunch reported a $105M cash price per the founder. — [Swell: Skio pricing](https://www.swell.is/content/skio-pricing); also reported by [Loop blog](https://www.loopwork.co/blog/best-shopify-subscription-apps)

**Seal Subscriptions** [PRIMARY App Store listing]
- Free: $0 for up to 50 subscriptions. SUPERSALE: $5.95/month for up to 100. RISING STAR: $9.95 for up to 250. LEGEND: $24.95 for up to 500. Every tier has 0% transaction fees and unlimited revenue, and larger plans are available "up to 150k+ subs". — [Shopify App Store: Seal Subscriptions](https://apps.shopify.com/seal-subscriptions)
- Supports classic and prepaid subscriptions, product swaps (Free tier), pause and skip, and subscription boxes. Custom cancellation flow starts at RISING STAR; retention and cancellation insights at LEGEND. Rated 4.9/5 from 3,146 reviews. — [Shopify App Store: Seal Subscriptions](https://apps.shopify.com/seal-subscriptions)

**Appstle Subscriptions** (App Store page returned 404 to my fetcher; figures are secondary)
- Free tier up to $500/month subscription revenue. Starter ~$10/month up to $5k/month. Business $30/month up to $30k/month. Business Premium $100/month up to $100k/month. 0% transaction fees on every plan. Reported 4.9 stars from 4,300+ reviews and "Built for Shopify". [3P-BLOG, 2025 guide] — [TrendTrack guide](https://wf.trendtrack.io/blog-post/best-subscription-apps-for-shopify); [Digismoothie](https://digismoothie.com/app/appstle-subscriptions); [Appstle blog on plans](https://appstle.com/blog/what-is-the-most-suitable-appstle-subscriptions-payment-plan-for-your-store/)

**Loop, Stay AI, Ordergroove**
- Loop: Ringly lists Starter at $99/month + 1% and Pro at $399/month + 0.75%. G2 lists a "Growth" plan at $99/month. Loop's own blog claims 0.75% and 0¢ per order. Sources are inconsistent. [3P-BLOG / VENDOR-CLAIM] — [Ringly: Skio alternatives](https://www.ringly.io/blog/skio-alternatives); [G2 Loop vs Ordergroove](https://www.g2.com/compare/loop-subscriptions-vs-ordergroove); [Loop blog](https://www.loopwork.co/blog/best-shopify-subscription-apps)
- Stay AI: reported "from $499/month plus 1% + $0.19 per transaction". This rests on a single third-party source. [3P-BLOG, unverified] — [Opensend roundup](https://www.opensend.com/post/best-shopify-subscription-apps)
- Ordergroove: no public pricing; quotes are custom (enterprise orientation). — [Loop: Ordergroove pricing](https://loopwork.co/blog/ordergroove-pricing) (competitor-authored); [G2](https://www.g2.com/compare/loop-subscriptions-vs-ordergroove)

**AB 2863-relevant features**
- Recharge sells "Smart Cancellation Prevention" (save flows) on Starter. — [Recharge pricing](https://getrecharge.com/pricing/)
- Seal sells a custom cancellation flow on RISING STAR and above. — [Seal App Store](https://apps.shopify.com/seal-subscriptions)
- California law limits save offers in online cancellation: a business may present a discount or benefit only if a prominent, continuously visible "click to cancel" link or button is shown at the same time (see Q7). No app I checked documents a mode certified as AB 2863-compliant. — [King & Spalding alert](https://ktslaw.com/insights/alert/2024/10/california-latest-automatic-renewal-law-amendments-take-effect-in-july-2025)

### Inferences
- **Cost arithmetic (my calculation from the published prices).** At $5k/month subscription GMV and a $40 AOV (125 orders), the cost of each app would be:
  - Recharge Starter: about $99 + $74.50 + $23.75 = ~$197/month, roughly 3.9% of subscription GMV.
  - Seal: $0 to $25/month at 0%.
  - Appstle: ~$10/month.
  - Skio: $499+ plus fees, which is not justifiable at this scale.
- Recommendation for the test phase: start with Seal or Appstle. Choose Shopify Subscriptions only if you will never need swap or prepaid. Revisit Recharge or Loop once subscription GMV exceeds roughly $20 to $30k/month or you need bundles, SDK, or loyalty, since Recharge owning Skio concentrates the premium segment.
- All of these apps run on Shopify's native Selling Plans and subscription contracts. Migrating between them is supported in principle (the native app lists "migration"), but the payment-token migration path should be confirmed before committing.

### Gaps
- I could not retrieve Appstle's live App Store pricing (404) or skio.com directly. Loop and Stay AI prices conflict across third-party sources.
- I found no vendor documentation stating explicit AB 2863 compliance (for example, a "click to cancel" button shown alongside retention offers). Each candidate's cancel flow needs a manual check.

---

## 2. Order flow: renewals, 3PLs, white-label suppliers, AutoDS; recommended architecture and test protocol

### Takeaway
On Shopify, every successful renewal billing attempt creates a normal Shopify order. Prepaid plans create $0 shipment orders in the months with no charge. 3PLs and most fulfillment apps simply ingest Shopify orders, so in principle renewals flow anywhere a normal order does. The risk sits in the downstream app's filters for $0 orders, bundles, tags, and paid status. Skeptically, there is still no public AutoDS documentation, and no merchant report I could find, confirming correct handling of subscription renewal or $0 prepaid orders. AutoDS does document that Shopify-native bundles are not auto-processed. Plan for manual fallback.

### Cited Findings
- Shopify developer docs: at renewal, the app initiates a billing attempt on the subscription contract "and a new order will be created". The `subscription_billing_attempts/success` webhook includes the `order_id`. Failed attempts have a null order_id. [PRIMARY] — [Shopify.dev: subscription contracts](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/contracts)
- Recharge tags its Shopify orders "Subscription" plus either "Subscription First Order" or "Subscription Recurring Order". Prepaid orders also get a "Prepaid" tag. [PRIMARY via search snippet; the page returned 403 to my fetcher] — [Recharge: identify Recharge orders](https://support.getrecharge.com/hc/en-us/articles/13482639209367-How-can-I-identify-Recharge-orders-in-my-ecommerce-platform)
- Recharge: "Prepaid subscriptions ship more often than you charge, therefore $0.00 shipment orders will be created each month of the subscription cycle." Prepaid future shipments sit as "queued" orders. [PRIMARY via snippet] — [Recharge: $0 prepaid order notifications](https://support.getrecharge.com/hc/en-us/articles/360008682434-Adjusting-Shopify-notification-for-0-prepaid-orders); [Recharge API docs: orders](https://docs.rechargepayments.com/docs/orders)
- 3PL flow, per DCL Logistics (a 3PL; page updated Oct 15, 2026): Recharge charges, then creates a Shopify order, then the 3PL's own Shopify integration picks it up. "No native Recharge-to-3PL connection in most implementations." DCL lists these failure points:
  - skips or swaps made after the cutoff;
  - BOM or insert changes the warehouse hasn't acknowledged;
  - failed or partial charges;
  - one-time DTC surges consuming subscription stock. It recommends separate safety stock for subscription items.

  [3P / 3PL vendor] — [DCL: Recharge 3PL integration](https://dclcorp.com/blog/technology/recharge-3pl-integration/)
- AutoDS help center:
  - Bundles created directly in Shopify are not processed by Fulfilled-by-AutoDS (FBA) or the Auto-Order automations and need manual handling.
  - Automation processes "all new eligible orders" without defining "eligible".
  - Settings apply only to orders placed after saving.
  - AutoDS updates a Shopify order only once tracking exists.

  [PRIMARY] — [AutoDS help: FBA full guide](https://help.autods.com/managing-orders/automate-your-orders-with-fulfilled-by-autods-fba-full-guide) (bundle point surfaced via search summary; the article is 174k characters and I read only the first 100k)
- AutoDS per-order control: a Shopify Community answer (~2 years old) says you cannot pause a single order in AutoDS. The workaround is to mark it fulfilled in Shopify so AutoDS skips it. [Community, dated] — [Shopify Community thread](https://community.shopify.com/t/i-dont-want-autods-to-fullfill-the-item/359797)
- I found no AutoDS article, Reddit thread, or Shopify Community thread specifically about subscription or recurring renewal orders or $0 prepaid orders. Searches returned only AutoDS's own billing complaints. — [Shopify Community: AutoDS billing](https://community.shopify.com/t/why-am-i-being-overcharged-for-my-autods-subscription/229890)
- Dripshipper (US white-label coffee) is a Shopify app that auto-fulfills orders from US facilities in 3 to 5 business days. Starter plan from $30/month with a 14-day trial. One reviewer calls it expensive. I found no public documentation of Recharge or subscription-order handling. [PRIMARY listing + 3P] — [Shopify App Store: Dripshipper](https://apps.shopify.com/dripshipper?locale=it)
- Shopify Collective: I found no official statement either way on subscription support. Community and dev posts document API gaps: there is no API for supplier connections or price lists, and no webhooks for inventory sync updates. Shopify Payments and a paid plan are required. [Community / 3P] — [Shopify dev community: Collective limitations](https://community.shopify.dev/t/shopify-collective-docs-and-limitations/13036); [Wholesale Helper](https://wholesalehelper.io/blog/shopify-collective/)

### Inferences
**Recommended architecture**
- **Phase A (test, 0 to ~300 orders/month).**
  - Hardware hero: AutoDS, US-warehouse supplier preferred.
  - Consumables: a US white-label app (Dripshipper-type) or US private-label stock self-shipped.
  - Subscriptions: Seal or Appstle, offered only on the consumable SKUs and only as pay-per-delivery (no prepaid) in Phase A. This avoids the $0-order edge case.
  - Do not build subscriptions as Shopify bundles, because AutoDS won't auto-process them.
  - Use separate SKUs and suppliers so hardware renewals never need to route through AutoDS.
- **Phase B (3PL).** Move consumables first, since repeat SKUs are predictable. Keep hardware on dropship until velocity justifies stocking it. Introduce prepaid only after confirming in writing that the 3PL ingests $0 orders.
- **Routing.**
  - Use the subscription app's order tags (for example "Subscription Recurring Order") plus a Shopify Flow or location rule to assign renewal orders to the right fulfillment location.
  - Hold any renewal with a hardware item, or a $0 value, for manual review until proven.

**Test protocol** (run before launch, and again after any app change)
1. Place a first subscription order with a test card or a 100% discount. Confirm the order arrives in AutoDS, the supplier app, or the 3PL portal. Confirm tags.
2. Force renewal using the app's "process now" or "charge now" for a test contract. Confirm a new Shopify order is created and auto-routed.
3. Test skip, swap (to a SKU at a different supplier), pause, and cancel. Confirm no order is generated, or the right supplier receives it.
4. Test a mixed order (subscription consumable + one-time hardware). Confirm the order is split correctly between AutoDS and the US supplier, and that the subscription app's fee basis is correct (Skio charges on the full order).
5. Test a prepaid plan in a staging store. Confirm whether the $0 child order is imported or skipped by each fulfillment app.
6. Test a failed payment or dunning case and confirm nothing ships.
7. Test inventory at zero. Confirm the renewal is held, not silently AutoDS-ordered from an alternate supplier.
8. Document results. Repeat monthly for the first 3 cycles on live orders.

### Gaps
- There is no primary AutoDS, DSers, or CJ documentation on recurring or subscription orders or $0 orders, and I found no merchant reports in public forums. DSers and CJ equivalents were not researched due to tool-call limits.
- ShipBob, ShipMonk, Red Stag, Flowspace, and Ware2Go documentation on $0 prepaid order handling was not found publicly. Ask each 3PL in writing.
- Shopify Collective subscription compatibility is unconfirmed.

---

## 3. 3PL economics for a small brand; when to switch from dropshipping

### Takeaway
None of the big 3PLs (ShipBob, ShipMonk, Red Stag) publish an official rate card. Every figure below is third-party or quote-based and conflicting. Rough planning numbers:
- Pick/pack: ~$2 to $3 for the first item plus $0.30 to $0.75 per additional item.
- Storage: ~$1 to $10 per bin or shelf per month, and $15 to $40 per pallet.
- Receiving: ~$25 to $45 per hour.
- Minimums: Red Stag is the least small-brand-friendly at 100 to 500 orders/month.

The commonly cited switch threshold, ~300 to 500 orders/month, is lore rather than data, and it applies to self-fulfillment, not dropshipping.

### Cited Findings
- ShipBob: requires a quote. Reported storage is ~$5/bin, $10/shelf, and $40/pallet per month. Receiving is ~$25 to $35 for the first 2 hours, then ~$40 to $45/hour. Pick fee covers the first few items, then ~$0.20 to $0.30 per extra item. Onboarding ~$500 to $1,000 (one source says from $975). All-in ~$4 to $10 per order. [3P-BLOG, some data dated Dec 2022] — [Dupple ShipBob review (Aug 2026)](https://dupple.com/reviews/shipbob); [FitSmallBusiness](https://fitsmallbusiness.com/best-fulfillment-warehouse/); [Business.org (dated 12/2022)](https://www.business.org/finance/inventory-management/shipbob-review/)
- Eightx claims 2026 ShipBob quotes include 3 to 5% Q4 storage surcharges and a 3% dashboard fee on some accounts. Uncorroborated. — [Eightx: ShipBob vs ShipMonk vs regional](https://eightx.co/blog/shipbob-shipmonk-regional-3pl-cost)
- ShipMonk: custom quote. Reported first pick $1.80 to $3.00, additional items $0.35 to $0.75. Bin storage $1 to $4/month (small to XL), pallet $25/month (undated). A $250/month minimum pick-pack fee is reported but possibly outdated. [3P-BLOG] — [Fulfill.com ShipBob vs ShipMonk](https://www.fulfill.com/shipbob-vs-shipmonk); [Toolradar ShipMonk](https://toolradar.com/tools/shipmonk/pricing); [Fulfyld ShipMonk calculator](https://www.fulfyld.com/tools/shipmonk-pricing-calculator/)
- Red Stag: published minimums conflict (100, ~200, or 500 orders/month). Storage ~$0.75/cu ft, or $2/bin and $15/pallet. Pick ~$1.80 to $3.00 first item, ~$0.30 to $0.75 per additional item. Receiving ~$14.25/pallet. No setup fee. Positioned for heavy and bulky goods. [3P-BLOG] — [FitSmallBusiness Red Stag review](https://fitsmallbusiness.com/red-stag-fulfillment-review/); [ShipScience Red Stag vs ShipMonk](https://shipscience.com/red-stag-fulfillment-vs-shipmonk); [eCommerceCEO](https://www.ecommerceceo.com/reviews/red-stag-fulfillment/)
- Switch thresholds:
  - ~300 to 500 orders/month is "the most commonly cited break-even threshold", "a starting point, not a rule".
  - Under 100 orders/month is generally a stay-in-house range.
  - Alternative trigger: more than 15 founder hours/week on fulfillment.
  - Error and complexity triggers (multi-SKU orders, mis-ships) matter more than volume.

  [3P-BLOG, including 3PL-vendor sources] — [EasySell 2026 3PL transition](https://easysellapp.com/blogs/wiki/shopify-3pl-transition-when-to-outsource-fulfillment-2026); [Endless Commerce playbook](https://endlesscommerce.com/playbook/3pl-vs-inhouse-decision-framework/); [Fulfillrite](https://www.fulfillrite.com/blog/when-should-an-ecommerce-business-outsource-fulfillment/)

### Inferences
- For a dropship-to-3PL move, the real trigger is unit economics and control, not order count:
  - landed cost of bulk-imported inventory + 3PL fees versus the per-unit dropship cost;
  - shipping speed (China dropship lead times hurt subscription retention);
  - branded packaging and inserts, which dropship suppliers often can't do.
- Consumables on subscription justify a 3PL earliest because demand is forecastable. A reasonable gate: about 100 to 200 consumable orders/month plus a confirmed sell-through of the first private-label MOQ batch.
- Expect roughly $3 to $5 per order in fulfillment fees (excluding postage) at small volume. Minimum-fee contracts can push effective cost higher below ~200 orders. Smaller regional 3PLs often have no minimums, but I have no sourced rate cards for them.

### Gaps
- No official 2025 to 2026 rate cards from ShipBob, ShipMonk, or Red Stag. Flowspace and Ware2Go pricing was not found. Smaller 3PLs with published rates were not researched.
- No credible data-driven study of a dropship-to-3PL threshold. All thresholds are practitioner heuristics.

---

## 4. Credible retention data: repeat rates, cross-sell, email/SMS share, subscription churn

### Takeaway
Independent, methodology-transparent retention data is scarce. Almost everything is vendor-sourced. The most transparent repeat-purchase figure is about 25% average and 22.5% median across ~1,500 Shopify stores (Little Stream Software, 2024). Recharge's 2026 report claims subscribers place "nearly 3x" more orders than one-time buyers, but its public page gives no churn by vertical. The category churn numbers in circulation are secondhand and conflict: health and wellness is cited at 4.2% monthly (2023) versus 8.8% (2026). Klaviyo's own 2026 benchmarks give rates and the flow/campaign revenue split, but not email's share of total store revenue.

### Cited Findings
**Repeat purchase**
- Little Stream Software analysis (2024) of 1,500+ Shopify stores: 25% average and 22.5% median repeat purchase rate, as relayed by Joy, which calls it the most methodologically transparent study. [3P, via vendor blog] — [Joy: customer retention benchmarks](https://joy.so/customer-retention-benchmarks/)
- Rivo puts the ecommerce repeat purchase rate at 28.2% average, ranging from 9.9% (luxury) to 65.2% (grocery), with CBD at 36.2%. Methodology unclear. [VENDOR-CLAIM, loyalty app] — [Rivo: repeat purchase rate guide](https://rivo.io/blog/repeat-purchase-rate-complete-guide)
- Joy warns that many published tables recycle the same older datasets and conflate retention rate with repeat purchase rate. — [Joy](https://joy.so/customer-retention-benchmarks/)

**Subscriptions**
- Recharge 2026 Subscription Trend Report (20,000 brands):
  - subscribers placed "nearly 3x more orders than one-time shoppers";
  - subscription checkouts up 16% vs one-time;
  - same-day cancels down 35%;
  - brands increased first-order discounts 18%.

  The public page has no churn by vertical, AOV, or time period. [PRIMARY vendor report] — [Recharge 2026 Subscription Trend Report](https://getrecharge.com/reports/subscription-trend-report-2026/)
- Eightx says Recharge data put health and wellness at ~4.2% monthly churn in 2023 (~3% voluntary + 1.2% involuntary) and 8.8% in the 2026 report (112M orders). I could not verify this against Recharge. [3P, secondhand] — [Eightx: supplement churn benchmark](https://eightx.co/blog/supplement-subscription-churn-rate-benchmark)
- Replenishment (supplements, household consumables, pet) is cited at 5 to 8% monthly churn, curation boxes at 10 to 15%, meal kits at 8 to 15%, and a cross-category average of 5.3%. This is an aggregated blog compilation. [3P-BLOG] — [Eightx: churn by category](https://www.eightx.co/blog/average-subscription-churn-rate-by-category)
- Involuntary churn share conflicts: 68% (attributed to Recurly) versus 30 to 40% in another benchmark. [3P-BLOG] — [Ringly subscription statistics 2026](https://www.ringly.io/blog/subscription-box-statistics-2026)
- Recurly's 2026 State of Subscriptions (2,200+ businesses) says growth is slowing and pause-and-return is a core retention lever. [VENDOR report] — [Subscription Insider on Recurly](https://www.subscriptioninsider.com/article-type/news/recurlys-annual-state-of-subscriptions-pause-and-return-becomes-a-core-retention-lever)
- Eightx's estimate that a subscriber averages 8 to 18 orders before churning (versus 1 to 1.5 for a one-time buyer) is a third-party estimate, not Recharge data. — [Eightx](https://eightx.co/blog/average-subscription-of-revenue-for-dtc)

**Email and SMS (Klaviyo 2026)** [PRIMARY vendor benchmark, 183,000+ customers]
- "Good" open rate 31% for campaigns and 32.2% for flows. "Good" click rate 1.69% for campaigns and 5.58% for flows; top 10% reach 3.38% and 10.48%. — [Klaviyo email benchmarks](https://www.klaviyo.com/products/email-marketing/benchmarks)
- Placed-order rates by industry (campaign / flow), relevant to candidate categories:

  | Industry | Campaigns | Flows |
  |---|---|---|
  | Automotive | 1.03% | 1.7% |
  | Home & garden | 1.34% | 2.17% |
  | Hardware & home improvement | 1.28% | 1.96% |
  | Sporting goods | 1.18% | 1.79% |
  | Toys & hobbies | 1.07% | 1.75% |
  | Food & beverage | 1.16% | 1.79% |

  Pet is not listed. — [Klaviyo email benchmarks](https://www.klaviyo.com/products/email-marketing/benchmarks)
- Flows are 5.3% of sends but "nearly 41%" of email revenue. Flow revenue per recipient (RPR) is ~18x campaign RPR, and top-10% flows reach RPR up to $7.79. — [Klaviyo email benchmarks](https://www.klaviyo.com/products/email-marketing/benchmarks)
- SMS: flows are 7.6% of sends but 45.2% of SMS revenue, per secondary sites citing Klaviyo's SMS benchmark page (not directly verified). Postscript's 2026 Shopify data puts median revenue per message at $0.98. — [Klaviyo SMS benchmarks](https://www.klaviyo.com/products/sms-marketing/benchmarks); [ClickMinded SMS benchmarks](https://www.clickminded.com/sms-marketing-benchmarks/)
- Email share of total store revenue:
  - Eightx attributes 27% to Klaviyo's 2026 benchmark, which I could not confirm on Klaviyo's page.
  - Eightx argues brands under $10M are closer to 15 to 20%, because the benchmark cohort skews mature.
  - SMS is 10 to 20% for mature programs.

  [3P, secondhand] — [Eightx email revenue share](https://eightx.co/blog/average-ecommerce-email-revenue-share-by-vertical-2026); [Eightx SMS revenue share](https://eightx.co/blog/average-ecommerce-sms-revenue-share-by-vertical-2026)

### Inferences
- **Modeling base case** for a new category brand: 20 to 25% of first-time customers make a second purchase within 12 months. That is the Little Stream median, with no category premium assumed. Subscription attach of single-digit to low-teens percent on consumable SKUs is my assumption, not sourced.
- **Subscription churn.** Use 6 to 10% monthly for replenishment consumables in the base case, not the "<4%" vendor figure from Checkpoint 1. The 2026 health and wellness figure (8.8%) suggests churn has risen. For hobby consumables (paints, detailing chemicals) use-rates are lumpy, so expect higher skip and cancel rates than for coffee or litter. This is an inference.
- The "3x orders" stat is a selection-biased comparison: people who subscribe are already heavy users. It should not be read as subscription *causing* 3x orders.
- **Email/SMS revenue share** for a new brand: plan on 15 to 20%, mostly from flows (welcome, post-purchase cross-sell, replenishment reminders).

### Gaps
- No primary cross-sell attach-rate benchmark found for Shopify brands.
- Recharge's full 2026 report PDF is gated, so category churn is not verified.
- No primary Metrilo, Yotpo, or Repeat category data was retrieved, and nothing from Skio, Ordergroove, Subscribe Pro, or McKinsey. McKinsey's often-cited 2018 subscription survey is older and was not re-fetched.
- No category-specific data for espresso accessories, cat products, car detailing, mini painting, or pickleball.

---

## 5. Brand-building cost benchmarks for a lean launch

### Takeaway
A lean launch stack is feasible for low thousands of dollars:
- Shopify Basic: $39/month ($29 annual).
- Subscription app: $0 to $25/month.
- AutoDS and supplier apps: ~$30 to $50+/month.
- Klaviyo.
- UGC: Billo from $99/video.
- Packaging: Packlane self-serve has no MOQ; ~$0.93/unit at 500 for a small mailer in a dated quote.
- Logo-only private label on stock items: commonly 50 to 300 units. Custom molds need 500+.

Most rate cards here are third-party and should be re-quoted.

### Cited Findings
- **Shopify (US):**
  - Basic $39/month ($29 annual); Grow $105 ($79 annual); Advanced $399 ($299 annual).
  - Card rates are listed as 2.9% + 30¢, 2.7% + 30¢, and 2.5% + 30¢ respectively.
  - Plus ~$2,300 to $2,500/month as of Mar 2026.

  [3P-BLOG consistent across sources; not checked against shopify.com] — [WebsiteBuilderExpert Shopify pricing 2026](https://www.websitebuilderexpert.com/ecommerce-website-builders/shopify-pricing/); [Swell Shopify pricing](https://www.swell.is/content/shopify-pricing)
- **Billo:** "starts at $99 per video", creator pay included. Reviewers say add-ons push the effective cost toward ~$150. [PRIMARY + 3P] — [Billo pricing explainer](https://billo.app/?p=54672); [Ainfluencer Billo review 2026](https://ainfluencer.com/billo/)
- **Insense:** subscription marketplace. Estimates are $400 to $800/month plus creator fees (one source says a 7 to 20% marketplace fee). Managed service from ~$1,600/month. [3P-BLOG, conflicting] — [Elev8or Billo vs Insense](https://www.elev8or.io/compare/billo-vs-insense); [Makeinfluence](https://www.makeinfluence.com/en/academy/billo-trend-and-insense-international-ugc-content-marketplaces)
- **Packlane:**
  - Self-serve mailers have no MOQ. Bulk "Packlane Plus" pricing is for 2,000+ units. [PRIMARY] — [Packlane bulk mailer boxes](https://packlane.com/bulk-mailer-boxes)
  - Example quote for a 4x4x2 in mailer: ~$68 to $72 for 1 unit, $0.93/unit at 500, $0.76/unit at 2,000. [3P, likely dated] — [eCommerceCEO Packlane review](https://www.ecommerceceo.com/reviews/packlane/); [Ecommerce-Platforms Packlane review](https://ecommerce-platforms.com/packaging/packlane-review)
- **noissue:**
  - Custom tissue: minimum 250 sheets from $125 (2020, outdated).
  - Custom 6x9 poly mailers: $4.80/unit at MOQ 25, falling to $0.21 at 5,000 (undated).

  [3P] — [Akula Kreative 2020](https://akulakreative.com/blog/2020/7/product-review-noissue-custom-tissue-paper-tape-and-stamps); [eCommerceCEO noissue](https://www.ecommerceceo.com/?p=11030423)
- **Private-label MOQs** (Alibaba seller blog, 2026, general guidance):
  - Logo on stock or template items: 50 to 100 units, 7 to 14 days, at a 10 to 20% cost premium.
  - Pet supplies low-MOQ: 100 to 300 units.
  - Laser engraving 50 to 100; screen print 100 to 250; embossing 200 to 500.
  - Custom molds 500+. Rigid boxes typically 500+.

  [VENDOR/marketplace blog] — [Alibaba seller blog: low MOQ custom logo](https://seller.alibaba.com/blogs/2026/southeast-asia/healthcare-supplements/low-moq-custom-logo-guide-alibaba-b2b); [Alibaba: pet supplies MOQ 100](https://seller.alibaba.com/blogs/2026/southeast-asia/pet-supplies/moq-lead-time-flexible-sourcing-guide-alibaba-b2b)
- **Dripshipper** (white-label coffee): from $30/month. — [Shopify App Store: Dripshipper](https://apps.shopify.com/dripshipper?locale=it)
- **AutoDS:** the App Store lists recurring charges every 30 days; rated 4.4 from 1,312 reviews, 9% 1-star. One user reported being billed $374.19 after choosing a $49.99 plan; a moderator suggested an annual-plan mix-up. — [Shopify Community AutoDS billing](https://community.shopify.com/t/why-am-i-being-overcharged-for-my-autods-subscription/229890)

### Inferences
**Indicative monthly software stack** (my sum of the sourced figures): ~$150 to $300/month in the test phase.

| Item | Monthly cost |
|---|---|
| Shopify Basic | $39 |
| AutoDS | ~$27 to $50 (plan price not verified) |
| Subscription app | $0 to $25 |
| Klaviyo | free to ~$45 at small list sizes (not verified) |
| Reviews app | ~$15 to $50 (not verified) |

This excludes UGC and ad spend.

**Initial UGC budget:** 5 to 10 Billo videos = ~$500 to $1,500.

### Gaps
- No sourced 2025 to 2026 rate cards for logo or packaging design (Fiverr, 99designs, agencies). Klaviyo, AutoDS, and review-app plan prices were not fetched.
- No sourced #paid rates. Arka MOQs were not found. No 1688-specific data.
- Product photography rates were not found.

---

## 6. Category-brand precedents (hero, then category)

### Takeaway
The precedents support "hero, then adjacent hardware, then consumables or recurring" over multi-year timelines, usually with venture funding and retail. Fellow went from a 2013 steeper to the Stagg kettle (2014/15), the EKG (2016), and the Ode grinder (2019). Wild One launched in 2018 with a walk kit and expanded into toys, carriers, grooming, and treats. Tuft + Paw (founded 2016, furniture and litter boxes) added a subscribable litter in 2023, about 7 years in. Our Place went from the Always Pan (2019) to appliances in 2023. Consumables arrived years after the hero in most cases. Good primary interview sourcing on sequencing was thin.

### Cited Findings
- **Fellow:**
  - Began as a 2013 Kickstarter with the Duo Coffee Steeper. The Stagg stovetop kettle followed (2014 or 2015; sources conflict), then the Stagg EKG electric kettle via Kickstarter (2016), and the Ode grinder in 2019.
  - In 2018 it took over the Barista Hustle tools line and launched a partnerships program to roll out 2 to 3 products/year with outside designers.
  - First flagship store in 2017. $30M Series B (NextWorld Evergreen) to expand products, content, and retail.

  — [SFMOMA store Q&A](https://museumstore.sfmoma.org/blogs/news/who-is-fellow); [Daily Coffee News 2018](https://dailycoffeenews.com/2018/11/13/fellow-products-partners-with-barista-hustle-makes-several-launches); [TechCrunch (Series B)](https://techcrunch.com/?p=2337293); [Phable](https://www.phable.io/phable-labs/fellow-redefining-coffee-brewing-through-design-and-innovation)
- **Wild One:**
  - Launched 2018 with a dog-walking kit (collar or harness, leash, poop-bag carrier). Expanded into toys and travel carriers, then grooming, single-ingredient and baked treats, with supplements planned.
  - Built an XS harness after 2,000+ customer requests.
  - Wholesale: Bloomingdale's, Nordstrom, Anthropologie, and Target.

  Coverage is mostly 2019 to 2021. — [The Wildest: Behind the Brand](https://www.thewildest.com/dog-shopping/wild-one); [NBC Select](https://www.nbcnews.com/select/shopping/wild-one-extra-small-harness-ncna1264576); [Fast Company 2019](https://www.fastcompany.com/90287410/finally-dog-gear-for-design-snobs)
- **Tuft + Paw:**
  - Founded 2016 in Vancouver by Jackson Cunningham. The Cove litter box is its most popular product.
  - Launched "Really Great Cat Litter" (tofu-based) in 2023 and updated it in 2025. $29 per 9.25 lb bag, with free shipping on Subscribe & Save.

  — [Cats.com review](https://cats.com/tuft-paw-really-great-cat-litter-review); [Thingtesting](https://thingtesting.com/brands/tuft-and-paw)
- **Our Place:**
  - Always Pan was the hero. Wonder Oven and Dream Cooker launched as a move into small appliances (2023, per Jan 2024 article). Expanded into a full homeware assortment with limited cultural collections.
  - Planned 2 to 4 cooking-tradition product lines per year (2020). Stores "always part of the plan".

  — [Canadian Business](https://canadianbusiness.com/?p=27073); [Inc. 2020](https://www.inc.com/leigh-buchanan/our-place-cooking-malala-fund-founder.html); [Retail Dive](https://retaildive.com/news/our-place-founder-ceo-physical-retail-stores/625376)
- **Chemical Guys:**
  - Origins are poorly sourced: CB Insights lists founding as 1968 in Gardena, CA, and David Knotek as founder/CEO.
  - Expanded into Smart Detailing University and Detail Garage franchise retail (founded 2016; 59 locations per a 2019 release).
  - CB Insights lists an Aug 2026 strategic sale of Fast5Xpress to Chemical Guys (headline only).

  It is not a clean "single hero" precedent; it is consumables-first. — [CB Insights](https://www.cbinsights.com/investor/chemical-guys); [Franchising.com 2019](https://www.franchising.com/amp/news/20191114_detail_garage_expands_further_into_california_with.html)

### Inferences
- In the precedents, the hero-to-consumable gap is multi-year: Tuft + Paw took ~7 years and Fellow's consumables are minor. Brands relied on design-led hardware and retail distribution, not subscriptions, for the second leg.
- That argues against modeling high subscription revenue in year 1 for a new brand. Treat subscriptions as an upside option on consumables, with the core plan driven by cross-sell of adjacent hardware and accessories.
- Wild One shows customer-request-driven line extension, a useful low-risk expansion signal.

### Gaps
- No interview-sourced details for Normcore, Hismile, or Chemical Guys' early sequencing. No revenue or timing metrics for any expansion step.
- No data on what share of revenue consumables or subscriptions eventually represent at these brands.

---

## 7. Compliance: AB 2863, other states, card-network rules, FTC status (Oct 2026)

### Takeaway
California's amended Automatic Renewal Law (ARL), via AB 2863 (effective for contracts entered into, amended, or extended on or after July 1, 2025), is the de facto national standard for a US Shopify brand. It requires:
- separate express consent to renewal terms;
- consent records kept 3 years, or 1 year after termination if longer;
- online "click to cancel";
- save offers only alongside a visible cancel button;
- annual reminders;
- price-change notice 7 to 30 days ahead;
- free-to-pay trials covered.

The FTC's 2024 click-to-cancel rule was vacated on July 8, 2025. An ANPRM on Mar 11, 2026 restarted rulemaking, but no new rule is in force. ROSCA enforcement continues. Visa requires a 7-day pre-conversion reminder for free and intro trials.

### Cited Findings
- **AB 2863:** signed Sept 24, 2024; applies to contracts entered into, amended, or extended on or after July 1, 2025. [LAW-FIRM] — [King & Spalding](https://ktslaw.com/insights/alert/2024/10/california-latest-automatic-renewal-law-amendments-take-effect-in-july-2025); [Davis Wright Tremaine](https://dwt.com/insights/2024/10/ab-2863-updates-california-automatic-renewal-law)
- **Consent and records:** requires "express affirmative consent to the automatic renewal or continuous service offer". DWT reads this as effectively requiring two consents. Consent records must be kept 3 years or 1 year after termination, whichever is longer. — [King & Spalding](https://ktslaw.com/insights/alert/2024/10/california-latest-automatic-renewal-law-amendments-take-effect-in-july-2025); [DWT](https://dwt.com/insights/2024/10/ab-2863-updates-california-automatic-renewal-law)
- **Disclosure timing:** the business must disclose auto-renewal, renewal terms, and charge amount before billing information is confirmed. — [DWT](https://dwt.com/insights/2024/10/ab-2863-updates-california-automatic-renewal-law)
- **Cancellation:**
  - Must be available in the medium used to sign up; online sign-ups need an online cancel.
  - Save offers online are allowed only with a "prominent, continuously visible" "click to cancel" link or button shown at the same time.
  - Phone: if a toll-free number is offered, it must be answered promptly, and voicemails returned within 1 business day.

  — [King & Spalding](https://ktslaw.com/insights/alert/2024/10/california-latest-automatic-renewal-law-amendments-take-effect-in-july-2025)
- **Price change and annual reminder:**
  - Price changes need clear notice 7 to 30 days before taking effect, with retainable cancel instructions.
  - An annual reminder must state the product, charge frequency and amount, and how to cancel, sent in the activation medium.
  - Free-to-pay conversions are now covered.
  - Any material misrepresentation is actionable.

  — [King & Spalding](https://ktslaw.com/insights/alert/2024/10/california-latest-automatic-renewal-law-amendments-take-effect-in-july-2025)
- **FTC:**
  - The Eighth Circuit vacated the Negative Option ("Click-to-Cancel") Rule on July 8, 2025, on procedural grounds.
  - The FTC sent a draft ANPRM to OIRA on Jan 30, 2026 and issued the ANPRM on Mar 11, 2026. Comments were due ~30 days after Federal Register publication (one source says Mar 13 publication, comments due Apr 13, 2026).
  - Commentators expect consent and disclosure provisions to return. Enforcement under ROSCA continues.
  - I found no proposed rule (NPRM) or final rule as of Oct 2026.

  [LAW-FIRM] — [Sidley (Feb 2026)](https://www.sidley.com/en/insights/newsupdates/2026/02/us-ftc-signals-renewed-interest-in-click-to-cancel-rulemaking); [Kelley Drye](https://www.kelleydrye.com/viewpoints/blogs/ad-law-access/ftc-relaunches-negative-option-rulemaking-with-new-questions-new-branding); [Jones Day (May 2026)](https://www.jonesday.com/en/insights/2026/05/ftc-revives-clicktocancel-rule-new-risks-for-subscription-businesses); [Troutman / Regulatory Oversight (Mar 2026)](https://www.regulatoryoversight.com/2026/03/ftc-revives-negative-option-rulemaking/); [CommLaw Group](https://commlawgroup.com/2026/ftc-reopens-the-click-to-cancel-debate-new-negative-option-anprm-puts-subscription-businesses-on-notice/)
- **New York:**
  - Existing ARL is General Business Law §527-a.
  - Pending 2025-26 "click to cancel act" (A3928 / S5615, multiple amended versions) would add cancellation terms, post-trial price disclosure, and, in one version, a notice 3 to 21 days before the cancellation deadline for trials over 31 days.
  - Enactment status was not confirmed.

  [PRIMARY bill text] — [NY Senate A3928](https://www.nysenate.gov/legislation/bills/2025/A3928/amendment/A); [S5615A PDF](https://legislation.nysenate.gov/pdf/bills/2025/S5615A)
- **Visa** (Article AI09334, Sept 26, 2019; effective Apr 18, 2020): applies to merchants offering free trials or introductory promotions that roll into subscriptions, physical or digital goods alike, and is "strongly recommended" but "not mandatory" for subscriptions without trials. Requirements:
  - notify the cardholder at least 7 days before the trial ends, electronically, with a simple cancel mechanism;
  - for trials under 7 days, put the reminder details in the initial confirmation;
  - online cancellation must be possible without a phone call;
  - an enhanced "trial" descriptor on the first post-trial transaction;
  - expanded dispute rights under condition 13.5.

  [PRIMARY] — [Visa subscription policy PDF](https://usa.visa.com/dam/VCOM/global/support-legal/documents/subscription-policy-vbn-visa-public.pdf)
- **Mastercard:** reported to require cardholder opt-in for trial-to-subscription. Details and timing were unclear in the sources found. [Press, undated] — [loveMONEY](https://www.lovemoney.com/news/amp/81124/mastercard-visa-free-trial-subscription-traps-scams-rip-off-refund-your-rights)

### Inferences
**Practical compliance spec for the brand** (applies to all US customers):
- an unchecked consent checkbox for auto-renew terms, separate from the purchase terms;
- terms shown next to the subscribe CTA, with price, frequency, and how to cancel;
- a confirmation email repeating the terms and the cancel link;
- a self-serve online cancel in the customer portal with no forced chat or call;
- any save offer shown alongside a persistent "cancel" button;
- a price-change email 7 to 30 days ahead;
- an annual reminder email;
- consent logs kept 3+ years;
- avoid free trials, or if used, send a 7-day pre-conversion reminder and use the trial descriptor.

A replenishment subscribe-and-save with no trial avoids most Visa trial rules.

**Verify each app's cancel flow** against the save-offer rule before enabling retention offers.

### Gaps
- No up-to-date state-by-state ARL tracker was retrieved. Other states (for example Colorado, Minnesota, Virginia, Delaware) were not researched.
- NY A3928/S5615 enactment status is unknown.
- Current Mastercard rulebook text was not retrieved.
- Statutory text (Bus. & Prof. Code §§17600-17606) was not read directly; the summaries rely on law-firm alerts.
