#!/usr/bin/env python3
"""Audit the V8 picture plan before rebuilding the V9 visual edit.

The report is intentionally independent from rendered segment files. It reads
the locked scene plan and storyboard timings, then exposes every placement,
reuse count, and any shot whose planned duration exceeds its source motion.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from final_visual_plan import SCENE_ASSETS


FORBIDDEN_ASSETS = {
    "assets/editorial_selects/S014_affected_users_1080p.mp4": (
        "Người có bề mặt sáp/bột; người dùng yêu cầu loại hoàn toàn."
    ),
    "assets/flow_selected/S031_flow_1080p.mp4": (
        "Thao tác máy lặp liên tục; người dùng yêu cầu loại hoàn toàn."
    ),
    "assets/flow_v8_odoo/S031_meta_choice_ramp_1080p.mp4": (
        "Hành động đóng cửa khi cửa đã mở, sai quan hệ nhân quả vật lý."
    ),
}


@dataclass(frozen=True)
class Placement:
    scene_id: str
    shot_index: int
    asset: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    source_duration_seconds: float | None


def parse_timecode(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def format_timecode(value: float) -> str:
    milliseconds = round(value * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def probe_duration(path: Path) -> float | None:
    if path.suffix.lower() not in {".mp4", ".mov", ".mkv", ".webm"}:
        return None
    output = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    return float(json.loads(output)["format"]["duration"])


def load_storyboard(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Storyboard is empty: {path}")
    return rows


def build_placements(project_dir: Path, rows: list[dict[str, str]]) -> list[Placement]:
    duration_cache: dict[str, float | None] = {}
    placements: list[Placement] = []
    for row in rows:
        scene_id = row["SCENE_ID"]
        assets = SCENE_ASSETS.get(scene_id)
        if not assets:
            raise ValueError(f"No assets configured for {scene_id}")
        scene_start = parse_timecode(row["START_TIME"])
        scene_duration = float(row["DURATION"])
        frame_total = round(scene_duration * 30)
        frame_base, remainder = divmod(frame_total, len(assets))
        cursor = scene_start
        for zero_index, asset in enumerate(assets):
            frames = frame_base + (1 if zero_index < remainder else 0)
            duration = frames / 30
            if asset not in duration_cache:
                source = project_dir / asset
                if not source.is_file():
                    raise FileNotFoundError(source)
                duration_cache[asset] = probe_duration(source)
            placements.append(
                Placement(
                    scene_id=scene_id,
                    shot_index=zero_index + 1,
                    asset=asset,
                    start_seconds=cursor,
                    end_seconds=cursor + duration,
                    duration_seconds=duration,
                    source_duration_seconds=duration_cache[asset],
                )
            )
            cursor += duration
    return placements


def placement_flags(item: Placement, counts: Counter[str]) -> list[str]:
    flags: list[str] = []
    if item.asset in FORBIDDEN_ASSETS:
        flags.append("REJECT_USER")
    if counts[item.asset] > 2:
        flags.append("REPLACE_REUSE_GT_2")
    if (
        item.source_duration_seconds is not None
        and item.duration_seconds > item.source_duration_seconds + 1 / 30
    ):
        flags.append("PLACEMENT_EXCEEDS_SOURCE_MOTION")
    return flags or ["MANUAL_REVIEW"]


def write_placement_csv(path: Path, placements: list[Placement], counts: Counter[str]) -> None:
    fieldnames = [
        "scene_id",
        "shot_index",
        "start_time",
        "end_time",
        "placement_duration_seconds",
        "source_duration_seconds",
        "reuse_count",
        "asset",
        "status",
        "reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in placements:
            writer.writerow(
                {
                    "scene_id": item.scene_id,
                    "shot_index": item.shot_index,
                    "start_time": format_timecode(item.start_seconds),
                    "end_time": format_timecode(item.end_seconds),
                    "placement_duration_seconds": f"{item.duration_seconds:.3f}",
                    "source_duration_seconds": (
                        f"{item.source_duration_seconds:.3f}"
                        if item.source_duration_seconds is not None
                        else ""
                    ),
                    "reuse_count": counts[item.asset],
                    "asset": item.asset,
                    "status": "|".join(placement_flags(item, counts)),
                    "reason": FORBIDDEN_ASSETS.get(item.asset, ""),
                }
            )


def write_asset_csv(path: Path, placements: list[Placement], counts: Counter[str]) -> None:
    by_asset: dict[str, list[Placement]] = defaultdict(list)
    for item in placements:
        by_asset[item.asset].append(item)
    fieldnames = [
        "asset",
        "reuse_count",
        "scenes",
        "timestamps",
        "source_duration_seconds",
        "max_placement_duration_seconds",
        "decision",
        "reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for asset, items in sorted(by_asset.items(), key=lambda entry: (-len(entry[1]), entry[0])):
            flags = sorted({flag for item in items for flag in placement_flags(item, counts)})
            writer.writerow(
                {
                    "asset": asset,
                    "reuse_count": counts[asset],
                    "scenes": " | ".join(item.scene_id for item in items),
                    "timestamps": " | ".join(format_timecode(item.start_seconds) for item in items),
                    "source_duration_seconds": (
                        f"{items[0].source_duration_seconds:.3f}"
                        if items[0].source_duration_seconds is not None
                        else ""
                    ),
                    "max_placement_duration_seconds": f"{max(item.duration_seconds for item in items):.3f}",
                    "decision": "|".join(flags),
                    "reason": FORBIDDEN_ASSETS.get(asset, ""),
                }
            )


def write_markdown(path: Path, placements: list[Placement], counts: Counter[str]) -> None:
    repeated = [(asset, count) for asset, count in counts.most_common() if count > 2]
    forbidden_occurrences = [item for item in placements if item.asset in FORBIDDEN_ASSETS]
    overlong = [
        item
        for item in placements
        if item.source_duration_seconds is not None
        and item.duration_seconds > item.source_duration_seconds + 1 / 30
    ]
    lines = [
        "# V8 visual audit — đầu vào bắt buộc cho V9",
        "",
        "## Kết luận",
        "",
        f"- Tổng placement: **{len(placements)}**.",
        f"- Asset duy nhất: **{len(counts)}**.",
        f"- Asset xuất hiện quá 2 lần: **{len(repeated)}**.",
        f"- Placement thuộc asset người dùng cấm: **{len(forbidden_occurrences)}**.",
        f"- Placement dài hơn chuyển động nguồn: **{len(overlong)}**.",
        "- Trạng thái: **V8 KHÔNG ĐẠT visual gate V9; không được dùng kế hoạch này để promote.**",
        "",
        "## Asset lặp quá giới hạn",
        "",
        "| Lần | Asset | Scene |",
        "|---:|---|---|",
    ]
    by_asset: dict[str, list[Placement]] = defaultdict(list)
    for item in placements:
        by_asset[item.asset].append(item)
    for asset, count in repeated:
        scenes = ", ".join(item.scene_id for item in by_asset[asset])
        lines.append(f"| {count} | `{asset}` | {scenes} |")
    lines.extend(
        [
            "",
            "## Asset bị loại theo phản hồi trực tiếp",
            "",
            "| Asset | Timestamp/scene | Lý do |",
            "|---|---|---|",
        ]
    )
    for asset, reason in FORBIDDEN_ASSETS.items():
        items = by_asset.get(asset, [])
        locations = ", ".join(
            f"{format_timecode(item.start_seconds)} ({item.scene_id})" for item in items
        ) or "Không có placement"
        lines.append(f"| `{asset}` | {locations} | {reason} |")
    lines.extend(
        [
            "",
            "## Quyết định dựng V9",
            "",
            "- Không sửa cục bộ bốn timestamp. Tái phân bổ toàn bộ 100 scene.",
            "- Mọi asset V9 phải có reuse count ≤2; ưu tiên 1.",
            "- Mọi clip người thật phải được xem chuyển động và kiểm frame tối thiểu 2 fps trước khi chọn.",
            "- Không kéo placement quá thời lượng chuyển động nguồn; thêm shot khác hoặc ảnh/diagram có chủ đích.",
            "- Ba asset bị cấm không được xuất hiện trong plan, segment hoặc candidate V9.",
            "",
            "Chi tiết từng placement nằm trong `V8_PLACEMENT_AUDIT.csv`; tổng hợp theo asset nằm trong `V8_ASSET_REUSE_AUDIT.csv`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_storyboard(args.storyboard.resolve())
    placements = build_placements(project_dir, rows)
    counts = Counter(item.asset for item in placements)

    write_placement_csv(output_dir / "V8_PLACEMENT_AUDIT.csv", placements, counts)
    write_asset_csv(output_dir / "V8_ASSET_REUSE_AUDIT.csv", placements, counts)
    write_markdown(output_dir / "V8_VISUAL_AUDIT.md", placements, counts)
    print(
        f"Audited {len(placements)} placements across {len(counts)} assets; "
        f"{sum(1 for count in counts.values() if count > 2)} assets exceed reuse limit."
    )


if __name__ == "__main__":
    main()
