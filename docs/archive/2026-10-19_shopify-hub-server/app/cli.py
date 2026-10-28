"""Operator CLI, run inside the api container::

docker compose exec api python -m app.cli settings show
docker compose exec api python -m app.cli settings set daily_spend_cap 150
docker compose exec api python -m app.cli settings set read_only false
docker compose exec api python -m app.cli storage init
docker compose exec api python -m app.cli health
docker compose exec api python -m app.cli jobs record backup success --stats '{"mb": 12}'
docker compose exec api python -m app.cli shopify status
docker compose exec api python -m app.cli shopify backfill all --days 730
docker compose exec api python -m app.cli shopify register-webhooks
docker compose exec api python -m app.cli shopify reattribute
docker compose exec api python -m app.cli ads status
docker compose exec api python -m app.cli ads sync meta --days 30
docker compose exec api python -m app.cli conversions status
docker compose exec api python -m app.cli conversions create-pixels meta tiktok google
docker compose exec api python -m app.cli conversions check --days 7
docker compose exec api python -m app.cli conversions test-event meta
docker compose exec api python -m app.cli higgsfield models
docker compose exec -T api python -m app.cli higgsfield estimate --n 3 < brief.json
docker compose exec -T api python -m app.cli creatives generate --n 3 < brief.json
docker compose exec api python -m app.cli creatives list
docker compose exec api python -m app.cli creatives launch 12 --platforms meta tiktok --budget 20     --url https://shop.com/products/x --text "Glow in 7 days"
docker compose exec -T api python -m app.cli ads upload-logo logo.png < logo.png
docker compose exec api python -m app.cli approvals list
docker compose exec api python -m app.cli approvals approve 7
docker compose exec api python -m app.cli mcp clients
docker compose exec api python -m app.cli kill-switch on
docker compose exec api python -m app.cli report daily --send
docker compose exec api python -m app.cli guardrails
docker compose exec api python -m app.cli analytics metrics
docker compose exec api python -m app.cli analytics bandit --dry-run
docker compose exec api python -m app.cli analytics model train
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from typing import Any

from app import business_settings
from app.db import session_scope


def _parse_value(raw: str) -> Any:
    """Accept JSON (true, 150, null, [..]) and fall back to the raw string."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def cmd_settings_show(_: argparse.Namespace) -> int:
    with session_scope() as s:
        current = business_settings.load(s)
    print(
        json.dumps(
            {**current.model_dump(mode="json"), "writes_allowed": current.writes_allowed}, indent=2
        )
    )
    return 0


def cmd_settings_set(args: argparse.Namespace) -> int:
    try:
        with session_scope() as s:
            updated = business_settings.set_value(
                s, args.key, _parse_value(args.value), actor="cli", requested_by=getpass.getuser()
            )
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"{args.key} = {json.dumps(updated.model_dump(mode='json')[args.key])}")
    return 0


def cmd_storage_init(_: argparse.Namespace) -> int:
    from app.storage import get_store

    store = get_store()
    created = store.ensure_bucket()
    print(f"bucket {store.bucket!r} {'created' if created else 'already exists'}")
    return 0


def cmd_health(_: argparse.Namespace) -> int:
    from app.health import full_status
    from app.queue import get_redis

    results = full_status(get_redis())
    for r in results:
        print(f"{'OK  ' if r.ok else 'FAIL'} {r.name:<10} {r.detail}")
    return 0 if all(r.ok for r in results) else 1


def cmd_jobs_record(args: argparse.Namespace) -> int:
    """Record the outcome of a job that runs outside the app (e.g. the backup timer)."""
    from datetime import UTC, datetime

    from app.log import scrub
    from app.models import JobRun, JobRunStatus

    with session_scope() as s:
        s.add(
            JobRun(
                job_name=args.name,
                status=JobRunStatus(args.status),
                finished_at=datetime.now(UTC),
                error=scrub(args.error)[:4000] if args.error else None,
                stats=json.loads(args.stats) if args.stats else None,
            )
        )
    return 0


SHOPIFY_WEBHOOK_TOPICS = (
    "ORDERS_CREATE",
    "ORDERS_UPDATED",
    "ORDERS_CANCELLED",
    "REFUNDS_CREATE",
    "PRODUCTS_CREATE",
    "PRODUCTS_UPDATE",
    "PRODUCTS_DELETE",
)


