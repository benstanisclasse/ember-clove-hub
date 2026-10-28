"""Briefs/variants/traits, budget cap, generate -> poll -> store, webhook, launch."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app import business_settings
from app.actions import WritesBlockedError
from app.config import Settings, get_settings
from app.creatives import media, pipeline
from app.creatives.briefs import CreativeBrief, length_bucket, make_variants
from app.integrations.ads.base import CreatedCampaign
from app.integrations.higgsfield import Estimate, JobStatus, Submission
from app.integrations.http import IntegrationError
from app.models import (
    Ad,
    Creative,
    CreativeAdLink,
    CreativeStatus,
    CreativeTrait,
    GenerationJob,
    GenerationStatus,
    Product,
)

SETTINGS = Settings(
    higgsfield_api_key=SecretStr("k"),
    higgsfield_api_secret=SecretStr("s"),
    higgsfield_video_model="kling/v3/i2v",
    public_base_url="https://hub.example.com",
    higgsfield_webhook_token=SecretStr("tok123"),
    google_ads_logo_asset="customers/1/assets/logo",
)

# --- briefs ----------------------------------------------------------------------------------


def test_variants_rotate_and_record_traits() -> None:
    brief = CreativeBrief(
        angles=["saves_time", "results"],
        hook_types=["pov"],
        avatar_types=["woman_25_34", "man_45_54"],
        hooks=["Line A", "Line B", "Line C"],
        duration_seconds=12,
        product_name="GlowSerum",
        product_id=3,
        reference_image_url="https://cdn/p.jpg",
        extra_params={"resolution": "720p"},
    )
    vs = make_variants(brief, 5, "kling/v3/i2v")
    assert [(v.traits["angle"], v.traits["avatar_type"]) for v in vs][:4] == [
        ("saves_time", "woman_25_34"),
        ("saves_time", "man_45_54"),
        ("results", "woman_25_34"),
        ("results", "man_45_54"),
    ]
    v = vs[0]
    assert v.traits | {} == {
        "hook_type": "pov",
        "avatar_type": "woman_25_34",
        "length_bucket": "9-15s",
        "product_id": 3,
        "voiceover": True,
        "format": "9x16_ugc_video",
        "angle": "saves_time",
        "cta": "shop_now",
    }
    assert v.params == {
        "prompt": v.prompt,
        "aspect_ratio": "9:16",
        "duration": 12,
        "image_url": "https://cdn/p.jpg",
        "resolution": "720p",
    }
    assert (
        '"Line A"' in v.prompt
        and "GlowSerum" in v.prompt
        and vs[3].extra_traits["hook_line"] == "Line A"
    )
    assert (
        make_variants(brief, 5, "m")[2].prompt == make_variants(brief, 5, "m")[2].prompt
    )  # deterministic
    with pytest.raises(ValueError):
        make_variants(brief, 0, "m")


def test_length_buckets() -> None:
    assert [length_bucket("video", s) for s in (5, 8, 9, 15, 30, 45, 90)] == [
        "0-8s",
        "0-8s",
        "9-15s",
        "9-15s",
        "16-30s",
        "31-60s",
        "60s+",
    ]
    assert length_bucket("image", 8) == "static"


def test_brief_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError):
        CreativeBrief.model_validate({"kind": "video", "budget": 10})


# --- fakes -----------------------------------------------------------------------------------


class FakeHF:
    def __init__(self, usd: str = "0.50", prefix: str = "r") -> None:
        self.usd, self.prefix = D(usd), prefix
        self.submitted: list[tuple[str, dict[str, Any], str | None, str | None]] = []
        self.statuses: dict[str, JobStatus] = {}
        self.fail_submit_after: int | None = None
        self.cancelled: list[str] = []

    def estimate(self, model: str, params: dict[str, Any]) -> Estimate:
        return Estimate(credits=D("8"), usd=self.usd)

    def submit(
        self,
        model: str,
        params: dict[str, Any],
        idempotency_key: str | None = None,
        webhook_url: str | None = None,
    ) -> Submission:
        if self.fail_submit_after is not None and len(self.submitted) >= self.fail_submit_after:
            raise IntegrationError("Too many concurrent requests", retryable=True)
        rid = f"{self.prefix}{len(self.submitted) + 1}"
        self.submitted.append((model, params, idempotency_key, webhook_url))
        return Submission(rid, "queued")

    def status(self, request_id: str) -> JobStatus:
        return self.statuses.get(request_id, JobStatus(request_id, "queued"))

    def cancel(self, request_id: str) -> None:
        self.cancelled.append(request_id)

    def download(self, url: str) -> tuple[bytes, str]:
        return b"VIDEO-BYTES", "video/mp4"


class FakeStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put(self, key: str, body: bytes, content_type: str) -> str:
        self.objects[key] = body
        return f"s3://hub-creatives/{key}"

    def get_bytes(self, key: str) -> bytes:
        return self.objects[key]


def _setup(factory, cap: str | None = "10", read_only: bool = False) -> None:  # type: ignore[no-untyped-def]
    with factory() as s:
        s.add(Product(shopify_id=1, title="GlowSerum"))
        business_settings.set_value(s, "read_only", read_only, actor="test")
        business_settings.set_value(s, "higgsfield_monthly_cap_usd", cap, actor="test")


# --- budget + generation ------------------------------------------------------------------------


def test_generation_blocked_without_cap_or_in_read_only(session_factory) -> None:  # type: ignore[no-untyped-def]
    _setup(session_factory, cap=None)
    hf = FakeHF()
    with pytest.raises(pipeline.BudgetExceededError, match="not set"):
        pipeline.generate_creatives(
            CreativeBrief(), 2, client=hf, session_factory=session_factory, settings=SETTINGS
        )
    with session_factory() as s:
        business_settings.set_value(s, "higgsfield_monthly_cap_usd", "10", actor="t")
        business_settings.set_value(s, "read_only", True, actor="t")
    with pytest.raises(WritesBlockedError):
        pipeline.generate_creatives(
            CreativeBrief(), 2, client=hf, session_factory=session_factory, settings=SETTINGS
        )
    assert hf.submitted == []


def test_batch_must_fit_under_cap_all_or_nothing(session_factory) -> None:  # type: ignore[no-untyped-def]
    _setup(session_factory, cap="1.20")
    hf = FakeHF(usd="0.50")
    with pytest.raises(pipeline.BudgetExceededError, match=r"1\.20"):
        pipeline.generate_creatives(
            CreativeBrief(), 3, client=hf, session_factory=session_factory, settings=SETTINGS
        )
    assert hf.submitted == []
    res = pipeline.generate_creatives(
        CreativeBrief(), 2, client=hf, session_factory=session_factory, settings=SETTINGS
    )
    assert len(res.creative_ids) == 2 and res.estimated_usd == D("1.00")
    with pytest.raises(pipeline.BudgetExceededError):  # $1.00 committed + $0.50 > $1.20
        pipeline.generate_creatives(
            CreativeBrief(), 1, client=hf, session_factory=session_factory, settings=SETTINGS
        )


def test_generate_records_creatives_traits_jobs(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    _setup(session_factory)
    hf = FakeHF()
    brief = CreativeBrief(product_id=1, angles=["a1", "a2"])
    res = pipeline.generate_creatives(
        brief, 2, client=hf, session_factory=session_factory, settings=SETTINGS
    )
    creatives = session.scalars(select(Creative).order_by(Creative.id)).all()
    assert [c.status for c in creatives] == [CreativeStatus.GENERATING] * 2
    assert "GlowSerum" in creatives[0].prompt and creatives[0].brief["product_name"] == "GlowSerum"
    traits = session.scalars(select(CreativeTrait).order_by(CreativeTrait.creative_id)).all()
    assert [t.angle for t in traits] == ["a1", "a2"] and traits[0].extra["model"] == "kling/v3/i2v"
    jobs = session.scalars(select(GenerationJob).order_by(GenerationJob.id)).all()
    assert [j.higgsfield_job_id for j in jobs] == ["r1", "r2"] and jobs[0].cost_usd == D("0.50")
    _model, _params, idem, hook = hf.submitted[0]
    assert (
        idem == f"hub-job-{jobs[0].id}"
        and hook == "https://hub.example.com/webhooks/higgsfield/tok123"
    )
    assert res.creative_ids == [c.id for c in creatives]


def test_failed_submit_refunds_and_continues(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    _setup(session_factory)
    hf = FakeHF()
    hf.fail_submit_after = 1
    res = pipeline.generate_creatives(
        CreativeBrief(), 2, client=hf, session_factory=session_factory, settings=SETTINGS
    )
    assert len(res.creative_ids) == 1 and len(res.errors) == 1
    failed = session.scalars(
        select(GenerationJob).where(GenerationJob.status == GenerationStatus.FAILED)
    ).one()
    assert failed.cost_usd == D("0")
    with session_factory() as s:
        assert pipeline.monthly_spend(s) == D("0.50")


# --- polling -------------------------------------------------------------------------------------


def _one_job(session_factory) -> tuple[FakeHF, int]:  # type: ignore[no-untyped-def]
    _setup(session_factory)
    hf = FakeHF()
    pipeline.generate_creatives(
        CreativeBrief(), 1, client=hf, session_factory=session_factory, settings=SETTINGS
    )
    with session_factory() as s:
        return hf, pipeline.active_job_ids(s)[0]


def test_poll_completed_stores_output(
    session_factory, session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        media, "probe", lambda c, m: {"width": 720, "height": 1280, "duration": 8.04}
    )
    hf, job_id = _one_job(session_factory)
    store = FakeStore()
    assert (
        pipeline.poll_job(
            job_id, client=hf, store=store, session_factory=session_factory, settings=SETTINGS
        )
        == "queued"
    )
    hf.statuses["r1"] = JobStatus("r1", "completed", video_url="https://cdn/out.mp4")
    assert (
        pipeline.poll_job(
            job_id, client=hf, store=store, session_factory=session_factory, settings=SETTINGS
        )
        == "completed"
    )
    c = session.scalars(select(Creative)).one()
    assert c.status == CreativeStatus.READY and c.storage_key == f"creatives/{c.id}/{job_id}.mp4"
    assert store.objects[c.storage_key] == b"VIDEO-BYTES"
    assert (c.width, c.height, c.duration_seconds, c.cost_usd) == (720, 1280, D("8.04"), D("0.50"))
    assert (
        pipeline.poll_job(
            job_id, client=hf, store=store, session_factory=session_factory, settings=SETTINGS
        )
        == "skip"
    )


def test_poll_nsfw_refunds_and_timeout_cancels(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    hf, job_id = _one_job(session_factory)
    hf.statuses["r1"] = JobStatus("r1", "nsfw", error="moderated")
    pipeline.poll_job(
        job_id, client=hf, store=FakeStore(), session_factory=session_factory, settings=SETTINGS
    )
    job = session.get(GenerationJob, job_id)
    assert (job.status, job.cost_usd, job.error) == (GenerationStatus.FAILED, D("0"), "moderated")
    assert session.scalars(select(Creative)).one().status == CreativeStatus.FAILED

    hf2 = FakeHF(prefix="t")
    pipeline.generate_creatives(
        CreativeBrief(), 1, client=hf2, session_factory=session_factory, settings=SETTINGS
    )
    with session_factory() as s:
        job2 = pipeline.active_job_ids(s)[0]
    later = datetime.now(UTC) + timedelta(hours=3)
    assert (
        pipeline.poll_job(
            job2,
            client=hf2,
            store=FakeStore(),
            session_factory=session_factory,
            settings=SETTINGS,
            now=later,
        )
        == "timeout"
    )
    assert hf2.cancelled == ["t1"]


# --- webhook ---------------------------------------------------------------------------------------


@pytest.fixture
def api(
    db_url: str, engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[TestClient, list[str]]]:
    import app.db as db
    from app import webhooks

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("HIGGSFIELD_WEBHOOK_TOKEN", "tok123")
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()
    polled: list[str] = []
    monkeypatch.setattr(webhooks, "_enqueue_higgsfield_poll", polled.append)
    from app.main import app

    with TestClient(app) as c:
        yield c, polled
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()


def test_higgsfield_webhook_needs_secret_token(api) -> None:  # type: ignore[no-untyped-def]
    client, polled = api
    payload = json.dumps({"request_id": "r1", "status": "completed", "payload": {}})
    assert client.post("/webhooks/higgsfield/wrong", content=payload).status_code == 404
    assert client.post("/webhooks/higgsfield/tok123", content=payload).status_code == 200
    assert client.post("/webhooks/higgsfield/tok123", content="nope").status_code == 400
    assert polled == ["r1"]


# --- launch ----------------------------------------------------------------------------------------


class FakePlatform:
    def __init__(self, name: str) -> None:
        self.name, self.calls = name, []
        self.account_external_id = f"{name}-acct"

    def upload_video(self, media_upload: Any, ctx: Any = None) -> str:
        self.calls.append(("video", media_upload.filename))
        return f"{self.name}-vid"

    def upload_image(self, media_upload: Any, ctx: Any = None) -> str:
        self.calls.append(("image", media_upload.filename))
        return f"{self.name}-img"

    def create_campaign(self, spec: Any, ctx: Any = None) -> CreatedCampaign:
        self.calls.append(("campaign", str(spec.daily_budget)))
        return CreatedCampaign(campaign_id=f"{self.name}-c1", ad_set_id=f"{self.name}-s1")

    def create_ad(self, spec: Any, ctx: Any = None) -> str:
        self.calls.append(("ad", spec.ad_set_id, spec.video_asset_id, spec.image_asset_id))
        return f"{self.name}-ad1"


def _ready_creative(session_factory, store: FakeStore) -> int:  # type: ignore[no-untyped-def]
    with session_factory() as s:
        c = Creative(
            type="video",
            status=CreativeStatus.READY,
            storage_key="creatives/1/1.mp4",
            mime_type="video/mp4",
            brief={"product_name": "GlowSerum"},
        )
        s.add(c)
        s.flush()
        store.objects["creatives/1/1.mp4"] = b"VIDEO"
        return c.id


def test_launch_creates_paused_ads_and_links(
    session_factory, session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    _setup(session_factory)
    monkeypatch.setattr(media, "thumbnail", lambda v, m: b"JPEG")
    store = FakeStore()
    cid = _ready_creative(session_factory, store)
    fakes = {p: FakePlatform(p) for p in ("meta", "google")}
    req = pipeline.LaunchRequest(
        creative_id=cid,
        platforms=["meta", "google"],
        landing_url="https://shop.com/p",
        primary_text="Try it",
        daily_budget=D("25"),
    )
    out = pipeline.launch_creative(
        req,
        platform_factory=fakes.__getitem__,
        store=store,
        session_factory=session_factory,
        settings=SETTINGS,
    )
    assert out["meta"] == {
        "ad_id": "meta-ad1",
        "ad_set_id": "meta-s1",
        "campaign_id": "meta-c1",
        "status": "paused",
    }
    assert ("image", "thumb.jpg") in fakes["meta"].calls  # thumbnail uploaded for Meta
    assert fakes["google"].calls[-1] == (
        "ad",
        "google-s1",
        "google-vid",
        "customers/1/assets/logo",
    )  # logo for Google
    session.expire_all()
    assert session.get(Creative, cid).status == CreativeStatus.LAUNCHED
    links = session.scalars(select(CreativeAdLink)).all()
    assert {(link.platform.value, link.external_ad_id) for link in links} == {
        ("meta", "meta-ad1"),
        ("google", "google-ad1"),
    }
    assert session.scalar(select(Ad).where(Ad.external_id == "meta-ad1")).status.value == "paused"


def test_launch_reports_per_platform_errors(
    session_factory, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    _setup(session_factory)
    monkeypatch.setattr(media, "thumbnail", lambda v, m: b"JPEG")
    store = FakeStore()
    cid = _ready_creative(session_factory, store)
    req = pipeline.LaunchRequest(
        creative_id=cid, platforms=["tiktok"], landing_url="u", primary_text="t"
    )  # no budget
    out = pipeline.launch_creative(
        req,
        platform_factory=FakePlatform,
        store=store,
        session_factory=session_factory,
        settings=SETTINGS,
    )
    assert "daily_budget is required" in out["tiktok"]["error"]


def test_launch_blocked_in_read_only(session_factory) -> None:  # type: ignore[no-untyped-def]
    _setup(session_factory, read_only=True)
    store = FakeStore()
    cid = _ready_creative(session_factory, store)
    req = pipeline.LaunchRequest(
        creative_id=cid, platforms=["meta"], landing_url="u", primary_text="t", daily_budget=D("5")
    )
    with pytest.raises(WritesBlockedError):
        pipeline.launch_creative(
            req,
            platform_factory=FakePlatform,
            store=store,
            session_factory=session_factory,
            settings=SETTINGS,
        )
