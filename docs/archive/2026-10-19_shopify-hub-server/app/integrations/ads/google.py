"""Google Ads API (REST) client, plus YouTube upload for video ads.

Auth: OAuth refresh token (offline access, ``adwords`` scope) + developer token, and the
manager account id in ``login-customer-id`` when the ad account sits under an MCC.

Reads use GAQL via ``googleAds:search`` (paged by ``nextPageToken``). Amounts arrive in
**micros** (1,000,000 = 1 unit of account currency).

Performance Max campaigns have no individual ads; their spend is reported on a synthetic
ad set + ad with external id ``c<campaign_id>`` so it isn't lost from profit totals.

Video ads: the file is uploaded to YouTube (unlisted) first, registered as a
``YOUTUBE_VIDEO`` asset, then used in a **Demand Gen** video responsive ad -- the video
format the Google Ads API can create.
"""

from __future__ import annotations

import base64
import time
from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime
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
from app.integrations.google_oauth import GoogleOAuthToken
from app.integrations.http import IntegrationError, NotConfiguredError, request_with_retries
from app.log import get_logger
from app.models import EntityStatus, Platform

log = get_logger(__name__)
MICROS = Decimal(1_000_000)
STATUS = {
    "ENABLED": EntityStatus.ACTIVE,
    "PAUSED": EntityStatus.PAUSED,
    "REMOVED": EntityStatus.DELETED,
}
# Geo target constants (https://developers.google.com/google-ads/api/data/geotargets)
GEO_TARGETS = {"US": "2840", "CA": "2124", "GB": "2826", "AU": "2036", "NZ": "2554", "IE": "2372"}
PMAX_PREFIX = "c"


def _micros_to_major(value: Any) -> Decimal | None:
    return (Decimal(str(value)) / MICROS) if value not in (None, "", "0") else None


def _major_to_micros(amount: Decimal) -> str:
    return str(int((amount * MICROS).to_integral_value()))


def _id_from_resource(resource_name: str) -> str:
    """``customers/1/campaigns/42`` -> ``42``; ``.../adGroupAds/7~99`` -> ``99``."""
    return resource_name.rsplit("/", 1)[-1].split("~")[-1]


