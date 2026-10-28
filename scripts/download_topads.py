"""Download Top Ads videos listed in research/tiktok/ads/video_urls_<date>.tsv (id<TAB>url) for frame/transcript analysis.

Owner approved 2026-10-25. Files go to research/tiktok/ads/videos/<id>.mp4. Signed URLs expire after a few hours.
Usage: python scripts/download_topads.py research/tiktok/ads/video_urls_2026-10-25.tsv
"""
import sys
import urllib.request
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
src = HUB / sys.argv[1]
out = HUB / "research" / "tiktok" / "ads" / "videos"
out.mkdir(parents=True, exist_ok=True)
ok = failed = 0
total = 0
for line in src.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    vid, url = line.split("\t", 1)
    dest = out / f"{vid}.mp4"
    if dest.exists() and dest.stat().st_size > 10_000:
        ok += 1
        total += dest.stat().st_size
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://ads.tiktok.com/"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        dest.write_bytes(data)
        ok += 1
        total += len(data)
    except Exception as e:  # noqa: BLE001
        failed += 1
        print(f"FAIL {vid}: {e}")
print(f"downloaded {ok}, failed {failed}, total {total / 1e6:.0f} MB")
