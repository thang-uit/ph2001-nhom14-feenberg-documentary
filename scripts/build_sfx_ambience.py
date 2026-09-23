#!/usr/bin/env python3
"""Create an original ambience/foley stem without third-party recordings."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


SAMPLE_RATE = 48_000
DURATION = 933.366667


EVENTS = {
    "click": [
        7.1, 13.2, 20.1, 49.0, 57.0, 66.0, 75.0, 83.0, 106.0,
        137.0, 145.0, 152.0, 159.0, 166.0, 173.0, 180.0,
        208.0, 216.0, 224.0, 232.0, 240.0, 248.0, 256.0, 264.0,
        296.0, 304.0, 312.0, 320.0, 368.0, 376.0, 384.0, 392.0,
        407.0, 416.0, 425.0, 434.0, 443.0, 452.0, 461.0, 470.0, 480.0,
        489.0, 499.0, 509.0, 519.0, 530.0, 541.0, 552.0, 563.0, 574.0,
        584.0, 595.0, 606.0, 617.0, 628.0, 639.0, 650.0, 661.0, 672.0,
        683.0, 694.0, 705.0, 716.0, 727.0, 738.0, 748.0, 758.0, 768.0,
        778.0, 788.0, 801.0, 813.0, 825.0, 838.0, 848.0, 858.0,
    ],
    "paper": [122.0, 187.0, 272.0, 320.0, 368.0, 425.0, 509.0, 574.0, 639.0, 895.0, 905.0],
    "servo": [13.0, 20.0, 49.0, 93.0, 138.0, 208.0, 232.0, 248.0, 296.0, 312.0, 344.0, 368.0, 407.0, 470.0, 499.0, 552.0, 683.0, 738.0, 788.0, 825.0, 848.0],
    "impact": [29.0, 115.0, 208.0, 296.0, 407.0, 509.0, 683.0, 801.0, 858.0],
    "steam": [328.0, 344.0, 360.0, 376.0],
    "modem": [519.0, 541.0, 574.0, 595.0, 617.0],
    "footstep": [1.4, 3.5, 5.6, 863.0, 866.0, 869.0],
    "whoosh": [29.0, 115.0, 208.0, 296.0, 407.0, 509.0, 683.0, 801.0, 858.0],
}


def aligned_events(storyboard: Path) -> dict[str, list[float]]:
    """Place only sparse, physically motivated cues on the speech-locked picture.

    The previous mix put a cue on most graphics and used paper turns for source
    cards/credits.  That made the film sound like a slideshow.  This pass keeps
    foley only where an on-screen physical action plausibly produces it.  In
    particular, the complete ending is free of page-turn and UI sounds.
    """
    with storyboard.open(encoding="utf-8-sig", newline="") as handle:
        rows = {row["SCENE_ID"]: row for row in csv.DictReader(handle)}

    def starts(numbers: list[int], offset: float = 0.10) -> list[float]:
        result = []
        for number in numbers:
            h, m, s = rows[f"S{number:03d}"]["START_TIME"].split(":")
            result.append(int(h) * 3600 + int(m) * 60 + float(s) + offset)
        return result

    return {
        "click": starts([2, 8]),
        "servo": starts([3, 4, 27, 41, 46]),
        "impact": starts([39, 64, 91]),
        "steam": starts([43, 44, 47]),
        "modem": starts([71, 73]),
        "footstep": starts([1], 0.55),
        "whoosh": starts([39, 64, 91]),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_inputs() -> tuple[list[str], dict[str, int]]:
    inputs = [
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude=0.016:duration={DURATION}:sample_rate={SAMPLE_RATE}",
        "-f", "lavfi", "-i", f"aevalsrc=exprs='0.006*sin(2*PI*49*t)|0.0057*sin(2*PI*49.03*t+0.2)':s={SAMPLE_RATE}:d={DURATION}:c=stereo",
    ]
    indexes: dict[str, int] = {}
    definitions = {
        "click": "aevalsrc=exprs='0.20*sin(2*PI*1320*t)*exp(-38*t)|0.17*sin(2*PI*1390*t+0.2)*exp(-40*t)':s=48000:d=0.22:c=stereo",
        "paper": "anoisesrc=color=white:amplitude=0.12:duration=0.55:sample_rate=48000",
        "servo": "aevalsrc=exprs='0.05*sin(2*PI*(150+210*t)*t)*(1-exp(-12*t))*exp(-2.8*t)|0.047*sin(2*PI*(157+205*t)*t+0.3)*(1-exp(-12*t))*exp(-2.7*t)':s=48000:d=1.15:c=stereo",
        "impact": "aevalsrc=exprs='0.16*sin(2*PI*72*t)*exp(-5.2*t)+0.04*sin(2*PI*181*t)*exp(-9*t)|0.15*sin(2*PI*70*t+0.12)*exp(-5*t)+0.035*sin(2*PI*188*t)*exp(-9*t)':s=48000:d=0.85:c=stereo",
        "steam": "anoisesrc=color=pink:amplitude=0.07:duration=3.2:sample_rate=48000",
        "modem": "aevalsrc=exprs='0.018*sin(2*PI*(510+160*sin(2*PI*2.3*t))*t)+0.012*sin(2*PI*980*t)|0.017*sin(2*PI*(516+155*sin(2*PI*2.1*t))*t+0.2)+0.011*sin(2*PI*971*t)':s=48000:d=3.6:c=stereo",
        "footstep": "aevalsrc=exprs='0.11*sin(2*PI*58*t)*exp(-8*t)+0.025*sin(2*PI*136*t)*exp(-14*t)|0.10*sin(2*PI*56*t+0.1)*exp(-8*t)+0.022*sin(2*PI*141*t)*exp(-14*t)':s=48000:d=0.42:c=stereo",
        "whoosh": "anoisesrc=color=pink:amplitude=0.08:duration=1.35:sample_rate=48000",
    }
    next_index = 2
    for name, definition in definitions.items():
        indexes[name] = next_index
        inputs.extend(["-f", "lavfi", "-i", definition])
        next_index += 1
    return inputs, indexes


def build_graph(indexes: dict[str, int]) -> str:
    graph = [
        "[0:a]highpass=f=85,lowpass=f=1250,volume='0.34+0.10*sin(2*PI*0.013*t)':eval=frame,pan=stereo|c0=c0|c1=c0[room]",
        "[1:a]highpass=f=35,lowpass=f=180,volume='if(between(t,328,407),1.18,if(between(t,509,683),0.72,0.42))':eval=frame[hum]",
    ]
    event_labels: list[str] = []
    filters = {
        "click": "highpass=f=500,lowpass=f=4200,volume=0.42",
        "paper": "highpass=f=650,lowpass=f=6200,afade=t=in:st=0:d=0.05,afade=t=out:st=0.30:d=0.25,volume=0.24,pan=stereo|c0=c0|c1=c0",
        "servo": "highpass=f=85,lowpass=f=1800,volume=0.33",
        "impact": "lowpass=f=520,volume=0.33",
        "steam": "highpass=f=250,lowpass=f=4600,afade=t=in:st=0:d=0.35,afade=t=out:st=2.1:d=1.1,volume=0.19,pan=stereo|c0=c0|c1=c0",
        "modem": "highpass=f=280,lowpass=f=2200,afade=t=in:st=0:d=0.4,afade=t=out:st=2.6:d=1.0,volume=0.11",
        "footstep": "lowpass=f=480,volume=0.23",
        "whoosh": "highpass=f=180,lowpass=f=4300,afade=t=in:st=0:d=0.42,afade=t=out:st=0.70:d=0.65,volume=0.12,pan=stereo|c0=c0|c1=c0",
    }
    for name, times in EVENTS.items():
        source_index = indexes[name]
        split_labels = [f"{name}src{i}" for i in range(len(times))]
        graph.append(f"[{source_index}:a]asplit={len(times)}{''.join(f'[{label}]' for label in split_labels)}")
        for i, (label, start) in enumerate(zip(split_labels, times)):
            delay = round(start * 1000)
            out = f"{name}{i}"
            graph.append(f"[{label}]{filters[name]},adelay={delay}|{delay}[{out}]")
            event_labels.append(f"[{out}]")
    graph.append(
        f"[room][hum]{''.join(event_labels)}amix=inputs={2 + len(event_labels)}:normalize=0,"
        "highpass=f=30,lowpass=f=10000,"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={DURATION - 6}:d=6,"
        "alimiter=limit=0.75:attack=5:release=120,"
        f"atrim=duration={DURATION},loudnorm=I=-28:TP=-5:LRA=12[out]"
    )
    return ";".join(graph)


def main() -> None:
    global DURATION, EVENTS
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=DURATION)
    parser.add_argument(
        "--storyboard",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "02_storyboard.csv",
        help="Storyboard whose scene starts drive the sparse physical cues.",
    )
    args = parser.parse_args()
    if args.duration <= 0:
        raise SystemExit("--duration must be positive")
    DURATION = args.duration
    EVENTS = aligned_events(args.storyboard.resolve())
    output = args.output.resolve()
    report = args.report.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    inputs, indexes = source_inputs()
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs,
        "-filter_complex", build_graph(indexes), "-map", "[out]",
        "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s24le", str(output),
    ]
    subprocess.run(command, check=True)
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=filename,duration,size:stream=codec_name,sample_rate,channels,bits_per_sample",
                "-of", "json", str(output),
            ],
            text=True,
        )
    )
    probe["production"] = {
        "method": "Original mathematical synthesis with FFmpeg; no samples or third-party recordings",
        "storyboard": str(args.storyboard.resolve()),
        "sha256": sha256(output),
        "event_count": sum(len(times) for times in EVENTS.values()),
    }
    report.write_text(json.dumps(probe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SFX/ambience stem: {output}")


if __name__ == "__main__":
    main()
