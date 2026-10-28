"""Shared fixtures.

Database tests run against a fresh SQLite file by default. Set ``TEST_DATABASE_URL``
(e.g. ``postgresql+psycopg://hub:hub@localhost:55432/hub_test``) to run the same tests
against real Postgres; the database is migrated down to base before and after.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

# Never read the deployment's .env during tests (must run before app imports).
os.environ["HUB_ENV_FILE"] = ""

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]


def alembic_config(connection: object) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.attributes["connection"] = connection
    cfg.attributes["skip_logging_config"] = True
    return cfg


@pytest.fixture
def db_url(tmp_path: Path) -> str:
    return os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def engine(db_url: str) -> Iterator[Engine]:
    """An engine on a database migrated to head (and cleaned up afterwards)."""
    eng = create_engine(db_url, future=True)
    if eng.dialect.name == "sqlite":

        @event.listens_for(eng, "connect")
        def _fk_on(dbapi_conn, _record):  # type: ignore[no-untyped-def]
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

    with eng.begin() as conn:
        command.downgrade(alembic_config(conn), "base")
        command.upgrade(alembic_config(conn), "head")
    yield eng
    with eng.begin() as conn:
        command.downgrade(alembic_config(conn), "base")
    eng.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine, expire_on_commit=False) as s:
        yield s


@pytest.fixture
def session_factory(engine: Engine):  # type: ignore[no-untyped-def]
    """A ``session_scope``-style factory bound to the test database (commit on exit)."""
    from contextlib import contextmanager

    @contextmanager
    def _scope() -> Iterator[Session]:
        with Session(engine, expire_on_commit=False) as s:
            yield s
            s.commit()

    return _scope


@pytest.fixture
def writes_on(session_factory):  # type: ignore[no-untyped-def]
    """Turn read-only mode off for a test (the default is on)."""
    from app import business_settings

    with session_factory() as s:
        business_settings.set_value(s, "read_only", False, actor="test")
    return session_factory


def seed_entity(
    factory,
    platform: str,
    campaign_id: str,
    budget=None,
    ad_set_id: str | None = None,  # type: ignore[no-untyped-def]
    ad_set_budget=None,
    status: str = "active",
    cap: str | None = "1000",
) -> None:
    """Synced campaign (+ optional ad set) rows so guardrails can check budget changes."""
    from decimal import Decimal

    from sqlalchemy import select

    from app import business_settings
    from app.models import AdAccount, AdSet, Campaign, EntityStatus, Platform

    with factory() as s:
        acct = s.scalar(
            select(AdAccount).where(AdAccount.platform == Platform(platform))
        ) or AdAccount(platform=Platform(platform), external_id=f"acct-{platform}")
        camp = Campaign(
            ad_account=acct,
            platform=Platform(platform),
            external_id=campaign_id,
            name="Test campaign",
            status=EntityStatus(status),
            daily_budget=Decimal(str(budget)) if budget is not None else None,
        )
        s.add(camp)
        if ad_set_id:
            s.add(
                AdSet(
                    campaign=camp,
                    platform=Platform(platform),
                    external_id=ad_set_id,
                    name="Test ad set",
                    status=EntityStatus(status),
                    daily_budget=Decimal(str(ad_set_budget)) if ad_set_budget is not None else None,
                )
            )
        if cap is not None:
            business_settings.set_value(s, "daily_spend_cap", cap, actor="test")
