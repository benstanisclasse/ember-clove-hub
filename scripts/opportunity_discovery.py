"""Product opportunity discovery on the point-in-time Kalodata panel (research/opportunity/2026-10/PREREGISTRATION.json).

Read-only: uses research/kalodata/snapshots/pit_2026-09_v1 (built from kalodata.db by scripts/market_data.py) and
saved CJ research in data/kalo_cj. Downloads nothing, spends no credits, writes only under research/opportunity/.

  python -I scripts/opportunity_discovery.py backtest   # rankers vs the pre-registered S3_sustained outcome
  python -I scripts/opportunity_discovery.py screen     # Sep 2026 screen, six strategies, top-50 and economics
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HUB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HUB / "scripts"))
from market_data import FEATURES  # noqa: E402

SNAP = HUB / "research" / "kalodata" / "snapshots" / "pit_2026-09_v1"
OUT = HUB / "research" / "opportunity" / "2026-10"
PRE = json.loads((OUT / "PREREGISTRATION.json").read_text(encoding="utf-8"))
MONTHS = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07",
          "2026-08", "2026-09"]
STORE_FIT = set(PRE["current_screen"]["store_fit_categories"])
RNG = np.random.default_rng(20261030)


def mshift(m, k):
    i = MONTHS.index(m) + k
    return MONTHS[i] if 0 <= i < len(MONTHS) else None


def load_panel():
    p = pd.read_parquet(SNAP / "panel.parquet")
    p = p[p.population.isin(["top500", "risers", "risers_deep"])].copy()
    p["cat"] = p["cat"].astype(str)
    top = {(r.product_id, r.month) for r in p[p.in_top500].itertuples()}
    listed = {(r.product_id, r.month) for r in p[p.population.isin(["top500", "risers"])].itertuples()}

    def s3(pid, m):
        nxt = [mshift(m, k) for k in (1, 2, 3)]
        if any(x is None for x in nxt):
            return np.nan
        return float(sum((pid, x) in top for x in nxt) >= 2)

    p["y_s3"] = [s3(a, b) for a, b in zip(p.product_id, p.month)]
    prev = p.set_index(["product_id", "month"])["revenue"]
    p["rev_prev"] = [prev.get((a, mshift(b, -1)), np.nan) if mshift(b, -1) else np.nan
                     for a, b in zip(p.product_id, p.month)]
    p["rev_prev2"] = [prev.get((a, mshift(b, -2)), np.nan) if mshift(b, -2) else np.nan
                      for a, b in zip(p.product_id, p.month)]
    p["n_listed_3"] = [sum((a, x) in listed for x in (mshift(b, -2), mshift(b, -1), b) if x)
                       for a, b in zip(p.product_id, p.month)]
    # category seller concentration (HHI of seller revenue in the primary category's top 500 that month)
    t5 = p[p.population == "top500"]
    sh = t5.groupby(["month", "cat", "seller_id"]).revenue.sum()
    tot = t5.groupby(["month", "cat"]).revenue.sum()
    hhi = ((sh / tot.reindex(sh.index.droplevel(2)).values) ** 2).groupby(level=[0, 1]).sum()
    p["cat_hhi"] = [hhi.get((m, c), np.nan) for m, c in zip(p.month, p.cat)]
    return p


def z(s):
    s = s.astype(float)
    sd = s.std()
    return (s - s.mean()) / sd if sd and not np.isnan(sd) else s * 0


def pct(s):
    return s.rank(pct=True, na_option="bottom")


def transparent_scores(d):
    """All transparent rankers for one month's rows (only information available at the end of that month)."""
    sc = pd.DataFrame(index=d.index)
    sc["B1_sales"] = d.revenue
    sc["B2_growth"] = d.mom_growth.fillna(-99)
    sc["B3_consistency"] = d.n_listed_3 * 1e9 + d.revenue
    gr = d.mom_growth.clip(-2, 3)
    dollar = np.log10((d.revenue - d.rev_prev).clip(lower=1)).where(d.rev_prev.notna())
    both = ((d.revenue > d.rev_prev) & (d.rev_prev > d.rev_prev2)).astype(float) * 0.5
    a = z(gr.fillna(gr.min())) + z(dollar.fillna(0)) + both
    sc["A_emerging"] = a.where(d.revenue >= 5000, -99)
    b = z(d.cat_growth.fillna(1)) - z(d.cat_hhi.fillna(d.cat_hhi.median())) - z(d.seller_share_cat.fillna(0)) \
        + 0.5 * z(np.log10(d.revenue.clip(lower=1)))
    sc["B_underserved"] = b
    return sc


