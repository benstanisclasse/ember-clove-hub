import json, re, sys
exp, out = sys.argv[1], sys.argv[2]
P = {p['id'].rsplit('/', 1)[1]: p for p in json.load(open(exp, encoding='utf-8'))['data']['products']['nodes']}
ALL = ["spring", "summer", "fall", "winter"]


def mk(pid, title, tags, desc, lead, alts, last, cren, oren, flags, notes, wardrobe):
    p = P[pid]
    ids = [m['id'] for m in p['media']['nodes']]
    g = lambda n: ids[n - 1]
    w = dict(wardrobe)
    w['photo_media_id'] = g(w['photo_media_id']) if w.get('photo_media_id') else None
    return {
        "handle": p['handle'], "product_id": p['id'], "original_title": p['title'], "new_title": title,
        "product_type": "Accessories", "tags": tags, "description_html": desc,
        "lead_media_id": g(lead),
        "media_alts": {g(n): f"{title} in {a}" for n, a in sorted(alts.items())},
        "media_last": [g(n) for n in last], "add_images_from_description": [],
        "color_renames": cren, "option_renames": oren, "flags": flags, "notes": notes, "wardrobe": w}


D = []
# 1 cherry bag charm
t = "Glitter Cherry Bag Charm"
D.append(mk("9757659955439", t,
  ["bag charm", "keychain", "cherry", "resin", "glitter", "gold-tone", "silver-tone", "red", "pink", "ec-collection"],
  "<p><strong>Two glossy resin cherries on a metal stem and leaf, hung from a swivel clip and key ring for a bag or keys.</strong></p>"
  "<ul><li>Resin cherries, glitter or glossy; gold-tone, silver-tone or gunmetal hardware</li>"
  "<li>Swivel clip, split key ring and a small hang tag</li>"
  "<li>Metal or green leaves; also as a gold-tone coiled snake</li></ul>"
  "<p>One size · clips onto a bag handle, strap or keys</p>",
  8,
  {1: "Red Glitter, shown flat", 2: "Red Green Leaf, shown flat", 3: "Red Glitter, side view on white",
   4: "Pink Glitter, shown flat", 5: "Glossy Red, shown flat", 6: "Amber Glitter, shown flat",
   7: "Gray Glitter, shown flat", 8: "Red Green Leaf, shown flat", 9: "Black Glitter, shown flat",
   10: "Gold Snake, shown flat", 11: "Pink Green Leaf, styled on a tray"},
  [2],
  {"Cherry": "Red Glitter", "Pink + Silver": "Pink Glitter", "Red Cherry": "Glossy Red", "Golden Cherry": "Amber Glitter",
   "Silver Gray Cherry": "Gray Glitter", "Double Leaf Cherry": "Red Green Leaf", "Black Cherry": "Black Glitter",
   "Pink + Gold": "Pink Green Leaf", "Spirit Snake [Dumb Gold]": "Gold Snake"},
  {},
  ["designer look-alike (Coach cherry bag charm)", "hang tag stamped \"china\"", "snake variant is not a cherry",
   "duplicate image", "size not stated"],
  "Closely copies Coach's signature cherry bag charm (dog-leash swivel clip, split ring, rectangular hang tag, glitter resin cherries with a metal leaf) and its coiled snake charm; the hang tag is stamped \"china\" instead of a brand name (legible in images 1 and 3), so no logo, but the owner may want to weigh the look-alike risk. Supplier material: \"Plastic/Resin\"; the hardware metal is not stated, so the copy says only gold-tone/silver-tone/gunmetal. Colors renamed from what the photos show: Cherry = red glitter with a gold-tone leaf, Pink + Silver = pink glitter on silver-tone, Red Cherry = solid glossy red, Golden Cherry = amber glitter, Silver Gray Cherry = gray glitter on gunmetal, Double Leaf Cherry = red glitter with two green leaves, Black Cherry = black glitter, Pink + Gold = pink/red speckled cherries with green leaves, Spirit Snake [Dumb Gold] = a gold-tone coiled snake (no cherry). Image 2 is a byte-identical copy of image 8 (the Red Green Leaf variant image), so image 8 leads and image 2 goes last. Image 3 is a cut-out on white showing only one cherry; image 11 is a styled shot with added sparkles. No dimensions in the supplier data.",
  {"use": False, "color": "Red Green Leaf", "photo_media_id": 8, "season": ALL, "open_toe": False, "occasion": ["day"],
   "category": "accessory",
   "prompt_description": "A bag charm of two glossy red glitter resin cherries with green enamel-look leaves on a gold-tone stem, hanging from a gold-tone swivel trigger clip with a split key ring and a small rectangular hang tag."}))

