import json,sys
d="C:/Users/Administrator/Documents/EmberClove-Hub/data/catalog/"
for h in sys.argv[1:]:
    j=json.load(open(d+h+".json",encoding="utf-8"))
    print("=====",h)
    for k in ["product_id","original_title","specs","colors","sizes","size_tables"]:
        print(k,":",json.dumps(j.get(k),ensure_ascii=True)[:1500])
    print("desc:",ascii(j.get("description_text"))[:600])
    print("imgs:",[g.get("url") for g in (j.get("gallery_images") or [])[:2]])
