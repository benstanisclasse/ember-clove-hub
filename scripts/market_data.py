"""Point-in-time product-month dataset for the market engine (Market Engine 2.0 Phase B, 2026-10-28).

One row per product per month from the monthly Kalodata lists: the category top 500 by sales (kind `top`, pages 1-5)
and the top 200 by Kalodata's growth field (kind `risers`, pages 1-2). The deeper riser pages 201-1,000 (kind
`risers_deep`, pulled only for Sep 2026) are kept as their own population and never mixed into the 1-200 history.

Point in time: `build(rows, cutoff=T)` first drops every row whose event month is after T, then computes features
and labels, so nothing after T can reach a row. Features of month t only look at months <= t (lags) and labels only
exist when every month they need is present (a label after the cutoff is NaN, not 0). The evaluation harness relies on
this: a month-t row has the same features in a build cut at t as in the full build (tested in test_market.py).

Exclusions (each with its reason in the manifest): Oct 2025 (about one week of data); features of Nov 2025 that need
the previous month (set missing); Virtual Products (no data); duplicate pulls of the same list page (the doubled
Womenswear Aug/Sep pilot pages); pulls that are not the monthly list spec (keyword, price-band, rolling-window,
level-2 category, probe pages). Thin categories (Pre-Owned, Muslim Fashion, or a 500th-place product under $2,000 a
month) are kept and flagged. Fields Kalodata returns as today's value (commission, SKU count, launch date / age,
review count, name, seller name) are never features; they are saved separately as `attributes_current` with the date
they were observed, for report filters only. Products listed in two categories in one month have revenue and units
summed and keep the category with more revenue. Growth is our own month-on-month change between consecutive listed
months; Kalodata's growth field is kept as a separate, labelled feature (`kalo_growth_slog`; the placeholder 100 and
values measured against an excluded month are missing).

Usage (run from the Hub folder):
  python -I scripts/market_data.py build [--cutoff 2026-09] [--name NAME]   write research/kalodata/snapshots/NAME/
  python -I scripts/market_data.py summary                                   row counts without writing anything
"""
import argparse
import datetime as dt
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HUB = Path(__file__).resolve().parent.parent
DB = HUB / "research" / "kalodata" / "kalodata.db"
SNAPSHOTS = HUB / "research" / "kalodata" / "snapshots"

LIST_KINDS = ("top", "risers", "risers_deep")
LIST_SPEC_KEYS = {"sort_field", "page_size", "page_number", "category_ids", "need_extra"}
MAX_PAGE = {"top": 5, "risers": 2, "risers_deep": 10}
LIST_SIZE = {"top": 500, "risers": 200}
PAGE_SIZE = 100
EXCLUDED_CATEGORIES = {"834312": "Virtual Products: Kalodata returned no data for any month"}
THIN_CATEGORIES = {"856720": "Pre-Owned", "601303": "Muslim Fashion"}
THIN_FLOOR = 2000  # a category-month whose 500th product sells less than this a month is flagged thin
EXCLUDED_MONTHS = {"2025-10": "partial month (about one week of data: 0.29 of a 2026 month's revenue); every Kalodata "
                              "growth value is the placeholder 100, so the riser list order is arbitrary"}
GROWTH_PLACEHOLDER = 100
AI_FLAG_FROM = "2026-06"  # Kalodata's ai_video flag is 0 in every row before June 2026: unknown, not 'not AI'
CURRENT_VALUE_FIELDS = {
    "commission_rate": "commission as of the pull date, repeated by Kalodata into every past month",
    "sku_count": "variant count as of the pull date",
    "launch_date": "listing date as of the pull date (a relisted product gets a later date); so product age is too",
    "product_review_count": "review count on the pull date (detail endpoint)",
    "product_name": "title as of the pull date",
    "seller_name": "seller name as of the pull date",
}
FEATURES = ["log_sales", "log_units", "unit_price", "video_share", "live_share", "shop_share", "log_vs_floor",
            "price_vs_cat", "mom_growth", "listed_prev", "was_top500_prev", "months_seen_before", "kalo_growth_slog",
            "rank_pos", "riser_pos", "seller_n_top500", "seller_share_cat", "cat_growth"]
