"""Ember Studio command line: the only way content moves. See studio/README.md.

  python scripts/studio/cli.py validate                         check the bible and the calendar
  python scripts/studio/cli.py plan --start 2026-11-02 --days 7  fill posting slots (PLANNED)
  python scripts/studio/cli.py script EP --file script.json      set the script; rejected unless every rule passes
  python scripts/studio/cli.py generate EP [--test]              make the video (bible approved, or --test)
  python scripts/studio/cli.py qa EP                              machine checks -> QA_PASSED / QA_FAILED
  python scripts/studio/cli.py approve EP --quote "owner's words" (owner only)
  python scripts/studio/cli.py reject EP --quote "owner's words"  (owner only)
  python scripts/studio/cli.py schedule EP --caption "..."        (again to change the caption)
  python scripts/studio/cli.py reschedule EP=2026-10-27@12:30 ... --reason "..."  (whole calendar re-checked)
  python scripts/studio/cli.py posted EP --url https://...
  python scripts/studio/cli.py board                              where every episode is
  python scripts/studio/cli.py bind-approvals                     one-time (Phase D): bind older approvals to their file
  python scripts/studio/cli.py bible-lock                         one-time (Phase D): lock approved images + templates
  python scripts/studio/cli.py refs list | sync | add PATH --kind example --note "..." | verdict N approved --quote "..."
  python scripts/studio/cli.py bible-approve templates --quote "..."  owner approves changed prompt templates

Approvals are bound to the media (Phase D): `approve` stores the video's sha256 and `schedule` the caption's (after
the shared caption rules in checks.py pass); publishing re-hashes both and refuses anything changed since.
  python scripts/studio/cli.py bible-approve FILE --quote "owner's words"
"""
import argparse
import datetime as dt
import json
import re
import sys
from itertools import cycle
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio import bible, checks, content, db, gates  # noqa: E402

HUB = Path(__file__).resolve().parents[2]


def cmd_validate(con, b, args):
    eps = [dict(r) for r in con.execute("SELECT * FROM episodes WHERE test = 0 ORDER BY post_date, slot")]  # trials aren't posts
    errs = gates.check_calendar(eps, b)
    draft = [n + (" (changed since approval" + (f": {', '.join(b[n].changed_assets)}" if b[n].changed_assets else "") + ")"
                  if b[n].changed_since_approval else "") for n in bible.unapproved(b)]
    unlocked = [n for n in bible.FILES if b[n].status == "approved" and not b[n].assets_locked]
    tpl = bible.template_status()
    print("Bible: OK (draft: " + (", ".join(draft) or "none") + ")")
    print("Images/templates locked to the approval: " + ("files " + ", ".join(unlocked) + " not locked yet; " if unlocked else "all approved files; ")
          + ("templates CHANGED: " + ", ".join(tpl["changed"]) if tpl["changed"] else "templates locked" if tpl["locked"] else "templates not locked yet"))
    print("Calendar: " + ("OK" if not errs else "\n  " + "\n  ".join(errs)))
    return 1 if errs else 0


