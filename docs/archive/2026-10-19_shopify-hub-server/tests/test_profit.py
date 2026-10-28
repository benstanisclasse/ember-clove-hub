"""Unit tests for the contribution-profit formulas in app.profit."""

from decimal import Decimal as D

import pytest

from app.profit import (
    LineCost,
    OrderMoney,
    ad_day_profit,
    order_profit,
    profit_per_thousand,
    split_across_creatives,
)


def test_basic_order() -> None:
    # $110 paid incl. $10 tax; 2 units at $20 COGS, $4/unit shipping, $3.50 fees.
    p = order_profit(
        OrderMoney(
            total_price=D("110.00"),
            total_tax=D("10.00"),
            payment_fees=D("3.50"),
            lines=[LineCost(2, [D("20.00")], [D("4.00")])],
        )
    )
    assert p.net_revenue == D("100.00")
    assert p.cogs == D("40.00")
    assert p.shipping_cost == D("8.00")
    assert p.contribution_profit == D("48.50")  # 100 - 40 - 8 - 3.50
    assert p.units == 2 and p.units_missing_cost == 0


def test_refund_excludes_refunded_tax() -> None:
    p = order_profit(
        OrderMoney(
            total_price=D("110"), total_tax=D("10"), total_refunded=D("55"), refunded_tax=D("5")
        )
    )
    assert p.refunds == D("50")
    assert p.contribution_profit == D("50")


def test_cost_fallback_order_line_then_variant_then_product() -> None:
    line = LineCost(1, [None, D("7"), D("9")], [None, None, D("2")])
    p = order_profit(OrderMoney(total_price=D("30"), lines=[line]))
    assert p.cogs == D("7")  # variant wins over product
    assert p.shipping_cost == D("2")  # product fallback


def test_missing_cost_counts_units_and_treats_cost_as_zero() -> None:
    p = order_profit(OrderMoney(total_price=D("30"), lines=[LineCost(3, [None, None])]))
    assert p.cogs == D("0")
    assert p.units_missing_cost == 3


def test_actual_shipping_cost_overrides_estimate() -> None:
    p = order_profit(
        OrderMoney(
            total_price=D("50"), shipping_cost=D("6.25"), lines=[LineCost(5, [D("1")], [D("4")])]
        )
    )
    assert p.shipping_cost == D("6.25")


def test_ad_day_profit_and_per_thousand() -> None:
    assert ad_day_profit([D("40"), D("15.5")], spend=D("30")) == D("25.5")
    assert ad_day_profit([], spend=D("12")) == D("-12")
    assert profit_per_thousand(D("25"), D("50")) == D("500")
    assert profit_per_thousand(D("25"), D("0")) is None


def test_split_across_creatives() -> None:
    assert split_across_creatives(D("30"), 3) == D("10")
    with pytest.raises(ValueError):
        split_across_creatives(D("1"), 0)
