"""Unified content records for every channel (Content Studio 2.0, Phase B).

One row per piece of content in studio/studio.db, whatever the channel, so TikTok videos and Facebook posts can be
seen and managed in one queue. The channels keep their own machinery:

  TikTok    `episodes` + `transitions` stay the source of truth (stage machine, gates and tests unchanged); every
            episode is mirrored here as TT-<episode id>, its transitions as content_events.
  Facebook  plan files in data/facebook/ stay the working source for now; every planned post is mirrored here as
            FB-<plan start>-<nn>, and every change of status seen between syncs is recorded as a content_event.

Tables (all in studio.db):
  content_items     content_id, channel, kind, workflow, state, series, caption, hook, CTA, link placement, AI
                    disclosure, slot (UTC + Eastern), episode id / plan file + index, approval, timestamps
  content_products  content_id -> product handle (+ Shopify GID when known) and its role
  content_assets    content_id -> media file or URL (+ sha256 for local files)
  content_events    content_id, from/to state, actor, reason, at (TikTok transitions are copied once each)
  publish_jobs      one row per send to PostZen: idempotency key, PostZen id, honest publish state and the evidence
  media_uploads     sha256 -> PostZen media URL, so a file is uploaded once and reused on retries

Publish states are never collapsed (see STATES_PUBLISH): a TikTok upload that reached the owner's drafts is
"in_tiktok_drafts" until there is public evidence (the post has views/impressions in PostZen's analytics) or the owner
records it with `cli.py posted`. A URL or a PostZen status of "published" alone does not prove a TikTok post is public.
"""
import csv
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HUB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HUB / "scripts"))
from studio import db  # noqa: E402

ET = ZoneInfo("America/New_York")
FB_DIR = HUB / "data" / "facebook"
DASH = HUB / "studio" / "dashboard"

SCHEMA = """
CREATE TABLE IF NOT EXISTS content_items (
  content_id TEXT PRIMARY KEY, channel TEXT NOT NULL, kind TEXT NOT NULL, workflow TEXT NOT NULL, state TEXT NOT NULL,
  title TEXT, series TEXT, concept TEXT, hook_text TEXT, cta_type TEXT, caption TEXT, link_placement TEXT,
  ai_disclosure INTEGER, scheduled_at TEXT, slot_local TEXT, episode_id TEXT, plan_file TEXT, plan_index INTEGER,
  approval_json TEXT, test INTEGER DEFAULT 0, archived INTEGER DEFAULT 0, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS content_products (
  content_id TEXT, handle TEXT, product_gid TEXT, role TEXT, PRIMARY KEY (content_id, handle, role));
CREATE TABLE IF NOT EXISTS content_assets (
  content_id TEXT, position INTEGER, kind TEXT, path TEXT, url TEXT, sha256 TEXT, source TEXT,
  PRIMARY KEY (content_id, position));
CREATE TABLE IF NOT EXISTS content_events (
  id INTEGER PRIMARY KEY, content_id TEXT, from_state TEXT, to_state TEXT, actor TEXT, reason TEXT, at TEXT,
  source_key TEXT UNIQUE);
CREATE INDEX IF NOT EXISTS content_events_item ON content_events (content_id, at);
CREATE TABLE IF NOT EXISTS publish_jobs (
  job_id INTEGER PRIMARY KEY, content_id TEXT, channel TEXT, mode TEXT, idempotency_key TEXT UNIQUE,
  postzen_post_id TEXT, platform_post_url TEXT, asset_sha256 TEXT, caption_sha256 TEXT, scheduled_for TEXT,
  submitted_at TEXT, state TEXT, evidence TEXT, platform_status TEXT, last_checked_at TEXT, attempts INTEGER DEFAULT 0,
  error TEXT);
CREATE INDEX IF NOT EXISTS publish_jobs_item ON publish_jobs (content_id);
CREATE TABLE IF NOT EXISTS media_uploads (sha256 TEXT PRIMARY KEY, url TEXT, filename TEXT, uploaded_at TEXT);
"""

