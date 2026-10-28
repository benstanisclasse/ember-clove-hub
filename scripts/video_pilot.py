"""Video hook and script extraction pipeline (research/kalodata/VIDEO_EXTRACTION_DESIGN_2026-10-25.md).

Pairs: for a product, its best-selling video (the winner) and a typical video of the SAME product and month that got
distributed but stalled (the comparison). Same product and month means the difference is the video, not the product.
Within a product sales per view are roughly constant, so winners win on reach: the question is what earns views.
Per video: MP4 from the public TikTok link (owner's decision 2026-10-26; Kalodata's signed URL, 0.5 credits, as the
backup for winners) -> faster-whisper transcript (hook = words in the first 3 s) -> cut detection (OpenCV) -> frame sheet (0, 1, 2, 3 s, then every 3 s) -> a vision model on OpenRouter
fills a fixed tag form from the frame sheet and transcript -> one row in kalodata.db table video_features.
Videos are used for analysis only: never reposted or copied.
Run: OPENROUTER_API_KEY must be set (secrets.openrouter_api).
  python scripts/video_pilot.py --max-credits 6                  # the 5-pair pilot
  python scripts/video_pilot.py --scope all --max-credits 30     # every product with a full video list (~100 pairs)
"""
import argparse
import base64
import datetime as dt
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
import pandas as pd
import requests
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hub_env  # noqa: E402
import kalodata as k  # noqa: E402
import kalodata_db  # noqa: E402

VIDEOS = k.OUT / "videos"
FF = imageio_ffmpeg.get_ffmpeg_exe()
TAG_MODEL = "anthropic/claude-haiku-5.5"  # more accurate than Gemini Flash Lite in the pilot
BACKUP_MODELS = ["google/gemini-3.1-flash-lite", "google/gemini-2.5-flash-lite"]
PILOT_PRODUCTS = {  # one product per category, from the September full video lists
    "Womenswear & Underwear": "1732029147740410054", "Menswear & Underwear": "1729410057349075371",
    "Shoes": "1729412819500634176", "Health": "1731846112092393716", "Tools & Hardware": "1732550857886830764"}
FORM = {
    "hook_type": "the main hook in the first 3 s (spoken or on-screen), one of: question (asks the viewer something), "
                 "problem_pain (names a problem or who it's for, e.g. 'if you have X'), bold_claim (a strong statement "
                 "about the product), you_need_to_see_this (tells viewers to look or not scroll), before_after (old way vs "
                 "new way), demonstration (shows the product working, little or no words), humour_skit (joke or acted "
                 "scene), offer_discount (price, deal or urgency), trend_sound (relies on a trending sound or meme), none",
    "first_frame": "what fills the 0s tile: face, product_alone, person_with_product (wearing, holding or using it), "
                   "text_card, scene_without_product, other",
    "on_screen_text_first_3s": "exact on-screen text in the 0-3s tiles, or empty",
    "format": "one of: try_on (puts on or wears clothing/shoes to show fit), demo (shows a product working), "
              "talking_review (person talks about it, little action), unboxing, before_after, styling (outfit ideas, "
              "several pieces), lifestyle (product in daily life, no direct pitch), slideshow (still images), "
              "skit, other",
    "presenter": "one of: on_camera_speaking, on_camera_silent, voice_over_only, no_person",
    "presenter_looks_ai_generated": "true/false",
    "product_first_seen_s": "seconds until the product is first clearly visible (number)",
    "product_shown_as_0s": "in the 0s tile: worn, held, in_use, flat_or_packshot, not_shown",
    "detail_closeups": "true/false: close-ups of fabric, texture or a feature",
    "script_beats": "ordered list from: problem, product_intro, feature, proof_demo, social_proof, offer, cta",
    "claims": "list of claims made (comfort, quality, sizing, results, price_discount, urgency, other)",
    "cta": "one of: spoken, on_screen, both, none",
    "cta_text": "the call-to-action wording, or empty",
    "setting": "one of: home, studio, outdoors, store, car, gym, other",
    "production": "one of: phone_ugc, polished",
    "summary": "one sentence describing the video",
}


