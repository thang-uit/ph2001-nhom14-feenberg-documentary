#!/usr/bin/env python3
"""Compare the Whisper transcript of the V13 voice with the script text.

Prints every region where ASR and script disagree by more than a token or
two, so a human can listen to just those timestamps. ASR errors on proper
names are expected; the report is a pointer list, not a verdict.
"""

from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from v13_script_content import CHAPTERS  # noqa: E402

from common import ROOT  # noqa: E402


def tokens(s: str) -> list[str]:
    s = re.sub(r"\[PAUSE [\d.]+\]", " ", s).lower()
    return re.findall(r"[\wÀ-ỹ]+", s)


def main() -> None:
    script = [t for ch in CHAPTERS for _, p in ch["paras"] for t in tokens(p)]
    rows = [line.split("\t") for line in (ROOT / "docs/research/asr_transcript.txt").read_text().splitlines() if line.strip()]
    asr, times = [], []
    for start, _end, text in rows:
        for tok in tokens(text):
            asr.append(tok)
            times.append(float(start))
    sm = difflib.SequenceMatcher(a=script, b=asr, autojunk=False)
    issues = 0
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal" or max(a1 - a0, b1 - b0) < 2:
            continue
        issues += 1
        t = times[min(b0, len(times) - 1)] if times else 0
        print(f"{t:8.1f}s  script: {' '.join(script[a0:a1])!r:60.60}  asr: {' '.join(asr[b0:b1])!r}")
    print(f"\nscript tokens={len(script)} asr tokens={len(asr)} similarity={sm.ratio():.3f} regions={issues}")


if __name__ == "__main__":
    main()
