"""Phase E part A: category competition profiles (E1), concentration vs entrant survival (E2, H-D2), near-identical
product families and saturation (E3, H-D3). registry/PHASE_E_PLAN.md, frozen before this ran. Read-only.
Writes _work/phase_e_market.json and _work/cache/families.pkl. Run: python -I research/winning_products/scripts/phase_e_market.py
"""
import json
import math
import re
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse.csgraph import connected_components
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features as F  # noqa: E402
import panel  # noqa: E402
import phase_c as C  # noqa: E402

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
ROOT = panel.HUB / "research" / "winning_products"
con = sqlite3.connect(f"file:{panel.DB}?mode=ro", uri=True)
names = dict(con.execute("select category_id, category_name from categories"))
top, lists = panel.build()
top = top.copy()
R = {"plan": "registry/PHASE_E_PLAN.md"}
M = panel.MIDX
FEB_MAY = [M[m] for m in ("2026-02", "2026-03", "2026-04", "2026-05")]
JUN_SEP = [M[m] for m in ("2026-06", "2026-07", "2026-08", "2026-09")]

# ------------------------------------------------------------------ E1 category profiles
pres = set(zip(top["pid"], top["cat"], top["mi"]))
rows = []
for c, g in top[top["mi"] >= 1].groupby("cat"):
    rev_m = g.groupby("mi")["revenue"].sum()
    shares = g.groupby(["mi", "seller_id"])["revenue"].sum() / g.groupby("mi")["revenue"].sum()
    top3 = shares.groupby(level=0).apply(lambda s: s.sort_values(ascending=False).head(3).sum()).mean()
    hhi = shares.groupby(level=0).apply(lambda s: float((s ** 2).sum())).mean()
    shops = g.groupby("mi")["seller_id"].nunique().mean()
    ent, kept = 0, 0
    entr_per_month = []
    for m in range(2, M["2026-07"] + 1):  # entry months 2025-12..2026-07, survival checked at m+2
        e = g[(g["mi"] == m)]
        new = [p for p in e["pid"] if (p, c, m - 1) not in pres]
        entr_per_month.append(len(new) / 500)
        ent += len(new)
        kept += sum((p, c, m + 2) in pres for p in new)
    asp = g.groupby("mi")["asp"].median()
    rows.append({"cat": c, "name": names.get(c), "growth": rev_m.loc[JUN_SEP].mean() / rev_m.loc[FEB_MAY].mean() - 1,
                 "top3_share": top3, "hhi": hhi, "shops": shops, "entrant_rate": float(np.mean(entr_per_month)),
                 "entrant_ret2": kept / ent if ent else np.nan, "asp_median": float(g["asp"].median()),
                 "asp_trend": asp.loc[JUN_SEP].mean() / asp.loc[FEB_MAY].mean() - 1})
P = pd.DataFrame(rows)
Q = P[P["cat"] != "856720"]  # Pre-Owned excluded from terciles
t3 = Q["top3_share"].quantile([1 / 3, 2 / 3])
er = Q["entrant_ret2"].quantile([1 / 3, 0.5, 2 / 3])


def klass(r):
    if r["cat"] == "856720":
        return "Insufficient evidence"
    if r["top3_share"] >= t3.iloc[1]:
        return "Highly concentrated"
    if r["entrant_ret2"] >= er.iloc[2] and r["top3_share"] <= t3.iloc[0]:
        return "Potentially underserved"
    if r["growth"] >= 0.10 and r["entrant_ret2"] >= er.iloc[1]:
        return "Attractive emerging"
    if -0.10 <= r["growth"] <= 0.10 and r["entrant_ret2"] <= er.iloc[0]:
        return "Established but competitive"
    return "Mixed"


P["class"] = P.apply(klass, axis=1)
R["E1"] = {"thresholds": {"top3_terciles": t3.round(4).tolist(), "entrant_ret2_t1_median_t2": er.round(4).tolist()},
           "categories": P.round(4).sort_values("class").to_dict("records")}

# ------------------------------------------------------------------ E2 concentration vs entrant survival
rho, p = spearmanr(Q["top3_share"], Q["entrant_ret2"])
within = []
for m in range(2, M["2026-07"] + 1):
    cm = []
    for c, g in top[top["mi"] == m].groupby("cat"):
        if c == "856720":
            continue
        s = g.groupby("seller_id")["revenue"].sum() / g["revenue"].sum()
        new = [pp for pp in g["pid"] if (pp, c, m - 1) not in pres]
        if new:
            cm.append((s.sort_values(ascending=False).head(3).sum(), np.mean([(pp, c, m + 2) in pres for pp in new])))
    a = np.array(cm)
    within.append({"month": panel.MONTHS[m], "rho": round(float(spearmanr(a[:, 0], a[:, 1]).correlation), 3)})
neg = sum(w["rho"] < 0 for w in within)
R["E2_H-D2"] = {"rho_across_categories": round(float(rho), 3), "p": round(float(p), 4), "within_month": within,
                "months_negative": f"{neg}/{len(within)}",
                "supported": bool(rho < 0 and p < 0.05 and neg >= math.ceil(2 * len(within) / 3))}

# ------------------------------------------------------------------ E3 product families (near-identical titles)
pn = pd.read_sql_query("""select distinct p.product_id pid, q.category_id cat, p.product_name name from products p
    join pulls q using(pull_id) where q.kind='top' and q.month is not null""", con).drop_duplicates(["pid", "cat"])
