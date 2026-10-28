"""Seedance 2.0 Mini remake of the P01 try-on ad (EC-P01-A03-H01-V03, parent EC-P01-A03-H01-V01). Owner asked 2026-10-25.

Same 15 s / 4-shot prompt and face-free reference crops as V01, run on bytedance/seedance-2.0-mini via OpenRouter
(720p, 9:16, audio) to test whether a ~$1.13 video holds up against the $5.89 Seedance 2.5 original.
Price: $3.50 per M video tokens; tokens/s = 720 x 1280 x 24 / 1024 = 21,600, so 15 s ≈ $1.13.
Run: OPENROUTER_API_KEY must be set (secrets.openrouter_api). python -I scripts/make_ec_p01_a03_seedance_mini.py
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
from make_ec_p01_a03_tryon import PROMPT, REFS  # noqa: E402  (the V01 prompt and references, unchanged)

CREATIVE_ID = "EC-P01-A03-H01-V03"
PARENT_ID = "EC-P01-A03-H01-V01"
MODEL = "bytedance/seedance-2.0-mini"
DURATION, RESOLUTION, ASPECT = 15, "720p", "9:16"
USD_PER_M_TOKENS = 3.50
TOKENS_PER_SECOND = 720 * 1280 * 24 / 1024
API = "https://openrouter.ai/api/v1"
FOLDER = hd.ASSETS / CREATIVE_ID


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
        print("Not enough OpenRouter credit yet; nothing submitted.")
        return 2

    if not recipe._recipe_path(CREATIVE_ID).exists():
        recipe.new_creative(
            CREATIVE_ID, experiment_id="C1-P01-A03", product_id="gid://shopify/Product/9751656071407",
            parent_id=PARENT_ID, changed_field="model", length_s=DURATION, resolution=RESOLUTION, source="openrouter",
            hook_text="Okay, you need to see this sweater dress.",
            format="try-on", hook_type="curiosity", opening_visual="creator-face", setting="living-room",
            creator="on-camera", on_screen_text="none", voice="on-camera", pace_cuts_per_15s=3,
        )
        recipe.add_step(CREATIVE_ID, "concept", {
            "angle": "Seedance 2.0 Mini remake of EC-P01-A03-H01-V01 (same prompt and references, cheaper model)",
            "product": "Cable Knit Mock Neck Midi Dress", "color": "Caramel",
            "notes": "AI-generated presenter; label AI on TikTok; no testimonial or purchase claims",
        })

    urls = [hf_api.upload(p) for p in REFS]  # public HTTPS copies of the face-free crops
    payload = {"model": MODEL, "prompt": PROMPT, "duration": DURATION, "resolution": RESOLUTION,
               "aspect_ratio": ASPECT, "generate_audio": True,
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
