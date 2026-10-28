"""Tests for the market engine Phase B pieces: point-in-time builder, evaluation harness, decision rule, v1 pin and
the weekly research shortlist. Everything runs on a small synthetic database in pytest's tmp_path; nothing reads the
real kalodata.db and no network call is made.
Run: python -m pytest -q scripts/test_market.py
"""
import json
import socket
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kalodata_db  # noqa: E402
import market_data as md  # noqa: E402
import market_eval as me  # noqa: E402

CATS = {"100": "Alpha", "200": "Beta", "601303": "Muslim Fashion", "834312": "Virtual Products"}
MONTHS = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*a, **k):
        raise RuntimeError("network call attempted in a test")
    monkeypatch.setattr(socket.socket, "connect", refuse)


# ---------------------------------------------------------------- synthetic database
def make_db(path, months=MONTHS, deep_month=None, extra=True, seed=1):
    """Monthly top-500 (5 pages) and riser-200 (2 pages) lists for categories 100, 200 and 601303 (thin), plus
    Virtual Products pulls and assorted off-spec pulls."""
    rng = np.random.default_rng(seed)
    old = kalodata_db.DB
    kalodata_db.DB = Path(path)
    con = kalodata_db.connect()
    kalodata_db.DB = old
    pid = [0]

    def pull(name, kind, month, cat, page, filters, n, collected="2026-10-25T20:00:00", success=1):
        pid[0] += 1
        con.execute("INSERT INTO pulls (pull_id, file, pulled_on, name, endpoint, date_range, filters, success, "
                    "n_records, sha256, collected_at, kind, month, category_id, page) VALUES "
                    "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (pid[0], f"raw/core/{name}_{pid[0]}.json", "core", name, "tiktok/product/rank", month or "last30Day",
                     json.dumps(filters), success, n, f"sha{pid[0]}", collected, kind, month, cat, page))
        return pid[0]

    def spec(sort, page, cat, size=100, **kw):
        return dict({"sort_field": {"field": sort, "type": "DESC"}, "page_size": size, "page_number": page,
                     "category_ids": [cat], "need_extra": True}, **kw)

    def put(pull_id, rows):
        con.executemany("INSERT INTO products (pull_id, position, product_id, product_name, revenue, sales_volumn, "
                        "unit_price, revenue_growth_rate, commission_rate, live_revenue, video_revenue, "
                        "showcase_revenue, launch_date, seller_id, seller_name, sku_count, raw_json) VALUES "
                        "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        [(pull_id, i + 1, *r, "{}") for i, r in enumerate(rows)])

    con.execute("INSERT INTO pulls (pull_id, file, name, endpoint, success, kind) VALUES (9999, 'raw/core/cat.json', "
                "'core_categories_l1_last365Day_p1', 'tiktok/category/rank', 1, 'category')")
    con.executemany("INSERT INTO categories (pull_id, position, category_id, category_name, category_level) VALUES "
                    "(9999, ?, ?, ?, 1)", [(i, c, n) for i, (c, n) in enumerate(CATS.items(), 1)])
    pools = {c: rng.lognormal(10 if c != "601303" else 5, 1.0, 1000) for c in ("100", "200", "601303")}
    prev = {}
    for m in months:
        for c, base in pools.items():
            rev = base * rng.lognormal(0, 0.6, len(base))
            order = np.argsort(-rev)
            top, rest = order[:500], order[500:]
            growth = rev[rest] / prev.get(c, rev)[rest]
            ris = rest[np.argsort(-growth)]
            ids = lambda idx: [f"{c}-{i}" for i in idx]  # noqa: E731

            def rows(idx):
                out = []
                for i in idx:
                    r = float(rev[i])
                    out.append((f"{c}-{i}", f"Product {c}-{i}", r, max(1.0, r / 20), 20.0,
                                100.0 if m == "2025-10" else float(rng.normal(50, 30)), 12.0, 0.1 * r, 0.6 * r,
                                0.3 * r, "2025-01-01", f"S{i % 37}", f"Seller {i % 37}", 3))
                return out
            for p in range(1, 6):
                put(pull(f"core_products_{m}_{c}_p{p}", "top", m, c, p, spec("revenue", p, c), 100),
                    rows(top[(p - 1) * 100:p * 100]))
            pages = 4 if m == deep_month else 2
            for p in range(1, pages + 1):
                kind = "risers" if p <= 2 else "risers_deep"
                put(pull(f"core_risers_{m}_{c}_p{p}", kind, m, c, p, spec("revenue_growth_rate", p, c), 100),
                    rows(ris[(p - 1) * 100:p * 100]))
            prev[c] = rev
        pull(f"core_products_{m}_834312_p1", "top", m, "834312", 1, spec("revenue", 1, "834312"), 0, success=0)
    if extra:
        m = months[-2]
        put(pull("products_kw_dress", "top", None, None, 1, {"page_size": 100, "keyword": "dress"}, 1),
            [("kw-1", "kw", 1e6, 1, 1, 1, 1, 0, 0, 0, "2025-01-01", "S", "S", 1)])
        put(pull("probe_sort", "risers", m, "100", 1, spec("revenue_growth_rate", 1, "100", size=10), 1),
            [("probe-1", "p", 1e6, 1, 1, 1, 1, 0, 0, 0, "2025-01-01", "S", "S", 1)])
        put(pull("probe_l2", "top", m, "999", 1, spec("revenue", 1, "999"), 1),
            [("l2-1", "p", 1e6, 1, 1, 1, 1, 0, 0, 0, "2025-01-01", "S", "S", 1)])
        put(pull("probe_depth_p11", "top", m, "100", 11, spec("revenue", 11, "100"), 1),
            [("deep-1", "p", 1, 1, 1, 1, 1, 0, 0, 0, "2025-01-01", "S", "S", 1)])
    con.commit()
    con.close()
    return Path(path)


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    path = make_db(tmp_path_factory.mktemp("db") / "k.db", deep_month=MONTHS[-1])
    rows, cats, notes, pulls = md.load_rows(path)
    return path, rows, cats, notes, pulls


def copy_rows(rows, month, cat, product, **change):
    r = rows[(rows["month"] == month) & (rows["cat"] == cat)].head(1).copy()
    for k, v in change.items():
        r[k] = v
    r["product_id"] = product
    return r


# ---------------------------------------------------------------- point in time
def test_point_in_time_never_uses_later_data(synth):
    _, rows, *_ = synth
    cut = "2026-02"
    full, _, _ = md.build(rows)
    early, _, info = md.build(rows, cutoff=cut)
    assert early["month"].max() == cut and info["data_cutoff"] == cut
    key = ["product_id", "month"]
    a = full[full["month"] <= cut].set_index(key).sort_index()
    b = early.set_index(key).sort_index()
    assert a.index.equals(b.index)
    pd.testing.assert_frame_equal(a[md.FEATURES], b[md.FEATURES])
    # tamper with everything after the cutoff: the cut build must not change at all
    later = rows["month"] > cut
    tampered = rows.copy()
    tampered.loc[later, "revenue"] *= 50
    tampered.loc[later, "product_id"] = tampered.loc[later, "product_id"] + "x"
    again, _, _ = md.build(tampered, cutoff=cut)
    pd.testing.assert_frame_equal(early, again)
    # labels that need months after the cutoff are missing, not 0
    last = early[early["month"] == cut]
    assert last[["y_holders_1m", "y_breakout_1m", "y_holders_3m", "y_breakout_3m"]].isna().all().all()
    prev = early[(early["month"] == "2026-01")]
    assert prev.loc[prev["population"] == "top500", "y_holders_1m"].notna().all()
    assert prev["y_holders_3m"].isna().all() and prev["y_breakout_3m"].isna().all()
    # full build: a label at t equals membership of a top 500 at t+1
    t5 = set(zip(full.loc[full["in_top500"], "product_id"], full.loc[full["in_top500"], "month"]))
    r = full[(full["month"] == "2026-01") & (full["population"] == "risers")]
    assert (r["y_breakout_1m"] == [float((p, "2026-02") in t5) for p in r["product_id"]]).all()


def test_exclusions(synth):
    _, rows, cats, notes, pulls = synth
    reasons = " | ".join(n["reason"] for n in notes)
    for part in ("failed call", "rolling window", "page size 10", "not a level-1 category", "page 11"):
        assert part in reasons
    assert not pulls["name"].str.contains("probe|kw").any()
    p, attrs, info = md.build(rows)
    assert "2025-10" not in set(p["month"]) and info["dropped_rows"]["excluded_months"] > 0
    assert "834312" not in set(p["cat"])
    nov = p[p["month"] == "2025-11"]
    for f in ("mom_growth", "listed_prev", "was_top500_prev", "months_seen_before", "cat_growth", "kalo_growth_slog"):
        assert nov[f].isna().all(), f
    assert nov["q_prior_partial"].all() and not p.loc[p["month"] == "2026-01", "q_prior_partial"].any()
    assert p.loc[p["month"] == "2026-01", "listed_prev"].notna().all()
    assert p.loc[p["cat"] == "601303", "q_thin_category"].all()
    assert not p.loc[p["cat"] == "100", "q_thin_category"].any()
    for f in md.CURRENT_VALUE_FIELDS:
        assert f not in md.FEATURES
    assert {"commission_rate", "sku_count", "launch_date"} <= set(attrs.columns)
    assert not {"commission_rate", "sku_count", "launch_date", "age_days"} & set(md.FEATURES)
    assert md.ai_flag_point_in_time("2026-05", 0) is None and md.ai_flag_point_in_time("2026-07", 1) == 1
    deep = p[p["population"] == "risers_deep"]
    assert len(deep) and deep["riser_pos"].isna().all() and (deep["deep_riser_pos"] > 200).all()
    assert deep["month"].eq(MONTHS[-1]).all()


def test_growth_placeholder_is_missing(synth):
    _, rows, *_ = synth
    r = rows.copy()
    m = (r["month"] == "2026-02") & (r["cat"] == "100")
    r.loc[m, "growth_raw"] = 100.0
    p, _, _ = md.build(r)
    sub = p[(p["month"] == "2026-02") & (p["cat"] == "100")]
    assert sub["kalo_growth_slog"].isna().all() and sub["q_growth_placeholder"].all()


def test_dedupe_and_split_category(synth, tmp_path):
    path, rows, *_ = synth
    con = sqlite3.connect(path)
    pid = con.execute("SELECT pull_id FROM pulls WHERE name = 'core_products_2026-01_100_p1'").fetchone()[0]
    dup = make_dup(con, pid)
    con.close()
    try:
        rows2, _, notes, pulls = md.load_rows(path)
        assert any(n["pull_id"] == pid and n["reason"].startswith("duplicate") for n in notes)
        assert dup in set(pulls["pull_id"])
        p, _, _ = md.build(rows2)
        sub = p[(p["month"] == "2026-01") & (p["cat"] == "100")]
        assert sub["q_dedup"].any() and not p.duplicated(["product_id", "month"]).any()
        assert (sub["population"] == "top500").sum() == 500
    finally:
        con = sqlite3.connect(path)
        for t in ("products", "pulls"):
            con.execute(f"DELETE FROM {t} WHERE pull_id = ?", (dup,))
        con.commit()
        con.close()
    # split: the same product in categories 100 and 200 in one month
    a = copy_rows(rows, "2026-03", "100", "SPLIT", revenue=9000.0, units=300.0, kind="top", pos=1)
    b = copy_rows(rows, "2026-03", "200", "SPLIT", revenue=4000.0, units=100.0, kind="top", pos=2)
    p, _, _ = md.build(pd.concat([rows, a, b], ignore_index=True))
    s = p[(p["product_id"] == "SPLIT") & (p["month"] == "2026-03")]
    assert len(s) == 1
    s = s.iloc[0]
    assert s["revenue"] == 13000.0 and s["units"] == 400.0 and s["cat"] == "100" and s["q_split_category"]


def make_dup(con, pid):
    """A later re-pull of the same list page (like the Womenswear pilot pages)."""
    row = con.execute("SELECT name, kind, month, category_id, page, filters FROM pulls WHERE pull_id = ?",
                      (pid,)).fetchone()
    new = con.execute("SELECT MAX(pull_id) + 1 FROM pulls").fetchone()[0]
    con.execute("INSERT INTO pulls (pull_id, file, name, endpoint, date_range, filters, success, n_records, sha256, "
                "collected_at, kind, month, category_id, page) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (new, f"raw/x/{new}.json", "pilot_" + row[0], "tiktok/product/rank", row[2], row[5], 1, 100, "d",
                 "2026-10-26T00:00:00", row[1], row[2], row[3], row[4]))
    con.execute("INSERT INTO products SELECT ?, position, product_id, product_name, revenue, sales_volumn, unit_price, "
                "revenue_growth_rate, commission_rate, live_revenue, video_revenue, showcase_revenue, launch_date, "
                "seller_id, seller_name, sku_count, raw_json FROM products WHERE pull_id = ?", (new, pid))
    con.commit()
    return new


