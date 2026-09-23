#!/usr/bin/env python3
"""Build deterministic final typography overlays and source-document cards."""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from final_visual_plan import (
    EXTRA_OVERLAYS,
    FULL_GRAPHIC_SCENES,
    GROUP_HYPOTHETICAL_SCENES,
    GROUP_PROPOSAL_SCENES,
    RECONSTRUCTION_SCENES,
    SCENE_ASSETS,
    SOURCE_SCENES,
    is_generated_video,
    is_reconstruction_asset,
    validate_plan,
)


WIDTH = 1920
HEIGHT = 1080
FONT_PATH = Path("/System/Library/Fonts/Avenir Next.ttc")
OBSIDIAN = (8, 12, 17, 232)
DEEP_NAVY = (19, 32, 42, 242)
WARM_PAPER = (244, 239, 229, 255)
MUTED = (182, 193, 201, 255)
AMBER = (230, 162, 60, 255)
TEAL = (72, 184, 166, 255)
RED = (199, 91, 91, 255)


TITLE_OVERRIDES = {
    "S001": "AI QUYẾT ĐỊNH CÔNG NGHỆ HOẠT ĐỘNG THẾ NÀO?",
    "S003": "DỮ LIỆU · TIÊU CHÍ · NGOẠI LỆ",
    "S004": "GIÁ TRỊ · LỢI ÍCH · QUYỀN LỰC",
    "S006": "KHÔNG PHẢI CASE DO FEENBERG NGHIÊN CỨU",
    "S007": "SỬ DỤNG / THIẾT KẾ / QUẢN TRỊ",
    "S008": "TẦNG 1 · SỬ DỤNG",
    "S009": "TẦNG 2 · THIẾT KẾ",
    "S010": "TẦNG 3 · QUẢN TRỊ",
    "S011": "BA TẦNG LIÊN QUAN, NHƯNG KHÔNG ĐỒNG NGHĨA",
    "S012": "QUYỀN TRUY CẬP KHÔNG PHẢI QUYỀN THAM GIA QUYẾT ĐỊNH",
    "S014": "HIỆU QUẢ — CHO AI?",
    "S016": "BẢN ĐỒ HAI TRỤC · KHÔNG PHẢI BỐN GIAI ĐOẠN",
    "S017": "AI ĐÃ CHỌN CẤU TRÚC CỦA PHƯƠNG TIỆN?",
    "S018": "BẢN ĐỒ HAI TRỤC · BỐN LẬP TRƯỜNG",
    "S024": "LÝ THUYẾT PHÊ PHÁN CÔNG NGHỆ",
    "S026": "MANG GIÁ TRỊ · NHƯNG CÓ THỂ CẢI BIẾN",
    "S027": "TỪ CÔNG DỤNG ĐẾN LỰA CHỌN Ở CẤP KHUNG",
    "S031": "META-CHOICE · LỰA CHỌN Ở CẤP KHUNG",
    "S036": "BẤT ĐỊNH TƯƠNG ĐỐI · KHÔNG PHẢI TÙY Ý",
    "S038": "NHIỀU HƯỚNG PHÁT TRIỂN · KHÔNG CÓ TƯƠNG LAI VIẾT SẴN",
    "S039": "MÃ KỸ THUẬT · TECHNICAL CODE",
    "S040": "KHÔNG PHẢI MÃ NGUỒN · KHÔNG PHẢI ÂM MƯU BÍ MẬT",
    "S042": "GIÁ TRỊ XÃ HỘI CÓ THỂ THÀNH THAM SỐ THIẾT KẾ",
    "S043": "CASE QUY CHUẨN AN TOÀN NỒI HƠI",
    "S047": "KHI MÃ ỔN ĐỊNH, LỊCH SỬ TRANH CHẤP DỄ BỊ QUÊN",
    "S048": "QUAN HỆ XÃ HỘI VÀ KỸ THUẬT ‘CÔ ĐỌNG’ TRONG THIẾT BỊ",
    "S050": "AI CÓ MẶT TRONG MẠNG LƯỚI THIẾT KẾ?",
    "S051": "CHỈ SỐ ĐẠT · NHU CẦU VẪN CÓ THỂ BỊ LOẠI TRỪ",
    "S053": "DÂN CHỦ HÓA CÔNG NGHỆ LÀ GÌ?",
    "S055": "QUYỀN TRUY CẬP KHÔNG ĐỒNG NHẤT VỚI THAM GIA QUYẾT ĐỊNH",
    "S056": "SÁNG KIẾN + SỰ THAM GIA",
    "S058": "PHẢN HỒI PHẢI ĐI ĐẾN QUYẾT ĐỊNH",
    "S059": "MỞ RỘNG KHUNG HỢP LÝ · KHÔNG PHỦ NHẬN HIỆU QUẢ",
    "S062": "CHUYÊN MÔN VẪN CẦN THIẾT · QUYỀN LỰC KHÔNG MẶC NHIÊN NGANG NHAU",
    "S061": "ĐƯỢC NGHE CHƯA CÓ NGHĨA CÓ THỂ ĐỔI THIẾT KẾ",
    "S063": "CHUYÊN MÔN KỸ THUẬT + KINH NGHIỆM SỐNG",
    "S064": "CASE NGUỒN · MẠNG MÁY TÍNH VÀ NHÓM HỖ TRỢ ALS",
    "S065": "MÔ HÌNH BAN ĐẦU · PHÂN PHỐI DỮ LIỆU",
    "S067": "SỰ CHIẾM DỤNG CỦA NGƯỜI DÙNG",
    "S070": "GIAO TIẾP TRỞ THÀNH CHỨC NĂNG CHUẨN",
    "S071": "NHÓM HỖ TRỢ ALS TRÊN PRODIGY · NĂM 1995",
    "S072": "KHOẢNG 500 NGƯỜI ĐỌC · VÀI CHỤC NGƯỜI THAM GIA TÍCH CỰC",
    "S076": "ĐÃ TRÌNH DANH SÁCH · KHÔNG CÓ DỮ LIỆU VỀ KẾT QUẢ SAU ĐÓ",
    "S077": "GIỚI HẠN BẰNG CHỨNG · KHÔNG SUY DIỄN KẾT QUẢ",
    "S078": "THIẾT KẾ · LỢI ÍCH · QUYỀN LỰC",
    "S079": "TIỀM NĂNG · KHÔNG PHẢI BẢO ĐẢM",
    "S080": "VẬN DỤNG VÀO HỆ THỐNG PHÂN LỊCH KHÁM",
    "S081": "THUYẾT CÔNG CỤ · CẦN THIẾT, NHƯNG CHƯA ĐỦ",
    "S082": "NĂM CÂU HỎI MỞ HỘP ĐEN",
    "S088": "THEO DÕI · TRÁCH NHIỆM · TÁI THIẾT KẾ",
    "S090": "CHUYÊN MÔN KỸ THUẬT × KINH NGHIỆM SỐNG",
    "S091": "CÔNG NGHỆ CÓ THỰC SỰ TRUNG LẬP?",
    "S092": "KHÔNG TRUNG TÍNH THEO NGHĨA ‘TRỐNG RỖNG’",
    "S093": "MANG GIÁ TRỊ · NHƯNG CÓ THỂ CẢI BIẾN",
    "S095": "DÂN CHỦ HÓA = CÙNG ĐỊNH HÌNH KHUNG KỸ THUẬT",
    "S096": "MỘT PHIM TÀI LIỆU HỌC THUẬT CỦA NHÓM 14",
}