# 2 heart ball chain
t = "Puffy Heart Ball Chain Necklace"
D.append(mk("9757659988207", t,
  ["jewelry", "necklace", "bracelet", "heart", "pendant", "ball chain", "stainless steel", "gold-tone", "silver-tone", "ec-collection"],
  "<p><strong>A bold puffed heart pendant on a chunky ball chain, polished to a mirror shine.</strong></p>"
  "<ul><li>Stainless steel, plain silver-tone or gold-tone plated</li>"
  "<li>Puffed heart pendant about 1.4 in tall; round beads about 5/16 in across</li>"
  "<li>Extender chain at the clasp; also offered as a gold-tone bracelet</li></ul>"
  "<p>Necklace about 16 in + 2 in extender</p>",
  7,
  {1: "Gold Necklace, shown flat", 2: "Gold Necklace and Silver Necklace, styled flat lay",
   3: "Silver Necklace, close-up of the heart", 4: "Gold Necklace, full length with extender",
   5: "Gold Necklace, on model", 6: "Silver Necklace, shown flat", 7: "Gold Necklace, shown flat",
   8: "Gold Bracelet, close-up"},
  [1, 8],
  {"Steel Color Necklace": "Silver Necklace", "Golden  Necklace": "Gold Necklace", "Golden  Bracelet": "Gold Bracelet"},
  {},
  ["low-res image", "duplicate image", "bracelet variant in a necklace listing"],
  "Supplier title says \"18K gold\"; the spec says stainless steel (pendant titanium steel), electroplated, so the copy says gold-tone plated and never 18K gold. The \"Steel Color\" version is plain silver-tone steel. Measurements from description image 1: beads 0.8 cm, heart 3.5 cm, necklace about 40 cm + 5 cm extender (spec says 41-50 cm). Image 1 is a byte-identical copy of image 7 (the Gold Necklace variant image), so image 7 leads and image 1 goes last. Image 8, the only Gold Bracelet photo and its variant image, is 284x385 and blurry, so it goes last; bracelet length is not stated. The on-model shot (image 5) looks clean; owner to judge. Color option values had double spaces (\"Golden  Necklace\"), fixed in the renames.",
  {"use": True, "color": "Gold Necklace", "photo_media_id": 7, "season": ALL, "open_toe": False, "occasion": ["day", "night"],
   "category": "accessory",
   "prompt_description": "A gold-tone necklace of large round polished ball beads with a big glossy puffed heart pendant hanging at the center, sitting at the collarbone."}))

