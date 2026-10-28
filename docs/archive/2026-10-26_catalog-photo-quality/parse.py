import json
T = r"C:\Users\Administrator\AppData\Local\Temp\ec_q\tool"
rows = []; nprod = 0
for f in ["products.json", "products2.json"]:
    d = json.load(open(f"{T}\\{f}", encoding="utf-8"))["data"]["products"]
    for n in d["nodes"]:
        nprod += 1
        for pos, m in enumerate(n["media"]["nodes"], 1):
            img = m.get("image") or {}
            rows.append(dict(title=n["title"], pid=n["id"], vendor=n["vendor"], mid=m["id"], pos=pos, url=img.get("url"), w=img.get("width"), h=img.get("height")))
for i, r in enumerate(rows): r["name"] = f"i{i:03d}"
json.dump(rows, open(f"{T}\\rows.json", "w", encoding="utf-8"), indent=0)
print(nprod, len(rows), [r for r in rows if not r["url"]])
with open(f"{T}\\args.txt", "w") as fh:
    for r in rows:
        if r["url"]: fh.write(f'{r["name"]}={r["url"]}\n')
