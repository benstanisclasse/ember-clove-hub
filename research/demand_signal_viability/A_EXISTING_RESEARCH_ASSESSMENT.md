# Stage A: existing research audit (Demand Signal Intelligence viability assessment, 2026-11-01)

**Question for this stage:** what has actually been built, what runs, and what has actually been shown? Stages B-E answer
whether it supports a commercial product.

**Method:**
- I opened the code, data and evaluation files rather than relying on the reports.
- I re-ran the key results.
- I checked when the data was collected and whether values change between downloads.

**Script and outputs:**
- Script: `scripts/stage_a_checks.py`.
- Outputs: `_work/stage_a_checks.json`, plus the `_work/repro_*.log` re-run logs (kept locally; `*.log` is git-ignored).

**Cost:** no credits, no CJ calls, no money. The model_v2 evaluator writes a registry row to `kalodata.db`, so it was
re-run against a **scratch copy**. No production database was changed.

## 1. What the existing models actually predict

This is the most important finding of the stage. **Most of the models (the pilot, model_v2's two holder tasks and
Phase C's retention models) predict that products already at the top will stay there, not that new demand is emerging.**

| Model | Who it scores | What it predicts | Is it early discovery? | Best simple rule (same population) | Model vs that rule |
|---|---|---|---|---|---|
| Pilot (2026-10-25) | top 500 | still in top 500 next month | No: persistence | — | **Leaks**: uses commission and SKU count, which are current values, not historical. Superseded. |
| model_v1 (2026-10-25) | top 500 and risers | holders and breakouts | Partly | — | **Leaks** (same fields). Superseded by v2. |
| model_v2 `holders_1m` | top 500 | stays in top 500 and sells at least as much | No: persistence | Kalodata growth: 41.1% | **53.7%** (+12.6 pts) per category top 10 |
| model_v2 `holders_3m` | top 500 | in a top 500 three months later | No: persistence | revenue vs cutoff: 82.4% | **89.7%** (+7.3 pts) |
| model_v2 `breakout_1m` | **Kalodata's own riser list** (growth sort, positions 1-200), outside the top 500 | enters a top 500 next month | **Only after Kalodata already shows it as a riser** | revenue vs cutoff: 27.1% | 28.3% (**+1.2 pts**) |
| model_v2 `breakout_3m` | same | enters within 3 months | same | revenue vs cutoff: 32.9% | 34.7% (**+1.9 pts**) |
| Phase C M1 T1/T4 | top-500 ranks 101-500 | retention 1 and 3 months | No: persistence | revenue vs cutoff | T1 P@50 97% vs 85%; T4 92% vs 62% |
| Phase C/H **band model** (H-N2/H-N2b, H-H2) | **ranks 501-1,000** (just below the visible list) | enters the top 500 next month; enters and stays 3 months | **Yes, the only one**: one month before the product shows up in the top 500 | revenue vs cutoff: 27.8% / 9.8% | **38.5% / 14.3%** (+10.8 / +4.5 pts), 5-7 of 7 months ahead |

**Reading the table:**
- The brief's "four existing prediction models" are model_v2's four tasks.
- Two of the four (holders) are bestseller-persistence models.
- The two "breakout" models only score products **already on Kalodata's fast-riser list**. Against "pick the riser
  with the highest revenue", they add **1-2 points**. That is statistically non-zero in the original test, but
  commercially negligible. They can't show any advantage over Kalodata's riser list, because that list is their input.
- **The only model that looks below the visible bestseller list is the break-in model** (ranks 501-1,000). Its lead is
  one month before entry to the top 500, measured against a revenue rule on the same band. **Lead time against any
  real-world discovery date has never been measured.**

## 2. Did the results reproduce?

Everything was re-run on 2026-11-01:

| Result | Re-run outcome |
|---|---|
| Phase C retention, all 28 categories (`phase_c.py`) | **Byte-identical** `phase_c_results.json` (T1 M1 P@50 97.1% vs B1 84.6%, CI [+6, +22]) |
| Break-in model, niche check (`phase_c_band.py check`) | **Identical** (catP@20 43.0% vs 26.1%, coverage 44%) |
| Break-in replication, 24 categories (`phase_c_band.py replicate`) | **Identical** (38.8% vs 28.0%, 7/7 months, coverage 38%) |
| Break-in durability (`phase_h_backtest.py`, run today) | 38.5% enter / 14.3% hold 3 months vs 27.8% / 9.8% |
| model_v2 model selection (`market_eval.py select`, sandboxed) | **Identical** per-category top-10 numbers for all four tasks and every comparison rule; same adopted models |
| Market engine tests (`pytest scripts/test_market.py`) | 11 passed |

**The numbers are reproducible.** Reproducing them doesn't make them valid: the leakage and selection questions below still apply.

## 3. Data timing and leakage

| Check | Finding | Consequence |
|---|---|---|
| When the history was collected | **Every month (2025-10 … 2026-09) was downloaded between 2026-10-25 and 2026-11-01.** Nothing was collected at the time. | Every "June 2026" figure is June as Kalodata reported it **in late October**, 4 months later. Whether Kalodata revises figures after a month closes is **unknown**. |
| Revisions between our own downloads | The same product × category × month in pulls 6-7 days apart: **5,009/5,009 identical** | Values are stable over a week, months after the fact. This says nothing about changes in the first days or weeks after month-end, which is the window a live tool would use. |
| Fields that are only current | Commission rate, SKU count, launch date and title are identical in every month (Phase A). | The **pilot and model_v1 used commission and SKU count: leakage.** model_v2 and Phase C exclude them. Launch date is fixed by nature, so it's safe. |
| Kalodata `revenue_growth_rate` | Comparison window undocumented; agrees with our month-over-month growth only 1.5% of the time (Phase A) | Used as a feature in v2 and Phase C (`kalo_g`). It is probably computed per requested window, but **unverified**. |
| Holdout months | **None untouched.** Every month was used for training, selection or pattern-finding (Phase A ledger). | All historical results are **exploratory**. |
| Forward tests | Frozen September-2026 forecasts (retention, break-in, video concentration, reviews, strategies, Phase H shortlist), with SHA-256 hashes in `registry/experiments.jsonl` | **The only clean validation, and none has been scored yet.** The October pull is possible from 2026-11-02; 3-month outcomes in January 2027. |

## 4. Selection bias: what the data can and can't see

- **The universe is list-based.** Per category and month, we have:
  - the top 1,000 by revenue (ranks 501-1,000 were added on 10-31/11-01);
  - Kalodata's riser list (top 200 by its growth sort);
  - for September only, risers 201-1,000.
  Nothing else is visible.
- **The long tail is missing:** the top 500 holds roughly 33-66% of category revenue (Phase A, approximate).
- **Where new top-500 entrants come from:**

  | Before the next month's entry | Share of entrants |
  |---|---|
  | In ranks 501-1,000 | **38-44%** (Phase C) |
  | On the riser list | **3.5-3.9%** |
  | **Invisible to us** | **roughly half or more** |

- **What a backtest can therefore test:** earlier discovery among products **just below the top 500**, not true
  first-signal discovery from the long tail. It can't measure misses outside ranks 1-1,000.

## 5. System inventory

**Maturity levels:**
1. Concept only
2. Partially implemented
3. Implemented but untested
4. Internally tested (it runs, with checks)
5. Historically validated: walk-forward on months not trained on, beats simple baselines with a CI, reproduced.
   Exploratory here, because no month is untouched.
6. Forward validated
7. Commercially validated

| Component | Exists? | Functional? | Validated? | Evidence | Limitations | Maturity |
|---|---|---|---|---|---|---|
| **Historical data** (`kalodata.db`, 251,654 top-500 product-months, ranks 501-1,000 for all months, risers, top videos, Tier 2 detail) | Yes | Yes | Integrity-checked (Phase A); revision check above | `phase_a_integrity.py`, `stage_a_checks.py` | Retrospective; list-only; ~12 months, the first partial; long tail missing | **4. Internally tested** |
| **Feature engineering** (`features.py`, `market_data.py` point-in-time snapshot, band frame) | Yes | Yes (re-ran identically) | Leakage rules documented; current-only fields excluded since v2 | `DEFINITIONS_v1.md` §6a; snapshot `pit_2026-09_v1` | "Point-in-time" means as reported in October, not as known at the time | **4. Internally tested** |
| **Prediction models**: model_v2 (4 tasks), Phase C M1/M2, break-in model | Yes | Yes | Walk-forward vs baselines with bootstrap CIs; reproduced | evals `20261028-*`, `phase_c_results.json`, `phase_c_band_*.json`, `phase_h_backtest.json` | Mostly persistence; breakout models ≈ revenue rule; no untouched holdout | **5. Historically validated (exploratory)** for persistence and break-in. **Not validated as early discovery.** |
| **Historical backtesting** (rolling origin with embargo; month-block bootstrap; pre-registration) | Yes | Yes | Method sound; reused months disclosed | `market_eval.py`, `phase_c.py`, `registry/` | Comparisons are rank and revenue rules, not real discovery dates | **5** |
| **Demand-signal detection** (flagging unusual traction before the bestseller list) | Partly: the break-in model | Yes | Break-in vs revenue rule only | H-N2/H-N2b/H-H2 | **Lead time never measured**; no alerting; only ranks 501-1,000 | **3-4.** The signal is tested, but not as a lead-time product. |
| **Video intelligence** (top-300 video lists, product video sets, AI-video study, creative study) | Yes | Yes | Descriptive; creator breadth supported for retention (D5) | Phase D; `VIDEO_STUDY_2026-10.md` | Revenue-ranked lists only (survivor-biased); creative effects not significant; creator counts on 536 products only | **4** |
| **Supplier matching** (Kalodata → CJ) | Yes, 162 candidates matched (Phases F+H) plus 50+92 earlier (`data/kalo_cj`, `data/cj_compare`) | **Only through Claude agents using the CJ MCP connector.** No code path or CJ API key in the Hub. | 12/12 transcription checks passed; match quality **not photo-verified** (max score 2) | `_work/cj/*.json`, `phase_f_verify.json`, `phase_h_verify.json` | Manual and judgement-based; ~1 request/s limit; cannot run unattended in a SaaS today | **3-4.** Works as a research process, not as software. |
| **Margin calculations** (variant-level contribution, break-even CAC/ROAS, stress cases) | Yes | Yes | Arithmetic and rules tested; inputs are current CJ quotes | `phase_f_economics.py` | DDU (duties unknown); fee and return rates assumed; no real CAC | **4** |
| **Product rankings / opportunity scoring** (4 separate scores + 7 gates) | Yes | Yes | Market score calibrated (slope 0.84); supplier and ad scores **can't be validated** (no outcomes) | `scoring.py`, `phase_g.py`, Phase G/H | Rule-based; ad suitability untestable without ad data | **4** (market part 5) |
| **Research automation** (scheduled pulls, refresh, alerts) | **No scheduled research jobs.** Only "Ember Hub Nightly Backup" and the studio dashboard tasks exist. | Manual scripts only (`kalodata_gaps.py forward`, `weekly_breakout_report.py --offline`) | — | Windows Task Scheduler listing | Everything is run by hand or by a Claude session | **2. Partially implemented** |
| **Forward-test infrastructure** (frozen forecasts, sealed-pull command) | Yes | Yes (command written, not yet run) | Not scored | `registry/forward_test_*.csv` with hashes; `kalodata_gaps.py forward` | First result is 1 month away from Nov 2; 3-month results in January 2027 | **3** |
| **API capability audit** | Yes | — | Billing claims corrected after balance checks | `research/api_capability_audit/` | **Kalodata and CJ terms for storage and resale were never reviewed** | Reference |
| **Data licensing review** | **No** | — | — | none saved | Gate for any SaaS (Stage D) | **1. Concept only** |
| **Customer / willingness-to-pay evidence** | **No** | — | — | none | No interviews, waitlist, beta or payments | **1. Concept only** |

No component is **forward validated** or **commercially validated**.

## 6. Completeness of the previous research programme

- **Phase reports A-H exist**, with plans, registry entries and scripts.
- **Not done, or done thinly:**
  - lead-time measurement;
  - bundling;
  - a full lifecycle model;
  - a dedicated interaction / nonlinearity study;
  - attribute annotation (needs a paid LLM);
  - image-based saturation;
  - a large creative study;
  - photo-verified matches;
  - every forward-test score.

## 7. What Stage A already tells us about the viability question

These are preliminary findings; Stage B tests them.

1. **The infrastructure is real and reproducible, but almost all of the validated modelling is about persistence,**
   meaning which products already selling well keep selling. That is not the proposed product's promise.
2. **The one early-detection signal with evidence** is break-in prediction from ranks 501-1,000.
   - **The good news:** it beats a revenue rule by about 11 points on entry and about 4.5 points on lasting 3 months.
   - **The limit:** it works one list below the visible top 500, using Kalodata's own deep rankings, which **any
     Kalodata user can already sort and see.**
3. **The "breakout" models add almost nothing** over picking the highest-revenue product on Kalodata's own riser list.
4. **No lead time has been measured**, and no prediction has yet been checked against data collected afterwards.
5. **Supplier matching and economics work only as an agent-run research process.** There is no automated CJ
   integration a SaaS could run.
6. **Licensing and customer demand are completely unexamined.**

## 8. Checkpoint

- **Saved:**
  - this report;
  - `scripts/stage_a_checks.py` and `_work/stage_a_checks.json`;
  - reproduction logs in `_work/repro_*.log` (local only).
- **Assumptions:**
  - "historically validated" here means walk-forward on reused months;
  - the brief's "four existing prediction models" are the model_v2 tasks.
- **Unresolved, for Stages B-E:**
  - lead time;
  - leading vs coincident status of each signal;
  - whether break-in beats Kalodata's own riser list and a plain growth filter at equal alert volume;
  - Kalodata's revision policy;
  - licensing;
  - customers.
- **Stage B (demand-signal validation) is ready.** It needs only local data:
  - a signal inventory;
  - leading / coincident / lagging tests;
  - the comparisons the brief lists (revenue, growth, riser list, momentum, existing models, combined engine, ablations);
  - lead time at equal alert volumes.
