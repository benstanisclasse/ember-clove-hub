"""One rule module for everything we publish, on both channels (Content Studio 2.0, Phase D).

Every check returns findings {severity, check, detail}. Severities (docs/CONTENT_STUDIO_ARCHITECTURE_V2.md §5):
  critical  blocks, and can never be overridden: price, delivery, urgency or testimonial wording, missing AI
            disclosure, product inactive or out of stock, unapproved media, media or caption changed since approval
  high      blocks until the owner accepts it with a quote (an override), bound to the asset's and caption's sha256:
            unsupported product claims, other banned phrases, product not found in the store data
  medium    shown for review (e.g. availability data more than a day old)
  low       informational

Text rules come from the bible (studio/bible/rules.yaml banned_phrases and banned_regex, read as they are; changing
them still needs the owner's bible approval) plus the Facebook caption patterns that used to live in
facebook_photos.py. Scripts keep their exact old behaviour (gates.check_script uses script_errors); captions are
matched on word starts and with links removed, so a product handle in a URL or "relationship" never trips "ships".

Owner overrides:  python -I scripts/studio/checks.py override CONTENT_ID --check NAME --quote "owner's words"
"""
import argparse
import datetime as dt
import json
import re
import sqlite3
import sys
from functools import lru_cache
from pathlib import Path

HUB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HUB / "scripts"))

SEVERITIES = ("critical", "high", "medium", "low")
# Bible phrases by kind; a phrase added to rules.yaml later counts as "rule" (high) until it is listed here.
PHRASE_KIND = {
    "i bought": "testimonial", "i ordered": "testimonial", "my order": "testimonial", "i've been wearing": "testimonial",
    "free shipping": "delivery", "ships": "delivery", "delivery": "delivery", "arrives": "delivery",
    "on sale": "price", "discount": "price", "limited": "urgency", "selling out": "urgency", "last chance": "urgency",
    "warm": "claim", "wool": "claim", "not itchy": "claim", "flattering on every body": "claim", "slimming": "claim",
    "guarantee": "claim", "follow me": "cta", "follow for": "cta"}
KIND_SEVERITY = {"price": "critical", "delivery": "critical", "urgency": "critical", "testimonial": "critical",
                 "claim": "high", "rule": "high", "cta": "medium"}
CAPTION_PATTERNS = [(r"\$", "price"), (r"\bsale\b", "price"), (r"\bship", "delivery"), (r"\bdeliver", "delivery"),
                    (r"\bhurry\b", "urgency"), (r"\blimited\b", "urgency"), (r"\btoday only\b", "urgency")]
CRITICAL_CHECKS = {"price", "delivery", "urgency", "testimonial", "ai_disclosure", "product_unavailable",
                   "out_of_stock", "not_approved", "approval_unbound", "media_changed", "caption_changed",
                   "media_missing"}
URL = re.compile(r"https?://\S+")
STALE_H = 26  # availability data older than this is shown (medium)


def finding(severity, check, detail):
    return {"severity": severity, "check": check, "detail": detail}


@lru_cache(maxsize=1)
def bible_text_rules():
    import yaml
    data = yaml.safe_load((HUB / "studio" / "bible" / "rules.yaml").read_text(encoding="utf-8"))
    return tuple(data.get("banned_phrases") or []), tuple(data.get("banned_regex") or [])


def _regex_kind(rx):
    return "price" if ("\\$" in rx or "dollar" in rx) else "delivery" if ("days" in rx or "weeks" in rx) else "rule"


# --- words ---------------------------------------------------------------------------------------------------------

def script_errors(text, phrases, regexes):
    """The script gate's text rules, unchanged: plain substring match on the lowered script + caption."""
    errs = [f"banned phrase: {p!r}" for p in phrases if p.lower() in text]
    errs += [f"banned pattern: {rx}" for rx in regexes if re.search(rx, text, re.I)]
    return errs


def text_findings(text, phrases=None, regexes=None):
    """Caption / comment rules for both channels. Links are removed first; phrases match at a word start."""
    if phrases is None or regexes is None:
        phrases, regexes = bible_text_rules()
    body = URL.sub(" ", text or "").lower()
    hits = [(PHRASE_KIND.get(p.lower(), "rule"), p.lower()) for p in phrases if re.search(r"\b" + re.escape(p.lower()), body)]
    for rx, kind in [(rx, _regex_kind(rx)) for rx in regexes] + CAPTION_PATTERNS:
        m = re.search(rx, body, re.I)
        if m:
            hits.append((kind, m.group(0).strip()))
    out, seen = [], set()
    for kind, token in hits:
        if (kind, token) in seen or any(k == kind and token in t for k, t in seen):  # "limited" twice -> once
            continue
        seen.add((kind, token))
        out.append(finding(KIND_SEVERITY[kind], kind if kind != "rule" else "banned_phrase", f"{token!r} ({kind})"))
    return out


def text_ok(text):
    """True when a text has no critical or high finding (used to pick product description sentences)."""
    return not any(f["severity"] in ("critical", "high") for f in text_findings(text))


def disclosure_findings(caption, ai):
    # Owner 2026-10-28: captions no longer carry #aigenerated (TikTok's own AI label discloses); flag it if it creeps back
    if "#aigenerated" in (caption or "").lower():
        return [finding("medium", "ai_disclosure", "owner asked for no #aigenerated in captions (2026-10-28)")]
    return []


# --- products ------------------------------------------------------------------------------------------------------

