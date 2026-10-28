"""Make a labelled frame sheet for reviewing a generated ad: frames every 1.5 s, saved next to the video.

Usage: python scripts/review_frames.py <creative_id> [video_name]   (default video_name: tryon_raw.mp4)
"""
import sys
from pathlib import Path

import cv2
import numpy as np

HUB = Path(__file__).resolve().parent.parent
cid = sys.argv[1]
video = HUB / "assets" / cid / (sys.argv[2] if len(sys.argv) > 2 else "tryon_raw.mp4")
cap = cv2.VideoCapture(str(video))
duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 24)
tiles = []
for t in np.arange(0.0, duration, 1.5):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, frame = cap.read()
    if not ok:
        continue
    tile = cv2.resize(frame, (216, 384))
    cv2.rectangle(tile, (0, 0), (64, 24), (0, 0, 0), -1)
    cv2.putText(tile, f"{t:.1f}s", (4, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    tiles.append(tile)
cap.release()
cols = 5
blank = np.zeros_like(tiles[0])
rows = [tiles[i:i + cols] + [blank] * (cols - len(tiles[i:i + cols])) for i in range(0, len(tiles), cols)]
out = video.parent / "review_frames.jpg"
cv2.imwrite(str(out), np.vstack([np.hstack(r) for r in rows]), [cv2.IMWRITE_JPEG_QUALITY, 85])
print(f"{out} ({duration:.1f}s, {len(tiles)} frames)")