def cmd_shopify_status(_: argparse.Namespace) -> int:
    from app.config import get_settings
    from app.integrations.shopify import queries
    from app.jobs.shopify import get_client

    s = get_settings()
    if s.shopify_admin_access_token.get_secret_value():
        auth = "legacy static token"
    elif s.shopify_client_id:
        auth = "client credentials"
    else:
        auth = "(not set)"
    print(f"store domain : {s.shopify_store_domain or '(not set)'}")
    print(f"api version  : {s.shopify_api_version}")
    print(f"auth         : {auth}")
    if not s.shopify_configured:
        print("status       : NOT CONFIGURED -- see README 'Shopify setup'")
        return 1
    shop = get_client().execute(queries.SHOP)["shop"]
    print(f"connected    : {shop['name']} ({shop['myshopifyDomain']}, {shop['currencyCode']})")
    if shop.get("ianaTimezone") and shop["ianaTimezone"] != s.store_timezone:
        print(f"WARNING      : STORE_TIMEZONE={s.store_timezone}, shop uses {shop['ianaTimezone']}")
    if shop.get("currencyCode") and shop["currencyCode"] != s.store_currency:
        print(f"WARNING      : STORE_CURRENCY={s.store_currency}, shop uses {shop['currencyCode']}")
    return 0


def cmd_shopify_backfill(args: argparse.Namespace) -> int:
    from app.jobs.shopify import backfill

    print(json.dumps(backfill(args.kind, days=args.days)))
    return 0


def cmd_shopify_register_webhooks(_: argparse.Namespace) -> int:
    from app.config import get_settings
    from app.integrations.shopify import queries
    from app.jobs.shopify import get_client

    s = get_settings()
    uri = s.public_base_url.rstrip("/") + "/webhooks/shopify"
    if not uri.startswith("https://"):
        print(f"error: PUBLIC_BASE_URL must be the public https URL, got {uri}", file=sys.stderr)
        return 2
    client = get_client()
    subs = client.execute(queries.WEBHOOKS)["webhookSubscriptions"]["nodes"]
    existing = {(w["topic"], w["uri"]) for w in subs}
    for topic in SHOPIFY_WEBHOOK_TOPICS:
        if (topic, uri) in existing:
            print(f"exists   {topic}")
            continue
        result = client.execute(queries.WEBHOOK_CREATE, {"topic": topic, "uri": uri})
        client.check_user_errors(result["webhookSubscriptionCreate"], f"register {topic}")
        print(f"created  {topic} -> {uri}")
    return 0


def cmd_shopify_reattribute(args: argparse.Namespace) -> int:
    from app.attribution import reattribute

    with session_scope() as s:
        n = reattribute(s, only_unmatched=not args.all)
    print(f"re-attributed {n} orders")
    return 0


def cmd_ads_status(_: argparse.Namespace) -> int:
    from app.config import get_settings
    from app.integrations.ads.registry import get_platform, is_configured
    from app.models import Platform

    s, ok = get_settings(), True
    versions = {
        "google": s.google_ads_api_version,
        "meta": s.meta_api_version,
        "tiktok": s.tiktok_api_version,
    }
    for p in Platform:
        if not is_configured(p):
            print(f"{p.value:<7} not configured (api {versions[p.value]})")
            continue
        try:
            acct = get_platform(p).get_account()
        except Exception as exc:  # report every platform, don't stop at the first failure
            ok = False
            print(f"{p.value:<7} ERROR {exc}")
            continue
        warn = ""
        if acct.timezone and acct.timezone != s.store_timezone:
            warn = (
                f"  WARNING: account timezone {acct.timezone} != STORE_TIMEZONE {s.store_timezone}"
            )
        if acct.currency and acct.currency != s.store_currency:
            warn += f"  WARNING: account currency {acct.currency} != STORE_CURRENCY"
        print(
            f"{p.value:<7} OK {acct.name} ({acct.external_id}, {acct.currency}, {acct.timezone}){warn}"
        )
    return 0 if ok else 1


