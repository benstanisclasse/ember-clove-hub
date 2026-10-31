"""API capability audit (2026-10-31): build the machine-readable catalogues from the audit's working files.

Inputs (read only):
  _work/kalodata_endpoints_raw.json   official Kalodata OpenAPI spec + pricing page, normalised by the docs agent
  _work/cj_endpoints_raw.json         official CJ API 2.0 docs, normalised by the docs agent
  _work/cj_mcp_tools.json             CJ MCP tool catalogue + read-only access test
  ../kalodata/raw/**.json             our own past Kalodata responses (which fields really come back)
  ../kalodata/kalodata.db             only through _work/kalodata_db_inventory.json (what we store)
Outputs: kalodata_endpoints.json, cj_endpoints.json, kalodata_fields.csv, cj_fields.csv, api_costs.csv,
         capability_matrix.csv. Makes no API calls and changes no database.
Run: python -I research/api_capability_audit/build_catalog.py
"""
import collections
import csv
import glob
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "_work"
RAW = HERE.parent / "kalodata" / "raw"
USD_PER_CREDIT = 0.10  # Kalodata: "approximately"; purchase prices are behind login

# --- Kalodata: what our integration has actually done with each endpoint ---------------------------------------
# status vocabulary (Phase 24): confirmed_available | documented_not_access_tested | requires_additional_permissions |
# requires_account_upgrade | deprecated | unavailable | unknown
KALO_ACCESS = {
    "credit/balance": ("confirmed_available", "GET 200 on 2026-10-31 (free); 3 earlier calls", None),
    "credit/logs": ("confirmed_available", "POST 200 on 2026-10-31 (free), 5,317 charge records read", None),
    "tiktok/product/rank": ("confirmed_available", "2,617 responses 2026-10-25..26", "products"),
    "tiktok/product/detail": ("confirmed_available", "1,025 responses 2026-10-25..30 (never with need_extra/need_image)", "product_details"),
    "tiktok/video/rank": ("confirmed_available", "1,402 responses 2026-10-25..30", "videos"),
    "tiktok/video/detail": ("confirmed_available", "1 response 2026-10-26 (probe)", "videos"),
    "tiktok/video/url": ("confirmed_available", "26 responses (signed CloudFront URL, 5-minute expiry)", None),
    "tiktok/category/rank": ("confirmed_available", "14 responses; months rejected (code 501), rolling windows only", "categories"),
    "tiktok/product/comment/insight": ("confirmed_available", "18 responses; 2 'No enough comments' (not charged)", "comment_insights"),
}
KALO_UNTESTED_NOTE = ("Documented in the official spec; never called with our key. The open-center Home page says to "
                      "'select the target API in pricing', so some endpoints may need per-API enablement.")
KALO_EXTRA = [{  # called by our code but absent from the official docs
    "module": "video", "name": "Video download (undocumented)", "method": "POST", "path": "/openapi/v1/tiktok/video/download",
    "doc_url": None, "description": "Not in the official spec. Our pilot called it once (2026-10-26): HTTP 404. "
    "Use tiktok/video/url instead.", "request_params": [{"name": "video_id", "type": "string", "required": True}],
    "response_fields": [], "credit_cost": "unknown (credit log shows 27 x 0.5 charges vs 26 video/url responses)",
    "rate_limit": "unknown", "deprecated": None, "verification": "not documented"}]


def kalo_key(path):
    return path.replace("/openapi/v1/", "").strip("/")


def leaf(p):
    return p.split(".")[-1].replace("[]", "")


def observed_kalodata_fields():
    """endpoint -> {response field path as the spec writes it} seen in our raw files (sampled)."""
    files = collections.defaultdict(list)
    for f in glob.glob(str(RAW / "**" / "*.json"), recursive=True):
        try:
            j = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        if j.get("path"):
            files[j["path"]].append(j)
    random.seed(0)
    seen = {}
    for ep, items in files.items():
        paths = set()
        for j in random.sample(items, min(300, len(items))):
            r = j.get("response") or {}
            if not isinstance(r, dict):
                continue
            for k in r:
                paths.add(k)
            _walk(r.get("data"), "data", paths)
        seen[ep] = paths
    return seen


