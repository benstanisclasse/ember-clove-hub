import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
Q = r"C:\Users\Administrator\AppData\Local\Temp\ec_q"
rows = {r["name"]: r for r in json.load(open(Q + r"\tool\rows2.json", encoding="utf-8"))}
font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 18)
Z = 300
def region(im, mode):
    w, h = im.size
    if mode == "c":
        cx, cy = w // 2, int(h * 0.42)
        return (max(0, cx - Z//2), max(0, cy - Z//2), min(w, cx + Z//2), min(h, cy + Z//2))
    g = im.convert("L").filter(ImageFilter.FIND_EDGES)
    lap = np.asarray(g, dtype=np.float32)
    ii = np.pad(lap.cumsum(0).cumsum(1), ((1,0),(1,0)))
    cw, ch = min(Z, w), min(Z, h); best=(-1,0,0)
    for y in range(0, h-ch+1, 30):
        for x in range(0, w-cw+1, 30):
            s = ii[y+ch,x+cw]-ii[y,x+cw]-ii[y+ch,x]+ii[y,x]
            if s > best[0]: best=(s,x,y)
    _, x, y = best
    return (x, y, x+cw, y+ch)
def cell(name, mode):
    r = rows[name]; im = Image.open(f"{Q}\\all\\{name}.jpg").convert("RGB")
    c = im.crop(region(im, mode)); c = c.resize((c.width*2, c.height*2), Image.NEAREST)
    out = Image.new("RGB", (600, 630), "white"); out.paste(c, (0, 0))
    ImageDraw.Draw(out).text((5, 605), f'{name} pos{r["pos"]} {r["aw"]}x{r["ah"]} 2x zoom  {r["title"][:30]}', fill="red" if name=="i461" else "black", font=font)
    return out
items = [a.split(":") if ":" in a else (a, "d") for a in sys.argv[2:]]
S = Image.new("RGB", (1206, 1266), (120,120,120))
for j, (n, m) in enumerate([("i461","d")] + items):
    S.paste(cell(n, m), ((j%2)*606, (j//2)*636))
S.save(sys.argv[1])
