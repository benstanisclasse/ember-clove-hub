# Talking to the hub through Claude (MCP)

The hub serves one MCP server at **`https://hub.my-domain.com/mcp`**, over streamable HTTP through the
Cloudflare Tunnel. It has high-level tools only, and every result is pre-computed, with currency and
date range:

| Read (safe, no approval) | Write (creates a proposal; nothing runs until you approve) |
|---|---|
| `get_business_summary(period)` | `propose_budget_change(platform, level, external_id, new_daily_budget, rationale)` |
| `get_profit_by_product(period)` | `propose_pause_ad(platform, external_id, rationale, level=ad)` |
| `get_platform_performance(period)` | `propose_activate(platform, level, external_id, rationale)` |
| `get_campaigns(platform?, period)` (ids for proposals) | `generate_creatives(brief, product_id, n, model)` (shows the cost estimate) |
| `get_top_creatives(period, metric)` | `launch_creative(creative_id, platforms, budget, landing_url?, primary_text?)` |
| `get_creative_trait_insights(period)` | `approve_action(id)` / `reject_action(id, reason)` |
| `get_budget_recommendation()` / `get_model_status()` | `propose_budget_reallocation(window_days)`: bandit budget proposals |
| `get_pending_approvals()` / `get_generation_spend()` | `emergency_stop(reason)`: kill switch **on**, immediately (Claude can't turn it off) |

Periods: `today`, `yesterday`, `last_N_days` (complete days), `this_month`, `last_month`,
`YYYY-MM-DD..YYYY-MM-DD`, all in the store's timezone.

Every call, read or write, is recorded in `actions_log` with the connected client's name. Executions also
pass the guardrails and the read-only / kill-switch gate. Auto-approve rules
(`settings set auto_approve_rules '[...]'`) can let small, safe actions skip the queue, for example pauses.

## Connect Claude (web, Desktop, mobile)

Prerequisite: the Cloudflare Tunnel is up (`docs/cloudflare-tunnel.md`), and `PUBLIC_BASE_URL` is set to
that https URL.

1. Claude > **Settings > Connectors > Add custom connector**.
2. Name: `Shopify hub`. URL: `https://hub.my-domain.com/mcp` (must match `PUBLIC_BASE_URL` + `/mcp` exactly).
3. Leave *Advanced settings* at their defaults. Claude registers itself through Dynamic Client Registration,
   or Claude's published client metadata.
4. **Connect.** A "Connect Claude to your Shopify hub?" page opens. Enter your **owner password**, the
   `MCP_OWNER_PASSWORD` value in `~/shopify-hub/.env` on the VM, then **Allow**.
5. Per tool, choose under Customize > Connectors > Shopify hub: *Always allow* for the read tools, and
   keep *Ask* for the write tools.

How it works: the hub runs a small single-owner OAuth 2.1 server. It uses PKCE S256, 1-hour access tokens
and 30-day rotating refresh tokens, and stores only token hashes. Only someone with the owner password can
connect a new client. Five wrong attempts lock that IP for 15 minutes. To see or cut off connected clients:
```bash
docker compose exec api python -m app.cli mcp clients
docker compose exec api python -m app.cli mcp clients --revoke <client_id>
```

## Connect Claude Code

With the static token from `.env` (`MCP_BEARER_TOKEN`):
```bash
claude mcp add --transport http shopify-hub https://hub.my-domain.com/mcp --header "Authorization: Bearer <MCP_BEARER_TOKEN>"
```
On your LAN, `http://192.168.1.210:8081/mcp` works too. Claude Code can also use the OAuth flow
(`claude mcp add --transport http shopify-hub https://hub.my-domain.com/mcp`, then `/mcp` to sign in).
Write tools carry `anthropic/requiresUserInteraction`, so Claude Code asks before every write, even in
auto mode.

## Approvals

* Ask Claude for a change, for example "cut the Fall campaign budget 10%". Claude calls
  `propose_budget_change` and shows you the one-line summary: `meta campaign 'Fall': daily budget 50.00 -> 45.00 (-10.0%)`.
* Say "approve 12" and Claude calls `approve_action(12)`. Each proposal executes **once**. It expires
  after 72 h (`APPROVAL_EXPIRY_HOURS`).
* If you'd rather never let Claude approve, run `settings set approvals_via_mcp false`. Then approve from
  the VM instead:
  ```bash
  docker compose exec api python -m app.cli approvals list
  docker compose exec api python -m app.cli approvals approve 12
  ```
* `read_only` (on by default) still blocks execution: approved proposals then fail with "read-only mode is on".

Example prompts: *"How did we do last week vs the week before, after ad spend?"*, *"Which hook types make
the most profit per $1,000?"*, *"Generate 4 POV-hook videos for product 3 and tell me the cost."*,
*"Launch creative 18 on Meta and TikTok at $20/day."*
