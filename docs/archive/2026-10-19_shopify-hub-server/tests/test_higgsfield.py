"""Higgsfield client against a scripted transport."""

from __future__ import annotations

from decimal import Decimal as D

import httpx
import pytest
from ads_mock import MockHTTP, body
from pydantic import SecretStr

from app.config import Settings
from app.integrations.higgsfield import HiggsfieldClient
from app.integrations.http import IntegrationError, NotConfiguredError

BASE = "https://api.higgsfield.ai"


def client(mock: MockHTTP, **kw: object) -> tuple[HiggsfieldClient, list[float]]:
    s = Settings(
        **{
            "higgsfield_api_key": SecretStr("kid"),
            "higgsfield_api_secret": SecretStr("ksec"),
            "higgsfield_video_model": "kling/v3/i2v",
            **kw,
        }
    )  # type: ignore[arg-type]
    slept: list[float] = []
    return HiggsfieldClient(s, http=mock.client(), sleep=slept.append), slept


def test_not_configured() -> None:
    with pytest.raises(NotConfiguredError):
        HiggsfieldClient(Settings())


def test_submit_auth_idempotency_and_webhook() -> None:
    mock = MockHTTP().on(
        "POST",
        "/higgsfield-ai/soul/v2/standard",
        {
            "status": "queued",
            "request_id": "r-1",
            "status_url": f"{BASE}/requests/r-1/status",
            "cancel_url": f"{BASE}/requests/r-1/cancel",
        },
    )
    hf, _ = client(mock)
    sub = hf.submit(
        "higgsfield-ai/soul/v2/standard",
        {"prompt": "x"},
        idempotency_key="hub-job-7",
        webhook_url="https://hub.example.com/webhooks/higgsfield/tok",
    )
    assert (sub.request_id, sub.status) == ("r-1", "queued")
    req = mock.calls[0]
    assert (
        req.headers["Authorization"] == "Key kid:ksec"
        and req.headers["Idempotency-Key"] == "hub-job-7"
    )
    assert req.url.params["hf_webhook"] == "https://hub.example.com/webhooks/higgsfield/tok"
    assert body(req) == {"prompt": "x"}


def test_estimate_and_status_outputs() -> None:
    mock = (
        MockHTTP()
        .on("POST", "/estimate/kling/v3/i2v", {"credits": "14.000", "usd": "0.875"})
        .on(
            "GET",
            "/requests/r-2/status",
            {
                "status": "completed",
                "request_id": "r-2",
                "video": {"url": "https://cdn.hf/out.mp4"},
            },
        )
    )
    hf, _ = client(mock)
    est = hf.estimate("kling/v3/i2v", {"prompt": "x", "duration": 8})
    assert (est.credits, est.usd) == (D("14.000"), D("0.875"))
    st = hf.status("r-2")
    assert st.done and st.output_url == "https://cdn.hf/out.mp4"


def test_image_output_and_failure_status() -> None:
    mock = (
        MockHTTP()
        .on(
            "GET",
            "/requests/a/status",
            {"status": "completed", "images": [{"url": "https://cdn/i.png"}]},
        )
        .on("GET", "/requests/b/status", {"status": "nsfw", "error": "moderated"})
    )
    hf, _ = client(mock)
    assert hf.status("a").output_url == "https://cdn/i.png"
    b = hf.status("b")
    assert b.done and b.output_url is None and b.error == "moderated"


def test_concurrency_400_retries_but_bad_params_400_does_not() -> None:
    busy = httpx.Response(400, text="Too many concurrent requests")
    mock = MockHTTP().on("POST", "/estimate/m", [busy, {"credits": "1", "usd": "0.05"}])
    hf, slept = client(mock)
    assert hf.estimate("m", {}).usd == D("0.05") and len(slept) == 1

    bad, _ = client(
        MockHTTP().on(
            "POST", "/estimate/m", httpx.Response(400, text="field 'duration' must be 5 or 10")
        )
    )
    with pytest.raises(IntegrationError, match="duration") as exc:
        bad.estimate("m", {"duration": 7})
    assert exc.value.retryable is False


@pytest.mark.parametrize(
    ("code", "word", "retryable"),
    [(404, "not available", False), (423, "blocked", True), (503, "not ready", True)],
)
def test_model_unavailable_codes(code: int, word: str, retryable: bool) -> None:
    hf, _ = client(MockHTTP().on("POST", "/m", httpx.Response(code, text="nope")))
    with pytest.raises(IntegrationError, match=word) as exc:
        hf.submit("m", {})
    assert exc.value.retryable is retryable


def test_bad_key_does_not_leak_secret() -> None:
    hf, _ = client(MockHTTP().on("GET", "/status", httpx.Response(401, text="Unauthorized")))
    with pytest.raises(IntegrationError) as exc:
        hf.status("x")
    assert "ksec" not in str(exc.value)


def test_download_streams_and_returns_mime() -> None:
    mock = MockHTTP().on(
        "GET",
        "cdn.hf/out.mp4",
        httpx.Response(200, content=b"MP4DATA", headers={"content-type": "video/mp4"}),
    )
    hf, _ = client(mock)
    assert hf.download("https://cdn.hf/out.mp4") == (b"MP4DATA", "video/mp4")
    assert "Authorization" not in mock.calls[0].headers  # signed CDN url: no credentials sent


def test_models_probe_availability() -> None:
    mock = (
        MockHTTP()
        .on("POST", "/estimate/higgsfield-ai/soul/v2/standard", {"credits": "1.5", "usd": "0.094"})
        .on("POST", "/estimate/kling/v3/i2v", httpx.Response(400, text="image_url is required"))
        .on("POST", "/estimate/gone/model", httpx.Response(404, text="not found"))
    )
    hf, _ = client(mock, higgsfield_extra_models="gone/model")
    models = {m["model"]: m["available"] for m in hf.models()}
    assert models == {
        "higgsfield-ai/soul/v2/standard": True,
        "kling/v3/i2v": True,
        "gone/model": False,
    }
