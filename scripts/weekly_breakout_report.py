"""Weekly research shortlist of rising products (PDF): a ranked list, not a forecast.

Since Market Engine 2.0 Phase B (2026-10-28, owner decision D5) the report shows no probabilities. Each product's
place comes from the adopted breakout ranker in the newest research/kalodata/model_v2_<date>/ (chosen by
scripts/market_eval.py), and the only number about outcomes is that ranker's historical hit rate: how often products
in a category's top K by the same ranker entered a top 500 within 3 months in the rolling, embargoed back-test.

Population: products on a category riser list (positions 1-200) and outside every top 500 in the latest month — the
population the hit rates were measured on. Deep riser positions 201-1,000 (Sep 2026 only) are listed separately as
"outside the tested range" with no hit rate.

Steps: build the point-in-time panel (scripts/market_data.py) for the latest stored month, or (--scan) a fresh
last-30-day pull -> score the tested population with the adopted ranker -> keep each category's top K by that rank ->
apply the price / sales / steady / not-fallen / commission-or-unbranded filters -> enrich (product detail, top
videos, buyer comments) -> PDF, CSV and a history row per pick (the live holdout log).

Paid calls: --scan (about 1.5 credits per category) and online enrichment (about 1.2 credits per product: detail 0.1,
videos 0.1, comment analysis 1, reused if pulled in the last 28 days), plus a TikTok link check per pick and a
balance call. --offline makes none of these calls: it reuses enrichment already stored in kalodata.db (or shows
"not stored") and skips the link check and balance.

Run:
  python -I scripts/weekly_breakout_report.py --offline                # latest stored month, no API calls at all
  python -I scripts/weekly_breakout_report.py                          # latest stored month, paid enrichment
  python -I scripts/weekly_breakout_report.py --scan --categories fashion --max-credits 40
Output: research/kalodata/weekly/research_shortlist_<date>.pdf (+ .csv), history in weekly/history.csv
"""
import argparse
import datetime as dt
import json
import re
import sqlite3
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import LETTER  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import inch  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,  # noqa: E402
                                Table, TableStyle)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import market_data as md  # noqa: E402
import market_eval as me  # noqa: E402

OUT = md.HUB / "research" / "kalodata"
WEEKLY = OUT / "weekly"
TITLE = "Research shortlist — not a forecast"
TASK = "breakout_3m"
FASHION = {"601152": "Womenswear & Underwear", "824328": "Menswear & Underwear", "601352": "Shoes",
           "605248": "Fashion Accessories", "953224": "Jewelry Accessories & Derivatives", "824584": "Luggage & Bags"}
SKIP_CATS = set(md.EXCLUDED_CATEGORIES)
WINTER = r"fleece|faux fur|sherpa|thermal|boot|bootie|heater|winter|puffer|wool|christmas|holiday|thanksgiving|beanie|scarf"
SUMMER = r"\bfan\b|swim|sandal|slide|flip flop|shorts|summer|cooling|beach|sunscreen"
APPAREL_CATS = {"601152", "824328", "601352", "605248", "953224", "824584", "802184", "601303"}
FORBIDDEN = re.compile(r"chance|probabilit|likelihood|(?<!not a )forecast|will break in", re.I)  # our own wording


# ---------- data ----------
def scan(cats, budget, riser_pages, today):
    """Paid: pull last-30-day top-500 and riser lists; rows in the builder's input shape (kind by page)."""
    import kalodata as k
    k.RAW = k.OUT / "raw" / f"weekly_{today}"
    rows = []
    for c in cats:
        for kind, pages, sort in (("top", 5, "revenue"), ("risers", riser_pages, "revenue_growth_rate")):
            for page in range(1, pages + 1):
                payload = dict(k.COMMON, date_range="last30Day", sort_field={"field": sort, "type": "DESC"},
                               page_size=100, page_number=page, category_ids=[c], need_extra=True)
                data = k.call("tiktok/product/rank", payload, f"weekly_{kind}_{c}_p{page}", budget, 0.1) or []
                lk = kind if kind == "top" or page <= 2 else "risers_deep"
                for i, r in enumerate(data, 1):
                    rows.append(dict(r, kind=lk, cat=c, page=page, position=i, pull_id=-1,
                                     collected_at=dt.datetime.now().isoformat(timespec="seconds")))
                if len(data) < 100:
                    break
    return md.standardize(pd.DataFrame(rows))


def ranker():
    model_dir = me.latest_model_dir()
    man = json.loads((model_dir / "manifest.json").read_text(encoding="utf-8"))
    return model_dir, man, man["tasks"][TASK]


