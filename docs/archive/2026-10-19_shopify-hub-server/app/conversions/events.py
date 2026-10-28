"""Platform-neutral conversion event + builders from storefront payloads and orders."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from urllib.parse import parse_qs, urlsplit

from app.conversions.hashing import hash_email, hash_external_id, hash_phone
from app.integrations.shopify.mapping import gid_to_int

# Canonical names (Meta's standard events); each sender maps to its platform's names.
BROWSER_EVENTS = {"PageView", "ViewContent", "AddToCart", "InitiateCheckout"}
PURCHASE = "Purchase"
_MAX = 1024  # cap on any free-text field from the browser


@dataclass
class Item:
    id: str
    quantity: int
    price: Decimal


@dataclass
class Event:
    name: str
    event_id: str
    time: datetime
    url: str | None = None
    referrer: str | None = None
    ip: str | None = None
    user_agent: str | None = None
    fbp: str | None = None
    fbc: str | None = None
    ttp: str | None = None
    ttclid: str | None = None
    gclid: str | None = None
    gbraid: str | None = None
    wbraid: str | None = None
    email_hash: str | None = None
    phone_hash: str | None = None
    external_id_hash: str | None = None
    value: Decimal | None = None
    currency: str | None = None
    order_id: str | None = None
    items: list[Item] = field(default_factory=list)

    @property
    def unix_time(self) -> int:
        return int(self.time.timestamp())


def _s(value: Any, limit: int = _MAX) -> str | None:
    if value in (None, ""):
        return None
    return str(value)[:limit]


def _dec(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value)) if value not in (None, "") else None
    except ArithmeticError:
        return None


def url_params(url: str | None) -> dict[str, str]:
    if not url:
        return {}
    try:
        return {k.lower(): v[0] for k, v in parse_qs(urlsplit(url).query).items() if v}
    except ValueError:
        return {}


def fbc_from(fbc_cookie: str | None, url: str | None, now_ms: int | None = None) -> str | None:
    """Meta click id: the _fbc cookie, else build ``fb.1.<ms>.<fbclid>`` from the landing URL."""
    if fbc_cookie:
        return fbc_cookie
    fbclid = url_params(url).get("fbclid")
    return f"fb.1.{now_ms or int(time.time() * 1000)}.{fbclid}" if fbclid else None


def from_browser(payload: dict[str, Any], ip: str | None) -> Event:
    """Build an Event from a web-pixel payload (already validated by /collect)."""
    url = _s(payload.get("url"))
    params = url_params(url)
    ts = payload.get("ts")
    try:
        when = datetime.fromisoformat(str(ts).replace("Z", "+00:00")) if ts else datetime.now(UTC)
    except ValueError:
        when = datetime.now(UTC)
    items = [
        Item(
            # gid://shopify/Product/123 -> "123", matching the ids in server-side purchases
            id=str(gid_to_int(str(i.get("id"))) or i.get("id"))[:64],
            quantity=int(i.get("quantity") or 1),
            price=_dec(i.get("price")) or Decimal("0"),
        )
        for i in (payload.get("items") or [])[:50]
        if i.get("id")
    ]
    return Event(
        name=str(payload["name"]),
        event_id=_s(payload.get("id"), 128) or "",
        time=when,
        url=url,
        referrer=_s(payload.get("referrer")),
        ip=_s(ip, 64),
        user_agent=_s(payload.get("ua"), 512),
        fbp=_s(payload.get("fbp"), 256),
        fbc=fbc_from(_s(payload.get("fbc"), 512), url),
        ttp=_s(payload.get("ttp"), 256),
        ttclid=_s(params.get("ttclid"), 512),
        external_id_hash=hash_external_id(payload.get("clientId")),
        value=_dec(payload.get("value")),
        currency=_s(payload.get("currency"), 3),
        items=items,
    )


def purchase_from_order(
    order: Any,
    items: list[Any],
    product_shopify_ids: dict[int, int],
    signals: dict[str, Any],
    pii: dict[str, Any],
    customer_shopify_id: int | None = None,
) -> Event:
    """The server-side Purchase for one order (``order`` / ``items`` are ORM rows)."""
    url = signals.get("url") or order.landing_site
    return Event(
        name=PURCHASE,
        event_id=str(order.shopify_id),
        time=order.placed_at if order.placed_at.tzinfo else order.placed_at.replace(tzinfo=UTC),
        url=url,
        ip=signals.get("ip"),
        user_agent=signals.get("ua"),
        fbp=signals.get("fbp"),
        fbc=fbc_from(signals.get("fbc"), url)
        or (
            f"fb.1.{int(order.placed_at.timestamp() * 1000)}.{order.fbclid}"
            if order.fbclid
            else None
        ),
        ttp=signals.get("ttp"),
        ttclid=order.ttclid or url_params(url).get("ttclid"),
        gclid=order.gclid if order.gclid and not str(order.gclid).startswith("0A") else None,
        gbraid=order.gclid if order.gclid and str(order.gclid).startswith("0A") else None,
        email_hash=hash_email(pii.get("email")),
        phone_hash=hash_phone(pii.get("phone")),
        external_id_hash=hash_external_id(customer_shopify_id),
        value=(order.total_price - order.total_tax).quantize(Decimal("0.01")),
        currency=order.currency,
        order_id=str(order.shopify_id),
        items=[
            Item(
                id=str(product_shopify_ids.get(i.product_id) or i.sku or i.shopify_id),
                quantity=i.quantity,
                price=i.price,
            )
            for i in items
        ],
    )


def order_id_from_checkout(value: Any) -> int | None:
    """checkout.order.id from the web pixel (a gid or a number) -> Shopify order id."""
    return gid_to_int(str(value)) if value not in (None, "") else None
