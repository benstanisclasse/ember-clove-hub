"""Send approved episodes to TikTok through PostZen, and pull status and analytics back. Only called through cli.py.

publish(): an episode the owner approved and scheduled goes to PostZen for its planned slot, in one of two modes:
  draft      at the slot time PostZen puts it in the TikTok app's drafts; the owner posts it there with TikTok's
             AI-generated label on (PostZen can't set that label).
  scheduled  PostZen posts it publicly at the slot time by itself. PostZen can't set TikTok's AI flag (is_aigc), so the
             caption has to disclose it; an unlabelled post was flagged as a violation (2026-10-27). Owner-only, with their words.
sync(): post statuses, TikTok video metrics, followers and daily totals from PostZen, plus the conveyor's own
calendar and spend, written as JSON rows to studio/dashboard/ for the Ember Studio dashboard.
"""
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HUB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HUB / "scripts"))
import hub_env  # noqa: E402
import postzen as pz  # noqa: E402

from studio import checks, content, db  # noqa: E402

OUT = HUB / "studio" / "dashboard"
SETTINGS = {
    "draft": {"uploadAsDraft": True},
    "scheduled": {"privacyLevel": "publicToEveryone", "allowComments": True, "allowDuet": True, "allowStitch": True},
}


def account_id():
    return hub_env.load_config()["postzen"]["tiktok_account_id"]


def slot_time(ep, b):
    tz = ZoneInfo(b["rules"].posting.timezone)
    local = dt.datetime.fromisoformat(f"{ep['post_date']}T{ep['slot']}").replace(tzinfo=tz)
    return local, local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def paused(ep):
    """A scheduled post the owner paused: it sits in PostZen as a PostZen draft and won't go out by itself."""
    return ep["publish_mode"] == "scheduled" and ep["platform_status"] == "draft"


def tiktok_label(ep, live=None):
    """What the dashboard says about an episode's TikTok post. A draft upload is only "live" with public evidence
    (views/impressions in PostZen's analytics, `live` = {postzen id: evidence}) or the owner's `posted`: PostZen
    reports a URL and "published" seconds after a draft lands in the TikTok app (Content Studio audit, 2026-10-27)."""
    status = ep["platform_status"] or ""
    if ep["publish_mode"] == "draft" and ep["postzen_post_id"] in (live or {}):
        return "live (public views on TikTok)"
    if ep["publish_mode"] == "draft" and ep["state"] in ("POSTED", "MEASURED"):
        return "live (you recorded it as posted)"
    if ep["publish_mode"] == "draft" and status == "published":
        due = ep["post_date"] and slot_time_str(ep) <= dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return ("in your TikTok drafts: its time has passed, post it from the app with the AI label" if due
                else "in TikTok drafts, waiting for you to post it")
    if ep["publish_mode"] == "draft" and status in ("scheduled", "queued", "pending"):
        return "goes to your TikTok drafts at its time"
    if paused(ep):
        return "paused in PostZen"
    return status or ("posted" if ep["state"] == "POSTED" else "")


def slot_time_str(ep):
    return content.slot_utc(ep["post_date"], ep["slot"])


def _send(con, ep, body, key, mode_label, scheduled_for):
    """Send to PostZen with a publish-job record written before and after the call, so a failure or a crash leaves
    a trace. The video is uploaded once (content.media_uploads) and reused on retries."""
    cid = f"TT-{ep['id']}"
    ccon = content.connect()
    try:
        url, digest = content.upload_media(ccon, HUB / ep["video_path"], pz)
        body["mediaItems"] = [{"url": url}]
        content.record_publish(ccon, cid, "tiktok", mode_label, key, asset_sha256=digest,
                               caption_sha256=content.sha256_text(ep["caption"]), scheduled_for=scheduled_for,
                               submitted_at=content.now_utc(), state="submitting", attempt=1, error=None)
        try:
            res = pz.post("posts", body, idempotency_key=key)
        except Exception as e:
            content.record_publish(ccon, cid, "tiktok", mode_label, key, state="failed", error=f"{type(e).__name__}: {e}"[:500])
            raise
        post = res.get("post") or res.get("existingPost") or {}
        content.record_publish(ccon, cid, "tiktok", mode_label, key, postzen_post_id=post.get("_id"), state="submitted",
                               platform_status=post.get("status"), evidence="PostZen accepted the request")
        return post
    finally:
        ccon.close()


