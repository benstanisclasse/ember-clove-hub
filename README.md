# Ember & Clove Hub

Memory and rulebook for the Creative Testing Engine. Claude (with its connectors) does the work; this folder keeps the record. Every session and scheduled task reads here first and writes results back.

## Layout

| Path | Contents |
|---|---|
| `config/hub.json` | Account IDs, economics assumptions, decision thresholds, tag vocabulary, TikTok report request. **No secrets.** |
| `data/products.csv` | Price, cost, profit per sale, break-even CPA, loss limit, whether each product can be advertised |
| `data/experiments.csv` | Every test: hypothesis, ad group, budget, dates, status, decision |
| `data/creatives.csv` | Every ad: tags, cost, IDs, current status and why |
| `data/metrics.csv` | Daily numbers per ad (one row per ad per day) |
| `data/inbox/` | Raw pulls from Shopify and TikTok, kept as evidence |
| `data/catalog/<handle>.json` | Full supplier details per product (original title, specs, size table, every gallery and description image URL, variants with cost) — saved before listings are shortened; source material for Higgsfield videos |
| `data/catalog_index.csv` | One row per product: group, colors, sizes, price, cost, material, image counts |
| `recipes/{creative_id}.json` | Full production recipe of each creative, recorded as it's made |
| `assets/{creative_id}/` | Local copies of final videos, storyboards, creator images |
| `reports/` | Daily status and pattern reports |
| `log.md` | Append-only log of imports, approvals, actions, decisions |
| `learnings.md` | Running playbook of what works, with evidence level |
| `brand/` | Logo files |

## Scripts (`scripts/`)

| Script | What it does |
|---|---|
| `init_hub.py` | Creates folders and empty record files (safe to rerun) |
| `catalog.py` | `data/inbox/shopify_products_full_<date>.json` → `data/catalog/` + `catalog_index.csv` (keeps each product's first-seen original title) |
| `economics.py` | `--import data/inbox/shopify_products_<date>.json` loads products; without arguments recalculates profit, break-even CPA and loss limits |
| `recipe.py` | Library: `new_creative`, `add_step`, `finish`, `duplicate` (one change). CLI: `show <creative_id>` |
| `metrics_sync.py` | `data/inbox/tiktok_report_<date>.json` → `metrics.csv` (re-runs update, never duplicate) |
| `decide.py` | Labels each creative: STOP-LOSS, TRACKING-CHECK, LEARNING, WINNER-CANDIDATE, PROMISING, WEAK, INCONCLUSIVE → `reports/status_<date>.md` |
| `patterns.py` | Compares results by tag (hook type, opening visual, format, ...) → `reports/patterns_<date>.md` |
| `hub_env.py` | Loads config and secrets; run it to check secrets are set |

Run them from the Hub folder with `python scripts/<name>.py`.

## Daily loop (after ads are live)

1. Claude pulls yesterday's TikTok ad report via the connector using `tiktok.daily_report_request` in `config/hub.json`, saves it to `data/inbox/tiktok_report_<date>.json`.
2. `python scripts/metrics_sync.py data/inbox/tiktok_report_<date>.json`
3. `python scripts/decide.py` — Claude pauses any STOP-LOSS ads via the connector and reports the rest.
4. End of cycle: `python scripts/patterns.py`, then update `learnings.md`.

## Secrets

Secrets never go in this folder. They live in Windows user environment variables:

| Secret | Variable | How to set or rotate |
|---|---|---|
| Higgsfield API key (`id:secret`) | `HIGGSFIELD_API_KEY` | In PowerShell: `setx HIGGSFIELD_API_KEY "<key>"`, then restart the Claude app |

Check they're present (prints status only, never values): `python scripts/hub_env.py`

Connector-based access (Shopify, TikTok for Business, Higgsfield, Gmail, GA4, Meta Ads) is handled by Claude's connectors and needs no keys here.
