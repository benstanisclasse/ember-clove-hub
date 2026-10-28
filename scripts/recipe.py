"""Record each creative's production recipe as it is made, and duplicate winners one change at a time.

Library use (from other scripts or a session):
  recipe.new_creative("EC-P01-A01-H01-V01", experiment_id=..., product_id=..., format="product", ...)
  recipe.add_step("EC-P01-A01-H01-V01", "storyboard", {"prompt": "...", "job_id": "...", "credits": 9})
  recipe.finish("EC-P01-A01-H01-V01", video_url="...", local_path="...")
  recipe.duplicate("EC-P01-A01-H01-V01", "EC-P01-A01-H01-V02", "hook_text", "New first line")

CLI:
  python recipe.py show <creative_id>
"""
import copy
import json
import sys

import hubdata as hd

TAG_FIELDS = ("format", "hook_type", "opening_visual", "setting", "creator", "on_screen_text", "voice")
STEP_ORDER = ("concept", "product_reference", "creator", "script", "storyboard", "clip",
              "post_production", "distribution")


def _recipe_path(creative_id):
    return hd.RECIPES / f"{creative_id}.json"


def load(creative_id):
    return hd.load_json(_recipe_path(creative_id))


def _save(recipe):
    hd.RECIPES.mkdir(parents=True, exist_ok=True)
    with open(_recipe_path(recipe["creative_id"]), "w", encoding="utf-8") as f:
        json.dump(recipe, f, indent=2, ensure_ascii=False)


def _validate_tags(fields):
    vocab = hd.config()["tags"]
    bad = [f"{k}={fields[k]!r}" for k in TAG_FIELDS
           if fields.get(k) and fields[k] not in vocab.get(k, [])]
    if bad:
        raise ValueError(f"Unknown tag values: {', '.join(bad)}. Add them to config/hub.json 'tags' deliberately.")


def _creative_row(recipe):
    row = {k: recipe.get(k) for k in hd.SCHEMAS["creatives"]}
    row.update(recipe.get("tags", {}))
    row["credits_used"] = recipe["cost"]["credits"]
    row["cost_usd"] = recipe["cost"]["usd"]
    row["recipe_path"] = f"recipes/{recipe['creative_id']}.json"
    return row


def new_creative(creative_id, *, experiment_id, product_id, platform="tiktok", parent_id=None,
                 changed_field=None, length_s=15, resolution="720p", source="higgsfield", hook_text="",
                 **tags):
    if _recipe_path(creative_id).exists():
        raise FileExistsError(f"{creative_id} already exists")
    _validate_tags(tags)
    recipe = {
        "creative_id": creative_id, "parent_id": parent_id, "changed_field": changed_field,
        "experiment_id": experiment_id, "product_id": product_id, "platform": platform,
        "length_s": length_s, "resolution": resolution, "source": source, "hook_text": hook_text,
        "tags": {k: tags.get(k, "") for k in TAG_FIELDS} | {"pace_cuts_per_15s": tags.get("pace_cuts_per_15s", "")},
        "steps": {}, "cost": {"credits": 0, "usd": 0.0}, "status": "IN-PRODUCTION",
        "created_at": hd.now(),
    }
    _save(recipe)
    (hd.ASSETS / creative_id).mkdir(parents=True, exist_ok=True)
    hd.upsert("creatives", [_creative_row(recipe)], ["creative_id"])
    hd.log(f"New creative {creative_id} ({tags.get('format', '?')}, parent={parent_id or '-'})")
    return recipe


def add_step(creative_id, step, data, credits=0, usd=0.0):
    """Record one production step verbatim. Repeated steps (retries, multiple clips) are kept as a list."""
    recipe = load(creative_id)
    entry = dict(data, recorded_at=hd.now(), credits=credits, usd=usd)
    recipe["steps"].setdefault(step, []).append(entry)
    recipe["cost"]["credits"] += credits
    recipe["cost"]["usd"] = round(recipe["cost"]["usd"] + usd, 4)
    _save(recipe)
    hd.upsert("creatives", [_creative_row(recipe)], ["creative_id"])
    return recipe


def finish(creative_id, **fields):
    """Set final outputs (video_url, local_path, tiktok_video_id, tiktok_ad_id, ...) and mark READY."""
    recipe = load(creative_id)
    recipe.update(fields)
    recipe["status"] = fields.get("status", "READY")
    _save(recipe)
    hd.upsert("creatives", [_creative_row(recipe)], ["creative_id"])
    return recipe


def set_elements(creative_id, elements, source):
    """Record the video's detailed elements (room, presenter look, jewelry, styling, props, lighting, camera).

    source "intended" = what the prompt asked for (set at generation); "observed" = what a vision model saw in the
    finished video (scripts/video_elements.py). Keeping both shows where the model drifted from the brief.
    """
    recipe = load(creative_id)
    recipe.setdefault("elements", {})[source] = dict(elements, recorded_at=hd.now())
    _save(recipe)
    return recipe


def duplicate(parent_id, new_id, changed_field, new_value):
    """Copy a recipe, change exactly one field, and link it to its parent.

    changed_field "elements.<name>" (e.g. "elements.hair_color") changes one intended element for a one-element test.
    """
    parent = load(parent_id)
    child = copy.deepcopy(parent)
    child.update(creative_id=new_id, parent_id=parent_id, changed_field=changed_field,
                 status="PLANNED", created_at=hd.now(), cost={"credits": 0, "usd": 0.0},
                 video_url=None, local_path=None, tiktok_video_id=None, tiktok_ad_id=None, meta_ad_id=None)
    if changed_field in TAG_FIELDS or changed_field == "pace_cuts_per_15s":
        child["tags"][changed_field] = new_value
        _validate_tags(child["tags"])
    elif changed_field.startswith("elements."):
        intended = child.setdefault("elements", {}).setdefault("intended", {})
        intended[changed_field.split(".", 1)[1]] = new_value
        child["elements"].pop("observed", None)  # the new video hasn't been looked at yet
    else:
        child[changed_field] = new_value
    child["reuse_from_parent"] = {s: v[-1] for s, v in parent["steps"].items()}
    child["steps"] = {}
    _save(child)
    (hd.ASSETS / new_id).mkdir(parents=True, exist_ok=True)
    hd.upsert("creatives", [_creative_row(child)], ["creative_id"])
    hd.log(f"Duplicated {parent_id} -> {new_id}, changed {changed_field}")
    return child


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "show":
        print(json.dumps(load(sys.argv[2]), indent=2, ensure_ascii=False))
    else:
        print(__doc__)
