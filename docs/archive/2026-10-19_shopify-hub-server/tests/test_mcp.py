"""Phase 5: periods, reports, approvals, OAuth flow, and the /mcp endpoint end to end."""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal as D
from typing import Any
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

import fakeredis
import pytest
import shopify_fixtures as fx
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app import approvals, business_settings
from app.analytics import reports
from app.analytics.periods import Period, parse_period
from app.config import get_settings
from app.integrations.ads import sync as ads_sync
from app.integrations.ads.base import (
    AccountInfo,
    AdInfo,
    AdSetInfo,
    CampaignInfo,
    DailyMetric,
    Structure,
)
from app.integrations.shopify import sync as shopify_sync
from app.integrations.shopify.mapping import parse_order
from app.models import (
    ActionLog,
    Ad,
    ApprovalStatus,
    Creative,
    CreativeAdLink,
    CreativeStatus,
    CreativeTrait,
    EntityStatus,
    PendingApproval,
    Platform,
)

NY = ZoneInfo("America/New_York")
DAY = date(2026, 10, 1)
P = Period(DAY, DAY, "test day")

# --- periods ---------------------------------------------------------------------------------


def test_periods() -> None:
    today = date(2026, 10, 18)
    p = parse_period("last_7_days", NY, today)
    assert (p.start, p.end, p.days) == (date(2026, 10, 11), date(2026, 10, 17), 7)
    assert p.previous().end == date(2026, 10, 10) and p.previous().days == 7
    assert parse_period("last_month", NY, today).start == date(2026, 9, 1)
    assert parse_period("this_month", NY, today).end == today
    assert parse_period("2026-10-01..2026-10-03", NY, today).days == 3
    with pytest.raises(ValueError):
        parse_period("forever", NY, today)
    with pytest.raises(ValueError):
        parse_period("2026-10-05..2026-10-01", NY, today)


# --- seeded store ------------------------------------------------------------------------------


def seed(session: Session) -> None:
    """One Meta ad with $40 spend and two attributed orders (one with an uncosted item)."""
    st = Structure(
        AccountInfo("act1", "Shop", "USD", "America/New_York"),
        [CampaignInfo("c1", "Fall", EntityStatus.ACTIVE, daily_budget=D("50"))],
        [AdSetInfo("s1", "c1", "Broad", EntityStatus.ACTIVE)],
        [AdInfo("6001", "s1", "Hook A", EntityStatus.ACTIVE)],
    )
    ads_sync.upsert_structure(session, Platform.META, st)
    ads_sync.upsert_metrics(
        session,
        Platform.META,
        [
            DailyMetric(
                "6001",
                DAY,
                spend=D("40"),
                impressions=4000,
                clicks=80,
                video_3s_views=1200,
                purchases=3,
            )
        ],
    )
    visit = fx.visit(utm={"source": "facebook", "content": "6001"})
    for oid in (1, 2):
        node = fx.order(
            oid,
            processed_at="2026-10-01T16:00:00Z",
            last_visit=visit,
            customer=9000 + oid,
            lines=[fx.line(oid * 10, 2, "50.00", cost="7.00" if oid == 1 else None)],
        )
        shopify_sync.upsert_order(session, parse_order(node, NY, 2.9, 0.3))
    shopify_sync.recompute_customers(session, [1, 2])
    c = Creative(type="video", status=CreativeStatus.LAUNCHED)
    session.add(c)
    session.flush()
    session.add(
        CreativeTrait(
            creative_id=c.id,
            hook_type="pov",
            avatar_type="woman_25_34",
            angle="saves_time",
            length_bucket="0-8s",
            format="9x16_ugc_video",
            cta="shop_now",
            voiceover=True,
            extra={},
        )
    )
    ad = session.scalars(select(Ad)).one()
    session.add(
        CreativeAdLink(creative_id=c.id, ad_id=ad.id, platform=Platform.META, external_ad_id="6001")
    )
    session.commit()


