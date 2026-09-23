#!/opt/homebrew/bin/python3.13
"""Semantic-first visual plan for the V11 Feenberg documentary.

V11 keeps the approved Vale narration and replaces the weak V10 picture edit.
Every scene is tied to the argument already recorded in the storyboard.  Real
footage comes only from the dedicated V11 Mixkit directory; the end-credit
footage directory is rejected by prefix, not merely by a short blacklist.
"""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


V9 = "assets/flow_v9_raw"
F = "assets/flow_selected"
N = "assets/flow_v8_namthanguit"
O = "assets/flow_v8_odoo"
R = "assets/v11_real/mixkit"
G = "assets/v11_graphics_r5"
C = "assets/v11_source_cards_r6"
P = "assets/v11_sources"
E = "assets/editorial_selects"


def a(root: str, name: str) -> str:
    return f"{root}/{name}"


SCENE_ASSETS: dict[str, list[str]] = {
    "S001": [a(F, "S002_phone_tap_1080p_v2.mp4")],
    "S002": [a(N, "S002_phone_tap_alt_1080p.mp4")],
    "S003": [a(G, "MG01_open_black_box.mp4")],
    "S004": [a(O, "S034_multiple_options_1080p.mp4")],
    "S005": [a(V9, "V9_004.mp4"), a(R, "mixkit_4547_1080.mp4"), a(F, "S063_flow_1080p.mp4"), a(R, "mixkit_914_1080.mp4"), a(R, "mixkit_4169_1080.mp4"), a(R, "mixkit_918_1080.mp4")],
    "S006": [a(V9, "V9_006.mp4"), a(G, "MG27_hypothetical_boundary.mp4")],
    "S007": [a(G, "MG02_three_layers.mp4")],
    "S008": [a(R, "mixkit_41165_1080.mp4")],
    "S009": [a(F, "S009_flow_1080p.mp4")],
    "S010": [a(R, "mixkit_42666_1080.mp4"), a(R, "mixkit_42656_1080.mp4"), a(R, "mixkit_914_1080.mp4")],
    "S011": [a(G, "MG02_three_layers.mp4")],
    "S012": [a(G, "MG03_access_participation.mp4")],
    "S013": [a(V9, "V9_014.mp4"), a(R, "mixkit_41180_1080.mp4"), a(V9, "V9_006.mp4"), a(G, "MG44_correct_spec_wrong_goal.mp4")],
    "S014": [a(F, "S051_flow_1080p.mp4"), a(R, "mixkit_42648_1080.mp4"), a(R, "mixkit_42664_1080.mp4"), a(G, "MG42_efficiency_for_whom.mp4")],
    "S015": [a(F, "S015_neutral_tool_1080p.mp4")],
    "S016": [a(C, "S016_source_card.png")],
    "S017": [a(R, "mixkit_29991_1080.mp4"), a(G, "MG04_matrix_intro.mp4")],
    "S018": [a(G, "MG05_matrix_axes.mp4")],
    "S019": [a(G, "MG06_matrix_instrumentalism.mp4")],
    "S020": [a(G, "MG07_matrix_determinism.mp4")],
    "S021": [a(V9, "V9_008.mp4")],
    "S022": [a(G, "MG08_matrix_substantivism.mp4")],
    "S023": [a(P, "andrew_feenberg_card.png"), a(G, "MG09_matrix_critical_theory.mp4"), a(F, "S050_flow_1080p.mp4"), a(R, "mixkit_4169_1080.mp4")],
    "S024": [a(G, "MG09_matrix_critical_theory.mp4")],
    "S025": [a(C, "S025_source_card.png")],
    "S026": [a(V9, "V9_015.mp4")],
    "S027": [a(G, "MG35_red_thread_bridge.mp4")],
    "S028": [a(V9, "V9_008.mp4")],
    "S029": [a(G, "MG43_action_frame.mp4")],
    "S030": [a(V9, "V9_014.mp4")],
    "S031": [a(V9, "V9_069.mp4")],
    "S032": [a(G, "MG10_meta_choice.mp4")],
    "S033": [a(R, "mixkit_3257_1080.mp4"), a(V9, "V9_029.mp4"), a(R, "mixkit_4809_1080.mp4")],
    "S034": [a(G, "MG11_relative_underdetermination.mp4")],
    "S035": [a(R, "mixkit_29993_1080.mp4"), a(V9, "V9_017.mp4"), a(V9, "V9_007.mp4")],
    "S036": [a(C, "S036_source_card.png")],
    "S037": [a(V9, "V9_017.mp4"), a(G, "MG29_ambivalent_paths.mp4"), a(V9, "V9_007.mp4"), a(R, "mixkit_29991_1080.mp4")],
    "S038": [a(G, "MG32_design_genealogy.mp4"), a(R, "mixkit_50598_1080.mp4"), a(R, "mixkit_50600_1080.mp4"), a(R, "mixkit_785_1080.mp4")],
    "S039": [a(G, "MG12_technical_code.mp4")],
    "S040": [a(F, "S040_technical_code_materials_1080p.mp4")],
    "S041": [a(G, "MG12_technical_code.mp4"), a(F, "S040_technical_code_materials_1080p.mp4"), a(N, "S040_constraints_alt_1080p.mp4")],
    "S042": [a(C, "S042_source_card.png")],
    "S043": [a(F, "S043_boiler_reconstruction_1080p.mp4")],
    "S044": [a(O, "S043_boiler_reconstruction_1080p.mp4")],
    "S045": [a(V9, "V9_021.mp4"), a(V9, "V9_023.mp4")],
    "S046": [a(V9, "V9_024.mp4")],
    "S047": [a(V9, "V9_019.mp4")],
    "S048": [a(C, "S048_source_card.png")],
    "S049": [a(R, "mixkit_921_1080.mp4")],
    "S050": [a(F, "S050_flow_1080p.mp4")],
    "S051": [a(R, "mixkit_8739_1080.mp4"), a(G, "MG38_excluded_interest.mp4")],
    "S052": [a(O, "S073_adaptive_computer_1080p.mp4"), a(V9, "V9_010.mp4"), a(R, "mixkit_29993_1080.mp4"), a(G, "MG20_value_to_parameter.mp4"), a(G, "MG41_value_specification.mp4")],
    "S053": [a(G, "MG13_democratization_title.mp4")],
    "S054": [a(G, "MG28_democracy_not_access.mp4"), a(G, "MG13_democratization_title.mp4")],
    "S055": [a(R, "mixkit_4401_1080.mp4"), a(G, "MG34_access_at_scale.mp4")],
    "S056": [a(C, "S056_source_card.png")],
    "S057": [a(V9, "V9_027.mp4"), a(V9, "V9_004.mp4"), a(G, "MG31_participation_chain.mp4")],
    "S058": [a(G, "MG14_democratic_rationalization.mp4"), a(N, "S034_scheduling_options_alt_1080p.mp4")],
    "S059": [a(G, "MG37_effective_window.mp4"), a(G, "MG15_effective_feedback.mp4")],
    "S060": [a(V9, "V9_036.mp4"), a(R, "mixkit_42666_1080.mp4")],
    "S061": [a(G, "MG15_effective_feedback.mp4")],
    "S062": [a(R, "mixkit_4648_1080.mp4")],
    "S063": [a(R, "mixkit_4809_1080.mp4"), a(V9, "V9_030.mp4"), a(F, "S086_flow_1080p.mp4")],
    "S064": [a(C, "S064_source_card.png")],
    "S065": [a(O, "S065_network_users_1080p.mp4"), a(R, "mixkit_242_1080.mp4")],
    "S066": [a(R, "mixkit_41165_1080.mp4")],
    "S067": [a(R, "mixkit_4916_1080.mp4"), a(R, "mixkit_4872_1080.mp4")],
    "S068": [a(G, "MG16_network_transformation.mp4")],
    "S069": [a(R, "mixkit_4907_1080.mp4")],
    "S070": [a(C, "S070_source_card.png")],
    "S071": [a(V9, "V9_037.mp4"), a(R, "mixkit_308_1080.mp4")],
    "S072": [a(R, "mixkit_308_1080.mp4"), a(R, "mixkit_4907_1080.mp4")],
    "S073": [a(R, "mixkit_1781_1080.mp4"), a(R, "mixkit_41180_1080.mp4")],
    "S074": [a(G, "MG30_collective_priority.mp4")],
    "S075": [a(G, "MG17_evidence_boundary.mp4")],
    "S076": [a(C, "S076_source_card.png")],
    "S077": [a(C, "S076_source_card.png"), a(V9, "V9_034.mp4"), a(V9, "V9_033.mp4")],
    "S078": [a(G, "MG18_three_analytic_layers.mp4"), a(N, "S065_network_users_alt_1080p.mp4"), a(N, "S073_adaptive_computer_alt_1080p.mp4"), a(V9, "V9_038.mp4"), a(V9, "V9_035.mp4"), a(V9, "V9_012.mp4")],
    "S079": [a(G, "MG17_evidence_boundary.mp4"), a(G, "MG45_feedback_path.mp4"), a(G, "MG39_cautious_potential.mp4"), a(R, "mixkit_4916_1080.mp4"), a(G, "MG40_stakeholder_map.mp4")],
    "S080": [a(N, "S002_phone_tap_alt_1080p.mp4"), a(V9, "V9_002.mp4"), a(G, "MG19_five_questions.mp4")],
    "S081": [a(G, "MG19_five_questions.mp4"), a(R, "mixkit_3257_1080.mp4"), a(R, "mixkit_42656_1080.mp4")],
    "S082": [a(G, "MG20_value_to_parameter.mp4")],
    "S083": [a(G, "MG33_parameter_trace.mp4"), a(V9, "V9_068.mp4"), a(R, "mixkit_50598_1080.mp4")],
    "S084": [a(V9, "V9_005.mp4"), a(V9, "V9_018.mp4"), a(G, "MG38_excluded_interest.mp4")],
    "S085": [a(G, "MG40_stakeholder_map.mp4"), a(R, "mixkit_918_1080.mp4"), a(R, "mixkit_8739_1080.mp4")],
    "S086": [a(G, "MG31_participation_chain.mp4"), a(R, "mixkit_4648_1080.mp4"), a(R, "mixkit_4872_1080.mp4")],
    "S087": [a(G, "MG21_traceable_feedback.mp4"), a(V9, "V9_029.mp4")],
    "S088": [a(G, "MG21_traceable_feedback.mp4"), a(R, "mixkit_4547_1080.mp4")],
    "S089": [a(G, "MG22_five_conditions.mp4")],
    "S090": [a(G, "MG36_complementary_knowledge.mp4"), a(R, "mixkit_30005_1080.mp4")],
    "S091": [a(G, "MG23_central_question.mp4")],
    "S092": [a(G, "MG24_conclusion_layers.mp4")],
    "S093": [a(G, "MG25_open_paths.mp4")],
    "S094": [a(G, "MG26_methodological_motif.mp4")],
    "S095": [a(V9, "V9_066.mp4"), a(N, "S099_closing_kiosk_alt_1080p.mp4")],
}