def stored_enrichment(pid, db=None):
    """Offline: the most recent product detail, top videos and comment analysis already in kalodata.db."""
    con = md.connect_ro(db)
    info = {"detail": {}, "videos": [], "comments": None, "source": []}
    row = con.execute("SELECT d.raw_json, u.date_range, u.collected_at FROM product_details d JOIN pulls u ON "
                      "d.pull_id = u.pull_id WHERE d.product_id = ? ORDER BY u.collected_at DESC LIMIT 1",
                      (str(pid),)).fetchone()
    if row:
        info["detail"] = json.loads(row[0])
        info["source"].append(f"detail {row[1]} (stored {str(row[2])[:10]})")
    vids = con.execute("SELECT v.raw_json, u.date_range, u.collected_at FROM videos v JOIN pulls u ON "
                       "v.pull_id = u.pull_id WHERE v.product_filter = ? AND u.collected_at = (SELECT MAX(u2.collected_at) "
                       "FROM videos v2 JOIN pulls u2 ON v2.pull_id = u2.pull_id WHERE v2.product_filter = ?)",
                       (str(pid), str(pid))).fetchall()
    if vids:
        vs = [json.loads(v[0]) for v in vids]
        info["videos"] = sorted(vs, key=lambda v: -float(pd.to_numeric(v.get("revenue"), errors="coerce") or 0))[:3]
        info["source"].append(f"videos {vids[0][1]} (stored {str(vids[0][2])[:10]})")
    com = con.execute("SELECT c.raw_json, u.collected_at FROM comment_insights c JOIN pulls u ON c.pull_id = u.pull_id "
                      "WHERE c.product_id = ? ORDER BY u.collected_at DESC LIMIT 1", (str(pid),)).fetchone()
    if com:
        info["comments"] = json.loads(com[0])
        info["source"].append(f"comments (stored {str(com[1])[:10]})")
    con.close()
    return info


def recent_comments(pid, today):
    cutoff = dt.date.fromisoformat(today) - dt.timedelta(days=28)
    for f in sorted((OUT / "raw").glob(f"*/*comments_{pid}.json"), reverse=True):
        try:
            if dt.date.fromisoformat(f.parent.name.replace("weekly_", "")[:10]) >= cutoff:
                body = json.loads(f.read_text(encoding="utf-8")).get("response") or {}
                if body.get("success"):
                    return body.get("data")
        except ValueError:
            continue
    return None


def fetch(path, payload, name, budget, credits, tries=3):
    """Paid. Reuse today's saved response if it succeeded; otherwise call, retrying Kalodata timeouts."""
    import kalodata as k
    f = k.RAW / f"{name}.json"
    if f.exists():
        body = json.loads(f.read_text(encoding="utf-8")).get("response") or {}
        if body.get("success"):
            return body.get("data")
    for attempt in range(tries):
        data = k.call(path, payload, name, budget, credits)
        if data is not None:
            return data
        body = (json.loads(f.read_text(encoding="utf-8")).get("response") or {}) if f.exists() else {}
        if "timeout" not in str(body.get("message", "")).lower():
            break
        time.sleep(15 * (attempt + 1))
    return None


def enrich(pid, budget, today):
    """Paid enrichment (about 1.2 credits per product)."""
    import kalodata as k
    k.RAW = k.OUT / "raw" / f"weekly_{today}"
    info = {"source": ["fresh pull (last 30 days)"]}
    info["detail"] = fetch("tiktok/product/detail", dict(k.COMMON, date_range="last30Day", product_id=pid),
                           f"weekly_detail_{pid}", budget, 0.1) or {}
    vids = fetch("tiktok/video/rank", dict(k.COMMON, date_range="last30Day", page_size=10, page_number=1,
                                           sort_field={"field": "revenue", "type": "DESC"}, product_id=pid),
                 f"weekly_videos_{pid}", budget, 0.1) or []
    info["videos"] = vids[:3]
    info["comments"] = recent_comments(pid, today)
    if info["comments"] is None:
        info["comments"] = fetch("tiktok/product/comment/insight", {"product_id": pid, "country_code": "us"},
                                 f"weekly_comments_{pid}", budget, 1.0)
    return info


def link_ok(url, name):
    """External request to TikTok (not made with --offline)."""
    import requests
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        words = [w for w in re.sub(r"[^A-Za-z0-9 ]", " ", name).split() if len(w) > 3][:6]
        return r.status_code == 200 and sum(w.lower() in r.text.lower() for w in words) >= 2
    except requests.RequestException:
        return False


