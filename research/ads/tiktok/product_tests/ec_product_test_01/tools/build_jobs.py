"""Write the Phase C hero-image job file (one slide-1 picture per concept) for scripts/hf_image_batch.py."""
import json

REFS = json.load(open("data/media_generated/tiktok_test_01/refs/selected_refs.json"))
STYLE = ("Photorealistic premium fashion advertising photo, vertical 9:16, natural light, true-to-life fabric and color, "
         "realistic skin texture. Late November in the US (autumn turning to winter). The garment must match the reference "
         "images exactly: same color, cut, length, details and hardware; do not invent or remove any detail. Natural relaxed "
         "pose, legs uncrossed, both feet naturally placed, anatomically correct arms, hands and fingers. Keep the top fifth "
         "of the frame calm (plain background or sky) for a headline. No text, no logos, no watermarks, no brand labels, "
         "no coffee cups.")
STUDIO = "Plain warm cream seamless studio backdrop (#F4E9DA tone), soft even light, nothing else in frame."

# per product: garment description from the Shopify page, and one fictional model used in all three concepts
P = {
    "P001": ("the brown sleeveless mini dress from the references: high mock neck, fitted bodice with princess seams, "
             "sculpted pleats that flare out from a small metal ring at each hip, smooth matte polyester, above-knee length",
             "a fictional woman in her late 20s with a sleek dark low bun"),
    "P003": ("the black blazer mini dress from the references: structured suiting, puffed shoulders, notch lapels, "
             "single-breasted black buttons, flap pockets, long sleeves, fitted waist, red 3D fabric roses on long green "
             "stems climbing the front exactly as placed in the references",
             "a fictional woman in her early 30s with shoulder-length straight black hair"),
    "P006": ("the off-white chunky rib-knit cardigan from the references: high stand collar that buttons off-center, "
             "small button tabs on the shoulders, full button front with dark buttons, loose fit, dropped shoulders, "
             "banded hem at the hip, long sleeves",
             "a fictional woman in her early 30s with wavy auburn shoulder-length hair"),
    "P007": ("the camel faux suede blazer from the references: relaxed fit, notch lapels, yoke seam across the chest, "
             "three-button front, flap hip pockets, long sleeves, hip length, matte suede texture",
             "a fictional woman in her late 20s with a light brown curtain-bang bob"),
    "P009": ("the camel utility zip jacket from the references: canvas-look shell, full front zip, dark brown contrast "
             "collar, drawstring hood lined with plush dark fleece, zip chest pocket, slant side pockets, hip length, "
             "worn as a relaxed oversized fit on a woman",
             "a fictional woman in her mid 30s with a dark blonde ponytail"),
    "P011": ("the black faux leather moto jacket from the references: smooth PU with a soft sheen, snap-tab stand collar, "
             "center zip, zip chest pocket, zip side pockets, shaped seams through the waist, fitted hip length, long sleeves",
             "a fictional woman in her late 20s with a sharp jaw-length platinum-blonde bob"),
    "P012": ("the beige knee-high boots from the references: smooth faux leather, wide fold-over cuff at the top with a "
             "vertical row of small brass snap buttons, 2.8 inch block heel, rounded toe, about 14 inch shaft",
             "a fictional woman in her early 30s"),
    "P013": ("the caramel cable-knit sweater dress from the references: mock neck, long sleeves, ribbed waist, fitted "
             "through the hip, midi length to mid-calf, front slit from the hem, vertical cable pattern",
             "a fictional woman in her early 30s with long chestnut hair worn loose"),
    "P014": ("the navy and bright green wide-striped knit sweater from the references: open polo collar in navy, relaxed "
             "fit with dropped shoulders, ribbed cuffs and hem, long sleeves; stripes alternate navy and green exactly "
             "as in the reference",
             "a fictional woman in her late 20s with short curly dark hair"),
}