def cmd_plan(con, b, args):
    r = b["rules"]
    start = dt.date.fromisoformat(args.start)
    value = [s for s in b["series"].items if s.pillar == "value" and not s.weekdays]  # the rotation
    pinned = [s for s in b["series"].items if s.pillar == "value" and s.weekdays]   # e.g. Night out, Fri/Sat 19:30
    # owner 2026-10-26: audience first; product posts only once rules.mix.product_share_max is raised above 0
    product_series = [s for s in b["series"].items if s.pillar == "product"] if bible.selling(b) else []
    products = cycle([p.id for p in b["products"].items])
    value_cycle = cycle(value)
    soft = cycle(r.cta.soft_lines)
    counters = {s.id: con.execute("SELECT COUNT(*) FROM episodes WHERE series_id = ?", (s.id,)).fetchone()[0]
                for s in b["series"].items}
    recent = [dict(x) for x in con.execute("SELECT * FROM episodes WHERE post_date < ? AND test = 0 ORDER BY post_date, slot",
                                           (args.start,))]
    new = []
    slots = r.posting.slots[: r.posting.max_posts_per_day]
    for d in range(args.days):
        day = (start + dt.timedelta(days=d)).isoformat()
        for i, slot in enumerate(slots):
            if con.execute("SELECT 1 FROM episodes WHERE post_date = ? AND slot = ? AND test = 0", (day, slot)).fetchone():
                continue
            # one product post per day at most (only while selling); the rest are value posts
            weekday = dt.date.fromisoformat(day).strftime("%a")
            pin = next((p for p in pinned if weekday in p.weekdays and (not p.slots or slot in p.slots)), None)
            s = pin or (product_series[0] if (product_series and i == len(slots) - 1) else next(value_cycle))
            last = (recent + new)[-1] if (recent + new) else None
            k = counters[s.id] % len(s.rooms)  # rotate through the series' rooms, skipping the previous post's
            room = next((x for x in s.rooms[k:] + s.rooms[:k] if not last or x != last["room_id"]), s.rooms[0])
            product = next(products) if s.pillar == "product" else None
            window = (recent + new)[-(r.cta.window_posts - 1):] if r.cta.window_posts > 1 else []
            cta_line = None
            if s.cta == "soft" and sum(1 for e in window if e.get("cta_line")) < r.cta.max_soft_cta_per_window:
                cta_line = next(soft)
            counters[s.id] += 1
            name = next((p.name for p in b["products"].items if p.id == product), "")
            ep = {"id": f"EW-{day.replace('-', '')}-{i + 1}", "series_id": s.id, "ep_no": counters[s.id],
                  "pillar": s.pillar, "title": s.episode_title.format(n=counters[s.id], topic="TBD", product=name),
                  "post_date": day, "slot": slot, "room_id": room, "product_id": product,
                  "cta_type": "product" if s.pillar == "product" else s.cta, "cta_line": cta_line}
            ep["outfit_json"] = json.dumps(gates.pick_outfit(ep, recent + new, b))
            new.append(ep)
    errs = gates.check_calendar(recent + new, b)
    if errs:
        raise db.GateError("Plan breaks the rules, nothing saved:\n  " + "\n  ".join(errs))
    for ep in new:
        con.execute("INSERT INTO episodes (id, series_id, ep_no, pillar, title, post_date, slot, room_id, product_id,"
                    " outfit_json, cta_type, cta_line, state, created_at, updated_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (ep["id"], ep["series_id"], ep["ep_no"], ep["pillar"], ep["title"], ep["post_date"], ep["slot"],
                     ep["room_id"], ep["product_id"], ep["outfit_json"], ep["cta_type"], ep["cta_line"], "PLANNED",
                     db.now(), db.now()))
        con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                    (ep["id"], None, "PLANNED", "studio", "planned", db.now()))
    con.commit()
    print(f"Planned {len(new)} episodes")
    for ep in new:
        print(f"  {ep['id']} {ep['slot']} {ep['pillar']:7} {ep['title']} | {ep['room_id']} | "
              f"{ep['product_id'] or '-'} | {ep['cta_line'] or ep['cta_type']}\n      wears: "
              + ", ".join(json.loads(ep["outfit_json"])))
    return 0


def cmd_script(con, b, args):
    ep = db.get(con, args.episode)
    script = json.loads(Path(args.file).read_text(encoding="utf-8"))
    errs = gates.check_script(script, ep, b)
    planned = json.loads(ep["outfit_json"] or "[]")
    if "outfit" in script and script["outfit"] != planned:  # the planner picks outfits; scripts can't swap them
        errs.append(f"the outfit is planned ({planned}); drop 'outfit' from the script or match it exactly")
    if errs:
        raise db.GateError(f"{ep['id']}: script rejected:\n  " + "\n  ".join(errs))
    db.move(con, ep["id"], "SCRIPTED", args.actor, "script set",
            script_json=json.dumps(script, ensure_ascii=False))
    print(f"{ep['id']}: SCRIPTED")
    return 0


