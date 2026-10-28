"""A tiny scripted HTTP mock for ad platform clients."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs

import httpx

Handler = Callable[[httpx.Request], httpx.Response | dict[str, Any]]


class MockHTTP:
    """Route by (method, substring of path). First match wins; responses can be a
    dict (200 JSON), an httpx.Response, or a list consumed one item per call.

    When one path contains another (TikTok ``smart_plus/ad/get`` contains ``ad/get``), anchor
    the shorter one (``/v1.3/ad/get``) so it can't catch the longer path's calls."""

    def __init__(self) -> None:
        self.routes: list[tuple[str, str, Any]] = []
        self.calls: list[httpx.Request] = []

    def on(self, method: str, path_part: str, response: Any) -> MockHTTP:
        self.routes.append((method.upper(), path_part, response))
        return self

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        for method, part, resp in self.routes:
            if request.method == method and part in str(request.url):
                if isinstance(resp, list):
                    resp = resp.pop(0) if len(resp) > 1 else resp[0]
                if callable(resp):
                    resp = resp(request)
                return resp if isinstance(resp, httpx.Response) else httpx.Response(200, json=resp)
        raise AssertionError(f"unmocked {request.method} {request.url}")

    def client(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self))

    # helpers for assertions
    def find(self, method: str, path_part: str) -> list[httpx.Request]:
        return [c for c in self.calls if c.method == method and path_part in str(c.url)]


def form(request: httpx.Request) -> dict[str, str]:
    return {k: v[0] for k, v in parse_qs(request.content.decode()).items()}


def body(request: httpx.Request) -> Any:
    return json.loads(request.content)


def query(request: httpx.Request) -> dict[str, str]:
    return {k: v for k, v in request.url.params.items()}
