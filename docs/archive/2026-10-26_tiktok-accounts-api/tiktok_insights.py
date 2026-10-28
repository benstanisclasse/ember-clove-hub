"""Pull TikTok account + post analytics through the TikTok Accounts API (API for Business v1.3).

Usage:
    python tiktok_insights.py auth            # one-time: exchange the authorization code for tokens
    python tiktok_insights.py report          # fetch profile + all posts, write report files
    python tiktok_insights.py report --days 30

Needs tiktok_config.json next to this script (created as a template on first run).
Tokens are stored in tiktok_tokens.json and refreshed automatically.
Standard library only.
"""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "https://business-api.tiktok.com/open_api/v1.3"
HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "tiktok_config.json"
TOKENS_PATH = HERE / "tiktok_tokens.json"

PROFILE_FIELDS = [
    "is_business_account", "has_advanced_access", "profile_image", "username", "profile_deep_link",
    "display_name", "bio_description", "is_verified", "following_count", "followers_count",
    "total_likes", "videos_count", "video_views", "unique_video_views", "profile_views", "likes",
    "comments", "shares", "phone_number_clicks", "lead_submissions", "app_download_clicks",
    "bio_link_clicks", "email_clicks", "address_clicks", "daily_total_followers",
    "daily_new_followers", "daily_lost_followers", "audience_activity", "engaged_audience",
    "audience_ages", "audience_genders", "audience_countries", "audience_cities",
]
VIDEO_FIELDS = [
    "item_id", "create_time", "media_type", "is_ad", "caption", "share_url", "thumbnail_url",
    "video_duration", "video_views", "reach", "likes", "comments", "shares", "favorites",
    "total_time_watched", "average_time_watched", "full_video_watched_rate", "new_followers",
    "profile_views", "website_clicks", "phone_number_clicks", "lead_submissions",
    "app_download_clicks", "email_clicks", "address_clicks", "video_view_retention",
    "impression_sources", "audience_genders", "audience_countries", "audience_cities",
    "audience_types", "engagement_likes",
]
DAILY_COLUMNS = [
    "date", "followers_count", "daily_new_followers", "daily_lost_followers", "daily_total_followers",
    "video_views", "unique_video_views", "profile_views", "likes", "comments", "shares",
    "engaged_audience", "bio_link_clicks", "email_clicks", "phone_number_clicks", "address_clicks",
    "app_download_clicks", "lead_submissions",
]
# Breakdown fields come back as lists of objects; they go into the CSV as JSON text
NESTED_VIDEO_FIELDS = {
    "video_view_retention", "impression_sources", "audience_genders", "audience_countries",
    "audience_cities", "audience_types", "engagement_likes",
}

CONFIG_TEMPLATE = {
    "app_id": "PASTE_APP_ID",
    "app_secret": "PASTE_APP_SECRET",
    "redirect_uri": "PASTE_THE_REDIRECT_URL_SET_IN_YOUR_APP",
}


class ApiError(RuntimeError):
    pass


# ---------- HTTP ----------

def http(method, path, params=None, body=None, token=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(
            {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in params.items()})
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Access-Token"] = token
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as e:
        raise ApiError(f"HTTP {e.code} on {path}: {e.read().decode(errors='replace')[:500]}") from e
    if payload.get("code") != 0:
        raise ApiError(f"{path} failed (code {payload.get('code')}): {payload.get('message')} "
                       f"[request_id {payload.get('request_id')}]")
    return payload.get("data") or {}


# ---------- config + tokens ----------

def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(CONFIG_TEMPLATE, indent=2))
        sys.exit(f"Created {CONFIG_PATH.name}. Fill in app_id, app_secret and redirect_uri, then run again.")
    cfg = json.loads(CONFIG_PATH.read_text())
    missing = [k for k in CONFIG_TEMPLATE if not cfg.get(k) or cfg[k].startswith("PASTE_")]
    if missing:
        sys.exit(f"{CONFIG_PATH.name} is missing: {', '.join(missing)}")
    return cfg


def save_tokens(data):
    now = int(time.time())
    tokens = {
        "open_id": data["open_id"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "scope": data.get("scope", ""),
        "access_expires_at": now + int(data.get("expires_in", 86400)),
        "refresh_expires_at": now + int(data.get("refresh_token_expires_in", 31536000)),
    }
    TOKENS_PATH.write_text(json.dumps(tokens, indent=2))
    return tokens


def extract_code(text):
    text = text.strip()
    if "://" in text:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(text).query)
        for key in ("code", "auth_code"):
            if key in query:
                return query[key][0]
        sys.exit("No 'code' parameter found in that URL.")
    return text


