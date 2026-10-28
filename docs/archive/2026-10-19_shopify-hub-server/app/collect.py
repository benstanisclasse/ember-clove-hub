"""``POST /collect/pixel``: storefront events from the hub's Shopify web pixel (public).

The browser can't keep a secret, so this endpoint is hardened instead of authenticated:
strict schema + size limit, per-IP rate limit, no PII accepted, and nothing is stored
except short-lived signals in Redis. When conversions are disabled it returns at once.
Responses carry ``Access-Control-Allow-Origin: *`` (the pixel posts as text/plain, so no
CORS preflight is needed).
"""

from __future__ import annotations

import json
import time
from typing import Any

from fastapi import APIRouter, Request, Response
from starlette.concurrency import run_in_threadpool

from app.conversions import signals
from app.conversions.events import BROWSER_EVENTS, PURCHASE, order_id_from_checkout
from app.log import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/collect", tags=["collect"])

MAX_BODY = 16 * 1024
RATE_LIMIT_PER_MIN = 300
ALLOWED = BROWSER_EVENTS | {PURCHASE}
CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type"}
FIELDS = {
    "name",
    "id",
    "ts",
    "url",
    "referrer",
    "ua",
    "fbp",
    "fbc",
    "ttp",
    "clientId",
    "value",
    "currency",
    "items",
    "orderId",
}


def client_ip(request: Request) -> str | None:
    """Real visitor IP: Cloudflare's header first, then the proxy chain, then the socket."""
    for header in ("cf-connecting-ip", "x-forwarded-for"):
        value = request.headers.get(header)
        if value:
            return value.split(",")[0].strip()[:64]
    return request.client.host if request.client else None


def _rate_limited(redis: Any, ip: str | None) -> bool:
    key = f"hub:rl:collect:{ip or 'unknown'}:{int(time.time() // 60)}"
    n = redis.incr(key)
    if n == 1:
        redis.expire(key, 120)
    return int(n) > RATE_LIMIT_PER_MIN


def validate(payload: Any) -> dict[str, Any] | None:
    """Keep only known fields; reject anything malformed (returns None)."""
    if not isinstance(payload, dict) or payload.get("name") not in ALLOWED or not payload.get("id"):
        return None
    clean = {k: v for k, v in payload.items() if k in FIELDS}
    for k, v in clean.items():
        if k == "items":
            if not isinstance(v, list) or len(v) > 50:
                return None
        elif v is not None and not isinstance(v, str | int | float):
            return None
    return clean


def _handle(raw: bytes, ip: str | None) -> int:
    from app.conversions.service import conversions_on
    from app.queue import get_redis

    if not conversions_on():
        return 204
    redis = get_redis()
    if _rate_limited(redis, ip):
        return 429
    try:
        payload = validate(json.loads(raw))
    except ValueError:
        payload = None
    if payload is None:
        return 400
    if payload["name"] == PURCHASE:
        order_id = order_id_from_checkout(payload.get("orderId"))
        if order_id:
            signals.save_order_signals(
                redis,
                order_id,
                {k: payload.get(k) for k in ("fbp", "fbc", "ttp", "url", "ua")} | {"ip": ip},
            )
        return 204
    return 204 if signals.enqueue_browser_event(redis, {"payload": payload, "ip": ip}) else 503


@router.options("/pixel", include_in_schema=False)
def preflight() -> Response:
    return Response(status_code=204, headers=CORS)


@router.post("/pixel", include_in_schema=False)
async def collect_pixel(request: Request) -> Response:
    raw = await request.body()
    if len(raw) > MAX_BODY:
        return Response(status_code=413, headers=CORS)
    status = await run_in_threadpool(_handle, raw, client_ip(request))
    return Response(status_code=status, headers=CORS)
