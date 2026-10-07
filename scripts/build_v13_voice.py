#!/usr/bin/env python3
"""Generate the V13 narration (one voice, see VOICE) and its timeline.

Text is read verbatim from ``v13_script_content.py`` (the DOCX submitted to the
lecturer). Only TTS input is respelled for words the voice misreads; subtitles
keep the original spelling. Each paragraph is split at ``[PAUSE x]`` marks;
every chunk is synthesized once (cached by text hash), then the master is
assembled with exact silences.

Outputs (audio/vo/v13_vivienne/):
  VO_V13_48K.wav         mono 48 kHz 16-bit master
  timeline.json          chapters → paragraphs → chunks with global times
                         and word boundaries
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import wave
from array import array
from pathlib import Path

import edge_tts

from v13_script_content import CHAPTERS

from common import FFMPEG, ROOT

OUT = ROOT / "audio/vo/v13_vivienne"
CHUNKS = ROOT / "audio/tts_cache"  # TTS cache keyed by voice|rate|text: unchanged paragraphs are never re-synthesized
VOICE = "fr-FR-VivienneMultilingualNeural"  # chosen by the user 2026-10-04 (brighter, livelier)
SR = 48_000
LEAD_IN = 0.8
CHAPTER_BREATH = 4.0
PAUSE_SCALE = 1.1  # pause marks slightly longer for the faster voice
PARAGRAPH_GAP = 0.65  # breath after every paragraph (user feedback)
TAIL = 1.2
PAUSE_RE = re.compile(r"\[PAUSE ([\d.]+)\]")

# Respellings verified with Whisper ASR (2026-10-04): only words the voice misread.
PRONUNCIATION = {
    "VNeID": "Vê En e ai đi",
    "“technical code”": "tếch-ni-cồn cốt",
    "technical code": "tếch-ni-cồn cốt",
}


def tts_text(text: str) -> str:
    for src, dst in PRONUNCIATION.items():
        text = text.replace(src, dst)
    return text


def split_chunks(paragraph: str) -> list[tuple[str, float]]:
    """Return [(text, pause_after_seconds)] split at PAUSE marks."""
    parts = PAUSE_RE.split(paragraph)
    chunks = []
    for i in range(0, len(parts), 2):
        text = parts[i].strip()
        pause = float(parts[i + 1]) * PAUSE_SCALE if i + 1 < len(parts) else 0.0
        if text:
            chunks.append((text, pause))
        elif chunks:
            chunks[-1] = (chunks[-1][0], chunks[-1][1] + pause)
    return chunks


async def synth(text: str, mp3: Path, rate: str, attempts: int = 4) -> list[dict]:
    for attempt in range(1, attempts + 1):
        try:
            return await _synth_once(text, mp3, rate)
        except (edge_tts.exceptions.NoAudioReceived, OSError, asyncio.TimeoutError) as exc:
            if attempt == attempts:
                raise RuntimeError(f"TTS failed after {attempts} attempts: {text[:80]!r}") from exc
            await asyncio.sleep(2 ** attempt)
    raise AssertionError("unreachable")


async def _synth_once(text: str, mp3: Path, rate: str) -> list[dict]:
    comm = edge_tts.Communicate(text, VOICE, rate=rate, boundary="WordBoundary")
    words, audio = [], bytearray()
    async for msg in comm.stream():
        if msg["type"] == "audio":
            audio.extend(msg["data"])
        elif msg["type"] == "WordBoundary":
            words.append({"t": msg["offset"] / 1e7, "d": msg["duration"] / 1e7, "w": msg["text"]})
    if not audio:
        raise RuntimeError(f"empty audio for: {text[:60]}")
    mp3.write_bytes(bytes(audio))
    return words


def decode(mp3: Path) -> array:
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        check=True, capture_output=True).stdout
    pcm = array("h")
    pcm.frombytes(raw)
    return pcm


def trim_silence(pcm: array, threshold: int = 300) -> tuple[array, float]:
    """Trim leading/trailing near-silence; return trimmed pcm and lead offset seconds."""
    start = next((i for i, v in enumerate(pcm) if abs(v) > threshold), 0)
    end = next((i for i in range(len(pcm) - 1, -1, -1) if abs(pcm[i]) > threshold), len(pcm) - 1)
    pad = int(0.04 * SR)
    start, end = max(0, start - pad), min(len(pcm), end + pad)
    return pcm[start:end], start / SR


async def build(rate: str) -> dict:
    chunk_dir = CHUNKS
    chunk_dir.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    master = array("h", bytes(int(LEAD_IN * SR) * 2))
    timeline = {"voice": VOICE, "rate": rate, "sample_rate": SR, "chapters": []}

    def now() -> float:
        return len(master) / SR

    for ci, ch in enumerate(CHAPTERS):
        if ci:
            master.extend(array("h", bytes(int(CHAPTER_BREATH * SR) * 2)))
        ch_rec = {"title": ch["title"], "start": now(), "paragraphs": []}
        for para_label, para in ch["paras"]:
            p_rec = {"label": para_label, "start": now(), "chunks": []}
            for text, pause in split_chunks(para):
                spoken = tts_text(text)
                key = hashlib.sha1(f"{VOICE}|{rate}|{spoken}".encode()).hexdigest()[:16]
                mp3, meta = chunk_dir / f"{key}.mp3", chunk_dir / f"{key}.json"
                if mp3.exists() and meta.exists():
                    words = json.loads(meta.read_text())
                else:
                    words = await synth(spoken, mp3, rate)
                    meta.write_text(json.dumps(words, ensure_ascii=False))
                pcm, lead = trim_silence(decode(mp3))
                t0 = now()
                master.extend(pcm)
                p_rec["chunks"].append({
                    "text": text, "tts": spoken, "start": t0, "end": now(),
                    "words": [{**w, "t": round(t0 + w["t"] - lead, 3)} for w in words],
                })
                master.extend(array("h", bytes(int(pause * SR) * 2)))
            # A short breath after every paragraph (user feedback: regular pauses).
            master.extend(array("h", bytes(int(PARAGRAPH_GAP * SR) * 2)))
            p_rec["end"] = now()
            ch_rec["paragraphs"].append(p_rec)
        ch_rec["end"] = now()
        timeline["chapters"].append(ch_rec)
    master.extend(array("h", bytes(int(TAIL * SR) * 2)))
    timeline["duration"] = now()

    with wave.open(str(OUT / "VO_V13_48K.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(master.tobytes())
    (OUT / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
    return timeline


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rate", default="+7%")
    args = ap.parse_args()
    tl = asyncio.run(build(args.rate))
    for ch in tl["chapters"]:
        print(f"{ch['start']:8.2f} {ch['end']:8.2f}  {ch['title']}")
    print(f"total {tl['duration']:.2f}s")


if __name__ == "__main__":
    main()
