# Market Intelligence Engine 2.0 — Roadmap (Phase A result)

Date: 2026-10-28. Source: the owner's "Market Intelligence Engine 2.0" master prompt. Built from four Phase A audits:

| Audit | File |
|---|---|
| Engineering (code, collection, credits, operations, Hub fit) | `MARKET_ENGINE_AUDIT.md` |
| Data quality (coverage, duplicates, what the numbers mean) | `MARKET_DATA_QUALITY_REPORT.md` + `research/kalodata/audit/coverage_matrix_2026-10-28.csv` |
| Model validation (leakage, baselines, calibration) | `MARKET_MODEL_VALIDATION_AUDIT.md` + `research/kalodata/audit/model_audit_eval.py` |
| Creative and competitive research (video study, seasonality, Meta, TikTok, rights) | `MARKET_CREATIVE_COMPETITIVE_AUDIT.md` |

Phase A made no API calls and changed no database, model, script or report. **Nothing below starts without the owner's
approval.**

---

## 1. What Phase A found, in one page

**Solid, keep as is**
- The download itself: every requested page came back full for 28 categories × 12 months, and the numbers are
  internally consistent (revenue = units × price, channels add up). The raw-file-first habit, the credit cap in the
  Kalodata client and the resumable downloader are good foundations.
- SQLite is the right store: the heaviest training query reads 257,600 rows in 0.9 s; integrity check passes.
- The holder models (will a top-500 product stay?) carry real but modest skill: rolling forward test AUC 0.68
  (1 month) and 0.79 (3 months).
- The video study's design (winner vs stalled video of the same product in the same month), its extraction pipeline,
  its logs, and the "paid boosting" finding (84% vs 41%, the only result that survives correction for 152 tests).

**Overstated, needs correcting before anyone relies on it**
- **Breakout models:** the 0.89/0.88 AUCs reproduce, but one number — *product sales ÷ the category's 500th-place
  sales* — scores as well or better (0.896 / 0.878). The model adds little beyond "it already sells close to the top
  500". Among products at similar distance from that floor its AUC is only 0.60–0.68.
- **"≥ 50% chance" in the weekly report** is not a calibrated probability: such picks came true 42% of the time,
  ~32% when scoring beyond the training positions (the deep 201–1,000 list).
- **Leakage:** commission rate, variant count and launch date are *today's* values copied into every past month;
  October 2025 is about one week of data (all its growth values are a placeholder). Removing both makes the breakout
  model a little worse, further below the one-number rule.
- **Creative findings:** "person with product in the first frame", length, talking speed, text hooks and close-ups do
  not survive correction and mostly vanish when paid status is matched. Winners and comparisons were not matched on
  video age (median 37 vs 17 days). Some of these already became production rules (2.9–3.8 words/s band, 70% speech
  gate in `rules.yaml`, the cycle-1 ad ranking).
- **Seasonality:** one observed year, so "peaks" are observations, not validated recurring patterns. The "heating up"
  ratios include ~11% market-wide growth.
- **Meta Ad Library:** US commercial ads expose no impressions, spend or results. "Longest-running first" was actually
  the newest ads. Run time as a "spend signal" or "current winners" is inference the data can't support.

**Engineering gaps**
- `research/` (397 MB database, 304 MB raw paid responses ≈ 533 credits, models, reports) is in **neither git nor the
  nightly backup**.
- The loader never reloads a file it has seen, so 6 comment pulls that later succeeded still show as failed.
- No credit ledger (≈ 8 credits unexplained); paid calls are skipped only when a same-named file exists, only in the
  bulk downloader; 12 duplicate paid files.
- 97% of pulls have no collection date (`pulled_on = "core"`), no cost, no checksum; month/category/page are parsed from
  file names in four places; deep riser pages share the `core_risers` name, so re-running the trainer now silently
  picks them up (251,654 vs 230,052 rows) and would overwrite model v1.
- Nothing is scheduled; nothing reaches the dashboard, `analytics.db`, sync health, the cost ledger or the Shopify
  product mapping. `pricing_study.py` has its own fee constants instead of `config/hub.json` / `profit.py`.

**Rights and privacy**
- 1.6 GB of third-party videos are still stored although three documents promised deletion; 6,106 review records with
  buyer names and user IDs sit in raw files.

---

## 2. How the engine fits the Hub (no parallel systems)