NO_GENERIC_OVERLAY = set(EXTRA_OVERLAYS) | FULL_GRAPHIC_SCENES | {"S082", "S083", "S084", "S085", "S086", "S087"}


def font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def parse_seconds(value: str) -> float:
    hours, minutes, seconds = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def width(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=face)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = value.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if width(draw, candidate, face) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def normalize_title(value: str) -> str:
    parts = [part.strip() for part in value.split("|") if part.strip()]
    if not parts:
        return ""
    labels = {
        "TÁI DỰNG MINH HỌA",
        "MINH HỌA BẰNG AI",
        "MINH HỌA KHÁI NIỆM",
        "ĐỀ XUẤT CỦA NHÓM 14",
        "DỮ KIỆN TỪ NGUỒN",
        "PHÂN TÍCH THEO FEENBERG",
    }
    if parts[0] in labels and len(parts) > 1:
        parts = parts[1:]
    semantic = [part for part in parts if not re.search(r"\b(PDF|tr\.|Feenberg,|Andrew Feenberg)", part, re.I)]
    value = " · ".join(semantic[:2] or parts[:1])
    value = value.replace("→", " / ").replace("↔", " / ").replace("←", " / ").replace("↑↓", " / ")
    return re.sub(r"\s+", " ", value).strip()


def kicker(scene_id: str) -> tuple[str, tuple[int, int, int, int]]:
    if scene_id in SOURCE_SCENES:
        return "ĐỐI CHIẾU VĂN BẢN GỐC", AMBER
    if scene_id in RECONSTRUCTION_SCENES:
        return "MINH HỌA BẰNG AI", TEAL
    if scene_id in GROUP_HYPOTHETICAL_SCENES:
        return "TÌNH HUỐNG GIẢ ĐỊNH · NHÓM 14", TEAL
    if scene_id in GROUP_PROPOSAL_SCENES:
        return "ĐỀ XUẤT PHƯƠNG PHÁP LUẬN · NHÓM 14", TEAL
    if scene_id in {"S091", "S092", "S093", "S094", "S095", "S096"}:
        return "TỔNG HỢP PHƯƠNG PHÁP LUẬN", AMBER
    if scene_id in {"S038", "S039", "S040", "S049", "S052", "S053", "S059", "S066", "S068", "S069", "S078"}:
        return "MINH HỌA KHÁI NIỆM", AMBER
    return "PHÂN TÍCH THEO FEENBERG", AMBER


