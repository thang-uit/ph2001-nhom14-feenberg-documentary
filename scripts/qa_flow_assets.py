#!/usr/bin/env python3
"""Validate Google Flow reference images and opening-proof clips before editing.

The checker is intentionally strict about final-footage resolution. A 720p clip
may be useful for a disposable preview, but it must never silently enter the
1080p submission master.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image


REFERENCE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
TARGET_ASPECT_RATIO = 16 / 9


@dataclass
class Finding:
    task_id: str
    scene_id: str
    basename: str
    path: str | None
    status: str
    errors: list[str]
    warnings: list[str]
    technical: dict[str, Any]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_seconds(value: str) -> float:
    parts = value.replace(",", ".").split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise ValueError(f"Unsupported timestamp: {value}")


def frame_rate(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    numerator, denominator = value.split("/", 1)
    denominator_value = float(denominator)
    return float(numerator) / denominator_value if denominator_value else None


def probe_video(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def find_exact_asset(directory: Path, basename: str, extensions: set[str]) -> tuple[Path | None, list[str]]:
    matches = sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions and path.stem == basename
    )
    if not matches:
        return None, []
    return matches[0], [str(path) for path in matches[1:]]


def validate_reference(task: dict[str, str], path: Path | None, duplicates: list[str]) -> Finding:
    errors: list[str] = []
    warnings: list[str] = []
    technical: dict[str, Any] = {}
    if path is None:
        errors.append("Missing exact reference filename")
    else:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                technical.update(
                    width=width,
                    height=height,
                    mode=image.mode,
                    format=image.format,
                    sha256=sha256(path),
                )
                if width < 1280 or height < 720:
                    errors.append(f"Reference is too small: {width}x{height}; require at least 1280x720")
                ratio = width / height
                if abs(ratio - TARGET_ASPECT_RATIO) > 0.12:
                    warnings.append(f"Reference is not close to 16:9: {width}x{height}")
        except Exception as exc:  # Pillow exposes format-specific exception types.
            errors.append(f"Unreadable/corrupt reference: {exc}")
    if duplicates:
        errors.append(f"Ambiguous duplicate filenames: {duplicates}")
    return Finding(
        task_id=task["TASK_ID"],
        scene_id=task["SCENE_ID"],
        basename=task["OUTPUT_BASENAME"],
        path=str(path) if path else None,
        status="FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        errors=errors,
        warnings=warnings,
        technical=technical,
    )


def validate_video(
    task: dict[str, str],
    path: Path | None,
    duplicates: list[str],
    expected_duration: float,
) -> Finding:
    errors: list[str] = []
    warnings: list[str] = []
    technical: dict[str, Any] = {}
    if path is None:
        errors.append("Missing exact Flow clip filename")
    else:
        try:
            probe = probe_video(path)
            streams = probe.get("streams", [])
            video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
            if len(video_streams) != 1:
                errors.append(f"Expected exactly one video stream, found {len(video_streams)}")
            else:
                stream = video_streams[0]
                width = int(stream.get("width") or 0)
                height = int(stream.get("height") or 0)
                duration = float(stream.get("duration") or probe.get("format", {}).get("duration") or 0)
                fps = frame_rate(stream.get("avg_frame_rate") or stream.get("r_frame_rate"))
                technical.update(
                    codec=stream.get("codec_name"),
                    profile=stream.get("profile"),
                    width=width,
                    height=height,
                    duration=duration,
                    fps=fps,
                    pix_fmt=stream.get("pix_fmt"),
                    field_order=stream.get("field_order"),
                    color_range=stream.get("color_range"),
                    color_space=stream.get("color_space"),
                    color_transfer=stream.get("color_transfer"),
                    color_primaries=stream.get("color_primaries"),
                    sha256=sha256(path),
                )
                if width < 1920 or height < 1080:
                    errors.append(
                        f"Native clip is only {width}x{height}; do not upscale it into the submission master"
                    )
                if height and abs((width / height) - TARGET_ASPECT_RATIO) > 0.03:
                    errors.append(f"Unexpected aspect ratio: {width}x{height}")
                required_duration = 6.0 if task["SCENE_ID"] == "S005" else expected_duration - 0.08
                if duration < required_duration:
                    errors.append(
                        f"Clip is {duration:.3f}s; scene requires at least {required_duration:.3f}s"
                    )
                if fps is None or fps < 23 or fps > 61:
                    errors.append(f"Unsupported or unreadable frame rate: {fps}")
                if stream.get("field_order") not in {None, "unknown", "progressive"}:
                    errors.append(f"Interlaced footage is not accepted: {stream.get('field_order')}")
                missing_tags = [
                    key
                    for key in ("color_space", "color_transfer", "color_primaries")
                    if not stream.get(key)
                ]
                if missing_tags:
                    warnings.append(
                        "Missing source color metadata; conform explicitly to Rec.709 in post: "
                        + ", ".join(missing_tags)
                    )
        except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"Unreadable/corrupt video: {exc}")
    if duplicates:
        errors.append(f"Ambiguous duplicate filenames: {duplicates}")
    return Finding(
        task_id=task["TASK_ID"],
        scene_id=task["SCENE_ID"],
        basename=task["OUTPUT_BASENAME"],
        path=str(path) if path else None,
        status="FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        errors=errors,
        warnings=warnings,
        technical=technical,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope", choices=("references", "proof", "all"), default="all")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    queue_path = project_dir / "assets/flow_production_queue.csv"
    storyboard_path = project_dir / "02_storyboard.csv"
    reference_dir = project_dir / "assets/flow/references"
    proof_dir = project_dir / "assets/flow/proof/raw"
    report_json = project_dir / "qa/flow_proof_asset_QA.json"
    report_text = project_dir / "qa/flow_proof_asset_QA.txt"

    reference_dir.mkdir(parents=True, exist_ok=True)
    proof_dir.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)

    with queue_path.open(encoding="utf-8-sig", newline="") as handle:
        queue = list(csv.DictReader(handle))
    with storyboard_path.open(encoding="utf-8-sig", newline="") as handle:
        storyboard = {row["SCENE_ID"]: row for row in csv.DictReader(handle)}

    batches: set[str]
    if args.scope == "references":
        batches = {"P0_REFERENCE"}
    elif args.scope == "proof":
        batches = {"P1_PROOF"}
    else:
        batches = {"P0_REFERENCE", "P1_PROOF"}

    selected = [task for task in queue if task["BATCH"] in batches]
    findings: list[Finding] = []
    for task in selected:
        basename = task["OUTPUT_BASENAME"]
        if task["BATCH"] == "P0_REFERENCE":
            path, duplicates = find_exact_asset(reference_dir, basename, REFERENCE_EXTENSIONS)
            findings.append(validate_reference(task, path, duplicates))
        else:
            path, duplicates = find_exact_asset(proof_dir, basename, VIDEO_EXTENSIONS)
            scene = storyboard[task["SCENE_ID"]]
            expected_duration = parse_seconds(scene["END_TIME"]) - parse_seconds(scene["START_TIME"])
            findings.append(validate_video(task, path, duplicates, expected_duration))

    hashes: dict[str, list[Finding]] = {}
    for finding in findings:
        digest = finding.technical.get("sha256")
        if digest:
            hashes.setdefault(str(digest), []).append(finding)
    for matching in hashes.values():
        if len(matching) > 1:
            names = ", ".join(item.basename for item in matching)
            for item in matching:
                item.errors.append(f"Duplicate binary asset detected across expected outputs: {names}")
                item.status = "FAIL"

    failed = sum(finding.status == "FAIL" for finding in findings)
    warned = sum(finding.status == "PASS_WITH_WARNINGS" for finding in findings)
    overall = "FAIL" if failed else ("PASS_WITH_WARNINGS" if warned else "PASS")
    payload = {
        "scope": args.scope,
        "overall_status": overall,
        "strict_native_video_minimum": "1920x1080",
        "checked": len(findings),
        "failed": failed,
        "warnings": warned,
        "findings": [asdict(finding) for finding in findings],
    }
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "FLOW REFERENCE / PROOF ASSET QA",
        f"Scope: {args.scope}",
        f"Overall: {overall}",
        f"Checked: {len(findings)} | Failed: {failed} | Pass with warnings: {warned}",
        "Submission rule: video below native 1920x1080 is rejected; no silent upscale.",
        "",
    ]
    for finding in findings:
        lines.append(f"[{finding.status}] {finding.task_id} / {finding.scene_id} / {finding.basename}")
        lines.append(f"  File: {finding.path or 'MISSING'}")
        for error in finding.errors:
            lines.append(f"  ERROR: {error}")
        for warning in finding.warnings:
            lines.append(f"  WARNING: {warning}")
    report_text.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Flow asset QA: {overall}")
    print(f"JSON: {report_json}")
    print(f"Text: {report_text}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