| Need | Use what already exists | New piece (only this) |
|---|---|---|
| Storage | `research/kalodata/kalodata.db` (SQLite) | New columns/tables in the same file, non-destructive |
| Backups | `scripts/backup_hub.py` nightly task | Add `kalodata.db` (snapshot) and `raw/` (append-only mirror, like media) |
| Versioning | Hub git repo | Track research *code and reports*; keep data out (size), with manifests |
| Scheduling | Windows scheduled task + `analytics.db` `sync_runs` health (Dashboard Phase B) | One task "Ember Market Research" writing `sync_runs` rows |
| Costs | Hub cost ledger (Dashboard Phase F, `profit.py import_generation_costs`) | Kalodata credit ledger feeding that ledger |
| Economics | `profit.py` + `shopify_sync.product_economics` + `config/hub.json` econ | Candidate economics call these; no new fee constants |
| Shopify identity | `shopify_sync.py` catalog (Dashboard Phase C) | Link table external product ↔ Shopify product ↔ supplier SKU |
| Dashboard | Same dashboard; **Intelligence** section (Dashboard Phase G) | A "Market" area inside Intelligence; credit ledger + jobs on **Operations** |
| Findings | One findings table shared by Dashboard G and Content Studio F | Market findings write to it with source = market |
| Experiments | One experiment registry (Content Studio Phase E / Dashboard G) | Market hypotheses become rows there; Studio produces, Shopify measures |
| Creative rules | `studio/bible/rules.yaml` (owner-approved only) | Research never edits rules; it proposes, owner approves |

Placement in the sidebar: the master prompt asks for a dedicated **Market Intelligence** section. The dashboard
already has six sections; my recommendation is a *Market* tab group inside **Intelligence** (Overview, Discovery,
Watchlist, Creative, Models) so there is one place for insight. Owner decision (D4 below).

---

## 3. Phases, re-ordered by what Phase A found

Effort: S ≈ under half a day, M ≈ 1–2 days, L ≈ 3+ days. "Credits" = Kalodata spend.

### Phase B0 — Protect and correct (S–M, 0 credits) — do first
1. Add `kalodata.db` and `research/kalodata/raw/` to the nightly backup (run a backup before any migration).
2. Git-track research scripts' outputs that are text (reports, manifests); keep `.db`, raw JSON and media ignored.
3. Fix the loader so a changed raw file is reloaded (checksum per file); reload the 6 stale comment pulls.
4. Put a correction block at the top of `MODEL_V1`, `BREAKOUT_EXPLAINED`, `VIDEO_STUDY_2026-10`, the seasonality and
   Meta notes: what holds, what is overstated (from the audits).
5. Weekly report: replace "≥ 50% chance" with a rank and the honest hit rate; label it "research shortlist".
6. Pin model v1 outputs: stop the trainer picking up the deep riser pages (filter positions 1–200) so a rerun can't
   overwrite v1.
7. Rights: delete the 1.6 GB of stored third-party videos (keep transcripts, frame-level tags and logs) and strip buyer
   names/user IDs from raw review files — **owner decision D2**.

### Phase B — Data quality and model validation (M–L, 0 credits)
1. Pull metadata: proper `kind / month / category / page / position band` columns on `pulls`, collection time from
   file times where known, cost and checksum; deep risers as their own kind. Non-destructive (add columns, backfill).
2. Exclusions with documented reasons: Oct 2025; Nov features built on Oct; Virtual Products; thin categories flagged
   (Pre-Owned, Muslim Fashion); AI flag before Jun 2026 treated as unknown; today's-value fields (commission, SKU
   count, launch date, review count) never used as past features.
3. Duplicates: drop the doubled Womenswear Aug/Sep rows in views; sum the 159 split product-months.
4. Point-in-time dataset builder: for each month-end T, only data with event period ≤ T; written as a versioned
   snapshot with a manifest (data cutoff, feature list, row counts, code commit).
5. Rolling-origin evaluation with embargo as the standard harness (from `model_audit_eval.py`): ROC-AUC, PR-AUC,
   precision/recall/lift @10/20/50 per category, Brier score, reliability table, month-block bootstrap CIs.
6. Baselines always reported next to the model: distance to the top-500 floor, rank, Kalodata growth, momentum,
   logistic. A model ships only if it beats the best baseline on top-K hit rate with a CI that excludes zero.
