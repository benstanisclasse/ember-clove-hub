import json,sys,re
h=r"C:\Users\Administrator\Documents\EmberClove-Hub"
d=json.load(open(h+r"\data\inbox\shopify_products_full_2026-10-26_new.json",encoding="utf-8"))
ids=sys.argv[1].split(",")
for n in d["data"]["products"]["nodes"]:
    if n["id"].split("/")[-1] not in ids: continue
    print("=====",n["id"].split("/")[-1],n["handle"]); print("TITLE:",n["title"])
    for o in n["options"]: print(" OPT",o["name"],o["values"])
    for i,x in enumerate(n["media"]["nodes"]): print(f"  M{i} {x['id'].split('/')[-1]} {x['image']['width']}x{x['image']['height']}")
    vm={}
    for x in n["variants"]["nodes"]:
        k=x["title"].split(" / ")[0]; vm.setdefault(k,set()).update(m["id"].split("/")[-1] for m in x["media"]["nodes"])
    for k,v in vm.items(): print("  VAR",k,sorted(v))
    imgs=re.findall(r'src="([^"]+)"',n.get("descriptionHtml",""))
    print("  DESC_IMGS",len(imgs))
