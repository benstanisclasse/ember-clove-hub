# Phase C: early-winner prediction study (2026-11-01)

**Evidence labels:**
- Walk-forward results are **exploratory**, because every month was used by earlier research (Phase A §5).
- The **replication on 24 new categories** (§4) is out-of-sample in categories, not in time.
- The **sealed forward test** (§6) is the only confirmatory test. Its predictions are frozen and committed; the outcomes
  arrive with the October 2026 pull.

Sources:
- Plan, frozen before computing: `registry/PHASE_C_PLAN.md` (EXP-C-000).
- Results: EXP-C-001..004 in `registry/experiments.jsonl`.
- Scripts: `scripts/features.py`, `phase_c.py`, `phase_c_niche.py`, `phase_c_band.py`, `phase_c_freeze.py`.
- Numbers: `_work/phase_c_results.json`, `phase_c_niche.json`, `phase_c_band_check.json`, `phase_c_band_replicate.json`.

Scope: **all 28 L1 categories**. Universe: products ranked 101-500 in their category at month m (11,200 per month).
Training is walk-forward: each test month is scored by a model trained only on months whose outcome was already known.

## 1. Can we predict which products keep selling? Yes, clearly better than simple rules

Mean over the test months. P@50 = share of the 50 top-scored products that achieved the target.

| Target | Months | Base rate | Best simple rule | **Logit (M1)** | Boosted trees (M2) | Lift of M1 over best rule [95% CI] | Verdict |
|---|---|---|---|---|---|---|---|
| **T1: still in the top 500 next month** (primary) | 7 (Feb-Aug) | 58% | revenue vs category cutoff: 85% | **97%** (AUC 0.80) | 98% (AUC 0.82) | **+12.6 pts [+6, +22]**, ahead 7/7 | **beats the baselines** |
| T4: in the top 500 for each of the next 3 months | 4 (Mar-Jun) | 32% | rank: 62% | **92%** (AUC 0.78) | 93% | **+30 pts [+21, +37]**, ahead 4/4 | **beats the baselines** |
| T2: climbs into the top 100 next month | 7 | 6% | rank: 33% | 39% (AUC 0.81) | 36% | +6.6 pts [−1.7, +14.3], ahead 5/7 | **not better than rank** |

Other baselines for T1, P@50:
- rank 84%
- computed month-over-month growth 83%
- 3-month momentum 82%
- Kalodata's momentum field 59% (no better than random, 59%)

The top-scored lists are dominated by products that have **already been in the top 500 for several months and sit well
above the category cutoff**. The model mostly formalises "established and holding" better than any single number does.
That is useful for **avoiding fading products**. It is not a way to find new products: predicting a *climb* into the
top 100 is no better than sorting by rank.

Calibration (Brier): 0.18 for T1, 0.05 for T2, 0.17 for T4. The earlier Hub models were overconfident above about 20%.
A reliability check of these probabilities belongs to the forward test.

## 2. Which signals carry their own weight? (registered ablations, T1)

Each feature group was removed from M1 in turn. The registered decision metric is the change in P@50. **No group passes.**
P@50 is near its ceiling (97%), so this metric can barely move: a weakness of the plan, recorded and not re-scored. The
change in AUC is the secondary measure:

| Hypothesis (feature group) | ΔP@50 [95% CI] | ΔAUC [95% CI] | Registered verdict |
|---|---|---|---|
| H-B2 Kalodata momentum field | −0.6 pts [−3.4, +2.0] | **+0.031 [+0.026, +0.035]** | not supported (P@50) |
| H-B8 channel mix (video/live share) | +0.3 [−0.6, +1.1] | +0.004 [+0.003, +0.006] | not supported |
| H-B5 product age | +0.6 [−2.0, +2.9] | +0.001 [−0.000, +0.002] | not supported |
| H-B1 computed MoM growth | −0.3 [−1.1, +0.9] | +0.0004 [+0.0001, +0.0007] | not supported |
| H-B3 growth acceleration | −0.3 [−0.9, 0.0] | −0.0003 | not supported |
| H-B7 price (level, relative, change) | −0.9 [−2.0, 0.0] | +0.0002 | not supported |
| H-D1 category growth | 0.0 | 0.000 | not supported |
| H-D4 shop strength | −0.3 [−0.9, 0.0] | +0.0002 | not supported |

**Read:**
- **Kalodata's undocumented momentum field is the one extra signal with a clear, consistent contribution** to ranking quality
  (AUC +0.03). On its own it ranks no better than random. It is useful only combined with rank and history, which fits
  Phase B (it separated emerging from declining entrants).
- Channel mix adds a little.
- Price, acceleration, category growth and shop size add nothing once rank and history are known.

**H-B4 (does very fast growth reverse?): not supported.** Next-month retention *rises* steadily with growth, from 52%
in the lowest growth decile to 77% in the highest. Among products already in the top 500, fast growers do not fall back
the next month. New entrants (no prior month) are retained only 42% of the time.

## 3. Value of the niche data already bought (owner's question)

Pre-registered decision rule (PHASE_C_PLAN §5): extend ranks 501-1,000 to all categories if H-N2 coverage ≥ 30% and
precision ≥ 2× the base rate, or if H-N1 is supported. Extend the shop ranks only if H-N3 is supported.

