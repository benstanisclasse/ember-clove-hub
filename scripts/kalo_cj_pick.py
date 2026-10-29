"""Product-picking sheet (2026-10-29): Kalodata winners in our niche + CJ Dropshipping cost, freight, listed count,
stock and reviews.

Step 1 `winners`: reads research/kalodata/kalodata.db (no Kalodata API calls) and keeps the best sellers of the latest
stored month in our niche: Womenswear (no bras, shapewear, underwear or lingerie), women's and unisex Shoes, Fashion
Accessories and Jewelry (sunglasses, necklaces, bracelets, earrings, hair clips, scarves, hats, belts, bags).
Retail price $12-$80. Top N per group by monthly revenue. Writes data/kalo_cj/winners_<month>.csv.

Step 2 (done by agents with the CJ MCP, read-only): for each winner, closest CJ match -> data/kalo_cj/cj_*.jsonl.

Step 3 `build`: joins both and prices each match with the same per-order model as scripts/pricing_study.py
(price - cost - shipping - 2.9% - $0.30 - 5% refunds - $20 CPA, free shipping to the customer). Our test price is
the Kalodata average selling price (what TikTok buyers paid); price_for_10 is the lowest .99 price keeping $10 after
the CPA. Hand corrections go in data/kalo_cj/cj_fixes.jsonl (read last, so they win). Writes data/kalo_cj/picking_sheet_<date>.csv and .xlsx.

Kalodata revenue and units are third-party estimates. CJ "listed" = how many CJ stores listed the item (competition
and seller interest), not sales. Changes nothing anywhere.
Run: python -I scripts/kalo_cj_pick.py winners   |   python -I scripts/kalo_cj_pick.py build
"""
import csv
import datetime as dt
import glob
import json
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pricing_study import kept, suggested  # noqa: E402

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HUB, "research", "kalodata", "kalodata.db")
DIR = os.path.join(HUB, "data", "kalo_cj")

# group -> (Kalodata top-level categories, how many winners to keep)
GROUPS = {
    "Clothing": (["601152"], 25),
    "Shoes": (["601352"], 12),
    "Accessories": (["605248", "953224"], 13),
}
PRICE_MIN, PRICE_MAX = 12.0, 80.0
NOT_NICHE = re.compile(
    r"\b(bras?|bralette|shapewear|shaper|faja|fajas|tummy control bodysuit|butt lift|underwear|panty|panties|thongs?|"
    r"briefs?|boxers?|lingerie|nipple|pasties|corset|waist trainer|postpartum|maternity|men['‘’]?s|mens|boys?|"
    r"girls?|kids?|toddler|baby|socks?|insoles?|shoe ?laces|watch band|apple watch|phone|airpods|wigs?|"
    r"human hair|extensions?|case|"
    r"pre-?owned|gift card|scrub|nurse)\b", re.I)
# Kalodata names are seller titles; jewelry/accessory categories also hold items we don't sell (watches, wallets).
ACCESSORY_OK = re.compile(r"sunglass|glasses|necklace|bracelet|earring|ring\b|rings\b|choker|pendant|anklet|"
                          r"claw clip|hair clip|scrunchie|headband|scarf|scarves|beanie|hat\b|cap\b|belt|tote|"
                          r"handbag|purse|shoulder bag|crossbody|gloves", re.I)


