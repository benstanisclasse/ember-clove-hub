"""Phase 6: hard limits, enforcement inside platform writes, kill switch, daily report, scheduling."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal as D
from typing import Any

import anyio
import pytest
from ads_mock import MockHTTP
from conftest import seed_entity
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import business_settings, guardrails
from app.actions import write_action
from app.config import Settings, get_settings
from app.integrations.ads.meta import MetaAds
from app.models import (
    ActionLog,
    ActionStatus,
    Ad,
    AdMetricsDaily,
    AdSet,
    Campaign,
    EntityStatus,
    Platform,
)

G = guardrails.GuardrailError


def _set(factory, **kv: Any) -> None:  # type: ignore[no-untyped-def]
    with factory() as s:
        for k, v in kv.items():
            business_settings.set_value(s, k, v, actor="test")


def test_committed_budget_counts_only_what_can_spend(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "cbo", budget="100")  # campaign budget
    seed_entity(
        session_factory, "tiktok", "abo", ad_set_id="g1", ad_set_budget="30"
    )  # ad set budget
    seed_entity(
        session_factory, "google", "off", budget="500", status="paused"
    )  # paused: not counted
    with session_factory() as s:
        camp = s.scalar(select(Campaign).where(Campaign.external_id == "abo"))
        s.add(
            AdSet(
                campaign_id=camp.id,
                platform=Platform.TIKTOK,
                external_id="g2",
                status=EntityStatus.PAUSED,
                daily_budget=D("999"),
            )
        )
    assert guardrails.committed_daily_budget(session) == D("130")


def test_spend_cap_not_set_blocks_increases_but_allows_cuts(session_factory) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "c1", budget="100", cap=None)
    with session_factory() as s:
        with pytest.raises(G, match="daily_spend_cap is not set"):
            guardrails.enforce_budget(s, "meta", "campaign", "c1", D("110"))
        guardrails.enforce_budget(s, "meta", "campaign", "c1", D("90"))  # decrease: fine


def test_spend_cap_and_today_spend(session_factory) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "c1", budget="100", cap="150")
    seed_entity(session_factory, "tiktok", "c2", budget="40", cap="150")
    _set(session_factory, max_budget_change_pct=50)
    with session_factory() as s:
        guardrails.enforce_budget(
            s, "meta", "campaign", "c1", D("110")
        )  # 110 + 40 = 150: at the cap, ok
        with pytest.raises(G, match="above daily_spend_cap"):
            guardrails.enforce_budget(s, "meta", "campaign", "c1", D("115"))
    with session_factory() as s:  # today's spend already at the cap: no increases at all
        ad_set = AdSet(
            campaign_id=s.scalar(select(Campaign.id).where(Campaign.external_id == "c2")),
            platform=Platform.TIKTOK,
            external_id="s9",
            status=EntityStatus.ACTIVE,
        )
        s.add(ad_set)
        s.flush()
        ad = Ad(
            ad_set_id=ad_set.id,
            platform=Platform.TIKTOK,
            external_id="a9",
            status=EntityStatus.ACTIVE,
        )
        s.add(ad)
        s.flush()
        s.add(
            AdMetricsDaily(ad_id=ad.id, date=datetime.now(get_settings().tz).date(), spend=D("150"))
        )
    with session_factory() as s, pytest.raises(G, match="already reached"):
        guardrails.enforce_budget(s, "tiktok", "campaign", "c2", D("41"))


def test_daily_change_limit_is_cumulative(session_factory) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "c1", budget="100")
    _set(session_factory, read_only=False)  # max_budget_change_pct default 20
    # A first change today 100 -> 115 succeeded (recorded the way AdPlatform.update_budget records it).
    with write_action(
        "meta.update_budget",
        target_type="campaign",
        target_id="c1",
        payload={"level": "campaign", "daily_budget": "115", "previous_daily_budget": "100"},
        session_factory=session_factory,
    ):
        pass
    with session_factory() as s:
        s.scalar(select(Campaign).where(Campaign.external_id == "c1")).daily_budget = D("115")
    with session_factory() as s:
        guardrails.enforce_budget(s, "meta", "campaign", "c1", D("120"))  # +20% vs today's 100: ok
        with pytest.raises(G, match="today's starting budget 100"):
            guardrails.enforce_budget(
                s, "meta", "campaign", "c1", D("125")
            )  # +25% vs 100, though +8.7% vs 115


def test_activation_and_unknown_entities(session_factory) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "live", budget="80", cap="100")
    seed_entity(session_factory, "meta", "new", budget="30", status="paused", cap="100")
    with session_factory() as s:
        with pytest.raises(G, match="activating campaign new"):
            guardrails.enforce_activation(s, "meta", "campaign", "new")  # 80 + 30 > 100
        with pytest.raises(G, match="not synced"):
            guardrails.enforce_budget(s, "meta", "campaign", "ghost", D("10"))
    _set(session_factory, daily_spend_cap="120")
    with session_factory() as s:
        guardrails.enforce_activation(s, "meta", "campaign", "new")


def test_new_ads_per_day(session_factory) -> None:  # type: ignore[no-untyped-def]
    _set(session_factory, read_only=False, max_new_ads_per_day=2)
    for _ in range(2):
        with write_action(
            "meta.create_ad",
            target_type="ad",
            target_id=None,
            payload={},
            session_factory=session_factory,
        ):
            pass
    with (
        session_factory() as s,
        pytest.raises(G, match="max_new_ads_per_day is 2; 2 created today"),
    ):
        guardrails.enforce_new_ads(s, 1)


def test_platform_write_is_blocked_before_any_http_call(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    seed_entity(session_factory, "meta", "c1", budget="50")
    _set(session_factory, read_only=False)
    mock = MockHTTP()
    meta = MetaAds(
        Settings(meta_system_user_token=SecretStr("EAAx"), meta_ad_account_id="1"),
        http=mock.client(),
        sleep=lambda s: None,
        session_factory=session_factory,
    )
    with pytest.raises(G):
        meta.update_budget("campaign", "c1", D("100"))  # +100%
    assert mock.calls == []
    log = session.scalars(
        select(ActionLog).where(ActionLog.action_type == "meta.update_budget")
    ).one()
    assert log.status == ActionStatus.BLOCKED and "max_budget_change_pct" in log.error
    assert log.payload["previous_daily_budget"] == "50.00"


def test_kill_switch_blocks_everything_and_alerts(
    session_factory, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    import app.alerts as alerts

    sent: list[str] = []
    monkeypatch.setattr(alerts, "send_slack", lambda text, settings=None: sent.append(text) or True)
    seed_entity(session_factory, "meta", "c1", budget="50")
    _set(session_factory, read_only=False, kill_switch=True)
    assert any("Kill switch ON" in t for t in sent)
    with session_factory() as s:
        for fn in (
            lambda: guardrails.enforce_budget(s, "meta", "campaign", "c1", D("45")),
            lambda: guardrails.enforce_new_ads(s, 1),
            lambda: guardrails.check_action(s, "pause_ad", {}),
        ):
            with pytest.raises(G, match="kill switch"):
                fn()


def test_emergency_stop_tool_only_turns_it_on(
    db_url: str, engine, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    import app.db as db
    from app.config import get_settings
    from app.mcpserver.server import server

    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()
    try:
        names = {t.name for t in anyio.run(server.list_tools)}
        assert "emergency_stop" in names and not any("resume" in n or "kill" in n for n in names)
        anyio.run(server.call_tool, "emergency_stop", {"reason": "CPA spiking"})
        with db.session_scope() as s:
            assert business_settings.load(s).kill_switch is True
    finally:
        get_settings.cache_clear()
        db.get_engine.cache_clear()
        db._session_factory.cache_clear()


def test_daily_report_and_job(session_factory, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    from test_mcp import seed

    from app import daily_report

    with session_factory() as s:
        seed(s)
    with session_factory() as s:
        r = daily_report.build(s, day=date(2026, 10, 1))
    assert (
        r["summary"]["contribution_profit_after_ads"] == 139.02 and r["top_creative"]["creative_id"]
    )
    text = daily_report.format_slack(r)
    assert (
        "daily summary: 2026-10-01" in text and "139.02 USD" in text and "meta: spend 40.00" in text
    )
    assert "without a unit cost" in text


def test_scheduler_runs_cron_jobs_on_time_not_paused() -> None:
    from apscheduler.triggers.cron import CronTrigger

    from app.scheduler import build_scheduler

    sched = build_scheduler(start_now=True)  # not started: jobs are still pending
    job = sched.get_job("daily_report")
    assert isinstance(job.trigger, CronTrigger)
    assert "hour='8'" in str(job.trigger)
    assert getattr(job, "next_run_time", "pending") is not None  # None would mean the job is paused
