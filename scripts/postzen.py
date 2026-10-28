"""Minimal PostZen client (api.postzen.dev, docs https://docs.postzen.dev/). Never prints the key.

Key: POSTZEN_API_KEY (config secrets.postzen_api). Used by the studio conveyor for scheduling and analytics.

  get(path, **params)     GET /v1/<path>          (retried on 429/5xx/connection errors, 4 attempts)
  post(path, body, key)   POST /v1/<path>         (retried only with an idempotency key, which makes it repeatable)
  upload(path)            presigned upload of a local file -> public URL PostZen can post
  sync_external(account)  pull an account's live posts into PostZen now (dashboard syncs call it first)
"""
import mimetypes
import time
import uuid

import requests

import hub_env

API = "https://api.postzen.dev/v1"


def _headers():
    return {"Authorization": f"Bearer {hub_env.get_secret('postzen_api')}", "Content-Type": "application/json"}


def _check(r):
    if not r.ok:
        raise RuntimeError(f"PostZen {r.request.method} {r.url.split('?')[0]}: HTTP {r.status_code} {r.text[:400]}")
    return r.json() if r.content else {}


RETRY_STATUS = {429, 500, 502, 503, 504}
RETRY_WAITS = (2, 5, 15)  # seconds between attempts (4 attempts in all)


def _request(method, url, retry, **kw):
    """One API call with retries on rate limits, server errors and dropped connections. Only calls that are safe to
    repeat retry: reads, updates, deletes, and creates that carry an idempotency key (PostZen returns the original
    post for a repeated x-request-id instead of creating a second one)."""
    for attempt in range(len(RETRY_WAITS) + 1):
        try:
            r = requests.request(method, url, timeout=60, **kw)
        except (requests.ConnectionError, requests.Timeout):
            if not retry or attempt == len(RETRY_WAITS):
                raise
            time.sleep(RETRY_WAITS[attempt])
            continue
        if r.status_code in RETRY_STATUS and retry and attempt < len(RETRY_WAITS):
            wait = RETRY_WAITS[attempt]
            if r.status_code == 429 and (r.headers.get("Retry-After") or "").isdigit():
                wait = min(int(r.headers["Retry-After"]), 60)
            time.sleep(wait)
            continue
        return _check(r)


def get(path, **params):
    return _request("GET", f"{API}/{path}", True, headers=_headers(), params=params)


def post(path, body, idempotency_key=None, retry=None):
    """retry defaults to True only when an idempotency key makes the create safe to repeat."""
    headers = _headers() | ({"x-request-id": idempotency_key} if idempotency_key else {})
    return _request("POST", f"{API}/{path}", bool(idempotency_key) if retry is None else retry, headers=headers, json=body)


def put(path, body):
    return _request("PUT", f"{API}/{path}", True, headers=_headers(), json=body)


def delete(path):
    return _request("DELETE", f"{API}/{path}", True, headers=_headers())


def sync_external(account_id):
    """Ask PostZen to pull the account's live posts from the platform now, so its analytics list includes posts it
    hasn't picked up yet (draft uploads posted from the app, posts made directly on TikTok or Facebook). Returns a
    short summary; a failure is reported, not raised, so a dashboard sync still runs."""
    try:
        s = post("posts/sync-external", {"accountId": account_id}, retry=True).get("synced") or {}  # repeatable
        return f"found {s.get('postsFound', 0)}, synced {s.get('postsSynced', 0)}"
    except (RuntimeError, requests.RequestException) as e:
        return f"failed ({str(e)[:120]})"


def upload(path):
    content_type = mimetypes.guess_type(str(path))[0] or "video/mp4"
    info = post("media/presign", {"filename": f"{uuid.uuid4().hex[:8]}_{path.name}", "contentType": content_type})
    with open(path, "rb") as f:
        put_r = requests.put(info["uploadUrl"], data=f, headers={"Content-Type": content_type}, timeout=600)
    if not put_r.ok:
        raise RuntimeError(f"PostZen upload of {path.name} failed: HTTP {put_r.status_code}")
    return info["publicUrl"]
