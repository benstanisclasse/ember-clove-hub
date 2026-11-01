"""Phase E part B: review themes (E4), attribute flags (E5), comment insights (E6), and the frozen review forward test.
registry/PHASE_E_PLAN.md, frozen before this ran. Read-only. Writes _work/phase_e_consumer.json and, once,
registry/forward_test_reviews_2026-09.csv. Run: python -I research/winning_products/scripts/phase_e_consumer.py
"""
import datetime as dt
import glob
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import panel  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = panel.HUB / "research" / "winning_products"
RAW = panel.HUB / "research" / "kalodata" / "raw" / "gaps_tier2"
con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
names = dict(con.execute("select category_id, category_name from categories"))
THEMES = {  # frozen in PHASE_E_PLAN.md
    "size_fit": ["too small", "too big", "runs small", "runs large", "size up", "size down", "sizing", "didn't fit", "does not fit",
                 "doesn't fit", "tight", "loose", "too short", "too long"],
    "quality": ["cheap", "cheaply", "poor quality", "flimsy", "thin", "broke", "broken", "ripped", "tore", "fell apart",
                "falling apart", "stitching", "pilling", "defective", "faded"],
    "not_as_pictured": ["not as pictured", "not like the picture", "doesn't look like", "does not look like", "looks nothing like",
                        "different from the picture", "not what i expected", "misleading", "false advertising", "color is off",
                        "not the same color"],
    "shipping": ["late", "never arrived", "never received", "shipping", "delivery", "took forever", "arrived damaged", "missing"],
    "comfort": ["comfortable", "comfy", "soft", "itchy", "scratchy", "uncomfortable"],
    "value": ["worth the money", "worth it", "great price", "overpriced", "not worth", "waste of money", "for the price"],
    "smell": ["smell", "smells", "odor", "chemical"],
    "gift": ["gift", "gifted", "for my daughter", "for my wife", "for my mom", "birthday", "christmas"],
    "compliments": ["compliment", "compliments", "everyone asked", "so many people"],
}
FLAGS = {"problem_solving": ["control", "relief", "support", "prevent", "anti", "waterproof", "pain", "fix", "protect"],
         "aesthetic": ["elegant", "stylish", "cute", "chic", "trendy", "aesthetic", "flattering"],
         "comfort": ["comfort", "soft", "breathable", "stretch"],
         "convenience": ["easy", "portable", "quick", "adjustable", "lightweight"]}
SEP_END = dt.datetime(2026, 9, 30, 23, 59, 59).timestamp()
R = {"plan": "registry/PHASE_E_PLAN.md"}

# ------------------------------------------------------------------ reviews
rows = []
for f in glob.glob(str(RAW / "reviews_*.json")):
    for x in json.load(open(f, encoding="utf-8"))["response"].get("data") or []:
        rows.append({"pid": str(x.get("product_id")), "review_id": x.get("review_id"), "rating": x.get("rating"),
                     "text": (x.get("display_text") or "").lower(), "ts": float(x.get("review_timestamp") or 0)})
rv = pd.DataFrame(rows).drop_duplicates("review_id")
rv["rating"] = pd.to_numeric(rv["rating"], errors="coerce")
for t, terms in THEMES.items():
    rv[t] = rv["text"].map(lambda s, terms=terms: any(term in s for term in terms))
rv["low"] = rv["rating"] <= 2
rv["high"] = rv["rating"] >= 4
sample = pd.read_csv(ROOT / "_work" / "tier2_sample.csv", dtype={"product_id": str, "category_id": str})
sample = sample.rename(columns={"product_id": "pid", "category_id": "cat"})


def per_product(r):
    out = {"n_reviews": len(r), "mean_rating": r["rating"].mean(), "low_star": r["low"].mean()}
    lo, hi = r[r["low"]], r[r["high"]]
    for t in THEMES:
        out[f"c_{t}"] = lo[t].mean() if len(lo) else np.nan   # complaint rate among 1-2 star reviews
        out[f"p_{t}"] = hi[t].mean() if len(hi) else np.nan   # praise mention rate among 4-5 star reviews
    out["n_low"] = len(lo)
    return pd.Series(out)


allp = rv.groupby("pid").apply(per_product).reset_index().merge(sample, on="pid", how="right")
R["E4_overall"] = {"reviews": len(rv), "products_with_reviews": int(rv["pid"].nunique()),
                   "rating_dist": rv["rating"].value_counts(normalize=True).sort_index().round(3).to_dict(),
                   "low_star_share_all": round(float(rv["low"].mean()), 3),
                   "theme_rate_in_low_star": {t: round(float(rv.loc[rv["low"], t].mean()), 3) for t in THEMES},
                   "theme_rate_in_high_star": {t: round(float(rv.loc[rv["high"], t].mean()), 3) for t in THEMES}}
bycat = {}
for c, g in rv.merge(sample[["pid", "cat"]], on="pid").groupby("cat"):
    lo = g[g["low"]]
    bycat[names.get(c, c)] = {"reviews": len(g), "low_star": round(float(g["low"].mean()), 3),
                              "top_complaints": dict(sorted(((t, round(float(lo[t].mean()), 3)) for t in THEMES), key=lambda kv: -kv[1])[:4]),
                              "top_praise": dict(sorted(((t, round(float(g[g["high"]][t].mean()), 3)) for t in THEMES), key=lambda kv: -kv[1])[:4])}