FEATURE_DEFS = {
    "log_sales": "log10 of the product's month revenue (summed across categories), clipped at $1",
    "log_units": "log10 of month units (summed across categories), clipped at 1",
    "unit_price": "month revenue / units (Kalodata's unit_price is this ratio)",
    "video_share": "video revenue / revenue in the month", "live_share": "live revenue / revenue",
    "shop_share": "showcase (shop page) revenue / revenue",
    "log_vs_floor": "log10(revenue / revenue of the 500th product in the primary category that month); "
                    "missing when that top-500 list is incomplete",
    "price_vs_cat": "unit price / median unit price of the primary category's top 500 that month",
    "mom_growth": "our month-on-month growth: ln(revenue_t / revenue_t-1) when the product is listed (top 500 or "
                  "risers 1-200) in both months; missing when not listed in t-1 or t-1 is not available",
    "listed_prev": "1 if listed (top 500 or risers 1-200) in month t-1, 0 if not; missing when t-1 is not available",
    "was_top500_prev": "1 if in any category top 500 in t-1, 0 if not; missing when t-1 is not available",
    "months_seen_before": "number of available months before t in which the product was listed (top 500 or risers "
                          "1-200); missing in the first available month (no history window)",
    "kalo_growth_slog": "Kalodata revenue_growth_rate (undefined comparison window; does not match our MoM), as "
                        "sign(g)*ln(1+|g|); missing for the placeholder 100 and when the previous month is excluded",
    "rank_pos": "best position in a category top 500 that month (1-500); missing if not in a top 500",
    "riser_pos": "best position in a category riser list 1-200 that month; missing otherwise (deep positions "
                 "201-1,000 are in deep_riser_pos, never a feature)",
    "seller_n_top500": "seller's products in the primary category's top 500 that month (seller_id used as an "
                       "identity key only)",
    "seller_share_cat": "seller's share of the primary category's top-500 revenue that month",
    "cat_growth": "primary category top-500 revenue, month t / month t-1; missing when t-1 is not available",
}
LABEL_DEFS = {
    "y_holders_1m": "population top500 at t: 1 if in any category top 500 at t+1 AND revenue(t+1) >= revenue(t)",
    "y_holders_3m": "population top500 at t: 1 if in any category top 500 at exactly t+3",
    "y_breakout_1m": "population risers / risers_deep at t (not in a top 500): 1 if in any category top 500 at t+1",
    "y_breakout_3m": "population risers / risers_deep at t: 1 if in any category top 500 at t+1, t+2 or t+3",
    "absence": "top-500 lists are complete (5 full pages), so absence from next month's top 500 means 'below the 500th "
               "product' and is a valid 0. A label is NaN (not 0) when a month it needs is after the cutoff, missing, "
               "or the primary category's top-500 list that month is incomplete. Absence is never read as zero sales: "
               "revenue(t+1) is only used when the product is in a top 500 at t+1",
}
FLAG_DEFS = {
    "q_complete": "the primary category's top-500 and riser-200 lists for the month are complete",
    "q_partial_month": "month covers fewer than 90% of categories or is a known partial month",
    "q_prior_partial": "the previous month is excluded or missing: lag features and Kalodata growth are missing",
    "q_thin_category": "Pre-Owned / Muslim Fashion, or the category's 500th product sells under $2,000 that month",
    "q_split_category": "the product appeared in two category lists that month: revenue and units are summed, the "
                        "category with more revenue is kept",
    "q_dedup": "a duplicate pull of the same list page was dropped for this row's list",
    "q_growth_placeholder": "Kalodata growth was the placeholder 100 (set missing)",
}
NUM = ["revenue", "sales_volumn", "unit_price", "revenue_growth_rate", "commission_rate", "live_revenue",
       "video_revenue", "showcase_revenue", "sku_count"]


# ---------------------------------------------------------------- loading
def connect_ro(db=None):
    return sqlite3.connect(f"file:{Path(db or DB)}?mode=ro", uri=True)


def category_names(con):
    try:
        rows = con.execute("SELECT DISTINCT category_id, category_name FROM categories WHERE category_level = 1")
        return {str(a): b for a, b in rows.fetchall()}
    except sqlite3.OperationalError:
        return {}


