"""Cycle 1, P01 'Moves with you' AI base video (EC-P01-A02-H01-V01). Owner approved up to ~$3 on 2026-10-24.

Kling 4.0 reference-to-video, 12 s, 720p, 9:16. References are face-free crops of the store's caramel photo,
so the output shows an AI-generated model, not the supplier's model. Run: python scripts/make_ec_p01_a02_base.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

CREATIVE_ID = "EC-P01-A02-H01-V01"
MODEL = "kling-video/v4.0/reference-to-video"
DURATION, RESOLUTION, ASPECT = 12, "720p", "9:16"
MAX_USD_PER_SECOND = 0.157  # highest Kling 4.0 rate listed on open.higgsfield.ai, 2026-10-24
FOLDER = hd.ASSETS / CREATIVE_ID
REFS = [FOLDER / "ref1_dress_neck_down.jpg", FOLDER / "ref2_cable_slit_closeup.jpg"]

PROMPT = (
    "Vertical 9:16 fashion video. An AI-generated young adult woman (not any real person) wears the exact "
    "caramel-brown cable-knit midi sweater dress shown in @image_1: mock neck, ribbed waistband, long sleeves, "
    "vertical cable-knit pattern down the skirt, fitted through the hip, midi length, and a front slit on her "
    "right side exactly as shown in @image_2. She walks confidently toward the camera along a quiet city "
    "sidewalk with pale concrete walls in soft overcast autumn daylight, wearing black knee-high boots and "
    "carrying a black slouchy leather bag. Her natural stride opens the front slit as she walks. Smooth handheld "
    "tracking shot at eye level, ending with a slow push-in on the cable-knit texture and the slit. Keep the "
    "dress color, knit pattern, neckline, waistband and slit identical to the references. No text, no logos."
)


def main():
    if not recipe._recipe_path(CREATIVE_ID).exists():
        recipe.new_creative(
            CREATIVE_ID, experiment_id="C1-P01-A02", product_id="gid://shopify/Product/9751656071407",
            length_s=DURATION, resolution=RESOLUTION, source="higgsfield-api",
            hook_text="POV: a sweater dress you can actually walk in",
            format="try-on", hook_type="pov", opening_visual="lifestyle", setting="outdoor",
            creator="on-camera", on_screen_text="captions+hook", voice="none",
        )
        recipe.add_step(CREATIVE_ID, "concept", {
            "angle": "Moves with you (front slit, easy to walk in)", "product": "Cable Knit Mock Neck Midi Dress",
            "color": "Caramel", "notes": "AI-generated model; label as AI-generated on TikTok",
        })
        recipe.add_step(CREATIVE_ID, "product_reference", {
            "source_photo": "Shopify 1E3E6FA7B028205FCC94E89C7CF6CC63.jpg (caramel street shot)",
            "references": [p.name for p in REFS], "processing": "cropped collar-down to exclude the supplier model's face",
        })

    urls = [hf_api.upload(p) for p in REFS]
    payload = {"prompt": PROMPT, "image_urls": urls, "duration": DURATION,
               "resolution": RESOLUTION, "aspect_ratio": ASPECT}
    sub = hf_api.submit(MODEL, payload)
    request_id = sub.get("request_id")
    print(f"Submitted {MODEL} request {request_id} ({DURATION}s {RESOLUTION} {ASPECT}); max est. ${DURATION * MAX_USD_PER_SECOND:.2f}")
    (FOLDER / "request.json").write_text(json.dumps({"request_id": request_id, "model": MODEL}, indent=2), encoding="utf-8")

    def tick(status, secs):
        print(f"  {secs:>4}s  {status.get('status')}", flush=True)

    final = hf_api.wait(sub["status_url"], on_tick=tick)
    est_usd = round(DURATION * MAX_USD_PER_SECOND, 2)
    step = {"model": MODEL, "prompt": PROMPT, "duration": DURATION, "resolution": RESOLUTION,
            "aspect_ratio": ASPECT, "request_id": request_id, "status": final.get("status"),
            "cost_note": f"estimate at ${MAX_USD_PER_SECOND}/s; confirm in open.higgsfield.ai billing"}
    if final.get("status") != "completed":
        step["error"] = final.get("error") or final
        # Rejected or failed jobs have not been billed so far (balance unchanged); record $0 and check billing.
        recipe.add_step(CREATIVE_ID, "clip", step, usd=0.0)
        print(f"Generation ended with status {final.get('status')}: {str(step['error'])[:400]}")
        return 1

    video_url = (final.get("video") or {}).get("url")
    dest = FOLDER / "base_raw.mp4"
    hf_api.download(video_url, dest)
    step["video_url"] = video_url
    recipe.add_step(CREATIVE_ID, "clip", step, usd=est_usd)
    recipe.finish(CREATIVE_ID, video_url=video_url, local_path=str(dest.relative_to(hd.HUB_ROOT)), status="REVIEW")
    hd.log(f"{CREATIVE_ID}: base clip generated ({MODEL}, {DURATION}s {RESOLUTION}), est ${est_usd}; awaiting owner review")
    print(f"Done: {dest} ({dest.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