def products(con, scope):
    if scope == "pilot":
        return list(PILOT_PRODUCTS.items())
    cats = dict(con.execute("SELECT c.category_id, c.category_name FROM categories c JOIN pulls u ON c.pull_id = "
                            "u.pull_id WHERE u.name LIKE 'core_categories_l1_last365Day%'").fetchall())
    names = [r[0] for r in con.execute("SELECT DISTINCT name FROM pulls WHERE name LIKE 'core_allvideos_%'")]
    pairs = sorted({(n.split("_")[3], n.split("_")[4]) for n in names})
    return [(cats.get(c, c), pid) for c, pid in pairs]


def pick_pairs(con, scope="pilot"):
    v = pd.read_sql("SELECT DISTINCT v.video_id, v.product_filter AS pid, v.belonged_creator_handle AS handle, "
                    "v.revenue, v.views, v.ai_video, v.ad, v.video_title FROM videos v JOIN pulls u ON v.pull_id = "
                    "u.pull_id WHERE u.name LIKE 'core_allvideos_%'", con).drop_duplicates("video_id")
    for c in ("revenue", "views"):
        v[c] = pd.to_numeric(v[c], errors="coerce").fillna(0)
    v["per1k"] = v["revenue"] / v["views"].clip(lower=1) * 1000
    pairs = []
    for cat, pid in products(con, scope):
        d = v[(v["pid"] == pid) & (v["views"] >= 5000)]
        if not len(d):
            continue
        wins = [r for _, r in d.sort_values("revenue", ascending=False).head(3).iterrows()]  # backups if one fails
        win = wins[0]
        # Within a product, sales per view are roughly constant: winners win on reach. So the comparison is a typical
        # video of the same product that got distributed but stalled: >= 500 views, <= 10% of the winner's views,
        # nearest the product's median views among those.
        allv = v[(v["pid"] == pid) & (v["video_id"] != win["video_id"])]
        c = allv[(allv["views"] >= 500) & (allv["views"] <= 0.1 * win["views"])]
        if not len(c):
            print(f"  {cat}: no comparison video found, skipped")
            continue
        med = np.log(allv["views"].clip(lower=1)).median()
        flops = [c.iloc[i] for i in (np.log(c["views"]) - med).abs().argsort().iloc[:4]]  # backups if one won't download
        print(f"  pair {cat}: winner ${win['revenue']:,.0f} / {win['views']:,.0f} views; comparison "
              f"${flops[0]['revenue']:,.0f} / {flops[0]['views']:,.0f} views", flush=True)
        pairs.append((cat, pid, wins, flops))
    return pairs


def download(vid, budget):
    out = VIDEOS / vid / "video.mp4"
    if out.exists() and out.stat().st_size > 10000:
        return out
    k.RAW = k.OUT / "raw" / "pilot_videos"
    data = k.call("tiktok/video/url", {"video_id": vid}, f"url_{vid}", budget, 0.5)
    if not data or not data.get("video_url"):
        return None
    r = requests.get(data["video_url"], timeout=120)
    if not r.ok:  # Kalodata may not hold a copy of every video (seen with low-view videos)
        print(f"  {vid}: video file refused (HTTP {r.status_code})")
        return None
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(r.content)
    return out


def download_link(vid, handle):
    """Low-view comparison videos: Kalodata doesn't hold them, so fetch from the public TikTok link (owner's decision,
    2026-10-26). Small, slow and for analysis only."""
    out = VIDEOS / vid / "video.mp4"
    if out.exists() and out.stat().st_size > 10000:
        return out
    import yt_dlp
    out.parent.mkdir(parents=True, exist_ok=True)
    opts = {"outtmpl": str(out), "format": "best[ext=mp4]/best", "quiet": True, "no_warnings": True, "noprogress": True,
            "overwrites": True, "retries": 2, "sleep_interval": 5}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([f"https://www.tiktok.com/@{handle}/video/{vid}"])
    except Exception as e:  # deleted, private, or blocked
        print(f"  {vid}: link download failed ({type(e).__name__})")
        return None
    time.sleep(5)
    return out if out.exists() and out.stat().st_size > 10000 else None


def has_picture(path):
    r = subprocess.run([FF, "-i", str(path)], capture_output=True, text=True).stderr
    return "Video:" in r


