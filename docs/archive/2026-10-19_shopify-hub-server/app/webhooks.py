"""Inbound webhooks (public via the tunnel). Every request must prove who sent it.

Shopify: ``X-Shopify-Hmac-Sha256`` = base64(HMAC-SHA256(raw body, app client secret)).
The handler only verifies, records and enqueues -- the worker re-fetches the resource
through the API, so payloads (which contain customer PII) are never stored and a forged
or stale payload can't inject data.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from rq import Retry
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from app.config import get_settings
from app.db import session_scope
from app.log import get_logger, scrub
from app.models import WebhookEvent

log = get_logger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# topic -> which payload field holds the resource id the worker should re-fetch
SHOPIFY_TOPICS: dict[str, str] = {
    "orders/create": "id",
    "orders/updated": "id",
    "orders/cancelled": "id",
    "refunds/create": "order_id",
    "products/create": "id",
    "products/update": "id",
    "products/delete": "id",
}
RETRY = Retry(max=5, interval=[10, 30, 120, 600, 1800])


def verify_shopify_hmac(raw: bytes, signature: str, secret: str) -> bool:
    """Constant-time check of Shopify's webhook signature."""
    if not signature or not secret:
        return False
    digest = hmac.new(secret.encode(), raw, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(digest).decode(), signature.strip())


def _record(topic: str, delivery_id: str, resource_id: str | None, sha: str) -> tuple[int, bool]:
    """Insert the event. Returns (event_id, needs_enqueue)."""
    with session_scope() as s:
        existing = s.scalar(select(WebhookEvent).where(WebhookEvent.delivery_id == delivery_id))
        if existing is not None:
            # Duplicate delivery. Re-enqueue only if we never finished it (e.g. Redis was down).
            return existing.id, existing.status in ("received", "failed")
        event = WebhookEvent(
            source="shopify",
            topic=topic,
            delivery_id=delivery_id,
            resource_id=resource_id,
            payload_sha256=sha,
            status="received" if resource_id else "ignored",
        )
        s.add(event)
        try:
            s.flush()
        except IntegrityError:  # raced with a parallel duplicate delivery
            s.rollback()
            return 0, False
        return event.id, bool(resource_id)


def _enqueue(event_id: int) -> None:
    from app.queue import get_queue

    get_queue("high").enqueue("app.jobs.shopify.process_webhook", event_id, retry=RETRY)


@router.post("/shopify", status_code=200)
async def shopify_webhook(request: Request) -> dict[str, Any]:
    settings = get_settings()
    secret = settings.shopify_client_secret.get_secret_value()
    if not secret:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Shopify webhooks not configured")

    raw = await request.body()
    if not verify_shopify_hmac(raw, request.headers.get("X-Shopify-Hmac-Sha256", ""), secret):
        log.warning("shopify_webhook_bad_hmac", topic=request.headers.get("X-Shopify-Topic"))
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid signature")

    shop = request.headers.get("X-Shopify-Shop-Domain", "")
    if settings.shopify_store_domain and shop != settings.shopify_store_domain:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "unexpected shop")

    topic = request.headers.get("X-Shopify-Topic", "").lower()
    delivery_id = request.headers.get("X-Shopify-Webhook-Id") or request.headers.get(
        "X-Shopify-Event-Id"
    )
    if not delivery_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "missing X-Shopify-Webhook-Id")

    resource_id: str | None = None
    if topic in SHOPIFY_TOPICS:
        try:
            resource_id = str(json.loads(raw)[SHOPIFY_TOPICS[topic]])
        except (ValueError, KeyError, TypeError):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "unexpected payload") from None

    event_id, needs_enqueue = await run_in_threadpool(
        _record, topic, delivery_id, resource_id, hashlib.sha256(raw).hexdigest()
    )
    if needs_enqueue:
        try:
            await run_in_threadpool(_enqueue, event_id)
        except Exception as exc:
            # Non-2xx makes Shopify retry later; the stored event lets us resume then.
            log.error("shopify_webhook_enqueue_failed", error=scrub(str(exc)))
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "queue unavailable") from exc
    log.info("shopify_webhook", topic=topic, event_id=event_id, queued=needs_enqueue)
    return {"status": "ok"}


# --- Higgsfield -------------------------------------------------------------------------------
# Higgsfield webhooks are unsigned, so the URL carries a secret token and the payload is only
# a nudge: the worker re-checks the job through the authenticated status API.


def _enqueue_higgsfield_poll(request_id: str) -> None:
    from app.queue import get_queue

    get_queue("high").enqueue("app.jobs.creatives.poll_request", request_id)


@router.post("/higgsfield/{token}", status_code=200)
async def higgsfield_webhook(token: str, request: Request) -> dict[str, Any]:
    expected = get_settings().higgsfield_webhook_token.get_secret_value()
    if not expected or not hmac.compare_digest(token.encode(), expected.encode()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    raw = await request.body()
    try:
        request_id = str(json.loads(raw)["request_id"])[:128]
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "unexpected payload") from None
    try:
        await run_in_threadpool(_enqueue_higgsfield_poll, request_id)
    except Exception as exc:
        log.error("higgsfield_webhook_enqueue_failed", error=scrub(str(exc)))
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "queue unavailable"
        ) from exc  # retried by Higgsfield
    return {"status": "ok"}
