# Guardrails, kill switch, daily report

## Hard limits (server-side, can't be bypassed)

They are enforced **inside every platform write**, so they hold no matter what asked for the change:
Claude, an auto-approve rule, the CLI, or a bug. They are also checked when a proposal is created, so
Claude gets an immediate, specific "no".

| Setting | Default | Meaning |
|---|---|---|
| `read_only` | `true` | Master switch for all writes. Turn off when you're ready. |
| `kill_switch` | `false` | Emergency stop: blocks every write, regardless of anything else. |
| `daily_spend_cap` | not set | Sum of all **active** daily budgets (all platforms) may not exceed it. Once today's actual spend reaches it, no budget may go up. **Not set = every spend-increasing action is blocked.** Cuts and pauses are always allowed. |
| `max_budget_change_pct` | `20` | Per campaign or ad set, **per day, cumulative**: measured from the budget it had before its first change today, so +20% three times is still blocked after the first. |
| `max_new_ads_per_day` | `5` | Ads the hub creates per day (store timezone), all platforms together. |
| `higgsfield_monthly_cap_usd` | not set | Creative generation; a whole batch must fit (see `docs/creatives.md`). |

Only entities the hub has synced can be changed. An unknown campaign is refused until the next ad sync,
because its budget can't be checked. Every refusal is recorded in `actions_log` as `blocked`, with the reason.

```bash
docker compose exec api python -m app.cli guardrails                    # limits + today's usage
docker compose exec api python -m app.cli settings set daily_spend_cap 300
docker compose exec api python -m app.cli settings set max_budget_change_pct 15
docker compose exec api python -m app.cli settings set max_new_ads_per_day 4
docker compose exec api python -m app.cli settings set read_only false  # go live
```

Auto-approve rules sit *under* these limits: a rule can skip your approval, never a limit. Example of
pre-approving small budget nudges and all pauses:
```bash
docker compose exec api python -m app.cli settings set auto_approve_rules \
  '[{"name":"small-bumps","action_type":"budget_change","max_change_pct":10,"max_amount":100},
    {"name":"pauses","action_type":"pause_ad"}]'
```

## Kill switch

* **From Claude:** "stop everything" calls `emergency_stop(reason)`. It turns the kill switch **on**
  immediately, with no approval needed. Claude has no tool to turn it off.
* **From the VM:** `docker compose exec api python -m app.cli kill-switch on|off`.
* Every toggle posts to Slack. While it's on, the hub changes nothing on any platform: no budgets, no ads,
  no generation, no conversions. Ads already running keep running. To stop spend, pause them in the
  platforms, or turn the kill switch off, approve the pauses, and turn it on again.

## Daily summary (Slack)

Every day at **08:00 store time** the hub posts yesterday's numbers:
* revenue, orders, and ad spend by platform
* contribution profit after ads, vs the day before and the 7-day average
* margin, MER and new-customer orders
* per-platform CPA and after-spend profit
* the top creative
* every action taken (counts, executed approvals, blocked attempts with reasons)
* pending approvals, Higgsfield spend vs cap, and any active alerts

```bash
docker compose exec api python -m app.cli report daily                 # preview yesterday
docker compose exec api python -m app.cli report daily --date 2026-10-01 --send
```
It needs `SLACK_WEBHOOK_URL`. A missed report (VM down at 08:00) shows up as a stale `daily_report` job
in the watchdog.
