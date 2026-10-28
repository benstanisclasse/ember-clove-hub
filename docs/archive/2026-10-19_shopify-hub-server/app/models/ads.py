"""Ad platform hierarchy (account > campaign > ad set > ad) and daily metrics.

Google's "ad group" and TikTok's "ad group" map to ``ad_sets``. Every row carries
its ``platform`` and the platform's ``external_id``; ``(platform, external_id)`` is
unique, which is what the hourly sync upserts on.

Spend and platform revenue are in the ad account's ``currency``. The hub assumes ad
accounts bill in the store currency; FX conversion is out of scope until needed.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    BigIntPK,
    EntityStatus,
    Money,
    Platform,
    TimestampMixin,
    str_enum,
)


class AdAccount(TimestampMixin, Base):
    __tablename__ = "ad_accounts"
    __table_args__ = (UniqueConstraint("platform", "external_id"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    platform: Mapped[Platform] = mapped_column(str_enum(Platform, "platform"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    currency: Mapped[str | None] = mapped_column(String(3))
    timezone: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[EntityStatus] = mapped_column(
        str_enum(EntityStatus, "entity_status"), default=EntityStatus.UNKNOWN, nullable=False
    )

    campaigns: Mapped[list[Campaign]] = relationship(back_populates="ad_account")


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"
    __table_args__ = (UniqueConstraint("platform", "external_id"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    ad_account_id: Mapped[int] = mapped_column(
        ForeignKey("ad_accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    platform: Mapped[Platform] = mapped_column(str_enum(Platform, "platform"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[EntityStatus] = mapped_column(
        str_enum(EntityStatus, "entity_status"), default=EntityStatus.UNKNOWN, nullable=False
    )
    objective: Mapped[str | None] = mapped_column(String(64))
    daily_budget: Mapped[Decimal | None] = mapped_column(Money)
    lifetime_budget: Mapped[Decimal | None] = mapped_column(Money)

    ad_account: Mapped[AdAccount] = relationship(back_populates="campaigns")
    ad_sets: Mapped[list[AdSet]] = relationship(back_populates="campaign")


class AdSet(TimestampMixin, Base):
    __tablename__ = "ad_sets"
    __table_args__ = (UniqueConstraint("platform", "external_id"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), index=True, nullable=False
    )
    platform: Mapped[Platform] = mapped_column(str_enum(Platform, "platform"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[EntityStatus] = mapped_column(
        str_enum(EntityStatus, "entity_status"), default=EntityStatus.UNKNOWN, nullable=False
    )
    daily_budget: Mapped[Decimal | None] = mapped_column(Money)
    lifetime_budget: Mapped[Decimal | None] = mapped_column(Money)
    optimization_goal: Mapped[str | None] = mapped_column(String(64))

    campaign: Mapped[Campaign] = relationship(back_populates="ad_sets")
    ads: Mapped[list[Ad]] = relationship(back_populates="ad_set")


class Ad(TimestampMixin, Base):
    __tablename__ = "ads"
    __table_args__ = (UniqueConstraint("platform", "external_id"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    ad_set_id: Mapped[int] = mapped_column(
        ForeignKey("ad_sets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    platform: Mapped[Platform] = mapped_column(str_enum(Platform, "platform"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[EntityStatus] = mapped_column(
        str_enum(EntityStatus, "entity_status"), default=EntityStatus.UNKNOWN, nullable=False
    )

    ad_set: Mapped[AdSet] = relationship(back_populates="ads")


class AdMetricsDaily(Base):
    """One row per ad per day (in the ad account's timezone). Upserted by the sync."""

    __tablename__ = "ad_metrics_daily"
    __table_args__ = (UniqueConstraint("ad_id", "date"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    ad_id: Mapped[int] = mapped_column(
        ForeignKey("ads.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    spend: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    impressions: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    clicks: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    video_3s_views: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    add_to_cart: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    purchases: Mapped[int] = mapped_column(
        BigInteger, default=0, nullable=False, comment="Platform-reported; diagnostics only"
    )
    platform_revenue: Mapped[Decimal] = mapped_column(
        Money, default=Decimal("0"), nullable=False, comment="Platform-reported; diagnostics only"
    )
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
