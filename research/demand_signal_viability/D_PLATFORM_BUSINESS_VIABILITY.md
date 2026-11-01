# Stage D: platform business viability (2026-11-01)

**Evidence labels:**
- **Competitors:** vendors' own public pages, accessed 2026-11-01. Almost nothing is independently verified, since we
  signed up for nothing.
- **Licensing:** a reading of public terms. **Not legal advice.**
- **Costs:** documented price lists plus labelled assumptions.
- **Willingness to pay:** **no customer evidence exists.**

**Sources:**
- Plan, frozen first: `registry/STAGE_D_PLAN.md` (DSI-D-000).
- Results: DSI-D-001.
- Research files:
  - `_work/stage_d_competitors.md` (19 tools, 49 sources)
  - `_work/stage_d_licensing.md` (24 sources)
  - `_work/stage_d_cost_model.json`, from `scripts/stage_d_cost.py`
- Earlier provider comparison: `research/kalodata/PROVIDER_COMPARISON_2026-10-25.md`.

**Cost:** nothing spent. No sign-ups, no contact with vendors.

## The short answer

1. **Licensing is a launch blocker today.**
   - **Kalodata:** its current terms are behind a bot wall. The readable 2023 terms forbid reselling, redistributing,
     building the service into another product, and giving it to third parties without written consent.
   - **CJ:** its terms make an account personal to the holder's business and require written permission to show its
     content off-platform.
   - **The product as designed needs written permission from both.**
2. **The feature bundle is not new.**
   - **Sell The Trend** already combines a TikTok Shop explorer, CJ integration, an AI supplier finder and a profit-margin
     figure. AutoDS and Dropship.io are close behind.
   - **At least 11 tools claim "early" or "before it goes viral" detection, and none publishes any evidence.**
3. **What nobody offers is evidence:**
   - a public, timestamped record of past flags and how they turned out;
   - a stated SKU-level margin formula;
   - match-confidence scores.

   That's the only gap our work actually fills. It's also a gap an incumbent could close quickly.
4. **Running costs are not the problem.**
   - Shared data costs **$30-$460 a month** whatever the customer count.
   - Lean or mid usage costs about **$3-$7 per customer a month**, so a **$13-$26 price** gives a 70% gross margin.
   - Market prices for these tools are $20-$100 a month.

   **The risk is not cost but permission, differentiation, and whether anyone would pay.**

## D1. Competitors

Detail in `_work/stage_d_competitors.md`.

| Group | Examples | Price band (list, 2026-11-01) | Demand data | Supplier link | Margin |
|---|---|---|---|---|---|
| TikTok Shop intelligence | Kalodata, FastMoss, EchoTik, Shoplus, Tabcut, ShopShark | **$10-$180/mo** self-serve (Kalodata App Store $49.99-$179.99; FastMoss $49/$89/$139; EchoTik from $9.9); enterprise or API custom, or $450-$900 | Yes: the source of the data | **None found** | No |
| Dropshipping research suites | **Sell The Trend** ($49.97/$99.97/$299.97), Minea ($49/$99/$199), Dropship.io ($39/$59/$99), AutoDS ($26.90-$66.90 + $14.97 TikTok add-on), Winning Hunter, TrendTrack | **$20-$100/mo** core, up to $300 | Some TikTok Shop data (Sell The Trend since June 2026; AutoDS add-on; Dropship.io library) | **Yes**: CJ / AliExpress / own warehouse | A figure is shown; **no formula published** |
| Supplier platforms | CJ app, Zendrop | **Free** (CJ); Zendrop $0/$49/$79 | Trending lists | Native | — |

**What this means for the claims:**
- **"Combine demand signals, supplier matching and margin": already partly done.** No one documents our exact chain
  (TikTok Shop product → automatic CJ SKU match → landed cost → break-even CPA/ROAS), but **Sell The Trend is one step from it.**
- **"Find products before they're popular": everyone claims it, and nobody shows evidence.**
  - Our Stage B result (no real lead time) suggests the claim is hard to back up. Our data is a fair sample of what
    these tools also see.
  - Kalodata's own FAQ warns against using its data where high precision is needed.
- **Free substitutes cap the price:** CJ's free trending feed, FindNiche ("now free") and EchoTik from $9.9.

## D2. Licensing: the gate

Detail and the 25 drafted questions are in `_work/stage_d_licensing.md`.

### Kalodata

**The current terms couldn't be read:** every kalodata.com page, including the Open API docs and terms, returned a
Cloudflare 403. The readable copies are its 2023 Terms of Service (gitbook, Aug and Nov 2023). They predate the 2026
Open API, so we can't confirm they still apply.