7. Calibration (isotonic or Platt on a held-out month) only if it improves Brier on the next month.
8. Holdout policy: freeze the last labelled month as the final holdout; the October 2026 live picks become a
   genuinely unseen check when October's lists exist. Every run goes into an experiment registry (research question,
   data version, params, seed, result, decision); a used holdout is marked spent.
9. Check the 10/26 deep-list picks against October actuals (needs October lists: ~1.5 credits per category; or wait
   for the scheduled refresh in Phase G).

### Phase C — Research data architecture (M)
- Listing identity vs product family kept separate; merges only on strong evidence (same seller + near-identical title +
  price), never title alone. Link table to Shopify products and supplier SKUs (reusing the Shopify sync catalog).
- Prediction registry (product, date, model version, population, feature snapshot, score, target, horizon, outcome when
  known). Old predictions are never overwritten.
- Per-record quality flags (completeness, freshness, duplicate risk, consistency) used by reports.

### Phase D — Early opportunity detection and scoring (M–L)
- Lifecycle states with explicit rules (Newly observed, Emerging, Accelerating, Established, Mature, Declining,
  Rebound, Seasonal, Insufficient data).
- Separate targets: near-term breakout, sustained demand, revenue threshold, decline risk; robust growth (log growth,
  volume floors, category-relative, shrinkage for small bases).
- Scorecard with six separate dimensions (demand, competition, economics, creative potential, operational viability,
  evidence quality). Each shows its inputs; "Unknown" when inputs are missing — no invented scores.
- Hard gates: no supplier, margin below the allowable CPA from `profit.py`, shipping beyond store policy, safety/IP
  issues, anything that needs misleading presentation.

### Phase E — Creative intelligence (M, small credits)
- Hand-check AI tags on 20 pairs before any new tagging.
- Second study matched on paid status and posting week, with an attempts table (attempted / downloaded / failed /
  reason / views / sales) to measure download bias; outcome per 1,000 views where views exist.
- Pattern library rows (pattern, examples, sample size, CI, confounders, confidence, last validated) stored in the
  Content Studio's planned knowledge table — one tag vocabulary.
- Research → hypothesis → experiment proposal → owner approval → Content Studio production → measured in Shopify.
- **Owner decision D3** on the `rules.yaml` gates that came from non-significant findings.

### Phase F — Sourcing and profitability (M)
- Supplier states (Unresearched → Candidate found → Specs matched → Pricing verified → Fulfillment verified → Sample
  required → Approved / Rejected). Start manual (owner or me checking supplier pages); add an integration only where an
  official API exists.
- Contribution margin and allowable CPA from `profit.py` with the same config as the store.

### Phase G — Automated, cost-controlled collection (M)
- Credit ledger written by the Kalodata client on every call; reconciles with the provider balance; feeds the Hub cost
  ledger.
- Request-level cache: before paying, check raw archive + database + freshness; refuse duplicates.
- Incremental monthly refresh (top 500 + risers for the categories that matter to us first), plus the weekly scan.
- Budgets: per-run estimate, daily/weekly/monthly caps, pause at cap — **owner sets the monthly budget (D1)**.
- Windows task with checkpoints, no overlap, retries, `sync_runs` health; read-only research only (never purchases,
  publishes, or changes Shopify).

### Phase H — Dashboard (M–L)
- Market area inside Intelligence: overview tiles, discovery explorer (filters, export), product page (history, scores
  with uncertainty, top videos, comments, competition, supplier, economics), watchlist with statuses, creative explorer,
  model validation view. Credit ledger, schedule and failed jobs on Operations.

### Phase I — Closed loop (ongoing, needs store history)
- Map researched products to Shopify products; compare market signal vs our sessions, conversion, orders, margin and
  ad results; test whether breakout scores, video share or low competition predict *our* results. Our own outcomes are
  the validation that matters.

---

## 4. Order across the Hub's programs

| When | Market engine | Dashboard 2.0 | Content Studio 2.0 |
|---|---|---|---|
| Now | **B0, B** (no store history needed) | G waits for ~2 weeks of history (≈ 11/10) | D items 5–7 |
| ~11/10 | C, D | G (shared findings table + experiment registry) | E (experiments) |
| Later | E, F, G, H | — | F/G (product intelligence uses market scores) |
| Ongoing | I | | |

Coordination rules: one findings table, one experiment registry, one cost ledger, one scheduler pattern with
`sync_runs`, one backup job, one dashboard. Market engine work touches `scripts/kalodata*.py`, the training/report
scripts and `research/`; it edits shared files (`backup_hub.py`, `dashboard_server.py`, `profit.py`) only in short,
committed steps, after checking the other sessions aren't mid-change.

