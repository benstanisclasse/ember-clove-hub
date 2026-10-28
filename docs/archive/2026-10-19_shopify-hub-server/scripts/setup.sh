#!/usr/bin/env bash
# One-time, idempotent bootstrap of the hub on a fresh Ubuntu 24.04 VM.
# Run from the repo as the user that will own the stack (needs sudo):
#   git clone <repo> ~/shopify-hub && cd ~/shopify-hub && scripts/setup.sh
# Safe to re-run: existing secrets, Garage keys and data are kept.
set -euo pipefail
source "$(dirname "$0")/lib.sh"

USER_NAME="$(id -un)"

# --- 1. OS packages + Docker -------------------------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
  log "installing Docker Engine + compose plugin"
  export DEBIAN_FRONTEND=noninteractive
  sudo -E apt-get update -qq
  sudo -E apt-get install -y -qq ca-certificates curl git jq openssl qemu-guest-agent unattended-upgrades
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo -E apt-get update -qq
  sudo -E apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER_NAME"
  die "Docker installed. Log out and back in (docker group), then re-run scripts/setup.sh"
fi
sudo systemctl enable --now docker qemu-guest-agent >/dev/null 2>&1 || true

# --- 2. .env with generated secrets ------------------------------------------------------
if [[ ! -f "$ENV_FILE" ]]; then
  log "creating .env from .env.example"
  cp .env.example "$ENV_FILE"
fi
chmod 600 "$ENV_FILE"
env_default POSTGRES_PASSWORD "$(rand_hex 24)"
env_default ADMIN_TOKEN "$(rand_hex 32)"
env_default GARAGE_RPC_SECRET "$(rand_hex 32)"
env_default GARAGE_ADMIN_TOKEN "$(rand_hex 32)"
env_default GARAGE_METRICS_TOKEN "$(rand_hex 32)"
env_default HIGGSFIELD_WEBHOOK_TOKEN "$(rand_hex 24)"
env_default MCP_BEARER_TOKEN "$(rand_hex 32)"
env_default MCP_OWNER_PASSWORD "$(rand_hex 12)"

# --- 3. Object storage ---------------------------------------------------------------------
if [[ "$(env_get STORAGE_PROVIDER)" == "garage" ]]; then
  "$REPO/scripts/garage-init.sh"
fi

# --- 4. Backup directory --------------------------------------------------------------------
BACKUP_DIR="$(env_get BACKUP_DIR)"; BACKUP_DIR="${BACKUP_DIR:-/var/backups/shopify-hub}"
sudo mkdir -p "$BACKUP_DIR"
sudo chown "$USER_NAME:$USER_NAME" "$BACKUP_DIR"
sudo chmod 700 "$BACKUP_DIR"

# --- 5. Build, migrate, start ---------------------------------------------------------------
"$REPO/scripts/deploy.sh" --no-pull

# --- 6. systemd: start on boot, nightly backup, weekly restore test --------------------------
log "installing systemd units"
for unit in "$REPO"/deploy/systemd/*; do
  sed -e "s|__REPO__|$REPO|g" -e "s|__USER__|$USER_NAME|g" "$unit" \
    | sudo tee "/etc/systemd/system/$(basename "$unit")" >/dev/null
done
sudo systemctl daemon-reload
sudo systemctl enable shopify-hub.service shopify-hub-backup.timer shopify-hub-restore-test.timer >/dev/null
sudo systemctl start shopify-hub-backup.timer shopify-hub-restore-test.timer

# --- 7. First backup + restore test so monitoring starts green -------------------------------
log "running first backup and restore test"
"$REPO/scripts/backup.sh"
"$REPO/scripts/restore-test.sh"

log "setup complete"
log "  admin/health (LAN): http://$(env_get ADMIN_BIND_ADDR):8081/health/ready"
log "  next: add CLOUDFLARE_TUNNEL_TOKEN, SLACK_WEBHOOK_URL, HEARTBEAT_URL to .env, then scripts/deploy.sh"
