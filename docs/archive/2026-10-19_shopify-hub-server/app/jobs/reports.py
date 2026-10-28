"""Scheduled reports."""

from __future__ import annotations

from app import daily_report
from app.alerts import send_slack
from app.db import session_scope
from app.jobs.tracking import track_job
from app.queue import get_redis


def daily_summary() -> None:
    """08:00 store time: yesterday's summary to Slack."""
    with track_job("daily_report") as stats, session_scope() as s:
        report = daily_report.build(s, redis=get_redis())
        stats["sent"] = send_slack(daily_report.format_slack(report))
        stats["day"] = report["day"]
