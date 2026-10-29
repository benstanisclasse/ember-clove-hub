"""Outfit board ("shop the look" collage): a model on the left, product cut-outs arranged around her on a soft grey
background, Ember & Clove wordmark bottom right.

`cutout <src.jpg> <out.png> [crop x0,y0,x1,y1 | -] [white 0-255] [erode px, odd]`: removes a plain white/near-white studio background by flood-filling
from the image border (only background touching the edge is removed, so light parts inside the product stay), then
feathers the edge and trims to the product. Works for shop photos shot on white; not for photos with a scene behind.

`board <layout.json> <out.jpg>`: places the pieces. Layout: {"size": [w, h], "bg": "#cfcbc6", "items": [{"src":
"<png>", "box": [x, y, w, h], "shadow": true}, ...], "wordmark": true}. Each piece is scaled to fit its box (aspect
kept) and centred in it; items are drawn in order, so later ones sit on top. Changes nothing anywhere.
Run: python -I scripts/outfit_board.py cutout|board ...
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

WHITE = 238  # a pixel is "background" when all channels are at least this bright and it touches the border


def cutout(src, out, crop=None, white=WHITE, erode=3):
    im = Image.open(src).convert("RGB")
    if crop and crop != "-":
        im = im.crop(tuple(int(v) for v in crop.split(",")))
    a = np.asarray(im).astype(np.int16)
    light = (a.min(axis=2) >= white)
    labels, _ = ndimage.label(light)
    edge = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    bg = np.isin(labels, edge[edge > 0])
    # Small, almost pure white pockets enclosed by the subject (background seen through hair or between arm and body).
    # Large light areas (a white top) are kept: only pockets under 0.2% of the picture are removed.
    pockets, n = ndimage.label((a.min(axis=2) >= 250) & ~bg)
    if n:
        sizes = ndimage.sum(np.ones_like(pockets), pockets, index=np.arange(1, n + 1))
        small = np.flatnonzero((sizes >= 40) & (sizes < pockets.size * 0.002)) + 1
        bg |= np.isin(pockets, small)
    alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(erode)).filter(ImageFilter.GaussianBlur(1.2))
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    rgba = rgba.crop(rgba.getbbox())
    rgba.save(out)
    print(f"{out}: {rgba.size[0]}x{rgba.size[1]}")


def board(layout_path, out):
    lay = json.loads(Path(layout_path).read_text(encoding="utf-8"))
    w, h = lay["size"]
    canvas = Image.new("RGBA", (w, h), lay.get("bg", "#cfcbc6"))
    base = Path(layout_path).parent
    for it in lay["items"]:
        piece = Image.open(base / it["src"]).convert("RGBA")
        bx, by, bw, bh = it["box"]
        scale = min(bw / piece.width, bh / piece.height)
        piece = piece.resize((max(1, int(piece.width * scale)), max(1, int(piece.height * scale))), Image.LANCZOS)
        x, y = bx + (bw - piece.width) // 2, by + (bh - piece.height) // 2
        if it.get("shadow", True):
            sh = Image.new("RGBA", piece.size, (40, 30, 20, 0))
            sh.putalpha(piece.getchannel("A").point(lambda v: int(v * 0.28)))
            sh = sh.filter(ImageFilter.GaussianBlur(max(6, w // 160)))
            canvas.alpha_composite(sh, (x + w // 180, y + w // 120))
        canvas.alpha_composite(piece, (x, y))
    if lay.get("wordmark", True):
        d = ImageDraw.Draw(canvas)
        big = ImageFont.truetype("georgia.ttf", w // 26)
        text = "EMBER & CLOVE"
        tw = d.textlength(text, font=big)
        d.text((w - tw - w // 22, h - w // 14), text, fill=(45, 38, 32, 255), font=big)
    canvas.convert("RGB").save(out, quality=92)
    print(f"{out}: {w}x{h}")


if __name__ == "__main__":
    if sys.argv[1] == "cutout":
        cutout(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None,
               int(sys.argv[5]) if len(sys.argv) > 5 else WHITE, int(sys.argv[6]) if len(sys.argv) > 6 else 3)
    else:
        board(sys.argv[2], sys.argv[3])
