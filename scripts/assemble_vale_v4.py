#!/usr/bin/env python3
"""Assemble the verified, single-speaker ChatGPT Vale narration master.

Only the approved Vale takes are used.  Known conversational lead-ins are
trimmed at their exact speech boundaries and every part is normalized to the
same broadcast level before concatenation.  The generated JSON is the timing
source for subtitle and picture retiming.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


SAMPLE_RATE = 48_000
PART_GAP = 0.18
SECTION_GAP = 0.75


@dataclass(frozen=True)
class Part:
    section: int
    name: str
    source: str
    trim_start: float = 0.0


PARTS = (
    Part(1, "section_01", "audio/vo/chatgpt_vale_v3/section_01_part_01_vale.wav"),
    Part(2, "section_02", "audio/vo/chatgpt_vale_v3/section_02_part_01_vale.wav"),
    # Remove the false start “Cách nhìn…”, keeping the complete restart.
    Part(3, "section_03_part_01", "audio/vo/chatgpt_vale_v4/section_03_part_01_vale.wav", 2.84),
    Part(3, "section_03_part_02", "audio/vo/chatgpt_vale_v4/section_03_part_02_vale.wav"),
    Part(4, "section_04", "audio/vo/chatgpt_vale_v4/section_04_full_vale.wav"),
    Part(5, "section_05_part_01", "audio/vo/chatgpt_vale_v4/section_05_part_01_vale_uncut.wav"),
    Part(5, "section_05_part_02", "audio/vo/chatgpt_vale_v4/section_05_part_02_vale_uncut.wav"),
    Part(5, "section_05_part_03", "audio/vo/chatgpt_vale_v4/section_05_part_03_vale.wav"),
    # Remove the spoken “Hmm” before “Vậy…”.
    Part(6, "section_06_part_01", "audio/vo/chatgpt_vale_v4/section_06_part_01_vale.wav", 1.75),
    Part(6, "section_06_part_02", "audio/vo/chatgpt_vale_v4/section_06_part_02_vale.wav"),
    Part(6, "section_06_part_03", "audio/vo/chatgpt_vale_v4/section_06_part_03_vale.wav"),
    # Remove the complete conversational lead-in before “Hãy theo dõi…”.
    Part(7, "section_07", "audio/vo/chatgpt_vale_v4/section_07_full_vale.wav", 3.72),
    Part(8, "section_08_part_01", "audio/vo/chatgpt_vale_v4/section_08_part_01_vale.wav"),
    # The second take starts cleanly on “Hai”, with the conversational lead-in
    # excluded by the capture processor.
    Part(8, "section_08_part_02", "audio/vo/chatgpt_vale_v4/section_08_part_02_vale_take2.wav"),
    Part(8, "section_08_part_03", "audio/vo/chatgpt_vale_v4/section_08_part_03_vale.wav"),
    # Remove “Ừm, để xem” before “Từ đó…”.
    Part(8, "section_08_part_04", "audio/vo/chatgpt_vale_v4/section_08_part_04_vale.wav", 1.25),
    # Clean section 9 uses the same Vale voice throughout. Its conclusion
    # sentence is a verified Read Aloud pickup because the earlier take
    # skipped the final clause “rồi hỏi… cải biến thật”.
    Part(9, "section_09", "audio/vo/chatgpt_vale_v4/section_09_part_01_vale_patched.wav"),
)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def duration(path: Path) -> float:
    output = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return float(output.strip())


def make_silence(path: Path, seconds: float) -> None:
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r={SAMPLE_RATE}:cl=mono",
            "-t",
            f"{seconds:.3f}",
            "-c:a",
            "pcm_s24le",
            str(path),
        ]
    )


def render_part(source: Path, output: Path, trim_start: float) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{trim_start:.3f}",
            "-i",
            str(source),
            "-af",
            (
                "aresample=48000,highpass=f=75,lowpass=f=15500,"
                "acompressor=threshold=0.10:ratio=1.7:attack=12:release=120,"
                "loudnorm=I=-16.5:TP=-1.5:LRA=6,"
                "afade=t=in:st=0:d=0.012,areverse,"
                "afade=t=in:st=0:d=0.012,areverse"
            ),
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path, default=Path("audio/vo/VO_VALE_V4_MASTER_48K.wav"))
    parser.add_argument("--timing", type=Path, default=Path("qa/vale_v4_assembly_timing.json"))
    args = parser.parse_args()

    root = args.project_dir.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    timing = args.timing if args.timing.is_absolute() else root / args.timing
    work = root / "audio/vo/chatgpt_vale_v4/assembled_parts"
    work.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    timing.parent.mkdir(parents=True, exist_ok=True)

    part_silence = work / "silence_part.wav"
    section_silence = work / "silence_section.wav"
    make_silence(part_silence, PART_GAP)
    make_silence(section_silence, SECTION_GAP)

    concat_entries: list[Path] = []
    records: list[dict[str, object]] = []
    cursor = 0.0
    for index, part in enumerate(PARTS):
        source = root / part.source
        if not source.is_file():
            raise FileNotFoundError(source)
        clean = work / f"{index + 1:02d}_{part.name}.wav"
        render_part(source, clean, part.trim_start)
        clean_duration = duration(clean)
        records.append(
            {
                "section": part.section,
                "name": part.name,
                "source": part.source,
                "trim_start": part.trim_start,
                "timeline_start": cursor,
                "timeline_end": cursor + clean_duration,
                "duration": clean_duration,
            }
        )
        concat_entries.append(clean)
        cursor += clean_duration
        if index == len(PARTS) - 1:
            continue
        gap = SECTION_GAP if PARTS[index + 1].section != part.section else PART_GAP
        concat_entries.append(section_silence if gap == SECTION_GAP else part_silence)
        cursor += gap

    concat_file = work / "concat.ffconcat"
    concat_file.write_text(
        "ffconcat version 1.0\n"
        + "\n".join(f"file {shlex.quote(str(path.resolve()))}" for path in concat_entries)
        + "\n",
        encoding="utf-8",
    )
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
            str(concat_file),
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )
    final_duration = duration(output)
    payload = {
        "voice": "ChatGPT Vale",
        "single_voice": True,
        "sample_rate": SAMPLE_RATE,
        "part_gap": PART_GAP,
        "section_gap": SECTION_GAP,
        "duration": final_duration,
        "parts": records,
    }
    timing.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Vale v4 master: {output}")
    print(f"Duration: {final_duration:.3f}s ({final_duration / 60:.2f} min)")
    print(f"Timing: {timing}")


if __name__ == "__main__":
    main()
