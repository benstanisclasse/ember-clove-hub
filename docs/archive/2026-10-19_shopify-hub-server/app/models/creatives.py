"""Generated creatives, their ML traits, links to live ads, and Higgsfield jobs."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    BigIntPK,
    CreativeStatus,
    CreativeType,
    GenerationStatus,
    JSONType,
    Platform,
    TimestampMixin,
    UsdCost,
    str_enum,
)


class Creative(TimestampMixin, Base):
    """A video or image asset. Variants point at their source via ``parent_creative_id``."""

    __tablename__ = "creatives"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    type: Mapped[CreativeType] = mapped_column(
        str_enum(CreativeType, "creative_type"), nullable=False
    )
    status: Mapped[CreativeStatus] = mapped_column(
        str_enum(CreativeStatus, "creative_status"), default=CreativeStatus.DRAFT, nullable=False
    )
    storage_key: Mapped[str | None] = mapped_column(String(1024), comment="Object key in bucket")
    storage_url: Mapped[str | None] = mapped_column(Text)
    mime_type: Mapped[str | None] = mapped_column(String(64))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    higgsfield_model: Mapped[str | None] = mapped_column(String(128))
    prompt: Mapped[str | None] = mapped_column(Text)
    brief: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    duration_seconds: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    cost_usd: Mapped[Decimal] = mapped_column(UsdCost, default=Decimal("0"), nullable=False)
    parent_creative_id: Mapped[int | None] = mapped_column(
        ForeignKey("creatives.id", ondelete="SET NULL"), index=True
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True
    )

    traits: Mapped[CreativeTrait | None] = relationship(
        back_populates="creative", uselist=False, cascade="all, delete-orphan"
    )
    parent: Mapped[Creative | None] = relationship(remote_side="Creative.id")


class CreativeTrait(Base):
    """Categorical features of a creative -- the ML feature table.

    Values are free-form strings on purpose (vocabularies will evolve); the creative
    brief schema in Phase 4 constrains what gets written here.
    """

    __tablename__ = "creative_traits"

    creative_id: Mapped[int] = mapped_column(
        ForeignKey("creatives.id", ondelete="CASCADE"), primary_key=True
    )
    hook_type: Mapped[str | None] = mapped_column(String(64), comment="e.g. problem, question")
    avatar_type: Mapped[str | None] = mapped_column(String(64), comment="e.g. woman_25_34")
    length_bucket: Mapped[str | None] = mapped_column(String(16), comment="e.g. 0-8s, static")
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    voiceover: Mapped[bool | None] = mapped_column(Boolean)
    format: Mapped[str | None] = mapped_column(String(64), comment="e.g. 9x16_ugc_selfie")
    angle: Mapped[str | None] = mapped_column(String(128), comment="e.g. saves_time")
    cta: Mapped[str | None] = mapped_column(String(64), comment="e.g. shop_now")
    extra: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)

    creative: Mapped[Creative] = relationship(back_populates="traits")


class CreativeAdLink(Base):
    """Which platform ad(s) a creative runs in. An ad linked to N creatives splits its
    spend and profit equally across them in ``v_creative_daily_profit``."""

    __tablename__ = "creative_ad_links"
    __table_args__ = (UniqueConstraint("creative_id", "ad_id"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    creative_id: Mapped[int] = mapped_column(
        ForeignKey("creatives.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ad_id: Mapped[int] = mapped_column(
        ForeignKey("ads.id", ondelete="CASCADE"), index=True, nullable=False
    )
    platform: Mapped[Platform] = mapped_column(str_enum(Platform, "platform"), nullable=False)
    external_ad_id: Mapped[str] = mapped_column(String(64), nullable=False)
    platform_asset_id: Mapped[str | None] = mapped_column(
        String(128), comment="Uploaded video/image id on the platform (YouTube id for Google)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class GenerationJob(TimestampMixin, Base):
    """One async Higgsfield generation request."""

    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    creative_id: Mapped[int | None] = mapped_column(
        ForeignKey("creatives.id", ondelete="SET NULL"), index=True
    )
    higgsfield_job_id: Mapped[str | None] = mapped_column(String(128), unique=True)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[CreativeType] = mapped_column(
        str_enum(CreativeType, "creative_type"), nullable=False
    )
    status: Mapped[GenerationStatus] = mapped_column(
        str_enum(GenerationStatus, "generation_status"),
        default=GenerationStatus.QUEUED,
        nullable=False,
        index=True,
    )
    request: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    cost_usd: Mapped[Decimal] = mapped_column(UsdCost, default=Decimal("0"), nullable=False)
    retries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CreativeMetric(Base):
    """Nightly per-creative performance snapshot for a window (7 / 30 days, or 0 = lifetime)."""

    __tablename__ = "creative_metrics"
    __table_args__ = (UniqueConstraint("creative_id", "as_of", "window_days"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    creative_id: Mapped[int] = mapped_column(
        ForeignKey("creatives.id", ondelete="CASCADE"), index=True, nullable=False
    )
    as_of: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    window_days: Mapped[int] = mapped_column(Integer, nullable=False, comment="0 = lifetime")
    spend: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False)
    video_3s_views: Mapped[int] = mapped_column(Integer, nullable=False)
    orders: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    contribution_profit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    hook_rate: Mapped[float | None] = mapped_column(Float, comment="3s views / impressions")
    ctr: Mapped[float | None] = mapped_column(Float, comment="clicks / impressions")
    cpa: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    profit_per_1000: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    enough_data: Mapped[bool] = mapped_column(Boolean, nullable=False)
    verdict: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="learning | winner | loser | neutral"
    )
