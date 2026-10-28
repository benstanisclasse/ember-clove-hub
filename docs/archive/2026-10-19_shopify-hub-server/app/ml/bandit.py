"""Thompson-sampling budget allocation across ad platforms (recommendations only).

Reward = **marginal ROI after spend** on Shopify contribution profit: how much contribution
profit (minus the spend itself) the next unit of spend on a platform returns.

1. Daily series per platform over the window: spend and Shopify-attributed contribution
   (ad-matched orders + platform-attributed orders without an ad match).
2. Estimate per platform:
   * *regression* (preferred): with >= 14 spend days and enough day-to-day spend variation
     (CV >= 0.15), regress daily contribution on daily spend; marginal ROI after spend =
     slope - 1. This captures diminishing returns that averages hide.
   * *average*: otherwise sum(contribution - spend) / sum(spend), SE from daily variation.
   * *prior only*: under 7 spend days or 100 spend: we know nothing yet.
3. Posterior = estimate shrunk toward a skeptical prior N(0, 0.5) by precision weighting.
4. Thompson sampling: many draws from each posterior; P(best) = share of draws a
   platform wins. Target budget share = 10% exploration floor + rest by P(best).
5. Moves are bounded by ``max_budget_change_pct`` (x0.9 margin), the **total never goes up**
   (pure reallocation), and moves under 5% are skipped. Each budget-holding campaign / ad set
   gets a ``budget_change`` proposal (decreases first) through the normal approval queue,
   with guardrails, so nothing changes until approved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

import numpy as np
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import approvals, business_settings
from app.actions import SessionFactory, WritesBlockedError
from app.config import get_settings
from app.db import session_scope
from app.log import get_logger
from app.models import (
    AdSet,
    ApprovalStatus,
    BanditRun,
    Campaign,
    EntityStatus,
    PendingApproval,
    Platform,
)

log = get_logger(__name__)
PRIOR_MEAN, PRIOR_SD = 0.0, 0.5
MIN_DAYS, MIN_ARM_SPEND = 7, 100.0
REGRESSION_DAYS, REGRESSION_MIN_CV = 14, 0.15
FLOOR_SHARE, MIN_MOVE_PCT, SAMPLES = 0.10, 5.0, 4000


@dataclass
class Arm:
    platform: str
    days: int = 0
    spend: float = 0.0
    contribution: float = 0.0
    method: str = "prior only"
    estimate: float | None = None
    se: float | None = None
    post_mean: float = PRIOR_MEAN
    post_sd: float = PRIOR_SD
    p_best: float = 0.0
    current_budget: float = 0.0
    target_budget: float = 0.0
    new_budget: float = 0.0
    entities: list[dict[str, Any]] = field(default_factory=list)

    @property
    def avg_roi_after_spend(self) -> float | None:
        return (self.contribution - self.spend) / self.spend if self.spend else None


def estimate(daily: list[tuple[float, float]]) -> tuple[float | None, float | None, str]:
    """(estimate, standard error, method) of marginal ROI after spend from (spend, contribution) days."""
    pts = [(s, c) for s, c in daily if s > 0]
    n, total = len(pts), sum(s for s, _ in pts)
    if n < MIN_DAYS or total < MIN_ARM_SPEND:
        return None, None, "prior only"
    s = np.array([p[0] for p in pts], dtype=float)
    c = np.array([p[1] for p in pts], dtype=float)
    if n >= REGRESSION_DAYS and s.std() / s.mean() >= REGRESSION_MIN_CV:
        sxx = float(((s - s.mean()) ** 2).sum())
        slope = float(((s - s.mean()) * (c - c.mean())).sum() / sxx)
        resid = c - (c.mean() + slope * (s - s.mean()))
        se = float(np.sqrt((resid**2).sum() / (n - 2) / sxx))
        if np.isfinite(slope) and np.isfinite(se) and se > 0:
            return slope - 1.0, max(se, 0.02), "regression (marginal)"
    roi = (c - s) / s
    avg = float((c - s).sum() / s.sum())
    w = s / s.sum()
    sd = float(np.sqrt((w * (roi - avg) ** 2).sum()))
    return avg, max(sd / np.sqrt(n), 0.02), "average"


def posterior(est: float | None, se: float | None) -> tuple[float, float]:
    if est is None or se is None:
        return PRIOR_MEAN, PRIOR_SD
    prior_prec, data_prec = 1 / PRIOR_SD**2, 1 / se**2
    var = 1 / (prior_prec + data_prec)
    return var * (PRIOR_MEAN * prior_prec + est * data_prec), float(np.sqrt(var))


def p_best(
    means: list[float], sds: list[float], samples: int = SAMPLES, seed: int | None = None
) -> list[float]:
    rng = np.random.default_rng(seed)
    draws = rng.normal(np.array(means), np.array(sds), size=(samples, len(means)))
    wins = np.bincount(draws.argmax(axis=1), minlength=len(means))
    return [float(w) / samples for w in wins]


def allocate(
    current: list[float], probs: list[float], max_change_pct: float
) -> tuple[list[float], list[float]]:
    """(targets, new budgets): exploration floor, bounded moves, total never increases."""
    k, total = len(current), sum(current)
    floor = min(FLOOR_SHARE, 1.0 / k)
    targets = [total * (floor + (1 - floor * k) * p) for p in probs]
    m = max_change_pct * 0.9 / 100
    bounded = [min(max(t, c * (1 - m)), c * (1 + m)) for t, c in zip(targets, current, strict=True)]
    up = sum(max(b - c, 0) for b, c in zip(bounded, current, strict=True))
    down = sum(max(c - b, 0) for b, c in zip(bounded, current, strict=True))
    if up > down:  # pure reallocation: increases are funded only by decreases
        factor = down / up if up else 0
        bounded = [
            c + (b - c) * factor if b > c else b for b, c in zip(bounded, current, strict=True)
        ]
    new = [
        b if c and abs(b - c) / c * 100 >= MIN_MOVE_PCT else c
        for b, c in zip(bounded, current, strict=True)
    ]
    return targets, new


# --- data ----------------------------------------------------------------------------------


def daily_series(session: Session, start: date, end: date) -> dict[str, dict[date, list[float]]]:
    out: dict[str, dict[date, list[float]]] = {}
    for platform, day, spend, contribution in session.execute(
        text("""
        SELECT platform, date, SUM(spend), SUM(attributed_contribution) FROM v_ad_daily_profit
        WHERE date BETWEEN :a AND :b GROUP BY platform, date"""),
        {"a": start, "b": end},
    ):
        d = day if isinstance(day, date) else date.fromisoformat(str(day))
        out.setdefault(str(platform), {}).setdefault(d, [0.0, 0.0])
        out[str(platform)][d][0] += float(spend or 0)
        out[str(platform)][d][1] += float(contribution or 0)
    for platform, day, contribution in session.execute(
        text("""
        SELECT attributed_platform, order_date, SUM(contribution_profit) FROM v_order_profit
        WHERE order_date BETWEEN :a AND :b AND attributed_platform IS NOT NULL AND attributed_ad_id IS NULL
        GROUP BY attributed_platform, order_date"""),
        {"a": start, "b": end},
    ):
        d = day if isinstance(day, date) else date.fromisoformat(str(day))
        out.setdefault(str(platform), {}).setdefault(d, [0.0, 0.0])
        out[str(platform)][d][1] += float(contribution or 0)
    return out


def budget_entities(session: Session, platform: str) -> list[dict[str, Any]]:
    """Active campaigns / ad sets on a platform that carry the spendable daily budget."""
    out = []
    for c in session.scalars(
        select(Campaign).where(
            Campaign.platform == Platform(platform), Campaign.status == EntityStatus.ACTIVE
        )
    ):
        if c.daily_budget:
            out.append(
                {"level": "campaign", "external_id": c.external_id, "budget": float(c.daily_budget)}
            )
            continue
        for s in session.scalars(
            select(AdSet).where(
                AdSet.campaign_id == c.id,
                AdSet.status == EntityStatus.ACTIVE,
                AdSet.daily_budget.is_not(None),
            )
        ):
            out.append(
                {"level": "ad_set", "external_id": s.external_id, "budget": float(s.daily_budget)}
            )
    return out


def _pending_budget_targets(session: Session) -> set[tuple[str, str, str]]:
    rows = session.scalars(
        select(PendingApproval.payload).where(
            PendingApproval.status == ApprovalStatus.PENDING,
            PendingApproval.action_type == "budget_change",
        )
    )
    return {(p.get("platform"), p.get("level"), p.get("external_id")) for p in rows if p}


# --- run -----------------------------------------------------------------------------------


def run(
    *,
    window_days: int = 28,
    session_factory: SessionFactory = session_scope,
    today: date | None = None,
    seed: int | None = None,
    propose: bool = True,
) -> dict[str, Any]:
    tz = get_settings().tz
    today = today or datetime.now(UTC).astimezone(tz).date()
    end, start = today - timedelta(days=1), today - timedelta(days=window_days)
    with session_factory() as s:
        series = daily_series(s, start, end)
        max_pct = business_settings.load(s).max_budget_change_pct
        arms: list[Arm] = []
        for platform in sorted({p.value for p in Platform}):
            entities = budget_entities(s, platform)
            current = sum(e["budget"] for e in entities)
            if current <= 0:
                continue
            days = series.get(platform, {})
            pairs = [(v[0], v[1]) for v in days.values()]
            est, se, method = estimate(pairs)
            mean, sd = posterior(est, se)
            arms.append(
                Arm(
                    platform=platform,
                    days=sum(1 for sp, _ in pairs if sp > 0),
                    spend=sum(p[0] for p in pairs),
                    contribution=sum(p[1] for p in pairs),
                    method=method,
                    estimate=est,
                    se=se,
                    post_mean=mean,
                    post_sd=sd,
                    current_budget=current,
                    entities=entities,
                )
            )

    def record(
        status: str, total: float, notes: str, proposals: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        arm_dicts = [asdict(a) | {"avg_roi_after_spend": a.avg_roi_after_spend} for a in arms]
        with session_factory() as s:
            row = BanditRun(
                window_days=window_days,
                total_daily_budget=Decimal(str(round(total, 2))),
                arms=arm_dicts,
                proposals=proposals,
                status=status,
                notes=notes,
            )
            s.add(row)
            s.flush()
            run_id = row.id
        return {
            "run_id": run_id,
            "status": status,
            "notes": notes,
            "arms": arm_dicts,
            "proposals": proposals or [],
        }

    if len(arms) < 2:
        return record(
            "skipped",
            sum(a.current_budget for a in arms),
            "needs at least two platforms with active daily budgets to reallocate between",
        )

    probs = p_best([a.post_mean for a in arms], [a.post_sd for a in arms], seed=seed)
    targets, new = allocate([a.current_budget for a in arms], probs, max_pct)
    for a, p, t, n in zip(arms, probs, targets, new, strict=True):
        a.p_best, a.target_budget, a.new_budget = round(p, 4), round(t, 2), round(n, 2)
    total = sum(a.current_budget for a in arms)
    movers = [a for a in arms if abs(a.new_budget - a.current_budget) >= 0.01]
    if not movers:
        return record(
            "no_change",
            total,
            "current split is within 5% of the recommendation (or limits prevent moves)",
        )
    if not propose:
        return record("dry_run", total, "recommendation only (propose=False)")

    proposals: list[dict[str, Any]] = []
    with session_factory() as s:
        pending = _pending_budget_targets(s)
    run_hint = "Budget bandit"
    for a in sorted(movers, key=lambda x: x.new_budget - x.current_budget):  # decreases first
        ratio = Decimal(str(a.new_budget / a.current_budget))
        rationale = (
            f"{run_hint}: {a.platform} marginal ROI after spend {a.post_mean:+.0%} (±{a.post_sd:.0%}, "
            f"{a.method}, {a.days} spend days), P(best) {a.p_best:.0%}; platform budget "
            f"{a.current_budget:.2f} -> {a.new_budget:.2f}/day. Total unchanged."
        )
        for e in a.entities:
            key = (a.platform, e["level"], e["external_id"])
            if key in pending:
                proposals.append({"entity": key, "skipped": "a budget proposal is already pending"})
                continue
            new_budget = (Decimal(str(e["budget"])) * ratio).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            try:
                with session_factory() as s:
                    payload, summary = approvals.build_budget_change(
                        s, a.platform, e["level"], e["external_id"], new_budget
                    )
                res = approvals.propose(
                    "budget_change",
                    payload,
                    summary,
                    rationale=rationale,
                    requested_by="budget-bandit",
                    session_factory=session_factory,
                )
                proposals.append(
                    {
                        "entity": key,
                        "approval_id": res["approval_id"],
                        "status": res["status"],
                        "summary": summary,
                    }
                )
            except (WritesBlockedError, approvals.ApprovalError) as exc:
                proposals.append({"entity": key, "skipped": str(exc)[:200]})
    made = sum(1 for p in proposals if "approval_id" in p)
    return record(
        "proposed" if made else "no_change",
        total,
        f"{made} budget proposal(s) created; approve decreases before increases",
        proposals,
    )


def latest(session: Session) -> dict[str, Any] | None:
    r = session.scalars(select(BanditRun).order_by(BanditRun.id.desc()).limit(1)).first()
    if r is None:
        return None
    return {
        "run_id": r.id,
        "created_at": r.created_at.isoformat(),
        "status": r.status,
        "notes": r.notes,
        "window_days": r.window_days,
        "total_daily_budget": float(r.total_daily_budget),
        "arms": [
            {
                k: a.get(k)
                for k in (
                    "platform",
                    "method",
                    "days",
                    "spend",
                    "avg_roi_after_spend",
                    "post_mean",
                    "post_sd",
                    "p_best",
                    "current_budget",
                    "new_budget",
                )
            }
            for a in r.arms
        ],
        "proposals": r.proposals or [],
    }
