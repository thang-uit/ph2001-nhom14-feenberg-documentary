#!/usr/bin/env python3
"""Synthesize an original documentary music bed with FFmpeg only.

The score uses mathematical oscillators and filtered noise; it contains no
third-party recordings or samples. It is intentionally restrained so the
Vietnamese narration remains the dominant element in the final mix.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


SAMPLE_RATE = 48_000
TOTAL_DURATION = 933.366667
CHORD_DURATION = 26.0
CROSSFADE = 3.0


@dataclass(frozen=True)
class Chord:
    name: str
    frequencies: tuple[float, ...]


CHORDS = {
    "Dm9": Chord("Dm9", (73.416, 110.000, 130.813, 174.614, 329.628)),
    "BbM7": Chord("BbM7", (58.270, 87.307, 110.000, 146.832, 349.228)),
    "FM7A": Chord("FM7A", (55.000, 130.813, 164.814, 174.614, 220.000)),
    "Csus2": Chord("Csus2", (65.406, 97.999, 146.832, 195.998, 293.665)),
    "Gm9": Chord("Gm9", (48.999, 97.999, 116.541, 146.832, 220.000)),
    "Am7": Chord("Am7", (55.000, 110.000, 130.813, 164.814, 261.626)),
    "EbM7": Chord("EbM7", (77.782, 116.541, 146.832, 195.998, 311.127)),
    "Dsus2": Chord("Dsus2", (73.416, 110.000, 146.832, 164.814, 293.665)),
}


# Forty-three 26-second plates joined with 3-second equal-power crossfades yield
# 992 seconds. The mix is trimmed to the current speech-locked V7 timeline.
# Changes in progression follow the eight documentary chapters without using
# moralizing major/minor contrasts for philosophical positions.
SEQUENCE = (
    ["Dm9", "BbM7", "FM7A", "Csus2", "Dm9"]
    + ["Dm9", "Gm9", "BbM7", "Csus2", "FM7A"]
    + ["Dsus2", "BbM7", "Gm9", "Csus2", "Dsus2"]
    + ["Dm9", "EbM7", "Gm9", "Dm9", "BbM7"]
    + ["Gm9", "BbM7", "Dm9", "Csus2", "Gm9"]
    + ["BbM7", "FM7A", "Dm9", "Gm9", "BbM7"]
    + ["Dsus2", "Gm9", "BbM7", "Csus2", "Dm9"]
    + ["Dm9", "BbM7", "FM7A", "Csus2", "Dm9", "Dm9", "BbM7", "Dm9"]
)


NOTE_FREQUENCIES = {
    "D4": 293.665,
    "F4": 349.228,
    "A4": 440.000,
    "C5": 523.251,
    "E5": 659.255,
    "G5": 783.991,
}


# Six-note motif: CÔNG CỤ → THIẾT KẾ → GIÁ TRỊ → QUYỀN LỰC → THAM GIA
# → CẢI BIẾN. Earlier statements deliberately stop before all six notes.
MOTIF_EVENTS = [
    (30.0, "D4"), (30.52, "F4"), (31.08, "A4"),
    (137.0, "D4"), (137.55, "F4"), (138.10, "A4"), (138.65, "C5"),
    (296.0, "D4"), (296.58, "F4"), (297.18, "A4"),
    (407.0, "D4"), (407.58, "F4"), (408.18, "A4"), (408.78, "C5"),
    (509.0, "C5"),
    (683.0, "D4"), (683.62, "F4"), (684.28, "A4"),
    (801.0, "D4"), (801.50, "F4"), (802.00, "A4"),
    (802.50, "C5"), (803.00, "E5"), (803.50, "G5"),
    (838.0, "D4"), (838.52, "F4"), (839.04, "A4"),
    (839.56, "C5"), (840.08, "E5"), (840.60, "G5"),
    (858.0, "D4"), (858.72, "A4"), (859.50, "D4"),
    (905.0, "F4"), (905.75, "A4"), (906.55, "D4"),
    # A sparse closing cadence under the silent film credits.  It resolves
    # the recurring motif without introducing a new musical style.
    (936.0, "D4"), (937.0, "F4"), (938.0, "A4"),
    (946.0, "C5"), (947.0, "A4"), (948.0, "F4"),
    (959.0, "D4"),
]


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_tools() -> None:
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise SystemExit(f"Required binary not found: {binary}")


def render_chord(chord: Chord, output: Path) -> None:
    envelope = (
        f"min(1,t/2.4)*min(1,({CHORD_DURATION}-t)/2.8)"
        "*(0.94+0.06*sin(2*PI*0.067*t))"
    )
    weights = (0.040, 0.023, 0.019, 0.015, 0.010)
    left_parts: list[str] = []
    right_parts: list[str] = []
    for index, (frequency, weight) in enumerate(zip(chord.frequencies, weights)):
        phase = 0.17 * (index + 1)
        left_parts.append(f"{weight}*sin(2*PI*{frequency:.5f}*t+{phase:.3f})")
        right_parts.append(
            f"{weight}*sin(2*PI*{frequency * (1.00035 + index * 0.00004):.5f}*t+{phase + 0.31:.3f})"
        )
    left = f"({'+'.join(left_parts)})*{envelope}"
    right = f"({'+'.join(right_parts)})*{envelope}"
    source = f"aevalsrc=exprs='{left}|{right}':s={SAMPLE_RATE}:d={CHORD_DURATION}:c=stereo"
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            source,
            "-af",
            "highpass=f=38,lowpass=f=2600,"
            "aecho=0.86:0.52:347|733:0.16|0.09,"
            "acompressor=threshold=0.12:ratio=1.6:attack=80:release=500",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "2",
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )


def render_note(name: str, frequency: float, output: Path) -> None:
    duration = 4.2
    left = (
        f"(0.095*sin(2*PI*{frequency:.5f}*t)"
        f"+0.027*sin(4*PI*{frequency:.5f}*t+0.18)"
        f"+0.010*sin(6*PI*{frequency:.5f}*t+0.31))*exp(-1.65*t)"
    )
    right_frequency = frequency * 1.0007
    right = (
        f"(0.091*sin(2*PI*{right_frequency:.5f}*t+0.13)"
        f"+0.026*sin(4*PI*{right_frequency:.5f}*t+0.41)"
        f"+0.009*sin(6*PI*{right_frequency:.5f}*t+0.57))*exp(-1.61*t)"
    )
    source = f"aevalsrc=exprs='{left}|{right}':s={SAMPLE_RATE}:d={duration}:c=stereo"
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            source,
            "-af",
            "highpass=f=90,lowpass=f=4800,aecho=0.82:0.48:281|617:0.13|0.08",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "2",
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )


def render_texture(output: Path) -> None:
    duration = TOTAL_DURATION
    source = (
        "aevalsrc=exprs='"
        "0.0038*sin(2*PI*36.708*t)*(0.55+0.45*sin(2*PI*0.041*t))"
        "+0.0018*sin(2*PI*55*t+0.3)*(0.55+0.45*sin(2*PI*0.083*t))|"
        "0.0036*sin(2*PI*36.721*t+0.2)*(0.55+0.45*sin(2*PI*0.039*t))"
        "+0.0019*sin(2*PI*55.018*t+0.5)*(0.55+0.45*sin(2*PI*0.079*t))'"
        f":s={SAMPLE_RATE}:d={duration}:c=stereo"
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            source,
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=pink:amplitude=0.0022:duration={duration}:sample_rate={SAMPLE_RATE}",
            "-filter_complex",
            "[1:a]highpass=f=95,lowpass=f=520,pan=stereo|c0=c0|c1=c0[air];"
            "[0:a][air]amix=inputs=2:normalize=0,"
            f"afade=t=in:st=0:d=3,afade=t=out:st={TOTAL_DURATION - 6}:d=6[out]",
            "-map",
            "[out]",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "2",
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )


def render_pulse(output: Path) -> None:
    """Add a restrained documentary pulse so the score has forward motion."""

    left = (
        "0.020*sin(2*PI*73.416*t)*exp(-5.6*mod(t,2))"
        "+0.006*sin(2*PI*146.832*t+0.16)*exp(-8.4*mod(t,2))"
    )
    right = (
        "0.019*sin(2*PI*73.442*t+0.08)*exp(-5.4*mod(t,2))"
        "+0.006*sin(2*PI*146.884*t+0.31)*exp(-8.1*mod(t,2))"
    )
    source = f"aevalsrc=exprs='{left}|{right}':s={SAMPLE_RATE}:d={TOTAL_DURATION}:c=stereo"
    chapter_gain = (
        "if(between(t,509,683),0.18,"
        "if(between(t,296,407),0.88,"
        f"if(between(t,858,{TOTAL_DURATION}),0.38,0.58)))"
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", source,
            "-af",
            f"highpass=f=42,lowpass=f=1100,volume='{chapter_gain}':eval=frame,"
            "aecho=0.76:0.30:179|367:0.09|0.05,"
            f"afade=t=in:st=0:d=2.5,afade=t=out:st={TOTAL_DURATION - 6}:d=6",
            "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s24le", str(output),
        ]
    )


def build_score(work_dir: Path, output: Path) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    chord_dir = work_dir / "chords"
    note_dir = work_dir / "notes"
    chord_dir.mkdir(exist_ok=True)
    note_dir.mkdir(exist_ok=True)

    for chord in CHORDS.values():
        render_chord(chord, chord_dir / f"{chord.name}.wav")
    for name, frequency in NOTE_FREQUENCIES.items():
        render_note(name, frequency, note_dir / f"{name}.wav")
    texture = work_dir / "organic_texture.wav"
    render_texture(texture)
    pulse_track = work_dir / "documentary_pulse.wav"
    render_pulse(pulse_track)

    inputs: list[str] = []
    for chord_name in SEQUENCE:
        inputs.extend(["-i", str(chord_dir / f"{chord_name}.wav")])
    texture_index = len(SEQUENCE)
    inputs.extend(["-i", str(texture)])
    pulse_index = texture_index + 1
    inputs.extend(["-i", str(pulse_track)])
    motif_start_index = pulse_index + 1
    for _, note_name in MOTIF_EVENTS:
        inputs.extend(["-i", str(note_dir / f"{note_name}.wav")])

    graph: list[str] = []
    previous = "[0:a]"
    for index in range(1, len(SEQUENCE)):
        label = f"bed{index}"
        graph.append(
            f"{previous}[{index}:a]acrossfade=d={CROSSFADE}:c1=tri:c2=tri[{label}]"
        )
        previous = f"[{label}]"
    graph.append(
        f"{previous}atrim=duration={TOTAL_DURATION},asetpts=N/SR/TB,volume=0.78[bed]"
    )
    graph.append(f"[{texture_index}:a]atrim=duration={TOTAL_DURATION},volume=0.72[texture]")
    graph.append(f"[{pulse_index}:a]atrim=duration={TOTAL_DURATION},volume=0.78[pulse]")

    motif_labels: list[str] = []
    for offset, (start, _) in enumerate(MOTIF_EVENTS):
        input_index = motif_start_index + offset
        label = f"note{offset}"
        delay_ms = round(start * 1000)
        graph.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms}[{label}]")
        motif_labels.append(f"[{label}]")
    graph.append(
        f"{''.join(motif_labels)}amix=inputs={len(motif_labels)}:normalize=0,volume=0.72[motif]"
    )
    graph.append(
        "[bed][texture][pulse][motif]amix=inputs=4:normalize=0,"
        "highpass=f=32,lowpass=f=9200,"
        "acompressor=threshold=0.11:ratio=1.5:attack=100:release=650,"
        f"afade=t=out:st={TOTAL_DURATION - 6}:d=6,atrim=duration={TOTAL_DURATION},"
        "loudnorm=I=-23:TP=-2:LRA=10[out]"
    )

    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            *inputs,
            "-filter_complex",
            ";".join(graph),
            "-map",
            "[out]",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "2",
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )


def probe(output: Path, report: Path) -> None:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=filename,duration,size,bit_rate:stream=codec_name,sample_rate,channels,bits_per_sample",
            "-of",
            "json",
            str(output),
        ],
        text=True,
    )
    data = json.loads(raw)
    data["production"] = {
        "method": "Original mathematical synthesis with FFmpeg; no third-party samples",
        "timeline_seconds": TOTAL_DURATION,
        "sha256": sha256(output),
        "motif": "Six-note methodological motif: D4 F4 A4 C5 E5 G5",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    global TOTAL_DURATION
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=TOTAL_DURATION)
    args = parser.parse_args()
    if args.duration <= 0:
        raise SystemExit("--duration must be positive")
    TOTAL_DURATION = args.duration
    ensure_tools()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build_score(args.work_dir.resolve(), args.output.resolve())
    probe(args.output.resolve(), args.report.resolve())
    print(f"Original score created: {args.output.resolve()}")
    print(f"Score metadata: {args.report.resolve()}")


if __name__ == "__main__":
    main()
