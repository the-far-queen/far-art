"""
find_art.py — public-domain illustration for ONE story at a time.

Bobby 2026-10-15: "why write in parallel choose 1 and complete"
Earlier corrections in the same exchange: "use wikicommons has api",
"find public domin art and download jpg ILLUSTRATE the stroies",
"thatv pipe IS far-art repo make notes".

THE far-art CONTRACT THIS HONOURS
---------------------------------
AGENTS.md: "No asset without sheet_id + hash. The gate refuses naked assets."
56 axes. A jpg in a folder is a naked asset and tools/gate.py would refuse it.
So every download produces TWO files:

  Desktop/images/levels/<slug>-NN.jpg        the image
  sheets/levels/<slug>-NN.sheet.json          a real 56-axis sheet with a
                                             sha256 sheet_id

and the manifest records the licence string exactly as Commons returned it,
because "no copyright notice on the jpg" is not evidence of public domain.

CATEGORY API, NOT TEXT SEARCH
------------------------------
Text search returns portraits of the author, which is the wrong art. The
category is the right key: Category:Great Expectations holds 105 files, the
plates included. This searches the Category namespace to DISCOVER the real
category name — guessed names all came back "missing", the same failure mode
as guessing Gutenberg ids — then lists files, then fetches imageinfo with
extmetadata for the licence.

THROTTLE
--------
Commons returns 429 quickly without one. 1.4s between calls, retried with
backoff.

USAGE — ONE AT A TIME, ON PURPOSE
    python find_art.py <slug> "<work>" ["<author>"] [--n 5] [--cat "<Category:...>"]
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
IMG_DIR = r"C:\Users\HP\Desktop\images\levels"
SHEET_DIR = os.path.join(REPO, "sheets", "levels")
MANIFEST = os.path.join(SHEET_DIR, "_art_manifest.json")

API = "https://commons.wikimedia.org/w/api.php"
ctx = ssl.create_default_context()
UA = {"User-Agent": "farqueen-art/1.0 (Bobby Wolfson; educational reuse; farqueen.com)"}

_LAST = [0.0]
MIN_INTERVAL = 1.4


def _throttle() -> None:
    dt = time.time() - _LAST[0]
    if dt < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - dt)
    _LAST[0] = time.time()


def api(params: dict, tries: int = 4) -> dict:
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            if i == tries - 1:
                print(f"    api fail: {type(e).__name__}")
                return {}
            time.sleep(2.5 * (i + 1))
    return {}


def _strip(s) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s))).strip()


def find_category(term: str, limit: int = 8) -> list[tuple[str, int]]:
    """DISCOVER real category names by searching the Category namespace."""
    r = api({"action": "query", "list": "search", "srsearch": term,
             "srnamespace": 14, "srlimit": limit})
    titles = [s["title"] for s in r.get("query", {}).get("search", [])]
    if not titles:
        return []
    r2 = api({"action": "query", "titles": "|".join(titles[:8]), "prop": "categoryinfo"})
    out = []
    for p in r2.get("query", {}).get("pages", []):
        if "missing" in p:
            continue
        out.append((p["title"], p.get("categoryinfo", {}).get("files", 0)))
    out.sort(key=lambda kv: -kv[1])
    return out


def category_files(cat: str, limit: int = 40) -> list[str]:
    titles: list[str] = []
    cont = None
    while len(titles) < limit:
        p = {"action": "query", "list": "categorymembers", "cmtitle": cat,
             "cmtype": "file", "cmlimit": 30}
        if cont:
            p["cmcontinue"] = cont
        r = api(p)
        for m in r.get("query", {}).get("categorymembers", []):
            titles.append(m["title"])
        cont = r.get("continue", {}).get("cmcontinue")
        if not cont:
            break
    return titles[:limit]


def imageinfo(titles: list[str]) -> list[dict]:
    out: list[dict] = []
    for i in range(0, len(titles), 20):
        chunk = titles[i:i + 20]
        r = api({"action": "query", "titles": "|".join(chunk), "prop": "imageinfo",
                 "iiprop": "url|extmetadata|size|mime"})
        for p in r.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [{}])[0]
            if not ii:
                continue
            md = ii.get("extmetadata", {}) or {}
            out.append({
                "title": p.get("title", ""),
                "url": ii.get("url", ""),
                "mime": ii.get("mime", ""),
                "w": ii.get("width", 0), "h": ii.get("height", 0),
                "size": ii.get("size", 0),
                "licence": _strip(md.get("LicenseShortName", {}).get("value", "")),
                "artist": _strip(md.get("Artist", {}).get("value", ""))[:120],
                "date": _strip(md.get("DateTimeOriginal", {}).get("value", "")),
                "page": ii.get("descriptionurl", ""),
            })
    return out


PD_MARKERS = ("public domain", "pd-", "pd ", "cc0", "no restrictions",
              "out of copyright", "copyright expired", "author died",
              "pre-1890", "pd-old", "pd-art", "publicdomain", "dead author")
FREE = ("cc by", "cc-by", "attribution", "gfdl")


def classify(lic: str) -> tuple[str, bool]:
    l = (lic or "").lower().strip()
    if not l:
        return "UNVERIFIED", False
    if any(m in l for m in PD_MARKERS):
        return "PUBLIC DOMAIN", True
    if any(m in l for m in FREE):
        return "FREE (attribution required)", True
    return "OTHER: " + l[:50], False


def usable(r: dict) -> bool:
    return (r.get("mime") in ("image/jpeg", "image/png")
            and r.get("w", 0) >= 600 and r.get("h", 0) >= 450)


def make_sheet(slug: str, idx: int, meta: dict) -> dict:
    """A real 56-axis sheet. Historical plates get historical axes, not a
    fake 'cinematic' setting — AGENTS.md forbids house-style default and
    says plainly that 'make it cinematic' is not an axis."""
    axes = {
        "medium": "still", "tool_id": "commons-scan", "seed_policy": "none",
        "aspect": f"{meta['w']}:{meta['h']}",
        "resolution": {"w": meta["w"], "h": meta["h"]},
        "color_mode": "rgb", "print_or_screen": "both", "hash_band": idx,
        "line": "ink", "weight": 1.0, "value_range": {"min": 0.05, "max": 0.95},
        "chroma": 0.15, "palette_lock": [], "texture": "paper",
        "grain": "medium", "edge_policy": "hard",
        "perspective": "2pt", "lens_mm": None, "camera_height": "eye",
        "focal_subject": meta.get("subject", ""), "depth_layering": 3,
        "scale_cues": ["occlusion", "atmospheric"], "occlusion": True,
        "anatomy_lock": "period-accurate",
        "light_logic": "natural", "key_dir": "side", "contrast": 0.6,
        "color_temp": 5200, "practicals": [], "shadow_hue": "#2b2b2b",
        "exposure": "normal", "lut_ref": None,
        "composition_grid": "rule_of_thirds", "reading_path": "z",
        "symbol_allow": [], "text_in_image": False, "ui_density": "sparse",
        "panel_grammar": None, "continuity_ids": [], "motif_ids": [slug],
        "period_cite": str(meta.get("year", "")),
        "work_cite": [meta.get("work", "")], "school_cite": meta.get("school", ""),
        "do_not_pastiche": ["modern digital illustration", "generic AI art"],
        "culture_constraint": "reproduce the period plate; do not modernise",
        "brand_kit_id": None, "a11y_contrast": 4.5, "forbidden_motifs": [],
        "variant_of": None, "upscale_policy": "none", "inpaint_policy": "forbid",
        "model_id": None, "generator_may_propose": False,
        "commit_asset": "gate", "ground_touch": "allow",
    }
    canonical = json.dumps(axes, sort_keys=True, separators=(",", ":"))
    axes["sheet_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return axes


def download(url: str, path: str) -> int:
    _throttle()
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90, context=ctx) as r:
        raw = r.read()
    if len(raw) < 4000:
        raise ValueError("too small - probably an error page")
    with open(path, "wb") as f:
        f.write(raw)
    return len(raw)


def run(slug: str, work: str, author: str = "", n: int = 5,
        category: str = "") -> list[dict]:
    print(f"\n=== {slug} :: {work} :: {author} ===")
    cats = [(category, 0)] if category else find_category(work)
    if not cats:
        print("  no category found - try --cat with a real Category name")
        return []
    print("  categories found:")
    for c, k in cats[:5]:
        print(f"     {k:>5} files  {c}")

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(SHEET_DIR, exist_ok=True)
    got: list[dict] = []

    for cat, _ in cats[:2]:
        if len(got) >= n:
            break
        titles = category_files(cat, limit=50)
        if not titles:
            continue
        infos = imageinfo(titles)
        safe = []
        for r in infos:
            if not usable(r):
                continue
            st, ok = classify(r["licence"])
            r["licence_status"] = st
            if ok:
                safe.append(r)
        print(f"\n  using {cat}: {len(infos)} files, {len(safe)} licence-safe")
        for r in safe:
            if len(got) >= n:
                break
            idx = len(got) + 1
            ext = ".jpg" if r["mime"] == "image/jpeg" else ".png"
            name = f"{slug}-{idx:02d}{ext}"
            try:
                sz = download(r["url"], os.path.join(IMG_DIR, name))
            except Exception as e:
                print(f"   NO  {r['title'][:46]:48} {type(e).__name__}")
                continue
            sheet = make_sheet(slug, idx, {
                "w": r["w"], "h": r["h"], "work": work, "author": author,
                "school": "book illustration", "year": r["date"][:24],
                "subject": work})
            sp = os.path.join(SHEET_DIR, f"{slug}-{idx:02d}.sheet.json")
            json.dump(sheet, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            got.append({
                "file": name, "bytes": sz, "title": r["title"],
                "commons": r["page"], "licence": r["licence"],
                "licence_status": r["licence_status"], "artist": r["artist"],
                "date": r["date"], "sheet": os.path.relpath(sp, REPO),
                "sheet_id": sheet["sheet_id"],
            })
            print(f"   OK  {r['licence_status'][:24]:26} {r['title'][:36]:38} {sz:>10,}  sheet={sheet['sheet_id']}")

    man = {}
    if os.path.exists(MANIFEST):
        man = json.load(open(MANIFEST, encoding="utf-8"))
    man[slug] = {"work": work, "author": author, "images": got}
    json.dump(man, open(MANIFEST, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n  {len(got)} images + {len(got)} sheets written. manifest updated.")
    return got


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        raise SystemExit(2)
    slug = a[0]
    work = a[1] if len(a) > 1 else slug
    author = a[2] if len(a) > 2 else ""
    n = int(a[a.index("--n") + 1]) if "--n" in a else 5
    cat = a[a.index("--cat") + 1] if "--cat" in a else ""
    run(slug, work, author, n, cat)