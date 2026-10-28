"""Conversion jobs. All of them no-op until conversions_enabled is on."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app import business_settings
from app.config import get_settings
from app.conversions import service
from app.conversions.senders import configured_senders
from app.db import session_scope
from app.jobs.tracking import track_job
from app.queue import get_queue, get_redis

RETRY_INTERVALS = [60, 300, 1800, 7200]


def _enabled() -> bool:
    with session_scope() as s:
        bs = business_settings.load(s)
    return bs.conversions_enabled and not bs.kill_switch


def schedule_purchase(order_id: int) -> None:
    """Called after a new order is synced: report it after a short delay so the
    checkout's browser signals (cookies, IP, user agent) have reached the hub."""
    if not _enabled():
        return
    from rq import Retry

    get_queue("default").enqueue_in(
        timedelta(seconds=get_settings().conversions_purchase_delay_s),
        "app.jobs.conversions.send_purchase",
        order_id,
        retry=Retry(max=len(RETRY_INTERVALS), interval=RETRY_INTERVALS),
    )


def send_purchase(order_id: int) -> dict[str, str]:
    return service.send_purchase(order_id, redis=get_redis())


def flush_browser_events() -> None:
    """Every minute: forward queued storefront events (drains up to 10 batches)."""
    if not _enabled():
        return
    redis = get_redis()
    for _ in range(10):
        if service.flush_browser_events(redis)["events"] == 0:
            break


def sweep() -> None:
    """Every 15 min: report recent orders that never got a purchase (missed webhook, outage)."""
    with track_job("conversions_sweep") as stats:
        if not _enabled():
            stats["skipped"] = "conversions disabled"
            return
        platforms = [s.platform for s in configured_senders()]
        if not platforms:
            stats["skipped"] = "no platform configured"
            return
        since = datetime.now(UTC) - timedelta(days=3)
        with session_scope() as s:
            missing = service.orders_missing_purchase(s, platforms, since)
        for order_id in missing:
            try:
                service.send_purchase(order_id, redis=get_redis())
            except Exception:  # noqa: S112 - the next sweep retries; keep going
                continue
        stats["checked"] = len(missing)
