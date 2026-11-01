"""Phase F steps 3-7: variant-level contribution economics, fulfilment confidence, price competitiveness and the H-F1
classification (registry/PHASE_F_PLAN.md F3-F7). Reads _work/phase_f_candidates.csv and the collector files
_work/cj/F*.json. Read-only. Writes _work/phase_f_variants.csv, _work/phase_f_products.csv, _work/phase_f_results.json.
Run: python -I research/winning_products/scripts/phase_f_economics.py            (economics)
     python -I research/winning_products/scripts/phase_f_economics.py --phase h  (Phase H pool, same rules)
     python -I research/winning_products/scripts/phase_f_economics.py --sample   (transcription-check sample)
"""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "_work"
ZIPS = ("10001", "60601", "90001")
FEE_PCT, FEE_FIXED = 0.029, 0.30
TARGET_PROFIT = 10.0
MAX_DAYS = 12
APPAREL = {"Womenswear & Underwear", "Menswear & Underwear", "Kids' Fashion", "Muslim Fashion", "Shoes"}
DUTY_STRESS = 0.30          # share of product cost, China-origin only (assumption, unverified)
SEED = 20261101

# --phase h reuses these frozen Phase F rules for the Phase H early-stage pool (registry/PHASE_H_PLAN.md H4)
PH = "h" if "--phase" in sys.argv and sys.argv[sys.argv.index("--phase") + 1] == "h" else "f"
cand = pd.read_csv(W / f"phase_{PH}_candidates.csv", dtype={"pid": str, "cat": str, "saved_cj_pid": str})
if PH == "h":
    cand = cand.assign(pool="H", score=cand["enter_M1"])


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def upper_days(aging):
    m = re.findall(r"\d+", str(aging or ""))
    return int(m[-1]) if m else None


def load(c):
    f = W / "cj" / f"{c}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def pick_method(methods):
    """Frozen rule F5: cheapest method with upper delivery bound <= 12 days, else cheapest overall (flagged slow)."""
    ok = []
    for m in methods or []:
        if m.get("error") or m.get("errorEn"):
            continue
        fee = num(m.get("totalPostageFee"))
        if fee is None:
            fee = num(m.get("logisticPrice"))
        if fee is None:
            continue
        ok.append({"name": m.get("logisticName"), "fee": fee + (num(m.get("taxesFee")) or 0), "taxes": num(m.get("taxesFee")) or 0,
                   "days": m.get("logisticAging"), "upper": upper_days(m.get("logisticAging"))})
    if not ok:
        return None
    fast = [m for m in ok if m["upper"] is not None and m["upper"] <= MAX_DAYS]
    best = min(fast or ok, key=lambda m: m["fee"])
    best["slow"] = not fast
    best["fastest"] = min(ok, key=lambda m: (m["upper"] if m["upper"] is not None else 999, m["fee"]))["name"]
    return best


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def econ(P, cost, ship, r, duty=0.0):
    cba = P - cost - ship - duty - (FEE_PCT * P + FEE_FIXED) - r * P
    tcac = cba - TARGET_PROFIT
    pstar = (cost + ship + duty + FEE_FIXED) / (1 - 0.5 - FEE_PCT - r)
    return {"cba": cba, "be_roas": P / cba if cba > 0 else None, "target_cac": tcac,
            "target_roas": P / tcac if tcac > 0 else None, "p_star": pstar, "premium_needed": pstar / P - 1}


if "--sample" in sys.argv:
    done = [c for c in cand["cand"] if (d := load(c)) and (d.get("match") or {}).get("score") == 2]
    k = max(7, math.ceil(0.1 * len(done)))
    pick = sorted(np.random.default_rng(SEED).choice(sorted(done), size=min(k, len(done)), replace=False).tolist())
    print(json.dumps({"eligible_score2": len(done), "sample": pick}))
    sys.exit()

