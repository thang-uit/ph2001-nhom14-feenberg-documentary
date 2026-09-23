#!/usr/bin/env python3
"""Export actual shot/audio cues and distinguish them from prompt intentions."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from build_sfx_ambience import aligned_events
from final_visual_plan import RECONSTRUCTION_SCENES, SCENE_ASSETS
from qa_final_video import normalized, parse_srt, seconds, sha256
from render_final_visuals import build_shots, probe_media, video_filter


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-storyboard", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    board = root / "02_storyboard.csv"
    audit_dir = root / "qa/final_v8"
    with board.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    # One legacy storyboard cell used “chuyển dụng”; the locked Vale
    # transcript says “vận dụng”.  Normalize this harmless metadata typo before
    # the exact-transcript gate and when --sync-storyboard writes the CSV.
    for row in rows:
        row["NARRATION"] = row["NARRATION"].replace(
            "chuyển dụng phương pháp luận", "vận dụng phương pháp luận"
        )
        if row["SCENE_ID"] in RECONSTRUCTION_SCENES:
            row["ON_SCREEN_TEXT"] = row["ON_SCREEN_TEXT"].replace(
                "TÁI DỰNG MINH HỌA", "MINH HỌA BẰNG AI"
            )
    shots = build_shots(
        rows,
        root,
        root / "assets/final_overlays_v8",
        root / "assets/final_stills_v8",
        root / "video/final_work_v8/segments",
    )
    events = sorted(
        ({"type": kind, "start_seconds": round(start, 3)} for kind, times in aligned_events(board).items() for start in times),
        key=lambda item: item["start_seconds"],
    )
    details: list[dict[str, object]] = []
    cursor_frames = 0
    for shot in shots:
        metadata = probe_media(shot.source_asset)
        details.append({
            "shot_id": f"{shot.scene_id}_{shot.shot_index:02d}",
            "scene_id": shot.scene_id,
            "start_frame": cursor_frames,
            "end_frame": cursor_frames + shot.frames,
            "start_seconds": cursor_frames / 30,
            "duration_seconds": shot.duration,
            "asset": shot.relative_asset,
            "resolved_asset": str(shot.source_asset.relative_to(root)),
            "source_technical": metadata,
            "actual_video_filter": video_filter(shot, metadata) if shot.source_asset.suffix.lower() == ".mp4" else None,
            "overlays": [str(path.relative_to(root)) for path in (shot.generic_overlay, shot.extra_overlay, shot.provenance_overlay) if path],
        })
        cursor_frames += shot.frames
    spoken = normalized((root / "audio/vo/narration_spoken.txt").read_text(encoding="utf-8"))
    reconstructed = normalized(" ".join(row["NARRATION"] for row in rows[:95]))
    if spoken != reconstructed:
        raise ValueError("Storyboard narration does not reconstruct the locked transcript")
    expected_frames = round(seconds(rows[-1]["END_TIME"]) * 30)
    expected_shots = sum(len(assets) for assets in SCENE_ASSETS.values())
    if len(rows) != 100 or len(shots) != expected_shots or cursor_frames != expected_frames:
        raise ValueError(
            "Unexpected final timeline structure: "
            f"scenes={len(rows)}, shots={len(shots)}/{expected_shots}, "
            f"frames={cursor_frames}/{expected_frames}"
        )
    if args.sync_storyboard:
        extra_fields = ["AS_BUILT_SHOTS", "AS_BUILT_SOUND", "CAMERA_METADATA_STATUS"]
        fields.extend(field for field in extra_fields if field not in fields)
        for row in rows:
            scene_shots = [item for item in details if item["scene_id"] == row["SCENE_ID"]]
            row["ASSET_STATUS"] = "RENDERED_SELECTED; " + "; ".join(item["asset"] for item in scene_shots)
            row["AS_BUILT_SHOTS"] = " | ".join(
                f"{item['shot_id']} @ {item['start_seconds']:.3f}s, {item['duration_seconds']:.3f}s: {item['asset']}" for item in scene_shots
            )
            start, end = seconds(row["START_TIME"]), seconds(row["END_TIME"])
            cues = [f"{item['type']} @ {item['start_seconds']:.3f}s" for item in events if start <= item["start_seconds"] < end]
            voice = "VO ChatGPT + nhạc duck theo waveform" if row["SCENE_ID"] <= "S095" else "Không lời; nhạc credit"
            row["AS_BUILT_SOUND"] = voice + "; ambience tổng hợp; " + (", ".join(cues) if cues else "không cue SFX rời")
            row["CAMERA_METADATA_STATUS"] = "CAMERA/LENS/LIGHTING/MOVEMENT/COMPOSITION là ý đồ storyboard hoặc prompt, không phải thông số máy quay đo từ cảnh AI. Shot/cue thực dùng ở AS_BUILT và JSON audit."
        with board.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    sources = json.loads((root / "06_source_manifest.json").read_text(encoding="utf-8"))
    source_checks = []
    for source in sources["academic_sources"]:
        actual_hash = sha256(Path(source["local_path"]))
        if actual_hash != source["sha256"]:
            raise ValueError(f"Source changed: {source['source_id']}")
        source_checks.append({"source_id": source["source_id"], "sha256": actual_hash, "status": "HASH_MATCH"})
    inventory = json.loads((root / "assets/final_motion_asset_inventory.json").read_text(encoding="utf-8"))
    for asset in inventory["assets"]:
        if sha256(root / asset["relative_path"]) != asset["sha256"]:
            raise ValueError(f"Selected motion asset changed: {asset['relative_path']}")
    cues = parse_srt(root / "05_subtitles.srt")
    subtitle_text = normalized(" ".join(" ".join(cue["lines"]) for cue in cues))
    if subtitle_text != spoken:
        raise ValueError("Subtitle wording differs from locked transcript")
    used_audio = {
        "voice": "audio/vo/vale_unified_v7/VO_VALE_UNIFIED_V7_48K.wav",
        "music_source": "Feenberg-NhacNen.mp3",
        "music_master": "audio/music/SCORE_SUNO_V8_48K.wav",
        "sfx": "audio/sfx/SFX_AMBIENCE_V7_48K.wav",
        "mix": "audio/mix/FULL_MIX_DELIVERY_V8_SUNO_48K.wav",
    }
    summary = {
        "duration_seconds": cursor_frames / 30, "scenes": len(rows), "shots": len(shots),
        "narration_words_whitespace": len(spoken.split()), "storyboard_exact_transcript": True,
        "subtitle_cues": len(cues), "subtitle_exact_transcript": True,
        "subtitle_max_characters_per_second": max(len(" ".join(cue["lines"])) / (cue["end"] - cue["start"]) for cue in cues),
        "subtitle_min_duration_seconds": min(cue["end"] - cue["start"] for cue in cues),
        "selected_assets_by_provider": dict(Counter(asset["provider"] for asset in inventory["assets"])),
        "selected_motion_hashes": f"{len(inventory['assets'])}/{len(inventory['assets'])} MATCH",
        "audio": {kind: {"file": filename, "sha256": sha256(root / filename)} for kind, filename in used_audio.items()},
        "sfx_cue_count": len(events), "academic_source_hash_checks": source_checks,
        "qa_scope_limit": "Hash/text/structural checks do not certify complete audible pronunciation, every generated video frame, or a guaranteed grade.",
    }
    write_json(audit_dir / "as_built_shot_manifest.json", details)
    write_json(audit_dir / "audio_cue_manifest.json", events)
    write_json(audit_dir / "as_built_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
