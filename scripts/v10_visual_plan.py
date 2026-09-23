#!/usr/bin/env python3
"""Editorially locked V10 visual plan.

The plan deliberately keeps academic evidence, deterministic graphics,
real footage and AI illustration as separate asset classes.  No banned V8
asset is referenced here.  A file may be placed at most twice and every human
clip is played forward inside a manually approved trim window.
"""

from __future__ import annotations

from pathlib import Path


V9 = "assets/flow_v9_raw"
F = "assets/flow_selected"
N = "assets/flow_v8_namthanguit"
O = "assets/flow_v8_odoo"
R = "assets/credit_tphcm/raw"
MX = "assets/v10_selected/real_mixkit/staging"
G = "assets/v10_graphics"
C = "assets/v10_source_cards"


SCENE_ASSETS: dict[str, list[str]] = {
    "S001": [f"{V9}/V9_002.mp4"],
    "S002": [f"{V9}/V9_002.mp4"],
    "S003": [f"{G}/MG01_open_black_box.mp4"],
    "S004": [f"{V9}/V9_004.mp4"],
    "S005": [f"{MX}/mixkit_4169_1080.mp4", f"{MX}/mixkit_918_1080.mp4", f"{R}/pexels_aerial_skyline_32427394.mp4"],
    "S006": [f"{V9}/V9_006.mp4"],
    "S007": [f"{G}/MG02_three_layers.mp4"],
    "S008": [f"{F}/S095_flow_1080p.mp4"],
    "S009": [f"{F}/S009_flow_1080p.mp4"],
    "S010": [f"{F}/S050_flow_1080p.mp4", f"{N}/S034_scheduling_options_alt_1080p.mp4"],
    "S011": [f"{G}/MG02_three_layers.mp4"],
    "S012": [f"{G}/MG03_access_participation.mp4"],
    "S013": [f"{F}/S051_flow_1080p.mp4", f"{V9}/V9_014.mp4"],
    "S014": [f"{R}/incoming/12602357_3840_2160_25fps.mp4", f"{R}/incoming/14305269_3840_2160_30fps.mp4", f"{MX}/mixkit_914_1080.mp4"],
    "S015": [f"{V9}/V9_007.mp4"],
    "S016": [f"{C}/S016_source_card.png"],
    "S017": [f"{F}/S015_neutral_tool_1080p.mp4", f"{G}/MG04_matrix_intro.mp4"],
    "S018": [f"{G}/MG05_matrix_axes.mp4"],
    "S019": [f"{G}/MG06_matrix_instrumentalism.mp4"],
    "S020": [f"{G}/MG07_matrix_determinism.mp4", f"{R}/incoming/14194592_3840_2160_30fps.mp4"],
    "S021": [f"{R}/incoming/12984242_3840_2160_30fps.mp4"],
    "S022": [f"{G}/MG08_matrix_substantivism.mp4"],
    "S023": [f"{G}/MG09_matrix_critical_theory.mp4", f"{F}/S063_flow_1080p.mp4"],
    "S024": [f"{G}/MG09_matrix_critical_theory.mp4"],
    "S025": [f"{C}/S025_source_card.png"],
    "S026": [f"{V9}/V9_015.mp4"],
    "S027": [f"{R}/pexels_city_hall_39357829.mp4"],
    "S028": [f"{R}/pexels_busy_street_37886978.mp4"],
    "S029": [f"{R}/pexels_motorcyclist_19888308.mp4", f"{R}/pexels_ben_thanh_29185453.mp4"],
    "S030": [f"{G}/MG10_meta_choice.mp4"],
    "S031": [f"{V9}/V9_014.mp4"],
    "S032": [f"{V9}/V9_015.mp4", f"{G}/MG10_meta_choice.mp4"],
    "S033": [f"{V9}/V9_017.mp4", f"{V9}/V9_029.mp4"],
    "S034": [f"{G}/MG11_relative_underdetermination.mp4"],
    "S035": [f"{V9}/V9_029.mp4", f"{N}/S040_constraints_alt_1080p.mp4"],
    "S036": [f"{C}/S036_source_card.png"],
    "S037": [f"{V9}/V9_030.mp4", f"{V9}/V9_005.mp4"],
    "S038": [f"{G}/MG11_relative_underdetermination.mp4", f"{MX}/mixkit_918_1080.mp4", f"{R}/pexels_sai_gon_skyline_18343662.mp4", f"{R}/pexels_night_traffic_29185408.mp4"],
    "S039": [f"{G}/MG12_technical_code.mp4"],
    "S040": [f"{G}/MG12_technical_code.mp4"],
    "S041": [f"{V9}/V9_018.mp4", f"{V9}/V9_005.mp4"],
    "S042": [f"{C}/S042_source_card.png"],
    "S043": [f"{V9}/V9_019.mp4"],
    "S044": [f"{N}/S043_boiler_alt_1080p.mp4"],
    "S045": [f"{V9}/V9_021.mp4", f"{V9}/V9_023.mp4"],
    "S046": [f"{V9}/V9_024.mp4"],
    "S047": [f"{N}/S043_boiler_alt_1080p.mp4"],
    "S048": [f"{C}/S048_source_card.png"],
    "S049": [f"{V9}/V9_024.mp4"],
    "S050": [f"{F}/S050_flow_1080p.mp4"],
    "S051": [f"{F}/S051_flow_1080p.mp4", f"{R}/pexels_night_skyline_31111952.mp4"],
    "S052": [f"{V9}/V9_010.mp4", f"{V9}/V9_030.mp4", f"{F}/S063_codesign_kiosk_1080p.mp4", f"{N}/S062_codesign_kiosk_alt_1080p.mp4"],
    "S053": [f"{G}/MG13_democratization_title.mp4"],
    "S054": [f"{F}/S010_flow_1080p.mp4", f"{G}/MG13_democratization_title.mp4"],
    "S055": [f"{V9}/V9_006.mp4", f"{G}/MG03_access_participation.mp4", f"{MX}/mixkit_4169_1080.mp4"],
    "S056": [f"{C}/S056_source_card.png"],
    "S057": [f"{V9}/V9_004.mp4", f"{F}/S063_codesign_kiosk_1080p.mp4"],
    "S058": [f"{G}/MG14_democratic_rationalization.mp4", f"{R}/pexels_sai_gon_skyline_18343662.mp4"],
    "S059": [f"{F}/S010_flow_1080p.mp4", f"{V9}/V9_010.mp4"],
    "S060": [f"{F}/S063_flow_1080p.mp4", f"{N}/S062_codesign_kiosk_alt_1080p.mp4"],
    "S061": [f"{G}/MG15_effective_feedback.mp4"],
    "S062": [f"{V9}/V9_017.mp4"],
    "S063": [f"{N}/S040_constraints_alt_1080p.mp4", f"{F}/S088_flow_1080p.mp4", f"{F}/S086_flow_1080p.mp4"],
    "S064": [f"{C}/S064_source_card.png"],
    "S065": [f"{V9}/V9_035.mp4", f"{F}/S071_flow_1080p.mp4"],
    "S066": [f"{V9}/V9_034.mp4"],
    "S067": [f"{V9}/V9_033.mp4", f"{V9}/V9_036.mp4"],
    "S068": [f"{G}/MG16_network_transformation.mp4"],
    "S069": [f"{V9}/V9_036.mp4"],
    "S070": [f"{C}/S070_source_card.png"],
    "S071": [f"{V9}/V9_037.mp4", f"{V9}/V9_038.mp4"],
    "S072": [f"{F}/S073_flow_1080p.mp4", f"{F}/S071_flow_1080p.mp4"],
    "S073": [f"{V9}/V9_038.mp4", f"{V9}/V9_033.mp4"],
    "S074": [f"{F}/S075_priority_cards_1080p.mp4", f"{V9}/V9_035.mp4"],
    "S075": [f"{G}/MG17_evidence_boundary.mp4"],
    "S076": [f"{C}/S076_source_card.png"],
    "S077": [f"{G}/MG17_evidence_boundary.mp4", f"{V9}/V9_034.mp4", f"{F}/S073_flow_1080p.mp4"],
    "S078": [f"{G}/MG18_three_analytic_layers.mp4", f"{V9}/V9_037.mp4", f"{F}/S075_priority_cards_1080p.mp4", f"{R}/incoming/15300802_3840_2160_60fps.mp4", f"{R}/incoming/12205461_3840_2160_30fps.mp4", f"{R}/incoming/16602191_3840_2160_30fps.mp4"],
    "S079": [f"{R}/pexels_landmark_31111825.mp4", f"{R}/pexels_river_skyline_31975717.mp4", f"{R}/pexels_day_night_3963629.mp4", f"{R}/incoming/15980643_3840_2160_25fps.mp4"],
    "S080": [f"{F}/S095_flow_1080p.mp4", f"{N}/S034_scheduling_options_alt_1080p.mp4"],
    "S081": [f"{V9}/V9_007.mp4", f"{G}/MG19_five_questions.mp4"],
    "S082": [f"{G}/MG19_five_questions.mp4"],
    "S083": [f"{F}/S009_flow_1080p.mp4", f"{V9}/V9_068.mp4", f"{G}/MG20_value_to_parameter.mp4"],
    "S084": [f"{F}/S040_technical_code_materials_1080p.mp4", f"{G}/MG20_value_to_parameter.mp4"],
    "S085": [f"{R}/pexels_motorcyclist_19888308.mp4", f"{F}/S013_schedule_exclusion_1080p.mp4", f"{R}/motorbikers_cc0.jpg"],
    "S086": [f"{F}/S086_flow_1080p.mp4", f"{F}/S088_flow_1080p.mp4", f"{V9}/V9_027.mp4"],
    "S087": [f"{G}/MG21_traceable_feedback.mp4"],
    "S088": [f"{G}/MG21_traceable_feedback.mp4", f"{F}/S040_technical_code_materials_1080p.mp4"],
    "S089": [f"{G}/MG22_five_conditions.mp4"],
    "S090": [f"{G}/MG22_five_conditions.mp4", f"{F}/S090_feedback_redesign_retest_1080p.mp4", f"{MX}/mixkit_914_1080.mp4"],
    "S091": [f"{G}/MG23_central_question.mp4"],
    "S092": [f"{G}/MG24_conclusion_layers.mp4"],
    "S093": [f"{G}/MG25_open_paths.mp4"],
    "S094": [f"{G}/MG26_methodological_motif.mp4"],
    "S095": [f"{R}/sunset_publicdomain.jpg", f"{V9}/V9_066.mp4"],
}


