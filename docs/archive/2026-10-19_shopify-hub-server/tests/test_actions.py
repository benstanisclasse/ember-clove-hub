"""The write gate: read-only + kill switch block writes; every attempt is audited."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import business_settings
from app.actions import ActionContext, WritesBlockedError, write_action
from app.models import ActionLog, ActionStatus


def _logs(session: Session) -> list[ActionLog]:
    session.expire_all()
    return list(
        session.scalars(
            select(ActionLog)
            .where(ActionLog.action_type != "setting_change")
            .order_by(ActionLog.id)
        )
    )


def test_blocked_by_default_read_only(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    ran = []
    with pytest.raises(WritesBlockedError, match="read-only"):
        with write_action(
            "meta.update_budget",
            target_type="campaign",
            target_id="1",
            payload={"x": 1},
            session_factory=session_factory,
        ):
            ran.append(True)
    assert ran == []
    (log,) = _logs(session)
    assert (log.status, log.error, log.target_id) == (
        ActionStatus.BLOCKED,
        "read-only mode is on",
        "1",
    )


def test_success_records_result_and_context(writes_on, session: Session) -> None:  # type: ignore[no-untyped-def]
    ctx = ActionContext(
        actor="mcp",
        requested_by="claude",
        tool="approve_action",
        approval_id=None,
        approved_by="ben",
    )
    with write_action(
        "tiktok.set_status",
        target_type="ad",
        target_id="9",
        payload={"status": "paused"},
        ctx=ctx,
        session_factory=writes_on,
    ) as res:
        res.data = {"ok": True}
    (log,) = _logs(session)
    assert log.status == ActionStatus.SUCCESS and log.result == {"ok": True}
    assert (log.actor, log.requested_by, log.tool, log.approved_by) == (
        "mcp",
        "claude",
        "approve_action",
        "ben",
    )


def test_failure_is_logged_scrubbed_and_reraised(writes_on, session: Session) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(RuntimeError):
        with write_action(
            "google.create_ad",
            target_type="ad",
            target_id=None,
            payload={},
            session_factory=writes_on,
        ):
            raise RuntimeError("401 for access_token=SECRET")
    (log,) = _logs(session)
    assert log.status == ActionStatus.FAILED and "SECRET" not in (log.error or "")


def test_kill_switch_overrides(writes_on, session: Session) -> None:  # type: ignore[no-untyped-def]
    with writes_on() as s:
        business_settings.set_value(s, "kill_switch", True, actor="test")
    with pytest.raises(WritesBlockedError, match="kill switch"):
        with write_action(
            "meta.set_status",
            target_type="ad",
            target_id="1",
            payload={},
            session_factory=writes_on,
        ):
            pass
