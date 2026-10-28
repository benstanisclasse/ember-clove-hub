import sys, os, glob, math
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
src, out, pattern, cell = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
files = sorted(glob.glob(os.path.join(src, pattern)))
cols = min(4, len(files)) or 1
rows = math.ceil(len(files)/cols)
W = cols*cell; H = rows*(cell+22)
sheet = Image.new("RGB", (W, H), "white")
dr = ImageDraw.Draw(sheet)
try: font = ImageFont.truetype("arial.ttf", 18)
except Exception: font = ImageFont.load_default()
for i, f in enumerate(files):
    try:
        im = Image.open(f).convert("RGB")
    except Exception as e:
        continue
    w0,h0 = im.size
    im.thumbnail((cell, cell))
    x = (i%cols)*cell; y = (i//cols)*(cell+22)
    sheet.paste(im, (x + (cell-im.width)//2, y+22))
    dr.text((x+4, y+2), f"{os.path.basename(f)} {w0}x{h0}", fill="red", font=font)
sheet.save(out, quality=85)
print(out, len(files))