def select_pulls(con, l1=None):
    """Monthly list pulls that match the list spec, one per (kind, month, category, page).
    Returns (accepted DataFrame, list of {pull_id, name, reason} for every pull left out)."""
    pulls = pd.read_sql("SELECT pull_id, name, kind, month, category_id AS cat, page, filters, success, sha256, "
                        "collected_at FROM pulls WHERE kind IN ('top', 'risers', 'risers_deep')", con)
    out, keep = [], []
    for r in pulls.itertuples(index=False):
        try:
            f = json.loads(r.filters or "{}")
        except ValueError:
            f = {}
        reason = None
        if not r.success:
            reason = "failed call (no rows)"
        elif r.month is None:
            reason = "rolling window (last30Day-style), not a calendar month"
        elif set(f) - LIST_SPEC_KEYS:
            reason = "extra filters (" + ", ".join(sorted(set(f) - LIST_SPEC_KEYS)) + "): not the list spec"
        elif int(f.get("page_size") or 0) != PAGE_SIZE:
            reason = f"page size {f.get('page_size')} (probe), not {PAGE_SIZE}"
        elif l1 and str(r.cat) not in l1:
            reason = "not a level-1 category"
        elif (r.page or 1) > MAX_PAGE[r.kind]:
            reason = f"page {r.page} beyond the {r.kind} list spec"
        if reason:
            out.append({"pull_id": int(r.pull_id), "name": r.name, "reason": reason})
        else:
            keep.append(r.pull_id)
    acc = pulls[pulls["pull_id"].isin(keep)].copy()
    acc["page"] = acc["page"].fillna(1).astype(int)
    acc["cat"] = acc["cat"].astype(str)
    acc = acc.sort_values(["collected_at", "pull_id"], na_position="first")
    key = ["kind", "month", "cat", "page"]
    dup = acc.duplicated(key, keep="last")
    last = acc.drop_duplicates(key, keep="last").set_index(key)["pull_id"]
    for r in acc[dup].itertuples(index=False):
        out.append({"pull_id": int(r.pull_id), "name": r.name,
                    "reason": f"duplicate of pull {int(last[(r.kind, r.month, r.cat, r.page)])} "
                              "(same list, month, category and page; values identical)"})
    acc = acc[~dup].copy()
    dup_lists = {(k, m, c) for k, m, c, _ in pulls[pulls["pull_id"].isin([o["pull_id"] for o in out if
                                                                          o["reason"].startswith("duplicate")])]
                 [key].itertuples(index=False, name=None)}
    acc["dedup"] = [(k, m, c) in dup_lists for k, m, c in zip(acc["kind"], acc["month"], acc["cat"])]
    return acc, out


def load_rows(db=None):
    """Standard list rows from the database plus pull notes and category names."""
    con = connect_ro(db)
    cats = category_names(con)
    pulls, notes = select_pulls(con, set(cats) or None)
    df = pd.read_sql("SELECT p.pull_id, p.position, p.product_id, p.product_name, p.seller_id, p.seller_name, "
                     "p.launch_date, " + ", ".join(f"p.{c}" for c in NUM) +
                     " FROM products p JOIN pulls u ON p.pull_id = u.pull_id "
                     "WHERE u.kind IN ('top', 'risers', 'risers_deep') AND u.success = 1", con)
    con.close()
    df = df.merge(pulls[["pull_id", "kind", "month", "cat", "page", "collected_at", "dedup"]], on="pull_id")
    return standardize(df), cats, notes, pulls


def standardize(df):
    """Shape raw list rows (from the DB or a live scan) into the builder's input columns."""
    df = df.copy()
    df[NUM] = df[NUM].apply(pd.to_numeric, errors="coerce")
    df["product_id"] = df["product_id"].astype(str)
    df["cat"] = df["cat"].astype(str)
    df["pos"] = (df["page"].astype(int) - 1) * PAGE_SIZE + df["position"].astype(int)
    df = df.rename(columns={"sales_volumn": "units", "revenue_growth_rate": "growth_raw"})
    if "dedup" not in df:
        df["dedup"] = False
    return df


def pulls_fingerprint(pulls):
    h = hashlib.sha256()
    for pid, sha in sorted(zip(pulls["pull_id"], pulls.get("sha256", pulls["pull_id"]).astype(str))):
        h.update(f"{pid}:{sha};".encode())
    return h.hexdigest()


def ai_flag_point_in_time(month, ai_video):
    """Kalodata's AI-video flag as a point-in-time value: unknown (None) before June 2026, where it is always 0."""
    return None if str(month) < AI_FLAG_FROM else ai_video


