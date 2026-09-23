#!/usr/bin/env python3
"""Bind each editorial scene to an exact phrase in the locked voice transcript.

Unlike proportional chapter retiming, this keeps argument, source cards and
illustrations synchronized. Existing planning rows are archived before update.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

from build_aligned_subtitles import align_words, normalized_word, transcript_words, whisper_words
from final_visual_plan import SCENE_ASSETS

PHRASES = [
    "Người bệnh chạm", "Một giây sau", "Nhưng trước đó", "Nút bấm trông", "Kính chào thầy",
    "Tình huống vừa rồi", "Nó giúp phân biệt", "Thứ nhất là sử dụng", "Thứ hai là thiết kế", "Thứ ba là quản trị",
    "Ba tầng liên quan", "Được dùng ứng dụng", "Giả sử hệ thống", "Mâu thuẫn triết học",
    "Cách nhìn đầu tiên", "Trong What Is Philosophy", "Cách nhìn này nhắc", "Feenberg định vị tranh luận",
    "Trục thứ nhất hỏi", "Trục thứ hai hỏi", "Trung tính kết hợp với con người", "Trung tính kết hợp với tự trị",
    "Mang giá trị kết hợp", "Giao điểm cuối", "công nghệ mang giá trị nhưng vẫn", "Feenberg không xem", "Khoảng căng ấy",
    "Theo Feenberg hệ thống", "nó phân phối khả năng", "Phương tiện và mục đích", "Feenberg gọi đây là meta-choice",
    "Ta không chỉ hỏi", "Lý thuyết phê phán giữ", "Trong bài năm 1992", "Có thể tồn tại nhiều",
    "Đó là tính bất định", "Vật liệu quy luật", "Theo cách hiểu phi bản chất luận",
    "Khái niệm tiếp theo", "Mã kỹ thuật không phải", "Trong bài Subversive Rationalization",
    "Điều được coi là bình thường", "Feenberg minh họa bằng", "Ban đầu an toàn", "Khi quy chuẩn ổn định",
    "Điểm triết học", "Khi quá trình hoàn tất", "Trong From Essentialism", "Giá trị có thể trở thành",
    "Các giá trị không", "Nhóm ngoài mạng lưới", "Feenberg bác lựa chọn",
    "Vậy dân chủ hóa", "Feenberg nói rõ", "Ta cũng không được", "Trong bài năm 1992",
    "Từ kinh nghiệm dưới", "Feenberg gọi hướng đi", "Theo diễn giải của Nhóm 14",
    "Sự tham gia phải", "hoặc hội thảo không", "Dân chủ hóa không phủ nhận", "Câu hỏi là ai tham gia",
    "Hãy theo dõi", "Trước hết là dữ kiện", "kỹ sư hình dung chủ yếu", "Người dùng sớm chiếm dụng",
    "Đây không chỉ là dùng", "rồi làm đổi cả định nghĩa", "Giao tiếp trở thành chức năng",
    "Tiếp theo là nhóm hỗ trợ", "Năm 1995", "Họ không chỉ trao đổi", "Feenberg nhận xét",
    "Nguồn ghi nhận", "và trình cho Amyotrophic", "Giới hạn bằng chứng",
    "Bây giờ là phân tích", "Không nên lãng mạn hóa",
    "Trở lại hệ thống phân lịch", "Theo thuyết công cụ", "Lý thuyết phê phán mở rộng",
    "Một ai định nghĩa", "Hai giá trị nào", "Ba ai chịu tác động", "Bốn sự tham gia", "Năm phản hồi",
    "Cần theo dõi tác động", "Nhóm 14 đề xuất", "Chuyên môn vẫn thiết yếu",
    "Ta trở lại câu hỏi", "Theo Feenberg không thể", "Nhưng công nghệ cũng", "Bài học phương pháp luận", "Dân chủ hóa không chỉ là mở",
]


def stamp(frame: int) -> str:
    milliseconds = round(frame * 1000 / 30)
    h, rest = divmod(milliseconds, 3600000)
    m, rest = divmod(rest, 60000)
    s, ms = divmod(rest, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    text = (root / "audio/vo/narration_spoken.txt").read_text()
    words = transcript_words(text)
    observed = whisper_words(json.loads((root / "qa/whisper/chatgpt_170wpm.json").read_text()))
    aligned = align_words(words, observed, 858.051271)
    normalized = [normalized_word(w) for w in words]
    cursor = 0
    word_starts = []
    for sid, phrase in enumerate(PHRASES, 1):
        tokens = [normalized_word(w) for w in phrase.split()]
        matches = [i for i in range(cursor, len(words) - len(tokens) + 1) if normalized[i:i + len(tokens)] == tokens]
        if not matches:
            raise ValueError(f"S{sid:03d} phrase not found after word {cursor}: {phrase}")
        cursor = matches[0]
        word_starts.append(cursor)
        cursor += 1
    if len(word_starts) != 95:
        raise AssertionError("Expected exactly 95 voiced scenes")
    # Cut no more than one frame ahead of the voice anchor. Keep all scene and
    # shot boundaries on real 30fps frames; never accumulate rounding drift.
    frames = [max(0, round(aligned[i].start * 30) - 1) for i in word_starts]
    frames[0] = 0
    frames.extend([859 * 30, 867 * 30, 876 * 30, 895 * 30, 911 * 30, 917 * 30])
    with (root / "02_storyboard.csv").open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    records = []
    for index, row in enumerate(rows):
        start, end = frames[index:index + 2]
        if end - start < 20:
            raise ValueError(f"Scene too short: {row['SCENE_ID']}: {(end-start)/30:.3f}s")
        sid = row["SCENE_ID"]
        row.update(START_TIME=stamp(start), END_TIME=stamp(end), DURATION=f"{(end-start)/30:.6f}")
        if index < 95:
            until = word_starts[index + 1] if index < 94 else len(words)
            row["NARRATION"] = " ".join(words[word_starts[index]:until])
        else:
            row["NARRATION"] = "Không lời — nhạc kết và credit."
        row["ASSET_STATUS"] = "RENDERED_SELECTED; " + "; ".join(SCENE_ASSETS[sid])
        records.append({"scene": sid, "start_frame": start, "end_frame": end, "anchor": PHRASES[index] if index < 95 else "credits", "assets": SCENE_ASSETS[sid]})
        print(f"{sid} {row['START_TIME']}–{row['END_TIME']} {row['DURATION']}s | {row['NARRATION'][:100]}")
    exact = " ".join(r["NARRATION"] for r in rows[:95])
    if exact != " ".join(words):
        raise AssertionError("Scene narration must reconstruct the entire transcript exactly")
    if not args.apply:
        return
    archive = root / "archive/pre_speech_alignment_20260906"
    archive.mkdir(parents=True, exist_ok=True)
    if not (archive / "02_storyboard.csv").exists():
        shutil.copy2(root / "02_storyboard.csv", archive / "02_storyboard.csv")
    with (root / "02_storyboard.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (root / "qa/final_917/picture_speech_alignment.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
