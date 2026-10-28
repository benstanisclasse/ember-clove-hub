"""Phase 7: creative metrics, the Thompson-sampling bandit, the gated LightGBM model."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal as D
from typing import Any

import numpy as np
import pytest
from conftest import seed_entity
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ml import bandit, creative_metrics, model
from app.models import (
    ApprovalStatus,
    BanditRun,
    Creative,
    CreativeMetric,
    CreativeStatus,
    CreativeTrait,
    PendingApproval,
)

# --- creative metrics ------------------------------------------------------------------------


def test_creative_metrics_snapshot_and_verdicts(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    from test_mcp import seed

    seed(session)
    with session_factory() as s:
        counts = creative_metrics.compute(s, date(2026, 10, 1))
    with session_factory() as s:  # idempotent upsert
        creative_metrics.compute(s, date(2026, 10, 1))
    rows = session.scalars(select(CreativeMetric).where(CreativeMetric.window_days == 0)).all()
    assert len(rows) == 1
    m = rows[0]
    assert (m.spend, m.impressions, float(m.profit_per_1000)) == (D("40.00"), 4000, 3475.5)
    assert (
        m.hook_rate == pytest.approx(0.30) and m.ctr == pytest.approx(0.02) and m.cpa == D("20.00")
    )
    assert m.enough_data is True and m.verdict == "winner"
    assert (
        counts["lifetime_winner"] == 1
        and session.scalar(select(func.count(CreativeMetric.id))) == 3
    )


# --- bandit math -----------------------------------------------------------------------------


def test_estimate_methods() -> None:
    assert bandit.estimate([(10, 20)] * 5) == (None, None, "prior only")  # too few days
    est, _se, method = bandit.estimate([(50, 75)] * 10)  # flat spend: average
    assert method == "average" and est == pytest.approx(0.5)
    rng = np.random.default_rng(1)
    spends = rng.uniform(20, 200, 28)
    est, _se, method = bandit.estimate([(s, 2.0 * s + rng.normal(0, 2)) for s in spends])
    assert method == "regression (marginal)" and est == pytest.approx(1.0, abs=0.05)


def test_marginal_detects_diminishing_returns() -> None:
    spends = np.linspace(20, 400, 28)
    daily = [(s, 60 * np.sqrt(s)) for s in spends]  # each extra dollar returns less
    avg = sum(c - s for s, c in daily) / sum(s for s, _ in daily)
    est, _, method = bandit.estimate(daily)
    assert method.startswith("regression") and est < avg - 0.5  # marginal well below average


def test_posterior_shrinks_noisy_estimates_toward_zero() -> None:
    assert bandit.posterior(None, None) == (bandit.PRIOR_MEAN, bandit.PRIOR_SD)
    noisy_mean, noisy_sd = bandit.posterior(1.0, 2.0)
    sure_mean, sure_sd = bandit.posterior(1.0, 0.05)
    assert noisy_mean < 0.1 and sure_mean > 0.95 and sure_sd < noisy_sd


def test_thompson_and_allocation() -> None:
    probs = bandit.p_best([0.8, -0.3, 0.0], [0.1, 0.1, 0.5], seed=3)
    assert sum(probs) == pytest.approx(1.0) and probs[0] > probs[2] > probs[1]
    current = [100.0, 100.0, 100.0]
    targets, new = bandit.allocate(current, probs, max_change_pct=20)
    assert sum(new) <= sum(current) + 1e-6  # never increases total
    assert all(
        abs(n - c) / c <= 0.18 + 1e-9 for n, c in zip(new, current, strict=True)
    )  # 0.9 x 20%
    assert new[0] > 100 and new[1] < 100
    assert min(targets) >= sum(current) * 0.10 - 1e-6  # exploration floor


# --- bandit run -----------------------------------------------------------------------------


def _series(roi_after: dict[str, float]):  # type: ignore[no-untyped-def]
    rng = np.random.default_rng(5)

    def fake(session: Any, start: date, end: date) -> dict[str, dict[date, list[float]]]:
        out: dict[str, dict[date, list[float]]] = {}
        for p, r in roi_after.items():
            out[p] = {}
            for i in range(28):
                s = float(rng.uniform(60, 140))
                out[p][end - timedelta(days=i)] = [s, s * (1 + r) + float(rng.normal(0, 3))]
        return out

    return fake


def test_bandit_run_proposes_reallocation(
    session_factory, session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "m1", budget="100")
    seed_entity(session_factory, "tiktok", "t1", budget="100")
    monkeypatch.setattr(bandit, "daily_series", _series({"meta": 1.0, "tiktok": -0.5}))
    out = bandit.run(session_factory=session_factory, today=date(2026, 10, 18), seed=1)
    assert out["status"] == "proposed"
    arms = {a["platform"]: a for a in out["arms"]}
    assert (
        arms["meta"]["p_best"] > 0.95
        and arms["meta"]["new_budget"] > 100 > arms["tiktok"]["new_budget"]
    )
    assert arms["meta"]["new_budget"] + arms["tiktok"]["new_budget"] <= 200.0 + 1e-6
    pending = session.scalars(
        select(PendingApproval).where(PendingApproval.status == ApprovalStatus.PENDING)
    ).all()
    assert {p.payload["platform"] for p in pending} == {"meta", "tiktok"}
    assert all(p.requested_by == "budget-bandit" and "P(best)" in p.rationale for p in pending)
    again = bandit.run(session_factory=session_factory, today=date(2026, 10, 18), seed=1)
    assert all("already pending" in p.get("skipped", "") for p in again["proposals"])
    assert session.scalar(select(func.count(BanditRun.id))) == 2


def test_bandit_needs_two_platforms(session_factory) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "m1", budget="100")
    assert (
        bandit.run(session_factory=session_factory, today=date(2026, 10, 18))["status"] == "skipped"
    )


# --- model ----------------------------------------------------------------------------------


def _creatives(factory, n: int, signal: bool) -> None:  # type: ignore[no-untyped-def]
    rng = np.random.default_rng(11)
    with factory() as s:
        for i in range(n):
            hook = "pov" if i % 2 else "talking_head"
            label = (
                (800 if hook == "pov" else -200) + rng.normal(0, 60)
                if signal
                else rng.normal(0, 400)
            )
            c = Creative(type="video", status=CreativeStatus.LAUNCHED, duration_seconds=D("8"))
            s.add(c)
            s.flush()
            s.add(
                CreativeTrait(
                    creative_id=c.id,
                    hook_type=hook,
                    avatar_type=["w25", "m35", "w45"][i % 3],
                    angle="saves_time",
                    length_bucket="0-8s",
                    format="9x16_ugc_video",
                    cta="shop_now",
                    voiceover=bool(i % 3),
                    extra={},
                )
            )
            s.add(
                CreativeMetric(
                    creative_id=c.id,
                    as_of=date(2026, 10, 17),
                    window_days=0,
                    spend=D("400"),
                    impressions=20000,
                    clicks=300,
                    video_3s_views=5000,
                    orders=D("8"),
                    contribution_profit=D(str(round(label * 0.4, 2))),
                    profit_per_1000=D(str(round(label, 2))),
                    enough_data=True,
                    verdict="neutral",
                )
            )


class Store:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put(self, key: str, body: bytes, content_type: str) -> str:
        self.objects[key] = body
        return key

    def get_bytes(self, key: str) -> bytes:
        return self.objects[key]


def test_model_waits_for_enough_data(session_factory) -> None:  # type: ignore[no-untyped-def]
    _creatives(session_factory, 20, signal=True)
    out = model.train(session_factory=session_factory, store=Store())
    assert out["status"] == "inactive" and "20/50" in out["notes"]
    assert model.predict([{"hook_type": "pov"}], session_factory=session_factory) is None


def test_model_activates_on_real_signal_and_ranks_traits(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    _creatives(session_factory, 80, signal=True)
    store = Store()
    out = model.train(session_factory=session_factory, store=store)
    assert out["status"] == "active" and out["metrics"]["improvement"] > 0.5
    assert out["metrics"]["top_features"][0]["feature"].startswith("hook_type=")
    base = {
        "avatar_type": "w25",
        "angle": "saves_time",
        "length_bucket": "0-8s",
        "format": "9x16_ugc_video",
        "cta": "shop_now",
        "voiceover": True,
        "kind": "video",
        "duration_seconds": 8,
    }
    pov, talking, unseen = model.predict(
        [
            base | {"hook_type": "pov"},
            base | {"hook_type": "talking_head"},
            base | {"hook_type": "brand_new_hook"},
        ],
        session_factory=session_factory,
        store=store,
    )
    assert pov > 500 > talking and unseen is not None  # unseen values map to "other"
    with session_factory() as s:
        st = model.status(s)
    assert st["active"] and st["labeled_creatives"] == 80


def test_model_stays_inactive_on_noise(session_factory) -> None:  # type: ignore[no-untyped-def]
    _creatives(session_factory, 80, signal=False)
    out = model.train(session_factory=session_factory, store=Store())
    assert out["status"] == "inactive" and "not better than predicting the average" in out["notes"]


def test_registry_and_tools() -> None:
    import anyio

    from app.jobs.registry import JOBS
    from app.mcpserver.server import server

    names = [j.name for j in JOBS]
    assert len(names) == len(set(names)), "duplicate job names in the registry"
    crons = {j.name: j.cron for j in JOBS if j.cron}
    # metrics before the bandit, bandit before the 08:00 report
    assert crons["creative_metrics"] == "30 2 * * *" and crons["budget_bandit"] == "45 6 * * *"
    assert crons["daily_report"] == "0 8 * * *"
    tools = {t.name for t in anyio.run(server.list_tools)}
    assert {"get_budget_recommendation", "get_model_status", "propose_budget_reallocation"} <= tools
