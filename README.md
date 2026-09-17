# far-art

**Free art repo. Style is the gate. Prompt is not.**

Stills, comics boards (spatial, not editorial cut), style sheets,
drawing-app specs, web UI/UX kits, 3D, architecture massing,
art-history constraint lists.

This is a sister repo to `the-far-queen/fieldcore` (geometry + math) and
`the-far-queen/simself` (identity + kernel). far-art handles the *style
substrate*: the named axes, sheets, and gates that AI image generators
and human illustrators both need.

## What this repo is

- A free, public domain art substrate for AI-assisted illustration.
- A 56-axis style schema that refuses house-style drift.
- A gate (commit_asset) that no image enters without a style sheet.
- A growing library of sheets, comics boards, UI kits, 3D plans.

## What this repo is not

- A prompt collection. (Prompts are noise without axes.)
- A video repo. (Sequences belong in `the-far-queen/far-film`.)
- A model zoo. (Models belong upstream; we use the open ones.)
- A house-style. (The whole point is *named* style, not default look.)

## AGENTS.md

The schema lives in [AGENTS.md](./AGENTS.md). Read it first. The seven
groups of axes (Medium, Mark, Space, Light, Language of pictures,
Citation, Pipeline) are the contract.

## Repo layout

```
far-art/
├── AGENTS.md                # the 56-axis schema (this is the contract)
├── README.md                # this file
├── LICENSE                  # MIT
├── sheets/                  # style sheets (YAML / JSON, hashed)
│   ├── by-genre/
│   ├── by-period/
│   └── by-tool/
├── boards/                  # comics boards (spatial, not editorial cut)
├── ui-kits/                 # web UI/UX kits
├── 3d/                      # 3D stills + plans
├── architecture/            # massing + plans
├── history/                 # art-history constraint lists (period_cite)
├── tests/                   # R1..R5 sheet/gate tests
├── tools/                   # sheet.compile, still.generate, board.from_script
└── examples/                # example sheets + renders
```

## Quick start

```bash
git clone https://github.com/the-far-queen/far-art.git
cd far-art
# Read AGENTS.md
# Pick a sheet from sheets/by-genre/
# Compile a variant: python tools/compile_sheet.py path/to/sheet.yaml
# Generate: still.generate(sheet, span) -- your image tool, gated
```

## License

MIT. Free for all agents, human and non-human. No copyright trap.
No paywall. No "research only" carve-out. Style axes belong to everyone.

## Sister repos

- [the-far-queen/fieldcore](https://github.com/the-far-queen/fieldcore) — geometry + math substrate
- [the-far-queen/simself](https://github.com/the-far-queen/simself) — identity + kernel
- `the-far-queen/far-film` — coming: video sequences + shots
