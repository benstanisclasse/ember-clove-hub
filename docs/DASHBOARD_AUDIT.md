# Ember Studio Dashboard — Technical Audit (Phase A)

Date: 2026-10-27. Scope: the local dashboard at `http://192.168.1.215:8790`, its server, data, integrations and
neighbouring Hub code. Method: code read-through, database inspection, test run, and read-only queries against
PostZen, Shopify, Meta Ads, TikTok Ads and Microsoft Advertising. **No dashboard code was changed for this audit.**

---

## 1. Executive summary

The dashboard works and is cheap to run: one ~180-line Python server, two HTML pages, vanilla JS + d3, data in
flat JSON/CSV files refreshed every 15 minutes (organic) and every 3 hours (ads). It is good at **operations**
(what posts when, where each video is in production) and adequate at **organic reach**. It cannot yet answer the
question it exists for: *which marketing activity produces profitable sales*, because:

1. **Shopify is not connected.** Store revenue, orders, sessions and attribution are absent.
2. **There is nothing to attribute yet.** The store has **0 orders, ever** (Shopify `ordersCount` = 0, exact).
   Paid ads have spent **$0** on all three platforms (Meta and Microsoft campaigns are approved/learning but not
   delivering yet; the TikTok sales campaign is an unpublished draft).
3. **History is thrown away.** Every sync overwrites the dashboard files. Only PostZen's own per-post timeline
   survives, so period comparisons, trend lines and "views after 24/48/72 h" cannot be built from our data.
4. **No version control or backups.** The Hub is not a git repository and `studio/studio.db` has no backup.

The most valuable next work is therefore not visual: it is **measurement plumbing** (Shopify sync, tracking-link
hygiene, history, sync health, version control). Several items in the master prompt — anomaly detection, opportunity
scoring, creative intelligence, ML compatibility — need weeks of orders and spend before they can say anything
true. They should be designed for, but built after the data exists.

### Key facts found during the audit

| Area | Finding | Evidence |
|---|---|---|
| Store sales | 0 orders lifetime; $0 sales last 30 days | Shopify Admin `ordersCount` (EXACT); ShopifyQL `FROM sales` |
| Store traffic | 2,145 sessions since 10/23; 1,104 on 10/24 alone | ShopifyQL `FROM sessions TIMESERIES day` |
| Traffic quality | 87% "direct" (1,856); likely bots, our own checks, Cloudflare probing | referrer breakdown; log.md 10/24 notes on rate-limited curl checks |
| Funnel | 9 sessions added to cart, 7 reached checkout, 0 completed | ShopifyQL sessions funnel |
| Organic → store | Facebook social 278 sessions; TikTok social 5; `utm_campaign=fb_photos` 5 sessions | ShopifyQL by referrer / UTM |
| **Tracking to verify** | 3 sessions arrived with `utm_campaign=__CAMPAIGN_NAME__` (TikTok macro not substituted). The campaign is an unpublished draft, so these are most likely ad-preview clicks, where TikTok does not fill macros; verify on the first live clicks | ShopifyQL UTM breakdown |
| Ad spend | $0 on Meta, TikTok, Microsoft (30 days) | the three ad connectors |
| Meta | 1 campaign ACTIVE, ad set + 3 ads "pending / preparing" since 10/27 20:06 ET | Meta Ads connector |
| Microsoft | "PMax Ember & Clove" Active, delivery "learning / delivering soon" | Microsoft Ads connector |
| Weekly cap tile "$0.00" | Not a bug in the data: `rules.yaml` sets all caps to `null` ("owner 2026-10-26: no caps until full automation"); the page renders `null` as `$0.00` | `studio/bible/rules.yaml:83-85`, `caps.json` |
| Tests | 38/38 studio tests pass | `pytest scripts/studio/test_studio.py` |

---

## 2. Current architecture

