"""
test_sheet.py — R1..R5 tests for the far-art sheet schema.

R1: same axes → same sheet_id; different axes → different sheet_id.
R2: forbidden motif in asset → refused with reason forbidden_motif.
R3: board ids survive restart (continuity_ids + motif_ids preserved).
R4: two different 09-16 settings cannot share a sheet_id hash.
R5: naked asset (no sheet) → refused with reason no_sheet.

Run:
    python -m pytest tests/test_sheet.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
sys.path.insert(0, str(TOOLS))

from sheet import compile_sheet, gate, sheet_to_dict  # noqa: E402


# Minimal valid axes (covers all 56 fields with sensible defaults)
def _base_axes(**overrides):
    base = {
        "medium": "still",
        "tool_id": "test",
        "seed_policy": "hash-band",
        "aspect": "1:1",
        "resolution_w": 1024,
        "resolution_h": 1024,
        "color_mode": "srgb",
        "print_or_screen": "screen",
        "hash_band": 0,
        "line": "none",
        "weight": 1.0,
        "value_min": 0.0,
        "value_max": 1.0,
        "chroma": 0.5,
        "palette_lock": [],
        "texture": "smooth",
        "grain": "none",
        "edge_policy": "hard",
        "perspective": "flat",
        "lens_mm": 50.0,
        "camera_height": "eye",
        "focal_subject": "test",
        "depth_layering": 3,
        "scale_cues": ["linear"],
        "occlusion": True,
        "anatomy_lock": "",
        "light_logic": "natural",
        "key_dir": "front",
        "contrast": 0.5,
        "color_temp": 5500,
        "practicals": [],
        "shadow_hue": "#000000",
        "exposure": "normal",
        "lut_ref": "",
        "composition_grid": "rule_of_thirds",
        "reading_path": "z",
        "symbol_allow": [],
        "text_in_image": False,
        "ui_density": "balanced",
        "panel_grammar": "",
        "continuity_ids": ["char-001", "obj-door-001"],
        "motif_ids": ["motif-circle", "motif-line"],
        "period_cite": "",
        "work_cite": [],
        "school_cite": "",
        "do_not_pastiche": [],
        "culture_constraint": "",
        "brand_kit_id": "",
        "a11y_contrast": 4.5,
        "forbidden_motifs": [],
        "variant_of": "",
        "upscale_policy": "none",
        "inpaint_policy": "forbid",
        "model_id": "",
        "generator_may_propose": False,
        "commit_asset": "gate",
        "ground_touch": "forbid",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# R1 — repro hash/band
# ---------------------------------------------------------------------------

def test_r1_same_axes_same_sheet_id():
    a = compile_sheet(_base_axes())
    b = compile_sheet(_base_axes())
    assert a.sheet_id == b.sheet_id
    assert len(a.sheet_id) == 16  # truncated sha256


def test_r1_different_axes_different_sheet_id():
    a = compile_sheet(_base_axes(line="ink"))
    b = compile_sheet(_base_axes(line="pencil"))
    assert a.sheet_id != b.sheet_id


def test_r1_hash_band_changes_id():
    a = compile_sheet(_base_axes(hash_band=0))
    b = compile_sheet(_base_axes(hash_band=1))
    assert a.sheet_id != b.sheet_id


# ---------------------------------------------------------------------------
# R2 — forbidden motif rejected
# ---------------------------------------------------------------------------

def test_r2_forbidden_motif_rejected():
    sheet = compile_sheet(_base_axes(forbidden_motifs=["blood"]))
    allow, reason = gate(sheet, "a painting with blood on the floor")
    assert allow is False
    assert reason.startswith("forbidden_motif")


def test_r2_forbidden_motif_case_insensitive():
    sheet = compile_sheet(_base_axes(forbidden_motifs=["BLOOD"]))
    allow, reason = gate(sheet, "Blood everywhere")
    assert allow is False
    assert reason.startswith("forbidden_motif")


def test_r2_no_forbidden_motif_passes():
    sheet = compile_sheet(_base_axes(forbidden_motifs=["blood"]))
    allow, reason = gate(sheet, "a clean white room")
    assert allow is True
    assert reason == "ok"


# ---------------------------------------------------------------------------
# R3 — board ids survive restart
# ---------------------------------------------------------------------------

def test_r3_continuity_ids_preserved():
    a = compile_sheet(_base_axes(continuity_ids=["char-001", "obj-door-001"]))
    d1 = sheet_to_dict(a)

    # "restart": serialize → deserialize via compile
    b = compile_sheet({k: v for k, v in d1.items() if k != "sheet_id"})
    d2 = sheet_to_dict(b)

    assert d2["continuity_ids"] == d1["continuity_ids"]
    assert d2["motif_ids"] == d1["motif_ids"]
    assert d2["sheet_id"] == d1["sheet_id"]  # same axes → same id


def test_r3_motif_ids_preserved():
    a = compile_sheet(_base_axes(motif_ids=["motif-circle", "motif-line", "motif-arrow"]))
    d = sheet_to_dict(a)
    assert d["motif_ids"] == ["motif-circle", "motif-line", "motif-arrow"]


# ---------------------------------------------------------------------------
# R4 — different 09-16 settings → different sheet_id
# ---------------------------------------------------------------------------

def test_r4_line_change_different_id():
    a = compile_sheet(_base_axes(line="ink"))
    b = compile_sheet(_base_axes(line="pencil"))
    assert a.sheet_id != b.sheet_id


def test_r4_weight_change_different_id():
    a = compile_sheet(_base_axes(weight=1.0))
    b = compile_sheet(_base_axes(weight=2.0))
    assert a.sheet_id != b.sheet_id


def test_r4_chroma_change_different_id():
    a = compile_sheet(_base_axes(chroma=0.3))
    b = compile_sheet(_base_axes(chroma=0.7))
    assert a.sheet_id != b.sheet_id


def test_r4_palette_lock_change_different_id():
    a = compile_sheet(_base_axes(palette_lock=["#000000"]))
    b = compile_sheet(_base_axes(palette_lock=["#ffffff"]))
    assert a.sheet_id != b.sheet_id


def test_r4_texture_change_different_id():
    a = compile_sheet(_base_axes(texture="smooth"))
    b = compile_sheet(_base_axes(texture="paper"))
    assert a.sheet_id != b.sheet_id


# ---------------------------------------------------------------------------
# R5 — naked prompt refused
# ---------------------------------------------------------------------------

def test_r5_naked_asset_refused():
    allow, reason = gate(None, "make it cinematic")
    assert allow is False
    assert reason == "no_sheet"


def test_r5_commit_forbidden_refused():
    sheet = compile_sheet(_base_axes(commit_asset="forbid"))
    allow, reason = gate(sheet, "anything")
    assert allow is False
    assert reason == "commit_forbidden"


def test_r5_commit_allowed_passes():
    sheet = compile_sheet(_base_axes(commit_asset="allow"))
    allow, reason = gate(sheet, "anything")
    assert allow is True
    assert reason == "ok"


# ---------------------------------------------------------------------------
# Bonus — gate refuses stills that touch ground
# ---------------------------------------------------------------------------

def test_gate_ground_touch_must_be_forbidden_for_still():
    sheet = compile_sheet(_base_axes(medium="still", ground_touch="allow"))
    allow, reason = gate(sheet, "an image")
    assert allow is False
    assert reason == "ground_touch_not_forbidden"


def test_gate_ground_touch_required_for_ui():
    # ui doesn't have ground-touch restriction by default
    sheet = compile_sheet(_base_axes(medium="ui", ground_touch="allow"))
    allow, reason = gate(sheet, "a wireframe")
    assert allow is True


def test_gate_a11y_too_low_refused():
    sheet = compile_sheet(_base_axes(a11y_contrast=2.0))
    allow, reason = gate(sheet, "low contrast ui")
    assert allow is False
    assert reason == "a11y_contrast_too_low"
