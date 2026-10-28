#!/usr/bin/env bash
# Weekly restore test (systemd timer, Sun 04:00): restore the newest dump into a
# throwaway Postgres, then check the schema version and row counts against live.
# Never touches the live database.
set -Eeuo pipefail
source "$(dirname "$0")/lib.sh"

DIR="$(env_get BACKUP_DIR)"; DIR="${DIR:-/var/backups/shopify-hub}"
PGUSER="$(env_get POSTGRES_USER)"; PGUSER="${PGUSER:-hub}"
PGDB="$(env_get POSTGRES_DB)"; PGDB="${PGDB:-hub}"
NAME="hub-restore-test"
TABLES=(settings products orders order_items customers ads ad_metrics_daily creatives actions_log)

cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
on_fail() {
  trap - ERR
  local msg="Restore test FAILED on $(hostname): $1"
  warn "$msg"; notify ":x: $msg"; record_job restore_test failed --error "$msg"; cleanup; exit 1
}
trap cleanup EXIT

latest="$(ls -1t "$DIR"/postgres/hub-*.dump 2>/dev/null | head -1 || true)"
[[ -n "$latest" ]] || on_fail "no dump found in $DIR/postgres"
log "restoring $(basename "$latest")"

cleanup
docker run -d --name "$NAME" -e POSTGRES_USER=restore -e POSTGRES_PASSWORD="$(rand_hex 16)" \
  -e POSTGRES_DB=restore postgres:17-alpine >/dev/null
for _ in $(seq 1 30); do docker exec "$NAME" pg_isready -U restore -q 2>/dev/null && break; sleep 1; done
sleep 2  # the image restarts postgres once after init

docker exec -i "$NAME" pg_restore -U restore -d restore --no-owner --exit-on-error < "$latest" \
  || on_fail "pg_restore returned an error"

q_restored() { docker exec "$NAME" psql -U restore -d restore -tAc "$1"; }
q_live() { compose exec -T postgres psql -U "$PGUSER" -d "$PGDB" -tAc "$1"; }

rv="$(q_restored 'SELECT version_num FROM alembic_version')"
lv="$(q_live 'SELECT version_num FROM alembic_version')"
[[ "$rv" == "$lv" ]] || on_fail "schema version differs (restored=$rv live=$lv)"

report="schema $rv"
for t in "${TABLES[@]}"; do
  r="$(q_restored "SELECT count(*) FROM $t")"; l="$(q_live "SELECT count(*) FROM $t")"
  # Live keeps growing after the dump, so restored may be lower -- but never higher.
  (( r <= l )) || on_fail "$t has more rows restored ($r) than live ($l)"
  report+=", $t $r/$l"
done
[[ "$(q_restored 'SELECT count(*) FROM v_order_profit')" =~ ^[0-9]+$ ]] || on_fail "profit view unusable"

trap - EXIT; cleanup
log "restore test OK: $report"
record_job restore_test success --stats "{\"dump\": \"$(basename "$latest")\"}"
notify ":white_check_mark: Weekly restore test OK ($(basename "$latest")): $report"
