#!/opt/homebrew/bin/python3.13
"""Render the V11 content picture from the locked semantic visual plan.

The renderer is deliberately deterministic.  It never reverses or loops a
human action, keeps every source inside its approved window, applies one
light-touch Civic Daylight grade, and uses short cross-dissolves whose extra
tail frames are trimmed only after the dissolve graph is complete.  This
keeps the picture frame-locked to the Vale narration while avoiding the
hard-cut/black-flash problem in the earlier delivery.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shlex
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from v11_visual_plan import (
    ASSET_WINDOWS,
    BANNED_ASSETS,
    FORBIDDEN_PREFIXES,
    G,
    SCENE_ASSETS,
    SOURCE_SCENES,
    category,
    validate,
)


WIDTH = 1920
HEIGHT = 1080
FPS = 30
TRANSITION_SECONDS = 0.25
TRANSITION_FRAMES = round(TRANSITION_SECONDS * FPS)
STILL_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass
class Shot:
    ordinal: int
    scene_id: str
    shot_index: int
    frames: int
    render_frames: int
    relative_asset: str
    source_asset: str
    source_start: float
    source_end: float
    source_available: float
    reuse_index: int
    reuse_count: int
    category: str
    generic_overlay: str | None
    provenance_overlay: str | None

    @property
    def duration(self) -> float:
        return self.frames / FPS

    @property
    def render_duration(self) -> float:
        return self.render_frames / FPS


def run(command: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.PIPE if capture else subprocess.PIPE,
    )
    return result.stdout if capture else ""


def probe(path: Path) -> dict[str, float | int]:
    text = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate:format=duration",
            "-of", "json", str(path),
        ],
        text=True,
    )
    data = json.loads(text)
    if not data.get("streams"):
        raise ValueError(f"No video stream: {path}")
    stream = data["streams"][0]
    return {
        "width": int(stream.get("width", 0) or 0),
        "height": int(stream.get("height", 0) or 0),
        "duration": float(data.get("format", {}).get("duration", 0) or 0),
    }


def seconds(value: str) -> float:
    h, m, s = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def frame_count(value: str) -> int:
    return round(seconds(value) * FPS)


def title_overlay_path(overlay_dir: Path, scene_id: str) -> Path | None:
    path = overlay_dir / f"{scene_id}_overlay.png"
    return path if path.is_file() else None


def build_shots(
    rows: list[dict[str, str]],
    project_dir: Path,
    overlay_dir: Path,
    *,
    scene_limit: int | None = None,
) -> tuple[list[Shot], int]:
    content_rows = [row for row in rows if row["SCENE_ID"].startswith("S")]
    if scene_limit is not None:
        content_rows = content_rows[:scene_limit]
    scene_ids = [row["SCENE_ID"] for row in content_rows]
    if scene_limit is None:
        validate(scene_ids, project_dir)
    else:
        expected = {f"S{i:03d}" for i in range(1, scene_limit + 1)}
        if set(scene_ids) != expected:
            raise ValueError(f"Non-contiguous limited scene list: {scene_ids}")

    reuse_counts: Counter[str] = Counter(
        relative
        for row in content_rows
        for relative in SCENE_ASSETS[row["SCENE_ID"]]
    )
    occurrences: Counter[str] = Counter()
    source_cursors: dict[str, float] = {}
    shots: list[Shot] = []
    ordinal = 0
    total_content_frames = 0
    for row in content_rows:
        scene_id = row["SCENE_ID"]
        if not row.get("VISUAL_ARGUMENT_LINK", "").strip():
            raise ValueError(f"Missing V11 visual_argument_link: {scene_id}")
        start_frame = frame_count(row["START_TIME"])
        end_frame = frame_count(row["END_TIME"])
        scene_frames = end_frame - start_frame
        if scene_frames <= 0:
            raise ValueError(f"Non-positive scene duration: {scene_id}")
        total_content_frames += scene_frames
        assets = SCENE_ASSETS[scene_id]
        base, remainder = divmod(scene_frames, len(assets))
        generic = title_overlay_path(overlay_dir, scene_id)
        for index, relative in enumerate(assets):
            frames = base + (1 if index < remainder else 0)
            ordinal += 1
            is_last = scene_id == content_rows[-1]["SCENE_ID"] and index == len(assets) - 1
            render_frames = frames + (0 if is_last else TRANSITION_FRAMES)
            suffix = Path(relative).suffix.lower()
            source = project_dir / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            if relative in BANNED_ASSETS or relative.startswith(FORBIDDEN_PREFIXES):
                raise ValueError(f"Banned or credit asset in V11 plan: {relative}")

            info = probe(source)
            source_duration = float(info["duration"])
            occurrences[relative] += 1
            reuse_index = occurrences[relative]
            reuse_count = reuse_counts[relative]
            if suffix in STILL_SUFFIXES:
                source_start = 0.0
                source_end = render_frames / FPS
                source_available = float("inf")
            else:
                width = int(info["width"])
                height = int(info["height"])
                aspect = width / height if height else 0.0
                if width < WIDTH or height < HEIGHT or abs(aspect - WIDTH / HEIGHT) > 0.02:
                    raise ValueError(
                        f"V11 refuses non-native Full-HD 16:9 motion source: {scene_id} {relative}: "
                        f"{width}x{height}, aspect={aspect:.4f}"
                    )
                approved_start, approved_end = ASSET_WINDOWS.get(relative, (0.0, source_duration))
                approved_start = max(0.0, approved_start)
                approved_end = min(source_duration, approved_end)
                source_available = max(0.0, approved_end - approved_start)
                source_start = source_cursors.get(relative, approved_start)
                source_end = source_start + render_frames / FPS
                if source_end > approved_end + 0.025:
                    raise ValueError(
                        f"No disjoint motion window for {scene_id} {relative}: "
                        f"need [{source_start:.3f}, {source_end:.3f}), approved "
                        f"[{approved_start:.3f}, {approved_end:.3f})"
                    )
                source_cursors[relative] = source_end

            # Generic scene title is shown only once and is never placed over
            # a deterministic graphic or a source-card (those carry their own
            # carefully typeset heading).
            is_graphic = relative.startswith(G + "/")
            is_source_card = (
                (scene_id in SOURCE_SCENES and suffix in STILL_SUFFIXES)
                or category(relative) == "verified_real_photo"
            )
            generic_for_shot = str(generic) if generic and index == 0 and not is_graphic and not is_source_card else None
            provenance = overlay_dir / f"{scene_id}_{index + 1:02d}_provenance.png"
            provenance_for_shot = str(provenance) if provenance.is_file() and not is_graphic and not is_source_card else None
            shots.append(
                Shot(
                    ordinal=ordinal,
                    scene_id=scene_id,
                    shot_index=index + 1,
                    frames=frames,
                    render_frames=render_frames,
                    relative_asset=relative,
                    source_asset=str(source),
                    source_start=source_start,
                    source_end=source_end,
                    source_available=source_available,
                    reuse_index=reuse_index,
                    reuse_count=reuse_count,
                    category=category(relative),
                    generic_overlay=generic_for_shot,
                    provenance_overlay=provenance_for_shot,
                )
            )
    if sum(s.frames for s in shots) != total_content_frames:
        raise AssertionError("Shot frame allocation does not match storyboard")
    return shots, total_content_frames


def still_filter(shot: Shot, info: dict[str, float | int]) -> str:
    # Source cards are large enough to receive a very restrained Ken Burns
    # move.  The expression starts at native framing and never enlarges a
    # small image beyond its actual pixels.
    width, height = int(info["width"]), int(info["height"])
    if width < WIDTH or height < HEIGHT:
        scale = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#F4EFE5"
        return f"{scale},fps={FPS},setsar=1"
    return (
        f"scale={max(WIDTH, 2048)}:{max(HEIGHT, 1152)}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"zoompan=z='min(zoom+0.00016,1.012)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={WIDTH}x{HEIGHT}:fps={FPS},"
        "setsar=1"
    )


def base_video_filter(shot: Shot, info: dict[str, float | int]) -> str:
    suffix = Path(shot.source_asset).suffix.lower()
    if suffix in STILL_SUFFIXES:
        filters = [still_filter(shot, info)]
    else:
        duration = shot.render_duration
        source_duration = float(info["duration"])
        start = shot.source_start
        approved_end = min(shot.source_end, source_duration)
        available = max(0.01, approved_end - start)
        trim_duration = min(duration, available)
        filters = [f"trim=start={start:.6f}:duration={trim_duration:.6f}", "setpts=PTS-STARTPTS"]
        if trim_duration + 0.01 < duration:
            shortage = duration - trim_duration
            if shot.category != "deterministic_motion_graphic" or shortage > 1 / FPS + 0.01:
                raise ValueError(
                    f"V11 refuses to hold motion source {shot.scene_id} {shot.relative_asset}: "
                    f"need {duration:.3f}s, have {trim_duration:.3f}s"
                )
            filters.append(f"tpad=stop_mode=clone:stop_duration={shortage:.6f}")
        filters.append("fps=30")
        # The Flow/Veo exports in this project have a small provider sparkle
        # inside the lower-right title-safe area rather than on the final few
        # pixels.  The earlier 80×60 edge crop left part of that mark visible.
        # Use one 16:9 source crop, verified against every unique AI asset, so
        # the mark is removed without stretching the picture.  This modest
        # reframing is never applied to real footage, graphics or source cards.
        if shot.category == "veo_flow_illustration" and int(info["width"]) == 1920 and int(info["height"]) == 1080:
            filters.extend(["crop=1680:945:20:10", f"scale={WIDTH}:{HEIGHT}:flags=lanczos", "setsar=1"])
        else:
            filters.extend([f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={WIDTH}:{HEIGHT}", "setsar=1"])

    # A single restrained grade makes the varied real/Flow sources sit in the
    # same Civic Daylight world without turning skin into plastic or crushing
    # the bright editorial graphics.
    if shot.category == "real_footage":
        filters.append("eq=contrast=1.025:brightness=0.008:saturation=1.015:gamma=1.0")
    elif shot.category == "veo_flow_illustration":
        filters.append("eq=contrast=1.035:brightness=0.006:saturation=0.965:gamma=0.99")
    elif shot.category == "instructor_source_card":
        filters.append("eq=contrast=1.01:brightness=0.004:saturation=0.99:gamma=1.0")
    filters.append("format=yuv420p")
    return ",".join(filters)


def overlay_graph(shot: Shot, base: str, overlay_inputs: list[Path]) -> tuple[str, list[str]]:
    graph: list[str] = [f"[0:v]{base}[base0]"]
    current = "base0"
    for idx, overlay in enumerate(overlay_inputs, start=1):
        label = f"ov{idx}"
        out = f"base{idx}"
        is_provenance = str(overlay) == shot.provenance_overlay
        title_window = 5.6 if shot.scene_id == "S005" else 4.6
        visible = min(title_window, shot.render_duration) if not is_provenance else shot.render_duration
        fade_start = max(0.0, visible - 0.30)
        if is_provenance:
            graph.append(f"[{idx}:v]format=rgba[{label}]")
        else:
            graph.append(
                f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.22:alpha=1,"
                f"fade=t=out:st={fade_start:.6f}:d=0.30:alpha=1[{label}]"
            )
        graph.append(f"[{current}][{label}]overlay=0:0:format=auto:eof_action=repeat[{out}]")
        current = out
    graph.append(f"[{current}]fps=30,setsar=1,format=yuv420p[out]")
    return ";".join(graph), [str(x) for x in overlay_inputs]


def render_shot(shot: Shot, output: Path, *, force: bool, bitrate: str) -> None:
    if output.is_file() and not force:
        return
    source = Path(shot.source_asset)
    info = probe(source)
    suffix = source.suffix.lower()
    inputs: list[str] = []
    if suffix in STILL_SUFFIXES:
        inputs += ["-loop", "1", "-framerate", str(FPS), "-i", str(source)]
    else:
        inputs += ["-i", str(source)]
    overlays: list[Path] = []
    if shot.generic_overlay:
        overlays.append(Path(shot.generic_overlay))
    if shot.provenance_overlay:
        overlays.append(Path(shot.provenance_overlay))
    for overlay in overlays:
        inputs += ["-loop", "1", "-framerate", str(FPS), "-i", str(overlay)]
    graph, _ = overlay_graph(shot, base_video_filter(shot, info), overlays)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        *inputs, "-filter_complex", graph, "-map", "[out]", "-an",
        "-frames:v", str(shot.render_frames), "-r", str(FPS),
        "-c:v", "h264_videotoolbox", "-profile:v", "high", "-level:v", "4.2",
        "-b:v", bitrate, "-maxrate", str(int(float(bitrate.rstrip("M")) * 1.3)) + "M",
        "-bufsize", str(int(float(bitrate.rstrip("M")) * 2.0)) + "M", "-g", "60",
        "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709",
        "-color_trc", "bt709", "-color_primaries", "bt709", "-movflags", "+faststart",
        str(output),
    ]
    run(command)


def xfade_segments(
    segment_paths: list[Path],
    assigned_frames: list[int],
    output: Path,
    *,
    force: bool,
    bitrate: str,
    keep_tail: bool = False,
) -> None:
    if output.is_file() and not force:
        return
    if not segment_paths:
        raise ValueError("No segments to xfade")
    output.parent.mkdir(parents=True, exist_ok=True)
    if len(segment_paths) == 1:
        output_frames = assigned_frames[0] + (TRANSITION_FRAMES if keep_tail else 0)
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(segment_paths[0]),
            "-c:v", "h264_videotoolbox", "-profile:v", "high",
            "-level:v", "4.2", "-b:v", bitrate, "-maxrate", "22M", "-bufsize", "32M",
            "-frames:v", str(output_frames), "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_trc", "bt709",
            "-color_primaries", "bt709", "-movflags", "+faststart", str(output),
        ])
        return
    command: list[str] = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    command.extend(item for path in segment_paths for item in ("-i", str(path)))
    graph: list[str] = []
    for idx in range(len(segment_paths)):
        graph.append(f"[{idx}:v]setpts=PTS-STARTPTS,settb=AVTB,format=yuv420p[v{idx}]")
    current = "v0"
    cumulative = assigned_frames[0] / FPS
    for idx in range(1, len(segment_paths)):
        out_label = f"xf{idx}"
        offset = cumulative
        graph.append(
            f"[{current}][v{idx}]xfade=transition=fade:duration={TRANSITION_SECONDS:.6f}:offset={offset:.6f},"
            f"settb=AVTB[{out_label}]"
        )
        current = out_label
        cumulative += assigned_frames[idx] / FPS
    total_frames = sum(assigned_frames)
    total_duration = total_frames / FPS
    output_frames = total_frames + (TRANSITION_FRAMES if keep_tail else 0)
    output_duration = output_frames / FPS
    graph.append(f"[{current}]trim=duration={output_duration:.6f},setpts=PTS-STARTPTS,fps=30,setsar=1,format=yuv420p[out]")
    command += [
        "-filter_complex", ";".join(graph), "-map", "[out]", "-frames:v", str(output_frames),
        "-an", "-c:v", "h264_videotoolbox", "-profile:v", "high", "-level:v", "4.2",
        "-b:v", bitrate, "-maxrate", "22M", "-bufsize", "32M", "-g", "60", "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-colorspace", "bt709", "-color_trc", "bt709", "-color_primaries", "bt709",
        "-movflags", "+faststart", str(output),
    ]
    run(command)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render(
    rows: list[dict[str, str]],
    project_dir: Path,
    overlay_dir: Path,
    segment_dir: Path,
    scene_dir: Path,
    output: Path,
    manifest_path: Path,
    *,
    force: bool,
    jobs: int,
    scene_limit: int | None,
    bitrate: str,
) -> None:
    shots, total_frames = build_shots(rows, project_dir, overlay_dir, scene_limit=scene_limit)
    segment_dir.mkdir(parents=True, exist_ok=True)
    # Shot rendering is embarrassingly parallel, but keep the default small
    # enough not to starve the machine while the user is working.
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def one(shot: Shot) -> tuple[Shot, Path, str]:
        path = segment_dir / f"{shot.ordinal:04d}_{shot.scene_id}_{shot.shot_index:02d}.mp4"
        render_shot(shot, path, force=force, bitrate=bitrate)
        return shot, path, "rendered" if force or not path.exists() else "cached"

    # We need a reliable status, so detect existence before each call.
    def one_status(shot: Shot) -> tuple[Shot, Path, str]:
        path = segment_dir / f"{shot.ordinal:04d}_{shot.scene_id}_{shot.shot_index:02d}.mp4"
        existed = path.is_file() and not force
        render_shot(shot, path, force=force, bitrate=bitrate)
        return shot, path, "cached" if existed else "rendered"

    with ThreadPoolExecutor(max_workers=max(1, min(jobs, 4))) as pool:
        futures = [pool.submit(one_status, shot) for shot in shots]
        for done, future in enumerate(as_completed(futures), start=1):
            shot, path, status = future.result()
            print(f"[{done:03d}/{len(shots):03d}] {status} {shot.scene_id}_{shot.shot_index:02d} {path.name}", flush=True)

    # Build scene-level crossfades first.  This keeps the final filter graph
    # compact and makes it easy to inspect each chapter independently.
    scenes: list[Path] = []
    shot_cursor = 0
    scene_rows = [row for row in rows if row["SCENE_ID"].startswith("S")]
    if scene_limit is not None:
        scene_rows = scene_rows[:scene_limit]
    for row in scene_rows:
        sid = row["SCENE_ID"]
        count = len(SCENE_ASSETS[sid])
        group = shots[shot_cursor:shot_cursor + count]
        paths = [segment_dir / f"{s.ordinal:04d}_{s.scene_id}_{s.shot_index:02d}.mp4" for s in group]
        scene_out = scene_dir / f"{sid}.mp4"
        xfade_segments(
            paths,
            [s.frames for s in group],
            scene_out,
            force=force,
            bitrate=bitrate,
            keep_tail=(row is not scene_rows[-1]),
        )
        scenes.append(scene_out)
        shot_cursor += count
    if shot_cursor != len(shots):
        raise AssertionError("Scene grouping did not consume all shots")

    # Crossfade all scene outputs.  Scene outputs have a transition tail by
    # construction except the last content scene; assigned durations remain
    # exactly the storyboard durations and the final trim preserves them.
    xfade_segments(
        scenes,
        [round(float(r["DURATION"]) * FPS) for r in scene_rows],
        output,
        force=force,
        bitrate=bitrate,
        keep_tail=False,
    )
    records = []
    counts: Counter[str] = Counter()
    for shot in shots:
        counts[shot.relative_asset] += 1
        records.append({
            **asdict(shot),
            "duration_seconds": shot.duration,
            "render_duration_seconds": shot.render_duration,
            "segment": str((segment_dir / f"{shot.ordinal:04d}_{shot.scene_id}_{shot.shot_index:02d}.mp4").relative_to(project_dir)),
        })
    manifest = {
        "schema_version": "v11-picture-2-disjoint-windows",
        "visual_identity": "Civic Daylight / Red Thread · semantic-first V11",
        "width": WIDTH,
        "height": HEIGHT,
        "fps": FPS,
        "transition_seconds": TRANSITION_SECONDS,
        "scene_count": len(scene_rows),
        "shot_count": len(shots),
        "content_frames": total_frames,
        "content_duration_seconds": total_frames / FPS,
        "asset_count": len(counts),
        "max_asset_reuse": max(counts.values(), default=0),
        "asset_reuse": dict(sorted(counts.items())),
        "category_placement_counts": dict(Counter(s.category for s in shots)),
        "shots": records,
        "output": str(output),
        "output_sha256": sha256(output),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("scene_count", "shot_count", "content_duration_seconds", "asset_count", "max_asset_reuse", "category_placement_counts", "output_sha256")}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--overlay-dir", type=Path, required=True)
    parser.add_argument("--segment-dir", type=Path, required=True)
    parser.add_argument("--scene-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--scene-limit", type=int)
    parser.add_argument("--bitrate", default="8M")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    with args.storyboard.resolve().open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    render(
        rows,
        args.project_dir.resolve(),
        args.overlay_dir.resolve(),
        args.segment_dir.resolve(),
        args.scene_dir.resolve(),
        args.output.resolve(),
        args.manifest.resolve(),
        force=args.force,
        jobs=args.jobs,
        scene_limit=args.scene_limit,
        bitrate=args.bitrate,
    )


if __name__ == "__main__":
    main()
