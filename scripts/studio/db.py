"""Episode database (studio/studio.db) and the locked stage order.

Every change of stage goes through move(), which checks the allowed path and the stage's preconditions and writes an
audit row (who, when, why). Owner-only stages (APPROVED, REJECTED) need actor "owner" and the owner's words quoted.
"""
import datetime as dt
import json
import sqlite3
from pathlib import Path

HUB = Path(__file__).resolve().parents[2]
DB = HUB / "studio" / "studio.db"

STATES = ["PLANNED", "SCRIPTED", "GENERATED", "QA_FAILED", "QA_PASSED", "APPROVED", "REJECTED", "SCHEDULED",
          "POSTED", "MEASURED"]
ALLOWED = {
    "PLANNED": {"SCRIPTED"},
    "SCRIPTED": {"SCRIPTED", "GENERATED"},
    "GENERATED": {"QA_PASSED", "QA_FAILED"},
    "QA_FAILED": {"SCRIPTED", "GENERATED", "QA_PASSED"},  # QA_PASSED only by the owner, after listening
    "QA_PASSED": {"APPROVED", "REJECTED"},
    "REJECTED": {"SCRIPTED"},
    "APPROVED": {"SCHEDULED"},
    "SCHEDULED": {"SCHEDULED", "POSTED"},  # SCHEDULED again = caption change
    "POSTED": {"MEASURED"},
    "MEASURED": set(),
}
OWNER_ONLY = {"APPROVED", "REJECTED"}


class GateError(Exception):
    pass


