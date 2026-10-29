"""Proof that the conveyor's gates hold. Run: python -I -m pytest scripts/studio/test_studio.py -q"""
import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio import bible, cli, db, gates  # noqa: E402


@pytest.fixture
def b():
    return bible.load()


@pytest.fixture
def con(tmp_path):
    return db.connect(tmp_path / "test.db")


@pytest.fixture
def selling(b, monkeypatch):
    """Rules as they will be once the owner turns selling on."""
    monkeypatch.setattr(b["rules"].mix, "product_share_max", 0.4)
    monkeypatch.setattr(b["rules"].mix, "value_share_min", 0.6)
    return b


def planned(con, b, days=3, start="2026-11-02"):
    cli.cmd_plan(con, b, argparse.Namespace(start=start, days=days))
    return [dict(r) for r in con.execute("SELECT * FROM episodes ORDER BY post_date, slot")]


GOOD_PRODUCT = {
    "lines": ["If you live in boots all winter, you need this dress.",
              "Chunky cable knit, a mock neck, and a ribbed waist that keeps it fitted.",
              "The front slit lets you actually walk in it, and it sits right over your boots.",
              "It comes in seven colors. Tap the link to see it."],
    "actions": ["walks toward the camera from the mirror", "close-ups of the knit, neck and waist",
                "one slow step so the slit opens over the boots", "smiling close-up"],
    "caption": "Boot season dress. AI-generated video."}


def test_bible_loads_and_draft_blocks_production(b):
    b["rules"] = b["rules"].model_copy(update={"status": "draft"})
    assert bible.unapproved(b)
    with pytest.raises(bible.BibleError):
        bible.require_approved(b)


def test_character_cannot_be_approved_without_face(b):
    data = b["character"].model_dump()
    data.update(status="approved", approved_by="owner", approved_at="2026-10-26T00:00:00", face_refs=[])
    with pytest.raises(Exception):
        bible.Character.model_validate(data)


def test_approval_must_come_from_owner(b):
    data = b["rules"].model_dump()
    data.update(status="approved", approved_by="claude", approved_at="2026-10-26T00:00:00")
    with pytest.raises(Exception):
        bible.Rules.model_validate(data)


def test_planner_output_obeys_calendar_rules(con, b):
    eps = planned(con, b, days=7)
    assert len(eps) == 21
    assert gates.check_calendar(eps, b) == []
    assert sum(e["pillar"] == "value" for e in eps) / len(eps) >= b["rules"].mix.value_share_min


def test_calendar_catches_broken_rotation(con, b):
    eps = planned(con, b)
    eps[1]["room_id"] = eps[0]["room_id"]
    eps[0]["cta_line"] = eps[1]["cta_line"] = "New one every morning."
    errs = gates.check_calendar(eps, b)
    assert any("same room" in e for e in errs) and any("soft line" in e for e in errs)


def test_good_product_script_passes(con, b, selling):
    ep = next(e for e in planned(con, b) if e["pillar"] == "product" and e["product_id"] == "P01")
    assert gates.check_script(GOOD_PRODUCT, ep, b) == []


@pytest.mark.parametrize("bad_line, expect", [
    ("It's only $52 right now. Tap the link to see it.", "banned pattern"),
    ("I bought it last week. Tap the link to see it.", "banned phrase"),
    ("Perfect with knee-high boots. Tap the link to see it.", "mispronounces"),
    ("It comes in seven colors.", "end with exactly"),
])
def test_bad_scripts_are_rejected(con, b, selling, bad_line, expect):
    ep = next(e for e in planned(con, b) if e["pillar"] == "product" and e["product_id"] == "P01")
    s = json.loads(json.dumps(GOOD_PRODUCT))
    s["lines"][3] = bad_line
    assert any(expect in e for e in gates.check_script(s, ep, b))


def test_word_count_is_enforced(con, b, selling):
    ep = next(e for e in planned(con, b) if e["pillar"] == "product")
    s = json.loads(json.dumps(GOOD_PRODUCT))
    s["lines"] = ["Cable knit.", "Mock neck.", "Ribbed waist.", "Tap the link to see it."]
    assert any("spoken words" in e for e in gates.check_script(s, ep, b))


