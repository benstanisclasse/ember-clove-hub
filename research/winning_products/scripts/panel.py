"""Shared panel for the winning-product research (DEFINITIONS_v1 §1). Read-only on kalodata.db.

build() returns (top, lists):
  top    one row per product x L1 category x month from the top-500 lists (kind 'top', pages 1-5), deduped:
         rank, revenue, units, asp, video/live/showcase revenue, launch_date, seller_id, kalo_g (Kalodata's
         undocumented momentum field), cutoff (the category-month's 500th revenue), n_in_list.
  lists  membership of every product-month in any list (top, top_deep, risers, risers_deep) with its best position,
         for "was it visible the month before" features.
Cached in _work/cache/ (git-ignored); delete the cache to rebuild.
"""
import sqlite3
from pathlib import Path

import pandas as pd

HUB = Path(__file__).resolve().parents[3]
DB = HUB / "research" / "kalodata" / "kalodata.db"
CACHE = HUB / "research" / "winning_products" / "_work" / "cache"
MONTHS = ["2025-10", "2025-11", "2025-12"] + [f"2026-{i:02d}" for i in range(1, 10)]
MIDX = {m: i for i, m in enumerate(MONTHS)}


def _load():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    q = """select p.product_id pid, q.category_id cat, q.month, q.kind, q.page, p.position, q.collected_at,
                  p.revenue, p.sales_volumn units, p.unit_price asp, p.video_revenue, p.live_revenue,
                  p.showcase_revenue, p.launch_date, p.seller_id, p.revenue_growth_rate kalo_g
           from products p join pulls q using(pull_id)
           where q.month in ({}) and q.kind in ('top','top_deep','risers','risers_deep') and q.category_id is not null
                 and q.success = 1""".format(",".join("?" * len(MONTHS)))
    df = pd.read_sql_query(q, con, params=MONTHS)
    con.close()
    df["rank"] = df["position"] + (df["page"] - 1) * 100
    return df


def build(refresh=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    fp_top, fp_lists = CACHE / "top.pkl", CACHE / "lists.pkl"
    if fp_top.exists() and fp_lists.exists() and not refresh:
        return pd.read_pickle(fp_top), pd.read_pickle(fp_lists)
    df = _load()
    lists = (df.sort_values("rank").drop_duplicates(["pid", "cat", "month", "kind"])
             [["pid", "cat", "month", "kind", "rank", "revenue"]])
    top = df[(df["kind"] == "top") & (df["page"] <= 5)].sort_values(["collected_at", "rank"])
    top = top.drop_duplicates(["pid", "cat", "month"], keep="first").copy()
    top = top[top["cat"] != "834312"]  # Virtual Products: only ranks 1-100 (v1 §1)
    full = top.groupby("cat")["month"].nunique()
    top = top[top["cat"].isin(full[full == len(MONTHS)].index)]  # L1 only: drops L2 probe pulls (900488, 842504)
    cut = top.groupby(["cat", "month"])["revenue"].agg(cutoff="min", n_in_list="size").reset_index()
    top = top.merge(cut, on=["cat", "month"])
    top["mi"] = top["month"].map(MIDX)
    top = top.drop(columns=["kind", "page", "position", "collected_at"])
    top.to_pickle(fp_top)
    lists.to_pickle(fp_lists)
    return top, lists


if __name__ == "__main__":
    t, lst = build(refresh=True)
    print(len(t), "top rows;", t["pid"].nunique(), "products;", t.groupby("cat")["month"].nunique().min(), "min months/cat")
    print(lst["kind"].value_counts().to_dict())
    print(t.groupby(["cat", "month"]).size().describe())
