"""P01 "knee-high boots" ad rebuilt from the video study (EC-P01-A05-H01-V03, parent EC-P01-A05-H01-V02). 2026-10-26.

Owner chose Seedance 2.5 via OpenRouter, 15 s, 720p, 9:16, audio. Changes from V02, per the 91-pair study
(research/kalodata/VIDEO_STUDY_2026-10.md): wearing the dress from 0 s, a run of detail close-ups, denser continuous
speech (~45 words, ~3 words/s vs 2.3), no price or delivery lines (owner rule 2026-10-25), no on-screen text (owner
rule stands). Same face-free reference crops, so the presenter is AI-generated; label AI on TikTok.
Price: $10.70 per M video tokens; 720x1280x24/1024 = 21,600 tokens/s, so 15 s ≈ $3.47.
Run: OPENROUTER_API_KEY must be set (secrets.openrouter_api). python -I scripts/make_ec_p01_a05_v03.py
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
from prompt_style import PRESENTER, REALISM  # noqa: E402
from make_ec_p01_a03_tryon import REFS  # noqa: E402  (face-free crops of the P01 product photo)

CREATIVE_ID = "EC-P01-A05-H01-V03"
PARENT_ID = "EC-P01-A05-H01-V02"
MODEL = "bytedance/seedance-2.5"
DURATION, RESOLUTION, ASPECT = 15, "720p", "9:16"
USD_PER_M_TOKENS = 10.70
TOKENS_PER_SECOND = 720 * 1280 * 24 / 1024
API = "https://openrouter.ai/api/v1"
FOLDER = hd.ASSETS / CREATIVE_ID
LINES = [
    "If you own knee-high boots, you need this dress this winter.",
    "Chunky cable knit, a mock neck, and a ribbed waist that keeps it fitted.",
    "The front slit lets you actually walk in it, and the midi length looks so good over boots.",
    "It comes in seven colors. Tap the link to see them.",
]
PROMPT = (
    "Vertical 9:16 UGC-style fashion try-on video for social media, 15 seconds, four quick cuts, natural phone-camera "
    "look, bright warm apartment with wood floors, an arched mirror and soft daylight. The presenter is "
    f"{PRESENTER} with long brunette hair, friendly and confident, speaking "
    "English directly to the camera at a brisk, natural pace with no pauses between lines. In every shot she wears the "
    "exact caramel-brown cable-knit midi sweater dress from the reference images: mock neck, ribbed waistband, long "
    "sleeves with ribbed cuffs, vertical cable-knit pattern down the skirt with a diagonal wrap seam, fitted through "
    "the hip, midi length, and a front slit. Keep its color, knit pattern, neckline, waistband and slit identical to "
    "the references. She wears plain black knee-high leather boots with a low heel; the dress hem overlaps the boot "
    "tops.\n"
    f"Shot 1 (0-3 s): already wearing the dress and boots, she walks toward the camera from the mirror and says: "
    f"\"{LINES[0]}\"\n"
    f"Shot 2 (3-7 s): detail close-ups: her hand runs over the chunky cable knit, then the mock neck, then the ribbed "
    f"waist, while she says: \"{LINES[1]}\"\n"
    f"Shot 3 (7-11 s): full-length shot; she steps toward the camera so the front slit opens over the boots, then "
    f"turns once, saying: \"{LINES[2]}\"\n"
    f"Shot 4 (11-15 s): smiling close-up as she glances down at the dress and says: \"{LINES[3]}\"\n"
    "Clear natural speech, light room tone, no background music, no brand names on any item. "
    + REALISM
)


def headers():
    return {"Authorization": f"Bearer {hub_env.get_secret('openrouter_api')}", "Content-Type": "application/json"}


def main():
    est = round(DURATION * TOKENS_PER_SECOND * USD_PER_M_TOKENS / 1e6, 2)
    credits = requests.get(f"{API}/credits", headers=headers(), timeout=60)
    if not credits.ok:
        print(f"Couldn't read the OpenRouter balance (HTTP {credits.status_code}); nothing submitted.")
        return 1
    d = credits.json().get("data", {})
    left = (d.get("total_credits") or 0) - (d.get("total_usage") or 0)
    print(f"OpenRouter credit left: ${left:.2f}; this job ≈ ${est:.2f}")
    if left < est:
        print("Not enough OpenRouter credit; nothing submitted.")
        return 2

    if not recipe._recipe_path(CREATIVE_ID).exists():
        recipe.new_creative(
            CREATIVE_ID, experiment_id="C1-P01-A05", product_id="gid://shopify/Product/9751656071407",
            parent_id=PARENT_ID, changed_field="script", length_s=DURATION, resolution=RESOLUTION, source="openrouter",
            hook_text=LINES[0], format="try-on", hook_type="callout", opening_visual="product-on-body-walk",
            setting="living-room", creator="on-camera", on_screen_text="none", voice="on-camera", pace_cuts_per_15s=3,
        )
        recipe.add_step(CREATIVE_ID, "concept", {
            "angle": "Knee-high boots callout, rebuilt from the 91-pair video study",
            "product": "Cable Knit Mock Neck Midi Dress", "color": "Caramel",
            "notes": "AI-generated presenter; label AI on TikTok; no testimonial, price or delivery claims",
        })
        recipe.add_step(CREATIVE_ID, "script", {"lines": LINES})

    urls = [hf_api.upload(p) for p in REFS]
    payload = {"model": MODEL, "prompt": PROMPT, "duration": DURATION, "resolution": RESOLUTION, "aspect_ratio": ASPECT,
               "generate_audio": True,
               "input_references": [{"type": "image_url", "image_url": {"url": u}} for u in urls]}
    r = requests.post(f"{API}/videos", headers=headers(), json=payload, timeout=60)
    if not r.ok:
        print(f"Submit failed: HTTP {r.status_code} {r.text[:600]}")
        recipe.add_step(CREATIVE_ID, "clip", {"model": MODEL, "status": "rejected", "error": r.text[:600]}, usd=0.0)
        return 1
    job = r.json()
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / "request.json").write_text(json.dumps({"job_id": job.get("id"), "model": MODEL}, indent=2), encoding="utf-8")
    print(f"Submitted {MODEL} job {job.get('id')} ({DURATION}s {RESOLUTION} {ASPECT}, audio), est ${est:.2f}")

    start = time.time()
    while True:
        time.sleep(10)
        s = requests.get(job["polling_url"], headers=headers(), timeout=60).json()
        print(f"  {int(time.time() - start):>4}s  {s.get('status')}", flush=True)
        if s.get("status") in ("completed", "failed") or time.time() - start > 1500:
            break

    cost = (s.get("usage") or {}).get("cost")
    step = {"model": MODEL, "prompt": PROMPT, "duration": DURATION, "resolution": RESOLUTION, "aspect_ratio": ASPECT,
            "generate_audio": True, "references": [str(p.relative_to(hd.HUB_ROOT)) for p in REFS],
            "job_id": job.get("id"), "status": s.get("status"), "cost_note": f"OpenRouter usage.cost {cost}; est ${est:.2f}"}
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
