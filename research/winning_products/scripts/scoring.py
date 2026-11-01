"""Phase G candidate scoring (registry/PHASE_G_PLAN.md G4), shared with Phase H (PHASE_H_PLAN.md H4).
score(S, r5) takes the merged candidate/economics frame and returns one row per candidate with gates, the four scores
and risk flags. r5=True applies Phase G's demand gate R5 (>= $10k and >= 300 units); Phase H replaces it with its
pre-CJ floor (units >= 100) and passes r5=False.
"""
import pandas as pd

GENERIC = {"women", "womens", "women's", "men's", "mens", "kids", "baby", "premium", "portable", "electric", "automatic", "free",
           "upgraded", "new", "with", "the", "and", "for", "set", "pack", "pcs", "piece", "large", "small", "smart"}
ADULT_FLAGS = {"children": ["kid", "kids", "child", "children", "baby", "infant", "toddler"],
               "battery_electrical": ["battery", "rechargeable", "electric", "charging", "usb", "bluetooth", "printer"],
               "safety_critical": ["hitch", "towing", "tow ", "brake", "helmet", "car seat", "ladder", "propane", "torch", "gas "]}
SIZING = {"Womenswear & Underwear", "Menswear & Underwear", "Kids' Fashion", "Muslim Fashion", "Shoes"}
LEVEL = {"Strong": 0, "Moderate": 1, "Weak": 2}


def brand_tokens(name, seller):
    toks = set()
    first = str(name).replace("[", " ").replace("]", " ").split()
    # brand = first title word + seller name words (first version also took the 2nd title word; it matched "deep" in
    # "Wingslove Deep V", an implementation bug fixed before reporting, recorded in EXP-G-001)
    for w in first[:1] + str(seller).replace("&", " ").split():
        w = w.strip("|:,.-®™").lower()
        if len(w) >= 4 and w.isalpha() and w not in GENERIC:
            toks.add(w)
    return toks


def score(S, r5=True):
    rows = []
    for _, r in S.iterrows():
        gates = []
        if r["class"] == "Ineligible":
            gates.append("R1")
        if not (r.get("match_score") == 2):
            gates.append("R2")
        if r.get("fulfilment") == "Low":
            gates.append("R3")
        if r.get("match_score") == 2 and r.get("fulfilment") in ("High", "Medium") and (
                pd.isna(r.get("med_b_cba")) or r["med_b_cba"] <= 0 or pd.isna(r.get("med_b_be_roas")) or r["med_b_be_roas"] > 3.0):
            gates.append("R4")
        if r5 and (r["revenue"] < 10000 or r["units"] < 300):
            gates.append("R5")
        hit = sorted(t for t in brand_tokens(r["name"], r["seller"]) if isinstance(r.get("cj_name"), str) and t in r["cj_name"].lower())
        if r.get("match_score") == 2 and hit:
            gates.append("R6")
        if r.get("supplier_shipped") is True or r.get("supplier_shipped") == "True":
            if pd.notna(r.get("cost_max")) and r["cost_max"] / r["asp"] >= 0.90:
                gates.append("R7")
        txt = f" {str(r['name']).lower()} {str(r.get('cj_name') or '').lower()} {str(r.get('med_method') or '').lower()} "
        flags = [k for k, ws in ADULT_FLAGS.items() if any(w in txt for w in ws)]
        if "electricity" in txt and "battery_electrical" not in flags:
            flags.append("battery_electrical")
        if r["cat_name"] in SIZING:
            flags.append("sizing")
        if pd.notna(r.get("listedNum")) and r["listedNum"] < 10:
            flags.append("unproven_listing")
        if r.get("match_score") == 2 and pd.notna(r.get("stock_cj_total")) and r["stock_cj_total"] < 100:
            flags.append("factory_stock_only")
        sv = "Provisional" if r.get("match_score") == 2 and r.get("fulfilment") in ("High", "Medium") else "Weak"
        roas, vsh = r.get("med_b_be_roas"), r.get("video_sh")
        if pd.notna(roas) and roas <= 2.0 and pd.notna(vsh) and vsh >= 0.5:
            asl = "Strong"
        elif pd.notna(roas) and roas <= 2.5:
            asl = "Moderate"
        else:
            asl = "Weak"
        cr = "Rejected" if gates else "Needs verification"
        rows.append({"cand": r["cand"], "pool": r["pool"], "cat_name": r["cat_name"], "name": r["name"], "cj_pid": r.get("cj_pid"),
                     "rev_sep": r["revenue"], "units_sep": r["units"], "asp": r["asp"],
                     "mo_pct": round(float(r["mo_pct"]), 3) if pd.notna(r["mo_pct"]) else None,
                     "supplier_viability": sv, "be_roas": round(float(roas), 2) if pd.notna(roas) else None,
                     "be_roas_stress": round(float(r["med_s_be_roas"]), 2) if pd.notna(r.get("med_s_be_roas")) else None,
                     "video_sh": round(float(vsh), 3) if pd.notna(vsh) else None, "creator_breadth": "unknown (not pulled)",
                     "ad_suitability": asl, "gates_failed": ",".join(gates), "brand_tokens_in_cj_name": ",".join(hit),
                     "risk_flags": ",".join(flags), "commercial_readiness": cr, "phase_f_class": r["class"]})
    G = pd.DataFrame(rows)
    G["_o"] = G["ad_suitability"].map(LEVEL)
    return pd.concat([G[G["commercial_readiness"] != "Rejected"].sort_values(["_o", "be_roas", "mo_pct"], ascending=[True, True, False]),
                      G[G["commercial_readiness"] == "Rejected"]]).drop(columns="_o")
