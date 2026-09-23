#!/usr/bin/env python3
"""Redistribute storyboard scene durations across the locked chapter timing."""

from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path


GROUPS = [
    # The nine voiced groups follow waveform-aligned section boundaries from
    # VO_CHATGPT_170WPM_48K.wav.  Values are rounded to whole seconds because
    # the storyboard is an editorial document; final subtitle timings retain
    # millisecond precision from the actual voice waveform.
    (1, 5, 41),
    (6, 14, 74),
    (15, 27, 93),
    (28, 38, 88),
    (39, 52, 111),
    (53, 63, 102),
    (64, 79, 174),
    (80, 90, 118),
    (91, 95, 58),
    # 58 seconds of readable film-style credits keep the finished programme
    # safely above the lecturer's 15-minute minimum without stretching speech.
    (96, 100, 58),
]
EXPECTED_TOTAL_SECONDS = 15 * 60 + 17


def parse_hhmmss(value: str) -> int:
    hours, minutes, seconds = (int(part) for part in value.split(":"))
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"Invalid HH:MM:SS timestamp: {value}")
    return hours * 3600 + minutes * 60 + seconds


def format_hhmmss(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def allocate_durations(original: list[int], target_total: int) -> list[int]:
    original_total = sum(original)
    if original_total <= 0:
        raise ValueError("Original duration total must be positive")
    exact = [duration * target_total / original_total for duration in original]
    allocated = [max(1, math.floor(value)) for value in exact]
    remainder = target_total - sum(allocated)
    if remainder < 0:
        raise ValueError("Target duration is too small for one-second minimum scenes")
    ranking = sorted(
        range(len(original)),
        key=lambda index: (exact[index] - math.floor(exact[index]), original[index], -index),
        reverse=True,
    )
    for index in ranking[:remainder]:
        allocated[index] += 1
    if sum(allocated) != target_total:
        raise AssertionError("Largest-remainder allocation failed")
    return allocated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    storyboard = args.storyboard.resolve()
    if not storyboard.is_file():
        raise SystemExit(f"Storyboard not found: {storyboard}")

    with storyboard.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if fieldnames is None or len(rows) != 100:
        raise SystemExit("Storyboard must contain one header and exactly 100 scenes")

    expected_ids = [f"S{index:03d}" for index in range(1, 101)]
    actual_ids = [row["SCENE_ID"] for row in rows]
    if actual_ids != expected_ids:
        raise SystemExit("Storyboard scene IDs are not the exact S001–S100 sequence")

    cursor = 0
    for first, last, target_total in GROUPS:
        group_rows = rows[first - 1 : last]
        original = [int(row["DURATION"]) for row in group_rows]
        allocated = allocate_durations(original, target_total)
        for row, duration in zip(group_rows, allocated):
            row["START_TIME"] = format_hhmmss(cursor)
            cursor += duration
            row["END_TIME"] = format_hhmmss(cursor)
            row["DURATION"] = str(duration)
        print(
            f"S{first:03d}–S{last:03d}: {target_total:3d}s -> "
            f"{group_rows[0]['START_TIME']}–{group_rows[-1]['END_TIME']}"
        )

    if cursor != EXPECTED_TOTAL_SECONDS:
        raise SystemExit(
            f"Retimed total is {cursor}s, expected {EXPECTED_TOTAL_SECONDS}s"
        )

    previous_end = 0
    for row in rows:
        start = parse_hhmmss(row["START_TIME"])
        end = parse_hhmmss(row["END_TIME"])
        duration = int(row["DURATION"])
        if start != previous_end or end - start != duration or duration <= 0:
            raise SystemExit(f"Timeline invariant failed at {row['SCENE_ID']}")
        previous_end = end

    if not args.apply:
        print("Dry run only. Pass --apply to update the storyboard.")
        return

    temporary = storyboard.with_suffix(".csv.retime.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, storyboard)
    print(f"Updated {storyboard}")


if __name__ == "__main__":
    main()
