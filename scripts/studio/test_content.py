"""Tests for Content Studio 2.0 Phase B: unified content records, honest publish states, PostZen retries, and the
Facebook publishing guards. Temporary databases and folders only; the live studio.db is never written.

Run: python -m pytest -q scripts/studio/test_content.py
"""
import datetime as dt
import json
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import facebook_photos  # noqa: E402
import postzen  # noqa: E402
from studio import content, db  # noqa: E402

FUTURE = "2099-01-01T12:00:00Z"
PAST = "2000-01-01T12:00:00Z"


@pytest.fixture()
def tmpdb(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB", tmp_path / "studio.db")
    return tmp_path / "studio.db"


# --- honest publish states -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("mode,status,sched,live,owner,expect", [
    ("draft", "scheduled", FUTURE, {}, False, "scheduled"),
    ("draft", "published", FUTURE, {}, False, "in_tiktok_drafts"),       # delivered to drafts, slot ahead
    ("draft", "published", PAST, {}, False, "awaiting_manual_post"),     # delivered, slot passed, still not public
    ("draft", "published", PAST, {"pz1": "33 views"}, False, "public"),  # public evidence
    ("draft", "published", PAST, {}, True, "public"),                    # owner recorded it
    ("draft", "draft", FUTURE, {}, False, "paused"),
    ("scheduled", "published", PAST, {}, False, "public"),               # PostZen posted it publicly itself
    ("scheduled", "draft", FUTURE, {}, False, "paused"),
    ("draft", "failed", FUTURE, {}, False, "failed"),
])
def test_tiktok_publish_state(mode, status, sched, live, owner, expect):
    assert content.tiktok_publish_state(mode, status, "pz1", sched, live, owner)[0] == expect


def test_a_draft_with_a_url_is_not_public():
    state, evidence = content.tiktok_publish_state("draft", "published", "pz9", PAST, {}, False)
    assert state != "public" and "no public views" in evidence


@pytest.mark.parametrize("status,expect", [("published", "public"), ("scheduled", "scheduled"), ("draft", "paused"),
                                           ("failed", "failed"), ("queued", "scheduled")])
def test_fb_publish_state(status, expect):
    assert content.fb_publish_state(status, "u")[0] == expect


# --- mirrors -------------------------------------------------------------------------------------------------------

def _episode(con, ep_id="EW-20990101-1", **kw):
    row = {"id": ep_id, "series_id": "get-ready", "title": "Test", "post_date": "2099-01-01", "slot": "08:30",
           "outfit_json": "[]", "script_json": json.dumps({"lines": ["Hook line.", "b", "c", "d"]}), "caption": "Cap #aigenerated",
           "state": "SCHEDULED", "test": 0, "postzen_post_id": "pz1", "publish_mode": "draft", "platform_status": "published",
           "created_at": "x", "updated_at": "x"} | kw
    con.execute(f"INSERT INTO episodes ({', '.join(row)}) VALUES ({', '.join('?' * len(row))})", list(row.values()))
    con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                (ep_id, "APPROVED", "SCHEDULED", "claude", "scheduled", "2026-10-27T10:00:00"))
    con.commit()


def test_mirror_tiktok_is_idempotent_and_honest(tmpdb, tmp_path):
    con = content.connect()
    _episode(con)
    _episode(con, "EW-20990101-2", test=1)  # test episodes are never mirrored
    for _ in range(2):
        assert content.mirror_tiktok(con, None, tmp_path) == 1
    item = con.execute("SELECT * FROM content_items").fetchone()
    assert item["content_id"] == "TT-EW-20990101-1" and item["state"] == "in_tiktok_drafts"
    assert item["hook_text"] == "Hook line." and item["ai_disclosure"] == 1
    assert con.execute("SELECT COUNT(*) FROM content_events").fetchone()[0] == 1  # copied once
    job = con.execute("SELECT * FROM publish_jobs").fetchone()
    assert job["state"] == "in_tiktok_drafts" and job["idempotency_key"] == "pz:pz1"
    # public evidence from the analytics file flips it to public
    (tmp_path / "tiktok_videos.csv").write_text("post_id,views,impressions\npz1,12,12\n", encoding="utf-8")
    content.mirror_tiktok(con, None, tmp_path)
    assert con.execute("SELECT state FROM content_items").fetchone()[0] == "public"


