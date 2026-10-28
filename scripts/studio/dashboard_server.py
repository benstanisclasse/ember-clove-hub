"""Ember Studio dashboard on the local network: http://<this machine>:8790 (control room) and /metrics

Serves studio/dashboard/index.html (the same page as the online dashboard) and metrics.html with a small stand-in for
the online dashboard's `dash` data API, reading the files `cli.py sync` and `facebook_photos.py sync` write. Every 15
minutes it runs both syncs itself (PostZen status, TikTok and Facebook metrics, followers; calendar and spend from
studio.db; Facebook plans from data/facebook), so the pages stay current.

Each sync job (TikTok, Facebook, history snapshots) runs on its own: one failing never skips the others, and every
run is recorded in studio/analytics.db (sync_runs) and shown on the pages. Ads arrive from the Claude scheduled task
through scripts/ads_snapshot.py and are recorded the same way. Server messages and tracebacks go to
logs/dashboard.log (rotated).

Read-only: GET only, no write endpoints, no keys or prompts served. Run:
  python scripts/studio/dashboard_server.py [--port 8790] [--every-min 15] [--no-sync]
POSTZEN_API_KEY must be in the environment for the sync (scripts/studio/run_dashboard.cmd sets it).
"""
import argparse
import csv
import json
import logging
import logging.handlers
import mimetypes
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import facebook_photos  # noqa: E402
from studio import analytics, bible, db, publishing, shopify_sync  # noqa: E402

OUT = publishing.OUT
STATIC = OUT / "static"
LOG = logging.getLogger("dashboard")
DATASETS = ["schedule", "followers", "tiktok_videos", "post_timeline", "daily_metrics", "spend", "caps",
            "fb_schedule", "fb_posts", "fb_daily", "fb_followers", "ads_daily", "ads_accounts", "sync_health",
            "store_daily", "store_sources", "store_utm", "store_products", "store_reconciliation"]
JOB_LABELS = {"tiktok": "TikTok", "facebook": "Facebook", "shopify": "Shopify", "snapshots": "History", "ads:meta": "Meta ads",
              "ads:tiktok": "TikTok ads", "ads:microsoft": "Microsoft ads"}
PAGES = {"/": ("index.html", "Ember Studio Control Room"), "/index.html": ("index.html", "Ember Studio Control Room"),
         "/metrics": ("metrics.html", "Ember & Clove Metrics"), "/store": ("store.html", "Ember & Clove Store")}
STATE = {"last_sync": None, "last_error": None}

