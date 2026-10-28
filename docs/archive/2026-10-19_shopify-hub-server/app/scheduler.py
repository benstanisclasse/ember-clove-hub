"""Scheduler process: ``python -m app.scheduler``.

Runs the watchdog inline and enqueues every other job from ``app.jobs.registry`` onto
RQ. Only one scheduler container runs, so jobs are never double-scheduled.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.jobs.registry import JOBS, JobSpec, resolve
from app.log import configure_logging, get_logger
from app.queue import get_queue

log = get_logger(__name__)


def _runner(job: JobSpec) -> Callable[[], None]:
    def run() -> None:
        if job.run_in_scheduler:
            try:
                resolve(job.func)()
            except Exception:
                log.exception("scheduled_job_failed", job=job.name)
        else:
            get_queue(job.queue).enqueue(job.func, description=job.name)
            log.info("job_enqueued", job=job.name, queue=job.queue)

    return run


def build_scheduler(start_now: bool = True) -> BlockingScheduler:
    """One interval job per registry entry; the first run fires immediately on boot."""
    sched = BlockingScheduler(timezone="UTC", job_defaults={"coalesce": True, "max_instances": 1})
    tz = get_settings().tz
    for job in (j for j in JOBS if not j.external):
        extra: dict[str, object] = {}
        if job.cron:  # wall-clock jobs (e.g. the 08:00 report) run at their time, not on boot
            trigger: CronTrigger | IntervalTrigger = CronTrigger.from_crontab(job.cron, timezone=tz)
        else:
            trigger = IntervalTrigger(minutes=job.interval_minutes)
            # NB: an explicit next_run_time=None would add the job *paused* in APScheduler 3.
            extra["next_run_time"] = datetime.now(UTC) if start_now else None
        sched.add_job(
            _runner(job),
            trigger,
            id=job.name,
            name=job.name,
            misfire_grace_time=3600 if job.cron else 300,
            **extra,
        )
    return sched


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    log.info("scheduler_starting", jobs=[j.name for j in JOBS if not j.external])
    build_scheduler().start()


if __name__ == "__main__":
    main()
