"""Owner decision 2026-10-24: no post-production edits. Ads are the generated videos as delivered by the API.

- EC-P01-A03-H01-V01: back to the approved raw try-on video (no captions / end card).
- EC-P01-A03-H02-V01, EC-P01-A02-H02-V01: text-hook edit variants -> REJECTED.
- EC-P01-A02-H01-V01: silent walking clip without a spoken hook -> NOT_USED (not an ad on its own).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

REASON = "Owner 2026-10-24: no text/end-card edits; use generated videos as delivered"


def update(cid, status, reason, local_path=None):
    r = recipe.load(cid)
    r["status"] = status
    r["status_reason"] = reason
    if local_path:
        r["local_path"] = local_path
    for step in r["steps"].get("post_production", []):
        step["superseded"] = True
    with open(recipe._recipe_path(cid), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    hd.upsert("creatives", [recipe._creative_row(r)], ["creative_id"])


update("EC-P01-A03-H01-V01", "APPROVED", "Raw generated try-on video approved by owner (watched and listened)",
       local_path="assets/EC-P01-A03-H01-V01/tryon_raw.mp4")
update("EC-P01-A03-H02-V01", "REJECTED", REASON)
update("EC-P01-A02-H02-V01", "REJECTED", REASON)
update("EC-P01-A02-H01-V01", "NOT_USED", "Silent walking clip with no spoken hook; owner wants complete generated ads. Kept for reference.")
hd.log("Owner decision: no post-production edits (captions/hook text/end cards). Ads must be complete generated videos. "
       "EC-P01-A03-H01-V01 restored to the approved raw video; edit variants rejected; walking clip not used. "
       "Edited files kept in assets/final/ for reference only.")
print("updated")
