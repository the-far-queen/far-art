# sheets/

Style sheets, organized by intent.

## Layout

```
sheets/
├── by-genre/        # sheets grouped by genre (comic, ui, still, plan)
├── by-period/       # sheets grouped by historical period
└── by-tool/         # sheets grouped by tool/model
```

## Sheet format

JSON or minimal YAML. Field names match the 56 axes in AGENTS.md.

A sheet must:

- have a `medium` (Group A, axis 01)
- have a `commit_asset` policy (Group G, axis 55)
- pass the gate (tools/gate.py)
- have a deterministic `sheet_id` (sha256 of canonical axes)

## Adding a sheet

```bash
# 1. Write your sheet (use examples/tonalist-landscape-16x9.json as a template)
# 2. Compile
python tools/compile_sheet.py sheets/by-genre/your-sheet.json
# 3. Gate
python tools/gate.py sheets/by-genre/your-sheet.json
# 4. Commit. The gate result is your proof.
```

## What is NOT here

- Naked assets (image files without a sheet).
- Video sequences. Those belong in `the-far-queen/far-film`.
- Prompts without axes.
- Vibe paragraphs.