def cmd_generate(con, b, args):
    from studio import production
    if not args.test:
        bible.require_approved(b)
    elif not bible.unapproved(b):
        raise db.GateError("The bible is fully approved: generate without --test")
    ep = db.get(con, args.episode)
    if ep["state"] not in ("SCRIPTED", "QA_FAILED"):
        raise db.GateError(f"{ep['id']} is {ep['state']}; only SCRIPTED or QA_FAILED episodes can be generated")
    errs = gates.check_script(json.loads(ep["script_json"]), ep, b)  # rules may have changed since scripting
    if errs:
        raise db.GateError(f"{ep['id']}: script no longer passes the rules:\n  " + "\n  ".join(errs))
    ep = production.generate(con, ep, b, args.test)
    print(f"{ep['id']}: GENERATED {ep['video_path']} (total ${ep['cost_usd']:.2f})")
    return 0


def cmd_trial(con, b, args):
    """Try another video model on a copy of a scripted episode. The copy is a test episode: same gates and caps, but
    its video can never be approved for posting. --frame-only makes just the opening still (frame-only models)."""
    from studio import production
    bible.require_approved(b)
    trial = production.TRIAL_MODELS.get(args.model)
    if not trial:
        raise db.GateError(f"Unknown trial model {args.model}; known: {', '.join(production.TRIAL_MODELS)}")
    src = db.get(con, args.episode)
    errs = gates.check_script(json.loads(src["script_json"] or "{}"), src, b)
    if errs:
        raise db.GateError(f"{src['id']}: script no longer passes the rules:\n  " + "\n  ".join(errs))
    if args.frame_only:
        if not trial["frames_only"]:
            raise db.GateError(f"{args.model} takes reference images; there is no first frame to make")
        out = production.EPISODES / src["id"] / f"{src['id']}_first_frame_preview.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        cost = production.first_frame(src, json.loads(src["script_json"]), b, out)
        con.execute("INSERT INTO spend (episode_id, usd, at) VALUES (?,?,?)", (src["id"], cost, db.now()))
        con.commit()
        print(f"{src['id']}: first frame {out.relative_to(production.HUB)} (${cost:.3f}); stage unchanged")
        return 0
    cap, day_cap = args.owner_cap, args.owner_day_cap
    if (cap is not None or day_cap is not None) and (args.actor != "owner" or not args.quote):
        # one-off limits only in the owner's own words
        raise db.GateError("--owner-cap / --owner-day-cap need --actor owner and the owner's own words in --quote")
    production.check_budget(con, b, round(trial["usd_per_s"] * b["rules"].generation.duration_s, 2), cap, day_cap)
    reason = f"model trial {args.model}" + (" without face reference" if args.no_face_ref else "") + (f"; one-off caps video ${cap} day ${day_cap} (owner: {args.quote})"
                                            if args.quote else "")
    ep = db.trial_copy(con, src["id"], args.actor, reason)
    preview = production.EPISODES / src["id"] / f"{src['id']}_first_frame_preview.png"
    ep = production.generate(con, ep, b, True, trial_model=args.model, video_cap=cap, day_cap=day_cap,
                             face_ref=not args.no_face_ref,
                             frame=preview if preview.exists() and trial["frames_only"] else None)
    print(f"{ep['id']}: GENERATED (TEST, never approvable) {ep['video_path']} (total ${ep['cost_usd']:.2f})")
    return 0


def cmd_qa(con, b, args):
    from studio import production
    ep = db.get(con, args.episode)
    if ep["state"] != "GENERATED":
        raise db.GateError(f"{ep['id']} is {ep['state']}; QA runs on GENERATED episodes")
    ep = production.qa(con, ep, b)
    print(f"{ep['id']}: {ep['state']}")
    for c in json.loads(ep["qa_json"])["checks"]:
        print(f"  {'PASS' if c['passed'] else 'FAIL'}  {c['check']}  {c['detail'] if not c['passed'] else ''}")
    return 0 if ep["state"] == "QA_PASSED" else 1


def cmd_promote(con, b, args):
    ep = db.promote_trial(con, args.trial, args.actor, args.quote)
    print(f"{ep['id']}: GENERATED from {args.trial} ({ep['video_path']}); run qa next")
    return 0


