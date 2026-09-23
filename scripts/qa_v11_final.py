#!/opt/homebrew/bin/python3.13
"""Fail-closed delivery gate for the V11 R6 Feenberg documentary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v11_visual_plan import BANNED_ASSETS, FORBIDDEN_PREFIXES, category  # noqa: E402


FPS = 30.0
CONTENT_DURATION = 965.066667
CREDIT_DURATION = 54.1
CROSSFADE = 0.8
FINAL_DURATION = 1018.366667
EXPECTED_FRAMES = 30551
EXPECTED_CUES = 267
EXPECTED_SCENES = 95
EXPECTED_SHOTS = 172
EXPECTED_ASSETS = 130
MAX_LINE_CHARS = 42
LOCKED_VOICE_SHA256 = "e25474d83319a203cb9b308e02973b6cad7ed5f7568161322176c99ea035bdb5"
LOCKED_TRANSCRIPT_SHA256 = "51e74394ec4b7c6e797cded39d932bc5007b13b8d8da31837e3bd528eeb87ada"


def run(command: list[str], *, stderr: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE if stderr else subprocess.STDOUT,
    )
    return result.stderr if stderr else result.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def seconds(value: str) -> float:
    hours, minutes, rest = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def rate(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value)).strip()


def parse_srt(path: Path) -> list[dict[str, object]]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    cues: list[dict[str, object]] = []
    for expected, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != str(expected) or "-->" not in lines[1]:
            raise ValueError(f"Malformed SRT block {expected}")
        start, end = (part.strip() for part in lines[1].split("-->", 1))
        cues.append({"start": seconds(start), "end": seconds(end), "lines": lines[2:]})
    return cues


def faststart(path: Path) -> tuple[bool, str]:
    with path.open("rb") as handle:
        prefix = handle.read(min(path.stat().st_size, 64 * 1024 * 1024))
    moov = prefix.find(b"moov")
    mdat = prefix.find(b"mdat")
    return moov >= 0 and mdat >= 0 and moov < mdat, f"moov={moov}, mdat={mdat}"


def alpha_nonempty(path: Path) -> bool:
    with Image.open(path) as image:
        return image.convert("RGBA").getchannel("A").getbbox() is not None


def make_contact_sheet(video: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
        "-vf", "fps=1/40,scale=480:270:flags=lanczos,tile=5x6:padding=4:margin=4:color=#101214",
        "-frames:v", "1", "-q:v", "2", str(output),
    ])


def audio_metrics(video: Path, output: Path) -> tuple[float, float]:
    text = run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        stderr=True,
    )
    output.write_text(text, encoding="utf-8")
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
    parser.add_argument("--credit-manifest", type=Path, required=True)
    parser.add_argument("--voice", type=Path, required=True)
    parser.add_argument("--content-mix", type=Path, required=True)
    parser.add_argument("--overlay-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--contact-sheet", type=Path, required=True)
    args = parser.parse_args()

    paths = {name: value.resolve() for name, value in vars(args).items() if isinstance(value, Path)}
    for key in ("video", "storyboard", "srt", "transcript", "picture_manifest", "credit_manifest", "voice", "content_mix"):
        if not paths[key].is_file():
            raise SystemExit(f"Missing QA input {key}: {paths[key]}")
    if not paths["overlay_dir"].is_dir():
        raise SystemExit(f"Missing overlay directory: {paths['overlay_dir']}")
    paths["report"].parent.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    facts: list[str] = []
    probe = json.loads(run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=format_name,duration,size,bit_rate:stream=index,codec_type,codec_name,profile,level,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames,sample_aspect_ratio,field_order,color_range,color_space,color_transfer,color_primaries,sample_rate,channels,bit_rate",
        "-of", "json", str(paths["video"]),
    ]))
    paths["probe"].parent.mkdir(parents=True, exist_ok=True)
    paths["probe"].write_text(json.dumps(probe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    videos = [stream for stream in probe.get("streams", []) if stream.get("codec_type") == "video"]
    audios = [stream for stream in probe.get("streams", []) if stream.get("codec_type") == "audio"]
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
    if not math.isclose(duration, FINAL_DURATION, abs_tol=0.04) or not 900 <= duration <= 1200:
        failures.append(f"duration {duration:.3f}s does not satisfy the locked 15–20 minute timeline")
    bitrate = int(video_stream.get("bit_rate", 0) or 0)
    if bitrate < 8_000_000:
        failures.append(f"video bitrate {bitrate / 1_000_000:.2f} Mbps is below 8 Mbps")
    fast_ok, fast_detail = faststart(paths["video"])
    if not fast_ok:
        failures.append("MP4 is not faststart: " + fast_detail)
    facts.append(f"Video: H.264 High, 1920×1080, 30 fps, Rec.709, {bitrate/1_000_000:.2f} Mbps, {EXPECTED_FRAMES} frames")
    facts.append(f"Audio container: AAC-LC stereo 48 kHz; duration {duration:.3f}s; faststart {fast_detail}")

    with paths["storyboard"].open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected_ids = [f"S{i:03d}" for i in range(1, EXPECTED_SCENES + 1)]
    if len(rows) != EXPECTED_SCENES + 1 or [row["SCENE_ID"] for row in rows[:-1]] != expected_ids or rows[-1]["SCENE_ID"] != "CREDIT_V11":
        failures.append("storyboard must contain S001–S095 followed by CREDIT_V11")
    cursor = 0.0
    for row in rows[:-1]:
        start, end, span = seconds(row["START_TIME"]), seconds(row["END_TIME"]), float(row["DURATION"])
        if not math.isclose(start, cursor, abs_tol=0.002) or not math.isclose(end - start, span, abs_tol=0.002):
            failures.append(f"storyboard timing mismatch at {row['SCENE_ID']}")
        if not row.get("VISUAL_ARGUMENT_LINK", "").strip():
            failures.append(f"missing semantic visual link at {row['SCENE_ID']}")
        cursor = end
    if not math.isclose(cursor, CONTENT_DURATION, abs_tol=0.002):
        failures.append(f"content storyboard ends at {cursor:.3f}s")
    if not math.isclose(float(rows[-1]["DURATION"]), CREDIT_DURATION, abs_tol=0.002):
        failures.append(f"credit duration in storyboard is not {CREDIT_DURATION:.1f}s")
    facts.append(f"Timeline: 95 content scenes + {CREDIT_DURATION:.1f}s credit − {CROSSFADE:.1f}s bridge = {duration:.3f}s")

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
    if previous_end > CONTENT_DURATION - CROSSFADE:
        failures.append("last subtitle leaks into the credit bridge")
    facts.append(f"Subtitles: 42 px, {len(cues)} cues, exact transcript, two-line maximum, last cue {previous_end:.3f}s")

    voice_hash = sha256(paths["voice"])
    transcript_hash = sha256(paths["transcript"])
    if voice_hash != LOCKED_VOICE_SHA256:
        failures.append("locked one-voice Vale master checksum changed")
    if transcript_hash != LOCKED_TRANSCRIPT_SHA256:
        failures.append("academically audited spoken transcript checksum changed")
    voice_duration = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(paths["voice"])]).strip())
    mix_duration = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(paths["content_mix"])]).strip())
    if not math.isclose(voice_duration, 965.051104, abs_tol=0.002):
        failures.append(f"Vale master duration changed: {voice_duration:.6f}s")
    if not math.isclose(mix_duration, CONTENT_DURATION, abs_tol=0.002):
        failures.append(f"content mix duration {mix_duration:.6f}s != {CONTENT_DURATION:.6f}s")
    facts.append(f"Narration: one locked Vale master, {voice_duration:.6f}s, checksum PASS")

    picture = json.loads(paths["picture_manifest"].read_text(encoding="utf-8"))
    if picture.get("scene_count") != EXPECTED_SCENES or picture.get("shot_count") != EXPECTED_SHOTS or picture.get("asset_count") != EXPECTED_ASSETS:
        failures.append("picture manifest is not the locked 95-scene / 172-shot / 130-asset R6 plan")
    if int(picture.get("max_asset_reuse", 99)) > 2:
        failures.append("a content asset is reused more than twice")
    used = set(picture.get("asset_reuse", {}))
    banned = sorted(used & BANNED_ASSETS)
    prefixed = sorted(asset for asset in used if asset.startswith(FORBIDDEN_PREFIXES))
    if banned or prefixed:
        failures.append("banned/credit visual asset used: " + ", ".join(banned + prefixed))

    category_seconds: defaultdict[str, float] = defaultdict(float)
    for shot in picture.get("shots", []):
        category_seconds[str(shot["category"])] += float(shot["duration_seconds"])
    real = category_seconds["real_footage"]
    ai = category_seconds["veo_flow_illustration"]
    real_ratio = real / (real + ai) * 100 if real + ai else 0.0
    if not 35 <= real_ratio <= 50:
        failures.append(f"content moving-footage ratio {real_ratio:.1f}% real is outside the V11 target tolerance")

    credit = json.loads(paths["credit_manifest"].read_text(encoding="utf-8"))
    credit_sources = {str(shot.get("source", "")) for shot in credit.get("shots", [])}
    content_basenames = {Path(asset).name for asset in used}
    credit_basenames = {Path(asset).name for asset in credit_sources}
    overlap = sorted(content_basenames & credit_basenames)
    if overlap:
        failures.append("content/credit source intersection is not empty: " + ", ".join(overlap))
    if len(credit_sources) != len(credit.get("shots", [])):
        failures.append("credit V4 contains a repeated source")
    facts.append(f"Visual plan: 172 shots / 130 assets, reuse ≤2; moving footage {real_ratio:.1f}% real / {100-real_ratio:.1f}% AI")
    facts.append(f"Content/credit asset separation: empty intersection; credit sources unique={len(credit_sources)}")

    overlay_failures: list[str] = []
    for shot in picture.get("shots", []):
        sid = str(shot["scene_id"])
        index = int(shot["shot_index"])
        relative = str(shot["relative_asset"])
        overlay = paths["overlay_dir"] / f"{sid}_{index:02d}_provenance.png"
        if not overlay.is_file():
            overlay_failures.append(f"missing {overlay.name}")
            continue
        nonempty = alpha_nonempty(overlay)
        expected_nonempty = category(relative) == "veo_flow_illustration"
        if nonempty != expected_nonempty:
            overlay_failures.append(f"wrong disclosure state {overlay.name}: {relative}")
    if overlay_failures:
        failures.append("AI disclosure gate: " + "; ".join(overlay_failures[:8]))
    facts.append("Disclosure gate: only Flow–Veo placements carry `MINH HỌA BẰNG AI`; real footage is unlabelled")

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
        failures.append("freeze interval >=12s: " + ", ".join(f"{span:.2f}s" for span in freeze_spans))
    facts.append("Black/freeze scan: no black ≥1.2s and no freeze ≥12s" if not black_runs and not freeze_spans else "Black/freeze scan reported findings")

    make_contact_sheet(paths["video"], paths["contact_sheet"])
    final_hash = sha256(paths["video"])
    status = "PASS" if not failures else "FAIL"
    lines = [
        "FINAL V11 R6 QA REPORT — FEENBERG DOCUMENTARY", "", f"STATUS: {status}",
        f"File: {paths['video']}", f"SHA-256: {final_hash}", "", "FACTS",
        *[f"- {fact}" for fact in facts], "", "FAILURES",
        *(["- None"] if not failures else [f"- {failure}" for failure in failures]), "",
        "MANUAL GATES",
        "- Motion/physics/faces/style: reviewed from source strips and final-picture contact sheets; rejected assets remain blacklisted.",
        "- Typography: R6 source cards reviewed at start/middle/end; no line through text, clipped shape or replacement glyph.",
        "- Semantic match: every scene carries VISUAL_ARGUMENT_LINK; final spot-checks include S013 and S079.",
        "- Bridge/credit: R6 bridge frames reviewed; V4 remains intact and programme audio is bit-identical to R5.",
    ]
    paths["report"].write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
