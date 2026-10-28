# Shopify hub

One self-hosted server that syncs a Shopify store and its Google / Meta / TikTok ads into a
single Postgres database. It generates UGC creatives with Higgsfield and runs guarded
automations. Claude controls it through one MCP server. The number everything is judged by
is **contribution profit**, computed from Shopify orders rather than platform-reported conversions.

Runs on **VM 210 `shopify-hub` (192.168.1.210) on the `proxmax` Proxmox node**. See [docs/proxmox.md](docs/proxmox.md).

## Status

| Phase | What | State |
|---|---|---|
| 1 | Foundation: VM, stack, schema, profit views, health, backups | **done** |
| 2 | Shopify sync + webhooks + UTM/click-id capture | **built**, waiting for your app keys ([setup](docs/shopify.md)) |
| 3 | Google Ads / Meta / TikTok (read, then write) | **built**, waiting for your keys ([setup](docs/ad-platforms.md)) |
| 3b | Conversions + pixels: web pixel, Meta CAPI, TikTok Events API, Google click conversions | **built**, off until enabled ([setup](docs/conversions.md)) |
| 4 | Higgsfield generation pipeline: briefs, variants + traits, cost cap, storage, launch | **built**, waiting for your keys ([setup](docs/creatives.md)) |
| 5 | MCP server for Claude: 8 read + 7 write tools, approvals, OAuth for connectors | **built** ([connect](docs/mcp.md)) |
| 6 | Guardrails (spend cap, cumulative daily change, new ads/day), kill switch, daily Slack report | **built** ([details](docs/guardrails.md)) |
| 7 | Nightly creative metrics, Thompson-sampling budget bandit, gated LightGBM creative model | **built** ([details](docs/ml.md)) |

The hub starts **read-only**: every write action is blocked until you run
`settings set read_only false`. Spend and generation caps start unset, which blocks the
matching actions until you set them.

## Architecture

```
                Cloudflare Tunnel (public: /healthz /webhooks /oauth /mcp only)
                        │
LAN :8081 ──> caddy ────┴──> api (FastAPI) ──┐
                                             ├── postgres 17   (all data, profit views)
              scheduler (APScheduler) ──> redis ── worker (RQ)
                   │ watchdog every 5 min    └── garage (S3)   (creatives)
                   └──> Slack alerts + external heartbeat
```

| Path | Purpose |
|---|---|
| `app/models/` | SQLAlchemy models: commerce, ads, creatives, ops |
| `migrations/` | Alembic. `0001` = full schema + profit views + settings seed |
| `app/profit.py` | Profit formulas (tests check the SQL views match them) |
| `app/business_settings.py` | Runtime settings: read-only, kill switch, caps, auto-approve rules |
| `app/health.py`, `app/jobs/watchdog.py` | Health checks and alerting |
| `app/log.py` | JSON logging that masks tokens by key name and by value shape |
| `app/integrations/shopify/` | GraphQL client (client-credentials auth, cost throttling), mapping, sync |
| `app/attribution.py` | Last-touch attribution from Shopify visits / click ids / UTMs |
| `app/webhooks.py` | HMAC-verified Shopify webhooks; payloads not stored, resource re-fetched |
| `app/integrations/ads/` | Google Ads (REST + YouTube upload), Meta, TikTok behind one `AdPlatform` interface |
| `app/conversions/`, `app/collect.py`, `shopify-app/` | Web pixel extension, `/collect/pixel`, server-side purchase reporting |
| `app/integrations/higgsfield.py`, `app/creatives/` | Higgsfield client, briefs/variants/traits, generate → store → launch |
| `app/mcpserver/`, `app/approvals.py`, `app/analytics/` | MCP server + OAuth, proposals/approvals, pre-computed reports |
| `app/ml/` | Creative metric snapshots, budget bandit (proposals only), LightGBM creative profit model |
| `app/actions.py` | The write gate: read-only / kill switch, plus an `actions_log` entry for every write attempt |
| `deploy/` | Caddyfile, Garage config template, systemd units |
| `scripts/` | `setup.sh`, `deploy.sh`, `backup.sh`, `restore-test.sh`, `garage-init.sh` |

### Profit views

