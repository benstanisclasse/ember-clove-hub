#!/usr/bin/env bash
# Deploy / update: git pull, build, migrate, restart, verify.
#   scripts/deploy.sh            # normal update
#   scripts/deploy.sh --no-pull  # deploy the working tree as-is (used by setup.sh)
set -euo pipefail
source "$(dirname "$0")/lib.sh"

[[ -f "$ENV_FILE" ]] || die ".env missing -- run scripts/setup.sh first"
env_merge_example
[[ -n "$(env_get HIGGSFIELD_WEBHOOK_TOKEN)" ]] || env_set HIGGSFIELD_WEBHOOK_TOKEN "$(rand_hex 24)"
[[ -n "$(env_get MCP_BEARER_TOKEN)" ]] || env_set MCP_BEARER_TOKEN "$(rand_hex 32)"
[[ -n "$(env_get MCP_OWNER_PASSWORD)" ]] || env_set MCP_OWNER_PASSWORD "$(rand_hex 12)"

if [[ "${1:-}" != "--no-pull" ]] && git remote get-url origin >/dev/null 2>&1; then
  log "pulling latest code"
  git pull --ff-only
fi

log "building image"
compose build --pull api

log "running database migrations"
compose run --rm api alembic upgrade head

log "starting stack"
compose up -d --remove-orphans

# Caddy's config is a bind mount: compose won't restart it when only the file changes,
# and its admin API is off (no hot reload), so restart it when the Caddyfile hash changes.
STATE="$REPO/.deploy-state"
caddy_hash="$(sha256sum "$REPO/deploy/Caddyfile" | cut -d' ' -f1)"
if [[ "$(cat "$STATE/caddyfile.sha256" 2>/dev/null)" != "$caddy_hash" ]]; then
  log "Caddyfile changed: restarting caddy"
  compose restart caddy >/dev/null
  mkdir -p "$STATE" && echo "$caddy_hash" > "$STATE/caddyfile.sha256"
fi

log "ensuring storage bucket"
compose exec -T api python -m app.cli storage init

log "waiting for readiness"
for _ in $(seq 1 30); do
  if compose exec -T api python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health/ready', timeout=3).status==200 else 1)" 2>/dev/null; then
    log "deploy OK ($(git rev-parse --short HEAD 2>/dev/null || echo 'no git'))"
    docker image prune -f >/dev/null
    exit 0
  fi
  sleep 3
done
compose ps
notify "Deploy finished but the API is not ready -- check \`docker compose logs api\` on $(hostname)."
die "API did not become ready"
