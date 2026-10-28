import csv
import json
import sys

sys.path.insert(0, "scripts")
import attribution  # noqa: E402

D = "research/ads/tiktok/product_tests/ec_product_test_01"
prods = json.load(open(f"{D}/products.json", encoding="utf-8"))["products"]
url = {p["test_product_id"]: p["url"] for p in prods}
url.update({
    "P011": "https://emberandclove.com/products/slim-zipper-jacket-jacket",
    "P012": "https://emberandclove.com/products/autumn-and-winter-high-heels-thick-heels-one-foot-stomping-warehouse-tube-high-pass-boots-for-women",
    "P013": "https://emberandclove.com/products/half-high-collar-knee-length-slim-fit-woolen-dress",
    "P014": "https://emberandclove.com/products/elegant-contrast-stripe-knit-cardigan-womens-top-with-lapel-collar-slimming-fit",
})
TYPE = {"A": "PRODUCT", "B": "LIFESTYLE", "C": "BENEFIT"}
HYP = {
    "A": "The product's own look, shown large on a plain studio backdrop, creates purchase interest without a setting or story.",
    "B": "Seeing the product worn in a believable, desirable real-life moment lifts purchase intent over a product-first image.",
    "C": "One concrete, verified feature or styling advantage, shown as proof, gives a clearer reason to buy than look or mood alone.",
}
# (concept, motivation, slide-1 headline, slide plan, caption sentence, expected learning)
R = [
    ("P001", "Mock Neck Side-Pleat Mini Dress", "Brown", [
        ("A", "Visual attraction", "Sculpted pleats, clean lines",
         "1 Model in the brown dress, studio cream backdrop, dress fills frame | 2 Side profile: mock neck and fitted bodice | 3 Pleats flaring at the hip, mid-step",
         "Mock neck, fitted bodice and pleats that flare from metal rings at the hip.",
         "Can a premium dress sell on silhouette alone?"),
        ("B", "Occasion need", "Holiday party, one piece",
         "1 Evening holiday dinner, warm lights, dress with sheer black tights and knee boots | 2 At the table with friends, dress visible | 3 Leaving with a long coat over the dress",
         "One dress for the holiday party. Add tights and boots and you are ready.",
         "Does a party occasion beat the dress shown on its own?"),
        ("C", "Differentiation", "The detail: metal ring pleats",
         "1 Macro of the metal ring and pleat fan | 2 Mid-shot of the bodice and mock neck | 3 Full look, walking, pleats moving",
         "The detail that makes it: pleats fanned out from metal ring hardware.",
         "Does calling out the signature detail beat mood and occasion?"),
    ]),
    ("P003", "3D Rose Blazer Mini Dress", "Black", [
        ("A", "Visual attraction", "A blazer dress with roses",
         "1 Model in the dress, plain warm backdrop, roses fully visible | 2 Three-quarter view: puffed shoulders and lapels | 3 Back view of the tailored fit",
         "Black blazer dress with red 3D roses on long green stems.",
         "Is the statement look enough on its own?"),
        ("B", "Occasion need", "The office party dress",
         "1 Office holiday party, warm evening light, dress with sheer tights and heels | 2 Toasting with colleagues | 3 Walking out with a clutch",
         "The office holiday party dress: tailored, long-sleeved, roses up front.",
         "Does the office-party setting lift purchase intent?"),
        ("C", "Outfit completion", "Blazer and dress in one",
         "1 Macro of the 3D roses on the black suiting | 2 Lapels, buttons and flap pockets | 3 Full look: no extra layer needed",
         "Blazer and dress in one piece. Nothing else to plan.",
         "Does 'outfit done' beat the look and the occasion?"),
    ]),
    ("P005", "Two-Button Notch Lapel Long Coat", "Burgundy", [
        ("A", "Visual attraction", "The long burgundy coat",
         "1 Full-length coat on a model, studio cream backdrop | 2 Wide notch lapel and brushed texture close-up | 3 Back view: dropped shoulders, below-knee length",
         "Long burgundy coat with wide notch lapels and dropped shoulders.",
         "Does the coat's color and length sell it alone?"),
        ("B", "Seasonal relevance", "Made for cold-week walks",
         "1 November city sidewalk, coat open over a cream turtleneck (cost-probe picture) | 2 Crossing the street, coat moving | 3 Arriving at a doorway, hands in pockets",
         "The long coat for November city days, over your favorite knit.",
         "Does a real cold-season setting lift intent?"),
        ("C", "Versatility", "Cut roomy to layer",
         "1 Coat over a cable-knit midi dress and boots | 2 Same coat over jeans and a sweater | 3 Same coat over black trousers for work",
         "Cut roomy and long to layer over knits, dresses and work clothes.",
         "Does the layering benefit beat the look?"),
    ]),
    ("P006", "Stand Collar Chunky Knit Cardigan", "Off-White", [
        ("A", "Visual attraction", "Chunky rib, high collar",
         "1 Model in the off-white cardigan, studio, rib texture filling frame | 2 Stand collar and off-center buttons close-up | 3 Shoulder button tabs detail",
         "Chunky rib knit with a high stand collar and button-tab shoulders.",
         "Does the knit texture alone create interest?"),
        ("B", "Seasonal relevance", "Your weekend knit",
         "1 Saturday farmers market, cardigan over jeans | 2 Browsing a bookshop | 3 Walking home, collar up",
         "The cardigan for slow weekends: chunky rib, easy fit.",
         "Does a cozy weekend scene beat the knit on its own?"),
        ("C", "Practical value", "Button it up like a jacket",
         "1 Collar buttoned up, worn as an outer layer outdoors | 2 Worn open over a dress | 3 Full button front close-up",
         "Button the stand collar up and wear it like a jacket.",
         "Does a 'two ways to wear it' benefit beat texture and mood?"),
    ]),
    ("P007", "Notch Lapel Faux Suede Blazer", "Camel", [
        ("A", "Visual attraction", "Soft faux suede, notch lapels",
         "1 Model in the camel blazer, studio, suede texture visible | 2 Yoke seam and lapels close-up | 3 Flap pockets and three-button front",
         "Relaxed faux suede blazer with notch lapels and a yoke seam.",
         "Does the suede look sell itself?"),
        ("B", "Identity", "Weekend in the city",
         "1 Late-autumn city street, blazer over a turtleneck and jeans | 2 Window table in a cafe (no mug in hand) | 3 Walking past shop fronts",
         "Faux suede over a turtleneck and jeans: the easy city look.",
         "Does a lifestyle scene lift intent over the product?"),
        ("C", "Outfit completion", "Turtleneck + jeans + this",
         "1 The three pieces shown as an outfit formula | 2 Same blazer over a striped polo sweater | 3 Same blazer with trousers for work",
         "Turtleneck, jeans and this blazer: an outfit in three pieces.",
         "Does an outfit formula beat the look and mood?"),
    ]),
    ("P009", "Fleece-Lined Hooded Zip Jacket", "Camel", [
        ("A", "Visual attraction", "Plush-lined hood, utility zip",
         "1 Model in the camel jacket, studio, hood lining visible | 2 Contrast collar and zip chest pocket close-up | 3 Back view of the relaxed, oversized fit",
         "Utility zip jacket with a plush-lined hood and contrast collar.",
         "Does the utility look sell on its own?"),
        ("B", "Practical value", "Cold-morning errands",
         "1 Frosty morning walking a dog in a park, hood down | 2 Loading a grocery bag into a car | 3 Hood up against the wind",
         "The easy top layer for cold mornings and quick errands.",
         "Does an everyday cold-weather moment beat the product shot?"),
        ("C", "Practical value", "Lined where it counts",
         "1 Hood turned out to show the plush lining | 2 Inside front showing the fleece lining | 3 Zipped up over a knit, oversized fit",
         "Plush fleece lining in the hood and body, oversized over your knits.",
         "Does showing the lining (a concrete feature) beat look and mood?"),
    ]),
    ("P011", "Snap Collar Faux Leather Jacket", "Black", [
        ("A", "Visual attraction", "Black moto, polished collar",
         "1 Model in the zipped black jacket, studio | 2 Snap-tab stand collar close-up | 3 Zip pockets and shaped waist seams",
         "Fitted faux leather moto jacket with a snap-tab stand collar.",
         "Does the jacket's look alone create interest?"),
        ("B", "Identity", "Dinner downtown",
         "1 Evening street, jacket over a knit dress and knee boots | 2 At a restaurant door | 3 Walking with a friend, city lights",
         "A black moto over your knit dress for dinner downtown.",
         "Does an evening lifestyle scene lift intent?"),
        ("C", "Versatility", "One jacket, three outfits",
         "1 Over a cable-knit midi dress with boots | 2 Over a sweater and jeans | 3 Over a black mini with tights",
         "One black jacket, three outfits: dresses, jeans and minis.",
         "Does showing versatility beat look and mood?"),
    ]),
    ("P012", "Snap Button Fold-Over Knee Boots", "Beige", [
        ("A", "Visual attraction", "Fold-over cuff, brass snaps",
         "1 Boots worn, knees down, studio backdrop, snaps and cuff in focus | 2 Side view of the 2.8 in block heel | 3 The pair standing side by side",
         "Knee-high boots with a fold-over cuff, brass snaps and a block heel.",
         "Do the boots sell on their design?"),
        ("B", "Outfit completion", "Boots for every dress",
         "1 Walking in a caramel cable-knit midi dress and the boots | 2 Sitting on a step, slit showing the shaft | 3 Climbing stairs, hem and boots in frame",
         "The knee boots your sweater dresses have been waiting for.",
         "Does a styled outfit moment beat the product shot?"),
        ("C", "Versatility", "One pair, three outfits",
         "1 With a midi knit dress | 2 With a mini skirt and tights | 3 With straight jeans over the shaft",
         "One pair, three outfits: midi dress, mini and jeans.",
         "Does versatility beat the design and the outfit moment?"),
    ]),
    ("P013", "Cable Knit Mock Neck Midi Dress", "Caramel", [
        ("A", "Visual attraction", "Cable knit, mock neck, midi",
         "1 Model in the caramel dress, studio, full length | 2 Cable knit and mock neck close-up | 3 Back view of the fitted shape",
         "Cable knit sweater dress with a mock neck, long sleeves and midi length.",
         "Does the dress sell on its look alone?"),
        ("B", "Occasion need", "Holiday plans, one dress",
         "1 Family holiday dinner, warm light, dress with knee boots | 2 Greeting guests at the door | 3 By a window during a toast",
         "One dress for every holiday plan: dinners, visits and photos.",
         "Does a holiday occasion beat the plain look?"),
        ("C", "Outfit completion", "The slit makes boots work",
         "1 Mid-stride, front slit opening over tall boots | 2 Slit and boot shaft close-up | 3 Full look, seated",
         "A front slit that shows off tall boots and keeps you moving.",
         "Does the boots-and-slit benefit beat look and occasion?"),
    ]),
    ("P014", "Striped Polo Collar Knit Sweater", "Navy & Green Color Block", [
        ("A", "Visual attraction", "Stripes with a polo collar",
         "1 Model in the sweater, studio, stripes and collar fill frame | 2 Open polo collar close-up | 3 Ribbed cuffs and hem",
         "Bold stripes and a soft open polo collar in a relaxed knit.",
         "Does the striped look sell alone?"),
        ("B", "Identity", "Easy weekend, put-together",
         "1 Weekend brunch walk, sweater with jeans and loafers | 2 Choosing flowers at a market stall | 3 Laughing on a bench",
         "Stripes and a polo collar: weekend easy, still put-together.",
         "Does a weekend scene lift intent over the product?"),
        ("C", "Versatility", "Jeans to skirt to office",
         "1 With straight jeans | 2 Tucked into a midi skirt | 3 Under a faux suede blazer for work",
         "One sweater, three outfits: jeans, a skirt or under a blazer.",
         "Does versatility beat look and mood?"),
    ]),
]

