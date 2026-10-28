"""The rules as code: script checks, calendar checks, prompt building and cost estimates.

Nothing here uses judgement. A script or calendar either passes every rule in studio/bible/rules.yaml or is rejected
with the list of broken rules. Prompts are rendered only from the template and the bible; there is no free-text prompt.
"""
import datetime as dt
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

HUB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HUB / "scripts"))
from prompt_style import PRESENTER, REALISM  # noqa: E402
from studio import checks  # noqa: E402

PIXELS = {"480p": (480, 854), "720p": (720, 1280)}


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower().replace("-", " "))


def check_script(script, ep, b):
    """script = {"lines": [...], "actions": [...], "caption": "..."}; returns a list of broken rules (empty = pass)."""
    r, ch = b["rules"], b["character"]
    errs = []
    lines, actions = script.get("lines", []), script.get("actions", [])
    if len(lines) != r.script.lines or len(actions) != r.script.lines:
        errs.append(f"needs exactly {r.script.lines} lines and {r.script.lines} shot actions")
    text = " ".join(lines).lower()
    every = (text + " " + " ".join(actions).lower() + " " + script.get("caption", "").lower())
    errs += checks.script_errors(every, r.banned_phrases + ch.never_says, r.banned_regex)  # shared rule module
    for w in r.tts_avoid:
        if w.lower() in text:
            errs.append(f"the video voice mispronounces {w!r}: rephrase")
    n, dur = len(words(" ".join(lines))), r.generation.duration_s
    lo, hi = r.script.words_per_second_min * dur, r.script.words_per_second_max * dur
    if not lo <= n <= hi:
        errs.append(f"{n} spoken words; needs {lo:.0f}-{hi:.0f} for {dur} s")
    soft_hits = [s for s in r.cta.soft_lines if s.lower() in text]
    has_product_cta = r.cta.product_cta.lower() in text
    if ep["cta_type"] == "product" and not (lines and lines[-1].strip().endswith(r.cta.product_cta)):
        errs.append(f"product episodes end with exactly: {r.cta.product_cta!r}")
    if ep["cta_type"] == "soft" and soft_hits != [ep.get("cta_line")] and ep.get("cta_line"):
        errs.append(f"this episode's soft line is {ep['cta_line']!r} (planned); use exactly that")
    if ep["cta_type"] == "soft" and not ep.get("cta_line") and soft_hits:
        errs.append("no soft follow line is planned for this episode")
    if ep["cta_type"] in ("soft", "none") and has_product_cta:
        errs.append("product call to action in a non-product episode")
    if ep.get("product_id"):
        prod = next(p for p in b["products"].items if p.id == ep["product_id"])
        used = [f for f in prod.facts if f.lower() in text]
        if len(used) < 2:
            errs.append(f"product episodes name at least 2 listed facts for {prod.id}: {prod.facts}")
    return errs


BASE = ("top", "knitwear", "bottom", "dress")