## 5. Decisions needed from the owner

| # | Decision | Recommendation |
|---|---|---|
| D1 | Monthly Kalodata budget for scheduled collection | ~30 credits/month (≈ $3) for the monthly refresh of our categories + ~20 per weekly scan only when you want one; pause at cap |
| D2 | Delete the 1.6 GB of stored third-party videos and strip buyer names from raw review files | Yes (keep transcripts, tags, logs) |
| D3 | `rules.yaml` gates built on non-significant study results (words/s band, 70% speech share) | Keep as production defaults, not as "proven" rules; widen if they block good videos |
| D4 | Where Market lives in the dashboard | Tab group inside Intelligence (not a 7th sidebar section) |
| D5 | Use the weekly breakout report until Phase B is done? | Keep it as a ranked research shortlist without probabilities |
| D6 | Widen the breakout population with sales ranks 501–1,000 (needs credits) | Later, after Phase B shows what the current population supports |

**Approve Phase B0 + B to start.** B0 and B spend no credits.

---

## 6. Phase B report (2026-10-28)

Owner approval: "Yes, start Market Engine Phase B0 and B. Use your recommendations for decisions D1-D6." (2026-10-28).
This section covers Phase B items 2-8 and B0 items 5-6. No paid or external calls were made: everything ran on the
stored database. Commits: `7772346` (code and tests), `628b04b` (results, offline shortlist).

### 6.1 What was built

| Piece | File | What it does |
|---|---|---|
| Point-in-time dataset | `scripts/market_data.py` | One row per product-month from the monthly lists, using only months ≤ the cutoff. Exclusions and flags below. Writes a versioned snapshot (`research/kalodata/snapshots/<name>/`: parquet + `manifest.json` with cutoff, exclusions and reasons, feature and label definitions, row counts, code commit, pulls fingerprint) |
| Evaluation harness | `scripts/market_eval.py` | Rolling origin, expanding window, embargo = horizon, at least 2 training months. Four tasks, nine rankers, metrics, month-block bootstrap CIs, calibration check, decision rule, registry, frozen holdout, versioned `model_v2_<date>/` (refuses an existing folder) |
| Run registry | `research_runs` table in `kalodata.db` | One row per task per run: question, snapshot, cutoff, features, params, seed, commit, design, results, decision, `holdout_used`. A task whose holdout month is spent can't be run in `final` mode again |
| v1 pin | `train_product_model.py`, `score_breakouts.py`, `explain_breakouts.py` | Risers selected by pull kind `risers` (positions 1-200), so the deep Sep pages can't leak in; `--out` must be a new folder. v1 was not rerun |
| Weekly report | `scripts/weekly_breakout_report.py` | "Research shortlist — not a forecast" (6.5) |
| Tests | `scripts/test_market.py` | 11 tests on a synthetic database: nothing after the cutoff reaches a row, exclusions, dedupe and split-sum, embargo and label maturity, decision rule, registry and spent holdout, v1 refusal, offline report with no forecast wording. `pytest -q scripts/test_market.py`: 11 passed; `pytest -q scripts/studio`: 166 passed |

**Snapshot `pit_2026-09_v1`:** 232,467 product-months, 127,048 products, Nov 2025-Sep 2026. 2,576 list pulls used;
48 left out (27 failed calls, 7 rolling-window keyword/price pulls, 3 page-size-10 probes, 1 page-11 probe, 10
duplicate Womenswear Aug/Sep pilot pages). Oct 2025 (19,600 rows) excluded; Nov 2025 lag features missing (18,938
rows flagged). Virtual Products had no rows. 150 split product-months summed (the other 9 of the 159 were in Oct).
1,000 rows flagged `q_dedup`, 7,765 Kalodata growth placeholders set missing. Thin flag: Pre-Owned, Muslim Fashion
and, by the "$2,000 500th-place" rule, Kids' Fashion (22,789 rows); flagged, not dropped. The Sep deep riser rows
(21,602) are their own population and never train or score in the 1-200 tasks.

**Features (18):** sales, units, price, channel shares, sales ÷ category 500th-place sales, price vs category, our own
month-on-month growth, listed last month, top 500 last month, months already listed, Kalodata growth (labelled,
placeholder = missing), sales rank, riser position, seller's top-500 count and share, category growth. Never used:
commission, SKU count, launch date / age, review count, names (today's values; kept in `attributes_current` for
report filters only). AI-video flag: unknown before Jun 2026 (no video feature is in this panel yet).