def fit_m4(train):
    X = train[FEATURES]
    fill = X.median()
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))
    m.fit(X.fillna(fill).fillna(0), train.y_s3.astype(int))
    return m, fill


def topk_hits(score, y, k):
    order = np.lexsort((RNG.random(len(score)), -score))
    return y[order[:k]].sum(), min(k, len(y))


def evaluate(d, sc):
    y = d.y_s3.values
    out = {"n": int(len(d)), "pos": int(y.sum()), "base": float(y.mean())}
    for name in sc.columns:
        s = sc[name].values
        r = {}
        for k in (10, 20, 50):
            h, n = topk_hits(s, y, k)
            r[f"p@{k}"] = h / n
            r[f"lift@{k}"] = (h / n) / out["base"] if out["base"] else np.nan
        h50, _ = topk_hits(s, y, 50)
        r["recall@50"] = h50 / out["pos"] if out["pos"] else np.nan
        hits = picks = 0
        for c, g in d.groupby("cat"):
            idx = d.index.get_indexer(g.index)
            h, n = topk_hits(s[idx], y[idx], 10)
            hits += h
            picks += n
        r["p_cat@10"] = hits / picks
        sf = d.cat.isin(STORE_FIT).values
        h, n = topk_hits(s[sf], y[sf], 10)
        r["p_storefit@10"] = h / n if n else np.nan
        out[name] = r
    return out


def backtest():
    p = load_panel()
    pop = p[p.population.isin(["top500", "risers"])]
    results, per_month_cat = {}, {}
    for m in ["2026-01", "2026-02"] + PRE["evaluation"]["test_months"]:
        d = pop[(pop.month == m) & pop.y_s3.notna()].copy()
        sc = transparent_scores(d)
        train = pop[(pop.month.map(MONTHS.index) <= MONTHS.index(m) - 3) & pop.y_s3.notna()]
        if train.month.nunique() >= 2:
            model, fill = fit_m4(train)
            sc["M4_existing_spec"] = model.predict_proba(d[FEATURES].fillna(fill).fillna(0))[:, 1]
            sc["M5_composite"] = (pct(sc.M4_existing_spec) + pct(sc.A_emerging) + pct(sc.B3_consistency)
                                  + pct(sc.B1_sales)) / 4
        results[m] = evaluate(d, sc)
        results[m]["train_months"] = sorted(train.month.unique().tolist())
    test = PRE["evaluation"]["test_months"]
    names = [k for k in results[test[0]] if isinstance(results[test[0]][k], dict)]
    summary = {}
    for nm in names:
        summary[nm] = {met: float(np.mean([results[m][nm][met] for m in test]))
                       for met in results[test[0]][nm]}
    best_base = max(["B1_sales", "B2_growth", "B3_consistency"], key=lambda b: summary[b]["p_cat@10"])
    boot = {}
    for nm in names:
        diffs = []
        for _ in range(2000):
            ms = RNG.choice(test, len(test))
            diffs.append(np.mean([results[m][nm]["p_cat@10"] - results[m][best_base]["p_cat@10"] for m in ms]))
        boot[nm] = [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]
    res = {"test_months": test, "best_baseline_by_p_cat@10": best_base, "mean_over_test_months": summary,
           "p_cat@10_diff_vs_best_baseline_95ci": boot, "by_month": results,
           "base_rate_by_month": {m: results[m]["base"] for m in results}}
    (OUT / "backtest_results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    rows = [{"ranker": nm, **{k: round(v, 3) for k, v in summary[nm].items()},
             "p_cat10_diff_ci": boot[nm]} for nm in names]
    print(pd.DataFrame(rows).to_string(index=False))
    print("best baseline:", best_base, "| base rates:", {m: round(results[m]["base"], 3) for m in test})
    exploratory_segments(pop)


