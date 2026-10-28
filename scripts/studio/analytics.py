"""History and sync health for the dashboard: studio/analytics.db (Dashboard 2.0, Phase B).

studio.db stays the production conveyor; this separate database only stores what the platforms reported and when,
so it can be rebuilt from the platforms and a bad change here never touches the conveyor.

  sync_runs       one row per sync job run: started/finished, ok, rows written, error (powers sync health)
  post_snapshots  each post's lifetime counters at every sync (append-only), for 24/48/72 h and 7-day values
  account_daily   followers per account per day (latest reading of that day kept)
  ad_daily        each ad platform's daily numbers at every fetch (append-only; platforms revise conversions);
                  the view ad_daily_latest keeps the newest fetch per platform/level/entity/day

Times are stored in UTC (ISO 8601, 'Z'). Reporting days are Eastern (America/New_York): use local_day().
"""
import contextlib
import csv
import datetime as dt
import json
import sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo

HUB = Path(__file__).resolve().parents[2]
DB = HUB / "studio" / "analytics.db"
DASH = HUB / "studio" / "dashboard"
REPORT_TZ = ZoneInfo("America/New_York")
POST_METRICS = ("views", "impressions", "reach", "likes", "comments", "shares", "saves", "clicks")
AD_METRICS = ("spend", "impressions", "clicks", "purchases", "revenue")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sync_runs (
  id INTEGER PRIMARY KEY, job TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, ok INTEGER,
  rows_written INTEGER DEFAULT 0, error TEXT, detail TEXT);
CREATE INDEX IF NOT EXISTS sync_runs_job ON sync_runs (job, started_at);
CREATE TABLE IF NOT EXISTS post_snapshots (
  platform TEXT NOT NULL, post_id TEXT NOT NULL, fetched_at TEXT NOT NULL, published TEXT, url TEXT, episode TEXT,
  views REAL, impressions REAL, reach REAL, likes REAL, comments REAL, shares REAL, saves REAL, clicks REAL,
  PRIMARY KEY (platform, post_id, fetched_at));
CREATE TABLE IF NOT EXISTS account_daily (
  platform TEXT NOT NULL, day TEXT NOT NULL, followers REAL, fetched_at TEXT NOT NULL,
  PRIMARY KEY (platform, day));
CREATE TABLE IF NOT EXISTS ad_daily (
  platform TEXT NOT NULL, level TEXT NOT NULL, entity_id TEXT NOT NULL, day TEXT NOT NULL, fetched_at TEXT NOT NULL,
  spend REAL, impressions REAL, clicks REAL, purchases REAL, revenue REAL,
  PRIMARY KEY (platform, level, entity_id, day, fetched_at));
CREATE VIEW IF NOT EXISTS ad_daily_latest AS
  SELECT a.* FROM ad_daily a JOIN (SELECT platform, level, entity_id, day, MAX(fetched_at) AS f FROM ad_daily
    GROUP BY platform, level, entity_id, day) m
  ON a.platform = m.platform AND a.level = m.level AND a.entity_id = m.entity_id AND a.day = m.day AND a.fetched_at = m.f;
"""


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def local_day(ts):
    """Eastern reporting day ('YYYY-MM-DD') of a UTC timestamp string or aware datetime. DST-correct."""
    if isinstance(ts, str):
        ts = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        raise ValueError("naive datetime: pass UTC with tzinfo")
    return ts.astimezone(REPORT_TZ).date().isoformat()


def day_bounds_utc(day):
    """UTC start and end (exclusive) of an Eastern reporting day; a DST change day is 23 or 25 hours long."""
    d = dt.date.fromisoformat(day)
    start = dt.datetime.combine(d, dt.time(), REPORT_TZ)
    end = dt.datetime.combine(d + dt.timedelta(days=1), dt.time(), REPORT_TZ)
    return start.astimezone(dt.timezone.utc), end.astimezone(dt.timezone.utc)


def connect(path=None):
    con = sqlite3.connect(path or DB, timeout=30)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


@contextlib.contextmanager
def job(name, path=None):
    """Record one sync job run. Yields a dict; set ['rows'] and ['detail']. Exceptions are recorded, then re-raised."""
    con = connect(path)
    cur = con.execute("INSERT INTO sync_runs (job, started_at) VALUES (?, ?)", (name, now_utc()))
    con.commit()
    run = {"rows": 0, "detail": ""}
    try:
        yield run
        con.execute("UPDATE sync_runs SET finished_at = ?, ok = 1, rows_written = ?, detail = ? WHERE id = ?",
                    (now_utc(), run["rows"], str(run["detail"])[:500], cur.lastrowid))
    except Exception as e:
        con.execute("UPDATE sync_runs SET finished_at = ?, ok = 0, error = ? WHERE id = ?",
                    (now_utc(), f"{type(e).__name__}: {str(e)[:300]}", cur.lastrowid))
        raise
    finally:
        con.commit()
        con.close()


def health(path=None):
    """Per job: last attempt, last success, last error, rows and duration of the last run."""
    con = connect(path)
    out = []
    for (name,) in con.execute("SELECT DISTINCT job FROM sync_runs ORDER BY job"):
        last = con.execute("SELECT * FROM sync_runs WHERE job = ? ORDER BY id DESC LIMIT 1", (name,)).fetchone()
        ok = con.execute("SELECT finished_at FROM sync_runs WHERE job = ? AND ok = 1 ORDER BY id DESC LIMIT 1",
                         (name,)).fetchone()
        secs = None
        if last["finished_at"]:
            secs = (dt.datetime.fromisoformat(last["finished_at"].replace("Z", "+00:00"))
                    - dt.datetime.fromisoformat(last["started_at"].replace("Z", "+00:00"))).total_seconds()
        out.append({"job": name, "last_attempt": last["started_at"], "last_success": ok["finished_at"] if ok else None,
                    "ok": None if last["ok"] is None else bool(last["ok"]), "error": last["error"] or "",
                    "rows": last["rows_written"], "seconds": secs, "detail": last["detail"] or ""})
    con.close()
    return out


def _num(x):
    try:
        return None if x in (None, "") else float(x)
    except (TypeError, ValueError):
        return None


def record_post_snapshots(platform, rows, fetched_at=None, path=None):
    """rows: dicts with post_id, published, url, episode (optional) and POST_METRICS. Returns rows written."""
    fetched_at = fetched_at or now_utc()
    con = connect(path)
    n = 0
    for r in rows:
        if not r.get("post_id"):
            continue
        con.execute("INSERT OR IGNORE INTO post_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (platform, r["post_id"], fetched_at, r.get("published") or "", r.get("url") or "",
                     r.get("episode") or "", *[_num(r.get(k)) for k in POST_METRICS]))
        n += 1
    con.commit()
    con.close()
    return n


def record_followers(platform, followers, fetched_at=None, path=None):
    """Store today's (Eastern) follower count; a later reading the same day replaces the earlier one."""
    if followers is None:
        return 0
    fetched_at = fetched_at or now_utc()
    con = connect(path)
    con.execute("INSERT OR REPLACE INTO account_daily VALUES (?,?,?,?)",
                (platform, local_day(fetched_at), float(followers), fetched_at))
    con.commit()
    con.close()
    return 1


def record_ad_days(platform, days, level="account", entity_id="", fetched_at=None, path=None):
    """days: dicts with date + AD_METRICS (as saved by ads_snapshot.py). Append-only."""
    fetched_at = fetched_at or now_utc()
    con = connect(path)
    for d in days:
        con.execute("INSERT OR IGNORE INTO ad_daily VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (platform, level, str(entity_id), d["date"], fetched_at, *[_num(d.get(k)) or 0.0 for k in AD_METRICS]))
    con.commit()
    con.close()
    return len(days)


def snapshot_dashboard_files(out=DASH, path=None):
    """After the organic syncs: copy the freshly written post and follower numbers into history."""
    fetched_at = now_utc()
    n = 0
    for platform, posts_file, followers_file in (("tiktok", "tiktok_videos.csv", "followers.json"),
                                                 ("facebook", "fb_posts.csv", "fb_followers.json")):
        if (out / posts_file).exists():
            with open(out / posts_file, newline="", encoding="utf-8") as f:
                n += record_post_snapshots(platform, list(csv.DictReader(f)), fetched_at, path)
        if (out / followers_file).exists():
            rows = json.loads((out / followers_file).read_text(encoding="utf-8"))
            if rows:
                n += record_followers(platform, rows[-1].get("followers"), fetched_at, path)
    return n


def write_health_file(out=DASH, path=None):
    (out / "sync_health.json").write_text(json.dumps(health(path), indent=1), encoding="utf-8")
