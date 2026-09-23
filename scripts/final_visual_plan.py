#!/usr/bin/env python3
"""Locked visual edit plan for the Feenberg documentary.

This module contains no rendering code.  Keeping editorial choices separate
from FFmpeg orchestration makes it possible to audit which factual source,
generated illustration, or deterministic graphic is shown in every scene.
"""

from __future__ import annotations


P = "assets/flow/proof/raw"
F = "assets/flow_selected"
E = "assets/editorial_selects"
G = "assets/graphics"
C = "assets/source_pages/crops"
M = "assets/motion"
O = "assets/flow_v8_odoo"
N = "assets/flow_v8_namthanguit"


# One scene may contain several shots.  The renderer divides the scene duration
# evenly across the entries.  Repeated entries are intentional holds/cut-backs,
# not missing assets.
SCENE_ASSETS: dict[str, list[str]] = {
    # Opening: one coherent clinic situation, then an exact three-level model.
    "S001": [f"{P}/S001_clinic_arrival.mp4"],
    "S002": [f"{N}/S002_phone_tap_alt_1080p.mp4"],
    "S003": [f"{P}/S003_open_black_box.mp4"],
    "S004": [f"{P}/S004_design_power_participation.mp4"],
    "S005": [f"{P}/S005_title_plate.mp4", f"{P}/S004_design_power_participation.mp4", f"{F}/S095_flow_1080p.mp4"],
    "S006": [f"{N}/S006_clinic_waiting_alt_1080p.mp4"],
    "S007": [f"{M}/MG01_three_layers.mp4"],
    "S008": [f"{N}/S002_phone_tap_alt_1080p.mp4", f"{N}/S006_clinic_waiting_alt_1080p.mp4"],
    "S009": [f"{F}/S050_flow_1080p.mp4"],
    "S010": [f"{N}/S034_scheduling_options_alt_1080p.mp4"],
    "S011": [f"{M}/MG01_three_layers.mp4"],
    "S012": [f"{M}/MG07_access_participation.mp4", f"{N}/S006_clinic_waiting_alt_1080p.mp4"],
    "S013": [f"{F}/S013_schedule_exclusion_1080p.mp4", f"{E}/S014_affected_users_1080p.mp4", f"{F}/S095_flow_1080p.mp4"],
    "S014": [f"{E}/S014_affected_users_1080p.mp4", f"{F}/S051_flow_1080p.mp4"],

    # Four positions in Feenberg's map are never presented as four stages.
    "S015": [f"{F}/S015_neutral_tool_1080p.mp4"],
    "S016": [f"{C}/S016_S01_p05_matrix_crop.png"],
    "S017": [f"{F}/S015_neutral_tool_1080p.mp4", f"{F}/S095_flow_1080p.mp4"],
    "S018": [f"{M}/MG02_matrix.mp4"],
    "S019": [f"{M}/MG02_matrix.mp4"],
    "S020": [f"{F}/S031_flow_1080p.mp4"],
    "S021": [f"{F}/S015_neutral_tool_1080p.mp4"],
    "S022": [f"{F}/S031_flow_1080p.mp4"],
    "S023": [f"{F}/S031_flow_1080p.mp4", f"{F}/S091_flow_1080p.mp4"],
    "S024": [f"{F}/S024_flow_1080p.mp4"],
    "S025": [f"{C}/S025_S01_p09_critical_theory_crop.png"],
    "S026": [f"{O}/S034_multiple_options_1080p.mp4"],
    "S027": [f"{F}/S028_technical_frame_civic_space_720p.mp4"],

    # Meta-choice, underdetermination and ambivalence.
    "S028": [f"{F}/S028_technical_frame_civic_space_720p.mp4"],
    "S029": [f"{F}/S013_schedule_exclusion_1080p.mp4", f"{E}/S014_affected_users_1080p.mp4"],
    "S030": [f"{M}/MG03_meta_choice.mp4"],
    "S031": [f"{O}/S031_meta_choice_ramp_1080p.mp4"],
    "S032": [f"{F}/S028_technical_frame_civic_space_720p.mp4", f"{O}/S031_meta_choice_ramp_1080p.mp4"],
    "S033": [f"{F}/S009_flow_1080p.mp4", f"{F}/S010_flow_1080p.mp4", f"{F}/S040_technical_code_materials_1080p.mp4"],
    "S034": [f"{O}/S034_multiple_options_1080p.mp4"],
    "S035": [f"{N}/S040_constraints_alt_1080p.mp4"],
    "S036": [f"{C}/S036_S03_p05_underdetermination_crop.png"],
    "S037": [f"{O}/S034_multiple_options_1080p.mp4", f"{N}/S040_constraints_alt_1080p.mp4"],
    "S038": [f"{F}/S040_technical_code_materials_1080p.mp4", f"{F}/S024_flow_1080p.mp4", f"{O}/S034_multiple_options_1080p.mp4"],

    # Technical code and the boiler example.  Reconstructions are labelled in post.
    "S039": [f"{M}/MG05_technical_code.mp4"],
    "S040": [f"{N}/S040_constraints_alt_1080p.mp4"],
    "S041": [f"{F}/S040_technical_code_materials_1080p.mp4", f"{M}/MG05_technical_code.mp4"],
    "S042": [f"{C}/S042_S03_p13_technical_code_definition_crop.png"],
    "S043": [f"{O}/S043_boiler_reconstruction_1080p.mp4"],
    "S044": [f"{N}/S043_boiler_alt_1080p.mp4"],
    "S045": [f"{O}/S043_boiler_reconstruction_1080p.mp4", f"{N}/S043_boiler_alt_1080p.mp4", f"{F}/S040_technical_code_materials_1080p.mp4"],
    "S046": [f"{N}/S043_boiler_alt_1080p.mp4"],
    "S047": [f"{O}/S043_boiler_reconstruction_1080p.mp4"],
    "S048": [f"{C}/S048_S02_p24_condensed_relations_crop.png"],
    "S049": [f"{F}/S040_technical_code_materials_1080p.mp4"],
    "S050": [f"{N}/S062_codesign_kiosk_alt_1080p.mp4"],
    "S051": [f"{E}/S014_affected_users_1080p.mp4", f"{F}/S051_flow_1080p.mp4"],
    "S052": [f"{F}/S063_flow_1080p.mp4", f"{F}/S051_flow_1080p.mp4", f"{F}/S050_flow_1080p.mp4"],

    # Democratization: effective participation, not access or consultation theatre.
    "S053": [f"{F}/S091_flow_1080p.mp4"],
    "S054": [f"{F}/S063_flow_1080p.mp4"],
    "S055": [f"{M}/MG07_access_participation.mp4"],
    "S056": [f"{C}/S056_S03_p18_participation_crop.png"],
    "S057": [f"{F}/S009_flow_1080p.mp4", f"{N}/S062_codesign_kiosk_alt_1080p.mp4", f"{N}/S034_scheduling_options_alt_1080p.mp4"],
    "S058": [f"{F}/S063_flow_1080p.mp4"],
    "S059": [f"{F}/S063_flow_1080p.mp4", f"{F}/S024_flow_1080p.mp4"],
    "S060": [f"{F}/S010_flow_1080p.mp4"],
    "S061": [f"{F}/S009_flow_1080p.mp4", f"{F}/S050_flow_1080p.mp4"],
    "S062": [f"{E}/S063_codesign_no_applause_1080p.mp4"],
    "S063": [f"{N}/S062_codesign_kiosk_alt_1080p.mp4", f"{F}/S063_flow_1080p.mp4", f"{F}/S051_flow_1080p.mp4"],

    # Network trajectory and the tightly bounded ALS case.
    "S064": [f"{C}/S064_S02_p10_network_origin_crop.png"],
    "S065": [f"{O}/S065_network_users_1080p.mp4"],
    "S066": [f"{N}/S065_network_users_alt_1080p.mp4"],
    "S067": [f"{O}/S065_network_users_1080p.mp4", f"{N}/S065_network_users_alt_1080p.mp4"],
    "S068": [f"{M}/MG10_network_transform.mp4"],
    "S069": [f"{O}/S065_network_users_1080p.mp4", f"{N}/S065_network_users_alt_1080p.mp4"],
    "S070": [f"{C}/S070_S02_p11_design_change_crop.png"],
    # These clips illustrate an online-support setting; they are not presented
    # as archival footage of the specific 1995 Prodigy group.
    "S071": [f"{N}/S073_adaptive_computer_alt_1080p.mp4", f"{O}/S073_adaptive_computer_1080p.mp4"],
    "S072": [f"{N}/S073_adaptive_computer_alt_1080p.mp4", f"{O}/S073_adaptive_computer_1080p.mp4"],
    "S073": [f"{O}/S073_adaptive_computer_1080p.mp4", f"{N}/S073_adaptive_computer_alt_1080p.mp4"],
    "S074": [f"{F}/S075_priority_cards_1080p.mp4", f"{N}/S073_adaptive_computer_alt_1080p.mp4"],
    "S075": [f"{F}/S075_priority_cards_1080p.mp4"],
    "S076": [f"{M}/MG11_evidence_boundary.mp4"],
    "S077": [f"{M}/MG11_evidence_boundary.mp4"],
    "S078": [f"{O}/S065_network_users_1080p.mp4", f"{N}/S065_network_users_alt_1080p.mp4", f"{M}/MG10_network_transform.mp4", f"{O}/S073_adaptive_computer_1080p.mp4", f"{N}/S073_adaptive_computer_alt_1080p.mp4", f"{F}/S075_priority_cards_1080p.mp4", f"{M}/MG09_participation_loop.mp4"],
    "S079": [f"{M}/MG11_evidence_boundary.mp4", f"{O}/S073_adaptive_computer_1080p.mp4", f"{N}/S065_network_users_alt_1080p.mp4"],

    # Methodological transfer by Group 14.
    "S080": [f"{F}/S095_flow_1080p.mp4", f"{N}/S002_phone_tap_alt_1080p.mp4"],
    "S081": [f"{F}/S015_neutral_tool_1080p.mp4"],
    "S082": [f"{M}/MG12_five_questions.mp4"],
    "S083": [f"{N}/S034_scheduling_options_alt_1080p.mp4", f"{F}/S095_flow_1080p.mp4"],
    "S084": [f"{F}/S040_technical_code_materials_1080p.mp4", f"{N}/S006_clinic_waiting_alt_1080p.mp4"],
    "S085": [f"{O}/S031_meta_choice_ramp_1080p.mp4", f"{E}/S014_affected_users_1080p.mp4"],
    "S086": [f"{N}/S062_codesign_kiosk_alt_1080p.mp4", f"{F}/S051_flow_1080p.mp4"],
    "S087": [f"{E}/S087_redesign_button_macro_1080p.mp4", f"{N}/S040_constraints_alt_1080p.mp4"],
    "S088": [f"{N}/S034_scheduling_options_alt_1080p.mp4", f"{N}/S040_constraints_alt_1080p.mp4"],
    "S089": [f"{G}/S089_five_criteria.png"],
    "S090": [
        f"{F}/S063_flow_1080p.mp4",
        f"{F}/S095_flow_1080p.mp4",
        f"{E}/S014_affected_users_1080p.mp4",
    ],

    # Return to the central question, then film-style credits.
    "S091": [f"{P}/S003_open_black_box.mp4"],
    "S092": [f"{M}/MG16_conclusion_layers.mp4"],
    "S093": [f"{O}/S034_multiple_options_1080p.mp4", f"{O}/S031_meta_choice_ramp_1080p.mp4"],
    "S094": [f"{M}/MG17_method_motif.mp4"],
    "S095": [f"{N}/S099_closing_kiosk_alt_1080p.mp4"],
    "S096": [f"{O}/S099_closing_kiosk_1080p.mp4"],
    "S097": [f"{N}/S099_closing_kiosk_alt_1080p.mp4"],
    "S098": [f"{P}/S005_title_plate.mp4", f"{N}/S062_codesign_kiosk_alt_1080p.mp4", f"{N}/S099_closing_kiosk_alt_1080p.mp4"],
    "S099": [f"{O}/S099_closing_kiosk_1080p.mp4"],
    "S100": [f"{N}/S099_closing_kiosk_alt_1080p.mp4"],
}


