"""Load a saved TikTok ad report into data/metrics.csv (one row per ad per day).

The report itself is pulled through Claude's TikTok connector (report_integrated_get with the
arguments in config/hub.json tiktok.daily_report_request) and saved as JSON in data/inbox/.

Usage:
  python metrics_sync.py data/inbox/tiktok_report_<date>.json
"""
import re
import sys

import hubdata as hd

# metrics.csv column -> TikTok metric names to try, in order.
FIELD_MAP = {
    "spend": ["spend"],
    "impressions": ["impressions"],
    "clicks": ["clicks"],
    "ctr": ["ctr"],
    "cpc": ["cpc"],
    "cpm": ["cpm"],
    "video_views": ["video_play_actions"],
    "views_2s": ["video_watched_2s"],
    "views_6s": ["video_watched_6s"],
    "avg_watch_s": ["average_video_play"],
    "add_to_cart": ["onsite_on_web_cart", "web_event_add_to_cart"],
    "checkouts": ["checkout", "initiate_checkout"],
    "purchases": ["complete_payment", "purchase"],
}
CREATIVE_ID = re.compile(r"EC-P\d+-A\d+-H\d+-V\d+")


def _first(metrics, names):
    for name in names:
        value = metrics.get(name)
        if value not in (None, "", "-"):
            return value
    return ""


def rows_from_report(report, platform="tiktok"):
    items = report.get("data", report).get("list", report.get("list", []))
    by_ad = {r["tiktok_ad_id"]: r["creative_id"] for r in hd.read("creatives") if r.get("tiktok_ad_id")}
    rows, unmatched = [], set()
    for item in items:
        dims, metrics = item.get("dimensions", {}), item.get("metrics", {})
        ad_id = str(dims.get("ad_id", ""))
        date = str(dims.get("stat_time_day", ""))[:10]
        creative_id = by_ad.get(ad_id, "")
        if not creative_id:
            match = CREATIVE_ID.search(metrics.get("ad_name", ""))
            creative_id = match.group(0) if match else ""
        if not creative_id:
            unmatched.add(ad_id)
        row = {"date": date, "platform": platform, "ad_id": ad_id, "creative_id": creative_id,
               "synced_at": hd.now()}
        for column, names in FIELD_MAP.items():
            row[column] = _first(metrics, names)
        roas = hd.num(metrics.get("complete_payment_roas"))
        spend = hd.num(row["spend"], 0.0)
        row["purchase_value"] = f"{roas * spend:.2f}" if roas is not None else ""
        rows.append(row)
    return rows, unmatched


def main(path):
    rows, unmatched = rows_from_report(hd.load_json(path))
    inserted, updated = hd.upsert("metrics", rows, ["date", "platform", "ad_id"])
    hd.log(f"Metrics sync from {path}: {inserted} new, {updated} updated rows")
    print(f"metrics.csv: {inserted} new, {updated} updated")
    if unmatched:
        print(f"WARNING: {len(unmatched)} ad(s) not linked to a creative: {', '.join(sorted(unmatched))}. "
              "Name ads with their creative ID or set tiktok_ad_id in creatives.csv.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
