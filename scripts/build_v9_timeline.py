#!/usr/bin/env python3
"""Insert deliberate music/visual breaths without altering the Vale delivery.

The locked V7 voice remains the only narration source. This script inserts
silence at scene boundaries, shifts subtitle cues, and writes a V9 storyboard
copy. It never edits the submission deliverables in place.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path


PAUSES_AFTER_SCENE = {
    "S005": 3.5,
    "S014": 4.0,
    "S027": 3.5,
    "S038": 4.0,
    "S052": 4.0,
    "S063": 4.0,
    "S079": 5.0,
    "S090": 4.5,
}


def parse_storyboard_time(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def storyboard_time(value: float) -> str:
    milliseconds = round(value * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def parse_srt_time(value: str) -> float:
    hours, minutes, remainder = value.split(":")
    seconds, milliseconds = remainder.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000


def srt_time(value: float) -> str:
    milliseconds = round(value * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def load_storyboard(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    if not rows:
        raise ValueError(f"Storyboard is empty: {path}")
    return fieldnames, rows


def srt_cue_ranges(path: Path) -> list[tuple[float, float]]:
    pattern = re.compile(
        r"(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})"
    )
    return [
        (parse_srt_time(match.group("start")), parse_srt_time(match.group("end")))
        for match in pattern.finditer(path.read_text(encoding="utf-8"))
    ]


def pause_boundaries(
    rows: list[dict[str, str]], subtitle_path: Path
) -> list[dict[str, float | str]]:
    cue_ranges = srt_cue_ranges(subtitle_path)
    safe_gaps = [
        ((previous[1] + current[0]) / 2, previous[1], current[0])
        for previous, current in zip(cue_ranges, cue_ranges[1:])
        if current[0] - previous[1] >= 0.08
    ]
    boundaries: list[dict[str, float | str]] = []
    for row in rows:
        scene_id = row["SCENE_ID"]
        if scene_id in PAUSES_AFTER_SCENE:
            target = parse_storyboard_time(row["END_TIME"])
            source_time, gap_start, gap_end = min(
                safe_gaps,
                key=lambda gap: abs(gap[0] - target),
            )
            if abs(source_time - target) > 1.25:
                raise ValueError(
                    f"No safe subtitle gap near {scene_id} boundary {target:.3f}s"
                )
            boundaries.append(
                {
                    "scene_id": scene_id,
                    "storyboard_boundary": target,
                    "source_time": source_time,
                    "source_gap_start": gap_start,
                    "source_gap_end": gap_end,
                    "duration": PAUSES_AFTER_SCENE[scene_id],
                }
            )
    if len(boundaries) != len(PAUSES_AFTER_SCENE):
        found = {item["scene_id"] for item in boundaries}
        raise ValueError(f"Missing pause scenes: {sorted(set(PAUSES_AFTER_SCENE) - found)}")
    return boundaries


def render_voice(source: Path, output: Path, boundaries: list[dict[str, float | str]]) -> None:
    probe = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(source),
        ],
        text=True,
    )
    source_duration = float(probe.strip())
    split_points = [0.0, *[float(item["source_time"]) for item in boundaries], source_duration]
    if split_points != sorted(split_points) or split_points[-2] >= source_duration:
        raise ValueError("Pause points must be increasing and inside the voice master")

    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, (start, end) in enumerate(zip(split_points, split_points[1:])):
        filters.append(
            f"[0:a]atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS[voice{index}]"
        )
        concat_inputs.append(f"[voice{index}]")
        if index < len(boundaries):
            pause_duration = float(boundaries[index]["duration"])
            filters.append(
                "anullsrc=r=48000:cl=stereo,"
                f"atrim=duration={pause_duration:.6f},asetpts=PTS-STARTPTS[pause{index}]"
            )
            concat_inputs.append(f"[pause{index}]")
    filters.append(
        "".join(concat_inputs)
        + f"concat=n={len(concat_inputs)}:v=0:a=1[out]"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-c:a",
            "pcm_s24le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(output),
        ],
        check=True,
    )


def cumulative_shift(value: float, boundaries: list[dict[str, float | str]]) -> float:
    return sum(float(item["duration"]) for item in boundaries if value >= float(item["source_time"]))


def shift_srt(source: Path, output: Path, boundaries: list[dict[str, float | str]]) -> int:
    pattern = re.compile(
        r"(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})"
    )
    text = source.read_text(encoding="utf-8")
    cue_count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal cue_count
        cue_count += 1
        start = parse_srt_time(match.group("start"))
        end = parse_srt_time(match.group("end"))
        for item in boundaries:
            boundary = float(item["source_time"])
            if start < boundary < end:
                raise ValueError(
                    f"Subtitle cue {cue_count} crosses pause boundary at {boundary:.3f}s"
                )
        return (
            f"{srt_time(start + cumulative_shift(start, boundaries))} --> "
            f"{srt_time(end + cumulative_shift(end, boundaries))}"
        )

    shifted = pattern.sub(replace, text)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(shifted, encoding="utf-8")
    return cue_count


def shift_storyboard(
    fieldnames: list[str],
    rows: list[dict[str, str]],
    output: Path,
) -> float:
    shift = 0.0
    for row in rows:
        original_start = parse_storyboard_time(row["START_TIME"])
        original_duration = float(row["DURATION"])
        pause = PAUSES_AFTER_SCENE.get(row["SCENE_ID"], 0.0)
        row["START_TIME"] = storyboard_time(original_start + shift)
        row["DURATION"] = f"{original_duration + pause:.6f}"
        row["END_TIME"] = storyboard_time(original_start + shift + original_duration + pause)
        if pause:
            row["SOUND"] = (
                row.get("SOUND", "").rstrip()
                + f"; nhịp thở hình/nhạc {pause:.1f}s, không kéo chậm giọng"
            ).lstrip("; ")
        shift += pause
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return parse_storyboard_time(rows[-1]["END_TIME"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, required=True)
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()

    fieldnames, rows = load_storyboard(project_dir / "02_storyboard.csv")
    subtitle_source = project_dir / "05_subtitles.srt"
    boundaries = pause_boundaries(rows, subtitle_source)
    output_dir = project_dir / "qa/v9"
    voice_output = project_dir / "audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav"
    srt_output = output_dir / "05_subtitles_v9.srt"
    storyboard_output = output_dir / "02_storyboard_v9.csv"

    render_voice(
        project_dir / "audio/vo/vale_unified_v7/VO_VALE_UNIFIED_V7_48K.wav",
        voice_output,
        boundaries,
    )
    cue_count = shift_srt(subtitle_source, srt_output, boundaries)
    final_duration = shift_storyboard(fieldnames, rows, storyboard_output)

    voice_duration = float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(voice_output),
            ],
            text=True,
        ).strip()
    )
    manifest = {
        "schema_version": "1.0",
        "source_voice": "audio/vo/vale_unified_v7/VO_VALE_UNIFIED_V7_48K.wav",
        "output_voice": str(voice_output.relative_to(project_dir)),
        "voice_duration_seconds": voice_duration,
        "final_program_duration_seconds": final_duration,
        "subtitle_cues": cue_count,
        "pauses": boundaries,
        "total_inserted_pause_seconds": sum(float(item["duration"]) for item in boundaries),
        "narration_processing": "Only digital silence inserted; no time-stretch, pitch shift, splice from another voice, or new words.",
    }
    (output_dir / "V9_TIMELINE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"V9 timeline: {voice_duration:.3f}s voice, {final_duration:.3f}s program, "
        f"{cue_count} subtitle cues, {manifest['total_inserted_pause_seconds']:.1f}s inserted."
    )


if __name__ == "__main__":
    main()
