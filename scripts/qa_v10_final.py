#!/opt/homebrew/bin/python3.13
"""Gate the V10 Feenberg delivery before it replaces the V8 fallback."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import unicodedata
from collections import defaultdict
from pathlib import Path


FPS = 30.0
CONTENT_DURATION = 965.066667
CREDIT_DURATION = 54.1
CROSSFADE = 0.8
FINAL_DURATION = CONTENT_DURATION + CREDIT_DURATION - CROSSFADE
EXPECTED_FRAMES = round(FINAL_DURATION * FPS)
EXPECTED_CUES = 267
MAX_LINE_CHARS = 42
BANNED_ASSETS = {
    "assets/editorial_selects/S014_affected_users_1080p.mp4",
    "assets/flow_selected/S031_flow_1080p.mp4",
    "assets/flow_v8_odoo/S031_meta_choice_ramp_1080p.mp4",
}


def run(command: list[str], *, stderr: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE if stderr else subprocess.STDOUT,
    )
    return result.stderr if stderr else result.stdout


def seconds(value: str) -> float:
    hours, minutes, rest = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def rate(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value)).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_srt(path: Path) -> list[dict[str, object]]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    cues: list[dict[str, object]] = []
    for expected, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != str(expected) or "-->" not in lines[1]:
            raise ValueError(f"SRT block {expected} is malformed")
        start, end = (part.strip() for part in lines[1].split("-->", 1))
        cues.append({"start": seconds(start), "end": seconds(end), "lines": lines[2:]})
    return cues


def faststart(path: Path) -> tuple[bool, str]:
    with path.open("rb") as handle:
        prefix = handle.read(min(path.stat().st_size, 64 * 1024 * 1024))
    moov = prefix.find(b"moov")
    mdat = prefix.find(b"mdat")
    return moov >= 0 and mdat >= 0 and moov < mdat, f"moov={moov}, mdat={mdat}"


def make_contact_sheet(video: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
            "-vf", "fps=1/40,scale=480:270:flags=lanczos,tile=5x6:padding=4:margin=4:color=#101214",
            "-frames:v", "1", "-q:v", "2", str(output),
        ]
    )


def audio_metrics(video: Path, report: Path) -> tuple[float, float]:
    text = run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        stderr=True,
    )
    report.write_text(text, encoding="utf-8")
    integrated = [float(x) for x in re.findall(r"^\s*I:\s*(-?\d+(?:\.\d+)?)\s+LUFS", text, re.M)]
    peaks = [float(x) for x in re.findall(r"^\s*Peak:\s*(-?\d+(?:\.\d+)?)\s+dBFS", text, re.M)]
    if not integrated or not peaks:
        raise ValueError("Cannot parse EBU R128 summary")
    return integrated[-1], peaks[-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--picture-manifest", type=Path, required=True)
    parser.add_argument("--credit-reuse", type=Path, required=True)
    parser.add_argument("--voice", type=Path, required=True)
    parser.add_argument("--programme-audio", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--contact-sheet", type=Path, required=True)
    args = parser.parse_args()

    paths = {name: value.resolve() for name, value in vars(args).items() if isinstance(value, Path)}
    for key in ("video", "storyboard", "srt", "transcript", "picture_manifest", "credit_reuse", "voice", "programme_audio"):
        if not paths[key].is_file():
            raise SystemExit(f"Missing QA input {key}: {paths[key]}")
    paths["report"].parent.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    warnings: list[str] = []
    facts: list[str] = []
    probe = json.loads(
        run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=format_name,duration,size,bit_rate:stream=index,codec_type,codec_name,profile,level,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames,sample_aspect_ratio,field_order,color_range,color_space,color_transfer,color_primaries,sample_rate,channels,bit_rate",
                "-of", "json", str(paths["video"]),
            ]
        )
    )
    paths["probe"].parent.mkdir(parents=True, exist_ok=True)
    paths["probe"].write_text(json.dumps(probe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    videos = [x for x in probe.get("streams", []) if x.get("codec_type") == "video"]
    audios = [x for x in probe.get("streams", []) if x.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        failures.append(f"stream count video={len(videos)}, audio={len(audios)}; expected 1/1")
    if not videos or not audios:
        raise SystemExit("Final candidate lacks required streams")
    video_stream, audio_stream = videos[0], audios[0]
    expected_video = {
        "codec_name": "h264", "profile": "High", "width": 1920, "height": 1080,
        "pix_fmt": "yuv420p", "sample_aspect_ratio": "1:1", "field_order": "progressive",
        "color_range": "tv", "color_space": "bt709", "color_transfer": "bt709", "color_primaries": "bt709",
    }
    for key, expected in expected_video.items():
        if video_stream.get(key) != expected:
            failures.append(f"video {key}={video_stream.get(key)!r}, expected {expected!r}")
    if not math.isclose(rate(str(video_stream.get("avg_frame_rate", "0/1"))), FPS, abs_tol=0.001):
        failures.append(f"frame rate {video_stream.get('avg_frame_rate')} is not 30 fps")
    if int(video_stream.get("nb_frames", 0) or 0) != EXPECTED_FRAMES:
        failures.append(f"frame count {video_stream.get('nb_frames')} != {EXPECTED_FRAMES}")
    if audio_stream.get("codec_name") != "aac" or audio_stream.get("profile") != "LC":
        failures.append("audio is not AAC-LC")
    if audio_stream.get("sample_rate") != "48000" or int(audio_stream.get("channels", 0)) != 2:
        failures.append("audio is not stereo 48 kHz")
    duration = float(probe.get("format", {}).get("duration", 0) or 0)
    if not math.isclose(duration, FINAL_DURATION, abs_tol=0.04):
        failures.append(f"duration {duration:.3f}s != {FINAL_DURATION:.3f}s")
    if not 900 <= duration <= 1200:
        failures.append("duration is outside the required 15–20 minutes")
    bitrate = int(video_stream.get("bit_rate", 0) or 0)
    if bitrate < 8_000_000:
        failures.append(f"video bitrate {bitrate / 1_000_000:.2f} Mbps is below 8 Mbps")
    fast_ok, fast_detail = faststart(paths["video"])
    if not fast_ok:
        failures.append("MP4 is not faststart: " + fast_detail)
    facts.append(f"Video: H.264 High, 1920×1080, 30 fps, Rec.709, {bitrate/1_000_000:.2f} Mbps, {EXPECTED_FRAMES} frames")
    facts.append(f"Audio: AAC-LC stereo 48 kHz; duration {duration:.3f}s; faststart {fast_detail}")

    with paths["storyboard"].open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 96 or [r["SCENE_ID"] for r in rows[:95]] != [f"S{i:03d}" for i in range(1, 96)] or rows[-1]["SCENE_ID"] != "CREDIT_V4":
        failures.append("storyboard must contain S001–S095 followed by CREDIT_V4")
    cursor = 0.0
    for row in rows[:95]:
        start, end, duration_value = seconds(row["START_TIME"]), seconds(row["END_TIME"]), float(row["DURATION"])
        if not math.isclose(start, cursor, abs_tol=0.002) or not math.isclose(end - start, duration_value, abs_tol=0.002):
            failures.append(f"storyboard timing mismatch at {row['SCENE_ID']}")
        cursor = end
    if not math.isclose(cursor, CONTENT_DURATION, abs_tol=0.002):
        failures.append(f"content storyboard ends at {cursor:.3f}s")
    if not math.isclose(float(rows[-1]["DURATION"]), CREDIT_DURATION, abs_tol=0.001):
        failures.append("credit duration in storyboard is not 54.1s")
    facts.append(f"Timeline: 95 content scenes to {cursor:.3f}s + 54.1s credit − 0.8s crossfade = {FINAL_DURATION:.3f}s")

    cues = parse_srt(paths["srt"])
    if len(cues) != EXPECTED_CUES:
        failures.append(f"subtitle cue count {len(cues)} != {EXPECTED_CUES}")
    previous_end = -1.0
    for index, cue in enumerate(cues, 1):
        start, end, lines = float(cue["start"]), float(cue["end"]), list(cue["lines"])
        if start <= previous_end or end <= start:
            failures.append(f"subtitle overlap/non-positive duration at cue {index}")
        if len(lines) > 2 or any(len(line) > MAX_LINE_CHARS for line in lines):
            failures.append(f"subtitle layout violation at cue {index}")
        if any(unicodedata.normalize("NFC", line) != line or "\ufffd" in line for line in lines):
            failures.append(f"subtitle Unicode violation at cue {index}")
        previous_end = end
    subtitle_text = normalized(" ".join(" ".join(cue["lines"]) for cue in cues))
    transcript_text = normalized(paths["transcript"].read_text(encoding="utf-8-sig"))
    if subtitle_text != transcript_text:
        failures.append("subtitle wording differs from the locked spoken transcript")
    bridge_start = CONTENT_DURATION - CROSSFADE
    if previous_end > bridge_start:
        failures.append(f"last subtitle ends at {previous_end:.3f}s, inside credit bridge at {bridge_start:.3f}s")
    facts.append(f"Subtitles: {len(cues)} cues, exact transcript PASS, last cue {previous_end:.3f}s before bridge {bridge_start:.3f}s")

    manifest = json.loads(paths["picture_manifest"].read_text(encoding="utf-8"))
    if manifest.get("scene_count") != 95 or manifest.get("shot_count") != 156:
        failures.append("picture manifest does not contain 95 scenes / 156 shots")
    if int(manifest.get("max_asset_reuse", 99)) > 2:
        failures.append("a content asset is reused more than twice")
    used = set(manifest.get("asset_reuse", {}))
    banned_used = sorted(used & BANNED_ASSETS)
    if banned_used:
        failures.append("banned visual asset used: " + ", ".join(banned_used))
    category_seconds: defaultdict[str, float] = defaultdict(float)
    for shot in manifest.get("shots", []):
        category_seconds[str(shot["category"])] += float(shot["duration_seconds"])
    real = category_seconds["real_footage"] + CREDIT_DURATION
    ai = category_seconds["veo_flow_illustration"]
    real_ratio = real / (real + ai) * 100
    if not 25 <= real_ratio <= 40:
        failures.append(f"real/AI moving-footage ratio {real_ratio:.1f}/{100-real_ratio:.1f} is outside the target range")
    credit_reuse = json.loads(paths["credit_reuse"].read_text(encoding="utf-8"))
    if not credit_reuse.get("all_assets_unique") or any(int(row.get("reuse_count", 99)) != 1 for row in credit_reuse.get("rows", [])):
        failures.append("credit V4 contains repeated assets")
    facts.append(f"Visual plan: 156 shots / 104 content assets, max reuse {manifest.get('max_asset_reuse')}; moving footage ≈ {real_ratio:.1f}% real / {100-real_ratio:.1f}% AI")
    facts.append(f"Credit V4: {len(credit_reuse.get('rows', []))} real-footage shots, each used once")

    voice_probe = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(paths["voice"])]).strip())
    programme_probe = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(paths["programme_audio"])]).strip())
    if not math.isclose(voice_probe, 965.051104, abs_tol=0.002):
        failures.append(f"locked Vale master duration changed: {voice_probe:.6f}s")
    if not math.isclose(programme_probe, FINAL_DURATION, abs_tol=0.002):
        failures.append("programme audio duration differs from the final timeline")
    facts.append(f"Voice chain: one locked Vale master, {voice_probe:.6f}s, SHA-256 {sha256(paths['voice'])}")

    decode = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-xerror", "-i", str(paths["video"]), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if decode.returncode or decode.stderr.strip():
        failures.append("full audio/video decode failed: " + decode.stderr.strip()[-800:])
    else:
        facts.append("Full audio/video decode with -xerror: PASS")

    integrated, peak = audio_metrics(paths["video"], paths["report"].with_name("final_audio_ebur128.txt"))
    if not -16.8 <= integrated <= -15.0:
        failures.append(f"integrated loudness {integrated:.1f} LUFS is outside −16.8…−15.0")
    if peak > -1.5:
        failures.append(f"true peak {peak:.1f} dBFS exceeds −1.5 dBFS")
    facts.append(f"Final audio: {integrated:.1f} LUFS integrated, {peak:.1f} dBFS true peak")

    anomaly_text = run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(paths["video"]), "-vf", "blackdetect=d=1.2:pix_th=0.04,freezedetect=n=-58dB:d=12", "-an", "-f", "null", "-"],
        stderr=True,
    )
    paths["report"].with_name("final_video_anomaly_scan.txt").write_text(anomaly_text, encoding="utf-8")
    black_runs = re.findall(r"black_start:[^\n]+", anomaly_text)
    freeze_spans = [float(x) for x in re.findall(r"freeze_duration:\s*([0-9.]+)", anomaly_text)]
    if black_runs:
        failures.extend("black run requires review: " + item for item in black_runs)
    if freeze_spans:
        failures.append("freeze interval >=12s: " + ", ".join(f"{x:.2f}s" for x in freeze_spans))
    facts.append("Black/freeze scan: no black >=1.2s and no freeze >=12s" if not black_runs and not freeze_spans else "Black/freeze scan reported findings")

    make_contact_sheet(paths["video"], paths["contact_sheet"])
    final_hash = sha256(paths["video"])
    status = "PASS" if not failures else "FAIL"
    lines = [
        "FINAL V10 QA REPORT — FEENBERG DOCUMENTARY", "", f"STATUS: {status}",
        f"File: {paths['video']}", f"SHA-256: {final_hash}", "", "FACTS",
        *[f"- {item}" for item in facts], "", "FAILURES",
        *(["- None"] if not failures else [f"- {item}" for item in failures]), "", "WARNINGS / MANUAL REVIEW",
        *(["- None"] if not warnings else [f"- {item}" for item in warnings]), "",
        "Automated QA complements, but does not replace, manual review of physical logic, faces, typography and the credit bridge.",
    ]
    paths["report"].write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