```
                    ┌──────────────────────────── Windows PC "brick" (192.168.1.215) ─────────────────────────────┐
                    │                                                                                              │
  PostZen API ◄─────┼── publishing.sync()  ──┐   every 15 min, in-process thread of dashboard_server.py            │
  (TikTok + FB      │   facebook_photos      │                                                                    │
   accounts)        │   .sync_dashboard() ───┤──► studio/dashboard/*.json|*.csv  ◄── GET /data ── browser (LAN)   │
                    │                        │         ▲     ▲                        GET / , /metrics             │
  studio.db ◄───────┼── (reads episodes,     │         │     │                        GET /health                  │
  bible/*.yaml      │    spend, transitions) ┘         │     │                                                     │
  data/facebook/    │                                  │     └── scripts/ads_snapshot.py merge                     │
   plan_*.json      │                                  │            ▲                                              │
                    │                                  │            │  every 3 h, only while the Claude app is open│
                    │                                  │   Claude scheduled task "ads-dashboard-refresh"           │
                    │                                  │     Meta Ads / TikTok Ads / Microsoft Ads connectors      │
                    │                                  │                                                           │
                    │  Windows task "Ember Studio Dashboard" (at startup) → run_dashboard.cmd → dashboard_server.py │
                    └──────────────────────────────────────────────────────────────────────────────────────────────┘
  Not connected: Shopify (orders, revenue, sessions, UTM) — reachable only through Claude's Shopify connector today.
```

### 2.1 Components

| File | Lines | Responsibility |
|---|---|---|
| `scripts/studio/dashboard_server.py` | 182 | `http.server` on 0.0.0.0:8790; serves 2 pages inside an HTML shell with a small `dash` data shim; `/data` returns all datasets; background sync thread every 15 min |
| `scripts/studio/publishing.py` | 225 | TikTok side: publish to PostZen (draft/scheduled), refresh post statuses, write schedule/followers/tiktok_videos/post_timeline/daily_metrics/spend/caps |
| `scripts/facebook_photos.py` | 373 | Facebook photo-post planner, publisher and dashboard sync (fb_schedule, fb_posts, fb_daily, fb_followers) |
| `scripts/postzen.py` | 65 | Minimal PostZen client (get/post/put/delete/upload/sync_external) |
| `scripts/ads_snapshot.py` | 62 | Merges one platform's daily ad numbers into ads_daily.csv / ads_accounts.json |
| `scripts/hub_env.py` | 57 | Config (`config/hub.json`) and secrets from Windows user env vars |
| `scripts/studio/{db,bible,gates,production,cli}.py` | ~1,430 | Ember Studio conveyor: episode state machine, bible validation, rule gates, generation, CLI |
| `studio/dashboard/index.html` | 483 | Control room page (CSS + markup + JS in one file) |
| `studio/dashboard/metrics.html` | 475 | Metrics page (same structure) |
| Hub 1.0 modules: `hubdata.py`, `economics.py`, `decide.py`, `metrics_sync.py`, `profitability_model.py`, `pricing_study.py`, `test_product_economics.py` | ~750 | CSV records (products, creatives, experiments, metrics), unit economics, creative status rules — **not connected to the dashboard** |

### 2.2 HTTP endpoints

| Path | Returns | Notes |
|---|---|---|
| `/`, `/index.html` | Control room page | Shell + `studio/dashboard/index.html` |
| `/metrics` | Metrics page | Shell + `metrics.html` |
| `/data` | All 13 datasets + last sync + last error | Read on page load and every 60 s; no secrets |
| `/health` | `{last_sync, last_error}` | |
| anything else | 404 | GET only; no write endpoints |

### 2.3 Data stores

**SQLite `studio/studio.db` (228 KB)**

| Table | Rows | Purpose | Notes |
|---|---|---|---|
| `episodes` | 33 (21 real, 12 test) | One TikTok video each: series, date/slot, outfit, script, prompt, model, cost, video path, QA, approval, caption, PostZen id, publish mode, platform status, post URL, state | Video-only model; Facebook posts live elsewhere |
| `transitions` | 216 | Audit log of every state change (actor, reason, time) | Good foundation for a "production history" panel |
| `spend` | 17 | Generation spend per episode | Only Ember Studio video jobs. Facebook pictures, store product photos, Higgsfield images, OpenRouter tagging and Kalodata credits are **not** recorded here |
| `metrics` | **0** | Designed for per-video snapshots by hours-after-post | **Never written.** Exactly what the "views after 24/48/72 h" feature needs |

No foreign keys, no indexes beyond primary keys (fine at this size).

**Flat files `studio/dashboard/` (13 datasets, all < 10 KB)** — `schedule.json`, `followers.json`, `tiktok_videos.csv`,
`post_timeline.csv`, `daily_metrics.csv`, `spend.json`, `caps.json`, `fb_schedule.json`, `fb_posts.csv`,
`fb_daily.csv`, `fb_followers.json`, `ads_daily.csv`, `ads_accounts.json`. Each sync **rewrites** its files in place
(no history, not atomic). `ads_daily.csv` is the exception: it merges by platform+date.