# The steps each kind of content goes through (Phase B: documented and used for display; enforcement stays in the
# TikTok stage machine and the Facebook publish guards).
WORKFLOWS = {
    "tiktok_video": ["planned", "scripted", "generated", "qa_failed", "awaiting_approval", "approved", "rejected",
                     "scheduled", "submitted", "in_tiktok_drafts", "awaiting_manual_post", "public", "measuring",
                     "failed"],
    "fb_photo": ["planned", "awaiting_approval", "scheduled", "paused", "submitted", "public", "failed"],
    "fb_ai_picture": ["planned", "awaiting_approval", "scheduled", "paused", "submitted", "public", "failed"],
}
STATES_PUBLISH = {
    "submitted": "PostZen accepted the request",
    "scheduled": "PostZen will send it at the slot",
    "in_tiktok_drafts": "Delivered to the owner's TikTok drafts; not public yet",
    "awaiting_manual_post": "In the TikTok drafts and its slot has passed: post it from the app with the AI label",
    "public": "Live and visible (public evidence or the owner's confirmation)",
    "paused": "Held in PostZen as a PostZen draft; will not go out by itself",
    "failed": "PostZen or the platform reported a failure",
}
TT_STATE = {"PLANNED": "planned", "SCRIPTED": "scripted", "GENERATED": "generated", "QA_FAILED": "qa_failed",
            "QA_PASSED": "awaiting_approval", "APPROVED": "approved", "REJECTED": "rejected",
            "SCHEDULED": "scheduled", "POSTED": "public", "MEASURED": "measuring"}


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(path=None):
    """studio.db with the content tables. WAL and a busy timeout let the dashboard sync and the CLI write safely."""
    con = db.connect(path or db.DB)
    con.executescript(SCHEMA)
    return con


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def atomic_write(path, text):
    """Write a file so readers never see it half-written (temp file + rename)."""
    path = Path(path)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def slot_utc(day, hhmm):
    local = dt.datetime.fromisoformat(f"{day}T{hhmm}").replace(tzinfo=ET)
    return local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- writing items, events and publish jobs ------------------------------------------------------------------------

ITEM_COLS = ["content_id", "channel", "kind", "workflow", "state", "title", "series", "concept", "hook_text", "cta_type",
             "caption", "link_placement", "ai_disclosure", "scheduled_at", "slot_local", "episode_id", "plan_file",
             "plan_index", "approval_json", "test", "archived"]


def upsert_item(con, item, actor="studio", reason="sync"):
    """Insert or update a content item; a change of state is recorded as a content_event."""
    old = con.execute("SELECT state FROM content_items WHERE content_id = ?", (item["content_id"],)).fetchone()
    ts = now_utc()
    vals = [item.get(c, 0 if c in ("test", "archived") else None) for c in ITEM_COLS]
    if old is None:
        con.execute(f"INSERT INTO content_items ({', '.join(ITEM_COLS)}, created_at, updated_at) "
                    f"VALUES ({', '.join('?' * len(ITEM_COLS))}, ?, ?)", vals + [ts, ts])
        if item.get("channel") != "tiktok":  # TikTok history is copied from transitions instead
            add_event(con, item["content_id"], None, item["state"], actor, reason or "imported")
        return "new"
    con.execute(f"UPDATE content_items SET {', '.join(f'{c} = ?' for c in ITEM_COLS[1:])}, updated_at = ? "
                f"WHERE content_id = ?", vals[1:] + [ts, item["content_id"]])
    if old["state"] != item["state"] and item.get("channel") != "tiktok":
        add_event(con, item["content_id"], old["state"], item["state"], actor, reason)
    return "changed" if old["state"] != item["state"] else "same"