# Extra deterministic overlays.  These are typography/diagrams created after
# generation; important Vietnamese text is never delegated to a video model.
EXTRA_OVERLAYS: dict[str, str] = {
    "S001": f"{P}/../overlays/S001_overlay.png",
    "S002": f"{P}/../overlays/S002_overlay.png",
    "S003": f"{P}/../overlays/S003_overlay.png",
    "S004": f"{P}/../overlays/S004_overlay.png",
    "S005": f"{G}/S005_title_overlay.png",
    "S006": f"{P}/../overlays/S006_overlay.png",
    "S083": f"{G}/S083_question_1_overlay.png",
    "S084": f"{G}/S084_question_2_overlay.png",
    "S085": f"{G}/S085_question_3_overlay.png",
    "S086": f"{G}/S086_question_4_overlay.png",
    "S087": f"{G}/S087_question_5_overlay.png",
    "S058": f"{G}/S058_terminology_revision.png",
    "S096": f"{G}/S096_film_credit.png",
    "S097": f"{G}/S097_course_credit.png",
    "S098": f"{G}/S098_members_credit.png",
    "S099": f"{G}/S099_thanks.png",
    "S100": f"{G}/S100_endcard.png",
}


FULL_GRAPHIC_SCENES = {
    scene_id
    for scene_id, assets in SCENE_ASSETS.items()
    if assets[0].startswith(f"{M}/")
} | {"S089", "S100"}

