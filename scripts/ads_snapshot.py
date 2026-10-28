"""Paid-ads numbers for the dashboard's Ads section (Meta, TikTok, Microsoft), saved by the scheduled refresh task.

The scheduled task "ads-dashboard-refresh" reads each platform through Claude's ad connectors (read-only) and hands the
numbers to this script, one platform at a time, as a JSON file:
  {"platform": "meta" | "tiktok" | "microsoft", "account": "...", "account_id": "...", "status": "ACTIVE",
   "active_campaigns": 0, "note": "",
   "days": [{"date": "YYYY-MM-DD", "spend": 0, "impressions": 0, "clicks": 0, "purchases": 0, "revenue": 0}]}
Rows for that platform and those dates replace the old ones; other platforms and older days are kept.

Optional (Phase E drill-down): "entities": the platform's own structure with totals for "entities_period"
(e.g. "last_7d"), one record per campaign, ad set / ad group / asset group, and ad:
  {"level": "campaign" | "adset" | "adgroup" | "asset_group" | "ad", "id": "...", "parent_id": "..." (the level above),
   "name": "...", "status": "...", "delivery": "...", "objective": "...", "daily_budget": 0,
   "spend": 0, "impressions": 0, "clicks": 0, "purchases": 0, "revenue": 0, "url_tags": "..." (optional)}
Each platform's list replaces its previous list; every fetch is also kept in analytics.db (ad_entities).

  python -I scripts/ads_snapshot.py merge <file.json>
Writes studio/dashboard/ads_daily.csv (one row per platform per day), ads_accounts.json (one row per platform) and
ads_entities.json (drill-down), and appends the same days to studio/analytics.db (ad_daily, kept per fetch) with a
sync_runs row "ads:<platform>".
"""
import csv
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from studio import analytics  # noqa: E402

OUT =Path(__file__).resolve().parent.parent / "studio" / "dashboard"
DAILY, ACCOUNTS, ENTITIES = OUT / "ads_daily.csv", OUT / "ads_accounts.json", OUT / "ads_entities.json"
PLATFORMS = ("meta", "tiktok", "microsoft")
COLS = ["date", "platform", "spend", "impressions", "clicks", "purchases", "revenue"]
LEVELS = ("campaign", "adset", "adgroup", "asset_group", "ad")
ENTITY_FIELDS = ("level", "id", "parent_id", "name", "status", "delivery", "objective", "daily_budget", "url_tags")


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
    with analytics.atomic_open(DAILY, newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    accounts = {a["platform"]: a for a in (json.loads(ACCOUNTS.read_text(encoding="utf-8")) if ACCOUNTS.exists() else [])}
    accounts[platform] = {"platform": platform, "account": snap.get("account", ""), "account_id": str(snap.get("account_id", "")),
                          "status": snap.get("status", ""), "active_campaigns": int(snap.get("active_campaigns") or 0),
                          "note": snap.get("note", ""), "refreshed_at": dt.datetime.now().isoformat(timespec="minutes")}
    analytics.write_text_atomic(ACCOUNTS, json.dumps([accounts[p] for p in PLATFORMS if p in accounts], indent=1))
    msg = f"{platform}: {len(days)} days saved, {len(rows)} rows in ads_daily.csv"
    if "entities" in snap:
        msg += f"; {merge_entities(platform, snap['entities'], snap.get('entities_period', 'last_7d'))} entities"
    return msg


def merge_entities(platform, entities, period):
    """Replace this platform's drill-down list in ads_entities.json (other platforms are kept)."""
    for e in entities:
        if e.get("level") not in LEVELS or not e.get("id"):
            raise SystemExit(f"bad entity {e!r}: level must be one of {', '.join(LEVELS)} and id is required")
    fetched = dt.datetime.now().isoformat(timespec="minutes")
    keep = [e for e in (json.loads(ENTITIES.read_text(encoding="utf-8")) if ENTITIES.exists() else [])
            if e.get("platform") != platform]
    new = [{"platform": platform, **{k: e.get(k) for k in ENTITY_FIELDS}, "id": str(e["id"]),
            "parent_id": str(e.get("parent_id") or ""), **{k: _num(e.get(k)) for k in COLS[2:]},
            "period": period, "refreshed_at": fetched} for e in entities]
    analytics.write_text_atomic(ENTITIES, json.dumps(keep + new, indent=1, ensure_ascii=False))
    return len(new)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "merge":
        raise SystemExit(__doc__)
    snap = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    with analytics.job(f"ads:{snap.get('platform')}") as run:  # sync health + append-only history
        print(merge(snap))
        run["rows"] = analytics.record_ad_days(snap["platform"], snap.get("days") or [], "account",
                                               snap.get("account_id", ""))
        run["rows"] += analytics.record_ad_entities(snap["platform"], snap.get("entities") or [],
                                                    snap.get("entities_period", "last_7d"))
        run["detail"] = snap.get("note", "")
