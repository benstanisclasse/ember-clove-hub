# DEMAND SIGNAL INTELLIGENCE
## Independent Platform Viability Assessment (Stage E: final verdict, 2026-11-01)

**Inputs:** Stages A-D and the winning-product research (Phases A-H). Every number below comes from those reports.
**Companion files:**
- `VIABILITY_EVIDENCE_MATRIX.csv`
- `UNRESOLVED_RISKS.md`
- `PROSPECTIVE_VALIDATION_PLAN.md`
- `MVP_RECOMMENDATION.md`

**Cost of the whole assessment:**
- no Kalodata credits, no CJ calls beyond the free-quota re-check, no money;
- no vendor contacted;
- no production database changed.

> **Verdict: PIVOT.** The proposed promise of finding demand *before it becomes obvious* is **not supported**; the
> available evidence points against it. A narrower product is partly supported: **evidence-logged research triage,
> with transparent sourcing economics**. **Nothing should be built until Kalodata and CJ give written permission.**
> If Kalodata refuses, the verdict becomes **NO-GO** for any product built on Kalodata data.

---

## 1. Executive summary

| Question from the brief | Answer | Evidence |
|---|---|---|
| 1. Do our demand signals have genuine predictive value? | **Partly.** A model on ranks 501-1,000 picks next-month break-ins at 39.7% vs 28.0% for revenue ranking. | Stage B |
| ↳ What drives that edge? | **Almost all of it comes from Kalodata's own growth field**, which tracks *next* month's growth more than its own month's and may contain post-month information. Without it: +2.7 pts, below the bar set in advance. | Stage B, post-hoc |
| 2. Do they find opportunities earlier than conventional methods? | **No.** Every method flags only 1.5-3% of first-time top-500 entrants even one month ahead. The engine and a plain growth filter catch shared products **in the same month 85% of the time**. | Stage B lead time |
| 3. Is any advantage large enough to matter? | **For alert precision, yes:** 36% vs 17% hit rate on new products vs a growth filter, so fewer wasted research hours. **For early discovery, no.** | Stage B post-hoc |
| 4. Does connecting Kalodata and CJ make the signals more actionable? | **Yes, as a filter.** It removes 94% of demand picks, which are brands or have no margin. Demand rank doesn't predict sourceability. **Yield:** 1 feasible product per 35 candidates, 0 verified. | Stage C |
| 5. Could customers get this elsewhere? | **Mostly yes.** Sell The Trend combines a TikTok Shop explorer, CJ integration, a supplier finder and a margin figure. What no one offers is **published evidence**: a scorecard, a margin formula, match confidence. | Stage D |
| 6. Can it run economically and within data rights? | **Economically, yes:** $3-7 per customer a month at lean or mid usage. **Within data rights: not as designed.** The readable Kalodata terms forbid resale and third-party provision; CJ terms restrict off-platform display. | Stage D |
| 7. Is there enough evidence to justify a commercial MVP? | **No.** Licensing is blocked, there is no lead-time advantage, no customer evidence, and the predictive edge is unverified. | All stages |

## 2. Current system assessment

**What has been built (Stage A):**
- a reproducible research system;
- 12 months of retrospective Kalodata lists (ranks 1-1,000, risers, top videos);
- walk-forward models that **reproduce byte-identically**;
- a variant-level CJ economics engine;
- rule-based opportunity scoring;
- frozen forward tests.

**Its limits:**
- **Nothing is forward- or commercially validated.**
- Supplier matching runs only as Claude agents using the CJ connector.
- No research job is scheduled.
- Licensing and customer evidence were never examined before Stage D.

**Most validated models predict persistence** (which bestsellers keep selling), not emerging demand. The two
model_v2 "breakout" models only score Kalodata's own riser list, and add 1-2 pts over a revenue rule.

## 3. Strongest research findings

1. **Retention is predictable:** top-20 products held 3 months 93% of the time. **That is not early discovery.**
2. **Break-ins from ranks 501-1,000 are predictable at about 3× the base rate,** but only about 1 in 7 picks lasts
   3 months. The edge depends on Kalodata's growth field.