ASSET_WINDOWS: dict[str, tuple[float, float]] = {
    a(V9, "V9_002.mp4"): (0.4, 8.0),
    a(V9, "V9_004.mp4"): (0.0, 9.6),
    a(V9, "V9_005.mp4"): (0.8, 9.6),
    a(V9, "V9_006.mp4"): (0.0, 9.7),
    a(V9, "V9_007.mp4"): (0.2, 9.6),
    a(V9, "V9_008.mp4"): (0.2, 9.7),
    a(V9, "V9_010.mp4"): (1.6, 8.6),
    a(V9, "V9_012.mp4"): (0.0, 9.7),
    a(V9, "V9_014.mp4"): (0.0, 9.4),
    a(V9, "V9_015.mp4"): (0.0, 9.3),
    a(V9, "V9_017.mp4"): (0.0, 8.9),
    a(V9, "V9_018.mp4"): (0.0, 7.9),
    a(V9, "V9_019.mp4"): (0.0, 9.8),
    a(V9, "V9_021.mp4"): (0.0, 9.7),
    a(V9, "V9_023.mp4"): (0.0, 9.7),
    a(V9, "V9_024.mp4"): (0.0, 9.6),
    a(V9, "V9_027.mp4"): (0.0, 6.0),
    a(V9, "V9_029.mp4"): (0.0, 9.6),
    a(V9, "V9_030.mp4"): (0.0, 9.7),
    a(V9, "V9_066.mp4"): (0.0, 8.0),
    a(V9, "V9_068.mp4"): (1.8, 7.8),
    a(V9, "V9_069.mp4"): (0.5, 6.5),
}


