"""generate -> store -> (on approval) upload -> create ad -> link creative to ad.

Money guards, in order, for generation:
1. read-only / kill switch (the write gate),
2. ``higgsfield_monthly_cap_usd`` must be set, and this month's committed spend plus the
   whole batch's estimate must fit under it (all-or-nothing),
3. per-job ``Idempotency-Key`` so a retried submit can't double-charge.

Spend accounting: a job's estimate counts as committed from submission; failed / nsfw /
canceled jobs drop to $0 (Higgsfield refunds them).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import business_settings
from app.actions import ActionContext, SessionFactory, WritesBlockedError, write_action
from app.config import Settings, get_settings
from app.creatives import media
from app.creatives.briefs import CreativeBrief, make_variants
from app.db import session_scope
from app.integrations.ads.base import AdSpec, CampaignSpec, MediaUpload
from app.integrations.higgsfield import HiggsfieldClient
from app.integrations.http import IntegrationError
from app.log import get_logger, scrub
from app.models import (
    Ad,
    AdAccount,
    AdSet,
    Campaign,
    Creative,
    CreativeAdLink,
    CreativeStatus,
    CreativeTrait,
    CreativeType,
    EntityStatus,
    GenerationJob,
    GenerationStatus,
    Platform,
    Product,
)

log = get_logger(__name__)
ACTIVE = (GenerationStatus.QUEUED, GenerationStatus.RUNNING)
CHARGED = (GenerationStatus.QUEUED, GenerationStatus.RUNNING, GenerationStatus.SUCCEEDED)


class BudgetExceededError(WritesBlockedError):
    """The Higgsfield monthly cap would be exceeded (or isn't set)."""


def month_start(now: datetime) -> datetime:
    return now.astimezone(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def monthly_spend(session: Session, now: datetime | None = None) -> Decimal:
    """USD committed to Higgsfield this calendar month (UTC)."""
    now = now or datetime.now(UTC)
    total = session.scalar(
        select(func.coalesce(func.sum(GenerationJob.cost_usd), 0)).where(
            GenerationJob.created_at >= month_start(now), GenerationJob.status.in_(CHARGED)
        )
    )
    return Decimal(str(total or 0))


def check_budget(session: Session, extra_usd: Decimal, now: datetime | None = None) -> Decimal:
    """Raise BudgetExceededError unless ``extra_usd`` fits under the monthly cap. Returns headroom after."""
    cap = business_settings.load(session).higgsfield_monthly_cap_usd
    if cap is None:
        raise BudgetExceededError(
            "higgsfield_monthly_cap_usd is not set: generation is blocked until you set a cap"
        )
    spent = monthly_spend(session, now)
    if spent + extra_usd > cap:
        raise BudgetExceededError(
            f"Higgsfield monthly cap ${cap} would be exceeded: ${spent} spent + ${extra_usd} requested"
        )
    return cap - spent - extra_usd


def _webhook_url(s: Settings) -> str | None:
    token = s.higgsfield_webhook_token.get_secret_value()
    if not token or not s.public_base_url.startswith("https://"):
        return None
    return f"{s.public_base_url.rstrip('/')}/webhooks/higgsfield/{token}"


@dataclass
class GenerationResult:
    creative_ids: list[int] = field(default_factory=list)
    estimated_usd: Decimal = Decimal("0")
    errors: list[str] = field(default_factory=list)


def estimate_brief(
    client: HiggsfieldClient, brief: CreativeBrief, n: int, settings: Settings | None = None
) -> tuple[list[Any], Decimal]:
    """Variants + their total estimated USD (the estimate call also validates the params)."""
    s = settings or get_settings()
    model = brief.model or (
        s.higgsfield_video_model if brief.kind == "video" else s.higgsfield_image_model
    )
    if not model:
        raise ValueError(
            "no Higgsfield model: set HIGGSFIELD_VIDEO_MODEL (from the console) or pass brief.model"
        )
    variants = make_variants(brief, n, model)
    estimates = [client.estimate(v.extra_traits["model"], v.params).usd for v in variants]
    for v, usd in zip(variants, estimates, strict=True):
        v.extra_traits["estimated_usd"] = str(usd)
    return variants, sum(estimates, Decimal("0"))


def generate_creatives(
    brief: CreativeBrief,
    n: int,
    *,
    client: HiggsfieldClient | None = None,
    ctx: ActionContext | None = None,
    session_factory: SessionFactory = session_scope,
    settings: Settings | None = None,
) -> GenerationResult:
    """Create ``n`` variant creatives from a brief and queue them on Higgsfield."""
    s = settings or get_settings()
    client = client or HiggsfieldClient(s)
    if brief.product_id and not brief.product_name:
        with session_factory() as db:
            product = db.get(Product, brief.product_id)
            if product is None:
                raise ValueError(f"product {brief.product_id} not found")
            brief = brief.model_copy(update={"product_name": product.title})

    variants, total = estimate_brief(client, brief, n, s)
    with session_factory() as db:
        check_budget(db, total)

    result = GenerationResult(estimated_usd=total)
    payload = {
        "n": n,
        "kind": brief.kind,
        "model": variants[0].extra_traits["model"],
        "estimated_usd": str(total),
        "product_id": brief.product_id,
    }
    with write_action(
        "higgsfield.generate",
        target_type="creative_batch",
        target_id=None,
        payload=payload,
        ctx=ctx,
        session_factory=session_factory,
    ) as audit:
        for v in variants:
            usd = Decimal(v.extra_traits["estimated_usd"])
            with session_factory() as db:
                creative = Creative(
                    type=CreativeType(brief.kind),
                    status=CreativeStatus.GENERATING,
                    prompt=v.prompt,
                    brief=brief.model_dump(mode="json") | {"variant_index": v.index},
                    higgsfield_model=v.extra_traits["model"],
                    product_id=brief.product_id,
                    parent_creative_id=brief.parent_creative_id,
                    duration_seconds=Decimal(brief.duration_seconds)
                    if brief.kind == "video"
                    else None,
                )
                db.add(creative)
                db.flush()
                db.add(CreativeTrait(creative_id=creative.id, **v.traits, extra=v.extra_traits))
                job = GenerationJob(
                    creative_id=creative.id,
                    model=v.extra_traits["model"],
                    kind=CreativeType(brief.kind),
                    status=GenerationStatus.QUEUED,
                    request=v.params,
                    cost_usd=usd,
                )
                db.add(job)
                db.flush()
                creative_id, job_id = creative.id, job.id
            try:
                sub = client.submit(
                    v.extra_traits["model"],
                    v.params,
                    idempotency_key=f"hub-job-{job_id}",
                    webhook_url=_webhook_url(s),
                )
                with session_factory() as db:
                    job = db.get(GenerationJob, job_id)
                    job.higgsfield_job_id, job.submitted_at = sub.request_id, datetime.now(UTC)
                    job.status = (
                        GenerationStatus.RUNNING
                        if sub.status == "in_progress"
                        else GenerationStatus.QUEUED
                    )
                result.creative_ids.append(creative_id)
            except IntegrationError as exc:
                _fail(session_factory, job_id, f"submit failed: {exc}")
                result.errors.append(f"variant {v.index}: {scrub(str(exc))[:300]}")
        audit.data = {"creative_ids": result.creative_ids, "errors": result.errors}
    return result


def _fail(
    session_factory: SessionFactory,
    job_id: int,
    error: str,
    status: GenerationStatus = GenerationStatus.FAILED,
) -> None:
    with session_factory() as db:
        job = db.get(GenerationJob, job_id)
        job.status, job.error, job.cost_usd = status, scrub(error)[:2000], Decimal("0")  # refunded
        job.completed_at = datetime.now(UTC)
        if job.creative_id:
            db.get(Creative, job.creative_id).status = CreativeStatus.FAILED


def poll_job(
    job_id: int,
    *,
    client: HiggsfieldClient | None = None,
    store: Any | None = None,
    session_factory: SessionFactory = session_scope,
    settings: Settings | None = None,
    now: datetime | None = None,
) -> str:
    """Advance one job: store the output when done, refund on failure, time out stragglers."""
    s = settings or get_settings()
    now = now or datetime.now(UTC)
    with session_factory() as db:
        job = db.get(GenerationJob, job_id)
        if job is None or job.status not in ACTIVE or not job.higgsfield_job_id:
            return "skip"
        request_id, creative_id = job.higgsfield_job_id, job.creative_id
        started = job.submitted_at or job.created_at
    client = client or HiggsfieldClient(s)
    st = client.status(request_id)

    if not st.done:
        started = started if started.tzinfo else started.replace(tzinfo=UTC)
        if now - started > timedelta(minutes=s.higgsfield_job_timeout_minutes):
            try:
                client.cancel(request_id)
            except IntegrationError:
                pass
            _fail(
                session_factory, job_id, f"timed out after {s.higgsfield_job_timeout_minutes} min"
            )
            return "timeout"
        if st.status == "in_progress":
            with session_factory() as db:
                db.get(GenerationJob, job_id).status = GenerationStatus.RUNNING
        return st.status

    if st.status != "completed" or not st.output_url:
        status = GenerationStatus.CANCELLED if st.status == "canceled" else GenerationStatus.FAILED
        _fail(session_factory, job_id, st.error or f"higgsfield status {st.status}", status)
        return st.status

    content, mime = client.download(st.output_url)
    if store is None:
        from app.storage import get_store

        store = get_store()
    key = f"creatives/{creative_id}/{job_id}{media.ext_for(mime)}"
    url = store.put(key, content, mime)
    info = media.probe(content, mime) or {}
    with session_factory() as db:
        job = db.get(GenerationJob, job_id)
        job.status, job.completed_at = GenerationStatus.SUCCEEDED, now
        job.result = {
            "output_url_expires": "~7 days",
            "storage_key": key,
            "bytes": len(content),
            "mime": mime,
        }
        creative = db.get(Creative, creative_id)
        creative.status, creative.storage_key, creative.storage_url, creative.mime_type = (
            CreativeStatus.READY,
            key,
            url,
            mime,
        )
        creative.width, creative.height = info.get("width"), info.get("height")
        if info.get("duration"):
            creative.duration_seconds = Decimal(str(round(info["duration"], 2)))
        creative.cost_usd = job.cost_usd
    log.info("creative_ready", creative=creative_id, key=key, bytes=len(content))
    return "completed"


def active_job_ids(session: Session) -> list[int]:
    return list(session.scalars(select(GenerationJob.id).where(GenerationJob.status.in_(ACTIVE))))


# --- launch ---------------------------------------------------------------------------------


@dataclass
class LaunchRequest:
    creative_id: int
    platforms: list[str]
    landing_url: str
    primary_text: str
    headline: str | None = None
    daily_budget: Decimal | None = None  # required when a new campaign is created
    countries: list[str] = field(default_factory=lambda: ["US"])
    ad_set_ids: dict[str, str] = field(
        default_factory=dict
    )  # platform -> existing ad set / ad group id


def _ensure_ad_row(
    db: Session,
    platform: Platform,
    account_ext: str,
    campaign_ext: str,
    ad_set_ext: str,
    ad_ext: str,
    name: str,
) -> Ad:
    """Local rows for a just-created ad so it can be linked now (the next sync fills details)."""

    def get(model: Any, ext: str) -> Any:
        return db.scalar(select(model).where(model.platform == platform, model.external_id == ext))

    account = get(AdAccount, account_ext) or AdAccount(platform=platform, external_id=account_ext)
    db.add(account)
    db.flush()
    campaign = get(Campaign, campaign_ext) or Campaign(
        platform=platform,
        external_id=campaign_ext,
        ad_account_id=account.id,
        name=name,
        status=EntityStatus.PAUSED,
    )
    db.add(campaign)
    db.flush()
    ad_set = get(AdSet, ad_set_ext) or AdSet(
        platform=platform,
        external_id=ad_set_ext,
        campaign_id=campaign.id,
        name=name,
        status=EntityStatus.PAUSED,
    )
    db.add(ad_set)
    db.flush()
    ad = get(Ad, ad_ext) or Ad(
        platform=platform,
        external_id=ad_ext,
        ad_set_id=ad_set.id,
        name=name,
        status=EntityStatus.PAUSED,
    )
    db.add(ad)
    db.flush()
    return ad


def launch_creative(
    req: LaunchRequest,
    *,
    platform_factory: Any | None = None,
    store: Any | None = None,
    ctx: ActionContext | None = None,
    session_factory: SessionFactory = session_scope,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Upload a ready creative and create a **paused** ad on each platform, then link them.

    Called on approval (Phase 5). Every platform call is itself gated + audited.
    """
    s = settings or get_settings()
    if platform_factory is None:
        from app.integrations.ads.registry import get_platform as platform_factory
    if store is None:
        from app.storage import get_store

        store = get_store()
    with session_factory() as db:
        c = db.get(Creative, req.creative_id)
        if c is None or c.status not in (
            CreativeStatus.READY,
            CreativeStatus.APPROVED,
            CreativeStatus.LAUNCHED,
        ):
            raise ValueError(f"creative {req.creative_id} is not ready to launch")
        kind, key, mime = c.type, c.storage_key, c.mime_type or "video/mp4"
        name = f"Hub creative {c.id}" + (
            f" - {c.brief.get('product_name')}" if c.brief and c.brief.get("product_name") else ""
        )

    content = store.get_bytes(key)
    thumb = media.thumbnail(content, mime) if kind == CreativeType.VIDEO else None
    results: dict[str, Any] = {}
    with write_action(
        "creative.launch",
        target_type="creative",
        target_id=str(req.creative_id),
        payload={
            "platforms": req.platforms,
            "daily_budget": str(req.daily_budget or ""),
            "landing_url": req.landing_url,
        },
        ctx=ctx,
        session_factory=session_factory,
    ) as audit:
        for p in req.platforms:
            try:
                client = platform_factory(p)
                upload = MediaUpload(
                    filename=key.rsplit("/", 1)[-1], content=content, mime_type=mime, title=name
                )
                video_id = image_id = None
                if kind == CreativeType.VIDEO:
                    video_id = client.upload_video(upload, ctx=ctx)
                    if p == "google":
                        image_id = s.google_ads_logo_asset or None
                        if not image_id:
                            raise ValueError(
                                "GOOGLE_ADS_LOGO_ASSET is required for Google video ads"
                            )
                    else:
                        if not thumb:
                            raise ValueError("could not make a thumbnail (ffmpeg) for the video")
                        image_id = client.upload_image(
                            MediaUpload("thumb.jpg", thumb, "image/jpeg", name), ctx=ctx
                        )
                else:
                    image_id = client.upload_image(upload, ctx=ctx)

                ad_set_id = req.ad_set_ids.get(p)
                campaign_id = None
                if not ad_set_id:
                    if req.daily_budget is None:
                        raise ValueError("daily_budget is required to create a new campaign")
                    created = client.create_campaign(
                        CampaignSpec(
                            name=name, daily_budget=req.daily_budget, countries=req.countries
                        ),
                        ctx=ctx,
                    )
                    ad_set_id, campaign_id = created.ad_set_id, created.campaign_id
                ad_id = client.create_ad(
                    AdSpec(
                        ad_set_id=ad_set_id,
                        name=name,
                        landing_url=req.landing_url,
                        primary_text=req.primary_text,
                        headline=req.headline,
                        video_asset_id=video_id,
                        image_asset_id=image_id,
                    ),
                    ctx=ctx,
                )
                with session_factory() as db:
                    existing_set = db.scalar(
                        select(AdSet).where(
                            AdSet.platform == Platform(p), AdSet.external_id == ad_set_id
                        )
                    )
                    if campaign_id is None and existing_set is not None:
                        campaign_id = db.get(Campaign, existing_set.campaign_id).external_id
                    account_ext = getattr(client, "account_external_id", None) or f"{p}-account"
                    ad = _ensure_ad_row(
                        db,
                        Platform(p),
                        account_ext,
                        campaign_id or f"{p}-campaign-{ad_set_id}",
                        ad_set_id,
                        ad_id,
                        name,
                    )
                    if not db.scalar(
                        select(CreativeAdLink).where(
                            CreativeAdLink.creative_id == req.creative_id,
                            CreativeAdLink.ad_id == ad.id,
                        )
                    ):
                        db.add(
                            CreativeAdLink(
                                creative_id=req.creative_id,
                                ad_id=ad.id,
                                platform=Platform(p),
                                external_ad_id=ad_id,
                                platform_asset_id=video_id or image_id,
                            )
                        )
                results[p] = {
                    "ad_id": ad_id,
                    "ad_set_id": ad_set_id,
                    "campaign_id": campaign_id,
                    "status": "paused",
                }
            except (IntegrationError, ValueError, WritesBlockedError) as exc:
                results[p] = {"error": scrub(str(exc))[:300]}
        if any("ad_id" in r for r in results.values()):
            with session_factory() as db:
                db.get(Creative, req.creative_id).status = CreativeStatus.LAUNCHED
        audit.data = results
    return results
