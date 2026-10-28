"""Shopify mapping + DB sync: money, COGS snapshots, refunds, customers, cursors, views."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime
from decimal import Decimal as D
from typing import Any
from zoneinfo import ZoneInfo

import shopify_fixtures as fx
from sqlalchemy import Engine, select, text
from sqlalchemy.orm import Session

from app.config import Settings
from app.integrations.shopify import sync
from app.integrations.shopify.mapping import parse_order, parse_product, payment_fees
from app.models import Customer, Order, OrderItem, Product, ProductVariant, Refund

NY = ZoneInfo("America/New_York")


def parse(node: dict[str, Any]) -> Any:
    return parse_order(node, NY, 2.9, 0.30)


# --- mapping -------------------------------------------------------------------------------


def test_parse_order_money_and_local_date() -> None:
    # 02:30 UTC on Oct 2 is still Oct 1 in New York
    data = parse(
        fx.order(
            processed_at="2026-10-02T02:30:00Z",
            refunds=[fx.refund(1, "22.00", "2.00")],
            refunded="22.00",
        )
    )
    c = data.columns
    assert c["order_date"] == date(2026, 10, 1)
    assert c["total_price"] == D("110.00") and c["total_tax"] == D("10.00")
    assert c["total_refunded"] == D("22.00") and c["refunded_tax"] == D("2.00")
    assert c["payment_fees"] == D("3.49")
    assert data.customer_shopify_id == 9001
    assert data.lines[0].current_unit_cost == D("7.00") and data.lines[0].quantity == 2


def test_payment_fee_fallback_and_free_gateways() -> None:
    paypal = [
        {
            "kind": "SALE",
            "status": "SUCCESS",
            "gateway": "paypal",
            "amountSet": fx.m("100"),
            "fees": [],
        }
    ]
    assert payment_fees(paypal, 3.49, 0.49) == D("3.98")
    manual = [
        {
            "kind": "SALE",
            "status": "SUCCESS",
            "gateway": "manual",
            "amountSet": fx.m("100"),
            "fees": [],
        }
    ]
    assert payment_fees(manual, 2.9, 0.30) == D("0.00")
    failed = [
        {
            "kind": "SALE",
            "status": "FAILURE",
            "gateway": "paypal",
            "amountSet": fx.m("100"),
            "fees": [],
        }
    ]
    assert payment_fees(failed, 2.9, 0.30) == D("0.00")


def test_parse_product_marks_status_and_costs() -> None:
    p = parse_product(fx.product(status="DRAFT"))
    assert p.active is False and p.price == D("50.00")
    assert [v.unit_cost for v in p.variants] == [D("7.00"), None]


# --- upserts -------------------------------------------------------------------------------


def test_upsert_product_keeps_manual_product_costs(session: Session) -> None:
    sync.upsert_product(session, parse_product(fx.product()))
    prod = session.scalars(select(Product)).one()
    prod.unit_cost, prod.shipping_cost = D("9.00"), D("3.00")  # set by you, manually
    sync.upsert_product(session, parse_product(fx.product(variants=[(11, "55.00", "7.50")])))
    session.commit()
    assert (prod.unit_cost, prod.shipping_cost) == (D("9.00"), D("3.00"))
    variants = {v.shopify_id: v for v in session.scalars(select(ProductVariant))}
    assert variants[11].unit_cost == D("7.50") and variants[11].price == D("55.00")
    assert variants[12].active is False  # removed from Shopify


def test_upsert_order_is_idempotent_and_snapshots_cost(session: Session) -> None:
    sync.upsert_product(session, parse_product(fx.product()))
    sync.upsert_order(session, parse(fx.order(lines=[fx.line(1, 2, "50.00", cost="7.00")])))
    # Cost goes up later in Shopify; re-syncing the old order must keep the original COGS.
    sync.upsert_order(session, parse(fx.order(lines=[fx.line(1, 2, "50.00", cost="9.99")])))
    session.commit()
    assert session.scalar(select(text("count(*)")).select_from(Order)) == 1
    item = session.scalars(select(OrderItem)).one()
    assert item.unit_cost == D("7.00")
    assert item.variant_id is not None and item.product_id is not None


def test_order_edit_removes_lines_and_adds_refunds(session: Session) -> None:
    sync.upsert_order(session, parse(fx.order(lines=[fx.line(1, 1, "50"), fx.line(2, 1, "50")])))
    sync.upsert_order(
        session,
        parse(
            fx.order(
                lines=[fx.line(1, 1, "50")],
                refunds=[fx.refund(77, "55.00", "5.00")],
                refunded="55.00",
            )
        ),
    )
    session.commit()
    assert [i.shopify_id for i in session.scalars(select(OrderItem))] == [1]
    r = session.scalars(select(Refund)).one()
    assert (r.amount, r.tax_amount) == (D("55.00"), D("5.00"))


def test_customer_aggregates_and_first_order(session: Session) -> None:
    for oid, ts in ((1, "2026-09-01T12:00:00Z"), (2, "2026-10-01T12:00:00Z")):
        sync.upsert_order(session, parse(fx.order(oid, processed_at=ts)))
    sync.upsert_order(
        session,
        parse(
            fx.order(3, processed_at="2026-08-01T12:00:00Z", cancelled_at="2026-08-02T00:00:00Z")
        ),
    )
    cust = session.scalars(select(Customer)).one()
    sync.recompute_customers(session, [cust.id])
    session.commit()
    assert cust.order_count == 2  # cancelled order excluded
    assert cust.total_revenue == D("200.00")  # 2 x (110 - 10)
    firsts = {o.shopify_id: o.is_first_order for o in session.scalars(select(Order))}
    assert firsts == {1: True, 2: False, 3: False}


def test_synced_order_flows_into_profit_view(session: Session) -> None:
    sync.upsert_product(session, parse_product(fx.product()))
    sync.upsert_order(session, parse(fx.order()))
    session.commit()
    row = session.execute(
        text("SELECT contribution_profit, cogs, payment_fees FROM v_order_profit")
    ).one()
    # 100 net revenue - 14 COGS (2 x 7) - 0 shipping - 3.49 fees
    assert D(str(row.cogs)).quantize(D("0.01")) == D("14.00")
    assert D(str(row.contribution_profit)).quantize(D("0.01")) == D("82.51")


# --- incremental sync with a fake client ----------------------------------------------------


class FakeClient:
    def __init__(self, nodes: list[dict[str, Any]]) -> None:
        self.nodes = nodes
        self.settings = Settings(store_timezone="America/New_York", shopify_backfill_days=30)
        self.queries: list[str] = []

    def paginate(
        self, query: str, variables: dict[str, Any], connection: str, page_size: int = 50
    ) -> Iterator[dict[str, Any]]:
        self.queries.append(variables.get("query") or "")
        yield from self.nodes


def factory_for(engine: Engine):  # type: ignore[no-untyped-def]
    @contextmanager
    def _scope() -> Iterator[Session]:
        with Session(engine, expire_on_commit=False) as s:
            yield s
            s.commit()

    return _scope


def test_sync_orders_advances_cursor_with_overlap(engine: Engine) -> None:
    nodes = [fx.order(i, updated_at=f"2026-10-0{i}T10:00:00Z") for i in (1, 2, 3)]
    client = FakeClient(nodes)
    out = sync.sync_orders(client, factory_for(engine), page_size=2)  # type: ignore[arg-type]
    assert out == {"orders": 3}
    with Session(engine) as s:
        assert sync.get_cursor(s, sync.ORDERS_CURSOR) == datetime(2026, 10, 3, 10, tzinfo=UTC)
    # next run starts from the stored cursor minus the 10-minute overlap
    sync.sync_orders(FakeClient([]), factory_for(engine))  # type: ignore[arg-type]
    with Session(engine) as s:
        assert sync.get_cursor(s, sync.ORDERS_CURSOR) == datetime(2026, 10, 3, 10, tzinfo=UTC)
    second = FakeClient([])
    sync.sync_orders(second, factory_for(engine))  # type: ignore[arg-type]
    assert second.queries == ["updated_at:>='2026-10-03T09:50:00+00:00'"]