def test_business_summary(session: Session) -> None:
    seed(session)
    r = reports.business_summary(session, P)
    s = r["summary"]
    assert r["period"]["start"] == "2026-10-01" and r["currency"] == "USD"
    assert s["orders_count"] == 2 and s["net_revenue"] == 200.0
    assert s["cogs"] == 14.0 and s["payment_fees"] == 6.98 and s["ad_spend"] == 40.0
    assert (
        s["contribution_profit_before_ads"] == 179.02
        and s["contribution_profit_after_ads"] == 139.02
    )
    assert (
        s["mer"] == 5.0
        and s["orders_missing_cost_count"] == 1
        and s["new_customer_orders_count"] == 2
    )
    assert any("without a unit cost" in n for n in r["notes"])


def test_platform_performance_compares_claims(session: Session) -> None:
    seed(session)
    (meta,) = reports.platform_performance(session, P)["platforms"]
    assert (
        meta["platform"] == "meta" and meta["attributed_orders_count"] == 2 and meta["cpa"] == 20.0
    )
    assert meta["roas"] == 5.0 and meta["ctr_pct"] == 2.0
    assert (
        meta["platform_reported_purchases_count"] == 3
        and meta["platform_overreporting_ratio"] == 1.5
    )


def test_profit_by_product_allocates_order_costs(session: Session) -> None:
    seed(session)
    (prod,) = reports.profit_by_product(session, P)["products"]
    assert prod["units_count"] == 4 and prod["net_sales"] == 200.0 and prod["cogs"] == 14.0
    assert (
        prod["refunds_shipping_fees"] == 6.98 and prod["contribution_profit_before_ads"] == 179.02
    )


def test_creative_reports(session: Session) -> None:
    seed(session)
    top = reports.top_creatives(session, P, metric="profit_per_1000_spend")
    (c,) = top["creatives"]
    assert c["spend"] == 40.0 and c["enough_data"] is True and c["hook_rate_pct"] == 30.0
    assert c["contribution_profit"] == 139.02 and c["profit_per_1000_spend"] == 3475.5
    ins = reports.creative_trait_insights(session, P, min_creatives=1)["traits"]
    assert ins["hook_type"][0]["value"] == "pov" and ins["voiceover"][0]["value"] == "true"
    with pytest.raises(ValueError):
        reports.top_creatives(session, P, metric="vibes")


# --- approvals ----------------------------------------------------------------------------------


class FakePlatform:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    def update_budget(self, level: str, external_id: str, budget: D, ctx: Any = None) -> None:
        self.calls.append(("budget", level, external_id, budget, ctx.approval_id))

    def set_status(
        self, level: str, external_id: str, status: EntityStatus, ctx: Any = None
    ) -> None:
        self.calls.append(("status", level, external_id, status))


def _writes_on(factory) -> None:  # type: ignore[no-untyped-def]
    with factory() as s:
        business_settings.set_value(s, "read_only", False, actor="test")