def availability(handles, analytics_path=None, now=None):
    """Each product (handle, or Shopify product gid as the wardrobe stores it) must exist in the synced Shopify data,
    be ACTIVE and have stock on at least one variant."""
    path = Path(analytics_path or HUB / "studio" / "analytics.db")
    handles = [h for h in handles if h]
    if not handles:
        return []
    if not path.exists():
        return [finding("high", "availability_unknown", "no store data (studio/analytics.db) to check products against")]
    a = sqlite3.connect(path)
    a.row_factory = sqlite3.Row
    out = []
    try:
        for h in handles:
            p = a.execute("SELECT * FROM products WHERE handle = ? OR product_id = ?", (h, h)).fetchone()
            if p is None:
                out.append(finding("high", "product_unknown", f"{h} is not in the store data (deleted or renamed?)"))
                continue
            h = p["handle"] or h
            if (p["status"] or "").upper() != "ACTIVE":
                out.append(finding("critical", "product_unavailable", f"{h} is {p['status']} in Shopify"))
                continue
            inv = [r[0] for r in a.execute("SELECT inventory FROM variants WHERE product_id = ?", (p["product_id"],))]
            known = [v for v in inv if v is not None]
            if inv and known and len(known) == len(inv) and max(known) <= 0:
                out.append(finding("critical", "out_of_stock", f"{h} has no stock on any variant"))
            if p["fetched_at"]:
                age = ((now or dt.datetime.now(dt.timezone.utc)) - dt.datetime.fromisoformat(
                    p["fetched_at"].replace("Z", "+00:00"))).total_seconds() / 3600
                if age > STALE_H:
                    out.append(finding("medium", "availability_stale", f"{h}: store data is {age:.0f} h old"))
    finally:
        a.close()
    return out


# --- approvals bound to the media ----------------------------------------------------------------------------------

def binding_findings(approval, asset_sha, caption_sha):
    """The approval must name the exact file (sha256) and, once fixed, the exact caption."""
    if not approval:
        return [finding("critical", "not_approved", "no approval on record")]
    if asset_sha is None:
        return [finding("critical", "media_missing", "the approved file is missing")]
    if not approval.get("asset_sha256"):
        return [finding("critical", "approval_unbound",
                        "approved before approvals were bound to the file; approve this exact file again")]
    out = []
    if approval["asset_sha256"] != asset_sha:
        out.append(finding("critical", "media_changed", "the file changed after it was approved; approve it again"))
    if approval.get("caption_sha256") and caption_sha and approval["caption_sha256"] != caption_sha:
        out.append(finding("critical", "caption_changed", "the caption changed after it was approved; approve it again"))
    return out


# --- overrides -----------------------------------------------------------------------------------------------------

def overrides(con, content_id):
    return [dict(r) for r in con.execute("SELECT * FROM overrides WHERE content_id = ?", (content_id,))]


def record_override(con, content_id, check, asset_sha, caption_sha, quote, actor):
    if actor != "owner" or not (quote or "").strip():
        raise ValueError("only the owner overrides a check, with their words (--quote)")
    if check in CRITICAL_CHECKS:
        raise ValueError(f"{check} is critical and can't be overridden")
    from studio import content
    con.execute("INSERT INTO overrides (content_id, check_name, asset_sha256, caption_sha256, quote, actor, at) "
                "VALUES (?,?,?,?,?,?,?)", (content_id, check, asset_sha, caption_sha, quote, actor, content.now_utc()))
    content.add_event(con, content_id, None, None, actor, f"override {check}: {quote}")
    con.commit()


def unresolved(findings, ovr, asset_sha, caption_sha):
    """Findings that still block: every critical one, and each high one without an owner override for this exact
    check, file and caption."""
    ok = {(o["check_name"], o["asset_sha256"], o["caption_sha256"]) for o in ovr}
    return [f for f in findings if f["severity"] == "critical"
            or (f["severity"] == "high" and (f["check"], asset_sha, caption_sha) not in ok)]


def describe(findings):
    return "; ".join(f"[{f['severity']}] {f['check']}: {f['detail']}" for f in findings)


# --- current hashes of a content item ------------------------------------------------------------------------------

def current_hashes(con, content_id):
    """(asset_sha256, caption_sha256) as the files and records are right now."""
    from studio import content
    if content_id.startswith("TT-"):
        ep = con.execute("SELECT video_path, caption FROM episodes WHERE id = ?", (content_id[3:],)).fetchone()
        if ep is None:
            raise ValueError(f"no episode {content_id[3:]}")
        f = HUB / (ep["video_path"] or "").replace("\\", "/")
        return (content.sha256_file(f) if ep["video_path"] and f.exists() else None,
                content.sha256_text(ep["caption"]) if ep["caption"] else None)
    row = con.execute("SELECT image_path, caption FROM fb_ai_posts WHERE content_id = ?", (content_id,)).fetchone()
    if row is None:
        raise ValueError(f"{content_id} is not a Facebook AI-picture post made in the database")
    f = HUB / (row["image_path"] or "")
    return (content.sha256_file(f) if row["image_path"] and f.exists() else None,
            content.sha256_text(row["caption"]) if row["caption"] else None)


def main():
    from studio import content
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("override", help="owner accepts a high finding for this exact file and caption")
    p.add_argument("content_id")
    p.add_argument("--check", required=True)
    p.add_argument("--quote", required=True, help="the owner's words")
    p = sub.add_parser("text", help="check a caption or comment")
    p.add_argument("text")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if args.cmd == "text":
        print(json.dumps(text_findings(args.text), indent=1) if text_findings(args.text) else "no findings")
        return
    con = content.connect()
    asset, cap = current_hashes(con, args.content_id)
    record_override(con, args.content_id, args.check, asset, cap, args.quote, "owner")
    print(f"{args.content_id}: {args.check} accepted by the owner for this file and caption")


if __name__ == "__main__":
    main()
