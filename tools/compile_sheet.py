"""
compile_sheet.py — CLI wrapper around sheet.compile_sheet().

Usage:
    python tools/compile_sheet.py path/to/sheet.yaml
    python tools/compile_sheet.py path/to/sheet.json
    python tools/compile_sheet.py --stdin   # read JSON from stdin

Outputs the compiled Sheet as JSON to stdout, including the computed
sheet_id. Errors are printed to stderr and exit 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as a script from anywhere
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sheet import compile_sheet, sheet_to_dict  # noqa: E402


def _load_yaml(path: Path) -> dict:
    """Tiny YAML loader. Avoids PyYAML dependency by using JSON only.

    For YAML files, we require the file to be valid JSON (a common
    subset). If you need full YAML, add PyYAML as a dev dep.
    """
    text = path.read_text(encoding="utf-8")
    # Try JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try minimal YAML: key: value, one per line, no anchors
    out = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Cannot parse YAML line: {line!r}")
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # Strip surrounding quotes
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        out[key] = val
    return out


def main(argv):
    p = argparse.ArgumentParser(description="Compile a far-art style sheet.")
    p.add_argument("path", nargs="?", help="Path to sheet YAML/JSON file.")
    p.add_argument("--stdin", action="store_true", help="Read JSON from stdin.")
    args = p.parse_args(argv)

    if args.stdin:
        axes = json.loads(sys.stdin.read())
    elif args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"error: {path} does not exist", file=sys.stderr)
            return 2
        axes = _load_yaml(path)
    else:
        p.print_help()
        return 2

    try:
        sheet = compile_sheet(axes)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    out = sheet_to_dict(sheet)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
