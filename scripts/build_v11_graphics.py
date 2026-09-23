#!/opt/homebrew/bin/python3.13
"""Render the corrected V11 Civic Daylight motion-graphic set.

V10 remains an immutable fallback.  This module reuses its already audited
drawing primitives while replacing the elements called out in the V11 QA:
the rule crossing the title area, decorative question-mark glyphs, and the
crowded evidence-boundary layout.  Arrows that explain relationships are
drawn as vector shapes, never as Unicode arrow glyphs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

import build_v10_graphics as v10


def header(im: Image.Image, kicker: str, title: str, progress: float) -> None:
    """Draw a title-safe header without a rule crossing the kicker text."""
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, round(v10.W * v10.clamp(progress)), 12), fill=v10.rgba(v10.VERMILION, 255))
    # The former cobalt rail sat at y=74, directly inside the kicker glyph
    # bounds (roughly y=57..83).  Keep the red section marker as the visual
    # anchor and remove that rail entirely so no Vietnamese title can ever be
    # struck through, regardless of its width.
    d.rectangle((76, 55, 91, 90), fill=v10.rgba(v10.VERMILION, 255))
    v10.txt(d, (112, 57), kicker.upper(), v10.F_KICK, v10.COBALT)
    v10.txt(d, (76, 112), title, v10.F_TITLE, v10.CHARCOAL)


def mg05(im: Image.Image, t: float) -> None:
    """Explain two independent axes without an ambiguous centre glyph."""
    v10.matrix_base(im, t, None, "TRỤC PHÂN TÍCH")
    d = ImageDraw.Draw(im)
    p = v10.ease((t - 1.8) / 2.2)
    radius = round(37 * p)
    if radius > 0:
        d.ellipse(
            (960 - radius, 610 - radius, 960 + radius, 610 + radius),
            fill=v10.rgba(v10.PAPER, 248),
            outline=v10.rgba(v10.VERMILION, 240),
            width=5,
        )
        d.line((960 - radius + 11, 610, 960 + radius - 11, 610), fill=v10.rgba(v10.COBALT, 235), width=5)
        d.line((960, 610 - radius + 11, 960, 610 + radius - 11), fill=v10.rgba(v10.VERMILION, 235), width=5)
        for x, y, color in (
            (960 - radius, 610, v10.COBALT),
            (960 + radius, 610, v10.COBALT),
            (960, 610 - radius, v10.VERMILION),
            (960, 610 + radius, v10.VERMILION),
        ):
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=v10.rgba(color, 255))


def mg13(im: Image.Image, t: float) -> None:
    """Show participation reaching design and governance with shape arrows."""
    header(im, "DÂN CHỦ HÓA CÔNG NGHỆ", "AI ĐƯỢC THAM GIA VÀO VIỆC ĐỊNH HÌNH?", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    v10.center(d, 960, 475, "THIẾT KẾ", v10.F_HUGE, v10.COBALT)
    positions = [(350, 725), (650, 800), (960, 835), (1270, 800), (1570, 725)]
    for i, point in enumerate(positions):
        color = v10.VERMILION if i in (1, 2, 3) else v10.COBALT
        v10.node(im, point, color, 23, v10.ease((t - i * 0.25) / 1.7))
        v10.arrow(im, point, (960, 545), color, (t - 1.3 - i * 0.22) / 2.2, 4)

    labels = [(535, "KINH NGHIỆM"), (960, "THIẾT KẾ"), (1385, "QUẢN TRỊ")]
    for x, label in labels:
        v10.pill(im, (x - 155, 895, x + 155, 955), label, v10.VERMILION if x == 960 else v10.COBALT)
    v10.arrow(im, (690, 925), (805, 925), v10.VERMILION, (t - 3.2) / 1.4, 5)
    v10.arrow(im, (1115, 925), (1230, 925), v10.VERMILION, (t - 3.8) / 1.4, 5)
    v10.footer(im)


def mg17(im: Image.Image, t: float) -> None:
    """Separate verified facts from unverified outcomes without '?' icons."""
    header(im, "GIỚI HẠN BẰNG CHỨNG", "CHỈ KẾT LUẬN ĐẾN MỨC NGUỒN CHO PHÉP", t / v10.DURATION)
    d = ImageDraw.Draw(im)

    v10.box(im, (130, 285, 1005, 865), v10.PAPER, v10.COBALT)
    v10.txt(d, (190, 335), "ĐÃ XÁC NHẬN", v10.F_BODY_B, v10.COBALT)
    confirmed = ("CỘNG ĐỒNG LẬP DANH SÁCH", "DANH SÁCH ĐƯỢC GỬI", "TIẾNG NÓI TẬP THỂ HÌNH THÀNH")
    for i, label in enumerate(confirmed):
        y = 435 + i * 125
        v10.pill(im, (200, y, 935, y + 80), label, v10.COBALT)
        if i < len(confirmed) - 1:
            v10.arrow(im, (568, y + 80), (568, y + 117), v10.COBALT, (t - 1.0 - i * 0.45) / 1.25, 4)

    # The border is a semantic boundary, kept well away from both text areas.
    d.line((1080, 285, 1080, 865), fill=v10.rgba(v10.VERMILION, 225), width=5)
    v10.center(d, 1080, 915, "RANH GIỚI SUY LUẬN", v10.F_SMALL, v10.VERMILION)

    v10.txt(d, (1180, 335), "CHƯA ĐƯỢC XÁC NHẬN", v10.F_BODY_B, v10.VERMILION)
    unverified = ("DANH SÁCH ĐƯỢC CHẤP NHẬN", "CHÍNH SÁCH ĐƯỢC THAY ĐỔI", "ĐIỀU TRỊ ĐƯỢC CẢI THIỆN")
    for i, label in enumerate(unverified):
        y = 435 + i * 125
        v10.pill(im, (1165, y, 1770, y + 80), label, v10.VERMILION, 235)
        # A short stop rail communicates "do not infer" without typography.
        d.line((1105, y + 40, 1148, y + 40), fill=v10.rgba(v10.VERMILION, 235), width=7)
        d.line((1148, y + 21, 1148, y + 59), fill=v10.rgba(v10.VERMILION, 235), width=7)
    v10.footer(im)


def mg23(im: Image.Image, t: float) -> None:
    """Return to the central question through the film's red-thread motif."""
    header(im, "CÂU HỎI TRUNG TÂM", "CÔNG NGHỆ CÓ THỰC SỰ TRUNG LẬP?", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    p = v10.ease(t / 3.0)
    v10.box(im, (600, 310, 1320, 755), v10.PAPER, v10.COBALT)
    d.rectangle((600, 310, 960, 755), fill=v10.rgba(v10.MIST, 210))
    d.line((960, 310, 960, 755), fill=v10.rgba(v10.VERMILION, 235), width=7)
    v10.center(d, 780, 530, "KẾT QUẢ", v10.F_BODY_B, v10.COBALT)
    v10.center(d, 1140, 530, "LỰA CHỌN", v10.F_BODY_B, v10.VERMILION)
    v10.thread(im, [(270, 820), (600, 660), (960, 660), (1320, 475), (1650, 650)], p, v10.VERMILION, 9)
    for x, label, color in (
        (515, "GIÁ TRỊ", v10.VERMILION),
        (960, "LỢI ÍCH", v10.COBALT),
        (1405, "QUYỀN LỰC", v10.VERMILION),
    ):
        v10.pill(im, (x - 145, 850, x + 145, 910), label, color)
    v10.footer(im)


def mg27(im: Image.Image, t: float) -> None:
    """Mark the cold-open clinic as the group's hypothetical example."""
    header(im, "RANH GIỚI BẰNG CHỨNG", "TÌNH HUỐNG GIẢ ĐỊNH CỦA NHÓM 14", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    left = (150, 330, 840, 795)
    right = (1080, 330, 1770, 795)
    v10.box(im, left, v10.PAPER, v10.COBALT)
    v10.box(im, right, v10.PAPER, v10.VERMILION)
    v10.center(d, 495, 405, "DÙNG ĐỂ MINH HỌA", v10.F_BODY_B, v10.COBALT)
    for i, label in enumerate(("SỬ DỤNG", "THIẾT KẾ", "QUẢN TRỊ")):
        p = v10.ease((t - i * 0.35) / 1.5)
        if p > 0:
            v10.pill(im, (245, 500 + i * 82, 745, 560 + i * 82), label, v10.COBALT, round(150 + 100 * p))
    d.line((960, 290, 960, 845), fill=v10.rgba(v10.VERMILION, 220), width=6)
    d.line((934, 545, 986, 545), fill=v10.rgba(v10.VERMILION, 245), width=8)
    v10.center(d, 1425, 430, "KHÔNG GÁN THÀNH", v10.F_BODY_B, v10.VERMILION)
    v10.center(d, 1425, 545, "CASE DO FEENBERG", v10.F_BODY_B, v10.CHARCOAL)
    v10.center(d, 1425, 640, "NGHIÊN CỨU", v10.F_BODY_B, v10.CHARCOAL)
    v10.center(d, 960, 910, "MINH HỌA  ≠  DỮ KIỆN LỊCH SỬ", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg28(im: Image.Image, t: float) -> None:
    """Keep access and effective participation visibly distinct."""
    header(im, "DÂN CHỦ HÓA CÔNG NGHỆ", "TRUY CẬP CHƯA PHẢI QUYỀN ĐỊNH HÌNH", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    v10.box(im, (150, 310, 790, 790), v10.PAPER, v10.COBALT)
    v10.box(im, (1130, 310, 1770, 790), v10.PAPER, v10.VERMILION)
    v10.center(d, 470, 395, "TRUY CẬP", v10.F_BODY_B, v10.COBALT)
    v10.center(d, 1450, 395, "THAM GIA", v10.F_BODY_B, v10.VERMILION)
    for i in range(5):
        v10.node(im, (270 + i * 100, 585), v10.COBALT, 19, v10.ease((t - i * .2) / 1.4))
    v10.pill(im, (280, 675, 660, 735), "DÙNG HỆ THỐNG", v10.COBALT)
    points = [(1245, 660), (1450, 525), (1655, 660)]
    labels = ("KINH NGHIỆM", "QUYẾT ĐỊNH", "TÁI THIẾT KẾ")
    for i, (point, label) in enumerate(zip(points, labels)):
        v10.node(im, point, v10.VERMILION if i else v10.COBALT, 24, v10.ease((t - i * .35) / 1.5))
        v10.center(d, point[0], point[1] + 65, label, v10.F_TINY, v10.CHARCOAL)
        if i:
            v10.arrow(im, points[i - 1], point, v10.VERMILION, (t - 1.2 - i * .35) / 1.7, 5)
    d.line((910, 470, 1010, 650), fill=v10.rgba(v10.VERMILION, 245), width=9)
    v10.center(d, 960, 875, "DÙNG ĐƯỢC  ≠  ĐỔI ĐƯỢC KHUNG", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg29(im: Image.Image, t: float) -> None:
    """Show ambivalence as constrained plurality, not arbitrary choice."""
    header(im, "TÍNH NƯỚC ĐÔI · AMBIVALENT", "NHIỀU HƯỚNG PHÁT TRIỂN KHẢ THI", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    constraints = ((360, "VẬT LIỆU"), (690, "CHI PHÍ"), (1020, "HẠ TẦNG"), (1350, "TRI THỨC"))
    for x, label in constraints:
        v10.pill(im, (x - 130, 275, x + 130, 335), label, v10.SAGE)
        d.line((x, 345, x, 820), fill=v10.rgba(v10.SAGE, 75), width=2)
    start = (250, 805)
    routes = [
        [start, (600, 690), (910, 465), (1300, 520), (1670, 345)],
        [start, (600, 760), (930, 650), (1320, 720), (1670, 610)],
        [start, (600, 830), (950, 825), (1320, 845), (1670, 820)],
    ]
    for i, route in enumerate(routes):
        v10.thread(im, route, (t - .45 - i * .65) / 4.6, (v10.COBALT, v10.VERMILION, v10.SAGE)[i], 7)
    v10.pill(im, (250, 880, 735, 942), "KHÔNG ĐỊNH SẴN", v10.VERMILION)
    v10.pill(im, (1185, 880, 1670, 942), "KHÔNG TÙY TIỆN", v10.COBALT)
    v10.footer(im)


def mg30(im: Image.Image, t: float) -> None:
    """Visualize the verified move from individual exchanges to a list."""
    header(im, "CASE ALS · DỮ KIỆN", "TỪ TRAO ĐỔI ĐẾN ƯU TIÊN CHUNG", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    people = [(260, 390), (260, 560), (260, 730)]
    for i, point in enumerate(people):
        v10.node(im, point, v10.COBALT, 23, v10.ease((t - i * .3) / 1.5))
        v10.box(im, (340, point[1] - 38, 760, point[1] + 38), v10.PAPER, v10.COBALT, 235)
        d.line((380, point[1], 690, point[1]), fill=v10.rgba(v10.COBALT, 105), width=5)
        v10.arrow(im, (760, point[1]), (900, 560), v10.VERMILION, (t - 1.2 - i * .25) / 2.0, 5)
    v10.box(im, (900, 355, 1330, 765), v10.MIST, v10.VERMILION)
    v10.center(d, 1115, 420, "DANH SÁCH", v10.F_BODY_B, v10.VERMILION)
    v10.center(d, 1115, 465, "ƯU TIÊN", v10.F_BODY_B, v10.VERMILION)
    for i in range(4):
        y = 545 + i * 48
        d.ellipse((965, y - 6, 977, y + 6), fill=v10.rgba(v10.VERMILION, 255))
        d.line((1000, y, 1240, y), fill=v10.rgba(v10.CHARCOAL, 110), width=4)
    v10.arrow(im, (1330, 560), (1510, 560), v10.VERMILION, (t - 4.0) / 2.2, 7)
    v10.box(im, (1510, 430, 1770, 690), v10.PAPER, v10.COBALT)
    v10.center(d, 1640, 540, "TỔ CHỨC", v10.F_SMALL, v10.COBALT)
    v10.center(d, 1640, 595, "LIÊN QUAN", v10.F_SMALL, v10.CHARCOAL)
    v10.center(d, 960, 895, "CÁ NHÂN  →  LỢI ÍCH ĐƯỢC PHÁT BIỂU TẬP THỂ", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg31(im: Image.Image, t: float) -> None:
    """Connect lived experience to an actionable redesign path."""
    header(im, "SỰ THAM GIA CÓ CƠ CHẾ", "KINH NGHIỆM ĐI TỚI THAY ĐỔI THẾ NÀO", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    labels = ["KINH NGHIỆM SỐNG", "PHẢN BIỆN", "TỔ CHỨC TẬP THỂ", "YÊU CẦU THIẾT KẾ", "SỬA QUY TẮC"]
    points = [(235 + i * 360, 560 + (70 if i % 2 else -55)) for i in range(5)]
    for i, (point, label) in enumerate(zip(points, labels)):
        active = v10.ease((t - i * 1.15) / 1.8)
        color = v10.VERMILION if i >= 3 else v10.COBALT
        v10.node(im, point, color, 27, active)
        v10.pill(im, (point[0] - 155, point[1] + 75, point[0] + 155, point[1] + 137), label, color)
        if i:
            v10.arrow(im, points[i - 1], point, color, (t - .6 - i * 1.05) / 1.8, 6)
    v10.thread(im, points, (t - 5.8) / 4.0, v10.VERMILION, 8)
    v10.center(d, 960, 875, "HIỆN DIỆN CHỈ LÀ BƯỚC ĐẦU · QUYỀN THAY ĐỔI MỚI LÀ ĐÍCH", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg32(im: Image.Image, t: float) -> None:
    """Trace an apparently finished design backwards to its choices."""
    header(im, "PHÂN TÍCH PHẢ HỆ THIẾT KẾ", "LẦN NGƯỢC TỪ KẾT QUẢ ĐÃ ỔN ĐỊNH", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    labels = ["KẾT QUẢ", "THÔNG SỐ", "TIÊU CHÍ", "PHƯƠNG ÁN", "ĐỊNH NGHĨA VẤN ĐỀ"]
    colors = [v10.COBALT, v10.COBALT, v10.SAGE, v10.VERMILION, v10.VERMILION]
    for i, (label, color) in enumerate(zip(labels, colors)):
        x = 1490 - i * 315
        y = 475 + (95 if i % 2 else 0)
        p = v10.ease((t - i * .65) / 1.7)
        v10.node(im, (x, y), color, 28, p)
        v10.pill(im, (x - 145, y + 75, x + 145, y + 137), label, color)
        if i:
            prev_x = 1490 - (i - 1) * 315
            prev_y = 475 + (95 if (i - 1) % 2 else 0)
            v10.arrow(im, (prev_x, prev_y), (x, y), color, (t - .7 - i * .6) / 1.8, 6)
    v10.center(d, 960, 860, "CÁI TRÔNG NHƯ TẤT YẾU TỪNG LÀ MỘT CHUỖI LỰA CHỌN", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg33(im: Image.Image, t: float) -> None:
    """Locate social priorities in operational parameters."""
    header(im, "ĐỌC MÃ KỸ THUẬT", "TÌM VẾT GIÁ TRỊ TRONG THAM SỐ", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    steps = [
        ("ƯU TIÊN XÃ HỘI", v10.VERMILION),
        ("ĐỊNH NGHĨA MỤC TIÊU", v10.SAGE),
        ("NGƯỠNG · TRỌNG SỐ · NGOẠI LỆ", v10.COBALT),
        ("KẾT QUẢ PHÂN BỔ", v10.VERMILION),
    ]
    for i, (label, color) in enumerate(steps):
        y = 300 + i * 150
        p = v10.ease((t - i * .55) / 1.6)
        x = 305 + (1 - p) * (75 if i % 2 == 0 else -75)
        v10.pill(im, (round(x), y, round(x + 1310), y + 86), label, color, 250, str(i + 1))
        if i:
            v10.arrow(im, (960, y - 55), (960, y - 9), color, (t - .8 - i * .45) / 1.4, 5)
    v10.center(d, 960, 910, "THAM SỐ KHÔNG TỰ CHỌN MỤC TIÊU CHO MÌNH", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg34(im: Image.Image, t: float) -> None:
    """Show that scale of use does not imply decision power."""
    header(im, "PHỔ CẬP VÀ QUYỀN LỰC", "NHIỀU NGƯỜI DÙNG VẪN CÓ THỂ VẮNG TIẾNG NÓI", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    hub = (700, 560)
    users = [(230 + (i % 4) * 180, 335 + (i // 4) * 210) for i in range(8)]
    for i, point in enumerate(users):
        v10.node(im, point, v10.COBALT, 18, v10.ease((t - i * .16) / 1.2))
        v10.arrow(im, point, hub, v10.COBALT, (t - .8 - i * .1) / 2.0, 3)
    v10.box(im, (590, 465, 810, 655), v10.MIST, v10.COBALT)
    v10.center(d, 700, 560, "NỀN TẢNG", v10.F_SMALL, v10.COBALT)
    d.line((1010, 280, 1010, 820), fill=v10.rgba(v10.VERMILION, 235), width=7)
    d.line((980, 550, 1040, 550), fill=v10.rgba(v10.VERMILION, 245), width=9)
    v10.box(im, (1180, 390, 1720, 720), v10.PAPER, v10.VERMILION)
    v10.center(d, 1450, 465, "BÀN QUYẾT ĐỊNH", v10.F_BODY_B, v10.VERMILION)
    for i in range(3):
        d.rectangle((1280, 555 + i * 42, 1620, 568 + i * 42), fill=v10.rgba(v10.CHARCOAL, 95))
    v10.center(d, 960, 895, "QUY MÔ SỬ DỤNG  ≠  KHẢ NĂNG ĐỊNH HÌNH", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg35(im: Image.Image, t: float) -> None:
    """Bridge value-laden structure to democratic transformation."""
    header(im, "MẠCH LẬP LUẬN", "TỪ CẤU TRÚC MANG GIÁ TRỊ ĐẾN DÂN CHỦ HÓA", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    points = [(285, 610), (720, 430), (1130, 670), (1635, 435)]
    labels = ["CẤU TRÚC", "GIÁ TRỊ · QUYỀN LỰC", "KHẢ NĂNG CẢI BIẾN", "DÂN CHỦ HÓA"]
    for i, (point, label) in enumerate(zip(points, labels)):
        color = v10.VERMILION if i in (1, 3) else v10.COBALT
        v10.node(im, point, color, 31, v10.ease((t - i * .45) / 1.5))
        v10.pill(im, (point[0] - 170, point[1] + 75, point[0] + 170, point[1] + 139), label, color)
    v10.thread(im, points, (t - 1.0) / 4.8, v10.VERMILION, 9)
    v10.center(d, 960, 885, "THIẾT KẾ KHÔNG ĐÓNG KÍN · QUYẾT ĐỊNH CÓ THỂ ĐƯỢC MỞ RA", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg36(im: Image.Image, t: float) -> None:
    """Treat expertise and lived experience as complementary knowledge."""
    header(im, "LUẬN ĐIỂM NHÓM 14", "HAI LOẠI TRI THỨC CẦN GẶP NHAU", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    v10.box(im, (130, 300, 830, 760), v10.PAPER, v10.COBALT)
    v10.box(im, (1090, 300, 1790, 760), v10.PAPER, v10.VERMILION)
    v10.center(d, 480, 385, "CHUYÊN MÔN KỸ THUẬT", v10.F_BODY_B, v10.COBALT)
    v10.center(d, 1440, 385, "KINH NGHIỆM SỐNG", v10.F_BODY_B, v10.VERMILION)
    for i, label in enumerate(("RÀNG BUỘC", "ĐỘ TIN CẬY", "AN TOÀN")):
        v10.pill(im, (245, 485 + i * 75, 715, 540 + i * 75), label, v10.COBALT)
    for i, label in enumerate(("HẬU QUẢ", "RÀO CẢN", "NHU CẦU")):
        v10.pill(im, (1205, 485 + i * 75, 1675, 540 + i * 75), label, v10.VERMILION)
    v10.arrow(im, (830, 545), (930, 545), v10.COBALT, (t - 2.0) / 2.0, 6)
    v10.arrow(im, (1090, 545), (990, 545), v10.VERMILION, (t - 2.5) / 2.0, 6)
    v10.node(im, (960, 545), v10.VERMILION, 38, v10.ease((t - 3.0) / 2.0))
    v10.pill(im, (655, 830, 1265, 900), "QUYẾT ĐỊNH CÓ THỂ SỬA", v10.VERMILION)
    v10.center(d, 960, 950, "DÂN CHỦ HÓA KHÔNG PHỦ NHẬN CHUYÊN MÔN", v10.F_TINY, v10.SAGE)
    v10.footer(im)


def mg37(im: Image.Image, t: float) -> None:
    """Place participation inside the window where choices remain open."""
    header(im, "THỜI ĐIỂM THAM GIA", "PHƯƠNG ÁN PHẢI CÒN CÓ THỂ THAY ĐỔI", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    labels = ["ĐẶT VẤN ĐỀ", "TẠO PHƯƠNG ÁN", "THỬ NGHIỆM", "TRIỂN KHAI", "THEO DÕI"]
    points = [(230 + i * 365, 600) for i in range(5)]
    d.rounded_rectangle((150, 300, 1110, 800), radius=24, fill=v10.rgba(v10.MIST, 120), outline=v10.rgba(v10.VERMILION, 210), width=4)
    v10.center(d, 630, 350, "CỬA SỔ CÒN HIỆU LỰC", v10.F_BODY_B, v10.VERMILION)
    for i, (point, label) in enumerate(zip(points, labels)):
        color = v10.VERMILION if i <= 2 else v10.SAGE
        v10.node(im, point, color, 25, v10.ease((t - i * .4) / 1.5))
        v10.pill(im, (point[0] - 145, 690, point[0] + 145, 752), label, color)
        if i:
            v10.arrow(im, points[i - 1], point, color, (t - .7 - i * .35) / 1.5, 5)
    d.line((1210, 330, 1210, 820), fill=v10.rgba(v10.CHARCOAL, 60), width=3)
    v10.center(d, 1490, 380, "SAU KHI ĐÃ KHÓA", v10.F_BODY_B, v10.SAGE)
    v10.center(d, 1490, 430, "CHỈ THÔNG BÁO", v10.F_SMALL, v10.CHARCOAL)
    v10.center(d, 1490, 480, "CHƯA PHẢI", v10.F_SMALL, v10.CHARCOAL)
    v10.center(d, 1490, 530, "CÙNG ĐỊNH HÌNH", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg38(im: Image.Image, t: float) -> None:
    """Bring an excluded interest into the technical problem definition."""
    header(im, "LỢI ÍCH BỊ GẠT RA NGOÀI", "TỪ HẬU QUẢ KHÓ THẤY ĐẾN TIÊU CHÍ KIỂM THỬ", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    v10.box(im, (560, 300, 1360, 740), v10.MIST, v10.COBALT)
    v10.center(d, 960, 385, "CHỈ SỐ CHÍNH", v10.F_BODY_B, v10.COBALT)
    v10.pill(im, (710, 505, 1210, 580), "HIỆU QUẢ ĐÃ CHỌN", v10.COBALT)
    outside = [
        ((250, 390), "NGƯỜI CAO TUỔI", (750, 680)),
        ((250, 680), "HỖ TRỢ NGÔN NGỮ", (850, 710)),
        ((1670, 550), "NHÂN VIÊN TIẾP NHẬN", (1150, 680)),
    ]
    for i, (point, label, target) in enumerate(outside):
        v10.node(im, point, v10.VERMILION, 22, v10.ease((t - i * .35) / 1.5))
        v10.pill(im, (point[0] - 175, point[1] + 55, point[0] + 175, point[1] + 115), label, v10.VERMILION)
        v10.arrow(im, point, target, v10.VERMILION, (t - 2.0 - i * .45) / 2.4, 4)
    p = v10.ease((t - 6.0) / 3.0)
    if p > 0:
        v10.pill(im, (650, 805, 1270, 885), "TIÊU CHÍ KIỂM THỬ MỚI", v10.VERMILION, round(130 + 120 * p))
    v10.center(d, 960, 940, "NHU CẦU ĐƯỢC CHUYỂN THÀNH VẤN ĐỀ KỸ THUẬT", v10.F_TINY, v10.SAGE)
    v10.footer(im)


def mg39(im: Image.Image, t: float) -> None:
    """Frame democratization as a conditional potential, not a guarantee."""
    header(im, "KẾT LUẬN THẬN TRỌNG", "TIỀM NĂNG CẢI BIẾN KHÔNG TỰ ĐỘNG XẢY RA", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    left = (190, 360, 735, 760)
    right = (1185, 360, 1730, 760)
    v10.box(im, left, v10.PAPER, v10.COBALT)
    v10.box(im, right, v10.PAPER, v10.VERMILION)
    v10.center(d, 462, 440, "TIỀM NĂNG", v10.F_BODY_B, v10.COBALT)
    v10.center(d, 1457, 440, "BẢO ĐẢM TỰ ĐỘNG", v10.F_BODY_B, v10.VERMILION)
    for i, label in enumerate(("PHẢN HỒI", "THÔNG TIN", "QUYỀN TÁC ĐỘNG")):
        v10.pill(im, (275, 525 + i * 70, 650, 580 + i * 70), label, v10.COBALT)
    d.line((930, 330, 990, 790), fill=v10.rgba(v10.VERMILION, 240), width=10)
    d.line((1255, 585, 1660, 585), fill=v10.rgba(v10.VERMILION, 220), width=8)
    v10.center(d, 960, 875, "CẦN CƠ CHẾ TIẾP NHẬN VÀ TƯƠNG QUAN QUYỀN LỰC PHÙ HỢP", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg40(im: Image.Image, t: float) -> None:
    """Map heterogeneous stakeholders around a technical system."""
    header(im, "BẢN ĐỒ TÁC NHÂN", "NGƯỜI DÙNG KHÔNG PHẢI MỘT KHỐI ĐỒNG NHẤT", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    centre = (960, 565)
    v10.box(im, (785, 455, 1135, 675), v10.MIST, v10.COBALT)
    v10.center(d, centre[0], centre[1], "HỆ THỐNG", v10.F_BODY_B, v10.COBALT)
    actors = [
        ((300, 330), "BỆNH NHÂN", v10.VERMILION),
        ((300, 765), "NGƯỜI CHĂM SÓC", v10.COBALT),
        ((960, 750), "NHÂN VIÊN TIẾP NHẬN", v10.SAGE),
        ((1620, 765), "NHÀ QUẢN LÝ", v10.COBALT),
        ((1620, 330), "KỸ SƯ", v10.VERMILION),
    ]
    targets = ((785, 500), (785, 630), (960, 675), (1135, 630), (1135, 500))
    for i, ((point, label, color), target) in enumerate(zip(actors, targets)):
        v10.node(im, point, color, 24, v10.ease((t - i * .35) / 1.5))
        v10.pill(im, (point[0] - 170, point[1] + 58, point[0] + 170, point[1] + 120), label, color)
        v10.arrow(im, point, target, color, (t - 1.0 - i * .32) / 2.0, 4)
    v10.center(d, 960, 930, "VỊ TRÍ KHÁC NHAU · NHU CẦU VÀ RỦI RO KHÁC NHAU", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg41(im: Image.Image, t: float) -> None:
    """Translate values into concrete specifications without conflation."""
    header(im, "GIÁ TRỊ THÀNH ĐẶC TẢ", "TỪ YÊU CẦU XÃ HỘI ĐẾN CẤU TRÚC VẬN HÀNH", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    rows = [
        ("AN TOÀN", "NGƯỠNG", v10.VERMILION),
        ("CÔNG BẰNG", "QUY TẮC NGOẠI LỆ", v10.COBALT),
        ("TIẾP CẬN", "TIÊU CHÍ KIỂM THỬ", v10.SAGE),
    ]
    for i, (value, spec, color) in enumerate(rows):
        y = 330 + i * 190
        v10.pill(im, (170, y, 690, y + 88), value, color)
        v10.arrow(im, (690, y + 44), (930, y + 44), color, (t - .8 - i * .55) / 1.8, 6)
        v10.pill(im, (930, y, 1750, y + 88), spec, color)
    v10.thread(im, [(430, 850), (960, 900), (1490, 850)], (t - 4.5) / 3.2, v10.VERMILION, 7)
    v10.center(d, 960, 950, "GIÁ TRỊ KHÔNG ĐỨNG NGOÀI THIẾT KẾ", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg42(im: Image.Image, t: float) -> None:
    """Open the apparently singular metric of efficiency."""
    header(im, "MÂU THUẪN TRIẾT HỌC", "HIỆU QUẢ ĐƯỢC ĐỊNH NGHĨA CHO AI", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    centre = (960, 520)
    v10.box(im, (720, 395, 1200, 645), v10.MIST, v10.VERMILION)
    v10.center(d, centre[0], centre[1], "HIỆU QUẢ", v10.F_HUGE, v10.VERMILION)
    options = [
        ((300, 320), "THỜI GIAN TRỐNG"),
        ((300, 745), "THỜI GIAN CHỜ"),
        ((1620, 320), "CA NGUY CẤP"),
        ((1620, 745), "KHÔNG LOẠI TRỪ"),
    ]
    targets = ((720, 450), (720, 590), (1200, 450), (1200, 590))
    for i, ((point, label), target) in enumerate(zip(options, targets)):
        color = v10.COBALT if i < 2 else v10.VERMILION
        v10.node(im, point, color, 24, v10.ease((t - i * .25) / 1.4))
        v10.pill(im, (point[0] - 175, point[1] + 65, point[0] + 175, point[1] + 127), label, color)
        v10.arrow(im, point, target, color, (t - 1.1 - i * .22) / 1.7, 4)
    v10.center(d, 960, 900, "MỖI PHÉP ĐO ĐƯA MỘT ƯU TIÊN VÀO KHUNG KỸ THUẬT", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg43(im: Image.Image, t: float) -> None:
    """Show a technical frame distributing possibilities of action."""
    header(im, "CẤU TRÚC VÀ HÀNH ĐỘNG", "KHUNG KỸ THUẬT PHÂN PHỐI KHẢ NĂNG", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    v10.box(im, (235, 300, 1685, 790), v10.PAPER, v10.COBALT)
    d.rectangle((235, 300, 1685, 326), fill=v10.rgba(v10.COBALT, 220))
    v10.center(d, 960, 380, "KHUNG KỸ THUẬT", v10.F_BODY_B, v10.COBALT)
    lanes = [
        ((365, 510, 735, 655), "DỄ HƠN", v10.COBALT, True),
        ((775, 510, 1145, 655), "KHÓ HƠN", v10.SAGE, True),
        ((1185, 510, 1555, 655), "BỊ NGĂN", v10.VERMILION, False),
    ]
    for i, (box, label, color, open_lane) in enumerate(lanes):
        v10.box(im, box, v10.MIST if open_lane else v10.PAPER, color)
        text_x = (box[0] + box[2]) / 2 - (38 if not open_lane else 0)
        v10.center(d, text_x, (box[1] + box[3]) / 2, label, v10.F_BODY_B, color)
        if not open_lane:
            d.line((box[2] - 75, box[1] + 28, box[2] - 75, box[3] - 28), fill=v10.rgba(v10.VERMILION, 235), width=8)
            d.line((box[2] - 48, box[1] + 28, box[2] - 48, box[3] - 28), fill=v10.rgba(v10.VERMILION, 235), width=8)
    v10.thread(im, [(350, 730), (650, 730), (960, 705), (1270, 730), (1570, 730)], (t - 1.8) / 4.0, v10.VERMILION, 8)
    v10.center(d, 960, 885, "PHƯƠNG TIỆN VÀ MỤC ĐÍCH KHÔNG HOÀN TOÀN TÁCH RỜI", v10.F_SMALL, v10.CHARCOAL)
    v10.footer(im)


def mg44(im: Image.Image, t: float) -> None:
    """Separate correct execution from an inadequately chosen objective."""
    header(im, "ĐẶC TẢ VÀ VẤN ĐỀ", "CHẠY ĐÚNG CHƯA CÓ NGHĨA LÀ CHỌN ĐÚNG MỤC TIÊU", t / v10.DURATION)
    d = ImageDraw.Draw(im)

    # The upper rail is deliberately enclosed: it is the narrow objective
    # that the system can satisfy perfectly.  Affected interests remain
    # outside that frame instead of being misrepresented as software errors.
    d.rounded_rectangle(
        (115, 270, 1805, 655),
        radius=25,
        fill=v10.rgba(v10.MIST, 105),
        outline=v10.rgba(v10.COBALT, 205),
        width=4,
    )
    v10.center(d, 960, 315, "KHUNG MỤC TIÊU ĐÃ CHỌN", v10.F_SMALL, v10.COBALT)
    stages = [
        ((180, 420, 610, 545), "MỤC TIÊU HẸP", v10.VERMILION),
        ((745, 420, 1175, 545), "ĐẶC TẢ", v10.COBALT),
        ((1310, 420, 1740, 545), "CHẠY ĐÚNG", v10.COBALT),
    ]
    for i, (box, label, color) in enumerate(stages):
        alpha = round(115 + 135 * v10.ease((t - i * 0.45) / 1.5))
        v10.box(im, box, v10.PAPER, color, alpha)
        v10.center(d, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2, label, v10.F_BODY_B, color)
        if i:
            previous = stages[i - 1][0]
            v10.arrow(
                im,
                (previous[2], (previous[1] + previous[3]) / 2),
                (box[0], (box[1] + box[3]) / 2),
                v10.VERMILION if i == 1 else v10.COBALT,
                (t - 0.8 - i * 0.45) / 1.5,
                6,
            )

    v10.center(d, 960, 710, "NHỮNG GÌ CÓ THỂ NẰM NGOÀI PHÉP TÍNH", v10.F_SMALL, v10.VERMILION)
    excluded = [
        (390, "NGƯỜI CAO TUỔI"),
        (960, "KẾT NỐI KHÔNG ỔN ĐỊNH"),
        (1530, "NHU CẦU HỖ TRỢ"),
    ]
    for i, (x, label) in enumerate(excluded):
        p = v10.ease((t - 2.4 - i * 0.35) / 1.5)
        v10.node(im, (x, 825), v10.VERMILION, 23, p)
        v10.pill(im, (x - 205, 875, x + 205, 937), label, v10.VERMILION, round(125 + 125 * p))
    v10.footer(im)


def mg45(im: Image.Image, t: float) -> None:
    """Show the institutional path required for feedback to gain effect."""
    header(im, "ĐIỀU KIỆN CỦA TIỀM NĂNG", "PHẢN HỒI CHỈ CÓ TÁC DỤNG KHI CÓ ĐƯỜNG ĐI", t / v10.DURATION)
    d = ImageDraw.Draw(im)
    inputs = [
        ((145, 305, 650, 405), "KÊNH TIẾP NHẬN", v10.COBALT),
        ((145, 500, 650, 600), "QUYỀN TIẾP CẬN THÔNG TIN", v10.SAGE),
        ((145, 695, 650, 795), "QUYỀN CAN THIỆP", v10.VERMILION),
    ]
    hub = (1010, 550)
    for i, (box, label, color) in enumerate(inputs):
        p = v10.ease((t - i * 0.4) / 1.5)
        v10.box(im, box, v10.PAPER, color, round(130 + 120 * p))
        v10.center(d, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2, label, v10.F_SMALL, color)
        v10.arrow(im, (box[2], (box[1] + box[3]) / 2), hub, color, (t - 1.2 - i * 0.35) / 1.9, 5)

    v10.node(im, hub, v10.VERMILION, 36, v10.ease((t - 2.8) / 1.8))
    v10.box(im, (1135, 420, 1755, 680), v10.MIST, v10.COBALT)
    v10.center(d, 1445, 510, "KHẢ NĂNG", v10.F_BODY_B, v10.COBALT)
    v10.center(d, 1445, 565, "TÁC ĐỘNG", v10.F_BODY_B, v10.VERMILION)
    v10.arrow(im, hub, (1135, 550), v10.VERMILION, (t - 3.6) / 1.8, 7)

    # A separate lower rail names the power relation without drawing across
    # any label or implying that three procedural inputs guarantee an outcome.
    d.line((260, 885, 1660, 885), fill=v10.rgba(v10.CHARCOAL, 65), width=3)
    v10.pill(im, (560, 835, 1360, 935), "TƯƠNG QUAN QUYỀN LỰC GIỮA CÁC BÊN", v10.VERMILION)
    v10.center(d, 960, 985, "TIỀM NĂNG  ≠  BẢO ĐẢM", v10.F_TINY, v10.SAGE)
    v10.footer(im)


# Monkey-patch only the V11 process.  The V10 source and rendered fallback are
# untouched, while all inherited painters resolve the corrected header here.
v10.header = header
V11_ANIM = dict(v10.ANIM)
V11_ANIM.update(
    {
        "MG05_matrix_axes": mg05,
        "MG13_democratization_title": mg13,
        "MG17_evidence_boundary": mg17,
        "MG23_central_question": mg23,
        "MG27_hypothetical_boundary": mg27,
        "MG28_democracy_not_access": mg28,
        "MG29_ambivalent_paths": mg29,
        "MG30_collective_priority": mg30,
        "MG31_participation_chain": mg31,
        "MG32_design_genealogy": mg32,
        "MG33_parameter_trace": mg33,
        "MG34_access_at_scale": mg34,
        "MG35_red_thread_bridge": mg35,
        "MG36_complementary_knowledge": mg36,
        "MG37_effective_window": mg37,
        "MG38_excluded_interest": mg38,
        "MG39_cautious_potential": mg39,
        "MG40_stakeholder_map": mg40,
        "MG41_value_specification": mg41,
        "MG42_efficiency_for_whom": mg42,
        "MG43_action_frame": mg43,
        "MG44_correct_spec_wrong_goal": mg44,
        "MG45_feedback_path": mg45,
    }
)

# A few V11 scenes intentionally hold a diagram long enough for the lecturer
# and class to read it.  Render those masters at their actual approved scene
# length instead of padding the final frame of a 12-second V10 asset.  Human
# footage is never affected by this deterministic-graphic duration map.
V11_DURATIONS = {
    "MG10_meta_choice": 15.0,
    "MG22_five_conditions": 13.0,
    "MG24_conclusion_layers": 13.0,
    "MG26_methodological_motif": 13.0,
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--only", action="append", choices=sorted(V11_ANIM))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    selected = args.only or list(V11_ANIM)
    default_duration = v10.DURATION
    records = []
    try:
        for name in selected:
            duration = V11_DURATIONS.get(name, default_duration)
            v10.DURATION = duration
            out = args.output_dir / f"{name}.mp4"
            v10.render(name, V11_ANIM[name], out, args.force)
            records.append(
                {
                    "name": name,
                    "path": str(out),
                    "duration": duration,
                    "width": v10.W,
                    "height": v10.H,
                    "fps": v10.FPS,
                    "palette": "Civic Daylight / Red Thread · V11 corrected",
                    "sha256": sha(out),
                }
            )
    finally:
        v10.DURATION = default_duration
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest {args.manifest}")


if __name__ == "__main__":
    main()
