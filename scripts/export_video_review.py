#!/usr/bin/env python3
"""Export labelled scene and shot frames from the actual delivery candidate."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from render_final_visuals import build_shots


def seconds(value: str) -> float:
    h, m, s = value.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def export(video: Path, output: Path, samples: list[tuple[str, float]]) -> None:
    output.mkdir(parents=True, exist_ok=True)

    def frame(sample: tuple[str, float]) -> None:
        name, timestamp = sample
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(timestamp),
            "-i", str(video), "-frames:v", "1", "-q:v", "2", str(output / f"{name}.jpg"),
        ], check=True)

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(frame, samples))
    face = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", 20, index=5)
    for start in range(0, len(samples), 20):
        group = samples[start:start + 20]
        sheet = Image.new("RGB", (1920, 1200), (8, 12, 17))
        for index, (name, timestamp) in enumerate(group):
            x, y = index % 4 * 480, index // 4 * 240
            with Image.open(output / f"{name}.jpg") as im:
                sheet.paste(ImageOps.contain(im.convert("RGB"), (480, 216)), (x, y + 24))
            ImageDraw.Draw(sheet).text((x + 8, y), f"{name}  {timestamp:.2f}s", font=face, fill="white")
        sheet.save(output / f"sheet_{start + 1:03d}_{start + len(group):03d}.jpg", quality=94)
    (output / "sample_times.json").write_text(json.dumps(samples, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    with (root / "02_storyboard.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    shots = build_shots(rows, root, root / "assets/final_overlays", root / "assets/final_stills", root / "video/final_work/segments")
    scene_samples = [(r["SCENE_ID"], (seconds(r["START_TIME"]) + seconds(r["END_TIME"])) / 2) for r in rows]
    shot_samples = []
    cursor = 0.0
    for shot in shots:
        shot_samples.append((f"{shot.scene_id}_{shot.shot_index:02d}", cursor + shot.duration / 2))
        cursor += shot.duration
    export(args.video.resolve(), args.output_dir / "scenes", scene_samples)
    export(args.video.resolve(), args.output_dir / "shots", shot_samples)
    print(f"Exported {len(scene_samples)} scene frames and {len(shot_samples)} shot frames from {args.video}")


if __name__ == "__main__":
    main()
