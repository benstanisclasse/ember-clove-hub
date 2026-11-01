# Phase B: the anatomy of a TikTok winning product (2026-10-31)

**Evidence label: descriptive / exploratory.** The groups are defined using months *after* entry, and no untouched
holdout month exists (Phase A §5). Nothing here is a validated predictor yet. Phase C tests which of these signals
predict forward.

- Plan, frozen before computing: `registry/PHASE_B_PLAN.md`.
- Run record: `registry/experiments.jsonl` EXP-B-001.
- Scripts: `scripts/panel.py`, `scripts/phase_b.py`, `scripts/phase_b_extra.py`.
- Numbers: `_work/phase_b_results.json`, `_work/phase_b_extra.json`.
- Data: 168,000 top-500 product-months, 28 L1 categories, 2025-11..2026-09 (Oct-2025 used for membership only).
- Costs: no credits for the analysis. The niche sections use the Tier 2 data bought on 2026-10-31.

**Deviation from the plan (technical, recorded before results were read):** the three channel shares always sum to 1, so
the first logit could not be estimated (NaN intervals). The showcase share was dropped from the logit only, and the solver
changed to Newton. The registered support test (SMD + cohort signs) is unchanged.

## 1. The basic fact: the top 500 churns hard

Month-to-month moves between rank bands, pooled over 2025-11..2026-08 (140,000 product-months):

| From \ next month | 1-100 | 101-250 | 251-500 | out (>500) |
|---|---|---|---|---|
| **1-100** | **59.6%** | 22.0% | 6.7% | 11.8% |
| **101-250** | 12.3% | 36.9% | 24.9% | 26.0% |
| **251-500** | 2.5% | 11.9% | 32.3% | **53.4%** |

- Staying in the top 100 is stable across months (52-62%; lowest in Dec 2025, after the holidays).
- **After entering the top 500**, the share still there k months later (all entrants, 2025-11..2026-08):

| Entry rank | +1 month | +2 | +3 | +6 |
|---|---|---|---|---|
| 1-100 | 65.8% | 41.8% | 34.0% | 21.7% |
| 101-250 | 51.9% | 33.8% | 26.6% | 18.1% |
| 251-500 | 36.3% | 23.9% | 19.4% | 12.7% |

- 15.5% of product-category trajectories leave the top 500 and come back later (seasonal or relaunched demand).
- **Read:** a top-500 appearance is mostly a short visit. Only about 1 entrant in 5 is still there after six months, even
  among those that entered in the top 100. Selection must reward durability, not a single good month.

## 2. Trajectory groups (DEFINITIONS_v1 §3)

55,498 product × category trajectories:

| Group | n | Share | Months in top 500 (median) | Median rank | Median monthly revenue | ASP (median) | Age at first month (median, months) | Video / live / showcase share |
|---|---|---|---|---|---|---|---|---|
| A Sustained winner | 3,842 | 6.9% | 10 | 103 | $62,866 | $33.55 | 7 | 78% / 17% / 5% |
| E Stable seller | 1,943 | 3.5% | 8 | 281 | $26,998 | $31.40 | 8 | 78% / 18% / 5% |
| B Emerging winner | 2,676 | 4.8% | 4 | 173 | $38,823 | $37.19 | 2 | 69% / 19% / 12% |
| C Temporary viral | 1,803 | 3.2% | 2 | 139 | $47,922 | $36.95 | 1 | 59% / 22% / 18% |
| D Declining | 4,130 | 7.4% | 3 | 296 | $26,561 | $30.89 | 5 | 72% / 18% / 10% |
| U Unclassified | 10,155 | 18.3% | 3 | 328 | $23,624 | $32.76 | 4 | 70% / 17% / 13% |
| F Inconclusive | 30,949 | 55.8% | 1 | 339 | $20,445 | $40.58 | 2 | 52% / 23% / 25% |

Censoring: 54% of A and 44% of E were already present at the window start, and 79% of A run to the end. True lifespans
are longer than measured.