def test_stage_order_is_locked(con, b):
    ep = planned(con, b)[0]
    with pytest.raises(db.GateError, match="not an allowed step"):
        db.move(con, ep["id"], "GENERATED", "claude", "skip ahead", prompt_text="x", prompt_hash="x",
                video_path="x", model="x")
    with pytest.raises(db.GateError, match="missing"):
        db.move(con, ep["id"], "SCRIPTED", "claude", "no script")


def test_only_owner_with_quote_can_approve(con, b):
    ep = planned(con, b)[0]
    con.execute("UPDATE episodes SET state = 'QA_PASSED', qa_json = ? WHERE id = ?",
                (json.dumps({"passed": True}), ep["id"]))
    with pytest.raises(db.GateError, match="only the owner"):
        db.move(con, ep["id"], "APPROVED", "claude", "looks fine", approval_json=json.dumps({"owner_quote": "ok"}))
    with pytest.raises(db.GateError, match="own words"):
        db.move(con, ep["id"], "APPROVED", "owner", "ok", approval_json=json.dumps({}))
    assert db.move(con, ep["id"], "APPROVED", "owner", "ok",
                   approval_json=json.dumps({"owner_quote": "approved"}))["state"] == "APPROVED"


def test_test_videos_can_never_be_approved(con, b):
    ep = planned(con, b)[0]
    con.execute("UPDATE episodes SET state = 'QA_PASSED', qa_json = ?, test = 1 WHERE id = ?",
                (json.dumps({"passed": True}), ep["id"]))
    with pytest.raises(db.GateError, match="test episode"):
        db.move(con, ep["id"], "APPROVED", "owner", "ok", approval_json=json.dumps({"owner_quote": "yes"}))


def test_posting_requires_the_ai_label(con, b):
    ep = planned(con, b)[0]
    con.execute("UPDATE episodes SET state = 'APPROVED' WHERE id = ?", (ep["id"],))
    db.move(con, ep["id"], "SCHEDULED", "claude", "go", caption="Boot season dress")  # caption text is free
    db.move(con, ep["id"], "SCHEDULED", "claude", "new caption", caption="Boot season.")
    with pytest.raises(db.GateError, match="disclosed as AI"):
        db.move(con, ep["id"], "POSTED", "claude", "live", post_url="https://x")
    assert db.move(con, ep["id"], "POSTED", "claude", "live", post_url="https://x", ai_label_on=True)["state"] == "POSTED"


def test_prompt_comes_only_from_template_and_bible(con, b, selling):
    ep = next(e for e in planned(con, b) if e["pillar"] == "product" and e["product_id"] == "P01")
    ep["outfit_json"] = json.dumps(["boots-black-tall"])
    t1, h1 = gates.build_prompt(ep, GOOD_PRODUCT, b)
    t2, h2 = gates.build_prompt(ep, GOOD_PRODUCT, b)
    assert h1 == h2 and "Photorealistic" in t1 and "caramel-brown cable-knit" in t1
    assert "black leather boots to the knee" in t1


def test_budget_gate(con, b, monkeypatch):
    from studio import production
    monkeypatch.setattr(b["rules"].generation, "max_usd_per_video", 0.5)
    with pytest.raises(db.GateError, match="Budget"):
        production.check_budget(con, b)


def test_bible_approve_round_trip(tmp_path, monkeypatch, con):
    import shutil
    folder = tmp_path / "studio" / "bible"
    shutil.copytree(bible.BIBLE, folder)
    monkeypatch.setattr(bible, "BIBLE", folder)
    cli.cmd_bible_approve(con, None, argparse.Namespace(file="wardrobe", quote="test approval"))
    reloaded = bible.MODELS["wardrobe"].model_validate(
        __import__("yaml").safe_load((folder / "wardrobe.yaml").read_text(encoding="utf-8")))
    assert reloaded.status == "approved" and reloaded.approved_by == "owner"


