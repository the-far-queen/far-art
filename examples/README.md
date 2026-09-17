# Examples

Sheets that compile, gate, and pass the R1..R5 tests.

## Usage

```bash
# Compile a sheet
python tools/compile_sheet.py examples/tonalist-landscape-16x9.json

# Check the gate (refuses if forbidden motifs in asset)
python tools/gate.py examples/tonalist-landscape-16x9.json
```

## Sheets

- `tonalist-landscape-16x9.json` — Tonalist landscape, 16:9, 1920×1080.
  - Forbidden motifs: blood, skull.
  - ground_touch: forbid (still cannot touch ground).
  - palette_lock: 4 muted earth tones.

## Adding a new sheet

1. Copy `tonalist-landscape-16x9.json` to a new file.
2. Change `medium`, `aspect`, `tool_id`, palette, and forbidden motifs.
3. Run `python tools/compile_sheet.py your-sheet.json`.
4. Verify the `sheet_id` looks right (16 hex chars).
5. Run `python tools/gate.py your-sheet.json` to confirm the gate passes.
6. Commit. No naked assets in the commit.
