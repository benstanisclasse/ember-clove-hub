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


def test_full_ad_metrics_map_both_platforms_to_one_funnel(tmp_path, monkeypatch):
    db = tmp_path / "a.db"
    monkeypatch.setattr(ads_snapshot, "OUT", tmp_path)
    monkeypatch.setattr(ads_snapshot, "FUNNEL", tmp_path / "ads_funnel.json")
    tiktok = [{"dimensions": {"ad_id": "XXX", "stat_time_day": "2026-10-28 00:00:00"},
               "metrics": {"ad_name": "P012_B", "campaign_id": "c1", "adgroup_id": "g1", "spend": "20.30", "clicks": "8",
                           "total_landing_page_view": "6", "onsite_on_web_cart": "0", "web_event_add_to_cart": "2",
                           "initiate_checkout": "1", "complete_payment": "0",
                           "video_views_p25": "229", "average_video_play": "3.26"}}]
    meta = [{"date_start": "2026-10-28", "date_stop": "2026-10-28", "id": "1209", "name": "Turtleneck",
             "campaign_id": "c2", "adset_id": "s2", "amount_spent": {"value": "4.31", "unit": "USD"}, "clicks": "42",
             "link_click": "4", "ctr": "19.63%", "like": "48", "landing_page_view": None,
             "results": {"indicator": "actions:like", "values": [{"value": "48"}]}}]
    tt, mt = ads_snapshot.ad_days("tiktok", tiktok), ads_snapshot.ad_days("meta", meta)
    assert tt[0]["funnel"]["clicks"] == 8 and tt[0]["funnel"]["landing_page_views"] == 6 and tt[0]["group_id"] == "g1"
    # website pixel events, not TikTok Shop's in-app onsite_on_web_cart / checkout
    assert tt[0]["funnel"]["add_to_cart"] == 2 and tt[0]["funnel"]["checkout"] == 1
    assert tt[0]["metrics"]["video_views_p25"] == "229"  # every field kept, not only the funnel ones
    assert mt[0]["funnel"]["spend"] == 4.31 and mt[0]["funnel"]["clicks"] == 4  # link clicks, not clicks (all)
    assert mt[0]["funnel"]["follows"] == 48 and mt[0]["funnel"]["landing_page_views"] is None
    assert ads_snapshot.value("19.63%") == 19.63 and ads_snapshot.value({"value": "Not available"}) is None
    analytics.record_ad_metrics("tiktok", tt, "2026-10-29T09:00:00Z", db)
    analytics.record_ad_metrics("tiktok", [{**tt[0], "funnel": {**tt[0]["funnel"], "clicks": 9}}], "2026-10-29T12:00:00Z", db)
    analytics.record_ad_metrics("meta", mt, "2026-10-29T09:00:00Z", db)
    rows = analytics.ad_funnel_rows(db)
    assert [(r["platform"], r["clicks"]) for r in rows] == [("meta", 4), ("tiktok", 9)]  # newest fetch wins
    assert ads_snapshot.write_funnel(db) == 2 and json.loads((tmp_path / "ads_funnel.json").read_text())[1]["ad_name"] == "P012_B"
    with pytest.raises(ValueError):
        ads_snapshot.ad_days("meta", [{**meta[0], "date_start": ""}])


def test_audience_splits_keep_the_newest_split_per_day(tmp_path):
    db = tmp_path / "a.db"
    row = lambda v, spend: {"dimensions": {"campaign_id": "c1", "stat_time_day": "2026-10-28 00:00:00", "age": v},
                            "metrics": {"spend": spend, "purchase": "0"}}
    first = ads_snapshot.breakdowns({"age": [row("AGE_25_34", "60"), row("AGE_35_44", "40")]})
    assert first[0] == {"level": "campaign", "id": "c1", "date": "2026-10-28", "dimension": "age", "value": "AGE_25_34",
                        "metrics": {"spend": "60", "purchase": "0"}}
    analytics.record_ad_breakdowns("tiktok", first, "2026-10-29T01:00:00Z", db)
    analytics.record_ad_breakdowns("tiktok", ads_snapshot.breakdowns({"age": [row("AGE_25_34", "100")]}), "2026-10-29T04:00:00Z", db)
    con = analytics.connect(db)
    assert [tuple(r) for r in con.execute("SELECT value, metrics FROM ad_breakdown_latest")] == [
        ("AGE_25_34", json.dumps({"purchase": "0", "spend": "100"}))]
    with pytest.raises(SystemExit):
        ads_snapshot.breakdowns({"interests": [row("x", "1")]})
    with pytest.raises(ValueError):
        ads_snapshot.breakdowns({"age": [{"dimensions": {"campaign_id": "c1", "age": "AGE_25_34"}, "metrics": {}}]})


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
    for path in ("/", "/content", "/content/performance", "/ads", "/store", "/intelligence", "/ops"):
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


