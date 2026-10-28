"""Write platform structure + metrics into the database (idempotent upserts).

* Structure is upserted on ``(platform, external_id)`` for accounts, campaigns, ad sets
  and ads. Objects that disappear from the platform are marked ``deleted`` (never removed:
  their history still counts).
* Metrics are upserted on ``(ad_id, date)``: re-reading the last few days replaces the
  numbers (platforms revise conversions for days), it never double counts.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import attribution
from app.integrations.ads.base import AdPlatform, DailyMetric, Structure
from app.log import get_logger
from app.models import Ad, AdAccount, AdMetricsDaily, AdSet, Campaign, EntityStatus, Platform

log = get_logger(__name__)


def _by_external(session: Session, model: Any, platform: Platform) -> dict[str, Any]:
    return {
        r.external_id: r for r in session.scalars(select(model).where(model.platform == platform))
    }


def upsert_structure(session: Session, platform: Platform, st: Structure) -> dict[str, int]:
    account = session.scalar(
        select(AdAccount).where(
            AdAccount.platform == platform, AdAccount.external_id == st.account.external_id
        )
    ) or AdAccount(platform=platform, external_id=st.account.external_id)
    account.name, account.currency = st.account.name, st.account.currency
    account.timezone, account.status = st.account.timezone, st.account.status
    session.add(account)
    session.flush()

    campaigns = _by_external(session, Campaign, platform)
    seen_c = set()
    for c in st.campaigns:
        row = campaigns.get(c.external_id) or Campaign(platform=platform, external_id=c.external_id)
        row.ad_account_id = account.id
        row.name, row.status, row.objective = c.name, c.status, c.objective
        row.daily_budget, row.lifetime_budget = c.daily_budget, c.lifetime_budget
        session.add(row)
        campaigns[c.external_id] = row
        seen_c.add(c.external_id)
    session.flush()

    ad_sets = _by_external(session, AdSet, platform)
    seen_s, skipped = set(), 0
    for a in st.ad_sets:
        parent = campaigns.get(a.campaign_external_id)
        if parent is None:
            skipped += 1
            continue
        row = ad_sets.get(a.external_id) or AdSet(platform=platform, external_id=a.external_id)
        row.campaign_id = parent.id
        row.name, row.status, row.optimization_goal = a.name, a.status, a.optimization_goal
        row.daily_budget, row.lifetime_budget = a.daily_budget, a.lifetime_budget
        session.add(row)
        ad_sets[a.external_id] = row
        seen_s.add(a.external_id)
    session.flush()

    ads = _by_external(session, Ad, platform)
    seen_a = set()
    for ad in st.ads:
        parent = ad_sets.get(ad.ad_set_external_id)
        if parent is None:
            skipped += 1
            continue
        row = ads.get(ad.external_id) or Ad(platform=platform, external_id=ad.external_id)
        row.ad_set_id = parent.id
        row.name, row.status = ad.name, ad.status
        session.add(row)
        seen_a.add(ad.external_id)
    session.flush()

    # Gone from the platform listing (deleted there): keep the row, mark it.
    for rows, seen in ((campaigns, seen_c), (ad_sets, seen_s), (ads, seen_a)):
        for ext, row in rows.items():
            if ext not in seen and row.status != EntityStatus.DELETED and row.id is not None:
                row.status = EntityStatus.DELETED
    session.flush()
    return {
        "campaigns": len(seen_c),
        "ad_sets": len(seen_s),
        "ads": len(seen_a),
        "orphans_skipped": skipped,
    }


def upsert_metrics(
    session: Session, platform: Platform, metrics: list[DailyMetric]
) -> dict[str, int]:
    """Upsert daily metrics; rows for ads the structure sync hasn't seen are counted, not lost
    silently (they're picked up on the next run after a structure sync)."""
    ad_ids = {
        a.external_id: a.id for a in session.scalars(select(Ad).where(Ad.platform == platform))
    }
    if not metrics:
        return {"rows": 0, "unknown_ads": 0}
    dates = [m.date for m in metrics]
    existing = {
        (r.ad_id, r.date): r
        for r in session.scalars(
            select(AdMetricsDaily)
            .join(Ad, Ad.id == AdMetricsDaily.ad_id)
            .where(Ad.platform == platform, AdMetricsDaily.date.between(min(dates), max(dates)))
        )
    }
    # Platforms may return several rows per ad/day (e.g. Google PMax segments): sum them.
    merged: dict[tuple[int, date], DailyMetric] = {}
    unknown = 0
    for m in metrics:
        ad_id = ad_ids.get(m.ad_external_id)
        if ad_id is None:
            unknown += 1
            continue
        key = (ad_id, m.date)
        if key in merged:
            acc = merged[key]
            for f in (
                "spend",
                "impressions",
                "clicks",
                "video_3s_views",
                "add_to_cart",
                "purchases",
                "platform_revenue",
            ):
                setattr(acc, f, getattr(acc, f) + getattr(m, f))
        else:
            merged[key] = DailyMetric(**vars(m))
    now = datetime.now(UTC)
    for (ad_id, day), m in merged.items():
        row = existing.get((ad_id, day)) or AdMetricsDaily(ad_id=ad_id, date=day)
        row.spend, row.impressions, row.clicks = m.spend, m.impressions, m.clicks
        row.video_3s_views, row.add_to_cart, row.purchases = (
            m.video_3s_views,
            m.add_to_cart,
            m.purchases,
        )
        row.platform_revenue, row.synced_at = m.platform_revenue, now
        session.add(row)
    session.flush()
    if unknown:
        log.warning("ad_metrics_unknown_ads", platform=platform.value, rows=unknown)
    return {"rows": len(merged), "unknown_ads": unknown}


def sync_platform(
    client: AdPlatform, session: Session, lookback_days: int, today: date | None = None
) -> dict[str, int]:
    """Structure, then the last ``lookback_days`` of metrics, then re-match orders to new ads."""
    today = today or date.today()
    stats: dict[str, int] = {}
    stats |= upsert_structure(session, client.platform, client.list_structure())
    metrics = client.get_daily_metrics(today - timedelta(days=lookback_days - 1), today)
    stats |= upsert_metrics(session, client.platform, metrics)
    since = datetime.combine(today - timedelta(days=60), time.min, tzinfo=UTC)
    stats["orders_reattributed"] = attribution.reattribute(session, since=since)
    return stats
