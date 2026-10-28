"""FastAPI application: ``uvicorn app.main:app``.

Route groups and who can reach them (enforced by Caddy, see ``deploy/Caddyfile``):

* ``/healthz``                     -- public liveness, no details
* ``/webhooks/*``, ``/oauth/*``    -- public (Phase 2-3), each verifies its own signature
* ``/mcp``                         -- public (Phase 5), bearer/OAuth protected
* ``/health/ready``, ``/admin/*``  -- LAN only, and ``/admin`` also needs ``ADMIN_TOKEN``
"""

from __future__ import annotations

import hmac
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import business_settings
from app.collect import router as collect_router
from app.config import get_settings
from app.db import get_session
from app.health import readiness
from app.log import configure_logging, get_logger
from app.mcpserver.oauth import router as oauth_router
from app.mcpserver.server import mcp_app, mcp_lifespan
from app.queue import get_redis
from app.webhooks import router as webhooks_router

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    log.info("api_starting", env=settings.app_env)
    async with mcp_lifespan():
        yield


app = FastAPI(
    title="Shopify hub",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if get_settings().app_env == "prod" else "/docs",
    redoc_url=None,
)


app.include_router(webhooks_router)
app.include_router(collect_router)
app.include_router(oauth_router)


def require_admin(authorization: Annotated[str | None, Header()] = None) -> None:
    """Bearer-token guard for /admin routes (defence in depth behind the LAN-only route)."""
    expected = get_settings().admin_token.get_secret_value()
    if not expected:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "ADMIN_TOKEN is not configured")
    supplied = (authorization or "").removeprefix("Bearer ").strip()
    if not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid admin token")


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict[str, str]:
    """Liveness: the process is up. Safe to expose publicly (no details)."""
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready() -> JSONResponse:
    """Readiness: database, Redis and object storage reachable."""
    results = readiness(get_redis())
    ok = all(r.ok for r in results)
    return JSONResponse(
        status_code=200 if ok else 503,
        content={"status": "ok" if ok else "degraded", "checks": [r.as_dict() for r in results]},
    )


@app.get("/admin/settings", dependencies=[Depends(require_admin)])
def admin_settings(session: Annotated[Session, Depends(get_session)]) -> dict[str, Any]:
    """Current runtime business settings."""
    s = business_settings.load(session)
    return {**s.model_dump(mode="json"), "writes_allowed": s.writes_allowed}


# Must stay last: the MCP app (behind its own bearer auth) is the fallback for /mcp.
app.mount("/", mcp_app)