def store_pieces(ep, b):
    """Shopify product ids of the Ember & Clove pieces in the episode (outfit store pieces and the product)."""
    pieces = content._wardrobe_products(b)
    out = [pieces[o][0] for o in json.loads(ep["outfit_json"] or "[]") if o in pieces]
    prod = next((p for p in b["products"].items if p.id == ep["product_id"]), None) if ep["product_id"] else None
    return out + ([prod.shopify_gid] if prod else [])


def release_checks(con, ep, b):
    """Content Studio Phase D, right before anything goes to PostZen: the video and caption are exactly the ones
    approved (sha256 bound at `approve` and `schedule`), the caption passes the shared rules (scripts/studio/checks.py)
    and every store piece is live and in stock. Critical findings block; high ones block unless the owner accepted
    them for this exact file and caption."""
    f = HUB / (ep["video_path"] or "").replace("\\", "/")
    asset = content.sha256_file(f) if ep["video_path"] and f.exists() else None
    cap = content.sha256_text(ep["caption"]) if ep["caption"] else None
    found = (checks.binding_findings(json.loads(ep["approval_json"] or "null"), asset, cap)
             + checks.text_findings(ep["caption"] or "") + checks.availability(store_pieces(ep, b)))
    content.ensure_schema(con)  # the content tables live in the same studio.db
    blocking = checks.unresolved(found, checks.overrides(con, f"TT-{ep['id']}"), asset, cap)
    if blocking:
        raise db.GateError(f"{ep['id']} held: {checks.describe(blocking)}")


def publish(con, ep, b, mode, actor, quote, now=False, existing=None):
    """now (draft mode only): send it to the TikTok app's drafts right away instead of at the slot. A paused post can
    go to TikTok drafts (now or at its slot); its paused PostZen draft stays as it is. existing: a PostZen post
    already sent to drafts, recorded instead of sending again."""
    if mode not in SETTINGS:
        raise db.GateError(f"mode must be one of {', '.join(SETTINGS)}")
    if (now or existing) and mode != "draft":
        raise db.GateError("only draft mode can go now; scheduled mode posts publicly at its slot")
    if existing and not now:
        raise db.GateError("--existing goes with --now")
    if ep["state"] != "SCHEDULED" or ep["test"]:
        raise db.GateError(f"{ep['id']} is {ep['state']}{' (test)' if ep['test'] else ''}; only approved, scheduled "
                           "episodes go to TikTok")
    replaced = ""
    if ep["postzen_post_id"]:
        if not (mode == "draft" and paused(ep)):
            raise db.GateError(f"{ep['id']} is already with PostZen ({ep['postzen_post_id']}, {ep['publish_mode']})")
        replaced = f"; paused PostZen draft {ep['postzen_post_id']} kept"
    if now:
        if existing:
            post = pz.get(f"posts/{existing}").get("post") or {}
            target = next(iter(post.get("platforms") or []), {})
            acc = target.get("accountId")
            if (acc.get("_id") if isinstance(acc, dict) else acc) != account_id() \
                    or not (target.get("settings") or {}).get("uploadAsDraft") or post.get("content") != ep["caption"]:
                raise db.GateError(f"PostZen post {existing} isn't a TikTok draft upload of {ep['id']}'s caption")
        else:
            release_checks(con, ep, b)
            body = {"content": ep["caption"] or "", "publishNow": True, "timezone": b["rules"].posting.timezone,
                    "platforms": [{"platform": "tiktok", "accountId": account_id(), "settings": SETTINGS[mode]}]}
            post = _send(con, ep, body, f"{ep['id']}-draft-now", "tiktok_draft", content.now_utc())
        return db.note(con, ep["id"], f"sent to the TikTok app's drafts now{replaced}",
                       postzen_post_id=post.get("_id"), publish_mode=mode,
                       platform_status=post.get("status") or "queued")
    if mode == "scheduled" and (actor != "owner" or not quote):
        raise db.GateError("scheduled mode posts publicly by itself: owner only, with their words")
    # PostZen can't set TikTok's AI-generated label and captions no longer carry #aigenerated (owner 2026-10-28),
    # so AI videos go to drafts, where the owner switches the label on when posting.
    if mode == "scheduled":
        raise db.GateError(f"{ep['id']}: a scheduled post can't carry TikTok's AI label; send it to drafts instead")
    local, when = slot_time(ep, b)
    if local <= dt.datetime.now(local.tzinfo) + dt.timedelta(minutes=2):
        raise db.GateError(f"{ep['id']}'s slot {local:%Y-%m-%d %H:%M} has passed; re-plan it")
    release_checks(con, ep, b)
    body = {"content": ep["caption"] or "", "scheduledFor": when, "timezone": b["rules"].posting.timezone,
            "platforms": [{"platform": "tiktok", "accountId": account_id(), "settings": SETTINGS[mode]}]}
    post = _send(con, ep, body, f"{ep['id']}-{mode}", f"tiktok_{mode}", when)
    reason = (f"sent to PostZen ({mode}) for {local:%a %b %d %H:%M %Z}" + (f" (owner: {quote})" if quote else "")
              + replaced)
    return db.note(con, ep["id"], reason, postzen_post_id=post.get("_id"), publish_mode=mode,
                   platform_status=post.get("status") or "scheduled")


