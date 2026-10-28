# Ember Studio Dashboard 2.0 — Proposed Architecture

Status: **proposal for owner review** (Phase A). Nothing here is built yet. Companion documents:
`DASHBOARD_AUDIT.md` (current state, risks, ranking) and `DASHBOARD_IMPLEMENTATION_PLAN.md` (phases).

Guiding rule: **extend, don't replace.** Same Python standard-library server, SQLite, vanilla JS + d3, no build step,
no new services. Every new number carries its source, its period and its freshness; unknown is never shown as zero.

---

## 1. Target shape

```
 Sources                       Ingestion (Python, on the PC)                 Store                        Serve / UI
 ─────────                     ─────────────────────────────                 ─────                        ──────────
 PostZen (TikTok, Facebook) ─► jobs/organic.py      every 15 min ─┐
 studio.db (conveyor)       ─► jobs/studio.py       every 15 min ─┤
 data/facebook/plans        ─► jobs/facebook_plan.py every 15 min ┤
 Shopify  (token or feed)   ─► jobs/shopify.py      every 15 min ─┼─► studio/analytics.db ─► /api/v2/* (JSON, ─► 6 pages, shared
 Ads feeds (Claude task)    ─► jobs/ads_ingest.py   on new file  ─┤    (append-only           date range,          components,
 Generation usage           ─► jobs/costs.py        hourly       ─┤     observations +        compare)             vendored d3
 Product economics          ─► jobs/economics.py    daily        ─┘     latest views)        /data (legacy, kept
                                     │                                                         until migration done)
                                     └─► sync_runs table (health)       backups/ nightly copy
```

- `studio/studio.db` stays the **conveyor** (episodes, transitions, spend). It is not reshaped.
- A new `studio/analytics.db` holds **observations** (what platforms reported, when). Separate file = a bad migration
  can never damage the production workflow, and it can be rebuilt from feeds.
- Connector-only sources (ads, and Shopify if option (b) is chosen) use a **drop-folder contract**: the Claude task
  writes a JSON feed into `data/feeds/<source>/<timestamp>.json`; the PC ingests it like any API response. Switching
  a source to a direct API later changes only its job, not the schema or the pages.

## 2. Data model (analytics.db)

All timestamps stored UTC (ISO 8601). Every metric row carries `source`, `fetched_at`, and the platform's own id.
Names are attributes, never keys.

| Table | Key | Purpose |
|---|---|---|
| `sync_runs` | id | job, started_at, finished_at, ok, rows_written, error, auth_ok — powers the Health page |
| `accounts` | platform, account_id | Ad accounts, Page/TikTok accounts, store; status, currency, timezone |
| `campaigns` / `ad_groups` / `ads` | platform, external id | Hierarchy per platform (Meta ad set, TikTok ad group, Microsoft ad group **or asset group**); status, objective, budget, links to `creatives` |
| `ad_daily` | platform, level, entity_id, date, fetched_at | spend, impressions, reach, clicks, link_clicks, add_to_cart, checkouts, purchases, purchase_value. Append-only; `ad_daily_latest` view picks the newest fetch per day (platforms revise conversions) |
| `organic_posts` | platform, post_id | TikTok video or Facebook post; episode/plan link, product ids, format, series, hook, published_at, url |
| `post_snapshots` | platform, post_id, fetched_at | Lifetime counters at each sync (views, impressions, reach, likes, comments, shares, saves, clicks). 24/48/72 h and 7-day values are read from the snapshot nearest each mark — **only from real snapshots, never back-filled** |
| `account_daily` | platform, account_id, date | Followers and daily totals from PostZen |
| `store_daily` | date | orders, gross_sales, discounts, returns, net_sales, shipping, taxes, total_sales, new/returning customers (Shopify definitions) |
| `store_sessions_daily` | date, referrer_source, referrer_name, utm_source, utm_medium, utm_campaign, utm_content | sessions, cart sessions, checkout sessions, completed checkouts |
| `orders` | order_id | created_at, net/total, discount, refunds, landing-page UTM fields, referrer, customer_type (new/returning) — **no names, emails or addresses** |
| `order_lines` | order_id, line_id | product_id, variant_id, qty, price, discount |
| `products` / `variants` | product_id / variant_id | title, status, price, unit cost, weight, inventory, image |
| `product_costs` | variant_id, effective_from | COGS, supplier shipping, fulfilment, packaging (from EPROLO data + overrides); history kept |
| `generation_costs` | id | provider, model, kind (video/image/audio/llm/data), usd, at, episode/asset/product link, ok |
| `experiments` | experiment_id | hypothesis, variants, metric, product, channel, dates, status, decision (seeded from `data/experiments.csv` schema) |
| `alerts` | id | rule, severity, first_seen, last_seen, state, evidence JSON |
| `settings` | key | timezone, budgets, target CPA, caps, alert thresholds — **non-secret only**; changes go to `audit_log` |
| `audit_log` | id | who, what, before/after, at |

