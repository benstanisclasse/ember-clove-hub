"""Facebook AI-picture posts, made and tracked in the database (Content Studio 2.0, Phase D).

Replaces the hand-assembled week of 2026-10-28 (plan file -> prompt JSON -> image batch -> upload -> editing the plan
JSON by hand). Every post is a row in studio.db (`fb_ai_posts` + `content_items`) and walks these steps; nothing is
edited by hand and every step is recorded as a content_event:

  plan      planned            products, slots and captions from facebook_photos.plan (same rules: season, no repeats,
                               outfit every Nth post); caption ends #aigenerated; scene from the product type
  scene     planned            optional: a custom scene for one post (the rest of the prompt is the template)
  generate  image_generated    Higgsfield image from the post's supplier photos (template studio/templates/
                               fb_ai_picture.j2); the generation job is recorded (Phase C)
  review    -                  side-by-side sheet: each AI picture next to the product's supplier photos
  verdict   captioned |        product-fidelity check of this exact file (sha256): product matches, no added text or
            fidelity_failed    logos, no face that looks like a real person. Owner 2026-10-27: "i dont need to approve
                               every image i approve do it" -> Claude checks; a failed picture is held, `generate`
                               makes a new one
  qa        awaiting_approval  shared rules (scripts/studio/checks.py): caption wording, #aigenerated, every product
            | qa_failed        ACTIVE and in stock, the file present and the one that passed the fidelity check
  approve   approved           {quote, actor, at, asset_sha256, caption_sha256}: bound to this file and caption
  schedule  scheduled          hashes and availability checked again, image uploaded once, sent to PostZen
  sync      public / failed    PostZen status (run by facebook_photos.py sync, the dashboard's facebook job)

  python -I scripts/studio/fb_ai.py plan --start 2026-11-04 --days 7
  python -I scripts/studio/fb_ai.py scene FB-2026-11-04-03 "She wears ..."
  python -I scripts/studio/fb_ai.py generate --week 2026-11-04 [--ids FB-...]
  python -I scripts/studio/fb_ai.py review --week 2026-11-04
  python -I scripts/studio/fb_ai.py verdict FB-2026-11-04-03 --pass  |  --fail "the print is wrong"
  python -I scripts/studio/fb_ai.py qa --week 2026-11-04
  python -I scripts/studio/fb_ai.py approve --week 2026-11-04 --quote "owner's words"
  python -I scripts/studio/fb_ai.py schedule --week 2026-11-04
  python -I scripts/studio/fb_ai.py board --week 2026-11-04
"""
import argparse
import datetime as dt
import html
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HUB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HUB / "scripts"))
from studio import checks, content  # noqa: E402

TEMPLATE = "fb_ai_picture.j2"
MODEL = "flare"
OUT = HUB / "data" / "media_generated" / "fb_ai"
STANDING_QUOTE = "i dont need to approve every image i approve do it"  # owner, 2026-10-27 (memory + log.md)
FIDELITY_CHECKS = ("product_match", "no_text_or_logos", "no_real_person_face")
SETTINGS = ["standing by a big window in a bright apartment with plants",
            "walking along a leafy city sidewalk on a crisp autumn afternoon",
            "sitting at a small café table by the window",
            "in a cozy living room with warm lamp light in the evening",
            "on a front porch with fallen leaves on the steps",
            "in a bright kitchen in the morning, holding a coffee mug"]
CLOSE_TYPES = {"Shoes", "Sandals", "Boots", "Slippers", "Sneakers"}
TOP_TYPES = {"Accessories", "Jewelry"}


# --- records -------------------------------------------------------------------------------------------------------

def _row(con, cid):
    r = con.execute("SELECT * FROM fb_ai_posts WHERE content_id = ?", (cid,)).fetchone()
    if r is None:
        raise SystemExit(f"{cid}: not a Facebook AI-picture post made in the database")
    return dict(r)


def _week(con, week, ids=None):
    rows = [dict(r) for r in con.execute("SELECT * FROM fb_ai_posts WHERE week = ? ORDER BY content_id", (week,))]
    return [r for r in rows if not ids or r["content_id"] in ids]