# ---------------------------------------------------------------- harness
def test_embargo_and_label_maturity(synth):
    _, rows, *_ = synth
    p, _, _ = md.build(rows)
    for name, t in me.TASKS.items():
        d = me.task_frame(p, name)
        sel, hold = me.origins(d, t["h"])
        months = sorted(d["mo"].unique())
        if hold is None:  # too few labelled months in the synthetic data for this horizon
            assert t["h"] == 3 and len(months) < me.MIN_TRAIN_MONTHS + t["h"] + 1
            continue
        assert hold == max(months)  # the last fully labelled month is the holdout
        for o in sel + [hold]:
            tr, te = me.split(d, o, t["h"])
            assert tr["mo"].max() + t["h"] <= o  # every training label matured by the test month
            assert tr["mo"].nunique() >= me.MIN_TRAIN_MONTHS
            assert (te["mo"] == o).all() and te["y"].notna().all()
        assert d[t["y"]].notna().all()
        assert d["mo"].max() + t["h"] <= md._ord(pd.Series([p["month"].max()]))[0]


def by_month_from(diffs, base=0.3, metric_noise=0.0):
    out = {}
    for i, dlt in enumerate(diffs):
        m = f"2026-0{i + 1}"
        out[m] = {b: {"p_cat@10": base, "lift@20": 3.0} for b in me.BASELINES + me.TRANSPARENT}
        out[m]["floor_ratio"] = {"p_cat@10": base + 0.02, "lift@20": 3.5}
        out[m]["hgb"] = {"p_cat@10": base + 0.02 + dlt, "lift@20": 3.5 + metric_noise}
        out[m]["logistic"] = {"p_cat@10": base + 0.02, "lift@20": 3.5}
    return out


