#!/usr/bin/env python3
"""Prepare and assemble section-level OpenAI.fm narration exports.

The browser-facing generation step is intentionally manual/observable: the
official OpenAI.fm demo generates one MP3 per locked narration section.  This
script owns deterministic text extraction, file naming, validation, pacing,
and assembly so the production timeline stays reproducible.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from extract_narration import parse_sections


TARGET_SAMPLE_RATE = 48_000
TARGET_CHANNELS = 2


@dataclass(frozen=True)
class ExportRecord:
    section: int
    part: int
    title: str
    word_count: int
    char_count: int
    text_file: str
    audio_file: str


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def probe_duration(path: Path) -> float:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nk=1:nw=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(raw)


def split_for_tts(text: str, max_chars: int) -> list[str]:
    """Split without rewriting, preferring paragraph then sentence boundaries."""

    if max_chars < 300:
        raise ValueError("max_chars must be at least 300")
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    units: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            units.append(paragraph)
            continue
        sentences = [
            item.strip()
            for item in re.split(r"(?<=[.!?])\s+", paragraph)
            if item.strip()
        ]
        current = ""
        for sentence in sentences:
            candidate = f"{current} {sentence}".strip()
            if current and len(candidate) > max_chars:
                units.append(current)
                current = sentence
            else:
                current = candidate
        if current:
            units.append(current)

    chunks: list[str] = []
    current = ""
    for unit in units:
        candidate = f"{current}\n\n{unit}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = unit
        else:
            current = candidate
    if current:
        chunks.append(current)
    if any(len(chunk) > max_chars for chunk in chunks):
        raise ValueError("A TTS chunk still exceeds the character limit")
    normalized_original = re.sub(r"\s+", " ", text).strip()
    normalized_chunks = re.sub(r"\s+", " ", " ".join(chunks)).strip()
    if normalized_original != normalized_chunks:
        raise AssertionError("TTS splitting changed the narration text")
    return chunks


def prepare(
    source: Path,
    output_dir: Path,
    max_chars: int,
    audio_extension: str,
    voice: str,
) -> None:
    audio_extension = audio_extension.lower().lstrip(".")
    if audio_extension not in {"mp3", "wav", "m4a"}:
        raise ValueError("audio_extension must be mp3, wav, or m4a")
    sections = parse_sections(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[ExportRecord] = []
    for section in sections:
        chunks = split_for_tts(section.clean_text, max_chars=max_chars)
        for part, chunk in enumerate(chunks, start=1):
            stem = f"section_{section.index:02d}_part_{part:02d}"
            text_file = output_dir / f"{stem}.txt"
            text_file.write_text(chunk + "\n", encoding="utf-8")
            audio_file = output_dir / f"{stem}_{voice.lower()}.{audio_extension}"
            records.append(
                ExportRecord(
                    section=section.index,
                    part=part,
                    title=section.title,
                    word_count=len(chunk.split()),
                    char_count=len(chunk),
                    text_file=str(text_file),
                    audio_file=str(audio_file),
                )
            )
    manifest = output_dir / "openai_voice_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "source": str(source),
                "voice": voice,
                "model_surface": "ChatGPT voice / OpenAI audio surface",
                "max_chars_per_chunk": max_chars,
                "records": [asdict(record) for record in records],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Prepared {len(records)} section scripts in {output_dir}")


def detect_primary_speech_window(path: Path) -> tuple[float, float]:
    """Locate the complete narration window in a system-audio capture.

    A long ChatGPT read-aloud may contain natural pauses longer than the
    silence detector threshold.  Selecting only the single longest block can
    therefore discard whole chapters.  We instead keep the strongest cluster
    of plausible speech blocks, allowing editorial pauses inside the cluster
    while rejecting short browser/UI sounds before or after playback.
    """

    duration = probe_duration(path)
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "silencedetect=noise=-52dB:d=1.5",
            "-f",
            "null",
            "-",
        ],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr)

    events = re.findall(
        r"silence_(start|end):\s*([0-9.]+)",
        result.stderr,
    )
    silences: list[tuple[float, float]] = []
    current_start: float | None = None
    for kind, raw_value in events:
        value = float(raw_value)
        if kind == "start":
            current_start = value
        elif current_start is not None:
            silences.append((current_start, value))
            current_start = None
    if current_start is not None:
        silences.append((current_start, duration))

    speech_blocks: list[tuple[float, float]] = []
    cursor = 0.0
    for silence_start, silence_end in silences:
        if silence_start > cursor:
            speech_blocks.append((cursor, silence_start))
        cursor = max(cursor, silence_end)
    if cursor < duration:
        speech_blocks.append((cursor, duration))
    candidates = [block for block in speech_blocks if block[1] - block[0] >= 2.0]
    if not candidates:
        raise SystemExit(f"No plausible speech block found in {path}")

    clusters: list[list[tuple[float, float]]] = []
    for block in candidates:
        if not clusters or block[0] - clusters[-1][-1][1] > 12.0:
            clusters.append([block])
        else:
            clusters[-1].append(block)

    cluster = max(
        clusters,
        key=lambda blocks: sum(end - start for start, end in blocks),
    )
    start, end = cluster[0][0], cluster[-1][1]
    return max(0.0, start - 0.12), min(duration, end + 0.28)


def process_capture(raw_capture: Path, output: Path) -> None:
    start, end = detect_primary_speech_window(raw_capture)
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.6f}",
            "-t",
            f"{end - start:.6f}",
            "-i",
            str(raw_capture),
            "-af",
            f"aresample={TARGET_SAMPLE_RATE}",
            "-ar",
            str(TARGET_SAMPLE_RATE),
            "-ac",
            str(TARGET_CHANNELS),
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )
    print(
        f"Processed capture: {raw_capture.name} -> {output.name} "
        f"({start:.2f}s–{end:.2f}s, {probe_duration(output):.2f}s)"
    )


def validate(output_dir: Path) -> list[Path]:
    manifest_path = output_dir / "openai_voice_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    files: list[Path] = []
    problems: list[str] = []
    for record in payload["records"]:
        audio = Path(record["audio_file"])
        if not audio.is_file():
            problems.append(f"missing section {record['section']:02d}: {audio}")
            continue
        duration = probe_duration(audio)
        words_per_minute = record["word_count"] / duration * 60
        if duration < 10:
            problems.append(
                f"implausibly short section {record['section']:02d}: {duration:.2f}s"
            )
        print(
            f"section {record['section']:02d} part {record['part']:02d}: "
            f"{duration:7.2f}s, "
            f"{words_per_minute:6.1f} wpm, {audio.name}"
        )
        files.append(audio)
    if problems:
        raise SystemExit("\n".join(problems))
    return files


def assemble(output_dir: Path, output: Path, target_wpm: float) -> None:
    files = validate(output_dir)
    manifest = json.loads(
        (output_dir / "openai_voice_manifest.json").read_text(encoding="utf-8")
    )
    if not 140 <= target_wpm <= 210:
        raise SystemExit("target_wpm must be between 140 and 210")
    filter_parts: list[str] = []
    inputs: list[str] = []
    labels: list[str] = []
    for index, (path, record) in enumerate(zip(files, manifest["records"])):
        inputs.extend(["-i", str(path)])
        label = f"a{index}"
        duration = probe_duration(path)
        desired_duration = record["word_count"] / target_wpm * 60
        tempo = duration / desired_duration
        if not 0.5 <= tempo <= 2.0:
            raise SystemExit(
                f"section {record['section']:02d} part {record['part']:02d} "
                f"requires unsupported atempo={tempo:.4f}"
            )
        # A short editorial breath separates chapters without the sluggish
        # one-to-four-second synthetic gaps of the earlier draft.
        filter_parts.append(
            f"[{index}:a]aresample={TARGET_SAMPLE_RATE},"
            f"atempo={tempo:.6f},"
            "apad=pad_dur=0.45,asetpts=PTS-STARTPTS"
            f"[{label}]"
        )
        labels.append(f"[{label}]")
    filter_parts.append(
        "".join(labels) + f"concat=n={len(files)}:v=0:a=1[voice]"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            *inputs,
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[voice]",
            "-ar",
            str(TARGET_SAMPLE_RATE),
            "-ac",
            str(TARGET_CHANNELS),
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )
    print(f"Assembled raw OpenAI voice: {output} ({probe_duration(output):.2f}s)")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--source", type=Path, required=True)
    prepare_parser.add_argument("--output-dir", type=Path, required=True)
    prepare_parser.add_argument("--max-chars", type=int, default=850)
    prepare_parser.add_argument(
        "--audio-extension",
        choices=("mp3", "wav", "m4a"),
        default="mp3",
    )
    prepare_parser.add_argument("--voice", default="cedar")

    process_parser = subparsers.add_parser("process-capture")
    process_parser.add_argument("--input", type=Path, required=True)
    process_parser.add_argument("--output", type=Path, required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--output-dir", type=Path, required=True)

    assemble_parser = subparsers.add_parser("assemble")
    assemble_parser.add_argument("--output-dir", type=Path, required=True)
    assemble_parser.add_argument("--output", type=Path, required=True)
    assemble_parser.add_argument("--target-wpm", type=float, default=170.0)

    args = parser.parse_args()
    if args.command == "prepare":
        prepare(
            args.source.resolve(),
            args.output_dir.resolve(),
            args.max_chars,
            args.audio_extension,
            args.voice,
        )
    elif args.command == "process-capture":
        process_capture(args.input.resolve(), args.output.resolve())
    elif args.command == "validate":
        validate(args.output_dir.resolve())
    else:
        assemble(args.output_dir.resolve(), args.output.resolve(), args.target_wpm)


if __name__ == "__main__":
    main()
