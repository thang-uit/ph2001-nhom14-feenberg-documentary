#!/opt/homebrew/bin/python3.13
"""Create the semantic-first V11 storyboard and 41-second credit timeline."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from v11_visual_plan import SCENE_ASSETS, category


CONTENT_SCENES = 95
CREDIT_DURATION = 41.033333
CREDIT_ASSET = "renders/credit_tphcm/archive_20260912_v2/CREDIT_TPHCM_OH_YEAH_v2.mp4"


def parse(value: str) -> float:
    h, m, s = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def stamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    h, remain = divmod(millis, 3_600_000)
    m, remain = divmod(remain, 60_000)
    s, ms = divmod(remain, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def type_label(assets: list[str]) -> str:
    categories = {category(asset) for asset in assets}
    labels = []
    for key, label in (
        ("verified_real_photo", "ẢNH NGƯỜI THẬT ĐÃ XÁC MINH"),
        ("instructor_source_card", "TÀI LIỆU NGUỒN"),
        ("deterministic_motion_graphic", "ĐỒ HỌA GIẢI THÍCH"),
        ("real_footage", "FOOTAGE QUAY THẬT"),
        ("veo_flow_illustration", "MINH HỌA FLOW–VEO"),
    ):
        if key in categories:
            labels.append(label)
    return "V11 · " + " + ".join(labels)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()

    with args.source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    content = [dict(row) for row in rows if row["SCENE_ID"].startswith("S")][:CONTENT_SCENES]
    expected = [f"S{i:03d}" for i in range(1, CONTENT_SCENES + 1)]
    if [row["SCENE_ID"] for row in content] != expected:
        raise SystemExit("Source storyboard does not contain contiguous S001–S095")
    if "VISUAL_ARGUMENT_LINK" not in fields:
        fields.append("VISUAL_ARGUMENT_LINK")

    for row in content:
        sid = row["SCENE_ID"]
        assets = SCENE_ASSETS[sid]
        argument_link = row.get("PURPOSE", "").strip()
        if not argument_link:
            raise SystemExit(f"Missing PURPOSE/semantic link for {sid}")
        row["VISUAL_TYPE"] = type_label(assets)
        row["VISUAL_DESCRIPTION"] = (
            f"Chuỗi hình V11 khớp trực tiếp luận điểm: {argument_link} "
            f"Asset: {', '.join(Path(asset).name for asset in assets)}."
        )
        row["SOURCE"] = " | ".join(assets)
        row["ASSET_STATUS"] = "V11_PLAN_LOCKED · MOTION_AND_SEMANTIC_QA_REQUIRED"
        row["TRANSITION"] = "Dissolve 0,25 giây có kiểm soát; không loop/reverse hành động"
        row["AS_BUILT_SHOTS"] = "V11 plan: " + " | ".join(assets)
        row["CAMERA_METADATA_STATUS"] = "Nguồn thật giữ chuyển động gốc; AI là minh họa, không phải bằng chứng lịch sử"
        row["VISUAL_ARGUMENT_LINK"] = argument_link

    content_duration = parse(content[-1]["END_TIME"])
    credit = {field: "" for field in fields}
    credit.update(
        {
            "SCENE_ID": "CREDIT_V11",
            "START_TIME": stamp(content_duration),
            "END_TIME": stamp(content_duration + CREDIT_DURATION),
            "DURATION": f"{CREDIT_DURATION:.6f}",
            "NARRATION": "Không lời — credit điện ảnh và nhạc Oh Yeah.",
            "VISUAL_TYPE": "C — END CREDIT",
            "VISUAL_DESCRIPTION": "Credit 41 giây riêng biệt, đủ lớp, giảng viên, thành viên và lời cảm ơn.",
            "CAMERA": "Theo artifact credit v2 đã chọn",
            "LENS_PERSPECTIVE": "Theo artifact credit v2 đã chọn",
            "MOVEMENT": "Montage credit; chuyển động gốc, không lặp",
            "LIGHTING": "Grade điện ảnh riêng của credit",
            "COMPOSITION": "Typography title-safe, đủ thời gian đọc",
            "ON_SCREEN_TEXT": "NHÓM 14 · CẢM ƠN THẦY VÀ CÁC BẠN",
            "SOURCE": CREDIT_ASSET,
            "ASSET_STATUS": "LOCKED_CREDIT_ARTIFACT · 41.033333 GIÂY",
            "TRANSITION": "Crossfade hình và nhạc 0,80 giây từ câu cảm ơn",
            "SOUND": "Audio Oh Yeah tích hợp trong artifact; không lời; không page-turn SFX",
            "PURPOSE": "Kết phim bằng credit điện ảnh ngắn gọn, không disclosure kỹ thuật.",
            "AS_BUILT_SHOTS": CREDIT_ASSET,
            "AS_BUILT_SOUND": "Audio tích hợp trong credit v2",
            "CAMERA_METADATA_STATUS": "Theo hồ sơ dựng credit riêng",
            "VISUAL_ARGUMENT_LINK": "Ghi nhận giảng viên và Nhóm 14 sau khi luận giải đã khép lại.",
        }
    )
    out_rows = content + [credit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    manifest = {
        "schema_version": "v11-timeline-1",
        "content_scene_count": CONTENT_SCENES,
        "content_duration_seconds": content_duration,
        "credit_duration_seconds": CREDIT_DURATION,
        "crossfade_seconds": 0.8,
        "programme_duration_seconds": content_duration + CREDIT_DURATION - 0.8,
        "credit_asset": CREDIT_ASSET,
        "subtitle_source": "qa/v9/05_subtitles_v9.srt",
        "voice_source": "audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav",
        "semantic_field": "VISUAL_ARGUMENT_LINK",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