# --- Shopify (Phase C) ---------------------------------------------------------------------------------------------

from studio import shopify_sync  # noqa: E402
import profitability_model  # noqa: E402


def _days(sessions, carts=None):
    start = dt.date(2026, 10, 20)
    return [{"day": (start + dt.timedelta(days=i)).isoformat(), "sessions": s, "cart_sessions": (carts or {}).get(i, 0)}
            for i, s in enumerate(sessions)]


def test_bot_flag_catches_spike_only():
    days = shopify_sync.flag_bot_days(_days([0, 0, 0, 159, 1104, 65, 405, 412], {4: 5, 6: 1, 7: 3}))
    assert [d["day"] for d in days if d["bot_flag"]] == ["2026-10-24"]
    assert "3.9x the nearby median (282)" in days[4]["bot_reason"]  # neighbours 159, 65, 405, 412


def test_bot_flag_needs_neighbours_and_low_cart_rate():
    assert not any(d["bot_flag"] for d in shopify_sync.flag_bot_days(_days([0, 900, 0])))  # one day alone
    spike_with_carts = shopify_sync.flag_bot_days(_days([100, 100, 1000, 100], {2: 50}))  # 5% carts: real buyers
    assert not any(d["bot_flag"] for d in spike_with_carts)
    assert not any(d["bot_flag"] for d in shopify_sync.flag_bot_days(_days([20, 20, 90, 20])))  # under 100 visits


def test_product_economics_matches_profitability_model():
    v = [{"price": 55.99, "unit_cost": 17.77, "grams": 380}, {"price": 55.99, "unit_cost": 17.77, "grams": 380},
         {"price": 59.99, "unit_cost": 18.50, "grams": 400}]
    e = shopify_sync.product_economics("Test Dress", v, cpa=20.0)
    expect = profitability_model.contribution("Test Dress", 55.99, 18.50, 400)  # median_low price, costliest variant
    assert e["contribution"] == round(expect, 2) and e["kept_after_cpa"] == round(expect - 20, 2)
    assert e["breakeven_cpa"] == e["contribution"] and e["econ_status"] == "Estimate"
    assert shopify_sync.product_economics("X", [{"price": 10.0}])["econ_status"] == "No unit cost on record"
    assert shopify_sync.product_economics("X", [])["econ_status"] == "No price"


def test_reconcile_flags_mismatch():
    rows = [{"orders": 1, "net_sales": 40, "total_sales": 48, "sessions": 10}, {"orders": 0, "net_sales": 0,
                                                                                "total_sales": 0, "sessions": 5}]
    ok = shopify_sync.reconcile(rows, {"orders": 1, "net_sales": 40, "total_sales": 48}, 15, 1, 1)
    assert ok["ok"] is True
    bad = shopify_sync.reconcile(rows, {"orders": 2, "net_sales": 40, "total_sales": 48}, 15, 1, 2)
    assert bad["ok"] is False and [c["check"] for c in bad["checks"] if not c["ok"]] == [
        "Orders (sales report)", "Orders stored vs order count"]


def test_store_page_and_single_record_dataset(server):
    code, ctype, body = get(server + "/store")
    assert code == 200 and b"Product economics" in body and b'href="/store"' in body
    j = json.loads(get(server + "/data")[2])
    rec = j["datasets"]["store_reconciliation"]
    assert rec is None or (len(rec["rows"]) == 1 and "checks" in rec["rows"][0])


# --- Phase D: navigation and pages ---------------------------------------------------------------------------------

def test_old_addresses_redirect(server):
    import http.client
    host, port = server.replace("http://", "").split(":")
    for old, new in (("/index.html", "/content"), ("/metrics", "/content/performance")):
        c = http.client.HTTPConnection(host, int(port), timeout=10)
        c.request("GET", old)
        r = c.getresponse()
        assert r.status == 301 and r.getheader("Location") == new


def test_every_page_has_the_sidebar_and_shared_assets(server):
    for path, label in (("/", "Overview"), ("/content", "Content Studio"), ("/ads", "Advertising"), ("/store", "Store"),
                        ("/intelligence", "Intelligence"), ("/ops", "Operations"), ("/content/performance", "Performance")):
        body = get(server + path)[2].decode("utf-8")
        assert 'class="side-nav"' in body and "/static/app.css" in body and "/static/components.js" in body
        current = body.split('aria-current="page"')[1].split("</a>")[0]
        assert label in current, f"{path} should mark {label} as the current section"
    for f in ("app.css", "components.js"):
        assert get(server + "/static/" + f)[0] == 200


