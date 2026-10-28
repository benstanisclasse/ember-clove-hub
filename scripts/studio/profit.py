"""Marketing profitability (Dashboard 2.0, Phase F). Run at the end of every Shopify sync; read-only.

Per order, from Shopify orders + variant unit costs (all ESTIMATES, labelled as such on the pages):
  revenue        merchandise after discounts (current subtotal) + shipping charged, minus refunds already made
  cogs           sum of quantity x the variant's unit cost (Shopify "cost per item", from EPROLO)
  supplier ship  EPROLO shipping per unit (profitability_model.ship: real quotes where known, else the YANWEN fit);
                 per unit, so multi-item orders are costed on the safe side
  fees           2.9% + $0.30 of what the customer paid before tax (config economics)
  refund allow.  5% of merchandise for orders with no refund yet and younger than 30 days (config economics)
  contribution   revenue - cogs - supplier ship - fees - refund allowance   (before ads)
Per day: contribution - ad spend (all platforms) - content generation cost = profit after marketing.
Break-even ROAS = revenue / contribution; allowable cost per order = contribution - target profit per order.
With no orders yet, the same figures are shown from the catalog (store_products: one item per order), clearly marked.

Content cost ledger (analytics.db generation_costs): Ember Studio spend (studio.db, exact) + data/costs/generation_costs.csv
for any other real dollar charge (provider, kind, date, usd, note). Credits-only tools are not converted to dollars.

Budgets (config/hub.json "budgets"): display and alerts only. Nothing here changes a campaign or a budget.
"""
import csv
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hub_env  # noqa: E402
import profitability_model  # noqa: E402
from studio import analytics  # noqa: E402

HUB = analytics.HUB
MANUAL_COSTS = HUB / "data" / "costs" / "generation_costs.csv"
COST_COLS = ["date", "provider", "kind", "usd", "note"]
DEFAULT_BUDGETS = {"target_cpa": 20.0, "target_profit_per_order": 10.0, "daily_ad_budget": None, "weekly_ad_budget": None,
                   "monthly_ad_budget": None, "per_platform_daily": {}}

SCHEMA = """
CREATE TABLE IF NOT EXISTS generation_costs (
  source TEXT NOT NULL, ref TEXT NOT NULL, day TEXT, provider TEXT, kind TEXT, model TEXT, usd REAL, note TEXT,
  PRIMARY KEY (source, ref));
"""


def _econ():
    e = hub_env.load_config().get("economics", {})
    return float(e.get("payment_fee_pct", 0.029)), float(e.get("payment_fee_fixed", 0.30)), float(e.get("refund_rate", 0.05))


def budgets():
    b = {**DEFAULT_BUDGETS, **(hub_env.load_config().get("budgets") or {})}
    b.pop("_note", None)
    return b


def order_economics(o, lines, variants, titles, today=None, econ=None):
    """o: order row (dict); lines: its order_lines; variants: variant_id -> {unit_cost, grams, product_id};
    titles: product_id -> title. Returns a dict; cost_complete is False when any line lacks a unit cost."""
    fee_pct, fee_fixed, refund_rate = econ or _econ()
    today = today or dt.date.fromisoformat(analytics.local_day(analytics.now_utc()))
    merch, ship_charged, refunded = float(o.get("subtotal") or 0), float(o.get("shipping") or 0), float(o.get("refunded") or 0)
    cogs = supplier = 0.0
    complete = True
    for li in lines:
        v = variants.get(li["variant_id"]) or {}
        qty = float(li.get("quantity") or 0)
        if v.get("unit_cost") is None:
            complete = False
        cogs += qty * float(v.get("unit_cost") or 0)
        supplier += qty * profitability_model.ship(titles.get(v.get("product_id") or li.get("product_id"), ""),
                                                   float(v.get("grams") or 0))
    revenue = merch + ship_charged - refunded
    fees = (merch + ship_charged) * fee_pct + fee_fixed if merch + ship_charged > 0 else 0.0
    age = (today - dt.date.fromisoformat(analytics.local_day(o["created_at"]))).days
    allowance = merch * refund_rate if refunded == 0 and age < 30 else 0.0
    contrib = revenue - cogs - supplier - fees - allowance
    return {"order_id": o["order_id"], "day": analytics.local_day(o["created_at"]), "revenue": round(revenue, 2),
            "cogs": round(cogs, 2), "supplier_shipping": round(supplier, 2), "fees": round(fees, 2),
            "refund_allowance": round(allowance, 2), "refunded": round(refunded, 2), "contribution": round(contrib, 2),
            "margin": round(contrib / revenue, 4) if revenue > 0 else None, "cost_complete": complete}


