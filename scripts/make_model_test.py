"""Cheap-tier model test (owner, 2026-10-26): the same P01 "knee-high boots" script on three sub-$1.50 setups, to pick
the model for test videos (two-tier strategy: cheap tests, Seedance 2.5 720p only for winners).

  EC-P01-A05-H01-V04  bytedance/seedance-2.0-mini   720p 15 s  ≈ $1.13
  EC-P01-A05-H01-V05  bytedance/seedance-2.0-fast   720p 15 s  ≈ $1.36
  EC-P01-A05-H01-V06  bytedance/seedance-2.5        480p 14 s  ≈ $1.44
Same script as V03 except the "midi" line (V03 came out as "mini"), plus the photorealism block (prompt_style.py).
All three jobs are submitted together and polled until done.
Run: OPENROUTER_API_KEY must be set. python -I scripts/make_model_test.py
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
from make_ec_p01_a03_tryon import REFS  # noqa: E402
from prompt_style import PRESENTER, REALISM  # noqa: E402

API = "https://openrouter.ai/api/v1"
PARENT_ID = "EC-P01-A05-H01-V03"
RUNS = [  # creative id, model, resolution, seconds, $ per M video tokens, pixels (w, h)
    ("EC-P01-A05-H01-V04", "bytedance/seedance-2.0-mini", "720p", 15, 3.50, (720, 1280)),
    ("EC-P01-A05-H01-V05", "bytedance/seedance-2.0-fast", "720p", 15, 4.20, (720, 1280)),
    ("EC-P01-A05-H01-V06", "bytedance/seedance-2.5", "480p", 14, 10.70, (480, 854)),
]
LINES = [
    "If you own knee-high boots, you need this dress this winter.",
    "Chunky cable knit, a mock neck, and a ribbed waist that keeps it fitted.",
    "The front slit lets you actually walk in it, and the below-the-knee length looks so good over boots.",
    "It comes in seven colors. Tap the link to see them.",
]


def prompt(seconds):
    t = [0, 3, 7, 11, 15] if seconds == 15 else [0, 3, 6.5, 10.5, 14]
    return (
        f"Vertical 9:16 UGC-style fashion try-on video for social media, {seconds} seconds, four quick cuts, natural "
        "phone-camera look, bright warm apartment with wood floors, an arched mirror and soft daylight. The presenter "
        f"is {PRESENTER} with long brunette hair, friendly and confident, speaking English directly to the camera at a "
        "brisk, natural pace with no pauses between lines. In every shot she wears the exact caramel-brown cable-knit "
        "midi sweater dress from the reference images: mock neck, ribbed waistband, long sleeves with ribbed cuffs, "
        "vertical cable-knit pattern down the skirt with a diagonal wrap seam, fitted through the hip, below-the-knee "
        "length, and a front slit. Keep its color, knit pattern, neckline, waistband and slit identical to the "
        "references. She wears plain black knee-high leather boots with a low heel; the dress hem overlaps the boot "
        "tops.\n"
        f"Shot 1 ({t[0]}-{t[1]} s): already wearing the dress and boots, she walks toward the camera from the mirror "
        f"and says: \"{LINES[0]}\"\n"
        f"Shot 2 ({t[1]}-{t[2]} s): detail close-ups: her hand runs over the chunky cable knit, then the mock neck, "
        f"then the ribbed waist, while she says: \"{LINES[1]}\"\n"
        f"Shot 3 ({t[2]}-{t[3]} s): full-length shot; she steps toward the camera so the front slit opens over the "
        f"boots, then turns once, saying: \"{LINES[2]}\"\n"
        f"Shot 4 ({t[3]}-{t[4]} s): smiling close-up, lips moving clearly with every word, as she says: "
        f"\"{LINES[3]}\"\n"
        "Clear natural speech, light room tone, no background music, no brand names on any item. " + REALISM
    )


def headers():
    return {"Authorization": f"Bearer {hub_env.get_secret('openrouter_api')}", "Content-Type": "application/json"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    urls = [hf_api.upload(p) for p in REFS]
    jobs = {}
    for cid, model, res, secs, usd_m, (w, h) in RUNS:
        est = round(secs * w * h * 24 / 1024 * usd_m / 1e6, 2)
        if not recipe._recipe_path(cid).exists():
            recipe.new_creative(
                cid, experiment_id="C1-P01-A05-MODELTEST", product_id="gid://shopify/Product/9751656071407",
                parent_id=PARENT_ID, changed_field="model", length_s=secs, resolution=res, source="openrouter",
                hook_text=LINES[0], format="try-on", hook_type="callout", opening_visual="product-on-body-walk",
                setting="living-room", creator="on-camera", on_screen_text="none", voice="on-camera",
                pace_cuts_per_15s=3)
            recipe.add_step(cid, "script", {"lines": LINES})
        payload = {"model": model, "prompt": prompt(secs), "duration": secs, "resolution": res, "aspect_ratio": "9:16",
                   "generate_audio": True,
                   "input_references": [{"type": "image_url", "image_url": {"url": u}} for u in urls]}
        r = requests.post(f"{API}/videos", headers=headers(), json=payload, timeout=60)
        if not r.ok:
            print(f"{cid} {model}: submit failed HTTP {r.status_code} {r.text[:300]}")
            continue
        jobs[cid] = (r.json(), model, res, secs, est, payload["prompt"])
        print(f"{cid}: submitted {model} {res} {secs}s, est ${est}", flush=True)

    start, pending = time.time(), set(jobs)
    while pending and time.time() - start < 1800:
        time.sleep(15)
        for cid in list(pending):
            job, model, res, secs, est, text = jobs[cid]
            s = requests.get(job["polling_url"], headers=headers(), timeout=60).json()
            if s.get("status") not in ("completed", "failed"):
                continue
            pending.discard(cid)
            cost = (s.get("usage") or {}).get("cost")
            step = {"model": model, "prompt": text, "duration": secs, "resolution": res, "aspect_ratio": "9:16",
                    "generate_audio": True, "job_id": job.get("id"), "status": s.get("status"),
                    "cost_note": f"OpenRouter usage.cost {cost}; est ${est}"}
            if s.get("status") != "completed":
                step["error"] = s.get("error") or s
                recipe.add_step(cid, "clip", step, usd=float(cost or 0))
                print(f"{cid}: failed {str(step['error'])[:200]}")
                continue
            dest = hd.ASSETS / cid / "tryon_raw.mp4"
            dest.parent.mkdir(parents=True, exist_ok=True)
            content = requests.get(s["unsigned_urls"][0], headers=headers(), timeout=300)
            content.raise_for_status()
            dest.write_bytes(content.content)
            recipe.add_step(cid, "clip", step, usd=float(cost if cost is not None else est))
            recipe.finish(cid, local_path=str(dest.relative_to(hd.HUB_ROOT)), status="REVIEW")
            print(f"{cid}: done in {int(time.time() - start)}s, cost ${cost}", flush=True)
    print("Still pending:", sorted(pending) if pending else "none")


if __name__ == "__main__":
    main()