SHELL = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>%TITLE%</title>
<style>
:root { --color-bg:#f7f5f2; --color-panel:#ffffff; --color-fg:#24201d; --color-fg-muted:#6f665f; --color-border-line:#e4ded7;
  --color-ok:#2f7d4f; --color-warn:#a86a12; --color-bad:#b3362c; --cds-chart-grid:#ece7e1; --cds-chart-axis:#c9c1b8;
  --cds-chart-reference:#8a7f75; --cds-chart-status-critical:#c0392b; --cds-surface-popover:#ffffff; --cds-border:#ddd5cc;
  --cds-shadow-popover:0 4px 16px rgba(36,32,29,.12); --cds-text-secondary:#6f665f; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root { --color-bg:#1b1917; --color-panel:#24211e; --color-fg:#eee8e2; --color-fg-muted:#a99f96;
  --color-border-line:#3a3531; --color-ok:#6cc08d; --color-warn:#e0a54a; --color-bad:#ef7a6f; --cds-chart-grid:#332f2b;
  --cds-chart-axis:#4a443f; --cds-chart-reference:#a99f96; --cds-chart-status-critical:#ef7a6f; --cds-surface-popover:#2c2825;
  --cds-border:#443e39; --cds-shadow-popover:0 4px 16px rgba(0,0,0,.4); --cds-text-secondary:#a99f96; color-scheme: dark; } }
:root { --font-anthropic-sans: system-ui, -apple-system, "Segoe UI", sans-serif; --font-anthropic-serif: Georgia, "Times New Roman", serif;
  --cds-font-size-caption:.8125rem; --cds-font-size-body:.9375rem; --cds-font-size-heading:1.0625rem; --cds-font-size-title:1.75rem;
  --cds-font-weight-medium:500; --cds-gap-xs:4px; --cds-gap-sm:8px; --cds-gap-md:12px; --cds-gap-lg:20px; --cds-gap-xl:32px;
  --cds-pad-xs:4px; --cds-pad-sm:8px; --cds-pad-md:12px; --cds-pad-lg:16px; --cds-radius:8px; --cds-dur-slow:.3s; }
html, body { margin:0; background:var(--color-bg); color:var(--color-fg); font-family:var(--font-anthropic-sans); }
#dash-root { max-width:1200px; margin-inline:auto; padding-block:24px 48px;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); }
.lan-bar { font-size:.75rem; color:var(--color-fg-muted); margin-bottom:12px; display:flex; gap:8px; flex-wrap:wrap; }
.lan-bar .bad { color:var(--color-bad); } .lan-bar .warn { color:var(--color-warn); } .lan-bar .ok { color:var(--color-ok); }
#lan-health { display:flex; gap:10px; flex-wrap:wrap; }
html.lan-stale .es-big { opacity:.55; }
.lan-nav { display:flex; gap:6px; margin-bottom:16px; }
.lan-nav a { font-size:.8125rem; padding:4px 12px; border:1px solid var(--color-border-line); border-radius:999px;
  color:var(--color-fg); text-decoration:none; background:var(--color-panel); }
.lan-nav a[aria-current="page"] { background:var(--color-fg); color:var(--color-bg); border-color:var(--color-fg); }
.dash-skeleton { color:transparent !important; background:var(--color-border-line); border-radius:4px; }
</style>
<script src="/static/d3.min.js"></script>
<script>
window.dash = (() => {
  const names = %NAMES%;
  const ds = {}, calcs = {}, order = [], cbs = [];
  names.forEach(n => ds[n] = {status: 'loading', data: [], columns: [], meta: []});
  const get = id => ds[id] || (calcs[id] && calcs[id].res) || {status: 'missing', data: [], columns: []};
  const run = () => {
    order.forEach(id => { const c = calcs[id];
      const st = c.inputs.map(i => get(i).status);
      try { c.res = {status: st.includes('error') ? 'error' : st.every(s => s === 'ok') ? 'ok' : 'loading',
                     data: st.every(s => s === 'ok') ? c.fn(...c.inputs.map(i => get(i).data)) : [], columns: []}; }
      catch (e) { c.res = {status: 'error', data: [], message: String(e)}; } });
    cbs.forEach(f => { try { f(); } catch (e) { console.error(e); } });
  };
  async function load() {
    try {
      const j = await (await fetch('data', {cache: 'no-store'})).json();
      names.forEach(n => ds[n] = j.datasets[n] ? {status: 'ok', data: j.datasets[n].rows, columns: j.datasets[n].columns, meta: []}
                                               : {status: 'error', data: [], columns: [], message: 'missing'});
      const bar = document.getElementById('lan-synced');
      const ageMin = j.last_sync ? (Date.now() - new Date(j.last_sync)) / 60000 : null;
      const stale = ageMin == null || ageMin > 2.5 * j.every_min;
      if (bar) { bar.textContent = j.last_sync ? 'Updated ' + new Date(j.last_sync).toLocaleString() + (stale ? ' (stale)' : '') : 'Not synced yet';
                 bar.className = stale ? 'warn' : ''; }
      document.documentElement.classList.toggle('lan-stale', stale);
      const err = document.getElementById('lan-error');
      if (err) { err.hidden = !j.last_error; err.textContent = j.last_error ? 'Last sync failed: ' + j.last_error : ''; }
      const hl = document.getElementById('lan-health');
      if (hl) hl.replaceChildren(...(j.health || []).map(h => {
        // A job is late when its last success is older than its expected interval allows (ads: 3 h task).
        const age = h.last_success ? (Date.now() - new Date(h.last_success)) / 60000 : null;
        const late = age == null || age > (h.job.startsWith('ads:') ? 7 * 60 : 2.5 * j.every_min);
        const s = document.createElement('span');
        s.className = h.ok === false ? 'bad' : late ? 'warn' : 'ok';
        s.textContent = `${h.ok === false ? '✕' : late ? '!' : '✓'} ${h.label}`;
        s.title = `${h.label}: last success ${h.last_success ? new Date(h.last_success).toLocaleString() : 'never'}`
          + (h.error ? ` · last error: ${h.error}` : '') + (h.rows != null ? ` · ${h.rows} rows` : '');
        return s;
      }));
    } catch (e) { names.forEach(n => ds[n] = {status: 'error', data: [], columns: [], message: String(e)}); }
    run();
  }
  window.addEventListener('DOMContentLoaded', () => { load(); setInterval(load, 60000); });
  let w = 0; window.addEventListener('resize', () => { if (Math.abs(innerWidth - w) > 20) { w = innerWidth; run(); } });
  return {
    data: get, colors: ['#c2652a', '#3f7cac', '#7a9a3c', '#8e5ea2', '#c94f6d', '#2e9c8f', '#b08a2e', '#6b6f78'],
    calc: (id, o) => { calcs[id] = {...o, res: {status: 'loading', data: []}}; order.push(id); },
    onData: f => { cbs.push(f); try { f(); } catch (e) { console.error(e); } },
    refresh: () => load(), loader() {}, params: () => ({}), setParams() {}, resetParams() {}, setLink() {},
  };
})();
</script></head><body><div id="dash-root">
<nav class="lan-nav" aria-label="Pages">%NAV%</nav>
<div class="lan-bar"><span id="lan-synced">Loading…</span><span>· syncs with PostZen every %EVERY% min ·</span>
<span id="lan-health" aria-label="Sync health"></span><span id="lan-error" class="bad" hidden></span></div>
%PAGE%
</div></body></html>"""


def _rows(name):
    jp, cp = OUT / f"{name}.json", OUT / f"{name}.csv"
    if jp.exists():
        rows = json.loads(jp.read_text(encoding="utf-8"))
        if isinstance(rows, dict):  # single-record files (e.g. store_reconciliation) become one row
            rows = [rows]
        return {"rows": rows, "columns": list(rows[0]) if rows else []}
    if cp.exists():
        with open(cp, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            return {"rows": list(r), "columns": r.fieldnames or []}
    return None


def page(path, every):
    file, title = PAGES[path]
    nav = "".join(f'<a href="{href}"{' aria-current="page"' if PAGES[href][0] == file else ''}>{label}</a>'
                  for href, label in (("/", "Control room"), ("/metrics", "Metrics"), ("/store", "Store")))
    body = (OUT / file).read_text(encoding="utf-8")
    return (SHELL.replace("%NAMES%", json.dumps(DATASETS)).replace("%EVERY%", str(every)).replace("%TITLE%", title)
            .replace("%NAV%", nav).replace("%PAGE%", body))


def _tiktok():
    con = db.connect()
    try:
        return publishing.sync(con, bible.load())
    finally:
        con.close()


JOBS = [("tiktok", _tiktok), ("facebook", lambda: facebook_photos.sync_dashboard(OUT)),
        ("shopify", lambda: shopify_sync.sync(OUT)),
        ("snapshots", lambda: [f"{analytics.snapshot_dashboard_files(OUT)} rows"])]


def sync_once():
    """Run every job independently; return the list of failures (empty when all succeeded)."""
    failures = []
    for name, fn in JOBS:
        try:
            with analytics.job(name) as run:
                lines = fn() or []
                run["detail"] = "; ".join(lines)
                # each job returns summary lines like "fb_posts 3"; count the first number on each line
                run["rows"] = sum(int(m.group()) for line in lines if (m := re.search(r"\d+", str(line))))
        except Exception as e:  # recorded in sync_runs by analytics.job; keep serving the last good data
            failures.append(f"{JOB_LABELS.get(name, name)}: {type(e).__name__}: {str(e)[:160]}")
            LOG.exception("sync job %s failed", name)
    analytics.write_health_file(OUT)
    STATE.update(last_sync=time.strftime("%Y-%m-%dT%H:%M:%S%z"), last_error="; ".join(failures) or None)
    LOG.info("sync done%s", f" with failures: {failures}" if failures else "")
    return failures


def sync_loop(every_min):
    while True:
        try:
            sync_once()
        except Exception:  # never let the loop die
            LOG.exception("sync loop error")
        time.sleep(every_min * 60)


def health_rows():
    return [{**h, "label": JOB_LABELS.get(h["job"], h["job"])} for h in analytics.health()]


def make_handler(every):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in PAGES:
                return self._send(200, page(path, every), "text/html; charset=utf-8")
            if path == "/data":
                last = STATE["last_sync"]
                if not last and (OUT / "synced_at.txt").exists():
                    last = (OUT / "synced_at.txt").read_text(encoding="utf-8").strip()
                return self._send(200, json.dumps({"datasets": {n: _rows(n) for n in DATASETS}, "last_sync": last,
                                                   "last_error": STATE["last_error"], "every_min": every,
                                                   "health": health_rows()}), "application/json")
            if path == "/health":
                return self._send(200, json.dumps({**STATE, "jobs": health_rows()}), "application/json")
            if path.startswith("/static/"):
                f = (STATIC / path[len("/static/"):]).resolve()
                if STATIC.resolve() in f.parents and f.is_file():  # no path traversal outside static/
                    ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
                    return self._send_bytes(200, f.read_bytes(), ctype, cache=True)
            return self._send(404, "Not found", "text/plain")

        def _send_bytes(self, code, data, ctype, cache=False):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "max-age=86400" if cache else "no-store")
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            pass

    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("--every-min", type=int, default=15)
    ap.add_argument("--no-sync", action="store_true", help="serve the current files only (tests)")
    a = ap.parse_args()
    setup_logging()
    if not a.no_sync:
        threading.Thread(target=sync_loop, args=(a.every_min,), daemon=True).start()
    srv = ThreadingHTTPServer((a.host, a.port), make_handler(a.every_min))
    LOG.info("Ember Studio dashboard on http://%s:%s (sync every %s min%s)", a.host, a.port, a.every_min,
             ", sync off" if a.no_sync else "")
    srv.serve_forever()


def setup_logging():
    logs = OUT.parents[1] / "logs"
    logs.mkdir(exist_ok=True)
    h = logging.handlers.RotatingFileHandler(logs / "dashboard.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOG.addHandler(h)
    LOG.addHandler(logging.StreamHandler())
    LOG.setLevel(logging.INFO)


if __name__ == "__main__":
    main()
