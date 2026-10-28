"""Generate and QA one episode. Only called through cli.py, which enforces the stage order and the bible gate."""
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import requests

HUB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HUB / "scripts"))
import hf_api  # noqa: E402
import hub_env  # noqa: E402
import video_pilot as vp  # noqa: E402

from studio import content, db, gates  # noqa: E402

API = "https://openrouter.ai/api/v1"
EPISODES = HUB / "studio" / "episodes"


def _headers():
    return {"Authorization": f"Bearer {hub_env.get_secret('openrouter_api')}", "Content-Type": "application/json"}


# Models tried with `cli.py trial` (never approvable). Prices from OpenRouter /api/v1/videos/models, 2026-10-26.
# frames_only: the model takes a first-frame image, not reference images, so the conveyor makes that frame first.
TRIAL_MODELS = {
    "kwaivgi/kling-v3.0-std": {"usd_per_s": 0.126, "resolution": "720p", "frames_only": True, "max_prompt_chars": 2500},
    "kwaivgi/kling-v3.0-pro": {"usd_per_s": 0.168, "resolution": "720p", "frames_only": True, "max_prompt_chars": 2500},
    # The rules' own model, for trials that differ in another way (e.g. --no-face-ref). $10.70/M tokens at 480p.
    "bytedance/seedance-2.5": {"usd_per_s": 0.103, "resolution": "480p", "frames_only": False},
    # Higgsfield developer API (open.higgsfield.ai, separate $ balance). It can't report a job's cost: the rate is an
    # estimate from past bills (720p was $0.32-0.39/s); check open.higgsfield.ai billing for the real charge.
    "higgsfield:bytedance/seedance-2.5/reference-to-video": {"usd_per_s": 0.30, "resolution": "480p",
                                                              "frames_only": False, "provider": "higgsfield"},
}
FRAME_MODEL = "google/gemini-3.1-flash-image"


def check_budget(con, b, est=None, video_cap=None, day_cap=None):
    """video_cap / day_cap: one-off limits the owner approved in their own words (cli trial --owner-cap /
    --owner-day-cap); the weekly cap always applies."""
    g = b["rules"].generation
    est = gates.estimate_usd(b) if est is None else est
    cap = g.max_usd_per_video if video_cap is None else video_cap
    daily = g.max_usd_per_day if day_cap is None else day_cap
    today = dt.date.today()
    week_start = (today - dt.timedelta(days=today.weekday())).isoformat()
    problems = []
    if cap is not None and est > cap:  # a cap set to null in the rules is off
        problems.append(f"estimate ${est} > max ${cap} per video")
    if daily is not None and db.spent(con, today.isoformat()) + est > daily:
        problems.append(f"would pass the daily cap ${daily}")
    if g.max_usd_per_week is not None and db.spent(con, week_start) + est > g.max_usd_per_week:
        problems.append(f"would pass the weekly cap ${g.max_usd_per_week}")
    if problems:
        raise db.GateError("Budget: " + "; ".join(problems))
    return est


def first_frame(ep, script, b, out):
    """Make the opening still for a frame-only model from the face, place and store-piece images. Returns cost."""
    import base64
    text, images = gates.build_first_frame_prompt(ep, script, b)
    content = [{"type": "text", "text": text}]
    for p in images:
        mime = "image/png" if p.endswith(".png") else "image/jpeg"
        content.append({"type": "image_url", "image_url": {
            "url": f"data:{mime};base64," + base64.b64encode((HUB / p).read_bytes()).decode()}})
    r = requests.post(f"{API}/chat/completions", headers=_headers(), timeout=300, json={
        "model": FRAME_MODEL, "modalities": ["image", "text"], "image_config": {"aspect_ratio": "9:16"},
        "usage": {"include": True}, "messages": [{"role": "user", "content": content}]})
    if not r.ok:
        raise db.GateError(f"First frame refused: HTTP {r.status_code} {r.text[:300]}")
    data = r.json()
    imgs = (data["choices"][0]["message"].get("images") or [])
    if not imgs:
        raise db.GateError(f"First frame: no image returned ({str(data['choices'][0]['message'].get('content'))[:200]})")
    out.write_bytes(base64.b64decode(imgs[0]["image_url"]["url"].split(",", 1)[1]))
    out.with_suffix(".prompt.txt").write_text(text + "\n\nimages: " + ", ".join(images), encoding="utf-8")
    return float((data.get("usage") or {}).get("cost") or 0)


