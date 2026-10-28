"""Shopify Admin GraphQL client.

Rate limiting: Shopify meters GraphQL by *query cost* (a leaky bucket per app per store).
Every response reports ``extensions.cost.throttleStatus``; when the bucket runs low the
client sleeps just long enough to refill it, and a ``THROTTLED`` error waits and retries.
HTTP 429 / 5xx / network errors back off exponentially (``request_with_retries``), and a
401 refreshes the access token once.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.integrations.http import IntegrationError, NotConfiguredError, request_with_retries
from app.integrations.shopify.auth import TokenProvider
from app.log import get_logger

log = get_logger(__name__)


class ShopifyGraphQLError(IntegrationError):
    """GraphQL-level errors (bad query, missing scope, userErrors)."""


class ShopifyClient:
    def __init__(
        self,
        settings: Settings | None = None,
        http: httpx.Client | None = None,
        tokens: TokenProvider | None = None,
        redis: Any | None = None,
        sleep: Callable[[float], None] = time.sleep,
        max_throttle_retries: int = 8,
    ) -> None:
        self.settings = settings or get_settings()
        if not self.settings.shopify_configured:
            raise NotConfiguredError(
                "Shopify not configured: set SHOPIFY_STORE_DOMAIN plus SHOPIFY_CLIENT_ID / "
                "SHOPIFY_CLIENT_SECRET in .env"
            )
        self.http = http or httpx.Client(timeout=httpx.Timeout(30.0, connect=10.0))
        self.tokens = tokens or TokenProvider(self.settings, self.http, redis=redis, sleep=sleep)
        self.sleep = sleep
        self.max_throttle_retries = max_throttle_retries
        s = self.settings
        self.endpoint = (
            f"https://{s.shopify_store_domain}/admin/api/{s.shopify_api_version}/graphql.json"
        )

    # -- core ------------------------------------------------------------------------------

    def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run one GraphQL document and return ``data``; raise on errors."""
        for _ in range(self.max_throttle_retries + 1):
            resp = request_with_retries(
                self.http,
                "POST",
                self.endpoint,
                json={"query": query, "variables": variables or {}},
                headers=self._headers(),
                sleep=self.sleep,
                on_unauthorized=self._refresh_headers,
            )
            body = resp.json()
            cost = (body.get("extensions") or {}).get("cost") or {}
            errors = body.get("errors") or []
            if any((e.get("extensions") or {}).get("code") == "THROTTLED" for e in errors):
                wait = self._throttle_wait(cost, throttled=True)
                log.info("shopify_throttled", wait_s=round(wait, 2))
                self.sleep(wait)
                continue
            if errors:
                msgs = "; ".join(str(e.get("message")) for e in errors)[:800]
                raise ShopifyGraphQLError(f"Shopify GraphQL error: {msgs}")
            wait = self._throttle_wait(cost, throttled=False)
            if wait > 0:
                self.sleep(wait)
            return body.get("data") or {}
        raise IntegrationError("Shopify: still throttled after retries", retryable=True)

    def paginate(
        self,
        query: str,
        variables: dict[str, Any],
        connection: str,
        page_size: int = 50,
    ) -> Iterator[dict[str, Any]]:
        """Yield every node of top-level ``connection`` across all pages."""
        after: str | None = None
        while True:
            data = self.execute(query, {**variables, "first": page_size, "after": after})
            conn = data.get(connection) or {}
            yield from conn.get("nodes") or []
            info = conn.get("pageInfo") or {}
            if not info.get("hasNextPage"):
                return
            after = info.get("endCursor")

    @staticmethod
    def check_user_errors(payload: dict[str, Any] | None, what: str) -> None:
        errs = (payload or {}).get("userErrors") or []
        if errs:
            raise ShopifyGraphQLError(f"{what}: " + "; ".join(e.get("message", "") for e in errs))

    # -- internals ---------------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {"X-Shopify-Access-Token": self.tokens.get(), "Content-Type": "application/json"}

    def _refresh_headers(self) -> dict[str, str]:
        self.tokens.invalidate()
        return self._headers()

    @staticmethod
    def _throttle_wait(cost: dict[str, Any], throttled: bool) -> float:
        """Seconds to wait so the next query of similar cost won't be throttled."""
        status = cost.get("throttleStatus") or {}
        available = float(status.get("currentlyAvailable", 1000))
        restore = float(status.get("restoreRate", 50)) or 50.0
        needed = float(cost.get("requestedQueryCost") or cost.get("actualQueryCost") or 0)
        if throttled:
            return max(1.0, (needed - available) / restore)
        # Keep a buffer of two queries' worth so parallel workers don't trip the limit.
        deficit = 2 * needed - available
        return deficit / restore if deficit > 0 else 0.0
