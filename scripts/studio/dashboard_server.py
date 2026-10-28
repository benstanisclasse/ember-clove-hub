"""Ember Studio dashboard on the local network: http://<this machine>:8790 (control room) and /metrics

Serves studio/dashboard/index.html (the same page as the online dashboard) and metrics.html with a small stand-in for
the online dashboard's `dash` data API, reading the files `cli.py sync` and `facebook_photos.py sync` write. Every 15
minutes it runs both syncs itself (PostZen status, TikTok and Facebook metrics, followers; calendar and spend from
studio.db; Facebook plans from data/facebook), so the pages stay current.

Read-only: GET only, no write endpoints, no keys or prompts served. Run:
  python scripts/studio/dashboard_server.py [--port 8790] [--every-min 15]
POSTZEN_API_KEY must be in the environment for the sync (scripts/studio/run_dashboard.ps1 sets it).
"""
import argparse
import csv
import json
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import facebook_photos  # noqa: E402
from studio import bible, db, publishing  # noqa: E402

OUT = publishing.OUT
DATASETS = ["schedule", "followers", "tiktok_videos", "post_timeline", "daily_metrics", "spend", "caps",
            "fb_schedule", "fb_posts", "fb_daily", "fb_followers", "ads_daily", "ads_accounts"]
PAGES = {"/": ("index.html", "Ember Studio Control Room"), "/index.html": ("index.html", "Ember Studio Control Room"),
         "/metrics": ("metrics.html", "Ember & Clove Metrics")}
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
.lan-bar .bad { color:var(--color-bad); }
.lan-nav { display:flex; gap:6px; margin-bottom:16px; }
.lan-nav a { font-size:.8125rem; padding:4px 12px; border:1px solid var(--color-border-line); border-radius:999px;
  color:var(--color-fg); text-decoration:none; background:var(--color-panel); }
.lan-nav a[aria-current="page"] { background:var(--color-fg); color:var(--color-bg); border-color:var(--color-fg); }
.dash-skeleton { color:transparent !important; background:var(--color-border-line); border-radius:4px; }
</style>
<script src="https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js"></script>
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
      if (bar) bar.textContent = j.last_sync ? 'Updated ' + new Date(j.last_sync).toLocaleString() : 'Not synced yet';
      const err = document.getElementById('lan-error');
      if (err) { err.hidden = !j.last_error; err.textContent = j.last_error ? 'Last sync failed: ' + j.last_error : ''; }
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
<div class="lan-bar"><span id="lan-synced">Loading…</span><span>· syncs with PostZen every %EVERY% min</span>
<span id="lan-error" class="bad" hidden></span></div>
%PAGE%
</div></body></html>"""


def _rows(name):
    jp, cp = OUT / f"{name}.json", OUT / f"{name}.csv"
    if jp.exists():
        rows = json.loads(jp.read_text(encoding="utf-8"))
        return {"rows": rows, "columns": list(rows[0]) if rows else []}
    if cp.exists():
        with open(cp, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            return {"rows": list(r), "columns": r.fieldnames or []}
    return None


def page(path, every):
    file, title = PAGES[path]
    nav = "".join(f'<a href="{href}"{' aria-current="page"' if PAGES[href][0] == file else ''}>{label}</a>'
                  for href, label in (("/", "Control room"), ("/metrics", "Metrics")))
    body = (OUT / file).read_text(encoding="utf-8")
    return (SHELL.replace("%NAMES%", json.dumps(DATASETS)).replace("%EVERY%", str(every)).replace("%TITLE%", title)
            .replace("%NAV%", nav).replace("%PAGE%", body))


def sync_loop(every_min):
    while True:
        try:
            con = db.connect()
            publishing.sync(con, bible.load())
            con.close()
            facebook_photos.sync_dashboard(OUT)
            STATE.update(last_sync=time.strftime("%Y-%m-%dT%H:%M:%S%z"), last_error=None)
        except Exception as e:  # keep serving the last good data
            STATE["last_error"] = f"{type(e).__name__}: {str(e)[:200]}"
            traceback.print_exc()
        time.sleep(every_min * 60)


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
                                                   "last_error": STATE["last_error"]}), "application/json")
            if path == "/health":
                return self._send(200, json.dumps(STATE), "application/json")
            return self._send(404, "Not found", "text/plain")

        def log_message(self, fmt, *args):
            pass

    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("--every-min", type=int, default=15)
    a = ap.parse_args()
    threading.Thread(target=sync_loop, args=(a.every_min,), daemon=True).start()
    srv = ThreadingHTTPServer((a.host, a.port), make_handler(a.every_min))
    print(f"Ember Studio dashboard on http://{a.host}:{a.port} (sync every {a.every_min} min)", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
