"""Paid-ad tests for the dashboard's Advertising > TikTok tests page. Run on every dashboard sync; read-only.

A test is a folder under research/ads/tiktok/product_tests/ with a live.json (the published campaign's facts: ids,
launch time, budget, rebate trial). For each live test this joins:
  launch_set.json      the ads as built: name, product, angle (A Product / B Lifestyle / C Benefit), captions, video
  products.json        product titles
  ads_entities.json    TikTok's own per-ad totals, written by the ads refresh task (scripts/ads_snapshot.py). TikTok
                       names an ad "<video file>_<our ad name>", so ads are matched on that form; every other ad in
                       the test's ad group was made by TikTok (auto-add creatives, or its own variants of one of our
                       ads, named "<variant>_<our ad name>" with no video file) and is totalled separately.
  DAILY_CHECKS.md      the daily read-only check's table (scheduled task tiktok-test01-daily-check)

A folder with a draft.json and no live.json is a test that isn't published yet (a TikTok draft or ad material only):
it gets one row in ad_test_drafts.json with what's built and what blocks it, and no numbers.

Writes studio/dashboard/ad_tests.json (one row per ad), ad_test_info.json (one row per test),
ad_test_checks.json (one row per daily check) and ad_test_drafts.json (one row per unpublished test). Numbers are
unknown (null), never 0, until TikTok reports the ad.
"""
import json
import re
from pathlib import Path

from studio import analytics

TESTS = analytics.HUB / "research" / "ads" / "tiktok" / "product_tests"
METRICS = ("spend", "impressions", "clicks", "purchases", "revenue")
CHECK_COLS = ("date", "status", "spend", "impressions", "clicks", "purchases", "added")


def _load(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _checks(path):
    """Rows of the table in DAILY_CHECKS.md (lines starting with a date cell)."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= len(CHECK_COLS) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[0]):
            rows.append(dict(zip(CHECK_COLS, cells[:len(CHECK_COLS)])))
    return rows


def _ours(entity_name, ad_name):
    """TikTok names our uploaded ads "<video file>_<our ad name>"; its own variants of an ad end with our name too
    but have no video file name in front."""
    return entity_name.endswith(ad_name) and ".mp4_" in entity_name


def build_test(folder, entities):
    """(ad rows, info row, check rows) for one test folder with a live.json; None when the test isn't live."""
    live = _load(folder / "live.json", None)
    if not live:
        return None
    launch = _load(folder / "launch_set.json", {})
    titles = {p.get("test_product_id"): p.get("title") for p in _load(folder / "products.json", {}).get("products", [])
              if isinstance(p, dict)}
    angles = live.get("angles", {})
    group = str(live.get("adgroup_id", ""))
    tt_ads = [e for e in entities if e.get("platform") == live.get("platform", "tiktok") and e.get("level") == "ad"]
    rows, matched = [], set()
    for a in launch.get("ads", []):
        name = a["ad_name"]
        hit = [e for e in tt_ads if _ours(str(e.get("name", "")), name)]
        matched.update(id(e) for e in hit)
        letter = name.split("_")[3] if name.count("_") >= 3 else ""
        caps = [c["text"] for c in a.get("caption_variants", [])] or a.get("captions") or [a.get("caption", "")]
        row = {"test": live["test"], "ad_name": name, "product_id": a.get("product_id"),
               "product": titles.get(a.get("product_id"), a.get("product_id")) or live.get("product"),
               "angle": f"{letter} {angles.get(letter) or a.get('angle', '')}".strip(), "captions": len(caps),
               "caption_1": caps[0], "caption_all": "\n".join(caps),
               "video": Path(a.get("video", "")).name, "reported": bool(hit)}
        for k in METRICS:
            row[k] = round(sum(float(e.get(k) or 0) for e in hit), 2) if hit else None
        rows.append(row)
    # Everything else in the test's ad group was made by TikTok (auto-add creatives, or its own variants of our ads:
    # "Music_Refresh", "New_Hook", "AI Generated Video" ...). Kept apart so they never pass as our approved ads.
    added = [e for e in tt_ads if id(e) not in matched and str(e.get("parent_id", "")) == group]
    period = next((e.get("period") for e in tt_ads if e.get("period")), None)
    refreshed = max((e.get("refreshed_at") or "" for e in tt_ads), default="") or None
    reb = live.get("rebate", {})
    info = {"test": live["test"], "name": live.get("name"), "campaign_name": live.get("campaign_name"),
            "campaign_id": live.get("campaign_id"), "adgroup_name": live.get("adgroup_name"),
            "launched_at": live.get("launched_at"), "daily_budget": live.get("daily_budget"),
            "budget_note": live.get("budget_note"), "rebate_target": reb.get("target_conversions"),
            "trial_ends_at": reb.get("trial_ends_at"), "rebate_rule": reb.get("rule"),
            "auto_add_creatives": live.get("auto_add_creatives"), "owner_decision": live.get("owner_decision"),
            "balance_loaded": live.get("balance_loaded"), "status": live.get("status", "active"),
            "status_note": live.get("status_note"), "watch": live.get("watch"),
            "ads": len(rows), "ads_reported": sum(r["reported"] for r in rows),
            "added_by_tiktok": len(added), "added_names": "; ".join(sorted({str(e.get("name")) for e in added})),
            "period": period, "refreshed_at": refreshed}
    for k in METRICS:
        info[f"added_{k}"] = round(sum(float(e.get(k) or 0) for e in added), 2) if added else None
    checks = [{"test": live["test"], **c} for c in _checks(folder / "DAILY_CHECKS.md")]
    return rows, info, checks


def build_draft(folder):
    """One row for a test that isn't live yet (draft.json, no live.json): what's built and what blocks it; else None."""
    draft = _load(folder / "draft.json", None)
    if not draft or (folder / "live.json").exists():
        return None
    ads = _load(folder / "launch_set.json", {}).get("ads", [])
    return {"test": draft["test"], "name": draft.get("name"), "product": draft.get("product"),
            "stage": draft.get("stage"), "campaign_name": draft.get("campaign_name"), "campaign_id": draft.get("campaign_id"),
            "adgroup_name": draft.get("adgroup_name"), "daily_budget": draft.get("daily_budget"),
            "starts_at": draft.get("starts_at"), "ads": len(ads),
            "ad_list": "\n".join(f"{a['ad_name']}: {a.get('angle', '')}" for a in ads),
            "blockers": "\n".join(draft.get("blockers", [])), "note": draft.get("note"), "plan": draft.get("plan")}


def build(out, tests_dir=TESTS):
    """Write the four datasets for every live and draft test; return summary lines for the sync log."""
    entities = _load(Path(out) / "ads_entities.json", [])
    ads, infos, checks, drafts = [], [], [], []
    for folder in sorted(p for p in Path(tests_dir).glob("*") if p.is_dir()):
        got = build_test(folder, entities)
        if got:
            ads += got[0]
            infos.append(got[1])
            checks += got[2]
        draft = build_draft(folder)
        if draft:
            drafts.append(draft)
    for name, data in (("ad_tests", ads), ("ad_test_info", infos), ("ad_test_checks", checks), ("ad_test_drafts", drafts)):
        analytics.write_text_atomic(Path(out) / f"{name}.json", json.dumps(data, ensure_ascii=False))
    return [f"ad_tests {len(ads)}", f"ad_test_info {len(infos)}", f"ad_test_checks {len(checks)}",
            f"ad_test_drafts {len(drafts)}"]
