"""Shopify webhook endpoint + worker processing (HMAC, shop check, dedupe, re-enqueue)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest
import shopify_fixtures as fx
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app import webhooks
from app.config import get_settings
from app.models import Order, WebhookEvent

SECRET = "whsec-test"
SHOP = "demo.myshopify.com"


def sign(body: bytes, secret: str = SECRET) -> str:
    return base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()


@pytest.fixture
def app_env(db_url: str, engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Iterator[list[int]]:
    """Point the app's own session_scope at the test DB and capture enqueued event ids."""
    import app.db as db

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("SHOPIFY_STORE_DOMAIN", SHOP)
    monkeypatch.setenv("SHOPIFY_CLIENT_ID", "cid")
    monkeypatch.setenv("SHOPIFY_CLIENT_SECRET", SECRET)
    monkeypatch.setenv("STORE_TIMEZONE", "America/New_York")
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()
    queued: list[int] = []
    monkeypatch.setattr(webhooks, "_enqueue", queued.append)
    yield queued
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()


@pytest.fixture
def client(app_env: list[int]) -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def post(
    client: TestClient, topic: str, payload: dict[str, Any], delivery: str = "d-1", **hdr: str
) -> Any:
    body = json.dumps(payload).encode()
    headers = {
        "X-Shopify-Hmac-Sha256": hdr.pop("sig", sign(body)),
        "X-Shopify-Topic": topic,
        "X-Shopify-Shop-Domain": hdr.pop("shop", SHOP),
        "X-Shopify-Webhook-Id": delivery,
        "Content-Type": "application/json",
    }
    return client.post("/webhooks/shopify", content=body, headers=headers)


def test_hmac_helper() -> None:
    assert webhooks.verify_shopify_hmac(b"abc", sign(b"abc"), SECRET)
    assert not webhooks.verify_shopify_hmac(b"abc", sign(b"abd"), SECRET)
    assert not webhooks.verify_shopify_hmac(b"abc", "", SECRET)


def test_valid_webhook_is_recorded_and_queued(
    client: TestClient, app_env: list[int], session: Session
) -> None:
    resp = post(client, "orders/create", {"id": 5001, "email": "pii@example.com"})
    assert resp.status_code == 200
    event = session.scalars(select(WebhookEvent)).one()
    assert (event.topic, event.resource_id, event.status) == ("orders/create", "5001", "received")
    assert app_env == [event.id]


def test_refund_webhook_targets_its_order(client: TestClient, session: Session) -> None:
    post(client, "refunds/create", {"id": 77, "order_id": 5001})
    assert session.scalars(select(WebhookEvent)).one().resource_id == "5001"


def test_bad_signature_and_wrong_shop_rejected(client: TestClient, app_env: list[int]) -> None:
    assert post(client, "orders/create", {"id": 1}, sig="bogus").status_code == 401
    assert post(client, "orders/create", {"id": 1}, shop="evil.myshopify.com").status_code == 403
    assert app_env == []


def test_duplicate_delivery_not_requeued_once_processed(
    client: TestClient, app_env: list[int], session: Session
) -> None:
    post(client, "orders/create", {"id": 1}, delivery="same")
    post(client, "orders/create", {"id": 1}, delivery="same")  # still 'received' -> re-enqueue
    assert len(app_env) == 2
    event = session.scalars(select(WebhookEvent)).one()
    event.status = "processed"
    session.commit()
    post(client, "orders/create", {"id": 1}, delivery="same")
    assert len(app_env) == 2


def test_unknown_topic_is_ignored(client: TestClient, app_env: list[int], session: Session) -> None:
    assert post(client, "app/uninstalled", {"id": 1}).status_code == 200
    assert session.scalars(select(WebhookEvent)).one().status == "ignored"
    assert app_env == []


def test_queue_down_returns_503_so_shopify_retries(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(_id: int) -> None:
        raise ConnectionError("redis down")

    monkeypatch.setattr(webhooks, "_enqueue", boom)
    assert post(client, "orders/create", {"id": 1}).status_code == 503


def test_not_configured_returns_503(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHOPIFY_CLIENT_SECRET", "")
    get_settings.cache_clear()
    assert post(client, "orders/create", {"id": 1}).status_code == 503


def test_worker_refetches_and_upserts(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, session: Session
) -> None:
    from app.jobs import shopify as jobs

    class Fake:
        settings = get_settings()

        def execute(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
            assert variables == {"id": "gid://shopify/Order/5001"}
            return {"order": fx.order(5001)}

    @contextmanager
    def no_lock(_name: str, timeout: int = 120) -> Iterator[None]:
        yield

    monkeypatch.setattr(jobs, "get_client", lambda: Fake())
    monkeypatch.setattr(jobs, "_lock", no_lock)
    post(client, "orders/updated", {"id": 5001})
    event_id = session.scalars(select(WebhookEvent)).one().id
    session.commit()  # release SQLite read lock before the worker writes
    assert jobs.process_webhook(event_id) == "processed"
    assert jobs.process_webhook(event_id) == "skip"
    session.expire_all()
    assert session.scalars(select(Order)).one().shopify_id == 5001
    assert session.get(WebhookEvent, event_id).status == "processed"
