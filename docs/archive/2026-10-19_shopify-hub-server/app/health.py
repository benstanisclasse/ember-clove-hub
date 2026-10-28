"""Dependency and job health checks, shared by ``/health/ready`` and the watchdog."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from app.log import scrub


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = "ok"
    latency_ms: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_check(name: str, fn: Callable[[], str | None]) -> CheckResult:
    """Run ``fn``; any exception marks the check failed (with a scrubbed message)."""
    start = time.perf_counter()
    try:
        detail = fn() or "ok"
        ok = True
    except Exception as exc:
        detail, ok = scrub(f"{type(exc).__name__}: {exc}")[:300], False
    return CheckResult(name, ok, detail, round((time.perf_counter() - start) * 1000, 1))


def check_database() -> str | None:
    from app.db import ping

    ping()
    return None


def check_redis(redis: Any) -> Callable[[], str | None]:
    def _check() -> str | None:
        redis.ping()
        return None

    return _check


def check_storage() -> str | None:
    from app.storage import get_store

    get_store().ping()
    return None


def check_workers(redis: Any) -> Callable[[], str | None]:
    def _check() -> str | None:
        from rq import Worker

        n = len(Worker.all(connection=redis))
        if n == 0:
            raise RuntimeError("no RQ workers registered")
        return f"{n} worker(s)"

    return _check


def stale_jobs(session: Any, now: datetime | None = None) -> list[str]:
    """Jobs whose last success is older than their ``stale_after_minutes``.

    A job that has never succeeded is only stale once it has existed (first noticed by this
    check) for longer than that window -- so adding a new daily job doesn't alert at once.
    """
    from app.jobs.registry import JOBS
    from app.jobs.tracking import last_success
    from app.models import SyncState

    now = now or datetime.now(UTC)
    stale = []
    for job in JOBS:
        if job.stale_after_minutes is None:
            continue
        window = timedelta(minutes=job.stale_after_minutes)
        last = last_success(session, job.name)
        if last is None:
            key = f"job_first_seen:{job.name}"
            row = session.get(SyncState, key)
            if row is None:
                session.add(SyncState(key=key, value=now.isoformat()))
                session.flush()
                continue
            first_seen = datetime.fromisoformat(row.value)
            if now - first_seen > window:
                stale.append(
                    f"{job.name} (last ok: never, registered {first_seen:%Y-%m-%d %H:%M} UTC)"
                )
        elif now - last > window:
            stale.append(f"{job.name} (last ok: {last.isoformat()})")
    return stale


def check_shopify() -> str | None:
    """Token + a 1-point query. 'not configured' counts as healthy until keys are added."""
    from app.config import get_settings

    if not get_settings().shopify_configured:
        return "not configured"
    from app.integrations.shopify import queries
    from app.jobs.shopify import get_client

    shop = get_client().execute(queries.SHOP).get("shop") or {}
    return f"{shop.get('myshopifyDomain')} ({shop.get('currencyCode')})"


def check_ad_platforms() -> str | None:
    from app.integrations.ads.registry import configured_platforms

    configured = [p.value for p in configured_platforms()]
    return ("configured: " + ", ".join(configured)) if configured else "none configured"


def check_conversions() -> str | None:
    """Only judged when conversions are on: purchases reported and storefront events flowing."""
    from app import business_settings
    from app.conversions.service import report
    from app.db import session_scope

    with session_scope() as s:
        if not business_settings.load(s).conversions_enabled:
            return "disabled"
        r = report(s, days=2)
    if r["problems"]:
        raise RuntimeError("; ".join(r["problems"]))
    return f"{r['orders']} orders / 2d tracked"


def check_higgsfield() -> str | None:
    from app import business_settings
    from app.config import get_settings
    from app.creatives.pipeline import monthly_spend
    from app.db import session_scope

    if not get_settings().higgsfield_configured:
        return "not configured"
    with session_scope() as s:
        cap = business_settings.load(s).higgsfield_monthly_cap_usd
        spent = monthly_spend(s)
    return f"${spent} this month" + (
        f" of ${cap} cap" if cap is not None else " (no cap set: generation blocked)"
    )


def check_jobs() -> str | None:
    from app.db import session_scope

    with session_scope() as s:
        stale = stale_jobs(s)
    if stale:
        raise RuntimeError("stale: " + ", ".join(stale))
    return None


def readiness(redis: Any) -> list[CheckResult]:
    """Fast checks the API needs to serve traffic."""
    return [
        run_check("database", check_database),
        run_check("redis", check_redis(redis)),
        run_check("storage", check_storage),
    ]


def full_status(redis: Any) -> list[CheckResult]:
    """Everything the watchdog alerts on."""
    return [
        *readiness(redis),
        run_check("workers", check_workers(redis)),
        run_check("jobs", check_jobs),
        run_check("shopify", check_shopify),
        run_check("ads", check_ad_platforms),
        run_check("conversions", check_conversions),
        run_check("higgsfield", check_higgsfield),
    ]
