"""Paid-ads numbers for the dashboard's Ads section (Meta, TikTok, Microsoft), saved by the scheduled refresh task.

The scheduled task "ads-dashboard-refresh" reads each platform through Claude's ad connectors (read-only) and hands the
numbers to this script, one platform at a time, as a JSON file:
  {"platform": "meta" | "tiktok" | "microsoft", "account": "...", "account_id": "...", "status": "ACTIVE",
   "active_campaigns": 0, "note": "",
   "days": [{"date": "YYYY-MM-DD", "spend": 0, "impressions": 0, "clicks": 0, "purchases": 0, "revenue": 0}]}
Rows for that platform and those dates replace the old ones; other platforms and older days are kept.

  python -I scripts/ads_snapshot.py merge <file.json>
Writes studio/dashboard/ads_daily.csv (one row per platform per day) and ads_accounts.json (one row per platform).
"""
import csv
import datetime as dt
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "studio" / "dashboard"
DAILY, ACCOUNTS = OUT / "ads_daily.csv", OUT / "ads_accounts.json"
PLATFORMS = ("meta", "tiktok", "microsoft")
COLS = ["date", "platform", "spend", "impressions", "clicks", "purchases", "revenue"]


def _num(x):
    try:
        return round(float(x or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def merge(snap):
    platform = snap["platform"]
    if platform not in PLATFORMS:
        raise SystemExit(f"platform must be one of {', '.join(PLATFORMS)}")
    days = {d["date"]: d for d in snap.get("days") or []}
    for day in days:
        dt.date.fromisoformat(day)  # refuse malformed dates before touching the file
    rows = []
    if DAILY.exists():
        with open(DAILY, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if not (r["platform"] == platform and r["date"] in days)]
    rows += [{"date": day, "platform": platform, **{k: _num(d.get(k)) for k in COLS[2:]}} for day, d in days.items()]
    rows.sort(key=lambda r: (r["date"], r["platform"]))
    OUT.mkdir(parents=True, exist_ok=True)
    with open(DAILY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    accounts = {a["platform"]: a for a in (json.loads(ACCOUNTS.read_text(encoding="utf-8")) if ACCOUNTS.exists() else [])}
    accounts[platform] = {"platform": platform, "account": snap.get("account", ""), "account_id": str(snap.get("account_id", "")),
                          "status": snap.get("status", ""), "active_campaigns": int(snap.get("active_campaigns") or 0),
                          "note": snap.get("note", ""), "refreshed_at": dt.datetime.now().isoformat(timespec="minutes")}
    ACCOUNTS.write_text(json.dumps([accounts[p] for p in PLATFORMS if p in accounts], indent=1), encoding="utf-8")
    return f"{platform}: {len(days)} days saved, {len(rows)} rows in ads_daily.csv"


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "merge":
        raise SystemExit(__doc__)
    print(merge(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))))
