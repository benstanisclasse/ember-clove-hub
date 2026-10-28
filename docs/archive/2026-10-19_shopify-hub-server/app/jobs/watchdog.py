"""Every 5 minutes: check everything, alert Slack on failures, ping the heartbeat.

Two layers of monitoring:

* **Inside the VM** -- this watchdog alerts on a broken dependency, a missing worker
  or a stale sync job, and posts a recovery message when it clears.
* **Outside the VM** -- the heartbeat URL (e.g. healthchecks.io) is pinged only when
  every check passes. If the VM, Docker or the scheduler dies, pings stop and the
  external service alerts you. Nothing inside a dead VM can do that.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.alerts import Alerter
from app.config import get_settings
from app.health import CheckResult, full_status
from app.jobs.tracking import track_job
from app.log import get_logger, scrub

log = get_logger(__name__)


def evaluate(results: list[CheckResult], alerter: Alerter) -> bool:
    """Fire/resolve one alert per check. Returns True when all checks pass."""
    for r in results:
        key = f"health:{r.name}"
        if r.ok:
            alerter.resolve(key, f"{r.name} is healthy again")
        else:
            alerter.fire(key, f"{r.name} check failing: {r.detail}")
    return all(r.ok for r in results)


def ping_heartbeat(url: str, healthy: bool) -> None:
    if not url:
        return
    try:
        # healthchecks.io convention: /fail marks the check down immediately.
        httpx.get(url if healthy else url.rstrip("/") + "/fail", timeout=10)
    except httpx.HTTPError as exc:
        log.warning("heartbeat_failed", error=scrub(str(exc)))


def run_watchdog(redis: Any | None = None) -> bool:
    from app.queue import get_redis

    settings = get_settings()
    redis = redis or get_redis()
    with track_job("watchdog") as stats:
        results = full_status(redis)
        healthy = evaluate(results, Alerter(redis, settings))
        stats["failing"] = [r.name for r in results if not r.ok]
        ping_heartbeat(settings.heartbeat_url.get_secret_value(), healthy)
    return healthy
