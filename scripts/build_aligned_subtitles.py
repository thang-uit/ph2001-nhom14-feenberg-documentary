#!/usr/bin/env python3
"""Force-align the locked Vietnamese narration to the final voice waveform.

Whisper is used only as a timing sensor.  Its recognized wording is never
written to the submission: every subtitle character comes from the locked
narration.  Exact transcript words are anchored to Whisper word timestamps,
and recognition gaps are interpolated between trustworthy anchors.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from build_subtitles import MAX_LINE_CHARS, can_wrap, normalize_text, split_into_cues


FPS = 30
MIN_GAP = 1 / FPS
MAX_CHARACTERS_PER_SECOND = 28.0


@dataclass(frozen=True)
class TimedWord:
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class Cue:
    index: int
    text: str
    lines: list[str]
    start: float
    end: float


def normalized_word(value: str) -> str:
    value = unicodedata.normalize("NFD", value.casefold())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return re.sub(r"[^0-9a-zA-ZđĐ]+", "", value)


def transcript_words(value: str) -> list[str]:
    return [word for word in re.split(r"\s+", normalize_text(value)) if word]


def whisper_words(payload: dict) -> list[TimedWord]:
    words: list[TimedWord] = []
    current_text = ""
    current_start: float | None = None
    current_end = 0.0

    def flush() -> None:
        nonlocal current_text, current_start, current_end
        cleaned = current_text.strip()
        if cleaned and normalized_word(cleaned) and current_start is not None:
            words.append(TimedWord(cleaned, current_start, max(current_start, current_end)))
        current_text = ""
        current_start = None
        current_end = 0.0

    for segment in payload["transcription"]:
        for token in segment.get("tokens", []):
            text = str(token.get("text", ""))
            if not text or (text.startswith("[") and text.endswith("]")):
                continue
            offsets = token.get("offsets") or {}
            start = float(offsets.get("from", 0)) / 1000
            end = float(offsets.get("to", offsets.get("from", 0))) / 1000
            if text[:1].isspace() and current_text:
                flush()
            if current_start is None:
                current_start = start
            current_text += text
            current_end = max(current_end, end)
    flush()
    return words


def align_words(exact: list[str], observed: list[TimedWord], duration: float) -> list[TimedWord]:
    exact_norm = [normalized_word(word) for word in exact]
    observed_norm = [normalized_word(word.text) for word in observed]
    matcher = difflib.SequenceMatcher(None, exact_norm, observed_norm, autojunk=False)
    anchors: dict[int, TimedWord] = {}
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            anchors[block.a + offset] = observed[block.b + offset]

    if len(anchors) < len(exact) * 0.55:
        raise SystemExit(
            f"Alignment is unreliable: only {len(anchors)}/{len(exact)} exact-word anchors"
        )

    aligned: list[TimedWord | None] = [None] * len(exact)
    for index, word in anchors.items():
        aligned[index] = TimedWord(exact[index], word.start, word.end)

    anchor_indexes = sorted(anchors)
    boundaries = [-1, *anchor_indexes, len(exact)]
    for left_index, right_index in zip(boundaries, boundaries[1:]):
        gap_indexes = list(range(left_index + 1, right_index))
        if not gap_indexes:
            continue
        left_time = 0.0 if left_index < 0 else anchors[left_index].end
        right_time = duration if right_index >= len(exact) else anchors[right_index].start
        if right_time <= left_time:
            right_time = left_time + max(0.12 * len(gap_indexes), 0.12)
        weights = [max(1, len(normalized_word(exact[index]))) for index in gap_indexes]
        total_weight = sum(weights)
        cursor = left_time
        for index, weight in zip(gap_indexes, weights):
            span = (right_time - left_time) * weight / total_weight
            aligned[index] = TimedWord(exact[index], cursor, cursor + span)
            cursor += span

    result: list[TimedWord] = []
    cursor = 0.0
    for index, item in enumerate(aligned):
        if item is None:
            raise AssertionError(f"Unaligned transcript word {index}")
        start = min(duration, max(cursor, item.start))
        end = min(duration, max(start + 0.01, item.end))
        result.append(TimedWord(item.text, start, end))
        cursor = start
    return result


def build_cues(text: str, words: list[TimedWord]) -> list[Cue]:
    cue_texts: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = normalize_text(paragraph)
        if paragraph:
            cue_texts.extend(split_into_cues(paragraph))

    cue_ranges: list[tuple[str, list[str], float, float]] = []
    word_cursor = 0
    for cue_text in cue_texts:
        cue_word_count = len(cue_text.split())
        cue_words = words[word_cursor : word_cursor + cue_word_count]
        if len(cue_words) != cue_word_count:
            raise AssertionError("Subtitle cue allocation exceeded aligned transcript")
        fits, lines = can_wrap(cue_text.split())
        if not fits:
            raise AssertionError(f"Cannot wrap subtitle cue: {cue_text}")
        cue_ranges.append((cue_text, lines, cue_words[0].start, cue_words[-1].end))
        word_cursor += cue_word_count
    if word_cursor != len(words):
        raise AssertionError(f"Subtitle allocation used {word_cursor}/{len(words)} words")

    cues: list[Cue] = []
    previous_end = 0.0
    for index, (cue_text, lines, raw_start, raw_end) in enumerate(cue_ranges):
        next_start = cue_ranges[index + 1][2] if index + 1 < len(cue_ranges) else raw_end + 0.25
        start = max(previous_end + (MIN_GAP if cues else 0.0), raw_start - 0.06)
        end = min(next_start - MIN_GAP, raw_end + 0.12)
        if end - start < 0.72:
            end = min(next_start - MIN_GAP, start + 0.72)
        # Prefer a modest lead-in during an existing natural pause instead of
        # displaying a dense Vietnamese cue too quickly.  This never changes
        # wording and never crosses the preceding cue's title-safe gap.
        minimum_readable_duration = len(cue_text) / MAX_CHARACTERS_PER_SECOND
        if end - start < minimum_readable_duration:
            earliest_start = previous_end + (MIN_GAP if cues else 0.0)
            start = max(earliest_start, end - minimum_readable_duration)
        if end <= start:
            raise SystemExit(f"Non-positive aligned subtitle cue at {index + 1}")
        cues.append(Cue(index + 1, cue_text, lines, start, end))
        previous_end = end
    return cues


def srt_timestamp(value: float) -> str:
    milliseconds = max(0, round(value * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def write_srt(cues: list[Cue], path: Path) -> None:
    blocks = []
    for cue in cues:
        blocks.append(
            f"{cue.index}\n{srt_timestamp(cue.start)} --> {srt_timestamp(cue.end)}\n"
            + "\n".join(cue.lines)
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def section_timing(
    sections_payload: dict,
    aligned: list[TimedWord],
    total_duration: float,
) -> list[dict]:
    timings: list[dict] = []
    cursor = 0
    for section in sections_payload["sections"]:
        count = len(transcript_words(section["clean_text"]))
        first = aligned[cursor]
        last = aligned[cursor + count - 1]
        timings.append(
            {
                "index": section["index"],
                "title": section["title"],
                "word_start": cursor,
                "word_end": cursor + count,
                "speech_start": first.start,
                "speech_end": last.end,
            }
        )
        cursor += count
    if cursor != len(aligned):
        raise AssertionError("Section transcript does not equal the locked narration")

    boundaries = [0.0]
    for previous, current in zip(timings, timings[1:]):
        boundaries.append((previous["speech_end"] + current["speech_start"]) / 2)
    boundaries.append(total_duration)
    for index, timing in enumerate(timings):
        timing["timeline_start"] = boundaries[index]
        timing["timeline_end"] = boundaries[index + 1]
        timing["timeline_duration"] = boundaries[index + 1] - boundaries[index]
    return timings


def write_report(
    path: Path,
    exact_words: list[str],
    observed: list[TimedWord],
    cues: list[Cue],
    anchor_count: int,
) -> None:
    errors: list[str] = []
    cue_text = normalize_text(" ".join(cue.text for cue in cues))
    exact_text = normalize_text(" ".join(exact_words))
    if cue_text != exact_text:
        errors.append("Subtitle wording differs from the locked narration.")
    for previous, current in zip(cues, cues[1:]):
        if current.start <= previous.end:
            errors.append(f"Timestamp overlap: cue {previous.index}->{current.index}")
    long_lines = [cue.index for cue in cues for line in cue.lines if len(line) > MAX_LINE_CHARS]
    if long_lines:
        errors.append(f"Lines exceed {MAX_LINE_CHARS} characters: {long_lines}")
    status = "PASS" if not errors else "FAIL"
    path.write_text(
        "SUBTITLE QA REPORT — WAVEFORM-ALIGNED FINAL VOICE\n"
        f"Status: {status}\n"
        f"Locked narration words: {len(exact_words)}\n"
        f"Whisper timing words: {len(observed)}\n"
        f"Exact timing anchors: {anchor_count} ({anchor_count / len(exact_words):.1%})\n"
        f"Subtitle cues: {len(cues)}\n"
        "Subtitle text source: locked narration only; ASR wording is never used.\n"
        "Unicode: NFC Vietnamese\n"
        "Maximum lines per cue: 2\n"
        f"Maximum characters per line: {MAX_LINE_CHARS}\n"
        f"Overlap check: {'PASS' if not any('overlap' in error.lower() for error in errors) else 'FAIL'}\n"
        f"Transcript identity check: {'PASS' if cue_text == exact_text else 'FAIL'}\n"
        + ("Errors: none\n" if not errors else "Errors:\n- " + "\n- ".join(errors) + "\n"),
        encoding="utf-8",
    )
    if errors:
        raise SystemExit("\n".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--narration", type=Path, required=True)
    parser.add_argument("--sections", type=Path, required=True)
    parser.add_argument("--whisper-json", type=Path, required=True)
    parser.add_argument("--voice-duration", type=float, required=True)
    parser.add_argument("--output-srt", type=Path, required=True)
    parser.add_argument("--output-timing", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    narration = unicodedata.normalize("NFC", args.narration.read_text(encoding="utf-8"))
    exact = transcript_words(narration)
    whisper_payload = json.loads(args.whisper_json.read_text(encoding="utf-8"))
    observed = whisper_words(whisper_payload)
    aligned = align_words(exact, observed, args.voice_duration)
    cues = build_cues(narration, aligned)

    args.output_srt.parent.mkdir(parents=True, exist_ok=True)
    args.output_timing.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    write_srt(cues, args.output_srt)

    sections_payload = json.loads(args.sections.read_text(encoding="utf-8"))
    timings = section_timing(sections_payload, aligned, args.voice_duration)
    args.output_timing.write_text(
        json.dumps(
            {
                "voice_duration": args.voice_duration,
                "exact_word_count": len(exact),
                "whisper_word_count": len(observed),
                "sections": timings,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    exact_norm = [normalized_word(word) for word in exact]
    observed_norm = [normalized_word(word.text) for word in observed]
    anchor_count = sum(
        block.size
        for block in difflib.SequenceMatcher(None, exact_norm, observed_norm, autojunk=False).get_matching_blocks()
    )
    write_report(args.report, exact, observed, cues, anchor_count)
    print(f"Aligned subtitles: {args.output_srt} ({len(cues)} cues)")
    print(f"Voice timing map: {args.output_timing}")


if __name__ == "__main__":
    main()
