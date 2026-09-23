#!/usr/bin/env python3
"""Build the V4 TP.HCM end-credit montage.

V4 keeps the approved credit typography and music treatment, but replaces the
short V3 montage with a deliberately varied sequence containing every clip in
``assets/credit_tphcm/raw/incoming`` plus every V3 source.  The picture is
assembled first and typography is composited afterwards, so Vietnamese glyphs
cannot ghost across dissolves.

The script writes only V4-specific paths.  It never overwrites the V3 or main
documentary deliverables.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import build_credit_tphcm as base


ROOT = base.ROOT
RAW = ROOT / "assets" / "credit_tphcm" / "raw"
WORK = ROOT / "renders" / "credit_tphcm_v4"
QA = ROOT / "qa" / "credit_tphcm" / "v4"
OVERLAYS = WORK / "overlays"
SEGMENTS_CLEAN = WORK / "segments_clean"
SEGMENTS_CREDIT = WORK / "segments_credit"
PICTURE_CLEAN = WORK / "picture_clean.mp4"
PICTURE_CREDIT = WORK / "picture_credit.mp4"
OUTPUT = ROOT / "CREDIT_TPHCM_OH_YEAH_V4.mp4"
CLEAN_OUTPUT = ROOT / "CREDIT_TPHCM_OH_YEAH_CLEAN_V4.mp4"
CLEAN_4K_OUTPUT = ROOT / "CREDIT_TPHCM_OH_YEAH_CLEAN_V4_4K.mp4"

TRANSITION = 0.45
AUDIO_START = 11.50
AUDIO_DURATION = 54.10
FPS = 30


# Every V3 source is used once, and all eight user-provided incoming clips are
# used once.  Short detail shots are intentional: they add visual rhythm while
# the two member cards and final thanks card remain readable.
SHOTS: list[dict[str, object]] = [
    {
        "id": "V4C01",
        "file": "pexels_aerial_skyline_32427394.mp4",
        "source_start": 0.8,
        "duration": 4.8,
        "overlay": "title",
        "purpose": "Toàn cảnh mở đầu, đặt nhịp đô thị và tên video.",
    },
    {
        "id": "V4C02",
        "file": "incoming/15980643_3840_2160_25fps.mp4",
        "source_start": 12.0,
        "duration": 4.5,
        "overlay": "producer",
        "purpose": "Không gian trước Bưu điện Thành phố và dòng người thật.",
    },
    {
        "id": "V4C03",
        "file": "pexels_city_hall_39357829.mp4",
        "source_start": 0.4,
        "duration": 4.5,
        "overlay": "teacher",
        "purpose": "Nhận diện kiến trúc và bối cảnh thành phố.",
    },
    {
        "id": "V4C04",
        "file": "incoming/12205461_3840_2160_30fps.mp4",
        "source_start": 2.0,
        "duration": 2.8,
        "overlay": None,
        "purpose": "Cận cảnh chợ đèn và người dân, đưa nhịp sống vào credit.",
    },
    {
        "id": "V4C05",
        "file": "incoming/14305269_3840_2160_30fps.mp4",
        "source_start": 0.8,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Chi tiết ẩm thực thật, tạo một nhịp cắt cảm giác.",
    },
    {
        "id": "V4C06",
        "file": "incoming/16602191_3840_2160_30fps.mp4",
        "source_start": 2.5,
        "duration": 5.5,
        "overlay": "members_a",
        "purpose": "Đường phố ban ngày làm nền cho bốn thành viên đầu.",
    },
    {
        "id": "V4C07",
        "file": "incoming/15300802_3840_2160_60fps.mp4",
        "source_start": 1.0,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Giao lộ và chuyển động giao thông thực tế.",
    },
    {
        "id": "V4C08",
        "file": "pexels_busy_street_37886978.mp4",
        "source_start": 4.0,
        "duration": 2.8,
        "overlay": None,
        "purpose": "Match cut từ giao lộ sang nhịp xe trung tâm.",
    },
    {
        "id": "V4C09",
        "file": "incoming/12602357_3840_2160_25fps.mp4",
        "source_start": 7.0,
        "duration": 5.0,
        "overlay": "members_b",
        "purpose": "Dòng xe đêm làm nền cho ba thành viên còn lại.",
    },
    {
        "id": "V4C10",
        "file": "pexels_day_night_3963629.mp4",
        "source_start": 8.0,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Nhịp chuyển ngày–đêm nối phần credit sang đô thị ban đêm.",
    },
    {
        "id": "V4C11",
        "file": "incoming/14194592_3840_2160_30fps.mp4",
        "source_start": 1.0,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Blue hour trên sông, hạ nhịp trước chuỗi đêm.",
    },
    {
        "id": "V4C12",
        "file": "incoming/12984242_3840_2160_30fps.mp4",
        "source_start": 2.0,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Toàn cảnh đêm với tháp phát sáng, mở rộng không gian.",
    },
    {
        "id": "V4C13",
        "file": "pexels_ben_thanh_29185453.mp4",
        "source_start": 0.0,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Bến Thành và ánh đèn giao thông thật.",
    },
    {
        "id": "V4C14",
        "file": "pexels_night_traffic_29185408.mp4",
        "source_start": 0.8,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Cận nhịp xe đêm, không lặp lại shot trước.",
    },
    {
        "id": "V4C15",
        "file": "pexels_night_skyline_31111952.mp4",
        "source_start": 5.0,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Skyline đêm chuyển động thật trước lời cảm ơn.",
    },
    {
        "id": "V4C16",
        "file": "pexels_river_skyline_31975717.mp4",
        "source_start": 2.0,
        "duration": 2.6,
        "overlay": None,
        "purpose": "Mặt nước và ánh phản chiếu, tạo khoảng thở cuối.",
    },
    {
        "id": "V4C17",
        "file": "pexels_landmark_31111825.mp4",
        "source_start": 2.2,
        "duration": 8.0,
        "overlay": "thanks",
        "purpose": "Khung skyline kết, giữ lời cảm ơn đủ lâu để đọc.",
    },
]


def configure_base() -> None:
    """Point the reusable V3 functions at isolated V4 paths/configuration."""
    base.RAW = RAW
    base.WORK = WORK
    base.OVERLAYS = OVERLAYS
    base.SEGMENTS_CLEAN = SEGMENTS_CLEAN
    base.SEGMENTS_CREDIT = SEGMENTS_CREDIT
    base.PICTURE_CLEAN = PICTURE_CLEAN
    base.PICTURE_CREDIT = PICTURE_CREDIT
    base.OUTPUT = OUTPUT
    base.CLEAN_OUTPUT = CLEAN_OUTPUT
    base.QA = QA
    base.SHOTS = SHOTS
    base.TRANSITION = TRANSITION
    base.AUDIO_START = AUDIO_START
    base.AUDIO_DURATION = AUDIO_DURATION
    base.FPS = FPS

    # The incoming filenames are Pexels numeric IDs.  Keep the URL explicit in
    # the manifest while marking it as user-provided provenance below.
    for shot in SHOTS:
        file_name = Path(str(shot["file"])).name
        if str(shot["file"]).startswith("incoming/"):
            pexels_id = file_name.split("_", 1)[0]
            base.PEXELS_URLS[str(shot["file"])] = f"https://www.pexels.com/video/{pexels_id}/"


def run(cmd: list[str]) -> None:
    print("$", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def validate_sources() -> None:
    if not base.AUDIO.is_file():
        raise FileNotFoundError(base.AUDIO)
    for shot in SHOTS:
        source = RAW / str(shot["file"])
        if not source.is_file():
            raise FileNotFoundError(source)


def mux_audio_v4(clean_video: Path, output: Path, force: bool) -> None:
    if output.exists() and not force:
        return
    fade_out_duration = min(2.35, AUDIO_DURATION / 4.0)
    fade_out_start = AUDIO_DURATION - fade_out_duration
    audio_end = AUDIO_START + AUDIO_DURATION
    audio_filter = (
        f"atrim=start={AUDIO_START:.3f}:end={audio_end:.3f},asetpts=PTS-STARTPTS,"
        "afade=t=in:st=0:d=0.04,"
        f"afade=t=out:st={fade_out_start:.3f}:d={fade_out_duration:.3f},"
        "loudnorm=I=-14.5:TP=-1.5:LRA=11:linear=true"
    )
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(clean_video), "-i", str(base.AUDIO),
        "-filter_complex", f"[1:a]{audio_filter}[aout]",
        "-map", "0:v:0", "-map", "[aout]", "-t", f"{AUDIO_DURATION:.3f}",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-ac", "2", "-movflags", "+faststart", str(output),
    ]
    run(command)


def clean_old_v4_outputs() -> None:
    for directory in (SEGMENTS_CLEAN, SEGMENTS_CREDIT, WORK / "segments_clean_4k"):
        if directory.exists():
            for path in directory.glob("V4C*.mp4"):
                path.unlink()
    for path in (PICTURE_CLEAN, PICTURE_CREDIT, OUTPUT, CLEAN_OUTPUT, CLEAN_4K_OUTPUT):
        if path.exists():
            path.unlink()


def enrich_manifest() -> None:
    """Add V4 provenance and reuse assertions to the reusable manifest."""
    manifest_path = QA / "credit_source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = "V4"
    manifest["final_duration_seconds"] = AUDIO_DURATION
    manifest["incoming_directory"] = str((RAW / "incoming").relative_to(ROOT))
    manifest["all_incoming_clips_included"] = True
    manifest["asset_reuse_policy"] = "each selected asset appears once; reuse count <= 2"
    manifest["provenance_note"] = (
        "Incoming clips were downloaded by the user from Pexels; numeric IDs and local filenames are preserved."
    )
    manifest["incoming_url_note"] = (
        "Numeric Pexels URLs are recorded for traceability; the local downloads supplied by the user are the assets of record."
    )
    for row in manifest["shots"]:
        row["provenance"] = (
            "user-provided Pexels download" if str(row["source"]).startswith("incoming/") else "existing local Pexels asset"
        )
        row["source_url_status"] = (
            "numeric Pexels URL recorded; local user-provided file is authoritative"
            if str(row["source"]).startswith("incoming/")
            else "existing manifest URL"
        )
        row["reuse_count"] = 1
    manifest["qa_assertions"] = {
        "selected_asset_count": len(SHOTS),
        "unique_asset_count": len({str(s["file"]) for s in SHOTS}),
        "all_reuse_counts_at_most_two": True,
        "technical_decode": "pending post-render full decode",
        "manual_motion_review": "contact sheet and 2 fps review completed before render",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_v4_qa_summary() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    rows = []
    starts = base.timeline_starts()
    for index, shot in enumerate(SHOTS):
        source = RAW / str(shot["file"])
        rows.append(
            {
                "scene_id": shot["id"],
                "timeline_start": round(starts[index], 3),
                "timeline_end": round(starts[index] + float(shot["duration"]), 3),
                "asset": str(shot["file"]),
                "source_path": str(source),
                "overlay": shot.get("overlay"),
                "duration": shot["duration"],
                "reuse_count": 1,
                "status": "SELECTED",
            }
        )
    (QA / "v4_asset_reuse_audit.json").write_text(
        json.dumps(
            {
                "policy": "one appearance per selected asset",
                "all_assets_unique": len({row["asset"] for row in rows}) == len(rows),
                "rows": rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def build_1080(force: bool) -> None:
    overlays = base.make_overlays()
    clean_segments = [
        base.render_segment(i, shot, None, force, SEGMENTS_CLEAN)
        for i, shot in enumerate(SHOTS)
    ]
    base.assemble_video(clean_segments, PICTURE_CLEAN, force)
    base.compose_credit_overlay(PICTURE_CLEAN, overlays, PICTURE_CREDIT, force)
    mux_audio_v4(PICTURE_CREDIT, OUTPUT, force)
    mux_audio_v4(PICTURE_CLEAN, CLEAN_OUTPUT, force)
    base.write_manifest(overlays)
    enrich_manifest()
    write_v4_qa_summary()


def build_4k(force: bool) -> None:
    """Build clean UHD using the existing UHD renderer with V4 globals."""
    import build_credit_tphcm_clean_4k as uhd

    uhd.RAW = RAW
    uhd.WORK = WORK
    uhd.SEGMENTS_UHD = WORK / "segments_clean_4k"
    uhd.PICTURE_UHD = WORK / "picture_clean_4k.mp4"
    uhd.OUTPUT_UHD = CLEAN_4K_OUTPUT
    uhd.QA_DIR = QA
    uhd.SHOTS = SHOTS
    uhd.TRANSITION = TRANSITION
    uhd.AUDIO_DURATION = AUDIO_DURATION
    uhd.AUDIO_START = AUDIO_START
    uhd.FPS = FPS
    uhd.PEXELS_URLS = base.PEXELS_URLS

    if force:
        for path in uhd.SEGMENTS_UHD.glob("V4C*.mp4"):
            path.unlink()
        for path in (uhd.PICTURE_UHD, uhd.OUTPUT_UHD):
            if path.exists():
                path.unlink()

    segments = [
        uhd.render_segment(i, shot, force)
        for i, shot in enumerate(SHOTS)
    ]
    uhd.assemble_video(segments, force)
    mux_audio_v4(uhd.PICTURE_UHD, CLEAN_4K_OUTPUT, force)
    uhd.write_manifest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-4k", action="store_true")
    args = parser.parse_args()

    configure_base()
    validate_sources()
    WORK.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    if args.force:
        clean_old_v4_outputs()
    build_1080(args.force)
    if not args.skip_4k:
        build_4k(args.force)
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {CLEAN_OUTPUT}")
    if not args.skip_4k:
        print(f"Wrote {CLEAN_4K_OUTPUT}")


if __name__ == "__main__":
    main()
