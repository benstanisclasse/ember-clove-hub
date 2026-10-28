"""Conversion orchestration: purchases, storefront batches, sweeps, health report, setup."""

from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import business_settings
from app.actions import ActionContext, SessionFactory, write_action
from app.config import Settings, get_settings
from app.conversions import signals
from app.conversions.events import PURCHASE, Event, from_browser, purchase_from_order
from app.conversions.senders import Sender, configured_senders
from app.db import session_scope
from app.integrations.http import IntegrationError
from app.log import get_logger, scrub
from app.models import ConversionEvent, ConversionEventCount, Customer, Order, OrderItem, Product

log = get_logger(__name__)
MAX_AGE = {"meta": timedelta(days=7), "tiktok": timedelta(days=7), "google": timedelta(days=89)}
PiiFetcher = Callable[[int], dict[str, Any]]

_enabled_cache: tuple[float, bool] = (0.0, False)


def conversions_on(session_factory: SessionFactory = session_scope, ttl_s: float = 60.0) -> bool:
    """Cached check used by the high-traffic /collect endpoint."""
    global _enabled_cache
    if time.monotonic() - _enabled_cache[0] < ttl_s:
        return _enabled_cache[1]
    with session_factory() as s:
        bs = business_settings.load(s)
    value = bs.conversions_enabled and not bs.kill_switch
    _enabled_cache = (time.monotonic(), value)
    return value


def shopify_pii(order_shopify_id: int) -> dict[str, Any]:
    """Email / phone / billing country for one order, fetched transiently. Empty dict if the
    app lacks protected-customer-data access (events still go out, just without hashes)."""
    from app.integrations.shopify import queries
    from app.integrations.shopify.mapping import order_gid
    from app.jobs.shopify import get_client

    try:
        node = (
            get_client()
            .execute(queries.ORDER_PII, {"id": order_gid(order_shopify_id)})
            .get("order")
            or {}
        )
    except IntegrationError as exc:
        log.warning("shopify_pii_unavailable", error=str(exc)[:200])
        return {}
    return {
        "email": node.get("email"),
        "phone": node.get("phone"),
        "country": (node.get("billingAddress") or {}).get("countryCodeV2"),
    }


def _row(session: Session, platform: str, name: str, event_id: str) -> ConversionEvent | None:
    return session.scalar(
        select(ConversionEvent).where(
            ConversionEvent.platform == platform,
            ConversionEvent.event_name == name,
            ConversionEvent.event_id == event_id,
        )
    )


def _record(
    session: Session,
    platform: str,
    event: Event,
    order_id: int,
    status: str,
    detail: str | None = None,
) -> None:
    row = _row(session, platform, event.name, event.event_id) or ConversionEvent(
        platform=platform,
        event_name=event.name,
        event_id=event.event_id,
        order_id=order_id,
        attempts=0,
    )
    row.status, row.detail, row.value = status, detail, event.value
    row.attempts = (row.attempts or 0) + (status in ("sent", "failed"))
    if status == "sent":
        row.sent_at = datetime.now(UTC)
    session.add(row)


def send_purchase(
    order_id: int,
    *,
    session_factory: SessionFactory = session_scope,
    redis: Any | None = None,
    senders: list[Sender] | None = None,
    pii_fetcher: PiiFetcher | None = None,
    now: datetime | None = None,
) -> dict[str, str]:
    """Report one order as a purchase to every configured platform, at most once each.

    Raises IntegrationError if a retryable send failed (RQ retries the job).
    """
    now = now or datetime.now(UTC)
    with session_factory() as s:
        bs = business_settings.load(s)
        if not bs.conversions_enabled or bs.kill_switch:
            return {"all": "disabled"}
        order = s.get(Order, order_id)
        if order is None:
            return {"all": "missing order"}
        if order.test or order.cancelled_at is not None:
            return {"all": "test or cancelled"}
        items = list(s.scalars(select(OrderItem).where(OrderItem.order_id == order.id)))
        products = dict(
            s.execute(
                select(Product.id, Product.shopify_id).where(
                    Product.id.in_([i.product_id for i in items if i.product_id])
                )
            ).all()
        )
        customer_shopify_id = (
            s.scalar(select(Customer.shopify_id).where(Customer.id == order.customer_id))
            if order.customer_id
            else None
        )
        senders = senders if senders is not None else configured_senders()
        if not senders:
            return {"all": "no platform configured"}
        pending = [
            x
            for x in senders
            if not (
                (r := _row(s, x.platform, PURCHASE, str(order.shopify_id)))
                and r.status in ("sent", "skipped")
            )
        ]
        if not pending:
            return {"all": "already sent"}
        shopify_id, placed_at = order.shopify_id, order.placed_at

        needs_pii = bs.conversions_hashed_pii or bool(bs.conversions_exclude_countries)
        pii = (pii_fetcher or shopify_pii)(shopify_id) if needs_pii else {}
        if not bs.conversions_hashed_pii:
            pii = {"country": pii.get("country")}
        browser = signals.load_order_signals(redis, shopify_id) if redis is not None else {}
        event = purchase_from_order(order, items, products, browser, pii, customer_shopify_id)

        out: dict[str, str] = {}
        retry = False
        excluded = (pii.get("country") or "").upper() in {
            c.upper() for c in bs.conversions_exclude_countries
        }
        age = now - (placed_at if placed_at.tzinfo else placed_at.replace(tzinfo=UTC))
        for sender in pending:
            p = sender.platform
            if excluded:
                _record(s, p, event, order.id, "skipped", "excluded country")
                out[p] = "skipped: excluded country"
            elif age > MAX_AGE[p]:
                _record(s, p, event, order.id, "skipped", "too old for this platform")
                out[p] = "skipped: too old"
            elif not sender.supports(event):
                _record(s, p, event, order.id, "skipped", "no click id")
                out[p] = "skipped: no click id"
            else:
                try:
                    sender.send([event])
                    _record(s, p, event, order.id, "sent")
                    out[p] = "sent"
                except IntegrationError as exc:
                    _record(s, p, event, order.id, "failed", scrub(str(exc))[:2000])
                    out[p] = "failed"
                    retry = retry or exc.retryable
        log.info("purchase_reported", order=shopify_id, result=out)
    if retry:
        raise IntegrationError(f"purchase {shopify_id}: retryable failure {out}", retryable=True)
    return out


