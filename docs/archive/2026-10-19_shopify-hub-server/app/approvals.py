"""Proposals -> (auto-)approval -> execution.

Every write Claude asks for becomes a ``pending_approvals`` row with a one-line summary.
It executes only when approved (by you via Claude's approve_action, the CLI, or an
auto-approve rule) and passes guardrails at both proposal and execution time. Execution
goes through the platform write methods, i.e. through the read-only / kill-switch gate and
``actions_log`` with ``approval_id`` and ``approved_by`` recorded.

Action types (also the ``action_type`` used by auto-approve rules):
``budget_change`` · ``pause_ad`` · ``activate`` · ``generate_creatives`` · ``launch_creative``
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import business_settings, guardrails
from app.actions import ActionContext, SessionFactory
from app.business_settings import AutoApproveRule
from app.config import Settings, get_settings
from app.db import session_scope
from app.log import get_logger, scrub
from app.models import (
    Ad,
    AdSet,
    ApprovalStatus,
    Campaign,
    Creative,
    CreativeStatus,
    EntityStatus,
    PendingApproval,
    Platform,
)

log = get_logger(__name__)
ACTIONS = ("budget_change", "pause_ad", "activate", "generate_creatives", "launch_creative")
PlatformFactory = Callable[[str], Any]


class ApprovalError(Exception):
    """Bad proposal input, or an approval that can't be acted on."""


# --- auto-approve -------------------------------------------------------------------------------


def _amount(action_type: str, payload: dict[str, Any]) -> Decimal:
    key = {
        "budget_change": "new_daily_budget",
        "generate_creatives": "estimated_usd",
        "launch_creative": "daily_budget",
    }.get(action_type)
    return Decimal(str(payload.get(key) or 0)) if key else Decimal("0")


def match_rule(
    rules: list[AutoApproveRule], action_type: str, payload: dict[str, Any]
) -> AutoApproveRule | None:
    """First rule whose limits the proposal fits within (no limits = matches any of its type)."""
    platforms = set(
        payload.get("platforms") or ([payload["platform"]] if payload.get("platform") else [])
    )
    for r in rules:
        if r.action_type != action_type:
            continue
        if r.platforms is not None and not platforms <= set(r.platforms):
            continue
        if (
            r.max_change_pct is not None
            and abs(float(payload.get("change_pct") or 1e9)) > r.max_change_pct
        ):
            continue
        if r.max_amount is not None and _amount(action_type, payload) > r.max_amount:
            continue
        return r
    return None


# --- proposal validation -----------------------------------------------------------------------


def _entity(session: Session, platform: str, level: str, external_id: str) -> Any:
    model = {"campaign": Campaign, "ad_set": AdSet, "ad": Ad}.get(level)
    if model is None:
        raise ApprovalError("level must be campaign, ad_set or ad")
    row = session.scalar(
        select(model).where(
            model.platform == Platform(platform), model.external_id == str(external_id)
        )
    )
    if row is None:
        raise ApprovalError(f"{platform} {level} {external_id} not found (has the ad sync run?)")
    return row


def build_budget_change(
    session: Session, platform: str, level: str, external_id: str, new_daily_budget: Any
) -> tuple[dict[str, Any], str]:
    row = _entity(session, platform, level, external_id)
    if level == "ad":
        raise ApprovalError("budgets live on campaigns or ad sets")
    current = row.daily_budget
    new = Decimal(str(new_daily_budget)).quantize(Decimal("0.01"))
    pct = float((new - current) / current * 100) if current else None
    payload = {
        "platform": platform,
        "level": level,
        "external_id": str(external_id),
        "name": row.name,
        "current_daily_budget": str(current) if current is not None else None,
        "new_daily_budget": str(new),
        "change_pct": round(pct, 1) if pct is not None else None,
    }
    change = f" ({pct:+.1f}%)" if pct is not None else ""
    summary = f"{platform} {level} '{row.name or external_id}': daily budget {current or '?'} -> {new}{change}"
    return payload, summary


def build_status(
    session: Session, platform: str, level: str, external_id: str, status: EntityStatus
) -> tuple[dict[str, Any], str]:
    row = _entity(session, platform, level, external_id)
    payload = {
        "platform": platform,
        "level": level,
        "external_id": str(external_id),
        "name": row.name,
        "status": status.value,
        "current_status": row.status.value,
    }
    verb = "pause" if status == EntityStatus.PAUSED else "activate"
    return (
        payload,
        f"{verb} {platform} {level} '{row.name or external_id}' (now {row.status.value})",
    )


