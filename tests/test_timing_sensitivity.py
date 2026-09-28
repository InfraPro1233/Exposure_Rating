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

from scripts.check_reconstitution_timing import ROOT, TIMING_CASES, main, timing_sensitivity


class TimingSensitivityTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))

    def test_roots_and_fixed_inputs(self):
        original = copy.deepcopy(self.settings)
        rows = timing_sensitivity(self.settings)
        self.assertEqual(len(rows), 14)
        self.assertEqual(self.settings, original)
        expected = {
            "baseline": 1.45, "delay_0": 1.25 + 160 / (14 * 80),
            "delay_12": 1.75, "ramp_0": 1.375, "ramp_24": 1.5,
            "delay_20": math.inf, "path_unavailable": math.inf,
        }
        for row in rows:
            self.assertEqual(row["actual_reconstitution_cost_planned"], 160)
            self.assertAlmostEqual(row["incumbent_spending_share"], 80 / 180)
            threshold = 1.075 if row["case"].endswith("with_rival") else expected[row["sensitivity"]]
            self.assertAlmostEqual(row["outside_option_threshold"], threshold)

    def test_partial_beyond_horizon_and_infeasible_are_distinct(self):
        rows = {row["sensitivity"]: row for row in timing_sensitivity(self.settings)
                if row["case"] == "depleted_capacity_without_rival"}
        self.assertFalse(rows["delay_12"]["target_attained"])
        self.assertEqual(rows["delay_12"]["human_reconstitution_status"], "positive_root")
        self.assertAlmostEqual(rows["delay_12"]["reconstitution_cost_paid"], 160 * 8 / 12)
        self.assertFalse(rows["delay_20"]["target_attained"])
        self.assertEqual(rows["delay_20"]["human_reconstitution_status"], "non_unique")
        self.assertEqual(rows["delay_20"]["reconstitution_cost_paid"], 0)
        self.assertEqual(rows["path_unavailable"]["human_reconstitution_status"], "institutional_path_infeasible")
        self.assertIsNone(rows["path_unavailable"]["reconstitution_cost_paid"])

    def test_export_and_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "timing.csv"
            with patch.object(sys, "argv", ["check_reconstitution_timing.py", "--output", str(target)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    main()
            with target.open(newline="", encoding="utf-8") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 14)
            snapshot = json.loads(target.with_suffix(".inputs.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["settings"], self.settings)
            self.assertEqual(len(snapshot["tested_timing_cases"]), len(TIMING_CASES))


if __name__ == "__main__":
    unittest.main()
