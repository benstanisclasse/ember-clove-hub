"""Send conversion events to Meta (Conversions API), TikTok (Events API) and Google Ads
(click conversion upload). Each sender takes a batch of platform-neutral ``Event``s."""

from __future__ import annotations

import abc
import hashlib
import hmac
import json
import time
from collections.abc import Callable
from datetime import UTC
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.conversions.events import PURCHASE, Event
from app.integrations.http import IntegrationError, request_with_retries
from app.log import get_logger

log = get_logger(__name__)


def _clean(d: dict[str, Any]) -> dict[str, Any]:
    """Drop None / empty values (platforms reject nulls in some fields)."""
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}


class Sender(abc.ABC):
    platform: str
    batch_size = 500

    @abc.abstractmethod
    def supports(self, event: Event) -> bool: ...

    @abc.abstractmethod
    def send(self, events: list[Event]) -> int:
        """Send ``events``; returns how many the platform accepted. Raises IntegrationError."""


class MetaCapi(Sender):
    """Meta Conversions API: POST /{pixel_id}/events (up to 1,000 events per call)."""

    platform = "meta"

    def __init__(
        self,
        settings: Settings | None = None,
        http: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.s = settings or get_settings()
        self.http = http or httpx.Client(timeout=30)
        self.sleep = sleep

    @staticmethod
    def configured(s: Settings) -> bool:
        return bool(s.meta_system_user_token.get_secret_value() and s.meta_pixel_id)

    def supports(self, event: Event) -> bool:
        return True

    def payload(self, e: Event) -> dict[str, Any]:
        # Meta requires client_user_agent for action_source=website; server-only purchases
        # without browser signals are sent as system_generated instead.
        source = "website" if e.user_agent else "system_generated"
        custom = _clean(
            {
                "currency": e.currency,
                "value": float(e.value) if e.value is not None else None,
                "order_id": e.order_id,
                "content_type": "product" if e.items else None,
                "content_ids": [i.id for i in e.items],
                "contents": [
                    {"id": i.id, "quantity": i.quantity, "item_price": float(i.price)}
                    for i in e.items
                ],
                "num_items": sum(i.quantity for i in e.items) or None,
            }
        )
        return _clean(
            {
                "event_name": e.name,
                "event_time": e.unix_time,
                "event_id": e.event_id,
                "action_source": source,
                "event_source_url": e.url,
                "user_data": _clean(
                    {
                        "em": [e.email_hash] if e.email_hash else None,
                        "ph": [e.phone_hash] if e.phone_hash else None,
                        "external_id": [e.external_id_hash] if e.external_id_hash else None,
                        "client_ip_address": e.ip,
                        "client_user_agent": e.user_agent,
                        "fbc": e.fbc,
                        "fbp": e.fbp,
                    }
                ),
                "custom_data": custom,
            }
        )

    def send(self, events: list[Event]) -> int:
        token = self.s.meta_system_user_token.get_secret_value()
        data: dict[str, Any] = {
            "data": json.dumps([self.payload(e) for e in events]),
            "access_token": token,
        }
        secret = self.s.meta_app_secret.get_secret_value()
        if secret:
            data["appsecret_proof"] = hmac.new(
                secret.encode(), token.encode(), hashlib.sha256
            ).hexdigest()
        if self.s.meta_capi_test_event_code:
            data["test_event_code"] = self.s.meta_capi_test_event_code
        url = f"https://graph.facebook.com/{self.s.meta_api_version}/{self.s.meta_pixel_id}/events"
        resp = request_with_retries(self.http, "POST", url, data=data, sleep=self.sleep)
        return int(resp.json().get("events_received", 0))


TIKTOK_NAMES = {
    "ViewContent": "ViewContent",
    "AddToCart": "AddToCart",
    "InitiateCheckout": "InitiateCheckout",
    PURCHASE: "CompletePayment",  # matches the ad groups' COMPLETE_PAYMENT optimization event
}


class TikTokEvents(Sender):
    """TikTok Events API: POST /event/track/ with ``event_source=web`` and the pixel code."""

    platform = "tiktok"

    def __init__(
        self,
        settings: Settings | None = None,
        http: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.s = settings or get_settings()
        self.http = http or httpx.Client(timeout=30)
        self.sleep = sleep

    @staticmethod
    def token(s: Settings) -> str:
        return (
            s.tiktok_events_access_token.get_secret_value()
            or s.tiktok_access_token.get_secret_value()
        )

    @classmethod
    def configured(cls, s: Settings) -> bool:
        return bool(cls.token(s) and s.tiktok_pixel_code)

    def supports(self, event: Event) -> bool:
        return event.name in TIKTOK_NAMES  # TikTok's own pixel covers page views

    def payload(self, e: Event) -> dict[str, Any]:
        return _clean(
            {
                "event": TIKTOK_NAMES[e.name],
                "event_time": e.unix_time,
                "event_id": e.event_id,
                "user": _clean(
                    {
                        "email": e.email_hash,
                        "phone": e.phone_hash,
                        "external_id": e.external_id_hash,
                        "ttclid": e.ttclid,
                        "ttp": e.ttp,
                        "ip": e.ip,
                        "user_agent": e.user_agent,
                    }
                ),
                "properties": _clean(
                    {
                        "currency": e.currency,
                        "value": float(e.value) if e.value is not None else None,
                        "order_id": e.order_id,
                        "content_type": "product" if e.items else None,
                        "contents": [
                            {"content_id": i.id, "quantity": i.quantity, "price": float(i.price)}
                            for i in e.items
                        ],
                    }
                ),
                "page": _clean({"url": e.url, "referrer": e.referrer}),
            }
        )

    def send(self, events: list[Event]) -> int:
        body = _clean(
            {
                "event_source": "web",
                "event_source_id": self.s.tiktok_pixel_code,
                "test_event_code": self.s.tiktok_test_event_code or None,
                "data": [self.payload(e) for e in events],
            }
        )
        url = f"https://business-api.tiktok.com/open_api/{self.s.tiktok_api_version}/event/track/"
        resp = request_with_retries(
            self.http,
            "POST",
            url,
            json=body,
            headers={"Access-Token": self.token(self.s)},
            sleep=self.sleep,
        )
        out = resp.json()
        if out.get("code") != 0:
            raise IntegrationError(
                f"TikTok Events API code={out.get('code')}: {out.get('message')}",
                retryable=out.get("code") in (40100, 50000, 50002),
            )
        return len(events)


class GoogleClickConversions(Sender):
    """Google Ads offline click conversions (orders that carry a gclid / gbraid / wbraid)."""

    platform = "google"
    batch_size = 200

    def __init__(self, settings: Settings | None = None, client: Any | None = None) -> None:
        self.s = settings or get_settings()
        self._client = client

    @staticmethod
    def configured(s: Settings) -> bool:
        return bool(s.google_ads_configured and s.google_ads_conversion_action)

    @property
    def client(self) -> Any:
        if self._client is None:
            from app.integrations.ads.registry import get_platform

            self._client = get_platform("google")
        return self._client

    def supports(self, event: Event) -> bool:
        return event.name == PURCHASE and bool(event.gclid or event.gbraid or event.wbraid)

    def payload(self, e: Event) -> dict[str, Any]:
        click = (
            {"gclid": e.gclid}
            if e.gclid
            else {"gbraid": e.gbraid}
            if e.gbraid
            else {"wbraid": e.wbraid}
        )
        return _clean(
            {
                **click,
                "conversionAction": self.s.google_ads_conversion_action,
                "conversionDateTime": e.time.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S+00:00"),
                "conversionValue": float(e.value) if e.value is not None else None,
                "currencyCode": e.currency,
                "orderId": e.order_id,
            }
        )

    def send(self, events: list[Event]) -> int:
        result = self.client.upload_click_conversions([self.payload(e) for e in events])
        failure = result.get("partialFailureError")
        if failure:
            raise IntegrationError(f"Google click conversion upload: {failure.get('message')}")
        return len(result.get("results") or [])


def configured_senders(settings: Settings | None = None) -> list[Sender]:
    s = settings or get_settings()
    out: list[Sender] = []
    if MetaCapi.configured(s):
        out.append(MetaCapi(s))
    if TikTokEvents.configured(s):
        out.append(TikTokEvents(s))
    if GoogleClickConversions.configured(s):
        out.append(GoogleClickConversions(s))
    return out
