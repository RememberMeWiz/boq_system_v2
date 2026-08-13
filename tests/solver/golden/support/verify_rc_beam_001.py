#!/usr/bin/env python3
"""Regenerate and verify the RC-BEAM-001 golden reference case.

This helper intentionally uses only the Python standard library. It reads source
facts and policies from rc_beam_001_input.json, computes all expected results,
and renders both rc_beam_001_expected.json and docs/solver/golden/RC-BEAM-001.md.

Usage from the repository root:

    python tests/solver/golden/support/verify_rc_beam_001.py --write
    python tests/solver/golden/support/verify_rc_beam_001.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any, Iterable

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[4]
INPUT_PATH = REPO_ROOT / "tests/solver/golden/rc_beam_001_input.json"
EXPECTED_PATH = REPO_ROOT / "tests/solver/golden/rc_beam_001_expected.json"
MARKDOWN_PATH = REPO_ROOT / "docs/solver/golden/RC-BEAM-001.md"

D0 = Decimal("0")
D1 = Decimal("1")


def d(value: Any) -> Decimal:
    """Convert a JSON-compatible scalar to Decimal without binary-float drift."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def q(quantity: dict[str, Any]) -> Decimal:
    return d(quantity["value"])


def decstr(value: Decimal) -> str:
    return format(value, "f")


def quantize_places(value: Decimal, places: int) -> Decimal:
    quantum = D1.scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def ceiling_to_increment(value: Decimal, increment: Decimal) -> Decimal:
    if increment <= 0:
        raise ValueError("Procurement increment must be greater than zero")
    units = (value / increment).to_integral_value(rounding=ROUND_CEILING)
    return units * increment


def numeric_json(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def json_safe(value: Any) -> Any:
    """Recursively convert Decimal instances into JSON-compatible numbers."""
    if isinstance(value, Decimal):
        return numeric_json(value)
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    return value


def quantity_result(value: Decimal, unit: str, places: int = 6) -> dict[str, Any]:
    reported = quantize_places(value, places)
    return {
        "unrounded_value": decstr(value),
        "reported_value": numeric_json(reported),
        "display": f"{reported:.{places}f}",
        "unit": unit,
    }


def calc_result(
    formula_id: str,
    description: str,
    symbolic_formula: str,
    substitution: str,
    value: Decimal,
    unit: str,
    places: int = 6,
    rounding_stage: str = "reporting_only",
) -> dict[str, Any]:
    result = {
        "formula_id": formula_id,
        "description": description,
        "symbolic_formula": symbolic_formula,
        "substitution": substitution,
        "rounding_stage": rounding_stage,
    }
    result.update(quantity_result(value, unit, places))
    return result


def money_result(
    formula_id: str,
    description: str,
    symbolic_formula: str,
    substitution: str,
    value: Decimal,
) -> dict[str, Any]:
    return calc_result(
        formula_id,
        description,
        symbolic_formula,
        substitution,
        value,
        "PHP",
        places=2,
        rounding_stage="round_half_up_to_PHP_0.01_at_line_level",
    )


def unit_weight(diameter_mm: Decimal, divisor: Decimal) -> Decimal:
    return diameter_mm * diameter_mm / divisor


@dataclass(frozen=True)
class CutPattern:
    stock_length: Decimal
    pieces: int
    piece_length: Decimal
    kerf: Decimal
    offcut: Decimal
    reusable: Decimal
    scrap: Decimal

    @property
    def used_length(self) -> Decimal:
        return self.stock_length - self.offcut

    @property
    def signature(self) -> tuple[str, int]:
        return (decstr(self.stock_length), self.pieces)


@dataclass
class PlanState:
    purchased_length: Decimal
    stock_bar_count: int
    scrap_length: Decimal
    largest_offcut: Decimal
    patterns: list[CutPattern]

    def objective(self) -> tuple[Any, ...]:
        signature = tuple(sorted((p.signature for p in self.patterns), reverse=True))
        return (
            self.purchased_length,
            self.stock_bar_count,
            self.scrap_length,
            self.largest_offcut,
            signature,
        )


def optimize_identical_cuts(
    piece_length: Decimal,
    piece_count: int,
    stock_lengths: Iterable[Decimal],
    kerf: Decimal,
    reusable_threshold: Decimal,
) -> list[CutPattern]:
    """Exact-piece dynamic program using the declared lexicographic objective."""
    if piece_length <= 0 or piece_count <= 0:
        raise ValueError("Cut length and count must be greater than zero")
    if kerf < 0:
        raise ValueError("Cut kerf cannot be negative")

    patterns: list[CutPattern] = []
    for stock in sorted(set(stock_lengths)):
        if stock <= 0:
            raise ValueError("Stock length must be greater than zero")
        max_pieces = int((stock / (piece_length + kerf)).to_integral_value(rounding=ROUND_FLOOR))
        for pieces in range(1, max_pieces + 1):
            used = piece_length * pieces + kerf * pieces
            offcut = stock - used
            if offcut < 0:
                continue
            reusable = offcut if offcut >= reusable_threshold else D0
            scrap = offcut if D0 < offcut < reusable_threshold else D0
            patterns.append(
                CutPattern(
                    stock_length=stock,
                    pieces=pieces,
                    piece_length=piece_length,
                    kerf=kerf,
                    offcut=offcut,
                    reusable=reusable,
                    scrap=scrap,
                )
            )

    best: dict[int, PlanState] = {
        0: PlanState(D0, 0, D0, D0, [])
    }
    for completed in range(piece_count + 1):
        state = best.get(completed)
        if state is None:
            continue
        for pattern in patterns:
            new_completed = completed + pattern.pieces
            if new_completed > piece_count:
                continue
            candidate = PlanState(
                purchased_length=state.purchased_length + pattern.stock_length,
                stock_bar_count=state.stock_bar_count + 1,
                scrap_length=state.scrap_length + pattern.scrap,
                largest_offcut=max(state.largest_offcut, pattern.offcut),
                patterns=state.patterns + [pattern],
            )
            incumbent = best.get(new_completed)
            if incumbent is None or candidate.objective() < incumbent.objective():
                best[new_completed] = candidate

    if piece_count not in best:
        raise ValueError(
            f"No exact cutting plan for {piece_count} pieces at {piece_length} m"
        )

    return sorted(
        best[piece_count].patterns,
        key=lambda p: (p.stock_length, p.pieces, p.offcut),
        reverse=True,
    )


def generate_zone_positions(zone: dict[str, Any]) -> list[Decimal]:
    start = q(zone["start"])
    end = q(zone["end"])
    spacing = q(zone["spacing"])
    if spacing <= 0:
        raise ValueError(f"{zone['zone_id']}: spacing must be greater than zero")
    if end < start:
        raise ValueError(f"{zone['zone_id']}: end must not be less than start")

    positions: list[Decimal] = []
    index = 0 if zone["include_start_boundary"] else 1
    while True:
        position = start + d(index) * spacing
        if position > end:
            break
        if position == end and not zone["include_end_boundary"]:
            break
        positions.append(position)
        index += 1
    return positions


def load_input() -> dict[str, Any]:
    with INPUT_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle, parse_float=Decimal)


