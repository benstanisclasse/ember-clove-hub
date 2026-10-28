"""Declarative base, shared column types and enums."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import JSON, BigInteger, DateTime, Integer, MetaData, Numeric, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# BIGINT primary keys on Postgres; SQLite only auto-increments INTEGER PRIMARY KEY,
# so tests (which run on SQLite) get INTEGER instead.
BigIntPK = BigInteger().with_variant(Integer, "sqlite")
JSONType = JSON().with_variant(JSONB(), "postgresql")
# Store-currency amounts.
Money = Numeric(14, 2)
# Small USD costs (per-second video billing etc.) need more precision.
UsdCost = Numeric(12, 4)

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base with deterministic constraint names (needed for clean migrations)."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map: ClassVar[dict[Any, Any]] = {dict[str, Any]: JSONType}


class TimestampMixin:
    """``created_at`` / ``updated_at`` maintained by the database / ORM."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


def str_enum(enum_cls: type[enum.Enum], name: str) -> SAEnum:
    """A portable enum column: VARCHAR + CHECK constraint, storing the enum *values*.

    Native Postgres ENUM types are avoided on purpose: adding a value to them needs
    ``ALTER TYPE`` outside a transaction, and sharing one across tables complicates
    migrations. A CHECK constraint gives the same safety with simpler migrations.
    """
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=32,
        values_callable=lambda e: [m.value for m in e],
        validate_strings=True,
    )


class Platform(enum.StrEnum):
    GOOGLE = "google"
    META = "meta"
    TIKTOK = "tiktok"


class EntityStatus(enum.StrEnum):
    """Normalized status for ad accounts, campaigns, ad sets and ads across platforms."""

    ACTIVE = "active"
    PAUSED = "paused"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    DELETED = "deleted"
    UNKNOWN = "unknown"


class AttributionMethod(enum.StrEnum):
    CLICK_ID = "click_id"  # gclid / fbclid / ttclid matched
    UTM = "utm"  # utm_* parameters matched to a campaign / ad
    MANUAL = "manual"
    NONE = "none"


class CreativeType(enum.StrEnum):
    VIDEO = "video"
    IMAGE = "image"


class CreativeStatus(enum.StrEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"
    APPROVED = "approved"
    LAUNCHED = "launched"
    ARCHIVED = "archived"


class GenerationStatus(enum.StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ApprovalStatus(enum.StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"
    FAILED = "failed"


class ActionStatus(enum.StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"  # stopped by a guardrail / read-only / kill switch
    PENDING_APPROVAL = "pending_approval"
    DRY_RUN = "dry_run"


class JobRunStatus(enum.StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
