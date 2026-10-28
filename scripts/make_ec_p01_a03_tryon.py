"""Cycle 1, P01 UGC try-on haul ad (EC-P01-A03-H01-V01). Owner approved up to $3.50 on 2026-10-24.

Seedance 2.5 reference-to-video, 15 s, 720p, 9:16, generated audio. Modeled on the owner's Marketing Studio
sample (4 shots, apartment, presenter speaking to camera). References are the face-free crops made for
EC-P01-A02, so the presenter is AI-generated, not the supplier's model. Run: python scripts/make_ec_p01_a03_tryon.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

CREATIVE_ID = "EC-P01-A03-H01-V01"
MODEL = "bytedance/seedance-2.5/reference-to-video"
DURATION, RESOLUTION, ASPECT = 15, "720p", "9:16"
# The "from $0.175/s" list price is the cheapest setting. This exact job (2 reference images, 9:16, 720p, audio)
# was actually billed $5.89 for 15 s (~$0.39/s) on 2026-10-25. Quote with this rate, not the list price.
EST_USD_PER_SECOND = 0.39
FOLDER = hd.ASSETS / CREATIVE_ID
REF_FOLDER = hd.ASSETS / "EC-P01-A02-H01-V01"
REFS = [REF_FOLDER / "ref1_dress_neck_down.jpg", REF_FOLDER / "ref2_cable_slit_closeup.jpg"]

PROMPT = (
    "Vertical 9:16 UGC-style fashion try-on video for social media, 15 seconds, four quick cuts, natural phone-camera "
    "look, bright warm apartment with wood floors, an arched mirror and soft daylight. The presenter is an "
    "AI-generated young adult woman (not any real person) with long brunette hair, friendly and excited, speaking "
    "English directly to the camera. The dress in every shot is the exact caramel-brown cable-knit midi sweater "
    "dress from the reference images: mock neck, ribbed waistband, long sleeves with ribbed cuffs, vertical "
    "cable-knit pattern down the skirt with a diagonal wrap seam, fitted through the hip, midi length, and a front "
    "slit. Keep its color, knit pattern, neckline, waistband and slit identical to the references.\n"
    "Shot 1 (0-3 s): wearing a casual white tee, she holds the caramel dress on a hanger up to the camera and says: "
    "\"Okay, you need to see this sweater dress.\"\n"
    "Shot 2 (3-7 s): cut to her wearing the dress, mid-shot, smoothing the ribbed waist and turning slightly, "
    "saying: \"It's cable knit, and it's fitted through the hips.\"\n"
    "Shot 3 (7-11 s): cut to a full-length shot in black knee-high boots; she takes big confident steps that open "
    "the front slit, then does a little twirl, saying: \"And the slit means you can actually walk in it.\"\n"
    "Shot 4 (11-15 s): she walks up to the camera into a smiling close-up and says: "
    "\"It comes in seven colors. Link's right here.\"\n"
    "Clear natural speech, light room tone, no background music, no on-screen text, no logos."
)


def main():
    if not recipe._recipe_path(CREATIVE_ID).exists():
        recipe.new_creative(
            CREATIVE_ID, experiment_id="C1-P01-A03", product_id="gid://shopify/Product/9751656071407",
            length_s=DURATION, resolution=RESOLUTION, source="higgsfield-api",
            hook_text="Okay, you need to see this sweater dress.",
            format="try-on", hook_type="curiosity", opening_visual="creator-face", setting="living-room",
            creator="on-camera", on_screen_text="none", voice="on-camera", pace_cuts_per_15s=3,
        )
        recipe.add_step(CREATIVE_ID, "concept", {
            "angle": "UGC try-on haul (modeled on owner's Marketing Studio sample)", "product": "Cable Knit Mock Neck Midi Dress",
            "color": "Caramel", "notes": "AI-generated presenter; label AI on TikTok; no testimonial or purchase claims",
        })
        recipe.add_step(CREATIVE_ID, "product_reference", {
            "references": [str(p.relative_to(hd.HUB_ROOT)) for p in REFS],
            "processing": "face-free crops of Shopify 1E3E6FA7B028205FCC94E89C7CF6CC63.jpg (from EC-P01-A02)",
        })
        recipe.add_step(CREATIVE_ID, "script", {"lines": [
            "Okay, you need to see this sweater dress.", "It's cable knit, and it's fitted through the hips.",
            "And the slit means you can actually walk in it.", "It comes in seven colors. Link's right here."]})

    urls = [hf_api.upload(p) for p in REFS]
    payload = {"prompt": PROMPT, "image_urls": urls, "duration": DURATION, "resolution": RESOLUTION,
               "aspect_ratio": ASPECT, "output_format": "mp4", "generate_audio": True}
    sub = hf_api.submit(MODEL, payload)
    request_id = sub.get("request_id")
    print(f"Submitted {MODEL} request {request_id} ({DURATION}s {RESOLUTION} {ASPECT}, audio); est ${DURATION * EST_USD_PER_SECOND:.2f}")
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / "request.json").write_text(json.dumps({"request_id": request_id, "model": MODEL}, indent=2), encoding="utf-8")

    final = hf_api.wait(sub["status_url"], on_tick=lambda s, t: print(f"  {t:>4}s  {s.get('status')}", flush=True))
    step = {"model": MODEL, "prompt": PROMPT, "duration": DURATION, "resolution": RESOLUTION,
            "aspect_ratio": ASPECT, "generate_audio": True, "request_id": request_id, "status": final.get("status"),
            "cost_note": f"estimate at ${EST_USD_PER_SECOND}/s; confirm in open.higgsfield.ai billing"}
    if final.get("status") != "completed":
        step["error"] = final.get("error") or final
        # Rejected or failed jobs have been refunded so far; record $0 and check billing.
        recipe.add_step(CREATIVE_ID, "clip", step, usd=0.0)
        print(f"Generation ended with status {final.get('status')}: {str(step['error'])[:400]}")
        return 1

    video_url = (final.get("video") or {}).get("url")
    dest = FOLDER / "tryon_raw.mp4"
    hf_api.download(video_url, dest)
    step["video_url"] = video_url
    est_usd = round(DURATION * EST_USD_PER_SECOND, 2)
    recipe.add_step(CREATIVE_ID, "clip", step, usd=est_usd)
    recipe.finish(CREATIVE_ID, video_url=video_url, local_path=str(dest.relative_to(hd.HUB_ROOT)), status="REVIEW")
    print(f"Done: {dest} ({dest.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