BANNED_ASSETS = {
    "assets/editorial_selects/S014_affected_users_1080p.mp4",
    "assets/flow_selected/S031_flow_1080p.mp4",
    "assets/flow_v8_odoo/S031_meta_choice_ramp_1080p.mp4",
    "assets/flow_selected/S063_codesign_kiosk_1080p.mp4",
    "assets/flow_selected/S071_flow_1080p.mp4",
    "assets/flow_selected/S073_flow_1080p.mp4",
    "assets/flow_selected/S013_schedule_exclusion_1080p.mp4",
    "assets/flow_selected/S090_feedback_redesign_retest_1080p.mp4",
    # V11 motion audit: these clips carry a visible CGI/wax look or an
    # implausible empty-screen/object animation.  Keep the full paths here so
    # no later plan edit can silently reintroduce them.
    "assets/flow_selected/S024_flow_1080p.mp4",
    "assets/flow_selected/S039_flow_1080p.mp4",
    "assets/flow_selected/S059_flow_1080p.mp4",
    "assets/flow_selected/S078_flow_1080p.mp4",
    "assets/flow_selected/S091_flow_1080p.mp4",
    "assets/flow_selected/S093_flow_1080p.mp4",
    # V11 full-motion / 2-fps picture audit.  These four sources contain a
    # discontinuous drawing/morph, pseudo-text, or an empty screen that fails
    # to support the narration.  Reject the sources, not merely their trims.
    "assets/flow_selected/S075_priority_cards_1080p.mp4",
    "assets/flow_selected/S088_flow_1080p.mp4",
    "assets/flow_selected/S095_flow_1080p.mp4",
    "assets/flow_selected/ALS_1995_new_1080p.mp4",
    # Manual picture-test QA: the phone is visibly switched off throughout
    # the usable window.  A blank screen cannot support either the clinic
    # specification argument in S013 or the feedback/power argument in S079.
    "assets/v11_real/mixkit/mixkit_41638_1080.mp4",
}

