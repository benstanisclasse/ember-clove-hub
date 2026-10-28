"""Generate a UGC try-on ad with Seedance 2.5 reference-to-video (15 s, 720p, 9:16, generated audio).

Owner rule (2026-10-24): the generated video IS the ad — no post-production edits. Each ad is one SPECS entry.
References are face-free crops of store photos, so the presenter is AI-generated (label AI on TikTok).
Usage: python scripts/make_tryon.py <creative_id> --max-usd 6.50
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_api  # noqa: E402
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

MODEL = "bytedance/seedance-2.5/reference-to-video"
DURATION, RESOLUTION, ASPECT = 15, "720p", "9:16"
# EC-P01-A03 was billed $5.89 for 15 s at the 15%-off rate (~$0.393/s). Owner's discount is now 30% off,
# so expect ~$0.324/s (~$4.85 per 15 s). Confirm against billing after every run.
EST_USD_PER_SECOND = 0.324

from prompt_style import PRESENTER, REALISM  # noqa: E402

STYLE = (
    "Vertical 9:16 UGC-style fashion try-on video for social media, 15 seconds, four quick cuts, natural "
    "phone-camera look, bright warm apartment with wood floors, an arched mirror and soft daylight. The presenter is "
    f"{PRESENTER}, friendly and excited, speaking English directly to "
    "the camera. Clear natural speech, light room tone, no background music, no on-screen text, no logos. "
    # Added 2026-10-25: EC-P02-A05-H01-V02 generated a bag clasp resembling a designer logo.
    "All bags, shoes, jewelry and props are plain and unbranded, with no monograms or designer-style hardware. "
    # Added 2026-10-26 (owner): photorealistic people and settings, above all on cheaper models.
    + REALISM
)

SPECS = {
    "EC-P02-A03-H01-V01": {
        "experiment_id": "C1-P02-A03", "product_id": "gid://shopify/Product/9751655809263",
        "product": "Turtleneck Rib Knit Sweater Dress", "color": "Burgundy",
        "refs": ["assets/EC-P02-A03-H01-V01/ref1_dress_neck_down.jpg",
                 "assets/EC-P02-A03-H01-V01/ref2_turtleneck_knit_closeup.jpg"],
        "source_photo": "Shopify EB40AEBD79AAF3FECCF037153E856C2F.jpg (burgundy studio shot)",
        "dress": ("the exact burgundy chunky rib-knit turtleneck sweater dress from the reference images: loose "
                  "slouchy fit, folded turtleneck, dropped shoulders, long full sleeves with ribbed cuffs, ribbed hem, "
                  "mini length ending at mid-thigh. Keep its color, chunky rib knit, turtleneck and length identical "
                  "to the references."),
        "shots": [
            ("0-3 s", "wearing a casual white tee, she holds the burgundy sweater dress on a hanger up to the camera",
             "Okay, this sweater dress is so cozy."),
            ("3-7 s", "cut to her wearing it, mid-shot, folding the turtleneck down and pushing up the slouchy sleeves",
             "It's a slouchy turtleneck with dropped shoulders."),
            ("7-11 s", "cut to a full-length shot wearing it with opaque black tights and black knee-high boots; she "
             "does a little twirl", "Throw it on with tights and boots and you're done."),
            ("11-15 s", "she walks up to the camera into a smiling close-up",
             "Seven colors, sizes small to 3X. Link's right here."),
        ],
        "hook_type": "statement",
    },
}


# Cycle 1 test videos (Checkpoint C, research/tiktok/EMBER_CLOVE_CREATIVE_CONCEPTS.md). These replace the four
# never-generated V01 drafts written 2026-10-24.
from concept_specs_cycle1 import SPECS as CYCLE1_SPECS  # noqa: E402

SPECS.update(CYCLE1_SPECS)

def build_prompt(spec):
    style = STYLE.replace("bright warm apartment with wood floors, an arched mirror and soft daylight",
                          spec["setting"]) if spec.get("setting") else STYLE
    lines = [style, f"The dress in every shot is {spec['dress']}"]
    for i, (when, action, line) in enumerate(spec["shots"], start=1):
        lines.append(f'Shot {i} ({when}): {action}, saying: "{line}"')
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("creative_id")
    ap.add_argument("--max-usd", type=float, required=True)
    args = ap.parse_args()
    cid, spec = args.creative_id, SPECS[args.creative_id]
    est = round(DURATION * EST_USD_PER_SECOND, 2)
    if est > args.max_usd:
        sys.exit(f"Estimated ${est} exceeds the approved ${args.max_usd}; not submitting.")
    prompt = build_prompt(spec)
    refs = [hd.HUB_ROOT / p for p in spec["refs"]]

    if not recipe._recipe_path(cid).exists():
        recipe.new_creative(
            cid, experiment_id=spec["experiment_id"], product_id=spec["product_id"], length_s=DURATION,
            resolution=RESOLUTION, source="higgsfield-api", hook_text=spec["shots"][0][2],
            format="try-on", hook_type=spec["hook_type"], opening_visual=spec.get("opening_visual", "creator-face"),
            setting="living-room", creator="on-camera", on_screen_text="none", voice="on-camera", pace_cuts_per_15s=3,
        )
        recipe.add_step(cid, "concept", {"angle": spec.get("angle", "UGC try-on haul"), "icp": spec.get("icp"),
                                          "product": spec["product"], "color": spec["color"],
                                          "notes": "AI-generated presenter; label AI on TikTok; no testimonial or purchase claims; no post-production"})
        recipe.add_step(cid, "product_reference", {"references": spec["refs"], "source_photo": spec["source_photo"],
                                                    "processing": "cropped below the chin to exclude the supplier model's face"})
        recipe.add_step(cid, "script", {"lines": [s[2] for s in spec["shots"]]})

    urls = [hf_api.upload(p) for p in refs]
    payload = {"prompt": prompt, "image_urls": urls, "duration": DURATION, "resolution": RESOLUTION,
               "aspect_ratio": ASPECT, "output_format": "mp4", "generate_audio": True}
    sub = hf_api.submit(MODEL, payload)
    request_id = sub.get("request_id")
    print(f"Submitted {MODEL} request {request_id} for {cid}; est ${est} (cap ${args.max_usd})", flush=True)
    folder = hd.ASSETS / cid
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "request.json").write_text(json.dumps({"request_id": request_id, "model": MODEL}, indent=2), encoding="utf-8")

    final = hf_api.wait(sub["status_url"], on_tick=lambda s, t: print(f"  {t:>4}s  {s.get('status')}", flush=True))
    step = {"model": MODEL, "prompt": prompt, "duration": DURATION, "resolution": RESOLUTION, "aspect_ratio": ASPECT,
            "generate_audio": True, "request_id": request_id, "status": final.get("status"),
            "cost_note": f"estimate ${est} at ${EST_USD_PER_SECOND}/s; replace with the billed amount"}
    if final.get("status") != "completed":
        step["error"] = final.get("error") or final
        recipe.add_step(cid, "clip", step, usd=0.0)
        print(f"Generation ended with status {final.get('status')}: {str(step['error'])[:400]}")
        return 1
    video_url = (final.get("video") or {}).get("url")
    dest = folder / "tryon_raw.mp4"
    hf_api.download(video_url, dest)
    step["video_url"] = video_url
    recipe.add_step(cid, "clip", step, usd=est)
    recipe.finish(cid, video_url=video_url, local_path=str(dest.relative_to(hd.HUB_ROOT)), status="REVIEW")
    print(f"Done: {dest} ({dest.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
