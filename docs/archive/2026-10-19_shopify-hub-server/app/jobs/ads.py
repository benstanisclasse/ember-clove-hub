"""Ad platform sync jobs. Each platform no-ops cleanly until its keys are configured."""

from __future__ import annotations

from app.config import get_settings
from app.db import session_scope
from app.integrations.ads import sync
from app.integrations.ads.registry import get_platform, is_configured
from app.jobs.tracking import track_job
from app.models import Platform


def sync_one(
    platform: str, lookback_days: int | None = None, job_name: str | None = None
) -> dict[str, int]:
    p = Platform(platform)
    days = lookback_days or get_settings().ads_metrics_lookback_days
    with track_job(job_name or f"ads_{p.value}") as stats:
        if not is_configured(p):
            stats["skipped"] = f"{p.value} not configured"
            return {}
        client = get_platform(p)
        with session_scope() as s:
            stats.update(sync.sync_platform(client, s, lookback_days=days))
        return dict(stats)


def hourly_google() -> None:
    sync_one("google")


def hourly_meta() -> None:
    sync_one("meta")


def hourly_tiktok() -> None:
    sync_one("tiktok")


def nightly_all() -> None:
    """Re-read a longer window: platforms keep revising conversions for days."""
    days = get_settings().ads_nightly_lookback_days
    for p in Platform:
        sync_one(p.value, lookback_days=days, job_name=f"ads_{p.value}_nightly")
