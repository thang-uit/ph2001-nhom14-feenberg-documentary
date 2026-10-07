#!/usr/bin/env python3
"""Create a relative-path SHA-256 inventory of current media (no downloads)."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict

from verify_repository import ROOT, sha256

OUTPUT = ROOT / "docs/media/manifest.json"
MEDIA_ROOTS = ("assets", "audio", "templates", "delivery")


def build() -> dict:
    film = json.loads((ROOT / "remotion/src/data/film.json").read_text(encoding="utf-8"))
    uses: dict[str, list[str]] = defaultdict(list)
    for shot in film["shots"]:
        if shot["kind"] == "F":
            uses[shot["ref"]].append(shot["id"])
    entries = []
    for folder in MEDIA_ROOTS:
        for path in sorted((ROOT / folder).rglob("*")):
            if not path.is_file() or path.name == ".DS_Store":
                continue
            rel = path.relative_to(ROOT).as_posix()
            entry = {"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)}
            if rel in uses:
                entry["shots"] = uses[rel]
            entries.append(entry)
    categories = Counter(entry["path"].split("/")[0] for entry in entries)
    return {
        "version": "V13",
        "hash_algorithm": "SHA-256",
        "path_base": "repository root",
        "note": "Inventory is not a redistribution licence; see ATTRIBUTION.md.",
        "file_count": len(entries),
        "total_bytes": sum(entry["bytes"] for entry in entries),
        "categories": dict(categories),
        "files": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the reviewed inventory to docs/media/manifest.json")
    args = parser.parse_args()
    manifest = build()
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"media inventory: {manifest['file_count']} files, {manifest['total_bytes'] / 1024**3:.3f} GiB")
    if args.write:
        print("wrote docs/media/manifest.json")


if __name__ == "__main__":
    main()
