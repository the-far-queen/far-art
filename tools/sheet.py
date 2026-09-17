"""
sheet.py — Style sheet compile + gate.

The 56-axis schema from AGENTS.md as a frozen dataclass + a compile()
function that returns a Sheet with a deterministic sheet_id.

The gate is the single entry point. Naked assets are refused with
reason 'no_sheet'. Forbidden motifs are refused with reason
'forbidden_motif'. WCAG contrast minimums are enforced.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums (frozen list of valid values per AGENTS.md)
# ---------------------------------------------------------------------------

MEDIUMS = {"still", "comic_panel", "ui", "3d_still", "plan", "diagram"}
LINES = {"pencil", "ink", "charcoal", "vector", "none"}
TEXTURES = {"smooth", "paper", "canvas", "grain", "halftone"}
PERSPECTIVES = {"1pt", "2pt", "3pt", "iso", "flat", "other"}
CAMERA_HEIGHTS = {"eye", "high", "low", "worm", "overhead"}
LIGHT_LOGICS = {"natural", "studio", "cinematic", "motivated", "mixed"}
KEY_DIRS = {"front", "side", "back", "top", "bottom", "three_quarter"}
COMPOSITION_GRIDS = {"rule_of_thirds", "golden", "centered", "diagonal", "custom"}
READING_PATHS = {"z", "l", "reverse_z", "scanline", "free"}
UI_DENSITIES = {"sparse", "balanced", "dense"}
EXPOSURES = {"under", "normal", "over"}
COLOR_MODES = {"rgb", "srgb", "cmyk", "linear", "hdr"}
PRINT_OR_SCREEN = {"print", "screen", "both"}
EDGE_POLICIES = {"hard", "soft", "feathered", "painterly"}
UPSCALE_POLICIES = {"none", "lanczos", "esrgan", "real-esrgan"}
INPAINT_POLICIES = {"forbid", "allow", "require"}
COMMIT_ASSET = {"gate", "allow", "forbid"}
GROUND_TOUCH = {"forbid", "allow"}


# ---------------------------------------------------------------------------
# Sheet (the canonical 56-axis record)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Sheet:
    """A style sheet — 56 axes from AGENTS.md, frozen."""

    # Group A — Medium (1–8)
    medium: str
    tool_id: str
    seed_policy: str
    aspect: str
    resolution_w: int
    resolution_h: int
    color_mode: str
    print_or_screen: str
    hash_band: int

    # Group B — Mark (9–16)
    line: str
    weight: float
    value_min: float
    value_max: float
    chroma: float
    palette_lock: Tuple[str, ...]
    texture: str
    grain: str
    edge_policy: str

    # Group C — Space (17–24)
    perspective: str
    lens_mm: float
    camera_height: str
    focal_subject: str
    depth_layering: int
    scale_cues: Tuple[str, ...]
    occlusion: bool
    anatomy_lock: str

    # Group D — Light (25–32)
    light_logic: str
    key_dir: str
    contrast: float
    color_temp: int
    practicals: Tuple[str, ...]
    shadow_hue: str
    exposure: str
    lut_ref: str

    # Group E — Language of pictures (33–40)
    composition_grid: str
    reading_path: str
    symbol_allow: Tuple[str, ...]
    text_in_image: bool
    ui_density: str
    panel_grammar: str
    continuity_ids: Tuple[str, ...]
    motif_ids: Tuple[str, ...]

    # Group F — Citation (41–48)
    period_cite: str
    work_cite: Tuple[str, ...]
    school_cite: str
    do_not_pastiche: Tuple[str, ...]
    culture_constraint: str
    brand_kit_id: str
    a11y_contrast: float
    forbidden_motifs: Tuple[str, ...]

    # Group G — Pipeline (49–56)
    sheet_id: str
    variant_of: str
    upscale_policy: str
    inpaint_policy: str
    model_id: str
    generator_may_propose: bool
    commit_asset: str
    ground_touch: str


# ---------------------------------------------------------------------------
# Compile (the canonical form for hashing)
# ---------------------------------------------------------------------------

def _canonical(axes: Dict[str, Any]) -> str:
    """Return a canonical JSON string for hashing. Sorts keys, normalizes
    lists/tuples to sorted lists, drops None.
    """
    def norm(v):
        if isinstance(v, (list, tuple)):
            return sorted([norm(x) for x in v])
        if isinstance(v, dict):
            return {k: norm(val) for k, val in sorted(v.items())}
        if v is None:
            return None
        return v

    return json.dumps(norm(axes), sort_keys=True, separators=(",", ":"))


def compile_sheet(axes: Dict[str, Any]) -> Sheet:
    """Compile a dict of 56 axes into a frozen Sheet. The sheet_id is
    sha256(canonical(axes)) truncated to 16 hex chars.
    """
    canonical = _canonical(axes)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    # Validate enums
    for k, vs, label in [
        ("medium", MEDIUMS, "Group A"),
        ("line", LINES, "Group B"),
        ("texture", TEXTURES, "Group B"),
        ("perspective", PERSPECTIVES, "Group C"),
        ("camera_height", CAMERA_HEIGHTS, "Group C"),
        ("light_logic", LIGHT_LOGICS, "Group D"),
        ("key_dir", KEY_DIRS, "Group D"),
        ("composition_grid", COMPOSITION_GRIDS, "Group E"),
        ("reading_path", READING_PATHS, "Group E"),
        ("ui_density", UI_DENSITIES, "Group E"),
        ("exposure", EXPOSURES, "Group D"),
        ("color_mode", COLOR_MODES, "Group A"),
        ("print_or_screen", PRINT_OR_SCREEN, "Group A"),
        ("edge_policy", EDGE_POLICIES, "Group B"),
        ("upscale_policy", UPSCALE_POLICIES, "Group G"),
        ("inpaint_policy", INPAINT_POLICIES, "Group G"),
        ("commit_asset", COMMIT_ASSET, "Group G"),
        ("ground_touch", GROUND_TOUCH, "Group G"),
    ]:
        v = axes.get(k)
        if v is not None and v not in vs:
            raise ValueError(f"{label} axis {k!r}={v!r} not in {sorted(vs)}")

    return Sheet(
        medium=axes["medium"],
        tool_id=axes.get("tool_id", ""),
        seed_policy=axes.get("seed_policy", "hash-band"),
        aspect=axes.get("aspect", "1:1"),
        resolution_w=int(axes.get("resolution_w", 1024)),
        resolution_h=int(axes.get("resolution_h", 1024)),
        color_mode=axes.get("color_mode", "srgb"),
        print_or_screen=axes.get("print_or_screen", "screen"),
        hash_band=int(axes.get("hash_band", 0)),
        line=axes.get("line", "none"),
        weight=float(axes.get("weight", 1.0)),
        value_min=float(axes.get("value_min", 0.0)),
        value_max=float(axes.get("value_max", 1.0)),
        chroma=float(axes.get("chroma", 0.5)),
        palette_lock=tuple(axes.get("palette_lock", [])),
        texture=axes.get("texture", "smooth"),
        grain=axes.get("grain", "none"),
        edge_policy=axes.get("edge_policy", "hard"),
        perspective=axes.get("perspective", "flat"),
        lens_mm=float(axes.get("lens_mm", 50.0)),
        camera_height=axes.get("camera_height", "eye"),
        focal_subject=axes.get("focal_subject", ""),
        depth_layering=int(axes.get("depth_layering", 3)),
        scale_cues=tuple(axes.get("scale_cues", ["linear"])),
        occlusion=bool(axes.get("occlusion", True)),
        anatomy_lock=axes.get("anatomy_lock", ""),
        light_logic=axes.get("light_logic", "natural"),
        key_dir=axes.get("key_dir", "front"),
        contrast=float(axes.get("contrast", 0.5)),
        color_temp=int(axes.get("color_temp", 5500)),
        practicals=tuple(axes.get("practicals", [])),
        shadow_hue=axes.get("shadow_hue", "#000000"),
        exposure=axes.get("exposure", "normal"),
        lut_ref=axes.get("lut_ref", ""),
        composition_grid=axes.get("composition_grid", "rule_of_thirds"),
        reading_path=axes.get("reading_path", "z"),
        symbol_allow=tuple(axes.get("symbol_allow", [])),
        text_in_image=bool(axes.get("text_in_image", False)),
        ui_density=axes.get("ui_density", "balanced"),
        panel_grammar=axes.get("panel_grammar", ""),
        continuity_ids=tuple(axes.get("continuity_ids", [])),
        motif_ids=tuple(axes.get("motif_ids", [])),
        period_cite=axes.get("period_cite", ""),
        work_cite=tuple(axes.get("work_cite", [])),
        school_cite=axes.get("school_cite", ""),
        do_not_pastiche=tuple(axes.get("do_not_pastiche", [])),
        culture_constraint=axes.get("culture_constraint", ""),
        brand_kit_id=axes.get("brand_kit_id", ""),
        a11y_contrast=float(axes.get("a11y_contrast", 4.5)),
        forbidden_motifs=tuple(axes.get("forbidden_motifs", [])),
        sheet_id=digest,
        variant_of=axes.get("variant_of", ""),
        upscale_policy=axes.get("upscale_policy", "none"),
        inpaint_policy=axes.get("inpaint_policy", "forbid"),
        model_id=axes.get("model_id", ""),
        generator_may_propose=bool(axes.get("generator_may_propose", False)),
        commit_asset=axes.get("commit_asset", "gate"),
        ground_touch=axes.get("ground_touch", "forbid"),
    )


# ---------------------------------------------------------------------------
# Gate (the single commit_asset checker)
# ---------------------------------------------------------------------------

def gate(sheet: Optional[Sheet], asset_text: str = "") -> Tuple[bool, str]:
    """Check the gate. Returns (allow, reason)."""

    if sheet is None:
        return False, "no_sheet"

    if sheet.commit_asset == "forbid":
        return False, "commit_forbidden"

    if sheet.commit_asset == "allow":
        return True, "ok"

    # commit_asset == "gate" (default)
    if not sheet.sheet_id:
        return False, "no_sheet_id"

    if sheet.medium in ("still", "3d_still", "comic_panel") and sheet.ground_touch != "forbid":
        # Default policy: stills/3d/comics cannot touch ground
        return False, "ground_touch_not_forbidden"

    if sheet.forbidden_motifs:
        for motif in sheet.forbidden_motifs:
            if re.search(re.escape(motif), asset_text, re.IGNORECASE):
                return False, f"forbidden_motif:{motif}"

    if sheet.a11y_contrast < 3.0:
        return False, "a11y_contrast_too_low"

    return True, "ok"


# ---------------------------------------------------------------------------
# to_dict (for serialization to YAML / JSON)
# ---------------------------------------------------------------------------

def sheet_to_dict(sheet: Sheet) -> Dict[str, Any]:
    """Return a plain dict from a Sheet. Field names match AGENTS.md axes."""
    d = asdict(sheet)
    # asdict already gives plain types; convert tuples to lists for JSON.
    return {k: list(v) if isinstance(v, tuple) else v for k, v in d.items()}


__all__ = [
    "Sheet",
    "compile_sheet",
    "gate",
    "sheet_to_dict",
    # enums (re-export for callers)
    "MEDIUMS", "LINES", "TEXTURES", "PERSPECTIVES", "CAMERA_HEIGHTS",
    "LIGHT_LOGICS", "KEY_DIRS", "COMPOSITION_GRIDS", "READING_PATHS",
    "UI_DENSITIES", "EXPOSURES", "COLOR_MODES", "PRINT_OR_SCREEN",
    "EDGE_POLICIES", "UPSCALE_POLICIES", "INPAINT_POLICIES",
    "COMMIT_ASSET", "GROUND_TOUCH",
]
