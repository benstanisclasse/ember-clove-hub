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
-- Phase C: generation records, assets, features, performance marks, tracking links
CREATE TABLE IF NOT EXISTS generation_jobs (
  job_id INTEGER PRIMARY KEY, content_ref TEXT, kind TEXT, provider TEXT, provider_job_id TEXT, model TEXT,
  settings TEXT, template TEXT, template_sha TEXT, prompt_hash TEXT, prompt_text TEXT, started_at TEXT, finished_at TEXT,
  status TEXT, cost_usd REAL, cost_basis TEXT, asset_id INTEGER, error TEXT, note TEXT, source_key TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS assets (
  asset_id INTEGER PRIMARY KEY, content_ref TEXT, type TEXT, path TEXT UNIQUE, url TEXT, sha256 TEXT, bytes INTEGER,
  source TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS asset_refs (job_id INTEGER, position INTEGER, ref TEXT, PRIMARY KEY (job_id, position));
CREATE TABLE IF NOT EXISTS content_features (
  content_id TEXT, feature TEXT, value TEXT, source TEXT, PRIMARY KEY (content_id, feature));
CREATE TABLE IF NOT EXISTS content_marks (
  content_id TEXT, mark TEXT, anchor_at TEXT, anchor_basis TEXT, snapshot_at TEXT, views REAL, impressions REAL,
  reach REAL, likes REAL, comments REAL, shares REAL, saves REAL, clicks REAL, PRIMARY KEY (content_id, mark));
CREATE TABLE IF NOT EXISTS content_links (content_id TEXT, utm_content TEXT, url TEXT, PRIMARY KEY (content_id, utm_content));
-- Phase D: owner overrides of high findings (bound to the file and caption), Facebook AI-picture posts made here
CREATE TABLE IF NOT EXISTS overrides (
  id INTEGER PRIMARY KEY, content_id TEXT, check_name TEXT, asset_sha256 TEXT, caption_sha256 TEXT, quote TEXT,
  actor TEXT, at TEXT);
CREATE TABLE IF NOT EXISTS fb_ai_posts (
  content_id TEXT PRIMARY KEY, week TEXT, date TEXT, slot TEXT, kind TEXT, products TEXT, titles TEXT,
  supplier_photos TEXT, scene TEXT, prompt TEXT, prompt_hash TEXT, image_path TEXT, image_sha256 TEXT, image_url TEXT,
  caption TEXT, first_comment TEXT, fidelity_json TEXT, checks_json TEXT, approval_json TEXT, postzen_post_id TEXT,
  status TEXT, post_url TEXT, caption_format TEXT, question TEXT);
-- Phase D item 7: Ember's references library (scripts/studio/character_refs.py); never changes character.yaml
CREATE TABLE IF NOT EXISTS character_refs (
  ref_id INTEGER PRIMARY KEY, kind TEXT, version INTEGER, path TEXT UNIQUE, sha256 TEXT, verdict TEXT,
  in_use INTEGER DEFAULT 0, source TEXT, quote TEXT, actor TEXT, at TEXT, note TEXT);
"""
MARKS = (("24h", 24), ("48h", 48), ("7d", 168))
MARK_WINDOW_H = 6  # a mark uses the first snapshot taken within 6 hours after it; otherwise it stays empty

# The steps each kind of content goes through (Phase B: documented and used for display; enforcement stays in the
# TikTok stage machine and the Facebook publish guards).
WORKFLOWS = {
    "tiktok_video": ["planned", "scripted", "generated", "qa_failed", "awaiting_approval", "approved", "rejected",
                     "scheduled", "submitted", "in_tiktok_drafts", "awaiting_manual_post", "public", "measuring",
                     "failed"],
    "fb_photo": ["planned", "awaiting_approval", "scheduled", "paused", "submitted", "public", "failed"],
    # Phase D: AI-picture posts made in the database (scripts/studio/fb_ai.py) walk every step; older plan-file
    # posts show only planned/awaiting_approval and the publish states.
    "fb_ai_picture": ["planned", "image_generated", "fidelity_failed", "captioned", "qa_failed", "awaiting_approval",
                      "approved", "scheduled", "paused", "submitted", "public", "failed"],
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
    ensure_schema(con)
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


# --- generation jobs and assets (Phase C) ----------------------------------------------------------------------------

TEMPLATES = HUB / "studio" / "templates"


def template_fingerprint(name):
    """Version of a prompt template: sha256 of the template plus scripts/prompt_style.py (16 hex chars)."""
    h = hashlib.sha256()
    for p in (TEMPLATES / name, HUB / "scripts" / "prompt_style.py"):
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def ensure_schema(con):
    con.executescript(SCHEMA)
    if "sha256" not in {r[1] for r in con.execute("PRAGMA table_info(asset_refs)")}:  # Phase D: references hashed
        con.execute("ALTER TABLE asset_refs ADD COLUMN sha256 TEXT")
    have = {r[1] for r in con.execute("PRAGMA table_info(fb_ai_posts)")}
    for col in ("caption_format", "question"):  # Phase D item 6: caption rotation carried into the history
        if col not in have:
            con.execute(f"ALTER TABLE fb_ai_posts ADD COLUMN {col} TEXT")


def start_job(con, content_ref, kind, provider, model, settings=None, template=None, prompt_hash=None,
              prompt_text=None, refs=(), note=None):
    """Record a generation job before calling the provider; returns job_id. finish_job() closes it."""
    ensure_schema(con)
    cur = con.execute(
        "INSERT INTO generation_jobs (content_ref, kind, provider, model, settings, template, template_sha, prompt_hash, "
        "prompt_text, started_at, status, note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (content_ref, kind, provider, model, json.dumps(settings or {}), template,
         template_fingerprint(template) if template else None, prompt_hash, prompt_text, now_utc(), "running", note))
    for i, r in enumerate(refs):
        local = HUB / str(r) if not str(r).startswith("http") else None  # local reference files are hashed
        con.execute("INSERT OR REPLACE INTO asset_refs (job_id, position, ref, sha256) VALUES (?,?,?,?)",
                    (cur.lastrowid, i, str(r), sha256_file(local) if local and local.exists() else None))
    con.commit()
    return cur.lastrowid


def add_asset(con, content_ref, type_, path=None, url=None, source="generated"):
    ensure_schema(con)
    p = (HUB / path) if path and not Path(path).is_absolute() else (Path(path) if path else None)
    sha = sha256_file(p) if p and p.exists() else None
    rel = str(p.relative_to(HUB)).replace("\\", "/") if p and p.is_relative_to(HUB) else (str(p) if p else None)
    con.execute("INSERT OR IGNORE INTO assets (content_ref, type, path, url, sha256, bytes, source, created_at) "
                "VALUES (?,?,?,?,?,?,?,?)", (content_ref, type_, rel, url, sha, p.stat().st_size if p and p.exists() else None,
                                             source, now_utc()))
    if rel:
        con.execute("UPDATE assets SET url = COALESCE(?, url), sha256 = COALESCE(?, sha256) WHERE path = ?", (url, sha, rel))
        return con.execute("SELECT asset_id FROM assets WHERE path = ?", (rel,)).fetchone()[0]
    return con.execute("SELECT last_insert_rowid()").fetchone()[0]


def finish_job(con, job_id, status, provider_job_id=None, cost_usd=None, cost_basis=None, output_path=None,
               output_url=None, error=None):
    asset_id = None
    if output_path or output_url:
        ref = con.execute("SELECT content_ref, kind FROM generation_jobs WHERE job_id = ?", (job_id,)).fetchone()
        asset_id = add_asset(con, ref["content_ref"], "video" if ref["kind"] == "video" else "image", output_path, output_url)
    con.execute("UPDATE generation_jobs SET status = ?, provider_job_id = COALESCE(?, provider_job_id), cost_usd = ?, "
                "cost_basis = ?, asset_id = COALESCE(?, asset_id), finished_at = ?, error = ? WHERE job_id = ?",
                (status, provider_job_id, cost_usd, cost_basis, asset_id, now_utc(), (error or "")[:500] or None, job_id))
    con.commit()
    return asset_id


def backfill_generation(con):
    """One-time, idempotent: build generation_jobs/assets from what existed before Phase C — the spend table and the
    video files for Ember Studio, and the batch job files + results for Higgsfield images. Costs come from the
    spend table where it has them; image costs were never recorded and stay empty."""
    ensure_schema(con)
    n = 0
    ep_rows = {r["id"]: dict(r) for r in con.execute("SELECT id, model, resolution, prompt_hash, video_path FROM episodes")}
    by_ep = {}
    for r in con.execute("SELECT id, episode_id, usd, at FROM spend ORDER BY at"):
        by_ep.setdefault(r["episode_id"], []).append(dict(r))
    for ep_id, rows in by_ep.items():
        ep_dir = HUB / "studio" / "episodes" / ep_id
        videos = sorted(ep_dir.glob(f"{ep_id}_a*.mp4")) if ep_dir.exists() else []
        paid = [r for r in rows if r["usd"] > 0.5]  # video jobs; small amounts are first frames, 0 = failed
        for r in rows:
            vid = videos[paid.index(r)] if r in paid and paid.index(r) < len(videos) else None
            frame = r["usd"] > 0 and r not in paid
            provider = "higgsfield" if vid and "reference-to-video" in vid.name else ("openrouter" if vid or frame else None)
            model = (ep_rows.get(ep_id) or {}).get("model") if vid else ("google/gemini-3.1-flash-image" if frame else None)
            cur = con.execute(
                "INSERT OR IGNORE INTO generation_jobs (content_ref, kind, provider, model, prompt_hash, started_at, "
                "finished_at, status, cost_usd, cost_basis, note, source_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (f"TT-{ep_id}", "image" if frame else "video", provider, model,
                 (ep_rows.get(ep_id) or {}).get("prompt_hash") if vid else None, None, r["at"],
                 "completed" if (vid or frame) else "failed_or_unknown", r["usd"],
                 "estimate" if provider == "higgsfield" else "billed (spend table)",
                 "backfilled from the spend table on 2026-10-27; start time, template and references were not recorded",
                 f"spend:{r['id']}"))
            if cur.rowcount and vid:
                aid = add_asset(con, f"TT-{ep_id}", "video", vid)
                con.execute("UPDATE generation_jobs SET asset_id = ? WHERE source_key = ?", (aid, f"spend:{r['id']}"))
            n += cur.rowcount
    media = HUB / "data" / "media_generated"
    for spec_file, out_dir in ((media / "facebook_jobs_2026-10-28.json", media / "facebook_2026-10-28"),
                               (media / "facebook_jobs_2026-10-27_remake.json", media / "facebook_2026-10-28"),
                               (media / "gallery_jobs_2026-10-27.json", media / "gallery")):
        if not spec_file.exists():
            continue
        spec = json.loads(spec_file.read_text(encoding="utf-8"))
        results = json.loads((out_dir / "results.json").read_text(encoding="utf-8")) if (out_dir / "results.json").exists() else {}
        for job in spec.get("jobs") or []:
            png = out_dir / f"{job['key']}.png"
            prompt = f"{spec.get('style', '')} {job['prompt']}".strip()
            cur = con.execute(
                "INSERT OR IGNORE INTO generation_jobs (content_ref, kind, provider, model, settings, prompt_hash, prompt_text, "
                "status, cost_usd, cost_basis, note, source_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (f"IMG-{out_dir.name}/{job['key']}", "image", "higgsfield", "marketing-studio/image/flare",
                 json.dumps({"aspect": job.get("aspect")}), sha256_text(prompt)[:16], prompt,
                 "completed" if png.exists() else "failed_or_unknown", None, "not recorded",
                 f"backfilled from {spec_file.name}; Higgsfield image cost and request id were not recorded",
                 f"img:{spec_file.name}:{job['key']}"))
            if cur.rowcount:
                jid = cur.lastrowid
                for i, ref in enumerate(job.get("refs") or []):
                    con.execute("INSERT OR REPLACE INTO asset_refs (job_id, position, ref) VALUES (?,?,?)", (jid, i, ref))
                if png.exists():
                    aid = add_asset(con, f"IMG-{out_dir.name}/{job['key']}", "image", png, results.get(job["key"]))
                    con.execute("UPDATE generation_jobs SET asset_id = ? WHERE job_id = ?", (aid, jid))
            n += cur.rowcount
    con.commit()
    return n


# --- content features (Phase C) ------------------------------------------------------------------------------------

def hook_type(line):
    """Simple, transparent hook classes from the opening line (from the Hub tag vocabulary)."""
    t = (line or "").strip().lower()
    if not t:
        return None
    if t.startswith("pov"):
        return "pov"
    if "?" in t:
        return "question"
    return "statement"


def set_feature(con, content_id, feature, value, source="auto"):
    """Owner-set features (source 'owner') are never overwritten by the automatic ones."""
    old = con.execute("SELECT source FROM content_features WHERE content_id = ? AND feature = ?", (content_id, feature)).fetchone()
    if old and old["source"] == "owner" and source != "owner":
        return
    con.execute("INSERT OR REPLACE INTO content_features VALUES (?,?,?,?)",
                (content_id, feature, None if value is None else str(value), source))


def derive_features(con, b=None):
    """Fill the automatic features for every item from the bible, plan and Shopify data. Returns rows written."""
    ptype = {}
    try:
        import sqlite3
        a = sqlite3.connect(HUB / "studio" / "analytics.db")
        ptype = dict(a.execute("SELECT handle, product_type FROM products"))
    except Exception:
        pass
    pieces = {i.id: i for i in (b["wardrobe"].items if b else [])}
    n = 0
    for it in [dict(r) for r in con.execute("SELECT * FROM content_items")]:
        cid, f = it["content_id"], {}
        if it["slot_local"]:
            d, t = it["slot_local"].split(" ")
            f.update(slot=t, weekday=dt.date.fromisoformat(d).strftime("%a"))
        f["link_placement"] = it["link_placement"]
        f["ai_disclosure"] = it["ai_disclosure"]
        if it["channel"] == "tiktok" and it["episode_id"]:
            ep = con.execute("SELECT * FROM episodes WHERE id = ?", (it["episode_id"],)).fetchone()
            script = json.loads(ep["script_json"] or "{}") if ep["script_json"] else {}
            lines = script.get("lines") or []
            outfit = json.loads(ep["outfit_json"] or "[]")
            store = [pieces[o] for o in outfit if o in pieces and getattr(pieces[o], "store_product", None)]
            f.update(series=ep["series_id"], room=ep["room_id"], cta_type=ep["cta_type"], duration_s=ep["duration_s"],
                     hook_type=hook_type(lines[0] if lines else None), hook_text=lines[0] if lines else None,
                     words=sum(len(l.split()) for l in lines) or None, outfit_pieces=len(outfit) or None,
                     store_piece=", ".join(getattr(s, "name", s.id) for s in store) or None,
                     product_category=", ".join(sorted({str(getattr(s, "category", "")) for s in store})) or None,
                     model=ep["model"], attempts=ep["attempt"], qa_owner_accepted=int("owner_accepted" in (ep["qa_json"] or "")))
        else:
            cap = it["caption"] or ""
            handles = [r["handle"] for r in con.execute("SELECT handle FROM content_products WHERE content_id = ?", (cid,))]
            f.update(series=it["series"], post_kind=it["concept"], ai_picture=int(it["kind"] == "fb_ai_picture"),
                     caption_question=int("?" in cap.split("Shop it here")[0]), caption_chars=len(cap),
                     product_category=", ".join(sorted({ptype.get(h) or "?" for h in handles})) or None,
                     products=len(handles))
        for k, v in f.items():
            set_feature(con, cid, k, v)
            n += 1
    con.commit()
    return n


# --- performance marks (Phase C) ---------------------------------------------------------------------------------

def _ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def compute_marks(con, analytics_path=None):
    """24 h / 48 h / 7 d values per public item, read from real snapshots in analytics.db post_snapshots. The anchor
    is the scheduled time for posts PostZen published itself, or the first snapshot showing views for TikTok drafts
    the owner posted by hand (its exact posting time is unknown). A mark is filled only from a snapshot taken within
    MARK_WINDOW_H hours after it; nothing is interpolated or back-filled."""
    import sqlite3
    p = analytics_path or HUB / "studio" / "analytics.db"
    if not Path(p).exists():
        return 0
    a = sqlite3.connect(p)
    a.row_factory = sqlite3.Row
    n = 0
    for j in con.execute("SELECT content_id, channel, mode, postzen_post_id, scheduled_for, state FROM publish_jobs "
                         "WHERE state = 'public' AND postzen_post_id IS NOT NULL"):
        snaps = [dict(r) for r in a.execute("SELECT * FROM post_snapshots WHERE post_id = ? ORDER BY fetched_at",
                                            (j["postzen_post_id"],))]
        if not snaps:
            continue
        if j["mode"] == "tiktok_draft":
            first = next((s for s in snaps if (s["views"] or 0) + (s["impressions"] or 0) > 0), None)
            anchor, basis = (first["fetched_at"], "first snapshot with views (posted by hand)") if first else (None, None)
        else:
            anchor, basis = j["scheduled_for"], "scheduled publish time"
        if not anchor:
            continue
        for mark, hours in MARKS + (("latest", None),):
            if hours is None:
                s = snaps[-1]
            else:
                lo = _ts(anchor) + dt.timedelta(hours=hours)
                hi = lo + dt.timedelta(hours=MARK_WINDOW_H)
                s = next((x for x in snaps if lo <= _ts(x["fetched_at"]) <= hi), None)
            if s is None:
                continue
            con.execute("INSERT OR REPLACE INTO content_marks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (j["content_id"], mark, anchor, basis, s["fetched_at"], s["views"], s["impressions"], s["reach"],
                         s["likes"], s["comments"], s["shares"], s["saves"], s["clicks"]))
            n += 1
    con.commit()
    return n


# --- tracking links (Phase C) --------------------------------------------------------------------------------------

URL_RE = __import__("re").compile(r"https?://\S+")


def collect_links(con):
    """Every store link in each item's caption/first comment, with its utm_content, so store sessions tagged with that
    value can be credited to the item. New links carry utm_content=<content_id>; older ones a date_slot value."""
    from urllib.parse import parse_qs, urlsplit
    con.execute("DELETE FROM content_links")
    n = 0
    for it in con.execute("SELECT content_id, caption FROM content_items"):
        plan_text = ""
        row = con.execute("SELECT plan_file, plan_index FROM content_items WHERE content_id = ?", (it["content_id"],)).fetchone()
        if row["plan_file"] and (FB_DIR / row["plan_file"]).exists():
            post = json.loads((FB_DIR / row["plan_file"]).read_text(encoding="utf-8"))["posts"][row["plan_index"]]
            plan_text = post.get("first_comment") or ""
        for url in URL_RE.findall(f"{it['caption'] or ''}\n{plan_text}"):
            uc = (parse_qs(urlsplit(url).query).get("utm_content") or [None])[0]
            if uc:
                con.execute("INSERT OR IGNORE INTO content_links VALUES (?,?,?)", (it["content_id"], uc, url))
                n += 1
    con.commit()
    return n


def store_sessions_by_content(con, analytics_path=None):
    """content_id -> {sessions, cart_sessions, checkout_sessions, completed_sessions} from Shopify UTM sessions."""
    import sqlite3
    p = analytics_path or HUB / "studio" / "analytics.db"
    out = {}
    try:
        a = sqlite3.connect(p)
        a.row_factory = sqlite3.Row
        rows = a.execute("SELECT content, SUM(sessions) s, SUM(cart_sessions) c, SUM(checkout_sessions) k, "
                         "SUM(completed_sessions) d FROM store_sources_daily WHERE kind = 'utm' AND content != '' "
                         "GROUP BY content").fetchall()
    except Exception:
        return out
    by_uc = {r["content"]: r for r in rows}
    for l in con.execute("SELECT content_id, utm_content FROM content_links"):
        r = by_uc.get(l["utm_content"])
        if r:
            o = out.setdefault(l["content_id"], {"sessions": 0, "cart_sessions": 0, "checkout_sessions": 0, "completed_sessions": 0})
            o["sessions"] += r["s"] or 0
            o["cart_sessions"] += r["c"] or 0
            o["checkout_sessions"] += r["k"] or 0
            o["completed_sessions"] += r["d"] or 0
    return out


# --- data quality (Phase C) ----------------------------------------------------------------------------------------

def quality_checks(con):
    issues = []
    for r in con.execute("SELECT postzen_post_id, GROUP_CONCAT(content_id) ids, COUNT(DISTINCT content_id) n FROM publish_jobs "
                         "WHERE postzen_post_id IS NOT NULL GROUP BY postzen_post_id HAVING n > 1"):
        issues.append({"severity": "high", "check": "duplicate PostZen post", "detail": f"{r['postzen_post_id']} used by {r['ids']}"})
    for r in con.execute("SELECT c.content_id FROM content_items c JOIN publish_jobs j ON j.content_id = c.content_id "
                         "WHERE j.state = 'public' AND (j.platform_post_url IS NULL OR j.platform_post_url = '')"):
        issues.append({"severity": "medium", "check": "public without a post link", "detail": r["content_id"]})
    for r in con.execute("SELECT content_id FROM content_items WHERE content_id NOT IN (SELECT content_id FROM content_products) "
                         "AND state NOT IN ('planned')"):
        issues.append({"severity": "low", "check": "no product linked", "detail": r["content_id"]})
    for r in con.execute("SELECT content_id FROM content_items WHERE channel = 'facebook' AND state NOT IN ('planned') "
                         "AND content_id NOT IN (SELECT content_id FROM content_links)"):
        issues.append({"severity": "medium", "check": "Facebook post without a tracked store link", "detail": r["content_id"]})
    for r in con.execute("SELECT job_id, content_ref FROM generation_jobs WHERE status = 'running' AND started_at < ?",
                         ((dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),)):
        issues.append({"severity": "medium", "check": "generation job never finished", "detail": f"job {r['job_id']} {r['content_ref']}"})
    from studio import character_refs
    issues += character_refs.check(con)
    for cid, found in upcoming_checks(con).items():
        issues += [{**f, "detail": f"{cid}: {f['detail']}"} for f in found if f["severity"] in ("critical", "high")]
    return issues


UPCOMING = ("captioned", "awaiting_approval", "approved", "scheduled", "submitted", "paused", "in_tiktok_drafts",
            "awaiting_manual_post")


def upcoming_checks(con, analytics_path=None):
    """Phase D: every item not yet public, re-checked now with the shared rules: caption wording, AI disclosure for
    AI pictures, and each product still ACTIVE and in stock. Items already with PostZen are flagged here, never
    changed or cancelled automatically (the owner decides: pause, replace or let it run)."""
    from studio import checks
    out = {}
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for it in con.execute(f"SELECT * FROM content_items WHERE test = 0 AND archived = 0 AND state IN "
                          f"({', '.join('?' * len(UPCOMING))}) AND (scheduled_at IS NULL OR scheduled_at >= ?)",
                          (*UPCOMING, cutoff)):
        handles = [r["handle"] for r in con.execute("SELECT handle FROM content_products WHERE content_id = ?",
                                                    (it["content_id"],))]
        found = (checks.text_findings(it["caption"] or "")
                 + checks.disclosure_findings(it["caption"], it["kind"] == "fb_ai_picture")
                 + checks.availability(handles, analytics_path))
        if found:
            out[it["content_id"]] = found
    return out


# --- dashboard files -----------------------------------------------------------------------------------------------

def _mark_fields(m):
    """Flat per-mark fields for the dashboard: views, engagements and clicks, plus per-1,000-impressions rates."""
    out = {}
    for mark in ("24h", "48h", "7d", "latest"):
        r = m.get(mark)
        if not r:
            continue
        seen = (r["impressions"] or r["views"] or 0)
        eng = sum(r[k] or 0 for k in ("likes", "comments", "shares", "saves"))
        out.update({f"views_{mark}": r["views"], f"impressions_{mark}": r["impressions"], f"eng_{mark}": eng,
                    f"clicks_{mark}": r["clicks"], f"eng_per_1k_{mark}": round(1000 * eng / seen, 1) if seen else None,
                    f"clicks_per_1k_{mark}": round(1000 * (r["clicks"] or 0) / seen, 1) if seen else None})
        out["mark_anchor_basis"] = r["anchor_basis"]
    return out


def write_dashboard_files(con, out=DASH):
    """content_queue.json (every item with its latest publish job) and content_events.json (recent history)."""
    jobs = {}
    for j in con.execute("SELECT * FROM publish_jobs ORDER BY job_id"):
        jobs[j["content_id"]] = dict(j)
    prods = {}
    for r in con.execute("SELECT content_id, handle FROM content_products"):
        prods.setdefault(r["content_id"], []).append(r["handle"])
    feats = {}
    for r in con.execute("SELECT content_id, feature, value FROM content_features"):
        feats.setdefault(r["content_id"], {})[r["feature"]] = r["value"]
    marks = {}
    for r in con.execute("SELECT * FROM content_marks"):
        marks.setdefault(r["content_id"], {})[r["mark"]] = dict(r)
    costs = dict(con.execute("SELECT content_ref, ROUND(SUM(COALESCE(cost_usd, 0)), 2) FROM generation_jobs GROUP BY content_ref"))
    store = store_sessions_by_content(con)
    upcoming = upcoming_checks(con)
    rows = []
    for it in con.execute("SELECT * FROM content_items WHERE archived = 0 AND test = 0 ORDER BY scheduled_at"):
        it = dict(it)
        j = jobs.get(it["content_id"]) or {}
        approval = json.loads(it["approval_json"] or "{}")
        found = upcoming.get(it["content_id"], [])
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
                     # Phase D: approval bound to the exact file/caption; current findings from the shared rules
                     "approval_bound": bool(approval.get("asset_sha256") or approval.get("photos_sha256")),
                     "checks": found, "held": any(f["severity"] in ("critical", "high") for f in found),
                     "publish_state": j.get("state") or "", "publish_evidence": j.get("evidence") or "",
                     "postzen_post_id": j.get("postzen_post_id") or "", "post_url": j.get("platform_post_url") or "",
                     "episode_id": it["episode_id"] or "", "has_frames": bool(frames),
                     "features": feats.get(it["content_id"], {}), "gen_cost_usd": costs.get(it["content_id"]),
                     **_mark_fields(marks.get(it["content_id"], {})),
                     **{f"store_{k}": v for k, v in (store.get(it["content_id"]) or {}).items()}})
    atomic_write(out / "content_queue.json", json.dumps(rows, ensure_ascii=False, indent=1))
    jobs_rows = [dict(r) for r in con.execute(
        "SELECT job_id, content_ref, kind, provider, model, template, template_sha, status, cost_usd, cost_basis, started_at, "
        "finished_at, error, note FROM generation_jobs ORDER BY COALESCE(finished_at, started_at)")]
    atomic_write(out / "content_jobs.json", json.dumps(jobs_rows, ensure_ascii=False, indent=1))
    atomic_write(out / "content_quality.json", json.dumps(quality_checks(con), ensure_ascii=False, indent=1))
    ev = [dict(r) for r in con.execute(
        "SELECT content_id, from_state, to_state, actor, reason, at FROM content_events ORDER BY at DESC LIMIT 300")]
    atomic_write(out / "content_events.json", json.dumps(ev, ensure_ascii=False))
    return len(rows)


def write_reference_files(con, b, out=DASH):
    """character_refs.json (the references library) and bible_locks.json (which approvals cover their images and the
    prompt templates, and anything changed since). Returns the number of library entries."""
    from studio import bible, character_refs
    character_refs.sync(con)
    refs = character_refs.rows(con)
    atomic_write(out / "character_refs.json", json.dumps(refs, ensure_ascii=False, indent=1))
    lock = bible.read_lock()
    units = []
    for name in bible.FILES:
        m = b[name]
        units.append({"unit": name, "status": m.status, "changed_since_approval": m.changed_since_approval,
                      "approved_at": m.approved_at, "images_locked": m.assets_locked, "images": len((lock.get(name) or {}).get("files") or {}),
                      "changed": m.changed_assets, "basis": (lock.get(name) or {}).get("basis")})
    tpl = bible.template_status()
    units.append({"unit": "templates", "status": "approved" if tpl["locked"] and not tpl["changed"] else "draft",
                  "changed_since_approval": bool(tpl["changed"]), "approved_at": (lock.get("templates") or {}).get("at"),
                  "images_locked": tpl["locked"], "images": len(bible.TEMPLATE_FILES), "changed": tpl["changed"],
                  "basis": (lock.get("templates") or {}).get("basis")})
    atomic_write(out / "bible_locks.json", json.dumps(units, ensure_ascii=False, indent=1))
    return len(refs)


def sync(out=DASH, b=None):
    """Mirror both channels and write the dashboard files. Returns summary lines like the other sync jobs."""
    con = connect()
    try:
        if b is None:
            from studio import bible
            b = bible.load()
        n_tt = mirror_tiktok(con, b, out)
        n_fb = mirror_facebook(con)
        n_back = backfill_generation(con)  # idempotent: only the first run inserts anything
        n_feat = derive_features(con, b)
        n_marks = compute_marks(con)
        n_links = collect_links(con)
        n_refs = write_reference_files(con, b, out)  # before the queue: its quality checks read the library
        n_rows = write_dashboard_files(con, out)
        states = dict(con.execute("SELECT state, COUNT(*) FROM content_items WHERE test = 0 GROUP BY state").fetchall())
    finally:
        con.close()
    return [f"tiktok items {n_tt}", f"facebook items {n_fb}", f"queue rows {n_rows}", f"backfilled jobs {n_back}",
            f"features {n_feat}", f"marks {n_marks}", f"tracked links {n_links}", f"references {n_refs}",
            "states " + ", ".join(f"{k} {v}" for k, v in sorted(states.items()))]


if __name__ == "__main__":
    for line in sync():
        print(" ", line)
