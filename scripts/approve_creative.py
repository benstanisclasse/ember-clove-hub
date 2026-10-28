"""Mark a creative as owner-approved. Usage: python scripts/approve_creative.py <creative_id> "<note>" """
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

cid, note = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
r = recipe.load(cid)
r["status"] = "APPROVED"
r.setdefault("qa", {})["owner_review"] = {"approved_at": hd.now(), "note": note}
with open(recipe._recipe_path(cid), "w", encoding="utf-8") as f:
    json.dump(r, f, indent=2, ensure_ascii=False)
hd.upsert("creatives", [recipe._creative_row(r)], ["creative_id"])
hd.log(f"{cid}: approved by owner. {note}")
print(f"{cid} -> APPROVED")
