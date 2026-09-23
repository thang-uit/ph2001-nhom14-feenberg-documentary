#!/usr/bin/env python3
"""Render cinematic, deterministic 3D-style concept animations.

These clips replace repeated AI footage where the argument calls for an exact
diagram.  All important Vietnamese typography is drawn locally, never by a
generative model.  The visual language is a dark physical studio with amber
technical structure and teal participant feedback.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 12.0
FONT_PATH = Path("/System/Library/Fonts/Avenir Next.ttc")

OBSIDIAN = (7, 11, 16)
NAVY = (16, 29, 39)
PAPER = (241, 235, 224)
MUTED = (158, 171, 181)
AMBER = (230, 162, 60)
AMBER_DARK = (128, 79, 24)
TEAL = (72, 184, 166)
TEAL_DARK = (20, 91, 85)
RED = (199, 91, 91)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size, index=1 if bold else 0)


F_TITLE = font(46, True)
F_SUB = font(25, True)
F_BODY = font(30)
F_SMALL = font(21, True)
F_NUMBER = font(54, True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, value))


def smooth(value: float) -> float:
    value = clamp(value)
    return value * value * (3 - 2 * value)


def ease_out(value: float) -> float:
    value = clamp(value)
    return 1 - (1 - value) ** 3


def pulse(t: float, speed: float = 1.0, phase: float = 0.0) -> float:
    return 0.5 + 0.5 * math.sin((t * speed + phase) * math.tau)


def rgba(color: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return (*color, alpha)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    amount = clamp(amount)
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def base_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), OBSIDIAN)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        amount = y / HEIGHT
        color = mix(NAVY, OBSIDIAN, amount * 0.88)
        draw.line((0, y, WIDTH, y), fill=color)
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((90, -260, 900, 550), fill=rgba(AMBER_DARK, 36))
    gd.ellipse((1260, 440, 2050, 1210), fill=rgba(TEAL_DARK, 32))
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    image = image.convert("RGBA")
    image.alpha_composite(glow)
    return image


BASE = base_background()


def add_moving_light(image: Image.Image, t: float) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x = -500 + 2800 * ((t * 0.055) % 1.0)
    draw.polygon(
        ((x, -100), (x + 230, -100), (x + 880, HEIGHT + 100), (x + 600, HEIGHT + 100)),
        fill=(255, 226, 176, 14),
    )
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(46)))


def add_stage(image: Image.Image, t: float) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    horizon = 790
    draw.polygon(((0, horizon), (WIDTH, horizon), (WIDTH, HEIGHT), (0, HEIGHT)), fill=(2, 5, 8, 92))
    draw.line((90, horizon, WIDTH - 90, horizon), fill=rgba(AMBER_DARK, 54), width=2)
    for index in range(5):
        x = 230 + index * 365 + math.sin(t * 0.45 + index) * 6
        draw.ellipse((x - 120, 905, x + 120, 948), fill=(0, 0, 0, 34))
    image.alpha_composite(layer)


def draw_header(image: Image.Image, kicker: str, title: str, progress: float) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle((76, 62, 105, 91), radius=7, fill=AMBER)
    draw.text((128, 57), kicker, font=F_SUB, fill=AMBER)
    draw.text((76, 116), title, font=F_TITLE, fill=PAPER)
    draw.line((76, 184, WIDTH - 76, 184), fill=(255, 255, 255, 28), width=2)
    draw.line((76, 184, 76 + (WIDTH - 152) * clamp(progress), 184), fill=AMBER, width=3)
    image.alpha_composite(layer)


def draw_text_center(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    face: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
) -> None:
    box = draw.textbbox((0, 0), text, font=face)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2), text, font=face, fill=fill)


def draw_glow_line(
    image: Image.Image,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    width: int = 5,
    alpha: int = 230,
) -> None:
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(points, fill=rgba(color, alpha // 2), width=width * 5, joint="curve")
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(width * 2)))
    draw = ImageDraw.Draw(image)
    draw.line(points, fill=rgba(color, alpha), width=width, joint="curve")


def draw_arrow(
    image: Image.Image,
    start: tuple[float, float],
    end: tuple[float, float],
    color: tuple[int, int, int],
    progress: float = 1.0,
    width: int = 5,
) -> None:
    progress = smooth(progress)
    x = start[0] + (end[0] - start[0]) * progress
    y = start[1] + (end[1] - start[1]) * progress
    draw_glow_line(image, [start, (x, y)], color, width)
    if progress > 0.92:
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        size = 18
        draw = ImageDraw.Draw(image)
        p1 = (x - size * math.cos(angle - 0.55), y - size * math.sin(angle - 0.55))
        p2 = (x - size * math.cos(angle + 0.55), y - size * math.sin(angle + 0.55))
        draw.polygon(((x, y), p1, p2), fill=color)


def draw_card(
    image: Image.Image,
    box: tuple[float, float, float, float],
    label: str,
    accent: tuple[int, int, int] = AMBER,
    opacity: int = 235,
    number: str | None = None,
) -> None:
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 12, y0 + 16, x1 + 12, y1 + 16), radius=18, fill=(0, 0, 0, 120))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=18, fill=(13, 22, 29, opacity), outline=rgba(accent, 155), width=2)
    draw.rectangle((x0, y0, x0 + 7, y1), fill=accent)
    if number:
        draw.text((x0 + 28, y0 + 21), number, font=F_NUMBER, fill=accent)
        draw.text((x0 + 104, y0 + 33), label, font=F_SMALL, fill=PAPER)
    else:
        draw_text_center(draw, ((x0 + x1) / 2, (y0 + y1) / 2), label, F_SMALL, PAPER)


def draw_iso_prism(
    image: Image.Image,
    center: tuple[float, float],
    width: float,
    depth: float,
    height: float,
    accent: tuple[int, int, int],
    alpha: int = 245,
) -> None:
    cx, cy = center
    top = [(cx, cy - depth / 2), (cx + width / 2, cy), (cx, cy + depth / 2), (cx - width / 2, cy)]
    right = [(cx + width / 2, cy), (cx + width / 2, cy + height), (cx, cy + depth / 2 + height), (cx, cy + depth / 2)]
    left = [(cx - width / 2, cy), (cx, cy + depth / 2), (cx, cy + depth / 2 + height), (cx - width / 2, cy + height)]
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((cx - width * 0.6, cy + height + depth * 0.25, cx + width * 0.65, cy + height + depth * 0.75), fill=(0, 0, 0, 130))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))
    draw = ImageDraw.Draw(image)
    draw.polygon(left, fill=(15, 24, 31, alpha), outline=rgba(accent, 120))
    draw.polygon(right, fill=(9, 16, 22, alpha), outline=rgba(accent, 120))
    draw.polygon(top, fill=(31, 42, 49, alpha), outline=rgba(accent, 210))
    draw.line(top + [top[0]], fill=rgba(accent, 210), width=3)


def draw_node(image: Image.Image, xy: tuple[float, float], radius: int, color: tuple[int, int, int], active: float = 1.0) -> None:
    x, y = xy
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((x - radius * 2, y - radius * 2, x + radius * 2, y + radius * 2), fill=rgba(color, round(80 * active)))
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(radius)))
    draw = ImageDraw.Draw(image)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(mix(OBSIDIAN, color, 0.35), 255), outline=rgba(color, round(255 * active)), width=4)


def animation_three_layers(image: Image.Image, t: float) -> None:
    draw_header(image, "BA TẦNG PHÂN TÍCH", "SỬ DỤNG · THIẾT KẾ · QUẢN TRỊ", t / DURATION)
    add_stage(image, t)
    labels = [("SỬ DỤNG", TEAL), ("THIẾT KẾ", AMBER), ("QUẢN TRỊ", PAPER)]
    reveal = smooth(t / 2.2)
    for index, (label, accent) in enumerate(labels):
        separation = (index - 1) * 160 * reveal
        cx = 960 + (index - 1) * 18
        cy = 510 + separation
        draw_iso_prism(image, (cx, cy), 720, 170, 58, accent, 225)
        draw = ImageDraw.Draw(image)
        draw_text_center(draw, (cx, cy + 50), label, F_BODY, accent)
    if t > 3.1:
        draw_arrow(image, (520, 760), (1400, 390), TEAL, (t - 3.1) / 3.2, 6)
        draw = ImageDraw.Draw(image)
        draw_text_center(draw, (960, 885), "LIÊN QUAN — NHƯNG KHÔNG ĐỒNG NGHĨA", F_SUB, PAPER)


def animation_matrix(image: Image.Image, t: float) -> None:
    draw_header(image, "BẢN ĐỒ LẬP TRƯỜNG CỦA FEENBERG", "HAI TRỤC · BỐN GIAO ĐIỂM", t / DURATION)
    cx, cy = 960, 600
    line_p = smooth(t / 2.0)
    draw_arrow(image, (420, cy), (1500, cy), AMBER, line_p, 4)
    draw_arrow(image, (cx, 900), (cx, 285), TEAL, line_p, 4)
    draw = ImageDraw.Draw(image)
    draw.text((395, 640), "TỰ TRỊ", font=F_SMALL, fill=MUTED)
    draw.text((1370, 640), "CON NGƯỜI KIỂM SOÁT", font=F_SMALL, fill=MUTED)
    draw.text((990, 280), "TRUNG TÍNH", font=F_SMALL, fill=MUTED)
    draw.text((990, 860), "MANG GIÁ TRỊ", font=F_SMALL, fill=MUTED)
    cards = [
        ((480, 330, 845, 505), "TẤT ĐỊNH\nCÔNG NGHỆ", AMBER),
        ((1075, 330, 1440, 505), "THUYẾT\nCÔNG CỤ", TEAL),
        ((480, 695, 845, 870), "THUYẾT\nTHỰC CHẤT", RED),
        ((1075, 695, 1440, 870), "LÝ THUYẾT PHÊ PHÁN\nCÔNG NGHỆ", AMBER),
    ]
    active = int((t * 0.55) % 4)
    for index, (box, label, accent) in enumerate(cards):
        progress = smooth((t - 1.0 - index * 0.38) / 1.2)
        if progress <= 0:
            continue
        x0, y0, x1, y1 = box
        y_shift = (1 - progress) * 45
        draw_card(image, (x0, y0 + y_shift, x1, y1 + y_shift), label, accent if index == active else mix(accent, MUTED, 0.55), round(205 + 30 * progress))


def animation_framework(image: Image.Image, t: float) -> None:
    draw_header(image, "LỰA CHỌN Ở CẤP KHUNG", "KHÔNG CHỈ CHỌN BÊN TRONG MỘT HỘP", t / DURATION)
    add_stage(image, t)
    p = smooth(t / 2.5)
    draw_iso_prism(image, (700, 520), 520, 150, 190, AMBER)
    draw_iso_prism(image, (1270, 520), 520, 150, 190, TEAL)
    draw = ImageDraw.Draw(image)
    draw_text_center(draw, (700, 600), "KHUNG A", F_BODY, AMBER)
    draw_text_center(draw, (1270, 600), "KHUNG B", F_BODY, TEAL)
    frame_x = 700 + (1270 - 700) * smooth((t - 2) / 4)
    draw.rounded_rectangle((frame_x - 245, 380, frame_x + 245, 735), radius=26, outline=rgba(PAPER, 220), width=8)
    draw_arrow(image, (850, 865), (1110, 865), TEAL, p, 5)
    draw_text_center(draw, (960, 910), "META-CHOICE · THAY ĐỔI CẤU TRÚC KHẢ NĂNG", F_SUB, PAPER)


def animation_multiple_solutions(image: Image.Image, t: float) -> None:
    draw_header(image, "BẤT ĐỊNH TƯƠNG ĐỐI CỦA THIẾT KẾ", "RÀNG BUỘC CÓ THẬT · GIẢI PHÁP KHÔNG DUY NHẤT", t / DURATION)
    draw = ImageDraw.Draw(image)
    for x, label in ((335, "VẬT LIỆU"), (700, "TỰ NHIÊN"), (1065, "CHI PHÍ"), (1430, "HẠ TẦNG")):
        draw_card(image, (x - 145, 270, x + 145, 365), label, MUTED, 190)
        draw.line((x, 365, x, 770), fill=rgba(MUTED, 45), width=2)
    starts = [(210, 840), (210, 840), (210, 840)]
    ends = [(1710, 480), (1710, 650), (1710, 820)]
    colors = [AMBER, TEAL, PAPER]
    for index, (start, end, color) in enumerate(zip(starts, ends, colors)):
        points = [start, (500, 770 - index * 80), (900, 520 + index * 100), (1320, 590 + index * 80), end]
        progress = (t - 1.0 - index * 0.65) / 4.5
        segment_count = max(1, round(clamp(progress) * (len(points) - 1)))
        draw_glow_line(image, points[: segment_count + 1], color, 5, 210)
        if progress > 0:
            draw_node(image, end, 22, color, clamp(progress))
    draw_text_center(draw, (960, 940), "NHIỀU ĐƯỜNG KHẢ THI TRONG PHẠM VI RÀNG BUỘC", F_SUB, PAPER)


def animation_technical_code(image: Image.Image, t: float) -> None:
    draw_header(image, "MÃ KỸ THUẬT · TECHNICAL CODE", "GIÁ TRỊ XÃ HỘI ĐI VÀO CẤU TRÚC THIẾT KẾ", t / DURATION)
    labels = [
        ("CHÂN TRỜI VĂN HÓA – XÃ HỘI", AMBER),
        ("PHÁN ĐOÁN · GIẢ ĐỊNH", PAPER),
        ("TIÊU CHUẨN · THỦ TỤC", TEAL),
        ("CẤU TRÚC THIẾT KẾ", AMBER),
    ]
    for index, (label, accent) in enumerate(labels):
        p = smooth((t - index * 0.7) / 1.8)
        y = 285 + index * 155
        x0 = 380 + (1 - p) * 160
        x1 = 1540 - (1 - p) * 160
        draw_card(image, (x0, y, x1, y + 102), label, accent, round(150 + 85 * p))
        if index:
            draw_arrow(image, (960, y - 48), (960, y - 6), accent, p, 4)
    travel = (t * 0.28) % 1.0
    dot_y = 305 + travel * 565
    draw_node(image, (960, dot_y), 13, TEAL, 0.65 + 0.35 * pulse(t, 1.8))
    draw = ImageDraw.Draw(image)
    draw_text_center(draw, (960, 932), "KHÔNG PHẢI MÃ NGUỒN · KHÔNG PHẢI ÂM MƯU BÍ MẬT", F_SUB, MUTED)


def animation_nonzero_sum(image: Image.Image, t: float) -> None:
    draw_header(image, "TÁI THIẾT KẾ", "HIỆU QUẢ KHÔNG NHẤT THIẾT LOẠI TRỪ GIÁ TRỊ", t / DURATION)
    add_stage(image, t)
    labels = [("HIỆU QUẢ", AMBER), ("AN TOÀN", TEAL), ("TIẾP CẬN", PAPER)]
    positions = [(665, 560), (960, 470), (1255, 560)]
    for index, ((label, color), (x, y)) in enumerate(zip(labels, positions)):
        angle = t * (0.3 if index % 2 == 0 else -0.28)
        radius = 118
        draw_node(image, (x, y), radius, color, 0.9)
        draw = ImageDraw.Draw(image)
        for tooth in range(12):
            a = angle + tooth * math.tau / 12
            tx, ty = x + math.cos(a) * 142, y + math.sin(a) * 142
            draw.rectangle((tx - 10, ty - 18, tx + 10, ty + 18), fill=rgba(color, 130))
        draw_text_center(draw, (x, y), label, F_SMALL, PAPER)
    draw_glow_line(image, [positions[0], positions[1], positions[2]], TEAL, 4, 150)
    draw = ImageDraw.Draw(image)
    draw_text_center(draw, (960, 885), "MỘT CẤU TRÚC MỚI CÓ THỂ ĐÁP ỨNG NHIỀU ĐÒI HỎI", F_SUB, PAPER)


def animation_access_participation(image: Image.Image, t: float) -> None:
    draw_header(image, "DÂN CHỦ HÓA CÔNG NGHỆ", "QUYỀN TRUY CẬP ≠ THAM GIA QUYẾT ĐỊNH", t / DURATION)
    draw = ImageDraw.Draw(image)
    draw.line((960, 260, 960, 910), fill=(255, 255, 255, 30), width=2)
    draw_text_center(draw, (485, 260), "TRUY CẬP", F_BODY, AMBER)
    draw_text_center(draw, (1435, 260), "THAM GIA CÓ HIỆU LỰC", F_BODY, TEAL)
    for x in (280, 410, 540, 670):
        draw_node(image, (x, 760), 24, AMBER, 0.65)
    draw_iso_prism(image, (485, 490), 390, 130, 125, AMBER)
    draw_arrow(image, (485, 730), (485, 565), AMBER, t / 2.2, 5)
    draw.line((290, 355, 680, 355), fill=rgba(RED, 190), width=9)
    draw_text_center(draw, (485, 330), "QUYẾT ĐỊNH VẪN ĐÓNG", F_SMALL, RED)
    for x in (1230, 1365, 1500, 1635):
        draw_node(image, (x, 760), 24, TEAL, 0.78)
    draw_iso_prism(image, (1435, 490), 390, 130, 125, TEAL)
    draw_arrow(image, (1435, 730), (1435, 565), TEAL, t / 1.8, 5)
    draw_arrow(image, (1545, 455), (1310, 455), TEAL, (t - 2.0) / 2.6, 5)
    draw_text_center(draw, (1435, 330), "PHẢN HỒI ĐI TỚI TÁI THIẾT KẾ", F_SMALL, TEAL)


def animation_decision_locked(image: Image.Image, t: float) -> None:
    draw_header(image, "THAM GIA HÌNH THỨC", "ĐƯỢC NGHE CHƯA CÓ NGHĨA CÓ THỂ THAY ĐỔI", t / DURATION)
    draw = ImageDraw.Draw(image)
    draw_card(image, (220, 430, 650, 670), "PHẢN HỒI CỦA\nNGƯỜI CHỊU TÁC ĐỘNG", TEAL)
    draw_card(image, (1270, 430, 1700, 670), "THIẾT KẾ\nĐÃ KHÓA", RED)
    wall_x = 1050
    draw.rounded_rectangle((wall_x - 32, 285, wall_x + 32, 830), radius=8, fill=rgba(RED, 190))
    draw_text_center(draw, (wall_x, 875), "KHÔNG CÓ CƠ CHẾ CHUYỂN HÓA", F_SMALL, RED)
    p = smooth((t % 5.0) / 3.0)
    end_x = min(1010, 650 + 380 * p)
    draw_arrow(image, (650, 550), (end_x, 550), TEAL, 1.0, 6)
    if end_x >= 1005:
        for offset in (-30, 0, 30):
            draw.line((1000, 550, 975, 550 + offset), fill=rgba(TEAL, 115), width=3)


def animation_participation_loop(image: Image.Image, t: float) -> None:
    draw_header(image, "THAM GIA CÓ HIỆU LỰC", "AI · KHI NÀO · THÔNG TIN · PHẢN BIỆN · THAY ĐỔI", t / DURATION)
    center = (960, 585)
    labels = ["AI?", "KHI NÀO?", "THÔNG TIN", "PHẢN BIỆN", "THAY ĐỔI"]
    positions: list[tuple[float, float]] = []
    for index in range(5):
        angle = -math.pi / 2 + index * math.tau / 5
        positions.append((center[0] + math.cos(angle) * 430, center[1] + math.sin(angle) * 285))
    for index, (label, position) in enumerate(zip(labels, positions)):
        active = 0.5 + 0.5 * smooth((t - index * 0.55) / 1.1)
        draw_node(image, position, 48, TEAL if index == 4 else AMBER, active)
        draw_text_center(ImageDraw.Draw(image), (position[0], position[1] + 82), label, F_SMALL, PAPER)
        draw_arrow(image, position, positions[(index + 1) % 5], TEAL, (t - 0.7 - index * 0.45) / 2.2, 3)
    draw_iso_prism(image, center, 330, 105, 120, AMBER)
    draw_text_center(ImageDraw.Draw(image), (center[0], center[1] + 48), "THIẾT KẾ", F_BODY, PAPER)
    orbit = (t / DURATION) * math.tau * 1.4 - math.pi / 2
    token = (center[0] + math.cos(orbit) * 430, center[1] + math.sin(orbit) * 285)
    draw_node(image, token, 18, TEAL, 1.0)


def animation_network_transform(image: Image.Image, t: float) -> None:
    draw_header(
        image,
        "QUỸ ĐẠO CỦA MẠNG",
        "TỪ PHÂN PHỐI DỮ LIỆU ĐẾN GIAO TIẾP GIỮA NGƯỜI VỚI NGƯỜI",
        t / DURATION,
    )
    hub = (960, 510)
    terminals = [(380, 350), (380, 700), (720, 850), (1200, 850), (1540, 700), (1540, 350)]
    draw_iso_prism(image, hub, 360, 115, 135, AMBER)
    draw_text_center(ImageDraw.Draw(image), (hub[0], hub[1] + 48), "TRUNG TÂM DỮ LIỆU", F_SMALL, PAPER)
    transform = smooth((t - 3.5) / 3.5)
    for index, terminal in enumerate(terminals):
        draw_node(image, terminal, 38, TEAL if transform > 0.5 else AMBER, 0.75)
        draw_arrow(image, hub, terminal, AMBER, (t - index * 0.18) / 2.8, 3)
    if transform > 0:
        for start, end in zip(terminals, terminals[1:] + terminals[:1]):
            draw_glow_line(image, [start, end], TEAL, max(1, round(4 * transform)), round(210 * transform))
        draw_card(image, (740, 760, 1180, 890), "GIAO TIẾP TRỞ THÀNH CHỨC NĂNG CHUẨN", TEAL, round(120 + 110 * transform))


def animation_evidence_boundary(image: Image.Image, t: float) -> None:
    draw_header(image, "GIỚI HẠN BẰNG CHỨNG", "DỮ KIỆN NGUỒN KHÔNG CHO PHÉP SUY DIỄN KẾT QUẢ", t / DURATION)
    draw = ImageDraw.Draw(image)
    p = smooth(t / 2.2)
    boundary = (130, 280, 1040, 890)
    draw.rounded_rectangle(boundary, radius=24, fill=(20, 38, 44, 185), outline=rgba(TEAL, round(230 * p)), width=5)
    draw.text((175, 315), "ĐÃ XÁC NHẬN TRONG NGUỒN", font=F_SUB, fill=TEAL)
    draw_card(image, (210, 430, 905, 565), "CỘNG ĐỒNG LẬP DANH SÁCH ƯU TIÊN", TEAL)
    draw_card(image, (210, 650, 905, 785), "DANH SÁCH ĐƯỢC TRÌNH CHO TỔ CHỨC LIÊN QUAN", TEAL)
    draw_arrow(image, (558, 565), (558, 645), TEAL, t / 2.0, 5)
    unknown = ["ĐƯỢC CHẤP NHẬN?", "ĐỔI CHÍNH SÁCH?", "CẢI THIỆN ĐIỀU TRỊ?"]
    for index, label in enumerate(unknown):
        y = 365 + index * 190
        draw_card(image, (1180, y, 1745, y + 120), label, MUTED, 160)
        draw_text_center(draw, (1135, y + 60), "?", F_NUMBER, MUTED)
    draw.line((1088, 280, 1088, 890), fill=rgba(RED, 180), width=5)
    draw_text_center(draw, (1088, 940), "RANH GIỚI SUY LUẬN", F_SMALL, RED)


def animation_five_questions(image: Image.Image, t: float) -> None:
    draw_header(image, "NĂM CÂU HỎI MỞ HỘP ĐEN", "KHUNG CHUYỂN DỤNG PHƯƠNG PHÁP LUẬN · NHÓM 14", t / DURATION)
    labels = [
        "AI ĐỊNH NGHĨA VẤN ĐỀ?",
        "GIÁ TRỊ NÀO THÀNH MẶC ĐỊNH?",
        "AI CHỊU TÁC ĐỘNG NHƯNG VẮNG MẶT?",
        "SỰ THAM GIA CÓ QUYỀN GÌ?",
        "PHẢN HỒI CÓ ĐI TỚI TÁI THIẾT KẾ?",
    ]
    active = min(4, int((t / DURATION) * 5))
    for index, label in enumerate(labels):
        depth = index - active
        scale = 1.0 - max(0, depth) * 0.055
        width = 1320 * scale
        x0 = (WIDTH - width) / 2 + depth * 26
        y0 = 290 + index * 130
        p = smooth((t - index * 0.35) / 1.4)
        if p <= 0:
            continue
        accent = TEAL if index == active else mix(AMBER, MUTED, 0.55)
        draw_card(image, (x0, y0 + (1 - p) * 45, x0 + width, y0 + 100 + (1 - p) * 45), label, accent, 220, str(index + 1))


def animation_efficiency_exclusion(image: Image.Image, t: float) -> None:
    draw_header(image, "HIỆU QUẢ — CHO AI?", "HỆ THỐNG CÓ THỂ ĐẠT CHỈ SỐ VÀ VẪN TẠO BẤT LỢI", t / DURATION)
    draw = ImageDraw.Draw(image)
    left, top = 210, 310
    cell_w, cell_h = 108, 86
    filled = min(35, round(t / DURATION * 42))
    for row in range(5):
        for col in range(7):
            index = row * 7 + col
            x0, y0 = left + col * cell_w, top + row * cell_h
            color = AMBER if index < filled else NAVY
            draw.rounded_rectangle((x0, y0, x0 + 88, y0 + 62), radius=10, fill=rgba(color, 210), outline=rgba(PAPER, 35), width=1)
    draw_card(image, (220, 800, 930, 905), "GIẢM THỜI GIAN TRỐNG · CHỈ SỐ ĐẠT", AMBER)
    people = [(1240, 405, "THIẾU THIẾT BỊ"), (1475, 575, "CẦN HỖ TRỢ"), (1240, 745, "MẠNG KHÔNG ỔN ĐỊNH")]
    for index, (x, y, label) in enumerate(people):
        draw_node(image, (x, y), 44, RED, 0.72)
        draw_card(image, (x + 72, y - 48, x + 395, y + 48), label, RED, 175)
    draw.line((1065, 280, 1065, 915), fill=rgba(RED, 150), width=5)
    draw_text_center(draw, (1065, 955), "NGOÀI PHÉP TÍNH", F_SMALL, RED)


def animation_lifecycle(image: Image.Image, t: float) -> None:
    draw_header(image, "QUẢN TRỊ XUYÊN VÒNG ĐỜI", "TRIỂN KHAI KHÔNG PHẢI ĐIỂM KẾT THÚC", t / DURATION)
    center = (960, 585)
    labels = ["TRIỂN KHAI", "THEO DÕI", "KHÁNG NGHỊ", "TÁI THIẾT KẾ"]
    positions = [(960, 300), (1390, 585), (960, 870), (530, 585)]
    for index, (label, position) in enumerate(zip(labels, positions)):
        accent = AMBER if index == 0 else TEAL
        draw_node(image, position, 46, accent, 0.85)
        draw_text_center(ImageDraw.Draw(image), (position[0], position[1] + (82 if index in (0, 2) else 76)), label, F_SMALL, PAPER)
        draw_arrow(image, position, positions[(index + 1) % 4], TEAL, (t - 0.5 - index * 0.5) / 2.2, 4)
    draw_iso_prism(image, center, 360, 115, 125, TEAL if t > 6 else AMBER)
    draw_text_center(ImageDraw.Draw(image), (center[0], center[1] + 48), "V2" if t > 6 else "V1", F_NUMBER, PAPER)
    angle = -math.pi / 2 + t / DURATION * math.tau * 1.25
    token = (center[0] + math.cos(angle) * 430, center[1] + math.sin(angle) * 285)
    draw_node(image, token, 18, TEAL, 1.0)


def animation_five_criteria(image: Image.Image, t: float) -> None:
    draw_header(image, "ĐỀ XUẤT CỦA NHÓM 14", "NĂM ĐIỀU KIỆN ĐỂ THAM GIA CÓ HIỆU LỰC", t / DURATION)
    labels = ["SỚM", "CÓ THÔNG TIN", "CÓ ĐẠI DIỆN", "CÓ QUYỀN PHẢN HỒI", "CÓ DẤU VẾT XỬ LÝ"]
    reveal = smooth(t / 2.8)
    for index, label in enumerate(labels):
        y = 320 + index * 115
        x_shift = (1 - reveal) * (220 if index % 2 == 0 else -220)
        draw_card(image, (515 + x_shift, y, 1405 + x_shift, y + 82), label, TEAL if index >= 2 else AMBER, 225, str(index + 1))
    if t > 4.5:
        draw = ImageDraw.Draw(image)
        alpha = round(230 * smooth((t - 4.5) / 2.0))
        draw.rounded_rectangle((445, 260, 1475, 955), radius=38, outline=rgba(PAPER, alpha), width=7)
        draw.line((1475, 555, 1655, 555), fill=rgba(TEAL, alpha), width=7)
        draw_node(image, (1680, 555), 24, TEAL, alpha / 230)


def animation_conclusion_layers(image: Image.Image, t: float) -> None:
    draw_header(image, "MỞ HỘP ĐEN", "GIÁ TRỊ · LỢI ÍCH · QUYỀN LỰC CÓ THỂ ĐI VÀO THIẾT KẾ", t / DURATION)
    labels = ["ĐỊNH NGHĨA VẤN ĐỀ", "TIÊU CHUẨN", "THỦ TỤC", "CẤU TRÚC THIẾT KẾ"]
    for index, label in enumerate(labels):
        p = smooth((t - index * 0.55) / 1.8)
        y = 350 + index * 135
        draw_iso_prism(image, (960 + (index - 1.5) * 18, y), 860, 150, 54, TEAL if index == 3 else AMBER, round(150 + 90 * p))
        draw_text_center(ImageDraw.Draw(image), (960, y + 48), label, F_SMALL, PAPER)
    draw_arrow(image, (370, 820), (1550, 350), TEAL, (t - 2.0) / 5.0, 7)


def animation_method_motif(image: Image.Image, t: float) -> None:
    draw_header(image, "BÀI HỌC PHƯƠNG PHÁP LUẬN", "LẦN NGƯỢC TỪ KẾT QUẢ · MỞ KHẢ NĂNG CẢI BIẾN", t / DURATION)
    labels = ["KẾT QUẢ", "THIẾT KẾ", "MÃ KỸ THUẬT", "LỢI ÍCH / QUYỀN LỰC", "THAM GIA", "CẢI BIẾN"]
    points = [(205 + index * 302, 650 - math.sin(index * math.pi / 5) * 155) for index in range(6)]
    for index, (label, point) in enumerate(zip(labels, points)):
        p = smooth((t - index * 0.45) / 1.2)
        if p <= 0:
            continue
        draw_node(image, point, 42, TEAL if index >= 4 else AMBER, p)
        draw_text_center(ImageDraw.Draw(image), (point[0], point[1] + 82), label, F_SMALL, PAPER)
        if index:
            draw_arrow(image, points[index - 1], point, TEAL if index >= 4 else AMBER, (t - 0.7 - index * 0.4) / 1.7, 4)
    if t > 6:
        draw_arrow(image, points[3], points[1], RED, (t - 6) / 2.2, 3)
        draw_text_center(ImageDraw.Draw(image), (810, 880), "PHÂN TÍCH NGƯỢC", F_SMALL, RED)


ANIMATIONS: dict[str, Callable[[Image.Image, float], None]] = {
    "MG01_three_layers": animation_three_layers,
    "MG02_matrix": animation_matrix,
    "MG03_meta_choice": animation_framework,
    "MG04_multiple_solutions": animation_multiple_solutions,
    "MG05_technical_code": animation_technical_code,
    "MG06_nonzero_sum": animation_nonzero_sum,
    "MG07_access_participation": animation_access_participation,
    "MG08_decision_locked": animation_decision_locked,
    "MG09_participation_loop": animation_participation_loop,
    "MG10_network_transform": animation_network_transform,
    "MG11_evidence_boundary": animation_evidence_boundary,
    "MG12_five_questions": animation_five_questions,
    "MG13_efficiency_exclusion": animation_efficiency_exclusion,
    "MG14_lifecycle": animation_lifecycle,
    "MG15_five_criteria": animation_five_criteria,
    "MG16_conclusion_layers": animation_conclusion_layers,
    "MG17_method_motif": animation_method_motif,
}


@dataclass(frozen=True)
class RenderRecord:
    name: str
    path: str
    duration: float
    width: int
    height: int
    fps: int
    sha256: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render(name: str, painter: Callable[[Image.Image, float], None], output: Path, force: bool) -> None:
    if output.is_file() and not force:
        print(f"cached: {output.name}")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "rgba", "-video_size", f"{WIDTH}x{HEIGHT}",
        "-framerate", str(FPS), "-i", "-", "-an",
        "-c:v", "h264_videotoolbox", "-profile:v", "high", "-level:v", "4.2",
        "-b:v", "15M", "-maxrate", "20M", "-bufsize", "30M", "-g", "60",
        "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709",
        "-color_trc", "bt709", "-color_primaries", "bt709", "-movflags", "+faststart",
        str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    if process.stdin is None:
        raise RuntimeError("FFmpeg stdin is unavailable")
    try:
        total_frames = round(DURATION * FPS)
        for frame_index in range(total_frames):
            t = frame_index / FPS
            image = BASE.copy()
            add_moving_light(image, t)
            painter(image, t)
            process.stdin.write(image.tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise SystemExit(f"FFmpeg failed while rendering {name}")
    print(f"rendered: {output.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--only", choices=sorted(ANIMATIONS), action="append")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    selected = args.only or list(ANIMATIONS)
    records: list[RenderRecord] = []
    for name in selected:
        output = args.output_dir / f"{name}.mp4"
        render(name, ANIMATIONS[name], output, args.force)
        records.append(
            RenderRecord(name, str(output), DURATION, WIDTH, HEIGHT, FPS, sha256(output))
        )
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps([record.__dict__ for record in records], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"manifest: {args.manifest}")


if __name__ == "__main__":
    main()