def _update(con, cid, **fields):
    con.execute(f"UPDATE fb_ai_posts SET {', '.join(f'{k} = ?' for k in fields)} WHERE content_id = ?",
                [*fields.values(), cid])


def _state(con, cid):
    r = con.execute("SELECT state FROM content_items WHERE content_id = ?", (cid,)).fetchone()
    return r["state"] if r else None


def save(con, cid, state, reason, actor="claude"):
    """Mirror the post into content_items (state change recorded as a content_event) and its products/assets."""
    p = _row(con, cid)
    content.upsert_item(con, {
        "content_id": cid, "channel": "facebook", "kind": "fb_ai_picture", "workflow": "fb_ai_picture", "state": state,
        "title": " + ".join(json.loads(p["titles"])), "series": "fb_outfit" if p["kind"] == "outfit" else "fb_product",
        "concept": p["kind"], "cta_type": "link", "caption": p["caption"],
        "link_placement": "first_comment" if p["first_comment"] else "caption",
        "ai_disclosure": int("#aigenerated" in (p["caption"] or "").lower()),
        "scheduled_at": content.slot_utc(p["date"], p["slot"]), "slot_local": f"{p['date']} {p['slot']}",
        "approval_json": p["approval_json"], "test": 0}, actor=actor, reason=reason)
    gids = content._handle_gids()
    role = "outfit_piece" if p["kind"] == "outfit" else "featured"
    assets = [{"kind": "image", "url": u, "source": "supplier"} for u in json.loads(p["supplier_photos"])]
    if p["image_path"]:
        assets.append({"kind": "image", "path": p["image_path"], "url": p["image_url"], "sha256": p["image_sha256"],
                       "source": "ai_generated"})
    content.set_children(con, cid, [(h, gids.get(h), role) for h in json.loads(p["products"])], assets)
    con.commit()


# --- plan ----------------------------------------------------------------------------------------------------------

def default_scene(post, product_types, n):
    """A plain scene from the product type, rotated by post number; `scene` replaces it for one post."""
    setting = SETTINGS[n % len(SETTINGS)]
    titles = [t.lower() for t in post["titles"]]
    if post["kind"] == "outfit":
        return (f"She wears these exact pieces together as one outfit: {', '.join(titles[:-1])} and {titles[-1]}, "
                f"{setting}, full-length framing, relaxed natural pose.")
    ptype = product_types.get(post["products"][0], "")
    framing = ("close-up from the knees down" if ptype in CLOSE_TYPES or any(w in titles[0] for w in ("shoe", "boot", "sandal", "slipper", "sneaker"))
               else "close-up from the shoulders up" if ptype in TOP_TYPES else "framed from mid-thigh up")
    return f"She wears this exact {titles[0]}, {setting}, {framing}, relaxed natural pose."


def plan_week(con, start, days, products, rules, history):
    """Create the week's posts (state planned). Refuses a week that already has posts in the database or a plan file."""
    import facebook_photos as fp
    week = start.isoformat()
    if con.execute("SELECT 1 FROM content_items WHERE content_id LIKE ?", (f"FB-{week}-%",)).fetchone() \
            or (fp.DIR / f"plan_{week}.json").exists():
        raise SystemExit(f"week {week} already has Facebook posts; pick another start date")
    posts = fp.plan(start, days, rules, products, history)
    types = {p["handle"]: p["product_type"] for p in products}
    for n, p in enumerate(posts):
        caption = p["caption"].rstrip() + "\n\n#aigenerated"
        con.execute("INSERT INTO fb_ai_posts (content_id, week, date, slot, kind, products, titles, supplier_photos, "
                    "scene, caption, first_comment, caption_format, question) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (p["content_id"], week, p["date"], p["slot"], p["kind"], json.dumps(p["products"]),
                     json.dumps(p["titles"]), json.dumps(p["photos"]), default_scene(p, types, n), caption,
                     p["first_comment"], p.get("caption_format"), p.get("question")))
        save(con, p["content_id"], "planned", "planned (fb_ai plan)")
    return posts


def render_prompt(scene):
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    env = Environment(loader=FileSystemLoader(str(content.TEMPLATES)), undefined=StrictUndefined)
    text = env.get_template(TEMPLATE).render(scene=scene).strip()
    return text, content.sha256_text(text)[:16]


