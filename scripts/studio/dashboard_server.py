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
from studio import analytics, bible, content, db, publishing, shopify_sync  # noqa: E402

OUT = publishing.OUT
STATIC = OUT / "static"
LOG = logging.getLogger("dashboard")
DATASETS = ["schedule", "followers", "tiktok_videos", "post_timeline", "daily_metrics", "spend", "caps",
            "fb_schedule", "fb_posts", "fb_daily", "fb_followers", "ads_daily", "ads_accounts", "sync_health",
            "store_daily", "store_sources", "store_utm", "store_products", "store_reconciliation", "system_info",
            "episode_history", "ads_entities", "store_attribution", "content_queue", "content_events",
            "profit_daily", "profit_products", "profit_summary", "cost_ledger", "content_jobs", "content_quality"]
JOB_LABELS = {"tiktok": "TikTok", "facebook": "Facebook", "shopify": "Shopify", "snapshots": "History", "content": "Content queue", "ads:meta": "Meta ads",
              "ads:tiktok": "TikTok ads", "ads:microsoft": "Microsoft ads"}
# path -> (file, title, nav key). Six sections (Phase D); old addresses redirect.
PAGES = {"/": ("overview.html", "Overview · Ember & Clove", "overview"),
         "/content": ("index.html", "Content Studio · Ember & Clove", "content"),
         "/content/performance": ("metrics.html", "Content performance · Ember & Clove", "performance"),
         "/ads": ("ads.html", "Advertising · Ember & Clove", "ads"),
         "/store": ("store.html", "Store · Ember & Clove", "store"),
         "/intelligence": ("intelligence.html", "Intelligence · Ember & Clove", "intelligence"),
         "/ops": ("ops.html", "Operations · Ember & Clove", "ops")}
