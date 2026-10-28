"""Tag background music in the video-study videos and compare winners with their stalled comparison videos.

Per video (research/kalodata/videos/<id>/video.mp4 + transcript.json):
  - AST audio classifier (MIT/ast-finetuned-audioset-10-10-0.4593, AudioSet labels), run locally on 5 s windows:
    music_share = share of windows where "Music" scores >= MUSIC_P; also mean Music / Singing / Speech scores.
  - Loudness from the waveform: speech_db = median RMS while words are spoken (transcript timings), gap_db = median
    RMS in pauses >= 0.3 s; gap_rel_db = gap_db - speech_db (near 0 = something as loud as the voice fills the gaps).
  - music_level: none | quiet bed | clear | music-led (little speech, mostly music).
Writes table video_audio in research/kalodata/kalodata.db and prints the paired winner-vs-stalled comparison.

Run: python scripts/video_audio.py [--limit N] [--report-only]
"""
import argparse
import json
import math
import sqlite3
import subprocess
import sys
from pathlib import Path

import numpy as np

HUB = Path(__file__).resolve().parents[1]
DB = HUB / "research" / "kalodata" / "kalodata.db"
VIDEOS = HUB / "research" / "kalodata" / "videos"
MODEL = "MIT/ast-finetuned-audioset-10-10-0.4593"
SR, WIN = 16000, 5.0
MUSIC_P = 0.25


def ffmpeg():
    sys.path.insert(0, str(HUB / "scripts"))
    import video_pilot as vp
    return vp.FF


