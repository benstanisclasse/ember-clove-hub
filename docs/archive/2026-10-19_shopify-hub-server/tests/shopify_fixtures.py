"""Builders for Shopify Admin GraphQL nodes shaped like real 2026-07 responses."""

from __future__ import annotations

from typing import Any


def m(amount: str | float) -> dict[str, Any]:
    return {"shopMoney": {"amount": str(amount)}}


def visit(
    landing: str | None = None, utm: dict[str, str] | None = None, referrer: str | None = None
) -> dict[str, Any]:
    return {"landingPage": landing, "referrerUrl": referrer, "source": "x", "utmParameters": utm}


def line(
    lid: int,
    qty: int,
    price: str,
    variant: int | None = 11,
    product: int | None = 1,
    cost: str | None = "7.00",
) -> dict[str, Any]:
    return {
        "id": f"gid://shopify/LineItem/{lid}",
        "name": f"Widget {lid}",
        "sku": f"W-{lid}",
        "quantity": qty,
        "originalUnitPriceSet": m(price),
        "totalDiscountSet": m("0"),
        "product": {"id": f"gid://shopify/Product/{product}"} if product else None,
        "variant": (
            {
                "id": f"gid://shopify/ProductVariant/{variant}",
                "inventoryItem": {"unitCost": {"amount": cost} if cost else None},
            }
            if variant
            else None
        ),
    }


def order(
    oid: int = 5001,
    *,
    processed_at: str = "2026-10-01T15:00:00Z",
    updated_at: str = "2026-10-01T15:05:00Z",
    total: str = "110.00",
    tax: str = "10.00",
    refunded: str = "0.00",
    customer: int | None = 9001,
    lines: list[dict[str, Any]] | None = None,
    refunds: list[dict[str, Any]] | None = None,
    transactions: list[dict[str, Any]] | None = None,
    last_visit: dict[str, Any] | None = None,
    first_visit: dict[str, Any] | None = None,
    attrs: list[dict[str, str]] | None = None,
    cancelled_at: str | None = None,
    test: bool = False,
) -> dict[str, Any]:
    return {
        "id": f"gid://shopify/Order/{oid}",
        "name": f"#{oid}",
        "createdAt": processed_at,
        "processedAt": processed_at,
        "updatedAt": updated_at,
        "cancelledAt": cancelled_at,
        "test": test,
        "sourceName": "web",
        "currencyCode": "USD",
        "displayFinancialStatus": "PAID",
        "displayFulfillmentStatus": "UNFULFILLED",
        "customer": {"id": f"gid://shopify/Customer/{customer}"} if customer else None,
        "subtotalPriceSet": m("100.00"),
        "totalDiscountsSet": m("0"),
        "totalShippingPriceSet": m("0"),
        "totalTaxSet": m(tax),
        "totalPriceSet": m(total),
        "totalRefundedSet": m(refunded),
        "customAttributes": attrs or [],
        "customerJourneySummary": {"firstVisit": first_visit, "lastVisit": last_visit},
        "lineItems": {"nodes": lines if lines is not None else [line(oid * 100 + 1, 2, "50.00")]},
        "refunds": refunds or [],
        "transactions": transactions
        if transactions is not None
        else [
            {
                "kind": "SALE",
                "status": "SUCCESS",
                "gateway": "shopify_payments",
                "amountSet": m(total),
                "fees": [{"amount": {"amount": "3.49"}}],
            }
        ],
    }


def refund(
    rid: int, amount: str, tax: str, created: str = "2026-10-03T10:00:00Z"
) -> dict[str, Any]:
    return {
        "id": f"gid://shopify/Refund/{rid}",
        "createdAt": created,
        "note": None,
        "totalRefundedSet": m(amount),
        "refundLineItems": {"nodes": [{"totalTaxSet": m(tax)}]},
    }


def product(
    pid: int = 1, variants: list[tuple[int, str, str | None]] | None = None, status: str = "ACTIVE"
) -> dict[str, Any]:
    variants = variants if variants is not None else [(11, "50.00", "7.00"), (12, "60.00", None)]
    return {
        "id": f"gid://shopify/Product/{pid}",
        "title": "Widget",
        "handle": "widget",
        "productType": "Gadgets",
        "status": status,
        "updatedAt": "2026-10-01T00:00:00Z",
        "variants": {
            "nodes": [
                {
                    "id": f"gid://shopify/ProductVariant/{vid}",
                    "sku": f"SKU-{vid}",
                    "title": f"V{vid}",
                    "price": price,
                    "inventoryItem": {"unitCost": {"amount": cost} if cost else None},
                }
                for vid, price, cost in variants
            ]
        },
    }


def page(
    connection: str, nodes: list[dict[str, Any]], next_cursor: str | None = None
) -> dict[str, Any]:
    return {
        "data": {
            connection: {
                "nodes": nodes,
                "pageInfo": {"hasNextPage": next_cursor is not None, "endCursor": next_cursor},
            }
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 50,
                "actualQueryCost": 20,
                "throttleStatus": {
                    "maximumAvailable": 2000,
                    "currentlyAvailable": 1980,
                    "restoreRate": 100,
                },
            }
        },
    }