**Other records:** `data/facebook/plan_*.json` + `history.json` (Facebook plan and sends, edited in place),
`data/products.csv` (13 rows, Hub 1.0), `data/creatives.csv` (16), `data/experiments.csv` (**0**),
`data/metrics.csv` (**0**), `data/pricing_study_*.csv`, `data/price_proposal_*.csv`, `log.md` (hand-written operations log).

### 2.4 Integrations

| Integration | Access path | Used for | Independent of Claude app? |
|---|---|---|---|
| PostZen | REST, key `pzn_…` | Publishing, statuses, organic metrics, followers, `sync-external` | Yes |
| TikTok (organic) | via PostZen | Views, impressions, likes etc. per video; followers | Yes |
| Facebook Page (organic) | via PostZen | Impressions, reach, clicks per post; followers | Yes |
| Meta Ads | Claude connector (read) | Spend, impressions, clicks, purchases, value, campaigns | **No** |
| TikTok Ads | Claude connector (read) | Same | **No** |
| Microsoft Advertising | Claude connector (read) | Same (per-day totals need one call per day) | **No** |
| Shopify | Claude connector only (Admin GraphQL + ShopifyQL) | Not used by the dashboard yet | **No** (no Admin token on the PC) |
| Higgsfield | REST, key in user env | Image/video generation | Yes |
| Google Analytics / Ads | Claude connectors exist | Not used by the dashboard | No |

### 2.5 Scheduled jobs

| Job | Where | Schedule | Notes |
|---|---|---|---|
| Ember Studio Dashboard | Windows Task Scheduler | At startup (+1 min), restarts ×3 | Runs `run_dashboard.cmd`; console output is not saved anywhere |
| Organic sync | Thread inside the server | Every 15 min | TikTok sync then Facebook sync, sequentially; one failure skips the rest of that cycle |
| ads-dashboard-refresh | Claude scheduled task | Every 3 h at :20 | Read-only; needs the Claude app open; Auto permission mode |
| Facebook auto-plan | `run_facebook_auto.cmd` | **Not scheduled** (owner OK pending) | `auto_publish` false |

### 2.6 Frontend

- No build step. Each page is one HTML file with inline CSS and JS, injected into the server's shell.
- d3 v7.8.5 loaded from **cdn.jsdelivr.net** — the dashboard has no charts if the PC is offline or the CDN is blocked.
- A `window.dash` shim imitates the claude.ai artifact data API so the same `index.html` can run online; the online
  artifact (`E1BKotHzjjV1BQ6jQymzwe`) is **out of date** (no Facebook, calendar, Metrics or Ads).
- Theme follows the device (light/dark) via `prefers-color-scheme`; tokens defined in the shell.
- Components are hand-rolled per page (bars, line, stacked, table, growthTable). `metrics.html` and `index.html`
  each carry their own copies of similar helpers (e.g. `growthTable`, `bars`, `tooltip`).
- Data refresh: full `/data` payload every 60 s and a full redraw.

### 2.7 Configuration and credentials

- `config/hub.json`: non-secret IDs, economics assumptions, decision thresholds, tag vocabularies. Secrets map to
  Windows user env vars (`higgsfield_api`, `kalodata_api`, `openrouter_api`, `postzen_api`).
- **PostZen key**: `POSTZEN_API_KEY` user env var is **not** set; `run_dashboard.cmd` reads the `pzn_` token from
  `%USERPROFILE%\Downloads\key.txt` (plain text) into the server process environment.
- `studio/bible/*.yaml`: content rules, caps (all `null` by owner decision), posting slots and timezone.
- Never served: keys, prompts. `/data` exposes captions, schedule, post URLs and performance only.

### 2.8 Tests

- `scripts/studio/test_studio.py`: 38 tests, all passing (state machine, gates, bible approval, publishing rules).
- Hub 1.0: `test_product_economics.py` is a calculation script, not a test suite.
- **No tests** for the dashboard server, the sync output shapes, `facebook_photos.py`, `ads_snapshot.py`, or any
  metric formula on the pages.

### 2.9 Logging and error handling

- `log.md`: thorough human/Claude operations log (good audit trail of owner decisions).
- Server: only the **last** sync error is kept (in memory, shown in the page bar); tracebacks go to a console nobody sees.
- No record of sync duration, records updated, or per-source success.
- `postzen.sync_external` swallows its own failure by design so the rest of the sync runs.

---

## 3. Limitations and risks

### 3.1 Data integrity

