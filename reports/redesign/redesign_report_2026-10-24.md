# Ember & Clove redesign report — 2026-10-24

Staging theme: **"Ember & Clove – women's apparel (preview)"** (ID 165614420207, unpublished).
Preview: https://nkpfvz-ra.myshopify.com/?preview_theme_id=165614420207
The live theme has not been changed or replaced.

---

## A. Original audit (before)

| Area | What I found |
|---|---|
| Brand | The storefront still spoke as a wellness brand: "Warm Rituals for Everyday Wellness", ritual and spice copy, and wellness promises, on a women's apparel catalog. |
| Catalog | 53 active products: 20 apparel and 20 sandals from EPROLO, plus 13 old wellness/print-on-demand items that can't be fulfilled since Syncee was removed. 2 lingerie and 2 men's items didn't fit the brand. |
| Product names | Supplier keyword strings, e.g. "Women's Sandals Luxury Designer Fashion Gold Chunky Sandals Elegant Square toe Low block-heel Sandals". Several were wrong: a "jumpsuit" that is a bodysuit, a "turkey" print that shows pheasants, a "velvet" sweatshirt that is printed fleece, a "round toe wedge" that is closed-toe. |
| Descriptions | Long supplier dumps with style-tag lists, "sexy", "slimming" and "eco-friendly" claims, and Chinese-size tables. |
| Variants | Lowercase and garbled colors ("black white+green", "Pastel  Blue", "Color", "Grandma Gray", "Purplish Red"); EU-only shoe sizes in random order ("42, 43, 40, 41…"). |
| Product page | The gallery stacked every image, so you saw 2 images at once. Generic accordions. No shipping, returns or fit info near the buy button. |
| Navigation | A generic main menu with no apparel collections. |
| Images | Supplier photos about 1000 px, mixed backgrounds and crops. Empty alt text on every image. |
| Purchasing | **Every product shows Sold out / Unavailable.** The EPROLO fulfillment location isn't in the General shipping profile. |
| Policies | The shipping policy promises "processed within 1 business day", which EPROLO can't meet. There's a $15 Express rate EPROLO can't honor. |
| SEO | The homepage title and meta description still describe wellness. |

## B. Brand identity spec

- **Positioning:** cozy, easy-to-wear women's clothing in warm, earthy tones, made for real life. Knits, dresses and skirts lead; sandals are the seasonal second category.
- **Voice:** warm, plain and concrete. Say what it is and how you'd wear it. No hype words ("luxury", "designer", "sexy", "slimming", "elegant"), no unsupported claims (eco, genuine leather, handmade), and no invented urgency, reviews or stats.
- **Palette:**

  | Role | Name | Hex |
  |---|---|---|
  | Background | Cream | `#FBF6EF` |
  | Text | Espresso | `#3B2418` |
  | Secondary text | Cocoa | `#5A3E2E` |
  | Lines | Linen | `#E7DACB` |
  | Panels | Oat | `#F1E6D8` |
  | Accent / buttons | Ember | `#A84A1C` |
  | Highlight on dark | Clay | `#E8A27A` |

- **Type:** Playfair Display 500 for headings, Inter 400/500 for body and labels, 16 px body.
- **Shape:** 8 px radius on buttons, cards, inputs and swatches; portrait 4:5 product cards.
- **Icons:** line icons (heart, flame, sparkle, leaf, sun, moon) in Ember on Oat circles.
- **Naming rule:** `[Key detail] [Fabric/feature] [Item]`, 3–5 words, Title Case, unique, no "Women's".
- **Description rule:** one bold sentence on how it feels or wears, 3 bullets (fabric · fit and details · length or heel), then a size line. About 250–340 characters.
- **Colors and sizes:** clear Title Case color names; shoe sizes shown as `US 7 (EU 38)` in ascending order.

## C. Change log (everything is reversible)

