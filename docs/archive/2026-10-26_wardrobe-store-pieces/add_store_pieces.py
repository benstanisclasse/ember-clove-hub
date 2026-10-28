"""One-off: add the Ember & Clove store pieces to wardrobe.yaml and the one-store-piece rule to rules.yaml."""
import re
from pathlib import Path

HUB = Path(r"C:\Users\Administrator\Documents\EmberClove-Hub")
G = "gid://shopify/Product/"


def to_draft(text):
    text = re.sub(r"^status: .*$", "status: draft", text, count=1, flags=re.M)
    text = re.sub(r"^approved_by: .*$", "approved_by: null", text, count=1, flags=re.M)
    text = re.sub(r"^approved_at: .*$", "approved_at: null", text, count=1, flags=re.M)
    return re.sub(r"^approved_hash: .*\n", "", text, count=1, flags=re.M)


STORE = [
    ("ec-offshoulder-sweatshirt", "Casual Long Sleeve Off-Shoulder Sweatshirt", "knitwear", "black", "[fall, winter, spring]",
     "9756905537775", "offshoulder-sweatshirt",
     "a black cropped sweatshirt with a wide boat neckline that can slip off one shoulder, a front kangaroo pocket, dropped shoulders, full long sleeves with ribbed cuffs, and a wide ribbed band at the waist"),
    ("ec-offshoulder-tee", "Long Sleeve Asymmetric Off-Shoulder T-Shirt", "top", "heather grey", "[all]", "9756901933295",
     "offshoulder-tee",
     "a light heather-grey loose long-sleeve top in thin soft jersey with a one-shoulder neckline that leaves one shoulder bare with a thin strap across it, and a slanted asymmetric hem"),
    ("ec-crossfront-top", "Long Sleeve Cross Front V-Neck Slim Fit Top", "top", "black", "[all]", "9756890005743",
     "crossfront-top",
     "a fitted black long-sleeve top in smooth stretch fabric with a deep crossover wrap V-neckline, a seam under the bust, slightly puffed shoulders, hip length"),
    ("ec-lace-shirt", "Asymmetrical Sheer Lace Long Sleeve Shirt", "top", "black", "[all]", "9756889874671", "lace-shirt",
     "a loose black sheer chiffon blouse with wide balloon sleeves gathered into ruffled cuffs, a deep V-front edged with wide cream-and-grey lace panels over a cream lining, closed at the center with thin black ribbon ties"),
    ("ec-lace-squareneck-top", "Double-Layer Long Sleeve Square Neck Top", "top", "mustard", "[all]", "9756889612527",
     "squareneck-tee",
     "a fitted mustard-yellow floral lace long-sleeve top with a wide square neckline with scalloped lace edges, a nude lining under the lace body, and sheer lace sleeves that flare at the wrists"),
    ("ec-tie-sleeve-top", "Long Sleeve V-Neck Tie Flare Sleeve Ruched Waist Top", "top", "mocha brown", "[all]",
     "9756889252079", "tiesleeve-top",
     "a fitted mocha-brown long-sleeve knit top with an asymmetric V-neckline, a thin matching scarf tie looped around the neck with long ends, a draped ruffle peplum at the hip with an uneven hem, and flared ruffle cuffs"),
    ("ec-asym-top", "Premium Asymmetrical Long Sleeve Slim Fit T-Shirt", "top", "navy", "[all]", "9756889153775", "asym-tee",
     "a fitted navy-blue long-sleeve top in smooth stretch fabric with an asymmetric draped neckline that crosses diagonally over the chest and soft ruching at the waist"),
    ("ec-cutout-cable-sweater", "Knit Sweater with 3D Crochet Hollow-out Details", "knitwear", "cream",
     "[fall, winter, spring]", "9756888989935", "crochet-sweater",
     "a cream cable-knit crew-neck sweater with a small lattice cut-out at the center of the chest, cable panels down the front, a fitted ribbed waist and ribbed cuffs, regular length"),
    ("ec-rib-button-cardigan", "Casual Ribbed V-Neck Sweater", "knitwear", "grey-green", "[fall, winter, spring]",
     "9756888924399", "twopiece-sweater",
     "a grey-green fine-ribbed V-neck cardigan with one row of small matching buttons down the front, long fitted sleeves, hip length"),
    ("ec-stripe-cardigan", "Color-Block Stripe Knit Cardigan with Lapel", "knitwear", "red, navy, brown and grey stripes",
     "[fall, winter, spring]", "9756888498415", "stripe-cardigan",
     "a slim knit cardigan with a brown collar and small buttons down the front, in wide horizontal stripes of red, navy, brown and light grey, long sleeves with striped cuffs"),
    ("ec-stripe-polo-sweater", "Striped Polo Collar Knit Sweater", "knitwear", "brown with grey and blue stripes",
     "[fall, winter, spring]", "9751659741423", "polo-sweater",
     "a relaxed chocolate-brown knit sweater with a polo collar and open V-placket, wide horizontal stripes of light grey and royal blue across the body and sleeves, dropped shoulders, ribbed cuffs and hem"),
    ("ec-chunky-cardigan", "Chunky Knit High Neck Cardigan", "knitwear", "khaki", "[fall, winter]", "9756889022703",
     "chunky-cardigan",
     "a beige-khaki chunky rib-knit cardigan with a high stand-up collar fastened by two black buttons, black buttons down the front, small button tabs on the dropped shoulders, wide sleeves and a ribbed hem band, hip length"),
    ("ec-textured-bodysuit", "Textured Rib Mock Neck Bodysuit", "top", "off-white", "[all]", "9751657021679",
     "textured-bodysuit",
     "an off-white fitted long-sleeve bodysuit with a mock neck and fine crinkled vertical ribs, tucked in so it reads as a smooth fitted top"),
    ("ec-diagonal-bodysuit", "Diagonal Rib Mock Neck Bodysuit", "top", "black", "[all]", "9751656923375", "diagonal-bodysuit",
     "a black fitted long-sleeve bodysuit with a mock neck and raised ribs sweeping diagonally across the body, tucked in so it reads as a smooth fitted top"),
    ("ec-floral-bodysuit", "Floral Rib Knit Bodysuit", "top", "cream", "[all]", "9751656857839", "floral-bodysuit",
     "a cream fitted long-sleeve bodysuit with a crew neck, fine vertical ribs and a tone-on-tone floral pattern, tucked in so it reads as a smooth fitted top"),
    ("ec-mesh-wrap-top", "Ruched Mesh Wrap V-Neck Top", "top", "black", "[all]", "9751656759535", "mesh-wrap-top",
     "a fitted black top with a wide V-neck, gathered ruched mesh crossing over the front, and sheer black mesh long sleeves"),
    ("ec-pinstripe-skirt", "Pinstripe Pleated Mini Skirt", "bottom", "coffee pinstripe", "[fall, winter, spring]",
     "9751656366319", "pinstripe-skirt",
     "a dark coffee-brown pinstriped pleated mini skirt with a smooth flat yoke, a covered-button tab at each hip and crisp knife pleats"),
    ("ec-suede-skirt", "Asymmetric Faux Suede Midi Skirt", "bottom", "coffee brown", "[fall, winter, spring]",
     "9751656268015", "suede-skirt",
     "a coffee-brown faux-suede skirt with a curved smooth yoke flaring into a full skirt with a pointed asymmetric handkerchief hem that falls below the knee"),
    ("ec-ruffle-skirt", "Ruffle Slit Knit Midi Skirt", "bottom", "oatmeal", "[fall, winter]", "9751656104175", "ruffle-skirt",
     "an oatmeal knit skirt, high-waisted and close-fitting then softly flared to mid-calf, with a curved front slit and a small ruffle trimming the slit edge and the hem"),
    ("ec-pleated-knit-skirt", "Long Pleated Knit Skirt", "bottom", "black", "[fall, winter]", "9751656005871", "pleated-skirt",
     "a black long knit skirt with a high elastic waist and fine knife pleats that flare out to the ankle"),
    ("ec-henley-maxi-dress", "Henley Tie-Waist Rib Maxi Dress", "dress", "dark grey", "[fall, winter, spring]",
     "9751655842031", "henley-maxi",
     "a heather dark-grey fitted rib-knit long-sleeve maxi dress with a henley neckline and button placket, a matching sash wrapped and knotted at the hip, and a front slit"),
    ("ec-belted-shirt-dress", "Belted Collared Midi Shirt Dress", "dress", "khaki", "[all]", "9751655678191", "shirt-dress",
     "a light khaki long-sleeve shirt dress with an open collar and V-neckline, a slim black belt with a black buckle at the waist, soft pleats falling to a long below-the-knee length, and buttoned cuffs"),
]

