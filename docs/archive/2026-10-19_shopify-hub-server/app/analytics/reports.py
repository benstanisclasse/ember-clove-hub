"""Pre-computed reports. Every number is in the store currency (``currency``) unless the key
says otherwise (``_pct``, ``_count``, ``ratio``), and every report states its date range.

Contribution profit always comes from Shopify orders (the profit views); platform-reported
conversions appear only as ``platform_*`` diagnostics.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import business_settings
from app.analytics.periods import Period
from app.config import Settings, get_settings
from app.models import (
    ApprovalStatus,
    Creative,
    CreativeStatus,
    CreativeTrait,
    GenerationJob,
    OrderItem,
    PendingApproval,
    Product,
)

# Minimum data before a creative / trait is judged on ratios (Phase 7 reuses these).
MIN_SPEND = Decimal("50")
MIN_IMPRESSIONS = 2000
TRAITS = ("hook_type", "avatar_type", "angle", "length_bucket", "format", "cta", "voiceover")


def _f(v: Any, nd: int = 2) -> float:
    return round(float(v or 0), nd)


def _pct(num: Any, den: Any) -> float | None:
    return round(float(num) / float(den) * 100, 2) if den else None


def _ratio(num: Any, den: Any, nd: int = 2) -> float | None:
    return round(float(num) / float(den), nd) if den else None


def _delta(cur: Any, prev: Any) -> float | None:
    return round((float(cur) - float(prev)) / abs(float(prev)) * 100, 1) if prev else None


def _meta(p: Period, s: Settings) -> dict[str, Any]:
    return {"period": p.as_dict(s.store_timezone), "currency": s.store_currency}


def _order_totals(session: Session, p: Period) -> dict[str, float]:
    row = session.execute(
        text("""
        SELECT COUNT(*) AS orders, COALESCE(SUM(net_revenue),0) AS net_revenue, COALESCE(SUM(discounts),0) AS discounts,
               COALESCE(SUM(refunds),0) AS refunds, COALESCE(SUM(cogs),0) AS cogs,
               COALESCE(SUM(shipping_cost),0) AS shipping_cost, COALESCE(SUM(payment_fees),0) AS payment_fees,
               COALESCE(SUM(contribution_profit),0) AS contribution_profit,
               COALESCE(SUM(CASE WHEN is_first_order THEN 1 ELSE 0 END),0) AS new_customer_orders,
               COALESCE(SUM(CASE WHEN units_missing_cost > 0 THEN 1 ELSE 0 END),0) AS orders_missing_cost,
               COALESCE(SUM(CASE WHEN attributed_platform IS NOT NULL THEN net_revenue ELSE 0 END),0) AS attributed_revenue
        FROM v_order_profit WHERE order_date BETWEEN :a AND :b"""),
        {"a": p.start, "b": p.end},
    ).one()
    return {k: float(v or 0) for k, v in row._mapping.items()}


def _spend(session: Session, p: Period) -> dict[str, float]:
    rows = session.execute(
        text("""
        SELECT a.platform, COALESCE(SUM(m.spend),0) FROM ad_metrics_daily m JOIN ads a ON a.id = m.ad_id
        WHERE m.date BETWEEN :a AND :b GROUP BY a.platform"""),
        {"a": p.start, "b": p.end},
    ).all()
    return {str(r[0]): float(r[1]) for r in rows}


def business_summary(session: Session, p: Period, s: Settings | None = None) -> dict[str, Any]:
    """Revenue, costs, contribution profit, ad spend and efficiency, vs the previous period."""
    s = s or get_settings()

    def block(period: Period) -> dict[str, Any]:
        o, spend = _order_totals(session, period), _spend(session, period)
        total_spend = sum(spend.values())
        after_ads = o["contribution_profit"] - total_spend
        return {
            "orders_count": int(o["orders"]),
            "net_revenue": _f(o["net_revenue"]),
            "aov": _f(_ratio(o["net_revenue"], o["orders"]) or 0),
            "discounts": _f(o["discounts"]),
            "refunds": _f(o["refunds"]),
            "cogs": _f(o["cogs"]),
            "shipping_cost": _f(o["shipping_cost"]),
            "payment_fees": _f(o["payment_fees"]),
            "contribution_profit_before_ads": _f(o["contribution_profit"]),
            "ad_spend": _f(total_spend),
            "ad_spend_by_platform": {k: _f(v) for k, v in sorted(spend.items())},
            "contribution_profit_after_ads": _f(after_ads),
            "contribution_margin_pct": _pct(after_ads, o["net_revenue"]),
            "mer": _ratio(o["net_revenue"], total_spend),
            "new_customer_orders_count": int(o["new_customer_orders"]),
            "attributed_revenue_share_pct": _pct(o["attributed_revenue"], o["net_revenue"]),
            "orders_missing_cost_count": int(o["orders_missing_cost"]),
        }

    cur, prev = block(p), block(p.previous())
    changes = {
        f"{k}_change_pct": _delta(cur[k], prev[k])
        for k in ("net_revenue", "ad_spend", "contribution_profit_after_ads", "orders_count")
    }
    notes = []
    if cur["orders_missing_cost_count"]:
        notes.append(
            f"{cur['orders_missing_cost_count']} orders have items without a unit cost: profit is overstated"
        )
    return {
        **_meta(p, s),
        "summary": cur,
        "vs_previous_period": {**changes, "previous": p.previous().as_dict(s.store_timezone)},
        "notes": notes,
    }


def profit_by_product(
    session: Session, p: Period, s: Settings | None = None, limit: int = 25
) -> dict[str, Any]:
    """Per product: units, net sales, COGS, allocated costs, contribution (before ad spend).

    Order-level refunds, shipping cost and fees are allocated to lines by their share of the
    order's line sales.
    """
    s = s or get_settings()
    orders = {
        r.order_id: r
        for r in session.execute(
            text("""
        SELECT order_id, refunds, shipping_cost, payment_fees FROM v_order_profit
        WHERE order_date BETWEEN :a AND :b"""),
            {"a": p.start, "b": p.end},
        )
    }
    if not orders:
        return {**_meta(p, s), "products": [], "notes": ["no orders in this period"]}
    items = session.execute(
        select(
            OrderItem.order_id,
            OrderItem.product_id,
            OrderItem.quantity,
            OrderItem.price,
            OrderItem.total_discount,
            OrderItem.unit_cost,
        ).where(OrderItem.order_id.in_(list(orders)))
    ).all()
    products = {
        pid: (title, cost)
        for pid, title, cost in session.execute(
            select(Product.id, Product.title, Product.unit_cost)
        )
    }
    line_sales: dict[int, Decimal] = defaultdict(Decimal)
    for it in items:
        line_sales[it.order_id] += it.price * it.quantity - it.total_discount
    agg: dict[Any, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for it in items:
        o = orders[it.order_id]
        sales = it.price * it.quantity - it.total_discount
        share = sales / line_sales[it.order_id] if line_sales[it.order_id] else Decimal("0")
        cost = (
            it.unit_cost
            if it.unit_cost is not None
            else (products.get(it.product_id, (None, None))[1] or Decimal("0"))
        )
        allocated = (
            Decimal(str(o.refunds)) + Decimal(str(o.shipping_cost)) + Decimal(str(o.payment_fees))
        ) * share
        a = agg[it.product_id]
        a["units"] += it.quantity
        a["net_sales"] += sales
        a["cogs"] += cost * it.quantity
        a["allocated_costs"] += allocated
    out = []
    for pid, a in agg.items():
        contribution = a["net_sales"] - a["cogs"] - a["allocated_costs"]
        out.append(
            {
                "product_id": pid,
                "title": products.get(pid, ("(unknown product)", None))[0],
                "units_count": int(a["units"]),
                "net_sales": _f(a["net_sales"]),
                "cogs": _f(a["cogs"]),
                "refunds_shipping_fees": _f(a["allocated_costs"]),
                "contribution_profit_before_ads": _f(contribution),
                "margin_pct": _pct(contribution, a["net_sales"]),
            }
        )
    out.sort(key=lambda r: r["contribution_profit_before_ads"], reverse=True)
    return {
        **_meta(p, s),
        "products": out[:limit],
        "notes": [
            "ad spend is not allocated to products; see get_platform_performance / get_top_creatives"
        ],
    }


def platform_performance(session: Session, p: Period, s: Settings | None = None) -> dict[str, Any]:
    """Per platform: spend, delivery, Shopify-attributed orders/revenue/contribution, efficiency."""
    s = s or get_settings()
    ads = {
        r[0]: r
        for r in session.execute(
            text("""
        SELECT platform, SUM(spend), SUM(impressions), SUM(clicks), SUM(video_3s_views), SUM(platform_purchases),
               SUM(platform_revenue), SUM(attributed_orders), SUM(attributed_revenue), SUM(attributed_contribution)
        FROM v_ad_daily_profit WHERE date BETWEEN :a AND :b GROUP BY platform"""),
            {"a": p.start, "b": p.end},
        )
    }
    unmatched = {
        r[0]: r
        for r in session.execute(
            text("""
        SELECT attributed_platform, COUNT(*), SUM(net_revenue), SUM(contribution_profit) FROM v_order_profit
        WHERE order_date BETWEEN :a AND :b AND attributed_platform IS NOT NULL AND attributed_ad_id IS NULL
        GROUP BY attributed_platform"""),
            {"a": p.start, "b": p.end},
        )
    }
    out = []
    for platform in sorted(set(ads) | set(unmatched)):
        a = ads.get(platform) or (platform, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        u = unmatched.get(platform) or (platform, 0, 0, 0)
        spend, impressions, clicks = float(a[1] or 0), int(a[2] or 0), int(a[3] or 0)
        orders = int(a[7] or 0) + int(u[1] or 0)
        revenue = float(a[8] or 0) + float(u[2] or 0)
        contribution = float(a[9] or 0) + float(u[3] or 0)
        out.append(
            {
                "platform": str(platform),
                "spend": _f(spend),
                "impressions_count": impressions,
                "clicks_count": clicks,
                "ctr_pct": _pct(clicks, impressions),
                "cpc": _ratio(spend, clicks),
                "attributed_orders_count": orders,
                "attributed_revenue": _f(revenue),
                "attributed_contribution": _f(contribution),
                "contribution_profit_after_spend": _f(contribution - spend),
                "roas": _ratio(revenue, spend),
                "cpa": _ratio(spend, orders),
                "orders_without_ad_match_count": int(u[1] or 0),
                "platform_reported_purchases_count": int(a[5] or 0),
                "platform_reported_revenue": _f(a[6]),
                "platform_overreporting_ratio": _ratio(a[5] or 0, orders),
            }
        )
    return {
        **_meta(p, s),
        "platforms": out,
        "notes": [
            "attributed_* = Shopify orders (last touch); platform_reported_* = the platform's own claim"
        ],
    }


def _creative_rows(session: Session, p: Period) -> dict[int, dict[str, float]]:
    rows = session.execute(
        text("""
        SELECT creative_id, SUM(spend), SUM(impressions), SUM(clicks), SUM(video_3s_views), SUM(attributed_orders),
               SUM(attributed_revenue), SUM(contribution_profit)
        FROM v_creative_daily_profit WHERE date BETWEEN :a AND :b GROUP BY creative_id"""),
        {"a": p.start, "b": p.end},
    )
    keys = (
        "spend",
        "impressions",
        "clicks",
        "video_3s_views",
        "orders",
        "revenue",
        "contribution_profit",
    )
    return {int(r[0]): {k: float(v or 0) for k, v in zip(keys, r[1:], strict=True)} for r in rows}


def _derive(m: dict[str, float]) -> dict[str, Any]:
    enough = m["spend"] >= float(MIN_SPEND) or m["impressions"] >= MIN_IMPRESSIONS
    return {
        "spend": _f(m["spend"]),
        "impressions_count": int(m["impressions"]),
        "attributed_orders_count": round(m["orders"], 2),
        "contribution_profit": _f(m["contribution_profit"]),
        "profit_per_1000_spend": _f(m["contribution_profit"] / m["spend"] * 1000)
        if m["spend"]
        else None,
        "hook_rate_pct": _pct(m["video_3s_views"], m["impressions"]),
        "ctr_pct": _pct(m["clicks"], m["impressions"]),
        "cpa": _ratio(m["spend"], m["orders"]),
        "enough_data": enough,
    }


CREATIVE_METRICS = {
    "contribution_profit": True,
    "profit_per_1000_spend": True,
    "hook_rate_pct": True,
    "ctr_pct": True,
    "cpa": False,
    "spend": True,
}  # metric -> higher is better


def top_creatives(
    session: Session,
    p: Period,
    metric: str = "contribution_profit",
    limit: int = 10,
    s: Settings | None = None,
) -> dict[str, Any]:
    s = s or get_settings()
    if metric not in CREATIVE_METRICS:
        raise ValueError(f"metric must be one of {', '.join(CREATIVE_METRICS)}")
    rows = _creative_rows(session, p)
    meta = (
        {c.id: c for c in session.scalars(select(Creative).where(Creative.id.in_(list(rows))))}
        if rows
        else {}
    )
    traits = (
        {
            t.creative_id: t
            for t in session.scalars(
                select(CreativeTrait).where(CreativeTrait.creative_id.in_(list(rows)))
            )
        }
        if rows
        else {}
    )
    out = []
    for cid, m in rows.items():
        d = _derive(m)
        t = traits.get(cid)
        d |= {
            "creative_id": cid,
            "type": meta[cid].type.value if cid in meta else None,
            "traits": {k: getattr(t, k) for k in TRAITS} if t else {},
        }
        out.append(d)
    ratio = metric not in ("contribution_profit", "spend")
    ranked = [r for r in out if r["enough_data"] and r[metric] is not None] if ratio else out
    ranked.sort(
        key=lambda r: r[metric] if r[metric] is not None else 0, reverse=CREATIVE_METRICS[metric]
    )
    notes = (
        [
            f"ratio metrics only rank creatives with >= {MIN_SPEND} spend or >= {MIN_IMPRESSIONS} impressions"
        ]
        if ratio
        else []
    )
    skipped = len(out) - len(ranked)
    if skipped:
        notes.append(f"{skipped} creatives skipped for insufficient data")
    return {**_meta(p, s), "metric": metric, "creatives": ranked[:limit], "notes": notes}


def creative_trait_insights(
    session: Session, p: Period, s: Settings | None = None, min_creatives: int = 3
) -> dict[str, Any]:
    """For each trait value: how creatives with it performed (profit per $1,000 spend first)."""
    s = s or get_settings()
    rows = _creative_rows(session, p)
    traits = (
        list(
            session.scalars(select(CreativeTrait).where(CreativeTrait.creative_id.in_(list(rows))))
        )
        if rows
        else []
    )
    groups: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for t in traits:
        m = rows[t.creative_id]
        for name in TRAITS:
            value = getattr(t, name)
            if value is None:
                continue
            g = groups[(name, str(value).lower() if isinstance(value, bool) else str(value))]
            g["creatives"] += 1
            for k in (
                "spend",
                "impressions",
                "video_3s_views",
                "clicks",
                "orders",
                "contribution_profit",
            ):
                g[k] += m[k]
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (name, value), g in groups.items():
        out[name].append(
            {
                "value": value,
                "creatives_count": int(g["creatives"]),
                "spend": _f(g["spend"]),
                "contribution_profit": _f(g["contribution_profit"]),
                "profit_per_1000_spend": _f(g["contribution_profit"] / g["spend"] * 1000)
                if g["spend"]
                else None,
                "hook_rate_pct": _pct(g["video_3s_views"], g["impressions"]),
                "ctr_pct": _pct(g["clicks"], g["impressions"]),
                "low_sample": g["creatives"] < min_creatives
                or g["spend"] < float(MIN_SPEND) * min_creatives,
            }
        )
    for name in out:
        out[name].sort(
            key=lambda r: (not r["low_sample"], r["profit_per_1000_spend"] or float("-inf")),
            reverse=True,
        )
    return {
        **_meta(p, s),
        "traits": dict(out),
        "notes": [
            f"low_sample = fewer than {min_creatives} creatives or < {MIN_SPEND * min_creatives} spend: treat as anecdotal",
            "correlation, not causation; Phase 7's model controls for overlaps between traits",
        ],
    }


def pending_approvals(session: Session, s: Settings | None = None) -> dict[str, Any]:
    s = s or get_settings()
    now = datetime.now(UTC)
    rows = session.scalars(
        select(PendingApproval)
        .where(PendingApproval.status == ApprovalStatus.PENDING)
        .order_by(PendingApproval.created_at)
    ).all()
    items = []
    for a in rows:
        created = a.created_at if a.created_at.tzinfo else a.created_at.replace(tzinfo=UTC)
        expires = (
            a.expires_at.replace(tzinfo=UTC)
            if a.expires_at and not a.expires_at.tzinfo
            else a.expires_at
        )
        items.append(
            {
                "id": a.id,
                "action": a.action_type,
                "summary": a.summary,
                "rationale": a.rationale,
                "requested_by": a.requested_by,
                "age_hours": round((now - created).total_seconds() / 3600, 1),
                "expires_in_hours": round((expires - now).total_seconds() / 3600, 1)
                if expires
                else None,
                "payload": a.payload,
            }
        )
    return {"pending_count": len(items), "approvals": items, "currency": s.store_currency}


def generation_spend(session: Session, s: Settings | None = None) -> dict[str, Any]:
    """Higgsfield spend this month vs cap, job outcomes, cost per usable creative (USD)."""
    from app.creatives.pipeline import CHARGED, month_start, monthly_spend

    s = s or get_settings()
    now = datetime.now(UTC)
    cap = business_settings.load(session).higgsfield_monthly_cap_usd
    spent = monthly_spend(session, now)
    by_status = dict(
        session.execute(
            select(GenerationJob.status, func.count(GenerationJob.id))
            .where(GenerationJob.created_at >= month_start(now))
            .group_by(GenerationJob.status)
        ).all()
    )
    ready = (
        session.scalar(
            select(func.count(Creative.id)).where(
                Creative.created_at >= month_start(now),
                Creative.status.in_(
                    (CreativeStatus.READY, CreativeStatus.APPROVED, CreativeStatus.LAUNCHED)
                ),
            )
        )
        or 0
    )
    last30 = (
        session.scalar(
            select(func.coalesce(func.sum(GenerationJob.cost_usd), 0)).where(
                GenerationJob.created_at >= now - timedelta(days=30),
                GenerationJob.status.in_(CHARGED),
            )
        )
        or 0
    )
    return {
        "month": now.strftime("%Y-%m"),
        "currency": "USD",
        "spent_this_month": _f(spent),
        "monthly_cap": _f(cap) if cap is not None else None,
        "headroom": _f(cap - spent) if cap is not None else None,
        "cap_status": "not set: generation blocked"
        if cap is None
        else ("exhausted" if spent >= cap else "ok"),
        "jobs_this_month": {getattr(k, "value", str(k)): v for k, v in by_status.items()},
        "usable_creatives_this_month_count": int(ready),
        "cost_per_usable_creative": _ratio(spent, ready),
        "spent_last_30_days": _f(last30),
    }
