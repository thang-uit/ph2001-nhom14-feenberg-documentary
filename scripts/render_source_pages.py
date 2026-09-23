#!/usr/bin/env python3
"""Render verified academic PDF pages into high-resolution source stills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

import pymupdf as fitz


TARGET_DPI = 300
MAX_EDGE = 4096


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_map(manifest: dict) -> dict[str, dict]:
    return {entry["source_id"]: entry for entry in manifest["academic_sources"]}


def render_page(pdf_path: Path, page_number: int, output_path: Path) -> tuple[int, int, int]:
    with fitz.open(pdf_path) as document:
        if page_number < 1 or page_number > document.page_count:
            raise ValueError(
                f"Page {page_number} is outside 1–{document.page_count} for {pdf_path.name}"
            )
        page = document.load_page(page_number - 1)
        base_scale = TARGET_DPI / 72.0
        projected_width = page.rect.width * base_scale
        projected_height = page.rect.height * base_scale
        scale = min(base_scale, MAX_EDGE / max(projected_width, projected_height) * base_scale)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False, colorspace=fitz.csRGB)
        temporary = output_path.with_suffix(".render.tmp.png")
        pixmap.save(temporary)
        os.replace(temporary, output_path)
        effective_dpi = round(72 * scale)
        return pixmap.width, pixmap.height, effective_dpi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    output_dir = args.output_dir.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = source_map(manifest)
    planned = manifest["source_page_assets"]["planned_assets"]
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for asset in planned:
        source_id = asset["source_id"]
        if source_id not in sources:
            raise SystemExit(f"Unknown source ID for page asset: {source_id}")
        pdf_path = Path(sources[source_id]["local_path"])
        if not pdf_path.is_file():
            raise SystemExit(f"Source PDF not found: {pdf_path}")
        actual_source_hash = sha256(pdf_path)
        expected_source_hash = sources[source_id]["sha256"]
        if actual_source_hash != expected_source_hash:
            raise SystemExit(
                f"SHA-256 mismatch for {source_id}: expected {expected_source_hash}, "
                f"got {actual_source_hash}"
            )

        output_path = output_dir / asset["filename"]
        width, height, dpi = render_page(pdf_path, int(asset["pdf_page"]), output_path)
        result = {
            "filename": asset["filename"],
            "source_id": source_id,
            "source_pdf": str(pdf_path),
            "source_pdf_sha256": actual_source_hash,
            "pdf_page_1_based": int(asset["pdf_page"]),
            "width": width,
            "height": height,
            "effective_dpi": dpi,
            "output_sha256": sha256(output_path),
            "content_modified": False,
            "status": "RENDERED_FROM_VERIFIED_SOURCE"
        }
        results.append(result)
        print(
            f"{result['filename']}: {width}x{height}, {dpi} dpi, "
            f"source {source_id} p.{asset['pdf_page']}"
        )

    index = {
        "schema_version": "1.0",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "method": "PyMuPDF rasterization from hash-verified PDFs; no generative AI; no content alteration",
        "target_dpi": TARGET_DPI,
        "max_edge": MAX_EDGE,
        "asset_count": len(results),
        "assets": results,
    }
    index_path = output_dir / "source_pages_index.json"
    index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Index: {index_path}")


if __name__ == "__main__":
    main()
