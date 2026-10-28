"""Read-only Shopify Admin API client for the dashboard (Dashboard 2.0, Phase C).

App: "Ember Dashboard (read-only)" in the Shopify Dev Dashboard (created and installed 2026-10-27, owner approved).
Scopes: read_orders, read_products, read_inventory, read_reports, read_analytics. It cannot change anything.

Credentials are the app's client id and secret in Windows user env vars (config/hub.json "secrets":
shopify_client_id, shopify_client_secret). They are exchanged for a 24-hour access token (client credentials grant)
that lives only in this process's memory and is renewed before it expires. Nothing secret is printed or written.

  graphql(query, variables=None)  Admin GraphQL; raises on HTTP or GraphQL errors; retries 429/5xx with backoff
  shopifyql(query)                ShopifyQL through Admin GraphQL; returns (columns, rows as dicts)
  python -I scripts/shopify_api.py   connection check (shop name, scopes, order count) - no secrets shown
"""
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hub_env  # noqa: E402

API_VERSION = "2026-10"
_TOKEN = {"value": None, "expires": 0.0}


def _shop():
    return hub_env.load_config()["store"]["shopify_domain"]


def token():
    if _TOKEN["value"] and time.time() < _TOKEN["expires"] - 300:
        return _TOKEN["value"]
    r = requests.post(f"https://{_shop()}/admin/oauth/access_token", timeout=30,
                      data={"grant_type": "client_credentials", "client_id": hub_env.get_secret("shopify_client_id"),
                            "client_secret": hub_env.get_secret("shopify_client_secret")})
    if not r.ok:
        raise RuntimeError(f"Shopify token exchange failed: HTTP {r.status_code}")  # body may echo inputs; not shown
    j = r.json()
    _TOKEN.update(value=j["access_token"], expires=time.time() + float(j.get("expires_in") or 3600))
    return _TOKEN["value"]


def graphql(query, variables=None, tries=5):
    url = f"https://{_shop()}/admin/api/{API_VERSION}/graphql.json"
    for attempt in range(tries):
        r = requests.post(url, json={"query": query, "variables": variables or {}}, timeout=60,
                          headers={"X-Shopify-Access-Token": token(), "Content-Type": "application/json"})
        if r.status_code in (429, 500, 502, 503, 504) and attempt < tries - 1:
            time.sleep(min(2 ** attempt, 30))
            continue
        if r.status_code == 401 and attempt == 0:  # token revoked or expired early: get a new one once
            _TOKEN["value"] = None
            continue
        if not r.ok:
            raise RuntimeError(f"Shopify GraphQL HTTP {r.status_code}: {r.text[:300]}")
        j = r.json()
        errors = [e for e in j.get("errors") or [] if (e.get("extensions") or {}).get("code") != "THROTTLED"]
        throttled = len(errors) < len(j.get("errors") or [])
        if throttled and attempt < tries - 1:
            time.sleep(min(2 ** attempt, 30))
            continue
        if errors:
            raise RuntimeError(f"Shopify GraphQL errors: {errors[:3]}")
        return j["data"]
    raise RuntimeError("Shopify GraphQL: retries exhausted")


SHOPIFYQL = """query($q: String!) { shopifyqlQuery(query: $q) {
  tableData { columns { name dataType } rows } parseErrors } }"""


def shopifyql(query):
    res = graphql(SHOPIFYQL, {"q": query})["shopifyqlQuery"]
    if res.get("parseErrors"):
        raise RuntimeError(f"ShopifyQL parse errors: {res['parseErrors']}")
    table = res.get("tableData") or {}
    cols = [c["name"] for c in table.get("columns") or []]
    rows = [r if isinstance(r, dict) else dict(zip(cols, r)) for r in table.get("rows") or []]
    return cols, rows


if __name__ == "__main__":
    d = graphql("{ shop { name ianaTimezone currencyCode } ordersCount(limit: null) { count precision }"
                " productsCount { count } currentAppInstallation { accessScopes { handle } } }")
    print("shop:", d["shop"]["name"], d["shop"]["ianaTimezone"], d["shop"]["currencyCode"])
    print("scopes:", ", ".join(s["handle"] for s in d["currentAppInstallation"]["accessScopes"]))
    print("orders:", d["ordersCount"]["count"], d["ordersCount"]["precision"], "| products:", d["productsCount"]["count"])
    cols, rows = shopifyql("FROM sessions SHOW sessions, sessions_that_completed_checkout SINCE -7d UNTIL today")
    print("shopifyql sessions last 7 days:", rows)
