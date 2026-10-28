"""Transcribe and frame-sample downloaded Top Ads videos for the Checkpoint B creative database.

For each research/tiktok/ads/videos/<id>.mp4 writes research/tiktok/ads/analysis/<id>.json (transcript segments with
timestamps, first spoken words, scene cuts) and <id>_sheet.jpg (frames at 0, 0.5, 1, 1.5, 2, 3 s, then every ~2 s, each
labelled with its time). Transcription: faster-whisper base.en on CPU (English only; non-English speech is flagged).
Usage: python scripts/analyze_topads.py
"""
import json
from pathlib import Path

import subprocess

import cv2
import imageio_ffmpeg
import numpy as np
from faster_whisper import WhisperModel

HUB = Path(__file__).resolve().parent.parent
VIDEOS = HUB / "research" / "tiktok" / "ads" / "videos"
OUT = HUB / "research" / "tiktok" / "ads" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
EARLY = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
TILE_W, TILE_H = 180, 320


def scene_cuts(path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    # Calibrated 2026-10-25 on three ads checked by eye: a cut is a colour-histogram jump OR a large mean pixel change.
    prev, cuts, i = None, [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (64, 112))
        hist = cv2.calcHist([cv2.cvtColor(small, cv2.COLOR_BGR2HSV)], [0, 1], None, [16, 16], [0, 180, 0, 256])
        cv2.normalize(hist, hist)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            jump = cv2.compareHist(prev[0], hist, cv2.HISTCMP_BHATTACHARYYA) > 0.25 or float(np.abs(gray - prev[1]).mean()) > 30
            t = i / fps
            if jump and (not cuts or t - cuts[-1] > 0.3):
                cuts.append(round(t, 2))
        prev, i = (hist, gray), i + 1
    cap.release()
    return cuts, i / fps


def contact_sheet(path, duration, dest):
    times = EARLY + [round(t, 1) for t in np.arange(5.0, max(duration - 0.2, 5.0), 2.0)][:18]
    cap = cv2.VideoCapture(str(path))
    tiles = []
    for t in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        tile = cv2.resize(frame, (TILE_W, TILE_H))
        cv2.rectangle(tile, (0, 0), (60, 22), (0, 0, 0), -1)
        cv2.putText(tile, f"{t:.1f}s", (3, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        tiles.append(tile)
    cap.release()
    cols = 6
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    blank = np.zeros((TILE_H, TILE_W, 3), np.uint8)
    grid = np.vstack([np.hstack(r + [blank] * (cols - len(r))) for r in rows])
    cv2.imwrite(str(dest), grid, [cv2.IMWRITE_JPEG_QUALITY, 80])


def load_audio(path):
    # faster-whisper's own PyAV decoder breaks with the installed av version; decode with ffmpeg instead.
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-i", str(path), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=False).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def main():
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    for path in sorted(VIDEOS.glob("*.mp4")):
        vid = path.stem
        dest = OUT / f"{vid}.json"
        if dest.exists():
            continue
        cuts, duration = scene_cuts(path)
        contact_sheet(path, duration, OUT / f"{vid}_sheet.jpg")
        audio = load_audio(path)
        segments, info = model.transcribe(audio, beam_size=1, vad_filter=True) if audio.size else ([], None)
        segs = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                 "no_speech_prob": round(s.no_speech_prob, 2)} for s in segments]
        speech = [s for s in segs if s["no_speech_prob"] < 0.6]
        record = {
            "id": vid, "duration_s": round(duration, 2), "scene_cuts_s": cuts, "n_cuts": len(cuts),
            "cuts_per_10s": round(len(cuts) / duration * 10, 2) if duration else None,
            "first_speech_start_s": speech[0]["start"] if speech else None,
            "first_line": speech[0]["text"] if speech else None,
            "words_in_first_3s": " ".join(s["text"] for s in speech if s["start"] < 3.0),
            "speech_coverage_s": round(sum(s["end"] - s["start"] for s in speech), 1),
            "transcript": segs,
            "note": "base.en transcribes English only; garbled text likely means non-English speech or song lyrics",
        }
        dest.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{vid}: {duration:.1f}s, {len(cuts)} cuts, first line: {(record['first_line'] or '')[:60]}", flush=True)


if __name__ == "__main__":
    main()