# 3 pearl flower choker
t = "Pearl Daisy Chain Choker"
D.append(mk("9757660053743", t,
  ["jewelry", "necklace", "choker", "pearl", "flower", "daisy", "copper", "gold-tone", "ec-collection"],
  "<p><strong>A fine gold-tone chain set with five tiny daisies of pearl-look beads that sit close at the collarbone.</strong></p>"
  "<ul><li>Copper with gold-tone plating</li>"
  "<li>Five evenly spaced pearl-bead flowers with gold-tone centers on a fine cable chain</li>"
  "<li>Lobster clasp and extender chain with a small charm at the end</li></ul>"
  "<p>Chain about 14 in + 2 in extender</p>",
  4,
  {1: "Gold, shown flat with text", 2: "Gold, on model", 3: "Gold, on model", 4: "Gold, shown flat",
   5: "Gold, on model, framed close-up", 6: "Gold, on model"},
  [1, 5, 2],
  {}, {"Purity": "Plating"},
  ["text overlay", "low-res on-model photos (upscaled)", "duplicate image", "title said 5 necklaces"],
  "Photos win over the supplier title: \"5 flower necklaces\" is one necklace with five pearl-bead flowers, not five necklaces. Spec: copper, \"Purity: 14K\"; image 1 says \"14k gold plated\", so the copy says gold-tone plated copper and never 14K gold. The option \"Purity: 14k\" reads like solid gold to a shopper, so the option is renamed Plating (value 14k unchanged). Pearls: spec only says \"Design Element: Pearl\"; the copy says pearl-look beads. Length from image 1: 14 in + 2 in extender. Image 1 has a text overlay and goes last; image 5 is a small framed crop with rounded corners and a white border, last; image 2 is a byte-identical copy of image 6 (the variant image), last. The on-model shots (2, 3, 5, 6) are soft and look upscaled to 1920 px; the flat lay (image 4) is the sharpest and leads.",
  {"use": True, "color": "Gold", "photo_media_id": 4, "season": ALL, "open_toe": False, "occasion": ["day"],
   "category": "accessory",
   "prompt_description": "A delicate gold-tone choker-length cable chain with five tiny white pearl-bead daisy flowers with gold centers spaced evenly along it, sitting at the base of the neck."}))

# 4 stone curb choker
t = "Oval Stone Curb Chain Choker"
D.append(mk("9757660086511", t,
  ["jewelry", "necklace", "choker", "curb chain", "rhinestone", "stone", "stainless steel", "gold-tone", "green", "red", "ec-collection"],
  "<p><strong>A chunky gold-tone curb chain choker centered on an oval cabochon stone framed by tiny rhinestones.</strong></p>"
  "<ul><li>Stainless steel with gold-tone plating, rhinestone accents</li>"
  "<li>Oval cabochon in green, red or cream set in a curved center bar</li>"
  "<li>Curb chain about 0.2 in wide, extender chain at the clasp</li></ul>"
  "<p>Chain about 16 in + 2 in extender</p>",
  2,
  {1: "Cream, Red and Green, shown flat side by side", 2: "Green, Red and Cream, styled flat lay",
   3: "Red and Cream, styled flat lay", 4: "Green and Red, styled flat lay", 5: "Red, on model",
   6: "Green, close-up with measurements", 7: "Red, close-up with measurements", 8: "Cream, close-up with measurements"},
  [6, 7, 8],
  {"White": "Cream"}, {},
  ["text overlay", "variant images have text overlays"],
  "Supplier title says \"cat's eye stone\" and the measurement images say \"opal\"; neither is in the spec (stainless steel, electroplated) and the photos show plain glossy cabochons with no cat's-eye band, so the copy says only \"oval cabochon stone\". Gold-tone from the photos; the spec gives only electroplating, so no karat is claimed. Sizes from images 6-8: 41 cm + 5 cm chain, chain 5.3 mm wide, center 9.5 mm; weight 20.5 g. \"White\" shows as a milky cream stone, renamed Cream. Images 6-8 carry measurement text and are also the variant images, so they go last; no clean single-color shot exists to point the variants at. Lead is image 2 (all three colors, clean). The spec lists a brand \"Oujia Jewelry\"; no logo is visible. Description images carry decorative text (\"Fashion Items\", \"America\") and were not used.",
  {"use": True, "color": "Green", "photo_media_id": 2, "season": ALL, "open_toe": False, "occasion": ["day", "night"],
   "category": "accessory",
   "prompt_description": "A chunky gold-tone curb chain choker with a curved gold-tone center bar set with an oval green cabochon stone surrounded by tiny clear rhinestones."}))