| Planned use | 2023 terms |
|---|---|
| 1. Show raw records to subscribers | **Prohibited/ambiguous**: no distributing or providing to third parties (4.1.3-4.1.5) |
| 2. Show derived metrics | Ambiguous: derivative works barred (4.1.2) |
| 3. Predictive rankings from the data | **Ambiguous** (derivative work / commercial use without consent, 4.1.5, 10.3) |
| 4. Store history indefinitely | **Silent** |
| 5. Cache responses | Silent |
| 6. Serve many customers | **Prohibited** (third parties, 4.1.5; the Chinese text prevails) |
| 7. Sell subscriptions to derived intelligence | **Prohibited** without written consent (4.1.3-4.1.5) |
| 8. Build a competing product | Barred from incorporating the Services into another product (4.1.7) |
| 9-11. Attribution, deletion, model training | Silent |

**Other terms:**
- PRC law, with arbitration at the Shenzhen Court of International Arbitration (SCIA);
- an uncapped indemnity;
- a limited, non-transferable licence.

**Two more problems:**
- **API pricing and eligibility are unclear.** Third-party reports conflict: Enterprise-only at about $570/month, or
  self-serve keys at about 0.1 credit per call. We actually paid about $0.10 per credit.
- **TikTok's developer terms**, which Kalodata's terms bring in, were not reviewed.

**Verdict: launch blocker on items 1, 3, 4, 6 and 7 until Kalodata gives written permission.**

### CJ

**User Agreement (effective 2025-10-04):**
- The account is personal-use only without consent (III.2), and sharing it outside your business is barred (III.6).
- Commercial use of platform content, and re-displaying it off-platform, need written permission (IX.3(1)-(2)).
- The ToS (§2) bars resale.

**The developer docs fit own-account use only:**
- a key "only views the data under the current account";
- at most 3 users per IP;
- 50,000 points a day, plus 100 per $1 of recent orders;
- access suspended after 30 days with no transactions.

**No partner or ISV programme** was found. CJ's "Dropshipping Agreement 2024.12.23" PDF couldn't be read.

**Verdict:** serving subscribers from our account, or displaying CJ data inside our product, is a **blocker until CJ
agrees in writing.**
- A partial workaround exists: **each customer connects their own CJ account** (a bring-your-own-key design).
- **That design still needs CJ's confirmation** and changes the product.

**Nothing has been sent to either provider.** Asking them needs the owner's approval.

## D3. Customer segments: what we could actually deliver

| Segment | Their problem | What Stages B-C showed we can deliver | Fit |
|---|---|---|---|
| Beginner dropshippers | "Tell me a product that will sell" | We can't promise that: 1 feasible product per 35 candidates; early signals barely beat a growth filter on timing | **Poor**: high expectations, high false-positive burden, price-sensitive, free alternatives |
| Experienced dropshippers / small teams | Too many candidates to research; poor margins; brand traps | **Demonstrated**: fewer wasted alerts (36% vs 17% hit rate on new products); a sourcing filter that removes 94% of demand picks; transparent break-even maths | **Best fit**, as research-triage software, not "winning products" |
| Shopify store owners | Products that sell through ads | Margin maths yes. **TikTok Shop → Shopify transfer unvalidated.** | Plausible, unvalidated |
| TikTok Shop sellers | What to stock next | They can buy Kalodata or FastMoss directly; sourcing value is the same | Weak differentiation |
| Agencies / product-research teams | Screening many products for clients | Demonstrated triage and consistency (match κ 0.90); they would also want the evidence log | Plausible; needs alerts and exports |
| Established brands | Market intelligence | Not our strength; they buy enterprise data | Poor |

**Willingness to pay: unvalidated.** We have no interviews, waitlist, beta, survey or payments. Competitor prices show
what people pay for *those* tools, not that anyone would pay for ours.

**A low-cost test**, with spending and publishing subject to owner approval:
1. **A landing page** with the evidence-first positioning, plus a "join the beta" or "pre-order at $29/mo" button.
2. **Traffic:** $200-300 of targeted ads, or posts in 2-3 dropshipping communities.
3. **Success:** at least 5% of visitors leave an email and at least 1% pre-pay.
4. **About 10 interviews** with experienced dropshippers about research time and alert value.

## D4. Unit economics

**Inputs:**
- Kalodata at $0.10 per credit (observed);
- documented credit costs;
- CJ points free;
- Claude list prices: Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50, Opus 5.5 $4/$20 per million tokens; Batch API 50% off.

**Assumptions** (labelled in the script):
- hosting $150 / $600 / $3,000 a month at 100 / 1,000 / 10,000 customers;
- support at $2.50 per customer;
- 3% payment fees;
- half of watchlist refreshes shared between customers;
- 90% of flags new each refresh (Stage B stability).

| Scenario (per month) | 100 customers | 1,000 | 10,000 | Cost per customer | Price for 70% gross margin |
|---|---|---|---|---|---|
| **Lean:** weekly refresh, 300 products enriched, Haiku batch matcher, small watchlists | $477 | $3,566 | $32,363 | $4.77 → $3.24 | **$18 → $12** |
| **Mid:** weekly, 1,000 enriched, Sonnet matcher, 50-item watchlists | $699 | $4,373 | $39,016 | $6.99 → $3.90 | **$26 → $14** |
| **Heavy:** daily, 1,000 enriched, agent-style matcher (as we ran it), 100-item daily watchlists | $13,156 | $29,356 | $189,256 | $132 → $19 | **$487 → $70** |

