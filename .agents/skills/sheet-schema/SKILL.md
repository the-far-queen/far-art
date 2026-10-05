---
name: sheet-schema
description: >-
  Use when the user wants to compile an art style sheet, run the R gate, or load the 56-axis
  style contract. Triggers: "style sheet", "sheet axes", "compile sheet", "R gate",
  "met open access", "sdxl", "flux".
---

# Sheet schema (far-art)

The style sheet is the **canonical unit** of art in this repo. Every sheet is a frozen dataclass with a deterministic id.

## Compile

```python
from far_art.tools.sheet import compile_sheet, gate

sheet = compile_sheet({
    "medium": "still",
    "tool_id": "sdxl-1.0",
    "aspect": "16:9",
    "line": "ink",
    "weight": 1.0,
    "value_min": 0.0, "value_max": 1.0,
    "chroma": 0.5,
    "palette_lock": ["#1a1a2e", "#e94560", "#f8f5f0"],
    "perspective": "1pt",
    "lens_mm": 50,
    "light_logic": "natural",
    "key_dir": "three_quarter",
    "contrast": 0.5,
    "composition_grid": "rule_of_thirds",
    "a11y_contrast": 4.5,
    "forbidden_motifs": [],
    "upscale_policy": "none",
    "inpaint_policy": "forbid",
    "commit_asset": "gate",
    "ground_touch": "forbid",
})
```

The sheet_id is `sha256(canonical(axes))[:16]`. Same axes → same id.

## Gate

```python
allow, reason = sheet.gate(sheet, asset_text="...")
```

`commit_asset="gate"` refuses:
- naked images (no sheet) → `no_sheet`
- stills/3d/comics that touch ground (default policy) → `ground_touch_not_forbidden`
- forbidden motifs matched in asset text → `forbidden_motif:<term>`
- WCAG contrast below 3.0 → `a11y_contrast_too_low`

## Public-domain sources

See `docs/sources.md` in the repo. Met Open Access (CC0, 375k images) + pdimagearchive + gutenberg illustrations + wikimedia commons + public domain review.

## See also

- `AGENTS.md` in the repo — the contract (56 axes, 7 groups)
- `tools/gate.py` — CLI gate check
- `tools/compile_sheet.py` — CLI compile
- `examples/7-stills-3-sheets-radio-western-2026-09-17.md` — worked example