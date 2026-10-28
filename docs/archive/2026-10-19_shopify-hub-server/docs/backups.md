# Backups and restore

Three layers, each covering a different failure:

| Layer | When | What | Where | Protects against |
|---|---|---|---|---|
| `scripts/backup.sh` | daily 01:45 (VM time, America/New_York) | `pg_dump -Fc` (checked with `pg_restore --list`) + rclone mirror of the creatives bucket | `/var/backups/shopify-hub` in the VM | bad migration, accidental delete, corrupted DB |
| Proxmox vzdump | daily 02:30 (host) + weekly all-guests job Sat 03:00 | the whole VM, snapshot mode with guest-agent fs-freeze | `Synology` (192.168.1.84, share `Vault`) | VM disk loss, host failure, botched upgrade |
| restic (optional) | after each backup.sh run | `/var/backups/shopify-hub` | offsite S3 (Backblaze B2 / Cloudflare R2) | house fire / theft / ransomware hitting the LAN |

The vzdump runs 45 minutes after the in-VM dump, so every VM image on the Synology already contains a
fresh, consistent `pg_dump`.

Retention: local dumps 14 days (`BACKUP_RETENTION_DAYS`); vzdump 7 daily + 4 weekly; restic
7 daily / 4 weekly / 6 monthly.

## Monitoring

* `backup.sh` and `restore-test.sh` record each run in `job_runs`. The watchdog alerts Slack if the last
  successful backup is more than 26 h old, or the last restore test more than 8 days old.
* Any failure posts to Slack immediately, naming the step that failed.
* vzdump failures email root on the Proxmox host (`mailnotification failure`).

## Turning on the offsite copy

1. Create a bucket plus an application key limited to that bucket (B2 or R2).
2. In `.env`:
   ```
   RESTIC_REPOSITORY=s3:https://s3.us-west-004.backblazeb2.com/<bucket>/shopify-hub
   RESTIC_PASSWORD=<long random -- store it in Vaultwarden; without it the backups are unreadable>
   RESTIC_S3_ACCESS_KEY_ID=...
   RESTIC_S3_SECRET_ACCESS_KEY=...
   ```
3. `scripts/backup.sh`: the first run initializes the repository.

## Restore test (automatic, weekly)

`scripts/restore-test.sh` runs every Sunday at 04:00. It restores the newest dump into a throwaway
Postgres container, then checks:
* `alembic_version` matches live,
* each core table's restored row count is no greater than live,
* the profit views can be queried.

It never touches the live database. Run it by hand any time: `scripts/restore-test.sh`.

## Restore procedures

**A. Roll back the database to last night** (VM is fine, data is bad):
```bash
cd ~/shopify-hub
source scripts/lib.sh
compose stop api worker scheduler
DUMP=$(ls -1t /var/backups/shopify-hub/postgres/hub-*.dump | head -1); echo "$DUMP"
compose exec -T postgres dropdb -U hub hub
compose exec -T postgres createdb -U hub hub
compose exec -T postgres pg_restore -U hub -d hub --no-owner < "$DUMP"
scripts/deploy.sh --no-pull   # applies any newer migrations, restarts, checks health
```

**B. Restore creatives** (bucket lost or emptied):
```bash
source scripts/lib.sh
docker run --rm --network shopify-hub_backend \
  -e RCLONE_CONFIG_DST_TYPE=s3 -e RCLONE_CONFIG_DST_PROVIDER=Other \
  -e RCLONE_CONFIG_DST_ENDPOINT=http://garage:3900 -e RCLONE_CONFIG_DST_REGION=garage \
  -e RCLONE_CONFIG_DST_FORCE_PATH_STYLE=true \
  -e RCLONE_CONFIG_DST_ACCESS_KEY_ID="$(env_get S3_ACCESS_KEY_ID)" \
  -e RCLONE_CONFIG_DST_SECRET_ACCESS_KEY="$(env_get S3_SECRET_ACCESS_KEY)" \
  -v /var/backups/shopify-hub/objects:/data:ro rclone/rclone:1.71 \
  copy /data/hub-creatives dst:hub-creatives
```

**C. Whole VM** (disk dead, host rebuilt): Proxmox UI > *Synology* storage > *Backups* > pick the
newest `vzdump-qemu-210-*` > **Restore** (to any node with room). Or from the shell:
`qmrestore /mnt/pve/backupS/.../vzdump-qemu-210-<date>.vma.zst 210 --storage local-lvm`.
The stack comes up on its own at boot. Then run `scripts/restore-test.sh` and `python -m app.cli health`.

**D. Offsite only** (LAN gone): build a new VM (see `docs/proxmox.md`), clone the repo, run
`scripts/setup.sh`, then:
`docker run --rm -e RESTIC_REPOSITORY=... -e RESTIC_PASSWORD=... -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -v /var/backups/shopify-hub:/restore restic/restic:0.18.0 restore latest --target /restore`,
then run procedures A and B.

Test procedure C at least once: restore the VM backup to a spare VM ID with the network unplugged
(`--unique 1`, and remove `net0` before starting it), and check that it boots and `app.cli health` passes.
