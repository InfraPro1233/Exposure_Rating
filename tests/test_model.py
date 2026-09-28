import contextlib
import csv
import io
import json
import math
import random
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from exposure.cost import agent_cost_components, effective_cost, price_exposure, production_cost, relative_exposure
from exposure.portfolio import cheapest_configuration, portfolio_costs, portfolio_exposure
from exposure.provider import optimal_provider_price, provider_profit, provider_revenue
from exposure.restoration import compare_paths, path_price_exposure, simulate_path
from exposure.threshold import adoption_threshold, cheapest_path, cost_crossing, outside_option_threshold, restoration_cost
from scripts.run_model import ROOT, main


class CostTests(unittest.TestCase):
    def test_original_example(self):
        self.assertEqual(effective_cost(12, 0.6), 20)
        baseline = production_cost(1000, 0.75, 20, 80)
        shocked = production_cost(1000, 0.75, 30, 80)
        self.assertEqual((baseline, shocked), (35000, 42500))
        self.assertAlmostEqual(relative_exposure(baseline, shocked), 0.21428571428571427)

    def test_invalid_inputs(self):
        for cost, rate in ((-1, 0.5), (1, 0), (1, 1.1), (math.nan, 0.5)):
            with self.subTest(cost=cost, rate=rate), self.assertRaises(ValueError):
                effective_cost(cost, rate)
        with self.assertRaises(ValueError):
            production_cost(1, 1.1, 20, 80)
        with self.assertRaises(ValueError):
            relative_exposure(0, 0)
        with self.assertRaises(ValueError):
            price_exposure(100, 0)

    def test_fixed_mix_identity_and_scaling(self):
        for adoption in (0, 0.1, 0.75, 1):
            for price in (0.5, 1, 3):
                baseline = production_cost(1000, adoption, 20, 80)
                shocked = production_cost(1000, adoption, price * 20, 80)
                self.assertAlmostEqual(shocked - baseline, price_exposure(1000 * adoption * 20, price))
                self.assertAlmostEqual(relative_exposure(baseline, shocked),
                                       relative_exposure(baseline * 10, shocked * 10))

    def test_review_not_price_shocked(self):
        execution, other = agent_cost_components(1, 0.5, review_hours=0.25, review_wage=20, rework=2)
        self.assertEqual((execution, other), (2, 14))


