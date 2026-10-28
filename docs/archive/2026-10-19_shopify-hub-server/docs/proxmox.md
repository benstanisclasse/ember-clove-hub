# Proxmox VM

## What's running now

| | |
|---|---|
| Host | `proxmax` (192.168.1.100), cluster `BSNet` |
| VM | **210 `shopify-hub`**, Ubuntu 24.04 LTS cloud image |
| Sizing | 4 vCPU (`host`), 6 GB RAM (balloon min 4 GB), 60 GB disk on `local-lvm` (NVMe, discard/SSD/iothread) |
| Network | `vmbr0`, static **192.168.1.210/24**, gateway 192.168.1.254, DNS 192.168.1.202 then 1.1.1.1 |
| Boot | `onboot=1`, QEMU guest agent enabled |
| Login | `ssh hub@192.168.1.210` (key-only; cloud-init user `hub`, passwordless sudo) |
| Backups | nightly vzdump job 02:30 to `Synology` (keep 7 daily / 4 weekly) + the existing weekly all-guests job |
| Repo | `/home/hub/shopify-hub` |

Room for the VM came from stopping LXC 135 `minecraft-paper` and turning off its autostart.
To bring it back: `pct set 135 --onboot 1 && pct start 135`. It needs about 7 GB, so give the hub VM less memory first.

### Host issues spotted (not changed)

* **proxmax's own default gateway is 192.168.1.1, which doesn't respond**, so the host has
  no internet: no `apt` updates, and no downloads from the Proxmox UI. Proxmox2 uses
  192.168.1.254, which works. Fix it in the UI (*proxmax > System > Network > vmbr0 > Gateway*) or in
  `/etc/network/interfaces`, then `ifreload -a`.
* `local-lvm` on proxmax is **thin-provisioned past its size** (about 338 GiB of virtual disks in a
  pool of about 338 GiB, currently 44% used). That's fine until the disks actually fill. Watch `lvs`, and set
  `thin_pool_autoextend_threshold` or move a large guest elsewhere if usage climbs past ~80%.
* proxmax was using 7.5 of 8 GB swap before Minecraft was stopped. That will drain over time; to
  clear it immediately, run `swapoff -a && swapon -a` on the host when RAM is free.

## Rebuilding the VM from scratch

Run on a Proxmox node that has internet access (Proxmox2 does; proxmax doesn't, see above).

```bash
# 1. Image (verify the checksum)
cd /var/lib/vz/template/iso
U=https://cloud-images.ubuntu.com/noble/current
curl -fsSLO $U/noble-server-cloudimg-amd64.img && curl -fsSL $U/SHA256SUMS | grep '\*noble-server-cloudimg-amd64.img$' | sed 's/\*//' | sha256sum -c -

# 2. VM
qm create 210 --name shopify-hub --memory 6144 --balloon 4096 --cores 4 --cpu host \
  --ostype l26 --machine q35 --scsihw virtio-scsi-single --net0 virtio,bridge=vmbr0 \
  --agent enabled=1,fstrim_cloned_disks=1 --onboot 1 --serial0 socket --vga serial0
qm set 210 --scsi0 local-lvm:0,import-from=/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img,discard=on,ssd=1,iothread=1
qm set 210 --ide2 local-lvm:cloudinit --boot order=scsi0
qm resize 210 scsi0 60G
qm set 210 --ciuser hub --sshkeys ~/hub.pub \
  --ipconfig0 ip=192.168.1.210/24,gw=192.168.1.254 --nameserver "192.168.1.202 1.1.1.1"
qm start 210

# 3. Nightly backup job to the Synology
pvesh create /cluster/backup --schedule 02:30 --vmid 210 --storage Synology --mode snapshot \
  --compress zstd --prune-backups keep-daily=7,keep-weekly=4 --mailnotification failure
```

Then, inside the VM:

```bash
sudo timedatectl set-timezone America/New_York
git clone <repo> ~/shopify-hub && cd ~/shopify-hub
scripts/setup.sh        # installs Docker, then asks you to log out/in once, then re-run it
```

**Why a VM and not an LXC:** Docker inside an unprivileged LXC needs nesting/keyctl
workarounds and breaks on some kernel updates. A VM gives the stack its own kernel and makes
vzdump snapshots consistent through the guest agent's fs-freeze.

**Sizing guidance:** 4 GB RAM is enough while the hub just syncs data. Go to 8 GB before Phase 7
(LightGBM training) or if Postgres grows past a few GB. Disk: plan for Postgres plus the creatives
bucket. Videos are the big item (~5–20 MB each).