def test_no_product_posts_until_selling_starts(con, b):
    assert b["rules"].mix.product_share_max == 0
    eps = planned(con, b, days=7)
    assert all(e["pillar"] == "value" and not e["product_id"] for e in eps)
    eps[2].update(pillar="product", product_id="P01")
    assert any("product posts are off" in e for e in gates.check_calendar(eps, b))


def test_products_file_not_needed_while_not_selling(b, selling):
    approved = {"status": "approved", "approved_by": "owner", "approved_at": "2026-10-26T00:00:00"}
    for name in bible.FILES:
        if name != "products":
            b[name] = b[name].model_copy(update=approved)
    with pytest.raises(bible.BibleError, match="products"):
        bible.require_approved(b)  # selling on: products must be approved
    b["rules"].mix.product_share_max = 0
    bible.require_approved(b)       # selling off: products can stay draft


def test_every_post_gets_a_fresh_in_season_outfit(con, b):
    eps = planned(con, b, days=7)
    outfits = [json.loads(e["outfit_json"]) for e in eps]
    assert all(outfits) and len({frozenset(o) for o in outfits}) == len(outfits)
    assert gates.check_outfits(eps, b) == []
    items = {i.id: i for i in b["wardrobe"].items}
    assert all(any(items[o].category in gates.BASE for o in outfit) for outfit in outfits)
    assert not any("puffer-cream" in o for o in outfits)  # winter-only piece, November is fall


def test_outfits_follow_the_season(con, b):
    eps = planned(con, b, days=3, start="2027-01-11")
    items = {i.id: i for i in b["wardrobe"].items}
    worn = [items[o] for e in eps for o in json.loads(e["outfit_json"])]
    assert all("all" in i.season or "winter" in i.season for i in worn)


def test_outfit_planning_is_reproducible(tmp_path, b):
    a = planned(db.connect(tmp_path / "a.db"), b, days=5)
    c = planned(db.connect(tmp_path / "c.db"), b, days=5)
    assert [e["outfit_json"] for e in a] == [e["outfit_json"] for e in c]


def test_calendar_catches_repeated_outfits(con, b):
    eps = planned(con, b, days=3)
    eps[5]["outfit_json"] = eps[0]["outfit_json"]
    errs = gates.check_calendar(eps, b)
    assert any("same outfit" in e for e in errs)
    eps = planned(db.connect(con.execute("PRAGMA database_list").fetchone()[2] + "2"), b, days=3)
    base = sorted(gates.base_pieces(json.loads(eps[0]["outfit_json"]), b))[0]
    eps[2]["outfit_json"] = json.dumps(json.loads(eps[2]["outfit_json"]) + [base])
    assert any("worn again" in e for e in gates.check_calendar(eps, b))


def test_script_cannot_swap_the_planned_outfit(con, b, tmp_path):
    ep = planned(con, b)[0]
    f = tmp_path / "s.json"
    f.write_text(json.dumps({**GOOD_PRODUCT, "outfit": ["sneakers-white"]}), encoding="utf-8")
    with pytest.raises(db.GateError, match="outfit is planned"):
        cli.cmd_script(con, b, argparse.Namespace(episode=ep["id"], file=str(f), actor="claude"))


def test_every_outfit_has_exactly_one_store_piece(con, b):
    eps = planned(con, b, days=7)
    items = {i.id: i for i in b["wardrobe"].items}
    store = {i.id for i in items.values() if i.store_product}
    clothes = {o for o in store if items[o].category != "shoes"}
    assert all(len(set(json.loads(e["outfit_json"])) & clothes) <= 1 and set(json.loads(e["outfit_json"])) & store
               for e in eps)  # one clothing piece (store shoes may be a second piece)
    no_store = json.loads(eps[3]["outfit_json"])
    eps[3]["outfit_json"] = json.dumps([o for o in no_store if o not in store])
    two = json.loads(eps[5]["outfit_json"]) + [sorted(clothes - set(json.loads(eps[5]["outfit_json"])))[0]]
    eps[5]["outfit_json"] = json.dumps(two)
    errs = gates.check_calendar(eps, b)
    assert any(eps[3]["id"] in e and "needs exactly 1" in e for e in errs)
    assert any(eps[5]["id"] in e and "needs exactly 1" in e for e in errs)


