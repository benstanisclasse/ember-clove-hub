import json, sys
src, out = sys.argv[1], sys.argv[2]
seen = {}
for line in open(src, encoding="utf-8"):
    try: rec = json.loads(line)
    except Exception: continue
    content = (rec.get("message") or {}).get("content")
    if not isinstance(content, list): continue
    for c in content:
        if c.get("type") != "tool_result": continue
        cc = c.get("content")
        texts = [x.get("text","") for x in cc] if isinstance(cc, list) else [cc or ""]
        for t in texts:
            t = t.strip()
            if t.startswith('{"data":{"products":{"pageInfo"'):
                d = json.loads(t)["data"]["products"]
                seen[d["pageInfo"]["endCursor"]] = [n["title"] for n in d["nodes"]]
titles = [t for v in seen.values() for t in v]
print(len(seen), "pages", len(titles), "titles", len(set(x.lower() for x in titles)), "unique")
open(out, "w", encoding="utf-8").write("\n".join(t.lower() for t in titles) + "\n")