class ThresholdTests(unittest.TestCase):
    def test_boundary_cases(self):
        self.assertAlmostEqual(outside_option_threshold(100, 80, [(180, 20)]), 4 / 3)
        self.assertEqual(outside_option_threshold(100, 80, [(80, 100)]), 1)
        self.assertEqual(outside_option_threshold(100, 80, []), math.inf)
        self.assertEqual(outside_option_threshold(100, 80, [(110, 90)]), math.inf)
        self.assertEqual(outside_option_threshold(100, 0, [(90, 0)]), 1)
        self.assertEqual(outside_option_threshold(100, 0, [(110, 0)]), math.inf)

    def test_human_capacity_rival_cap(self):
        for capacity in (0, 0.25, 0.5, 0.75, 0.9, 1):
            human = 200 + restoration_cost(capacity, 200)
            no_rival = outside_option_threshold(100, 80, [(human, 0)])
            with_rival = outside_option_threshold(100, 80, [(human, 0), (180, 20)])
            self.assertAlmostEqual(no_rival, 3.75 - 2.5 * capacity)
            self.assertAlmostEqual(with_rival, min(no_rival, 4 / 3))

    def test_root_statuses(self):
        self.assertEqual(cost_crossing((1, 1), (1, 1))["status"], "non_unique")
        self.assertEqual(cost_crossing((1, 1), (2, 1))["status"], "no_crossing")
        self.assertEqual(cost_crossing((10, 1), (0, 0))["status"], "no_positive_root")
        root = adoption_threshold(20, 80, price_range=(0.5, 3))
        self.assertEqual(root, {"root": 4, "status": "positive_root", "range_status": "above_range"})

    def test_ties_are_exact_and_first_listed(self):
        paths = [(100, 80), (180, 20)]
        self.assertEqual(cheapest_path(paths, Fraction(4, 3)), paths[0])
        self.assertEqual(cheapest_path(reversed(paths), Fraction(4, 3)), paths[1])
        with self.assertRaises(ValueError):
            cheapest_path(iter([]), 1)

    def test_larger_incumbent_spend_can_lower_threshold(self):
        self.assertGreater(outside_option_threshold(100, 80, [(300, 0)]),
                           outside_option_threshold(100, 160, [(300, 0)]))

    def test_random_positive_roots(self):
        rng = random.Random(1)
        for _ in range(100):
            fixed, spend = rng.uniform(0, 100), rng.uniform(1, 100)
            alt_fixed = fixed + spend + rng.uniform(1, 100)
            alt_spend = rng.uniform(0, spend / 2)
            root = outside_option_threshold(fixed, spend, [(alt_fixed, alt_spend)])
            self.assertAlmostEqual(fixed + root * spend, alt_fixed + root * alt_spend)


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.sectors = [[(100, 80), (180, 20), (300, 0)], [(100, 80), (260, 0)]]

    def test_original_revenue_profit(self):
        self.assertEqual(provider_revenue(self.sectors, 1), 160)
        self.assertEqual(provider_revenue(self.sectors, 1.5), 150)
        self.assertEqual(provider_profit(self.sectors, 1, 0.25), 120)
        self.assertEqual(provider_profit(self.sectors, 1.5, 0.25), 125)

    def test_exact_global_maximum(self):
        result = optimal_provider_price(self.sectors, 0.25)
        self.assertEqual(result["status"], "maximum")
        self.assertEqual((result["price"], result["profit"]), (2, 175))
        for index in range(1, 1000):
            self.assertLessEqual(provider_profit(self.sectors, index / 100, 0.25), result["profit"] + 1e-9)

    def test_unbounded(self):
        result = optimal_provider_price([[(100, 80), (180, 20)]], 0.25)
        self.assertEqual(result["status"], "unbounded")
        self.assertEqual(result["profit"], math.inf)
        self.assertIsNone(result["price"])

    def test_supremum_not_attained(self):
        result = optimal_provider_price([[(200, 0), (0, 100)]], 0.25)
        self.assertEqual(result["status"], "supremum_not_attained")
        self.assertEqual((result["price"], result["profit"], result["boundary_side"]), (2, 175, "left"))
        self.assertEqual(provider_profit([[(200, 0), (0, 100)]], 2, 0.25), 0)

    def test_zero_provider_spend_and_validation(self):
        self.assertEqual(optimal_provider_price([[(100, 0)]], 0.25)["profit"], 0)
        with self.assertRaises(ValueError):
            provider_profit(self.sectors, 1, -0.25)
        with self.assertRaises(ValueError):
            optimal_provider_price([], 0.25)

    def test_flat_zero_demand_maximum_is_attained(self):
        sectors = [[(0, 100), (200, 0)]]
        result = optimal_provider_price(sectors, 10)
        self.assertEqual(result["status"], "maximum")
        self.assertEqual(result["profit"], 0)
        self.assertEqual(provider_profit(sectors, Fraction(result["price_exact"]), 10), 0)

    def test_rational_price_can_be_reconstructed_exactly(self):
        sectors = [[(0, 3), (5, 0)]]
        result = optimal_provider_price(sectors, 0)
        self.assertEqual(result["price_exact"], "5/3")
        self.assertEqual(provider_profit(sectors, Fraction(result["price_exact"]), 0), 5)

    def test_first_switch_need_not_be_profit_optimum(self):
        incumbent, rival, human = (100, 80), (180, 20), (400, 0)
        threshold = outside_option_threshold(*incumbent, [rival, human])
        optimum = optimal_provider_price([[incumbent, rival, human]], 0.25)
        self.assertAlmostEqual(threshold, 4 / 3)
        self.assertEqual((optimum["price"], optimum["profit"]), (11, 215))
        self.assertEqual(optimum["status"], "maximum")
        self.assertGreater(optimum["price"], threshold)


