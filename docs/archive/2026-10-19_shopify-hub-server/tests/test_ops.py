"""API routes, alerts, watchdog, job tracking and storage (all external calls mocked)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

import boto3
import fakeredis
import pytest
from botocore.stub import Stubber
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app import alerts, health
from app.alerts import Alerter
from app.config import Settings, get_settings
from app.health import CheckResult
from app.jobs import registry, watchdog
from app.jobs.tracking import last_success, track_job
from app.models import JobRun, JobRunStatus
from app.storage import ObjectStore


@pytest.fixture
def factory(engine: Engine):  # type: ignore[no-untyped-def]
    @contextmanager
    def _scope() -> Iterator[Session]:
        with Session(engine, expire_on_commit=False) as s:
            yield s
            s.commit()

    return _scope


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    messages: list[str] = []
    monkeypatch.setattr(
        alerts, "send_slack", lambda text, settings=None: messages.append(text) or True
    )
    return messages


# --- API ------------------------------------------------------------------------------


@pytest.fixture
def client(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
    monkeypatch.setenv("LOG_JSON", "false")
    get_settings.cache_clear()
    from app.db import get_session
    from app.main import app

    def _session() -> Iterator[Session]:
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = _session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_healthz_is_minimal(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_ready_reports_503_when_a_dependency_fails(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.main as main

    monkeypatch.setattr(main, "get_redis", lambda: None)
    monkeypatch.setattr(
        main,
        "readiness",
        lambda _r: [CheckResult("database", True), CheckResult("redis", False, "down")],
    )
    resp = client.get("/health/ready")
    assert resp.status_code == 503
    assert resp.json()["status"] == "degraded"


def test_admin_settings_requires_token(client: TestClient) -> None:
    assert client.get("/admin/settings").status_code == 401
    assert (
        client.get("/admin/settings", headers={"Authorization": "Bearer nope"}).status_code == 401
    )
    resp = client.get("/admin/settings", headers={"Authorization": "Bearer test-admin-token"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["read_only"] is True and body["writes_allowed"] is False


# --- Alerts + watchdog ------------------------------------------------------------------


def test_alert_dedupes_within_cooldown_and_resolves_once(sent: list[str]) -> None:
    a = Alerter(fakeredis.FakeRedis(), Settings(alert_cooldown_minutes=60))
    assert a.fire("health:redis", "redis down")
    assert not a.fire("health:redis", "redis down")  # suppressed
    assert a.resolve("health:redis")
    assert not a.resolve("health:redis")  # nothing active any more
    assert len(sent) == 2 and "redis down" in sent[0]


def test_alert_still_sent_when_redis_is_down(sent: list[str]) -> None:
    class Broken:
        def set(self, *a: object, **k: object) -> None:
            raise ConnectionError("redis gone")

    assert Alerter(Broken(), Settings()).fire("health:x", "x broke")
    assert len(sent) == 1


def test_watchdog_evaluate_fires_and_resolves(sent: list[str]) -> None:
    a = Alerter(fakeredis.FakeRedis(), Settings())
    assert not watchdog.evaluate([CheckResult("storage", False, "timeout")], a)
    assert watchdog.evaluate([CheckResult("storage", True)], a)
    assert len(sent) == 2 and "recovered" not in sent[0] and "healthy again" in sent[1]


def test_heartbeat_hits_fail_endpoint_when_unhealthy(monkeypatch: pytest.MonkeyPatch) -> None:
    urls: list[str] = []
    monkeypatch.setattr(watchdog.httpx, "get", lambda url, timeout: urls.append(url))
    watchdog.ping_heartbeat("https://hc-ping.com/abc", healthy=True)
    watchdog.ping_heartbeat("https://hc-ping.com/abc", healthy=False)
    watchdog.ping_heartbeat("", healthy=True)  # not configured: no call
    assert urls == ["https://hc-ping.com/abc", "https://hc-ping.com/abc/fail"]


def test_run_check_scrubs_secrets_from_errors() -> None:
    def boom() -> None:
        raise RuntimeError("connect to postgresql+psycopg://hub:topsecret@db failed")

    r = health.run_check("database", boom)
    assert not r.ok and "topsecret" not in r.detail


# --- Job tracking + staleness ---------------------------------------------------------


def test_track_job_records_success_and_failure(factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    with track_job("demo", session_factory=factory) as stats:
        stats["rows"] = 3
    with pytest.raises(ValueError), track_job("demo", session_factory=factory):
        raise ValueError("bad token shpat_" + "f" * 32)

    runs = session.scalars(select(JobRun).order_by(JobRun.id)).all()
    assert [r.status for r in runs] == [JobRunStatus.SUCCESS, JobRunStatus.FAILED]
    assert runs[0].stats["rows"] == 3
    assert "shpat_" not in (runs[1].error or "")
    assert last_success(session, "demo") is not None


def test_stale_jobs(factory, session: Session, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        registry, "JOBS", [registry.JobSpec("sync_x", "x.y", 60, stale_after_minutes=90)]
    )
    assert health.stale_jobs(session) == []  # brand-new job: not stale yet
    session.commit()  # stale_jobs recorded "first seen"; release the SQLite write lock
    later = health.stale_jobs(session, now=datetime.now(UTC) + timedelta(hours=2))
    assert len(later) == 1 and later[0].startswith("sync_x (last ok: never")
    with track_job("sync_x", session_factory=factory):
        pass
    assert health.stale_jobs(session) == []
    assert health.stale_jobs(session, now=datetime.now(UTC) + timedelta(hours=2))


# --- Storage ----------------------------------------------------------------------------


def test_ensure_bucket_creates_when_missing() -> None:
    client = boto3.client(
        "s3", region_name="us-east-1", aws_access_key_id="x", aws_secret_access_key="y"
    )
    settings = Settings(s3_bucket="hub-creatives", s3_public_base_url="https://cdn.example.com")
    with Stubber(client) as stub:
        stub.add_client_error("head_bucket", service_error_code="404", http_status_code=404)
        stub.add_response("create_bucket", {}, {"Bucket": "hub-creatives"})
        store = ObjectStore(settings, client=client)
        assert store.ensure_bucket() is True
    assert store.url_for("creatives/1.mp4") == "https://cdn.example.com/creatives/1.mp4"
    assert ObjectStore(Settings(s3_bucket="b"), client=client).url_for("k") == "s3://b/k"
