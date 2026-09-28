import csv
from pathlib import Path
from exposure.cost import effective_cost

source = Path("data/raw/swebench_runs.csv")
target = Path("data/processed/agent_costs.csv")
target.parent.mkdir(parents=True, exist_ok=True)

columns = [
    "submission_folder", "model", "avg_cost_usd",
    "resolution_rate", "effective_cost_usd",
]

with source.open(newline="", encoding="utf-8") as infile, target.open(
    "w", newline="", encoding="utf-8"
) as outfile:
    writer = csv.DictWriter(outfile, fieldnames=columns)
    writer.writeheader()

    for row in csv.DictReader(infile):
        writer.writerow({
            "submission_folder": row["submission_folder"],
            "model": row["model"],
            "avg_cost_usd": row["avg_cost_usd"],
            "resolution_rate": row["resolution_rate"],
            "effective_cost_usd": effective_cost(
                float(row["avg_cost_usd"]),
                float(row["resolution_rate"]),
            ),
        })

print(f"Wrote {target}")
