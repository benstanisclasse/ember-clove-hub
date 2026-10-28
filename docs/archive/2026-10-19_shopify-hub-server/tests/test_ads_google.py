"""Google Ads REST client + YouTube upload against a scripted transport."""

from __future__ import annotations

import base64
from datetime import date
from decimal import Decimal as D

import httpx
import pytest
from ads_mock import MockHTTP, body, form
from conftest import seed_entity
from pydantic import SecretStr

from app.config import Settings
from app.integrations.ads.base import AdSpec, CampaignSpec, MediaUpload
from app.integrations.ads.google import GoogleAds
from app.integrations.http import IntegrationError
from app.models import EntityStatus

TOKEN = {"access_token": "ya29.test-access", "expires_in": 3599}


def settings(**kw: object) -> Settings:
    base = dict(
        google_ads_developer_token=SecretStr("devtok"),
        google_ads_client_id="cid",
        google_ads_client_secret=SecretStr("csec"),
        google_ads_refresh_token=SecretStr("1//refresh-ads"),
        google_ads_customer_id="123-456-7890",
        google_ads_login_customer_id="111-222-3333",
        youtube_refresh_token=SecretStr("1//refresh-yt"),
        google_ads_business_name="Demo Shop",
    )
    return Settings(**{**base, **kw})  # type: ignore[arg-type]


def client(mock: MockHTTP, session_factory=None, **kw: object) -> GoogleAds:  # type: ignore[no-untyped-def]
    mock.routes.insert(0, ("POST", "oauth2.googleapis.com/token", TOKEN))
    extra = {"session_factory": session_factory} if session_factory else {}
    return GoogleAds(settings(**kw), http=mock.client(), sleep=lambda s: None, **extra)


def search_router(pages: dict[str, list[dict]]):  # type: ignore[no-untyped-def]
    """Answer googleAds:search by the FROM clause of the GAQL query."""

    def handler(req: httpx.Request) -> dict:
        q = body(req)["query"]
        resource = q.split(" FROM ")[1].split()[0]
        return {"results": pages.get(resource, [])}

    return handler


def test_headers_and_customer_id_normalization() -> None:
    mock = MockHTTP().on(
        "POST",
        "googleAds:search",
        {
            "results": [
                {
                    "customer": {
                        "id": "1234567890",
                        "descriptiveName": "Shop",
                        "currencyCode": "USD",
                        "timeZone": "America/New_York",
                    }
                }
            ]
        },
    )
    g = client(mock)
    acct = g.get_account()
    assert acct.currency == "USD" and acct.timezone == "America/New_York"
    req = mock.find("POST", "googleAds:search")[0]
    assert "/v25/customers/1234567890/" in str(req.url)
    assert (
        req.headers["developer-token"] == "devtok"
        and req.headers["login-customer-id"] == "1112223333"
    )
    assert req.headers["Authorization"] == "Bearer ya29.test-access"
    assert form(mock.find("POST", "oauth2")[0])["refresh_token"] == "1//refresh-ads"


def test_search_pages_with_next_page_token() -> None:
    pages = [{"results": [{"n": 1}], "nextPageToken": "p2"}, {"results": [{"n": 2}]}]
    mock = MockHTTP().on("POST", "googleAds:search", pages)
    assert [r["n"] for r in client(mock).search("SELECT x FROM campaign")] == [1, 2]
    assert body(mock.find("POST", "googleAds:search")[1])["pageToken"] == "p2"


