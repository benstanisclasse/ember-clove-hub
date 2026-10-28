# Ember Studio Dashboard 2.0 — Implementation Plan

Status: **for owner approval.** Ordering follows the ranking in `DASHBOARD_AUDIT.md` §5: measurement before
modelling, foundations before visuals. Each phase ends with a short report (features, files, database changes,
tests, results, open issues, next phase) and a checkpoint with the owner.

Reality check that shapes the order: **0 store orders and $0 ad spend to date** (2026-10-27). Phases B–D make the
dashboard ready to measure the first sales correctly; Phases E–G only become meaningful as orders and spend arrive.

---

## Phase B — Core reliability (≈ 1–2 sessions)

| # | Task | Acceptance criteria |
|---|---|---|
| B1 | Local git repo for the Hub (`.gitignore` for media, db, keys, inbox); initial commit | `git log` shows baseline; no secrets or large media tracked |
| B2 | Nightly backup job (`studio.db`, `data/`, `config/`, docs) → `backups/<date>/`, keep 14 | Restore drill: copy back a backup into a scratch folder and open it |
| B3 | Honest states on today's pages: caps `null` → **No cap (owner, 10/26)**; unknown ≠ 0; stale data dimmed with age | Cap tile reads "No cap"; a missing dataset shows "Not connected", never "0" |
| B4 | Sync health: per-job `sync_runs` (start, end, ok, rows, error); jobs isolated so one failure doesn't skip the rest; server log to `logs/dashboard.log` | Kill PostZen access in a test → Facebook/TikTok rows show the error, ads still fresh |
| B5 | `analytics.db` with `post_snapshots` + `account_daily` + `ad_daily` (append-only); organic and ads syncs start writing history | After 24 h, a post has ≥ 48 snapshots; `ad_daily` keeps revisions |
| B6 | Reporting timezone utility (Eastern) used by every new query; label UTC-bucketed PostZen daily totals | Unit tests for DST boundaries (Nov 1 2026 fall-back) |
| B7 | Vendor d3 locally | Pages render with network to CDN blocked |
| B8 | Tests: server endpoints, sync output shapes, `ads_snapshot.merge`, formula helpers | New tests pass with the 38 existing |

**Owner input:** OK to create the local git repo and backups folder; cap display wording.

## Phase C — Shopify integration (≈ 2 sessions) — highest business value

| # | Task | Acceptance criteria |
|---|---|---|
| C1 | Access per owner decision: (a) custom app read-only token in user env var, or (b) Claude task drop-feed every hour | Health page shows Shopify "OK", last sync time |
| C2 | Daily store metrics via ShopifyQL (`FROM sales`, `FROM sessions` by referrer/UTM) and Admin GraphQL (orders, lines, refunds, products, variants, inventory) with pagination and rate-limit backoff | Totals for any day match Shopify Analytics to the cent; order count exact |
| C3 | Store Analytics page v1: net sales, orders, AOV, sessions, funnel (cart → checkout → purchase), sessions by channel/UTM, traffic-quality flag | Shows "No orders yet" correctly today; 10/24 flagged |
| C4 | Products: price, inventory, units sold, net sales, refunds, cost and contribution from `profitability_model.py` | Economics per product match `profitability_2026-10-25.csv` / current prices |
| C5 | Reconciliation test: dashboard vs Shopify for 3 sample days | Differences explained in the phase report |

**Owner input:** Shopify access option (a) or (b); if (a), create the custom app (I list exact scopes and clicks).

## Phase D — Navigation, design system, Overview (≈ 2–3 sessions)

| # | Task | Acceptance criteria |
|---|---|---|
| D1 | Shared `static/app.css` + `components.js` (KPI card with delta/sparkline/source/freshness, tables with sort/filter/CSV, badges, drawer, date-range control with compare) | Old pages render using shared components with no visual regressions |
| D2 | Sidebar + six sections; migrate Control room and Metrics content per the migration map (Architecture §7) | Regression checklist: every current component present and correct |
| D3 | Overview: revenue, orders, ad spend, MER, blended cost per order, sessions, conversion rate, organic reach, followers, generation cost — each with previous-period comparison | Numbers match their source pages; missing states shown |
| D4 | Content Studio calendar: week/month/day/list, filters (channel, status, product, series), item detail drawer with production history from `transitions` | All 21 episodes and 12 Facebook posts placed correctly in Eastern time |
| D5 | Dark-first theme in brand colours; phone layout for Overview, alerts, schedule, campaigns, health | Checked at 375 px, 768 px and desktop |

