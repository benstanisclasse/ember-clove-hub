"""Creative generation jobs: poll Higgsfield until outputs are stored."""

from __future__ import annotations

from sqlalchemy import select

from app.config import get_settings
from app.creatives import pipeline
from app.db import session_scope
from app.log import get_logger
from app.models import GenerationJob

log = get_logger(__name__)


def poll_active() -> int:
    """Every minute: advance every queued / running job (no-op when there are none)."""
    if not get_settings().higgsfield_configured:
        return 0
    with session_scope() as s:
        ids = pipeline.active_job_ids(s)
    for job_id in ids:
        try:
            pipeline.poll_job(job_id)
        except Exception:
            log.exception("generation_poll_failed", job=job_id)  # next minute retries
    return len(ids)


def poll_request(request_id: str) -> str:
    """Webhook nudge for one Higgsfield request id."""
    with session_scope() as s:
        job_id = s.scalar(
            select(GenerationJob.id).where(GenerationJob.higgsfield_job_id == request_id)
        )
    return pipeline.poll_job(job_id) if job_id else "unknown request"
