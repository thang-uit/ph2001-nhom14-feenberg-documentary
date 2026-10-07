#!/usr/bin/env python3
"""Read-only integrity checks for the frozen V13 repository.

The checker deliberately does not render, synthesize, download, or modify any
media. It validates paths, the credit checksum, the delivery checksums, and
the generated-plan references before a collaborator spends time installing
the toolchain.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CREDIT = "a96f6eb30342562e69b84c5e58c1d28d7b6da591a8969a35b8c013362cab4b93"
EXPECTED_DELIVERY = {
    "delivery/Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg_V13_1080p.mp4":
        "22132136e55b0c92aedcc5eef304266ef6043ad0d519345c718f62be85301afb",
    "delivery/Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg_V13_2K_1440p.mp4":
        "b468bc57ac07421a392f491b360fdd8065ceccdc022b1e12ed7f6469a110bc0d",
}
REQUIRED = (
    "AGENTS.md",
    "README.md",
    "scripts/v13_script_content.py",
    "scripts/v13_film.py",
    "scripts/build_v13_voice.py",
    "templates/KICH_BAN_CHI_TIET_FEENBERG_NHOM_14.docx",
    "delivery/PhuDe_V13.srt",
    "audio/vo/v13_vivienne/VO_V13_48K.wav",
    "audio/vo/v13_vivienne/timeline.json",
    "assets/photos/andrew_feenberg_wikimedia.jpg",
    "assets/credit/CREDIT_TPHCM_OH_YEAH_V4.mp4",
    "remotion/package-lock.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"VERIFY FAILED: {message}")


def main() -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")

    credit = ROOT / "assets/credit/CREDIT_TPHCM_OH_YEAH_V4.mp4"
    if sha256(credit) != EXPECTED_CREDIT:
        fail("credit V4 checksum changed")

    for rel, expected in EXPECTED_DELIVERY.items():
        path = ROOT / rel
        if sha256(path) != expected:
            fail(f"delivery checksum changed: {rel}")

    timeline = json.loads((ROOT / "audio/vo/v13_vivienne/timeline.json").read_text(encoding="utf-8"))
    duration = float(timeline["duration"])
    if not 900 <= duration <= 1200:
        fail(f"narration duration is outside 15–20 minutes: {duration:.2f}s")

    film_source = ROOT / "scripts/v13_film.py"
    plan_refs = {
        ("assets/real/" if prefix else "") + name
        for prefix, name in re.findall(r'F\((M \+ )?["\']([^"\']+)["\']', film_source.read_text(encoding="utf-8"))
    }
    missing = sorted(rel for rel in plan_refs if not (ROOT / rel).is_file())
    if missing:
        fail("missing plan assets: " + ", ".join(missing))

    actual_refs = {
        str(path.relative_to(ROOT))
        for folder in ("assets/ai", "assets/real")
        for path in (ROOT / folder).glob("*.mp4")
    }
    if actual_refs != plan_refs:
        fail("unreferenced footage: " + ", ".join(sorted(actual_refs - plan_refs)))

    cache_keys = {
        hashlib.sha1(f"{timeline['voice']}|{timeline['rate']}|{chunk['tts']}".encode()).hexdigest()[:16]
        for chapter in timeline["chapters"]
        for paragraph in chapter["paragraphs"]
        for chunk in paragraph["chunks"]
    }
    for key in cache_keys:
        for suffix in ("mp3", "json"):
            if not (ROOT / "audio/tts_cache" / f"{key}.{suffix}").is_file():
                fail(f"missing frozen TTS cache: {key}.{suffix}")

    print(f"OK: {len(plan_refs)} referenced footage assets exist")
    print(f"OK: narration timeline {duration:.2f}s")
    print(f"OK: {len(cache_keys)} TTS chunks can be reused offline")
    print("OK: credit and both V13 delivery masters match frozen SHA-256 values")


if __name__ == "__main__":
    main()
