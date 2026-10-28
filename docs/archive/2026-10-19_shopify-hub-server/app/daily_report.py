"""The daily summary (Slack): yesterday's money, ads, creatives and every action the hub took."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics import reports
from app.analytics.periods import Period
from app.config import Settings, get_settings
from app.models import ActionLog, ActionStatus, ApprovalStatus, PendingApproval

QUIET_ACTIONS = ("mcp.read_tool",)  # reads aren't "actions taken"


def _day_bounds_utc(day: date, s: Settings) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=s.tz).astimezone(UTC)
    return start, start + timedelta(days=1)


def build(
    session: Session, day: date | None = None, s: Settings | None = None, redis: Any | None = None
) -> dict[str, Any]:
    s = s or get_settings()
    day = day or (datetime.now(UTC).astimezone(s.tz).date() - timedelta(days=1))
    p = Period(day, day, day.isoformat())
    summary = reports.business_summary(session, p, s)
    week = reports.business_summary(session, Period(day - timedelta(days=6), day, "7 days"), s)[
        "summary"
    ]
    platforms = reports.platform_performance(session, p, s)["platforms"]
    top = reports.top_creatives(session, p, metric="contribution_profit", limit=1, s=s)["creatives"]

    start, end = _day_bounds_utc(day, s)
    acts = list(
        session.scalars(
            select(ActionLog).where(
                ActionLog.created_at >= start,
                ActionLog.created_at < end,
                ActionLog.action_type.notin_(QUIET_ACTIONS),
            )
        )
    )
    by_status = Counter(a.status.value for a in acts)
    blocked = [f"{a.action_type}: {a.error}" for a in acts if a.status == ActionStatus.BLOCKED][:5]
    executed = [
        a.summary
        for a in session.scalars(
            select(PendingApproval).where(
                PendingApproval.executed_at >= start,
                PendingApproval.executed_at < end,
                PendingApproval.status == ApprovalStatus.EXECUTED,
            )
        )
    ]
    pending = reports.pending_approvals(session, s)["pending_count"]
    gen = reports.generation_spend(session, s)
    active_alerts: list[str] = []
    if redis is not None:
        try:
            active_alerts = sorted(
                x.decode() if isinstance(x, bytes) else str(x)
                for x in redis.smembers("hub:alert:active")
            )
        except Exception:
            active_alerts = ["(alert state unavailable)"]
    return {
        "day": day.isoformat(),
        "currency": s.store_currency,
        "summary": summary["summary"],
        "vs_previous_day": summary["vs_previous_period"],
        "seven_day_avg_contribution_after_ads": round(week["contribution_profit_after_ads"] / 7, 2),
        "platforms": platforms,
        "top_creative": top[0] if top else None,
        "actions": {
            "by_status": dict(by_status),
            "executed_approvals": executed,
            "blocked": blocked,
        },
        "bandit": _recent_bandit(session, start),
        "pending_approvals": pending,
        "generation": gen,
        "active_alerts": active_alerts,
        "notes": summary["notes"],
    }


def _recent_bandit(session: Session, since: datetime) -> dict[str, Any] | None:
    from app.ml import bandit

    latest = bandit.latest(session)
    if not latest or latest["status"] not in ("proposed", "no_change"):
        return None
    created = datetime.fromisoformat(latest["created_at"])
    created = created if created.tzinfo else created.replace(tzinfo=UTC)
    return latest if created >= since else None


def _money(v: float | None, cur: str) -> str:
    return "n/a" if v is None else f"{v:,.2f} {cur}"


def _chg(v: float | None) -> str:
    return "" if v is None else f" ({v:+.1f}% vs day before)"


def format_slack(r: dict[str, Any]) -> str:
    c, s = r["currency"], r["summary"]
    lines = [
        f"*Shopify hub daily summary: {r['day']}*",
        f"• Revenue: *{_money(s['net_revenue'], c)}* from {s['orders_count']} orders"
        f"{_chg(r['vs_previous_day'].get('net_revenue_change_pct'))}",
        f"• Ad spend: *{_money(s['ad_spend'], c)}*"
        + (
            " (" + ", ".join(f"{k} {v:,.2f}" for k, v in s["ad_spend_by_platform"].items()) + ")"
            if s["ad_spend_by_platform"]
            else ""
        ),
        f"• Contribution profit after ads: *{_money(s['contribution_profit_after_ads'], c)}*"
        f"{_chg(r['vs_previous_day'].get('contribution_profit_after_ads_change_pct'))}; "
        f"7-day avg {_money(r['seven_day_avg_contribution_after_ads'], c)}",
        f"• Margin {s['contribution_margin_pct'] if s['contribution_margin_pct'] is not None else 'n/a'}% · "
        f"MER {s['mer'] if s['mer'] is not None else 'n/a'} · new-customer orders {s['new_customer_orders_count']}",
    ]
    for p in r["platforms"]:
        lines.append(
            f"  ◦ {p['platform']}: spend {p['spend']:,.2f}, {p['attributed_orders_count']} orders, "
            f"CPA {p['cpa'] if p['cpa'] is not None else 'n/a'}, after-spend {p['contribution_profit_after_spend']:,.2f}"
        )
    if r["top_creative"]:
        t = r["top_creative"]
        lines.append(
            f"• Top creative #{t['creative_id']}: {_money(t['contribution_profit'], c)} contribution on "
            f"{t['spend']:,.2f} spend ({(t['traits'] or {}).get('hook_type') or 'no traits'})"
        )
    a = r["actions"]
    counts = ", ".join(f"{k} {v}" for k, v in sorted(a["by_status"].items())) or "none"
    lines.append(f"• Actions: {counts}")
    lines += [f"  ◦ executed: {x}" for x in a["executed_approvals"][:8]]
    lines += [f"  ◦ blocked: {x}" for x in a["blocked"]]
    if r["pending_approvals"]:
        lines.append(f"• {r['pending_approvals']} proposal(s) waiting for your approval")
    if r.get("bandit"):
        b = r["bandit"]
        lines.append(
            "• Budget bandit ("
            + b["status"]
            + "): "
            + ", ".join(
                f"{a['platform']} {a['current_budget']:,.0f}->{a['new_budget']:,.0f} (P best {a['p_best']:.0%})"
                for a in b["arms"]
            )
        )
    g = r["generation"]
    cap = "no cap set" if g["monthly_cap"] is None else f"of {g['monthly_cap']:,.2f} cap"
    lines.append(f"• Higgsfield this month: {g['spent_this_month']:,.2f} USD {cap}")
    if r["active_alerts"]:
        lines.append(":warning: Active alerts: " + ", ".join(r["active_alerts"]))
    lines += [f"_{n}_" for n in r["notes"]]
    return "\n".join(lines)