**Tasks** (definitions are written into every results file): holders_1m / holders_3m on the top-500 population;
breakout_1m / breakout_3m on risers 1-200 outside every top 500. Labels are membership of any top 500 in later months;
top-500 lists are complete, so absence means "below the 500th product". A label that needs a month after the cutoff
is missing, not 0. Origins: Jan-Aug 2026 (1-month tasks), Mar-Jun 2026 (3-month). Frozen holdouts: Aug 2026 (1m),
Jun 2026 (3m); selection used only the months before.

### 6.2 Results

All numbers are month means over every evaluated month (selection + holdout) with month-block 95% CIs. "Top 10/cat"
= hit rate of each category's 10 highest-ranked products (the decision metric); "lift@20" = hit rate of the 20
highest across all categories ÷ base rate. Results file: `research/kalodata/evals/20261028-005841_final.json`.

**Breakouts, 3 months** (20,714 rows, base 5.3%)

| Ranker | AUC | Top 10/cat | Top 3/cat | Lift@20 | Holdout (Jun) top 10/cat |
|---|---|---|---|---|---|
| HGB (cleaned features) | 0.883 [0.874-0.898] | 33.4% [31.2-36.2] | 40.5% | 9.1 [7.1-10.5] | 30.4% |
| **Logistic (adopted)** | 0.885 [0.871-0.897] | **34.7%** [32.7-37.7] | 45.2% | 10.9 [9.4-11.9] | 32.9% |
| Floor ratio (best single rule) | 0.877 [0.869-0.886] | 32.9% [30.8-35.8] | 43.8% | 7.7 [6.1-9.5] | 30.4% |
| Persistence | 0.562 | 14.1% | 23.5% | 10.2 [8.4-13.5] | 16.8% |
| Riser rank / Kalodata growth | 0.614 / 0.521 | 14.0% / 14.1% | 20.2% | 4.1 / 2.8 | 15.0% |
| Momentum (our MoM) | 0.482 | 5.8% | 8.3% | 2.6 | 6.1% |
| Random | 0.496 | 4.7% | 4.8% | 0.9 | 5.0% |

**Breakouts, 1 month** (41,620 rows, base 3.7%)

| Ranker | AUC | Top 10/cat | Top 3/cat | Lift@20 | Holdout (Aug) top 10/cat |
|---|---|---|---|---|---|
| HGB | 0.901 [0.896-0.907] | 28.4% [25.9-31.0] | 36.6% | 11.6 [10.0-13.6] | 23.6% |
| **Logistic (adopted)** | 0.905 [0.899-0.911] | **28.3%** [26.0-30.4] | 40.3% | 14.2 [11.8-16.4] | 22.9% |
| Floor ratio | 0.896 [0.888-0.902] | 27.1% [25.1-28.9] | 38.2% | 10.7 [8.8-13.0] | 21.8% |
| Persistence | 0.563 | 9.5% | 17.0% | 9.2 | 6.8% |
| Random | 0.502 | 4.6% | 3.1% | 1.0 | 6.4% |

**Holders, 1 month** (111,900 rows, base 30.3%)

| Ranker | AUC | Top 10/cat | Top 3/cat | Lift@20 | Holdout (Aug) top 10/cat |
|---|---|---|---|---|---|
| HGB | 0.673 [0.661-0.685] | 51.4% [46.7-55.6] | 53.0% | 1.9 | 51.8% |
| **Logistic (adopted)** | 0.667 [0.652-0.682] | **53.7%** [48.3-58.0] | 58.5% | 1.9 | 55.0% |
| Kalodata growth (best single rule) | 0.653 [0.641-0.664] | 41.1% [37.0-44.9] | 44.2% | 1.5 | 40.7% |
| Persistence | 0.561 | 36.1% | 37.0% | 1.2 | 30.0% |
| Floor ratio / rank / sales | ~0.50 | 26.9% | 26.3% | 0.7-0.8 | 23.6% |
| Random | 0.501 | 30.0% | 31.2% | 1.0 | 24.6% |

**Holders, 3 months** (55,953 rows, base 46.5%)

