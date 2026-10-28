# Cat Home Financial Model: Key Outputs (Checkpoint 4, Phase G), as of Oct 19, 2026

Workbook: `models/Cat home financial model.xlsx`. It has 11 sheets (including Repositioned, added later) and 9,823 live formulas, with no formula errors. Unless a figure says otherwise, it comes from that workbook with the scenario selector set to Base and the cohort stage set to private label (Inputs!D3 = 2, D4 = 2). Most inputs are tagged **ASSUMPTION**: they are the analyst's planning values, not market facts. Every input row carries a tag (FILING / VENDOR / SECONDHAND / ESTIMATE / ASSUMPTION) and a source or note.

All figures are contribution profit, meaning net revenue minus all variable costs. They are never revenue. "First order" is the first-order mix: the fountain, plus a litter mat on 25% of orders (base), at private-label landed cost.

## 1. Headline

**On the current inputs, the cat base case fails every financial gate in all three scenarios, including optimistic. The espresso shadow case has better unit economics than cat in every scenario. It still fails at base, but passes every gate in the optimistic scenario.**

- **The fountain makes almost no money even before ads.** At $49.99 with free shipping, a private-label fountain earns **$2.08 per order before ads**. The cost stack: landed cost $25.97, 3PL $5.10, USPS Zone 5 postage $10.50, fees, warranty and returns.
  - The first-order mix earns **$5.00** before ads and **−$40.00 after the $45 CAC**.
  - Break-even CPA on a private-label first order is about **$4**. The Triple Whale pet median CPA is $38.51, and this model's new-store base CPA is $45.
