"""Weekly breakout report: 10 products the model says are likely to break into their category's top 500, as a PDF.

Steps: (optionally) scan Kalodata for the last 30 days -> score every riser outside its category's top 500 with the
3-month breakout model -> pick 10 with the filters below -> enrich each (product detail, its top videos, buyer-comment
analysis) -> check each TikTok Shop link opens -> write the PDF, a CSV and a history row per pick.

Without --scan it uses the latest month already downloaded (core data). --scan pulls fresh last-30-day lists:
the top 500 and the top 1,000 risers per category, 1.5 credits per category (all 28 ≈ 42, fashion's 6 ≈ 9; fewer
with --riser-pages). Enrichment is about 1.2 credits per product (comment analysis 1, reused if pulled in the last
28 days).

Run:
  python -I scripts/weekly_breakout_report.py                      # latest downloaded month, affiliate, all categories
  python -I scripts/weekly_breakout_report.py --scan --categories fashion --max-credits 40
Output: research/kalodata/weekly/weekly_breakouts_<date>.pdf (+ .csv), history in weekly/history.csv
"""
import argparse
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape

import joblib
import matplotlib
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import HistGradientBoostingClassifier

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
import kalodata as k  # noqa: E402
import train_product_model as tp  # noqa: E402
from explain_breakouts import LABEL, show  # noqa: E402
from score_breakouts import FEATS  # noqa: E402

WEEKLY = k.OUT / "weekly"
MODEL_CACHE = tp.OUT / "breakout_models.joblib"
FASHION = {"601152": "Womenswear & Underwear", "824328": "Menswear & Underwear", "601352": "Shoes",
           "605248": "Fashion Accessories", "953224": "Jewelry Accessories & Derivatives", "824584": "Luggage & Bags"}
SKIP_CATS = {"834312"}  # Virtual Products: no data
WINTER = r"fleece|faux fur|sherpa|thermal|boot|bootie|heater|winter|puffer|wool|christmas|holiday|thanksgiving|beanie|scarf"
SUMMER = r"\bfan\b|swim|sandal|slide|flip flop|shorts|summer|cooling|beach|sunscreen"
APPAREL_CATS = {"601152", "824328", "601352", "605248", "953224", "824584", "802184", "601303"}


# ---------- data ----------
def scan(cats, budget, riser_pages, today):
    """Pull last-30-day risers and top-500 lists; return rows shaped like train_product_model.load()."""
    k.RAW = k.OUT / "raw" / f"weekly_{today}"
    rows = []
    for c in cats:
        for kind, pages, sort in (("products", 5, "revenue"), ("risers", riser_pages, "revenue_growth_rate")):
            for page in range(1, pages + 1):
                payload = dict(k.COMMON, date_range="last30Day", sort_field={"field": sort, "type": "DESC"},
                               page_size=100, page_number=page, category_ids=[c], need_extra=True)
                data = k.call("tiktok/product/rank", payload, f"weekly_{kind}_{c}_p{page}", budget, 0.1) or []
                for i, r in enumerate(data, 1):
                    rows.append(dict(r, list=kind, cat=c, position=i, pos=(page - 1) * 100 + i))
                if len(data) < 100:
                    break
    df = pd.DataFrame(rows)
    df[tp.NUM] = df[tp.NUM].apply(pd.to_numeric, errors="coerce")
    df["name"] = "scan"
    return df


def live_label(today):
    return today[:7]  # the last 30 days are labelled with the current month


def extend_months(label):
    """Add the scan month (and any gap months) after the last core month, so lag features line up."""
    last = pd.Period(tp.MONTHS[-1], "M")
    target = pd.Period(label, "M")
    while last < target:
        last += 1
        tp.MONTHS.append(str(last))
        tp.MI[str(last)] = len(tp.MONTHS) - 1


