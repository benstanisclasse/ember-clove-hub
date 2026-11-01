# Phase C analysis plan (frozen 2026-11-01, before any Phase C model, feature effect or outcome was computed)

Implements `DEFINITIONS_v1.md` §2, §4 and §5 (targets, baselines, metrics) and the forward policy in §7. **Evidence
label:** walk-forward results are *exploratory* (no untouched month, Phase A §5). Only the sealed forward test (§6
below) is confirmatory.

## 1. Universe, targets, cutoffs

- **Universe at cutoff m:** products in a top-500 list (28 L1 categories, `scripts/panel.py`) at month m.
- **Targets:**

  | Target | Universe | Definition |
  |---|---|---|
  | **Primary: T1 retain, h = 1** | ranks 101-500 at m | in the top 500 at m+1 |
  | T2 climb, h = 1 | ranks 101-500 | rank ≤ 100 at m+1 |
  | T4 sustain | ranks 101-500 | in the top 500 at m+1, m+2 and m+3 |

  T3 and T5 (censored growth targets) are deferred: they add censoring complexity without a new question.
- **Feature cutoffs** m = 2025-12 … 2026-08 (2025-12 is the first month with a valid prior month; 2025-10 is never a growth base).
- **Walk-forward test months:**
  - h = 1: 2026-02 … 2026-08 (7 months)
  - T4: 2026-03 … 2026-06 (4 months)
- Each test month t is scored by models trained only on cutoffs ≤ t − h (expanding window), so every training label is
  known by t.

## 2. Features (only information at or before m)

| Feature | Definition |
|---|---|
| rank_pct | rank / 500 |
| log_rev_cut | log(revenue / category cutoff) |
| log_rev | log revenue |
| new_entrant | 1 if absent from the top 500 at m−1 |
| mom_g | log(rev_m / rev_{m−1}), clipped to ±3; 0 for new entrants |
| accel | mom_g(m) − mom_g(m−1), with a missing flag |
| months_top_last3 | count of m−1, m−2, m−3 in the top 500 |
| kalo_g | signed log of Kalodata's momentum field |
| log_asp, asp_rel | ASP and ASP vs category median |
| asp_chg | log ASP change vs m−1, with a missing flag |
| age | months since launch_date, 0..36 |
| video_sh, live_sh | showcase is the reference share |
| log_shop_n | the shop's products in the category top 500 at m |
| prev_riser | in the riser list at m−1 |
| cat_growth | log change in the category's top-500 revenue, m vs m−1 |
| category | one-hot |

Excluded: commission and SKU count (current values only), the AI flag, and anything collected after m.

## 3. Models and baselines (v1 §4)

- **Baselines:**
  - B0: random (expected value = base rate)
  - B1: log_rev_cut (revenue relative to the category; also the dominant feature of the earlier Hub models, so it stands
    in for B6)
  - B2: −rank_pct
  - B3: mom_g, with new entrants last
  - B4: kalo_g
  - B5: months_top_last3 + 0.5 × mom_g
- **The earlier v2 models are not re-implemented in full** (time). Their main signal is B1, and that limitation is stated
  in the report.
- **Models:**
  - M1: L2 logistic regression (C = 0.5) on standardised features + category one-hot
  - M2: HistGradientBoosting (300 iterations, lr 0.05, 31 leaves, l2 = 1, seed 20261031) with category as a categorical feature
- **Metrics per test month:**
  - global P@50 (top 50 over all categories): **the decision metric**
  - mean within-category P@10
  - P@20, AUC, Brier (M1/M2)
- **Support rule (v1 §5):** a model "beats" the best baseline if the month-block bootstrap 95% CI (2,000 resamples of
  test months) of its mean P@50 lift excludes 0 **and** it is ahead in ≥ 2/3 of test months. The best baseline is the
  one with the highest mean P@50, chosen in-sample, which is conservative for the models.

## 4. Hypothesis tests (ablations of M1, primary target T1)

- **Method:** for each group, ΔP@50 = M1 full − M1 without the group, per test month. Supported if the bootstrap CI excludes 0
  and Δ > 0 in ≥ 2/3 months. ΔAUC is also reported. Holm adjustment over the 8 groups (bootstrap one-sided p).
- **Groups:**

  | Hypothesis | Feature group |
  |---|---|
  | H-B1 growth | mom_g |
  | H-B2 Kalodata momentum | kalo_g |
  | H-B3 acceleration | accel + flag |
  | H-B5 age | age |
  | H-B7 price | log_asp, asp_rel, asp_chg + flag |
  | H-B8 channels | video_sh, live_sh |
  | H-D1 category growth | cat_growth |
  | H-D4 shop strength | log_shop_n |

- **H-B4 (non-linearity):** T1 rate by decile of mom_g, pooled over cutoffs, with Wilson 95% CIs. Supported if the top
  decile's retention is below deciles 6-9 with non-overlapping CIs.

## 5. Value of the niche Tier 2 data (owner's question, 2026-11-01)

New hypotheses, registered now. Niche = 601152, 601352, 605248, 953224.

- **H-N1:** for niche T1 (ranks 101-500), adding (a) "was in ranks 501-1,000 at m−1" and (b) growth computed from
  that deep-rank revenue for products absent from the top 500 at m−1 improves M1.
  - Test: ablation ΔP@20 (niche universe ≈ 1,600/month), bootstrap CI.
- **H-N2:** products in ranks 501-1,000 at m can be ranked by their chance of entering the top 500 at m+1.
  - Report the base rate, and the **coverage**: the share of next-month niche entrants that were in 501-1,000 at m, vs in
    a riser list, vs neither.
  - M1 trained within the band (walk-forward), against the baselines B1 (revenue rank within the band) and random.
    Metric: within-category P@20 per month.
- **H-N3:** the shop being in the category's top-100 shop list at m (monthly shop ranks) improves niche T1 M1.
  Test: ablation ΔP@20.
- **Creator ranks, reviews, attributes and images** can't be tested historically: creator lists carry no product ids,
  and the review/attribute sample was drawn from 2026-09 only. They are reserved for the forward test and Phase E.
- **Expansion decision rule (decided in advance):** recommend paying to extend the 501-1,000 band to all categories only
  if **H-N2 coverage ≥ 30% of next-month entrants and band P@20 ≥ 2× the band base rate**, or if **H-N1 is supported**.
  Recommend extending the shop ranks only if H-N3 is supported. Otherwise recommend no expansion.

## 6. Forward-test freeze

- **Done before any 2026-10 data enters `kalodata.db`.** Train M1 and M2 on all labelled cutoffs: h = 1 on cutoffs up to
  2026-08; T4 on cutoffs up to 2026-06.
- Score the **2026-09** universe (all ranks 1-500, all 28 categories) with M1, M2 and every baseline, for T1, T2 and T4.
  Also score the niche 501-1,000 band for entry in 2026-10.
- Write `registry/forward_test_2026-09.csv` and record its SHA-256 in `experiments.jsonl`.
- **The primary forward model is declared in that record**, from walk-forward results only. It is evaluated once, on the
  sealed 2026-10/11/12 pulls, with no refit.