def citation(source: str) -> str:
    value = source.strip()
    if not value or value in {"G01", "G02", "G03", "N/A"}:
        return ""
    value = re.sub(r"\s+", " ", value)
    source_names = {
        "1": "Feenberg (2003)",
        "2": "Feenberg (2000)",
        "3": "Feenberg (1992)",
        "4": "Dusek (2006)",
    }
    references: list[str] = []
    for match in re.finditer(r"S0([1-4])(?:\s+PDF)?\s+tr\.\s*([^;]+)", value, flags=re.I):
        pages = re.sub(r"\s+", " ", match.group(2)).strip()
        references.append(f"{source_names[match.group(1)]}, PDF tr. {pages}")
    if references:
        result = " · ".join(dict.fromkeys(references))
        if re.search(r"diễn giải|interpretation|chuyển dụng", value, flags=re.I):
            result += " · diễn giải Nhóm 14"
        return result if len(result) <= 96 else result[:93].rstrip(" ·,;") + "…"

    if re.search(r"đề xuất", value, flags=re.I):
        return "Đề xuất của Nhóm 14"
    if re.search(r"nhóm 14", value, flags=re.I):
        return "Minh họa / diễn giải của Nhóm 14"
    # Suppress production metadata and internal IDs from the film image.  Full
    # provenance remains in the manifest and source-credit cards.
    if re.search(r"thông tin người dùng|câu hỏi trung tâm|kiến trúc tự sự|tên đề tài|giao thức", value, flags=re.I):
        return ""
    return ""


