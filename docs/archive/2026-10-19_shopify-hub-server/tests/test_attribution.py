"""Attribution: which visit wins, click ids vs UTMs, matching ads/campaigns by id."""

from __future__ import annotations

from zoneinfo import ZoneInfo

import shopify_fixtures as fx
from sqlalchemy.orm import Session

from app.attribution import platform_for, reattribute, touch_from_order
from app.integrations.shopify import sync
from app.integrations.shopify.mapping import parse_order
from app.models import Ad, AdAccount, AdSet, AttributionMethod, Campaign, Order, Platform

NY = ZoneInfo("America/New_York")


def test_last_visit_wins_as_a_whole() -> None:
    node = fx.order(
        first_visit=fx.visit(utm={"source": "google", "campaign": "g1"}),
        last_visit=fx.visit(utm={"source": "facebook", "campaign": "m1", "content": "ad9"}),
    )
    t = touch_from_order(node)
    assert (t.utm_source, t.utm_campaign, t.utm_content) == ("facebook", "m1", "ad9")
    assert platform_for(t) == (Platform.META, AttributionMethod.UTM)


def test_falls_back_to_first_visit_then_cart_attributes() -> None:
    t = touch_from_order(
        fx.order(
            last_visit=fx.visit("https://shop.com/"), first_visit=fx.visit(utm={"source": "tiktok"})
        )
    )
    assert t.utm_source == "tiktok"
    assert t.landing_site == "https://shop.com/"  # most recent landing page kept

    t = touch_from_order(
        fx.order(
            attrs=[{"key": "utm_source", "value": "ig"}, {"key": "utm_content", "value": "123"}]
        )
    )
    assert (t.utm_source, t.utm_content) == ("ig", "123")
    assert platform_for(t)[0] == Platform.META


def test_click_id_from_landing_url_beats_utm_source() -> None:
    node = fx.order(
        last_visit=fx.visit(
            "https://shop.com/p?utm_source=newsletter&ttclid=E.C.P.abc",
            utm={"source": "newsletter"},
        )
    )
    t = touch_from_order(node)
    assert t.ttclid == "E.C.P.abc"
    assert platform_for(t) == (Platform.TIKTOK, AttributionMethod.CLICK_ID)


def test_gbraid_stored_as_google_click() -> None:
    t = touch_from_order(fx.order(last_visit=fx.visit("https://shop.com/?gbraid=0AAAA")))
    assert platform_for(t) == (Platform.GOOGLE, AttributionMethod.CLICK_ID)
    assert t.as_columns()["gclid"] == "0AAAA"


def test_no_signal_is_unattributed() -> None:
    t = touch_from_order(
        fx.order(last_visit=fx.visit("https://shop.com/", referrer="https://duckduckgo.com"))
    )
    assert platform_for(t) == (None, AttributionMethod.NONE)
    assert t.referring_site == "https://duckduckgo.com"


def _meta_ad(session: Session) -> Ad:
    acct = AdAccount(platform=Platform.META, external_id="act_1")
    camp = Campaign(ad_account=acct, platform=Platform.META, external_id="2385", name="Fall promo")
    ad = Ad(
        ad_set=AdSet(campaign=camp, platform=Platform.META, external_id="as1"),
        platform=Platform.META,
        external_id="6001",
    )
    session.add(ad)
    session.flush()
    return ad


def test_resolve_matches_ad_and_campaign_by_id(session: Session) -> None:
    ad = _meta_ad(session)
    node = fx.order(
        last_visit=fx.visit(utm={"source": "facebook", "campaign": "2385", "content": "6001"})
    )
    order = sync.upsert_order(session, parse_order(node, NY, 2.9, 0.3))
    assert order.attributed_ad_id == ad.id
    assert order.attributed_campaign_id == ad.ad_set.campaign_id
    assert order.attributed_platform == Platform.META


def test_platform_inferred_from_ad_when_source_unknown(session: Session) -> None:
    ad = _meta_ad(session)
    node = fx.order(last_visit=fx.visit(utm={"source": "partner-x", "content": "6001"}))
    order = sync.upsert_order(session, parse_order(node, NY, 2.9, 0.3))
    assert (order.attributed_platform, order.attributed_ad_id) == (Platform.META, ad.id)


def test_reattribute_picks_up_ads_synced_later_and_respects_manual(session: Session) -> None:
    node = fx.order(1, last_visit=fx.visit(utm={"source": "facebook", "content": "6001"}))
    o1 = sync.upsert_order(session, parse_order(node, NY, 2.9, 0.3))
    o2 = sync.upsert_order(
        session,
        parse_order(
            fx.order(2, last_visit=fx.visit(utm={"source": "facebook", "content": "6001"})),
            NY,
            2.9,
            0.3,
        ),
    )
    o2.attribution_method = AttributionMethod.MANUAL
    assert o1.attributed_ad_id is None  # ad not synced yet
    ad = _meta_ad(session)
    reattribute(session)
    session.flush()
    assert session.get(Order, o1.id).attributed_ad_id == ad.id
    assert session.get(Order, o2.id).attributed_ad_id is None
