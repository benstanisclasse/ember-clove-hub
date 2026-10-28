"""Load and validate the world bible (studio/bible/*.yaml). Fails closed: a missing or malformed field is an error.

Each file carries status draft|approved, and an approval is locked to the file's contents (approved_hash): editing an
approved file in any way other than its comments makes it draft again until the owner re-approves it.
Content Studio Phase D: an approval also covers the files the text points to. studio/bible/approved_assets.json keeps,
per approved file, the sha256 of every reference image it names (face_refs, ref_images, reference_images), and for the
unit "templates" the prompt templates and scripts/prompt_style.py (TEMPLATE_FILES). A changed or missing image makes its
file draft again; a changed template blocks production until the owner approves the templates (`cli.py bible-approve
templates`). A file approved before this lock existed counts as "not locked yet" (shown, not blocking). Production (anything that can be posted) requires every file approved
(products.yaml only once selling is on, i.e. rules.mix.product_share_max > 0); test runs (--test) may use draft files
and their outputs can never be approved for posting.
"""
import hashlib
import json
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

HUB = Path(__file__).resolve().parents[2]
BIBLE = HUB / "studio" / "bible"
FILES = ["rules", "character", "world", "wardrobe", "products", "series"]
APPROVAL_KEYS = ("status", "approved_by", "approved_at", "approved_hash")
LOCK = "approved_assets.json"
REF_KEYS = ("face_refs", "ref_images", "reference_images")
TEMPLATE_FILES = ["studio/templates/video_prompt.j2", "studio/templates/video_prompt_frame.j2",
                  "studio/templates/first_frame.j2", "scripts/prompt_style.py"]


def content_hash(data):
    """Hash of a bible file's settings (comments and approval fields don't count)."""
    body = {k: v for k, v in data.items() if k not in APPROVAL_KEYS}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()[:16]


def asset_paths(data):
    """Every reference image a bible file names, in file order."""
    out = []
    if isinstance(data, dict):
        for k, v in data.items():
            out += [str(x) for x in v] if k in REF_KEYS and isinstance(v, list) else asset_paths(v)
    elif isinstance(data, list):
        for x in data:
            out += asset_paths(x)
    return list(dict.fromkeys(out))


def file_sha(hub, rel):
    p = Path(hub) / rel
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "missing"


def assets_lock(hub, paths):
    """{hash, files: {path: sha256}} for a set of files; the hash changes when any file changes or goes missing."""
    files = {p: file_sha(hub, p) for p in paths}
    return {"hash": hashlib.sha256(json.dumps(sorted(files.items())).encode()).hexdigest()[:16], "files": files}


