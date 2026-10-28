import json, sys, os, io, requests
from PIL import Image, ImageDraw
imgs = json.load(open(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
maxn = int(sys.argv[3]) if len(sys.argv) > 3 else 6
for i, (h, urls) in enumerate(imgs.items()):
    tiles = []
    for u in urls[:maxn]:
        sep = '&' if '?' in u else '?'
        try:
            r = requests.get(u + sep + 'width=360', timeout=30)
            im = Image.open(io.BytesIO(r.content)).convert('RGB')
            im.thumbnail((360, 480))
            tiles.append(im)
        except Exception as e:
            print('fail', h, e)
    if not tiles:
        continue
    W = sum(t.width for t in tiles) + 6 * len(tiles)
    H = max(t.height for t in tiles)
    sheet = Image.new('RGB', (W, H + 20), 'white')
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 20)); x += t.width + 6
    ImageDraw.Draw(sheet).text((4, 4), h[:60] + f'  ({len(urls)} imgs total)', fill='black')
    sheet.save(os.path.join(out, f'{i:02d}_{h[:30]}.jpg'), quality=80)
    print(i, h, len(urls))