# ---------------------------------------------------------------- building
def _ord(months):
    """Month 'YYYY-MM' -> integer (consecutive months differ by 1)."""
    s = pd.Series(list(months) if not isinstance(months, pd.Series) else months)
    return s.map({m: int(m[:4]) * 12 + int(m[5:7]) - 1 for m in s.unique()}).values


def _mstr(o):
    return f"{int(o) // 12:04d}-{int(o) % 12 + 1:02d}"


def build(rows, cutoff=None):
    """Product-month panel from standard list rows using only months <= cutoff. Returns (panel, attrs, info)."""
    info = {"cutoff_requested": cutoff, "dropped_rows": {}}
    r = rows.copy()
    if cutoff:
        info["dropped_rows"]["after_cutoff"] = int((r["month"] > cutoff).sum())
        r = r[r["month"] <= cutoff]
    m = r["cat"].isin(EXCLUDED_CATEGORIES)
    info["dropped_rows"]["excluded_categories"] = int(m.sum())
    r = r[~m]
    m = r["month"].isin(EXCLUDED_MONTHS)
    info["dropped_rows"]["excluded_months"] = int(m.sum())
    r = r[~m].copy()
    attrs = current_attributes(r)
    r["mo"] = _ord(r["month"])

    # list completeness per (kind, category, month) and month availability
    cnt = r.groupby(["kind", "cat", "month"])["pos"].nunique()
    complete = {kind: {(c, mth) for (k, c, mth), n in cnt.items() if k == kind and n >= size}
                for kind, size in LIST_SIZE.items()}
    n_cats = r[r["kind"] == "top"].groupby("month")["cat"].nunique()
    all_cats = r["cat"].nunique()
    avail = sorted(n_cats[n_cats >= 0.5 * all_cats].index)
    avail_ord = set(_ord(avail)) if avail else set()
    partial_months = {mth for mth, n in n_cats.items() if n < 0.9 * all_cats}

    # per product-month-category: values from the top row when present (values match across lists), positions
    key = ["product_id", "month", "cat"]
    r["_pref"] = r["kind"].map({"top": 0, "risers": 1, "risers_deep": 2})
    vals = r.sort_values(["_pref", "pull_id"]).drop_duplicates(key)
    pos = r.pivot_table(index=key, columns="kind", values="pos", aggfunc="min")
    for k in LIST_KINDS:
        if k not in pos:
            pos[k] = np.nan
    dd = r.groupby(key)["dedup"].any()
    g = vals.set_index(key)[["mo", "revenue", "units", "live_revenue", "video_revenue", "showcase_revenue",
                             "growth_raw", "seller_id"]].join(pos[list(LIST_KINDS)]).join(dd).reset_index()

    # category-month statistics from the top lists (per-category revenue)
    top = g[g["top"].notna()]
    floor = top.groupby(["cat", "month"])["revenue"].min()
    floor = floor[[k in complete["top"] for k in floor.index]]
    cat_sales = top.groupby(["cat", "month"])["revenue"].sum()
    top_price = (top["revenue"] / top["units"].replace(0, np.nan))
    med_price = top_price.groupby([top["cat"], top["month"]]).median()
    sel = top.groupby(["seller_id", "cat", "month"])["revenue"].agg(["size", "sum"])
    floor, cat_sales, med_price = floor.to_dict(), cat_sales.to_dict(), med_price.to_dict()
    sel_n, sel_sum = sel["size"].to_dict(), sel["sum"].to_dict()

    # product-month: sum across categories, keep the category with more revenue
    pm = ["product_id", "month"]
    g["n_cats"] = g.groupby(pm)["cat"].transform("size")
    sums = g.groupby(pm)[["revenue", "units", "live_revenue", "video_revenue", "showcase_revenue"]].sum()
    prim = g.sort_values(["revenue", "cat"], ascending=[False, True]).drop_duplicates(pm).set_index(pm)
    p = prim[["cat", "mo", "growth_raw", "seller_id", "n_cats", "dedup"]].join(sums)
    p = p.join(g.groupby(pm)[list(LIST_KINDS)].min().rename(
        columns={"top": "rank_pos", "risers": "riser_pos", "risers_deep": "deep_riser_pos"}))
    p["dedup"] = g.groupby(pm)["dedup"].any()
    p = p.reset_index()
    p["in_top500"] = p["rank_pos"].notna()
    p["in_risers"] = p["riser_pos"].notna()
    p["population"] = np.where(p["in_top500"], "top500", np.where(p["in_risers"], "risers",
                                                                  np.where(p["deep_riser_pos"].notna(), "risers_deep",
                                                                           "other")))
    cm = list(zip(p["cat"], p["month"]))

    # features of month t (lags look only at t-1 and earlier)
    p["unit_price"] = p["revenue"] / p["units"].replace(0, np.nan)
    p["log_sales"] = np.log10(p["revenue"].clip(lower=1))
    p["log_units"] = np.log10(p["units"].clip(lower=1))
    for col, src in (("video_share", "video_revenue"), ("live_share", "live_revenue"), ("shop_share", "showcase_revenue")):
        p[col] = (p[src] / p["revenue"].replace(0, np.nan)).clip(0, 1)
    p["floor"] = [floor.get(k, np.nan) for k in cm]
    p["log_vs_floor"] = np.log10(p["revenue"].clip(lower=1) / p["floor"])
    p["price_vs_cat"] = p["unit_price"] / np.array([med_price.get(k, np.nan) for k in cm])
    sk = list(zip(p["seller_id"], p["cat"], p["month"]))
    p["seller_n_top500"] = [float(sel_n.get(k, 0)) for k in sk]
    p["seller_share_cat"] = np.array([sel_sum.get(k, 0.0) for k in sk]) / np.array([cat_sales.get(k, np.nan)
                                                                                        for k in cm])
    p["has_prev"] = (p["mo"] - 1).isin(avail_ord)
    mstr = {o: _mstr(o) for o in
            {int(o) + k for o in set(p["mo"]) for k in (-1, 0, 1, 2, 3)}}
    prev_cat = [cat_sales.get((c, mstr[o - 1]), np.nan) for c, o in zip(p["cat"], p["mo"])]
    p["cat_growth"] = np.where(p["has_prev"], np.array([cat_sales.get(k, np.nan) for k in cm]) / np.array(prev_cat),
                               np.nan)
    listed = p[p["population"].isin(["top500", "risers"])][["product_id", "mo", "revenue", "in_top500"]]
    lag = listed.assign(mo=listed["mo"] + 1).rename(columns={"revenue": "prev_revenue", "in_top500": "prev_top"})
    p = p.merge(lag, on=["product_id", "mo"], how="left")
    hp = p["has_prev"]
    p["listed_prev"] = np.where(hp, p["prev_revenue"].notna().astype(float), np.nan)
    p["was_top500_prev"] = np.where(hp, (p["prev_top"] == True).astype(float), np.nan)  # noqa: E712
    p["mom_growth"] = np.where(hp & p["prev_revenue"].notna(),
                               np.log(p["revenue"].clip(lower=1) / p["prev_revenue"].clip(lower=1)), np.nan)
    seen = listed[["product_id", "mo"]].assign(_w=1)
    allr = pd.concat([p[["product_id", "mo"]].assign(_w=0, _i=np.arange(len(p))), seen.assign(_i=-1)])
    allr = allr.sort_values(["product_id", "mo", "_w"])  # a row is counted before its own month's listing
    allr["_c"] = allr.groupby("product_id")["_w"].cumsum() - allr["_w"]
    cnt_before = allr[allr["_i"] >= 0].set_index("_i")["_c"].sort_index()
    p["months_seen_before"] = np.where(hp, cnt_before.values, np.nan)
    gr = p["growth_raw"]
    p["q_growth_placeholder"] = (gr == GROWTH_PLACEHOLDER)
    g_ok = gr.where((gr != GROWTH_PLACEHOLDER) & hp)
    p["kalo_growth_slog"] = np.sign(g_ok) * np.log1p(g_ok.abs())

    # labels: membership of any category top 500 in later months, only when that month is present and complete
    t5 = p[p["in_top500"]][["product_id", "mo", "revenue"]]
    for k in (1, 2, 3):
        f = t5.assign(mo=t5["mo"] - k).rename(columns={"revenue": f"rev_{k}"})
        f[f"top_{k}"] = 1.0
        p = p.merge(f, on=["product_id", "mo"], how="left")
        ok = (p["mo"] + k).isin(avail_ord) & np.array(
            [(c, mstr[o + k]) in complete["top"] for c, o in zip(p["cat"], p["mo"])])
        p[f"top_{k}"] = np.where(ok, p[f"top_{k}"].fillna(0.0), np.nan)
    hold, brk = p["population"] == "top500", p["population"].isin(["risers", "risers_deep"])
    y1 = np.where(p["top_1"].isna(), np.nan, ((p["top_1"] == 1) & (p["rev_1"] >= p["revenue"])).astype(float))
    p["y_holders_1m"] = np.where(hold, y1, np.nan)
    p["y_holders_3m"] = np.where(hold, p["top_3"], np.nan)
    p["y_breakout_1m"] = np.where(brk, p["top_1"], np.nan)
    any3 = p[["top_1", "top_2", "top_3"]].max(axis=1, skipna=False)
    p["y_breakout_3m"] = np.where(brk, any3, np.nan)

    # quality flags
    p["q_complete"] = [(k in complete["top"]) and (k in complete["risers"]) for k in cm]
    p["q_partial_month"] = p["month"].isin(partial_months | set(EXCLUDED_MONTHS))
    p["q_prior_partial"] = ~hp
    p["q_thin_category"] = p["cat"].isin(THIN_CATEGORIES) | (p["floor"] < THIN_FLOOR)
    p["q_split_category"] = p["n_cats"] > 1
    p["q_dedup"] = p["dedup"].astype(bool)
    p[FEATURES] = p[FEATURES].replace([np.inf, -np.inf], np.nan)
    p = p.drop(columns=["prev_revenue", "prev_top", "rev_2", "rev_3", "dedup", "has_prev"])
    p = p.rename(columns={"rev_1": "revenue_next_if_top500", "growth_raw": "kalo_growth_raw"})  # raw: display only
    p = p.sort_values(["month", "cat", "product_id"]).reset_index(drop=True)
    info.update({"months": sorted(p["month"].unique().tolist()), "available_months": avail,
                 "partial_months": sorted(partial_months), "data_cutoff": max(avail) if avail else None,
                 "rows_input": int(len(rows)), "rows_after_exclusions": int(len(r))})
    return p, attrs, info


