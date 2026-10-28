"""Short-lived browser signals in Redis.

* ``hub:conv:order:<order_id>`` -- the checkout's cookies / IP / user agent, captured by
  the web pixel's checkout_completed event, kept 7 days so the server-side purchase
  (sent after the order webhook) can include them.
* ``hub:conv:queue`` -- storefront events waiting to be forwarded in batches.

IP and user agent exist only here, transiently (they're required for event matching);
they're never written to Postgres.
"""

from __future__ import annotations

import json
from typing import Any

ORDER_KEY = "hub:conv:order:{}"
QUEUE_KEY = "hub:conv:queue"
ORDER_TTL_S = 7 * 24 * 3600
MAX_QUEUE = 100_000  # drop new events rather than exhaust Redis memory if the sender is down


def save_order_signals(redis: Any, order_id: int, signals: dict[str, Any]) -> None:
    redis.set(ORDER_KEY.format(order_id), json.dumps(signals), ex=ORDER_TTL_S)


def load_order_signals(redis: Any, order_id: int) -> dict[str, Any]:
    raw = redis.get(ORDER_KEY.format(order_id))
    return json.loads(raw) if raw else {}


def enqueue_browser_event(redis: Any, event: dict[str, Any]) -> bool:
    if redis.llen(QUEUE_KEY) >= MAX_QUEUE:
        return False
    redis.rpush(QUEUE_KEY, json.dumps(event))
    return True


def pop_browser_events(redis: Any, limit: int = 500) -> list[dict[str, Any]]:
    """Atomically take up to ``limit`` queued events."""
    pipe = redis.pipeline()
    pipe.lrange(QUEUE_KEY, 0, limit - 1)
    pipe.ltrim(QUEUE_KEY, limit, -1)
    raw, _ = pipe.execute()
    return [json.loads(r) for r in raw]