def cmd_auth(_args):
    cfg = load_config()
    print("1. Open the TikTok account authorization URL from your developer app (My Apps > your app).")
    print("2. Sign in as the TikTok account you want analytics for and approve every permission.")
    print("3. You'll land on your redirect URL. Copy the whole address from the browser bar.")
    print("   The code is single-use and expires after 10 minutes.\n")
    code = extract_code(input("Paste the redirected URL (or just the code): "))
    data = http("POST", "/tt_user/oauth2/token/", body={
        "client_id": cfg["app_id"],
        "client_secret": cfg["app_secret"],
        "grant_type": "authorization_code",
        "auth_code": code,
        "redirect_uri": cfg["redirect_uri"],
    })
    tokens = save_tokens(data)
    print(f"\nAuthorized. Tokens saved to {TOKENS_PATH.name} (keep this file private).")
    print(f"Granted scopes: {tokens['scope']}")
    needed = {"user.info.basic", "user.info.username", "user.info.profile", "user.info.stats",
              "user.account.type", "user.insights", "video.list", "video.insights"}
    lacking = sorted(needed - set(tokens["scope"].split(",")))
    if lacking:
        print(f"Warning: these scopes were not granted, so some fields will fail: {', '.join(lacking)}")


def get_access_token():
    if not TOKENS_PATH.exists():
        sys.exit("No tokens yet. Run: python tiktok_insights.py auth")
    tokens = json.loads(TOKENS_PATH.read_text())
    if time.time() < tokens["access_expires_at"] - 300:
        return tokens
    if time.time() >= tokens["refresh_expires_at"]:
        sys.exit("Refresh token expired. Run: python tiktok_insights.py auth")
    cfg = load_config()
    data = http("POST", "/tt_user/oauth2/refresh_token/", body={
        "client_id": cfg["app_id"],
        "client_secret": cfg["app_secret"],
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
    })
    data.setdefault("open_id", tokens["open_id"])
    return save_tokens(data)


# ---------- fetching ----------

def fetch_profile(tokens, days):
    end = datetime.now(timezone.utc).date() - timedelta(days=1)
    start = end - timedelta(days=min(days, 60) - 1)
    return http("GET", "/business/get/", token=tokens["access_token"], params={
        "business_id": tokens["open_id"],
        "fields": PROFILE_FIELDS,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    })


def fetch_videos(tokens):
    videos, cursor = [], None
    while True:
        params = {"business_id": tokens["open_id"], "fields": VIDEO_FIELDS, "max_count": 20}
        if cursor:
            params["cursor"] = cursor
        data = http("GET", "/business/video/list/", token=tokens["access_token"], params=params)
        page = data.get("videos") or []
        videos.extend(page)
        if not data.get("has_more") or not page:
            return videos
        cursor = data.get("cursor")


# ---------- formatting ----------

def num(v):
    return v if isinstance(v, (int, float)) else 0


def pct(v):
    if not isinstance(v, (int, float)):
        return "—"
    return f"{v * 100:.1f}%" if v <= 1 else f"{v:.1f}%"


def breakdown(items, top=5):
    """Lists like [{"country": "US", "percentage": 0.4}] -> 'US 40.0%, ...'."""
    if not items:
        return "—"
    rows = []
    for it in items:
        label = next((str(v) for k, v in it.items() if k != "percentage" and not isinstance(v, (int, float))),
                     next((str(v) for k, v in it.items() if k != "percentage"), "?"))
        rows.append((label, it.get("percentage", 0)))
    rows.sort(key=lambda r: -num(r[1]))
    return ", ".join(f"{label} {pct(p)}" for label, p in rows[:top])


