"""Minimal Higgsfield developer-API client (open.higgsfield.ai, billed per second).

Uses the key in the HIGGSFIELD_API_KEY user environment variable (via hub_env). Never prints the key
or signed upload URLs. Docs: https://docs.higgsfield.ai/docs/llms.txt and each model's API reference.

  upload(path)                      -> public_url of an uploaded reference file
  submit(model_path, payload)       -> submission dict (request_id, status_url, cancel_url)
  wait(status_url)                  -> final status dict (completed / failed / nsfw / canceled)
  download(url, dest)               -> dest
"""
import mimetypes
import time

import requests

import hub_env

API = "https://api.higgsfield.ai"
TERMINAL = {"completed", "failed", "nsfw", "canceled"}


def _headers():
    return {"Authorization": f"Key {hub_env.get_secret('higgsfield_api')}", "Content-Type": "application/json"}


def upload(path):
    content_type = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    r = requests.post(f"{API}/files/generate-upload-url", json={"content_type": content_type},
                      headers=_headers(), timeout=60)
    r.raise_for_status()
    info = r.json()
    with open(path, "rb") as f:
        put = requests.put(info["upload_url"], data=f, headers=info.get("upload_headers") or {}, timeout=120)
    if not put.ok:
        raise RuntimeError(f"Upload of {path} failed with HTTP {put.status_code}")
    return info["public_url"]


def submit(model_path, payload):
    r = requests.post(f"{API}/{model_path}", json=payload, headers=_headers(), timeout=60)
    if not r.ok:
        raise RuntimeError(f"Submit failed: HTTP {r.status_code} {r.text[:500]}")
    return r.json()


def wait(status_url, every=10, timeout_s=1500, on_tick=None):
    start = time.time()
    while True:
        r = requests.get(status_url, headers=_headers(), timeout=60)
        r.raise_for_status()
        status = r.json()
        if on_tick:
            on_tick(status, int(time.time() - start))
        if status.get("status") in TERMINAL:
            return status
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Still {status.get('status')} after {timeout_s}s; request kept running, not cancelled")
        time.sleep(every)


def download(url, dest):
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    return dest