def test_data_includes_new_datasets(server):
    j = json.loads(get(server + "/data")[2])
    assert {"system_info", "episode_history", "store_daily"} <= set(j["datasets"])


# --- Phase E: attribution ------------------------------------------------------------------------------------------

import attribution  # noqa: E402


def test_tag_link_uses_the_convention_and_replaces_old_tags():
    url = attribution.tag_link("https://emberandclove.com/products/x?variant=1&utm_source=old", "facebook_organic", "fb_photos", "2026-10-28_0900")
    assert url == ("https://emberandclove.com/products/x?variant=1&utm_source=facebook&utm_medium=organic_social"
                   "&utm_campaign=fb_photos&utm_content=2026-10-28_0900")
    assert "utm_medium=paid_social" in attribution.tag_link("https://e.com", "tiktok_ads", "c1")


@pytest.mark.parametrize("args,expect", [
    (("facebook", "social"), ("facebook_organic", "Directly tracked")),         # posts before 10/28
    (("facebook", "organic_social"), ("facebook_organic", "Directly tracked")),
    (("fb", "paid_social"), ("meta_ads", "Directly tracked")),
    (("instagram", "cpc"), ("meta_ads", "Directly tracked")),
    (("tiktok", "paid"), ("tiktok_ads", "Directly tracked")),
    (("tiktok", "organic_social"), ("tiktok_organic", "Directly tracked")),
    (("bing", "cpc"), ("search", "Directly tracked")),  # no Microsoft ads since 2026-10-28
    (("newsletter", "email"), ("email", "Directly tracked")),
    (("", "", "social", "facebook"), ("facebook_organic", "Inferred")),
    (("", "", "social", "tiktok"), ("tiktok_organic", "Inferred")),
    (("", "", "search", "google"), ("search", "Inferred")),
    (("", "", "direct", ""), ("direct", "Unattributed")),
    ((), ("direct", "Unattributed")),
])
def test_channel_of(args, expect):
    assert attribution.channel_of(*args) == expect


def test_unfilled_macros():
    assert attribution.unfilled_macros("__CAMPAIGN_NAME__", "x") == ["__CAMPAIGN_NAME__"]
    assert attribution.unfilled_macros("{{campaign.name}}", "{AdId}", "fb_photos") == ["{AdId}", "{{campaign.name}}"]
    assert attribution.unfilled_macros("fb_photos", "", None) == []


def test_order_channel_prefers_last_visit_tags():
    from studio import shopify_sync
    base = {f"{p}_{k}": "" for p in ("first", "last") for k in ("utm_source", "utm_medium", "source")}
    assert shopify_sync.order_channel({**base, "first_utm_source": "facebook", "first_utm_medium": "social",
                                       "last_utm_source": "tiktok", "last_utm_medium": "paid"}) == ("tiktok_ads", "Directly tracked")
    assert shopify_sync.order_channel({**base, "last_source": "Instagram"}) == ("instagram_organic", "Inferred")
    assert shopify_sync.order_channel(base) == ("direct", "Unattributed")


def test_ads_entities_replace_per_platform(tmp_path, monkeypatch):
    monkeypatch.setattr(ads_snapshot, "ENTITIES", tmp_path / "ads_entities.json")
    ads_snapshot.merge_entities("meta", [{"level": "campaign", "id": 1, "name": "A", "spend": "1.5"}], "p")
    ads_snapshot.merge_entities("tiktok", [{"level": "adgroup", "id": "2", "parent_id": "9", "name": "B"}], "p")
    ads_snapshot.merge_entities("meta", [{"level": "ad", "id": "3", "parent_id": "1", "name": "C"}], "p")
    e = json.loads((tmp_path / "ads_entities.json").read_text(encoding="utf-8"))
    assert sorted((x["platform"], x["id"]) for x in e) == [("meta", "3"), ("tiktok", "2")]
    with pytest.raises(SystemExit):
        ads_snapshot.merge_entities("meta", [{"level": "keyword", "id": "4"}], "p")


# --- Advertising > TikTok tests ------------------------------------------------------------------------------------

from studio import ad_tests  # noqa: E402


