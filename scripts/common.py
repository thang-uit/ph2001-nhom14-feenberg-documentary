"""Shared, machine-independent settings for the V13 pipeline.

Everything is resolved relative to this repository, so the folder can be moved or
unzipped on another Mac. Only two things come from the machine:
  * ffmpeg — from the `imageio-ffmpeg` pip package (bundled binary) or `ffmpeg` on PATH;
  * the Avenir Next font — part of macOS (/System/Library/Fonts).
"""

from __future__ import annotations

import os
import shutil
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
DELIVER = ROOT / "delivery"  # finished videos, script DOCX, subtitles

W, H = 1920, 1080
IVORY = (244, 239, 229)

# One typeface for the whole film. Only faces verified to carry every Vietnamese glyph.
_AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
_AVENIR_INDEX = {"bold": 0, "demi": 2, "italic": 4, "medium": 5, "regular": 7}


def _find_ffmpeg() -> str:
    try:
        import imageio_ffmpeg  # bundled static binary, no Homebrew needed
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        found = shutil.which("ffmpeg")
        if not found:
            raise SystemExit("ffmpeg not found: `pip install imageio-ffmpeg` or install ffmpeg")
        return found


FFMPEG = _find_ffmpeg()


def node_env() -> dict:
    """Environment for npx/remotion. Behind a TLS-inspecting proxy, set EXTRA_CA_BUNDLE to its CA file."""
    env = dict(os.environ)
    ca = os.environ.get("EXTRA_CA_BUNDLE") or "/usr/local/opt/openssl@3/ssl/cert.pem"
    if Path(ca).exists():
        env.setdefault("NODE_EXTRA_CA_CERTS", ca)
    return env


@lru_cache(maxsize=None)
def sans(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_AVENIR, size, index=_AVENIR_INDEX[weight])


def text_w(face: ImageFont.FreeTypeFont, s: str) -> int:
    left, _, right, _ = face.getbbox(s)
    return right - left


def wrap(face: ImageFont.FreeTypeFont, s: str, max_w: int) -> list[str]:
    """Greedy word wrap with the real font metrics (same face the browser uses)."""
    words, lines, line = s.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if text_w(face, trial) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines
