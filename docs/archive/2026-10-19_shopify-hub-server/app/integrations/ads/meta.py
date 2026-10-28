"""Meta (Facebook / Instagram) Marketing API client.

Auth: a **system user** access token from Business Manager (set to never expire),
scoped to the ad account, page and pixel. Every call carries ``appsecret_proof``
(HMAC of the token with the app secret) when ``META_APP_SECRET`` is set.

Rate limits: Meta answers HTTP 400 with error codes 4 / 17 / 32 / 613 / 80000-80014
when an app, account or ads-insights bucket is exhausted; those, ``is_transient``
errors and 5xx back off and retry. Code 190 (bad / expired token) fails fast with a
clear message.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections.abc import Callable, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

import httpx

from app.actions import SessionFactory
from app.config import Settings, get_settings
from app.db import session_scope
from app.integrations.ads.base import (
    AccountInfo,
    AdInfo,
    AdPlatform,
    AdSetInfo,
    AdSpec,
    CampaignInfo,
    CampaignSpec,
    CreatedCampaign,
    DailyMetric,
    Level,
    MediaUpload,
    Structure,
    as_decimal,
    as_int,
)
from app.integrations.http import (
    RETRYABLE_STATUS,
    IntegrationError,
    NotConfiguredError,
    backoff_delay,
)
from app.log import get_logger
from app.models import EntityStatus, Platform

log = get_logger(__name__)

STATUS = {
    "ACTIVE": EntityStatus.ACTIVE,
    "PAUSED": EntityStatus.PAUSED,
    "CAMPAIGN_PAUSED": EntityStatus.PAUSED,
    "ADSET_PAUSED": EntityStatus.PAUSED,
    "PENDING_BILLING_INFO": EntityStatus.PAUSED,
    "IN_PROCESS": EntityStatus.PENDING_REVIEW,
    "PENDING_REVIEW": EntityStatus.PENDING_REVIEW,
    "PREAPPROVED": EntityStatus.PENDING_REVIEW,
    "WITH_ISSUES": EntityStatus.ACTIVE,
    "DISAPPROVED": EntityStatus.REJECTED,
    "ARCHIVED": EntityStatus.ARCHIVED,
    "DELETED": EntityStatus.DELETED,
}
ACCOUNT_STATUS = {1: EntityStatus.ACTIVE, 2: EntityStatus.PAUSED, 101: EntityStatus.DELETED}
RATE_LIMIT_CODES = {4, 17, 32, 613, *range(80000, 80015)}
AUTH_CODES = {102, 190}
# Action types, most specific first; only the first present is counted (no double count).
PURCHASE_TYPES = ("omni_purchase", "purchase", "offsite_conversion.fb_pixel_purchase")
ATC_TYPES = ("omni_add_to_cart", "add_to_cart", "offsite_conversion.fb_pixel_add_to_cart")
VIDEO_3S_TYPES = ("video_view",)  # Meta's "video_view" action = 3-second video plays
ZERO_DECIMAL = {"JPY", "KRW", "VND", "CLP", "ISK", "PYG", "UGX", "HUF", "TWD"}


class MetaAds(AdPlatform):
    platform = Platform.META

    def __init__(
        self,
        settings: Settings | None = None,
        http: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
        session_factory: SessionFactory = session_scope,
        max_attempts: int = 6,
    ) -> None:
        super().__init__(session_factory)
        self.settings = s = settings or get_settings()
        if not s.meta_configured:
            raise NotConfiguredError(
                "Meta not configured: set META_SYSTEM_USER_TOKEN and META_AD_ACCOUNT_ID"
            )
        self.http = http or httpx.Client(timeout=httpx.Timeout(60.0, connect=10.0))
        self.sleep = sleep
        self.max_attempts = max_attempts
        self.base = f"https://graph.facebook.com/{s.meta_api_version}"
        self.video_base = f"https://graph-video.facebook.com/{s.meta_api_version}"
        self.act = f"act_{s.meta_ad_account_id}"
        self.account_external_id = s.meta_ad_account_id
        self._currency: str | None = None

    # --- transport ------------------------------------------------------------------------

    def _auth_params(self) -> dict[str, str]:
        token = self.settings.meta_system_user_token.get_secret_value()
        params = {"access_token": token}
        secret = self.settings.meta_app_secret.get_secret_value()
        if secret:
            params["appsecret_proof"] = hmac.new(
                secret.encode(), token.encode(), hashlib.sha256
            ).hexdigest()
        return params

    def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        query = {**(self._auth_params() if auth else {}), **(params or {})}
        for attempt in range(self.max_attempts):
            try:
                # params=None (not {}): an empty dict makes httpx drop the URL's own query
                # string, which would strip the cursor from Meta's paging "next" URLs.
                resp = self.http.request(method, url, params=query or None, data=data, files=files)
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                if attempt == self.max_attempts - 1:
                    raise IntegrationError(f"Meta {method} {url}: {exc}", retryable=True) from exc
                self.sleep(backoff_delay(attempt))
                continue
            try:
                body = resp.json()
            except ValueError:
                body = {}
            err = body.get("error") if isinstance(body, dict) else None
            if resp.status_code < 400 and not err:
                return body  # type: ignore[no-any-return]
            code = (err or {}).get("code")
            msg = (err or {}).get("message") or resp.text[:300]
            if code in AUTH_CODES:
                raise IntegrationError(
                    f"Meta token rejected (code {code}): {msg}", status=resp.status_code
                )
            retry = (
                code in RATE_LIMIT_CODES
                or (err or {}).get("is_transient")
                or resp.status_code in RETRYABLE_STATUS
            )
            if retry and attempt < self.max_attempts - 1:
                # Rate-limit buckets refill over minutes, not seconds.
                delay = backoff_delay(
                    attempt, base=30.0 if code in RATE_LIMIT_CODES else 1.0, cap=300.0
                )
                log.warning(
                    "meta_retry", code=code, status=resp.status_code, delay_s=round(delay, 1)
                )
                self.sleep(delay)
                continue
            raise IntegrationError(
                f"Meta {method} {url.split('?')[0]} -> {resp.status_code} code={code} "
                f"subcode={(err or {}).get('error_subcode')}: {msg}",
                status=resp.status_code,
                retryable=bool(retry),
            )
        raise IntegrationError("Meta: retries exhausted", retryable=True)  # pragma: no cover

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        return self._request("GET", f"{self.base}/{path}", params=params)

    def _post(
        self,
        path: str,
        data: dict[str, Any],
        files: dict[str, Any] | None = None,
        video: bool = False,
    ) -> dict[str, Any]:
        base = self.video_base if video else self.base
        encoded = {k: json.dumps(v) if isinstance(v, dict | list) else v for k, v in data.items()}
        return self._request("POST", f"{base}/{path}", data=encoded, files=files)

    def _paged(self, path: str, **params: Any) -> Iterator[dict[str, Any]]:
        body = self._get(path, limit=500, **params)
        while True:
            yield from body.get("data") or []
            nxt = (body.get("paging") or {}).get("next")
            if not nxt:
                return
            body = self._request("GET", nxt, auth=False)  # next URL already carries auth

    # --- money ----------------------------------------------------------------------------

    def _minor(self, amount: Decimal) -> int:
        return (
            int(amount)
            if self.currency in ZERO_DECIMAL
            else int((amount * 100).to_integral_value())
        )

    def _major(self, minor: Any) -> Decimal | None:
        if minor in (None, "", "0", 0):
            return None
        value = Decimal(str(minor))
        return value if self.currency in ZERO_DECIMAL else value / 100

    @property
    def currency(self) -> str:
        if self._currency is None:
            self._currency = self.get_account().currency or "USD"
        return self._currency

    # --- reads ----------------------------------------------------------------------------

    def get_account(self) -> AccountInfo:
        a = self._get(self.act, fields="id,name,currency,timezone_name,account_status")
        self._currency = a.get("currency")
        return AccountInfo(
            external_id=self.settings.meta_ad_account_id,
            name=a.get("name"),
            currency=a.get("currency"),
            timezone=a.get("timezone_name"),
            status=ACCOUNT_STATUS.get(a.get("account_status"), EntityStatus.UNKNOWN),
        )

    @staticmethod
    def _status(node: dict[str, Any]) -> EntityStatus:
        return STATUS.get(
            node.get("effective_status") or node.get("status") or "", EntityStatus.UNKNOWN
        )

    def list_structure(self) -> Structure:
        account = self.get_account()
        campaigns = [
            CampaignInfo(
                external_id=c["id"],
                name=c.get("name"),
                status=self._status(c),
                objective=c.get("objective"),
                daily_budget=self._major(c.get("daily_budget")),
                lifetime_budget=self._major(c.get("lifetime_budget")),
            )
            for c in self._paged(
                f"{self.act}/campaigns",
                fields="id,name,status,effective_status,objective,daily_budget,lifetime_budget",
            )
        ]
        ad_sets = [
            AdSetInfo(
                external_id=a["id"],
                campaign_external_id=a["campaign_id"],
                name=a.get("name"),
                status=self._status(a),
                daily_budget=self._major(a.get("daily_budget")),
                lifetime_budget=self._major(a.get("lifetime_budget")),
                optimization_goal=a.get("optimization_goal"),
            )
            for a in self._paged(
                f"{self.act}/adsets",
                fields="id,name,campaign_id,status,effective_status,daily_budget,lifetime_budget,optimization_goal",
            )
        ]
        ads = [
            AdInfo(
                external_id=a["id"],
                ad_set_external_id=a["adset_id"],
                name=a.get("name"),
                status=self._status(a),
            )
            for a in self._paged(
                f"{self.act}/ads", fields="id,name,adset_id,status,effective_status"
            )
        ]
        return Structure(account, campaigns, ad_sets, ads)

    @staticmethod
    def _action(rows: list[dict[str, Any]] | None, types: tuple[str, ...]) -> Decimal:
        values = {r.get("action_type"): r.get("value") for r in rows or []}
        for t in types:
            if t in values:
                return as_decimal(values[t])
        return Decimal("0")

    def get_daily_metrics(self, start: date, end: date) -> list[DailyMetric]:
        rows = self._paged(
            f"{self.act}/insights",
            level="ad",
            time_increment=1,
            time_range=json.dumps({"since": start.isoformat(), "until": end.isoformat()}),
            fields="ad_id,date_start,spend,impressions,inline_link_clicks,actions,action_values",
        )
        out = []
        for r in rows:
            out.append(
                DailyMetric(
                    ad_external_id=r["ad_id"],
                    date=date.fromisoformat(r["date_start"]),
                    spend=as_decimal(r.get("spend")),
                    impressions=as_int(r.get("impressions")),
                    clicks=as_int(r.get("inline_link_clicks")),
                    video_3s_views=int(self._action(r.get("actions"), VIDEO_3S_TYPES)),
                    add_to_cart=int(self._action(r.get("actions"), ATC_TYPES)),
                    purchases=int(self._action(r.get("actions"), PURCHASE_TYPES)),
                    platform_revenue=self._action(r.get("action_values"), PURCHASE_TYPES),
                )
            )
        return out

    # --- writes (called only through the gated public methods) ----------------------------

    def _create_campaign(self, spec: CampaignSpec) -> CreatedCampaign:
        pixel = self.settings.meta_pixel_id
        if not pixel:
            raise ValueError("META_PIXEL_ID is required to create a sales campaign")
        campaign = self._post(
            f"{self.act}/campaigns",
            {
                "name": spec.name,
                "objective": spec.objective or "OUTCOME_SALES",
                "status": "PAUSED",
                "buying_type": "AUCTION",
                "special_ad_categories": [],
                # Advantage campaign budget: the budget lives on the campaign.
                "daily_budget": self._minor(spec.daily_budget),
                "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            },
        )
        targeting: dict[str, Any] = {"geo_locations": {"countries": spec.countries}}
        if spec.age_min:
            targeting["age_min"] = spec.age_min
        if spec.age_max:
            targeting["age_max"] = spec.age_max
        ad_set = self._post(
            f"{self.act}/adsets",
            {
                "name": f"{spec.name} - ad set",
                "campaign_id": campaign["id"],
                "billing_event": "IMPRESSIONS",
                "optimization_goal": "OFFSITE_CONVERSIONS",
                "promoted_object": {"pixel_id": pixel, "custom_event_type": "PURCHASE"},
                "targeting": targeting,
                "status": "PAUSED",
            },
        )
        return CreatedCampaign(campaign_id=campaign["id"], ad_set_id=ad_set["id"])

    def _upload_video(self, media: MediaUpload) -> str:
        body = self._post(
            f"{self.act}/advideos",
            {"name": media.title or media.filename},
            files={"source": (media.filename, media.content, media.mime_type)},
            video=True,
        )
        return str(body["id"])

    def _upload_image(self, media: MediaUpload) -> str:
        body = self._post(
            f"{self.act}/adimages",
            {},
            files={"filename": (media.filename, media.content, media.mime_type)},
        )
        images = body.get("images") or {}
        first = next(iter(images.values()), {})
        if not first.get("hash"):
            raise IntegrationError(f"Meta image upload returned no hash: {body}")
        return str(first["hash"])

    def _create_ad(self, spec: AdSpec) -> str:
        page = self.settings.meta_page_id
        if not page:
            raise ValueError("META_PAGE_ID is required to create ads")
        cta = {"type": spec.call_to_action, "value": {"link": spec.landing_url}}
        if spec.video_asset_id:
            if not spec.image_asset_id:
                raise ValueError(
                    "Meta video ads need a thumbnail: upload an image and pass image_asset_id"
                )
            story = {
                "page_id": page,
                "video_data": {
                    "video_id": spec.video_asset_id,
                    "image_hash": spec.image_asset_id,
                    "message": spec.primary_text,
                    "title": spec.headline or "",
                    "call_to_action": cta,
                },
            }
        elif spec.image_asset_id:
            story = {
                "page_id": page,
                "link_data": {
                    "image_hash": spec.image_asset_id,
                    "link": spec.landing_url,
                    "message": spec.primary_text,
                    "name": spec.headline or "",
                    "call_to_action": cta,
                },
            }
        else:
            raise ValueError("an ad needs a video_asset_id or image_asset_id")
        creative = self._post(
            f"{self.act}/adcreatives",
            {"name": f"{spec.name} - creative", "object_story_spec": story},
        )
        ad = self._post(
            f"{self.act}/ads",
            {
                "name": spec.name,
                "adset_id": spec.ad_set_id,
                "creative": {"creative_id": creative["id"]},
                "status": "PAUSED",
            },
        )
        return str(ad["id"])

    def _update_budget(self, level: Level, external_id: str, daily_budget: Decimal) -> None:
        if level == "ad":
            raise ValueError(
                "Meta budgets live on campaigns (Advantage budget) or ad sets, not ads"
            )
        self._post(external_id, {"daily_budget": self._minor(daily_budget)})

    def _set_status(self, level: Level, external_id: str, status: EntityStatus) -> None:
        self._post(external_id, {"status": "ACTIVE" if status == EntityStatus.ACTIVE else "PAUSED"})
