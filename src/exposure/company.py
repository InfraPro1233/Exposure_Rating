"""Company-owned cost inputs plus SEPARATE institutional reconstruction assumptions.

No model identifiers, token prices, benchmark scores, or task-count estimates
are required. One output unit is the current affected-AI workload basket.
"""

import math

from exposure.cost import relative_exposure
from exposure.restoration import compare_paths, simulate_path
from exposure.threshold import (
    adoption_threshold, cheapest_path, outside_option_threshold, restoration_cost,
)
from exposure.validation import nonnegative, positive, quarters, share


def evaluate_company(company_inputs, institutional_assumptions, basis, prices):
    prices = list(prices)
    if not prices:
        raise ValueError("At least one price scenario is required")
    for price in prices:
        positive(price, "Price multiplier")
    if not basis.get("cost_unit") or not basis.get("output_unit"):
        raise ValueError("Specify cost and common-output units")
    horizon = quarters(basis["horizon_quarters"], "Horizon")
    rate = nonnegative(basis["annual_discount_rate"], "Annual discount rate")
    fixed = nonnegative(company_inputs["unaffected_cost_per_quarter"], "Unaffected costs")
    spend = nonnegative(company_inputs["incumbent_ai_spend_per_quarter"], "Incumbent AI spending")
    human = nonnegative(company_inputs["replacement_human_cost_per_quarter"], "Incremental human replacement cost")
    capacity = share(company_inputs["retained_capability"], "Retained capability")
    available = share(company_inputs["immediately_replaceable_ai_output_share"], "Immediately replaceable share")
    institution = institutional_assumptions
    if institution["cost_rule"] == "full_reconstitution_cost_times_one_minus_K":
        total_rebuild = restoration_cost(capacity, institution["full_reconstitution_cost"])
    elif institution["cost_rule"] == "supplied_total":
        total_rebuild = nonnegative(institution["total_reconstitution_cost"], "Supplied rebuilding bill")
    else:
        raise ValueError("Specify a supported restoration-cost rule")
    delay = quarters(institution["delay_quarters"], "Institutional delay", allow_zero=True)
    ramp = quarters(institution["ramp_quarters"], "Institutional ramp", allow_zero=True)
    if not isinstance(institution["human_substitution_path_feasible"], bool):
        raise ValueError("Institutional path feasibility must be an explicit boolean")
    common = {
        "volume": 1, "agent_share": 1, "retained_capacity": capacity,
        "initial_availability": available, "execution_cost": spend, "human_cost": human,
        "carrying_cost_per_quarter": fixed, "horizon": horizon, "annual_discount_rate": rate,
        "review_hours_per_output": company_inputs.get("review_hours_per_ai_basket", 0),
        "review_hours_available": company_inputs.get("dedicated_review_hours_available"),
    }
    continuation = simulate_path(**common)
    if not continuation["summary"]["output_feasible"]:
        raise ValueError("Company baseline cannot meet the supplied output/review constraints")
    paths = {"incumbent": continuation}
    # Existing human capacity can be a PARTIAL outside option even when full
    # institutional reconstruction is impossible. Do not delete this option.
    if available > 0:
        paths["retained_humans"] = simulate_path(**{**common, "agent_share": 1 - available})
    rebuilding = None
    if institution["human_substitution_path_feasible"]:
        rebuilding = simulate_path(
            **common, restore=True, total_restoration_cost=total_rebuild,
            delay_quarters=delay, ramp_quarters=ramp,
        )
    period_weights = sum((1 + rate) ** (-t / 4) for t in range(1, horizon + 1))
    rival_paths = {}
    for rival in company_inputs.get("feasible_rivals", []):
        if not isinstance(rival["feasible"], bool):
            raise ValueError("Rival feasibility must be an explicit boolean")
        if not rival["feasible"]:
            continue
        name = rival["name"]
        if name in ("incumbent", "retained_humans", "human_reconstitution") or name in rival_paths:
            raise ValueError(f"Rival name must be unique: {name}")
        alternative_fixed = nonnegative(rival["fixed_cost_per_quarter"], "Rival fixed cost")
        residual = nonnegative(rival["residual_incumbent_spend_per_quarter"], "Rival residual incumbent spending")
        switching = nonnegative(rival["one_time_switching_cost"], "Rival switching cost")
        # Rival fixed cost is TOTAL unshocked cost, not a surcharge on fixed.
        # The switching bill is paid in quarter 1 with the same discount rule.
        rival_paths[name] = (
            alternative_fixed * period_weights + switching * (1 + rate) ** (-1 / 4),
            residual * period_weights,
        )
    coefficients = {
        name: (path["summary"]["fixed_cost"], path["summary"]["provider_spend_baseline"])
        for name, path in paths.items() if path["summary"]["output_feasible"]
    }
    coefficients.update(rival_paths)
    if rebuilding is not None:
        paths["human_reconstitution"] = rebuilding
    if (rebuilding is not None and rebuilding["summary"]["output_feasible"]
            and any(row["human_share"] > 0 for row in rebuilding["quarters"])):
        coefficients["human_reconstitution"] = (
            rebuilding["summary"]["fixed_cost"], rebuilding["summary"]["provider_spend_baseline"],
        )
    incumbent = coefficients["incumbent"]
    alternatives = [path for name, path in coefficients.items() if name != "incumbent"]
    threshold = outside_option_threshold(*incumbent, alternatives)
    price_range = min(prices), max(prices)
    if rebuilding is None:
        human_root = {"root": None, "status": "institutional_path_infeasible", "range_status": "not_applicable"}
    else:
        human_root = compare_paths(continuation, rebuilding, price_range)
    unit_benchmark = adoption_threshold(spend, human, price_range=price_range)
    gap = None
    if human_root["status"] == unit_benchmark["status"] == "positive_root":
        gap = human_root["root"] - unit_benchmark["root"]
    feasible_paths = list(coefficients.values())
    names = list(coefficients)
    unshocked_best = cheapest_path(feasible_paths, 1)
    adaptive_baseline = sum(unshocked_best)
    baseline = sum(incumbent)
    exposure_rows = []
    for price in prices:
        shocked = incumbent[0] + price * incumbent[1]
        chosen = cheapest_path(feasible_paths, price)
        best_cost = chosen[0] + price * chosen[1]
        exposure_rows.append({
            "price_multiplier": price, "baseline_cost": baseline, "fixed_mix_cost": shocked,
            "fixed_mix_absolute_exposure": shocked - baseline,
            "fixed_mix_relative_exposure": relative_exposure(baseline, shocked) if baseline > 0 else None,
            "selected_path": names[feasible_paths.index(chosen)], "minimum_feasible_cost": best_cost,
            "adaptive_baseline_cost": adaptive_baseline,
            "adaptive_relative_exposure": relative_exposure(adaptive_baseline, best_cost) if adaptive_baseline > 0 else None,
            "selected_residual_incumbent_spend": chosen[1],
        })
    summary = {
        "cost_unit": basis["cost_unit"], "horizon_quarters": horizon,
        "retained_capability": capacity, "immediately_replaceable_ai_output_share": available,
        "baseline_cost": baseline,
        "incumbent_spending_share": incumbent[1] / baseline if baseline > 0 else None,
        "outside_option_threshold": threshold,
        "outside_option_status": "no_feasible_crossing" if math.isinf(threshold) else (
            "baseline_competitive" if threshold == 1 else "finite_threshold"
        ),
        "outside_option_range_status": "no_crossing" if math.isinf(threshold) else (
            "above_range" if threshold > max(prices) else (
                "below_range" if threshold < min(prices) else "within_range"
            )
        ),
        "incremental_human_unit_benchmark": unit_benchmark["root"],
        "human_reconstitution_root": human_root["root"],
        "human_reconstitution_status": human_root["status"],
        "human_reconstitution_range_status": human_root["range_status"],
        "conditional_reconstitution_gap": gap,
        "reconstitution_cost_planned": total_rebuild,
        "restoration_path_feasible": rebuilding["summary"]["output_feasible"] if rebuilding else False,
        "restoration_target_attained": rebuilding["summary"]["target_attained"] if rebuilding else False,
        "restoration_paid": rebuilding["summary"]["restoration_paid"] if rebuilding else None,
        "target_time_quarters": rebuilding["summary"]["target_time_quarters"] if rebuilding else None,
        "restoration_residual_incumbent_spend": rebuilding["summary"]["provider_spend_baseline"] if rebuilding else None,
        "capability_end": rebuilding["summary"]["capability_end"] if rebuilding else capacity,
        "rival_count": len(rival_paths),
        "oversight_status": continuation["summary"]["oversight_status"],
    }
    return {
        "summary": summary, "exposure": exposure_rows, "coefficients": coefficients,
        "quarterly_paths": paths,
    }
