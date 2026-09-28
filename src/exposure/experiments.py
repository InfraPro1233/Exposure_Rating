"""Small, declared scenario contrasts; not forecasts or estimated causal effects."""

from copy import deepcopy

from exposure.company import evaluate_company
from exposure.cost import relative_exposure
from exposure.threshold import cheapest_path, outside_option_threshold
from exposure.validation import nonnegative, share


def _cases(settings):
    cases = {case["name"]: case for case in settings["company_cases"]}
    if len(cases) != len(settings["company_cases"]):
        raise ValueError("Company case names must be unique")
    return [cases[name] for name in settings["experiment_settings"]["case_names"]]


def _evaluate(settings, case, inputs=None, basis=None):
    experiment = settings["experiment_settings"]
    prices = list(settings["price_multipliers"])
    comparison = experiment["comparison_price_multiplier"]
    if comparison not in prices:
        prices.append(comparison)
    return evaluate_company(
        inputs if inputs is not None else case["company_inputs"],
        settings["institutional_assumptions"][case["institutional_profile"]],
        basis if basis is not None else settings["basis"], prices,
    )


def _row(settings, case, result, **metadata):
    summary = result["summary"]
    exposure = next(row for row in result["exposure"]
                    if row["price_multiplier"] == settings["experiment_settings"]["comparison_price_multiplier"])
    return {
        "case": case["name"], **metadata, **summary,
        "comparison_price_multiplier": exposure["price_multiplier"],
        "fixed_mix_relative_exposure": exposure["fixed_mix_relative_exposure"],
        "adaptive_relative_exposure": exposure["adaptive_relative_exposure"],
        "selected_path_at_comparison_price": exposure["selected_path"],
        "selected_residual_incumbent_spend": exposure["selected_residual_incumbent_spend"],
        "provenance": "Hypothetical conditional comparison; not an estimated industry or monopoly effect.",
    }


def capacity_sensitivity(settings):
    experiment = settings["experiment_settings"]
    rows = []
    for case in _cases(settings):
        base = case["company_inputs"]
        for field, values in (
            ("retained_capability", experiment["capability_grid"]),
            ("immediately_replaceable_ai_output_share", experiment["available_share_grid"]),
        ):
            for value in values:
                result = _evaluate(settings, case, {**base, field: value})
                rows.append(_row(settings, case, result, changed_parameter=field, parameter_value=value))
    return rows


def capacity_surface(settings):
    experiment = settings["experiment_settings"]
    rows = []
    for case in _cases(settings):
        for capacity in experiment["capability_grid"]:
            for available in experiment["available_share_grid"]:
                inputs = {
                    **case["company_inputs"], "retained_capability": capacity,
                    "immediately_replaceable_ai_output_share": available,
                }
                rows.append(_row(settings, case, _evaluate(settings, case, inputs),
                                 comparison="joint K/availability scenario, not a causal estimate"))
    return rows


def horizon_sensitivity(settings):
    experiment = settings["experiment_settings"]
    rows = []
    for case in _cases(settings):
        for field, values in (
            ("horizon_quarters", experiment["horizon_grid"]),
            ("annual_discount_rate", experiment["annual_discount_rates"]),
        ):
            for value in values:
                basis = {**settings["basis"], field: value}
                rows.append(_row(settings, case, _evaluate(settings, case, basis=basis),
                                 changed_parameter=field, parameter_value=value))
    return rows


def spending_sensitivity(settings):
    rows = []
    for case in _cases(settings):
        for spend in settings["experiment_settings"]["incumbent_spend_grid"]:
            inputs = {**case["company_inputs"], "incumbent_ai_spend_per_quarter": spend}
            rows.append(_row(settings, case, _evaluate(settings, case, inputs),
                             changed_parameter="incumbent_ai_spend_per_quarter", parameter_value=spend,
                             note="A and H fixed; total baseline cost changes. Not an adoption or concentration estimate."))
    return rows


def rivalry_sensitivity(settings):
    experiment = settings["experiment_settings"]
    rows = []
    for case in _cases(settings):
        rivals = case["company_inputs"].get("feasible_rivals", [])
        if not any(rival["feasible"] for rival in rivals):
            continue
        names = [rival["name"] for rival in rivals if rival["feasible"]]
        for name in names:
            variants = [("eligibility", False)]
            variants += [("switching_cost", fee) for fee in experiment["rival_switching_costs"]]
            variants += [("residual_share", fraction) for fraction in experiment["rival_residual_shares"]]
            for parameter, value in variants:
                inputs = deepcopy(case["company_inputs"])
                rival = next(row for row in inputs["feasible_rivals"] if row["name"] == name)
                baseline = rival["fixed_cost_per_quarter"] + rival["residual_incumbent_spend_per_quarter"]
                if parameter == "eligibility":
                    rival["feasible"] = value
                elif parameter == "switching_cost":
                    rival["one_time_switching_cost"] = value
                else:
                    share(value, "Rival residual share")
                    residual = value * inputs["incumbent_ai_spend_per_quarter"]
                    if residual > baseline:
                        raise ValueError("Residual spending cannot exceed the fixed rival baseline")
                    # Keep rival total baseline cost fixed, replacing unshocked
                    # cost with incumbent-dependent cost. This is a declared
                    # linked reparameterization, not two independent changes.
                    rival["residual_incumbent_spend_per_quarter"] = residual
                    rival["fixed_cost_per_quarter"] = baseline - residual
                rows.append(_row(settings, case, _evaluate(settings, case, inputs),
                                 rival=name, changed_parameter=parameter, parameter_value=value,
                                 rival_total_baseline_cost_per_quarter=(
                                     rival["fixed_cost_per_quarter"] + rival["residual_incumbent_spend_per_quarter"]
                                 ),
                                 note="Residual-share contrast preserves rival baseline cost; fees/eligibility vary separately."))
    return rows


