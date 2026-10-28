"""TikTok Marketing API client against a scripted transport."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal as D

import pytest
from ads_mock import MockHTTP, body, query
from conftest import seed_entity
from pydantic import SecretStr

from app.config import Settings
from app.integrations.ads.base import AdSpec, CampaignSpec, MediaUpload
from app.integrations.ads.tiktok import SMART_PLUS, TikTokAds, age_groups
from app.integrations.http import IntegrationError
from app.models import EntityStatus

V = "/v1.3/"  # pins a legacy path: "smart_plus/ad/get" also contains "ad/get"


def ok(data: object) -> dict[str, object]:
    return {"code": 0, "message": "OK", "request_id": "r", "data": data}


def client(mock: MockHTTP, session_factory=None, **kw: object) -> tuple[TikTokAds, list[float]]:  # type: ignore[no-untyped-def]
    s = Settings(
        **{
            "tiktok_access_token": SecretStr("tt-token"),
            "tiktok_advertiser_id": "700",
            "tiktok_pixel_id": "px1",
            "tiktok_identity_id": "id1",
            **kw,
        }
    )  # type: ignore[arg-type]
    slept: list[float] = []
    extra = {"session_factory": session_factory} if session_factory else {}
    return TikTokAds(s, http=mock.client(), sleep=slept.append, **extra), slept


ACCOUNT = ok(
    {
        "list": [
            {
                "advertiser_id": "700",
                "name": "Shop",
                "currency": "USD",
                "timezone": "America/New_York",
                "status": "STATUS_ENABLE",
            }
        ]
    }
)


def test_structure_paging_and_status_mapping() -> None:
    mock = MockHTTP().on("GET", "advertiser/info", ACCOUNT)
    mock.on(
        "GET",
        "campaign/get",
        [
            ok(
                {
                    "list": [
                        {
                            "campaign_id": 1,
                            "campaign_name": "A",
                            "operation_status": "ENABLE",
                            "budget_mode": "BUDGET_MODE_DAY",
                            "budget": 50,
                        }
                    ],
                    "page_info": {"page": 1, "total_page": 2},
                }
            ),
            ok(
                {
                    "list": [
                        {
                            "campaign_id": 2,
                            "campaign_name": "B",
                            "operation_status": "DISABLE",
                            "budget_mode": "BUDGET_MODE_INFINITE",
                        }
                    ],
                    "page_info": {"page": 2, "total_page": 2},
                }
            ),
        ],
    )
    mock.on(
        "GET",
        "adgroup/get",
        ok(
            {
                "list": [
                    {
                        "adgroup_id": 10,
                        "campaign_id": 1,
                        "operation_status": "ENABLE",
                        "secondary_status": "ADGROUP_STATUS_DELIVERY_OK",
                    }
                ],
                "page_info": {"total_page": 1},
            }
        ),
    )
    mock.on(
        "GET",
        V + "ad/get",
        ok(
            {
                "list": [
                    {
                        "ad_id": 100,
                        "adgroup_id": 10,
                        "operation_status": "ENABLE",
                        "secondary_status": "AD_STATUS_NOT_APPROVED",
                        "campaign_automation_type": "MANUAL",
                    },
                    {  # one creative of the Smart+ ad below, not an ad of its own
                        "ad_id": 901,
                        "smart_plus_ad_id": "sp1",
                        "adgroup_id": 11,
                        "operation_status": "ENABLE",
                        "campaign_automation_type": "UPGRADED_SMART_PLUS_CREATIVE",
                    },
                ],
                "page_info": {"total_page": 1},
            }
        ),
    )
    mock.on(
        "GET",
        "smart_plus/ad/get",
        ok(
            {
                "list": [
                    {
                        "smart_plus_ad_id": "sp1",
                        "adgroup_id": "11",
                        "ad_name": "Hook A",
                        "operation_status": "DISABLE",
                        "secondary_status": "AD_STATUS_DISABLE",
                    }
                ],
                "page_info": {"total_page": 1},
            }
        ),
    )
    tt, _ = client(mock)
    st = tt.list_structure()
    assert [(c.external_id, c.status, c.daily_budget) for c in st.campaigns] == [
        ("1", EntityStatus.ACTIVE, D("50")),
        ("2", EntityStatus.PAUSED, None),
    ]
    assert [(a.external_id, a.ad_set_external_id, a.status) for a in st.ads] == [
        ("100", "10", EntityStatus.REJECTED),
        ("sp1", "11", EntityStatus.PAUSED),
    ]
    assert mock.calls[0].headers["Access-Token"] == "tt-token"
    assert json.loads(query(mock.find("GET", "campaign/get")[0])["fields"])[0] == "campaign_id"
    ad_fields = json.loads(query(mock.find("GET", V + "ad/get")[0])["fields"])
    assert "campaign_automation_type" in ad_fields


def test_report_metrics_mapping_and_30_day_chunks() -> None:
    row = {
        "dimensions": {"ad_id_v2": 100, "stat_time_day": "2026-10-01 00:00:00"},
        "metrics": {
            "spend": "20.00",
            "impressions": "5000",
            "clicks": "60",
            "video_watched_2s": "900",
            "complete_payment": "2",
            "complete_payment_roas": "3.5",
        },
    }
    mock = MockHTTP().on(
        "GET", "report/integrated/get", ok({"list": [row], "page_info": {"total_page": 1}})
    )
    tt, _ = client(mock)
    metrics = tt.get_daily_metrics(date(2026, 8, 1), date(2026, 10, 1))  # 62 days -> 3 requests
    assert len(mock.calls) == 3
    q = query(mock.calls[0])
    assert (q["start_date"], q["end_date"], q["data_level"]) == (
        "2026-08-01",
        "2026-08-30",
        "AUCTION_AD",
    )
    assert json.loads(q["dimensions"]) == ["ad_id_v2", "stat_time_day"]  # Smart+ ad, not creative
    m = metrics[0]
    assert (m.ad_external_id, m.date, m.spend, m.video_3s_views, m.purchases) == (
        "100",
        date(2026, 10, 1),
        D("20.00"),
        900,
        2,
    )
    assert m.platform_revenue == D("70.00")  # roas x spend


def test_rate_limit_code_retries_and_auth_code_fails_fast() -> None:
    mock = MockHTTP().on(
        "GET", "advertiser/info", [{"code": 40100, "message": "Too many requests"}, ACCOUNT]
    )
    tt, slept = client(mock)
    assert tt.get_account().name == "Shop" and len(slept) == 1

    tt2, _ = client(
        MockHTTP().on(
            "GET", "advertiser/info", {"code": 40105, "message": "Access token is invalid"}
        )
    )
    with pytest.raises(IntegrationError, match="token rejected"):
        tt2.get_account()


def automation(kind: str) -> dict[str, object]:
    """A legacy getter's answer to the Smart+-or-manual lookup made before a write."""
    return ok({"list": [{"campaign_automation_type": kind}], "page_info": {"total_page": 1}})


