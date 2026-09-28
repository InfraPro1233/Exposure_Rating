"""Export a separate hypothetical shared-capacity bound; do not aggregate firms."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from exposure.systemic import price_change_bound, shared_capacity_path_bound

ROOT = Path(__file__).resolve().parents[1]


def shared_capacity_tables(settings):
    experiment = settings["shared_capacity_experiment"]
    basis = settings["basis"]
    sectors = experiment["sector_workloads"]
    prices = settings["price_multipliers"]
    summaries, quarters = [], []
    for profile, capacities in experiment["capacity_schedules"].items():
        if len(capacities) != basis["horizon_quarters"]:
            raise ValueError("Shared capacity schedule must match the comparison horizon")
        result = shared_capacity_path_bound(sectors, capacities, basis["annual_discount_rate"])
        metadata = {
            "capacity_profile": profile, "cost_unit": basis["cost_unit"],
            "scope": "Independent hypothetical workloads, NOT aggregated company cases.",
            "provenance": experiment["provenance"],
        }
        quarters.extend({**metadata, **row} for row in result["quarters"])
        for price in prices:
            summaries.append({
                **metadata, **result["summary"],
                "shock_scope": "all qualified AI routes share the same proportional price shock",
                **price_change_bound(result["summary"]["discounted_residual_ai_spending_floor"], 1, price),
            })
    return summaries, quarters


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "company_scenarios.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/company_model")
    args = parser.parse_args()
    raw = args.config.read_bytes()
    settings = json.loads(raw.decode("utf-8"))
    summaries, quarters = shared_capacity_tables(settings)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in (("shared_capacity_bound.csv", summaries), ("shared_capacity_quarters.csv", quarters)):
        if not rows:
            raise ValueError("At least one declared shared-capacity profile is required")
        with (args.output / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"{name}: {len(rows)} rows")
    snapshot = {
        "source_config_sha256": hashlib.sha256(raw).hexdigest(),
        "settings": settings,
        "code_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), *sorted((ROOT / "src/exposure").glob("*.py")))
        },
        "limitations": [
            "Sector workload and capacity numbers are independent hypothetical inputs, not industry observations.",
            "Spending floors must hold across every qualified AI route and scale with remaining output.",
            "Shared productive hours must be comparable and net of oversight/training commitments.",
            "Demand, quality, technology, feasible paths and capacity schedules do not change with theta.",
            "The bound is pooled cost exposure, not supplier profits, pricing power or permanent lock-in.",
            "Zero floor does not prove zero exposure; positive horizon floors may only reflect transition bills.",
            "No joint workforce optimization or institutional rebuilding cost estimate is supplied.",
        ],
    }
    (args.output / "shared_capacity_bound.inputs.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
