"""Pure functions turning Shopify GraphQL nodes into column dicts (no DB access)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from app.attribution import Touch, touch_from_order

ZERO = Decimal("0")
CENT = Decimal("0.01")
FEE_KINDS = {"SALE", "CAPTURE"}
NO_FEE_GATEWAYS = {"manual", "cash_on_delivery", "bogus", "gift_card", "shopify_store_credit"}


def gid_to_int(gid: str | None) -> int | None:
    """``gid://shopify/Order/123`` -> 123."""
    if not gid:
        return None
    tail = str(gid).rsplit("/", 1)[-1].split("?", 1)[0]
    return int(tail) if tail.isdigit() else None


def order_gid(order_id: int | str) -> str:
    return f"gid://shopify/Order/{order_id}"


def product_gid(product_id: int | str) -> str:
    return f"gid://shopify/Product/{product_id}"


def money(bag: dict[str, Any] | None) -> Decimal:
    """Amount from a MoneyBag (``{shopMoney: {amount}}``) or MoneyV2 (``{amount}``)."""
    if not bag:
        return ZERO
    node = bag.get("shopMoney", bag)
    raw = node.get("amount") if isinstance(node, dict) else None
    return Decimal(str(raw)) if raw not in (None, "") else ZERO


def parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def local_date(ts: datetime, tz: ZoneInfo) -> date:
    return ts.astimezone(tz).date()


# --- Products ---------------------------------------------------------------------------


@dataclass
class VariantData:
    shopify_id: int
    sku: str | None
    title: str | None
    price: Decimal | None
    unit_cost: Decimal | None


@dataclass
class ProductData:
    shopify_id: int
    title: str
    handle: str | None
    product_type: str | None
    active: bool
    price: Decimal | None
    shopify_updated_at: datetime | None
    variants: list[VariantData] = field(default_factory=list)


def parse_product(node: dict[str, Any]) -> ProductData:
    variants = []
    for v in (node.get("variants") or {}).get("nodes") or []:
        cost = ((v.get("inventoryItem") or {}).get("unitCost") or {}).get("amount")
        variants.append(
            VariantData(
                shopify_id=gid_to_int(v["id"]) or 0,
                sku=v.get("sku") or None,
                title=v.get("title"),
                price=Decimal(str(v["price"])) if v.get("price") not in (None, "") else None,
                unit_cost=Decimal(str(cost)) if cost not in (None, "") else None,
            )
        )
    prices = [v.price for v in variants if v.price is not None]
    return ProductData(
        shopify_id=gid_to_int(node["id"]) or 0,
        title=node.get("title") or "",
        handle=node.get("handle"),
        product_type=node.get("productType") or None,
        active=(node.get("status") or "ACTIVE").upper() == "ACTIVE",
        price=min(prices) if prices else None,
        shopify_updated_at=parse_dt(node.get("updatedAt")),
        variants=variants,
    )


# --- Orders -----------------------------------------------------------------------------


@dataclass
class LineData:
    shopify_id: int
    product_shopify_id: int | None
    variant_shopify_id: int | None
    sku: str | None
    title: str | None
    quantity: int
    price: Decimal
    total_discount: Decimal
    current_unit_cost: Decimal | None  # snapshotted on first insert only


@dataclass
class RefundData:
    shopify_id: int
    refunded_at: datetime
    amount: Decimal
    tax_amount: Decimal
    note: str | None


@dataclass
class OrderData:
    shopify_id: int
    columns: dict[str, Any]
    customer_shopify_id: int | None
    lines: list[LineData]
    refunds: list[RefundData]
    touch: Touch


def payment_fees(
    transactions: list[dict[str, Any]], fallback_pct: float, fallback_fixed: float
) -> Decimal:
    """Processor fees for an order.

    Shopify reports exact fees only for Shopify Payments. For other gateways (PayPal,
    Stripe, ...) estimate ``pct% + fixed`` per successful sale/capture; manual, cash and
    gift-card payments cost nothing.
    """
    ok = [t for t in transactions if t.get("status") == "SUCCESS" and t.get("kind") in FEE_KINDS]
    reported = sum((money(f.get("amount")) for t in ok for f in t.get("fees") or []), ZERO)
    if reported > 0:
        return reported.quantize(CENT)
    estimated = ZERO
    for t in ok:
        if (t.get("gateway") or "").lower() in NO_FEE_GATEWAYS:
            continue
        amount = money(t.get("amountSet"))
        if amount > 0:
            estimated += amount * Decimal(str(fallback_pct)) / 100 + Decimal(str(fallback_fixed))
    return estimated.quantize(CENT)


def parse_order(node: dict[str, Any], tz: ZoneInfo, fee_pct: float, fee_fixed: float) -> OrderData:
    placed_at = parse_dt(node.get("processedAt") or node.get("createdAt"))
    if placed_at is None:
        raise ValueError(f"order {node.get('id')} has no processedAt/createdAt")

    lines = []
    for li in (node.get("lineItems") or {}).get("nodes") or []:
        variant = li.get("variant") or {}
        cost = ((variant.get("inventoryItem") or {}).get("unitCost") or {}).get("amount")
        lines.append(
            LineData(
                shopify_id=gid_to_int(li["id"]) or 0,
                product_shopify_id=gid_to_int((li.get("product") or {}).get("id")),
                variant_shopify_id=gid_to_int(variant.get("id")),
                sku=li.get("sku") or None,
                title=li.get("name"),
                quantity=int(li.get("quantity") or 0),
                price=money(li.get("originalUnitPriceSet")),
                total_discount=money(li.get("totalDiscountSet")),
                current_unit_cost=Decimal(str(cost)) if cost not in (None, "") else None,
            )
        )

    refunds = []
    for r in node.get("refunds") or []:
        tax = sum(
            (
                money(n.get("totalTaxSet"))
                for n in (r.get("refundLineItems") or {}).get("nodes") or []
            ),
            ZERO,
        )
        refunds.append(
            RefundData(
                shopify_id=gid_to_int(r["id"]) or 0,
                refunded_at=parse_dt(r.get("createdAt")) or placed_at,
                amount=money(r.get("totalRefundedSet")),
                tax_amount=tax,
                note=r.get("note"),
            )
        )

    touch = touch_from_order(node)
    columns = {
        "name": node.get("name"),
        "placed_at": placed_at,
        "order_date": local_date(placed_at, tz),
        "currency": node.get("currencyCode") or "USD",
        "financial_status": (node.get("displayFinancialStatus") or "").lower() or None,
        "fulfillment_status": (node.get("displayFulfillmentStatus") or "").lower() or None,
        "cancelled_at": parse_dt(node.get("cancelledAt")),
        "test": bool(node.get("test")),
        "source_name": node.get("sourceName"),
        "subtotal_price": money(node.get("subtotalPriceSet")),
        "total_discounts": money(node.get("totalDiscountsSet")),
        "shipping_revenue": money(node.get("totalShippingPriceSet")),
        "total_tax": money(node.get("totalTaxSet")),
        "total_price": money(node.get("totalPriceSet")),
        "total_refunded": money(node.get("totalRefundedSet")),
        "refunded_tax": sum((r.tax_amount for r in refunds), ZERO),
        "payment_fees": payment_fees(node.get("transactions") or [], fee_pct, fee_fixed),
        "shopify_updated_at": parse_dt(node.get("updatedAt")),
        **touch.as_columns(),
    }
    return OrderData(
        shopify_id=gid_to_int(node["id"]) or 0,
        columns=columns,
        customer_shopify_id=gid_to_int((node.get("customer") or {}).get("id")),
        lines=lines,
        refunds=refunds,
        touch=touch,
    )
