"""Operational tables: audit log, approvals queue, runtime settings, job runs."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import (
    ActionStatus,
    ApprovalStatus,
    Base,
    BigIntPK,
    JobRunStatus,
    JSONType,
    Money,
    str_enum,
)


class ActionLog(Base):
    """Append-only record of every write action and every MCP tool call."""

    __tablename__ = "actions_log"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
    actor: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="mcp | scheduler | worker | admin | cli | system"
    )
    requested_by: Mapped[str | None] = mapped_column(String(255), comment="Client / user id")
    tool: Mapped[str | None] = mapped_column(String(128), comment="MCP tool name, if any")
    action_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(64))
    target_id: Mapped[str | None] = mapped_column(String(128))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    approval_id: Mapped[int | None] = mapped_column(
        ForeignKey("pending_approvals.id", ondelete="SET NULL"), index=True
    )
    approved_by: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[ActionStatus] = mapped_column(
        str_enum(ActionStatus, "action_status"), nullable=False
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    error: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)


class PendingApproval(Base):
    """A proposed write action waiting for a human decision."""

    __tablename__ = "pending_approvals"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, comment="One-line human summary")
    rationale: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType, nullable=False)
    requested_by: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[ApprovalStatus] = mapped_column(
        str_enum(ApprovalStatus, "approval_status"),
        default=ApprovalStatus.PENDING,
        index=True,
        nullable=False,
    )
    auto_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_approve_rule: Mapped[str | None] = mapped_column(String(128))
    decided_by: Mapped[str | None] = mapped_column(String(255))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONType)


class Setting(Base):
    """Runtime business settings (key -> JSON value). Typed access: ``app.business_settings``."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[Any] = mapped_column(JSONType, nullable=True)
    description: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    updated_by: Mapped[str | None] = mapped_column(String(255))


class SyncState(Base):
    """Cursors for incremental syncs, e.g. ``shopify:orders`` -> last ``updatedAt`` seen."""

    __tablename__ = "sync_state"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[Any] = mapped_column(JSONType, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class WebhookEvent(Base):
    """One received webhook delivery: de-duplication + audit.

    The payload is deliberately NOT stored (order webhooks carry customer PII); the
    worker re-fetches the resource by id through the API instead.
    """

    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, comment="shopify | ...")
    topic: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    delivery_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(128))
    payload_sha256: Mapped[str | None] = mapped_column(String(64))
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        String(16), default="received", nullable=False, comment="received|processed|ignored|failed"
    )
    error: Mapped[str | None] = mapped_column(Text)


class JobRun(Base):
    """One execution of a scheduled job; the watchdog alerts when these go stale."""

    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    job_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[JobRunStatus] = mapped_column(
        str_enum(JobRunStatus, "job_run_status"), default=JobRunStatus.RUNNING, nullable=False
    )
    error: Mapped[str | None] = mapped_column(Text)
    stats: Mapped[dict[str, Any] | None] = mapped_column(JSONType)


class ConversionEvent(Base):
    """One purchase reported (or attempted) to one platform. Unique per (platform, event,
    event_id) so a purchase is never reported twice, whatever retries / sweeps happen."""

    __tablename__ = "conversion_events"
    __table_args__ = (UniqueConstraint("platform", "event_name", "event_id"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    event_name: Mapped[str] = mapped_column(String(32), nullable=False)
    event_id: Mapped[str] = mapped_column(String(128), nullable=False)
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="sent | failed | skipped"
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, comment="skip reason or scrubbed error")
    value: Mapped[Decimal | None] = mapped_column(Money)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class ConversionEventCount(Base):
    """Daily counters for high-volume storefront events (PageView, AddToCart, ...)."""

    __tablename__ = "conversion_event_counts"
    __table_args__ = (UniqueConstraint("date", "platform", "event_name"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    platform: Mapped[str] = mapped_column(String(16), nullable=False, comment="hub = received")
    event_name: Mapped[str] = mapped_column(String(32), nullable=False)
    sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class OAuthClient(Base):
    """An MCP client registered via Dynamic Client Registration (or a trusted CIMD URL)."""

    __tablename__ = "oauth_clients"

    client_id: Mapped[str] = mapped_column(String(512), primary_key=True)
    client_name: Mapped[str | None] = mapped_column(String(255))
    redirect_uris: Mapped[list[str]] = mapped_column(JSONType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class OAuthToken(Base):
    """Authorization codes, access and refresh tokens. Only SHA-256 hashes are stored."""

    __tablename__ = "oauth_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, comment="code | access | refresh")
    client_id: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    scope: Mapped[str | None] = mapped_column(String(255))
    redirect_uri: Mapped[str | None] = mapped_column(Text)
    code_challenge: Mapped[str | None] = mapped_column(String(128))
    resource: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class BanditRun(Base):
    """One budget-allocation recommendation (Thompson sampling across platforms)."""

    __tablename__ = "bandit_runs"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
    window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    total_daily_budget: Mapped[Decimal] = mapped_column(Money, nullable=False)
    arms: Mapped[Any] = mapped_column(
        JSONType, nullable=False, comment="per-platform estimates + shares"
    )
    proposals: Mapped[Any] = mapped_column(JSONType, nullable=True, comment="approval ids / skips")
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="proposed | no_change | skipped"
    )
    notes: Mapped[str | None] = mapped_column(Text)


class MLModel(Base):
    """A trained (or declined) model version. Only one ``active`` model per kind."""

    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="active | inactive | retired"
    )
    n_labeled: Mapped[int] = mapped_column(Integer, nullable=False)
    metrics: Mapped[Any] = mapped_column(JSONType, nullable=True)
    features: Mapped[Any] = mapped_column(JSONType, nullable=True, comment="encoder vocabulary")
    storage_key: Mapped[str | None] = mapped_column(String(512))
    notes: Mapped[str | None] = mapped_column(Text)
