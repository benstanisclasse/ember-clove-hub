"""Tests for the dashboard server, history/health store and ads snapshots (Dashboard 2.0, Phase B).

Run: python -m pytest -q scripts/studio/test_dashboard.py
Uses temporary databases and folders; the live studio.db, analytics.db and dashboard files are only read.
"""
import datetime as dt
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ads_snapshot  # noqa: E402
from studio import analytics, dashboard_server  # noqa: E402


# --- Eastern reporting days -------------------------------------------------------------------------------------

def test_local_day_around_fall_back():
    # DST ends 2026-11-01 at 02:00 EDT -> 01:00 EST
    assert analytics.local_day("2026-11-01T03:59:00Z") == "2026-10-31"  # 23:59 EDT
    assert analytics.local_day("2026-11-01T04:30:00Z") == "2026-11-01"  # 00:30 EDT
    assert analytics.local_day("2026-11-02T04:30:00Z") == "2026-11-01"  # 23:30 EST


def test_day_bounds_have_dst_lengths():
    start, end = analytics.day_bounds_utc("2026-11-01")
    assert (end - start) == dt.timedelta(hours=25)
    start, end = analytics.day_bounds_utc("2026-03-08")
    assert (end - start) == dt.timedelta(hours=23)
    start, _ = analytics.day_bounds_utc("2026-10-28")
    assert start.isoformat() == "2026-10-28T04:00:00+00:00"


def test_local_day_rejects_naive_datetimes():
    with pytest.raises(ValueError):
        analytics.local_day(dt.datetime(2026, 10, 28, 12, 0))


# --- sync health and history ------------------------------------------------------------------------------------

def test_job_records_success_and_failure(tmp_path):
    db = tmp_path / "a.db"
    with analytics.job("tiktok", db) as run:
        run["rows"] = 5
    with pytest.raises(RuntimeError):
        with analytics.job("facebook", db):
            raise RuntimeError("PostZen 401")
    h = {r["job"]: r for r in analytics.health(db)}
    assert h["tiktok"]["ok"] is True and h["tiktok"]["rows"] == 5 and h["tiktok"]["last_success"]
    assert h["facebook"]["ok"] is False and "PostZen 401" in h["facebook"]["error"]
    assert h["facebook"]["last_success"] is None


def test_post_snapshots_are_append_only(tmp_path):
    db = tmp_path / "a.db"
    row = {"post_id": "p1", "published": "2026-10-27", "url": "u", "views": "39"}
    analytics.record_post_snapshots("tiktok", [row], "2026-10-27T13:00:00Z", db)
    analytics.record_post_snapshots("tiktok", [{**row, "views": "42"}], "2026-10-28T13:00:00Z", db)
    analytics.record_post_snapshots("tiktok", [{"post_id": "", "views": "1"}], None, db)  # no id: skipped
    con = analytics.connect(db)
    assert [r[0] for r in con.execute("SELECT views FROM post_snapshots ORDER BY fetched_at")] == [39.0, 42.0]


def test_followers_keep_latest_reading_per_eastern_day(tmp_path):
    db = tmp_path / "a.db"
    analytics.record_followers("tiktok", 3, "2026-10-28T14:00:00Z", db)
    analytics.record_followers("tiktok", 5, "2026-10-28T20:00:00Z", db)
    analytics.record_followers("tiktok", None, None, db)  # unknown is not stored as 0
    con = analytics.connect(db)
    assert [tuple(r) for r in con.execute("SELECT day, followers FROM account_daily")] == [("2026-10-28", 5.0)]