class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.configs = {
            "a": {"provider": "A", "execution_cost": 10},
            "b": {"provider": "B", "execution_cost": 20},
        }

    def test_provider_spending_not_output_shares(self):
        result = portfolio_costs(self.configs, {"a": 0.5, "b": 0.5})
        self.assertEqual(result["provider_output_shares"], {"A": 0.5, "B": 0.5})
        self.assertEqual(result["provider_spend"], {"A": 5, "B": 10})

    def test_shock_superposition(self):
        result = portfolio_exposure(100, 0.75, 80, self.configs, {"a": 0.5, "b": 0.5}, {"A": 2, "B": 0.5})
        self.assertEqual(result["absolute_exposure"], 0)

    def test_switching_baseline_and_rankings(self):
        self.assertEqual(cheapest_configuration(self.configs), ("a", 10))
        self.assertEqual(cheapest_configuration(self.configs, {"A": 3, "B": 3}), ("a", 30))
        self.assertEqual(cheapest_configuration(self.configs, {"A": 3}), ("b", 20))

    def test_invalid_allocations_and_no_alternative(self):
        with self.assertRaises(ValueError):
            portfolio_costs(self.configs, {"a": 0.9})
        with self.assertRaises(ValueError):
            portfolio_costs(self.configs, {"a": 1}, {"typo": 2})
        with self.assertRaises(ValueError):
            cheapest_configuration({"a": {**self.configs["a"], "feasible": False}})