def test_store_piece_is_described_exactly_and_its_photo_is_sent(con, b):
    ep = planned(con, b)[0]
    piece = next(i for i in b["wardrobe"].items if i.id in json.loads(ep["outfit_json"]) and i.store_product)
    script = {"lines": ["a"] * 4, "actions": ["b"] * 4}
    text, _ = gates.build_prompt(ep, script, b)
    assert piece.prompt_description in text and piece.name not in text.split("also wears:")[-1]
    assert piece.reference_images[0] in gates.reference_images(ep, b)
    assert len(gates.reference_images(ep, b)) <= b["rules"].generation.max_reference_images


def test_editing_an_approved_file_voids_the_approval(tmp_path, monkeypatch, con):
    import shutil
    folder = tmp_path / "studio" / "bible"
    shutil.copytree(bible.BIBLE, folder)
    shutil.copytree(bible.HUB / "studio" / "refs", tmp_path / "studio" / "refs")
    shutil.copytree(bible.HUB / "assets", tmp_path / "assets", dirs_exist_ok=True,
                    ignore=lambda d, names: [n for n in names if n.endswith((".mp4", ".mov"))])
    monkeypatch.setattr(bible, "BIBLE", folder)
    cli.cmd_bible_approve(con, None, argparse.Namespace(file="wardrobe", quote="test approval"))
    assert bible.load(folder)["wardrobe"].status == "approved"
    path = folder / "wardrobe.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("plain white crew-neck tee", "white tee"), encoding="utf-8")
    w = bible.load(folder)["wardrobe"]
    assert w.status == "draft" and w.changed_since_approval
    path.write_text(path.read_text(encoding="utf-8").replace("# Ember's wardrobe.", "# Ember's closet."), encoding="utf-8")
    path.write_text(path.read_text(encoding="utf-8").replace("white tee", "plain white crew-neck tee"), encoding="utf-8")
    assert bible.load(folder)["wardrobe"].status == "approved"  # comments don't count


def test_outdoor_spots_are_used_and_sunglasses_stay_outside(con, b):
    eps = planned(con, b, days=14)
    outdoor = {r.id for r in b["world"].rooms if r.outdoor}
    shades = {i.id for i in b["wardrobe"].items if i.outdoor_only}
    out_eps = [e for e in eps if e["room_id"] in outdoor]
    assert len(out_eps) >= 7 and {e["room_id"] for e in out_eps} == outdoor
    assert not any(set(json.loads(e["outfit_json"])) & shades for e in eps if e["room_id"] not in outdoor)
    assert any(set(json.loads(e["outfit_json"])) & shades for e in out_eps)
    items = {i.id: i for i in b["wardrobe"].items}
    assert all(any(items[o].category == "outerwear" for o in json.loads(e["outfit_json"])) for e in out_eps)


def test_calendar_catches_sunglasses_indoors_and_no_coat_outside(con, b):
    eps = planned(con, b, days=3)
    outdoor = {r.id for r in b["world"].rooms if r.outdoor}
    items = {i.id: i for i in b["wardrobe"].items}
    inside = next(e for e in eps if e["room_id"] not in outdoor)
    inside["outfit_json"] = json.dumps([o for o in json.loads(inside["outfit_json"]) if not items[o].store_product]
                                       + ["ec-cateye-sunglasses-black"])
    outside = next(e for e in eps if e["room_id"] in outdoor)
    outside["outfit_json"] = json.dumps([o for o in json.loads(outside["outfit_json"]) if items[o].category != "outerwear"])
    errs = gates.check_calendar(eps, b)
    assert any("only worn outdoors" in e for e in errs) and any("needs a coat" in e for e in errs)