def train_or_load(p):
    core_months = list(tp.MONTHS)
    if MODEL_CACHE.exists():
        cached = joblib.load(MODEL_CACHE)
        if cached.get("months") == core_months and cached.get("feats") == FEATS:
            return cached
    models = {}
    for name in ("breakouts_1m", "breakouts_3m"):
        which, label, h = tp.TASKS[name]
        d = tp.subset(p, which, h)
        d["y"] = label(d)
        models[name] = HistGradientBoostingClassifier(**tp.HGB).fit(d[FEATS], d["y"])
        if name == "breakouts_3m":
            ref = d[FEATS].median()
    cached = {"months": core_months, "feats": FEATS, "models": models, "ref": ref}
    joblib.dump(cached, MODEL_CACHE)
    return cached


def seller_names(pids):
    import sqlite3
    con = sqlite3.connect(f"file:{tp.DB}?mode=ro", uri=True)
    q = f"SELECT product_id, seller_name FROM products WHERE product_id IN ({','.join('?' * len(pids))})"
    out = dict(con.execute(q, list(pids)).fetchall())
    con.close()
    return out


# ---------- picking ----------
def pick(cur, args):
    d = cur.copy()
    d["growth_pct"] = d["revenue_growth_rate"]
    d["steady"] = (d["months_seen_before"].fillna(0) >= 1) | (d["growth_pct"] < 2000)
    mask = (d["p_breakouts_3m"] >= args.min_chance) & d["unit_price"].between(args.min_price, args.max_price) & \
        (d["revenue"] >= args.min_sales) & d["steady"]
    if not args.include_fallen:  # early risers only: not products sliding back from an earlier, bigger month
        mask &= ~d["fallen"]
    if args.purpose == "affiliate":
        mask &= d["commission_rate"] >= args.min_commission
    else:
        mask &= ~d["branded"]
    passed = d[mask].sort_values("p_breakouts_3m", ascending=False)
    picks = passed.groupby("cat", group_keys=False).head(args.max_per_category).head(args.n)
    return picks, len(passed)


def contributions(model, ref, row):
    base = float(model.predict_proba(row[FEATS])[:, 1][0])
    out = []
    for f in FEATS:
        alt = row[FEATS].copy()
        alt[f] = ref[f]
        out.append((f, base - float(model.predict_proba(alt)[:, 1][0])))
    return sorted(out, key=lambda x: -abs(x[1]))[:5]


# ---------- enrichment ----------
def recent_comments(pid, today):
    cutoff = dt.date.fromisoformat(today) - dt.timedelta(days=28)
    for f in sorted((k.OUT / "raw").glob(f"*/*comments_{pid}.json"), reverse=True):
        try:
            if dt.date.fromisoformat(f.parent.name.replace("weekly_", "")[:10]) >= cutoff:
                body = json.loads(f.read_text(encoding="utf-8")).get("response") or {}
                if body.get("success"):
                    return body.get("data")
        except ValueError:
            continue
    return None


def fetch(path, payload, name, budget, credits, tries=3):
    """Reuse today's saved response if it succeeded; otherwise call, retrying Kalodata timeouts."""
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
    k.RAW = k.OUT / "raw" / f"weekly_{today}"
    info = {}
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
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        words = [w for w in re.sub(r"[^A-Za-z0-9 ]", " ", name).split() if len(w) > 3][:6]
        return r.status_code == 200 and sum(w.lower() in r.text.lower() for w in words) >= 2
    except requests.RequestException:
        return False


# ---------- text helpers ----------
def clean(s, n=None):
    s = "".join(ch for ch in str(s) if ord(ch) < 0x2000 or ch in "–—‘’“”•…×")
    s = re.sub(r"\s+", " ", s).strip()
    return (s[: n - 1] + "…") if n and len(s) > n else s


def money(v):
    return "–" if pd.isna(v) else (f"${v / 1000:,.1f}K" if v >= 1000 else f"${v:,.0f}")


def points(lst, n=3):
    if not lst:
        return "–"
    lst = sorted(lst, key=lambda x: -len(x.get("id_list") or []))[:n]
    return "; ".join(f"{clean(x.get('view_point'))} ({len(x.get('id_list') or [])} reviews)" for x in lst)


