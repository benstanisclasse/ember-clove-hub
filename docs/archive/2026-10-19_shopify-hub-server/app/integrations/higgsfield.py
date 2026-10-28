"""Higgsfield API client (https://docs.higgsfield.ai).

* Auth: ``Authorization: Key <key_id>:<secret>`` (server-side only).
* Every model has its own endpoint: ``POST /{model_id}`` -> ``{request_id, status, status_url,
  cancel_url}``. Body fields depend on the model (see its page in the console); the hub
  passes them through and validates them first with the free estimate call.
* ``POST /estimate/{model_id}`` (same body) -> ``{credits, usd}``: used for the budget cap.
* ``GET /requests/{id}/status`` -> ``queued | in_progress | completed | failed | nsfw | canceled``
  with ``images[].url`` / ``video.url``. Failed, nsfw and canceled requests aren't charged.
* Outputs are kept ~7 days, so completed files are copied into our object storage at once.
* Webhooks (``?hf_webhook=<url>``) are unsigned; the hub only uses them as a "check now"
  nudge and always confirms through the authenticated status call.
* Concurrency limits answer HTTP 400 (not 429) without Retry-After; treated as retryable.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from urllib.parse import quote

import httpx

from app.config import Settings, get_settings
from app.integrations.http import IntegrationError, NotConfiguredError, backoff_delay
from app.log import get_logger

log = get_logger(__name__)
TERMINAL = {"completed", "failed", "nsfw", "canceled"}
UNAVAILABLE = {
    404: "not available to this account",
    423: "temporarily blocked",
    503: "disabled or not ready",
}


@dataclass
class Submission:
    request_id: str
    status: str
    status_url: str | None = None
    cancel_url: str | None = None


@dataclass
class JobStatus:
    request_id: str
    status: str
    error: str | None = None
    image_urls: list[str] = field(default_factory=list)
    video_url: str | None = None

    @property
    def done(self) -> bool:
        return self.status in TERMINAL

    @property
    def output_url(self) -> str | None:
        return self.video_url or (self.image_urls[0] if self.image_urls else None)


@dataclass
class Estimate:
    credits: Decimal
    usd: Decimal


class HiggsfieldClient:
    def __init__(
        self,
        settings: Settings | None = None,
        http: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
        max_attempts: int = 5,
    ) -> None:
        self.s = settings or get_settings()
        if not self.s.higgsfield_configured:
            raise NotConfiguredError(
                "Higgsfield not configured: set HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET"
            )
        self.http = http or httpx.Client(timeout=httpx.Timeout(60.0, connect=10.0))
        self.sleep = sleep
        self.max_attempts = max_attempts
        self.base = self.s.higgsfield_base_url.rstrip("/")

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        key = self.s.higgsfield_api_key.get_secret_value()
        secret = self.s.higgsfield_api_secret.get_secret_value()
        h = {"Authorization": f"Key {key}:{secret}", "Content-Type": "application/json"}
        if idempotency_key:
            h["Idempotency-Key"] = idempotency_key
        return h

    def _request(
        self,
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        for attempt in range(self.max_attempts):
            try:
                resp = self.http.request(
                    method,
                    url,
                    json=json,
                    params=params or None,
                    headers=self._headers(idempotency_key),
                )
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                if attempt == self.max_attempts - 1:
                    raise IntegrationError(
                        f"Higgsfield {method} {url}: {exc}", retryable=True
                    ) from exc
                self.sleep(backoff_delay(attempt))
                continue
            if resp.status_code < 400:
                return resp.json() if resp.content else {}
            text = resp.text[:500]
            if resp.status_code == 401:
                raise IntegrationError("Higgsfield rejected the API key (401)", status=401)
            if resp.status_code in UNAVAILABLE:
                raise IntegrationError(
                    f"Higgsfield model {UNAVAILABLE[resp.status_code]}: {text}",
                    status=resp.status_code,
                    retryable=resp.status_code != 404,
                )
            concurrency = resp.status_code == 400 and any(
                w in text.lower() for w in ("concurren", "too many", "limit")
            )
            if (
                resp.status_code >= 500 or resp.status_code == 429 or concurrency
            ) and attempt < self.max_attempts - 1:
                self.sleep(backoff_delay(attempt, base=5.0, cap=120.0))
                continue
            raise IntegrationError(
                f"Higgsfield {method} {url.split('?')[0]} -> {resp.status_code}: {text}",
                status=resp.status_code,
                retryable=concurrency or resp.status_code >= 500,
            )
        raise IntegrationError("Higgsfield: retries exhausted", retryable=True)  # pragma: no cover

    # --- API --------------------------------------------------------------------------------

    def estimate(self, model_id: str, params: dict[str, Any]) -> Estimate:
        body = self._request("POST", f"{self.base}/estimate/{model_id.strip('/')}", json=params)
        return Estimate(
            credits=Decimal(str(body.get("credits", "0"))), usd=Decimal(str(body.get("usd", "0")))
        )

    def submit(
        self,
        model_id: str,
        params: dict[str, Any],
        idempotency_key: str | None = None,
        webhook_url: str | None = None,
    ) -> Submission:
        """Queue a generation. Re-sending with the same ``idempotency_key`` never double-charges."""
        url = f"{self.base}/{model_id.strip('/')}"
        query = {"hf_webhook": webhook_url} if webhook_url else None
        body = self._request(
            "POST",
            url,
            json=params,
            idempotency_key=idempotency_key or str(uuid.uuid4()),
            params=query,
        )
        return Submission(
            str(body["request_id"]),
            str(body.get("status", "queued")),
            body.get("status_url"),
            body.get("cancel_url"),
        )

    def status(self, request_id: str) -> JobStatus:
        body = self._request("GET", f"{self.base}/requests/{quote(request_id)}/status")
        return JobStatus(
            request_id=str(body.get("request_id", request_id)),
            status=str(body.get("status", "")),
            error=body.get("error"),
            image_urls=[i["url"] for i in body.get("images") or [] if i.get("url")],
            video_url=(body.get("video") or {}).get("url"),
        )

    def cancel(self, request_id: str) -> None:
        """Cancel a queued request (refunded). Running requests may not be cancellable."""
        self._request("POST", f"{self.base}/requests/{quote(request_id)}/cancel")

    def download(self, url: str, max_bytes: int = 500 * 1024 * 1024) -> tuple[bytes, str]:
        """Fetch an output file (pre-signed CDN URL: no auth header). Returns (bytes, mime)."""
        with self.http.stream("GET", url, timeout=httpx.Timeout(300.0, connect=10.0)) as resp:
            if resp.status_code >= 400:
                raise IntegrationError(
                    f"Higgsfield output download -> HTTP {resp.status_code}", retryable=True
                )
            chunks, size = [], 0
            for chunk in resp.iter_bytes():
                size += len(chunk)
                if size > max_bytes:
                    raise IntegrationError("Higgsfield output larger than the 500 MB safety limit")
                chunks.append(chunk)
            return b"".join(chunks), resp.headers.get(
                "content-type", "application/octet-stream"
            ).split(";")[0]

    def models(self) -> list[dict[str, Any]]:
        """Configured models with availability (probed with the free estimate call).

        Higgsfield has no public catalog endpoint; models are discovered in the console.
        """
        ids = [
            self.s.higgsfield_image_model,
            self.s.higgsfield_video_model,
            *[m.strip() for m in self.s.higgsfield_extra_models.split(",")],
        ]
        out = []
        for model_id in dict.fromkeys(m for m in ids if m):
            try:
                est = self.estimate(model_id, {"prompt": "availability check"})
                out.append({"model": model_id, "available": True, "example_usd": str(est.usd)})
            except IntegrationError as exc:
                ok = exc.status == 400  # reachable; just needs model-specific fields
                out.append({"model": model_id, "available": ok, "detail": str(exc)[:200]})
        return out