def add_event(con, content_id, from_state, to_state, actor, reason, at=None, source_key=None):
    con.execute("INSERT OR IGNORE INTO content_events (content_id, from_state, to_state, actor, reason, at, source_key) "
                "VALUES (?,?,?,?,?,?,?)", (content_id, from_state, to_state, actor, reason, at or now_utc(), source_key))


def set_children(con, content_id, products, assets):
    con.execute("DELETE FROM content_products WHERE content_id = ?", (content_id,))
    for handle, gid, role in products:
        con.execute("INSERT OR IGNORE INTO content_products VALUES (?,?,?,?)", (content_id, handle, gid, role))
    con.execute("DELETE FROM content_assets WHERE content_id = ?", (content_id,))
    for i, a in enumerate(assets):
        con.execute("INSERT INTO content_assets VALUES (?,?,?,?,?,?,?)",
                    (content_id, i, a.get("kind"), a.get("path"), a.get("url"), a.get("sha256"), a.get("source")))


def record_publish(con, content_id, channel, mode, key, **fields):
    """Create or update the publish job for an idempotency key. Call before sending (state 'submitting') and after."""
    row = con.execute("SELECT job_id, attempts FROM publish_jobs WHERE idempotency_key = ?", (key,)).fetchone()
    cols = ["postzen_post_id", "platform_post_url", "asset_sha256", "caption_sha256", "scheduled_for", "submitted_at",
            "state", "evidence", "platform_status", "last_checked_at", "error"]
    data = {c: fields[c] for c in cols if c in fields}
    if row is None:
        con.execute(f"INSERT INTO publish_jobs (content_id, channel, mode, idempotency_key, attempts, "
                    f"{', '.join(data)}) VALUES (?,?,?,?,?{', ?' * len(data)})",
                    [content_id, channel, mode, key, int(fields.get("attempt", 0))] + list(data.values()))
    else:
        sets = ", ".join(f"{c} = ?" for c in data) + (", attempts = attempts + 1" if fields.get("attempt") else "")
        if sets:
            con.execute(f"UPDATE publish_jobs SET {sets.lstrip(', ')} WHERE job_id = ?", list(data.values()) + [row["job_id"]])
    con.commit()


# --- honest publish state ------------------------------------------------------------------------------------------

def tiktok_live_evidence(out=DASH):
    """PostZen post ids that TikTok reports with views or impressions: proof the post is public."""
    f = out / "tiktok_videos.csv"
    live = {}
    if f.exists():
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                try:
                    seen = float(r.get("views") or 0) + float(r.get("impressions") or 0)
                except ValueError:
                    seen = 0
                if seen > 0 and r.get("post_id"):
                    live[r["post_id"]] = f"{int(float(r.get('views') or 0))} views in PostZen analytics"
    return live


def tiktok_publish_state(mode, platform_status, postzen_id, scheduled_for, live, owner_posted):
    """Return (state, evidence). Drafts are never 'public' without evidence."""
    if owner_posted:
        return "public", "owner recorded it as posted"
    if postzen_id in live:
        return "public", live[postzen_id]
    s = (platform_status or "").lower()
    if s in ("failed", "error"):
        return "failed", f"PostZen status {platform_status}"
    if mode == "scheduled":  # public scheduled post sent by PostZen itself
        if s == "published":
            return "public", "PostZen published it publicly (scheduled mode)"
        return ("paused", "PostZen draft (paused)") if s == "draft" else ("scheduled", f"PostZen status {platform_status}")
    if s == "draft":
        return "paused", "PostZen draft (paused)"
    if s in ("scheduled", "queued", "pending", ""):
        return "scheduled", "goes to the TikTok drafts at its slot"
    if s == "published":  # delivered to the owner's TikTok drafts
        due = scheduled_for and scheduled_for <= now_utc()
        return ("awaiting_manual_post" if due else "in_tiktok_drafts",
                "PostZen delivered it to the TikTok drafts; no public views yet")
    return "submitted", f"PostZen status {platform_status}"


