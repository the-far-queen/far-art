# AGENTS.md — ( far-art repo )

> A prompt is not a style sheet.

This file is the contract. Every commit_asset gate checks against it.
Every style sheet references it. Every test (R1..R5) reads it.

If you change the schema, update AGENTS.md first. The repo is downstream
of this file.

## What this repo is

Stills, comics boards (spatial, not editorial cut), style sheets,
drawing-app specs, web UI/UX kits, 3D, architecture massing,
art-history constraint lists.

## Packet

```
style  Sheet | Board | AssetRef
```

**No asset without `sheet_id` + `hash`.** The gate refuses naked assets.

## Error this repo exists to stop

Conflating every image prompt into one house look.
**"Make it cinematic" is not an axis.** Lens, grain, LUT-ref, and blocking are.

## Art intake — 56 axes

### Group A — Medium (1–8)

| # | Axis | Type | Notes |
|---|---|---|---|
| 01 | medium | enum | `{still, comic_panel, ui, 3d_still, plan, diagram}` |
| 02 | tool_id | string | generator / model id, e.g. `sdxl-1.0`, `flux-dev`, `krita-pencil` |
| 03 | seed_policy | string | how seeds are assigned (deterministic, hash-band, free) |
| 04 | aspect | ratio | e.g. `16:9`, `1:1`, `2.39:1` |
| 05 | resolution | `{w,h}` | pixel dimensions |
| 06 | color_mode | enum | `{rgb, srgb, cmyk, linear, hdr}` |
| 07 | print_or_screen | enum | `{print, screen, both}` |
| 08 | hash_band | int | which hash band the asset lives in |

### Group B — Mark (9–16)

| # | Axis | Type | Notes |
|---|---|---|---|
| 09 | line | enum | `{pencil, ink, charcoal, vector, none}` |
| 10 | weight | float | line thickness (pt or px) |
| 11 | value_range | `{min,max}` | luma range |
| 12 | chroma | float | saturation level |
| 13 | palette_lock[] | color[] | restricted palette (hex) |
| 14 | texture | enum | `{smooth, paper, canvas, grain, halftone}` |
| 15 | grain | enum | `{none, fine, medium, heavy}` |
| 16 | edge_policy | enum | `{hard, soft, feathered, painterly}` |

### Group C — Space (17–24)

| # | Axis | Type | Notes |
|---|---|---|---|
| 17 | perspective | enum | `{1pt, 2pt, 3pt, iso, flat, other}` |
| 18 | lens_mm | float | for still camera; film coverage is far-film |
| 19 | camera_height | enum | `{eye, high, low, worm, overhead}` |
| 20 | focal_subject | string | what's in focus |
| 21 | depth_layering | int | number of depth planes |
| 22 | scale_cues | string[] | which cues are used (`{occlusion, atmospheric, linear}`) |
| 23 | occlusion | bool | does nearer stuff occlude farther |
| 24 | anatomy_lock | string | anatomy convention / reference |

### Group D — Light (25–32)

| # | Axis | Type | Notes |
|---|---|---|---|
| 25 | light_logic | enum | `{natural, studio, cinematic, motivated, mixed}` |
| 26 | key_dir | enum | `{front, side, back, top, bottom, three_quarter}` |
| 27 | contrast | float | 0..1 |
| 28 | color_temp | int | Kelvin |
| 29 | practicals | string[] | visible light sources in frame |
| 30 | shadow_hue | color | shadow tint |
| 31 | exposure | enum | `{under, normal, over}` |
| 32 | lut_ref | string | still grade only — points to LUT file |

### Group E — Language of pictures (33–40)

| # | Axis | Type | Notes |
|---|---|---|---|
| 33 | composition_grid | enum | `{rule_of_thirds, golden, centered, diagonal, custom}` |
| 34 | reading_path | enum | `{z, l, reverse_z, scanline, free}` |
| 35 | symbol_allow | string[] | allowed symbols / motifs |
| 36 | text_in_image | bool | text permitted in image |
| 37 | ui_density | enum | `{sparse, balanced, dense}` (if `medium=ui`) |
| 38 | panel_grammar | string | panel layout convention (if `medium=comic_panel`) |
| 39 | continuity_ids[] | string[] | shared character/object ids for continuity |
| 40 | motif_ids[] | string[] | recurring visual motifs |

### Group F — Citation (41–48)

| # | Axis | Type | Notes |
|---|---|---|---|
| 41 | period_cite | string | historical period referenced |
| 42 | work_cite | string[] | specific works referenced |
| 43 | school_cite | string | school / movement |
| 44 | do_not_pastiche[] | string[] | forbidden pastiche targets |
| 45 | culture_constraint | string | cultural constraints / sensitivities |
| 46 | brand_kit_id | string | brand kit (if commercial) |
| 47 | a11y_contrast | float | WCAG contrast minimum |
| 48 | forbidden_motifs[] | string[] | motifs refused at the gate |

### Group G — Pipeline (49–56)

| # | Axis | Type | Notes |
|---|---|---|---|
| 49 | sheet_id | string | unique id, sha256 of axes |
| 50 | variant_of | string | parent sheet id (if variant) |
| 51 | upscale_policy | enum | `{none, lanczos, esrgan, real-esrgan}` |
| 52 | inpaint_policy | enum | `{forbid, allow, require}` |
| 53 | model_id | string | upstream model id |
| 54 | generator_may_propose | bool | can the generator propose axis changes? |
| 55 | commit_asset | enum | `{gate, allow, forbid}` |
| 56 | ground_touch | enum | `{forbid, allow}` |

## Surface

```python
sheet.compile(axes)         -> Sheet
still.generate(sheet, span)
board.from_script(scene_units)   # spatial boards only
ui.kit(sheet)
spatial.massing(sheet, program)
history.cite(...)           -> constraints
```

## Gate

`commit_asset` defaults to `{gate}`. The gate checks:

1. `sheet_id` is set.
2. `sheet_id == sha256(canonical(axes))`.
3. `variant_of` (if set) is a known parent.
4. `ground_touch == forbid` for `medium ∈ {still, 3d_still, comic_panel}` by default.
5. No forbidden_motifs present (axis 48).
6. WCAG contrast minimum met (axis 47).

A naked asset (no sheet) is refused with reason `no_sheet`.

## Tests

| # | Test | What it checks |
|---|---|---|
| R1 | repro hash/band | Sheet with same axes → same `sheet_id`; different axes → different `sheet_id`. |
| R2 | forbidden motif rejected | Sheet with `forbidden_motifs=[x]` + asset containing `x` → refused. |
| R3 | board ids survive restart | `board.from_script(...)` then re-load → all `continuity_ids[]` and `motif_ids[]` preserved. |
| R4 | two different 09–16 settings cannot share a sheet hash | Vary line/weight/value_range/chroma/palette_lock/texture/grain/edge → different `sheet_id`. |
| R5 | prompt with sheet unset does not apply house look | Naked prompt + gate → refused, no fallback to default. |

## Anti-patterns

- **House-style default.** Refused.
- **Video sequences in this repo.** Send to far-film.
- **Vibe paragraphs without axes.** Refused.
- **"Make it cinematic" / "make it pop" / "make it epic" without named axes.** Refused.

## Related

- [fieldcore/docs/](../../fieldcore/blob/main/docs/) — geometry + math substrate
- [simself/docs/](../../simself/blob/main/docs/) — identity + kernel
- `the-far-queen/far-film` — coming: video sequences + shots

## License

MIT. Free for all agents, human and non-human.
