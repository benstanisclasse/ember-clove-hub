import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
HUB = r'C:/Users/Administrator/Documents/EmberClove-Hub'
nodes = json.load(open(HUB + '/data/inbox/shopify_products_full_2026-10-26_new.json', encoding='utf-8'))['data']['products']['nodes']
byid = {n['id'].split('/')[-1]: n for n in nodes}


def D(lead, a, b, c, size):
    return f'<p><strong>{lead}</strong></p><ul><li>{a}</li><li>{b}</li><li>{c}</li></ul><p>{size}</p>'


P = [
dict(pid='9756889153775', title='Asymmetric Drape Neck Knit Top',
 tags=['knit', 'top', 'long-sleeve', 'asymmetric', 'ruched', 'neutral', 'fall'],
 desc=D('A folded drape cuts across the neckline at an angle, with soft gathers at the side waist on a close, fitted knit.',
        'Soft rayon and cotton blend knit', 'Slim fit, asymmetric draped neckline, ruched side waist',
        'Long sleeves, lettuce-edge hems, length about 20–21 in', 'Sizes S–L'),
 lead=3, last=[1],
 alts=['Mauve, shown flat', 'Black, Navy, Gray, Cream, Pink and Mauve, shown together', 'Pink, shown flat',
       'Cream, shown flat', 'Mauve, close-up of the draped neckline', 'Gray, shown flat', 'Navy, shown flat', 'Black, shown flat'],
 colors={'Light Purple': 'Mauve', 'Rose Red': 'Pink', 'Apricot': 'Cream', 'Navy Blue': 'Navy'},
 flags=[],
 notes="Supplier title says 'Premium' and 'T-shirt'; photos show a fitted knit top with a draped asymmetric neckline and ruched side waist. Color renames match the photos: 'Light Purple' is a dusty mauve, 'Rose Red' is a mid pink, 'Apricot' is cream. Listed bust is only 62–70 cm (stretch knit), so the size line gives sizes only, as on the Ruched Mesh Wrap V-Neck Top. Lead moved to the cream flat shot (warm neutral); the six-color collage goes last."),
dict(pid='9756889252079', title='Tie Neck Ruffle Hem Top',
 tags=['knit', 'top', 'long-sleeve', 'tie-neck', 'ruffle', 'brown', 'fall'],
 desc=D('A slim strap loops around the neck and falls as a long tie over a crossover V, ending in a ruched, ruffled hem.',
        'Stretch rib knit', 'Slim fit, crossover V-neck, ruched side waist',
        'Long bell-cuff sleeves, asymmetric ruffle hem, length about 23–24 in', 'Sizes S–L'),
 lead=2, last=[1],
 alts=['Peach, shown flat', 'Black, Coffee, Olive, Peach and Beige, shown together', 'Coffee, shown flat',
       'Beige, close-up of the neck strap and tie', 'Beige, shown flat'],
 colors={'Yellow-Green': 'Olive', 'Orange Pink': 'Peach'},
 flags=['no single gallery photo for Olive or Black (collage only)'],
 notes="Supplier title says 'flare sleeve' and specs say 'U-neck'; photos show a crossover V-neck with a neck strap that ends in a long tie, bell cuffs and an asymmetric ruffle peplum hem. Fabric content not listed (size table says 'knitted fabric, elastic'). 'Yellow-Green' is an olive/chartreuse and 'Orange Pink' is peach in the photos. Listed bust 62–70 cm (stretch), so sizes only. Specs call it 'Outerwear' (not accurate)."),
dict(pid='9756889612527', title='Scalloped Square Neck Lace Top',
 tags=['lace', 'top', 'square-neck', 'long-sleeve', 'sheer-sleeve', 'yellow', 'fall'],
 desc=D('Floral lace over a nude lining, finished with a scalloped square neckline and long, slightly flared sheer sleeves.',
        'Nylon floral lace with a nude lining in the body', 'Slim fit, square neck with a scalloped lace edge',
        'Long sheer lace sleeves, length about 19–20 in', 'Sizes S–L'),
 lead=0, last=[1],
 alts=['Mustard, shown flat', 'Black, White and Mustard, shown together'],
 colors={'Khaki': 'Mustard'},
 flags=['photo/title mismatch: listed as double-layer embossed T-shirt, photos show a lace top',
        'photo color mismatch: Khaki shown as mustard',
        'only 2 gallery images; White and Black appear only in the collage'],
 notes="Listed as a 'double-layer embossed square neck T-shirt', but every photo shows a floral lace square-neck top lined in nude (the 'double layer' is lace over lining); copy follows the photos. 'Khaki' is mustard/golden yellow in every photo. Specs say 'Unisex' and 'Outerwear' (ignored). Listed bust 78–86 cm with stretch, so sizes only. The description has clean single-color shots of White and Black that could be added to the gallery later."),
dict(pid='9756889874671', title='Lace Panel Sheer Chiffon Blouse',
 tags=['chiffon', 'blouse', 'lace', 'sheer', 'long-sleeve', 'black', 'spring'],
 desc=D('Airy chiffon falls into wide batwing sleeves, with a cream lace V-panel and two ribbon ties down the front.',
        'Sheer polyester chiffon with lace trim, no stretch', 'Loose fit, lace V-panel front, ribbon ties',
        'Batwing sleeves, gathered cuffs, pointed hem, length about 27–28 in', 'Sizes XS–L'),
 lead=4, last=[1, 3],
 alts=['Red, shown flat', 'Mustard, Coffee, Black, Red and Ivory, shown together', 'Mustard, shown flat',
       'Mustard, shown flat with sleeves spread', 'Black, shown flat', 'Ivory, shown flat', 'Red, shown flat, close view'],
 colors={'As shown in the picture': 'Mustard', 'White': 'Ivory'},
 flags=['brand logo: woven neck label on the Mustard image and collage',
        "variant named 'As shown in the picture' (renamed Mustard)",
        'no gallery photo for Coffee', 'near-duplicate red images'],
 notes="Supplier title says 'asymmetrical shirt'; photos show a loose sheer chiffon blouse with batwing sleeves, cream lace V-panel, ribbon ties, gathered cuffs and a pointed handkerchief hem. The 'As shown in the picture' variant photo is the mustard one, so it is renamed Mustard; that image (and the collage) shows a readable brand neck label, so both move last. White reads ivory. Coffee only appears in the collage and description. Bust 'reference' of 166–178 cm is the batwing span, so sizes only. Three description close-ups carry 1688.com watermarks (not in gallery). The two red gallery images are the same shot at different crops."),
dict(pid='9756890005743', title='Crossover Rib Waist Top',
 tags=['knit', 'top', 'v-neck', 'long-sleeve', 'cropped', 'neutral', 'fall'],
 desc=D('A crossover V-neck sits above a fitted rib-knit waist panel for a clean empire line and a short, cropped length.',
        'Soft rayon blend knit', 'Slim fit, crossover V-neck, rib-knit waist panel',
        'Long sleeves with gathered shoulders, cropped length about 18 in', 'Sizes S–M'),
 lead=0, last=[],
 alts=['Blush, shown flat', 'White, shown flat', 'Blush, close-up of the crossover neckline', 'Black, shown flat'],
 colors={'Pink': 'Blush'},
 flags=['no gallery photo for Gray'],
 notes="Photos match the supplier title: crossover V-neck, rib-knit waist panel, slight puff at the shoulders. 'Pink' is a pale blush/nude, renamed Blush as on the Ruched Mesh Wrap V-Neck Top. Gray (a dark heather) appears only in the description photos. Specs say 'Unisex' and 'Outerwear' (ignored). Listed bust 70–74 cm (stretch), so sizes only. Title avoids 'Wrap V-Neck Top' to stay clear of the existing Ruched Mesh Wrap V-Neck Top."),
dict(pid='9756901933295', title='Strappy One-Shoulder Jersey Top',
 tags=['jersey', 'top', 'one-shoulder', 'long-sleeve', 'gray', 'neutral'],
 desc=D('One bare shoulder with a thin strap on that side and an angled hem give this relaxed long-sleeve tee an easy shape.',
        'Soft, lightweight jersey knit', 'Relaxed fit, one-shoulder neckline with a thin strap',
        'Long sleeves, asymmetric hem, length about 24–25 in', 'Sizes S–M · Bust 44–46 in'),
 lead=0, last=[1],
 alts=['Gray, shown flat', 'Black, White and Gray, shown together', 'Gray, close-up of the shoulder strap'],
 colors={},
 flags=['fabric content not listed', 'White and Black appear only in the collage'],
 notes="Supplier says 'off-shoulder' and 'slim fit'; photos show a one-shoulder tee with a thin strap over the bare shoulder and a relaxed, dolman-like body (listed bust 112–116 cm). Specs give no fabric; 'jersey knit' is from the photos, please confirm content. 'Sweet & Spicy' style tag ignored."),
dict(pid='9756905537775', title='Boat Neck Cropped Pocket Sweatshirt', type='Sweaters & Sweatshirts',
 tags=['sweatshirt', 'cropped', 'boat-neck', 'pocket', 'long-sleeve', 'neutral', 'fall'],
 desc=D('A wide boat neck, kangaroo pocket and cropped ribbed hem make an easy weekend sweatshirt.',
        'Sweatshirt knit with a brushed inside', 'Loose fit, dropped shoulders, wide boat neck, front pocket',
        'Long sleeves with ribbed cuffs, cropped length about 23 in', 'Sizes S–M · Bust 43–44 in'),
 lead=2, last=[1],
 alts=['Lime, shown flat', 'Black, Heather Gray and Lime, shown together', 'Heather Gray, shown flat',
       'Black, shown flat', 'Lime, close-up of the boat neck'],
 colors={'Green': 'Lime', 'White Gray': 'Heather Gray'},
 flags=['off-brand color: neon lime', 'not off-shoulder in photos: wide boat neck', 'fabric content not listed'],
 notes="Supplier title says 'off-shoulder'; photos show a wide boat neck worn on the shoulders, so the copy says boat neck. 'Green' is a bright neon lime (off the store's warm palette); lead moved to Heather Gray. 'White Gray' is a heather gray. Brushed interior is visible at the neckline; fabric content is not listed in specs, please confirm."),
dict(pid='9756949676271', title='Tie-Front Ruffle Lace Top',
 tags=['lace', 'top', 'square-neck', 'tie-front', 'long-sleeve', 'brown', 'fall'],
 desc=D('Rose-pattern lace gathers under a ruffled square neckline with a small front tie, over a nude-lined bust.',
        'Stretch lace, 90% polyester and 10% spandex', 'Slim fit, ruffled square neck, gathered bust with tie',
        'Sheer long sleeves, lettuce-edge hems, length about 19–20 in', 'Sizes S–L'),
 lead=0, last=[1],
 alts=['Coffee, shown flat', 'Black, Burgundy, Ivory and Coffee, shown together', 'Burgundy, shown flat',
       'Ivory, shown flat', 'Coffee, close-up of the tie neckline', 'Black, shown flat'],
 colors={'White': 'Ivory'},
 flags=["'Sexy' dropped from title", 'title said short sleeve; photos show long sleeves'],
 notes="Supplier title says 'Sexy' and 'short sleeve'; photos (and specs) show long sleeves. Rose-pattern stretch lace with a ruffled, gathered square neckline, front tie and a nude lining at the bust; lettuce-edge hem and cuffs. 'White' reads ivory. Specs list 'Wine Red' while the option is Burgundy (kept). Listed bust 72–80 cm (stretch), so sizes only. 'Sweet & Spicy, Sexy Chic' style tags ignored."),
]

