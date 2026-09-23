#!/usr/bin/env python3
"""Verify restored external media against the public upload manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--strict", action="store_true", help="fail if any listed file is missing")
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    root = (args.root or manifest.parents[1]).resolve()
    missing: list[str] = []
    mismatched: list[str] = []
    checked = 0
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            relative = row["relative_path"]
            path = root / relative
            if not path.is_file():
                missing.append(relative)
                continue
            checked += 1
            actual_size = path.stat().st_size
            expected_size = int(row["size_bytes"])
            actual_hash = sha256(path)
            if actual_size != expected_size or actual_hash != row["sha256"]:
                mismatched.append(
                    f"{relative}: size {actual_size}/{expected_size}, sha256 {actual_hash}/{row['sha256']}"
                )
    print(f"Checked: {checked}")
    print(f"Missing: {len(missing)}")
    print(f"Mismatched: {len(mismatched)}")
    if mismatched:
        print("\n".join(mismatched))
    if missing:
        print("\nMissing paths:")
        print("\n".join(f"- {item}" for item in missing))
    if mismatched or (args.strict and missing):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