vrows, prows = [], []
for _, c in cand.iterrows():
    base = {"cand": c["cand"], "pool": c["pool"], "cat_name": c["cat_name"], "kalo_pid": c["pid"], "name": c["name"],
            "rank": c["rank"], "score": c["score"], "asp": c["asp"]}
    if isinstance(c.get("ineligible"), str) and c["ineligible"]:
        prows.append({**base, "class": "Ineligible", "reason": c["ineligible"]})
        continue
    d = load(c["cand"])
    if d is None:
        prows.append({**base, "class": "Not collected", "reason": "no collector file"})
        continue
    m = d.get("match") or {}
    ms = m.get("score")
    base.update({"cj_pid": m.get("cj_pid"), "cj_name": m.get("cj_name"), "match_score": ms, "branded_cap": m.get("branded_cap"),
                 "match_note": m.get("note"), "listedNum": (d.get("detail") or {}).get("listedNum"),
                 # descriptive flag (not a rule): CJ "supplier-shipped" listings quote $0 US freight, postage is in the price
                 "supplier_shipped": (d.get("detail") or {}).get("productType") == "SUPPLIER_SHIPPED_PRODUCT" or any(
                     fq.get("origin") == "US" and fq.get("methods") and all(num(x.get("totalPostageFee")) == 0 for x in fq["methods"])
                     for fq in d.get("freight") or []) if ms == 2 else None})
    if ms is None or ms < 2:
        prows.append({**base, "class": "Not sourceable", "reason": "substitute only (score 1)" if ms == 1 else "not on CJ (score 0)"})
        continue
    V = pd.DataFrame(d.get("variants") or [])
    if V.empty:
        prows.append({**base, "class": "Not sourceable", "reason": "no variants returned"})
        continue
    V["vid"] = V["vid"].astype(str)
    V["w"] = V["variantWeight"].map(num)
    V["cost"] = V["variantSellPrice"].map(num)
    inv = pd.DataFrame(d.get("inventory") or [])
    if not inv.empty:
        inv["vid"] = inv["vid"].astype(str)
        for col in ("totalInventory", "cjInventory", "factoryInventory"):
            inv[col] = inv[col].map(num).fillna(0)
    # freight quotes by (origin, quoted vid) -> per-zip picked method
    Q = {}
    for fq in d.get("freight") or []:
        Q.setdefault((fq.get("origin"), str(fq.get("vid"))), {})[str(fq.get("zip"))] = pick_method(fq.get("methods"))
    qweights = {vid: num(V.loc[V["vid"] == vid, "w"].iloc[0]) if (V["vid"] == vid).any() else None for _, vid in Q}

    for _, v in V.iterrows():
        vi = inv[inv["vid"] == v["vid"]] if not inv.empty else pd.DataFrame()
        stock = {r["countryCode"]: r for _, r in vi.iterrows()}
        tot = float(vi["totalInventory"].sum()) if len(vi) else 0.0
        cjs = float(vi["cjInventory"].sum()) if len(vi) else 0.0
        best = None
        for origin in ("CN", "US"):
            if origin not in stock or stock[origin]["totalInventory"] <= 0:
                continue
            # quote of the lightest quoted variant that is at least as heavy as this one (else the heaviest quoted)
            qs = [(qweights.get(qv) or 0, qv) for (o, qv) in Q if o == origin]
            if not qs or v["cost"] is None:
                continue
            heavier = [q for q in qs if q[0] >= (v["w"] or 0)]
            qv = (min(heavier) if heavier else max(qs))[1]
            picks = [Q[(origin, qv)].get(z) for z in ZIPS]
            if any(p is None for p in picks):
                continue
            fees = [p["fee"] for p in picks]
            r_base = 0.05
            r_stress = 0.10 if c["cat_name"] in APPAREL else 0.05
            b = econ(c["asp"], v["cost"], float(np.mean(fees)), r_base)
            s = econ(c["asp"], v["cost"], float(max(fees)), r_stress, DUTY_STRESS * v["cost"] if origin == "CN" else 0.0)
            row = {"origin": origin, "ship_base": round(float(np.mean(fees)), 2), "ship_stress": round(float(max(fees)), 2),
                   "method": picks[0]["name"], "days": picks[0]["days"], "slow": any(p["slow"] for p in picks),
                   "fastest": picks[0]["fastest"], "quoted_vid": qv, "taxes_quoted": max(p["taxes"] for p in picks),
                   **{f"b_{k}": val for k, val in b.items()}, **{f"s_{k}": val for k, val in s.items()}}
            if best is None or row["b_cba"] > best["b_cba"]:
                best = row
        vrows.append({**base, "vid": v["vid"], "variantKey": v.get("variantKey"), "weight_g": v["w"], "cost": v["cost"],
                      "stock_total": tot, "stock_cj": cjs, "stock_us": float(stock["US"]["totalInventory"]) if "US" in stock else 0.0,
                      "in_stock": tot > 0, **(best or {})})

    pv = pd.DataFrame([r for r in vrows if r["cand"] == c["cand"]])
    ins = pv[pv["in_stock"]]
    n_var = len(pv)
    cj_total = float(ins["stock_cj"].sum())
    share_cj = float((pv["stock_cj"] > 0).mean())
    share_any = float((pv["stock_total"] > 0).mean())
    fulfil = ("High" if cj_total >= 100 and share_cj >= 0.5 else
              "Medium" if float(ins["stock_total"].sum()) >= 500 and share_any >= 0.8 else "Low")
    priced = ins.dropna(subset=["b_cba"]) if "b_cba" in ins else ins.iloc[0:0]
    prod = {**base, "n_variants": n_var, "n_in_stock": len(ins), "stock_cj_total": cj_total, "share_var_cj": round(share_cj, 3),
            "share_var_any": round(share_any, 3), "fulfilment": fulfil, "has_us_stock": bool((pv["stock_us"] > 0).any()),
            "cost_min": pv["cost"].min(), "cost_max": pv["cost"].max()}
    if priced.empty:
        prows.append({**prod, "class": "Not sourceable", "reason": "no priced in-stock variant (stock or freight missing)"})
        continue
    pr = priced.sort_values("b_cba").reset_index(drop=True)
    med = pr.iloc[(len(pr) - 1) // 2]        # lower median: conservative
    worst = pr.iloc[0]
    cheapest = priced.sort_values("cost").iloc[0]
    for tag, row in (("med", med), ("worst", worst)):
        for k in ("origin", "ship_base", "ship_stress", "method", "days", "slow", "b_cba", "b_be_roas", "b_target_cac", "b_target_roas",
                  "b_p_star", "b_premium_needed", "s_cba", "s_be_roas"):
            prod[f"{tag}_{k}"] = row.get(k)
    prod["cba_spread"] = float(pr["b_cba"].max() - pr["b_cba"].min())
    prod["cheapest_overstates_median_by"] = float(cheapest["b_cba"] - med["b_cba"])
    roas = med["b_be_roas"]
    if fulfil == "Low":
        cls, why = "Not sourceable", "fulfilment Low"
    elif roas is None or med["b_cba"] <= 0 or roas > 3.0:
        cls, why = "Not viable", "break-even ROAS > 3.0 or contribution <= 0"
    elif roas <= 2.0 and med["b_target_cac"] > 0:
        cls, why = "Feasible", ""
    else:
        cls, why = "Marginal", "break-even ROAS 2.0-3.0" if roas > 2.0 else "target CAC <= 0"
    prows.append({**prod, "class": cls, "reason": why})

VD, PD = pd.DataFrame(vrows), pd.DataFrame(prows)
VD.to_csv(W / f"phase_{PH}_variants.csv", index=False)
PD.to_csv(W / f"phase_{PH}_products.csv", index=False)

R = {"plan": "registry/PHASE_F_PLAN.md", "n_candidates": len(PD)}
order = ["Feasible", "Marginal", "Not viable", "Not sourceable", "Ineligible", "Not collected"]
n = len(PD)
R["H-F1_overall"] = {k: {"n": int((PD["class"] == k).sum()), "share": round(float((PD["class"] == k).mean()), 3),
                         "wilson95": wilson(int((PD["class"] == k).sum()), n)} for k in order}
R["by_pool"] = PD.groupby("pool")["class"].value_counts().unstack(fill_value=0).to_dict("index")
R["by_category"] = PD.groupby("cat_name")["class"].agg(lambda s: dict(s.value_counts())).to_dict()
R["match_scores"] = PD["match_score"].value_counts(dropna=False).rename(index=str).to_dict() if "match_score" in PD else {}
R["fulfilment"] = PD["fulfilment"].value_counts().to_dict() if "fulfilment" in PD else {}
E = PD[PD["class"].isin(["Feasible", "Marginal", "Not viable"])].copy()
if len(E) >= 5:
    t = pd.qcut(E["asp"], 3, labels=["low", "mid", "high"], duplicates="drop")
    rho = spearmanr(E["asp"], E["med_b_cba"])
    R["Q1_asp"] = {"spearman_asp_cba": round(float(rho.correlation), 3), "p": round(float(rho.pvalue), 4),
                   "feasible_share_by_tercile": E.assign(t=t).groupby("t", observed=True)["class"].apply(lambda s: round(float((s == "Feasible").mean()), 3)).to_dict(),
                   "asp_tercile_edges": [round(float(x), 2) for x in E["asp"].quantile([0, 1 / 3, 2 / 3, 1])]}
R["Q2_pool"] = {p: {"n": int(len(g)), "feasible": int((g["class"] == "Feasible").sum()),
                    "feasible_or_marginal": int(g["class"].isin(["Feasible", "Marginal"]).sum())} for p, g in PD.groupby("pool")}
# Q3: cost/ASP ratio vs match score, among products whose best search hit was opened (score 1-2 with a CJ price)
M = PD[PD["match_score"].isin([1, 2])].copy() if "match_score" in PD else PD.iloc[0:0]
M = M[M["cost_max"].notna()] if "cost_max" in M else M
R["Q3_cost_ratio_vs_match"] = {"testable": bool(M["match_score"].nunique() > 1) if len(M) else False, "n_with_cost": len(M),
                               "note": "variants (and so CJ cost) were collected only for score-2 matches, so cost/ASP can't be compared across scores"}
if R["Q3_cost_ratio_vs_match"]["testable"]:
    rr = spearmanr(M["cost_max"] / M["asp"], M["match_score"])
    R["Q3_cost_ratio_vs_match"]["rho"] = round(float(rr.correlation), 3)
if len(E):
    R["Q4_variant_spread"] = {"median_cba_spread": round(float(E["cba_spread"].median()), 2),
                              "share_cheapest_overstates_by_gt2": round(float((E["cheapest_overstates_median_by"] > 2).mean()), 3),
                              "n": len(E)}
    R["Q5_us_stock"] = {"share_with_us_stock": round(float(E["has_us_stock"].mean()), 3),
                        "median_origin_used": E["med_origin"].value_counts().to_dict()}
    usv = VD[VD.get("origin").eq("US")] if "origin" in VD else VD.iloc[0:0]
    cnv = VD[VD.get("origin").eq("CN")] if "origin" in VD else VD.iloc[0:0]
    R["Q5_us_stock"]["variant_ship_base_median"] = {"US": float(usv["ship_base"].median()) if len(usv) else None,
                                                    "CN": float(cnv["ship_base"].median()) if len(cnv) else None}
(W / f"phase_{PH}_results.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")
print(json.dumps(R, indent=1, default=str)[:4000])
cols = ["cand", "cat_name", "asp", "match_score", "fulfilment", "med_origin", "med_ship_base", "med_b_cba", "med_b_be_roas",
        "med_b_premium_needed", "class"]
print(PD[[c for c in cols if c in PD]].round(2).to_string(index=False))
