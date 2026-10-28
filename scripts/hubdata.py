"""Shared read/write helpers and schemas for the Hub's CSV records."""
import csv
import datetime
import json
import sys

from hub_env import HUB_ROOT, load_config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA = HUB_ROOT / "data"
REPORTS = HUB_ROOT / "reports"
RECIPES = HUB_ROOT / "recipes"
ASSETS = HUB_ROOT / "assets"
INBOX = DATA / "inbox"
LOG = HUB_ROOT / "log.md"
LEARNINGS = HUB_ROOT / "learnings.md"

SCHEMAS = {
    "products": [
        "product_id", "title", "group", "vendor", "product_type", "handle", "url",
        "inventory", "in_stock", "price_min", "price_max", "unit_cost_min", "unit_cost_max",
        "cost_source", "shipping_cost", "shipping_known", "payment_fees", "refund_allowance",
        "contribution", "margin_pct", "break_even_cpa", "target_cpa", "max_loss",
        "price_for_desired_cpa", "advertisable", "notes", "updated_at",
    ],
    "experiments": [
        "experiment_id", "cycle", "platform", "product_id", "hypothesis", "angle", "test_type",
        "campaign_id", "ad_group_id", "optimization_event", "start_date", "end_date",
        "daily_budget", "max_loss", "status", "result", "decision", "notes",
    ],
    "creatives": [
        "creative_id", "parent_id", "changed_field", "experiment_id", "product_id", "platform",
        "format", "length_s", "resolution", "hook_text", "hook_type", "opening_visual", "setting",
        "creator", "pace_cuts_per_15s", "on_screen_text", "voice", "source", "credits_used",
        "cost_usd", "video_url", "local_path", "tiktok_video_id", "tiktok_ad_id", "meta_ad_id",
        "status", "status_reason", "recipe_path", "created_at",
    ],
    "metrics": [
        "date", "platform", "ad_id", "creative_id", "spend", "impressions", "clicks", "ctr",
        "cpc", "cpm", "video_views", "views_2s", "views_6s", "avg_watch_s", "add_to_cart",
        "checkouts", "purchases", "purchase_value", "synced_at",
    ],
}


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def today():
    return datetime.date.today().isoformat()


def csv_path(name):
    return DATA / f"{name}.csv"


def read(name):
    path = csv_path(name)
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    DATA.mkdir(parents=True, exist_ok=True)
    with open(csv_path(name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMAS[name], extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in SCHEMAS[name]})


def upsert(name, new_rows, keys):
    """Insert or update rows matched on the key columns; returns (inserted, updated)."""
    rows = read(name)
    index = {tuple(r.get(k, "") for k in keys): i for i, r in enumerate(rows)}
    inserted = updated = 0
    for new in new_rows:
        key = tuple(str(new.get(k, "")) for k in keys)
        if key in index:
            rows[index[key]].update({k: v for k, v in new.items() if v is not None})
            updated += 1
        else:
            index[key] = len(rows)
            rows.append(new)
            inserted += 1
    write(name, rows)
    return inserted, updated


def num(value, default=None):
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def log(text):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"- {now()} — {text}\n")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def config():
    return load_config()