JOBS = {
    "P001": {
        "A": f"{STUDIO} Three-quarter-length shot of {{model}} standing in {{g}}, face turned slightly away, the dress filling most of the frame, the hip pleats and metal rings clearly visible.",
        "B": "Evening holiday dinner in a warm restaurant with soft string lights and a decorated table, {model} standing by the table wearing {g} with sheer black tights and black knee-high boots, smiling, full body visible.",
        "C": "Close macro photo of the hip of {g}: one small metal ring with the pleats fanning out from it, the brown fabric texture sharp, part of the fitted bodice visible, warm cream studio light.",
    },
    "P003": {
        "A": f"{STUDIO} Full-length shot of {{model}} wearing {{g}} with sheer black tights and black heels, standing straight, roses fully visible.",
        "B": "Office holiday party in the evening, warm lights and a subtle decorated tree in the background, {model} wearing {g} with sheer black tights and black heels, holding a glass of sparkling water, smiling at colleagues out of focus, full body visible.",
        "C": "Close detail photo of {g} on a woman: the red 3D fabric roses on long green stems against the black suiting, the notch lapel and black buttons in frame, soft warm light.",
    },
    "P006": {
        "A": f"{STUDIO} Waist-up shot of {{model}} wearing {{g}} buttoned, over a plain cream top, the chunky rib texture, stand collar and shoulder button tabs filling most of the frame.",
        "B": "Saturday morning at an outdoor farmers market in late November, bare trees, crates of apples and squash, {model} wearing {g} open over a white tee with straight blue jeans, carrying a canvas tote, three-quarter body visible.",
        "C": "Outdoors on a crisp late-November street, {model} wearing {g} fully buttoned up with the stand collar closed at the neck like a jacket, black trousers, hands relaxed, three-quarter body visible.",
    },
    "P007": {
        "A": f"{STUDIO} Three-quarter-length shot of {{model}} wearing {{g}} open over a black turtleneck, the suede texture, lapels and yoke seam clearly visible.",
        "B": "Late-November city street with brick shop fronts and bare trees, {model} walking in {g} over a black turtleneck and straight blue jeans with brown loafers, full body visible.",
        "C": f"{STUDIO} Full-body outfit photo of {{model}}: {{g}} worn open over a black ribbed turtleneck with straight light-blue jeans and brown loafers, standing naturally, the three pieces clearly readable as one outfit.",
    },
    "P009": {
        "A": f"{STUDIO} Three-quarter-length shot of {{model}} wearing {{g}} unzipped over a gray knit, hood down so the plush fleece lining shows, collar and chest pocket clearly visible.",
        "B": "Frosty late-November morning in a park, pale sun, frost on the grass, {model} walking a golden retriever on a leash, wearing {g} zipped halfway over a gray knit with dark jeans and boots, full body visible.",
        "C": "Close detail photo of {g}: the hood folded open to show the plush dark fleece lining, the dark brown contrast collar and the zip, soft daylight, product filling the frame.",
    },
    "P011": {
        "A": f"{STUDIO} Three-quarter-length shot of {{model}} wearing {{g}} zipped up, with black straight trousers, the snap-tab collar and zip pockets clearly visible.",
        "B": "Evening downtown street in late November, warm shop lights and a restaurant entrance, {model} wearing {g} open over a caramel cable-knit midi dress with black knee-high boots, full body visible.",
        "C": f"{STUDIO} Full-body outfit photo of {{model}} wearing {{g}} open over a caramel cable-knit midi sweater dress with black knee-high boots, standing naturally.",
    },
    "P012": {
        "A": f"{STUDIO} Photo from the knees down of {{model}} standing in {{g}}, under a black wool-look midi skirt hem, the fold-over cuff and brass snaps in sharp focus.",
        "B": "Late-November city sidewalk with fallen leaves, {model} walking in {g} with a caramel cable-knit midi sweater dress whose front slit shows the boot shaft, full body visible.",
        "C": f"{STUDIO} Full-body photo of {{model}} wearing {{g}} with a black mini skirt, sheer black tights and a cream knit sweater, standing naturally, boots clearly visible.",
    },
    "P013": {
        "A": f"{STUDIO} Full-length shot of {{model}} wearing {{g}} with black knee-high boots, standing naturally, the cable knit and midi length clearly visible.",
        "B": "Warm family holiday dinner at home in late November, candles and a set table, {model} standing beside the table wearing {g} with black knee-high boots, smiling, full body visible.",
        "C": "Late-November city sidewalk, {model} mid-stride in {g}, the front slit opening naturally over black knee-high boots, full body visible, the slit drawn exactly as in the reference.",
    },
    "P014": {
        "A": f"{STUDIO} Waist-up shot of {{model}} wearing {{g}}, the stripes and open polo collar filling most of the frame.",
        "B": "Weekend late-November morning on a neighborhood street with bare trees, {model} walking in {g} with straight blue jeans and brown loafers, carrying a small bunch of flowers, full body visible.",
        "C": f"{STUDIO} Full-body outfit photo of {{model}} wearing {{g}} tucked into a black midi skirt with black knee-high boots, standing naturally.",
    },
}

jobs = []
for pid, concepts in JOBS.items():
    g, model = P[pid]
    for c, tmpl in concepts.items():
        jobs.append({"key": f"{pid}_{c}", "aspect": "9:16", "refs": REFS[pid],
                     "prompt": tmpl.format(model=model, g=g)})
spec = {"B": "", "style": STYLE, "jobs": jobs}
json.dump(spec, open("data/media_generated/tiktok_test_01/heroes/jobs.json", "w", encoding="utf-8"), indent=1)
print(len(jobs), "jobs")
