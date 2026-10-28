"""Build the review page (HTML with embedded data + 720x1280 review JPEGs) from the manifest and matrix.

Run from the Hub root: python -I research/ads/tiktok/product_tests/ec_product_test_01/tools/build_review_page.py <out_dir>
Publish <out_dir>/tiktok_test01_review.html with its img/ files to the review artifact.
"""
import csv
import json
import os
import sys

from PIL import Image

T = "research/ads/tiktok/product_tests/ec_product_test_01"
OUT = sys.argv[1]
ORDER = ["P001", "P003", "P005", "P006", "P007", "P009", "P011", "P012", "P013", "P014"]

os.makedirs(f"{OUT}/img", exist_ok=True)
man = json.load(open(f"{T}/prototypes_manifest.json", encoding="utf-8"))
rows = {r["ad_name"]: r for r in csv.DictReader(open(f"{T}/creative_matrix.csv", encoding="utf-8"))}
prods = {p["test_product_id"]: p for p in json.load(open(f"{T}/products.json", encoding="utf-8"))["products"]}
data = {"products": []}
for pid in ORDER:
    p, ads = prods[pid], []
    for m in sorted([m for m in man if m["product_id"] == pid], key=lambda m: m["concept"]):
        r = rows[m["ad_name"]]
        fn = f"img/{m['ad_name']}_v{m['version']}.jpg"
        if not os.path.exists(f"{OUT}/{fn}"):
            Image.open(m["prototype"]).resize((720, 1280), Image.LANCZOS).save(f"{OUT}/{fn}", quality=84)
        ads.append({"ad_name": m["ad_name"], "product_id": pid, "product": p["title"], "concept": r["concept"],
                    "version": m["version"], "prototype_sha256": m["prototype_sha256"], "image": fn,
                    "headline": r["slide1_headline"], "caption": r["caption"], "learning": r["expected_learning"],
                    "motivation": r["motivation"], "slides": r["slides"]})
    e = p["economics"]
    data["products"].append({"id": pid, "title": p["title"], "price": p["price"], "breakeven": e["breakeven_cpa"],
                             "kept": e["kept_after_20_cpa"], "variant": rows[ads[0]["ad_name"]]["variant"],
                             "url": p["url"], "ads": ads})
tpl = open(f"{T}/tools/review_template.html", encoding="utf-8").read()
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
open(f"{OUT}/tiktok_test01_review.html", "w", encoding="utf-8").write(tpl.replace("__DATA__", blob))
print("files:", " ".join(a["image"] for p in data["products"] for a in p["ads"]))
