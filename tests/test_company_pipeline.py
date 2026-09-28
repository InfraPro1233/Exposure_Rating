import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CompanyPipelineTests(unittest.TestCase):
    def test_reproducible_exports_and_optional_figures(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results"
            command = [sys.executable, str(ROOT / "scripts/run_company_research.py"),
                       "--skip-tests", "--output", str(output)]
            plots = importlib.util.find_spec("matplotlib") is not None
            if plots:
                command.append("--plots")
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((output / "pipeline_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "complete")
            self.assertEqual(manifest["tests"], "skipped")
            counts = manifest["table_rows"]
            for table, count in (
                ("company_summary.csv", 3), ("company_exposure.csv", 27),
                ("reconstitution_cost_sensitivity.csv", 8),
                ("reconstitution_timing_sensitivity.csv", 14),
                ("capacity_sensitivity.csv", 20), ("capacity_surface.csv", 50),
                ("horizon_discount_sensitivity.csv", 12), ("spending_sensitivity.csv", 8),
                ("rival_constraints.csv", 9), ("shock_scope_sensitivity.csv", 36),
                ("provider_allocation_sensitivity.csv", 144),
                ("shared_capacity_bound.csv", 27), ("shared_capacity_quarters.csv", 60),
            ):
                self.assertEqual(counts[table], count, table)
            self.assertEqual((output / "inputs/research_config.json").read_bytes(),
                             (ROOT / "company_scenarios.json").read_bytes())
            for name, expected in manifest["method_documents_sha256"].items():
                snapshot = output / "inputs/methods" / name
                self.assertEqual(snapshot.read_bytes(), (ROOT / name).read_bytes())
                self.assertEqual(hashlib.sha256(snapshot.read_bytes()).hexdigest(), expected)
            for name, expected in manifest["output_sha256"].items():
                path = output / name
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, name)
                if name.endswith(".png"):
                    self.assertTrue(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            with (output / "company_summary.csv").open(newline="", encoding="utf-8") as stream:
                thresholds = {row["case"]: float(row["outside_option_threshold"]) for row in csv.DictReader(stream)}
            self.assertAlmostEqual(thresholds["retained_human_capacity"], 1.25)
            self.assertAlmostEqual(thresholds["depleted_capacity_with_rival"], 1.075)
            self.assertAlmostEqual(thresholds["depleted_capacity_without_rival"], 1.45)

    def test_failed_run_does_not_leave_a_success_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            settings = json.loads((ROOT / "company_scenarios.json").read_text(encoding="utf-8"))
            settings["basis"]["horizon_quarters"] = 0
            config = folder / "invalid.json"
            config.write_text(json.dumps(settings), encoding="utf-8")
            output = folder / "results"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/run_company_research.py"),
                 "--config", str(config), "--output", str(output), "--skip-tests"],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            manifest = json.loads((output / "pipeline_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "failed")
            self.assertIn("error", manifest)
            self.assertNotIn("output_sha256", manifest)


if __name__ == "__main__":
    unittest.main()