3. **Supplier economics are the bottleneck.** Of 141 strong demand picks, 37% have a close CJ match, 19% make money at
   the market price, and 2.8% are feasible.
4. **Engagement, Kalodata's ROAS, star ratings and shop concentration don't predict anything.** Revenue level,
   video-driven sales and creator breadth do, at least cross-sectionally.
5. **Most lasting TikTok demand is brand-owned,** so it can't be dropshipped as the same product.

## 4. Demand-signal inventory (Stage B; `_work/stage_b_signal_inventory.csv`)

| Classification | Signals |
|---|---|
| **Leading** | Kalodata growth field (**suspect**, +0.041 AUC); on the riser list (+0.004, negligible) |
| **Leading for durability only** | Video share of revenue (+0.0065 AUC on 3-month hold) |
| **Coincident** (describe the rise you can already see) | Our month-over-month growth, acceleration, fell out of the top 500 |
| **No detectable lead** | Units, consecutive growth, previous riser, live share, price, price change, age, category growth |
| **Untestable** (no per-product history) | Video count, creator count and concentration, new creators, views per video, ad share, reviews, complaints, attributes, CJ cost and stock |

## 5. Predictive performance vs conventional discovery

Universe: products just below the top 500; 20 alerts per category per month.

| Method | Enters next month | Enters and stays 3 months |
|---|---|---|
| Revenue ranking | 28.0% | 9.7% |
| Growth ranking | 19.1% | 5.5% |
| Kalodata riser order | 8.7% | 2.5% |
| Revenue + growth momentum | 19.9% | 6.2% |
| Existing break-in model | 39.6% | 13.8% |
| **Combined engine** | **39.7%** | **14.1%** |
| Combined engine **without** Kalodata growth | 30.7% | 10.9% |

**How to read it:**
- **The combined engine adds nothing over the existing model.** Of the 7 signal families, only revenue level and
  momentum contribute. Momentum here means mostly Kalodata growth.
- **Calibration** is good (slope 0.92).
- **Rankings churn:** only 2-9% of flags repeat the next month.

## 6. Early-detection advantage

**Not demonstrated.**
- **Coverage:** of 30,243 first-time entrants, 34.5% were visible beforehand.
  - At equal alert volume, **3.0%** were flagged ≥ 1 month ahead (growth filter: 2.9%).
  - **0.5%** were flagged ≥ 2 months ahead (growth filter: 1.1%).
- **Median lead time is 1 month** for every method.
- **Data ceiling:** we can only see about 41% of next month's entrants beforehand.

## 7. False positives and limitations

**Alert accuracy:**
- At 20 alerts per category per month, the engine raises **1.5 false alerts per correct break-in**, against 2.6 for
  revenue and 4.3 for growth.
- On "breaks in and lasts 3 months" it raises **6.4 false alerts per hit**.
- **57% of correct calls are returning ex-bestsellers.**

**Main limitations:**
- retrospective data, all downloaded in October 2026;
- no untouched month;
- list-only universe;
- 12 months of history;
- estimated revenue;
- a suspect Kalodata field;
- no promotion-signal history;
- TikTok Shop → Shopify transfer untested;
- no real CAC.

Full register: `UNRESOLVED_RISKS.md`.

## 8. Kalodata + CJ integration value

**Real decision value:**
- it removes 94% of picks that aren't actionable;
- demand rank and sourceability are independent;
- match scoring is consistent (κ 0.90 between two blind AI raters).

**But:**
- **the yield is low:** 1 feasible product per 35 candidates;
- **nothing is verified:** no photos, no samples;
- **duties are unknown;**
- **it isn't automated.**

It is a **convenience and filtering benefit, not a predictive one.**

## 9. Competitive differentiation

**The bundle exists:**
- **Sell The Trend** is closest. AutoDS and Dropship.io are close behind.
- **Eleven or more tools** make unevidenced "early" claims.
- **Prices:** TikTok-data tools run $10-180 a month, research suites $20-100, and CJ's own app is free.

**The only gap we fill:** evidence and transparency, meaning a public prediction scorecard, a stated margin formula,
and match confidence. **It's easy to copy, and it only becomes an asset after months of logged predictions.**

