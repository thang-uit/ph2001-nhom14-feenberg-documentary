#!/usr/bin/env python3
"""Build a clean UHD upload master for the standalone TP.HCM credit montage.

The clean master contains no typography or credit overlays.  It is rendered
from the original local city footage at 3840x2160 wherever source resolution
supports it; 1920x1080 sources are upscaled transparently because the montage
deliberately combines footage from different capture resolutions.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from build_credit_tphcm import (
    AUDIO,
    AUDIO_DURATION,
    AUDIO_START,
    FPS,
    PEXELS_URLS,
    RAW,
    ROOT,
    SHOTS,
    TRANSITION,
    WORK,
    mux_audio,
)


UHD_WIDTH = 3840
UHD_HEIGHT = 2160
SEGMENTS_UHD = WORK / "segments_clean_4k"
PICTURE_UHD = WORK / "picture_clean_4k.mp4"
OUTPUT_UHD = WORK.parent.parent / "CREDIT_TPHCM_OH_YEAH_CLEAN_4K.mp4"
QA_DIR = ROOT / "qa" / "credit_tphcm"


def run(cmd: list[str]) -> None:
    print("$", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def grade_filter_uhd() -> str:
    # Match the approved V3 grade while preserving the extra source detail.
    return (
        f"scale={UHD_WIDTH}:{UHD_HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={UHD_WIDTH}:{UHD_HEIGHT},setsar=1,fps={FPS},"
        "eq=contrast=0.96:brightness=-0.018:saturation=0.82:gamma=1.02,"
        "colorbalance=rs=-0.015:gs=0.018:bs=0.035:"
        "rm=0.025:gm=0.012:bm=-0.035:"
        "rh=0.055:gh=0.028:bh=-0.075:pl=1,"
        "curves=all='0/0.025 0.18/0.15 0.50/0.52 0.82/0.87 1/0.965',"
        "unsharp=5:5:0.22:3:3:0.08,vignette=PI/10,"
        "noise=alls=0.20:allf=t+u,format=yuv420p"
    )


def render_segment(index: int, shot: dict[str, object], force: bool) -> Path:
    SEGMENTS_UHD.mkdir(parents=True, exist_ok=True)
    output = SEGMENTS_UHD / f"{shot['id']}.mp4"
    if output.exists() and not force:
        return output

    source = RAW / str(shot["file"])
    duration = float(shot["duration"])
    source_start = float(shot["source_start"])
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{source_start:.3f}", "-i", str(source),
        "-t", f"{duration:.3f}", "-vf", grade_filter_uhd(),
        "-r", str(FPS), "-an", "-c:v", "libx264", "-profile:v", "high",
        "-level", "5.2", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "slow",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        str(output),
    ]
    run(command)
    return output


def assemble_video(segments: list[Path], force: bool) -> None:
    if PICTURE_UHD.exists() and not force:
        return
    inputs: list[str] = []
    for path in segments:
        inputs.extend(["-i", str(path)])

    filters: list[str] = []
    previous = "[0:v]"
    cumulative = float(SHOTS[0]["duration"])
    for index in range(1, len(segments)):
        output = f"[v{index}]"
        offset = cumulative - TRANSITION
        filters.append(
            f"{previous}[{index}:v]xfade=transition=fade:duration={TRANSITION:.3f}:"
            f"offset={offset:.3f}{output}"
        )
        previous = output
        cumulative += float(SHOTS[index]["duration"]) - TRANSITION
    filters.append(f"{previous}format=yuv420p[vout]")

    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs,
        "-filter_complex", ";".join(filters), "-map", "[vout]",
        "-r", str(FPS), "-an", "-c:v", "libx264", "-profile:v", "high",
        "-level", "5.2", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "slow",
        "-maxrate", "60M", "-bufsize", "120M",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-movflags", "+faststart", str(PICTURE_UHD),
    ]
    run(command)


def write_manifest() -> None:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "deliverable": OUTPUT_UHD.name,
        "text_layers": False,
        "resolution": f"{UHD_WIDTH}x{UHD_HEIGHT}",
        "frame_rate": FPS,
        "audio_source": str(AUDIO),
        "audio_segment": f"{AUDIO_START:.3f}–{AUDIO_START + AUDIO_DURATION:.3f} s",
        "visual_rule": "real TP.HCM footage only; no typography or synthetic city imagery",
        "source_resolution_note": "Mixed source resolutions: 4K footage retained at UHD; 1920x1080 sources are high-quality Lanczos upscales.",
        "transition": f"dissolve {TRANSITION:.2f}s",
        "shots": [
            {
                "scene_id": shot["id"],
                "source": shot["file"],
                "source_url": PEXELS_URLS.get(str(shot["file"])),
                "source_start": shot["source_start"],
                "duration": shot["duration"],
                "overlay": None,
            }
            for shot in SHOTS
        ],
    }
    (QA_DIR / "credit_clean_4k_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not AUDIO.is_file():
        raise FileNotFoundError(AUDIO)
    for shot in SHOTS:
        source = RAW / str(shot["file"])
        if not source.is_file():
            raise FileNotFoundError(source)

    if args.force:
        for path in SEGMENTS_UHD.glob("C*.mp4"):
            path.unlink()
        for path in (PICTURE_UHD, OUTPUT_UHD):
            if path.exists():
                path.unlink()

    segments = [render_segment(index, shot, args.force) for index, shot in enumerate(SHOTS)]
    assemble_video(segments, args.force)
    mux_audio(PICTURE_UHD, OUTPUT_UHD, args.force)
    write_manifest()
    print(f"Wrote {OUTPUT_UHD}")


if __name__ == "__main__":
    main()
