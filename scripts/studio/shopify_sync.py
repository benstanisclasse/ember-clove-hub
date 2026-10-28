"""Shopify -> dashboard (Dashboard 2.0, Phase C). Read-only; run every 15 minutes by the dashboard server.

What it keeps in studio/analytics.db:
  store_daily          per Eastern day: orders, gross/net/total sales, discounts, returns, shipping, taxes,
                       new/returning customers (ShopifyQL `sales`), sessions and the funnel (ShopifyQL `sessions`)
  store_sources_daily  per day: sessions and funnel by referrer (kind 'referrer') and by UTM tags (kind 'utm')
  orders, order_lines  incremental by updated_at; order money, cancel/test flags, first/last visit source, UTM and
                       landing page. No customer names, emails or addresses are requested.
  products, variants   active catalog: price, unit cost, weight, inventory

What it writes for the pages (studio/dashboard/): store_daily.json (with the bot-traffic flag), store_sources.csv,
store_utm.csv (last 30 days), store_products.csv (economics + 30-day sales), store_reconciliation.json.

Definitions follow Shopify's: net_sales = gross - discounts - returns; total_sales = net + shipping + taxes (+ duties,
fees). Days are the shop's time zone (America/New_York), the dashboard's reporting zone.
Run by hand: python -I scripts/studio/shopify_sync.py
"""
import csv
import datetime as dt
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pricing_study  # noqa: E402  (CPA planning figure and the per-order 'kept' model used for prices)
import profitability_model  # noqa: E402  (EPROLO shipping and contribution before ads)
import shopify_api  # noqa: E402
from studio import analytics  # noqa: E402

DASH = analytics.DASH
HISTORY_DAYS = 90       # sales and sessions re-read each run (Shopify revises recent days: refunds, late sessions)
WINDOW_DAYS = 30        # what the pages summarise
ORDERS_FROM = "2026-10-01"  # store opened 2026-10-23; first order sync starts before that
BOT_FACTOR, BOT_MIN_SESSIONS, BOT_MAX_CART_RATE, BOT_NEIGHBOUR_DAYS = 3.0, 100, 0.01, 7

SCHEMA = """
CREATE TABLE IF NOT EXISTS store_daily (
  day TEXT PRIMARY KEY, orders REAL, gross_sales REAL, discounts REAL, returns REAL, net_sales REAL, shipping REAL,
  taxes REAL, total_sales REAL, new_customers REAL, returning_customers REAL, sessions REAL, visitors REAL,
  cart_sessions REAL, checkout_sessions REAL, completed_sessions REAL, fetched_at TEXT);
CREATE TABLE IF NOT EXISTS store_sources_daily (
  day TEXT, kind TEXT, source TEXT, medium TEXT, campaign TEXT, content TEXT, sessions REAL, cart_sessions REAL,
  checkout_sessions REAL, completed_sessions REAL, fetched_at TEXT,
  PRIMARY KEY (day, kind, source, medium, campaign, content));
CREATE TABLE IF NOT EXISTS orders (
  order_id TEXT PRIMARY KEY, name TEXT, created_at TEXT, updated_at TEXT, cancelled INTEGER, test INTEGER,
  source_name TEXT, financial_status TEXT, subtotal REAL, discounts REAL, shipping REAL, taxes REAL, refunded REAL,
  total REAL, returning_customer INTEGER, days_to_conversion INTEGER,
  first_source TEXT, first_utm_source TEXT, first_utm_medium TEXT, first_utm_campaign TEXT, first_utm_content TEXT,
  last_source TEXT, last_utm_source TEXT, last_utm_medium TEXT, last_utm_campaign TEXT, last_utm_content TEXT,
  landing_page TEXT, referrer TEXT, fetched_at TEXT);
CREATE TABLE IF NOT EXISTS order_lines (
  line_id TEXT PRIMARY KEY, order_id TEXT, product_id TEXT, variant_id TEXT, quantity REAL, unit_price REAL,
  discount REAL);
CREATE TABLE IF NOT EXISTS products (
  product_id TEXT PRIMARY KEY, title TEXT, handle TEXT, status TEXT, product_type TEXT, image TEXT,
  inventory REAL, fetched_at TEXT);
CREATE TABLE IF NOT EXISTS variants (
  variant_id TEXT PRIMARY KEY, product_id TEXT, title TEXT, price REAL, unit_cost REAL, grams REAL, inventory REAL);
"""

