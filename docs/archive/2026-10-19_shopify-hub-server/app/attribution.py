"""Order attribution: which platform / campaign / ad gets credit for a Shopify order.

Model: **last touch**. Signals are read, most recent first, from Shopify's
``customerJourneySummary.lastVisit``, then ``firstVisit``, then the order's cart
``customAttributes`` (for themes that store UTMs at checkout). The first source that has
any signal wins as a whole, so UTMs and click ids always come from the same visit.

Within that visit a click id (gclid/gbraid/wbraid, fbclid, ttclid) beats utm_source for
the platform. Campaign / ad are matched by **id** against synced platform objects, so ads
should carry ids in their URL parameters:

* Meta:   ``utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.id}}&utm_content={{ad.id}}``
* TikTok: ``utm_source=tiktok&utm_medium=paid&utm_campaign=__CAMPAIGN_ID__&utm_content=__CID__``
* Google: ``utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={creative}``

Orders with a platform but no matching ad still count toward platform totals; re-run
:func:`reattribute` after ad syncs to pick up ads that didn't exist locally yet.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlsplit

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Ad, AdSet, AttributionMethod, Campaign, Order, Platform

CLICK_ID_PLATFORM: dict[str, Platform] = {
    "gclid": Platform.GOOGLE,
    "gbraid": Platform.GOOGLE,
    "wbraid": Platform.GOOGLE,
    "fbclid": Platform.META,
    "ttclid": Platform.TIKTOK,
}

SOURCE_PLATFORM: dict[str, Platform] = {
    **dict.fromkeys(
        ("google", "adwords", "googleads", "google_ads", "youtube", "yt"), Platform.GOOGLE
    ),
    **dict.fromkeys(("facebook", "fb", "instagram", "ig", "meta", "an", "msg"), Platform.META),
    **dict.fromkeys(("tiktok", "tt", "tiktokads", "tiktok_ads"), Platform.TIKTOK),
}

_UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
_CLICK_FIELDS = ("gclid", "gbraid", "fbclid", "ttclid")  # wbraid is folded into gclid
_MAX_LEN = {"fbclid": 512, "landing_site": 4000, "referring_site": 4000}


@dataclass
class Touch:
    """Attribution inputs for one order (what gets stored on ``orders``)."""

    landing_site: str | None = None
    referring_site: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    utm_content: str | None = None
    utm_term: str | None = None
    gclid: str | None = None
    fbclid: str | None = None
    ttclid: str | None = None
    gbraid: str | None = None  # folded into gclid on storage (Google iOS click ids)

    def has_signal(self) -> bool:
        return any(getattr(self, k) for k in (*_UTM_KEYS, *_CLICK_FIELDS))

    def as_columns(self) -> dict[str, str | None]:
        """Values for the ``orders`` attribution columns, trimmed to column sizes."""
        out = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "gbraid"}
        out["gclid"] = self.gclid or self.gbraid
        return {k: (v[: _MAX_LEN.get(k, 255)] if isinstance(v, str) else v) for k, v in out.items()}


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _query_params(url: str | None) -> dict[str, str]:
    if not url:
        return {}
    try:
        qs = parse_qs(urlsplit(url).query)
    except ValueError:
        return {}
    return {k.lower(): v[0] for k, v in qs.items() if v and v[0]}


def _touch_from_source(
    params: dict[str, str | None], landing: str | None, referrer: str | None
) -> Touch:
    url_params = _query_params(landing)
    merged: dict[str, str | None] = {**url_params, **{k: v for k, v in params.items() if v}}
    t = Touch(landing_site=_clean(landing), referring_site=_clean(referrer))
    for key in _UTM_KEYS:
        setattr(t, key, _clean(merged.get(key)))
    t.gclid = _clean(merged.get("gclid") or merged.get("wbraid"))
    t.gbraid = _clean(merged.get("gbraid"))
    t.fbclid = _clean(merged.get("fbclid"))
    t.ttclid = _clean(merged.get("ttclid"))
    return t


def touch_from_order(node: dict[str, Any]) -> Touch:
    """Pick the attribution touch for a GraphQL ``Order`` node (see module docstring)."""
    journey = node.get("customerJourneySummary") or {}
    candidates: list[Touch] = []
    for visit in (journey.get("lastVisit"), journey.get("firstVisit")):
        if visit:
            utm = visit.get("utmParameters") or {}
            candidates.append(
                _touch_from_source(
                    {
                        f"utm_{k}": utm.get(k)
                        for k in ("source", "medium", "campaign", "content", "term")
                    },
                    visit.get("landingPage"),
                    visit.get("referrerUrl"),
                )
            )
    attrs = {
        str(a.get("key", "")).lower(): a.get("value") for a in node.get("customAttributes") or []
    }
    candidates.append(
        _touch_from_source(
            attrs, attrs.get("landing_page") or attrs.get("landing_site"), attrs.get("referrer")
        )
    )

    chosen = next((c for c in candidates if c.has_signal()), Touch())
    # Landing / referrer: keep the most recent known even if that visit had no signal.
    chosen.landing_site = chosen.landing_site or next(
        (c.landing_site for c in candidates if c.landing_site), None
    )
    chosen.referring_site = chosen.referring_site or next(
        (c.referring_site for c in candidates if c.referring_site), None
    )
    return chosen


def touch_from_columns(order: Order) -> Touch:
    return Touch(**{f.name: getattr(order, f.name) for f in fields(Touch) if f.name != "gbraid"})


def platform_for(touch: Touch) -> tuple[Platform | None, AttributionMethod]:
    """Platform credited by a touch: click id first, then utm_source."""
    for key in _CLICK_FIELDS:
        if getattr(touch, key):
            platform = CLICK_ID_PLATFORM[key]
            return platform, AttributionMethod.CLICK_ID
    if touch.utm_source and (p := SOURCE_PLATFORM.get(touch.utm_source.lower())):
        return p, AttributionMethod.UTM
    return None, AttributionMethod.NONE


def resolve(session: Session, order: Order) -> None:
    """Set ``attributed_*`` columns on ``order`` from its stored touch columns."""
    touch = touch_from_columns(order)
    platform, method = platform_for(touch)
    ad_ids = [v for v in (touch.utm_content, touch.utm_term) if v]

    ad: Ad | None = None
    if ad_ids:
        stmt = select(Ad).where(Ad.external_id.in_(ad_ids))
        if platform:
            stmt = stmt.where(Ad.platform == platform)
        ad = session.scalars(stmt.limit(1)).first()

    campaign: Campaign | None = None
    if ad is not None:
        campaign = session.scalars(
            select(Campaign)
            .join(AdSet, AdSet.campaign_id == Campaign.id)
            .where(AdSet.id == ad.ad_set_id)
        ).first()
        if platform is None:
            platform, method = ad.platform, AttributionMethod.UTM
    elif touch.utm_campaign:
        stmt = select(Campaign).where(
            or_(Campaign.external_id == touch.utm_campaign, Campaign.name == touch.utm_campaign)
        )
        if platform:
            stmt = stmt.where(Campaign.platform == platform)
        campaign = session.scalars(stmt.limit(1)).first()
        if campaign is not None and platform is None:
            platform, method = campaign.platform, AttributionMethod.UTM

    if order.attribution_method == AttributionMethod.MANUAL:
        return  # never overwrite a manual attribution
    order.attributed_platform = platform
    order.attributed_ad_id = ad.id if ad else None
    order.attributed_campaign_id = campaign.id if campaign else None
    order.attribution_method = method


def reattribute(
    session: Session, since: datetime | None = None, only_unmatched: bool = True
) -> int:
    """Re-run attribution (e.g. after an ad sync). Returns how many orders were checked."""
    stmt = select(Order).where(Order.attribution_method != AttributionMethod.MANUAL)
    if only_unmatched:
        stmt = stmt.where(Order.attributed_ad_id.is_(None))
    if since is not None:
        stmt = stmt.where(Order.placed_at >= since)
    n = 0
    for order in session.scalars(stmt).yield_per(500):
        resolve(session, order)
        n += 1
    return n
