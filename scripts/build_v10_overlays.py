#!/opt/homebrew/bin/python3.13
"""Create light editorial lower-thirds/provenance overlays for the V10 edit."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from v10_visual_plan import (
    G,
    HYPOTHETICAL_SCENES,
    RECONSTRUCTION_SCENES,
    SCENE_ASSETS,
    SOURCE_SCENES,
    TITLE_TEXT,
)

W, H = 1920, 1080
FONT = "/System/Library/Fonts/Avenir Next.ttc"
IVORY = (244, 239, 229, 255)
PAPER = (255, 252, 246, 245)
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


def title_from_row(row: dict[str, str]) -> str:
    if row["SCENE_ID"] in TITLE_TEXT:
        return TITLE_TEXT[row["SCENE_ID"]].replace("\n", " · ")
    value = row.get("ON_SCREEN_TEXT", "")
    value = re.sub(r"\s*\|\s*", " · ", value)
    value = re.sub(r"\s*—\s*", " · ", value)
    value = re.sub(r"\s+", " ", value).strip()
    # Internal source/citation metadata belongs in the dossier, not the image.
    value = re.sub(r"\s*·\s*(Andrew Feenberg|Feenberg|PDF tr\.).*$", "", value, flags=re.I)
    return value[:135]


def make_overlay(row: dict[str, str], out: Path) -> None:
    sid = row["SCENE_ID"]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if sid == "S005":
        # The opening deserves a real title composition, not a generic
        # lower-third.  It remains above the subtitle-safe area and is drawn
        # entirely in post so the Vietnamese typography is exact.
        x0, y0, x1, y1 = 95, 122, 1195, 590
        d.rounded_rectangle((x0 + 12, y0 + 14, x1 + 12, y1 + 14), radius=18, fill=(0, 0, 0, 42))
        d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=(255, 252, 246, 242), outline=VERMILION, width=4)
        d.rectangle((x0, y0, x0 + 13, y1), fill=VERMILION)
        d.text((x0 + 54, y0 + 38), "PHIM TÀI LIỆU HỌC THUẬT · NHÓM 14", font=font(22, 2), fill=SAGE)
        title_face = font(55, 0)
        title_lines = ["DÂN CHỦ HÓA THIẾT KẾ", "VÀ QUẢN TRỊ CÔNG NGHỆ"]
        for index, line in enumerate(title_lines):
            d.text((x0 + 54, y0 + 92 + index * 74), line, font=title_face, fill=CHARCOAL)
        d.line((x0 + 54, y0 + 272, x1 - 54, y0 + 272), fill=COBALT, width=3)
        d.text((x0 + 54, y0 + 304), "THEO ANDREW FEENBERG", font=font(33, 0), fill=COBALT)
        d.text((x0 + 54, y0 + 364), "CÔNG NGHỆ CÓ THỰC SỰ TRUNG LẬP?", font=font(25, 2), fill=VERMILION)
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, optimize=True)
        return
    title = title_from_row(row)
    if not title:
        im.save(out, optimize=True)
        return
    # A restrained panel leaves the footage visible and keeps text out of the
    # subtitle safe area.  It appears only for the opening seconds in the
    # renderer, so scene headings do not turn the film into slides.
    face = font(34, 0)
    kicker_face = font(18, 2)
    lines = wrap(d, title, face, 720)[:2]
    width = max([d.textbbox((0, 0), x, font=face)[2] for x in lines] + [480]) + 64
    height = 66 + 48 * len(lines)
    x0, y0 = 70, 92
    accent = VERMILION if sid in RECONSTRUCTION_SCENES or sid in HYPOTHETICAL_SCENES else COBALT
    d.rounded_rectangle((x0 + 8, y0 + 10, x0 + width + 8, y0 + height + 10), radius=14, fill=(0, 0, 0, 34))
    d.rounded_rectangle((x0, y0, x0 + width, y0 + height), radius=14, fill=PAPER, outline=accent, width=3)
    d.rectangle((x0, y0, x0 + 9, y0 + height), fill=accent)
    if sid in SOURCE_SCENES:
        kicker = "ĐỐI CHIẾU VĂN BẢN GỐC"
    elif sid in RECONSTRUCTION_SCENES:
        kicker = "MINH HỌA BẰNG AI · TÁI DỰNG"
    elif sid in HYPOTHETICAL_SCENES:
        kicker = "TÌNH HUỐNG GIẢ ĐỊNH · NHÓM 14"
    elif sid in {f"S{i:03d}" for i in range(80, 91)}:
        kicker = "ĐỀ XUẤT PHƯƠNG PHÁP LUẬN · NHÓM 14"
    else:
        kicker = "PHÂN TÍCH THEO FEENBERG"
    d.text((x0 + 28, y0 + 16), kicker, font=kicker_face, fill=SAGE if sid not in RECONSTRUCTION_SCENES else VERMILION)
    for i, line in enumerate(lines):
        d.text((x0 + 28, y0 + 40 + i * 44), line, font=face, fill=CHARCOAL)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)


def make_provenance(row: dict[str, str], relative: str, out: Path) -> None:
    sid = row["SCENE_ID"]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if relative.startswith(G + "/") or sid in SOURCE_SCENES:
        im.save(out, optimize=True)
        return
    if relative.startswith(("assets/flow_v9_raw/", "assets/flow_selected/", "assets/flow_v8_")):
        label = "MINH HỌA BẰNG AI"
    elif relative.startswith(("assets/credit_tphcm/", "assets/v10_selected/")):
        label = "FOOTAGE QUAY THẬT"
    else:
        label = "MINH HỌA"
    face = font(17, 2)
    x0, y0 = 70, 26
    bbox = d.textbbox((0, 0), label, font=face)
    width = bbox[2] - bbox[0] + 30
    d.rounded_rectangle((x0, y0, x0 + width, y0 + 30), radius=6, fill=(255, 252, 246, 224), outline=COBALT, width=2)
    d.text((x0 + 15, y0 + 5), label, font=face, fill=COBALT)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--storyboard", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    with args.storyboard.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    # The V10 storyboard also contains a CREDIT_V4 row.  Overlay generation
    # is for content scenes only; the credit artifact already carries its own
    # typography and must not receive a numeric scene overlay.
    rows = [r for r in rows if r["SCENE_ID"].startswith("S") and int(r["SCENE_ID"][1:]) <= 95]
    for row in rows:
        sid = row["SCENE_ID"]
        make_overlay(row, args.output_dir / f"{sid}_overlay.png")
        for index, relative in enumerate(SCENE_ASSETS[sid], 1):
            make_provenance(row, relative, args.output_dir / f"{sid}_{index:02d}_provenance.png")
    print(f"overlays: {len(list(args.output_dir.glob('*_overlay.png')))}")
    print(f"provenance: {len(list(args.output_dir.glob('*_provenance.png')))}")


if __name__ == "__main__":
    main()
