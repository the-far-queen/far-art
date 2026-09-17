"""
gate.py — CLI wrapper around sheet.gate().

Usage:
    python tools/gate.py path/to/sheet.json [--asset path/to/asset.txt]

Without --asset, the gate checks for naked assets (refused with no_sheet).
With --asset, the gate also checks forbidden_motifs in the asset text.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sheet import compile_sheet, gate, sheet_to_dict  # noqa: E402


def main(argv):
    p = argparse.ArgumentParser(description="Check the far-art commit_asset gate.")
    p.add_argument("sheet", help="Path to sheet YAML/JSON file.")
    p.add_argument("--asset", default="", help="Path to asset text file (forbidden_motif check).")
    args = p.parse_args(argv)

    path = Path(args.sheet)
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    try:
        axes = json.loads(text)
    except json.JSONDecodeError:
        # Try YAML
        axes = {}
        for line in text.splitlines():
            line = line.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            axes[key] = val

    try:
        sheet = compile_sheet(axes)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    asset_text = ""
    if args.asset:
        ap = Path(args.asset)
        if not ap.exists():
            print(f"error: asset {ap} does not exist", file=sys.stderr)
            return 2
        asset_text = ap.read_text(encoding="utf-8")

    allow, reason = gate(sheet, asset_text)
    out = {
        "sheet_id": sheet.sheet_id,
        "allow": allow,
        "reason": reason,
    }
    print(json.dumps(out, indent=2))
    return 0 if allow else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
