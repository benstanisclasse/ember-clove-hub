"""Typed runtime business settings stored in the ``settings`` table.

Defaults are deliberately safe: the hub starts in **read-only** mode, and caps that
are ``None`` mean "not configured", which guardrails (Phase 6) treat as *block every
action that would need that cap*. You have to set a cap explicitly before the hub
can spend money against it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActionLog, ActionStatus, Setting


class AutoApproveRule(BaseModel):
    """A rule letting a proposed action skip the approval queue.

    Example: ``{"name": "small-pauses", "action_type": "pause_ad", "max_abs_change": null}``
    or ``{"name": "tiny-budget-bumps", "action_type": "budget_change", "max_change_pct": 10}``.
    Matching logic lands with guardrails in Phase 6.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    action_type: str
    max_change_pct: float | None = Field(default=None, ge=0, le=100)
    max_amount: Decimal | None = Field(default=None, ge=0)
    platforms: list[str] | None = None


class BusinessSettings(BaseModel):
    """The full set of runtime settings with defaults and validation."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    read_only: bool = True
    kill_switch: bool = False
    daily_spend_cap: Decimal | None = Field(default=None, ge=0)
    max_budget_change_pct: float = Field(default=20.0, gt=0, le=100)
    max_new_ads_per_day: int = Field(default=5, ge=0)
    higgsfield_monthly_cap_usd: Decimal | None = Field(default=None, ge=0)
    auto_approve_rules: list[AutoApproveRule] = Field(default_factory=list)
    # Conversions (Phase 3b): reporting purchases / browser events to ad platforms.
    conversions_enabled: bool = False
    conversions_hashed_pii: bool = True
    conversions_exclude_countries: list[str] = Field(default_factory=list)
    # MCP (Phase 5): may Claude approve proposals through the approve_action tool?
    approvals_via_mcp: bool = True

    @property
    def writes_allowed(self) -> bool:
        """True only when neither read-only mode nor the kill switch is on."""
        return not self.read_only and not self.kill_switch


DESCRIPTIONS: dict[str, str] = {
    "read_only": "When true, every write action is blocked. Starts true.",
    "kill_switch": "Emergency stop: blocks all write actions regardless of other settings.",
    "daily_spend_cap": (
        "Max total daily ad budget across platforms (store currency). "
        "null = not set; spend increases blocked."
    ),
    "max_budget_change_pct": "Max % change to any single budget per day.",
    "max_new_ads_per_day": "Max ads the hub may create per day.",
    "higgsfield_monthly_cap_usd": (
        "Max Higgsfield spend per calendar month (USD). null = not set; generation blocked."
    ),
    "auto_approve_rules": "List of rules that let matching proposals skip the approval queue.",
    "conversions_enabled": (
        "Send purchases and storefront events to Meta / TikTok / Google. Off until you turn it on."
    ),
    "conversions_hashed_pii": (
        "Include SHA-256 hashed email + phone in purchase events (better matching). "
        "Raw values are never stored."
    ),
    "approvals_via_mcp": (
        "Allow approving proposals through Claude (approve_action tool). Off = approve only via the admin API/CLI."
    ),
    "conversions_exclude_countries": (
        'ISO country codes (billing) whose orders are never reported, e.g. ["DE", "FR"].'
    ),
}


def default_rows() -> list[dict[str, Any]]:
    """Rows used to seed the settings table (also used by the initial migration)."""
    defaults = BusinessSettings().model_dump(mode="json")
    return [{"key": k, "value": v, "description": DESCRIPTIONS[k]} for k, v in defaults.items()]


def load(session: Session) -> BusinessSettings:
    """Read all settings, falling back to defaults for missing keys.

    Unknown keys in the table are ignored. A stored value that fails validation raises,
    so a corrupted setting can never silently loosen a guardrail.
    """
    stored = {row.key: row.value for row in session.scalars(select(Setting))}
    known = {k: v for k, v in stored.items() if k in BusinessSettings.model_fields}
    return BusinessSettings.model_validate(known)


def set_value(
    session: Session, key: str, value: Any, actor: str, requested_by: str | None = None
) -> BusinessSettings:
    """Validate and store one setting, recording the change in ``actions_log``."""
    if key not in BusinessSettings.model_fields:
        raise KeyError(f"Unknown setting {key!r}. Known: {sorted(BusinessSettings.model_fields)}")
    current = load(session)
    try:
        updated = current.model_copy(update={})
        setattr(updated, key, value)  # validate_assignment=True validates here
    except ValidationError as exc:
        raise ValueError(f"Invalid value for {key!r}: {exc.errors()[0]['msg']}") from exc

    new_json = updated.model_dump(mode="json")[key]
    old_json = current.model_dump(mode="json")[key]
    row = session.get(Setting, key)
    if row is None:
        row = Setting(key=key, description=DESCRIPTIONS.get(key))
        session.add(row)
    row.value = new_json
    row.updated_by = requested_by or actor
    session.add(
        ActionLog(
            actor=actor,
            requested_by=requested_by,
            action_type="setting_change",
            target_type="setting",
            target_id=key,
            payload={"old": old_json, "new": new_json},
            status=ActionStatus.SUCCESS,
        )
    )
    session.flush()
    if key == "kill_switch" and old_json != new_json:
        from app.alerts import send_slack

        state = (
            ":octagonal_sign: *Kill switch ON*: all hub writes are blocked"
            if new_json
            else ":large_green_circle: *Kill switch OFF*: hub writes allowed again (read-only and limits still apply)"
        )
        send_slack(f"{state} (by {requested_by or actor})")
    return updated
