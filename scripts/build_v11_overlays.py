#!/opt/homebrew/bin/python3.13
"""Create restrained V11 titles and the single allowed AI disclosure label."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from v11_visual_plan import SCENE_ASSETS, TITLE_TEXT, category


W, H = 1920, 1080
FONT = "/System/Library/Fonts/Avenir Next.ttc"
PAPER = (255, 252, 246, 242)
CHARCOAL = (36, 40, 43, 255)
COBALT = (27, 74, 137, 255)
VERMILION = (211, 73, 54, 255)
SAGE = (112, 132, 117, 255)


def font(size: int, index: int = 7) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size=size, index=index)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        trial = f"{line} {word}"
        if draw.textbbox((0, 0), trial, font=face)[2] <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def blank() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def make_title(scene_id: str, output: Path) -> None:
    im = blank()
    if scene_id not in TITLE_TEXT:
        output.parent.mkdir(parents=True, exist_ok=True)
        im.save(output, optimize=True)
        return
    d = ImageDraw.Draw(im)
    title = TITLE_TEXT[scene_id]
    if scene_id == "S005":
        x0, y0, x1, y1 = 88, 112, 1225, 585
        d.rounded_rectangle((x0 + 12, y0 + 15, x1 + 12, y1 + 15), radius=20, fill=(0, 0, 0, 43))
        d.rounded_rectangle((x0, y0, x1, y1), radius=20, fill=PAPER, outline=VERMILION, width=4)
        d.rectangle((x0, y0, x0 + 13, y1), fill=VERMILION)
        d.text((x0 + 50, y0 + 34), "PHIM TÀI LIỆU HỌC THUẬT · NHÓM 14", font=font(21, 2), fill=SAGE)
        for index, line in enumerate(("DÂN CHỦ HÓA THIẾT KẾ", "VÀ QUẢN TRỊ CÔNG NGHỆ")):
            d.text((x0 + 50, y0 + 92 + index * 73), line, font=font(54, 0), fill=CHARCOAL)
        d.line((x0 + 50, y0 + 268, x1 - 50, y0 + 268), fill=COBALT, width=3)
        d.text((x0 + 50, y0 + 304), "THEO ANDREW FEENBERG", font=font(32, 0), fill=COBALT)
        d.text((x0 + 50, y0 + 365), "CÔNG NGHỆ CÓ THỰC SỰ TRUNG LẬP?", font=font(24, 2), fill=VERMILION)
    else:
        face = font(34, 0)
        lines = wrap(d, title.replace("\n", " "), face, 780)[:2]
        widths = [d.textbbox((0, 0), line, font=face)[2] for line in lines]
        panel_width = max(widths + [440]) + 64
        panel_height = 58 + len(lines) * 45
        x0, y0 = 66, 88
        d.rounded_rectangle((x0 + 8, y0 + 10, x0 + panel_width + 8, y0 + panel_height + 10), radius=14, fill=(0, 0, 0, 34))
        d.rounded_rectangle((x0, y0, x0 + panel_width, y0 + panel_height), radius=14, fill=PAPER, outline=COBALT, width=3)
        d.rectangle((x0, y0, x0 + 9, y0 + panel_height), fill=VERMILION)
        d.text((x0 + 28, y0 + 14), "LẬP LUẬN · NHÓM 14", font=font(17, 2), fill=SAGE)
        for index, line in enumerate(lines):
            d.text((x0 + 28, y0 + 39 + index * 43), line, font=face, fill=CHARCOAL)
    output.parent.mkdir(parents=True, exist_ok=True)
    im.save(output, optimize=True)


def make_provenance(relative: str, output: Path) -> None:
    im = blank()
    if category(relative) == "veo_flow_illustration":
        d = ImageDraw.Draw(im)
        label = "MINH HỌA BẰNG AI"
        face = font(16, 2)
        bbox = d.textbbox((0, 0), label, font=face)
        width = bbox[2] - bbox[0] + 28
        x0, y0 = 68, 28
        d.rounded_rectangle((x0, y0, x0 + width, y0 + 29), radius=6, fill=(255, 252, 246, 218), outline=COBALT, width=2)
        d.text((x0 + 14, y0 + 5), label, font=face, fill=COBALT)
    output.parent.mkdir(parents=True, exist_ok=True)
    im.save(output, optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--storyboard", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    with args.storyboard.open(encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["SCENE_ID"].startswith("S")]
    for row in rows:
        sid = row["SCENE_ID"]
        make_title(sid, args.output_dir / f"{sid}_overlay.png")
        for index, relative in enumerate(SCENE_ASSETS[sid], 1):
            make_provenance(relative, args.output_dir / f"{sid}_{index:02d}_provenance.png")
    print(f"scene overlays: {len(list(args.output_dir.glob('*_overlay.png')))}")
    print(f"provenance overlays: {len(list(args.output_dir.glob('*_provenance.png')))}")


if __name__ == "__main__":
    main()