## Phase E — Attribution (as soon as ads deliver)

| # | Task | Acceptance criteria |
|---|---|---|
| E1 | UTM convention adopted for new organic links (Facebook planner, TikTok link) | New posts produce sessions under the expected source/medium/campaign |
| E2 | Ad URL parameters checked on first live clicks per platform; fixes proposed to owner | Shopify shows `paid_social` / `paid_search` sessions per campaign |
| E3 | Advertising page: campaign → ad set/group/asset group → ad drill-down, trends (spend, CPC, CTR, CPA, ROAS) | Matches each platform's own UI for a sample day |
| E4 | Three lenses side by side (platform-claimed, Shopify-attributed, blended) with confidence labels | Platform claims never added to store orders |

**Owner input:** approval for any change to live or draft ad URLs.

## Phase F — Profitability (once orders exist)

- Product and order contribution, break-even ROAS, allowable CPA, MER trend, cost composition, generation-cost
  ledger completed across providers (Higgsfield, OpenRouter, Kalodata, Seedance direct).
- Budget settings (daily/weekly/monthly, per platform, target CPA starting at the $20 planning figure) — **display and
  alert only; nothing changes spend.**
- Acceptance: a test basket (single and multi-item) reproduces the model's numbers; modelled profit is labelled
  "estimate".

## Phase G — Intelligence (rule-based first; when ≥ ~2 weeks of history)

- Daily summary (what changed vs previous period, with numbers and sample sizes).
- Alerts with transparent thresholds: sync stale, campaign delivering with spend and no store sessions, spend without
  orders above X, CPA > allowable for N days, scheduled post failed, cap approaching, low inventory on promoted
  products, expired credentials.
- `decide.py` creative statuses applied to live ads (STOP-LOSS, TRACKING-CHECK, LEARNING, PROMISING, WEAK…), shown as
  **recommendations only**.
- Experiment registry in SQLite (schema from `data/experiments.csv`), linked to episodes, posts and ads; results
  labelled Winner / Loser / Inconclusive / Collecting with minimum sample rules.
- Creative comparisons and opportunity scoring **after** there are enough posts, ads and orders; every insight shows
  sample size and limitations.

## Phase H — Hardening

- Regression run against the checklist below, security review (password, bind, firewall, secrets), Windows startup
  test after reboot, performance check (page < 1 s on LAN, `/api/v2` < 200 ms), maintenance docs
  (`docs/DASHBOARD_OPERATIONS.md`: start/stop, backups/restore, adding a source, metric definitions).

---

## Regression checklist (every phase)

TikTok scheduling and draft sends · Facebook planning and sends · PostZen sync incl. `sync-external` · publishing
status · production pipeline · first-week table · generation spend · Meta/TikTok/Microsoft ads section · unified
calendar · Windows startup task · LAN access · 38 studio tests.

## Approval rules (unchanged)

The dashboard and its jobs only **read** platforms. Publishing, ad creation or edits, budgets, pausing/enabling,
prices, listings, purchases and deleting production data each need the owner's explicit OK. Backups are taken before
any database migration.

## Decisions requested now

1. Approve the order **B → C → D → E**, with F–G started as data arrives.
2. Shopify access: **(a) custom app token** (recommended) or **(b) Claude task feed**.
3. Local git repo + nightly backups: yes/no.
4. Generation caps: keep **No cap** (display fix only) or set limits.
5. Dashboard password on the home network: yes/no.
6. Bot/test traffic: flag and exclude flagged days from conversion KPIs (raw kept), yes/no.

---

## Phase B report (2026-10-27, approved by owner: "Approved: order B, C, D, E ... Start Phase B.")