def _walk(o, prefix, out):
    if isinstance(o, dict):
        for k, v in o.items():
            p = f"{prefix}.{k}"
            out.add(p)
            _walk(v, p, out)
    elif isinstance(o, list):
        for v in o[:5]:
            _walk(v, prefix + "[]", out)


def stored_columns():
    inv = json.loads((WORK / "kalodata_db_inventory.json").read_text(encoding="utf-8"))
    return {t: set(i["columns"]) for t, i in inv["tables"].items()}


def build_kalodata():
    src = json.loads((WORK / "kalodata_endpoints_raw.json").read_text(encoding="utf-8"))
    seen = observed_kalodata_fields()
    cols = stored_columns()
    endpoints, fields = [], []
    for e in src["endpoints"] + KALO_EXTRA:
        key = kalo_key(e["path"])
        status, evidence, table = KALO_ACCESS.get(key, ("documented_not_access_tested", KALO_UNTESTED_NOTE, None))
        if key == "tiktok/video/download":
            status, evidence = "unavailable", "Not in official docs; HTTP 404 on 2026-10-26"
        obs = seen.get(key)
        out = dict(e)
        out.update(provider="kalodata", endpoint_key=key, access_status=status, access_evidence=evidence,
                   stored_in=f"kalodata.db:{table}" if table else ("raw files only" if obs else "not stored"),
                   observed_response_fields=sorted(obs) if obs else None,
                   field_doc_ref=f"kalodata_fields.csv (endpoint = {key})")
        out.pop("request_schema", None)
        out.pop("response_schema", None)
        endpoints.append(out)
        for p in e.get("request_params", []):
            fields.append(dict(provider="kalodata", module=e["module"], endpoint=key, method=e["method"], direction="request",
                               field_path=p["name"], type=p.get("type"), required=p.get("required"),
                               description=(p.get("description") or "").replace("\n", " "),
                               accepted_values=json.dumps(p.get("accepted_values"), ensure_ascii=False) if p.get("accepted_values") else "",
                               documented="yes", observed_in_our_responses="", stored_in_hub="",
                               source_url=e.get("doc_url") or ""))
        for r in e.get("response_fields", []):
            path = r["path"]
            if obs is None:
                o = "never called"
            else:
                o = "yes" if path in obs else "no"
            lf = leaf(path)
            if table and lf in cols.get(table, set()):
                st = f"column {table}.{lf}"
            elif table and o == "yes":
                st = f"raw_json in {table}"
            elif o == "yes":
                st = "raw files only"
            else:
                st = "no"
            fields.append(dict(provider="kalodata", module=e["module"], endpoint=key, method=e["method"], direction="response",
                               field_path=path, type=r.get("type"), required="",
                               description=(r.get("description") or "").replace("\n", " "), accepted_values="",
                               documented="yes" if r.get("documented", True) and not r.get("description_missing_in_spec") else "in spec, no description",
                               observed_in_our_responses=o, stored_in_hub=st, source_url=e.get("doc_url") or ""))
        # fields our responses carry that the spec does not list
        for path in sorted(obs or []):
            if path.startswith("data") and path not in {r["path"] for r in e.get("response_fields", [])}:
                lf = leaf(path)
                fields.append(dict(provider="kalodata", module=e["module"], endpoint=key, method=e["method"], direction="response",
                                   field_path=path, type="", required="", description="returned by the API but not in the spec",
                                   accepted_values="", documented="undocumented", observed_in_our_responses="yes",
                                   stored_in_hub=(f"column {table}.{lf}" if table and lf in cols.get(table, set()) else
                                                  f"raw_json in {table}" if table else "raw files only"),
                                   source_url=""))
    doc = {"provider": "Kalodata Open API", "retrieved": src.get("retrieved"), "source_urls": src.get("source_urls"),
           "local_copies": ["sources/kalodata_openapi_2026-10-31.json", "sources/kalodata_pricing_2026-10-31.json"],
           "global": src["global"], "status_vocabulary": "confirmed_available = called successfully with our key; "
           "documented_not_access_tested = in the official spec, never called; unavailable = called and failed / not documented",
           "endpoints": endpoints}
    (HERE / "kalodata_endpoints.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    write_csv(HERE / "kalodata_fields.csv", fields)
    return endpoints, fields


# --- CJ ---------------------------------------------------------------------------------------------------------
# MCP tool -> REST endpoint ("METHOD /path"). Inferred from tool names and descriptions (the tools rarely name their
# endpoint); mark as inferred wherever it is used. Tools with no REST twin (login/rate-limit status) are left out.
MCP_TO_REST = {
    "get_account_settings": "GET /setting/get", "get_warehouses": "GET /product/globalWarehouseList",
    "get_category_tree": "GET /product/getCategory", "search_products": "GET /product/listV2",
    "get_product_detail": "GET /product/query", "get_product_variants": "GET /product/variant/query",
    "get_product_inventory": "GET /product/stock/getInventoryByPid", "query_cj_inventory": "GET /product/stock/queryByVid",
    "get_product_reviews": "GET /product/productComments", "calculate_freight": "POST /logistic/freightCalculate",
    "calculate_freight_tip": "POST /logistic/freightCalculateTip",
    "diagnose_shipping_methods": "POST /logistic/unavailableShippingMethods", "get_tracking_info": "GET /logistic/trackInfo",
    "list_shops": "GET /shop/getShops", "get_my_products": "GET /product/myProduct/query",
    "list_product_connections": "GET /product/conn/connection", "create_product_connection": "POST /product/conn/connection",
    "disconnect_product": "DELETE /product/conn/connection", "get_order_list": "GET /shopping/order/list",
    "get_order_detail": "GET /shopping/order/getOrderDetail", "list_disputes": "GET /disputes/getDisputeList",
    "get_dispute_detail": "GET /disputes/getDisputeDetail", "get_dispute_products": "GET /disputes/disputeProducts",
    "confirm_dispute": "POST /disputes/disputeConfirmInfo", "create_dispute": "POST /disputes/create",
    "cancel_dispute": "POST /disputes/cancel", "query_private_inventory": "POST /product/stock/privateInventory/querySpuPage",
    "query_sku_details": "POST /product/stock/privateInventory/querySkuListByProductId",
    "query_sku_detail_page": "POST /product/stock/privateInventory/querySkuDetailPage",
    "query_sku_detail_by_sku": "POST /product/stock/privateInventory/querySkuDetailListBySku",
    "get_storage_info": "GET /warehouse/detail", "query_sourcing": "POST /product/sourcing/query",
    "create_sourcing": "POST /product/sourcing/create", "get_account_balance": "GET /shopping/pay/getBalance",
    "create_order": "POST /shopping/order/createOrderV2", "add_to_cart": "POST /shopping/order/addCart",
    "confirm_cart_and_pay": "POST /shopping/order/addCartConfirm",
    "generate_payment_link": "POST /shopping/order/saveGenerateParentOrder", "confirm_order": "PATCH /shopping/order/confirmOrder",
    "delete_order": "DELETE /shopping/order/deleteOrder", "pay_by_balance": "POST /shopping/pay/payBalance",
    "pay_by_balance_v2": "POST /shopping/pay/payBalanceV2", "merge_orders": "POST /shopping/mergeOrder/autoMatchMergeOrderListV3",
    "get_merge_progress": "POST /shopping/mergeOrder/autoMergeQueryProgress", "configure_webhook": "POST /webhook/set",
    "publish_product_async": "POST /listed/publishAsync", "publish_product_sync": "POST /listed/publishSync",
    "republish_product": "POST /listed/republish", "query_publish_status": "POST /listed/queryPublishStatus",
    "query_shop_publish_info": "POST /listed/queryShopInfo", "get_platform_child_categories": "POST /listed/getChildCategoryList",
    "get_platform_category_attributes": "POST /listed/getCategorySpecificsList", "query_platform_brands": "POST /listed/queryBrand",
    "save_product_to_shop": "POST /store/product/saveProduct",
    "query_warehouse_order_pictures": "POST /storehouseCenterWeb/syncStorehouseVideoRequests",
}


def cj_points(e):
    import re
    m = re.search(r"(\d+)\s*points per call", str(e.get("rate_limit") or "") + " " + str(e.get("notes") or ""))
    return int(m.group(1)) if m else 0


def build_cj():
    src_file, mcp_file = WORK / "cj_endpoints_raw.json", WORK / "cj_mcp_tools.json"
    if not src_file.exists():
        return [], [], []
    src = json.loads(src_file.read_text(encoding="utf-8"))
    mcp = json.loads(mcp_file.read_text(encoding="utf-8")) if mcp_file.exists() else {"tools": []}
    wraps = collections.defaultdict(list)
    for t in mcp["tools"]:
        t["rest_endpoint_inferred"] = MCP_TO_REST.get(t["name"])
        if t["rest_endpoint_inferred"]:
            wraps[t["rest_endpoint_inferred"]].append(t)
    endpoints, fields = [], []
    for e in src["endpoints"]:
        tail = e["path"].split("api2.0/v1")[-1].split("?")[0]
        tools = wraps.get(f"{e['method']} {tail}", [])
        ok = [t["name"] for t in tools if str(t.get("call_result", "")).startswith("ok")]
        failed = [(t["name"], t.get("call_result")) for t in tools if str(t.get("call_result", "")).startswith("error")]
        if e.get("deprecated"):
            status = "deprecated"
        elif ok:
            status = "confirmed_available"
        elif failed and any("reauthorize" in str(r).lower() or "authorization" in str(r).lower() for _, r in failed):
            status = "requires_additional_permissions"
        elif failed:
            status = "unknown"
        elif "image" in tail.lower() and "queryProductsByImage" in tail:
            status = "requires_account_upgrade"  # docs: Level 3+ accounts only
        else:
            status = "documented_not_access_tested"
        out = dict(e)
        out.update(provider="cj", access_status=status, points_per_call=cj_points(e),
                   access_evidence=(f"read-only call via CJ MCP tool(s) {ok} succeeded on 2026-10-31 (mapping inferred)" if ok else
                                    f"CJ MCP tool(s) returned an error: {failed}" if failed else
                                    "Docs: Level 3+ accounts only; never called" if status == "requires_account_upgrade" else
                                    "No direct CJ API key in the Hub; reachable only through the CJ MCP " +
                                    (f"tool(s) {[t['name'] for t in tools]}, not called in the audit" if tools else "(no tool wraps it)")),
                   mcp_tools=[t["name"] for t in tools],
                   stored_in="data/kalo_cj, data/cj_compare (hand-picked summary fields only)" if ok and e["module"].startswith(("Product", "Logistic")) else "not stored",
                   field_doc_ref=f"cj_fields.csv (endpoint = {e['path']})")
        endpoints.append(out)
        for p in e.get("request_params", []):
            fields.append(dict(provider="cj", module=e["module"], endpoint=e["path"], method=e["method"], direction="request",
                               field_path=p["name"], type=p.get("type"), required=p.get("required"),
                               description=(p.get("description") or "").replace("\n", " "),
                               accepted_values=json.dumps(p.get("accepted_values"), ensure_ascii=False) if p.get("accepted_values") else "",
                               documented="yes", safety_class=e.get("safety_class"), source_url=e.get("doc_url") or ""))
        for r in e.get("response_fields", []):
            fields.append(dict(provider="cj", module=e["module"], endpoint=e["path"], method=e["method"], direction="response",
                               field_path=r["path"], type=r.get("type"), required="",
                               description=(r.get("description") or "").replace("\n", " "), accepted_values="",
                               documented="yes" if r.get("documented", True) else "undocumented",
                               safety_class=e.get("safety_class"), source_url=e.get("doc_url") or ""))
    doc = {"provider": "CJ Dropshipping Open API 2.0", "retrieved": src.get("retrieved"), "source_urls": src.get("source_urls"),
           "global": src["global"], "mcp_server": {k: v for k, v in mcp.items() if k != "tools"},
           "mcp_tools": mcp["tools"], "endpoints": endpoints}
    (HERE / "cj_endpoints.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    write_csv(HERE / "cj_fields.csv", fields)
    return endpoints, fields, mcp["tools"]


# --- costs and matrix -------------------------------------------------------------------------------------------
KALO_COST = {  # endpoint -> (credits, unit, conditions, confidence)
    "rank": (0.1, "per 100 rows returned, rounded up (one page of up to 100 = 0.1)",
             "Pricing page rule. Our credit log: every rank page billed 0.1, including pages of 10 rows.", "verified (pricing page + our credit log)"),
    "detail": (0.1, "per call", "Pricing page.", "verified for product/detail and video/detail (credit log); documented for the rest"),
    "tiktok/video/url": (0.5, "per call", "Signed URL expires in 5 minutes; the file itself may be missing for low-view videos.", "verified (credit log: 27 x 0.5)"),
    "tiktok/product/images": (0.01, "per call", "Signed image URLs that expire.", "documented"),
    "tiktok/product/comments": (0.01, "per call (page of up to 100 reviews)", "Regions US, SG, ID, TH, VN, PH, MY only.", "documented"),
    "tiktok/product/comment/insight": (1.0, "per call, only when the insight is new", "Free to re-fetch until Kalodata refreshes it (about every two weeks). Failed / 'No enough comments' calls are not charged.", "verified (credit log: 24 charges for 26 calls)"),
    "tiktok/product/analysis": (0.1, "per call when data exists", "Pricing group 'Detail API'.", "documented"),
    "tiktok/creator/avatar-images": (0.1, "per call", "Pricing group 'Detail API'.", "documented"),
    "credit/balance": (0.0, "free", "", "verified"),
    "credit/logs": (0.0, "free", "", "verified"),
}


def kalo_cost(key):
    if key in KALO_COST:
        return KALO_COST[key]
    if key.endswith("/rank"):
        return KALO_COST["rank"]
    if key.endswith("/detail"):
        return KALO_COST["detail"]
    return (None, "unknown", "", "unknown")


def write_costs_and_matrix(kalo_eps, cj_eps):
    costs, matrix = [], []
    for e in kalo_eps:
        key = e["endpoint_key"]
        cr, unit, cond, conf = kalo_cost(key)
        if key == "tiktok/video/download":
            cr, unit, cond, conf = (0.5, "per call (inferred)", "Undocumented endpoint; 404 for us.", "inferred from credit log")
        pag = e.get("pagination") or ""
        costs.append(dict(provider="kalodata", endpoint=key, method=e["method"], purpose=e.get("name") or e.get("description", "")[:80],
                          credit_cost=cr, cost_unit=unit, usd_estimate=None if cr is None else round(cr * USD_PER_CREDIT, 4),
                          rate_limit=e.get("rate_limit"), pagination=pag, billing_conditions=cond, cost_confidence=conf))
        params = [p["name"] for p in e.get("request_params", []) if p["name"] not in ("region", "language", "currency", "sort_field.field", "sort_field.type", "page_size", "page_number", "rank_field", "asc")]
        matrix.append(dict(provider="Kalodata", category=e["module"], endpoint=f"{e['method']} {key}",
                           data_available="; ".join(sorted({leaf(r["path"]) for r in e.get("response_fields", []) if r["path"].startswith("data") and r["path"] not in ("data",)}))[:600],
                           filters=", ".join(params), historical_data=e.get("date_ranges") or "",
                           cost=f"{cr} credit {unit}" if cr is not None else unit, rate_limit=e.get("rate_limit"),
                           current_access=e["access_status"], currently_stored=e["stored_in"]))
    for e in cj_eps:
        pts = e["points_per_call"]
        money = ("SPENDS MONEY (pays from CJ balance)" if e.get("safety_class") == "financial" else
                 "creates an order: may spend money (createOrderV2/V3 with payType=2 pays from balance)" if e.get("safety_class") == "creates_order" else
                 "no money")
        costs.append(dict(provider="cj", endpoint=e["path"], method=e["method"], purpose=e.get("name"),
                          credit_cost=pts, cost_unit="CJ API points per call (daily quota: 50,000 free + 100 per $1 of top monthly spend; not money)",
                          usd_estimate=0, rate_limit=str(e.get("rate_limit") or "")[:200], pagination=e.get("pagination"),
                          billing_conditions=f"safety class: {e.get('safety_class')}; {money}",
                          cost_confidence="documented (points table)" if pts else "documented: not in points table (0)"))
        params = [p["name"] for p in e.get("request_params", [])]
        matrix.append(dict(provider="CJ", category=e["module"], endpoint=f"{e['method']} {e['path'].split('api2.0/v1')[-1]}",
                           data_available="; ".join(sorted({leaf(r["path"]) for r in e.get("response_fields", [])}))[:600],
                           filters=", ".join(params)[:400], historical_data="current state only (no history endpoints)" if e.get("safety_class") == "read_only" else "",
                           cost=f"{e['points_per_call']} points" + (" + the action spends money" if e.get("safety_class") in ("financial", "creates_order") else ""),
                           rate_limit=e.get("rate_limit"), current_access=e["access_status"], currently_stored=e["stored_in"]))
    write_csv(HERE / "api_costs.csv", costs)
    write_csv(HERE / "capability_matrix.csv", matrix)
    cell = lambda v, n: str(v or "").replace("|", "/").replace("\n", " ")[:n]  # noqa: E731
    lines = ["# API capability matrix (generated by build_catalog.py, 2026-10-31)", "",
             "One row per verified endpoint. Full field lists: `kalodata_fields.csv`, `cj_fields.csv`. Untruncated: "
             "`capability_matrix.csv`. Kalodata cost is in credits (1 credit ≈ $0.10). CJ cost is in API points, a "
             "daily quota, not money. Access status: confirmed_available = a call with our credentials succeeded "
             "(CJ: through the CJ MCP, mapping inferred).", "",
             "| Provider | Category | API endpoint | Data available | Filters | Historical data | Cost | Rate limit | Current access | Currently stored |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for m in matrix:
        lines.append("| " + " | ".join([m["provider"], cell(m["category"], 20), f"`{cell(m['endpoint'], 80)}`",
                                         cell(m["data_available"], 160), cell(m["filters"], 120), cell(m["historical_data"], 90),
                                         cell(m["cost"], 50), cell(m["rate_limit"], 50), m["current_access"],
                                         cell(m["currently_stored"], 50)]) + " |")
    (HERE / "capability_matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows):>6} rows -> {path.name}")


if __name__ == "__main__":
    k_eps, k_fields = build_kalodata()
    c_eps, c_fields, tools = build_cj()
    write_costs_and_matrix(k_eps, c_eps)
    print("kalodata endpoints", collections.Counter(e["access_status"] for e in k_eps))
    print("cj endpoints", collections.Counter(e["access_status"] for e in c_eps))