def test_decision_rule():
    sel, hold = ["2026-01", "2026-02", "2026-03", "2026-04"], "2026-05"
    win = me.decide(by_month_from([0.05, 0.04, 0.06, 0.05, 0.03]), sel, hold)
    assert win["adopted"] == "hgb" and win["adopted_type"] == "model"
    tie = me.decide(by_month_from([0.0, 0.0, 0.0, 0.0, 0.0]), sel, hold)
    assert tie["adopted"] == "floor_ratio" and tie["adopted_type"] == "baseline"
    mixed = me.decide(by_month_from([0.05, -0.04, 0.06, -0.05, 0.01]), sel, hold)
    assert mixed["adopted"] == "floor_ratio"  # CI includes zero
    lost = me.decide(by_month_from([0.05, 0.04, 0.06, 0.05, -0.01]), sel, hold)
    assert lost["adopted"] == "floor_ratio"  # loses on the holdout month
    bm = by_month_from([0.0] * 5)
    for m in bm:  # logistic clearly beats every single rule; hgb only ties logistic
        bm[m]["logistic"] = {"p_cat@10": 0.40, "lift@20": 3.5}
        bm[m]["hgb"] = {"p_cat@10": 0.40, "lift@20": 3.5}
    lad = me.decide(bm, sel, hold)
    assert lad["adopted"] == "logistic" and lad["best_rule"] == "floor_ratio"
    assert me.decide(by_month_from([0.05] * 5), sel, None)["final"] is False


