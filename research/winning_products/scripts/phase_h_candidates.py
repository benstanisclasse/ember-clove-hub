"""Phase H, H2: early-stage candidate pool from the frozen Sep-2026 band predictions (registry/PHASE_H_PLAN.md).
Read-only. Writes _work/phase_h_candidates.csv (+ _skipped). Run: python -I research/winning_products/scripts/phase_h_candidates.py
"""
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import panel  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = panel.HUB / "research" / "winning_products"
EXCLUDED_CATS = {"Food & Beverages", "Books, Magazines & Audio", "Pre-Owned", "Collectibles"}
TERMS = ["supplement", "capsule", "gummies", "gummy", "vitamin", "probiotic", "creatine", "protein powder", "collagen", "tea",
         "coffee", "drink", "oral", "tablet", "medicine", "cbd", "nicotine", "vape", "ozempic",
         "softgel", "testosterone", "powder", "enzyme", "prebiotic", "electrolyte", "keto", "detox", "nmn", "ashwagandha",
         "sea moss", "shilajit", "melatonin", "edible"]
TERM_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in TERMS) + r")s?\b", re.I)
MIN_ASP, MIN_UNITS, PER_CAT = 15.0, 100, 4

con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
names = dict(con.execute("select category_id, category_name from categories"))
sep = pd.read_sql_query("""select p.product_id pid, q.category_id cat, p.product_name name, p.revenue, p.sales_volumn units,
    p.seller_name, p.launch_date, p.video_revenue from products p join pulls q using(pull_id)
    where q.month='2026-09' and q.kind in ('top','top_deep')""", con).drop_duplicates(["pid", "cat"])
for c in ("revenue", "units", "video_revenue"):
    sep[c] = sep[c].astype(float)
sep["asp"] = sep["revenue"] / sep["units"].where(lambda s: s > 0)
band = pd.read_csv(ROOT / "registry" / "forward_test_band_2026-09.csv", dtype={"pid": str, "cat": str})
band = band.merge(sep.drop(columns="revenue"), on=["pid", "cat"], how="left")
band["cat_name"] = band["cat"].map(names)
prevF = pd.read_csv(ROOT / "_work" / "phase_f_candidates.csv", dtype={"pid": str, "cat": str}).query("pool == 'B'")
reuse = {(p, c): k for p, c, k in zip(prevF["pid"], prevF["cat"], prevF["cand"])}

rows, skipped = [], []
for c, g in band.groupby("cat"):
    if names.get(c) in EXCLUDED_CATS:
        continue
    n = 0
    for _, r in g.sort_values("enter_M1", ascending=False).iterrows():
        why = None
        if pd.isna(r["name"]):
            why = "no product record"
        elif TERM_RE.search(r["name"]):
            why = f"excluded term: {TERM_RE.search(r['name']).group(0)}"
        elif not (r["asp"] >= MIN_ASP):
            why = f"ASP {r['asp']:.2f} < {MIN_ASP}"
        elif not (r["units"] >= MIN_UNITS):
            why = f"units {r['units']:.0f} < {MIN_UNITS}"
        if why:
            skipped.append({"cat_name": r["cat_name"], "pid": r["pid"], "name": r["name"], "why": why})
            continue
        n += 1
        rows.append({"cat": c, "cat_name": r["cat_name"], "pid": r["pid"], "rank": int(r["rank"]), "enter_M1": round(float(r["enter_M1"]), 4),
                     "name": r["name"], "asp": round(float(r["asp"]), 2), "revenue": float(r["revenue"]), "units": int(r["units"]),
                     "video_sh": round(float(r["video_revenue"] / r["revenue"]), 3) if r["revenue"] else None,
                     "seller": r["seller_name"], "launch_date": r["launch_date"], "reuse_phase_f": reuse.get((r["pid"], c), "")})
        if n == PER_CAT:
            break
out = pd.DataFrame(rows)
out.insert(0, "cand", [k if k else f"H{i + 1:02d}" for i, k in enumerate(out["reuse_phase_f"])])
# renumber new ones consecutively
new = [c for c in out["cand"] if c.startswith("H")]
out.loc[out["cand"].str.startswith("H"), "cand"] = [f"H{i + 1:02d}" for i in range(len(new))]
# The frozen term list misses two ingestibles (H59 diet "cutting jelly", H60 peptide). As in Phase F (EXP-F-001) they stay
# on the list and are marked ineligible, rather than patching the list after seeing the candidates (EXP-H-001).
out["ineligible"] = ["ingestible (frozen term list gap)" if c in {"H59", "H60"} else "" for c in out["cand"]]
out.to_csv(ROOT / "_work" / "phase_h_candidates.csv", index=False)
pd.DataFrame(skipped).to_csv(ROOT / "_work" / "phase_h_candidates_skipped.csv", index=False)
print(len(out), "candidates;", int((out["reuse_phase_f"] != "").sum()), "reuse Phase F files;", len(new), "new; skipped while ranking:", len(skipped))
print(out[["cand", "cat_name", "rank", "enter_M1", "asp", "units", "name"]].assign(name=out["name"].str[:55]).to_string(index=False))