TAIL = '''  - id: ec-cable-knit-dress
    name: "Cable Knit Mock Neck Midi Dress"
    category: dress
    color: caramel
    season: [fall, winter]
    store_product: "gid://shopify/Product/9751656071407"
    reference_images: [assets/EC-P01-A02-H01-V01/ref1_dress_neck_down.jpg, assets/EC-P01-A02-H01-V01/ref2_cable_slit_closeup.jpg]
    prompt_description: "the exact caramel-brown cable-knit sweater dress from the reference images: mock neck, ribbed waistband, long sleeves with ribbed cuffs, plain knit bodice, vertical cable-knit pattern down the skirt with a diagonal wrap seam, fitted through the hip, below-the-knee length, and a single straight front slit with a clean edge"
  - id: ec-turtleneck-sweater-dress
    name: "Turtleneck Rib Knit Sweater Dress"
    category: dress
    color: burgundy
    season: [fall, winter]
    store_product: "gid://shopify/Product/9751655809263"
    reference_images: [assets/EC-P02-A03-H01-V01/ref1_dress_neck_down.jpg, assets/EC-P02-A03-H01-V01/ref2_turtleneck_knit_closeup.jpg]
    prompt_description: "the exact burgundy chunky rib-knit turtleneck sweater dress from the reference images: loose slouchy fit, folded turtleneck, dropped shoulders, long full sleeves with ribbed cuffs, ribbed hem, mini length ending at mid-thigh"
'''