| Ranker | AUC | Top 10/cat | Top 3/cat | Lift@20 | Holdout (Jun) top 10/cat |
|---|---|---|---|---|---|
| HGB | 0.790 [0.783-0.796] | 89.7% [88.7-90.5] | 92.9% | 2.1 | 88.2% |
| **Logistic (adopted)** | 0.787 [0.776-0.797] | **89.7%** [88.9-90.8] | 89.9% | 2.0 | 91.4% |
| Floor ratio = rank = sales (same order in a category) | 0.72 / 0.71 / 0.66 | 82.4% [81.2-83.1] | 81.6% | 1.7-1.8 | 83.2% |
| Persistence | 0.724 | 74.2% | 75.0% | 1.6 | 79.6% |
| Random | 0.496 | 47.0% | 47.6% | 1.0 | 45.7% |

**Decision tests** (difference in the monthly metric, month-block CI over all evaluated months, plus the holdout
month on its own):

| Task | HGB vs best baseline | Logistic vs best single rule | Adopted |
|---|---|---|---|
| breakout_3m | top 10/cat −1.3 pts [−2.1, −0.5] vs logistic; lift@20 −1.8 [−4.8, +0.8] | top 10/cat +1.9 pts [+1.1, +2.4] vs floor ratio, holdout +2.5 | logistic |
| breakout_1m | top 10/cat +0.1 [−1.2, +1.7] vs logistic; lift@20 −2.6 [−4.1, −1.2] | top 10/cat +1.2 [+0.3, +2.1] vs floor ratio, holdout +1.1; lift@20 +5.0 [+2.3, +7.5] vs persistence | logistic |
| holders_1m | top 10/cat −2.3 [−4.7, −0.5] vs logistic | top 10/cat +12.6 [+10.4, +14.8] vs Kalodata growth, holdout +14.3 | logistic |
| holders_3m | top 10/cat 0.0 [−2.2, +1.5], holdout −3.2 vs logistic | top 10/cat +7.3 [+6.2, +8.2] vs floor ratio, holdout +8.2 | logistic |

**Calibration:** neither isotonic nor Platt (fitted on a held-out month) lowered the next-month Brier score on any
task (e.g. breakouts 1m: raw 0.0315, isotonic 0.0325, Platt 0.0319; climatology 0.0365), so none is kept. For the
3-month tasks only one month (May) could be checked. The raw HGB scores are still overconfident at the top
(breakouts 3m: scores 0.3-0.5 averaged 0.39 and came true 0.28; 0.5-0.7 averaged 0.56 and came true 0.49), which is
another reason the weekly report shows no probabilities.

**Per category:** the gains are averages. In Womenswear (our category) every breakout ranker is weak: top 10/cat
over the four 3-month origins was 17.5% for the floor ratio, 15% for logistic and 12.5% for HGB (40 picks each;
base 2.8%). Holders 1m in Womenswear: logistic 52.5% vs Kalodata growth 36%.

### 6.3 Decisions

| Task | Adopted ranker | Historical top 10 per category (all evaluated months) | Registry run |
|---|---|---|---|
| breakout_3m | logistic regression, 18 cleaned features | 34.7% (389 of 1,120); top 3: 45.2% | `20261028-005841-final-breakout_3m` |
| breakout_1m | logistic regression | 28.3% (634 of 2,240); top 3: 40.3% | `20261028-005841-final-breakout_1m` |
| holders_1m | logistic regression | 53.7% (1,202 of 2,240); top 3: 58.5% | `20261028-005841-final-holders_1m` |
| holders_3m | logistic regression | 89.7% (1,005 of 1,120); top 3: 89.9% | `20261028-005841-final-holders_3m` |

