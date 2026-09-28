"""Export the remaining declared company-model sensitivities without benchmark data."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from exposure.experiments import company_experiments

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "company_scenarios.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/company_model")
    args = parser.parse_args()
    raw = args.config.read_bytes()
    settings = json.loads(raw.decode("utf-8"))
    tables = company_experiments(settings)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        if not rows:
            raise ValueError(f"No scenario rows for {name}; check the declared cases/grids")
        columns = list(dict.fromkeys(key for row in rows for key in row))
        with (args.output / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        print(f"{name}: {len(rows)} rows")
    snapshot = {
        "source_config_sha256": hashlib.sha256(raw).hexdigest(), "settings": settings,
        "code_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), *sorted((ROOT / "src/exposure").glob("*.py")))
        },
        "limitations": [
            "All declared scenario ranges are hypothetical, not probability distributions or confidence intervals.",
            "Partial human replacement need not eliminate incumbent dependence.",
            "Common-price slopes include all explicitly repriced AI spending, not just incumbent bills.",
            "Financial spending HHI is not a legal market-concentration measure.",
            "Horizon/rate comparisons have equal output within each comparison; future bills/terminal values are excluded.",
        ],
    }
    (args.output / "company_sensitivities.inputs.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Results: {args.output}")


if __name__ == "__main__":
    main()
