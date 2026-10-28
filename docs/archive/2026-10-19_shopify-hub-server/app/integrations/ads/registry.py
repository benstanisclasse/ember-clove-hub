"""Build platform clients by name."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.integrations.ads.base import AdPlatform
from app.integrations.http import NotConfiguredError
from app.models import Platform


def is_configured(platform: Platform, settings: Settings | None = None) -> bool:
    s = settings or get_settings()
    return {
        Platform.GOOGLE: s.google_ads_configured,
        Platform.META: s.meta_configured,
        Platform.TIKTOK: s.tiktok_configured,
    }[platform]


def get_platform(platform: Platform | str) -> AdPlatform:
    """A ready client for ``platform``; raises NotConfiguredError if keys are missing."""
    p = Platform(platform)
    if p == Platform.GOOGLE:
        from app.integrations.ads.google import GoogleAds
        from app.queue import get_redis

        return GoogleAds(redis=get_redis())
    if p == Platform.META:
        from app.integrations.ads.meta import MetaAds

        return MetaAds()
    if p == Platform.TIKTOK:
        from app.integrations.ads.tiktok import TikTokAds

        return TikTokAds()
    raise NotConfiguredError(f"unknown platform {platform}")  # pragma: no cover


def configured_platforms() -> list[Platform]:
    return [p for p in Platform if is_configured(p)]
