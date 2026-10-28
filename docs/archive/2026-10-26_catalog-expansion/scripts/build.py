import json,re,sys
sys.stdout.reconfigure(encoding="utf-8")
H=r"C:\Users\Administrator\Documents\EmberClove-Hub"
exp=json.load(open(H+r"\data\inbox\shopify_products_full_2026-10-26_new.json",encoding="utf-8"))
nodes={n["id"].split("/")[-1]:n for n in exp["data"]["products"]["nodes"]}
G=lambda i:"gid://shopify/MediaImage/"+i
def med(pid): return [m["id"] for m in nodes[pid]["media"]["nodes"]]
def desc_urls(pid): return re.findall(r'src="([^"]+)"',nodes[pid]["descriptionHtml"])
def alts(pid,title,specs):
    ids=med(pid); assert len(ids)==len(specs),(pid,len(ids),len(specs))
    return {i:f"{title} in {c}, {v}" for i,(c,v) in zip(ids,specs)}
def D(lead,lis,size): return f"<p><strong>{lead}</strong></p><ul>"+"".join(f"<li>{x}</li>" for x in lis)+f"</ul><p>{size}</p>"
out=[]
def add(pid,title,ptype,tags,desc,lead,alt_specs,last,addimg,cren,flags,notes):
    n=nodes[pid]; m=med(pid)
    out.append(dict(handle=n["handle"],product_id=n["id"],original_title=n["title"],new_title=title,product_type=ptype,
        tags=tags+["ec-collection"],description_html=desc,lead_media_id=(m[lead] if lead is not None else None),
        media_alts=(alts(pid,title,alt_specs) if alt_specs else {}),media_last=[m[i] for i in last],
        add_images_from_description=addimg,color_renames=cren,option_renames={},flags=flags,notes=notes))
SZ="Sizes S–XXL · Bust 43–51 in"
H_="shown on a hanger, front"
# 1 lip print
t="Lip Print Fleece Sweatshirt"
add("9756888596719",t,"Sweaters & Sweatshirts",["sweatshirt","fleece","graphic","crewneck","long-sleeve","fall"],
 D("A bold lip graphic with jewel-toned gold teeth, printed on a loose crewneck with dropped shoulders.",
   ["Polyester sweatshirt fleece","Loose fit, crew neck, ribbed cuffs and hem","Long sleeves, hip length (about 26–29 in)"],SZ),
 0,[("gray","shown flat, front"),("pink",H_),("white",H_),("sage green",H_),("black",H_),("white",H_),("pink",H_),("sage green",H_),("black",H_),("orange",H_)],
 [],[],{"Olive Green":"Sage Green"},
 ["text overlay ('Sweatshirt Only' on every photo)","no photo for Coffee","Gray variant has no image"],
 "Every gallery photo carries a small 'Sweatshirt Only' text overlay (styled over denim shorts), so none can be moved aside; lead is the plain-background gray shot. Gray variant has no image: assign the lead (41317799854319). No Coffee photo exists in the gallery. 'Olive Green' shows as a muted sage green. Supplier mentions lantern sleeves; photos show plain ribbed cuffs. Size table says 2XL, option says XXL.")
# 2 sunshine
t="Sunshine Graphic Fleece Sweatshirt"
add("9756888760559",t,"Sweaters & Sweatshirts",["sweatshirt","fleece","graphic","crewneck","long-sleeve","fall"],
 D("A retro sun-and-moon graphic with flowers and \u201cStay Magical\u201d lettering on a relaxed crewneck.",
   ["Polyester sweatshirt fleece","Loose fit, crew neck, ribbed cuffs and hem","Long sleeves, hip length (about 26–29 in)"],SZ),
 0,[("coffee","shown flat, front"),("black",H_),("sage green",H_),("gray",H_),("orange",H_),("white",H_),("pink",H_),("sage green",H_),("black",H_),("gray",H_),("orange",H_)],
 [],[],{"Olive Green":"Sage Green"},
 ["listed as hoodie (no hood)","text overlay ('Sweatshirt Only' on every photo)","Coffee variant has no image"],
 "Title says 'hoodie' but every photo shows a hoodless crewneck sweatshirt: photo wins, typed as a sweatshirt. All photos carry a small 'Sweatshirt Only' overlay. Coffee variant has no image: the lead (41317800575215) is the brown/coffee one, assign it. 'Olive Green' shows as sage green. Same base garment and size table as the Lip Print sweatshirt.")
