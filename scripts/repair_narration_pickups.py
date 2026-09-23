#!/usr/bin/env python3
"""Replace an unclear term with an authorized ChatGPT read-aloud pickup.

Only the specified waveform interval changes. Duration and locked subtitles
remain stable. Keep the original stem for a recoverable comparison.
"""
import argparse
import json
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--pickup", type=Path, required=True)
    parser.add_argument("--source-start", type=float, required=True)
    parser.add_argument("--source-end", type=float, required=True)
    parser.add_argument("--target-start", type=float, required=True)
    parser.add_argument("--target-end", type=float, required=True)
    parser.add_argument("--gain-db", type=float, default=0)
    parser.add_argument("--compressor", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() in {args.original.resolve(), args.pickup.resolve()}:
        raise ValueError("Refusing to overwrite a source recording")
    target_duration = args.target_end - args.target_start
    speed = (args.source_end - args.source_start) / target_duration
    if not 0.72 <= speed <= 1.40:
        raise ValueError(f"Pickup pace change too large: {speed:.3f}")
    dynamics = "acompressor=threshold=0.10:ratio=3:attack=5:release=80:makeup=2.3," if args.compressor else ""
    graph = (
        f"[0:a]asplit=2[a][b];[a]atrim=end={args.target_start},asetpts=PTS-STARTPTS[before];"
        f"[b]atrim=start={args.target_end},asetpts=PTS-STARTPTS[after];"
        f"[1:a]atrim=start={args.source_start}:end={args.source_end},asetpts=PTS-STARTPTS,"
        f"atempo={speed:.9f},{dynamics}volume={args.gain_db}dB,aresample=48000,"
        f"apad=whole_dur={target_duration},atrim=duration={target_duration},"
        f"afade=t=in:d=0.008,afade=t=out:st={target_duration-0.008}:d=0.008[fixed];"
        "[before][fixed][after]concat=n=3:v=0:a=1[out]"
    )
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.original), "-i", str(args.pickup), "-filter_complex", graph, "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(args.output)], check=True)
    args.report.write_text(json.dumps({k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}, indent=2) + "\n")


if __name__ == "__main__":
    main()
