"""Tests for the profitability engine (Dashboard 2.0, Phase F). Temporary databases and folders only.

Run: python -m pytest -q scripts/studio/test_profit.py
"""
import csv
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import profitability_model  # noqa: E402
from studio import analytics, profit, shopify_sync  # noqa: E402

ECON = (0.029, 0.30, 0.05)
TODAY = dt.date(2026, 11, 20)


def order(**k):  # standard shipping is free since 2026-10-29; express ($5) is passed explicitly
    return {"order_id": "o1", "created_at": "2026-11-18T15:00:00Z", "subtotal": 45.0, "shipping": 0.0, "refunded": 0.0, **k}


VARIANTS = {"v1": {"unit_cost": 14.0, "grams": 400, "product_id": "p1"}, "v2": {"unit_cost": None, "grams": 100, "product_id": "p2"}}
TITLES = {"p1": "Test Dress", "p2": "Test Necklace"}


def test_single_item_order_matches_the_profitability_model():
    e = profit.order_economics(order(), [{"variant_id": "v1", "product_id": "p1", "quantity": 1}], VARIANTS, TITLES, TODAY, ECON)
    expect = profitability_model.contribution("Test Dress", 45.0, 14.0, 400)  # same formula the prices were set with
    assert e["contribution"] == round(expect, 2)
    assert e["revenue"] == 45.0 and e["fees"] == round(45 * 0.029 + 0.30, 2) and e["refund_allowance"] == 2.25
    express = profit.order_economics(order(shipping=5.0), [{"variant_id": "v1", "product_id": "p1", "quantity": 1}], VARIANTS, TITLES, TODAY, ECON)
    assert express["revenue"] == 50.0 and express["fees"] == round(50 * 0.029 + 0.30, 2)  # express fee counts as revenue
    assert e["cost_complete"] is True and e["day"] == "2026-11-18"


def test_multi_item_orders_refunds_and_old_orders():
    lines = [{"variant_id": "v1", "product_id": "p1", "quantity": 2}]
    e = profit.order_economics(order(subtotal=90.0, shipping=0.0), lines, VARIANTS, TITLES, TODAY, ECON)
    assert e["cogs"] == 28.0 and e["supplier_shipping"] == round(2 * profitability_model.ship("Test Dress", 400), 2)
    refunded = profit.order_economics(order(refunded=45.0), lines[:1], VARIANTS, TITLES, TODAY, ECON)
    assert refunded["refund_allowance"] == 0 and refunded["revenue"] == 0.0  # actual refund replaces the allowance
    old = profit.order_economics(order(created_at="2026-09-01T15:00:00Z"), lines, VARIANTS, TITLES, TODAY, ECON)
    assert old["refund_allowance"] == 0  # past the 30-day return window


def test_missing_unit_cost_is_flagged_not_hidden():
    e = profit.order_economics(order(), [{"variant_id": "v2", "product_id": "p2", "quantity": 1}], VARIANTS, TITLES, TODAY, ECON)
    assert e["cost_complete"] is False


def test_evening_order_belongs_to_the_eastern_day():
    e = profit.order_economics(order(created_at="2026-11-19T03:30:00Z"), [], VARIANTS, TITLES, TODAY, ECON)
    assert e["day"] == "2026-11-18"  # 10:30 pm Eastern


