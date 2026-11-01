# Prospective validation plan (frozen 2026-11-01, before any forward outcome exists)

**Purpose:** settle, on data collected *before* outcomes are known, the questions history can't:
1. whether the break-in engine's precision advantage is real;
2. whether Kalodata's growth field is legitimate;
3. whether any lead time exists at finer granularity;
4. whether flagged products are sourceable at the time they're flagged.

These thresholds are fixed **now**. The first forward data (the sealed October 2026 pull) does not exist yet.

## 1. Monthly prediction cycle

**On day 2 of each month M+1, for month M:**
1. **Sealed pull:** run `python -I scripts/kalodata_gaps.py forward --month <M> --max-credits 30`.
   - Contents: top 500, risers and top videos for all 29 categories. **Add ranks 501-1,000 (pages 6-10)**, which is
     needed for the break-in universe; it costs about +14 credits a month and needs owner approval.
   - Saved under `research/kalodata/sealed/<M>/`, with SHA-256 hashes, and **never loaded into `kalodata.db`** before scoring.
2. **Score.** The universe is products outside the top 500 in ranks 501-1,000 or on the riser list. Every method runs:
   - A Revenue
   - B Growth
   - C Kalodata risers
   - D Momentum
   - E Existing model
   - F Engine (with Kalodata growth)
   - **F′ Engine without Kalodata growth**

   The models are trained only on data available at M (the frozen code in `stage_b.py`, versioned by commit hash).
3. **Lock.** For each method, save:
   - the top 20 per category (560 alerts) and the full score vector;
   - the timestamp, data hashes, code commit and model version;
   - **the probabilities** (F, F′).

   Append a record with the file's SHA-256 to `registry/experiments.jsonl`. **Never edit a locked file.**
4. **Sourcing snapshot.** For the top 3 per category by F′ (~84 products):
   - CJ search, match, variants and freight to 3 zips, using the Phase F protocol (free CJ points);
   - stored with the prediction, so sourcing is known **as of the prediction date.**
5. **Revision check.** About 4 weeks after each sealed pull, re-pull the same month M (same queries). Compare:
   - revenue;
   - rank;
   - **`revenue_growth_rate`**, product by product.

**Weekly sub-study** (optional, needs owner approval for credits):
- the same as above, on a rolling 7-day window, for 6 categories;
- **purpose:** test lead time below one month.

## 2. Outcomes

**Scored from later sealed pulls only:**

| Outcome | Definition | Available |
|---|---|---|
| S1 | in the category top 500 at M+1 | one month after the prediction |
| S2 | in the top 500 at M+1, M+2 and M+3 | three months after |
| Lead (weekly study) | weeks between first flag and first top-500 appearance | — |
| Sourcing persistence | CJ match still available, and cost within ±10%, at M+1 | — |

**Unsuccessful predictions are kept and reported.**

## 3. Minimum horizon and statistics

**Sample size:** ~560 alerts per method per month. For a 3-point precision difference (e.g. 28% vs 31%), the per-month
standard error is about 2.7 pts. That needs **at least 7 monthly cohorts** for 80% power at α = 0.05 (pooled; 2.8 × 2.7 / √k ≤ 3 gives k ≥ 6.4; month-block bootstrap).

| Outcome | Cohorts needed | Earliest verdict |
|---|---|---|
| S1 | Oct 2026 … Apr 2027 | ~June 2027 |
| S2 | Oct 2026 … Apr 2027 | ~September 2027 |

**No claim about S2 before its outcomes are observable.** Interim checkpoints after cohorts 1 and 3 are reported as
descriptive only.

**Reporting:**
- catP@20, recall at budget and false alerts per hit;
- PR-AUC;
- calibration (Brier score, slope);
- the share of hits that are first-time vs returning;
- **lead time** (weekly study);
- sourcing feasibility at prediction time;
- the stability of flags.

## 4. Decision thresholds (frozen)

| Gate | Pass if | Fail if |
|---|---|---|
| **V1 Precision is real** | **F′** (no Kalodata growth) beats A Revenue on S1 catP@20 by **≥ 3 pts**, pooled month-block CI > 0, ahead in ≥ 5 of 7 cohorts | F′ − A CI includes 0 or is negative |
| **V2 Kalodata growth is legitimate** | Sealed vs re-pull `revenue_growth_rate` identical (or \|change\| < 1%) for ≥ 95% of products, **and** F beats F′ forward by ≥ 3 pts | Values change materially after the month closes, **or** F's forward edge over F′ is < 1 pt |
| **V3 Lead time exists** (weekly study) | F flags ≥ 10% of first-time entrants ≥ 2 weeks before entry, **and** ≥ 1.5× the growth filter's share at the same budget | Otherwise |
| **V4 Durability** | F or F′ beats A Revenue on S2 by ≥ 2 pts (CI > 0) | Otherwise |
| **V5 Sourcing yield at prediction time** | ≥ 5% of top-3 F′ flags pass all Phase G/H gates | < 3% |

**How the gates drive the decision:**
- **V1 failing** removes the triage proposition's quantitative basis. The pivot then becomes a pure sourcing and
  margin tool, or **NO-GO**.
- **V3 passing** would reopen the original "earlier detection" proposition.

## 5. Cost and approvals

**Monthly credits:**

| Item | Credits |
|---|---|
| Sealed pull | ~30 |
| Ranks 501-1,000 | ~14 |
| Revision re-pull | ~44 |
| Kalodata images for checking the top 84 | ~1 |
| **Total** | **~90 a month ≈ $9** |

- The weekly sub-study adds roughly ~25 credits a week.
- CJ: ~84 × 124 ≈ 10,400 free points a month.

**Approvals:**
- The October sealed pull (30 credits) is **already approved** as part of Tier 1.
- **Ranks 501-1,000, the re-pull and the weekly study need owner approval.**
