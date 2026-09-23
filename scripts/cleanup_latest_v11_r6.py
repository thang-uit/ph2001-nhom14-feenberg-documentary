#!/usr/bin/env python3
"""Safely remove obsolete Feenberg media while preserving the V11 R6 pipeline.

Dry-run is the default.  Pass --execute only after reviewing the inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROJECT_NAME = "VideoCodex"
EXPECTED_FINAL_SHA256 = "22e39eced2b8454d1ad8fdbe35d7f3d34e7e7a2cce63cc34400d99b513feb788"
EXPECTED_R5_SHA256 = "8b7e88a4bf2849369bc4f8bf25e721afba332a201b8e8da588a3720bacd39102"
EXPECTED_ASSET_COUNT = 130


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> Path:
    resolved = path.resolve()
    resolved.relative_to(PROJECT_ROOT.resolve())
    return resolved.relative_to(PROJECT_ROOT.resolve())


def all_files(directory: Path) -> set[Path]:
    if not directory.exists():
        return set()
    return {path for path in directory.rglob("*") if path.is_file() or path.is_symlink()}


def validate_keep_set(paths: set[Path]) -> None:
    missing = sorted(str(relative(path)) for path in paths if not path.is_file())
    if missing:
        raise SystemExit("Required R6 resources are missing:\n- " + "\n- ".join(missing))
    for path in paths:
        relative(path)


def unique_bytes(paths: set[Path]) -> int:
    seen: set[tuple[int, int]] = set()
    total = 0
    for path in paths:
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        key = (stat.st_dev, stat.st_ino)
        if key not in seen:
            seen.add(key)
            total += stat.st_size
    return total


def removable_bytes(delete: set[Path], keep: set[Path]) -> int:
    kept_inodes = {(path.stat().st_dev, path.stat().st_ino) for path in keep if path.is_file()}
    seen: set[tuple[int, int]] = set()
    total = 0
    for path in delete:
        if not path.exists() or not path.is_file():
            continue
        stat = path.stat()
        key = (stat.st_dev, stat.st_ino)
        if key not in kept_inodes and key not in seen:
            seen.add(key)
            total += stat.st_size
    return total


def remove_empty_directories(roots: list[Path]) -> None:
    for root in roots:
        if not root.exists():
            continue
        directories = sorted(
            (path for path in root.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        )
        for directory in directories:
            try:
                directory.rmdir()
            except OSError:
                pass
        try:
            root.rmdir()
        except OSError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Permanently delete the audited obsolete files")
    args = parser.parse_args()

    root = PROJECT_ROOT.resolve()
    if root.name != EXPECTED_PROJECT_NAME:
        raise SystemExit(f"Refusing cleanup outside {EXPECTED_PROJECT_NAME}: {root}")

    final = root / "Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4"
    if not final.is_file() or sha256(final) != EXPECTED_FINAL_SHA256:
        raise SystemExit("FINAL checksum does not match the locked V11 R6 delivery")
    rollback = root / "renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R5_LOCKED.mp4"
    if not rollback.is_file() or sha256(rollback) != EXPECTED_R5_SHA256:
        raise SystemExit("R5 rollback checksum does not match the locked delivery")

    picture_manifest_path = root / "qa/v11/picture_r6/manifest.json"
    picture_manifest = json.loads(picture_manifest_path.read_text(encoding="utf-8"))
    used_assets = {root / path for path in picture_manifest.get("asset_reuse", {})}
    if len(used_assets) != EXPECTED_ASSET_COUNT:
        raise SystemExit(f"Expected {EXPECTED_ASSET_COUNT} R6 assets, found {len(used_assets)}")

    keep_assets = set(used_assets)
    keep_assets.update(all_files(root / "assets/v11_overlays_r3"))
    # Keep the real portrait source as academic provenance for the rendered Feenberg card.
    keep_assets.add(root / "assets/v11_sources/andrew_feenberg_wikimedia.jpg")

    keep_renders = {
        root / "renders/v11_final_r5/PICTURE_MASTER_V11_R5_1080P.mp4",
        root / "renders/v11_final_r5/subtitles/SUBTITLE_ALPHA_V11_R5_CONTENT_1080P.mov",
        root / "renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R5_LOCKED.mp4",
        root / "renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R6_LOCKED.mp4",
    }
    keep_renders.update(all_files(root / "renders/v11_final_r6"))

    keep_audio = {
        root / "audio/mix/FULL_MIX_V10_CONTENT_48K.wav",
        root / "audio/music/SCORE_SUNO_V8_48K.wav",
        root / "audio/sfx/SFX_AMBIENCE_V10_48K.wav",
        root / "audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav",
        root / "audio/vo/narration_spoken.txt",
        root / "audio/vo/narration_sections.json",
    }

    keep_qa = {
        root / "qa/v9/05_subtitles_v9.srt",
        root / "qa/v11/02_storyboard_v11.csv",
        root / "qa/v11/timeline_manifest.json",
        root / "qa/v11/visual_plan_validation_r3.json",
        root / "qa/v11/picture_r5/manifest.json",
        root / "qa/v11/picture_r6/manifest.json",
        root / "qa/v11/source_cards_r6/manifest.json",
        root / "qa/v11/source_cards_r6/contact_sheet_titles.png",
        root / "qa/v11/source_cards_r6/visual_plan_validation_r6.json",
        root / "qa/v11/r6_typography/frame_manifest.csv",
        root / "qa/v11/r6_typography/picture_probe.json",
        root / "qa/v11/r6_typography/source_card_motion_10x3.jpg",
        root / "qa/v11/r6_typography/source_card_titles_footers_10.jpg",
        root / "qa/v11/delivery_r6/FINAL_V11_R6_DELIVERY_QA_REPORT.txt",
        root / "qa/v11/delivery_r6/final_probe.json",
        root / "qa/v11/delivery_r6/final_contact_sheet.jpg",
        root / "qa/v11/delivery_r6/bridge_contact_sheet.jpg",
        root / "qa/v11/delivery_r6/source_card_final_contact_sheet.jpg",
        root / "qa/v11/delivery_r6/final_audio_ebur128.txt",
        root / "qa/v11/delivery_r6/final_video_anomaly_scan.txt",
        root / "qa/v11/delivery_r6/r5_audio_framemd5.txt",
        root / "qa/v11/delivery_r6/r6_audio_framemd5.txt",
        root / "qa/v11/delivery_r6/r5_audio_pcm.sha256",
        root / "qa/v11/delivery_r6/r6_audio_pcm.sha256",
        root / "qa/v11/andrew_feenberg_card_manifest.json",
        root / "qa/v11/andrew_feenberg_wikimedia_api.json",
        root / "qa/v11/feenberg_sfu_current.html",
        root / "qa/v11/feenberg_sfu_profile.html",
        root / "qa/v11/feenberg_sfu_retirement.html",
        root / "qa/v11/real_mixkit_inventory.json",
        root / "qa/v11/mixkit_catalog.json",
        root / "qa/v11/graphics_manifest.json",
        root / "qa/v11/graphics_manifest_r3_patch.json",
        root / "qa/v11/graphics_manifest_r5.json",
        root / "qa/v11/credit_r4_select/final/title.jpg",
        root / "qa/v11/credit_r4_select/final/members.jpg",
        root / "qa/v11/credit_r4_select/final/thanks.jpg",
        root / "qa/v11/r5_current/matrix_header.jpg",
        root / "qa/v11/r5_current/technical_code_header.jpg",
        root / "qa/v11/r5_current/parameter_trace_header.jpg",
        root / "qa/v11/r5_current/R5_TITLE_RAIL_PATCH_REPORT.txt",
        root / "qa/credit_tphcm/v4/credit_source_manifest.json",
        root / "qa/credit_tphcm/v4/credit_storyboard.csv",
        root / "qa/credit_tphcm/v4/V4_FINAL_QA_REPORT.txt",
        root / "qa/credit_tphcm/v4/v4_asset_reuse_audit.json",
        root / "qa/credit_tphcm/v4/v4_probe_1080.json",
    }
    keep_qa.update(all_files(root / "qa/v11/delivery_r6/bridge_frames"))
    keep_qa.update(all_files(root / "qa/v11/delivery_r6/source_card_final_frames"))
    keep_qa.update(all_files(root / "qa/v11/r6_typography/frames"))

    keep = {final} | keep_assets | keep_renders | keep_audio | keep_qa
    validate_keep_set(keep)

    delete: set[Path] = set()
    delete.update(all_files(root / "assets") - keep_assets)
    delete.update(all_files(root / "renders") - keep_renders)
    delete.update(all_files(root / "audio") - keep_audio)
    delete.update(all_files(root / "video"))
    delete.update(all_files(root / "qa") - keep_qa)
    delete.update(all_files(root / "build"))
    delete.update(all_files(root / "scripts/__pycache__"))

    for obsolete in (
        root / ".DS_Store",
        root / "CREDIT_TPHCM_OH_YEAH_CLEAN_V4.mp4",
        root / "CREDIT_TPHCM_OH_YEAH_CLEAN_V4_4K.mp4",
        root / "Nhom5_KyTriVaQuyenLucCuaChuyenGiaTrongQuanTriAI.mp4",
    ):
        if obsolete.exists():
            delete.add(obsolete)

    overlap = keep & delete
    if overlap:
        raise SystemExit("Internal cleanup error: keep/delete overlap")
    for path in delete:
        relative(path)

    logical_delete = unique_bytes(delete)
    actual_delete = removable_bytes(delete, keep | {final})
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print(f"Project: {root}")
    print(f"Locked FINAL: {EXPECTED_FINAL_SHA256}")
    print(f"Kept current picture assets: {len(used_assets)}")
    print(f"Kept files total: {len(keep)}")
    print(f"Delete file entries: {len(delete)}")
    print(f"Logical obsolete data: {logical_delete / 1024**3:.2f} GiB")
    print(f"Estimated filesystem space reclaimed: {actual_delete / 1024**3:.2f} GiB")

    buckets: dict[str, tuple[int, int]] = {}
    for path in delete:
        rel = relative(path)
        bucket = rel.parts[0]
        count, size = buckets.get(bucket, (0, 0))
        try:
            file_size = path.stat().st_size
        except FileNotFoundError:
            file_size = 0
        buckets[bucket] = (count + 1, size + file_size)
    print("Delete by top-level area:")
    for bucket, (count, size) in sorted(buckets.items()):
        print(f"- {bucket}: {count} entries, {size / 1024**3:.2f} GiB logical")

    largest = sorted(
        ((path.stat().st_size, relative(path)) for path in delete if path.exists() and path.is_file()),
        reverse=True,
    )[:20]
    print("Largest obsolete entries:")
    for size, path in largest:
        print(f"- {size / 1024**2:8.1f} MiB  {path}")

    if not args.execute:
        return

    for path in sorted(delete, key=lambda item: len(item.parts), reverse=True):
        if path.is_symlink() or path.is_file():
            path.unlink()

    remove_empty_directories([
        root / "assets",
        root / "renders",
        root / "audio",
        root / "video",
        root / "qa",
        root / "build",
        root / "scripts/__pycache__",
    ])

    if not final.is_file() or sha256(final) != EXPECTED_FINAL_SHA256:
        raise SystemExit("Post-cleanup FINAL verification failed")
    validate_keep_set(keep)
    print("Cleanup complete; FINAL/R5 rollback checksums and all R6 keep resources verified.")


if __name__ == "__main__":
    main()