def cmd_ads_sync(args: argparse.Namespace) -> int:
    from app.jobs.ads import sync_one

    print(
        json.dumps(
            sync_one(args.platform, lookback_days=args.days, job_name=f"ads_{args.platform}_manual")
        )
    )
    return 0


def cmd_ads_tiktok_token(args: argparse.Namespace) -> int:
    """Exchange a TikTok advertiser authorization code for a long-lived access token."""
    import httpx

    from app.config import get_settings

    s = get_settings()
    if not (s.tiktok_app_id and s.tiktok_app_secret.get_secret_value()):
        print("error: set TIKTOK_APP_ID and TIKTOK_APP_SECRET in .env first", file=sys.stderr)
        return 2
    resp = httpx.post(
        f"https://business-api.tiktok.com/open_api/{s.tiktok_api_version}/oauth2/access_token/",
        json={
            "app_id": s.tiktok_app_id,
            "secret": s.tiktok_app_secret.get_secret_value(),
            "auth_code": args.auth_code,
        },
        timeout=30,
    )
    body = resp.json()
    if body.get("code") != 0:
        print(f"error: TikTok said code={body.get('code')}: {body.get('message')}", file=sys.stderr)
        return 1
    data = body.get("data") or {}
    print("Add these to .env, then run scripts/deploy.sh:")
    print(f"TIKTOK_ACCESS_TOKEN={data.get('access_token')}")
    ids = data.get("advertiser_ids") or []
    print(
        f"TIKTOK_ADVERTISER_ID={ids[0] if ids else '<pick one>'}"
        + (f"   # all: {ids}" if len(ids) > 1 else "")
    )
    return 0


def cmd_conversions_status(_: argparse.Namespace) -> int:
    from app.config import get_settings
    from app.conversions.senders import GoogleClickConversions, MetaCapi, TikTokEvents

    s = get_settings()
    with session_scope() as db:
        bs = business_settings.load(db)
    print(f"enabled       : {bs.conversions_enabled}  (kill switch: {bs.kill_switch})")
    print(f"hashed PII    : {bs.conversions_hashed_pii}")
    print(f"excluded      : {bs.conversions_exclude_countries or '-'}")
    rows = [
        ("meta", MetaCapi.configured(s), f"pixel {s.meta_pixel_id or '(META_PIXEL_ID not set)'}"),
        (
            "tiktok",
            TikTokEvents.configured(s),
            f"pixel code {s.tiktok_pixel_code or '(TIKTOK_PIXEL_CODE not set)'}",
        ),
        (
            "google",
            GoogleClickConversions.configured(s),
            s.google_ads_conversion_action or "(GOOGLE_ADS_CONVERSION_ACTION not set)",
        ),
    ]
    for name, ok, detail in rows:
        print(f"{name:<14}: {'ready' if ok else 'not configured'}  {detail}")
    return 0


def cmd_conversions_create_pixels(args: argparse.Namespace) -> int:
    from app.actions import ActionContext
    from app.conversions.service import create_pixels

    lines = create_pixels(
        args.platforms, args.name, ctx=ActionContext(actor="cli", requested_by=getpass.getuser())
    )
    print("Add to .env, then run scripts/deploy.sh:")
    for k, v in lines.items():
        print(f"{k}={v}")
    return 0


def cmd_conversions_activate_pixel(_: argparse.Namespace) -> int:
    from app.conversions.service import activate_web_pixel
    from app.jobs.shopify import get_client

    pixel = activate_web_pixel(get_client())
    print(f"web pixel connected: {pixel.get('id')} settings={pixel.get('settings')}")
    return 0


def cmd_conversions_check(args: argparse.Namespace) -> int:
    from app.conversions.service import report

    with session_scope() as s:
        r = report(s, days=args.days)
    print(json.dumps(r, indent=2, default=str))
    return 1 if r["problems"] else 0


