"""Hardening tests (Dashboard 2.0, Phase H): security headers, read-only server, atomic writes, last-good fallback.

Run: python -m pytest -q scripts/studio/test_hardening.py
"""
import json
import sqlite3
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio import analytics, dashboard_server  # noqa: E402


@pytest.fixture()
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(analytics, "DB", tmp_path / "a.db")
    srv = dashboard_server.ThreadingHTTPServer(("127.0.0.1", 0), dashboard_server.make_handler(15))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_security_headers_and_no_version_banner(server):
    for path in ("/", "/data", "/static/app.css", "/nope"):
        try:
            h = urllib.request.urlopen(server + path, timeout=10).headers
        except urllib.error.HTTPError as e:
            h = e.headers
        assert h["X-Content-Type-Options"] == "nosniff" and h["X-Frame-Options"] == "SAMEORIGIN"
        assert h["Referrer-Policy"] == "no-referrer"
        assert "Python" not in (h["Server"] or "")


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
def test_server_is_read_only(server, method):
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(urllib.request.Request(server + "/data", data=b"{}", method=method), timeout=10)
    assert e.value.code == 501


def test_atomic_write_never_leaves_a_partial_file(tmp_path):
    target = tmp_path / "x.json"
    analytics.write_text_atomic(target, '{"a": 1}')
    with pytest.raises(RuntimeError):
        with analytics.atomic_open(target) as f:
            f.write('{"a": 2, "half')
            raise RuntimeError("writer crashed mid-way")
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 1}  # the old version is untouched
    analytics.write_text_atomic(target, '{"a": 3}')
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 3}


def test_rows_serves_last_good_copy_when_a_file_breaks(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard_server, "OUT", tmp_path)
    (tmp_path / "demo.json").write_text('[{"k": 1}]', encoding="utf-8")
    assert dashboard_server._rows("demo")["rows"] == [{"k": 1}]
    (tmp_path / "demo.json").write_text('[{"k": 2', encoding="utf-8")  # a half-written file
    assert dashboard_server._rows("demo")["rows"] == [{"k": 1}]
    assert dashboard_server._rows("never_written") is None


def test_ref_images_only_from_refs_or_episodes(tmp_path, monkeypatch):
    out = tmp_path / "studio" / "dashboard"
    out.mkdir(parents=True)
    monkeypatch.setattr(dashboard_server, "OUT", out)
    dbf = tmp_path / "s.db"
    def connect():
        con = sqlite3.connect(dbf)
        con.row_factory = sqlite3.Row
        return con
    monkeypatch.setattr(dashboard_server.db, "connect", connect)
    assert dashboard_server.ref_image("1") is None  # table not there yet
    for rel in ("studio/refs/a.png", "studio/episodes/e1/b.JPG", "studio/other/c.png", "secret.png", "studio/refs/d.txt"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes(b"img")
    con = connect()
    con.execute("CREATE TABLE character_refs (ref_id INTEGER PRIMARY KEY, path TEXT)")
    con.executemany("INSERT INTO character_refs VALUES (?, ?)", [
        (1, "studio/refs/a.png"), (2, r"studio\episodes\e1\b.JPG"), (3, "studio/other/c.png"),
        (4, "studio/refs/../../secret.png"), (5, str(tmp_path / "secret.png")), (6, "studio/refs/d.txt"),
        (7, "studio/refs/missing.png")])
    con.commit()
    con.close()
    assert dashboard_server.ref_image("1") == (tmp_path / "studio/refs/a.png").resolve()
    assert dashboard_server.ref_image("2") == (tmp_path / "studio/episodes/e1/b.JPG").resolve()
    for bad in ("3", "4", "5", "6", "7", "99", "1.png", "../1", "", "-1"):
        assert dashboard_server.ref_image(bad) is None, bad
