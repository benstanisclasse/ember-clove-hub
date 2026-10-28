"""Tracking-link convention and channel mapping (Dashboard 2.0, Phase E).

One UTM convention for every link we create, and one function that decides which channel a visit or order came from,
with how sure we are:
  Directly tracked  the link carried our UTM tags (or an ad platform's)
  Inferred          no tags, but Shopify saw where the visitor came from (e.g. a facebook.com referrer)
  Unattributed      no tags and no usable referrer (typed the address, bookmarks, many apps)

Organic social links use utm_medium=organic_social; earlier Facebook posts used "social", which maps the same way.
Ad links get their tags from each platform's URL parameters (see docs/DASHBOARD_ARCHITECTURE_V2.md §5); unfilled
macros such as __CAMPAIGN_NAME__ or {{campaign.name}} are reported by unfilled_macros().
"""
import re
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

# channel key -> (utm_source, utm_medium) for links we build ourselves
CONVENTION = {
    "facebook_organic": ("facebook", "organic_social"),
    "instagram_organic": ("instagram", "organic_social"),
    "tiktok_organic": ("tiktok", "organic_social"),
    "meta_ads": ("facebook", "paid_social"),
    "tiktok_ads": ("tiktok", "paid_social"),
}
LABELS = {"facebook_organic": "Facebook organic", "instagram_organic": "Instagram organic", "tiktok_organic": "TikTok organic",
          "meta_ads": "Meta ads", "tiktok_ads": "TikTok ads", "search": "Search",
          "direct": "Direct", "email": "Email", "other_tagged": "Other tagged links", "other": "Other referrers"}
DIRECT, INFERRED, NONE = "Directly tracked", "Inferred", "Unattributed"
MACRO = re.compile(r"__[A-Z_]+__|\{\{[^}]+\}\}|\{[A-Za-z_]+\}")
PAID = {"paid", "paid_social", "paid_search", "cpc", "ppc", "cpm", "ads", "ad", "paidsocial"}
ORGANIC = {"social", "organic_social", "organic", "post", "bio"}


def tag_link(url, channel, campaign, content="", term=""):
    """Add our UTM tags to a store link (existing query parameters are kept; old utm_* are replaced)."""
    source, medium = CONVENTION[channel]
    parts = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")]
    q += [("utm_source", source), ("utm_medium", medium), ("utm_campaign", campaign)]
    q += [("utm_content", content)] if content else []
    q += [("utm_term", term)] if term else []
    return urlunsplit(parts._replace(query=urlencode(q)))


def unfilled_macros(*values):
    """Platform placeholders that reached the store unreplaced (e.g. ad previews or a wrong macro name)."""
    return sorted({m for v in values if v for m in MACRO.findall(str(v))})


def channel_of(utm_source="", utm_medium="", referrer_source="", referrer_name=""):
    """-> (channel key, confidence). UTM tags win over the referrer; the referrer is only an inference."""
    s, m = (utm_source or "").strip().lower(), (utm_medium or "").strip().lower()
    rs, rn = (referrer_source or "").strip().lower(), (referrer_name or "").strip().lower()
    if s:
        paid = m in PAID or "paid" in m or "cpc" in m
        if s in ("facebook", "fb", "meta", "instagram", "ig", "an", "msg"):  # Meta's {{site_source_name}} values
            if paid:
                return "meta_ads", DIRECT
            return ("instagram_organic" if s in ("instagram", "ig") else "facebook_organic"), DIRECT
        if s == "tiktok":
            return ("tiktok_ads" if paid else "tiktok_organic"), DIRECT
        if s in ("microsoft", "bing", "msn"):  # we run no Microsoft ads (removed 2026-10-28)
            return "search", DIRECT
        if s in ("email", "klaviyo", "shopify_email") or m == "email":
            return "email", DIRECT
        return "other_tagged", DIRECT
    if rs == "direct" or (not rs and not rn):
        return "direct", NONE
    if rs == "social":
        if "tiktok" in rn:
            return "tiktok_organic", INFERRED
        if "instagram" in rn:
            return "instagram_organic", INFERRED
        if "facebook" in rn or rn in ("fb", "meta"):
            return "facebook_organic", INFERRED
        return "other", INFERRED
    if rs == "search":
        return "search", INFERRED
    if rs == "email":
        return "email", INFERRED
    if "microsoft" in rn or "bing" in rn:
        return "search", INFERRED
    return "other", INFERRED
