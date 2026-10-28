import json, re, sys, os, urllib.request, concurrent.futures as cf
exp, outdir = sys.argv[1], sys.argv[2]
P = json.load(open(exp, encoding="utf-8"))["data"]["products"]["nodes"]
jobs = []
for i, p in enumerate(P):
    d = os.path.join(outdir, f"p{i:02d}"); os.makedirs(d, exist_ok=True)
    for k, m in enumerate(p["media"]["nodes"]):
        jobs.append((m["image"]["url"], os.path.join(d, f"g{k+1}.jpg")))
    for k, u in enumerate(re.findall(r'<img[^>]+src="([^"]+)"', p["descriptionHtml"])):
        jobs.append((u, os.path.join(d, f"d{k+1:02d}.jpg")))
def get(j):
    u, f = j
    if os.path.exists(f): return
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        open(f, "wb").write(data)
    except Exception as e:
        print("fail", u, e)
with cf.ThreadPoolExecutor(12) as ex: list(ex.map(get, jobs))
print(len(jobs), "jobs")
