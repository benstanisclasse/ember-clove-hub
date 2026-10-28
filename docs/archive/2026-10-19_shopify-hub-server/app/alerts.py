"""Slack alerts with de-duplication.

Alerts are keyed (e.g. ``health:database``); the same key fires at most once per
``ALERT_COOLDOWN_MINUTES``, and a "resolved" message is sent when a key clears.
State lives in Redis so the API, worker and scheduler share it. If Redis itself is
down, alerts are still sent (without de-duplication) -- better noisy than silent.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings, get_settings
from app.log import get_logger, scrub

log = get_logger(__name__)
_PREFIX = "hub:alert:"


def send_slack(text: str, settings: Settings | None = None) -> bool:
    """Post a message to the Slack incoming webhook. Returns False if not configured/failed."""
    settings = settings or get_settings()
    url = settings.slack_webhook_url.get_secret_value()
    if not url:
        log.warning("slack_not_configured", message=text)
        return False
    try:
        resp = httpx.post(url, json={"text": text}, timeout=10)
        resp.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.error("slack_send_failed", error=scrub(str(exc)))
        return False


class Alerter:
    """Fire / resolve keyed alerts with a cooldown."""

    def __init__(self, redis: Any | None, settings: Settings | None = None) -> None:
        self.redis = redis
        self.settings = settings or get_settings()

    def fire(self, key: str, message: str) -> bool:
        """Send ``message`` unless ``key`` already fired within the cooldown."""
        ttl = self.settings.alert_cooldown_minutes * 60
        try:
            if self.redis is not None and not self.redis.set(_PREFIX + key, "1", nx=True, ex=ttl):
                return False
            if self.redis is not None:
                self.redis.sadd(_PREFIX + "active", key)
        except Exception as exc:  # Redis down: still alert
            log.warning("alert_dedupe_unavailable", error=scrub(str(exc)))
        log.warning("alert_fired", key=key, message=message)
        return send_slack(f":rotating_light: *Shopify hub*: {message}", self.settings)

    def resolve(self, key: str, message: str | None = None) -> bool:
        """Send a recovery message if ``key`` was active."""
        try:
            if self.redis is None or not self.redis.srem(_PREFIX + "active", key):
                return False
            self.redis.delete(_PREFIX + key)
        except Exception:
            return False
        log.info("alert_resolved", key=key)
        return send_slack(
            f":white_check_mark: *Shopify hub*: {message or key + ' recovered'}", self.settings
        )