METRICS = ("views", "impressions", "reach", "likes", "comments", "shares", "saves", "clicks")  # PostZen AnalyticsMetrics


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")


def _write_csv(name, columns, rows):
    """Tables that can be empty (no TikTok videos yet) go out as CSV: the header keeps an empty table readable."""
    import csv
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def sync(con, b):
    """Refresh PostZen statuses, then write the dashboard's data files. Returns a one-line summary per file."""
    now = db.now()
    acc = account_id()
    pulled = pz.sync_external(acc)
    skipped = []
    for ep in [dict(r) for r in con.execute("SELECT * FROM episodes WHERE postzen_post_id IS NOT NULL AND test = 0")]:
        try:  # one failed status check is skipped (and reported), not fatal for the whole sync
            post = pz.get(f"posts/{ep['postzen_post_id']}").get("post") or {}
        except RuntimeError as e:
            skipped.append(f"{ep['id']}: {str(e)[:80]}")
            continue
        target = next(iter(post.get("platforms") or []), {})
        status = target.get("status") or post.get("status")
        url = target.get("platformPostUrl")
        if status != ep["platform_status"] or (url and url != ep["post_url"]):
            db.note(con, ep["id"], f"PostZen status {status}", platform_status=status, post_url=url or ep["post_url"])

    eps = [dict(r) for r in con.execute("SELECT * FROM episodes WHERE test = 0 ORDER BY post_date, slot")]
    live = content.tiktok_live_evidence(OUT)  # public evidence from the last analytics pull
    b_items = {i.id: i for i in b["wardrobe"].items}
    rooms = {r.id: r.name for r in b["world"].rooms}
    series = {s.id: s.name for s in b["series"].items}
    schedule = []
    for e in eps:
        outfit = json.loads(e["outfit_json"] or "[]")
        piece = next((b_items[o] for o in outfit if o in b_items and b_items[o].store_product), None)
        schedule.append({
            "episode": e["id"], "date": e["post_date"], "time": e["slot"],
            "weekday": dt.date.fromisoformat(e["post_date"]).strftime("%a"),
            "series": series.get(e["series_id"], e["series_id"]), "location": rooms.get(e["room_id"], e["room_id"]),
            "store_piece": f"{piece.name} ({piece.color})" if piece else "", "stage": e["state"],
            "tiktok": tiktok_label(e, live),
            "send_mode": e["publish_mode"] or "", "caption": e["caption"] or "", "post_url": e["post_url"] or "",
            "cost_usd": round(e["cost_usd"] or 0, 2)})
    _write("schedule", schedule)

    stats = pz.get("accounts/follower-stats", accountIds=acc)
    followers = [{"date": p["date"][:10], "followers": p["followers"]} for p in (stats.get("stats") or {}).get(acc, [])]
    _write("followers", followers)

    episode_of = {e["postzen_post_id"]: e["id"] for e in eps if e["postzen_post_id"]}
    posts, page = [], 1
    while True:
        a = pz.get("analytics", platform="tiktok", accountId=acc, limit=100, page=page)
        for p in a.get("posts") or []:
            m = p.get("analytics") or p.get("metrics") or p
            pid = p.get("postzenPostId") or p.get("postId") or p.get("_id") or p.get("platformPostId")
            posts.append({
                "post_id": pid, "episode": episode_of.get(pid) or episode_of.get(p.get("postId")) or "",
                "published": (p.get("publishedAt") or p.get("createdAt") or "")[:10],
                "caption": (p.get("content") or "(posted directly on TikTok)")[:120], "url": p.get("platformPostUrl") or "",
                **{k: _num(m.get(k)) for k in METRICS}, "source": "external" if p.get("isExternal") else "postzen"})
        if page >= ((a.get("pagination") or {}).get("totalPages") or 1):
            break
        page += 1
    _write_csv("tiktok_videos", ["post_id", "episode", "published", "caption", "url", *METRICS, "source"], posts)

    # Day-by-day numbers for each of our posts that has gone live (PostZen has none before then).
    timeline = []
    for e in eps:
        if not e["postzen_post_id"] or (e["publish_mode"] == "draft" and not e["post_url"]) \
                or (e["platform_status"] or "scheduled") in ("scheduled", "pending", "draft"):
            continue
        try:
            t = pz.get("analytics/post-timeline", postId=e["postzen_post_id"])
        except RuntimeError as err:
            print(f"  timeline {e['id']}: {err}")
            continue
        timeline += [{"episode": e["id"], "date": (d.get("date") or "")[:10], **{k: _num(d.get(k)) for k in METRICS}}
                     for d in t.get("timeline") or []]
    _write_csv("post_timeline", ["episode", "date", *METRICS], timeline)

    daily = pz.get("analytics/daily-metrics", platform="tiktok", accountId=acc)
    _write_csv("daily_metrics", ["date", *METRICS, "posts"],
               [{"date": (d.get("date") or "")[:10], **{k: _num((d.get("metrics") or d).get(k)) for k in METRICS},
                 "posts": _num(d.get("postCount"))}
                for d in daily.get("dailyData") or []])

    g = b["rules"].generation
    spend = [{"date": r[0], "usd": round(r[1], 2), "videos": r[2]} for r in con.execute(
        "SELECT substr(at, 1, 10), SUM(usd), SUM(CASE WHEN usd > 0.5 THEN 1 ELSE 0 END) FROM spend "
        "GROUP BY substr(at, 1, 10) ORDER BY 1")]
    _write("spend", spend)
    _write("caps", [{"cap": "per video", "usd": g.max_usd_per_video}, {"cap": "per day", "usd": g.max_usd_per_day},
                    {"cap": "per week", "usd": g.max_usd_per_week}])
    (OUT / "synced_at.txt").write_text(now, encoding="utf-8")
    return [f"pulled from TikTok: {pulled}"] + [f"status check skipped {s}" for s in skipped] + [
            f"schedule {len(schedule)}", f"followers {len(followers)}",
            f"tiktok_videos {len(posts)}",
            f"post_timeline {len(timeline)}",
            f"daily_metrics {len(daily.get('dailyData') or [])}", f"spend {len(spend)}", "caps 3"]
