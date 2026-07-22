"""
Plan2Takeoff V2 — Unit Test Suite
Validates Fajardo Takeoff & Direct Cost calculations and 1D Rebar Stock Optimizer.
"""

import unittest
from backend.engine.fajardo import FajardoTakeoffEngineV2, TakeoffElementV2, CONCRETE_MIX_FACTORS, CHB_COUNT_PER_SQM
from backend.engine.rebar_optimizer import RebarStockOptimizer, RebarCutDemand


class TestFajardoEngineV2(unittest.TestCase):
    def test_concrete_direct_cost(self):
        engine = FajardoTakeoffEngineV2()
        elem = TakeoffElementV2(
            element_id="F1", element_type="footing", label="F-1", location="Grid A-1",
            drawing_ref="S-1", length=2.0, width=2.0, height_or_thickness=0.50, count=2,
            concrete_class="Class A"
        )
        rows = engine.compute_element(elem)
        self.assertEqual(len(rows), 1)
        row = rows[0]

        expected_vol = 2.0 * 2.0 * 0.50 * 2  # 4.0 cu.m.
        self.assertAlmostEqual(row.quantity, expected_vol)
        self.assertEqual(row.unit, "cu.m.")
        self.assertGreater(row.material_unit_cost, 0.0)
        self.assertGreater(row.labor_unit_cost, 0.0)
        self.assertGreater(row.total_amount, 0.0)

    def test_chb_wall_takeoff(self):
        engine = FajardoTakeoffEngineV2()
        elem = TakeoffElementV2(
            element_id="W1", element_type="chb_wall", label="W-1", location="Grid 1",
            drawing_ref="A-1", length=10.0, width=0.15, height_or_thickness=3.0, count=1,
            chb_thickness="150mm", opening_area=3.0
        )
        rows = engine.compute_element(elem)
        self.assertEqual(len(rows), 1)
        row = rows[0]

        net_area = (10.0 * 3.0) - 3.0  # 27.0 sq.m.
        expected_pcs = net_area * CHB_COUNT_PER_SQM  # 337.5 pcs
        self.assertAlmostEqual(row.quantity, expected_pcs)
        self.assertEqual(row.unit, "pc")


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
