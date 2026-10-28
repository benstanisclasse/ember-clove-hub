# Where we left off (saved 2026-10-27, ~22:45 ET)

Two development programs run side by side. Each has its own documents in `docs/`.

## 1. Dashboard 2.0 ("Marketing Intelligence & Operations Dashboard 2.0" master prompt) — Phase H done 2026-10-28; next G (from ~2026-11-10)

| Phase | Status | Report |
|---|---|---|
| A Audit | done | `DASHBOARD_AUDIT.md`, `DASHBOARD_ARCHITECTURE_V2.md` |
| B Reliability (git, backups, history db, sync health, honest states, local d3) | done | `DASHBOARD_IMPLEMENTATION_PLAN.md` → "Phase B report" |
| C Shopify (read-only app, sync, Store page, product economics, bot flag, reconciliation) | done | "Phase C report" |
| D Design system, six-section sidebar, Overview, Ads/Intelligence/Ops pages, calendar views | done | "Phase D report" |
| E Attribution (tracking convention, store attribution, campaign drill-down, three lenses) | done | "Phase E report" |
| F Profitability (profit engine, cost ledger, budgets) | done | "Phase F report" |
| **G Intelligence** | **next, from ~2026-11-10** (needs ~2 weeks of history) | |
| H Hardening (security, atomic writes, startup, speed, operations guide) | done | "Phase H report", `DASHBOARD_OPERATIONS.md` |

To resume: "Continue Dashboard 2.0 with Phase G." Phase E = one UTM convention for new links, launch-day check that
TikTok/Meta/Microsoft URL macros fill, campaign → ad set/group/asset group → ad drill-down, three lenses
(platform-claimed / Shopify-attributed / blended). Meta began delivering on 10/27 ($0.44, 16 impressions).

Open owner decisions carried over: none blocking Phase E. TikTok test 01 LIVE since 2026-10-28 (rebate trial, no edits until 2026-11-04 12:04 CST); dashboard page Advertising > TikTok tests (/ads/tests, scripts/studio/ad_tests.py).
**Microsoft Advertising removed 2026-10-28** (account suspended; owner: "remove Microsoft from our system"). Ads = Meta + TikTok only.

## 2. Content Studio 2.0 ("Autonomous Content Studio 2.0" master prompt) — Phase D done 2026-10-28; next E (~2 weeks of tagged content)

Phase A audit DONE → `CONTENT_STUDIO_AUDIT.md`, `CONTENT_STUDIO_ARCHITECTURE_V2.md`, `CONTENT_STUDIO_ROADMAP.md`.
Phase B DONE 2026-10-27 (report at the end of CONTENT_STUDIO_ROADMAP.md): unified content records, honest publish states.
Phase C DONE 2026-10-27 (commit 97f7869; report at the end of CONTENT_STUDIO_ROADMAP.md): generation/asset records,
content features, 24h/48h/7d marks, utm_content=<content id>, performance + production-cost views.
Phase D (items 1–4) DONE 2026-10-28 (commit 382a7ad): shared rule module (checks.py), media-bound approvals,
product availability at publish, Facebook AI-picture weeks in the database (fb_ai.py).
Phase D items 5–7 DONE 2026-10-28 (commit 1aabcec): approvals cover reference images + prompt templates
(approved_assets.json), Facebook outfit compatibility + caption rotation, Ember's references library. Phase D complete.
To resume: "Start Content Studio Phase E" (once ~2 weeks of tagged content exist). Wardrobe approved 2026-10-28 (bible fully approved; products.yaml only once selling).
First real use of fb_ai.py: the AI-picture week from 2026-11-04.
Note: Dashboard 2.0 Phases E and F were completed in a parallel session.
Must share Dashboard 2.0's infrastructure: same dashboard, same `studio/analytics.db` history store, same Shopify
connector (`scripts/shopify_api.py`), same sync-health and backup jobs. No second dashboard or connector.

## 3. Market Intelligence Engine 2.0 ("Market Intelligence Engine 2.0" master prompt) — Phases A, B0, B done 2026-10-28; next C (with D)

Phase A audit DONE → `MARKET_ENGINE_AUDIT.md`, `MARKET_DATA_QUALITY_REPORT.md`, `MARKET_MODEL_VALIDATION_AUDIT.md`,
`MARKET_CREATIVE_COMPETITIVE_AUDIT.md`, `MARKET_ENGINE_V2_ROADMAP.md`.
B0 DONE (commits 8c598e9, 1edfe2b, a3dbec6): research/ in backups and git (reports), checksum reload + pull metadata,
buyer identities stripped, 280 videos to the Recycle Bin, correction notes, credit budget in config (D1=30/month).
B DONE (commits 7772346, 628b04b, 1e45b59; report = roadmap section 6): `scripts/market_data.py` point-in-time builder,
`scripts/market_eval.py` rolling-origin harness + `research_runs` registry, model_v2 = logistic for all four tasks,
v1 pinned, weekly report is now an offline-capable "Research shortlist — not a forecast". Tests: `scripts/test_market.py`.
Next untouched test: Sep 2026 outcomes for the 1-month tasks once October lists exist (needs ~1.5 credits/category).
Shares the Hub's backup job, cost ledger, sync_runs, dashboard (Intelligence section), findings table and experiment
registry; no parallel systems. To resume: "Start Market Engine Phase C".