FORBIDDEN_PREFIXES = ("assets/credit_tphcm/",)
MOTION_TAIL_SECONDS = 8 / 30

SOURCE_SCENES = {"S016", "S025", "S036", "S042", "S048", "S056", "S064", "S070", "S076", "S077"}

TITLE_TEXT = {
    "S005": "DÂN CHỦ HÓA THIẾT KẾ\nVÀ QUẢN TRỊ CÔNG NGHỆ",
    "S015": "BỐN CÁCH NHÌN VỀ CÔNG NGHỆ",
    "S039": "MÃ KỸ THUẬT · TECHNICAL CODE",
    "S053": "DÂN CHỦ HÓA CÔNG NGHỆ LÀ GÌ?",
    "S064": "CASE · TỪ PHÂN PHỐI DỮ LIỆU ĐẾN TIẾNG NÓI TẬP THỂ",
    "S080": "VẬN DỤNG PHƯƠNG PHÁP LUẬN",
    "S082": "1 · AI ĐỊNH NGHĨA VẤN ĐỀ?",
    "S083": "2 · GIÁ TRỊ NÀO ĐÃ THÀNH THAM SỐ?",
    "S084": "3 · AI CHỊU TÁC ĐỘNG NHƯNG VẮNG MẶT?",
    "S085": "4 · SỰ THAM GIA CÓ QUYỀN GÌ?",
    "S086": "5 · PHẢN HỒI CÓ ĐI ĐẾN TÁI THIẾT KẾ?",
    "S091": "TRỞ LẠI CÂU HỎI TRUNG TÂM",
    "S095": "CÙNG ĐỊNH HÌNH KHUNG KỸ THUẬT",
}


def category(relative: str) -> str:
    if relative.startswith(G + "/"):
        return "deterministic_motion_graphic"
    if relative.startswith(C + "/"):
        return "instructor_source_card"
    if relative.startswith(P + "/"):
        return "verified_real_photo"
    if relative.startswith(R + "/"):
        return "real_footage"
    return "veo_flow_illustration"


def seconds(value: str) -> float:
    h, m, s = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def duration(path: Path) -> float:
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        text=True,
    )
    return float(json.loads(raw)["format"]["duration"])