class RestorationTests(unittest.TestCase):
    def path(self, **overrides):
        inputs = dict(volume=1000, agent_share=0.75, retained_capacity=0.25,
                      initial_availability=0.25, execution_cost=20, human_cost=80,
                      horizon=20, review_hours_available=0)
        inputs.update(overrides)
        return simulate_path(**inputs)

    def test_immediate_restoration_and_root(self):
        continuation = self.path()
        restoration = self.path(restore=True, ramp_quarters=0, total_restoration_cost=3000)
        crossing = compare_paths(continuation, restoration)
        expected = 4 + 3000 / (20 * 1000 * 0.75 * 20)
        self.assertAlmostEqual(crossing["root"], expected)
        left, right = continuation["summary"], restoration["summary"]
        price = crossing["root"]
        self.assertAlmostEqual(left["fixed_cost"] + price * left["provider_spend_baseline"],
                               right["fixed_cost"] + price * right["provider_spend_baseline"])
        self.assertTrue(restoration["summary"]["target_attained"])
        self.assertEqual(restoration["quarters"][0]["restoration_spend"], 3000)

    def test_quarter_average_ramp(self):
        path = self.path(restore=True, delay_quarters=1, ramp_quarters=2, total_restoration_cost=100)
        self.assertEqual([row["human_availability_average"] for row in path["quarters"][:4]],
                         [0.25, 0.4375, 0.8125, 1])
        self.assertEqual([row["restoration_spend"] for row in path["quarters"][:4]], [0, 50, 50, 0])
        for row in path["quarters"]:
            self.assertLessEqual(row["human_share"], row["human_availability_average"])
            self.assertAlmostEqual(row["human_output"] + row["agent_output"], row["required_output"])

    def test_beyond_horizon_and_non_unique(self):
        continuation = self.path(horizon=4)
        delayed = self.path(horizon=4, restore=True, delay_quarters=5, ramp_quarters=2,
                            total_restoration_cost=100)
        self.assertEqual(compare_paths(continuation, delayed)["status"], "non_unique")
        self.assertFalse(delayed["summary"]["target_attained"])
        self.assertEqual(delayed["summary"]["restoration_paid"], 0)

    def test_partial_restoration_has_disclosed_root(self):
        path = self.path(horizon=2, restore=True, ramp_quarters=4, total_restoration_cost=100)
        root = compare_paths(self.path(horizon=2), path)
        self.assertEqual(root["status"], "positive_root")
        self.assertFalse(root["restoration_target_attained"])
        self.assertEqual(path["summary"]["restoration_paid"], 50)

    def test_discounting_applies_to_all_costs(self):
        path = self.path(horizon=1, annual_discount_rate=0.1)
        self.assertAlmostEqual(path["summary"]["total_cost"], 35000 / 1.1 ** 0.25)
        with self.assertRaises(ValueError):
            compare_paths(self.path(), self.path(restore=True, annual_discount_rate=0.1))

    def test_initial_output_agent_and_review_infeasibility(self):
        for overrides in ({"initial_availability": 0.1}, {"agent_output_capacity": 0.5},
                          {"review_hours_per_output": 1, "review_hours_available": 100}):
            with self.subTest(overrides=overrides):
                path = self.path(**overrides)
                self.assertFalse(path["summary"]["output_feasible"])
                self.assertIsNone(path["summary"]["total_cost"])
                self.assertEqual(compare_paths(self.path(), path)["status"], "infeasible_path")

    def test_capability_and_output_are_separate(self):
        high = self.path(retained_capacity=0.9)
        low = self.path(retained_capacity=0.1)
        self.assertEqual(high["summary"]["total_cost"], low["summary"]["total_cost"])
        self.assertNotEqual(high["summary"]["capability_end"], low["summary"]["capability_end"])

    def test_path_exposure_zero_and_discounted_identity(self):
        path = self.path(restore=True, annual_discount_rate=0.05)
        self.assertEqual(path_price_exposure(path, 1)["relative_exposure"], 0)
        self.assertAlmostEqual(path_price_exposure(path, 2)["absolute_exposure"],
                               path["summary"]["provider_spend_baseline"])

    def test_zero_adoption_and_instant_delay_boundary(self):
        no_agents = self.path(agent_share=0, retained_capacity=1, initial_availability=1)
        restored = self.path(agent_share=0, retained_capacity=1, initial_availability=1, restore=True)
        self.assertEqual(compare_paths(no_agents, restored)["status"], "non_unique")
        delayed = self.path(horizon=2, restore=True, delay_quarters=2, ramp_quarters=0,
                            total_restoration_cost=100)
        self.assertFalse(delayed["summary"]["target_attained"])
        self.assertEqual(delayed["summary"]["restoration_paid"], 0)

    def test_same_price_and_horizon_required(self):
        with self.assertRaises(ValueError):
            compare_paths(self.path(), self.path(restore=True, horizon=12))
        with self.assertRaises(ValueError):
            compare_paths(self.path(), self.path(restore=True, price_multiplier=2))


class RunnerTests(unittest.TestCase):
    def test_small_end_to_end_run(self):
        settings = json.loads((ROOT / "scenarios.json").read_text(encoding="utf-8"))
        settings["agent_shares"] = [0.75]
        settings["retained_capacities"] = [0.25]
        settings["price_multipliers"] = [1, 2]
        settings["software_application"]["restoration_profiles"] = {
            "medium": settings["software_application"]["restoration_profiles"]["medium"]
        }
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            config, output = folder / "scenarios.json", folder / "output"
            config.write_text(json.dumps(settings), encoding="utf-8")
            with patch.object(sys, "argv", ["run_model.py", "--config", str(config), "--output", str(output)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    main()
            def read(name):
                with (output / name).open(newline="", encoding="utf-8") as stream:
                    return list(csv.DictReader(stream))
            self.assertEqual(len(read("static_exposure.csv")), 26)
            self.assertEqual(len(read("restoration_summaries.csv")), 2)
            self.assertEqual(len(read("restoration_quarters.csv")), 80)
            self.assertEqual(read("supplier_price_solution.csv")[0]["price"], "2.0")
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["dynamic_summary_rows"], 2)
            self.assertEqual((output / "inputs/scenarios.json").read_bytes(), config.read_bytes())
            self.assertTrue(all(row["provenance"] for row in read("hypothetical_firms.csv")))


if __name__ == "__main__":
    unittest.main()
