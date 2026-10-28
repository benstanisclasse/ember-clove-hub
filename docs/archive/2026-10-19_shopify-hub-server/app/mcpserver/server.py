"""The hub's MCP server (streamable HTTP, stateless, JSON responses) at ``/mcp``.

High-level tools only -- every number is pre-computed, with units and date ranges:

Read:  get_business_summary · get_profit_by_product · get_platform_performance · get_campaigns
       get_top_creatives · get_creative_trait_insights · get_pending_approvals · get_generation_spend
Write: propose_budget_change · propose_pause_ad · propose_activate · generate_creatives · launch_creative
       approve_action · reject_action

Write tools never change anything directly: they create a proposal (pending approval) unless
an auto-approve rule matches; execution passes guardrails and the read-only / kill-switch
gate. Every call -- read or write -- is recorded in ``actions_log`` with the caller.
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any

import anyio
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from sqlalchemy import text
from starlette.types import Receive, Scope, Send

from app import approvals
from app.actions import WritesBlockedError
from app.analytics import reports
from app.analytics.periods import parse_period
from app.config import get_settings
from app.db import session_scope
from app.integrations.http import IntegrationError
from app.log import get_logger, scrub
from app.mcpserver.oauth import verify_access_token, www_authenticate
from app.models import ActionLog, ActionStatus, EntityStatus

log = get_logger(__name__)

INSTRUCTIONS = """Shopify hub: one store's Shopify orders, Google/Meta/TikTok ads and Higgsfield creatives.
Profit numbers are contribution profit from Shopify orders (revenue - tax - refunds - COGS - shipping - fees),
not platform-reported conversions. Periods: today, yesterday, last_N_days (complete days), this_month,
last_month, or YYYY-MM-DD..YYYY-MM-DD, in the store's timezone.
Write tools only create proposals; nothing executes until the user approves (approve_action) or an
auto-approve rule matches. Always show the user the proposal summary and ask before calling approve_action."""

server = FastMCP(
    "shopify-hub",
    instructions=INSTRUCTIONS,
    stateless_http=True,
    json_response=True,
    streamable_http_path="/mcp",
    # Host checks are done by Caddy + the tunnel; auth is enforced by MCPApp below.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

READ = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False
)
WRITE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=True
)
WRITE_META = {"anthropic/requiresUserInteraction": True}  # Claude Code: always confirm
EXPECTED_ERRORS = (
    ValueError,
    approvals.ApprovalError,
    WritesBlockedError,
    IntegrationError,
    KeyError,
)


def caller(ctx: Context | None) -> str:
    try:
        return str(ctx.request_context.request.state.mcp_caller)  # type: ignore[union-attr]
    except Exception:
        return "mcp"


def _json_safe(v: Any) -> Any:
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, dict):
        return {k: _json_safe(x) for k, x in v.items() if k != "ctx"}
    if isinstance(v, list | tuple):
        return [_json_safe(x) for x in v]
    return v if v is None or isinstance(v, str | int | float | bool) else str(v)


def logged(write: bool) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., Any]]:
    """Run the (sync) tool in a worker thread, log the call to actions_log, and turn expected
    errors into a clear ``{"error": ...}`` result instead of a stack trace."""

    def deco(fn: Callable[..., dict[str, Any]]) -> Callable[..., Any]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            who = caller(kwargs.get("ctx"))
            started = time.monotonic()
            status, error = ActionStatus.SUCCESS, None
            try:
                result = await anyio.to_thread.run_sync(functools.partial(fn, *args, **kwargs))
            except EXPECTED_ERRORS as exc:
                status, error = (
                    (
                        ActionStatus.BLOCKED
                        if isinstance(exc, WritesBlockedError)
                        else ActionStatus.FAILED
                    ),
                    scrub(str(exc)),
                )
                result = {"error": error}
            except Exception as exc:
                log.exception("mcp_tool_crashed", tool=fn.__name__)
                status, error = ActionStatus.FAILED, scrub(repr(exc))[:500]
                result = {"error": "internal error; see hub logs"}
            try:
                with session_scope() as s:
                    s.add(
                        ActionLog(
                            actor="mcp",
                            requested_by=who,
                            tool=fn.__name__,
                            action_type="mcp.write_tool" if write else "mcp.read_tool",
                            payload=_json_safe(kwargs),
                            status=status,
                            error=error,
                            result={
                                k: _json_safe(v)
                                for k, v in result.items()
                                if k in ("approval_id", "status", "auto_approved_by_rule", "error")
                            }
                            or None,
                            duration_ms=int((time.monotonic() - started) * 1000),
                        )
                    )
            except Exception:
                log.exception("mcp_audit_failed", tool=fn.__name__)
            return result

        return wrapper

    return deco


def _period(value: str | None) -> Any:
    return parse_period(value, get_settings().tz)


# --- read tools ------------------------------------------------------------------------------


@server.tool(title="Business summary", annotations=READ)
@logged(write=False)
def get_business_summary(period: str = "last_7_days", ctx: Context | None = None) -> dict[str, Any]:
    """Revenue, COGS, refunds, fees, contribution profit before/after ad spend, MER and margin for the
    period, with % change vs the previous period of equal length."""
    with session_scope() as s:
        return reports.business_summary(s, _period(period))


@server.tool(title="Profit by product", annotations=READ)
@logged(write=False)
def get_profit_by_product(
    period: str = "last_30_days", limit: int = 25, ctx: Context | None = None
) -> dict[str, Any]:
    """Per product: units, net sales, COGS, allocated refunds/shipping/fees, contribution and margin (before ads)."""
    with session_scope() as s:
        return reports.profit_by_product(s, _period(period), limit=max(1, min(limit, 100)))


@server.tool(title="Platform performance", annotations=READ)
@logged(write=False)
def get_platform_performance(
    period: str = "last_7_days", ctx: Context | None = None
) -> dict[str, Any]:
    """Per ad platform: spend, CTR, CPA, ROAS and contribution after spend using Shopify-attributed orders,
    plus what the platform itself claims (to spot over-reporting)."""
    with session_scope() as s:
        return reports.platform_performance(s, _period(period))


@server.tool(title="Campaigns and ad sets", annotations=READ)
@logged(write=False)
def get_campaigns(
    platform: str | None = None, period: str = "last_7_days", ctx: Context | None = None
) -> dict[str, Any]:
    """Campaigns and ad sets with ids, status, daily budget, spend and contribution profit for the period.
    Use the ids with propose_budget_change / propose_pause_ad / propose_activate."""
    p = _period(period)
    s = get_settings()
    with session_scope() as db:
        sql = """
            SELECT c.platform, c.external_id AS campaign_id, c.name AS campaign, c.status AS campaign_status,
                   c.daily_budget AS campaign_budget, s.external_id AS ad_set_id, s.name AS ad_set,
                   s.status AS ad_set_status, s.daily_budget AS ad_set_budget,
                   COALESCE(SUM(p.spend),0) AS spend, COALESCE(SUM(p.contribution_profit),0) AS contribution
            FROM campaigns c JOIN ad_sets s ON s.campaign_id = c.id
            LEFT JOIN ads a ON a.ad_set_id = s.id
            LEFT JOIN v_ad_daily_profit p ON p.ad_id = a.id AND p.date BETWEEN :a AND :b
            WHERE c.status != 'deleted' {platform_filter}
            GROUP BY c.platform, c.external_id, c.name, c.status, c.daily_budget, s.external_id, s.name, s.status, s.daily_budget
            ORDER BY spend DESC LIMIT 200"""
        params: dict[str, Any] = {"a": p.start, "b": p.end}
        if platform:
            params["platform"] = platform
        query = sql.format(platform_filter="AND c.platform = :platform" if platform else "")
        rows = db.execute(text(query), params).all()
    items = [
        {k: (float(v) if isinstance(v, Decimal) else v) for k, v in r._mapping.items()}
        for r in rows
    ]
    for i in items:
        i["contribution_profit_after_spend"] = round(float(i.pop("contribution") or 0), 2)
        i["spend"] = round(float(i["spend"] or 0), 2)
    return {"period": p.as_dict(s.store_timezone), "currency": s.store_currency, "ad_sets": items}


@server.tool(title="Top creatives", annotations=READ)
@logged(write=False)
def get_top_creatives(
    period: str = "last_30_days",
    metric: str = "contribution_profit",
    limit: int = 10,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Best creatives by contribution_profit | profit_per_1000_spend | hook_rate_pct | ctr_pct | cpa | spend,
    with their traits. Ratio metrics only rank creatives with enough data."""
    with session_scope() as s:
        return reports.top_creatives(
            s, _period(period), metric=metric, limit=max(1, min(limit, 50))
        )


