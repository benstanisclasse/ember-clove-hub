"""A minimal, single-owner OAuth 2.1 authorization server for Claude custom connectors.

What Claude requires (claude.com/docs/connectors/building/authentication):
* MCP endpoint answers 401 + ``WWW-Authenticate: Bearer resource_metadata="<url>"``
* RFC 9728 protected-resource metadata whose ``resource`` == the MCP URL exactly
* RFC 8414 authorization-server metadata; PKCE S256; form-encoded /token; rotating
  refresh tokens; ``invalid_grant`` for dead ones; no client_credentials
* clients via Dynamic Client Registration (RFC 7591) or a Client ID Metadata Document
  (``client_id`` is an https URL); redirect to https://claude.ai/api/mcp/auth_callback,
  or a localhost loopback on any port for Claude Code

"Single owner": the consent page asks for ``MCP_OWNER_PASSWORD``. Only you can connect a
new Claude client; failed attempts are rate limited. Tokens are random; only SHA-256
hashes are stored, so a database leak doesn't leak working tokens.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import secrets
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode, urlsplit

import httpx
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy import select

from app.config import Settings, get_settings
from app.db import session_scope
from app.log import get_logger
from app.models import OAuthClient, OAuthToken

log = get_logger(__name__)
router = APIRouter(include_in_schema=False)
SCOPE = "hub"
CODE_TTL = timedelta(minutes=10)
MAX_CLIENTS = 50
MAX_PASSWORD_FAILURES = 5  # per IP per 15 minutes
NO_STORE = {"Cache-Control": "no-store", "Pragma": "no-cache"}


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _issuer(s: Settings) -> str:
    return s.public_base_url.rstrip("/")


def _now() -> datetime:
    return datetime.now(UTC)


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=UTC)


# --- metadata ----------------------------------------------------------------------------------


def protected_resource_metadata(s: Settings) -> dict[str, Any]:
    return {
        "resource": s.mcp_url,
        "authorization_servers": [_issuer(s)],
        "scopes_supported": [SCOPE],
        "bearer_methods_supported": ["header"],
        "resource_name": "Shopify hub",
    }


def authorization_server_metadata(s: Settings) -> dict[str, Any]:
    i = _issuer(s)
    return {
        "issuer": i,
        "authorization_endpoint": f"{i}/oauth/authorize",
        "token_endpoint": f"{i}/oauth/token",
        "registration_endpoint": f"{i}/oauth/register",
        "revocation_endpoint": f"{i}/oauth/revoke",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": [SCOPE, "offline_access"],
        "client_id_metadata_document_supported": True,
    }


@router.get("/.well-known/oauth-protected-resource")
@router.get("/.well-known/oauth-protected-resource/mcp")
def _prm() -> JSONResponse:
    return JSONResponse(protected_resource_metadata(get_settings()))


@router.get("/.well-known/oauth-authorization-server")
def _asm() -> JSONResponse:
    return JSONResponse(authorization_server_metadata(get_settings()))


# --- clients -------------------------------------------------------------------------------------


def _valid_redirect(uri: str) -> bool:
    try:
        u = urlsplit(uri)
    except ValueError:
        return False
    if u.fragment:
        return False
    if u.scheme == "https" and u.hostname:
        return True
    return u.scheme == "http" and u.hostname in ("localhost", "127.0.0.1")


def redirect_allowed(registered: list[str], uri: str) -> bool:
    """Exact match, except loopback redirects match any port and localhost == 127.0.0.1."""
    if uri in registered:
        return True
    try:
        u = urlsplit(uri)
    except ValueError:
        return False
    if u.scheme != "http" or u.hostname not in ("localhost", "127.0.0.1"):
        return False
    for r in registered:
        ru = urlsplit(r)
        if ru.scheme == "http" and ru.hostname in ("localhost", "127.0.0.1") and ru.path == u.path:
            return True
    return False


def _fetch_cimd(client_id: str, s: Settings) -> dict[str, Any] | None:
    """Client ID Metadata Document: only from trusted hosts (no SSRF to arbitrary URLs)."""
    u = urlsplit(client_id)
    trusted = {h.strip().lower() for h in s.mcp_cimd_hosts.split(",") if h.strip()}
    if u.scheme != "https" or (u.hostname or "").lower() not in trusted:
        return None
    try:
        resp = httpx.get(client_id, timeout=5, follow_redirects=False)
        if resp.status_code != 200 or len(resp.content) > 64 * 1024:
            return None
        doc = resp.json()
    except (httpx.HTTPError, ValueError):
        return None
    if doc.get("client_id") not in (None, client_id) or not isinstance(
        doc.get("redirect_uris"), list
    ):
        return None
    return doc


def get_client(client_id: str, s: Settings) -> OAuthClient | None:
    with session_scope() as db:
        c = db.get(OAuthClient, client_id)
        if c is not None:
            return None if c.revoked else c
    if client_id.startswith("https://"):
        doc = _fetch_cimd(client_id, s)
        if doc is None:
            return None
        uris = [u for u in doc["redirect_uris"] if isinstance(u, str) and _valid_redirect(u)]
        with session_scope() as db:
            c = OAuthClient(
                client_id=client_id,
                client_name=str(doc.get("client_name") or client_id)[:255],
                redirect_uris=uris,
                revoked=False,
            )
            db.merge(c)
        return c
    return None


@router.post("/oauth/register")
async def register(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except ValueError:
        return JSONResponse({"error": "invalid_client_metadata"}, status_code=400)
    uris = body.get("redirect_uris")
    if (
        not isinstance(uris, list)
        or not uris
        or not all(isinstance(u, str) and _valid_redirect(u) for u in uris)
    ):
        return JSONResponse({"error": "invalid_redirect_uri"}, status_code=400)
    if body.get("token_endpoint_auth_method", "none") != "none":
        return JSONResponse(
            {
                "error": "invalid_client_metadata",
                "error_description": "only public clients (token_endpoint_auth_method=none)",
            },
            status_code=400,
        )
    with session_scope() as db:
        count = len(
            db.scalars(select(OAuthClient.client_id).where(OAuthClient.revoked.is_(False))).all()
        )
        if count >= MAX_CLIENTS:
            return JSONResponse(
                {"error": "invalid_client_metadata", "error_description": "too many clients"},
                status_code=400,
            )
        client = OAuthClient(
            client_id="hub-" + secrets.token_urlsafe(18),
            client_name=str(body.get("client_name") or "MCP client")[:255],
            redirect_uris=uris[:10],
            revoked=False,
        )
        db.add(client)
    log.info("oauth_client_registered", client=client.client_name)
    return JSONResponse(
        status_code=201,
        headers=NO_STORE,
        content={
            "client_id": client.client_id,
            "client_id_issued_at": int(time.time()),
            "client_name": client.client_name,
            "redirect_uris": client.redirect_uris,
            "token_endpoint_auth_method": "none",
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
        },
    )


# --- authorize -----------------------------------------------------------------------------------

_PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Connect to Shopify hub</title><style>
body{{font-family:system-ui,sans-serif;max-width:420px;margin:12vh auto;padding:0 16px;color:#1a1a1a;background:#fafafa}}
.card{{background:#fff;border:1px solid #e3e3e3;border-radius:12px;padding:24px}}h1{{font-size:20px;margin:0 0 12px}}
p{{line-height:1.5;color:#444}}input[type=password]{{width:100%;padding:10px;margin:8px 0 16px;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}}
button{{padding:10px 16px;border-radius:8px;border:0;font-size:15px;cursor:pointer}}.ok{{background:#111;color:#fff}}.no{{background:#eee;margin-left:8px}}
.err{{color:#b00020}}</style></head><body><div class="card"><h1>Connect {client} to your Shopify hub?</h1>
<p>It will be able to read your store, ad and creative data and <b>propose</b> changes. Changes only run after you approve them.</p>
{error}<form method="post" action="/oauth/authorize">{hidden}<label>Owner password<input type="password" name="password" autofocus required></label>
<button class="ok" name="decision" value="allow">Allow</button><button class="no" name="decision" value="deny" formnovalidate>Deny</button></form></div></body></html>"""


