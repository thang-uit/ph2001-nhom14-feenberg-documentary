#!/usr/bin/env python3
"""Create the V10 content+credit storyboard without touching V8/V9 files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse(value: str) -> float:
    h, m, s = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def stamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()

    with args.source.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
        fields = list(fh.seek(0) or []) if False else None
    if len(rows) < 95:
        raise SystemExit("V9 storyboard has fewer than 95 content scenes")
    content = [dict(row) for row in rows[:95]]
    # Preserve the already waveform-aligned V9 timings and words exactly.
    content_duration = parse(content[-1]["END_TIME"])
    credit_duration = 54.1
    credit = {
        key: "" for key in (rows[0].keys() if rows else [])
    }
    credit.update(
        {
            "SCENE_ID": "CREDIT_V4",
            "START_TIME": stamp(content_duration),
            "END_TIME": stamp(content_duration + credit_duration),
            "DURATION": f"{credit_duration:.6f}",
            "NARRATION": "Không lời — nhạc Oh Yeah và credit điện ảnh.",
            "VISUAL_TYPE": "C — END CREDIT",
            "VISUAL_DESCRIPTION": "CREDIT_TPHCM_OH_YEAH_V4.mp4; montage TP.HCM quay thật, credit Nhóm 14 và lời cảm ơn.",
            "CAMERA": "Theo artifact credit V4",
            "LENS_PERSPECTIVE": "Theo artifact credit V4",
            "MOVEMENT": "Dissolve nội bộ 0,45 s",
            "LIGHTING": "Grade vàng–olive đã QA trong artifact V4",
            "COMPOSITION": "Typography title-safe theo artifact V4",
            "ON_SCREEN_TEXT": "CREDIT V4 · NHÓM 14 · CẢM ƠN THẦY VÀ CÁC BẠN",
            "SOURCE": "CREDIT_TPHCM_OH_YEAH_V4.mp4; oh-yeah.mp3",
            "ASSET_STATUS": "LOCKED_ARTIFACT_QA_PASS",
            "TRANSITION": "Crossfade hình/nhạc 0,80 s từ kết luận sang credit",
            "SOUND": "Oh Yeah trong artifact V4; nhạc nội dung hạ trước điểm nối",
            "PURPOSE": "Kết phim bằng credit điện ảnh, không thêm disclosure kỹ thuật.",
            "AS_BUILT_SHOTS": "CREDIT_V4 @ content end; 54.100s",
            "AS_BUILT_SOUND": "Audio tích hợp trong CREDIT_TPHCM_OH_YEAH_V4.mp4",
            "CAMERA_METADATA_STATUS": "Theo hồ sơ QA credit V4",
        }
    )
    out_rows = content + [credit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)
    manifest = {
        "schema_version": "1.0",
        "content_scene_count": 95,
        "credit_artifact": "CREDIT_TPHCM_OH_YEAH_V4.mp4",
        "content_duration_seconds": content_duration,
        "credit_duration_seconds": credit_duration,
        "programme_duration_seconds": content_duration + credit_duration,
        "subtitle_source": "qa/v9/05_subtitles_v9.srt",
        "voice_source": "audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav",
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
