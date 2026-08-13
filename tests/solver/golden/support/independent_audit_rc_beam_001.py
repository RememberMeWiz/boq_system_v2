#!/usr/bin/env python3
"""Independent Decimal audit for RC-BEAM-001.

Independence boundary
---------------------
This audit intentionally does NOT import verify_rc_beam_001.py, any production
solver module, or any future formula module.  It has its own small Decimal
helpers, its own stirrup-coordinate construction, its own stock-plan search,
and its own resource-cost reconstruction.  Source facts and policies are read
from rc_beam_001_input.json.  rc_beam_001_expected.json is read only as the
assertion target after each quantity has been independently recalculated.

No common utility is used with the authoritative generator, including for JSON
loading or formatting.  The only shared inputs are the committed JSON/Markdown
artifacts themselves and Python's standard library.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[4]
INPUT_PATH = REPO_ROOT / "tests/solver/golden/rc_beam_001_input.json"
EXPECTED_PATH = REPO_ROOT / "tests/solver/golden/rc_beam_001_expected.json"
MARKDOWN_PATH = REPO_ROOT / "docs/solver/golden/RC-BEAM-001.md"

with INPUT_PATH.open("r", encoding="utf-8") as handle:
    SOURCE = json.load(handle)
with EXPECTED_PATH.open("r", encoding="utf-8") as handle:
    EXPECTED = json.load(handle)

getcontext().prec = int(SOURCE["reporting_policy"]["calculation_decimal_precision"]["value"])

ZERO = Decimal("0")
ONE = Decimal("1")
CENT = Decimal("0.01")
errors: list[str] = []
lines: list[str] = []


def dec(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def source_quantity(obj: dict[str, Any]) -> Decimal:
    return dec(obj["value"])


def expected_unrounded(obj: dict[str, Any]) -> Decimal:
    return dec(obj["unrounded_value"])


def expected_display(obj: dict[str, Any]) -> Decimal:
    return dec(obj["display"])


def ceil_increment(value: Decimal, increment: Decimal) -> Decimal:
    if increment <= ZERO:
        raise ValueError("increment must be positive")
    units = (value / increment).to_integral_value(rounding=ROUND_CEILING)
    return units * increment


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def check(label: str, actual: Any, target: Any) -> None:
    a = dec(actual)
    t = dec(target)
    passed = a == t
    lines.append(f"{label}: actual={a} expected={t} [{'PASS' if passed else 'FAIL'}]")
    if not passed:
        errors.append(f"{label}: actual={a} expected={t}")


def check_obj(label: str, actual: Decimal, target_obj: dict[str, Any]) -> None:
    check(label, actual, expected_unrounded(target_obj))


def collect_formula_ids(node: Any, found: list[str]) -> None:
    if isinstance(node, dict):
        formula_id = node.get("formula_id")
        if isinstance(formula_id, str):
            found.append(formula_id)
        for child in node.values():
            collect_formula_ids(child, found)
    elif isinstance(node, list):
        for child in node:
            collect_formula_ids(child, found)


def find_missing_units(node: Any, path: str = "$") -> list[str]:
    missing: list[str] = []
    if isinstance(node, dict):
        if "unrounded_value" in node and not isinstance(node.get("unit"), str):
            missing.append(path)
        for key, child in node.items():
            missing.extend(find_missing_units(child, f"{path}.{key}"))
    elif isinstance(node, list):
        for index, child in enumerate(node):
            missing.extend(find_missing_units(child, f"{path}[{index}]"))
    return missing


def optimizer(piece: Decimal, demand: int, stocks: list[Decimal], kerf: Decimal, reuse_threshold: Decimal):
    """Independent exact-demand dynamic-programming stock search."""
    patterns: list[tuple[Decimal, int, Decimal, Decimal, Decimal, Decimal, Decimal]] = []
    for stock in sorted(stocks):
        max_count = int(stock // (piece + kerf))
        for cut_count in range(1, max_count + 1):
            used = piece * cut_count
            kerf_total = kerf * cut_count
            offcut = stock - used - kerf_total
            reusable = offcut if offcut >= reuse_threshold else ZERO
            scrap = offcut if ZERO < offcut < reuse_threshold else ZERO
            patterns.append((stock, cut_count, used, kerf_total, reusable, scrap, offcut))

    # completed -> (objective, plan)
    best: dict[int, tuple[tuple[Any, ...], list[tuple[Any, ...]]]] = {
        0: ((ZERO, 0, ZERO, ZERO, ()), [])
    }
    for completed in range(demand + 1):
        current = best.get(completed)
        if current is None:
            continue
        _, current_plan = current
        for pattern in patterns:
            new_completed = completed + pattern[1]
            if new_completed > demand:
                continue
            plan = current_plan + [pattern]
            purchased = sum((p[0] for p in plan), ZERO)
            stock_count = len(plan)
            scrap = sum((p[5] for p in plan), ZERO)
            largest_offcut = max((p[6] for p in plan), default=ZERO)
            signature = tuple(sorted(((p[0], p[1], p[6]) for p in plan), reverse=True))
            objective = (purchased, stock_count, scrap, largest_offcut, signature)
            incumbent = best.get(new_completed)
            if incumbent is None or objective < incumbent[0]:
                best[new_completed] = (objective, plan)
    if demand not in best:
        return None
    return best[demand]


lines.append("S0-004-R2 RC-BEAM-001 INDEPENDENT DECIMAL AUDIT")
lines.append("generator_imported=False")
lines.append("production_formula_module_imported=False")
lines.append(f"decimal_precision={getcontext().prec}")
lines.append("")

# Geometry and concrete, independently reconstructed from source facts.
g = SOURCE["geometry"]
b = source_quantity(g["beam_width"])
overall_depth = source_quantity(g["overall_depth"])
net_depth = source_quantity(g["net_beam_below_slab_depth"])
clear_span = source_quantity(g["clear_span_between_support_faces"])
left_support = source_quantity(g["left_support"]["dimension_along_beam"])
right_support = source_quantity(g["right_support"]["dimension_along_beam"])
slab_thickness = source_quantity(g["slab"]["thickness"])

outer_length = clear_span + left_support + right_support
centerline_span = clear_span + left_support / 2 + right_support / 2
net_depth_check = overall_depth - slab_thickness

gross = b * overall_depth * outer_length
left_deduction = b * overall_depth * left_support
right_deduction = b * overall_depth * right_support
support_deduction = left_deduction + right_deduction
slab_deduction = b * slab_thickness * clear_span
net = gross - support_deduction - slab_deduction
net_direct = b * net_depth * clear_span
waste = net * source_quantity(SOURCE["concrete_policy"]["waste_rate"])
required_concrete = net + waste
procured_concrete = ceil_increment(required_concrete, source_quantity(SOURCE["concrete_policy"]["procurement_increment"]))
procurement_excess = procured_concrete - required_concrete

lines.append("GEOMETRY_AND_CONCRETE")
check_obj("outer_face_length", outer_length, EXPECTED["geometry"]["outer_face_to_outer_face_length"])
check_obj("support_centerline_span", centerline_span, EXPECTED["geometry"]["support_centerline_span"])
check_obj("net_depth_check", net_depth_check, EXPECTED["geometry"]["net_depth_check"])
check_obj("gross_concrete", gross, EXPECTED["concrete"]["gross_volume"])
check_obj("left_support_deduction", left_deduction, EXPECTED["concrete"]["left_support_intersection"])
check_obj("right_support_deduction", right_deduction, EXPECTED["concrete"]["right_support_intersection"])
check_obj("support_deduction", support_deduction, EXPECTED["concrete"]["support_intersection_deduction"])
check_obj("slab_deduction", slab_deduction, EXPECTED["concrete"]["slab_intersection_deduction"])
check_obj("net_concrete", net, EXPECTED["concrete"]["net_measured_volume"])
check_obj("net_concrete_second_method", net_direct, EXPECTED["concrete"]["independent_direct_net_volume"])
check("net_method_difference", net - net_direct, ZERO)
check_obj("waste_concrete", waste, EXPECTED["concrete"]["waste_quantity"])
check_obj("required_concrete", required_concrete, EXPECTED["concrete"]["required_quantity"])
check_obj("procured_concrete", procured_concrete, EXPECTED["concrete"]["procurement_quantity"])
check_obj("concrete_procurement_excess", procurement_excess, EXPECTED["concrete"]["procurement_rounding_excess"])
lines.append("")

# Formwork and formwork resources.
soffit = b * clear_span
left_side = net_depth * clear_span
right_side = net_depth * clear_span
end_forms = ZERO
formwork_total = soffit + left_side + right_side + end_forms
formwork_perimeter_check = (b + 2 * net_depth) * clear_span
lines.append("FORMWORK")
check_obj("soffit_area", soffit, EXPECTED["formwork"]["soffit_area"])
check_obj("left_side_area", left_side, EXPECTED["formwork"]["left_side_area"])
check_obj("right_side_area", right_side, EXPECTED["formwork"]["right_side_area"])
check_obj("end_form_area", end_forms, EXPECTED["formwork"]["end_form_area"])
check_obj("formwork_total", formwork_total, EXPECTED["formwork"]["total_contact_area"])
check_obj("formwork_second_method", formwork_perimeter_check, EXPECTED["formwork"]["independent_contact_area"])
check("formwork_method_difference", formwork_total - formwork_perimeter_check, ZERO)

factors = SOURCE["formwork_policy"]["resource_factors"]
ply_theoretical = formwork_total * source_quantity(factors["plywood_sheet_equivalent_per_contact_area"])
lumber_theoretical = formwork_total * source_quantity(factors["form_lumber_per_contact_area"])
oil_theoretical = formwork_total * source_quantity(factors["release_oil_per_contact_area"])
rounding = SOURCE["formwork_policy"]["resource_procurement_rounding"]
ply_procured = ceil_increment(ply_theoretical, source_quantity(rounding["plywood_sheet"]["increment"]))
lumber_procured = ceil_increment(lumber_theoretical, source_quantity(rounding["form_lumber"]["increment"]))
oil_procured = ceil_increment(oil_theoretical, source_quantity(rounding["release_oil"]["increment"]))
lines.append("")

# Reinforcement quantities.
rp = SOURCE["reinforcement_policy"]
unit_weight_divisor = source_quantity(rp["unit_weight_rule"]["divisor"])
installed_length = ZERO
installed_weight = ZERO
cut_demands: dict[int, tuple[Decimal, int]] = {}
installed_weight_by_diameter: dict[int, Decimal] = {}
lines.append("LONGITUDINAL_REINFORCEMENT")
for group in rp["longitudinal_bar_groups"]:
    gid = group["group_id"]
    expected_group = EXPECTED["reinforcement"]["longitudinal_groups"][gid]
    diameter = int(source_quantity(group["diameter"]))
    bar_count = int(source_quantity(group["bar_count"]))
    base = source_quantity(group["base_length"])
    anchorage = source_quantity(group["left_anchorage_addition"]) + source_quantity(group["right_anchorage_addition"])
    hook = source_quantity(group["hook_addition"])
    lap_addition = source_quantity(group["lap"]["count_per_bar"]) * source_quantity(group["lap"]["length_each"])
    effective_length = base + anchorage + hook
    physical_length = effective_length + lap_addition
    pieces_per_bar = int(source_quantity(group["fabrication"]["pieces_per_assembled_bar"]))
    piece_length = physical_length / pieces_per_bar
    piece_count = bar_count * pieces_per_bar
    total_length = physical_length * bar_count
    unit_weight = dec(diameter) * dec(diameter) / unit_weight_divisor
    total_weight = total_length * unit_weight

    check_obj(f"{gid}.effective_length", effective_length, expected_group["effective_assembled_length_per_bar"])
    check_obj(f"{gid}.lap_addition", lap_addition, expected_group["lap_addition_per_bar"])
    check_obj(f"{gid}.physical_length", physical_length, expected_group["physical_steel_length_per_bar"])
    check_obj(f"{gid}.piece_length", piece_length, expected_group["fabrication_piece_length"])
    check_obj(f"{gid}.piece_count", dec(piece_count), expected_group["fabrication_piece_count"])
    check_obj(f"{gid}.total_length", total_length, expected_group["theoretical_total_length"])
    check_obj(f"{gid}.unit_weight", unit_weight, expected_group["unit_weight"])
    check_obj(f"{gid}.total_weight", total_weight, expected_group["theoretical_total_weight"])

    installed_length += total_length
    installed_weight += total_weight
    cut_demands[diameter] = (piece_length, piece_count)
    installed_weight_by_diameter[diameter] = installed_weight_by_diameter.get(diameter, ZERO) + total_weight

# Stirrup coordinate construction is independent from the generator.
stirrups = rp["stirrups"]
stirrup_diameter = int(source_quantity(stirrups["diameter"]))
cover = source_quantity(stirrups["cover_to_outside_of_stirrup"])
clear_width = b - 2 * cover
clear_depth = overall_depth - 2 * cover
hook_each = dec(stirrups["hook_rule"]["extension_multiplier"]["value"]) * dec(stirrup_diameter) / 1000
hook_total = dec(stirrups["hook_rule"]["hook_count"]["value"]) * hook_each
bend_deduction = dec(stirrups["bend_deduction_rule"]["total_multiplier"]["value"]) * dec(stirrup_diameter) / 1000
stirrup_cut_length = 2 * (clear_width + clear_depth) + hook_total - bend_deduction
positions: list[Decimal] = []
lines.append("")
lines.append("STIRRUPS")
for zone, expected_zone in zip(stirrups["spacing_zones"], EXPECTED["reinforcement"]["stirrups"]["zones"]):
    start = source_quantity(zone["start"])
    end = source_quantity(zone["end"])
    spacing = source_quantity(zone["spacing"])
    intervals = int(((end - start) / spacing).to_integral_value())
    candidates = [start + spacing * i for i in range(intervals + 1)]
    if not zone["include_start_boundary"]:
        candidates = [p for p in candidates if p != start]
    if not zone["include_end_boundary"]:
        candidates = [p for p in candidates if p != end]
    positions.extend(candidates)
    check_obj(f"{zone['zone_id']}.final_count", dec(len(candidates)), expected_zone["count"])

unique_positions = sorted(set(positions))
duplicate_count = len(positions) - len(unique_positions)
stirrup_count = len(unique_positions)
stirrup_total_length = stirrup_cut_length * stirrup_count
stirrup_unit_weight = dec(stirrup_diameter) * dec(stirrup_diameter) / unit_weight_divisor
stirrup_total_weight = stirrup_total_length * stirrup_unit_weight
stirrup_expected = EXPECTED["reinforcement"]["stirrups"]
check_obj("stirrup.clear_width", clear_width, stirrup_expected["clear_width"])
check_obj("stirrup.clear_depth", clear_depth, stirrup_expected["clear_depth"])
check_obj("stirrup.hook_each", hook_each, stirrup_expected["hook_extension_each"])
check_obj("stirrup.hook_total", hook_total, stirrup_expected["hook_extension_total"])
check_obj("stirrup.bend_deduction", bend_deduction, stirrup_expected["bend_deduction"])
check_obj("stirrup.cut_length", stirrup_cut_length, stirrup_expected["cutting_length"])
check_obj("stirrup.raw_zone_count_sum", dec(len(positions)), stirrup_expected["sum_of_zone_counts_before_deduplication"])
check_obj("stirrup.duplicate_boundary_count", dec(duplicate_count), stirrup_expected["duplicate_boundary_count"])
check_obj("stirrup.unique_count", dec(stirrup_count), stirrup_expected["theoretical_count"])
check_obj("stirrup.total_length", stirrup_total_length, stirrup_expected["theoretical_total_length"])
check_obj("stirrup.unit_weight", stirrup_unit_weight, stirrup_expected["unit_weight"])
check_obj("stirrup.total_weight", stirrup_total_weight, stirrup_expected["theoretical_total_weight"])

installed_length += stirrup_total_length
installed_weight += stirrup_total_weight
cut_demands[stirrup_diameter] = (stirrup_cut_length, stirrup_count)
installed_weight_by_diameter[stirrup_diameter] = installed_weight_by_diameter.get(stirrup_diameter, ZERO) + stirrup_total_weight
check_obj("installed_rebar_length", installed_length, EXPECTED["reinforcement"]["theoretical_installed_length"])
check_obj("installed_rebar_weight", installed_weight, EXPECTED["reinforcement"]["theoretical_installed_weight"])
lines.append("")

# Procurement, with independent dynamic programming.
proc_policy = SOURCE["rebar_procurement_policy"]
kerf = source_quantity(proc_policy["cut_kerf"])
reuse_threshold = source_quantity(proc_policy["reusable_offcut_threshold"])
purchased_total_length = ZERO
purchased_total_weight = ZERO
reusable_total_length = ZERO
reusable_total_weight = ZERO
scrap_total_length = ZERO
scrap_total_weight = ZERO
unresolved_total = 0
purchased_weight_by_diameter: dict[int, Decimal] = {}
lines.append("PROCUREMENT")
for diameter in sorted(cut_demands, reverse=True):
    piece_length, demand = cut_demands[diameter]
    stocks = [source_quantity(qty) for qty in proc_policy["available_stock_lengths_by_diameter"][f"{diameter}_mm"]]
    result = optimizer(piece_length, demand, stocks, kerf, reuse_threshold)
    expected_diameter = EXPECTED["procurement"]["by_diameter"][f"{diameter}_mm"]
    if result is None:
        unresolved = demand
        errors.append(f"{diameter}mm: independent optimizer found unresolved demand={demand}")
        continue
    _, plan = result
    produced = sum(p[1] for p in plan)
    unresolved = demand - produced
    purchased_length = sum((p[0] for p in plan), ZERO)
    used_length = sum((p[2] for p in plan), ZERO)
    kerf_length = sum((p[3] for p in plan), ZERO)
    reusable_length = sum((p[4] for p in plan), ZERO)
    scrap_length = sum((p[5] for p in plan), ZERO)
    unit_weight = dec(diameter) * dec(diameter) / unit_weight_divisor
    purchased_weight = purchased_length * unit_weight
    reusable_weight = reusable_length * unit_weight
    scrap_weight = scrap_length * unit_weight

    check_obj(f"{diameter}mm.required_piece_count", dec(demand), expected_diameter["required_piece_count"])
    check_obj(f"{diameter}mm.required_cut_length", piece_length * demand, expected_diameter["required_cut_length"])
    check_obj(f"{diameter}mm.stock_bar_count", dec(len(plan)), expected_diameter["stock_bar_count"])
    check_obj(f"{diameter}mm.purchased_length", purchased_length, expected_diameter["purchased_length"])
    check_obj(f"{diameter}mm.purchased_weight", purchased_weight, expected_diameter["purchased_weight"])
    check_obj(f"{diameter}mm.reusable_length", reusable_length, expected_diameter["reusable_offcut_length"])
    check_obj(f"{diameter}mm.reusable_weight", reusable_weight, expected_diameter["reusable_offcut_weight"])
    check_obj(f"{diameter}mm.scrap_length", scrap_length, expected_diameter["scrap_length"])
    check_obj(f"{diameter}mm.scrap_weight", scrap_weight, expected_diameter["scrap_weight"])
    check_obj(f"{diameter}mm.unresolved", dec(unresolved), expected_diameter["unresolved_demand"])
    check(f"{diameter}mm.stock_identity", purchased_length, used_length + kerf_length + reusable_length + scrap_length)

    independent_patterns = Counter((p[0], p[1]) for p in plan)
    expected_patterns = Counter(
        (expected_unrounded(bar["stock_length"]), int(expected_unrounded(bar["cut_count"])))
        for bar in expected_diameter["optimizer_result"]["stock_bars"]
    )
    if independent_patterns != expected_patterns:
        errors.append(f"{diameter}mm stock assignment mismatch: actual={independent_patterns}, expected={expected_patterns}")
        lines.append(f"{diameter}mm.stock_assignments: actual={independent_patterns} expected={expected_patterns} [FAIL]")
    else:
        lines.append(f"{diameter}mm.stock_assignments: {independent_patterns} [PASS]")

    purchased_total_length += purchased_length
    purchased_total_weight += purchased_weight
    reusable_total_length += reusable_length
    reusable_total_weight += reusable_weight
    scrap_total_length += scrap_length
    scrap_total_weight += scrap_weight
    unresolved_total += unresolved
    purchased_weight_by_diameter[diameter] = purchased_weight

check_obj("procurement.total_purchased_length", purchased_total_length, EXPECTED["procurement"]["total_purchased_length"])
check_obj("procurement.total_purchased_weight", purchased_total_weight, EXPECTED["procurement"]["total_purchased_weight"])
check_obj("procurement.total_reusable_length", reusable_total_length, EXPECTED["procurement"]["total_reusable_offcut_length"])
check_obj("procurement.total_reusable_weight", reusable_total_weight, EXPECTED["procurement"]["total_reusable_offcut_weight"])
check_obj("procurement.total_scrap_length", scrap_total_length, EXPECTED["procurement"]["total_scrap_length"])
check_obj("procurement.total_scrap_weight", scrap_total_weight, EXPECTED["procurement"]["total_scrap_weight"])
check_obj("procurement.total_unresolved", dec(unresolved_total), EXPECTED["procurement"]["total_unresolved_demand"])
check("procurement.overall_length_identity", purchased_total_length, installed_length + kerf * sum(count for _, count in cut_demands.values()) + reusable_total_length + scrap_total_length)
check("procurement.overall_weight_identity", purchased_total_weight, installed_weight + reusable_total_weight + scrap_total_weight)
lines.append("")

# Tie wire and resource/cost reconstruction from source policies, not expected rows.
tie_policy = rp["tie_wire"]
tie_theoretical = installed_weight * source_quantity(tie_policy["factor"])
tie_procured = ceil_increment(tie_theoretical, source_quantity(tie_policy["procurement_increment"]))

material_quantities = {
    "MAT-CON-RM": procured_concrete,
    "MAT-FRM-PLY": ply_procured,
    "MAT-FRM-LBR": lumber_procured,
    "MAT-FRM-OIL": oil_procured,
    "MAT-RB-20": purchased_weight_by_diameter[20],
    "MAT-RB-16": purchased_weight_by_diameter[16],
    "MAT-RB-10": purchased_weight_by_diameter[10],
    "MAT-TIE-WIRE": tie_procured,
}
material_expected = {row["resource_id"]: row for row in EXPECTED["resources_and_costs"]["materials"]}
material_lines: list[Decimal] = []
lines.append("RESOURCE_COSTS")
for rate_row in SOURCE["resources_and_pricing"]["material_rates"]:
    rid = rate_row["resource_id"]
    quantity = material_quantities[rid]
    rate = source_quantity(rate_row["rate"])
    raw_amount = quantity * rate
    rounded_amount = money(raw_amount)
    target = material_expected[rid]
    check_obj(f"{rid}.quantity", quantity, target["quantity"])
    check_obj(f"{rid}.rate", rate, target["rate"])
    check_obj(f"{rid}.raw_amount", raw_amount, target["amount"])
    check(f"{rid}.reported_amount", rounded_amount, expected_display(target["amount"]))
    material_lines.append(rounded_amount)

labor_basis = {
    "concrete_required_volume": required_concrete,
    "formwork_contact_area": formwork_total,
    "theoretical_installed_rebar_weight": installed_weight,
}
labor_expected = {row["resource_id"]: row for row in EXPECTED["resources_and_costs"]["labor"]}
labor_lines: list[Decimal] = []
for source_row in SOURCE["resources_and_pricing"]["labor_resources"]:
    rid = source_row["resource_id"]
    basis = labor_basis[source_row["quantity_basis"]]
    productivity = source_quantity(source_row["productivity"])
    crew_days = basis / productivity
    rate = source_quantity(source_row["rate"])
    raw_amount = crew_days * rate
    rounded_amount = money(raw_amount)
    target = labor_expected[rid]
    check_obj(f"{rid}.basis", basis, target["basis_quantity"])
    check_obj(f"{rid}.productivity", productivity, target["productivity"])
    check_obj(f"{rid}.crew_days", crew_days, target["crew_days"])
    check_obj(f"{rid}.rate", rate, target["rate"])
    check_obj(f"{rid}.raw_amount", raw_amount, target["amount"])
    check(f"{rid}.reported_amount", rounded_amount, expected_display(target["amount"]))
    labor_lines.append(rounded_amount)

equipment_basis = labor_basis
equipment_expected = {row["resource_id"]: row for row in EXPECTED["resources_and_costs"]["equipment"]}
equipment_lines: list[Decimal] = []
for source_row in SOURCE["resources_and_pricing"]["equipment_resources"]:
    rid = source_row["resource_id"]
    basis = equipment_basis[source_row["quantity_basis"]]
    productivity = source_quantity(source_row["productivity"])
    computed_days = basis / productivity
    minimum = source_quantity(source_row["minimum_charge"])
    charged_days = max(computed_days, minimum)
    rate = source_quantity(source_row["rate"])
    raw_amount = charged_days * rate
    rounded_amount = money(raw_amount)
    target = equipment_expected[rid]
    check_obj(f"{rid}.basis", basis, target["basis_quantity"])
    check_obj(f"{rid}.productivity", productivity, target["productivity"])
    check_obj(f"{rid}.computed_days", computed_days, target["computed_unit_days"])
    check_obj(f"{rid}.minimum", minimum, target["minimum_charge"])
    check_obj(f"{rid}.charged_days", charged_days, target["charged_unit_days"])
    check_obj(f"{rid}.rate", rate, target["rate"])
    check_obj(f"{rid}.raw_amount", raw_amount, target["amount"])
    check(f"{rid}.reported_amount", rounded_amount, expected_display(target["amount"]))
    equipment_lines.append(rounded_amount)

material_subtotal = sum(material_lines, ZERO)
labor_subtotal = sum(labor_lines, ZERO)
equipment_subtotal = sum(equipment_lines, ZERO)
direct_cost = material_subtotal + labor_subtotal + equipment_subtotal
check("material_subtotal", material_subtotal, expected_display(EXPECTED["resources_and_costs"]["direct_material_cost"]))
check("labor_subtotal", labor_subtotal, expected_display(EXPECTED["resources_and_costs"]["direct_labor_cost"]))
check("equipment_subtotal", equipment_subtotal, expected_display(EXPECTED["resources_and_costs"]["direct_equipment_cost"]))
check("direct_cost", direct_cost, expected_display(EXPECTED["resources_and_costs"]["total_direct_cost"]))
check("direct_cost_identity", direct_cost, material_subtotal + labor_subtotal + equipment_subtotal)
for excluded_name in ("overhead", "tax", "profit"):
    check_obj(f"excluded.{excluded_name}", ZERO, EXPECTED["resources_and_costs"]["excluded_costs"][excluded_name])
lines.append("")

# Contract checks and classification.
formula_ids: list[str] = []
collect_formula_ids(EXPECTED, formula_ids)
markdown_text = MARKDOWN_PATH.read_text(encoding="utf-8")
missing_formula_ids = [fid for fid in formula_ids if fid not in markdown_text]
duplicated_formula_count = len(formula_ids) - len(set(formula_ids))
missing_units = find_missing_units(EXPECTED)
classification = "RC-BEAM-001 is a proposed normative target for the replacement solver architecture and is not a regression expectation for the frozen legacy solver."
check("formula_id_duplicate_count", dec(duplicated_formula_count), ZERO)
check("formula_ids_missing_from_markdown", dec(len(missing_formula_ids)), ZERO)
check("expected_quantity_objects_missing_units", dec(len(missing_units)), ZERO)
if classification not in markdown_text:
    errors.append("required normative-target classification is absent from Markdown")
    lines.append("classification_present=False [FAIL]")
else:
    lines.append("classification_present=True [PASS]")

# Input-versus-expected separation guard.  These are calculated-output fields,
# not source facts or declared policies.
forbidden_input_keys = {
    "formula_id",
    "symbolic_formula",
    "substitution",
    "unrounded_value",
    "reported_value",
    "display",
    "calculation_payload_sha256",
    "status",
}
found_forbidden: list[str] = []

def scan_input(node: Any, path: str = "$") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in forbidden_input_keys:
                found_forbidden.append(f"{path}.{key}")
            scan_input(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            scan_input(value, f"{path}[{index}]")

scan_input(SOURCE)
check("forbidden_calculated_keys_in_input", dec(len(found_forbidden)), ZERO)

# Expected payload hash is verified from committed expected JSON bytes/content.
payload_without_hash = {
    key: value for key, value in EXPECTED.items() if key != "calculation_payload_sha256"
}
canonical = json.dumps(payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
calculated_payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
stored_payload_hash = EXPECTED.get("calculation_payload_sha256", "")
if calculated_payload_hash != stored_payload_hash:
    errors.append("calculation payload SHA-256 mismatch")
    lines.append(f"payload_sha256={calculated_payload_hash} expected={stored_payload_hash} [FAIL]")
else:
    lines.append(f"payload_sha256={calculated_payload_hash} [PASS]")

lines.append("")
lines.append("GOLDEN_VALUE_GUARD")
for label, actual, target in [
    ("net_concrete_m3", net, "0.729000"),
    ("required_concrete_m3", required_concrete, "0.750870"),
    ("procured_concrete_m3", procured_concrete, "0.800000"),
    ("formwork_m2", formwork_total, "6.480000"),
    ("installed_rebar_kg", installed_weight.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP), "104.956843"),
    ("purchased_rebar_kg", purchased_total_weight.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP), "115.339088"),
    ("reusable_offcuts_m", reusable_total_length, "10.600000"),
    ("scrap_m", scrap_total_length, "0.000000"),
    ("unresolved_pieces", dec(unresolved_total), "0"),
    ("material_subtotal_PHP", material_subtotal, "15454.28"),
    ("labor_subtotal_PHP", labor_subtotal, "4997.11"),
    ("equipment_subtotal_PHP", equipment_subtotal, "525.00"),
    ("direct_cost_PHP", direct_cost, "20976.39"),
]:
    check(f"golden.{label}", actual, dec(target))

lines.append("")
lines.append("FILE_SHA256")
for path in [INPUT_PATH, EXPECTED_PATH, MARKDOWN_PATH, SCRIPT_PATH]:
    lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(REPO_ROOT)}")

lines.append("")
if errors:
    lines.append("FINAL RESULT: FAIL")
    lines.append("ERRORS:")
    lines.extend(f"- {error}" for error in errors)
else:
    lines.append("FINAL RESULT: PASS")
    lines.append("No arithmetic contradiction, procurement contradiction, cost contradiction, or contract mismatch was found.")

print("\n".join(lines))
raise SystemExit(1 if errors else 0)