**Categories differ a lot** (share of each category's trajectories):
- **Most durable:** Health (16% A, 0.3% C), Food & Beverages (11% A, 8% E), Baby & Maternity (11% A).
- **Most spiky or one-off:** Toys & Hobbies (5.8% C, 4.5% A), Collectibles (2.3% A, 67% F), Kids' Fashion, Muslim Fashion.
- **Our niche:** Jewelry 10% A / 1.7% C; Womenswear 7.9% A / 2.1% C; Fashion Accessories 8.3% A / 3.0% C; Shoes 5.9% A / 3.9% C.
- Pre-Owned is 94% one-offs (single items).

Any score must therefore be **category-relative**. The base rate of durability in Health is three times that of Toys.

## 3. H-A1: sustained winners vs temporary viral products, at the month they entered

- **Comparison set:** products with an observed entry in 2025-11..2026-04. A = 1,775, C = 1,253.
- **Features:** taken from the entry month only.
- **Registered support rule:** |SMD| ≥ 0.2 **and** the same sign in ≥ 4 of 6 entry cohorts.
- **Odds ratios:** from a logit with category and entry-cohort fixed effects, per 1 SD, Holm-adjusted. Shares are relative
  to the showcase share.

| Entry-month feature | A mean | C mean | SMD | Cohorts same sign | **Supported?** | Odds ratio A vs C [95% CI], p (Holm) |
|---|---|---|---|---|---|---|
| Video share of revenue | 0.775 | 0.608 | **+0.47** | 6/6 | **yes** | 2.03 [1.76, 2.33], <0.001 |
| Showcase (shop-tab) share | 0.072 | 0.174 | **−0.40** | 6/6 | **yes** | reference |
| Rank percentile (higher = worse rank) | 0.425 | 0.331 | **+0.34** | 6/6 | **yes** ⚠ | 1.02 [0.84, 1.24], 1.0 |
| Revenue vs category cutoff (log) | 1.02 | 1.26 | **−0.30** | 6/6 | **yes** ⚠ | 0.73 [0.60, 0.89], 0.011 |
| Live share | 0.153 | 0.218 | **−0.23** | 6/6 | **yes** | 1.34 [1.18, 1.51], <0.001 (vs showcase) |
| Product age (months) | 5.5 | 4.3 | **+0.21** | 5/6 | **yes** | 1.13 [1.04, 1.23], 0.023 |
| Visible in a riser list the month before | 11.4% | 6.3% | +0.18 | 6/6 | no (just under 0.2) | 1.17 [1.07, 1.28], 0.005 |
| ASP relative to category median | +0.15 | +0.01 | +0.15 | 6/6 | no | 2.35 [0.99, 5.60], 0.26 |
| ASP (log) | 3.70 | 3.77 | −0.06 | 6/6 | no | — |
| Shop's other top-500 products (log) | 1.20 | 1.28 | −0.07 | 5/6 | no | 1.00 [0.91, 1.09], 1.0 |
| Kalodata momentum field | 3.85 | 3.68 | +0.05 | 3/6 | no | 0.99 [0.91, 1.08], 1.0 |
| *Growth entry → next month (mechanical)* | *+0.46* | *+0.13* | *+0.33* | *5/6* | *excluded* | — |

How well the two groups can be told apart (leave-one-cohort-out AUC): logit **0.71**, depth-3 tree 0.69, entry rank alone
0.39. Read inverted, a better entry rank points to C.

**What the evidence says (descriptive):**
1. **Video-driven entries last. Showcase- and live-driven entries fade.** This is the strongest and most consistent
   difference (6/6 cohorts, within category). A plausible mechanism: showcase (shop-tab) and live spikes come from
   one-off promotions, mall campaigns or a single live event. Video demand is spread over many viewers and keeps
   working. This is a *correlation*. Category, promotions and seller strategy could all drive both.
2. **Spikes enter big; durable winners enter lower and climb.** C products enter at better ranks and further above the
   cutoff. ⚠ This is partly built into the definitions: C qualifies by peaking at rank ≤ 100 within 2 months, and entering
   high makes that easier. Treat it as weak. The practical point still stands: **"entered the top 500 high" is not a
   reason to expect durability.**
3. **Sustained winners are slightly older at entry** (median 3 vs 1 month since launch). Brand-new products dominate the
   spikes.
4. **Not different:** price, price relative to category, shop size, and Kalodata's momentum field.
5. **Brand vs retailer can't be tested this way.** Kalodata labels about 90% of niche shops as BRAND in every group.

## 4. Secondary: emerging winners (B) vs decliners (D), at entry

B = 1,412, D = 2,265.

- **Supported:** revenue vs category cutoff (B higher, SMD +0.22, 5/6) and **Kalodata's momentum field (B higher, SMD
  +0.22, 6/6; OR 1.27 [1.17, 1.37], p < 0.001)**.
- **Not supported:** price, age, channel mix, shop size, prior visibility.
- **Caveat:** in the logit, rank percentile and revenue-vs-cutoff are nearly collinear, so their very large odds ratios
  (5.7 and 6.4) cancel out and are not interpretable on their own.
