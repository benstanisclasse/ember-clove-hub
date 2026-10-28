"""Facebook Page photo posts through PostZen: real supplier photos or owner-approved AI pictures.

Owner 2026-10-27: the Facebook Page posts pictures only (no videos, no Ember backstory), 2 posts on weekdays and 1 on
weekends. Products come from the store's public feed (emberandclove.com/products.json). The planner picks the
supplier's real photos (32-character hex file names), each scanned for AI content credentials before use.
Owner 2026-10-27 (Content Studio Phase B): AI pictures are a standard post type, each approved by the owner; any post
whose photos are not real supplier photos (or that has an `ai_picture`) must carry #aigenerated in its caption, and
publish refuses it otherwise. Captions use the product's own description, never prices, delivery times or urgency.
The store link goes in the caption by default (rules.json "link_placement": "caption"; "first_comment" puts it in
the first comment instead).

Every send is recorded per post: the plan file and history are saved right after each post (atomically), a
publish job with the caption's hash is written to studio.db (scripts/studio/content.py) before and after the call,
and a failure is recorded on that job before the error stops the run. Each sent post carries its own approval
(owner's words, time, caption and photo hashes). `plan` refuses to overwrite a plan file that already has posts in
PostZen.

  python -I scripts/facebook_photos.py plan --start 2026-10-28 --days 7     plan posts + review sheet (nothing sent)
  python -I scripts/facebook_photos.py publish data/facebook/plan_2026-10-28.json --quote "owner's words"
  python -I scripts/facebook_photos.py auto                                  plan + publish next week (only if
                                                                              rules.json auto_publish is true)
Rules: data/facebook/rules.json. Every post sent is kept in data/facebook/history.json (no product repeats too soon).
"""
import argparse
import datetime as dt
import html
import json
import random
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hub_env  # noqa: E402

HUB = Path(__file__).resolve().parent.parent
DIR = HUB / "data" / "facebook"
RULES = DIR / "rules.json"
HISTORY = DIR / "history.json"
FEED = "https://emberandclove.com/products.json?limit=250&page={}"
REAL_PHOTO = re.compile(r"^[0-9A-Fa-f]{32}(_[0-9a-f-]+)?\.(jpe?g|png|webp)$")
NO_CAPTION = re.compile(r"\$|\bship|\bdeliver|\bsale\b|\bhurry\b|\blimited\b|\btoday only\b", re.I)


def load_rules():
    return json.loads(RULES.read_text(encoding="utf-8"))


def load_history():
    return json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []


def fetch_products():
    out, page = [], 1
    while True:
        req = urllib.request.Request(FEED.format(page), headers={"User-Agent": "Mozilla/5.0"})
        batch = json.load(urllib.request.urlopen(req, timeout=60))["products"]
        out += batch
        if len(batch) < 250:
            return out
        page += 1


def lead_sentence(body):
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body or ""))).strip()
    first = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0].strip()
    return "" if not first or NO_CAPTION.search(first) or len(first) > 220 else first


def real_photos(p):
    return [i["src"].split("?")[0] for i in p["images"] if REAL_PHOTO.match(i["src"].split("/")[-1].split("?")[0])]


# Content credentials and generator names that mark a file as AI-made. A photo carrying any of them is never posted:
# the Page posts real photos only, so it needs no AI label (Meta has no API switch for one).
AI_MARKERS = (b"trainedAlgorithmicMedia", b"c2pa", b"jumb", b"Midjourney", b"DALL-E", b"Stable Diffusion",
              b"Firefly", b"SynthID", b"AIGC")
CHECKS_FILE = DIR / "photo_checks.json"
_checks = None


def no_ai_marker(url):
    global _checks
    if _checks is None:
        _checks = json.loads(CHECKS_FILE.read_text(encoding="utf-8")) if CHECKS_FILE.exists() else {}
    if url not in _checks:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
        _checks[url] = not any(m in data for m in AI_MARKERS)
        CHECKS_FILE.write_text(json.dumps(_checks, indent=0), encoding="utf-8")
    return _checks[url]


def clean_photos(p, n):
    """Up to n of the product's real photos, each checked for AI markers."""
    out = []
    for u in real_photos(p):
        if len(out) == n:
            break
        if no_ai_marker(u):
            out.append(u)
    return out


