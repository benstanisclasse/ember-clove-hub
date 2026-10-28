"""Build the product catalog: full supplier details and every image, saved before listings are shortened.

Each product gets data/catalog/<handle>.json with the original title, parsed supplier specs, size
table, all gallery and description image URLs, variants with cost and price, and the raw description.
data/catalog_index.csv lists every product on one row. Higgsfield video work reads from here.

Usage:
  python catalog.py data/inbox/shopify_products_full_<date>.json
"""
import csv
import html
import json
import re
import sys
from html.parser import HTMLParser

import hubdata as hd

CATALOG = hd.DATA / "catalog"

GROUP_RULES = [  # first match wins; whole-word regexes against the lowercased original title
    ("lingerie", r"\b(lingerie|push-up|built-in bra)\b"),
    ("mens", r"(?<!wo)\bmen'?s\b"),
    ("shoes", r"\b(sandals?|heels?|flats|shoes)\b"),
    ("dresses", r"\b(dress|jumpsuit|one-piece)\b"),
    ("skirts", r"\bskirt\b"),
    ("knitwear", r"\b(sweater|sweatshirt|cardigan|hoodie)\b"),
    ("tops", r"\b(top|bodysuit|blouse)\b"),
]


class _DescriptionParser(HTMLParser):
    """Collect visible text lines, <img> sources and <table> rows from a supplier description."""

    def __init__(self):
        super().__init__()
        self.lines, self.images, self.tables = [], [], []
        self._line, self._row, self._cell, self._table = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)
        elif tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag in ("p", "br", "li", "div", "h1", "h2", "h3", "h4"):
            self._flush()

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None
        elif tag in ("p", "li", "div", "h1", "h2", "h3", "h4"):
            self._flush()

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)
        elif self._table is None:
            self._line.append(data)

    def _flush(self):
        text = " ".join("".join(self._line).split())
        if text:
            self.lines.append(text)
        self._line = []

    def close(self):
        super().close()
        self._flush()


def parse_description(raw_html):
    parser = _DescriptionParser()
    parser.feed(html.unescape(raw_html or ""))
    parser.close()
    specs, prose = {}, []
    for line in parser.lines:
        match = re.match(r"^[-•*]?\s*([A-Za-z][A-Za-z /&()-]{1,30})\s*[:：]\s*(.+)$", line)
        if match:
            specs[match.group(1).strip()] = match.group(2).strip()
        else:
            prose.append(line)
    return specs, prose, parser.images, parser.tables


def group_for(title):
    lowered = title.lower()
    for group, pattern in GROUP_RULES:
        if re.search(pattern, lowered):
            return group
    return "other"


def build(product):
    specs, prose, desc_images, tables = parse_description(product.get("descriptionHtml"))
    gallery = [m["image"] for m in product["media"]["nodes"] if m.get("image")]
    variants = product["variants"]["nodes"]
    prices = [hd.num(v["price"]) for v in variants if v.get("price")]
    costs = [hd.num(v["inventoryItem"]["unitCost"]["amount"]) for v in variants
             if v.get("inventoryItem") and v["inventoryItem"].get("unitCost")]
    options = {o["name"].strip().title(): o["values"] for o in product["options"]}
    return {
        "product_id": product["id"],
        "handle": product["handle"],
        "original_title": product["title"],
        "current_title": product["title"],
        "vendor": product["vendor"],
        "status": product["status"],
        "group": group_for(product["title"]) if product["vendor"].lower() == "eprolo" else "legacy",
        "url": product.get("onlineStoreUrl"),
        "category": (product.get("category") or {}).get("fullName"),
        "colors": options.get("Color", []),
        "sizes": options.get("Size", []),
        "options": options,
        "price_min": min(prices) if prices else None,
        "price_max": max(prices) if prices else None,
        "cost_min": min(costs) if costs else None,
        "cost_max": max(costs) if costs else None,
        "specs": specs,
        "description_text": prose,
        "size_tables": tables,
        "gallery_images": gallery,
        "description_images": desc_images,
        "variants": [{"title": v["title"], "sku": v["sku"], "price": v["price"],
                      "cost": (v.get("inventoryItem") or {}).get("unitCost", {}).get("amount"),
                      "options": {o["name"]: o["value"] for o in v["selectedOptions"]}} for v in variants],
        "raw_description_html": product.get("descriptionHtml"),
        "cataloged_at": hd.now(),
    }


INDEX_FIELDS = ["handle", "original_title", "current_title", "vendor", "status", "group", "colors",
                "sizes", "price_min", "cost_min", "material", "fit", "gallery_count",
                "description_image_count", "size_table", "file"]


def main(path):
    products = hd.load_json(path)["data"]["products"]["nodes"]
    CATALOG.mkdir(parents=True, exist_ok=True)
    rows = []
    for product in products:
        entry = build(product)
        out = CATALOG / f"{entry['handle']}.json"
        if out.exists():  # keep the first-seen original title; only refresh everything else
            entry["original_title"] = hd.load_json(out).get("original_title", entry["original_title"])
        with open(out, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        specs = entry["specs"]
        rows.append({
            "handle": entry["handle"], "original_title": entry["original_title"],
            "current_title": entry["current_title"], "vendor": entry["vendor"], "status": entry["status"],
            "group": entry["group"], "colors": " | ".join(entry["colors"]), "sizes": " | ".join(entry["sizes"]),
            "price_min": entry["price_min"], "cost_min": entry["cost_min"],
            "material": specs.get("Material", ""), "fit": specs.get("Fit Type", specs.get("Fit", "")),
            "gallery_count": len(entry["gallery_images"]),
            "description_image_count": len(entry["description_images"]),
            "size_table": "yes" if entry["size_tables"] else "no",
            "file": f"data/catalog/{entry['handle']}.json",
        })
    index = hd.DATA / "catalog_index.csv"
    if index.exists():  # an export of only some products (e.g. new arrivals) keeps the other rows
        seen = {r["handle"] for r in rows}
        with open(index, newline="", encoding="utf-8") as f:
            rows += [r for r in csv.DictReader(f) if r["handle"] not in seen]
    rows.sort(key=lambda r: (r["group"], r["original_title"]))
    with open(index, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    hd.log(f"Catalog built from {path}: {len(rows)} products")
    counts = {}
    for r in rows:
        counts[r["group"]] = counts.get(r["group"], 0) + 1
    print(f"{len(rows)} products cataloged: " + ", ".join(f"{g} {n}" for g, n in sorted(counts.items())))
    print(f"images: {sum(int(r['gallery_count']) for r in rows)} gallery, "
          f"{sum(int(r['description_image_count']) for r in rows)} from descriptions")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
