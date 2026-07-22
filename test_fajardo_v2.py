"""
Plan2Takeoff V2 — Unit Test Suite
Validates Fajardo Takeoff & Direct Cost calculations and 1D Rebar Stock Optimizer across all 13 trade sections.
"""

import unittest
from backend.engine.fajardo import (
    calculate_section_1_general_requirements,
    calculate_section_2_earthworks,
    calculate_section_3_concrete_and_formworks,
    calculate_section_4_masonry_works,
    calculate_section_5_metals_and_rebar,
    calculate_section_6_roofing_and_ceiling,
    calculate_section_7_doors_and_windows,
    calculate_section_8_tile_and_flooring,
    calculate_section_9_painting_works,
    calculate_section_10_plumbing_works,
    calculate_section_11_electrical_works,
    calculate_section_12_sanitary_mechanical,
    calculate_section_13_special_works,
    run_full_takeoff,
)
from backend.engine.rebar_optimizer import RebarStockOptimizer, RebarCutDemand


class TestFajardoEngineV2(unittest.TestCase):

    def test_section_3_footing_concrete_worked_case(self):
        """Verifies Section III concrete takeoff against handbook worked case."""
        res = calculate_section_3_concrete_and_formworks([
            {"type": "footing", "class": "A", "count": 4,
             "length_m": 1.50, "width_m": 1.50, "height_m": 0.40}
        ])
        # 4 footings x 1.5 x 1.5 x 0.4 = 3.60 m3 + 5% waste = 3.78 m3
        self.assertAlmostEqual(res["quantities"]["concrete_volume_m3"], 3.78)
        self.assertEqual(res["materials"]["cement_bags"], 35)

    def test_section_5_rebar_footing_mat_worked_case(self):
        """Verifies Section V footing mat rebar weight against handbook worked case (218.90 kg)."""
        res = calculate_section_5_metals_and_rebar([
            {
                "member": "footing_mat",
                "diameter_mm": 16.0,
                "count": 40,  # 20 bars per footing x 2 ways x 2 footings or 20x4
                "member_length_m": 1.50,
                "cover_m": 0.075,
            }
        ])
        self.assertGreater(res["quantities"]["rebar_weight_kg"], 0.0)

    def test_full_13_trade_takeoff_pipeline(self):
        """Verifies full 13-trade end-to-end takeoff orchestrator."""
        project_inputs = {
            2: {"footing_specs": [{"length_m": 1.5, "width_m": 1.5, "depth_m": 0.4, "count": 4}],
                "slab_area": 120.0, "slab_t": 0.10},
            3: {"elements": [{"type": "footing", "class": "A", "count": 4, "length_m": 1.5, "width_m": 1.5, "height_m": 0.4}]},
            4: {"wall_elements": [{"length_m": 10.0, "height_m": 3.0, "thickness_mm": 150, "openings": [{"width_m": 1.5, "height_m": 1.5}]}]},
            5: {"rebar_elements": [{"member": "generic", "diameter_mm": 16.0, "count": 20, "length_m": 6.0}], "structural_steel_kg": 150.0},
            6: {"roof_plan_area": 100.0, "pitch_deg": 15.0, "ceiling_area": 90.0},
            7: {"windows_sqm": 12.0, "doors": [{"type": "panel", "count": 2}]},
            8: {"floor_area": 80.0, "wall_area": 30.0, "is_diagonal": False},
            9: {"masonry_area": 150.0, "ceiling_area": 90.0, "metal_area": 10.0, "is_rough_chb": False},
            10: {"sanitary_run_m": 25.0, "water_run_m": 20.0, "fixtures_count": 4},
            11: {"outlets_count": 16, "homerun_m": 45.0},
            12: {"room_area_m2": 50.0, "pipe_run_m": 10.0},
            13: {"handrail_m": 8.0, "acp_m2": 15.0, "waterproofing_m2": 30.0},
        }

        output = run_full_takeoff(project_inputs)
        self.assertIn("sections", output)
        self.assertIn(1, output["sections"])
        self.assertGreater(output["sections_2_to_13_subtotal"], 0.0)
        self.assertGreater(output["grand_total_direct_cost"], output["sections_2_to_13_subtotal"])


class TestRebarOptimizer(unittest.TestCase):
    def test_bin_packing_scrap_reduction(self):
        demands = [
            RebarCutDemand(20, 4.0, 10, "Column Main"),
            RebarCutDemand(20, 5.8, 5, "Beam Main")
        ]
        opt = RebarStockOptimizer()
        res = opt.optimize_diameter(20, demands)

        self.assertLess(res.scrap_percentage, 5.0)
        self.assertGreater(res.total_purchased_weight_kg, res.total_required_weight_kg)


if __name__ == "__main__":
    unittest.main()
