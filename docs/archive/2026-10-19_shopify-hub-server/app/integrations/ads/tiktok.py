"""TikTok API for Business (Marketing API) client.

Auth: an advertiser access token from the OAuth authorization flow of your TikTok for
Business developer app (long-lived until revoked), sent as ``Access-Token``.

Every response is ``{"code": 0, "message": "OK", "data": ...}`` -- HTTP 200 even for
errors, so the client checks ``code``: 40100 (rate limited) and 5xxxx back off and retry;
401xx token errors fail fast.

Creation uses the **Upgraded Smart+** endpoints (``smart_plus/...``): from 2027-01-01 the
legacy ``campaign/create``, ``adgroup/create`` and ``ad/create`` stop creating non-Search
Sales, App Promotion and Lead Generation campaigns. The hub creates Smart+ *Web* (Sales)
campaigns with CBO off, so each ad group keeps its own (dynamic daily) budget.

Reads use the legacy getters, which also return Smart+ campaigns and ad groups. Ads are
identified by ``ad_id_v2`` (a manual ad id, or a Smart+ ad id) because the legacy ``ad_id``
of a Smart+ ad is one *creative* inside it. Budget/status writes look up whether the target
is a Smart+ entity and pick the matching ``smart_plus/...`` or legacy endpoint.

Metric caveats (documented, not hidden):
* TikTok has no 3-second view metric; ``video_watched_2s`` is stored in
  ``video_3s_views``. Compare hook rates *within* a platform, not across.
* Platform revenue = ``complete_payment_roas * spend`` (diagnostics only; Shopify orders
  are the source of truth).
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime, timedelta
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

RATE_LIMIT_CODES = {40100, 40133}
AUTH_CODES = {40001, 40102, 40104, 40105}
METRICS = [
    "spend",
    "impressions",
    "clicks",
    "video_watched_2s",
    "complete_payment",
    "complete_payment_roas",
]
MAX_REPORT_DAYS = 30
# TikTok targets by location id (GeoNames ids), not ISO codes. Extend as needed.
AGE_GROUPS = (
    ("AGE_18_24", 18, 24),
    ("AGE_25_34", 25, 34),
    ("AGE_35_44", 35, 44),
    ("AGE_45_54", 45, 54),
    ("AGE_55_100", 55, 100),
)
LOCATION_IDS = {
    "US": "6252001",
    "CA": "6251999",
    "GB": "2635167",
    "AU": "2077456",
    "NZ": "2186224",
    "IE": "2963597",
}
SMART_PLUS = "UPGRADED_SMART_PLUS"
# Spark Ads identities. TikTok no longer serves non-Spark (CUSTOMIZED_USER) ads on the TikTok
# placement, and Spark Ads Push (our uploaded video + cover) takes these two types.
SPARK_IDENTITY_TYPES = ("TT_USER", "BC_AUTH_TT")
# Legacy getter + id filter used to tell a Smart+ entity from a manual one before a write.
LOOKUP = {
    "campaign": ("campaign/get/", "campaign_ids", "campaign_id"),
    "ad_set": ("adgroup/get/", "adgroup_ids", "adgroup_id"),
    "ad": ("ad/get/", "ad_ids_v2", "ad_id_v2"),
}


def _request_id() -> str:
    """Smart+ create idempotency key: a 64-bit integer as a string (same key on retries)."""
    return str(secrets.randbits(63))


def _status(node: dict[str, Any]) -> EntityStatus:
    op = (node.get("operation_status") or "").upper()
    secondary = (node.get("secondary_status") or "").upper()
    if op == "DELETE" or "DELETE" in secondary:
        return EntityStatus.DELETED
    if "NOT_APPROVED" in secondary or "REJECT" in secondary:
        return EntityStatus.REJECTED
    if "REVIEW" in secondary:
        return EntityStatus.PENDING_REVIEW
    if op == "DISABLE":
        return EntityStatus.PAUSED
    if op == "ENABLE":
        return EntityStatus.ACTIVE
    return EntityStatus.UNKNOWN


def age_groups(age_min: int | None, age_max: int | None) -> list[str]:
    """TikTok age buckets overlapping ``age_min..age_max`` (18+ only)."""
    lo, hi = max(age_min or 18, 18), age_max or 100
    return [name for name, a, b in AGE_GROUPS if a <= hi and b >= lo]


def _budgets(node: dict[str, Any]) -> tuple[Decimal | None, Decimal | None]:
    mode, budget = node.get("budget_mode"), as_decimal(node.get("budget"))
    if mode == "BUDGET_MODE_DAY" or mode == "BUDGET_MODE_DYNAMIC_DAILY_BUDGET":
        return budget or None, None
    if mode == "BUDGET_MODE_TOTAL":
        return None, budget or None
    return None, None


class TikTokAds(AdPlatform):
    platform = Platform.TIKTOK

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
        if not s.tiktok_configured:
            raise NotConfiguredError(
                "TikTok not configured: set TIKTOK_ACCESS_TOKEN and TIKTOK_ADVERTISER_ID"
            )
        self.http = http or httpx.Client(timeout=httpx.Timeout(60.0, connect=10.0))
        self.sleep = sleep
        self.max_attempts = max_attempts
        self.base = f"https://business-api.tiktok.com/open_api/{s.tiktok_api_version}"
        self.advertiser_id = s.tiktok_advertiser_id
        self.account_external_id = s.tiktok_advertiser_id
        self._cta_portfolio_id = s.tiktok_cta_portfolio_id

    # --- transport ------------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        headers = {"Access-Token": self.settings.tiktok_access_token.get_secret_value()}
        # GET params that are lists/dicts must be JSON-encoded strings.
        query = {
            k: json.dumps(v) if isinstance(v, list | dict) else v for k, v in (params or {}).items()
        }
        url = f"{self.base}/{path}"
        for attempt in range(self.max_attempts):
            try:
                resp = self.http.request(
                    method,
                    url,
                    params=query,
                    json=json_body,
                    data=data,
                    files=files,
                    headers=headers,
                )
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                if attempt == self.max_attempts - 1:
                    raise IntegrationError(f"TikTok {path}: {exc}", retryable=True) from exc
                self.sleep(backoff_delay(attempt))
                continue
            try:
                body = resp.json()
            except ValueError:
                body = {"code": resp.status_code, "message": resp.text[:300]}
            code = body.get("code")
            if code == 0 and resp.status_code < 400:
                return body.get("data")
            msg = body.get("message")
            if code in AUTH_CODES:
                raise IntegrationError(
                    f"TikTok token rejected (code {code}): {msg}", status=resp.status_code
                )
            retry = (
                code in RATE_LIMIT_CODES
                or (isinstance(code, int) and code >= 50000)
                or resp.status_code in RETRYABLE_STATUS
            )
            if retry and attempt < self.max_attempts - 1:
                delay = backoff_delay(attempt, base=2.0 if code in RATE_LIMIT_CODES else 1.0)
                log.warning("tiktok_retry", code=code, delay_s=round(delay, 1))
                self.sleep(delay)
                continue
            raise IntegrationError(
                f"TikTok {path} code={code}: {msg} (request_id={body.get('request_id')})",
                status=resp.status_code,
                retryable=bool(retry),
            )
        raise IntegrationError("TikTok: retries exhausted", retryable=True)  # pragma: no cover

    def _paged(self, path: str, **params: Any) -> Iterator[dict[str, Any]]:
        page = 1
        while True:
            data = (
                self._request(
                    "GET",
                    path,
                    params={
                        "advertiser_id": self.advertiser_id,
                        "page": page,
                        "page_size": 1000,
                        **params,
                    },
                )
                or {}
            )
            yield from data.get("list") or []
            total = (data.get("page_info") or {}).get("total_page") or 1
            if page >= total:
                return
            page += 1

    # --- reads ----------------------------------------------------------------------------

    def get_account(self) -> AccountInfo:
        data = (
            self._request(
                "GET",
                "advertiser/info/",
                params={
                    "advertiser_ids": [self.advertiser_id],
                    "fields": ["advertiser_id", "name", "currency", "timezone", "status"],
                },
            )
            or {}
        )
        info = (data.get("list") or [{}])[0]
        return AccountInfo(
            external_id=self.advertiser_id,
            name=info.get("name"),
            currency=info.get("currency"),
            timezone=info.get("timezone"),
            status=EntityStatus.ACTIVE
            if info.get("status") in (None, "STATUS_ENABLE")
            else EntityStatus.PAUSED,
        )

    def list_structure(self) -> Structure:
        account = self.get_account()
        campaigns = []
        for c in self._paged(
            "campaign/get/",
            fields=[
                "campaign_id",
                "campaign_name",
                "operation_status",
                "secondary_status",
                "objective_type",
                "budget",
                "budget_mode",
            ],
        ):
            daily, lifetime = _budgets(c)
            campaigns.append(
                CampaignInfo(
                    str(c["campaign_id"]),
                    c.get("campaign_name"),
                    _status(c),
                    c.get("objective_type"),
                    daily,
                    lifetime,
                )
            )
        ad_sets = []
        for a in self._paged(
            "adgroup/get/",
            fields=[
                "adgroup_id",
                "campaign_id",
                "adgroup_name",
                "operation_status",
                "secondary_status",
                "budget",
                "budget_mode",
                "optimization_goal",
            ],
        ):
            daily, lifetime = _budgets(a)
            ad_sets.append(
                AdSetInfo(
                    str(a["adgroup_id"]),
                    str(a["campaign_id"]),
                    a.get("adgroup_name"),
                    _status(a),
                    daily,
                    lifetime,
                    a.get("optimization_goal"),
                )
            )
        # Manual ads from ad/get. It lists a Smart+ ad as one row per creative (ad_id = the
        # creative), so those rows are skipped and the ads come from smart_plus/ad/get instead,
        # keyed like the report's ad_id_v2.
        ads = [
            AdInfo(str(a["ad_id"]), str(a["adgroup_id"]), a.get("ad_name"), _status(a))
            for a in self._paged(
                "ad/get/",
                fields=[
                    "ad_id",
                    "adgroup_id",
                    "ad_name",
                    "operation_status",
                    "secondary_status",
                    "campaign_automation_type",
                ],
            )
            if not str(a.get("campaign_automation_type") or "").startswith(SMART_PLUS)
        ]
        ads += [
            AdInfo(str(a["smart_plus_ad_id"]), str(a["adgroup_id"]), a.get("ad_name"), _status(a))
            for a in self._paged(
                "smart_plus/ad/get/",
                fields=[
                    "smart_plus_ad_id",
                    "adgroup_id",
                    "ad_name",
                    "operation_status",
                    "secondary_status",
                ],
            )
        ]
        return Structure(account, campaigns, ad_sets, ads)

    def get_daily_metrics(self, start: date, end: date) -> list[DailyMetric]:
        out: list[DailyMetric] = []
        chunk_start = start
        while chunk_start <= end:  # TikTok caps daily reports at 30 days per request
            chunk_end = min(end, chunk_start + timedelta(days=MAX_REPORT_DAYS - 1))
            for row in self._paged(
                "report/integrated/get/",
                report_type="BASIC",
                data_level="AUCTION_AD",
                # ad_id_v2: the manual ad id, or the Smart+ ad id (ad_id would be per creative)
                dimensions=["ad_id_v2", "stat_time_day"],
                metrics=METRICS,
                start_date=chunk_start.isoformat(),
                end_date=chunk_end.isoformat(),
            ):
                dims, m = row.get("dimensions") or {}, row.get("metrics") or {}
                spend = as_decimal(m.get("spend"))
                out.append(
                    DailyMetric(
                        ad_external_id=str(dims["ad_id_v2"]),
                        date=date.fromisoformat(str(dims["stat_time_day"])[:10]),
                        spend=spend,
                        impressions=as_int(m.get("impressions")),
                        clicks=as_int(m.get("clicks")),
                        video_3s_views=as_int(m.get("video_watched_2s")),
                        purchases=as_int(m.get("complete_payment")),
                        platform_revenue=(
                            as_decimal(m.get("complete_payment_roas")) * spend
                        ).quantize(Decimal("0.01")),
                    )
                )
            chunk_start = chunk_end + timedelta(days=1)
        return out

    # --- writes ---------------------------------------------------------------------------

    def _create_campaign(self, spec: CampaignSpec) -> CreatedCampaign:
        """An Upgraded Smart+ Web (Sales) campaign plus one ad group, both disabled."""
        objective = spec.objective or "WEB_CONVERSIONS"
        if objective != "WEB_CONVERSIONS":
            raise ValueError(
                f"TikTok campaigns are created as Upgraded Smart+ Sales (WEB_CONVERSIONS) "
                f"campaigns; objective {objective} is not supported"
            )
        pixel = self.settings.tiktok_pixel_id
        if not pixel:
            raise ValueError("TIKTOK_PIXEL_ID is required to create a conversion campaign")
        try:
            locations = [LOCATION_IDS[c.upper()] for c in spec.countries]
        except KeyError as exc:
            raise ValueError(
                f"no TikTok location id mapped for {exc.args[0]}; add it to LOCATION_IDS"
            ) from None
        campaign = self._request(
            "POST",
            "smart_plus/campaign/create/",
            json_body={
                "advertiser_id": self.advertiser_id,
                "request_id": _request_id(),
                "campaign_name": spec.name,
                "objective_type": objective,
                "sales_destination": "WEBSITE",
                "budget_optimize_on": False,  # no CBO: the budget lives on the ad group
                "operation_status": "DISABLE",
            },
        )
        start = (datetime.now(UTC) + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        targeting: dict[str, Any] = {"location_ids": locations}
        if spec.age_min or spec.age_max:  # age ranges need custom (MANUAL) targeting
            targeting["age_groups"] = age_groups(spec.age_min, spec.age_max)
        group: dict[str, Any] = {
            "advertiser_id": self.advertiser_id,
            "request_id": _request_id(),
            "campaign_id": campaign["campaign_id"],
            "adgroup_name": f"{spec.name} - ad group",
            "promotion_type": "WEBSITE",
            "pixel_id": pixel,
            "optimization_goal": "CONVERT",
            "optimization_event": "COMPLETE_PAYMENT",
            "billing_event": "OCPM",
            "bid_type": "BID_TYPE_NO_BID",
            # Smart+ ad groups have no fixed daily mode: a dynamic daily budget averages over
            # the week and may spend up to 125% of it on a single day.
            "budget_mode": "BUDGET_MODE_DYNAMIC_DAILY_BUDGET",
            "budget": float(spec.daily_budget),
            "schedule_type": "SCHEDULE_FROM_NOW",
            "schedule_start_time": start,
            "targeting_optimization_mode": "MANUAL" if "age_groups" in targeting else "AUTOMATIC",
            "targeting_spec": targeting,
            "operation_status": "DISABLE",
        }  # placement left unset = Automatic Placement
        ad_group = self._request("POST", "smart_plus/adgroup/create/", json_body=group)
        return CreatedCampaign(
            campaign_id=str(campaign["campaign_id"]), ad_set_id=str(ad_group["adgroup_id"])
        )

    def _upload_video(self, media: MediaUpload) -> str:
        data = self._request(
            "POST",
            "file/video/ad/upload/",
            data={
                "advertiser_id": self.advertiser_id,
                "upload_type": "UPLOAD_BY_FILE",
                "video_signature": hashlib.md5(media.content).hexdigest(),  # noqa: S324 - API-required checksum
                "file_name": media.title or media.filename,
            },
            files={"video_file": (media.filename, media.content, media.mime_type)},
        )
        item = data[0] if isinstance(data, list) else data
        return str(item["video_id"])

    def _upload_image(self, media: MediaUpload) -> str:
        data = self._request(
            "POST",
            "file/image/ad/upload/",
            data={
                "advertiser_id": self.advertiser_id,
                "upload_type": "UPLOAD_BY_FILE",
                "image_signature": hashlib.md5(media.content).hexdigest(),  # noqa: S324
            },
            files={"image_file": (media.filename, media.content, media.mime_type)},
        )
        return str(data["image_id"])

    def _cta_portfolio(self) -> str:
        """A dynamic CTA (CTA creative portfolio). Spark Ads in Smart+ Sales campaigns on
        Automatic Placement must use one instead of a fixed call-to-action."""
        if self._cta_portfolio_id:
            return self._cta_portfolio_id
        data = (
            self._request(
                "GET",
                "creative/cta/recommend/",
                params={
                    "advertiser_id": self.advertiser_id,
                    "new_version": True,
                    "objective_type": "WEB_CONVERSIONS",
                    "promotion_type": "WEBSITE",
                    "language": "en",
                },
            )
            or {}
        )
        content = [
            {"asset_content": a.get("asset_content"), "asset_ids": a["asset_ids"]}
            for a in data.get("recommend_assets") or []
            if a.get("asset_ids")
        ]
        if not content:
            raise IntegrationError(
                "TikTok recommended no CTAs; create a dynamic CTA portfolio in Ads Manager "
                "and set TIKTOK_CTA_PORTFOLIO_ID"
            )
        created = self._request(
            "POST",
            "creative/portfolio/create/",
            json_body={
                "advertiser_id": self.advertiser_id,
                "creative_portfolio_type": "CTA",
                "portfolio_content": content,
            },
        )
        self._cta_portfolio_id = str(created["creative_portfolio_id"])
        log.info(
            "tiktok_cta_portfolio_created",
            portfolio_id=self._cta_portfolio_id,
            hint="set TIKTOK_CTA_PORTFOLIO_ID to reuse it",
        )
        return self._cta_portfolio_id

    def _create_ad(self, spec: AdSpec) -> str:
        """An Upgraded Smart+ ad with one Spark Ads Push creative (our video + cover).

        ``spec.call_to_action`` is not used: TikTok only accepts a dynamic CTA here.
        """
        s = self.settings
        identity = s.tiktok_identity_id
        if not identity:
            raise ValueError(
                "TIKTOK_IDENTITY_ID is required (the TikTok account shown as the ad's author)"
            )
        if s.tiktok_identity_type not in SPARK_IDENTITY_TYPES:
            raise ValueError(
                f"TIKTOK_IDENTITY_TYPE={s.tiktok_identity_type} can't author ads on TikTok any "
                f"more (custom identities were retired); use a TikTok account identity: "
                f"{' or '.join(SPARK_IDENTITY_TYPES)}"
            )
        if not spec.video_asset_id or not spec.image_asset_id:
            raise ValueError("TikTok video ads need video_asset_id and a cover image_asset_id")
        creative: dict[str, Any] = {
            "ad_format": "SINGLE_VIDEO",
            "video_info": {"video_id": spec.video_asset_id},
            "image_info": [{"web_uri": spec.image_asset_id}],
            "identity_type": s.tiktok_identity_type,
            "identity_id": identity,
        }
        if s.tiktok_identity_type == "BC_AUTH_TT":
            if not s.tiktok_identity_authorized_bc_id:
                raise ValueError(
                    "TIKTOK_IDENTITY_AUTHORIZED_BC_ID is required when TIKTOK_IDENTITY_TYPE "
                    "is BC_AUTH_TT"
                )
            creative["identity_authorized_bc_id"] = s.tiktok_identity_authorized_bc_id
        data = self._request(
            "POST",
            "smart_plus/ad/create/",
            json_body={
                "advertiser_id": self.advertiser_id,
                "adgroup_id": spec.ad_set_id,
                "ad_name": spec.name,
                "operation_status": "DISABLE",
                "creative_list": [{"creative_info": creative}],
                "ad_text_list": [{"ad_text": spec.primary_text}],
                "landing_page_url_list": [{"landing_page_url": spec.landing_url}],
                "ad_configuration": {"call_to_action_id": self._cta_portfolio()},
            },
        )
        return str(data["smart_plus_ad_id"])

    def _is_smart_plus(self, level: Level, external_id: str) -> bool:
        """Whether the entity belongs to an Upgraded Smart+ campaign (they have their own
        update endpoints). Ad ids are ``ad_id_v2`` values, as synced."""
        path, key, id_field = LOOKUP[level]
        data = (
            self._request(
                "GET",
                path,
                params={
                    "advertiser_id": self.advertiser_id,
                    "filtering": {key: [external_id]},
                    "fields": [id_field, "campaign_automation_type"],
                },
            )
            or {}
        )
        return any(r.get("campaign_automation_type") == SMART_PLUS for r in data.get("list") or [])

    def _update_budget(self, level: Level, external_id: str, daily_budget: Decimal) -> None:
        if level == "ad":
            raise ValueError("TikTok budgets live on campaigns or ad groups, not ads")
        prefix = "smart_plus/" if self._is_smart_plus(level, external_id) else ""
        if level == "campaign":
            self._request(
                "POST",
                f"{prefix}campaign/update/",
                json_body={
                    "advertiser_id": self.advertiser_id,
                    "campaign_id": external_id,
                    "budget": float(daily_budget),
                },
            )
        else:
            self._request(
                "POST",
                f"{prefix}adgroup/budget/update/",
                json_body={
                    "advertiser_id": self.advertiser_id,
                    "budget": [{"adgroup_id": external_id, "budget": float(daily_budget)}],
                },
            )

    def _set_status(self, level: Level, external_id: str, status: EntityStatus) -> None:
        smart_plus = self._is_smart_plus(level, external_id)
        path, key = {
            "campaign": ("campaign/status/update/", "campaign_ids"),
            "ad_set": ("adgroup/status/update/", "adgroup_ids"),
            "ad": ("ad/status/update/", "smart_plus_ad_ids" if smart_plus else "ad_ids"),
        }[level]
        self._request(
            "POST",
            f"smart_plus/{path}" if smart_plus else path,
            json_body={
                "advertiser_id": self.advertiser_id,
                key: [external_id],
                "operation_status": "ENABLE" if status == EntityStatus.ACTIVE else "DISABLE",
            },
        )
