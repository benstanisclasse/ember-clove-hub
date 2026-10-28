"""Process configuration loaded from environment variables.

Only infrastructure config lives here. Business rules that should be changeable at
runtime (spend caps, read-only mode, kill switch, auto-approve rules) live in the
``settings`` database table -- see :mod:`app.business_settings`.

Every secret is a :class:`pydantic.SecretStr`, so it never shows up in ``repr()``,
tracebacks or log lines unless code explicitly calls ``get_secret_value()``.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import Field, SecretStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed view over the process environment. See ``.env.example`` for documentation."""

    # HUB_ENV_FILE="" disables .env loading (tests); containers get env from compose anyway.
    model_config = SettingsConfigDict(
        env_file=os.environ.get("HUB_ENV_FILE", ".env") or None,
        extra="ignore",
        case_sensitive=False,
    )

    # --- App -------------------------------------------------------------------------
    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    log_json: bool = True
    public_base_url: str = "http://localhost:8081"

    # --- Store -----------------------------------------------------------------------
    store_timezone: str = "UTC"
    store_currency: str = "USD"
    store_niche: str = ""

    # --- Infra -----------------------------------------------------------------------
    database_url: str = "postgresql+psycopg://hub:hub@postgres:5432/hub"
    redis_url: str = "redis://redis:6379/0"

    # --- Object storage (Garage by default; any S3-compatible store works) -----------
    storage_provider: Literal["garage", "r2", "s3"] = "garage"
    s3_endpoint_url: str = "http://garage:3900"
    s3_region: str = "garage"
    s3_bucket: str = "hub-creatives"
    s3_access_key_id: SecretStr = SecretStr("")
    s3_secret_access_key: SecretStr = SecretStr("")
    s3_public_base_url: str = ""
    s3_presign_ttl_seconds: int = Field(default=3600, ge=60, le=7 * 24 * 3600)

    # --- Auth for internal admin routes ---------------------------------------------
    admin_token: SecretStr = SecretStr("")

    # --- Alerting --------------------------------------------------------------------
    slack_webhook_url: SecretStr = SecretStr("")
    heartbeat_url: SecretStr = SecretStr("")
    alert_cooldown_minutes: int = Field(default=60, ge=1)

    # --- Shopify (Phase 2) -------------------------------------------------------------
    # Dev Dashboard app: client credentials grant -> 24h token, refreshed automatically.
    # SHOPIFY_ADMIN_ACCESS_TOKEN is only for a pre-2026 legacy custom-app token.
    shopify_store_domain: str = ""
    shopify_client_id: str = ""
    shopify_client_secret: SecretStr = SecretStr("")
    shopify_admin_access_token: SecretStr = SecretStr("")
    shopify_api_version: str = "2026-07"
    shopify_backfill_days: int = Field(default=730, ge=1)
    # Used only when Shopify reports no transaction fees (non-Shopify-Payments gateways).
    payment_fee_fallback_pct: float = Field(default=2.9, ge=0, le=20)
    payment_fee_fallback_fixed: float = Field(default=0.30, ge=0)

    @property
    def shopify_configured(self) -> bool:
        """True when there's a store domain plus some way to get an access token."""
        has_token = bool(self.shopify_admin_access_token.get_secret_value())
        has_creds = bool(self.shopify_client_id and self.shopify_client_secret.get_secret_value())
        return bool(self.shopify_store_domain) and (has_token or has_creds)

    # --- Ad platforms (Phase 3) -------------------------------------------------------
    # API versions are pinned here; bump deliberately after reading the changelog.
    ads_metrics_lookback_days: int = Field(default=3, ge=1, le=28)  # hourly re-read window
    ads_nightly_lookback_days: int = Field(default=7, ge=1, le=28)  # catches late conversions

    google_ads_developer_token: SecretStr = SecretStr("")
    google_ads_client_id: str = ""
    google_ads_client_secret: SecretStr = SecretStr("")
    google_ads_refresh_token: SecretStr = SecretStr("")
    google_ads_login_customer_id: str = ""  # manager (MCC) id, digits only; optional
    google_ads_customer_id: str = ""  # the ad account, digits only
    google_ads_api_version: str = "v25"
    google_ads_business_name: str = ""  # shown on Demand Gen ads (max 25 chars)
    youtube_refresh_token: SecretStr = SecretStr("")  # youtube.upload scope, same OAuth client
    youtube_channel_id: str = ""

    meta_app_id: str = ""
    meta_app_secret: SecretStr = SecretStr("")
    meta_system_user_token: SecretStr = SecretStr("")
    meta_ad_account_id: str = ""  # digits, with or without "act_"
    meta_page_id: str = ""
    meta_pixel_id: str = ""
    meta_api_version: str = "v26.0"

    tiktok_app_id: str = ""
    tiktok_app_secret: SecretStr = SecretStr("")
    tiktok_access_token: SecretStr = SecretStr("")
    tiktok_advertiser_id: str = ""
    tiktok_pixel_id: str = ""
    tiktok_identity_id: str = ""  # TikTok account identity used as the ad's author (Spark Ads)
    tiktok_identity_type: str = "TT_USER"  # TT_USER or BC_AUTH_TT; custom identities are retired
    tiktok_identity_authorized_bc_id: str = ""  # Business Center id, for BC_AUTH_TT only
    tiktok_cta_portfolio_id: str = ""  # dynamic CTA portfolio; created on the first ad if empty
    tiktok_api_version: str = "v1.3"

    # --- Conversions (Phase 3b) ---------------------------------------------------------
    # On/off + PII hashing live in DB settings (conversions_enabled, conversions_hashed_pii).
    tiktok_events_access_token: SecretStr = SecretStr("")  # Events Manager > Settings > Events API
    tiktok_pixel_code: str = (
        ""  # the alphanumeric pixel code (Events API); TIKTOK_PIXEL_ID is numeric
    )
    google_ads_conversion_action: str = (
        ""  # customers/<id>/conversionActions/<id>, from create-pixels
    )
    meta_capi_test_event_code: str = (
        ""  # e.g. TEST12345: events show in Events Manager > Test events
    )
    tiktok_test_event_code: str = ""
    conversions_purchase_delay_s: int = Field(default=120, ge=0, le=3600)

    # --- Higgsfield (Phase 4) -----------------------------------------------------------
    higgsfield_api_key: SecretStr = SecretStr("")  # the key ID from console.higgsfield.ai
    higgsfield_api_secret: SecretStr = SecretStr("")
    higgsfield_base_url: str = "https://api.higgsfield.ai"
    higgsfield_image_model: str = "higgsfield-ai/soul/v2/standard"
    higgsfield_video_model: str = ""  # copy a video model id from the console (no public catalog)
    higgsfield_extra_models: str = ""  # comma-separated, shown by `higgsfield models`
    higgsfield_webhook_token: SecretStr = SecretStr("")  # generated by setup; secret URL segment
    higgsfield_job_timeout_minutes: int = Field(default=120, ge=10)
    google_ads_logo_asset: str = ""  # customers/<id>/assets/<id> (square logo for Demand Gen ads)

    # --- MCP server (Phase 5) -----------------------------------------------------------
    mcp_bearer_token: SecretStr = SecretStr("")  # static token for Claude Code (generated)
    mcp_owner_password: SecretStr = SecretStr("")  # approves new Claude connections (generated)
    mcp_access_token_minutes: int = Field(default=60, ge=5, le=1440)
    mcp_refresh_token_days: int = Field(default=30, ge=1, le=365)
    mcp_cimd_hosts: str = "claude.ai,claude.com"  # client-metadata-document hosts we trust
    store_public_url: str = (
        ""  # e.g. https://your-store.com (landing pages); defaults to the myshopify domain
    )
    approval_expiry_hours: int = Field(default=72, ge=1, le=720)

    @property
    def mcp_url(self) -> str:
        return self.public_base_url.rstrip("/") + "/mcp"

    @property
    def storefront_url(self) -> str:
        if self.store_public_url:
            return self.store_public_url.rstrip("/")
        return f"https://{self.shopify_store_domain}" if self.shopify_store_domain else ""

    @property
    def higgsfield_configured(self) -> bool:
        return bool(
            self.higgsfield_api_key.get_secret_value()
            and self.higgsfield_api_secret.get_secret_value()
        )

    @property
    def google_ads_configured(self) -> bool:
        return all(
            (
                self.google_ads_developer_token.get_secret_value(),
                self.google_ads_client_id,
                self.google_ads_client_secret.get_secret_value(),
                self.google_ads_refresh_token.get_secret_value(),
                self.google_ads_customer_id,
            )
        )

    @property
    def meta_configured(self) -> bool:
        return bool(self.meta_system_user_token.get_secret_value() and self.meta_ad_account_id)

    @property
    def tiktok_configured(self) -> bool:
        return bool(self.tiktok_access_token.get_secret_value() and self.tiktok_advertiser_id)

    @field_validator(
        "shopify_api_version",
        "google_ads_api_version",
        "meta_api_version",
        "tiktok_api_version",
        mode="before",
    )
    @classmethod
    def _blank_version_uses_pin(cls, value: object, info: ValidationInfo) -> object:
        """``FOO_API_VERSION=`` (blank line in .env) means "use the pinned default"."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return cls.model_fields[info.field_name].default  # type: ignore[index]
        return value

    @field_validator("google_ads_customer_id", "google_ads_login_customer_id")
    @classmethod
    def _digits_only(cls, value: str) -> str:
        return value.replace("-", "").strip()

    @field_validator("meta_ad_account_id")
    @classmethod
    def _no_act_prefix(cls, value: str) -> str:
        return value.strip().removeprefix("act_")

    @field_validator("shopify_store_domain")
    @classmethod
    def _bare_domain(cls, value: str) -> str:
        value = value.strip().removeprefix("https://").removeprefix("http://").rstrip("/")
        return "" if value.startswith("[") else value  # ignore the .env.example placeholder

    @field_validator("store_timezone")
    @classmethod
    def _valid_timezone(cls, value: str) -> str:
        ZoneInfo(value)  # raises ZoneInfoNotFoundError on typos
        return value

    @property
    def tz(self) -> ZoneInfo:
        """The store's timezone; order dates and daily ad metrics are bucketed in it."""
        return ZoneInfo(self.store_timezone)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings (cached; call ``get_settings.cache_clear()`` in tests)."""
    return Settings()