SALES_Q = ("FROM sales SHOW orders, gross_sales, discounts, sales_reversals, net_sales, shipping_charges, taxes, "
           "total_sales, new_customers, returning_customers TIMESERIES day SINCE {a} UNTIL {b}")
SESSIONS_Q = ("FROM sessions SHOW sessions, online_store_visitors, sessions_with_cart_additions, "
              "sessions_that_reached_checkout, sessions_that_completed_checkout TIMESERIES day SINCE {a} UNTIL {b}")
REFERRER_Q = ("FROM sessions SHOW sessions, sessions_with_cart_additions, sessions_that_reached_checkout, "
              "sessions_that_completed_checkout GROUP BY referrer_source, referrer_name TIMESERIES day SINCE {a} UNTIL {b}")
UTM_Q = ("FROM sessions SHOW sessions, sessions_with_cart_additions, sessions_that_reached_checkout, "
         "sessions_that_completed_checkout GROUP BY utm_source, utm_medium, utm_campaign, utm_content "
         "TIMESERIES day SINCE {a} UNTIL {b}")
TOTALS_Q = "FROM sales SHOW orders, net_sales, total_sales SINCE {a} UNTIL {b}"
SESSION_TOTALS_Q = "FROM sessions SHOW sessions SINCE {a} UNTIL {b}"

PRODUCTS_Q = """query($after: String) { products(first: 100, after: $after, query: "status:active") {
  pageInfo { hasNextPage endCursor }
  nodes { id title handle status productType totalInventory featuredMedia { preview { image { url } } } } } }"""
VARIANTS_Q = """query($after: String) { productVariants(first: 250, after: $after, query: "product_status:active") {
  pageInfo { hasNextPage endCursor }
  nodes { id title price inventoryQuantity product { id }
    inventoryItem { unitCost { amount } measurement { weight { value unit } } } } } }"""
VISIT = "source sourceType referrerUrl landingPage utmParameters { source medium campaign content term }"
ORDERS_Q = """query($after: String, $q: String) { orders(first: 50, after: $after, query: $q, sortKey: UPDATED_AT) {
  pageInfo { hasNextPage endCursor }
  nodes { id name createdAt updatedAt cancelledAt test sourceName displayFinancialStatus
    currentSubtotalPriceSet { shopMoney { amount } } totalDiscountsSet { shopMoney { amount } }
    totalShippingPriceSet { shopMoney { amount } } totalTaxSet { shopMoney { amount } }
    totalRefundedSet { shopMoney { amount } } currentTotalPriceSet { shopMoney { amount } }
    customer { numberOfOrders }
    customerJourneySummary { daysToConversion firstVisit { %s } lastVisit { %s } }
    lineItems(first: 100) { nodes { id quantity product { id } variant { id }
      originalUnitPriceSet { shopMoney { amount } } totalDiscountSet { shopMoney { amount } } } } } } }""" % (VISIT, VISIT)
ORDERS_COUNT_Q = """query($q: String) { ordersCount(query: $q, limit: null) { count precision } }"""


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def money(node, key):
    return num((((node or {}).get(key) or {}).get("shopMoney") or {}).get("amount"))


def grams(weight):
    w = weight or {}
    return num(w.get("value")) * {"GRAMS": 1, "KILOGRAMS": 1000, "POUNDS": 453.6, "OUNCES": 28.35}.get(w.get("unit"), 1)


def paged(query, key, variables=None):
    after = None
    while True:
        data = shopify_api.graphql(query, {**(variables or {}), "after": after})[key]
        yield from data["nodes"]
        if not data["pageInfo"]["hasNextPage"]:
            return
        after = data["pageInfo"]["endCursor"]


# --- pure helpers (tested) ------------------------------------------------------------------------------------

def flag_bot_days(days):
    """Mark days whose sessions look non-human: at least BOT_MIN_SESSIONS, >= BOT_FACTOR x the median of the other
    days with traffic within +-BOT_NEIGHBOUR_DAYS, and almost no cart activity (< BOT_MAX_CART_RATE). Needs at least
    two such neighbour days. Raw numbers are kept; the flag only lets KPIs exclude the day. days: list of dicts."""
    by_day = {d["day"]: d for d in days}
    for d in days:
        d["bot_flag"], d["bot_reason"] = 0, ""
        s = num(d.get("sessions"))
        if s < BOT_MIN_SESSIONS:
            continue
        day = dt.date.fromisoformat(d["day"])
        near = [num(by_day[k]["sessions"]) for k in by_day if k != d["day"]
                and abs((dt.date.fromisoformat(k) - day).days) <= BOT_NEIGHBOUR_DAYS and num(by_day[k]["sessions"]) > 0]
        if len(near) < 2:
            continue
        med = statistics.median(near)
        cart_rate = num(d.get("cart_sessions")) / s
        if s >= BOT_FACTOR * med and cart_rate < BOT_MAX_CART_RATE:
            d["bot_flag"] = 1
            d["bot_reason"] = (f"{int(s):,} sessions = {s / med:.1f}x the nearby median ({med:,.0f}), "
                               f"cart rate {cart_rate:.1%}")
    return days


