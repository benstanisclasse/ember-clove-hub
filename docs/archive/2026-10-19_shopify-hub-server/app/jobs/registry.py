"""Every scheduled job, its cadence, and when it counts as stale.

Later phases add their sync jobs here (Shopify, ad platforms, Higgsfield polling,
nightly analytics); the scheduler and the watchdog both read this list.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class JobSpec:
    name: str
    func: str  # dotted path, resolved lazily so importing the registry stays cheap
    interval_minutes: int
    stale_after_minutes: int | None  # None = never alert on staleness
    run_in_scheduler: bool = False  # True: run inline (watchdog), False: enqueue to RQ
    queue: str = "default"
    external: bool = False  # run outside the app (systemd timer); only watched for staleness
    cron: str | None = None  # crontab in the store timezone; overrides interval_minutes


JOBS: list[JobSpec] = [
    JobSpec(
        name="watchdog",
        func="app.jobs.watchdog.run_watchdog",
        interval_minutes=5,
        stale_after_minutes=None,  # covered externally by the heartbeat URL
        run_in_scheduler=True,
    ),
    # --- Shopify (no-op until configured) ---
    JobSpec(
        name="shopify_orders",
        func="app.jobs.shopify.incremental_orders",
        interval_minutes=15,
        stale_after_minutes=60,
    ),
    JobSpec(
        name="shopify_products",
        func="app.jobs.shopify.nightly_products",
        interval_minutes=24 * 60,
        stale_after_minutes=26 * 60,
        queue="low",
    ),
    # --- Ad platforms (no-op until configured) ---
    *(
        JobSpec(
            name=f"ads_{p}",
            func=f"app.jobs.ads.hourly_{p}",
            interval_minutes=60,
            stale_after_minutes=3 * 60,
        )
        for p in ("google", "meta", "tiktok")
    ),
    JobSpec(
        name="ads_nightly",
        func="app.jobs.ads.nightly_all",
        interval_minutes=24 * 60,
        stale_after_minutes=None,
        queue="low",
    ),
    # --- Conversions (no-op until conversions_enabled) ---
    JobSpec(
        name="conversions_flush",
        func="app.jobs.conversions.flush_browser_events",
        interval_minutes=1,
        stale_after_minutes=None,
    ),
    JobSpec(
        name="conversions_sweep",
        func="app.jobs.conversions.sweep",
        interval_minutes=15,
        stale_after_minutes=60,
    ),
    # --- Higgsfield (no-op until configured / no active jobs) ---
    JobSpec(
        name="higgsfield_poll",
        func="app.jobs.creatives.poll_active",
        interval_minutes=1,
        stale_after_minutes=None,
    ),
    # --- Analytics + ML (Phase 7) ---
    JobSpec(
        name="creative_metrics",
        func="app.jobs.analytics.nightly_creative_metrics",
        interval_minutes=24 * 60,
        stale_after_minutes=26 * 60,
        queue="low",
        cron="30 2 * * *",
    ),
    JobSpec(
        name="budget_bandit",
        func="app.jobs.analytics.budget_bandit",
        interval_minutes=24 * 60,
        stale_after_minutes=26 * 60,
        queue="low",
        cron="45 6 * * *",
    ),
    JobSpec(
        name="creative_model",
        func="app.jobs.analytics.train_creative_model",
        interval_minutes=7 * 24 * 60,
        stale_after_minutes=8 * 24 * 60,
        queue="low",
        cron="30 3 * * 0",
    ),
    JobSpec(
        name="daily_report",
        func="app.jobs.reports.daily_summary",
        interval_minutes=24 * 60,
        stale_after_minutes=26 * 60,
        queue="low",
        cron="0 8 * * *",
    ),
    JobSpec(
        name="housekeeping",
        func="app.jobs.housekeeping.run",
        interval_minutes=24 * 60,
        stale_after_minutes=None,
        queue="low",
    ),
    JobSpec(
        name="backup",
        func="scripts/backup.sh",  # systemd timer on the VM; reports via `app.cli jobs record`
        interval_minutes=24 * 60,
        stale_after_minutes=26 * 60,
        external=True,
    ),
    JobSpec(
        name="restore_test",
        func="scripts/restore-test.sh",  # weekly systemd timer
        interval_minutes=7 * 24 * 60,
        stale_after_minutes=8 * 24 * 60,
        external=True,
    ),
]


def resolve(dotted: str) -> Callable[[], object]:
    module, _, attr = dotted.rpartition(".")
    mod = __import__(module, fromlist=[attr])
    return getattr(mod, attr)  # type: ignore[no-any-return]
