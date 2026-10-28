"""One-off: record the actual Higgsfield charge and QA notes for EC-P01-A03-H01-V01 (2026-10-25)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import json  # noqa: E402

import hubdata as hd  # noqa: E402
import recipe  # noqa: E402

CID = "EC-P01-A03-H01-V01"
r = recipe.load(CID)
for s in r["steps"].get("clip", []):
    if s.get("status") == "completed":
        s["usd"] = 5.89
        s["cost_note"] = ("actual: open.higgsfield.ai billing 2026-10-25 usage -$5.89 (~$0.39/s); quoted ~$2.63 from the "
                          "'from $0.175/s' list price; owner cap was $3.50 -> exceeded by $2.39")
r["cost"]["usd"] = 5.89
r["qa"] = {
    "checked_at": hd.now(), "result": "visual pass; audio not verified",
    "notes": ("caramel color, ribbed mock neck, ribbed waistband, cable pattern with diagonal seam, front slit all match; "
              "hanger shot matches; 4 beats (hanger 0-3s, fit check 3-7s, full-length walk + twirl in boots 7-11s, "
              "selfie close-up 12-15s); AI-generated presenter; audio track present (15.07s) but speech not listened "
              "to - owner to confirm lines are clear and correct"),
}
with open(recipe._recipe_path(CID), "w", encoding="utf-8") as f:
    json.dump(r, f, indent=2, ensure_ascii=False)
hd.upsert("creatives", [recipe._creative_row(r)], ["creative_id"])
hd.log(f"{CID}: try-on ad generated (Seedance 2.5 ref-to-video 15s 720p 9:16 + audio). Actual charge $5.89 vs quote "
       f"~$2.63 and owner cap $3.50 (over by $2.39). Higgsfield API balance $57.51. Visual QA pass; audio unverified.")
print("recorded")