**Implemented**
- B1 Local git repository (3+ commits), `.gitignore` excludes media, raw exports, databases, backups, logs, secrets;
  line endings kept as-is (bible approvals are content-hash locked). 315 files tracked, none containing keys.
- B2 `scripts/backup_hub.py` + Windows task "Ember Hub Nightly Backup" (02:30, S4U, test run result 0). Daily snapshot
  ≈ 5 MB (keep 14) + append-only media mirror (268 MB first run). Restore drill: backup row counts = live.
- B3 Honest states: weekly/daily cap read "No … cap set (owner choice, 10/26)" instead of $0.00; spend bars no longer
  turn red against a non-existent cap; missing sources say "Not connected yet"; stale data marked "(stale)" and dimmed;
  UTC-bucketed PostZen days labelled.
- B4 Sync jobs isolated (TikTok, Facebook, History) and recorded in `sync_runs`; ads refreshes recorded as
  `ads:meta|tiktok|microsoft`; health dots in every page's top bar with hover details; `/health` lists jobs;
  `logs/dashboard.log` (rotating 1 MB × 5).
- B5 `studio/analytics.db`: `post_snapshots` (append-only per sync), `account_daily`, `ad_daily` (+ `ad_daily_latest`).
- B6 `analytics.local_day()` / `day_bounds_utc()` (America/New_York, DST-correct).
- B7 d3 7.8.5 served from `studio/dashboard/static/` (checksum identical on jsdelivr and unpkg).
- B8 `scripts/studio/test_dashboard.py` (11 tests): DST days, job health, snapshots, followers, ad revisions, ads merge,
  pages, `/data` shape, static path-traversal. **49/49 tests pass.**

**Files changed:** `.gitignore`, `CLAUDE.md`, `scripts/backup_hub.py` (new), `scripts/studio/analytics.py` (new),
`scripts/studio/test_dashboard.py` (new), `scripts/studio/dashboard_server.py`, `scripts/ads_snapshot.py`,
`studio/dashboard/index.html`, `studio/dashboard/metrics.html`, `studio/dashboard/static/d3.min.js` (new).

**Database changes:** new `studio/analytics.db` only; `studio/studio.db` untouched (still has its unused `metrics` table).

**Verified live:** server restarted; all 6 jobs green; both pages render with local d3, no console errors.

**Known limitations / carried forward**
- History starts now: no back-filled snapshots before 2026-10-27 21:02 ET (by design).
- PostZen daily totals remain UTC-bucketed (labelled, not re-bucketed); re-bucketing needs per-post timestamps (Phase D).
- Bot-traffic flagging needs Shopify sessions → Phase C.
- Generation spend still only covers Studio video jobs (Phase F ledger).

**Next: Phase C (Shopify).** Needs the owner to create the read-only custom app token.

---

## Phase C report (2026-10-27, owner: "Yes, build the rest of Phase C now: the Shopify sync, Store Analytics page, product economics, bot-traffic flag and the reconciliation check.")

**Implemented**
- C1 Access: Dev Dashboard app "Ember Dashboard (read-only)" (scopes read_orders, read_products, read_inventory,
  read_reports, read_analytics), installed by the owner; client id/secret in user env vars; `scripts/shopify_api.py`
  exchanges them for 24 h tokens (memory only), GraphQL with backoff, ShopifyQL.
- C2 `scripts/studio/shopify_sync.py` (dashboard job "shopify", every 15 min, ~5 s): last 90 days of sales and the
  sessions funnel per Eastern day; sessions by referrer and by UTM per day; orders + lines incremental by updated_at
  (first/last visit source, UTM, landing page; no names, emails or addresses); active products and variants (price,
  unit cost, weight, stock). Tables in `studio/analytics.db`: store_daily, store_sources_daily, orders, order_lines,
  products, variants.
- C3 Store page (`/store`, nav "Store"): net/total sales, orders, AOV, visits, conversion, cart rate for 7/14/30 days;
  visits and net sales per day; purchase funnel; traffic sources; tracking tags; data check.
- C4 Product economics for all 92 active products, from `profitability_model.contribution` / `.ship` (same basis as
  the price changes): price (a real variant price), unit cost, supplier shipping, contribution before ads, margin,
  break-even CPA/ROAS, kept after the $20 planning ad cost, stock, 30-day units and net sales. Labelled "Estimate".
