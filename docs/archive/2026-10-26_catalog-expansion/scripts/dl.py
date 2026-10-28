import json,sys,re,os,urllib.request,concurrent.futures as cf
sys.stdout.reconfigure(encoding='utf-8')
h=r"C:\Users\Administrator\Documents\EmberClove-Hub"
out=sys.argv[1]; ids=sys.argv[2].split(",")
d=json.load(open(h+r"\data\inbox\shopify_products_full_2026-10-26_new.json",encoding="utf-8"))
jobs=[]
for n in d["data"]["products"]["nodes"]:
    pid=n["id"].split("/")[-1]
    if pid not in ids: continue
    os.makedirs(os.path.join(out,pid),exist_ok=True)
    for i,m in enumerate(n["media"]["nodes"]):
        jobs.append((m["image"]["url"],os.path.join(out,pid,f"g{i:02d}_{m['id'].split('/')[-1]}.img")))
    for i,u in enumerate(re.findall(r'src="([^"]+)"',n["descriptionHtml"])):
        if u.startswith("//"): u="https:"+u
        jobs.append((u,os.path.join(out,pid,f"d{i:02d}.img")))
    with open(os.path.join(out,pid,"desc_urls.txt"),"w",encoding="utf-8") as f:
        f.write("\n".join(re.findall(r'src="([^"]+)"',n["descriptionHtml"])))
def get(j):
    u,p=j
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
        open(p,"wb").write(r); return None
    except Exception as e: return f"FAIL {u} {e}"
with cf.ThreadPoolExecutor(8) as ex:
    for r in ex.map(get,jobs):
        if r: print(r)
print("jobs",len(jobs))
