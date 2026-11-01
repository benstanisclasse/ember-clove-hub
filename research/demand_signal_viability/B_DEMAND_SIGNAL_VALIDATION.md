# Stage B: demand-signal validation (2026-11-01)

**Evidence label:** predictive, **exploratory**. Every month was already used by earlier research (Stage A).

**Sources:**
- Plan, frozen before computing: `registry/STAGE_B_PLAN.md` (DSI-B-000).
- Results and deviations: DSI-B-001.
- Scripts: `scripts/stage_b.py` (registered analysis); `stage_b_posthoc.py` and `stage_b_sensitivity.py` (post-hoc,
  labelled as such).
- Outputs: `_work/stage_b_*`.

**Cost:** no credits, no CJ calls, read-only.

## The short answer

1. **Engine vs simple rules.** On the registered test, the combined engine flags products just below the top 500 that
   break in next month at **39.7%**, vs **28.0%** for ranking by revenue, and much better than growth filters or
   Kalodata's riser list. That passes the pre-set materiality bar. **But it is no better than the existing break-in
   model**, and the new signal families add nothing.
2. **Almost all of that edge comes from one input: Kalodata's own `revenue_growth_rate`.**
   - Its time window is undocumented, and it tracks the **next** month's growth more than its own month's.
   - **Without it, the engine beats revenue ranking by only +2.7 points** (break-in) and +1.2 points (staying 3 months),
     **below the materiality bar.**
   - Whether that input is a legitimate early signal or post-month information can only be settled by the forward test.
3. **Lead time is essentially absent.**
   - At 20 alerts per category per month, every method, the engine included, flags **only 1.5-3% of first-time
     top-500 entrants even one month ahead**.
   - The lead is almost always exactly 1 month.
   - When the engine and a plain growth filter both catch a product, they catch it **in the same month 85% of the time**.
4. **57% of the engine's correct calls are products that were bestsellers before** and are coming back, not new demand.

**Verdict for this stage:**

| Question | Answer |
|---|---|
| Statistically detectable early-demand signal? | **Yes, but small** without the suspect input |
| Lead-time advantage? | **Not demonstrated** |
| Advantage independent of a Kalodata field anyone can see? | **No evidence yet** |

## B1. The universe, and how much of the market it can see

- **Who is in it:** products outside their category's top 500 but visible in ranks 501-1,000 or on Kalodata's riser list (1-200).
- **Size:** 206,409 product-months, about 18,800 a month:
  - 149,392 band only
  - 52,901 risers only
  - 4,116 both
- **Coverage ceiling:** only **40.9%** of each month's ~5,000 new top-500 entrants (range 38-44%) were in this universe
  the month before. The rest come from outside anything we download.

  **No method here can find them, and that is a data limit, not a model failure.**

## B2-B5. Discovery methods at equal alert budgets

**Set-up:** walk-forward, 28 categories, 20 alerts per category per month (560 a month).

**S1: enters the top 500 next month** (base rate 10.9%, 8 test months):

| Method | catP@10 | **catP@20** | P@100 | Recall@20 | False positives per hit | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|
| A Revenue | 28.2% | **28.0%** | 25.8% | 7.7% | 2.6 | 0.717 | 0.207 |
| B Growth | 16.6% | 19.1% | 13.5% | 5.2% | 4.3 | 0.646 | 0.153 |
| C Kalodata riser list | 10.6% | **8.7%** (below base) | 13.9% | 2.4% | 10.9 | 0.489 | 0.100 |
| D Momentum (revenue + growth) | 17.5% | 19.9% | 15.1% | 5.5% | 4.1 | 0.643 | 0.166 |
| E Existing break-in model | 41.7% | 39.6% | 48.4% | 10.9% | 1.5 | 0.780 | 0.286 |
| **F Combined engine** (logit, chosen over boosted trees on Jan-Apr) | 41.4% | **39.7%** | 47.9% | 10.9% | 1.5 | 0.779 | 0.284 |