REDIRECTS = {"/index.html": "/content", "/metrics": "/content/performance"}
ICON = {  # 16px line icons (Lucide-style paths, drawn inline)
    "overview": '<path d="M3 13h8V3H3zM13 21h8V11h-8zM3 21h8v-6H3zM13 3v6h8V3z"/>',
    "content": '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "performance": '<path d="M4 19V9M10 19V5M16 19v-7M22 19H2"/>',
    "ads": '<path d="M3 11l18-8v18L3 13z"/><path d="M7 13v5a2 2 0 0 0 4 0v-3"/>',
    "store": '<path d="M3 9l1.5-5h15L21 9M3 9h18v11H3zM9 20v-6h6v6"/>',
    "intelligence": '<path d="M12 3a6 6 0 0 0-3.5 10.9V17h7v-3.1A6 6 0 0 0 12 3zM9.5 21h5"/>',
    "ops": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'}
NAV = [("/", "overview", "Overview", False), ("/content", "content", "Content Studio", False),
       ("/content/performance", "performance", "Performance", True), ("/ads", "ads", "Advertising", False),
       ("/store", "store", "Store", False), ("/intelligence", "intelligence", "Intelligence", False),
       ("/ops", "ops", "Operations", False)]
STATE = {"last_sync": None, "last_error": None}

SHELL = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>%TITLE%</title>
<link rel="stylesheet" href="/static/app.css">
<script>try { if (localStorage.getItem('ec-theme') === 'light') document.documentElement.dataset.theme = 'light'; } catch (e) {}</script>
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
      const j = await (await fetch('/data', {cache: 'no-store'})).json();
      window.dashHealth = j.health || [];
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
</script>
<script src="/static/components.js"></script></head><body><div class="app">
<aside class="side"><a class="brand" href="/"><span class="brand-mark">E&amp;C</span><span><div class="brand-name">Ember &amp; Clove</div>
<div class="brand-sub">Ember Studio</div></span></a>
<nav class="side-nav" aria-label="Sections">%NAV%</nav>
<div class="side-foot"><button class="theme-btn" type="button" id="theme-btn">Switch theme</button>
<span>Read-only dashboard · home network</span></div></aside>
<main id="dash-root">
<div class="lan-bar"><span id="lan-synced">Loading…</span><span>· syncs with PostZen every %EVERY% min ·</span>
<span id="lan-health" aria-label="Sync health"></span><span id="lan-error" class="bad" hidden></span></div>
%PAGE%
</main></div>
<script>document.getElementById('theme-btn').addEventListener('click', () => {
  const light = document.documentElement.dataset.theme !== 'light';
  if (light) document.documentElement.dataset.theme = 'light'; else delete document.documentElement.dataset.theme;
  try { localStorage.setItem('ec-theme', light ? 'light' : 'dark'); } catch (e) {}
  if (window.dash) dash.refresh();
});</script></body></html>"""


_LAST_GOOD = {}


def _rows(name):
    """One dataset for /data. If a file can't be read or parsed (a writer that doesn't write atomically, a disk hiccup),
    serve the last good copy instead of failing the whole page."""
    jp, cp = OUT / f"{name}.json", OUT / f"{name}.csv"
    try:
        if jp.exists():
            rows = json.loads(jp.read_text(encoding="utf-8"))
            if isinstance(rows, dict):  # single-record files (e.g. store_reconciliation) become one row
                rows = [rows]
            out = {"rows": rows, "columns": list(rows[0]) if rows else []}
        elif cp.exists():
            with open(cp, newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                out = {"rows": list(r), "columns": r.fieldnames or []}
        else:
            return None
    except (OSError, ValueError, csv.Error) as e:
        LOG.warning("dataset %s unreadable (%s); serving the last good copy", name, e)
        return _LAST_GOOD.get(name)
    _LAST_GOOD[name] = out
    return out


def page(path, every):
    file, title, key = PAGES[path]
    nav = "".join(f'<a href="{href}" class="{"sub" if sub else ""}"{' aria-current="page"' if k == key else ''}>'
                  f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICON[k]}</svg>{label}</a>'
                  for href, k, label, sub in NAV)
    body = (OUT / file).read_text(encoding="utf-8")
    shell = SHELL
    for asset in ("app.css", "components.js"):  # version tag so browsers never run a stale copy after an update
        shell = shell.replace(f"/static/{asset}", f"/static/{asset}?v={int((STATIC / asset).stat().st_mtime)}")
    return (shell.replace("%NAMES%", json.dumps(DATASETS)).replace("%EVERY%", str(every)).replace("%TITLE%", title)
            .replace("%NAV%", nav).replace("%PAGE%", body))


def _tiktok():
    con = db.connect()
    try:
        lines = publishing.sync(con, bible.load())
        # production history for the calendar's detail panel (real episodes only)
        hist = [dict(r) for r in con.execute(
            "SELECT t.episode_id, t.from_state, t.to_state, t.actor, t.reason, t.at FROM transitions t "
            "JOIN episodes e ON e.id = t.episode_id WHERE e.test = 0 ORDER BY t.episode_id, t.at")]
        analytics.write_text_atomic((OUT / "episode_history.json"), json.dumps(hist, ensure_ascii=False))
        return lines + [f"episode_history {len(hist)}"]
    finally:
        con.close()


def write_system_info():
    """Backups and other facts for the Operations page (no secrets)."""
    root = OUT.parents[1] / "backups"
    snaps = sorted(p.name for p in root.iterdir() if p.is_dir() and len(p.name) == 10 and p.name[4] == "-") if root.exists() else []
    mirror = root / "media_mirror"
    info = {"latest_backup": snaps[-1] if snaps else None, "backup_count": len(snaps), "backup_dir": str(root),
            "mirror_files": sum(1 for f in mirror.rglob("*") if f.is_file()) if mirror.exists() else 0}
    analytics.write_text_atomic((OUT / "system_info.json"), json.dumps(info))


def episode_frames(episode_id):
    """Path of a real (non-test) episode's frame sheet, looked up by id in studio.db; None for anything else."""
    if not re.fullmatch(r"[A-Z]{2}-\d{8}-\d+", episode_id or ""):
        return None
    con = db.connect()
    try:
        row = con.execute("SELECT video_path FROM episodes WHERE id = ? AND test = 0", (episode_id,)).fetchone()
    finally:
        con.close()
    if not row or not row["video_path"]:
        return None
    video = OUT.parents[1] / row["video_path"].replace("\\", "/")
    f = video.with_name(video.stem + "_frames.jpg")
    return f if f.is_file() else None


JOBS = [("tiktok", _tiktok), ("facebook", lambda: facebook_photos.sync_dashboard(OUT)),
        ("shopify", lambda: shopify_sync.sync(OUT)),
        ("snapshots", lambda: [f"{analytics.snapshot_dashboard_files(OUT)} rows"]),
        ("content", lambda: content.sync(OUT))]  # Content Studio: one queue for TikTok + Facebook (after their syncs)


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
    write_system_info()
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
        server_version, sys_version = "EmberStudio", ""  # don't advertise the Python version

        def end_headers(self):  # Phase H: basic browser hardening on every response
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            self.send_header("Referrer-Policy", "no-referrer")
            super().end_headers()

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
            if path in REDIRECTS:
                self.send_response(301)
                self.send_header("Location", REDIRECTS[path])
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
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
                    # only the third-party library is cached; our own CSS/JS change with every release
                    return self._send_bytes(200, f.read_bytes(), ctype, cache=f.name == "d3.min.js")
            if path.startswith("/media/frames/"):  # a real episode's QA frame sheet, used as its thumbnail
                frames = episode_frames(path[len("/media/frames/"):])
                if frames:
                    return self._send_bytes(200, frames.read_bytes(), "image/jpeg")
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
