#!/usr/bin/env bash
# Idempotent Garage bootstrap: render config, assign the single-node layout, create the
# bucket and an access key, and write the key into .env (S3_ACCESS_KEY_ID / SECRET).
set -euo pipefail
source "$(dirname "$0")/lib.sh"

CONF="$REPO/deploy/garage/garage.toml"
BUCKET="$(env_get S3_BUCKET)"; BUCKET="${BUCKET:-hub-creatives}"
KEY_NAME="hub-app"
CAPACITY="${GARAGE_CAPACITY:-40G}"

g() { docker compose exec -T garage /garage "$@"; }

if [[ ! -f "$CONF" ]]; then
  log "rendering $CONF"
  sed -e "s|__RPC_SECRET__|$(env_get GARAGE_RPC_SECRET)|" \
      -e "s|__ADMIN_TOKEN__|$(env_get GARAGE_ADMIN_TOKEN)|" \
      -e "s|__METRICS_TOKEN__|$(env_get GARAGE_METRICS_TOKEN)|" \
      "$REPO/deploy/garage/garage.toml.template" > "$CONF"
  chmod 600 "$CONF"
fi

log "starting garage"
docker compose up -d garage >/dev/null
for _ in $(seq 1 30); do g status >/dev/null 2>&1 && break; sleep 2; done
g status >/dev/null || die "garage did not become ready"

if g status | grep -q "NO ROLE ASSIGNED"; then
  node="$(g node id -q 2>/dev/null | cut -d@ -f1)"
  [[ -n "$node" ]] || die "could not read garage node id"
  log "assigning layout (capacity $CAPACITY) to node ${node:0:16}..."
  g layout assign -z dc1 -c "$CAPACITY" "$node" >/dev/null
  version="$(g layout show | grep -oE -- '--version [0-9]+' | tail -1 | awk '{print $2}')"
  g layout apply --version "${version:-1}" >/dev/null
fi

g bucket info "$BUCKET" >/dev/null 2>&1 || { log "creating bucket $BUCKET"; g bucket create "$BUCKET" >/dev/null; }

if [[ -z "$(env_get S3_ACCESS_KEY_ID)" || -z "$(env_get S3_SECRET_ACCESS_KEY)" ]]; then
  if ! g key info "$KEY_NAME" >/dev/null 2>&1; then
    log "creating access key $KEY_NAME"
    g key create "$KEY_NAME" >/dev/null
  fi
  info="$(g key info "$KEY_NAME" --show-secret)"
  key_id="$(grep -oE 'GK[0-9a-f]+' <<<"$info" | head -1)"
  secret="$(grep -iE 'secret key' <<<"$info" | grep -oE '[0-9a-f]{64}' | head -1)"
  [[ -n "$key_id" && -n "$secret" ]] || die "could not parse garage key output"
  env_set S3_ACCESS_KEY_ID "$key_id"
  env_set S3_SECRET_ACCESS_KEY "$secret"
  log "wrote S3 credentials for $KEY_NAME to .env"
fi

g bucket allow --read --write --owner "$BUCKET" --key "$KEY_NAME" >/dev/null
log "garage ready: bucket=$BUCKET key=$KEY_NAME"
