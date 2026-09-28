"""One-at-a-time restoration delay, ramp and feasibility comparisons."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from exposure.company import evaluate_company


ROOT = Path(__file__).resolve().parents[1]
CASES = ("depleted_capacity_with_rival", "depleted_capacity_without_rival")
TIMING_CASES = (
    ("baseline", {}),
    ("delay_0", {"delay_quarters": 0}),
    ("delay_12", {"delay_quarters": 12}),
    ("delay_20", {"delay_quarters": 20}),
    ("ramp_0", {"ramp_quarters": 0}),
    ("ramp_24", {"ramp_quarters": 24}),
    ("path_unavailable", {"human_substitution_path_feasible": False}),
)


def timing_sensitivity(settings):
    cases = {case["name"]: case for case in settings["company_cases"]}
    if len(cases) != len(settings["company_cases"]):
        raise ValueError("Company case names must be unique")
    rows = []
    for name in CASES:
        case = cases[name]
        inputs = case["company_inputs"]
        original = settings["institutional_assumptions"][case["institutional_profile"]]
        for label, changes in TIMING_CASES:
            profile = {**original, **changes}
            result = evaluate_company(inputs, profile, settings["basis"], settings["price_multipliers"])
            summary = result["summary"]
            rows.append({
                "case": name, "sensitivity": label,
                "changed_parameter": next(iter(changes), "none"),
                "horizon_quarters": settings["basis"]["horizon_quarters"],
                "cost_unit": settings["basis"]["cost_unit"],
                "retained_capability": inputs["retained_capability"],
                "delay_quarters": profile["delay_quarters"],
                "ramp_quarters": profile["ramp_quarters"],
                "declared_institutional_path_feasible": profile["human_substitution_path_feasible"],
                "actual_reconstitution_cost_planned": summary["reconstitution_cost_planned"],
                "reconstitution_cost_paid": summary["restoration_paid"],
                "target_time_quarters": summary["target_time_quarters"],
                "target_attained": summary["restoration_target_attained"],
                "capability_end": summary["capability_end"],
                "restoration_path_output_feasible": summary["restoration_path_feasible"],
                "human_reconstitution_root": summary["human_reconstitution_root"],
                "human_reconstitution_status": summary["human_reconstitution_status"],
                "human_reconstitution_range_status": summary["human_reconstitution_range_status"],
                "outside_option_threshold": summary["outside_option_threshold"],
                "outside_option_status": summary["outside_option_status"],
                "restoration_residual_incumbent_spend": summary["restoration_residual_incumbent_spend"],
                "incumbent_spending_share": summary["incumbent_spending_share"],
                "provenance": "Hypothetical timing/feasibility sensitivity; company and rival inputs unchanged.",
            })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "company_scenarios.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "data/processed/company_model/reconstitution_timing_sensitivity.csv")
    args = parser.parse_args()
    raw = args.config.read_bytes()
    settings = json.loads(raw.decode("utf-8"))
    rows = timing_sensitivity(settings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    snapshot = {
        "source_config_sha256": hashlib.sha256(raw).hexdigest(),
        "settings": settings, "tested_timing_cases": TIMING_CASES,
        "code_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), *sorted((ROOT / "src/exposure").glob("*.py")))
        },
        "limitation": "Unfinished restoration roots compare supplied partial paths; future bills and terminal values are not charged.",
    }
    args.output.with_suffix(".inputs.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} timing/feasibility rows: {args.output}")
    for row in rows:
        print(f"{row['case']}, {row['sensitivity']}: threshold={row['outside_option_threshold']:.4g}, "
              f"target_attained={row['target_attained']}")
    print("Partial restoration and institutional infeasibility are reported separately; results are hypothetical.")


if __name__ == "__main__":
    main()