def test_cat_ranks_and_metrics():
    cats = np.array(["a", "a", "a", "b", "b"])
    s = np.array([0.1, 0.9, 0.5, 0.2, 0.3])
    assert me.cat_ranks(cats, s, np.zeros(5)).tolist() == [3, 1, 2, 2, 1]
    te = pd.DataFrame({"cat": cats, "y": [0, 1, 0, 1, 0]})
    r = me.month_metrics(te, s, np.zeros(5))
    assert r["hits_cat@3"] == 2 and r["picks_cat@3"] == 5 and r["p@10"] == 0.4


def test_eval_registry_holdout_spent_and_model_dir(synth, tmp_path, monkeypatch):
    _, rows, cats, notes, pulls = synth
    monkeypatch.setattr(md, "SNAPSHOTS", tmp_path / "snaps")
    p, attrs, info = md.build(rows)
    snap = md.write_snapshot(p, attrs, info, notes, pulls, "t", cats)
    with pytest.raises(SystemExit):
        md.write_snapshot(p, attrs, info, notes, pulls, "t", cats)  # snapshots are never overwritten
    man = json.loads((snap / "manifest.json").read_text(encoding="utf-8"))
    assert man["data_cutoff"] == MONTHS[-1] and "2025-10" in man["exclusions"]["months"]
    db = tmp_path / "reg.db"
    args = ["--tasks", "breakout_1m,holders_1m", "--snapshot", str(snap), "--db", str(db), "--models-root",
            str(tmp_path), "--evals-dir", str(tmp_path / "evals"), "--date", "2099-01-01"]
    me.main(["select"] + args)
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM research_runs WHERE holdout_used = 0").fetchone()[0] == 2
    con.close()
    me.main(["final"] + args)
    con = sqlite3.connect(db)
    rows_ = con.execute("SELECT task, decision, holdout_used FROM research_runs WHERE holdout_used = 1").fetchall()
    con.close()
    assert len(rows_) == 2 and all(r[1].startswith("ADOPT") for r in rows_)
    mdir = tmp_path / "model_v2_2099-01-01"
    mm = json.loads((mdir / "manifest.json").read_text(encoding="utf-8"))
    assert set(mm["tasks"]) == {"breakout_1m", "holders_1m"}
    assert "p_cat@10" in mm["tasks"]["breakout_1m"]["hit_rates_all_evaluated_months"]
    with pytest.raises(SystemExit, match="already exists"):
        me.main(["final"] + args)
    with pytest.raises(SystemExit, match="already spent"):
        me.main(["final"] + args[:-1] + ["2099-01-02"])