def test_budget_proposal_approve_executes_once(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    seed(session)
    _writes_on(session_factory)
    fake = FakePlatform()
    with session_factory() as s:
        business_settings.set_value(s, "daily_spend_cap", "500", actor="test")
        payload, summary = approvals.build_budget_change(s, "meta", "campaign", "c1", 55)
    assert payload["change_pct"] == 10.0 and "50.00 -> 55.00 (+10.0%)" in summary
    res = approvals.propose(
        "budget_change", payload, summary, requested_by="claude", session_factory=session_factory
    )
    assert res["status"] == "pending" and fake.calls == []
    out = approvals.approve(
        res["approval_id"],
        "ben",
        via_mcp=True,
        session_factory=session_factory,
        platform_factory=lambda p: fake,
    )
    assert out["status"] == "executed" and fake.calls == [
        ("budget", "campaign", "c1", D("55.00"), res["approval_id"])
    ]
    with pytest.raises(approvals.ApprovalError, match="not pending"):
        approvals.approve(
            res["approval_id"],
            "ben",
            session_factory=session_factory,
            platform_factory=lambda p: fake,
        )
    assert len(fake.calls) == 1


def test_guardrail_blocks_big_budget_jump(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    seed(session)
    with session_factory() as s:
        payload, summary = approvals.build_budget_change(s, "meta", "campaign", "c1", 100)  # +100%
    with pytest.raises(approvals.guardrails.GuardrailError, match="max_budget_change_pct"):
        approvals.propose("budget_change", payload, summary, session_factory=session_factory)


def test_auto_approve_rule_executes_immediately(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    seed(session)
    _writes_on(session_factory)
    with session_factory() as s:
        business_settings.set_value(
            s, "auto_approve_rules", [{"name": "pauses", "action_type": "pause_ad"}], actor="t"
        )
        payload, summary = approvals.build_status(s, "meta", "ad", "6001", EntityStatus.PAUSED)
    fake = FakePlatform()
    res = approvals.propose(
        "pause_ad",
        payload,
        summary,
        session_factory=session_factory,
        platform_factory=lambda p: fake,
    )
    assert res["status"] == "executed" and res["auto_approved_by_rule"] == "pauses"
    assert fake.calls == [("status", "ad", "6001", EntityStatus.PAUSED)]


def test_match_rule_limits() -> None:
    rule = business_settings.AutoApproveRule(
        name="small",
        action_type="budget_change",
        max_change_pct=10,
        max_amount=D("100"),
        platforms=["meta"],
    )
    ok = {"platform": "meta", "change_pct": 8, "new_daily_budget": "54"}
    assert approvals.match_rule([rule], "budget_change", ok) is rule
    assert approvals.match_rule([rule], "budget_change", ok | {"change_pct": 15}) is None
    assert approvals.match_rule([rule], "budget_change", ok | {"platform": "tiktok"}) is None
    assert approvals.match_rule([rule], "budget_change", ok | {"new_daily_budget": "150"}) is None


def test_failure_in_read_only_is_recorded(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    seed(session)  # read-only stays ON
    with session_factory() as s:
        payload, summary = approvals.build_status(s, "meta", "ad", "6001", EntityStatus.PAUSED)
    res = approvals.propose("pause_ad", payload, summary, session_factory=session_factory)

    class GatedFake(FakePlatform):
        def set_status(
            self, level: str, external_id: str, status: EntityStatus, ctx: Any = None
        ) -> None:
            from app.actions import write_action

            with write_action(
                "meta.set_status",
                target_type=level,
                target_id=external_id,
                payload={},
                ctx=ctx,
                session_factory=session_factory,
            ):
                super().set_status(level, external_id, status, ctx)

    out = approvals.approve(
        res["approval_id"],
        "ben",
        session_factory=session_factory,
        platform_factory=lambda p: GatedFake(),
    )
    assert out["status"] == "failed" and "read-only" in out["result"]["error"]


def test_reject_expiry_and_mcp_approval_switch(session_factory, session: Session) -> None:  # type: ignore[no-untyped-def]
    seed(session)
    with session_factory() as s:
        payload, summary = approvals.build_status(s, "meta", "ad", "6001", EntityStatus.PAUSED)
    a = approvals.propose("pause_ad", payload, summary, session_factory=session_factory)[
        "approval_id"
    ]
    assert (
        approvals.reject(a, "ben", "not now", session_factory=session_factory)["status"]
        == "rejected"
    )
    b = approvals.propose("pause_ad", payload, summary, session_factory=session_factory)[
        "approval_id"
    ]
    with session_factory() as s:
        s.get(PendingApproval, b).expires_at = datetime.now(UTC) - timedelta(minutes=1)
    with pytest.raises(approvals.ApprovalError, match="expired"):
        approvals.approve(
            b, "ben", session_factory=session_factory, platform_factory=lambda p: FakePlatform()
        )
    c = approvals.propose("pause_ad", payload, summary, session_factory=session_factory)[
        "approval_id"
    ]
    with session_factory() as s:
        business_settings.set_value(s, "approvals_via_mcp", False, actor="t")
    with pytest.raises(approvals.ApprovalError, match="turned off"):
        approvals.approve(c, "claude", via_mcp=True, session_factory=session_factory)
    session.expire_all()
    assert session.get(PendingApproval, c).status == ApprovalStatus.PENDING  # untouched


# --- OAuth + /mcp ------------------------------------------------------------------------------

STATIC = "static-test-token"
PASSWORD = "owner-pass"
CALLBACK = "https://claude.ai/api/mcp/auth_callback"


@pytest.fixture
def api(db_url: str, engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    import app.db as db
    import app.queue as q

    for k, v in {
        "DATABASE_URL": db_url,
        "PUBLIC_BASE_URL": "https://hub.example.com",
        "MCP_BEARER_TOKEN": STATIC,
        "MCP_OWNER_PASSWORD": PASSWORD,
        "STORE_TIMEZONE": "America/New_York",
    }.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()
    redis = fakeredis.FakeRedis()
    monkeypatch.setattr(q, "get_redis", lambda: redis)
    from app.main import app

    with TestClient(app, base_url="https://hub.example.com") as c:
        yield c
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    db._session_factory.cache_clear()


def pkce() -> tuple[str, str]:
    verifier = "v" * 50
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    )
    return verifier, challenge


def test_discovery_metadata(api: TestClient) -> None:
    r = api.post("/mcp", json={})
    assert r.status_code == 401
    assert (
        'resource_metadata="https://hub.example.com/.well-known/oauth-protected-resource"'
        in r.headers["www-authenticate"]
    )
    prm = api.get("/.well-known/oauth-protected-resource").json()
    assert prm["resource"] == "https://hub.example.com/mcp" and prm["authorization_servers"] == [
        "https://hub.example.com"
    ]
    assert api.get("/.well-known/oauth-protected-resource/mcp").json() == prm
    asm = api.get("/.well-known/oauth-authorization-server").json()
    assert asm["code_challenge_methods_supported"] == ["S256"] and asm[
        "registration_endpoint"
    ].endswith("/oauth/register")
    assert (
        asm["client_id_metadata_document_supported"] is True
        and "none" in asm["token_endpoint_auth_methods_supported"]
    )


def _authorize(
    api: TestClient,
    client_id: str,
    challenge: str,
    password: str = PASSWORD,
    redirect: str = CALLBACK,
) -> Any:
    form = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": "st8",
        "scope": "hub",
        "resource": "https://hub.example.com/mcp",
        "password": password,
        "decision": "allow",
    }
    return api.post("/oauth/authorize", data=form, follow_redirects=False)


def test_full_oauth_flow_with_refresh_rotation(api: TestClient) -> None:
    reg = api.post("/oauth/register", json={"client_name": "Claude", "redirect_uris": [CALLBACK]})
    assert reg.status_code == 201
    cid = reg.json()["client_id"]
    verifier, challenge = pkce()
    page = api.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": cid,
            "redirect_uri": CALLBACK,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": "st8",
        },
    )
    assert page.status_code == 200 and "Connect Claude" in page.text

    assert _authorize(api, cid, challenge, password="wrong").status_code == 401
    ok = _authorize(api, cid, challenge)
    assert ok.status_code == 302
    q = parse_qs(urlsplit(ok.headers["location"]).query)
    assert q["state"] == ["st8"] and q["iss"] == ["https://hub.example.com"]
    code = q["code"][0]

    bad = api.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": cid,
            "redirect_uri": CALLBACK,
            "code_verifier": "x" * 50,
        },
    )
    assert bad.json()["error"] == "invalid_grant"
    # the code was burned by the failed attempt: single use
    again = api.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": cid,
            "redirect_uri": CALLBACK,
            "code_verifier": verifier,
        },
    )
    assert again.json()["error"] == "invalid_grant"

    ok = _authorize(api, cid, challenge)
    code = parse_qs(urlsplit(ok.headers["location"]).query)["code"][0]
    tok = api.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": cid,
            "redirect_uri": CALLBACK,
            "code_verifier": verifier,
        },
    ).json()
    assert tok["token_type"] == "Bearer" and tok["expires_in"] == 3600

    new = api.post(
        "/oauth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": tok["refresh_token"],
            "client_id": cid,
        },
    ).json()
    assert new["access_token"] != tok["access_token"]
    reuse = api.post(
        "/oauth/token", data={"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]}
    )
    assert reuse.status_code == 400 and reuse.json()["error"] == "invalid_grant"

    r = _rpc(api, new["access_token"], "tools/list")
    assert r.status_code == 200 and any(
        t["name"] == "get_business_summary" for t in r.json()["result"]["tools"]
    )


def test_authorize_rejects_bad_requests(api: TestClient) -> None:
    cid = api.post(
        "/oauth/register", json={"client_name": "Claude", "redirect_uris": [CALLBACK]}
    ).json()["client_id"]
    _, challenge = pkce()
    assert (
        _authorize(api, cid, challenge, redirect="https://evil.example/cb").status_code == 400
    )  # unregistered redirect
    assert _authorize(api, "nope", challenge).status_code == 400
    no_pkce = api.get(
        "/oauth/authorize",
        params={"response_type": "code", "client_id": cid, "redirect_uri": CALLBACK},
        follow_redirects=False,
    )
    assert no_pkce.status_code == 302 and "PKCE" in no_pkce.headers["location"]
    assert (
        api.post("/oauth/register", json={"redirect_uris": ["javascript:alert(1)"]}).status_code
        == 400
    )
    for _ in range(5):
        _authorize(api, cid, challenge, password="wrong")
    assert _authorize(api, cid, challenge).status_code == 429  # locked out after repeated failures


def test_loopback_redirect_any_port_and_cimd_host_allowlist(
    api: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.mcpserver import oauth

    assert oauth.redirect_allowed(
        ["http://localhost:3118/callback"], "http://127.0.0.1:54001/callback"
    )
    assert not oauth.redirect_allowed(
        ["http://localhost:3118/callback"], "http://localhost:54001/other"
    )
    s = get_settings()
    assert (
        oauth.get_client("https://evil.example.com/client.json", s) is None
    )  # not a trusted CIMD host

    class Resp:
        status_code, content = 200, b"{}"

        @staticmethod
        def json() -> dict[str, Any]:
            return {
                "client_id": "https://claude.ai/oauth/claude-code-client-metadata",
                "client_name": "Claude Code",
                "redirect_uris": ["http://localhost/callback"],
            }

    monkeypatch.setattr(oauth.httpx, "get", lambda url, timeout, follow_redirects: Resp())
    c = oauth.get_client("https://claude.ai/oauth/claude-code-client-metadata", s)
    assert c is not None and c.client_name == "Claude Code"


def _rpc(
    api: TestClient, token: str | None, method: str, params: dict[str, Any] | None = None
) -> Any:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": "2025-06-18",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return api.post(
        "/mcp",
        headers=headers,
        content=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}),
    )