## 3. Reporting rules (metric definitions)

- **Reporting timezone: America/New_York** (store and owner). Day boundaries for every chart and filter are Eastern.
  Sources reported in another zone are re-bucketed from timestamps where possible; where only daily buckets exist
  (PostZen daily totals, ad platforms in account time), the page labels the zone.
- **Period types** shown on every card: *selected period*, *lifetime*, *snapshot (now)*, *estimate*, *forecast*.
- **Missing states**: `Not connected`, `Pending sync`, `No data`, `Not applicable`, `Insufficient data`, `No cap`.
  A value is only `0` when the source reported zero.
- **Three revenue lenses, never summed together:**
  1. *Platform-attributed* — purchases/value each ad platform claims (may overlap).
  2. *Shopify-attributed* — orders whose landing UTM/referrer maps to a channel (directly tracked).
  3. *Blended* — all Shopify orders and net sales vs all ad spend (MER, blended cost per order).
- **Core formulas** (all with zero-denominator → `—`): CTR = clicks/impressions; CPC = spend/clicks;
  CPM = 1000·spend/impressions; platform CPA = spend/platform purchases; platform ROAS = platform value/spend;
  MER = Shopify net sales/total ad spend; blended cost per order = ad spend/Shopify orders;
  blended CAC = ad spend/new customers; conversion rate = completed-checkout sessions/sessions.
- **Contribution before ads (per order)** reuses `profitability_model.py`: price + shipping charged − COGS − supplier
  shipping − fees (2.9% + $0.30) − refund allowance (5%). Break-even ROAS = 1/contribution margin ratio;
  allowable CPA = contribution − target profit per order. Assumptions are labelled as assumptions.
- **Traffic quality flag**: days whose sessions exceed a multiple of the trailing median with no cart activity are
  flagged (e.g. 10/24) and can be excluded from conversion-rate KPIs; the raw number stays visible.

## 4. Attribution design

- Confidence labels per order: **Directly tracked** (UTM or ad click id on landing), **Platform reported**,
  **Inferred** (referrer only), **Unattributed**.
- An order is counted once in Shopify views. Platform claims are shown side by side, with a "claims exceed store
  orders by N" note when they do.
- No multi-touch modelling until there are enough orders to make it meaningful (see plan, Phase F).

## 5. Tracking-link convention (UTM taxonomy)

Keep what works (`utm_source=facebook&utm_medium=social&utm_campaign=fb_photos` already produces sessions). Proposed
standard for new links:

| Channel | utm_source | utm_medium | utm_campaign | utm_content |
|---|---|---|---|---|
| Facebook organic posts | facebook | organic_social | fb_photos | `<date>_<slot>` or post id |
| TikTok organic (bio/link sticker) | tiktok | organic_social | ember_studio | episode id |
| Meta ads | facebook / instagram (`{{site_source_name}}`) | paid_social | `{{campaign.name}}` | `{{ad.id}}` |
| TikTok ads | tiktok | paid_social | `__CAMPAIGN_NAME__` | `__CID__` |
| Microsoft ads | microsoft | paid_search | `{Campaign}` (or `{CampaignId}`) | `{AdId}` |

