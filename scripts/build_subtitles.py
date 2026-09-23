#!/usr/bin/env python3
"""Build and structurally audit Vietnamese SRT from the locked narration."""

from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from extract_narration import EMPHASIS_RE, PAUSE_RE, parse_sections


FPS = 30
MAX_LINE_CHARS = 42
MAX_CUE_CHARS = 64
MAX_CUE_LINES = 2
GAP_FRAMES = 1
VOICE_FILL_RATIO = 0.985
BREAK_PUNCTUATION = (".", "?", "!", ":", ";", ",", "—")


@dataclass
class CueDraft:
    text: str
    pause_after_seconds: float = 0.0


@dataclass
class Cue:
    index: int
    start_frame: int
    end_frame: int
    lines: list[str]

    @property
    def duration_seconds(self) -> float:
        return (self.end_frame - self.start_frame) / FPS

    @property
    def text(self) -> str:
        return " ".join(self.lines)


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    return re.sub(r"\s+", " ", value).strip()


def can_wrap(words: list[str]) -> tuple[bool, list[str]]:
    if not words:
        return False, []
    joined = " ".join(words)
    if len(joined) > MAX_CUE_CHARS:
        return False, []
    if len(joined) <= MAX_LINE_CHARS:
        return True, [joined]

    candidates: list[tuple[float, list[str]]] = []
    for split in range(1, len(words)):
        left = " ".join(words[:split])
        right = " ".join(words[split:])
        if len(left) > MAX_LINE_CHARS or len(right) > MAX_LINE_CHARS:
            continue
        balance = abs(len(left) - len(right))
        punctuation_bonus = -8 if words[split - 1].endswith(BREAK_PUNCTUATION) else 0
        orphan_penalty = 12 if len(words[:split]) == 1 or len(words[split:]) == 1 else 0
        score = balance + punctuation_bonus + orphan_penalty
        candidates.append((score, [left, right]))
    if not candidates:
        return False, []
    candidates.sort(key=lambda item: item[0])
    return True, candidates[0][1]


def split_into_cues(text: str) -> list[str]:
    words = normalize_text(text).split()
    cues: list[str] = []
    current: list[str] = []

    for word in words:
        candidate = current + [word]
        fits, _ = can_wrap(candidate)
        if fits:
            current = candidate
            continue
        if not current:
            raise ValueError(f"Single token cannot fit subtitle line: {word}")

        preferred_break = None
        if len(current) >= 5:
            for position in range(len(current) - 1, max(1, len(current) - 5), -1):
                if current[position - 1].endswith(BREAK_PUNCTUATION):
                    prefix = current[:position]
                    suffix = current[position:] + [word]
                    prefix_fits, _ = can_wrap(prefix)
                    suffix_fits, _ = can_wrap(suffix)
                    if prefix_fits and suffix_fits:
                        preferred_break = (prefix, suffix)
                        break
        if preferred_break:
            prefix, current = preferred_break
            cues.append(" ".join(prefix))
        else:
            cues.append(" ".join(current))
            current = [word]

    if current:
        cues.append(" ".join(current))

    index = 1
    while index < len(cues):
        current_words = cues[index].split()
        if len(cues[index]) >= 18 and len(current_words) >= 3:
            index += 1
            continue
        previous_words = cues[index - 1].split()
        combined = previous_words + current_words
        combined_fits, _ = can_wrap(combined)
        if combined_fits:
            cues[index - 1] = " ".join(combined)
            del cues[index]
            continue

        moved = False
        while len(" ".join(current_words)) < 18 or len(current_words) < 3:
            if len(previous_words) <= 3:
                break
            current_words.insert(0, previous_words.pop())
            previous_fits, _ = can_wrap(previous_words)
            current_fits, _ = can_wrap(current_words)
            if previous_fits and current_fits:
                moved = True
            else:
                previous_words.append(current_words.pop(0))
                break
        if moved:
            cues[index - 1] = " ".join(previous_words)
            cues[index] = " ".join(current_words)
        index += 1
    return cues


def section_cue_drafts(text_with_markers: str) -> list[CueDraft]:
    drafts: list[CueDraft] = []
    text_with_markers = EMPHASIS_RE.sub("", text_with_markers)
    cursor = 0
    for match in PAUSE_RE.finditer(text_with_markers):
        segment = text_with_markers[cursor : match.start()]
        for cue_text in split_into_cues(segment):
            drafts.append(CueDraft(cue_text))
        if not drafts:
            raise ValueError("Pause marker appears before any spoken text")
        drafts[-1].pause_after_seconds += float(match.group("seconds"))
        cursor = match.end()
    trailing = text_with_markers[cursor:]
    for cue_text in split_into_cues(trailing):
        drafts.append(CueDraft(cue_text))
    return drafts