def test_structure_includes_pmax_container_and_disapproved_ads() -> None:
    pages = {
        "customer": [{"customer": {"id": "1234567890", "currencyCode": "USD"}}],
        "campaign": [
            {
                "campaign": {
                    "id": "1",
                    "name": "Search",
                    "status": "ENABLED",
                    "advertisingChannelType": "SEARCH",
                },
                "campaignBudget": {"amountMicros": "25000000"},
            },
            {
                "campaign": {
                    "id": "2",
                    "name": "PMax",
                    "status": "PAUSED",
                    "advertisingChannelType": "PERFORMANCE_MAX",
                }
            },
        ],
        "ad_group": [
            {"adGroup": {"id": "10", "name": "AG", "status": "ENABLED"}, "campaign": {"id": "1"}}
        ],
        "ad_group_ad": [
            {
                "adGroupAd": {
                    "ad": {"id": "100", "name": "Ad"},
                    "status": "ENABLED",
                    "policySummary": {"approvalStatus": "DISAPPROVED"},
                },
                "adGroup": {"id": "10"},
            }
        ],
    }
    st = client(MockHTTP().on("POST", "googleAds:search", search_router(pages))).list_structure()
    assert st.campaigns[0].daily_budget == D("25")
    assert [a.external_id for a in st.ads] == ["100", "c2"]
    assert st.ads[0].status == EntityStatus.REJECTED
    assert st.ad_sets[-1].campaign_external_id == "2"


def test_metrics_micros_and_pmax_rows() -> None:
    pages = {
        "ad_group_ad": [
            {
                "adGroupAd": {"ad": {"id": "100"}},
                "segments": {"date": "2026-10-01"},
                "metrics": {
                    "costMicros": "12345678",
                    "impressions": "900",
                    "clicks": "30",
                    "conversions": 2.0,
                    "conversionsValue": 180.5,
                },
            }
        ],
        "campaign": [
            {
                "campaign": {"id": "2"},
                "segments": {"date": "2026-10-01"},
                "metrics": {"costMicros": "5000000"},
            }
        ],
    }
    mock = MockHTTP().on("POST", "googleAds:search", search_router(pages))
    a, p = client(mock).get_daily_metrics(date(2026, 10, 1), date(2026, 10, 1))
    assert (a.ad_external_id, a.spend, a.clicks, a.purchases, a.platform_revenue) == (
        "100",
        D("12.35"),
        30,
        2,
        D("180.50"),
    )
    assert (p.ad_external_id, p.spend) == ("c2", D("5.00"))
    assert "BETWEEN '2026-10-01' AND '2026-10-01'" in body(mock.calls[1])["query"]


def test_401_refreshes_access_token() -> None:
    expired = httpx.Response(401, json={"error": {"status": "UNAUTHENTICATED"}})
    mock = MockHTTP().on(
        "POST", "googleAds:search", [expired, {"results": [{"customer": {"id": "1"}}]}]
    )
    client(mock).get_account()
    assert len(mock.find("POST", "oauth2")) == 2


def test_revoked_refresh_token_message() -> None:
    mock = MockHTTP().on(
        "POST", "oauth2.googleapis.com/token", httpx.Response(400, json={"error": "invalid_grant"})
    )
    g = GoogleAds(settings(), http=mock.client(), sleep=lambda s: None)
    with pytest.raises(IntegrationError, match="refresh token rejected"):
        g.get_account()