def current_attributes(r):
    """Today's-value fields per product (latest observation), never used as historical features."""
    cols = [c for c in ("product_id", "product_name", "seller_id", "seller_name", "commission_rate", "sku_count",
                        "launch_date", "collected_at", "month") if c in r]
    a = r[cols].sort_values([c for c in ("collected_at", "month") if c in cols]).drop_duplicates("product_id",
                                                                                                 keep="last")
    return a.rename(columns={"collected_at": "observed_at", "month": "last_month_seen"}).reset_index(drop=True)


# ---------------------------------------------------------------- snapshot
def git_commit():
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HUB, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "scripts/market_data.py"], cwd=HUB,
                               capture_output=True, text=True).stdout.strip()
        return sha + ("+uncommitted market_data.py" if dirty else "")
    except OSError:
        return None


def summarize(p):
    out = {"rows": int(len(p)), "products": int(p["product_id"].nunique())}
    out["by_month_population"] = {m: {k: int(v) for k, v in g["population"].value_counts().items()}
                                  for m, g in p.groupby("month")}
    out["flags"] = {f: int(p[f].sum()) for f in FLAG_DEFS}
    out["labels_matured"] = {y: int(p[y].notna().sum()) for y in LABEL_DEFS if y.startswith("y_")}
    return out