def season_of(day):
    """Minneapolis calendar: winter runs Dec-Mar."""
    m = dt.date.fromisoformat(day).month
    return {12: "winter", 1: "winter", 2: "winter", 3: "winter", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer"}.get(m, "fall")


def in_season(item, day):
    return "all" in item.season or season_of(day) in item.season


def occasion_of(ep, b):
    return next((s.occasion for s in b["series"].items if s.id == ep.get("series_id")), "day")


def light_for(room, ep, b):
    """Evening posts use the room's lamp or night light when it has one."""
    if occasion_of(ep, b) == "night":
        lit = [x for x in room.lighting if "lamp" in x or "night" in x or "dim" in x]
        if lit:
            return lit[0].replace("_", " ")
    return room.lighting[0].replace("_", " ")


def is_outdoor(ep, b):
    return any(r.outdoor for r in b["world"].rooms if r.id == ep.get("room_id"))


def shoe_ok(shoe_id, ep, earlier, b):
    """Shoe rotation: not the same pair as the post before, at most shoes_max_per_week times Mon-Sun."""
    r = b["rules"].outfits
    if r.shoe_rules_from and ep["post_date"] < r.shoe_rules_from:
        return True
    worn = lambda e: shoe_id in json.loads(e.get("outfit_json") or "[]")  # noqa: E731
    if r.shoes_no_back_to_back and earlier and worn(earlier[-1]):
        return False
    if r.shoes_max_per_week:
        d = dt.date.fromisoformat(ep["post_date"])
        monday = (d - dt.timedelta(days=d.weekday())).isoformat()
        if sum(1 for e in earlier if monday <= e["post_date"] <= ep["post_date"] and worn(e)) >= r.shoes_max_per_week:
            return False
    return True


def base_pieces(outfit_ids, b):
    cat = {i.id: i.category for i in b["wardrobe"].items}
    return {o for o in outfit_ids if cat.get(o) in BASE}


def pick_outfit(ep, recent, b):
    """A random but reproducible outfit (seeded by the episode id) that obeys rules.outfits against `recent`
    (earlier episodes in posting order). It starts from rules.outfits.store_pieces_per_outfit Ember & Clove pieces and
    fills the rest from her basics. Product episodes: the product is the store piece and the base, so basics only."""
    rules = b["rules"].outfits
    occ = occasion_of(ep, b)
    fits = [i for i in b["wardrobe"].items if in_season(i, ep["post_date"]) and occ in i.occasion]
    used = set().union(*[base_pieces(json.loads(e.get("outfit_json") or "[]"), b)
                         for e in recent[-rules.no_repeat_base_piece_posts:]]) if rules.no_repeat_base_piece_posts else set()
    cold = season_of(ep["post_date"]) in ("fall", "winter")
    outdoor = is_outdoor(ep, b)
    n_store = 0 if ep.get("product_id") else rules.store_pieces_per_outfit
    for attempt in range(200):
        rnd = random.Random(f"{ep['id']}#{attempt}")

        def basics(*cats):
            return [i for i in fits if i.category in cats and not i.store_product and i.id not in used]

        pick = []
        if n_store:
            stores = [i for i in fits if i.store_product and i.id not in used and (outdoor or not i.outdoor_only)
                      and not (outdoor and cold and i.open_toe) and (i.category != "shoes" or shoe_ok(i.id, ep, recent, b))]
            if not stores:
                break
            # half the posts feature a piece made for the moment: sunglasses outdoors, night-only pieces at night
            featured = [i for i in stores if i.outdoor_only or (occ == "night" and i.occasion == ["night"])]
            pick.append(rnd.choice(featured if featured and rnd.random() < 0.5 else stores))
        have = {i.category for i in pick}
        if not ep.get("product_id") and "dress" not in have:
            if have & {"top", "knitwear"}:
                pick.append(rnd.choice(basics("bottom")))
            elif "bottom" in have:
                pick.append(rnd.choice(basics("top", "knitwear")))
            elif basics("dress") and rnd.random() < 0.25:
                pick.append(rnd.choice(basics("dress")))
            else:
                pick += [rnd.choice(basics("top", "knitwear")), rnd.choice(basics("bottom"))]
        have = {i.category for i in pick}
        layer = basics("outerwear")
        if "outerwear" not in have and layer and (ep.get("room_id") == "entryway" or (outdoor and cold)
                                                  or rnd.random() < (0.5 if cold else 0.2)):
            pick.append(rnd.choice(layer))
        if "shoes" not in have:
            pairs = [i for i in fits if i.category == "shoes" and not (outdoor and cold and i.open_toe)
                     and shoe_ok(i.id, ep, recent, b)]
            store_pairs = [i for i in pairs if i.store_product] if (rules.extra_store_shoes and n_store) else []
            basic_pairs = [i for i in pairs if not i.store_product]
            choice = store_pairs if store_pairs and rnd.random() < 0.5 else basic_pairs
            if not choice:
                continue
            pick.append(rnd.choice(choice))
        for cat, chance in (("bag", 0.4), ("accessory", 0.3)):
            options = [i for i in basics(cat) if "belt" not in i.id or "bottom" in have]  # belts only with a bottom
            if cat not in have and options and rnd.random() < chance:
                pick.append(rnd.choice(options))
        legs_out = any(i.category == "dress" or "skirt" in i.id for i in pick) or ep.get("product_id")
        tights = basics("hosiery")
        if tights and cold and legs_out and rnd.random() < 0.6:
            pick.append(rnd.choice(tights))
        ids = [i.id for i in pick]
        if not check_outfits(recent + [{**ep, "outfit_json": json.dumps(ids)}], b):
            return ids
    raise ValueError(f"{ep['id']}: no outfit satisfies the outfit rules; add wardrobe or store pieces for this season")


def check_outfits(eps, b):
    """Every outfit exists, is in season, isn't a repeat within no_repeat_outfit_days, doesn't reuse a base piece
    from the previous no_repeat_base_piece_posts posts, and has exactly store_pieces_per_outfit store pieces
    (none extra in product episodes, where the product is the store piece)."""
    rules = b["rules"].outfits
    items = {i.id: i for i in b["wardrobe"].items}
    errs = []
    worn = [(e, json.loads(e.get("outfit_json") or "[]")) for e in eps]
    for k, (e, ids) in enumerate(worn):
        if not ids:
            continue
        errs += [f"{e['id']}: unknown wardrobe item {o!r}" for o in ids if o not in items]
        errs += [f"{e['id']}: {o} is out of season" for o in ids if o in items and not in_season(items[o], e["post_date"])]
        occ = occasion_of(e, b)
        errs += [f"{e['id']}: {o} isn't a {occ} piece" for o in ids if o in items and occ not in items[o].occasion]
        if not is_outdoor(e, b):
            errs += [f"{e['id']}: {o} is only worn outdoors" for o in ids if o in items and items[o].outdoor_only]
        elif season_of(e["post_date"]) in ("fall", "winter") and not any(
                items[o].category == "outerwear" for o in ids if o in items):
            errs.append(f"{e['id']}: outdoors in {season_of(e['post_date'])} needs a coat or jacket")
        for prev, prev_ids in worn[:k]:
            if set(prev_ids) == set(ids) and e["post_date"] < _minus(prev["post_date"], -rules.no_repeat_outfit_days):
                errs.append(f"{e['id']}: same outfit as {prev['id']} within {rules.no_repeat_outfit_days} days")
        window = worn[max(0, k - rules.no_repeat_base_piece_posts): k]
        again = base_pieces(ids, b) & set().union(*[base_pieces(x, b) for _, x in window]) if window else set()
        errs += [f"{e['id']}: {o} worn again within {rules.no_repeat_base_piece_posts} posts" for o in sorted(again)]
        store = [o for o in ids if o in items and items[o].store_product]
        need = 0 if e.get("product_id") else rules.store_pieces_per_outfit
        shoes = [o for o in store if items[o].category == "shoes"]
        clothes = [o for o in store if items[o].category != "shoes"]
        ok = len(store) == need
        if rules.extra_store_shoes:  # one clothing piece plus at most one pair of store shoes, or the shoes alone
            ok = (len(clothes) == need and len(shoes) <= 1) or (need == 1 and not clothes and len(shoes) == 1)
        if not ok:
            errs.append(f"{e['id']}: {len(store)} Ember & Clove pieces in the outfit; needs exactly {need}"
                        + (" (plus at most one pair of store shoes)" if rules.extra_store_shoes else ""))
        if is_outdoor(e, b) and season_of(e["post_date"]) in ("fall", "winter"):
            errs += [f"{e['id']}: {o} is open-toe outdoors in the cold" for o in ids if o in items and items[o].open_toe]
        pair = [o for o in ids if o in items and items[o].category == "shoes"]
        errs += [f"{e['id']}: {o} breaks the shoe rotation" for o in pair if not shoe_ok(o, e, [x for x, _ in worn[:k]], b)]
    return errs


def check_calendar(eps, b):
    """eps: episodes in posting order (dicts with post_date, product_id, room_id, series_id, pillar, cta_line)."""
    r = b["rules"]
    errs = []
    per_day = Counter(e["post_date"] for e in eps)
    errs += [f"{d}: {n} posts (max {r.posting.max_posts_per_day})" for d, n in per_day.items()
             if n > r.posting.max_posts_per_day]
    for a, c in zip(eps, eps[1:]):
        if r.rotation.no_same_product_back_to_back and a["product_id"] and a["product_id"] == c["product_id"]:
            errs.append(f"{c['id']}: same product as the post before")
        if r.rotation.no_same_room_back_to_back and a["room_id"] == c["room_id"]:
            errs.append(f"{c['id']}: same room as the post before")
        if r.rotation.no_same_series_back_to_back and a["series_id"] == c["series_id"]:
            errs.append(f"{c['id']}: same series as the post before")
    if r.mix.product_share_max == 0:
        errs += [f"{e['id']}: product posts are off (rules.mix.product_share_max is 0)" for e in eps
                 if e["pillar"] == "product"]
    errs += check_outfits(eps, b)
    w = r.cta.window_posts
    for i in range(len(eps)):
        window = eps[max(0, i - w + 1): i + 1]
        if sum(1 for e in window if e.get("cta_line")) > r.cta.max_soft_cta_per_window:
            errs.append(f"{eps[i]['id']}: more than {r.cta.max_soft_cta_per_window} soft line in {w} posts")
    for i in range(len(eps)):
        week = [e for e in eps if e["post_date"] <= eps[i]["post_date"] and e["post_date"] > _minus(eps[i]["post_date"], 7)]
        if len(week) >= 7:
            share = sum(1 for e in week if e["pillar"] == "value") / len(week)
            if share < r.mix.value_share_min:
                errs.append(f"week to {eps[i]['post_date']}: value share {share:.0%} < {r.mix.value_share_min:.0%}")
    return sorted(set(errs))


def _minus(day, n):
    return (dt.date.fromisoformat(day) - dt.timedelta(days=n)).isoformat()


def shot_times(n, duration):
    cuts = [round(duration * i / n, 1) for i in range(n + 1)]
    return list(zip(cuts, cuts[1:]))


def build_prompt(ep, script, b, template="video_prompt.j2", face_ref=True):
    """template video_prompt_frame.j2 is the short form for models that start from a first frame (it already shows the
    face, place and outfit)."""
    env = Environment(loader=FileSystemLoader(str(HUB / "studio" / "templates")), undefined=StrictUndefined)
    room = next(r for r in b["world"].rooms if r.id == ep["room_id"])
    product = next((p for p in b["products"].items if p.id == ep["product_id"]), None)
    outfit_ids = json.loads(ep["outfit_json"] or "[]")
    worn = [i for i in b["wardrobe"].items if i.id in outfit_ids]
    store_piece = next((i for i in worn if i.store_product), None)
    outfit = [i.name for i in worn if not i.store_product]
    shots = [{"start": s, "end": e, "action": a, "line": ln}
             for (s, e), a, ln in zip(shot_times(len(script["lines"]), b["rules"].generation.duration_s),
                                      script["actions"], script["lines"])]
    text = env.get_template(template).render(
        duration=b["rules"].generation.duration_s, room=room, lighting=light_for(room, ep, b),
        presenter=PRESENTER, character=b["character"], product=product, store_piece=store_piece, outfit=outfit,
        shots=shots, realism=REALISM, face_ref=face_ref)
    return text, hashlib.sha256(text.encode()).hexdigest()[:16]


def build_first_frame_prompt(ep, script, b):
    """Prompt and images for the still that opens a frame-only video (e.g. Kling): image 1 = face, image 2 = place,
    image 3 = the Ember & Clove piece (or the product). Same rule as build_prompt: template + bible only."""
    env = Environment(loader=FileSystemLoader(str(HUB / "studio" / "templates")), undefined=StrictUndefined)
    room = next(r for r in b["world"].rooms if r.id == ep["room_id"])
    product = next((p for p in b["products"].items if p.id == ep["product_id"]), None)
    worn = [i for i in b["wardrobe"].items if i.id in json.loads(ep["outfit_json"] or "[]")]
    store_piece = next((i for i in worn if i.store_product), None)
    text = env.get_template("first_frame.j2").render(
        lighting=light_for(room, ep, b), presenter=PRESENTER, character=b["character"], room=room,
        store_piece=store_piece, product=product, outfit=[i.name for i in worn if not i.store_product],
        first_action=script["actions"][0], realism=REALISM)
    images = [b["character"].face_refs[0], room.ref_images[0]]
    images += (product.reference_images[:1] if product else store_piece.reference_images[:1] if store_piece else [])
    return text, images


def reference_images(ep, b, face=True):
    """face=False for models whose safety filter refuses any realistic face (Seedance 2.5)."""
    refs = list(b["character"].face_refs[:1]) if face else []
    room = next(r for r in b["world"].rooms if r.id == ep["room_id"])
    refs += room.ref_images[:1]
    product = next((p for p in b["products"].items if p.id == ep["product_id"]), None)
    if product:
        refs += product.reference_images
    worn = json.loads(ep.get("outfit_json") or "[]")
    refs += [img for i in b["wardrobe"].items if i.id in worn and i.store_product for img in i.reference_images]
    return refs[: b["rules"].generation.max_reference_images]


def estimate_usd(b):
    g = b["rules"].generation
    w, h = PIXELS[g.resolution]
    return round(g.duration_s * w * h * 24 / 1024 * g.usd_per_m_tokens / 1e6, 2)
