"""Turn reviewed listing drafts (data/copy_drafts/*.json, format in BRIEF_new_items.md) into batched Shopify mutations.

Checks every draft first (banned words, length, type, tags, media ids that really belong to the product, unique
titles) and refuses to build anything if one fails. Output, for the main session to send with the Shopify connector:
  <out>/1_products.json   productUpdate per product: title, description, type, tags, vendor (+ media from description)
  <out>/2_alts.json       fileUpdate: alt text on every gallery image
  <out>/3_order.json      productReorderMedia per product: lead image first, flagged images last
  <out>/4_options.json    productOptionUpdate per product: option and color name fixes
and a before/after record. Nothing is ever deleted; prices, inventory and handles are not touched.

Usage:
  python scripts/build_listing_updates.py --export data/inbox/shopify_products_full_2026-10-26_new.json \
      --titles data/inbox/store_titles_2026-10-26.txt --out data/copy_drafts/apply_2026-10-26 \
      --record reports/redesign/product_changes_2026-10-26.json data/copy_drafts/new_2026-10-26_*.json
"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

VENDOR = "Ember & Clove"
TYPES = {"Dresses", "Skirts", "Tops & Bodysuits", "Sweaters & Sweatshirts", "Sandals", "Jeans & Pants", "Outerwear",
         "Accessories"}
BANNED = ["women's", "womens", "sexy", "slimming", "flattering", "eco", "premium", "warm", "waterproof", "vintage brand",
          "british", "free shipping", "ships", "limited", "best seller", "guarantee", "$"]


def check(d, product, titles):
    errs = []
    text = (d["new_title"] + " " + re.sub("<[^>]+>", " ", d["description_html"])).lower()
    errs += [f"banned word {w!r}" for w in BANNED if re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", text)]
    words = len(d["new_title"].split())
    if not 2 <= words <= 6:
        errs.append(f"title has {words} words")
    plain = len(re.sub("<[^>]+>", "", d["description_html"]))
    if not 180 <= plain <= 460:
        errs.append(f"description is {plain} characters")
    if d["description_html"].count("<li>") != 3 or not d["description_html"].startswith("<p><strong>"):
        errs.append("description must be a bold sentence plus exactly 3 bullets")
    if d["product_type"] not in TYPES:
        errs.append(f"unknown product type {d['product_type']!r}")
    if "ec-collection" not in d["tags"]:
        errs.append("missing ec-collection tag")
    if d["new_title"].lower() in titles:
        errs.append(f"title {d['new_title']!r} already used")
    media = {m["id"] for m in product["media"]["nodes"]}
    for mid in [d.get("lead_media_id")] + list(d.get("media_alts", {})) + list(d.get("media_last", [])):
        if mid and mid not in media:
            errs.append(f"media {mid} is not on this product")
    if media and set(d.get("media_alts", {})) != media:
        errs.append(f"alt text missing for {len(media - set(d.get('media_alts', {})))} images")
    if not media and not d.get("add_images_from_description"):
        errs.append("no gallery images and none added")
    colors = {v for o in product["options"] if "color" in o["name"].lower() for v in o["values"]}
    errs += [f"color {c!r} is not an option value" for c in d.get("color_renames", {}) if c not in colors]
    return errs


def final_order(d, product):
    ids = [m["id"] for m in product["media"]["nodes"]]
    last = [m for m in d.get("media_last", []) if m != d.get("lead_media_id")]
    lead = [d["lead_media_id"]] if d.get("lead_media_id") else []
    return lead + [m for m in ids if m not in lead and m not in last] + [m for m in ids if m in last]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True)
    ap.add_argument("--titles", required=True, help="one existing store title per line")
    ap.add_argument("--out", required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("drafts", nargs="+")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    products = {p["id"]: p for p in json.load(open(a.export, encoding="utf-8"))["data"]["products"]["nodes"]}
    titles = {t.strip().lower() for t in open(a.titles, encoding="utf-8") if t.strip()}
    drafts = [d for f in sorted({x for g in a.drafts for x in glob.glob(g)}) for d in json.load(open(f, encoding="utf-8"))]
    problems, seen = {}, set()
    for d in drafts:
        pid = d["product_id"] if d["product_id"].startswith("gid://") else f"gid://shopify/Product/{d['product_id']}"
        d["product_id"] = pid
        if pid not in products:
            problems[pid] = ["not in the export"]
            continue
        errs = check(d, products[pid], titles | seen)
        seen.add(d["new_title"].lower())
        if errs:
            problems[f"{pid} {d['new_title']}"] = errs
    if problems:
        for k, v in problems.items():
            print(f"REFUSED {k}:\n  " + "\n  ".join(v))
        sys.exit(1)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    upd, var, alts, order, opts, record = [], {}, [], [], [], []
    for i, d in enumerate(drafts):
        p = products[d["product_id"]]
        var[f"p{i}"] = {"id": p["id"], "title": d["new_title"], "descriptionHtml": d["description_html"],
                        "productType": d["product_type"], "tags": d["tags"], "vendor": VENDOR}
        media_arg = ""
        if not p["media"]["nodes"] and d.get("add_images_from_description"):
            var[f"m{i}"] = [{"originalSource": u, "mediaContentType": "IMAGE",
                             "alt": f"{d['new_title']}, photo {n + 1}"}
                            for n, u in enumerate(d["add_images_from_description"])]
            media_arg = f", media: $m{i}"
        upd.append(f"  u{i}: productUpdate(product: $p{i}{media_arg}) {{ product {{ id title }} "
                   f"userErrors {{ field message }} }}")
        alts += [{"id": mid, "alt": alt} for mid, alt in d.get("media_alts", {}).items()]
        ids = [m["id"] for m in p["media"]["nodes"]]
        new = final_order(d, p)
        moves = [{"id": m, "newPosition": str(k)} for k, m in enumerate(new)]  # full order: moves apply one by one
        if new != ids:
            order.append((p["id"], moves))
        for o in p["options"]:
            ren_name = d.get("option_renames", {}).get(o["name"])
            values = [{"id": v["id"], "name": d["color_renames"][v["name"]]} for v in o["optionValues"]
                      if "color" in o["name"].lower() and v["name"] in d.get("color_renames", {})]
            if ren_name or values:
                opts.append({"productId": p["id"], "option": {"id": o["id"], **({"name": ren_name} if ren_name else {})},
                             "optionValuesToUpdate": values})
        record.append({"product_id": p["id"], "handle": p["handle"],
                       "before": {"title": p["title"], "productType": p["productType"], "tags": p["tags"],
                                  "vendor": p["vendor"], "media_order": ids,
                                  "alts": {m["id"]: m.get("alt") for m in p["media"]["nodes"]},
                                  "options": {o["name"]: o["values"] for o in p["options"]}},
                       "after": {"title": d["new_title"], "productType": d["product_type"], "tags": d["tags"],
                                 "vendor": VENDOR, "media_order": new, "color_renames": d.get("color_renames", {}),
                                 "option_renames": d.get("option_renames", {}),
                                 "added_media": d.get("add_images_from_description", [])},
                       "flags": d.get("flags", []), "notes": d.get("notes", "")})

    decl = ", ".join([f"$p{i}: ProductUpdateInput!" for i in range(len(drafts))]
                     + [f"${k}: [CreateMediaInput!]" for k in var if k.startswith("m")])
    json.dump({"query": f"mutation({decl}) {{\n" + "\n".join(upd) + "\n}", "variables": var},
              open(out / "1_products.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"query": "mutation($files: [FileUpdateInput!]!) { fileUpdate(files: $files) { files { id alt } "
                        "userErrors { field message code } } }", "variables": {"files": alts}},
              open(out / "2_alts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    oq = "\n".join(f"  r{k}: productReorderMedia(id: $id{k}, moves: $mv{k}) {{ job {{ id }} mediaUserErrors {{ field message }} }}"
                   for k in range(len(order)))
    od = ", ".join(f"$id{k}: ID!, $mv{k}: [MoveInput!]!" for k in range(len(order)))
    ov = {**{f"id{k}": pid for k, (pid, _) in enumerate(order)}, **{f"mv{k}": mv for k, (_, mv) in enumerate(order)}}
    json.dump({"query": f"mutation({od}) {{\n{oq}\n}}", "variables": ov},
              open(out / "3_order.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pq = "\n".join(f"  o{k}: productOptionUpdate(productId: $pid{k}, option: $opt{k}, optionValuesToUpdate: $val{k}) "
                   f"{{ product {{ id }} userErrors {{ field message code }} }}" for k in range(len(opts)))
    pd = ", ".join(f"$pid{k}: ID!, $opt{k}: OptionUpdateInput!, $val{k}: [OptionValueUpdateInput!]"
                   for k in range(len(opts)))
    pv = {}
    for k, o in enumerate(opts):
        pv.update({f"pid{k}": o["productId"], f"opt{k}": o["option"], f"val{k}": o["optionValuesToUpdate"]})
    json.dump({"query": f"mutation({pd}) {{\n{pq}\n}}", "variables": pv},
              open(out / "4_options.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(record, open(a.record, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(drafts)} products: {len(alts)} alt texts, {len(order)} reorders, {len(opts)} option fixes, "
          f"{sum(1 for k in var if k.startswith('m'))} products get photos from their description")


if __name__ == "__main__":
    main()
