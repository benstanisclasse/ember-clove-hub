"""Contribution-profit math.

This module is the readable, unit-tested specification of the profit numbers. The SQL
views created by migration ``0001`` (``v_order_profit``, ``v_ad_daily_profit``,
``v_creative_daily_profit``) implement exactly the same formulas in the database, and
``tests/test_profit_views.py`` checks the two agree.

Per order::

    net_revenue   = total_price - total_tax              (after discounts, incl. shipping charged)
    refunds       = total_refunded - refunded_tax
    cogs          = sum(qty * unit_cost)                 (line snapshot > variant > product > 0)
    shipping_cost = order.shipping_cost if known else sum(qty * per-unit shipping cost)
    contribution  = net_revenue - refunds - cogs - shipping_cost - payment_fees

Cancelled and test orders are excluded. Per ad per day::

    contribution_profit = sum(contribution of orders attributed to the ad that day) - spend

Per creative per day: the sum over its linked ads, with each ad's numbers split equally
across all creatives linked to that ad.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal

ZERO = Decimal("0")


@dataclass(frozen=True)
class LineCost:
    """Cost inputs for one order line, already resolved where the caller can.

    ``unit_cost`` / ``shipping_cost_per_unit`` are tried in order; the first non-None
    wins (mirroring ``COALESCE(line, variant, product)`` in SQL).
    """

    quantity: int
    unit_costs: Sequence[Decimal | None] = ()
    shipping_costs_per_unit: Sequence[Decimal | None] = ()


@dataclass(frozen=True)
class OrderMoney:
    total_price: Decimal
    total_tax: Decimal = ZERO
    total_refunded: Decimal = ZERO
    refunded_tax: Decimal = ZERO
    payment_fees: Decimal = ZERO
    shipping_cost: Decimal | None = None  # actual cost, if known
    lines: Sequence[LineCost] = ()


@dataclass(frozen=True)
class OrderProfit:
    net_revenue: Decimal
    refunds: Decimal
    cogs: Decimal
    shipping_cost: Decimal
    payment_fees: Decimal
    contribution_profit: Decimal
    units: int
    units_missing_cost: int


def _first(values: Iterable[Decimal | None]) -> Decimal | None:
    return next((v for v in values if v is not None), None)


def order_profit(order: OrderMoney) -> OrderProfit:
    """Compute contribution profit for one order."""
    cogs = ZERO
    est_shipping = ZERO
    units = 0
    missing = 0
    for line in order.lines:
        units += line.quantity
        cost = _first(line.unit_costs)
        if cost is None:
            missing += line.quantity
        else:
            cogs += line.quantity * cost
        est_shipping += line.quantity * (_first(line.shipping_costs_per_unit) or ZERO)

    shipping = order.shipping_cost if order.shipping_cost is not None else est_shipping
    net_revenue = order.total_price - order.total_tax
    refunds = order.total_refunded - order.refunded_tax
    contribution = net_revenue - refunds - cogs - shipping - order.payment_fees
    return OrderProfit(
        net_revenue=net_revenue,
        refunds=refunds,
        cogs=cogs,
        shipping_cost=shipping,
        payment_fees=order.payment_fees,
        contribution_profit=contribution,
        units=units,
        units_missing_cost=missing,
    )


def ad_day_profit(attributed_contributions: Iterable[Decimal], spend: Decimal) -> Decimal:
    """Contribution profit for one ad on one day: attributed contribution minus spend."""
    return sum(attributed_contributions, ZERO) - spend


def split_across_creatives(amount: Decimal, n_creatives: int) -> Decimal:
    """An ad's amount allocated to each of the ``n_creatives`` linked to it."""
    if n_creatives < 1:
        raise ValueError("an ad needs at least one linked creative to allocate to")
    return amount / n_creatives


def profit_per_thousand(contribution_profit: Decimal, spend: Decimal) -> Decimal | None:
    """Contribution profit per $1,000 of spend (None when nothing was spent)."""
    if spend <= 0:
        return None
    return contribution_profit / spend * 1000