# --- core ---------------------------------------------------------------------------------------


def propose(
    action_type: str,
    payload: dict[str, Any],
    summary: str,
    *,
    rationale: str | None = None,
    requested_by: str | None = None,
    session_factory: SessionFactory = session_scope,
    platform_factory: PlatformFactory | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Store a proposal (after guardrails); auto-approve and execute it if a rule matches."""
    if action_type not in ACTIONS:
        raise ApprovalError(f"unknown action {action_type}")
    s = settings or get_settings()
    with session_factory() as db:
        guardrails.check_action(db, action_type, payload)
        rule = match_rule(business_settings.load(db).auto_approve_rules, action_type, payload)
        row = PendingApproval(
            action_type=action_type,
            summary=summary,
            rationale=rationale,
            payload=payload,
            requested_by=requested_by,
            expires_at=datetime.now(UTC) + timedelta(hours=s.approval_expiry_hours),
        )
        db.add(row)
        db.flush()
        approval_id = row.id
    log.info(
        "proposal_created",
        id=approval_id,
        action=action_type,
        auto_rule=rule.name if rule else None,
    )
    if rule is None:
        return {
            "approval_id": approval_id,
            "status": "pending",
            "summary": summary,
            "next": f"Say 'approve {approval_id}' to execute, or 'reject {approval_id}'.",
        }
    with session_factory() as db:
        a = db.get(PendingApproval, approval_id)
        a.auto_approved, a.auto_approve_rule = True, rule.name
    result = approve(
        approval_id,
        decided_by=f"auto:{rule.name}",
        via_mcp=False,
        session_factory=session_factory,
        platform_factory=platform_factory,
        settings=s,
    )
    return {**result, "auto_approved_by_rule": rule.name}


def expire_old(session: Session) -> int:
    res = session.execute(
        update(PendingApproval)
        .where(
            PendingApproval.status == ApprovalStatus.PENDING,
            PendingApproval.expires_at < datetime.now(UTC),
        )
        .values(status=ApprovalStatus.EXPIRED)
    )
    return res.rowcount or 0


def reject(
    approval_id: int,
    decided_by: str,
    reason: str | None = None,
    session_factory: SessionFactory = session_scope,
) -> dict[str, Any]:
    with session_factory() as db:
        a = db.get(PendingApproval, approval_id)
        if a is None or a.status != ApprovalStatus.PENDING:
            raise ApprovalError(f"approval {approval_id} is not pending")
        a.status, a.decided_by, a.decided_at = (
            ApprovalStatus.REJECTED,
            decided_by,
            datetime.now(UTC),
        )
        a.result = {"reason": reason} if reason else None
    return {"approval_id": approval_id, "status": "rejected"}


def approve(
    approval_id: int,
    decided_by: str,
    *,
    via_mcp: bool = True,
    session_factory: SessionFactory = session_scope,
    platform_factory: PlatformFactory | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Approve and execute. Exactly-once: the pending -> approved transition is atomic."""
    s = settings or get_settings()
    with session_factory() as db:
        if via_mcp and not business_settings.load(db).approvals_via_mcp:
            raise ApprovalError(
                "approving through Claude is turned off (approvals_via_mcp); use the CLI"
            )
        expire_old(db)
        claimed = db.execute(
            update(PendingApproval)
            .where(
                PendingApproval.id == approval_id, PendingApproval.status == ApprovalStatus.PENDING
            )
            .values(
                status=ApprovalStatus.APPROVED, decided_by=decided_by, decided_at=datetime.now(UTC)
            )
        ).rowcount
        a = db.get(PendingApproval, approval_id)
        if a is None:
            raise ApprovalError(f"approval {approval_id} not found")
        if not claimed:
            raise ApprovalError(f"approval {approval_id} is {a.status.value}, not pending")
        action_type, payload = a.action_type, dict(a.payload)

    ctx = ActionContext(
        actor="mcp" if via_mcp else "approval",
        requested_by=decided_by,
        approval_id=approval_id,
        approved_by=decided_by,
    )
    try:
        with session_factory() as db:
            guardrails.check_action(
                db, action_type, payload
            )  # limits may have changed since proposal
        result = _execute(action_type, payload, ctx, session_factory, platform_factory, s)
        status = ApprovalStatus.EXECUTED
    except (
        Exception
    ) as exc:  # any failure (guardrail, platform, validation) is recorded on the approval
        result, status = {"error": scrub(str(exc))[:1000]}, ApprovalStatus.FAILED
        log.warning("approval_failed", id=approval_id, error=result["error"])
    with session_factory() as db:
        a = db.get(PendingApproval, approval_id)
        a.status, a.result, a.executed_at = status, result, datetime.now(UTC)
    return {"approval_id": approval_id, "status": status.value, "result": result}


# --- execution ----------------------------------------------------------------------------------


def _execute(
    action_type: str,
    payload: dict[str, Any],
    ctx: ActionContext,
    session_factory: SessionFactory,
    platform_factory: PlatformFactory | None,
    s: Settings,
) -> dict[str, Any]:
    if platform_factory is None:
        from app.integrations.ads.registry import get_platform as platform_factory
    if action_type == "budget_change":
        new = Decimal(payload["new_daily_budget"])
        platform_factory(payload["platform"]).update_budget(
            payload["level"], payload["external_id"], new, ctx=ctx
        )
        with session_factory() as db:
            _entity(
                db, payload["platform"], payload["level"], payload["external_id"]
            ).daily_budget = new
        return {"daily_budget": str(new)}
    if action_type in ("pause_ad", "activate"):
        status = EntityStatus(payload["status"])
        platform_factory(payload["platform"]).set_status(
            payload["level"], payload["external_id"], status, ctx=ctx
        )
        with session_factory() as db:
            _entity(
                db, payload["platform"], payload["level"], payload["external_id"]
            ).status = status
        return {"status": status.value}
    if action_type == "generate_creatives":
        from app.creatives.briefs import CreativeBrief
        from app.creatives.pipeline import generate_creatives

        res = generate_creatives(
            CreativeBrief.model_validate(payload["brief"]),
            int(payload["n"]),
            ctx=ctx,
            session_factory=session_factory,
            settings=s,
        )
        return {
            "creative_ids": res.creative_ids,
            "estimated_usd": str(res.estimated_usd),
            "errors": res.errors,
        }
    if action_type == "launch_creative":
        from app.creatives.pipeline import LaunchRequest, launch_creative

        req = LaunchRequest(
            creative_id=int(payload["creative_id"]),
            platforms=list(payload["platforms"]),
            landing_url=payload["landing_url"],
            primary_text=payload["primary_text"],
            headline=payload.get("headline"),
            daily_budget=Decimal(payload["daily_budget"]) if payload.get("daily_budget") else None,
            countries=list(payload.get("countries") or ["US"]),
            ad_set_ids=dict(payload.get("ad_set_ids") or {}),
        )
        return launch_creative(
            req,
            platform_factory=platform_factory,
            ctx=ctx,
            session_factory=session_factory,
            settings=s,
        )
    raise ApprovalError(f"no executor for {action_type}")


def creative_launch_payload(
    session: Session,
    creative_id: int,
    platforms: list[str],
    daily_budget: Any,
    landing_url: str | None,
    primary_text: str | None,
    headline: str | None,
    countries: list[str] | None,
    s: Settings,
) -> tuple[dict[str, Any], str]:
    c = session.get(Creative, creative_id)
    if c is None or c.status not in (
        CreativeStatus.READY,
        CreativeStatus.APPROVED,
        CreativeStatus.LAUNCHED,
    ):
        raise ApprovalError(
            f"creative {creative_id} is not ready (status: {c.status.value if c else 'missing'})"
        )
    bad = set(platforms) - {"meta", "tiktok", "google"}
    if bad or not platforms:
        raise ApprovalError("platforms must be a non-empty subset of meta, tiktok, google")
    url = landing_url or s.storefront_url
    if not url:
        raise ApprovalError("landing_url is required (or set STORE_PUBLIC_URL)")
    text = primary_text or ((c.brief or {}).get("hooks") or [None])[0] or "Shop now"
    budget = (
        Decimal(str(daily_budget)).quantize(Decimal("0.01"))
        if daily_budget not in (None, "")
        else None
    )
    payload = {
        "creative_id": creative_id,
        "platforms": platforms,
        "daily_budget": str(budget) if budget else None,
        "landing_url": url,
        "primary_text": text,
        "headline": headline,
        "countries": countries or ["US"],
    }
    summary = (
        f"launch creative {creative_id} ({c.type.value}) on {', '.join(platforms)}"
        + (f" with a new campaign at {budget}/day each" if budget else "")
        + " -- created PAUSED"
    )
    return payload, summary
