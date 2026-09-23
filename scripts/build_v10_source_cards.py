#!/opt/homebrew/bin/python3.13
"""Frame verified instructor-document crops as readable documentary cards."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


W, H = 2560, 1440
FONT = "/System/Library/Fonts/Avenir Next.ttc"
IVORY = (244, 239, 229)
PAPER = (255, 252, 246)
CHARCOAL = (36, 40, 43)
COBALT = (27, 74, 137)
VERMILION = (211, 73, 54)
SAGE = (112, 132, 117)

CARDS = {
    "S016": ("S016_S01_p05_matrix_crop.png", "THUYẾT CÔNG CỤ · TRUNG TÍNH + CON NGƯỜI KIỂM SOÁT", "S01 · PDF tr. 5–6"),
    "S025": ("S025_S01_p09_critical_theory_crop.png", "LÝ THUYẾT PHÊ PHÁN CÔNG NGHỆ", "S01 · PDF tr. 9"),
    "S036": ("S036_S03_p05_underdetermination_crop.png", "BẤT ĐỊNH TƯƠNG ĐỐI · KHÔNG PHẢI TÙY Ý", "S03 · PDF tr. 5"),
    "S042": ("S042_S03_p13_technical_code_definition_crop.png", "MÃ KỸ THUẬT · TECHNICAL CODE", "S03 · PDF tr. 13"),
    "S048": ("S048_S02_p24_condensed_relations_crop.png", "QUAN HỆ XÃ HỘI + KỸ THUẬT ‘CÔ ĐỌNG’", "S02 · PDF tr. 24"),
    "S056": ("S056_S03_p18_participation_crop.png", "SÁNG KIẾN + SỰ THAM GIA", "S03 · PDF tr. 18"),
    "S064": ("S064_S02_p10_network_origin_crop.png", "CASE NGUỒN · QUỸ ĐẠO CỦA MẠNG", "S02 · PDF tr. 10"),
    "S070": ("S070_S02_p11_design_change_crop.png", "NGƯỜI DÙNG CHIẾM DỤNG → THAY ĐỔI THIẾT KẾ", "S02 · PDF tr. 11"),
    "S076": ("S076_S02_p12_priority_list_crop.png", "ĐÃ TRÌNH DANH SÁCH · GIỚI HẠN BẰNG CHỨNG", "S02 · PDF tr. 12"),
}


def font(size: int, index: int = 7) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size=size, index=index)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for part in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        trial = f"{line} {word}"
        if draw.textbbox((0, 0), trial, font=face)[2] <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def build(scene_id: str, source: Path, output: Path, title: str, source_tag: str) -> None:
    im = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(im)
    for y in range(H):
        p = y / H
        c = tuple(round(a + (b - a) * p * .22) for a, b in zip(IVORY, (229, 223, 211)))
        d.line((0, y, W, y), fill=c)
    d.rectangle((0, 0, W, 18), fill=COBALT)
    d.line((110, 128, W - 110, 128), fill=COBALT, width=3)
    d.rectangle((110, 100, 132, 154), fill=VERMILION)
    d.text((170, 104), "ĐỐI CHIẾU VĂN BẢN GỐC", font=font(28, 2), fill=COBALT)
    d.text((110, 205), title, font=font(48, 0), fill=CHARCOAL)
    d.text((W - 110, 210), source_tag, font=font(24, 5), fill=SAGE, anchor="ra")

    src = Image.open(source).convert("RGB")
    max_w, max_h = 2220, 900
    scale = min(max_w / src.width, max_h / src.height, 1.0)
    fitted = src.resize((round(src.width * scale), round(src.height * scale)), Image.Resampling.LANCZOS)
    x = (W - fitted.width) // 2
    y = 300 + (900 - fitted.height) // 2
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x - 28, y - 28, x + fitted.width + 28, y + fitted.height + 28), radius=22, fill=(0, 0, 0, 38))
    im = Image.alpha_composite(im.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x - 12, y - 12, x + fitted.width + 12, y + fitted.height + 12), radius=15, fill=(*PAPER, 255), outline=(*COBALT, 190), width=3)
    im.alpha_composite(fitted.convert("RGBA"), (x, y))
    d = ImageDraw.Draw(im)
    d.line((110, 1270, 930, 1270), fill=VERMILION, width=7)
    d.line((930, 1270, 1720, 1270), fill=COBALT, width=4)
    d.line((1720, 1270, W - 110, 1270), fill=VERMILION, width=2)
    d.text((110, 1320), "CROP ĐÃ HIGHLIGHT · NỘI DUNG GỐC GIỮ NGUYÊN", font=font(22, 5), fill=SAGE)
    d.text((W - 110, 1320), "NHÓM 14 · FEENBERG", font=font(22, 5), fill=SAGE, anchor="ra")
    output.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(output, format="PNG", optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crop-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    records = []
    for sid, (filename, title, tag) in CARDS.items():
        source = args.crop_dir / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        out = args.output_dir / f"{sid}_source_card.png"
        build(sid, source, out, title, tag)
        records.append({"scene_id": sid, "source_crop": str(source), "output": str(out), "width": W, "height": H, "sha256": sha(out), "status": "RENDERED_FROM_HIGHLIGHTED_SOURCE_CROP"})
        print(f"{sid}: {out.name}")
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest: {args.manifest}")


if __name__ == "__main__":
    main()
