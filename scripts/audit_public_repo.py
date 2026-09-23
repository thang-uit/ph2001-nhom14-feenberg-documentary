#!/usr/bin/env python3
"""Fail-closed audit for the public GitHub source repository.

The audit reads only tracked files, so it is safe to run before committing.
It rejects oversized/media files and common local-private metadata.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


MAX_TRACKED_BYTES = 95 * 1024 * 1024
MEDIA_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".wav", ".mp3", ".m4a", ".aac", ".flac"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
ABSOLUTE_RE = re.compile(r"/(?:Users|Volumes|private/var|home)/")


def tracked(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    )
    return [root / value for value in result.stdout.decode().split("\0") if value]


def private_url_pattern() -> re.Pattern[str]:
    # Split literals so this checker does not flag its own source code.
    host = "flow" + ".google" + ".com"
    return re.compile(re.escape(host) + r"/u/\d+/project/")


def drive_folder_marker() -> str:
    # Split the literal so this checker does not flag its own source code.
    return "drive" + ".google" + ".com/drive/folders/"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    failures: list[str] = []
    files = tracked(root)
    if not files:
        failures.append("No tracked files found; initialize Git and stage the source set first")
    private_url = private_url_pattern()
    for path in files:
        if not path.is_file():
            failures.append(f"tracked path missing: {path.relative_to(root)}")
            continue
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        if size > MAX_TRACKED_BYTES:
            failures.append(f"tracked file exceeds 95 MiB: {relative} ({size} bytes)")
        if path.suffix.lower() in MEDIA_SUFFIXES:
            failures.append(f"media must remain outside Git: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if EMAIL_RE.search(text):
            failures.append(f"email-like identifier found: {relative}")
        if ABSOLUTE_RE.search(text):
            failures.append(f"absolute local path found: {relative}")
        if private_url.search(text):
            failures.append(f"private Flow project URL found: {relative}")
        if drive_folder_marker() in text:
            failures.append(f"Drive folder URL found: {relative}")
    if failures:
        print("PUBLIC REPO AUDIT: FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"PUBLIC REPO AUDIT: PASS ({len(files)} tracked files; no media or private local metadata)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
