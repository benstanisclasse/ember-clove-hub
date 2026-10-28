import json, re, sys, pathlib
HUB = pathlib.Path.home() / "Documents/EmberClove-Hub"
OUT = pathlib.Path(sys.argv[1])
ids = json.load(open(HUB / "data/inbox/shopify_option_ids_2026-10-24.json", encoding="utf-8"))
drafts = []
for f in ["apparel", "shoes_a", "shoes_b"]:
    drafts += json.load(open(HUB / f"data/copy_drafts/{f}.json", encoding="utf-8"))
# the 3 test products already have titles/descriptions; add type, tags, alt, color/size cleanup
extra = [
    {"product_id": "gid://shopify/Product/9751659741423", "product_type": "Sweaters & Sweatshirts",
     "tags": ["knit", "sweater", "stripe", "polo-collar", "fall"],
     "image_alt": "Striped polo collar knit sweater with a contrast collar", "color_renames": {}},
    {"product_id": "gid://shopify/Product/9751656071407", "product_type": "Dresses",
     "tags": ["knit", "dress", "midi", "mock-neck", "cable-knit", "fall"],
     "image_alt": "Cable knit mock neck midi dress in camel", "color_renames": {"Grandma Gray": "Heather Gray", "Purplish Red": "Berry"}},
    {"product_id": "gid://shopify/Product/9751717118191", "product_type": "Sandals",
     "tags": ["wedge", "slides", "platform", "summer", "black", "white"],
     "image_alt": "Clear strap platform wedge slides in black and white", "color_renames": {}},
]
OFF_BRAND = {"9751655481583", "9751656562927"}  # mesh party mini, Malibu graphic sweatshirt: renamed but kept out of New Arrivals
HOLD_COLOR = {("9751716561135", "Pastel Yellow")}  # verify against variant photo before renaming
EU_US = {34: "3", 35: "4", 36: "5", 37: "6", 38: "7", 39: "8", 40: "9", 41: "10", 42: "10.5", 43: "11", 44: "12", 45: "13"}

def q(s): return json.dumps(s, ensure_ascii=False)

blocks, log = [], []
for d in drafts + extra:
    pid = d["product_id"].split("/")[-1]
    info = ids[pid]
    tags = list(dict.fromkeys(d["tags"] + ([] if pid in OFF_BRAND else ["ec-collection"])))
    a = f"p{pid[-6:]}"
    fields = [f'id: "gid://shopify/Product/{pid}"', f'productType: {q(d["product_type"])}', f'tags: {q(tags)}']
    if "new_title" in d:
        fields += [f'title: {q(d["new_title"])}', f'descriptionHtml: {q(d["description_html"])}']
    m = [f'{a}u: productUpdate(product: {{{", ".join(fields)}}}) {{ userErrors {{ field message }} }}',
         f'{a}m: fileUpdate(files: [{{id: "gid://shopify/MediaImage/{info["media"]}", alt: {q(d["image_alt"])}}}]) {{ userErrors {{ field message }} }}']
    change = {"product_id": pid, "title": d.get("new_title"), "type": d["product_type"], "tags": tags, "options": {}}
    reorder = []
    for oname, (oid, values) in info["options"].items():
        is_size = oname.lower() == "size"
        renames = {}
        for vname, vid in values.items():
            new = vname
            if is_size:
                eu = int(re.match(r"(\d+)", vname).group(1)) if re.match(r"\d+", vname) else None
                if eu in EU_US:
                    new = f"US {EU_US[eu]} (EU {eu})"
            elif vname in d.get("color_renames", {}) and (pid, vname) not in HOLD_COLOR:
                new = d["color_renames"][vname]
            if new != vname:
                renames[vid] = (vname, new)
        new_oname = oname.title()
        if renames or new_oname != oname:
            vals = ", ".join(f'{{id: "gid://shopify/ProductOptionValue/{vid}", name: {q(n)}}}' for vid, (_, n) in renames.items())
            m.append(f'{a}{oname[:1].lower()}: productOptionUpdate(productId: "gid://shopify/Product/{pid}", '
                     f'option: {{id: "gid://shopify/ProductOption/{oid}", name: {q(new_oname)}}}, '
                     f'optionValuesToUpdate: [{vals}]) {{ userErrors {{ field message }} }}')
            change["options"][oname] = {"name": new_oname, "values": {o: n for o, n in renames.values()}}
        order = list(values.items())
        if is_size and all(re.match(r"\d+", v) for v in values):
            order.sort(key=lambda kv: int(re.match(r"\d+", kv[0]).group()))
        reorder.append((oid, [vid for _, vid in order], [v for v, _ in order] != list(values)))
    if any(changed for *_, changed in reorder):
        opts = ", ".join(f'{{id: "gid://shopify/ProductOption/{oid}", values: [{", ".join(f"{{id: \"gid://shopify/ProductOptionValue/{v}\"}}" for v in vals)}]}}'
                         for oid, vals, _ in reorder)
        m.append(f'{a}r: productOptionsReorder(productId: "gid://shopify/Product/{pid}", options: [{opts}]) {{ userErrors {{ field message }} }}')
    blocks.append("\n".join(m))
    log.append(change)

for old in OUT.glob("chunk*.graphql"):
    old.unlink()
skip = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # products already applied
chunks, cur = [], []
for b in blocks[skip:]:
    if cur and sum(len(x) + 1 for x in cur) + len(b) > 14500:
        chunks.append(cur); cur = []
    cur.append(b)
chunks.append(cur)
for n, c in enumerate(chunks, 1):
    (OUT / f"chunk{n}.graphql").write_text("mutation {\n" + "\n".join(c) + "\n}\n", encoding="utf-8")
json.dump(log, open(OUT / "changes.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(blocks) - skip, "products left,", len(chunks), "chunks")
