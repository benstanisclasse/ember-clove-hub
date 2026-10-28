#!/usr/bin/env bash
# Deploy the hub's Shopify app config + web pixel extension with Shopify CLI, then connect
# the pixel to the store. Re-run after changing shopify-app/ (it's idempotent).
#
# Auth, pick one:
#   * SHOPIFY_CLI_PARTNERS_TOKEN in .env -> fully non-interactive (CI-style token)
#   * otherwise the CLI prints a login link + code once; open it and approve. The session
#     is kept in the docker volume "shopify-hub_shopify-cli" for next time.
set -euo pipefail
source "$(dirname "$0")/lib.sh"

CID="$(env_get SHOPIFY_CLIENT_ID)"
URL="$(env_get PUBLIC_BASE_URL)"
[[ -n "$CID" ]] || die "SHOPIFY_CLIENT_ID is empty -- create the Dev Dashboard app first (docs/shopify.md)"
[[ "$URL" == https://* ]] || die "PUBLIC_BASE_URL must be your public https URL (Cloudflare Tunnel)"

APP="$REPO/shopify-app"
sed -e "s|__CLIENT_ID__|$CID|g" -e "s|__PUBLIC_BASE_URL__|${URL%/}|g" \
  "$APP/shopify.app.toml.template" > "$APP/shopify.app.toml"
log "rendered shopify-app/shopify.app.toml for app $CID"

TTY=()
[[ -t 0 ]] && TTY=(-it)
TOKEN="$(env_get SHOPIFY_CLI_PARTNERS_TOKEN)"
log "deploying app config + web pixel extension (Shopify CLI)"
docker run --rm "${TTY[@]}" \
  -v "$APP:/app" -v shopify-hub_shopify-cli:/root/.config -w /app \
  -e SHOPIFY_CLI_PARTNERS_TOKEN="$TOKEN" -e SHOPIFY_FLAG_CLIENT_ID="$CID" \
  node:22-alpine sh -c "npm install --no-audit --no-fund --loglevel=error && npx -y @shopify/cli@3 app deploy --force"

# The CLI writes generated ids (extension uid) into the mounted folder as root.
docker run --rm -v "$APP:/app" alpine chown -R "$(id -u):$(id -g)" /app >/dev/null

log "connecting the web pixel to the store"
compose exec -T api python -m app.cli conversions activate-pixel
log "done -- check Shopify admin > Settings > Customer events: 'Store Hub' should show Connected"