Artefacts: `research/kalodata/model_v2_2026-10-28/` (one joblib per task, trained on every matured row, plus a
manifest with each ranker's hit rates). All four holdouts are marked spent in `research_runs`.

**HGB is not adopted anywhere.** On no task did it beat the best baseline with a CI above zero. The roadmap rule says
the fallback is "the best transparent baseline". Logistic regression was itself one of the baselines, and on every
task it beat the best single rule with a CI above zero and did not lose on the holdout. I therefore read the rule as
a ladder: single rule → logistic (linear, inspectable) → HGB, where each step must beat the one before by the same
test. **This is my interpretation, for the owner to confirm.** Under the literal rule (single rule only), the adopted
rankers would be the floor ratio for both breakout tasks (32.9% / 27.1% top 10/cat), Kalodata growth for holders 1m
(41.1%) and the floor ratio (= sales rank within a category) for holders 3m (82.4%). Switching is one argument
(`decide(..., middle=None)`) and a new final run once the next month exists.

For breakouts the honest summary from the audit still holds: logistic adds about 1-2 points of top-10 hit rate over
"sort by sales as a share of the 500th-place sales" (32.9% → 34.7%). It is a better sort, not a different kind of
signal.

**Disclosure:** before the registered final run, I ran the identical final code once on a scratch copy of the
registry (development check of the artefact and report path). That run saw the holdout months. Nothing in the design
was changed afterwards. The ladder and all settings were fixed on the selection months, and the registered run
reproduced the same numbers. Strictly, the holdouts were looked at twice with the same code.

### 6.4 What changed in v1

- `train_product_model.py` loads risers by `pulls.kind = 'risers'`; a rerun gives the 230,052-row history v1 was
  trained on, not 251,654. It, `score_breakouts.py` and `explain_breakouts.py` take `--out` and refuse an existing
  folder. `model_v1_2026-10-25/` was not touched and v1 was not rerun.
- The old weekly report cached a retrained model into the v1 folder (`breakout_models.joblib`). The new report
  doesn't train anything.

### 6.5 What changed in the weekly report (B0 item 5, decision D5)

- Title "Research shortlist — not a forecast". There are no probabilities, no "chance" wording and no `--min-chance`
  filter. A built-in check refuses to write a PDF whose own wording mentions chance, probability or forecasts
  (product titles and buyer comments are exempt).
- Ranking: the adopted `breakout_3m` ranker from the newest `model_v2_*`. Each pick shows its rank in its category
  and the ranker's back-test hit rate: a category's top 10 entered a top 500 within 3 months 35% of the time (389 of
  1,120), and its top 3 45% (152 of 336). The category's own rate is shown where available (40 picks each).
- Picking: each category's top K by rank (`--top-k`, default 10), then the existing price, sales, steady, not-fallen
  and commission/unbranded filters, ≤ 3 per category. The report says the filters were not part of the back-test.
- Population stated on page 1: risers 1-200 outside every top 500. Sep riser positions 201-1,000 appear only in a
  separate "outside the tested range" table with no hit rate.
- Commission, variants and age are labelled "as of the pull date". Growth shown is our own month-on-month change.
- `--offline`: no Kalodata call, no TikTok link check and no balance call. Enrichment is read from what is already
  stored in `kalodata.db`, or shown as "not stored". `--scan --offline` is refused. `--riser-pages` now defaults to
  2 (the tested range).
- Offline edition generated: `weekly/research_shortlist_2026-10-28.pdf` (+ `.csv`, 10 picks logged in
  `history.csv` with ranker and model version). It ran with network access and the Kalodata client blocked.

### 6.6 Known limits

- Ten usable months. The 3-month tasks have four origins (Mar-Jun), so their month-block CIs rest on four numbers.
  No holiday month has been forward-tested.
- The breakout population (risers 1-200) is where only about 4% of new top-500 products come from. Widening it with
  sales ranks 501-1,000 (D6) needs credits.
- Kalodata figures are estimates measured retrospectively on one day. Live scans see first estimates.
- `seller_id` is used only as an identity key for the seller features (assumed static; not tested).
- The weekly filters, the deep riser list and the `--scan` path are unvalidated. `--scan` was adapted to the new
  builder but was not run, because it makes paid calls. Scan windows (last 30 days) are labelled as the calendar
  month, as before.
- Spent holdouts: Aug 2026 (1m tasks), Jun 2026 (3m tasks). The next honest test is Sep 2026 for the 1-month tasks
  once October's lists exist, and the live picks in `weekly/history.csv` (10/26 and 10/28).
- Within a category, floor ratio, sales and sales rank give the same order, so their top-10 hit rates are identical.

### 6.7 What Phase C needs

- A prediction registry in the database: the weekly `history.csv` rows (product, date, ranker, model version,
  population, rank) should move into a table, never overwritten, with outcomes filled when labels mature.
- Quality flags as a database view (they exist only in snapshots today) and listing identity / relist clusters
  (seller + title), so relisted products don't look new.
- October 2026 lists (Phase B item 9, about 1.5 credits per category, or the Phase G refresh): they mature the Sep
  1-month labels (a new untouched holdout) and let the 10/26 and 10/28 picks be checked.
- After each new month: rebuild the snapshot, run `market_eval.py select`, then `final` on the new holdout month. The
  registry refuses a spent holdout.