**Preview theme (unpublished)**
| File | Change |
|---|---|
| `config/settings_data.json` | Ember & Clove palette, Playfair 500 headings, 16 px body, 8 px radius, Ember primary buttons and sale badge |
| `templates/index.json` | Hero "Wear the warmth" (camel cable-knit photo) → new promise bar (cozy, warm colors, free shipping over $70, 7-day returns) → "Shop new arrivals" grid (8, portrait) → "How to wear it" three looks linked to real products → "Why Ember & Clove" story (pleated skirt photo) |
| `templates/product.json` | Carousel gallery with left thumbnails (fixes the double image), 4:5 frame, variant images hidden from the strip, sticky add-to-cart, Shipping, Returns and Size & fit accordions linking to the policies, a 3-item promise bar, "You may also like" |
| `templates/page.contact.json` | Heading font, short intro line, "Send message" button |
| `sections/header-group.json` | Announcement "Free US shipping on orders over $70"; menu switched to `ember-clove-main` |
| `sections/footer-group.json` | Newsletter "Join the Ember & Clove list", TikTok link |

Originals are in `theme-staging/baseline/`; new versions are in `theme-staging/staged/`.

**Store objects (visible only through the new theme/menu)**
- Smart collections, published to the Online Store:

  | Collection | Products |
  |---|---|
  | New Arrivals | 34, manual order: knits and dresses first, then sandals |
  | Dresses | 5 |
  | Sweaters & Knitwear | 3 |
  | Skirts | 4 |
  | Tops & Bodysuits | 4 |
  | Sandals | 20 |

- Menu `ember-clove-main`: New Arrivals · Clothing (Dresses, Sweaters & Knitwear, Skirts, Tops & Bodysuits) · Sandals · Contact.

**Products (live data, 36 EPROLO products)**
- New title, short description, product type, tags (`ec-collection` controls New Arrivals) and first-image alt text.
- Color clean-up:
  - Apricot → Cream/Oatmeal
  - Oats → Oatmeal
  - Navy Blue → Navy
  - Off-white → Off-White
  - Purple → Lavender
  - Pink → Blush (ruched top only)
  - Grandma Gray → Heather Gray
  - Purplish Red → Berry
  - Grey → Gray
  - crocodile pattern → Croc
  - lowercase/"+" names fixed
- All shoe sizes renamed to `US x (EU y)` and sorted ascending.
- **Handles (URLs) unchanged.**
- Per-product before/after: `reports/redesign/product_changes_2026-10-24.json`. Original supplier titles, specs and images: `data/catalog/<handle>.json`.
- Not changed: prices, inventory, shipping, taxes, payments, policies, product media.

## D. Image report

- **Kept all supplier media**; nothing deleted or replaced.
- Quality: about 1000 px square JPGs with mixed backgrounds (street, studio, flat lay, mannequin). The 4:5 "contain" frame keeps them uncropped, so the page looks consistent even when the photos don't.
- **Problems to fix:**

  | Product | Issue |
  |---|---|
  | Ruffle Slit Knit Midi Skirt | First photo is pink, which isn't an offered color. Swap the lead image. |
  | Metallic Square Toe Heeled Mules | Looks like a retailer's studio photo with a brand logo on the heel caps. Image-rights risk; consider removing the product. |
  | Braided Cord Strappy Flat Sandals | Photo 2 shows a brand logo on the footbed. |
  | Pheasant Print Sweatshirt | Photos have "Sweatshirt Only" text on them. |
  | Diagonal Rib Bodysuit | First image shows all colors together. |
  | Double Buckle Platform Sandals | Supplier "FASHION" logo printed on the insole. |
  | Ruffle Hem Mesh Mini Dress | Mannequin-only photos. |

- **Alt text** was added to the first image of every product; the other images still have none.
- **Upgrade path:** reshoot hero products as consistent cream-background on-model images, or Higgsfield lifestyle stills, once the Higgsfield plan is active (10 credits today). They must show the real product: same color, same details, no added features.

## E. Copy report

- 36 products rewritten (33 new plus type/tags/alt on the 3 test products). Descriptions run about 250–340 characters, down from 1,500–4,000+.
- Corrections made from the photos rather than the supplier text:
  - jumpsuit → bodysuit (×2)
  - turkey → pheasant
  - "velvet" → printed fleece (now Malibu Beach Graphic Sweatshirt)
  - "round toe" → closed-toe espadrille wedge
  - "gold" mules → metallic orange
  - "suede" → braided cord
  - "herringbone" → diagonal rib
  - "ruffled" → ruched
  - "V-neck shawl" → henley tie-waist