def fb_publish_state(platform_status, post_url):
    s = (platform_status or "").lower()
    if s == "published":
        return "public", f"Facebook post {post_url}" if post_url else "PostZen published it"
    if s in ("failed", "error"):
        return "failed", f"PostZen status {platform_status}"
    if s == "draft":
        return "paused", "PostZen draft (paused)"
    if s in ("scheduled", "queued", "pending"):
        return "scheduled", f"PostZen status {platform_status}"
    return "submitted", f"PostZen status {platform_status}"


# --- mirrors -------------------------------------------------------------------------------------------------------

def _wardrobe_products(b):
    """wardrobe item id -> (handle, role) for store pieces."""
    out = {}
    for i in b["wardrobe"].items if b else []:
        if getattr(i, "store_product", None):
            out[i.id] = (str(i.store_product), "store_shoes" if getattr(i, "category", "") == "shoes" else "outfit_piece")
    return out


def _handle_gids():
    """Shopify handle -> product GID from the shared Shopify sync (analytics.db); empty if not synced yet."""
    import sqlite3
    p = HUB / "studio" / "analytics.db"
    if not p.exists():
        return {}
    try:
        con = sqlite3.connect(p)
        return dict(con.execute("SELECT handle, product_id FROM products"))
    except sqlite3.Error:
        return {}


def mirror_tiktok(con, b=None, out=DASH):
    """Mirror every real episode into content_items, its transitions into content_events and its PostZen send into
    publish_jobs. Returns the number of items written."""
    live = tiktok_live_evidence(out)
    pieces = _wardrobe_products(b)
    n = 0
    for ep in [dict(r) for r in con.execute("SELECT * FROM episodes WHERE test = 0")]:
        cid = f"TT-{ep['id']}"
        script = json.loads(ep["script_json"] or "{}") if ep["script_json"] else {}
        sched = slot_utc(ep["post_date"], ep["slot"]) if ep["post_date"] and ep["slot"] else None
        owner_posted = ep["state"] in ("POSTED", "MEASURED")
        state = TT_STATE.get(ep["state"], ep["state"].lower())
        pub_state = evidence = None
        if ep["postzen_post_id"]:
            pub_state, evidence = tiktok_publish_state(ep["publish_mode"], ep["platform_status"], ep["postzen_post_id"],
                                                       sched, live, owner_posted)
            if ep["state"] == "SCHEDULED":
                state = pub_state
        upsert_item(con, {"content_id": cid, "channel": "tiktok", "kind": "tiktok_video", "workflow": "tiktok_video",
                          "state": state, "title": ep["title"], "series": ep["series_id"], "concept": ep["pillar"],
                          "hook_text": (script.get("lines") or [None])[0], "cta_type": ep["cta_type"],
                          "caption": ep["caption"], "link_placement": None,
                          "ai_disclosure": int("#aigenerated" in (ep["caption"] or "").lower() or ep["publish_mode"] == "draft"),
                          "scheduled_at": sched, "slot_local": f"{ep['post_date']} {ep['slot']}", "episode_id": ep["id"],
                          "approval_json": ep["approval_json"], "test": 0})
        products = []
        for wid in json.loads(ep["outfit_json"] or "[]"):
            if wid in pieces:
                handle, role = pieces[wid]
                products.append((handle, None, role))
        assets = []
        if ep["video_path"] and (HUB / ep["video_path"]).exists():
            assets.append({"kind": "video", "path": ep["video_path"], "sha256": _cached_sha(HUB / ep["video_path"]),
                           "source": "generated"})
        set_children(con, cid, products, assets)
        for t in con.execute("SELECT * FROM transitions WHERE episode_id = ?", (ep["id"],)):
            add_event(con, cid, TT_STATE.get(t["from_state"], t["from_state"]), TT_STATE.get(t["to_state"], t["to_state"]),
                      t["actor"], t["reason"], t["at"], f"tt:{t['id']}")
        if ep["postzen_post_id"]:
            key = f"pz:{ep['postzen_post_id']}"
            record_publish(con, cid, "tiktok", f"tiktok_{ep['publish_mode'] or 'unknown'}", key,
                           postzen_post_id=ep["postzen_post_id"], platform_post_url=ep["post_url"], scheduled_for=sched,
                           state=pub_state, evidence=evidence, platform_status=ep["platform_status"],
                           last_checked_at=now_utc())
        n += 1
    con.commit()
    return n


