#!/usr/bin/env python3
"""Build the standalone TP.HCM end-credit montage.

The montage deliberately uses only locally supplied/licensed live-action city
footage and the user's local ``oh-yeah.mp3``.  Text is rasterised with Pillow
so Vietnamese diacritics are deterministic and never delegated to a video
generator.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1920
HEIGHT = 1080
FPS = 30
# A slightly shorter overlap keeps each credit card legible while making the
# montage feel like a continuous camera move instead of a slideshow.
TRANSITION = 0.55
AUDIO_START = 11.50  # the supplied track's first vocal phrase begins at ~11.52 s
AUDIO_DURATION = 41.00

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "credit_tphcm" / "raw"
WORK = ROOT / "renders" / "credit_tphcm"
OVERLAYS = WORK / "overlays"
SEGMENTS_CREDIT = WORK / "segments_credit"
SEGMENTS_CLEAN = WORK / "segments_clean"
PICTURE_CREDIT = WORK / "picture_credit.mp4"
PICTURE_CLEAN = WORK / "picture_clean.mp4"
QA = ROOT / "qa" / "credit_tphcm"
OUTPUT = ROOT / "CREDIT_TPHCM_OH_YEAH.mp4"
CLEAN_OUTPUT = ROOT / "CREDIT_TPHCM_OH_YEAH_CLEAN.mp4"
AUDIO = ROOT / "oh-yeah.mp3"

FONT_SANS = Path("/System/Library/Fonts/Avenir Next.ttc")
# Avenir Next Condensed lacks several Vietnamese glyphs on this macOS build.
# Use the full Avenir Next face for every card so the encoded PNGs keep all
# diacritics intact.
FONT_CONDENSED = FONT_SANS

PEXELS_URLS = {
    "pexels_aerial_skyline_32427394.mp4": "https://www.pexels.com/video/aerial-view-of-ho-chi-minh-city-skyline-32427394/",
    "pexels_city_hall_39357829.mp4": "https://www.pexels.com/video/vietnam-s-city-hall-and-modern-skyline-view-39357829/",
    "pexels_busy_street_37886978.mp4": "https://www.pexels.com/video/bustling-urban-street-scene-with-skyscrapers-37886978/",
    "pexels_day_night_3963629.mp4": "https://www.pexels.com/video/a-time-lapse-video-of-buildings-from-daylight-to-night-lights-3963629/",
    "pexels_ben_thanh_29185453.mp4": "https://www.pexels.com/video/bustling-night-traffic-near-ben-thanh-market-29185453/",
    "pexels_night_traffic_29185408.mp4": "https://www.pexels.com/video/bustling-night-traffic-in-vibrant-urban-cityscape-29185408/",
    "pexels_night_skyline_31111952.mp4": "https://www.pexels.com/video/aerial-night-view-of-ho-chi-minh-city-skyline-31111952/",
    "pexels_river_skyline_31975717.mp4": "https://www.pexels.com/video/ho-chi-minh-city-skyline-over-saigon-river-31975715/",
    "pexels_landmark_31111825.mp4": "https://www.pexels.com/video/aerial-night-view-of-ho-chi-minh-city-skyline-31111825/",
    "motorbikers_cc0.jpg": "https://commons.wikimedia.org/wiki/File:Ho_Chi_Minh_City_motorbikers_(Unsplash_LhENdA-0yCM).jpg",
}


SHOTS: list[dict[str, object]] = [
    {
        "id": "C01",
        "file": "pexels_aerial_skyline_32427394.mp4",
        "source_start": 0.8,
        "duration": 5.4,
        "overlay": "title",
        "purpose": "Mở bằng toàn cảnh đô thị và nhận diện phim.",
    },
    {
        "id": "C02",
        "file": "pexels_city_hall_39357829.mp4",
        "source_start": 0.4,
        "duration": 5.0,
        "overlay": "producer",
        "purpose": "Đặt bối cảnh TP.HCM và tên nhóm.",
    },
    {
        "id": "C03",
        "file": "pexels_busy_street_37886978.mp4",
        "source_start": 3.2,
        "duration": 5.2,
        "overlay": "teacher",
        "purpose": "Đưa nhịp sống đường phố vào phần credit.",
    },
    {
        "id": "C04",
        "file": "pexels_day_night_3963629.mp4",
        "source_start": 7.0,
        "duration": 5.5,
        "overlay": "members_a",
        "purpose": "Chuyển ngày sang tối, hiển thị bốn thành viên đầu.",
    },
    {
        "id": "C05",
        "file": "pexels_ben_thanh_29185453.mp4",
        "source_start": 0.0,
        "duration": 4.7,
        "overlay": "members_b",
        "purpose": "Nhịp cắt có chuyển động thật tại Bến Thành.",
    },
    {
        "id": "C06",
        "file": "pexels_night_skyline_31111952.mp4",
        "source_start": 4.8,
        "duration": 4.3,
        "overlay": None,
        "purpose": "Một nhịp thở chuyển động thật trên skyline đêm, thay cho ảnh tĩnh bị khựng.",
    },
    {
        "id": "C07",
        "file": "pexels_night_traffic_29185408.mp4",
        "source_start": 0.4,
        "duration": 3.8,
        "overlay": None,
        "purpose": "Khoảng thở hình ảnh sau danh sách thành viên.",
    },
    {
        "id": "C08",
        "file": "pexels_river_skyline_31975717.mp4",
        "source_start": 1.0,
        "duration": 3.25,
        "overlay": None,
        "purpose": "Hạ nhịp trên mặt nước trước lời cảm ơn.",
    },
    {
        "id": "C09",
        "file": "pexels_landmark_31111825.mp4",
        "source_start": 2.2,
        "duration": 8.25,
        "overlay": "thanks",
        "purpose": "Khung kết đêm, giữ lời cảm ơn đủ lâu để đọc.",
    },
]


def run(cmd: list[str]) -> None:
    print("$", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def font(path: Path, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size, index=index)


def bold(size: int) -> ImageFont.FreeTypeFont:
    # Index 0 is Avenir Next Bold.  The italic face (index 1) on some macOS
    # builds misses Vietnamese combining marks, so it is intentionally not
    # used for production overlays.
    return font(FONT_SANS, size, 0)


def regular(size: int) -> ImageFont.FreeTypeFont:
    return font(FONT_SANS, size, 7)


def text_width(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0]


def draw_shadow_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    face: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    *,
    anchor: str | None = None,
    shadow: int = 8,
) -> None:
    # The previous two-offset drop shadow produced a visible ghost/"lòe" on
    # Vietnamese diacritics.  Use one restrained, pixel-tight outline instead;
    # it keeps type crisp over moving footage without a second glyph layer.
    outline_width = max(1, min(2, int(getattr(face, "size", 32) / 32)))
    draw.text(
        xy,
        text,
        font=face,
        fill=fill,
        anchor=anchor,
        stroke_width=outline_width,
        stroke_fill=(3, 7, 9, 165),
    )


def add_left_gradient(image: Image.Image, top: int = 510, bottom: int = 1080) -> None:
    """Add an unobtrusive cinematic readability gradient, not a UI card."""
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    px = layer.load()
    for y in range(top, bottom):
        amount = (y - top) / max(1, bottom - top)
        alpha = int(120 + 95 * amount)
        for x in range(0, 1180):
            horizontal = 1.0 - (x / 1180.0) * 0.55
            px[x, y] = (7, 12, 15, int(alpha * horizontal))
    image.alpha_composite(layer)


def add_rule(image: Image.Image, x: int, y: int, width: int = 340) -> None:
    draw = ImageDraw.Draw(image)
    draw.rectangle((x, y, x + width, y + 4), fill=(218, 91, 61, 235))
    draw.rectangle((x + width + 18, y, x + width + 72, y + 4), fill=(231, 198, 126, 210))


def add_rounded_panel(
    image: Image.Image,
    box: tuple[int, int, int, int],
    *,
    radius: int = 36,
    fill: tuple[int, int, int, int] = (7, 13, 17, 174),
) -> None:
    """Add one polished translucent credit surface with a soft outer shadow."""
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x0 + 4, y0 + 12, x1 + 4, y1 + 12),
        radius=radius,
        fill=(0, 0, 0, 118),
    )
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20)))

    panel = Image.new("RGBA", image.size, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=(239, 221, 178, 102),
        width=2,
    )
    panel_draw.rounded_rectangle(
        (x0 + 8, y0 + 8, x1 - 8, y1 - 8),
        radius=max(8, radius - 8),
        outline=(255, 247, 224, 28),
        width=1,
    )
    image.alpha_composite(panel)


def base_overlay() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    # A fine, barely visible frame keeps all typography inside title-safe.
    frame = Image.new("RGBA", image.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.line((72, 72, 72, 1008), fill=(239, 221, 178, 80), width=1)
    fd.line((72, 1008, 1848, 1008), fill=(239, 221, 178, 52), width=1)
    image.alpha_composite(frame)
    return image


def make_title() -> Image.Image:
    image = base_overlay()
    add_rounded_panel(image, (86, 606, 1115, 984), radius=38, fill=(7, 13, 17, 162))
    draw = ImageDraw.Draw(image)
    kicker = bold(24)
    title = bold(65)
    sub = regular(30)
    draw_shadow_text(draw, (126, 650), "PHILOSOPHY VIDEO ESSAY  ·  NHÓM 14", kicker, (239, 221, 178, 245))
    draw_shadow_text(draw, (126, 695), "DÂN CHỦ HÓA THIẾT KẾ", title, (250, 245, 232, 255))
    draw_shadow_text(draw, (126, 770), "VÀ QUẢN TRỊ CÔNG NGHỆ", title, (250, 245, 232, 255))
    add_rule(image, 126, 866, 290)
    draw_shadow_text(draw, (126, 900), "THEO ANDREW FEENBERG", sub, (228, 217, 195, 235))
    return image


def make_producer() -> Image.Image:
    image = base_overlay()
    add_rounded_panel(image, (86, 630, 1125, 970), radius=38, fill=(7, 13, 17, 166))
    draw = ImageDraw.Draw(image)
    small = bold(25)
    big = bold(78)
    body = regular(30)
    draw_shadow_text(draw, (126, 690), "MỘT SẢN PHẨM CỦA", small, (239, 221, 178, 245))
    draw_shadow_text(draw, (126, 730), "NHÓM 14", big, (250, 245, 232, 255))
    add_rule(image, 126, 840, 220)
    draw_shadow_text(draw, (126, 875), "MÔN TRIẾT HỌC  ·  PH2001.26.1.CH.02", body, (228, 217, 195, 235))
    return image


def make_teacher() -> Image.Image:
    image = base_overlay()
    add_rounded_panel(image, (86, 630, 1115, 970), radius=38, fill=(7, 13, 17, 168))
    draw = ImageDraw.Draw(image)
    small = bold(25)
    big = bold(68)
    draw_shadow_text(draw, (126, 690), "GIẢNG VIÊN", small, (239, 221, 178, 245))
    draw_shadow_text(draw, (126, 735), "TS NGUYỄN HỮU SƠN", big, (250, 245, 232, 255))
    add_rule(image, 126, 840, 220)
    draw_shadow_text(draw, (126, 878), "HỌC PHẦN TRIẾT HỌC", regular(30), (228, 217, 195, 235))
    return image


def make_members(rows: list[tuple[str, str]], range_label: str) -> Image.Image:
    image = base_overlay()
    # One carefully aligned, double-stroked panel keeps the roster legible
    # without looking like a generic UI card.
    panel_box = (94, 242, 1234, 930)
    add_rounded_panel(image, panel_box, radius=42, fill=(7, 13, 17, 186))
    draw = ImageDraw.Draw(image)
    header = bold(25)
    column_face = bold(19)
    name_face = bold(32)
    id_face = regular(27)
    x_left = 158
    x_right = 1168

    draw_shadow_text(draw, (x_left, 294), "THÀNH VIÊN NHÓM 14", header, (239, 221, 178, 250))
    draw_shadow_text(draw, (x_right, 294), range_label, header, (239, 221, 178, 238), anchor="ra")
    add_rule(image, x_left, 344, 230)
    draw_shadow_text(draw, (x_left, 378), "HỌ VÀ TÊN", column_face, (202, 194, 177, 224))
    draw_shadow_text(draw, (x_right, 378), "MSHV", column_face, (202, 194, 177, 224), anchor="ra")
    draw.line((x_left, 420, x_right, 420), fill=(239, 221, 178, 62), width=1)

    content_top = 438
    content_bottom = 884
    row_height = (content_bottom - content_top) / len(rows)
    for index, (name, student_id) in enumerate(rows):
        center_y = int(content_top + (index + 0.5) * row_height)
        draw_shadow_text(draw, (x_left, center_y), name, name_face, (250, 245, 232, 255), anchor="lm")
        draw_shadow_text(draw, (x_right, center_y), student_id, id_face, (226, 216, 198, 248), anchor="rm")
        if index < len(rows) - 1:
            separator_y = int(content_top + (index + 1) * row_height)
            draw.line((x_left, separator_y, x_right, separator_y), fill=(239, 221, 178, 42), width=1)
    return image


def make_thanks() -> Image.Image:
    image = base_overlay()
    # A centered, transparent veil allows the final night skyline to remain
    # visible while keeping the closing line readable.
    veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rounded_rectangle((250, 300, 1670, 790), radius=24, fill=(6, 12, 16, 142), outline=(239, 221, 178, 90), width=1)
    image.alpha_composite(veil)
    draw = ImageDraw.Draw(image)
    kicker = bold(25)
    big = bold(75)
    body = regular(30)
    draw_shadow_text(draw, (960, 410), "LỜI CẢM ƠN", kicker, (239, 221, 178, 250), anchor="mm")
    draw_shadow_text(draw, (960, 495), "CẢM ƠN THẦY VÀ CÁC BẠN", big, (250, 245, 232, 255), anchor="mm")
    add_rule(image, 710, 620, 280)
    draw_shadow_text(draw, (960, 690), "NHÓM 14  ·  PH2001.26.1.CH.02", body, (228, 217, 195, 240), anchor="mm")
    return image


def make_overlays() -> dict[str, Path]:
    OVERLAYS.mkdir(parents=True, exist_ok=True)
    data = {
        "title": make_title(),
        "producer": make_producer(),
        "teacher": make_teacher(),
        "members_a": make_members(
            [
                ("CHU NAM THẮNG", "26848201"),
                ("VŨ NGỌC QUỐC KHÁNH", "26848097"),
                ("NGUYỄN LƯU MINH ĐĂNG", "26848028"),
                ("ĐẶNG THỊ THUÝ HỒNG", "26848070"),
            ],
            "01 — 04",
        ),
        "members_b": make_members(
            [
                ("LÂM MINH THIỆN", "26848210"),
                ("HOÀNG VŨ", "26848267"),
                ("ĐÀO HOÀNG PHÚC", "26848169"),
            ],
            "05 — 07",
        ),
        "thanks": make_thanks(),
    }
    result: dict[str, Path] = {}
    for key, image in data.items():
        path = OVERLAYS / f"{key}.png"
        image.save(path, optimize=True)
        result[key] = path
    return result


def grade_look_filter() -> str:
    """One shared filmic yellow/olive look for footage and stills.

    The lifted toe and soft shoulder keep shadow detail and highlight texture
    intact at Full HD.  Warm highlights and a trace of teal in the shadows
    echo the supplied cinematic reference without turning skin or lights neon.
    """
    return (
        "eq=contrast=0.96:brightness=-0.018:saturation=0.82:gamma=1.02,"
        "colorbalance=rs=-0.015:gs=0.018:bs=0.035:"
        "rm=0.025:gm=0.012:bm=-0.035:"
        "rh=0.055:gh=0.028:bh=-0.075:pl=1,"
        "curves=all='0/0.025 0.18/0.15 0.50/0.52 0.82/0.87 1/0.965',"
        "unsharp=5:5:0.35:3:3:0.12,"
        "vignette=PI/10,noise=alls=0.35:allf=t+u,format=yuv420p"
    )


def grade_filter() -> str:
    return (
        "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1920:1080,setsar=1,fps=30," + grade_look_filter()
    )


def still_motion_filter(duration: float) -> str:
    """Create a restrained, physically honest Ken Burns move on a still."""
    frames = max(1, int(round(duration * FPS)))
    return (
        "scale=2400:-1:flags=lanczos,"
        "zoompan=z='min(zoom+0.00024,1.032)':"
        "x='iw/2-(iw/zoom/2)':y='ih*0.49-(ih/zoom/2)':"
        f"d={frames}:s=1920x1080:fps={FPS},trim=duration={duration:.3f},"
        "setpts=PTS-STARTPTS,setsar=1," + grade_look_filter()
    )


def render_segment(
    index: int,
    shot: dict[str, object],
    overlay: Path | None,
    force: bool,
    segment_dir: Path,
) -> Path:
    segment_dir.mkdir(parents=True, exist_ok=True)
    out = segment_dir / f"{shot['id']}.mp4"
    if out.exists() and not force:
        return out
    source = RAW / str(shot["file"])
    duration = float(shot["duration"])
    source_start = float(shot["source_start"])
    is_still = source.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    vf = still_motion_filter(duration) if is_still else grade_filter()
    source_args = (
        ["-loop", "1", "-framerate", "1", "-i", str(source)]
        if is_still
        else ["-ss", f"{source_start:.3f}", "-i", str(source)]
    )
    if overlay is None:
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            *source_args,
            "-t", f"{duration:.3f}", "-vf", vf,
            "-r", str(FPS), "-c:v", "libx264", "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium",
            "-an", str(out),
        ]
    else:
        # Keep text out of the xfade overlap.  If both the outgoing and
        # incoming cards are visible during the dissolve, glyphs appear to
        # double (especially Vietnamese diacritics).  Fade the old card out
        # before the dissolve starts and bring the new card in just after it
        # ends; the picture itself still receives the smooth 0.55 s xfade.
        is_first = index == 0
        is_last = index == len(SHOTS) - 1
        fade_in_start = 0.0 if is_first else TRANSITION + 0.10
        fade_in_duration = 0.35
        fade_out_end = duration if is_last else max(0.45, duration - TRANSITION)
        fade_out_start = max(fade_in_start + fade_in_duration, fade_out_end - 0.35)
        overlay_filter = (
            f"[{1}:v]format=rgba,fade=t=in:st={fade_in_start:.3f}:d={fade_in_duration:.3f}:alpha=1,"
            f"fade=t=out:st={fade_out_start:.3f}:d=0.35:alpha=1[ov];"
            f"[0:v]{vf}[base];[base][ov]overlay=0:0:format=auto,format=yuv420p[out]"
        )
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            *source_args,
            "-loop", "1", "-framerate", str(FPS), "-i", str(overlay),
            "-filter_complex", overlay_filter, "-map", "[out]",
            "-t", f"{duration:.3f}", "-r", str(FPS), "-c:v", "libx264",
            "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "17",
            "-preset", "medium", "-an", str(out),
        ]
    run(cmd)
    return out


def assemble_video(segments: list[Path], clean_output: Path, force: bool) -> None:
    if clean_output.exists() and not force:
        return
    inputs: list[str] = []
    for path in segments:
        inputs.extend(["-i", str(path)])
    filters: list[str] = []
    previous = "[0:v]"
    cumulative = float(SHOTS[0]["duration"])
    for i in range(1, len(segments)):
        out = f"[v{i}]"
        offset = cumulative - TRANSITION
        filters.append(
            f"{previous}[{i}:v]xfade=transition=fade:duration={TRANSITION:.3f}:offset={offset:.3f}{out}"
        )
        previous = out
        cumulative += float(SHOTS[i]["duration"]) - TRANSITION
    filters.append(f"{previous}format=yuv420p[vout]")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        *inputs, "-filter_complex", ";".join(filters), "-map", "[vout]",
        "-r", str(FPS), "-an", "-c:v", "libx264", "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium",
        "-movflags", "+faststart", str(clean_output),
    ]
    run(cmd)


def timeline_starts() -> list[float]:
    """Return each shot's start time after accounting for xfade overlaps."""
    starts: list[float] = []
    cursor = 0.0
    for index, shot in enumerate(SHOTS):
        starts.append(cursor)
        cursor += float(shot["duration"])
        if index < len(SHOTS) - 1:
            cursor -= TRANSITION
    return starts


