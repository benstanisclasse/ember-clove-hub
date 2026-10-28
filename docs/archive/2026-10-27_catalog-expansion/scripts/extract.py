import json, sys
src, out = sys.argv[1], sys.argv[2]
want = sys.argv[3].split(",")
results = []
for line in open(src, encoding="utf-8"):
    try: rec = json.loads(line)
    except Exception: continue
    msg = rec.get("message") or {}
    content = msg.get("content")
    if not isinstance(content, list): continue
    for c in content:
        if c.get("type") != "tool_result": continue
        cc = c.get("content")
        texts = [x.get("text","") for x in cc] if isinstance(cc, list) else [cc or ""]
        for t in texts:
            t = t.strip()
            if t.startswith('{"data":{"nodes"'):
                results.append(json.loads(t))
nodes = {}
for r in results:
    for n in r["data"]["nodes"]:
        if n: nodes[n["id"]] = n
order = [f"gid://shopify/Product/{i}" for i in want]
missing = [o for o in order if o not in nodes]
print("results", len(results), "missing", missing)
json.dump({"data":{"products":{"nodes":[nodes[o] for o in order]}}}, open(out,"w",encoding="utf-8"), ensure_ascii=False)
