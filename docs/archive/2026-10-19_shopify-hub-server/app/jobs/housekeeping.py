"""Daily cleanup of operational rows that only matter for a while."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete

from app.db import session_scope
from app.jobs.tracking import track_job
from app.models import JobRun, OAuthToken, WebhookEvent

JOB_RUNS_DAYS = 30
WEBHOOK_EVENTS_DAYS = 90


def run() -> None:
    """Prune job_runs (> 30 days) and webhook_events (> 90 days). actions_log and
    conversion_events are kept: they're the audit trail."""
    now = datetime.now(UTC)
    with track_job("housekeeping") as stats, session_scope() as s:
        stats["job_runs_deleted"] = s.execute(
            delete(JobRun).where(JobRun.started_at < now - timedelta(days=JOB_RUNS_DAYS))
        ).rowcount
        stats["oauth_tokens_deleted"] = s.execute(
            delete(OAuthToken).where(OAuthToken.expires_at < now - timedelta(days=1))
        ).rowcount
        stats["webhook_events_deleted"] = s.execute(
            delete(WebhookEvent).where(
                WebhookEvent.received_at < now - timedelta(days=WEBHOOK_EVENTS_DAYS)
            )
        ).rowcount
