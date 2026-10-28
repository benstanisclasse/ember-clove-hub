"""Nightly backup of the Hub's records (owner approved 2026-10-27).

  backups/<YYYY-MM-DD>/      databases (consistent SQLite copies), data/ records, config/, studio/bible/, docs/, log.md
                             - one folder per day, the newest 14 kept
  backups/media_mirror/      paid or irreplaceable media (studio/episodes, studio/refs, data/media_generated,
                             data/media_originals): new or changed files are copied in, nothing is ever deleted
  backups/research_mirror/   research/ (paid Kalodata raw responses, models, reports, audits) the same way, minus
                             databases and third-party video files
  backups/research_db/       kalodata_<date>.db: a consistent copy of the market database whenever it changed since
                             the newest copy, the newest 4 kept (it is ~400 MB, so not copied into every day folder)

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
RESEARCH = "research"
RESEARCH_SKIP = {".db", ".db-journal", ".db-wal", ".db-shm", ".mp4", ".mov", ".webm", ".mp3", ".wav"}
RESEARCH_DB = "research/kalodata/kalodata.db"
RESEARCH_DB_KEEP = 4


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


def mirror(src, dest, skip_suffixes=()):
    """Add new or changed files only; never delete from the mirror."""
    n = 0
    for f in src.rglob("*"):
        if not f.is_file() or f.suffix.lower() in skip_suffixes:
            continue
        t = dest / f.relative_to(src)
        if t.exists() and t.stat().st_size == f.stat().st_size and t.stat().st_mtime >= f.stat().st_mtime:
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, t)
        n += 1
    return n


def backup_research_db(src, dest_dir, keep=RESEARCH_DB_KEEP):
    """Copy the market database only when it changed since the newest copy; keep the newest `keep` copies."""
    copies = sorted(dest_dir.glob("kalodata_*.db")) if dest_dir.exists() else []
    if copies and copies[-1].stat().st_mtime >= src.stat().st_mtime:
        return "unchanged since " + copies[-1].name
    target = dest_dir / f"kalodata_{dt.date.today().isoformat()}.db"
    tmp = dest_dir / (target.name + ".partial")
    copy_db(src, tmp)
    tmp.replace(target)
    copies = sorted(dest_dir.glob("kalodata_*.db"))
    for old in copies[:-keep]:
        old.unlink()
    return "copied " + target.name


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
    if (HUB / RESEARCH).exists():
        n = mirror(HUB / RESEARCH, dest_root / "research_mirror", RESEARCH_SKIP)
        report.append(f"mirror {RESEARCH}: {n} new/changed")
    if (HUB / RESEARCH_DB).exists():
        report.append(f"research db: {backup_research_db(HUB / RESEARCH_DB, dest_root / 'research_db')}")
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