def test_trial_copy_is_test_and_leaves_original(con, b):
    ep = planned(con, b)[0]
    con.execute("UPDATE episodes SET state = 'SCRIPTED', script_json = ? WHERE id = ?",
                (json.dumps(GOOD_PRODUCT), ep["id"]))
    t = db.trial_copy(con, ep["id"], "claude", "test")
    assert t["id"] == ep["id"] + "-T1" and t["test"] == 1 and db.get(con, ep["id"])["state"] == "SCRIPTED"
    con.execute("UPDATE episodes SET state = 'QA_PASSED', qa_json = ? WHERE id = ?", (json.dumps({"passed": True}), t["id"]))
    with pytest.raises(db.GateError, match="test episode"):
        db.move(con, t["id"], "APPROVED", "owner", "ok", approval_json=json.dumps({"owner_quote": "yes"}))
    with pytest.raises(db.GateError, match="trials start"):
        db.trial_copy(con, t["id"], "claude", "again")


def test_trial_models_obey_the_video_cap(con, b):
    from studio import production
    kling = production.TRIAL_MODELS["kwaivgi/kling-v3.0-std"]["usd_per_s"] * b["rules"].generation.duration_s
    cap = b["rules"].generation.max_usd_per_video
    if cap is not None and kling > cap:
        with pytest.raises(db.GateError, match="Budget"):
            production.check_budget(con, b, round(kling, 2))


def test_first_frame_prompt_uses_face_place_and_store_piece(con, b):
    ep = next(e for e in planned(con, b) if gates.is_outdoor(e, b))
    text, images = gates.build_first_frame_prompt(ep, {"actions": ["steps out of the front door"]}, b)
    piece = next(i for i in b["wardrobe"].items if i.id in json.loads(ep["outfit_json"]) and i.store_product)
    assert images[0] == b["character"].face_refs[0] and images[2] == piece.reference_images[0]
    assert piece.prompt_description in text and "steps out of the front door" in text and "no logos" in text


def test_owner_cap_only_with_owner_words(con, b, monkeypatch):
    from studio import production
    args = argparse.Namespace(episode="x", model="kwaivgi/kling-v3.0-std", frame_only=False, owner_cap=1.76, owner_day_cap=None, no_face_ref=False,
                              quote=None, actor="claude")
    monkeypatch.setattr(db, "get", lambda c, i: {"id": "x", "script_json": json.dumps(GOOD_PRODUCT), "cta_type": "none",
                                                 "cta_line": None, "product_id": None})
    monkeypatch.setattr(gates, "check_script", lambda s, e, bb: [])
    monkeypatch.setattr(bible, "require_approved", lambda bb: None)  # the live bible may have a file back in draft
    with pytest.raises(db.GateError, match="owner's own words"):
        cli.cmd_trial(con, b, args)
    assert production.check_budget(con, b, 1.76, 1.76) == 1.76


def test_owner_accept_and_promote(con, b, tmp_path, monkeypatch):
    ep = planned(con, b)[0]
    con.execute("UPDATE episodes SET state = 'SCRIPTED', script_json = ? WHERE id = ?", (json.dumps(GOOD_PRODUCT), ep["id"]))
    t = db.trial_copy(con, ep["id"], "claude", "x")
    video = tmp_path / "v.mp4"; video.write_bytes(b"x")
    monkeypatch.setattr(db, "HUB", tmp_path)
    con.execute("UPDATE episodes SET state = 'QA_FAILED', video_path = 'v.mp4', prompt_text = 'p', prompt_hash = 'h', "
                "model = 'm', qa_json = ? WHERE id = ?", (json.dumps({"passed": False}), t["id"]))
    with pytest.raises(db.GateError, match="owner-only"):
        db.promote_trial(con, t["id"], "claude", "go")
    real = db.promote_trial(con, t["id"], "owner", "post it")
    assert real["state"] == "GENERATED" and real["video_path"] == "v.mp4" and real["test"] == 0
    con.execute("UPDATE episodes SET state = 'QA_FAILED', qa_json = ? WHERE id = ?", (json.dumps({"passed": False}), ep["id"]))
    with pytest.raises(db.GateError, match="only the owner"):
        db.move(con, ep["id"], "QA_PASSED", "claude", "fine", qa_json=json.dumps({"passed": True}))
    cli.cmd_accept(con, b, argparse.Namespace(episode=ep["id"], quote="its fine", actor="owner"))
    assert db.get(con, ep["id"])["state"] == "QA_PASSED"


