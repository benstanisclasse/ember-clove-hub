# Ember & Clove Hub

The back office of Ember & Clove, an online clothing and accessories store on Shopify. Claude (with its connectors)
does the work; this folder keeps the record. Every session and scheduled task reads here first and writes results
back. The rules every session follows are in `CLAUDE.md`; every material action is logged, with the owner's own
words for approvals, in `log.md`.

The Hub has five parts:

| Part | What it does | Start here |
|---|---|---|
| **Store and products** | Supplier details, sizes, costs, prices and profit per sale for every product; break-even ad cost and loss limit per product; pricing, offer and supplier (CJ vs EPROLO) studies | `data/`, `reports/` |
| **Ad testing engine** | Every ad test and creative on record; daily TikTok/Meta numbers; each ad labelled (winner candidate, weak, stop-loss, ...); patterns by tag feed the playbook | `data/experiments.csv`, `learnings.md` |
| **Ember Studio** | The content conveyor for the AI character account: plan → script → generate → QA → owner approval → schedule → post → measure, enforced in code | `studio/README.md` |
| **Dashboard** | Local web dashboard (overview, content, ads, profit), synced from TikTok, Facebook and Shopify every 15 minutes, with history | [`docs/DASHBOARD_TOUR.md`](docs/DASHBOARD_TOUR.md) (screenshots), `docs/DASHBOARD_OPERATIONS.md` |
| **Market research** | Kalodata (TikTok Shop US) data, product models, weekly breakout report, winning-video studies, Meta Ad Library and TikTok Top Ads notes | `research/README.md` |

Where things stand and what's next: `docs/RESUME_HERE.md`.

## The dashboard

[![Dashboard overview](docs/gui/1_overview.jpg)](docs/DASHBOARD_TOUR.md)

Eight read-only pages: Overview, Content Studio, Content performance, Advertising, TikTok tests, Store,
Intelligence and Operations. Each is shown and explained in the [dashboard tour](docs/DASHBOARD_TOUR.md).

## Layout

| Path | Contents |
|---|---|
| `CLAUDE.md` | Standing rules for every Claude session (AI presenter labelled as AI, no testimonials, no prices in spoken lines, nothing published or spent without owner approval) |
| `log.md` | Append-only log of imports, approvals, actions, decisions |
| `learnings.md` | Running playbook of what works, with evidence level |
| `config/hub.json` | Account IDs, economics assumptions, decision thresholds, TikTok report request, names of secret variables. **No secrets.** |
| `data/products.csv` | Price, cost, profit per sale, break-even CPA, loss limit, whether each product can be advertised |
| `data/experiments.csv` | Every test: hypothesis, ad group, budget, dates, status, decision |
| `data/creatives.csv` | Every ad: tags, cost, IDs, current status and why |
| `data/metrics.csv` | Daily numbers per ad (one row per ad per day) |
| `data/catalog/<handle>.json`, `data/catalog_index.csv` | Full supplier details per product, saved before listings are shortened, and a one-row-per-product index |
| `data/*_study_*.csv`, `data/cj_compare/`, `data/kalo_cj/` | Pricing, offer, bundle and supplier studies |
| `data/inbox/` | Raw pulls from Shopify and TikTok, kept as evidence (not in git) |
| `recipes/{creative_id}.json` | Full production recipe of each creative, recorded as it's made |
| `reports/` | Status, pattern, pricing, profitability and planning reports |
| `studio/` | Ember Studio: the bible (`studio/bible/*.yaml`), dashboard pages, `studio.db` (the conveyor) and `analytics.db` (history) |
| `research/` | Market research; see `research/README.md` |
| `docs/` | Architecture, audits and roadmaps (Content Studio, Dashboard, Market Engine); `docs/archive/` for finished work |
| `brand/` | Logo files, brand guide, social images |
| `assets/`, `data/media_*`, `backups/` | Videos, images and backups (not in git) |

## Scripts

Run them from the Hub folder: `python scripts/<name>.py`. Each script's first docstring line says what it does.

**Ember Studio and dashboard (`scripts/studio/`)**

