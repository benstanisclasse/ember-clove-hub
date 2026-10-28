import json, sys, io
from pathlib import Path
import requests
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding="utf-8")
HUB = Path(r"C:\Users\Administrator\Documents\EmberClove-Hub")
OUT = HUB / "studio" / "refs" / "store"; OUT.mkdir(parents=True, exist_ok=True)
page1 = json.load(open(sys.argv[1], encoding="utf-8"))["data"]["products"]["nodes"]
CDN = "https://cdn.shopify.com/s/files/1/0845/4665/0351/files/"
picks = {  # product id: (color, short name)
 "9756905537775": ("Black", "offshoulder-sweatshirt"), "9756901933295": ("Gray", "offshoulder-tee"),
 "9756890005743": ("Black", "crossfront-top"), "9756889874671": ("Black", "lace-shirt"),
 "9756889612527": ("Khaki", "squareneck-tee"), "9756889252079": ("Coffee", "tiesleeve-top"),
 "9756889153775": ("Navy Blue", "asym-tee"), "9756889022703": ("Camel", "chunky-cardigan"),
 "9756888989935": ("Apricot", "crochet-sweater"), "9756888924399": ("Gray", "twopiece-sweater"),
 "9756888760559": ("Gray", "sports-hoodie"), "9756888596719": ("White", "lipprint-sweatshirt"),
 "9756888498415": ("Striped", "stripe-cardigan"), "9756888432879": ("Gray", "fleece-hoodie"),
 "9756887810287": ("Camel color", "hooded-jacket"), "9751659741423": ("Brown and Blue Color-block", "polo-sweater"),
 "9751657152751": ("Coffee", "pheasant-sweatshirt"), "9751657021679": ("Off-White", "textured-bodysuit"),
 "9751656923375": ("Black", "diagonal-bodysuit"), "9751656857839": ("Cream", "floral-bodysuit"),
 "9751656759535": ("Black", "mesh-wrap-top"), "9751656562927": ("Gray", "malibu-sweatshirt"),
 "9751656366319": ("Coffee", "pinstripe-skirt"),
}
fixed = {  # from the second page / by-id query
 "9751656268015": ("Coffee", "suede-skirt", CDN + "3DF3B9E3798B9295593D890A9717B34D.jpg"),
 "9751656104175": ("Oatmeal", "ruffle-skirt", CDN + "6291CACEBD689AE36DA459246508E0B5.jpg"),
 "9751656005871": ("Black", "pleated-skirt", CDN + "17421AF38C25276A86344EC7F9E0B74B.jpg"),
 "9751655842031": ("Dark Gray", "henley-maxi", CDN + "7E57BC6536DC156B3B814547CA8CEC2D.jpg"),
 "9751655678191": ("Khaki", "shirt-dress", CDN + "5C7FABE9FA36996EA75630A20BCA6644.jpg"),
}
rows = []
for p in page1:
    pid = p["id"].split("/")[-1]
    if pid not in picks: continue
    color, short = picks[pid]
    url = next(v["media"]["nodes"][0]["image"]["url"] for v in p["variants"]["nodes"]
               if v["media"]["nodes"] and any(o["value"] == color for o in v["selectedOptions"]))
    rows.append((pid, p["title"], color, short, url.split("?")[0], p["description"]))
for pid, (color, short, url) in fixed.items():
    rows.append((pid, "", color, short, url, ""))
thumbs = []
for pid, title, color, short, url, desc in rows:
    path = OUT / f"{short}.jpg"
    if not path.exists():
        path.write_bytes(requests.get(url, timeout=60).content)
    im = Image.open(path).convert("RGB"); im.thumbnail((360, 480))
    tile = Image.new("RGB", (360, 510), "white"); tile.paste(im, (0, 30))
    ImageDraw.Draw(tile).text((5, 8), f"{short} [{color}]", fill="black")
    thumbs.append(tile)
for k in range(0, len(thumbs), 8):
    sheet = Image.new("RGB", (360 * 4, 510 * 2), "white")
    for j, t in enumerate(thumbs[k:k + 8]):
        sheet.paste(t, ((j % 4) * 360, (j // 4) * 510))
    sheet.save(Path(sys.argv[2]) / f"sheet{k // 8 + 1}.jpg", quality=85)
json.dump([dict(zip(["pid", "title", "color", "short", "url", "desc"], r)) for r in rows],
          open(Path(sys.argv[2]) / "picks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rows), "pieces")