def fit_and_risks(r, info, args):
    name = r["product_name"].lower()
    det = info["detail"]
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
    if pd.notna(r.get("riser_pos")) and r["riser_pos"] > 200:
        risks.append("Ranked below 200 on growth: outside the model's training range, treat the score as a ranking.")
    if r["pct_of_floor"] < 25:
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
    return {"font": font, "bold": bold, "body": base,
            "small": ParagraphStyle("s", parent=base, fontSize=7.5, leading=9.5),
            "h1": ParagraphStyle("h1", parent=base, fontName=bold, fontSize=16, leading=20, spaceAfter=4),
            "h2": ParagraphStyle("h2", parent=base, fontName=bold, fontSize=12, leading=15, spaceBefore=4, spaceAfter=3),
            "h3": ParagraphStyle("h3", parent=base, fontName=bold, fontSize=9.5, leading=12, spaceBefore=5, spaceAfter=2)}


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


def build_pdf(path, picks, meta, st):
    doc = SimpleDocTemplate(str(path), pagesize=LETTER, leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.55 * inch, bottomMargin=0.55 * inch, title=meta["title"])
    W = LETTER[0] - 1.2 * inch
    S = []
    S.append(Paragraph(escape(meta["title"]), st["h1"]))
    S.append(Paragraph(escape(meta["subtitle"]), st["body"]))
    S.append(Spacer(1, 6))
    S.append(table([[escape(a), escape(b)] for a, b in meta["settings"]], st, [1.6 * inch, W - 1.6 * inch], header=False))
    S.append(Spacer(1, 8))
    S.append(Paragraph("Summary", st["h2"]))
    rows = [["#", "Product", "Category", "Chance 3 mo", "Price", "Comm.", "Cut / sale", "Sales (30 d)", "Status", "Link"]]
    for i, r in enumerate(picks, 1):
        rows.append([str(i), escape(clean(r["product_name"], 48)), escape(clean(r["category"], 22)),
                     f"{r['p_breakouts_3m']:.0%}", f"${r['unit_price']:.2f}", f"{r['commission_rate']:.0f}%",
                     f"${r['unit_price'] * r['commission_rate'] / 100:.2f}", money(r["revenue"]),
                     escape(r["status"]), link(r["url"], "Open" if r["link_ok"] else "Open (check)")])
    S.append(table(rows, st, [x * inch for x in (0.3, 1.95, 1.05, 0.6, 0.55, 0.45, 0.55, 0.65, 0.55, 0.65)]))
    S.append(Spacer(1, 8))
    S.append(Paragraph("How these were picked", st["h2"]))
    for line in meta["method"]:
        S.append(Paragraph("• " + escape(line), st["body"]))
    for i, r in enumerate(picks, 1):
        S.append(PageBreak())
        S += product_page(i, r, st, W)
    S.append(PageBreak())
    S.append(Paragraph("Limits", st["h2"]))
    for line in meta["limits"]:
        S.append(Paragraph("• " + escape(line), st["body"]))
    doc.build(S)