def cmd_conversions_test_event(args: argparse.Namespace) -> int:
    """Send one PageView to a platform (use META_CAPI_TEST_EVENT_CODE / TIKTOK_TEST_EVENT_CODE
    to see it in the platform's test console without affecting reporting)."""
    import uuid
    from datetime import UTC, datetime

    from app.config import get_settings
    from app.conversions.events import Event
    from app.conversions.senders import MetaCapi, TikTokEvents

    s = get_settings()
    sender = {"meta": MetaCapi, "tiktok": TikTokEvents}[args.platform](s)
    name = "PageView" if args.platform == "meta" else "ViewContent"
    event = Event(
        name=name,
        event_id=f"hub-test-{uuid.uuid4()}",
        time=datetime.now(UTC),
        url=s.public_base_url,
        user_agent="shopify-hub/test",
        ip="127.0.0.1",
    )
    print(f"{args.platform}: accepted {sender.send([event])} event(s)")
    return 0


def _read_brief(path: str) -> object:
    from app.creatives.briefs import CreativeBrief

    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    return CreativeBrief.model_validate_json(raw)


def cmd_higgsfield_models(_: argparse.Namespace) -> int:
    from app.integrations.higgsfield import HiggsfieldClient

    for m in HiggsfieldClient().models():
        print(json.dumps(m))
    return 0


def cmd_higgsfield_estimate(args: argparse.Namespace) -> int:
    from app.creatives.pipeline import estimate_brief, monthly_spend
    from app.integrations.higgsfield import HiggsfieldClient

    variants, total = estimate_brief(HiggsfieldClient(), _read_brief(args.brief), args.n)  # type: ignore[arg-type]
    with session_scope() as s:
        cap = business_settings.load(s).higgsfield_monthly_cap_usd
        spent = monthly_spend(s)
    for v in variants:
        print(
            f"variant {v.index}: ${v.extra_traits['estimated_usd']}  {v.traits['hook_type']} / {v.traits['angle']} / {v.traits['avatar_type']}"
        )
    print(
        f"total ${total}; this month ${spent} spent; cap {('$' + str(cap)) if cap is not None else 'NOT SET (blocked)'}"
    )
    return 0


def cmd_creatives_generate(args: argparse.Namespace) -> int:
    from app.actions import ActionContext
    from app.creatives.pipeline import generate_creatives

    res = generate_creatives(
        _read_brief(args.brief),
        args.n,  # type: ignore[arg-type]
        ctx=ActionContext(actor="cli", requested_by=getpass.getuser()),
    )
    print(
        json.dumps(
            {
                "creative_ids": res.creative_ids,
                "estimated_usd": str(res.estimated_usd),
                "errors": res.errors,
            }
        )
    )
    return 0 if not res.errors else 1


def cmd_creatives_list(args: argparse.Namespace) -> int:
    from sqlalchemy import select

    from app.models import Creative

    with session_scope() as s:
        q = select(Creative).order_by(Creative.id.desc()).limit(args.limit)
        if args.status:
            q = q.where(Creative.status == args.status)
        for c in s.scalars(q):
            print(
                f"{c.id:>5} {c.type.value:<5} {c.status.value:<10} ${c.cost_usd:<7} {c.higgsfield_model or '-'}  {c.storage_key or ''}"
            )
    return 0


def cmd_creatives_launch(args: argparse.Namespace) -> int:
    from decimal import Decimal

    from app.actions import ActionContext
    from app.creatives.pipeline import LaunchRequest, launch_creative

    req = LaunchRequest(
        creative_id=args.creative_id,
        platforms=args.platforms,
        landing_url=args.url,
        primary_text=args.text,
        headline=args.headline,
        daily_budget=Decimal(args.budget) if args.budget else None,
        countries=args.countries,
        ad_set_ids=dict(kv.split("=", 1) for kv in args.ad_set or []),
    )
    out = launch_creative(req, ctx=ActionContext(actor="cli", requested_by=getpass.getuser()))
    print(json.dumps(out, indent=2))
    return 0 if all("ad_id" in r for r in out.values()) else 1


def cmd_ads_upload_logo(args: argparse.Namespace) -> int:
    from app.actions import ActionContext
    from app.integrations.ads.base import MediaUpload
    from app.integrations.ads.registry import get_platform

    content = sys.stdin.buffer.read()
    mime = "image/png" if args.filename.lower().endswith(".png") else "image/jpeg"
    asset = get_platform("google").upload_image(
        MediaUpload(args.filename, content, mime, title="Logo"),
        ctx=ActionContext(actor="cli", requested_by=getpass.getuser()),
    )
    print(f"GOOGLE_ADS_LOGO_ASSET={asset}")
    return 0