def test_publish_gates(con, b):
    from studio import publishing
    ep = planned(con, b)[0]
    with pytest.raises(db.GateError, match="only approved, scheduled"):
        publishing.publish(con, db.get(con, ep["id"]), b, "draft", "claude", None)
    con.execute("UPDATE episodes SET state = 'SCHEDULED' WHERE id = ?", (ep["id"],))
    with pytest.raises(db.GateError, match="owner only"):
        publishing.publish(con, db.get(con, ep["id"]), b, "scheduled", "claude", None)
    with pytest.raises(db.GateError, match="can't set"):
        db.note(con, ep["id"], "x", state="POSTED")
    local, utc = publishing.slot_time({"post_date": "2026-11-02", "slot": "12:30"}, b)
    assert utc == "2026-11-02T17:30:00Z"  # 12:30 Eastern (EST) = 17:30 UTC


def test_night_out_on_fri_sat_evenings_with_night_outfits(con, b):
    eps = planned(con, b, days=7, start="2026-11-09")
    items = {i.id: i for i in b["wardrobe"].items}
    night = [e for e in eps if e["series_id"] == "night-out"]
    assert {(e["post_date"], e["slot"]) for e in night} == {("2026-11-13", "19:30"), ("2026-11-14", "19:30")}
    for e in eps:
        occ = gates.occasion_of(e, b)
        assert all(occ in items[o].occasion for o in json.loads(e["outfit_json"]))
    assert not any(items[o].occasion == ["night"] for e in eps if e["series_id"] != "night-out"
                   for o in json.loads(e["outfit_json"]))
    e = night[0]
    e["outfit_json"] = json.dumps(json.loads(e["outfit_json"]) + ["sneakers-white"])
    assert any("isn't a night piece" in x for x in gates.check_outfits([e], b))


def test_shoe_rotation_and_store_shoes(con, b):
    eps = planned(con, b, days=14, start="2026-11-09")
    items = {i.id: i for i in b["wardrobe"].items}
    shoes = [next(o for o in json.loads(e["outfit_json"]) if items[o].category == "shoes") for e in eps]
    assert all(a != c for a, c in zip(shoes, shoes[1:]))
    for week in (eps[:21], eps[21:]):
        ws = [next(o for o in json.loads(e["outfit_json"]) if items[o].category == "shoes") for e in week]
        assert max(ws.count(s) for s in set(ws)) <= 3
    for e in eps:
        o = json.loads(e["outfit_json"])
        if gates.is_outdoor(e, b):
            assert not any(items[x].open_toe for x in o)
    assert gates.check_calendar(eps, b) == []


# --- Phase D: approvals bound to the video and caption ------------------------------------------------------------

def _approved_episode(con, b, tmp_path, monkeypatch):
    from studio import checks, publishing
    monkeypatch.setattr(cli, "HUB", tmp_path)
    monkeypatch.setattr(publishing, "HUB", tmp_path)
    monkeypatch.setattr(checks, "availability", lambda handles, *a, **k: [])
    ep = planned(con, b)[0]
    video = tmp_path / "v.mp4"
    video.write_bytes(b"approved video")
    con.execute("UPDATE episodes SET state = 'QA_PASSED', video_path = 'v.mp4', qa_json = ? WHERE id = ?",
                (json.dumps({"passed": True}), ep["id"]))
    cli.cmd_owner(con, b, argparse.Namespace(episode=ep["id"], quote="approved", actor="owner"), "APPROVED")
    return ep["id"], video


def test_approval_names_the_video_and_schedule_the_caption(con, b, tmp_path, monkeypatch):
    from studio import content
    ep_id, video = _approved_episode(con, b, tmp_path, monkeypatch)
    approval = json.loads(db.get(con, ep_id)["approval_json"])
    assert approval["asset_sha256"] == content.sha256_file(video)
    with pytest.raises(db.GateError, match="price"):
        cli.cmd_schedule(con, b, argparse.Namespace(episode=ep_id, caption="Only $20! #aigenerated", actor="claude"))
    cli.cmd_schedule(con, b, argparse.Namespace(episode=ep_id, caption="Errand day. #aigenerated", actor="claude"))
    assert json.loads(db.get(con, ep_id)["approval_json"])["caption_sha256"] == content.sha256_text("Errand day. #aigenerated")


