#!/usr/bin/env python3
"""Retime the 100-scene edit to the locked Vale voice master.

The first 95 scenes keep their established conceptual order.  Within each
chapter, prior scene word-density is used only as an editorial weight; exact
new narration words and their waveform-aligned timestamps are authoritative.
The last five scenes form a concise forty-second film credit sequence.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from build_aligned_subtitles import align_words, transcript_words, whisper_words


FPS = 30
GROUPS = [
    (1, 5),
    (6, 14),
    (15, 27),
    (28, 38),
    (39, 52),
    (53, 63),
    (64, 79),
    (80, 90),
    (91, 95),
]
CREDIT_DURATIONS_SECONDS = [6, 8, 18, 6, 2]


def stamp(frame: int) -> str:
    milliseconds = round(frame * 1000 / FPS)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def allocate_scene_word_starts(
    rows: list[dict[str, str]],
    section_words: list[str],
) -> list[int]:
    """Map old scene density onto a new chapter transcript.

    Boundaries are snapped to nearby punctuation so a scene does not switch in
    the middle of a sentence unless the chapter is unusually dense.
    """

    weights = [max(1, len(transcript_words(row["NARRATION"]))) for row in rows]
    total_weight = sum(weights)
    starts = [0]
    cumulative = 0
    for weight_index, weight in enumerate(weights[:-1], start=1):
        cumulative += weight
        ideal = round(len(section_words) * cumulative / total_weight)
        minimum = starts[-1] + 4
        maximum = len(section_words) - 4 * (len(weights) - weight_index)
        ideal = max(minimum, min(maximum, ideal))
        candidates = [
            index
            for index in range(max(minimum, ideal - 7), min(maximum, ideal + 7) + 1)
            if section_words[index - 1].endswith((".", "?", "!", ":", ";"))
        ]
        starts.append(min(candidates, key=lambda index: abs(index - ideal)) if candidates else ideal)
    return starts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--narration", type=Path, required=True)
    parser.add_argument("--sections", type=Path, required=True)
    parser.add_argument("--whisper-json", type=Path, required=True)
    parser.add_argument("--voice-duration", type=float, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    narration = args.narration.read_text(encoding="utf-8")
    exact_words = transcript_words(narration)
    observed = whisper_words(json.loads(args.whisper_json.read_text(encoding="utf-8")))
    aligned = align_words(exact_words, observed, args.voice_duration)
    sections = json.loads(args.sections.read_text(encoding="utf-8"))["sections"]

    with args.storyboard.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if len(rows) != 100 or [row["SCENE_ID"] for row in rows] != [f"S{i:03d}" for i in range(1, 101)]:
        raise SystemExit("Storyboard must contain the exact S001–S100 sequence")
    if len(sections) != len(GROUPS):
        raise SystemExit("Expected nine spoken sections")

    global_starts: list[int] = []
    section_cursor = 0
    for section, (first, last) in zip(sections, GROUPS):
        section_count = len(transcript_words(section["clean_text"]))
        section_words = exact_words[section_cursor : section_cursor + section_count]
        local_rows = rows[first - 1 : last]
        local_starts = allocate_scene_word_starts(local_rows, section_words)
        global_starts.extend(section_cursor + start for start in local_starts)
        section_cursor += section_count
    if section_cursor != len(exact_words) or len(global_starts) != 95:
        raise AssertionError("Spoken scene allocation does not cover the exact narration")

    credit_start_frame = round(args.voice_duration * FPS)
    scene_frames = [max(0, round(aligned[index].start * FPS) - 1) for index in global_starts]
    scene_frames[0] = 0
    scene_frames.append(credit_start_frame)
    # Whisper may assign an identical token timestamp to several neighboring
    # words.  Preserve editability by guaranteeing at least half a second per
    # voiced scene while keeping the final speech/credit boundary locked.
    for index in range(1, len(scene_frames) - 1):
        scene_frames[index] = max(scene_frames[index], scene_frames[index - 1] + 15)
    for index in range(len(scene_frames) - 2, 0, -1):
        scene_frames[index] = min(scene_frames[index], scene_frames[index + 1] - 15)
    cursor = credit_start_frame
    for duration in CREDIT_DURATIONS_SECONDS:
        cursor += duration * FPS
        scene_frames.append(cursor)

    report: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        start_frame, end_frame = scene_frames[index : index + 2]
        if end_frame - start_frame < 15:
            raise SystemExit(f"Scene too short after Vale alignment: {row['SCENE_ID']}")
        row["START_TIME"] = stamp(start_frame)
        row["END_TIME"] = stamp(end_frame)
        row["DURATION"] = f"{(end_frame - start_frame) / FPS:.6f}"
        if index < 95:
            word_start = global_starts[index]
            word_end = global_starts[index + 1] if index < 94 else len(exact_words)
            row["NARRATION"] = " ".join(exact_words[word_start:word_end])
        else:
            row["NARRATION"] = "Không lời — nhạc kết và credit."
        report.append(
            {
                "scene": row["SCENE_ID"],
                "start_frame": start_frame,
                "end_frame": end_frame,
                "duration": (end_frame - start_frame) / FPS,
                "narration": row["NARRATION"],
            }
        )

    credit_rows = rows[95:]
    credit_rows[0].update(
        ON_SCREEN_TEXT="MỘT PHIM TÀI LIỆU HỌC THUẬT CỦA NHÓM 14 | TRIẾT HỌC",
        SOURCE="Thông tin người dùng",
        PURPOSE="Mở credit theo ngôn ngữ điện ảnh, không chèm ghi chú kỹ thuật.",
    )
    credit_rows[1].update(
        ON_SCREEN_TEXT="MÔN: TRIẾT HỌC | LỚP: PH2001.26.1.CH.02 | GIẢNG VIÊN: TS. NGUYỄN HỮU SƠN",
        SOURCE="Thông tin người dùng",
        PURPOSE="Ghi đúng học phần và giảng viên.",
    )
    credit_rows[2].update(
        ON_SCREEN_TEXT="NHÓM 14 · THÀNH VIÊN | Chu Nam Thắng — 26848201 | Vũ Ngọc Quốc Khánh — 26848097 | Nguyễn Lưu Minh Đăng — 26848028 | Đặng Thị Thuý Hồng — 26848070 | Lâm Minh Thiện — 26848210 | Hoàng Vũ — 26848267 | Đào Hoàng Phúc — 26848169",
        SOURCE="Thông tin người dùng",
        PURPOSE="Credit đầy đủ thành viên và MSSV.",
    )
    credit_rows[3].update(
        VISUAL_TYPE="C — END CREDIT",
        VISUAL_DESCRIPTION="Lời cảm ơn lớn, sạch trên nền obsidian–navy; đường amber và teal hội tụ rồi dừng.",
        ON_SCREEN_TEXT="NHÓM 14 TRÂN TRỌNG CẢM ƠN THẦY VÀ CÁC BẠN ĐÃ THEO DÕI",
        SOURCE="Thông tin người dùng",
        PURPOSE="Kết thúc bằng lời cảm ơn, không hiện disclosure AI hay bibliography dài.",
    )
    credit_rows[4].update(
        VISUAL_TYPE="C — END CARD",
        VISUAL_DESCRIPTION="Nền obsidian sạch, một đường sáng mảnh tắt dần về đen.",
        ON_SCREEN_TEXT="",
        SOURCE="Nhóm 14",
        PURPOSE="Fade-out sạch cho file MP4 và YouTube.",
    )

    exact_rebuilt = " ".join(row["NARRATION"] for row in rows[:95])
    if exact_rebuilt != " ".join(exact_words):
        raise AssertionError("Scene narration no longer reconstructs the locked transcript")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(
            {
                "voice_duration": args.voice_duration,
                "credit_duration": sum(CREDIT_DURATIONS_SECONDS),
                "programme_duration": cursor / FPS,
                "scenes": report,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Vale voice: {args.voice_duration:.3f}s")
    print(f"Credits: {sum(CREDIT_DURATIONS_SECONDS)}s")
    print(f"Programme: {cursor / FPS:.3f}s ({stamp(cursor)})")
    if not args.apply:
        print("Dry run only; pass --apply to update the storyboard")
        return

    temporary = args.storyboard.with_suffix(".csv.vale.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, args.storyboard)
    print(f"Updated {args.storyboard}")


if __name__ == "__main__":
    main()
