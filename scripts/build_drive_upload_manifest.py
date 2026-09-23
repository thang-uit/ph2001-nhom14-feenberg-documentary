#!/usr/bin/env python3
"""Create a relative-path inventory for media kept outside the public Git repo.

The output intentionally contains no absolute paths, account identifiers, or
cloud URLs.  It is safe to publish after a human checks the list.  Hashing is
done once per inode so hard-linked delivery/archive copies do not cost extra
I/O.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass, replace
from pathlib import Path


MEDIA_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v",
    ".wav", ".mp3", ".m4a", ".aac", ".flac",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff",
}
DEFAULT_THRESHOLD = 50 * 1024 * 1024
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class Entry:
    relative_path: str
    size_bytes: int
    sha256: str
    media_kind: str
    priority: str
    drive_action: str
    duplicate_of: str = ""


def sha256(path: Path, cache: dict[tuple[int, int], str]) -> str:
    stat = path.stat()
    key = (stat.st_dev, stat.st_ino)
    if key in cache:
        return cache[key]
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    value = digest.hexdigest()
    cache[key] = value
    return value


def priority_for(relative: str, size: int) -> tuple[str, str]:
    name = Path(relative).name
    if name == "Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4":
        return "P1 — VERIFY DELIVERY", "Kiểm tra file đã có trên Drive; không upload bản trùng"
    if name == "KICH_BAN_CHI_TIET_FEENBERG_NHOM_14.docx":
        return "P1 — VERIFY SCRIPT", "Kiểm tra file đã có trên Drive; không upload bản trùng"
    if relative.startswith("audio/"):
        return "P2 — REBUILD INPUT", "Upload nếu cần tái dựng hoặc rollback"
    if relative.startswith("assets/"):
        return "P2 — REBUILD INPUT", "Upload các asset được storyboard tham chiếu"
    if "CREDIT_TPHCM" in name:
        return "P1 — DELIVERY SUPPORT", "Giữ một bản credit V4 đã kiểm hash"
    if relative.startswith("renders/"):
        if "candidate" in name.lower():
            return "P4 — DO NOT UPLOAD", "Candidate có thể tái sinh; không đưa lên Drive"
        if "archive_v11" in relative and "R5_LOCKED" in name:
            return "P3 — OPTIONAL ROLLBACK", "Chỉ upload nếu nhóm muốn giữ đường lui R5"
        if "archive_v11" in relative:
            return "P4 — DUPLICATE DELIVERY", "Không upload nếu checksum trùng file giao nộp"
        return "P3 — OPTIONAL PATCH MASTER", "Hữu ích khi vá picture/subtitle; không bắt buộc để nộp"
    if size >= 500 * 1024 * 1024:
        return "P3 — OPTIONAL ARCHIVE", "Chỉ upload khi cần rollback/đối chiếu"
    return "P3 — OPTIONAL ARCHIVE", "Không bắt buộc cho lần dựng hiện hành"


def media_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}:
        return "video"
    if suffix in {".wav", ".mp3", ".m4a", ".aac", ".flac"}:
        return "audio"
    return "image"


def collect(root: Path, threshold: int) -> list[Entry]:
    entries: list[Entry] = []
    hash_cache: dict[tuple[int, int], str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix()
        stat = path.stat()
        is_media = path.suffix.lower() in MEDIA_EXTENSIONS
        if not is_media or stat.st_size < threshold:
            continue
        # Generated/source binary media are the intended external set.
        kind = media_kind(path) if is_media else "large-binary-or-document"
        priority, action = priority_for(relative, stat.st_size)
        entries.append(Entry(relative, stat.st_size, sha256(path, hash_cache), kind, priority, action))
    groups: dict[str, list[Entry]] = {}
    for entry in entries:
        groups.setdefault(entry.sha256, []).append(entry)

    def canonical_key(entry: Entry) -> tuple[int, str]:
        relative = entry.relative_path
        if relative == "Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4":
            return (0, relative)
        if relative == "CREDIT_TPHCM_OH_YEAH_V4.mp4":
            return (1, relative)
        if "renders/v11_final_r6/" in relative:
            return (2, relative)
        if "renders/archive_v11/" in relative:
            return (3, relative)
        return (4, relative)

    normalized: list[Entry] = []
    for digest_entries in groups.values():
        canonical = min(digest_entries, key=canonical_key)
        for entry in digest_entries:
            if entry.relative_path == canonical.relative_path:
                normalized.append(entry)
            else:
                normalized.append(replace(
                    entry,
                    priority="P4 — DUPLICATE",
                    drive_action=f"Không upload; trùng nội dung với {canonical.relative_path}",
                    duplicate_of=canonical.relative_path,
                ))
    return sorted(normalized, key=lambda item: (item.priority, item.relative_path))


def write_csv(entries: list[Entry], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["relative_path", "size_bytes", "size_mib", "sha256", "media_kind", "priority", "drive_action", "duplicate_of"])
        for entry in entries:
            writer.writerow([
                entry.relative_path,
                entry.size_bytes,
                f"{entry.size_bytes / 1024 / 1024:.2f}",
                entry.sha256,
                entry.media_kind,
                entry.priority,
                entry.drive_action,
                entry.duplicate_of,
            ])


def write_markdown(entries: list[Entry], output: Path, threshold: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Media nặng không commit Git",
        "",
        f"Manifest được sinh tự động với ngưỡng **{threshold / 1024 / 1024:.0f} MiB**; chỉ các file từ ngưỡng này trở lên được liệt kê.",
        "",
        "> Không upload tự động. Hãy kiểm tra ba file delivery trên Drive trước, không xóa file cũ, rồi khôi phục theo đúng `relative_path`.",
        "",
        "| Ưu tiên | Đường dẫn tương đối | Dung lượng | Loại | SHA-256 | Hành động |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            f"| {entry.priority} | `{entry.relative_path}` | {entry.size_bytes / 1024 / 1024:.2f} MiB | {entry.media_kind} | `{entry.sha256}` | {entry.drive_action} |"
        )
    lines.extend([
        "",
        f"Tổng số file: **{len(entries)}** · Tổng dung lượng (tính cả hardlink theo từng đường dẫn): **{sum(e.size_bytes for e in entries) / 1024 / 1024 / 1024:.2f} GiB**.",
        "",
        "Lệnh tái sinh:",
        "",
        "```bash",
        "python3 scripts/build_drive_upload_manifest.py \\",
        "  --root . \\",
        "  --csv docs/HEAVY_FILES_TO_UPLOAD_DRIVE.csv \\",
        "  --markdown docs/HEAVY_FILES_TO_UPLOAD_DRIVE.md",
        "```",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--threshold-mib", type=float, default=50.0)
    parser.add_argument("--csv", type=Path, default=Path("docs/HEAVY_FILES_TO_UPLOAD_DRIVE.csv"))
    parser.add_argument("--markdown", type=Path, default=Path("docs/HEAVY_FILES_TO_UPLOAD_DRIVE.md"))
    args = parser.parse_args()
    root = args.root.resolve()
    threshold = int(args.threshold_mib * 1024 * 1024)
    entries = collect(root, threshold)
    csv_path = args.csv if args.csv.is_absolute() else root / args.csv
    markdown_path = args.markdown if args.markdown.is_absolute() else root / args.markdown
    write_csv(entries, csv_path)
    write_markdown(entries, markdown_path, threshold)
    print(f"Wrote {len(entries)} external-media entries")
    print(f"CSV: {csv_path}")
    print(f"Markdown: {markdown_path}")


if __name__ == "__main__":
    main()
