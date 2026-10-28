# Where we left off (saved 2026-10-27, ~22:45 ET)

Two development programs run side by side. Each has its own documents in `docs/`.

## 1. Dashboard 2.0 ("Marketing Intelligence & Operations Dashboard 2.0" master prompt) — PAUSED after Phase D

| Phase | Status | Report |
|---|---|---|
| A Audit | done | `DASHBOARD_AUDIT.md`, `DASHBOARD_ARCHITECTURE_V2.md` |
| B Reliability (git, backups, history db, sync health, honest states, local d3) | done | `DASHBOARD_IMPLEMENTATION_PLAN.md` → "Phase B report" |
| C Shopify (read-only app, sync, Store page, product economics, bot flag, reconciliation) | done | "Phase C report" |
| D Design system, six-section sidebar, Overview, Ads/Intelligence/Ops pages, calendar views | done | "Phase D report" |
| **E Attribution** | **next** (approved order B→C→D→E) | plan in `DASHBOARD_IMPLEMENTATION_PLAN.md` |
| F Profitability | after first orders | |
| G Intelligence | after ~2 weeks of history | |
| H Hardening | last | |

To resume: "Continue Dashboard 2.0 with Phase E." Phase E = one UTM convention for new links, launch-day check that
TikTok/Meta/Microsoft URL macros fill, campaign → ad set/group/asset group → ad drill-down, three lenses
(platform-claimed / Shopify-attributed / blended). Meta began delivering on 10/27 ($0.44, 16 impressions).

Open owner decisions carried over: none blocking Phase E. Microsoft PMax still learning; TikTok sales campaign still a draft.

## 2. Content Studio 2.0 ("Autonomous Content Studio 2.0" master prompt) — STARTED 2026-10-27

Phase A audit in progress → `CONTENT_STUDIO_AUDIT.md`, `CONTENT_STUDIO_ARCHITECTURE_V2.md`, `CONTENT_STUDIO_ROADMAP.md`.
Must share Dashboard 2.0's infrastructure: same dashboard, same `studio/analytics.db` history store, same Shopify
connector (`scripts/shopify_api.py`), same sync-health and backup jobs. No second dashboard or connector.