def common_price_coefficients(result, inputs, basis):
    """Reprice OTHER AI execution costs under the same theta, preserving baseline costs.

    Decompositions must be explicitly supplied; do not infer them from total
    costs or organization names. Returned slopes are pooled AI spend, NOT only
    incumbent-provider spend. Feasible options remain those in the base result.
    """
    if "other_ai_spend_per_quarter" not in inputs:
        raise ValueError("Common-price comparison requires an explicit other-AI spending decomposition")
    other = nonnegative(inputs["other_ai_spend_per_quarter"], "Other AI spending")
    if other > inputs["unaffected_cost_per_quarter"]:
        raise ValueError("Other AI spending cannot exceed unaffected baseline costs")
    rivals = {rival["name"]: rival for rival in inputs.get("feasible_rivals", [])}
    rate = basis["annual_discount_rate"]
    weights = sum((1 + rate) ** (-quarter / 4)
                  for quarter in range(1, basis["horizon_quarters"] + 1))
    transformed = {}
    for name, (fixed, spend) in result["coefficients"].items():
        if name in rivals:
            if "other_provider_ai_spend_per_quarter" not in rivals[name]:
                raise ValueError("Common-price comparison requires rival other-provider AI spending")
            other_spend = nonnegative(rivals[name]["other_provider_ai_spend_per_quarter"],
                                     "Rival other-provider AI spending")
            if other_spend > rivals[name]["fixed_cost_per_quarter"]:
                raise ValueError("Rival other-provider spending cannot exceed fixed baseline costs")
        else:
            other_spend = other
        amount = weights * other_spend
        transformed[name] = (fixed - amount, spend + amount)
    return transformed


def shock_scope_sensitivity(settings):
    rows = []
    basis = settings["basis"]
    for case in _cases(settings):
        result = _evaluate(settings, case)
        scopes = {
            "incumbent_provider": result["coefficients"],
            "common_ai_prices": common_price_coefficients(result, case["company_inputs"], basis),
        }
        for scope, coefficients in scopes.items():
            names, paths = list(coefficients), list(coefficients.values())
            incumbent = coefficients["incumbent"]
            baseline = sum(incumbent)
            adaptive_baseline = sum(cheapest_path(paths, 1))
            threshold = outside_option_threshold(*incumbent, [
                path for name, path in coefficients.items() if name != "incumbent"
            ])
            for price in settings["price_multipliers"]:
                selected = cheapest_path(paths, price)
                shocked = incumbent[0] + price * incumbent[1]
                best = selected[0] + price * selected[1]
                rows.append({
                    "case": case["name"], "shock_scope": scope, "price_multiplier": price,
                    "outside_option_threshold": threshold,
                    "baseline_cost": baseline, "shocked_fixed_mix_cost": shocked,
                    "fixed_mix_relative_exposure": relative_exposure(baseline, shocked) if baseline > 0 else None,
                    "selected_path": names[paths.index(selected)], "minimum_feasible_cost": best,
                    "adaptive_relative_exposure": (
                        relative_exposure(adaptive_baseline, best) if adaptive_baseline > 0 else None
                    ),
                    "selected_shock_sensitive_spend": selected[1],
                    "cost_unit": basis["cost_unit"],
                    "provenance": "Hypothetical proportional repricing; pooled slopes in common-shock rows.",
                })
    return rows


def provider_allocation_sensitivity(settings):
    """Pure spending-share identity at a fixed total budget; no inferred task shares."""
    rows = []
    for case in _cases(settings):
        inputs = case["company_inputs"]
        other = nonnegative(inputs["other_ai_spend_per_quarter"], "Other AI spending")
        total_ai = inputs["incumbent_ai_spend_per_quarter"] + other
        non_ai = inputs["unaffected_cost_per_quarter"] - other
        nonnegative(non_ai, "Non-AI cost")
        baseline = non_ai + total_ai
        for fraction in settings["experiment_settings"]["selected_provider_spending_shares"]:
            share(fraction, "Selected provider spending share")
            remainder = (1 - fraction) / 2
            hhi = fraction ** 2 + 2 * remainder ** 2
            for scope in ("selected_provider", "common_ai_prices"):
                affected = total_ai * fraction if scope == "selected_provider" else total_ai
                for price in settings["price_multipliers"]:
                    change = (price - 1) * affected
                    rows.append({
                        "case": case["name"], "selected_provider_spending_share": fraction,
                        "cost_unit": settings["basis"]["cost_unit"],
                        "spending_hhi": hhi, "shock_scope": scope, "price_multiplier": price,
                        "baseline_cost_per_quarter": baseline, "total_ai_spending_per_quarter": total_ai,
                        "affected_spend_per_quarter": affected, "absolute_exposure": change,
                        "relative_exposure": change / baseline if baseline > 0 else None,
                        "provenance": "Hypothetical 3-provider spending allocation; other two split remainder equally.",
                        "note": "Financial spending concentration, not task shares, market concentration or monopoly evidence.",
                    })
    return rows


def company_experiments(settings):
    return {
        "capacity_sensitivity.csv": capacity_sensitivity(settings),
        "capacity_surface.csv": capacity_surface(settings),
        "horizon_discount_sensitivity.csv": horizon_sensitivity(settings),
        "spending_sensitivity.csv": spending_sensitivity(settings),
        "rival_constraints.csv": rivalry_sensitivity(settings),
        "shock_scope_sensitivity.csv": shock_scope_sensitivity(settings),
        "provider_allocation_sensitivity.csv": provider_allocation_sensitivity(settings),
    }