def cmd_accept(con, b, args):
    """Owner listened to a video that failed QA and accepts it anyway; the machine result is kept alongside."""
    ep = db.get(con, args.episode)
    if ep["state"] != "QA_FAILED":
        raise db.GateError(f"{ep['id']} is {ep['state']}; accept is for QA_FAILED episodes")
    qa = json.loads(ep["qa_json"])
    qa.update(passed=True, owner_accepted={"quote": args.quote, "at": db.now()})
    ep = db.move(con, ep["id"], "QA_PASSED", args.actor, f"owner accepted after QA failed: {args.quote}",
                 qa_json=json.dumps(qa, ensure_ascii=False),
                 approval_json=json.dumps({"owner_quote": args.quote}, ensure_ascii=False))
    print(f"{ep['id']}: QA_PASSED (owner accepted)")
    return 0


def _video_sha(ep):
    f = HUB / (ep["video_path"] or "").replace("\\", "/")
    return content.sha256_file(f) if ep["video_path"] and f.exists() else None


def cmd_owner(con, b, args, to):
    approval = {"owner_quote": args.quote, "at": db.now()}
    if to == "APPROVED":  # Phase D: the approval names the exact video file; publishing checks it again
        digest = _video_sha(db.get(con, args.episode))
        if not digest:
            raise db.GateError(f"{args.episode}: no video file to approve")
        approval.update(asset_sha256=digest)
    ep = db.move(con, args.episode, to, args.actor, f"owner: {args.quote}",
                 approval_json=json.dumps(approval, ensure_ascii=False))
    print(f"{ep['id']}: {ep['state']}")
    return 0


def cmd_schedule(con, b, args):
    """The caption is checked with the shared rules and its sha256 is added to the approval: from here on a changed
    caption (or video) can't go out under this approval."""
    ep = db.get(con, args.episode)
    cap = content.sha256_text(args.caption)
    content.ensure_schema(con)  # the content tables live in the same studio.db
    blocking = checks.unresolved(checks.text_findings(args.caption), checks.overrides(con, f"TT-{ep['id']}"),
                                 _video_sha(ep), cap)
    if blocking:
        raise db.GateError(f"{ep['id']}: caption refused: {checks.describe(blocking)}")
    approval = json.loads(ep["approval_json"] or "{}")
    approval.update(caption_sha256=cap, caption_bound_at=db.now())
    ep = db.move(con, args.episode, "SCHEDULED", args.actor, "scheduled", caption=args.caption,
                 approval_json=json.dumps(approval, ensure_ascii=False))
    print(f"{ep['id']}: SCHEDULED for {ep['post_date']} {ep['slot']}")
    return 0


def cmd_reschedule(con, b, args):
    moves = {}
    for m in args.moves:
        ep_id, _, when = m.partition("=")
        day, _, slot = when.partition("@")
        dt.date.fromisoformat(day)
        if slot not in b["rules"].posting.slots:
            raise db.GateError(f"{slot!r} isn't a posting slot ({', '.join(b['rules'].posting.slots)})")
        moves[ep_id] = (day, slot)
    db.reschedule(con, moves, args.actor, args.reason, lambda eps: gates.check_calendar(eps, b))
    for ep_id, (day, slot) in moves.items():
        print(f"{ep_id}: {day} {slot}")
    return 0


def cmd_set_line(con, b, args):
    ep = db.set_cta_line(con, args.episode, args.line, b["rules"].cta.soft_lines, "retired line replaced")
    print(f"{ep['id']}: follow line now {ep['cta_line']!r}; re-script it")
    return 0


def cmd_publish(con, b, args):
    from studio import publishing
    ep = publishing.publish(con, db.get(con, args.episode), b, args.mode, args.actor, args.quote,
                            now=args.now, existing=args.existing, resend=args.resend)
    when = "now" if args.now else f"for {ep['post_date']} {ep['slot']}"
    print(f"{ep['id']}: sent to PostZen as {ep['publish_mode']} {when} "
          f"({ep['postzen_post_id']}); TikTok status {ep['platform_status']}")
    return 0