def validate(scene_ids: list[str], project_dir: Path, storyboard: Path | None = None) -> dict[str, object]:
    expected = set(scene_ids)
    actual = set(SCENE_ASSETS)
    if expected != actual:
        raise ValueError(f"V11 plan mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")

    counts: Counter[str] = Counter()
    category_seconds: defaultdict[str, float] = defaultdict(float)
    semantic_links: dict[str, str] = {}
    row_by_scene: dict[str, dict[str, str]] = {}
    if storyboard:
        with storyboard.open(encoding="utf-8-sig", newline="") as handle:
            row_by_scene = {r["SCENE_ID"]: r for r in csv.DictReader(handle) if r["SCENE_ID"].startswith("S")}

    # A repeated motion asset is only acceptable when its approved source
    # window can be partitioned into disjoint forward-play ranges.  This is a
    # stronger check than a reuse counter: two placements trimmed from the
    # same seconds are still visually the same shot and violate V11.
    motion_requirements: defaultdict[str, list[tuple[str, float]]] = defaultdict(list)

    for scene_id, assets in SCENE_ASSETS.items():
        if not assets:
            raise ValueError(f"No asset for {scene_id}")
        if row_by_scene:
            link = row_by_scene[scene_id].get("VISUAL_ARGUMENT_LINK", "").strip()
            if not link:
                raise ValueError(f"Missing visual_argument_link for {scene_id}")
            semantic_links[scene_id] = link
            scene_duration = float(row_by_scene[scene_id]["DURATION"])
            per_asset = scene_duration / len(assets)
        else:
            per_asset = 0.0
        for relative in assets:
            if relative in BANNED_ASSETS or relative.startswith(FORBIDDEN_PREFIXES):
                raise ValueError(f"Forbidden asset referenced: {scene_id}: {relative}")
            source = project_dir / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            counts[relative] += 1
            category_seconds[category(relative)] += per_asset
            if source.suffix.lower() in {".mp4", ".mov", ".m4v"}:
                raw = subprocess.check_output(
                    [
                        "ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "json", str(source),
                    ],
                    text=True,
                )
                streams = json.loads(raw).get("streams", [])
                if not streams:
                    raise ValueError(f"No video stream: {scene_id}: {relative}")
                width = int(streams[0].get("width", 0) or 0)
                height = int(streams[0].get("height", 0) or 0)
                aspect = width / height if height else 0.0
                if width < 1920 or height < 1080 or abs(aspect - 16 / 9) > 0.02:
                    raise ValueError(
                        f"V11 source is not native Full-HD 16:9: {scene_id} {relative}: "
                        f"{width}x{height}, aspect={aspect:.4f}"
                    )
                approved = ASSET_WINDOWS.get(relative, (0.0, duration(source)))
                available = approved[1] - approved[0]
                if available + 0.04 < per_asset and category(relative) in {"real_footage", "veo_flow_illustration"}:
                    raise ValueError(
                        f"Motion window too short: {scene_id} {relative}: need {per_asset:.3f}s, have {available:.3f}s"
                    )
                motion_requirements[relative].append((scene_id, per_asset + MOTION_TAIL_SECONDS))

    overused = {path: count for path, count in counts.items() if count > 2}
    if overused:
        raise ValueError(f"Assets reused more than twice: {overused}")

    overlap_failures: dict[str, dict[str, object]] = {}
    for relative, requirements in motion_requirements.items():
        source = project_dir / relative
        approved_start, approved_end = ASSET_WINDOWS.get(relative, (0.0, duration(source)))
        available = max(0.0, min(approved_end, duration(source)) - max(0.0, approved_start))
        needed = sum(seconds for _, seconds in requirements)
        if len(requirements) > 1 and needed > available + 0.04:
            overlap_failures[relative] = {
                "placements": [scene for scene, _ in requirements],
                "needed_seconds_in_disjoint_windows": round(needed, 3),
                "approved_window_seconds": round(available, 3),
            }
    if overlap_failures:
        raise ValueError(
            "Repeated motion assets do not have disjoint approved windows: "
            + json.dumps(overlap_failures, ensure_ascii=False, sort_keys=True)
        )

    dynamic = category_seconds["real_footage"] + category_seconds["veo_flow_illustration"]
    real_share = category_seconds["real_footage"] / dynamic if dynamic else 0.0
    ai_share = category_seconds["veo_flow_illustration"] / dynamic if dynamic else 0.0
    return {
        "scene_count": len(scene_ids),
        "placement_count": sum(counts.values()),
        "unique_assets": len(counts),
        "max_reuse": max(counts.values(), default=0),
        "category_seconds": dict(sorted(category_seconds.items())),
        "dynamic_real_share": real_share,
        "dynamic_ai_share": ai_share,
        "semantic_links": semantic_links,
        "asset_reuse": dict(sorted(counts.items())),
        "disjoint_motion_windows": True,
    }
