#!/usr/bin/env python3
"""Synchronize the Group 14 script DOCX with the locked V11 R5 film.

The existing DOCX is the formatting authority. This script edits text in place,
reuses the existing table rows/cells/paragraphs/runs, and removes only the four
obsolete credit rows S097-S100 after converting S096 to the single V11 credit
artifact row.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
DOCX_PATH = ROOT / "KICH_BAN_CHI_TIET_FEENBERG_NHOM_14.docx"
STORYBOARD_PATH = ROOT / "qa/v11/02_storyboard_v11.csv"
PICTURE_MANIFEST_PATH = ROOT / "qa/v11/picture_r5/manifest.json"

DELIVERY_FILE = "Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4"
DELIVERY_SHA256 = "8b7e88a4bf2849369bc4f8bf25e721afba332a201b8e8da588a3720bacd39102"


CHAPTERS = [
    ("MỞ HỘP ĐEN", 1, 5),
    ("MỘT NÚT BẤM KHÔNG CHỈ LÀ MỘT NÚT BẤM", 6, 14),
    ("HAI CÁCH NHÌN VÀ BẢN ĐỒ BỐN LẬP TRƯỜNG", 15, 27),
    ("TỪ CÔNG DỤNG ĐẾN LỰA CHỌN Ở CẤP KHUNG", 28, 38),
    ("MÃ KỸ THUẬT KHI GIÁ TRỊ ĐÔNG LẠI TRONG THIẾT KẾ", 39, 52),
    ("DÂN CHỦ HÓA KHÔNG PHẢI MỘT NÚT BÌNH CHỌN", 53, 63),
    ("KHI NGƯỜI DÙNG VIẾT LẠI Ý NGHĨA CỦA MẠNG", 64, 79),
    ("VẬN DỤNG VÀO QUẢN TRỊ HỆ THỐNG SỐ", 80, 90),
    ("KẾT LUẬN VÀ CẢM ƠN", 91, 95),
]


CHAPTER_TIMING_PARAGRAPHS = {
    109: (1, 5),
    125: (6, 14),
    143: (15, 27),
    163: (28, 38),
    183: (39, 52),
    203: (53, 63),
    222: (64, 79),
    247: (80, 90),
    269: (91, 95),
}


def map_r5_path(value: str) -> str:
    return value.replace("assets/v11_graphics/", "assets/v11_graphics_r5/")


def clean_production_text(value: str) -> str:
    """Correct two inherited storyboard typos without changing meaning."""
    return (
        value.replace("Push nhẹ pushdolly 3 cm", "Push-in nhẹ 3 cm")
        .replace("50dolly 50 mm, eye-level", "50 mm, eye-level")
    )


def display_time(value: str) -> str:
    """Convert HH:MM:SS.mmm to MM:SS.mmm for this sub-hour film."""
    if value.startswith("00:"):
        return value[3:]
    return value


def set_paragraph_text(paragraph, value: str) -> None:
    """Replace text while preserving the paragraph and first-run formatting."""
    if not paragraph.runs:
        paragraph.add_run(value)
        return
    paragraph.runs[0].text = value
    for run in paragraph.runs[1:]:
        run.text = ""


def set_paragraph_runs(paragraph, values: list[str]) -> None:
    if len(paragraph.runs) < len(values):
        raise AssertionError(
            f"Paragraph does not have enough preserved runs: {paragraph.text!r}"
        )
    for index, value in enumerate(values):
        paragraph.runs[index].text = value
    for run in paragraph.runs[len(values) :]:
        run.text = ""


def set_plain_cell(cell, value: str) -> None:
    if len(cell.paragraphs) != 1:
        raise AssertionError(f"Expected one paragraph in plain cell, got {len(cell.paragraphs)}")
    set_paragraph_text(cell.paragraphs[0], value)


def set_structured_cell(cell, first_line: str, fields: list[tuple[str, str]]) -> None:
    expected = 1 + len(fields)
    if len(cell.paragraphs) != expected:
        raise AssertionError(
            f"Expected {expected} paragraphs, got {len(cell.paragraphs)} in {cell.text!r}"
        )
    set_paragraph_text(cell.paragraphs[0], first_line)
    for paragraph, (label, value) in zip(cell.paragraphs[1:], fields):
        set_paragraph_runs(paragraph, [label, value])


def set_labeled_cell(cell, fields: list[tuple[str, str]]) -> None:
    if len(cell.paragraphs) != len(fields):
        raise AssertionError(
            f"Expected {len(fields)} paragraphs, got {len(cell.paragraphs)} in {cell.text!r}"
        )
    for paragraph, (label, value) in zip(cell.paragraphs, fields):
        set_paragraph_runs(paragraph, [label, value])


def build_as_built_shot_text(scene_id: str, shots_by_scene: dict[str, list[dict]]) -> str:
    parts = []
    for shot in shots_by_scene[scene_id]:
        asset = map_r5_path(shot["relative_asset"])
        parts.append(
            f"{scene_id}_{shot['shot_index']:02d} · nguồn "
            f"{shot['source_start']:.3f}–{shot['source_end']:.3f} giây · "
            f"timeline {shot['duration_seconds']:.3f} giây · {asset}"
        )
    return " | ".join(parts)


def normalize_as_built_sound(value: str) -> str:
    return value.replace("VO ChatGPT", "Một master Vale")


def ensure_update_fields(document: Document) -> None:
    settings = document.settings.element
    update_fields = settings.find(qn("w:updateFields"))
    if update_fields is None:
        update_fields = OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set(qn("w:val"), "true")


def flatten_pdf_outline(reader, items) -> list[tuple[str, int]]:
    flattened: list[tuple[str, int]] = []
    for item in items:
        if isinstance(item, list):
            flattened.extend(flatten_pdf_outline(reader, item))
            continue
        flattened.append((item.title, reader.get_destination_page_number(item) + 1))
    return flattened


def update_toc_cache_from_pdf(document: Document, pdf_path: Path) -> None:
    """Update cached TOC page results from the verified rendered PDF outline."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    outline = flatten_pdf_outline(reader, reader.outline)
    toc_paragraphs = [
        paragraph
        for paragraph in document.paragraphs
        if paragraph.style and paragraph.style.name.lower().startswith("toc ")
    ]
    if len(toc_paragraphs) != 69 or len(outline) != 69:
        raise AssertionError(
            f"Expected 69 TOC entries and PDF outline items, got {len(toc_paragraphs)} and {len(outline)}"
        )

    # The first three physical PDF pages are the cover and two TOC pages;
    # printed body page 1 starts on physical PDF page 4.
    for paragraph, (title, physical_page) in zip(toc_paragraphs, outline):
        cached_title = paragraph.text.rsplit("\t", 1)[0]
        if cached_title != title:
            raise AssertionError(f"TOC/PDF outline mismatch: {cached_title!r} != {title!r}")
        text_nodes = paragraph._p.findall(".//" + qn("w:t"))
        if not text_nodes or not (text_nodes[-1].text or "").isdigit():
            raise AssertionError(f"TOC entry has no cached numeric result: {paragraph.text!r}")
        text_nodes[-1].text = str(physical_page - 3)


