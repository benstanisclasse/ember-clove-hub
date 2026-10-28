#!/usr/bin/env bash
# Shared helpers for the hub's operator scripts. Source it; don't run it.

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO/.env"
cd "$REPO"

log()  { printf '\033[1;34m[hub]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[hub]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[hub]\033[0m %s\n' "$*" >&2; exit 1; }

# Read one KEY from .env without sourcing the whole file into the environment.
env_get() {
  [[ -f "$ENV_FILE" ]] || return 0
  grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2-
}

# Set KEY=value in .env (replaces an existing line, else appends).
env_set() {
  local key="$1" value="$2"
  if grep -qE "^${key}=" "$ENV_FILE"; then
    # | as sed delimiter: values are hex/base64url, never contain it
    sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
  fi
}

# Set KEY only if it is currently empty or missing.
env_default() {
  [[ -n "$(env_get "$1")" ]] || env_set "$1" "$2"
}

# Append keys that exist in .env.example but not yet in .env (new settings after an update).
env_merge_example() {
  local added=0 line key
  while IFS= read -r line; do
    [[ "$line" =~ ^([A-Z][A-Z0-9_]*)= ]] || continue
    key="${BASH_REMATCH[1]}"
    if ! grep -qE "^${key}=" "$ENV_FILE"; then
      printf '%s\n' "$line" >> "$ENV_FILE"; added=$((added + 1))
    fi
  done < "$REPO/.env.example"
  (( added == 0 )) || log "added $added new setting(s) to .env from .env.example"
}

rand_hex() { openssl rand -hex "${1:-32}"; }

compose() {
  local profiles=()
  [[ -n "$(env_get CLOUDFLARE_TUNNEL_TOKEN)" ]] && profiles=(--profile tunnel)
  docker compose "${profiles[@]}" "$@"
}

# Post to Slack if configured (never prints the webhook URL).
notify() {
  local url; url="$(env_get SLACK_WEBHOOK_URL)"
  [[ -n "$url" ]] || return 0
  local text; text="$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  curl -fsS -m 10 -H 'Content-Type: application/json' -d "{\"text\":\"$text\"}" "$url" >/dev/null || warn "slack notify failed"
}

# Record an external job outcome in job_runs (watched by the watchdog).
record_job() {
  local name="$1" status="$2"; shift 2
  compose exec -T api python -m app.cli jobs record "$name" "$status" "$@" >/dev/null 2>&1 \
    || warn "could not record $name=$status in job_runs"
}
