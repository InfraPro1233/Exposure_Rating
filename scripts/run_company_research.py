"""Reproduce the primary hypothetical company analysis, without benchmark data."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = (
    "company_inputs.csv", "institutional_assumptions.csv", "company_summary.csv",
    "company_exposure.csv", "company_paths.csv", "company_quarters.csv",
    "reconstitution_cost_sensitivity.csv", "reconstitution_timing_sensitivity.csv",
    "capacity_sensitivity.csv", "capacity_surface.csv", "horizon_discount_sensitivity.csv",
    "spending_sensitivity.csv", "rival_constraints.csv", "shock_scope_sensitivity.csv",
    "provider_allocation_sensitivity.csv",
    "shared_capacity_bound.csv", "shared_capacity_quarters.csv",
)
FIGURES = ("rebuilding_thresholds.png", "capacity_thresholds.png", "shock_scope.png")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "company_scenarios.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/company_model")
    parser.add_argument("--plots", action="store_true", help="Add headless Matplotlib figures")
    parser.add_argument("--skip-tests", action="store_true", help="Skip tests already run separately")
    args = parser.parse_args()
    raw = args.config.read_bytes()
    settings = json.loads(raw.decode("utf-8"))
    output = args.output.resolve()
    (output / "inputs").mkdir(parents=True, exist_ok=True)
    frozen = output / "inputs/research_config.json"
    frozen.write_bytes(raw)
    code = sorted((ROOT / "src/exposure").glob("*.py"))
    code += sorted((ROOT / "scripts").glob("*.py"))
    code += sorted((ROOT / "tests").glob("test_*.py"))
    code.append(ROOT / "pyproject.toml")
    method_sources = [
        ROOT / "MODEL_CONTRACT.md",
        *(ROOT / "Docs" / name for name in (
            "COMPANY_INPUT_CONTRACT.md", "THEORY_REVIEW.md", "SHARED_CAPACITY_BOUND.md",
            "LITERATURE_COMPARISON.md", "RESEARCH_PACKAGE.md",
        )),
    ]
    method_snapshots = []
    for source in method_sources:
        destination = output / "inputs/methods" / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        method_snapshots.append(destination)
    manifest = {
        "status": "running", "started_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "basis": settings["basis"], "provenance": settings["provenance"],
        "tests": "skipped" if args.skip_tests else "pending",
        "plots_requested": args.plots, "steps_completed": [],
        "code_sha256": {str(path.relative_to(ROOT)): digest(path) for path in code},
        "method_documents_sha256": {
            str(source.relative_to(ROOT)): digest(snapshot)
            for source, snapshot in zip(method_sources, method_snapshots)
        },
        "limitations": [
            "Hypothetical scenarios, not calibrated firm, industry, or monopoly estimates.",
            "Equal output/quality, fixed demand, supplied alternatives and restoration paths.",
            "First weakly competitive outside option is not an optimal provider price or complete escape.",
            "K and immediately usable output are distinct; fixed-mix exposure has no direct K effect.",
            "Future completion bills and terminal values are excluded; review capacity may be unverified.",
            "Institutional assumptions require independent evidence; firm hiring may only reallocate capacity.",
        ],
    }
    manifest_path = output / "pipeline_manifest.json"

    def record():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    def run(arguments):
        subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)
        manifest["steps_completed"].append(arguments)
        record()

    record()
    try:
        if not args.skip_tests:
            run(["-m", "unittest", "discover", "-s", "tests", "-q"])
            manifest["tests"] = "passed"
        config = ["--config", str(frozen)]
        run(["scripts/run_company_model.py", *config, "--output", str(output)])
        for script, table in (
            ("check_reconstitution_costs.py", "reconstitution_cost_sensitivity.csv"),
            ("check_reconstitution_timing.py", "reconstitution_timing_sensitivity.csv"),
        ):
            run([f"scripts/{script}", *config, "--output", str(output / table)])
        run(["scripts/check_company_sensitivities.py", *config, "--output", str(output)])
        run(["scripts/check_shared_capacity.py", *config, "--output", str(output)])
        files = [output / name for name in TABLES]
        files += method_snapshots
        files += [
            frozen, output / "manifest.json",
            output / "reconstitution_cost_sensitivity.inputs.json",
            output / "reconstitution_timing_sensitivity.inputs.json",
            output / "company_sensitivities.inputs.json",
            output / "shared_capacity_bound.inputs.json",
        ]
        if args.plots:
            run(["scripts/plot_company_results.py", "--input", str(output)])
            manifest["matplotlib_version"] = importlib.metadata.version("matplotlib")
            files += [output / "figures" / name for name in FIGURES]
        manifest["table_rows"] = {}
        for name in TABLES:
            with (output / name).open(newline="", encoding="utf-8") as stream:
                manifest["table_rows"][name] = sum(1 for _ in csv.DictReader(stream))
        notes = output / "RESULTS.md"
        notes.write_text(
            "# Hypothetical company-model results\n\n"
            "Start with company_summary.csv, then company_exposure.csv. "
            "Thresholds are AI price multipliers, not total-company cost increases.\n\n"
            "Capacity sensitivities separate retained capability from immediately usable output. "
            "capacity_surface.csv reports outside-option thresholds, not immediate price exposure.\n\n"
            "Cost and timing tables distinguish paid/planned rebuilding, unfinished paths, "
            "physical feasibility and accounting roots. Horizon comparisons omit terminal values.\n\n"
            "Rival constraints test eligibility, switching bills and residual incumbent spending. "
            "Common-shock comparisons need an explicit decomposition of other-provider AI spending. "
            "Financial spending HHI is not legal market concentration.\n\n"
            "Shared-capacity tables concern a separate hypothetical workload system, NOT summed company cases. "
            "The analytical floor bounds common-price cost changes across all feasible paths. "
            "For cuts it is an upper bound on the negative cost change; for increases a lower bound. "
            "A zero floor is inconclusive, and a positive horizon floor can reflect earlier transition bills.\n\n"
            "Every scenario is hypothetical. Missing review budgets remain unverified. "
            "Partial switching may leave supplier dependence; a threshold is not monopoly power. "
            "Evidence collection, formal contribution review and paper writing remain separate work.\n\n"
            "pipeline_manifest.json lists this run's outputs, hashes, steps and test status. "
            "Only listed artifacts belong to this run; older optional plots/files are not refreshed.\n",
            encoding="utf-8",
        )
        files.append(notes)
        manifest["output_sha256"] = {str(path.relative_to(output)): digest(path) for path in files}
        manifest["status"] = "complete"
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        record()
    except Exception as error:
        manifest["status"] = "failed"
        manifest["error"] = str(error)
        record()
        raise
    print(f"Primary results package: {output}")
    print("Implementation verified; empirical calibration and academic contribution remain for review.")


if __name__ == "__main__":
    main()