# ---------------------------------------------------------------- v1 pin
def test_v1_pin_refuses_existing_dir_and_ignores_deep_risers(synth, tmp_path, monkeypatch):
    import score_breakouts
    import train_product_model as tp
    existing = tmp_path / "out"
    existing.mkdir()
    monkeypatch.setattr(tp, "load", lambda: (_ for _ in ()).throw(AssertionError("loaded before the check")))
    with pytest.raises(SystemExit, match="Refusing"):
        tp.main(["--out", str(existing)])
    monkeypatch.setattr(score_breakouts, "load", tp.load)
    with pytest.raises(SystemExit, match="Refusing"):
        score_breakouts.main(["--out", str(existing)])
    monkeypatch.undo()
    path, *_ = synth
    monkeypatch.setattr(tp, "DB", path)
    df, _, _ = tp.load()
    deep_pages = df[(df["list"] == "risers") & (df["name"].str.endswith(("_p3", "_p4")))]
    assert deep_pages.empty and df["pos"][df["list"] == "risers"].max() <= 200
    assert (tp.OUT.name == "model_v1_2026-10-25")


# ---------------------------------------------------------------- weekly report
def fake_task_info():
    return {"registry_run_id": "test-run", "ranker": {"type": "baseline", "name": "floor_ratio",
                                                      "feature": "log_vs_floor", "sign": 1, "fill": -9.0,
                                                      "label": "sales as a share of the category's 500th-place sales"},
            "hit_rates_all_evaluated_months": {"months": ["2026-03", "2026-06"], "base_rate": 0.05,
                                               "p_cat@10": {"hit_rate": 0.33, "hits": 33, "picks": 100},
                                               "p_cat@3": {"hit_rate": 0.45, "hits": 9, "picks": 20},
                                               "by_category_p_cat@10": {}}}


