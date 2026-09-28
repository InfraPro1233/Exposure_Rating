"""Plot exported hypothetical company comparisons, without running new scenarios."""

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_table(folder, name):
    with (folder / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def label(name):
    return name.replace("depleted_capacity_", "").replace("_", " ")


def plot_results(folder):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    figures = folder / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    def save(fig, name, caption):
        fig.text(0.5, 0.025, caption, ha="center", va="bottom", fontsize=9)
        fig.tight_layout(rect=(0, 0.12, 1, 0.94))
        fig.savefig(figures / name, dpi=160)
        plt.close(fig)

    cost = read_table(folder, "reconstitution_cost_sensitivity.csv")
    fig, axis = plt.subplots(figsize=(7, 4.5))
    for case in sorted({row["case"] for row in cost}):
        rows = sorted((row for row in cost if row["case"] == case),
                      key=lambda row: float(row["actual_reconstitution_cost"]))
        roots = [float(row["outside_option_threshold"]) for row in rows]
        axis.plot([float(row["actual_reconstitution_cost"]) for row in rows],
                  [value if math.isfinite(value) else math.nan for value in roots],
                  marker="o", label=label(case))
        if any(not math.isfinite(value) for value in roots):
            axis.text(0.02, 0.95, "Non-finite crossings omitted; see source CSV.", transform=axis.transAxes)
    axis.set(xlabel="Planned rebuilding bill (normalized cost units)",
             ylabel="Outside-option threshold (AI price multiplier)",
             title="Hypothetical rebuilding-cost comparison")
    axis.legend()
    save(fig, "rebuilding_thresholds.png",
         "Only rebuilding cost varies. Fixed horizon, availability, delay/ramp and rival terms.\n"
         "First weakly competitive alternative; not an optimal price or complete independence.")

    surface = read_table(folder, "capacity_surface.csv")
    cases = sorted({row["case"] for row in surface})
    finite = [float(row["outside_option_threshold"]) for row in surface
              if math.isfinite(float(row["outside_option_threshold"]))]
    if not finite:
        raise ValueError("No finite capacity threshold is available for a heatmap")
    fig, axes = plt.subplots(1, len(cases), figsize=(6 * len(cases), 5), squeeze=False)
    for axis, case in zip(axes[0], cases):
        rows = [row for row in surface if row["case"] == case]
        capability = sorted({float(row["retained_capability"]) for row in rows})
        available = sorted({float(row["immediately_replaceable_ai_output_share"]) for row in rows})
        cells = {(float(row["retained_capability"]), float(row["immediately_replaceable_ai_output_share"])):
                 float(row["outside_option_threshold"]) for row in rows}
        values = np.array([[cells[(k, a)] for a in available] for k in capability])
        cmap = plt.get_cmap("viridis").copy()
        cmap.set_bad("lightgray")
        chart = axis.imshow(np.ma.masked_invalid(values), origin="lower", aspect="auto",
                            cmap=cmap, vmin=min(finite), vmax=max(finite))
        axis.set_xticks(range(len(available)), [f"{value:g}" for value in available])
        axis.set_yticks(range(len(capability)), [f"{value:g}" for value in capability])
        axis.set(xlabel="Immediately replaceable affected AI output share",
                 ylabel="Retained capability K", title=label(case))
        for y in range(len(capability)):
            for x in range(len(available)):
                value = values[y, x]
                axis.text(x, y, f"{value:.3g}" if math.isfinite(value) else "no crossing",
                          ha="center", va="center", fontsize=8,
                          color="white" if math.isfinite(value) and value < (min(finite) + max(finite)) / 2 else "black")
        fig.colorbar(chart, ax=axis, label="Outside-option AI price multiplier", fraction=0.046)
    fig.suptitle("Hypothetical capability and immediately usable output", fontsize=12)
    save(fig, "capacity_thresholds.png",
         "Fixed spending/horizon/delay/ramp; rebuilding bill follows the supplied K rule.\n"
         "An available partial human path can bind before complete restoration. No causal K effect is identified.")

    shocks = read_table(folder, "shock_scope_sensitivity.csv")
    cases = sorted({row["case"] for row in shocks})
    fig, axes = plt.subplots(1, len(cases), figsize=(6 * len(cases), 4.5), squeeze=False)
    for axis, case in zip(axes[0], cases):
        for scope in sorted({row["shock_scope"] for row in shocks}):
            rows = sorted((row for row in shocks if row["case"] == case and row["shock_scope"] == scope),
                          key=lambda row: float(row["price_multiplier"]))
            axis.plot([float(row["price_multiplier"]) for row in rows],
                      [100 * float(row["adaptive_relative_exposure"]) for row in rows],
                      marker="o", label=scope.replace("_", " "))
        axis.axhline(0, color="gray", linewidth=0.6)
        axis.set(xlabel="AI price multiplier", ylabel="Adaptive cost change (%)", title=label(case))
        axis.legend(fontsize=8)
    fig.suptitle("Hypothetical provider-specific versus common shocks", fontsize=12)
    save(fig, "shock_scope.png",
         "Same supplied paths and their own unshocked adaptive baseline; other AI bills explicitly repriced.\n"
         "Common shocks can remove rival protection. Cheapest supplied path is not an optimized workforce policy.")
    print(f"Three source-table figures: {figures}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/processed/company_model")
    args = parser.parse_args()
    plot_results(args.input)


if __name__ == "__main__":
    main()