- Bot-traffic flag: ≥ 100 visits, ≥ 3× the median of nearby days with traffic (±7 days, ≥ 2 such days), < 1% adding to
  cart. Flags 10/24 only (1,104 visits). Excluded from visits/conversion KPIs by default; raw totals stay visible.
- C5 Reconciliation every sync, last 30 days: orders, net sales, total sales, sessions (stored daily sum vs Shopify's
  own total) and stored orders vs Shopify's order count. All 5 checks pass (sessions 2,147 = 2,147).

**Tests:** 5 new (bot flag ×2, economics vs model, reconciliation mismatch, store page) — **54/54 pass.**

**Files:** `scripts/shopify_api.py` (new), `scripts/studio/shopify_sync.py` (new), `studio/dashboard/store.html`
(new), `scripts/studio/dashboard_server.py`, `scripts/studio/test_dashboard.py`, `config/hub.json` (secret names).

**Findings surfaced by the new page**
- 0 orders so far; 1,043 visits excluding the flagged day; 4 reached checkout, 0 purchased.
- Of 30-day visits: direct 1,857, Facebook 278, TikTok 5; tagged visits: `fb_photos` 5, TikTok ads with unfilled
  `__CAMPAIGN_NAME__` 3 (likely previews).
- About 70 products keep un-rounded prices (e.g. $35.78, $41.50); only the 22 repriced on 10/27 end in .99.
- No product loses money at the $20 planning ad cost, but several keep under $1 per order after it.

**Limitations:** product-level conversion needs per-product sessions (not in this sync); refunds are taken at order level;
orders older than 60 days would need read_all_orders (not needed yet, store opened 10/23).

**Next: Phase D** (navigation, design system, Overview with store + ads + organic together).

---

## Phase D report (2026-10-27, owner: "Yes, start Phase D: the shared design system, sidebar navigation with the six sections, the Overview page and the improved content calendar.")

**Implemented**
- D1 Design system: `studio/dashboard/static/app.css` (dark-first Ember & Clove palette, light theme toggle remembered per
  browser, shared card/table/chart/KPI/alert/drawer/calendar styles) and `static/components.js` (`ui.*`: KPI card with
  previous-period change, sparkline, source and freshness dot; bars; sortable table with totals and CSV export; detail
  drawer; period helpers; rule-based `ui.alerts`). Unknown values render as states (`Not connected`, `No orders yet`,
  `No ad spend yet`, `Needs orders first`), never as 0.
- D2 Sidebar shell with six sections: Overview `/`, Content Studio `/content` (+ Performance `/content/performance`),
  Advertising `/ads`, Store `/store`, Intelligence `/intelligence`, Operations `/ops`. Old `/index.html` and `/metrics`
  redirect (301). Phone layout: sticky top bar with scrolling sections, KPI cards two per row, no sideways scrolling.
  Our CSS/JS are version-tagged and not cached; only d3 is cached.
- D3 Overview: 7/14/30-day KPIs with the previous period (net sales, orders, ad spend, MER, blended cost per order,
  visits without bot days, conversion, organic reach, followers, content cost, contribution profit marked "needs
  orders"), switchable performance chart, Today panel (scheduled today, waiting in TikTok drafts, waiting approval,
  failed, live campaigns, delivering today, next posts), Needs-attention alerts, channel table (organic reach, store
  visits by channel, ad spend, clicks, platform claims — never added to store orders).
- Advertising page (paid-ads section moved here from Metrics): KPIs with comparison, spend per day stacked by platform,
  per-platform cards with what is running, platforms table with CTR/CPC/CPM/CPA/ROAS and CSV export.
- Intelligence page: every rule-based finding with why it matters, evidence and suggested action; honest "what the data
  can say yet"; Phase G plan.
- Operations page: sync-health table, backups (from new `system_info` file), automatic jobs, content cost chart with
  "No cap", read-only settings.
- D4 Content calendar: Week / Month / Day / List views, prev/next/today, filters (channel, status, series/post type,
  product or caption search), CSV export of the list, detail drawer per post with the full production history
  (new `episode_history` file from `studio.db` transitions).
