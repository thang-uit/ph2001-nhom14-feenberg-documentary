#!/usr/bin/env python3
"""V13 film: semantic visual plan → Remotion picture → mix → final with credit.

Pipeline (cached under renders/v13/):
  plan     scene/shot timing from audio/vo/v13_vivienne/timeline.json
  export   remotion/src/data/film.json + public/ hardlinks (footage, paper, photo)
  picture  `npx remotion render Film` → PICTURE_V13_CONTENT.mp4 (graphics, footage,
           dissolves, chapter cards and subtitles are all drawn by Remotion)
  mix      voice + score (ducked) → content mix
  final    picture + mix, crossfade into the untouched credit V4 → YouTube master,
           copied to delivery/

Usage: v13_film.py [plan|export|picture|mix|final|all] [--res 1080|1440] [--concurrency N]
       --res 1440 renders the same film natively at 2560×1440 (2K) for YouTube.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from common import DELIVER, FFMPEG, IVORY, ROOT, H as BASE_H, W as BASE_W, node_env, sans, wrap
from v13_script_content import CHAPTERS

REMOTION = ROOT / "remotion"
TIMELINE = ROOT / "audio/vo/v13_vivienne/timeline.json"
VOICE = ROOT / "audio/vo/v13_vivienne/VO_V13_48K.wav"
SCORE = ROOT / "audio/music/SCORE_SUNO_V8_48K.wav"
CREDIT = ROOT / "assets/credit/CREDIT_TPHCM_OH_YEAH_V4.mp4"
CREDIT_SHA = "a96f6eb30342562e69b84c5e58c1d28d7b6da591a8969a35b8c013362cab4b93"
CREDIT_DURATION = 54.1
CREDIT_XFADE = 0.8
OUT = ROOT / "renders/v13"
FEENBERG_PHOTO = ROOT / "assets/photos/andrew_feenberg_wikimedia.jpg"

FPS = 30
TRANS = 0.4
TRANS_F = round(TRANS * FPS)
CHAPTER_CARD_S = 5.6
MIN_GRAPHIC_F = round(4.5 * FPS)
FOOTAGE_BOOST = 1.45  # user feedback (V12): more live footage, less text-only screen time
SUB_FACE = sans(40, "demi")
SUB_MAX_W = 1560
FINAL_NAME = "Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg_V13"
# Output profiles. 1440 = native 2K render (Remotion --scale), not an upscale of the 1080p master.
PROFILES = {
    1080: {"w": 1920, "h": 1080, "scale": 1, "level": "4.2", "suffix": "1080p"},
    1440: {"w": 2560, "h": 1440, "scale": 4 / 3, "level": "5.1", "suffix": "2K_1440p"},
}
BT709 = ["-color_range", "tv", "-colorspace", "bt709", "-color_trc", "bt709", "-color_primaries", "bt709"]

M = "assets/real/"  # real footage (Mixkit licence), separate from the credit footage
AI_PREFIXES = ("assets/ai/",)  # AI illustration clips: cropped + labelled MINH HỌA BẰNG AI

CHAPTER_META = [
    ("Mở đầu", "Một thao tác, hai chiều — dân chủ nằm ở đâu?"),
    ("Dân chủ là gì?", "Từ nghĩa gốc đến định nghĩa làm việc."),
    ("Dân chủ hóa là gì?", "Quyền nào, ở mức độ nào?"),
    ("Từ triết học đến công nghệ", "Quyền lực công trong hệ thống kỹ thuật."),
    ("Andrew Feenberg", "Công nghệ mang giá trị — nhưng có thể được định hướng."),
    ("Một tình huống cụ thể", "Phản hồi của người bệnh đã sửa thiết kế ra sao?"),
    ("Ví dụ phân tích: VNeID", "Quản trị dữ liệu công dân dưới góc nhìn dân chủ."),
    ("Bảo mật, góp ý, phản hồi", "Được góp ý chưa chắc là được tham gia."),
    ("Sở hữu trí tuệ", "Bảo vệ quyền có phải là dân chủ hóa?"),
    ("Lập trường của Nhóm 14", "Ai giám sát, ai yêu cầu sửa, ai khắc phục?"),
    ("Kết luận", "Trả lời câu hỏi ban đầu."),
]


def F(asset: str, weight: float, start: float = 0.0) -> tuple:
    return ("F", asset, weight, start)


def Gx(name: str, weight: float = 1.0) -> tuple:
    return ("G", name, weight)


# scene id → shots. Weights split the scene after fixed chapter cards. Graphic names are
# keys of remotion/src/gfx/registry.tsx.
PLAN: dict[str, list[tuple]] = {
    # 1 Mở đầu (shortened)
    "V13-S01": [F(M + "mixkit_41165_1080.mp4", 0.4, 1.0), Gx("data_trace", 0.6)],
    "V13-S02": [F("assets/ai/V9_004.mp4", 0.4, 0.3), Gx("three_questions", 0.6)],
    "V13-S03": [Gx("film_title", 0.55), Gx("two_concepts", 0.45)],
    # 2 Dân chủ là gì?
    "V13-S04": [F(M + "mixkit_4401_1080.mp4", 0.4, 1.0), Gx("etymology", 0.6)],
    "V13-S05": [F(M + "mixkit_4169_1080.mp4", 0.22, 1.0), Gx("dimensions", 0.78)],
    "V13-S06": [F(M + "mixkit_914_1080.mp4", 0.25, 1.0), Gx("lenin", 0.75)],
    "V13-S07": [Gx("hcm", 0.3), F("assets/ai/S009_flow_1080p.mp4", 0.22, 0.3), Gx("constitution", 0.48)],
    "V13-S08": [F("assets/ai/V9_030.mp4", 0.3, 0.3), Gx("rings", 0.7)],
    "V13-S09": [F(M + "mixkit_4547_1080.mp4", 0.4, 2.0), Gx("check_test", 0.6)],
    # 3 Dân chủ hóa
    "V13-S10": [F(M + "mixkit_42666_1080.mp4", 0.38, 0.3), Gx("process", 0.62)],
    "V13-S11": [F(M + "mixkit_42664_1080.mp4", 0.28, 0.3), Gx("law_levels", 0.72)],
    "V13-S12": [F(M + "mixkit_4916_1080.mp4", 0.3, 1.0), Gx("myths", 0.7)],
    "V13-S13": [F("assets/ai/S051_flow_1080p.mp4", 0.22, 0.3), F("assets/ai/V9_010.mp4", 0.22, 0.3), Gx("conditions", 0.56)],
    "V13-S14": [Gx("rights_matrix")],
    "V13-S15": [Gx("change_test")],
    # 4 Triết học → công nghệ (public power through technical systems)
    "V13-S16": [F(M + "mixkit_4648_1080.mp4", 0.35, 1.0), Gx("chain1", 0.65)],
    "V13-S17": [F(M + "mixkit_4872_1080.mp4", 0.25, 1.0), Gx("power_bridge", 0.75)],
    "V13-S18": [F(M + "mixkit_29991_1080.mp4", 0.25, 1.0), Gx("feen_power", 0.75)],
    "V13-S19": [F(M + "mixkit_50598_1080.mp4", 0.2, 1.0), Gx("three_terms", 0.55), Gx("chain2", 0.25)],
    "V13-S20": [Gx("two_way")],
    "V13-S21": [F("assets/ai/V9_002.mp4", 0.4, 0.3), Gx("chain3", 0.6)],
    # 5 Feenberg
    "V13-S22": [Gx("feenberg")],
    "V13-S23": [F("assets/ai/S015_neutral_tool_1080p.mp4", 0.25, 0.3), Gx("matrix", 0.75)],
    "V13-S24": [F("assets/ai/S034_multiple_options_1080p.mp4", 0.3, 0.3), F("assets/ai/S034_scheduling_options_alt_1080p.mp4", 0.3, 0.3), Gx("options", 0.4)],
    "V13-S25": [F("assets/ai/S040_technical_code_materials_1080p.mp4", 0.28, 1.3), F("assets/ai/S040_constraints_alt_1080p.mp4", 0.25, 0.3), Gx("code", 0.47)],
    "V13-S26": [F("assets/ai/S065_network_users_alt_1080p.mp4", 0.3, 0.3), F("assets/ai/V9_036.mp4", 0.28, 0.3), Gx("email", 0.42)],
    "V13-S27": [F("assets/ai/V9_037.mp4", 0.35, 0.3), Gx("rationality", 0.65)],
    "V13-S28": [F("assets/ai/V9_006.mp4", 0.3, 0.3), Gx("paths", 0.7)],
    "V13-S29": [F("assets/ai/V9_008.mp4", 0.28, 0.3), Gx("extend", 0.52), F("assets/ai/V9_007.mp4", 0.2, 0.3)],
    "V13-S30": [Gx("initiative", 0.45), F("assets/ai/V9_015.mp4", 0.25, 0.3), F(M + "mixkit_4809_1080.mp4", 0.3, 0.5)],
    # 6 Tình huống: AIDS patients and the redesign of drug trials (graphics + sources, no AI re-enactment)
    "V13-S31": [F(M + "mixkit_8739_1080.mp4", 0.25, 1.0), Gx("case_before", 0.75)],
    "V13-S32": [Gx("case_timeline")],
    "V13-S33": [F(M + "mixkit_42648_1080.mp4", 0.22, 0.2), Gx("case_quote", 0.78)],
    "V13-S34": [Gx("case_test")],
    # 7 VNeID
    "V13-S35": [F(M + "mixkit_242_1080.mp4", 0.35, 0.3), Gx("vneid", 0.65)],
    "V13-S36": [F("assets/ai/V9_012.mp4", 0.4, 0.3), Gx("scope", 0.6)],
    "V13-S37": [F(M + "mixkit_41180_1080.mp4", 0.35, 0.5), Gx("questions", 0.65)],
    "V13-S38": [F(M + "mixkit_308_1080.mp4", 0.2, 1.0), Gx("privacy_law", 0.6), F(M + "mixkit_4907_1080.mp4", 0.2, 1.0)],
    "V13-S39": [F("assets/ai/S073_adaptive_computer_1080p.mp4", 0.3, 0.3), Gx("whose", 0.7)],
    "V13-S40": [F("assets/ai/S050_flow_1080p.mp4", 0.15, 0.3), Gx("lifecycle", 0.73), F("assets/ai/V9_018.mp4", 0.12, 0.3)],
    "V13-S41": [F(M + "mixkit_1781_1080.mp4", 0.2, 0.5), Gx("winwin", 0.8)],
    # 8 Bảo mật, góp ý
    "V13-S42": [F("assets/ai/V9_005.mp4", 0.35, 0.3), Gx("four_terms", 0.65)],
    "V13-S43": [F("assets/ai/V9_027.mp4", 0.25, 0.5), Gx("ab", 0.75)],
    "V13-S45": [F(M + "mixkit_918_1080.mp4", 0.32, 0.5), Gx("funnel", 0.68)],
    # 9 Sở hữu trí tuệ
    "V13-S46": [F(M + "mixkit_29993_1080.mp4", 0.35, 1.0), Gx("ip_law", 0.65)],
    "V13-S47": [F("assets/ai/V9_029.mp4", 0.35, 0.3), Gx("ip_split", 0.65)],
    "V13-S48": [F(M + "mixkit_785_1080.mp4", 0.45, 0.5), Gx("ai_law", 0.55)],
    # 10 Lập trường
    "V13-S49": [Gx("thesis", 0.7), F("assets/ai/V9_017.mp4", 0.3, 0.3)],
    "V13-S50": [F("assets/ai/S063_flow_1080p.mp4", 0.4, 0.3), Gx("should", 0.6)],
    "V13-S51": [Gx("should_not")],
    "V13-S52": [F(M + "mixkit_8739_1080.mp4", 0.3, 8.5), Gx("obstacles", 0.7)],
    "V13-S53": [F(M + "mixkit_4547_1080.mp4", 0.18, 15.0), Gx("accountability", 0.82)],
    "V13-S54": [F(M + "mixkit_42656_1080.mp4", 0.25, 0.3), Gx("proposals", 0.75)],
    # 11 Kết luận
    "V13-S55": [F("assets/ai/V9_014.mp4", 0.25, 0.5), F("assets/ai/S086_flow_1080p.mp4", 0.2, 0.3), F("assets/ai/V9_069.mp4", 0.18, 0.3), Gx("answer", 0.37)],
    "V13-S56": [Gx("vn_values")],
    "V13-S57": [Gx("chain4")],
    "V13-S58": [F("assets/ai/V9_066.mp4", 0.45, 0.3), Gx("thanks", 0.55)],
}


@dataclass
class Shot:
    chapter: int
    scene: str
    index: int
    kind: str           # F footage, G graphic, C chapter card
    ref: str            # asset path, graphic name, or chapterN
    start: float        # global timeline start (s)
    frames: int         # assigned frames (without tail)
    tail: int           # extra frames that sit under the next shot's dissolve
    src_start: float = 0.0
    tag: str | None = None


# ----------------------------------------------------------------- helpers
def run(cmd: list[str], env: dict | None = None, cwd: Path | None = None) -> None:
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env, cwd=cwd)
    if res.returncode:
        raise RuntimeError(f"command failed: {' '.join(cmd[:12])}…\n{res.stderr[-3000:]}")


def media_duration(path: Path) -> float:
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if not m:
        raise ValueError(f"no duration: {path}")
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def load_timeline() -> dict:
    return json.loads(TIMELINE.read_text())


def all_words(tl: dict) -> list[dict]:
    return [w for ch in tl["chapters"] for p in ch["paragraphs"] for c in p["chunks"] for w in c["words"]]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# -------------------------------------------------------------------- plan
def build_plan() -> tuple[list[Shot], float]:
    tl = load_timeline()
    if len(tl["chapters"]) != len(CHAPTERS) or len(CHAPTER_META) != len(CHAPTERS):
        raise ValueError("timeline / CHAPTERS / CHAPTER_META disagree: rebuild the voice first")
    content_end = tl["duration"]
    shots: list[Shot] = []
    # Scene boundaries: the first scene of a chapter absorbs the chapter breath.
    bounds: list[tuple[int, str, float]] = []
    prev_end = 0.0
    for ci, (ch, tch) in enumerate(zip(CHAPTERS, tl["chapters"])):
        for si, (sid, idx, *_rest) in enumerate(ch["scenes"]):
            start = prev_end if si == 0 else tch["paragraphs"][idx[0]]["start"]
            bounds.append((ci, sid, 0.0 if (ci == 0 and si == 0) else start))
        prev_end = tch["end"]
    for k, (ci, sid, start) in enumerate(bounds):
        end = bounds[k + 1][2] if k + 1 < len(bounds) else content_end
        f0, f1 = round(start * FPS), round(end * FPS)
        total = f1 - f0
        specs = list(PLAN[sid])
        first_in_chapter = k == 0 or bounds[k - 1][0] != ci
        fixed: list[tuple[tuple, int]] = []
        if first_in_chapter and ci > 0:
            fixed.append((("C", f"chapter{ci + 1}", 0), round(CHAPTER_CARD_S * FPS)))
        remaining = total - sum(n for _, n in fixed)
        w = [s[2] * (FOOTAGE_BOOST if s[0] == "F" else 1.0) for s in specs]
        alloc = [round(remaining * x / sum(w)) for x in w]
        alloc[-1] = remaining - sum(alloc[:-1])
        # Cap footage by available source; give the excess to graphics in the scene.
        excess = 0
        for i, s in enumerate(specs):
            if s[0] == "F":
                avail = int((media_duration(ROOT / s[1]) - s[3] - TRANS - 0.1) * FPS)
                if alloc[i] > avail:
                    excess += alloc[i] - avail
                    alloc[i] = avail
        gi = [i for i, s in enumerate(specs) if s[0] == "G"]
        if excess:
            if not gi:
                raise ValueError(f"{sid}: footage too short by {excess / FPS:.2f}s and no graphic to absorb")
            for j, i in enumerate(gi):
                alloc[i] += excess // len(gi) + (1 if j < excess % len(gi) else 0)
        # Every graphic needs time to be read: borrow from the longest footage shot in the scene.
        for i in gi:
            deficit = MIN_GRAPHIC_F - alloc[i]
            fi = [j for j, s in enumerate(specs) if s[0] == "F"]
            while deficit > 0 and fi:
                j = max(fi, key=lambda q: alloc[q])
                take = min(deficit, alloc[j] - 2 * FPS)
                if take <= 0:
                    break
                alloc[j] -= take
                alloc[i] += take
                deficit -= take
        cursor = f0
        items = fixed + list(zip(specs, alloc))
        tag = f"{ci + 1:02d} · {CHAPTER_META[ci][0].upper()}"
        for i, (s, n) in enumerate(items):
            if n <= 0:
                raise ValueError(f"{sid}: non-positive shot length")
            shots.append(Shot(chapter=ci + 1, scene=sid, index=i + 1, kind=s[0], ref=s[1], start=cursor / FPS, frames=n,
                              tail=0, src_start=s[3] if s[0] == "F" else 0.0,
                              tag=tag if (s[0] == "F" and i == 0) else None))
            cursor += n
        assert cursor == f1, (sid, cursor, f1)
    for s in shots[:-1]:
        s.tail = TRANS_F
    return shots, content_end


# --------------------------------------------------------------- subtitles
def split_cues(text: str) -> list[str]:
    """Split a chunk into ≤2-line subtitle cues, preferring sentence then clause boundaries."""
    def fits(s: str) -> bool:
        return len(wrap(SUB_FACE, s, SUB_MAX_W)) <= 2

    sentences = re.findall(r"[^.?!]+[.?!]?[”\"]?", text)
    cues: list[str] = []
    for sent in (s.strip() for s in sentences):
        if not sent:
            continue
        if fits(sent):
            cues.append(sent)
            continue
        parts = re.split(r"(?<=[,;:])\s+", sent)
        cur = ""
        for part in parts:
            trial = f"{cur} {part}".strip()
            if fits(trial):
                cur = trial
                continue
            if cur:
                cues.append(cur)
            if fits(part):
                cur = part
            else:  # very long clause: hard split by words
                words, cur = part.split(), ""
                for w in words:
                    trial = f"{cur} {w}".strip()
                    if fits(trial):
                        cur = trial
                    else:
                        cues.append(cur)
                        cur = w
        if cur:
            cues.append(cur)
    return cues


def build_subtitle_cues() -> list[tuple[float, float, str]]:
    tl = load_timeline()
    out = []
    for ch in tl["chapters"]:
        for p in ch["paragraphs"]:
            for c in p["chunks"]:
                cues = split_cues(c["text"])
                n_orig = sum(len(q.split()) for q in cues)
                words = c["words"]
                m = len(words)
                k = 0
                for q in cues:
                    a = k
                    k += len(q.split())
                    ia = min(m - 1, round(a * m / n_orig))
                    t0 = words[ia]["t"] if a else c["start"]
                    t1 = words[min(m - 1, round(k * m / n_orig))]["t"] if k < n_orig else c["end"]
                    out.append((t0, max(t1, t0 + 0.6), q))
    fixed = []
    for i, (a, b, q) in enumerate(out):
        nxt = out[i + 1][0] if i + 1 < len(out) else b
        b = min(b, nxt) if nxt > a else b
        if nxt - b < 0.25:
            b = nxt
        fixed.append((a, b, q))
    return fixed


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ------------------------------------------------------------------ export
def paper_texture() -> Image.Image:
    """Ivory dossier paper (grain + faint fibres); the chapter spine is drawn by Remotion."""
    rnd = random.Random(1412)
    base = Image.new("RGB", (BASE_W, BASE_H), IVORY)
    noise = Image.effect_noise((BASE_W // 2, BASE_H // 2), 9).resize((BASE_W, BASE_H), Image.BICUBIC)
    base = Image.blend(base, ImageOps.colorize(noise, (230, 224, 212), (250, 246, 238)), 0.35)
    d = ImageDraw.Draw(base)
    for _ in range(140):
        x, y = rnd.randrange(BASE_W), rnd.randrange(BASE_H)
        ln, ang = rnd.randrange(20, 70), rnd.random() * math.pi
        d.line((x, y, x + ln * math.cos(ang), y + ln * math.sin(ang)), fill=(226, 219, 205), width=1)
    return base


def link(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and os.path.samefile(src, dst):
        return
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError as exc:
        if exc.errno != errno.EXDEV:
            raise
        # A collaborator may keep the public directory on another volume.
        shutil.copy2(src, dst)


def export(shots: list[Shot], content_end: float) -> Path:
    public = REMOTION / "public"
    used = sorted({s.ref for s in shots if s.kind == "F"})
    for ref in used:
        link(ROOT / ref, public / ref)
    # Drop stale footage links so the bundle copies only what the film uses.
    for p in (public / "assets").rglob("*.mp4"):
        if str(p.relative_to(public)) not in used:
            p.unlink()
    link(FEENBERG_PHOTO, public / "feenberg.jpg")
    if not (public / "paper.png").exists():
        paper_texture().save(public / "paper.png", optimize=True)
    # Lightweight public dir for graphic stills (tools/still.sh): no footage to copy.
    for name in ("paper.png", "feenberg.jpg"):
        link(public / name, REMOTION / "public_gfx" / name)
    tl = load_timeline()
    cues = build_subtitle_cues()
    DELIVER.mkdir(parents=True, exist_ok=True)
    (DELIVER / "PhuDe_V13.srt").write_text(
        "\n".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{chr(10).join(wrap(SUB_FACE, q, SUB_MAX_W))}\n"
                  for i, (a, b, q) in enumerate(cues, 1)), encoding="utf-8")
    data = {
        "fps": FPS,
        "width": BASE_W,
        "height": BASE_H,
        "durationInFrames": round(content_end * FPS),
        "transitionFrames": TRANS_F,
        "chapters": [{"num": i + 1, "name": n, "question": q} for i, (n, q) in enumerate(CHAPTER_META)],
        "shots": [{
            "id": f"{s.scene}_{s.index:02d}", "chapter": s.chapter, "scene": s.scene, "kind": s.kind, "ref": s.ref,
            "from": round(s.start * FPS), "frames": s.frames, "tail": s.tail, "srcStart": s.src_start,
            "tag": s.tag, "ai": s.kind == "F" and s.ref.startswith(AI_PREFIXES),
        } for s in shots],
        "words": [{"t": round(w["t"], 3), "w": w["w"]} for w in all_words(tl)],
        "subtitles": [{"from": round(a * FPS), "to": round(b * FPS), "lines": wrap(SUB_FACE, q, SUB_MAX_W)}
                      for a, b, q in cues],
    }
    out = REMOTION / "src/data/film.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False))
    print(f"export: {len(shots)} shots, {len(used)} clips, {len(cues)} cues → {out}")
    return out


# ----------------------------------------------------------------- picture
def picture_path(res: int) -> Path:
    return OUT / f"PICTURE_V13_CONTENT_{PROFILES[res]['suffix']}.mp4"


def render_picture(res: int, concurrency: int, frames: str | None = None) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    prof = PROFILES[res]
    out = picture_path(res) if not frames else OUT / f"PICTURE_V13_TEST_{prof['suffix']}_{frames.replace('-', '_')}.mp4"
    cmd = ["npx", "remotion", "render", "Film", str(out), "--codec=h264", "--crf=10", "--x264-preset=slow",
           f"--scale={prof['scale']}", "--muted", f"--concurrency={concurrency}", "--color-space=bt709", "--log=warn"]
    if frames:
        cmd.append(f"--frames={frames}")
    env = node_env()
    print("render:", " ".join(cmd[3:]), flush=True)
    res = subprocess.run(cmd, cwd=REMOTION, env=env)
    if res.returncode:
        raise RuntimeError("remotion render failed")
    return out


# --------------------------------------------------------------------- mix
def render_mix(content_end: float) -> Path:
    out = OUT / "MIX_V13_CONTENT_48K.wav"
    key = OUT / "MIX_V13_CONTENT_48K.key"
    stamp = f"{sha256(VOICE)}|{content_end:.4f}"
    if out.exists() and key.exists() and key.read_text() == stamp:
        return out
    score_len = media_duration(SCORE)
    fade_st = content_end - 3.0
    if score_len >= content_end:
        music = f"[1:a]aresample=48000,atrim=0:{content_end:.3f}"
    else:
        # Film outgrows the single score track: append the score again from 60 s (skips the intro)
        # with a 6 s equal-power crossfade instead of time-stretching the music.
        music = (f"[1:a]aresample=48000,asplit=2[sa][sb];[sb]atrim=start=60,asetpts=PTS-STARTPTS[sb2];"
                 f"[sa][sb2]acrossfade=d=6:c1=qsin:c2=qsin,atrim=0:{content_end:.3f}")
    graph = (
        f"[0:a]aresample=48000,highpass=f=70,acompressor=threshold=0.15:ratio=2:attack=15:release=160,"
        f"apad=whole_dur={content_end:.3f},atrim=0:{content_end:.3f},asplit=2[voice][key];"
        f"{music},volume=0.20,"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_st:.3f}:d=3.0[music];"
        f"[music][key]sidechaincompress=threshold=0.012:ratio=5:attack=110:release=600[ducked];"
        f"[voice][ducked]amix=inputs=2:normalize=0,alimiter=limit=0.85,loudnorm=I=-16:TP=-2:LRA=9[m]"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    run([FFMPEG, "-v", "error", "-y", "-i", str(VOICE), "-i", str(SCORE), "-filter_complex", graph, "-map", "[m]",
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(out)])
    key.write_text(stamp)
    return out


# ------------------------------------------------------------------- final
def render_final(res: int, mix: Path, content_end: float) -> Path:
    """YouTube master: H.264 High, closed GOP of 15 (half the frame rate), CRF 16 slow, AAC-LC 320k."""
    prof = PROFILES[res]
    picture = picture_path(res)
    if sha256(CREDIT) != CREDIT_SHA:
        raise RuntimeError("Credit V4 checksum mismatch — refusing to use it")
    offset = content_end - CREDIT_XFADE
    total = offset + CREDIT_DURATION
    graph = (
        f"[0:v]trim=duration={content_end:.4f},setpts=PTS-STARTPTS,fps={FPS},setsar=1,format=yuv420p,settb=AVTB[cv];"
        f"[2:v]trim=duration={CREDIT_DURATION},setpts=PTS-STARTPTS,fps={FPS},scale={prof['w']}:{prof['h']}:flags=lanczos,setsar=1,"
        f"format=yuv420p,settb=AVTB[kv];"
        f"[cv][kv]xfade=transition=fade:duration={CREDIT_XFADE}:offset={offset:.4f},trim=duration={total:.4f},format=yuv420p[v];"
        f"[1:a]aresample=48000,atrim=0:{content_end:.4f},asetpts=PTS-STARTPTS[ca];"
        f"[2:a]aresample=48000,atrim=0:{CREDIT_DURATION},asetpts=PTS-STARTPTS[ka];"
        f"[ca][ka]acrossfade=d={CREDIT_XFADE}:c1=qsin:c2=qsin[a]"
    )
    tmp = OUT / f"FINAL_V13_{prof['suffix']}.mp4"
    run([FFMPEG, "-v", "error", "-y", "-i", str(picture), "-i", str(mix), "-i", str(CREDIT),
         "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-t", f"{total:.4f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level:v", prof["level"],
         "-pix_fmt", "yuv420p", "-g", "15", "-keyint_min", "15", "-sc_threshold", "0", "-bf", "2",
         "-x264-params", "open-gop=0", *BT709,
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(tmp)])
    DELIVER.mkdir(parents=True, exist_ok=True)
    final = DELIVER / f"{FINAL_NAME}_{prof['suffix']}.mp4"
    if final.exists():
        final.unlink()
    os.replace(tmp, final)
    return final


# -------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["plan", "export", "picture", "mix", "final", "all"])
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--res", type=int, choices=sorted(PROFILES), default=1080)
    ap.add_argument("--frames", default=None, help="test render range, e.g. 0-299")
    args = ap.parse_args()
    shots, content_end = build_plan()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "plan.json").write_text(json.dumps([asdict(s) for s in shots], ensure_ascii=False, indent=1))
    if args.step == "plan":
        for s in shots:
            print(f"{s.start:8.2f} {s.frames / FPS:6.2f} {s.scene} {s.kind} {s.ref}")
        g = sum(s.frames for s in shots if s.kind == "F") / FPS
        print(f"shots={len(shots)} content={content_end:.2f}s footage={g:.0f}s ({g / content_end:.0%})")
    if args.step in ("export", "all"):
        export(shots, content_end)
    if args.step in ("picture", "all"):
        render_picture(args.res, args.concurrency, args.frames)
    if args.step in ("mix", "all"):
        render_mix(content_end)
    if args.step in ("final", "all"):
        out = render_final(args.res, OUT / "MIX_V13_CONTENT_48K.wav", content_end)
        print("final:", out)


if __name__ == "__main__":
    sys.exit(main())
