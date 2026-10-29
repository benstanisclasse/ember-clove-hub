"""History and sync health for the dashboard: studio/analytics.db (Dashboard 2.0, Phase B).

studio.db stays the production conveyor; this separate database only stores what the platforms reported and when,
so it can be rebuilt from the platforms and a bad change here never touches the conveyor.

  sync_runs       one row per sync job run: started/finished, ok, rows written, error (powers sync health)
  post_snapshots  each post's lifetime counters at every sync (append-only), for 24/48/72 h and 7-day values
  account_daily   followers per account per day (latest reading of that day kept)
  ad_daily        each ad platform's daily numbers at every fetch (append-only; platforms revise conversions);
                  the view ad_daily_latest keeps the newest fetch per platform/level/entity/day
  ad_metrics_daily  every metric each platform reports per ad per day, at every fetch (append-only): `metrics` is
                  the platform's own fields as JSON, `funnel` the same day mapped to AD_FUNNEL (one shape for
                  Meta and TikTok); the view ad_metrics_latest keeps the newest fetch per platform/ad/day. Days are
                  each ad account's own reporting day.
  ad_breakdown_daily  the same per day split by one audience dimension (age, gender, country_code, placement) at
                  campaign level, at every fetch (append-only; view ad_breakdown_latest). `metrics` is the platform's
                  own fields as JSON (TikTok splits omit add to cart, checkout and completed payment).

Times are stored in UTC (ISO 8601, 'Z'). Reporting days are Eastern (America/New_York): use local_day().
"""
import contextlib
import csv
import datetime as dt
import json
import os
import sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo

HUB = Path(__file__).resolve().parents[2]
DB = HUB / "studio" / "analytics.db"
DASH = HUB / "studio" / "dashboard"
REPORT_TZ = ZoneInfo("America/New_York")
POST_METRICS = ("views", "impressions", "reach", "likes", "comments", "shares", "saves", "clicks")
AD_METRICS = ("spend", "impressions", "clicks", "purchases", "revenue")
AD_FUNNEL = ("spend", "impressions", "reach", "clicks", "landing_page_views", "add_to_cart", "checkout", "purchases",
             "revenue", "video_plays", "video_completes", "engaged_views", "likes", "comments", "follows")

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
CREATE TABLE IF NOT EXISTS ad_entities (
  platform TEXT NOT NULL, level TEXT NOT NULL, entity_id TEXT NOT NULL, fetched_at TEXT NOT NULL, parent_id TEXT,
  name TEXT, status TEXT, delivery TEXT, period TEXT, spend REAL, impressions REAL, clicks REAL, purchases REAL,
  revenue REAL, PRIMARY KEY (platform, level, entity_id, fetched_at));
CREATE VIEW IF NOT EXISTS ad_daily_latest AS
  SELECT a.* FROM ad_daily a JOIN (SELECT platform, level, entity_id, day, MAX(fetched_at) AS f FROM ad_daily
    GROUP BY platform, level, entity_id, day) m
  ON a.platform = m.platform AND a.level = m.level AND a.entity_id = m.entity_id AND a.day = m.day AND a.fetched_at = m.f;
CREATE TABLE IF NOT EXISTS ad_metrics_daily (
  platform TEXT NOT NULL, ad_id TEXT NOT NULL, day TEXT NOT NULL, fetched_at TEXT NOT NULL, campaign_id TEXT,
  group_id TEXT, ad_name TEXT, metrics TEXT, funnel TEXT, PRIMARY KEY (platform, ad_id, day, fetched_at));
CREATE VIEW IF NOT EXISTS ad_metrics_latest AS
  SELECT a.* FROM ad_metrics_daily a JOIN (SELECT platform, ad_id, day, MAX(fetched_at) AS f FROM ad_metrics_daily
    GROUP BY platform, ad_id, day) m
  ON a.platform = m.platform AND a.ad_id = m.ad_id AND a.day = m.day AND a.fetched_at = m.f;
CREATE TABLE IF NOT EXISTS ad_breakdown_daily (
  platform TEXT NOT NULL, level TEXT NOT NULL, entity_id TEXT NOT NULL, day TEXT NOT NULL, dimension TEXT NOT NULL,
  value TEXT NOT NULL, fetched_at TEXT NOT NULL, metrics TEXT,
  PRIMARY KEY (platform, level, entity_id, day, dimension, value, fetched_at));
CREATE VIEW IF NOT EXISTS ad_breakdown_latest AS
  SELECT a.* FROM ad_breakdown_daily a JOIN (SELECT platform, level, entity_id, day, dimension, MAX(fetched_at) AS f
    FROM ad_breakdown_daily GROUP BY platform, level, entity_id, day, dimension) m
  ON a.platform = m.platform AND a.level = m.level AND a.entity_id = m.entity_id AND a.day = m.day
    AND a.dimension = m.dimension AND a.fetched_at = m.f;
"""


@contextlib.contextmanager
def atomic_open(path, newline=None):
    """Write a file so readers only ever see the old or the new version, never half of one (temp file + replace)."""
    path = Path(path)
    tmp = path.with_name(f".{path.name}.tmp")
    with open(tmp, "w", encoding="utf-8", newline=newline) as f:
        yield f
    os.replace(tmp, path)


def write_text_atomic(path, text):
    with atomic_open(path) as f:
        f.write(text)


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


def record_ad_entities(platform, entities, period, fetched_at=None, path=None):
    """Campaign / ad set / ad group / asset group / ad totals as each platform reported them at this fetch."""
    fetched_at = fetched_at or now_utc()
    con = connect(path)
    for e in entities:
        con.execute("INSERT OR IGNORE INTO ad_entities VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (platform, e["level"], str(e["id"]), fetched_at, str(e.get("parent_id") or ""), e.get("name") or "",
                     e.get("status") or "", e.get("delivery") or "", period,
                     *[_num(e.get(k)) or 0.0 for k in AD_METRICS]))
    con.commit()
    con.close()
    return len(entities)


def record_ad_metrics(platform, rows, fetched_at=None, path=None):
    """rows: dicts with date, id, name, campaign_id, group_id, metrics (the platform's fields) and funnel (AD_FUNNEL),
    as built by ads_snapshot.py. Append-only."""
    fetched_at = fetched_at or now_utc()
    con = connect(path)
    for r in rows:
        con.execute("INSERT OR IGNORE INTO ad_metrics_daily VALUES (?,?,?,?,?,?,?,?,?)",
                    (platform, str(r["id"]), r["date"], fetched_at, str(r.get("campaign_id") or ""),
                     str(r.get("group_id") or ""), r.get("name") or "", json.dumps(r.get("metrics") or {}, sort_keys=True),
                     json.dumps({k: (r.get("funnel") or {}).get(k) for k in AD_FUNNEL})))
    con.commit()
    con.close()
    return len(rows)


def record_ad_breakdowns(platform, rows, fetched_at=None, path=None):
    """rows: dicts with level, id, date, dimension, value, metrics (as built by ads_snapshot.py). Append-only. The
    newest fetch of a day and dimension replaces the whole split (a value that drops out is gone from the view)."""
    fetched_at = fetched_at or now_utc()
    con = connect(path)
    for r in rows:
        con.execute("INSERT OR IGNORE INTO ad_breakdown_daily VALUES (?,?,?,?,?,?,?,?)",
                    (platform, r["level"], str(r["id"]), r["date"], r["dimension"], str(r["value"]), fetched_at,
                     json.dumps(r.get("metrics") or {}, sort_keys=True)))
    con.commit()
    con.close()
    return len(rows)


def ad_funnel_rows(path=None):
    """Newest fetch of every ad-day, flattened for the dashboard: platform, date, ad, parents and AD_FUNNEL."""
    con = connect(path)
    out = [{"platform": r["platform"], "date": r["day"], "ad_id": r["ad_id"], "ad_name": r["ad_name"],
            "campaign_id": r["campaign_id"], "group_id": r["group_id"], **json.loads(r["funnel"] or "{}")}
           for r in con.execute("SELECT * FROM ad_metrics_latest ORDER BY day, platform, ad_id")]
    con.close()
    return out


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
    write_text_atomic((out / "sync_health.json"), json.dumps(health(path), indent=1))
