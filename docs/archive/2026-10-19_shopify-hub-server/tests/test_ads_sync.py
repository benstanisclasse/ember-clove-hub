"""Ad structure + metrics upserts, deletion marking, and the end-to-end profit view."""

from __future__ import annotations

from datetime import date
from decimal import Decimal as D
from zoneinfo import ZoneInfo

import shopify_fixtures as fx
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.integrations.ads import sync
from app.integrations.ads.base import (
    AccountInfo,
    AdInfo,
    AdSetInfo,
    CampaignInfo,
    DailyMetric,
    Structure,
)
from app.integrations.shopify import sync as shopify_sync
from app.integrations.shopify.mapping import parse_order
from app.models import Ad, AdMetricsDaily, Campaign, EntityStatus, Order, Platform

DAY = date(2026, 10, 1)


def structure(ads: list[str] = ["6001", "6002"]) -> Structure:  # noqa: B006
    return Structure(
        account=AccountInfo("123", "Shop", "USD", "America/New_York"),
        campaigns=[CampaignInfo("2385", "Fall", EntityStatus.ACTIVE, daily_budget=D("50"))],
        ad_sets=[AdSetInfo("as1", "2385", "Broad", EntityStatus.ACTIVE)],
        ads=[AdInfo(a, "as1", f"Ad {a}", EntityStatus.ACTIVE) for a in ads],
    )


def test_structure_upsert_is_idempotent_and_marks_deleted(session: Session) -> None:
    sync.upsert_structure(session, Platform.META, structure())
    sync.upsert_structure(session, Platform.META, structure())
    assert session.scalar(select(text("count(*)")).select_from(Ad)) == 2
    sync.upsert_structure(session, Platform.META, structure(ads=["6001"]))  # 6002 deleted in Meta
    statuses = {a.external_id: a.status for a in session.scalars(select(Ad))}
    assert statuses == {"6001": EntityStatus.ACTIVE, "6002": EntityStatus.DELETED}
    assert session.scalars(select(Campaign)).one().daily_budget == D("50")


def test_same_external_id_on_two_platforms_is_two_ads(session: Session) -> None:
    sync.upsert_structure(session, Platform.META, structure(ads=["1"]))
    sync.upsert_structure(session, Platform.TIKTOK, structure(ads=["1"]))
    assert session.scalar(select(text("count(*)")).select_from(Ad)) == 2


def test_metrics_upsert_replaces_not_doubles_and_counts_unknown(session: Session) -> None:
    sync.upsert_structure(session, Platform.META, structure())
    first = [
        DailyMetric("6001", DAY, spend=D("10"), impressions=100),
        DailyMetric("9999", DAY, spend=D("5")),
    ]
    assert sync.upsert_metrics(session, Platform.META, first) == {"rows": 1, "unknown_ads": 1}
    # the platform revises the numbers a day later
    sync.upsert_metrics(
        session, Platform.META, [DailyMetric("6001", DAY, spend=D("12"), impressions=130)]
    )
    row = session.scalars(select(AdMetricsDaily)).one()
    assert (row.spend, row.impressions) == (D("12"), 130)


def test_duplicate_rows_for_one_ad_day_are_summed(session: Session) -> None:
    sync.upsert_structure(session, Platform.GOOGLE, structure(ads=["c2"]))
    rows = [
        DailyMetric("c2", DAY, spend=D("3"), clicks=1),
        DailyMetric("c2", DAY, spend=D("4"), clicks=2),
    ]
    sync.upsert_metrics(session, Platform.GOOGLE, rows)
    row = session.scalars(select(AdMetricsDaily)).one()
    assert (row.spend, row.clicks) == (D("7"), 3)


class FakePlatform:
    platform = Platform.META

    def list_structure(self) -> Structure:
        return structure()

    def get_daily_metrics(self, start: date, end: date) -> list[DailyMetric]:
        assert (start, end) == (date(2026, 9, 29), DAY)
        return [
            DailyMetric(
                "6001", DAY, spend=D("40.00"), impressions=2000, clicks=50, video_3s_views=600
            )
        ]


def test_full_sync_reattributes_orders_and_feeds_profit_view(session: Session) -> None:
    # An order arrives from a Meta ad before the hub has ever synced Meta.
    node = fx.order(
        processed_at="2026-10-01T16:00:00Z",
        last_visit=fx.visit(utm={"source": "facebook", "campaign": "2385", "content": "6001"}),
    )
    order = shopify_sync.upsert_order(
        session, parse_order(node, ZoneInfo("America/New_York"), 2.9, 0.3)
    )
    session.commit()
    assert order.attributed_ad_id is None

    stats = sync.sync_platform(FakePlatform(), session, lookback_days=3, today=DAY)  # type: ignore[arg-type]
    session.commit()
    assert stats["ads"] == 2 and stats["rows"] == 1 and stats["orders_reattributed"] >= 1

    session.expire_all()
    ad = session.scalars(select(Ad).where(Ad.external_id == "6001")).one()
    assert session.get(Order, order.id).attributed_ad_id == ad.id
    row = session.execute(
        text(
            "SELECT spend, attributed_orders, attributed_contribution, contribution_profit FROM v_ad_daily_profit WHERE ad_id = :a"
        ),
        {"a": ad.id},
    ).one()
    # order: 100 net revenue - 14 COGS - 3.49 fees = 82.51 contribution; minus 40 spend
    assert row.attributed_orders == 1
    assert D(str(row.contribution_profit)).quantize(D("0.01")) == D("42.51")