## 10. Data licensing and commercial constraints

**Blocker.**
- **Kalodata:**
  - the current terms are unreadable (bot wall);
  - the 2023 terms bar distribution, resale, derivative works, incorporation into other products and third-party
    provision without written consent (PRC law, Shenzhen arbitration);
  - API eligibility and pricing are unclear.
- **CJ:**
  - the account is personal to your own business;
  - commercial use and off-platform display of its content need written permission;
  - the API sees only your own account's data;
  - access is suspended after 30 days without transactions.
- **25 clarification questions are drafted** in `_work/stage_d_licensing.md`. **Nothing has been sent.**

## 11. Business model analysis

- **Best-fit segment:** experienced dropshippers and small research teams triaging many candidates. **Poor fit:**
  beginners wanting "a product that will sell".
- **Price:** the market sits at $20-100 a month. Our cost floor is $12-26 for a 70% gross margin at lean or mid usage.
- **Willingness to pay: unvalidated.** There is no evidence of any kind.
- **Commercial risks:**
  - a supplier-licence refusal;
  - dependence on a data vendor that is also a potential competitor;
  - an incumbent copying the evidence features;
  - weak signals once scored in public.

## 12. Proposed MVP

See `MVP_RECOMMENDATION.md`.
- **Don't build a SaaS now.**
- **If and when licensing is cleared:** the smallest coherent product is a **weekly research-triage brief.** It contains:
  - break-in candidates from ranks 501-1,000 with a "returning vs new" label;
  - a transparent SKU-level break-even calculator;
  - match confidence;
  - a **public, timestamped scorecard of every past flag, misses included.**
- **Delivery:** first by hand to about 10 experienced sellers, with **customer-supplied API keys if the providers allow it.**

## 13. Missing evidence

1. **Forward validation:** do the frozen September forecasts hold on sealed October data?
2. **Whether Kalodata's growth field is legitimate:** re-pull October in about 4 weeks and compare.
3. Lead time at weekly granularity.
4. Written licence permission from Kalodata and CJ.
5. Willingness to pay: interviews, waitlist, pre-orders.
6. Match correctness: photos and samples.
7. Duties on China parcels.
8. Real customer-acquisition cost for flagged products.
9. History of promotion signals (creators, videos).
10. Coverage outside ranks 1-1,000.

## 14. Prospective validation plan

See `PROSPECTIVE_VALIDATION_PLAN.md`. Its decision thresholds are frozen there, before any forward outcome exists.
- **Cadence:** monthly sealed pulls, starting 2026-11-02 (approved).
- **Comparison:** locked predictions for every method at equal alert budgets, scored at +1 and +3 months.
- **Kalodata check:** a revision re-pull, to settle the growth-field question.
- **Sourcing:** CJ snapshots at prediction time.
- **Minimum horizon:** 7 monthly cohorts for both the 1-month outcome (about June 2027) and the 3-month outcome (about September 2027).
- **Cost:** about $9 a month in credits.

## 15. Final viability verdict: **PIVOT**

### Go/no-go criteria

**How the thresholds were set:**
- Where a threshold was pre-registered, it is used as registered.
- **Where it wasn't, it was set after seeing Stages B-D. That is disclosed in every case**, and those thresholds are
  given no more weight than the evidence behind them.

