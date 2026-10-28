import json
D="C:/Users/Administrator/Documents/EmberClove-Hub/data/"
def h(s,b,f): return f"<p><strong>{s}</strong></p><ul><li>{b[0]}</li><li>{b[1]}</li><li>{b[2]}</li></ul><p>{f}</p>"
P=[
("floral-knitted-long-sleeve-round-neck-slim-fit-stretchy-one-piece","Floral Rib Knit Bodysuit","Tops & Bodysuits",["knit","bodysuit","long-sleeve","floral","neutral","fall"],
 h("Tonal flowers bloom across fine vertical ribs, a quiet layer that tucks away smoothly under skirts and high-waist jeans.",["Polyester rib knit with slight stretch","Slim fit, crew neck, tonal floral pattern","Long sleeves, snug bodysuit cut"],"One size · Length about 27 in"),
 "Floral Rib Knit Bodysuit in cream with a tonal flower pattern, shown flat",{"Apricot":"Cream"},
 "Supplier title calls it a 'one-piece' and specs say solid color/'Sexy' style; photos show a rib-knit bodysuit with a tonal floral pattern. 'Apricot' option is shown as cream in the photos."),
("high-neck-loose-woolen-dress","Turtleneck Rib Knit Sweater Dress","Dresses",["knit","sweater-dress","turtleneck","mini","long-sleeve","fall"],
 h("A slouchy turtleneck sweater grown into a mini dress, chunky and easy over tights and boots.",["Acrylic and polyester knit with an angora wool blend","Loose fit, folded turtleneck, dropped shoulders","Long sleeves, mini length (about 27–28 in)"],"Sizes S–3XL · Bust 44–48 in"),
 "Woman wearing the Turtleneck Rib Knit Sweater Dress in burgundy",{"Navy Blue":"Navy"},
 "Specs say 'lapel collar' but photos show a turtleneck. Length is only about 27–28 in, so it wears as a short mini/tunic. Specs say 'Gender: Unisex'. Size table labels 2XL/3XL while variant options are XXL/XXXL."),
("long-sleeve-v-neck-shawl-button-slim-fit-waist-cinching-womens-knit-long-dress","Henley Tie-Waist Rib Maxi Dress","Dresses",["knit","maxi","henley","long-sleeve","tie-waist","fall"],
 h("A buttoned henley neckline and a sash that wraps and knots at the hip give this long ribbed dress an easy, put-together line.",["Fine rib knit","Slim fit, button placket, wrap tie at the waist","Long sleeves, front slit, maxi length (about 52–53 in)"],"Sizes S–L"),
 "Henley Tie-Waist Rib Maxi Dress in pink with a knotted sash, shown flat",{},
 "Specs list no fiber content (fabric bullet kept generic). Specs say 'round neck' and title says 'V-neck shawl'; photos show a henley button placket and a wrap tie sash. 'Waist-cinching' and 'Sexy' wording dropped."),
("loose-fitting-waist-belt-dress","Belted Collared Midi Shirt Dress","Dresses",["midi","shirt-dress","belted","long-sleeve","khaki","neutral"],
 h("Soft pleats fall from a slim black belt on this khaki shirt dress, crisp for work, easy on weekends.",["Polyester shirting","Open collar, V-neckline, pleated waist with elastic back, black belt","Long sleeves, buttoned cuffs, long midi length (about 49–50 in)"],"Sizes XS–L · Bust 34–39 in"),
 "Belted Collared Midi Shirt Dress in khaki with a black belt, shown flat",{},
 "Only one color (Khaki). Supplier style text 'European and American style' dropped."),
("resort-tiered-long-sleeve-high-waist-mesh-elegant-dress","Ruffle Hem Mesh Mini Dress","Dresses",["mesh","mini","long-sleeve","ruffle","orange"],
 h("Layered ruffles at the hem and cuffs swing with every step on this close-fitting mesh mini.",["Mesh fabric","Fitted bodycon shape, high round neck","Long bell sleeves with ruffle cuffs, double-ruffle hem, about 33–35 in long"],"Sizes S–XXL · Bust 30–42 in"),
 "Ruffle Hem Mesh Mini Dress in tangerine on a dress form",{},
 "Off-brand: a tight bodycon party/club mini in bright tangerine or peacock blue, not warm-earthy cozy. Mesh may be sheer and lining is not stated. Photos are mannequin-only. Supplier 'Resort', 'Tiered' and 'Elegant' wording is misleading (only the hem is ruffled). Consider not listing."),
("womens-knit-mock-neck-bodycon-jumpsuit","Textured Rib Mock Neck Bodysuit","Tops & Bodysuits",["knit","bodysuit","mock-neck","long-sleeve","neutral","fall"],
 h("Crinkled ribs add soft texture to a clean mock neck, a smooth base under cardigans, blazers and wide-leg trousers.",["Thin knit in nylon and regenerated cellulose fiber, slight stretch","Slim fit, mock neck, textured vertical rib","Long sleeves, length about 27 in"],"One size"),
 "Textured Rib Mock Neck Bodysuit in off-white, shown flat",{"Off-white":"Off-White"},
 "Supplier title and specs call it a jumpsuit; photos show a bodysuit (no legs). 'Sexy' style tag ignored. High-cut leg; style it as a layering top."),
("grassland-turkey-pattern-printed-round-neck-fleece-hoodie","Pheasant Print Crewneck Fleece Sweatshirt","Sweaters & Sweatshirts",["sweatshirt","fleece","graphic","crewneck","long-sleeve","fall"],
 h("Pheasants take flight over tall prairie grass on this roomy crewneck, a cozy pick for cool-morning walks.",["Polyester sweatshirt fleece","Loose fit, dropped shoulders, ribbed crew neck","Long sleeves, ribbed cuffs and hem, heat-transfer print"],"Sizes S–2XL · Bust 43–51 in"),
 "Gray Pheasant Print Crewneck Fleece Sweatshirt on a hanger over denim shorts",{},
 "Supplier title says 'turkey' and 'hoodie', but the print shows pheasants and the photos show a crewneck with no hood. Photos carry a 'Sweatshirt Only' text overlay. Specs mention 'lantern sleeves', not clearly visible, so left out. Variants are S–XXL; size table labels 2XL."),
("loose-velvet-sweatshirt","Malibu Beach Graphic Sweatshirt","Sweaters & Sweatshirts",["sweatshirt","fleece","graphic","crewneck","long-sleeve"],
 h("Pink and teal varsity lettering spells out Malibu Beach on this relaxed, laid-back crewneck.",["Polyester sweatshirt fleece","Loose fit, dropped shoulders, ribbed crew neck","Long sleeves, ribbed cuffs and hem, heat-transfer print"],"Sizes S–2XL · Bust 43–51 in"),
 "Coffee brown Malibu Beach Graphic Sweatshirt with pink and teal lettering on a hanger over denim shorts",{},
 "Supplier title says 'velvet' but specs say sweatshirt fleece; 'velvet' not used. Specs and size table are identical to the pheasant sweatshirt (copied supplier template), so verify. Bright pink/teal collegiate graphic is less on-palette. Photos carry a 'Sweatshirt Only' overlay."),
("casual-high-waist-pleated-knitted-long-skirt-for-women","Long Pleated Knit Skirt","Skirts",["knit","pleated","skirt","neutral","fall"],
 h("Fine knife pleats flare from a smooth waistband and sway as you walk, lovely with a chunky sweater and boots.",["Soft acrylic, viscose and polyester knit","High elastic waist, A-line pleated flare","Long length (about 31 in), hand wash or dry clean"],"One size · Waist 24 in, elastic"),
 "Woman wearing the Long Pleated Knit Skirt in off-white with a shaggy camel jacket",{"Oats":"Oatmeal","Off-white":"Off-White"},
 "Fiber content conflicts: specs list Acrylic (fabric name) and Viscose (composition), description lists polyester; all three mentioned. Photos show it near ankle length on the model, but 80 cm (about 31 in) reads mid-calf on most heights, so 'maxi' avoided."),
("eco-friendly-suede-asymmetrical-hem-slimming-long-skirt","Asymmetric Faux Suede Midi Skirt","Skirts",["faux-suede","midi","asymmetric","skirt","brown","fall"],
 h("A curved yoke gives way to a pointed handkerchief hem on this soft faux suede skirt in rich, earthy shades.",["Polyester-blend faux suede, light stretch","Elastic waistband with belt loops, full flared skirt","Asymmetric hem, about 28–29 in long"],"Sizes S–L · Hip 45–48 in"),
 "Asymmetric Faux Suede Midi Skirt in coffee brown, shown flat",{},
 "Supplier 'Eco-Friendly' and 'Slimming' claims removed; 'suede' is polyester blend, so labeled faux suede. The 'Khaki' option looks sage/olive green in photos; consider renaming to 'Sage' after checking a real sample."),
("elegant-commuter-knitted-high-waist-a-line-irregular-ruffle-midi-skirt","Ruffle Slit Knit Midi Skirt","Skirts",["knit","midi","ruffle","skirt","neutral","fall"],
 h("A playful ruffle traces the curved front slit and hem of this soft knit skirt.",["Polyester-cotton knit","Elastic high waist, close fit easing into a soft flare","Ruffle-trimmed front slit and hem, midi length (about 31 in)"],"One size · Waist 24–39 in, elastic"),
 "Woman wearing the Ruffle Slit Knit Midi Skirt in pink with a white sweatshirt",{"Apricot":"Oatmeal","Off-white":"Off-White"},
 "First photo shows the skirt in PINK, but pink is not an option (Gray, Off-White, Apricot, Black); swap the lead image or confirm colors. Supplier 'A-line' is generous; it looks straight with a flared hem. Care per supplier: cold wash, hang dry."),
("preppy-tailored-stripe-pleated-a-line-button-womens-skirt","Pinstripe Pleated Mini Skirt","Skirts",["pinstripe","pleated","mini","skirt","fall"],
 h("Fine pinstripes and crisp pleats give this little skirt a tailored, schoolroom feel, with button tabs at each hip.",["Polyester and spandex suiting fabric","Flat yoke waist, button tab details, knife pleats","Short mini length (about 13 in)"],"Sizes S–L · Waist 28–31 in"),
 "Pinstripe Pleated Mini Skirt in coffee brown, shown flat",{},
 "Very short (about 13 in) low-slung micro-mini targeted at 'Youth' per specs; may read too young/short for the brand. Specs list spandex yet 'non-stretch', so stretch not mentioned. Body-type list in specs ignored."),
("herringbone-texture-long-sleeve-mock-neck-knit-bodysuit-women-slim-fit-base-layer","Diagonal Rib Mock Neck Bodysuit","Tops & Bodysuits",["knit","bodysuit","mock-neck","long-sleeve","base-layer"],
 h("Raised lines sweep diagonally across the body of this sleek mock-neck bodysuit, a polished base under open knits and coats.",["Regenerated cellulose fiber knit, slight stretch","Slim fit, ribbed mock neck, diagonal raised-rib detail","Long sleeves, length about 27 in"],"One size"),
 "Diagonal Rib Mock Neck Bodysuits laid out in black, coffee, dark gray, mist blue and pink",{},
 "Supplier calls it 'herringbone', but photos show diagonal raised lines, not herringbone. Specs say 'Jumpsuit' and 'Sexy/Sexy Girl'. High-cut leg; style it as a layering top. Lead image is a multi-color layout rather than a single product shot."),
("ruffled-long-sleeve-v-neck-womens-top","Ruched Mesh Wrap V-Neck Top","Tops & Bodysuits",["mesh","ruched","wrap","v-neck","long-sleeve","cropped"],
 h("Gathered mesh crosses over the front in soft folds, giving this fitted top a gentle wrap look under a cardigan or blazer.",["Polyester-blend mesh","Slim fit, crossover ruched front, wide V-neckline","Sheer mesh long sleeves, cropped length (about 15–16 in)"],"Sizes S–L"),
 "Ruched Mesh Wrap V-Neck Top in lavender, shown flat",{"Purple":"Lavender","Pink":"Blush","Apricot":"Cream"},
 "Supplier title says 'ruffled', but it is ruched, not ruffled. Sleeves are sheer mesh. Specs say 'Unisex' and 'Outerwear' (not accurate). Cropped and small (listed bust 62–70 cm). Color renames match the photos (lilac, peachy nude, cream)."),
]
out=[]
for (hd,t,pt,tags,desc,alt,cr,notes) in P:
    j=json.load(open(D+"catalog/"+hd+".json",encoding="utf-8"))
    out.append(dict(handle=hd,product_id=j["product_id"],original_title=j["original_title"],new_title=t,product_type=pt,tags=tags,description_html=desc,image_alt=alt,color_renames=cr,notes=notes))
    for k in cr: assert k in j["colors"],(hd,k)
    print(len(desc),len(t.split()),t)
titles=[o["new_title"] for o in out]; assert len(set(titles))==len(titles)
json.dump(out,open(D+"copy_drafts/apparel.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
print("ok",len(out))
