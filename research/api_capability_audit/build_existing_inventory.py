"""API capability audit (2026-10-31): field-level inventory of research/kalodata/kalodata.db.

Reads _work/kalodata_db_inventory.json (made by a read-only pass over the database: column completeness, every key
path seen in raw_json) and writes existing_kalodata_db_fields.csv: one row per stored column and per raw_json path
that has no column of its own. Opens nothing else and changes no database.
Run: python -I research/api_capability_audit/build_existing_inventory.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = json.loads((HERE / "_work" / "kalodata_db_inventory.json").read_text(encoding="utf-8"))
OUT = HERE / "existing_kalodata_db_fields.csv"

K = "Kalodata API"
SOURCE = {  # table -> (source, endpoint, key, relationship)
    "pulls": ("Hub (scripts/kalodata_db.py)", "all endpoints (one row per raw response file)", "pull_id",
              "parent of every API table via pull_id"),
    "products": (K, "POST tiktok/product/rank", "pull_id+position (product_id repeats per month/query)",
                 "pull_id -> pulls; product_id -> product_details.product_id; seller_id = shop id"),
    "videos": (K, "POST tiktok/video/rank (1 row from tiktok/video/detail)", "pull_id+position (video_id repeats)",
               "pull_id -> pulls; product_filter = product_id when the rank was filtered by product; "
               "belonged_creator_id = creator id"),
    "product_details": (K, "POST tiktok/product/detail", "pull_id (one product per pull)",
                        "pull_id -> pulls; product_id -> products; product_shop_id = products.seller_id; "
                        "pri/sec/ter_cate_id -> categories.category_id"),
    "categories": (K, "POST tiktok/category/rank", "pull_id+position", "pull_id -> pulls; category_id"),
    "comment_insights": (K, "POST tiktok/product/comment/insight", "pull_id", "pull_id -> pulls; product_id -> products"),
    "video_features": ("Derived (Hub: scripts/video_pilot.py)", "video file via tiktok/video/url or public TikTok link; "
                       "faster-whisper, OpenCV, vision LLM via OpenRouter", "video_id",
                       "video_id -> videos.video_id; product_id -> products"),
    "video_elements": ("Derived (Hub: scripts/video_elements.py)", "frame sheets + vision LLM", "video_id",
                       "video_id -> video_features.video_id"),
    "video_audio": ("Derived (Hub: scripts/video_audio.py)", "audio classifier (AST AudioSet model)", "video_id",
                    "video_id -> video_features.video_id"),
    "research_runs": ("Hub (model registry)", "none (model training runs)", "run_id", "data_snapshot names a point-in-time panel"),
}

MEANING = {
    "pull_id": "Hub id of the API response this row came from", "position": "1-based row position in the response page",
    "file": "raw response file under research/kalodata/raw/", "pulled_on": "raw folder name (date or batch name)",
    "name": "raw file stem", "endpoint": "API path called", "region": "request region (US)",
    "date_range": "request date_range: rolling (last30Day...) or month (YYYY-MM)", "filters": "request body minus common params",
    "http_status": "HTTP status", "success": "API success flag", "n_records": "records in the response",
    "sha256": "raw file hash (idempotent load)", "collected_at": "raw file modified time (Kalodata gives no timestamp)",
    "kind": "Hub classification: top/risers/risers_deep/top_videos/product_videos/detail/comments/category/other",
    "month": "YYYY-MM when date_range is a month", "category_id": "first category filter in the request",
    "page": "request page_number",
    "product_id": "TikTok Shop product id", "product_name": "seller's product title",
    "revenue": "estimated GMV in the period (USD)", "sales_volumn": "estimated units sold in the period (API spelling)",
    "unit_price": "average selling price in the period", "revenue_growth_rate": "% change vs previous equal period",
    "commission_rate": "affiliate commission %", "live_revenue": "estimated GMV from livestreams",
    "video_revenue": "estimated GMV from videos", "showcase_revenue": "estimated GMV from product showcase / shop tab",
    "shopping_mall_revenue": "estimated GMV from the shop/mall surface (detail endpoint name)",
    "launch_date": "first-seen / listing date", "seller_id": "shop id", "seller_name": "shop name",
    "sku_count": "number of SKUs (variants)", "master_image_url": "main image URL (always null in our pulls)",
    "product_shop_id": "shop id", "pri_cate_id": "level-1 category id", "sec_cate_id": "level-2 category id",
    "ter_cate_id": "level-3 category id", "min_price": "lowest SKU price", "max_price": "highest SKU price",
    "creator_number": "creators promoting it in the period", "video_number": "videos promoting it in the period",
    "live_number": "livestreams promoting it in the period", "product_review_count": "review count",
    "delivery_type": "local (US warehouse) or global (cross-border)", "revenue_trend": "daily trend (always null in our pulls)",
    "product_region": "region code", "product_description": "rich-text description blocks (text, images)",
    "video_id": "TikTok video id", "video_title": "caption", "belonged_creator_id": "creator id",
    "belonged_creator_handle": "creator @handle", "views": "views in the period", "ads_roas": "estimated ad ROAS",
    "ad": "1 = ran as a paid ad", "ai_video": "1 = flagged AI-generated", "digg_count": "likes",
    "share_count": "shares", "comment_count": "comments", "ad_revenue_ratio": "% of video GMV from ads",
    "ad_view_ratio": "% of views from ads", "publish_date": "publish time (YYYY/MM/DD hh:mm:ss)",
    "creator_debut": "creator's first-seen date", "product_filter": "Hub: product_id the video rank was filtered by",
    "category_name": "category name", "rank": "rank in the response", "sale": "estimated units sold",
    "top3_shop_revenue_ratio": "% of category GMV held by the top 3 shops (concentration)",
    "average_revenue": "average GMV per shop/product (definition not confirmed)", "category_level": "Hub: requested level 1-3",
    "comment_summary": "AI summary of reviews (en + zh)", "pain_points": "AI-extracted complaints with key review ids",
    "positive_points": "AI-extracted praise", "usage_scenarios": "AI-extracted usage scenarios",
    "cached_at": "when Kalodata generated the insight (freshness)", "country_code": "review country",
    "original_comments": "raw reviews behind the insight (buyer identity stripped by the Hub)",
    "category": "Hub: product category name", "role": "Hub: winner or comparison video", "pair": "Hub: pairing key",
    "duration_s": "Hub: video length (s)", "cuts": "Hub: shot cuts (OpenCV)", "cuts_per_10s": "Hub: cut rate",
    "words": "Hub: spoken words (whisper)", "words_per_s": "Hub: speech rate", "speech_share": "Hub: share of time with speech",
    "hook_text": "Hub: words in first 3 s", "transcript": "Hub: whisper transcript", "tags_json": "Hub: vision-LLM tag form",
    "tag_model": "Hub: tagging model", "created_at": "Hub: processing time", "elements_json": "Hub: vision-LLM scene elements",
    "model": "Hub: model used", "music_share": "Hub: share of frames with music", "music_p": "Hub: music probability",
    "singing_p": "Hub: singing probability", "speech_p": "Hub: speech probability", "speech_db": "Hub: speech loudness",
    "gap_db": "Hub: background loudness", "gap_rel_db": "Hub: speech minus background", "music_level": "Hub: none/low/mid/high",
    "at": "Hub: processing time", "run_id": "model run id", "question": "research question", "task": "model task",
    "data_snapshot": "panel snapshot name", "data_cutoff": "last month of data", "features": "model features",
    "params": "model parameters", "seed": "random seed", "code_commit": "git commit", "eval_design": "evaluation design",
    "results_json": "metrics", "decision": "outcome", "holdout_used": "1 if the final holdout was used",
}


def meaning(path):
    leaf = path.split(".")[-1].replace("[]", "")
    return MEANING.get(path, MEANING.get(leaf, "undocumented: see raw response"))


rows = []
for table, info in INV["tables"].items():
    src, endpoint, key, rel = SOURCE[table]
    dates = info.get("pull_dates") or [None, None, None, None]
    last = dates[3] or ""
    derived = "derived" if src.startswith("Derived") else ("hub_metadata" if src.startswith("Hub") else "api_raw")
    for col, ci in info["columns"].items():
        rows.append(dict(table=table, field=col, kind="column", data_type=ci["declared"] or (ci["storage_types"][0][0] if ci["storage_types"] else ""),
                         meaning=meaning(col), source=src, source_endpoint=endpoint,
                         origin=("hub_metadata" if col in ("pull_id", "position", "category_level", "product_filter") and derived == "api_raw" else derived),
                         non_null_pct=ci["non_null_pct"], distinct=ci["distinct"], last_observation=last,
                         rows=info["rows"], key=key, relationship=rel))
    for p, pi in (info.get("raw_json_paths") or {}).items():
        if p in info["columns"]:
            continue
        rows.append(dict(table=table, field=f"raw_json.{p}", kind="raw_json only (no column)",
                         data_type="/".join(pi["types"]), meaning=meaning(p), source=src, source_endpoint=endpoint,
                         origin="api_raw", non_null_pct=pi["present_pct"], distinct="",
                         last_observation=last, rows=info["rows"], key=key, relationship=rel))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} rows -> {OUT}")
