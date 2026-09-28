import contextlib
import copy
import csv
import io
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from exposure.company import evaluate_company
from scripts.run_company_model import ROOT, main


class CompanyModelTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))

    def evaluate(self, index, **institutional_overrides):
        case = self.settings["company_cases"][index]
        profile = {
            **self.settings["institutional_assumptions"][case["institutional_profile"]],
            **institutional_overrides,
        }
        return evaluate_company(case["company_inputs"], profile,
                                self.settings["basis"], self.settings["price_multipliers"])

    def test_three_cases_and_competition_counterexample(self):
        retained, rival, no_rival = [self.evaluate(index) for index in range(3)]
        self.assertAlmostEqual(retained["summary"]["outside_option_threshold"], 1.25)
        self.assertAlmostEqual(rival["summary"]["outside_option_threshold"], 1.075)
        self.assertAlmostEqual(no_rival["summary"]["outside_option_threshold"], 1.45)
        self.assertLess(rival["summary"]["outside_option_threshold"],
                        retained["summary"]["outside_option_threshold"])
        self.assertGreater(no_rival["summary"]["outside_option_threshold"],
                           retained["summary"]["outside_option_threshold"])
        for result in (retained, rival, no_rival):
            row = next(row for row in result["exposure"] if row["price_multiplier"] == 2)
            self.assertAlmostEqual(row["fixed_mix_relative_exposure"], 80 / 180)
            self.assertEqual(result["summary"]["baseline_cost"], 3600)
        left, right = self.settings["company_cases"][1:3]
        left, right = copy.deepcopy(left["company_inputs"]), copy.deepcopy(right["company_inputs"])
        left.pop("feasible_rivals")
        right.pop("feasible_rivals")
        self.assertEqual(left, right)

    def test_reconstitution_root_matches_affine_costs(self):
        result = self.evaluate(2)
        price = result["summary"]["human_reconstitution_root"]
        fixed, spend = result["coefficients"]["incumbent"]
        alt_fixed, alt_spend = result["coefficients"]["human_reconstitution"]
        self.assertAlmostEqual(fixed + price * spend, alt_fixed + price * alt_spend)
        self.assertAlmostEqual(result["summary"]["conditional_reconstitution_gap"], 0.2)
        self.assertEqual(result["summary"]["restoration_residual_incumbent_spend"], 800)
        self.assertTrue(result["summary"]["restoration_target_attained"])

    def test_unavailable_institution_does_not_delete_retained_humans(self):
        retained = self.evaluate(0, human_substitution_path_feasible=False)
        depleted = self.evaluate(2, human_substitution_path_feasible=False)
        self.assertAlmostEqual(retained["summary"]["outside_option_threshold"], 1.25)
        self.assertIn("retained_humans", retained["coefficients"])
        self.assertEqual(depleted["summary"]["outside_option_threshold"], math.inf)
        self.assertEqual(depleted["summary"]["human_reconstitution_status"], "institutional_path_infeasible")

    def test_rebuild_beyond_horizon_is_not_a_new_outside_option(self):
        result = self.evaluate(2, delay_quarters=30)
        self.assertEqual(result["summary"]["human_reconstitution_status"], "non_unique")
        self.assertEqual(result["summary"]["outside_option_threshold"], math.inf)
        self.assertFalse(result["summary"]["restoration_target_attained"])
        self.assertNotIn("human_reconstitution", result["coefficients"])
        self.assertIn("human_reconstitution", result["quarterly_paths"])

    def test_supplied_bill_and_zero_cost_delay_limit(self):
        direct = self.evaluate(2, cost_rule="supplied_total", total_reconstitution_cost=160)
        self.assertAlmostEqual(direct["summary"]["human_reconstitution_root"], 1.45)
        free = self.evaluate(2, cost_rule="supplied_total", total_reconstitution_cost=0)
        self.assertAlmostEqual(free["summary"]["human_reconstitution_root"], 1.25)
        self.assertAlmostEqual(free["summary"]["conditional_reconstitution_gap"], 0)

    def test_delay_can_amplify_nonzero_bill_without_changing_immediate_exposure(self):
        immediate = self.evaluate(2, delay_quarters=0, ramp_quarters=0)
        delayed = self.evaluate(2)
        self.assertAlmostEqual(immediate["summary"]["human_reconstitution_root"], 1.35)
        self.assertGreater(delayed["summary"]["human_reconstitution_root"],
                           immediate["summary"]["human_reconstitution_root"])
        self.assertEqual(immediate["exposure"][0]["fixed_mix_relative_exposure"],
                         delayed["exposure"][0]["fixed_mix_relative_exposure"])

    def test_rival_cost_is_total_and_switching_paid_once(self):
        result = self.evaluate(1)
        self.assertEqual(result["coefficients"]["qualified_rival"], (3720, 0))
        self.assertEqual(result["summary"]["reconstitution_cost_planned"], 160)
        self.assertAlmostEqual(result["summary"]["restoration_paid"], 160)

    def test_zero_spend_and_invalid_inputs(self):
        self.settings["company_cases"][2]["company_inputs"]["incumbent_ai_spend_per_quarter"] = 0
        result = self.evaluate(2)
        self.assertTrue(all(row["fixed_mix_absolute_exposure"] == 0 for row in result["exposure"]))
        self.settings["company_cases"][2]["company_inputs"]["retained_capability"] = 1.1
        with self.assertRaises(ValueError):
            self.evaluate(2)

    def test_runner_exports_separate_groups_without_swe_loading(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            with patch.object(sys, "argv", ["run_company_model.py", "--output", str(output)]):
                with patch("scripts.run_model.load_technology", side_effect=AssertionError("SWE not required")):
                    with contextlib.redirect_stdout(io.StringIO()):
                        main()
            with (output / "company_summary.csv").open(newline="", encoding="utf-8") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 3)
            with (output / "company_exposure.csv").open(newline="", encoding="utf-8") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 27)
            self.assertTrue((output / "company_inputs.csv").is_file())
            self.assertTrue((output / "institutional_assumptions.csv").is_file())
            self.assertEqual((output / "inputs/company_scenarios.json").read_bytes(),
                             (ROOT / "company_scenarios.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
