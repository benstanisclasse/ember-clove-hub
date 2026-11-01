# Phase E analysis plan: competition and consumer behaviour (frozen 2026-11-01, before any Phase E computation)

**Labels:**
- Category profiles and review analyses are **descriptive**.
- E2 and E3 are **exploratory tests** (no untouched months).
- E4's review features are frozen as a **forward test**: the review sample was drawn from 2026-09, so there is no
  historical outcome to check them against.

## A. Market structure and saturation (all 28 L1 categories)

**E1. Category competition profile.** Computed from the top-500 panel for each category:

| Measure | Definition |
|---|---|
| `growth` | mean monthly top-500 revenue Jun-Sep 2026 / Feb-May 2026 − 1 (skips the Nov-Dec holiday peak) |
| `top3_share` | revenue share of the 3 biggest shops in the top 500 (mean over months) |
| `hhi` | Herfindahl index of shop shares |
| `shops` | distinct shops in the top 500 (mean over months) |
| `entrant_rate` | new entrants per month / 500 |
| `entrant_ret2` | share of entrants still in the top 500 two months later |
| `asp_median`, `asp_trend` | ASP and its change, Jun-Sep vs Feb-May |

**Classification**, applied in this order. Terciles are across the 27 categories, excluding Pre-Owned:

| Class | Rule |
|---|---|
| Insufficient evidence | Pre-Owned (single-item listings) |
| Highly concentrated | top3_share in the top tercile |
| Potentially underserved | entrant_ret2 in the top tercile **and** top3_share in the bottom tercile |
| Attractive emerging | growth ≥ +10% **and** entrant_ret2 ≥ median |
| Established but competitive | growth between −10% and +10% **and** entrant_ret2 in the bottom tercile |
| Mixed | otherwise |

**E2 (H-D2). Do fragmented categories let new entrants survive more?**
- **Unit:** category × month, entry months 2025-12..2026-07. Each entrant's survival is checked 2 months later.
- **Primary test:** Spearman ρ, across the 27 categories, between mean top3_share and mean entrant_ret2.
- **Secondary:** within-month Spearman (8 months), with the sign checked month by month.
- **Supported** if ρ < 0 with p < 0.05 **and** a negative sign in ≥ 2/3 of months.

**E3 (H-D3). Saturation of near-identical products.**
- **Clustering:** product titles within each category (all products ever in its top 500), TF-IDF on word uni- and
  bigrams (English stop words, digits removed), cosine ≥ 0.70, connected components. A cluster is a "product family" when
  it has ≥ 2 products.
- **Quality check:** 10 random multi-member clusters are printed for review.
- **Features at m, per product:**
  - `fam_shops`: distinct shops of the product's family in the top 500 at m
  - `fam_shops_chg`: change vs m−1
  - `fam_size`: family products in the top 500 at m
  - `fam_asp_rel`: product ASP vs the family median at m
- **Test:** add these features to Phase C's M1 for T1 (ranks 101-500), with the same walk-forward months
  (2026-02..2026-08).
- **Primary metric: ΔAUC** (Phase C showed P@50 sits at its ceiling), with a month-block bootstrap 95% CI. ΔP@50 is reported too.
- **Supported** if the ΔAUC CI excludes 0 and Δ > 0 in ≥ 2/3 of months.
- **Descriptive:** does a rise in family shops precede a fall in family ASP (m → m+1)? Spearman.

## B. Consumer behaviour (Tier 2 niche sample: 499 products, 83,156 reviews; 196 attribute sets; 24 insights)

**E4. Review themes.**
- **Dictionary** (frozen here, case-insensitive substring match on review text):

  | Theme | Terms |
  |---|---|
  | **size_fit** | too small, too big, runs small, runs large, size up, size down, sizing, didn't fit, does not fit, doesn't fit, tight, loose, too short, too long |
  | **quality** | cheap, cheaply, poor quality, flimsy, thin, broke, broken, ripped, tore, fell apart, falling apart, stitching, pilling, defective, faded |
  | **not_as_pictured** | not as pictured, not like the picture, doesn't look like, does not look like, looks nothing like, different from the picture, not what i expected, misleading, false advertising, color is off, not the same color |
  | **shipping** | late, never arrived, never received, shipping, delivery, took forever, arrived damaged, missing |
  | **comfort** | comfortable, comfy, soft, itchy, scratchy, uncomfortable |
  | **value** | worth the money, worth it, great price, overpriced, not worth, waste of money, for the price |
  | **smell** | smell, smells, odor, chemical |
  | **gift** | gift, gifted, for my daughter, for my wife, for my mom, birthday, christmas |
  | **compliments** | compliment, compliments, everyone asked, so many people |

- **Per product:** share of reviews with ≤ 2★ (low_star), mean rating, and each theme's rate. Each rate is computed among
  low-star reviews (complaints) and among 4-5★ reviews (praise).
- **Descriptive comparisons:** by category, and by the product's Phase B trajectory group (A sustained vs B/C/D/U/F).
  The latter is cross-sectional (reviews are recent), so it is labelled descriptive.
- **Forward test (registered now):** among sample products ranked 101-500 in Sep 2026, using **only reviews dated
  ≤ 2026-09-30**:
  - **R1:** Spearman(low_star share, in the Oct-2026 top 500) < 0
  - **R2:** Spearman(not_as_pictured complaint rate, in the Oct-2026 top 500) < 0
  - The features are frozen in `registry/forward_test_reviews_2026-09.csv`.

**E5. Attribute taxonomy (H-E2).** From `product/analysis` attributes and highlights:
- frequency of attribute keys and values by category;
- deterministic flags from highlight keywords:
  - **problem_solving:** control, relief, support, prevent, anti-, waterproof, pain, fix, protect
  - **aesthetic:** elegant, stylish, cute, chic, trendy, aesthetic, flattering
  - **comfort:** comfort, soft, breathable, stretch
  - **convenience:** easy, portable, quick, adjustable, lightweight
- Flags join the R-test file as descriptive covariates.
- **H-E2 proper** (annotation with an inter-rater check) is **not run**: it needs a two-annotator protocol, and LLM
  annotation costs money. The protocol and its cost go in the report.

**E6. Comment insights (24 products).** Qualitative summary only; no statistics (n = 24).