def draw_overlay(row: dict[str, str], output: Path) -> None:
    scene_id = row["SCENE_ID"]
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    title = TITLE_OVERRIDES.get(scene_id, normalize_title(row["ON_SCREEN_TEXT"]))
    kick, accent = kicker(scene_id)

    if scene_id == "S096":
        title_face = font(58, index=1)
        sub_face = font(26)
        title_lines = wrap(draw, title, title_face, 1250)[:2]
        block_w = max(width(draw, line, title_face) for line in title_lines) + 120
        block_h = 190 + 70 * (len(title_lines) - 1)
        x0 = (WIDTH - block_w) // 2
        y0 = (HEIGHT - block_h) // 2
        draw.rounded_rectangle((x0, y0, x0 + block_w, y0 + block_h), radius=24, fill=(8, 12, 17, 224), outline=AMBER, width=2)
        y = y0 + 40
        for line in title_lines:
            line_w = width(draw, line, title_face)
            draw.text(((WIDTH - line_w) // 2, y), line, font=title_face, fill=WARM_PAPER)
            y += 72
        subtitle = "TRIẾT HỌC · PH2001.26.1.CH.02"
        subtitle_w = width(draw, subtitle, sub_face)
        draw.text(((WIDTH - subtitle_w) // 2, y0 + block_h - 50), subtitle, font=sub_face, fill=MUTED)
        image.save(output, optimize=True)
        return

    title_face = font(38, index=1)
    kick_face = font(20, index=1)
    source_face = font(21)
    max_text_width = 750
    lines = wrap(draw, title, title_face, max_text_width)[:2]
    content_width = max([width(draw, line, title_face) for line in lines] + [width(draw, kick, kick_face)])
    source_line = ""  # Bibliographic references belong in the dossier/end credits.
    if source_line:
        content_width = max(content_width, min(width(draw, source_line, source_face), max_text_width))
    box_width = min(850, max(510, content_width + 76))
    box_height = 88 + 52 * len(lines) + (37 if source_line else 0)
    right = scene_id == "S091"
    x0 = WIDTH - box_width - 72 if right else 72
    y0 = 62
    draw.rounded_rectangle((x0, y0, x0 + box_width, y0 + box_height), radius=17, fill=OBSIDIAN)
    draw.rectangle((x0, y0, x0 + 7, y0 + box_height), fill=accent)
    draw.text((x0 + 30, y0 + 17), kick, font=kick_face, fill=MUTED)
    y = y0 + 51
    for line in lines:
        draw.text((x0 + 30, y), line, font=title_face, fill=WARM_PAPER)
        y += 50
    if source_line:
        draw.line((x0 + 30, y + 1, x0 + box_width - 30, y + 1), fill=(110, 123, 132, 150), width=1)
        draw.text((x0 + 30, y + 10), source_line, font=source_face, fill=MUTED)
    image.save(output, optimize=True)


def make_background(seed: str) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT - 1)
        color = (
            round(10 + 7 * ratio),
            round(16 + 15 * ratio),
            round(22 + 19 * ratio),
        )
        draw.line((0, y, WIDTH, y), fill=color)
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16))
    texture = Image.new("RGBA", (240, 135), (0, 0, 0, 0))
    pixels = texture.load()
    for y in range(texture.height):
        for x in range(texture.width):
            value = rng.randint(0, 22)
            pixels[x, y] = (255, 255, 255, value)
    texture = texture.resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    image = Image.alpha_composite(image.convert("RGBA"), texture)
    return image


def source_card(source: Path, output: Path, seed: str, row: dict[str, str]) -> None:
    background = make_background(seed)
    source_image = Image.open(source).convert("RGB")
    max_w, max_h = 1660, 600
    scale = min(max_w / source_image.width, max_h / source_image.height, 1.0)
    fitted = source_image.resize(
        (max(1, round(source_image.width * scale)), max(1, round(source_image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    x = (WIDTH - fitted.width) // 2
    y = 235 + (600 - fitted.height) // 2
    shadow = Image.new("RGBA", background.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x - 24, y - 24, x + fitted.width + 24, y + fitted.height + 24),
        radius=18,
        fill=(0, 0, 0, 145),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    background.alpha_composite(shadow)
    background.alpha_composite(fitted.convert("RGBA"), (x, y))
    draw = ImageDraw.Draw(background)
    draw.line((72, 40, WIDTH - 72, 40), fill=AMBER, width=3)
    title = TITLE_OVERRIDES.get(row["SCENE_ID"], normalize_title(row["ON_SCREEN_TEXT"]))
    title_lines = wrap(draw, title, font(32, 0), 1700)
    if len(title_lines) > 2:
        raise ValueError(f"Source title does not fit: {title}")
    for index, line in enumerate(title_lines):
        draw.text((84, 72 + index * 40), line, font=font(32, 0), fill=WARM_PAPER)
    background.convert("RGB").save(output, quality=96, optimize=True)


def draw_provenance(row: dict[str, str], relative: str, output: Path) -> None:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    sid = row["SCENE_ID"]
    if int(sid[1:]) >= 97 or relative.startswith("assets/source_pages/"):
        image.save(output)
        return
    if is_generated_video(relative):
        label = "MINH HỌA BẰNG AI"
    else:
        image.save(output)
        return
    reference = ""  # Keep evidence-category labels, not running bibliography.
    text = label + ("  |  " + reference if reference else "")
    face = font(20, 5)
    lines = wrap(draw, text, face, 1740)
    if len(lines) > 2:
        raise ValueError(f"Provenance does not fit: {sid}: {text}")
    y0 = 8
    block_width = max(width(draw, line, face) for line in lines) + 32
    draw.rounded_rectangle((80, y0, 80 + block_width, y0 + 10 + 24 * len(lines)), radius=6, fill=(8, 12, 17, 230))
    for index, line in enumerate(lines):
        draw.text((96, y0 + 5 + index * 24), line, font=face, fill=WARM_PAPER)
    image.save(output, optimize=True)


def build(storyboard: Path, project_dir: Path, overlay_dir: Path, still_dir: Path) -> None:
    with storyboard.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    validate_plan([row["SCENE_ID"] for row in rows])
    overlay_dir.mkdir(parents=True, exist_ok=True)
    still_dir.mkdir(parents=True, exist_ok=True)

    for row in rows:
        scene_id = row["SCENE_ID"]
        if scene_id not in NO_GENERIC_OVERLAY:
            draw_overlay(row, overlay_dir / f"{scene_id}_overlay.png")
        for index, relative in enumerate(SCENE_ASSETS[scene_id], start=1):
            draw_provenance(row, relative, overlay_dir / f"{scene_id}_{index:02d}_provenance.png")
            if scene_id not in SOURCE_SCENES or not relative.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            source = project_dir / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            source_card(source, still_dir / f"{scene_id}_{index:02d}_source_card.jpg", f"{scene_id}:{index}", row)

    print(f"Final overlays: {len(list(overlay_dir.glob('S*_overlay.png')))}")
    print(f"Source cards: {len(list(still_dir.glob('*_source_card.jpg')))}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--overlay-dir", type=Path, required=True)
    parser.add_argument("--still-dir", type=Path, required=True)
    args = parser.parse_args()
    build(
        args.storyboard.resolve(),
        args.project_dir.resolve(),
        args.overlay_dir.resolve(),
        args.still_dir.resolve(),
    )


if __name__ == "__main__":
    main()