def winners():
    con = sqlite3.connect(DB)
    month = con.execute("select max(month) from pulls where kind='top'").fetchone()[0]
    prev = (dt.date.fromisoformat(month + "-01") - dt.timedelta(days=1)).strftime("%Y-%m")
    rows = []
    for group, (cats, keep) in GROUPS.items():
        marks = ",".join("?" * len(cats))
        q = f"""select p.product_id, p.product_name, p.revenue, p.sales_volumn, p.unit_price, p.revenue_growth_rate,
                       p.commission_rate, p.seller_name, p.launch_date, pl.category_id
                from products p join pulls pl using(pull_id)
                where pl.kind='top' and pl.month=? and pl.category_id in ({marks}) order by p.revenue desc"""
        seen, picked = set(), []
        for r in con.execute(q, [month, *cats]):
            pid, name, rev, units, price = r[0], r[1] or "", r[2] or 0, r[3] or 0, r[4] or 0
            if pid in seen or not PRICE_MIN <= price <= PRICE_MAX or NOT_NICHE.search(name):
                continue
            if group == "Accessories" and not ACCESSORY_OK.search(name):
                continue
            if group == "Shoes" and re.search(r"\bmen\b", name, re.I) and not re.search(r"women|unisex", name, re.I):
                continue
            seen.add(pid)
            picked.append(r)
            if len(picked) == keep:
                break
        for rank, r in enumerate(picked, 1):
            prev_rev = con.execute(
                """select max(p.revenue) from products p join pulls pl using(pull_id)
                   where pl.kind='top' and pl.month=? and p.product_id=?""", (prev, r[0])).fetchone()[0]
            rows.append(dict(
                k=f"{group[0]}{rank:02d}", group=group, rank=rank, kalo_id=r[0], kalo_name=r[1],
                kalo_revenue=round(r[2] or 0, 2), kalo_units=r[3], kalo_price=round(r[4] or 0, 2),
                kalo_growth_pct=r[5], kalo_prev_month_revenue=round(prev_rev, 2) if prev_rev else None,
                commission_pct=r[6], seller=r[7], launch_date=r[8], month=month,
                tiktok_url=f"https://www.tiktok.com/view/product/{r[0]}?region=US"))
    os.makedirs(DIR, exist_ok=True)
    out = os.path.join(DIR, f"winners_{month}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} winners from {month} top lists ->", out)
    for r in rows:
        print(f"{r['k']}  ${r['kalo_price']:>6.2f}  ${r['kalo_revenue']:>11,.0f}  {r['kalo_name'][:90]}")


