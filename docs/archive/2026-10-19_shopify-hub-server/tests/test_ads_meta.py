"""Meta Marketing API client against a scripted transport."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import date
from decimal import Decimal as D

import httpx
import pytest
from ads_mock import MockHTTP, form, query
from conftest import seed_entity
from pydantic import SecretStr

from app.actions import WritesBlockedError
from app.config import Settings
from app.integrations.ads.base import AdSpec, CampaignSpec
from app.integrations.ads.meta import MetaAds
from app.integrations.http import IntegrationError, NotConfiguredError
from app.models import EntityStatus

ACCOUNT = {
    "id": "act_123",
    "name": "Shop",
    "currency": "USD",
    "timezone_name": "America/New_York",
    "account_status": 1,
}


def settings(**kw: object) -> Settings:
    base = dict(
        meta_system_user_token=SecretStr("EAAtoken123"),
        meta_ad_account_id="act_123",
        meta_app_secret=SecretStr("appsecret"),
        meta_page_id="555",
        meta_pixel_id="777",
    )
    return Settings(**{**base, **kw})  # type: ignore[arg-type]


def client(mock: MockHTTP, session_factory=None, **kw: object) -> tuple[MetaAds, list[float]]:  # type: ignore[no-untyped-def]
    slept: list[float] = []
    extra = {"session_factory": session_factory} if session_factory else {}
    return MetaAds(settings(**kw), http=mock.client(), sleep=slept.append, **extra), slept


def test_not_configured() -> None:
    with pytest.raises(NotConfiguredError):
        MetaAds(Settings(meta_system_user_token=SecretStr("")))


def test_structure_paging_budgets_and_status() -> None:
    # page-2 route first: the page-1 route's substring also matches the "next" URL
    mock = MockHTTP().on(
        "GET",
        "campaigns?after=x",
        {"data": [{"id": "c2", "name": "Old", "effective_status": "CAMPAIGN_PAUSED"}]},
    )
    mock.on(
        "GET",
        "/act_123/campaigns",
        {
            "data": [
                {
                    "id": "c1",
                    "name": "Sales",
                    "effective_status": "ACTIVE",
                    "objective": "OUTCOME_SALES",
                    "daily_budget": "5000",
                }
            ],
            "paging": {
                "next": "https://graph.facebook.com/v26.0/act_123/campaigns?after=x&access_token=EAAtoken123"
            },
        },
    )
    mock.on(
        "GET",
        "/act_123/adsets",
        {"data": [{"id": "s1", "campaign_id": "c1", "effective_status": "ACTIVE"}]},
    )
    mock.on(
        "GET",
        "/act_123/ads",
        {"data": [{"id": "a1", "adset_id": "s1", "effective_status": "DISAPPROVED"}]},
    )
    mock.on("GET", "/act_123", ACCOUNT)
    meta, _ = client(mock)
    st = meta.list_structure()
    assert [c.external_id for c in st.campaigns] == ["c1", "c2"]
    assert st.campaigns[0].daily_budget == D("50") and st.campaigns[1].status == EntityStatus.PAUSED
    assert st.ads[0].status == EntityStatus.REJECTED
    assert st.account.timezone == "America/New_York"
    # page 2 must be fetched with the cursor from paging.next intact
    assert "after=x" in str(mock.find("GET", "campaigns?after=x")[0].url)
    assert len(mock.find("GET", "/act_123/campaigns")) == 2
    # appsecret_proof = HMAC-SHA256(token, app secret)
    q = query(mock.calls[0])
    assert (
        q["appsecret_proof"] == hmac.new(b"appsecret", b"EAAtoken123", hashlib.sha256).hexdigest()
    )


def test_insights_pick_one_action_type_without_double_counting() -> None:
    row = {
        "ad_id": "a1",
        "date_start": "2026-10-01",
        "spend": "12.34",
        "impressions": "1000",
        "inline_link_clicks": "25",
        "actions": [
            {"action_type": "omni_purchase", "value": "3"},
            {"action_type": "purchase", "value": "3"},
            {"action_type": "offsite_conversion.fb_pixel_purchase", "value": "3"},
            {"action_type": "video_view", "value": "400"},
            {"action_type": "add_to_cart", "value": "9"},
        ],
        "action_values": [
            {"action_type": "omni_purchase", "value": "150.00"},
            {"action_type": "purchase", "value": "150.00"},
        ],
    }
    mock = MockHTTP().on("GET", "/insights", {"data": [row]})
    meta, _ = client(mock)
    (m,) = meta.get_daily_metrics(date(2026, 10, 1), date(2026, 10, 1))
    assert (m.spend, m.impressions, m.clicks) == (D("12.34"), 1000, 25)
    assert (m.purchases, m.platform_revenue, m.video_3s_views, m.add_to_cart) == (
        3,
        D("150.00"),
        400,
        9,
    )
    q = query(mock.calls[0])
    assert q["level"] == "ad" and q["time_increment"] == "1"
    assert json.loads(q["time_range"]) == {"since": "2026-10-01", "until": "2026-10-01"}


def test_rate_limit_backs_off_then_succeeds() -> None:
    limited = httpx.Response(
        400, json={"error": {"code": 17, "message": "User request limit reached"}}
    )
    mock = MockHTTP().on("GET", "/act_123", [limited, ACCOUNT])
    meta, slept = client(mock)
    assert meta.get_account().name == "Shop"
    assert len(slept) == 1


def test_bad_token_fails_fast_without_leaking_it() -> None:
    bad = httpx.Response(
        400, json={"error": {"code": 190, "message": "Error validating access token"}}
    )
    meta, slept = client(MockHTTP().on("GET", "/act_123", bad))
    with pytest.raises(IntegrationError, match="token rejected") as exc:
        meta.get_account()
    assert slept == [] and "EAAtoken123" not in str(exc.value)


def test_writes_blocked_in_read_only_mode(session_factory) -> None:  # type: ignore[no-untyped-def]
    mock = MockHTTP()
    meta, _ = client(mock, session_factory=session_factory)
    with pytest.raises(WritesBlockedError):
        meta.update_budget("campaign", "c1", D("75"))
    assert mock.calls == []  # nothing reached Meta


def test_budget_update_and_status_when_allowed(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = MockHTTP().on("GET", "/act_123", ACCOUNT).on("POST", "/c1", {"success": True})
    meta, _ = client(mock, session_factory=writes_on)
    seed_entity(writes_on, "meta", "c1", budget="70.00")
    meta.update_budget("campaign", "c1", D("75.50"))
    meta.set_status("campaign", "c1", EntityStatus.PAUSED)
    posts = mock.find("POST", "/c1")
    assert form(posts[0]) == {"daily_budget": "7550"}
    assert form(posts[1]) == {"status": "PAUSED"}
    with pytest.raises(WritesBlockedError, match="campaigns or ad sets"):  # guardrail fires first
        meta.update_budget("ad", "a1", D("10"))


def test_create_campaign_and_video_ad_shapes(writes_on) -> None:  # type: ignore[no-untyped-def]
    mock = (
        MockHTTP()
        .on("GET", "/act_123", ACCOUNT)
        .on("POST", "/act_123/campaigns", {"id": "c9"})
        .on("POST", "/act_123/adsets", {"id": "s9"})
        .on("POST", "/act_123/adcreatives", {"id": "cr9"})
        .on("POST", "/act_123/ads", {"id": "a9"})
    )
    meta, _ = client(mock, session_factory=writes_on)
    created = meta.create_campaign(
        CampaignSpec(name="UGC test", daily_budget=D("40"), countries=["US", "CA"])
    )
    assert (created.campaign_id, created.ad_set_id) == ("c9", "s9")
    camp = form(mock.find("POST", "/act_123/campaigns")[0])
    assert (
        camp["status"] == "PAUSED"
        and camp["daily_budget"] == "4000"
        and camp["objective"] == "OUTCOME_SALES"
    )
    adset = form(mock.find("POST", "/act_123/adsets")[0])
    assert json.loads(adset["promoted_object"]) == {
        "pixel_id": "777",
        "custom_event_type": "PURCHASE",
    }
    assert json.loads(adset["targeting"])["geo_locations"]["countries"] == ["US", "CA"]

    spec = AdSpec(
        ad_set_id="s9",
        name="Hook A",
        landing_url="https://shop.com/p",
        primary_text="Try it",
        video_asset_id="v1",
        image_asset_id="hash1",
    )
    assert meta.create_ad(spec) == "a9"
    story = json.loads(form(mock.find("POST", "/act_123/adcreatives")[0])["object_story_spec"])
    assert story["page_id"] == "555" and story["video_data"]["video_id"] == "v1"
    assert story["video_data"]["call_to_action"]["value"]["link"] == "https://shop.com/p"
    ad_post = form(mock.find("POST", "/act_123/ads?")[0])
    assert ad_post["status"] == "PAUSED" and json.loads(ad_post["creative"]) == {
        "creative_id": "cr9"
    }

    with pytest.raises(ValueError, match="thumbnail"):
        meta.create_ad(
            AdSpec(ad_set_id="s9", name="x", landing_url="u", primary_text="t", video_asset_id="v1")
        )


def test_upload_image_returns_hash(writes_on) -> None:  # type: ignore[no-untyped-def]
    from app.integrations.ads.base import MediaUpload

    mock = MockHTTP().on("POST", "/adimages", {"images": {"a.png": {"hash": "abc123"}}})
    meta, _ = client(mock, session_factory=writes_on)
    assert meta.upload_image(MediaUpload("a.png", b"\x89PNG", "image/png")) == "abc123"