def exploratory_segments(pop):
    """EXPLORATORY (not pre-registered): the same rankers inside two segments where an outsider could still enter:
    risers outside any top 500, and top-500 products ranked 201-500 (the mid tier)."""
    segs = {"risers_not_top500": lambda d: d[~d.in_top500],
            "top500_rank_201_500": lambda d: d[d.in_top500 & (d.rank_pos > 200)]}
    test = PRE["evaluation"]["test_months"]
    out = {}
    for sname, f in segs.items():
        per = {}
        for m in test:
            d_all = pop[(pop.month == m) & pop.y_s3.notna()]
            train = pop[(pop.month.map(MONTHS.index) <= MONTHS.index(m) - 3) & pop.y_s3.notna()]
            model, fill = fit_m4(train)
            d = f(d_all).copy()
            sc = transparent_scores(d)
            sc["M4_existing_spec"] = model.predict_proba(d[FEATURES].fillna(fill).fillna(0))[:, 1]
            sc["M5_composite"] = (pct(sc.M4_existing_spec) + pct(sc.A_emerging) + pct(sc.B3_consistency)
                                  + pct(sc.B1_sales)) / 4
            per[m] = evaluate(d, sc)
        names = [k for k in per[test[0]] if isinstance(per[test[0]][k], dict)]
        out[sname] = {"base": float(np.mean([per[m]["base"] for m in test])),
                      "n_per_month": int(np.mean([per[m]["n"] for m in test])),
                      "rankers": {nm: {met: float(np.mean([per[m][nm][met] for m in test]))
                                       for met in ("p@20", "p@50", "p_cat@10", "p_storefit@10")} for nm in names}}
        print(f"\nEXPLORATORY {sname}: base {out[sname]['base']:.3f}, ~{out[sname]['n_per_month']} rows/month")
        print(pd.DataFrame(out[sname]["rankers"]).T.round(3).to_string())
    (OUT / "backtest_exploratory_segments.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


CLAIMS = re.compile(r"shapewear|tummy control|slimming|waist trainer|body shaper|posture|compression|butt lift|"
                    r"push.?up|medical|orthopedic|therapy", re.I)
MENS = re.compile(r"\bmen'?s\b|\bmens\b|for men\b", re.I)
HAIR = re.compile(r"\bwig\b|human hair|lace front|hair extension|bundles\b", re.I)


def econ(price, cost, ship, target=0.20, fee_pct=0.029, fee_fix=0.30, refund=0.05):
    """Pre-registered per-order economics. Returns contribution, break-even CAC/ROAS, target CAC/ROAS."""
    if pd.isna(cost) or pd.isna(ship) or pd.isna(price):
        return dict(contribution=np.nan, be_cac=np.nan, be_roas=np.nan, target_cac=np.nan, target_roas=np.nan)
    contrib = price - cost - ship - (price * fee_pct + fee_fix) - price * refund
    tcac = contrib - target * price
    return dict(contribution=contrib, be_cac=contrib, be_roas=price / contrib if contrib > 0 else np.nan,
                target_cac=tcac, target_roas=price / tcac if tcac > 0 else np.nan)


def trend(r):
    g1, g0 = r.mom_growth, r.mom_prev
    if r.months_seen_before is not None and r.months_seen_before <= 1 and (pd.isna(g1) or g1 > 0):
        return "emerging"
    if pd.notna(g1) and pd.notna(g0) and g1 > np.log(1.1) and g0 > np.log(1.1):
        return "accelerating"
    if pd.notna(g1) and g1 < np.log(0.75):
        return "declining"
    if r.n_listed_3 == 3 and pd.notna(g1) and abs(g1) < np.log(1.25):
        return "stable"
    return "uncertain"


def video_stats():
    """Per-product video concentration from the per-product video pulls (Sep 2026 / last 30 days only)."""
    import sqlite3
    con = sqlite3.connect(f"file:{HUB / 'research' / 'kalodata' / 'kalodata.db'}?mode=ro", uri=True)
    v = pd.read_sql("select v.product_filter product_id, v.video_id, v.belonged_creator_id creator, v.revenue, "
                    "v.views, v.ad, v.ai_video from videos v join pulls p using(pull_id) "
                    "where p.kind='product_videos'", con).drop_duplicates(["product_id", "video_id"])
    con.close()
    v["revenue"] = v.revenue.fillna(0)
    rows = []
    for pid, g in v.groupby("product_id"):
        tot = g.revenue.sum()
        cre = g.groupby("creator").revenue.sum()
        rows.append(dict(product_id=str(pid), vid_n=len(g), vid_selling=int((g.revenue > 0).sum()),
                         creators_selling=int((cre > 0).sum()),
                         top_video_share=g.revenue.max() / tot if tot else np.nan,
                         top_creator_share=cre.max() / tot if tot else np.nan,
                         ad_rev_share=g.loc[g.ad == 1, "revenue"].sum() / tot if tot else np.nan,
                         organic_selling_videos=int(((g.revenue > 0) & (g.ad != 1)).sum())))
    return pd.DataFrame(rows)


def saved_cj():
    s = pd.read_csv(HUB / "data" / "kalo_cj" / "picking_sheet_2026-10-29.csv")
    s["product_id"] = s.tiktok_url.str.extract(r"product/(\d+)")[0]
    keep = ["product_id", "k", "match", "photo_verdict", "photo_note", "cj_name", "cj_sku", "cj_url", "cj_cost",
            "cj_ship", "ship_method", "ship_days", "cj_stock", "cj_us_stock", "cj_reviews", "cj_avg_rating",
            "sizes_ok", "cj_listed"]
    return s[keep]


def screen():
    p = load_panel()
    a = pd.read_parquet(SNAP / "attributes_current.parquet")[["product_id", "product_name", "seller_name"]]
    pop = p[p.population.isin(["top500", "risers"])]
    train = pop[(pop.month.map(MONTHS.index) <= MONTHS.index("2026-06")) & pop.y_s3.notna()]
    model, fill = fit_m4(train)
    s = p[p.month == "2026-09"].copy()
    s["m4"] = model.predict_proba(s[FEATURES].fillna(fill).fillna(0))[:, 1]
    s["m4_out_of_range"] = s.population == "risers_deep"
    prevg = p.set_index(["product_id", "month"])["mom_growth"]
    s["mom_prev"] = [prevg.get((pid, "2026-08"), np.nan) for pid in s.product_id]
    s = s.join(transparent_scores(s))
    s = s.merge(a, on="product_id", how="left")
    s["trend"] = [trend(r) for r in s.itertuples()]
    s["store_fit"] = s.cat.isin(STORE_FIT)
    s["cat_name"] = s.cat.map(json.loads((SNAP / "manifest.json").read_text())["categories"])
    s["eligible"] = s.store_fit & s.unit_price.between(15, 120) & (s.revenue >= 5000)
    nm = s.product_name.fillna("")
    first = s.seller_name.fillna("").str.extract(r"([A-Za-z]{4,})")[0].fillna("@@")
    s["flag_brand"] = [bool(re.search(r"[™®©]|\|", n)) or (f.lower() in n.lower()) for n, f in zip(nm, first)]
    s["flag_claims"] = nm.str.contains(CLAIMS)
    s["flag_mens"] = nm.str.contains(MENS) & ~nm.str.contains(r"women", case=False)
    s["flag_hair"] = nm.str.contains(HAIR)
    s = s.merge(video_stats(), on="product_id", how="left").merge(saved_cj(), on="product_id", how="left")
    e = s.apply(lambda r: pd.Series(econ(r.unit_price, r.cj_cost, r.cj_ship)), axis=1)
    s = pd.concat([s, e], axis=1)

    # ---- strategy lists (market-wide and store-fit) ----
    lists = {}
    base = s[(s.revenue >= 5000) & s.unit_price.between(8, 200)]
    lists["A_emerging"] = base.sort_values("A_emerging", ascending=False)
    lists["A_emerging_model"] = base[~base.in_top500].sort_values("m4", ascending=False)
    lists["C_repeatable_video"] = s[s.creators_selling.notna() & (s.creators_selling >= 5)].sort_values(
        ["top_creator_share", "creators_selling"], ascending=[True, False])
    lists["D_organic"] = s[s.organic_selling_videos.notna() & (s.organic_selling_videos >= 3)].sort_values(
        "ad_rev_share")
    lists["E_margin"] = s[s.contribution.notna()].sort_values("be_cac", ascending=False)
    for k, d in lists.items():
        cols = ["product_id", "product_name", "cat_name", "population", "revenue", "unit_price", "mom_growth",
                "trend", "m4", "store_fit", "creators_selling", "top_creator_share", "ad_rev_share", "contribution",
                "be_cac", "flag_brand", "flag_claims"]
        d.head(100)[cols].to_csv(OUT / f"strategy_{k}.csv", index=False)
    # B underserved: category level (top 500, Sep vs Jun)
    t5 = p[p.population == "top500"]
    catm = t5.groupby(["cat", "month"]).agg(rev=("revenue", "sum"), sellers=("seller_id", "nunique"),
                                            hhi=("cat_hhi", "first")).reset_index()
    cs = catm[catm.month == "2026-09"].set_index("cat")
    cj = catm[catm.month == "2026-06"].set_index("cat")
    top10 = t5[t5.month == "2026-09"].sort_values("revenue", ascending=False).groupby("cat").head(10) \
        .groupby("cat").revenue.sum()
    cs["growth_3m"] = cs.rev / cj.rev
    cs["top10_share"] = top10 / cs.rev
    cs["median_price"] = t5[t5.month == "2026-09"].groupby("cat").unit_price.median()
    cs["price_iqr_ratio"] = t5[t5.month == "2026-09"].groupby("cat").unit_price.quantile(.75) / \
        t5[t5.month == "2026-09"].groupby("cat").unit_price.quantile(.25)
    cs["cat_name"] = cs.index.map(json.loads((SNAP / "manifest.json").read_text())["categories"])
    cs["store_fit"] = cs.index.isin(STORE_FIT)
    cs.sort_values("growth_3m", ascending=False).to_csv(OUT / "strategy_B_categories.csv")

    # ---- scoring (pre-registered weights; percentiles within category among eligible) ----
    el = s[s.eligible].copy()
    g = el.groupby("cat")
    comp = pd.DataFrame(index=el.index)
    comp["market_demand"] = g.revenue.rank(pct=True)
    comp["growth_potential"] = g.m4.rank(pct=True)
    comp["creative_potential"] = g.video_share.rank(pct=True)
    comp["competitive_opportunity"] = (g.seller_share_cat.rank(pct=True, ascending=False)
                                       + el.cat_hhi.rank(pct=True, ascending=False)) / 2
    comp["profitability"] = el.be_cac.rank(pct=True).where(el.be_cac.notna())
    q = pd.Series(np.nan, index=el.index)
    has = el.ship_days.notna()
    ship_max = el.ship_days.astype(str).str.extract(r"(\d+)\D*$")[0].astype(float)
    parts = pd.concat([(ship_max <= 12).astype(float).where(ship_max.notna()),
                       (el.cj_stock >= 500).astype(float).where(el.cj_stock.notna()),
                       (el.cj_avg_rating >= 4.5).astype(float).where(el.cj_avg_rating.notna())], axis=1)
    q[has] = parts[has].mean(axis=1)  # reviews are mostly 0 on CJ, so rating is used only where it exists
    comp["fulfillment_quality"] = q
    W = PRE["current_screen"]["score_weights"]
    mk = ["market_demand", "growth_potential", "creative_potential", "competitive_opportunity"]
    el["market_score"] = sum(comp[c] * W[c] for c in mk) / sum(W[c] for c in mk) * 100
    full = comp.notna().all(axis=1)
    el["commercial_score"] = (sum(comp[c] * W[c] for c in W) * 100).where(full)
    for c in comp:
        el[f"s_{c}"] = comp[c].round(3)
    el["hard_reject"] = (el.photo_verdict.eq("no") | el.match.eq("low") | (el.contribution <= 0))
    el["store_note"] = np.select([el.flag_mens, el.flag_hair], ["men's item", "wig/hair (not our range)"], "")
    el = el.sort_values("market_score", ascending=False)
    el.to_csv(OUT / "screen_eligible_scored.csv", index=False)
    stats = {"sep_rows": int(len(s)), "sep_listed_top500_risers": int(s.population.isin(["top500", "risers"]).sum()),
             "sep_deep_risers": int((s.population == "risers_deep").sum()), "store_fit_rows": int(s.store_fit.sum()),
             "eligible": int(len(el)), "eligible_by_cat": el.cat_name.value_counts().to_dict(),
             "with_video_stats": int(s.creators_selling.notna().sum()),
             "with_saved_cj": int(s.cj_cost.notna().sum()), "eligible_with_saved_cj": int(el.cj_cost.notna().sum()),
             "flags_eligible": {f: int(el[f].sum()) for f in ["flag_brand", "flag_claims", "flag_mens", "flag_hair"]},
             "trend_eligible": el.trend.value_counts().to_dict()}
    (OUT / "screen_stats.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
    print(json.dumps(stats, indent=1))


BRANDS = ["SKIMS", "Crocs", "HEYDUDE", "Vans", "Yeezy", "Clarks", "Dr. Scholl", "Maison Mihara", "Patented", "PUFF",
          "BOOMBA", "Comfrt", "Danielle Guizio"]
SCENARIOS = {  # sensitivity cases from the brief; each changes one input of the pre-registered formula
    "base": {}, "ship_plus_25pct": {"ship": 1.25}, "price_minus_15pct": {"price": 0.85}, "refunds_10pct": {"refund": 0.10},
    "cost_plus_20pct": {"cost": 1.20}, "generic_price_minus_30pct": {"price": 0.70},
    "all_adverse": {"ship": 1.25, "price": 0.85, "refund": 0.10, "cost": 1.20}}
CPC_REF = 1.00  # round-1 best ads paid $0.96-$1.07 per click (TikTok report 2026-10-29)


def outputs():
    """Top-50 table, full filtered ranking, supplier validation and sensitivity, from the screen plus live CJ checks."""
    e = pd.read_csv(OUT / "screen_eligible_scored.csv", dtype={"product_id": str})
    lv = json.loads((OUT / "live_cj_verdicts.json").read_text(encoding="utf-8"))
    lv = {k: v for k, v in lv.items() if isinstance(v, dict)}
    e["live_verdict"] = np.nan
    e["live_verdict"] = e["live_verdict"].astype(object)
    for pid, v in lv.items():  # live checks overrule the saved title match
        i = e.index[e.product_id == pid]
        e.loc[i, "live_verdict"] = v["verdict"]
        e.loc[i, "photo_note"] = v["note"]
        if "cj_ship" in v and v["verdict"] in ("match", "partial"):
            e.loc[i, ["cj_sku", "cj_cost", "cj_ship"]] = [v["cj_sku"], v["cj_cost"], v["cj_ship"]]
            for k, val in econ(float(e.loc[i, "unit_price"].iloc[0]), v["cj_cost"], v["cj_ship"]).items():
                e.loc[i, k] = val

    def supplier(r):
        if pd.notna(r.live_verdict):
            sku = f" {r.cj_sku}" if pd.notna(r.cj_sku) and "no match" not in r.live_verdict else ""
            return f"CJ live {r.live_verdict}{sku}"
        if pd.notna(r.cj_cost):
            return f"CJ saved ({r.match} title, photo {r.photo_verdict}) {r.cj_sku}"
        return "none checked"

    e["supplier"] = e.apply(supplier, axis=1)
    e["ip_risk"] = e.product_name.astype(str).apply(lambda n: any(b in n for b in BRANDS))
    f = e[e.store_note.isna()].copy().reset_index(drop=True)
    f["rank"] = range(1, len(f) + 1)
    verified = f.supplier.str.contains("photo match|live match", na=False)
    f["confidence"] = np.select([verified, f.contribution.notna()],
                                ["high (market + supplier photo verified)", "medium (supplier not photo verified)"],
                                "low (market evidence only)")

    def risk(r):
        if r.flag_claims: return "claims-heavy or intimate item (returns, hygiene, ad policy)"
        if r.ip_risk: return "famous brand or patented design (IP; we could only sell a generic)"
        if pd.notna(r.contribution) and r.contribution <= 0: return "negative contribution at TikTok price with CJ costs"
        if r.trend == "declining": return "demand falling month on month"
        if r.supplier == "none checked": return "no supplier verified"
        if "no match" in r.supplier: return "no matching supplier found"
        if pd.notna(r.contribution) and r.contribution < 15: return f"thin headroom (contribution ${r.contribution:.0f})"
        return "paid-ad competition from incumbent sellers"

    def action(r):
        if r.hard_reject or (pd.notna(r.contribution) and r.contribution <= 0) or "rejected" in r.supplier: return "Reject"
        if r.flag_claims: return "Monitor"
        if r.ip_risk and r.confidence.startswith("high"): return "Investigate (generic version, IP check)"
        if r.confidence.startswith("high") and r.contribution >= 15: return "Test (controlled, after sample)"
        if r.supplier == "none checked" or "no match" in r.supplier: return "Investigate (supplier)"
        return "Investigate (photo + sample)"

    f["main_risk"] = f.apply(risk, axis=1)
    f["recommendation"] = f.apply(action, axis=1)
    f["growth"] = f.mom_growth.apply(lambda g: f"{(np.exp(g) - 1) * 100:+.0f}% MoM" if pd.notna(g) else "n/a (not listed in Aug)")
    f["video"] = f.apply(lambda r: f"{int(r.creators_selling)} selling creators, top creator {r.top_creator_share:.0%}, "
                         f"paid {r.ad_rev_share:.0%}" if pd.notna(r.creators_selling)
                         else f"video share of sales {r.video_share:.0%} (creator data n/a)", axis=1)
    f["competition"] = f.apply(lambda r: f"rank {int(r.rank_pos) if pd.notna(r.rank_pos) else 'riser'}; seller "
                               f"{r.seller_share_cat:.1%} of category; category HHI {r.cat_hhi:.3f}", axis=1)
    f["tiktok_url"] = "https://www.tiktok.com/view/product/" + f.product_id + "?region=US"
    cols = ["rank", "product_id", "product_name", "cat_name", "unit_price", "revenue", "growth", "trend", "video",
            "competition", "m4", "supplier", "cj_cost", "cj_ship", "contribution", "be_cac", "target_cac", "market_score",
            "commercial_score", "confidence", "main_risk", "recommendation", "tiktok_url"]
    f[cols].round(3).to_csv(OUT / "ranking_full_filtered.csv", index=False)
    f.head(50)[cols].round(3).to_csv(OUT / "top50.csv", index=False)

    sv = f[f.cj_cost.notna() | f.live_verdict.notna()].copy()
    sv["photo"] = sv.live_verdict.where(sv.live_verdict.notna(), sv.photo_verdict)
    sv[["rank", "product_id", "product_name", "unit_price", "supplier", "photo", "photo_note", "cj_sku", "cj_cost",
        "cj_ship", "ship_method", "ship_days", "cj_stock", "cj_us_stock", "sizes_ok", "contribution", "be_cac",
        "target_cac", "recommendation"]].round(3).to_csv(OUT / "supplier_validation.csv", index=False)

    keep = f.confidence.str.startswith("high") | (f.supplier.str.contains("partial", na=False)
                                                  & ~f.supplier.str.contains("rejected", na=False))
    rows = []
    for _, r in f[keep].iterrows():
        for name, sc in SCENARIOS.items():
            x = econ(r.unit_price * sc.get("price", 1), r.cj_cost * sc.get("cost", 1), r.cj_ship * sc.get("ship", 1),
                     refund=sc.get("refund", 0.05))
            rows.append({"product_id": r.product_id, "product": r.product_name[:60], "scenario": name,
                         "price": r.unit_price * sc.get("price", 1), **x,
                         "cvr_needed_at_be_cpc1": CPC_REF / x["be_cac"] if x["be_cac"] > 0 else np.nan,
                         "cvr_needed_at_target_cpc1": CPC_REF / x["target_cac"] if x["target_cac"] > 0 else np.nan})
    pd.DataFrame(rows).round(3).to_csv(OUT / "sensitivity.csv", index=False)
    print(f.head(50).recommendation.value_counts().to_dict())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"backtest": backtest, "screen": screen, "outputs": outputs}[sys.argv[1]]()