CTA_RECOMMEND = ok(
    {
        "recommend_assets": [
            {"asset_ids": ["201902", "201404"], "asset_content": "Shop now"},
            {"asset_ids": ["202114"], "asset_content": "Learn more"},
            {"asset_ids": [], "asset_content": "empty"},
        ]
    }
)


def smart_plus_mock() -> MockHTTP:
    return (
        MockHTTP()
        .on("POST", "smart_plus/campaign/create", ok({"campaign_id": "c1"}))
        .on("POST", "smart_plus/adgroup/create", ok({"adgroup_id": "g1"}))
        .on("POST", "file/video/ad/upload", ok([{"video_id": "v1"}]))
        .on("POST", "file/image/ad/upload", ok({"image_id": "i1"}))
        .on("GET", "creative/cta/recommend", CTA_RECOMMEND)
        .on("POST", "creative/portfolio/create", ok({"creative_portfolio_id": "p1"}))
        .on(
            "POST",
            "smart_plus/ad/create",
            [ok({"smart_plus_ad_id": "sp1"}), ok({"smart_plus_ad_id": "sp2"})],
        )
    )


def ad_spec(**kw: object) -> AdSpec:
    return AdSpec(
        **{
            "ad_set_id": "g1",
            "name": "Hook A",
            "landing_url": "https://shop.com",
            "primary_text": "Try",
            "video_asset_id": "v1",
            "image_asset_id": "i1",
            **kw,
        }
    )  # type: ignore[arg-type]