| Category | Threshold | Source of threshold | Result | Pass? |
|---|---|---|---|---|
| A. Predictive validity | Beats the best simple rule with CI > 0, and the lift is material (≥ 5 pts entry, ≥ 2 pts 3-month) | **Pre-registered** (Stage B) | Met with Kalodata growth (+11.6/+4.4); **not met without it** (+2.7/+1.2); leakage unresolved | **Unproven** |
| B. Early-detection value | Lead ≥ 1 month for clearly more successes than a growth filter at the same alert volume | Set after results (the brief's Part 8 question) | 3.0% vs 2.9%; 2-month lead 0.5% vs 1.1% | **Fail** |
| C. Commercial actionability | A meaningful share of flagged products sourceable at a margin | Set after results | 2.8% feasible, 0 verified; the filter itself is valuable | **Weak pass for a triage product; fail for "actionable winners"** |
| D. Technical and legal feasibility | Runs reliably **and** within written data rights | Set after results; the licensing gate was pre-registered in the Stage D plan | Technically feasible; **legally blocked** | **Fail (pending permission)** |
| E. Customer value | Any evidence of use or willingness to pay | Set after results | None exists | **Unknown** |

### Why PIVOT and not the other verdicts

- **Not GO or CONDITIONAL GO.** Two core claims fail on the data:
  - early detection;
  - differentiation from existing tools.

  A legal blocker also stands.
- **Not plain NO-GO.** The research supports a narrower, honest proposition:
  - a **research-prioritisation tool** that saves sellers time on dead ends (better alert precision, a brand and
    margin filter);
  - with a **published track record**, which no competitor offers.

  It isn't validated as a business, but it isn't contradicted either.
- **Not RESEARCH FURTHER as the headline.** The early-detection question has been answered with the data we have, and
  more data of the same kind won't change it. More research is needed, but for the pivoted proposition, and it is
  gated on licensing.

### Conditions

- **If Kalodata refuses written permission** (including a customer-supplied-key model), **the verdict becomes NO-GO**
  for any product built on Kalodata data.
- **If the forward test shows the engine without Kalodata growth below revenue ranking,** the triage proposition
  loses its main quantitative support.

## 16. Confidence assessment

| Conclusion | Confidence | Why |
|---|---|---|
| No meaningful early-detection lead with this data | **Moderate-high** | 30,243 successes; consistent across methods. The limits are monthly granularity and a list-only universe: weekly data could show more lead, but nothing here suggests it would. |
| The predictive edge depends on Kalodata's growth field | **High** | Direct sensitivity test |
| That field may leak post-month information | **Low-moderate** | Indirect evidence only; the forward re-pull will settle it |
| Licensing blocks the design as specified | **Moderate-high** | The terms are explicit, but the current Kalodata terms were unreadable and a separate API licence may exist |
| Competitors already offer the bundle | **Moderate** | Vendor pages only; nothing verified hands-on |
| Costs are low | **Moderate** | Documented prices plus assumptions; Kalodata API eligibility unclear |
| Customer demand | **Very low** | No evidence at all |

**Overall:** moderate confidence that the **original proposition should not be built**. Low confidence about whether
the pivoted proposition would succeed commercially.

---

## Final decision matrix (Part 23)

| Dimension | Evidence | Assessment | Confidence | Outstanding risk |
|---|---|---|---|---|
| Historical predictive validity | Engine 39.7% vs revenue 28.0% (CI > 0, 8/8 months); without Kalodata growth +2.7 pts | Unproven: edge rests on one suspect field | Moderate | Leakage; no untouched months |
| Early-detection advantage | 3.0% of entrants flagged ≥ 1 month ahead vs 2.9% for growth; median lead 1 month | **Not demonstrated** | Moderate-high | Monthly granularity; universe ceiling 41% |
| False-positive control | 1.5 false alerts per break-in (growth 4.3); 6.4 per lasting break-in | Better than simple rules | Moderate | Rankings churn monthly |
| Product sourcing feasibility | 37% close match, 19% margin-positive, 2.8% feasible, 0 verified | Low yield | Moderate | Match correctness; duties; supplier quality |
| Commercial usefulness | Filter removes 94% of non-actionable picks; ~35 candidates per feasible | Useful as triage, not as "winners" | Moderate | No real CAC; TikTok → Shopify transfer |
| Technical feasibility | Reproducible pipeline; matching agent-only; nothing scheduled | Feasible with engineering work | Moderate-high | CJ API access model; LLM matching cost |
| Data licensing | Kalodata 2023 terms bar resale and third parties; CJ personal-use terms | **Blocker** | Moderate-high | Written permission may be refused |
| Competitive differentiation | Sell The Trend has the bundle; nobody publishes evidence | Weak; evidence and transparency only | Moderate | Easy for incumbents to copy |
| Customer demand | None | **Unvalidated** | Very low | May be no demand at viable prices |
| Operating economics | $3-7 per customer a month (lean/mid); data $32-456 a month total | Favourable | Moderate | Kalodata enterprise API pricing |
| MVP readiness | No licence, no customers, no automated matcher | **Not ready** | High | — |

---

## Adversarial review (Part 24)

| # | Objection | Evidence for | Evidence against | Resolved? | Experiment to settle it |
|---|---|---|---|---|---|
| 1 | It doesn't predict demand; it finds products already growing | Our growth measures are coincident; 57% of hits are returning ex-bestsellers; lead time = growth filter | Beats growth and momentum on next-month precision by ~20 pts; 36% vs 17% hit rate on new products | **Largely upheld** for "demand discovery"; rejected for "alert precision" | Forward scoring of all methods (validation plan) |
| 2 | Performance comes from leakage | Kalodata growth tracks next-month growth more than its own month's (ρ 0.26 vs 0.24; partial 0.31); all data retrospective | Values identical across pulls 6-7 days apart; the field varies by month (not a static current value); our own features are leak-checked | **Open, and material:** the edge drops to +2.7 pts without the field | Sealed October pull vs a re-pull ~4 weeks later; forward scores |
| 3 | Results inflated because the data holds mostly successful products | Lists are top-ranked by construction; the long tail is missing | Universe includes all of ranks 501-1,000 and risers, many of which fail (base rate 10.9%) | **Partly upheld:** precision is valid inside the universe, but recall outside it is unknown (59% of entrants invisible) | Deeper or wider pulls (ranks 1,001-2,000), costing credits |
| 4 | A basic growth filter works nearly as well | Lead time equal; growth catches 872 vs 906 eventual entrants | Next-month precision 39.7% vs 19.1% | **Upheld for earliness; rejected for precision** | Forward test |
| 5 | Signals too noisy to be useful | Rankings churn (2-9% repeat); 6.4 false alerts per lasting break-in | Calibrated probabilities; 28/28 categories better than revenue | **Partly upheld** | Forward calibration |
| 6 | Early detection creates too many false positives | At a 2-month lead, almost nothing is caught | At equal budgets the engine has the *fewest* false positives | **Rejected at the 1-month horizon;** earlier detection is untested because none exists | Weekly cohorts |
| 7 | The products can't be sourced profitably | 2.8% feasible; median close match earns $1.69 before ads | 4 feasible and 8 gate-passing products exist | **Largely upheld** for single-unit dropshipping; bundles untested | Photo checks, samples, bundle economics |
| 8 | TikTok Shop demand doesn't transfer to independent stores | No store or ad data; the shop is closed | None | **Unresolved** (no evidence either way) | Paid test on a store (needs owner budget) |
| 9 | Customers can get the same elsewhere | Sell The Trend, AutoDS, Dropship.io; CJ's free trending feed | Nobody publishes evidence or a margin formula | **Largely upheld** | Willingness-to-pay test |
| 10 | API costs make the SaaS unattractive | Heavy usage $19-132 per customer; CJ quota exceeded at the daily-heavy level | Lean/mid $3-7 per customer; data $32-456 a month total | **Rejected,** if licences are available at current prices | Get Kalodata API pricing in writing |
| 11 | Kalodata's licence doesn't permit the intended use | 2023 terms bar resale, third parties and derivative products | Current or API terms unknown; a customer-supplied-key model might fit | **Upheld provisionally:** blocker | Written clarification (questions drafted) |
| 12 | It needs much more history before predictions are reliable | 12 months, first partial; no untouched month; few cohorts for 3-month outcomes | Large n per month (~18,800); effects consistent across all 8 months | **Partly upheld:** precision estimates are stable, but generalisation over time and seasons is untested | 7+ forward cohorts; a second provider's 2-4-year history (trial) |

**Does the review change the verdict?**
- Objections 1, 4, 9 and 11 are upheld, and they strengthen the rejection of the original proposition.
- Objection 10 is rejected and Objection 6 is partly rejected, which keeps the narrower pivot alive.
- **The verdict stays PIVOT,** with NO-GO if Kalodata licensing is refused.