def test_publishing_refuses_a_changed_video(con, b, tmp_path, monkeypatch):
    from studio import publishing
    ep_id, video = _approved_episode(con, b, tmp_path, monkeypatch)
    cli.cmd_schedule(con, b, argparse.Namespace(episode=ep_id, caption="Errand day. #aigenerated", actor="claude"))
    publishing.release_checks(con, db.get(con, ep_id), b)  # unchanged: passes
    video.write_bytes(b"re-rendered")
    with pytest.raises(db.GateError, match="media_changed"):
        publishing.release_checks(con, db.get(con, ep_id), b)
    con.execute("UPDATE episodes SET caption = 'Edited. #aigenerated' WHERE id = ?", (ep_id,))
    with pytest.raises(db.GateError, match="caption_changed"):
        publishing.release_checks(con, db.get(con, ep_id), b)


def test_resend_draft_is_owner_only_and_checks_the_file(con, b, tmp_path, monkeypatch):
    from studio import publishing
    ep_id, video = _approved_episode(con, b, tmp_path, monkeypatch)
    cli.cmd_schedule(con, b, argparse.Namespace(episode=ep_id, caption="Errand day. #aigenerated", actor="claude"))
    sent = []
    monkeypatch.setattr(publishing, "account_id", lambda: "acc")
    monkeypatch.setattr(publishing, "_send", lambda c, e, body, key, *a: sent.append(key) or {"_id": "pz2"})
    with pytest.raises(db.GateError, match="hasn't been sent"):
        publishing.publish(con, db.get(con, ep_id), b, "draft", "owner", "send it", now=True, resend=True)
    db.note(con, ep_id, "x", postzen_post_id="pz1", publish_mode="draft", platform_status="published")
    with pytest.raises(db.GateError, match="already with PostZen"):
        publishing.publish(con, db.get(con, ep_id), b, "draft", "claude", None, now=True)
    with pytest.raises(db.GateError, match="owner only"):
        publishing.publish(con, db.get(con, ep_id), b, "draft", "claude", None, now=True, resend=True)
    with pytest.raises(db.GateError, match="goes with --now"):
        publishing.publish(con, db.get(con, ep_id), b, "draft", "owner", "send it", resend=True)
    video.write_bytes(b"re-rendered")
    with pytest.raises(db.GateError, match="media_changed"):
        publishing.publish(con, db.get(con, ep_id), b, "draft", "owner", "send it", now=True, resend=True)
    assert not sent
    video.write_bytes(b"approved video")
    ep = publishing.publish(con, db.get(con, ep_id), b, "draft", "owner", "send it", now=True, resend=True)
    assert ep["postzen_post_id"] == "pz2" and sent[0].startswith(f"{ep_id}-draft-resend-")


def test_old_approvals_are_bound_only_to_unchanged_files(con, b, tmp_path, monkeypatch):
    import os
    monkeypatch.setattr(cli, "HUB", tmp_path)
    eps = planned(con, b)[:2]
    for i, ep in enumerate(eps):
        (tmp_path / f"v{i}.mp4").write_bytes(b"v")
        con.execute("UPDATE episodes SET state = 'APPROVED', video_path = ?, approval_json = ? WHERE id = ?",
                    (f"v{i}.mp4", json.dumps({"owner_quote": "ok", "at": "2026-10-26T20:00:00"}), ep["id"]))
    os.utime(tmp_path / "v0.mp4", (1761500000, 1761500000))  # 2025-10-26: before the approval
    con.commit()
    cli.cmd_bind_approvals(con, b, argparse.Namespace(actor="claude"))  # v1 was written just now: after the approval
    assert json.loads(db.get(con, eps[0]["id"])["approval_json"]).get("asset_sha256")
    assert not json.loads(db.get(con, eps[1]["id"])["approval_json"]).get("asset_sha256")


