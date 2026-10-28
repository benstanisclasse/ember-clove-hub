# Variable and Fixed Cost Inputs: Small US Shopify DTC Brand (Cat Fountain BASE / Espresso Kit SHADOW), as of Oct 19, 2026

Research date: 2026-10-19. Every figure has a source and a date where one was available. "VENDOR CLAIM" means the figure comes from a party selling the service, or from a marketing or SEO blog. "ASSUMPTION" means no source was found and the value is a planning placeholder. Several primary pages (UPS fuel surcharge page, AutoDS pricing page, Federal Register June 2026 postal rule) were blocked or did not render, and the gaps are noted where that happened.

Important 2026 context the model must reflect (sources in Q3/Q4):
- The Supreme Court struck down IEEPA tariffs on Feb 20, 2026.
- A 10% Section 122 surcharge ran from Feb 24 to Jul 24, 2026.
- A Section 301 "forced-labor" duty (12.5% for China) has applied since Jul 24, 2026, stacked on the existing Section 301 China lists.
- USPS added a temporary 8% surcharge (Apr 26, 2026 to Jan 17, 2027) and changed its dim divisor from 166 to 139 on Jul 12, 2026.
- The Strait of Hormuz disruption since late Feb 2026 pushed up fuel surcharges and ocean rates.

---

## Q1. Parcel rates: USPS Ground Advantage, UPS Ground, discounted platforms (0.5/1/2/3 lb, zones 2/5/8), 2026 changes, dim weight

### Takeaway
USPS Notice 123 (edition effective Oct 4, 2026) gives Ground Advantage commercial rates of about $7.34–$8.95 under 1 lb, $8.48–$13.42 at 2 lb, and $9.06–$16.30 at 3 lb (zones 2–8). These rates include a temporary 8% surcharge that runs to Jan 17, 2027. The 10x10x8 box (800 cu in) is under USPS's 1,728 cu in dim threshold, so USPS bills it at actual weight. UPS would bill it at dimensional weight (~6 lb billable). Pirate Ship and Shopify Shipping rates (below-commercial, with ounce tiers kept) could not be pulled cell by cell.

