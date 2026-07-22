"""
Plan2Takeoff V2 — Fajardo Quantity Takeoff & Direct Costing Engine
Based on Max Fajardo's Simplified Construction Estimate and Philippine DPWH CMPD Rates.

Supported Trades (CSI MasterFormat / DPWH Categories):
- Division 02: Earthworks (Excavation, Gravel Bedding, Backfill)
- Division 03: Concrete Works & Formworks (Footings, Columns, Beams, Slabs, Forms)
- Division 04: Masonry Works (100mm & 150mm CHB, Mortar Laying, Plastering)
- Division 05: Metals & Reinforcement (Deformed Rebar Grade 40/60, G.I. Tie Wire)
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ====================================================================
# FAJARDO FORMULA LIBRARY REFERENCE FACTORS
# ====================================================================

# 1. Concrete Mix Factors per 1.0 cu.m. (40kg Cement Bag Standard)
CONCRETE_MIX_FACTORS = {
    "Class AA": {"cement_bags": 12.0, "sand_m3": 0.50, "gravel_m3": 1.00},
    "Class A":  {"cement_bags": 9.00, "sand_m3": 0.50, "gravel_m3": 1.00},
    "Class B":  {"cement_bags": 7.50, "sand_m3": 0.50, "gravel_m3": 1.00},
    "Class C":  {"cement_bags": 6.00, "sand_m3": 0.50, "gravel_m3": 1.00},
}

# 2. Rebar Theoretical Unit Weights (kg/m) based on PNS 49 / ASTM A615 (D^2 / 162.2)
REBAR_UNIT_WEIGHTS = {
    10: 0.617,
    12: 0.888,
    16: 1.578,
    20: 2.466,
    25: 3.853,
    28: 4.834,
    32: 6.313,
}

# Tie wire factor (#16 G.I. wire kg per kg of rebar)
TIE_WIRE_FACTOR = 0.015  # 15kg per metric ton

# 3. Masonry factors per 1.0 sq.m. of net wall surface area.
MORTAR_CLASS_CEMENT_BAGS_PER_M3 = {
    "Class A": 18.0,
    "Class B": 12.0,
    "Class C": 9.0,
    "Class D": 7.5,
}

CHB_COUNT_PER_SQM = 12.5  # Constant for 100mm and 150mm CHB

MORTAR_CLASS_B_FACTORS = {
    "100mm": {"cement_bags": 0.522, "sand_m3": 0.0435},
    "150mm": {"cement_bags": 1.010, "sand_m3": 0.0840},
}

PLASTER_CLASS_B_FACTORS_PER_FACE = {
    "16mm": {"cement_bags": 0.192, "sand_m3": 0.016}
}

# 4. Formwork factors (Plywood & Lumber per sq.m. of contact area)
FORMWORK_FACTORS = {
    "plywood_sheets_per_sqm": 0.28,  # 1/4" or 1/2" Marine Plywood
    "lumber_bdft_per_sqm": 7.0,      # 2x2 or 2x3 Form Lumber
}

QA_DIVERGENCE_THRESHOLD = 0.02

# DPWH Construction Materials Price Data (CMPD) & Labor Productivity Matrix
DPWH_CMPD_RATES = {
    # Materials
    "Cement (40kg bag)": 205.36,          # MG03.0002 PORTLAND CEMENT
    "Sand (cu.m.)": 1473.21,              # MG01.0008 FINE AGGREGATE
    "Gravel (cu.m.)": 1517.86,            # MG01.0009 GRAVEL 3/4"
    "Rebar (per kg)": 42.68,              # MG10.0001 REINFORCING STEEL BAR (GRADE 40)
    "Tie Wire #16 G.I. (per kg)": 62.50,  # MG10.0003 GI TIE WIRE #16
    "100mm CHB (per pc)": 15.18,           # MG04.0003 CHB ORDINARY 4"
    "150mm CHB (per pc)": 22.32,           # MG04.0004 CHB ORDINARY 6"
    "Marine Plywood 1/2 (per sheet)": 750.0,# Formwork Plywood
    "Form Lumber (per bdft)": 45.0,       # Form Lumber 2x2 / 2x3
    
    # Labor & Equipment Productivity Rates (DPWH DO standard crew costs)
    "Concrete Labor (per cu.m.)": 850.0,
    "Concrete Equipment (per cu.m.)": 250.0,  # Bagger Mixer + Vibrator
    "Rebar Labor (per kg)": 12.0,
    "Rebar Equipment (per kg)": 2.50,         # Bar Cutter + Bar Bender
    "Masonry Labor (per sq.m.)": 240.0,
    "Masonry Equipment (per sq.m.)": 15.0,
    "Earthworks Labor (per cu.m.)": 350.0,
    "Formworks Labor (per sq.m.)": 280.0,
}


@dataclass
class TakeoffElementV2:
    element_id: str
    element_type: str  # 'footing', 'column', 'beam', 'slab', 'chb_wall', 'excavation', 'formwork'
    label: str
    location: str
    drawing_ref: str
    length: float
    width: float
    height_or_thickness: float
    count: int = 1
    concrete_class: str = "Class A"
    rebar_specs: List[Dict[str, Any]] = field(default_factory=list)
    chb_thickness: str = "150mm"
    plaster_faces: int = 2
    mortar_class: str = "Class B"
    plaster_class: str = "Class B"
    opening_area: float = 0.0
    bounding_box: List[float] = field(default_factory=list)  # [x1, y1, x2, y2] on blueprint


@dataclass
class BackupComputationRowV2:
    division: str  # 'Division 02 — Earthworks', 'Division 03 — Concrete & Formwork', etc.
    item_code: str
    description: str
    location: str
    drawing_ref: str
    length: float
    width: float
    height: float
    count: float
    quantity: float
    unit: str  # 'cu.m.', 'sq.m.', 'kg', 'pc', 'sheet', 'bdft'
    material_unit_cost: float = 0.0
    labor_unit_cost: float = 0.0
    equipment_unit_cost: float = 0.0
    total_unit_cost: float = 0.0
    total_amount: float = 0.0
    status: str = "Confirmed"


@dataclass
class BOQAccordionItemV2:
    item_no: str
    item_code: str
    division: str
    description: str
    unit: str
    qty: float
    material_unit_cost: float = 0.0
    labor_unit_cost: float = 0.0
    equipment_unit_cost: float = 0.0
    total_unit_cost: float = 0.0
    total_amount: float = 0.0
    status: str = "Confirmed"


class FajardoTakeoffEngineV2:
    def __init__(self, rates_override: Optional[Dict[str, float]] = None):
        self.rates = dict(DPWH_CMPD_RATES)
        if rates_override:
            self.rates.update(rates_override)
        self.backup_rows: List[BackupComputationRowV2] = []

    def compute_element(self, elem: TakeoffElementV2) -> List[BackupComputationRowV2]:
        """Compute takeoff for an element across material, labor, and equipment."""
        rows = []
        elem_type = elem.element_type.lower()

        # Division 02: Earthworks
        if elem_type == 'excavation':
            vol = elem.length * elem.width * elem.height_or_thickness * elem.count
            l_cost = self.rates["Earthworks Labor (per cu.m.)"]
            row = BackupComputationRowV2(
                division="Division 02 — Earthworks",
                item_code="EXC-2.1",
                description=f"Structural Excavation ({elem.label})",
                location=elem.location,
                drawing_ref=elem.drawing_ref,
                length=elem.length, width=elem.width, height=elem.height_or_thickness,
                count=elem.count, quantity=vol, unit="cu.m.",
                material_unit_cost=0.0, labor_unit_cost=l_cost, equipment_unit_cost=0.0,
                total_unit_cost=l_cost, total_amount=vol * l_cost
            )
            rows.append(row)

        # Division 03: Concrete & Formwork
        elif elem_type in ['footing', 'column', 'beam', 'slab']:
            vol = elem.length * elem.width * elem.height_or_thickness * elem.count
            mix = CONCRETE_MIX_FACTORS.get(elem.concrete_class, CONCRETE_MIX_FACTORS["Class A"])
            
            # Concrete Volume Row
            c_mat = mix["cement_bags"] * self.rates["Cement (40kg bag)"] + \
                    mix["sand_m3"] * self.rates["Sand (cu.m.)"] + \
                    mix["gravel_m3"] * self.rates["Gravel (cu.m.)"]
            c_lab = self.rates["Concrete Labor (per cu.m.)"]
            c_eqp = self.rates["Concrete Equipment (per cu.m.)"]
            total_uc = c_mat + c_lab + c_eqp

            code_map = {'footing': 'CON-3.1', 'column': 'CON-3.2', 'beam': 'CON-3.3', 'slab': 'CON-3.4'}
            row_conc = BackupComputationRowV2(
                division="Division 03 — Concrete & Formwork",
                item_code=code_map.get(elem_type, 'CON-3.5'),
                description=f"Concrete Works ({elem.label}, {elem.concrete_class})",
                location=elem.location,
                drawing_ref=elem.drawing_ref,
                length=elem.length, width=elem.width, height=elem.height_or_thickness,
                count=elem.count, quantity=vol, unit="cu.m.",
                material_unit_cost=c_mat, labor_unit_cost=c_lab, equipment_unit_cost=c_eqp,
                total_unit_cost=total_uc, total_amount=vol * total_uc
            )
            rows.append(row_conc)

            # Rebar if specified
            for rspec in elem.rebar_specs:
                dia = rspec.get('diameter', 16)
                cnt = rspec.get('count', 4)
                length = rspec.get('length', elem.length)
                weight_per_m = REBAR_UNIT_WEIGHTS.get(dia, 0.617)
                total_length = length * cnt * elem.count
                total_weight = total_length * weight_per_m

                r_mat = self.rates["Rebar (per kg)"]
                r_lab = self.rates["Rebar Labor (per kg)"]
                r_eqp = self.rates["Rebar Equipment (per kg)"]
                r_uc = r_mat + r_lab + r_eqp

                row_reb = BackupComputationRowV2(
                    division="Division 05 — Metals & Rebar",
                    item_code=f"REB-5.{dia}",
                    description=f"Deformed Rebar {dia}mm ({elem.label})",
                    location=elem.location,
                    drawing_ref=elem.drawing_ref,
                    length=length, width=0, height=0, count=cnt * elem.count,
                    quantity=total_weight, unit="kg",
                    material_unit_cost=r_mat, labor_unit_cost=r_lab, equipment_unit_cost=r_eqp,
                    total_unit_cost=r_uc, total_amount=total_weight * r_uc
                )
                rows.append(row_reb)

        # Division 04: Masonry Works
        elif elem_type == 'chb_wall':
            gross_area = elem.length * elem.height_or_thickness * elem.count
            net_area = max(0.0, gross_area - (elem.opening_area * elem.count))
            chb_count = net_area * CHB_COUNT_PER_SQM

            chb_price_key = "150mm CHB (per pc)" if elem.chb_thickness == "150mm" else "100mm CHB (per pc)"
            m_mat = self.rates.get(chb_price_key, 22.32)
            m_lab = self.rates["Masonry Labor (per sq.m.)"] / CHB_COUNT_PER_SQM
            m_eqp = self.rates["Masonry Equipment (per sq.m.)"] / CHB_COUNT_PER_SQM
            m_uc = m_mat + m_lab + m_eqp

            row_chb = BackupComputationRowV2(
                division="Division 04 — Masonry Works",
                item_code="MAS-4.1",
                description=f"{elem.chb_thickness} Concrete Hollow Blocks ({elem.label})",
                location=elem.location,
                drawing_ref=elem.drawing_ref,
                length=elem.length, width=0, height=elem.height_or_thickness,
                count=elem.count, quantity=chb_count, unit="pc",
                material_unit_cost=m_mat, labor_unit_cost=m_lab, equipment_unit_cost=m_eqp,
                total_unit_cost=m_uc, total_amount=chb_count * m_uc
            )
            rows.append(row_chb)

        self.backup_rows.extend(rows)
        return rows

    def consolidate_boq(self) -> List[BOQAccordionItemV2]:
        """Roll up backup rows into consolidated trade accordions."""
        summaries: Dict[str, Dict[str, Any]] = {}
        for r in self.backup_rows:
            key = f"{r.division}::{r.item_code}::{r.description}"
            if key not in summaries:
                summaries[key] = {
                    "division": r.division,
                    "item_code": r.item_code,
                    "description": r.description,
                    "unit": r.unit,
                    "qty": 0.0,
                    "mat_cost": r.material_unit_cost,
                    "lab_cost": r.labor_unit_cost,
                    "eqp_cost": r.equipment_unit_cost,
                    "total_uc": r.total_unit_cost,
                    "amount": 0.0
                }
            summaries[key]["qty"] += r.quantity
            summaries[key]["amount"] += r.total_amount

        result = []
        for idx, (k, v) in enumerate(summaries.items(), 1):
            result.append(BOQAccordionItemV2(
                item_no=str(idx),
                item_code=v["item_code"],
                division=v["division"],
                description=v["description"],
                unit=v["unit"],
                qty=round(v["qty"], 2),
                material_unit_cost=round(v["mat_cost"], 2),
                labor_unit_cost=round(v["lab_cost"], 2),
                equipment_unit_cost=round(v["eqp_cost"], 2),
                total_unit_cost=round(v["total_uc"], 2),
                total_amount=round(v["amount"], 2)
            ))
        return result
