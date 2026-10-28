"""Shopify background jobs (RQ). All of them no-op cleanly until Shopify is configured."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select

from app.config import get_settings
from app.db import session_scope
from app.integrations.http import NotConfiguredError
from app.integrations.shopify import sync
from app.integrations.shopify.client import ShopifyClient
from app.jobs.tracking import track_job
from app.log import get_logger, scrub
from app.models import Product, WebhookEvent
from app.queue import get_redis

log = get_logger(__name__)
ORDER_TOPICS = {"orders/create", "orders/updated", "orders/cancelled", "refunds/create"}
PRODUCT_TOPICS = {"products/create", "products/update"}


def get_client() -> ShopifyClient:
    return ShopifyClient(get_settings(), redis=get_redis())


@contextmanager
def _lock(name: str, timeout: int = 120) -> Iterator[None]:
    """Serialize work on one resource across workers (two webhooks for the same order)."""
    lock = get_redis().lock(f"hub:lock:{name}", timeout=timeout, blocking_timeout=timeout)
    if not lock.acquire():
        raise TimeoutError(f"could not lock {name}")
    try:
        yield
    finally:
        try:
            lock.release()
        except Exception:  # noqa: S110 - lock already expired
            pass


def process_webhook(event_id: int) -> str:
    """Handle one stored webhook event: re-fetch the resource and upsert it."""
    with session_scope() as s:
        event = s.get(WebhookEvent, event_id)
        if event is None or event.status in ("processed", "ignored"):
            return "skip"
        topic, resource_id = event.topic, int(event.resource_id or 0)
    new_order_id: int | None = None
    try:
        client = get_client()
        with _lock(f"shopify:{topic.split('/')[0]}:{resource_id}"), session_scope() as s:
            if topic in ORDER_TOPICS:
                order = sync.sync_order(client, s, resource_id)
                new_order_id = order.id if order is not None and topic == "orders/create" else None
            elif topic in PRODUCT_TOPICS:
                sync.sync_product(client, s, resource_id)
            elif topic == "products/delete":
                p = s.scalar(select(Product).where(Product.shopify_id == resource_id))
                if p is not None:
                    p.active = False
        _mark(event_id, "processed")
        if new_order_id is not None:
            from app.jobs.conversions import schedule_purchase

            schedule_purchase(new_order_id)  # no-op unless conversions are enabled
        return "processed"
    except Exception as exc:
        _mark(event_id, "failed", scrub(repr(exc))[:2000])
        raise  # RQ retries with backoff


def _mark(event_id: int, status: str, error: str | None = None) -> None:
    with session_scope() as s:
        event = s.get(WebhookEvent, event_id)
        if event is not None:
            event.status, event.error = status, error
            event.processed_at = datetime.now(UTC)


def _skip_if_unconfigured(stats: dict[str, Any]) -> ShopifyClient | None:
    try:
        return get_client()
    except NotConfiguredError:
        stats["skipped"] = "shopify not configured"
        return None


def incremental_orders() -> None:
    """Every 15 min: safety net for missed webhooks (orders updated since the cursor)."""
    with track_job("shopify_orders") as stats:
        client = _skip_if_unconfigured(stats)
        if client:
            with _lock("shopify:orders:incremental", timeout=1800):
                stats.update(sync.sync_orders(client, session_scope))


def nightly_products() -> None:
    """Daily: full product + variant cost refresh (catches cost edits, which send no webhook)."""
    with track_job("shopify_products") as stats:
        client = _skip_if_unconfigured(stats)
        if client:
            stats.update(sync.sync_products(client, session_scope))


def backfill(kind: str = "all", days: int | None = None) -> dict[str, int]:
    """Initial import. ``kind``: products | customers | orders | all."""
    client = get_client()
    out: dict[str, int] = {}
    with track_job(f"shopify_backfill_{kind}") as stats:
        if kind in ("products", "all"):
            out |= sync.sync_products(client, session_scope)
        if kind in ("customers", "all"):
            out |= sync.sync_customers(client, session_scope)
        if kind in ("orders", "all"):
            since = datetime.now(UTC) - timedelta(
                days=days or client.settings.shopify_backfill_days
            )
            out |= sync.sync_orders(client, session_scope, since=since, field="created_at")
        stats.update(out)
    return out
