"""Paid-ads numbers for the dashboard's Ads section (Meta, TikTok), saved by the scheduled refresh task.

The scheduled task "ads-dashboard-refresh" reads each platform through Claude's ad connectors (read-only) and hands the
numbers to this script, one platform at a time, as a JSON file:
  {"platform": "meta" | "tiktok", "account": "...", "account_id": "...", "status": "ACTIVE",
   "active_campaigns": 0, "note": "",
   "days": [{"date": "YYYY-MM-DD", "spend": 0, "impressions": 0, "clicks": 0, "purchases": 0, "revenue": 0}]}
Rows for that platform and those dates replace the old ones; other platforms and older days are kept.

Optional (Phase E drill-down): "entities": the platform's own structure with totals for "entities_period"
(e.g. "last_7d"), one record per campaign, ad set / ad group / asset group, and ad:
  {"level": "campaign" | "adset" | "adgroup" | "ad", "id": "...", "parent_id": "..." (the level above),
   "name": "...", "status": "...", "delivery": "...", "objective": "...", "daily_budget": 0,
   "spend": 0, "impressions": 0, "clicks": 0, "purchases": 0, "revenue": 0, "url_tags": "..." (optional)}
Each platform's list replaces its previous list; every fetch is also kept in analytics.db (ad_entities).

Optional (full metrics, since 2026-10-29): "ad_days": every metric the platform reports, per ad per day, exactly as its
connector returned it (no retyping):
  TikTok: the "list" of report_integrated_get (data_level AUCTION_AD, dimensions ["ad_id", "stat_time_day"]), each
          {"dimensions": {"ad_id", "stat_time_day"}, "metrics": {...}} with ad_name, campaign_id, adgroup_id in metrics;
  Meta:   the ad_entities list of ads_get_ad_entities (level ad, time_increment "1"), each with id, name, campaign_id,
          adset_id, date_start and the metric fields.
Each row is kept whole in analytics.db (ad_metrics_daily.metrics) and mapped to one funnel shared by both platforms
(analytics.AD_FUNNEL, see FUNNEL_FIELDS); studio/dashboard/ads_funnel.json is rebuilt from the newest fetch of every
ad-day. Days are each ad account's own reporting day.

  python -I scripts/ads_snapshot.py merge <file.json>
  python -I scripts/ads_snapshot.py funnel        rebuild ads_funnel.json from analytics.db
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
FUNNEL = OUT / "ads_funnel.json"
# funnel step -> each platform's own field. Clicks are clicks to the store (TikTok "clicks" = destination clicks; Meta
# link clicks, not clicks (all)). Purchases and revenue are what the platform credits to its ads.
FUNNEL_FIELDS = {
    "tiktok": {"spend": "spend", "impressions": "impressions", "reach": "reach", "clicks": "clicks",
               "landing_page_views": "total_landing_page_view", "add_to_cart": "onsite_on_web_cart",
               "checkout": "checkout", "purchases": "complete_payment", "revenue": "total_purchase_value",
               "video_plays": "video_play_actions", "video_completes": "video_views_p100",
               "engaged_views": "engaged_view", "likes": "likes", "comments": "comments", "follows": "follows"},
    "meta": {"spend": "amount_spent", "impressions": "impressions", "reach": "reach", "clicks": "link_click",
             "landing_page_views": "landing_page_view", "add_to_cart": "omni_add_to_cart",
             "checkout": "omni_initiated_checkout", "purchases": "omni_purchase", "revenue": "omni_purchase_values",
             "video_plays": "video_play_actions", "video_completes": "video_p100_watched_actions",
             "engaged_views": "post_engagement", "likes": "post_reaction", "comments": "comment",
             "follows": "like"},  # Meta "like" = Page follows from the ads
}
PLATFORMS = ("meta", "tiktok")  # Microsoft removed 2026-10-28 (account suspended)
COLS = ["date", "platform", "spend", "impressions", "clicks", "purchases", "revenue"]
LEVELS = ("campaign", "adset", "adgroup", "ad")
ENTITY_FIELDS = ("level", "id", "parent_id", "name", "status", "delivery", "objective", "daily_budget", "url_tags")


def _num(x):
    try:
        return round(float(x or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def value(x):
    """A connector value as a number: '4.31', {'value': '4.31', 'unit': 'USD'}, '23.91%', a Meta results block
    ({'values': [{'value': '12'}]}) or 'Not available' / None (-> None)."""
    if isinstance(x, dict):
        x = x.get("value") if "value" in x else sum(value(v) or 0 for v in x.get("values") or [])
    if isinstance(x, str):
        x = x.strip().rstrip("%").replace(",", "")
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def ad_days(platform, raw):
    """The connector's per-ad-per-day rows -> [{date, id, name, campaign_id, group_id, metrics, funnel}]."""
    out = []
    for r in raw:
        if platform == "tiktok":
            dims, m = r.get("dimensions") or {}, dict(r.get("metrics") or {})
            day, ad, name = (dims.get("stat_time_day") or "")[:10], dims.get("ad_id"), m.get("ad_name")
            camp, group = m.get("campaign_id"), m.get("adgroup_id")
        else:
            m = {k: v for k, v in r.items() if k not in ("id", "name", "campaign_id", "adset_id", "date_start", "date_stop")}
            day, ad, name, camp, group = (r.get("date_start") or "")[:10], r.get("id"), r.get("name"), r.get("campaign_id"), r.get("adset_id")
        dt.date.fromisoformat(day)  # refuse a row without a proper day
        if not ad:
            raise SystemExit(f"{platform} row without an ad id: {r!r}"[:300])
        out.append({"date": day, "id": str(ad), "name": name or "", "campaign_id": str(camp or ""), "group_id": str(group or ""),
                    "metrics": m, "funnel": {k: value(m.get(f)) for k, f in FUNNEL_FIELDS[platform].items()}})
    return out


def write_funnel(path=None):
    """studio/dashboard/ads_funnel.json from the newest fetch of every ad-day in analytics.db."""
    rows = analytics.ad_funnel_rows(path)
    OUT.mkdir(parents=True, exist_ok=True)
    analytics.write_text_atomic(FUNNEL, json.dumps(rows, indent=1, ensure_ascii=False))
    return len(rows)


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
    if sys.argv[1:] == ["funnel"]:
        print(f"ads_funnel.json: {write_funnel()} ad-days")
        raise SystemExit(0)
    if len(sys.argv) != 3 or sys.argv[1] != "merge":
        raise SystemExit(__doc__)
    snap = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    ads = ad_days(snap.get("platform"), snap.get("ad_days") or []) if snap.get("platform") in PLATFORMS else []
    with analytics.job(f"ads:{snap.get('platform')}") as run:  # sync health + append-only history
        print(merge(snap) if snap.get("days") or "entities" in snap or not ads else f"{snap['platform']}: full metrics only")
        run["rows"] = analytics.record_ad_days(snap["platform"], snap.get("days") or [], "account",
                                               snap.get("account_id", ""))
        run["rows"] += analytics.record_ad_entities(snap["platform"], snap.get("entities") or [],
                                                    snap.get("entities_period", "last_7d"))
        if ads:
            run["rows"] += analytics.record_ad_metrics(snap["platform"], ads)
            print(f"{snap['platform']}: {len(ads)} ad-days of full metrics; ads_funnel.json {write_funnel()} ad-days")
        run["detail"] = snap.get("note", "")
