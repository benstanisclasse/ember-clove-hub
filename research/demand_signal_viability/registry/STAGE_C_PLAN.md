# Stage C plan: commercial feasibility of Kalodata × CJ (frozen 2026-11-01, before any Stage C computation)

**Labels:**
- **Descriptive, current-snapshot evidence.** CJ data comes from 2026-11-01. There is no CJ price history, so
  historical profitability is not reconstructed.
- The match-reliability test (C3) is a **measurement-consistency test, not a correctness test**: neither rater sees photos.

**Cost:**
- No Kalodata credits and no CJ calls.
- C3 uses saved CJ files and one blind rating agent (model tokens only).

## C1. Candidates

**Pool:** every candidate collected in Phases F and H. That is 72 F + 73 new H = **145 unique products**.
- **Ineligible:** 4 ingestibles (F39, F40, H59, H60), reported separately.
- **Collected:** 141, from all 24 eligible categories.

**Two lanes:**
- *validated*: Phase F pool A, ranks 101-500;
- *early-stage*: Phase F pool B plus Phase H, ranks 501-1,000.

## C2. Sourcing funnel (Part 12)

Shares are of the 141 collected, overall and by lane, with Wilson 95% CIs:

| Stage | Definition |
|---|---|
| F1 | any CJ candidate found (match score ≥ 1) |
| F2 | plausible match (score 2, "close substitute") |
| F3 | variant-level sourcing verified: variants and inventory retrieved, ≥ 1 in-stock variant, fulfilment ≥ Medium |
| F4 | viable US shipping: quotes for all 3 zips from an origin with stock, using a method delivering in ≤ 12 days |
| F5 | contribution before ads > 0 at the market price (median in-stock variant) |
| F6 | break-even ROAS ≤ 3.0 |
| F7 | passes all of its lane's gates (Phase G for validated, Phase H for early-stage) |
| F8 | break-even ROAS ≤ 2.0 and target CAC > 0 ("feasible") |
| F9 | photo-verified match **and** sample checked: currently 0 by construction |

**Also reported for F2+:**
- share with US warehouse stock;
- share supplier-shipped;
- CJ cost as % of the TikTok price;
- freight as % of the price;
- median contribution, break-even CAC and target CAC.

## C3. Match reliability: blind re-score

**Sample:**
- 40 candidates with a chosen CJ product: 20 scored 1 and 20 scored 2 by the collectors.
- Seed 20261103, drawn from the 141.

**What the independent agent sees,** for each candidate:
- the Kalodata title, category and price;
- the chosen CJ product's name, description excerpt, material, packing, sell price, and up to 15 variant keys.

**What it doesn't see:** the collector's score, note or reasons.

**What it does:** scores 0/1/2 with the same rubric, including the brand cap.

**Metrics:**
- percent agreement;
- Cohen's κ, unweighted and linear-weighted.

**Read:**

| κ (unweighted) | Reliability of the match score |
|---|---|
| ≥ 0.60 | reliable enough to automate |
| 0.40-0.60 | moderate: needs human review |
| < 0.40 | unreliable |

Disagreements are listed.

## C4. Does demand rank predict sourceability? (Part 11/12)

Spearman correlations, and Wilson rates by tercile, of the Kalodata demand score's within-pool percentile
(T4_M1 for validated, enter_M1 for early-stage) with:
- F2 (close match);
- F7 (passes gates);
- brand cap (score 1 for branded or licensed designs);
- the same three by Sep revenue tercile.

Descriptive, small n.

## C5. Research effort per actionable product (Part 11 "reduces effort")

**Measured** from the saved files and the agent run records:
- CJ calls per candidate, by type;
- documented CJ points per candidate;
- agent wall time and tokens per candidate;
- candidates researched per product that passes all gates, and per "feasible" product.

**Not measured:** human time. No user did this research by hand, so that comparison is a gap, stated as such.

## C6. Capability assessment (Part 11)

**Capabilities:**
1. supply-validated demand signals;
2. margin-aware discovery;
3. fulfilment-aware ranking;
4. supplier availability alerts;
5. demand-to-source matching;
6. opportunity risk.

**Each is rated on Part 11's eight questions:**
1. Technically possible?
2. Implemented?
3. Is the matching reliable? (C3)
4. Does it reduce effort? (C5)
5. Does it improve selection? (C4, plus how many demand picks the gates remove)
6. Is the data current?
7. Obtainable elsewhere? Deferred to Stage D's competitor research, and marked "pending D".
8. Depends on expensive API access?

**Convenience vs predictive advantage:** every capability is labelled one or the other.

## Outputs

- `_work/stage_c_results.json`
- `_work/stage_c_funnel.csv`
- `_work/stage_c_rescore_sample.json`
- `_work/stage_c_rescore_blind.json`
- Report: `C_COMMERCIAL_FEASIBILITY.md`