def write_snapshot(p, attrs, info, notes, pulls, name=None, cats=None):
    stamp = dt.datetime.now()
    name = name or f"pit_{info['data_cutoff']}_{stamp:%Y%m%d-%H%M}"
    out = SNAPSHOTS / name
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing snapshot {out}")
    out.mkdir(parents=True)
    try:
        import pyarrow  # noqa: F401
        fmt = "parquet"
        p.to_parquet(out / "panel.parquet", index=False)
        attrs.to_parquet(out / "attributes_current.parquet", index=False)
    except ImportError:
        fmt = "csv.gz"
        p.to_csv(out / "panel.csv.gz", index=False, compression="gzip")
        attrs.to_csv(out / "attributes_current.csv.gz", index=False, compression="gzip")
    reasons = pd.Series([n["reason"].split(" (")[0] if not n["reason"].startswith("duplicate") else "duplicate pull"
                         for n in notes]).value_counts().to_dict() if notes else {}
    manifest = {
        "name": name, "created_at": stamp.isoformat(timespec="seconds"), "format": fmt,
        "data_cutoff": info["data_cutoff"], "cutoff_requested": info["cutoff_requested"],
        "months": info["months"], "available_months": info["available_months"],
        "code_commit": git_commit(), "builder": "scripts/market_data.py",
        "packages": {"pandas": pd.__version__, "numpy": np.__version__, "python": sys.version.split()[0]},
        "source_db": str(DB.relative_to(HUB)), "pulls_used": int(len(pulls)),
        "pulls_fingerprint_sha256": pulls_fingerprint(pulls),
        "exclusions": {
            "months": EXCLUDED_MONTHS,
            "nov_2025_lag_features": "features that need the previous month (mom_growth, listed_prev, was_top500_prev, "
                                     "months_seen_before, cat_growth, kalo_growth_slog) are missing in Nov 2025 "
                                     "because Oct 2025 is excluded (flag q_prior_partial)",
            "categories": EXCLUDED_CATEGORIES,
            "thin_categories_flagged_not_dropped": THIN_CATEGORIES, "thin_floor_usd": THIN_FLOOR,
            "current_value_fields_never_features": CURRENT_VALUE_FIELDS,
            "ai_flag": f"ai_video before {AI_FLAG_FROM} is unknown, not 0 (ai_flag_point_in_time); no video-derived "
                       "feature is in this panel",
            "risers_deep": "Sep 2026 riser pages 3-10 (positions 201-1,000) are population 'risers_deep': never "
                           "training rows for the 1-200 population and not counted as 'listed' in history features",
            "duplicates": "one pull per (kind, month, category, page): the latest collected wins (removes the doubled "
                          "Womenswear Aug/Sep pilot pages)",
            "split_category": "a product in two category lists in one month: revenue and units summed, category "
                              "with more revenue kept",
            "kalodata_growth": "kept only as kalo_growth_slog (labelled); placeholder 100 = missing",
            "pulls_left_out_by_reason": reasons,
            "rows_dropped": info["dropped_rows"],
        },
        "features": FEATURE_DEFS, "labels": LABEL_DEFS, "quality_flags": FLAG_DEFS,
        "counts": summarize(p), "attributes_current_rows": int(len(attrs)),
        "categories": cats or {},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "pulls_left_out.json").write_text(json.dumps(notes, indent=0, ensure_ascii=False), encoding="utf-8")
    return out