class YouTubeUploader:
    """Resumable upload to the YouTube Data API (videos.insert costs ~1,600 quota units of
    the default 10,000/day -- a handful of uploads per day unless you request more)."""

    URL = "https://www.googleapis.com/upload/youtube/v3/videos"

    def __init__(
        self,
        token: GoogleOAuthToken,
        http: httpx.Client,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.token, self.http, self.sleep = token, http, sleep

    def upload(self, media: MediaUpload, description: str = "") -> str:
        meta = {
            "snippet": {
                "title": (media.title or media.filename)[:100],
                "description": description,
                "categoryId": "22",
            },
            "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False},
        }
        start = request_with_retries(
            self.http,
            "POST",
            self.URL,
            params={"uploadType": "resumable", "part": "snippet,status"},
            json=meta,
            headers={
                **self.token.headers(),
                "X-Upload-Content-Type": media.mime_type,
                "X-Upload-Content-Length": str(len(media.content)),
            },
            sleep=self.sleep,
            on_unauthorized=self._refresh,
        )
        location = start.headers.get("Location")
        if not location:
            raise IntegrationError("YouTube did not return an upload URL")
        done = request_with_retries(
            self.http,
            "PUT",
            location,
            content=media.content,
            headers={**self.token.headers(), "Content-Type": media.mime_type},
            sleep=self.sleep,
            on_unauthorized=self._refresh,
        )
        return str(done.json()["id"])

    def _refresh(self) -> dict[str, str]:
        self.token.invalidate()
        return self.token.headers()


class GoogleAds(AdPlatform):
    platform = Platform.GOOGLE

    def __init__(
        self,
        settings: Settings | None = None,
        http: httpx.Client | None = None,
        redis: Any | None = None,
        sleep: Callable[[float], None] = time.sleep,
        session_factory: SessionFactory = session_scope,
    ) -> None:
        super().__init__(session_factory)
        self.settings = s = settings or get_settings()
        if not s.google_ads_configured:
            raise NotConfiguredError(
                "Google Ads not configured: set GOOGLE_ADS_DEVELOPER_TOKEN, _CLIENT_ID, _CLIENT_SECRET, "
                "_REFRESH_TOKEN and _CUSTOMER_ID"
            )
        self.http = http or httpx.Client(timeout=httpx.Timeout(120.0, connect=10.0))
        self.sleep = sleep
        self.cid = s.google_ads_customer_id
        self.account_external_id = s.google_ads_customer_id
        self.base = (
            f"https://googleads.googleapis.com/{s.google_ads_api_version}/customers/{self.cid}"
        )
        self.token = GoogleOAuthToken(
            s.google_ads_client_id,
            s.google_ads_client_secret.get_secret_value(),
            s.google_ads_refresh_token.get_secret_value(),
            self.http,
            redis=redis,
            sleep=sleep,
        )
        yt_refresh = s.youtube_refresh_token.get_secret_value()
        self.youtube = (
            YouTubeUploader(
                GoogleOAuthToken(
                    s.google_ads_client_id,
                    s.google_ads_client_secret.get_secret_value(),
                    yt_refresh,
                    self.http,
                    redis=redis,
                    sleep=sleep,
                ),
                self.http,
                sleep,
            )
            if yt_refresh
            else None
        )

    # --- transport ------------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        h = {
            **self.token.headers(),
            "developer-token": self.settings.google_ads_developer_token.get_secret_value(),
            "Content-Type": "application/json",
        }
        if self.settings.google_ads_login_customer_id:
            h["login-customer-id"] = self.settings.google_ads_login_customer_id
        return h

    def _refresh(self) -> dict[str, str]:
        self.token.invalidate()
        return self._headers()

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = request_with_retries(
                self.http,
                "POST",
                f"{self.base}/{path}",
                json=body,
                headers=self._headers(),
                sleep=self.sleep,
                on_unauthorized=self._refresh,
            )
        except IntegrationError as exc:
            raise IntegrationError(
                f"Google Ads {path}: {exc}", status=exc.status, retryable=exc.retryable
            ) from exc
        return resp.json()  # type: ignore[no-any-return]

    def search(self, query: str) -> Iterator[dict[str, Any]]:
        body: dict[str, Any] = {"query": " ".join(query.split())}
        while True:
            page = self._post("googleAds:search", body)
            yield from page.get("results") or []
            token = page.get("nextPageToken")
            if not token:
                return
            body["pageToken"] = token

    def _mutate(self, resource: str, operations: list[dict[str, Any]]) -> list[str]:
        result = self._post(f"{resource}:mutate", {"operations": operations})
        return [r["resourceName"] for r in result.get("results") or []]

    # --- conversions (Phase 3b) -----------------------------------------------------------

    def upload_click_conversions(self, conversions: list[dict[str, Any]]) -> dict[str, Any]:
        """``customers/{id}:uploadClickConversions`` with partial failure on, so one bad
        click id doesn't reject the batch. Returns the raw response."""
        url = f"{self.base}:uploadClickConversions"
        resp = request_with_retries(
            self.http,
            "POST",
            url,
            json={"conversions": conversions, "partialFailure": True},
            headers=self._headers(),
            sleep=self.sleep,
            on_unauthorized=self._refresh,
        )
        return resp.json()  # type: ignore[no-any-return]

    def create_conversion_action(self, name: str, currency: str) -> str:
        """An UPLOAD_CLICKS purchase conversion action; returns its resource name.
        (Account change: call it through app.actions.write_action.)"""
        (rn,) = self._mutate(
            "conversionActions",
            [
                {
                    "create": {
                        "name": name,
                        "type": "UPLOAD_CLICKS",
                        "category": "PURCHASE",
                        "status": "ENABLED",
                        "countingType": "ONE_PER_CLICK",
                        "valueSettings": {
                            "defaultValue": 0,
                            "defaultCurrencyCode": currency,
                            "alwaysUseDefaultValue": False,
                        },
                    }
                }
            ],
        )
        return rn

    # --- reads ----------------------------------------------------------------------------

    def get_account(self) -> AccountInfo:
        row = next(
            self.search(
                "SELECT customer.id, customer.descriptive_name, customer.currency_code, customer.time_zone FROM customer"
            ),
            {},
        )
        c = row.get("customer") or {}
        return AccountInfo(
            self.cid, c.get("descriptiveName"), c.get("currencyCode"), c.get("timeZone")
        )

    def list_structure(self) -> Structure:
        account = self.get_account()
        campaigns, ad_sets, ads = [], [], []
        pmax: list[str] = []
        for r in self.search("""
            SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
                   campaign_budget.amount_micros
            FROM campaign WHERE campaign.status != 'REMOVED'"""):
            c, budget = r["campaign"], r.get("campaignBudget") or {}
            campaigns.append(
                CampaignInfo(
                    external_id=str(c["id"]),
                    name=c.get("name"),
                    status=STATUS.get(c.get("status", ""), EntityStatus.UNKNOWN),
                    objective=c.get("advertisingChannelType"),
                    daily_budget=_micros_to_major(budget.get("amountMicros")),
                )
            )
            if c.get("advertisingChannelType") == "PERFORMANCE_MAX":
                pmax.append(str(c["id"]))
        for r in self.search("""
            SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id
            FROM ad_group WHERE ad_group.status != 'REMOVED'"""):
            g = r["adGroup"]
            ad_sets.append(
                AdSetInfo(
                    str(g["id"]),
                    str(r["campaign"]["id"]),
                    g.get("name"),
                    STATUS.get(g.get("status", ""), EntityStatus.UNKNOWN),
                )
            )
        for r in self.search("""
            SELECT ad_group_ad.ad.id, ad_group_ad.ad.name, ad_group_ad.status,
                   ad_group_ad.policy_summary.approval_status, ad_group.id
            FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
            a = r["adGroupAd"]
            status = STATUS.get(a.get("status", ""), EntityStatus.UNKNOWN)
            if (a.get("policySummary") or {}).get("approvalStatus") == "DISAPPROVED":
                status = EntityStatus.REJECTED
            ads.append(
                AdInfo(str(a["ad"]["id"]), str(r["adGroup"]["id"]), a["ad"].get("name"), status)
            )
        for cid in pmax:  # synthetic containers so PMax spend has somewhere to land
            camp = next(c for c in campaigns if c.external_id == cid)
            ad_sets.append(
                AdSetInfo(PMAX_PREFIX + cid, cid, f"{camp.name} (campaign level)", camp.status)
            )
            ads.append(
                AdInfo(
                    PMAX_PREFIX + cid,
                    PMAX_PREFIX + cid,
                    f"{camp.name} (campaign level)",
                    camp.status,
                )
            )
        return Structure(account, campaigns, ad_sets, ads)

    def get_daily_metrics(self, start: date, end: date) -> list[DailyMetric]:
        between = f"segments.date BETWEEN '{start.isoformat()}' AND '{end.isoformat()}'"
        out = []
        # Google has no 3-second video view metric; video_3s_views stays 0 for Google.
        for r in self.search(f"""
            SELECT ad_group_ad.ad.id, segments.date, metrics.cost_micros, metrics.impressions,
                   metrics.clicks, metrics.conversions, metrics.conversions_value
            FROM ad_group_ad WHERE {between} AND metrics.impressions > 0"""):
            out.append(self._metric(str(r["adGroupAd"]["ad"]["id"]), r))
        for r in self.search(f"""
            SELECT campaign.id, segments.date, metrics.cost_micros, metrics.impressions,
                   metrics.clicks, metrics.conversions, metrics.conversions_value
            FROM campaign WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX' AND {between}"""):
            out.append(self._metric(PMAX_PREFIX + str(r["campaign"]["id"]), r))
        return out

    @staticmethod
    def _metric(ad_id: str, row: dict[str, Any]) -> DailyMetric:
        m = row.get("metrics") or {}
        return DailyMetric(
            ad_external_id=ad_id,
            date=date.fromisoformat(row["segments"]["date"]),
            spend=(Decimal(str(m.get("costMicros", 0))) / MICROS).quantize(Decimal("0.01")),
            impressions=as_int(m.get("impressions")),
            clicks=as_int(m.get("clicks")),
            purchases=as_int(round(float(m.get("conversions") or 0))),
            platform_revenue=as_decimal(m.get("conversionsValue")).quantize(Decimal("0.01")),
        )

    # --- writes ---------------------------------------------------------------------------

    def _rn(self, kind: str, external_id: str) -> str:
        return f"customers/{self.cid}/{kind}/{external_id}"

    def _create_campaign(self, spec: CampaignSpec) -> CreatedCampaign:
        try:
            geos = [GEO_TARGETS[c.upper()] for c in spec.countries]
        except KeyError as exc:
            raise ValueError(
                f"no Google geo target mapped for {exc.args[0]}; add it to GEO_TARGETS"
            ) from None
        stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        (budget,) = self._mutate(
            "campaignBudgets",
            [
                {
                    "create": {
                        "name": f"{spec.name} budget {stamp}",
                        "amountMicros": _major_to_micros(spec.daily_budget),
                        "deliveryMethod": "STANDARD",
                        "explicitlyShared": False,
                    }
                }
            ],
        )
        (campaign,) = self._mutate(
            "campaigns",
            [
                {
                    "create": {
                        "name": spec.name,
                        "status": "PAUSED",
                        "advertisingChannelType": spec.objective or "DEMAND_GEN",
                        "campaignBudget": budget,
                        "maximizeConversions": {},
                        "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
                    }
                }
            ],
        )
        (ad_group,) = self._mutate(
            "adGroups",
            [
                {
                    "create": {
                        "name": f"{spec.name} - ad group",
                        "campaign": campaign,
                        "status": "PAUSED",
                    }
                }
            ],
        )
        # Demand Gen targets locations at the ad group level.
        self._mutate(
            "adGroupCriteria",
            [
                {
                    "create": {
                        "adGroup": ad_group,
                        "location": {"geoTargetConstant": f"geoTargetConstants/{g}"},
                    }
                }
                for g in geos
            ],
        )
        return CreatedCampaign(
            _id_from_resource(campaign), _id_from_resource(ad_group), extra={"budget": budget}
        )

    def _upload_video(self, media: MediaUpload) -> str:
        if self.youtube is None:
            raise NotConfiguredError("YOUTUBE_REFRESH_TOKEN is required to upload Google video ads")
        video_id = self.youtube.upload(media)
        (asset,) = self._mutate(
            "assets",
            [
                {
                    "create": {
                        "name": f"{media.title or media.filename} ({video_id})",
                        "type": "YOUTUBE_VIDEO",
                        "youtubeVideoAsset": {"youtubeVideoId": video_id},
                    }
                }
            ],
        )
        log.info("youtube_video_uploaded", video_id=video_id)
        return asset

    def _upload_image(self, media: MediaUpload) -> str:
        (asset,) = self._mutate(
            "assets",
            [
                {
                    "create": {
                        "name": f"{media.title or media.filename} {datetime.now(UTC):%Y%m%d%H%M%S}",
                        "type": "IMAGE",
                        "imageAsset": {"data": base64.b64encode(media.content).decode()},
                    }
                }
            ],
        )
        return asset

    def _create_ad(self, spec: AdSpec) -> str:
        if not spec.video_asset_id:
            raise ValueError("Google Demand Gen video ads need video_asset_id (from upload_video)")
        if not spec.image_asset_id:
            raise ValueError(
                "Google Demand Gen ads need a logo: pass image_asset_id (square image asset)"
            )
        business = (self.settings.google_ads_business_name or "").strip()
        if not business:
            raise ValueError("GOOGLE_ADS_BUSINESS_NAME is required for Demand Gen ads")
        headline = (spec.headline or spec.name)[:40]
        (ad,) = self._mutate(
            "adGroupAds",
            [
                {
                    "create": {
                        "adGroup": self._rn("adGroups", spec.ad_set_id),
                        "status": "PAUSED",
                        "ad": {
                            "name": spec.name,
                            "finalUrls": [spec.landing_url],
                            "demandGenVideoResponsiveAd": {
                                "headlines": [{"text": headline}],
                                "longHeadlines": [
                                    {"text": (spec.headline or spec.primary_text)[:90]}
                                ],
                                "descriptions": [{"text": spec.primary_text[:90]}],
                                "videos": [{"asset": spec.video_asset_id}],
                                "logoImages": [{"asset": spec.image_asset_id}],
                                "businessName": {"text": business[:25]},
                                "callToActions": [
                                    {"text": spec.call_to_action.replace("_", " ").title()[:10]}
                                ],
                            },
                        },
                    }
                }
            ],
        )
        return _id_from_resource(ad)

    def _update_budget(self, level: Level, external_id: str, daily_budget: Decimal) -> None:
        if level != "campaign":
            raise ValueError("Google Ads budgets live on campaigns")
        row = next(
            self.search(
                f"SELECT campaign.campaign_budget FROM campaign WHERE campaign.id = {int(external_id)}"
            ),
            None,
        )
        if not row:
            raise IntegrationError(f"Google campaign {external_id} not found")
        self._mutate(
            "campaignBudgets",
            [
                {
                    "update": {
                        "resourceName": row["campaign"]["campaignBudget"],
                        "amountMicros": _major_to_micros(daily_budget),
                    },
                    "updateMask": "amount_micros",
                }
            ],
        )

    def _set_status(self, level: Level, external_id: str, status: EntityStatus) -> None:
        value = "ENABLED" if status == EntityStatus.ACTIVE else "PAUSED"
        if external_id.startswith(PMAX_PREFIX):
            level, external_id = "campaign", external_id[len(PMAX_PREFIX) :]
        if level == "campaign":
            resource, rn = "campaigns", self._rn("campaigns", external_id)
        elif level == "ad_set":
            resource, rn = "adGroups", self._rn("adGroups", external_id)
        else:
            row = next(
                self.search(
                    f"SELECT ad_group.id FROM ad_group_ad WHERE ad_group_ad.ad.id = {int(external_id)}"
                ),
                None,
            )
            if not row:
                raise IntegrationError(f"Google ad {external_id} not found")
            resource, rn = (
                "adGroupAds",
                self._rn("adGroupAds", f"{row['adGroup']['id']}~{external_id}"),
            )
        self._mutate(
            resource, [{"update": {"resourceName": rn, "status": value}, "updateMask": "status"}]
        )