| Script | What it does |
|---|---|
| `cli.py` | The only way character-account content moves through the conveyor (see `studio/README.md`) |
| `dashboard_server.py` | The dashboard (port 8790) and its 15-minute sync jobs; started by the Windows task "Ember Studio Dashboard" |
| `shopify_sync.py`, `profit.py`, `ad_tests.py`, `analytics.py` | Read-only Shopify sync, marketing profit, TikTok test pages, history and sync health |
| `publishing.py` | Sends approved episodes to TikTok through PostZen (only through `cli.py`) |

**Ad testing and store**

| Script | What it does |
|---|---|
| `economics.py` | Per-product profit before ads, break-even CPA and loss limit |
| `catalog.py` | Shopify product export → `data/catalog/` + `catalog_index.csv` |
| `recipe.py`, `approve_creative.py`, `record_actual_cost.py` | Record each creative's recipe, owner approval and real cost |
| `metrics_sync.py` | Saved TikTok ad report → `data/metrics.csv` (re-runs update, never duplicate) |
| `decide.py` | Labels each creative: STOP-LOSS, TRACKING-CHECK, LEARNING, WINNER-CANDIDATE, PROMISING, WEAK, INCONCLUSIVE |
| `patterns.py` | Compares results by tag (hook type, opening visual, format, ...) |
| `ads_snapshot.py` | Paid-ads numbers (Meta, TikTok) for the dashboard |
| `pricing_study.py`, `offer_study.py`, `bundle_study.py`, `stack_study.py`, `cj_compare.py` | Pricing, offer and supplier studies |
| `hf_video_batch.py`, `hf_image_batch.py`, `slideshow.py`, `text_label.py`, `ad_edit.py` | Ad video and image production (Higgsfield API) and finishing |

**Market research**

| Script | What it does |
|---|---|
| `kalodata.py`, `kalodata_core.py`, `kalodata_db.py` | Kalodata API pulls and the local research database |
| `market_data.py`, `market_eval.py`, `train_product_model.py`, `score_breakouts.py` | Product dataset, evaluation and models |
| `weekly_breakout_report.py` | Weekly shortlist of rising products (a ranked list, not a forecast) |
| `video_pilot.py`, `video_elements.py`, `video_audio.py`, `analyze_video_study.py` | Winning-video studies |

**Housekeeping**

| Script | What it does |
|---|---|
| `hub_env.py` | Loads config and secrets; run it to check secrets are set (prints status only) |
| `backup_hub.py` | Nightly backup to `backups/` (Windows task "Ember Hub Nightly Backup", 02:30) |
| `publish_public.py` | Updates the public GitHub copy with private IDs shown as XXX |
| `init_hub.py` | Creates folders and empty record files (safe to rerun) |

Tests: `python -m pytest -q scripts/studio`.

## Daily ad loop (while ads are live)

1. Claude pulls yesterday's TikTok ad report via the connector using `tiktok.daily_report_request` in `config/hub.json`, saves it to `data/inbox/tiktok_report_<date>.json`.
2. `python scripts/metrics_sync.py data/inbox/tiktok_report_<date>.json`
3. `python scripts/decide.py`. Claude pauses any STOP-LOSS ads via the connector and reports the rest.
4. End of cycle: `python scripts/patterns.py`, then update `learnings.md`.

## Code, history and backups

- Git, with two GitHub copies: **private** `benstanisclasse/ember-clove-hub-private` (full history, `origin`) and
  **public** `benstanisclasse/ember-clove-hub`, rebuilt by `scripts/publish_public.py` with emails and account/ad IDs
  replaced by XXX. Never push to the public repo directly.
- Databases, media, raw exports, backups and logs stay out of git (`.gitignore`) and are covered by the nightly backup.

## Secrets

Secrets never go in this folder. They live in Windows user environment variables; `config/hub.json` → `secrets` lists
the variable names (Higgsfield, Kalodata, OpenRouter, PostZen, Shopify client ID and secret). To set or rotate one, in
PowerShell: `setx <VARIABLE> "<value>"`, then restart the Claude app. Check they're present (status only, never values):
`python scripts/hub_env.py`.

Connector-based access (Shopify, TikTok for Business, Meta Ads, Google Ads, GA4, Higgsfield, Gmail) is handled by
Claude's connectors and needs no keys here.
