import contextlib
import copy
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_reconstitution_costs import COSTS, ROOT, cost_sensitivity, main


class CostSensitivityTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))

    def test_expected_roots_and_competition_cap(self):
        before = copy.deepcopy(self.settings)
        rows = cost_sensitivity(self.settings)
        self.assertEqual(len(rows), 8)
        self.assertEqual(self.settings, before)
        expected = dict(zip(COSTS, (1.25, 1.35, 1.45, 1.65)))
        for row in rows:
            self.assertAlmostEqual(row["human_reconstitution_root"], expected[row["full_reconstitution_cost"]])
            self.assertAlmostEqual(row["root_check_error"], 0)
            self.assertAlmostEqual(row["actual_reconstitution_cost"], 0.8 * row["full_reconstitution_cost"])
            self.assertEqual((row["retained_capability"], row["delay_quarters"], row["ramp_quarters"]),
                             (0.2, 4, 12))
            self.assertAlmostEqual(row["incumbent_spending_share"], 80 / 180)
            threshold = 1.075 if row["case"].endswith("with_rival") else expected[row["full_reconstitution_cost"]]
            self.assertAlmostEqual(row["outside_option_threshold"], threshold)

    def test_incompatible_cost_rule_and_invalid_costs(self):
        self.settings["institutional_assumptions"]["institutional_shortage"]["cost_rule"] = "supplied_total"
        with self.assertRaises(ValueError):
            cost_sensitivity(self.settings)
        self.settings["institutional_assumptions"]["institutional_shortage"]["cost_rule"] = "full_reconstitution_cost_times_one_minus_K"
        with self.assertRaises(ValueError):
            cost_sensitivity(self.settings, [-1])
        with self.assertRaises(ValueError):
            cost_sensitivity(self.settings, [])

    def test_export_and_input_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "sensitivity.csv"
            with patch.object(sys, "argv", ["check_reconstitution_costs.py", "--output", str(target)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    main()
            with target.open(newline="", encoding="utf-8") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 8)
            snapshot = json.loads(target.with_suffix(".inputs.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["settings"], self.settings)
            self.assertEqual(snapshot["tested_full_reconstitution_costs"], list(COSTS))


if __name__ == "__main__":
    unittest.main()
