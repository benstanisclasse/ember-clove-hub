"""Write Shopify data into the database. Every function is idempotent (keyed on Shopify ids).

* Products: variant ``unit_cost`` tracks Shopify's current inventory cost. Product-level
  ``unit_cost`` / ``shipping_cost`` are **yours** (manual defaults) and never overwritten.
* Orders: line ``unit_cost`` is snapshotted the first time a line is seen, so editing a
  product's cost later doesn't rewrite historical profit.
* Customers: only the Shopify id is stored; aggregates are recomputed from orders.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from contextlib import AbstractContextManager
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import attribution
from app.config import Settings
from app.integrations.shopify import queries
from app.integrations.shopify.client import ShopifyClient
from app.integrations.shopify.mapping import (
    OrderData,
    ProductData,
    gid_to_int,
    order_gid,
    parse_dt,
    parse_order,
    parse_product,
    product_gid,
)
from app.log import get_logger
from app.models import Customer, Order, OrderItem, Product, ProductVariant, Refund, SyncState

log = get_logger(__name__)
SessionFactory = Callable[[], AbstractContextManager[Session]]
ORDERS_CURSOR = "shopify:orders:updated_at"
PRODUCTS_CURSOR = "shopify:products:updated_at"
CURSOR_OVERLAP = timedelta(minutes=10)  # re-read a little to never miss late writes


# --- sync state -------------------------------------------------------------------------


def get_cursor(session: Session, key: str) -> datetime | None:
    row = session.get(SyncState, key)
    return parse_dt(row.value) if row and row.value else None


def set_cursor(session: Session, key: str, value: datetime) -> None:
    row = session.get(SyncState, key) or SyncState(key=key)
    row.value = value.astimezone(UTC).isoformat()
    session.add(row)


# --- upserts ----------------------------------------------------------------------------


def upsert_product(session: Session, data: ProductData) -> Product:
    product = session.scalar(select(Product).where(Product.shopify_id == data.shopify_id))
    if product is None:
        product = Product(shopify_id=data.shopify_id, title=data.title)
        session.add(product)
    product.title = data.title
    product.handle = data.handle
    product.product_type = data.product_type
    product.active = data.active
    product.price = data.price
    product.shopify_updated_at = data.shopify_updated_at
    session.flush()

    existing = {
        v.shopify_id: v
        for v in session.scalars(
            select(ProductVariant).where(ProductVariant.product_id == product.id)
        )
    }
    seen = set()
    for v in data.variants:
        row = existing.get(v.shopify_id) or session.scalar(
            select(ProductVariant).where(ProductVariant.shopify_id == v.shopify_id)
        )
        if row is None:
            row = ProductVariant(shopify_id=v.shopify_id, product_id=product.id)
            session.add(row)
        row.product_id = product.id
        row.sku, row.title, row.price, row.active = v.sku, v.title, v.price, True
        if v.unit_cost is not None:
            row.unit_cost = v.unit_cost
        seen.add(v.shopify_id)
    for shopify_id, row in existing.items():
        if shopify_id not in seen:
            row.active = False  # deleted in Shopify; keep for historical orders
    session.flush()
    return product


def upsert_customer(session: Session, shopify_id: int) -> Customer:
    customer = session.scalar(select(Customer).where(Customer.shopify_id == shopify_id))
    if customer is None:
        customer = Customer(shopify_id=shopify_id)
        session.add(customer)
        session.flush()
    return customer


def upsert_order(session: Session, data: OrderData) -> Order:
    order = session.scalar(select(Order).where(Order.shopify_id == data.shopify_id))
    if order is None:
        order = Order(shopify_id=data.shopify_id)
        session.add(order)
    for key, value in data.columns.items():
        setattr(order, key, value)
    order.customer_id = (
        upsert_customer(session, data.customer_shopify_id).id if data.customer_shopify_id else None
    )
    session.flush()

    products = _id_map(session, Product, {li.product_shopify_id for li in data.lines})
    variants = _id_map(session, ProductVariant, {li.variant_shopify_id for li in data.lines})
    existing_lines = {
        li.shopify_id: li
        for li in session.scalars(select(OrderItem).where(OrderItem.order_id == order.id))
    }
    keep = set()
    for li in data.lines:
        row = existing_lines.get(li.shopify_id)
        if row is None:
            row = OrderItem(
                order_id=order.id, shopify_id=li.shopify_id, unit_cost=li.current_unit_cost
            )
            session.add(row)
        elif row.unit_cost is None:
            row.unit_cost = li.current_unit_cost
        row.product_id = products.get(li.product_shopify_id)
        row.variant_id = variants.get(li.variant_shopify_id)
        row.sku, row.title = li.sku, li.title
        row.quantity, row.price, row.total_discount = li.quantity, li.price, li.total_discount
        keep.add(li.shopify_id)
    for shopify_id, row in existing_lines.items():
        if shopify_id not in keep:
            session.delete(row)  # line removed by an order edit

    existing_refunds = {
        r.shopify_id: r for r in session.scalars(select(Refund).where(Refund.order_id == order.id))
    }
    for r in data.refunds:
        row = existing_refunds.get(r.shopify_id) or Refund(
            order_id=order.id, shopify_id=r.shopify_id
        )
        row.refunded_at, row.amount, row.tax_amount, row.note = (
            r.refunded_at,
            r.amount,
            r.tax_amount,
            r.note,
        )
        session.add(row)

    attribution.resolve(session, order)
    session.flush()
    return order


def _id_map(session: Session, model: Any, shopify_ids: Iterable[int | None]) -> dict[int, int]:
    ids = {i for i in shopify_ids if i}
    if not ids:
        return {}
    rows = session.execute(select(model.shopify_id, model.id).where(model.shopify_id.in_(ids)))
    return {sid: pk for sid, pk in rows}


def recompute_customers(session: Session, customer_ids: Iterable[int]) -> None:
    """Refresh customer aggregates and ``orders.is_first_order`` from live orders."""
    for cid in {c for c in customer_ids if c}:
        live = (Order.customer_id == cid, Order.cancelled_at.is_(None), Order.test.is_(False))
        first, last, count, revenue = session.execute(
            select(
                func.min(Order.placed_at),
                func.max(Order.placed_at),
                func.count(Order.id),
                func.coalesce(
                    func.sum(
                        Order.total_price
                        - Order.total_tax
                        - (Order.total_refunded - Order.refunded_tax)
                    ),
                    0,
                ),
            ).where(*live)
        ).one()
        customer = session.get(Customer, cid)
        if customer is None:
            continue
        customer.first_order_at, customer.last_order_at = first, last
        customer.order_count, customer.total_revenue = count, Decimal(str(revenue))
        first_id = session.scalar(
            select(Order.id).where(*live).order_by(Order.placed_at, Order.id).limit(1)
        )
        for order in session.scalars(select(Order).where(Order.customer_id == cid)):
            order.is_first_order = order.id == first_id
    session.flush()


# --- fetch + write ------------------------------------------------------------------------


def _parse(settings: Settings, node: dict[str, Any]) -> OrderData:
    return parse_order(
        node, settings.tz, settings.payment_fee_fallback_pct, settings.payment_fee_fallback_fixed
    )


def sync_order(client: ShopifyClient, session: Session, order_id: int) -> Order | None:
    """Fetch one order by numeric id and upsert it (used by webhooks)."""
    node = client.execute(queries.ORDER, {"id": order_gid(order_id)}).get("order")
    if not node:
        log.warning("shopify_order_not_found", order_id=order_id)
        return None
    order = upsert_order(session, _parse(client.settings, node))
    recompute_customers(session, [order.customer_id] if order.customer_id else [])
    return order


def sync_product(client: ShopifyClient, session: Session, product_id: int) -> Product | None:
    node = client.execute(queries.PRODUCT, {"id": product_gid(product_id)}).get("product")
    if not node:
        return None
    return upsert_product(session, parse_product(node))


def sync_orders(
    client: ShopifyClient,
    session_factory: SessionFactory,
    since: datetime | None = None,
    field: str = "updated_at",
    page_size: int = 25,
) -> dict[str, int]:
    """Upsert every order with ``field >= since`` (committing per page) and advance the
    cursor. With ``since=None`` it continues from the stored cursor (incremental sync)."""
    with session_factory() as s:
        since = (
            since
            or get_cursor(s, ORDERS_CURSOR)
            or (datetime.now(UTC) - timedelta(days=client.settings.shopify_backfill_days))
        )
    query = f"{field}:>='{(since - CURSOR_OVERLAP).astimezone(UTC).isoformat()}'"
    n, newest, batch = 0, since, []

    def flush(nodes: list[dict[str, Any]]) -> None:
        nonlocal newest
        with session_factory() as s:
            customers = set()
            for node in nodes:
                order = upsert_order(s, _parse(client.settings, node))
                customers.add(order.customer_id)
                if order.shopify_updated_at and order.shopify_updated_at > newest:
                    newest = order.shopify_updated_at
            recompute_customers(s, [c for c in customers if c])
            set_cursor(s, ORDERS_CURSOR, newest)

    for node in client.paginate(queries.ORDERS, {"query": query}, "orders", page_size=page_size):
        batch.append(node)
        n += 1
        if len(batch) >= page_size:
            flush(batch)
            batch = []
    if batch:
        flush(batch)
    return {"orders": n}


def sync_products(
    client: ShopifyClient, session_factory: SessionFactory, since: datetime | None = None
) -> dict[str, int]:
    """Upsert all products (or those updated since ``since``)."""
    variables = (
        {"query": f"updated_at:>='{since.astimezone(UTC).isoformat()}'"}
        if since
        else {"query": None}
    )
    n = 0
    with session_factory() as s:
        for node in client.paginate(queries.PRODUCTS, variables, "products", page_size=50):
            upsert_product(s, parse_product(node))
            n += 1
            if n % 50 == 0:
                s.commit()
        set_cursor(s, PRODUCTS_CURSOR, datetime.now(UTC))
    return {"products": n}


def sync_customers(client: ShopifyClient, session_factory: SessionFactory) -> dict[str, int]:
    """Create a row for every Shopify customer (ids only), then refresh aggregates."""
    n = 0
    with session_factory() as s:
        for node in client.paginate(queries.CUSTOMERS, {"query": None}, "customers", page_size=250):
            sid = gid_to_int(node.get("id"))
            if sid:
                upsert_customer(s, sid)
                n += 1
            if n % 500 == 0:
                s.commit()
        recompute_customers(s, s.scalars(select(Customer.id)).all())
    return {"customers": n}