def build():
    win = sorted(glob.glob(os.path.join(DIR, "winners_*.csv")))[-1]
    wins = list(csv.DictReader(open(win, encoding="utf-8")))
    cj = {}
    for path in sorted(glob.glob(os.path.join(DIR, "cj_*.jsonl"))):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                o = json.loads(line)
                cj[o["k"]] = o  # last row for a product wins (an agent may have retried)
    rows = []
    for w in wins:
        o = cj.get(w["k"], {})
        price = float(w["kalo_price"])
        cost, ship = o.get("cj_cost_max"), o.get("ship15_price") or o.get("cheapest_price")
        usable = o.get("match") in ("high", "medium") and cost and ship
        k = kept(price, float(cost), float(ship)) if usable else None
        need = suggested(float(cost), float(ship)) if usable else None
        rows.append(dict(
            k=w["k"], group=w["group"], rank=int(w["rank"]), product=w["kalo_name"],
            kalo_revenue=float(w["kalo_revenue"]), kalo_units=int(w["kalo_units"] or 0), kalo_price=price,
            kalo_growth_pct=w["kalo_growth_pct"], seller=w["seller"], tiktok_url=w["tiktok_url"],
            match=o.get("match", "not checked"), cj_name=o.get("cj_name"), cj_sku=o.get("cj_sku"),
            cj_url=o.get("cj_url"), cj_cost=cost, cj_weight_g=o.get("weight_g"), ship_from=o.get("ship_from"),
            cj_ship=ship, ship_method=o.get("ship15_name") or o.get("cheapest_name"),
            ship_days=o.get("ship15_days") or o.get("cheapest_days"),
            landed=round(float(cost) + float(ship), 2) if usable else None,
            kept_per_order=round(k, 2) if k is not None else None,
            breakeven_cpa=round(k + 20, 2) if k is not None else None,
            price_for_10=need, vs_tiktok_pct=round(100 * (need / price - 1)) if need else None,
            sizes_ok=o.get("sizes_ok"),
            cj_listed=o.get("listed_num"), cj_stock=o.get("stock"), cj_us_stock=o.get("us_stock"),
            cj_reviews=o.get("review_count"), cj_avg_rating=o.get("avg_rating"),
            review_note=o.get("review_note"), note=o.get("match_note") or o.get("error")))
    rows.sort(key=lambda r: (r["kept_per_order"] is None, -(r["kept_per_order"] or 0)))
    stamp = dt.date.today().isoformat()
    out = os.path.join(DIR, f"picking_sheet_{stamp}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    write_xlsx(rows, out[:-4] + ".xlsx")
    usable = [r for r in rows if r["kept_per_order"] is not None]
    print(f"{len(rows)} winners, {len(usable)} with a high/medium CJ match, "
          f"{sum(r['kept_per_order'] > 0 for r in usable)} profitable at the TikTok price after a $20 CPA")
    for level in ("high", "medium", "low", "none", "not checked"):
        print(f"  {level:<12} {sum(r['match'] == level for r in rows)}")
    print(f"\n{'k':<5}{'match':<8}{'price':>7}{'landed':>8}{'kept':>8}{'listed':>7}{'stock':>8}{'rev':>6}  product")
    for r in usable:
        print(f"{r['k']:<5}{r['match']:<8}{r['kalo_price']:>7.2f}{r['landed']:>8.2f}{r['kept_per_order']:>8.2f}"
              f"{str(r['cj_listed']):>7}{str(r['cj_stock']):>8}{str(r['cj_reviews']):>6}  {r['product'][:60]}")
    print("->", out)


def write_xlsx(rows, path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    ws = wb.active
    ws.title = "Picking sheet"
    cols = list(rows[0])
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True)
    green, red = PatternFill("solid", fgColor="D9EAD3"), PatternFill("solid", fgColor="F4CCCC")
    kept_col = cols.index("kept_per_order") + 1
    for r in rows:
        ws.append([r[c] for c in cols])
        v = r["kept_per_order"]
        if v is not None:
            ws.cell(ws.max_row, kept_col).fill = green if v > 0 else red
    widths = {"product": 50, "cj_name": 40, "tiktok_url": 18, "cj_url": 18, "note": 50, "review_note": 40}
    for i, c in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(c, 12)
    ws.freeze_panes = "E2"
    ws.auto_filter.ref = ws.dimensions
    notes = wb.create_sheet("Read me")
    for line in [
        "Kalodata winners (latest stored month, TikTok Shop US) in our niche, matched to the closest CJ product.",
        "kalo_revenue / kalo_units: Kalodata estimates for the month, not audited sales.",
        "kalo_price: average TikTok selling price, used as our test price.",
        "match: high = looks like the same item; medium = close substitute; low/none = no usable CJ match.",
        "cj_cost: CJ price of the dearest variant. cj_ship: cheapest CJ freight to the US delivering within 15 days.",
        "kept_per_order: price - CJ cost - CJ shipping - 2.9% - $0.30 - 5% refunds - $20 CPA (free shipping).",
        "breakeven_cpa: the most an order can cost in ads before it loses money.",
        "price_for_10: lowest .99 price that keeps $10 per order after the $20 CPA (same rule as the pricing study).",
        "vs_tiktok_pct: how far price_for_10 sits above what TikTok buyers paid (+50 = 50% dearer).",
        "sizes_ok: CJ has women's S-XL (shoes US 6-10); false = gaps. S06 cost uses the dearest normal size "
        "(data/kalo_cj/cj_fixes.jsonl).",
        "cj_listed: how many CJ stores listed this item (seller interest / competition), not sales.",
        "cj_stock: CJ warehouse stock, all warehouses. cj_us_stock: US warehouse stock.",
        "cj_reviews / cj_avg_rating: CJ buyer reviews (often few or none).",
        "Matches were judged from CJ titles and variants, not photos. Check photos before listing anything.",
    ]:
        notes.append([line])
    notes.column_dimensions["A"].width = 120
    wb.save(path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Kalodata titles hold CJK brackets and emoji
    {"winners": winners, "build": build}[sys.argv[1]]()