pn = pn[pn["cat"].isin(top["cat"].unique())]
fam = {}
examples = []
rng = np.random.default_rng(C.SEED)
for c, g in pn.groupby("cat"):
    txt = g["name"].fillna("").str.lower().map(lambda s: re.sub(r"\d+", " ", s))
    X = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1).fit_transform(txt)
    S = (X @ X.T).tocsr()
    S.data[S.data < 0.70] = 0
    S.eliminate_zeros()
    n, lab = connected_components(S, directed=False)
    for pid, l in zip(g["pid"], lab):
        fam[(pid, c)] = f"{c}_{l}"
    sizes = pd.Series(lab).value_counts()
    multi = sizes[sizes >= 2].index.tolist()
    for l in rng.choice(multi, size=min(1, len(multi)), replace=False) if multi else []:
        examples.append({"cat": names.get(c), "titles": g["name"].values[lab == l][:4].tolist()})
top["fam"] = [fam.get((p, c)) for p, c in zip(top["pid"], top["cat"])]
fsz = pd.Series(list(fam.values())).value_counts()
R["E3_families"] = {"products": len(fam), "families": int(len(fsz)), "multi_member_families": int((fsz >= 2).sum()),
                    "products_in_multi": int(fsz[fsz >= 2].sum()), "largest": int(fsz.max()),
                    "examples": rng.permutation(examples)[:10].tolist()}
fm = top.groupby(["fam", "mi"]).agg(fam_shops=("seller_id", "nunique"), fam_size=("pid", "size"), fam_asp=("asp", "median")).reset_index()
fm_prev = fm.assign(mi=fm["mi"] + 1)[["fam", "mi", "fam_shops"]].rename(columns={"fam_shops": "fam_shops_p1"})
fm = fm.merge(fm_prev, on=["fam", "mi"], how="left").fillna({"fam_shops_p1": 0})
fm["fam_shops_chg"] = fm["fam_shops"] - fm["fam_shops_p1"]
fm.to_pickle(panel.CACHE / "families.pkl")
# descriptive: family shop growth vs next-month family ASP change (families with >= 2 products)
nxt = fm.assign(mi=fm["mi"] - 1)[["fam", "mi", "fam_asp"]].rename(columns={"fam_asp": "fam_asp_n1"})
fd = fm.merge(nxt, on=["fam", "mi"]).query("fam_size >= 2 and fam_shops_p1 >= 1")
r_asp = spearmanr(fd["fam_shops_chg"], np.log(fd["fam_asp_n1"] / fd["fam_asp"]))
R["E3_shops_vs_next_asp"] = {"family_months": len(fd), "rho": round(float(r_asp.correlation), 3), "p": round(float(r_asp.pvalue), 4)}

# ablation on Phase C M1 (T1, ranks 101-500), primary metric dAUC
D = C.D.copy()
D["fam"] = [fam.get((p, c)) for p, c in zip(D["pid"], D["cat"])]
D = D.merge(fm[["fam", "mi", "fam_shops", "fam_size", "fam_shops_chg", "fam_asp"]], on=["fam", "mi"], how="left")
D["fam_asp_rel"] = np.log(D["asp"].clip(lower=0.01) / D["fam_asp"].clip(lower=0.01))
D["log_fam_shops"], D["log_fam_size"] = np.log(D["fam_shops"]), np.log(D["fam_size"])
EXTRA = ["log_fam_shops", "log_fam_size", "fam_shops_chg", "fam_asp_rel"]
U = D[C.mid(D) & D["T1"].notna()]
dauc, dp50 = [], []
for t in C.H1_TEST:
    tr, te = U[U["mi"] <= t - 1], U[U["mi"] == t]
    full = C.metrics(te, C.fit_logit(tr, te, F.NUM + EXTRA, "T1"), "T1")
    base = C.metrics(te, C.fit_logit(tr, te, F.NUM, "T1"), "T1")
    dauc.append(full["AUC"] - base["AUC"])
    dp50.append(full["P@50"] - base["P@50"])
ci, pb = C.boot_ci(dauc)
pos = sum(d > 0 for d in dauc)
R["E3_H-D3_ablation"] = {"dAUC_mean": round(float(np.mean(dauc)), 5), "dAUC_ci95": ci, "months_positive": f"{pos}/{len(dauc)}",
                         "dP@50_mean": round(float(np.mean(dp50)), 4), "dAUC_by_month": [round(float(x), 5) for x in dauc],
                         "supported": bool(ci[0] > 0 and pos >= math.ceil(2 * len(dauc) / 3))}
# direction: logit coefficients on the full pooled set (descriptive)
import statsmodels.api as sm  # noqa: E402
Z = U[EXTRA + ["rank_pct", "log_rev_cut", "months_top_last3"]]
Z = (Z - Z.mean()) / Z.std()
mm = sm.Logit(U["T1"], sm.add_constant(Z)).fit(disp=0, method="newton")
R["E3_direction_pooled"] = {f: round(float(np.exp(mm.params[f])), 3) for f in EXTRA}

(ROOT / "_work" / "phase_e_market.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(P.sort_values("class")[["name", "class", "growth", "top3_share", "shops", "entrant_ret2", "asp_median", "asp_trend"]].round(3).to_string(index=False))
print("E2", json.dumps(R["E2_H-D2"]))
print("E3 families", json.dumps({k: v for k, v in R["E3_families"].items() if k != "examples"}))
for ex in R["E3_families"]["examples"]:
    print("   ", ex["cat"], "|", " || ".join(t[:60] for t in ex["titles"]))
print("E3 asp", R["E3_shops_vs_next_asp"], "\nE3 ablation", R["E3_H-D3_ablation"], "\nE3 direction OR/SD", R["E3_direction_pooled"])
