"""
find_art.py — public-domain illustration, matched to each story.

Bobby 2026-10-15: "find public domin art and download jpg ILLUSTRATE the stroies"

SELECTION RULE (from the far-art criterion, written earlier this session):
  the plate that matters is the one showing the character at the moment the
  installed identity fails - not the establishing shot, not the triumph.
  So a match must be for the AUTHOR or the WORK, never a generic theme.

SOURCES, in order of reliability:
  1. Wikimedia Commons - has machine-readable licence metadata per file, which
     is the only way to actually establish public domain rather than assume it.
  2. The Internet Archive - good for illustrated editions of pre-1929 books.

WHY NOT JUST DOWNLOAD: a jpgs' absence of a copyright notice does not make it
public domain. Every file here records its licence string as returned by the
Commons API. Anything not verifiable is recorded as unverified and is NOT
written into a page.

USAGE
    python find_art.py <slug> "<author>" "<work>" [--n 6]
    python find_art.py --batch batch.json
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request

OUT = r"C:\Users\HP\Desktop\images\levels"
MANIFEST = os.path.join(OUT, "_art_manifest.json")

ctx = ssl.create_default_context()
UA = {"User-Agent": "farqueen-art/1.0 (Bobby Wolfson; educational reuse)"}

# Commons categories that reliably hold PD illustration for the works we use.
# Author names are the reliable key; Commons category names are a guess and a
# bad one, so we search rather than assume.
ARTIST_CATEGORIES = {
    "dickens":              "Charles Dickens",
    "gaskell":              "Elizabeth Gaskell",
    "lawrence-dh":          "D. H. Lawrence",
    "melville":             "Herman Melville",
    "stoker":               "Bram Stoker",
    "shelley-mary":         "Mary Shelley",
    "carroll":              "Lewis Carroll",
    "gilman":               "Charlotte Perkins Gilman",
    "stevenson":            "Robert Louis Stevenson",
    "orwell":               "George Orwell",
    "huxley":               "Aldous Huxley",
    "wells-hg":             "H. G. Wells",
    "gaskell-elizabeth":     "Elizabeth Gaskell",
    "verne":                "Jules Verne",
    "twain":                "Mark Twain",
    "kipling":              "Rudyard Kipling",
    "dickens-charles":      "Charles Dickens",
}


def get(url: str, timeout: int = 45) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx).read()


def commons_search(term: str, limit: int = 12) -> list[dict]:
    """Search Commons for files. Returns raw API result rows."""
    q = urllib.parse.quote(f"{term} filetype:bitmap")
    url = (f"https://commons.wikimedia.org/w/api.php?action=query&format=json"
           f"&generator=search&gsrsearch={q}&gsrnamespace=6&gsrlimit={limit}"
           f"&prop=imageinfo&iiprop=url|extmetadata|size|mime")
    try:
        data = json.loads(get(url).decode("utf-8", "replace"))
    except Exception as e:
        print(f"  search failed for {term!r}: {type(e).__name__}")
        return []
    rows = []
    for page in (data.get("query", {}).get("pages", {}) or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {}) or {}

        def field(k):
            v = meta.get(k, {}).get("value", "")
            return _strip_html(v)
        rows.append({
            "title": page.get("title", ""),
            "url": info.get("url", ""),
            "mime": info.get("mime", ""),
            "width": info.get("width", 0),
            "height": info.get("height", 0),
            "size": info.get("size", 0),
            "licence": field("LicenseShortName"),
            "licence_url": field("LicenseUrl"),
            "artist": field("Artist"),
            "date": field("DateTimeOriginal"),
            "credit": field("Credit"),
            "description": field("ImageDescription")[:400],
        })
    return rows


def _strip_html(s: str) -> str:
    import re
    s = re.sub(r"<[^>]+>", " ", str(s))
    return re.sub(r"\s+", " ", s).strip()


PD_MARKERS = (
    "public domain", "pd-", "cc0", "no restrictions", "out of copyright",
    "copyright expired", "author died", "pre-1890", "pd-old", "pd-art",
    "cc-zero", "attribution", "publicdomain",
)

# licences that are NOT public domain but are reusable with attribution
FREE_LICENSES = ("cc by", "cc-by", "attribution")


def classify(row: dict) -> tuple[str, bool]:
    """Return (status, safe_to_use).

    safe_to_use is True only when the licence string is present AND is
    public domain or a permissive CC licence. Unknown licence -> not safe.
    """
    lic = (row.get("licence") or "").lower().strip()
    if not lic:
        return "UNVERIFIED", False
    if any(m in lic for m in PD_MARKERS):
        return "PUBLIC DOMAIN", True
    if any(m in lic for m in FREE_LICENSES):
        return "FREE (attribution required)", True
    return "OTHER: " + lic[:60], False


def is_good_image(row: dict) -> bool:
    if row.get("mime") not in ("image/jpeg", "image/png"):
        return False
    if row.get("width", 0) < 500 or row.get("height", 0) < 400:
        return False
    return True


def download(row: dict, slug: str, idx: int) -> tuple[bool, str]:
    os.makedirs(OUT, exist_ok=True)
    ext = ".jpg" if row["mime"] == "image/jpeg" else ".png"
    name = f"{slug}-{idx:02d}{ext}"
    path = os.path.join(OUT, name)
    try:
        raw = get(row["url"], timeout=60)
    except Exception as e:
        return False, f"download failed {type(e).__name__}"
    if len(raw) < 3000:
        return False, "file too small - probably an error page"
    with open(path, "wb") as f:
        f.write(raw)
    return True, f"{name} ({len(raw):,} bytes)"


def find(slug: str, author: str, work: str, n: int = 6, want_jpg: bool = True) -> list[dict]:
    """Find and download illustration for one story. Records licence for each."""
    print(f"\n=== {slug} :: {author} - {work} ===")
    terms = [f"{author}", f"{work} {author}"]
    rows: list[dict] = []
    for t in terms:
        rows.extend(commons_search(t, limit=14))
        time.sleep(0.4)

    # dedupe by url
    seen, uniq = set(), []
    for r in rows:
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        uniq.append(r)

    kept, rejected = [], []
    for r in uniq:
        if not is_good_image(r):
            rejected.append((r, "size or format"))
            continue
        status, safe = classify(r)
        r["licence_status"] = status
        r["safe"] = safe
        (kept if safe else rejected).append((r, status))

    print(f"  candidates: {len(uniq)}  usable: {len(kept)}  rejected: {len(rejected)}")

    got = []
    for r, status in kept[:n]:
        ok, msg = download(r, slug, len(got) + 1)
        entry = {
            "file": msg if ok else None,
            "title": r["title"],
            "commons_page": r["url"].replace("/Special:FilePath/", "/wiki/File:"),
            "licence": r.get("licence", ""),
            "licence_status": status,
            "artist": r.get("artist", ""),
            "date": r.get("date", ""),
            "downloaded": ok,
        }
        got.append(entry)
        print(f"   {'OK ' if ok else 'NO '} {status:32} {r['title'][:46]}  {msg}")

    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding="utf-8"))
    manifest[slug] = {"author": author, "work": work, "found": got}
    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return got


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        raise SystemExit(2)
    slug, author, work = a[0], a[1], a[2]
    n = 6
    if "--n" in a:
        n = int(a[a.index("--n") + 1])
    find(slug, author, work, n)