_SHA_CACHE = {}


def _cached_sha(path):
    key = (str(path), path.stat().st_mtime, path.stat().st_size)
    if key not in _SHA_CACHE:
        _SHA_CACHE[key] = sha256_file(path)
    return _SHA_CACHE[key]


def _fb_kind(post):
    ai = bool(post.get("ai_picture")) or any("media.postzen.dev" in u for u in post.get("photos") or [])
    return "fb_ai_picture" if ai else "fb_photo"


def mirror_facebook(con, fb_dir=FB_DIR):
    """Mirror every post of every Facebook plan file. Items keep a stable id: FB-<plan start>-<index>."""
    gids = _handle_gids()
    n = 0
    for path in sorted(fb_dir.glob("plan_*.json")):
        plan = json.loads(path.read_text(encoding="utf-8"))
        approvals = plan.get("approvals") or []
        for i, p in enumerate(plan.get("posts") or []):
            cid = f"FB-{plan.get('start', path.stem[5:])}-{i:02d}"
            sched = slot_utc(p["date"], p["slot"])
            if p.get("postzen_post_id"):
                state, evidence = fb_publish_state(p.get("status"), p.get("post_url"))
            else:
                state, evidence = ("awaiting_approval" if p.get("caption") else "planned"), None
            caption = p.get("caption") or ""
            approval = _fb_approval(p, approvals)
            upsert_item(con, {"content_id": cid, "channel": "facebook", "kind": _fb_kind(p), "workflow": _fb_kind(p),
                              "state": state, "title": " + ".join(p.get("titles") or []),
                              "series": "fb_outfit" if p.get("kind") == "outfit" else "fb_product",
                              "concept": p.get("kind"), "hook_text": None, "cta_type": "link",
                              "caption": caption,
                              "link_placement": "first_comment" if p.get("first_comment") else "caption",
                              "ai_disclosure": int("#aigenerated" in caption.lower()),
                              "scheduled_at": sched, "slot_local": f"{p['date']} {p['slot']}", "episode_id": None,
                              "plan_file": path.name, "plan_index": i,
                              "approval_json": json.dumps(approval) if approval else None, "test": 0},
                        reason=f"PostZen status {p.get('status')}" if p.get("postzen_post_id") else "planned")
            products = [(h, gids.get(h), "outfit_piece" if p.get("kind") == "outfit" else "featured")
                        for h in p.get("products") or []]
            assets = [{"kind": "image", "url": u, "source": "ai_generated" if "media.postzen.dev" in u else "supplier"}
                      for u in p.get("photos") or []]
            if p.get("ai_picture"):
                local = HUB / p["ai_picture"].replace("\\", "/")
                assets.append({"kind": "image", "path": p["ai_picture"], "source": "ai_generated",
                               "sha256": _cached_sha(local) if local.exists() else None})
            set_children(con, cid, products, assets)
            if p.get("postzen_post_id"):
                record_publish(con, cid, "facebook", "fb_scheduled", f"pz:{p['postzen_post_id']}",
                               postzen_post_id=p["postzen_post_id"], platform_post_url=p.get("post_url"),
                               caption_sha256=sha256_text(caption), scheduled_for=sched, state=state, evidence=evidence,
                               platform_status=p.get("status"), last_checked_at=now_utc())
            n += 1
    con.commit()
    return n


