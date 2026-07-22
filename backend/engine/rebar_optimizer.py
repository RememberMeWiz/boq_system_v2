"""
Plan2Takeoff V2 — 1D Commercial Rebar Cutting Stock Optimizer
Uses First Fit Decreasing (FFD) Bin-Packing Algorithm to minimize cutting scrap
across standard commercial steel bar stock lengths (6m, 9m, 12m).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class RebarCutDemand:
    diameter_mm: int
    required_length_m: float
    quantity: int
    element_ref: str = ""


@dataclass
class CommercialBarPattern:
    stock_length_m: float
    cuts: List[float]
    scrap_m: float
    utilization_pct: float


@dataclass
class OptimizationResult:
    diameter_mm: int
    total_required_weight_kg: float
    total_purchased_weight_kg: float
    total_scrap_weight_kg: float
    scrap_percentage: float
    purchased_bars: Dict[float, int]  # e.g. {6.0: 10, 9.0: 5, 12.0: 20}
    patterns: List[CommercialBarPattern]


# PNS 49 Theoretical Rebar Weights (kg/m)
REBAR_UNIT_WEIGHTS = {
    10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853, 28: 4.834, 32: 6.313
}

AVAILABLE_STOCK_LENGTHS = [12.0, 9.0, 6.0]  # Preferred largest first for max efficiency


class RebarStockOptimizer:
    def __init__(self, stock_lengths: List[float] = None):
        self.stock_lengths = sorted(stock_lengths or AVAILABLE_STOCK_LENGTHS, reverse=True)

    def optimize_diameter(self, diameter_mm: int, demands: List[RebarCutDemand]) -> OptimizationResult:
        """Runs 1D Bin Packing for a single rebar diameter."""
        unit_weight = REBAR_UNIT_WEIGHTS.get(diameter_mm, 0.617)

        # Expand demand list into individual cuts
        all_cuts = []
        for d in demands:
            for _ in range(d.quantity):
                all_cuts.append(d.required_length_m)

        # Sort cuts in descending order for First Fit Decreasing
        all_cuts.sort(reverse=True)

        patterns: List[CommercialBarPattern] = []
        purchased_counts = {sl: 0 for sl in self.stock_lengths}

        remaining_cuts = list(all_cuts)

        while remaining_cuts:
            best_pattern = None
            best_stock_len = None
            min_scrap = float('inf')

            # Try to pack into the best matching stock length
            for stock_len in self.stock_lengths:
                temp_cuts = []
                temp_remaining = list(remaining_cuts)
                current_used = 0.0

                idx = 0
                while idx < len(temp_remaining):
                    cut_len = temp_remaining[idx]
                    if current_used + cut_len <= stock_len:
                        current_used += cut_len
                        temp_cuts.append(cut_len)
                        temp_remaining.pop(idx)
                    else:
                        idx += 1

                if temp_cuts:
                    scrap = stock_len - current_used
                    if scrap < min_scrap:
                        min_scrap = scrap
                        best_stock_len = stock_len
                        best_pattern = CommercialBarPattern(
                            stock_length_m=stock_len,
                            cuts=temp_cuts,
                            scrap_m=scrap,
                            utilization_pct=round((current_used / stock_len) * 100, 2)
                        )

            if best_pattern:
                patterns.append(best_pattern)
                purchased_counts[best_stock_len] += 1
                # Remove cuts included in best pattern from remaining_cuts
                for c in best_pattern.cuts:
                    remaining_cuts.remove(c)
            else:
                # If cut is longer than max stock (e.g. > 12m), split with lap splice
                break

        # Calculate metrics
        total_req_len = sum(all_cuts)
        total_purchased_len = sum(p.stock_length_m for p in patterns)
        total_scrap_len = sum(p.scrap_m for p in patterns)

        total_req_wt = total_req_len * unit_weight
        total_purch_wt = total_purchased_len * unit_weight
        total_scrap_wt = total_scrap_len * unit_weight
        scrap_pct = (total_scrap_len / total_purchased_len * 100) if total_purchased_len > 0 else 0.0

        return OptimizationResult(
            diameter_mm=diameter_mm,
            total_required_weight_kg=round(total_req_wt, 2),
            total_purchased_weight_kg=round(total_purch_wt, 2),
            total_scrap_weight_kg=round(total_scrap_wt, 2),
            scrap_percentage=round(scrap_pct, 2),
            purchased_bars=purchased_counts,
            patterns=patterns
        )
