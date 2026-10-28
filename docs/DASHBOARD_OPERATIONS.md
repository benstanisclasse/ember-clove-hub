# Ember Studio Dashboard — Operations Guide

How to run, check, fix, back up and extend the dashboard. Written 2026-10-28 (Dashboard 2.0, Phase H).
Architecture and metric definitions: `DASHBOARD_ARCHITECTURE_V2.md`. Phase history: `DASHBOARD_IMPLEMENTATION_PLAN.md`.

## 1. What runs where

| Piece | Where | When |
|---|---|---|
| Dashboard server (`scripts/studio/dashboard_server.py`) | Windows task **Ember Studio Dashboard** (runs `scripts/studio/run_dashboard.cmd`) | Starts ~1 min after boot; restarts 3× (5 min apart) if it crashes |
| Sync jobs inside the server: TikTok, Facebook, Shopify (+ attribution + profit), Content, History | same process | Every 15 min; each job independent |
| Ads refresh (Meta, TikTok; Microsoft removed 2026-10-28) | Claude scheduled task **ads-dashboard-refresh** (Claude app, Auto mode, read-only) | Every 3 h at :20, only while the Claude app is open |
| Nightly backup (`scripts/backup_hub.py`) | Windows task **Ember Hub Nightly Backup** | 02:30 daily; retries 2× (15 min apart) |

Pages (home network only): `http://192.168.1.215:8790/` — Overview, `/content` (+ `/content/performance`), `/ads`,
`/store`, `/intelligence`, `/ops`. Old `/metrics` and `/index.html` redirect.

## 2. Is it healthy?

- Every page's top bar: one ✓ / ! / ✕ per source (hover for last success and error). **Operations → Sync health**
  has the full table.
- `http://192.168.1.215:8790/health` — JSON with every job's last attempt, last success, rows, seconds and error.
- Log: `logs/dashboard.log` (rotates at 1 MB, keeps 5).
- Expected freshness: organic/store/content within ~15 min; ads within ~3 h (if the Claude app was open).

## 3. Start, stop, restart (PowerShell)

```powershell
Start-ScheduledTask -TaskName "Ember Studio Dashboard"
Stop-ScheduledTask  -TaskName "Ember Studio Dashboard"
# full restart (also stops a stray server process):
Stop-ScheduledTask -TaskName "Ember Studio Dashboard"
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*dashboard_server*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-ScheduledTask -TaskName "Ember Studio Dashboard"
```
A restart is needed after changing server code (`dashboard_server.py`, any sync module). Page files (`studio/dashboard/*.html`,
`static/*`) are read on every request: no restart, just reload the page. Cold start: page up in ~2 s, first full sync ~17 s.

## 4. Credentials (never in files, logs or pages)

| Secret | Where it lives | Used by |
|---|---|---|
| PostZen key | `pzn_…` token in `%USERPROFILE%\Downloads\key.txt` (read by `run_dashboard.cmd`); `POSTZEN_API_KEY` user env var if set | TikTok/Facebook sync, publishing |
| Shopify app | `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET` user env vars (Dev Dashboard app "Ember Dashboard (read-only)") | Shopify sync (24 h tokens kept in memory) |
| Higgsfield, Kalodata, OpenRouter | user env vars named in `config/hub.json` → `secrets` | content generation / research |

Rotate a secret: update it at the provider, then in a Command Prompt `setx NAME "new value"`, close that window, restart
the dashboard. Recommended: set `POSTZEN_API_KEY` as a user env var and delete `key.txt` (the server prefers the env var).
Phase H check (2026-10-28): no secret value appears in any page, `/data`, dashboard data file or log.

## 5. Security posture

- Read-only server: GET only (POST/PUT/DELETE/PATCH → 501); no endpoint publishes, spends or edits anything.
- Listens on all interfaces, port 8790; Windows Firewall rule **Ember Studio dashboard (LAN)** allows the local subnet
  only, Private/Domain profiles. Never forward this port on the router.
- No password (owner choice, 2026-10-27). Anyone on the home Wi-Fi can read the dashboard.
- Headers on every response: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`,
  `Referrer-Policy: no-referrer`; no Python version banner. Static and frame-sheet routes refuse paths outside their folders.
- No customer names, emails or addresses are requested from Shopify.

## 6. Backups and restore

- `backups/<YYYY-MM-DD>/` — consistent copies of `studio.db` and `analytics.db`, plus `data/`, `config/`, bible, dashboard
  files, docs, `log.md`; newest 14 kept. `backups/media_mirror/` — videos, refs, generated and original photos, add-only.
- Run by hand (do this before any database change): `python -I scripts/backup_hub.py`
- Restore a database: stop the dashboard, copy `backups/<day>/studio/studio.db` (or `analytics.db`) over the live file,
  start the dashboard. `analytics.db` can also be rebuilt by the syncs (history before the rebuild is then lost).
- Code: the Hub is a local git repository. `git log --oneline` shows history; `git show <commit>` shows a change;
  `git checkout <commit> -- <file>` brings back an older version of one file. Nothing is pushed anywhere.

## 7. Common problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Ads ✓ turns ! (late) | Claude app was closed, so the 3-hour task didn't run | Open the Claude app; the task catches up. Run it now from Scheduled in the sidebar |
| Shopify ✕ "token exchange failed" | App uninstalled, secret rotated, or env vars missing | Check the app is installed on the store (Dev Dashboard); re-`setx` both values; restart |
| TikTok/Facebook ✕ HTTP 401 | PostZen key changed or missing | Update `key.txt` or `POSTZEN_API_KEY`; restart |
| Page stuck on "Loading…" / can't connect | Server not running | `Start-ScheduledTask -TaskName "Ember Studio Dashboard"`; check `logs/dashboard.log` |
| Another device can't open the page | Firewall profile or the PC's IP changed | Network must be Private; check the PC's IP (`ipconfig`) — the address is 192.168.1.215 today |
| "Store numbers do not match Shopify" alert | Sync caught Shopify mid-update, or a real mismatch | Wait one sync; if it stays, compare Store → Data check with Shopify Analytics |
| Old-looking page after an update | Browser cache | Reload; our CSS/JS are version-tagged, so a normal reload is enough |

## 8. Changing things

- **Settings** (`config/hub.json`): `budgets` (display and alerts only), `economics` (fees, refund rate). Bible rules
  (`studio/bible/*.yaml`) need owner re-approval after any edit. Restart not needed for budgets (read each sync).
- **A new data source**: write a sync job that saves `studio/dashboard/<name>.json|csv` with
  `analytics.write_text_atomic` / `analytics.atomic_open`, wrap it in `analytics.job("<name>")` (adds it to sync health),
  register it in `JOBS` and the file name in `DATASETS` in `dashboard_server.py`, restart. Pages read it with
  `dash.data('<name>')`.
- **Real dollar costs not tracked automatically** (e.g. an image batch billed in dollars): add a row to
  `data/costs/generation_costs.csv` (date, provider, kind, usd, note); it appears in Operations and in profit after the next sync.
- **Approvals**: the dashboard and its jobs only read. Publishing, ad changes, budgets, prices, listings and deleting data
  always need the owner's explicit OK (see the Hub `CLAUDE.md`).

## 9. Tests

`python -m pytest -q scripts/studio` — all studio, dashboard, profit, content and hardening tests (151 on 2026-10-28).
Run after any change; commit only when they pass.