**Reading the costs:**
- **Data is cheap.** Shared Kalodata collection is **$32 a month (weekly) to $456 (daily)**, whatever the customer count.
- **The big variable costs are:**
  - **per-customer watchlist calls** (up to $15 per customer a month at daily refresh);
  - **agent-style matching** (~$0.40 per product). A structured matcher brings that to $0.001-$0.03.
- **CJ:** the heavy scenario needs ~112,000 points a day, **over one account's free 50,000**. This is moot until CJ
  licensing is settled.
- **The unknown cost line:** if Kalodata requires an Enterprise API plan (reportedly ~$570 a month), fixed costs rise.
  That matters at 100 customers and is minor at 1,000+.
- **Objection 10 ("API costs make it unattractive") is not supported**, assuming licences can be obtained at roughly current prices.

## D5. Defensibility

| Possible advantage | Status | Evidence |
|---|---|---|
| 1. Proprietary historical demand research | **Real, but thin** | 12 months of retrospective data (Kalodata-licensed, not ours to resell); the research method is replicable |
| 2. Validated predictive features | **Not real yet** | Most of the edge comes from Kalodata's own growth field (Stage B); our own signals are coincident |
| 3. Cross-platform data integration | Real as a prototype; **replicable** | Sell The Trend already integrates CJ plus TikTok Shop data |
| 4. Supplier matching | Real as an agent process (κ 0.90 consistency); **replicable** with any LLM | Stage C |
| 5. Commercial feasibility maths | Real, simple, **replicable**; transparency is the gap | Stage C; no competitor publishes a formula |
| 6. **Historical signal-performance record** | **Plausible later**: the one advantage that **builds with time** and that no competitor offers | Frozen forward tests exist; first scores from Nov 2026 |
| 7. Personalised discovery | Not real | — |
| 8. Alerts / monitoring | Not built | — |
| 9. User feedback loops | Not real (no users) | — |
| 10. Ad-outcome data | Not real (the shop is closed) | — |

**The brief's questions:**
- **Could a competitor reproduce our results with Kalodata alone?** **Largely, yes.** Revenue level plus Kalodata's
  growth field gives most of the predictive edge.
- **Could a spreadsheet?** **Close:** a sort on revenue and Kalodata growth captures much of it. The sourcing filter is
  harder to replicate by hand, but software already does it.
- **Would a competitor with more data easily outperform us?** **Probably.** FastMoss and EchoTik claim 2-4 years of
  history, and Kalodata owns the source.
- **Does our research get more useful over time?** **Only if we keep timestamped predictions and score them.** That
  log is the only compounding asset we've found.

## D6. MVP feature scoring

Rubric: 3 = best (high value / low complexity / low cost / data available / research-supported / fast / differentiated).

| Feature | Value | Complexity | API cost | Data available | Research validity | Build time | Differentiation | Total |
|---|---|---|---|---|---|---|---|---|
| **Evidence log** (timestamped flags + outcomes, public scorecard) | 3 | 3 | 3 | 3 | 3 | 3 | **3** | **21** |
| **Profit / break-even calculator** (SKU-level, stated formula) | 3 | 3 | 3 | 2 | 3 | 3 | 2 | **19** |
| **Signal explanation** (why flagged, confidence, re-entrant vs new) | 2 | 3 | 3 | 3 | 3 | 3 | 2 | **19** |
| Opportunity feed (break-in candidates, ranks 501-1,000) | 2 | 2 | 3 | 3 | 2 (edge depends on one Kalodata field) | 2 | 1 | 15 |
| Supplier matching (with confidence score) | 3 | 1 | 2 | 2 | 2 (consistent, not verified) | 1 | 2 | 13 |
| Watchlist | 2 | 2 | 2 | 3 | 2 | 2 | 1 | 14 |
| Historical demand chart | 2 | 3 | 3 | 2 (12 months) | 3 | 3 | 1 | 17 |
| Alerts (demand **and** margin threshold) | 2 | 2 | 2 | 2 | 1 (lead time not shown) | 2 | 2 | 13 |
| Growth-stage classification | 1 | 2 | 3 | 2 | 1 (lifecycle not validated) | 2 | 1 | 12 |

**What scores best:** the evidence log, transparent margin maths and honest explanations. That is, **trust and
research triage, not prediction.** Stage E turns this into the MVP recommendation, which is conditional on licensing.

## Checkpoint

- **Saved:**
  - this report and the plan (DSI-D-000); DSI-D-001;
  - the competitor and licensing research files;
  - the cost model script and output.
- **Unresolved:**
  - **Kalodata and CJ written permission** (a blocker);
  - Kalodata's current API terms and pricing;
  - TikTok developer terms;
  - CJ's Dropshipping Agreement PDF;
  - **willingness to pay** (no evidence);
  - whether Sell The Trend already auto-matches TikTok products to CJ (not verifiable without an account).
- **Stage E (final verdict, adversarial review, the evidence matrix, risks, validation plan and MVP) is ready.**
  It uses local synthesis only.