Macro names follow each platform's documented URL parameters; confirm each against a real click before relying on it.

Existing live URLs are changed **only with owner approval**. The current Facebook value `social` stays readable;
the mapper treats `social` and `organic_social` as the same medium.

## 6. Server and API

- Keep `ThreadingHTTPServer`. Add a tiny router: `/api/v2/overview`, `/api/v2/content`, `/api/v2/ads`,
  `/api/v2/store`, `/api/v2/products/<id>`, `/api/v2/health`, `/api/v2/settings` (read), all accepting
  `from`, `to`, `compare=previous_period`, `grain=day|week`. Aggregation runs in SQL, so the browser receives
  only what a view needs.
- `/data` stays until every page is migrated, then is retired.
- Write endpoints (later, settings only): POST with a CSRF token, behind the dashboard password, validated, logged
  to `audit_log`. **No endpoint ever publishes, spends, or changes an ad or the store.**
- Static assets served from `studio/dashboard/static/` with d3 **vendored locally** (no CDN dependency).

## 7. Frontend

- Pages (separate HTML files, no SPA framework): **Overview, Content Studio, Advertising, Store Analytics,
  Intelligence, Operations & Settings**. Persistent left sidebar on desktop; bottom bar or menu on phones.
- Shared `static/app.css` (design tokens: dark-first charcoal theme with the Ember & Clove terracotta accent, light
  theme kept via the same tokens) and `static/components.js` (KPI card with delta + sparkline + source + freshness,
  chart wrappers, sortable/filterable table with CSV export, status badge, alert item, detail drawer, date-range
  control with compare). Removes the duplicated helpers in today's two pages.
- Global date control in the header; state kept in the URL (`?from=&to=&compare=`) so views are linkable.
- Every component renders the six states: loading, ok, empty, not connected, stale, error.

### Migration map (nothing removed)

| Today | Moves to |
|---|---|
| Next up, headline tiles | Overview (+ store and ads KPIs) |
| Unified posting calendar, Facebook table, Pipeline | Content Studio (calendar gains month/day/list views and filters) |
| Video performance, First week per post, per-channel organic sections | Content Studio → Performance tab |
| All channels | Overview → Channel summary |
| Paid ads section | Advertising (+ campaign hierarchy, trends) |
| Spend (generation) | Operations → Costs (and Overview tile) |
| Sync line in the top bar | Operations → Health (+ freshness dots on every card) |

## 8. Security

- Optional **dashboard password** (single operator): salted hash in a user env var, session cookie, HttpOnly,
  SameSite=Strict; `/health` stays open for monitoring.
- Bind to the LAN address and keep a Windows Firewall rule limited to the private network profile. Never expose
  publicly.
- Secrets only via `hub_env` (user env vars; Windows Credential Manager as an option). Move the PostZen key out of
  `Downloads\key.txt` into the `POSTZEN_API_KEY` user variable that `hub_env` already expects.
- API responses never include tokens, prompts, customer PII or raw order addresses.

## 9. Reliability

- Each job is independent: one failing source never blocks the others; each writes a `sync_runs` row.
- Retries with exponential backoff on 429/5xx; pagination everywhere; idempotent upserts keyed on external ids.
- Atomic writes (temp file + rename) for any remaining flat files.
- Nightly backup of `studio.db`, `analytics.db`, `data/`, `config/` to `backups/<date>/` (keep 14), plus a local
  git repository for code and docs.
- Server stdout/stderr to `logs/dashboard.log` (rotated).

## 10. What stays dependent on the Claude app

Ad platforms (and Shopify, if option (b)) are reachable only through Claude's connectors today; standalone Python
cannot use those credentials. The drop-folder contract keeps the dashboard working when Claude is closed — data just
ages, and the Health page and freshness dots say so. Direct ad APIs (Meta Marketing API token, TikTok developer app,
Microsoft developer token) can replace the feeds later without schema changes.
