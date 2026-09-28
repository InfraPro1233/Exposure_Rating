"""Reproducible, explicitly hypothetical applications of the general model."""

import argparse
import csv
import hashlib
import json
import math
import platform
import shutil
from importlib.metadata import version
from pathlib import Path

from exposure.cost import agent_cost_components, production_cost, relative_exposure
from exposure.portfolio import cheapest_configuration, portfolio_costs, portfolio_exposure
from exposure.provider import optimal_provider_price, provider_profit, provider_revenue
from exposure.restoration import compare_paths, simulate_path
from exposure.threshold import adoption_threshold, cheapest_path, outside_option_threshold, restoration_cost


ROOT = Path(__file__).resolve().parents[1]
LABEL = "Scenario result; not an observed industry estimate."


def write_csv(folder, name, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(f"No rows for {name}")
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with (folder / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def load_technology(source):
    with source.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    records = {}
    for row in rows:
        name = row["submission_folder"]
        if name in records:
            raise ValueError(f"Duplicate submission: {name}")
        if row["cost_denominator"] != "per evaluated instance":
            raise ValueError("Execution cost must have the per-evaluated-task denominator")
        execution, _ = agent_cost_components(float(row["avg_cost_usd"]), float(row["resolution_rate"]))
        records[name] = {
            **row, "execution_cost": execution,
            "resolution_rate": float(row["resolution_rate"]),
            "avg_cost_usd": float(row["avg_cost_usd"]),
            "cost_status": "Derived C/P from local benchmark observations; not production acceptance.",
        }
    if not records:
        raise ValueError("Technology input is empty")
    return records


def static_results(settings, records, folder):
    app = settings["software_application"]
    rows = []
    for name, record in records.items():
        for adoption in settings["agent_shares"]:
            baseline = production_cost(app["quarterly_volume"], adoption,
                                       record["execution_cost"], app["human_cost_per_output"])
            for price in settings["price_multipliers"]:
                shocked = production_cost(app["quarterly_volume"], adoption,
                                          price * record["execution_cost"], app["human_cost_per_output"])
                rows.append({
                    "submission": name, "model": record["model"], "agent_share": adoption,
                    "price_multiplier": price, "volume": app["quarterly_volume"],
                    "human_unit_cost": app["human_cost_per_output"], "baseline_cost": baseline,
                    "shocked_cost": shocked, "absolute_exposure": shocked - baseline,
                    "relative_exposure": relative_exposure(baseline, shocked) if baseline > 0 else None,
                    "baseline_execution_spending_share": (
                        app["quarterly_volume"] * adoption * record["execution_cost"] / baseline
                        if baseline > 0 else None
                    ),
                    "provenance": LABEL,
                })
    write_csv(folder, "static_exposure.csv", rows)
    return rows


def supplier_results(settings, folder):
    example = settings["supplier_example"]
    named_sectors = example["sectors"]
    paths = [
        [(p["fixed_cost"], p["provider_spend"]) for p in sector["paths"] if p.get("feasible", True)]
        for sector in named_sectors
    ]
    thresholds, choices = [], []
    for sector, sector_paths in zip(named_sectors, paths):
        # First feasible path is the incumbent; path order defines the tie rule.
        if not sector_paths:
            raise ValueError(f"No feasible path in {sector['name']}")
        feasible_names = [p["name"] for p in sector["paths"] if p.get("feasible", True)]
        thresholds.append({
            "sector": sector["name"],
            "outside_option_threshold": outside_option_threshold(*sector_paths[0], sector_paths[1:]),
            "tie_policy": "first_listed_path", "provenance": "Hypothetical fixed-output sector.",
        })
        for price in settings["price_multipliers"]:
            chosen = cheapest_path(sector_paths, price)
            choices.append({
                "sector": sector["name"], "price_multiplier": price,
                "selected_path": feasible_names[sector_paths.index(chosen)],
                "fixed_cost": chosen[0], "provider_spend_baseline": chosen[1],
                "customer_cost": chosen[0] + price * chosen[1],
                "provenance": "Hypothetical fixed-output sector.",
            })
    optimum = optimal_provider_price(paths, example["marginal_cost_multiplier"],
                                     example["minimum_price"])
    prices = set(settings["price_multipliers"])
    prices.update(t["outside_option_threshold"] for t in thresholds
                  if math.isfinite(t["outside_option_threshold"]))
    if optimum["price"] is not None:
        prices.add(optimum["price"])
    profit_rows = [{
        "price_multiplier": price, "revenue": provider_revenue(paths, price),
        "profit_before_fixed_costs": provider_profit(paths, price, example["marginal_cost_multiplier"]),
        "marginal_cost_multiplier": example["marginal_cost_multiplier"],
        "provenance": "Hypothetical fixed-demand single-supplier pricing example.",
    } for price in sorted(prices)]
    write_csv(folder, "sector_choices.csv", choices)
    write_csv(folder, "outside_option_thresholds.csv", thresholds)
    write_csv(folder, "supplier_profit.csv", profit_rows)
    write_csv(folder, "supplier_price_solution.csv", [{
        **optimum, "minimum_price": example["minimum_price"],
        "provenance": "Conditional optimization of supplied paths; not a market-power estimate.",
    }])
    return optimum


def capacity_results(settings, folder):
    """Separate first substitution from profit-maximizing residual dependence."""
    case = settings["capacity_comparison"]
    incumbent = (case["incumbent_fixed"], case["incumbent_provider_spend"])
    rival = (case["rival_fixed"], case["rival_provider_spend"])
    rows = []
    for capacity in case["retained_capacities"]:
        human_cost = case["human_production_cost"] + restoration_cost(capacity, case["full_restoration_cost"])
        for with_rival in (False, True):
            alternatives = ([rival] if with_rival else []) + [(human_cost, 0)]
            optimum = optimal_provider_price([[incumbent, *alternatives]],
                                             case["marginal_cost_multiplier"])
            rows.append({
                "retained_capacity": capacity, "rival_available": with_rival,
                "human_path_cost": human_cost,
                "outside_option_threshold": outside_option_threshold(*incumbent, alternatives),
                **{f"supplier_{key}": value for key, value in optimum.items()},
                "provenance": "Hypothetical immediate-restoration, one-sector comparison.",
            })
    write_csv(folder, "capacity_supplier_pricing.csv", rows)


def portfolio_results(settings, records, folder):
    app = settings["software_application"]
    configs = {
        row["submission"]: {
            "provider": row["supplier"], "execution_cost": records[row["submission"]]["execution_cost"],
            "feasible": True,
        } for row in app["portfolio_configurations"]
    }
    if len(configs) != len(app["portfolio_configurations"]):
        raise ValueError("Portfolio configurations must be unique")
    shock_provider = app["portfolio_configurations"][0]["supplier"]
    names = list(configs)
    rows, shares = [], []
    for portfolio, weights in app["portfolio_allocations"].items():
        if len(weights) != len(names):
            raise ValueError("One portfolio weight per configuration is required")
        allocation = dict(zip(names, weights))
        base = portfolio_costs(configs, allocation)
        execution_total = sum(base["provider_spend"].values())
        for provider, workload_share in base["provider_output_shares"].items():
            shares.append({
                "portfolio": portfolio, "supplier": provider, "output_share": workload_share,
                "execution_spending_share": (
                    base["provider_spend"][provider] / execution_total if execution_total > 0 else None
                ),
                "provenance": app["portfolio_mapping_note"],
                "output_hhi": sum(weight ** 2 for weight in base["provider_output_shares"].values()),
            })
        for mode in ("common", "provider_specific"):
            for price in settings["price_multipliers"]:
                prices = {provider: price for provider in base["provider_spend"]} if mode == "common" else {
                    shock_provider: price
                }
                exposure = portfolio_exposure(
                    app["quarterly_volume"], app["sensitivity_agent_share"],
                    app["human_cost_per_output"], configs, allocation, prices,
                )
                selected, selected_cost = cheapest_configuration(configs, prices)
                _, cheapest_baseline = cheapest_configuration(configs)
                switched_base = production_cost(app["quarterly_volume"], app["sensitivity_agent_share"],
                                                cheapest_baseline, app["human_cost_per_output"])
                switched_cost = production_cost(app["quarterly_volume"], app["sensitivity_agent_share"],
                                                selected_cost, app["human_cost_per_output"])
                rows.append({
                    "portfolio": portfolio, "shock": mode, "price_multiplier": price, **exposure,
                    "cheapest_configuration": selected, "switching_baseline_cost": switched_base,
                    "switching_shocked_cost": switched_cost,
                    "switching_relative_exposure": (
                        relative_exposure(switched_base, switched_cost) if switched_base > 0 else None
                    ),
                    "switching_level_savings": exposure["shocked_cost"] - switched_cost,
                    "provenance": "Hypothetical allocations and eligibility; frictionless switching bound.",
                })
    write_csv(folder, "provider_shares.csv", shares)
    write_csv(folder, "provider_exposure_switching.csv", rows)


def dynamic_case(settings, record, adoption, capacity, profile, price, **overrides):
    app = settings["software_application"]
    if app["initial_availability_rule"] != "equal_to_initial_human_output":
        raise ValueError("Supply an explicit initial-availability rule before changing it")
    common = {
        "volume": app["quarterly_volume"], "agent_share": adoption,
        "retained_capacity": capacity, "initial_availability": 1 - adoption,
        "execution_cost": record["execution_cost"], "human_cost": app["human_cost_per_output"],
        "horizon": app["horizon_quarters"], "price_multiplier": price,
        "annual_discount_rate": app["annual_discount_rate"],
        "carrying_cost_per_quarter": app["carrying_cost_per_quarter"],
        "review_hours_available": app["review_hours_available"],
        "agent_output_capacity": app["agent_output_capacity"],
    }
    common.update(overrides)
    continuation = simulate_path(**common)
    restoration = simulate_path(
        **common, restore=True,
        total_restoration_cost=restoration_cost(capacity, common["volume"] * profile["cost_per_quarterly_output"]),
        delay_quarters=profile["delay_quarters"], ramp_quarters=profile["ramp_quarters"],
    )
    crossing = compare_paths(continuation, restoration,
                             (min(settings["price_multipliers"]), max(settings["price_multipliers"])))
    adoption_root = adoption_threshold(
        common["execution_cost"], common["human_cost"], common.get("agent_other_cost", 0),
        (min(settings["price_multipliers"]), max(settings["price_multipliers"])),
    )
    gap = None
    if crossing["status"] == adoption_root["status"] == "positive_root":
        gap = crossing["root"] - adoption_root["root"]
    left, right = continuation["summary"], restoration["summary"]
    summary = {
        "agent_share": adoption, "retained_capacity": capacity, "initial_availability": 1 - adoption,
        "price_multiplier": price, "horizon": common["horizon"], "quarterly_volume": common["volume"],
        "human_unit_cost": common["human_cost"], "execution_unit_cost": common["execution_cost"],
        "agent_other_unit_cost": common.get("agent_other_cost", 0),
        "annual_discount_rate": common["annual_discount_rate"],
        "delay_quarters": profile["delay_quarters"], "ramp_quarters": profile["ramp_quarters"],
        "continuation_cost": left["total_cost"], "restoration_cost": right["total_cost"],
        "transition_cost_difference": (
            right["total_cost"] - left["total_cost"]
            if left["total_cost"] is not None and right["total_cost"] is not None else None
        ),
        "adoption_threshold": adoption_root["root"], "adoption_status": adoption_root["status"],
        "adoption_range_status": adoption_root["range_status"],
        "reversal_threshold": crossing["root"], "reversal_status": crossing["status"],
        "reversal_range_status": crossing["range_status"], "reversal_cost_gap": gap,
        "output_feasible": left["output_feasible"] and right["output_feasible"],
        "restoration_target_attained": right["target_attained"],
        "target_time_quarters": right["target_time_quarters"],
        "capability_end": right["capability_end"], "availability_end": right["availability_end"],
        "restoration_paid": right["restoration_paid"], "restoration_planned": right["restoration_planned"],
        "oversight_status": right["oversight_status"],
        "provenance": LABEL,
    }
    return summary, continuation, restoration


def dynamic_results(settings, record, folder):
    summaries, quarters = [], []
    profiles = settings["software_application"]["restoration_profiles"]
    for adoption in settings["agent_shares"]:
        for capacity in settings["retained_capacities"]:
            for profile_name, profile in profiles.items():
                for price in settings["price_multipliers"]:
                    scenario = f"D{adoption}_K{capacity}_{profile_name}_theta{price}"
                    summary, continuation, restoration = dynamic_case(
                        settings, record, adoption, capacity, profile, price
                    )
                    summaries.append({"scenario": scenario, "profile": profile_name, **summary})
                    for path in (continuation, restoration):
                        quarters.extend({
                            "scenario": scenario, "path": path["summary"]["path"], **row,
                            "provenance": LABEL,
                        } for row in path["quarters"])
    write_csv(folder, "restoration_summaries.csv", summaries)
    write_csv(folder, "restoration_quarters.csv", quarters)
    return summaries


def sensitivity_results(settings, record, folder):
    app = settings["software_application"]
    sensitivity = app["sensitivities"]
    base_profile = app["restoration_profiles"][app["sensitivity_profile"]]
    cases = [("baseline", base_profile, {})]
    for horizon in sensitivity["horizons"]:
        cases.append((f"horizon_{horizon}", base_profile, {"horizon": horizon}))
    for rate in sensitivity["annual_discount_rates"]:
        cases.append((f"discount_{rate}", base_profile, {"annual_discount_rate": rate}))
    for human_cost in sensitivity["human_costs"]:
        cases.append((f"human_cost_{human_cost}", base_profile, {"human_cost": human_cost}))
    for factor in sensitivity["acceptance_factors"]:
        execution, other = agent_cost_components(record["avg_cost_usd"], record["resolution_rate"] * factor)
        cases.append((f"acceptance_factor_{factor}", base_profile, {
            "execution_cost": execution, "agent_other_cost": other
        }))
    for minutes in sensitivity["review_minutes_per_evaluated_task"]:
        execution, other = agent_cost_components(
            record["avg_cost_usd"], record["resolution_rate"],
            review_hours=minutes / 60, review_wage=sensitivity["review_hourly_wage"],
        )
        cases.append((f"review_minutes_{minutes}", base_profile, {
            "execution_cost": execution, "agent_other_cost": other,
            "review_hours_per_output": minutes / 60 / record["resolution_rate"],
        }))
    for rework in sensitivity["rework_costs_per_evaluated_task"]:
        execution, other = agent_cost_components(record["avg_cost_usd"], record["resolution_rate"], rework=rework)
        cases.append((f"rework_{rework}", base_profile, {
            "execution_cost": execution, "agent_other_cost": other
        }))
    for pipeline in sensitivity["pipeline"]:
        if pipeline["additional_delay"] < 0 or pipeline["ramp_multiplier"] < 1:
            raise ValueError("Pipeline delay must be nonnegative and ramp multiplier >= 1")
        profile = {
            **base_profile,
            "delay_quarters": base_profile["delay_quarters"] + pipeline["additional_delay"],
            "ramp_quarters": math.ceil(base_profile["ramp_quarters"] * pipeline["ramp_multiplier"]),
        }
        cases.append((f"talent_pipeline_{pipeline['name']}", profile, {}))
    rows = []
    for name, profile, overrides in cases:
        summary, _, _ = dynamic_case(
            settings, record, app["sensitivity_agent_share"], app["sensitivity_capacity"],
            profile, app["sensitivity_price"], **overrides,
        )
        rows.append({
            "sensitivity": name, **summary,
            "note": "One-at-a-time hypothetical sensitivity. Pipeline cases assume talent development is relevant.",
        })
    write_csv(folder, "sensitivities.csv", rows)


def firm_results(settings, record, folder):
    app = settings["software_application"]
    profile = app["restoration_profiles"][app["sensitivity_profile"]]
    rows = []
    for firm in settings["hypothetical_firms"]:
        annual = firm["annual_volume"]
        for price in settings["price_multipliers"]:
            summary, _, _ = dynamic_case(
                settings, record, firm["agent_share"], firm["retained_capacity"], profile, price,
                volume=1000,
            )
            normalized = production_cost(1000, firm["agent_share"], record["execution_cost"],
                                         app["human_cost_per_output"])
            shocked = production_cost(1000, firm["agent_share"], price * record["execution_cost"],
                                       app["human_cost_per_output"])
            rows.append({
                "firm": firm["name"], "annual_volume": annual,
                "normalized_baseline_cost_per_1000": normalized,
                "normalized_shocked_cost_per_1000": shocked,
                "annual_baseline_cost": normalized * annual / 1000 if annual is not None else None,
                "annual_shocked_cost": shocked * annual / 1000 if annual is not None else None,
                "static_relative_exposure": relative_exposure(normalized, shocked),
                **summary, "provenance": "Hypothetical firm; dynamic costs per 1000 output units per quarter.",
            })
    write_csv(folder, "hypothetical_firms.csv", rows)


def plots(static, dynamic, settings, destination):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    destination.mkdir(parents=True, exist_ok=True)
    reference = settings["software_application"]["reference_submission"]
    fig, ax = plt.subplots()
    for adoption in settings["agent_shares"]:
        rows = sorted((row for row in static if row["submission"] == reference and row["agent_share"] == adoption),
                      key=lambda row: row["price_multiplier"])
        ax.plot([row["price_multiplier"] for row in rows],
                [row["shocked_cost"] / row["baseline_cost"] if row["baseline_cost"] > 0 else math.nan
                 for row in rows], marker="o", label=f"D={adoption}")
    ax.set(xlabel="Execution price multiplier", ylabel="Cost / same-mix baseline",
           title="Scenario software price exposure")
    ax.legend()
    fig.savefig(destination / "price_exposure.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    app = settings["software_application"]
    adoptions, capacities = settings["agent_shares"], settings["retained_capacities"]
    lookup = {(row["agent_share"], row["retained_capacity"]): row for row in dynamic
              if row["profile"] == app["sensitivity_profile"] and row["price_multiplier"] == app["sensitivity_price"]}
    matrix = [[lookup[d, k]["transition_cost_difference"]
               if lookup[d, k]["transition_cost_difference"] is not None else math.nan
               for d in adoptions] for k in capacities]
    fig, ax = plt.subplots()
    bound = max((abs(value) for line in matrix for value in line if math.isfinite(value)), default=1) or 1
    im = ax.imshow(matrix, cmap="coolwarm", vmin=-bound, vmax=bound, aspect="auto")
    ax.set_xticks(range(len(adoptions)), labels=adoptions)
    ax.set_yticks(range(len(capacities)), labels=capacities)
    ax.set(xlabel="Initial agent output share D", ylabel="Retained human capability K",
           title=f"Scenario transition cost difference (theta={app['sensitivity_price']})")
    fig.colorbar(im, ax=ax, label="Restoration minus continuation cost (USD)")
    fig.savefig(destination / "transition_cost_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "scenarios.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/model")
    parser.add_argument("--plots", action="store_true", help="Optional matplotlib figures; no interactive windows")
    args = parser.parse_args()
    settings = json.loads(args.config.read_text(encoding="utf-8"))
    source = ROOT / "data/raw/swebench_runs.csv"
    records = load_technology(source)
    app = settings["software_application"]
    reference = records[app["reference_submission"]]
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output, "technology_inputs.csv", records.values())
    static = static_results(settings, records, args.output)
    optimum = supplier_results(settings, args.output)
    capacity_results(settings, args.output)
    portfolio_results(settings, records, args.output)
    dynamic = dynamic_results(settings, reference, args.output)
    sensitivity_results(settings, reference, args.output)
    firm_results(settings, reference, args.output)
    inputs = args.output / "inputs"
    inputs.mkdir(exist_ok=True)
    for path in (args.config, source):
        destination = inputs / path.name
        if path.resolve() != destination.resolve():
            shutil.copyfile(path, destination)
    code_files = [Path(__file__), *sorted((ROOT / "src/exposure").glob("*.py"))]
    manifest = {
        "python_version": platform.python_version(), "provenance": settings["provenance"],
        "input_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (args.config, source)},
        "code_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in code_files},
        "reference_submission": app["reference_submission"],
        "plotting_library_version": version("matplotlib") if args.plots else None,
        "limitations": [
            "No economy-wide population weights or measured adoption/capability values.",
            "Human cost, restoration, sector paths and supplier identities are hypothetical.",
            "Benchmark-resolved output is not proven production acceptance.",
            "Available human production capacity is net of separately budgeted review work.",
            "Oversight is unverified unless a dedicated review budget is supplied.",
            "Supplier pricing assumes fixed demand, price-independent paths, and first-listed ties.",
            "Finite-horizon paths have no terminal value; unfinished restoration is reported.",
        ],
        "static_rows": len(static), "dynamic_summary_rows": len(dynamic),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if args.plots:
        plots(static, dynamic, settings, args.output / "figures")
    print(f"Results: {args.output}")
    print(f"Static scenarios: {len(static)}; restoration scenarios: {len(dynamic)}")
    print(f"Conditional supplier solution: {optimum['status']}, price={optimum['price']}, profit={optimum['profit']}")
    print("All examples remain conditional scenarios, not observed industry or monopoly estimates.")


if __name__ == "__main__":
    main()
