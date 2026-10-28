import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
Q = r"C:\Users\Administrator\AppData\Local\Temp\ec_q"
rows = json.load(open(Q + r"\tool\rows2.json", encoding="utf-8"))
rev = [r for r in rows if r["review"]]
C, TH, PER, COLS = 360, 120, 7, 4
font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 15)
def best_crop(im):
    g = np.asarray(im.convert("L"), dtype=np.float32)
    lap = np.abs(np.asarray(im.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32))
    h, w = g.shape; cw, ch = min(C, w), min(C, h)
    best, bx, by = -1, 0, 0
    step = 40
    # integral image of lap
    ii = np.pad(lap.cumsum(0).cumsum(1), ((1,0),(1,0)))
    for y in range(0, h - ch + 1, step):
        for x in range(0, w - cw + 1, step):
            s = ii[y+ch, x+cw] - ii[y, x+cw] - ii[y+ch, x] + ii[y, x]
            if s > best: best, bx, by = s, x, y
    return im.crop((bx, by, bx + cw, by + ch))
def cell(r, ref=False):
    im = Image.open(f'{Q}\\all\\{r["name"]}.jpg').convert("RGB")
    c = Image.new("RGB", (C, C + TH + 10), "white")
    c.paste(best_crop(im), (0, 0))
    t = im.copy(); t.thumbnail((TH, TH)); c.paste(t, (0, C + 5))
    d = ImageDraw.Draw(c)
    lines = [("REF BAD cardigan" if ref else r["name"]) + f' pos{r["pos"]}', f'{r["aw"]}x{r["ah"]} {r["kb"]}KB', f'p90={r["p90"]:.0f} d={r["detail"]:.2f}', r["title"][:22]]
    for i, l in enumerate(lines): d.text((TH + 10, C + 8 + i * 20), l, fill="red" if ref else "black", font=font)
    return c
ref = next(r for r in rows if r["name"] == "i461")
sheets = [rev[i:i+PER] for i in range(0, len(rev), PER)]
idx = []
for k, sh in enumerate(sheets):
    S = Image.new("RGB", (COLS * C + (COLS-1)*6, 2 * (C + TH + 10) + 6), (120,120,120))
    for j, r in enumerate([ref] + sh if True else sh):
        S.paste(cell(r, ref=(j == 0)), ((j % COLS) * (C + 6), (j // COLS) * (C + TH + 16)))
    S.save(f"{Q}\\sh\\s{k:02d}.png")
    idx.append((k, [r["name"] for r in sh]))
for k, n in idx: print(k, " ".join(n))
