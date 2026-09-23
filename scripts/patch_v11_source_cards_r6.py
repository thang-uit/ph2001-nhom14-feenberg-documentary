#!/opt/homebrew/bin/python3.13
"""Patch the nine locked source cards without touching their document crops.

R6 is intentionally a surgical typography patch over the existing R5 cards:

* remove the full-width cobalt rail that crossed the kicker;
* remove the unnecessary highlighted-crop disclosure;
* replace the unsupported right-arrow glyph in S070 with safe wording.

The verified document crop, citation, framing, colours and all other card
content remain pixel-identical outside the explicitly patched bands.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 2560, 1440
FONT = "/System/Library/Fonts/Avenir Next.ttc"
IVORY = (244, 239, 229)
END_TONE = (229, 223, 211)
COBALT = (27, 74, 137)
VERMILION = (211, 73, 54)
SAGE = (112, 132, 117)

SCENE_IDS = ("S016", "S025", "S036", "S042", "S048", "S056", "S064", "S070", "S076")
S070_TITLE = "NGƯỜI DÙNG CHIẾM DỤNG · THIẾT KẾ THAY ĐỔI"
S070_SOURCE_TAG = "S02 · PDF tr. 11"


def font(size: int, index: int = 7) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size=size, index=index)


def gradient_colour(y: int) -> tuple[int, int, int]:
    progress = y / H
    return tuple(
        round(start + (end - start) * progress * 0.22)
        for start, end in zip(IVORY, END_TONE)
    )


def clear_band(draw: ImageDraw.ImageDraw, top: int, bottom: int) -> None:
    for y in range(top, bottom + 1):
        draw.line((0, y, W - 1, y), fill=gradient_colour(y), width=1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def patch_card(scene_id: str, source: Path, output: Path) -> dict[str, object]:
    image = Image.open(source).convert("RGB")
    if image.size != (W, H):
        raise ValueError(f"Unexpected source-card size for {scene_id}: {image.size}")
    draw = ImageDraw.Draw(image)

    # Remove the old rail and reconstruct only the red anchor + kicker.  The
    # rail is not relocated, so it cannot intersect the text through a font-
    # metric or renderer difference later.
    clear_band(draw, 82, 174)
    draw.rectangle((110, 100, 132, 154), fill=VERMILION)
    draw.text((170, 104), "ĐỐI CHIẾU VĂN BẢN GỐC", font=font(28, 2), fill=COBALT)

    # Remove the left disclosure while preserving the bottom colour rail and
    # the small project signature on the right.
    clear_band(draw, 1292, 1372)
    draw.text((W - 110, 1320), "NHÓM 14 · FEENBERG", font=font(22, 5), fill=SAGE, anchor="ra")

    if scene_id == "S070":
        # The previous arrow fell back to a boxed question mark.  Redraw this
        # one title with glyphs already proven by the other cards.
        clear_band(draw, 182, 278)
        draw.text((110, 205), S070_TITLE, font=font(48, 0), fill=(36, 40, 43))
        draw.text((W - 110, 210), S070_SOURCE_TAG, font=font(24, 5), fill=SAGE, anchor="ra")

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)
    return {
        "scene_id": scene_id,
        "source": str(source),
        "output": str(output),
        "width": W,
        "height": H,
        "sha256": sha256(output),
        "patches": [
            "remove_kicker_rail",
            "remove_crop_disclosure",
            *( ["replace_unsupported_arrow_glyph"] if scene_id == "S070" else [] ),
        ],
        "status": "R6_SOURCE_CARD_TYPOGRAPHY_PATCHED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    records = []
    for scene_id in SCENE_IDS:
        source = args.input_dir / f"{scene_id}_source_card.png"
        if not source.is_file():
            raise FileNotFoundError(source)
        output = args.output_dir / source.name
        record = patch_card(scene_id, source, output)
        records.append(record)
        print(f"{scene_id}: {output}")

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"manifest: {args.manifest}")


if __name__ == "__main__":
    main()