@server.tool(title="Creative trait insights", annotations=READ)
@logged(write=False)
def get_creative_trait_insights(
    period: str = "last_90_days", min_creatives: int = 3, ctx: Context | None = None
) -> dict[str, Any]:
    """How hook type, avatar, angle, length, format, CTA and voiceover relate to profit per $1,000 spend,
    hook rate and CTR. Small samples are flagged."""
    with session_scope() as s:
        return reports.creative_trait_insights(
            s, _period(period), min_creatives=max(1, min_creatives)
        )


@server.tool(title="Pending approvals", annotations=READ)
@logged(write=False)
def get_pending_approvals(ctx: Context | None = None) -> dict[str, Any]:
    """Proposals waiting for the user's decision, with summaries and expiry."""
    with session_scope() as s:
        approvals.expire_old(s)
    with session_scope() as s:
        return reports.pending_approvals(s)


@server.tool(title="Budget recommendation", annotations=READ)
@logged(write=False)
def get_budget_recommendation(ctx: Context | None = None) -> dict[str, Any]:
    """The latest Thompson-sampling budget run: per-platform marginal ROI after spend (posterior mean +/- sd),
    P(best), current vs recommended daily budget, and the proposals it created."""
    from app.ml import bandit

    with session_scope() as s:
        return bandit.latest(s) or {
            "status": "no run yet",
            "notes": "runs nightly at 06:45, or call propose_budget_reallocation",
        }