def product_economics(title, variants, cpa=None):
    """Per-order economics for a product, on the same basis as the 2026-10-26 pricing study: costed on the variant
    that is most expensive to source (highest unit cost, then heaviest), priced at the median variant price
    (the lower middle one when there is an even number, so it is a price a customer actually pays)."""
    cpa = pricing_study.CPA if cpa is None else cpa
    priced = [v for v in variants if v.get("price")]
    costed = [v for v in priced if v.get("unit_cost")]
    if not priced:
        return {"econ_status": "No price"}
    price = statistics.median_low(v["price"] for v in priced)  # a real variant price, never an average of two
    if not costed:
        return {"price": price, "econ_status": "No unit cost on record"}
    worst = max(costed, key=lambda v: (v["unit_cost"], v.get("grams") or 0))
    ship = profitability_model.ship(title, worst.get("grams") or 0)
    contrib = profitability_model.contribution(title, price, worst["unit_cost"], worst.get("grams") or 0)
    revenue = profitability_model.revenue(price)
    return {"price": round(price, 2), "unit_cost": round(worst["unit_cost"], 2), "supplier_shipping": round(ship, 2),
            "contribution": round(contrib, 2), "margin_pct": round(contrib / revenue, 4) if revenue else None,
            "breakeven_cpa": round(contrib, 2), "breakeven_roas": round(revenue / contrib, 2) if contrib > 0 else None,
            "kept_after_cpa": round(contrib - cpa, 2), "cpa_assumed": cpa, "econ_status": "Estimate"}


def reconcile(daily_rows, totals, session_total, orders_synced, orders_count):
    """Compare what the dashboard stored with Shopify's own totals for the same days."""
    checks = []

    def add(name, ours, theirs, tol=0.005):
        ok = abs(ours - theirs) <= tol
        checks.append({"check": name, "dashboard": round(ours, 2), "shopify": round(theirs, 2), "ok": ok})

    add("Orders (sales report)", sum(num(r["orders"]) for r in daily_rows), num(totals.get("orders")))
    add("Net sales", sum(num(r["net_sales"]) for r in daily_rows), num(totals.get("net_sales")))
    add("Total sales", sum(num(r["total_sales"]) for r in daily_rows), num(totals.get("total_sales")))
    add("Sessions", sum(num(r["sessions"]) for r in daily_rows), num(session_total))
    add("Orders stored vs order count", orders_synced, orders_count)
    return {"ok": all(c["ok"] for c in checks), "checks": checks}


# --- sync ------------------------------------------------------------------------------------------------------

def _window(days):
    today = dt.date.fromisoformat(analytics.local_day(analytics.now_utc()))
    return (today - dt.timedelta(days=days - 1)).isoformat(), today.isoformat()


def sync_store(con, fetched_at):
    a, b = _window(HISTORY_DAYS)
    _, sales = shopify_api.shopifyql(SALES_Q.format(a=a, b=b))
    _, sess = shopify_api.shopifyql(SESSIONS_Q.format(a=a, b=b))
    s_by = {r["day"]: r for r in sess}
    for r in sales:
        s = s_by.get(r["day"], {})
        con.execute("INSERT OR REPLACE INTO store_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            r["day"], num(r["orders"]), num(r["gross_sales"]), num(r["discounts"]), num(r["sales_reversals"]),
            num(r["net_sales"]), num(r["shipping_charges"]), num(r["taxes"]), num(r["total_sales"]),
            num(r["new_customers"]), num(r["returning_customers"]), num(s.get("sessions")),
            num(s.get("online_store_visitors")), num(s.get("sessions_with_cart_additions")),
            num(s.get("sessions_that_reached_checkout")), num(s.get("sessions_that_completed_checkout")), fetched_at))
    n = len(sales)
    con.execute("DELETE FROM store_sources_daily WHERE day >= ?", (a,))  # re-read window replaces itself
    for kind, q, keys in (("referrer", REFERRER_Q, ("referrer_source", None, "referrer_name", None)),
                          ("utm", UTM_Q, ("utm_source", "utm_medium", "utm_campaign", "utm_content"))):
        _, rows = shopify_api.shopifyql(q.format(a=a, b=b))
        for r in rows:
            if not num(r.get("sessions")):
                continue
            src, med, camp, cont = [(r.get(k) or "") if k else "" for k in keys]
            con.execute("INSERT OR REPLACE INTO store_sources_daily VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                r["day"], kind, src, med, camp, cont, num(r["sessions"]), num(r.get("sessions_with_cart_additions")),
                num(r.get("sessions_that_reached_checkout")), num(r.get("sessions_that_completed_checkout")),
                fetched_at))
            n += 1
    return n