# 3 stripe cardigan
t="Color-Block Stripe Rib Cardigan"
add("9756888498415",t,"Sweaters & Sweatshirts",["cardigan","knit","striped","collared","long-sleeve","red","fall"],
 D("Red, navy, brown and gray stripes on a fitted rib cardigan with a contrast brown polo collar.",
   ["Polyester, viscose and spandex rib knit with stretch","Slim fit, pointed collar, button front","Long sleeves, regular length (about 21–22 in)"],"Sizes S–L · Bust 29–32 in"),
 1,[("red and navy stripe","shown flat, front"),("red and navy stripe","shown flat, front"),("red and navy stripe","close-up of the collar and buttons"),("red and navy stripe","close-up of the collar and ribbing")],
 [0,2,3],[],{"Striped":"Red & Navy Stripe"},
 ["brand logo ('BBWM' neck label)"],
 "Three of four photos show a 'BBWM WOMAN' neck label; lead is the only shot without it, the labelled ones go last. Title kept clear of the store's 'Striped Polo Collar Knit Sweater'; photos show a button-front cardigan with a polo collar. Supplier says 'Pullover / Cardigan'. 'Striped' renamed to describe the actual colorway.")
# 4 double v cardigan
t="Double V-Neck Rib Cardigan"
add("9756888924399",t,"Sweaters & Sweatshirts",["cardigan","knit","rib","v-neck","long-sleeve","neutral","fall"],
 D("A fitted rib cardigan with a layered double V-neckline, so it reads as two pieces in one.",
   ["Rib knit blend","Slim fit, button front, raglan sleeves","Long sleeves, regular length (about 21–22 in)"],"Sizes S–M · Bust 30–31 in"),
 0,[("khaki","shown flat, front"),("cream","shown flat, front"),("gray","shown flat, front")],
 [],[],{"Apricot":"Cream","Green":"Charcoal"},
 ["listed as pullover sweater, photos show a cardigan","no photo for Green (Charcoal)"],
 "Listed as a 'fake two-piece sweater' pullover; every photo shows a button-front rib cardigan whose layered V-neck trim gives the faux two-piece look: photo wins. Green has no gallery image; the description's color photos show it as a dark warm charcoal, so renamed Charcoal (owner please confirm). Apricot shows as cream. Spec says crop length but the size table gives 54–55 cm, a regular length. Spec says 'Unisex'.")
# 5 cable lace-up
t="Lace-Up Cable Knit Sweater"
add("9756888989935",t,"Sweaters & Sweatshirts",["sweater","cable-knit","lace-up","crewneck","long-sleeve","fall"],
 D("Allover cable knit with a criss-cross laced keyhole at the neckline, fitted through the body.",
   ["Polyester cable knit","Slim fit, crew neck, laced keyhole front","Long sleeves, ribbed cuffs and hem (about 22–23 in long)"],"Sizes S–M · Bust 29–31 in"),
 0,[("gray","shown flat, front"),("cream, red, gray and black","all four colors shown flat"),("red","shown flat, front"),("cream","shown flat, front"),("gray","close-up of the laced neckline"),("black","shown flat, front"),("cream","shown flat, front"),("gray","shown flat, front"),("red","shown flat, front")],
 [1],[],{"Apricot":"Cream"},
 ["collage"],
 "The cut-out is a laced keyhole (cord criss-crossed through eyelets), not a lattice. Four-color collage moved last. Apricot shows as cream. Two red shots differ in shade (coral vs bright red); the variant image is the bright red. Size table lists shoulder 54 cm for S vs 35 for M (supplier typo). Spec 'waist-cinching' not visible; photos show a fitted body.")
