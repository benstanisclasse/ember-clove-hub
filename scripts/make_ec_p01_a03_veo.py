"""Veo 3.1 remake of the P01 try-on ad (EC-P01-A03-H01-V02, parent EC-P01-A03-H01-V01). Owner asked 2026-10-25.

Google Veo 3.1 via OpenRouter, 720p, 9:16, with audio. Veo clips max out at 8 s, so the 15 s / 4-shot script is cut to
3 shots and the first two spoken lines (the colors/link line is dropped). Same face-free reference crops as V01, so
the presenter is AI-generated. List price $0.40/s with audio = $3.20.
Run: OPENROUTER_API_KEY must be set (secrets.openrouter_api). python -I scripts/make_ec_p01_a03_veo.py
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402
import hub_env  # noqa: E402
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

CREATIVE_ID = "EC-P01-A03-H01-V02"
PARENT_ID = "EC-P01-A03-H01-V01"
MODEL = "google/veo-3.1"
DURATION, RESOLUTION, ASPECT = 8, "720p", "9:16"
USD_PER_SECOND = 0.40
API = "https://openrouter.ai/api/v1"
FOLDER = hd.ASSETS / CREATIVE_ID
REF_FOLDER = hd.ASSETS / "EC-P01-A02-H01-V01"
REFS = [REF_FOLDER / "ref1_dress_neck_down.jpg", REF_FOLDER / "ref2_cable_slit_closeup.jpg"]

PROMPT = (
    "Vertical 9:16 UGC-style fashion try-on video for social media, 8 seconds, three quick cuts, natural phone-camera "
    "look, bright warm apartment with wood floors, an arched mirror and soft daylight. The presenter is an "
    "AI-generated young adult woman (not any real person) with long brunette hair, friendly and excited, speaking "
    "English directly to the camera. The dress is the exact caramel-brown cable-knit midi sweater dress from the "
    "reference images: mock neck, ribbed waistband, long sleeves with ribbed cuffs, vertical cable-knit pattern down "
    "the skirt with a diagonal wrap seam, fitted through the hip, midi length, and a front slit. Keep its color, knit "
    "pattern, neckline, waistband and slit identical to the references.\n"
    "Shot 1 (0-2.5 s): wearing a casual white tee, she holds the caramel dress on a hanger up to the camera and says: "
    "\"Okay, you need to see this sweater dress.\"\n"
    "Shot 2 (2.5-5.5 s): cut to her wearing the dress, mid-shot, smoothing the ribbed waist and turning slightly, "
    "saying: \"It's cable knit, and it's fitted through the hips.\"\n"
    "Shot 3 (5.5-8 s): cut to a full-length shot in black knee-high boots; she takes big confident steps toward the "
    "camera that open the front slit and smiles.\n"
    "Clear natural speech, light room tone, no background music, no on-screen text, no subtitles, no logos."
)


def headers():
    return {"Authorization": f"Bearer {hub_env.get_secret('openrouter_api')}", "Content-Type": "application/json"}


def main():
    est = DURATION * USD_PER_SECOND
    credits = requests.get(f"{API}/credits", headers=headers(), timeout=60)
    if credits.ok:
        d = credits.json().get("data", {})
        left = (d.get("total_credits") or 0) - (d.get("total_usage") or 0)
        print(f"OpenRouter credit left: ${left:.2f}; this job ≈ ${est:.2f}")
        if left < est:
            print("Not enough OpenRouter credit; nothing submitted.")
            return 1
    else:
        print(f"Couldn't read the credit balance (HTTP {credits.status_code}); continuing.")

    if not recipe._recipe_path(CREATIVE_ID).exists():
        recipe.new_creative(
            CREATIVE_ID, experiment_id="C1-P01-A03", product_id="gid://shopify/Product/9751656071407",
            parent_id=PARENT_ID, changed_field="model", length_s=DURATION, resolution=RESOLUTION, source="openrouter",
            hook_text="Okay, you need to see this sweater dress.",
            format="try-on", hook_type="curiosity", opening_visual="creator-face", setting="living-room",
            creator="on-camera", on_screen_text="none", voice="on-camera", pace_cuts_per_15s=5,
        )
        recipe.add_step(CREATIVE_ID, "concept", {
            "angle": "Veo 3.1 remake of EC-P01-A03-H01-V01 (8 s cap: 3 shots, first two lines)",
            "product": "Cable Knit Mock Neck Midi Dress", "color": "Caramel",
            "notes": "AI-generated presenter; label AI on TikTok; no testimonial or purchase claims",
        })
        recipe.add_step(CREATIVE_ID, "script", {"lines": [
            "Okay, you need to see this sweater dress.", "It's cable knit, and it's fitted through the hips."]})

    urls = [hf_api.upload(p) for p in REFS]  # public HTTPS copies of the face-free crops
    payload = {
        "model": MODEL, "prompt": PROMPT, "duration": DURATION, "resolution": RESOLUTION, "aspect_ratio": ASPECT,
        "generate_audio": True,
        "input_references": [{"type": "image_url", "image_url": {"url": u}} for u in urls],
        "provider": {"options": {"google-vertex": {"parameters": {
            "personGeneration": "allow_adult",
            "negativePrompt": "subtitles, captions, on-screen text, logos, watermark, distorted hands"}}}},
    }
    r = requests.post(f"{API}/videos", headers=headers(), json=payload, timeout=60)
    if not r.ok:
        print(f"Submit failed: HTTP {r.status_code} {r.text[:600]}")
        recipe.add_step(CREATIVE_ID, "clip", {"model": MODEL, "status": "rejected", "error": r.text[:600]}, usd=0.0)
        return 1
    job = r.json()
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / "request.json").write_text(json.dumps({"job_id": job.get("id"), "model": MODEL}, indent=2), encoding="utf-8")
    print(f"Submitted {MODEL} job {job.get('id')} ({DURATION}s {RESOLUTION} {ASPECT}, audio), list ${est:.2f}")

    start = time.time()
    while True:
        time.sleep(10)
        s = requests.get(job["polling_url"], headers=headers(), timeout=60).json()
        print(f"  {int(time.time() - start):>4}s  {s.get('status')}", flush=True)
        if s.get("status") in ("completed", "failed") or time.time() - start > 1500:
            break

    cost = (s.get("usage") or {}).get("cost")
    step = {"model": MODEL, "prompt": PROMPT, "duration": DURATION, "resolution": RESOLUTION, "aspect_ratio": ASPECT,
            "generate_audio": True, "job_id": job.get("id"), "status": s.get("status"),
            "cost_note": f"OpenRouter usage.cost {cost}; list ${est:.2f}"}
    if s.get("status") != "completed":
        step["error"] = s.get("error") or s
        recipe.add_step(CREATIVE_ID, "clip", step, usd=float(cost or 0))
        print(f"Generation ended with status {s.get('status')}: {str(step['error'])[:400]}")
        return 1

    dest = FOLDER / "tryon_raw.mp4"
    content = requests.get(s["unsigned_urls"][0], headers=headers(), timeout=300)
    content.raise_for_status()
    dest.write_bytes(content.content)
    recipe.add_step(CREATIVE_ID, "clip", step, usd=float(cost if cost is not None else est))
    recipe.finish(CREATIVE_ID, local_path=str(dest.relative_to(hd.HUB_ROOT)), status="REVIEW")
    print(f"Done: {dest} ({dest.stat().st_size // 1024} KB), cost ${cost}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