# ---------- picking ----------
def prepare(panel, attrs, label, cat_ids, spec, model_dir):
    """Rows of the latest month in the tested (risers 1-200) and outside (risers_deep) populations, scored."""
    cur = panel[(panel["month"] == label) & panel["population"].isin(["risers", "risers_deep"])
                & panel["cat"].isin(cat_ids)].copy()
    a = attrs.set_index("product_id")
    for c in ("product_name", "seller_name", "commission_rate", "sku_count", "launch_date"):
        cur[c] = cur["product_id"].map(a[c]) if c in a else np.nan
    cur["product_name"] = cur["product_name"].fillna("").astype(str)
    cur["score"] = me.score_with(spec, cur, model_dir)
    cur["rank_in_category"] = np.nan
    tested = cur["population"] == "risers"
    tb = np.random.default_rng(me.SEED).random(int(tested.sum()))
    cur.loc[tested, "rank_in_category"] = me.cat_ranks(cur.loc[tested, "cat"].values, cur.loc[tested, "score"].values,
                                                       tb)
    cur["pct_of_floor"] = cur["revenue"] / cur["floor"] * 100
    cur["seller_name"] = cur["seller_name"].fillna("").astype(str)
    cur["branded"] = [bool(s) and len(s) > 2 and s.split()[0].lower() in n.lower()
                      for s, n in zip(cur["seller_name"], cur["product_name"])]
    earlier = panel[(panel["mo"] < cur["mo"].max()) & panel["population"].isin(["top500", "risers"])]
    past_peak = earlier.groupby("product_id")["revenue"].max()
    was_top = earlier[earlier["mo"] >= cur["mo"].max() - 3].groupby("product_id")["in_top500"].any()
    cur["past_peak"] = cur["product_id"].map(past_peak)
    cur["fallen"] = (cur["past_peak"] > 1.5 * cur["revenue"]) | cur["product_id"].map(was_top).eq(True)
    cur["steady"] = (cur["months_seen_before"].fillna(0) >= 1) | (cur["kalo_growth_raw"] < 2000)
    lt = pd.to_datetime(cur["launch_date"], errors="coerce")
    cur["age_days_today"] = (pd.Timestamp(dt.date.today()) - lt).dt.days
    return cur


def filter_mask(d, args):
    m = d["unit_price"].between(args.min_price, args.max_price) & (d["revenue"] >= args.min_sales) & d["steady"]
    if not args.include_fallen:
        m &= ~d["fallen"]
    if args.purpose == "affiliate":
        m &= d["commission_rate"].fillna(0) >= args.min_commission
    else:
        m &= ~d["branded"]
    return m


def pick(cur, args):
    """Each category's top K by the adopted ranker, then the filters, then at most max_per_category per category."""
    t = cur[cur["population"] == "risers"]
    in_k = t[t["rank_in_category"] <= args.top_k]
    passed = in_k[filter_mask(in_k, args)].sort_values("score", ascending=False)
    picks = passed.groupby("cat", group_keys=False).head(args.max_per_category).head(args.n)
    return picks, len(in_k), len(passed)


def outside(cur, args):
    d = cur[cur["population"] == "risers_deep"]
    d = d[filter_mask(d, args)].sort_values("score", ascending=False)
    return d.groupby("cat", group_keys=False).head(args.max_per_category).head(args.outside_n)


# ---------- text helpers ----------
def clean(s, n=None):
    s = "".join(ch for ch in str(s) if ord(ch) < 0x2000 or ch in "–—‘’“”•…×")
    s = re.sub(r"\s+", " ", s).strip()
    return (s[: n - 1] + "…") if n and len(s) > n else s


def money(v):
    return "–" if pd.isna(v) else (f"${v / 1000:,.1f}K" if v >= 1000 else f"${v:,.0f}")


def pct(v, digits=0):
    return "–" if v is None or pd.isna(v) else f"{v * 100:.{digits}f}%"


def points(lst, n=3):
    if not lst:
        return "–"
    lst = sorted(lst, key=lambda x: -len(x.get("id_list") or []))[:n]
    return "; ".join(f"{clean(x.get('view_point'))} ({len(x.get('id_list') or [])} reviews)" for x in lst)


def ranker_label(spec):
    if spec["type"] == "baseline":
        return f"rule: {spec.get('label', spec['name'])}"
    return f"{spec['name']} ranking score (cleaned point-in-time features)"


def hit_line(hr, k):
    x = hr.get(f"p_cat@{k}") or {}
    if not x:
        return "–"
    return f"{pct(x['hit_rate'])} ({x['hits']} of {x['picks']})"


def fit_and_risks(r, info):
    name = r["product_name"].lower()
    det = info["detail"] or {}
    season = "autumn/winter" if re.search(WINTER, name) else ("summer" if re.search(SUMMER, name) else "not obviously seasonal")
    apparel = r["cat"] in APPAREL_CATS
    angle = ("AI try-on: show fit, fabric and the key detail up close; the hook calls out who it's for" if apparel
             else "AI demo: show the problem it solves, then the product doing it")
    fit = [("Who could use it", "Affiliate only: seller's own brand, we can't stock it" if r["branded"]
            else "Affiliate, or look for an unbranded version to stock"),
           ("Season", season),
           ("Video angle to test", angle + ". Rules: AI label on, no 'I bought it', no price or delivery claims.")]
    risks = []
    if r["branded"]:
        risks.append("Brand: affiliate only.")
    if season != "not obviously seasonal":
        risks.append(f"Seasonal ({season}): the window may close after the season.")
    creators = pd.to_numeric(det.get("creator_number"), errors="coerce")
    if pd.notna(creators) and creators > 200:
        risks.append(f"Crowded: {int(creators)} creators already promoting it.")
    if str(det.get("delivery_type") or "").lower() in ("global", "cross_border", "crossborder", "2"):
        risks.append("Ships cross-border: slower delivery, more complaints.")
    if pd.notna(r["pct_of_floor"]) and r["pct_of_floor"] < 25:
        risks.append(f"Sales are only {r['pct_of_floor']:.0f}% of the category's top-500 bar.")
    pains = " ".join((x.get("view_point") or "").lower() for x in ((info["comments"] or {}).get("pain_points") or []))
    if re.search(r"size|fit|small|large", pains):
        risks.append("Buyers mention sizing problems: return risk.")
    if re.search(r"quality|cheap|thin|broke", pains):
        risks.append("Buyers mention quality problems.")
    if re.search(r"photo|picture|different|expect", pains):
        risks.append("Buyers say it looks different from the photos.")
    return fit, risks or ["None flagged beyond the usual: Kalodata figures are estimates."]