* `v_order_profit`: per order. `net_revenue (total − tax) − refunds (ex-tax) − COGS − shipping cost − payment fees`.
  COGS uses the line's snapshot cost, then the variant cost, then the product cost. `units_missing_cost` flags gaps.
  Cancelled and test orders are excluded.
* `v_ad_daily_profit`: per ad per day. Contribution of attributed orders minus spend. Includes days
  with spend but no orders, and days with orders but no spend.
* `v_creative_daily_profit`: per creative per day. An ad linked to N creatives is split equally between them.

## Operating it

SSH in with `ssh hub@192.168.1.210`, then `cd ~/shopify-hub`.

```bash
scripts/deploy.sh                                   # update: git pull, build, migrate, restart, verify
docker compose ps                                   # service status
docker compose logs -f api worker scheduler         # logs (JSON, tokens masked)
docker compose exec api python -m app.cli health    # all checks incl. workers + job staleness
docker compose exec api python -m app.cli settings show
docker compose exec api python -m app.cli settings set daily_spend_cap 150
docker compose exec api python -m app.cli kill-switch on                  # emergency stop (Slack alert)
docker compose exec api python -m app.cli guardrails                     # limits + today's usage
docker compose exec api python -m app.cli report daily                   # preview the daily summary
```

From the LAN: `http://192.168.1.210:8081/health/ready`, plus `/admin/settings`, which needs
`Authorization: Bearer $ADMIN_TOKEN` (the token is in `.env`).

Reliability: containers use `restart: unless-stopped`; `shopify-hub.service` starts the stack at boot;
the VM has `onboot=1`. The watchdog posts to Slack when a dependency, the worker or a scheduled job
fails, and pings `HEARTBEAT_URL` while healthy, so an external service such as healthchecks.io can
alert you if the whole VM goes down.

## Still to configure (you)

1. **Slack**: create an incoming webhook and set `SLACK_WEBHOOK_URL` in `.env`.
2. **Heartbeat**: create a free check at healthchecks.io (period 5 min, grace 10 min), connect its
   Slack integration, and set `HEARTBEAT_URL`.
3. **Cloudflare Tunnel**: follow [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md).
4. **Shopify app**: create it in the Dev Dashboard and add its keys. See [docs/shopify.md](docs/shopify.md).
   Also set `STORE_TIMEZONE`, `STORE_CURRENCY`, `STORE_NICHE`.
5. **Ad platforms**: Google Ads, Meta and TikTok. See [docs/ad-platforms.md](docs/ad-platforms.md).
   TikTok and Google developer approval can take days, so start those applications early.
6. **Tracking**: the hub runs the pixels itself; don't install the official ad-platform Shopify apps.
   See [docs/conversions.md](docs/conversions.md).
7. **Higgsfield**: API key + a video model id + a monthly cap. See [docs/creatives.md](docs/creatives.md).
8. **Offsite backups** (optional): see [docs/backups.md](docs/backups.md).

After editing `.env`, run `scripts/deploy.sh`.

## Tests

```bash
.venv/bin/pytest -q                                   # SQLite
TEST_DATABASE_URL=postgresql+psycopg://hub:hub@127.0.0.1:55432/hub_test .venv/bin/pytest -q   # real Postgres
.venv/bin/ruff check app tests migrations
```
Covered so far: profit math, SQL views vs. Python (both databases), migration round-trip and
model drift, settings validation and audit, log redaction, API auth, alert de-duplication,
watchdog and heartbeat, job staleness, storage (mocked S3); Shopify client against a mocked
transport (token grant, 401 refresh, cost throttling, 429/5xx backoff, pagination), order and
product mapping, COGS snapshots, refunds, customer aggregates, sync cursors, attribution, and
webhook HMAC, shop check, de-dup and re-enqueue.

## Platform credentials

* **Shopify**: [docs/shopify.md](docs/shopify.md) (Dev Dashboard app, scopes, backfill, webhooks, UTM templates).

* **Google Ads, Meta, TikTok**: [docs/ad-platforms.md](docs/ad-platforms.md) (developer token access level,
  OAuth consent publishing, system user, App Review, TikTok developer approval and auth-code exchange).

* **Higgsfield**: [docs/creatives.md](docs/creatives.md).

* **Claude (custom connector) and Claude Code**: [docs/mcp.md](docs/mcp.md).
