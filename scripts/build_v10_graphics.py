#!/opt/homebrew/bin/python3.13
"""Build the deterministic V10 Civic Daylight / Red Thread graphics.

The graphics are intentionally editorial rather than synthetic 3-D.  They
provide exact Vietnamese typography and concept relationships while the
documentary footage carries the human situations.  No generated text is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


W, H, FPS, DURATION = 1920, 1080, 30, 12.0
FONT = "/System/Library/Fonts/Avenir Next.ttc"

IVORY = (244, 239, 229)
PAPER = (255, 252, 246)
CHARCOAL = (36, 40, 43)
COBALT = (27, 74, 137)
VERMILION = (211, 73, 54)
SAGE = (112, 132, 117)
MIST = (215, 224, 232)
WHITE = (255, 255, 255)


def f(size: int, index: int = 7) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size=size, index=index)


F_HUGE = f(66, 0)
F_TITLE = f(43, 0)
F_KICK = f(21, 2)
F_BODY = f(30, 7)
F_BODY_B = f(30, 0)
F_SMALL = f(22, 2)
F_TINY = f(18, 5)
F_NUM = f(52, 0)


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def ease(x: float) -> float:
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a: tuple[float, float], b: tuple[float, float], p: float) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p)


def rgba(c: tuple[int, int, int], a: int = 255) -> tuple[int, int, int, int]:
    return (*c, max(0, min(255, a)))


def mix(a: tuple[int, int, int], b: tuple[int, int, int], p: float) -> tuple[int, int, int]:
    p = clamp(p)
    return tuple(round(x + (y - x) * p) for x, y in zip(a, b))


def background() -> Image.Image:
    im = Image.new("RGBA", (W, H), IVORY + (255,))
    d = ImageDraw.Draw(im)
    # Very quiet paper gradient.  It keeps the same surface in every graphic.
    for y in range(H):
        c = mix(IVORY, (232, 226, 214), y / H * 0.28)
        d.line((0, y, W, y), fill=rgba(c))
    d.rectangle((0, 0, W, 12), fill=rgba(COBALT, 255))
    # One continuous red thread is the visual spine of the film.
    d.line((76, 1006, 540, 1006), fill=rgba(VERMILION, 210), width=5)
    d.line((540, 1006, 970, 1006), fill=rgba(COBALT, 170), width=3)
    d.line((970, 1006, 1844, 1006), fill=rgba(VERMILION, 130), width=2)
    return im


BASE = background()


def txt(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, face: ImageFont.FreeTypeFont,
        fill: tuple[int, int, int] = CHARCOAL, anchor: str | None = None) -> None:
    draw.text(xy, text, font=face, fill=fill, anchor=anchor)


def center(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, face: ImageFont.FreeTypeFont,
           fill: tuple[int, int, int] = CHARCOAL) -> None:
    txt(draw, (x, y), text, face, fill, "mm")


def wrapped(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    out: list[str] = []
    line = words[0]
    for word in words[1:]:
        trial = f"{line} {word}"
        if draw.textbbox((0, 0), trial, font=face)[2] <= max_width:
            line = trial
        else:
            out.append(line)
            line = word
    out.append(line)
    return out


def header(im: Image.Image, kicker: str, title: str, progress: float) -> None:
    d = ImageDraw.Draw(im)
    d.line((76, 74, 1844, 74), fill=rgba(COBALT, 135), width=2)
    d.rectangle((76, 55, 91, 90), fill=rgba(VERMILION, 255))
    txt(d, (112, 57), kicker.upper(), F_KICK, COBALT)
    txt(d, (76, 112), title, F_TITLE, CHARCOAL)
    d.line((76, 183, 1844, 183), fill=rgba(CHARCOAL, 35), width=2)
    d.line((76, 183, 76 + 1768 * clamp(progress), 183), fill=rgba(VERMILION, 235), width=5)


def pill(im: Image.Image, box: tuple[int, int, int, int], label: str, accent: tuple[int, int, int],
         alpha: int = 245, number: str | None = None) -> None:
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 7, y0 + 8, x1 + 7, y1 + 8), radius=13, fill=rgba((0, 0, 0), 24))
    d.rounded_rectangle(box, radius=13, fill=rgba(PAPER, alpha), outline=rgba(accent, 215), width=3)
    d.rectangle((x0, y0, x0 + 9, y1), fill=rgba(accent, 255))
    if number:
        txt(d, (x0 + 29, (y0 + y1) / 2), number, F_NUM, accent, "lm")
        txt(d, (x0 + 102, (y0 + y1) / 2), label, F_SMALL, CHARCOAL, "lm")
    else:
        center(d, (x0 + x1) / 2 + 5, (y0 + y1) / 2, label, F_SMALL, CHARCOAL)


def node(im: Image.Image, p: tuple[float, float], color: tuple[int, int, int], radius: int = 18,
         active: float = 1.0) -> None:
    d = ImageDraw.Draw(im)
    x, y = p
    d.ellipse((x - radius - 9, y - radius - 9, x + radius + 9, y + radius + 9),
              fill=rgba(color, round(30 + 50 * clamp(active))))
    d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=rgba(PAPER, 255), outline=rgba(color, 255), width=5)
    d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=rgba(color, 255))


def arrow(im: Image.Image, a: tuple[float, float], b: tuple[float, float], color: tuple[int, int, int], p: float,
          width: int = 5) -> None:
    p = ease(p)
    if p <= 0:
        return
    q = lerp(a, b, p)
    d = ImageDraw.Draw(im)
    d.line((a[0], a[1], q[0], q[1]), fill=rgba(color, 220), width=width)
    if p > 0.88:
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        size = 18
        p1 = (q[0] - size * math.cos(ang - 0.55), q[1] - size * math.sin(ang - 0.55))
        p2 = (q[0] - size * math.cos(ang + 0.55), q[1] - size * math.sin(ang + 0.55))
        d.polygon((q, p1, p2), fill=rgba(color, 235))


def thread(im: Image.Image, points: list[tuple[float, float]], p: float, color: tuple[int, int, int] = VERMILION,
           width: int = 7) -> None:
    p = ease(p)
    if p <= 0:
        return
    # Draw a polyline up to the animated travel position.
    lengths = []
    total = 0.0
    for a, b in zip(points, points[1:]):
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        lengths.append(length)
        total += length
    target = total * p
    d = ImageDraw.Draw(im)
    drawn = [points[0]]
    for (a, b), length in zip(zip(points, points[1:]), lengths):
        if target <= 0:
            break
        if target >= length:
            drawn.append(b)
            target -= length
        else:
            drawn.append(lerp(a, b, target / max(length, 1e-6)))
            target = 0
            break
    if len(drawn) > 1:
        d.line(drawn, fill=rgba(color, 235), width=width, joint="curve")
        x, y = drawn[-1]
        d.ellipse((x - width, y - width, x + width, y + width), fill=rgba(color, 255))


def box(im: Image.Image, xy: tuple[int, int, int, int], fill: tuple[int, int, int] = PAPER,
        outline: tuple[int, int, int] = COBALT, alpha: int = 245) -> None:
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(xy, radius=16, fill=rgba(fill, alpha), outline=rgba(outline, 235), width=3)


def footer(im: Image.Image, left: str = "NHÓM 14", right: str = "PHƯƠNG PHÁP LUẬN · FEENBERG") -> None:
    d = ImageDraw.Draw(im)
    txt(d, (76, 1034), left, F_TINY, SAGE)
    txt(d, (1844, 1034), right, F_TINY, SAGE, "ra")


def mg01(im: Image.Image, t: float) -> None:
    header(im, "MỞ HỘP ĐEN", "KẾT QUẢ NHÌN THẤY · LỰA CHỌN KHÓ NHÌN THẤY", t / DURATION)
    d = ImageDraw.Draw(im)
    # An editorial cabinet, not a sci-fi cube.
    x0, y0, x1, y1 = 560, 350, 1360, 770
    p = ease(t / 3.0)
    d.rectangle((x0, y0, x1, y1), fill=rgba(MIST, 255), outline=rgba(COBALT, 255), width=6)
    d.line((x0, y0, x1, y0), fill=rgba(VERMILION, 255), width=12)
    center(d, 960, 555, "HỘP ĐEN", F_HUGE, COBALT)
    if t > 2.6:
        openp = ease((t - 2.6) / 2.3)
        d.rectangle((x0, y0 - 190 * openp, x1, y0 - 190 * openp + 16), fill=rgba(VERMILION, 235))
        for i, label in enumerate(("DỮ LIỆU", "TIÊU CHÍ", "NGOẠI LỆ", "QUYỀN XEM LẠI")):
            yy = 395 + i * 78
            xx = 620 + i * 26
            pill(im, (xx, yy, 1300 - i * 26, yy + 50), label, [VERMILION, COBALT, SAGE, VERMILION][i], 245)
    footer(im)


def mg02(im: Image.Image, t: float) -> None:
    header(im, "BA TẦNG PHÂN TÍCH", "SỬ DỤNG · THIẾT KẾ · QUẢN TRỊ", t / DURATION)
    labels = [("SỬ DỤNG", 360, COBALT), ("THIẾT KẾ", 545, VERMILION), ("QUẢN TRỊ", 730, SAGE)]
    d = ImageDraw.Draw(im)
    for i, (label, yy, color) in enumerate(labels):
        p = ease((t - i * 0.45) / 2.0)
        x = 250 + (1 - p) * (80 if i % 2 == 0 else -80)
        box(im, (int(x), yy, int(x + 1420), yy + 105), MIST if i == 1 else PAPER, color)
        txt(d, (x + 40, yy + 53), f"0{i + 1}", F_NUM, color, "lm")
        txt(d, (x + 150, yy + 53), label, F_BODY_B, CHARCOAL, "lm")
    thread(im, [(430, 850), (770, 850), (1060, 850), (1490, 850)], (t - 2.4) / 3.3, COBALT, 5)
    center(d, 960, 925, "LIÊN QUAN — NHƯNG KHÔNG ĐỒNG NGHĨA", F_SMALL, CHARCOAL)
    footer(im)


def mg03(im: Image.Image, t: float) -> None:
    header(im, "PHÂN BIỆT KHÁI NIỆM", "TRUY CẬP KHÔNG TỰ ĐỘNG TRỞ THÀNH THAM GIA", t / DURATION)
    d = ImageDraw.Draw(im)
    d.line((960, 260, 960, 900), fill=rgba(CHARCOAL, 45), width=2)
    center(d, 490, 270, "TRUY CẬP", F_BODY_B, COBALT)
    center(d, 1430, 270, "THAM GIA CÓ HIỆU LỰC", F_BODY_B, VERMILION)
    for side, color, x in ((0, COBALT, 490), (1, VERMILION, 1430)):
        p = ease((t - side * 0.5) / 2.2)
        box(im, (x - 220, 410, x + 220, 560), PAPER, color)
        center(d, x, 485, "DÙNG HỆ THỐNG" if side == 0 else "ĐỔI ĐƯỢC KHUNG", F_SMALL, CHARCOAL)
        for j in range(4):
            node(im, (x - 150 + j * 100, 760), color, 19, p)
        arrow(im, (x, 730), (x, 585), color, (t - 1.1 - side * .2) / 2.0, 5)
    d.line((220, 335, 760, 335), fill=rgba(COBALT, 180), width=7)
    d.line((1160, 335, 1700, 335), fill=rgba(VERMILION, 180), width=7)
    center(d, 490, 330, "QUYẾT ĐỊNH VẪN ĐÓNG", F_SMALL, COBALT)
    center(d, 1430, 330, "PHẢN HỒI ĐI TỚI TÁI THIẾT KẾ", F_SMALL, VERMILION)
    footer(im)


def matrix_base(im: Image.Image, t: float, active: int | None = None, kicker_text: str = "BẢN ĐỒ HAI TRỤC") -> None:
    header(im, kicker_text, "BỐN LẬP TRƯỜNG · KHÔNG PHẢI BỐN GIAI ĐOẠN", t / DURATION)
    d = ImageDraw.Draw(im)
    cx, cy = 960, 610
    arrow(im, (360, cy), (1560, cy), COBALT, t / 2.0, 5)
    arrow(im, (cx, 900), (cx, 300), VERMILION, t / 2.0, 5)
    txt(d, (330, 645), "TỰ TRỊ", F_SMALL, SAGE)
    txt(d, (1450, 645), "CON NGƯỜI KIỂM SOÁT", F_SMALL, SAGE)
    center(d, 1020, 292, "TRUNG TÍNH", F_SMALL, SAGE)
    center(d, 1020, 925, "MANG GIÁ TRỊ", F_SMALL, SAGE)
    cards = [
        ((470, 350, 850, 520), "TẤT ĐỊNH\nCÔNG NGHỆ", COBALT),
        ((1070, 350, 1450, 520), "THUYẾT\nCÔNG CỤ", SAGE),
        ((470, 700, 850, 870), "THUYẾT\nTHỰC CHẤT", VERMILION),
        ((1070, 700, 1450, 870), "LÝ THUYẾT PHÊ PHÁN\nCÔNG NGHỆ", VERMILION),
    ]
    for i, (xy, label, color) in enumerate(cards):
        col = color if active == i else mix(color, (160, 165, 165), .42)
        p = ease((t - i * .32) / 1.1)
        if p <= 0:
            continue
        x0, y0, x1, y1 = xy
        dy = round((1 - p) * 34)
        box(im, (x0, y0 + dy, x1, y1 + dy), MIST if active == i else PAPER, col, 255)
        for j, line in enumerate(label.split("\n")):
            center(d, (x0 + x1) / 2 + 5, (y0 + y1) / 2 + (j - (len(label.split("\n")) - 1) / 2) * 38 + dy, line, F_SMALL, CHARCOAL)
    footer(im, right="FEENBERG · BẢN ĐỒ PHÂN TÍCH")


def mg04(im: Image.Image, t: float) -> None:
    matrix_base(im, t, None, "BẢN ĐỒ LẬP TRƯỜNG")


def mg05(im: Image.Image, t: float) -> None:
    matrix_base(im, t, None, "TRỤC PHÂN TÍCH")
    d = ImageDraw.Draw(im)
    p = ease((t - 2.0) / 2.5)
    d.ellipse((925 - 30 * p, 575 - 30 * p, 995 + 30 * p, 645 + 30 * p), fill=rgba(VERMILION, 60), outline=rgba(VERMILION, 240), width=5)
    center(d, 960, 610, "?", F_HUGE, VERMILION)


def matrix_highlight(im: Image.Image, t: float, index: int, title: str, explanation: str) -> None:
    matrix_base(im, t, index, "ĐỌC BẢN ĐỒ")
    d = ImageDraw.Draw(im)
    p = ease((t - 3.2) / 2.2)
    box(im, (560, 900, 1360, 955), MIST, VERMILION if index in (2, 3) else COBALT, round(180 * p))
    center(d, 960, 928, title, F_SMALL, CHARCOAL)
    center(d, 960, 970, explanation, F_TINY, SAGE)


def mg06(im: Image.Image, t: float) -> None:
    matrix_highlight(im, t, 1, "TRUNG TÍNH + CON NGƯỜI KIỂM SOÁT", "THUYẾT CÔNG CỤ")


def mg07(im: Image.Image, t: float) -> None:
    matrix_highlight(im, t, 0, "CÔNG NGHỆ TỰ TRỊ", "TẤT ĐỊNH CÔNG NGHỆ")


def mg08(im: Image.Image, t: float) -> None:
    matrix_highlight(im, t, 2, "MANG GIÁ TRỊ + TỰ TRỊ", "THUYẾT THỰC CHẤT")


def mg09(im: Image.Image, t: float) -> None:
    matrix_highlight(im, t, 3, "MANG GIÁ TRỊ + CON NGƯỜI KIỂM SOÁT", "LÝ THUYẾT PHÊ PHÁN CÔNG NGHỆ")


def mg10(im: Image.Image, t: float) -> None:
    header(im, "LỰA CHỌN Ở CẤP KHUNG", "META-CHOICE · KHÔNG CHỈ CHỌN BÊN TRONG", t / DURATION)
    d = ImageDraw.Draw(im)
    p = ease(t / 2.2)
    for i, (x, label, color) in enumerate(((555, "KHUNG A", COBALT), (1365, "KHUNG B", VERMILION))):
        box(im, (x - 260, 350, x + 260, 700), MIST if i == 1 else PAPER, color)
        d.rectangle((x - 210, 430, x + 210, 460), fill=rgba(color, 175))
        d.rectangle((x - 160, 515, x + 160, 545), fill=rgba(SAGE, 145))
        d.rectangle((x - 110, 600, x + 110, 630), fill=rgba(color, 130))
        center(d, x, 760, label, F_BODY_B, color)
    arrow(im, (820, 540), (1100, 540), VERMILION, (t - 1.9) / 2.7, 7)
    center(d, 960, 860, "THAY ĐỔI CẤU TRÚC CỦA NHỮNG GÌ CÓ THỂ ĐƯỢC CHỌN", F_SMALL, CHARCOAL)
    footer(im)


def mg11(im: Image.Image, t: float) -> None:
    header(im, "BẤT ĐỊNH TƯƠNG ĐỐI", "RÀNG BUỘC CÓ THẬT · GIẢI PHÁP KHÔNG DUY NHẤT", t / DURATION)
    d = ImageDraw.Draw(im)
    labels = [(330, "VẬT LIỆU"), (700, "CHI PHÍ"), (1070, "HẠ TẦNG"), (1440, "NHU CẦU")]
    for x, label in labels:
        pill(im, (x - 135, 290, x + 135, 345), label, SAGE)
        d.line((x, 345, x, 800), fill=rgba(SAGE, 90), width=2)
    routes = [
        [(210, 850), (520, 760), (870, 550), (1240, 630), (1700, 430)],
        [(210, 850), (520, 800), (870, 690), (1240, 760), (1700, 650)],
        [(210, 850), (520, 830), (870, 800), (1240, 820), (1700, 850)],
    ]
    for i, points in enumerate(routes):
        thread(im, points, (t - 1.0 - i * .7) / 4.3, [COBALT, VERMILION, SAGE][i], 6)
        if t > 4.5 + i * .5:
            node(im, points[-1], [COBALT, VERMILION, SAGE][i], 18, 1)
    center(d, 960, 930, "NHIỀU ĐƯỜNG KHẢ THI TRONG PHẠM VI RÀNG BUỘC", F_SMALL, CHARCOAL)
    footer(im)


def mg12(im: Image.Image, t: float) -> None:
    header(im, "MÃ KỸ THUẬT · TECHNICAL CODE", "GIÁ TRỊ XÃ HỘI ĐI VÀO CẤU TRÚC THIẾT KẾ", t / DURATION)
    d = ImageDraw.Draw(im)
    labels = [("CHÂN TRỜI XÃ HỘI", VERMILION), ("PHÁN ĐOÁN · GIẢ ĐỊNH", SAGE), ("TIÊU CHUẨN · THỦ TỤC", COBALT), ("THAM SỐ THIẾT KẾ", VERMILION)]
    for i, (label, color) in enumerate(labels):
        p = ease((t - i * .65) / 1.6)
        x0 = 310 + (1 - p) * (100 if i % 2 == 0 else -100)
        y = 285 + i * 145
        pill(im, (round(x0), y, round(x0 + 1300), y + 88), label, color, 250)
        if i:
            arrow(im, (960, y - 44), (960, y - 4), color, p, 4)
    thread(im, [(960, 260), (960, 820)], (t - 1.8) / 4.5, VERMILION, 6)
    center(d, 960, 930, "KHÔNG PHẢI MÃ NGUỒN · KHÔNG PHẢI ÂM MƯU BÍ MẬT", F_SMALL, CHARCOAL)
    footer(im)


def mg13(im: Image.Image, t: float) -> None:
    header(im, "DÂN CHỦ HÓA CÔNG NGHỆ", "AI ĐƯỢC THAM GIA VÀO VIỆC ĐỊNH HÌNH?", t / DURATION)
    d = ImageDraw.Draw(im)
    center(d, 960, 520, "THIẾT KẾ", F_HUGE, COBALT)
    positions = [(360, 780), (650, 850), (960, 900), (1270, 850), (1560, 780)]
    for i, p in enumerate(positions):
        node(im, p, VERMILION if i in (1, 2, 3) else COBALT, 23, ease((t - i * .25) / 1.7))
    for i, p in enumerate(positions):
        arrow(im, p, (960, 590), VERMILION if i in (1, 2, 3) else COBALT, (t - 1.4 - i * .25) / 2.3, 4)
    center(d, 960, 950, "KINH NGHIỆM → THIẾT KẾ → QUẢN TRỊ", F_SMALL, CHARCOAL)
    footer(im)


def mg14(im: Image.Image, t: float) -> None:
    header(im, "LÝ TÍNH HÓA DÂN CHỦ", "PHẢN HỒI PHẢI ĐI ĐẾN QUYẾT ĐỊNH", t / DURATION)
    d = ImageDraw.Draw(im)
    center(d, 960, 540, "THIẾT KẾ", F_HUGE, COBALT)
    pts = [(960, 300), (1450, 540), (960, 780), (470, 540)]
    labels = ["ĐẶT VẤN ĐỀ", "THỬ NGHIỆM", "THEO DÕI", "PHẢN BIỆN"]
    for i, (p, label) in enumerate(zip(pts, labels)):
        node(im, p, VERMILION if i == 3 else COBALT, 24, ease((t - i * .45) / 1.4))
        center(d, p[0], p[1] + 64, label, F_SMALL, CHARCOAL)
        arrow(im, p, pts[(i + 1) % 4], VERMILION, (t - 1.2 - i * .42) / 2.2, 5)
    thread(im, [pts[3], pts[0], pts[1], pts[2], pts[3]], (t - 3.0) / 3.6, VERMILION, 7)
    footer(im)


def mg15(im: Image.Image, t: float) -> None:
    header(im, "THAM GIA CÓ HIỆU LỰC", "ĐƯỢC NGHE CHƯA CÓ NGHĨA CÓ THỂ THAY ĐỔI", t / DURATION)
    d = ImageDraw.Draw(im)
    box(im, (190, 370, 770, 710), PAPER, COBALT)
    box(im, (1150, 370, 1730, 710), PAPER, VERMILION)
    center(d, 480, 440, "PHẢN HỒI", F_BODY_B, COBALT)
    center(d, 1440, 440, "THIẾT KẾ ĐÃ KHÓA", F_BODY_B, VERMILION)
    for x in (340, 480, 620):
        node(im, (x, 600), COBALT, 21, 1)
    d.rectangle((920, 285, 1000, 805), fill=rgba(VERMILION, 235))
    center(d, 960, 850, "KHÔNG CÓ CƠ CHẾ CHUYỂN HÓA", F_TINY, VERMILION)
    arrow(im, (770, 540), (920, 540), COBALT, (t - 1.8) / 2.0, 6)
    center(d, 960, 925, "THAM VẤN HÌNH THỨC", F_SMALL, CHARCOAL)
    footer(im)


def mg16(im: Image.Image, t: float) -> None:
    header(im, "QUỸ ĐẠO CỦA MẠNG", "TỪ PHÂN PHỐI DỮ LIỆU ĐẾN GIAO TIẾP GIỮA NGƯỜI VỚI NGƯỜI", t / DURATION)
    d = ImageDraw.Draw(im)
    hub = (960, 520)
    terminals = [(430, 340), (430, 760), (780, 870), (1140, 870), (1490, 760), (1490, 340)]
    box(im, (760, 430, 1160, 625), MIST, COBALT)
    center(d, 960, 525, "TRUNG TÂM", F_BODY_B, CHARCOAL)
    for i, p in enumerate(terminals):
        node(im, p, COBALT, 25, .9)
        arrow(im, hub, p, COBALT, (t - i * .2) / 2.5, 4)
    if t > 4.0:
        for a, b in zip(terminals, terminals[1:] + terminals[:1]):
            arrow(im, a, b, VERMILION, (t - 4.0) / 3.3, 3)
    center(d, 960, 950, "GIAO TIẾP TRỞ THÀNH CHỨC NĂNG CHUẨN", F_SMALL, CHARCOAL)
    footer(im)


def mg17(im: Image.Image, t: float) -> None:
    header(im, "GIỚI HẠN BẰNG CHỨNG", "DỮ KIỆN NGUỒN KHÔNG CHO PHÉP SUY DIỄN KẾT QUẢ", t / DURATION)
    d = ImageDraw.Draw(im)
    box(im, (150, 300, 1000, 870), PAPER, COBALT)
    txt(d, (210, 350), "ĐÃ XÁC NHẬN", F_BODY_B, COBALT)
    for i, label in enumerate(("CỘNG ĐỒNG LẬP DANH SÁCH", "DANH SÁCH ĐƯỢC TRÌNH", "HỆ THỐNG ĐƯỢC CHIẾM DỤNG")):
        pill(im, (220, 450 + i * 125, 930, 530 + i * 125), label, COBALT)
        if i < 2:
            arrow(im, (575, 530 + i * 125), (575, 575 + i * 125), COBALT, (t - 1.2 - i * .4) / 1.3, 4)
    d.line((1080, 290, 1080, 875), fill=rgba(VERMILION, 220), width=5)
    center(d, 1080, 920, "RANH GIỚI SUY LUẬN", F_SMALL, VERMILION)
    for i, label in enumerate(("ĐƯỢC CHẤP NHẬN?", "ĐỔI CHÍNH SÁCH?", "CẢI THIỆN ĐIỀU TRỊ?")):
        pill(im, (1200, 380 + i * 160, 1750, 480 + i * 160), label, VERMILION, 235)
        center(d, 1140, 430 + i * 160, "?", F_NUM, VERMILION)
    footer(im)


def mg18(im: Image.Image, t: float) -> None:
    header(im, "BA LỚP ĐỌC MỘT CASE", "DỮ KIỆN · DIỄN GIẢI · PHÂN TÍCH THEO FEENBERG", t / DURATION)
    d = ImageDraw.Draw(im)
    labels = [("DỮ KIỆN", "Điều nguồn trực tiếp ghi nhận", COBALT),
              ("DIỄN GIẢI", "Cách nhóm nối dữ kiện với câu hỏi", SAGE),
              ("PHÂN TÍCH", "Khái niệm dùng để đọc quan hệ thiết kế–quyền lực", VERMILION)]
    for i, (a, b, color) in enumerate(labels):
        p = ease((t - i * .65) / 1.7)
        x = 230 + (1 - p) * 180
        y = 330 + i * 190
        box(im, (round(x), y, round(x + 1460), y + 125), PAPER, color)
        txt(d, (x + 42, y + 35), a, F_BODY_B, color)
        txt(d, (x + 42, y + 82), b, F_SMALL, CHARCOAL)
    thread(im, [(360, 880), (740, 880), (1120, 880), (1540, 880)], (t - 2.8) / 3.0, VERMILION, 6)
    footer(im)


def mg19(im: Image.Image, t: float) -> None:
    header(im, "MỞ HỘP ĐEN", "NĂM CÂU HỎI ĐỂ ĐỌC MỘT HỆ THỐNG", t / DURATION)
    d = ImageDraw.Draw(im)
    labels = ["AI ĐỊNH NGHĨA VẤN ĐỀ?", "GIÁ TRỊ NÀO THÀNH MẶC ĐỊNH?", "AI CHỊU TÁC ĐỘNG NHƯNG VẮNG MẶT?", "SỰ THAM GIA CÓ QUYỀN GÌ?", "PHẢN HỒI CÓ ĐI TỚI TÁI THIẾT KẾ?"]
    for i, label in enumerate(labels):
        p = ease((t - i * .35) / 1.35)
        x = 240 + (1 - p) * (80 if i % 2 == 0 else -80)
        y = 270 + i * 125
        box(im, (round(x), y, round(x + 1440), y + 88), MIST if i == min(4, int(t / 2.1)) else PAPER,
            VERMILION if i == min(4, int(t / 2.1)) else COBALT)
        txt(d, (x + 40, y + 44), str(i + 1), F_NUM, VERMILION if i == min(4, int(t / 2.1)) else COBALT, "lm")
        txt(d, (x + 120, y + 44), label, F_SMALL, CHARCOAL, "lm")
    footer(im)


def mg20(im: Image.Image, t: float) -> None:
    header(im, "TỪ GIÁ TRỊ ĐẾN THAM SỐ", "KHI MỘT ƯU TIÊN XÃ HỘI TRỞ THÀNH LỰA CHỌN KỸ THUẬT", t / DURATION)
    d = ImageDraw.Draw(im)
    pts = [(330, 570), (760, 570), (1190, 570), (1600, 570)]
    labels = ["GIÁ TRỊ", "TIÊU CHÍ", "THAM SỐ", "THIẾT BỊ"]
    colors = [VERMILION, SAGE, COBALT, VERMILION]
    for i, (p, label, color) in enumerate(zip(pts, labels, colors)):
        node(im, p, color, 38, ease((t - i * .5) / 1.4))
        center(d, p[0], p[1] + 85, label, F_BODY_B, CHARCOAL)
        if i:
            arrow(im, pts[i - 1], p, color, (t - 1.0 - i * .4) / 1.8, 5)
    center(d, 960, 850, "ĐƯỜNG ĐI CỦA LỰA CHỌN", F_SMALL, CHARCOAL)
    footer(im)


def mg21(im: Image.Image, t: float) -> None:
    header(im, "TRUY VẾT PHẢN HỒI", "Ý KIẾN CHỈ CÓ SỨC NẶNG KHI CÓ DẤU VẾT XỬ LÝ", t / DURATION)
    d = ImageDraw.Draw(im)
    cols = [(240, "NGƯỜI NÓI"), (610, "VẤN ĐỀ"), (980, "QUYẾT ĐỊNH"), (1350, "THAY ĐỔI")]
    for i, (x, label) in enumerate(cols):
        pill(im, (x, 300, x + 300, 360), label, [VERMILION, SAGE, COBALT, VERMILION][i])
        for r in range(3):
            box(im, (x, 420 + r * 100, x + 300, 485 + r * 100), MIST if r == i % 3 else PAPER, [VERMILION, SAGE, COBALT, VERMILION][i], 230)
    for i in range(3):
        arrow(im, (540, 450 + i * 100), (610, 450 + i * 100), VERMILION, (t - 1.0 - i * .2) / 1.4, 4)
        arrow(im, (910, 450 + i * 100), (980, 450 + i * 100), COBALT, (t - 1.7 - i * .2) / 1.4, 4)
        arrow(im, (1280, 450 + i * 100), (1350, 450 + i * 100), VERMILION, (t - 2.4 - i * .2) / 1.4, 4)
    center(d, 960, 860, "AI · ĐIỀU GÌ · VÌ SAO · THAY ĐỔI Ở ĐÂU?", F_SMALL, CHARCOAL)
    footer(im)


def mg22(im: Image.Image, t: float) -> None:
    header(im, "ĐỀ XUẤT CỦA NHÓM 14", "NĂM ĐIỀU KIỆN ĐỂ THAM GIA CÓ HIỆU LỰC", t / DURATION)
    d = ImageDraw.Draw(im)
    labels = ["SỚM", "CÓ THÔNG TIN", "CÓ ĐẠI DIỆN", "CÓ QUYỀN PHẢN BIỆN", "CÓ DẤU VẾT XỬ LÝ"]
    for i, label in enumerate(labels):
        p = ease((t - i * .45) / 1.4)
        y = 285 + i * 125
        x = 360 + (1 - p) * (90 if i % 2 == 0 else -90)
        pill(im, (round(x), y, round(x + 1200), y + 86), label, VERMILION if i >= 2 else COBALT, 250, str(i + 1))
    footer(im)


def mg23(im: Image.Image, t: float) -> None:
    header(im, "CÂU HỎI TRUNG TÂM", "CÔNG NGHỆ CÓ THỰC SỰ TRUNG LẬP?", t / DURATION)
    d = ImageDraw.Draw(im)
    p = ease(t / 3.0)
    d.line((300, 700, 1620, 700), fill=rgba(COBALT, 150), width=4)
    thread(im, [(320, 700), (650, 510), (970, 650), (1320, 420), (1600, 700)], p, VERMILION, 9)
    center(d, 960, 460, "?", f(150, 0), VERMILION)
    center(d, 960, 860, "GIÁ TRỊ · LỢI ÍCH · QUYỀN LỰC", F_BODY_B, CHARCOAL)
    footer(im)


def mg24(im: Image.Image, t: float) -> None:
    header(im, "KẾT LUẬN CÓ ĐIỀU KIỆN", "KHÔNG TRỐNG RỖNG · KHÔNG ĐỊNH MỆNH", t / DURATION)
    d = ImageDraw.Draw(im)
    labels = ["ĐỊNH NGHĨA VẤN ĐỀ", "TIÊU CHUẨN", "THỦ TỤC", "CẤU TRÚC THIẾT KẾ"]
    for i, label in enumerate(labels):
        p = ease((t - i * .55) / 1.7)
        y = 320 + i * 125
        x = 360 + (i - 1.5) * 18
        box(im, (round(x), y, round(x + 1200), y + 80), MIST if i == 3 else PAPER, VERMILION if i == 3 else COBALT)
        center(d, x + 600, y + 40, label, F_SMALL, CHARCOAL)
    thread(im, [(280, 860), (620, 800), (960, 830), (1300, 760), (1640, 820)], ease((t - 2) / 4.0), VERMILION, 7)
    footer(im)


def mg25(im: Image.Image, t: float) -> None:
    header(im, "KHẢ NĂNG CẢI BIẾN", "THIẾT KẾ MỞ RA NHIỀU ĐƯỜNG ĐI", t / DURATION)
    d = ImageDraw.Draw(im)
    start = (960, 820)
    ends = [(350, 350), (720, 280), (1120, 280), (1540, 350)]
    for i, end in enumerate(ends):
        points = [start, (start[0] + (i - 1.5) * 130, 620), (end[0], 480), end]
        thread(im, points, (t - i * .45) / 4.0, [COBALT, VERMILION, SAGE, COBALT][i], 7)
        if t > 5 + i * .3:
            node(im, end, [COBALT, VERMILION, SAGE, COBALT][i], 22, 1)
    center(d, 960, 920, "RÀNG BUỘC KỸ THUẬT · KHẢ NĂNG XÃ HỘI", F_SMALL, CHARCOAL)
    footer(im)


def mg26(im: Image.Image, t: float) -> None:
    header(im, "BÀI HỌC PHƯƠNG PHÁP LUẬN", "LẦN NGƯỢC TỪ KẾT QUẢ · MỞ KHẢ NĂNG CẢI BIẾN", t / DURATION)
    d = ImageDraw.Draw(im)
    labels = ["KẾT QUẢ", "THIẾT KẾ", "MÃ KỸ THUẬT", "LỢI ÍCH / QUYỀN LỰC", "THAM GIA", "CẢI BIẾN"]
    points = [(180 + i * 310, 650 - math.sin(i * math.pi / 5) * 145) for i in range(6)]
    for i, (label, p) in enumerate(zip(labels, points)):
        if i:
            arrow(im, points[i - 1], p, VERMILION if i >= 4 else COBALT, (t - .7 - i * .35) / 1.7, 5)
        node(im, p, VERMILION if i >= 4 else COBALT, 24, ease((t - i * .42) / 1.2))
        center(d, p[0], p[1] + 66, label, F_TINY, CHARCOAL)
    thread(im, [points[3], points[1], points[4], points[5]], (t - 5.0) / 3.0, VERMILION, 7)
    center(d, 960, 920, "PHÂN TÍCH NGƯỢC", F_SMALL, VERMILION)
    footer(im)


ANIM: dict[str, Callable[[Image.Image, float], None]] = {
    "MG01_open_black_box": mg01,
    "MG02_three_layers": mg02,
    "MG03_access_participation": mg03,
    "MG04_matrix_intro": mg04,
    "MG05_matrix_axes": mg05,
    "MG06_matrix_instrumentalism": mg06,
    "MG07_matrix_determinism": mg07,
    "MG08_matrix_substantivism": mg08,
    "MG09_matrix_critical_theory": mg09,
    "MG10_meta_choice": mg10,
    "MG11_relative_underdetermination": mg11,
    "MG12_technical_code": mg12,
    "MG13_democratization_title": mg13,
    "MG14_democratic_rationalization": mg14,
    "MG15_effective_feedback": mg15,
    "MG16_network_transformation": mg16,
    "MG17_evidence_boundary": mg17,
    "MG18_three_analytic_layers": mg18,
    "MG19_five_questions": mg19,
    "MG20_value_to_parameter": mg20,
    "MG21_traceable_feedback": mg21,
    "MG22_five_conditions": mg22,
    "MG23_central_question": mg23,
    "MG24_conclusion_layers": mg24,
    "MG25_open_paths": mg25,
    "MG26_methodological_motif": mg26,
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def render(name: str, painter: Callable[[Image.Image, float], None], out: Path, force: bool) -> None:
    if out.exists() and not force:
        print(f"cached {out.name}", flush=True)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "rgba", "-video_size", f"{W}x{H}",
        "-framerate", str(FPS), "-i", "-", "-an",
        "-c:v", "h264_videotoolbox", "-profile:v", "high", "-level:v", "4.2",
        "-b:v", "14M", "-maxrate", "18M", "-bufsize", "28M", "-g", "60",
        "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709",
        "-color_trc", "bt709", "-color_primaries", "bt709", "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(round(DURATION * FPS)):
            im = BASE.copy()
            painter(im, i / FPS)
            proc.stdin.write(im.tobytes())
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {name}")
    print(f"rendered {out.name}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--only", action="append", choices=sorted(ANIM))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    selected = args.only or list(ANIM)
    records = []
    for name in selected:
        out = args.output_dir / f"{name}.mp4"
        render(name, ANIM[name], out, args.force)
        records.append({"name": name, "path": str(out), "duration": DURATION, "width": W, "height": H,
                        "fps": FPS, "palette": "Civic Daylight / Red Thread", "sha256": sha(out)})
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest {args.manifest}")


if __name__ == "__main__":
    main()