def flush_browser_events(
    redis: Any,
    *,
    session_factory: SessionFactory = session_scope,
    senders: list[Sender] | None = None,
    batch: int = 500,
) -> dict[str, int]:
    """Forward queued storefront events in batches; best effort (failures are counted, not retried)."""
    raw = signals.pop_browser_events(redis, batch)
    if not raw:
        return {"events": 0}
    events = [from_browser(r["payload"], r.get("ip")) for r in raw]
    senders = senders if senders is not None else configured_senders()
    counts: Counter[tuple[date, str, str, str]] = Counter()
    for e in events:
        counts[(e.time.date(), "hub", e.name, "sent")] += 1  # received by the hub
    for sender in senders:
        mine = [e for e in events if sender.supports(e)]
        for i in range(0, len(mine), sender.batch_size):
            chunk = mine[i : i + sender.batch_size]
            try:
                sender.send(chunk)
                outcome = "sent"
            except IntegrationError as exc:
                log.warning(
                    "browser_events_failed",
                    platform=sender.platform,
                    n=len(chunk),
                    error=str(exc)[:200],
                )
                outcome = "failed"
            for e in chunk:
                counts[(e.time.date(), sender.platform, e.name, outcome)] += 1
    with session_factory() as s:
        for (day, platform, name, outcome), n in counts.items():
            row = s.scalar(
                select(ConversionEventCount).where(
                    ConversionEventCount.date == day,
                    ConversionEventCount.platform == platform,
                    ConversionEventCount.event_name == name,
                )
            ) or ConversionEventCount(
                date=day, platform=platform, event_name=name, sent=0, failed=0
            )
            if outcome == "sent":
                row.sent = (row.sent or 0) + n
            else:
                row.failed = (row.failed or 0) + n
            s.add(row)
    return {"events": len(events)}


def orders_missing_purchase(
    session: Session, platforms: list[str], since: datetime, limit: int = 200
) -> list[int]:
    """Live orders since ``since`` lacking a sent/skipped purchase row for some platform."""
    orders = session.scalars(
        select(
            Order.id,
        )
        .where(Order.placed_at >= since, Order.test.is_(False), Order.cancelled_at.is_(None))
        .order_by(Order.placed_at.desc())
        .limit(limit * 5)
    ).all()
    done: dict[int, set[str]] = {}
    for oid, platform in session.execute(
        select(ConversionEvent.order_id, ConversionEvent.platform).where(
            ConversionEvent.order_id.in_(orders),
            ConversionEvent.event_name == PURCHASE,
            ConversionEvent.status.in_(("sent", "skipped")),
        )
    ):
        done.setdefault(oid, set()).add(platform)
    return [o for o in orders if not set(platforms) <= done.get(o, set())][:limit]