- **Read:** the undocumented momentum field carries signal about which entrants keep climbing. That makes H-B2 worth its
  Phase C test, even though the field is not month-over-month growth.

## 5. Lifecycle (§13 of the brief)

- **Products enter the top 500 young.** Median age at entry: C 1 month, B 2, A 3, D 4, E 6. The 90th percentile is 12-18
  months.
- Age at entry and duration are related: spikes are the youngest, stable sellers the oldest.
- The stages "introduction → acceleration → maturity → decline" **can't be inferred reliably** from monthly top-500 data:
  - most products are seen for 1-3 months;
  - the pre-entry climb is invisible outside the niche deep lists;
  - Kalodata's launch date is probably a first-seen date, not a true launch.
- The confirmed daily `revenue_trend` (`need_extra`) is the way to study within-month acceleration. It was not part of
  the approved pulls.

## 6. Niche-only evidence (Womenswear, Shoes, Fashion Accessories, Jewelry)

| Group (niche entrants 2025-11..2026-04) | n | In ranks 501-1,000 the month before entry | In a riser list the month before |
|---|---|---|---|
| A Sustained | 301 | **39.5%** | 4.0% |
| E Stable | 157 | 53.5% | 1.9% |
| D Declining | 366 | 46.7% | 5.5% |
| B Emerging | 190 | 36.8% | 2.6% |
| C Temporary viral | 158 | **20.9%** | 2.5% |

- Durable products were twice as often visible just below the top 500 before entering. A − C = +18.6 points, 95% CI
  roughly +10 to +27.
- **Spikes mostly come from nowhere** (below rank 1,000).
- The riser lists (sorted by Kalodata's field) catch almost none of either group.
- **Implication:** the 501-1,000 band is a cheap early-warning zone. A product that climbs through it is more likely to
  last than one that jumps in from outside.
- Creator, video and live counts (random detail sample, only 230 product-months hit; 4-25 per group): A at its first month
  had a median of 116 creators and 300 videos, vs C's 29 and 86. This is consistent with "video demand spread over many
  creators", but **n is far too small to claim anything**.

## 7. Conventional wisdom vs this data

| Belief | What the data shows |
|---|---|
| "Find products that are exploding right now" | Explosive entries are the most likely to vanish: C enters highest and fades within 2 months |
| "Big launch = winner" | Entering high does not mark durability. Durable winners enter lower and climb |
| "Cheap products win on TikTok" | No price difference between durable and spiky products (ASP $33.55 vs $36.95; SMD −0.06) |
| "Big shops win" | No difference in the shop's other top-500 products |
| "Video is what sells on TikTok" | Supported in a specific form: **video-heavy demand is the durable kind**, while shop-tab/live spikes fade |

## 8. Candidate signals for Phase C (each must earn its place in forward prediction)

1. Video share of revenue, positive. Showcase share, negative.
2. Product age (very new = riskier).
3. Being visible in ranks 501-1,000 before entering (niche; deep lists exist only for the niche).
4. Kalodata's momentum field, for emerging vs declining (H-B2).
5. Entry position. Use it carefully; it is partly definitional here.
6. Category base rates (Health vs Toys differ by 3×).

Commission can't be used (not historical). Price and shop size showed nothing.

## 9. Limitations

- Groups are defined with hindsight, so these are differences between outcomes, not predictions.
- All months were pulled retrospectively on 2026-10-25, so survivorship can't be checked.
- Revenue and channel splits are Kalodata estimates.
- One year only: Nov-Dec holiday effects appear once.
- 56% of trajectories are inconclusive (one-off or censored), so the clean groups are a minority. They are not a
  random sample of all products.
- The deep-rank evidence covers only 4 categories, and the creator counts are tiny.

## 10. Checkpoint

- **Saved:** this report, the frozen plan, EXP-B-000/001 in the registry, scripts, and JSON outputs.
- **Assumptions:** DEFINITIONS_v1 + PHASE_B_PLAN, plus the one recorded technical deviation.
- **Unresolved:**
  - Is the showcase effect promotions (it would need event data)?
  - Does deep-rank visibility predict forward, or only describe?
  - What does the momentum field measure?
- **Phase C (early-winner prediction) is ready.** It runs on local data, uses the frozen targets T1-T6 and baselines
  B0-B6, and ends by freezing September-2026 predictions for the sealed forward test (October pull from 2026-11-02).