rows = []
for pid, title, var, cons in R:
    for c, mot, head, slides, cap, learn in cons:
        caption = f"{cap} #aigenerated"
        assert len(caption) <= 100, (pid, c, len(caption), caption)
        content = f"{pid.lower()}_{c.lower()}"
        rows.append({
            "experiment_id": f"T01-{pid}-{c}", "ad_name": f"EC_TT_{pid}_{c}_{TYPE[c]}", "product_id": pid,
            "product": title, "variant": var, "concept": f"{c} {TYPE[c].title()}", "hypothesis": HYP[c],
            "motivation": mot, "slide1_headline": head, "slides": slides, "caption": caption,
            "caption_chars": len(caption), "cta": "Shop now", "expected_learning": learn,
            "primary_metric": "Cost per Shopify purchase vs break-even CPA",
            "landing_page": attribution.tag_link(url[pid], "tiktok_ads", "ec_product_test_01", content),
            "status": "designed",
        })
with open(f"{D}/creative_matrix.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
lines = []
for pid, title, var, cons in R:
    lines.append(f"\n### {pid} {title} (variant shown: {var})\n")
    lines.append("| Ad | Motivation | Slide 1 headline | Slides | Caption (≤100 chars) | What we learn |")
    lines.append("|---|---|---|---|---|---|")
    for r in [r for r in rows if r["product_id"] == pid]:
        lines.append(f"| {r['ad_name']} | {r['motivation']} | {r['slide1_headline']} | {r['slides']} | {r['caption']} | {r['expected_learning']} |")
open(f"{D}/_section7.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(len(rows), "rows; longest caption", max(r["caption_chars"] for r in rows))
