import json, csv, os
Q = r"C:\Users\Administrator\AppData\Local\Temp\ec_q"
rows = json.load(open(Q + r"\tool\rows2.json", encoding="utf-8"))
R = lambda s: [f"i{int(x):03d}" for x in s.split()]
def rng(a, b): return [f"i{x:03d}" for x in range(a, b + 1)]
V = {}
def put(names, verdict, reason):
    for n in names: V[n] = (verdict, reason)
# SOFT
put(R("9 12 15 17"), "SOFT", "knit OK but hair/skin painterly, mild AI-upscale look")
put(rng(126, 130), "SOFT", "760px, smooth/soft metallic leather, mild compression")
put(R("158 159"), "SOFT", "slightly soft, low detail")
put(rng(160, 163), "SOFT", "640px render, clean but soft")
put(R("179 194 228 248 213"), "SOFT", "slightly soft but acceptable")
put(R("184 185 187"), "SOFT", "macro close-up, soft/blocky but detail present")
put(R("212"), "SOFT", "soft, waxy skin; stitching still visible")
put(R("266 270 271 272 273"), "SOFT", "800px, fleece mushy/soft")
put(R("287") + rng(290, 297), "SOFT", "product render slightly soft, temple text smeared")
put(R("300 301"), "SOFT", "render slightly soft")
put(R("315 319 321 322"), "SOFT", "print mockup clean; composited background jeans heavily smeared")
put(R("330"), "SOFT", "graphic posterized/smeared (print art)")
put(R("363 364 374"), "SOFT", "knit slightly soft")
put(R("398 402 403"), "SOFT", "lace slightly soft")
put(R("459 460"), "SOFT", "smooth, soft edges, product small in frame")
put(R("478 486 491 492"), "SOFT", "slightly soft/low detail")
put(R("479"), "SOFT", "waxy skin, soft rhinestones, JPEG artifacts")
put(R("487 488 489"), "SOFT", "745px lifestyle shot, soft with compression")
put(R("493 497"), "SOFT", "soft, rough cutout edges")
put(rng(515, 520), "SOFT", "750px, slightly soft")
put(R("522 524 525 526"), "SOFT", "soft, compression")
put(R("527 530 531 532"), "SOFT", "1500px but wool texture flattened (upscaled), edges clean")
put(R("564 580 001"), "SOFT", "soft / mild compression")
# BAD
put(R("000"), "BAD", "upscaled: no mesh texture, waxy plastic ruffles, soft edges")
put(R("002 004"), "BAD", "video-frame look: blurry, smeared, motion blur")
put(R("003"), "BAD", "657px video frame, soft and smeared")
put(R("046 050"), "BAD", "upscaled smear: knit/heart print mushy, waxy hands, jagged edges")
put(rng(148, 152), "BAD", "upscaled: smeared skin and strap texture, soft edges")
put(R("153 154"), "BAD", "562px and soft/smeared")
put(R("189 190"), "BAD", "over-magnified detail crop: blurry, smeared, ringing")
put(R("206 208 209 210"), "BAD", "upscaled: smeared croc texture and carpet, soft edges")
put(R("207"), "BAD", "562px and soft/smeared")
put(R("216"), "BAD", "463x617, blurry")
put(R("217"), "BAD", "327x452, very low resolution")
put(rng(218, 224), "BAD", "500x500, very low resolution")
put(R("225"), "BAD", "collage of small photos, smeared/noisy")
put(R("232"), "BAD", "upscaled: plastic toes, smeared leather texture")
put(R("258"), "BAD", "upscaled: cat fur smeared/painted")
put(R("262 263"), "BAD", "120x120 thumbnail")
put(R("288 289"), "BAD", "upscaled lifestyle shot: blurry, smeared hair/skin")
put(R("299"), "BAD", "upscaled: blurry, smeared face/frame")
put(R("399 400"), "BAD", "upscaled: lace smeared to mush, very soft")
put(rng(461, 465), "BAD", "owner reference: upscaled from small original, smeared knit, waxy skin")
put(R("511 512 514"), "BAD", "upscaled: very soft, waxy skin, smeared fabric")
put(R("523"), "BAD", "blurry, almost no detail")
extra_ok = set(R("048 051 054 513"))
out = r"C:\Users\Administrator\Documents\EmberClove-Hub\reports\photo_quality_2026-10-26.csv"
os.makedirs(os.path.dirname(out), exist_ok=True)
cnt = {}
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["product_title","product_id","vendor","media_id","position","width","height","p90","detail","verdict","reason"])
    for r in rows:
        n = r["name"]
        if n in V: v, why = V[n]
        elif r["review"] or n in extra_ok: v, why = "OK", "viewed at 100%, acceptable"
        else: v, why = "OK (not reviewed)", "above thresholds"
        cnt[v] = cnt.get(v, 0) + 1
        w.writerow([r["title"], r["pid"], r["vendor"], r["mid"], r["pos"], r["aw"], r["ah"], round(r["p90"]), round(r["detail"], 2), v, why])
print(cnt, len(rows), "reviewed", sum(1 for r in rows if r["review"] or r["name"] in extra_ok))
missing = [n for n in V if not any(r["name"] == n and (r["review"]) for r in rows)]
print("verdict on non-review", missing)
# summary per product
from collections import defaultdict
P = defaultdict(list)
for r in rows: P[(r["title"], r["pid"])].append((r["pos"], V.get(r["name"], ("OK",))[0], r["mid"], r["name"]))
for (t, pid), L in P.items():
    bad = [p for p, v, m, n in L if v == "BAD"]
    if bad: print(f"{t[:50]} | {pid} | lead={L[0][1]} | BAD {len(bad)} of {len(L)} | pos {bad}")
for n in ["i048","i051","i054","i513","i001"]:
    r = next(x for x in rows if x["name"] == n); print(n, r["title"][:30], r["pos"], r["mid"])
