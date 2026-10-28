"""Nightly backup of the Hub's records (owner approved 2026-10-27).

  backups/<YYYY-MM-DD>/      databases (consistent SQLite copies), data/ records, config/, studio/bible/, docs/, log.md
                             - one folder per day, the newest 14 kept
  backups/media_mirror/      paid or irreplaceable media (studio/episodes, studio/refs, data/media_generated,
                             data/media_originals): new or changed files are copied in, nothing is ever deleted

Code is versioned separately in the local git repository. Secrets are never copied (they live in user env vars).
Run: python -I scripts/backup_hub.py [--dest D:\\EmberClove-backups] [--keep 14]
Scheduled nightly by the Windows task "Ember Hub Nightly Backup".
"""
import argparse
import datetime as dt
import shutil
import sqlite3
import sys
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
DATABASES = ["studio/studio.db", "studio/analytics.db"]
RECORDS = ["data", "config", "studio/bible", "studio/dashboard", "docs", "log.md", "learnings.md"]
SKIP_IN_RECORDS = {"media_generated", "media_originals", "sizes", "__pycache__"}  # sizes = re-downloadable charts
MEDIA = ["studio/episodes", "studio/refs", "data/media_generated", "data/media_originals"]


def copy_db(src, dest):
    """SQLite's online backup: a consistent copy even while the dashboard is writing."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    s, d = sqlite3.connect(src), sqlite3.connect(dest)
    try:
        s.backup(d)
    finally:  # `with` on a sqlite3 connection only commits; close explicitly so Windows releases the file
        d.close()
        s.close()


def copy_tree(src, dest):
    if src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return 1
    n = 0
    for f in src.rglob("*"):
        if f.is_file() and not SKIP_IN_RECORDS.intersection(f.relative_to(src).parts):
            t = dest / f.relative_to(src)
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, t)
            n += 1
    return n


def mirror(src, dest):
    """Add new or changed files only; never delete from the mirror."""
    n = 0
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        t = dest / f.relative_to(src)
        if t.exists() and t.stat().st_size == f.stat().st_size and t.stat().st_mtime >= f.stat().st_mtime:
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, t)
        n += 1
    return n


def run(dest_root, keep):
    day = dest_root / dt.date.today().isoformat()
    tmp = dest_root / f".{day.name}.partial"
    if tmp.exists():
        shutil.rmtree(tmp)
    report = []
    for rel in DATABASES:
        if (HUB / rel).exists():
            copy_db(HUB / rel, tmp / rel)
            report.append(f"db {rel}")
    for rel in RECORDS:
        if (HUB / rel).exists():
            report.append(f"{rel}: {copy_tree(HUB / rel, tmp / rel)} files")
    if day.exists():
        shutil.rmtree(day)  # a second run on the same day replaces that day's snapshot
    tmp.rename(day)  # the day folder only appears once complete
    for rel in MEDIA:
        if (HUB / rel).exists():
            report.append(f"mirror {rel}: {mirror(HUB / rel, dest_root / 'media_mirror' / rel)} new/changed")
    days = sorted(p for p in dest_root.iterdir() if p.is_dir() and len(p.name) == 10 and p.name[4] == "-")
    for old in days[:-keep]:
        shutil.rmtree(old)
        report.append(f"removed old snapshot {old.name}")
    return day, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=str(HUB / "backups"))
    ap.add_argument("--keep", type=int, default=14)
    a = ap.parse_args()
    day, report = run(Path(a.dest), a.keep)
    print(f"Backup {day}:")
    for line in report:
        print("  " + line)


if __name__ == "__main__":
    sys.exit(main())