def transcribe(path, model):
    # Decode with ffmpeg ourselves: the installed PyAV is newer than faster-whisper's own decoder expects.
    raw = subprocess.run([FF, "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    segs, info = model.transcribe(audio, language="en", word_timestamps=True, vad_filter=True)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in (s.words or [])]
    return words, info.duration


def structure(path, words, duration):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    prev, cuts, i = None, [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % 2 == 0:  # every other frame is plenty for cut detection
            hsv = cv2.cvtColor(cv2.resize(frame, (160, 284)), cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
            cv2.normalize(hist, hist)
            if prev is not None and cv2.compareHist(prev, hist, cv2.HISTCMP_BHATTACHARYYA) > 0.3:
                t = i / fps
                if not cuts or t - cuts[-1] > 0.4:
                    cuts.append(round(t, 2))
            prev = hist
        i += 1
    cap.release()
    spoken = sum(w["e"] - w["s"] for w in words)
    return {"duration_s": round(duration, 1), "cuts": len(cuts), "cut_times": cuts,
            "cuts_per_10s": round(len(cuts) / max(duration, 1) * 10, 2), "words": len(words),
            "words_per_s": round(len(words) / max(duration, 1), 2), "speech_share": round(spoken / max(duration, 1), 2),
            "hook_text": " ".join(w["w"] for w in words if w["s"] < 3.0)}


def frame_sheet(path, duration, out):
    times = [0, 1, 2, 3] + [t for t in np.arange(6, min(duration, 45), 3)][:8]
    tiles = []
    for t in times:
        tmp = out.parent / f"_f{t}.jpg"
        subprocess.run([FF, "-y", "-loglevel", "quiet", "-ss", str(t), "-i", str(path), "-frames:v", "1",
                        "-vf", "scale=-2:420", str(tmp)], check=False)  # an unreadable frame is skipped, not fatal
        if tmp.exists() and tmp.stat().st_size > 0:
            im = Image.open(tmp).convert("RGB")
            ImageDraw.Draw(im).rectangle([0, 0, 60, 22], fill="black")
            ImageDraw.Draw(im).text((5, 4), f"{t:.0f}s", fill="yellow")
            tiles.append(im)
        tmp.unlink(missing_ok=True)
    if not tiles:
        raise RuntimeError("no frames could be read")
    w, h = tiles[0].size
    cols = 6
    sheet = Image.new("RGB", (w * cols, h * ((len(tiles) + cols - 1) // cols)), "black")
    for i, im in enumerate(tiles):
        sheet.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
    sheet.save(out, quality=82)
    return [float(t) for t in times[:len(tiles)]]


def tag(sheet, words, meta, model=None):
    transcript = " ".join(f"[{w['s']:.1f}] {w['w']}" for w in words) or "(no speech detected)"
    speech = meta.get("speech_share", 1)
    note = ("Speech covers only {:.0%} of the video: the transcript may be song lyrics, not the presenter. Only tag "
            "a presenter as speaking if a person is visible and clearly talking.".format(speech) if speech < 0.3 else "")
    prompt = ("You are tagging a TikTok Shop product video for marketing research. The image is a contact sheet of "
              "frames; each tile is labelled with its time in seconds (0s, 1s, 2s, 3s, then every 3 s). The timed "
              f"transcript follows. Product category: {meta['category']}. Caption: {meta['caption']!r}. {note}\n"
              "Judge 'first_frame' and 'product_shown_as_0s' from the 0s tile itself: a garment held up or laid flat "
              "is not 'worn'. If no person is visible, presenter is 'no_person' or 'voice_over_only'.\n\n"
              f"TRANSCRIPT:\n{transcript[:6000]}\n\nReturn ONLY a JSON object with exactly these keys:\n"
              + json.dumps(FORM, indent=1) + "\nBase every answer on what is visible or said; use empty or 'other' "
              "when unsure.")
    img = base64.b64encode(sheet.read_bytes()).decode()
    first = model or TAG_MODEL
    body = {"model": first, "models": [first] + [m for m in BACKUP_MODELS if m != first], "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}]}]}
    for attempt in range(4):  # rate limits: wait and retry; OpenRouter falls back to the backup models in order
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", timeout=120, json=body,
                          headers={"Authorization": f"Bearer {hub_env.get_secret('openrouter_api')}"})
        if r.status_code != 429:
            break
        time.sleep(20 * (attempt + 1))
    r.raise_for_status()
    out = r.json()
    text = out["choices"][0]["message"]["content"].strip().removeprefix("```json").removesuffix("```")
    return json.loads(text), (out.get("usage") or {}).get("cost")


def store(con, row):
    con.execute("""CREATE TABLE IF NOT EXISTS video_features (video_id TEXT PRIMARY KEY, product_id TEXT, category TEXT,
        role TEXT, pair TEXT, revenue REAL, views REAL, ai_video INTEGER, ad INTEGER, duration_s REAL, cuts INTEGER,
        cuts_per_10s REAL, words INTEGER, words_per_s REAL, speech_share REAL, hook_text TEXT, transcript TEXT,
        tags_json TEXT, tag_model TEXT, created_at TEXT)""")
    con.execute("INSERT OR REPLACE INTO video_features VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
    con.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-credits", type=float, required=True)
    ap.add_argument("--whisper", default="small")
    ap.add_argument("--scope", choices=["pilot", "all"], default="pilot")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    from faster_whisper import WhisperModel
    budget = k.Budget(args.max_credits)
    con = sqlite3.connect(kalodata_db.DB)
    pairs = pick_pairs(con, args.scope)
    print(f"{len(pairs)} pairs", flush=True)
    model = WhisperModel(args.whisper, device="cpu", compute_type="int8", cpu_threads=8)
    tag_cost = 0.0
    for cat, pid, wins, flops in pairs:
        for role, options in (("winner", wins), ("comparison", flops)):
            path = None
            for v in options:
                vid = v["video_id"]
                path = download_link(vid, v["handle"])  # links first; Kalodata only as a winner's backup
                if path is None and role == "winner":
                    path = download(vid, budget)
                if path is not None and not has_picture(path):  # slideshow or audio-only post: no visuals
                    print(f"  {vid}: no picture in the file, skipped")
                    path = None
                if path is not None:
                    break
            if path is None:
                print(f"  {cat} {role}: no downloadable video")
                continue
            if con.execute("SELECT name FROM sqlite_master WHERE name = 'video_features'").fetchone() and \
                    con.execute("SELECT 1 FROM video_features WHERE video_id = ?", (vid,)).fetchone():
                print(f"  {cat} | {role} | already processed")
                continue
            try:  # one broken video shouldn't stop the run
                words, duration = transcribe(path, model)
                st = structure(path, words, duration)
                sheet = VIDEOS / vid / "sheet.jpg"
                frame_sheet(path, duration, sheet)
                tags, cost = tag(sheet, words, {"category": cat, "caption": v["video_title"],
                                                "speech_share": st["speech_share"]})
            except Exception as e:
                print(f"  {cat} | {role} | {vid}: skipped ({type(e).__name__}: {str(e)[:80]})", flush=True)
                continue
            tag_cost += cost or 0
            (VIDEOS / vid / "transcript.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
            (VIDEOS / vid / "tags.json").write_text(json.dumps({**st, **tags}, indent=1, ensure_ascii=False),
                                                    encoding="utf-8")
            store(con, (vid, pid, cat, role, f"{pid}", float(v["revenue"]), float(v["views"]), int(v["ai_video"] or 0),
                        int(v["ad"] or 0), st["duration_s"], st["cuts"], st["cuts_per_10s"], st["words"],
                        st["words_per_s"], st["speech_share"], st["hook_text"], " ".join(w["w"] for w in words),
                        json.dumps(tags, ensure_ascii=False), TAG_MODEL, dt.datetime.now().isoformat(timespec="seconds")))
            print(f"  {cat} | {role} | ${v['revenue']:,.0f} on {v['views']:,.0f} views | {st['duration_s']}s, "
                  f"{st['cuts']} cuts | hook: {st['hook_text'][:70]!r} | {tags.get('hook_type')} / {tags.get('format')}",
                  flush=True)
    print(f"Done: {budget.spent:.1f} Kalodata credits charged, tagging ${tag_cost:.4f}")


if __name__ == "__main__":
    main()