### Cited Findings
**USPS Ground Advantage, Notice 123, edition effective Oct 4, 2026** ([USPS Notice 123](https://pe.usps.com/text/dmm300/Notice123.htm), fetched 2026-10-19; extracted by tool, so verify the cells before final use):

| Weight | Retail Z2 | Retail Z5 | Retail Z8 | Commercial Z2 | Commercial Z5 | Commercial Z8 |
|---|---|---|---|---|---|---|
| 8 oz (0.5 lb) | $8.55 | $9.35 | $10.20 | $7.34 | $8.24 | $8.95 |
| 15.999 oz | $10.45 | $11.70 | $13.65 | $7.34 | $8.24 | $8.95 |
| 1 lb | $10.45 | $11.70 | $13.65 | $8.08 | $9.29 | $11.22 |
| 2 lb | $12.00 | $14.85 | $19.80 | $8.48 | $10.50 | $13.42 |
| 3 lb | $12.50 | $15.70 | $23.15 | $9.06 | $12.12 | $16.30 |

- Notice 123 also says "Parcels that exceed one cubic foot (1,728 cubic inches) are charged based on the actual weight or the dimensional weight, whichever is greater." — [USPS Notice 123](https://pe.usps.com/text/dmm300/Notice123.htm)
- **Jan 2026 change:** Pirate Ship said most Ground Advantage shipments of 10–20 lb got cheaper by up to 26%, while shipments under 1 lb rose about 4%. — [Pirate Ship: 2026 USPS rate changes](https://support.pirateship.com/en/articles/13216719-2026-usps-rate-changes) (via search snippet)
- **Apr 26, 2026:** USPS applied a temporary 8% increase to retail and commercial base prices (Priority Mail Express, Priority Mail, Ground Advantage, Parcel Select), described as a "time-limited transportation adjustment" that is "scheduled to expire at midnight Central on January 17, 2027." — [ship.com, USPS rate changes July 2026](https://www.ship.com/post/usps-rate-changes-july-2026) (secondary, cites USPS Newsroom)
- **July 12, 2026 changes:**
  - The DIM divisor fell from 166 to 139.
  - Fractional inches now round up.
  - The maximum cubic length rose from 18 to 22 in.
  - Ground Advantage Cubic softpack tiers went from 10 to 5.
  - Signature Confirmation rose from $3.95 to $4.15.
  - Pirate Ship says commercial ounce-based pricing was eliminated for non-contiguous destinations and certain rural ZIPs (charged the 15.99 oz rate), while "most contiguous shipments use below-Commercial rates, which keep ounce-based pricing."
  — [Pirate Ship: July 2026 USPS rate and rule changes](https://support.pirateship.com/en/articles/15453569-july-2026-usps-rate-and-rule-changes); USPS filing: [USPS release, May 11, 2026](https://about.usps.com/newsroom/national-releases/2026/0511-usps-recommends-competitive-price-changes-for-july-2026.pdf)
- TransImpact projected the July 2026 changes would raise Ground Advantage commercial rates by an average of 11.8%, with lightweight and oversized parcels hit hardest. — [TransImpact](https://transimpact.com/blog/usps-rate-to-increase-ground-advantage-commercial-rates-by-11.8) (VENDOR CLAIM / analysis)
- An earlier 2026 data point: ship.com listed 1 lb zone 5 Ground Advantage at $10.95 retail and $8.74 commercial (Notice 123 effective Apr 26, 2026), and UPS Ground Saver list at $15.31 for the same parcel. — [ship.com, UPS Ground Saver vs USPS Ground Advantage](https://www.ship.com/post/ups-ground-saver-vs-usps-ground-advantage)
- **UPS 2026 GRI:** 5.9% average, effective Dec 22, 2025. — [TransImpact](https://transimpact.com/blog/ups-announces-2026-gri-at-5.9-but-your-real-costs-will-be-higher); [LateShipment](https://www.lateshipment.com/blog/ups-rates/)
- **UPS fuel surcharges in 2026:**
  - Ground was about 21.5% in the week of Mar 2 and 25.5% by Mar 16, 2026 (tied to Hormuz and diesel). — [Supply Chain Dive](https://www.supplychaindive.com/news/ups-fuel-surcharge-table-increase-2026/814187/)
  - A report put it at 27% as of Apr 6, 2026. — [blackamericaweb](https://blackamericaweb.com/2026/04/08/amazon-ups-usps-fuel-surcharges-donald-trump-iran-war-details/) (low-quality source)
  - Eightx listed a UPS air/ground surcharge of 32.0% for the week of Jul 14, 2026 (mixed air/ground figure). — [eightx](https://eightx.co/blog/strait-hormuz-conflict-shipping-supply-chain-cost)
  - The official UPS fuel surcharge page returned "Access Denied" on 2026-10-19.
- At light weights, USPS generally beats UPS Ground, and UPS tends to win at about 6 lb and up. — [ParcelPath](https://parcelpath.com/shipping-terms-glossary/is-ups-or-usps-cheaper/) (secondary)

### Inferences
- **10x10x8 box, USPS:** 800 cu in is below the 1,728 cu in threshold, so USPS bills actual weight (2–3 lb packed). Ground Advantage commercial for the fountain would run about $8.48–$9.06 (Z2), $10.50–$12.12 (Z5), or $13.42–$16.30 (Z8). A blended average across zones of roughly $11–12 per fountain order is reasonable before platform discounts.
- **10x10x8 box, UPS:** UPS applies dim weight to all package sizes. ASSUMPTION, not verified this session: UPS daily-rate divisor 139. At 139, dim weight is 800/139 = 5.76, which rounds up to 6 lb billable, so UPS Ground is likely uncompetitive for this box unless negotiated.
- **Filters (0.3–0.5 lb, poly mailer):** For contiguous US addresses, Pirate Ship and Shopify Shipping keep ounce tiers, so 8 oz will likely price below the $7.34–$8.95 commercial flat. Use the commercial table as a conservative ceiling.
- The 8% surcharge is set to expire Jan 17, 2027. Model a scenario where rates drop about 7.4% (1/1.08) after that date, but assume a January 2027 GRI could offset it.

### Gaps
- Exact Pirate Ship and Shopify Shipping (below-commercial) cell prices for 0.5/1/2/3 lb at Z2/5/8 were not retrievable without the live calculator.
- No UPS Ground published-rate cells for 1–3 lb, and no official current UPS fuel surcharge % (the page was blocked). ASSUMPTION for the model: UPS ground fuel surcharge of 25–30% on top of base, flagged as high-volatility.
- The UPS dim divisor (139) was not verified from a 2026 UPS source.
- Whether USPS will announce a January 2027 price change was not found.

---

## Q2. 3PL fees 2025–2026 (receiving, storage, pick/pack, packaging, minimums, onboarding)

### Takeaway
Few large 3PLs (ShipBob, ShipMonk, Red Stag, Fulfillrite) publish full rate cards. 2026 benchmarks are:
- First-item pick of about $2–$3.20 and additional item about $0.40–$0.50.
- Pallet storage about $18–25/month and bin storage about $3/month.
- Monthly minimums averaging about $517.
- Setup about $250–1,000.

Simpl Fulfillment publishes an all-in "from $7/order including postage" card with a $750/month minimum.

### Cited Findings
**Benchmarks:** [Fulfill.com 3PL pricing, page dated Jun 10, 2026, methodology updated Sep 2026](https://fulfill.com/3pl-pricing). Data comes from The Fulfillment Advisor 2025 survey (600+ warehouses) plus provider pages fetched June 2026.

| Fee | 2026 typical | Survey avg (2025) |
|---|---|---|
| Receiving per pallet | $5–$15 | $10.52 |
| Receiving per hour | $30–$60 | $39.88 |
| Container unload | $250–$600 | $500 |
| Storage per pallet/month | $15–$40 (most $18–$25) | $20.17 |
| Storage per bin/month | $1–$5 | $3.08 |
| Storage per cubic foot/month | $0.45–$0.55 | $0.46 |
| B2C first item | $2–$3 (published cards $0.99–$2.00) | $3.20 |
| Additional item | $0.30–$0.75 | $0.48 |
| Monthly minimum | $0–$750 | $517 (vs $337.50 in 2024) |
| Setup | $250–$1,000+ (51% charge it) | $333–$425 |
| Integration | $0–$500 | $275 |
| Returns | $1–$7 | $4.06 |
| Account management (35% charge it) | $30–$1,000+/month | $102.88 |

- Fulfill.com's analysis of 25+ real cards found a median first-item rate of about $2.00 and an additional item of about $0.40. — [Fulfill.com](https://fulfill.com/3pl-pricing)
- 48.6% of warehouses now charge long-term storage surcharges, up from 23.3%. — [Fulfill.com](https://fulfill.com/3pl-pricing)
- Eightx put the average across six published guides at $2.75 first item and $0.50 per additional item. It said invoices run 20–50% above the quoted rate once receiving, storage, returns, packaging, minimums and surcharges are added. — [eightx 3PL all-in cost per order](https://eightx.co/blog/3pl-all-in-cost-per-order) (consultancy)
- **Simpl Fulfillment published card** (page dateModified 2026-07-27) — [simplfulfillment.com/pricing](https://www.simplfulfillment.com/pricing):
  - "From $7/order", weight-based, including up to 3 picks, standard packaging, and postage.
  - Receiving is free.
  - Storage: small bin $3, large bin $5, shelf $15, pallet $40 per month (from JSON-LD).
  - $750/month minimum.
  - $0 setup.
  - 3-month auto-renew term with 60-day notice.
  - Carrier surcharges passed through.
- **ShipBob** has no public card. Third-party reported figures (VENDOR CLAIM / third-party): bins $5/month, shelves $10/month, pallets $40/month, $275 minimum for fulfillment, receiving about $25–35/hour, pick/pack about $2.50–3.50/order with first 4 items included, onboarding about $500–1,000, returns $3. Eightx says 2026 quotes include 3–5% Q4 storage surcharges and a 3% dashboard fee on some accounts. — [costbench ShipBob](https://costbench.com/software/shipping-software/shipbob/); [attnagency](https://www.attnagency.com/blog/shipbob-shopify-review); [eightx ShipBob/ShipMonk](https://eightx.co/blog/shipbob-shipmonk-regional-3pl-cost)
- **ShipMonk** publishes no dollar rates. Its minimum is "monthly order volume by your first item pick fee and then reducing it by 20%." Custom packaging is billed as an additional pick. — [shipmonk.com/pricing](https://www.shipmonk.com/pricing). Third-party sources list storage at $25/pallet/month and $1–4/bin/month, starting at $2.50/order. — [fitsmallbusiness](https://fitsmallbusiness.com/shipbob-competitors/); [costbench ShipMonk](https://costbench.com/software/shipping-software/shipmonk/)
- **Red Stag** is listed at about $3.25/order starting, recommended for 200+ orders/month, and positioned for heavy or high-value goods. No storage figures were found. — [ecommerce-platforms.com](https://ecommerce-platforms.com/fulfillment/best-fulfillment-center-for-small-business)
- **Fulfillrite** has a $399/month pick-and-pack minimum (about 140 orders), monthly storage by space used, and custom quotes. — [Fulfill.com Fulfillrite profile](https://www.fulfill.com/3pl-bio-collection/fulfillrite); [Fulfillrite FAQ](https://fulfillrite.com/faqs/)
- **Other no-minimum published cards:** HermesLines has no minimum, $10/pallet receiving, $13.01–15.99/pallet/month storage, and returns of $0.99–6.95. Fulfillment San Diego has no minimum, $15/pallet receiving, $4/bin, and pallets at $29 then $49. — [Fulfill.com](https://fulfill.com/3pl-pricing)

### Inferences
- **Stage B volumes:** 500–1,000 fountains at about 0.4–0.5 cu ft/carton is roughly 2–4 pallets. 1,000–5,000 filter 6-packs is about 1–2 pallets. Storage would run roughly $60–$240/month at $20–40/pallet.
- **Per-order pick/pack for the model:**
  - Base: $3.00 first item plus $0.50 per additional item, plus $0.50–1.00 packaging (ASSUMPTION; no packaging price data found).
  - Conservative all-in fulfillment excluding postage: about $4.00–$4.50/order. Add 20–50% contingency per Eightx.
- At low early volume, the minimum fee (about $400–750) will dominate the per-order cost. Model 3PL cost as max(minimum, volume × rate).

### Gaps
- No public 2026 rate cards were found for Flowspace, Ware2Go, ShipHero, or Rush Order (not searched individually due to tool-call limits). Red Stag's storage rates and ShipBob's official card are also unavailable.
- Packaging-material pass-through prices (boxes, mailers) were not found. ASSUMPTION: $0.35–$0.75 per poly mailer or box, and $1.00–$1.50 for the 10x10x8 corrugated box if the 3PL supplies it.

---

## Q3. China→US freight 2026: LCL, air, express samples, customs broker/ISF/MPF/HMF/bond

### Takeaway
Container spot rates in mid-October 2026 are near their 2026 highs:
- Drewry WCI Shanghai–LA was $7,884/FEU and Shanghai–NY $10,075/FEU (Oct 15, 2026).
- The Freightos Air Index for China–North America was about $6.30/kg (early Sep 2026).

LCL quotes from forwarders range widely, about $40–$165/CBM before destination charges. CBP fees for FY2026 are fixed: MPF 0.3464% (min $33.58, max $651.50) and HMF 0.125% on ocean shipments.

### Cited Findings
- **Drewry WCI, Oct 15, 2026:** composite $4,485/40ft (+3%), Shanghai–Los Angeles $7,884/40ft (+3%), Shanghai–New York $10,075/40ft (−1%). Drewry "expects rates to remain less volatile next week" on the transpacific. — [Drewry WCI](https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry)
- **Xeneta, Oct 1, 2026:** Far East–US West Coast spot was $8,346/FEU (+1.4% week on week). Xeneta's Peter Sand said rates "appear to have reached their post-Hormuz crisis peak for 2026." **Freightos, Sep 30, 2026:** Asia–USWC was about $8,400/FEU, a 2026 high. FBX01 was $7,666 in July 2026. — via search summary; the original article was not opened. Sources surfaced: [FreightWaves](https://www.freightwaves.com/news/chartofweek-2-ktce3), [Tradlinx](https://blogs.tradlinx.com/asia-us-freight-rates-near-a-peak-as-blank-sailings-increase/), [Baltic Exchange wk 28](https://www.balticexchange.com/en/data-services/WeeklyRoundup/Container/News/2026/container-report-week-28.html). Treat these as secondary.
- **Air:** The Freightos Air Index for China–North America was USD 6.30/kg for the week of Sep 8, 2026, airport to airport, with origin and destination charges extra. — [DocShipper China](https://china.docshipper.com/en/?p=30165) (secondary, citing Freightos). Sino-Shipping lists air at 100+ kg at $6.91/kg for Sep 2026 (+5% vs Aug). — [Sino-Shipping](https://www.sino-shipping.com/country-guides/shipping-from-china-to-usa/) (VENDOR CLAIM)
- **LCL China→US West Coast, 2026 (all VENDOR CLAIMS from forwarders):**
  - Epic Sourcing: $45–80/CBM (1–2 CBM minimum), with destination charges of about $700–1,500 per shipment on top. — [Epic Sourcing](https://www.epicsourcing.co/post/sea-freight-from-china-to-usa-costs-transit-times-2026)
  - ExFreight: $40–80/CBM, with FCL break-even around 15 CBM. — [ExFreight](https://www.exfreight.com/?p=19478)
  - Suaid Global: $85–165/CBM plus a 15–25% peak surcharge. — [Suaid](https://suaidglobal.com/insights/lcl-cost-per-cbm/)
  - Suaid calculator: Shanghai–LA $55–90/CBM all-in, CFS about $15/CBM, 18–24 days transit. — [Suaid calculator](https://suaidglobal.com/tools/lcl-rate-calculator/)
  - Sino-Shipping (Danish): $40–60/CBM, rising 20–40% in Aug–Oct peak. — [Sino-Shipping DA](https://www.sino-shipping.com/da/soefragt-fra-kina/omkostninger/lcl-pricing-breakdown-from-china/)
- **Express samples (DHL/FedEx/UPS):** about $5–10/kg, 1–5 day transit (ExFreight); about $6–10/kg for light parcels (NewBuyingAgent). Fuel and peak surcharges are extra. No verified 2026 DHL 2 kg quote was found. — [ExFreight](https://www.exfreight.com/?p=19478); [NewBuyingAgent](https://www.newbuyingagent.com/ja/resources/shipping-from-china-to-the-us-in-2026-the-definitive-guide-to-maximizing-efficiency-profit)
- **MPF FY2026** (effective Oct 1, 2025, CBP Dec. 25-10):
  - 0.3464% ad valorem, with a minimum of $33.58 and a maximum of $651.50 per formal entry.
  - The base excludes duty and freight, so Section 301 tariffs do not raise MPF.
  - Informal entry: $2.69 automated, $8.06 manual, $12.09 CBP-prepared.
  — [GHY International](https://www.ghy.com/trade-compliance/cbp-customs-user-fees-fy-2026/); [GingerControl MPF guide](https://gingercontrol.com/blog/merchandise-processing-fee-guide)
- **FY2027 MPF:** CBP normally adjusts these fees on Oct 1, so FY2027 values (effective Oct 1, 2026) may now apply. They were not found in this session. Note as a gap.
- **HMF:** 0.125% of value, ocean shipments only. — [Strix](https://strixsmart.com/resources/blog/customs-broker-cost); [GingerControl](https://gingercontrol.com/blog/customs-fees-explained)
- **Broker entry fee:**
  - $100–250 per standard entry (Strix) or $150–350 (GingerControl), with informal entries at about $50–150.
  - Clearit (a broker) lists $129.95 air brokerage plus a 5% disbursement fee on duties and fees.
  — [Strix](https://strixsmart.com/resources/blog/customs-broker-cost); [GingerControl](https://gingercontrol.com/blog/customs-fees-explained); [Clearit pricing, 2026-04-24](https://clearitusa.com/customs-clearance-pricing-rates/) (VENDOR CLAIMS)
- **ISF filing:** about $30–75 per filing, with a $5,000 late-filing penalty. — [Strix](https://strixsmart.com/resources/blog/customs-broker-cost); [Suaid broker fees 2026](https://suaidglobal.com/insights/customs-broker-fees-2026/)
- **Bonds:**
  - Continuous bond: about $300–500/year per Strix, $500/year per Clearit, $250–750 for a $50k bond per another source.
  - Single-entry bond (Clearit): $5 per $1,000 of value, $40 minimum, plus a $35 prep fee.
  - A continuous bond becomes cheaper at about 3+ imports per year.
  — [Clearit](https://clearitusa.com/customs-clearance-pricing-rates/); [Strix](https://strixsmart.com/resources/guides/customs-bonds); [beancount.io, Sep 13, 2026](https://beancount.io/blog/2026/09/13/customs-bonds-new-importers-single-entry-vs-continuous-bond-sufficiency-guide)

### Inferences
- **Fountain shipment volume:** Assume about 0.4–0.5 cu ft per master carton unit. ASSUMPTION: about 0.012–0.015 CBM per retail-boxed fountain (10x10x8 in = 0.0131 m³). So 500 units is about 6.6 CBM and 1,000 units is about 13 CBM, near the 15 CBM FCL break-even.
- **LCL cost at $60–120/CBM:** about $400–800 ocean (500 units) or $800–1,600 (1,000 units), plus $700–1,500 destination charges. Per-unit freight comes to roughly $2.20–$4.60 for 500 units. ASSUMPTION for the planning base: $3.50/fountain landed freight (sea, LCL), or $5.00 conservative during the 2026 peak.
- **Air (1,000 filter 6-packs at about 0.2 kg each):** about 200 kg chargeable × $6.30–7/kg is about $1,260–1,400 airport to airport, or about $1.30–$1.40 per pack before destination charges.
- **Per-entry fixed fees:** broker $150 + ISF $50 + MPF min $33.58 + single bond about $75. That is roughly $300–350 fixed per ocean entry before HMF. Use a $500 continuous bond if planning 3+ entries per year.

### Gaps
- No direct October 2026 Freightos FBX or Air Index readings from Freightos itself (its weekly-update URL returned 404).
- No direct Xeneta article was fetched.
- The FY2027 MPF min/max (effective Oct 1, 2026) was not found. The FY2026 values may already be superseded.
- No verified DHL/FedEx 2026 China→US 2 kg tariff.

---

## Q4. Duty treatment (HTS + Section 301 + forced-labor 301) and de minimis / AliExpress postal handling

### Takeaway
Pet fountains are classified under HTS 8413.70.2004, MFN free, and are on Section 301 List 1 (9903.88.01, 25%). Since Jul 24, 2026, the 12.5% Section 301 forced-labor duty stacks on top, for an indicative 37.5% total (excluding Section 232 if applicable). Espresso tampers (8205.51.30) and naked portafilters (8516.90.90) carry List 3 (9903.88.03, 25%) per CBP ruling N335954, plus 12.5% forced-labor. De minimis remains suspended for all countries, upheld by the CIT on Aug 13, 2026. No official AliExpress statement on US duty collection at checkout was found.

### Cited Findings
- **Pet fountains:** CBP rulings N303286 and N303288 (2019) classify pet fountains under 8413.70.2004 (pump gives the essential character), free general rate, with companion code 9903.88.01 (List 1, 25%). — [N303286](https://www.tarifflens.ai/rulings/N303286); [N303288](https://open-gov.usebase.io/rulings/N303288); [N303287 Bloom Pet Fountain](https://www.tarifflens.ai/rulings/N303287)
- An older 2008 CBP ruling (Drinkwell) used 8413.81.0040, and a 2025 UK ruling used 8413810090. These show some classification variance. — [N025473](https://www.tarifflens.ai/rulings/N025473) (via search summary)
- List 1 exclusions for 8413.70.2004 existed in 2019–2020 (oil/gas submersible pumps; pumps ≤15 kW). They were extended only to Dec 30, 2020 and do not appear to be current. — [Livingston](https://www.livingstonintl.com/16-of-89-exclusions-extended-for-china-section-301-list-1-products/); [Mohawk Global](https://mohawkglobal.com/global-news/certain-product-exclusions-extended-from-list-1-others-to-expire-june-4/)
- **Forced-labor Section 301:**
  - Effective Jul 24, 2026, covering 60 economies.
  - "12.5% (all others)." China is not in the reduced tiers. It applies "on top of existing Section 301 tariffs for China."
  - Section 232 goods and 471 HTSUS subheadings (mostly raw materials) are excluded.
  - In-transit relief applied for vessels loaded before Jul 24 and entered by Jul 28.
  — [C.H. Robinson, Jul 29, 2026](https://www.chrobinson.com/en-us/resources/blog/section-301-forced-labor-tariffs/); [PwC](https://www.pwc.com/us/en/tax-services/publications/insights/assets/pwc-ustr-imposes-sec-301-tariffs-following-forced-labor-investigations.pdf)
- **China stack per Ecommerce Fastlane/Portless (Jul 29, 2026), assuming 0% MFN:** Lists 1–3 at 25% + 12.5% = 37.5% from Jul 24; List 4A at 7.5% + 12.5% = 20.0%; goods on no list at 12.5%. The IEEPA tariffs were struck down Feb 20, 2026. The 10% Section 122 surcharge ran Feb 24 to Jul 24, 2026 (Proclamation 11012). — [Ecommerce Fastlane](https://ecommercefastlane.com/section-301-tariffs-what-changed-for-china-in-2026/)
- **Tamper and portafilter:** CBP ruling N335954 (Nov 6, 2023, Breville) covers calibrated tamper 8205.51.3030 and naked portafilter 8516.90.9000, with 9903.88.03 (List 3). — [N335954](https://www.tarifflens.ai/rulings/N335954)
- **Filters:**
  - No pet-fountain-filter ruling was found.
  - The closest precedent is a 1990 CBP revocation treating aquarium filter cartridges (polyester pouch with carbon and zeolite) as 8421.99.00 parts. — [HQ 086936](https://www.tarifflens.ai/rulings/086936)
  - Because the fountain itself is 8413, parts-of-pump classification (8413.91) is also arguable.
- **Litter mat:**
  - No litter-mat ruling was found.
  - A 1998 "Meow Mat" (cotton with catnip) was classified 6307.90.9989 at 7%.
  - A felt door mat was classified under 5704.
  - A plastic litter scoop was classified 3924.90.5000.
  — [C81682 via tarifflens](https://www.tarifflens.ai/rulings/C81682); [N021518 door mats](https://www.tarifflens.ai/rulings/N021518)
- **De minimis:**
  - The Supreme Court IEEPA ruling (Learning Resources v. Trump, Feb 20, 2026) did not address the de minimis suspension. EO 14388/14389 kept the suspension.
  - A Federal Register rule (Jun 24, 2026) made the suspension for mail shipments indefinite and created a new postal informal entry. — [Federal Register 2026-12669](https://www.federalregister.gov/documents/2026/06/24/2026-12669/indefinite-suspension-of-the-de-minimis-exemption-for-mail-shipments-and-new-postal-informal-entry) (page blocked; title and date only)
  - On Aug 13, 2026, the CIT reportedly upheld the president's authority to suspend de minimis (Detroit Axle). — [EcomCrew](https://www.ecomcrew.com/?p=67521) (secondary)
  - ST&R summary (Feb 25, 2026): commercial de minimis has been suspended for all countries since Aug 29, 2025, and former de minimis shipments must be filed as an appropriate entry type in ACE. — [ST&R](https://www.strtrade.com/trade-news-resources/str-trade-report/trade-report/february/de-minimis-suspension-remains-in-place); [Thomson Reuters](https://www.thomsonreuters.com/en-us/help/onesource-global-trade/regulatory-insights/2026/february-25th/de-min-suspension-means-global-trade-prof)
  - Statutory repeal of de minimis takes effect July 2027. — [Supply Chain Dive, Feb 23, 2026](https://www.supplychaindive.com/news/de-minimis-status-supreme-court-trump/812785/)
- **Postal duty:** In Feb 2026, postal duty was set at 10%, matching the Section 122 rate, with carriers or qualified parties collecting and remitting. It was to last until the surcharge expired or CBP's new postal entry process took effect. The prior IEEPA-era $80–200 per-item option was superseded. — [Supply Chain Dive, Feb 23, 2026](https://www.supplychaindive.com/news/de-minimis-status-supreme-court-trump/812785/)
- **AliExpress:**
  - No official statement was found.
  - Third-party guides say some sellers show "incl. import charges" at checkout while others leave duty to be billed on delivery, so collection is inconsistent. — [Fulfillbot](https://fulfillbot.com/?p=1000518); [Tariffstool](https://www.tariffstool.com/import-tax/aliexpress) (secondary)
  - Claims about Choice routing through Cainiao bonded warehouses are unverified. — [Yakkyofy](https://yakkyofy.com/aliexpress-import-tax-what-to-do/)

### Inferences
- **Fountain landed duty (Stage B):** 0% MFN + 25% List 1 + 12.5% forced-labor = 37.5% of FOB/entered value, plus MPF/HMF. Example: a $12 FOB fountain pays about $4.50 duty.
- **Section 232 risk:** If CBP treats a stainless fountain as a steel derivative under Section 232, the 301 forced-labor duty would not apply but 232 would. Not verified. Flag for broker review.
- **Tamper:** 8205.51.30 MFN (ASSUMPTION; MFN not verified this session) + 25% List 3 + 12.5%. **Portafilter:** 8516.90.90 + 25% List 3 + 12.5%. So about 37.5% plus MFN for both.
- **Filters:** If 8421.21 or 8421.99, the List 3 25% status is likely (List 3 covered most of Chapter 84) but NOT verified. Planning ASSUMPTION: 37.5% total.
- **Litter mat:** Possibly 3926 (plastic/EVA/PVC) or 5705/6307 (textile). List status is not verified. Conservative ASSUMPTION: 25% + 12.5% + MFN of about 5% = ~42.5%. Lower if on List 4A (about 20% + MFN).
- **Stage A (AliExpress/AutoDS):** Because collection is inconsistent, model a duty or price-uplift of 25–40% of item value for China-origin goods. ASSUMPTION: assume the supplier price already embeds or passes through about 30% duty, and budget a 5% risk of carrier "duty due on delivery" refusals or re-ships.

### Gaps
- The current postal duty basis after the Section 122 expiry (Jul 24, 2026) was not found. It may now track Section 301 rates under the Jun 24, 2026 postal informal entry rule.
- No official AliExpress US checkout duty policy was found.
- No CBP ruling exists for pet fountain filter cartridges or litter mats.
- MFN rates for 8205.51.30, 8516.90.90, 8421.x and 3926/5705 were not verified this session.
- The Chapter 99 code for the forced-labor duty was not found (reportedly unpublished as of late July 2026).

---

## Q5. Compliance and testing costs

### Takeaway
Public prices are sparse and mostly from vendors:
- FCC Part 15B SDoC for a basic unintentional radiator: about $3,000–5,000 (US lab).
- Prop 65 lead/cadmium/phthalate panel example: about $445 per product.
- LFGB/FDA food-contact testing: about $300–1,800 per material or variant.
- General liability for pet-product businesses: about $22–43/month.

No source quantified the UL-listed adapter premium.

### Cited Findings
- **FCC Part 15B:** Compliance Testing (US lab) lists $3,000–$5,000 for "basic electronic devices with no transmitters" (unintentional radiators). Most Part 15B products use SDoC rather than certification. — [Compliance Testing, FCC certification cost](https://compliancetesting.com/fcc-certification-faqs/fcc-certification-cost/) (VENDOR CLAIM); [Compliance Gate SDoC guide](https://compliancegate.com/fcc-sdoc)
- **Prop 65 sample quote** (ComplianceGate, updated Mar 7, 2023, older): cadmium surface $20 and substrate $40, lead surface $20 and substrate $55, phthalates (6P) $310, total $445. Costs rise with the number of materials. — [ComplianceGate Prop 65 lab testing](https://www.compliancegate.com/california-proposition-65-product-lab-testing/) (dated 2023)
- **XRF screening** was anecdotally about $5 per sample component (Etsy seller). — [Etsy community](https://community.etsy.com/t5/Keeping-Up-With-CPSIA/What-might-help-A-LOT/m-p/20921484/highlight/true) (anecdote, undated)
- **Food contact** (Alibaba seller blogs, 2026, conflicting VENDOR CLAIMS):
  - LFGB: $450–650 per material type, or $300–800 per stainless variant.
  - Stainless cutlery: FDA $600–1,000 and LFGB $1,200–1,800.
  - FDA testing: $200–400 per variant.
  - LFGB sensory testing adds $200–500 per SKU.
  — [Alibaba seller blog, FDA vs LFGB metal](https://seller.alibaba.com/blogs/2026/southeast-asia/metal-processing/fda-lfgb-certification-guide-alibaba-exporters); [Alibaba LFGB stainless](https://seller.alibaba.com/blogs/2026/southeast-asia/kitchenware/lfgb-certification-guide-alibaba-b2b); [Alibaba tableware](https://seller.alibaba.com/blogs/2026/southeast-asia/tableware/tableware-safety-certification-fda-lfgb-ce-sgs-guide-alibaba)
- **UL-listed adapters, retail examples only:**
  - Adafruit 5V 1A UL-listed USB supply about $7.85 each, $6.55 at volume (Jameco). — [Jameco](https://www.jameco.com/z/501-Adafruit-Industries-5V-1A-1000Ma-USB-Port-Power-Supply-UL-Listed_2501735.html)
  - XP Power 5V 2.1A UL 62368-1 listed, LPS: about $10.98 for 1 unit, $9.23 at 100. — [TRC Electronics](https://www.trcelectronics.com/products/xp-power-veu10us050-us)
  - No same-spec non-listed comparison was found.
- **Insurance:**
  - Next Insurance: 63% of pet-store customers pay $22–30/month for general liability ($500k–$1M per occurrence). — [Next pet store insurance cost](https://nextinsurance.com/business/pet-store-insurance/cost)
  - Insureon: pet care businesses average $43/month ($513/year) for $1M/$2M GL. BOP for pet shops averages about $174/month. — [Insureon pet care cost](https://www.insureon.com/pet-care-business-insurance/cost)
  - These figures are for pet services and stores, not product sellers specifically.

### Inferences
- **Stage B fountain compliance budget** (ASSUMPTION built from the above):
  - FCC 15B SDoC on the pump/controller: $1,500–5,000. Chinese labs are often cheaper, but no source was found.
  - Prop 65 panel: about $450–900 (2–3 materials).
  - Food-contact on the stainless bowl and plastic: $600–1,500.
  - Total about $3,000–7,500 one-time, before any NRTL listing.
- **Adapter:** A UL/ETL-listed Class 2/LPS adapter at volume likely costs about $1.50–3.00 more per unit than an unlisted one. ASSUMPTION: no source. The only data points are listed retail prices of $6.55–$10.98.
- **Product liability insurance:** Product sellers importing electrical items typically pay more than service businesses. ASSUMPTION: $50–150/month for a GL plus product liability policy with $1M/$2M limits at under $250k revenue. Get Next, Hiscox, or Thimble quotes.

### Gaps
- No China-lab FCC price, no Hiscox or Thimble product-seller premiums, no UL listing cost for a custom adapter, and no 2025–26 Prop 65 lab price list.

---

## Q6. Samples, molds, custom packaging

### Takeaway
Simple injection molds are quoted at about $1,000–15,000 depending on aluminum vs steel and complexity (Alibaba seller blogs, conflicting). Custom samples requiring tooling run about $300–2,000+. Packlane printed mailers are about $0.93/unit at 500 for a small box (older review). Larger 10x8x4 custom mailers run about $1.50–1.80/unit at 500 (estimator).

### Cited Findings
- **Molds (Alibaba seller blogs, 2026, VENDOR CLAIMS):**
  - Simple molds $5,000–15,000, complex $50,000+. — [Alibaba OEM/ODM sample guide](https://seller.alibaba.com/blogs/2026/southeast-asia/gifts-crafts/oem-odm-free-sample-evaluation-guide-alibaba-b2b)
  - Simple $3,000–5,000, complex $20,000–50,000+. — [Alibaba high-volume injection molding](https://seller.alibaba.com/blogs/2026/southeast-asia/plastics-manufacturing/injection-molding-high-volume-guide-alibaba-b2b)
  - Single-cavity aluminum prototype molds $1,000–5,000 for 100–500 units. — [Alibaba OEM/ODM sourcing guide](https://seller.alibaba.com/blogs/2026/southeast-asia/plastics-rubber/private-label-oem-odm-sourcing-guide-alibaba)
- **Custom samples requiring new tooling:** $300–2,000+, 15–30 days. — [Epic Sourcing 2026 sample cost guide](https://www.epicsourcing.co/post/how-much-do-product-samples-cost-sourcing-from-china-usa-2026) (sourcing agent)
- **Packlane:**
  - 4x4x2 mailer, matte white, satin print: $0.93/unit at 500 and $0.76 at 2,000. — [ecommerce-platforms Packlane review](https://ecommerce-platforms.com/packaging/packlane-review) (undated review)
  - Packlane's bulk pricing starts at 2,000+ units, and the self-serve tool handles smaller runs. — [Packlane bulk mailer boxes](https://packlane.com/bulk-mailer-boxes)
  - A generic estimator gives about $1.50–1.80/unit at 500 for a 10x8x4 mailer. — [Packwire estimator](https://packwire.com/packaging-cost-estimator) (via search summary)

### Inferences
- **Custom filter shape:** If the brand uses the supplier's existing filter tooling, the mold cost is $0. A custom filter frame would need an aluminum prototype mold (about $1,000–5,000) or a steel production mold (about $3,000–15,000). ASSUMPTION base: $4,000, amortized over the first 5,000 filter packs.
- **Fountain retail box (10x10x8, printed) at 500–1,000 units:**
  - From a Chinese supplier bundled with the product: ASSUMPTION $0.60–1.20/unit.
  - From a US print-on-demand supplier like Packlane: ASSUMPTION $2.50–4.00/unit (no direct quote retrieved).
  - Inserts: ASSUMPTION $0.10–0.30/unit.
- **Samples:** ASSUMPTION of 3 suppliers × (sample $30–80 + express $40–80) is about $250–500 for off-the-shelf samples, plus $300–2,000 for a customized golden sample.

### Gaps
- No Arka quote and no live Packlane quote for a 10x10x8 box.
- No Alibaba printed-box price for 500–1,000 units.
- No sourced typical Alibaba sample fee for off-the-shelf fountains.

---

## Q7. Platform and tool stack (monthly)

### Takeaway
A lean stack costs roughly $100–200/month at launch:
- Shopify Basic: $39/month ($29 annual).
- AutoDS: about $20–50/month (annual-billed tiers) plus a $9.90 auto-order add-on.
- Klaviyo: $20–30 at 500–1,000 profiles.
- Judge.me Awesome: $15.
- Seal Subscriptions: $0–25.

Payments cost 2.9% + $0.30 on Basic (2.7% + $0.30 on Grow), and chargebacks cost about $15 each.

### Cited Findings
- **Shopify plans:** Basic $39/month monthly or $29 annual. Grow $105 monthly or $79 annual. — [NerdWallet Shopify pricing 2026](https://www.nerdwallet.com/article/small-business/shopify-pricing)
- **Shopify Payments rates:**
  - Basic: 2.9% + 30¢ online.
  - Grow: 2.7% + 30¢ online.
  - +1.0% on international cards, 1.5% currency conversion.
  - Third-party gateway surcharge: 1.0% on Grow (secondary).
  — [NerdWallet](https://www.nerdwallet.com/article/small-business/shopify-pricing); [First Pier](https://www.firstpier.com/resources/how-much-does-shopify-cost)
- **Chargeback:** $15 per dispute on US Shopify Payments, refunded if the merchant wins. — [chargeback.io](https://www.chargeback.io/de/blog/whats-the-shopify-chargeback-fee) (VENDOR CLAIM; Shopify help center not retrieved). A lost dispute costs about 2–2.5× the order value all-in. — [Ringly](https://www.ringly.io/blog/shopify-chargeback-fees) (VENDOR CLAIM)
- **AutoDS:**
  - PricingSaaS (captured Jul 27, 2026; annual-billed monthly equivalents): Import $19.90, Starter $29.90, Advanced $49.90, Enterprise custom. — [PricingSaaS AutoDS](https://pricingsaas.com/companies/autods)
  - Add-ons: Auto Ordering $9.90, Product Finding Hub $14.97, VA Access $14.97, Mentor $39.97. — [PricingSaaS AutoDS](https://pricingsaas.com/companies/autods)
  - AutoDS's own page shows "Annual (25% off)" and a 3-day trial for $0.99/$1, but prices did not render. — [autods.com/pricing](https://www.autods.com/pricing/)
  - A Nifty guide lists Import at $26.90/month on Shopify (likely the monthly-billed price). — [Nifty AutoDS pricing](https://nifty.ai/post/autods-pricing)
- **AutoDS "5% wallet fee": NOT VERIFIED.**
  - A Shoplazza blog lists a 5% fee on each top-up of the "FBA-managed balance." — [Shoplazza PT](https://www.shoplazza.com/pt/blog/autods-dropshipping-alternatives) (May 26, 2026, third party)
  - User reviews mention "5% of your sales" on the automated route and 15% withheld on wallet refunds. — [AutoDS Shopify reviews](https://apps.shopify.com/reviews/1716648) (anecdotal)
  - No official AutoDS help-center source was found.
- **Klaviyo Email** (third-party, tiers conflict):
  - 250 profiles free; 500 profiles $20; 1,000 profiles $30.
  - 2,500 profiles: $60 (First Pier) vs $70 (SendX).
  - 5,000 profiles: $70 (SendX) vs $100 (First Pier).
  — [First Pier Klaviyo 2026](https://www.firstpier.com/resources/sms-klaviyo-pricing); [SendX Klaviyo 2026](https://www.sendx.io/blog/klaviyo-pricing-plans-costs-alternatives-2026)
- **Reviews:** Judge.me Awesome is $15/month flat (Forever Free tier available). Okendo is about $19/month entry, about $119 (Growth) and $299 (Power), with tier names inconsistent across sources. — [Joy.so comparison](https://joy.so/blog/judgeme-vs-okendo-vs-yotpo/); [costbench Judge.me](https://costbench.com/software/review-management/judge-me/)
- **Subscriptions:**
  - Seal: free tier, $5.95 (100 subscriptions), $9.95 (250), $24.95 (500), 0% transaction fee. — [CraftShift 2026](https://craftshift.com/best-shopify-subscription-apps-2026/); [Seal Shopify listing](https://apps.shopify.com/seal-subscriptions?locale=th)
  - Appstle: a free plan and a $10/month package mentioned in a Nov 2025 review; full tiers not found. — [Appstle reviews](https://apps.shopify.com/reviews/2100084)
- **UGC:**
  - Billo: from $99/video (15s $99, 30s $139, 60s $169), creator pay included, product and shipping extra. — [Billo pricing](https://billo.app/?p=54672)
  - Insense: Brand $500/month (quarterly), Trial $650/month, Agency $640–800. Marketplace fee of 20%/10%/7% on creator payments. — [PricingSaaS Insense](https://pricingsaas.com/companies/insense); [ToolRadar](https://toolradar.com/tools/insense/pricing)

### Inferences
- **Stage A monthly fixed costs:** Shopify Basic $39 + AutoDS Starter about $30–40 + auto-order $9.90 + Judge.me $15 + Klaviyo $20 (or $0 under 250 profiles) + Seal $0–10. Total is about $115–135/month before UGC and ads.
- **Stage B fixed costs:** Drop AutoDS (−$40–50). Klaviyo grows to $60–100 at 2,500–5,000 profiles. Add Grow ($79–105) only if the payment-rate saving exceeds the $50–66 premium, which happens at roughly $25–33k/month GMV (0.2% saving).
- **UGC:** ASSUMPTION of 4 Billo videos per month at about $120 average, or about $480/month, during the test phase.
- **AutoDS wallet fee:** Model as ASSUMPTION 0–5% of supplier cost, flagged unverified. Base case 0%, and run a sensitivity case at 5%.

### Gaps
- No official Shopify help-center chargeback fee and no official Klaviyo slider value.
- AutoDS official plan prices on the monthly-billing option and the wallet fee are unconfirmed.
- No Appstle tier list or Okendo official page.

---

## Q8. Returns and defects

### Takeaway
No US-specific return rate for pet fountains or small appliances was found:
- NRF expects about 16% overall US retail returns for 2025.
- A Swiss retailer reports pet supplies at about 1.2%.
- Electronics run about 8–10% (vendor blog).

Review analysis shows the dominant failure mode is the pump failing or clogging within months. Retail replacement pumps cost about $17.

### Cited Findings
- **NRF/Happy Returns 2025:** shoppers expected to return about 16% of purchases (about $850B). — [SupplyChain247](https://www.supplychain247.com/article/2025-retail-returns-hit-850-billion)
- **Galaxus (Switzerland, 2025):** pet supplies return rate 1.2% (ranked 13th). Within the category, cat flaps are at 5%, aquarium lighting 10%, and dog clothing 11%. — [Global Pet Industry](https://globalpetindustry.com/news/pet-supplies-among-least-returned-e-commerce-categories-in-switzerland/)
- Electronics category average return rate is 8–10%. — [Channelwill](https://www.channelwill.com/blogs/ecommerce-return-rates) (VENDOR blog)
- **Cat fountain review analysis (Amazon, 30 reviews):** "many customers reported issues with the pump breaking or the fountain stopping working after a few months." — [Kimola](https://kimola.com/reports/comprehensive-cat-water-fountain-feedback-analysis-amazon-en-us-143234)
- Replacement pump complaints include premature failure and low flow. — [Tractor Supply Drinkwell replacement pump](https://www.tractorsupply.com/tsc/product/drinkwell-platinum-replacement-pump-1339649)
- The Frisco replacement pump sells for $17.11 on Chewy. — [Chewy](https://www.chewy.com/frisco-pet-fountain-replacement-pump/dp/219881)
- Returns processing at 3PLs costs $1–7 per return (average $4.06). — [Fulfill.com](https://fulfill.com/3pl-pricing)

### Inferences
- **ASSUMPTION for the model:**
  - Fountain return/refund rate: 6% (base) to 10% (conservative).
  - Warranty defect re-ship rate: 3–5% within 90 days, since pump failure is the main complaint.
  - Filters: 1–2% (consumable, low-return category per Galaxus).
- **Cost per defect, cheapest path:** ship a replacement pump only, at a pump unit cost of about $1.50–3 (ASSUMPTION) plus a mailer at about $7.34–8.95 commercial postage. Total is about $10–12.
- **Cost per defect, full unit:** full fountain re-ship costs landed COGS + 3PL pick ($3–4) + postage ($10.50–13.40 Z5–Z8, 2 lb). Treat returned units as non-resaleable (ASSUMPTION).
- **Stage A (AliExpress):** Returns to China are uneconomic, so model 100% refund or reship with no recovery.

### Gaps
- No Amazon "frequently returned" badge data for pet fountains and no Marketplace Pulse data.
- No US small-appliance category return rate from an authoritative source.

---

## Q9. Dripshipper and alternatives (SHADOW case)

### Takeaway
Dripshipper plans are $30, $99, or $197 per month with no transaction fees, but its per-bag wholesale price is not public. One merchant cited about $14 landed per 12oz bag with shipping included. Roastify publishes a full card: $15 or $49 per month, $12.00 per member 12oz bag, and $4.50 dropship shipping for the first item ($1.25 each additional). Cerca starts at $20/month, and its per-bag cost was not found.

### Cited Findings
- **Dripshipper:** Starter $30/month, Professional $99/month, Elite $197/month, 14-day free trial. "No hidden fees. You only pay the plan price plus the wholesale cost of products." No setup or transaction fees. — [dripshipper.io/pricing](https://dripshipper.io/pricing) (fetched 2026-10-19). The Shopify listing also shows Starter annual at $240/year. — [Shopify App Store Dripshipper](https://apps.shopify.com/dripshipper)
- **Dripshipper per-bag cost:** A merchant review said a 12oz bag cost about $14 landed and needed a $19 price to make $5. The developer replied that "our coffees all come with free shipping." — [AppNavigator Dripshipper reviews](https://appnavigator.io/app/dripshipper/reviews/?page=6) (anecdotal, date unknown). Dripshipper ships within 3–5 business days from US facilities. — [Shopify App Store](https://apps.shopify.com/dripshipper)
- **Roastify** (fetched 2026-10-19) — [roastify.app/pricing](https://roastify.app/pricing):
  - Plans: Base $15/month, Pro $49/month.
  - Member 12oz bag $12.00; one-off 12oz box $18.00.
  - Dropship shipping: $4.50 first item, $1.25 each additional.
  - Wholesale case pricing: $16.99/unit (48) down to $9.99/unit (1,920).
  - No setup, design, or storage fees.
- **Cerca:** Starter $20/month, unlimited orders and products. Per-bag cost not found. — [PickYourApp Cerca](https://pickyourapp.com/de/products/cercacoffee)
- **General:** US private-label roasters charge about $9–12 per 12oz bag wholesale (dropship vendor blog, unverified). — [Easync](https://easync.io/articles/coffee-dropshipping/). Private-label or wholesale roasted coffee runs about $9–20+/lb. — [Bellwether Coffee](https://bellwethercoffee.com/blog/private-label-coffee-guide)

### Inferences
- **Shadow case COGS per 12oz bag delivered:**
  - Roastify Base: $12.00 + $4.50 = $16.50.
  - Dripshipper: about $14 including shipping (single anecdote).
  - Planning ASSUMPTION: $14–16.50 per bag delivered, plus $15–30/month platform fee.
- **Espresso kit + beans in one order:** They ship from different origins (3PL vs roaster), so there are two shipments and two postage charges per bundled order.

### Gaps
- No official Dripshipper per-bag or shipping price list (the catalog is likely behind a login).
- No Cerca per-bag price.

