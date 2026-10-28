# Brief: make new listings uniform with the rest of the store

Applies to products the owner adds after the 2026-10-24 cleanup. This produces DRAFTS only; nothing is written to Shopify
here. The main session reviews the drafts and applies them.

## Inputs
- Full export: `data/inbox/shopify_products_full_<date>_new.json` (id, handle, title, options, media ids + URLs + alt,
  variants with their media).
- Originals per product: `data/catalog/<handle>.json` (supplier specs, size tables, description images).
- Style reference: `data/copy_drafts/apparel.json` and `shoes_a.json` (finished drafts from the first cleanup).
- Report with the rules: `reports/redesign/redesign_report_2026-10-24.md` (section on copy).

## Look at the photos
Download each product's gallery images (and description images when the gallery is empty) into a temp folder outside
the Hub, build labelled contact sheets (PIL), and view them. Write copy from what the photos show; use supplier specs
only for facts photos can't show (fabric, sizes). When the photo and supplier text disagree, the photo wins and you
say so in `notes`.

## Rules
- **Title:** `[Key detail] [Fabric/feature] [Item]`, 3–5 words, Title Case, unique in the store, no "Women's", no
  "Sexy", no brand-like words ("Premium", "British", "Vintage Brand").
- **Description (`description_html`):** `<p><strong>one sentence on how it looks or wears</strong></p>` then
  `<ul>` with 3 `<li>` (fabric · fit and details · length or shape), then `<p>` size line, e.g.
  `Sizes S–L · Bust 34–39 in` (convert cm to inches, round to whole inches). About 250–340 characters. No claims that
  can't be checked: no "slimming", "flattering", "sexy", "eco", "premium", "warm", "waterproof" unless it's a plain
  material fact (e.g. "fleece-lined"). No shipping, price, urgency or reviews.
- **Product type:** reuse the store's types so collections pick items up: `Dresses`, `Skirts`, `Tops & Bodysuits`,
  `Sweaters & Sweatshirts` (also cardigans and hoodies), `Sandals` (all footwear). New types only when nothing fits:
  `Jeans & Pants`, `Outerwear`, `Accessories`.
- **Tags:** lowercase, like the reference drafts (garment, fabric, sleeve, color family, season), plus `ec-collection`.
  Shoes and knitwear also get exactly one style tag, which puts them in the menu's collections:
  shoes `style-boots` | `style-heels` | `style-flats` (incl. slippers) | `style-sandals` (flat sandals and slides) |
  `style-wedges` (wedges and platforms); knitwear `style-sweater` (sweaters, cardigans) | `style-sweatshirt`
  (sweatshirts, hoodies). Other clothing is grouped by product type, so it needs no style tag.
- **Colors:** Title Case names that match the photos (`color_renames`: old → new; only where needed).
  Option names Title Case (`option_renames`, e.g. `color` → `Color`, `Lenses Color` → `Lens Color`).
- **Photos (nothing is ever deleted):**
  - `lead_media_id`: the gallery image to show first: one garment, an offered color, plain background or clean
    on-model shot; avoid collages, watermarks, text overlays, size charts, brand logos.
  - `media_alts`: alt text for EVERY gallery image: `"<New Title> in <color>, <view>"` (e.g. "shown flat",
    "on model, front", "close-up of the cuff").
  - `media_last`: media ids to move to the end of the gallery (watermarked, text overlays, size charts, collages,
    logos, wrong product).
  - `add_images_from_description`: only when the gallery has no images: description image URLs that are clean
    product photos, in order (lead first).

## Output
Write a JSON list to the file path you were given, one object per product:
`handle, product_id, original_title, new_title, product_type, tags, description_html, lead_media_id, media_alts,
media_last, add_images_from_description, color_renames, option_renames, flags, notes`.
`flags` is a list of short strings for the owner: watermark, brand logo, men's item, duplicate listing, no photos,
photo color mismatch, off-brand, etc.