def report(session: Session, days: int = 7, today: date | None = None) -> dict[str, Any]:
    """Tracking health: Shopify orders vs purchases reported, plus storefront event volume."""
    today = today or date.today()
    start = today - timedelta(days=days - 1)
    orders = (
        session.scalar(
            select(func.count(Order.id)).where(
                Order.order_date >= start, Order.test.is_(False), Order.cancelled_at.is_(None)
            )
        )
        or 0
    )
    purchases: dict[str, dict[str, int]] = {}
    for platform, status, n in session.execute(
        select(ConversionEvent.platform, ConversionEvent.status, func.count(ConversionEvent.id))
        .join(Order, Order.id == ConversionEvent.order_id)
        .where(ConversionEvent.event_name == PURCHASE, Order.order_date >= start)
        .group_by(ConversionEvent.platform, ConversionEvent.status)
    ):
        purchases.setdefault(platform, {})[status] = n
    browser: dict[str, dict[str, dict[str, int]]] = {}
    for platform, name, sent, failed in session.execute(
        select(
            ConversionEventCount.platform,
            ConversionEventCount.event_name,
            func.sum(ConversionEventCount.sent),
            func.sum(ConversionEventCount.failed),
        )
        .where(ConversionEventCount.date >= start)
        .group_by(ConversionEventCount.platform, ConversionEventCount.event_name)
    ):
        browser.setdefault(platform, {})[name] = {
            "sent": int(sent or 0),
            "failed": int(failed or 0),
        }
    problems = []
    for platform, st in purchases.items():
        reported = st.get("sent", 0) + st.get("skipped", 0)
        if orders and platform != "google" and reported < 0.9 * orders:
            problems.append(f"{platform}: only {reported}/{orders} orders reported")
        if st.get("failed"):
            problems.append(f"{platform}: {st['failed']} purchase sends failed")
    if orders and not browser.get("hub", {}).get("PageView"):
        problems.append("no storefront events received: is the web pixel connected?")
    return {
        "days": days,
        "orders": orders,
        "purchases": purchases,
        "browser": browser,
        "problems": problems,
    }


# --- setup actions (account changes -> gated + audited) -------------------------------------


def create_pixels(
    platforms: list[str],
    name: str,
    settings: Settings | None = None,
    ctx: ActionContext | None = None,
) -> dict[str, str]:
    """Create the Meta pixel, TikTok pixel and/or Google conversion action. Returns the
    ``.env`` lines to add. Each creation is a gated write (read-only must be off)."""
    s = settings or get_settings()
    out: dict[str, str] = {}
    if "meta" in platforms:
        from app.integrations.ads.meta import MetaAds

        meta = MetaAds(s)
        with write_action(
            "meta.create_pixel",
            target_type="pixel",
            target_id=None,
            payload={"name": name},
            ctx=ctx,
        ) as r:
            pixel = meta._post(f"{meta.act}/adspixels", {"name": name})
            r.data = {"pixel_id": pixel["id"]}
        out["META_PIXEL_ID"] = str(pixel["id"])
    if "tiktok" in platforms:
        from app.integrations.ads.tiktok import TikTokAds

        tt = TikTokAds(s)
        with write_action(
            "tiktok.create_pixel",
            target_type="pixel",
            target_id=None,
            payload={"name": name},
            ctx=ctx,
        ) as r:
            data = tt._request(
                "POST",
                "pixel/create/",
                json_body={"advertiser_id": tt.advertiser_id, "pixel_name": name},
            )
            r.data = {k: data.get(k) for k in ("pixel_id", "pixel_code")}
        out["TIKTOK_PIXEL_ID"] = str(data.get("pixel_id", ""))
        out["TIKTOK_PIXEL_CODE"] = str(data.get("pixel_code", ""))
    if "google" in platforms:
        from app.integrations.ads.google import GoogleAds

        g = GoogleAds(s)
        with write_action(
            "google.create_conversion_action",
            target_type="conversion_action",
            target_id=None,
            payload={"name": name},
            ctx=ctx,
        ) as r:
            rn = g.create_conversion_action(f"{name} (server purchases)", s.store_currency)
            r.data = {"resource_name": rn}
        out["GOOGLE_ADS_CONVERSION_ACTION"] = rn
    return out


WEB_PIXEL_QUERY = "query { webPixel { id settings } }"
WEB_PIXEL_CREATE = """
mutation($settings: JSON!) { webPixelCreate(webPixel: {settings: $settings}) {
  webPixel { id settings } userErrors { code field message } } }
"""
WEB_PIXEL_UPDATE = """
mutation($id: ID!, $settings: JSON!) { webPixelUpdate(id: $id, webPixel: {settings: $settings}) {
  webPixel { id settings } userErrors { code field message } } }
"""


def activate_web_pixel(client: Any, settings: Settings | None = None) -> dict[str, Any]:
    """Connect (or re-point) the hub's web pixel extension on the store."""
    s = settings or get_settings()
    collect_url = s.public_base_url.rstrip("/") + "/collect/pixel"
    if not collect_url.startswith("https://"):
        raise ValueError(
            f"PUBLIC_BASE_URL must be the public https URL (collect URL would be {collect_url})"
        )
    pixel_settings = json.dumps({"collectUrl": collect_url})
    try:
        existing = (client.execute(WEB_PIXEL_QUERY) or {}).get("webPixel")
    except IntegrationError:
        existing = None  # no pixel yet: Shopify answers the query with an error
    if existing:
        res = client.execute(WEB_PIXEL_UPDATE, {"id": existing["id"], "settings": pixel_settings})[
            "webPixelUpdate"
        ]
    else:
        res = client.execute(WEB_PIXEL_CREATE, {"settings": pixel_settings})["webPixelCreate"]
    client.check_user_errors(res, "web pixel")
    return res["webPixel"]
