# Paid Social Breaks Both Finalists' Unit Economics

*Checkpoint 4 of an investor-style e-commerce study, as of October 19, 2026. Model figures come from `models/Cat home financial model.xlsx` (11 sheets, 9,823 formulas, zero formula errors), read at the Base scenario and private-label stage unless stated. Labels used throughout: **FACT** = cited source; **MODEL** = workbook output; **ASSUMPTION** = analyst planning input tagged as such in the workbook; **ESTIMATE** = analyst arithmetic on cited or modeled inputs; **Inference** = judgment. Scores in Phase H are preliminary analyst judgments, not measurements.*

On the current inputs, **neither the cat-home base case nor the espresso Dedica shadow case is fundable on paid-social acquisition, and no repositioning tested fixes that**. The cat fountain earns **$5.00 per first order before ads and −$40.00 after a $45 CAC**, every 90-day filter renewal **loses $3.42**, and 12-month contribution LTV:CAC is **0.07x**. Six repositionings (a $79 "easy-clean" system, 12-filter six-month packs, a 35% affiliate/organic CAC cut, a non-China OEM, and all of them combined) leave the best cat variant at **−$13.83 per first order after CAC and 0.59x**. Espresso is materially better but also fails: at $99 the Dedica kit reaches **−$11.39 after CAC and 0.88x**. The cause is structural, not a tuning problem. A ~2 lb, $50 hardware hero shipped free carries **$15.60 of 3PL and postage and $8.54 of duty, freight and entry fees** before a dollar of advertising, while paid-social benchmarks put pet CPA near **$38.51** and pet ROAS near **1.6**, and the consumable that follows is cheap, slow and easy to substitute. Several inputs are conservative (commercial postage used as a ceiling, a new-store CPA penalty, full-unit warranty re-ships, certification amortized over only 1,000 units), but the model's optimistic scenario already reverses most of them and cat still fails its LTV:CAC gate at 1.16x. The evidence therefore favors **not committing launch capital to cat as configured**, and spending a few hundred to a few thousand dollars on tests that settle the two numbers that decide espresso: **a 51mm kit landed cost near the modeled $34.66 or below, and a blended CAC at or under about $26**. Confidence is high that cat at $49.99 on paid social fails; low-to-medium that espresso can be made to pass.

---

## 1. Executive answer: not fundable as configured, and the gap is acquisition cost

### The verdict and what would have to be true

Neither case meets an investor floor of first-order break-even after CAC, 12-month contribution LTV:CAC of at least 1.5x, and payback inside 9–12 months. Those thresholds are the model's own GoNoGo policy (ASSUMPTION, Inputs section N). They track operator norms of payback under 12 months on contribution margin, which are themselves low-confidence blog compilations ([eightx](https://eightx.co/blog/average-cac-payback-period-by-vertical)).

| Question | Cat home (base case) | Espresso Dedica 51mm (shadow) |
|---|---|---|
| First-order contribution before ads / after $45 CAC (MODEL) | $5.00 / **−$40.00** | $21.11 / **−$23.89** |
| Contribution per subscription renewal (MODEL) | **−$3.42** per 90-day 6-pack | **+$4.38** per monthly 2-bag shipment |
| 12-month LTV:CAC (MODEL) | **0.07x** | **0.60x** |
| Payback (MODEL) | None within 24 months | None within 24 months |
| GoNoGo at Base (MODEL) | NO-GO on 13 gates | NO-GO on 8 gates, CONDITIONAL on 1 |
| Best repositioned variant (MODEL) | R6, all levers: −$13.83 after CAC, 0.59x | R5, $99 kit: −$11.39 after CAC, 0.88x |
| CAC that would pass both targets in the best variant (MODEL) | **≤ $11.44** (R6) | **≤ $26.43** (R5) |
| Hero price that would pass both targets in the best variant (MODEL) | **≥ $110.13** (R6), above the $95.99 top of the observed design tier | **≥ $130.22** (R5) |
| Optimistic scenario (MODEL) | Still NO-GO on LTV:CAC (1.16x), the minimum-attach gates and cash | **GO on every gate** (kit $99.99, CPA $30, landed $20.93, Dripshipper beans) |

