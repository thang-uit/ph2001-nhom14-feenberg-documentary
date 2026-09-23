#!/usr/bin/env python3
"""Build deterministic 4K typography and academic motion-design plates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 3840
HEIGHT = 2160
FONT_PATH = Path("/System/Library/Fonts/Avenir Next.ttc")

OBSIDIAN = "#0B0F14"
DEEP_NAVY = "#13202A"
WARM_PAPER = "#E8E1D3"
WHITE = "#F7F4ED"
MUTED = "#AAB3B9"
AMBER = "#E6A23C"
AMBER_DARK = "#9D641D"
TEAL = "#48B8A6"
TEAL_DARK = "#1D746C"
RED = "#C75B5B"


def font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    if not FONT_PATH.is_file():
        raise SystemExit(f"Required font not found: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_size(draw: ImageDraw.ImageDraw, value: str, text_font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), value, font=text_font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, value: str, text_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in value.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if text_size(draw, candidate, text_font)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int,
    anchor: str = "la",
) -> int:
    x, y = xy
    lines = wrap_text(draw, value, text_font, max_width)
    line_height = text_font.size + line_gap
    for line in lines:
        if anchor == "ra":
            width, _ = text_size(draw, line, text_font)
            draw.text((x - width, y), line, font=text_font, fill=fill)
        elif anchor == "ma":
            width, _ = text_size(draw, line, text_font)
            draw.text((x - width // 2, y), line, font=text_font, fill=fill)
        else:
            draw.text((x, y), line, font=text_font, fill=fill)
        y += line_height
    return y


def add_grain(image: Image.Image, opacity: int = 13, seed: int = 14) -> None:
    rng = random.Random(seed)
    small = Image.new("L", (480, 270))
    small.putdata([rng.randrange(88, 168) for _ in range(480 * 270)])
    noise = small.resize(image.size, Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(0.35))
    grain = Image.new("RGBA", image.size, (255, 255, 255, 0))
    grain.putalpha(noise.point(lambda value: value * opacity // 255))
    image.alpha_composite(grain)


def base_plate(seed: int = 14) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), OBSIDIAN)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 250), fill=DEEP_NAVY)
    draw.rectangle((0, HEIGHT - 22, WIDTH, HEIGHT), fill=AMBER_DARK)
    draw.line((260, 245, WIDTH - 260, 245), fill=AMBER, width=3)
    draw.line((WIDTH - 420, 90, WIDTH - 250, 90), fill=(72, 184, 166, 95), width=5)
    draw.line((WIDTH - 420, 120, WIDTH - 310, 120), fill=(72, 184, 166, 55), width=3)
    add_grain(image, seed=seed)
    return image


def transparent_plate() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))


def cinematic_text_overlay(left_weight: float = 0.78) -> Image.Image:
    """Transparent editorial veil for typography over live-action footage."""

    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    stop = int(WIDTH * left_weight)
    for x in range(0, stop, 12):
        progress = x / max(1, stop)
        alpha = int(224 * (1 - progress) ** 1.75)
        draw.rectangle((x, 0, min(stop, x + 12), HEIGHT), fill=(5, 9, 13, alpha))
    draw.rectangle((0, 0, WIDTH, 250), fill=(8, 14, 20, 175))
    draw.rectangle((0, HEIGHT - 250, WIDTH, HEIGHT), fill=(5, 9, 13, 120))
    return image


def draw_kicker(draw: ImageDraw.ImageDraw, value: str, x: int, y: int, color: str = AMBER) -> None:
    draw.rounded_rectangle((x, y, x + 28, y + 28), radius=7, fill=color)
    draw.text((x + 55, y - 11), value, font=font(42), fill=color)


def draw_citation(draw: ImageDraw.ImageDraw, value: str) -> None:
    draw.line((270, HEIGHT - 184, 480, HEIGHT - 184), fill=AMBER, width=4)
    draw_multiline(draw, (510, HEIGHT - 218), value, font(34), MUTED, WIDTH - 780, 10)


def draw_text_sequence_with_vector_arrows(
    draw: ImageDraw.ImageDraw,
    labels: list[str],
    y: int,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    center_x: int = WIDTH // 2,
) -> None:
    """Draw a centered text sequence without relying on an arrow font glyph."""

    widths = [text_size(draw, label, text_font)[0] for label in labels]
    arrow_length = 150
    gap = 44
    connector_width = arrow_length + gap * 2
    total_width = sum(widths) + connector_width * (len(labels) - 1)
    x = center_x - total_width // 2
    arrow_y = y + text_font.size // 2 + 8

    for index, (label, label_width) in enumerate(zip(labels, widths)):
        draw.text((x, y), label, font=text_font, fill=fill)
        x += label_width
        if index == len(labels) - 1:
            continue
        arrow_start = x + gap
        arrow_end = arrow_start + arrow_length
        draw.line((arrow_start, arrow_y, arrow_end, arrow_y), fill=fill, width=10)
        draw.polygon(
            (
                (arrow_end, arrow_y),
                (arrow_end - 32, arrow_y - 21),
                (arrow_end - 32, arrow_y + 21),
            ),
            fill=fill,
        )
        x = arrow_end + gap


def save(image: Image.Image, output_dir: Path, filename: str, records: list[dict], purpose: str) -> None:
    output = output_dir / filename
    image.save(output, format="PNG", optimize=True)
    records.append(
        {
            "filename": filename,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "sha256": sha256(output),
            "purpose": purpose,
        }
    )


def title_overlay() -> Image.Image:
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    panel = (1700, 380, 3560, 1770)
    draw.rounded_rectangle(panel, radius=22, fill=(11, 15, 20, 214), outline=(230, 162, 60, 112), width=3)
    draw_kicker(draw, "NHÓM 14 · PHIM TÀI LIỆU HỌC THUẬT", 1880, 540)
    y = draw_multiline(
        draw,
        (1880, 720),
        "DÂN CHỦ HÓA THIẾT KẾ\nVÀ QUẢN TRỊ CÔNG NGHỆ\nTHEO ANDREW FEENBERG",
        font(98),
        WHITE,
        1480,
        24,
    )
    draw.line((1880, y + 55, 3400, y + 55), fill=AMBER, width=7)
    draw_multiline(
        draw,
        (1880, y + 130),
        "Công nghệ có thực sự trung lập?",
        font(54),
        WARM_PAPER,
        1480,
        16,
    )
    return image


def matrix_plate() -> Image.Image:
    image = base_plate(18)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "BẢN ĐỒ LẬP TRƯỜNG · HAI TRỤC, KHÔNG PHẢI BỐN GIAI ĐOẠN", 270, 115)
    draw.text((270, 340), "CÔNG NGHỆ LÀ…", font=font(86), fill=WHITE)

    left, top, right, bottom = 700, 620, 3500, 1770
    mid_x, mid_y = 2100, 1195
    draw.rounded_rectangle((left, top, right, bottom), radius=18, outline=(232, 225, 211, 110), width=3)
    draw.line((mid_x, top, mid_x, bottom), fill=(232, 225, 211, 160), width=4)
    draw.line((left, mid_y, right, mid_y), fill=(232, 225, 211, 160), width=4)

    draw.text((left + 100, top - 100), "TỰ TRỊ", font=font(52), fill=MUTED)
    right_label = "CON NGƯỜI CÓ THỂ KIỂM SOÁT"
    label_width, _ = text_size(draw, right_label, font(52))
    draw.text((right - label_width - 100, top - 100), right_label, font=font(52), fill=MUTED)
    draw.text((left - 440, top + 210), "TRUNG TÍNH", font=font(48), fill=MUTED)
    draw.text((left - 440, mid_y + 250), "MANG GIÁ TRỊ", font=font(48), fill=MUTED)

    cells = [
        (left, top, mid_x, mid_y, "THUYẾT TẤT ĐỊNH\nCÔNG NGHỆ", "Trung tính · Tự trị", AMBER),
        (mid_x, top, right, mid_y, "THUYẾT CÔNG CỤ", "Trung tính · Có thể kiểm soát", WARM_PAPER),
        (left, mid_y, mid_x, bottom, "THUYẾT THỰC CHẤT", "Mang giá trị · Tự trị", WARM_PAPER),
        (mid_x, mid_y, right, bottom, "LÝ THUYẾT PHÊ PHÁN\nCÔNG NGHỆ", "Mang giá trị · Có thể kiểm soát", TEAL),
    ]
    for x0, y0, x1, y1, heading, note, accent in cells:
        draw.rounded_rectangle((x0 + 35, y0 + 35, x1 - 35, y1 - 35), radius=20, fill=(19, 32, 42, 130))
        draw_multiline(draw, (x0 + 95, y0 + 100), heading, font(62), accent, x1 - x0 - 190, 12)
        draw_multiline(draw, (x0 + 95, y1 - 125), note, font(34), MUTED, x1 - x0 - 190, 8)
    draw_citation(draw, "Andrew Feenberg, What Is Philosophy of Technology?, PDF tr. 5–9")
    return image


def technical_code_plate() -> Image.Image:
    image = base_plate(41)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "KHÁI NIỆM CỐT LÕI", 270, 115, TEAL)
    draw.text((270, 345), "MÃ KỸ THUẬT", font=font(116), fill=WHITE)
    draw.text((275, 495), "TECHNICAL CODE", font=font(45), fill=TEAL)

    x0, x1 = 900, 3270
    layers = [
        (700, "CHÂN TRỜI VĂN HÓA – XÃ HỘI", WARM_PAPER),
        (930, "PHÁN ĐOÁN VỀ ĐIỀU ‘CHẤP NHẬN ĐƯỢC’", AMBER),
        (1160, "TIÊU CHUẨN · THÔNG SỐ · THỦ TỤC", TEAL),
        (1390, "CẤU TRÚC THIẾT KẾ", WARM_PAPER),
    ]
    for index, (y, label, accent) in enumerate(layers):
        inset = index * 115
        draw.rounded_rectangle(
            (x0 + inset, y, x1 - inset, y + 140),
            radius=26,
            fill=(19, 32, 42, 235),
            outline=accent,
            width=4,
        )
        label_width, _ = text_size(draw, label, font(48))
        draw.text(((x0 + x1 - label_width) // 2, y + 39), label, font=font(48), fill=accent)
        if index < len(layers) - 1:
            center = (x0 + x1) // 2
            draw.line((center, y + 140, center, y + 230), fill=AMBER, width=5)
            draw.polygon(((center - 16, y + 210), (center + 16, y + 210), (center, y + 235)), fill=AMBER)
    draw_citation(draw, "Feenberg, “Subversive Rationalization”, PDF tr. 13–15; trang in 313–315")
    return image


def access_participation_plate() -> Image.Image:
    image = base_plate(58)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "KIỂM SOÁT KHÁI NIỆM", 270, 115)
    draw.text((270, 350), "TRUY CẬP KHÔNG ĐỒNG NGHĨA THAM GIA", font=font(88), fill=WHITE)
    columns = [
        (330, "QUYỀN TRUY CẬP", "Được vào · được sử dụng\nnhững phương án đã có", AMBER),
        (2040, "THAM GIA QUYẾT ĐỊNH", "Có thông tin · có phản biện\ncó đường dẫn đến tái thiết kế", TEAL),
    ]
    for x, title, body, accent in columns:
        draw.rounded_rectangle((x, 720, x + 1470, 1630), radius=28, fill=(19, 32, 42, 225), outline=accent, width=5)
        draw.ellipse((x + 90, 845, x + 190, 945), outline=accent, width=10)
        draw.line((x + 140, 945, x + 140, 1220), fill=accent, width=9)
        draw.line((x + 140, 1030, x + 300, 1030), fill=accent, width=9)
        draw.text((x + 350, 830), title, font=font(62), fill=accent)
        draw_multiline(draw, (x + 350, 1040), body, font(50), WARM_PAPER, 1000, 22)
    draw_citation(draw, "Feenberg, What Is Philosophy of Technology?, PDF tr. 10–11")
    return image


def participation_loop_plate() -> Image.Image:
    image = base_plate(62)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "SỰ THAM GIA CÓ HIỆU LỰC", 270, 115, TEAL)
    draw.text((270, 345), "PHẢN HỒI PHẢI ĐI ĐẾN QUYẾT ĐỊNH", font=font(90), fill=WHITE)
    center = (WIDTH // 2, 1260)
    radius_x, radius_y = 1250, 490
    labels = [
        ("KINH NGHIỆM", -150),
        ("PHẢN ĐỐI", -78),
        ("TỔ CHỨC TẬP THỂ", -6),
        ("THAY ĐỔI QUYẾT ĐỊNH", 66),
        ("TÁI THIẾT KẾ", 138),
    ]
    points: list[tuple[int, int]] = []
    for label, angle_degrees in labels:
        angle = math.radians(angle_degrees)
        points.append((int(center[0] + radius_x * math.cos(angle)), int(center[1] + radius_y * math.sin(angle))))
    for first, second in zip(points, points[1:] + points[:1]):
        draw.line((*first, *second), fill=TEAL_DARK, width=18)
    for (x, y), (label, _) in zip(points, labels):
        draw.ellipse((x - 72, y - 72, x + 72, y + 72), fill=DEEP_NAVY, outline=TEAL, width=7)
        label_width, _ = text_size(draw, label, font(41))
        draw.rounded_rectangle((x - label_width // 2 - 34, y + 104, x + label_width // 2 + 34, y + 174), radius=15, fill=(11, 15, 20, 230))
        draw.text((x - label_width // 2, y + 111), label, font=font(41), fill=WARM_PAPER)
    draw_citation(draw, "Feenberg, 1992, PDF tr. 18–20; trang in 318–320")
    return image


QUESTIONS = [
    "AI ĐỊNH NGHĨA VẤN ĐỀ?",
    "GIÁ TRỊ NÀO ĐÃ THÀNH THAM SỐ VÀ MẶC ĐỊNH?",
    "AI CHỊU TÁC ĐỘNG NHƯNG VẮNG MẶT?",
    "SỰ THAM GIA CÓ QUYỀN GÌ?",
    "PHẢN HỒI CÓ ĐI ĐẾN TÁI THIẾT KẾ?",
]


def five_questions_plate() -> Image.Image:
    image = base_plate(82)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "ĐỀ XUẤT CỦA NHÓM 14", 270, 115, AMBER)
    draw.text((270, 350), "NĂM CÂU HỎI MỞ HỘP ĐEN", font=font(98), fill=WHITE)
    top = 700
    for index, question in enumerate(QUESTIONS, start=1):
        y = top + (index - 1) * 255
        accent = TEAL if index in (4, 5) else AMBER
        draw.rounded_rectangle((360, y, 3480, y + 180), radius=24, fill=(19, 32, 42, 230), outline=(232, 225, 211, 45), width=2)
        draw.ellipse((425, y + 36, 533, y + 144), fill=accent)
        number = str(index)
        number_width, _ = text_size(draw, number, font(52))
        draw.text((479 - number_width // 2, y + 48), number, font=font(52), fill=OBSIDIAN)
        draw_multiline(draw, (610, y + 49), question, font(52), WARM_PAPER, 2680, 12)
    draw_citation(draw, "Chuyển dụng phương pháp luận của Nhóm 14; không phải mô hình năm bước do Feenberg trực tiếp nêu")
    return image


def question_overlay(index: int, question: str) -> Image.Image:
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    x, y, width, height = 270, 250, 2500, 290
    draw.rounded_rectangle((x, y, x + width, y + height), radius=22, fill=(11, 15, 20, 218), outline=(72, 184, 166, 130), width=3)
    draw.ellipse((x + 60, y + 69, x + 210, y + 219), fill=TEAL if index >= 4 else AMBER)
    number_width, _ = text_size(draw, str(index), font(72))
    draw.text((x + 135 - number_width // 2, y + 83), str(index), font=font(72), fill=OBSIDIAN)
    draw_multiline(draw, (x + 270, y + 75), question, font(62), WHITE, width - 350, 15)
    draw.rounded_rectangle((x, y + height + 25, x + 720, y + height + 105), radius=16, fill=AMBER)
    draw.text((x + 35, y + height + 35), "ĐỀ XUẤT CỦA NHÓM 14", font=font(38), fill=OBSIDIAN)
    return image


def five_criteria_plate() -> Image.Image:
    image = base_plate(89)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "ĐỀ XUẤT QUẢN TRỊ · NHÓM 14", 270, 115, AMBER)
    draw.text((270, 330), "NĂM ĐIỀU KIỆN ĐỂ THAM GIA CÓ HIỆU LỰC", font=font(88), fill=WHITE)
    labels = [
        ("THAM GIA ĐỦ SỚM", "KHI PHƯƠNG ÁN CÒN CÓ THỂ ĐỔI"),
        ("CÓ THÔNG TIN", "ĐỦ ĐỂ HIỂU VÀ PHẢN BIỆN"),
        ("CÓ ĐẠI DIỆN", "CỦA CÁC NHÓM CHỊU TÁC ĐỘNG"),
        ("CÓ QUYỀN PHẢN BIỆN", "KHÔNG CHỈ ĐƯỢC THÔNG BÁO"),
        ("CÓ DẤU VẾT XỬ LÝ", "PHẢN HỒI ĐI ĐẾN QUYẾT ĐỊNH"),
    ]
    positions = [(280, 670), (1440, 670), (2600, 670), (860, 1120), (2020, 1120)]
    for index, ((title, note), (x, y)) in enumerate(zip(labels, positions), start=1):
        accent = AMBER if index <= 2 else TEAL
        draw.rounded_rectangle(
            (x, y, x + 960, y + 340),
            radius=28,
            fill=(14, 25, 33, 235),
            outline=accent,
            width=4,
        )
        draw.ellipse((x + 55, y + 68, x + 195, y + 208), fill=accent)
        number = str(index)
        number_width, _ = text_size(draw, number, font(56))
        draw.text((x + 125 - number_width // 2, y + 92), number, font=font(56), fill=OBSIDIAN)
        draw_multiline(draw, (x + 245, y + 62), title, font(48), WHITE, 650, 10)
        draw_multiline(draw, (x + 245, y + 190), note, font(31), MUTED, 650, 8)
    draw.rounded_rectangle((730, 1570, 3110, 1688), radius=24, fill=(11, 15, 20, 220))
    draw_text_sequence_with_vector_arrows(
        draw,
        ["PHẢN HỒI", "QUYẾT ĐỊNH", "TÁI THIẾT KẾ"],
        1590,
        font(42),
        AMBER,
    )
    return image


def evidence_limit_plate() -> Image.Image:
    image = base_plate(77)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "GIỚI HẠN BẰNG CHỨNG", 270, 115, RED)
    draw.text((270, 350), "NGUỒN XÁC NHẬN ĐIỀU GÌ?", font=font(98), fill=WHITE)
    draw.rounded_rectangle((330, 740, 3510, 1470), radius=36, fill=(19, 32, 42, 235), outline=(199, 91, 91, 150), width=4)
    draw.text((480, 860), "XÁC NHẬN", font=font(55), fill=TEAL)
    draw_multiline(draw, (480, 980), "Người tham gia lập danh sách ưu tiên\nvà trình cho một tổ chức liên quan.", font(65), WARM_PAPER, 1250, 22)
    draw.line((1915, 820, 1915, 1390), fill=(232, 225, 211, 70), width=3)
    draw.text((2110, 860), "KHÔNG ĐƯỢC SUY RA", font=font(55), fill=RED)
    draw_multiline(draw, (2110, 980), "Danh sách được chấp nhận · đổi chính sách\nhoặc cải thiện điều trị.", font(58), WARM_PAPER, 1180, 22)
    draw_citation(draw, "Feenberg, From Essentialism to Constructivism, PDF tr. 11–12")
    return image


def methodology_plate() -> Image.Image:
    image = base_plate(94)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "BÀI HỌC PHƯƠNG PHÁP LUẬN", 270, 115, TEAL)
    draw.text((270, 350), "LẦN NGƯỢC · RỒI MỞ KHẢ NĂNG CẢI BIẾN", font=font(86), fill=WHITE)
    labels = ["KẾT QUẢ", "THIẾT KẾ", "MÃ KỸ THUẬT", "LỢI ÍCH / QUYỀN LỰC", "THAM GIA", "CẢI BIẾN"]
    positions = [390, 960, 1530, 2100, 2670, 3240]
    y = 1180
    for index, (x, label) in enumerate(zip(positions, labels)):
        accent = AMBER if index < 4 else TEAL
        if index < len(labels) - 1:
            draw.line((x + 86, y, positions[index + 1] - 86, y), fill=accent, width=12)
            draw.polygon(((positions[index + 1] - 110, y - 22), (positions[index + 1] - 110, y + 22), (positions[index + 1] - 70, y)), fill=accent)
        draw.ellipse((x - 70, y - 70, x + 70, y + 70), fill=DEEP_NAVY, outline=accent, width=8)
        label_font = font(36 if len(label) < 15 else 31)
        label_width, _ = text_size(draw, label, label_font)
        draw_multiline(draw, (x - min(label_width, 440) // 2, y + 125), label, label_font, WARM_PAPER, 470, 10)
    draw_citation(draw, "Tổng hợp phương pháp luận từ các khái niệm đã trình bày; không phải trích dẫn nguyên văn")
    return image


def credit_course_plate() -> Image.Image:
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    panel = (300, 350, 3320, 1760)
    draw.rounded_rectangle(panel, radius=34, fill=(7, 12, 17, 198), outline=(230, 162, 60, 130), width=4)
    draw.rectangle((300, 350, 322, 1760), fill=AMBER)
    draw_kicker(draw, "CREDITS · NHÓM 14", 430, 470, AMBER)
    draw.text((430, 690), "TRIẾT HỌC", font=font(142), fill=WHITE)
    draw.line((440, 930, 3100, 930), fill=(230, 162, 60, 170), width=5)
    rows = [
        ("LỚP", "PH2001.26.1.CH.02"),
        ("GIẢNG VIÊN", "TS. NGUYỄN HỮU SƠN"),
    ]
    y = 1080
    for label, value in rows:
        draw.text((450, y), label, font=font(38), fill=AMBER)
        draw.text((1180, y - 20), value, font=font(66), fill=WARM_PAPER)
        y += 220
    return image


def film_credit_plate() -> Image.Image:
    """Opening card for the film-style credits; no technical disclosure."""
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    panel = (250, 300, 3280, 1810)
    draw.rounded_rectangle(panel, radius=36, fill=(7, 12, 17, 188), outline=(230, 162, 60, 128), width=4)
    draw.rectangle((250, 300, 274, 1810), fill=AMBER)
    draw_kicker(draw, "MỘT PHIM TÀI LIỆU HỌC THUẬT", 410, 450, AMBER)
    draw.multiline_text(
        (410, 690),
        "DÂN CHỦ HÓA THIẾT KẾ\nVÀ QUẢN TRỊ CÔNG NGHỆ",
        font=font(100),
        fill=WHITE,
        spacing=30,
    )
    draw.line((420, 1240, 3020, 1240), fill=(230, 162, 60, 180), width=5)
    draw.text((430, 1370), "THEO ANDREW FEENBERG", font=font(60), fill=WARM_PAPER)
    draw.text((430, 1535), "NHÓM 14 · TRIẾT HỌC", font=font(50), fill=TEAL)
    return image


def credit_members_plate() -> Image.Image:
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    panel = (220, 230, 3620, 1920)
    draw.rounded_rectangle(panel, radius=36, fill=(7, 12, 17, 202), outline=(72, 184, 166, 120), width=4)
    draw.rectangle((220, 230, 244, 1920), fill=TEAL)
    draw_kicker(draw, "NHÓM 14 · THÀNH VIÊN", 390, 380, TEAL)
    members = [
        ("Chu Nam Thắng", "26848201"),
        ("Vũ Ngọc Quốc Khánh", "26848097"),
        ("Nguyễn Lưu Minh Đăng", "26848028"),
        ("Đặng Thị Thuý Hồng", "26848070"),
        ("Lâm Minh Thiện", "26848210"),
        ("Hoàng Vũ", "26848267"),
        ("Đào Hoàng Phúc", "26848169"),
    ]
    draw.text((390, 560), "TỔ SẢN XUẤT", font=font(94), fill=WHITE)
    columns = ((390, members[:4]), (2010, members[4:]))
    for column_index, (x, entries) in enumerate(columns):
        y = 840
        for row_index, (name, student_id) in enumerate(entries):
            accent = AMBER if (column_index + row_index) % 2 == 0 else TEAL
            draw.rounded_rectangle((x, y, x + 1400, y + 205), radius=20, fill=(19, 32, 42, 188), outline=accent, width=3)
            draw.rectangle((x, y, x + 12, y + 205), fill=accent)
            draw.text((x + 60, y + 37), name, font=font(49), fill=WARM_PAPER)
            draw.text((x + 60, y + 118), student_id, font=font(38), fill=MUTED)
            y += 245
    return image


def source_credit_plate(page: int) -> Image.Image:
    image = base_plate(99 + page)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, f"NGUỒN CHÍNH · {page}/2", 270, 115, TEAL)
    if page == 1:
        entries = [
            (
                "ANDREW FEENBERG",
                "What Is Philosophy of Technology?, 2003\nPDF tr. 5–11",
            ),
            (
                "ANDREW FEENBERG",
                "From Essentialism to Constructivism: Philosophy of Technology at the Crossroads\nPDF tr. 10–12, 24–28",
            ),
        ]
    else:
        entries = [
            (
                "ANDREW FEENBERG",
                "“Subversive Rationalization: Technology, Power, and Democracy”\nInquiry 35(3–4), 1992, 301–322\nDOI 10.1080/00201749208602296",
            ),
            (
                "VAL DUSEK",
                "Philosophy of Technology: An Introduction\nBlackwell Publishing, 2006 · PDF tr. 225",
            ),
        ]
    y = 500
    for author, detail in entries:
        draw.text((330, y), author, font=font(52), fill=AMBER)
        y = draw_multiline(draw, (330, y + 110), detail, font(62), WARM_PAPER, 3100, 22) + 120
        draw.line((330, y - 50, 3400, y - 50), fill=(232, 225, 211, 50), width=3)
    return image


def terminology_revision_plate() -> Image.Image:
    image = cinematic_text_overlay(0.95)
    draw = ImageDraw.Draw(image)
    draw_kicker(draw, "MỘT QUỸ ĐẠO KHÁI NIỆM", 250, 115, TEAL)
    draw.text((250, 350), "TỪ CẢI BIẾN ĐẾN DÂN CHỦ HÓA", font=font(92), fill=WHITE)

    x_year, x_text = 330, 1030
    draw.line((640, 690, 640, 1350), fill=(232, 225, 211, 105), width=7)
    entries = [
        (690, "1992", "SUBVERSIVE RATIONALIZATION", "HỢP LÝ HÓA MANG TÍNH CẢI BIẾN", AMBER),
        (1120, "2003", "DEMOCRATIC RATIONALIZATION", "HỢP LÝ HÓA DÂN CHỦ", TEAL),
    ]
    for y, year, english, vietnamese, accent in entries:
        draw.ellipse((598, y - 32, 682, y + 52), fill=OBSIDIAN, outline=accent, width=9)
        draw.text((x_year, y - 58), year, font=font(108), fill=accent)
        draw.text((x_text, y - 25), english, font=font(66), fill=WHITE)
        draw.text((x_text, y + 105), vietnamese, font=font(48), fill=WARM_PAPER)
    draw.rounded_rectangle((1030, 1455, 3360, 1605), radius=28, fill=(11, 15, 20, 205), outline=(72, 184, 166, 125), width=3)
    draw.text((1100, 1496), "CỐT LÕI: SỰ THAM GIA CÓ THỂ CẢI BIẾN CÔNG NGHỆ", font=font(42), fill=TEAL)
    return image


def thanks_plate() -> Image.Image:
    """Clean end-credit thanks card; no production disclosures or notes."""
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    panel = (430, 440, WIDTH - 430, 1700)
    draw.rounded_rectangle(panel, radius=42, fill=(7, 12, 17, 198), outline=(230, 162, 60, 122), width=4)
    draw_kicker(draw, "LỜI CẢM ƠN", 620, 620, TEAL)
    draw.text((WIDTH // 2, 850), "NHÓM 14", font=font(150), fill=WHITE, anchor="ma")
    draw.line((720, 1080, WIDTH - 720, 1080), fill=AMBER, width=7)
    draw_multiline(
        draw,
        (WIDTH // 2, 1210),
        "TRÂN TRỌNG CẢM ƠN THẦY VÀ CÁC BẠN\nĐÃ THEO DÕI",
        font(64),
        WARM_PAPER,
        2600,
        22,
        anchor="ma",
    )
    return image


def clean_end_card() -> Image.Image:
    """Transparent final mark over the moving closing shot."""
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1350, 930, 2490, 1230), radius=28, fill=(7, 12, 17, 202), outline=(230, 162, 60, 122), width=3)
    draw.text((WIDTH // 2, 1010), "NHÓM 14", font=font(86), fill=WHITE, anchor="ma")
    draw.line((1530, 1160, WIDTH // 2, 1160), fill=AMBER, width=6)
    draw.line((WIDTH // 2, 1160, 2310, 1160), fill=TEAL, width=6)
    return image


def evidence_label(value: str, background: str, foreground: str, outline: str | None = None) -> Image.Image:
    image = transparent_plate()
    draw = ImageDraw.Draw(image)
    label_font = font(44)
    text_width, text_height = text_size(draw, value, label_font)
    x, y = 270, 165
    box = (x, y, x + text_width + 110, y + text_height + 70)
    draw.rounded_rectangle(box, radius=17, fill=background, outline=outline, width=4 if outline else 1)
    draw.text((x + 55, y + 30), value, font=label_font, fill=foreground)
    return image


def build(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    save(title_overlay(), output_dir, "S005_title_overlay.png", records, "Opening group/topic/title overlay")
    save(matrix_plate(), output_dir, "S018_S024_matrix_full.png", records, "Verified two-axis four-position matrix")
    save(technical_code_plate(), output_dir, "S041_technical_code_layers.png", records, "Technical-code explanatory layers")
    save(access_participation_plate(), output_dir, "S058_access_not_participation.png", records, "Concept-control comparison")
    save(terminology_revision_plate(), output_dir, "S058_terminology_revision.png", records, "Verified 1992/2003 terminology distinction")
    save(participation_loop_plate(), output_dir, "S062_participation_loop.png", records, "Effective-participation feedback loop")
    save(evidence_limit_plate(), output_dir, "S077_ALS_evidence_limit.png", records, "Explicit ALS evidence boundary")
    save(five_questions_plate(), output_dir, "S082_five_questions_full.png", records, "Group 14 methodological transfer")
    for index, question in enumerate(QUESTIONS, start=1):
        save(question_overlay(index, question), output_dir, f"S{82 + index:03d}_question_{index}_overlay.png", records, f"Question {index} overlay")
    save(five_criteria_plate(), output_dir, "S089_five_criteria.png", records, "Group 14 governance criteria")
    save(methodology_plate(), output_dir, "S094_methodological_motif.png", records, "Final methodological chain")
    save(credit_course_plate(), output_dir, "S097_course_credit.png", records, "Course/class/lecturer credit")
    save(credit_members_plate(), output_dir, "S098_members_credit.png", records, "Seven member names and student IDs")
    save(thanks_plate(), output_dir, "S099_sources_a.png", records, "Clean thanks credit")
    save(clean_end_card(), output_dir, "S100_disclosure.png", records, "Clean final fade card")
    save(film_credit_plate(), output_dir, "S096_film_credit.png", records, "Film-style credit title without technical disclosure")
    save(thanks_plate(), output_dir, "S099_thanks.png", records, "Clean thanks credit")
    save(clean_end_card(), output_dir, "S100_endcard.png", records, "Clean final fade card")

    labels = [
        ("label_hypothetical.png", "TÌNH HUỐNG GIẢ ĐỊNH — NHÓM 14", AMBER_DARK, WHITE, None),
        ("label_reconstruction.png", "TÁI DỰNG MINH HỌA", "#282E35", WARM_PAPER, None),
        ("label_concept.png", "MINH HỌA KHÁI NIỆM", "#101820", TEAL, TEAL),
        ("label_source.png", "DỮ KIỆN TỪ NGUỒN", TEAL_DARK, WHITE, None),
        ("label_feenberg_analysis.png", "PHÂN TÍCH THEO FEENBERG", DEEP_NAVY, WARM_PAPER, AMBER),
        ("label_group_proposal.png", "ĐỀ XUẤT CỦA NHÓM 14", AMBER, OBSIDIAN, None),
    ]
    for filename, value, background, foreground, outline in labels:
        save(evidence_label(value, background, foreground, outline), output_dir, filename, records, value)

    index = {
        "schema_version": "1.0",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "canvas": {"width": WIDTH, "height": HEIGHT, "color_space_intent": "Rec.709 SDR"},
        "font": {"family": "Avenir Next", "path": str(FONT_PATH), "redistributed": False},
        "generator": "Pillow deterministic post-production graphics; no generative image model",
        "asset_count": len(records),
        "assets": records,
    }
    index_path = output_dir / "graphics_index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(records)} graphics at {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.output_dir.resolve())


if __name__ == "__main__":
    main()
