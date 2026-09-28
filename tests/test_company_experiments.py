import copy
import json
import math
import unittest
from pathlib import Path

from exposure.company import evaluate_company
from exposure.experiments import (
    capacity_sensitivity, capacity_surface, common_price_coefficients,
    company_experiments, horizon_sensitivity, provider_allocation_sensitivity,
    rivalry_sensitivity, shock_scope_sensitivity, spending_sensitivity,
)

ROOT = Path(__file__).resolve().parents[1]


class CompanyExperimentTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))

    def test_capability_and_available_output_are_distinct(self):
        rows = capacity_sensitivity(self.settings)
        self.assertEqual(len(rows), 20)
        for row in rows:
            self.assertAlmostEqual(row["fixed_mix_relative_exposure"], 80 / 180)
            if row["case"].endswith("without_rival"):
                if row["changed_parameter"] == "retained_capability":
                    self.assertEqual(row["immediately_replaceable_ai_output_share"], 0)
                    self.assertAlmostEqual(row["outside_option_threshold"], 1.5 - 0.25 * row["parameter_value"])
                else:
                    self.assertEqual(row["retained_capability"], 0.2)
                    self.assertAlmostEqual(row["outside_option_threshold"],
                                           1.45 if row["parameter_value"] == 0 else 1.25)
            else:
                self.assertAlmostEqual(row["outside_option_threshold"], 1.075)

    def test_surface_and_no_input_mutation(self):
        original = copy.deepcopy(self.settings)
        tables = company_experiments(self.settings)
        self.assertEqual(self.settings, original)
        self.assertEqual(len(tables["capacity_surface.csv"]), 50)
        self.assertTrue(all(row["provenance"] for rows in tables.values() for row in rows))

    def test_horizon_and_discount_accounting(self):
        rows = horizon_sensitivity(self.settings)
        self.assertEqual(len(rows), 12)
        expected = {12: 1.75, 20: 1.45, 40: 1.25 + 160 / (30 * 80)}
        for row in rows:
            self.assertAlmostEqual(row["fixed_mix_relative_exposure"], 80 / 180)
            if row["case"].endswith("without_rival") and row["changed_parameter"] == "horizon_quarters":
                self.assertAlmostEqual(row["outside_option_threshold"], expected[row["parameter_value"]])
                self.assertEqual(row["restoration_target_attained"], row["parameter_value"] >= 16)

    def test_more_spending_can_mean_more_exposure_but_earlier_substitution(self):
        rows = [row for row in spending_sensitivity(self.settings) if row["case"].endswith("without_rival")]
        by_spend = {row["parameter_value"]: row for row in rows}
        self.assertEqual(by_spend[0]["fixed_mix_relative_exposure"], 0)
        self.assertEqual(by_spend[0]["outside_option_threshold"], math.inf)
        self.assertGreater(by_spend[160]["fixed_mix_relative_exposure"], by_spend[40]["fixed_mix_relative_exposure"])
        self.assertLess(by_spend[160]["outside_option_threshold"], by_spend[40]["outside_option_threshold"])
        self.assertAlmostEqual(by_spend[40]["outside_option_threshold"], 2.9)
        self.assertEqual(by_spend[160]["outside_option_threshold"], 1)

    def test_rival_fees_eligibility_and_residual_dependence(self):
        rows = rivalry_sensitivity(self.settings)
        self.assertEqual(len(rows), 9)
        residual = {row["parameter_value"]: row for row in rows if row["changed_parameter"] == "residual_share"}
        for fraction, expected in ((0, 1.075), (0.25, 1.1), (0.5, 1.15), (0.75, 1.3), (1, 1.45)):
            self.assertAlmostEqual(residual[fraction]["outside_option_threshold"], expected)
            self.assertEqual(residual[fraction]["rival_total_baseline_cost_per_quarter"], 185)
        self.assertAlmostEqual(next(row["outside_option_threshold"] for row in rows
                                    if row["changed_parameter"] == "eligibility"), 1.45)
        self.assertAlmostEqual(next(row["outside_option_threshold"] for row in rows
                                    if row["changed_parameter"] == "switching_cost" and row["parameter_value"] == 1000), 1.45)

    def test_common_shock_can_remove_rival_price_discipline(self):
        rows = [row for row in shock_scope_sensitivity(self.settings)
                if row["case"].endswith("with_rival") and row["price_multiplier"] == 2]
        scopes = {row["shock_scope"]: row for row in rows}
        self.assertAlmostEqual(scopes["incumbent_provider"]["outside_option_threshold"], 1.075)
        self.assertAlmostEqual(scopes["common_ai_prices"]["outside_option_threshold"], 1.45)
        self.assertGreater(scopes["common_ai_prices"]["adaptive_relative_exposure"],
                           scopes["incumbent_provider"]["adaptive_relative_exposure"])
        self.assertEqual(scopes["common_ai_prices"]["baseline_cost"], scopes["incumbent_provider"]["baseline_cost"])

    def test_common_coefficients_preserve_each_baseline_and_require_decomposition(self):
        case = self.settings["company_cases"][1]
        inputs = copy.deepcopy(case["company_inputs"])
        inputs["other_ai_spend_per_quarter"] = 20
        basis = self.settings["basis"]
        result = evaluate_company(inputs, self.settings["institutional_assumptions"][case["institutional_profile"]],
                                  basis, self.settings["price_multipliers"])
        common = common_price_coefficients(result, inputs, basis)
        for name, costs in result["coefficients"].items():
            self.assertAlmostEqual(sum(costs), sum(common[name]))
        self.assertEqual(common["incumbent"], (1600, 2000))
        inputs.pop("other_ai_spend_per_quarter")
        with self.assertRaises(ValueError):
            common_price_coefficients(result, inputs, basis)

    def test_diversification_identity_not_common_shock_protection(self):
        rows = [row for row in provider_allocation_sensitivity(self.settings)
                if row["case"].endswith("without_rival") and row["price_multiplier"] == 2]
        for row in rows:
            expected = 80 / 180
            if row["shock_scope"] == "selected_provider":
                expected *= row["selected_provider_spending_share"]
            self.assertAlmostEqual(row["relative_exposure"], expected)
            self.assertEqual(row["baseline_cost_per_quarter"], 180)
            self.assertGreaterEqual(row["spending_hhi"], 1 / 3 - 1e-12)


if __name__ == "__main__":
    unittest.main()
