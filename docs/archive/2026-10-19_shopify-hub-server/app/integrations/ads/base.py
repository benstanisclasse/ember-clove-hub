"""The common ad-platform interface.

Each platform implements the ``_``-prefixed methods. The public write methods wrap them
in :func:`app.actions.write_action`, so no platform write can bypass read-only mode, the
kill switch or the audit log -- whoever calls it (MCP tool, approval executor, CLI).

Money crosses this interface in **major units** of the ad account currency
(``Decimal("25.00")``); each client converts to the platform's own unit (Google micros,
Meta cents, TikTok major units).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Literal

from app import guardrails
from app.actions import ActionContext, SessionFactory, write_action
from app.db import session_scope
from app.models import EntityStatus, Platform

Level = Literal["campaign", "ad_set", "ad"]


@dataclass
class AccountInfo:
    external_id: str
    name: str | None
    currency: str | None
    timezone: str | None
    status: EntityStatus = EntityStatus.ACTIVE


@dataclass
class CampaignInfo:
    external_id: str
    name: str | None
    status: EntityStatus
    objective: str | None = None
    daily_budget: Decimal | None = None
    lifetime_budget: Decimal | None = None


@dataclass
class AdSetInfo:
    external_id: str
    campaign_external_id: str
    name: str | None
    status: EntityStatus
    daily_budget: Decimal | None = None
    lifetime_budget: Decimal | None = None
    optimization_goal: str | None = None


@dataclass
class AdInfo:
    external_id: str
    ad_set_external_id: str
    name: str | None
    status: EntityStatus


@dataclass
class Structure:
    account: AccountInfo
    campaigns: list[CampaignInfo] = field(default_factory=list)
    ad_sets: list[AdSetInfo] = field(default_factory=list)
    ads: list[AdInfo] = field(default_factory=list)


@dataclass
class DailyMetric:
    ad_external_id: str
    date: date
    spend: Decimal = Decimal("0")
    impressions: int = 0
    clicks: int = 0
    video_3s_views: int = 0
    add_to_cart: int = 0
    purchases: int = 0
    platform_revenue: Decimal = Decimal("0")


@dataclass
class CampaignSpec:
    """A new campaign plus its first ad set, created PAUSED."""

    name: str
    daily_budget: Decimal
    countries: list[str] = field(default_factory=lambda: ["US"])
    objective: str | None = None  # platform default (sales / conversions) when None
    age_min: int | None = None
    age_max: int | None = None


@dataclass
class CreatedCampaign:
    campaign_id: str
    ad_set_id: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdSpec:
    """A new ad in an existing ad set, created PAUSED."""

    ad_set_id: str
    name: str
    landing_url: str
    primary_text: str
    headline: str | None = None
    call_to_action: str = "SHOP_NOW"
    video_asset_id: str | None = None  # from upload_video
    image_asset_id: str | None = None  # from upload_image (or video thumbnail)


@dataclass
class MediaUpload:
    """A creative file to push to a platform."""

    filename: str
    content: bytes
    mime_type: str
    title: str | None = None


class AdPlatform(abc.ABC):
    """One ad account on one platform."""

    platform: Platform
    account_external_id: str  # the ad account id on the platform (set by each client)

    def __init__(self, session_factory: SessionFactory = session_scope) -> None:
        self._session_factory = session_factory

    # --- reads (no gate) ----------------------------------------------------------------

    @abc.abstractmethod
    def get_account(self) -> AccountInfo: ...

    @abc.abstractmethod
    def list_structure(self) -> Structure:
        """Every non-deleted campaign, ad set and ad in the account."""

    def list_campaigns(self) -> list[CampaignInfo]:
        return self.list_structure().campaigns

    @abc.abstractmethod
    def get_daily_metrics(self, start: date, end: date) -> list[DailyMetric]:
        """Per-ad, per-day metrics for ``start..end`` inclusive (account timezone)."""

    # --- writes (always gated + audited) ------------------------------------------------

    def _gate(
        self,
        action: str,
        target_type: str,
        target_id: str | None,
        payload: dict[str, Any],
        ctx: ActionContext | None,
    ) -> Any:
        return write_action(
            f"{self.platform.value}.{action}",
            target_type=target_type,
            target_id=target_id,
            payload=payload,
            ctx=ctx,
            session_factory=self._session_factory,
        )

    def create_campaign(
        self, spec: CampaignSpec, ctx: ActionContext | None = None
    ) -> CreatedCampaign:
        payload = {
            "name": spec.name,
            "daily_budget": str(spec.daily_budget),
            "countries": spec.countries,
        }
        with self._gate("create_campaign", "campaign", None, payload, ctx) as res:
            created = self._create_campaign(spec)
            res.data = {"campaign_id": created.campaign_id, "ad_set_id": created.ad_set_id}
            return created

    def create_ad(self, spec: AdSpec, ctx: ActionContext | None = None) -> str:
        payload = {
            "ad_set_id": spec.ad_set_id,
            "name": spec.name,
            "landing_url": spec.landing_url,
            "video_asset_id": spec.video_asset_id,
            "image_asset_id": spec.image_asset_id,
        }
        with self._gate("create_ad", "ad", None, payload, ctx) as res:
            with self._session_factory() as db:
                guardrails.enforce_new_ads(db, 1)
            ad_id = self._create_ad(spec)
            res.data = {"ad_id": ad_id}
            return ad_id

    def upload_video(self, media: MediaUpload, ctx: ActionContext | None = None) -> str:
        payload = {"filename": media.filename, "bytes": len(media.content)}
        with self._gate("upload_video", "asset", None, payload, ctx) as res:
            asset_id = self._upload_video(media)
            res.data = {"asset_id": asset_id}
            return asset_id

    def upload_image(self, media: MediaUpload, ctx: ActionContext | None = None) -> str:
        payload = {"filename": media.filename, "bytes": len(media.content)}
        with self._gate("upload_image", "asset", None, payload, ctx) as res:
            asset_id = self._upload_image(media)
            res.data = {"asset_id": asset_id}
            return asset_id

    def update_budget(
        self,
        level: Level,
        external_id: str,
        daily_budget: Decimal,
        ctx: ActionContext | None = None,
    ) -> None:
        payload = {
            "level": level,
            "daily_budget": str(daily_budget),
            "previous_daily_budget": self._current_budget(level, external_id),
        }
        with self._gate("update_budget", level, external_id, payload, ctx):
            with self._session_factory() as db:
                guardrails.enforce_budget(db, self.platform.value, level, external_id, daily_budget)
            self._update_budget(level, external_id, daily_budget)

    def set_status(
        self, level: Level, external_id: str, status: EntityStatus, ctx: ActionContext | None = None
    ) -> None:
        if status not in (EntityStatus.ACTIVE, EntityStatus.PAUSED):
            raise ValueError("set_status supports ACTIVE or PAUSED only")
        with self._gate(
            "set_status", level, external_id, {"level": level, "status": status.value}, ctx
        ):
            if status == EntityStatus.ACTIVE:  # pausing is always allowed
                with self._session_factory() as db:
                    guardrails.enforce_activation(db, self.platform.value, level, external_id)
            self._set_status(level, external_id, status)

    def _current_budget(self, level: str, external_id: str) -> str | None:
        """The synced budget before a change (recorded so daily % limits are cumulative)."""
        try:
            with self._session_factory() as db:
                row = guardrails._entity(db, self.platform.value, level, external_id)
                return str(row.daily_budget) if row.daily_budget is not None else None
        except Exception:
            return None

    # --- platform implementations -------------------------------------------------------

    @abc.abstractmethod
    def _create_campaign(self, spec: CampaignSpec) -> CreatedCampaign: ...

    @abc.abstractmethod
    def _create_ad(self, spec: AdSpec) -> str: ...

    @abc.abstractmethod
    def _upload_video(self, media: MediaUpload) -> str: ...

    @abc.abstractmethod
    def _upload_image(self, media: MediaUpload) -> str: ...

    @abc.abstractmethod
    def _update_budget(self, level: Level, external_id: str, daily_budget: Decimal) -> None: ...

    @abc.abstractmethod
    def _set_status(self, level: Level, external_id: str, status: EntityStatus) -> None: ...


def as_int(value: Any) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def as_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value)) if value not in (None, "", "-") else Decimal("0")
    except ArithmeticError:
        return Decimal("0")