R["E4_by_category"] = bycat

# by Phase B trajectory group (descriptive, cross-sectional)
G = pd.read_pickle(panel.CACHE / "phase_b_groups.pkl")[["pid", "cat", "group"]]
gp = allp.merge(G, on=["pid", "cat"], how="left")
gp["is_A"] = gp["group"] == "A"
rng = np.random.default_rng(20261031)


def boot_diff(a, b, n=2000):
    a, b = a.dropna().values, b.dropna().values
    d = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(n)]
    return [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]


cmp = {}
for f in ("mean_rating", "low_star", "c_not_as_pictured", "c_size_fit", "c_quality", "p_comfort", "p_compliments", "p_gift"):
    a, b = gp.loc[gp["is_A"], f], gp.loc[~gp["is_A"], f]
    cmp[f] = {"sustained_A": round(float(a.mean()), 4), "others": round(float(b.mean()), 4), "diff_ci95": boot_diff(a, b)}
R["E4_sustained_vs_others"] = {"n_A": int(gp["is_A"].sum()), "n_others": int((~gp["is_A"]).sum()), "metrics": cmp,
                               "groups": gp["group"].value_counts(dropna=False).to_dict()}

# ------------------------------------------------------------------ E5 attributes and highlight flags
attr_rows, flag_rows = [], []
for f in glob.glob(str(RAW / "analysis_*.json")):
    d = json.load(open(f, encoding="utf-8"))["response"].get("data")
    if not d:
        continue
    pid = str(d.get("product_id"))
    for a in d.get("attributes") or []:
        attr_rows.append({"pid": pid, "key": a.get("key"), "value": a.get("value")})
    hl = " ".join(f"{h.get('key_word', '')} {h.get('region_text', '')}" for h in (d.get("highlights") or [])).lower()
    flag_rows.append({"pid": pid, "n_highlights": len(d.get("highlights") or []),
                      **{k: int(any(w in hl for w in ws)) for k, ws in FLAGS.items()}})
A = pd.DataFrame(attr_rows).merge(sample[["pid", "cat"]], on="pid")
FL = pd.DataFrame(flag_rows)
R["E5"] = {"products": int(FL["pid"].nunique()), "attributes_rows": len(A),
           "top_keys_by_category": {names.get(c, c): g["key"].value_counts().head(8).to_dict() for c, g in A.groupby("cat")},
           "flag_rates": FL[list(FLAGS)].mean().round(3).to_dict(),
           "flag_rates_by_category": FL.merge(sample[["pid", "cat"]], on="pid").groupby("cat")[list(FLAGS)].mean()
           .round(3).rename(index=lambda c: names.get(c, c)).to_dict("index")}

# ------------------------------------------------------------------ E6 comment insights (24): themes in pain points
ins = pd.read_sql_query("select product_id pid, pain_points, positive_points, usage_scenarios, raw_json from comment_insights", con)
pain_texts = []
for p in ins["pain_points"]:
    try:
        pain_texts += [str(x.get("view_point", "")).lower() for x in json.loads(p)]
    except Exception:
        pass
R["E6"] = {"products": len(ins), "pain_points": len(pain_texts),
           "pain_theme_counts": {t: sum(any(term in s for term in terms) for s in pain_texts) for t, terms in THEMES.items()},
           "examples": pain_texts[:12]}

# ------------------------------------------------------------------ frozen forward test (reviews dated <= 2026-09-30 only)
top, _ = panel.build()
sep_rank = top[top["month"] == "2026-09"][["pid", "cat", "rank"]]
pre = rv[rv["ts"] <= SEP_END]
fwd = pre.groupby("pid").apply(per_product).reset_index().merge(sample[["pid", "cat"]], on="pid").merge(sep_rank, on=["pid", "cat"])
fwd = fwd[fwd["rank"].between(101, 500)].merge(FL, on="pid", how="left")
R["forward"] = {"products": len(fwd), "reviews_used": int(pre["pid"].isin(fwd["pid"]).sum())}
fw = ROOT / "registry" / "forward_test_reviews_2026-09.csv"
if not fw.exists():
    fwd.to_csv(fw, index=False)
    R["forward"]["file"] = "registry/forward_test_reviews_2026-09.csv"
    R["forward"]["sha256"] = hashlib.sha256(fw.read_bytes()).hexdigest()
    R["forward"]["tests"] = ["R1: Spearman(low_star, in Oct-2026 top 500) < 0", "R2: Spearman(c_not_as_pictured, in Oct-2026 top 500) < 0"]

(ROOT / "_work" / "phase_e_consumer.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps(R["E4_overall"], indent=0))
for c, v in R["E4_by_category"].items():
    print(c, v)
print(json.dumps(R["E4_sustained_vs_others"], indent=0))
print(json.dumps({k: R["E5"][k] for k in ("products", "attributes_rows", "flag_rates")}))
for c, v in R["E5"]["top_keys_by_category"].items():
    print("  ", c, list(v)[:8])
print(json.dumps(R["E6"], indent=0)[:1500])
print(R["forward"])
