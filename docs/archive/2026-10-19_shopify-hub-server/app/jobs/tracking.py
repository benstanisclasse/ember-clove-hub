"""Record each job execution in ``job_runs`` so staleness can be detected."""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import session_scope
from app.log import get_logger, scrub
from app.models import JobRun, JobRunStatus

log = get_logger(__name__)


@contextmanager
def track_job(name: str, session_factory: Any = session_scope) -> Iterator[dict[str, Any]]:
    """Context manager: writes a RUNNING row, then SUCCESS/FAILED with stats or error.

    Yields a dict the job can fill with stats (``stats["orders"] = 42``).
    """
    stats: dict[str, Any] = {}
    started = time.monotonic()
    with session_factory() as s:
        run = JobRun(job_name=name, status=JobRunStatus.RUNNING)
        s.add(run)
        s.flush()
        run_id = run.id
    try:
        yield stats
    except Exception as exc:
        _finish(session_factory, run_id, JobRunStatus.FAILED, stats, scrub(repr(exc))[:4000])
        log.exception("job_failed", job=name)
        raise
    else:
        stats.setdefault("duration_s", round(time.monotonic() - started, 3))
        _finish(session_factory, run_id, JobRunStatus.SUCCESS, stats, None)
        log.info("job_succeeded", job=name, **stats)


def _finish(
    factory: Any, run_id: int, status: JobRunStatus, stats: dict[str, Any], error: str | None
) -> None:
    with factory() as s:
        run: JobRun | None = s.get(JobRun, run_id)
        if run is None:
            return
        run.status = status
        run.finished_at = datetime.now(UTC)
        run.stats = stats or None
        run.error = error


def last_success(session: Session, name: str) -> datetime | None:
    """When ``name`` last finished successfully (None if never)."""
    value = session.scalar(
        select(func.max(JobRun.finished_at)).where(
            JobRun.job_name == name, JobRun.status == JobRunStatus.SUCCESS
        )
    )
    if value is not None and value.tzinfo is None:  # SQLite drops tz info
        value = value.replace(tzinfo=UTC)
    return value
