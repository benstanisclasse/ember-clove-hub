"""Nightly per-creative metrics (7 / 30 days and lifetime) with a minimum-data threshold.

* hook rate   = 3-second views / impressions (TikTok: 2-second views; Google: n/a)
* CTR         = clicks / impressions
* CPA         = spend / Shopify-attributed orders
* profit/1000 = contribution profit (after spend) per 1,000 of spend

A creative is only **judged** (winner / loser / neutral) once it has at least
``MIN_SPEND`` spend or ``MIN_IMPRESSIONS`` impressions in that window; before that it is
``learning``. Loser = losing more than 100 per 1,000 spent (ROI after spend < -10%).
Winner = profitable *and* in the top quartile of judged creatives for the window.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.analytics.reports import MIN_IMPRESSIONS, MIN_SPEND
from app.models import CreativeMetric

WINDOWS = (7, 30, 0)  # 0 = lifetime
LOSER_PROFIT_PER_1000 = Decimal("-100")


def _rows(session: Session, as_of: date, window: int) -> list[Any]:
    where = "date <= :end" + ("" if window == 0 else " AND date >= :start")
    params = (
        {"end": as_of, "start": as_of - timedelta(days=window - 1)} if window else {"end": as_of}
    )
    return session.execute(
        text(f"""
        SELECT creative_id, SUM(spend) AS spend, SUM(impressions) AS impressions, SUM(clicks) AS clicks,
               SUM(video_3s_views) AS views, SUM(attributed_orders) AS orders,
               SUM(contribution_profit) AS contribution
        FROM v_creative_daily_profit WHERE {where} GROUP BY creative_id"""),  # noqa: S608 - fixed WHERE
        params,
    ).all()


def _q(v: float, places: str = "0.01") -> Decimal:
    return Decimal(str(v)).quantize(Decimal(places))


def compute(session: Session, as_of: date, windows: tuple[int, ...] = WINDOWS) -> dict[str, int]:
    """Upsert snapshots for every creative with data; returns counts per verdict."""
    counts: dict[str, int] = {}
    for window in windows:
        snaps = []
        for r in _rows(session, as_of, window):
            spend, imps = float(r.spend or 0), int(float(r.impressions or 0))
            clicks, views, orders = (
                int(float(r.clicks or 0)),
                int(float(r.views or 0)),
                float(r.orders or 0),
            )
            contribution = float(r.contribution or 0)
            enough = spend >= float(MIN_SPEND) or imps >= MIN_IMPRESSIONS
            snaps.append(
                {
                    "creative_id": int(r.creative_id),
                    "spend": _q(spend),
                    "impressions": imps,
                    "clicks": clicks,
                    "video_3s_views": views,
                    "orders": _q(orders),
                    "contribution_profit": _q(contribution),
                    "hook_rate": views / imps if imps else None,
                    "ctr": clicks / imps if imps else None,
                    "cpa": _q(spend / orders) if orders else None,
                    "profit_per_1000": _q(contribution / spend * 1000) if spend else None,
                    "enough_data": enough,
                }
            )
        judged = sorted(
            s["profit_per_1000"]
            for s in snaps
            if s["enough_data"] and s["profit_per_1000"] is not None
        )
        top_quartile = judged[int(len(judged) * 0.75)] if judged else None
        for snap in snaps:
            p = snap["profit_per_1000"]
            if not snap["enough_data"] or p is None:
                verdict = "learning"
            elif p < LOSER_PROFIT_PER_1000:
                verdict = "loser"
            elif p > 0 and top_quartile is not None and p >= top_quartile:
                verdict = "winner"
            else:
                verdict = "neutral"
            row = session.scalar(
                select(CreativeMetric).where(
                    CreativeMetric.creative_id == snap["creative_id"],
                    CreativeMetric.as_of == as_of,
                    CreativeMetric.window_days == window,
                )
            ) or CreativeMetric(creative_id=snap["creative_id"], as_of=as_of, window_days=window)
            for k, v in snap.items():
                setattr(row, k, v)
            row.verdict = verdict
            session.add(row)
            key = f"{'lifetime' if window == 0 else f'{window}d'}_{verdict}"
            counts[key] = counts.get(key, 0) + 1
    session.flush()
    return counts


def latest_lifetime(session: Session) -> list[CreativeMetric]:
    """The newest lifetime snapshot per creative (ML labels)."""
    newest = session.scalar(
        select(CreativeMetric.as_of)
        .where(CreativeMetric.window_days == 0)
        .order_by(CreativeMetric.as_of.desc())
        .limit(1)
    )
    if newest is None:
        return []
    return list(
        session.scalars(
            select(CreativeMetric).where(
                CreativeMetric.window_days == 0, CreativeMetric.as_of == newest
            )
        )
    )