def sync_orders(con, fetched_at):
    last = con.execute("SELECT MAX(updated_at) FROM orders").fetchone()[0]
    since = (dt.datetime.fromisoformat(last.replace("Z", "+00:00")) - dt.timedelta(days=1)).date().isoformat() \
        if last else ORDERS_FROM
    n = 0
    for o in paged(ORDERS_Q, "orders", {"q": f"updated_at:>={since}"}):
        j = o.get("customerJourneySummary") or {}
        fv, lv = j.get("firstVisit") or {}, j.get("lastVisit") or {}
        fu, lu = fv.get("utmParameters") or {}, lv.get("utmParameters") or {}
        con.execute("INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            o["id"], o["name"], o["createdAt"], o["updatedAt"], int(bool(o.get("cancelledAt"))), int(bool(o.get("test"))),
            o.get("sourceName") or "", o.get("displayFinancialStatus") or "", money(o, "currentSubtotalPriceSet"),
            money(o, "totalDiscountsSet"), money(o, "totalShippingPriceSet"), money(o, "totalTaxSet"),
            money(o, "totalRefundedSet"), money(o, "currentTotalPriceSet"),
            int(((o.get("customer") or {}).get("numberOfOrders") or 0) > 1), j.get("daysToConversion"),
            fv.get("source") or "", fu.get("source") or "", fu.get("medium") or "", fu.get("campaign") or "",
            fu.get("content") or "", lv.get("source") or "", lu.get("source") or "", lu.get("medium") or "",
            lu.get("campaign") or "", lu.get("content") or "", lv.get("landingPage") or fv.get("landingPage") or "",
            lv.get("referrerUrl") or fv.get("referrerUrl") or "", fetched_at))
        con.execute("DELETE FROM order_lines WHERE order_id = ?", (o["id"],))
        for li in o["lineItems"]["nodes"]:
            con.execute("INSERT OR REPLACE INTO order_lines VALUES (?,?,?,?,?,?,?)", (
                li["id"], o["id"], (li.get("product") or {}).get("id") or "", (li.get("variant") or {}).get("id") or "",
                num(li.get("quantity")), money(li, "originalUnitPriceSet"), money(li, "totalDiscountSet")))
        n += 1
    return n


def sync_catalog(con, fetched_at):
    con.execute("DELETE FROM products")
    con.execute("DELETE FROM variants")
    n = 0
    for p in paged(PRODUCTS_Q, "products"):
        img = (((p.get("featuredMedia") or {}).get("preview") or {}).get("image") or {}).get("url") or ""
        con.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", (
            p["id"], p["title"], p["handle"], p["status"], p.get("productType") or "", img, num(p.get("totalInventory")),
            fetched_at))
        n += 1
    for v in paged(VARIANTS_Q, "productVariants"):
        item = v.get("inventoryItem") or {}
        cost = (item.get("unitCost") or {}).get("amount")
        con.execute("INSERT INTO variants VALUES (?,?,?,?,?,?,?)", (
            v["id"], v["product"]["id"], v["title"], num(v.get("price")) or None, num(cost) if cost else None,
            grams((item.get("measurement") or {}).get("weight")) or None, num(v.get("inventoryQuantity"))))
        n += 1
    return n


