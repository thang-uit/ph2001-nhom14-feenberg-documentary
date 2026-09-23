#!/usr/bin/env python3
"""Render an alpha subtitle track without requiring FFmpeg's libass filter."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1920
HEIGHT = 1080
FPS = 30
FONT_PATH = Path("/System/Library/Fonts/Avenir Next.ttc")


def parse_seconds(value: str) -> float:
    hours, minutes, seconds = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_srt(path: Path) -> list[dict[str, object]]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    cues: list[dict[str, object]] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            raise ValueError(f"Invalid SRT block: {block}")
        start_text, end_text = (item.strip() for item in lines[1].split("-->", 1))
        cues.append(
            {
                "start": parse_seconds(start_text),
                "end": parse_seconds(end_text),
                "lines": lines[2:],
            }
        )
    return cues


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size, index=0)


def render_card(lines: list[str], path: Path) -> None:
    if not 1 <= len(lines) <= 2:
        raise ValueError(f"Subtitle must contain one or two lines: {lines}")
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    subtitle_font = font(48)
    line_height = 60
    boxes = [draw.textbbox((0, 0), line, font=subtitle_font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    box_width = max(widths) + 76
    box_height = len(lines) * line_height + 24
    x0 = (WIDTH - box_width) // 2
    # Keep captions inside the 8% title-safe area so classroom projectors and
    # YouTube controls do not cover the lower line.
    y1 = HEIGHT - 86
    y0 = y1 - box_height
    draw.rounded_rectangle(
        (x0, y0, x0 + box_width, y1),
        radius=16,
        fill=(0, 0, 0, 190),
    )
    y = y0 + 10
    for line, width in zip(lines, widths):
        draw.text(((WIDTH - width) // 2, y), line, font=subtitle_font, fill=(247, 244, 237, 255))
        y += line_height
    image.save(path)


def ffconcat_quote(path: Path) -> str:
    return str(path.resolve()).replace("'", "'\\''")


def build_overlay(srt: Path, output: Path, work_dir: Path, start: float, duration: float) -> None:
    if start < 0 or duration <= 0:
        raise ValueError("start must be non-negative and duration must be positive")
    work_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    blank_path = work_dir / "subtitle_blank.png"
    Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)).save(blank_path)

    range_end = start + duration
    segments: list[tuple[Path, float]] = []
    cursor = start
    cue_number = 0
    for cue in parse_srt(srt):
        cue_start = max(float(cue["start"]), start)
        cue_end = min(float(cue["end"]), range_end)
        if cue_end <= cue_start:
            continue
        if cue_start < cursor - 0.001:
            raise ValueError(f"Overlapping subtitle cue at {cue_start:.3f}s")
        if cue_start > cursor + 0.001:
            segments.append((blank_path, cue_start - cursor))
        cue_number += 1
        cue_path = work_dir / f"subtitle_{cue_number:04d}.png"
        render_card(list(cue["lines"]), cue_path)
        segments.append((cue_path, cue_end - cue_start))
        cursor = cue_end
    if cursor < range_end - 0.001:
        segments.append((blank_path, range_end - cursor))
    if not segments:
        segments.append((blank_path, duration))

    concat_path = work_dir / "subtitles.ffconcat"
    lines = ["ffconcat version 1.0"]
    for path, segment_duration in segments:
        lines.append(f"file '{ffconcat_quote(path)}'")
        lines.append(f"duration {segment_duration:.6f}")
    lines.append(f"file '{ffconcat_quote(segments[-1][0])}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-vf",
        f"fps={FPS},format=rgba",
        "-t",
        f"{duration:.6f}",
        "-an",
        "-c:v",
        "qtrle",
        "-pix_fmt",
        "argb",
        str(output),
    ]
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--duration", type=float, required=True)
    args = parser.parse_args()
    build_overlay(
        args.srt.resolve(),
        args.output.resolve(),
        args.work_dir.resolve(),
        args.start,
        args.duration,
    )
    print(f"Subtitle overlay rendered: {args.output.resolve()}")


if __name__ == "__main__":
    main()
