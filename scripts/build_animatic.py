#!/usr/bin/env python3
"""Build an internal 1080p timing animatic from storyboard and approved post assets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1920
HEIGHT = 1080
FONT_PATH = Path("/System/Library/Fonts/Avenir Next.ttc")
OBSIDIAN = "#0B0F14"
DEEP_NAVY = "#13202A"
WARM_PAPER = "#E8E1D3"
MUTED = "#9BA7AF"
AMBER = "#E6A23C"
TEAL = "#48B8A6"
RED = "#C75B5B"


ASSET_MAP = {
    "S005": "assets/graphics/S005_title_overlay.png",
    "S016": "assets/source_pages/crops/S016_S01_p05_matrix_crop.png",
    "S018": "assets/graphics/S018_S024_matrix_full.png",
    "S019": "assets/graphics/S018_S024_matrix_full.png",
    "S020": "assets/graphics/S018_S024_matrix_full.png",
    "S021": "assets/graphics/S018_S024_matrix_full.png",
    "S022": "assets/graphics/S018_S024_matrix_full.png",
    "S023": "assets/graphics/S018_S024_matrix_full.png",
    "S024": "assets/graphics/S018_S024_matrix_full.png",
    "S025": "assets/source_pages/crops/S025_S01_p09_critical_theory_crop.png",
    "S036": "assets/source_pages/crops/S036_S03_p05_underdetermination_crop.png",
    "S041": "assets/graphics/S041_technical_code_layers.png",
    "S042": "assets/source_pages/crops/S042_S03_p13_technical_code_definition_crop.png",
    "S048": "assets/source_pages/crops/S048_S02_p24_condensed_relations_crop.png",
    "S056": "assets/source_pages/crops/S056_S03_p18_participation_crop.png",
    "S058": "assets/graphics/S058_access_not_participation.png",
    "S062": "assets/graphics/S062_participation_loop.png",
    "S064": "assets/source_pages/crops/S064_S02_p10_network_origin_crop.png",
    "S070": "assets/source_pages/crops/S070_S02_p11_design_change_crop.png",
    "S076": "assets/source_pages/crops/S076_S02_p12_priority_list_crop.png",
    "S077": "assets/graphics/S077_ALS_evidence_limit.png",
    "S082": "assets/graphics/S082_five_questions_full.png",
    "S083": "assets/graphics/S083_question_1_overlay.png",
    "S084": "assets/graphics/S084_question_2_overlay.png",
    "S085": "assets/graphics/S085_question_3_overlay.png",
    "S086": "assets/graphics/S086_question_4_overlay.png",
    "S087": "assets/graphics/S087_question_5_overlay.png",
    "S089": "assets/graphics/S089_five_criteria.png",
    "S094": "assets/graphics/S094_methodological_motif.png",
    "S097": "assets/graphics/S097_course_credit.png",
    "S098": "assets/graphics/S098_members_credit.png",
    "S099": "assets/graphics/S099_sources_a.png",
    "S100": "assets/graphics/S100_disclosure.png",
}


def font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def text_width(draw: ImageDraw.ImageDraw, value: str, text_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=text_font)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, value: str, text_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = value.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if text_width(draw, candidate, text_font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit_asset(path: Path) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    if source.width == 3840 and source.height == 2160:
        return source.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    background = Image.new("RGBA", (WIDTH, HEIGHT), OBSIDIAN)
    max_width, max_height = 1650, 800
    scale = min(max_width / source.width, max_height / source.height)
    fitted = source.resize(
        (max(1, round(source.width * scale)), max(1, round(source.height * scale))),
        Image.Resampling.LANCZOS,
    )
    x = (WIDTH - fitted.width) // 2
    y = (HEIGHT - fitted.height) // 2
    shadow = Image.new("RGBA", background.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x - 24, y - 24, x + fitted.width + 24, y + fitted.height + 24), radius=18, fill=(0, 0, 0, 140))
    background.alpha_composite(shadow)
    background.alpha_composite(fitted, (x, y))
    return background


def placeholder(row: dict[str, str]) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), OBSIDIAN)
    draw = ImageDraw.Draw(image)
    digest = hashlib.sha256(row["SCENE_ID"].encode()).digest()
    accent = TEAL if "CONCEPT" in row["VISUAL_TYPE"] or "DIAGRAM" in row["VISUAL_TYPE"] else AMBER
    draw.rectangle((0, 0, WIDTH, 140), fill=DEEP_NAVY)
    draw.line((95, 140, WIDTH - 95, 140), fill=accent, width=3)
    draw.text((110, 50), "ANIMATIC NỘI BỘ · CHƯA PHẢI HÌNH CUỐI", font=font(31), fill=RED)
    draw.text((110, 230), row["SCENE_ID"], font=font(128), fill=accent)
    # Avenir Next's Pillow face does not expose the Unicode arrow glyph on
    # every macOS build. Keep the internal timing range ASCII-only so a
    # missing-glyph box can never be mistaken for bad Vietnamese typography.
    draw.text((110, 390), f"{row['START_TIME']}  |  {row['END_TIME']}", font=font(42), fill=MUTED)
    draw.text((110, 505), row["VISUAL_TYPE"], font=font(36), fill=WARM_PAPER)

    y = 615
    for line in wrap(draw, row["VISUAL_DESCRIPTION"], font(44), 1490)[:5]:
        draw.text((110, y), line, font=font(44), fill=WARM_PAPER)
        y += 62

    x0 = 1580
    for index in range(5):
        size = 42 + digest[index] % 115
        x = x0 + (digest[index + 5] % 190) - 70
        y_shape = 270 + index * 135
        if index % 2:
            draw.ellipse((x, y_shape, x + size, y_shape + size), outline=accent, width=4)
        else:
            draw.rounded_rectangle((x, y_shape, x + size, y_shape + size), radius=12, outline=accent, width=4)
    return image


def add_animatic_mark(image: Image.Image, scene_id: str) -> None:
    draw = ImageDraw.Draw(image)
    label = f"ANIMATIC · {scene_id} · KHÔNG PHẢI BẢN NỘP"
    label_font = font(27)
    width = text_width(draw, label, label_font)
    draw.rounded_rectangle((WIDTH - width - 95, 32, WIDTH - 45, 86), radius=12, fill=(11, 15, 20, 210))
    draw.text((WIDTH - width - 70, 44), label, font=label_font, fill=RED)


def parse_seconds(value: str) -> float:
    normalized = value.replace(",", ".")
    parts = normalized.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise ValueError(f"Unsupported timestamp: {value}")


def parse_srt(path: Path) -> list[dict[str, object]]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    cues: list[dict[str, object]] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            raise ValueError(f"Invalid SRT block: {block}")
        start_value, end_value = (value.strip() for value in lines[1].split("-->", 1))
        cues.append(
            {
                "start": parse_seconds(start_value),
                "end": parse_seconds(end_value),
                "lines": lines[2:],
            }
        )
    return cues


def draw_subtitle(image: Image.Image, lines: list[str]) -> None:
    if not lines:
        return
    draw = ImageDraw.Draw(image)
    subtitle_font = font(52)
    line_height = 65
    widths = [text_width(draw, line, subtitle_font) for line in lines]
    box_width = max(widths) + 76
    box_height = len(lines) * line_height + 34
    x0 = (WIDTH - box_width) // 2
    y1 = HEIGHT - 58
    y0 = y1 - box_height
    draw.rounded_rectangle((x0, y0, x0 + box_width, y1), radius=16, fill=(0, 0, 0, 190))
    y = y0 + 10
    for line, width in zip(lines, widths):
        draw.text(((WIDTH - width) // 2, y), line, font=subtitle_font, fill="#F7F4ED")
        y += line_height


def build(storyboard: Path, subtitles: Path, project_dir: Path, output_dir: Path) -> None:
    with storyboard.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 100:
        raise SystemExit("Storyboard must contain exactly 100 scenes")
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes: list[dict[str, object]] = []
    previous_end = "00:00:00"
    for row in rows:
        if row["START_TIME"] != previous_end:
            raise SystemExit(f"Timeline gap/overlap at {row['SCENE_ID']}")
        scene_id = row["SCENE_ID"]
        asset_relative = ASSET_MAP.get(scene_id)
        if asset_relative:
            asset_path = project_dir / asset_relative
            if not asset_path.is_file():
                raise SystemExit(f"Mapped animatic asset missing: {asset_path}")
            image = fit_asset(asset_path)
            if image.getbbox() is None:
                image = placeholder(row)
            elif asset_path.name.endswith("_overlay.png") or asset_path.name == "S005_title_overlay.png":
                background = placeholder(row)
                background.alpha_composite(image)
                image = background
        else:
            image = placeholder(row)
        add_animatic_mark(image, scene_id)
        output_path = output_dir / f"{scene_id}.png"
        image.convert("RGB").save(output_path, format="PNG", optimize=True)
        scenes.append(
            {
                "scene_id": scene_id,
                "start": parse_seconds(row["START_TIME"]),
                "end": parse_seconds(row["END_TIME"]),
                "path": output_path,
            }
        )
        previous_end = row["END_TIME"]

    cues = parse_srt(subtitles)
    boundaries = {0.0, parse_seconds(previous_end)}
    for scene in scenes:
        boundaries.add(float(scene["start"]))
        boundaries.add(float(scene["end"]))
    for cue in cues:
        boundaries.add(float(cue["start"]))
        boundaries.add(float(cue["end"]))
    ordered = sorted(boundaries)

    segment_dir = output_dir / "segments"
    segment_dir.mkdir(parents=True, exist_ok=True)
    concat_lines = ["ffconcat version 1.0"]
    scene_index = 0
    cue_index = 0
    last_segment_path: Path | None = None
    for segment_index, (start, end) in enumerate(zip(ordered, ordered[1:]), start=1):
        if end - start < 0.015:
            continue
        midpoint = (start + end) / 2
        while scene_index + 1 < len(scenes) and midpoint >= float(scenes[scene_index]["end"]):
            scene_index += 1
        scene = scenes[scene_index]
        while cue_index + 1 < len(cues) and midpoint >= float(cues[cue_index]["end"]):
            cue_index += 1
        active_lines: list[str] = []
        cue = cues[cue_index]
        if float(cue["start"]) <= midpoint < float(cue["end"]):
            active_lines = list(cue["lines"])

        composite = Image.open(Path(scene["path"])).convert("RGB")
        draw_subtitle(composite, active_lines)
        segment_path = segment_dir / f"SEG_{segment_index:04d}.jpg"
        composite.save(segment_path, format="JPEG", quality=92, subsampling=0, optimize=True)
        concat_lines.append(f"file '{segment_path}'")
        concat_lines.append(f"duration {end - start:.6f}")
        last_segment_path = segment_path

    if last_segment_path is None:
        raise SystemExit("No animatic timeline segments were generated")
    concat_lines.append(f"file '{last_segment_path}'")
    concat_path = output_dir / "animatic.ffconcat"
    concat_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    print(f"Built {len(rows)} animatic slates and {len(concat_lines) // 2} timed segments; end {previous_end}")
    print(f"Concat manifest: {concat_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--subtitles", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(
        args.storyboard.resolve(),
        args.subtitles.resolve(),
        args.project_dir.resolve(),
        args.output_dir.resolve(),
    )


if __name__ == "__main__":
    main()