def allocate_frames(weights: list[int], total_frames: int) -> list[int]:
    if total_frames < len(weights):
        raise ValueError("Not enough frames for subtitle cues")
    total_weight = sum(weights)
    exact = [weight * total_frames / total_weight for weight in weights]
    allocated = [max(1, int(value)) for value in exact]
    difference = total_frames - sum(allocated)
    if difference > 0:
        order = sorted(
            range(len(weights)),
            key=lambda index: exact[index] - int(exact[index]),
            reverse=True,
        )
        for offset in range(difference):
            allocated[order[offset % len(order)]] += 1
    elif difference < 0:
        order = sorted(
            range(len(weights)),
            key=lambda index: (allocated[index], exact[index] - int(exact[index])),
            reverse=True,
        )
        remaining = -difference
        for index in order:
            removable = min(remaining, allocated[index] - 1)
            allocated[index] -= removable
            remaining -= removable
            if remaining == 0:
                break
        if remaining:
            raise ValueError("Could not normalize allocated subtitle frames")
    if sum(allocated) != total_frames:
        raise AssertionError("Subtitle frame allocation failed")
    return allocated


def build_cues(source: Path) -> tuple[list[Cue], str]:
    sections = parse_sections(source)
    cues: list[Cue] = []

    for section in sections:
        drafts = section_cue_drafts(section.text_with_markers)
        section_start_frame = section.start_seconds * FPS
        voice_end_frame = round(
            (section.start_seconds + section.target_duration_seconds * VOICE_FILL_RATIO) * FPS
        )
        gap_total_frames = GAP_FRAMES * max(0, len(drafts) - 1)
        pause_frames = [round(draft.pause_after_seconds * FPS) for draft in drafts]
        speech_total_frames = voice_end_frame - section_start_frame - gap_total_frames - sum(pause_frames)
        weights = [max(1, len(normalize_text(draft.text))) for draft in drafts]
        durations = allocate_frames(weights, speech_total_frames)

        cursor = section_start_frame
        for draft, duration, pause_after_frames in zip(drafts, durations, pause_frames):
            fits, lines = can_wrap(draft.text.split())
            if not fits:
                raise ValueError(f"Cue cannot be wrapped: {draft.text}")
            end_frame = cursor + duration
            cues.append(
                Cue(
                    index=len(cues) + 1,
                    start_frame=cursor,
                    end_frame=end_frame,
                    lines=lines,
                )
            )
            cursor = end_frame + GAP_FRAMES + pause_after_frames

        expected_cursor = voice_end_frame + (GAP_FRAMES if drafts else 0)
        if cursor != expected_cursor:
            raise AssertionError(
                f"Subtitle allocation mismatch in section {section.index}: "
                f"{cursor} != {expected_cursor}"
            )

    return cues, normalize_text(" ".join(section.clean_text for section in sections))


