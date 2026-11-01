# Stage D plan: platform business viability (frozen 2026-11-01, before Stage D research)

**Labels:**
- **Competitor capabilities:** web sources only. Each claim is marked "documented by the vendor" or "independently
  verified"; we sign up for nothing, so in practice almost everything is vendor-documented.
- **Licensing:** a reading of public terms. **It is not legal advice.** Anything ambiguous is flagged for written
  clarification or legal review.
- **Cost model:** from the documented price lists, with every assumption labelled.
- **Willingness to pay:** no customer evidence exists. Labelled "unvalidated" unless some is found.

**Cost:**
- No spending.
- No sign-ups, no trials, no forms, no contacting vendors.
- Web research only (public pages).

## D1. Competitors and alternatives (Part 15.3)

**Who:**
- TikTok Shop intelligence tools: Kalodata itself, FastMoss, EchoTik, Shoplus, Tabcut, Pipiads/PiPiSpy and any others found.
- Dropshipping product-research tools: Minea, Sell The Trend, Dropship.io, AutoDS, Zendrop, Ecomhunt and others.
- Supplier platforms with discovery features: CJ's own trending and product search, plus the AutoDS and Zendrop supplier catalogues.

**For each:**
- discovery features;
- demand monitoring and alerts;
- historical analytics;
- any prediction claims (exact wording);
- supplier integration;
- profit calculator;
- transparency about method;
- target customer;
- **current list prices**, with a source URL and access date.

**Key question:** does any tool already offer **demand signals plus supplier matching plus margin** together?

## D2. Data licensing gates (Part 16)

**Read:**
- Kalodata's public Terms of Service and API / Open-Platform terms;
- CJ Dropshipping's Terms of Service and API / developer terms.

**For each permission, answer allowed / prohibited / silent-ambiguous, quoting the clause, at most ~15 words per quote:**
1. Display raw records.
2. Display derived metrics.
3. Provide predictive rankings.
4. Store history.
5. Cache responses.
6. Share across users (multi-tenant).
7. Resell derived intelligence.
8. Build a competing product.
9. Attribution requirements.

**Gate rule:** any "prohibited" or "silent-ambiguous" item among 1, 3, 4, 6 and 7 for Kalodata is a **launch blocker**
until written permission exists.

## D3. Customer segments and problems (Parts 15.1-15.2)

**Method:** map each segment's likely needs to what Stages B-C actually showed the system can do. Evidence classes:
- **demonstrated:** shown in Stages B-C;
- **plausible:** follows from them, untested;
- **unsupported.**

No willingness to pay is inferred from competitor prices.

## D4. Unit economics (Part 15.5)

**Data costs:**
- Kalodata: documented credits per call, at **$0.10 per credit**. That was our observed rate: 564.1 credits ≈ $56,
  per the audit. To be re-checked against the public pricing page if visible.
- CJ: API points are free. The quota is per account, which is a **licence question** for SaaS.
- **Shared collection:** one pipeline serves every customer.
  - **Scenarios:** refresh monthly, weekly or daily.
  - **Universe:** 28 categories × ranks 1-1,000 (10 pages) plus risers 1-200 (2 pages) plus top videos (3 pages).
  - **Enrichment:** product detail and images for the top N candidates each refresh, with N = 300 or 1,000.
- **Per-customer costs:**
  - watchlist detail refreshes: 0.1 credit per product per refresh;
  - CJ matching: LLM tokens per match. Measured at ~60k tokens per candidate in agent form. Scenario: a structured
    matcher at ~8k tokens per candidate, priced at current list prices for Claude models (from the official pricing
    reference);
  - support time, as an assumption.
- **Fixed costs**, as labelled assumptions: hosting, database, monitoring.
- **Scales:** 100, 1,000 and 10,000 active customers, combined with low / mid / high usage.
- **Reported:** monthly cost, cost per customer, and the price needed for a 70% gross margin.

## D5. Defensibility (Part 14)

Each of the brief's 10 advantages is rated:
- **real now** (with evidence);
- **plausible later**;
- **not real.**

The questions are answered with Stage B and C evidence: could Kalodata alone reproduce it, could a spreadsheet, and so on.

## D6. MVP requirements (Part 18)

**Feature scoring** for the candidate MVP features (opportunity feed, signal explanation, demand chart, stage
classification, supplier matching, profit calculator, alerts, watchlist, evidence view):
- customer value;
- technical complexity;
- API cost;
- data availability;
- research validity (from B and C);
- build time;
- differentiation (from D1).

Scored 1-3 on an explicit rubric. The full MVP recommendation follows in Stage E.

## Outputs

- `D_PLATFORM_BUSINESS_VIABILITY.md`
- `_work/stage_d_competitors.md`
- `_work/stage_d_licensing.md`
- `_work/stage_d_cost_model.json`
