#!/usr/bin/env python3
"""Create deterministic Vietnamese overlays for the S001-S006 style proof."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1920
HEIGHT = 1080
FONT_PATH = Path("/System/Library/Fonts/Avenir Next.ttc")
OBSIDIAN = (11, 15, 20, 236)
WARM_PAPER = "#F2ECE0"
MUTED = "#B8C1C8"
AMBER = "#E6A23C"
TEAL = "#48B8A6"


def font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def text_width(draw: ImageDraw.ImageDraw, value: str, text_font: ImageFont.FreeTypeFont) -> int:
    bounds = draw.textbbox((0, 0), value, font=text_font)
    return bounds[2] - bounds[0]


def blank() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))


def label(image: Image.Image, kicker: str, value: str, accent: str = AMBER) -> None:
    draw = ImageDraw.Draw(image)
    kicker_font = font(22)
    value_font = font(33, index=1)
    value_width = text_width(draw, value, value_font)
    box_width = max(560, value_width + 74)
    x0, y0 = 72, 70
    draw.rounded_rectangle((x0, y0, x0 + box_width, y0 + 126), radius=16, fill=OBSIDIAN)
    draw.rectangle((x0, y0, x0 + 7, y0 + 126), fill=accent)
    draw.text((x0 + 30, y0 + 18), kicker, font=kicker_font, fill=MUTED)
    draw.text((x0 + 30, y0 + 55), value, font=value_font, fill=WARM_PAPER)


def centered_keywords(image: Image.Image, values: list[str], accent: str = AMBER) -> None:
    draw = ImageDraw.Draw(image)
    keyword_font = font(42, index=1)
    gap = 34
    widths = [text_width(draw, value, keyword_font) + 52 for value in values]
    total = sum(widths) + gap * (len(values) - 1)
    x = (WIDTH - total) // 2
    y = 112
    for value, item_width in zip(values, widths):
        draw.rounded_rectangle((x, y, x + item_width, y + 72), radius=14, fill=OBSIDIAN)
        draw.text((x + 26, y + 12), value, font=keyword_font, fill=WARM_PAPER)
        draw.rectangle((x, y + 68, x + item_width, y + 72), fill=accent)
        x += item_width + gap


def phone_ui_plate(output_dir: Path) -> None:
    image = Image.new("RGBA", (820, 330), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 812, 322), radius=42, fill=(242, 244, 241, 248), outline=(28, 38, 45, 210), width=5)
    draw.text((62, 48), "ĐẶT LỊCH", font=font(31, index=1), fill="#34424A")
    draw.text((62, 112), "09:30", font=font(92, index=1), fill="#13202A")
    draw.rounded_rectangle((550, 114, 750, 224), radius=55, fill=TEAL)
    draw.text((596, 143), "CHỌN", font=font(34, index=1), fill="#09110F")
    draw.text((62, 244), "Khung giờ hệ thống trả về", font=font(27), fill="#5E6B72")
    image.save(output_dir / "S002_phone_ui_plate.png", optimize=True)


def main() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    output_dir = project_dir / "assets/flow/proof/overlays"
    output_dir.mkdir(parents=True, exist_ok=True)

    overlays: dict[str, Image.Image] = {scene_id: blank() for scene_id in ("S001", "S002", "S003", "S004", "S006")}
    label(overlays["S001"], "NHÓM 14 · MINH HỌA", "TÌNH HUỐNG GIẢ ĐỊNH")
    label(overlays["S002"], "PHẢN HỒI HỆ THỐNG", "ĐẶT LỊCH · 09:30", accent=TEAL)
    centered_keywords(overlays["S003"], ["DỮ LIỆU", "TIÊU CHÍ", "NGOẠI LỆ"])
    centered_keywords(overlays["S004"], ["GIÁ TRỊ", "LỢI ÍCH", "QUYỀN LỰC"], accent=TEAL)
    label(
        overlays["S006"],
        "GIỚI HẠN DẪN CHỨNG",
        "MINH HỌA GIẢ ĐỊNH · KHÔNG PHẢI CASE CỦA FEENBERG",
    )

    for scene_id, image in overlays.items():
        image.save(output_dir / f"{scene_id}_overlay.png", optimize=True)
    phone_ui_plate(output_dir)
    print(f"Proof overlays created: {output_dir}")


if __name__ == "__main__":
    main()