def test_ad_daily_latest_keeps_newest_fetch(tmp_path):
    db = tmp_path / "a.db"
    analytics.record_ad_days("meta", [{"date": "2026-10-28", "spend": 10, "purchases": 1}], "account", "1",
                             "2026-10-28T12:00:00Z", db)
    analytics.record_ad_days("meta", [{"date": "2026-10-28", "spend": 12, "purchases": 2}], "account", "1",
                             "2026-10-29T12:00:00Z", db)  # platform revised the day
    con = analytics.connect(db)
    assert con.execute("SELECT COUNT(*) FROM ad_daily").fetchone()[0] == 2
    assert [tuple(r) for r in con.execute("SELECT spend, purchases FROM ad_daily_latest")] == [(12.0, 2.0)]


# --- ads snapshots -------------------------------------------------------------------------------------------------

def test_ads_merge_replaces_only_that_platform_and_days(tmp_path, monkeypatch):
    monkeypatch.setattr(ads_snapshot, "OUT", tmp_path)
    monkeypatch.setattr(ads_snapshot, "DAILY", tmp_path / "ads_daily.csv")
    monkeypatch.setattr(ads_snapshot, "ACCOUNTS", tmp_path / "ads_accounts.json")
    day = lambda d, s: {"date": d, "spend": s, "impressions": 0, "clicks": 0, "purchases": 0, "revenue": 0}
    ads_snapshot.merge({"platform": "meta", "account": "A", "days": [day("2026-10-27", 1), day("2026-10-28", 2)]})
    ads_snapshot.merge({"platform": "tiktok", "account": "T", "days": [day("2026-10-28", 5)]})
    ads_snapshot.merge({"platform": "meta", "account": "A", "active_campaigns": 1, "days": [day("2026-10-28", 3)]})
    rows = (tmp_path / "ads_daily.csv").read_text(encoding="utf-8").splitlines()[1:]
    assert sorted(rows) == ["2026-10-27,meta,1.0,0.0,0.0,0.0,0.0", "2026-10-28,meta,3.0,0.0,0.0,0.0,0.0",
                            "2026-10-28,tiktok,5.0,0.0,0.0,0.0,0.0"]
    accts = json.loads((tmp_path / "ads_accounts.json").read_text(encoding="utf-8"))
    assert [a["platform"] for a in accts] == ["meta", "tiktok"] and accts[0]["active_campaigns"] == 1
    with pytest.raises(SystemExit):
        ads_snapshot.merge({"platform": "snapchat", "days": []})
    with pytest.raises(ValueError):
        ads_snapshot.merge({"platform": "meta", "days": [day("10/28/2026", 1)]})


# --- server ----------------------------------------------------------------------------------------------------------

@pytest.fixture()
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(analytics, "DB", tmp_path / "a.db")
    with analytics.job("tiktok") as run:
        run["rows"] = 1
    srv = dashboard_server.ThreadingHTTPServer(("127.0.0.1", 0), dashboard_server.make_handler(15))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status, r.headers.get("Content-Type"), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type"), e.read()


def test_pages_render_with_local_d3(server):
    for path in ("/", "/index.html", "/metrics"):
        code, ctype, body = get(server + path)
        assert code == 200 and ctype.startswith("text/html")
        assert b'src="/static/d3.min.js"' in body and b"cdn.jsdelivr" not in body
    code, ctype, body = get(server + "/static/d3.min.js")
    assert code == 200 and "javascript" in ctype and body.startswith(b"// https://d3js.org v7.8.5")


def test_data_endpoint_shape(server):
    code, _, body = get(server + "/data")
    j = json.loads(body)
    assert code == 200 and set(j["datasets"]) == set(dashboard_server.DATASETS)
    assert j["every_min"] == 15
    assert j["health"][0]["job"] == "tiktok" and j["health"][0]["label"] == "TikTok"
    for v in j["datasets"].values():  # each dataset is either missing (None) or rows + columns
        assert v is None or {"rows", "columns"} <= set(v)


def test_static_cannot_escape_its_folder(server):
    for path in ("/static/../../../config/hub.json", "/static/..%2F..%2F..%2Fconfig%2Fhub.json", "/static/", "/nope"):
        assert get(server + path)[0] == 404
