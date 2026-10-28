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