def test_budget_update_looks_up_budget_then_mutates(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = (
        MockHTTP()
        .on(
            "POST",
            "googleAds:search",
            {
                "results": [
                    {"campaign": {"campaignBudget": "customers/1234567890/campaignBudgets/77"}}
                ]
            },
        )
        .on(
            "POST",
            "campaignBudgets:mutate",
            {"results": [{"resourceName": "customers/1234567890/campaignBudgets/77"}]},
        )
    )
    seed_entity(writes_on, "google", "1", budget="40")
    client(mock, session_factory=writes_on).update_budget("campaign", "1", D("42.5"))
    op = body(mock.find("POST", "campaignBudgets:mutate")[0])["operations"][0]
    assert op == {
        "update": {
            "resourceName": "customers/1234567890/campaignBudgets/77",
            "amountMicros": "42500000",
        },
        "updateMask": "amount_micros",
    }


def test_set_status_on_ad_uses_ad_group_ad_resource(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = (
        MockHTTP()
        .on("POST", "googleAds:search", {"results": [{"adGroup": {"id": "10"}}]})
        .on("POST", "adGroupAds:mutate", {"results": [{"resourceName": "x"}]})
    )
    client(mock, session_factory=writes_on).set_status("ad", "100", EntityStatus.PAUSED)
    op = body(mock.find("POST", "adGroupAds:mutate")[0])["operations"][0]
    assert op["update"] == {
        "resourceName": "customers/1234567890/adGroupAds/10~100",
        "status": "PAUSED",
    }


def test_video_upload_goes_through_youtube_then_asset(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = (
        MockHTTP()
        .on(
            "POST",
            "upload/youtube/v3/videos",
            httpx.Response(200, headers={"Location": "https://upload.example/session1"}),
        )
        .on("PUT", "upload.example/session1", {"id": "yt123"})
        .on(
            "POST",
            "assets:mutate",
            {"results": [{"resourceName": "customers/1234567890/assets/555"}]},
        )
    )
    g = client(mock, session_factory=writes_on)
    asset = g.upload_video(MediaUpload("hook.mp4", b"\x00\x01", "video/mp4", title="Hook A"))
    assert asset == "customers/1234567890/assets/555"
    start = mock.find("POST", "upload/youtube")[0]
    assert body(start)["status"]["privacyStatus"] == "unlisted"
    assert mock.find("PUT", "session1")[0].content == b"\x00\x01"
    created = body(mock.find("POST", "assets:mutate")[0])["operations"][0]["create"]
    assert created["youtubeVideoAsset"] == {"youtubeVideoId": "yt123"}
    # the YouTube upload authenticated with the YouTube refresh token (the asset call uses the Ads one)
    assert [form(r)["refresh_token"] for r in mock.find("POST", "oauth2")] == [
        "1//refresh-yt",
        "1//refresh-ads",
    ]


def test_create_campaign_and_demand_gen_ad(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = (
        MockHTTP()
        .on(
            "POST",
            "campaignBudgets:mutate",
            {"results": [{"resourceName": "customers/1234567890/campaignBudgets/1"}]},
        )
        .on(
            "POST",
            "campaigns:mutate",
            {"results": [{"resourceName": "customers/1234567890/campaigns/2"}]},
        )
        .on(
            "POST",
            "adGroups:mutate",
            {"results": [{"resourceName": "customers/1234567890/adGroups/3"}]},
        )
        .on("POST", "adGroupCriteria:mutate", {"results": [{"resourceName": "x"}]})
        .on(
            "POST",
            "adGroupAds:mutate",
            {"results": [{"resourceName": "customers/1234567890/adGroupAds/3~4"}]},
        )
    )
    g = client(mock, session_factory=writes_on)
    created = g.create_campaign(
        CampaignSpec(name="DG test", daily_budget=D("20"), countries=["US"])
    )
    assert (created.campaign_id, created.ad_set_id) == ("2", "3")
    camp = body(mock.find("POST", "campaigns:mutate")[0])["operations"][0]["create"]
    assert camp["status"] == "PAUSED" and camp["advertisingChannelType"] == "DEMAND_GEN"
    crit = body(mock.find("POST", "adGroupCriteria:mutate")[0])["operations"][0]["create"]
    assert crit["location"] == {"geoTargetConstant": "geoTargetConstants/2840"}

    ad_id = g.create_ad(
        AdSpec(
            ad_set_id="3",
            name="Hook A",
            landing_url="https://shop.com",
            primary_text="Try it today",
            headline="Glow in 7 days",
            video_asset_id="customers/1/assets/9",
            image_asset_id="customers/1/assets/8",
        )
    )
    assert ad_id == "4"
    ad = body(mock.find("POST", "adGroupAds:mutate")[0])["operations"][0]["create"]
    dg = ad["ad"]["demandGenVideoResponsiveAd"]
    assert ad["status"] == "PAUSED" and dg["videos"] == [{"asset": "customers/1/assets/9"}]
    assert dg["businessName"] == {"text": "Demo Shop"}


def test_image_asset_is_base64(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = MockHTTP().on(
        "POST", "assets:mutate", {"results": [{"resourceName": "customers/1/assets/1"}]}
    )
    client(mock, session_factory=writes_on).upload_image(
        MediaUpload("logo.png", b"PNGDATA", "image/png")
    )
    created = body(mock.find("POST", "assets:mutate")[0])["operations"][0]["create"]
    assert base64.b64decode(created["imageAsset"]["data"]) == b"PNGDATA"
