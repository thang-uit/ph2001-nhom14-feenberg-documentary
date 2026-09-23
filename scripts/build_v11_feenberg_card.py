#!/opt/homebrew/bin/python3.13
"""Build the sourced, real-photo Andrew Feenberg identity card for V11."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


W, H = 2560, 1440
FONT = "/System/Library/Fonts/Avenir Next.ttc"
IVORY = (244, 239, 229)
PAPER = (255, 252, 246)
CHARCOAL = (36, 40, 43)
COBALT = (27, 74, 137)
VERMILION = (211, 73, 54)
SAGE = (112, 132, 117)


def font(size: int, index: int = 7) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size=size, index=index)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(source: Path, output: Path) -> None:
    im = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(im)
    for y in range(H):
        p = y / H
        color = tuple(round(a + (b - a) * p * 0.22) for a, b in zip(IVORY, (229, 223, 211)))
        d.line((0, y, W, y), fill=color)
    d.rectangle((0, 0, W, 18), fill=COBALT)
    d.rectangle((0, 0, round(W * 0.71), 18), fill=VERMILION)

    photo = Image.open(source).convert("RGB")
    # Downscale only: the verified original is taller than the displayed crop.
    framed = ImageOps.fit(photo, (900, 1140), method=Image.Resampling.LANCZOS, centering=(0.43, 0.50))
    px, py = 130, 150
    d.rounded_rectangle((px + 20, py + 24, px + 940, py + 1184), radius=24, fill=(0, 0, 0, 35))
    d.rounded_rectangle((px - 10, py - 10, px + 910, py + 1150), radius=24, fill=PAPER, outline=COBALT, width=4)
    im.paste(framed, (px, py))

    d = ImageDraw.Draw(im)
    tx = 1150
    d.rectangle((tx, 185, tx + 20, 260), fill=VERMILION)
    d.text((tx + 55, 188), "CON NGƯỜI VÀ TƯ TƯỞNG", font=font(30, 2), fill=COBALT)
    d.line((tx, 290, 2390, 290), fill=COBALT, width=3)
    d.text((tx, 385), "ANDREW", font=font(92, 0), fill=CHARCOAL)
    d.text((tx, 505), "FEENBERG", font=font(108, 0), fill=VERMILION)
    d.text((tx, 690), "TRIẾT GIA VỀ CÔNG NGHỆ", font=font(43, 0), fill=COBALT)
    d.text((tx, 780), "School of Communication", font=font(37, 7), fill=CHARCOAL)
    d.text((tx, 835), "Simon Fraser University", font=font(37, 7), fill=CHARCOAL)
    d.line((tx, 955, 2250, 955), fill=VERMILION, width=7)
    d.line((2250, 955, 2390, 955), fill=COBALT, width=4)
    d.text((tx, 1015), "LÝ THUYẾT PHÊ PHÁN CÔNG NGHỆ", font=font(31, 2), fill=SAGE)
    d.text((tx, 1070), "CÔNG NGHỆ MANG GIÁ TRỊ", font=font(31, 2), fill=SAGE)
    d.text((tx, 1125), "NHƯNG CÓ THỂ ĐƯỢC ĐỊNH HƯỚNG", font=font(31, 2), fill=SAGE)

    d.text((130, 1350), "Beatrice Murch · Wikimedia Commons · CC BY-SA 3.0", font=font(23, 5), fill=SAGE)
    d.text((2390, 1350), "NHÓM 14 · FEENBERG", font=font(23, 5), fill=SAGE, anchor="ra")
    output.parent.mkdir(parents=True, exist_ok=True)
    im.save(output, format="PNG", optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    build(args.source, args.output)
    record = {
        "output": str(args.output),
        "source": str(args.source),
        "identity": "Andrew Feenberg",
        "role_text": "Triết gia về công nghệ",
        "affiliation_text": "School of Communication · Simon Fraser University",
        "photographer": "Beatrice Murch",
        "license": "CC BY-SA 3.0",
        "width": W,
        "height": H,
        "sha256": sha(args.output),
        "status": "VERIFIED_REAL_PHOTO_CARD",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
