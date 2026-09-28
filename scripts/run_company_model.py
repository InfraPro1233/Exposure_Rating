"""Primary company-input model; requires NO SWE or current API-price dataset."""

import argparse
import csv
import hashlib
import json
import platform
import shutil
from pathlib import Path

from exposure.company import evaluate_company

ROOT = Path(__file__).resolve().parents[1]


def write_csv(folder, name, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(f"No rows for {name}")
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with (folder / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "company_scenarios.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/company_model")
    args = parser.parse_args()
    settings = json.loads(args.config.read_text(encoding="utf-8"))
    basis = settings["basis"]
    profiles = settings["institutional_assumptions"]
    summaries, exposure, inputs, coefficients, quarters = [], [], [], [], []
    names = set()
    for case in settings["company_cases"]:
        name, profile = case["name"], case["institutional_profile"]
        if name in names:
            raise ValueError(f"Duplicate company case: {name}")
        names.add(name)
        if profile not in profiles:
            raise ValueError(f"Unknown institutional profile: {profile}")
        result = evaluate_company(case["company_inputs"], profiles[profile], basis, settings["price_multipliers"])
        metadata = {"case": name, "institutional_profile": profile, "provenance": settings["provenance"]}
        summaries.append({**metadata, **result["summary"]})
        exposure.extend({**metadata, **row} for row in result["exposure"])
        inputs.append({
            "case": name,
            **{key: value for key, value in case["company_inputs"].items() if key != "feasible_rivals"},
            "feasible_rivals": json.dumps(case["company_inputs"].get("feasible_rivals", [])),
        })
        for path, (fixed, spend) in result["coefficients"].items():
            coefficients.append({
                **metadata, "path": path, "cost_unit": basis["cost_unit"],
                "fixed_cost_over_horizon": fixed, "incumbent_spend_over_horizon": spend,
                "cost_formula": "fixed_cost_over_horizon + theta * incumbent_spend_over_horizon",
            })
        for path, values in result["quarterly_paths"].items():
            quarters.extend({**metadata, "path": path, "cost_unit": basis["cost_unit"],
                             "table_price_multiplier": 1, **row} for row in values["quarters"])
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("company_inputs.csv", inputs),
        ("institutional_assumptions.csv", ({"profile": name, **profile} for name, profile in profiles.items())),
        ("company_summary.csv", summaries), ("company_exposure.csv", exposure),
        ("company_paths.csv", coefficients), ("company_quarters.csv", quarters),
    ):
        write_csv(args.output, filename, rows)
    snapshot = args.output / "inputs"
    snapshot.mkdir(exist_ok=True)
    destination = snapshot / args.config.name
    if args.config.resolve() != destination.resolve():
        shutil.copyfile(args.config, destination)
    code_files = [Path(__file__), *sorted((ROOT / "src/exposure").glob("*.py"))]
    manifest = {
        "python_version": platform.python_version(), "basis": basis,
        "provenance": settings["provenance"],
        "input_sha256": hashlib.sha256(args.config.read_bytes()).hexdigest(),
        "code_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in code_files},
        "cases": len(summaries), "price_scenario_rows": len(exposure),
        "limitations": [
            "Company inputs and institutional assumptions are separate, but all supplied example values are hypothetical.",
            "Same output and quality, unchanged unaffected costs, fixed workload and exogenous paths are assumed.",
            "Restoration cost is a company-facing burden, not the total cost of rebuilding national institutions.",
            "K does not directly determine immediate exposure or immediately replaceable output.",
            "Retained humans can provide a partial alternative even without institutional reconstruction.",
            "Outside-option competitiveness is not an optimal provider price or proof of monopoly.",
            "Missing dedicated review budgets remain unverified; no benchmark/API-price data are needed.",
            "A finite-horizon reconstruction path can still contain incumbent bills incurred during its delay and ramp.",
        ],
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Company results: {args.output}")
    for row in summaries:
        print(f"{row['case']}: outside-option threshold={row['outside_option_threshold']:.4g}")
    print("Hypothetical cost/feasibility comparisons, not estimated monopoly power.")


if __name__ == "__main__":
    main()