def test_ledger_imports_studio_spend_and_manual_rows(tmp_path):
    studio = tmp_path / "studio.db"
    s = sqlite3.connect(studio)
    s.executescript("CREATE TABLE episodes (id TEXT, model TEXT); CREATE TABLE spend (id INTEGER, episode_id TEXT, usd REAL, at TEXT);"
                    "INSERT INTO episodes VALUES ('e1','higgsfield:x'),('e2','bytedance/seedance-2.5');"
                    "INSERT INTO spend VALUES (1,'e1',4.2,'2026-10-26T20:00:00'),(2,'e2',1.44,'2026-10-26T18:00:00'),(3,'e2',0,'2026-10-26');")
    s.commit()
    s.close()
    manual = tmp_path / "costs.csv"
    manual.write_text("date,provider,kind,usd,note\n2026-10-27,Higgsfield,image,1.10,gallery photos\n,,,,\n", encoding="utf-8")
    con = analytics.connect(tmp_path / "a.db")
    assert profit.import_generation_costs(con, studio, manual) == 3  # zero-cost row skipped, blank row ignored
    got = {(r[0], r[1]): r[2] for r in con.execute("SELECT provider, kind, SUM(usd) FROM generation_costs GROUP BY 1, 2")}
    assert got == {("Higgsfield", "video"): 4.2, ("OpenRouter", "video"): 1.44, ("Higgsfield", "image"): 1.1}


def test_report_profit_after_marketing(tmp_path, monkeypatch):
    con = analytics.connect(tmp_path / "a.db")
    con.executescript(shopify_sync.SCHEMA)
    con.execute("INSERT INTO products (product_id, title) VALUES ('p1', 'Test Dress')")
    con.execute("INSERT INTO variants (variant_id, product_id, unit_cost, grams) VALUES ('v1', 'p1', 14.0, 400)")
    con.execute("INSERT INTO orders (order_id, created_at, cancelled, test, subtotal, shipping, refunded) "
                "VALUES ('o1', '2026-11-18T15:00:00Z', 0, 0, 45, 0, 0), ('o2', '2026-11-18T16:00:00Z', 1, 0, 99, 0, 0)")
    con.execute("INSERT INTO order_lines (line_id, order_id, product_id, variant_id, quantity, unit_price, discount) "
                "VALUES ('l1', 'o1', 'p1', 'v1', 1, 45, 0)")
    con.executescript(profit.SCHEMA)
    con.execute("INSERT INTO generation_costs VALUES ('studio','1','2026-11-18','OpenRouter','video','',1.44,'')")
    con.commit()
    (tmp_path / "ads_daily.csv").write_text("date,platform,spend,impressions,clicks,purchases,revenue\n"
                                            "2026-11-18,meta,10,0,0,0,0\n2026-11-18,tiktok,5,0,0,0,0\n", encoding="utf-8")
    monkeypatch.setattr(profit, "_econ", lambda: ECON)
    monkeypatch.setattr(profit, "budgets", lambda: dict(profit.DEFAULT_BUDGETS))
    profit.report(con, tmp_path, days=7, today=TODAY)
    day = {r["date"]: r for r in json.loads((tmp_path / "profit_daily.json").read_text(encoding="utf-8"))}["2026-11-18"]
    c = round(profitability_model.contribution("Test Dress", 45.0, 14.0, 400), 2)
    assert day["orders"] == 1 and day["contribution"] == c  # the cancelled order is left out
    assert day["profit_after_marketing"] == round(c - 15 - 1.44, 2)
    s = json.loads((tmp_path / "profit_summary.json").read_text(encoding="utf-8"))
    assert s["basis"] == "orders" and s["allowable_cpa"] == round(c - 10, 2)
    assert s["breakeven_roas"] == round(45 / c, 2)
    assert json.loads((tmp_path / "profit_products.json").read_text(encoding="utf-8"))[0]["units"] == 1


def test_catalog_fallback_when_no_orders(tmp_path):
    p = tmp_path / "store_products.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["price", "contribution", "kept_after_cpa", "econ_status"])
        w.writeheader()
        w.writerows([{"price": 40, "contribution": 20, "kept_after_cpa": 0, "econ_status": "Estimate"},
                     {"price": 60, "contribution": 30, "kept_after_cpa": -1, "econ_status": "Estimate"},
                     {"price": 10, "contribution": "", "kept_after_cpa": "", "econ_status": "No unit cost on record"}])
    cat = profit.catalog_economics(p)
    assert cat["products"] == 2 and cat["avg_contribution"] == 25.0 and cat["losing_at_target_cpa"] == 1
    assert profit.catalog_economics(tmp_path / "missing.csv") is None