def read_lock(folder=None):
    p = Path(folder or BIBLE) / LOCK
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def write_lock(lock, folder=None):
    p = Path(folder or BIBLE) / LOCK
    tmp = p.with_suffix(".tmp")
    tmp.write_bytes((json.dumps(lock, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    tmp.replace(p)


def template_status(folder=None):
    """{locked, changed: [files changed since the owner approved the templates]}."""
    folder = Path(folder or BIBLE)
    entry = read_lock(folder).get("templates")
    if not entry:
        return {"locked": False, "changed": []}
    now = assets_lock(folder.parents[1], TEMPLATE_FILES)["files"]
    return {"locked": True, "changed": [f for f in TEMPLATE_FILES if now.get(f) != entry["files"].get(f)]}


class Approval(BaseModel):
    status: Literal["draft", "approved"]
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    approved_hash: Optional[str] = None
    changed_since_approval: bool = False
    assets_locked: bool = False                  # Phase D: its reference images are hashed in approved_assets.json
    changed_assets: list[str] = []               # images changed or missing since the approval

    @model_validator(mode="after")
    def _approved_needs_owner(self):
        if self.status == "approved" and (self.approved_by != "owner" or not self.approved_at):
            raise ValueError("status approved requires approved_by: owner and approved_at")
        return self


class Posting(BaseModel):
    timezone: str
    max_posts_per_day: int = Field(ge=1, le=10)
    slots: list[str] = Field(min_length=1)


class Mix(BaseModel):
    value_share_min: float = Field(ge=0, le=1)
    product_share_max: float = Field(ge=0, le=1)


class Outfits(BaseModel):
    no_repeat_outfit_days: int = Field(ge=1)
    no_repeat_base_piece_posts: int = Field(ge=0)
    store_pieces_per_outfit: int = Field(ge=0, le=1)
    extra_store_shoes: bool = False        # store shoes may be a second Ember & Clove piece
    shoes_no_back_to_back: bool = False
    shoes_max_per_week: Optional[int] = None
    shoe_rules_from: Optional[str] = None  # shoe rules apply to posts on or after this date


class Rotation(BaseModel):
    no_same_product_back_to_back: bool
    no_same_room_back_to_back: bool
    no_same_series_back_to_back: bool


class Cta(BaseModel):
    soft_lines: list[str] = Field(min_length=1)
    max_soft_cta_per_window: int = Field(ge=0)
    window_posts: int = Field(ge=1)
    product_cta: str


class ScriptRules(BaseModel):
    words_per_second_min: float
    words_per_second_max: float
    lines: int = Field(ge=1, le=8)


class Generation(BaseModel):
    provider: Literal["openrouter"]
    model: str
    resolution: Literal["480p", "720p"]
    duration_s: int = Field(ge=4, le=30)
    usd_per_m_tokens: float
    max_usd_per_video: Optional[float] = None  # None = no cap
    max_usd_per_day: Optional[float] = None  # None = no cap
    max_usd_per_week: Optional[float] = None  # None = no cap
    max_attempts: int = Field(ge=1, le=5)
    max_reference_images: int = Field(ge=1, le=9)
    face_reference: bool = True  # False: describe her face in words only (no face image sent)


class Qa(BaseModel):
    require_exact_transcript: bool
    speech_share_min: float
    duration_tolerance_s: float
    frames_per_second_for_review: int


class Rules(Approval):
    posting: Posting
    mix: Mix
    outfits: Outfits
    rotation: Rotation
    cta: Cta
    script: ScriptRules
    banned_phrases: list[str]
    banned_regex: list[str]
    tts_avoid: list[str]
    generation: Generation
    qa: Qa


class Appearance(BaseModel):
    hair_color: str
    hair_length: str
    hair_style: str
    build: str
    nails: str
    signature_jewelry: list[str]


class Character(Approval):
    id: str
    name: str
    presents_as: str
    age_range: str
    personality: list[str] = Field(min_length=1)
    voice_style: str
    catchphrases: list[str]
    never_says: list[str]
    appearance: Appearance
    face_refs: list[str]
    ai_label_required: Literal[True]

    @model_validator(mode="after")
    def _approved_needs_face(self):
        if self.status == "approved" and (not self.face_refs or self.name in ("", "TBD")):
            raise ValueError("an approved character needs a name and at least one face reference image")
        return self


class Room(BaseModel):
    id: str
    name: str
    description: str
    ref_images: list[str]
    lighting: list[str]
    outdoor: bool = False


class World(Approval):
    city: str
    climate: str
    home: str
    rooms: list[Room] = Field(min_length=1)
    props: list[str]
    side_characters: list[str]

    @model_validator(mode="after")
    def _approved_needs_room_refs(self):
        if self.status == "approved" and any(not r.ref_images for r in self.rooms):
            raise ValueError("an approved world needs a reference image for every room")
        return self


Season = Literal["all", "spring", "summer", "fall", "winter"]
CATEGORIES = ("top", "knitwear", "bottom", "dress", "outerwear", "shoes", "bag", "accessory", "hosiery")


class WardrobeItem(BaseModel):
    id: str
    name: str
    category: Literal[CATEGORIES]
    color: str
    season: list[Season] = Field(min_length=1)
    store_product: Optional[str] = None          # Shopify product gid when the piece is sold in the store
    prompt_description: Optional[str] = None     # store pieces: exact look, written from the listing photo
    reference_images: list[str] = []            # store pieces: the listing photo of this color
    outdoor_only: bool = False                   # e.g. sunglasses: only planned for outdoor spots
    open_toe: bool = False                       # never outdoors in fall or winter
    occasion: list[Literal["day", "night"]] = ["day", "night"]  # night-only pieces never go on a coffee run

    @model_validator(mode="after")
    def _store_pieces_need_photo(self):
        if self.store_product and (not self.reference_images or not self.prompt_description):
            raise ValueError(f"{self.id}: a store piece needs reference_images and a prompt_description")
        return self


class Wardrobe(Approval):
    items: list[WardrobeItem]

    @model_validator(mode="after")
    def _enough_to_vary(self):
        ids = [i.id for i in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("wardrobe ids must be unique")
        for season in ("spring", "summer", "fall", "winter"):
            fits = [i for i in self.items if "all" in i.season or season in i.season]
            for need in (("top", "knitwear"), ("bottom",), ("shoes",)):
                if sum(i.category in need for i in fits) < 3:
                    raise ValueError(f"{season}: needs at least 3 items in {'/'.join(need)} so outfits can vary")
        return self


class Product(BaseModel):
    id: str
    shopify_gid: str
    name: str
    prompt_description: str
    reference_images: list[str] = Field(min_length=1)
    colors_count: Optional[int]
    facts: list[str] = Field(min_length=1)


class Products(Approval):
    items: list[Product] = Field(min_length=1)


class Series(BaseModel):
    id: str
    name: str
    pillar: Literal["value", "product"]
    premise: str
    episode_title: str
    rooms: list[str] = Field(min_length=1)
    cta: Literal["none", "soft", "product"]
    occasion: Literal["day", "night"] = "day"   # night series get night outfits and evening light
    weekdays: list[Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]] = []  # pinned days (empty = rotation)
    slots: list[str] = []                       # pinned times on those days


class SeriesSet(Approval):
    items: list[Series] = Field(min_length=1)


MODELS = {"rules": Rules, "character": Character, "world": World, "wardrobe": Wardrobe, "products": Products,
          "series": SeriesSet}


class BibleError(Exception):
    pass


def load(folder: Path = BIBLE):
    """Return {name: model}. Raises BibleError listing every problem across all files."""
    out, errors = {}, []
    lock = read_lock(folder)
    for name in FILES:
        path = folder / f"{name}.yaml"
        if not path.exists():
            errors.append(f"{name}.yaml: missing")
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            out[name] = MODELS[name].model_validate(data)
            if out[name].status == "approved" and out[name].approved_hash != content_hash(data):
                out[name] = out[name].model_copy(update={"status": "draft", "changed_since_approval": True})
            entry = lock.get(name)
            if out[name].status == "approved" and entry and entry.get("approved_hash") == out[name].approved_hash:
                now = assets_lock(folder.parents[1], asset_paths(data))
                changed = sorted(f for f in set(now["files"]) | set(entry["files"])
                                 if now["files"].get(f) != entry["files"].get(f))
                out[name] = out[name].model_copy(update={"assets_locked": True, "changed_assets": changed}
                                                 | ({"status": "draft", "changed_since_approval": True} if changed else {}))
        except ValidationError as e:
            errors += [f"{name}.yaml: {'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in e.errors()]
    if errors:
        raise BibleError("\n".join(errors))
    _cross_check(out, folder)
    return out


def _cross_check(b, folder):
    errors = []
    room_ids = {r.id for r in b["world"].rooms}
    for s in b["series"].items:
        errors += [f"series {s.id}: unknown room {r}" for r in s.rooms if r not in room_ids]
    hub = folder.parents[1]
    for p in b["products"].items:
        errors += [f"product {p.id}: missing image {img}" for img in p.reference_images if not (hub / img).exists()]
    for img in b["character"].face_refs:
        if not (hub / img).exists():
            errors.append(f"character: missing face image {img}")
    for r in b["world"].rooms:
        errors += [f"room {r.id}: missing image {img}" for img in r.ref_images if not (hub / img).exists()]
    for i in b["wardrobe"].items:
        errors += [f"wardrobe {i.id}: missing image {img}" for img in i.reference_images if not (hub / img).exists()]
    if errors:
        raise BibleError("\n".join(errors))


def selling(b):
    return b["rules"].mix.product_share_max > 0


def unapproved(b):
    return [name for name in FILES if b[name].status != "approved" and (name != "products" or selling(b))]


def require_approved(b):
    missing = unapproved(b)
    tpl = template_status()
    if tpl["changed"]:
        missing.append("templates (changed since approval: " + ", ".join(tpl["changed"]) + ")")
    if missing:
        raise BibleError("Production needs every bible file approved by the owner. Still draft: " + ", ".join(missing)
                         + ". Use --test for test runs (their videos can never be approved for posting).")
