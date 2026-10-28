"""Detailed video elements: room, presenter look, jewelry, styling, props, lighting, camera, actions.

A vision model reads each video's frame sheet (0, 1, 2, 3 s, then every 3 s) and fills the ELEMENTS form.
  --study  every video in kalodata.db table video_features -> table video_elements (for the winners-vs-stalled study)
  --ours   our own creatives with a local video -> recipe["elements"]["observed"] (via recipe.set_elements)
Race and ethnicity are deliberately not tagged. Age group and hair are perceived, approximate.
Run: OPENROUTER_API_KEY must be set (secrets.openrouter_api).
  python scripts/video_elements.py --study
  python scripts/video_elements.py --ours EC-P01-A05-H01-V03 EC-P02-A06-H01-V02 ...
"""
import argparse
import base64
import datetime as dt
import json
import sqlite3
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hub_env  # noqa: E402
import hubdata as hd  # noqa: E402
import kalodata_db  # noqa: E402
import recipe  # noqa: E402
import video_pilot as vp  # noqa: E402

MODEL = "anthropic/claude-haiku-5.5"
BACKUPS = ["google/gemini-3.1-flash-lite", "google/gemini-2.5-flash-lite"]
ELEMENTS = {
    "room": "main location, one of: bedroom, closet_dressing_room, living_room, kitchen, bathroom, home_office, "
            "hallway_entry, outdoors_street, outdoors_nature, store, car, gym, plain_studio_backdrop, other",
    "lighting": "one of: natural_daylight, warm_indoor_lamps, ring_or_studio_light, night_or_dim, mixed",
    "presenter_count": "number of people clearly featured (0, 1, 2, 3+)",
    "presenter_presents_as": "main presenter: woman, man, mixed_group, none",
    "age_group": "main presenter's apparent age group: under_25, 25_40, over_40, unclear, none",
    "hair_color": "main presenter: black, brown, blonde, red, gray_white, dyed_bright, covered, none",
    "hair_length": "main presenter: short, shoulder, long, covered, none",
    "jewelry": "list of visible jewelry: hoop_earrings, stud_earrings, necklace, rings, bracelet, watch, none",
    "makeup": "main presenter: natural_or_none, moderate, full_glam, not_visible",
    "nails_done": "true/false/not_visible: manicured or polished nails",
    "glasses": "true/false",
    "worn_with": "list of items worn with the product: boots, sneakers, heels, sandals, tights, jeans, jacket_coat, "
                 "bag, hat, scarf, none",
    "color_palette": "overall palette: neutral_earth, black_white, bright_bold, pastel, mixed",
    "props": "list of notable props: mirror, mug_or_drink, bag, plants, pet, phone, packaging_box, food, "
             "furniture_in_use, product_alternatives, none",
    "camera_style": "one of: selfie_handheld, filmed_by_someone_handheld, tripod_static, mirror_selfie, mixed",
    "main_shot_distance": "one of: close_up, medium, full_length, mixed",
    "camera_movement": "one of: static, slight, lots",
    "actions": "list of: walking, turning_twirling, sitting_lying, posing, hand_detail, putting_on_product, "
               "using_product, unboxing, talking_to_camera, cooking_or_cleaning, exercising",
    "background_people": "true/false: other people visible in the background",
    "visual_quality": "one of: sharp_well_lit, average, dark_or_blurry",
}


def tag_elements(sheet, meta):
    prompt = ("You are cataloguing visible elements of a short product video for marketing research. The image is a "
              "contact sheet of frames labelled with their time (0s, 1s, 2s, 3s, then every 3 s). Product category: "
              f"{meta.get('category', '')}. Describe only what is visible; use 'none', 'unclear' or 'not_visible' "
              "rather than guessing. Do not infer race or ethnicity. Return ONLY a JSON object with exactly these "
              "keys:\n" + json.dumps(ELEMENTS, indent=1))
    img = base64.b64encode(Path(sheet).read_bytes()).decode()
    body = {"model": MODEL, "models": [MODEL] + BACKUPS, "temperature": 0, "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}]}]}
    for attempt in range(4):
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", timeout=120, json=body,
                          headers={"Authorization": f"Bearer {hub_env.get_secret('openrouter_api')}"})
        if r.status_code != 429:
            break
        time.sleep(20 * (attempt + 1))
    if r.status_code == 403:
        raise SystemExit(f"OpenRouter refused the call: {r.text[:200]}")
    r.raise_for_status()
    out = r.json()
    text = out["choices"][0]["message"]["content"].strip().removeprefix("```json").removesuffix("```")
    return json.loads(text), (out.get("usage") or {}).get("cost") or 0


def run_study():
    con = sqlite3.connect(kalodata_db.DB)
    con.execute("CREATE TABLE IF NOT EXISTS video_elements (video_id TEXT PRIMARY KEY, elements_json TEXT, "
                "model TEXT, created_at TEXT)")
    done = {r[0] for r in con.execute("SELECT video_id FROM video_elements")}
    rows = con.execute("SELECT video_id, category FROM video_features").fetchall()
    cost = 0.0
    for i, (vid, cat) in enumerate(rows, 1):
        sheet = vp.VIDEOS / vid / "sheet.jpg"
        if vid in done or not sheet.exists():
            continue
        try:
            el, c = tag_elements(sheet, {"category": cat})
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"  {vid}: skipped ({type(e).__name__})")
            continue
        cost += c
        con.execute("INSERT OR REPLACE INTO video_elements VALUES (?,?,?,?)",
                    (vid, json.dumps(el, ensure_ascii=False), MODEL, dt.datetime.now().isoformat(timespec="seconds")))
        con.commit()
        if i % 20 == 0:
            print(f"  {i}/{len(rows)} done, ${cost:.3f}", flush=True)
    print(f"Study elements done: ${cost:.3f}")


def run_ours(ids):
    cost = 0.0
    for cid in ids:
        rec = recipe.load(cid)
        folder = hd.ASSETS / cid
        video = next((p for p in (folder / f"{cid}_tiktok.mp4", folder / "tryon_raw.mp4") if p.exists()), None)
        if video is None:
            print(f"  {cid}: no local video")
            continue
        sheet = folder / "study_sheet.jpg"
        if not sheet.exists():
            words, duration = vp.transcribe(video, _whisper())
            vp.frame_sheet(video, duration, sheet)
        el, c = tag_elements(sheet, {"category": "Womenswear & Underwear"})
        cost += c
        recipe.set_elements(cid, dict(el, model=MODEL), "observed")
        print(f"  {cid}: {el.get('room')} | {el.get('hair_color')} {el.get('hair_length')} | "
              f"jewelry {el.get('jewelry')} | with {el.get('worn_with')} | {el.get('lighting')}", flush=True)
    print(f"Our elements done: ${cost:.3f}")


_W = None


def _whisper():
    global _W
    if _W is None:
        from faster_whisper import WhisperModel
        _W = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
    return _W


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", action="store_true")
    ap.add_argument("--ours", nargs="*")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if args.ours:
        run_ours(args.ours)
    if args.study:
        run_study()


if __name__ == "__main__":
    main()