SOURCE_SCENES = {"S016", "S025", "S036", "S042", "S048", "S056", "S064", "S070"}
NATIVE_720_SCENES = {"S028", "S032", "S043"}
RECONSTRUCTION_SCENES = {"S043", "S044", "S045", "S046", "S047", "S065", "S067", "S071", "S072", "S073", "S074", "S075", "S076"}
GROUP_HYPOTHETICAL_SCENES = {f"S{index:03d}" for index in range(1, 15)}
GROUP_PROPOSAL_SCENES = {f"S{index:03d}" for index in range(80, 91)}


def is_generated_video(relative: str) -> bool:
    return relative.startswith((f"{P}/", f"{F}/", f"{E}/", f"{O}/", f"{N}/"))


def is_reconstruction_asset(relative: str) -> bool:
    return relative in {
        f"{F}/S043_pressure_vessel_v2.mp4",
        f"{F}/S043_boiler_reconstruction_1080p.mp4",
        f"{F}/S071_flow_1080p.mp4",
        f"{F}/S073_flow_1080p.mp4",
        f"{F}/S075_priority_cards_1080p.mp4",
        f"{F}/ALS_1995_new_1080p.mp4",
    }


# No asset in the locked edit relies on a hidden unsafe opening.  Scene-level
# trimming remains available for future replacements but is intentionally empty.
VIDEO_TRIM_START: dict[tuple[str, str], float] = {}