# 6 chunky cardigan
t="Stand Collar Chunky Knit Cardigan"
add("9756889022703",t,"Sweaters & Sweatshirts",["cardigan","chunky-knit","high-neck","long-sleeve","neutral","fall"],
 D("A chunky rib cardigan with a high stand collar that buttons off-center, plus button tabs at the shoulders.",
   ["Viscose and polyester rib knit","Loose fit, dropped shoulders, full button front","Long sleeves, banded hem (about 22–23 in long)"],"Sizes S–L · Bust 44–47 in"),
 6,[("gray","shown flat, front"),("all seven colors","shown flat"),("off-white","shown flat, front"),("taupe","shown flat, front"),("khaki","close-up of the buttoned collar"),("dark red","shown flat, back"),("khaki","shown flat, front"),("black","shown flat, front")],
 [1,0,2,3],[],{"Camel":"Taupe"},
 ["photo color mismatch: Camel variant shows the gray cardigan","Dark Red variant photo is a back view","title says 'Open Front' but it buttons","brand logo ('INDEFEIR' neck label)","no photo for Brown","collage"],
 "Camel variant points to the GRAY photo (41317803196655); the supplier color order matched to the 7-color collage makes Camel the taupe one, so point it to 41317804736751 and rename to Taupe. Dark Red's only photo (41317806637295) is a back view. Title says 'Open Front' but every photo shows a full button front: photo wins. Gray, off-white and taupe shots show an 'INDEFEIR' neck label and go last with the collage; lead is the label-free khaki front. Brown appears only in the collage. 'British' dropped as brand-like.")
# 7/8 duplicates
t="Ribbon Lace Oversized Knit Cardigan"
du=desc_urls("9757005742319"); assert du==desc_urls("9757006069999")
order=[du[2],du[3],du[0],du[1],du[4]]
dd=D("An oversized cream cardigan laced with soft blue ribbon down the front and sleeves, tied in bows at the hem.",
   ["Acrylic knit","Oversized fit, button front, dropped shoulders","Long puff sleeves, hip length (about 28–29 in)"],"Sizes S–XL · Bust 47–51 in")
tg=["cardigan","knit","oversized","ribbon","long-sleeve","cream","fall"]
add("9757005742319",t,"Sweaters & Sweatshirts",tg,dd,None,None,[],order,{"Beige":"Cream"},
 ["no photos","duplicate listing (same as 9757006069999)","low-res on-model photos (750x1000, faces cropped)"],
 "No gallery images; the 5 description images are clean on-model shots (no text or logos) but low resolution and dim. Lead is the buttoned front view. Photos show a button cardigan, matching the title's 'Cardigan' rather than 'Sweater'. Identical to 9757006069999 (same description images, sizes and options): keep this one and archive the other.")
add("9757006069999",t,"Sweaters & Sweatshirts",tg,dd,None,None,[],order,{"Beige":"Cream"},
 ["duplicate listing (same as 9757005742319): archive, do not apply title","no photos"],
 "Exact duplicate of 9757005742319 (same description images, size table and options; handle ends in -1). Copy mirrors that draft for reference only; applying this title too would create two identical titles, so archive this listing instead.")
# checks
store=["Cable Knit Mock Neck Midi Dress","Long Pleated Knit Skirt","Henley Tie-Waist Rib Maxi Dress","Turtleneck Rib Knit Sweater Dress","Belted Collared Midi Shirt Dress","Ruffle Hem Mesh Mini Dress","Ruffle Slit Knit Midi Skirt","Asymmetric Faux Suede Midi Skirt","Pinstripe Pleated Mini Skirt","Malibu Beach Graphic Sweatshirt","Ruched Mesh Wrap V-Neck Top","Floral Rib Knit Bodysuit","Diagonal Rib Mock Neck Bodysuit","Textured Rib Mock Neck Bodysuit","Pheasant Print Crewneck Fleece Sweatshirt","Striped Polo Collar Knit Sweater"]
for o in out:
    pid=o["product_id"].split("/")[-1]; ids=set(med(pid))
    assert o["new_title"] not in store
    assert 3<=len(o["new_title"].split())<=5, o["new_title"]
    for i in [o["lead_media_id"]]+list(o["media_alts"])+o["media_last"]:
        assert i is None or i in ids,(pid,i)
    assert set(o["media_alts"])==ids
    vals=nodes[pid]["options"][0]["values"]
    assert all(k in vals for k in o["color_renames"])
    print(len(o["description_html"]),o["new_title"])
json.dump(out,open(H+r"\data\copy_drafts\new_2026-10-26_b.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("written",len(out))

