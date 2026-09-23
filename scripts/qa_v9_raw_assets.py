#!/usr/bin/env python3
"""Technical gate and dense contact sheets for the V9 Flow footage.

This checker deliberately does not claim that a generated shot is visually or
physically correct.  It verifies the file itself, decodes every frame, samples
at two frames per second, and flags exact or near-static repetition so a manual
review can make the final keep/reject decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
SAMPLE_FPS = 2


@dataclass
class AssetFinding:
    asset_id: str
    path: str
    status: str
    errors: list[str]
    warnings: list[str]
    technical: dict[str, object]
    contact_sheet: str | None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True)


def probe(path: Path) -> dict[str, object]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            (
                "stream=codec_name,profile,width,height,r_frame_rate,avg_frame_rate,"
                "pix_fmt,field_order,color_range,color_space,color_transfer,color_primaries:"
                "format=duration,size,bit_rate"
            ),
            "-of",
            "json",
            str(path),
        ]
    )
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    if len(streams) != 1:
        raise ValueError(f"expected one video stream, found {len(streams)}")
    stream = streams[0]
    fmt = data.get("format", {})
    rate_text = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/0"
    numerator, denominator = (float(part) for part in str(rate_text).split("/", 1))
    fps = numerator / denominator if denominator else 0.0
    return {
        "codec": stream.get("codec_name"),
        "profile": stream.get("profile"),
        "width": int(stream.get("width") or 0),
        "height": int(stream.get("height") or 0),
        "fps": fps,
        "duration": float(fmt.get("duration") or 0),
        "size_bytes": int(fmt.get("size") or path.stat().st_size),
        "bit_rate": int(fmt.get("bit_rate") or 0),
        "pix_fmt": stream.get("pix_fmt"),
        "field_order": stream.get("field_order"),
        "color_range": stream.get("color_range"),
        "color_space": stream.get("color_space"),
        "color_transfer": stream.get("color_transfer"),
        "color_primaries": stream.get("color_primaries"),
    }


def full_decode(path: Path) -> None:
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-f", "null", "-"])


def extract_samples(path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for old in output_dir.glob("*.jpg"):
        old.unlink()
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-vf",
            f"fps={SAMPLE_FPS},scale=480:270:flags=lanczos",
            "-q:v",
            "2",
            str(output_dir / "%03d.jpg"),
        ]
    )
    return sorted(output_dir.glob("*.jpg"))


def mean_abs_difference(left: Image.Image, right: Image.Image) -> float:
    difference = ImageChops.difference(left.convert("L"), right.convert("L"))
    return float(ImageStat.Stat(difference).mean[0])


def sample_motion_metrics(frames: list[Path]) -> dict[str, object]:
    images = [Image.open(frame).convert("RGB") for frame in frames]
    try:
        adjacent = [mean_abs_difference(a, b) for a, b in zip(images, images[1:])]
        first_last = mean_abs_difference(images[0], images[-1]) if len(images) >= 2 else 0.0
        static_pairs = sum(value < 0.55 for value in adjacent)
        repeated_pairs = []
        for left_index, left in enumerate(images):
            for right_index in range(left_index + 4, len(images)):
                if mean_abs_difference(left, images[right_index]) < 0.45:
                    repeated_pairs.append([left_index + 1, right_index + 1])
        return {
            "sample_count": len(images),
            "adjacent_mad_min": min(adjacent) if adjacent else 0.0,
            "adjacent_mad_mean": sum(adjacent) / len(adjacent) if adjacent else 0.0,
            "adjacent_static_pairs": static_pairs,
            "first_last_mad": first_last,
            "near_duplicate_nonadjacent_pairs": repeated_pairs[:20],
        }
    finally:
        for image in images:
            image.close()


def build_contact_sheet(frames: list[Path], output: Path, asset_id: str) -> None:
    columns = 4
    rows = max(1, math.ceil(len(frames) / columns))
    tile_width = 480
    tile_height = 302
    sheet = Image.new("RGB", (columns * tile_width, rows * tile_height), "#F5F0E6")
    font_path = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    from PIL import ImageDraw, ImageFont

    font = ImageFont.truetype(str(font_path), 22) if font_path.is_file() else ImageFont.load_default()
    for index, frame_path in enumerate(frames):
        image = Image.open(frame_path).convert("RGB")
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height
        sheet.paste(image, (x, y))
        draw = ImageDraw.Draw(sheet)
        timecode = (index + 0.5) / SAMPLE_FPS
        label = f"{asset_id}  {timecode:04.1f}s"
        draw.rectangle((x, y + 270, x + tile_width, y + tile_height), fill="#173A66")
        draw.text((x + 14, y + 275), label, fill="#FFF9EF", font=font)
        image.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92, subsampling=0)


def inspect_asset(path: Path, project_dir: Path, qa_dir: Path) -> AssetFinding:
    asset_id = path.stem
    errors: list[str] = []
    warnings: list[str] = []
    technical: dict[str, object] = {"sha256": sha256(path)}
    contact_sheet: Path | None = None
    try:
        technical.update(probe(path))
        if technical["width"] < TARGET_WIDTH or technical["height"] < TARGET_HEIGHT:
            errors.append(
                f"native resolution {technical['width']}x{technical['height']} is below 1920x1080"
            )
        if abs((float(technical["width"]) / float(technical["height"])) - (16 / 9)) > 0.01:
            errors.append("aspect ratio is not 16:9")
        if not 23 <= float(technical["fps"]) <= 61:
            errors.append(f"unsupported frame rate: {technical['fps']}")
        if float(technical["duration"]) < 7.85:
            errors.append(f"clip is too short: {technical['duration']:.3f}s")
        if technical["field_order"] not in {None, "unknown", "progressive"}:
            errors.append(f"interlaced source: {technical['field_order']}")
        missing_color = [
            key
            for key in ("color_space", "color_transfer", "color_primaries")
            if not technical.get(key)
        ]
        if missing_color:
            warnings.append("missing source color tags; explicit Rec.709 conform required")
        full_decode(path)
        sample_dir = qa_dir / "frames" / asset_id
        frames = extract_samples(path, sample_dir)
        if len(frames) < max(12, int(float(technical["duration"]) * SAMPLE_FPS) - 1):
            errors.append(f"only {len(frames)} dense samples were extracted")
        if frames:
            motion = sample_motion_metrics(frames)
            technical["motion_samples"] = motion
            if int(motion["adjacent_static_pairs"]) >= max(3, len(frames) // 3):
                warnings.append("many near-static adjacent samples; inspect for freeze/hold")
            if motion["near_duplicate_nonadjacent_pairs"]:
                warnings.append("non-adjacent near-duplicate frames; inspect for loop/reverse")
            contact_sheet = qa_dir / "contact_sheets" / f"{asset_id}.jpg"
            build_contact_sheet(frames, contact_sheet, asset_id)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        errors.append(f"unreadable or corrupt media: {exc}")

    status = "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return AssetFinding(
        asset_id=asset_id,
        path=str(path.relative_to(project_dir)),
        status=status,
        errors=errors,
        warnings=warnings,
        technical=technical,
        contact_sheet=str(contact_sheet.relative_to(project_dir)) if contact_sheet else None,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--asset", action="append", help="Optional asset ID, for example V9_062")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    raw_dir = project_dir / "assets/flow_v9_raw"
    qa_dir = project_dir / "qa/v9/raw_asset_qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    wanted = set(args.asset or [])
    files = sorted(
        path for path in raw_dir.glob("V9_*.mp4") if not wanted or path.stem in wanted
    )
    if not files:
        raise SystemExit("No matching V9 raw assets")

    findings = [inspect_asset(path, project_dir, qa_dir) for path in files]
    digest_map: dict[str, list[AssetFinding]] = {}
    for finding in findings:
        digest = str(finding.technical.get("sha256", ""))
        if digest:
            digest_map.setdefault(digest, []).append(finding)
    for matching in digest_map.values():
        if len(matching) > 1:
            names = ", ".join(item.asset_id for item in matching)
            for item in matching:
                item.errors.append(f"exact duplicate binary across IDs: {names}")
                item.status = "FAIL"

    checked = len(findings)
    failed = sum(item.status == "FAIL" for item in findings)
    warned = sum(item.status == "PASS_WITH_WARNINGS" for item in findings)
    payload = {
        "schema_version": "1.0",
        "scope": sorted(wanted) if wanted else "all downloaded V9 raw assets",
        "sample_rate_fps": SAMPLE_FPS,
        "technical_status": "FAIL" if failed else ("PASS_WITH_WARNINGS" if warned else "PASS"),
        "manual_semantic_motion_status": "PENDING",
        "checked": checked,
        "failed": failed,
        "warnings": warned,
        "findings": [asdict(item) for item in findings],
    }
    report_json = qa_dir / "technical_report.json"
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# V9 raw footage technical QA",
        "",
        f"- Technical status: **{payload['technical_status']}**",
        f"- Checked: {checked}; failed: {failed}; warnings: {warned}",
        f"- Sampling: {SAMPLE_FPS} fps plus full-stream decode",
        "- Semantic/physics/manual motion status: **PENDING**",
        "",
        "| Asset | Technical | Resolution | Duration | Manual visual decision |",
        "|---|---:|---:|---:|---|",
    ]
    for item in findings:
        width = item.technical.get("width", "?")
        height = item.technical.get("height", "?")
        duration = item.technical.get("duration", 0)
        lines.append(
            f"| {item.asset_id} | {item.status} | {width}×{height} | {float(duration):.3f}s | PENDING |"
        )
    lines.extend(
        [
            "",
            "> A technical PASS never authorizes use. Each contact sheet and the complete motion must still be reviewed for anatomy, pseudo-text, causality, physical continuity, style, and relevance.",
        ]
    )
    (qa_dir / "technical_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("technical_status", "checked", "failed", "warnings")}, ensure_ascii=False))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
