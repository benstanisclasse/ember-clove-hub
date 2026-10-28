#!/usr/bin/env bash
# Prompt for a secret without echoing it and store it in .env.
#   scripts/set-secret.sh SHOPIFY_CLIENT_SECRET
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/lib.sh

key="${1:?usage: scripts/set-secret.sh KEY}"
[[ "$key" =~ ^[A-Z][A-Z0-9_]*$ ]] || { echo "invalid key: $key" >&2; exit 2; }

read -rsp "Paste ${key} (input is hidden), then press Enter: " value
echo
value="${value//[$'\r\n\t ']/}"
[[ -n "$value" ]] || { echo "nothing entered; .env unchanged" >&2; exit 1; }
[[ "$value" != *"|"* ]] || { echo "value contains '|'; set it with an editor instead" >&2; exit 1; }

env_set "$key" "$value"
echo "${key} saved to .env (${#value} characters)."
