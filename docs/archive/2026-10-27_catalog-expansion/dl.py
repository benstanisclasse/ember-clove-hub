import json, sys, os, urllib.request, hashlib, io
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
exp, catdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
prods = json.load(open(exp, encoding='utf-8'))['data']['products']['nodes']
jobs = []
for i, p in enumerate(prods, 1):
    c = json.load(open(os.path.join(catdir, p['handle'] + '.json'), encoding='utf-8'))
    for j, m in enumerate(p['media']['nodes'], 1):
        jobs.append((f"p{i}_g{j:02d}", m['image']['url'], m['id']))
    for j, u in enumerate(c['description_images'], 1):
        jobs.append((f"p{i}_d{j:02d}", u, ''))
def get(job):
    name, url, mid = job
    path = os.path.join(out, name + '.jpg')
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=60).read()
        open(path, 'wb').write(data)
    data = open(path, 'rb').read()
    im = Image.open(io.BytesIO(data))
    return name, mid, im.size, hashlib.md5(data).hexdigest()[:8], len(data)
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, jobs))
info = {}
for r in res:
    print(*r)
    info[r[0]] = r
# contact sheets per product: gallery and desc
font = ImageFont.load_default()
for i in range(1, len(prods) + 1):
    for kind in ('g', 'd'):
        names = sorted(n for n in info if n.startswith(f"p{i}_{kind}"))
        if not names: continue
        cell = 380; cols = 4
        rows = (len(names) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * cell, rows * (cell + 20)), 'white')
        d = ImageDraw.Draw(sheet)
        for k, n in enumerate(names):
            im = Image.open(os.path.join(out, n + '.jpg')).convert('RGB')
            im.thumbnail((cell - 6, cell - 6))
            x, y = (k % cols) * cell, (k // cols) * (cell + 20)
            sheet.paste(im, (x + 3, y + 20))
            d.text((x + 4, y + 4), f"{n} {info[n][2][0]}x{info[n][2][1]} {info[n][3]}", fill='black', font=font)
        sheet.save(os.path.join(out, f"sheet_p{i}_{kind}.jpg"), quality=85)
