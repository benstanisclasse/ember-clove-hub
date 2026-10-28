"""The single gate every external write passes through.

Platform write methods (budget changes, status changes, creating campaigns/ads,
uploading media) never call the API directly; they run inside :func:`write_action`,
which:

1. refuses when ``read_only`` or ``kill_switch`` is on (logged as ``blocked``),
2. records the attempt in ``actions_log`` with payload, actor and approval id,
3. records the outcome (success + result, or failure + scrubbed error).

Phase 6 adds the numeric guardrails (spend cap, max % change, max new ads) on top of
this; Phase 5's approval flow calls in with ``approval_id`` / ``approved_by``.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app import business_settings
from app.db import session_scope
from app.log import get_logger, scrub
from app.models import ActionLog, ActionStatus

log = get_logger(__name__)
SessionFactory = Callable[[], AbstractContextManager[Session]]


class WritesBlockedError(Exception):
    """A write was refused by read-only mode, the kill switch, or a guardrail."""


@dataclass
class ActionContext:
    """Who is asking, and on whose approval."""

    actor: str = "system"  # mcp | scheduler | worker | admin | cli | system
    requested_by: str | None = None
    tool: str | None = None
    approval_id: int | None = None
    approved_by: str | None = None


@dataclass
class ActionResult:
    """Filled in by the code inside ``write_action``; stored in ``actions_log.result``."""

    data: dict[str, Any] = field(default_factory=dict)


@contextmanager
def write_action(
    action_type: str,
    *,
    target_type: str,
    target_id: str | None,
    payload: dict[str, Any],
    ctx: ActionContext | None = None,
    session_factory: SessionFactory = session_scope,
) -> Iterator[ActionResult]:
    """Guard + audit one external write. See module docstring."""
    ctx = ctx or ActionContext()
    entry = dict(
        actor=ctx.actor,
        requested_by=ctx.requested_by,
        tool=ctx.tool,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        payload=payload,
        approval_id=ctx.approval_id,
        approved_by=ctx.approved_by,
    )
    with session_factory() as s:
        settings = business_settings.load(s)
        reason = None
        if not settings.writes_allowed:
            reason = "kill switch is on" if settings.kill_switch else "read-only mode is on"
            s.add(ActionLog(**entry, status=ActionStatus.BLOCKED, error=reason))
    # Raise only after the scope committed, so the "blocked" audit row is kept.
    if reason:
        log.warning("write_blocked", action=action_type, target=target_id, reason=reason)
        raise WritesBlockedError(f"{action_type} blocked: {reason}")

    result = ActionResult()
    started = time.monotonic()
    try:
        yield result
    except Exception as exc:
        blocked = isinstance(exc, WritesBlockedError)  # a guardrail said no inside the action
        with session_factory() as s:
            s.add(
                ActionLog(
                    **entry,
                    status=ActionStatus.BLOCKED if blocked else ActionStatus.FAILED,
                    error=scrub(str(exc) if blocked else repr(exc))[:4000],
                    duration_ms=int((time.monotonic() - started) * 1000),
                )
            )
        raise
    with session_factory() as s:
        s.add(
            ActionLog(
                **entry,
                status=ActionStatus.SUCCESS,
                result=result.data or None,
                duration_ms=int((time.monotonic() - started) * 1000),
            )
        )
    log.info("write_succeeded", action=action_type, target=target_id)