def colors(p):
    return next((o["values"] for o in p["options"] if o["name"].lower() in ("color", "colour")), [])


def in_season(p, day, rules):
    md = day.strftime("%m-%d")
    cold = md >= rules["cold_season"][0] or md <= rules["cold_season"][1]
    tags = {t.lower() for t in p["tags"]}
    if cold:
        title = p["title"].lower()
        return (p["product_type"] not in rules["warm_only_types"] and not tags & set(rules["warm_only_tags"])
                and not any(w in title for w in rules["warm_only_title_words"]))
    return not tags & set(rules["cold_only_tags"])


def eligible(products, day, rules):
    keep = []
    for p in products:
        if p["vendor"] != rules["vendor"] or not p["product_type"] or p["handle"] in rules["skip_handles"]:
            continue
        if not in_season(p, day, rules) or len(real_photos(p)) < 1 or not lead_sentence(p["body_html"]):
            continue
        keep.append(p)
    return keep


def question(p, rng):
    t = p["product_type"]
    pool = ["How would you style it?", "Work or weekend?", "Dressed up or dressed down?",
            "What would you pair it with?"]
    if len(colors(p)) > 1:
        pool.append("Which color would you pick?")
    if t in ("Dresses", "Skirts"):
        pool.append("Boots or sneakers with this?")
    if t in ("Sweaters & Sweatshirts", "Outerwear"):
        pool.append("What would you wear it over?")
    if t == "Accessories":
        pool.append("Everyday piece or special occasion?")
    return rng.choice(pool)


def link(p, rules, day, slot, content_id=None):
    # Hub tracking convention (scripts/attribution.py): organic_social; posts before 2026-10-28 used "social".
    # utm_content = the post's content id (Content Studio Phase C), so store visits map straight back to the post;
    # older posts carry <date>_<HHMM>, which content.collect_links still maps.
    from attribution import tag_link
    return tag_link(f"{rules['store_url']}/products/{p['handle']}", "facebook_organic", "fb_photos",
                    content_id or f"{day}_{slot.replace(':', '')}")


def single_post(p, rules, rng, day, slot, content_id=None):
    photos = clean_photos(p, rules["max_photos"])
    if not photos:
        return None
    cols = colors(p)
    lines = [p["title"], "", lead_sentence(p["body_html"])]
    if len(cols) > 1:
        lines.append(f"In {len(cols)} colors." if len(cols) > 3 else f"In {', '.join(cols[:-1])} and {cols[-1]}.")
    lines += ["", question(p, rng)]
    shop = f"Shop it here: {link(p, rules, day, slot, content_id)}"
    if rules.get("link_placement", "caption") == "caption":
        return {"kind": "product", "products": [p["handle"]], "titles": [p["title"]], "photos": photos,
                "caption": "\n".join(lines + ["", shop]), "first_comment": None}
    return {"kind": "product", "products": [p["handle"]], "titles": [p["title"]], "photos": photos,
            "caption": "\n".join(lines), "first_comment": shop}


def outfit_post(parts, rules, day, slot, content_id=None):
    firsts = [clean_photos(p, 1) for p in parts]
    if not all(firsts):
        return None
    names = [p["title"] for p in parts]
    caption = "\n".join(["One outfit, three pieces:", *[f"• {n}" for n in names], "",
                         "Which piece would you wear first?"])
    comment = "Shop the pieces:\n" + "\n".join(f"{p['title']}: {link(p, rules, day, slot, content_id)}" for p in parts)
    if rules.get("link_placement", "caption") == "caption":
        caption, comment = f"{caption}\n\n{comment}", None
    return {"kind": "outfit", "products": [p["handle"] for p in parts], "titles": names,
            "photos": [f[0] for f in firsts], "caption": caption, "first_comment": comment}


def pick_outfit(pool, rng, used):
    by = lambda types: [p for p in pool if p["product_type"] in types and p["handle"] not in used]
    tops, bottoms = by({"Tops & Bodysuits", "Sweaters & Sweatshirts"}), by({"Skirts", "Jeans & Pants"})
    finish = by({"Outerwear", "Accessories", "Sandals"})
    if not (tops and bottoms and finish):
        return None
    return [rng.choice(tops), rng.choice(bottoms), rng.choice(finish)]