def test_creates_use_upgraded_smart_plus(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = smart_plus_mock()
    tt, _ = client(mock, session_factory=writes_on)
    created = tt.create_campaign(
        CampaignSpec(name="UGC", daily_budget=D("30"), countries=["US"], age_min=25, age_max=44)
    )
    assert (created.campaign_id, created.ad_set_id) == ("c1", "g1")
    # nothing goes to the legacy create endpoints that stop on 2027-01-01
    assert not mock.find("POST", V + "campaign/create")
    assert not mock.find("POST", V + "adgroup/create")

    camp = body(mock.find("POST", "smart_plus/campaign/create")[0])
    assert {k: v for k, v in camp.items() if k != "request_id"} == {
        "advertiser_id": "700",
        "campaign_name": "UGC",
        "objective_type": "WEB_CONVERSIONS",
        "sales_destination": "WEBSITE",
        "budget_optimize_on": False,
        "operation_status": "DISABLE",
    }
    group = body(mock.find("POST", "smart_plus/adgroup/create")[0])
    assert camp["request_id"].isdigit() and group["request_id"].isdigit()
    assert camp["request_id"] != group["request_id"]
    assert (group["campaign_id"], group["promotion_type"], group["pixel_id"]) == (
        "c1",
        "WEBSITE",
        "px1",
    )
    assert (group["optimization_goal"], group["optimization_event"], group["billing_event"]) == (
        "CONVERT",
        "COMPLETE_PAYMENT",
        "OCPM",
    )
    assert (group["budget_mode"], group["budget"], group["operation_status"]) == (
        "BUDGET_MODE_DYNAMIC_DAILY_BUDGET",
        30.0,
        "DISABLE",
    )
    assert group["targeting_optimization_mode"] == "MANUAL"
    assert group["targeting_spec"] == {
        "location_ids": ["6252001"],
        "age_groups": ["AGE_25_34", "AGE_35_44"],
    }
    assert "placement_type" not in group  # Automatic Placement

    vid = tt.upload_video(MediaUpload("hook.mp4", b"video-bytes", "video/mp4"))
    img = tt.upload_image(MediaUpload("cover.jpg", b"img", "image/jpeg"))
    assert (vid, img) == ("v1", "i1")
    assert tt.create_ad(ad_spec(video_asset_id=vid, image_asset_id=img)) == "sp1"
    assert not mock.find("POST", V + "ad/create")
    assert body(mock.find("POST", "smart_plus/ad/create")[0]) == {
        "advertiser_id": "700",
        "adgroup_id": "g1",
        "ad_name": "Hook A",
        "operation_status": "DISABLE",
        "creative_list": [
            {
                "creative_info": {
                    "ad_format": "SINGLE_VIDEO",
                    "video_info": {"video_id": "v1"},
                    "image_info": [{"web_uri": "i1"}],
                    "identity_type": "TT_USER",
                    "identity_id": "id1",
                }
            }
        ],
        "ad_text_list": [{"ad_text": "Try"}],
        "landing_page_url_list": [{"landing_page_url": "https://shop.com"}],
        "ad_configuration": {"call_to_action_id": "p1"},
    }
    q = query(mock.find("GET", "creative/cta/recommend")[0])
    assert (q["new_version"], q["objective_type"], q["promotion_type"]) == (
        "true",
        "WEB_CONVERSIONS",
        "WEBSITE",
    )
    assert body(mock.find("POST", "creative/portfolio/create")[0]) == {
        "advertiser_id": "700",
        "creative_portfolio_type": "CTA",
        "portfolio_content": [
            {"asset_content": "Shop now", "asset_ids": ["201902", "201404"]},
            {"asset_content": "Learn more", "asset_ids": ["202114"]},
        ],
    }
    # the dynamic CTA is built once per client, then reused
    assert tt.create_ad(ad_spec(name="Hook B")) == "sp2"
    assert len(mock.find("POST", "creative/portfolio/create")) == 1


def test_configured_cta_portfolio_and_bc_identity(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = smart_plus_mock()
    tt, _ = client(
        mock,
        session_factory=writes_on,
        tiktok_cta_portfolio_id="p9",
        tiktok_identity_type="BC_AUTH_TT",
        tiktok_identity_authorized_bc_id="bc1",
    )
    tt.create_ad(ad_spec())
    ad = body(mock.find("POST", "smart_plus/ad/create")[0])
    assert ad["ad_configuration"] == {"call_to_action_id": "p9"}
    assert ad["creative_list"][0]["creative_info"]["identity_authorized_bc_id"] == "bc1"
    assert not mock.find("GET", "creative/cta/recommend")


@pytest.mark.parametrize(
    ("settings", "match"),
    [
        ({"tiktok_identity_type": "CUSTOMIZED_USER"}, "custom identities were retired"),
        ({"tiktok_identity_type": "BC_AUTH_TT"}, "TIKTOK_IDENTITY_AUTHORIZED_BC_ID"),
        ({"tiktok_identity_id": ""}, "TIKTOK_IDENTITY_ID"),
    ],
)
def test_ad_identity_errors(writes_on, settings: dict[str, str], match: str) -> None:  # type: ignore[no-untyped-def]
    mock = smart_plus_mock()
    tt, _ = client(mock, session_factory=writes_on, **settings)
    with pytest.raises(ValueError, match=match):
        tt.create_ad(ad_spec())
    assert not mock.find("POST", "smart_plus/ad/create")


def test_no_recommended_ctas_is_a_clear_error(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = MockHTTP().on("GET", "creative/cta/recommend", ok({"recommend_assets": []}))
    tt, _ = client(mock, session_factory=writes_on)
    with pytest.raises(IntegrationError, match="TIKTOK_CTA_PORTFOLIO_ID"):
        tt.create_ad(ad_spec())


def test_only_the_sales_objective(writes_on) -> None:  # type: ignore[no-untyped-def]
    tt, _ = client(MockHTTP(), session_factory=writes_on)
    with pytest.raises(ValueError, match="WEB_CONVERSIONS"):
        tt.create_campaign(CampaignSpec(name="x", daily_budget=D("10"), objective="TRAFFIC"))


def test_updates_route_smart_plus_and_legacy_entities(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = (
        MockHTTP()
        .on("GET", V + "adgroup/get", [automation(SMART_PLUS), automation("MANUAL")])
        .on("GET", V + "ad/get", [automation(SMART_PLUS), automation("MANUAL")])
        .on("GET", V + "campaign/get", automation(SMART_PLUS))
        .on("POST", "smart_plus/adgroup/budget/update", ok({}))
        .on("POST", V + "adgroup/budget/update", ok({}))
        .on("POST", "smart_plus/ad/status/update", ok({}))
        .on("POST", V + "ad/status/update", ok({}))
        .on("POST", "smart_plus/campaign/status/update", ok({}))
    )
    tt, _ = client(mock, session_factory=writes_on)
    seed_entity(writes_on, "tiktok", "c1", ad_set_id="g1", ad_set_budget="40")
    seed_entity(writes_on, "tiktok", "c2", ad_set_id="g2", ad_set_budget="40")

    tt.update_budget("ad_set", "g1", D("45"))  # a Smart+ ad group
    lookup = query(mock.find("GET", V + "adgroup/get")[0])
    assert json.loads(lookup["filtering"]) == {"adgroup_ids": ["g1"]}
    assert "campaign_automation_type" in json.loads(lookup["fields"])
    assert body(mock.find("POST", "smart_plus/adgroup/budget/update")[0]) == {
        "advertiser_id": "700",
        "budget": [{"adgroup_id": "g1", "budget": 45.0}],
    }
    tt.update_budget("ad_set", "g2", D("45"))  # a manual ad group keeps the legacy endpoint
    assert body(mock.find("POST", V + "adgroup/budget/update")[0])["budget"] == [
        {"adgroup_id": "g2", "budget": 45.0}
    ]

    tt.set_status("ad", "sp1", EntityStatus.PAUSED)
    assert json.loads(query(mock.find("GET", V + "ad/get")[0])["filtering"]) == {
        "ad_ids_v2": ["sp1"]
    }
    assert body(mock.find("POST", "smart_plus/ad/status/update")[0]) == {
        "advertiser_id": "700",
        "smart_plus_ad_ids": ["sp1"],
        "operation_status": "DISABLE",
    }
    tt.set_status("ad", "a1", EntityStatus.PAUSED)
    assert body(mock.find("POST", V + "ad/status/update")[0]) == {
        "advertiser_id": "700",
        "ad_ids": ["a1"],
        "operation_status": "DISABLE",
    }
    tt.set_status("campaign", "c1", EntityStatus.PAUSED)
    assert body(mock.find("POST", "smart_plus/campaign/status/update")[0])["campaign_ids"] == ["c1"]


def test_unknown_country_is_a_clear_error(writes_on) -> None:  # type: ignore[no-untyped-def]
    tt, _ = client(MockHTTP(), session_factory=writes_on)
    with pytest.raises(ValueError, match="location id"):
        tt.create_campaign(CampaignSpec(name="x", daily_budget=D("10"), countries=["ZZ"]))


def test_age_groups() -> None:
    assert age_groups(None, None) == [
        "AGE_18_24",
        "AGE_25_34",
        "AGE_35_44",
        "AGE_45_54",
        "AGE_55_100",
    ]
    assert age_groups(30, 50) == ["AGE_25_34", "AGE_35_44", "AGE_45_54"]
