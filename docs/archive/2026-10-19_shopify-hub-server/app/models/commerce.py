"""Shopify-side tables: products, variants, customers, orders, line items, refunds.

Shopify orders are the source of truth for revenue and profit everywhere in the hub;
platform-reported conversions are stored separately (``ad_metrics_daily``) and only
used for diagnostics.

No customer PII (names, emails, addresses) is stored -- it isn't needed for profit
math or ML, and keeping it out shrinks the blast radius of a leaked backup.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    AttributionMethod,
    Base,
    BigIntPK,
    JSONType,
    Money,
    Platform,
    TimestampMixin,
    str_enum,
)


class Product(TimestampMixin, Base):
    """A Shopify product. Costs here are defaults for variants that don't set their own."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    shopify_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    handle: Mapped[str | None] = mapped_column(String(255))
    product_type: Mapped[str | None] = mapped_column(String(255))
    price: Mapped[Decimal | None] = mapped_column(Money, comment="Lowest variant price")
    unit_cost: Mapped[Decimal | None] = mapped_column(Money, comment="COGS per unit")
    shipping_cost: Mapped[Decimal | None] = mapped_column(
        Money, comment="Our fulfilment cost per unit (not what the customer pays)"
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    shopify_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    variants: Mapped[list[ProductVariant]] = relationship(back_populates="product")


class ProductVariant(TimestampMixin, Base):
    """A purchasable SKU. ``unit_cost`` comes from Shopify's inventory item cost."""

    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    shopify_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    sku: Mapped[str | None] = mapped_column(String(255), index=True)
    title: Mapped[str | None] = mapped_column(String(512))
    price: Mapped[Decimal | None] = mapped_column(Money)
    unit_cost: Mapped[Decimal | None] = mapped_column(Money)
    shipping_cost: Mapped[Decimal | None] = mapped_column(Money)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    product: Mapped[Product] = relationship(back_populates="variants")


class Customer(TimestampMixin, Base):
    """Aggregates per Shopify customer (no PII)."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    shopify_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_order_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_order_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    order_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_revenue: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)


class Order(TimestampMixin, Base):
    """A Shopify order with the money fields needed for contribution profit.

    Money semantics (all in ``currency``, the shop currency):

    * ``total_price``   -- what the customer paid, after discounts, incl. shipping + tax
    * ``total_tax``     -- tax included in ``total_price`` (removed from revenue)
    * ``total_refunded`` / ``refunded_tax`` -- sums over ``refunds`` (gross / tax part)
    * ``payment_fees``  -- processor fees from Shopify transactions
    * ``shipping_cost`` -- *our* actual shipping cost if known; otherwise the view
      estimates it from per-unit product/variant ``shipping_cost``.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    shopify_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(64), comment="e.g. #1001")
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), index=True
    )
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    order_date: Mapped[date] = mapped_column(
        Date, index=True, nullable=False, comment="placed_at in the store timezone"
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    financial_status: Mapped[str | None] = mapped_column(String(32))
    fulfillment_status: Mapped[str | None] = mapped_column(String(32))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    test: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_name: Mapped[str | None] = mapped_column(String(64))
    is_first_order: Mapped[bool | None] = mapped_column(Boolean)

    subtotal_price: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    total_discounts: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    shipping_revenue: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    total_tax: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    total_refunded: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    refunded_tax: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    payment_fees: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    shipping_cost: Mapped[Decimal | None] = mapped_column(Money)

    # Attribution inputs (from landing_site / customerJourney)
    landing_site: Mapped[str | None] = mapped_column(Text)
    referring_site: Mapped[str | None] = mapped_column(Text)
    utm_source: Mapped[str | None] = mapped_column(String(255))
    utm_medium: Mapped[str | None] = mapped_column(String(255))
    utm_campaign: Mapped[str | None] = mapped_column(String(255))
    utm_content: Mapped[str | None] = mapped_column(String(255))
    utm_term: Mapped[str | None] = mapped_column(String(255))
    gclid: Mapped[str | None] = mapped_column(String(255), index=True)
    fbclid: Mapped[str | None] = mapped_column(String(512), index=True)
    ttclid: Mapped[str | None] = mapped_column(String(255), index=True)

    # Attribution result (filled by the attribution step)
    attributed_platform: Mapped[Platform | None] = mapped_column(str_enum(Platform, "platform"))
    attributed_campaign_id: Mapped[int | None] = mapped_column(
        ForeignKey("campaigns.id", ondelete="SET NULL"), index=True
    )
    attributed_ad_id: Mapped[int | None] = mapped_column(
        ForeignKey("ads.id", ondelete="SET NULL"), index=True
    )
    attribution_method: Mapped[AttributionMethod] = mapped_column(
        str_enum(AttributionMethod, "attribution_method"),
        default=AttributionMethod.NONE,
        nullable=False,
    )

    raw: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    shopify_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    refunds: Mapped[list[Refund]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """An order line. ``unit_cost`` is snapshotted at ingest so later cost edits don't
    rewrite historical profit; NULL falls back to the variant / product cost."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    shopify_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL"), index=True
    )
    sku: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(512))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Money, nullable=False, comment="Unit price")
    total_discount: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    unit_cost: Mapped[Decimal | None] = mapped_column(Money)

    order: Mapped[Order] = relationship(back_populates="items")


class Refund(Base):
    """A Shopify refund. ``amount`` is gross (incl. tax); ``tax_amount`` is the tax part."""

    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    shopify_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    refunded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Money, nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    order: Mapped[Order] = relationship(back_populates="refunds")