def fix_known_doc_text_issues(document: Document) -> None:
    replacements = {
        "Push nhẹ pushdolly 3 cm": "Push-in nhẹ 3 cm",
        "50dolly 50 mm, eye-level": "50 mm, eye-level",
    }
    replaced = set()
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for old, new in replacements.items():
                        if old not in paragraph.text:
                            continue
                        for run in paragraph.runs:
                            if old in run.text:
                                run.text = run.text.replace(old, new)
                                replaced.add(old)
    if replaced != set(replacements):
        missing = set(replacements) - replaced
        raise AssertionError(f"Did not find expected inherited text issue(s): {sorted(missing)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--toc-pdf",
        type=Path,
        help="Only refresh cached TOC page numbers from the already verified rendered PDF.",
    )
    args = parser.parse_args()

    if args.toc_pdf:
        document = Document(str(DOCX_PATH))
        update_toc_cache_from_pdf(document, args.toc_pdf)
        fix_known_doc_text_issues(document)
        ensure_update_fields(document)
        temp_path = DOCX_PATH.with_name(DOCX_PATH.stem + ".toc.tmp.docx")
        document.save(str(temp_path))
        os.replace(temp_path, DOCX_PATH)
        return

    with STORYBOARD_PATH.open(encoding="utf-8-sig", newline="") as handle:
        storyboard = list(csv.DictReader(handle))
    if len(storyboard) != 96:
        raise AssertionError(f"Expected 95 content scenes + credit, got {len(storyboard)}")

    content_rows = storyboard[:95]
    credit_row = storyboard[95]
    if [row["SCENE_ID"] for row in content_rows] != [f"S{i:03d}" for i in range(1, 96)]:
        raise AssertionError("Storyboard content scene IDs are not S001-S095 in order")
    if credit_row["SCENE_ID"] != "CREDIT_V11":
        raise AssertionError("Storyboard credit row is not CREDIT_V11")

    with PICTURE_MANIFEST_PATH.open(encoding="utf-8") as handle:
        picture_manifest = json.load(handle)
    if picture_manifest["scene_count"] != 95 or picture_manifest["shot_count"] != 172:
        raise AssertionError("Unexpected V11 R5 picture manifest dimensions")

    shots_by_scene: dict[str, list[dict]] = defaultdict(list)
    for shot in picture_manifest["shots"]:
        shots_by_scene[shot["scene_id"]].append(shot)
    if set(shots_by_scene) != {f"S{i:03d}" for i in range(1, 96)}:
        raise AssertionError("Picture manifest does not cover exactly S001-S095")

    document = Document(str(DOCX_PATH))
    if len(document.tables) != 18 or len(document.paragraphs) != 338:
        raise AssertionError("DOCX structure differs from the preserved 18-table/338-paragraph template")

    # I. Information and scope.
    info_table = document.tables[1]
    set_plain_cell(info_table.cell(6, 1), "00:16:58.367")
    set_plain_cell(
        info_table.cell(7, 1),
        "V11 R5 · 95 cảnh nội dung · 172 shot · 130 asset riêng · "
        "267 câu phụ đề · credit V4 dài 54,1 giây",
    )

    # III. Argument structure and current chapter timeline.
    scene_by_id = {row["SCENE_ID"]: row for row in content_rows}
    structure_table = document.tables[3]
    if len(structure_table.rows) != 11:
        raise AssertionError("Expected ten chapter rows plus header")
    for table_row, (title, start_scene, end_scene) in zip(structure_table.rows[1:10], CHAPTERS):
        start_id = f"S{start_scene:03d}"
        end_id = f"S{end_scene:03d}"
        start_time = display_time(scene_by_id[start_id]["START_TIME"])
        end_time = display_time(scene_by_id[end_id]["END_TIME"])
        set_paragraph_runs(
            table_row.cells[0].paragraphs[0],
            [f"{start_time} đến {end_time}", f"\n{start_id} đến {end_id}"],
        )
        set_plain_cell(table_row.cells[1], title)

    credit_structure_row = structure_table.rows[10]
    set_paragraph_runs(
        credit_structure_row.cells[0].paragraphs[0],
        ["16:05.066 đến 16:58.367", "\nCREDIT_V11"],
    )
    set_plain_cell(credit_structure_row.cells[1], "END CREDITS V4")
    set_plain_cell(
        credit_structure_row.cells[2],
        "Hiển thị credit V4 bo góc của môn học, lớp, giảng viên, bảy thành viên "
        "với nhãn MSHV và lời cảm ơn; artifact dài 54,1 giây, nối bằng crossfade 0,8 giây.",
    )
    set_plain_cell(
        credit_structure_row.cells[3],
        "Không lời; nhạc Oh Yeah tích hợp trong artifact credit V4.",
    )

    # IV. Scene-by-scene script. Reuse every existing formatted row.
    scene_table_rows = []
    for table_index in range(4, 13):
        scene_table_rows.extend(document.tables[table_index].rows[1:])
    if len(scene_table_rows) != 95:
        raise AssertionError(f"Expected 95 formatted scene rows, got {len(scene_table_rows)}")

    for table_row, scene in zip(scene_table_rows, content_rows):
        scene_id = scene["SCENE_ID"]
        source = map_r5_path(scene["SOURCE"])
        visual_description = map_r5_path(scene["VISUAL_DESCRIPTION"])
        as_built_shots = build_as_built_shot_text(scene_id, shots_by_scene)
        as_built_sound = normalize_as_built_sound(scene["AS_BUILT_SOUND"])

        set_structured_cell(
            table_row.cells[0],
            scene_id,
            [
                ("Thời gian: ", f"{display_time(scene['START_TIME'])} đến {display_time(scene['END_TIME'])}"),
                ("Thời lượng: ", f"{float(scene['DURATION']):.3f} giây"),
                ("Loại hình: ", scene["VISUAL_TYPE"]),
                ("Nguồn: ", source),
            ],
        )
        set_labeled_cell(
            table_row.cells[1],
            [
                ("Hình ảnh: ", visual_description),
                ("Máy quay: ", scene["CAMERA"]),
                ("Ống kính và góc nhìn: ", clean_production_text(scene["LENS_PERSPECTIVE"])),
                ("Chuyển động: ", clean_production_text(scene["MOVEMENT"])),
                ("Ánh sáng: ", scene["LIGHTING"]),
                ("Bố cục: ", scene["COMPOSITION"]),
            ],
        )
        set_labeled_cell(
            table_row.cells[2],
            [
                ("Lời thoại: ", scene["NARRATION"]),
                ("Chữ trên màn hình: ", scene["ON_SCREEN_TEXT"]),
            ],
        )
        set_labeled_cell(
            table_row.cells[3],
            [
                ("Âm thanh: ", scene["SOUND"]),
                ("Chuyển cảnh: ", scene["TRANSITION"]),
                ("Mục đích: ", scene["VISUAL_ARGUMENT_LINK"] or scene["PURPOSE"]),
                ("Asset: ", f"V11 R5 LOCKED; {source}"),
                ("Shot thực dùng: ", as_built_shots),
                ("Âm thanh thực dùng: ", as_built_sound),
            ],
        )

    # Replace the five obsolete V8 credit scene rows with one locked V11 credit row.
    credit_table = document.tables[13]
    if len(credit_table.rows) != 6:
        raise AssertionError("Expected header plus five obsolete credit rows")
    credit_target = credit_table.rows[1]
    set_structured_cell(
        credit_target.cells[0],
        "CREDIT_V11",
        [
            ("Thời gian: ", "16:05.066 đến 16:58.367"),
            ("Thời lượng: ", "54.100 giây; crossfade 0.800 giây"),
            ("Loại hình: ", "C — END CREDIT V4"),
            ("Nguồn: ", "CREDIT_TPHCM_OH_YEAH_V4.mp4"),
        ],
    )
    set_labeled_cell(
        credit_target.cells[1],
        [
            ("Hình ảnh: ", credit_row["VISUAL_DESCRIPTION"]),
            ("Máy quay: ", credit_row["CAMERA"]),
            ("Ống kính và góc nhìn: ", credit_row["LENS_PERSPECTIVE"]),
            ("Chuyển động: ", credit_row["MOVEMENT"]),
            ("Ánh sáng: ", credit_row["LIGHTING"]),
            ("Bố cục: ", credit_row["COMPOSITION"]),
        ],
    )
    set_labeled_cell(
        credit_target.cells[2],
        [
            ("Lời thoại: ", credit_row["NARRATION"]),
            ("Chữ trên màn hình: ", credit_row["ON_SCREEN_TEXT"]),
        ],
    )
    set_labeled_cell(
        credit_target.cells[3],
        [
            ("Âm thanh: ", credit_row["SOUND"]),
            ("Chuyển cảnh: ", credit_row["TRANSITION"]),
            ("Mục đích: ", credit_row["PURPOSE"]),
            ("Asset: ", credit_row["ASSET_STATUS"]),
            ("Shot thực dùng: ", credit_row["AS_BUILT_SHOTS"]),
            ("Âm thanh thực dùng: ", credit_row["AS_BUILT_SOUND"]),
        ],
    )
    for obsolete_row in list(credit_table.rows[2:]):
        credit_table._tbl.remove(obsolete_row._tr)

    # V. Audio and subtitle details for the locked delivery.
    audio_table = document.tables[14]
    audio_values = {
        1: (
            "Một giọng Vale duy nhất; master: "
            "audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav; "
            "ưu tiên lời nói, không đổi giọng giữa các chương và không có tiếng đệm."
        ),
        2: (
            "Nội dung chính dùng audio/music/SCORE_SUNO_V8_48K.wav và duck dưới lời. "
            "Credit V4 dùng nhạc Oh Yeah tích hợp riêng; crossfade 0,8 giây tại điểm nối."
        ),
        3: (
            "Ambience/SFX theo audio/sfx/SFX_AMBIENCE_V10_48K.wav; cue thưa, có nguyên nhân hình ảnh; "
            "không lấn giọng và không có tiếng lật trang ở credit."
        ),
        4: "audio/mix/FULL_MIX_V10_CONTENT_48K.wav; 48 kHz stereo cho phần nội dung, nối audio credit V4 ở master cuối.",
        5: "Khoảng -15,8 LUFS integrated; true peak khoảng -2,0 dBFS ở bản giao V11.",
        6: (
            "qa/v9/05_subtitles_v9.srt gồm 267 cue; Unicode tiếng Việt; tối đa hai dòng; "
            "không overlap; cỡ burn-in 42 px; bám đúng transcript Vale đã khóa."
        ),
        7: (
            "Nếu đổi lời thoại hoặc timeline phải retime phụ đề, storyboard, nhạc, SFX, "
            "crossfade credit và tổng thời lượng; bản hiện hành là V11 R5 đã khóa."
        ),
    }
    for row_index, value in audio_values.items():
        set_plain_cell(audio_table.cell(row_index, 1), value)

    # VII. Group review table terminology.
    set_plain_cell(document.tables[16].cell(0, 2), "MSHV")

    # Top-level prose: update only text whose underlying production state changed.
    paragraph_updates = {
        81: (
            "Bản khóa V11 R5 dài 16 phút 58,367 giây, gồm 95 cảnh nội dung và credit V4 "
            "dài 54,1 giây, nối bằng crossfade 0,8 giây. File giao nộp hiện hành là "
            f"{DELIVERY_FILE}; SHA-256: {DELIVERY_SHA256}."
        ),
        85: "• Đối chiếu từng cảnh với video theo mã S001 đến S095; phần credit dùng mã CREDIT_V11.",
        288: "Thời gian: 16:05.066 đến 16:58.367 (credit V4 dài 54,1 giây; crossfade 0,8 giây)",
        289: "Phân loại nội dung: [KHÔNG LỜI; CREDIT V4 BO GÓC; NHẠC OH YEAH; CROSSFADE 0,8 GIÂY]",
        291: "Hiển thị credit V4 của môn học, lớp, giảng viên, bảy thành viên với nhãn MSHV và lời cảm ơn trong phần nhạc kết.",
        297: "• Đủ thời gian đọc thông tin lớp, giảng viên, bảy thành viên và MSHV.",
        299: "• Nhạc Oh Yeah trong credit hạ tự nhiên về im lặng và hình kết không bị cắt đột ngột.",
        302: (
            "Toàn phim dùng một giọng Vale duy nhất. Master lời đọc là "
            "audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav. "
            "Đây là cùng một master Vale, có các khoảng nghỉ hình và nhạc được chèn có chủ đích; "
            "giọng giữ chất sáng, rõ, mạch lạc, không có tiếng đệm, không ghép sang giọng khác "
            "và không kéo giãn thời gian đến mức biến dạng."
        ),
        304: (
            "Phần nội dung dùng audio/music/SCORE_SUNO_V8_48K.wav và "
            "audio/sfx/SFX_AMBIENCE_V10_48K.wav, được duck dưới lời thoại. Credit V4 dùng audio "
            "Oh Yeah tích hợp riêng; hai phần nối bằng crossfade 0,8 giây. SFX chỉ dùng khi có "
            "nguyên nhân hình ảnh rõ; cuối phim không có tiếng lật trang."
        ),
    }
    for paragraph_index, value in paragraph_updates.items():
        set_paragraph_text(document.paragraphs[paragraph_index], value)

    for paragraph_index, (start_scene, end_scene) in CHAPTER_TIMING_PARAGRAPHS.items():
        start = display_time(scene_by_id[f"S{start_scene:03d}"]["START_TIME"])
        end = display_time(scene_by_id[f"S{end_scene:03d}"]["END_TIME"])
        set_paragraph_text(document.paragraphs[paragraph_index], f"Thời gian: {start} đến {end}")

    ensure_update_fields(document)

    temp_path = DOCX_PATH.with_name(DOCX_PATH.stem + ".v11r5.tmp.docx")
    document.save(str(temp_path))
    os.replace(temp_path, DOCX_PATH)


if __name__ == "__main__":
    main()
