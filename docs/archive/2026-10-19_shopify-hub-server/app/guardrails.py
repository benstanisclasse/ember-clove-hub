"""Server-side hard limits. Enforced in two places:

1. when a proposal is created and again before it executes (``check_action``), so Claude
   gets an immediate, specific "no" instead of a proposal that can never run;
2. inside every platform write method (``enforce_*``, called from ``AdPlatform``), so no path
   -- approvals, auto-approve rules, the CLI, a future bug -- can exceed them.

Limits (all in the ``settings`` table):

* ``kill_switch``           -- blocks every write.
* ``daily_spend_cap``       -- the sum of all *active* daily budgets may not exceed it, and no
  budget may go up once today's actual spend has reached it. ``null`` = not set = every
  spend-increasing action is blocked. Decreases and pauses are always allowed.
* ``max_budget_change_pct`` -- per campaign / ad set **per day, cumulative**: measured from the
  budget it had before its first change today, so repeated small bumps can't add up.
* ``max_new_ads_per_day``   -- ads created by the hub today (store timezone), all platforms.
* ``higgsfield_monthly_cap_usd`` -- enforced in the creative pipeline (see app.creatives.pipeline).

Budgets are compared in the ad account currency, assumed equal to the store currency.
"""

from __future__ import annotations

from datetime import UTC, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import business_settings
from app.actions import WritesBlockedError
from app.config import get_settings
from app.models import (
    ActionLog,
    ActionStatus,
    Ad,
    AdMetricsDaily,
    AdSet,
    Campaign,
    EntityStatus,
    Platform,
)

ZERO = Decimal("0")


class GuardrailError(WritesBlockedError):
    """A hard limit would be exceeded."""


def day_start_utc(now: datetime | None = None) -> datetime:
    """Midnight today in the store timezone, as a UTC timestamp."""
    tz = get_settings().tz
    local = (now or datetime.now(UTC)).astimezone(tz)
    return datetime.combine(local.date(), time.min, tzinfo=tz).astimezone(UTC)


# --- spend accounting ------------------------------------------------------------------------


def _campaign_budget(session: Session, c: Campaign, only_active_sets: bool = True) -> Decimal:
    """What an active campaign can spend per day: its own budget, or its ad sets' budgets."""
    if c.daily_budget:
        return c.daily_budget
    q = select(func.coalesce(func.sum(AdSet.daily_budget), 0)).where(AdSet.campaign_id == c.id)
    if only_active_sets:
        q = q.where(AdSet.status == EntityStatus.ACTIVE)
    return Decimal(str(session.scalar(q) or 0))


def committed_daily_budget(session: Session) -> Decimal:
    """Sum of daily budgets that can spend right now (active campaigns, all platforms)."""
    total = ZERO
    for c in session.scalars(select(Campaign).where(Campaign.status == EntityStatus.ACTIVE)):
        total += _campaign_budget(session, c)
    return total


def spend_today(session: Session) -> Decimal:
    tz = get_settings().tz
    today = datetime.now(UTC).astimezone(tz).date()
    return Decimal(
        str(
            session.scalar(
                select(func.coalesce(func.sum(AdMetricsDaily.spend), 0)).where(
                    AdMetricsDaily.date == today
                )
            )
            or 0
        )
    )


def _entity(session: Session, platform: str, level: str, external_id: str) -> Any:
    model = {"campaign": Campaign, "ad_set": AdSet, "ad": Ad}[level]
    row = session.scalar(
        select(model).where(
            model.platform == Platform(platform), model.external_id == str(external_id)
        )
    )
    if row is None:
        raise GuardrailError(
            f"{platform} {level} {external_id} is not synced yet; run the ad sync so limits can be checked"
        )
    return row


def _require_cap(session: Session) -> Decimal:
    cap = business_settings.load(session).daily_spend_cap
    if cap is None:
        raise GuardrailError(
            "daily_spend_cap is not set: actions that can increase spend are blocked until you set it"
        )
    return cap


def _check_cap(session: Session, new_committed: Decimal, what: str) -> None:
    cap = _require_cap(session)
    if new_committed > cap:
        raise GuardrailError(
            f"{what} would raise committed daily budgets to {new_committed:.2f}, above daily_spend_cap {cap}"
        )
    today = spend_today(session)
    if today >= cap:
        raise GuardrailError(
            f"today's spend ({today:.2f}) has already reached daily_spend_cap {cap}"
        )


# --- individual limits -----------------------------------------------------------------------