def import_generation_costs(con, studio_db=HUB / "studio" / "studio.db", manual=MANUAL_COSTS):
    """Refresh the ledger: Ember Studio spend rows (exact) + the manual CSV. Returns rows in the ledger."""
    con.executescript(SCHEMA)
    con.execute("DELETE FROM generation_costs")
    if Path(studio_db).exists():
        s = sqlite3.connect(studio_db)
        for sid, ep, usd, at, model in s.execute(  # zero-cost rows are refused jobs, not spend
                "SELECT s.id, s.episode_id, s.usd, s.at, e.model FROM spend s LEFT JOIN episodes e ON e.id = s.episode_id "
                "WHERE s.usd > 0"):
            provider = "Higgsfield" if (model or "").startswith("higgsfield") else "OpenRouter" if model else "unknown"
            con.execute("INSERT INTO generation_costs VALUES (?,?,?,?,?,?,?,?)",
                        ("studio", str(sid), (at or "")[:10], provider, "video", model or "", float(usd or 0), ep or ""))
        s.close()
    if Path(manual).exists():
        with open(manual, newline="", encoding="utf-8") as f:
            for i, r in enumerate(csv.DictReader(f)):
                if not r.get("date") or not r.get("usd"):
                    continue
                dt.date.fromisoformat(r["date"])
                con.execute("INSERT INTO generation_costs VALUES (?,?,?,?,?,?,?,?)",
                            ("manual", str(i), r["date"], r.get("provider") or "", r.get("kind") or "", "",
                             float(r["usd"]), r.get("note") or ""))
    con.commit()
    return con.execute("SELECT COUNT(*) FROM generation_costs").fetchone()[0]