def compose_credit_overlay(
    clean_video: Path,
    overlays: dict[str, Path],
    output: Path,
    force: bool,
) -> None:
    """Composite crisp credit cards only after the clean picture is assembled.

    Doing the picture dissolves first prevents outgoing and incoming Vietnamese
    glyphs from being blended together during an xfade.  Every card receives
    its own short fade and stays completely clear of neighbouring transitions.
    """
    if output.exists() and not force:
        return

    starts = timeline_starts()
    entries: list[tuple[int, Path, float, float, bool]] = []
    for index, shot in enumerate(SHOTS):
        overlay_key = shot.get("overlay")
        if not overlay_key:
            continue

        shot_start = starts[index]
        shot_end = shot_start + float(shot["duration"])
        is_first = index == 0
        is_last = index == len(SHOTS) - 1
        visible_start = shot_start if is_first else shot_start + TRANSITION + 0.10
        visible_end = shot_end if is_last else shot_end - TRANSITION - 0.10
        if visible_end <= visible_start:
            raise ValueError(f"Overlay window is empty for {shot['id']}")
        entries.append((index, overlays[str(overlay_key)], visible_start, visible_end, is_last))

    input_args: list[str] = ["-i", str(clean_video)]
    for _, overlay_path, _, _, _ in entries:
        input_args.extend(["-loop", "1", "-framerate", str(FPS), "-i", str(overlay_path)])

    filters: list[str] = []
    previous = "[0:v]"
    for input_index, (shot_index, _, visible_start, visible_end, is_last) in enumerate(entries, start=1):
        visible_duration = visible_end - visible_start
        fade_in = min(0.32, visible_duration / 4.0)
        fade_out = min(1.05 if is_last else 0.32, visible_duration / 3.0)
        fade_out_start = max(fade_in, visible_duration - fade_out)
        overlay_label = f"[ov{shot_index}]"
        output_label = f"[credit{shot_index}]"
        filters.append(
            f"[{input_index}:v]format=rgba,trim=duration={visible_duration:.3f},"
            "setpts=PTS-STARTPTS,"
            f"fade=t=in:st=0:d={fade_in:.3f}:alpha=1,"
            f"fade=t=out:st={fade_out_start:.3f}:d={fade_out:.3f}:alpha=1,"
            f"setpts=PTS+{visible_start:.3f}/TB{overlay_label}"
        )
        filters.append(
            f"{previous}{overlay_label}overlay=0:0:format=auto:eof_action=pass:repeatlast=0:"
            f"enable='between(t,{visible_start:.3f},{visible_end:.3f})'{output_label}"
        )
        previous = output_label
    filters.append(f"{previous}format=yuv420p[vout]")

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        *input_args,
        "-filter_complex", ";".join(filters), "-map", "[vout]",
        "-t", f"{AUDIO_DURATION:.3f}", "-r", str(FPS), "-an",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-crf", "17", "-preset", "medium",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-movflags", "+faststart", str(output),
    ]
    run(cmd)


