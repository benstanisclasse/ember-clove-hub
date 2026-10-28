import builtins, io, json, sys, time, tempfile, urllib.parse
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import tiktok_insights as ti

tmp = Path(tempfile.mkdtemp())
ti.CONFIG_PATH = tmp / "tiktok_config.json"
ti.TOKENS_PATH = tmp / "tiktok_tokens.json"
calls = []

# 1) first run creates template and exits
try:
    ti.load_config()
except SystemExit as e:
    print("template:", e, ti.CONFIG_PATH.exists())
ti.CONFIG_PATH.write_text(json.dumps({"app_id": "A", "app_secret": "S", "redirect_uri": "https://x.test/cb"}))


def fake_http(method, path, params=None, body=None, token=None):
    calls.append((method, path, params, body, token))
    if path == "/tt_user/oauth2/token/":
        assert body["auth_code"] == "CODE123", body
        return {"access_token": "AT1", "refresh_token": "RT1", "open_id": "OID", "expires_in": 86400,
                "refresh_token_expires_in": 31536000, "scope": "user.info.basic,video.list"}
    if path == "/tt_user/oauth2/refresh_token/":
        return {"access_token": "AT2", "refresh_token": "RT2", "expires_in": 86400,
                "refresh_token_expires_in": 31536000, "scope": "x"}
    if path == "/business/get/":
        assert token == "AT2" and params["business_id"] == "OID"
        return {"username": "emberandclove", "display_name": "Ember & Clove", "followers_count": 120,
                "following_count": 3, "total_likes": 900, "videos_count": 21, "is_verified": False,
                "audience_countries": [{"country": "US", "percentage": 0.62}, {"country": "CA", "percentage": 0.1}],
                "audience_genders": [{"gender": "Female", "percentage": 0.8}, {"gender": "Male", "percentage": 0.2}],
                "audience_ages": [], "audience_cities": [],
                "metrics": [{"date": "2026-10-24", "video_views": 100, "likes": 5, "daily_new_followers": 2,
                             "audience_activity": [{"hour": "1", "count": 2}]},
                            {"date": "2026-10-23", "video_views": 50, "likes": 1, "daily_new_followers": 1}]}
    if path == "/business/video/list/":
        if "cursor" not in params:
            vids = [{"item_id": str(i), "create_time": str(1792900000 + i), "caption": f"post {i} | test",
                     "share_url": f"https://t/{i}", "video_views": i * 10, "likes": i, "average_time_watched": 4.25,
                     "full_video_watched_rate": 0.31,
                     "impression_sources": [{"impression_source": "For You", "percentage": 0.9},
                                            {"impression_source": "Search", "percentage": 0.1}]} for i in range(20)]
            return {"videos": vids, "has_more": True, "cursor": 1792899999000}
        return {"videos": [{"item_id": "99", "create_time": "1792800000", "caption": "last", "video_views": 7}],
                "has_more": False, "cursor": 0}
    raise AssertionError(path)


ti.http = fake_http

# 2) auth with a pasted redirect URL
builtins.input = lambda _: "https://x.test/cb?code=CODE123&state=abc"
ti.cmd_auth(None)

# 3) force expiry so report has to refresh
t = json.loads(ti.TOKENS_PATH.read_text())
t["access_expires_at"] = int(time.time()) - 10
ti.TOKENS_PATH.write_text(json.dumps(t))


class A: days = 60; out = str(tmp / "reports")


ti.cmd_report(A)
print("paths:", [c[1] for c in calls])
print("refreshed token:", json.loads(ti.TOKENS_PATH.read_text())["access_token"])
fields_param = [c[2] for c in calls if c[1] == "/business/get/"][0]
print("dates:", fields_param["start_date"], fields_param["end_date"])
print("url fields encoded:", urllib.parse.urlencode({"fields": json.dumps(fields_param["fields"][:2])}))
print(sorted(p.name for p in (tmp / "reports").iterdir()))
print((tmp / "reports" / "emberandclove-report.md").read_text(encoding="utf-8")[:2600])
print((tmp / "reports" / "emberandclove-posts.csv").read_text(encoding="utf-8").splitlines()[1][:300])
