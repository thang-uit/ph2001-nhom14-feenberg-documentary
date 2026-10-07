#!/usr/bin/env python3
"""Build the V13 review script DOCX for the lecturer.

Reuses the cover page, styles, heading numbering and page-number footer of the
V11 script DOCX (formatting authority) and replaces the body with V13 content
from ``v13_script_content.py`` and ``v13_script_tables.py``. The V11 DOCX is
never modified.

Timing is measured on the final V13 narration (build_v13_voice.py timeline).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from v13_script_content import CHAPTERS, CREDIT, LABELS
import v13_script_tables as T

from common import DELIVER, ROOT
TEMPLATE = ROOT / "templates/KICH_BAN_CHI_TIET_FEENBERG_NHOM_14.docx"
OUTPUT = DELIVER / "KICH_BAN_TRINH_DUYET_FEENBERG_NHOM_14.docx"

PAUSE_RE = re.compile(r"\s*\[PAUSE ([\d.]+)\]")
WORD_RE = re.compile(r"[\wÀ-ỹ]+")

LABEL_COLOR = RGBColor(0x1F, 0x3A, 0x8A)  # deep cobalt, matches film identity
HEADER_FILL = "E7E8EA"
BORDER_COLOR = "B0B0B0"
COVER_LAST_ELEMENT = 8  # body index of the cover's section-break paragraph
TOC_TITLE_ELEMENT = 9
TOC_SECTION_BREAK_ELEMENT = 80


# ----------------------------------------------------------------- timing
def spoken(text: str) -> str:
    return PAUSE_RE.sub("", text).strip()


def build_timeline():
    """Return per-chapter and per-paragraph (start, end) seconds measured on the recorded voice."""
    tl = json.loads((ROOT / "audio/vo/v13_vivienne/timeline.json").read_text())
    assert [len(c["paragraphs"]) for c in tl["chapters"]] == [len(c["paras"]) for c in CHAPTERS], \
        "voice timeline is stale: rerun build_v13_voice.py"
    chapters = [(c["start"], c["end"]) for c in tl["chapters"]]
    paras = [[(p["start"], p["end"]) for p in c["paragraphs"]] for c in tl["chapters"]]
    return chapters, paras, tl["duration"]


def tc(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    return f"{m:02d}:{s:02d}"


# ----------------------------------------------------------- docx helpers
def set_cell_props(cell, width_dxa: int, fill: str | None = None) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    tcw = tcpr.find(qn("w:tcW"))
    if tcw is None:
        tcw = OxmlElement("w:tcW")
        tcpr.append(tcw)
    tcw.set(qn("w:w"), str(width_dxa))
    tcw.set(qn("w:type"), "dxa")
    if fill:
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
        tcpr.append(shd)
    mar = OxmlElement("w:tcMar")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), "70")
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcpr.append(mar)


def write_cell(cell, text: str, *, bold=False, size=10, center=False) -> None:
    cell.paragraphs[0].text = ""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(1)
        pf.space_before = Pt(0)
        if center:
            p.alignment = 1
        run = p.add_run(line)
        run.bold = bold
        run.font.size = Pt(size)


def add_table(doc, headers, rows, widths, size=10):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tblpr = table._tbl.tblPr
    for tag, attrs in (
        ("w:tblW", {"w:w": "5000", "w:type": "pct"}),
        ("w:jc", {"w:val": "center"}),
        ("w:tblLayout", {"w:type": "fixed"}),
    ):
        el = OxmlElement(tag)
        for k, v in attrs.items():
            el.set(qn(k), v)
        tblpr.append(el)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        for k, v in (("w:val", "single"), ("w:sz", "4"), ("w:space", "0"), ("w:color", BORDER_COLOR)):
            b.set(qn(k), v)
        borders.append(b)
    tblpr.append(borders)
    # Repeat header row on each page.
    trpr = table.rows[0]._tr.get_or_add_trPr()
    hdr = OxmlElement("w:tblHeader")
    trpr.append(hdr)
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        set_cell_props(cell, widths[j], HEADER_FILL)
        write_cell(cell, h, bold=True, size=size, center=True)
    for i, row in enumerate(rows, start=1):
        for j, value in enumerate(row):
            cell = table.rows[i].cells[j]
            set_cell_props(cell, widths[j])
            write_cell(cell, value, size=size)
    doc.add_paragraph("", style="Normal")
    return table


def heading(doc, text, level):
    return doc.add_paragraph(text, style=f"Heading {level}")


def body(doc, text, bold=False):
    p = doc.add_paragraph(style="Body Text Report")
    run = p.add_run(text)
    run.bold = bold
    return p


def bullets(doc, items):
    for item in items:
        doc.add_paragraph(f"• {item}", style="List Bullet")


def labelled(doc, label_code, text):
    p = doc.add_paragraph(style="Body Text Report")
    tag = p.add_run(f"[{LABELS[label_code]}] ")
    tag.bold = True
    tag.font.size = Pt(9)
    tag.font.color.rgb = LABEL_COLOR
    p.add_run(spoken(text))
    return p


def add_toc(doc_body_anchor):
    """Insert a real TOC field (Word refreshes it on open)."""
    p = OxmlElement("w:p")
    for kind, payload in (
        ("begin", None),
        ("instr", 'TOC \\o "1-2" \\h \\z \\u'),
        ("separate", None),
        ("text", "Nhấn chuột phải → Update Field để cập nhật số trang mục lục."),
        ("end", None),
    ):
        r = OxmlElement("w:r")
        if kind == "instr":
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = payload
            r.append(it)
        elif kind == "text":
            t = OxmlElement("w:t")
            t.text = payload
            r.append(t)
        else:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r.append(fc)
        p.append(r)
    doc_body_anchor.addnext(p)
    return p


def request_field_update(doc) -> None:
    settings = doc.settings.element
    el = settings.find(qn("w:updateFields"))
    if el is None:
        el = OxmlElement("w:updateFields")
        settings.append(el)
    el.set(qn("w:val"), "true")


# ------------------------------------------------------------- assembly
def prepare_template(doc):
    body_el = doc.element.body
    children = list(body_el)
    toc_title = children[TOC_TITLE_ELEMENT]
    toc_break = children[TOC_SECTION_BREAK_ELEMENT]
    keep = set(children[: COVER_LAST_ELEMENT + 1]) | {toc_title, toc_break, children[-1]}
    for el in children:
        if el not in keep:
            body_el.remove(el)
    # Cover subtitle: mark this as the V12 review draft.
    cover = doc.paragraphs[2]
    for run in cover.runs:
        if run.text.strip() == "KỊCH BẢN VIDEO":
            run.text = "\nKỊCH BẢN VIDEO (BẢN TRÌNH DUYỆT)"
    add_toc(toc_title)


def build(output: Path) -> dict:
    doc = Document(str(TEMPLATE))
    prepare_template(doc)
    chapter_spans, para_spans, content_end = build_timeline()
    credit_start = content_end - CREDIT["crossfade"]
    total = credit_start + CREDIT["duration"]

    # I. Thông tin chung
    heading(doc, "THÔNG TIN CHUNG VÀ TRẠNG THÁI", 1)
    body(doc, "Đây là bản kịch bản V13, sửa theo góp ý của thầy về bản V12. Video được thu giọng và dựng theo đúng lời thoại trong "
         "tài liệu này; mọi mốc thời gian đều đo trên bản thu cuối.")
    add_table(doc, ["Hạng mục", "Nội dung"], T.info_rows(tc(content_end), tc(total)), [2300, 7050])
    heading(doc, "Tiếp thu góp ý của thầy về kịch bản V12", 2)
    body(doc, "Thầy nhận xét bản V12 đã phân biệt rõ dân chủ với dân chủ hóa và trình bày các khái niệm của Feenberg đúng hướng, "
         "đồng thời yêu cầu chỉnh thêm các điểm dưới đây trước khi dựng clip. Bảng đối chiếu từng điểm với cách xử lý trong bản V13.")
    add_table(doc, ["Góp ý của thầy", "Cách xử lý trong kịch bản V13", "Vị trí"], T.FEEDBACK_ROWS, [3000, 4950, 1400])

    # II. Vấn đề và luận điểm
    heading(doc, "VẤN ĐỀ, CÂU HỎI TRUNG TÂM VÀ LUẬN ĐIỂM", 1)
    heading(doc, "Vấn đề triết học", 2)
    body(doc, T.PROBLEM)
    heading(doc, "Câu hỏi trung tâm", 2)
    body(doc, T.CENTRAL_QUESTION, bold=True)
    heading(doc, "Luận điểm của Nhóm 14", 2)
    body(doc, T.THESIS)
    body(doc, "Đây là đề xuất diễn giải của nhóm, không phải trích dẫn của Feenberg.")
    heading(doc, "Phạm vi và giới hạn", 2)
    bullets(doc, T.SCOPE)
    heading(doc, "Quy ước nhãn nội dung", 2)
    body(doc, "Mỗi đoạn lời thoại trong mục V được gắn nhãn (không đọc thành tiếng) để tách dữ kiện, khái niệm có nguồn, "
         "phân tích theo Feenberg và diễn giải của nhóm:")
    add_table(doc, ["Nhãn", "Ý nghĩa"], T.LABEL_ROWS, [3000, 6350])

    # III. Hệ khái niệm
    heading(doc, "HỆ KHÁI NIỆM: ĐỊNH NGHĨA TRƯỚC KHI PHÂN TÍCH", 1)
    heading(doc, "Dân chủ: các nguồn định nghĩa và cách nhóm sử dụng", 2)
    add_table(doc, ["Nguồn", "Nội dung chính", "Cách dùng trong video"], T.DEMOCRACY_ROWS, [2300, 4250, 2800], size=9)
    body(doc, T.DEMOCRACY_WORKING_DEF)
    heading(doc, "Dân chủ hóa và điều kiện của tham gia có hiệu lực", 2)
    body(doc, T.DEMOCRATIZATION_DEF)
    bullets(doc, T.NOT_DEMOCRATIZATION)
    heading(doc, "Ma trận quyền × mức độ tham gia và phép thử bốn câu hỏi", 2)
    add_table(doc, ["Quyền", "Chưa có", "Hình thức", "Có hiệu lực"], T.MATRIX_ROWS, [2100, 2150, 2350, 2750], size=9)
    body(doc, T.MATRIX_NOTE)
    heading(doc, "Công nghệ, thiết kế, quản trị và giá trị công nghệ", 2)
    add_table(doc, ["Khái niệm", "Định nghĩa làm việc", "Không đồng nghĩa với"], T.TECH_ROWS, [2000, 4850, 2500], size=9)
    heading(doc, "Khái niệm của Andrew Feenberg", 2)
    add_table(doc, ["Khái niệm", "Định nghĩa", "Nguồn", "Cách hiểu sai cần tránh"], T.FEENBERG_ROWS, [1900, 3900, 1500, 2050], size=9)
    heading(doc, "Bảo mật, riêng tư; quản lý hiệu quả và bảo vệ quyền", 2)
    add_table(doc, ["Khái niệm", "Nội dung", "Ghi chú"], T.PRIVACY_ROWS, [2200, 4650, 2500], size=9)
    body(doc, T.MANAGEMENT_AND_RIGHTS)
    heading(doc, "Dân chủ trong vòng đời công nghệ (mô hình của Nhóm 14)", 2)
    body(doc, "Bảng trả lời câu hỏi: đưa dân chủ vào giai đoạn nào, bằng cơ chế nào, ai quyết định. Đây là mô hình đề xuất cho "
         "một hệ thống số công nói chung, không mô tả quy trình thực tế của VNeID.")
    add_table(doc, ["Giai đoạn", "Quyết định kỹ thuật / quản trị", "Chủ thể quyết định", "Người chịu tác động",
                    "Kênh tham gia", "Phản hồi / kháng nghị", "Bảo mật", "Ràng buộc"],
              T.LIFECYCLE_ROWS, [1050, 1350, 1150, 1150, 1250, 1200, 1150, 1050], size=8)
    heading(doc, "Ai giám sát, ai có quyền yêu cầu sửa đổi, ai chịu trách nhiệm khắc phục", 2)
    body(doc, "Bản đồ trách nhiệm cho một hệ thống số công như VNeID, theo pháp luật hiện hành tại ngày khóa kịch bản.")
    add_table(doc, ["Câu hỏi", "Chủ thể theo pháp luật hiện hành", "Căn cứ"], T.ACCOUNTABILITY_ROWS, [2000, 4600, 2750], size=9)
    body(doc, T.PROPOSALS_NOTE)
    heading(doc, "Tình huống cụ thể: người bệnh AIDS và việc thiết kế lại thử nghiệm thuốc", 2)
    body(doc, "Dòng thời gian dùng cho Chương 6. Feenberg (1992b, 2008) phân tích tình huống này như một trường hợp hợp lý hóa dân chủ; "
         "các mốc pháp lý lấy từ Federal Register và tài liệu của FDA.")
    add_table(doc, ["Mốc", "Sự kiện", "Nguồn"], T.CASE_ROWS, [1500, 5350, 2500], size=9)

    # IV. Cấu trúc
    heading(doc, "CẤU TRÚC LẬP LUẬN VÀ PHÂN BỔ THỜI LƯỢNG", 1)
    body(doc, "Mạch lập luận: vấn đề triết học → nội hàm dân chủ → dân chủ hóa (ma trận quyền) → quyền lực công trong hệ thống kỹ thuật → "
         "Feenberg → tình huống phản hồi dẫn đến sửa thiết kế → ví dụ VNeID → bảo mật và phản hồi → sở hữu trí tuệ (nhánh phụ) → "
         "luận điểm, bản đồ trách nhiệm và đề xuất → kết luận.")
    rows = []
    for i, ch in enumerate(CHAPTERS):
        s, e = chapter_spans[i]
        rows.append([f"{tc(s)}–{tc(e)}", f"{i + 1}. {ch['title']}", ch["goal"]])
    rows.append([f"{tc(credit_start)}–{tc(total)}", CREDIT["title"], CREDIT["desc"]])
    add_table(doc, ["Thời gian", "Chương", "Mục tiêu lập luận"], rows, [1500, 2600, 5250], size=9)
    body(doc, "Trong toàn tài liệu, “Chương n” tương ứng với mục V.n của phần kịch bản chi tiết.")
    body(doc, f"Tổng thời lượng: {tc(total)} (nội dung {tc(content_end)} + credit {CREDIT['duration']:.1f} giây, "
         f"nối mềm {CREDIT['crossfade']:.1f} giây). Thời gian đo trên bản thu giọng, đã gồm các khoảng nghỉ có chủ đích.")

    # V. Kịch bản chi tiết
    heading(doc, "KỊCH BẢN CHI TIẾT THEO TIMELINE", 1)
    for i, ch in enumerate(CHAPTERS):
        s, e = chapter_spans[i]
        heading(doc, f"{ch['title']}", 2)
        body(doc, f"Thời gian: {tc(s)} đến {tc(e)}", bold=True)
        body(doc, f"Loại phát biểu: {ch['type']}")
        heading(doc, "Mục tiêu lập luận", 3)
        body(doc, ch["goal"])
        heading(doc, "Lời thoại", 3)
        for code, text in ch["paras"]:
            labelled(doc, code, text)
        heading(doc, "Kịch bản hình ảnh và âm thanh", 3)
        scene_rows = []
        for sid, idx, visual, onscreen, audio in ch["scenes"]:
            a = para_spans[i][idx[0]][0]
            b = para_spans[i][idx[-1]][1]
            scene_rows.append([f"{sid}\n{tc(a)}–{tc(b)}", visual, onscreen, audio])
        add_table(doc, ["Cảnh", "Hình ảnh", "Chữ / đồ họa trên màn hình", "Âm thanh"], scene_rows, [1350, 4100, 2500, 1400], size=9)
        heading(doc, "Điểm kiểm tra", 3)
        bullets(doc, ch["checks"])
    heading(doc, CREDIT["title"], 2)
    body(doc, f"Thời gian: {tc(credit_start)} đến {tc(total)}", bold=True)
    body(doc, CREDIT["desc"])

    # VI. Nguyên tắc hình ảnh âm thanh
    heading(doc, "NGUYÊN TẮC HÌNH ẢNH, ÂM THANH VÀ PHỤ ĐỀ", 1)
    bullets(doc, T.PRODUCTION_RULES)

    # VII. Kiểm chứng
    heading(doc, "BẢNG KIỂM CHỨNG NỘI DUNG", 1)
    body(doc, "Mỗi mệnh đề đọc trong video được gắn loại và nguồn. Mệnh đề có trạng thái “CẦN ĐỐI CHIẾU” sẽ chỉ được đọc "
         "như sự thật sau khi nhóm đối chiếu văn bản gốc và ghi số trang/điều khoản; nếu không đối chiếu được, câu đó sẽ được "
         "diễn đạt lại hoặc bỏ.")
    add_table(doc, ["Mã", "Mệnh đề", "Loại", "Nguồn / vị trí", "Trạng thái"], T.CLAIM_ROWS, [700, 3700, 1250, 2550, 1150], size=8)

    # VIII. Xin ý kiến
    heading(doc, "NHỮNG ĐIỂM NHÓM XIN Ý KIẾN THẦY", 1)
    bullets(doc, T.QUESTIONS_FOR_LECTURER)

    # IX. Tài liệu
    heading(doc, "DANH MỤC TÀI LIỆU THAM KHẢO", 1)
    for ref in T.REFERENCES:
        doc.add_paragraph(ref, style="Body Text Report")

    request_field_update(doc)
    doc.save(str(output))
    return {"content_end": content_end, "total": total,
            "syllables": sum(len(WORD_RE.findall(spoken(t))) for ch in CHAPTERS for _, t in ch["paras"])}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    args = ap.parse_args()
    stats = build(args.output)
    print(f"wrote {args.output}")
    print(f"syllables={stats['syllables']} content={tc(stats['content_end'])} total={tc(stats['total'])}")


if __name__ == "__main__":
    main()
