"""Secrets must never reach log output."""

from __future__ import annotations

import json
import logging

import pytest
import structlog

from app.log import REDACTED, configure_logging, get_logger, scrub

SHOPIFY = "shpat_" + "a1b2c3d4" * 4
META = "EAA" + "Bx7" * 10
GOOGLE_REFRESH = "1//0g" + "Ab3_" * 8
SLACK = "https://hooks.slack.com/services/T000/B000/" + "x" * 24


@pytest.mark.parametrize(
    "raw",
    [
        f"token is {SHOPIFY}",
        f"meta {META} done",
        f"refresh {GOOGLE_REFRESH}",
        "Authorization: Bearer abcdefghijklmnop",
        "GET /v21.0/me?access_token=SECRET123&fields=id",
        "postgresql+psycopg://hub:s3cretpass@postgres:5432/hub",
        f"posting to {SLACK}",
    ],
)
def test_scrub_masks_token_shapes(raw: str) -> None:
    out = scrub(raw)
    for secret in (
        SHOPIFY,
        META,
        GOOGLE_REFRESH,
        "abcdefghijklmnop",
        "SECRET123",
        "s3cretpass",
        SLACK,
    ):
        assert secret not in out
    assert REDACTED in out


def test_scrub_leaves_normal_text_alone() -> None:
    text = "synced 42 orders for key=orders_backfill in 3.2s"
    assert scrub(text) == text


def test_logger_redacts_by_key_value_and_traceback(capsys: pytest.CaptureFixture[str]) -> None:
    structlog.reset_defaults()
    configure_logging("INFO", json=True)
    log = get_logger("test")
    log.info("calling shopify", access_token=SHOPIFY, headers={"Authorization": "x"}, shop="demo")
    try:
        raise RuntimeError(f"upstream said {META}")
    except RuntimeError:
        log.exception("boom")
    logging.getLogger("thirdparty").warning("url=%s", f"https://x/?api_key=K123&{SHOPIFY}")

    out = capsys.readouterr().out
    for secret in (SHOPIFY, META, "K123"):
        assert secret not in out
    first = json.loads(out.splitlines()[0])
    assert first["access_token"] == REDACTED
    assert first["headers"]["Authorization"] == REDACTED
    assert first["shop"] == "demo"