def plan(start, days, rules, products, history, seed=None):
    rng = random.Random(seed if seed is not None else start.isoformat())
    recent = {h for e in history if e["date"] >= (start - dt.timedelta(days=rules["no_repeat_days"])).isoformat()
              for h in e["products"]}
    posts, used, last_type = [], set(recent), None
    for n in range(days):
        day = start + dt.timedelta(days=n)
        pool = eligible(products, day, rules)
        slots = rules["slots_weekend"] if day.weekday() >= 5 else rules["slots_weekday"]
        for slot in slots:
            post = None
            cid = f"FB-{start.isoformat()}-{len(posts):02d}"  # the id content.py gives this post (plan start + index)
            if len(posts) % rules["outfit_every"] == rules["outfit_every"] - 1:
                parts = pick_outfit(pool, rng, used)
                post = parts and outfit_post(parts, rules, day.isoformat(), slot, cid)
            if not post:
                fresh = [p for p in pool if p["handle"] not in used and p["product_type"] != last_type]
                if not fresh:
                    fresh = [p for p in pool if p["handle"] not in used] or pool
                for p in rng.sample(fresh, len(fresh)):  # first product with a usable photo
                    post = single_post(p, rules, rng, day.isoformat(), slot, cid)
                    if post:
                        last_type = p["product_type"]
                        break
                if not post:
                    print(f"  {day} {slot}: no product with a usable photo; slot left empty")
                    continue
            used |= set(post["products"])
            posts.append({"date": day.isoformat(), "slot": slot, "content_id": cid, **post})
    return posts


def review_sheet(posts, path):
    cards = []
    for i, p in enumerate(posts, 1):
        imgs = "".join(f'<img src="{u}?width=360" alt="">' for u in p["photos"])
        cards.append(f'<section><h2>{i}. {dt.date.fromisoformat(p["date"]):%a %b %d} · {p["slot"]} ET '
                     f'<small>{p["kind"]}</small></h2><div class="imgs">{imgs}</div>'
                     f'<pre>{html.escape(p["caption"])}</pre><p class="c">First comment: '
                     f'{html.escape(p["first_comment"] or "none (link in the caption)")}</p></section>')
    path.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Facebook posts review</title><style>
