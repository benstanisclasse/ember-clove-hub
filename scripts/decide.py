"""Assign each live creative a status from its metrics and its product's economics.

Statuses (first match wins):
  STOP-LOSS         spend >= loss limit with no purchase -> pause now
  TRACKING-CHECK    many clicks but no add-to-cart or purchase -> check the pixel before judging
  LEARNING          fewer than rules.learning_days days with spend -> too early to judge
  WINNER-CANDIDATE  >= winner_min_purchases at or below break-even CPA
  PROMISING         a purchase within promising_cpa_multiple x break-even, or above-median attention + add-to-carts
  WEAK              attention well below the group median
  INCONCLUSIVE      none of the above yet

Usage:
  python decide.py            update creatives.csv and write reports/status_<date>.md
"""
import statistics

import hubdata as hd


def aggregate():
    totals = {}
    for m in hd.read("metrics"):
        cid = m.get("creative_id")
        if not cid:
            continue
        t = totals.setdefault(cid, {"days": set(), "spend": 0.0, "impressions": 0.0, "clicks": 0.0,
                                    "video_views": 0.0, "views_2s": 0.0, "views_6s": 0.0,
                                    "add_to_cart": 0.0, "purchases": 0.0, "purchase_value": 0.0})
        spend = hd.num(m["spend"], 0.0)
        if spend > 0:
            t["days"].add(m["date"])
        for k in ("spend", "impressions", "clicks", "video_views", "views_2s", "views_6s",
                  "add_to_cart", "purchases", "purchase_value"):
            t[k] += hd.num(m.get(k), 0.0)
    for t in totals.values():
        t["days_live"] = len(t.pop("days"))
        t["ctr"] = t["clicks"] / t["impressions"] if t["impressions"] else 0.0
        t["hook_rate"] = t["views_2s"] / t["video_views"] if t["video_views"] else 0.0
        t["hold_rate"] = t["views_6s"] / t["video_views"] if t["video_views"] else 0.0
        t["cpa"] = t["spend"] / t["purchases"] if t["purchases"] else None
    return totals


def classify(t, product, rules, medians):
    be = hd.num(product.get("break_even_cpa"), 0.0) if product else 0.0
    max_loss = hd.num(product.get("max_loss"), 20.0) if product else 20.0
    if t["spend"] >= max_loss and t["purchases"] == 0:
        return "STOP-LOSS", f"spent ${t['spend']:.2f} >= loss limit ${max_loss:.2f} with no purchase"
    if t["clicks"] >= rules["tracking_check_clicks"] and t["add_to_cart"] == 0 and t["purchases"] == 0:
        return "TRACKING-CHECK", f"{t['clicks']:.0f} clicks but no add-to-cart or purchase recorded"
    if t["days_live"] < rules["learning_days"]:
        return "LEARNING", f"{t['days_live']} day(s) live; judge after {rules['learning_days']}"
    if be <= 0:
        econ_note = " (break-even CPA unknown or zero: profitability can't be judged)"
    else:
        econ_note = ""
    cpa = t["cpa"]
    if be > 0 and cpa is not None and t["purchases"] >= rules["winner_min_purchases"] and cpa <= be:
        return "WINNER-CANDIDATE", f"{t['purchases']:.0f} purchases at ${cpa:.2f} CPA <= break-even ${be:.2f}"
    attention_ok = t["hook_rate"] >= medians["hook_rate"] and t["ctr"] >= medians["ctr"]
    if (be > 0 and cpa is not None and cpa <= be * rules["promising_cpa_multiple"]) or \
            (attention_ok and t["add_to_cart"] > 0):
        return "PROMISING", (f"CPA ${cpa:.2f}" if cpa else f"above-median attention, {t['add_to_cart']:.0f} add-to-cart") + econ_note
    weak = rules["weak_ratio"]
    if t["hook_rate"] < medians["hook_rate"] * weak and t["ctr"] < medians["ctr"] * weak:
        return "WEAK", f"hook rate {t['hook_rate']:.0%} and CTR {t['ctr']:.2%} well below median"
    return "INCONCLUSIVE", "not enough signal yet" + econ_note


def main():
    rules = hd.config()["rules"]
    totals = aggregate()
    if not totals:
        print("No metrics yet.")
        return
    products = {p["product_id"]: p for p in hd.read("products")}
    creatives = hd.read("creatives")
    medians = {k: statistics.median([t[k] for t in totals.values()]) for k in ("hook_rate", "ctr")}

    lines = [f"# Creative status — {hd.today()}", "",
             "| Creative | Status | Spend | Days | Hook | CTR | ATC | Purch | CPA | Reason |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    pause = []
    for c in creatives:
        t = totals.get(c["creative_id"])
        if not t:
            continue
        status, reason = classify(t, products.get(c.get("product_id")), rules, medians)
        c["status"], c["status_reason"] = status, reason
        if status == "STOP-LOSS":
            pause.append(c)
        cpa = f"${t['cpa']:.2f}" if t["cpa"] else "-"
        lines.append(f"| {c['creative_id']} | {status} | ${t['spend']:.2f} | {t['days_live']} | "
                     f"{t['hook_rate']:.0%} | {t['ctr']:.2%} | {t['add_to_cart']:.0f} | "
                     f"{t['purchases']:.0f} | {cpa} | {reason} |")
    hd.write("creatives", creatives)

    if pause:
        lines += ["", "## Pause now (stop-loss)", ""]
        lines += [f"- {c['creative_id']} — TikTok ad {c.get('tiktok_ad_id') or '(ad id missing)'}" for c in pause]
    hd.REPORTS.mkdir(parents=True, exist_ok=True)
    out = hd.REPORTS / f"status_{hd.today()}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    hd.log(f"Status update: {len(totals)} creatives, {len(pause)} stop-loss")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
