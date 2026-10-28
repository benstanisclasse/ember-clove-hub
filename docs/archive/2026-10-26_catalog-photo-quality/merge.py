import json, re
T = r"C:\Users\Administrator\AppData\Local\Temp\ec_q\tool"
rows = json.load(open(T + r"\rows.json", encoding="utf-8"))
sc = {}
for l in open(T + r"\scores.tsv"):
    p = l.strip().split("\t")
    w, h = map(int, p[1].split("x"))
    sc[p[0]] = dict(aw=w, ah=h, kb=int(p[2][:-2]), sharp=float(p[3][6:]), detail=float(p[4][7:]), p90=float(p[5][4:]))
for r in rows:
    r.update(sc[r["name"]])
    r["flag"] = r["p90"] < 600 or r["detail"] < 1.0 or min(r["aw"], r["ah"]) < 800
    r["review"] = r["flag"] or r["pos"] == 1
json.dump(rows, open(T + r"\rows2.json", "w", encoding="utf-8"), indent=0)
print("flag", sum(r["flag"] for r in rows), "review", sum(r["review"] for r in rows), "mismatch", [(r["name"], r["w"], r["h"], r["aw"], r["ah"]) for r in rows if (r["w"], r["h"]) != (r["aw"], r["ah"])])
cur = None
for r in rows:
    if r["pid"] != cur:
        cur = r["pid"]; print("\n##", r["title"][:60])
    print(f' {r["name"]} p{r["pos"]} {r["aw"]}x{r["ah"]} {r["kb"]}KB d={r["detail"]:.2f} p90={r["p90"]:.0f}{" *" if r["flag"] else ""}', end=";")
