"""Phase F step 1: candidate list from the frozen Sep-2026 forward predictions (registry/PHASE_F_PLAN.md, F1).
Read-only. Writes _work/phase_f_candidates.csv. Run: python -I research/winning_products/scripts/phase_f_candidates.py
"""
import csv
import glob
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
EXCLUDED_TERMS = ["supplement", "capsule", "gummies", "gummy", "vitamin", "probiotic", "creatine", "protein powder",
                  "collagen", "tea", "coffee", "drink", "oral", "tablet", "medicine", "cbd", "nicotine", "vape", "ozempic"]
TERM_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in EXCLUDED_TERMS) + r")s?\b", re.I)
# The frozen term list misses some ingestibles (F39 softgel, F40 capsules). Per EXP-F-001 they stay on the list and
# are marked ineligible at the matching stage, rather than patching the list after seeing the candidates.
INGESTIBLE_GAP = {"F39", "F40"}
MIN_ASP = 15.0
PER_CAT = {"A": 2, "B": 1}

con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
names = dict(con.execute("select category_id, category_name from categories"))
sep = pd.read_sql_query("""select p.product_id pid, q.category_id cat, p.product_name name, p.revenue, p.sales_volumn units,
    p.seller_name, p.launch_date from products p join pulls q using(pull_id)
    where q.month='2026-09' and q.kind in ('top','top_deep')""", con).drop_duplicates(["pid", "cat"])
sep["asp"] = sep["revenue"].astype(float) / sep["units"].astype(float).where(lambda s: s > 0)

pools = {"A": pd.read_csv(ROOT / "registry" / "forward_test_2026-09.csv", dtype={"pid": str, "cat": str})
              .query("primary_universe == 1").rename(columns={"T4_M1": "score"})[["pid", "cat", "rank", "score"]],
         "B": pd.read_csv(ROOT / "registry" / "forward_test_band_2026-09.csv", dtype={"pid": str, "cat": str})
              .rename(columns={"enter_M1": "score"})[["pid", "cat", "rank", "score"]]}

# saved CJ matches (reused first, F2)
saved = {}
for f in glob.glob(str(panel.HUB / "data" / "kalo_cj" / "cj_*.jsonl")):
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if line:
            r = __import__("json").loads(line)
            if r.get("cj_pid"):
                saved.setdefault(r.get("k"), r["cj_pid"])
k2kalo = {r["k"]: r["kalo_id"] for r in csv.DictReader(open(panel.HUB / "data" / "kalo_cj" / "winners_2026-09.csv", encoding="utf-8"))}
saved_by_kalo = {k2kalo[k]: v for k, v in saved.items() if k in k2kalo}
for r in csv.DictReader(open(panel.HUB / "research" / "kalodata" / "EASY_WINS_2026-10-31.csv", encoding="utf-8")):
    if r.get("kalodata_id") and r.get("cj_pid") and r["cj_pid"] != "EPROLO":
        saved_by_kalo.setdefault(r["kalodata_id"], r["cj_pid"])

rows, excluded = [], []
for pool, P in pools.items():
    P = P.merge(sep, on=["pid", "cat"], how="left")
    P["cat_name"] = P["cat"].map(names)
    for c, g in P.groupby("cat"):
        if names.get(c) in EXCLUDED_CATS:
            continue
        picked = 0
        for _, r in g.sort_values("score", ascending=False).iterrows():
            why = None
            if pd.isna(r["name"]):
                why = "no product record"
            elif TERM_RE.search(r["name"]):
                why = f"excluded term: {TERM_RE.search(r['name']).group(0)}"
            elif not (r["asp"] >= MIN_ASP):
                why = f"ASP {r['asp']:.2f} < {MIN_ASP}"
            if why:
                excluded.append({"pool": pool, "cat_name": r["cat_name"], "pid": r["pid"], "name": r["name"], "why": why})
                continue
            rows.append({"cand": f"{pool}{len(rows) + 1:02d}", "pool": pool, "cat": c, "cat_name": r["cat_name"], "pid": r["pid"],
                         "rank": int(r["rank"]), "score": round(float(r["score"]), 4), "name": r["name"],
                         "asp": round(float(r["asp"]), 2), "revenue": float(r["revenue"]), "units": int(float(r["units"])),
                         "seller": r["seller_name"], "launch_date": r["launch_date"], "saved_cj_pid": saved_by_kalo.get(r["pid"], "")})
            picked += 1
            if picked == PER_CAT[pool]:
                break

out = pd.DataFrame(rows)
out["cand"] = [f"F{i + 1:02d}" for i in range(len(out))]
out["ineligible"] = ["ingestible (frozen term list gap)" if c in INGESTIBLE_GAP else "" for c in out["cand"]]
out.to_csv(ROOT / "_work" / "phase_f_candidates.csv", index=False)
pd.DataFrame(excluded).to_csv(ROOT / "_work" / "phase_f_candidates_skipped.csv", index=False)
print(len(out), "candidates;", out["pool"].value_counts().to_dict(), "; skipped while ranking:", len(excluded))
print("saved CJ matches reused:", int((out["saved_cj_pid"] != "").sum()))
print(out[["cand", "pool", "cat_name", "rank", "score", "asp", "name"]].assign(name=out["name"].str[:60]).to_string(index=False))
