"""Nightly analytics + ML jobs (all store-timezone cron schedules)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config import get_settings
from app.db import session_scope
from app.jobs.tracking import track_job
from app.ml import bandit, creative_metrics, model


def nightly_creative_metrics() -> None:
    """02:30: snapshots for yesterday (7 / 30 day and lifetime windows)."""
    as_of = datetime.now(UTC).astimezone(get_settings().tz).date() - timedelta(days=1)
    with track_job("creative_metrics") as stats, session_scope() as s:
        stats.update(creative_metrics.compute(s, as_of))
        stats["as_of"] = as_of.isoformat()


def budget_bandit() -> None:
    """06:45: budget reallocation proposals (land in the approval queue before the 08:00 report)."""
    with track_job("budget_bandit") as stats:
        out = bandit.run()
        stats.update(
            {
                "status": out["status"],
                "proposals": sum(1 for p in out["proposals"] if "approval_id" in p),
            }
        )


def train_creative_model() -> None:
    """Sundays 03:30: retrain the creative profit model (activates only if it clears the gates)."""
    with track_job("creative_model") as stats:
        out = model.train()
        stats.update({"status": out["status"], "n_labeled": out["n_labeled"]})
