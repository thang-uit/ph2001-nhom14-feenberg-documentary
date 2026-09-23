#!/usr/bin/env python3
"""Render argument-focused crops directly from verified academic PDFs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw


MAX_EDGE = 4096
TARGET_DPI = 360

CROPS = [
    {
        "filename": "S016_S01_p05_matrix_crop.png",
        "scene_ids": ["S016"],
        "source_id": "S01",
        "page": 5,
        "rect": [55, 555, 557, 735],
        "focus_terms": ["Technology is:", "Instrumentalism", "Critical Theory"],
    },
    {
        "filename": "S025_S01_p09_critical_theory_crop.png",
        "scene_ids": ["S025"],
        "source_id": "S01",
        "page": 9,
        "rect": [55, 55, 557, 390],
        "focus_terms": ["critical theory shares traits", "controllable", "value-laden"],
    },
    {
        "filename": "S036_S03_p05_underdetermination_crop.png",
        "scene_ids": ["S036"],
        "source_id": "S03",
        "page": 5,
        "rect": [45, 255, 470, 395],
        "focus_terms": ["surplus of workable solutions", "problem-definition often changes"],
    },
    {
        "filename": "S042_S03_p13_technical_code_definition_crop.png",
        "scene_ids": ["S042"],
        "source_id": "S03",
        "page": 13,
        "rect": [45, 585, 475, 725],
        "focus_terms": ["technical code", "technical parameters", "socially specified"],
    },
    {
        "filename": "S048_S02_p24_condensed_relations_crop.png",
        "scene_ids": ["S048"],
        "source_id": "S02",
        "page": 24,
        "rect": [40, 345, 580, 545],
        "focus_terms": ["technical and social relations are condensed in the device"],
    },
    {
        "filename": "S056_S03_p18_participation_crop.png",
        "scene_ids": ["S056"],
        "source_id": "S03",
        "page": 18,
        "rect": [45, 400, 495, 560],
        "focus_terms": ["What does it mean to democratize technology?", "not primarily one of legal rights", "initiative and participation"],
    },
    {
        "filename": "S064_S02_p10_network_origin_crop.png",
        "scene_ids": ["S064", "S070"],
        "source_id": "S02",
        "page": 10,
        "rect": [40, 425, 580, 725],
        "focus_terms": ["Teletel", "Internet", "data distribution"],
    },
    {
        "filename": "S070_S02_p11_design_change_crop.png",
        "scene_ids": ["S070"],
        "source_id": "S02",
        "page": 11,
        "rect": [40, 50, 580, 175],
        "focus_terms": ["new interpretation", "incorporated into its structure", "design changes"],
    },
    {
        "filename": "S070_S02_p11_ALS_participants_crop.png",
        "scene_ids": ["S070", "S071", "S072"],
        "source_id": "S02",
        "page": 11,
        "rect": [40, 415, 580, 580],
        "focus_terms": ["ALS", "Prodigy Medical Support Bulletin Board", "about 500 patients", "some dozens"],
    },
    {
        "filename": "S076_S02_p12_priority_list_crop.png",
        "scene_ids": ["S076", "S077"],
        "source_id": "S02",
        "page": 12,
        "rect": [40, 45, 580, 145],
        "focus_terms": ["established a list of priorities", "Amyotrophic Lateral Sclerosis Society of America"],
    },
    {
        "filename": "S099_S04_p225_democratic_rationalization_crop.png",
        "scene_ids": ["S099"],
        "source_id": "S04",
        "page": 225,
        "rect": [30, 75, 365, 145],
        "focus_terms": ["Feenberg, A. (1992)", "Democratic rationalization"],
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scale_for(rect: fitz.Rect) -> float:
    requested = TARGET_DPI / 72.0
    projected_max = max(rect.width, rect.height) * requested
    if projected_max <= MAX_EDGE:
        return requested
    return MAX_EDGE / max(rect.width, rect.height)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.resolve().read_text(encoding="utf-8"))
    sources = {entry["source_id"]: entry for entry in manifest["academic_sources"]}
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    for specification in CROPS:
        source = sources[specification["source_id"]]
        pdf_path = Path(source["local_path"])
        actual_hash = sha256(pdf_path)
        if actual_hash != source["sha256"]:
            raise SystemExit(f"SHA-256 mismatch for {specification['source_id']}")

        with fitz.open(pdf_path) as document:
            page = document.load_page(specification["page"] - 1)
            clip = fitz.Rect(specification["rect"])
            if not page.rect.contains(clip):
                raise SystemExit(f"Crop falls outside page: {specification['filename']}")
            scale = scale_for(clip)
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                clip=clip,
                alpha=False,
                colorspace=fitz.csRGB,
            )

            focus_hits: list[dict] = []
            for term in specification["focus_terms"]:
                hits = page.search_for(term)
                clipped_hits = [hit & clip for hit in hits if (hit & clip).get_area() > 0]
                focus_hits.append(
                    {
                        "term": term,
                        "found": bool(clipped_hits),
                        "page_rects": [list(hit) for hit in clipped_hits],
                        "crop_normalized_rects": [
                            [
                                (hit.x0 - clip.x0) / clip.width,
                                (hit.y0 - clip.y0) / clip.height,
                                (hit.x1 - clip.x0) / clip.width,
                                (hit.y1 - clip.y0) / clip.height,
                            ]
                            for hit in clipped_hits
                        ],
                    }
                )

        output_path = output_dir / specification["filename"]
        temporary = output_path.with_suffix(".render.tmp.png")
        pixmap.save(temporary)
        # Mark only the source words that the scene discusses.  The highlight
        # is a deterministic editorial annotation; the PDF pixels themselves
        # remain unchanged and the manifest records every matched rectangle.
        highlighted = Image.open(temporary).convert("RGBA")
        highlight_layer = Image.new("RGBA", highlighted.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(highlight_layer, "RGBA")
        for hit in focus_hits:
            for rect in hit["crop_normalized_rects"]:
                x0, y0, x1, y1 = (
                    round(rect[0] * highlighted.width),
                    round(rect[1] * highlighted.height),
                    round(rect[2] * highlighted.width),
                    round(rect[3] * highlighted.height),
                )
                pad_x = max(4, round(highlighted.width * 0.006))
                pad_y = max(3, round(highlighted.height * 0.012))
                draw.rounded_rectangle(
                    (x0 - pad_x, y0 - pad_y, x1 + pad_x, y1 + pad_y),
                    radius=max(4, round(highlighted.width * 0.002)),
                    fill=(230, 162, 60, 42),
                    outline=(178, 111, 18, 235),
                    width=max(2, round(highlighted.width * 0.0018)),
                )
        highlighted = Image.alpha_composite(highlighted, highlight_layer)
        highlighted.convert("RGB").save(temporary, format="PNG", optimize=True)
        os.replace(temporary, output_path)
        result = {
            **specification,
            "source_pdf": str(pdf_path),
            "source_pdf_sha256": actual_hash,
            "width": pixmap.width,
            "height": pixmap.height,
            "effective_dpi": round(scale * 72),
            "output_sha256": sha256(output_path),
            "focus_hits": focus_hits,
            "content_modified": False,
            "status": "RENDERED_FROM_VERIFIED_SOURCE",
        }
        results.append(result)
        missing = [hit["term"] for hit in focus_hits if not hit["found"]]
        suffix = "" if not missing else " | manual highlight check: " + "; ".join(missing)
        print(f"{output_path.name}: {pixmap.width}x{pixmap.height}{suffix}")

    index = {
        "schema_version": "1.0",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "method": "Direct PyMuPDF clipping from hash-verified source PDFs; no generative AI and no content alteration",
        "target_dpi": TARGET_DPI,
        "asset_count": len(results),
        "assets": results,
    }
    index_path = output_dir / "source_crops_index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Index: {index_path}")


if __name__ == "__main__":
    main()