- **The filter subscription loses money on every renewal at base: −$3.42 per 90-day pack.**
  - A $15.29 pack (6 filters, under Petlibro's ~$2.62/filter anchor) cannot absorb $8.24 commercial postage, $4.20 pick/pack and $5.24 landed filters.
  - So higher subscription attach *lowers* LTV, and higher churn *raises* it (see Sensitivity).
  - GoNoGo gate 9: the pack must sell for **≥$21.99** to earn $3 per renewal at commercial postage, or **≥$18.86** just to break even.
- **To break even on the first order after CAC (fountain only, base costs, $45 CPA), the hero price must be about $97** (gate 14).
- **Espresso Dedica kit (shadow case), base:**
  - First order earns **$21.11** before ads and **−$23.89** after CAC.
  - Bean renewals earn **+$4.38** per month (Roastify published rates).
  - 12-month LTV:CAC is **0.60x**, against cat's **0.07x**.

## 2. Scenarios (both cases, all three computed side by side)

### Cat home (BASE CASE)

| Metric | Pessimistic | Base | Optimistic |
|---|---|---|---|
| Fountain price / filter pack (subscription) price | $44.99 / $12.74 | $49.99 / $15.29 | $59.99 / $15.74 |
| Paid CPA, months 1–3 / months 4–12 | $90 / $65 | $60 / $45 | $40 / $32 |
| Subscription attach; later-cycle churn (monthly equivalent) | 10%; 9.7% | 20%; 5.9% | 30%; 3.5% |
| (a) Fountain, test stage (AliExpress): before ads / after CPA | −$15.24 / −$105.24 | $3.70 / −$56.30 | $32.89 / −$7.11 |
| (b) Fountain, private label: before ads / after CPA | −$23.96 / −$88.96 | $2.08 / −$42.92 | $26.35 / −$5.65 |
| (c) Fountain + mat bundle, private label: before ads / after CPA | −$17.96 / −$82.96 | $13.76 / −$31.24 | $43.35 / $11.35 |
| (d) Filter subscription renewal | −$9.05 | −$3.42 | $1.42 |
| (e) One-time filter repeat order | −$6.93 | −$1.79 | $6.98 |
| Private-label landed cost per fountain | $41.20 | $25.97 | $15.61 |
| **First-order contribution before ads / after CAC** | −$23.06 / −$88.06 | $5.00 / −$40.00 | $32.30 / $0.30 |
| First-order margin before ads | −53% | 10% | 49% |
| **12-month / 24-month contribution LTV (before CAC)** | −$25.48 / −$26.38 | $3.17 / $2.15 | $37.01 / $39.09 |
| 12-month / 24-month LTV net of CAC | −$90.48 / −$91.38 | −$41.83 / −$42.85 | $5.01 / $7.09 |
| 12-month LTV:CAC | −0.39x | 0.07x | 1.16x |
| Payback | none ≤24 months | none ≤24 months | month 1 |
| Cohort cumulative after CAC at month 24 (100 customers) | −$9,138 | −$4,285 | $709 |

The test-stage cohort (Inputs!D4 = 1) is worse:
- Base: first order after CAC −$56.30, 12-month LTV net of CAC −$58.13.
- Optimistic: −$7.11 and −$2.41.

### Espresso Dedica 51mm kit (SHADOW CASE)

| Metric | Pessimistic | Base | Optimistic |
|---|---|---|---|
| Kit price / bean shipment (subscription) price | $74.99 / $34.19 | $84.99 / $35.99 | $99.99 / $39.59 |
| Paid CPA, months 1–3 / months 4–12 | $85 / $64 | $60 / $45 | $40 / $30 |
| (a) Kit, test stage: before ads / after CPA | −$40.33 / −$125.33 | $14.62 / −$45.38 | $59.05 / $19.05 |
| (b) Kit, private label: before ads / after CPA | −$42.01 / −$106.01 | $20.43 / −$24.57 | $54.64 / $24.64 |
| (c) Kit + first beans, private label: before ads / after CPA | −$41.97 / −$105.97 | $24.94 / −$20.06 | $73.73 / $43.73 |
| (d) Bean renewal (monthly) | −$0.23 | $4.38 | $19.08 |
| Private-label landed kit cost | $77.19 | $34.66 | $20.93 |
| **First-order contribution before ads / after CAC** | −$42.01 / −$106.01 | $21.11 / −$23.89 | $59.41 / $29.41 |
| **12-month / 24-month LTV (before CAC)** | −$41.62 / −$41.61 | $27.16 / $29.07 | $104.88 / $129.51 |
| 12-month LTV net of CAC | −$105.62 | −$17.84 | $74.88 |
| 12-month LTV:CAC | −0.65x | 0.60x | 3.50x |
| Payback | none | none | month 1 |

The pessimistic espresso case carries the only 51mm-specific OEM quote: Everich at $32–$35 per set, versus the 54mm proxy of $8.47–$12 used in base.

## 3. Sensitivity (cat, base inputs, private-label stage)

| Shock | First order after CAC | Change | 12-month LTV (before CAC) | 12-month LTV net of CAC | Change | Payback |
|---|---|---|---|---|---|---|
| Base | −$40.00 | — | $3.17 | −$41.83 | — | none |
| CPA +30% | −$53.50 | −$13.50 | $3.17 | −$55.33 | −$13.50 | none |
| Supplier / COGS +15% | −$42.66 | −$2.66 | $0.09 | −$44.91 | −$3.08 | none |
| Shipping +20% | −$42.24 | −$2.24 | −$0.20 | −$45.20 | −$3.37 | none |
| Subscription attach −50% | −$40.00 | $0.00 | $3.73 | −$41.27 | **+$0.56** | none |
| Churn +50% | −$40.00 | $0.00 | $3.48 | −$41.52 | **+$0.31** | none |
| Returns 2x | −$44.00 | −$4.00 | −$0.97 | −$45.97 | −$4.14 | none |

**How to read this:**
- CPA is the dominant lever.
- Returns, shipping and COGS each move LTV by about $3–$4.
- Less attach or more churn *improves* LTV, because each base-case renewal loses $3.42.

**CPA × attach two-way table (12-month LTV net of CAC):**
- Every cell from $27 to $90 CPA, and from 0% to 50% attach, is negative: −$22.70 at $27 / 0% attach, −$41.83 at the base point, −$88.52 at $90 / 50%.
- The table's closed form reproduces the cohort engine exactly (difference $0.00).

## 4. Launch budget (cat; base scenario unit costs)

| | Lean | Moderate | Higher-capital |
|---|---|---|---|
| Fountain MOQ / filters / mats | 500 / 1,000 / 0 | 750 / 1,600 / 200 | 1,000 / 3,000 / 500 |
| Certification tests (FCC 15B + Prop 65 + food-contact) | $4,650 | $4,650 | $4,650 |
| Inventory + freight + duty + customs entry | $10,999 | $17,446 | $25,087 |
| **Total one-time costs (incl. contingency)** | **$20,297** | **$32,750** | **$52,931** |
| Monthly fixed, test stage / after private-label launch | $1,144 / $1,509 | $2,064 / $2,259 | $2,984 / $3,019 |
| Test ad budget (3 months) | $3,000 | $6,000 | $12,000 |
| **Total cash needed before first private-label sale** | **$28,830** | **$48,699** | **$76,125** |
| Cash available (placeholder ASSUMPTION) | $15,000 | $30,000 | $60,000 |
| Break-even new customers per month (12-month LTV net of CAC, cash basis) | not reachable | not reachable | not reachable |
| First orders/month to cover fixed costs if acquisition were free (cash basis) | 156 | 234 | 313 |

**Certification double-count fix (applied after the first version of this note).** Certification testing ($4,650 at base) was counted twice in some places:
- It is amortized into unit cost at $4.65 per fountain over 1,000 units. That P&L view is kept in all unit economics, cohorts and gates.
- It is also paid up front as one-time cash in Launch_Budget.

The cash needed before the first private-label sale was already correct, because it offsets only test-stage orders, which carry no certification charge. The post-launch burn, runway and break-even rows, however, deducted the amortization a second time. They now add the $4.65 per first order back, on a cash basis. Effects:
- Break-even with free acquisition fell from 302 / 452 / 604 to **156 / 234 / 313** first orders per month.
- Lean post-launch burn fell from $2,842 to $2,687 per month.
- No gate result changed.

Cash needed before the first private-label sale under the other scenarios:
- Pessimistic: lean $39,026.
- Optimistic: lean $17,343.

The espresso shadow case's core one-time cash for a first private-label run (200 kits, freight/duty/entry, Prop 65 + food-contact tests, samples) is **$8,351–$10,271**. That is roughly a third of cat's lean figure.

## 5. Go/no-go gates (computed from the model)

Base scenario, lean tier. The full table is on the GoNoGo sheet. GO / CONDITIONAL thresholds come from Inputs section N.

| Gate | Cat threshold (GO / COND) | Cat base value | Espresso threshold | Espresso base value |
|---|---|---|---|---|
| 1. Private-label CPA ceiling (payback ≤9 / ≤12 months) | ≤$3.62 / ≤$3.62 | $45 → NO-GO | ≤$26.24 / ≤$27.16 | $45 → NO-GO |
| 2. Test-stage CPA ceiling (gate 1 × learning ratio 60/45) | ≤$4.83 | $60 → NO-GO | ≤$34.98 / $36.21 | $60 → NO-GO |
| 3. Test-stage cash break-even CPA (information) | $3.70 | $60 | $14.62 | $60 |
| 4. First-order margin before ads | ≥35% / ≥25% | 10% → NO-GO | ≥35% / ≥25% | 25% → CONDITIONAL |
| 5. First-order contribution after CAC | ≥$0 / ≥−$10 | −$40.00 → NO-GO | ≥$0 / ≥−$10 | −$23.89 → NO-GO |
| 6. Payback | ≤9 / ≤12 months | none → NO-GO | ≤9 / ≤12 | none → NO-GO |
| 7. 12-month LTV:CAC | ≥1.5x / ≥1.2x | 0.07x → NO-GO | ≥1.5x / ≥1.2x | 0.60x → NO-GO |
| 8. Contribution per renewal | ≥$3 / ≥$0 | −$3.42 → NO-GO | ≥$3 / ≥$0 | $4.38 → GO |
| 9. Minimum subscription price per shipment | $21.99 / $18.86 | $15.29 → NO-GO | $34.55 / $31.41 | $35.99 → GO |
| 10. Minimum attach for LTV:CAC ≥1.5x | not achievable | 20% → NO-GO | 152% (impossible) | 15% → NO-GO |
| 11. Minimum attach to justify US filter inventory | not achievable (renewal ≤ $0) | 20% → NO-GO | n/a | n/a |
| 12. Cash need vs cash available (lean) | ≤$15,000 | $28,830 → NO-GO | n/a | n/a |
| 13. CPA at which 12-month LTV = CAC (information) | $3.17 | $45 | $27.16 | $45 |
| 14. Hero price for first order after CAC ≥ $0 / ≥ −$10 | $97.21 / $86.21 | $49.99 → NO-GO | $112.53 / $101.32 | $84.99 → NO-GO |

**Overall at base:**
- Cat: NO-GO, 13 gates.
- Espresso: NO-GO, 8 gates, plus 1 conditional.

**Overall at optimistic:**
- Espresso is GO on every gate.
- Cat is NO-GO on 3 gates: LTV:CAC 1.16x, the minimum attach gates, and cash $17,343 vs $15,000. It is CONDITIONAL on 3 more: renewal +$1.42, pack price $15.74 vs $17.38 needed, and hero price $59.99 vs $66.07 needed.

## 6. What has to be true for cat to clear the gates

These are model levers, not recommendations:
- **Paid CPA well under $10 on private-label economics at $49.99.** No benchmark supports this. Otherwise the price must rise toward about $60–$97, or acquisition must come mostly from organic and affiliate channels.
- **Filter pack economics have to be fixed before any filter inventory goes to US stock.** Options:
  - a pack price of at least $19–$22;
  - below-commercial ounce-tier postage (the optimistic case assumes 15% off; actual cells were not retrieved);
  - a larger 180-day pack;
  - shipping filters inside a bundle.
- **Landed cost must fall from $26 toward $16** (the optimistic case). The main drivers are certification amortization ($4.65/unit over 1,000 units), the 37.5% Section 301 stack (a non-China OEM is the client's parallel track), the adapter premium and LCL freight.

## 7. Most important assumptions and source conflicts (conservative choice taken)

- **CPA** is ASSUMPTION: $90/$60/$40 for months 1–3 and $65/$45/$32 for months 4–12. It is anchored on the Triple Whale Meta Pets median of $38.51 (secondhand) plus a new-store penalty. It is the single largest driver.
- **Postage:** USPS Ground Advantage commercial, Notice 123 (effective Oct 4, 2026), including the 8% temporary surcharge.
  - Zone 5 is base: 2 lb $10.50, 3 lb $12.12, ≤8 oz $8.24.
  - Pessimistic is the average of Zones 5 and 8. Optimistic is Zone 5 after surcharge expiry.
  - Below-commercial ounce rates were not retrievable, so base uses commercial rates as a ceiling.
- **Duty:**
  - Fountain 37.5% (FILING: CBP N303286 + Section 301 List 1 + 12.5% forced-labor 301). Section 232 risk is unverified.
  - Filters 37.5% (ASSUMPTION; HTS unconfirmed).
  - Espresso tools 41.4% at base (conflict between CP3's 24–36.5% + MFN and the cost notes' List 3 25% + 12.5% + MFN).
- **Test-stage duty** is 30% at base. Whether AliExpress collects duty is unresolved (Case A 0% vs Case B 37.5%).
- **AutoDS 5% wallet fee:** CP3 cites the AutoDS help page; the cost notes call it unverified. Base includes it.
- **Fountain freight:** CP3 has $1.00–$2.50 (unsourced) vs the cost notes' $2.20–$4.60. Base is $3.50; pessimistic is $5.00 (2026 peak).
- **Filter churn:** the acquisition notes imply ~5%/month vs CP2's 6–10%/month planning case. Base later-cycle churn is 15% voluntary plus 0.7%/month involuntary, about 5.9%/month in total. First renewal churn is 25%.
- **Filter pack price:** CP2 suggested ~$19.99 per quarter vs CP3's "under Petlibro ~$2.62/filter". Base subscription price is $15.29 ($2.55/filter).
- **Beans:** Roastify publishes $12.00 per bag + $4.50 shipping; Dripshipper shows "$9.39+" with free shipping; one merchant reported ~$14. Base uses Roastify; optimistic uses Dripshipper.
- **51mm portafilter OEM:** Everich $32–$35 per set (pessimistic) vs the 54mm proxy at $12 (base).
- **Returns and replacements** are ASSUMPTION, with no US category data:
  - fountain refunds 8/5/3% and warranty replacement 5/3/1.5% (full-unit re-ship);
  - kit refunds 12/7/4%.
- **Launch tiers and cash available are placeholders,** because the client's budget is not stated. Certification costs are vendor-claim ranges, amortized over 500/1,000/2,000 units.
- **MPF uses FY2026 values** (0.3464%, min $33.58, max $651.50). FY2027 values were not found.

## 8. Model mechanics and verification

- **Selectors** sit on the Inputs sheet:
  - D3 picks the scenario.
  - D4 picks the first-order/cohort stage (test vs private label).
  - D5 picks the launch tier used by GoNoGo.
- **Scenarios** are computed by independent engine groups, so they don't depend on the selector. Sensitivity cases are full recomputations with shock multipliers; the shock sizes are blue inputs on the Sensitivity sheet.
- **Cohort:** 100 customers in three segments: one-time, occasional repeat (one-time filter packs), and subscribers.
  - Filter renewals bill in months 4, 7, 10 and so on. Bean renewals bill monthly from month 2.
  - First-order profitability is reported separately from LTV.
- **Verification:**
  - LibreOffice and Excel were not installed in the build environment, so the skill's `recalc.py` could not run.
  - All formulas (7,242 originally; 9,823 after the Repositioned sheet was added) were evaluated with a purpose-built Python formula engine and returned zero errors. All six selector combinations (scenario × stage) also evaluated without errors.
  - The selected views match the engine groups exactly. The two-way-table closed form matches the cohort engine.
  - Cached values were written into the file, and the workbook is flagged to fully recalculate when opened in Excel.

## Repositioned scenarios

This section covers the **Repositioned** sheet, added to the workbook after the first version of this note. Each variant uses base-scenario costs and private-label economics. CPA is $60 for months 1–3 and $45 for months 4–12 (the months 4–12 CPA is the CAC). Each variant has its own 100-customer, 24-month cohort.

The variant drivers are in Inputs section P, all tagged ASSUMPTION:
- **R1:** a $79 "easy-clean" system with free shipping. It includes the fountain, 12 filters (a 6-month supply) and a brush. The brush costs $1.50, and the filters and brush need 2 extra 3PL picks. The system ships at the 3 lb rate. Base 90-day 6-pack renewals start in month 7.
- **R2:** R1 plus a 12-filter pack at $29.99 every 180 days, shipped at the 1 lb rate ($9.29). Churn per 180-day cycle is the base monthly churn compounded: 30.7% per cycle, and 39% before the first renewal in month 7.
- **R3:** R2 with CAC cut 35% to $29.25. 40% of first orders carry a 15% affiliate commission, booked as a variable cost on first-order revenue.
- **R4:** R2 with a non-China OEM. The fountain FOB is 20% higher at $11.72, an ASSUMPTION with no quote yet. Fountain duty is 0% (MFN Free under 8413.70.2004, no Section 301). Filters stay China-sourced at 37.5%.
- **R6:** an extra variant that was not requested. It is R2 + R3 + R4 together, added to test the full combination.
- **R5:** the espresso Dedica kit at $99, with the base bean subscription.

The R0 (cat base) and E0 (espresso base) reference columns reproduce the main engine exactly; all reconciliation checks are 0.

| Metric | R0 cat base | R1 | R2 | R3 | R4 | R6 (all cat levers) | E0 espresso base | R5 espresso $99 |
|---|---|---|---|---|---|---|---|---|
| Hero price | $49.99 | $79.00 | $79.00 | $79.00 | $79.00 | $79.00 | $84.99 | $99.00 |
| CAC | $45.00 | $45.00 | $45.00 | $29.25 | $45.00 | $29.25 | $45.00 | $45.00 |
| First-order contribution before ads | $5.00 | $16.92 | $16.92 | $12.89 | $19.45 | $15.42 | $21.11 | $33.61 |
| **First-order contribution after CPA** | −$40.00 | −$28.08 | −$28.08 | −$16.36 | −$25.55 | −$13.83 | −$23.89 | −$11.39 |
| First-order margin before ads | 10% | 21% | 21% | 16% | 24% | 19% | 25% | 34% |
| Contribution per renewal | −$3.42 | −$3.42 | $4.57 | $4.57 | $4.57 | $4.57 | $4.38 | $4.38 |
| 12-month LTV (before CAC) | $3.17 | $15.69 | $18.67 | $14.64 | $21.20 | $17.17 | $27.16 | $39.65 |
| **12-month LTV net of CAC** | −$41.83 | −$29.31 | −$26.33 | −$14.61 | −$23.80 | −$12.08 | −$17.84 | −$5.35 |
| **24-month LTV net of CAC** | −$42.85 | −$30.41 | −$24.54 | −$12.82 | −$22.01 | −$10.28 | −$15.93 | −$3.43 |
| **12-month LTV:CAC** | 0.07x | 0.35x | 0.41x | 0.50x | 0.47x | 0.59x | 0.60x | 0.88x |
| 24-month LTV:CAC | 0.05x | 0.32x | 0.45x | 0.56x | 0.51x | 0.65x | 0.65x | 0.92x |
| **Payback** | none ≤24 months | none | none | none | none | none | none | none |
| Cash needed before first private-label sale (lean) | $28,830 | $35,518 | $35,518 | $35,518 | $34,170 | $34,170 | $18,650 | $18,650 |
| Hero price needed for BOTH targets (all else fixed) | $120.76 | $136.00 | $132.72 | $113.08 | $129.94 | $110.13 | $130.22 | $130.22 |
| CAC needed for BOTH targets (all else fixed) | $2.11 | $10.46 | $12.44 | $9.76 | $14.13 | $11.44 | $18.10 | $26.43 |

"Both targets" means first-order contribution after CAC of at least $0 and 12-month LTV:CAC of at least 1.5x.

**Gates passed** (same gate definitions as the GoNoGo sheet; the test-stage gates 2–3 are not re-run):

| Variant | GO | CONDITIONAL | NO-GO |
|---|---|---|---|
| R0 cat base | none | none | all 12 |
| R1 | none | none | all 12 |
| R2 | 8 (renewal $4.57), 9 (pack price $29.99 ≥ $28.35 needed) | none | 1, 4, 5, 6, 7, 10, 11, 12, 13, 14 |
| R3 | 8, 9 | none | 1, 4, 5, 6, 7, 10, 11, 12, 13, 14 |
| R4 | 8, 9 | none | 1, 4, 5, 6, 7, 10, 11, 12, 13, 14 |
| R6 | 8, 9 | none | 1, 4, 5, 6, 7, 10, 11, 12, 13, 14 |
| E0 espresso base | 8, 9 | 4 (margin 25%) | 1, 5, 6, 7, 10, 12, 13, 14 |
| R5 espresso $99 | 8, 9 | 4 (margin 34%) | 1, 5, 6, 7, 10, 12, 13, 14 |

Gate details:
- **Gate 10 (minimum attach for LTV:CAC of 1.5x):** cat R2–R6 would need 2,068–3,764% attach, and espresso R5 would need 110%. No attach rate fixes the economics.
- **Gate 11 (attach needed to justify US filter stock):** 105% for R2/R4 and 68% for R3/R6, against 20% assumed.
- **Gate 12 (cash):** every variant exceeds the lean $15,000 placeholder. The included 12-filter supply adds about $6,700 of inventory, freight, duty and contingency to the cat launch. The non-China OEM saves about $1,350 net.

### Plain-language read

**No combination tested gets cat to first-order break-even after CAC, or to 12-month LTV:CAC of 1.5x. Stacking every cat lever (R6) still loses $13.83 per first order and reaches only 0.59x.** The levers do different jobs:
- **The 12-filter, 180-day pack (R2) is the one structural fix that works.** It turns the renewal from −$3.42 to +$4.57 per shipment and passes gates 8 and 9. It should be adopted whatever else happens. But a 6-month cadence produces too little contribution within 12 months to carry acquisition.
- **The $79 system (R1) adds about $12 per first order.** About $11.58 of the extra revenue goes on the included filters and brush, and more on the extra picks and heavier postage.
- **The affiliate/organic mix (R3) cuts CAC from $45 to $29.25.** The 40% × 15% commission gives back about $4 per first order.
- **The non-China OEM (R4) is worth about $2.50 per unit.** Its cost premium is unquoted.

For R6 to meet both targets, one more change would be needed, holding everything else fixed:
- **either** a hero price of about **$110** (vs $79), above Drinkwell Seascape's $95.99, the top of the observed design tier;
- **or** a blended CAC of about **$11** (vs $29.25), roughly a quarter of the base paid CPA, with nothing in the evidence base supporting it.

So, on current evidence, no realistic repositioning of the cat offer passes. The closest variant in the whole sheet is the espresso kit at $99 (R5): −$11.39 first order after CAC, 0.88x LTV:CAC. It would still need about $130, or a CAC of about $26, to meet both targets.