# 5 embrace pendant
t = "Embrace Figure Pendant Necklace"
D.append(mk("9757660119279", t,
  ["jewelry", "necklace", "pendant", "hug", "gift", "alloy", "silver-tone", "gold-tone", "black", "ec-collection"],
  "<p><strong>A small sculpted pendant of two figures wrapped in a hug, on a fine silver-tone chain.</strong></p>"
  "<ul><li>Polished plated alloy, silver-tone with gold-tone or black accents</li>"
  "<li>Couple design, or mother-and-child design with a smaller figure held</li>"
  "<li>Pendant hangs from a small bail on a fine chain</li></ul>"
  "<p>One size · chain length not stated by the supplier</p>",
  1,
  {1: "Silver & Gold Couple, shown flat", 2: "Silver & Gold Mother & Child, hanging, framed shot",
   3: "Gold and Silver, pendants without chain, shown flat", 4: "Silver & Black Couple, shown flat",
   5: "Silver Mother & Child, shown flat", 6: "Silver & Black Couple, shown flat", 7: "Silver Mother & Child, shown flat"},
  [3, 2, 5],
  {"White with Gold": "Silver & Gold Couple", "White and Black": "Silver & Black Couple",
   "Short white": "Silver Mother & Child", "Short White with Gold": "Silver & Gold Mother & Child"},
  {},
  ["low-res photos", "photo color mismatch", "chain length missing"],
  "Photos win over the supplier text: the \"White\" options are silver-tone, and \"Short\" means the mother-and-child design (a smaller figure held by a taller one), so the variants are renamed by finish and design. Spec: alloy, electroplated; no chain length, pendant size or clasp is given (\"Weight: 4\" has no unit), so the size line says the length is not stated; worth asking the supplier. Image 3 shows an all-gold-tone and an all-silver-tone couple pendant without chain, neither of which is offered, so it goes last. Image 2 is a small framed shot with rounded corners (the only photo of Silver & Gold Mother & Child, and its variant image) and goes last; image 5 is a near-copy of image 7 and goes last. All photos are 696-1445 px with soft edges.",
  {"use": False, "color": "Silver & Gold Couple", "photo_media_id": 1, "season": ALL, "open_toe": False, "occasion": ["day"],
   "category": "accessory",
   "prompt_description": "A fine silver-tone chain necklace with a small sculpted pendant of two slender abstract figures in a tight hug, one silver-tone and one gold-tone."}))

# 6 beaded daisy bracelet / necklace
t = "Beaded Daisy Bracelet & Necklace"
D.append(mk("9757660184815", t,
  ["jewelry", "bracelet", "necklace", "beaded", "flower", "daisy", "stainless steel", "gold-tone", "multicolor", "summer", "ec-collection"],
  "<p><strong>A dainty gold-tone chain dotted with faceted bead daisies and tiny gold-tone balls, as a bracelet or a matching necklace.</strong></p>"
  "<ul><li>Gold-tone stainless steel chain with small faceted beads</li>"
  "<li>Daisies in one color or mixed colors, little ball stations between them</li>"
  "<li>Lobster clasp with an extender chain</li></ul>"
  "<p>Bracelet or necklace · lengths not stated by the supplier</p>",
  1,
  {1: "Red Bracelet, shown flat", 2: "all colors, bracelets shown side by side", 3: "Silver Necklace, shown flat",
   4: "Bronze Bracelet, on wrist", 5: "Red Necklace, shown flat", 6: "Black Bracelet, shown flat",
   7: "Multicolor Bracelet, shown flat", 8: "Silver Bracelet, shown flat", 9: "Bronze Bracelet, shown flat",
   10: "Green Bracelet, shown flat", 11: "Dark Red Bracelet, shown flat", 12: "Black Necklace, shown flat",
   13: "Red Necklace, shown flat", 14: "Indigo Necklace, shown flat", 15: "Multicolor Necklace, shown flat",
   16: "Bronze Necklace, shown flat", 17: "Green Necklace, shown flat", 18: "Dark Red Necklace, shown flat"},
  [5],
  {"Colorful Bracelet": "Multicolor Bracelet", "White Bracelet": "Silver Bracelet", "Bronze  Bracelet": "Bronze Bracelet",
   "Blue Necklace": "Indigo Necklace", "Colorful Necklace": "Multicolor Necklace", "Bronze  Necklace": "Bronze Necklace",
   "Dark red Necklace": "Dark Red Necklace"},
  {},
  ["brand logo", "photo color mismatch", "lengths missing"],
  "Supplier title says \"titanium steel\" and the spec says stainless steel; the copy says stainless steel. The chain is gold-tone in every photo, but no plating is named, so no karat is claimed. Bead material is not stated; the copy says only faceted beads. \"White Bracelet\" (supplier \"White K\") shows silver-gray metallic beads on the gold-tone chain, matching the Silver Necklace, so it is renamed Silver Bracelet; \"Blue Necklace\" shows deep violet-blue beads, renamed Indigo; \"Colorful\" renamed Multicolor; double spaces and \"Dark red\" fixed. Image 5 carries a red \"ZOGXIN\" logo, so it goes last. No bracelet or necklace lengths are given anywhere; worth asking the supplier. The option still mixes color and item (\"Red Bracelet\"); a separate Style option would be cleaner but needs a variant rebuild.",
  {"use": True, "color": "Red Necklace", "photo_media_id": 13, "season": ["spring", "summer"], "open_toe": False, "occasion": ["day"],
   "category": "accessory",
   "prompt_description": "A dainty gold-tone chain necklace with small red faceted bead daisy flowers with gold centers, spaced between tiny gold-tone ball beads."}))

