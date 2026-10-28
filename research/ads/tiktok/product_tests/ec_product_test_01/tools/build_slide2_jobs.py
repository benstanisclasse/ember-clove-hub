"""Write slide-2 picture jobs (one per ad) for the launch products, split into parallel parts.

Each job uses the ad's own slide-1 picture (uploaded) as the first reference so model, outfit and setting carry over,
plus the product's Shopify photos. Run from the Hub root:
  python -I research/ads/tiktok/product_tests/ec_product_test_01/tools/build_slide2_jobs.py
then run scripts/hf_image_batch.py on each slide2/_partN/jobs.json.
"""
import json
import os
import sys

sys.path.insert(0, "scripts")
import hf_api  # noqa: E402

G = "data/media_generated/tiktok_test_01"
REFS = json.load(open(f"{G}/refs/selected_refs.json"))
REFS["P005"] = json.load(open(f"{G}/cost_probe/jobs.json", encoding="utf-8"))["jobs"][0]["refs"]
STYLE = ("Photorealistic premium fashion advertising photo, vertical 9:16, natural light, true-to-life fabric and color, "
         "realistic skin texture. Late November in the US. The first reference image is the previous picture of this "
         "same ad: keep the same woman (face, hair), the same outfit and the same setting and light. The garment must "
         "match the product reference images exactly: same color, cut, length, details and hardware. Natural relaxed "
         "pose, legs uncrossed, anatomically correct arms, hands and fingers. No text, no logos, no watermarks, no brand "
         "labels, no coffee cups.")
SLIDE2 = {
    "P001_A": "Side profile of the same woman in the brown mock-neck dress on the same cream studio backdrop, showing the high mock neck and the fitted bodice with princess seams, full figure.",
    "P001_B": "The same woman at the same holiday dinner, seated at the decorated table laughing with friends (out of focus), the brown dress and its hip ring clearly visible.",
    "P001_C": "Close macro photo of the hip of the same brown dress: one small metal ring with the pleats fanning out from it, fabric texture sharp, cream studio light, no face in frame.",
    "P005_A": "Close-up of the burgundy coat's wide notch lapel and brushed wool-look texture on the same woman, chest and shoulders in frame, same cream studio backdrop.",
    "P005_B": "The same woman crossing the same November city street mid-stride, the long burgundy coat moving with her step, full body visible.",
    "P005_C": "The same woman on the same cream studio backdrop wearing the same burgundy coat open over a cream sweater and straight blue jeans with black ankle boots, full body visible.",
    "P006_A": "Close-up of the off-white cardigan's high stand collar and off-center dark buttons on the same woman, shoulder button tab visible, same cream studio backdrop.",
    "P006_B": "The same woman browsing shelves in a cozy independent bookshop, wearing the same off-white cardigan open over a white tee with blue jeans, three-quarter body visible.",
    "P006_C": "The same woman wearing the same off-white cardigan open over a simple black knit midi dress with black knee-high boots, on a late-November street, full body visible.",
    "P012_A": "The same beige knee-high boots worn by a woman, side view from the knee down on the same cream backdrop, showing the 2.8 inch block heel, the fold-over cuff and the row of brass snaps.",
    "P012_B": "The same woman sitting on stone steps on the same November street in the same caramel cable-knit midi dress, the front slit showing the beige boot shaft and brass snaps, full body visible.",
    "P012_C": "The same woman on the same cream backdrop wearing the same beige knee-high boots with skinny dark jeans tucked into the boots and a cream knit sweater, full body visible.",
    "P013_A": "Close-up of the caramel cable-knit dress's mock neck and vertical cable pattern on the same woman, chest to waist in frame, same cream studio backdrop.",
    "P013_B": "The same woman in the same caramel cable-knit midi dress opening the front door to greet guests in a warm decorated home, late-November evening, full body visible.",
    "P013_C": "Close-up of the front slit of the same caramel cable-knit midi dress opening over a black knee-high boot mid-stride, from the hip down, same street, the slit drawn exactly as in the reference.",
}

hero_urls = {}
for key in SLIDE2:
    hero_urls[key] = hf_api.upload(f"{G}/heroes/{key}.png")
jobs = [{"key": f"{k}_s2", "aspect": "9:16", "refs": [hero_urls[k]] + REFS[k[:4]][:4], "prompt": p}
        for k, p in SLIDE2.items()]
for n in range(5):
    d = f"{G}/slide2/_part{n}"
    os.makedirs(d, exist_ok=True)
    json.dump({"B": "", "style": STYLE, "jobs": jobs[n::5]}, open(f"{d}/jobs.json", "w", encoding="utf-8"), indent=1)
json.dump({"style": STYLE, "jobs": jobs}, open(f"{G}/slide2/jobs_all.json", "w", encoding="utf-8"), indent=1)
print(len(jobs), "slide-2 jobs in 5 parts")