HEADER_OLD = """# Ember's wardrobe (besides store products). Owner 2026-10-26: she should look like she owns a lot of clothes, so the
# planner picks a different outfit for every post from this list (seeded, season-appropriate, no repeat of a full
# outfit within rules.outfits.no_repeat_outfit_days). Items are plain and unbranded. Add freely; ids must be unique."""
HEADER_NEW = """# Ember's wardrobe. Owner 2026-10-26: she should look like she owns a lot of clothes, so the planner picks a different
# outfit for every post from this list (seeded, season-appropriate, no repeat of a full outfit within
# rules.outfits.no_repeat_outfit_days). Owner 2026-10-26: "always one item from ember & clove": every outfit has exactly
# one store piece (the ec- items at the end, rules.outfits.store_pieces_per_outfit); the rest are her plain, unbranded
# basics. Store pieces carry the Shopify product, one color's listing photo, and a description written from that photo."""

w = HUB / "studio" / "bible" / "wardrobe.yaml"
s = w.read_text(encoding="utf-8")
assert HEADER_OLD in s and "ec-" not in s
s = to_draft(s.replace(HEADER_OLD, HEADER_NEW))
out = ["  # Ember & Clove store pieces: exactly one of these is in every outfit"]
for id_, name, cat, color, season, pid, img, desc in STORE:
    out += [f"  - id: {id_}", f'    name: "{name}"', f"    category: {cat}", f'    color: "{color}"',
            f"    season: {season}", f'    store_product: "{G}{pid}"',
            f"    reference_images: [studio/refs/store/{img}.jpg]", f'    prompt_description: "{desc}"']
w.write_text(s.rstrip("\n") + "\n" + "\n".join(out) + "\n" + TAIL, encoding="utf-8")

r = HUB / "studio" / "bible" / "rules.yaml"
x = r.read_text(encoding="utf-8")
old = "  no_repeat_base_piece_posts: 4   # the main piece (dress, or top + bottom) not reused within 4 posts"
assert old in x
x = x.replace(old, old + '\n  store_pieces_per_outfit: 1      # owner 2026-10-26: "always one item from ember & clove"')
r.write_text(to_draft(x), encoding="utf-8")
print(len(STORE) + 2, "store pieces added")
