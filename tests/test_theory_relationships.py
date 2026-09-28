"""Hand-checkable boundaries behind Docs/THEORY_REVIEW.md; not empirical tests."""

import json
import math
import unittest
from pathlib import Path

from exposure.company import evaluate_company
from exposure.cost import relative_exposure
from exposure.threshold import outside_option_threshold, path_cost

ROOT = Path(__file__).resolve().parents[1]


class TheoryRelationshipTests(unittest.TestCase):
    def test_exposure_identity(self):
        for fixed, spend in ((100, 80), (100, 0), (0, 80)):
            for price in (0.5, 0.75, 1, 1.25, 2, 12):
                baseline = fixed + spend
                self.assertAlmostEqual(
                    relative_exposure(baseline, path_cost(fixed, spend, price)),
                    (price - 1) * spend / baseline,
                )

    def test_threshold_cases(self):
        incumbent = (100, 80)
        for alternative, expected in (
            ((80, 90), 1), ((100, 80), 1), ((120, 60), 1),
            ((180, 20), 4 / 3), ((181, 80), math.inf), ((100, 90), math.inf),
        ):
            with self.subTest(alternative=alternative):
                result = outside_option_threshold(*incumbent, [alternative])
                self.assertEqual(result, expected)
                if math.isfinite(result):
                    self.assertLessEqual(path_cost(*alternative, result),
                                         path_cost(*incumbent, result) + 1e-10)
        self.assertEqual(outside_option_threshold(*incumbent, []), math.inf)

    def test_capacity_order_and_rival_bound(self):
        without_rival, with_rival = [], []
        for capacity in (0, 0.1, 0.25, 0.5, 0.75, 0.9, 1):
            human = (200 + 200 * (1 - capacity), 0)
            human_threshold = outside_option_threshold(100, 80, [human])
            bounded = outside_option_threshold(100, 80, [human, (180, 20)])
            without_rival.append(human_threshold)
            with_rival.append(bounded)
            self.assertAlmostEqual(human_threshold, max(1, 3.75 - 2.5 * capacity))
            self.assertAlmostEqual(bounded, min(human_threshold, 4 / 3))
        self.assertEqual(without_rival, sorted(without_rival, reverse=True))
        self.assertEqual(with_rival, sorted(with_rival, reverse=True))
        # Removing a feasible option can increase the threshold to infinity.
        self.assertEqual(outside_option_threshold(100, 80, []), math.inf)

    def test_fixed_cost_alone_does_not_order_thresholds(self):
        expensive_residual = outside_option_threshold(100, 80, [(200, 60)])
        larger_fixed_less_dependence = outside_option_threshold(100, 80, [(240, 0)])
        self.assertEqual(expensive_residual, 5)
        self.assertEqual(larger_fixed_less_dependence, 1.75)
        self.assertLess(larger_fixed_less_dependence, expensive_residual)

    def test_free_restoration_delay_limit(self):
        settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))
        case = next(case for case in settings["company_cases"] if case["name"].endswith("without_rival"))
        original = settings["institutional_assumptions"][case["institutional_profile"]]
        for delay, ramp in ((0, 0), (4, 12), (12, 12)):
            profile = {**original, "cost_rule": "supplied_total", "total_reconstitution_cost": 0,
                       "delay_quarters": delay, "ramp_quarters": ramp}
            result = evaluate_company(case["company_inputs"], profile, settings["basis"], [1, 2])
            self.assertAlmostEqual(result["summary"]["human_reconstitution_root"], 1.25)
            self.assertAlmostEqual(result["summary"]["conditional_reconstitution_gap"], 0)

    def test_baseline_competition_is_not_a_price_ceiling(self):
        incumbent, alternative = (100, 80), (80, 90)
        self.assertEqual(outside_option_threshold(*incumbent, [alternative]), 1)
        self.assertLess(path_cost(*alternative, 1), path_cost(*incumbent, 1))
        self.assertEqual(path_cost(*alternative, 2), path_cost(*incumbent, 2))
        self.assertGreater(path_cost(*alternative, 3), path_cost(*incumbent, 3))

    def test_completed_restoration_retains_transition_bills(self):
        settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))
        case = next(case for case in settings["company_cases"] if case["name"].endswith("without_rival"))
        result = evaluate_company(
            case["company_inputs"], settings["institutional_assumptions"][case["institutional_profile"]],
            settings["basis"], [1, 2],
        )
        self.assertTrue(result["summary"]["restoration_target_attained"])
        self.assertEqual(result["summary"]["restoration_residual_incumbent_spend"], 800)
        end = result["quarterly_paths"]["human_reconstitution"]["quarters"][-1]
        self.assertEqual(end["agent_output"], 0)
        self.assertEqual(end["human_output"], 1)

    def test_spending_comparative_statics(self):
        exposures, roots = [], []
        for spend in (20, 40, 80, 160):
            fixed, human, discounted_rebuild, shifted_output, horizon = 100, 100, 160, 10, 20
            baseline = horizon * (fixed + spend)
            exposures.append(relative_exposure(baseline, horizon * (fixed + 2 * spend)))
            incumbent = (fixed * horizon, spend * horizon)
            human_path = (fixed * horizon + human * shifted_output + discounted_rebuild,
                          spend * (horizon - shifted_output))
            expected = human / spend + discounted_rebuild / (spend * shifted_output)
            threshold = outside_option_threshold(*incumbent, [human_path])
            self.assertAlmostEqual(threshold, max(1, expected))
            roots.append(threshold)
        self.assertEqual(exposures, sorted(exposures))
        self.assertEqual(roots, sorted(roots, reverse=True))

    def test_shared_shock_weighted_exposure(self):
        # Same currency, horizon and non-overlapping coverage are stipulated.
        sectors = [(1000, 200), (500, 300)]
        for price in (0.5, 1, 2):
            baseline = sum(fixed + spend for fixed, spend in sectors)
            shocked = sum(path_cost(fixed, spend, price) for fixed, spend in sectors)
            weighted = sum(
                (fixed + spend) / baseline
                * relative_exposure(fixed + spend, path_cost(fixed, spend, price))
                for fixed, spend in sectors
            )
            self.assertAlmostEqual(relative_exposure(baseline, shocked), weighted)
            self.assertAlmostEqual(shocked - baseline, (price - 1) * sum(spend for _, spend in sectors))

    def test_shared_capacity_bounds(self):
        incumbent = path_cost(100, 80, 2)
        human = 200
        independent_lower_bound = 2 * min(incumbent, human)
        feasible_joint_cost = min(2 * incumbent, incumbent + human)  # At most one human path.
        self.assertEqual(independent_lower_bound, 400)
        self.assertEqual(feasible_joint_cost, 460)
        self.assertGreater(feasible_joint_cost, independent_lower_bound)


if __name__ == "__main__":
    unittest.main()