def product_page(i, r, st, W):
    det, info = r["info"]["detail"], r["info"]
    S = [Paragraph(f"{i}. {escape(clean(r['product_name'], 110))}", st["h2"]),
         Paragraph(f"{escape(r['category'])} · {link(r['url'], 'TikTok Shop page')}"
                   f"{' (checked: opens)' if r['link_ok'] else ' (could not confirm it opens)'} · Kalodata ID {r['product_id']}",
                   st["body"]),
         Paragraph(f"<b>Verdict:</b> {escape(r['verdict'])} · <b>{r['p_breakouts_3m']:.0%}</b> chance to break into the "
                   f"top 500 within 3 months · {r['p_breakouts_1m']:.0%} within 1 month · {escape(r['status'])}",
                   st["body"]), Spacer(1, 4)]
    S.append(Paragraph("The numbers", st["h3"]))
    S.append(table([["Price", "Sales (30 d)", "Units", "Growth", "Commission", "Your cut", "From videos", "Age",
                     "Variants"],
                    [f"${r['unit_price']:.2f}", money(r["revenue"]), f"{r['sales_volumn']:,.0f}",
                     f"{r['revenue_growth_rate']:+,.0f}%", f"{r['commission_rate']:.0f}%",
                     f"${r['unit_price'] * r['commission_rate'] / 100:.2f}",
                     "–" if pd.isna(r["video_share"]) else f"{r['video_share']:.0%}",
                     "–" if pd.isna(r["age_days"]) else f"{r['age_days'] / 30:.0f} mo",
                     "–" if pd.isna(r["sku_count"]) else f"{r['sku_count']:.0f}"]],
                   st, [W / 9] * 9))
    S.append(Paragraph("Path so far (monthly sales; a missing month means it wasn't on our lists)", st["h3"]))
    if len(r["path"]) >= 1:
        S.append(Image(str(r["spark"]), width=W, height=W * 1.5 / 6.6))
    S.append(Paragraph(f"Breakout bar: the category's top 500 starts at {money(r['floor'])} a month; this product is at "
                       f"{r['pct_of_floor']:.0f}% of it.", st["body"]))
    S.append(Paragraph("Why the model picked it", st["h3"]))
    for f, c in r["drivers"]:
        S.append(Paragraph(f"{'+' if c >= 0 else '−'}{abs(c):.2f} · {escape(LABEL[f])}: {escape(show(f, r[f]))} "
                           f"(typical riser {escape(show(f, r['ref'][f]))})", st["body"]))
    S.append(Paragraph("Competition (last 30 days)", st["h3"]))
    cr, vn = pd.to_numeric(det.get("creator_number"), errors="coerce"), pd.to_numeric(det.get("video_number"), errors="coerce")
    spv = r["revenue"] / vn if pd.notna(vn) and vn else np.nan
    S.append(Paragraph(f"{'–' if pd.isna(cr) else f'{cr:,.0f}'} creators · {'–' if pd.isna(vn) else f'{vn:,.0f}'} videos "
                       f"· {money(spv)} sales per video · reviews {det.get('product_review_count', '–')}", st["body"]))
    vrows = [["Top videos", "Creator", "Sales", "Views", "AI", "Ad"]]
    for v in info["videos"]:
        url = f"https://www.tiktok.com/@{v.get('belonged_creator_handle')}/video/{v.get('video_id')}"
        vrows.append([link(url, clean(v.get("video_title") or "(no caption)", 60)), escape(f"@{v.get('belonged_creator_handle')}"),
                      money(pd.to_numeric(v.get("revenue"), errors="coerce")),
                      f"{pd.to_numeric(v.get('views'), errors='coerce'):,.0f}", "yes" if str(v.get("ai_video")) == "1" else "no",
                      "yes" if str(v.get("ad")) == "1" else "no"])
    if len(vrows) > 1:
        S.append(table(vrows, st, [x * inch for x in (3.2, 1.3, 0.7, 0.8, 0.45, 0.45)]))
    com = info["comments"] or {}
    S.append(Paragraph("What buyers say", st["h3"]))
    if not com:
        S.append(Paragraph("Comment analysis unavailable this week (Kalodata didn't return it).", st["body"]))
    S.append(Paragraph(f"<b>Complaints:</b> {escape(points(com.get('pain_points')))}", st["body"]))
    S.append(Paragraph(f"<b>Praise:</b> {escape(points(com.get('positive_points')))}", st["body"]))
    S.append(Paragraph(f"<b>Used for:</b> {escape(points(com.get('usage_scenarios'), 2))}", st["body"]))
    S.append(Paragraph("Fit for us", st["h3"]))
    for a, b in r["fit"]:
        S.append(Paragraph(f"<b>{escape(a)}:</b> {escape(b)}", st["body"]))
    S.append(Paragraph("Risks", st["h3"]))
    for x in r["risks"]:
        S.append(Paragraph("• " + escape(x), st["body"]))
    return [KeepTogether(S[:4])] + S[4:]


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", choices=["affiliate", "store"], default="affiliate")
    ap.add_argument("--categories", default="all", help="all, fashion, or comma-separated category IDs")
    ap.add_argument("--scan", action="store_true", help="pull fresh last-30-day lists from Kalodata first")
    ap.add_argument("--riser-pages", type=int, default=10)
    ap.add_argument("--max-credits", type=float, default=15)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--min-chance", type=float, default=0.5)
    ap.add_argument("--min-commission", type=float, default=10)
    ap.add_argument("--min-price", type=float, default=15)
    ap.add_argument("--max-price", type=float, default=60)
    ap.add_argument("--min-sales", type=float, default=3000)
    ap.add_argument("--max-per-category", type=int, default=3)
    ap.add_argument("--include-fallen", action="store_true",
                    help="also allow products that sold 1.5x more in an earlier month or were top 500 recently")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    today = dt.date.today().isoformat()
    WEEKLY.mkdir(parents=True, exist_ok=True)
    budget = k.Budget(args.max_credits)

    df, cats, _ = tp.load()
    p = tp.build(df)
    cache = train_or_load(p)
    if args.categories == "all":
        cat_ids = sorted(c for c in df["cat"].unique() if c not in SKIP_CATS)
    elif args.categories == "fashion":
        cat_ids = sorted(FASHION)
    else:
        cat_ids = args.categories.split(",")

    if args.scan:
        label = live_label(today)
        live = scan(cat_ids, budget, args.riser_pages, today)
        live["month"] = label
        extend_months(label)
        p = tp.build(pd.concat([df, live], ignore_index=True))
        window = f"Last 30 days to {today} (fresh scan)"
    else:
        label = tp.MONTHS[-1]
        window = f"{label} (latest month downloaded)"
    print(f"Scoring {window}; credits so far {budget.spent:.1f}")

    cur = p[(p["month"] == label) & (~p["in_top500"]) & (p["in_risers"] == 1) & p["cat"].isin(cat_ids)].copy()
    for name in ("breakouts_1m", "breakouts_3m"):
        cur[f"p_{name}"] = cache["models"][name].predict_proba(cur[FEATS])[:, 1]
    cur["category"] = cur["cat"].map(cats)
    floors = p[(p["month"] == label) & p["in_top500"]].groupby("cat")["revenue"].min()
    cur["floor"] = cur["cat"].map(floors)
    cur["pct_of_floor"] = cur["revenue"] / cur["floor"] * 100
    sellers = seller_names(cur["product_id"].unique().tolist())
    cur["seller_name"] = cur["product_id"].map(sellers).fillna("")
    cur["branded"] = [bool(s) and len(s) > 2 and s.split()[0].lower() in n.lower()
                      for s, n in zip(cur["seller_name"], cur["product_name"].fillna(""))]
    earlier = p[p["mi"] < tp.MI[label]]
    past_peak = earlier.groupby("product_id")["revenue"].max()
    was_top = earlier[earlier["mi"] >= tp.MI[label] - 3].groupby("product_id")["in_top500"].any()
    cur["past_peak"] = cur["product_id"].map(past_peak)
    cur["fallen"] = (cur["past_peak"] > 1.5 * cur["revenue"]) | cur["product_id"].map(was_top).fillna(False).astype(bool)
    picks_df, n_passed = pick(cur, args)
    print(f"{len(cur):,} risers scored; {n_passed} pass the filters; picking {len(picks_df)}")

    hist_path = WEEKLY / "history.csv"
    hist = pd.read_csv(hist_path, dtype={"product_id": str}) if hist_path.exists() else \
        pd.DataFrame(columns=["date", "product_id"])
    hist = hist[hist["date"] != today]  # a rerun on the same day replaces that day's picks
    picks = []
    for _, r in picks_df.iterrows():
        r = r.to_dict()
        row = picks_df[picks_df["product_id"] == r["product_id"]].head(1)
        r["drivers"] = contributions(cache["models"]["breakouts_3m"], cache["ref"], row)
        r["ref"] = cache["ref"]
        r["info"] = enrich(r["product_id"], budget, today)
        r["url"] = f"https://www.tiktok.com/view/product/{r['product_id']}?region=US"
        r["link_ok"] = link_ok(r["url"], r["product_name"])
        seen = hist[hist["product_id"] == str(r["product_id"])]
        r["status"] = f"repeat ({len(seen)}x)" if len(seen) else "new"
        r["verdict"] = ("Affiliate only (brand)" if r["branded"] else "Affiliate candidate") if args.purpose == "affiliate" \
            else "Store candidate: find an unbranded supplier"
        path_rows = p[p["product_id"] == r["product_id"]].sort_values("mi")[["month", "revenue"]]
        r["path"] = list(path_rows.itertuples(index=False, name=None))
        r["spark"] = WEEKLY / f"_spark_{r['product_id']}.png"
        sparkline(r["path"], r["spark"])
        r["fit"], r["risks"] = fit_and_risks(r, r["info"], args)
        picks.append(r)
        print(f"  {r['category']}: {clean(r['product_name'], 60)} | {r['p_breakouts_3m']:.0%} | link {'ok' if r['link_ok'] else '?'}")

    balance = (k.call("credit/balance", {}, "balance", method="GET") or {}).get("totalRemain")
    meta = {
        "title": f"Weekly Breakout Report: {today}",
        "subtitle": f"{len(picks)} products the model rates as likely to break into their category's top 500 "
                    f"within 3 months. Ember & Clove · {args.purpose} view.",
        "settings": [("Data", window), ("Purpose", args.purpose), ("Categories", args.categories),
                     ("Filters", f"chance ≥ {args.min_chance:.0%}; price ${args.min_price:.0f}–{args.max_price:.0f}; "
                                 f"sales ≥ ${args.min_sales:,.0f}/month; steady growth; "
                                 + ("" if args.include_fallen else "not past an earlier peak; ")
                                 + f"≤ {args.max_per_category} per category"
                                 + (f"; commission ≥ {args.min_commission:.0f}%" if args.purpose == "affiliate"
                                    else "; unbranded only")),
                     ("Candidates", f"{len(cur):,} rising products scored; {n_passed} passed the filters"),
                     ("Credits", f"{budget.spent:.1f} charged this run; balance {balance}")],
        "method": ["Model: 3-month breakout model (gradient-boosted trees) trained on 12 months of Kalodata data, "
                   "28 categories. Tested forward in time: its top 10% broke in at about 25% vs 5% for all risers.",
                   "Chance = estimated probability the product enters its category's top 500 by sales within 3 months.",
                   "'Why the model picked it' shows each signal's effect: the change in chance if that signal were "
                   "a typical riser's value.",
                   "Links go to the product's TikTok Shop page; 'Open (check)' means the automatic check couldn't confirm it today."],
        "limits": ["Kalodata sales are estimates; the model sees sales patterns only, not looks, quality or trends off TikTok.",
                   "One year of history: holiday seasonality isn't learned yet.",
                   "Products ranked below 200 on growth are outside the model's training range: use the score as a ranking.",
                   "Brand and season flags are keyword checks; confirm before acting.",
                   "Check back: next month's data shows which of these actually broke in."]}
    pdf = WEEKLY / f"weekly_breakouts_{today}.pdf"
    build_pdf(pdf, picks, meta, styles())
    cols = ["category", "product_id", "product_name", "unit_price", "revenue", "revenue_growth_rate", "commission_rate",
            "p_breakouts_1m", "p_breakouts_3m", "pct_of_floor", "branded", "status", "url", "link_ok"]
    pd.DataFrame(picks)[cols].to_csv(WEEKLY / f"weekly_breakouts_{today}.csv", index=False)
    new_hist = pd.DataFrame([{"date": today, "product_id": str(r["product_id"]), "product_name": r["product_name"],
                              "category": r["category"], "chance_3m": round(r["p_breakouts_3m"], 3),
                              "sales": r["revenue"], "data": window} for r in picks])
    pd.concat([hist, new_hist], ignore_index=True).to_csv(hist_path, index=False)
    for r in picks:
        r["spark"].unlink(missing_ok=True)
    print(f"Saved {pdf} ({budget.spent:.1f} credits)")


if __name__ == "__main__":
    main()