| # | Risk | Impact | Severity |
|---|---|---|---|
| D1 | No history: dashboard files overwritten every sync | No period comparisons, no true 24/48/72 h snapshots, no audit of revisions | High |
| D2 | `metrics` table empty although designed for snapshots | Same as D1 | High |
| D3 | Non-atomic file writes | A page load during a write can read a half-written file → "Failed to load" flicker | Low |
| D4 | Mixed day boundaries: PostZen buckets in UTC, ads in each account's zone, Shopify in America/New_York | Evening posts land on "tomorrow"; cross-source days don't line up | Medium |
| D5 | `null` caps shown as `$0.00`; unknown values sometimes shown as 0 | Misleading tiles | Medium |
| D6 | Generation spend incomplete (only Studio video jobs) | Content cost understated | Medium |
| D7 | Platform-claimed purchases are summed in "Paid ads" totals | Will double count once more than one platform converts | Medium (later) |
| D8 | Traffic quality: ~1,100 likely non-human sessions on 10/24 | Conversion rate and sessions KPIs distorted unless filtered or flagged | Medium |
| D9 | Facebook plan files edited in place by both planner and sync | Hard to reconstruct what was planned vs posted | Low |
| D10 | TikTok ad links arrived with an unfilled `__CAMPAIGN_NAME__` macro (probably preview clicks of the draft) | If it persists after launch, paid TikTok traffic can't be tied to a campaign in Shopify | Medium (verify at launch) |

### 3.2 Operational

| # | Risk | Severity |
|---|---|---|
| O1 | **No version control** (Hub is not a git repo); no rollback for code edits | High |
| O2 | **No backup** of `studio.db`, `data/facebook/*`, Hub CSVs | High |
| O3 | Ads (and any future Shopify-via-connector sync) depend on the Claude app being open | Medium |
| O4 | Sync failures invisible beyond one line; no per-source health | Medium |
| O5 | d3 from CDN; no offline fallback | Low |
| O6 | Server output not persisted; crash cause unknowable after restart | Low |

### 3.3 Security

| # | Risk | Severity |
|---|---|---|
| S1 | Dashboard binds `0.0.0.0` with **no authentication**; anyone on the home Wi-Fi can read schedule, captions, numbers | Medium (LAN only, read-only) |
| S2 | PostZen key in plain text in `Downloads\key.txt` | Medium |
| S3 | `/data` and `/health` unauthenticated; no write endpoints (good) | Low |
| S4 | Claude task runs in Auto mode with ad-account access; prompt restricts it to reads | Low (instruction-based, not permission-based) |

### 3.4 Duplicated or disconnected functionality

- **Two economics models**: Hub 1.0 `economics.py` / `products.csv` (13 products) and the newer
  `profitability_model.py` / `test_product_economics.py` / `pricing_study.py` (92 products, EPROLO costs). The
  dashboard uses neither. One canonical product-economics module should feed Store Analytics.
- **Two experiment/creative registries**: Hub 1.0 `creatives.csv` / `experiments.csv` (0 experiments) and Studio
  `episodes`. Neither knows about Facebook posts or the AI picture batches.
- **Two ad-metrics paths**: Hub 1.0 `metrics_sync.py` → `data/metrics.csv` (empty) and the new `ads_snapshot.py`.
- **Duplicate JS helpers** across `index.html` and `metrics.html`.

---

## 4. Reuse map (what to keep)

| Keep | Why |
|---|---|
| Python `http.server` + SQLite + vanilla JS + d3 | Adequate for one operator and < 100k rows; no framework needed |
| `studio.db` state machine, `transitions`, gates | Solid, tested, owner-approved workflow |
| `publishing.sync` / `facebook_photos.sync_dashboard` | Working PostZen integration incl. `sync-external` |
| `ads_snapshot.py` merge-by-key pattern | Generalise into the history store |
| `hub_env.py` secrets via env vars | Extend to Windows Credential Manager or a set user env var |
| `profitability_model.py` / `test_product_economics.py` formulas | Become the product-economics engine |
| `decide.py` creative statuses + `config/hub.json` rules | Become the first rule-based "intelligence" layer |
| `log.md` discipline | Keep; add machine-readable sync/audit log alongside |

---

## 5. Recommended improvements (ranked)

Scored 1–5 (5 = best): **Impact** on the business question, **Effort** (5 = small), **Data available now**,
**Risk** (5 = safe), **Dependencies** (5 = none).

