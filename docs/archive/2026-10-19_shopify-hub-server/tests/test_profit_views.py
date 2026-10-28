"""The SQL profit views must agree with app.profit, on SQLite and on Postgres."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal as D
from itertools import count

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    Ad,
    AdAccount,
    AdMetricsDaily,
    AdSet,
    Campaign,
    Creative,
    CreativeAdLink,
    CreativeType,
    Order,
    OrderItem,
    Platform,
    Product,
    ProductVariant,
)
from app.profit import LineCost, OrderMoney, ad_day_profit, order_profit

_ids = count(1000)
DAY1, DAY2 = date(2026, 10, 1), date(2026, 10, 2)


def _ad(session: Session, external_id: str) -> Ad:
    acct = AdAccount(platform=Platform.META, external_id=f"act_{external_id}")
    camp = Campaign(ad_account=acct, platform=Platform.META, external_id=f"c_{external_id}")
    ad_set = AdSet(campaign=camp, platform=Platform.META, external_id=f"as_{external_id}")
    ad = Ad(ad_set=ad_set, platform=Platform.META, external_id=external_id)
    session.add(ad)
    session.flush()
    return ad


def _order(session: Session, day: date, ad: Ad | None = None, **money: object) -> Order:
    order = Order(
        shopify_id=next(_ids),
        placed_at=datetime(day.year, day.month, day.day, 12, tzinfo=UTC),
        order_date=day,
        currency="USD",
        attributed_ad_id=ad.id if ad else None,
        attributed_platform=ad.platform if ad else None,
        **money,
    )
    session.add(order)
    session.flush()
    return order


def _view(session: Session, sql: str) -> list[dict[str, object]]:
    return [dict(r._mapping) for r in session.execute(text(sql))]


def _d(value: object) -> D:
    """Normalize SQLite floats / Postgres Decimals for comparison."""
    return D(str(value)).quantize(D("0.01"))


@pytest.fixture
def catalog(session: Session) -> tuple[Product, ProductVariant, ProductVariant]:
    product = Product(shopify_id=1, title="Widget", unit_cost=D("9.00"), shipping_cost=D("3.00"))
    with_cost = ProductVariant(product=product, shopify_id=11, unit_cost=D("7.00"))
    no_cost = ProductVariant(product=product, shopify_id=12)  # falls back to product
    session.add_all([product, with_cost, no_cost])
    session.flush()
    return product, with_cost, no_cost


def test_order_view_matches_python(session: Session, catalog: tuple) -> None:
    _product, with_cost, no_cost = catalog
    order = _order(
        session,
        DAY1,
        total_price=D("121.00"),
        total_tax=D("11.00"),
        total_refunded=D("22.00"),
        refunded_tax=D("2.00"),
        payment_fees=D("3.81"),
    )
    session.add_all(
        [
            # snapshot cost wins over variant + product
            OrderItem(
                order=order,
                shopify_id=next(_ids),
                variant_id=with_cost.id,
                quantity=1,
                price=D("40"),
                unit_cost=D("6.50"),
            ),
            # variant cost
            OrderItem(
                order=order,
                shopify_id=next(_ids),
                variant_id=with_cost.id,
                quantity=2,
                price=D("40"),
            ),
            # product cost via variant's product
            OrderItem(
                order=order, shopify_id=next(_ids), variant_id=no_cost.id, quantity=1, price=D("30")
            ),
        ]
    )
    session.commit()

    expected = order_profit(
        OrderMoney(
            total_price=D("121.00"),
            total_tax=D("11.00"),
            total_refunded=D("22.00"),
            refunded_tax=D("2.00"),
            payment_fees=D("3.81"),
            lines=[
                LineCost(1, [D("6.50"), D("7.00"), D("9.00")], [None, None, D("3.00")]),
                LineCost(2, [None, D("7.00"), D("9.00")], [None, None, D("3.00")]),
                LineCost(1, [None, None, D("9.00")], [None, None, D("3.00")]),
            ],
        )
    )
    (row,) = _view(session, "SELECT * FROM v_order_profit")
    assert _d(row["net_revenue"]) == expected.net_revenue == D("110.00")
    assert _d(row["refunds"]) == expected.refunds == D("20.00")
    assert _d(row["cogs"]) == expected.cogs == D("29.50")
    assert _d(row["shipping_cost"]) == expected.shipping_cost == D("12.00")
    assert _d(row["contribution_profit"]) == expected.contribution_profit == D("44.69")
    assert row["units"] == 4 and row["units_missing_cost"] == 0


def test_cancelled_and_test_orders_excluded(session: Session) -> None:
    _order(session, DAY1, total_price=D("10"))
    _order(session, DAY1, total_price=D("10"), test=True)
    _order(session, DAY1, total_price=D("10"), cancelled_at=datetime(2026, 10, 1, tzinfo=UTC))
    session.commit()
    assert len(_view(session, "SELECT order_id FROM v_order_profit")) == 1


def test_ad_daily_profit_includes_spend_only_and_orders_only_days(session: Session) -> None:
    ad = _ad(session, "ad1")
    session.add(
        AdMetricsDaily(ad_id=ad.id, date=DAY1, spend=D("30.00"), impressions=1000, clicks=20)
    )
    o1 = _order(session, DAY1, ad, total_price=D("50.00"))
    o2 = _order(session, DAY2, ad, total_price=D("20.00"))  # no spend row that day
    session.commit()

    rows = {r["date"]: r for r in _view(session, "SELECT * FROM v_ad_daily_profit ORDER BY date")}
    rows = {(d if isinstance(d, date) else date.fromisoformat(d)): r for d, r in rows.items()}
    assert set(rows) == {DAY1, DAY2}
    assert _d(rows[DAY1]["contribution_profit"]) == ad_day_profit([D("50.00")], D("30.00"))
    assert _d(rows[DAY2]["spend"]) == D("0.00")
    assert _d(rows[DAY2]["contribution_profit"]) == D("20.00")
    assert rows[DAY1]["attributed_orders"] == 1
    assert {o1.id, o2.id}  # orders exist


def test_creative_view_splits_shared_ad_equally(session: Session) -> None:
    ad = _ad(session, "ad2")
    session.add(AdMetricsDaily(ad_id=ad.id, date=DAY1, spend=D("40.00"), impressions=1000))
    _order(session, DAY1, ad, total_price=D("100.00"))
    c1, c2 = Creative(type=CreativeType.VIDEO), Creative(type=CreativeType.IMAGE)
    session.add_all([c1, c2])
    session.flush()
    for c in (c1, c2):
        session.add(
            CreativeAdLink(
                creative_id=c.id, ad_id=ad.id, platform=Platform.META, external_ad_id="ad2"
            )
        )
    session.commit()

    rows = _view(session, "SELECT * FROM v_creative_daily_profit ORDER BY creative_id")
    assert len(rows) == 2
    for r in rows:
        assert _d(r["spend"]) == D("20.00")
        assert _d(r["impressions"]) == D("500.00")
        assert _d(r["contribution_profit"]) == D("30.00")  # (100 - 40) / 2
