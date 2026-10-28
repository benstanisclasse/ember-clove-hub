"""Record the billed amount and QA notes for a generated creative.

Usage: python scripts/record_actual_cost.py <creative_id> <usd> <balance_after> "<qa notes>"
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

cid, usd, balance, notes = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
r = recipe.load(cid)
for step in r["steps"].get("clip", []):
    if step.get("status") == "completed":
        step["usd"] = usd
        step["cost_note"] = f"actual: open.higgsfield.ai billing usage -${usd:.2f}; balance after ${balance}"
r["cost"]["usd"] = usd
r["qa"] = {"checked_at": hd.now(), "result": "visual pass; audio for owner to confirm", "notes": notes}
with open(recipe._recipe_path(cid), "w", encoding="utf-8") as f:
    json.dump(r, f, indent=2, ensure_ascii=False)
hd.upsert("creatives", [recipe._creative_row(r)], ["creative_id"])
hd.log(f"{cid}: generated; actual cost ${usd:.2f}; Higgsfield API balance ${balance}. QA: {notes}")
print(f"{cid}: recorded ${usd:.2f}")