@server.tool(title="Creative model status", annotations=READ)
@logged(write=False)
def get_model_status(ctx: Context | None = None) -> dict[str, Any]:
    """The creative profit model: labeled creatives vs the 50 needed, whether a model is active, its CV error
    vs baseline and top features."""
    from app.ml import model

    with session_scope() as s:
        return model.status(s)


@server.tool(title="Creative generation spend", annotations=READ)
@logged(write=False)
def get_generation_spend(ctx: Context | None = None) -> dict[str, Any]:
    """Higgsfield spend this month vs the monthly cap (USD), job outcomes, cost per usable creative."""
    with session_scope() as s:
        return reports.generation_spend(s)


# --- write tools (proposals) -------------------------------------------------------------------


@server.tool(title="Propose budget change", annotations=WRITE, meta=WRITE_META)
@logged(write=True)
def propose_budget_change(
    platform: str,
    level: str,
    external_id: str,
    new_daily_budget: float,
    rationale: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Propose a new daily budget for a campaign or ad set (level = campaign | ad_set). Creates a pending
    approval; limited by max_budget_change_pct."""
    with session_scope() as s:
        payload, summary = approvals.build_budget_change(
            s, platform, level, external_id, new_daily_budget
        )
    return approvals.propose(
        "budget_change", payload, summary, rationale=rationale, requested_by=caller(ctx)
    )


@server.tool(title="Propose pausing", annotations=WRITE, meta=WRITE_META)
@logged(write=True)
def propose_pause_ad(
    platform: str, external_id: str, rationale: str, level: str = "ad", ctx: Context | None = None
) -> dict[str, Any]:
    """Propose pausing an ad (or level = ad_set | campaign). Creates a pending approval."""
    with session_scope() as s:
        payload, summary = approvals.build_status(
            s, platform, level, external_id, EntityStatus.PAUSED
        )
    return approvals.propose(
        "pause_ad", payload, summary, rationale=rationale, requested_by=caller(ctx)
    )


@server.tool(title="Propose activating", annotations=WRITE, meta=WRITE_META)
@logged(write=True)
def propose_activate(
    platform: str, level: str, external_id: str, rationale: str, ctx: Context | None = None
) -> dict[str, Any]:
    """Propose turning on a paused ad / ad set / campaign (e.g. one created by launch_creative)."""
    with session_scope() as s:
        payload, summary = approvals.build_status(
            s, platform, level, external_id, EntityStatus.ACTIVE
        )
    return approvals.propose(
        "activate", payload, summary, rationale=rationale, requested_by=caller(ctx)
    )


@server.tool(title="Propose budget reallocation", annotations=WRITE, meta=WRITE_META)
@logged(write=True)
def propose_budget_reallocation(
    window_days: int = 28, ctx: Context | None = None
) -> dict[str, Any]:
    """Run the budget bandit now: move daily budget between platforms toward the best marginal ROI after
    spend (total unchanged, within daily change limits) and create budget proposals for approval."""
    from app.ml import bandit

    out = bandit.run(window_days=max(7, min(window_days, 90)))
    keys = ("platform", "method", "post_mean", "post_sd", "p_best", "current_budget", "new_budget")
    return {k: out[k] for k in ("run_id", "status", "notes", "proposals")} | {
        "arms": [{k: a[k] for k in keys} for a in out["arms"]]
    }


@server.tool(title="Generate creatives", annotations=WRITE, meta=WRITE_META)
@logged(write=True)
def generate_creatives(
    brief: dict[str, Any],
    product_id: int | None = None,
    n: int = 3,
    model: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Propose generating n UGC variants with Higgsfield. brief fields: kind (video|image), angles[], hook_types[],
    avatar_types[], hooks[] (opening lines), aspect_ratio, duration_seconds, voiceover, cta, style, notes,
    reference_image_url, extra_params{}. Returns the cost estimate; spends nothing until approved."""
    from app.creatives.briefs import CreativeBrief

    data = (
        dict(brief)
        | ({"product_id": product_id} if product_id is not None else {})
        | ({"model": model} if model else {})
    )
    b = CreativeBrief.model_validate(data)
    est = None
    s = get_settings()
    if s.higgsfield_configured:
        from app.creatives.pipeline import estimate_brief
        from app.integrations.higgsfield import HiggsfieldClient

        _, est = estimate_brief(HiggsfieldClient(s), b, n, s)
    predictions = _predict_variants(b, n, s)
    payload = {
        "brief": b.model_dump(mode="json"),
        "n": n,
        "estimated_usd": str(est) if est is not None else None,
        "predicted_profit_per_1000": predictions,
    }
    summary = (
        f"generate {n} {b.kind} variant(s)"
        + (f" for product {b.product_id}" if b.product_id else "")
        + (
            f", estimated ${est}"
            if est is not None
            else ", cost unknown (Higgsfield not configured)"
        )
    )
    if predictions:
        summary += f"; model predicts {min(predictions):,.0f} to {max(predictions):,.0f} profit per 1,000 spend"
    return approvals.propose("generate_creatives", payload, summary, requested_by=caller(ctx))


def _predict_variants(brief: Any, n: int, s: Any) -> list[float] | None:
    """Model predictions per variant (None until a model is active)."""
    from app.creatives.briefs import make_variants
    from app.ml import model

    try:
        default = brief.model or s.higgsfield_video_model or s.higgsfield_image_model or "model"
        variants = make_variants(brief, n, default)
        rows = [
            v.traits | {"kind": brief.kind, "duration_seconds": brief.duration_seconds}
            for v in variants
        ]
        return model.predict(rows)
    except Exception:
        log.exception("prediction_failed")
        return None


@server.tool(title="Launch creative", annotations=WRITE, meta=WRITE_META)
@logged(write=True)
def launch_creative(
    creative_id: int,
    platforms: list[str],
    budget: float | None = None,
    landing_url: str | None = None,
    primary_text: str | None = None,
    headline: str | None = None,
    countries: list[str] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Propose uploading a ready creative to meta / tiktok / google and creating a PAUSED ad (and a new
    PAUSED campaign at `budget`/day per platform when given). Activate later with propose_activate."""
    with session_scope() as s:
        payload, summary = approvals.creative_launch_payload(
            s,
            creative_id,
            platforms,
            budget,
            landing_url,
            primary_text,
            headline,
            countries,
            get_settings(),
        )
    return approvals.propose("launch_creative", payload, summary, requested_by=caller(ctx))


@server.tool(
    title="Emergency stop",
    annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False
    ),
)
@logged(write=True)
def emergency_stop(reason: str, ctx: Context | None = None) -> dict[str, Any]:
    """Turn the kill switch ON immediately: every hub write (budgets, ads, generation) is blocked.
    Use when something looks wrong. Only the owner can turn it off again (CLI), not Claude."""
    from app import business_settings

    with session_scope() as s:
        business_settings.set_value(
            s, "kill_switch", True, actor="mcp", requested_by=f"{caller(ctx)}: {reason}"[:255]
        )
    return {
        "kill_switch": True,
        "note": "All writes are blocked. To resume, the owner runs: "
        "docker compose exec api python -m app.cli kill-switch off",
    }


@server.tool(title="Approve proposal", annotations=WRITE, meta=WRITE_META)
@logged(write=True)
def approve_action(approval_id: int, ctx: Context | None = None) -> dict[str, Any]:
    """Execute a pending proposal. Only call this when the user has explicitly approved this exact id."""
    return approvals.approve(approval_id, decided_by=caller(ctx), via_mcp=True)


@server.tool(title="Reject proposal", annotations=WRITE)
@logged(write=True)
def reject_action(
    approval_id: int, reason: str | None = None, ctx: Context | None = None
) -> dict[str, Any]:
    """Reject a pending proposal (nothing is executed)."""
    return approvals.reject(approval_id, decided_by=caller(ctx), reason=reason)


# --- ASGI: auth in front of the SDK app -------------------------------------------------------


class MCPApp:
    """Requires a valid bearer token on /mcp (OAuth access token or MCP_BEARER_TOKEN);
    otherwise 401 with the discovery header Claude needs."""

    def __init__(self) -> None:
        self.inner: Any = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"].rstrip("/") == "/mcp":
            headers = dict(scope.get("headers") or [])
            auth = headers.get(b"authorization", b"").decode()
            token = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
            who = await anyio.to_thread.run_sync(verify_access_token, token) if token else None
            if who is None:
                s = get_settings()
                body = b'{"error":"invalid_token","error_description":"authentication required"}'
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [
                            (b"content-type", b"application/json"),
                            (
                                b"www-authenticate",
                                www_authenticate(s, "invalid_token" if token else None).encode(),
                            ),
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": body})
                return
            scope.setdefault("state", {})["mcp_caller"] = who
        if self.inner is None:
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [(b"content-type", b"text/plain")],
                }
            )
            await send({"type": "http.response.body", "body": b"MCP server not started"})
            return
        await self.inner(scope, receive, send)


mcp_app = MCPApp()


@asynccontextmanager
async def mcp_lifespan() -> Any:
    """Fresh session manager per app lifespan (the SDK's manager runs only once)."""
    server._session_manager = None
    mcp_app.inner = server.streamable_http_app()
    async with server.session_manager.run():
        yield
    mcp_app.inner = None
