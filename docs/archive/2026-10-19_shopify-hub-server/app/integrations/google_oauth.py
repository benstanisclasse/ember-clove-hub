"""Google OAuth: exchange a long-lived refresh token for 1-hour access tokens.

Shared by the Google Ads API and the YouTube Data API (each with its own refresh token
and scope). Access tokens are cached in Redis, keyed by a hash of the refresh token.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from typing import Any

import httpx

from app.integrations.http import IntegrationError, NotConfiguredError, request_with_retries
from app.log import get_logger

log = get_logger(__name__)
TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105 - endpoint, not a secret


class GoogleOAuthToken:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        http: httpx.Client,
        redis: Any | None = None,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not (client_id and client_secret and refresh_token):
            raise NotConfiguredError(
                "Google OAuth needs client id, client secret and refresh token"
            )
        self.client_id, self.client_secret, self.refresh_token = (
            client_id,
            client_secret,
            refresh_token,
        )
        self.http, self.redis, self.clock, self.sleep = http, redis, clock, sleep
        self._key = "hub:google:token:" + hashlib.sha256(refresh_token.encode()).hexdigest()[:16]
        self._token: str | None = None
        self._expires_at = 0.0

    def get(self) -> str:
        if self._token and self.clock() < self._expires_at:
            return self._token
        if self.redis is not None:
            try:
                cached = self.redis.get(self._key)
                if cached:
                    self._token = cached.decode() if isinstance(cached, bytes) else cached
                    self._expires_at = self.clock() + 60
                    return self._token
            except Exception:  # noqa: S110 - cache is best-effort
                pass
        return self._refresh()

    def invalidate(self) -> None:
        self._token, self._expires_at = None, 0.0
        if self.redis is not None:
            try:
                self.redis.delete(self._key)
            except Exception:  # noqa: S110
                pass

    def _refresh(self) -> str:
        try:
            resp = request_with_retries(
                self.http,
                "POST",
                TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                },
                sleep=self.sleep,
                max_attempts=4,
            )
        except IntegrationError as exc:
            if exc.status in (400, 401):
                raise IntegrationError(
                    "Google refresh token rejected (revoked, expired, or consent screen still in "
                    "'Testing' mode, which expires tokens after 7 days). Generate a new one.",
                    status=exc.status,
                ) from exc
            raise
        body = resp.json()
        ttl = max(int(body.get("expires_in", 3600)) - 120, 60)
        self._token, self._expires_at = body["access_token"], self.clock() + ttl
        if self.redis is not None:
            try:
                self.redis.set(self._key, self._token, ex=ttl)
            except Exception:  # noqa: S110
                pass
        return self._token  # type: ignore[return-value]

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.get()}"}