def latest_snapshot():
    snaps = sorted((d for d in SNAPSHOTS.glob("*") if (d / "manifest.json").exists()),
                   key=lambda d: json.loads((d / "manifest.json").read_text(encoding="utf-8"))["created_at"])
    if not snaps:
        raise SystemExit("No snapshot yet: run python -I scripts/market_data.py build")
    return snaps[-1]


def read_snapshot(path=None):
    path = Path(path) if path else latest_snapshot()
    if not path.is_absolute() and not path.exists():
        path = SNAPSHOTS / path
    man = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    if man["format"] == "parquet":
        p = pd.read_parquet(path / "panel.parquet")
        a = pd.read_parquet(path / "attributes_current.parquet")
    else:
        p = pd.read_csv(path / "panel.csv.gz", dtype={"product_id": str, "cat": str, "seller_id": str})
        a = pd.read_csv(path / "attributes_current.csv.gz", dtype={"product_id": str})
    return p, a, man


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["build", "summary"])
    ap.add_argument("--cutoff", help="last event month to include (YYYY-MM); default: all")
    ap.add_argument("--name", help="snapshot folder name (default pit_<cutoff>_<timestamp>)")
    ap.add_argument("--db", default=str(DB))
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    rows, cats, notes, pulls = load_rows(a.db)
    p, attrs, info = build(rows, a.cutoff)
    s = summarize(p)
    print(f"panel: {s['rows']:,} product-months, {s['products']:,} products, months {info['months'][0]}.."
          f"{info['months'][-1]}; pulls used {len(pulls):,}, left out {len(notes):,}")
    print("flags:", s["flags"])
    print("labels matured:", s["labels_matured"])
    if a.cmd == "build":
        print("snapshot:", write_snapshot(p, attrs, info, notes, pulls, a.name, cats))


if __name__ == "__main__":
    main()