def _ad_spend_by_day(ads_csv):
    out = {}
    if Path(ads_csv).exists():
        with open(ads_csv, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                out[r["date"]] = out.get(r["date"], 0.0) + float(r.get("spend") or 0)
    return out


def catalog_economics(products_csv):
    """No-orders fallback: average single-item economics across the active catalog (store_products.csv)."""
    rows = []
    if Path(products_csv).exists():
        with open(products_csv, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r.get("econ_status") == "Estimate"]
    if not rows:
        return None
    n = len(rows)
    avg = lambda k: sum(float(r[k]) for r in rows) / n  # noqa: E731
    rev = sum(profitability_model.revenue(float(r["price"])) for r in rows) / n
    c = avg("contribution")
    return {"products": n, "avg_price": round(avg("price"), 2), "avg_revenue": round(rev, 2), "avg_contribution": round(c, 2),
            "margin": round(c / rev, 4), "breakeven_roas": round(rev / c, 2) if c > 0 else None,
            "losing_at_target_cpa": sum(1 for r in rows if float(r["kept_after_cpa"]) < 0)}


def report(con, out=analytics.DASH, days=90, today=None):
    """Write profit_daily.json, profit_products.json, profit_summary.json and cost_ledger.json for the pages."""
    con.executescript(SCHEMA)
    today = today or dt.date.fromisoformat(analytics.local_day(analytics.now_utc()))
    start = (today - dt.timedelta(days=days - 1)).isoformat()
    variants = {r["variant_id"]: dict(r) for r in con.execute("SELECT * FROM variants")}
    titles = {r["product_id"]: r["title"] for r in con.execute("SELECT product_id, title FROM products")}
    orders = [dict(r) for r in con.execute(
        "SELECT * FROM orders WHERE cancelled = 0 AND test = 0 AND substr(created_at, 1, 10) >= ?",
        ((today - dt.timedelta(days=days + 1)).isoformat(),))]
    lines = {}
    for li in con.execute("SELECT * FROM order_lines"):
        lines.setdefault(li["order_id"], []).append(dict(li))
    econ = _econ()
    per_order = [order_economics(o, lines.get(o["order_id"], []), variants, titles, today, econ) for o in orders]
    per_order = [e for e in per_order if e["day"] >= start]

    ads = _ad_spend_by_day(out / "ads_daily.csv")
    gen = {}
    for d, usd in con.execute("SELECT day, SUM(usd) FROM generation_costs GROUP BY day"):
        gen[d] = usd or 0.0
    daily = []
    for i in range(days):
        d = (today - dt.timedelta(days=days - 1 - i)).isoformat()
        os_ = [e for e in per_order if e["day"] == d]
        contrib = sum(e["contribution"] for e in os_)
        spend, content = ads.get(d, 0.0), gen.get(d, 0.0)
        daily.append({"date": d, "orders": len(os_), "revenue": round(sum(e["revenue"] for e in os_), 2),
                      "cogs": round(sum(e["cogs"] + e["supplier_shipping"] for e in os_), 2),
                      "fees_refunds": round(sum(e["fees"] + e["refund_allowance"] for e in os_), 2),
                      "contribution": round(contrib, 2), "ad_spend": round(spend, 2), "content_cost": round(content, 2),
                      "profit_after_marketing": round(contrib - spend - content, 2),
                      "cost_complete": all(e["cost_complete"] for e in os_)})
    (out / "profit_daily.json").write_text(json.dumps(daily, indent=1), encoding="utf-8")

    prod = {}
    for o in per_order:
        for li in lines.get(o["order_id"], []):
            v = variants.get(li["variant_id"]) or {}
            pid = v.get("product_id") or li["product_id"]
            share = (li["quantity"] * li["unit_price"] - li["discount"])
            p = prod.setdefault(pid, {"product_id": pid.rsplit("/", 1)[-1], "title": titles.get(pid, "(removed product)"),
                                      "units": 0, "net_sales": 0.0, "cogs": 0.0})
            p["units"] += li["quantity"]
            p["net_sales"] = round(p["net_sales"] + share, 2)
            p["cogs"] = round(p["cogs"] + li["quantity"] * float(v.get("unit_cost") or 0), 2)
    (out / "profit_products.json").write_text(json.dumps(sorted(prod.values(), key=lambda r: -r["net_sales"]), indent=1),
                                              encoding="utf-8")

    b = budgets()
    n = len(per_order)
    rev = sum(e["revenue"] for e in per_order)
    contrib = sum(e["contribution"] for e in per_order)
    cat = catalog_economics(out / "store_products.csv")
    summary = {"orders": n, "revenue": round(rev, 2), "contribution": round(contrib, 2),
               "margin": round(contrib / rev, 4) if rev else None,
               "breakeven_roas": round(rev / contrib, 2) if contrib > 0 else None,
               "avg_contribution_per_order": round(contrib / n, 2) if n else None,
               "allowable_cpa": round(contrib / n - b["target_profit_per_order"], 2) if n else None,
               "basis": "orders" if n else "catalog", "catalog": cat, "budgets": b,
               "committed_daily_budgets": _committed_budgets(out / "ads_entities.json"),
               "cost_complete": all(e["cost_complete"] for e in per_order), "window_days": days, "to": today.isoformat()}
    if not n and cat:
        summary["allowable_cpa_catalog"] = round(cat["avg_contribution"] - b["target_profit_per_order"], 2)
    (out / "profit_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    ledger = [dict(r) for r in con.execute(
        "SELECT day, provider, kind, ROUND(SUM(usd), 2) AS usd, COUNT(*) AS items FROM generation_costs "
        "GROUP BY day, provider, kind ORDER BY day")]
    (out / "cost_ledger.json").write_text(json.dumps(ledger, indent=1), encoding="utf-8")
    return [f"orders costed {n}", f"profit days {len(daily)}", f"products sold {len(prod)}", f"ledger rows {len(ledger)}"]


def _committed_budgets(entities_json):
    if not Path(entities_json).exists():
        return []
    ents = json.loads(Path(entities_json).read_text(encoding="utf-8"))
    return [{"platform": e["platform"], "campaign": e["name"], "daily_budget": e.get("daily_budget")}
            for e in ents if e.get("level") == "campaign" and e.get("daily_budget") and str(e.get("status", "")).lower().startswith("active")]


def run(out=analytics.DASH, db_path=None):
    con = analytics.connect(db_path)
    try:
        import_generation_costs(con)
        return report(con, out)
    finally:
        con.close()


if __name__ == "__main__":
    for line in run():
        print(" ", line)
