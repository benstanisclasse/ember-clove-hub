"""HTTP helpers shared by every platform client: retries with backoff, safe errors."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import Any

import httpx

from app.log import get_logger, scrub

log = get_logger(__name__)

RETRYABLE_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


class IntegrationError(Exception):
    """A platform call failed. Messages are scrubbed of tokens before being stored."""

    def __init__(self, message: str, status: int | None = None, retryable: bool = False) -> None:
        super().__init__(scrub(message))
        self.status = status
        self.retryable = retryable


class NotConfiguredError(IntegrationError):
    """Credentials for this platform haven't been provided yet."""


def backoff_delay(
    attempt: int, base: float = 1.0, cap: float = 60.0, retry_after: str | None = None
) -> float:
    """Exponential backoff with full jitter; honours a numeric ``Retry-After`` header."""
    if retry_after:
        try:
            return min(float(retry_after), cap)
        except ValueError:
            pass
    return random.uniform(0, min(cap, base * 2**attempt))  # noqa: S311 - jitter, not crypto


def request_with_retries(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    max_attempts: int = 6,
    sleep: Callable[[float], None] = time.sleep,
    on_unauthorized: Callable[[], dict[str, str]] | None = None,
    **kwargs: Any,
) -> httpx.Response:
    """Send a request, retrying on network errors and retryable statuses.

    ``on_unauthorized``: called once on a 401 to refresh credentials; it returns new
    headers to merge, and the request is retried immediately.
    """
    refreshed = False
    for attempt in range(max_attempts):
        try:
            resp = client.request(method, url, **kwargs)
        except (httpx.TransportError, httpx.TimeoutException) as exc:
            if attempt == max_attempts - 1:
                raise IntegrationError(f"{method} {url}: {exc}", retryable=True) from exc
            delay = backoff_delay(attempt)
            log.warning("http_retry", url=url, error=type(exc).__name__, delay_s=round(delay, 2))
            sleep(delay)
            continue

        if resp.status_code == 401 and on_unauthorized and not refreshed:
            refreshed = True
            kwargs["headers"] = {**kwargs.get("headers", {}), **on_unauthorized()}
            continue
        if resp.status_code in RETRYABLE_STATUS and attempt < max_attempts - 1:
            delay = backoff_delay(attempt, retry_after=resp.headers.get("Retry-After"))
            log.warning("http_retry", url=url, status=resp.status_code, delay_s=round(delay, 2))
            sleep(delay)
            continue
        if resp.status_code >= 400:
            raise IntegrationError(
                f"{method} {url} -> HTTP {resp.status_code}: {resp.text[:500]}",
                status=resp.status_code,
                retryable=resp.status_code in RETRYABLE_STATUS,
            )
        return resp
    raise IntegrationError(f"{method} {url}: retries exhausted", retryable=True)  # pragma: no cover
