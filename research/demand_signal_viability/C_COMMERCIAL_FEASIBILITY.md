# Stage C: commercial feasibility of Kalodata × CJ (2026-11-01)

**Evidence label:** descriptive, current-snapshot evidence (CJ data from 2026-11-01). No historical profitability is
reconstructed: CJ has no price history.

**Sources:**
- Plan, frozen first: `registry/STAGE_C_PLAN.md` (DSI-C-000).
- Results: DSI-C-001.
- Script: `scripts/stage_c.py`.
- Data: the 141 CJ files from Phases F and H.
- Outputs: `_work/stage_c_*`.

**Cost:** no credits, no CJ calls. One blind rating agent.

## The short answer

**Connecting Kalodata demand to CJ sourcing changes the answer almost completely.**
- 94% of the strongest demand picks are not actionable products.
- Demand rank tells you **nothing** about whether a product can be sourced. The two pieces of information are
  independent, so the combination adds real decision value.
- **But it's a filter and a convenience, not a predictive edge.**

**The output is thin:** about 1 feasible product per 35 candidates researched, and none verified.

**Match scoring is consistent** (two independent AI raters agree 95%, κ 0.90). **It is not validated:** nobody has
compared photos or ordered samples.

**It runs only as an AI-agent research process.** Nothing yet operates as software a customer could use.

## C2. The sourcing funnel

**141 candidates** in 24 categories, from the strongest September-2026 demand predictions (Phases F and H). A
further 4 ingestibles were excluded.

| Stage | All (141) | Share [95% CI] | Validated lane (46) | Early-stage lane (95) |
|---|---|---|---|---|
| F1 Any CJ candidate found | 136 | 96% | 44 | 92 |
| F2 **Plausible (close) match** | **52** | **37%** [29, 45] | 20 | 32 |
| F3 Variant-level sourcing verified (stock, fulfilment ≥ Medium) | 44 | 31% | 18 | 26 |
| F4 Viable US shipping (all 3 test cities, ≤ 12 days) | 44 | 31% | 18 | 26 |
| F5 **Makes money before ads at the market price** | **27** | **19%** [13, 26] | 12 | 15 |
| F6 Break-even ROAS ≤ 3 | 12 | 8.5% | 5 | 7 |
| F7 **Passes every gate** (brand, demand floor, reseller price…) | **8** | **5.7%** [2.9, 10.8] | 3 | 5 |
| F8 Feasible: break-even ROAS ≤ 2 and target CAC > 0 | **4** | **2.8%** [1.1, 7.1] | 1 | 3 |
| F9 Photo-verified and sample-checked | **0** | 0% | 0 | 0 |

**Matched products (F2, n = 52):**
- **Where they ship from:** half have US warehouse stock, and that half is **supplier-shipped**, mostly at about the
  TikTok price.
- **What the product costs:** median CJ cost is **70%** of the TikTok price across all matches. For China-shipped
  ones, freight is **38%** of the price.
- **What's left over:** median contribution before ads is **$1.69 per order**. Only 33% leave anything after a
  $10 target profit.
- **Why the rest had no close match:** 46% of score-1 "substitutes" were branded or licensed designs.

**Reading:** a demand list on its own is mostly a list of things a dropshipper **can't** sell: brands, licences, and
products with no margin once shipping is paid. That is the strongest argument for the integration.

## C3. Is the match scoring reliable? (blind re-score)

**Test:** 40 matches (20 the collectors scored 1, 20 scored 2), seed 20261103, re-scored by an independent agent.
- **It saw** the TikTok title, category and price, and the CJ product's name, category, material, packing, price and
  description excerpt.
- **It did not see** the collectors' scores or notes.
- Variant lists were withheld: only close matches had them, so they would have given the answer away.

| | Blind: 1 | Blind: 2 |
|---|---|---|
| Collector: 1 | 20 | 0 |
| Collector: 2 | 2 | 18 |

- **Agreement 95%, Cohen's κ = 0.90** (linear-weighted 0.90): "reliable enough to automate" under the plan's rule.
- **The two disagreements** were downgrades: F70 (drawstring jeans vs baggy fly-front) and H72 (pavé proposal set vs
  dainty stackables). Neither had passed the economics anyway.
- **Limits:**
  - Both raters are Claude models reading the same text, so shared blind spots wouldn't show up.
  - **Neither saw photos.**
  - This shows the judgement is **consistent and automatable**, not that it is **correct**. Correctness needs a photo
    comparison (Kalodata images, ~0.01 credit each) and samples.

## C4. Does demand rank predict sourceability?

| Lane | Demand percentile vs close match (ρ) | vs passing all gates (ρ) | vs branded design (ρ) |
|---|---|---|---|
| Validated (46) | **−0.34** | −0.15 | +0.23 |
| Early-stage (95) | +0.06 | −0.11 | −0.13 |

