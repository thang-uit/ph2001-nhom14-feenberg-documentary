#!/usr/bin/env python3
"""Technical, timeline, subtitle and delivery QA for the final documentary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import unicodedata
from pathlib import Path


EXPECTED_DURATION = 972.566667
EXPECTED_CUES = 267
FPS = 30.0
MAX_SUBTITLE_CPS = 28.0


def run(command: list[str], *, capture_stderr: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE if capture_stderr else subprocess.STDOUT,
    )
    return result.stderr if capture_stderr else result.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def seconds(value: str) -> float:
    hours, minutes, rest = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value)).strip()


def parse_srt(path: Path) -> list[dict[str, object]]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    cues: list[dict[str, object]] = []
    for expected, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != str(expected) or "-->" not in lines[1]:
            raise ValueError(f"Invalid SRT block {expected}")
        start_text, end_text = (item.strip() for item in lines[1].split("-->", 1))
        cues.append({"start": seconds(start_text), "end": seconds(end_text), "lines": lines[2:]})
    return cues


def rate(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator)


def inspect_faststart(path: Path) -> tuple[bool, str]:
    with path.open("rb") as handle:
        prefix = handle.read(min(path.stat().st_size, 64 * 1024 * 1024))
    moov = prefix.find(b"moov")
    mdat = prefix.find(b"mdat")
    ok = moov >= 0 and mdat >= 0 and moov < mdat
    return ok, f"moov_offset={moov}, mdat_offset={mdat}"


def loudness(path: Path) -> tuple[float, float, str]:
    text = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
            "-filter_complex", "ebur128=peak=true", "-f", "null", "-",
        ],
        capture_stderr=True,
    )
    integrated = [float(item) for item in re.findall(r"^\s*I:\s*(-?\d+(?:\.\d+)?)\s+LUFS", text, re.M)]
    peaks = [float(item) for item in re.findall(r"^\s*Peak:\s*(-?\d+(?:\.\d+)?)\s+dBFS", text, re.M)]
    if not integrated or not peaks:
        raise ValueError("Could not parse EBU R128 summary")
    return integrated[-1], peaks[-1], text


def check_storyboard(path: Path, expected_duration: float, failures: list[str], facts: list[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 100:
        failures.append(f"Storyboard has {len(rows)} scenes, expected 100")
        return
    cursor = 0.0
    for expected, row in enumerate(rows, start=1):
        if row["SCENE_ID"] != f"S{expected:03d}":
            failures.append(f"Storyboard scene order mismatch at row {expected}")
        start = seconds(row["START_TIME"])
        end = seconds(row["END_TIME"])
        duration = float(row["DURATION"])
        if not math.isclose(start, cursor, abs_tol=0.001):
            failures.append(f"Storyboard gap/overlap before {row['SCENE_ID']}")
        if not math.isclose(end - start, duration, abs_tol=0.001):
            failures.append(f"Storyboard duration mismatch at {row['SCENE_ID']}")
        cursor = end
    if not math.isclose(cursor, expected_duration, abs_tol=0.001):
        failures.append(f"Storyboard ends at {cursor:.3f}s, expected {expected_duration:.3f}s")
    facts.append(f"Storyboard: {len(rows)} continuous scenes, end={cursor:.3f}s")


def check_subtitles(path: Path, transcript: Path, expected_cues: int, failures: list[str], facts: list[str]) -> None:
    cues = parse_srt(path)
    if len(cues) != expected_cues:
        failures.append(f"Subtitle cue count {len(cues)}, expected {expected_cues}")
    previous_end = -1.0
    reading_rates: list[float] = []
    for index, cue in enumerate(cues, start=1):
        start = float(cue["start"])
        end = float(cue["end"])
        lines = list(cue["lines"])
        if start <= previous_end:
            failures.append(f"Subtitle overlap/missing gap before cue {index}")
        if end <= start:
            failures.append(f"Non-positive subtitle cue {index}")
        if len(lines) > 2 or any(len(line) > 42 for line in lines):
            failures.append(f"Subtitle layout limit exceeded at cue {index}")
        text = " ".join(lines)
        if end > start:
            reading_rate = len(text) / (end - start)
            reading_rates.append(reading_rate)
            if reading_rate > MAX_SUBTITLE_CPS:
                failures.append(
                    f"Subtitle cue {index} exceeds {MAX_SUBTITLE_CPS:.0f} "
                    f"characters/second: {reading_rate:.2f}"
                )
            if end - start < 1.0:
                failures.append(f"Subtitle cue {index} is shorter than one second")
        if unicodedata.normalize("NFC", text) != text:
            failures.append(f"Subtitle cue {index} is not Unicode NFC")
        previous_end = end
    subtitle_text = normalized(" ".join(" ".join(cue["lines"]) for cue in cues))
    transcript_text = normalized(transcript.read_text(encoding="utf-8-sig"))
    if subtitle_text != transcript_text:
        failures.append("Subtitle transcript differs from locked spoken transcript")
    facts.append(
        f"Subtitles: cues={len(cues)}, final_cue={float(cues[-1]['end']):.3f}s, "
        f"exact_transcript={'PASS' if subtitle_text == transcript_text else 'FAIL'}"
    )
    facts.append(f"Subtitle reading rate: maximum={max(reading_rates, default=0):.2f} characters/second; minimum duration >=1s checked")


def make_contact_sheet(video: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
            "-vf", "fps=1/48,scale=480:270:flags=lanczos,tile=4x7:padding=4:margin=4:color=#0B0F14",
            "-frames:v", "1", "-q:v", "2", str(output),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--contact-sheet", type=Path, required=True)
    parser.add_argument("--expected-duration", type=float, default=EXPECTED_DURATION)
    parser.add_argument("--expected-cues", type=int, default=EXPECTED_CUES)
    args = parser.parse_args()

    video = args.video.resolve()
    failures: list[str] = []
    warnings: list[str] = []
    facts: list[str] = []

    probe_text = run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=format_name,duration,size,bit_rate:stream=index,codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,sample_aspect_ratio,field_order,color_range,color_space,color_transfer,color_primaries,sample_rate,channels,bit_rate",
            "-of", "json", str(video),
        ]
    )
    probe = json.loads(probe_text)
    args.probe.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.probe.resolve().write_text(json.dumps(probe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    streams = probe.get("streams", [])
    videos = [item for item in streams if item.get("codec_type") == "video"]
    audios = [item for item in streams if item.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        failures.append(f"Expected one video and one audio stream; got video={len(videos)}, audio={len(audios)}")
    if not videos or not audios:
        raise SystemExit("Missing required streams")
    v = videos[0]
    a = audios[0]
    container = probe.get("format", {})
    duration = float(container.get("duration", 0))
    video_rate = int(v.get("bit_rate", 0) or 0)

    expected_video = {
        "codec_name": "h264", "profile": "High", "width": 1920, "height": 1080,
        "pix_fmt": "yuv420p", "sample_aspect_ratio": "1:1", "field_order": "progressive",
        "color_range": "tv", "color_space": "bt709", "color_transfer": "bt709", "color_primaries": "bt709",
    }
    for key, expected in expected_video.items():
        if v.get(key) != expected:
            failures.append(f"Video {key}={v.get(key)!r}, expected {expected!r}")
    if not math.isclose(rate(str(v.get("avg_frame_rate", "0/1"))), FPS, abs_tol=0.001):
        failures.append(f"Average frame rate is {v.get('avg_frame_rate')}, expected 30/1")
    if a.get("codec_name") != "aac" or a.get("profile") != "LC":
        failures.append(f"Audio codec/profile is {a.get('codec_name')}/{a.get('profile')}, expected AAC/LC")
    if a.get("sample_rate") != "48000" or int(a.get("channels", 0)) != 2:
        failures.append(f"Audio is {a.get('sample_rate')} Hz/{a.get('channels')} channels, expected 48000/2")
    if not math.isclose(duration, args.expected_duration, abs_tol=0.050):
        failures.append(f"Container duration {duration:.3f}s, expected {args.expected_duration:.3f}s")
    if not 900 <= duration <= 1_200:
        failures.append("Duration is outside assignment limit 15:00–20:00")
    if video_rate and video_rate < 8_000_000:
        warnings.append(f"Video bitrate {video_rate / 1_000_000:.2f} Mbps is below the preferred 8 Mbps floor")

    faststart_ok, faststart_detail = inspect_faststart(video)
    if not faststart_ok:
        failures.append("MP4 faststart check failed: " + faststart_detail)
    facts.append(
        f"Video: {v.get('codec_name')} {v.get('profile')}, {v.get('width')}x{v.get('height')}, "
        f"{v.get('avg_frame_rate')}, {v.get('pix_fmt')}, {v.get('color_space')}/{v.get('color_transfer')}/{v.get('color_primaries')}"
    )
    facts.append(
        f"Audio: {a.get('codec_name')} {a.get('profile')}, {a.get('sample_rate')} Hz, channels={a.get('channels')}"
    )
    facts.append(f"Container: duration={duration:.3f}s, size={video.stat().st_size}, {faststart_detail}")

    check_storyboard(args.storyboard.resolve(), args.expected_duration, failures, facts)
    check_subtitles(args.srt.resolve(), args.transcript.resolve(), args.expected_cues, failures, facts)

    decode = subprocess.run(
        ["ffmpeg", "-hide_banner", "-v", "error", "-i", str(video), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if decode.returncode != 0 or decode.stderr.strip():
        failures.append("Full decode scan reported an error: " + decode.stderr.strip()[-1000:])
    else:
        facts.append("Full audio/video decode scan: PASS")

    integrated, true_peak, _ = loudness(video)
    if not -16.8 <= integrated <= -15.0:
        failures.append(f"Integrated loudness {integrated:.1f} LUFS outside -16.8…-15.0 LUFS")
    if true_peak > -1.0:
        failures.append(f"True peak {true_peak:.1f} dBFS exceeds -1.0 dBFS")
    facts.append(f"Audio loudness: {integrated:.1f} LUFS integrated, {true_peak:.1f} dBFS true peak")

    black_text = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(video),
            "-vf", "blackdetect=d=1.2:pix_th=0.05,freezedetect=n=-55dB:d=12", "-an", "-f", "null", "-",
        ],
        capture_stderr=True,
    )
    black_runs = re.findall(r"black_start:[^\n]+", black_text)
    if black_runs:
        warnings.extend("Black-frame run for manual review: " + item for item in black_runs)
    facts.append(f"Unexpected black-run scan: {len(black_runs)} run(s) >= 1.2s")
    args.report.with_suffix(".scan.log").write_text(black_text, encoding="utf-8")
    freeze_runs = re.findall(r"freeze_duration:\s*([0-9.]+)", black_text)
    starts = [float(item) for item in re.findall(r"freeze_start:\s*([0-9.]+)", black_text)]
    # S098 is an intentional 18-second full-screen end-credit card for seven
    # members. Derive its accepted interval from the storyboard so the gate
    # remains correct after a voice retime.
    with args.storyboard.resolve().open(encoding="utf-8-sig", newline="") as handle:
        credit_rows = {row["SCENE_ID"]: row for row in csv.DictReader(handle)}
    member_start = seconds(credit_rows["S098"]["START_TIME"])
    member_end = seconds(credit_rows["S098"]["END_TIME"])
    intentional_credit = []
    long_freezes = []
    for index, raw in enumerate(freeze_runs):
        span = float(raw)
        start = starts[index] if index < len(starts) else -1.0
        if span <= 18.0:
            continue
        if abs(start - member_start) <= 0.25 and abs(start + span - member_end) <= 0.35:
            intentional_credit.append(f"S098 member credits: {start:.3f}–{start + span:.3f}s")
        else:
            long_freezes.append(span)
    if long_freezes:
        failures.append("Freeze scan found interval(s) longer than 18s: " + ", ".join(f"{item:.2f}s" for item in long_freezes))
    facts.append(f"Freeze scan: {len(freeze_runs)} run(s) >= 12s; longest={max(map(float, freeze_runs), default=0):.2f}s")
    facts.extend("Reviewed intentional hold: " + item for item in intentional_credit)

    make_contact_sheet(video, args.contact_sheet.resolve())
    file_hash = sha256(video)
    status = "PASS" if not failures else "FAIL"
    report_lines = [
        "FINAL VIDEO QA REPORT",
        "",
        f"TECHNICAL / TIMING / SUBTITLE / YOUTUBE QA: {status}",
        f"File: {video}",
        f"SHA-256: {file_hash}",
        "",
        "FACTS",
        *[f"- {item}" for item in facts],
        "",
        "FAILURES",
        *( ["- None"] if not failures else [f"- {item}" for item in failures] ),
        "",
        "WARNINGS / MANUAL REVIEW",
        *( ["- None"] if not warnings else [f"- {item}" for item in warnings] ),
        "",
        "This automated gate does not replace the academic source audit or visual inspection of the contact sheet.",
    ]
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.resolve().write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print("\n".join(report_lines))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