def cmd_approvals_list(_: argparse.Namespace) -> int:
    from app import approvals
    from app.analytics import reports

    with session_scope() as s:
        approvals.expire_old(s)
    with session_scope() as s:
        for a in reports.pending_approvals(s)["approvals"]:
            print(
                f"#{a['id']:<5} {a['action']:<18} {a['summary']}  (by {a['requested_by']}, {a['age_hours']}h ago)"
            )
    return 0


def cmd_approvals_decide(args: argparse.Namespace) -> int:
    from app import approvals

    who = f"cli:{getpass.getuser()}"
    if args.decision == "approve":
        out = approvals.approve(args.id, decided_by=who, via_mcp=False)
    else:
        out = approvals.reject(args.id, decided_by=who, reason=args.reason)
    print(json.dumps(out, indent=2, default=str))
    return 0 if out.get("status") in ("executed", "rejected") else 1


def cmd_mcp_clients(args: argparse.Namespace) -> int:
    from sqlalchemy import select

    from app.models import OAuthClient

    with session_scope() as s:
        if args.revoke:
            c = s.get(OAuthClient, args.revoke)
            if c is None:
                print("no such client", file=sys.stderr)
                return 1
            c.revoked = True
            print(f"revoked {c.client_name}: its tokens stop working immediately")
            return 0
        for c in s.scalars(select(OAuthClient).order_by(OAuthClient.created_at)):
            print(
                f"{'REVOKED ' if c.revoked else ''}{c.client_name}  id={c.client_id}  since {c.created_at:%Y-%m-%d}"
            )
    return 0


def cmd_kill_switch(args: argparse.Namespace) -> int:
    with session_scope() as s:
        business_settings.set_value(
            s, "kill_switch", args.state == "on", actor="cli", requested_by=getpass.getuser()
        )
    print(f"kill switch {args.state.upper()}")
    return 0


def cmd_report_daily(args: argparse.Namespace) -> int:
    from datetime import date

    from app import daily_report
    from app.alerts import send_slack
    from app.queue import get_redis

    with session_scope() as s:
        r = daily_report.build(
            s, day=date.fromisoformat(args.date) if args.date else None, redis=get_redis()
        )
    text = daily_report.format_slack(r)
    print(text)
    if args.send:
        print("sent to Slack" if send_slack(text) else "Slack not configured / failed")
    return 0


def cmd_guardrails(_: argparse.Namespace) -> int:
    from app import guardrails

    with session_scope() as s:
        bs = business_settings.load(s)
        committed = guardrails.committed_daily_budget(s)
        print(
            f"kill switch          : {'ON' if bs.kill_switch else 'off'};  read-only: {bs.read_only}"
        )
        print(
            f"daily spend cap      : {bs.daily_spend_cap if bs.daily_spend_cap is not None else 'NOT SET (spend increases blocked)'}"
        )
        print(
            f"committed budgets/day: {committed:.2f};  spent today: {guardrails.spend_today(s):.2f}"
        )
        print(
            f"max budget change    : {bs.max_budget_change_pct}%/day (cumulative per campaign / ad set)"
        )
        print(
            f"new ads today        : {guardrails.ads_created_today(s)} of {bs.max_new_ads_per_day}"
        )
        print(
            f"higgsfield cap       : {bs.higgsfield_monthly_cap_usd if bs.higgsfield_monthly_cap_usd is not None else 'NOT SET'}"
        )
    return 0


def cmd_analytics_metrics(args: argparse.Namespace) -> int:
    from datetime import UTC, date, datetime, timedelta

    from app.config import get_settings
    from app.ml import creative_metrics

    if args.date:
        as_of = date.fromisoformat(args.date)
    else:
        as_of = datetime.now(UTC).astimezone(get_settings().tz).date() - timedelta(days=1)
    with session_scope() as s:
        print(
            json.dumps({"as_of": as_of.isoformat(), **creative_metrics.compute(s, as_of)}, indent=2)
        )
    return 0