| Test (Womenswear, Shoes, Fashion Accessories, Jewelry) | Result | Verdict |
|---|---|---|
| **H-N2: break-in from ranks 501-1,000** | **44.4%** of next-month top-500 entrants were in 501-1,000 the month before (riser lists: 3.5%). M1's top 20 per category broke in at **43.0%**, against a 15.1% base rate (**2.86×**) and 26.1% for revenue rank. Lift +17.0 pts [+13.2, +20.5], ahead 7/7 | **valuable** |
| H-N1: deep history added to top-500 retention | ΔP@20 −0.7 pts [−2.1, 0.0], 0/7 months | no value |
| H-N3: shop in the category's top-100 shops | ΔP@20 −0.7 pts [−2.1, 0.0], 0/7 months (71% of products are in top-100 shops anyway) | no value |

The rule therefore said **extend ranks 501-1,000 to all categories, but not the shop or creator ranks**. Reviews,
attributes and images can't be tested on history: the sample was drawn from 2026-09 only. They stay reserved for the
forward test and Phase E.

## 4. Replication in the other 24 categories (H-N2b, registered before the download)

The owner had said to download the rest if the niche data showed value. Ranks 501-1,000 were pulled for the 24 other
categories × 12 months: 1,428 of 1,440 pages had data (Pre-Owned runs out), and the balance fell by **142.8 credits**.
The identical code (`phase_c_band.py`) was first re-run on the niche and reproduced H-N2 exactly. It then ran once on the
new categories:

| Criterion (registered) | Needed | Result | |
|---|---|---|---|
| Coverage: entrants that were in 501-1,000 the month before | ≥ 30% | **37.7%** (riser lists 3.9%) | ✅ |
| M1 top-20 break-in rate vs base | ≥ 2× | **38.8% vs 13.8% = 2.82×** | ✅ |
| Lift over revenue rank (28.0%) | CI excludes 0 | **+10.8 pts [+9.4, +12.6]**, ahead 7/7 | ✅ |

**The early-warning band works across categories.** Ranks 501-1,000 hold about 4 in 10 of next month's new top-500
products, and a simple model picks break-ins at almost 3× the base rate. Base rates are similar across categories
(11-16%), except Pre-Owned (2%).

## 5. Answer to the Phase C question

> Which measurable signals help identify promising products before their strongest observed performance?

1. **Being in ranks 501-1,000 at all.** This is the only place we can see about 40% of future entrants a month early.
   Kalodata's riser lists catch under 4%.
2. **Within that band:** revenue relative to the category cutoff, having been seen the month before (and the change
   since), Kalodata's momentum field, channel mix and age, combined. Together they beat revenue rank by 11-17 points.
3. **For products already in the top 500:** rank, revenue vs cutoff and months held, plus Kalodata's momentum field,
   predict who holds for 1-3 months far better than any single rule. Price, shop size, category growth and acceleration
   add nothing.
4. **Not predictable here:** which mid-list products jump into the top 100 next month. The model is no better than rank.

None of this says a product is *profitable for us*. That is Phase F (CJ cost, freight, margin) and, eventually, our own ad
results (Level 3).

## 6. Forward test (frozen, confirmatory)

| Freeze | File (registry/) | SHA-256 | Rows | Primary comparison |
|---|---|---|---|---|
| EXP-C-002 | `forward_test_2026-09.csv` | `08b386a9…2ea5` | 14,000 (11,200 in the primary universe) | T1: M1 vs B1 P@50 on 2026-10 outcomes; T2 and T4 secondary |
| EXP-C-004 | `forward_test_band_2026-09.csv` | `03001dfe…547e` | 14,000 (ranks 501-1,000, 28 categories) | Entry into the 2026-10 top 500: M1 vs B1, within-category P@20 |

Both were made while `kalodata.db` held nothing after 2026-09, and the first was committed (`469362a`) before any
October data existed. Next steps:
- Run `scripts/kalodata_gaps.py forward --month 2026-10` from 2026-11-02 (sealed, not loaded into the database).
- Score both files once.
- Nov and Dec complete T4.
- **To keep the band monitor going, the monthly pull should also fetch ranks 501-1,000 for all 28 categories**
  (+14 credits/month, about 43/month in total). That needs owner approval.

## 7. Limitations

- **Exploratory walk-forward:** the months were already used by earlier work.
- **One year:** seasonality is seen once.
- **All history pulled retrospectively** on 2026-10-25 and 2026-11-01, so there is survivorship risk.
- **P@50 ceiling:** the registered ablation metric was too blunt for T1. ΔAUC is reported as secondary only.
- **Full earlier v2 models not re-implemented:** their main signal (revenue vs cutoff, B1) is the comparator.
- **Two-stage approval of the deep pull:** the expansion followed a rule fixed in advance, and the replication criteria
  were registered before the download.

## 8. Checkpoint

- **Saved:** this report, 4 experiment records, 2 frozen forward files, scripts and outputs.
- **Spend this phase:** 142.8 credits (the 24-category deep pull, including the 0.5-credit test). Balance **253.29**.
- **Unresolved:**
  - forward-test outcomes (October pull)
  - calibration
  - whether the monthly pull should include ranks 501-1,000 going forward
- **Phase D (video and advertising research) is ready.** It runs on local data: the video lists, 93 product-video sets,
  and the 185-video feature sample.