def connect(path=DB):
    # The dashboard sync thread and the CLI both write here: wait up to 30 s for a lock, and use WAL so readers and
    # a writer don't block each other (Content Studio 2.0, Phase B).
    con = sqlite3.connect(path, timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS episodes (
        id TEXT PRIMARY KEY, series_id TEXT, ep_no INTEGER, pillar TEXT, title TEXT, post_date TEXT, slot TEXT,
        room_id TEXT, product_id TEXT, outfit_json TEXT, cta_type TEXT, cta_line TEXT, script_json TEXT,
        prompt_text TEXT, prompt_hash TEXT, model TEXT, resolution TEXT, duration_s INTEGER, attempt INTEGER DEFAULT 0,
        cost_usd REAL DEFAULT 0, video_path TEXT, qa_json TEXT, approval_json TEXT, caption TEXT, post_url TEXT,
        test INTEGER DEFAULT 0, state TEXT NOT NULL, created_at TEXT, updated_at TEXT);
    CREATE TABLE IF NOT EXISTS transitions (
        id INTEGER PRIMARY KEY, episode_id TEXT, from_state TEXT, to_state TEXT, actor TEXT, reason TEXT, at TEXT);
    CREATE TABLE IF NOT EXISTS spend (id INTEGER PRIMARY KEY, episode_id TEXT, usd REAL, at TEXT);
    CREATE TABLE IF NOT EXISTS metrics (
        episode_id TEXT, measured_at TEXT, hours_after INTEGER, views INTEGER, avg_watch_s REAL, likes INTEGER,
        comments INTEGER, shares INTEGER, follows INTEGER, profile_visits INTEGER, PRIMARY KEY (episode_id, hours_after));
    """)
    have = {r[1] for r in con.execute("PRAGMA table_info(episodes)")}
    for col in ("postzen_post_id", "publish_mode", "platform_status"):  # PostZen publishing (2026-10-26)
        if col not in have:
            con.execute(f"ALTER TABLE episodes ADD COLUMN {col} TEXT")
    con.commit()
    return con


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


def get(con, ep_id):
    row = con.execute("SELECT * FROM episodes WHERE id = ?", (ep_id,)).fetchone()
    if row is None:
        raise GateError(f"No episode {ep_id}")
    return dict(row)


def _preconditions(ep, to, fields):
    merged = {**ep, **fields}
    need = {
        "SCRIPTED": ["script_json"],
        "GENERATED": ["prompt_text", "prompt_hash", "video_path", "model"],
        "QA_PASSED": ["qa_json"],
        "QA_FAILED": ["qa_json"],
        "APPROVED": ["approval_json"],
        "REJECTED": ["approval_json"],
        "SCHEDULED": ["caption"],
        "POSTED": ["post_url"],
    }.get(to, [])
    missing = [f for f in need if not merged.get(f)]
    if missing:
        raise GateError(f"{ep['id']} -> {to}: missing {', '.join(missing)}")
    if to == "GENERATED" and not Path(HUB / merged["video_path"]).exists():
        raise GateError(f"{ep['id']} -> GENERATED: video file not found")
    if to == "QA_PASSED" and not json.loads(merged["qa_json"]).get("passed"):
        raise GateError(f"{ep['id']} -> QA_PASSED: QA did not pass")
    if to == "APPROVED" and merged.get("test"):
        raise GateError(f"{ep['id']} is a test episode (draft bible): it can never be approved for posting")
    # Owner 2026-10-26: the caption no longer has to say "AI-generated"; the platform's AI-generated label does that,
    # and marking a post as published requires confirming it was on.
    if to == "POSTED" and not merged.get("ai_label_on"):
        raise GateError(f"{ep['id']} -> POSTED: confirm the post is disclosed as AI (--ai-label-on)")


def move(con, ep_id, to, actor, reason, **fields):
    ep = get(con, ep_id)
    if to not in ALLOWED[ep["state"]]:
        raise GateError(f"{ep_id}: {ep['state']} -> {to} is not an allowed step "
                        f"(allowed: {', '.join(sorted(ALLOWED[ep['state']])) or 'none'})")
    if to in OWNER_ONLY or (ep["state"] == "QA_FAILED" and to == "QA_PASSED"):
        if actor != "owner":
            raise GateError(f"{ep_id}: only the owner can move an episode to {to}")
        if not fields.get("approval_json") or not json.loads(fields["approval_json"]).get("owner_quote"):
            raise GateError(f"{ep_id}: {to} needs the owner's own words quoted")
    if to == "GENERATED" and ep["state"] == "QA_FAILED" and ep["attempt"] >= fields.get("max_attempts", 99):
        raise GateError(f"{ep_id}: attempt limit reached; rewrite the script instead")
    fields.pop("max_attempts", None)
    _preconditions(ep, to, fields)
    fields.pop("ai_label_on", None)  # checked, not stored as a column; recorded in the audit reason
    sets = ", ".join(f"{k} = ?" for k in fields)
    con.execute(f"UPDATE episodes SET state = ?, updated_at = ?{', ' + sets if sets else ''} WHERE id = ?",
                [to, now(), *fields.values(), ep_id])
    con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                (ep_id, ep["state"], to, actor, reason, now()))
    con.commit()
    return get(con, ep_id)


NOTE_FIELDS = {"postzen_post_id", "publish_mode", "platform_status", "post_url"}


def note(con, ep_id, reason, **fields):
    """Record publishing facts (PostZen id, mode, TikTok status, post link) without changing the stage; logged like
    any move. Only these fields: a stage change always goes through move()."""
    bad = set(fields) - NOTE_FIELDS
    if bad:
        raise GateError(f"note() can't set {', '.join(sorted(bad))}")
    ep = get(con, ep_id)
    con.execute(f"UPDATE episodes SET updated_at = ?, {', '.join(f'{k} = ?' for k in fields)} WHERE id = ?",
                [now(), *fields.values(), ep_id])
    con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                (ep_id, ep["state"], ep["state"], "studio", reason, now()))
    con.commit()
    return get(con, ep_id)


def reschedule(con, moves, actor, reason, check, with_postzen=False, dry_run=False):
    """Move episodes to new (date, slot) pairs in one step. check(episodes) returns calendar errors for the calendar as
    it would be; any error refuses the whole move. Episodes already with PostZen can't move unless with_postzen (the
    caller has moved the PostZen post first; only public posts still waiting for their slot); posted ones never move.
    dry_run: check only, change nothing."""
    eps = {r["id"]: dict(r) for r in con.execute("SELECT * FROM episodes WHERE test = 0")}
    old_errs = set(check(sorted(eps.values(), key=lambda e: (e["post_date"], e["slot"]))))  # already there; don't block
    for ep_id, (day, slot) in moves.items():
        ep = eps.get(ep_id) or get(con, ep_id)
        pz_ok = with_postzen and ep["publish_mode"] == "scheduled" and ep["platform_status"] == "scheduled"
        if ep["test"] or (ep["postzen_post_id"] and not pz_ok) or ep["state"] in ("POSTED", "MEASURED"):
            raise GateError(f"{ep_id} is {'with PostZen' if ep['postzen_post_id'] else ep['state']}; it can't move")
        ep.update(post_date=day, slot=slot)
    taken = {}
    for e in eps.values():
        if (e["post_date"], e["slot"]) in taken:
            raise GateError(f"{e['id']} and {taken[(e['post_date'], e['slot'])]} both on {e['post_date']} {e['slot']}")
        taken[(e["post_date"], e["slot"])] = e["id"]
    errs = [e for e in check(sorted(eps.values(), key=lambda e: (e["post_date"], e["slot"]))) if e not in old_errs]
    if errs:
        raise GateError("calendar rules fail:\n  " + "\n  ".join(errs))
    if dry_run:
        return
    for ep_id, (day, slot) in moves.items():
        old = get(con, ep_id)
        con.execute("UPDATE episodes SET post_date = ?, slot = ?, updated_at = ? WHERE id = ?", (day, slot, now(), ep_id))
        con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                    (ep_id, old["state"], old["state"], actor,
                     f"moved from {old['post_date']} {old['slot']} to {day} {slot}: {reason}", now()))
    con.commit()


def set_cta_line(con, ep_id, line, soft_lines, reason):
    """Swap a planned follow line for another line from the rules (e.g. after the owner retires one). Logged."""
    ep = get(con, ep_id)
    if line not in soft_lines:
        raise GateError(f"{line!r} is not one of the rules' follow lines")
    if not ep["cta_line"] or ep["cta_line"] in soft_lines:
        raise GateError(f"{ep_id}'s follow line {ep['cta_line']!r} is still valid; nothing to swap")
    con.execute("UPDATE episodes SET cta_line = ?, updated_at = ? WHERE id = ?", (line, now(), ep_id))
    con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                (ep_id, ep["state"], ep["state"], "studio", f"follow line {ep['cta_line']!r} -> {line!r}: {reason}", now()))
    con.commit()
    return get(con, ep_id)


def trial_copy(con, ep_id, actor, reason):
    """Copy a SCRIPTED episode to <id>-T<n> marked test, so a model trial never touches the real episode and its video
    can never be approved for posting."""
    ep = get(con, ep_id)
    if ep["state"] != "SCRIPTED" or ep["test"]:
        raise GateError(f"{ep_id}: trials start from a SCRIPTED, non-test episode (it is {ep['state']})")
    n = con.execute("SELECT COUNT(*) FROM episodes WHERE id LIKE ?", (f"{ep_id}-T%",)).fetchone()[0] + 1
    new = f"{ep_id}-T{n}"
    keep = ["series_id", "ep_no", "pillar", "title", "post_date", "slot", "room_id", "product_id", "outfit_json",
            "cta_type", "cta_line", "script_json"]
    con.execute(f"INSERT INTO episodes (id, {', '.join(keep)}, test, state, created_at, updated_at) "
                f"VALUES (?, {', '.join('?' for _ in keep)}, 1, 'SCRIPTED', ?, ?)",
                [new, *[ep[k] for k in keep], now(), now()])
    con.execute("INSERT INTO transitions (episode_id, from_state, to_state, actor, reason, at) VALUES (?,?,?,?,?,?)",
                (new, None, "SCRIPTED", actor, f"trial copy of {ep_id}: {reason}", now()))
    con.commit()
    return get(con, new)


def promote_trial(con, trial_id, actor, quote):
    """Owner-only: use a trial's video for the real episode it was copied from (same script), instead of generating
    again. The real episode then goes through QA, owner approval and scheduling like any other."""
    if actor != "owner" or not quote:
        raise GateError("promote is owner-only: pass --actor owner and the owner's own words in --quote")
    t = get(con, trial_id)
    if not t["test"] or "-T" not in t["id"] or not t["video_path"]:
        raise GateError(f"{trial_id}: only a generated trial copy can be promoted")
    src = get(con, t["id"].rsplit("-T", 1)[0])
    if src["script_json"] != t["script_json"] or src["outfit_json"] != t["outfit_json"]:
        raise GateError(f"{trial_id}: script or outfit differs from {src['id']}; it can't stand in for it")
    if src["state"] != "SCRIPTED":
        raise GateError(f"{src['id']} is {src['state']}; promote needs it SCRIPTED")
    return move(con, src["id"], "GENERATED", actor, f"promoted trial {trial_id} (owner: {quote})",
                prompt_text=t["prompt_text"], prompt_hash=t["prompt_hash"], model=t["model"],
                resolution=t["resolution"], duration_s=t["duration_s"], attempt=1, cost_usd=t["cost_usd"],
                video_path=t["video_path"])


def spent(con, since):
    return con.execute("SELECT COALESCE(SUM(usd), 0) FROM spend WHERE at >= ?", (since,)).fetchone()[0]