The "what would have to be true" list is short and specific. For cat at today's configuration, paid CPA would have to fall to **$3.62** (gate 1), or the fountain alone would have to sell at **$97.21** to break even on the first order (gate 14), and the filter pack would have to sell at **$21.99** to earn $3 per renewal at commercial postage (gate 9). For espresso, CPA would have to fall to **$26.24** for a nine-month payback (gate 1), or the kit would have to sell at **$112.53** to break even on the first order at a $45 CAC (gate 14). The espresso optimistic scenario shows the path in concrete terms: lower landed cost, cheaper beans and a $30 CAC together flip every gate. No benchmark in the evidence base supports a sub-$12 blended CAC for a new pet store. The espresso threshold of about $26 sits *above* the published TikTok medians for established brands ($17.07 all-category, $19.33 Home & Garden) but well below the model's own TikTok planning value of $45 ([Triple Whale TikTok](https://www.triplewhale.com/blog/tiktok-benchmarks); [Sovran](https://sovran.ai/benchmarks/tiktok-ads-benchmarks)). That gap is testable cheaply.

### Recommended path and confidence

The evidence favors three moves, in this order. First, **do not place the 500-unit fountain MOQ** or start certification spend for cat as configured. The model needs **$28,830** of cash before the first private-label sale on the lean tier, against a **$15,000** placeholder for cash available. Second, **adopt the 12-filter six-month pack** as the cat subscription format if cat continues in any form. It is the one structural fix that works (renewal −$3.42 → **+$4.57**). Third, spend only on tests that resolve espresso's two deciding inputs (Section 9), and reopen capital allocation at Checkpoint 5 with those results. Option (d), not launching, is the default if both tests fail.

Confidence is **high** that cat at $49.99 cannot be funded on paid social: the model, the Triple Whale pet ROAS median of 1.6 and Chewy's and BARK's disclosed marketing intensity all point the same way. Confidence is **low-to-medium** that espresso can pass. Its base case uses a 54mm portafilter cost as a proxy for a 51mm part, and the only 51mm-specific OEM quote is about three times higher.

---

## 2. Phase G1: the first order loses money before acquisition is even counted

### Where $49.99 goes

The workbook's line items show why a $49.99 fountain clears only **$2.08** before ads (MODEL, Cat_UnitEcon, private label, Base):

| Line (per fountain order) | Amount | Share of $49.99 | Basis |
|---|---|---|---|
| Gross revenue | $49.99 | 100% | ASSUMPTION retail price, free shipping |
| Refunds (5% of revenue) | −$2.50 | 5.0% | ASSUMPTION; no US category data |
| OEM FOB including UL/ETL-listed adapter | −$11.77 | 23.5% | VENDOR FOB $9.77 + ASSUMPTION adapter premium $2.00 |
| Duty (37.5% Section 301 stack) | −$4.41 | 8.8% | FILING (CBP N303286 + List 1 + 12.5% forced-labor 301) |
| Ocean LCL freight + destination | −$3.50 | 7.0% | ESTIMATE |
| Customs entry fees (broker, ISF, bond, MPF, HMF) | −$0.63 | 1.3% | VENDOR / FILING |
| Retail packaging | −$1.00 | 2.0% | ASSUMPTION |
| Certification amortization (FCC + Prop 65 + food contact over 1,000 units) | −$4.65 | 9.3% | VENDOR ranges, ASSUMPTION unit base |
| **Landed cost subtotal** | **−$25.97** | **52.0%** | |
| 3PL pick/pack, carton, 20% hidden-fee uplift | −$5.10 | 10.2% | SECONDHAND |
| USPS Ground Advantage, Zone 5, 2 lb | −$10.50 | 21.0% | VENDOR (Notice 123) |
| Payments, warranty re-ships, returns processing, chargebacks, affiliates | −$3.84 | 7.7% | Mixed |
| **Contribution before ads** | **$2.08** | **4.2%** | MODEL |

Two numbers explain most of the problem. Getting the product to the customer (3PL plus postage) costs **$15.60, or 31% of the price**, because the offer ships free and the box weighs about 2 lb. USPS bills the 10x10x8 box at actual weight because it is under the 1,728 cu in threshold ([USPS Notice 123](https://pe.usps.com/text/dmm300/Notice123.htm)). The tariff, freight and entry stack costs **$8.54, or 17%**, on a product whose FOB is under $12. The 12.5% forced-labor Section 301 duty has applied on top of List 1's 25% since July 24, 2026 ([C.H. Robinson](https://www.chrobinson.com/en-us/resources/blog/section-301-forced-labor-tariffs/); [Ecommerce Fastlane](https://ecommercefastlane.com/section-301-tariffs-what-changed-for-china-in-2026/)). Adding a litter mat to 25% of orders (bundle contribution $13.76) lifts the first-order mix to **$5.00 before ads, a 10% margin**, which is the number every cohort and gate uses.

The espresso kit has the same structure with more price to absorb it. At $84.99 the kit's landed cost is **$34.66**: FOB $19.30, duty $7.99 at a 41.4% stack, freight $1.50, entry fees $1.57, packaging $1.00 and certification $3.30. It then carries $6.90 of 3PL for four picks and $12.12 of 3 lb postage, and earns **$20.43 before ads**. The first-order mix, including the 15% who start beans in the first order, earns **$21.11 (25% margin)**.

### Test stage versus private label

The test stage is worse, as Checkpoint 3 predicted. AliExpress fountains cost more than Amazon generics sell for. A $28.39 AliExpress fountain lands at **$38.33** after a 30% duty pass-through (ASSUMPTION; whether AliExpress collects duty is unresolved) and the 5% AutoDS card fee. It earns **$3.70 before ads and −$56.30 after the $60 months-1–3 CPA**. The espresso test kit lands at **$56.86** and earns **$14.62 before ads, −$45.38 after CPA**. A test stage can therefore measure creative and conversion. It cannot measure margin, and its cash break-even CPAs (gate 3: **$3.70 cat, $14.62 espresso**) are informational only.

| Order type (MODEL, Base) | Cat: before ads / after CPA | Espresso: before ads / after CPA |
|---|---|---|
| (a) Hero, test stage (AliExpress) | $3.70 / −$56.30 | $14.62 / −$45.38 |
| (b) Hero, private label | $2.08 / −$42.92 | $20.43 / −$24.57 |
| (c) Hero + add-on, private label | $13.76 / −$31.24 (mat) | $24.94 / −$20.06 (first beans) |
| First-order mix, private label | $5.00 / −$40.00 | $21.11 / −$23.89 |

### Pessimistic, base and optimistic scenarios

The scenario engines compute all three cases side by side, independent of the selector (MODEL, Scenarios sheet).

**Cat home (base case)**

| Metric | Pessimistic | Base | Optimistic |
|---|---|---|---|
| Fountain price / subscription filter-pack price | $44.99 / $12.74 | $49.99 / $15.29 | $59.99 / $15.74 |
| Paid CPA, months 1–3 / months 4–12 | $90 / $65 | $60 / $45 | $40 / $32 |
| Subscription attach; later-cycle churn (monthly equivalent) | 10%; 9.7% | 20%; 5.9% | 30%; 3.5% |
| Private-label landed cost per fountain | $41.20 | $25.97 | $15.61 |
| Fountain + mat bundle, before ads / after CPA | −$17.96 / −$82.96 | $13.76 / −$31.24 | $43.35 / $11.35 |
| Filter subscription renewal | −$9.05 | −$3.42 | $1.42 |
| One-time filter repeat order | −$6.93 | −$1.79 | $6.98 |
| **First-order contribution before ads / after CAC** | −$23.06 / −$88.06 | **$5.00 / −$40.00** | $32.30 / $0.30 |
| First-order margin before ads | −53% | 10% | 49% |
| **12-month / 24-month LTV before CAC** | −$25.48 / −$26.38 | **$3.17 / $2.15** | $37.01 / $39.09 |
| 12-month LTV net of CAC | −$90.48 | −$41.83 | $5.01 |
| 12-month LTV:CAC | −0.39x | **0.07x** | 1.16x |
| Payback | None ≤24 months | None ≤24 months | Month 1 |
| 100-customer cohort, cumulative after CAC at month 24 | −$9,138 | −$4,285 | $709 |

**Espresso Dedica 51mm kit (shadow case)**

| Metric | Pessimistic | Base | Optimistic |
|---|---|---|---|
| Kit price / subscription bean-shipment price | $74.99 / $34.19 | $84.99 / $35.99 | $99.99 / $39.59 |
| Paid CPA, months 1–3 / months 4–12 | $85 / $64 | $60 / $45 | $40 / $30 |
| Private-label landed kit cost | $77.19 | $34.66 | $20.93 |
| Kit + first beans, before ads / after CPA | −$41.97 / −$105.97 | $24.94 / −$20.06 | $73.73 / $43.73 |
| Bean renewal (monthly) | −$0.23 | $4.38 | $19.08 |
| **First-order contribution before ads / after CAC** | −$42.01 / −$106.01 | **$21.11 / −$23.89** | $59.41 / $29.41 |
| **12-month / 24-month LTV before CAC** | −$41.62 / −$41.61 | **$27.16 / $29.07** | $104.88 / $129.51 |
| 12-month LTV net of CAC | −$105.62 | −$17.84 | $74.88 |
| 12-month LTV:CAC | −0.65x | **0.60x** | 3.50x |
| Payback | None | None | Month 1 |

The scenarios answer a question the base case cannot: how much optimism is needed. Cat needs *every* optimistic input at once (a $59.99 price, a $32 CPA, $15.61 landed cost, 30% attach and 3.5% monthly churn) just to break even on the first order ($0.30), and it still falls short of 1.5x LTV:CAC. Espresso's optimistic case is a strong business at 3.50x. The spread between espresso's base and optimistic outcomes is driven by three measurable inputs: the kit FOB ($19.30 base vs $13.67 optimistic, and $43.00 pessimistic), the CPA ($45 vs $30), and the bean cost (Roastify's $12.00 + $4.50 shipping vs Dripshipper's $9.39+ with free shipping) ([Roastify](https://roastify.app/pricing); [Dripshipper](https://www.dripshipper.io/bulk-espresso-beans)).

### Why this is structural, and why the market agrees

The cat model fails because five features compound, and none is unusual for the category. **The hero is low-ticket**: the observed fountain market runs from generic stainless at $18.99–$19.99 to Petlibro's Dockstream at $60.89, with the design tier topping out at Drinkwell Seascape's $95.99 ([Cats.com](https://cats.com/best-cat-water-fountain); [Amazon Best Sellers](https://www.amazon.com/Best-Sellers-Pet-Supplies-Cat-Fountains/zgbs/pet-supplies/2975263011)). **The hero is heavy relative to its price**, so free shipping costs a fifth of revenue. **The China tariff stack is 37.5%**, applied to an FOB that is already a small share of retail. **Paid-social acquisition is priced for higher-ticket baskets.** Triple Whale's Meta median for Pets & Animals (40,000+ brands, Aug 2025–Jul 2026) is a **$38.51 CPA at a 1.60 ROAS**, implying platform-attributed revenue of about $62 per acquisition ([Digital Applied, citing Triple Whale](https://www.digitalapplied.com/blog/facebook-ads-benchmarks-2026-cpc-cpm-ctr-industry)). At a 10% contribution margin, $62 of revenue funds about $6 of acquisition (ESTIMATE). **The consumable is low-value and slow**: six filters every 90 days at $15.29, against generic filters at about $0.53 each and Petlibro's subscribed price of about $2.62 per filter ([Petlibro](https://petlibro.com/products/dockstream-2-smart-fountain-replacement-filter)).

Public companies show the same arithmetic at scale. Chewy spent **6.4% of net sales** on advertising and marketing in Q2 FY2026, but it earns **$602 of net sales per active customer**, and **84.6%** of sales come from Autoship customers ([Chewy 10-Q](https://www.sec.gov/Archives/edgar/data/0001766502/000162828026061018/chwy-20260802.htm)). That is a retention machine amortizing acquisition across hundreds of dollars a year, not a $50 first order. BARK, a pet DTC brand with a **$31.06 AOV**, cut advertising and marketing **29% to $59.2M (15.0% of revenue)** in FY2026 while total orders fell **23.8%** ([BARK 10-K](https://www.sec.gov/Archives/edgar/data/0001819574/000162828026042242/bark-20260331.htm)). The inference is that low-AOV pet DTC is profitable only at scale with heavy repeat buying, and that a launch-stage brand paying median CPAs is buying revenue below cost.

---

## 3. Phase G2: subscription revenue cannot rescue a losing first order, and in cat it deepens the loss

### Renewal economics: the 90-day pack loses money on every shipment

The client default treats subscription as upside, not core. The model honors that by reporting first-order profitability separately from LTV, so the subscription cannot mask a losing first order. In cat, the subscription does the opposite of masking: it makes things worse.

| Renewal line (MODEL) | Cat 90-day 6-pack (R0) | Cat 180-day 12-pack (R2) | Espresso monthly beans |
|---|---|---|---|
| Subscription price | $15.29 | $29.99 | $35.99 |
| Product landed cost | −$5.24 | −$10.28 | −$24.00 (2 × $12.00 Roastify) |
| Pick/pack + mailer | −$4.20 | −$4.20 | — (roaster ships) |
| Postage / roaster shipping | −$8.24 (≤8 oz commercial) | −$9.29 (1 lb) | −$5.75 |
| Refunds, payments, chargebacks, returns | about −$1.03 | about −$1.65 | about −$1.86 |
| **Contribution per renewal** | **−$3.42** | **+$4.57** | **+$4.38** |
| Minimum price for +$3 / break-even (gate 9) | $21.99 / $18.86 | $28.35 needed for GO | $34.55 / $31.41 |

The 90-day pack fails because fixed per-parcel costs dominate a small basket: the $8.24 mailer and $4.20 pick/pack total $12.44, or **81% of the $15.29 price**, before the filters themselves. The pack is priced at **$2.55 per filter**, just under Petlibro's ~$2.62 anchor, as Checkpoint 3 recommended. That anchor leaves no room for a brand that ships each pack separately.

### 90-day versus 6-month packs: the client default should change

The client approved a 90-day filter cadence. **The model finds that a 12-filter, six-month pack works better on every renewal measure**, and this report recommends replacing the default. Doubling the filters per parcel adds only $1.05 of postage ($9.29 at 1 lb versus $8.24 at 8 oz) and no extra pick fee. That turns a −$3.42 renewal into **+$4.57** and passes gates 8 and 9.

| Per subscriber (MODEL, Repositioned sheet) | R0: 90-day 6-pack | R2: 180-day 12-pack |
|---|---|---|
| Month of first renewal | 4 | 7 (the $79 system includes 6 months of filters) |
| Survival to first renewal | 0.73 | 0.61 |
| Survival per later interval | 0.83 per 90 days | 0.69 per 180 days |
| Renewal contribution per subscriber, 12 months | −$6.34 | +$2.79 |
| Renewal contribution per subscriber, 24 months | −$10.83 | +$6.07 |
| Occasional (non-subscriber) repeat order | −$1.79 | +$7.44 |

The six-month pack's limit is time. It fixes the sign of renewal contribution, but it produces only about $2.79 per subscriber in the first year, against a $45 CAC. In the model's words, a six-month cadence "produces too little contribution within 12 months to carry acquisition." Churn per 180-day cycle is base monthly churn compounded, **30.7% per cycle and 39% before the first renewal** (ASSUMPTION). Checkpoint 3's operational argument for longer cadences still holds: they decouple delivery from China transit and customs holds.

### Attach, churn and lifetime: the inputs and their anchors

| Driver (ASSUMPTION unless noted) | Cat | Espresso | Anchors |
|---|---|---|---|
| Subscription attach at checkout or within 30 days | 10% / **20%** / 30% | 8% / **15%** / 25% | VetRxDirect: 34% of subscribers buy add-ons, recurring orders 20% of monthly revenue ([Ordergroove](https://www.ordergroove.com/case-studies/vetrxdirect/)) |
| Churn before first renewal | **25%** per 90-day cycle (35% / 15% P/O) | **18%** first-month drop | Peace Coffee month-1 retention 84.8% ([Loop](https://www.loopwork.co/customer-stories/peace-coffee)) |
| Later churn | **15%** per cycle + 0.7%/month involuntary ≈ **5.9%/month** | **7%/month** | Pet replenishment 3.4%/month, secondhand Recharge figure ([Foundry CRO](https://foundrycro.com/blog/dtc-pet-marketing-benchmarks-2026/)); Subbly replenishment median 6.31% ([Subbly](https://www.subbly.co/blog/subscription-churn-data-report/)); coffee 2–3% best-in-class to 9.2% before retention work ([Loop](https://www.loopwork.co/customer-stories/peace-coffee)) |
| Non-subscriber 12-month repeat rate | 20% | 15% | Cross-category average repeat rate 28.2% (vendor) ([Rivo](https://www.rivo.io/blog/repeat-purchase-rate-complete-guide)) |
| Survival to first renewal / per later interval (MODEL) | 0.73 / 0.83 per 90 days | 0.81 / 0.92 per month | — |
| Renewal contribution per subscriber, 12 / 24 months (MODEL) | −$6.34 / −$10.83 | **$27.22 / $39.18** | — |
| Payback (MODEL) | None ≤24 months | None ≤24 months | Operator norm: under 12 months on contribution ([eightx](https://eightx.co/blog/average-cac-payback-period-by-vertical)) |

Espresso's subscription is the stronger engine: about $27 per subscriber in year one. Only 15% of buyers subscribe, though, so subscription and repeat purchases together add only about $6 of 12-month LTV per acquired customer ($27.16 LTV versus a $21.11 first order). That cannot close a $45 CAC. Gate 10 makes the point precisely: espresso would need **152% attach** at base (impossible) to reach 1.5x LTV:CAC, and **110%** even at $99 (R5). For cat at base, no attach rate works, because each renewal loses money.

### A conflict in the evidence base that the model resolves

The acquisition notes' illustrative check assumed a ~$20 filter pack at ~65% margin earning about **$13 per shipment**, with a 6–9 month payback. Checkpoint 2 estimated **$7.50–$9.00** per $19.99 quarterly pack. The model's −$3.42 differs for three identified reasons: a lower price ($15.29, set under Petlibro's anchor), commercial postage ($8.24 versus Checkpoint 2's $5.00 assumption), and fuller pick/pack ($4.20 including mailer and a 20% hidden-fee uplift, versus $2.50). The model's inputs are the better-sourced set: USPS Notice 123 for postage, and Fulfill.com and Eightx for 3PL ([USPS Notice 123](https://pe.usps.com/text/dmm300/Notice123.htm); [Fulfill.com](https://fulfill.com/3pl-pricing); [eightx](https://eightx.co/blog/3pl-all-in-cost-per-order)). But postage is the input most likely to be too high (Section 4). As ESTIMATE arithmetic outside the model, restoring Checkpoint 2's $5.00 postage and $2.50 pick to the $15.29 pack would move the renewal by about $4.94, to roughly **+$1.50**. That improves the sign, not the verdict.

---

## 4. Phase G3: CPA dominates every sensitivity, and no repositioning reaches break-even

### One-way sensitivities (cat, base inputs, private label)

Each shock is a full recomputation of the cohort engine (MODEL, Sensitivity sheet).

| Shock | First order after CAC | Change | 12-month LTV before CAC | 12-month LTV net of CAC | Change |
|---|---|---|---|---|---|
| Base | −$40.00 | — | $3.17 | −$41.83 | — |
| **CPA +30%** | −$53.50 | **−$13.50** | $3.17 | −$55.33 | **−$13.50** |
| Supplier / COGS +15% | −$42.66 | −$2.66 | $0.09 | −$44.91 | −$3.08 |
| Shipping +20% | −$42.24 | −$2.24 | −$0.20 | −$45.20 | −$3.37 |
| Subscription attach −50% | −$40.00 | $0.00 | $3.73 | −$41.27 | **+$0.56** |
| Churn +50% | −$40.00 | $0.00 | $3.48 | −$41.52 | **+$0.31** |
| Returns 2x | −$44.00 | −$4.00 | −$0.97 | −$45.97 | −$4.14 |

Three readings follow. **CPA is the dominant lever**: a 30% CPA shock moves LTV four times more than any cost shock. Returns, shipping and COGS each move LTV by about $3–$4. And **less subscription attach and more churn *improve* cat LTV**, because each base renewal loses money. That is the clearest sign that the subscription is currently a liability. Payback is "none" in every row.

The **CPA × attach two-way table** (12-month LTV net of CAC) is negative in every cell from $27 to $90 CPA and from 0% to 50% attach: **−$22.70** at $27 and 0% attach, −$41.83 at the base point, and −$88.52 at $90 and 50%. Its closed form reproduces the cohort engine exactly, with a $0.00 difference.

### Repositioned scenarios R0–R6 and E0/R5

The Repositioned sheet tests whether a realistic change to the offer can pass. All variants use base costs, private-label economics, a $45 CAC (months 4–12, after any cut) and their own 100-customer, 24-month cohorts (MODEL; variant drivers are ASSUMPTION, Inputs section P). R0 and E0 reproduce the main engine exactly; every reconciliation check is 0.

| Metric (MODEL) | R0 cat base | R1 $79 system | R2 = R1 + 12-pack | R3 = R2 + CAC −35% | R4 = R2 + non-China OEM | R6 all cat levers | E0 espresso base | R5 espresso $99 |
|---|---|---|---|---|---|---|---|---|
| Hero price | $49.99 | $79.00 | $79.00 | $79.00 | $79.00 | $79.00 | $84.99 | $99.00 |
| CAC | $45.00 | $45.00 | $45.00 | $29.25 | $45.00 | $29.25 | $45.00 | $45.00 |
| First order before ads | $5.00 | $16.92 | $16.92 | $12.89 | $19.45 | $15.42 | $21.11 | $33.61 |
| **First order after CAC** | −$40.00 | −$28.08 | −$28.08 | −$16.36 | −$25.55 | **−$13.83** | −$23.89 | **−$11.39** |
| First-order margin before ads | 10% | 21% | 21% | 16% | 24% | 19% | 25% | 34% |
| Contribution per renewal | −$3.42 | −$3.42 | $4.57 | $4.57 | $4.57 | $4.57 | $4.38 | $4.38 |
| 12-month LTV before CAC | $3.17 | $15.69 | $18.67 | $14.64 | $21.20 | $17.17 | $27.16 | $39.65 |
| **12-month LTV net of CAC** | −$41.83 | −$29.31 | −$26.33 | −$14.61 | −$23.80 | −$12.08 | −$17.84 | −$5.35 |
| 24-month LTV net of CAC | −$42.85 | −$30.41 | −$24.54 | −$12.82 | −$22.01 | −$10.28 | −$15.93 | −$3.43 |
| **12-month LTV:CAC** | 0.07x | 0.35x | 0.41x | 0.50x | 0.47x | **0.59x** | 0.60x | **0.88x** |
| 24-month LTV:CAC | 0.05x | 0.32x | 0.45x | 0.56x | 0.51x | 0.65x | 0.65x | 0.92x |
| Payback | None | None | None | None | None | None | None | None |
| Cash before first PL sale (lean) | $28,830 | $35,518 | $35,518 | $35,518 | $34,170 | $34,170 | $18,650 | $18,650 |
| Hero price needed for both targets | $120.76 | $136.00 | $132.72 | $113.08 | $129.94 | $110.13 | $130.22 | $130.22 |
| CAC needed for both targets | $2.11 | $10.46 | $12.44 | $9.76 | $14.13 | $11.44 | $18.10 | $26.43 |

"Both targets" means first-order contribution after CAC of at least $0 and 12-month LTV:CAC of at least 1.5x. **No variant meets either one.** Gate results confirm it: R0 and R1 fail all 12 non-test gates. R2, R3, R4 and R6 pass only gates 8 and 9 (renewal and pack price). E0 and R5 pass 8 and 9 and are CONDITIONAL on gate 4, first-order margin (25% and 34%).

Each lever does a different job, and none is big enough alone. **The $79 system (R1)** adds about $12 per first order, but $11.58 of the extra revenue goes to the included 12 filters and brush, and more to two extra picks and 3 lb postage. **The 12-pack (R2)** is the one structural fix, and it should be adopted regardless. **The affiliate/organic mix (R3)** cuts CAC from $45 to $29.25, but 40% of first orders paying 15% commission gives back about $4 per order. **The non-China OEM (R4)** is worth about $2.50 per unit net after an unquoted 20% FOB premium. It assumes MFN Free under 8413.70.2004 with no Section 301, and filters stay China-sourced at 37.5%. Stacking everything (R6) still leaves cat needing either a **$110 price**, above every observed design-tier fountain, or an **$11 blended CAC**, roughly a quarter of base paid CPA with no evidence behind it. The closest variant in the sheet, R5, needs about $130 or a $26 CAC.

### The certification double-count fix

An earlier version of the model counted certification testing ($4,650 at base: FCC Part 15B $3,000, Prop 65 $650, food contact $1,000) twice in post-launch cash. It was amortized into unit cost at $4.65 per fountain, which is kept in all unit economics, cohorts and gates. It was also paid up front as one-time cash in Launch_Budget. Cash needed before the first private-label sale was already correct. The post-launch burn, runway and break-even rows, however, deducted the amortization a second time; they now add $4.65 back per first order on a cash basis. The fix cut break-even first orders with free acquisition from 302/452/604 to **156/234/313 per month** and lean post-launch burn from $2,842 to **$2,687 per month**. **No gate result changed.**

### Which inputs are conservative, which are weak, and which are optimistic

A critical reader should ask whether the model was built to fail. The honest answer is that several inputs lean conservative, a few lean optimistic, and the optimistic scenario already tests most of the conservative ones.

| Input | Base value | Leans conservative because | Leans optimistic because | Swing (MODEL where available) | Resolves with |
|---|---|---|---|---|---|
| **Paid CPA** (ASSUMPTION) | $60 months 1–3; $45 months 4–12 | $45 sits ~$6.50 above Triple Whale's $38.51 pet median, a new-store penalty no dataset quantifies ([Digital Applied](https://www.digitalapplied.com/blog/facebook-ads-benchmarks-2026-cpc-cpm-ctr-industry)) | The model's own funnel inputs (CPM $18, link CTR 1.1%, CVR 1.3%) imply an **uncapped CPA of $125.87** for cat and $163.64 for espresso; the $45 is a cap | CPA +30% = −$13.50 per customer | A capped live test (Section 9) |
| **Postage** (VENDOR, used as ceiling) | Commercial Zone 5: 2 lb $10.50; ≤8 oz $8.24 | Pirate Ship and Shopify Shipping keep below-commercial ounce tiers for most contiguous shipments; those cells were not retrieved ([Pirate Ship](https://support.pirateship.com/en/articles/15453569-july-2026-usps-rate-and-rule-changes)). The 8% temporary surcharge expires Jan 17, 2027 ([ship.com](https://www.ship.com/post/usps-rate-changes-july-2026)) | Zone 5 is mid-country; the pessimistic case averages Zones 5 and 8 | Shipping +20% = −$2.24 first order. Optimistic uses $9.72 fountain and $6.49 filter postage | Live Pirate Ship/Shopify rate cells |
| **3PL first-order cost** (SECONDHAND) | $5.10 ($3.00 pick + $1.25 carton + 20% uplift); renewal $4.20 | Published median first-pick is about $2.00 ([Fulfill.com](https://fulfill.com/3pl-pricing)) | Eightx reports invoices 20–50% above quoted rates ([eightx](https://eightx.co/blog/3pl-all-in-cost-per-order)); the $500/month minimum dominates at low volume | — | 2–3 written 3PL quotes |
| **Certification amortization** | $4.65/unit over 1,000 units | Vendor ranges; Chinese labs are reportedly cheaper (unsourced); over 2,000 units it would roughly halve | FCC Part 15B $3,000–$5,000 is a US-lab vendor claim ([Compliance Testing](https://compliancetesting.com/fcc-certification-faqs/fcc-certification-cost/)) | Pessimistic $14.80/unit; optimistic over 2,000 units | Lab quotes, ideally from the OEM's existing reports |
| **Returns and warranty** (ASSUMPTION) | 5% refunds; 3% full-unit warranty re-ship | Pet supplies return at 1.2% at one Swiss retailer ([Global Pet Industry](https://globalpetindustry.com/news/pet-supplies-among-least-returned-e-commerce-categories-in-switzerland/)); a pump-only replacement would cost about $10–12 instead of a full unit (ESTIMATE in cost notes) | Pump failure "after a few months" is the dominant complaint ([Kimola](https://kimola.com/reports/comprehensive-cat-water-fountain-feedback-analysis-amazon-en-us-143234)); Statista lists pet products at 8% | Returns 2x = −$4.00 first order | Sample burn-in tests; supplier warranty terms |
| **Non-China OEM premium** (ASSUMPTION) | +20% FOB ($11.72 vs $9.77), 0% duty | — | No quote exists; premium could be higher | R4 nets about +$2.50/unit | Vietnam/Thailand OEM RFQs |
| **Ocean freight** (ESTIMATE) | $3.50/fountain | Checkpoint 3 used $1.00–$2.50 (unsourced) | Cost notes put LCL at $2.20–$4.60/unit; Drewry Shanghai–LA at $7,884/FEU on Oct 15, 2026 ([Drewry](https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry)) | Pessimistic $5.00 | Forwarder quotes |
| **51mm portafilter FOB** (VENDOR proxy) | $12 (54mm proxy) | — | The only 51mm-specific quote is Everich at **$32–$35 per set** ([Alibaba](https://www.alibaba.com/product-detail/51mm-53mm-54mm-55mm-Coffee-Espresso_1600223449255.html)); AliExpress retail of a 51mm De'Longhi portafilter is $17.01–$25.66, which suggests sub-$17 FOB is plausible | Pessimistic landed kit $77.19 | Two 51mm RFQs with samples |
| **Espresso duty** (ESTIMATE) | 41.4% | Checkpoint 3 found MFN of 3.7% for tampers and 2% for kitchenware | Cost notes apply List 3 25% + 12.5% + MFN per CBP N335954 ([TariffLens](https://www.tarifflens.ai/rulings/N335954)) | Optimistic 27.9% | Broker classification |
| **Bean cost** (VENDOR) | Roastify $12.00/bag + $4.50 + $1.25 shipping | Dripshipper publishes $9.39+ with free shipping ([Dripshipper](https://www.dripshipper.io/bulk-espresso-beans)) | One merchant reported ~$14 landed per bag on Dripshipper | Optimistic renewal $19.08 | A Dripshipper account and price sheet |
| **Filter pack price** (ASSUMPTION) | $15.29 (90-day) | Checkpoint 2 suggested $19.99 | Petlibro's ~$2.62/filter and generics at ~$0.53 cap price | Gate 9: $18.86 break-even | Price test |
| **Test-stage duty / AutoDS fee** | 30% pass-through; 5% fee | Some AliExpress sellers show duty-inclusive prices | AutoDS's help page lists a 5% card top-up fee ([AutoDS](https://help.autods.com/en/articles/12700443-automate-your-orders-with-fulfilled-by-autods-fba)); the cost notes call it unverified | Test stage only | One test order |
| **MPF** | FY2026 values | FY2027 values (effective Oct 1, 2026) were not found | — | Negligible | Broker |

The table supports one strong conclusion. **Correcting every conservative input would not make cat fundable.** The optimistic scenario uses a $32 CPA, a $59.99 price, $15.61 landed cost, below-commercial filter postage, 30% attach and 3.5% churn, and it delivers 1.16x. The inputs that could change the *espresso* verdict are the ones leaning optimistic (the 51mm FOB proxy) or genuinely uncertain (CPA, bean cost). Those are the ones to test.

---

## 5. Launch capital: lean cat needs nearly twice the placeholder cash, espresso about a third as much product cash

| Cat launch tier (MODEL, base unit costs) | Lean | Moderate | Higher-capital |
|---|---|---|---|
| Fountain MOQ / filters / mats | 500 / 1,000 / 0 | 750 / 1,600 / 200 | 1,000 / 3,000 / 500 |
| Certification tests (FCC 15B + Prop 65 + food contact) | $4,650 | $4,650 | $4,650 |
| Inventory + freight + duty + customs entry | $10,999 | $17,446 | $25,087 |
| **Total one-time costs, incl. contingency** | **$20,297** | **$32,750** | **$52,931** |
| Monthly fixed, test stage / after private-label launch | $1,144 / $1,509 | $2,064 / $2,259 | $2,984 / $3,019 |
| Test ad budget (3 months) | $3,000 | $6,000 | $12,000 |
| **Total cash needed before first private-label sale** | **$28,830** | **$48,699** | **$76,125** |
| Cash available (placeholder ASSUMPTION) | $15,000 | $30,000 | $60,000 |
| Break-even new customers/month (12-month LTV net of CAC, cash basis) | Not reachable | Not reachable | Not reachable |
| First orders/month to cover fixed costs if acquisition were free | 156 | 234 | 313 |

The one-time costs bundle samples from three or more suppliers (including at least one non-China OEM), a golden sample, packaging and brand setup, a 3PL setup fee and contingency of 10–15% (ASSUMPTION inputs). Cash needed on the lean tier ranges from **$17,343** (optimistic) to **$39,026** (pessimistic). Lean post-launch burn after the certification fix is **$2,687 per month**.

Two readings matter more than the totals. First, **"not reachable" is literal.** Because 12-month LTV net of CAC is negative, every additional paid customer increases the cash need, so no volume of paid acquisition reaches break-even. Second, even with free acquisition, covering fixed costs takes **156 first orders a month** on the lean tier. That is the scale an organic or creator channel would need to deliver before the business stands on its own.

Repositioning raises cat's cash need. The included 12-filter supply in R1–R3 adds about $6,700 of inventory, freight, duty and contingency (**$35,518** lean). The non-China OEM saves about $1,350 net (**$34,170**). The espresso shadow case's core one-time cash for a first private-label run (200 kits, freight, duty and entry, Prop 65 and food-contact tests, samples) is **$8,351–$10,271**. Its total cash before the first private-label sale on the lean tier is **$18,650**, about two-thirds of cat's. Every variant in the sheet exceeds the $15,000 placeholder, so the client's real budget, still unstated, is a binding input.

---

## 6. Go/no-go gates: the numbers a validation test must hit

The GoNoGo sheet computes 14 gates at Base and the lean tier. Thresholds are analyst policy (ASSUMPTION, Inputs section N), applied identically to both cases. Any validation test should be judged against these thresholds, not against platform ROAS.

| # | Gate | Cat threshold (GO / COND) | Cat base value | Espresso threshold | Espresso base value |
|---|---|---|---|---|---|
| 1 | Private-label CPA ceiling (payback ≤9 / ≤12 months) | ≤$3.62 / ≤$3.62 | $45 → NO-GO | ≤$26.24 / ≤$27.16 | $45 → NO-GO |
| 2 | Test-stage CPA ceiling (gate 1 × learning ratio 60/45) | ≤$4.83 | $60 → NO-GO | ≤$34.98 / $36.21 | $60 → NO-GO |
| 3 | Test-stage cash break-even CPA (information) | $3.70 | $60 | $14.62 | $60 |
| 4 | First-order margin before ads | ≥35% / ≥25% | 10% → NO-GO | ≥35% / ≥25% | 25% → CONDITIONAL |
| 5 | First-order contribution after CAC | ≥$0 / ≥−$10 | −$40.00 → NO-GO | ≥$0 / ≥−$10 | −$23.89 → NO-GO |
| 6 | Payback | ≤9 / ≤12 months | None → NO-GO | ≤9 / ≤12 | None → NO-GO |
| 7 | 12-month LTV:CAC | ≥1.5x / ≥1.2x | 0.07x → NO-GO | ≥1.5x / ≥1.2x | 0.60x → NO-GO |
| 8 | Contribution per renewal | ≥$3 / ≥$0 | −$3.42 → NO-GO | ≥$3 / ≥$0 | $4.38 → GO |
| 9 | Minimum subscription price per shipment | $21.99 / $18.86 | $15.29 → NO-GO | $34.55 / $31.41 | $35.99 → GO |
| 10 | Minimum attach for LTV:CAC ≥1.5x | Not achievable | 20% → NO-GO | 152% (impossible) | 15% → NO-GO |
| 11 | Minimum attach to justify US filter inventory | Not achievable (renewal ≤$0) | 20% → NO-GO | n/a | n/a |
| 12 | Cash need vs cash available (lean) | ≤$15,000 | $28,830 → NO-GO | n/a | n/a |
| 13 | CPA at which 12-month LTV = CAC (information) | $3.17 | $45 | $27.16 | $45 |
| 14 | Hero price for first order after CAC ≥$0 / ≥−$10 | $97.21 / $86.21 | $49.99 → NO-GO | $112.53 / $101.32 | $84.99 → NO-GO |

**Overall at Base:** cat is NO-GO on 13 gates; espresso is NO-GO on 8 gates and CONDITIONAL on 1. **At Optimistic:** espresso is GO on every gate. Cat remains NO-GO on LTV:CAC (1.16x), the minimum-attach gates and cash ($17,343 vs $15,000), and CONDITIONAL on renewal (+$1.42), pack price ($15.74 vs $17.38 needed) and hero price ($59.99 vs $66.07 needed).

Translated into test targets, a validation spend is worth continuing only if it shows: a **test-stage CPA at or under about $35** for the espresso kit (gate 2), heading to **$26 or less** at private label (gate 1); a **first-order margin before ads of at least 25%, ideally 35%** (gate 4), which in practice means a kit price of $99 or more with landed cost at or under the modeled $34.66; and a **renewal contribution of at least $3** (gate 8), which espresso already meets at base and cat meets only with the 12-pack. No cat test can plausibly hit gate 1's $3.62 or gate 2's $4.83, which is why this report does not recommend a paid-social cat test.

---

## 7. Phase H: two weighted rankings of the top 10 niches disagree, and both are close

### Which ten niches, and why matcha is the tenth

The ten niches are the nine the client named plus **home matcha (prep kit plus US-supplied matcha replenishment)**. Matcha is the highest-ranked Checkpoint 1 shortlist niche (rank 7, launch 6.3 / subscription 5.9) that is neither already included nor excluded by a client default. Gel nails and scalp care fall under the MoCRA cosmetic exclusion, Montessori kits under the children's-product exclusion, and dog dental under the pet-ingestible exclusion. Matcha is also the closest structural analog to the espresso bean model, with a daily-use, higher-value consumable. That is exactly the "naturally higher-value consumable" pattern option (c) asks about. Its demand evidence is real (US retail matcha sales **+86% over three years**, NIQ via AP). Its supply is the binding risk: record tencha prices and FDA Prior Notice/FSVP obligations for imported food ([ABC7/AP](https://abc7.com/post/how-matcha-prices-popular-powdered-tea-soar-due-global-demand/17827300/); [VJM Global](https://www.vjmglobal.com/feeds/blog/fda-food-facility-registration-matcha-tea-manufacturer-requirements-2024)).

### Rubric (1–10, higher is better for the business)

| Factor | 9–10 | 5–6 | 1–2 |
|---|---|---|---|
| Demand / natural recurring demand | Large, growing, measured demand / consumed daily-to-monthly by nature | Moderate or uncertain / quarterly or usage-dependent | Shrinking or unmeasured / no real consumable |
| Sourcing (launch) / recurring fulfillment | Test-ready and private-label-ready, simple compliance / light, unregulated, US-stock-ready | Needs RFQs or a US supplier, manageable / needs a US supplier but simple | Blocked, hazmat, food or certified / liquids, hazmat, food import |
| **Unit economics (launch)** | First-order contribution before ads ≥2x a realistic CPA | Covers 50–100% of CPA | Covers <15% of CPA. **Only cat (2) and espresso (4) are modeled; all others are capped at 4 and labeled analyst estimates**, because nothing yet shows any of them beats espresso's modeled 47% coverage ($21.11 / $45) |
| Subscription contribution economics | ≥$10 per shipment and frequent | $3–$8 per shipment | Negative or near zero |
| Retention | Replenishment churn ≤4%/month evidence, low substitution | Mixed evidence, generic substitutes exist | Novelty, seasonal or lifespan-capped |
| Marketing / initial demand & acquisition | Visual demo, broad audience, low claim risk / demand plus a credible path to CAC under contribution | Workable with constraints | Claims-restricted or hostile audience |
| Competition / differentiation (higher = less hostile) | Fragmented, no owner / a defensible point of difference | Crowded tiers with room | One owner or commodity anchors |
| Ops / regulatory | Minimal | Manageable testing and claim discipline | Device, drug, food or hazmat exposure |
| Brand expansion | 8+ credible SKUs from $10 to $200 | Modest ladder | Hero plus one refill |

### Ranking 1: initial e-commerce launch

Weights: demand 20, sourcing 20, unit economics 20, marketing 15, competition 10, ops/regulatory 10, brand expansion 5.

| Rank | Niche | Demand | Sourcing | Unit econ | Marketing | Competition | Ops/reg | Expansion | **Weighted** | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 1= | Senior dog at home (traction kit) | 6 | 6 | 4* | 7 | 5 | 6 | 6 | **5.65** | Low |
| 1= | Miniature painting tools | 6 | 7 | 3.5* | 6 | 4 | 7 | 7 | **5.65** | Low |
| 3 | Cat home: stainless fountain + filters | 8 | 7 | **2 (MODEL)** | 7 | 3.5 | 5 | 6 | **5.60** | Medium |
| 4 | Pickleball accessories | 4 | 8 | 3.5* | 6 | 4 | 8 | 5 | **5.45** | Low-medium |
| 5 | Home matcha | 7 | 4 | 3.5* | 8 | 4 | 5 | 6 | **5.30** | Low |
| 6 | Oral care / cordless water flosser | 6 | 6 | 3.5* | 7 | 3 | 5 | 6 | **5.25** | Low |
| 7 | Espresso Dedica 51mm upgrade kit | 4.5 | 5 | **4 (MODEL)** | 7 | 5 | 6 | 7 | **5.20** | Medium-low |
| 8 | DIY car detailing | 5 | 6 | 3* | 8 | 3 | 4 | 7 | **5.05** | Low-medium |
| 9 | Shower filtration | 7 | 5 | 4* | 6 | 2 | 5 | 3 | **4.95** | Low-medium |
| 10 | Multi-cat litter odor (consumable-led) | 7 | 4 | 3* | 6 | 2 | 6 | 6 | **4.80** | Low |

\*Analyst estimate from Checkpoint 1–2 evidence, not modeled.

The headline is that **no niche scores above 5.7**, and the top seven sit within 0.45 points of each other, inside the noise of preliminary judgments. That is itself a finding. Once unit economics carries a fifth of the weight and is anchored to the cat model, no candidate is a strong one-time launch on paid social.

Cat's live demand earns the top demand score: "cat water fountain" search was +36% to +67% year over year in Aug–Oct 2026, and the #1 Veken stainless fountain is estimated at ~20–30K monthly sales ([Google Trends](https://trends.google.com/trends/explore?date=today%205-y&geo=US&q=cat%20water%20fountain,cat%20fountain%20filter,petlibro,pet%20water%20fountain&hl=en); [ASINsight](https://www.asinsight.com/report/US/cat-water-fountains-best)). The modeled unit economics cancel most of that advantage. Senior dog and miniature painting rise because their heroes are light and their sourcing is simple, not because their economics are proven. Senior dog faces Dr. Buzby's $39.99 anchor against generics at 24 grips for $13.91 ([Chewy](https://www.chewy.com/dr-buzbys-toegrips-dog-nail-grips/dp/1087734); [Rocketium](https://sentinel.rocketium.com/products/amazon/B08FG5TJRH)). Miniature painting's wet-palette hero sells at $29.99–$59.99 against budget options under $10 ([Redgrass](https://www.redgrasscreative.com/us/category/wet-palette/)). Pickleball scores well on sourcing and compliance, but participation growth slowed to **+1.3% in H1 2026** and Picklr filed Chapter 11 on October 9, 2026 ([Racket Business](https://racketbusiness.com/p/pickleball-s-players-keep-coming-why-are-some-clubs-going-broke); [The Kitchen Pickle](https://thekitchenpickle.com/blogs/news/picklr-bankruptcy-filing-indoor-pickleball-facilities/)). Espresso ranks seventh on launch because the Dedica wedge is narrow and December-weighted: accessory search runs at 2.1–2.6x October levels in December ([Google Trends](https://trends.google.com/trends/explore?date=today%205-y&geo=US&q=espresso%20machine,breville%20espresso,puck%20screen,WDT%20tool,bottomless%20portafilter&hl=en)). Shower filtration is penalized because Jolie owns the premium tier through Ulta and Costco, and an NBC-quoted Culligan expert says shower filters cannot soften water ([NBC Select](https://www.nbcnews.com/select/amp/rcna153901)).

### Ranking 2: subscription-enabled brand

Weights: natural recurring demand 25, retention 20, subscription contribution economics 20, initial demand & acquisition 10, recurring fulfillment 10, differentiation 10, brand expansion 5.

| Rank | Niche | Recurring demand | Retention | Sub econ | Initial demand & acq. | Fulfillment | Differentiation | Expansion | **Weighted** | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Espresso Dedica kit + beans | 9 | 5 | **5 (MODEL $4.38)** | 4 | 7 | 3 | 7 | **6.00** | Medium-low |
| 2 | Shower filtration (90-day cartridge) | 7 | 5 | 7* | 5 | 7 | 3 | 3 | **5.80** | Low-medium |
| 3 | Home matcha | 9 | 5 | 4* | 6 | 4 | 4 | 6 | **5.75** | Low |
| 4 | Senior dog (toe-grip refills) | 6 | 4 | 7* | 5 | 8 | 4 | 6 | **5.70** | Low |
| 5 | Cat home: fountain filters | 8 | 5 | **3 (MODEL −$3.42 / +$4.57)** | 5 | 7 | 3 | 6 | **5.40** | Medium |
| 6 | Multi-cat litter odor | 8 | 5 | 4* | 5 | 3 | 3 | 6 | **5.20** | Low |
| 7 | Oral care (tips, tablets) | 7 | 5 | 3* | 5 | 7 | 3 | 6 | **5.15** | Low |
| 8 | Miniature painting | 4 | 4 | 3* | 6 | 6 | 4 | 7 | **4.35** | Medium |
| 9 | Pickleball (balls + grips) | 5 | 3 | 4* | 4 | 6 | 2 | 5 | **4.10** | Medium |
| 10 | DIY car detailing (chemicals) | 4 | 4 | 3* | 5 | 3 | 3 | 7 | **3.85** | Medium |

\*From Checkpoint 2 per-shipment contribution ESTIMATES, not modeled: shower cartridge $8.35–$16.35, toe grips $17.6–$20.1 at $29.99, car chemicals $4–$6 on $40, palette paper $1.50–$4.50, pickleball $5.14 monthly or $19.93 quarterly. Oral care is scored low because Quip-style refills are reported at about $5 per quarter ([MySubscriptionAddiction](https://www.mysubscriptionaddiction.com/b/quip)), which postage alone would consume.

Espresso leads because beans are consumed daily and the modeled renewal is positive. Its weak points are differentiation (beans are interchangeable, and Breville runs its own bean program) and acquisition. Shower and senior dog rank high on per-shipment economics that come from Checkpoint 2 estimates, not this model. Their light, small refills avoid cat's postage trap, but both face an owner (Jolie; Dr. Buzby's), and senior-dog retention is capped by the dog's lifespan. Cat drops to fifth because the model shows its filter renewal is negative at the default cadence and only modestly positive at six months. Car detailing falls to last on slow consumption (a 16 oz bottle lasts 2–8 months), heavy liquids, CARB VOC limits and a DIY base that is a minority of washers (**83%** used professional washes in ICA's 2019 study) ([ICA](https://www.carwash.org/car-wash-news/ica-releases-u-s-car-wash-consumer-study)).

### Where the rankings diverge, and what the divergence means

The rankings are not forced to agree, and they do not.

| Niche | Ranking 1 (launch) | Ranking 2 (subscription) | Reading |
|---|---|---|---|
| Espresso Dedica | 7th (5.20) | **1st (6.00)** | Weak launch wedge, best recurring engine |
| Shower filtration | 9th (4.95) | **2nd (5.80)** | Proven cartridge economics; owned category |
| Miniature painting | **1st= (5.65)** | 8th (4.35) | Good one-time tools; consumable designed out |
| Pickleball | 4th (5.45) | 9th (4.10) | Easy launch, no real subscription |
| Senior dog | **1st= (5.65)** | 4th (5.70) | The only niche in the top four of both |
| Cat home | 3rd (5.60) | 5th (5.40) | Strong demand undone by economics in both |

Averaging the two rankings puts **senior dog (5.68), espresso (5.60), matcha (5.53), cat (5.50) and shower (5.38)** on top. Those five feed Phase I. Both rankings need the same caveat: unit-economics scores for the eight unmodeled niches are capped estimates. The cat model's lesson is that the paid-social CAC problem applies to any $30–$100 hardware hero, so the unmodeled niches are likely to score *lower*, not higher, once modeled.

---

## 8. Phase I (Report 6): five hybrid concepts, each with the CAC it must hit

Each concept pairs a demo-able hero with a light consumable, under the client defaults: lean budget, MOQ only after a creative win and passed samples, one US-stocked consumable line, and subscription as upside. **None is recommended for launch on current evidence.** They are ranked by how close the evidence brings them to the gates. No brand names are proposed.

### Concept 1: Dedica/51mm espresso upgrade kit with bean subscription (closest to fundable)

| Element | Detail |
|---|---|
| Positioning | "Make the Dedica you already own pull café shots": fit-guaranteed, model-specific upgrade with onboarding, priced between Amazon's $42.98–$45.99 7-piece kits and premium kits ([AS Insight](https://www.asinsight.com/report/US/tamper-tool-espresso)) |
| Target customer | Owners of De'Longhi Dedica (EC680/685/885) and other 51mm machines in their first two years. Rising queries include "51mm bottomless portafilter" (+250%) ([Complete Home Barista](https://completehomebarista.com/guides/best-upgrades-delonghi-dedica-ec685)) |
| First product | 51mm bottomless portafilter + tamper + WDT + puck screen kit at **$99** (R5), not $84.99 |
| Additional products | Knock box, scale, milk pitcher, precision basket, gasket/shower-screen annual kit; later a machine-care kit with FIFRA-safe claims ("cleans coffee oils", never "sanitizes") |
| Subscription and frequency | 2 × 12 oz espresso-roast bags **monthly** from a US white-label roaster; renewal **+$4.38** at Roastify rates, about +$19 at Dripshipper's optimistic rate (MODEL) |
| Acquisition and required CAC | Creator-led TikTok/Reels plus Spark-style whitelisting; email capture for the December gifting peak. **Blended CAC must be ≤ $26.43** to meet both targets at $99 (R5), and ≤ $34.98 at test stage (gate 2). The model's base TikTok planning CPA is $45; established-brand TikTok medians are $17–$19 (secondhand) |
| Retention strategy | Dial-in guidance by machine, roast-date freshness, easy skip and pause (AB 2863-style cancellation), the care kit riding inside bean boxes, and a 30-day default cadence (6-month retention 74% at 30 days vs 41% at 60 days, vendor data) ([Subscribfy](https://hub.subscribfy.com/docs/blog/2026-05-05-what-drives-retention-in-coffee-subscriptions-on-shopify)) |
| Supplier requirements | 51mm portafilter OEM with fit samples on real Dedica units at ≤ ~$12 FOB (the base proxy); 2-ear vs 3-ear SKU control; US roaster whose renewal orders import automatically (untested); broker ruling on the 41.4% duty stack |
| Main competitors | Normcore (5 of the top 10 58mm listings; Barista Compact Essentials Kit $282.99), unbranded Amazon kits, MHW-3Bomber, IKAPE 5-in-1 ($130.58–$175.19 on AliExpress), Breville's bean program ([Normcore](https://www.normcorewares.com/); [AS Insight](https://www.asinsight.com/report/US/espresso-accessories-58mm)) |
| Financial assumptions (MODEL) | First order $33.61 before ads, −$11.39 after a $45 CAC; 12-month LTV $39.65; 0.88x; lean cash before first PL sale $18,650; core one-time product cash $8,351–$10,271 |
| Biggest reason it might fail | The 51mm kit cannot be landed near $34.66: the only 51mm quote is $32–$35 for the portafilter alone, which produces a $77.19 landed kit in the pessimistic case. Second: a narrow, December-weighted audience cannot be bought at ≤$26 |

### Concept 2: senior-dog slippery-floor home kit with toe-grip refills

| Element | Detail |
|---|---|
| Positioning | "Help your older dog stay steady at home": traction-first, vet-friendly language, no treatment claims ("heals" turns a grooming aid into an animal drug) |
| Target customer | Owners of dogs 7+ with hard floors, often older adults, reached on Facebook and Instagram and through vet referral. Dogs 7+ are about 40% of US dogs per an unverified publisher claim ([IndexBox](https://www.indexbox.io/store/united-states-kw-orthopedic-dog-bed-840-market-analysis-forecast-size-trends-and-insights/)) |
| First product | Traction kit: sized grips, applicator and guide, plus a non-slip runner sample |
| Additional products | Non-slip runners, rear-lift harness, washable orthopedic bed cover; ramps only via a 3PL that handles bulk |
| Subscription and frequency | Toe grips every **~60 days** at $24.99–$29.99; Checkpoint 2 ESTIMATE of $17.6–$20.1 contribution per shipment |
| Acquisition and required CAC | Facebook/Instagram to older owners, vet storefront pilot, senior-dog creators. **Required CAC: unmodeled.** It must not exceed first-order contribution before ads to break even; Checkpoint 5 must model it before any test |
| Retention strategy | Sizing support, a "grips fell off" replacement guarantee, reminder cadence; sensitive end-of-life cancellation handling |
| Supplier requirements | Silicone vs latex grip quality testing; US stock of grips (tiny, light) |
| Main competitors | Dr. Buzby's (Chewy $39.99; Autoship 15% off; vet channel) ([ToeGrips](https://shop.toegrips.com/products/copy-of-vips-subscribe-save-free-encore-mobility)); generics at 24 for $13.91 |
| Financial assumptions | ESTIMATE only: light parcels avoid the cat postage trap; per-shipment refill margin is the best in the set; lifetime is capped by the dog's age |
| Biggest reason it might fail | Dr. Buzby's already owns the habit and the vet channel, generics undercut the hero, and every customer churns when the dog dies |

### Concept 3: cat "easy-clean" fountain system with six-month filter packs (base case, repositioned)

| Element | Detail |
|---|---|
| Positioning | "The 60-second-clean fountain": maintenance-led, with dishwasher-safe parts, a tool-free pump, a real pump warranty, and no kidney, UTI or "drink 40% more" claims (the best controlled study found no change in urine concentration) ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10822276/)) |
| Target customer | Multi-cat and apartment households (53M cat households, +5% in 2025) ([APPA](https://americanpetproducts.org/news/u.s.-pet-industry-reaches-158-billion-in-2025-poised-for-continued-growth-in-2026)) |
| First product | **$79 system**: corded stainless fountain, 12 filters (six-month supply) and a brush (R1) |
| Additional products | Litter mat ($19.99 add-on; 25% attach), stainless bowls, later a dry-powder deodorizer from a US co-packer if RFQs succeed |
| Subscription and frequency | **12-filter pack at $29.99 every 180 days** (R2), renewal +$4.57 |
| Acquisition and required CAC | Creator seeding (pet nano posts $50–$250; micro $250–$1,500) and an affiliate program near Petlibro's "up to 18%" ([LaunchPoint](https://www.launchpointhq.com/guides/rates/how-much-do-pets-micro-influencers-charge); [Petlibro affiliate](https://ca.petlibro.com/pages/affiliate-program)). **Blended CAC must be ≤ $11.44** with every lever stacked (R6), or ≤ $12.44 without the CAC cut and OEM switch (R2) |
| Retention strategy | Filter reminders, a pump-replacement program (pump-only re-ship instead of full unit), a care-kit add-on |
| Supplier requirements | OEM with a UL 1310/ETL-listed adapter at a 500 MOQ, FCC SDoC and food-contact reports; a non-China (e.g., Vietnam/Thailand) quote to avoid the 37.5% stack; filters in US stock |
| Main competitors | Petlibro (664 active Meta ads; ~$2.62/filter subscribed) ([BrandSearch](https://brandsearch.co/brands/petlibro.com)), Veken (44,308 reviews on one listing), Catit, PetSafe/Drinkwell, generic stainless fountains at $18.99–$19.99 |
| Financial assumptions (MODEL, R6) | First order $15.42 before ads, −$13.83 after a $29.25 CAC; 12-month LTV $17.17; 0.59x; lean cash $34,170 |
| Biggest reason it might fail | No channel in the evidence delivers an $11 CAC, and a $110 price is above every observed design-tier fountain (Drinkwell Seascape $95.99) |

### Concept 4: renter-first filtered shower system with 90-day cartridge

| Element | Detail |
|---|---|
| Positioning | Honest "chlorine-first" claims, not "softening", with easy cancellation as a deliberate contrast to reviewer complaints that a leading brand's auto-subscription is "incredibly hard to cancel" ([Thingtesting](https://thingtesting.com/brands/jolie/reviews)) |
| Target customer | Renters in hard-water or chloramine areas. Hard-water searches were +71.6% YoY in early 2026 (Spate data) ([Beauty Independent](https://orbit.beautyindependent.com/article/hard-water-rush-haircare-brands-retailers-address-mineral-buildup-consumer-awareness-grows)) |
| First product | $79–$99 handheld filtered head (Checkpoint 2's whitespace price) |
| Additional products | Inline filter, test strips, descaler; later "water" adjacencies |
| Subscription and frequency | Cartridge every **90 days** (60 for very hard water) at $25–$33; Checkpoint 2 ESTIMATE of $8.35–$16.35 contribution per shipment |
| Acquisition and required CAC | Demo-led short video (chlorine test strips, not hair-loss claims), bathroom-renovation creators. **Required CAC: unmodeled**; the higher-ticket hero improves the ratio but must still clear a ~$38–$48 paid CPA |
| Retention strategy | Hardness-based cadence, cartridge-life reminders, one-click skip |
| Supplier requirements | NSF/ANSI 177-tested cartridges from a certified OEM (NSF publicly said a leading brand was not NSF-certified) ([NSF](https://nsf.org/about-nsf/public-notices/jolie)) |
| Main competitors | Jolie (Ulta, Costco Annual Pack $139.99), Canopy, AquaTru, Afina, mass tier at $13.57–$34.99, compatible cartridges ([Warehouse Runner](https://app.warehouserunner.com/costco/1998778-jolie-filtered-showerhead-annual-pack)) |
| Financial assumptions | ESTIMATE only (Checkpoint 2); not modeled |
| Biggest reason it might fail | An owned category with ≥10 lookalikes, invisible performance ("no change" cancellations) and claims scrutiny; a shallow ladder limits LTV beyond the cartridge |

### Concept 5: home matcha prep kit with US-supplied matcha replenishment

| Element | Detail |
|---|---|
| Positioning | Café-quality matcha at home with honest origin labeling, as a deliberate answer to the "fake matcha" risk Japanese wholesalers flag |
| Target customer | Young home matcha drinkers. r/matcha is about 53K members, far smaller than r/espresso ([GummySearch](https://gummysearch.com/r/Matcha/)) |
| First product | Whisk, bowl, sifter and frother kit (prices not sourced; lead and glaze testing on ceramics required) |
| Additional products | Tins, scoops, frothers, cold-whisk bottles |
| Subscription and frequency | 30–100 g tins on a monthly-to-bimonthly cadence (ASSUMPTION; no churn data exists) |
| Acquisition and required CAC | Ritual-led short video. **Required CAC: unmodeled** |
| Retention strategy | Freshness, grade education, flexible cadence |
| Supplier requirements | A US importer or roaster-equivalent holding FDA facility registration, Prior Notice and FSVP; secured allocation of Japanese tencha despite record prices ([ABC7/AP](https://abc7.com/post/how-matcha-prices-popular-powdered-tea-soar-due-global-demand/17827300/)) |
| Main competitors | Established DTC matcha brands and Amazon |
| Financial assumptions | None sourced; Checkpoint 1 found no wholesale cost per kg for 2026 |
| Biggest reason it might fail | Supply allocation and record input costs squeeze the consumable margin that is the concept's whole point |

---

## 9. Strategic options: the evidence favors pausing capital and testing espresso's two deciding numbers

### Option (a): shift acquisition channels

The model quantifies what a channel shift must deliver: **≤ $11.44 blended CAC for the best cat configuration** and **≤ $26.43 for espresso at $99**. A 35% CAC cut from a 40% affiliate/organic share (R3) gets cat only to −$16.36 per first order, because commission claws back about $4. The channels differ in how plausible those targets are.

*TikTok and creators.* Triple Whale's TikTok cut shows a **$17.07 all-category CPA** and **$19.33 for Home & Garden**. Both are secondhand, platform-attributed and drawn from established brands, and an older calendar-2025 cut showed $32.74 ([Triple Whale](https://www.triplewhale.com/blog/tiktok-benchmarks); [Sovran](https://sovran.ai/benchmarks/tiktok-ads-benchmarks)). The model's own TikTok planning CPA is $70 / $45 / $28 because in-app attribution undercounts. Espresso's ~$26 target sits between those, which makes it testable. Cat's ~$11 sits below every published median. On cost, UGC runs about $99–$300 per video and Collabstr's average is about $197 ([Billo](https://billo.app/?p=54672); [Collabstr](https://collabstr.com/2026-influencer-marketing-report)). Checkpoint 3 estimated 30 pet nano creators at about $150 each at roughly $4.5K a month plus product.

*TikTok Shop.* US GMV was about $15.1–$15.8B in 2025 (estimates conflict; ByteDance discloses nothing) ([SmartScout](https://www.smartscout.com/blog/tiktok-shop-statistics-2026)). No fountain or espresso-accessory commission norms were found, so it cannot be modeled yet.

*Amazon.* This is where Veken (44,308 reviews), Petlibro filters (20,450 reviews) and Normcore win. Amazon's cat-fountain anchor is $18.99–$29.99 ([Amazon](https://www.amazon.com/Best-Sellers-Pet-Supplies-Cat-Fountains/zgbs/pet-supplies/2975263011)). Amazon referral and FBA fees were not researched, so an Amazon-first cat case is unmodeled. Its price anchor makes it harder, not easier, for a $49.99–$79 fountain.

*Email and SEO.* Email converts at about **4.2%** against **1.1%** for Meta paid social (secondhand) ([eightx](https://eightx.co/blog/average-ecommerce-conversion-rate-by-traffic-source-2026)), but a new brand has no list. That is a year-two lever, not a launch channel.

Verdict: plausible for espresso, implausible for cat. Confidence: low-medium.

### Option (b): raise AOV with bundles and systems at $90–$130

Price is the most powerful lever in the model because contribution is linear in price. For cat, the required prices are **$97.21** (fountain alone, first-order break-even) and **$110.13** (R6, both targets). These collide with the observed ceiling: Drinkwell Seascape at **$95.99** tops the design tier, Petlibro Dockstream sells at $60.89, and the R1 system shows that bundling filters into the price mostly moves cost around (about $11.58 of the extra revenue funds the included filters and brush). For espresso, the required prices are **$112.53** and **$130.22**. The market leaves more room there. IKAPE's 5-in-1 kit lists at $130.58–$175.19 and Normcore's Essentials Kit at $282.99, though a 7-piece Amazon kit at about $43 is the volume anchor ([AliExpress IKAPE](https://www.aliexpress.us/item/3256810579461409.html)). Verdict: raising the price works only where the category's price structure allows it; it does for espresso and does not for cat. Confidence: medium.

### Option (c): move to a niche with a heavier, higher-AOV hero or a higher-value consumable

Phase H says the next-best candidates are senior dog, shower filtration and matcha. Their appeal is real but unproven. Senior dog's grips and shower's cartridges are light, high-margin refills that avoid cat's postage trap. Matcha's consumable is daily and higher-value. A heavier hero is not a fix in itself: weight raises postage, and the binding ratio is contribution before ads to CAC. None of these has been modeled, and each faces an incumbent that owns the habit (Dr. Buzby's, Jolie) or a supply constraint (tencha). Verdict: worth one detailed model at Checkpoint 5 only if the espresso tests fail and the client still wants to launch. Confidence: low.

### Option (d): do not launch

Not launching preserves the **$28,830** lean cat cash need, or $18,650 for espresso, and avoids the base cohort's projected **−$4,285 per 100 customers by month 24**. The market evidence supports it as a rational default: a 1.6 pet ROAS median, BARK cutting acquisition spend while orders fell 23.8%, and Chewy's profitability built on $602 per customer per year rather than on first orders. Verdict: the right default for cat as configured. Confidence: high.

### Which option the evidence favors

The evidence favors **(d) for cat as configured, combined with a capped (a)+(b) test of espresso at ≥$99 through creator and TikTok acquisition**, with (c) held in reserve. The reasoning is asymmetric. For cat, every lever has been modeled and the best case still needs a CAC no channel has shown. For espresso, the optimistic scenario passes every gate, and the gap between base and optimistic rests on inputs (51mm FOB, CAC, bean cost) that RFQs and a small test can measure. Two caveats apply. First, espresso's December peak is a window: testing in November–December 2026 captures it, and missing it pushes the best test window a year out (Inference, from Checkpoint 3). Second, the founder-affinity question is still unanswered. A business built on a narrow hobby audience is harder to run without someone who lives it.

---

## 10. What remains unvalidated, and the cheapest tests to resolve it

Every material gap maps to a Checkpoint 3 checklist item or to a model input. The tests below are ordered by cost and by how much each could move the verdict. Costs cited are model inputs or cited benchmarks, not quotes.

| Unvalidated input | Why it matters | Cheapest test | Ties to CP3 check | Pass condition (gate) |
|---|---|---|---|---|
| **Blended CAC for espresso via creators/TikTok** | Decides espresso (needs ≤$26.43 at $99) | Seed 10–20 Dedica-owning creators with product (pet-free, so no cat-on-camera friction); run a small Spark-style test using the model's lean test-ad rate of $1,000/month, with a stop-loss | #1 (ad library), new | Test-stage CPA ≤ $34.98 (gate 2), trending to ≤ $26 |
| **51mm kit FOB and fit** | $12 proxy vs $32–$35 quote swings landed cost from $34.66 to $77.19 | RFQs to 2–3 51mm OEMs plus fit samples on a real Dedica; the model's lean tier budgets about $50 per sample + $60 express per supplier and a $300 golden sample | #3 | Landed kit ≤ $34.66 at a 200 MOQ; margin ≥ 25–35% at $99 (gate 4) |
| **Espresso duty stack** | 41.4% base vs 27.9% optimistic | Broker classification (tamper 8205.51, portafilter 8516.90 vs 7323/7326) | #4 | Confirms or lowers 41.4% |
| **Bean renewal automation and cost** | +$4.38 (Roastify) vs ~+$19 (Dripshipper, optimistic) | Dev-store renewal test; Dripshipper written confirmation and price sheet | #6 | Renewal order imports with no manual action; renewal ≥ $3 (gate 8) |
| **Price acceptance at $99–$130** | Price is the strongest modeled lever | A/B landing pages during the creator test | New | Conversion holds at $99+ |
| **Postage below commercial** | Commercial rates used as a ceiling | Free: pull Pirate Ship / Shopify Shipping live cells for 8 oz, 1 lb, 2 lb, 3 lb at Zones 2/5/8 | #7 | Filter mailer well below $8.24 |
| **3PL cost** | $5.10 first order; $4.20 renewal; $500 minimum | 2–3 written quotes incl. one no-minimum 3PL | #7 | ≤ model inputs |
| **Non-China fountain OEM premium** | R4 assumes +20%, unquoted | Vietnam/Thailand RFQs (client already approved parallel quotes) | #3, #4 | Premium ≤ 20% with UL-listed adapter |
| **AliExpress duty at checkout** | Test-stage 30% pass-through is a guess | One test order (fountain, filter, tamper, 51mm portafilter) | #5 | Duty treatment observed |
| **Competitive ad density** | Creative angle and CPA pressure | Meta Ad Library and TikTok Creative Center session | #1 | Maintenance or fit-guarantee angle open |
| **Absolute search volume** | Trends gives relative indices only | Keyword Planner; re-pull Trends in late November | #9 | Confirms the demand gap |
| **Senior dog, shower, matcha economics** | Phase H scores are estimates | Desk model at Checkpoint 5 (no spend) | — | Only if espresso fails |

Two tests from the Checkpoint 3 list should be **deprioritized**: US deodorizer co-packer RFQs (#8) and logged-in dropship catalogs for cat (#2). They do not affect a verdict that rests on acquisition cost. Nothing in this list requires the fountain MOQ, certification spend or inventory.

---

## 11. Decisions needed from the client before Checkpoint 5 (stop for approval)

Checkpoint 5 is the independent critical review and final recommendation. It should not start until the client answers the questions below, because several of them change what Checkpoint 5 reviews.

| # | Decision | Why it matters now | Default if unanswered |
|---|---|---|---|
| 1 | **Accept that cat as configured ($49.99 fountain, paid social, 90-day filters) is not fundable**, and freeze the fountain MOQ and certification spend | The model fails 13 of 14 gates at Base, and the best repositioning reaches 0.59x | Freeze; no cat capital |
| 2 | **State the real budget** (cash available, and the maximum acceptable loss on validation) | Every variant exceeds the $15,000 placeholder; lean cash needs are $28,830 (cat) and $18,650 (espresso) | Treat validation spend as the only approved spend |
| 3 | **Founder affinity**: does anyone drink espresso daily or live with cats? | Still unanswered since Checkpoint 2; it matters most for a hobby-audience brand | Treated as no affinity |
| 4 | **Elevate espresso Dedica to the lead candidate for testing**, at a $99+ price | The only modeled case whose optimistic scenario passes every gate | Yes, for testing only |
| 5 | **Run a capped November–December espresso creator/CPA test** | The December gifting peak is the cheapest window to measure CAC; missing it costs a year | No, unless the client approves; this reverses Checkpoint 3's default |
| 6 | **Replace the 90-day filter default with 12-filter six-month packs** if cat continues in any form | Renewal moves from −$3.42 to +$4.57 | Yes |
| 7 | **Acquisition commitment**: accept a creator/affiliate/organic-led engine (slower, labor-heavy) rather than paid social | The only route to the required CAC levels | Creator-led, with paid social for amplification only |
| 8 | **Authorize the zero- and low-cost tests in Section 10** (postage cells, 3PL quotes, broker classification, 51mm RFQs and samples, renewal dev-store test, one AliExpress test order) | They settle the inputs that decide espresso before any MOQ | Authorize |
| 9 | **Whether to model a third niche** (senior dog, shower or matcha) at Checkpoint 5 | Phase H suggests they are next-best, but none is modeled | Only if the espresso tests fail |
| 10 | **Whether to research Amazon or TikTok Shop as primary channels** (fees, commissions) | Neither is modeled; both are where incumbents win | Out of scope unless requested |

**Stop for approval.** Checkpoint 5 will proceed on the defaults above if the client does not respond.

---

## Conclusion

The study's question has changed. Checkpoints 1–3 asked which category had the best demand, ladder and recurring mechanic, and cat home won on live demand evidence. Checkpoint 4 shows that demand was never the constraint. **The constraint is the ratio between first-order contribution and the price of a new customer**, and a $50, 2 lb, 37.5%-tariffed fountain with free shipping cannot produce a ratio any paid channel accepts. Checkpoint 2's warning that no subscription would pay for acquisition was right but understated. The cat filter subscription does not merely fail to pay for acquisition; at the default cadence it loses money on every shipment. The fix that works (six-month packs) fixes the sign, not the scale.

The useful inversion is that the model now tells the client what to measure rather than what to believe. Espresso's fate rests on three numbers: a 51mm kit landed near $35, a blended CAC near $26, and conversion at $99 or more. Each can be learned for less than the cost of one fountain MOQ. If those tests fail, the honest recommendation at Checkpoint 5 is likely to be "do not launch in these categories with this acquisition model," and that is a legitimate and valuable outcome for an investor-style study.

---

## Sources

**Model and research notes (this checkpoint)**
- Workbook: `models/Cat home financial model.xlsx` (Inputs, Cat_UnitEcon, Espresso_UnitEcon, Scenarios, Sensitivity, Launch_Budget, GoNoGo, Repositioned)

**Acquisition, conversion and retention benchmarks**
- Digital Applied, Facebook Ads Benchmarks 2026 (Triple Whale and WordStream data) — https://www.digitalapplied.com/blog/facebook-ads-benchmarks-2026-cpc-cpm-ctr-industry
- Triple Whale, TikTok benchmarks — https://www.triplewhale.com/blog/tiktok-benchmarks
- Sovran, TikTok ads benchmarks — https://sovran.ai/benchmarks/tiktok-ads-benchmarks
- eightx, conversion rate by traffic source 2026 — https://eightx.co/blog/average-ecommerce-conversion-rate-by-traffic-source-2026
- eightx, CAC payback by vertical — https://eightx.co/blog/average-cac-payback-period-by-vertical
- eightx, 3PL all-in cost per order — https://eightx.co/blog/3pl-all-in-cost-per-order
- Foundry CRO, DTC pet benchmarks 2026 — https://foundrycro.com/blog/dtc-pet-marketing-benchmarks-2026/
- Subbly, subscription churn report — https://www.subbly.co/blog/subscription-churn-data-report/
- Loop, Peace Coffee case study — https://www.loopwork.co/customer-stories/peace-coffee
- Subscribfy, coffee subscription retention — https://hub.subscribfy.com/docs/blog/2026-05-05-what-drives-retention-in-coffee-subscriptions-on-shopify
- Ordergroove, VetRxDirect case study — https://www.ordergroove.com/case-studies/vetrxdirect/
- Rivo, repeat purchase rate — https://www.rivo.io/blog/repeat-purchase-rate-complete-guide
- Billo pricing — https://billo.app/?p=54672
- Collabstr 2026 influencer marketing report — https://collabstr.com/2026-influencer-marketing-report
- LaunchPoint, pet micro-influencer rates — https://www.launchpointhq.com/guides/rates/how-much-do-pets-micro-influencers-charge
- SmartScout, TikTok Shop statistics 2026 — https://www.smartscout.com/blog/tiktok-shop-statistics-2026

**Public company filings**
- Chewy 10-Q, Q2 FY2026 — https://www.sec.gov/Archives/edgar/data/0001766502/000162828026061018/chwy-20260802.htm
- BARK 10-K, FY2026 — https://www.sec.gov/Archives/edgar/data/0001819574/000162828026042242/bark-20260331.htm

**Costs: postage, 3PL, freight, duty, compliance, returns**
- USPS Notice 123 — https://pe.usps.com/text/dmm300/Notice123.htm
- Pirate Ship, July 2026 USPS rate and rule changes — https://support.pirateship.com/en/articles/15453569-july-2026-usps-rate-and-rule-changes
- ship.com, USPS rate changes July 2026 — https://www.ship.com/post/usps-rate-changes-july-2026
- Fulfill.com, 3PL pricing — https://fulfill.com/3pl-pricing
- Drewry World Container Index — https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry
- CBP ruling N303286 (pet fountains) — https://www.tarifflens.ai/rulings/N303286
- CBP ruling N335954 (tamper, portafilter) — https://www.tarifflens.ai/rulings/N335954
- C.H. Robinson, Section 301 forced-labor tariffs — https://www.chrobinson.com/en-us/resources/blog/section-301-forced-labor-tariffs/
- Ecommerce Fastlane, Section 301 China 2026 — https://ecommercefastlane.com/section-301-tariffs-what-changed-for-china-in-2026/
- Compliance Testing, FCC certification cost — https://compliancetesting.com/fcc-certification-faqs/fcc-certification-cost/
- Global Pet Industry, Galaxus return rates — https://globalpetindustry.com/news/pet-supplies-among-least-returned-e-commerce-categories-in-switzerland/
- Kimola, cat fountain review analysis — https://kimola.com/reports/comprehensive-cat-water-fountain-feedback-analysis-amazon-en-us-143234
- AutoDS help, FBA wallet — https://help.autods.com/en/articles/12700443-automate-your-orders-with-fulfilled-by-autods-fba

**Suppliers and consumables**
- Roastify pricing — https://roastify.app/pricing
- Dripshipper bulk espresso beans — https://www.dripshipper.io/bulk-espresso-beans
- Everich 51/53/54/55mm portafilter (Alibaba) — https://www.alibaba.com/product-detail/51mm-53mm-54mm-55mm-Coffee-Espresso_1600223449255.html
- IKAPE 5-in-1 kit (AliExpress) — https://www.aliexpress.us/item/3256810579461409.html

**Competition and demand**
- Cats.com, best cat water fountains — https://cats.com/best-cat-water-fountain
- Amazon Best Sellers, Cat Fountains — https://www.amazon.com/Best-Sellers-Pet-Supplies-Cat-Fountains/zgbs/pet-supplies/2975263011
- ASINsight, cat water fountains — https://www.asinsight.com/report/US/cat-water-fountains-best
- Petlibro filter subscription — https://petlibro.com/products/dockstream-2-smart-fountain-replacement-filter
- Petlibro affiliate program — https://ca.petlibro.com/pages/affiliate-program
- BrandSearch, Petlibro — https://brandsearch.co/brands/petlibro.com
- Google Trends, cat fountain set — https://trends.google.com/trends/explore?date=today%205-y&geo=US&q=cat%20water%20fountain,cat%20fountain%20filter,petlibro,pet%20water%20fountain&hl=en
- Google Trends, espresso set — https://trends.google.com/trends/explore?date=today%205-y&geo=US&q=espresso%20machine,breville%20espresso,puck%20screen,WDT%20tool,bottomless%20portafilter&hl=en
- AS Insight, tamper tool espresso — https://www.asinsight.com/report/US/tamper-tool-espresso
- AS Insight, espresso accessories 58mm — https://www.asinsight.com/report/US/espresso-accessories-58mm
- Normcore — https://www.normcorewares.com/
- Complete Home Barista, Dedica upgrades — https://completehomebarista.com/guides/best-upgrades-delonghi-dedica-ec685
- Grant 2010, fountain water intake study — https://pmc.ncbi.nlm.nih.gov/articles/PMC10822276/
- APPA, US pet industry 2025 — https://americanpetproducts.org/news/u.s.-pet-industry-reaches-158-billion-in-2025-poised-for-continued-growth-in-2026

**Other niches (Phase H and I)**
- Chewy, Dr. Buzby's ToeGrips — https://www.chewy.com/dr-buzbys-toegrips-dog-nail-grips/dp/1087734
- Rocketium, generic toe grips — https://sentinel.rocketium.com/products/amazon/B08FG5TJRH
- ToeGrips Autoship — https://shop.toegrips.com/products/copy-of-vips-subscribe-save-free-encore-mobility
- IndexBox, orthopedic dog beds — https://www.indexbox.io/store/united-states-kw-orthopedic-dog-bed-840-market-analysis-forecast-size-trends-and-insights/
- NBC Select, shower filters — https://www.nbcnews.com/select/amp/rcna153901
- NSF public notice, Jolie — https://nsf.org/about-nsf/public-notices/jolie
- Warehouse Runner, Jolie Costco Annual Pack — https://app.warehouserunner.com/costco/1998778-jolie-filtered-showerhead-annual-pack
- Thingtesting, Jolie reviews — https://thingtesting.com/brands/jolie/reviews
- Beauty Independent, hard-water rush — https://orbit.beautyindependent.com/article/hard-water-rush-haircare-brands-retailers-address-mineral-buildup-consumer-awareness-grows
- ICA, US car wash consumer study — https://www.carwash.org/car-wash-news/ica-releases-u-s-car-wash-consumer-study
- Redgrass wet palettes — https://www.redgrasscreative.com/us/category/wet-palette/
- Racket Business, pickleball clubs — https://racketbusiness.com/p/pickleball-s-players-keep-coming-why-are-some-clubs-going-broke
- The Kitchen Pickle, Picklr bankruptcy — https://thekitchenpickle.com/blogs/news/picklr-bankruptcy-filing-indoor-pickleball-facilities/
- MySubscriptionAddiction, Quip — https://www.mysubscriptionaddiction.com/b/quip
- ABC7/AP, matcha prices — https://abc7.com/post/how-matcha-prices-popular-powdered-tea-soar-due-global-demand/17827300/
- VJM Global, FDA requirements for matcha — https://www.vjmglobal.com/feeds/blog/fda-food-facility-registration-matcha-tea-manufacturer-requirements-2024
- GummySearch, r/Matcha — https://gummysearch.com/r/Matcha/