def cmd_sync(con, b, args):
    from studio import publishing
    for line in publishing.sync(con, b):
        print(" ", line)
    print(f"Dashboard data written to {publishing.OUT.relative_to(publishing.HUB)}")
    return 0


def cmd_posted(con, b, args):
    ep = db.move(con, args.episode, "POSTED", args.actor, "posted; disclosed as AI",
                 post_url=args.url, ai_label_on=args.ai_label_on)
    print(f"{ep['id']}: POSTED")
    return 0


def cmd_bind_approvals(con, b, args):
    """Phase D, one-time: approvals given before approvals named the file get the file's sha256, but only when the
    file has not been modified since the approval (file mtime earlier than the approval time). Others stay unbound
    and are held at publishing until the owner approves the file again. Already-scheduled captions are bound too."""
    bound, held = [], []
    for ep in con.execute("SELECT * FROM episodes WHERE state IN ('APPROVED', 'SCHEDULED') AND test = 0"):
        approval = json.loads(ep["approval_json"] or "{}")
        if approval.get("asset_sha256") or not approval.get("owner_quote"):
            continue
        f = HUB / (ep["video_path"] or "").replace("\\", "/")
        at = approval.get("at")
        if not (ep["video_path"] and f.exists() and at
                and dt.datetime.fromtimestamp(f.stat().st_mtime) <= dt.datetime.fromisoformat(at)):
            held.append(ep["id"])
            continue
        approval.update(asset_sha256=content.sha256_file(f), bound_at=db.now(),
                        bound_note="bound in Phase D to the file approved earlier (unchanged since the approval)")
        if ep["state"] == "SCHEDULED" and ep["caption"]:
            approval.update(caption_sha256=content.sha256_text(ep["caption"]), caption_bound_at=db.now())
        con.execute("UPDATE episodes SET approval_json = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(approval, ensure_ascii=False), db.now(), ep["id"]))
        con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                    (ep["id"], ep["state"], ep["state"], args.actor, "approval bound to the approved file (Phase D)", db.now()))
        bound.append(ep["id"])
    con.commit()
    print(f"bound {len(bound)}: {', '.join(bound) or '-'}")
    print(f"held (file changed after approval, or missing): {', '.join(held) or '-'}")
    return 0


def cmd_refs(con, b, args):
    """Ember's references library (character_refs.py): records face reference versions and approved/rejected examples;
    it never changes character.yaml."""
    from studio import character_refs as lib
    content.ensure_schema(con)
    if args.action == "sync":
        print(f"{lib.sync(con)} new entries")
    elif args.action == "add":
        print(f"added as candidate #{lib.add(con, args.target, args.kind, args.note, args.actor)}")
    elif args.action == "verdict":
        lib.verdict(con, int(args.target), args.value, args.quote, args.actor)
        print(f"#{args.target}: {args.value}")
    lib.sync(con)
    for r in lib.rows(con):
        print(f"#{r['ref_id']:<3} {r['kind']:8} {'v' + str(r['version']) if r['version'] else '  ':3} {r['verdict']:9}"
              f"{' IN USE' if r['in_use'] else '       '} {r['path']}  ({r['source']}{'' if r['file_ok'] else '; FILE CHANGED'})")
    return 0


def cmd_board(con, b, args):
    rows = con.execute("SELECT id, post_date, slot, pillar, title, state, test, cost_usd FROM episodes "
                       "ORDER BY post_date, slot").fetchall()
    for r in rows:
        print(f"{r['id']}  {r['post_date']} {r['slot']}  {r['state']:9} {'TEST ' if r['test'] else ''}"
              f"{r['pillar']:7} ${r['cost_usd']:.2f}  {r['title']}")
    print(f"{len(rows)} episodes")
    return 0


def _lock_entry(paths, approved_hash, quote, basis):
    return {**bible.assets_lock(HUB, paths), "approved_hash": approved_hash, "at": db.now(), "quote": quote,
            "basis": basis}