def budget_baseline(
    session: Session, platform: str, level: str, external_id: str, current: Decimal | None
) -> Decimal | None:
    """The budget before its first successful change today (or the current one)."""
    first = session.scalars(
        select(ActionLog.payload)
        .where(
            ActionLog.action_type == f"{platform}.update_budget",
            ActionLog.target_type == level,
            ActionLog.target_id == str(external_id),
            ActionLog.status == ActionStatus.SUCCESS,
            ActionLog.created_at >= day_start_utc(),
        )
        .order_by(ActionLog.created_at, ActionLog.id)
        .limit(1)
    ).first()
    prev = (first or {}).get("previous_daily_budget")
    return Decimal(str(prev)) if prev not in (None, "") else current


def enforce_budget(
    session: Session, platform: str, level: str, external_id: str, new: Decimal
) -> None:
    """Budget update: positive, within today's cumulative % limit, and within the spend cap."""
    bs = business_settings.load(session)
    if bs.kill_switch:
        raise GuardrailError("kill switch is on")
    if level == "ad":
        raise GuardrailError("budgets live on campaigns or ad sets")
    new = Decimal(str(new))
    if new <= 0:
        raise GuardrailError("new budget must be positive (pause instead)")
    row = _entity(session, platform, level, external_id)
    current = row.daily_budget
    baseline = budget_baseline(session, platform, level, external_id, current)
    if baseline:
        change = abs(new - baseline) / baseline * 100
        if change > Decimal(str(bs.max_budget_change_pct)):
            raise GuardrailError(
                f"{change:.1f}% change vs today's starting budget {baseline} exceeds max_budget_change_pct "
                f"({bs.max_budget_change_pct}%/day)"
            )
    if current is not None and new <= current:
        return  # decreases are always allowed
    # Does this budget count toward committed spend right now?
    campaign = row if level == "campaign" else session.get(Campaign, row.campaign_id)
    if campaign.status != EntityStatus.ACTIVE or row.status != EntityStatus.ACTIVE:
        return  # not spending; checked again when activated
    if level == "ad_set" and campaign.daily_budget:
        return  # campaign budget governs; the ad set budget doesn't add spend
    committed = committed_daily_budget(session)
    _check_cap(
        session, committed - (current or ZERO) + new, f"raising {level} {external_id} to {new}"
    )


def enforce_activation(session: Session, platform: str, level: str, external_id: str) -> None:
    """Turning something on may add its budget to committed spend."""
    if business_settings.load(session).kill_switch:
        raise GuardrailError("kill switch is on")
    row = _entity(session, platform, level, external_id)
    if row.status == EntityStatus.ACTIVE:
        return
    added = ZERO
    if level == "campaign":
        added = _campaign_budget(session, row, only_active_sets=True)
    elif level == "ad_set":
        campaign = session.get(Campaign, row.campaign_id)
        if campaign.status == EntityStatus.ACTIVE and not campaign.daily_budget:
            added = row.daily_budget or ZERO
    else:  # an ad: spends only if its ad set + campaign are active; their budgets are already counted
        ad_set = session.get(AdSet, row.ad_set_id)
        campaign = session.get(Campaign, ad_set.campaign_id)
        if ad_set.status != EntityStatus.ACTIVE or campaign.status != EntityStatus.ACTIVE:
            return
    _require_cap(session)
    _check_cap(
        session, committed_daily_budget(session) + added, f"activating {level} {external_id}"
    )


def ads_created_today(session: Session) -> int:
    return int(
        session.scalar(
            select(func.count(ActionLog.id)).where(
                ActionLog.action_type.like("%.create_ad"),
                ActionLog.status == ActionStatus.SUCCESS,
                ActionLog.created_at >= day_start_utc(),
            )
        )
        or 0
    )


def enforce_new_ads(session: Session, n: int = 1) -> None:
    bs = business_settings.load(session)
    if bs.kill_switch:
        raise GuardrailError("kill switch is on")
    done = ads_created_today(session)
    if done + n > bs.max_new_ads_per_day:
        raise GuardrailError(
            f"max_new_ads_per_day is {bs.max_new_ads_per_day}; {done} created today, {n} more requested"
        )


# --- proposal-level check --------------------------------------------------------------------


def check_action(session: Session, action_type: str, payload: dict[str, Any]) -> None:
    """Run the limits that apply to a proposal (at proposal time and before execution)."""
    if business_settings.load(session).kill_switch:
        raise GuardrailError("kill switch is on")
    if action_type == "budget_change":
        enforce_budget(
            session,
            payload["platform"],
            payload["level"],
            payload["external_id"],
            Decimal(str(payload["new_daily_budget"])),
        )
    elif action_type == "activate":
        enforce_activation(session, payload["platform"], payload["level"], payload["external_id"])
    elif action_type == "launch_creative":
        enforce_new_ads(session, len(payload.get("platforms") or []))
    elif action_type == "generate_creatives" and payload.get("estimated_usd"):
        from app.creatives.pipeline import check_budget

        check_budget(session, Decimal(str(payload["estimated_usd"])))