def format_srt_time(frame: int) -> str:
    milliseconds = round(frame * 1000 / FPS)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def write_srt(cues: list[Cue], output: Path) -> None:
    blocks: list[str] = []
    for cue in cues:
        cue_text = "\n".join(cue.lines)
        blocks.append(
            f"{cue.index}\n"
            f"{format_srt_time(cue.start_frame)} --> {format_srt_time(cue.end_frame)}\n"
            f"{cue_text}"
        )
    output.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def audit(cues: list[Cue], expected_text: str, source: Path, output: Path) -> None:
    errors: list[str] = []
    warnings: list[str] = []
    actual_text = normalize_text(" ".join(cue.text for cue in cues))
    if actual_text != expected_text:
        errors.append("Subtitle transcript differs from narration after whitespace normalization.")
    for expected_index, cue in enumerate(cues, start=1):
        if cue.index != expected_index:
            errors.append(f"Non-sequential cue index at {cue.index}.")
        if cue.start_frame >= cue.end_frame:
            errors.append(f"Non-positive duration at cue {cue.index}.")
        if len(cue.lines) > MAX_CUE_LINES:
            errors.append(f"More than two lines at cue {cue.index}.")
        for line in cue.lines:
            if len(line) > MAX_LINE_CHARS:
                errors.append(f"Line longer than {MAX_LINE_CHARS} characters at cue {cue.index}.")
        if cue.duration_seconds < 1.0:
            warnings.append(f"Cue {cue.index} is shorter than 1.0 second.")
        characters_per_second = len(cue.text) / cue.duration_seconds
        if characters_per_second > 25:
            warnings.append(
                f"Cue {cue.index} reads at {characters_per_second:.1f} characters/second."
            )
    for previous, current in zip(cues, cues[1:]):
        if current.start_frame <= previous.end_frame:
            errors.append(f"Cue overlap or missing frame gap: {previous.index}->{current.index}.")

    nfc_errors = [cue.index for cue in cues if unicodedata.normalize("NFC", cue.text) != cue.text]
    if nfc_errors:
        errors.append(f"Non-NFC Unicode in cues: {nfc_errors}")

    required_terms = [
        "Andrew Feenberg",
        "thuyết công cụ",
        "thuyết tất định công nghệ",
        "thuyết thực chất",
        "lý thuyết phê phán công nghệ",
        "mã kỹ thuật",
        "meta-choice",
        "subversive rationalization",
        "democratic rationalization",
        "Teletel",
        "Prodigy",
        "amyotrophic lateral sclerosis",
        "Amyotrophic Lateral Sclerosis Society of America",
    ]
    missing_terms = [term for term in required_terms if term not in actual_text]
    if missing_terms:
        errors.append("Missing required terms: " + "; ".join(missing_terms))

    shortest = min(cue.duration_seconds for cue in cues)
    longest = max(cue.duration_seconds for cue in cues)
    fastest = max(len(cue.text) / cue.duration_seconds for cue in cues)
    last_end = cues[-1].end_frame / FPS
    status = "PASS" if not errors else "FAIL"

    report = f"""SUBTITLE QA REPORT
Ngày tạo: 03/09/2026
Nguồn lời: {source.name}, phiên bản 2.1
File kiểm: 05_subtitles.srt

======================================================================
I. KẾT QUẢ CẤU TRÚC
======================================================================

SUBTITLE STRUCTURAL QA: {status}
FINAL VOICE-TO-SUBTITLE SYNC QA: PENDING

Số cue: {len(cues)}
Cue đầu: {format_srt_time(cues[0].start_frame)}
Cue cuối kết thúc: {format_srt_time(cues[-1].end_frame)}
Khoảng duration cue: {shortest:.3f}s–{longest:.3f}s
Tốc độ đọc cao nhất: {fastest:.1f} ký tự/giây
Giới hạn dòng: tối đa {MAX_CUE_LINES} dòng, tối đa {MAX_LINE_CHARS} ký tự/dòng
Giới hạn nội dung cue: tối đa {MAX_CUE_CHARS} ký tự
Transcript khớp narration sau chuẩn hóa khoảng trắng: {'PASS' if actual_text == expected_text else 'FAIL'}
Unicode NFC: {'PASS' if not nfc_errors else 'FAIL'}
Index liên tục, timestamp tăng và không overlap: {'PASS' if not any('overlap' in error.lower() or 'index' in error.lower() for error in errors) else 'FAIL'}

======================================================================
II. LỖI
======================================================================

"""
    report += "Không phát hiện lỗi cấu trúc.\n" if not errors else "\n".join(f"- {error}" for error in errors) + "\n"
    report += """

======================================================================
III. CẢNH BÁO MẬT ĐỘ
======================================================================

"""
    report += "Không có cảnh báo mật độ tự động.\n" if not warnings else "\n".join(f"- {warning}" for warning in warnings) + "\n"
    report += f"""

======================================================================
IV. KIỂM THUẬT NGỮ
======================================================================

Các thuật ngữ/tên riêng bắt buộc đều hiện đúng trong transcript: {'PASS' if not missing_terms else 'FAIL'}.
Phụ đề được lấy trực tiếp từ lời thoại; không rút gọn, diễn giải lại hoặc thay từ học thuật.

======================================================================
V. VIỆC CÒN PHẢI LÀM VỚI VOICE FINAL
======================================================================

Timing phải được canh theo waveform của voice final đã khóa. Khi tái tạo subtitle, phải:

1. canh lại từng cue theo waveform/word timing của voice final;
2. đối chiếu từng từ giữa voice final, narration và SRT;
3. xem burn-in ở 100% trên nền sáng/tối;
4. kiểm không che nhãn bằng chứng và citation;
5. cập nhật dòng FINAL VOICE-TO-SUBTITLE SYNC QA thành PASS chỉ sau khi xem toàn bộ video.

Thời điểm lời kết thúc: {last_end:.3f}s. Credit 14:19–15:17 không có lời và không có cue thoại.
"""
    output.write_text(report, encoding="utf-8")
    if errors:
        raise SystemExit("Subtitle QA failed:\n" + "\n".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    cues, expected_text = build_cues(args.source.resolve())
    write_srt(cues, args.srt.resolve())
    audit(cues, expected_text, args.source.resolve(), args.report.resolve())
    print(f"Created {len(cues)} subtitle cues with structural QA PASS.")


if __name__ == "__main__":
    main()
