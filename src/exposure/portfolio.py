"""Output-weighted configurations; provider IDs must be supplied, not inferred."""

import math

from exposure.cost import production_cost, relative_exposure
from exposure.validation import nonnegative, positive


def portfolio_costs(configurations, allocation, prices=None):
    prices = prices or {}
    providers = {config["provider"] for config in configurations.values()}
    if set(prices) - providers:
        raise ValueError("Price multipliers reference an unknown supplier")
    for price in prices.values():
        positive(price, "Provider price multiplier")
    if not allocation:
        raise ValueError("An output allocation is required")
    for weight in allocation.values():
        nonnegative(weight, "Allocation weight")
    if not math.isclose(sum(allocation.values()), 1, rel_tol=0, abs_tol=1e-10):
        raise ValueError("Output allocation must sum to one")
    execution, other = 0, 0
    provider_spend, provider_shares = {}, {}
    for name, weight in allocation.items():
        if name not in configurations:
            raise ValueError(f"Unknown configuration: {name}")
        config = configurations[name]
        if weight > 0 and not config.get("feasible", True):
            raise ValueError(f"Allocated configuration is infeasible: {name}")
        cost = nonnegative(config["execution_cost"], "Execution cost")
        extra = nonnegative(config.get("other_cost", 0), "Other agent cost")
        provider = config["provider"]
        provider_spend[provider] = provider_spend.get(provider, 0) + weight * cost
        provider_shares[provider] = provider_shares.get(provider, 0) + weight
        execution += weight * cost * prices.get(provider, 1)
        other += weight * extra
    return {
        "agent_cost": execution + other, "execution_cost": execution,
        "other_cost": other, "provider_spend": provider_spend,
        "provider_output_shares": provider_shares,
    }


def cheapest_configuration(configurations, prices=None):
    prices = prices or {}
    candidates = {
        name: portfolio_costs(configurations, {name: 1}, prices)["agent_cost"]
        for name, config in configurations.items() if config.get("feasible", True)
    }
    if not candidates:
        raise ValueError("No feasible configuration")
    name = min(candidates, key=candidates.get)
    return name, candidates[name]


def portfolio_exposure(volume, agent_share, human_cost, configurations, allocation, prices):
    baseline_agent = portfolio_costs(configurations, allocation)
    shocked_agent = portfolio_costs(configurations, allocation, prices)
    baseline = production_cost(volume, agent_share, baseline_agent["agent_cost"], human_cost)
    shocked = production_cost(volume, agent_share, shocked_agent["agent_cost"], human_cost)
    return {
        "baseline_cost": baseline, "shocked_cost": shocked,
        "absolute_exposure": shocked - baseline,
        "relative_exposure": relative_exposure(baseline, shocked) if baseline > 0 else None,
    }
