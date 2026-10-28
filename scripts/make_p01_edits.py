"""Finish the four P01 (Cable Knit Mock Neck Midi Dress) ads with text and an end card. No generation cost.

  EC-P01-A03-H01-V01  try-on (spoken hook), captions of the spoken lines, end card
  EC-P01-A03-H02-V01  same + on-screen hook text for the first 3 s (only change)
  EC-P01-A02-H01-V01  walking base, hook "POV: a sweater dress you can actually walk in", captions, end card
  EC-P01-A02-H02-V01  same with hook "The slit is the whole point." (only change)
Run: python scripts/make_p01_edits.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ad_edit  # noqa: E402
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

END_CARD = {"product": "Cable Knit Mock Neck Midi Dress", "price": "$52.99",
            "line1": "7 colors · Sizes S–XL", "line2": "Free US shipping over $70", "cta": "Shop now"}

TRYON_SRC = hd.ASSETS / "EC-P01-A03-H01-V01" / "tryon_raw.mp4"
WALK_SRC = hd.ASSETS / "EC-P01-A02-H01-V01" / "base_raw.mp4"

# Spoken lines, timed to the shots (cuts at ~3.0 s and ~12.0 s; fit check 3-7 s, walk 7-11.5 s).
TRYON_CAPTIONS = [
    (0.2, 2.9, "Okay, you need to see this sweater dress."),
    (3.0, 6.9, "It's cable knit, and it's fitted through the hips."),
    (7.0, 11.4, "And the slit means you can actually walk in it."),
    (11.5, 15.0, "It comes in seven colors. Link's right here."),
]
WALK_CAPTIONS = [
    (3.3, 7.4, "Cable knit, fitted at the hip"),
    (7.5, 12.0, "Front slit for a real stride"),
]

ADS = [
    {"id": "EC-P01-A03-H01-V01", "parent": None, "src": TRYON_SRC, "hook": None, "captions": TRYON_CAPTIONS},
    {"id": "EC-P01-A03-H02-V01", "parent": "EC-P01-A03-H01-V01", "src": TRYON_SRC,
     "hook": {"text": "The sweater dress you can actually walk in", "start": 0.0, "end": 3.0, "y": 205, "size": 40},
     "captions": TRYON_CAPTIONS},
    # Walking video: the face is at the top of frame, so the hook sits on the plain knit bodice instead.
    {"id": "EC-P01-A02-H01-V01", "parent": None, "src": WALK_SRC,
     "hook": {"text": "POV: a sweater dress you can actually walk in", "start": 0.0, "end": 3.2, "y": 560, "size": 46},
     "captions": WALK_CAPTIONS},
    {"id": "EC-P01-A02-H02-V01", "parent": "EC-P01-A02-H01-V01", "src": WALK_SRC,
     "hook": {"text": "The slit is the whole point.", "start": 0.0, "end": 3.2, "y": 560, "size": 46},
     "captions": WALK_CAPTIONS},
]


def main():
    out_dir = hd.ASSETS / "final"
    out_dir.mkdir(parents=True, exist_ok=True)
    for ad in ADS:
        cid = ad["id"]
        hook_text = ad["hook"]["text"] if ad["hook"] else None
        if ad["parent"] and not recipe._recipe_path(cid).exists():
            recipe.duplicate(ad["parent"], cid, "hook_text", hook_text)
        elif not ad["parent"] and hook_text:
            r = recipe.load(cid)
            r["hook_text"] = hook_text
            with open(recipe._recipe_path(cid), "w", encoding="utf-8") as f:
                json.dump(r, f, indent=2, ensure_ascii=False)
        dest = out_dir / f"{cid}.mp4"
        info = ad_edit.render_ad(ad["src"], dest, hook=ad["hook"], captions=ad["captions"], end_card_spec=END_CARD)
        recipe.add_step(cid, "post_production", {
            "tool": "ffmpeg 7.1 (imageio-ffmpeg) + Pillow, scripts/ad_edit.py",
            "source_video": str(Path(ad["src"]).relative_to(hd.HUB_ROOT)),
            "hook_overlay": ad["hook"], "captions": ad["captions"], "end_card": END_CARD, **info,
            "music": "none in file; add from TikTok commercial music library at ad creation",
        })
        recipe.finish(cid, local_path=str(dest.relative_to(hd.HUB_ROOT)), status="REVIEW")
        hd.log(f"{cid}: edited ad rendered ({info['total_seconds']}s incl. {info['end_card_seconds']}s end card), awaiting owner review")
        print(f"{cid}: {dest.name} {info['total_seconds']}s")


if __name__ == "__main__":
    main()
