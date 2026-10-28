"""One-off: add the night-out world spots, series, wardrobe day/night tags and night store pieces (owner 2026-10-26)."""
import re
from pathlib import Path

HUB = Path(r"C:\Users\Administrator\Documents\EmberClove-Hub")
BIBLE = HUB / "studio" / "bible"


def to_draft(text):
    for k, v in (("status", "draft"), ("approved_by", "null"), ("approved_at", "null")):
        text = re.sub(rf"^{k}: .*$", f"{k}: {v}", text, count=1, flags=re.M)
    return re.sub(r"^approved_hash: .*\n", "", text, count=1, flags=re.M)


# world: two night spots
w = BIBLE / "world.yaml"
t = w.read_text(encoding="utf-8")
anchor = "props:"
assert anchor in t and "night-street" not in t
t = t.replace(anchor, '''  # Night-out spots (owner 2026-10-26: "make some about going out at night to club ... show off different outfits")
  - id: night-street
    name: Downtown at night
    description: "a quiet downtown Minneapolis sidewalk at night beside an older red-brick building: a tall dark wooden door under a plain black awning lined with small warm bulbs, warm light glowing from tall curtained windows, wet pavement reflecting the lights"
    ref_images: [studio/refs/rooms/night-street.png]
    lighting: [night_street_lights]
    outdoor: true
  - id: club-lounge
    name: Club lounge
    description: "a dim lounge club at night: a dark velvet booth and a small round marble table with two cocktails, an exposed brick wall, warm amber wall lamps, a blurred dance floor with colored lights and out-of-focus people in the background"
    ref_images: [studio/refs/rooms/club-lounge.png]
    lighting: [dim_bar_lights]
''' + anchor, 1)
w.write_text(to_draft(t), encoding="utf-8")

# series: Night out, Fri and Sat at 19:30
s = BIBLE / "series.yaml"
t = s.read_text(encoding="utf-8")
anchor = "  # Off while rules.mix.product_share_max is 0"
assert anchor in t and "night-out" not in t
t = t.replace(anchor, '''  - id: night-out
    name: "Night out"
    pillar: value
    occasion: night               # night outfits (dressy pieces) and evening light; coat on outside
    premise: "getting ready and heading out for the night: the full look, the one choice that makes it a night outfit, and arriving"
    episode_title: "Night out {n}"
    rooms: [bedroom, night-street, club-lounge]
    cta: soft
    weekdays: [Fri, Sat]          # owner 2026-10-26: the 7:30pm slot, a couple of times a week
    slots: ["19:30"]
''' + anchor, 1)
s.write_text(to_draft(t), encoding="utf-8")

# wardrobe: day/night tags + night store pieces
DAY = {"tee-white", "sweatshirt-grey", "leggings-black", "sneakers-white", "tote-canvas", "beanie-cream", "puffer-cream",
       "jacket-denim", "shirt-oxford-blue", "top-striped-breton", "tank-ribbed-oat", "sweater-grey-crew", "cardigan-oat",
       "sweater-olive-cable", "sweater-cream-chunky", "trousers-camel", "skirt-denim-long", "loafers-black",
       "bag-brown-tote", "dress-grey-sweater-mini", "dress-brown-shirt", "jeans-straight-light",
       "ec-offshoulder-sweatshirt", "ec-cutout-cable-sweater", "ec-rib-button-cardigan", "ec-stripe-cardigan",
       "ec-stripe-polo-sweater", "ec-chunky-cardigan", "ec-ruffle-skirt", "ec-belted-shirt-dress",
       "ec-cateye-sunglasses-black", "ec-cateye-sunglasses-tortoise"}
NIGHT = {"dress-navy-slip"}
wd = BIBLE / "wardrobe.yaml"
lines = wd.read_text(encoding="utf-8").splitlines()
out, current = [], None
for line in lines:
    m = re.match(r"\s*- \{id: ([\w-]+),", line)
    if m and line.rstrip().endswith("}"):
        tag = "[day]" if m.group(1) in DAY else "[night]" if m.group(1) in NIGHT else None
        out.append(line.rstrip()[:-1] + f", occasion: {tag}}}" if tag else line)
        continue
    m = re.match(r"\s*- id: ([\w-]+)", line)
    if m:
        current = m.group(1)
    out.append(line)
    if current and re.match(r"\s+season: ", line):
        tag = "[day]" if current in DAY else "[night]" if current in NIGHT else None
        if tag:
            out.append(f"    occasion: {tag}")
        current = None
text = "\n".join(out) + "\n"
G = "gid://shopify/Product/"
text += f'''  # Night-out store pieces (owner 2026-10-26): only in night posts
  - id: ec-mesh-mini-dress-blue
    name: "Ruffle Hem Mesh Mini Dress"
    category: dress
    color: "peacock blue"
    season: [all]
    occasion: [night]
    store_product: "{G}9751655481583"
    reference_images: [studio/refs/store/mesh-mini-dress-blue.jpg]
    prompt_description: "a peacock-blue fitted mesh mini dress with a high round neck, long sheer bell sleeves ending in ruffled cuffs, and a double ruffle at the hem, mid-thigh length"
  - id: ec-mesh-mini-dress-tangerine
    name: "Ruffle Hem Mesh Mini Dress"
    category: dress
    color: "tangerine"
    season: [all]
    occasion: [night]
    store_product: "{G}9751655481583"
    reference_images: [studio/refs/store/mesh-mini-dress-tangerine.jpg]
    prompt_description: "a tangerine-orange fitted mesh mini dress with a high round neck, long sheer bell sleeves ending in ruffled cuffs, and a double ruffle at the hem, mid-thigh length"
  - id: ec-slingback-stilettos-black
    name: "Croc-Embossed Slingback Stiletto Sandals"
    category: shoes
    color: "black"
    season: [all]
    occasion: [night]
    store_product: "{G}9751717544175"
    reference_images: [studio/refs/store/stiletto-slingback-black.jpg]
    prompt_description: "black croc-embossed patent stiletto sandals with a pointed open toe, a thin slingback strap and a high thin heel"
  - id: ec-rose-stilettos-red
    name: "Rose Accent Strappy Stiletto Sandals"
    category: shoes
    color: "red"
    season: [all]
    occasion: [night]
    store_product: "{G}9751716823279"
    reference_images: [studio/refs/store/stiletto-rose-red.jpg]
    prompt_description: "red strappy stiletto sandals with thin straps that wrap up the ankle, a large red fabric rose on the front strap and another at the ankle, and a high thin heel"
'''
wd.write_text(to_draft(text), encoding="utf-8")
print("ok")