def test_mcp_tools_over_http_with_static_token_are_audited(
    api: TestClient, session: Session
) -> None:
    seed(session)
    init = _rpc(
        api,
        STATIC,
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        },
    )
    assert init.status_code == 200 and init.json()["result"]["serverInfo"]["name"] == "shopify-hub"
    assert _rpc(api, "wrong-token", "tools/list").status_code == 401

    r = _rpc(
        api,
        STATIC,
        "tools/call",
        {"name": "get_business_summary", "arguments": {"period": "2026-10-01"}},
    )
    body = r.json()["result"]
    data = body.get("structuredContent") or json.loads(body["content"][0]["text"])
    assert data["summary"]["orders_count"] == 2 and data["period"]["start"] == "2026-10-01"

    r = _rpc(
        api,
        STATIC,
        "tools/call",
        {
            "name": "propose_pause_ad",
            "arguments": {"platform": "meta", "external_id": "6001", "rationale": "CPA too high"},
        },
    )
    res = r.json()["result"]
    res = res.get("structuredContent") or json.loads(res["content"][0]["text"])
    assert res["status"] == "pending" and "approve" in res["next"]

    bad = _rpc(
        api, STATIC, "tools/call", {"name": "get_top_creatives", "arguments": {"metric": "vibes"}}
    )
    out = bad.json()["result"]
    out = out.get("structuredContent") or json.loads(out["content"][0]["text"])
    assert "metric must be one of" in out["error"]

    session.expire_all()
    logs = session.scalars(
        select(ActionLog).where(ActionLog.actor == "mcp").order_by(ActionLog.id)
    ).all()
    assert [(l.tool, l.status.value) for l in logs] == [  # noqa: E741
        ("get_business_summary", "success"),
        ("propose_pause_ad", "success"),
        ("get_top_creatives", "failed"),
    ]
    assert {l.requested_by for l in logs} == {"claude-code (static token)"}  # noqa: E741
    assert (
        session.scalars(select(PendingApproval)).one().requested_by == "claude-code (static token)"
    )