def generate(con, ep, b, test, trial_model=None, video_cap=None, frame=None, day_cap=None, face_ref=True):
    script = json.loads(ep["script_json"])
    g = b["rules"].generation
    face_ref = face_ref and g.face_reference  # the rule wins: no face image when the rules say so
    trial = TRIAL_MODELS.get(trial_model) if trial_model else None
    if trial_model and not trial:
        raise db.GateError(f"Unknown trial model {trial_model}; known: {', '.join(TRIAL_MODELS)}")
    template = "video_prompt_frame.j2" if trial and trial["frames_only"] else "video_prompt.j2"
    prompt, phash = gates.build_prompt(ep, script, b, template, face_ref)
    limit = (trial or {}).get("max_prompt_chars")
    if limit and len(prompt) > limit:
        raise db.GateError(f"Prompt is {len(prompt)} characters; {trial_model} takes at most {limit}. Shorten the script.")
    model, resolution = (trial_model, trial["resolution"]) if trial else (g.model, g.resolution)
    est = check_budget(con, b, round(trial["usd_per_s"] * g.duration_s, 2) if trial else None, video_cap, day_cap)
    payload = {"model": model, "prompt": prompt, "duration": g.duration_s, "resolution": resolution,
               "aspect_ratio": "9:16", "generate_audio": True}
    out_dir = EPISODES / ep["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    if trial and trial["frames_only"]:
        if frame is None:  # otherwise reuse the preview still the owner already saw
            frame = out_dir / f"{ep['id']}_a{ep['attempt'] + 1}_first_frame.png"
            fjob = content.start_job(con, f"TT-{ep['id']}", "image", "openrouter", FRAME_MODEL,
                                     {"purpose": "first_frame"}, "first_frame.j2")
            try:
                frame_cost = first_frame(ep, script, b, frame)
            except Exception as e:
                content.finish_job(con, fjob, "failed", error=f"{type(e).__name__}: {e}")
                raise
            content.finish_job(con, fjob, "completed", cost_usd=frame_cost, cost_basis="billed", output_path=frame)
            con.execute("INSERT INTO spend (episode_id, usd, at) VALUES (?,?,?)", (ep["id"], frame_cost, db.now()))
            con.commit()
        payload["frame_images"] = [{"type": "image_url", "image_url": {"url": hf_api.upload(frame)},
                                    "frame_type": "first_frame"}]
    else:
        urls = [hf_api.upload(HUB / p) for p in gates.reference_images(ep, b, face_ref)]
        payload["input_references"] = [{"type": "image_url", "image_url": {"url": u}} for u in urls]
    attempt = ep["attempt"] + 1
    out = out_dir / f"{ep['id']}_a{attempt}_{model.split('/')[-1]}_{resolution}.mp4"
    # Content Studio Phase C: every attempt is recorded (provider, model, template version, prompt, references,
    # timings, cost and how the cost is known) and never overwritten.
    provider = "higgsfield" if (trial or {}).get("provider") == "higgsfield" else "openrouter"
    refs = [str(frame)] if trial and trial["frames_only"] else list(gates.reference_images(ep, b, face_ref))
    job_id = content.start_job(con, f"TT-{ep['id']}", "video", provider, model,
                               {"resolution": resolution, "duration_s": g.duration_s, "face_ref": face_ref,
                                "trial": bool(trial), "attempt": attempt}, template, phash, prompt, refs)
    try:
        return _run_generation(con, ep, b, test, g, trial, model, resolution, payload, prompt, phash, est, out,
                               attempt, job_id, urls if not (trial and trial["frames_only"]) else None)
    except Exception as e:
        row = con.execute("SELECT status FROM generation_jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row and row["status"] == "running":
            content.finish_job(con, job_id, "failed", error=f"{type(e).__name__}: {e}")
        raise


def _run_generation(con, ep, b, test, g, trial, model, resolution, payload, prompt, phash, est, out, attempt, job_id, urls):
    if (trial or {}).get("provider") == "higgsfield":
        hf_model = model.split(":", 1)[1]
        try:
            sub = hf_api.submit(hf_model, {"prompt": prompt, "image_urls": urls, "duration": g.duration_s,
                                           "resolution": resolution, "aspect_ratio": "9:16", "output_format": "mp4",
                                           "generate_audio": True})
        except RuntimeError as e:
            raise db.GateError(f"Higgsfield refused the job: {str(e)[:300]}")
        s = hf_api.wait(sub["status_url"])
        done = s.get("status") == "completed"
        cost = est if done else 0.0  # Higgsfield can't report cost; failed jobs have been refunded so far
        con.execute("INSERT INTO spend (episode_id, usd, at) VALUES (?,?,?)", (ep["id"], cost, db.now()))
        con.commit()
        if not done:
            content.finish_job(con, job_id, s.get("status") or "failed", sub.get("request_id"), 0.0, "estimate",
                               error=str(s.get("error") or s)[:300])
            raise db.GateError(f"Generation ended {s.get('status')}: {str(s.get('error') or s)[:300]}")
        hf_api.download((s.get("video") or {})["url"], out)
        content.finish_job(con, job_id, "completed", sub.get("request_id"), cost, "estimate (Higgsfield reports no cost)",
                           output_path=out)
    else:
        r = requests.post(f"{API}/videos", headers=_headers(), json=payload, timeout=60)
        if not r.ok:
            raise db.GateError(f"OpenRouter refused the job: HTTP {r.status_code} {r.text[:300]}")
        job, start = r.json(), time.time()
        while True:
            time.sleep(15)
            s = requests.get(job["polling_url"], headers=_headers(), timeout=60).json()
            if s.get("status") in ("completed", "failed") or time.time() - start > 1800:
                break
        billed = (s.get("usage") or {}).get("cost")
        cost = float(billed or (est if s.get("status") == "completed" else 0))
        basis = "billed" if billed else "estimate"
        con.execute("INSERT INTO spend (episode_id, usd, at) VALUES (?,?,?)", (ep["id"], cost, db.now()))
        con.commit()
        if s.get("status") != "completed":
            content.finish_job(con, job_id, s.get("status") or "timeout", job.get("id"), cost, basis,
                               error=str(s.get("error") or s)[:300])
            raise db.GateError(f"Generation failed: {str(s.get('error') or s)[:300]}")
        resp = requests.get(s["unsigned_urls"][0], headers=_headers(), timeout=300)
        resp.raise_for_status()
        out.write_bytes(resp.content)
        content.finish_job(con, job_id, "completed", job.get("id"), cost, basis, output_path=out)
    (out.parent / f"{out.stem}.prompt.txt").write_text(prompt, encoding="utf-8")
    return db.move(con, ep["id"], "GENERATED", "studio", f"generated attempt {attempt} (${cost:.2f})",
                   prompt_text=prompt, prompt_hash=phash, model=model, resolution=resolution,
                   duration_s=g.duration_s, attempt=attempt, cost_usd=round(ep["cost_usd"] + cost, 4),
                   video_path=str(out.relative_to(HUB)), test=1 if test else 0,
                   max_attempts=b["rules"].generation.max_attempts)


_WHISPER = None


def qa(con, ep, b):
    global _WHISPER
    from faster_whisper import WhisperModel
    if _WHISPER is None:
        _WHISPER = WhisperModel("medium.en", device="cpu", compute_type="int8", cpu_threads=8)
    path = HUB / ep["video_path"]
    script = json.loads(ep["script_json"])
    raw = subprocess.run([vp.FF, "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    segs, info = _WHISPER.transcribe(np.frombuffer(raw, dtype=np.float32), language="en", word_timestamps=True)
    heard_words = [w for s in segs for w in s.words]
    same = {"grey": "gray"}  # one word, two spellings: the transcriber's spelling is not a voice mistake
    heard = [same.get(w, w) for w in gates.words(" ".join(w.word for w in heard_words))]
    expected = [same.get(w, w) for w in gates.words(" ".join(script["lines"]))]
    import difflib
    diffs = [{"script": " ".join(expected[a:b_]), "heard": " ".join(heard[c:d])}
             for op, a, b_, c, d in difflib.SequenceMatcher(None, expected, heard).get_opcodes() if op != "equal"]
    q = b["rules"].qa
    duration = float(info.duration)
    speech = float(sum(w.end - w.start for w in heard_words) / max(duration, 1))
    checks = [
        {"check": "transcript matches script word for word", "passed": not diffs or not q.require_exact_transcript,
         "detail": diffs},
        {"check": f"length {b['rules'].generation.duration_s} s ± {q.duration_tolerance_s}",
         "passed": abs(duration - b["rules"].generation.duration_s) <= q.duration_tolerance_s,
         "detail": round(duration, 2)},
        {"check": f"speech covers ≥ {q.speech_share_min:.0%}", "passed": speech >= q.speech_share_min,
         "detail": round(speech, 2)},
    ]
    sheet = path.parent / f"{path.stem}_frames.jpg"
    _sheet(path, sheet, q.frames_per_second_for_review)
    for c in checks:
        c["passed"] = bool(c["passed"])  # numpy bools aren't JSON
    passed = all(c["passed"] for c in checks)
    result = {"passed": passed, "checks": checks, "frames": str(sheet.relative_to(HUB)),
              "note": "Machine checks only. The owner watches and listens before approval; realism is the owner's call."}
    return db.move(con, ep["id"], "QA_PASSED" if passed else "QA_FAILED", "studio",
                   "QA " + ("passed" if passed else "failed: " + "; ".join(c["check"] for c in checks if not c["passed"])),
                   qa_json=json.dumps(result, ensure_ascii=False))


def _sheet(path, out, fps):
    from PIL import Image, ImageDraw
    tmp = out.parent / "_frames"
    tmp.mkdir(exist_ok=True)
    subprocess.run([vp.FF, "-y", "-loglevel", "quiet", "-i", str(path), "-vf", f"fps={fps},scale=-2:300",
                    str(tmp / "f_%03d.jpg")])
    files = sorted(tmp.glob("f_*.jpg"))
    tiles = []
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        ImageDraw.Draw(im).rectangle([0, 0, 44, 18], fill="black")
        ImageDraw.Draw(im).text((3, 3), f"{i / fps:.1f}s", fill="yellow")
        tiles.append(im)
        f.unlink()
    tmp.rmdir()
    if tiles:
        w, h = tiles[0].size
        cols = 10
        sheet = Image.new("RGB", (w * cols, h * ((len(tiles) + cols - 1) // cols)))
        for i, t in enumerate(tiles):
            sheet.paste(t.resize((w, h)), ((i % cols) * w, (i // cols) * h))
        sheet.save(out, quality=85)