def _error_page(message: str, status: int = 400) -> HTMLResponse:
    return HTMLResponse(
        f"<!doctype html><meta charset=utf-8><title>Error</title><p>{html.escape(message)}</p>",
        status_code=status,
    )


def _check_request(p: dict[str, str], s: Settings) -> tuple[OAuthClient | None, str | None]:
    """Validate an authorize request. Returns (client, error)."""
    client = get_client(p.get("client_id", ""), s)
    if client is None:
        return None, "Unknown OAuth client."
    if not redirect_allowed(client.redirect_uris, p.get("redirect_uri", "")):
        return None, "This redirect URI isn't registered for the client."
    if p.get("response_type") != "code":
        return client, "unsupported_response_type"
    if p.get("code_challenge_method") != "S256" or not p.get("code_challenge"):
        return client, "PKCE with S256 is required"
    if p.get("resource") and p["resource"].rstrip("/") != s.mcp_url.rstrip("/"):
        return client, "invalid_target"
    return client, None


def _redirect(uri: str, **params: str) -> RedirectResponse:
    sep = "&" if "?" in uri else "?"
    return RedirectResponse(
        uri + sep + urlencode({k: v for k, v in params.items() if v}), status_code=302
    )


AUTH_FIELDS = (
    "response_type",
    "client_id",
    "redirect_uri",
    "code_challenge",
    "code_challenge_method",
    "state",
    "scope",
    "resource",
)


