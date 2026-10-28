"""Shopify access tokens.

Since 2026-01-01 store-owned apps are created in the Shopify **Dev Dashboard** and get
short-lived (about 24 h) Admin API tokens through the OAuth *client credentials grant*:

    POST https://{shop}/admin/oauth/access_token
    grant_type=client_credentials&client_id=...&client_secret=...
    -> {"access_token": "...", "scope": "...", "expires_in": 86399}

The token is cached in Redis (shared by api / worker / scheduler) until 5 minutes before
expiry, and dropped on a 401 so the next call fetches a fresh one. A legacy non-expiring
token (``SHOPIFY_ADMIN_ACCESS_TOKEN``) is used as-is when set.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

from app.config import Settings
from app.integrations.http import NotConfiguredError, request_with_retries
from app.log import get_logger

log = get_logger(__name__)
_CACHE_KEY = "hub:shopify:access_token"
_REFRESH_MARGIN_S = 300


class TokenProvider:
    """Hands out a valid Admin API token, fetching / refreshing as needed."""

    def __init__(
        self,
        settings: Settings,
        http: httpx.Client,
        redis: Any | None = None,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.settings = settings
        self.http = http
        self.redis = redis
        self.clock = clock
        self.sleep = sleep
        self._token: str | None = None
        self._expires_at = 0.0

    def get(self) -> str:
        static = self.settings.shopify_admin_access_token.get_secret_value()
        if static:
            return static
        if self._token and self.clock() < self._expires_at:
            return self._token
        cached = self._cache_get()
        if cached:
            self._token, self._expires_at = cached, self.clock() + 60  # re-check redis soon
            return cached
        return self._fetch()

    def invalidate(self) -> None:
        self._token, self._expires_at = None, 0.0
        if self.redis is not None:
            try:
                self.redis.delete(_CACHE_KEY)
            except Exception:  # noqa: S110 - cache is best-effort
                pass

    def _fetch(self) -> str:
        s = self.settings
        if not (
            s.shopify_store_domain
            and s.shopify_client_id
            and s.shopify_client_secret.get_secret_value()
        ):
            raise NotConfiguredError(
                "Shopify not configured: set SHOPIFY_STORE_DOMAIN, SHOPIFY_CLIENT_ID and "
                "SHOPIFY_CLIENT_SECRET (Dev Dashboard app) in .env"
            )
        resp = request_with_retries(
            self.http,
            "POST",
            f"https://{s.shopify_store_domain}/admin/oauth/access_token",
            data={
                "grant_type": "client_credentials",
                "client_id": s.shopify_client_id,
                "client_secret": s.shopify_client_secret.get_secret_value(),
            },
            headers={"Accept": "application/json"},
            sleep=self.sleep,
            max_attempts=4,
        )
        body = resp.json()
        token = body["access_token"]
        ttl = max(int(body.get("expires_in", 86399)) - _REFRESH_MARGIN_S, 60)
        self._token, self._expires_at = token, self.clock() + ttl
        if self.redis is not None:
            try:
                self.redis.set(_CACHE_KEY, token, ex=ttl)
            except Exception:  # noqa: S110
                pass
        log.info("shopify_token_refreshed", expires_in_s=ttl, scope=body.get("scope"))
        return token  # type: ignore[no-any-return]

    def _cache_get(self) -> str | None:
        if self.redis is None:
            return None
        try:
            value = self.redis.get(_CACHE_KEY)
        except Exception:
            return None
        return value.decode() if isinstance(value, bytes) else value
