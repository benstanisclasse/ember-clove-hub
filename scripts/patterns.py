"""Compare results by creative tag (hook type, opening visual, setting, ...) across all tested creatives.

Output is observational: it shows which tag values co-occur with better results, not what causes them.
Confirm a pattern with a one-change duplicate test before treating it as a rule.

Usage:
  python patterns.py          writes reports/patterns_<date>.md
"""
import hubdata as hd
from decide import aggregate

DIMENSIONS = ("format", "hook_type", "opening_visual", "setting", "creator", "on_screen_text", "voice",
              "pace_cuts_per_15s", "product_id")
MIN_N = 3


def main():
    totals = aggregate()
    creatives = [c for c in hd.read("creatives") if c["creative_id"] in totals]
    if not creatives:
        print("No creatives with metrics yet.")
        return
    titles = {p["product_id"]: p["title"] for p in hd.read("products")}

    lines = [f"# Patterns — {hd.today()}", "",
             f"{len(creatives)} creatives with data. Groups with fewer than {MIN_N} creatives are marked *thin*.",
             "Observations only — confirm with a one-change duplicate before acting.", ""]
    for dim in DIMENSIONS:
        groups = {}
        for c in creatives:
            value = c.get(dim) or "(blank)"
            if dim == "product_id":
                value = titles.get(value, value)
            g = groups.setdefault(value, {"n": 0, "spend": 0.0, "impressions": 0.0, "clicks": 0.0,
                                          "video_views": 0.0, "views_2s": 0.0, "add_to_cart": 0.0,
                                          "purchases": 0.0, "winners": 0})
            t = totals[c["creative_id"]]
            g["n"] += 1
            for k in ("spend", "impressions", "clicks", "video_views", "views_2s", "add_to_cart", "purchases"):
                g[k] += t[k]
            g["winners"] += c.get("status") in ("WINNER-CANDIDATE", "PROMISING")
        if len(groups) < 2:
            continue
        lines += [f"## {dim}", "", "| Value | N | Spend | Hook | CTR | ATC | Purch | CPA | Promising+ |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for value, g in sorted(groups.items(), key=lambda kv: -kv[1]["spend"]):
            hook = g["views_2s"] / g["video_views"] if g["video_views"] else 0
            ctr = g["clicks"] / g["impressions"] if g["impressions"] else 0
            cpa = f"${g['spend'] / g['purchases']:.2f}" if g["purchases"] else "-"
            thin = " *thin*" if g["n"] < MIN_N else ""
            lines.append(f"| {value}{thin} | {g['n']} | ${g['spend']:.2f} | {hook:.0%} | {ctr:.2%} | "
                         f"{g['add_to_cart']:.0f} | {g['purchases']:.0f} | {cpa} | {g['winners']}/{g['n']} |")
        lines.append("")
    hd.REPORTS.mkdir(parents=True, exist_ok=True)
    out = hd.REPORTS / f"patterns_{hd.today()}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
