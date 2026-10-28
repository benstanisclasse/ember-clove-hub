"""Shopify auth + GraphQL client against a mocked HTTP transport."""

from __future__ import annotations

import json
from collections.abc import Callable

import fakeredis
import httpx
import pytest
from pydantic import SecretStr
from shopify_fixtures import page

from app.config import Settings
from app.integrations.http import IntegrationError, NotConfiguredError
from app.integrations.shopify.auth import TokenProvider
from app.integrations.shopify.client import ShopifyClient, ShopifyGraphQLError

SHOP = "demo.myshopify.com"
GQL = f"https://{SHOP}/admin/api/2026-07/graphql.json"
TOKEN_URL = f"https://{SHOP}/admin/oauth/access_token"


def settings(**kw: object) -> Settings:
    base = {
        "shopify_store_domain": SHOP,
        "shopify_client_id": "cid",
        "shopify_client_secret": SecretStr("csecret"),
    }
    return Settings(**{**base, **kw})  # type: ignore[arg-type]


class Recorder:
    """httpx MockTransport that replays scripted responses and records requests."""

    def __init__(self, handler: Callable[[httpx.Request, int], httpx.Response]) -> None:
        self.handler = handler
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.handler(request, len(self.requests))

    def client(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self))


def token_response(token: str = "tok-1") -> httpx.Response:
    return httpx.Response(
        200, json={"access_token": token, "scope": "read_orders", "expires_in": 86399}
    )


def shop_response() -> httpx.Response:
    return httpx.Response(200, json={"data": {"shop": {"name": "Demo"}}, "extensions": {}})


def make(
    handler: Callable[[httpx.Request, int], httpx.Response], **kw: object
) -> tuple[ShopifyClient, Recorder, list[float]]:
    rec = Recorder(handler)
    slept: list[float] = []
    redis = kw.pop("redis", None)
    return (
        ShopifyClient(settings(**kw), http=rec.client(), redis=redis, sleep=slept.append),
        rec,
        slept,
    )


def test_not_configured_raises() -> None:
    with pytest.raises(NotConfiguredError):
        ShopifyClient(Settings(shopify_store_domain=""))
    # the .env.example placeholder counts as not configured
    assert Settings(shopify_store_domain="[store-name].myshopify.com").shopify_configured is False


def test_client_credentials_token_fetched_once_and_sent() -> None:
    def handler(req: httpx.Request, n: int) -> httpx.Response:
        if str(req.url) == TOKEN_URL:
            body = dict(x.split("=") for x in req.content.decode().split("&"))
            assert body == {
                "grant_type": "client_credentials",
                "client_id": "cid",
                "client_secret": "csecret",
            }
            return token_response()
        assert req.headers["X-Shopify-Access-Token"] == "tok-1"
        return shop_response()

    client, rec, _ = make(handler)
    assert client.execute("{ shop { name } }")["shop"]["name"] == "Demo"
    client.execute("{ shop { name } }")
    assert [str(r.url) for r in rec.requests].count(TOKEN_URL) == 1


def test_token_shared_through_redis() -> None:
    redis = fakeredis.FakeRedis()
    first, _rec1, _ = make(
        lambda req, n: token_response("tok-r") if "oauth" in str(req.url) else shop_response(),
        redis=redis,
    )
    first.execute("{ shop { name } }")
    second, rec2, _ = make(lambda req, n: shop_response(), redis=redis)
    second.execute("{ shop { name } }")
    assert all("oauth" not in str(r.url) for r in rec2.requests)
    assert rec2.requests[0].headers["X-Shopify-Access-Token"] == "tok-r"


def test_401_refreshes_token_once() -> None:
    tokens = iter(["old", "new"])

    def handler(req: httpx.Request, n: int) -> httpx.Response:
        if "oauth" in str(req.url):
            return token_response(next(tokens))
        if req.headers["X-Shopify-Access-Token"] == "old":
            return httpx.Response(401, json={"errors": "Invalid API key or access token"})
        return shop_response()

    client, _, _ = make(handler)
    assert client.execute("{ shop { name } }")["shop"]["name"] == "Demo"