def posted(v):
    try:
        return datetime.fromtimestamp(int(v), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return ""


def write_outputs(profile, videos, out_dir, days):
    handle = profile.get("username") or "tiktok"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / f"{handle}-raw.json").write_text(
        json.dumps({"pulled_utc": stamp, "profile": profile, "videos": videos}, indent=2))

    daily = sorted(profile.get("metrics") or [], key=lambda m: m.get("date", ""))
    with open(out_dir / f"{handle}-daily.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=DAILY_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(daily)

    with open(out_dir / f"{handle}-posts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["posted_utc"] + VIDEO_FIELDS, extrasaction="ignore")
        w.writeheader()
        for v in videos:
            row = {k: json.dumps(v[k]) if k in NESTED_VIDEO_FIELDS and k in v else v.get(k, "") for k in VIDEO_FIELDS}
            row["posted_utc"] = posted(v.get("create_time"))
            w.writerow(row)

    def total(key):
        return sum(num(m.get(key)) for m in daily)

    md = [f"# {profile.get('display_name', handle)} (@{handle}) — TikTok analytics", "",
          f"Pulled {stamp} from the TikTok Accounts API. Daily figures cover the last {len(daily)} days "
          "available (TikTok keeps 60 days; the newest 1–2 days may still be filling in).", "",
          "## Profile", "", "| Field | Value |", "|---|---|"]
    for label, key in [("Followers", "followers_count"), ("Following", "following_count"),
                       ("Total likes", "total_likes"), ("Public videos", "videos_count"),
                       ("Bio", "bio_description"), ("Verified badge", "is_verified"),
                       ("Business account", "is_business_account"), ("Advanced access", "has_advanced_access"),
                       ("Profile link", "profile_deep_link")]:
        md.append(f"| {label} | {profile.get(key, '—')} |")

    md += ["", "## Followers' demographics", "",
           "TikTok only reports these once an account has 100+ followers.", "",
           "| Breakdown | Top values |", "|---|---|",
           f"| Age | {breakdown(profile.get('audience_ages'))} |",
           f"| Gender | {breakdown(profile.get('audience_genders'))} |",
           f"| Country | {breakdown(profile.get('audience_countries'))} |",
           f"| City | {breakdown(profile.get('audience_cities'))} |"]

    md += ["", f"## Last {len(daily)} days", "", "| Metric | Total |", "|---|---|"]
    for label, key in [("Video views", "video_views"), ("Unique viewers", "unique_video_views"),
                       ("Profile views", "profile_views"), ("Likes", "likes"), ("Comments", "comments"),
                       ("Shares", "shares"), ("Engaged viewers", "engaged_audience"),
                       ("New followers", "daily_new_followers"), ("Lost followers", "daily_lost_followers"),
                       ("Bio link clicks", "bio_link_clicks")]:
        md.append(f"| {label} | {total(key):,} |")
    md.append(f"\nDay-by-day numbers are in `{handle}-daily.csv`.")

    md += ["", f"## Posts ({len(videos)})", ""]
    if videos:
        md += ["| Posted | Views | Reach | Likes | Comments | Shares | Saves | Avg watch | Watched full | "
               "New followers | Top traffic source | Caption |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for v in sorted(videos, key=lambda v: -num(v.get("video_views"))):
            avg = v.get("average_time_watched")
            caption = (v.get("caption") or "").replace("|", "\\|").replace("\n", " ")
            caption = caption[:60] + "…" if len(caption) > 60 else caption
            link = f"[{caption or v.get('item_id')}]({v.get('share_url')})" if v.get("share_url") else caption
            md.append(
                f"| {posted(v.get('create_time'))[:10]} | {num(v.get('video_views')):,} | {num(v.get('reach')):,} | "
                f"{num(v.get('likes'))} | {num(v.get('comments'))} | {num(v.get('shares'))} | "
                f"{num(v.get('favorites'))} | {f'{avg:.1f}s' if isinstance(avg, (int, float)) else '—'} | "
                f"{pct(v.get('full_video_watched_rate'))} | {num(v.get('new_followers'))} | "
                f"{breakdown(v.get('impression_sources'), top=1)} | {link} |")
        md.append(f"\nEvery field per post (retention curve, traffic sources, viewer countries) is in `{handle}-posts.csv`.")
    else:
        md.append("No posts yet. Post at least one video and turn on Analytics in the TikTok app to start collecting data.")

    report = out_dir / f"{handle}-report.md"
    report.write_text("\n".join(md) + "\n", encoding="utf-8")
    return report


def cmd_report(args):
    tokens = get_access_token()
    profile = fetch_profile(tokens, args.days)
    videos = fetch_videos(tokens)
    report = write_outputs(profile, videos, Path(args.out), args.days)
    print(f"Wrote {report} ({len(videos)} posts, {len(profile.get('metrics') or [])} days of metrics)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("auth", help="exchange an authorization code for tokens").set_defaults(func=cmd_auth)
    rep = sub.add_parser("report", help="fetch analytics and write report files")
    rep.add_argument("--days", type=int, default=60, help="days of daily metrics, max 60 (default 60)")
    rep.add_argument("--out", default=str(HERE / "reports"), help="output folder (default ./reports)")
    rep.set_defaults(func=cmd_report)
    args = parser.parse_args()
    try:
        args.func(args)
    except ApiError as e:
        sys.exit(f"TikTok API error: {e}")


if __name__ == "__main__":
    main()