def write_dashboard_files(con, out=DASH):
    a, b = _window(WINDOW_DAYS)
    rows = [dict(r) for r in con.execute("SELECT * FROM store_daily WHERE day >= ? ORDER BY day", (a,))]
    flag_bot_days(rows)
    (out / "store_daily.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")

    def write_csv(name, cols, data):
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)

    agg = """SELECT source, medium, campaign, content, SUM(sessions) sessions, SUM(cart_sessions) cart_sessions,
             SUM(checkout_sessions) checkout_sessions, SUM(completed_sessions) completed_sessions
             FROM store_sources_daily WHERE kind = ? AND day >= ? GROUP BY source, medium, campaign, content
             ORDER BY sessions DESC"""
    cols = ["source", "medium", "campaign", "content", "sessions", "cart_sessions", "checkout_sessions",
            "completed_sessions"]
    write_csv("store_sources", cols, [dict(r) for r in con.execute(agg, ("referrer", a))])
    write_csv("store_utm", cols, [dict(r) for r in con.execute(agg, ("utm", a))])

    sold = {r["product_id"]: dict(r) for r in con.execute(
        """SELECT l.product_id, SUM(l.quantity) units, SUM(l.quantity * l.unit_price - l.discount) net_sales,
                  COUNT(DISTINCT o.order_id) orders
           FROM order_lines l JOIN orders o ON o.order_id = l.order_id
           WHERE o.cancelled = 0 AND o.test = 0 AND substr(o.created_at, 1, 10) >= ? GROUP BY l.product_id""", (a,))}
    variants = {}
    for v in con.execute("SELECT * FROM variants"):
        variants.setdefault(v["product_id"], []).append(dict(v))
    prods = []
    for p in con.execute("SELECT * FROM products ORDER BY title"):
        s = sold.get(p["product_id"], {})
        prods.append({"product_id": p["product_id"].rsplit("/", 1)[-1], "title": p["title"], "handle": p["handle"],
                      "type": p["product_type"], "image": p["image"], "inventory": p["inventory"],
                      "variants": len(variants.get(p["product_id"], [])),
                      **product_economics(p["title"], variants.get(p["product_id"], [])),
                      "units_30d": s.get("units") or 0, "orders_30d": s.get("orders") or 0,
                      "net_sales_30d": round(s.get("net_sales") or 0, 2)})
    write_csv("store_products", ["product_id", "title", "handle", "type", "image", "inventory", "variants", "price",
                                 "unit_cost", "supplier_shipping", "contribution", "margin_pct", "breakeven_cpa",
                                 "breakeven_roas", "kept_after_cpa", "cpa_assumed", "econ_status", "units_30d",
                                 "orders_30d", "net_sales_30d"], prods)
    return a, b, rows, len(prods)


def run_reconciliation(con, a, b, rows, out=DASH):
    _, t = shopify_api.shopifyql(TOTALS_Q.format(a=a, b=b))
    _, st = shopify_api.shopifyql(SESSION_TOTALS_Q.format(a=a, b=b))
    lo, hi = analytics.day_bounds_utc(a)[0], analytics.day_bounds_utc(b)[1]
    q = f"created_at:>='{lo.strftime('%Y-%m-%dT%H:%M:%SZ')}' AND created_at:<'{hi.strftime('%Y-%m-%dT%H:%M:%SZ')}'"
    count = shopify_api.graphql(ORDERS_COUNT_Q, {"q": q})["ordersCount"]["count"]
    stored = con.execute("SELECT COUNT(*) FROM orders WHERE created_at >= ? AND created_at < ?",
                         (lo.strftime("%Y-%m-%dT%H:%M:%SZ"), hi.strftime("%Y-%m-%dT%H:%M:%SZ"))).fetchone()[0]
    rec = {**reconcile(rows, (t or [{}])[0], (st or [{}])[0].get("sessions"), stored, count),
           "from": a, "to": b, "checked_at": analytics.now_utc()}
    (out / "store_reconciliation.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return rec


def sync(out=DASH, db_path=None):
    fetched_at = analytics.now_utc()
    con = analytics.connect(db_path)
    con.executescript(SCHEMA)
    try:
        n_store = sync_store(con, fetched_at)
        n_orders = sync_orders(con, fetched_at)
        n_catalog = sync_catalog(con, fetched_at)
        con.commit()
        a, b, rows, n_prod = write_dashboard_files(con, out)
        rec = run_reconciliation(con, a, b, rows, out)
    finally:
        con.close()
    flagged = sum(r["bot_flag"] for r in rows)
    return [f"store days/sources {n_store}", f"orders {n_orders}", f"products+variants {n_catalog}",
            f"products priced {n_prod}", f"bot-flagged days {flagged}",
            f"reconciliation {'OK' if rec['ok'] else 'MISMATCH'}"]


if __name__ == "__main__":
    for line in sync():
        print(" ", line)