- D5 Dark-first theme in brand colours; checked at 375 px and desktop.

**Verified live:** all 7 pages load with the right section highlighted and no console errors; calendar views, filters,
search and drawer exercised; KPI states correct with today's data (Meta began delivering: $0.44, 16 impressions).
**Tests:** 3 new (redirects, sidebar/assets on every page, new datasets) — **57/57 pass.**

**Files:** new `static/app.css`, `static/components.js`, `overview.html`, `ads.html`, `intelligence.html`, `ops.html`;
changed `dashboard_server.py` (shell, routes, redirects, system_info, episode_history, caching), `index.html`
(Content Studio + calendar), `metrics.html` (Content performance; ads moved out), `shopify_sync.py` (store_daily file
keeps 90 days for comparisons), `test_dashboard.py`.

**Not done / limits**
- Existing Content Studio, Performance and Store pages keep some of their own helper code (they work and look
  consistent via the shared tokens); folding them fully onto `ui.*` is clean-up, not a feature.
- Comparisons for ads show "no previous period data" until 60 days of ad history exist.
- Thumbnails in the calendar need asset paths exposed safely (Phase E/F with the creative library).
- Global date control is per page (Overview, Advertising, Store), not yet one shared header control.

**Next: Phase E (attribution)** as ads deliver: UTM convention for new links, launch-day macro check, campaign/ad-level
drill-down, and the three lenses (platform-claimed, Shopify-attributed, blended).

---

## Phase E report (2026-10-28, owner: "can we contineue on" — continuing the approved order B → C → D → E)

**Implemented**
- E1 Tracking convention: `scripts/attribution.py` — `tag_link()` (facebook/instagram/tiktok organic = `organic_social`,
  Meta/TikTok = `paid_social`, Microsoft = `paid_search`), `channel_of()` (UTM first, referrer second, with confidence
  Directly tracked / Inferred / Unattributed; the old `social` medium maps to organic), `unfilled_macros()`. The
  Facebook planner's links now use it (uncommitted in `facebook_photos.py` together with the Content Studio session's
  work on that file — that session commits it).
- E2 Store-side attribution in `shopify_sync`: each order gets a channel and confidence (last visit's UTM, then first,
  then visit source); tagged visits by channel; unfilled tags reported → `store_attribution.json`. Alerts for unfilled
  tags and for live campaigns whose links carry no tags.
- E3 Drill-down: `ads_snapshot.py` accepts each platform's structure (campaign → ad set / ad group / asset group → ad)
  with totals and tracking-tag status → `ads_entities.json`, history in `analytics.db` (`ad_entities`). The 3-hour
  Claude task now collects it (prompt updated). Advertising page: expandable campaign tree with status, budget, spend,
  CTR, CPC, claims and tags.
- E4 Three lenses on the Advertising page: platform-claimed purchases/revenue, store visits and orders carrying that
  platform's tags, and blended (all ad spend vs whole store: cost per order, MER) — never added together.

**Findings from the first pull**
- Meta "EC | Page follows | Test F2" ($5/day) delivered on 10/27: $1.19–1.22, 50–51 impressions, 11 clicks (CTR 21.6%,
  $0.11/click); Turtleneck sweater dress ad took $0.95. These are Like-Page ads: no store link, so no tags needed and no
  store visits expected.
- Microsoft "PMax Ember & Clove" ($20.80/day) has **no tracking tags** (URL suffix and tracking template empty): its
  store visits will look like ordinary search/direct. Fix = add a final URL suffix, e.g.
  `utm_source=microsoft&utm_medium=paid_search&utm_campaign={CampaignId}` — a change to a live campaign, **needs owner OK**.
- TikTok: 3 visits with an unfilled `__CAMPAIGN_NAME__` (likely previews of the unpublished draft); check on launch.

**Tests:** 17 new (link builder, 13 channel cases, macros, order channel, entity merge) — **74/74 pass.** Verified live:
Advertising page tree and lenses, new alerts, no console errors.

**Next:** F (profitability engine — can be built now and lights up with the first orders), then H, then G.
