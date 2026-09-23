#!/opt/homebrew/bin/python3.13
"""Render the V11 subtitle track at the approved smaller 42-pixel size."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

import build_subtitle_overlay as base


def render_card(lines: list[str], path: Path) -> None:
    if not 1 <= len(lines) <= 2:
        raise ValueError(f"Subtitle must contain one or two lines: {lines}")
    image = Image.new("RGBA", (base.WIDTH, base.HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    subtitle_font = base.font(42)
    line_height = 53
    boxes = [draw.textbbox((0, 0), line, font=subtitle_font) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    box_width = max(widths) + 66
    box_height = len(lines) * line_height + 22
    x0 = (base.WIDTH - box_width) // 2
    y1 = base.HEIGHT - 82
    y0 = y1 - box_height
    draw.rounded_rectangle((x0, y0, x0 + box_width, y1), radius=14, fill=(0, 0, 0, 188))
    y = y0 + 9
    for line, width in zip(lines, widths):
        draw.text(((base.WIDTH - width) // 2, y), line, font=subtitle_font, fill=(247, 244, 237, 255))
        y += line_height
    image.save(path)


base.render_card = render_card


if __name__ == "__main__":
    base.main()
