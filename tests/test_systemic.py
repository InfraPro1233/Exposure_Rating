import copy
import json
import unittest
from pathlib import Path

from exposure.systemic import (
    price_change_bound, shared_capacity_floor, shared_capacity_path_bound,
)
from scripts.check_shared_capacity import shared_capacity_tables

ROOT = Path(__file__).resolve().parents[1]
SECTORS = [
    {"name": "first", "human_hours_for_full_workload": 8, "ai_spending_floor_per_quarter": 80},
    {"name": "second", "human_hours_for_full_workload": 12, "ai_spending_floor_per_quarter": 60},
]


class SystemicBoundTests(unittest.TestCase):
    def test_hand_checkable_floors(self):
        for hours, expected in ((0, 140), (5, 90), (8, 60), (10, 50), (15, 25), (20, 0), (30, 0)):
            with self.subTest(hours=hours):
                self.assertEqual(shared_capacity_floor(SECTORS, hours)["residual_ai_spending_floor"], expected)

    def test_floor_holds_across_feasible_shares_not_an_allocation_policy(self):
        for available in (0, 5, 8, 10, 15, 20):
            bound = shared_capacity_floor(SECTORS, available)["residual_ai_spending_floor"]
            for first in (0, 0.25, 0.5, 0.75, 1):
                for second in (0, 0.25, 0.5, 0.75, 1):
                    if 8 * first + 12 * second <= available:
                        residual = 80 * (1 - first) + 60 * (1 - second)
                        self.assertGreaterEqual(residual, bound)

    def test_same_envelope_increases_and_cuts(self):
        # Shared capacity is 5 hours. The joint half-first/quarter-second
        # path would use 7 hours and is deliberately excluded.
        paths = [(200, 140), (250, 100), (225, 125)]
        floor = shared_capacity_floor(SECTORS, 5)["residual_ai_spending_floor"]
        baseline = min(fixed + spend for fixed, spend in paths)
        for price in (0.5, 0.75, 1, 1.25, 2, 3):
            change = min(fixed + price * spend for fixed, spend in paths) - baseline
            result = price_change_bound(floor, 1, price)
            if result["cost_change_lower_bound"] is not None:
                self.assertGreaterEqual(change, result["cost_change_lower_bound"])
            if result["cost_change_upper_bound"] is not None:
                self.assertLessEqual(change, result["cost_change_upper_bound"])

    def test_zero_ai_floor_can_remove_positive_shortage_bound(self):
        sectors = [
            {"name": "first", "human_hours_for_full_workload": 8, "ai_spending_floor_per_quarter": 0},
            {"name": "second", "human_hours_for_full_workload": 12, "ai_spending_floor_per_quarter": 60},
        ]
        result = shared_capacity_floor(sectors, 12)
        self.assertEqual(result["human_hours_shortfall"], 8)
        self.assertEqual(result["residual_ai_spending_floor"], 0)

    def test_less_available_capacity_cannot_lower_floor(self):
        floors = [shared_capacity_floor(SECTORS, hours)["residual_ai_spending_floor"]
                  for hours in range(26)]
        self.assertEqual(floors, sorted(floors, reverse=True))
        self.assertTrue(all(value >= 0 for value in floors))

    def test_bound_can_be_attained_by_a_supplied_path(self):
        sectors = [{"name": "one", "human_hours_for_full_workload": 10,
                    "ai_spending_floor_per_quarter": 100}]
        floor = shared_capacity_floor(sectors, 5)["residual_ai_spending_floor"]
        # Retained labour is already covered by fixed cost in this witness.
        paths = [(20, 100), (20, 50)]
        baseline = min(fixed + spend for fixed, spend in paths)
        for price in (0.5, 1, 2, 3):
            change = min(fixed + price * spend for fixed, spend in paths) - baseline
            result = price_change_bound(floor, 1, price)
            expected = (price - 1) * 50
            self.assertEqual(change, expected)
            self.assertEqual(result["cost_change_lower_bound"] if price >= 1
                             else result["cost_change_upper_bound"], expected)

    def test_transition_exposure_is_not_ending_dependence(self):
        settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))
        experiment = settings["shared_capacity_experiment"]
        result = shared_capacity_path_bound(experiment["sector_workloads"],
                                           experiment["capacity_schedules"]["restoration_with_transition"])
        self.assertEqual(result["summary"]["discounted_residual_ai_spending_floor"], 1070)
        self.assertEqual(result["summary"]["end_quarter_spending_floor"], 0)
        self.assertEqual(result["summary"]["end_quarter_human_hours_shortfall"], 0)

    def test_discounting_and_scaling(self):
        result = shared_capacity_path_bound(SECTORS, [5, 5], 0.1)
        self.assertAlmostEqual(result["summary"]["discounted_residual_ai_spending_floor"],
                               sum(90 / 1.1 ** (t / 4) for t in (1, 2)))
        scaled = [{**sector, "human_hours_for_full_workload": 3 * sector["human_hours_for_full_workload"],
                   "ai_spending_floor_per_quarter": 3 * sector["ai_spending_floor_per_quarter"]}
                  for sector in SECTORS]
        self.assertEqual(shared_capacity_floor(scaled, 15)["residual_ai_spending_floor"], 270)
        self.assertEqual(shared_capacity_floor(reversed(SECTORS), 5)["residual_ai_spending_floor"], 90)

    def test_invalid_inputs(self):
        invalid = (
            ([], 1), (SECTORS, -1), (SECTORS, float("inf")),
            ([SECTORS[0], SECTORS[0]], 1),
            ([{**SECTORS[0], "human_hours_for_full_workload": 0}], 1),
            ([{**SECTORS[0], "ai_spending_floor_per_quarter": -1}], 1),
            ([{**SECTORS[0], "human_hours_for_full_workload": 1e-308,
               "ai_spending_floor_per_quarter": 1e308}], 1),
        )
        for sectors, hours in invalid:
            with self.subTest(sectors=sectors, hours=hours), self.assertRaises(ValueError):
                shared_capacity_floor(sectors, hours)
        with self.assertRaises(ValueError):
            shared_capacity_path_bound(SECTORS, [])
        with self.assertRaises(ValueError):
            price_change_bound(90, 1, 0)

    def test_declared_tables_and_input_immutability(self):
        settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))
        original = copy.deepcopy(settings)
        summaries, quarters = shared_capacity_tables(settings)
        self.assertEqual(settings, original)
        self.assertEqual((len(summaries), len(quarters)), (27, 60))
        doubled = {row["capacity_profile"]: row for row in summaries if row["price_after"] == 2}
        self.assertEqual(doubled["persistent_shortage"]["cost_change_lower_bound"], 1800)
        self.assertEqual(doubled["capacity_available"]["cost_change_lower_bound"], 0)
        self.assertEqual(doubled["restoration_with_transition"]["cost_change_lower_bound"], 1070)
        settings["shared_capacity_experiment"]["capacity_schedules"]["capacity_available"] = [20]
        with self.assertRaises(ValueError):
            shared_capacity_tables(settings)


if __name__ == "__main__":
    unittest.main()
