# 7 stills x 3 sheets (far-art example)

**Source:** `C:\Users\Admin\Downloads\1a1a.txt` (Bobby paste 2026-09-17)
**Ingested:** 2026-09-17T09:43:57
**Where:** far-art/examples/

> **Per Bobby:** No house look. Three contracts: **ink-outlaw**,
> **wash-rabbit**, **period-grain**. The 3 sheets = 3 distinct
> `sheet_id`s.

## Three sheets (proposed)

| sheet_id | Style | Subject |
|---|---|---|
| `ink-outlaw-dual` | Black ink comic | Adult gunslinger in sombrero, dual revolvers |
| `wash-rabbit-radio` | Soft watercolor | Rabbit holding two-way radio |
| `period-grain-chair` | B&W archival photo | Empty chair + folded coat + child's cap |

Same subject (radio / western) != same hash B (line, texture,
grain). This is **R4 (two different settings cannot share a sheet
hash)** in image form.

## Stills generated (descriptions)

### ink-outlaw (3 stills)

1. Black and white comic ink illustration, high contrast, clean
   graphic novel linework, skull-faced gunslinger wearing a huge
   battered sombrero, charro jacket with decorative stitching,
   bandolier and knife, firing two revolvers toward the right, one
   arm crossing the face, hatched gray sky panel behind, white
   negative space, no color, no photorealism, adult character.

2. Close-up black and white manga-comic ink crop of an adult skeletal
   gunslinger in a wide sombrero, fierce squint, stitched leather
   jacket and harness, arm across the face aiming a revolver, bold
   blacks, screentone clouds.

3. Black ink comic panel of a serious rabbit in a tiny sombrero and
   bandolier holding a radio, bold graphic novel lines, hatched sky
   rectangle, white margin, dry humor.

### wash-rabbit (2 stills)

1. Soft watercolor illustration on cream paper of a small wild rabbit
   standing in dry grass holding a handheld two-way radio, oval speech
   bubble reading "WTF, OVER.", loose wet-on-wet washes, speckled
   paper texture, muted tan and blue-gray.

2. Watercolor painting of an adult outlaw in a wide sombrero sitting
   in dry grass with a walkie-talkie instead of guns, skull-lean face
   stylized not gory, wet paper bleeds, cream ground, speech bubble
   "WTF, OVER.", fusion of western costume and storybook wash.

### period-grain (2 stills)

1. Black and white archival photograph still life, empty dark wooden
   hoop-back chair, folded padded winter coat and a child's cloth cap
   resting on the seat, a blank white card on the lap of the coat,
   geometric painted backdrop of black and white shapes, heavy film
   grain, 1930s field-studio lighting, **no person present**.

2. Split scientific-poster still on black: left column grainy
   monochrome chair and coat still life, center gold-teal hairline
   frame with a radio and a blank card, right column ink outlaw
   silhouette in sombrero, labels only, no paragraph text, far-art
   plate look, density not dimension quietly implied by nested frames,
   **no child, no gore**.

## Note on the child photo reference

Per Bobby: "La photo d'enfant sert de reference de grain/epoque, pas
de modele a cloner." The child photo is a **grain / period /
composition reference**, not a clone target. The 7 stills use the
two source boards (outlaw ink, rabbit watercolor) + this period
photo for grain reference.

## Sister

- `far-art/AGENTS.md` — the 56-axis schema contract.
- `far-art/tools/sheet.py` — compile_sheet + gate_sheet.
- `far-art/tools/compile_sheet.py` — CLI.
- `far-art/examples/tonalist-landscape-16x9.json` — first shipped example.

## License

MIT. Free for all agents, human and non-human.