# Windows are conservative portions established by manual motion review.
ASSET_WINDOWS: dict[str, tuple[float, float]] = {
    f"{V9}/V9_002.mp4": (0.4, 8.0),
    f"{V9}/V9_004.mp4": (0.0, 9.6),
    f"{V9}/V9_005.mp4": (0.8, 9.6),
    f"{V9}/V9_006.mp4": (0.0, 9.7),
    f"{V9}/V9_007.mp4": (0.2, 9.6),
    f"{V9}/V9_008.mp4": (0.2, 9.7),
    f"{V9}/V9_010.mp4": (1.6, 8.6),
    f"{V9}/V9_012.mp4": (0.0, 5.0),
    f"{V9}/V9_014.mp4": (0.0, 9.4),
    f"{V9}/V9_015.mp4": (0.0, 9.3),
    f"{V9}/V9_017.mp4": (0.0, 8.9),
    f"{V9}/V9_018.mp4": (0.0, 7.9),
    f"{V9}/V9_019.mp4": (0.0, 9.8),
    f"{V9}/V9_021.mp4": (0.0, 9.7),
    f"{V9}/V9_023.mp4": (0.0, 9.7),
    f"{V9}/V9_024.mp4": (0.0, 9.6),
    f"{V9}/V9_027.mp4": (0.0, 6.0),
    f"{V9}/V9_029.mp4": (0.0, 9.6),
    f"{V9}/V9_030.mp4": (0.0, 9.7),
    f"{V9}/V9_033.mp4": (0.8, 8.8),
    f"{V9}/V9_034.mp4": (0.6, 9.3),
    f"{V9}/V9_035.mp4": (0.3, 9.2),
    f"{V9}/V9_036.mp4": (0.4, 9.2),
    f"{V9}/V9_037.mp4": (0.5, 9.3),
    f"{V9}/V9_038.mp4": (0.5, 8.8),
    f"{V9}/V9_066.mp4": (0.0, 8.0),
    f"{V9}/V9_068.mp4": (1.8, 7.8),
    f"{V9}/V9_069.mp4": (0.5, 6.5),
}