def audio(path, ff):
    raw = subprocess.run([ff, "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def db(x):
    r = float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
    return 20 * math.log10(r) if r > 1e-6 else -120.0


def loudness(wave, words):
    spans = [(w["s"], w["e"]) for w in words if w.get("e", 0) > w.get("s", 0)]
    speech = [wave[int(s * SR):int(e * SR)] for s, e in spans]
    gaps, prev = [], 0.0
    for s, e in spans:
        if s - prev >= 0.3:
            gaps.append(wave[int((prev + 0.05) * SR):int((s - 0.05) * SR)])
        prev = max(prev, e)
    if len(wave) / SR - prev >= 0.3:
        gaps.append(wave[int((prev + 0.05) * SR):])
    sp = [db(x) for x in speech if len(x) > SR * 0.1]
    gp = [db(x) for x in gaps if len(x) > SR * 0.2]
    return (float(np.median(sp)) if sp else None), (float(np.median(gp)) if gp else None)


def classify(wave, fe, model, labels):
    import torch
    n = max(1, int(math.ceil(len(wave) / (SR * WIN))))
    chunks = [wave[int(i * WIN * SR):int((i + 1) * WIN * SR)] for i in range(n)]
    chunks = [c for c in chunks if len(c) > SR] or [wave]
    inputs = fe(chunks, sampling_rate=SR, return_tensors="pt")
    with torch.no_grad():
        p = torch.sigmoid(model(**inputs).logits).numpy()
    return {k: p[:, labels[k]] for k in ("Music", "Singing", "Speech")}


def level(music_share, gap_rel, speech_share):
    if music_share < 0.2:
        return "none"
    if speech_share is not None and speech_share < 0.35 and music_share >= 0.5:
        return "music-led"
    if gap_rel is not None and gap_rel < -18:
        return "quiet bed"
    return "clear"


def tag(con, limit):
    from transformers import ASTFeatureExtractor, ASTForAudioClassification
    fe = ASTFeatureExtractor.from_pretrained(MODEL)
    model = ASTForAudioClassification.from_pretrained(MODEL).eval()
    labels = {v: int(k) for k, v in model.config.id2label.items()}
    ff = ffmpeg()
    con.execute("""CREATE TABLE IF NOT EXISTS video_audio (video_id TEXT PRIMARY KEY, music_share REAL, music_p REAL,
                   singing_p REAL, speech_p REAL, speech_db REAL, gap_db REAL, gap_rel_db REAL, music_level TEXT,
                   model TEXT, at TEXT)""")
    done = {r[0] for r in con.execute("SELECT video_id FROM video_audio")}
    todo = [r for r in con.execute("SELECT video_id, speech_share FROM video_features") if r[0] not in done]
    for i, (vid, speech_share) in enumerate(todo[:limit] if limit else todo, 1):
        folder = VIDEOS / vid
        try:
            wave = audio(folder / "video.mp4", ff)
            words = json.loads((folder / "transcript.json").read_text(encoding="utf-8")) if (folder / "transcript.json").exists() else []
            sc = classify(wave, fe, model, labels)
            sp_db, gp_db = loudness(wave, words)
            rel = (gp_db - sp_db) if (sp_db is not None and gp_db is not None) else None
            share = float(np.mean(sc["Music"] >= MUSIC_P))
            con.execute("INSERT OR REPLACE INTO video_audio VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'))",
                        (vid, share, float(sc["Music"].mean()), float(sc["Singing"].mean()), float(sc["Speech"].mean()),
                         sp_db, gp_db, rel, level(share, rel, speech_share), MODEL))
            con.commit()
            print(f"{i}/{len(todo)} {vid} music {share:.0%} gap {rel if rel is None else round(rel, 1)} dB", flush=True)
        except Exception as e:  # one bad file doesn't stop the run
            print(f"{i}/{len(todo)} {vid} ERROR {str(e)[:150]}", flush=True)


def sign_p(k, n):
    """Two-sided exact sign test."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, j) for j in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def report(con):
    rows = con.execute("""SELECT f.pair, f.role, f.ad, a.music_share, a.music_p, a.gap_rel_db, a.music_level, a.singing_p
                          FROM video_features f JOIN video_audio a USING (video_id)""").fetchall()
    by = {}
    for pair, role, ad, share, mp, rel, lvl, sing in rows:
        by.setdefault(pair, {})["winner" if role == "winner" else "stalled"] = dict(
            ad=ad, share=share, mp=mp, rel=rel, lvl=lvl, has=lvl != "none", sing=sing)
    pairs = [v for v in by.values() if "winner" in v and "stalled" in v]
    out = [f"Pairs with both videos tagged: {len(pairs)}"]
    for role in ("winner", "stalled"):
        vs = [p[role] for p in pairs]
        counts = {k: sum(v["lvl"] == k for v in vs) for k in ("none", "quiet bed", "clear", "music-led")}
        out.append(f"{role:8} has music {sum(v['has'] for v in vs) / len(vs):.0%}  levels {counts}  "
                   f"mean music share {np.mean([v['share'] for v in vs]):.2f}")
    only_w = sum(p["winner"]["has"] and not p["stalled"]["has"] for p in pairs)
    only_s = sum(p["stalled"]["has"] and not p["winner"]["has"] for p in pairs)
    out.append(f"Discordant pairs: music only in the winner {only_w}, only in the stalled video {only_s}; "
               f"sign test p = {sign_p(only_w, only_w + only_s):.3f}")
    rel = [(p["winner"]["rel"], p["stalled"]["rel"]) for p in pairs
           if p["winner"]["has"] and p["stalled"]["has"] and p["winner"]["rel"] is not None and p["stalled"]["rel"] is not None]
    if rel:
        louder = sum(w > s for w, s in rel)
        out.append(f"When both have music ({len(rel)} pairs): winner's music louder relative to the voice in {louder}; "
                   f"median gap level winner {np.median([w for w, _ in rel]):.1f} dB vs stalled {np.median([s for _, s in rel]):.1f} dB; "
                   f"p = {sign_p(louder, len(rel)):.3f}")
    for ad in (1, 0):
        sub = [p for p in pairs if p["winner"]["ad"] == ad]
        if sub:
            out.append(f"Winners {'paid-boosted' if ad else 'organic'} ({len(sub)} pairs): music in winner "
                       f"{np.mean([p['winner']['has'] for p in sub]):.0%} vs stalled {np.mean([p['stalled']['has'] for p in sub]):.0%}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    con = sqlite3.connect(DB)
    if not a.report_only:
        tag(con, a.limit)
    print("\n".join(report(con)))


if __name__ == "__main__":
    main()
