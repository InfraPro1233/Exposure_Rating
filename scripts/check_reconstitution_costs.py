"""One-at-a-time reconstruction-cost sensitivity; company inputs remain unchanged."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from exposure.company import evaluate_company


ROOT = Path(__file__).resolve().parents[1]
COSTS = (0, 100, 200, 400)
CASES = ("depleted_capacity_with_rival", "depleted_capacity_without_rival")


def cost_sensitivity(settings, costs=COSTS):
    cases = {case["name"]: case for case in settings["company_cases"]}
    if len(cases) != len(settings["company_cases"]):
        raise ValueError("Company case names must be unique")
    costs = list(costs)
    if not costs:
        raise ValueError("At least one reconstruction cost is required")
    rows = []
    for name in CASES:
        case = cases[name]
        inputs = case["company_inputs"]
        base = settings["institutional_assumptions"][case["institutional_profile"]]
        if base["cost_rule"] != "full_reconstitution_cost_times_one_minus_K":
            raise ValueError("This sweep varies Fmax; it requires the Fmax*(1-K) cost rule")
        for cost in costs:
            profile = {**base, "full_reconstitution_cost": cost}
            result = evaluate_company(inputs, profile, settings["basis"], settings["price_multipliers"])
            summary = result["summary"]
            path = result["quarterly_paths"].get("human_reconstitution")
            analytic_root = None
            shifted_output = 0
            discounted_rebuild = 0
            if path is not None:
                for row in path["quarters"]:
                    shifted_output += row["discount_weight"] * row["human_output"]
                    discounted_rebuild += row["discount_weight"] * row["restoration_spend"]
                execution = inputs["incumbent_ai_spend_per_quarter"]
                if path["summary"]["output_feasible"] and shifted_output > 0 and execution > 0:
                    # Constant unaffected costs cancel. This checks the root against
                    # H/V + discounted restoration bill / (discounted output shifted * V).
                    analytic_root = (
                        inputs["replacement_human_cost_per_quarter"] / execution
                        + discounted_rebuild / (shifted_output * execution)
                    )
            root = summary["human_reconstitution_root"]
            error = None if root is None or analytic_root is None else abs(root - analytic_root)
            if error is not None and not math.isclose(root, analytic_root, rel_tol=1e-9, abs_tol=1e-10):
                raise AssertionError(f"Accounting root disagrees with analytical formula: {name}, Fmax={cost}")
            rows.append({
                "case": name, "full_reconstitution_cost": cost,
                "actual_reconstitution_cost": summary["reconstitution_cost_planned"],
                "cost_unit": settings["basis"]["cost_unit"],
                "retained_capability": inputs["retained_capability"],
                "immediately_replaceable_ai_output_share": inputs["immediately_replaceable_ai_output_share"],
                "delay_quarters": profile["delay_quarters"], "ramp_quarters": profile["ramp_quarters"],
                "incumbent_spending_share": summary["incumbent_spending_share"],
                "human_reconstitution_root": root,
                "human_reconstitution_status": summary["human_reconstitution_status"],
                "human_reconstitution_range_status": summary["human_reconstitution_range_status"],
                "analytic_reconstitution_root": analytic_root, "root_check_error": error,
                "discounted_output_shifted": shifted_output,
                "discounted_reconstitution_paid": discounted_rebuild,
                "outside_option_threshold": summary["outside_option_threshold"],
                "outside_option_status": summary["outside_option_status"],
                "restoration_target_attained": summary["restoration_target_attained"],
                "provenance": "Hypothetical one-at-a-time cost sensitivity; no other inputs changed.",
            })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "company_scenarios.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "data/processed/company_model/reconstitution_cost_sensitivity.csv")
    args = parser.parse_args()
    raw = args.config.read_bytes()
    settings = json.loads(raw.decode("utf-8"))
    rows = cost_sensitivity(settings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    snapshot = {
        "source_config_sha256": hashlib.sha256(raw).hexdigest(),
        "settings": settings, "tested_full_reconstitution_costs": COSTS,
        "code_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), *sorted((ROOT / "src/exposure").glob("*.py")))
        },
    }
    args.output.with_suffix(".inputs.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} sensitivity rows: {args.output}")
    for name in CASES:
        case_rows = [row for row in rows if row["case"] == name]
        print(f"{name}: " + ", ".join(
            f"Fmax={row['full_reconstitution_cost']} -> threshold={row['outside_option_threshold']:.4g}"
            for row in case_rows
        ))
    print("Human roots checked against the analytical formula where defined; results are hypothetical.")


if __name__ == "__main__":
    main()