# --- generate ------------------------------------------------------------------------------------------------------

def generate(con, cid, hf=None, model=MODEL):
    """One Higgsfield image for the post; the job is recorded before the call and closed after it."""
    import hf_api
    from hf_image_edit import MODELS
    hf = hf or hf_api
    p = _row(con, cid)
    if _state(con, cid) not in ("planned", "image_generated", "fidelity_failed", "captioned", "qa_failed"):
        raise SystemExit(f"{cid} is {_state(con, cid)}; only posts not yet approved get a new picture")
    path, payload = MODELS[model]
    prompt, phash = render_prompt(p["scene"])
    refs = json.loads(p["supplier_photos"])[:4]
    jid = content.start_job(con, cid, "image", "higgsfield", path, {"aspect": "3:4", "model_key": model},
                            template=TEMPLATE, prompt_hash=phash, prompt_text=prompt, refs=refs)
    try:
        sub = hf.submit(path, payload(prompt, refs, "3:4"))
        status = hf.wait(sub["status_url"], every=5, timeout_s=600)
        url = (status.get("images") or [{}])[0].get("url") if status.get("status") == "completed" else None
        if not url:
            raise RuntimeError(f"Higgsfield status {status.get('status')}")
        dest = OUT / p["week"] / f"{cid}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        hf.download(url, dest)
    except Exception as e:
        content.finish_job(con, jid, "failed", error=f"{type(e).__name__}: {e}")
        raise
    content.finish_job(con, jid, "completed", sub.get("request_id"), None, "not reported", output_path=dest, output_url=url)
    rel = str(dest.relative_to(HUB)).replace("\\", "/")
    _update(con, cid, prompt=prompt, prompt_hash=phash, image_path=rel, image_sha256=content.sha256_file(dest),
            image_url=None, fidelity_json=None, checks_json=None, approval_json=None)
    save(con, cid, "image_generated", f"picture generated (job {jid})")
    return dest


# --- product fidelity ----------------------------------------------------------------------------------------------

def verdict(con, cid, passed, reason=None, actor="claude", failed_checks=()):
    p = _row(con, cid)
    if _state(con, cid) not in ("image_generated", "fidelity_failed", "captioned", "qa_failed"):
        raise SystemExit(f"{cid} is {_state(con, cid)}; a verdict needs a generated picture")
    f = HUB / (p["image_path"] or "")
    if not p["image_path"] or not f.exists() or content.sha256_file(f) != p["image_sha256"]:
        raise SystemExit(f"{cid}: the picture is missing or changed since it was generated; generate again")
    if not passed and not reason:
        raise SystemExit("a failed verdict needs a reason")
    record = {"verdict": "pass" if passed else "fail", "reason": reason, "actor": actor, "at": content.now_utc(),
              "image_sha256": p["image_sha256"],
              "checks": {c: (passed or c not in failed_checks) for c in FIDELITY_CHECKS}}
    _update(con, cid, fidelity_json=json.dumps(record))
    save(con, cid, "captioned" if passed else "fidelity_failed",
         "product fidelity: pass" if passed else f"product fidelity: fail ({reason})", actor=actor)


def review_sheet(con, week, path=None):
    """The AI picture beside the product's supplier photos, with its caption and where it stands."""
    rows = _week(con, week)
    path = path or content.FB_DIR / f"review_ai_{week}.html"
    cards = []
    for p in rows:
        img = os.path.relpath(HUB / p["image_path"], path.parent).replace("\\", "/") if p["image_path"] else None
        sup = "".join(f'<img src="{u}?width=300" alt="supplier photo">' for u in json.loads(p["supplier_photos"]))
        fid = json.loads(p["fidelity_json"] or "{}")
        cards.append(f'<section><h2>{p["content_id"]} · {p["date"]} {p["slot"]} <small>{_state(con, p["content_id"])}'
                     f'{" · fidelity " + fid["verdict"] if fid else ""}</small></h2><div class="imgs">'
                     f'{f"<img class=ai src={img!r} alt=AI picture>" if img else "<p>no picture yet</p>"}{sup}</div>'
                     f'<pre>{html.escape(p["caption"] or "")}</pre></section>')
    path.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>AI pictures review</title><style>