def test_mirror_facebook(tmpdb, tmp_path):
    plan = {"start": "2099-02-01", "posts": [
        {"date": "2099-02-01", "slot": "09:00", "kind": "product", "products": ["a"], "titles": ["A"],
         "photos": ["https://media.postzen.dev/x/1.png"], "caption": "A\n\nShop it here: link\n\n#aigenerated",
         "first_comment": None, "postzen_post_id": "p1", "status": "scheduled",
         "approval": {"quote": "yes", "at": "t"}},
        {"date": "2099-02-01", "slot": "19:00", "kind": "outfit", "products": ["b", "c", "d"], "titles": ["B", "C", "D"],
         "photos": ["https://cdn.shopify.com/s/files/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.jpg"], "caption": "B",
         "first_comment": "Shop the pieces"}]}
    (tmp_path / "plan_2099-02-01.json").write_text(json.dumps(plan), encoding="utf-8")
    con = content.connect()
    assert content.mirror_facebook(con, tmp_path) == 2
    a, b = [dict(r) for r in con.execute("SELECT * FROM content_items ORDER BY content_id")]
    assert a["content_id"] == "FB-2099-02-01-00" and a["kind"] == "fb_ai_picture" and a["state"] == "scheduled"
    assert a["link_placement"] == "caption" and a["ai_disclosure"] == 1 and json.loads(a["approval_json"])["quote"] == "yes"
    assert b["kind"] == "fb_photo" and b["state"] == "awaiting_approval" and b["link_placement"] == "first_comment"
    assert con.execute("SELECT COUNT(*) FROM content_products WHERE content_id = ?", (b["content_id"],)).fetchone()[0] == 3
    # a status change seen on a later sync becomes an event
    plan["posts"][0]["status"] = "published"
    (tmp_path / "plan_2099-02-01.json").write_text(json.dumps(plan), encoding="utf-8")
    content.mirror_facebook(con, tmp_path)
    ev = [tuple(r) for r in con.execute("SELECT from_state, to_state FROM content_events WHERE content_id = ?", (a["content_id"],))]
    assert ev[-1] == ("scheduled", "public")


def test_record_publish_updates_one_row(tmpdb):
    con = content.connect()
    content.record_publish(con, "TT-1", "tiktok", "tiktok_draft", "k1", state="submitting", attempt=1)
    content.record_publish(con, "TT-1", "tiktok", "tiktok_draft", "k1", state="submitted", postzen_post_id="p", attempt=1)
    rows = con.execute("SELECT state, postzen_post_id, attempts FROM publish_jobs").fetchall()
    assert [tuple(r) for r in rows] == [("submitted", "p", 2)]


def test_upload_media_once(tmpdb, tmp_path):
    f = tmp_path / "v.mp4"
    f.write_bytes(b"video")
    calls = []

    class FakePZ:
        @staticmethod
        def upload(path):
            calls.append(path)
            return "https://media/v.mp4"

    con = content.connect()
    assert content.upload_media(con, f, FakePZ)[0] == content.upload_media(con, f, FakePZ)[0] == "https://media/v.mp4"
    assert len(calls) == 1


def test_atomic_write(tmp_path):
    p = tmp_path / "a.json"
    content.atomic_write(p, "one")
    content.atomic_write(p, "two")
    assert p.read_text(encoding="utf-8") == "two" and not list(tmp_path.glob(".*.tmp"))


# --- PostZen retries ----------------------------------------------------------------------------------------------

class _Resp:
    def __init__(self, code, body=b"{}"):
        self.status_code, self.content, self.ok, self.headers, self.text = code, body, code < 400, {}, body.decode()
        self.request = type("R", (), {"method": "X"})()
        self.url = "https://api.postzen.dev/v1/x"

    def json(self):
        return json.loads(self.content)


def test_postzen_retries_reads_and_keyed_creates(monkeypatch):
    seq = [503, 429, 200]
    monkeypatch.setattr(postzen.time, "sleep", lambda s: None)
    monkeypatch.setattr(postzen, "_headers", lambda: {})
    monkeypatch.setattr(postzen.requests, "request", lambda *a, **k: _Resp(seq.pop(0)))
    assert postzen.get("posts") == {}
    seq[:] = [502, 200]
    assert postzen.post("posts", {}, idempotency_key="k") == {}


def test_postzen_does_not_retry_unkeyed_creates(monkeypatch):
    seq = [503, 200]
    monkeypatch.setattr(postzen.time, "sleep", lambda s: None)
    monkeypatch.setattr(postzen, "_headers", lambda: {})
    monkeypatch.setattr(postzen.requests, "request", lambda *a, **k: _Resp(seq.pop(0)))
    with pytest.raises(RuntimeError):
        postzen.post("posts", {})
    assert seq == [200]  # only one attempt was made


# --- Facebook guards ------------------------------------------------------------------------------------------------

def _product():
    return {"handle": "h", "title": "Soft Knit Top", "product_type": "Tops & Bodysuits", "options": [],
            "body_html": "<p>A soft knit top for cool days.</p>"}


def test_link_goes_in_caption_by_default(monkeypatch):
    monkeypatch.setattr(facebook_photos, "clean_photos", lambda p, n: ["https://x/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.jpg"])
    monkeypatch.setattr(facebook_photos, "link", lambda p, rules, day, slot, cid=None: "https://shop/link")
    post = facebook_photos.single_post(_product(), {"max_photos": 4}, random.Random(1), "2099-01-01", "09:00")
    assert post["first_comment"] is None and post["caption"].endswith("Shop it here: https://shop/link")
    post = facebook_photos.single_post(_product(), {"max_photos": 4, "link_placement": "first_comment"}, random.Random(1),
                                       "2099-01-01", "09:00")
    assert post["first_comment"] == "Shop it here: https://shop/link" and "Shop it here" not in post["caption"]


def test_ai_detection():
    real = {"photos": ["https://cdn.shopify.com/s/files/1/x/C892BA562BF4D42B54BB009A73B48380.jpg?v=1"]}
    assert not facebook_photos.is_ai_post(real)
    assert facebook_photos.is_ai_post({"photos": ["https://media.postzen.dev/u/b080c5ac_02_crossover_top.png"]})
    assert facebook_photos.is_ai_post({**real, "ai_picture": "data/x.png"})