@router.get("/oauth/authorize")
def authorize_page(request: Request) -> Response:
    s = get_settings()
    p = {k: request.query_params.get(k, "") for k in AUTH_FIELDS}
    client, error = _check_request(p, s)
    if client is None:
        return _error_page(error or "invalid request")
    if error:
        return _redirect(
            p["redirect_uri"], error="invalid_request", error_description=error, state=p["state"]
        )
    hidden = "".join(
        f'<input type="hidden" name="{k}" value="{html.escape(v)}">' for k, v in p.items()
    )
    return HTMLResponse(
        _PAGE.format(client=html.escape(client.client_name or "Claude"), hidden=hidden, error=""),
        headers={"X-Frame-Options": "DENY", **NO_STORE},
    )


def _too_many_failures(ip: str) -> bool:
    from app.queue import get_redis

    try:
        return int(get_redis().get(f"hub:oauth:fail:{ip}") or 0) >= MAX_PASSWORD_FAILURES
    except Exception:
        return False


def _record_failure(ip: str) -> None:
    from app.queue import get_redis

    try:
        r = get_redis()
        key = f"hub:oauth:fail:{ip}"
        r.incr(key)
        r.expire(key, 900)
    except Exception:  # noqa: S110 - rate limiting is best effort
        pass


@router.post("/oauth/authorize")
def authorize_submit(
    request: Request,
    password: str = Form(""),
    decision: str = Form("allow"),
    response_type: str = Form(""),
    client_id: str = Form(""),
    redirect_uri: str = Form(""),
    code_challenge: str = Form(""),
    code_challenge_method: str = Form(""),
    state: str = Form(""),
    scope: str = Form(""),
    resource: str = Form(""),
) -> Response:
    s = get_settings()
    p = {
        "response_type": response_type,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "state": state,
        "scope": scope,
        "resource": resource,
    }
    client, error = _check_request(p, s)
    if client is None:
        return _error_page(error or "invalid request")
    if error:
        return _redirect(
            redirect_uri, error="invalid_request", error_description=error, state=state
        )
    if decision != "allow":
        return _redirect(redirect_uri, error="access_denied", state=state)
    from app.collect import client_ip

    ip = client_ip(request) or "unknown"
    expected = s.mcp_owner_password.get_secret_value()
    if _too_many_failures(ip):
        return _error_page("Too many wrong passwords. Try again in 15 minutes.", 429)
    if not expected or not hmac.compare_digest(password.encode(), expected.encode()):
        _record_failure(ip)
        log.warning("oauth_bad_password", client=client.client_name)
        hidden = "".join(
            f'<input type="hidden" name="{k}" value="{html.escape(v)}">' for k, v in p.items()
        )
        return HTMLResponse(
            _PAGE.format(
                client=html.escape(client.client_name or "Claude"),
                hidden=hidden,
                error='<p class="err">Wrong password.</p>',
            ),
            status_code=401,
        )
    code = secrets.token_urlsafe(32)
    with session_scope() as db:
        db.add(
            OAuthToken(
                token_hash=_hash(code),
                kind="code",
                client_id=client.client_id,
                scope=SCOPE,
                redirect_uri=redirect_uri,
                code_challenge=code_challenge,
                resource=resource or s.mcp_url,
                expires_at=_now() + CODE_TTL,
                used=False,
            )
        )
    log.info("oauth_authorized", client=client.client_name)
    return _redirect(redirect_uri, code=code, state=state, iss=_issuer(s))