**By Sep revenue tercile:**
- **Validated lane:** close-match rate rises with revenue (27% → 40% → 63%), but gate passes don't (0%, 13%, 6%).
- **Early-stage lane:** the branded share rises with revenue (22% → 26% → 41%).

**Reading:**
- **The demand model's confidence doesn't predict actionability.** In the validated lane, the products it is surest
  about are, if anything, *less* likely to have a close CJ match.
- The two data sources carry **independent** information. That is why combining them is useful, and also why demand
  research alone over-promises.

## C5. Research effort per actionable product

| Measure | Value |
|---|---|
| CJ calls per candidate | 6.2 (1.5 searches, 2.2 detail lookups, 0.4 variants, 0.4 inventory, 1.7 freight) |
| CJ API points per candidate (documented rates) | ~124. The free quota of 50,000/day is enough for ~400 candidates a day. |
| AI agent tokens per candidate | ~59-65k |
| Agent wall time per candidate | ~90-110 s per collector; 6 in parallel finished 70 candidates in 22-28 min |
| Candidates researched per product passing all gates | **17.6** |
| Candidates researched per feasible product | **35** |
| Human time saved | **Not measured.** No user did this research by hand, so there is nothing to compare against. |

**At current rates:** a monthly run on 4 candidates per category across 24 categories would yield **about 5 gate-passes
and 2-3 feasible products a month, all still unverified.**

## C6. Capability assessment (brief Part 11)

| Capability | Technically possible? | Implemented? | Matching reliable? | Reduces effort? | Improves selection? | Data current? | Elsewhere? | Expensive API? | Convenience or predictive? |
|---|---|---|---|---|---|---|---|---|---|
| **Supply-validated demand signals** (only show sourceable demand) | Yes | **As an agent process only** (Claude + CJ MCP connector); no automated code path | Consistent (κ 0.90), not photo-verified | Likely: ~2 min of agent time vs unknown human time | **Yes:** removes 94% of demand picks; demand rank ≠ sourceability | CJ snapshot; drift unknown | pending Stage D | CJ points free (~124/candidate); needs a **direct CJ API key** and its terms (D) | **Convenience and filtering.** No predictive gain. |
| **Margin-aware discovery** (contribution, break-even CAC/ROAS) | Yes | Yes (`phase_f_economics.py`) | n/a | Yes | Yes: 22 of 52 matches have no contribution at market price | Fees and returns assumed; **duties unknown** (DDU) | pending D | None | Decision support |
| **Fulfilment-aware ranking** (stock, warehouse, delivery days) | Yes | Yes (gates R3, R7, ≤ 12-day rule) | n/a | Yes | Yes: exposes the US supplier-shipped retail-price trap (13 of 31 Phase F matches) | Snapshot; factory stock unverified | pending D | None | Decision support |
| **Supplier availability alerts** (an emerging product appears on CJ) | Yes: periodic CJ search plus match | **No** | Same matcher | Would | Unknown | Would be | pending D | Search costs 50 points; ~1,000 watch items a day fit the free quota | Convenience |
| **Demand-to-source matching** (one click from trend to supplier) | Yes | Agent-run; needs ~60k LLM tokens per product (a cost not counted above) | Consistent; correctness unverified | Yes | It *is* the filter | Snapshot | pending D | LLM cost per match, plus CJ terms | Convenience |
| **Opportunity risk** (brand/IP, children's products, battery, sizing, unproven listing, factory-only stock) | Yes | Yes (rule flags) | Rule-based; brand check has known false positives | Yes | Flags 2 of 5 Phase H finalists as compliance problems | Static rules | pending D | None | Decision support |

## What Stage C means for the platform idea

1. **The integration is the most commercially useful part of the system.** Demand rank alone sends sellers to brands
   and to products with no margin, and doesn't predict sourceability. That is a real, explainable benefit.
2. **It is a convenience and filtering benefit, not evidence of better demand prediction.**
3. **Yield is low:** about 1 feasible product per 35 candidates, and so far none verified. A product promising
   "actionable opportunities" would surface a handful a month, each needing photo checks, samples and compliance work.
4. **It isn't software yet.** Matching runs through Claude agents using the CJ connector in this desktop app. A product
   would need a direct CJ API integration (and its terms), an automated matcher (LLM costs per match), and photo comparison.
5. **The economics depend on assumptions we haven't verified:** duties, return rates, fees, and above all **our real
   customer-acquisition cost**, which is unknown.

## Checkpoint

- **Saved:** this report, the plan (DSI-C-000), DSI-C-001, `scripts/stage_c.py`, the funnel CSV, the results, and
  the blind re-score sample, key and ratings.
- **Deviation:** variant keys were withheld from the blind packets, a design fix made before rating.
- **Unresolved:**
  - match correctness (photos and samples);
  - CJ price and stock stability over time;
  - duties;
  - human research-time comparison;
  - whether competitors already offer supplier matching (Stage D).
- **Stage D (platform business viability) is ready.** It needs **web research** (competitors, pricing, Kalodata and CJ
  terms) and cost modelling. No spending is required.