# 7 zodiac moon
t = "Zodiac Crescent Moon Necklace"
D.append(mk("9757660250351", t,
  ["jewelry", "necklace", "pendant", "zodiac", "moon", "constellation", "alloy", "silver-tone", "ec-collection"],
  "<p><strong>A filigree crescent moon cradling a round domed pendant printed with a zodiac sign's constellation.</strong></p>"
  "<ul><li>Silver-tone plated alloy with a domed cabochon over the print</li>"
  "<li>Openwork swirl moon, sign name in small print, all 12 signs</li>"
  "<li>Pendant about 1.6 in tall, cabochon about 0.8 in across</li></ul>"
  "<p>Chain about 18 in, lobster clasp</p>",
  3,
  {1: "Libra, main view with three other signs (collage)", 2: "Libra, with measurements", 3: "Aquarius, shown flat",
   4: "Gemini, shown flat", 5: "Silver, plain white cabochon with full chain", 6: "Libra, shown flat",
   7: "Aquarius, shown flat", 8: "Gemini, shown flat", 9: "Pisces, shown flat", 10: "Cancer, shown flat",
   11: "Capricorn, shown flat", 12: "Leo, shown flat", 13: "Sagittarius, shown flat", 14: "Taurus, shown flat",
   15: "Virgo, shown flat", 16: "Aries, shown flat", 17: "Scorpio, shown flat"},
  [1, 2, 5],
  {"virgo": "Virgo"}, {"Color": "Zodiac Sign"},
  ["collage", "text overlay", "glow claim dropped", "off-brand"],
  "Supplier title says \"Luminous\" and \"Time Gem\"; the spec (alloy, electroplated) does not state glow-in-the-dark or the cabochon material, so the copy claims neither. Image 5 shows a plain white cabochon, possibly the glow face, but it matches no variant and goes last. Chain length: the spec says 51-60 cm, but the measurement image (2) says 46 cm / 18 in; the image is used. Pendant 40 mm, cabochon 20 mm from image 2. Image 1 is a collage and image 2 has text, both go last; lead is image 3 (largest clean shot, Aquarius). The option holds signs, not colors, so it is renamed Zodiac Sign and \"virgo\" re-cased. Variant photos assumed to match their sign (tiny printed labels). Printed-cabochon novelty look at a low price point; may read off-brand next to the apparel.",
  {"use": False, "color": "Silver", "photo_media_id": 3, "season": ALL, "open_toe": False, "occasion": ["day"],
   "category": "accessory",
   "prompt_description": "A silver-tone chain necklace with an openwork filigree crescent moon pendant holding a round domed cabochon printed with a glowing blue zodiac constellation on a black starry background."}))

json.dump(D, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for d in D:
    print(d['new_title'], len(re.sub('<[^>]+>', '', d['description_html'])))