- Claims removed: eco-friendly, slimming, sexy, luxury, designer, genuine-leather wording. PU is now "faux leather".
- **Site copy:** new hero, promise bar, "How to wear it" and story copy. No reviews, ratings, years in business, certifications, origins, guarantees or urgency claims anywhere.
- **Held for your check:**
  - Toe-loop slides "Pastel Yellow" looks gold in photos; not renamed yet.
  - Asymmetric skirt "Khaki" looks sage.
  - The Malibu sweatshirt's specs copy the pheasant one's; verify the measurements.
  - Stiletto mules only have a size table to EU 39 but sell to EU 45.

## F. Technical / UX testing (preview theme)

| Check | Result |
|---|---|
| Desktop 1366 px: home, collection, product | ✅ Layout, menu, gallery and grid render correctly |
| Mobile 375 px: home, product | ✅ No horizontal scroll (scrollWidth 375 = viewport), hamburger menu, swipe gallery with dots, readable type |
| Tablet ~790 px | ✅ The menu collapses extra items into "More"; fine |
| Product gallery double image | ✅ Fixed (one main image + thumbnails) |
| Collections and menu links | ✅ All resolve and are populated |
| Contact page, 404, search | ✅ Render on brand. ⚠️ Search still returns men's, lingerie and old POD products until they're hidden |
| Add to cart / checkout | ❌ **Blocked**: every variant shows Unavailable or Sold out (EPROLO location not in the shipping profile). Couldn't test cart or checkout; no orders placed. |
| Browser tab / SEO title | ⚠️ Homepage still "Warm Rituals for Everyday Wellness" (store-level setting) |

## G. Scores (preview theme, today)

| # | Category | Score | What's holding it back from 9+ |
|---|---|---|---|
| 1 | Brand identity and cohesion | 8.5 | Off-brand items still in the catalog and search |
| 2 | Homepage design | 8.5 | Hero and story photos are supplier images |
| 3 | Imagery | 5 | Mixed supplier photos, logos on 2 items, mismatched lead image |
| 4 | Product copy | 8.5 | A few colors and specs need your check (section E) |
| 5 | Product page UX | 8 | No size-chart page yet; "Unavailable" button |
| 6 | Navigation and collections | 8.5 | Small catalog per category (3–6 items) |
| 7 | Mobile experience | 8.5 | Not tested end-to-end through checkout |
| 8 | Trust and policies | 6 | Shipping policy promises 1-day processing; no About page |
| 9 | SEO and speed | 6.5 | Homepage title and meta are old; alt text only on first images; supplier-style URLs kept on purpose |
| 10 | Purchase readiness | 2 | Nothing can be bought until the shipping-profile fix |

**Path to 9+:** fix the shipping profile, hide off-brand items, update the shipping policy and homepage SEO, round prices, replace the 5–8 weakest lead images, and add a size-guide page.

## H. Publication readiness

**Not ready to publish yet.** These need your approval, in this order:

1. **Shipping profile (critical):** add the EPROLO location to the General profile, so products become purchasable.
2. **Hide off-brand products:** 13 old wellness/POD items, 2 lingerie, 2 men's, and optionally the Ruffle Hem Mesh Mini Dress and Metallic Square Toe Mules (image rights).
3. **Shipping policy:** replace "processed within 1 business day" with honest EPROLO processing and transit times.
4. **Remove the $15 Express rate.**
5. **Homepage SEO:** title "Ember & Clove | Cozy Knits, Dresses & Skirts for Women"; meta "Cozy knitwear, sweater dresses, skirts and sandals in warm, earthy tones. Free US shipping on orders over $70."
6. **Prices:** round to .99, e.g. $53.44 → $52.99/$54.99 (per the price proposal).
7. **Publish the preview theme**, after a test order once item 1 is fixed.

---

## Update — 7-day returns (2026-10-24)
Return window changed from 30 to **7 days** everywhere:
- Shopify return rule (Settings → Policies → Default rules)
- Refund policy page
- Merchant Center return policy, matched to the website: new items only, by mail, customer pays return shipping, no restocking fee, no exchanges
- Theme copy, in draft theme "Ember & Clove – 7-day returns" (165625921775): homepage promise bar, product page promise bar, and the product page Returns section. **This theme must be published to go live.**