body{{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#f7f5f2;color:#24201d}}
section{{background:#fff;border:1px solid #e4ded7;border-radius:10px;padding:12px;margin:0 0 14px}}
h2{{font-size:1rem;margin:0 0 8px}} small{{color:#6f665f;font-weight:400}} .imgs{{display:flex;gap:6px;overflow-x:auto}}
.imgs img{{height:220px;border-radius:6px}} .imgs img.ai{{outline:3px solid #b5651d}}
pre{{white-space:pre-wrap;font:inherit;margin:10px 0 0}}</style></head><body>
<h1>Facebook AI pictures, week of {week}: the AI picture (outlined) beside the supplier photos</h1>
{''.join(cards)}</body></html>""", encoding="utf-8")
    return path


# --- QA, approval, scheduling --------------------------------------------------------------------------------------

def post_findings(con, p, analytics_path=None):
    """Everything the shared rule module knows about this post right now."""
    f = HUB / (p["image_path"] or "")
    sha = content.sha256_file(f) if p["image_path"] and f.exists() else None
    fid = json.loads(p["fidelity_json"] or "{}")
    found = (checks.text_findings(f"{p['caption'] or ''}\n{p['first_comment'] or ''}")
             + checks.disclosure_findings(p["caption"], True)
             + checks.availability(json.loads(p["products"]), analytics_path))
    if sha is None:
        found.append(checks.finding("critical", "media_missing", "the picture file is missing"))
    elif fid.get("verdict") != "pass" or fid.get("image_sha256") != sha:
        found.append(checks.finding("critical", "media_changed", "this file has not passed the product-fidelity check"))
    if f"utm_content={p['content_id']}" not in f"{p['caption']}{p['first_comment'] or ''}":
        found.append(checks.finding("medium", "untracked_link", "the store link doesn't carry this post's content id"))
    return found, sha


def qa(con, cid, analytics_path=None):
    p = _row(con, cid)
    if _state(con, cid) not in ("captioned", "qa_failed", "awaiting_approval"):
        raise SystemExit(f"{cid} is {_state(con, cid)}; QA runs after a passed fidelity check")
    found, sha = post_findings(con, p, analytics_path)
    cap = content.sha256_text(p["caption"])
    blocking = checks.unresolved(found, checks.overrides(con, cid), sha, cap)
    _update(con, cid, checks_json=json.dumps({"at": content.now_utc(), "findings": found, "blocking": blocking}))
    save(con, cid, "qa_failed" if blocking else "awaiting_approval",
         f"QA: {checks.describe(blocking)}" if blocking else f"QA passed ({len(found)} note(s))")
    return blocking


def approve(con, cid, quote, actor="claude"):
    """Bound to this exact picture and caption. Claude approves under the owner's standing instruction for Facebook
    AI pictures; anyone else's approval is the owner's own, with their words."""
    if not (quote or "").strip():
        raise SystemExit("approval needs the owner's words (--quote)")
    if actor != "owner" and STANDING_QUOTE not in quote.lower():
        raise SystemExit(f"Claude approves Facebook AI pictures only under the owner's standing instruction "
                         f"({STANDING_QUOTE!r}); otherwise the owner approves with --actor owner")
    p = _row(con, cid)
    if _state(con, cid) != "awaiting_approval":
        raise SystemExit(f"{cid} is {_state(con, cid)}; only posts that passed QA can be approved")
    approval = {"quote": quote, "actor": actor, "at": content.now_utc(), "asset_sha256": p["image_sha256"],
                "caption_sha256": content.sha256_text(p["caption"]),
                "basis": "owner's standing instruction for Facebook AI pictures (2026-10-27)" if actor != "owner"
                else "owner"}
    _update(con, cid, approval_json=json.dumps(approval))
    save(con, cid, "approved", f"approved ({approval['basis']}): {quote}", actor=actor)


def schedule(con, cid, pz=None, rules=None, account=None, analytics_path=None, now=None):
    """Send one approved post to PostZen for its slot. Refused (and left approved) when anything changed since the
    approval, a rule now fails, a product went inactive or out of stock, or the slot has passed."""
    import facebook_photos as fp
    if pz is None:
        import postzen as pz
    rules = rules or fp.load_rules()
    p = _row(con, cid)
    if _state(con, cid) != "approved" or p["postzen_post_id"]:
        raise SystemExit(f"{cid} is {_state(con, cid)}; only approved posts not yet sent can be scheduled")
    tz = ZoneInfo(rules["timezone"])
    local = dt.datetime.fromisoformat(f"{p['date']}T{p['slot']}").replace(tzinfo=tz)
    if local <= (now or dt.datetime.now(tz)) + dt.timedelta(minutes=5):
        raise SystemExit(f"{cid}: slot {p['date']} {p['slot']} has passed; re-plan it")
    found, sha = post_findings(con, p, analytics_path)
    cap = content.sha256_text(p["caption"])
    found += checks.binding_findings(json.loads(p["approval_json"] or "null"), sha, cap)
    blocking = checks.unresolved(found, checks.overrides(con, cid), sha, cap)
    if blocking:
        content.add_event(con, cid, "approved", "approved", "studio", f"held at scheduling: {checks.describe(blocking)}")
        con.commit()
        raise SystemExit(f"{cid} held: {checks.describe(blocking)}")
    url, digest = content.upload_media(con, HUB / p["image_path"], pz)
    when = local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    acc = account or __import__("hub_env").load_config()["postzen"]["facebook_account_id"]
    body = {"content": p["caption"], "scheduledFor": when, "timezone": rules["timezone"], "mediaItems": [{"url": url}],
            "platforms": [{"platform": "facebook", "accountId": acc,
                           "settings": {"firstComment": p["first_comment"]} if p["first_comment"] else {}}]}
    key = f"fbai-{cid}"
    content.record_publish(con, cid, "facebook", "fb_scheduled", key, asset_sha256=digest, caption_sha256=cap,
                           scheduled_for=when, submitted_at=content.now_utc(), state="submitting", attempt=1, error=None)
    try:
        res = pz.post("posts", body, idempotency_key=key)
    except Exception as e:
        content.record_publish(con, cid, "facebook", "fb_scheduled", key, state="failed", error=f"{type(e).__name__}: {e}"[:500])
        raise
    post = res.get("post") or res.get("existingPost") or {}
    state, evidence = content.fb_publish_state(post.get("status") or "scheduled", None)
    content.record_publish(con, cid, "facebook", "fb_scheduled", key, postzen_post_id=post.get("_id"), state=state,
                           platform_status=post.get("status"), evidence="PostZen accepted the request")
    _update(con, cid, image_url=url, postzen_post_id=post.get("_id"), status=post.get("status") or "scheduled")
    save(con, cid, "scheduled", f"sent to PostZen for {local:%a %b %d %H:%M %Z} ({post.get('_id')})")
    history = fp.load_history()
    history.append({"date": p["date"], "slot": p["slot"], "products": json.loads(p["products"]),
                    "postzen_post_id": post.get("_id"), "ai_picture": True, "content_id": cid,
                    "caption_format": p["caption_format"], "question": p["question"]})
    content.atomic_write(fp.HISTORY, json.dumps(history, ensure_ascii=False, indent=1))
    return post


# --- sync (dashboard job) ------------------------------------------------------------------------------------------

def refresh(con, pz):
    """PostZen status and post link for every sent database post; a status change is recorded as an event."""
    n = 0
    for p in [dict(r) for r in con.execute("SELECT * FROM fb_ai_posts WHERE postzen_post_id IS NOT NULL")]:
        try:
            post = pz.get(f"posts/{p['postzen_post_id']}").get("post") or {}
        except RuntimeError:
            continue
        target = next(iter(post.get("platforms") or []), {})
        status, url = target.get("status") or post.get("status"), target.get("platformPostUrl")
        if status == p["status"] and (not url or url == p["post_url"]):
            continue
        _update(con, p["content_id"], status=status, post_url=url or p["post_url"])
        state, evidence = content.fb_publish_state(status, url or p["post_url"])
        content.record_publish(con, p["content_id"], "facebook", "fb_scheduled", f"fbai-{p['content_id']}",
                               platform_post_url=url or p["post_url"], state=state, evidence=evidence,
                               platform_status=status, last_checked_at=content.now_utc())
        save(con, p["content_id"], state, f"PostZen status {status}", actor="studio")
        n += 1
    return n


def schedule_rows(con):
    """Rows for the dashboard's fb_schedule.json, same shape as the plan-file posts."""
    out = []
    for p in con.execute("SELECT * FROM fb_ai_posts"):
        out.append({"date": p["date"], "time": p["slot"], "weekday": dt.date.fromisoformat(p["date"]).strftime("%a"),
                    "kind": p["kind"], "products": " + ".join(json.loads(p["titles"])), "photos": 1,
                    "status": p["status"] or _state(con, p["content_id"]) or "planned", "post_url": p["post_url"] or ""})
    return out


def board(con, week):
    lines = []
    for p in _week(con, week):
        fid = json.loads(p["fidelity_json"] or "{}").get("verdict", "-")
        blocking = json.loads(p["checks_json"] or "{}").get("blocking") or []
        lines.append(f"{p['content_id']}  {p['date']} {p['slot']}  {_state(con, p['content_id']):18} fidelity {fid:4}  "
                     f"{', '.join(json.loads(p['titles']))[:50]}" + (f"  HELD: {checks.describe(blocking)}" if blocking else ""))
    return lines


def main():
    import facebook_photos as fp
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--start", required=True)
    p.add_argument("--days", type=int, default=7)
    p = sub.add_parser("scene")
    p.add_argument("content_id")
    p.add_argument("text")
    for name in ("generate", "review", "qa", "approve", "schedule", "board"):
        p = sub.add_parser(name)
        p.add_argument("--week", required=True)
        p.add_argument("--ids", nargs="*")
        if name == "approve":
            p.add_argument("--quote", required=True)
            p.add_argument("--actor", default="claude")
    p = sub.add_parser("verdict")
    p.add_argument("content_id")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--pass", dest="passed", action="store_true")
    g.add_argument("--fail", dest="reason")
    p.add_argument("--failed-checks", nargs="*", default=[], choices=FIDELITY_CHECKS)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    con = content.connect()
    if args.cmd == "plan":
        posts = plan_week(con, dt.date.fromisoformat(args.start), args.days, fp.fetch_products(), fp.load_rules(),
                          fp.load_history())
        print(f"{len(posts)} posts planned for the week of {args.start} (state planned); nothing generated or sent")
    elif args.cmd == "scene":
        if _state(con, args.content_id) not in ("planned", "image_generated", "fidelity_failed"):
            raise SystemExit(f"{args.content_id} is {_state(con, args.content_id)}; the scene can't change now")
        _update(con, args.content_id, scene=args.text)
        content.add_event(con, args.content_id, None, None, "claude", f"scene set: {args.text}")
        con.commit()
        print(f"{args.content_id}: scene set; generate to make the picture")
    elif args.cmd == "verdict":
        verdict(con, args.content_id, args.passed, args.reason, failed_checks=args.failed_checks)
        print(f"{args.content_id}: {_state(con, args.content_id)}")
    elif args.cmd == "review":
        print(f"review sheet: {review_sheet(con, args.week).relative_to(HUB)}")
    elif args.cmd == "board":
        print("\n".join(board(con, args.week)) or "no posts for that week")
    else:
        for r in _week(con, args.week, args.ids):
            cid = r["content_id"]
            try:
                if args.cmd == "generate" and _state(con, cid) in ("planned", "fidelity_failed"):
                    print(f"{cid}: {generate(con, cid).relative_to(HUB)}")
                elif args.cmd == "qa" and _state(con, cid) in ("captioned", "qa_failed"):
                    blocking = qa(con, cid)
                    print(f"{cid}: {'HELD ' + checks.describe(blocking) if blocking else 'passed'}")
                elif args.cmd == "approve" and _state(con, cid) == "awaiting_approval":
                    approve(con, cid, args.quote, args.actor)
                    print(f"{cid}: approved")
                elif args.cmd == "schedule" and _state(con, cid) == "approved":
                    post = schedule(con, cid)
                    print(f"{cid}: scheduled ({post.get('_id')})")
            except SystemExit as e:
                print(f"{cid}: {e}")
    con.close()


if __name__ == "__main__":
    main()
