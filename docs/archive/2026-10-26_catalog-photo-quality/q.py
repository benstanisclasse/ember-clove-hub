"""Photo quality metrics. usage: q.py <outdir> <name>=<url> ...  Prints w h kb sharp detail."""
import sys, io, urllib.request
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

def metrics(im):
    g = im.convert("L")
    w, h = g.size
    s = 1000 / max(w, h)
    g1 = g.resize((round(w * s), round(h * s)), Image.LANCZOS)
    a = np.asarray(g1, dtype=np.float32)
    lap = np.asarray(g1.filter(ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], 1, 128)), dtype=np.float32) - 128
    sharp = float(lap.var())
    # sharpness of the most detailed tiles only (plain backgrounds don't drag it down)
    t = 50
    tiles = [lap[y:y+t, x:x+t].var() for y in range(0, lap.shape[0]-t+1, t) for x in range(0, lap.shape[1]-t+1, t)]
    p90 = float(np.percentile(tiles, 90))
    # detail lost by halving then restoring at native size: small = image was upscaled / blurry
    a0 = np.asarray(g, dtype=np.float32)
    half = g.resize((w // 2, h // 2), Image.LANCZOS).resize((w, h), Image.LANCZOS)
    detail = float(np.abs(a0 - np.asarray(half, dtype=np.float32)).mean())
    return w, h, sharp, detail, p90

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for arg in sys.argv[2:]:
    name, url = arg.split("=", 1)
    p = out / f"{name}.jpg"
    if not p.exists():
        p.write_bytes(urllib.request.urlopen(url, timeout=30).read())
    im = Image.open(p)
    w, h, sharp, detail, p90 = metrics(im)
    print(f"{name}\t{w}x{h}\t{p.stat().st_size//1024}KB\tsharp={sharp:.0f}\tdetail={detail:.2f}	p90={p90:.0f}")
