"""Migration round-trip, model/migration drift, and runtime business settings."""

from __future__ import annotations

from decimal import Decimal

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app import business_settings as bs
from app.models import ActionLog, ActionStatus, Base, Setting


def test_models_match_migrations(engine: Engine) -> None:
    """Fails if a model changed without a matching migration."""
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn, opts={"compare_type": True})
        diff = [d for d in compare_metadata(ctx, Base.metadata) if d[0] != "remove_table"]
    assert diff == []


def test_seed_matches_code_defaults(session: Session) -> None:
    stored = {r.key: r.value for r in session.scalars(select(Setting))}
    defaults = bs.BusinessSettings().model_dump(mode="json")
    assert set(stored) == set(defaults)
    assert bs.BusinessSettings.model_validate(stored) == bs.BusinessSettings()


def test_safe_defaults(session: Session) -> None:
    s = bs.load(session)
    assert s.read_only is True
    assert s.kill_switch is False
    assert s.writes_allowed is False
    assert s.daily_spend_cap is None and s.higgsfield_monthly_cap_usd is None


def test_set_value_validates_and_audits(session: Session) -> None:
    updated = bs.set_value(session, "daily_spend_cap", "250.00", actor="cli", requested_by="ben")
    session.commit()
    assert updated.daily_spend_cap == Decimal("250.00")
    assert bs.load(session).daily_spend_cap == Decimal("250.00")

    log = session.scalars(select(ActionLog).where(ActionLog.action_type == "setting_change")).one()
    assert log.status == ActionStatus.SUCCESS
    assert log.payload == {"old": None, "new": "250.00"}
    assert log.target_id == "daily_spend_cap"


def test_writes_allowed_needs_read_only_off_and_no_kill_switch(session: Session) -> None:
    bs.set_value(session, "read_only", False, actor="cli")
    assert bs.load(session).writes_allowed is True
    bs.set_value(session, "kill_switch", True, actor="cli")
    assert bs.load(session).writes_allowed is False


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("max_budget_change_pct", 0),
        ("max_budget_change_pct", 150),
        ("max_new_ads_per_day", -1),
        ("daily_spend_cap", "-5"),
        ("auto_approve_rules", [{"name": "x"}]),
    ],
)
def test_set_value_rejects_invalid(session: Session, key: str, value: object) -> None:
    with pytest.raises(ValueError):
        bs.set_value(session, key, value, actor="cli")


def test_set_value_rejects_unknown_key(session: Session) -> None:
    with pytest.raises(KeyError):
        bs.set_value(session, "no_such_setting", 1, actor="cli")


def test_blank_api_versions_fall_back_to_pins(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import Settings

    for key in (
        "GOOGLE_ADS_API_VERSION",
        "META_API_VERSION",
        "TIKTOK_API_VERSION",
        "SHOPIFY_API_VERSION",
    ):
        monkeypatch.setenv(key, "")
    s = Settings()
    assert (s.google_ads_api_version, s.meta_api_version) == ("v25", "v26.0")
    assert (s.tiktok_api_version, s.shopify_api_version) == ("v1.3", "2026-07")
    monkeypatch.setenv("META_API_VERSION", "v25.0")
    assert Settings().meta_api_version == "v25.0"


def test_cli_reports_unconfigured_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    from app.cli import main

    assert main(["higgsfield", "models"]) == 3
    assert "not configured" in capsys.readouterr().err
