"""Build the Ember & Clove 1200x628 social sharing card (Open Graph image)."""

import io
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

PHOTO_URL = "https://cdn.shopify.com/s/files/1/0845/4665/0351/files/WP5A0504.jpg?v=1792762799"
FONTS = "C:/Windows/Fonts/"
W, H = 1200, 628
PHOTO_W = 560
CLOVE, CREAM, SAND, ACCENT = "#3B2418", "#FBF6EF", "#F1E6D8", "#E8A27A"

out_path = sys.argv[1]

photo = Image.open(io.BytesIO(urllib.request.urlopen(PHOTO_URL, timeout=30).read())).convert("RGB")
scale = max(PHOTO_W / photo.width, H / photo.height)
photo = photo.resize((round(photo.width * scale), round(photo.height * scale)), Image.LANCZOS)
left = (photo.width - PHOTO_W) // 2
photo = photo.crop((left, 0, left + PHOTO_W, H))

card = Image.new("RGB", (W, H), CLOVE)
card.paste(photo, (0, 0))
draw = ImageDraw.Draw(card)

panel_left = PHOTO_W
cx = panel_left + (W - panel_left) // 2
max_text_w = W - panel_left - 80


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS + name, size)


def spaced(text: str, f: ImageFont.FreeTypeFont, tracking: int) -> int:
    return sum(draw.textlength(ch, font=f) for ch in text) + tracking * (len(text) - 1)


def draw_spaced(text: str, f: ImageFont.FreeTypeFont, tracking: int, y: int, fill: str) -> None:
    x = cx - spaced(text, f, tracking) / 2
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking


eyebrow_f = font("georgiab.ttf", 17)
size = 76
name_f = font("georgiab.ttf", size)
while draw.textlength("Ember & Clove", font=name_f) > max_text_w:
    size -= 2
    name_f = font("georgiab.ttf", size)
tag_f = font("georgiai.ttf", 30)

name_box = draw.textbbox((0, 0), "Ember & Clove", font=name_f)
name_h = name_box[3] - name_box[1]
block_h = 17 + 28 + name_h + 40 + 30
y = (H - block_h) // 2

draw_spaced("SMALL-BATCH RITUALS", eyebrow_f, 4, y, ACCENT)
y += 17 + 28
name_w = draw.textlength("Ember & Clove", font=name_f)
draw.text((cx - name_w / 2, y - name_box[1]), "Ember & Clove", font=name_f, fill=CREAM)
y += name_h + 20

# Ornament: line, dot, line.
draw.line((cx - 60, y, cx - 12, y), fill=ACCENT, width=2)
draw.ellipse((cx - 4, y - 4, cx + 4, y + 4), fill=ACCENT)
draw.line((cx + 12, y, cx + 60, y), fill=ACCENT, width=2)
y += 20

tag = "Warm rituals for everyday wellness"
draw.text((cx - draw.textlength(tag, font=tag_f) / 2, y), tag, font=tag_f, fill=SAND)

card.save(out_path, "PNG", optimize=True)
print("saved", out_path, card.size)