def write_model_dir(root):
    d = root / "model_v2_2099-01-01"
    d.mkdir(parents=True)
    (d / "manifest.json").write_text(json.dumps({"tasks": {"breakout_3m": fake_task_info()}}), encoding="utf-8")
    return d


def test_weekly_report_offline_has_no_forecast_wording(synth, tmp_path, monkeypatch):
    import weekly_breakout_report as w
    path, *_ = synth
    monkeypatch.setattr(md, "DB", path)
    monkeypatch.setattr(me, "MODELS_ROOT", tmp_path)
    monkeypatch.setattr(w, "WEEKLY", tmp_path / "weekly")
    write_model_dir(tmp_path)
    blocked = []
    monkeypatch.setitem(sys.modules, "kalodata", None)  # importing the paid client would fail the test
    pdf = w.main(["--offline", "--min-price", "0", "--max-price", "1000", "--min-sales", "0", "--min-commission", "0",
                  "--include-fallen"])
    assert pdf.exists() and not blocked
    csv = pd.read_csv(tmp_path / "weekly" / pdf.name.replace(".pdf", ".csv"))
    assert len(csv) and "rank_in_category" in csv and not any("chance" in c or c.startswith("p_") for c in csv)
    hist = pd.read_csv(tmp_path / "weekly" / "history.csv")
    assert {"rank_in_category", "ranker", "model_dir"} <= set(hist.columns) and "chance_3m" not in hist
    import pypdf
    text = "\n".join(pg.extract_text() for pg in pypdf.PdfReader(str(pdf)).pages)
    assert "Research shortlist — not a forecast" in text
    for bad in ("chance", "probabilit", "≥ 50%", "likely to break"):
        assert bad not in text.lower()
    assert "outside the tested range" in text.lower()


def test_weekly_report_story_wording_and_flags():
    import argparse
    import weekly_breakout_report as w
    args = argparse.Namespace(purpose="affiliate", categories="all", offline=True, top_k=10, min_price=15,
                              max_price=60, min_sales=3000, include_fallen=False, max_per_category=3,
                              min_commission=10)
    info = fake_task_info()
    meta = w.build_meta("2026-10-28", "2026-09", args, info["ranker"], info, Path("model_v2_x"), 100, 20, 5, 1, 0,
                        None, 50)
    pick = {"product_name": "Second Chance Jeans", "category": "Alpha", "cat": "100", "rank_in_category": 1,
            "n_in_category": 50, "pct_of_floor": 80.0, "unit_price": 20.0, "commission_rate": 12.0, "revenue": 5000,
            "units": 250, "mom_growth": np.nan, "video_share": 0.5, "age_days_today": 300, "sku_count": 3,
            "floor": 6000, "status": "new", "url": "https://example.invalid/p", "link_ok": None, "verdict": "x",
            "product_id": "1", "info": {"detail": {}, "videos": [], "comments": None, "source": []},
            "why": ["Sales are 80% of the bar."], "fit": [("Season", "n/a")], "risks": ["none"], "cat_hit": None}
    st = w.styles()
    flow = w.story([pick], [], meta, st, 500)
    own = w.text_of(flow, own_only=True)
    assert not w.FORBIDDEN.search(own)
    assert "Research shortlist — not a forecast" in own and "Second Chance" not in own
    assert "Second Chance" in w.text_of(flow)  # third-party text is still shown
    with pytest.raises(SystemExit):
        w.parse(["--scan", "--offline"])
    src = Path(w.__file__).read_text(encoding="utf-8")
    assert "min-chance" not in src and "p_breakouts" not in src
