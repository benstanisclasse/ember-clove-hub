"""Phase C: headline overlay on each hero (1080x1920), product contact sheets, overview sheet, manifest with hashes."""
import csv
import hashlib
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

T = Path("research/ads/tiktok/product_tests/ec_product_test_01")
G = Path("data/media_generated/tiktok_test_01")
HERO, OUT, SHEETS = G / "heroes", G / "prototypes", G / "review_sheets"
OUT.mkdir(parents=True, exist_ok=True)
SHEETS.mkdir(parents=True, exist_ok=True)
CREAM, INK, GRAY, TERRA = (244, 233, 218), (43, 37, 34), (111, 102, 95), (181, 83, 46)
FONT = "C:/Windows/Fonts/"
head_f = ImageFont.truetype(FONT + "georgiab.ttf", 72)
tag_f = ImageFont.truetype(FONT + "arial.ttf", 30)
W, H = 1080, 1920

rows = list(csv.DictReader(open(T / "creative_matrix.csv", encoding="utf-8")))
prods = {p["test_product_id"]: p for p in json.load(open(T / "products.json", encoding="utf-8"))["products"]}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fit(img):
    """Scale to cover 1080x1920 and center-crop."""
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def overlay(src, headline):
    img = fit(Image.open(src).convert("RGB"))
    global head_f
    probe = ImageDraw.Draw(img)
    for size in (58,):  # one size for the whole set; one line if it fits the safe width, else two balanced lines
        f = ImageFont.truetype(FONT + "georgiab.ttf", size)
        if probe.textlength(headline, font=f) <= 900:
            head_f, lines = f, [headline]
            break
    else:
        head_f = ImageFont.truetype(FONT + "georgiab.ttf", 58)
        lines = textwrap.wrap(headline, 20)
        for w in range(20, 8, -1):  # balance: the narrowest wrap that keeps the same line count
            if len(textwrap.wrap(headline, w)) == len(lines):
                best = textwrap.wrap(headline, w)
            else:
                break
        lines = best
    top = 175  # in the empty top band the pictures are framed with, below TikTok's top tabs
    lh = int(head_f.size * 1.17)
    zone = img.crop((120, top - 30, W - 120, top + lh * len(lines) + 70))
    bright = sum(ImageStat.Stat(zone.convert("L")).mean) > 165
    d = ImageDraw.Draw(img, "RGBA")
    if not bright:  # soft ink gradient behind cream text
        for i in range(0, top + lh * len(lines) + 160):
            a = int(120 * max(0, 1 - i / (top + lh * len(lines) + 160)))
            d.line([(0, i), (W, i)], fill=(*INK, a))
    color = INK if bright else CREAM
    y = top
    for ln in lines:
        w = d.textlength(ln, font=head_f)
        d.text(((W - w) / 2, y), ln, font=head_f, fill=color)
        y += lh
    # no disclosure text on the picture (owner 2026-10-28): it goes in TikTok's AI label and the caption
    return img


prev = {m["ad_name"]: m for m in json.load(open(T / "prototypes_manifest.json", encoding="utf-8"))}     if (T / "prototypes_manifest.json").exists() else {}
manifest = []
for r in rows:
    key = f"{r['product_id']}_{r['concept'][0]}"
    src = HERO / f"{key}.png"
    if not src.exists():
        print("missing", key)
        continue
    p0 = prev.get(r["ad_name"], {})
    version = p0.get("version", 1)
    img = overlay(src, r["slide1_headline"])
    if p0 and (p0.get("headline") != r["slide1_headline"] or p0.get("raw_sha256") != sha(src)):
        version += 1  # changed text or picture: new version, earlier approval no longer applies
    out = OUT / f"{r['ad_name']}_hero_v{version}.jpg"
    if not out.exists() or version != p0.get("version"):
        img.save(out, quality=92)
    manifest.append({"ad_name": r["ad_name"], "experiment_id": r["experiment_id"], "product_id": r["product_id"],
                     "concept": r["concept"], "raw_image": str(src).replace("\\", "/"), "raw_sha256": sha(src),
                     "prototype": str(out).replace("\\", "/"), "prototype_sha256": sha(out), "version": version,
                     "headline": r["slide1_headline"], "caption": r["caption"], "status": "awaiting_review"})

# product contact sheets: 3 concepts side by side with hypothesis and copy
f_t = ImageFont.truetype(FONT + "georgiab.ttf", 40)
f_b = ImageFont.truetype(FONT + "arialbd.ttf", 24)
f_s = ImageFont.truetype(FONT + "arial.ttf", 21)
cw, ch = 540, 960
by_pid = {}
for m in manifest:
    by_pid.setdefault(m["product_id"], []).append(m)
for pid, ms in by_pid.items():
    p = prods[pid]
    e = p["economics"]
    sheet = Image.new("RGB", (cw * 3 + 80, ch + 520), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((40, 24), f"{pid}  {p['title'][:60]}", font=f_t, fill=INK)
    d.text((40, 80), f"${p['price']:.2f}  |  break-even CPA ${e['breakeven_cpa']:.2f}  |  kept at $20 CPA ${e['kept_after_20_cpa']:.2f}  |  {p['url'][:80]}",
           font=f_s, fill=GRAY)
    for i, m in enumerate(sorted(ms, key=lambda x: x["concept"])):
        x = 20 + i * (cw + 20)
        sheet.paste(Image.open(m["prototype"]).resize((cw, ch)), (x, 130))
        r = next(r for r in rows if r["ad_name"] == m["ad_name"])
        y = 130 + ch + 14
        d.text((x, y), f"{r['concept']}  —  {r['motivation']}", font=f_b, fill=TERRA)
        y += 34
        for label, text in (("Tests", r["expected_learning"]), ("Caption", r["caption"])):
            for j, ln in enumerate(textwrap.wrap(f"{label}: {text}", 46)):
                d.text((x, y), ln, font=f_s, fill=INK)
                y += 26
            y += 8
        d.text((x, y), m["ad_name"], font=f_s, fill=GRAY)
    sheet.save(SHEETS / f"{pid}_contact_sheet.jpg", quality=88)

# overview: all concepts, one row per product
tw, th = 216, 384
ov = Image.new("RGB", (40 + 2 * (3 * (tw + 12) + 300), 90 + 5 * (th + 70)), CREAM)
d = ImageDraw.Draw(ov)
d.text((20, 20), "Ember & Clove — TikTok image test 01: 30 concept prototypes (A product | B lifestyle | C benefit)", font=f_b, fill=INK)
for n, pid in enumerate(sorted(by_pid)):
    col, row = divmod(n, 5)
    x0, y0 = 20 + col * (3 * (tw + 12) + 300), 70 + row * (th + 70)
    d.text((x0, y0), f"{pid} {prods[pid]['title'][:40]}", font=f_s, fill=INK)
    for i, m in enumerate(sorted(by_pid[pid], key=lambda x: x["concept"])):
        ov.paste(Image.open(m["prototype"]).resize((tw, th)), (x0 + i * (tw + 12), y0 + 30))
ov.save(SHEETS / "overview_30.jpg", quality=85)
json.dump(manifest, open(T / "prototypes_manifest.json", "w", encoding="utf-8"), indent=1)
print(len(manifest), "prototypes;", len(by_pid), "contact sheets")