body{{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#f7f5f2;color:#24201d}}
h1{{font-size:1.3rem}} section{{background:#fff;border:1px solid #e4ded7;border-radius:10px;padding:12px;margin:0 0 14px}}
h2{{font-size:1rem;margin:0 0 8px}} small{{color:#6f665f;font-weight:400}} .imgs{{display:flex;gap:6px;overflow-x:auto}}
.imgs img{{height:180px;border-radius:6px}} pre{{white-space:pre-wrap;font:inherit;margin:10px 0 4px}}
.c{{color:#6f665f;font-size:.85rem;word-break:break-all;margin:0}}</style></head><body>
<h1>Facebook Page posts: {posts[0]['date']} to {posts[-1]['date']} ({len(posts)} posts)</h1>
{''.join(cards)}</body></html>""", encoding="utf-8")


def is_ai_post(p):
    """A post counts as AI-made if it has an ai_picture or any photo that is not a real supplier photo."""
    return bool(p.get("ai_picture")) or any(not REAL_PHOTO.match(u.split("?")[0].rsplit("/", 1)[-1]) for u in p["photos"])


def publish(plan_path, quote):
    import postzen as pz
    from studio import content
    rules, history = load_rules(), load_history()
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    acc = hub_env.load_config()["postzen"]["facebook_account_id"]
    tz = ZoneInfo(rules["timezone"])
    con = content.connect()
    sent = 0
    try:
        for i, p in enumerate(data["posts"]):
            if p.get("postzen_post_id"):
                continue
            local = dt.datetime.fromisoformat(f"{p['date']}T{p['slot']}").replace(tzinfo=tz)
            if local <= dt.datetime.now(tz) + dt.timedelta(minutes=5):
                print(f"  skip {p['date']} {p['slot']}: slot has passed")
                continue
            if is_ai_post(p) and "#aigenerated" not in p["caption"].lower():
                print(f"  refused {p['date']} {p['slot']}: AI picture without #aigenerated in the caption")
                continue
            when = local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            settings = {"firstComment": p["first_comment"]} if p.get("first_comment") else {}
            body = {"content": p["caption"], "scheduledFor": when, "timezone": rules["timezone"],
                    "mediaItems": [{"url": u} for u in p["photos"]],
                    "platforms": [{"platform": "facebook", "accountId": acc, "settings": settings}]}
            key, cid = f"fb-{p['date']}-{p['slot']}", f"FB-{data.get('start', plan_path.stem[5:])}-{i:02d}"
            cap_hash = content.sha256_text(p["caption"])
            content.record_publish(con, cid, "facebook", "fb_scheduled", key, caption_sha256=cap_hash, scheduled_for=when,
                                   submitted_at=content.now_utc(), state="submitting", attempt=1, error=None)
            try:
                res = pz.post("posts", body, idempotency_key=key)
            except Exception as e:  # record the failure, keep everything sent so far, then stop
                content.record_publish(con, cid, "facebook", "fb_scheduled", key, state="failed",
                                       error=f"{type(e).__name__}: {e}"[:500])
                raise
            post = res.get("post") or res.get("existingPost") or {}
            p.update(postzen_post_id=post.get("_id"), status=post.get("status") or "scheduled",
                     approval={"quote": quote, "at": dt.datetime.now().isoformat(timespec="seconds"),
                               "caption_sha256": cap_hash, "photos_sha256": content.sha256_text("\n".join(p["photos"]))})
            content.record_publish(con, cid, "facebook", "fb_scheduled", key, postzen_post_id=p["postzen_post_id"],
                                   state="submitted", platform_status=p["status"], evidence="PostZen accepted the request")
            history.append({"date": p["date"], "slot": p["slot"], "products": p["products"],
                            "postzen_post_id": p["postzen_post_id"], "ai_picture": is_ai_post(p)})
            content.atomic_write(plan_path, json.dumps(data, ensure_ascii=False, indent=1))  # saved after every post
            content.atomic_write(HISTORY, json.dumps(history, ensure_ascii=False, indent=1))
            sent += 1
            print(f"  {p['date']} {p['slot']} {p['kind']}: {', '.join(p['titles'])[:70]} -> {p['postzen_post_id']}")
    finally:
        con.close()
    if sent:
        data.setdefault("approvals", []).append({"quote": quote, "at": dt.datetime.now().isoformat(timespec="seconds"),
                                                 "posts_sent": sent})
        content.atomic_write(plan_path, json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{sent} post(s) sent")


METRICS = ("views", "impressions", "reach", "likes", "comments", "shares", "saves", "clicks")  # PostZen AnalyticsMetrics


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def sync_dashboard(out):
    """Write the dashboard's Facebook files to `out`: fb_schedule (every planned post and where it stands), fb_posts
    (each live post's numbers), fb_daily (daily totals) and fb_followers. Planned posts need no key; the rest comes
    from PostZen."""
    import csv
    import postzen as pz
    acc = hub_env.load_config()["postzen"]["facebook_account_id"]
    pulled = pz.sync_external(acc)
    schedule = []
    for path in sorted(DIR.glob("plan_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for p in data["posts"]:
            if p.get("postzen_post_id"):
                try:  # one failed status check is skipped, not fatal for the whole sync
                    post = pz.get(f"posts/{p['postzen_post_id']}").get("post") or {}
                except RuntimeError:
                    post = {}
                target = next(iter(post.get("platforms") or []), {})
                if not target and not post:
                    target = {"status": p.get("status"), "platformPostUrl": p.get("post_url")}
                status, url = target.get("status") or post.get("status"), target.get("platformPostUrl")
                if status != p.get("status") or (url and url != p.get("post_url")):
                    p.update(status=status, post_url=url or p.get("post_url"))
                    changed = True
            schedule.append({"date": p["date"], "time": p["slot"],
                             "weekday": dt.date.fromisoformat(p["date"]).strftime("%a"), "kind": p["kind"],
                             "products": " + ".join(p["titles"]), "photos": len(p["photos"]),
                             "status": p.get("status") or "not sent", "post_url": p.get("post_url") or ""})
        if changed:
            from studio.content import atomic_write
            atomic_write(path, json.dumps(data, ensure_ascii=False, indent=1))
    schedule.sort(key=lambda r: (r["date"], r["time"]))
    (out / "fb_schedule.json").write_text(json.dumps(schedule, ensure_ascii=False, indent=1), encoding="utf-8")

    def write_csv(name, cols, rows):
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    posts, page = [], 1
    while True:
        a = pz.get("analytics", platform="facebook", accountId=acc, limit=100, page=page)
        for p in a.get("posts") or []:
            m = p.get("analytics") or {}
            posts.append({"post_id": p.get("postzenPostId") or p.get("postId"),
                          "published": (p.get("publishedAt") or "")[:10],
                          "caption": (p.get("content") or "(posted directly on Facebook)")[:120],
                          "url": p.get("platformPostUrl") or "", **{k: _num(m.get(k)) for k in METRICS}})
        if page >= ((a.get("pagination") or {}).get("totalPages") or 1):
            break
        page += 1
    write_csv("fb_posts", ["post_id", "published", "caption", "url", *METRICS], posts)
    daily = pz.get("analytics/daily-metrics", platform="facebook", accountId=acc).get("dailyData") or []
    write_csv("fb_daily", ["date", *METRICS, "posts"],
              [{"date": (d.get("date") or "")[:10], **{k: _num((d.get("metrics") or d).get(k)) for k in METRICS},
                "posts": _num(d.get("postCount"))} for d in daily])
    stats = (pz.get("accounts/follower-stats", accountIds=acc).get("stats") or {}).get(acc, [])
    (out / "fb_followers.json").write_text(json.dumps([{"date": s["date"][:10], "followers": s["followers"]}
                                                       for s in stats]), encoding="utf-8")
    return [f"pulled from Facebook: {pulled}", f"fb_schedule {len(schedule)}", f"fb_posts {len(posts)}", f"fb_daily {len(daily)}",
            f"fb_followers {len(stats)}"]


def make_plan(start, days):
    path = DIR / f"plan_{start}.json"
    if path.exists():  # never overwrite a week that already has posts in PostZen (ids, approvals, hand edits)
        old = json.loads(path.read_text(encoding="utf-8"))
        sent = [p for p in old.get("posts") or [] if p.get("postzen_post_id")]
        if sent:
            raise SystemExit(f"{path.name} already has {len(sent)} post(s) in PostZen; plan a different start date")
    rules, history = load_rules(), load_history()
    posts = plan(start, days, rules, fetch_products(), history)
    from studio.content import atomic_write
    atomic_write(path, json.dumps({"start": start.isoformat(), "days": days, "posts": posts}, ensure_ascii=False, indent=1))
    review_sheet(posts, DIR / f"review_{start}.html")
    return path, posts


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--start", required=True)
    p.add_argument("--days", type=int, default=7)
    p = sub.add_parser("publish")
    p.add_argument("plan")
    p.add_argument("--quote", required=True, help="the owner's words approving these posts")
    sub.add_parser("auto")
    sub.add_parser("sync", help="write the dashboard's Facebook data files")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    DIR.mkdir(parents=True, exist_ok=True)
    if args.cmd == "plan":
        path, posts = make_plan(dt.date.fromisoformat(args.start), args.days)
        print(f"{len(posts)} posts planned -> {path.relative_to(HUB)} (review sheet beside it); nothing sent")
    elif args.cmd == "publish":
        publish(Path(args.plan), args.quote)
    elif args.cmd == "sync":
        for line in sync_dashboard(HUB / "studio" / "dashboard"):
            print(" ", line)
    else:
        rules = load_rules()
        if not rules.get("auto_publish"):
            print("auto_publish is off in data/facebook/rules.json (owner turns it on); nothing done")
            return
        planned = sorted(e["date"] for e in load_history())
        start = max(dt.date.today() + dt.timedelta(days=1),
                    dt.date.fromisoformat(planned[-1]) + dt.timedelta(days=1) if planned else dt.date.today())
        if start > dt.date.today() + dt.timedelta(days=rules["plan_ahead_days"]):
            print(f"already planned through {planned[-1]}; nothing to do")
            return
        path, _ = make_plan(start, 7)
        publish(path, f"auto (owner turned on auto_publish: {rules['auto_publish_quote']})")


if __name__ == "__main__":
    main()