| Rank | Improvement | Impact | Effort | Data | Risk | Deps | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Version control (local git) + nightly backup of db/data | 4 | 5 | 5 | 5 | 5 | Prerequisite for every other change; local only |
| 2 | One UTM convention for every link we create (organic posts, Meta, TikTok, Microsoft) + a launch-day check that live TikTok clicks fill their macros | 5 | 5 | 5 | 4 | 4 | Before ad spend starts; any change to live/draft ad URLs needs owner OK |
| 3 | Honest empty/unknown states (`No cap`, `Not connected`, `No data`) | 3 | 5 | 5 | 5 | 5 | Fixes the "$0.00 cap" confusion |
| 4 | Shopify read-only sync: daily sales, orders, sessions funnel, referrer/UTM, products | 5 | 3 | 4 | 4 | 3 | Needs a decision on access (see §6) |
| 5 | History store: append-only daily snapshots for organic, ads, store; fill `metrics` table | 5 | 3 | 4 | 4 | 5 | Unlocks comparisons, 24/48/72 h, trends |
| 6 | Sync health page: per-source last success/attempt, rows, duration, error | 4 | 4 | 5 | 5 | 5 | Cheap, high trust value |
| 7 | One reporting timezone (America/New_York) across all sources | 3 | 3 | 4 | 4 | 4 | PostZen UTC buckets need re-bucketing from timestamps where available |
| 8 | Overview page: store revenue/orders, ad spend, blended cost per order, sessions, organic reach, with period comparison | 5 | 3 | 3 | 5 | needs 4,5 | Executive view; shows "No orders yet" honestly |
| 9 | Product economics in the dashboard (contribution, break-even CPA/ROAS per product) | 4 | 3 | 5 | 5 | 4 | Formulas exist; just wire them |
| 10 | Complete generation-cost ledger (all providers) | 3 | 3 | 3 | 5 | 5 | Higgsfield/OpenRouter/Kalodata usage records |
| 11 | Navigation + design system (sidebar, 6 sections, dark theme, shared components) | 3 | 2 | 5 | 4 | 5 | Do after data foundations; migrate, don't rewrite |
| 12 | Ads drill-down (campaign → ad set/group → ad; PMax asset groups) | 3 | 3 | 2 | 5 | 4 | Little to show until delivery starts |
| 13 | Attribution views (platform-claimed vs Shopify UTM vs blended) | 5 | 3 | 2 | 4 | needs 2,4 | Valuable once orders exist |
| 14 | Dashboard password + bind/firewall review; PostZen key to env/Credential Manager | 3 | 4 | 5 | 4 | 5 | |
| 15 | Rule-based alerts (sync stale, ad stopped, spend without sales, cap near) | 4 | 3 | 3 | 5 | needs 5,6 | Transparent thresholds only |
| 16 | Experiment registry unified with episodes/posts/ads | 3 | 3 | 2 | 5 | 5 | Reuse `experiments.csv` schema in SQLite |
| 17 | Creative comparison, opportunity scoring, anomaly detection | 3 | 2 | **1** | 4 | needs 5,13 | Defer: 2 live videos, 0 orders, $0 spend |
| 18 | Independent ads sync via direct APIs | 2 | 2 | 5 | 3 | owner setup | Only if the Claude-app dependency hurts in practice |

---

## 6. Decisions needed from the owner before Phase B/C

1. **Shopify access for the dashboard.** Options:
   - **(a) Shopify custom app, read-only Admin API token** (scopes: `read_orders`, `read_products`, `read_inventory`,
     `read_reports`, `read_analytics` where available). The PC syncs every 15 min on its own; no Claude app needed.
     Requires you to create the app in Shopify admin and store the token as a user env var. *Recommended.*
   - **(b) Claude scheduled task through the Shopify connector**, like the ads refresh. No setup, but hourly at best
     and only while the Claude app is open.
2. **Local git repository** for the Hub (no remote, nothing leaves the PC) and a nightly backup of `studio.db` and
   `data/` to a `backups/` folder (or another drive). *Recommended.*
3. **Generation caps**: keep "no caps" (your 10/26 decision) and show it as **No cap**, or set daily/weekly limits.
4. **Dashboard password** on the home network: yes/no.
5. **Ad tracking convention**: approve one UTM scheme for all platforms (see the architecture doc §5). Existing ad
   URLs are only changed with your OK; for TikTok, first confirm on the first live clicks whether `__CAMPAIGN_NAME__`
   is filled (preview clicks of a draft leave it empty).
6. **Bot/test traffic**: accept Shopify's numbers as-is with a warning, or exclude flagged days (10/23–10/24) from
   conversion-rate KPIs.
