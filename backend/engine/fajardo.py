"""
backend/engine/fajardo.py

Plan2Takeoff V2 — 13-Trade Direct Costing Calculation Engine
==============================================================

Computes quantities, material breakdowns, labor mandays, equipment hours,
and DPWH-style Total Direct Costs

    C_total = C_material + C_labor + C_equipment

across all 13 trade sections referenced in:
    - formula_exhaustive_handbook.md (standard PH quantity-surveying
      methodology: PNS steel standards, DPWH CMPD costing structure,
      CHB/mortar ratios, etc.)
    - sample_solved_cases.md (worked example verification)
    - tech_spec_v2.md (13-trade breakdown + DPWH CMPD rate matrix)

All unit rates in DPWH_RATES are ILLUSTRATIVE placeholders. Swap in live
DPWH CMPD regional rates or supplier/subcontractor quotes for production
use. Every calculate_section_* function returns a dict with:

    {
        "quantities": {...},   # raw computed quantities (m3, m2, kg, pcs, m, etc.)
        "materials": {...},    # material breakdown in purchasable units
        "labor_manday": float,
        "equipment_hours": float,
        "cost": {
            "material": float,
            "labor": float,
            "equipment": float,
            "total": float,
        },
    }

The top-level `run_full_takeoff` orchestrator wires Sections II-XIII
together and then feeds their combined direct cost subtotal into
Section I (General Requirements), which is priced as a lump-sum
percentage of that subtotal.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Global constants
# ---------------------------------------------------------------------------

CEMENT_BAG_KG = 40.0

# Section III — concrete mix design table (per 1.0 m3 finished concrete)
CONCRETE_MIX = {
    "AA": {"cement_bags": 12.00, "sand_m3": 0.50, "gravel_m3": 1.00},
    "A":  {"cement_bags": 9.00,  "sand_m3": 0.50, "gravel_m3": 1.00},
    "B":  {"cement_bags": 7.50,  "sand_m3": 0.50, "gravel_m3": 1.00},
    "C":  {"cement_bags": 6.00,  "sand_m3": 0.50, "gravel_m3": 1.00},
}

# Section V — PNS 49 theoretical unit weight: W(kg/m) = d^2 / 162.2
def rebar_unit_weight_kg_per_m(diameter_mm: float) -> float:
    return (diameter_mm ** 2) / 162.2


# Section IV — masonry factors per 1.0 m2 net wall area
CHB_PCS_PER_M2 = 12.5
MORTAR_FACTORS = {
    # thickness_mm: (cement_bags_per_m2, sand_m3_per_m2)
    100: (0.522, 0.0435),
    150: (1.010, 0.0840),
    200: (1.350, 0.1120),
}
PLASTER_CEMENT_BAGS_PER_M2_FACE_16MM = 0.192
PLASTER_SAND_M3_PER_M2_FACE_16MM = 0.016

# Section III — formwork material factors
MARINE_PLY_SHEETS_PER_M2 = 0.28
FORM_LUMBER_BDFT_PER_M2 = 7.0

# Section VI
ROOFING_LAP_ALLOWANCE = 0.12          # +12% lap
ROOFING_RIVETS_PCS_PER_M2 = 26
HARDIFLEX_WASTE = 0.05                # +5%
METAL_FURRING_M_PER_M2 = 2.5

# Section VIII
TILE_WASTE_STANDARD = 0.08            # 8%
TILE_WASTE_DIAGONAL = 0.15            # 15% for 45-degree diagonal lay
TILE_MORTAR_BED_BAGS_PER_M2 = 0.24    # 20mm 1:4 mortar bed
TILE_GROUT_KG_PER_M2 = 0.40

# Section IX
PAINT_PRIMER_COVERAGE_M2_PER_L_SMOOTH = 10.0
PAINT_PRIMER_COVERAGE_M2_PER_L_ROUGH = 6.25   # 6.0-6.5 m2/L, midpoint
PAINT_TOPCOAT_COVERAGE_M2_PER_L = 8.0
CEILING_LATEX_COVERAGE_M2_PER_L = 8.0
METAL_PRIMER_COVERAGE_M2_PER_L = 8.0
METAL_ENAMEL_COVERAGE_M2_PER_L = 9.0

# Section X
UPVC_FITTINGS_ALLOWANCE = 0.10        # +10%
PIPE_STD_LENGTH_M = 3.0               # commercial pipe length -> ceil(L/3)

# Section XI
WIRE_SLACK_ALLOWANCE = 0.12           # +12% drop/slack
CONDUIT_STD_LENGTH_M = 3.0

# Section XII
ACU_BTU_PER_M2 = 700.0
COPPER_PIPING_ALLOWANCE = 0.10        # +10%

# Section XIII
ACP_WASTE = 0.08                      # +8%
WATERPROOFING_KG_PER_M2 = 1.2         # 2-coat elastomeric

# Section II
BACKFILL_SHRINKAGE = 0.18             # 18% (mixed soil, matches worked example)
SOIL_POISONING_L_PER_M2 = 5.0

# Section I — lump-sum percentages of Sections II-XIII direct cost subtotal
GENREQ_MOBILIZATION_PCT = 0.010
GENREQ_TEMP_FACILITIES_PCT = 0.015
GENREQ_SAFETY_PCT = 0.0075
GENREQ_PERMITS_LOT = 18_500.00


# ---------------------------------------------------------------------------
# DPWH CMPD Master Direct Cost Matrix (illustrative placeholder rates, PHP)
# Each entry: (material_rate, labor_rate, equipment_rate) per stated unit.
# Swap with live regional CMPD rates / supplier quotes for production.
# ---------------------------------------------------------------------------

DPWH_RATES = {
    # unit-priced materials
    "cement_bag":            (205.36, 0.00, 0.00),     # per bag
    "sand_m3":                (1_473.21, 0.00, 0.00),  # per m3
    "gravel_m3":              (1_517.86, 0.00, 0.00),  # per m3
    "rebar_kg":               (42.68, 12.00, 2.50),    # per kg
    "tie_wire_kg":            (62.50, 12.00, 0.00),    # per kg
    "chb_100_pc":             (15.18, 19.20, 1.20),    # per pc
    "chb_150_pc":             (22.32, 19.20, 1.20),    # per pc
    "chb_200_pc":             (28.50, 19.20, 1.20),    # per pc (extrapolated)
    "marine_ply_sheet":       (750.00, 210.00, 0.00),  # per sheet
    "form_lumber_bdft":       (48.00, 12.00, 0.00),    # per bd.ft
    "gravel_bedding_m3":      (1_650.00, 0.00, 0.00),  # per m3 (placed)
    "excavation_m3":          (0.00, 350.00, 0.00),    # labor-only
    "backfill_m3":            (0.00, 280.00, 0.00),    # labor-only
    "soil_poison_l":          (185.00, 25.00, 0.00),   # per liter applied
    "structural_steel_kg":    (68.00, 15.00, 5.00),    # per kg
    "handrail_m":             (1_450.00, 350.00, 0.00),# per lin.m (stainless)

    # concrete classes: material rate is a synthetic composite baked in via
    # cement/sand/gravel unit rates; labor+equipment given per m3 poured.
    "concrete_labor_m3":      (0.00, 850.00, 250.00),

    # roofing
    "longspan_roofing_m2":    (620.00, 180.00, 0.00),
    "purlin_kg":              (68.00, 15.00, 0.00),
    "rivet_pc":                (3.50, 0.00, 0.00),
    "gi_strap_pc":            (35.00, 10.00, 0.00),
    "hardiflex_m2":            (295.00, 120.00, 0.00),
    "metal_furring_m":         (45.00, 15.00, 0.00),

    # doors/windows
    "aluminum_window_m2":      (4_200.00, 650.00, 0.00),
    "tempered_glass_door_set": (12_500.00, 1_200.00, 0.00),
    "panel_door_set":          (8_500.00, 900.00, 0.00),
    "flush_door_set":          (4_200.00, 700.00, 0.00),
    "jamb_lumber_bdft":        (48.00, 12.00, 0.00),

    # tile & flooring
    "floor_tile_m2":           (850.00, 220.00, 0.00),
    "wall_tile_m2":             (750.00, 220.00, 0.00),
    "tile_mortar_bed_bag":     (205.36, 60.00, 0.00),
    "tile_grout_kg":            (95.00, 0.00, 0.00),

    # painting
    "neutralizer_l":           (185.00, 0.00, 0.00),
    "primer_l":                 (220.00, 0.00, 0.00),
    "topcoat_l":                 (280.00, 0.00, 0.00),
    "ceiling_latex_l":          (260.00, 0.00, 0.00),
    "metal_primer_l":           (240.00, 0.00, 0.00),
    "metal_enamel_l":           (310.00, 0.00, 0.00),
    "paint_labor_m2":           (0.00, 85.00, 0.00),

    # plumbing
    "upvc_4in_pc":              (620.00, 150.00, 0.00),
    "upvc_2in_pc":              (280.00, 120.00, 0.00),
    "ppr_pipe_pc":              (350.00, 120.00, 0.00),
    "fixture_set":              (4_500.00, 850.00, 0.00),
    "catch_basin_lot":          (6_500.00, 1_800.00, 0.00),

    # electrical
    "thhn_wire_m":              (32.00, 18.00, 0.00),
    "pvc_conduit_pc":           (95.00, 40.00, 0.00),
    "outlet_pc":                 (180.00, 120.00, 0.00),
    "led_panel_pc":              (850.00, 150.00, 0.00),
    "breaker_pc":                 (650.00, 200.00, 0.00),

    # sanitary / mechanical
    "acu_unit_per_ton":         (28_000.00, 3_500.00, 0.00),
    "copper_piping_m":           (650.00, 180.00, 0.00),
    "commissioning_lot":          (0.00, 5_000.00, 0.00),

    # special works
    "acp_cladding_m2":            (1_850.00, 350.00, 0.00),
    "waterproofing_kg":            (145.00, 0.00, 0.00),
    "waterproofing_labor_m2":     (0.00, 65.00, 0.00),
}


def _rate(key: str) -> tuple[float, float, float]:
    return DPWH_RATES[key]


def _cost_line(qty: float, rate_key: str) -> tuple[float, float, float]:
    """Returns (material_cost, labor_cost, equipment_cost) for qty x rate."""
    m, l, e = _rate(rate_key)
    return (qty * m, qty * l, qty * e)


def _sum_costs(*lines: tuple[float, float, float]) -> dict:
    mat = sum(l[0] for l in lines)
    lab = sum(l[1] for l in lines)
    eq = sum(l[2] for l in lines)
    return {"material": round(mat, 2), "labor": round(lab, 2),
            "equipment": round(eq, 2), "total": round(mat + lab + eq, 2)}


def _round_up(x: float) -> int:
    return int(math.ceil(x - 1e-9))


# ===========================================================================
# SECTION II — EARTHWORKS
# ===========================================================================

def calculate_section_2_earthworks(footing_specs: list, slab_area: float,
                                    slab_t: float) -> dict:
    """
    footing_specs: list of dicts, each:
        {
            "length_m": float, "width_m": float, "depth_m": float,
            "count": int,
            "clearance_m": float (working clearance per side, default 0.25),
        }
    slab_area: plan area (m2) of slab-on-grade requiring gravel bedding.
    slab_t: (kept for interface compatibility; not used directly in bedding
             thickness, which is fixed per handbook convention).
    """
    total_exc_v = 0.0
    total_footing_v = 0.0
    footing_footprint_area = 0.0

    for spec in footing_specs:
        L = spec["length_m"]
        W = spec["width_m"]
        H = spec["depth_m"]
        N = spec["count"]
        clr = spec.get("clearance_m", 0.25)

        exc_L = L + clr
        exc_W = W + clr
        exc_v = exc_L * exc_W * H * N
        footing_v = L * W * H * N

        total_exc_v += exc_v
        total_footing_v += footing_v
        footing_footprint_area += (L * W) * N

    backfill_v = (total_exc_v - total_footing_v) * (1 + BACKFILL_SHRINKAGE)
    gravel_bedding_v = footing_footprint_area * 0.10  # 100mm under footings
    if slab_area:
        gravel_bedding_v += slab_area * 0.05           # 50mm under slabs

    soil_poison_area = footing_footprint_area + slab_area
    soil_poison_l = soil_poison_area * SOIL_POISONING_L_PER_M2

    quantities = {
        "excavation_m3": round(total_exc_v, 3),
        "backfill_m3": round(backfill_v, 3),
        "gravel_bedding_m3": round(gravel_bedding_v, 3),
        "soil_poisoning_l": round(soil_poison_l, 2),
    }

    costs = _sum_costs(
        _cost_line(quantities["excavation_m3"], "excavation_m3"),
        _cost_line(quantities["backfill_m3"], "backfill_m3"),
        _cost_line(quantities["gravel_bedding_m3"], "gravel_bedding_m3"),
        _cost_line(quantities["soil_poisoning_l"], "soil_poison_l"),
    )

    labor_manday = round((quantities["excavation_m3"] / 3.5) +
                          (quantities["backfill_m3"] / 4.0), 2)

    return {
        "quantities": quantities,
        "materials": {"gravel_m3": quantities["gravel_bedding_m3"],
                      "soil_poison_l": quantities["soil_poisoning_l"]},
        "labor_manday": labor_manday,
        "equipment_hours": round(quantities["excavation_m3"] / 6.0, 2),
        "cost": costs,
    }


# ===========================================================================
# SECTION III — CONCRETE WORKS & FORMWORKS
# ===========================================================================

def calculate_section_3_concrete_and_formworks(elements: list) -> dict:
    """
    elements: list of dicts, each describing one structural element group:
        {
            "type": "footing" | "column" | "beam" | "slab",
            "class": "AA" | "A" | "B" | "C",
            "count": int,
            # footing:
            "length_m", "width_m", "height_m",
            # column:
            "width_m", "depth_m", "clear_height_m",
            # beam:
            "width_m", "depth_m", "clear_span_m",
            # slab:
            "area_m2", "thickness_m",
            "wastage": float (default 0.05 site-mixed, 0.03 ready-mix),
        }
    """
    total_volume = 0.0
    total_formwork_area = 0.0
    cement_bags = 0.0
    sand_m3 = 0.0
    gravel_m3 = 0.0
    volume_by_class: dict[str, float] = {}

    for el in elements:
        etype = el["type"]
        cls = el.get("class", "A")
        N = el.get("count", 1)
        wastage = el.get("wastage", 0.05)

        if etype == "footing":
            L, W = el["length_m"], el["width_m"]
            H = el.get("depth_m") or el.get("height_m") or 0.40
            v = L * W * H * N
            area = 2 * (L + W) * H * N
        elif etype == "column":
            w, d, Hc = el["width_m"], el["depth_m"], el["clear_height_m"]
            v = w * d * Hc * N
            area = 2 * (w + d) * Hc * N
        elif etype == "beam":
            w, d, Lc = el["width_m"], el["depth_m"], el["clear_span_m"]
            v = w * d * Lc * N
            area = (w + 2 * d) * Lc * N
        elif etype == "slab":
            A, t = el["area_m2"], el["thickness_m"]
            v = A * t
            area = 0.0  # slab soffit formwork typically shored, not tallied here
        else:
            raise ValueError(f"Unknown element type: {etype}")

        v_with_waste = v * (1 + wastage)
        total_volume += v_with_waste
        total_formwork_area += area
        volume_by_class[cls] = volume_by_class.get(cls, 0.0) + v_with_waste

        mix = CONCRETE_MIX[cls]
        cement_bags += v_with_waste * mix["cement_bags"]
        sand_m3 += v_with_waste * mix["sand_m3"]
        gravel_m3 += v_with_waste * mix["gravel_m3"]

    marine_ply_sheets = total_formwork_area * MARINE_PLY_SHEETS_PER_M2
    form_lumber_bdft = total_formwork_area * FORM_LUMBER_BDFT_PER_M2

    quantities = {
        "concrete_volume_m3": round(total_volume, 3),
        "volume_by_class_m3": {k: round(v, 3) for k, v in volume_by_class.items()},
        "formwork_contact_area_m2": round(total_formwork_area, 3),
    }
    materials = {
        "cement_bags": _round_up(cement_bags),
        "sand_m3": round(sand_m3, 3),
        "gravel_m3": round(gravel_m3, 3),
        "marine_ply_sheets": _round_up(marine_ply_sheets),
        "form_lumber_bdft": round(form_lumber_bdft, 2),
    }

    costs = _sum_costs(
        _cost_line(materials["cement_bags"], "cement_bag"),
        _cost_line(materials["sand_m3"], "sand_m3"),
        _cost_line(materials["gravel_m3"], "gravel_m3"),
        _cost_line(quantities["concrete_volume_m3"], "concrete_labor_m3"),
        _cost_line(materials["marine_ply_sheets"], "marine_ply_sheet"),
        _cost_line(materials["form_lumber_bdft"], "form_lumber_bdft"),
    )

    labor_manday = round(quantities["concrete_volume_m3"] / 4.0 +
                          total_formwork_area / 8.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": round(quantities["concrete_volume_m3"] / 5.0, 2),
        "cost": costs,
    }


# ===========================================================================
# SECTION IV — MASONRY WORKS
# ===========================================================================

def calculate_section_4_masonry_works(wall_elements: list) -> dict:
    """
    wall_elements: list of dicts:
        {
            "length_m": float, "height_m": float,
            "thickness_mm": 100 | 150 | 200,
            "openings": [{"width_m": float, "height_m": float}, ...],
            "stiffener_area_m2": float (optional, embedded RC stiffeners),
            "plaster_faces": 0 | 1 | 2 (default 2),
        }
    """
    total_chb = 0.0
    chb_by_thickness: dict[int, float] = {}
    total_mortar_cement = 0.0
    total_mortar_sand = 0.0
    total_plaster_area = 0.0
    total_plaster_cement = 0.0
    total_plaster_sand = 0.0

    for wall in wall_elements:
        L, H = wall["length_m"], wall["height_m"]
        thickness = wall["thickness_mm"]
        openings = wall.get("openings", [])
        stiffener_area = wall.get("stiffener_area_m2", 0.0)
        plaster_faces = wall.get("plaster_faces", 2)

        gross_area = L * H
        opening_area = sum(o["width_m"] * o["height_m"] for o in openings)
        net_area = gross_area - opening_area - stiffener_area

        chb_pcs = net_area * CHB_PCS_PER_M2
        total_chb += chb_pcs
        chb_by_thickness[thickness] = chb_by_thickness.get(thickness, 0.0) + chb_pcs

        cement_f, sand_f = MORTAR_FACTORS[thickness]
        total_mortar_cement += net_area * cement_f
        total_mortar_sand += net_area * sand_f

        # jamb returns for each opening (Appendix B.3)
        jamb_area = sum(2 * (o["width_m"] + o["height_m"]) * (thickness / 1000.0)
                         for o in openings)

        plaster_area_this_wall = (net_area + jamb_area) * plaster_faces
        total_plaster_area += plaster_area_this_wall
        total_plaster_cement += plaster_area_this_wall * PLASTER_CEMENT_BAGS_PER_M2_FACE_16MM
        total_plaster_sand += plaster_area_this_wall * PLASTER_SAND_M3_PER_M2_FACE_16MM

    quantities = {
        "chb_count": _round_up(total_chb),
        "chb_by_thickness": {k: _round_up(v) for k, v in chb_by_thickness.items()},
        "plaster_area_m2": round(total_plaster_area, 3),
    }
    materials = {
        "mortar_cement_bags": round(total_mortar_cement, 2),
        "mortar_sand_m3": round(total_mortar_sand, 3),
        "plaster_cement_bags": round(total_plaster_cement, 2),
        "plaster_sand_m3": round(total_plaster_sand, 3),
    }

    chb_cost = (0.0, 0.0, 0.0)
    for thickness, pcs in quantities["chb_by_thickness"].items():
        key = f"chb_{thickness}_pc" if thickness in (100, 150, 200) else "chb_150_pc"
        c = _cost_line(pcs, key)
        chb_cost = tuple(a + b for a, b in zip(chb_cost, c))

    total_cement_bags = materials["mortar_cement_bags"] + materials["plaster_cement_bags"]
    total_sand_m3 = materials["mortar_sand_m3"] + materials["plaster_sand_m3"]

    costs = _sum_costs(
        chb_cost,
        _cost_line(_round_up(total_cement_bags), "cement_bag"),
        _cost_line(total_sand_m3, "sand_m3"),
        _cost_line(quantities["plaster_area_m2"], "paint_labor_m2"),  # generic plaster labor proxy
    )

    labor_manday = round(quantities["chb_count"] / 150.0 +
                          quantities["plaster_area_m2"] / 10.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION V — METALS & STEEL REINFORCEMENT
# ===========================================================================

def calculate_section_5_metals_and_rebar(rebar_elements: list,
                                          structural_steel_kg: float = 0.0) -> dict:
    """
    rebar_elements: list of dicts, each describing a rebar group:
        {
            "member": "footing_mat" | "column_main" | "beam_stirrup" | "generic",
            "diameter_mm": float,
            "count": int,                  # number of bars / stirrups
            # footing_mat:
            "member_length_m": float,      # footing dimension bar runs along
            "cover_m": float (default 0.075),
            # column_main:
            "story_height_m": float,
            "dowel_length_m": float (default 0.0),
            # beam_stirrup:
            "beam_width_m": float, "beam_depth_m": float,
            "cover_m": float (default 0.040),
            "apply_bend_deduction": bool (default False — see note below),
            # generic:
            "length_m": float,             # straight cut length, no deductions
        }

    NOTE on beam_stirrup bend deduction: sample_solved_cases.md Case 2.2
    (the verified V2 baseline) computes the 135-deg-hook stirrup length as
    2*(w-2c) + 2*(d-2c) + 2*(10*db) WITHOUT subtracting the 12*db bend
    shortening described in the handbook's Appendix B.2. This function
    matches the verified baseline by default (apply_bend_deduction=False).
    Set apply_bend_deduction=True per-element for the stricter Appendix B.2
    fabrication length (subtracts 12*db per stirrup for bend shortening).
    """
    total_weight_kg = 0.0
    weight_by_diameter: dict[float, float] = {}

    for el in rebar_elements:
        member = el.get("member", "generic")
        db_mm = el["diameter_mm"]
        db_m = db_mm / 1000.0
        N = el["count"]
        unit_w = rebar_unit_weight_kg_per_m(db_mm)

        if member == "footing_mat":
            L = el.get("member_length_m") or el.get("length_m") or 1.5
            cover = el.get("cover_m", 0.075)
            hook = 12 * db_m
            cut_len = max(0.5, (L - 2 * cover) + 2 * hook)
        elif member == "column_main":
            H = el.get("story_height_m") or el.get("length_m") or 3.2
            splice = 40 * db_m
            dowel = el.get("dowel_length_m", 0.0)
            cut_len = H + splice + dowel
        elif member == "beam_stirrup":
            w = el.get("beam_width_m") or 0.25
            d = el.get("beam_depth_m") or 0.40
            cover = el.get("cover_m", 0.040)
            hook_allow = 2 * (10 * db_m)          # 135 deg seismic hook, 2 legs
            apply_bend = el.get("apply_bend_deduction", False)
            bend_deduction = (12 * db_m) if apply_bend else 0.0  # 4 bends x 3*db each
            cut_len = (2 * (w - 2 * cover) + 2 * (d - 2 * cover)
                       + hook_allow - bend_deduction)
        elif member == "generic":
            cut_len = el["length_m"]
        else:
            raise ValueError(f"Unknown rebar member type: {member}")

        weight = cut_len * N * unit_w
        total_weight_kg += weight
        weight_by_diameter[db_mm] = weight_by_diameter.get(db_mm, 0.0) + weight

    tie_wire_kg = total_weight_kg * 0.015

    quantities = {
        "rebar_weight_kg": round(total_weight_kg, 2),
        "rebar_weight_by_diameter_kg": {k: round(v, 2) for k, v in weight_by_diameter.items()},
        "structural_steel_kg": round(structural_steel_kg, 2),
    }
    materials = {
        "tie_wire_kg": round(tie_wire_kg, 2),
    }

    costs = _sum_costs(
        _cost_line(quantities["rebar_weight_kg"], "rebar_kg"),
        _cost_line(materials["tie_wire_kg"], "tie_wire_kg"),
        _cost_line(quantities["structural_steel_kg"], "structural_steel_kg"),
    )

    labor_manday = round(quantities["rebar_weight_kg"] / 250.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION VI — ROOFING & CEILING WORKS
# ===========================================================================

def calculate_section_6_roofing_and_ceiling(roof_plan_area: float,
                                             pitch_deg: float,
                                             ceiling_area: float) -> dict:
    theta = math.radians(pitch_deg)
    slope_area_raw = roof_plan_area / math.cos(theta)
    slope_area_with_lap = slope_area_raw * (1 + ROOFING_LAP_ALLOWANCE)

    rivets = slope_area_with_lap * ROOFING_RIVETS_PCS_PER_M2
    ceiling_with_waste = ceiling_area * (1 + HARDIFLEX_WASTE)
    furring_m = ceiling_area * METAL_FURRING_M_PER_M2

    quantities = {
        "roof_slope_area_m2": round(slope_area_with_lap, 3),
        "ceiling_area_m2": round(ceiling_with_waste, 3),
        "metal_furring_m": round(furring_m, 2),
    }
    materials = {
        "roofing_rivets_pcs": _round_up(rivets),
    }

    costs = _sum_costs(
        _cost_line(quantities["roof_slope_area_m2"], "longspan_roofing_m2"),
        _cost_line(materials["roofing_rivets_pcs"], "rivet_pc"),
        _cost_line(quantities["ceiling_area_m2"], "hardiflex_m2"),
        _cost_line(quantities["metal_furring_m"], "metal_furring_m"),
    )

    labor_manday = round(quantities["roof_slope_area_m2"] / 15.0 +
                          quantities["ceiling_area_m2"] / 12.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION VII — DOORS & WINDOWS
# ===========================================================================

def calculate_section_7_doors_and_windows(windows_sqm: float, doors: list) -> dict:
    """
    doors: list of dicts:
        {"type": "tempered_glass" | "panel" | "flush", "count": int,
         "jamb_lumber_bdft_each": float (default 8.0)}
    """
    door_counts = {"tempered_glass": 0, "panel": 0, "flush": 0}
    jamb_lumber_bdft = 0.0
    for d in doors:
        dtype = d["type"]
        n = d["count"]
        door_counts[dtype] = door_counts.get(dtype, 0) + n
        jamb_lumber_bdft += n * d.get("jamb_lumber_bdft_each", 8.0)

    tempered_glass_with_waste = door_counts["tempered_glass"] * (1 + 0.02)

    quantities = {
        "windows_m2": round(windows_sqm, 2),
        "door_counts": door_counts,
        "jamb_lumber_bdft": round(jamb_lumber_bdft, 2),
    }
    materials = {}

    costs = _sum_costs(
        _cost_line(quantities["windows_m2"], "aluminum_window_m2"),
        _cost_line(math.ceil(tempered_glass_with_waste), "tempered_glass_door_set"),
        _cost_line(door_counts["panel"], "panel_door_set"),
        _cost_line(door_counts["flush"], "flush_door_set"),
        _cost_line(quantities["jamb_lumber_bdft"], "jamb_lumber_bdft"),
    )

    labor_manday = round(sum(door_counts.values()) / 4.0 + windows_sqm / 8.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION VIII — TILE & FLOORING WORKS
# ===========================================================================

def calculate_section_8_tile_and_flooring(floor_area: float, wall_area: float,
                                           is_diagonal: bool = False) -> dict:
    waste = TILE_WASTE_DIAGONAL if is_diagonal else TILE_WASTE_STANDARD
    floor_with_waste = floor_area * (1 + waste)
    wall_with_waste = wall_area * (1 + TILE_WASTE_STANDARD)

    mortar_bags = floor_area * TILE_MORTAR_BED_BAGS_PER_M2
    grout_kg = (floor_area + wall_area) * TILE_GROUT_KG_PER_M2

    quantities = {
        "floor_tile_area_m2": round(floor_with_waste, 3),
        "wall_tile_area_m2": round(wall_with_waste, 3),
    }
    materials = {
        "mortar_bed_bags": round(mortar_bags, 2),
        "tile_grout_kg": round(grout_kg, 2),
    }

    costs = _sum_costs(
        _cost_line(quantities["floor_tile_area_m2"], "floor_tile_m2"),
        _cost_line(quantities["wall_tile_area_m2"], "wall_tile_m2"),
        _cost_line(materials["mortar_bed_bags"], "tile_mortar_bed_bag"),
        _cost_line(materials["tile_grout_kg"], "tile_grout_kg"),
    )

    labor_manday = round((floor_area + wall_area) / 8.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION IX — PAINTING WORKS
# ===========================================================================

def calculate_section_9_painting_works(masonry_area: float, ceiling_area: float,
                                        metal_area: float,
                                        is_rough_chb: bool = False) -> dict:
    primer_coverage = (PAINT_PRIMER_COVERAGE_M2_PER_L_ROUGH if is_rough_chb
                        else PAINT_PRIMER_COVERAGE_M2_PER_L_SMOOTH)

    neutralizer_l = masonry_area / PAINT_PRIMER_COVERAGE_M2_PER_L_SMOOTH
    primer_l = masonry_area / primer_coverage
    topcoat_l = (masonry_area * 2) / PAINT_TOPCOAT_COVERAGE_M2_PER_L  # 2 topcoats

    ceiling_latex_l = ceiling_area / CEILING_LATEX_COVERAGE_M2_PER_L
    metal_primer_l = metal_area / METAL_PRIMER_COVERAGE_M2_PER_L
    metal_enamel_l = metal_area / METAL_ENAMEL_COVERAGE_M2_PER_L

    quantities = {
        "masonry_area_m2": round(masonry_area, 2),
        "ceiling_area_m2": round(ceiling_area, 2),
        "metal_area_m2": round(metal_area, 2),
    }
    materials = {
        "neutralizer_l": round(neutralizer_l, 2),
        "primer_l": round(primer_l, 2),
        "topcoat_l": round(topcoat_l, 2),
        "ceiling_latex_l": round(ceiling_latex_l, 2),
        "metal_primer_l": round(metal_primer_l, 2),
        "metal_enamel_l": round(metal_enamel_l, 2),
    }

    total_paint_area = masonry_area + ceiling_area + metal_area

    costs = _sum_costs(
        _cost_line(materials["neutralizer_l"], "neutralizer_l"),
        _cost_line(materials["primer_l"], "primer_l"),
        _cost_line(materials["topcoat_l"], "topcoat_l"),
        _cost_line(materials["ceiling_latex_l"], "ceiling_latex_l"),
        _cost_line(materials["metal_primer_l"], "metal_primer_l"),
        _cost_line(materials["metal_enamel_l"], "metal_enamel_l"),
        _cost_line(total_paint_area, "paint_labor_m2"),
    )

    labor_manday = round(total_paint_area / 20.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION X — PLUMBING WORKS
# ===========================================================================

def calculate_section_10_plumbing_works(sanitary_run_m: float, water_run_m: float,
                                         fixtures_count: int) -> dict:
    sanitary_4in_pcs = _round_up((sanitary_run_m / PIPE_STD_LENGTH_M) * (1 + UPVC_FITTINGS_ALLOWANCE))
    sanitary_2in_pcs = _round_up((sanitary_run_m * 0.5 / PIPE_STD_LENGTH_M) * (1 + UPVC_FITTINGS_ALLOWANCE))
    ppr_pcs = _round_up((water_run_m / PIPE_STD_LENGTH_M) * (1 + UPVC_FITTINGS_ALLOWANCE))

    quantities = {
        "sanitary_run_m": round(sanitary_run_m, 2),
        "water_run_m": round(water_run_m, 2),
        "fixtures_count": fixtures_count,
    }
    materials = {
        "upvc_4in_pcs": sanitary_4in_pcs,
        "upvc_2in_pcs": sanitary_2in_pcs,
        "ppr_pcs": ppr_pcs,
    }

    costs = _sum_costs(
        _cost_line(sanitary_4in_pcs, "upvc_4in_pc"),
        _cost_line(sanitary_2in_pcs, "upvc_2in_pc"),
        _cost_line(ppr_pcs, "ppr_pipe_pc"),
        _cost_line(fixtures_count, "fixture_set"),
        _cost_line(1, "catch_basin_lot"),
    )

    labor_manday = round((sanitary_run_m + water_run_m) / 20.0 + fixtures_count / 2.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION XI — ELECTRICAL WORKS
# ===========================================================================

def calculate_section_11_electrical_works(outlets_count: int, homerun_m: float) -> dict:
    wire_m = homerun_m * (1 + WIRE_SLACK_ALLOWANCE)
    conduit_pcs = _round_up(homerun_m / CONDUIT_STD_LENGTH_M)

    quantities = {
        "wire_m": round(wire_m, 2),
        "conduit_pcs": conduit_pcs,
        "outlets_count": outlets_count,
    }
    materials = {}

    costs = _sum_costs(
        _cost_line(quantities["wire_m"], "thhn_wire_m"),
        _cost_line(conduit_pcs, "pvc_conduit_pc"),
        _cost_line(outlets_count, "outlet_pc"),
        _cost_line(math.ceil(outlets_count / 3.0), "led_panel_pc"),
        _cost_line(1, "breaker_pc"),
    )

    labor_manday = round(wire_m / 60.0 + outlets_count / 8.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION XII — SANITARY / MECHANICAL WORKS
# ===========================================================================

def calculate_section_12_sanitary_mechanical(room_area_m2: float,
                                              pipe_run_m: float) -> dict:
    btu_required = room_area_m2 * ACU_BTU_PER_M2
    tons_required = btu_required / 12_000.0  # 1 ton = 12,000 BTU/h
    copper_piping_m = pipe_run_m * (1 + COPPER_PIPING_ALLOWANCE)

    quantities = {
        "cooling_load_btu": round(btu_required, 2),
        "acu_tons": round(tons_required, 2),
        "copper_piping_m": round(copper_piping_m, 2),
    }
    materials = {}

    costs = _sum_costs(
        _cost_line(quantities["acu_tons"], "acu_unit_per_ton"),
        _cost_line(quantities["copper_piping_m"], "copper_piping_m"),
        _cost_line(1, "commissioning_lot"),
    )

    labor_manday = round(copper_piping_m / 15.0 + 1.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION XIII — SPECIAL WORKS
# ===========================================================================

def calculate_section_13_special_works(handrail_m: float, acp_m2: float,
                                        waterproofing_m2: float) -> dict:
    acp_with_waste = acp_m2 * (1 + ACP_WASTE)
    waterproofing_kg = waterproofing_m2 * WATERPROOFING_KG_PER_M2

    quantities = {
        "handrail_m": round(handrail_m, 2),
        "acp_cladding_m2": round(acp_with_waste, 2),
        "waterproofing_m2": round(waterproofing_m2, 2),
    }
    materials = {
        "waterproofing_kg": round(waterproofing_kg, 2),
    }

    costs = _sum_costs(
        _cost_line(quantities["handrail_m"], "handrail_m"),
        _cost_line(quantities["acp_cladding_m2"], "acp_cladding_m2"),
        _cost_line(materials["waterproofing_kg"], "waterproofing_kg"),
        _cost_line(quantities["waterproofing_m2"], "waterproofing_labor_m2"),
    )

    labor_manday = round(handrail_m / 10.0 + acp_m2 / 8.0 + waterproofing_m2 / 25.0, 2)

    return {
        "quantities": quantities,
        "materials": materials,
        "labor_manday": labor_manday,
        "equipment_hours": 0.0,
        "cost": costs,
    }


# ===========================================================================
# SECTION I — GENERAL REQUIREMENTS (priced off Sections II-XIII subtotal)
# ===========================================================================

def calculate_section_1_general_requirements(sections_2_to_13_direct_cost: float) -> dict:
    base = sections_2_to_13_direct_cost
    mobilization = base * GENREQ_MOBILIZATION_PCT
    temp_facilities = base * GENREQ_TEMP_FACILITIES_PCT
    safety_ppe = base * GENREQ_SAFETY_PCT
    permits = GENREQ_PERMITS_LOT

    line_items = {
        "mobilization_demobilization": round(mobilization, 2),
        "temporary_facilities": round(temp_facilities, 2),
        "safety_health_ppe": round(safety_ppe, 2),
        "permits_clearances": round(permits, 2),
    }
    total = round(sum(line_items.values()), 2)

    return {
        "quantities": {"basis_direct_cost": round(base, 2)},
        "materials": {},
        "line_items": line_items,
        "labor_manday": 0.0,
        "equipment_hours": 0.0,
        "cost": {"material": 0.0, "labor": 0.0, "equipment": 0.0, "total": total},
    }


# ===========================================================================
# ORCHESTRATOR — full 13-section takeoff
# ===========================================================================

def run_full_takeoff(project_inputs: dict) -> dict:
    """
    project_inputs: a dict keyed by section number (2-13) whose values are
    the keyword-argument dicts for that section's calculate_section_N_*
    function. Section 1 is computed automatically from the II-XIII subtotal.

    Example:
        run_full_takeoff({
            2: {"footing_specs": [...], "slab_area": 120.0, "slab_t": 0.10},
            3: {"elements": [...]},
            4: {"wall_elements": [...]},
            5: {"rebar_elements": [...], "structural_steel_kg": 850.0},
            6: {"roof_plan_area": 140.0, "pitch_deg": 20, "ceiling_area": 130.0},
            7: {"windows_sqm": 18.0, "doors": [...]},
            8: {"floor_area": 110.0, "wall_area": 40.0, "is_diagonal": False},
            9: {"masonry_area": 200.0, "ceiling_area": 130.0, "metal_area": 15.0,
                "is_rough_chb": False},
            10: {"sanitary_run_m": 40.0, "water_run_m": 35.0, "fixtures_count": 6},
            11: {"outlets_count": 24, "homerun_m": 60.0},
            12: {"room_area_m2": 60.0, "pipe_run_m": 15.0},
            13: {"handrail_m": 12.0, "acp_m2": 20.0, "waterproofing_m2": 45.0},
        })
    """
    section_fns = {
        2: calculate_section_2_earthworks,
        3: calculate_section_3_concrete_and_formworks,
        4: calculate_section_4_masonry_works,
        5: calculate_section_5_metals_and_rebar,
        6: calculate_section_6_roofing_and_ceiling,
        7: calculate_section_7_doors_and_windows,
        8: calculate_section_8_tile_and_flooring,
        9: calculate_section_9_painting_works,
        10: calculate_section_10_plumbing_works,
        11: calculate_section_11_electrical_works,
        12: calculate_section_12_sanitary_mechanical,
        13: calculate_section_13_special_works,
    }

    results = {}
    subtotal = 0.0
    for n, fn in section_fns.items():
        kwargs = project_inputs.get(n, {})
        result = fn(**kwargs)
        results[n] = result
        subtotal += result["cost"]["total"]

    results[1] = calculate_section_1_general_requirements(subtotal)

    grand_total = subtotal + results[1]["cost"]["total"]

    return {
        "sections": results,
        "sections_2_to_13_subtotal": round(subtotal, 2),
        "grand_total_direct_cost": round(grand_total, 2),
    }


if __name__ == "__main__":
    # Minimal smoke test using the handbook's own worked examples.
    result = calculate_section_3_concrete_and_formworks([
        {"type": "footing", "class": "A", "count": 4,
         "length_m": 1.50, "width_m": 1.50, "height_m": 0.40},
    ])
    print("Section III smoke test (expect ~3.78 m3 with 5% wastage):")
    print(result["quantities"])
    print(result["materials"])
    print(result["cost"])
