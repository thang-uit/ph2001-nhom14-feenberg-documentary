#!/usr/bin/env python3
"""Extract the spoken Vietnamese script and its locked chapter timings."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


HEADER_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2})[–-](?P<end>\d{2}:\d{2})\s+—\s+(?P<title>.+)$"
)
PAUSE_RE = re.compile(r"\[PAUSE\s+(?P<seconds>\d+(?:\.\d+)?)\]")
EMPHASIS_RE = re.compile(r"\[EMPHASIS\]\s*")
META_RE = re.compile(r"^\[(?:NHÃN|CLAIM):")


@dataclass(frozen=True)
class Section:
    index: int
    title: str
    start_time: str
    end_time: str
    start_seconds: int
    end_seconds: int
    target_duration_seconds: int
    text_with_markers: str
    clean_text: str
    say_text: str
    word_count: int


def parse_mmss(value: str) -> int:
    minutes, seconds = (int(part) for part in value.split(":"))
    if seconds >= 60:
        raise ValueError(f"Invalid MM:SS timestamp: {value}")
    return minutes * 60 + seconds


def normalize_paragraphs(lines: list[str]) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if set(line) == {"="} or META_RE.match(line):
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs).strip()


def without_markers(text: str) -> str:
    text = EMPHASIS_RE.sub("", text)
    text = PAUSE_RE.sub("", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def for_macos_say(text: str) -> str:
    text = EMPHASIS_RE.sub("", text)

    def pause_command(match: re.Match[str]) -> str:
        milliseconds = round(float(match.group("seconds")) * 1000)
        return f" [[slnc {milliseconds}]] "

    text = PAUSE_RE.sub(pause_command, text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_sections(source: Path) -> list[Section]:
    lines = source.read_text(encoding="utf-8").splitlines()
    raw_sections: list[tuple[str, str, str, list[str]]] = []
    current_header: tuple[str, str, str] | None = None
    current_lines: list[str] = []

    for line in lines:
        match = HEADER_RE.match(line.strip())
        if match:
            if current_header is not None:
                raw_sections.append((*current_header, current_lines))
            current_header = (
                match.group("start"),
                match.group("end"),
                match.group("title").strip(),
            )
            current_lines = []
        elif current_header is not None:
            current_lines.append(line)

    if current_header is not None:
        raw_sections.append((*current_header, current_lines))

    sections: list[Section] = []
    for start_time, end_time, title, body_lines in raw_sections:
        text_with_markers = normalize_paragraphs(body_lines)
        clean_text = without_markers(text_with_markers)
        if not clean_text or title.upper().startswith("END CREDITS"):
            continue
        start_seconds = parse_mmss(start_time)
        end_seconds = parse_mmss(end_time)
        if end_seconds <= start_seconds:
            raise ValueError(f"Non-positive duration for {title}")
        word_count = len(clean_text.split())
        sections.append(
            Section(
                index=len(sections) + 1,
                title=title,
                start_time=start_time,
                end_time=end_time,
                start_seconds=start_seconds,
                end_seconds=end_seconds,
                target_duration_seconds=end_seconds - start_seconds,
                text_with_markers=text_with_markers,
                clean_text=clean_text,
                say_text=for_macos_say(text_with_markers),
                word_count=word_count,
            )
        )

    if not sections:
        raise ValueError("No spoken sections were found")
    for previous, current in zip(sections, sections[1:]):
        if previous.end_seconds != current.start_seconds:
            raise ValueError(
                f"Spoken section gap/overlap: {previous.title} -> {current.title}"
            )
    return sections


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.resolve()
    output_dir = args.output_dir.resolve()
    if not source.is_file():
        raise SystemExit(f"Narration source not found: {source}")

    sections = parse_sections(source)
    output_dir.mkdir(parents=True, exist_ok=True)

    clean_text = "\n\n".join(section.clean_text for section in sections) + "\n"
    say_text = "\n\n".join(section.say_text for section in sections) + "\n"
    (output_dir / "narration_spoken.txt").write_text(clean_text, encoding="utf-8")
    (output_dir / "narration_macos_say.txt").write_text(say_text, encoding="utf-8")

    payload = {
        "source": str(source),
        "section_count": len(sections),
        "spoken_start_seconds": sections[0].start_seconds,
        "spoken_end_seconds": sections[-1].end_seconds,
        "spoken_timeline_seconds": sections[-1].end_seconds - sections[0].start_seconds,
        "word_count": sum(section.word_count for section in sections),
        "sections": [asdict(section) for section in sections],
    }
    (output_dir / "narration_sections.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Extracted {payload['section_count']} sections, "
        f"{payload['word_count']} words/tokens, "
        f"timeline {payload['spoken_timeline_seconds']} seconds."
    )


if __name__ == "__main__":
    main()