# --- token ---------------------------------------------------------------------------------------


def _err(error: str, description: str | None = None, status: int = 400) -> JSONResponse:
    body = {"error": error} | ({"error_description": description} if description else {})
    return JSONResponse(body, status_code=status, headers=NO_STORE)


def _issue(db: Any, client_id: str, resource: str | None, s: Settings) -> dict[str, Any]:
    access, refresh = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    ttl = timedelta(minutes=s.mcp_access_token_minutes)
    db.add(
        OAuthToken(
            token_hash=_hash(access),
            kind="access",
            client_id=client_id,
            scope=SCOPE,
            resource=resource,
            expires_at=_now() + ttl,
            used=False,
        )
    )
    db.add(
        OAuthToken(
            token_hash=_hash(refresh),
            kind="refresh",
            client_id=client_id,
            scope=SCOPE,
            resource=resource,
            expires_at=_now() + timedelta(days=s.mcp_refresh_token_days),
            used=False,
        )
    )
    return {
        "access_token": access,
        "token_type": "Bearer",
        "expires_in": int(ttl.total_seconds()),
        "refresh_token": refresh,
        "scope": SCOPE,
    }


def pkce_ok(verifier: str, challenge: str) -> bool:
    digest = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    )
    return bool(verifier) and hmac.compare_digest(digest, challenge or "")


@router.post("/oauth/token")
def token(
    grant_type: str = Form(""),
    code: str = Form(""),
    redirect_uri: str = Form(""),
    client_id: str = Form(""),
    code_verifier: str = Form(""),
    refresh_token: str = Form(""),
    resource: str = Form(""),
) -> JSONResponse:
    s = get_settings()
    with session_scope() as db:
        if grant_type == "authorization_code":
            row = db.get(OAuthToken, _hash(code))
            if row is None or row.kind != "code" or row.used or _aware(row.expires_at) < _now():
                return _err("invalid_grant", "code is invalid or expired")
            row.used = True  # single use, even if the checks below fail
            if row.client_id != client_id or row.redirect_uri != redirect_uri:
                return _err("invalid_grant", "client or redirect_uri mismatch")
            if not pkce_ok(code_verifier, row.code_challenge or ""):
                return _err("invalid_grant", "PKCE verification failed")
            return JSONResponse(_issue(db, client_id, row.resource, s), headers=NO_STORE)
        if grant_type == "refresh_token":
            row = db.get(OAuthToken, _hash(refresh_token))
            if row is None or row.kind != "refresh" or row.used or _aware(row.expires_at) < _now():
                return _err("invalid_grant", "refresh token is invalid, expired or already used")
            if client_id and row.client_id != client_id:
                return _err("invalid_grant", "client mismatch")
            client = db.get(OAuthClient, row.client_id)
            if client is None or client.revoked:
                return _err("invalid_grant", "client revoked")
            row.used = True  # rotation: every refresh token works once
            return JSONResponse(_issue(db, row.client_id, row.resource, s), headers=NO_STORE)
    return _err("unsupported_grant_type")


@router.post("/oauth/revoke")
def revoke(token: str = Form("")) -> Response:
    with session_scope() as db:
        row = db.get(OAuthToken, _hash(token))
        if row is not None:
            row.used = True
    return Response(status_code=200)


# --- verification (used by the MCP auth middleware) ---------------------------------------------


def verify_access_token(token_value: str, s: Settings | None = None) -> str | None:
    """Return the caller identity for a valid bearer token, else None."""
    s = s or get_settings()
    static = s.mcp_bearer_token.get_secret_value()
    if static and hmac.compare_digest(token_value.encode(), static.encode()):
        return "claude-code (static token)"
    with session_scope() as db:
        row = db.get(OAuthToken, _hash(token_value))
        if row is None or row.kind != "access" or row.used or _aware(row.expires_at) < _now():
            return None
        client = db.get(OAuthClient, row.client_id)
        if client is None or client.revoked:
            return None
        return f"{client.client_name} ({client.client_id[:24]})"


def www_authenticate(s: Settings, error: str | None = None) -> str:
    value = f'Bearer resource_metadata="{_issuer(s)}/.well-known/oauth-protected-resource", scope="{SCOPE}"'
    return value + (f', error="{error}"' if error else "")
