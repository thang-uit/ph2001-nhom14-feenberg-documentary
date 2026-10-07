#!/usr/bin/env python3
"""Inspect staged public files without printing credential values.

This is a targeted publication gate, not a guarantee that no possible secret
exists. Git LFS media are inspected as staged pointers, not loaded into RAM.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LFS_SUFFIXES = {".mp4", ".mov", ".webm", ".wav", ".mp3", ".m4a", ".flac", ".png", ".jpg", ".jpeg", ".webp", ".docx"}
FORBIDDEN_DIRS = ("docs/local/", "materials/instructor/", "renders/", ".venv/", "node_modules/", "remotion/public/")
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})"),
    "OpenAI secret key": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{35,}"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "production account email": re.compile(r"\b[\w.+-]+@(?:gmail|icloud|outlook)\.com\b", re.I),
    "personal machine path": re.compile(r"(?:/Users/|/home/)[A-Za-z0-9_-]+/"),
    "credential in URL": re.compile(r"https?://[^\s/@]+:[^\s/@]+@"),
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main() -> None:
    paths = [p for p in git("ls-files", "-z").decode().split("\0") if p]
    issues: list[str] = []
    lfs_count = 0
    for rel in paths:
        path = Path(rel)
        if rel.startswith(FORBIDDEN_DIRS) or "node_modules" in path.parts or ".claude" in path.parts:
            issues.append(f"forbidden public path: {rel}")
        if path.name.startswith(".env") and path.name != ".env.example":
            issues.append(f"environment file: {rel}")
        if path.name == ".DS_Store" or path.suffix in {".pem", ".p12", ".pfx", ".key"}:
            issues.append(f"private/machine file: {rel}")
        size = int(git("cat-file", "-s", f":{rel}"))
        if size >= 100 * 1024 * 1024:
            issues.append(f"ordinary Git blob exceeds 100 MiB: {rel}")
            continue
        if path.suffix.lower() in LFS_SUFFIXES:
            blob = git("show", f":{rel}") if size < 1024 else b""
            if not re.fullmatch(rb"version https://git-lfs.github.com/spec/v1\noid sha256:[a-f0-9]{64}\nsize \d+\n", blob):
                issues.append(f"media is not an LFS pointer: {rel}")
            lfs_count += 1
            continue
        blob = git("show", f":{rel}")
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                issues.append(f"{label} detected: {rel}")
    if issues:
        print("PUBLICATION AUDIT FAILED:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print(f"PUBLICATION AUDIT OK: {len(paths)} staged files; {lfs_count} LFS media; no targeted secret patterns found")


if __name__ == "__main__":
    main()