def _fb_approval(post, approvals):
    """The owner approval that covers a post: a per-post approval if one exists, else the plan's approvals."""
    if post.get("approval"):
        return post["approval"]
    key = f"{post['date']} {post['slot']}"
    for a in approvals:
        if a.get("post") == key:
            return a
    return {"plan_approvals": approvals} if approvals else None


# --- PostZen media, uploaded once -----------------------------------------------------------------------------------

def upload_media(con, path, pz):
    """Upload a local file to PostZen once; later calls (retries, re-sends) reuse the stored URL."""
    digest = sha256_file(path)
    row = con.execute("SELECT url FROM media_uploads WHERE sha256 = ?", (digest,)).fetchone()
    if row:
        return row["url"], digest
    url = pz.upload(Path(path))
    con.execute("INSERT OR REPLACE INTO media_uploads VALUES (?,?,?,?)", (digest, url, Path(path).name, now_utc()))
    con.commit()
    return url, digest


# --- dashboard files -----------------------------------------------------------------------------------------------

def write_dashboard_files(con, out=DASH):
    """content_queue.json (every item with its latest publish job) and content_events.json (recent history)."""
    jobs = {}
    for j in con.execute("SELECT * FROM publish_jobs ORDER BY job_id"):
        jobs[j["content_id"]] = dict(j)
    prods = {}
    for r in con.execute("SELECT content_id, handle FROM content_products"):
        prods.setdefault(r["content_id"], []).append(r["handle"])
    rows = []
    for it in con.execute("SELECT * FROM content_items WHERE archived = 0 AND test = 0 ORDER BY scheduled_at"):
        it = dict(it)
        j = jobs.get(it["content_id"]) or {}
        frames = None
        if it["episode_id"]:
            ep = con.execute("SELECT video_path FROM episodes WHERE id = ?", (it["episode_id"],)).fetchone()
            if ep and ep["video_path"]:
                f = HUB / Path(ep["video_path"]).with_name(Path(ep["video_path"]).stem + "_frames.jpg")
                frames = f.exists()
        rows.append({"content_id": it["content_id"], "channel": it["channel"], "kind": it["kind"], "state": it["state"],
                     "title": it["title"], "series": it["series"], "caption": it["caption"],
                     "slot_local": it["slot_local"], "scheduled_at": it["scheduled_at"],
                     "link_placement": it["link_placement"], "ai_disclosure": it["ai_disclosure"],
                     "approved": bool(it["approval_json"]), "products": ", ".join(prods.get(it["content_id"], [])),
                     "publish_state": j.get("state") or "", "publish_evidence": j.get("evidence") or "",
                     "postzen_post_id": j.get("postzen_post_id") or "", "post_url": j.get("platform_post_url") or "",
                     "episode_id": it["episode_id"] or "", "has_frames": bool(frames)})
    atomic_write(out / "content_queue.json", json.dumps(rows, ensure_ascii=False, indent=1))
    ev = [dict(r) for r in con.execute(
        "SELECT content_id, from_state, to_state, actor, reason, at FROM content_events ORDER BY at DESC LIMIT 300")]
    atomic_write(out / "content_events.json", json.dumps(ev, ensure_ascii=False))
    return len(rows)


def sync(out=DASH, b=None):
    """Mirror both channels and write the dashboard files. Returns summary lines like the other sync jobs."""
    con = connect()
    try:
        if b is None:
            from studio import bible
            b = bible.load()
        n_tt = mirror_tiktok(con, b, out)
        n_fb = mirror_facebook(con)
        n_rows = write_dashboard_files(con, out)
        states = dict(con.execute("SELECT state, COUNT(*) FROM content_items WHERE test = 0 GROUP BY state").fetchall())
    finally:
        con.close()
    return [f"tiktok items {n_tt}", f"facebook items {n_fb}", f"queue rows {n_rows}",
            "states " + ", ".join(f"{k} {v}" for k, v in sorted(states.items()))]


if __name__ == "__main__":
    for line in sync():
        print(" ", line)
