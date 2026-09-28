import csv
from pathlib import Path

from exposure.threshold import (
    human_path_cost,
    outside_option_threshold,
    restoration_cost,
)


target = Path(__file__).resolve().parents[1] / "data/processed/capacity_thresholds.csv"
target.parent.mkdir(parents=True, exist_ok=True)

columns = [
    "retained_capacity",
    "threshold_without_rival",
    "threshold_with_rival",
]

with target.open("w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=columns)
    writer.writeheader()

    for k in [1.0, 0.9, 0.75, 0.5, 0.25, 0.0]:
        human_cost = human_path_cost(200, restoration_cost(k, 200))
        without_rival = outside_option_threshold(100, 80, [(human_cost, 0)])
        with_rival = outside_option_threshold(
            100, 80, [(human_cost, 0), (180, 20)]
        )

        writer.writerow({
            "retained_capacity": k,
            "threshold_without_rival": without_rival,
            "threshold_with_rival": with_rival,
        })
        print(k, without_rival, with_rival)

print(f"Wrote {target}")

# Separate feasibility checks: these do not belong in the capacity CSV.
print(outside_option_threshold(100, 80, [(180, 20)]))
print(outside_option_threshold(100, 80, []))

