#!/usr/bin/env python3
"""Transcribe the V13 narration master (faster-whisper small, int8) for qa_v13_asr.py.

Optional QA step: needs `pip install faster-whisper` (downloads the model once).
"""

from faster_whisper import WhisperModel

from common import ROOT


def main() -> None:
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(ROOT / "audio/vo/v13_vivienne/VO_V13_48K.wav"), language="vi", beam_size=5)
    out = ROOT / "docs/research/asr_transcript.txt"
    with out.open("w") as fh:
        for s in segments:
            fh.write(f"{s.start:.2f}\t{s.end:.2f}\t{s.text.strip()}\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