def mux_audio(clean_video: Path, output: Path, force: bool) -> None:
    if output.exists() and not force:
        return
    # Start immediately before the supplied track's first vocal phrase.  The
    # 40 ms ramp is only an anti-click guard and does not hide the consonant.
    audio_end = AUDIO_START + AUDIO_DURATION
    audio_filter = (
        f"atrim=start={AUDIO_START:.3f}:end={audio_end:.3f},asetpts=PTS-STARTPTS,"
        "afade=t=in:st=0:d=0.04,afade=t=out:st=38.65:d=2.35,"
        "loudnorm=I=-14.5:TP=-1.5:LRA=11:linear=true"
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(clean_video), "-i", str(AUDIO),
        "-filter_complex", f"[1:a]{audio_filter}[aout]",
        "-map", "0:v:0", "-map", "[aout]", "-t", f"{AUDIO_DURATION:.3f}",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-ac", "2", "-movflags", "+faststart", str(output),
    ]
    run(cmd)


def write_manifest(overlays: dict[str, Path]) -> None:
    start = 0.0
    rows = []
    for shot in SHOTS:
        end = start + float(shot["duration"])
        rows.append(
            {
                "scene_id": shot["id"],
                "timeline_start": round(start, 3),
                "timeline_end_before_xfade": round(end, 3),
                "duration": shot["duration"],
                "source": shot["file"],
                "source_url": PEXELS_URLS.get(str(shot["file"])),
                "source_start": shot["source_start"],
                "reuse_count": 1,
                "visual_type": (
                    "real documentary photograph with subtle Ken Burns move"
                    if Path(str(shot["file"])).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
                    else "real live-action footage"
                ),
                "overlay": shot["overlay"],
                "purpose": shot["purpose"],
            }
        )
        start = end - TRANSITION if shot is not SHOTS[-1] else end
    manifest = {
        "deliverable": OUTPUT.name,
        "duration_seconds": AUDIO_DURATION,
        "audio_source": str(AUDIO.relative_to(ROOT)),
        "audio_segment": f"{AUDIO_START:.3f}–{AUDIO_START + AUDIO_DURATION:.3f} s; starts on first Come on phrase",
        "visual_rule": "real TP.HCM footage/photography only; no AI-generated city imagery",
        "grade": "filmic yellow/olive highlights, slight teal shadows, lifted toe, soft highlight roll-off, restrained grain",
        "transition": f"dissolve {TRANSITION:.2f}s",
        "credit_compositing": "picture dissolves first; typography is composited afterward with isolated fades outside xfade windows",
        "shots": rows,
        "overlays": {key: str(path.relative_to(ROOT)) for key, path in overlays.items()},
        "credits": {
            "group": "Nhóm 14",
            "class": "PH2001.26.1.CH.02",
            "course": "Triết học",
            "lecturer": "TS Nguyễn Hữu Sơn",
            "learner_id_label": "MSHV",
            "members": [
                ["Chu Nam Thắng", "26848201"],
                ["Vũ Ngọc Quốc Khánh", "26848097"],
                ["Nguyễn Lưu Minh Đăng", "26848028"],
                ["Đặng Thị Thuý Hồng", "26848070"],
                ["Lâm Minh Thiện", "26848210"],
                ["Hoàng Vũ", "26848267"],
                ["Đào Hoàng Phúc", "26848169"],
            ],
        },
    }
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "credit_source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (QA / "credit_storyboard.csv").write_text(
        "scene_id,start_time,end_time,source,overlay,purpose\n"
        + "\n".join(
            f"{row['scene_id']},{row['timeline_start']:.3f},{row['timeline_end_before_xfade']:.3f},{row['source']},{row['overlay']},{row['purpose']}"
            for row in rows
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not AUDIO.is_file():
        raise FileNotFoundError(AUDIO)
    for shot in SHOTS:
        source = RAW / str(shot["file"])
        if not source.is_file():
            raise FileNotFoundError(source)
    if args.force:
        for segment_dir in (SEGMENTS_CREDIT, SEGMENTS_CLEAN):
            for path in segment_dir.glob("C*.mp4"):
                path.unlink()
        for path in (PICTURE_CREDIT, PICTURE_CLEAN, CLEAN_OUTPUT, OUTPUT):
            if path.exists():
                path.unlink()
    overlays = make_overlays()
    clean_segments = [
        render_segment(i, shot, None, args.force, SEGMENTS_CLEAN)
        for i, shot in enumerate(SHOTS)
    ]
    assemble_video(clean_segments, PICTURE_CLEAN, args.force)
    compose_credit_overlay(PICTURE_CLEAN, overlays, PICTURE_CREDIT, args.force)
    mux_audio(PICTURE_CREDIT, OUTPUT, args.force)
    mux_audio(PICTURE_CLEAN, CLEAN_OUTPUT, args.force)
    write_manifest(overlays)
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {CLEAN_OUTPUT}")


if __name__ == "__main__":
    main()
