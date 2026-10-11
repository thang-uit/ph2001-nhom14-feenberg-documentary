#!/usr/bin/env python3
"""Create the YouTube thumbnail from a real film frame and the verified Feenberg photo.

The title is rendered locally (rather than generated inside an image model) so that
Vietnamese diacritics remain exact.  The script is deterministic and does not alter
the source photo or the video.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
# Use the clean real opening clip instead of the final subtitled master.  This
# keeps the thumbnail free of subtitles and chapter labels baked into the film.
VIDEO = ROOT / "assets/real/mixkit_41165_1080.mp4"
FEENBERG = ROOT / "assets/photos/andrew_feenberg_wikimedia.jpg"
DEFAULT_OUTPUT = ROOT / "delivery/thumbnail_youtube_feenberg_v1.png"
FONT_HEAVY = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_HEAVY if bold else FONT_REGULAR, size=size)


def extract_frame(video: Path, output: Path, seconds: float) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{seconds:.3f}", "-i", str(video), "-frames:v", "1",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
        "-q:v", "2", str(output),
    ]
    subprocess.run(cmd, check=True)


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = max(tw / image.width, th / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - tw) // 2
    top = (resized.height - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    return mask


def make_thumbnail(frame: Path, output: Path) -> None:
    width, height = 1920, 1080
    bg = Image.open(frame).convert("RGB")
    bg = fit_cover(bg, (width, height))
    bg = ImageEnhance.Contrast(bg).enhance(1.06)
    bg = ImageEnhance.Color(bg).enhance(0.92)

    # Keep the real phone/hand footage visible while reserving a quiet reading zone.
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(1110, width):
        alpha = round(235 * ((x - 1110) / (width - 1110)))
        od.line((x, 0, x, height), fill=(10, 24, 48, alpha))
    od.rectangle((0, 0, width, 94), fill=(9, 22, 42, 122))
    od.rectangle((0, 960, width, height), fill=(9, 22, 42, 160))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(bg)
    heavy = font(78, bold=True)
    heavy_small = font(39, bold=True)
    demi = font(42, bold=True)
    medium = font(31)

    # Small documentary lock-up.
    draw.text((72, 30), "NHÓM 14  ·  TRIẾT HỌC", font=demi, fill=(247, 245, 237, 255), spacing=2)
    draw.line((72, 86, 288, 86), fill=(222, 74, 59, 255), width=7)

    # High-contrast title with safe margins and no generated text.
    title_x = 1170
    draw.text((title_x + 4, 214), "CÔNG NGHỆ", font=heavy, fill=(0, 0, 0, 120), stroke_width=2)
    draw.text((title_x, 206), "CÔNG NGHỆ", font=heavy, fill=(247, 245, 237, 255), stroke_width=1, stroke_fill=(247, 245, 237, 255))
    draw.text((title_x + 4, 314), "CÓ TRUNG LẬP?", font=heavy, fill=(0, 0, 0, 120), stroke_width=2)
    draw.text((title_x, 306), "CÓ TRUNG LẬP?", font=heavy, fill=(222, 74, 59, 255), stroke_width=1, stroke_fill=(222, 74, 59, 255))
    draw.text((title_x, 430), "Dân chủ hóa thiết kế và quản trị", font=medium, fill=(247, 245, 237, 255))
    draw.text((title_x, 470), "công nghệ theo Andrew Feenberg", font=medium, fill=(247, 245, 237, 255))

    # Verified real portrait, inset rather than AI-generated.
    portrait = fit_cover(Image.open(FEENBERG).convert("RGB"), (430, 320))
    portrait = ImageEnhance.Contrast(portrait).enhance(1.04)
    portrait = ImageEnhance.Color(portrait).enhance(0.9)
    mask = rounded_mask((430, 320), 28)
    border = Image.new("RGBA", (454, 344), (247, 245, 237, 255))
    border.paste(portrait.convert("RGBA"), (12, 12), mask)
    bg.alpha_composite(border, (1418, 610))
    draw = ImageDraw.Draw(bg)
    draw.text((1450, 971), "ANDREW FEENBERG", font=heavy_small, fill=(247, 245, 237, 255))

    # Thin vermilion rule anchors the composition without crossing text.
    draw.rectangle((1170, 560, 1812, 570), fill=(222, 74, 59, 255))
    draw.text((72, 1000), "DÂN CHỦ HÓA  ·  THIẾT KẾ  ·  QUẢN TRỊ", font=demi, fill=(247, 245, 237, 255))

    output.parent.mkdir(parents=True, exist_ok=True)
    bg.convert("RGB").save(output, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, default=VIDEO)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seconds", type=float, default=2.0, help="real opening shot to use as background")
    args = parser.parse_args()

    tmp_frame = args.output.with_suffix(".source.jpg")
    extract_frame(args.video, tmp_frame, args.seconds)
    try:
        make_thumbnail(tmp_frame, args.output)
    finally:
        tmp_frame.unlink(missing_ok=True)
    print(args.output)


if __name__ == "__main__":
    main()
