#!/usr/bin/env python3
"""Hash and probe every motion asset actually referenced by the final edit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path

from final_visual_plan import SCENE_ASSETS, is_generated_video


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def probe(path: Path) -> dict[str, object]:
    value = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,field_order:format=duration,size",
            "-of", "json", str(path),
        ],
        text=True,
    )
    parsed = json.loads(value)
    stream = parsed["streams"][0]
    container = parsed["format"]
    return {
        "codec": stream.get("codec_name"),
        "profile": stream.get("profile"),
        "width": stream.get("width"),
        "height": stream.get("height"),
        "fps": stream.get("r_frame_rate"),
        "pix_fmt": stream.get("pix_fmt"),
        "field_order": stream.get("field_order"),
        "duration_seconds": float(container.get("duration", 0)),
        "size_bytes": int(container.get("size", 0)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()
    usage: dict[str, list[str]] = defaultdict(list)
    for scene_id, assets in SCENE_ASSETS.items():
        for relative in assets:
            if relative.lower().endswith(".mp4"):
                usage[relative].append(scene_id)

    assets: list[dict[str, object]] = []
    for relative, scenes in sorted(usage.items()):
        path = project_dir / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        technical = probe(path)
        assets.append(
            {
                "relative_path": relative,
                "scene_ids": scenes,
                "provider": "Google Flow / Veo" if is_generated_video(relative) else "project asset",
                "sha256": sha256(path),
                "technical": technical,
                "qa_verdict": "SELECTED_AND_USED",
                "conform_note": "Source normalized to 1920x1080/30 fps/Rec.709 in final edit; 720p sources retained at native size inside a 1080p canvas.",
            }
        )

    rejected = [
        {
            "relative_path": "assets/flow_selected/S038_flow_720p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Visual metaphor drift and sparks could imply accident or spectacle.",
        },
        {
            "relative_path": "assets/flow_selected/S093_flow_1080p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "CGI/armour-like people and heated machinery were not suitable for the academic conclusion.",
        },
        {
            "relative_path": "assets/flow_selected/S039_flow_1080p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Model-generated pseudo-lettering remained visible on the machine layers and failed the no-gibberish-text visual gate.",
        },
        {
            "relative_path": "assets/flow_selected/S065_network_operations_reconstruction_720p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Fake CRT lettering and luminous cable artifacts made the reconstruction historically unreliable.",
        },
        {
            "relative_path": "assets/flow_selected/S065_network_new_candidate_720p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Fake CRT lettering, magical light paths and an implausible period computer room failed the evidence and realism gates.",
        },
        {
            "relative_path": "assets/flow_v8_odoo/S002_phone_booking_1080p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Generated phone lettering was not reliable enough to represent a real interface.",
        },
        {
            "relative_path": "assets/flow_v8_odoo/S006_clinic_waiting_1080p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Visible pseudo-signage failed the no-gibberish-text gate.",
        },
        {
            "relative_path": "assets/flow_v8_odoo/S038_constraints_review_1080p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Generated marks on the technical material could be mistaken for meaningful evidence.",
        },
        {
            "relative_path": "assets/flow_v8_odoo/S063_governance_feedback_1080p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Interface text and interaction continuity were not sufficiently reliable.",
        },
        {
            "relative_path": "assets/flow_v8_namthanguit/S063_governance_feedback_alt_1080p.mp4",
            "qa_verdict": "REJECTED_NOT_USED",
            "reason": "Interface text and interaction continuity were not sufficiently reliable.",
        },
    ]
    # Flow project links are private production metadata.  Keep them out of
    # public manifests by requiring an explicit opt-in environment variable.
    # Format: FLOW_PROJECT_URLS='https://...\nhttps://...'
    private_project_urls = [
        value.strip()
        for value in os.environ.get("FLOW_PROJECT_URLS", "").splitlines()
        if value.strip()
    ]
    data = {
        "schema_version": "1.0",
        "production_system": "Google Flow / Veo; exact model version is recorded only where the generation interface exposed it",
        "project_urls": private_project_urls,
        "used_motion_asset_count": len(assets),
        "assets": assets,
        "rejected_assets": rejected,
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Final motion asset inventory: {output} ({len(assets)} used assets)")


if __name__ == "__main__":
    main()