**F minus each rule:**
- vs revenue: **+11.6 pts** [+10.2, +13.1], 8/8 months, Holm p < 0.001. **Material** by the plan's rule (≥ 5 pts).
- vs growth: +20.5. vs riser list: +31.0. vs momentum: +19.8.
- **vs the existing model: +0.07 pts** [−0.6, +0.7]: **no difference.**
- Late months only (May-Aug, after F's selection): +12.7 vs revenue.

**S2: enters and stays 3 months** (base rate 3.4%, test months Mar-Jun):

| Method | catP@20 | Recall@20 | False positives per hit |
|---|---|---|---|
| A Revenue | 9.7% | 8.5% | 9.5 |
| B Growth | 5.5% | 4.8% | 20.1 |
| C Kalodata risers | 2.5% | 2.2% | 40.0 |
| D Momentum | 6.2% | 5.4% | 16.7 |
| E Existing model | 13.8% | 12.1% | 6.3 |
| **F Engine** | **14.1%** | 12.3% | 6.4 |

F minus revenue on S2: **+4.4 pts** [+2.8, +5.7], 4/4 months. Material by the plan (≥ 2 pts).

**Other properties of F (S1):**
- **Calibration** is good: Brier 0.089 vs 0.097 for the base rate; slope 0.92.
- **Ahead of revenue in 28/28 categories** (by +4 to +22 pts) and in every month.
- **Rankings are very unstable:**
  - month-to-month score correlation for the same products is only 0.05-0.19;
  - of last month's top-20 flags still in the universe, **only 2-9% are flagged again.**
  - A user would see an almost entirely new list every month.

### Ablations: which signal families matter (S1, removing one family at a time)

| Family removed | ΔAUC | ΔcatP@20 | Contributes? |
|---|---|---|---|
| Transaction level (revenue vs cutoff, units, band rank) | −0.050 | −9.4 pts | **Yes** |
| Momentum (our growth, acceleration, Kalodata growth) | −0.035 | −8.8 pts | **Yes** (mostly Kalodata growth; see B6) |
| Channel (video/live share) | −0.002 | −1.4 pts | Barely |
| Riser list | 0.000 | +0.2 | No |
| Price | 0.000 | 0.0 | No |
| Lifecycle (age, fell from top 500) | 0.000 | 0.0 | No |
| Category growth | +0.001 | 0.0 | No |

## B6. Which signals are leading?

**Test:** each signal's added value over revenue level and band rank, walk-forward.

| Signal | Added AUC, S1 [95% CI] | Months positive | Added AUC, S2 | Same-month link to growth (ρ) | Classification |
|---|---|---|---|---|---|
| **Kalodata growth rate** | **+0.041** [0.035, 0.046] | 8/8 | +0.028 | 0.21 | **Leading, but suspect** (see below) |
| On Kalodata's riser list | +0.0035 [0.002, 0.005] | 8/8 | +0.003 | 0.05 | Leading, negligible |
| Video share of revenue | +0.001 [−0.000, 0.002] | 6/8 | **+0.0065** [0.004, 0.009] | 0.03 | No lead for entry; small for **staying** |
| Our month-over-month growth | +0.001 [−0.001, 0.003] | 6/8 | −0.003 | — | **Coincident** (nothing beyond level) |
| Acceleration | −0.000 | 1/8 | −0.002 | 0.53 | **Coincident** |
| Fell out of the top 500 last month | −0.000 | 1/8 | +0.002 | −0.67 | **Coincident** |
| Units, 2 months of growth, previous riser, live share, price, price change, age, category growth | ≈ 0 | — | ≈ 0 | — | No detectable lead |

**Not testable, because there is no per-product monthly history:**
- video counts, creator counts, creator concentration, new creators, views per video;
- ad share of video revenue;
- reviews, complaints and attributes;
- CJ availability, cost, stock and margin.

**Why this matters:** our own growth measures carry **no information about next month beyond the current revenue level.**
- Growth, acceleration and momentum are **coincident.** They describe the rise you can already see.
- **The only leading information comes from Kalodata's own growth field.**

### Is Kalodata's growth field a leak? (post-hoc check)

**What we measured**, on 122,862 product-months:
- Kalodata's growth field correlates **ρ 0.235** with the product's own month-over-month growth, and **ρ 0.262** with
  **next** month's growth.
- After removing the own-month part, it still correlates **0.31** with next month.
- It is not a fixed current value: it varies by month for 99.9% of products.

**Two readings fit:**
- **(a) legitimate:** Kalodata measures within-month momentum, for example the last weeks against earlier ones, which
  genuinely leads;
- **(b) leakage:** the value for a past month was computed with data from after that month, when we downloaded it in October.

**We can't tell which.**

**Sensitivity**, the engine **without** Kalodata's growth field:

| | catP@20, S1 | vs revenue | catP@20, S2 | vs revenue |
|---|---|---|---|---|
| F with Kalodata growth | 39.7% | +11.6 pts | 14.1% | +4.4 pts |
| **F without it** | **30.7%** | **+2.7 pts** [+1.6, +3.6] | **10.9%** | **+1.2 pts** [+0.1, +2.3] |
| Existing break-in model without it | 27.8% | −0.2 pts | 10.6% | +0.9 pts |

Without the suspect field, the edge is statistically detectable but **below the materiality bar** (5 and 2 pts).

**This also applies to Phase C's break-in results** (H-N2/H-N2b/H-H2), which use the same field.

**How to settle it:**
1. Use the sealed October pull (from 2026-11-02). Its values are as they stood **2 days** after the month ended.
2. Re-pull October about 4 weeks later and compare the two.
3. Score the frozen September forecasts on October outcomes: those forecasts used September values pulled weeks after
   the month ended.

## B7. Lead time

**Successes:** 30,243 first-ever top-500 entries in a category, February-September 2026. Of the 23,420 that can be
followed for 3 months, 25% stayed.

**Method:** each method's flags, Jan-Aug 2026, at the same budget.

| Method (20 alerts/category/month) | Share of all successes flagged ≥ 1 month ahead | ≥ 2 months ahead | Among successes visible beforehand | Median lead when flagged | Alerts per success caught |
|---|---|---|---|---|---|
| A Revenue | 2.4% | 0.6% | 6.8% | 1 month | 6.3 |
| B Growth | 2.9% | **1.1%** | 8.4% | 1 month | 5.1 |
| C Kalodata risers | 1.6% | 0.5% | 4.7% | 1 month | 9.2 |
| D Momentum | 3.0% | 1.1% | 8.7% | 1 month | 5.0 |
| E Existing model | 3.0% | 0.5% | 8.8% | 1 month | 4.9 |
| **F Engine** | **3.0%** | **0.5%** | **8.7%** | **1 month** | **4.9** |

**F vs the growth filter, among successes both caught (top 20):**
- same month in 118 of 138;
- F earlier in 6, later in 14;
- average extra lead **−0.04 months**.

F caught 768 that growth missed, and growth caught 734 that F missed.

**F vs Kalodata's riser list:** same month in 114 of 118.

**Reading:**
- **No method gives a meaningful head start.** Detection is 1 month ahead, for a few percent of eventual entrants.
- A plain growth filter catches about as many as the engine at the same alert volume, and **slightly more of them
  2 months early.**
- The engine's precision advantage (B5) is not an earliness advantage.

### Where the engine's hits come from (post-hoc)

At 20 per category per month, Jan-Aug, out of 4,480 flags:

| Method | Correct calls | Share that are returning ex-bestsellers | Correct calls on first-time entrants, per month |
|---|---|---|---|
| A Revenue | 1,256 | 58% | 66.5 |
| B Growth | 857 | 34% | 70.4 |
| D Momentum | 891 | 34% | 74.0 |
| E Existing model | 1,774 | 56% | 97.1 |
| **F Engine** | 1,777 | **57%** | **94.8** |
| F without Kalodata growth (sensitivity) | — | — | 93.8 |

**Reading:**
- **More than half of the engine's correct calls are products that were already in a top 500 earlier,** coming back
  (a third of the universe by mid-2026).
- On genuinely new entrants, it finds about **35% more per month than a growth filter** (95 vs 70). That holds even
  without the suspect field: 94 vs 70. **This is the most defensible positive finding of the stage.**
- **For entrants that also stay 3 months**, the version without the suspect field finds **fewer** first-time ones
  than revenue ranking: 14.8 vs 20.8 a month.

## B8. Promotion vs genuine demand (with the signals we have)

Among products that broke in, the share that stayed 3 months:

| Group | Stayed 3 months | 95% CI | n |
|---|---|---|---|
| Growth came with a price cut of ≥ 10% | 34.4% | [31.8, 37.2] | 1,191 |
| No price cut | 35.3% | [34.2, 36.5] | 6,556 |
| Video share of revenue: low / mid / high tercile | 27.4% / 35.0% / 33.2% | ±1.2 | ~5,700 each |
| Live share ≥ 50% | 28.4% | [26.6, 30.2] | 2,396 |
| Live share < 50% | 32.4% | [31.7, 33.2] | 14,696 |

**Reading:**
- **Discount-driven growth holds no worse than other growth.** Price cuts don't explain spikes.
- **Livestream-driven and showcase-driven entries fade more.** Video-driven ones last better, as in Phase B.
- **The question the brief really asks, whether rising creator and video promotion precedes real demand, can't be
  tested:** there is no per-product promotion history.

## What Stage B means for the platform idea

- **Supported:**
  - At an equal alert budget, a model on ranks 501-1,000 picks next-month break-ins clearly better than revenue, growth
    or Kalodata's riser list.
  - Its probabilities are well calibrated.
  - It finds more genuinely new entrants than a growth filter.
- **Not supported:**
  - **"Earlier than conventional discovery":** the lead is 1 month, for 1.5-3% of entrants, the same as a growth filter.
  - **Signals beyond Kalodata's own fields:** ours are coincident.
  - **Value from video, creator or promotion signals:** untestable.
- **At risk:** the size of the advantage depends on a Kalodata field that may contain post-month information.
- **Structural limit:** we can only ever see about 41% of next month's entrants, and only one month before.
  True early discovery would need a broader or more frequent data feed. That costs more Kalodata credits (Stage D)
  and needs prospective collection (Stage E).

## Checkpoint

- **Saved:**
  - this report and the plan (DSI-B-000); DSI-B-001;
  - scripts and outputs: the signal inventory CSV, the per-success lead-time CSV, results, post-hoc checks and sensitivity.
- **Deviations** (DSI-B-001):
  - **S2 test months:** 2026-03..06 instead of 01..06. Training needs months ≤ t−3, and the universe starts 2025-11.
  - **Lead-time flags:** all methods use the walk-forward test months 2026-01..08 (the plan allowed 2025-11),
    so every method has the same window.
  - **Riser-only products:** the existing model's band-rank feature was filled as "beyond rank 1,000" for them.
  - **Post-hoc analyses:** the precision-source split, the Kalodata-growth leakage check and the without-Kalodata-growth
    sensitivity were all added after the registered results.
- **Unresolved:**
  - whether Kalodata's growth field is legitimate (needs the sealed October pull plus a later re-pull);
  - promotion-signal history;
  - a broader universe beyond rank 1,000.
- **Stage C (commercial feasibility) is ready.** It uses the Phase F/H CJ data that already exists, so it needs no new spending.
