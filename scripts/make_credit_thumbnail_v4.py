#!/usr/bin/env python3
"""Build the single Landmark 81 4K thumbnail from real V4 credit footage.

The source frame is taken from the approved UHD montage.  All typography and
grading are deterministic post-production; no city or landmark is generated.
"""

from __future__ import annotations

import argparse
import io
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = ROOT / "CREDIT_TPHCM_OH_YEAH_CLEAN_V4_4K.mp4"
OUT_DIR = ROOT / "qa" / "credit_tphcm" / "thumbnails"
FONT_PATH = Path("/System/Library/Fonts/Avenir Next.ttc")
WIDTH = 3840
HEIGHT = 2160


def get_font(size: int, index: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def frame_at(video: Path, seconds: float) -> Image.Image:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{seconds:.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-f",
        "image2pipe",
        "-vcodec",
        "png",
        "-",
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    with Image.open(io.BytesIO(result.stdout)) as image:
        if image.size != (WIDTH, HEIGHT):
            raise ValueError(f"Expected UHD frame {(WIDTH, HEIGHT)}, got {image.size}")
        return image.convert("RGBA")


def add_horizontal_gradient(
    image: Image.Image,
    *,
    max_alpha: int,
    end_x: int,
    color: tuple[int, int, int],
    bottom_lift: int = 0,
) -> None:
    """Add a smooth left-to-right veil without changing the source geometry."""
    veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = veil.load()
    for x in range(image.width):
        horizontal = max(0.0, 1.0 - x / max(1, end_x))
        alpha = int(max_alpha * horizontal * horizontal)
        for y in range(image.height):
            lower = max(0.0, (y / image.height - 0.64) / 0.36)
            pixels[x, y] = (*color, min(235, alpha + int(bottom_lift * lower)))
    image.alpha_composite(veil)


def add_bottom_gradient(image: Image.Image) -> None:
    veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(veil)
    # Restrained lower-third darkening preserves city lights while protecting
    # the small descriptor at the bottom-left at YouTube preview size.
    bands = 72
    start = int(HEIGHT * 0.66)
    for i in range(bands):
        y0 = start + int((HEIGHT - start) * i / bands)
        y1 = start + int((HEIGHT - start) * (i + 1) / bands)
        alpha = int(8 + 76 * (i / max(1, bands - 1)) ** 1.7)
        draw.rectangle((0, y0, WIDTH, y1), fill=(4, 7, 11, alpha))
    image.alpha_composite(veil)


def grade_frame(image: Image.Image) -> None:
    """Apply a subtle, consistent cinema grade while retaining real detail."""
    base = image.convert("RGB")
    base = ImageEnhance.Contrast(base).enhance(1.07)
    base = ImageEnhance.Color(base).enhance(1.08)
    base = ImageEnhance.Sharpness(base).enhance(1.05)
    image.alpha_composite(base.convert("RGBA"))
    add_horizontal_gradient(
        image,
        max_alpha=176,
        end_x=2180,
        color=(4, 7, 12),
        bottom_lift=30,
    )
    add_bottom_gradient(image)


def draw_tracking(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    tracking: int = 0,
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
) -> None:
    x, y = xy
    for char in text:
        draw.text(
            (x, y),
            char,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        advance = draw.textlength(char, font=font)
        x += int(advance) + tracking


def draw_thumbnail(image: Image.Image) -> None:
    grade_frame(image)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    ivory = (249, 246, 237, 255)
    gold = (238, 194, 116, 255)
    vermilion = (219, 78, 57, 255)
    muted = (223, 218, 207, 235)
    shadow = (0, 0, 0, 170)

    kicker = get_font(52, 2)  # Avenir Next Demi Bold
    title = get_font(164, 8)  # Avenir Next Heavy
    day = get_font(226, 8)
    descriptor = get_font(43, 5)  # Avenir Next Medium
    landmark = get_font(40, 2)

    # Editorial masthead: enough negative space remains around Landmark 81.
    draw_tracking(
        draw,
        (224, 284),
        "SAIGON / VIETNAM",
        font=kicker,
        fill=gold,
        tracking=5,
    )
    draw.rectangle((228, 392, 812, 406), fill=vermilion)
    draw.rectangle((844, 392, 1008, 406), fill=gold)

    def text_with_shadow(x: int, y: int, value: str, font: ImageFont.FreeTypeFont) -> None:
        draw.text((x + 7, y + 9), value, font=font, fill=shadow)
        draw.text(
            (x, y),
            value,
            font=font,
            fill=ivory,
            stroke_width=2,
            stroke_fill=(9, 12, 17, 180),
        )

    text_with_shadow(218, 454, "BRAND NEW", title)
    text_with_shadow(218, 650, "DAY", day)

    draw_tracking(
        draw,
        (226, 956),
        "LANDMARK 81  ·  CINEMATIC CITY PORTRAIT",
        font=descriptor,
        fill=muted,
        tracking=2,
        stroke_width=1,
        stroke_fill=(0, 0, 0, 140),
    )
    draw.rectangle((228, 1064, 246, 1186), fill=vermilion)
    draw_tracking(
        draw,
        (280, 1080),
        "4K  /  NIGHT EDIT",
        font=landmark,
        fill=gold,
        tracking=4,
    )

    # Very thin title-safe frame accent, intentionally outside the text block.
    draw.rectangle((74, 74, WIDTH - 75, HEIGHT - 75), outline=(238, 194, 116, 125), width=3)
    image.alpha_composite(layer)


def save_jpeg_under_limit(image: Image.Image, path: Path, limit: int = 1_950_000) -> int:
    rgb = image.convert("RGB")
    quality_used = 50
    for quality in range(94, 49, -2):
        rgb.save(
            path,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
            subsampling=2,
        )
        quality_used = quality
        if path.stat().st_size <= limit:
            return quality
    return quality_used


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--seconds", type=float, default=36.20)
    args = parser.parse_args()
    video = args.video.resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    image = frame_at(video, args.seconds)
    draw_thumbnail(image)
    stem = "THUMBNAIL_BRAND_NEW_DAY_SAIGON_LANDMARK_81_V4_4K"
    png_path = OUT_DIR / f"{stem}.png"
    jpg_path = OUT_DIR / f"{stem}.jpg"
    image.save(png_path, format="PNG", optimize=True)
    quality = save_jpeg_under_limit(image, jpg_path)
    print(f"source={video}")
    print(f"source_seconds={args.seconds:.3f}")
    print(f"png={png_path} bytes={png_path.stat().st_size}")
    print(f"jpg={jpg_path} bytes={jpg_path.stat().st_size} quality={quality}")


if __name__ == "__main__":
    main()
