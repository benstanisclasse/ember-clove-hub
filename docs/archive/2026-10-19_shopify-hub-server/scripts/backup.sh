#!/usr/bin/env bash
# Nightly backup (systemd timer 01:45, before the 02:30 Proxmox vzdump to the Synology):
#   1. pg_dump (custom format), validated with pg_restore --list
#   2. mirror the creatives bucket to plain files with rclone
#   3. prune local copies older than BACKUP_RETENTION_DAYS
#   4. optional offsite copy with restic (RESTIC_REPOSITORY set)
# Success/failure is recorded in job_runs; the watchdog alerts if backups go stale,
# and a failure posts to Slack immediately.
set -Eeuo pipefail
source "$(dirname "$0")/lib.sh"

DIR="$(env_get BACKUP_DIR)"; DIR="${DIR:-/var/backups/shopify-hub}"
KEEP="$(env_get BACKUP_RETENTION_DAYS)"; KEEP="${KEEP:-14}"
PGUSER="$(env_get POSTGRES_USER)"; PGUSER="${PGUSER:-hub}"
PGDB="$(env_get POSTGRES_DB)"; PGDB="${PGDB:-hub}"
BUCKET="$(env_get S3_BUCKET)"; BUCKET="${BUCKET:-hub-creatives}"
RCLONE_IMAGE="rclone/rclone:${RCLONE_VERSION:-1.71}"
RESTIC_IMAGE="restic/restic:${RESTIC_VERSION:-0.18.0}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
STEP="start"

on_fail() {
  local rc=$?
  trap - ERR
  local msg="Backup failed at step '$STEP' on $(hostname) (exit $rc)."
  warn "$msg"
  notify ":x: $msg"
  record_job backup failed --error "$msg"
  exit "$rc"
}
trap on_fail ERR

mkdir -p "$DIR/postgres" "$DIR/objects"

STEP="pg_dump"
dump="$DIR/postgres/hub-$STAMP.dump"
compose exec -T postgres pg_dump -U "$PGUSER" -d "$PGDB" -Fc --no-owner > "$dump.partial"
compose exec -T postgres pg_restore --list < "$dump.partial" > /dev/null   # fails on a corrupt dump
mv "$dump.partial" "$dump"
dump_mb=$(( $(stat -c %s "$dump") / 1048576 ))
log "postgres dump: $dump (${dump_mb} MB)"

STEP="objects"
if [[ "$(env_get STORAGE_PROVIDER)" == "garage" || -z "$(env_get STORAGE_PROVIDER)" ]]; then
  mkdir -p "$DIR/objects/$BUCKET"
  docker run --rm --network shopify-hub_backend --user "$(id -u):$(id -g)" \
    -e RCLONE_CONFIG_SRC_TYPE=s3 -e RCLONE_CONFIG_SRC_PROVIDER=Other \
    -e RCLONE_CONFIG_SRC_ENDPOINT="http://garage:3900" -e RCLONE_CONFIG_SRC_REGION=garage \
    -e RCLONE_CONFIG_SRC_FORCE_PATH_STYLE=true \
    -e RCLONE_CONFIG_SRC_ACCESS_KEY_ID="$(env_get S3_ACCESS_KEY_ID)" \
    -e RCLONE_CONFIG_SRC_SECRET_ACCESS_KEY="$(env_get S3_SECRET_ACCESS_KEY)" \
    -v "$DIR/objects:/data" "$RCLONE_IMAGE" \
    sync "src:$BUCKET" "/data/$BUCKET" --fast-list --quiet
  objects=$(find "$DIR/objects/$BUCKET" -type f | wc -l)
  log "object mirror: $objects files"
else
  objects=-1  # R2 / S3 are already durable offsite; nothing to mirror
  log "storage provider is $(env_get STORAGE_PROVIDER): skipping object mirror"
fi

STEP="prune"
find "$DIR/postgres" -name 'hub-*.dump' -mtime "+$KEEP" -delete
find "$DIR/postgres" -name '*.partial' -delete

STEP="offsite"
if [[ -n "$(env_get RESTIC_REPOSITORY)" ]]; then
  restic() {
    docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
      -e RESTIC_REPOSITORY="$(env_get RESTIC_REPOSITORY)" \
      -e RESTIC_PASSWORD="$(env_get RESTIC_PASSWORD)" \
      -e AWS_ACCESS_KEY_ID="$(env_get RESTIC_S3_ACCESS_KEY_ID)" \
      -e AWS_SECRET_ACCESS_KEY="$(env_get RESTIC_S3_SECRET_ACCESS_KEY)" \
      -e RESTIC_CACHE_DIR=/cache -v "$DIR/.restic-cache:/cache" \
      -v "$DIR:/data:ro" "$RESTIC_IMAGE" "$@"
  }
  mkdir -p "$DIR/.restic-cache"
  restic cat config >/dev/null 2>&1 || restic init
  restic backup /data --exclude /data/.restic-cache --tag nightly --quiet
  restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune --quiet
  log "offsite restic snapshot done"
fi

trap - ERR
record_job backup success --stats "{\"dump_mb\": $dump_mb, \"objects\": $objects}"
log "backup complete"