def cmd_analytics_bandit(args: argparse.Namespace) -> int:
    from app.ml import bandit

    out = bandit.run(window_days=args.window, propose=not args.dry_run)
    print(
        json.dumps(
            {k: out[k] for k in ("run_id", "status", "notes", "proposals")}, indent=2, default=str
        )
    )
    for a in out["arms"]:
        print(
            f"{a['platform']:<7} {a['method']:<22} ROI after spend {a['post_mean']:+.1%} +/-{a['post_sd']:.1%}  "
            f"P(best) {a['p_best']:.0%}  {a['current_budget']:.2f} -> {a['new_budget']:.2f}/day"
        )
    return 0


def cmd_analytics_model(args: argparse.Namespace) -> int:
    from app.ml import model

    if args.action == "train":
        print(json.dumps(model.train(), indent=2, default=str))
    else:
        with session_scope() as s:
            print(json.dumps(model.status(s), indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(required=True)

    settings = sub.add_parser("settings").add_subparsers(required=True)
    settings.add_parser("show").set_defaults(fn=cmd_settings_show)
    p_set = settings.add_parser("set")
    p_set.add_argument("key")
    p_set.add_argument("value", help="JSON value, e.g. true, 150, null")
    p_set.set_defaults(fn=cmd_settings_set)

    storage = sub.add_parser("storage").add_subparsers(required=True)
    storage.add_parser("init").set_defaults(fn=cmd_storage_init)

    sub.add_parser("health").set_defaults(fn=cmd_health)

    jobs = sub.add_parser("jobs").add_subparsers(required=True)
    p_rec = jobs.add_parser("record")
    p_rec.add_argument("name")
    p_rec.add_argument("status", choices=["success", "failed"])
    p_rec.add_argument("--error")
    p_rec.add_argument("--stats", help="JSON object")
    p_rec.set_defaults(fn=cmd_jobs_record)

    shopify = sub.add_parser("shopify").add_subparsers(required=True)
    shopify.add_parser("status").set_defaults(fn=cmd_shopify_status)
    p_bf = shopify.add_parser("backfill")
    p_bf.add_argument("kind", choices=["products", "customers", "orders", "all"])
    p_bf.add_argument("--days", type=int, default=None, help="orders: how far back")
    p_bf.set_defaults(fn=cmd_shopify_backfill)
    shopify.add_parser("register-webhooks").set_defaults(fn=cmd_shopify_register_webhooks)
    p_ra = shopify.add_parser("reattribute")
    p_ra.add_argument("--all", action="store_true", help="also re-check matched orders")
    p_ra.set_defaults(fn=cmd_shopify_reattribute)

    ads = sub.add_parser("ads").add_subparsers(required=True)
    ads.add_parser("status").set_defaults(fn=cmd_ads_status)
    p_as = ads.add_parser("sync")
    p_as.add_argument("platform", choices=["google", "meta", "tiktok"])
    p_as.add_argument("--days", type=int, default=None, help="metrics lookback (default 3)")
    p_as.set_defaults(fn=cmd_ads_sync)
    p_tt = ads.add_parser(
        "tiktok-token", help="exchange an advertiser auth_code for an access token"
    )
    p_tt.add_argument("auth_code")
    p_tt.set_defaults(fn=cmd_ads_tiktok_token)

    conv = sub.add_parser("conversions").add_subparsers(required=True)
    conv.add_parser("status").set_defaults(fn=cmd_conversions_status)
    p_cp = conv.add_parser("create-pixels")
    p_cp.add_argument("platforms", nargs="+", choices=["meta", "tiktok", "google"])
    p_cp.add_argument("--name", default="Shopify hub")
    p_cp.set_defaults(fn=cmd_conversions_create_pixels)
    conv.add_parser("activate-pixel").set_defaults(fn=cmd_conversions_activate_pixel)
    p_ck = conv.add_parser("check")
    p_ck.add_argument("--days", type=int, default=7)
    p_ck.set_defaults(fn=cmd_conversions_check)
    p_te = conv.add_parser("test-event")
    p_te.add_argument("platform", choices=["meta", "tiktok"])
    p_te.set_defaults(fn=cmd_conversions_test_event)

    hf = sub.add_parser("higgsfield").add_subparsers(required=True)
    hf.add_parser("models").set_defaults(fn=cmd_higgsfield_models)
    p_he = hf.add_parser("estimate")
    p_he.add_argument("--brief", default="-", help="brief JSON file, or - for stdin")
    p_he.add_argument("--n", type=int, default=1)
    p_he.set_defaults(fn=cmd_higgsfield_estimate)

    cr = sub.add_parser("creatives").add_subparsers(required=True)
    p_cg = cr.add_parser("generate")
    p_cg.add_argument("--brief", default="-", help="brief JSON file, or - for stdin")
    p_cg.add_argument("--n", type=int, default=1)
    p_cg.set_defaults(fn=cmd_creatives_generate)
    p_cl = cr.add_parser("list")
    p_cl.add_argument("--status", default=None)
    p_cl.add_argument("--limit", type=int, default=30)
    p_cl.set_defaults(fn=cmd_creatives_list)
    p_lc = cr.add_parser("launch")
    p_lc.add_argument("creative_id", type=int)
    p_lc.add_argument("--platforms", nargs="+", choices=["meta", "tiktok", "google"], required=True)
    p_lc.add_argument("--url", required=True)
    p_lc.add_argument("--text", required=True)
    p_lc.add_argument("--headline", default=None)
    p_lc.add_argument("--budget", default=None, help="daily budget for a NEW campaign")
    p_lc.add_argument("--countries", nargs="+", default=["US"])
    p_lc.add_argument("--ad-set", action="append", help="use an existing ad set: platform=ID")
    p_lc.set_defaults(fn=cmd_creatives_launch)

    p_ul = ads.add_parser("upload-logo", help="square logo for Google Demand Gen ads (stdin)")
    p_ul.add_argument("filename")
    p_ul.set_defaults(fn=cmd_ads_upload_logo)

    ap = sub.add_parser("approvals").add_subparsers(required=True)
    ap.add_parser("list").set_defaults(fn=cmd_approvals_list)
    for decision in ("approve", "reject"):
        p_d = ap.add_parser(decision)
        p_d.add_argument("id", type=int)
        p_d.add_argument("--reason", default=None)
        p_d.set_defaults(fn=cmd_approvals_decide, decision=decision)

    p_ks = sub.add_parser("kill-switch", help="block (on) or allow (off) every hub write")
    p_ks.add_argument("state", choices=["on", "off"])
    p_ks.set_defaults(fn=cmd_kill_switch)

    rp = sub.add_parser("report").add_subparsers(required=True)
    p_rd = rp.add_parser("daily")
    p_rd.add_argument("--date", default=None, help="YYYY-MM-DD (default: yesterday)")
    p_rd.add_argument("--send", action="store_true")
    p_rd.set_defaults(fn=cmd_report_daily)

    sub.add_parser("guardrails", help="current limits and usage").set_defaults(fn=cmd_guardrails)

    an = sub.add_parser("analytics").add_subparsers(required=True)
    p_am = an.add_parser("metrics", help="compute creative metric snapshots")
    p_am.add_argument("--date", default=None)
    p_am.set_defaults(fn=cmd_analytics_metrics)
    p_ab = an.add_parser("bandit", help="run the budget bandit")
    p_ab.add_argument("--window", type=int, default=28)
    p_ab.add_argument("--dry-run", action="store_true", help="recommend without creating proposals")
    p_ab.set_defaults(fn=cmd_analytics_bandit)
    p_ml = an.add_parser("model", help="creative profit model")
    p_ml.add_argument("action", choices=["train", "status"])
    p_ml.set_defaults(fn=cmd_analytics_model)

    mc = sub.add_parser("mcp").add_subparsers(required=True)
    p_mc = mc.add_parser("clients", help="list connected Claude clients (or --revoke CLIENT_ID)")
    p_mc.add_argument("--revoke", default=None)
    p_mc.set_defaults(fn=cmd_mcp_clients)

    args = parser.parse_args(argv)
    from app.actions import WritesBlockedError
    from app.integrations.http import IntegrationError, NotConfiguredError

    try:
        return int(args.fn(args))
    except NotConfiguredError as exc:
        print(f"not configured: {exc}", file=sys.stderr)
        return 3
    except WritesBlockedError as exc:  # read-only, kill switch, budget cap
        print(f"blocked: {exc}", file=sys.stderr)
        return 4
    except IntegrationError as exc:
        print(f"platform error: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
