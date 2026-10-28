"""Minimal PostZen client (api.postzen.dev, docs https://docs.postzen.dev/). Never prints the key.

Key: POSTZEN_API_KEY (config secrets.postzen_api). Used by the studio conveyor for scheduling and analytics.

  get(path, **params)     GET /v1/<path>
  post(path, body)        POST /v1/<path>
  upload(path)            presigned upload of a local file -> public URL PostZen can post
  sync_external(account)  pull an account's live posts into PostZen now (dashboard syncs call it first)
"""
import mimetypes
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


def get(path, **params):
    return _check(requests.get(f"{API}/{path}", headers=_headers(), params=params, timeout=60))


def post(path, body, idempotency_key=None):
    headers = _headers() | ({"x-request-id": idempotency_key} if idempotency_key else {})
    return _check(requests.post(f"{API}/{path}", headers=headers, json=body, timeout=60))


def put(path, body):
    return _check(requests.put(f"{API}/{path}", headers=_headers(), json=body, timeout=60))


def delete(path):
    return _check(requests.delete(f"{API}/{path}", headers=_headers(), timeout=60))


def sync_external(account_id):
    """Ask PostZen to pull the account's live posts from the platform now, so its analytics list includes posts it
    hasn't picked up yet (draft uploads posted from the app, posts made directly on TikTok or Facebook). Returns a
    short summary; a failure is reported, not raised, so a dashboard sync still runs."""
    try:
        s = post("posts/sync-external", {"accountId": account_id}).get("synced") or {}
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
