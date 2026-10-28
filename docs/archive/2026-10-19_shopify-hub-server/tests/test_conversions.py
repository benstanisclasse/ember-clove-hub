"""Conversions: hashing, payloads, once-per-platform purchases, batching, /collect, setup."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D
from typing import Any
from zoneinfo import ZoneInfo

import fakeredis
import httpx
import pytest
import shopify_fixtures as fx
from ads_mock import MockHTTP, body, form
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app import business_settings
from app.config import Settings, get_settings
from app.conversions import service, signals
from app.conversions.events import Event, Item, fbc_from, from_browser
from app.conversions.hashing import hash_email, hash_phone, normalize_phone, sha256
from app.conversions.senders import GoogleClickConversions, MetaCapi, Sender, TikTokEvents
from app.integrations.http import IntegrationError
from app.integrations.shopify import sync as shopify_sync
from app.integrations.shopify.mapping import parse_order
from app.models import ConversionEvent, ConversionEventCount

NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)

# --- hashing + event building -------------------------------------------------------------


def test_hashing_normalizes_first() -> None:
    assert hash_email("  Jane.Doe@Example.COM ") == sha256("jane.doe@example.com")
    assert hash_email("not-an-email") is None
    assert normalize_phone("+1 (415) 555-0100") == "14155550100"
    assert normalize_phone("(415) 555-0100") == "14155550100"  # US default country code
    assert normalize_phone("0044 20 7946 0958") == "442079460958"
    assert hash_phone("123") is None


def test_browser_event_builds_fbc_ttclid_and_numeric_ids() -> None:
    e = from_browser(
        {
            "name": "AddToCart",
            "id": "evt-1",
            "ts": "2026-10-01T10:00:00Z",
            "url": "https://shop.com/p?fbclid=FBX&ttclid=TTX",
            "ua": "UA",
            "fbp": "fb.1.1.2",
            "items": [{"id": "gid://shopify/Product/123", "quantity": 2, "price": 9.5}],
            "value": 19,
            "currency": "USD",
        },
        ip="1.2.3.4",
    )
    assert e.fbc and e.fbc.endswith(".FBX") and e.ttclid == "TTX"
    assert e.items[0].id == "123" and e.items[0].price == D("9.5") and e.ip == "1.2.3.4"
    assert fbc_from("fb.1.9.cookie", "https://x/?fbclid=Y") == "fb.1.9.cookie"  # cookie wins


# --- sender payloads ------------------------------------------------------------------------


def purchase(**kw: Any) -> Event:
    base = dict(
        name="Purchase",
        event_id="5001",
        time=NOW,
        value=D("100.00"),
        currency="USD",
        order_id="5001",
        items=[Item("1", 2, D("50"))],
    )
    return Event(**{**base, **kw})


def test_meta_payload_action_source_and_hashes() -> None:
    m = MetaCapi(Settings())
    web = m.payload(
        purchase(
            user_agent="UA", ip="1.1.1.1", email_hash="h1", fbc="fb.1.1.X", url="https://shop/x"
        )
    )
    assert web["action_source"] == "website" and web["user_data"]["em"] == ["h1"]
    assert web["custom_data"]["contents"] == [{"id": "1", "quantity": 2, "item_price": 50.0}]
    assert m.payload(purchase())["action_source"] == "system_generated"  # no browser signals


def test_meta_send_shape() -> None:
    mock = MockHTTP().on("POST", "/777/events", {"events_received": 1})
    s = Settings(
        meta_system_user_token=SecretStr("EAAtok"),
        meta_pixel_id="777",
        meta_app_secret=SecretStr("sec"),
        meta_capi_test_event_code="TEST1",
    )
    assert MetaCapi(s, http=mock.client(), sleep=lambda x: None).send([purchase()]) == 1
    f = form(mock.calls[0])
    assert f["test_event_code"] == "TEST1" and "appsecret_proof" in f
    assert json.loads(f["data"])[0]["event_name"] == "Purchase"


def test_tiktok_payload_and_errors() -> None:
    s = Settings(tiktok_events_access_token=SecretStr("evtok"), tiktok_pixel_code="CPIX")
    t = TikTokEvents(
        s,
        http=MockHTTP().on("POST", "event/track", {"code": 0, "data": {}}).client(),
        sleep=lambda x: None,
    )
    assert not t.supports(Event(name="PageView", event_id="x", time=NOW))
    assert t.payload(purchase(ttclid="TT"))["event"] == "CompletePayment"
    t.send([purchase()])
    sent = body(t.http._transport.handler.calls[0])  # type: ignore[attr-defined]
    assert sent["event_source"] == "web" and sent["event_source_id"] == "CPIX"
    bad = TikTokEvents(
        s, http=MockHTTP().on("POST", "event/track", {"code": 40002, "message": "bad"}).client()
    )
    with pytest.raises(IntegrationError, match="40002"):
        bad.send([purchase()])


def test_google_payload_and_partial_failure() -> None:
    s = Settings(google_ads_conversion_action="customers/1/conversionActions/9")

    class FakeGoogle:
        def __init__(self, resp: dict[str, Any]) -> None:
            self.resp, self.sent = resp, []

        def upload_click_conversions(self, conversions: list[dict[str, Any]]) -> dict[str, Any]:
            self.sent.extend(conversions)
            return self.resp

    g = GoogleClickConversions(s, client=FakeGoogle({"results": [{}]}))
    assert not g.supports(purchase())  # no click id
    assert g.send([purchase(gclid="GCL")]) == 1
    p = g.client.sent[0]
    assert (
        p["gclid"] == "GCL"
        and p["conversionDateTime"] == "2026-10-02 12:00:00+00:00"
        and p["orderId"] == "5001"
    )
    assert GoogleClickConversions(s).payload(purchase(gbraid="0AAB"))["gbraid"] == "0AAB"
    failing = GoogleClickConversions(
        s, client=FakeGoogle({"partialFailureError": {"message": "expired click"}})
    )
    with pytest.raises(IntegrationError, match="expired click"):
        failing.send([purchase(gclid="old")])


# --- once-per-platform purchases -------------------------------------------------------------


class FakeSender(Sender):
    def __init__(
        self, platform: str, fail: IntegrationError | None = None, needs_click: bool = False
    ) -> None:
        self.platform, self.fail, self.needs_click = platform, fail, needs_click
        self.sent: list[Event] = []

    def supports(self, event: Event) -> bool:
        return not self.needs_click or bool(event.gclid)

    def send(self, events: list[Event]) -> int:
        if self.fail:
            raise self.fail
        self.sent.extend(events)
        return len(events)


def _enable(factory, **extra: object) -> None:  # type: ignore[no-untyped-def]
    with factory() as s:
        business_settings.set_value(s, "conversions_enabled", True, actor="test")
        for k, v in extra.items():
            business_settings.set_value(s, k, v, actor="test")


def _order(factory, **kw: Any) -> int:  # type: ignore[no-untyped-def]
    node = fx.order(
        processed_at="2026-10-01T15:00:00Z",
        last_visit=fx.visit("https://shop.com/?gclid=GCL1&fbclid=FB1"),
        **kw,
    )
    with factory() as s:
        return shopify_sync.upsert_order(
            s, parse_order(node, ZoneInfo("America/New_York"), 2.9, 0.3)
        ).id


def test_disabled_by_default_sends_nothing(session_factory) -> None:  # type: ignore[no-untyped-def]
    oid = _order(session_factory)
    meta = FakeSender("meta")
    assert service.send_purchase(oid, session_factory=session_factory, senders=[meta], now=NOW) == {
        "all": "disabled"
    }
    assert meta.sent == []


def test_purchase_sent_once_per_platform_with_hashed_pii(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    _enable(session_factory)
    oid = _order(session_factory)
    redis = fakeredis.FakeRedis()
    signals.save_order_signals(redis, 5001, {"ua": "UA", "ip": "9.9.9.9", "fbp": "fb.1.1.1"})
    meta, google = FakeSender("meta"), FakeSender("google", needs_click=True)
    pii = lambda _id: {"email": "Jane@Example.com", "phone": "+1 415 555 0100", "country": "US"}  # noqa: E731
    out = service.send_purchase(
        oid,
        session_factory=session_factory,
        redis=redis,
        senders=[meta, google],
        pii_fetcher=pii,
        now=NOW,
    )
    assert out == {"meta": "sent", "google": "sent"}
    e = meta.sent[0]
    assert e.email_hash == sha256("jane@example.com") and e.phone_hash == sha256("14155550100")
    assert (e.user_agent, e.ip, e.fbp) == ("UA", "9.9.9.9", "fb.1.1.1")  # merged browser signals
    assert e.value == D("100.00") and e.gclid == "GCL1" and e.fbc and e.fbc.endswith(".FB1")
    # retries / sweeps never double-report
    again = service.send_purchase(
        oid,
        session_factory=session_factory,
        redis=redis,
        senders=[meta, google],
        pii_fetcher=pii,
        now=NOW,
    )
    assert again == {"all": "already sent"} and len(meta.sent) == 1
    rows = session.scalars(select(ConversionEvent)).all()
    assert {(r.platform, r.status) for r in rows} == {("meta", "sent"), ("google", "sent")}


def test_pii_off_excluded_country_old_and_no_click(session_factory) -> None:  # type: ignore[no-untyped-def]
    _enable(session_factory, conversions_hashed_pii=False)
    oid = _order(session_factory)
    meta = FakeSender("meta")
    service.send_purchase(
        oid,
        session_factory=session_factory,
        senders=[meta],
        pii_fetcher=lambda _i: {"email": "a@b.co", "country": "US"},
        now=NOW,
    )
    assert meta.sent[0].email_hash is None

    _enable(session_factory, conversions_exclude_countries=["DE"])
    oid2 = _order(session_factory, oid=5002)
    meta2 = FakeSender("meta")
    out = service.send_purchase(
        oid2,
        session_factory=session_factory,
        senders=[meta2],
        pii_fetcher=lambda _i: {"country": "de"},
        now=NOW,
    )
    assert out == {"meta": "skipped: excluded country"} and meta2.sent == []

    oid3 = _order(session_factory, oid=5003)
    late = NOW + timedelta(days=10)
    out = service.send_purchase(
        oid3,
        session_factory=session_factory,
        senders=[FakeSender("meta"), FakeSender("google")],
        pii_fetcher=lambda _i: {"country": "US"},
        now=late,
    )
    assert out == {"meta": "skipped: too old", "google": "sent"}


def test_retryable_failure_is_recorded_then_retried(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    _enable(session_factory)
    oid = _order(session_factory)
    flaky = FakeSender("tiktok", fail=IntegrationError("503", retryable=True))
    with pytest.raises(IntegrationError):
        service.send_purchase(
            oid,
            session_factory=session_factory,
            senders=[flaky],
            pii_fetcher=lambda _i: {},
            now=NOW,
        )
    assert session.scalars(select(ConversionEvent)).one().status == "failed"
    flaky.fail = None
    assert service.send_purchase(
        oid, session_factory=session_factory, senders=[flaky], pii_fetcher=lambda _i: {}, now=NOW
    ) == {"tiktok": "sent"}
    session.expire_all()
    row = session.scalars(select(ConversionEvent)).one()
    assert (row.status, row.attempts) == ("sent", 2)


def test_test_and_cancelled_orders_are_never_reported(session_factory) -> None:  # type: ignore[no-untyped-def]
    _enable(session_factory)
    oid = _order(session_factory, test=True)
    assert service.send_purchase(
        oid, session_factory=session_factory, senders=[FakeSender("meta")], now=NOW
    ) == {"all": "test or cancelled"}


def test_sweep_finds_unreported_orders(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    _enable(session_factory)
    a, b = _order(session_factory), _order(session_factory, oid=5002)
    service.send_purchase(
        a,
        session_factory=session_factory,
        senders=[FakeSender("meta")],
        pii_fetcher=lambda _i: {},
        now=NOW,
    )
    since = datetime(2026, 9, 30, tzinfo=UTC)
    assert service.orders_missing_purchase(session, ["meta"], since) == [b]


def test_flush_browser_events_batches_and_counts(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    redis = fakeredis.FakeRedis()
    for i, name in enumerate(["PageView", "PageView", "AddToCart"]):
        signals.enqueue_browser_event(
            redis,
            {
                "payload": {"name": name, "id": f"e{i}", "ts": "2026-10-01T10:00:00Z"},
                "ip": "1.1.1.1",
            },
        )
    meta, tiktok = FakeSender("meta"), FakeSender("tiktok")
    tiktok.supports = lambda e: e.name != "PageView"  # type: ignore[method-assign]
    assert service.flush_browser_events(
        redis, session_factory=session_factory, senders=[meta, tiktok]
    ) == {"events": 3}
    counts = {
        (c.platform, c.event_name): c.sent for c in session.scalars(select(ConversionEventCount))
    }
    assert counts == {
        ("hub", "PageView"): 2,
        ("hub", "AddToCart"): 1,
        ("meta", "PageView"): 2,
        ("meta", "AddToCart"): 1,
        ("tiktok", "AddToCart"): 1,
    }
    assert redis.llen(signals.QUEUE_KEY) == 0


def test_report_flags_gaps(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    _enable(session_factory)
    for oid in (5001, 5002):
        _order(session_factory, oid=oid)
    r = service.report(session, days=7, today=datetime(2026, 10, 2).date())
    assert r["orders"] == 2
    assert any("web pixel" in p for p in r["problems"])


# --- /collect endpoint ----------------------------------------------------------------------


@pytest.fixture
def collect(
    db_url: str, engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[TestClient, Any]]:
    import app.db as db
    import app.queue as q

    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()
    service._enabled_cache = (0.0, False)
    redis = fakeredis.FakeRedis()
    monkeypatch.setattr(q, "get_redis", lambda: redis)
    from app.main import app

    with TestClient(app) as c:
        yield c, redis
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()
    service._enabled_cache = (0.0, False)


def post(client: TestClient, payload: Any, ip: str = "5.5.5.5") -> httpx.Response:
    raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    return client.post(
        "/collect/pixel",
        content=raw,
        headers={"Content-Type": "text/plain", "Cf-Connecting-Ip": ip},
    )


def _enable_app() -> None:
    from app.db import session_scope

    with session_scope() as s:
        business_settings.set_value(s, "conversions_enabled", True, actor="test")
    service._enabled_cache = (0.0, False)


def test_collect_noop_when_disabled(collect) -> None:  # type: ignore[no-untyped-def]
    client, redis = collect
    r = post(client, {"name": "PageView", "id": "1"})
    assert r.status_code == 204 and r.headers["access-control-allow-origin"] == "*"
    assert redis.llen(signals.QUEUE_KEY) == 0


def test_collect_queues_events_and_stores_purchase_signals(collect) -> None:  # type: ignore[no-untyped-def]
    client, redis = collect
    _enable_app()
    assert (
        post(client, {"name": "AddToCart", "id": "a1", "ua": "UA", "email": "x@y.z"}).status_code
        == 204
    )
    queued = json.loads(redis.lindex(signals.QUEUE_KEY, 0))
    assert queued["ip"] == "5.5.5.5" and "email" not in queued["payload"]  # unknown fields dropped
    post(
        client,
        {
            "name": "Purchase",
            "id": "p1",
            "orderId": "gid://shopify/OrderIdentity/5001",
            "fbp": "fb.1.2.3",
            "ua": "UA",
        },
    )
    assert signals.load_order_signals(redis, 5001) == {
        "fbp": "fb.1.2.3",
        "fbc": None,
        "ttp": None,
        "url": None,
        "ua": "UA",
        "ip": "5.5.5.5",
    }
    assert redis.llen(signals.QUEUE_KEY) == 1  # purchases are not forwarded from the browser


def test_collect_rejects_bad_input_and_rate_limits(
    collect, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    import app.collect as col

    client, _ = collect
    _enable_app()
    assert post(client, {"name": "Hack", "id": "1"}).status_code == 400
    assert post(client, b"not json").status_code == 400
    assert post(client, {"name": "PageView", "id": "1", "url": {"nested": True}}).status_code == 400
    assert post(client, b"x" * (17 * 1024)).status_code == 413
    monkeypatch.setattr(col, "RATE_LIMIT_PER_MIN", 2)
    codes = [
        post(client, {"name": "PageView", "id": str(i)}, ip="7.7.7.7").status_code for i in range(3)
    ]
    assert codes == [204, 204, 429]


# --- web pixel activation -------------------------------------------------------------------


class FakeShopify:
    def __init__(self, existing: dict[str, Any] | None) -> None:
        self.existing, self.calls = existing, []

    def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append((query, variables))
        if "webPixelCreate" in query:
            return {
                "webPixelCreate": {
                    "webPixel": {
                        "id": "gid://shopify/WebPixel/1",
                        "settings": variables["settings"],
                    },
                    "userErrors": [],
                }
            }
        if "webPixelUpdate" in query:
            return {
                "webPixelUpdate": {
                    "webPixel": {"id": variables["id"], "settings": variables["settings"]},
                    "userErrors": [],
                }
            }
        if self.existing is None:
            raise IntegrationError("No web pixel was found for this app.")
        return {"webPixel": self.existing}

    @staticmethod
    def check_user_errors(payload: dict[str, Any], what: str) -> None:
        assert not payload.get("userErrors")


def test_activate_web_pixel_creates_then_updates() -> None:
    s = Settings(public_base_url="https://hub.example.com")
    fresh = FakeShopify(None)
    px = service.activate_web_pixel(fresh, s)
    assert json.loads(px["settings"]) == {"collectUrl": "https://hub.example.com/collect/pixel"}
    assert "webPixelCreate" in fresh.calls[-1][0]
    again = FakeShopify({"id": "gid://shopify/WebPixel/1", "settings": "{}"})
    service.activate_web_pixel(again, s)
    assert "webPixelUpdate" in again.calls[-1][0]
    with pytest.raises(ValueError, match="https"):
        service.activate_web_pixel(
            FakeShopify(None), Settings(public_base_url="http://localhost:8081")
        )