def sparkline(path, out_png):
    fig, ax = plt.subplots(figsize=(6.6, 1.5), dpi=150)
    labels = [m[2:] for m, _ in path]
    vals = [v / 1000 for _, v in path]
    ax.bar(labels, vals, color="#c4471f")
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:,.1f}K", ha="center", va="bottom", fontsize=6)
    ax.set_ylabel("$K / month", fontsize=7)
    ax.tick_params(labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


# ---------- PDF ----------
def styles():
    font, bold = "Helvetica", "Helvetica-Bold"
    fonts = Path("C:/Windows/Fonts")
    if (fonts / "arial.ttf").exists():
        pdfmetrics.registerFont(TTFont("Arial", str(fonts / "arial.ttf")))
        pdfmetrics.registerFont(TTFont("Arial-Bold", str(fonts / "arialbd.ttf")))
        font, bold = "Arial", "Arial-Bold"
    ss = getSampleStyleSheet()
    base = ParagraphStyle("b", parent=ss["Normal"], fontName=font, fontSize=8.5, leading=11, alignment=TA_LEFT)
    st = {"font": font, "bold": bold, "body": base,
          "small": ParagraphStyle("s", parent=base, fontSize=7.5, leading=9.5),
          "h1": ParagraphStyle("h1", parent=base, fontName=bold, fontSize=16, leading=20, spaceAfter=4),
          "h2": ParagraphStyle("h2", parent=base, fontName=bold, fontSize=12, leading=15, spaceBefore=4, spaceAfter=3),
          "h3": ParagraphStyle("h3", parent=base, fontName=bold, fontSize=9.5, leading=12, spaceBefore=5, spaceAfter=2)}
    for k in ("body", "small", "h2"):  # third-party text (product titles, video captions, buyer comments)
        st[f"{k}_3p"] = ParagraphStyle(f"{st[k].name}_3p", parent=st[k])
    return st


def p3(text, st, style="small"):
    """Paragraph holding third-party text: shown as is, skipped by the wording check."""
    return Paragraph(text, st[f"{style}_3p"])


def table(data, st, widths, header=True):
    rows = [[c if not isinstance(c, str) else Paragraph(c, st["small"]) for c in r] for r in data]
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d9d2cb")),
             ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3ece6")))
    t.setStyle(TableStyle(style))
    return t


def link(url, text):
    return f'<a href="{escape(url)}" color="#1a56b0">{escape(text)}</a>'


def link_text(r):
    return {True: "Open", False: "Open (check)", None: "Open (not checked)"}[r["link_ok"]]


def story(picks, deep, meta, st, W):
    S = [Paragraph(escape(meta["title"]), st["h1"]), Paragraph(escape(meta["subtitle"]), st["body"]), Spacer(1, 6),
         table([[escape(a), escape(b)] for a, b in meta["settings"]], st, [1.6 * inch, W - 1.6 * inch], header=False),
         Spacer(1, 8), Paragraph("Summary", st["h2"])]
    rows = [["#", "Product", "Category", "Rank in cat.", "% of top-500 bar", "Price", "Comm.", "Sales (month)",
             "Status", "Link"]]
    for i, r in enumerate(picks, 1):
        rows.append([str(i), p3(escape(clean(r["product_name"], 48)), st), escape(clean(r["category"], 22)),
                     f"{int(r['rank_in_category'])}", f"{r['pct_of_floor']:.0f}%", f"${r['unit_price']:.2f}",
                     "–" if pd.isna(r["commission_rate"]) else f"{r['commission_rate']:.0f}%", money(r["revenue"]),
                     escape(r["status"]), link(r["url"], link_text(r))])
    S.append(table(rows, st, [x * inch for x in (0.3, 1.85, 1.05, 0.55, 0.65, 0.55, 0.55, 0.65, 0.55, 0.65)]))
    S += [Spacer(1, 8), Paragraph("How these were picked", st["h2"])]
    S += [Paragraph("• " + escape(line), st["body"]) for line in meta["method"]]
    for i, r in enumerate(picks, 1):
        S.append(PageBreak())
        S += product_page(i, r, meta, st, W)
    if deep:
        S += [PageBreak(), Paragraph("Outside the tested range (riser positions 201–1,000)", st["h2"]),
              Paragraph(escape(meta["deep_note"]), st["body"]), Spacer(1, 4)]
        drows = [["Product", "Category", "Riser pos.", "% of top-500 bar", "Price", "Sales (month)"]]
        for r in deep:
            drows.append([p3(escape(clean(r["product_name"], 60)), st), escape(clean(r["category"], 24)),
                          f"{int(r['deep_riser_pos'])}", f"{r['pct_of_floor']:.0f}%", f"${r['unit_price']:.2f}",
                          money(r["revenue"])])
        S.append(table(drows, st, [x * inch for x in (2.9, 1.4, 0.65, 0.8, 0.6, 0.8)]))
    S += [PageBreak(), Paragraph("Limits", st["h2"])]
    S += [Paragraph("• " + escape(line), st["body"]) for line in meta["limits"]]
    return S


def product_page(i, r, meta, st, W):
    info = r["info"]
    det = info["detail"] or {}
    cat_hr = r.get("cat_hit")
    S = [p3(f"{i}. {escape(clean(r['product_name'], 110))}", st, "h2"),
         Paragraph(f"{escape(r['category'])} · {link(r['url'], 'TikTok Shop page')}"
                   f"{ {True: ' (checked: opens)', False: ' (could not confirm it opens)', None: ' (not checked)'}[r['link_ok']]}"
                   f" · Kalodata ID {r['product_id']}", st["body"]),
         Paragraph(f"<b>Rank:</b> {int(r['rank_in_category'])} of {int(r['n_in_category'])} in its category by the "
                   f"adopted ranker · {escape(r['verdict'])} · {escape(r['status'])}", st["body"]),
         Paragraph(f"<b>Track record of this rank:</b> in the back-test, a category's top 10 by this ranker entered a "
                   f"top 500 within 3 months {escape(meta['hit10'])}; top 3: {escape(meta['hit3'])}"
                   + (f"; in {escape(r['category'])}: {pct(cat_hr['hit_rate'])} of {cat_hr['picks']} top-10 picks"
                      if cat_hr and cat_hr.get("hit_rate") is not None else "") + ".", st["body"]),
         Spacer(1, 4)]
    S.append(Paragraph("The numbers", st["h3"]))
    S.append(table([["Price", "Sales (month)", "Units", "MoM growth", "Commission*", "Your cut*", "From videos",
                     "Age*", "Variants*"],
                    [f"${r['unit_price']:.2f}", money(r["revenue"]), f"{r['units']:,.0f}",
                     "–" if pd.isna(r["mom_growth"]) else f"{np.expm1(r['mom_growth']) * 100:+,.0f}%",
                     "–" if pd.isna(r["commission_rate"]) else f"{r['commission_rate']:.0f}%",
                     "–" if pd.isna(r["commission_rate"]) else f"${r['unit_price'] * r['commission_rate'] / 100:.2f}",
                     pct(r["video_share"]),
                     "–" if pd.isna(r["age_days_today"]) else f"{r['age_days_today'] / 30:.0f} mo",
                     "–" if pd.isna(r["sku_count"]) else f"{r['sku_count']:.0f}"]],
                   st, [W / 9] * 9))
    S.append(Paragraph("* values as of the pull date (Kalodata gives only today's commission, variants and listing "
                       "date). MoM growth is our own month-on-month change, '–' when not listed last month.",
                       st["small"]))
    S.append(Paragraph("Path so far (monthly sales; a missing month means it wasn't on our lists)", st["h3"]))
    if r.get("spark") and Path(r["spark"]).exists():
        S.append(Image(str(r["spark"]), width=W, height=W * 1.5 / 6.6))
    S.append(Paragraph(f"Top-500 bar: the category's top 500 starts at {money(r['floor'])} a month; this product is at "
                       f"{r['pct_of_floor']:.0f}% of it.", st["body"]))
    S.append(Paragraph("What puts it at this rank", st["h3"]))
    for line in r["why"]:
        S.append(Paragraph("• " + escape(line), st["body"]))
    S.append(Paragraph("Competition", st["h3"]))
    cr, vn = pd.to_numeric(det.get("creator_number"), errors="coerce"), pd.to_numeric(det.get("video_number"), errors="coerce")
    spv = r["revenue"] / vn if pd.notna(vn) and vn else np.nan
    S.append(Paragraph(f"{'–' if pd.isna(cr) else f'{cr:,.0f}'} creators · {'–' if pd.isna(vn) else f'{vn:,.0f}'} videos "
                       f"· {money(spv)} sales per video · reviews {det.get('product_review_count', '–')}"
                       f" · source: {escape('; '.join(info.get('source') or ['not stored']))}", st["body"]))
    vrows = [["Top videos", "Creator", "Sales", "Views", "AI", "Ad"]]
    for v in info["videos"]:
        url = f"https://www.tiktok.com/@{v.get('belonged_creator_handle')}/video/{v.get('video_id')}"
        vrows.append([p3(link(url, clean(v.get("video_title") or "(no caption)", 60)), st),
                      p3(escape(f"@{v.get('belonged_creator_handle')}"), st),
                      money(pd.to_numeric(v.get("revenue"), errors="coerce")),
                      f"{pd.to_numeric(v.get('views'), errors='coerce'):,.0f}", "yes" if str(v.get("ai_video")) == "1" else "no",
                      "yes" if str(v.get("ad")) == "1" else "no"])
    if len(vrows) > 1:
        S.append(table(vrows, st, [x * inch for x in (3.2, 1.3, 0.7, 0.8, 0.45, 0.45)]))
    com = info["comments"] or {}
    S.append(Paragraph("What buyers say", st["h3"]))
    if not com:
        S.append(Paragraph("No comment analysis available for this product.", st["body"]))
    S.append(p3(f"<b>Complaints:</b> {escape(points(com.get('pain_points')))}", st, "body"))
    S.append(p3(f"<b>Praise:</b> {escape(points(com.get('positive_points')))}", st, "body"))
    S.append(p3(f"<b>Used for:</b> {escape(points(com.get('usage_scenarios'), 2))}", st, "body"))
    S.append(Paragraph("Fit for us", st["h3"]))
    for a, b in r["fit"]:
        S.append(Paragraph(f"<b>{escape(a)}:</b> {escape(b)}", st["body"]))
    S.append(Paragraph("Risks", st["h3"]))
    for x in r["risks"]:
        S.append(Paragraph("• " + escape(x), st["body"]))
    return [KeepTogether(S[:5])] + S[5:]


def why_lines(r):
    out = [f"Sales are {r['pct_of_floor']:.0f}% of the category's 500th-place sales (the strongest single signal in "
           "the back-test)."]
    out.append("Our month-on-month growth: " + ("not listed last month" if pd.isna(r["mom_growth"]) else
                                                 f"{np.expm1(r['mom_growth']) * 100:+,.0f}%") + ".")
    if pd.notna(r["months_seen_before"]):
        out.append(f"Months already on our lists before this one: {int(r['months_seen_before'])}.")
    if pd.notna(r["price_vs_cat"]):
        out.append(f"Price vs the category's top-500 median: {r['price_vs_cat']:.2f}x.")
    if pd.notna(r["riser_pos"]):
        out.append(f"Position on the riser list (Kalodata growth sort): {int(r['riser_pos'])}.")
    return out


def text_of(flowables, own_only=False):
    """Visible text in a story; own_only skips third-party text (product titles, captions, buyer comments)."""
    out = []

    def walk(x):
        if isinstance(x, Paragraph):
            if not (own_only and x.style.name.endswith("_3p")):
                out.append(x.getPlainText())
        elif isinstance(x, KeepTogether):
            for y in x._content:
                walk(y)
        elif isinstance(x, Table):
            for row in x._cellvalues:
                for c in row:
                    walk(c)
        elif isinstance(x, (list, tuple)):
            for y in x:
                walk(y)
        elif isinstance(x, str):
            out.append(x)
    walk(flowables)
    return "\n".join(out)


def build_meta(today, window, args, spec, task_info, model_dir, n_scored, n_topk, n_passed, n_picks, credits, balance,
               n_deep):
    hr = task_info["hit_rates_all_evaluated_months"]
    months = hr["months"]
    hit10, hit3 = hit_line(hr, 10), hit_line(hr, 3)
    return {
        "title": f"{TITLE}: {today}",
        "subtitle": f"{n_picks} rising products ranked by the adopted breakout ranker, for research. A rank is an "
                    f"ordering, not a forecast. Ember & Clove · {args.purpose} view.",
        "hit10": hit10, "hit3": hit3,
        "settings": [("Data", window), ("Purpose", args.purpose), ("Categories", args.categories),
                     ("Population", "risers 1–200 outside every top 500 (the tested population); riser positions "
                                    "201–1,000 appear only in the 'outside the tested range' list"),
                     ("Ranker", f"{ranker_label(spec)} · {model_dir.name}"),
                     ("Track record", f"category top 10 entered a top 500 within 3 months: {hit10}; top 3: {hit3} "
                                      f"(back-test months {months[0]}–{months[-1]}; all risers: "
                                      f"{pct(hr['base_rate'], 1)})"),
                     ("Filters", f"top {args.top_k} per category by rank; price ${args.min_price:.0f}–"
                                 f"{args.max_price:.0f}; sales ≥ ${args.min_sales:,.0f}/month; steady growth; "
                                 + ("" if args.include_fallen else "not past an earlier peak; ")
                                 + f"≤ {args.max_per_category} per category"
                                 + (f"; commission ≥ {args.min_commission:.0f}% (as of the pull date)"
                                    if args.purpose == "affiliate" else "; unbranded only")),
                     ("Candidates", f"{n_scored:,} risers ranked; {n_topk:,} in a category top {args.top_k}; "
                                    f"{n_passed} passed the filters"),
                     ("API use", "none (offline edition: stored enrichment, no link check)" if args.offline else
                      f"{credits:.1f} credits charged this run; balance {balance}")],
        "method": [f"Ranker: {ranker_label(spec)}. It was chosen by the Phase B evaluation (scripts/market_eval.py): "
                   "rolling forward tests with an embargo, compared with simple rules and a model on the same data; "
                   "the decision is in the research_runs registry (" + task_info["registry_run_id"] + ").",
                   f"Track record: across back-test months {months[0]}–{months[-1]}, products in a category's top 10 by "
                   f"this ranker entered a top 500 within 3 months {hit10}; a category's top 3: {hit3}. All risers in "
                   f"the tested population: {pct(hr['base_rate'], 1)}.",
                   "The filters (price, sales, steady growth, not fallen, commission or branding) were not part of "
                   "that test; their effect on the hit rate is unknown until the logged picks can be checked.",
                   "Rank in category = place among this month's tested risers in the same category, before filters.",
                   "Links go to the product's TikTok Shop page"
                   + ("; this offline edition did not check them." if args.offline else
                      "; 'Open (check)' means the automatic check couldn't confirm it today.")],
        "deep_note": f"{n_deep:,} products from riser positions 201–1,000 (pulled only for Sep 2026) were ranked with the "
                     "same ranker but have no track record: nothing from this depth was in the back-test. Listed for "
                     "research only, after the same filters.",
        "limits": ["Kalodata sales are estimates; the ranker sees sales patterns only, not looks, quality or trends "
                   "off TikTok.",
                   "Ten months of usable history (Oct 2025 is a partial month and excluded): holiday seasonality isn't "
                   "in the back-test.",
                   "Only about 4% of products that enter a top 500 come from the previous month's riser list: this "
                   "shortlist covers a small corner of where new top-500 products come from.",
                   "Commission, variants and age are today's values, not what the product looked like earlier.",
                   "Brand and season flags are keyword checks; confirm before acting.",
                   "Check back: every pick is logged in weekly/history.csv before its outcome exists."]}


# ---------- main ----------
def parse(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", choices=["affiliate", "store"], default="affiliate")
    ap.add_argument("--categories", default="all", help="all, fashion, or comma-separated category IDs")
    ap.add_argument("--scan", action="store_true", help="paid: pull fresh last-30-day lists from Kalodata first")
    ap.add_argument("--offline", action="store_true",
                    help="no API or web calls: stored enrichment only, no link check, no balance call")
    ap.add_argument("--riser-pages", type=int, default=2, help="with --scan: riser pages (2 = the tested range)")
    ap.add_argument("--max-credits", type=float, default=15)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--top-k", type=int, default=10, help="keep each category's top K by the ranker before filters")
    ap.add_argument("--min-commission", type=float, default=10)
    ap.add_argument("--min-price", type=float, default=15)
    ap.add_argument("--max-price", type=float, default=60)
    ap.add_argument("--min-sales", type=float, default=3000)
    ap.add_argument("--max-per-category", type=int, default=3)
    ap.add_argument("--outside-n", type=int, default=10, help="rows in the 'outside the tested range' list")
    ap.add_argument("--include-fallen", action="store_true",
                    help="also allow products that sold 1.5x more in an earlier month or were top 500 recently")
    a = ap.parse_args(argv)
    if a.scan and a.offline:
        ap.error("--scan makes paid calls; it can't be combined with --offline")
    return a


def main(argv=None):
    args = parse(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    today = dt.date.today().isoformat()
    WEEKLY.mkdir(parents=True, exist_ok=True)
    model_dir, man, task_info = ranker()
    spec = task_info["ranker"]
    rows, cats, _, _ = md.load_rows()
    budget = None
    if args.scan:
        import kalodata as k
        budget = k.Budget(args.max_credits)
    base_cats = sorted(c for c in rows["cat"].unique() if c not in SKIP_CATS)
    cat_ids = base_cats if args.categories == "all" else (sorted(FASHION) if args.categories == "fashion"
                                                         else args.categories.split(","))
    if args.scan:
        label = today[:7]
        live = scan(cat_ids, budget, args.riser_pages, today)
        live["month"] = label
        rows = pd.concat([rows[rows["month"] < label], live], ignore_index=True)
        window = f"Last 30 days to {today} (fresh scan, labelled {label})"
    panel, attrs, info = md.build(rows)
    if not args.scan:
        label = info["data_cutoff"]
        window = f"{label} (latest month stored)"
    print(f"Ranking {window} with {ranker_label(spec)} from {model_dir.name}")
    cur = prepare(panel, attrs, label, cat_ids, spec, model_dir)
    cur["category"] = cur["cat"].map(cats).fillna(cur["cat"])
    picks_df, n_topk, n_passed = pick(cur, args)
    deep_df = outside(cur, args)
    n_tested = int((cur["population"] == "risers").sum())
    n_deep = int((cur["population"] == "risers_deep").sum())
    print(f"{n_tested:,} tested risers ranked ({n_deep:,} outside the tested range); {n_topk} in a category top "
          f"{args.top_k}; {n_passed} pass the filters; picking {len(picks_df)}")
    n_cat = cur[cur["population"] == "risers"].groupby("cat").size()
    by_cat = task_info["hit_rates_all_evaluated_months"].get("by_category_p_cat@10", {})

    hist_path = WEEKLY / "history.csv"
    hist = pd.read_csv(hist_path, dtype={"product_id": str}) if hist_path.exists() else \
        pd.DataFrame(columns=["date", "product_id"])
    hist = hist[hist["date"] != today]  # a rerun on the same day replaces that day's picks
    picks = []
    for _, r in picks_df.iterrows():
        r = r.to_dict()
        r["n_in_category"] = int(n_cat.get(r["cat"], 0))
        r["cat_hit"] = by_cat.get(r["cat"])
        r["info"] = stored_enrichment(r["product_id"]) if args.offline else enrich(r["product_id"], budget or
                                                                                    _budget(args), today)
        r["url"] = f"https://www.tiktok.com/view/product/{r['product_id']}?region=US"
        r["link_ok"] = None if args.offline else link_ok(r["url"], r["product_name"])
        seen = hist[hist["product_id"] == str(r["product_id"])]
        r["status"] = f"repeat ({len(seen)}x)" if len(seen) else "new"
        r["verdict"] = ("Affiliate only (brand)" if r["branded"] else "Affiliate candidate") if args.purpose == "affiliate" \
            else "Store candidate: find an unbranded supplier"
        path_rows = panel[panel["product_id"] == r["product_id"]].sort_values("mo")[["month", "revenue"]]
        r["path"] = list(path_rows.itertuples(index=False, name=None))
        r["spark"] = WEEKLY / f"_spark_{r['product_id']}.png"
        sparkline(r["path"], r["spark"])
        r["fit"], r["risks"] = fit_and_risks(r, r["info"])
        r["why"] = why_lines(r)
        picks.append(r)
        print(f"  {r['category']}: {clean(r['product_name'], 60)} | rank {int(r['rank_in_category'])} in category")
    deep = [dict(d, category=d["category"]) for d in deep_df.to_dict("records")]

    balance = None
    if not args.offline:
        import kalodata as k
        balance = (k.call("credit/balance", {}, "balance", method="GET") or {}).get("totalRemain")
    spent = (budget.spent if budget else 0.0) + (_BUDGET[0].spent if _BUDGET else 0.0)
    meta = build_meta(today, window, args, spec, task_info, model_dir, n_tested, n_topk, n_passed, len(picks), spent,
                      balance, n_deep)
    st = styles()
    W = LETTER[0] - 1.2 * inch
    flow = story(picks, deep, meta, st, W)
    bad = [m.group(0) for m in FORBIDDEN.finditer(text_of(flow, own_only=True))]
    if bad:
        raise SystemExit(f"Report text contains forecast wording {set(bad)}; fix the wording before publishing")
    pdf = WEEKLY / f"research_shortlist_{today}.pdf"
    doc = SimpleDocTemplate(str(pdf), pagesize=LETTER, leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.55 * inch, bottomMargin=0.55 * inch, title=meta["title"])
    doc.build(flow)
    cols = ["category", "product_id", "product_name", "unit_price", "revenue", "rank_in_category", "pct_of_floor",
            "mom_growth", "commission_rate", "branded", "status", "url", "link_ok"]
    pd.DataFrame(picks, columns=cols + ["info"])[cols].to_csv(WEEKLY / f"research_shortlist_{today}.csv", index=False)
    hr = task_info["hit_rates_all_evaluated_months"]
    new_hist = pd.DataFrame([{"date": today, "product_id": str(r["product_id"]), "product_name": r["product_name"],
                              "category": r["category"], "rank_in_category": int(r["rank_in_category"]),
                              "ranker": spec["name"], "model_dir": model_dir.name,
                              "hit_rate_top10_backtest": (hr.get("p_cat@10") or {}).get("hit_rate"),
                              "sales": r["revenue"], "data": window} for r in picks])
    pd.concat([hist, new_hist], ignore_index=True).to_csv(hist_path, index=False)
    for r in picks:
        Path(r["spark"]).unlink(missing_ok=True)
    print(f"Saved {pdf} ({'no API calls' if args.offline else f'{spent:.1f} credits'})")
    return pdf


_BUDGET = []


def _budget(args):
    """Paid enrichment without --scan still runs under a credit cap."""
    if not _BUDGET:
        import kalodata as k
        _BUDGET.append(k.Budget(args.max_credits))
    return _BUDGET[0]


if __name__ == "__main__":
    main()
