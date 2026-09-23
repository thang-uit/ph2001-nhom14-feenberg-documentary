#!/usr/bin/env python3
"""Render the locked scene plan into a 1080p/30fps picture master."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from final_visual_plan import (
    CHAPTER_FADE_SCENES,
    EXTRA_OVERLAYS,
    FULL_GRAPHIC_SCENES,
    REVERSIBLE_ASSETS,
    SCENE_ASSETS,
    SOURCE_SCENES,
    VIDEO_POST_FILTERS,
    VIDEO_TRIM_START,
    validate_plan,
)


WIDTH = 1920
HEIGHT = 1080
FPS = 30


@dataclass(frozen=True)
class Shot:
    scene_id: str
    scene_number: int
    shot_index: int
    frames: int
    relative_asset: str
    source_asset: Path
    output: Path
    generic_overlay: Path | None
    extra_overlay: Path | None
    fade_scene: bool
    provenance_overlay: Path | None = None

    @property
    def duration(self) -> float:
        return self.frames / FPS


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def probe_media(path: Path) -> dict[str, object]:
    output = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,r_frame_rate:format=duration",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    data = json.loads(output)
    if not data.get("streams"):
        raise ValueError(f"No video/image stream: {path}")
    stream = data["streams"][0]
    return {
        "width": int(stream.get("width", 0)),
        "height": int(stream.get("height", 0)),
        "duration": float(data.get("format", {}).get("duration", 0) or 0),
    }


def resolve_asset(project_dir: Path, still_dir: Path, scene_id: str, shot_index: int, relative: str) -> Path:
    if scene_id in SOURCE_SCENES and relative.lower().endswith((".png", ".jpg", ".jpeg")):
        card = still_dir / f"{scene_id}_{shot_index:02d}_source_card.jpg"
        if not card.is_file():
            raise FileNotFoundError(card)
        return card
    path = project_dir / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def build_shots(
    rows: list[dict[str, str]],
    project_dir: Path,
    overlay_dir: Path,
    still_dir: Path,
    segment_dir: Path,
) -> list[Shot]:
    validate_plan([row["SCENE_ID"] for row in rows])
    segment_dir.mkdir(parents=True, exist_ok=True)
    shots: list[Shot] = []
    for row in rows:
        scene_id = row["SCENE_ID"]
        scene_number = int(scene_id[1:])
        total_frames = round(float(row["DURATION"]) * FPS)
        relative_assets = SCENE_ASSETS[scene_id]
        frame_base, remainder = divmod(total_frames, len(relative_assets))
        generic = overlay_dir / f"{scene_id}_overlay.png"
        generic_overlay = generic if generic.is_file() and scene_id not in FULL_GRAPHIC_SCENES | SOURCE_SCENES | set(EXTRA_OVERLAYS) else None
        extra_relative = EXTRA_OVERLAYS.get(scene_id)
        extra_overlay = project_dir / extra_relative if extra_relative else None
        if extra_overlay is not None and not extra_overlay.is_file():
            raise FileNotFoundError(extra_overlay)
        for zero_index, relative in enumerate(relative_assets):
            shot_index = zero_index + 1
            frames = frame_base + (1 if zero_index < remainder else 0)
            is_diagram = relative.startswith(("assets/motion/", "assets/graphics/"))
            provenance = overlay_dir / f"{scene_id}_{shot_index:02d}_provenance.png"
            shots.append(
                Shot(
                    scene_id=scene_id,
                    scene_number=scene_number,
                    shot_index=shot_index,
                    frames=frames,
                    relative_asset=relative,
                    source_asset=resolve_asset(project_dir, still_dir, scene_id, shot_index, relative),
                    output=segment_dir / f"{scene_id}_{shot_index:02d}.mp4",
                    # A scene heading appears once at the start of the scene;
                    # repeating the same card after every editorial cut would
                    # turn the sequence back into a slide presentation.
                    generic_overlay=generic_overlay if zero_index == 0 and not is_diagram else None,
                    extra_overlay=extra_overlay if not is_diagram else None,
                    fade_scene=scene_id in CHAPTER_FADE_SCENES and zero_index == 0,
                    provenance_overlay=provenance if provenance.is_file() else None,
                )
            )
    return shots


def still_filter(width: int, height: int, duration: float) -> str:
    if width >= WIDTH * 1.35 and height >= HEIGHT * 1.35:
        increment = 0.000045 if duration >= 9 else 0.000065
        return (
            f"zoompan=z='min(zoom+{increment:.6f},1.018)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d=1:s={WIDTH}x{HEIGHT}:fps={FPS},setsar=1"
        )
    # 1080p source cards remain at native size.  This deliberately avoids a
    # cosmetic digital zoom that would enlarge already-rasterized evidence.
    return (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#0B0F14,"
        f"fps={FPS},setsar=1"
    )


def video_filter(shot: Shot, info: dict[str, object]) -> str:
    duration = shot.duration
    source_duration = float(info["duration"])
    trim_floor = VIDEO_TRIM_START.get((shot.scene_id, shot.relative_asset), 0.0)
    available = max(0.1, source_duration - trim_floor)
    filters: list[str] = []

    if duration <= available:
        spare = max(0.0, available - duration)
        phase = ((shot.scene_number * 17 + shot.shot_index * 11) % 101) / 100
        start = trim_floor + spare * phase
        filters.append(f"trim=start={start:.6f}:duration={duration:.6f}")
        filters.append("setpts=PTS-STARTPTS")
    else:
        speed_ratio = min(duration / available, 1.25)
        moving_duration = available * speed_ratio
        hold_duration = max(0.0, duration - moving_duration)
        filters.append(f"trim=start={trim_floor:.6f}:duration={available:.6f}")
        if shot.relative_asset in REVERSIBLE_ASSETS and shot.shot_index % 2 == 0:
            filters.append("reverse")
        filters.append(f"setpts=(PTS-STARTPTS)*{speed_ratio:.8f}")
        if hold_duration > 0.001:
            filters.append(f"tpad=stop_mode=clone:stop_duration={hold_duration:.6f}")
        filters.append(f"trim=duration={duration:.6f}")

    width = int(info["width"])
    height = int(info["height"])
    if width < WIDTH or height < HEIGHT:
        # Preserve 720p material at native pixel dimensions.  It is shown as a
        # sourced panel instead of being silently enlarged to fill the master.
        # Retain provider attribution, including the region-required visible
        # watermark shown by Flow.  No enlargement of native 720p material.
        visible_width = width
        visible_height = height
        x = (WIDTH - visible_width) // 2
        y = (HEIGHT - visible_height) // 2
        filters.extend(
            [
                "setsar=1",
                f"pad={WIDTH}:{HEIGHT}:{x}:{y}:color=#0B0F14",
            ]
        )
    else:
        filters.extend(
            [
                f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos",
                f"crop={WIDTH}:{HEIGHT}",
                "setsar=1",
            ]
        )
    filters.extend([f"fps={FPS}"])
    if shot.relative_asset.startswith("assets/flow_v8_namthanguit/"):
        # Conform the brighter alternate Flow batch to the same restrained
        # amber/teal documentary world as the Odoo and legacy selects.
        filters.append("eq=contrast=1.08:brightness=-0.035:saturation=0.92:gamma=0.96")
    elif shot.relative_asset.startswith("assets/flow_v8_odoo/"):
        filters.append("eq=contrast=1.05:brightness=-0.012:saturation=0.98:gamma=0.985")
    else:
        filters.append("eq=contrast=1.035:brightness=-0.006:saturation=1.045:gamma=0.995")
    filters.append("vignette=PI/7.5:eval=frame")
    filters.extend(VIDEO_POST_FILTERS.get((shot.scene_id, shot.relative_asset), ()))
    if shot.relative_asset.startswith("assets/motion/"):
        # Reserve space for captions below the diagram's lowest annotation.
        filters.extend(["scale=1728:972:flags=lanczos", "pad=1920:1080:96:0:color=#080C11"])
    return ",".join(filters)


def render_shot(shot: Shot, force: bool) -> tuple[str, Path]:
    if shot.output.is_file() and not force:
        return "cached", shot.output

    suffix = shot.source_asset.suffix.lower()
    is_still = suffix in {".png", ".jpg", ".jpeg", ".webp"}
    inputs: list[str] = []
    if is_still:
        inputs.extend(["-loop", "1", "-framerate", str(FPS), "-i", str(shot.source_asset)])
        still_info = probe_media(shot.source_asset)
        base_filter = still_filter(int(still_info["width"]), int(still_info["height"]), shot.duration)
    else:
        inputs.extend(["-i", str(shot.source_asset)])
        base_filter = video_filter(shot, probe_media(shot.source_asset))

    overlays = [item for item in (shot.generic_overlay, shot.extra_overlay, shot.provenance_overlay) if item is not None]
    for overlay in overlays:
        inputs.extend(["-loop", "1", "-framerate", str(FPS), "-i", str(overlay)])

    graph: list[str] = [f"[0:v]{base_filter},format=yuv420p[base0]"]
    previous = "base0"
    for index, overlay in enumerate(overlays, start=1):
        overlay_label = f"ov{index}"
        out_label = f"base{index}"
        is_provenance = overlay == shot.provenance_overlay
        is_scene_heading = overlay == shot.generic_overlay
        visible_duration = min(4.6, shot.duration) if is_scene_heading else shot.duration
        fade_out_start = max(0.0, visible_duration - 0.32)
        overlay_filter = (
            f"[{index}:v]scale={WIDTH}:{HEIGHT}:flags=lanczos,format=rgba,"
            f"fade=t=in:st=0:d=0.28:alpha=1,"
            f"fade=t=out:st={fade_out_start:.6f}:d=0.32:alpha=1[{overlay_label}]"
        )
        if is_provenance:
            overlay_filter = f"[{index}:v]format=rgba[{overlay_label}]"
        graph.append(overlay_filter)
        # The looping overlay is not allowed to terminate the main stream.
        # `shortest=1` drops the final main-frame on FFmpeg 9 for still-image
        # overlays, which would accumulate several seconds across this edit.
        graph.append(f"[{previous}][{overlay_label}]overlay=0:0:format=auto:eof_action=repeat[{out_label}]")
        previous = out_label

    final_filters: list[str] = []
    if shot.fade_scene:
        fade_duration = min(0.45, shot.duration / 4)
        final_filters.append(f"fade=t=in:st=0:d={fade_duration:.3f}")
        if shot.scene_id == "S100":
            final_filters.append(
                f"fade=t=out:st={max(0.0, shot.duration - fade_duration):.6f}:d={fade_duration:.3f}"
            )
    final_filters.extend([f"fps={FPS}", "setsar=1", "format=yuv420p"])
    graph.append(f"[{previous}]{','.join(final_filters)}[out]")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        *inputs,
        "-filter_complex",
        ";".join(graph),
        "-map",
        "[out]",
        "-an",
        "-frames:v",
        str(shot.frames),
        "-r",
        str(FPS),
        "-c:v",
        "h264_videotoolbox",
        "-profile:v",
        "high",
        "-level:v",
        "4.2",
        "-b:v",
        "16M",
        "-maxrate",
        "22M",
        "-bufsize",
        "32M",
        "-g",
        "60",
        "-pix_fmt",
        "yuv420p",
        "-color_range",
        "tv",
        "-colorspace",
        "bt709",
        "-color_trc",
        "bt709",
        "-color_primaries",
        "bt709",
        "-movflags",
        "+faststart",
        str(shot.output),
    ]
    run(command)
    return "rendered", shot.output


def concat_picture(shots: list[Shot], concat_path: Path, output: Path) -> None:
    lines = ["ffconcat version 1.0"]
    for shot in shots:
        lines.append(f"file {shlex.quote(str(shot.output.resolve()))}")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
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
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--overlay-dir", type=Path, required=True)
    parser.add_argument("--still-dir", type=Path, required=True)
    parser.add_argument("--segment-dir", type=Path, required=True)
    parser.add_argument("--concat", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    with args.storyboard.resolve().open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    shots = build_shots(
        rows,
        args.project_dir.resolve(),
        args.overlay_dir.resolve(),
        args.still_dir.resolve(),
        args.segment_dir.resolve(),
    )
    jobs = max(1, min(args.jobs, 4))
    rendered = 0
    cached = 0
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {pool.submit(render_shot, shot, args.force): shot for shot in shots}
        for future in as_completed(futures):
            status, path = future.result()
            rendered += status == "rendered"
            cached += status == "cached"
            print(f"[{rendered + cached:03d}/{len(shots):03d}] {status}: {path.name}", flush=True)

    ordered = sorted(shots, key=lambda item: (item.scene_number, item.shot_index))
    concat_picture(ordered, args.concat.resolve(), args.output.resolve())
    print(f"Picture master: {args.output.resolve()}")
    print(f"Shots rendered={rendered}, cached={cached}, total={len(shots)}")


if __name__ == "__main__":
    main()