def test_static_legacy_token_skips_oauth() -> None:
    client, rec, _ = make(
        lambda req, n: shop_response(), shopify_admin_access_token=SecretStr("shpat_legacy")
    )
    client.execute("{ shop { name } }")
    assert (
        len(rec.requests) == 1
        and rec.requests[0].headers["X-Shopify-Access-Token"] == "shpat_legacy"
    )


def test_throttled_error_waits_then_retries() -> None:
    throttled = {
        "errors": [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}],
        "extensions": {
            "cost": {
                "requestedQueryCost": 500,
                "throttleStatus": {"currentlyAvailable": 100, "restoreRate": 100},
            }
        },
    }

    def handler(req: httpx.Request, n: int) -> httpx.Response:
        if "oauth" in str(req.url):
            return token_response()
        return httpx.Response(200, json=throttled) if n == 2 else shop_response()

    client, _, slept = make(handler)
    client.execute("{ shop { name } }")
    assert slept == [4.0]  # (500 - 100) / 100


def test_low_bucket_sleeps_proactively() -> None:
    low = {
        "data": {"ok": True},
        "extensions": {
            "cost": {
                "requestedQueryCost": 300,
                "throttleStatus": {"currentlyAvailable": 200, "restoreRate": 100},
            }
        },
    }
    client, _, slept = make(
        lambda req, n: (
            token_response() if "oauth" in str(req.url) else httpx.Response(200, json=low)
        )
    )
    client.execute("{ x }")
    assert slept == [4.0]  # keep 2x300 available: (600 - 200) / 100


def test_429_and_5xx_back_off_and_retry() -> None:
    def handler(req: httpx.Request, n: int) -> httpx.Response:
        if "oauth" in str(req.url):
            return token_response()
        if n == 2:
            return httpx.Response(429, headers={"Retry-After": "2"})
        if n == 3:
            return httpx.Response(503)
        return shop_response()

    client, _, slept = make(handler)
    client.execute("{ shop { name } }")
    assert slept[0] == 2.0 and len(slept) == 2


def test_graphql_errors_raise_with_message() -> None:
    bad = {"errors": [{"message": "Field 'nope' doesn't exist on type 'Shop'"}]}
    client, _, _ = make(
        lambda req, n: (
            token_response() if "oauth" in str(req.url) else httpx.Response(200, json=bad)
        )
    )
    with pytest.raises(ShopifyGraphQLError, match="doesn't exist"):
        client.execute("{ shop { nope } }")


def test_403_is_not_retried_and_secret_not_leaked() -> None:
    def handler(req: httpx.Request, n: int) -> httpx.Response:
        if "oauth" in str(req.url):
            return token_response()
        return httpx.Response(403, text="missing scope read_all_orders token=tok-1")

    client, rec, _ = make(handler)
    with pytest.raises(IntegrationError) as exc:
        client.execute("{ orders { nodes { id } } }")
    assert exc.value.status == 403 and "tok-1" not in str(exc.value)
    assert len(rec.requests) == 2


def test_paginate_follows_cursors() -> None:
    pages = {None: page("orders", [{"id": 1}, {"id": 2}], "c1"), "c1": page("orders", [{"id": 3}])}

    def handler(req: httpx.Request, n: int) -> httpx.Response:
        if "oauth" in str(req.url):
            return token_response()
        after = json.loads(req.content)["variables"]["after"]
        return httpx.Response(200, json=pages[after])

    client, _, _ = make(handler)
    assert [n["id"] for n in client.paginate("q", {}, "orders")] == [1, 2, 3]


def test_user_errors_raise() -> None:
    with pytest.raises(ShopifyGraphQLError, match="Address is invalid"):
        ShopifyClient.check_user_errors(
            {"userErrors": [{"field": ["uri"], "message": "Address is invalid"}]}, "x"
        )


def test_token_provider_requires_credentials() -> None:
    tp = TokenProvider(Settings(shopify_store_domain=SHOP), httpx.Client())
    with pytest.raises(NotConfiguredError):
        tp.get()