def test_publish_refuses_ai_post_without_disclosure(tmpdb, tmp_path, monkeypatch, capsys):
    plan = {"start": "2099-03-01", "posts": [{"date": "2099-03-01", "slot": "09:00", "kind": "product", "products": ["a"],
            "titles": ["A"], "photos": ["https://media.postzen.dev/u/x.png"], "caption": "A nice top", "first_comment": None}]}
    path = tmp_path / "plan_2099-03-01.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    monkeypatch.setattr(facebook_photos, "HISTORY", tmp_path / "history.json")
    monkeypatch.setattr(facebook_photos.hub_env, "load_config", lambda: {"postzen": {"facebook_account_id": "acc"}})
    monkeypatch.setattr(postzen, "post", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not send")))
    facebook_photos.publish(path, "owner words")
    assert "refused" in capsys.readouterr().out
    assert "postzen_post_id" not in json.loads(path.read_text(encoding="utf-8"))["posts"][0]


def test_plan_refuses_to_overwrite_a_sent_week(tmp_path, monkeypatch):
    monkeypatch.setattr(facebook_photos, "DIR", tmp_path)
    (tmp_path / "plan_2099-04-01.json").write_text(json.dumps({"posts": [{"postzen_post_id": "p"}]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="already has 1 post"):
        facebook_photos.make_plan(dt.date(2099, 4, 1), 7)


def test_frame_route_only_serves_real_episode_ids():
    from studio import dashboard_server
    for bad in ("../../config/hub", "EW-20261103-1/../../x", "", "TT-EW-20261103-1", "EW-20261102-2-T1"):
        assert dashboard_server.episode_frames(bad) is None


# --- Phase C: generation records, features, marks, links ------------------------------------------------------------

def test_generation_job_lifecycle(tmpdb, tmp_path, monkeypatch):
    monkeypatch.setattr(content, "HUB", tmp_path)
    con = content.connect()
    jid = content.start_job(con, "TT-EW-1", "video", "openrouter", "bytedance/seedance-2.5", {"resolution": "480p"},
                            prompt_hash="abc", prompt_text="p", refs=["https://x/a.jpg", "https://x/b.jpg"])
    assert con.execute("SELECT status FROM generation_jobs WHERE job_id = ?", (jid,)).fetchone()[0] == "running"
    out = tmp_path / "v.mp4"
    out.write_bytes(b"video")
    aid = content.finish_job(con, jid, "completed", "or-1", 1.44, "billed", output_path=out)
    j = con.execute("SELECT * FROM generation_jobs WHERE job_id = ?", (jid,)).fetchone()
    assert (j["status"], j["provider_job_id"], j["cost_usd"], j["asset_id"]) == ("completed", "or-1", 1.44, aid)
    assert con.execute("SELECT sha256 FROM assets WHERE asset_id = ?", (aid,)).fetchone()[0] == content.sha256_file(out)
    assert con.execute("SELECT COUNT(*) FROM asset_refs WHERE job_id = ?", (jid,)).fetchone()[0] == 2


def test_failed_job_keeps_no_cost(tmpdb):
    con = content.connect()
    jid = content.start_job(con, "IMG-x/1", "image", "higgsfield", "flare")
    content.finish_job(con, jid, "failed", error="TimeoutError: slow")
    j = con.execute("SELECT status, cost_usd, error, asset_id FROM generation_jobs WHERE job_id = ?", (jid,)).fetchone()
    assert tuple(j) == ("failed", None, "TimeoutError: slow", None)


def test_backfill_is_idempotent(tmpdb, tmp_path, monkeypatch):
    monkeypatch.setattr(content, "HUB", tmp_path)
    con = content.connect()
    _episode(con, model="bytedance/seedance-2.5")
    ep_dir = tmp_path / "studio" / "episodes" / "EW-20990101-1"
    ep_dir.mkdir(parents=True)
    (ep_dir / "EW-20990101-1_a1.mp4").write_bytes(b"v")
    con.executemany("INSERT INTO spend (episode_id, usd, at) VALUES (?,?,?)",
                    [("EW-20990101-1", 0.07, "t1"), ("EW-20990101-1", 1.44, "t2"), ("EW-20990101-1", 0, "t3")])
    con.commit()
    assert content.backfill_generation(con) == 3
    assert content.backfill_generation(con) == 0
    rows = {r["cost_usd"]: (r["kind"], r["status"]) for r in con.execute("SELECT * FROM generation_jobs")}
    assert rows == {0.07: ("image", "completed"), 1.44: ("video", "completed"), 0: ("video", "failed_or_unknown")}


def test_owner_features_are_never_overwritten(tmpdb):
    con = content.connect()
    content.ensure_schema(con)
    content.set_feature(con, "TT-1", "hook_type", "pov", source="owner")
    content.set_feature(con, "TT-1", "hook_type", "question")
    content.set_feature(con, "TT-1", "room", "closet")
    got = {r[0]: r[1] for r in con.execute("SELECT feature, value FROM content_features WHERE content_id = ?", ("TT-1",))}
    assert got == {"hook_type": "pov", "room": "closet"}


@pytest.mark.parametrize("line, expect", [("POV: you overslept", "pov"), ("Can you wear this?", "question"),
                                          ("Three ways to style it.", "statement"), ("", None)])
def test_hook_type(line, expect):
    assert content.hook_type(line) == expect


def _analytics(path, snaps=(), sources=()):
    import sqlite3
    a = sqlite3.connect(path)
    a.execute("CREATE TABLE post_snapshots (post_id TEXT, fetched_at TEXT, views INT, impressions INT, reach INT, likes INT, "
              "comments INT, shares INT, saves INT, clicks INT)")
    a.execute("CREATE TABLE store_sources_daily (day TEXT, kind TEXT, content TEXT, sessions INT, cart_sessions INT, "
              "checkout_sessions INT, completed_sessions INT)")
    a.executemany("INSERT INTO post_snapshots VALUES (?,?,?,?,0,0,0,0,0,0)", snaps)
    a.executemany("INSERT INTO store_sources_daily VALUES (?,?,?,?,?,?,?)", sources)
    a.commit()
    a.close()
    return path


def _marks(con, cid):
    return {r["mark"]: r for r in con.execute("SELECT * FROM content_marks WHERE content_id = ?", (cid,))}


def test_marks_only_from_real_snapshots_in_the_window(tmpdb, tmp_path):
    con = content.connect()
    content.ensure_schema(con)
    content.record_publish(con, "FB-1", "facebook", "facebook_scheduled", "k1", state="public", postzen_post_id="fb1",
                           scheduled_for="2026-10-20T13:00:00Z")
    # 24h: a snapshot 2 h after the mark is used. 48h: only one 8 h late, so it stays empty. 7d: not reached yet.
    path = _analytics(tmp_path / "a.db", [("fb1", "2026-10-20T14:00:00Z", 5, 9), ("fb1", "2026-10-21T15:00:00Z", 40, 80),
                                          ("fb1", "2026-10-22T21:00:00Z", 60, 120)])
    content.compute_marks(con, path)
    marks = _marks(con, "FB-1")
    assert set(marks) == {"24h", "latest"}
    assert marks["24h"]["snapshot_at"] == "2026-10-21T15:00:00Z" and marks["latest"]["snapshot_at"] == "2026-10-22T21:00:00Z"
    assert marks["24h"]["anchor_basis"] == "scheduled publish time"


def test_hand_posted_draft_is_timed_from_first_views(tmpdb, tmp_path):
    con = content.connect()
    content.ensure_schema(con)
    content.record_publish(con, "TT-1", "tiktok", "tiktok_draft", "k1", state="public", postzen_post_id="tt1",
                           scheduled_for="2026-10-20T12:00:00Z")
    path = _analytics(tmp_path / "a.db", [("tt1", "2026-10-20T12:15:00Z", 0, 0), ("tt1", "2026-10-21T09:00:00Z", 3, 3),
                                          ("tt1", "2026-10-22T10:00:00Z", 50, 50)])
    content.compute_marks(con, path)
    m = _marks(con, "TT-1")["24h"]
    assert m["anchor_at"] == "2026-10-21T09:00:00Z" and m["snapshot_at"] == "2026-10-22T10:00:00Z"
    assert "posted by hand" in m["anchor_basis"]


def test_links_and_store_sessions_by_content_id(tmpdb, tmp_path):
    con = content.connect()
    content.ensure_schema(con)
    content.upsert_item(con, {"content_id": "FB-2099-01-01-00", "channel": "facebook", "kind": "fb_photo", "workflow": "fb",
                              "state": "scheduled", "caption": "Soft top.\nShop it here: https://emberandclove.com/products/h"
                              "?utm_source=facebook&utm_content=FB-2099-01-01-00"})
    assert content.collect_links(con) == 1
    path = _analytics(tmp_path / "a.db", sources=[("2099-01-01", "utm", "FB-2099-01-01-00", 4, 1, 1, 0),
                                                  ("2099-01-02", "utm", "FB-2099-01-01-00", 2, 0, 0, 0),
                                                  ("2099-01-02", "utm", "other", 9, 9, 9, 9)])
    got = content.store_sessions_by_content(con, path)
    assert got == {"FB-2099-01-01-00": {"sessions": 6, "cart_sessions": 1, "checkout_sessions": 1, "completed_sessions": 0}}


def test_ai_picture_needs_no_caption_tag(tmpdb):
    # owner 2026-10-28: no #aigenerated in captions, so an AI picture without it is not an issue
    con = content.connect()
    content.ensure_schema(con)
    content.upsert_item(con, {"content_id": "FB-x", "channel": "facebook", "kind": "fb_ai_picture", "workflow": "fb",
                              "state": "scheduled", "ai_disclosure": 0})
    assert not any("aigenerated" in i["check"] for i in content.quality_checks(con))
    assert checks.disclosure_findings("Soft knit. #aigenerated", True)[0]["severity"] == "medium"
    assert checks.disclosure_findings("Soft knit.", True) == []


def test_facebook_link_carries_the_content_id():
    rules = {"store_url": "https://emberandclove.com"}
    url = facebook_photos.link({"handle": "soft-top"}, rules, "2099-01-01", "09:00", "FB-2099-01-01-00")
    assert "utm_content=FB-2099-01-01-00" in url and "utm_campaign=fb_photos" in url
    assert "utm_content=2099-01-01_0900" in facebook_photos.link({"handle": "soft-top"}, rules, "2099-01-01", "09:00")


# --- Phase D: shared rules, availability, media-bound approvals, Facebook AI-picture workflow -------------------------

from studio import checks, fb_ai  # noqa: E402


@pytest.mark.parametrize("text, expect", [
    ("Only $20 today!", {"price"}), ("Free shipping, arrives in 3 days.", {"delivery"}),
    ("Limited stock, hurry.", {"urgency"}), ("I ordered two.", {"testimonial"}),
    ("Keeps you warm.", {"claim"}), ("A soft knit top for cool days.", set()),
    ("Shop it here: https://emberandclove.com/products/relationship-sale-top?utm_content=x", set())])
def test_caption_rules(text, expect):
    assert {f["check"] for f in checks.text_findings(text)} == expect


def test_caption_rule_severities():
    sev = {f["check"]: f["severity"] for f in checks.text_findings("Was $40. Keeps you warm. Follow me!")}
    assert sev == {"price": "critical", "claim": "high", "cta": "medium"}


def test_script_rules_keep_their_old_messages():
    assert checks.script_errors("it ships fast for $5", ["ships"], [r"\$\s?\d"]) == ["banned phrase: 'ships'",
                                                                                   "banned pattern: \\$\\s?\\d"]


def _store(path, products):
    import sqlite3
    a = sqlite3.connect(path)
    a.execute("CREATE TABLE products (product_id TEXT, title TEXT, handle TEXT, status TEXT, product_type TEXT, image TEXT, "
              "inventory INT, fetched_at TEXT)")
    a.execute("CREATE TABLE variants (variant_id TEXT, product_id TEXT, title TEXT, price REAL, unit_cost REAL, grams REAL, "
              "inventory INT)")
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for i, (handle, status, inv) in enumerate(products):
        a.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", (f"gid://shopify/Product/{i}", handle, handle, status,
                                                                    "Tops", None, inv, now))
        a.execute("INSERT INTO variants VALUES (?,?,?,?,?,?,?)", (f"v{i}", f"gid://shopify/Product/{i}", "S", 10, 3, 1, inv))
    a.commit()
    a.close()
    return path


def test_availability(tmp_path):
    path = _store(tmp_path / "a.db", [("live", "ACTIVE", 100), ("gone", "ARCHIVED", 100), ("empty", "ACTIVE", 0)])
    got = {f["check"]: f["severity"] for f in checks.availability(["live", "gone", "empty", "missing"], path)}
    assert got == {"product_unavailable": "critical", "out_of_stock": "critical", "product_unknown": "high"}
    assert checks.availability(["gid://shopify/Product/0"], path) == []  # wardrobe pieces are stored as gids


def test_binding_and_overrides(tmpdb):
    assert checks.binding_findings(None, "a", "c")[0]["check"] == "not_approved"
    assert checks.binding_findings({"quote": "ok"}, "a", "c")[0]["check"] == "approval_unbound"
    ok = {"asset_sha256": "a", "caption_sha256": "c"}
    assert checks.binding_findings(ok, "a", "c") == []
    assert {f["check"] for f in checks.binding_findings(ok, "b", "d")} == {"media_changed", "caption_changed"}
    con = content.connect()
    high = [checks.finding("high", "claim", "'warm' (claim)"), checks.finding("critical", "price", "'$4'")]
    with pytest.raises(ValueError):
        checks.record_override(con, "TT-1", "claim", "a", "c", "fine by me", "claude")
    with pytest.raises(ValueError):
        checks.record_override(con, "TT-1", "price", "a", "c", "fine by me", "owner")
    checks.record_override(con, "TT-1", "claim", "a", "c", "fine by me", "owner")
    assert [f["check"] for f in checks.unresolved(high, checks.overrides(con, "TT-1"), "a", "c")] == ["price"]
    assert len(checks.unresolved(high, checks.overrides(con, "TT-1"), "a", "OTHER")) == 2  # bound to the caption


def test_upcoming_items_are_flagged_when_a_product_goes_inactive(tmpdb, tmp_path):
    con = content.connect()
    content.upsert_item(con, {"content_id": "FB-x", "channel": "facebook", "kind": "fb_photo", "workflow": "fb_photo",
                              "state": "scheduled", "caption": "A soft knit top.", "scheduled_at": FUTURE})
    content.set_children(con, "FB-x", [("gone", None, "featured")], [])
    path = _store(tmp_path / "a.db", [("gone", "DRAFT", 5)])
    assert content.upcoming_checks(con, path)["FB-x"][0]["check"] == "product_unavailable"


def test_facebook_publish_refuses_an_inactive_product(tmpdb, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(facebook_photos, "HISTORY", tmp_path / "history.json")
    monkeypatch.setattr(checks, "availability", lambda handles, *a, **k: [checks.finding("critical", "out_of_stock", "h")])
    monkeypatch.setattr(facebook_photos.hub_env, "load_config", lambda: {"postzen": {"facebook_account_id": "acc"}})
    monkeypatch.setattr(facebook_photos, "load_rules", lambda: {"timezone": "America/New_York"})
    path = tmp_path / "plan_2099-05-01.json"
    path.write_text(json.dumps({"start": "2099-05-01", "posts": [
        {"date": "2099-05-01", "slot": "09:00", "kind": "product", "products": ["h"], "titles": ["T"],
         "photos": ["https://cdn/" + "A" * 32 + ".jpg"], "caption": "A soft top.", "first_comment": None}]}), encoding="utf-8")
    facebook_photos.publish(path, "go")
    out = capsys.readouterr().out
    assert "refused" in out and "out_of_stock" in out
    assert not json.loads(path.read_text(encoding="utf-8"))["posts"][0].get("postzen_post_id")


# --- the Facebook AI-picture workflow, end to end with fake providers --------------------------------------------------

FB_RULES = {"vendor": "EC", "skip_handles": [], "cold_season": ["10-01", "03-31"], "warm_only_types": [],
            "warm_only_tags": [], "warm_only_title_words": [], "cold_only_tags": [], "slots_weekday": ["09:00"],
            "slots_weekend": ["10:00"], "outfit_every": 99, "no_repeat_days": 14, "max_photos": 4,
            "store_url": "https://emberandclove.com", "link_placement": "caption", "timezone": "America/New_York"}


def _feed(n=2):
    return [{"handle": f"top-{i}", "title": f"Soft Top {i}", "vendor": "EC", "product_type": "Tops & Bodysuits",
             "tags": [], "options": [], "body_html": "<p>A soft knit top for cool days.</p>",
             "images": [{"src": f"https://cdn/{'A' * 31}{i}.jpg"}]} for i in range(n)]


class FakeHF:
    def __init__(self):
        self.n = 0

    def submit(self, path, payload):
        self.payload = payload
        return {"status_url": "s", "request_id": f"r{self.n}"}

    def wait(self, url, every, timeout_s):
        self.n += 1
        return {"status": "completed", "images": [{"url": f"https://hf/img{self.n}.png"}]}

    def download(self, url, dest):
        Path(dest).write_bytes(b"png " + url.encode())


class FakePZ:
    def __init__(self):
        self.sent = []

    def upload(self, path):
        return "https://media.postzen.dev/pic.png"

    def post(self, path, body, idempotency_key=None):
        self.sent.append((body, idempotency_key))
        return {"post": {"_id": f"pz{len(self.sent)}", "status": "scheduled"}}


@pytest.fixture
def fbweek(tmpdb, tmp_path, monkeypatch):
    for mod in (fb_ai, content):
        monkeypatch.setattr(mod, "HUB", tmp_path)
    monkeypatch.setattr(fb_ai, "OUT", tmp_path / "media")
    monkeypatch.setattr(facebook_photos, "no_ai_marker", lambda u: True)
    monkeypatch.setattr(facebook_photos, "DIR", tmp_path)
    monkeypatch.setattr(facebook_photos, "HISTORY", tmp_path / "history.json")
    con = content.connect()
    posts = fb_ai.plan_week(con, dt.date(2099, 1, 5), 2, _feed(), FB_RULES, [])
    store = _store(tmp_path / "a.db", [("top-0", "ACTIVE", 100), ("top-1", "ACTIVE", 100)])
    return con, [p["content_id"] for p in posts], store


def test_ai_week_is_made_in_the_database(fbweek):
    con, ids, _ = fbweek
    assert ids == ["FB-2099-01-05-00", "FB-2099-01-05-01"]
    rows = {r["content_id"]: dict(r) for r in con.execute("SELECT * FROM content_items")}
    assert all(r["state"] == "planned" and r["kind"] == "fb_ai_picture" and r["plan_file"] is None for r in rows.values())
    cap = rows[ids[0]]["caption"]
    assert "#aigenerated" not in cap and "utm_content=FB-2099-01-05-00" in cap
    with pytest.raises(SystemExit):
        fb_ai.plan_week(con, dt.date(2099, 1, 5), 2, _feed(), FB_RULES, [])  # never planned twice


def test_ai_post_walks_every_step_and_is_sent_once(fbweek):
    con, ids, store = fbweek
    cid, hf, pz = ids[0], FakeHF(), FakePZ()
    fb_ai.generate(con, cid, hf)
    assert "Copy every product exactly" in hf.payload["prompt"] and hf.payload["image_urls"][0].startswith("https://cdn/")
    job = con.execute("SELECT * FROM generation_jobs WHERE content_ref = ?", (cid,)).fetchone()
    assert job["status"] == "completed" and job["template"] == "fb_ai_picture.j2" and job["cost_basis"] == "not reported"
    with pytest.raises(SystemExit):
        fb_ai.qa(con, cid, store)  # no fidelity verdict yet
    fb_ai.verdict(con, cid, True)
    assert fb_ai.qa(con, cid, store) == []
    with pytest.raises(SystemExit):
        fb_ai.approve(con, cid, "looks good")  # Claude only under the owner's standing instruction
    fb_ai.approve(con, cid, "Owner 2026-10-27: i dont need to approve every image i approve do it")
    post = fb_ai.schedule(con, cid, pz, FB_RULES, "acc", store)
    assert post["_id"] == "pz1" and pz.sent[0][1] == f"fbai-{cid}"
    assert pz.sent[0][0]["mediaItems"] == [{"url": "https://media.postzen.dev/pic.png"}]
    assert con.execute("SELECT state FROM content_items WHERE content_id = ?", (cid,)).fetchone()[0] == "scheduled"
    with pytest.raises(SystemExit):
        fb_ai.schedule(con, cid, pz, FB_RULES, "acc", store)  # already sent
    steps = [r[0] for r in con.execute("SELECT to_state FROM content_events WHERE content_id = ? ORDER BY id", (cid,))]
    assert steps == ["planned", "image_generated", "captioned", "awaiting_approval", "approved", "scheduled"]


def test_failed_fidelity_holds_the_picture_until_a_new_one(fbweek):
    con, ids, store = fbweek
    cid = ids[0]
    fb_ai.generate(con, cid, FakeHF())
    fb_ai.verdict(con, cid, False, "print is wrong", failed_checks=["product_match"])
    with pytest.raises(SystemExit):
        fb_ai.qa(con, cid, store)
    fb_ai.generate(con, cid, FakeHF())
    assert con.execute("SELECT fidelity_json FROM fb_ai_posts WHERE content_id = ?", (cid,)).fetchone()[0] is None


def _approved(fbweek):
    con, ids, store = fbweek
    cid = ids[0]
    fb_ai.generate(con, cid, FakeHF())
    fb_ai.verdict(con, cid, True)
    fb_ai.qa(con, cid, store)
    fb_ai.approve(con, cid, "the owner approves", actor="owner")
    return con, cid, store


def test_a_changed_picture_cannot_go_out_under_the_old_approval(fbweek, tmp_path):
    con, cid, store = _approved(fbweek)
    (tmp_path / con.execute("SELECT image_path FROM fb_ai_posts WHERE content_id = ?", (cid,)).fetchone()[0]).write_bytes(b"edited")
    pz = FakePZ()
    with pytest.raises(SystemExit, match="media_changed"):
        fb_ai.schedule(con, cid, pz, FB_RULES, "acc", store)
    assert pz.sent == []


def test_a_changed_caption_cannot_go_out_under_the_old_approval(fbweek):
    con, cid, store = _approved(fbweek)
    con.execute("UPDATE fb_ai_posts SET caption = caption || ' New line.' WHERE content_id = ?", (cid,))
    with pytest.raises(SystemExit, match="caption_changed"):
        fb_ai.schedule(con, cid, FakePZ(), FB_RULES, "acc", store)


def test_an_out_of_stock_product_blocks_its_post(fbweek, tmp_path):
    con, cid, _ = _approved(fbweek)
    empty = _store(tmp_path / "b.db", [("top-0", "ACTIVE", 0), ("top-1", "ACTIVE", 0)])
    with pytest.raises(SystemExit, match="out_of_stock"):
        fb_ai.schedule(con, cid, FakePZ(), FB_RULES, "acc", empty)
    assert con.execute("SELECT state FROM content_items WHERE content_id = ?", (cid,)).fetchone()[0] == "approved"


def test_refresh_records_public(fbweek):
    con, cid, store = _approved(fbweek)
    fb_ai.schedule(con, cid, FakePZ(), FB_RULES, "acc", store)

    class StatusPZ:
        def get(self, path):
            return {"post": {"platforms": [{"status": "published", "platformPostUrl": "https://fb/p/1"}]}}
    assert fb_ai.refresh(con, StatusPZ()) == 1
    assert con.execute("SELECT state FROM content_items WHERE content_id = ?", (cid,)).fetchone()[0] == "public"
    assert fb_ai.schedule_rows(con)[0]["post_url"] == "https://fb/p/1"


# --- Phase D item 6: Facebook outfit compatibility and caption rotation ---------------------------------------------

def _piece(title, ptype):
    return {"title": title, "product_type": ptype, "handle": title.lower().replace(" ", "-")}


@pytest.mark.parametrize("titles, expect", [
    ([("Rib Knit Top", "Tops & Bodysuits"), ("Denim Skirt", "Skirts"), ("Suede Jacket", "Outerwear")], []),
    ([("Lace Top", "Tops & Bodysuits"), ("Ripped Jeans", "Jeans & Pants"), ("Wool Coat", "Outerwear")], []),
    ([("Leopard Print Top", "Tops & Bodysuits"), ("Plaid Skirt", "Skirts"), ("Coat", "Outerwear")],
     ["2 patterned pieces (max 1)"]),
    ([("Satin Blouse", "Tops & Bodysuits"), ("Jogger Pants", "Jeans & Pants"), ("Coat", "Outerwear")],
     ["dressy and lounge pieces mixed"]),
    ([("Top A", "Tops & Bodysuits"), ("Top B", "Tops & Bodysuits"), ("Coat", "Outerwear")], ["two pieces of the same type"])])
def test_outfit_compatibility(titles, expect):
    assert facebook_photos.outfit_problems([_piece(t, k) for t, k in titles], {}) == expect


def test_outfit_rules_can_be_overridden_in_rules_json():
    parts = [_piece("Leopard Print Top", "Tops"), _piece("Plaid Skirt", "Skirts"), _piece("Coat", "Outerwear")]
    assert facebook_photos.outfit_problems(parts, {"outfit_rules": {"max_patterned": 2}}) == []


def test_pick_outfit_never_returns_a_clash():
    pool = [_piece("Satin Cami", "Tops & Bodysuits"), _piece("Rib Knit Top", "Tops & Bodysuits"),
            _piece("Jogger Pants", "Jeans & Pants"), _piece("Straight Jeans", "Jeans & Pants"),
            _piece("Wool Coat", "Outerwear")]
    for seed in range(30):
        parts = facebook_photos.pick_outfit(pool, random.Random(seed), set(), {})
        assert parts and not facebook_photos.outfit_problems(parts, {})
    assert facebook_photos.pick_outfit(pool[:1] + pool[2:3] + pool[4:], random.Random(1), set(), {}) is None


def test_captions_rotate_and_questions_never_repeat_back_to_back(monkeypatch):
    monkeypatch.setattr(facebook_photos, "no_ai_marker", lambda u: True)
    rules = {**FB_RULES, "outfit_every": 3}
    products = _feed(6) + [{**_feed(1)[0], "handle": f"bottom-{i}", "title": f"Denim Skirt {i}", "product_type": "Skirts"}
                           for i in range(3)] + [{**_feed(1)[0], "handle": "coat", "title": "Wool Coat", "product_type": "Outerwear"}]
    history = [{"date": "2099-01-04", "slot": "10:00", "products": [], "caption_format": "title_first",
                "question": "How would you style it?"}]
    posts = facebook_photos.plan(dt.date(2099, 1, 5), 5, rules, products, history)
    fmts = ["title_first"] + [p["caption_format"] for p in posts]
    qs = ["How would you style it?"] + [p["question"] for p in posts]
    assert all(a != b for a, b in zip(fmts, fmts[1:])), fmts
    assert all(a != b for a, b in zip(qs, qs[1:]) if a != "Which piece would you wear first?"), qs
    assert any(p["kind"] == "outfit" for p in posts)
    for p in posts:  # every format still ends with the store link and asks its question
        assert "https://emberandclove.com/products/" in p["caption"].rstrip().split("\n")[-1] and p["question"] in p["caption"]


# --- Phase D item 7: Ember's references library ---------------------------------------------------------------------

@pytest.fixture
def library(tmpdb, tmp_path, monkeypatch):
    from studio import character_refs
    monkeypatch.setattr(character_refs, "HUB", tmp_path)
    monkeypatch.setattr(content, "HUB", tmp_path)
    bdir = tmp_path / "studio" / "bible"
    (tmp_path / "studio" / "refs" / "candidates").mkdir(parents=True)
    bdir.mkdir(parents=True)
    (bdir / "character.yaml").write_text('approved_at: "2026-10-26T16:16:30"\n'
                                         "face_refs: [studio/refs/face_main.png]   # owner chose option B\n", encoding="utf-8")
    (bdir / "approvals.log").write_text("2026-10-26T16:16:30\tcharacter\towner: Ember is the name and i approve it\n",
                                        encoding="utf-8")
    (tmp_path / "studio" / "refs" / "face_main.png").write_bytes(b"face B")
    (tmp_path / "studio" / "refs" / "candidates" / "face_option_A.png").write_bytes(b"face A")
    (tmp_path / "studio" / "refs" / "candidates" / "face_option_B.png").write_bytes(b"face B")
    con = content.connect()
    _episode(con, "EW-20990101-1", state="SCHEDULED", video_path="studio/episodes/EW-20990101-1/v.mp4",
             approval_json=json.dumps({"owner_quote": "these are approved", "at": "2026-10-26T20:00:00"}))
    (tmp_path / "studio" / "episodes" / "EW-20990101-1").mkdir(parents=True)
    (tmp_path / "studio" / "episodes" / "EW-20990101-1" / "v_frames.jpg").write_bytes(b"frames")
    return con, character_refs, bdir


def test_library_is_seeded_from_the_record(library):
    con, lib, bdir = library
    assert lib.sync(con, bdir) == 4 and lib.sync(con, bdir) == 0
    got = {r["path"]: (r["kind"], r["verdict"], r["in_use"], r["version"]) for r in lib.rows(con)}
    assert got["studio/refs/face_main.png"] == ("face_ref", "approved", 1, 1)
    assert got["studio/refs/candidates/face_option_A.png"][1] == "rejected"
    assert got["studio/refs/candidates/face_option_B.png"][1] == "approved"  # the option chosen
    assert got["studio/episodes/EW-20990101-1/v_frames.jpg"][:2] == ("example", "approved")
    assert lib.check(con, bdir) == []


def test_only_the_owner_gives_verdicts_and_identity_never_changes(library, tmp_path):
    con, lib, bdir = library
    lib.sync(con, bdir)
    (tmp_path / "studio" / "refs" / "face_new.png").write_bytes(b"maybe")
    rid = lib.add(con, "studio/refs/face_new.png", "face_ref", "softer light")
    with pytest.raises(ValueError):
        lib.verdict(con, rid, "approved", "yes", "claude")
    lib.verdict(con, rid, "approved", "I like this one", "owner")
    r = con.execute("SELECT * FROM character_refs WHERE ref_id = ?", (rid,)).fetchone()
    assert (r["verdict"], r["version"], r["in_use"]) == ("approved", 2, 0)  # approved, but not Ember's face
    assert "face_new" not in (bdir / "character.yaml").read_text(encoding="utf-8")
    in_use = con.execute("SELECT ref_id FROM character_refs WHERE in_use = 1").fetchone()[0]
    with pytest.raises(ValueError, match="in use"):
        lib.verdict(con, in_use, "rejected", "no", "owner")
    with pytest.raises(ValueError):
        lib.add(con, "data/elsewhere.png", "example", "outside the reference folders")


def test_library_flags_a_changed_file(library, tmp_path):
    con, lib, bdir = library
    lib.sync(con, bdir)
    (tmp_path / "studio" / "refs" / "face_main.png").write_bytes(b"edited face")
    assert [i["check"] for i in lib.check(con, bdir)] == ["reference file changed or missing"]