def validate_source_case(source: dict[str, Any]) -> None:
    """Reject hidden defaults, calculated answers, and unsupported policies."""
    errors: list[str] = []
    forbidden_output_keys = {
        "formula_id",
        "symbolic_formula",
        "substitution",
        "unrounded_value",
        "reported_value",
        "display",
        "calculation_payload_sha256",
        "status",
    }

    def walk(value: Any, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            if "value" in value and "unit" not in value:
                errors.append(f"{'.'.join(path) or '<root>'}: quantity value has no unit")
            for key, item in value.items():
                if key in forbidden_output_keys:
                    errors.append(
                        f"{'.'.join(path + (key,))}: calculated-output key is not allowed in input"
                    )
                walk(item, path + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, path + (str(index),))
        elif isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
            if not path or path[-1] != "value":
                errors.append(
                    f"{'.'.join(path)}: numeric source fact must be wrapped as value plus unit"
                )

    walk(source)

    reporting = source.get("reporting_policy", {})
    expected_reporting = {
        "calculation_decimal_precision": 36,
        "reported_quantity_decimal_places": 6,
        "reported_cost_decimal_places": 2,
    }
    for key, expected_value in expected_reporting.items():
        if key not in reporting or q(reporting[key]) != d(expected_value):
            errors.append(f"reporting_policy.{key} must explicitly equal {expected_value}")
    if reporting.get("quantity_rounding_mode") != "round_half_up":
        errors.append("reporting_policy.quantity_rounding_mode must be round_half_up")
    if reporting.get("cost_rounding_mode") != "round_half_up":
        errors.append("reporting_policy.cost_rounding_mode must be round_half_up")

    geometry = source.get("geometry", {})
    positive_geometry_paths = [
        ("beam_count",),
        ("beam_width",),
        ("overall_depth",),
        ("net_beam_below_slab_depth",),
        ("clear_span_between_support_faces",),
        ("left_support", "dimension_along_beam"),
        ("right_support", "dimension_along_beam"),
        ("slab", "thickness"),
    ]
    for keys in positive_geometry_paths:
        current: Any = geometry
        try:
            for key in keys:
                current = current[key]
            if q(current) <= 0:
                errors.append(f"geometry.{'.'.join(keys)} must be greater than zero")
        except (KeyError, TypeError):
            errors.append(f"geometry.{'.'.join(keys)} is required")
    if geometry.get("beam_count") and q(geometry["beam_count"]) != D1:
        errors.append("geometry.beam_count must explicitly equal one beam")
    for side in ("left_support", "right_support"):
        if not geometry.get(side, {}).get("fully_overlaps_beam_cross_section", False):
            errors.append(f"geometry.{side}.fully_overlaps_beam_cross_section must be true")

    concrete = source.get("concrete_policy", {})
    if concrete.get("waste_basis") != "net_measured_volume":
        errors.append("concrete_policy.waste_basis must be net_measured_volume")
    if concrete.get("procurement_rounding") != "ceiling_to_increment":
        errors.append("concrete_policy.procurement_rounding must be ceiling_to_increment")

    formwork = source.get("formwork_policy", {})
    if formwork.get("length_basis") != "clear_span_only":
        errors.append("formwork_policy.length_basis must be clear_span_only")
    if formwork.get("side_depth_basis") != "net_beam_below_slab_depth":
        errors.append(
            "formwork_policy.side_depth_basis must be net_beam_below_slab_depth"
        )
    expected_surfaces = {
        "soffit_included": True,
        "left_side_included": True,
        "right_side_included": True,
        "left_end_form_included": False,
        "right_end_form_included": False,
        "top_surface_included": False,
        "support_intersection_surfaces_included": False,
    }
    for key, expected_value in expected_surfaces.items():
        if formwork.get(key) is not expected_value:
            errors.append(f"formwork_policy.{key} must explicitly be {expected_value}")
    for key, item in formwork.get("resource_procurement_rounding", {}).items():
        if item.get("mode") != "ceiling":
            errors.append(
                f"formwork_policy.resource_procurement_rounding.{key}.mode must be ceiling"
            )

    reinforcement = source.get("reinforcement_policy", {})
    if reinforcement.get("structural_design_inference_allowed") is not False:
        errors.append(
            "reinforcement_policy.structural_design_inference_allowed must be false"
        )
    stirrups = reinforcement.get("stirrups", {})
    if stirrups.get("section_depth_basis") != "overall_depth":
        errors.append("reinforcement_policy.stirrups.section_depth_basis must be overall_depth")
    cutting_policy = stirrups.get("cutting_length_policy", {})
    if cutting_policy.get("formula") != (
        "L_st = 2*(b_st + D_st) + total_hook_extension - aggregate_bend_deduction"
    ):
        errors.append("reinforcement_policy.stirrups.cutting_length_policy.formula is required")
    if cutting_policy.get("additional_centerline_or_bend_radius_adjustment") != (
        "none beyond the explicitly supplied aggregate bend deduction"
    ):
        errors.append(
            "reinforcement_policy.stirrups must explicitly prohibit additional inferred adjustments"
        )

    procurement = source.get("rebar_procurement_policy", {})
    if not procurement.get("cut_kerf_application_rule"):
        errors.append("rebar_procurement_policy.cut_kerf_application_rule is required")
    if procurement.get("unresolved_demand_policy") != "must_equal_zero":
        errors.append("rebar_procurement_policy.unresolved_demand_policy must be must_equal_zero")
    if not procurement.get("optimization_objective_order"):
        errors.append("rebar_procurement_policy.optimization_objective_order is required")

    cost_policy = source.get("resources_and_pricing", {}).get(
        "cost_rounding_policy", {}
    )
    if q(cost_policy.get("line_amount_increment", {"value": -1})) != d("0.01"):
        errors.append("cost line amount increment must explicitly equal PHP 0.01")
    if cost_policy.get("mode") != "round_half_up_each_line_before_subtotal":
        errors.append("cost rounding mode must be round_half_up_each_line_before_subtotal")
    if cost_policy.get("category_subtotal_policy") != "sum_reported_line_amounts":
        errors.append("category subtotals must sum reported line amounts")
    if cost_policy.get("grand_total_policy") != "sum_reported_category_subtotals":
        errors.append("grand total must sum reported category subtotals")

    if errors:
        raise ValueError("Invalid RC-BEAM-001 source input:\n- " + "\n- ".join(errors))


def build_expected(source: dict[str, Any]) -> dict[str, Any]:
    validate_source_case(source)
    getcontext().prec = int(q(source["reporting_policy"]["calculation_decimal_precision"]))
    geometry = source["geometry"]
    concrete_policy = source["concrete_policy"]
    formwork_policy = source["formwork_policy"]
    reinforcement = source["reinforcement_policy"]
    procurement_policy = source["rebar_procurement_policy"]
    resources = source["resources_and_pricing"]

    b = q(geometry["beam_width"])
    overall_depth = q(geometry["overall_depth"])
    net_depth = q(geometry["net_beam_below_slab_depth"])
    clear_span = q(geometry["clear_span_between_support_faces"])
    left_support = q(geometry["left_support"]["dimension_along_beam"])
    right_support = q(geometry["right_support"]["dimension_along_beam"])
    slab_t = q(geometry["slab"]["thickness"])

    computed_net_depth = overall_depth - slab_t
    overall_length = clear_span + left_support + right_support
    centerline_span = clear_span + left_support / d(2) + right_support / d(2)

    geometry_results = {
        "net_depth_check": calc_result(
            "RCB-GEO-001",
            "Compute the beam drop below the monolithic slab and compare it with the explicitly supplied net depth.",
            "D_net,calc = D_overall - t_slab",
            f"{decstr(overall_depth)} - {decstr(slab_t)}",
            computed_net_depth,
            "m",
        ),
        "outer_face_to_outer_face_length": calc_result(
            "RCB-GEO-002",
            "Overall beam prism length before support deductions.",
            "L_outer = L_clear + w_support,left + w_support,right",
            f"{decstr(clear_span)} + {decstr(left_support)} + {decstr(right_support)}",
            overall_length,
            "m",
        ),
        "support_centerline_span": calc_result(
            "RCB-GEO-003",
            "Centerline-to-centerline span derived transparently from the supplied clear span and support widths.",
            "L_c/c = L_clear + w_left/2 + w_right/2",
            f"{decstr(clear_span)} + {decstr(left_support)}/2 + {decstr(right_support)}/2",
            centerline_span,
            "m",
        ),
        "explicit_net_depth": quantity_result(net_depth, "m"),
        "net_depth_difference": calc_result(
            "RCB-GEO-004",
            "Difference between computed and explicitly supplied net depth.",
            "Delta_D = D_net,calc - D_net,input",
            f"{decstr(computed_net_depth)} - {decstr(net_depth)}",
            computed_net_depth - net_depth,
            "m",
        ),
    }

    gross_volume = b * overall_depth * overall_length
    left_intersection = b * overall_depth * left_support
    right_intersection = b * overall_depth * right_support
    support_deduction = left_intersection + right_intersection
    clear_span_overall_depth_volume = gross_volume - support_deduction
    slab_deduction = b * slab_t * clear_span
    net_concrete = clear_span_overall_depth_volume - slab_deduction
    direct_net_concrete = b * net_depth * clear_span
    waste_rate = q(concrete_policy["waste_rate"])
    waste_quantity = net_concrete * waste_rate
    required_concrete = net_concrete + waste_quantity
    concrete_increment = q(concrete_policy["procurement_increment"])
    procured_concrete = ceiling_to_increment(required_concrete, concrete_increment)
    concrete_rounding_excess = procured_concrete - required_concrete

    concrete_results = {
        "gross_volume": calc_result(
            "RCB-CON-001",
            "Gross full-prism beam volume before any intersection deductions.",
            "V_gross = b * D_overall * L_outer",
            f"{decstr(b)} * {decstr(overall_depth)} * {decstr(overall_length)}",
            gross_volume,
            "m^3",
        ),
        "left_support_intersection": calc_result(
            "RCB-CON-002",
            "Beam prism volume inside the left support.",
            "V_left = b * D_overall * w_left",
            f"{decstr(b)} * {decstr(overall_depth)} * {decstr(left_support)}",
            left_intersection,
            "m^3",
        ),
        "right_support_intersection": calc_result(
            "RCB-CON-003",
            "Beam prism volume inside the right support.",
            "V_right = b * D_overall * w_right",
            f"{decstr(b)} * {decstr(overall_depth)} * {decstr(right_support)}",
            right_intersection,
            "m^3",
        ),
        "support_intersection_deduction": calc_result(
            "RCB-CON-004",
            "Combined support-intersection deduction.",
            "V_support = V_left + V_right",
            f"{decstr(left_intersection)} + {decstr(right_intersection)}",
            support_deduction,
            "m^3",
        ),
        "clear_span_overall_depth_volume": calc_result(
            "RCB-CON-005",
            "Clear-span beam prism at overall depth after support deductions.",
            "V_clear,overall = V_gross - V_support",
            f"{decstr(gross_volume)} - {decstr(support_deduction)}",
            clear_span_overall_depth_volume,
            "m^3",
        ),
        "slab_intersection_deduction": calc_result(
            "RCB-CON-006",
            "Slab-owned volume across the clear-span beam strip.",
            "V_slab = b * t_slab * L_clear",
            f"{decstr(b)} * {decstr(slab_t)} * {decstr(clear_span)}",
            slab_deduction,
            "m^3",
        ),
        "net_measured_volume": calc_result(
            "RCB-CON-007",
            "Net measured beam concrete after support and slab deductions.",
            "V_net = V_gross - V_support - V_slab",
            f"{decstr(gross_volume)} - {decstr(support_deduction)} - {decstr(slab_deduction)}",
            net_concrete,
            "m^3",
        ),
        "independent_direct_net_volume": calc_result(
            "RCB-CON-008",
            "Independent direct calculation using clear span and the explicit beam-below-slab depth.",
            "V_net,check = b * D_net * L_clear",
            f"{decstr(b)} * {decstr(net_depth)} * {decstr(clear_span)}",
            direct_net_concrete,
            "m^3",
        ),
        "waste_quantity": calc_result(
            "RCB-CON-009",
            "Concrete waste allowance kept separate from net measured volume.",
            "V_waste = V_net * r_waste",
            f"{decstr(net_concrete)} * {decstr(waste_rate)}",
            waste_quantity,
            "m^3",
        ),
        "required_quantity": calc_result(
            "RCB-CON-010",
            "Concrete required before commercial procurement rounding.",
            "V_required = V_net + V_waste",
            f"{decstr(net_concrete)} + {decstr(waste_quantity)}",
            required_concrete,
            "m^3",
        ),
        "procurement_quantity": calc_result(
            "RCB-CON-011",
            "Concrete ordered after ceiling to the declared batch increment.",
            "V_proc = ceil(V_required / increment) * increment",
            f"ceil({decstr(required_concrete)} / {decstr(concrete_increment)}) * {decstr(concrete_increment)}",
            procured_concrete,
            "m^3",
            rounding_stage="procurement_ceiling_to_0.100000_m^3",
        ),
        "procurement_rounding_excess": calc_result(
            "RCB-CON-012",
            "Quantity caused only by commercial batch rounding.",
            "V_rounding = V_proc - V_required",
            f"{decstr(procured_concrete)} - {decstr(required_concrete)}",
            concrete_rounding_excess,
            "m^3",
        ),
    }

    soffit = b * clear_span
    left_side = net_depth * clear_span
    right_side = net_depth * clear_span
    end_forms = D0
    contact_area = soffit + left_side + right_side + end_forms
    contact_area_check = (b + d(2) * net_depth) * clear_span

    factors = formwork_policy["resource_factors"]
    plywood_theoretical = contact_area * q(factors["plywood_sheet_equivalent_per_contact_area"])
    lumber_theoretical = contact_area * q(factors["form_lumber_per_contact_area"])
    release_oil_theoretical = contact_area * q(factors["release_oil_per_contact_area"])

    roundings = formwork_policy["resource_procurement_rounding"]
    plywood_proc = ceiling_to_increment(
        plywood_theoretical, q(roundings["plywood_sheet"]["increment"])
    )
    lumber_proc = ceiling_to_increment(
        lumber_theoretical, q(roundings["form_lumber"]["increment"])
    )
    oil_proc = ceiling_to_increment(
        release_oil_theoretical, q(roundings["release_oil"]["increment"])
    )

    formwork_results = {
        "soffit_area": calc_result(
            "RCB-FRM-001",
            "Soffit contact area over the clear span.",
            "A_soffit = b * L_clear",
            f"{decstr(b)} * {decstr(clear_span)}",
            soffit,
            "m^2",
        ),
        "left_side_area": calc_result(
            "RCB-FRM-002",
            "Left beam-side contact area using only the beam drop below the slab.",
            "A_left = D_net * L_clear",
            f"{decstr(net_depth)} * {decstr(clear_span)}",
            left_side,
            "m^2",
        ),
        "right_side_area": calc_result(
            "RCB-FRM-003",
            "Right beam-side contact area using only the beam drop below the slab.",
            "A_right = D_net * L_clear",
            f"{decstr(net_depth)} * {decstr(clear_span)}",
            right_side,
            "m^2",
        ),
        "end_form_area": calc_result(
            "RCB-FRM-004",
            "End form area. Both ends are excluded because they are monolithic support interfaces.",
            "A_ends = 0",
            "0",
            end_forms,
            "m^2",
        ),
        "total_contact_area": calc_result(
            "RCB-FRM-005",
            "Total form-contact area. This remains an area and is never merged into concrete volume.",
            "A_form = A_soffit + A_left + A_right + A_ends",
            f"{decstr(soffit)} + {decstr(left_side)} + {decstr(right_side)} + {decstr(end_forms)}",
            contact_area,
            "m^2",
        ),
        "independent_contact_area": calc_result(
            "RCB-FRM-006",
            "Independent beam-form perimeter method.",
            "A_form,check = (b + 2*D_net) * L_clear",
            f"({decstr(b)} + 2*{decstr(net_depth)}) * {decstr(clear_span)}",
            contact_area_check,
            "m^2",
        ),
        "resources": {
            "plywood_theoretical": calc_result(
                "RCB-FRM-007",
                "Theoretical plywood sheet-equivalent consumption.",
                "Q_ply,theory = A_form * f_ply",
                f"{decstr(contact_area)} * {decstr(q(factors['plywood_sheet_equivalent_per_contact_area']))}",
                plywood_theoretical,
                "sheet",
            ),
            "plywood_procurement": calc_result(
                "RCB-FRM-008",
                "Whole-sheet plywood procurement.",
                "Q_ply,proc = ceil(Q_ply,theory / 1 sheet) * 1 sheet",
                f"ceil({decstr(plywood_theoretical)} / 1) * 1",
                plywood_proc,
                "sheet",
                places=0,
                rounding_stage="procurement_ceiling_to_whole_sheet",
            ),
            "form_lumber_theoretical": calc_result(
                "RCB-FRM-009",
                "Theoretical form-lumber consumption.",
                "Q_lumber,theory = A_form * f_lumber",
                f"{decstr(contact_area)} * {decstr(q(factors['form_lumber_per_contact_area']))}",
                lumber_theoretical,
                "board_foot",
            ),
            "form_lumber_procurement": calc_result(
                "RCB-FRM-010",
                "Form-lumber procurement rounded upward to a whole board foot.",
                "Q_lumber,proc = ceil(Q_lumber,theory / 1 bdft) * 1 bdft",
                f"ceil({decstr(lumber_theoretical)} / 1) * 1",
                lumber_proc,
                "board_foot",
                places=0,
                rounding_stage="procurement_ceiling_to_whole_board_foot",
            ),
            "release_oil_theoretical": calc_result(
                "RCB-FRM-011",
                "Theoretical form release oil.",
                "Q_oil,theory = A_form * f_oil",
                f"{decstr(contact_area)} * {decstr(q(factors['release_oil_per_contact_area']))}",
                release_oil_theoretical,
                "L",
            ),
            "release_oil_procurement": calc_result(
                "RCB-FRM-012",
                "Release oil procurement rounded upward to a whole litre.",
                "Q_oil,proc = ceil(Q_oil,theory / 1 L) * 1 L",
                f"ceil({decstr(release_oil_theoretical)} / 1) * 1",
                oil_proc,
                "L",
                places=0,
                rounding_stage="procurement_ceiling_to_whole_litre",
            ),
        },
        "excluded_surfaces": [
            "Top face at the monolithic slab interface",
            "Left support intersection",
            "Right support intersection",
            "Both beam end faces at monolithic supports",
        ],
    }

    divisor = q(reinforcement["unit_weight_rule"]["divisor"])
    longitudinal_results: dict[str, Any] = {}
    procurement_demands: dict[int, dict[str, Any]] = {}
    installed_length_by_diameter: dict[int, Decimal] = {}
    installed_weight_by_diameter: dict[int, Decimal] = {}

    for index, group in enumerate(reinforcement["longitudinal_bar_groups"], start=1):
        group_id = group["group_id"]
        diameter = int(q(group["diameter"]))
        count = int(q(group["bar_count"]))
        base = q(group["base_length"])
        left_add = q(group["left_anchorage_addition"])
        right_add = q(group["right_anchorage_addition"])
        hook_add = q(group["hook_addition"])
        lap_count = q(group["lap"]["count_per_bar"])
        lap_each = q(group["lap"]["length_each"])
        pieces_per_bar = int(q(group["fabrication"]["pieces_per_assembled_bar"]))

        effective_length = base + left_add + right_add + hook_add
        lap_addition = lap_count * lap_each
        physical_length_per_bar = effective_length + lap_addition
        piece_length = physical_length_per_bar / d(pieces_per_bar)
        total_pieces = count * pieces_per_bar
        total_length = physical_length_per_bar * d(count)
        assembly_check = piece_length * d(pieces_per_bar) - lap_addition
        uw = unit_weight(d(diameter), divisor)
        total_weight = total_length * uw

        prefix = f"RCB-LON-{index:03d}"
        longitudinal_results[group_id] = {
            "diameter": quantity_result(d(diameter), "mm", 0),
            "bar_count": quantity_result(d(count), "bar", 0),
            "effective_assembled_length_per_bar": calc_result(
                f"{prefix}-01",
                "Effective assembled bar length before lap overlap is added as physical steel.",
                "L_effective = L_base + L_anchor,left + L_anchor,right + L_hook",
                f"{decstr(base)} + {decstr(left_add)} + {decstr(right_add)} + {decstr(hook_add)}",
                effective_length,
                "m/bar",
            ),
            "lap_addition_per_bar": calc_result(
                f"{prefix}-02",
                "Physical steel added for the explicitly specified lap.",
                "L_lap,add = n_lap * L_lap,each",
                f"{decstr(lap_count)} * {decstr(lap_each)}",
                lap_addition,
                "m/bar",
            ),
            "physical_steel_length_per_bar": calc_result(
                f"{prefix}-03",
                "Physical steel length required for one assembled longitudinal bar.",
                "L_steel,bar = L_effective + L_lap,add",
                f"{decstr(effective_length)} + {decstr(lap_addition)}",
                physical_length_per_bar,
                "m/bar",
            ),
            "fabrication_piece_length": calc_result(
                f"{prefix}-04",
                "Equal fabrication piece length under the declared group policy.",
                "L_piece = L_steel,bar / n_piece,bar",
                f"{decstr(physical_length_per_bar)} / {pieces_per_bar}",
                piece_length,
                "m/piece",
            ),
            "fabrication_piece_count": calc_result(
                f"{prefix}-05",
                "Total fabrication-piece demand for the group.",
                "N_piece = N_bar * n_piece,bar",
                f"{count} * {pieces_per_bar}",
                d(total_pieces),
                "piece",
                places=0,
            ),
            "assembly_length_check": calc_result(
                f"{prefix}-06",
                "Independent assembly check. Sum of pieces less lap overlap must recover the effective bar length.",
                "L_effective,check = n_piece,bar * L_piece - L_lap,add",
                f"{pieces_per_bar} * {decstr(piece_length)} - {decstr(lap_addition)}",
                assembly_check,
                "m/bar",
            ),
            "theoretical_total_length": calc_result(
                f"{prefix}-07",
                "Theoretical physical steel length for the complete group.",
                "L_group = N_bar * L_steel,bar",
                f"{count} * {decstr(physical_length_per_bar)}",
                total_length,
                "m",
            ),
            "unit_weight": calc_result(
                f"{prefix}-08",
                "Theoretical unit weight under the declared project test rule.",
                "w_d = d_mm^2 / 162.2",
                f"{diameter}^2 / {decstr(divisor)}",
                uw,
                "kg/m",
            ),
            "theoretical_total_weight": calc_result(
                f"{prefix}-09",
                "Theoretical physical steel weight for the group.",
                "W_group = L_group * w_d",
                f"{decstr(total_length)} * {decstr(uw)}",
                total_weight,
                "kg",
            ),
            "lap_or_coupler_case": {
                "type": group["lap"]["type"],
                "lap_count_per_bar": quantity_result(lap_count, "lap/bar", 0),
                "lap_length_each": quantity_result(lap_each, "m/lap"),
                "coupler_count": quantity_result(D0, "coupler", 0),
            },
        }

        if diameter in procurement_demands:
            raise ValueError(
                "This support solver expects one identical cut length per diameter for RC-BEAM-001"
            )
        procurement_demands[diameter] = {
            "piece_length": piece_length,
            "piece_count": total_pieces,
            "source_groups": [group_id],
        }
        installed_length_by_diameter[diameter] = total_length
        installed_weight_by_diameter[diameter] = total_weight

    stirrup = reinforcement["stirrups"]
    stirrup_diameter = int(q(stirrup["diameter"]))
    cover = q(stirrup["cover_to_outside_of_stirrup"])
    hook_count = q(stirrup["hook_rule"]["hook_count"])
    hook_multiplier = q(stirrup["hook_rule"]["extension_multiplier"])
    bend_multiplier = q(stirrup["bend_deduction_rule"]["total_multiplier"])
    diameter_m = d(stirrup_diameter) / d(1000)

    clear_stirrup_width = b - d(2) * cover
    clear_stirrup_depth = overall_depth - d(2) * cover
    hook_each = hook_multiplier * diameter_m
    hook_total = hook_count * hook_each
    bend_deduction = bend_multiplier * diameter_m
    stirrup_cut_length = (
        d(2) * (clear_stirrup_width + clear_stirrup_depth)
        + hook_total
        - bend_deduction
    )

    zone_results: list[dict[str, Any]] = []
    all_positions: list[Decimal] = []
    for zone_index, zone in enumerate(stirrup["spacing_zones"], start=1):
        positions = generate_zone_positions(zone)
        all_positions.extend(positions)
        zone_results.append(
            {
                "zone_id": zone["zone_id"],
                "formula_id": f"RCB-STI-Z{zone_index:02d}",
                "description": f"Generate stirrup coordinates for spacing zone {zone['zone_id']}.",
                "symbolic_formula": "Generate x = x_start + k*s subject to the zone's explicit boundary inclusions.",
                "substitution": (
                    f"start={decstr(q(zone['start']))}, end={decstr(q(zone['end']))}, "
                    f"s={decstr(q(zone['spacing']))}, "
                    f"include_start={zone['include_start_boundary']}, "
                    f"include_end={zone['include_end_boundary']}"
                ),
                "rounding_stage": "none_integer_coordinate_generation",
                "count": quantity_result(d(len(positions)), "stirrup", 0),
                "positions": {
                    "values": [numeric_json(p) for p in positions],
                    "display_values": [f"{p:.3f}" for p in positions],
                    "unit": "m",
                },
                "include_start_boundary": zone["include_start_boundary"],
                "include_end_boundary": zone["include_end_boundary"],
            }
        )

    unique_positions = sorted(set(all_positions))
    duplicate_count = len(all_positions) - len(unique_positions)
    stirrup_count = len(unique_positions)
    stirrup_total_length = stirrup_cut_length * d(stirrup_count)
    stirrup_uw = unit_weight(d(stirrup_diameter), divisor)
    stirrup_total_weight = stirrup_total_length * stirrup_uw

    stirrup_results = {
        "clear_width": calc_result(
            "RCB-STI-001",
            "Stirrup width inside the specified cover lines.",
            "b_st = b_beam - 2*c",
            f"{decstr(b)} - 2*{decstr(cover)}",
            clear_stirrup_width,
            "m",
        ),
        "clear_depth": calc_result(
            "RCB-STI-002",
            "Stirrup depth inside the specified cover lines, using overall beam depth.",
            "D_st = D_overall - 2*c",
            f"{decstr(overall_depth)} - 2*{decstr(cover)}",
            clear_stirrup_depth,
            "m",
        ),
        "hook_extension_each": calc_result(
            "RCB-STI-003",
            "Project-specific hook extension per hook.",
            "L_hook,each = m_hook * d_b",
            f"{decstr(hook_multiplier)} * {decstr(diameter_m)}",
            hook_each,
            "m/hook",
        ),
        "hook_extension_total": calc_result(
            "RCB-STI-004",
            "Total hook extension for one stirrup.",
            "L_hook,total = n_hook * L_hook,each",
            f"{decstr(hook_count)} * {decstr(hook_each)}",
            hook_total,
            "m/stirrup",
        ),
        "bend_deduction": calc_result(
            "RCB-STI-005",
            "Project-specific aggregate bend deduction for one stirrup.",
            "Delta_bend = m_bend * d_b",
            f"{decstr(bend_multiplier)} * {decstr(diameter_m)}",
            bend_deduction,
            "m/stirrup",
        ),
        "cutting_length": calc_result(
            "RCB-STI-006",
            "Cutting length for one rectangular stirrup under the declared hook and bend rule.",
            "L_st = 2*(b_st + D_st) + L_hook,total - Delta_bend",
            f"2*({decstr(clear_stirrup_width)} + {decstr(clear_stirrup_depth)}) + {decstr(hook_total)} - {decstr(bend_deduction)}",
            stirrup_cut_length,
            "m/stirrup",
        ),
        "zones": zone_results,
        "sum_of_zone_counts_before_deduplication": calc_result(
            "RCB-STI-007",
            "Sum of all zone-generated stirrup positions before deduplication.",
            "N_zone,sum = sum(N_zone,i)",
            " + ".join(str(len(z["positions"]["values"])) for z in zone_results),
            d(len(all_positions)),
            "stirrup",
            places=0,
        ),
        "duplicate_boundary_count": calc_result(
            "RCB-STI-008",
            "Duplicate transition coordinates removed by the boundary policy.",
            "N_duplicate = N_zone,sum - size(unique(position_union))",
            f"{len(all_positions)} - {len(unique_positions)}",
            d(duplicate_count),
            "stirrup",
            places=0,
        ),
        "theoretical_count": calc_result(
            "RCB-STI-009",
            "Unique stirrup count after applying explicit transition-boundary ownership.",
            "N_st = size(unique(position_union))",
            f"size(unique({len(all_positions)} generated coordinates))",
            d(stirrup_count),
            "stirrup",
            places=0,
        ),
        "unique_positions": {
            "values": [numeric_json(p) for p in unique_positions],
            "display_values": [f"{p:.3f}" for p in unique_positions],
            "unit": "m",
        },
        "theoretical_total_length": calc_result(
            "RCB-STI-010",
            "Total theoretical stirrup steel length.",
            "L_st,total = N_st * L_st",
            f"{stirrup_count} * {decstr(stirrup_cut_length)}",
            stirrup_total_length,
            "m",
        ),
        "unit_weight": calc_result(
            "RCB-STI-011",
            "Theoretical 10 mm unit weight under the declared project test rule.",
            "w_10 = 10^2 / 162.2",
            f"{stirrup_diameter}^2 / {decstr(divisor)}",
            stirrup_uw,
            "kg/m",
        ),
        "theoretical_total_weight": calc_result(
            "RCB-STI-012",
            "Total theoretical stirrup weight.",
            "W_st = L_st,total * w_10",
            f"{decstr(stirrup_total_length)} * {decstr(stirrup_uw)}",
            stirrup_total_weight,
            "kg",
        ),
        "boundary_policy": stirrup["boundary_counting_policy"],
    }

    if stirrup_diameter in procurement_demands:
        raise ValueError("Stirrup diameter unexpectedly conflicts with a longitudinal demand")
    procurement_demands[stirrup_diameter] = {
        "piece_length": stirrup_cut_length,
        "piece_count": stirrup_count,
        "source_groups": [stirrup["group_id"]],
    }
    installed_length_by_diameter[stirrup_diameter] = stirrup_total_length
    installed_weight_by_diameter[stirrup_diameter] = stirrup_total_weight

    theoretical_total_length = sum(installed_length_by_diameter.values(), D0)
    theoretical_total_weight = sum(installed_weight_by_diameter.values(), D0)

    tie_factor = q(reinforcement["tie_wire"]["factor"])
    tie_theoretical = theoretical_total_weight * tie_factor
    tie_increment = q(reinforcement["tie_wire"]["procurement_increment"])
    tie_procurement = ceiling_to_increment(tie_theoretical, tie_increment)

    rebar_summary = {
        "longitudinal_groups": longitudinal_results,
        "stirrups": stirrup_results,
        "theoretical_installed_length": calc_result(
            "RCB-REB-001",
            "Total physical reinforcing-steel length, including the explicit lap overlap and all stirrups.",
            "L_rebar,total = sum(L_longitudinal groups) + L_stirrups",
            " + ".join(decstr(v) for _, v in sorted(installed_length_by_diameter.items())),
            theoretical_total_length,
            "m",
        ),
        "theoretical_installed_weight": calc_result(
            "RCB-REB-002",
            "Total theoretical installed reinforcing-steel weight.",
            "W_rebar,total = sum(W_by_diameter)",
            " + ".join(decstr(v) for _, v in sorted(installed_weight_by_diameter.items())),
            theoretical_total_weight,
            "kg",
        ),
        "tie_wire_theoretical": calc_result(
            "RCB-REB-003",
            "Theoretical tie-wire quantity based on installed rebar weight.",
            "W_tie,theory = W_rebar,total * f_tie",
            f"{decstr(theoretical_total_weight)} * {decstr(tie_factor)}",
            tie_theoretical,
            "kg",
        ),
        "tie_wire_procurement": calc_result(
            "RCB-REB-004",
            "Tie wire rounded upward to the declared procurement increment.",
            "W_tie,proc = ceil(W_tie,theory / increment) * increment",
            f"ceil({decstr(tie_theoretical)} / {decstr(tie_increment)}) * {decstr(tie_increment)}",
            tie_procurement,
            "kg",
            places=0,
            rounding_stage="procurement_ceiling_to_whole_kg",
        ),
    }

    kerf = q(procurement_policy["cut_kerf"])
    threshold = q(procurement_policy["reusable_offcut_threshold"])
    procurement_results: dict[str, Any] = {}
    purchased_length_total = D0
    purchased_weight_total = D0
    reusable_length_total = D0
    reusable_weight_total = D0
    scrap_length_total = D0
    scrap_weight_total = D0
    unresolved_piece_total = 0

    purchased_length_by_diameter: dict[int, Decimal] = {}
    purchased_weight_by_diameter: dict[int, Decimal] = {}

    for proc_index, diameter in enumerate(sorted(procurement_demands, reverse=True), start=1):
        demand = procurement_demands[diameter]
        piece_length = demand["piece_length"]
        piece_count = demand["piece_count"]
        stock_key = f"{diameter}_mm"
        stock_lengths = [q(item) for item in procurement_policy["available_stock_lengths_by_diameter"][stock_key]]
        patterns = optimize_identical_cuts(
            piece_length,
            piece_count,
            stock_lengths,
            kerf,
            threshold,
        )
        prefix = f"RCB-PRC-{proc_index:03d}"

        stock_rows: list[dict[str, Any]] = []
        purchased_length = D0
        reusable_length = D0
        scrap_length = D0
        produced_pieces = 0
        for stock_index, pattern in enumerate(patterns, start=1):
            cut_length_total = pattern.piece_length * d(pattern.pieces)
            kerf_length_total = pattern.kerf * d(pattern.pieces)
            bar_balance = (
                pattern.stock_length
                - cut_length_total
                - kerf_length_total
                - pattern.reusable
                - pattern.scrap
            )
            purchased_length += pattern.stock_length
            reusable_length += pattern.reusable
            scrap_length += pattern.scrap
            produced_pieces += pattern.pieces
            stock_rows.append(
                {
                    "stock_bar_id": f"D{diameter}-S{stock_index:02d}",
                    "formula_id": f"{prefix}-04-{stock_index:02d}",
                    "description": "Selected stock-bar pattern and its complete length balance.",
                    "symbolic_formula": (
                        "L_stock = sum(L_cut) + L_kerf + L_reusable + L_scrap"
                    ),
                    "substitution": (
                        f"{decstr(pattern.stock_length)} = "
                        f"({pattern.pieces} * {decstr(pattern.piece_length)}) + "
                        f"({pattern.pieces} * {decstr(pattern.kerf)}) + "
                        f"{decstr(pattern.reusable)} + {decstr(pattern.scrap)}"
                    ),
                    "rounding_stage": "reporting_only",
                    "stock_length": quantity_result(pattern.stock_length, "m"),
                    "cut_count": quantity_result(d(pattern.pieces), "piece", 0),
                    "cut_lengths": {
                        "values": [numeric_json(piece_length)] * pattern.pieces,
                        "display_values": [f"{piece_length:.3f}"] * pattern.pieces,
                        "unit": "m",
                    },
                    "used_length": quantity_result(cut_length_total, "m"),
                    "kerf_length": quantity_result(kerf_length_total, "m"),
                    "reusable_offcut": quantity_result(pattern.reusable, "m"),
                    "scrap": quantity_result(pattern.scrap, "m"),
                    "length_balance_difference": quantity_result(bar_balance, "m"),
                }
            )

        required_cut_length = piece_length * d(piece_count)
        unresolved_pieces = piece_count - produced_pieces
        uw = unit_weight(d(diameter), divisor)
        purchased_weight = purchased_length * uw
        reusable_weight = reusable_length * uw
        scrap_weight = scrap_length * uw
        installed_length = installed_length_by_diameter[diameter]
        installed_weight = installed_weight_by_diameter[diameter]

        if required_cut_length != installed_length:
            raise AssertionError(
                f"Diameter {diameter}: procurement cut demand does not equal theoretical installed length"
            )

        procurement_results[f"{diameter}_mm"] = {
            "source_groups": demand["source_groups"],
            "available_stock_lengths": {
                "values": [numeric_json(v) for v in stock_lengths],
                "unit": "m",
            },
            "piece_length": calc_result(
                f"{prefix}-01",
                "Uniform cut length used by the diameter-specific cutting plan.",
                "L_piece = source demand cut length",
                decstr(piece_length),
                piece_length,
                "m/piece",
            ),
            "required_piece_count": calc_result(
                f"{prefix}-02",
                "Required cut-piece count for this diameter.",
                "N_required = sum(source piece counts)",
                str(piece_count),
                d(piece_count),
                "piece",
                places=0,
            ),
            "required_cut_length": calc_result(
                f"{prefix}-03",
                "Total physical cut length required for this diameter.",
                "L_required = N_required * L_piece",
                f"{piece_count} * {decstr(piece_length)}",
                required_cut_length,
                "m",
            ),
            "optimizer_result": {
                "formula_id": f"{prefix}-04",
                "description": "Exact-piece cutting plan selected by the declared lexicographic procurement objective.",
                "symbolic_formula": (
                    "arg min_plan (L_purchased, N_stock, L_scrap, max(L_offcut), signature) "
                    "subject to exact piece demand"
                ),
                "substitution": (
                    f"piece_length={decstr(piece_length)} m, piece_count={piece_count}, "
                    f"stock_lengths=[{', '.join(decstr(v) for v in stock_lengths)}] m, "
                    f"kerf={decstr(kerf)} m/cut, reusable_threshold={decstr(threshold)} m"
                ),
                "rounding_stage": "none_discrete_selection",
                "objective_order": procurement_policy["optimization_objective_order"],
                "stock_bars": stock_rows,
            },
            "stock_bar_count": calc_result(
                f"{prefix}-05",
                "Count of purchased commercial stock bars in the selected plan.",
                "N_stock = count(selected stock bars)",
                str(len(patterns)),
                d(len(patterns)),
                "stock_bar",
                places=0,
            ),
            "purchased_length": calc_result(
                f"{prefix}-06",
                "Total purchased commercial stock length for this diameter.",
                "L_purchased = sum(L_stock bars)",
                " + ".join(decstr(p.stock_length) for p in patterns),
                purchased_length,
                "m",
            ),
            "purchased_weight": calc_result(
                f"{prefix}-07",
                "Purchased weight for this diameter.",
                "W_purchased = L_purchased * w_d",
                f"{decstr(purchased_length)} * {decstr(uw)}",
                purchased_weight,
                "kg",
            ),
            "reusable_offcut_length": calc_result(
                f"{prefix}-08",
                "Offcut length at or above the declared reusable threshold.",
                "L_reusable = sum(offcut where offcut >= threshold)",
                " + ".join(decstr(p.reusable) for p in patterns),
                reusable_length,
                "m",
            ),
            "reusable_offcut_weight": calc_result(
                f"{prefix}-09",
                "Reusable offcut weight for this diameter.",
                "W_reusable = L_reusable * w_d",
                f"{decstr(reusable_length)} * {decstr(uw)}",
                reusable_weight,
                "kg",
            ),
            "scrap_length": calc_result(
                f"{prefix}-10",
                "Non-reusable offcut length below the declared threshold.",
                "L_scrap = sum(offcut where 0 < offcut < threshold)",
                " + ".join(decstr(p.scrap) for p in patterns),
                scrap_length,
                "m",
            ),
            "scrap_weight": calc_result(
                f"{prefix}-11",
                "Non-reusable scrap weight for this diameter.",
                "W_scrap = L_scrap * w_d",
                f"{decstr(scrap_length)} * {decstr(uw)}",
                scrap_weight,
                "kg",
            ),
            "unresolved_demand": calc_result(
                f"{prefix}-12",
                "Cut pieces not satisfied by the selected plan.",
                "N_unresolved = N_required - N_produced",
                f"{piece_count} - {produced_pieces}",
                d(unresolved_pieces),
                "piece",
                places=0,
            ),
            "length_reconciliation_difference": calc_result(
                f"{prefix}-13",
                "Purchased length less required cut length, reusable offcut, and scrap.",
                "Delta_L = L_purchased - L_required - L_reusable - L_scrap",
                f"{decstr(purchased_length)} - {decstr(required_cut_length)} - {decstr(reusable_length)} - {decstr(scrap_length)}",
                purchased_length - required_cut_length - reusable_length - scrap_length,
                "m",
            ),
            "weight_reconciliation_difference": calc_result(
                f"{prefix}-14",
                "Purchased weight less installed, reusable offcut, and scrap weight.",
                "Delta_W = W_purchased - W_installed - W_reusable - W_scrap",
                f"{decstr(purchased_weight)} - {decstr(installed_weight)} - {decstr(reusable_weight)} - {decstr(scrap_weight)}",
                purchased_weight - installed_weight - reusable_weight - scrap_weight,
                "kg",
            ),
        }

        purchased_length_total += purchased_length
        purchased_weight_total += purchased_weight
        reusable_length_total += reusable_length
        reusable_weight_total += reusable_weight
        scrap_length_total += scrap_length
        scrap_weight_total += scrap_weight
        unresolved_piece_total += unresolved_pieces
        purchased_length_by_diameter[diameter] = purchased_length
        purchased_weight_by_diameter[diameter] = purchased_weight

    procurement_summary = {
        "by_diameter": procurement_results,
        "total_required_cut_length": calc_result(
            "RCB-PRC-TOT-001",
            "Total theoretical cut length across all diameters.",
            "L_required,total = sum(L_required,d)",
            " + ".join(decstr(installed_length_by_diameter[k]) for k in sorted(installed_length_by_diameter, reverse=True)),
            theoretical_total_length,
            "m",
        ),
        "total_purchased_length": calc_result(
            "RCB-PRC-TOT-002",
            "Total purchased stock length across all diameters.",
            "L_purchased,total = sum(L_purchased,d)",
            " + ".join(decstr(purchased_length_by_diameter[k]) for k in sorted(purchased_length_by_diameter, reverse=True)),
            purchased_length_total,
            "m",
        ),
        "total_purchased_weight": calc_result(
            "RCB-PRC-TOT-003",
            "Total purchased reinforcing-steel weight across all diameters.",
            "W_purchased,total = sum(W_purchased,d)",
            " + ".join(decstr(purchased_weight_by_diameter[k]) for k in sorted(purchased_weight_by_diameter, reverse=True)),
            purchased_weight_total,
            "kg",
        ),
        "total_reusable_offcut_length": calc_result(
            "RCB-PRC-TOT-004",
            "Total reusable offcut length across all diameters.",
            "L_reusable,total = sum(L_reusable,d)",
            decstr(reusable_length_total),
            reusable_length_total,
            "m",
        ),
        "total_reusable_offcut_weight": calc_result(
            "RCB-PRC-TOT-005",
            "Total reusable offcut weight across all diameters.",
            "W_reusable,total = sum(W_reusable,d)",
            decstr(reusable_weight_total),
            reusable_weight_total,
            "kg",
        ),
        "total_scrap_length": calc_result(
            "RCB-PRC-TOT-006",
            "Total non-reusable scrap length across all diameters.",
            "L_scrap,total = sum(L_scrap,d)",
            decstr(scrap_length_total),
            scrap_length_total,
            "m",
        ),
        "total_scrap_weight": calc_result(
            "RCB-PRC-TOT-007",
            "Total non-reusable scrap weight across all diameters.",
            "W_scrap,total = sum(W_scrap,d)",
            decstr(scrap_weight_total),
            scrap_weight_total,
            "kg",
        ),
        "total_unresolved_demand": calc_result(
            "RCB-PRC-TOT-008",
            "Total unresolved cut-piece demand.",
            "N_unresolved,total = sum(N_unresolved,d)",
            str(unresolved_piece_total),
            d(unresolved_piece_total),
            "piece",
            places=0,
        ),
        "length_reconciliation_difference": calc_result(
            "RCB-PRC-TOT-009",
            "Overall purchased-length reconciliation.",
            "Delta_L,total = L_purchased,total - L_required,total - L_reusable,total - L_scrap,total",
            f"{decstr(purchased_length_total)} - {decstr(theoretical_total_length)} - {decstr(reusable_length_total)} - {decstr(scrap_length_total)}",
            purchased_length_total - theoretical_total_length - reusable_length_total - scrap_length_total,
            "m",
        ),
        "weight_reconciliation_difference": calc_result(
            "RCB-PRC-TOT-010",
            "Overall purchased-weight reconciliation.",
            "Delta_W,total = W_purchased,total - W_installed,total - W_reusable,total - W_scrap,total",
            f"{decstr(purchased_weight_total)} - {decstr(theoretical_total_weight)} - {decstr(reusable_weight_total)} - {decstr(scrap_weight_total)}",
            purchased_weight_total - theoretical_total_weight - reusable_weight_total - scrap_weight_total,
            "kg",
        ),
        "reusable_offcut_threshold": quantity_result(threshold, "m"),
        "cut_kerf": quantity_result(kerf, "m/cut"),
        "reusable_offcut_cost_credit_applied": procurement_policy[
            "reusable_offcut_cost_credit_in_current_case"
        ],
    }

    # Resource ledger quantities.
    material_quantity_map: dict[str, tuple[Decimal, str]] = {
        "concrete_procurement_volume": (procured_concrete, "m^3"),
        "plywood_procurement_quantity": (plywood_proc, "sheet"),
        "form_lumber_procurement_quantity": (lumber_proc, "board_foot"),
        "release_oil_procurement_quantity": (oil_proc, "L"),
        "20_mm_purchased_weight": (purchased_weight_by_diameter[20], "kg"),
        "16_mm_purchased_weight": (purchased_weight_by_diameter[16], "kg"),
        "10_mm_purchased_weight": (purchased_weight_by_diameter[10], "kg"),
        "tie_wire_procurement_quantity": (tie_procurement, "kg"),
    }

    material_ledger: list[dict[str, Any]] = []
    material_subtotal = D0
    for index, rate_row in enumerate(resources["material_rates"], start=1):
        quantity, quantity_unit = material_quantity_map[rate_row["quantity_basis"]]
        rate = q(rate_row["rate"])
        amount_unrounded = quantity * rate
        amount_reported = quantize_places(amount_unrounded, 2)
        material_subtotal += amount_reported
        material_ledger.append(
            {
                "resource_id": rate_row["resource_id"],
                "description": rate_row["description"],
                "quantity_basis": rate_row["quantity_basis"],
                "quantity": quantity_result(quantity, quantity_unit),
                "rate": quantity_result(rate, rate_row["rate"]["unit"], 2),
                "amount": money_result(
                    f"RCB-CST-MAT-{index:03d}",
                    f"Direct material cost for {rate_row['description']}.",
                    "C_material,line = Q_procurement * rate",
                    f"{decstr(quantity)} * {decstr(rate)}",
                    amount_unrounded,
                ),
            }
        )

    labor_basis_map: dict[str, tuple[Decimal, str]] = {
        "concrete_required_volume": (required_concrete, "m^3"),
        "formwork_contact_area": (contact_area, "m^2"),
        "theoretical_installed_rebar_weight": (theoretical_total_weight, "kg"),
    }
    labor_ledger: list[dict[str, Any]] = []
    labor_subtotal = D0
    for index, row in enumerate(resources["labor_resources"], start=1):
        basis, basis_unit = labor_basis_map[row["quantity_basis"]]
        productivity = q(row["productivity"])
        rate = q(row["rate"])
        crew_days = basis / productivity
        amount_unrounded = crew_days * rate
        amount_reported = quantize_places(amount_unrounded, 2)
        labor_subtotal += amount_reported
        labor_ledger.append(
            {
                "resource_id": row["resource_id"],
                "description": row["description"],
                "quantity_basis": row["quantity_basis"],
                "basis_quantity": quantity_result(basis, basis_unit),
                "productivity": quantity_result(
                    productivity, row["productivity"]["unit"], 6
                ),
                "crew_days": calc_result(
                    f"RCB-CST-LAB-{index:03d}-A",
                    f"Crew usage for {row['description']}.",
                    "T_crew = Q_basis / productivity",
                    f"{decstr(basis)} / {decstr(productivity)}",
                    crew_days,
                    "crew-day",
                ),
                "rate": quantity_result(rate, row["rate"]["unit"], 2),
                "amount": money_result(
                    f"RCB-CST-LAB-{index:03d}-B",
                    f"Direct labor cost for {row['description']}.",
                    "C_labor,line = T_crew * rate",
                    f"{decstr(crew_days)} * {decstr(rate)}",
                    amount_unrounded,
                ),
            }
        )

    equipment_basis_map = labor_basis_map
    equipment_ledger: list[dict[str, Any]] = []
    equipment_subtotal = D0
    for index, row in enumerate(resources["equipment_resources"], start=1):
        basis, basis_unit = equipment_basis_map[row["quantity_basis"]]
        productivity = q(row["productivity"])
        minimum = q(row["minimum_charge"])
        computed_days = basis / productivity
        charged_days = max(computed_days, minimum)
        rate = q(row["rate"])
        amount_unrounded = charged_days * rate
        amount_reported = quantize_places(amount_unrounded, 2)
        equipment_subtotal += amount_reported
        equipment_ledger.append(
            {
                "resource_id": row["resource_id"],
                "description": row["description"],
                "quantity_basis": row["quantity_basis"],
                "basis_quantity": quantity_result(basis, basis_unit),
                "productivity": quantity_result(
                    productivity, row["productivity"]["unit"], 6
                ),
                "computed_unit_days": calc_result(
                    f"RCB-CST-EQ-{index:03d}-A",
                    f"Calculated equipment usage before minimum charge for {row['description']}.",
                    "T_calc = Q_basis / productivity",
                    f"{decstr(basis)} / {decstr(productivity)}",
                    computed_days,
                    "unit-day",
                ),
                "minimum_charge": quantity_result(minimum, "unit-day"),
                "charged_unit_days": calc_result(
                    f"RCB-CST-EQ-{index:03d}-B",
                    f"Charged equipment usage for {row['description']}.",
                    "T_charge = max(T_calc, T_min)",
                    f"max({decstr(computed_days)}, {decstr(minimum)})",
                    charged_days,
                    "unit-day",
                ),
                "rate": quantity_result(rate, row["rate"]["unit"], 2),
                "amount": money_result(
                    f"RCB-CST-EQ-{index:03d}-C",
                    f"Direct equipment cost for {row['description']}.",
                    "C_equipment,line = T_charge * rate",
                    f"{decstr(charged_days)} * {decstr(rate)}",
                    amount_unrounded,
                ),
            }
        )

    direct_cost_total = material_subtotal + labor_subtotal + equipment_subtotal
    cost_results = {
        "materials": material_ledger,
        "labor": labor_ledger,
        "equipment": equipment_ledger,
        "direct_material_cost": money_result(
            "RCB-CST-SUB-001",
            "Direct material subtotal as the sum of reported material line amounts.",
            "C_material = sum(reported material line amounts)",
            " + ".join(row["amount"]["display"] for row in material_ledger),
            material_subtotal,
        ),
        "direct_labor_cost": money_result(
            "RCB-CST-SUB-002",
            "Direct labor subtotal as the sum of reported labor line amounts.",
            "C_labor = sum(reported labor line amounts)",
            " + ".join(row["amount"]["display"] for row in labor_ledger),
            labor_subtotal,
        ),
        "direct_equipment_cost": money_result(
            "RCB-CST-SUB-003",
            "Direct equipment subtotal as the sum of reported equipment line amounts.",
            "C_equipment = sum(reported equipment line amounts)",
            " + ".join(row["amount"]["display"] for row in equipment_ledger),
            equipment_subtotal,
        ),
        "total_direct_cost": money_result(
            "RCB-CST-TOT-001",
            "Total direct cost with no overhead, tax, or profit.",
            "C_direct = C_material + C_labor + C_equipment",
            f"{material_subtotal:.2f} + {labor_subtotal:.2f} + {equipment_subtotal:.2f}",
            direct_cost_total,
        ),
        "excluded_costs": {
            "overhead": quantity_result(D0, "PHP", 2),
            "tax": quantity_result(D0, "PHP", 2),
            "profit": quantity_result(D0, "PHP", 2),
        },
        "rounding_policy": resources["cost_rounding_policy"],
    }

    reconciliations = {
        "geometry_net_depth": {
            "formula_id": "RCB-REC-001",
            "description": "Check the explicit net beam depth against overall depth less slab thickness.",
            "symbolic_formula": "Delta_D = (D_overall - t_slab) - D_net,input",
            "substitution": (
                f"({decstr(overall_depth)} - {decstr(slab_t)}) - {decstr(net_depth)}"
            ),
            "rounding_stage": "reporting_only",
            "difference": quantity_result(computed_net_depth - net_depth, "m"),
            "status": "PASS" if computed_net_depth == net_depth else "FAIL",
        },
        "concrete_two_method_check": {
            "formula_id": "RCB-REC-002",
            "description": "Compare net concrete from deductions with the direct beam-drop prism method.",
            "symbolic_formula": "Delta_V = V_net,deduction - V_net,direct",
            "substitution": (
                f"{decstr(net_concrete)} - {decstr(direct_net_concrete)}"
            ),
            "rounding_stage": "reporting_only",
            "difference": quantity_result(net_concrete - direct_net_concrete, "m^3"),
            "status": "PASS" if net_concrete == direct_net_concrete else "FAIL",
        },
        "formwork_two_method_check": {
            "formula_id": "RCB-REC-003",
            "description": "Compare component-sum formwork with the independent perimeter method.",
            "symbolic_formula": "Delta_A = A_form,components - A_form,perimeter",
            "substitution": f"{decstr(contact_area)} - {decstr(contact_area_check)}",
            "rounding_stage": "reporting_only",
            "difference": quantity_result(contact_area - contact_area_check, "m^2"),
            "status": "PASS" if contact_area == contact_area_check else "FAIL",
        },
        "stirrup_boundary_check": {
            "formula_id": "RCB-REC-004",
            "description": "Confirm that spacing-zone transition coordinates are not double-counted.",
            "symbolic_formula": "N_duplicate = N_generated - N_unique",
            "substitution": f"{len(all_positions)} - {len(unique_positions)}",
            "rounding_stage": "none_integer_count",
            "duplicate_count": quantity_result(d(duplicate_count), "stirrup", 0),
            "status": "PASS" if duplicate_count == 0 else "FAIL",
        },
        "rebar_length_check": {
            "formula_id": "RCB-REC-005",
            "description": "Reconcile purchased stock length with cuts, reusable offcuts, and scrap.",
            "symbolic_formula": (
                "Delta_L = L_purchased - L_installed - L_reusable - L_scrap"
            ),
            "substitution": (
                f"{decstr(purchased_length_total)} - {decstr(theoretical_total_length)} - "
                f"{decstr(reusable_length_total)} - {decstr(scrap_length_total)}"
            ),
            "rounding_stage": "reporting_only",
            "difference": quantity_result(
                purchased_length_total
                - theoretical_total_length
                - reusable_length_total
                - scrap_length_total,
                "m",
            ),
            "status": "PASS"
            if purchased_length_total
            == theoretical_total_length + reusable_length_total + scrap_length_total
            else "FAIL",
        },
        "rebar_weight_check": {
            "formula_id": "RCB-REC-006",
            "description": "Reconcile purchased stock weight with installed steel, reusable offcuts, and scrap.",
            "symbolic_formula": (
                "Delta_W = W_purchased - W_installed - W_reusable - W_scrap"
            ),
            "substitution": (
                f"{decstr(purchased_weight_total)} - {decstr(theoretical_total_weight)} - "
                f"{decstr(reusable_weight_total)} - {decstr(scrap_weight_total)}"
            ),
            "rounding_stage": "reporting_only",
            "difference": quantity_result(
                purchased_weight_total
                - theoretical_total_weight
                - reusable_weight_total
                - scrap_weight_total,
                "kg",
            ),
            "status": "PASS"
            if purchased_weight_total
            == theoretical_total_weight + reusable_weight_total + scrap_weight_total
            else "FAIL",
        },
        "unresolved_demand_check": {
            "formula_id": "RCB-REC-007",
            "description": "Confirm that every required reinforcing-steel cut piece is assigned to stock.",
            "symbolic_formula": "N_unresolved,total = sum(N_required,d - N_produced,d)",
            "substitution": str(unresolved_piece_total),
            "rounding_stage": "none_integer_count",
            "unresolved": quantity_result(d(unresolved_piece_total), "piece", 0),
            "status": "PASS" if unresolved_piece_total == 0 else "FAIL",
        },
        "cost_check": {
            "formula_id": "RCB-REC-008",
            "description": "Reconcile total direct cost with reported material, labor, and equipment subtotals.",
            "symbolic_formula": (
                "Delta_C = C_direct - C_material - C_labor - C_equipment"
            ),
            "substitution": (
                f"{direct_cost_total:.2f} - {material_subtotal:.2f} - "
                f"{labor_subtotal:.2f} - {equipment_subtotal:.2f}"
            ),
            "rounding_stage": "reported_category_subtotals",
            "difference": quantity_result(
                direct_cost_total
                - material_subtotal
                - labor_subtotal
                - equipment_subtotal,
                "PHP",
                2,
            ),
            "status": "PASS"
            if direct_cost_total
            == material_subtotal + labor_subtotal + equipment_subtotal
            else "FAIL",
        },
    }

    acceptance_status = (
        "PASS"
        if all(item["status"] == "PASS" for item in reconciliations.values())
        else "FAIL"
    )

    payload: dict[str, Any] = {
        "schema_version": "0.1.0",
        "case_id": source["case_id"],
        "case_title": source["case_title"],
        "status": acceptance_status,
        "calculation_scope": {
            "structural_analysis_performed": False,
            "reinforcement_design_performed": False,
            "quantities_and_direct_cost_only": True,
        },
        "rounding_policy": source["reporting_policy"],
        "geometry": geometry_results,
        "concrete": concrete_results,
        "formwork": formwork_results,
        "reinforcement": rebar_summary,
        "procurement": procurement_summary,
        "resources_and_costs": cost_results,
        "reconciliations": reconciliations,
    }

    payload = json_safe(payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    payload["calculation_payload_sha256"] = payload_hash
    return payload


def cell(entry: dict[str, Any]) -> str:
    return f"{entry['display']} {entry['unit']}"


def calc_table(entries: Iterable[dict[str, Any]]) -> str:
    lines = [
        "| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |",
        "|---|---|---|---|---:|---:|",
    ]
    for entry in entries:
        lines.append(
            "| {id} | {desc} | `{symbol}` | `{sub}` | {unrounded} {unit} | {display} {unit} |".format(
                id=entry["formula_id"],
                desc=entry["description"],
                symbol=entry["symbolic_formula"].replace("|", "\\|"),
                sub=entry["substitution"].replace("|", "\\|"),
                unrounded=entry["unrounded_value"],
                display=entry["display"],
                unit=entry["unit"],
            )
        )
    return "\n".join(lines)


def render_markdown(source: dict[str, Any], expected: dict[str, Any]) -> str:
    g = expected["geometry"]
    c = expected["concrete"]
    f = expected["formwork"]
    r = expected["reinforcement"]
    p = expected["procurement"]
    costs = expected["resources_and_costs"]
    rec = expected["reconciliations"]

    lines: list[str] = []
    lines.append("# RC-BEAM-001: Golden reinforced-concrete beam reference case")
    lines.append("")
    lines.append(f"**Acceptance status:** {expected['status']}")
    lines.append("")
    lines.append(
        "**Classification:** RC-BEAM-001 is a proposed normative target for the replacement solver architecture and is not a regression expectation for the frozen legacy solver."
    )
    lines.append("")
    lines.append(
        "This document is the independently calculated acceptance reference for one rectangular, monolithic reinforced-concrete beam. "
        "It is a quantity, procurement, and direct-cost case only. No structural analysis, bar sizing, spacing design, or code compliance inference is performed."
    )
    lines.append("")
    lines.append(
        f"Calculation payload SHA-256: `{expected['calculation_payload_sha256']}`"
    )
    lines.append("")
    lines.append("## 1. Source facts and explicit assumptions")
    lines.append("")
    lines.append("All values in this section are inputs or declared policies, not calculated answers.")
    lines.append("")
    lines.append("### 1.1 Geometry and ownership of intersections")
    lines.append("")
    lines.append("```text")
    lines.append("outer face                                                     outer face")
    lines.append("|<-- left support 0.400 m -->|<------ clear span 5.400 m ------>|<-- right support 0.500 m -->|")
    lines.append("|============================|==================================|==============================|")
    lines.append("                    x = 0.000 m                         x = 5.400 m")
    lines.append("                    clear-span coordinates for stirrups")
    lines.append("")
    lines.append("Beam section: width 0.300 m, overall depth 0.600 m")
    lines.append("Monolithic slab: thickness 0.150 m")
    lines.append("Explicit beam-below-slab depth: 0.450 m")
    lines.append("```")
    lines.append("")
    lines.append(
        "Concrete ownership is explicit: support concrete owns both beam-support intersections, and slab concrete owns the 0.150 m slab layer across the clear-span beam strip. "
        "The beam quantity therefore retains only the 0.450 m drop below the slab over the 5.400 m clear span."
    )
    lines.append("")
    lines.append("### 1.2 Concrete, formwork, reinforcement, and procurement policies")
    lines.append("")
    lines.extend(
        [
            "- Concrete waste is a project-specific 3.000000% of net measured beam concrete.",
            "- Ready-mix procurement is rounded upward to 0.100000 m^3 increments.",
            "- Formwork includes the soffit and two beam-drop sides over the clear span. The top face, both support intersections, and both monolithic end faces are excluded.",
            "- Longitudinal reinforcement is supplied as source facts: 3 bottom 20 mm bars and 2 top 16 mm bars. The top bars each have one explicit 0.800000 m lap and are fabricated as two equal pieces.",
            "- Stirrups are 10 mm bars with 0.040000 m cover, two 10db hook extensions, and a project-specific aggregate 12db bend deduction. No additional centerline or bend-radius adjustment is inferred.",
            "- Commercial stock lengths are 6.000000 m, 9.000000 m, and 12.000000 m for all three diameters.",
            "- Cutting kerf is explicitly 0.000000 m/cut and is applied once per produced cut piece. Offcuts at least 1.000000 m long are reusable; shorter positive remnants are scrap.",
            "- Reusable offcuts receive no credit against this case's material cost.",
            "- Rates and productivity values are illustrative project test assumptions. Overhead, tax, and profit are excluded.",
        ]
    )
    lines.append("")
    lines.append("## 2. Geometry checks")
    lines.append("")
    lines.append(
        calc_table(
            [
                g["net_depth_check"],
                g["outer_face_to_outer_face_length"],
                g["support_centerline_span"],
                g["net_depth_difference"],
            ]
        )
    )
    lines.append("")
    lines.append(
        f"The supplied net depth is {cell(g['explicit_net_depth'])}. The calculated difference is {cell(g['net_depth_difference'])}, so the redundant geometry facts reconcile."
    )
    lines.append("")
    lines.append("## 3. Concrete takeoff")
    lines.append("")
    lines.append(
        calc_table(
            [
                c["gross_volume"],
                c["left_support_intersection"],
                c["right_support_intersection"],
                c["support_intersection_deduction"],
                c["clear_span_overall_depth_volume"],
                c["slab_intersection_deduction"],
                c["net_measured_volume"],
                c["independent_direct_net_volume"],
                c["waste_quantity"],
                c["required_quantity"],
                c["procurement_quantity"],
                c["procurement_rounding_excess"],
            ]
        )
    )
    lines.append("")
    lines.append("Concrete quantity stages remain separate:")
    lines.append("")
    lines.append(
        f"- Gross full-prism volume: {cell(c['gross_volume'])}\n"
        f"- Net measured beam volume: {cell(c['net_measured_volume'])}\n"
        f"- Waste quantity: {cell(c['waste_quantity'])}\n"
        f"- Required quantity before procurement rounding: {cell(c['required_quantity'])}\n"
        f"- Procured quantity: {cell(c['procurement_quantity'])}\n"
        f"- Commercial rounding excess: {cell(c['procurement_rounding_excess'])}"
    )
    lines.append("")
    lines.append(
        f"Independent check: gross-minus-deductions and direct net-prism methods differ by {cell(rec['concrete_two_method_check']['difference'])}. Status: {rec['concrete_two_method_check']['status']}."
    )
    lines.append("")
    lines.append("## 4. Formwork takeoff")
    lines.append("")
    lines.append(
        calc_table(
            [
                f["soffit_area"],
                f["left_side_area"],
                f["right_side_area"],
                f["end_form_area"],
                f["total_contact_area"],
                f["independent_contact_area"],
            ]
        )
    )
    lines.append("")
    lines.append("Excluded surfaces:")
    lines.append("")
    for surface in f["excluded_surfaces"]:
        lines.append(f"- {surface}")
    lines.append("")
    lines.append(
        "Formwork contact area is reported only in m^2. It is not added to, converted into, or otherwise merged with concrete volume."
    )
    lines.append("")
    lines.append("### 4.1 Formwork material resources")
    lines.append("")
    lines.append(
        calc_table(
            [
                f["resources"]["plywood_theoretical"],
                f["resources"]["plywood_procurement"],
                f["resources"]["form_lumber_theoretical"],
                f["resources"]["form_lumber_procurement"],
                f["resources"]["release_oil_theoretical"],
                f["resources"]["release_oil_procurement"],
            ]
        )
    )
    lines.append("")
    lines.append(
        f"Independent formwork check differs by {cell(rec['formwork_two_method_check']['difference'])}. Status: {rec['formwork_two_method_check']['status']}."
    )
    lines.append("")
    lines.append("## 5. Longitudinal reinforcement")
    lines.append("")
    for group_id, group in r["longitudinal_groups"].items():
        lines.append(f"### 5.{1 if group_id.startswith('L1') else 2} {group_id}")
        lines.append("")
        lines.append(
            f"Diameter: {cell(group['diameter'])}; assembled bar count: {cell(group['bar_count'])}; lap case: `{group['lap_or_coupler_case']['type']}`."
        )
        lines.append("")
        lines.append(
            calc_table(
                [
                    group["effective_assembled_length_per_bar"],
                    group["lap_addition_per_bar"],
                    group["physical_steel_length_per_bar"],
                    group["fabrication_piece_length"],
                    group["fabrication_piece_count"],
                    group["assembly_length_check"],
                    group["theoretical_total_length"],
                    group["unit_weight"],
                    group["theoretical_total_weight"],
                ]
            )
        )
        lines.append("")
    lines.append(
        "The 16 mm top group is the explicit lap case. Each assembled bar has an effective length of "
        f"{cell(r['longitudinal_groups']['L2_TOP_16_LAPPED']['effective_assembled_length_per_bar'])}, "
        f"uses two {cell(r['longitudinal_groups']['L2_TOP_16_LAPPED']['fabrication_piece_length'])} pieces, and subtracts the "
        f"{cell(r['longitudinal_groups']['L2_TOP_16_LAPPED']['lap_addition_per_bar'])} overlap when checking assembled length."
    )
    lines.append("")
    lines.append("## 6. Stirrups")
    lines.append("")
    lines.append(
        calc_table(
            [
                r["stirrups"]["clear_width"],
                r["stirrups"]["clear_depth"],
                r["stirrups"]["hook_extension_each"],
                r["stirrups"]["hook_extension_total"],
                r["stirrups"]["bend_deduction"],
                r["stirrups"]["cutting_length"],
            ]
        )
    )
    lines.append("")
    lines.append("### 6.1 Spacing zones and transition ownership")
    lines.append("")
    lines.append(
        "Zone coordinates use `x = x_start + k*s` with each zone's explicit start/end ownership. "
        "The table shows the numerical substitution and the generated unrounded coordinate set."
    )
    lines.append("")
    lines.append("| Formula ID | Zone | Boundary rule | Spacing | Numerical substitution | Count | Generated x-coordinates (m) |")
    lines.append("|---|---|---|---:|---|---:|---|")
    source_zones = {z["zone_id"]: z for z in source["reinforcement_policy"]["stirrups"]["spacing_zones"]}
    for zone in r["stirrups"]["zones"]:
        src = source_zones[zone["zone_id"]]
        boundary = (
            ("[" if src["include_start_boundary"] else "(")
            + f"{q(src['start']):.3f}, {q(src['end']):.3f}"
            + ("]" if src["include_end_boundary"] else ")")
        )
        lines.append(
            f"| {zone['formula_id']} | {zone['zone_id']} | `{boundary}` | {q(src['spacing']):.3f} m | "
            f"`{zone['substitution']}` | {zone['count']['display']} {zone['count']['unit']} | "
            + ", ".join(zone["positions"]["display_values"])
            + " |"
        )
    lines.append("")
    lines.append(
        calc_table(
            [
                r["stirrups"]["sum_of_zone_counts_before_deduplication"],
                r["stirrups"]["duplicate_boundary_count"],
                r["stirrups"]["theoretical_count"],
                r["stirrups"]["theoretical_total_length"],
                r["stirrups"]["unit_weight"],
                r["stirrups"]["theoretical_total_weight"],
            ]
        )
    )
    lines.append("")
    lines.append(
        f"Boundary result: {r['stirrups']['duplicate_boundary_count']['display']} duplicate coordinates and {r['stirrups']['theoretical_count']['display']} unique stirrups. Status: {rec['stirrup_boundary_check']['status']}."
    )
    lines.append("")
    lines.append("## 7. Reinforcement totals before procurement")
    lines.append("")
    lines.append(
        calc_table(
            [
                r["theoretical_installed_length"],
                r["theoretical_installed_weight"],
                r["tie_wire_theoretical"],
                r["tie_wire_procurement"],
            ]
        )
    )
    lines.append("")
    lines.append("## 8. Rebar procurement and cutting schedule")
    lines.append("")
    lines.append(
        "The optimizer must satisfy every cut piece exactly. It first minimizes purchased stock length, then stock-bar count, non-reusable scrap, the largest individual offcut, and finally a deterministic pattern signature."
    )
    lines.append("")
    for diameter_index, (diameter_key, result) in enumerate(p["by_diameter"].items(), start=1):
        lines.append(f"### 8.{diameter_index} Diameter {diameter_key.replace('_', ' ')}")
        lines.append("")
        lines.append(
            f"Available stock lengths: {', '.join(f'{v:.3f}' for v in result['available_stock_lengths']['values'])} m. "
            f"Required demand: {cell(result['required_piece_count'])} at {cell(result['piece_length'])}."
        )
        lines.append("")
        lines.append(
            f"Plan-selection formula ID: `{result['optimizer_result']['formula_id']}`. "
            f"Symbolic rule: `{result['optimizer_result']['symbolic_formula']}`. "
            f"Numerical substitution: `{result['optimizer_result']['substitution']}`."
        )
        lines.append("")
        lines.append(
            "Each selected stock bar applies `L_stock = sum(L_cut) + L_kerf + L_reusable + L_scrap`."
        )
        lines.append("")
        lines.append("| Formula ID | Stock bar | Stock length | Cuts | Used cut length | Kerf | Reusable offcut | Scrap | Length-balance substitution | Difference |")
        lines.append("|---|---|---:|---|---:|---:|---:|---:|---|---:|")
        for bar in result["optimizer_result"]["stock_bars"]:
            lines.append(
                f"| {bar['formula_id']} | {bar['stock_bar_id']} | {cell(bar['stock_length'])} | "
                + " + ".join(bar["cut_lengths"]["display_values"])
                + f" m | {cell(bar['used_length'])} | {cell(bar['kerf_length'])} | "
                f"{cell(bar['reusable_offcut'])} | {cell(bar['scrap'])} | "
                f"`{bar['substitution']}` | {cell(bar['length_balance_difference'])} |"
            )
        lines.append("")
        lines.append(
            calc_table(
                [
                    result["piece_length"],
                    result["required_piece_count"],
                    result["required_cut_length"],
                    result["stock_bar_count"],
                    result["purchased_length"],
                    result["purchased_weight"],
                    result["reusable_offcut_length"],
                    result["reusable_offcut_weight"],
                    result["scrap_length"],
                    result["scrap_weight"],
                    result["unresolved_demand"],
                    result["length_reconciliation_difference"],
                    result["weight_reconciliation_difference"],
                ]
            )
        )
        lines.append("")
    lines.append("### 8.4 Overall procurement reconciliation")
    lines.append("")
    lines.append(
        calc_table(
            [
                p["total_required_cut_length"],
                p["total_purchased_length"],
                p["total_purchased_weight"],
                p["total_reusable_offcut_length"],
                p["total_reusable_offcut_weight"],
                p["total_scrap_length"],
                p["total_scrap_weight"],
                p["total_unresolved_demand"],
                p["length_reconciliation_difference"],
                p["weight_reconciliation_difference"],
            ]
        )
    )
    lines.append("")
    lines.append(
        f"Length reconciliation: {cell(p['total_purchased_length'])} purchased = {cell(p['total_required_cut_length'])} installed demand + {cell(p['total_reusable_offcut_length'])} reusable offcut + {cell(p['total_scrap_length'])} scrap."
    )
    lines.append("")
    lines.append(
        f"Weight reconciliation: {cell(p['total_purchased_weight'])} purchased = {cell(r['theoretical_installed_weight'])} theoretical installed + {cell(p['total_reusable_offcut_weight'])} reusable offcut + {cell(p['total_scrap_weight'])} scrap."
    )
    lines.append("")
    lines.append(
        f"Unresolved demand is {cell(p['total_unresolved_demand'])}. Length status: {rec['rebar_length_check']['status']}; weight status: {rec['rebar_weight_check']['status']}; unresolved-demand status: {rec['unresolved_demand_check']['status']}."
    )
    lines.append("")
    lines.append("## 9. Resource and direct-cost ledger")
    lines.append("")
    lines.append("### 9.1 Materials")
    lines.append("")
    lines.append("| Resource | Quantity | Rate | Unrounded amount | Reported amount | Formula ID |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for row in costs["materials"]:
        lines.append(
            f"| {row['resource_id']} - {row['description']} | {cell(row['quantity'])} | {cell(row['rate'])} | "
            f"{row['amount']['unrounded_value']} PHP | {cell(row['amount'])} | {row['amount']['formula_id']} |"
        )
    lines.append("")
    lines.append("Material cost calculation trace:")
    lines.append("")
    lines.append(calc_table([row["amount"] for row in costs["materials"]]))
    lines.append("")
    lines.append(f"Direct material subtotal: **{cell(costs['direct_material_cost'])}**")
    lines.append("")
    lines.append("### 9.2 Labor")
    lines.append("")
    lines.append("| Resource | Basis quantity | Productivity | Crew-days | Rate | Reported amount |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in costs["labor"]:
        lines.append(
            f"| {row['resource_id']} - {row['description']} | {cell(row['basis_quantity'])} | {cell(row['productivity'])} | "
            f"{cell(row['crew_days'])} | {cell(row['rate'])} | {cell(row['amount'])} |"
        )
    lines.append("")
    lines.append("Labor usage and cost calculation trace:")
    lines.append("")
    labor_trace = []
    for row in costs["labor"]:
        labor_trace.extend([row["crew_days"], row["amount"]])
    lines.append(calc_table(labor_trace))
    lines.append("")
    lines.append(f"Direct labor subtotal: **{cell(costs['direct_labor_cost'])}**")
    lines.append("")
    lines.append("### 9.3 Equipment")
    lines.append("")
    lines.append("| Resource | Basis quantity | Calculated use | Minimum | Charged use | Rate | Reported amount |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for row in costs["equipment"]:
        lines.append(
            f"| {row['resource_id']} - {row['description']} | {cell(row['basis_quantity'])} | {cell(row['computed_unit_days'])} | "
            f"{cell(row['minimum_charge'])} | {cell(row['charged_unit_days'])} | {cell(row['rate'])} | {cell(row['amount'])} |"
        )
    lines.append("")
    lines.append("Equipment usage, minimum-charge, and cost calculation trace:")
    lines.append("")
    equipment_trace = []
    for row in costs["equipment"]:
        equipment_trace.extend(
            [row["computed_unit_days"], row["charged_unit_days"], row["amount"]]
        )
    lines.append(calc_table(equipment_trace))
    lines.append("")
    lines.append(f"Direct equipment subtotal: **{cell(costs['direct_equipment_cost'])}**")
    lines.append("")
    lines.append("### 9.4 Cost reconciliation")
    lines.append("")
    lines.append(
        calc_table(
            [
                costs["direct_material_cost"],
                costs["direct_labor_cost"],
                costs["direct_equipment_cost"],
                costs["total_direct_cost"],
            ]
        )
    )
    lines.append("")
    lines.append(
        f"Total direct cost is **{cell(costs['total_direct_cost'])}**. Overhead, tax, and profit are each {cell(costs['excluded_costs']['overhead'])}. Cost reconciliation difference: {cell(rec['cost_check']['difference'])}. Status: {rec['cost_check']['status']}."
    )
    lines.append("")
    lines.append("## 10. Independent checks and acceptance summary")
    lines.append("")
    lines.append("| Formula ID | Check | Symbolic formula | Numerical substitution | Difference or unresolved quantity | Status |")
    lines.append("|---|---|---|---|---:|---|")
    reconciliation_rows = [
        ("geometry_net_depth", "difference"),
        ("concrete_two_method_check", "difference"),
        ("formwork_two_method_check", "difference"),
        ("stirrup_boundary_check", "duplicate_count"),
        ("rebar_length_check", "difference"),
        ("rebar_weight_check", "difference"),
        ("unresolved_demand_check", "unresolved"),
        ("cost_check", "difference"),
    ]
    for check_key, quantity_key in reconciliation_rows:
        check = rec[check_key]
        lines.append(
            f"| {check['formula_id']} | {check['description']} | "
            f"`{check['symbolic_formula']}` | `{check['substitution']}` | "
            f"{cell(check[quantity_key])} | {check['status']} |"
        )
    lines.append("")
    lines.append("## 11. Assumptions requiring domain review")
    lines.append("")
    lines.extend(
        [
            "1. Confirm that support concrete, rather than beam concrete, should own the complete beam cross-section within both support widths for the project's measurement rules.",
            "2. Confirm that the slab is measured at full 0.150000 m thickness across the clear-span beam strip, leaving only the 0.450000 m beam drop in the beam quantity.",
            "3. Confirm the 3.000000% concrete waste allowance and 0.100000 m^3 ready-mix ordering increment.",
            "4. Confirm the formwork consumption factors and whole-unit procurement rounding. They are costing assumptions, not geometric necessities.",
            "5. Confirm every reinforcement detail supplied in the input, especially the anchorage additions, the 0.800000 m lap, the equal-piece fabrication policy, 0.040000 m stirrup cover, 10db hooks, and 12db aggregate bend deduction.",
            "6. Confirm that 6.000000 m, 9.000000 m, and 12.000000 m bars are actually available for all diameters, and whether cutting kerf should remain zero.",
            "7. Confirm the 1.000000 m reusable-offcut threshold and whether offcut inventory should receive a cost credit or be reserved for later elements.",
            "8. Confirm illustrative rates, labor productivity, equipment productivity, and minimum equipment charges before using this case for real estimating.",
        ]
    )
    lines.append("")
    lines.append("No assumption above is asserted to be required by a Philippine code.")
    lines.append("")
    lines.append("## 12. Proposed boundary and invalid-input tests")
    lines.append("")
    lines.extend(
        [
            "1. Reject zero or negative beam width, overall depth, clear span, support width, slab thickness, or procurement increment.",
            "2. Reject a slab thickness greater than or equal to overall beam depth, and reject an explicit net depth that does not equal overall depth less slab thickness within tolerance.",
            "3. Reject a support marked as a full cross-section overlap when its along-beam dimension is missing.",
            "4. Verify a zero-width support produces zero support-intersection deduction only when the input explicitly allows a face support with no overlap length.",
            "5. Verify zero concrete waste keeps net and required quantities equal while procurement rounding remains separate.",
            "6. Verify an exact 0.100000 m^3 concrete multiple produces zero procurement-rounding excess.",
            "7. Reject negative cover or cover large enough to make stirrup clear width or clear depth non-positive.",
            "8. Reject zero or negative stirrup spacing and zones whose end coordinate is less than their start coordinate.",
            "9. Verify adjacent zones that both include the same transition coordinate are either rejected or explicitly deduplicated with a nonzero duplicate diagnostic.",
            "10. Verify a middle zone shorter than one spacing interval can validly generate zero interior stirrups without division errors.",
            "11. Reject non-integer bar counts, lap counts, pieces per bar, and stock-bar demand counts.",
            "12. Reject a lap length that is negative or an equal-piece policy that cannot recover the declared effective assembled length.",
            "13. Report unresolved demand when every available stock length is shorter than a required cut piece.",
            "14. Verify a leftover exactly equal to the 1.000000 m threshold is reusable, while a 0.999999 m leftover is scrap.",
            "15. Verify nonzero cutting kerf is included in each stock pattern and can change the optimum or create unresolved demand.",
            "16. Verify the optimizer's tie-break order with equal purchased length but different stock-bar counts, scrap, and maximum offcut.",
            "17. Reject missing resource rates, zero productivity, negative rates, and negative minimum equipment charges.",
            "18. Verify line-level half-up rounding before subtotals using a rate that creates a half-cent boundary.",
            "19. Verify JSON input contains no expected-output keys and that expected JSON contains no undeclared source assumptions.",
            "20. Run the support checker and fail on any byte-level difference between the regenerated Markdown/expected JSON and the committed files.",
        ]
    )
    lines.append("")
    lines.append("## 13. Reproduction")
    lines.append("")
    lines.append("From the repository root:")
    lines.append("")
    lines.append("```bash")
    lines.append("python tests/solver/golden/support/verify_rc_beam_001.py")
    lines.append("```")
    lines.append("")
    lines.append("To regenerate the expected JSON and this Markdown file from the input facts:")
    lines.append("")
    lines.append("```bash")
    lines.append("python tests/solver/golden/support/verify_rc_beam_001.py --write")
    lines.append("```")
    lines.append("")
    lines.append(
        "The checker compares the entire calculated JSON object and the entire rendered Markdown text. A mismatch returns a nonzero exit code."
    )
    lines.append("")
    return "\n".join(lines)


def write_outputs(expected: dict[str, Any], markdown: str) -> None:
    EXPECTED_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED_PATH.write_text(
        json.dumps(expected, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    MARKDOWN_PATH.write_text(markdown, encoding="utf-8")


def formula_contract_errors(expected: dict[str, Any], markdown: str) -> list[str]:
    errors: list[str] = []
    formula_paths: dict[str, str] = {}
    required_fields = {
        "description",
        "symbolic_formula",
        "substitution",
        "rounding_stage",
    }

    def walk(value: Any, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            if "formula_id" in value:
                formula_id = value["formula_id"]
                location = ".".join(path) or "<root>"
                if not isinstance(formula_id, str) or not formula_id:
                    errors.append(f"{location}: formula_id must be a non-empty string")
                elif formula_id in formula_paths:
                    errors.append(
                        f"duplicate formula_id {formula_id}: {formula_paths[formula_id]} and {location}"
                    )
                else:
                    formula_paths[formula_id] = location
                missing = sorted(required_fields - value.keys())
                if missing:
                    errors.append(
                        f"{location}: formula record {formula_id} is missing {', '.join(missing)}"
                    )
                if isinstance(formula_id, str) and formula_id not in markdown:
                    errors.append(
                        f"{location}: formula_id {formula_id} is absent from the Markdown solution"
                    )
            for key, item in value.items():
                walk(item, path + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, path + (str(index),))

    walk(expected)
    return errors


def expected_unit_contract_errors(expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def walk(value: Any, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            has_unit = isinstance(value.get("unit"), str) and bool(value.get("unit"))
            for key, item in value.items():
                if isinstance(item, (int, float, Decimal)) and not isinstance(item, bool):
                    if not has_unit:
                        errors.append(
                            f"{'.'.join(path + (key,))}: numeric expected value has no unit in its quantity object"
                        )
                elif isinstance(item, list) and any(
                    isinstance(member, (int, float, Decimal))
                    and not isinstance(member, bool)
                    for member in item
                ):
                    if not has_unit:
                        errors.append(
                            f"{'.'.join(path + (key,))}: numeric expected array has no unit"
                        )
                walk(item, path + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, path + (str(index),))

    walk(expected)
    return errors


def verify_outputs(expected: dict[str, Any], markdown: str) -> list[str]:
    errors: list[str] = []
    errors.extend(formula_contract_errors(expected, markdown))
    errors.extend(expected_unit_contract_errors(expected))
    if expected.get("status") != "PASS":
        errors.append("calculated acceptance status is not PASS")

    stored_hash = expected.get("calculation_payload_sha256")
    hash_payload = {
        key: value
        for key, value in expected.items()
        if key != "calculation_payload_sha256"
    }
    canonical = json.dumps(
        hash_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    calculated_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if stored_hash != calculated_hash:
        errors.append("calculation payload SHA-256 does not match the expected JSON payload")
    if not EXPECTED_PATH.exists():
        errors.append(f"Missing expected file: {EXPECTED_PATH}")
    else:
        with EXPECTED_PATH.open("r", encoding="utf-8") as handle:
            committed = json.load(handle)
        if committed != expected:
            errors.append("rc_beam_001_expected.json does not match regenerated calculations")

    if not MARKDOWN_PATH.exists():
        errors.append(f"Missing Markdown file: {MARKDOWN_PATH}")
    else:
        committed_markdown = MARKDOWN_PATH.read_text(encoding="utf-8")
        if committed_markdown != markdown:
            errors.append("RC-BEAM-001.md does not match regenerated Markdown")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate the expected JSON and Markdown from the input facts",
    )
    args = parser.parse_args(argv)

    source = load_input()
    expected = build_expected(source)
    markdown = render_markdown(source, expected)

    if args.write:
        write_outputs(expected, markdown)
        print(f"WROTE {EXPECTED_PATH.relative_to(REPO_ROOT)}")
        print(f"WROTE {MARKDOWN_PATH.relative_to(REPO_ROOT)}")

    errors = verify_outputs(expected, markdown)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"PASS: {source['case_id']}")
    print(f"payload_sha256={expected['calculation_payload_sha256']}")
    print(
        "summary="
        f"net_concrete={expected['concrete']['net_measured_volume']['display']} m^3, "
        f"procured_concrete={expected['concrete']['procurement_quantity']['display']} m^3, "
        f"installed_rebar={expected['reinforcement']['theoretical_installed_weight']['display']} kg, "
        f"purchased_rebar={expected['procurement']['total_purchased_weight']['display']} kg, "
        f"direct_cost={expected['resources_and_costs']['total_direct_cost']['display']} PHP"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
