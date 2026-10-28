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