def cmd_bible_lock(con, b, args):
    """Phase D, one-time: lock the reference images of every approved bible file, and the prompt templates, as they
    are now, but only where every file is older than the approval it is bound to (unchanged since). Anything newer stays
    unlocked and needs the owner's `bible-approve` again."""
    lock = bible.read_lock()
    for name in bible.FILES:
        data = yaml.safe_load((bible.BIBLE / f"{name}.yaml").read_text(encoding="utf-8"))
        if name in lock or b[name].status != "approved":
            print(f"{name}: {'already locked' if name in lock else 'not approved'}")
            continue
        paths = bible.asset_paths(data)
        at = dt.datetime.fromisoformat(data["approved_at"])
        late = [p for p in paths if not (HUB / p).exists() or dt.datetime.fromtimestamp((HUB / p).stat().st_mtime) > at]
        if late:
            print(f"{name}: NOT locked; changed after the approval or missing: {', '.join(late)}")
            continue
        lock[name] = _lock_entry(paths, data["approved_hash"], None,
                                 f"bound in Phase D to the images as approved on {data['approved_at']} (unchanged since)")
        print(f"{name}: locked ({len(paths)} images)")
    if "templates" not in lock:
        last = max(dt.datetime.fromisoformat(b[n].approved_at) for n in bible.FILES if b[n].status == "approved")
        late = [p for p in bible.TEMPLATE_FILES if dt.datetime.fromtimestamp((HUB / p).stat().st_mtime) > last]
        if late:
            print(f"templates: NOT locked; changed after the last bible approval: {', '.join(late)}")
        else:
            lock["templates"] = _lock_entry(bible.TEMPLATE_FILES, None, None,
                                            f"bound in Phase D to the templates in use at the last bible approval ({last:%Y-%m-%dT%H:%M:%S}, unchanged since)")
            print("templates: locked")
    bible.write_lock(lock)
    return 0