def _test_folder(tmp_path):
    t = tmp_path / "tests" / "t1"
    t.mkdir(parents=True)
    (t / "live.json").write_text(json.dumps({
        "test": "t1", "name": "Test one", "platform": "tiktok", "campaign_id": "c1", "campaign_name": "C", "adgroup_id": "g1",
        "launched_at": "2026-10-28T13:04:00-05:00", "daily_budget": 120.34, "angles": {"A": "Product", "B": "Lifestyle"},
        "rebate": {"target_conversions": 10, "trial_ends_at": "2026-11-04T12:04:00-06:00", "rule": "No edits."},
        "auto_add_creatives": True}), encoding="utf-8")
    (t / "products.json").write_text(json.dumps({"products": [{"test_product_id": "P001", "title": "Dress"}]}), encoding="utf-8")
    (t / "launch_set.json").write_text(json.dumps({"ads": [
        {"ad_name": "EC_TT_P001_A_PRODUCT", "product_id": "P001", "video": "x/EC_TT_P001_A_PRODUCT.mp4",
         "caption_variants": [{"text": "one"}, {"text": "two"}]},
        {"ad_name": "EC_TT_P001_B_LIFESTYLE", "product_id": "P001", "video": "x/EC_TT_P001_B_LIFESTYLE.mp4", "caption": "solo"}]}),
        encoding="utf-8")
    (t / "DAILY_CHECKS.md").write_text("# x\n\n| Date | Status | Spend | Impressions | Clicks | Purchases | Videos added by TikTok |\n"
                                       "|---|---|---|---|---|---|---|\n| 2026-10-29 | active | 12.50 | 900 | 20 | 0 | none |\n",
                                       encoding="utf-8")
    (t.parent / "draft_only").mkdir()  # no live.json: ignored
    return t.parent


def test_ad_tests_match_tiktok_names_and_find_added_videos(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "ads_entities.json").write_text(json.dumps([
        {"platform": "tiktok", "level": "ad", "name": "EC_TT_P001_A_PRODUCT_A36d.mp4_EC_TT_P001_A_PRODUCT", "parent_id": "g1",
         "spend": 4.5, "impressions": 300, "clicks": 9, "purchases": 1, "revenue": 170.16, "period": "2026-10-22..2026-10-28",
         "refreshed_at": "2026-10-28T15:00"},
        {"platform": "tiktok", "level": "ad", "name": "EC-P01-A06-H01-V02.mp4", "parent_id": "g1", "spend": 1},
        {"platform": "tiktok", "level": "ad", "name": "other campaign ad", "parent_id": "g9", "spend": 2},
        {"platform": "meta", "level": "ad", "name": "EC_TT_P001_B_LIFESTYLE", "parent_id": "g1", "spend": 3}]), encoding="utf-8")
    assert ad_tests.build(out, _test_folder(tmp_path)) == ["ad_tests 2", "ad_test_info 1", "ad_test_checks 1"]
    ads = {r["ad_name"]: r for r in json.loads((out / "ad_tests.json").read_text(encoding="utf-8"))}
    a, b = ads["EC_TT_P001_A_PRODUCT"], ads["EC_TT_P001_B_LIFESTYLE"]
    assert a["spend"] == 4.5 and a["purchases"] == 1 and a["product"] == "Dress" and a["angle"] == "A Product"
    assert a["captions"] == 2 and a["caption_all"] == "one\ntwo" and a["video"] == "EC_TT_P001_A_PRODUCT.mp4"
    assert b["spend"] is None and b["reported"] is False and b["captions"] == 1  # unknown stays null; Meta row ignored
    info = json.loads((out / "ad_test_info.json").read_text(encoding="utf-8"))[0]
    assert info["added_by_tiktok"] == 1 and info["added_names"] == "EC-P01-A06-H01-V02.mp4"  # other ad group not counted
    assert info["ads_reported"] == 1 and info["period"] == "2026-10-22..2026-10-28" and info["rebate_target"] == 10
    checks = json.loads((out / "ad_test_checks.json").read_text(encoding="utf-8"))
    assert checks == [{"test": "t1", "date": "2026-10-29", "status": "active", "spend": "12.50", "impressions": "900",
                       "clicks": "20", "purchases": "0", "added": "none"}]


def test_ad_tests_without_numbers_or_live_tests(tmp_path):
    out = tmp_path / "out"
    out.mkdir()  # no ads_entities.json at all
    assert ad_tests.build(out, _test_folder(tmp_path))[0] == "ad_tests 2"
    assert all(r["spend"] is None for r in json.loads((out / "ad_tests.json").read_text(encoding="utf-8")))
    empty = tmp_path / "none"
    empty.mkdir()
    assert ad_tests.build(out, empty) == ["ad_tests 0", "ad_test_info 0", "ad_test_checks 0"]


def test_tiktok_tests_page_is_a_sub_page_of_advertising(server):
    code, ctype, body = get(server + "/ads/tests")
    text = body.decode("utf-8")
    assert code == 200 and ctype.startswith("text/html") and 'id="tt-ads"' in text
    assert "TikTok tests" in text.split('aria-current="page"')[1].split("</a>")[0]
    assert {"ad_tests", "ad_test_info", "ad_test_checks"} <= set(json.loads(get(server + "/data")[2])["datasets"])
