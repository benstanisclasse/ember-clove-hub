# Unresolved risks: Demand Signal Intelligence (2026-11-01)

**Severity scale:** H = could invalidate the product, M = changes the design or economics, L = manageable.
**"Blocks?"** means it would prevent commercial deployment as things stand.

| # | Risk | Severity | Likelihood | Conclusions it affects | Mitigation | Data or action needed | Blocks? |
|---|---|---|---|---|---|---|---|
| R1 | **Kalodata licence** forbids resale, third-party provision or derived products | H | High (2023 terms say so; current terms unreadable) | Everything commercial | Ask for written permission; explore a customer-supplied-key design (each user's own Kalodata key) | Send the drafted questions (owner approval) | **Yes** |
| R2 | **CJ licence**: personal-use account, off-platform display needs permission, API sees own account only | H | High | Supplier matching, margins | Ask CJ; customer-connected CJ accounts; partner programme if one exists | Send the drafted questions; read CJ's Dropshipping Agreement PDF | **Yes** |
| R3 | **Kalodata growth field leaks post-month information** | H | Unknown (indirect evidence: tracks next-month growth) | Size of the predictive edge (Stage B; Phases C/H) | Treat the edge as +2.7 pts until cleared | Sealed October pull now vs a re-pull ~4 weeks later; forward scoring | No, but it removes the main quantitative claim |
| R4 | **No lead-time advantage**: early detection = growth filter | H | High (measured) | Core value proposition | Pivot to triage and precision positioning | Weekly-granularity cohorts (custom date windows; credits) to test sub-monthly lead | No; it changes the product |
| R5 | **Selection bias**: only ranks 1-1,000 and risers visible; 59% of entrants invisible beforehand | M | Certain | Recall, "finds products nobody knows" claims | Never claim market-wide coverage | Pull ranks 1,001-2,000 for a sample of categories (credits) | No |
| R6 | **Retrospective data**: history downloaded Oct 2026; Kalodata revision policy unknown | M | Certain | All backtests | Forward-only validation from now | Ask Kalodata about revisions; monthly re-pulls | No |
| R7 | **Short history** (12 months, first partial; one season) | M | Certain | Temporal generalisation, seasonality | Accumulate forward cohorts; trial a 2-4-year provider | Second provider trial (free trials need owner approval) | No |
| R8 | **Estimated revenue**: Kalodata says not to rely on it where precision matters | M | Certain | Every metric | Rank-based use only; show uncertainty | Cross-check two vendors on a sample | No |
| R9 | **Competitors** already offer the bundle (Sell The Trend, AutoDS, Dropship.io) | H | High | Differentiation, pricing | Compete on published evidence and transparency | Hands-on review of Sell The Trend (a trial needs owner approval) | No; it limits the upside |
| R10 | **No willingness-to-pay evidence** | H | Unknown | The whole business | Landing page plus interviews before building | Owner-approved test (~$200-300 of ads) | Not technically, but it decides GO |
| R11 | **TikTok Shop demand may not transfer to Shopify / independent-store ads** | H | Unknown | Commercial usefulness | Position for TikTok Shop sellers too; test with paid traffic | Small paid test on a store (shop closed; owner decision) | No |
| R12 | **Unverified matches**: no photos or samples; supplier quality unknown | M | Medium | Sourcing claims | Show match confidence; require photo comparison | Kalodata images (0.01 credit each) and samples (money) | No |
| R13 | **Duties on China-origin parcels unknown** (CJ quotes are DDU) | M | Medium | Margin maths | Show duty scenarios | Duty and tariff check per category | No |
| R14 | **Matching only runs as an agent process**, with high token use (~60k per product) | M | Certain | Technical feasibility, cost | Build a structured matcher (~8k tokens) and test agreement against agent scores | Engineering | No |
| R15 | **Data-vendor dependency**: Kalodata is the source and a potential competitor; API pricing or eligibility could change | M | Medium | Economics, continuity | Abstract the data layer; second provider | Written API pricing | No |
| R16 | **Ranking instability** (2-9% of flags repeat month to month) may confuse users | L | Certain | UX, trust | Explain "why now"; track flag history | — | No |
| R17 | **Weak signals exposed by a public scorecard** | M | Medium | Marketing | Accept it: the scorecard *is* the differentiator, misses included | Forward data | No |
| R18 | **Compliance**: children's, battery and safety-critical products flagged by demand models | M | Medium | Recommendations | Keep the risk-flag gates; never recommend without compliance checks | — | No |
| R19 | **CJ API suspended after 30 days with no transactions** | L | Medium | Data continuity | Keep minimal transactions, or use customer accounts | — | No |