def cmd_bible_approve(con, b, args):
    if args.file == "templates":  # the prompt templates and prompt_style.py, approved as one unit
        lock = bible.read_lock()
        lock["templates"] = _lock_entry(bible.TEMPLATE_FILES, None, args.quote, "owner")
        bible.write_lock(lock)
        with open(bible.BIBLE / "approvals.log", "a", encoding="utf-8") as f:
            f.write(f"{db.now()}\ttemplates\towner: {args.quote}\n")
        print("templates approved")
        return 0
    path = bible.BIBLE / f"{args.file}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.update(status="approved", approved_by="owner", approved_at=db.now(), approved_hash=bible.content_hash(data))
    bible.MODELS[args.file].model_validate(data)  # refuses incomplete files (e.g. no face reference)
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^approved_hash:", text, flags=re.M):
        text = re.sub(r"^(approved_at:.*)$", r"\1\napproved_hash: null", text, count=1, flags=re.M)
    for k in bible.APPROVAL_KEYS:
        value = f'"{data[k]}"' if k in ("approved_at", "approved_hash") else data[k]  # quoted: YAML would retype them
        text = re.sub(rf"^{k}:.*$", f"{k}: {value}", text, count=1, flags=re.M)
    bible.MODELS[args.file].model_validate(yaml.safe_load(text))  # the file as written must load
    path.write_text(text, encoding="utf-8")
    lock = bible.read_lock()  # Phase D: the approval covers the reference images this file names, by sha256
    lock[args.file] = _lock_entry(bible.asset_paths(data), data["approved_hash"], args.quote, "owner")
    bible.write_lock(lock)
    log = bible.BIBLE / "approvals.log"
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{db.now()}\t{args.file}\towner: {args.quote}\n")
    print(f"{args.file}.yaml approved")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--actor", default="claude", help="who is acting: owner, claude, or studio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    p = sub.add_parser("plan")
    p.add_argument("--start", required=True)
    p.add_argument("--days", type=int, default=7)
    p = sub.add_parser("script")
    p.add_argument("episode")
    p.add_argument("--file", required=True)
    p = sub.add_parser("generate")
    p.add_argument("episode")
    p.add_argument("--test", action="store_true")
    p = sub.add_parser("trial")
    p.add_argument("episode")
    p.add_argument("--model", required=True)
    p.add_argument("--frame-only", action="store_true")
    p.add_argument("--owner-cap", type=float, help="one-off per-video $ limit approved by the owner (needs --quote)")
    p.add_argument("--no-face-ref", action="store_true", help="describe her face in words only (Seedance refuses faces)")
    p.add_argument("--owner-day-cap", type=float, help="one-off daily $ limit approved by the owner (needs --quote)")
    p.add_argument("--quote", help="the owner's own words approving --owner-cap / --owner-day-cap")
    p = sub.add_parser("qa")
    p.add_argument("episode")
    for name in ("approve", "reject", "accept"):
        p = sub.add_parser(name)
        p.add_argument("episode")
        p.add_argument("--quote", required=True)
    p = sub.add_parser("promote")
    p.add_argument("trial")
    p.add_argument("--quote", required=True)
    p = sub.add_parser("schedule")
    p.add_argument("episode")
    p.add_argument("--caption", required=True)
    p = sub.add_parser("publish")
    p.add_argument("episode")
    p.add_argument("--mode", required=True, choices=["draft", "scheduled"])
    p.add_argument("--quote", help="owner's words (required for --mode scheduled)")
    p.add_argument("--now", action="store_true", help="draft mode: into the TikTok app's drafts right away")
    p.add_argument("--existing", metavar="POSTZEN_ID", help="with --now: record a draft upload already sent")
    p.add_argument("--resend", action="store_true",
                   help="with --now, owner only (--quote): send a draft upload that never reached TikTok again")
    sub.add_parser("sync")
    p = sub.add_parser("reschedule")
    p.add_argument("moves", nargs="+", metavar="EP=YYYY-MM-DD@HH:MM")
    p.add_argument("--reason", required=True)
    p = sub.add_parser("set-line")
    p.add_argument("episode")
    p.add_argument("--line", required=True)
    p = sub.add_parser("posted")
    p.add_argument("episode")
    p.add_argument("--url", required=True)
    p.add_argument("--ai-label-on", action="store_true", help="the post is disclosed as AI (TikTok's label or a caption disclosure)")
    sub.add_parser("board")
    sub.add_parser("bind-approvals")
    sub.add_parser("bible-lock")
    p = sub.add_parser("refs", help="Ember's references library")
    p.add_argument("action", choices=["sync", "list", "add", "verdict"])
    p.add_argument("target", nargs="?", help="add: image path; verdict: reference number")
    p.add_argument("value", nargs="?", choices=["approved", "rejected"])
    p.add_argument("--kind", default="example", choices=["example", "face_ref"])
    p.add_argument("--note")
    p.add_argument("--quote")
    p = sub.add_parser("bible-approve")
    p.add_argument("file", choices=bible.FILES + ["templates"])
    p.add_argument("--quote", required=True)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        b = bible.load()
        con = db.connect()
        if args.cmd in ("approve", "reject", "accept", "promote", "bible-approve") and args.actor != "owner":
            raise db.GateError("Owner-only command: pass --actor owner with the owner's own words in --quote")
        handler = {"validate": cmd_validate, "plan": cmd_plan, "script": cmd_script, "generate": cmd_generate,
                   "trial": cmd_trial, "promote": cmd_promote, "accept": cmd_accept, "publish": cmd_publish,
                   "sync": cmd_sync, "set-line": cmd_set_line, "reschedule": cmd_reschedule,
                   "qa": cmd_qa, "approve": lambda c, bb, a: cmd_owner(c, bb, a, "APPROVED"),
                   "reject": lambda c, bb, a: cmd_owner(c, bb, a, "REJECTED"), "schedule": cmd_schedule,
                   "posted": cmd_posted, "board": cmd_board, "bible-approve": cmd_bible_approve,
                   "bind-approvals": cmd_bind_approvals, "bible-lock": cmd_bible_lock, "refs": cmd_refs}[args.cmd]
        sys.exit(handler(con, b, args))
    except (bible.BibleError, db.GateError) as e:
        print(f"REFUSED: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
