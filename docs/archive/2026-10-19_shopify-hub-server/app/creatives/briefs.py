"""Creative briefs and deterministic variants.

A brief describes *what* to make; ``make_variants`` turns it into N concrete generation
requests by rotating through the lists you give (hooks, avatars, angles...). Each variant
carries its **traits** -- the categorical features stored in ``creative_traits`` that the
Phase 7 model learns from -- so every creative is labelled the moment it's created.

Vocabulary is free-form but should stay consistent (``problem_solution`` every time, not
``problem/solution`` once), because the ML features are exact strings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle, islice
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ASPECTS = {
    "9:16": "vertical 9:16",
    "1:1": "square 1:1",
    "4:5": "portrait 4:5",
    "16:9": "horizontal 16:9",
}


class CreativeBrief(BaseModel):
    """What to make. Lists rotate across variants; scalars apply to all."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["video", "image"] = "video"
    product_id: int | None = Field(default=None, description="hub product id (products.id)")
    product_name: str | None = Field(default=None, description="filled from the product if omitted")
    angles: list[str] = Field(default_factory=lambda: ["benefit"], min_length=1)
    hook_types: list[str] = Field(default_factory=lambda: ["problem_solution"], min_length=1)
    avatar_types: list[str] = Field(default_factory=lambda: ["woman_25_34"], min_length=1)
    hooks: list[str] = Field(default_factory=list, description="literal opening lines, optional")
    aspect_ratio: Literal["9:16", "1:1", "4:5", "16:9"] = "9:16"
    duration_seconds: int = Field(default=8, ge=2, le=60)
    voiceover: bool = True
    cta: str = "shop_now"
    style: str = "authentic handheld UGC, natural light, phone camera, no text overlays"
    notes: str | None = None
    reference_image_url: str | None = Field(
        default=None, description="product photo for image-to-video"
    )
    model: str | None = Field(default=None, description="Higgsfield model id; defaults per kind")
    extra_params: dict[str, Any] = Field(
        default_factory=dict, description="model-specific fields, passed through"
    )
    parent_creative_id: int | None = Field(
        default=None, description="iterate on an existing creative"
    )

    @field_validator("angles", "hook_types", "avatar_types", "hooks")
    @classmethod
    def _slugs(cls, v: list[str]) -> list[str]:
        return [s.strip() for s in v if s and s.strip()]


@dataclass
class VariantSpec:
    index: int
    prompt: str
    params: dict[str, Any]
    traits: dict[str, Any]
    extra_traits: dict[str, Any] = field(default_factory=dict)


def length_bucket(kind: str, seconds: int | float | None) -> str:
    if kind == "image" or not seconds:
        return "static"
    s = float(seconds)
    if s <= 8:
        return "0-8s"
    if s <= 15:
        return "9-15s"
    if s <= 30:
        return "16-30s"
    if s <= 60:
        return "31-60s"
    return "60s+"


def _humanize(slug: str) -> str:
    return slug.replace("_", " ").replace("-", " ")


def build_prompt(
    brief: CreativeBrief, angle: str, hook_type: str, avatar: str, hook_line: str | None
) -> str:
    product = brief.product_name or "the product"
    if brief.kind == "video":
        parts = [
            f"{ASPECTS[brief.aspect_ratio]} user-generated-content style video, about {brief.duration_seconds} seconds.",
            f"A {_humanize(avatar)} creator speaks to the camera about {product}.",
            f"Opening hook ({_humanize(hook_type)}): "
            + (f'"{hook_line}".' if hook_line else "grab attention in the first 2 seconds."),
            f"Angle: {_humanize(angle)}.",
            "Natural voiceover in the creator's voice."
            if brief.voiceover
            else "No voiceover; visual storytelling only.",
            f"Ends with a clear call to action: {_humanize(brief.cta)}.",
            f"Style: {brief.style}.",
        ]
    else:
        parts = [
            f"{ASPECTS[brief.aspect_ratio]} photo, user-generated-content style, of a {_humanize(avatar)} using {product}.",
            f"Angle: {_humanize(angle)}. Hook: {_humanize(hook_type)}"
            + (f' -- "{hook_line}".' if hook_line else "."),
            f"Style: {brief.style}.",
        ]
    if brief.notes:
        parts.append(brief.notes)
    return " ".join(parts)


def make_variants(brief: CreativeBrief, n: int, default_model: str) -> list[VariantSpec]:
    """N variants rotating angles x hook types x avatars (and literal hooks if given).

    Deterministic: the same brief + n always yields the same variants, so a retried
    request can't create a different set.
    """
    if n < 1 or n > 20:
        raise ValueError("n must be between 1 and 20")
    combos = [(a, h, v) for h in brief.hook_types for a in brief.angles for v in brief.avatar_types]
    hooks = brief.hooks or [None]  # type: ignore[list-item]
    model = brief.model or default_model
    out = []
    for i, ((angle, hook_type, avatar), hook_line) in enumerate(
        islice(zip(cycle(combos), cycle(hooks)), n)
    ):
        prompt = build_prompt(brief, angle, hook_type, avatar, hook_line)
        params: dict[str, Any] = {"prompt": prompt, "aspect_ratio": brief.aspect_ratio}
        if brief.kind == "video":
            params["duration"] = brief.duration_seconds
        if brief.reference_image_url:
            params["image_url"] = brief.reference_image_url
        params |= brief.extra_params
        traits = {
            "hook_type": hook_type,
            "avatar_type": avatar,
            "length_bucket": length_bucket(brief.kind, brief.duration_seconds),
            "product_id": brief.product_id,
            "voiceover": brief.voiceover if brief.kind == "video" else None,
            "format": f"{brief.aspect_ratio.replace(':', 'x')}_ugc_{brief.kind}",
            "angle": angle,
            "cta": brief.cta,
        }
        extra = {
            "model": model,
            "variant_index": i,
            "hook_line": hook_line,
            "style": brief.style,
            "has_reference_image": bool(brief.reference_image_url),
        }
        out.append(
            VariantSpec(index=i, prompt=prompt, params=params, traits=traits, extra_traits=extra)
        )
    return out