# --- Phase D item 5: approvals cover reference images and prompt templates ------------------------------------------

def _bible_copy(tmp_path, monkeypatch):
    import shutil
    folder = tmp_path / "studio" / "bible"
    shutil.copytree(bible.BIBLE, folder)
    (folder / bible.LOCK).unlink(missing_ok=True)
    shutil.copytree(bible.HUB / "studio" / "refs", tmp_path / "studio" / "refs")
    shutil.copytree(bible.HUB / "assets", tmp_path / "assets", dirs_exist_ok=True,
                    ignore=lambda d, names: [n for n in names if n.endswith((".mp4", ".mov"))])
    shutil.copytree(bible.HUB / "studio" / "templates", tmp_path / "studio" / "templates")
    (tmp_path / "scripts").mkdir()
    shutil.copy2(bible.HUB / "scripts" / "prompt_style.py", tmp_path / "scripts" / "prompt_style.py")
    monkeypatch.setattr(bible, "BIBLE", folder)
    monkeypatch.setattr(cli, "HUB", tmp_path)
    return folder


def test_a_changed_reference_image_voids_the_approval(tmp_path, monkeypatch, con):
    folder = _bible_copy(tmp_path, monkeypatch)
    cli.cmd_bible_approve(con, None, argparse.Namespace(file="character", quote="test approval"))
    c = bible.load(folder)["character"]
    assert c.status == "approved" and c.assets_locked and not c.changed_assets
    (tmp_path / "studio" / "refs" / "face_main.png").write_bytes(b"a different face")
    c = bible.load(folder)["character"]
    assert c.status == "draft" and c.changed_assets == ["studio/refs/face_main.png"]


def test_changed_templates_block_production_until_approved(tmp_path, monkeypatch, con, b):
    _bible_copy(tmp_path, monkeypatch)
    cli.cmd_bible_approve(con, None, argparse.Namespace(file="templates", quote="the templates are fine"))
    assert bible.template_status() == {"locked": True, "changed": []}
    tpl = tmp_path / "studio" / "templates" / "video_prompt.j2"
    tpl.write_text(tpl.read_text(encoding="utf-8") + "\nextra line", encoding="utf-8")
    assert bible.template_status()["changed"] == ["studio/templates/video_prompt.j2"]
    with pytest.raises(bible.BibleError, match="templates"):
        bible.require_approved(b)


def test_bible_lock_only_binds_files_older_than_the_approval(tmp_path, monkeypatch, con):
    import os
    folder = _bible_copy(tmp_path, monkeypatch)
    room = next(p for p in bible.asset_paths(__import__("yaml").safe_load((folder / "world.yaml").read_text(encoding="utf-8"))))
    os.utime(tmp_path / room, (4102444800, 4102444800))  # 2100: newer than the world approval
    cli.cmd_bible_lock(con, bible.load(folder), argparse.Namespace())
    lock = bible.read_lock(folder)
    assert "character" in lock and "templates" in lock and "world" not in lock
    assert not bible.load(folder)["world"].assets_locked


def test_higgsfield_downloads_are_cleaned_before_qa(tmp_path):
    import subprocess
    from studio import production
    src = tmp_path / "EW-1_a1_reference-to-video_480p.mp4"
    subprocess.run([production.vp.FF, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=red:s=480x854:r=24:d=1",
                    "-f", "lavfi", "-i", "sine=f=440:sample_rate=32000:d=1", "-shortest", "-c:v", "libx264", str(src)],
                   check=True)
    out = production.clean_copy(src)
    assert out.name == "EW-1_a1_reference-to-video_480p_clean.mp4" and src.exists()
    info = subprocess.run([production.vp.FF, "-hide_banner", "-i", str(out)], capture_output=True, text=True).stderr
    assert "480x854" in info and "44100 Hz" in info and "h264 (High)" in info
    assert out.read_bytes().find(b"moov") < out.read_bytes().find(b"mdat")  # index first (faststart)