# Scene-specific cleanup that cannot be applied globally.  AI provenance is
# disclosed in every reconstruction label and again in the end credit.
VIDEO_POST_FILTERS: dict[tuple[str, str], tuple[str, ...]] = {
    **{
        (scene_id, f"{F}/S043_boiler_reconstruction_1080p.mp4"): (
            "delogo=x=1:y=1011:w=368:h=68:show=0",
        )
        for scene_id in ("S043", "S044", "S045", "S046", "S047")
    },
}


# These conceptual mechanical shots are safe to play backwards when a cut-back
# requires a contrasting direction.  Human actions are deliberately excluded.
REVERSIBLE_ASSETS = {
    f"{P}/S003_open_black_box.mp4",
    f"{F}/S024_flow_1080p.mp4",
    f"{F}/S059_flow_1080p.mp4",
    f"{F}/S078_flow_1080p.mp4",
    f"{F}/S091_flow_1080p.mp4",
}


CHAPTER_FADE_SCENES = {"S001", "S005", "S027", "S053", "S064", "S080", "S096", "S100"}


def validate_plan(scene_ids: list[str]) -> None:
    """Fail fast if the storyboard and locked edit plan diverge."""

    expected = set(scene_ids)
    actual = set(SCENE_ASSETS)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise ValueError(f"Visual plan mismatch; missing={missing}, extra={extra}")
    for scene_id, assets in SCENE_ASSETS.items():
        if not assets:
            raise ValueError(f"Scene {scene_id} has no visual asset")