existing = """Cable Knit Mock Neck Midi Dress, Long Pleated Knit Skirt, Henley Tie-Waist Rib Maxi Dress, Turtleneck Rib Knit Sweater Dress, Belted Collared Midi Shirt Dress, Ruffle Hem Mesh Mini Dress, Ruffle Slit Knit Midi Skirt, Asymmetric Faux Suede Midi Skirt, Pinstripe Pleated Mini Skirt, Malibu Beach Graphic Sweatshirt, Ruched Mesh Wrap V-Neck Top, Floral Rib Knit Bodysuit, Diagonal Rib Mock Neck Bodysuit, Textured Rib Mock Neck Bodysuit, Pheasant Print Crewneck Fleece Sweatshirt, Striped Polo Collar Knit Sweater""".split(', ')
bad = re.compile(r'sexy|slimming|flattering|\beco|premium|warm|waterproof|women', re.I)

out = []
seen = set()
for p in P:
    n = byid[p['pid']]
    media = [m['id'] for m in n['media']['nodes']]
    assert len(p['alts']) == len(media), (p['pid'], len(media))
    t = p['title']
    assert t not in seen and t not in existing
    seen.add(t)
    assert 3 <= len(t.split()) <= 5
    optvals = {v for o in n['options'] for v in o['values']}
    for k in p['colors']:
        assert k in optvals, (p['pid'], k)
    assert not bad.search(t + p['desc']), t
    text_len = len(re.sub('<[^>]+>', '', p['desc']))
    print(p['pid'], t, '| html', len(p['desc']), 'text', text_len)
    out.append(dict(
        handle=n['handle'], product_id=n['id'], original_title=n['title'], new_title=t,
        product_type=p.get('type', 'Tops & Bodysuits'), tags=p['tags'] + ['ec-collection'],
        description_html=p['desc'], lead_media_id=media[p['lead']],
        media_alts={m: f"{t} in {a}" for m, a in zip(media, p['alts'])},
        media_last=[media[i] for i in p['last']], add_images_from_description=[],
        color_renames=p['colors'], option_renames={}, flags=p['flags'], notes=p['notes']))

json.dump(out, open(HUB + '/data/copy_drafts/new_2026-10-26_c.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('written', len(out))