BANNED_ASSETS = {
    "assets/editorial_selects/S014_affected_users_1080p.mp4",
    "assets/flow_selected/S031_flow_1080p.mp4",
    "assets/flow_v8_odoo/S031_meta_choice_ramp_1080p.mp4",
}

SOURCE_SCENES = {"S016", "S025", "S036", "S042", "S048", "S056", "S064", "S070", "S076"}
RECONSTRUCTION_SCENES = {f"S{i:03d}" for i in range(43, 48)} | {f"S{i:03d}" for i in range(65, 78)}
HYPOTHETICAL_SCENES = {f"S{i:03d}" for i in range(1, 15)} | {f"S{i:03d}" for i in range(80, 91)}

TITLE_TEXT = {
    "S001": "TÌNH HUỐNG GIẢ ĐỊNH · NHÓM 14",
    "S005": "DÂN CHỦ HÓA THIẾT KẾ\nVÀ QUẢN TRỊ CÔNG NGHỆ",
    "S015": "THUYẾT CÔNG CỤ",
    "S027": "LỰA CHỌN Ở CẤP KHUNG",
    "S031": "META-CHOICE · LỰA CHỌN Ở CẤP KHUNG",
    "S039": "MÃ KỸ THUẬT · TECHNICAL CODE",
    "S043": "CASE QUY CHUẨN AN TOÀN NỒI HƠI",
    "S053": "DÂN CHỦ HÓA CÔNG NGHỆ LÀ GÌ?",
    "S064": "CASE · MẠNG MÁY TÍNH VÀ NHÓM HỖ TRỢ ALS",
    "S080": "VẬN DỤNG PHƯƠNG PHÁP LUẬN",
    "S083": "1 · AI ĐỊNH NGHĨA VẤN ĐỀ?",
    "S084": "2 · GIÁ TRỊ NÀO ĐÃ THÀNH THAM SỐ?",
    "S085": "3 · AI CHỊU TÁC ĐỘNG NHƯNG VẮNG MẶT?",
    "S086": "4 · SỰ THAM GIA CÓ QUYỀN GÌ?",
    "S087": "5 · PHẢN HỒI CÓ ĐI ĐẾN TÁI THIẾT KẾ?",
    "S095": "CÙNG ĐỊNH HÌNH KHUNG KỸ THUẬT",
}


def category(relative: str) -> str:
    if relative.startswith(G + "/"):
        return "deterministic_motion_graphic"
    if relative.startswith(C + "/"):
        return "instructor_source_card"
    if relative.startswith((R + "/", MX + "/")):
        return "real_footage"
    return "veo_flow_illustration"


def validate(scene_ids: list[str], project_dir: Path) -> None:
    expected = set(scene_ids)
    actual = set(SCENE_ASSETS)
    if expected != actual:
        raise ValueError(f"V10 plan mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    counts: dict[str, int] = {}
    for scene_id, assets in SCENE_ASSETS.items():
        if not assets:
            raise ValueError(f"No asset for {scene_id}")
        for relative in assets:
            if relative in BANNED_ASSETS:
                raise ValueError(f"Banned asset referenced: {scene_id}: {relative}")
            if not (project_dir / relative).is_file():
                raise FileNotFoundError(project_dir / relative)
            counts[relative] = counts.get(relative, 0) + 1
    overused = {path: count for path, count in counts.items() if count > 2}
    if overused:
        raise ValueError(f"Assets reused more than twice: {overused}")
