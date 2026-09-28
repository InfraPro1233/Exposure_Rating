from exposure.validation import nonnegative, positive, share


def effective_cost(cost_per_evaluated_task, resolution_rate):
    """Recorded execution dollars per benchmark-resolved output, not production proof."""
    nonnegative(cost_per_evaluated_task, "Execution cost")
    positive(resolution_rate, "Resolution rate")
    share(resolution_rate, "Resolution rate")
    return cost_per_evaluated_task / resolution_rate


def agent_cost_components(cost, resolution_rate, review_hours=0, review_wage=0, rework=0):
    """All numerator inputs are per evaluated task. Only execution is price-shocked."""
    execution = effective_cost(cost, resolution_rate)
    nonnegative(review_hours, "Review hours")
    nonnegative(review_wage, "Review wage")
    nonnegative(rework, "Rework")
    other = (review_hours * review_wage + rework) / resolution_rate
    return execution, other


def production_cost(volume, agent_share, agent_cost, human_cost):
    nonnegative(volume, "Volume")
    share(agent_share, "Agent share")
    nonnegative(agent_cost, "Agent cost")
    nonnegative(human_cost, "Human cost")
    return volume * (agent_share * agent_cost + (1 - agent_share) * human_cost)


def relative_exposure(baseline_cost, shocked_cost):
    positive(baseline_cost, "Baseline cost")
    nonnegative(shocked_cost, "Shocked cost")
    return (shocked_cost - baseline_cost) / baseline_cost


def price_exposure(provider_spend, price_multiplier):
    nonnegative(provider_spend, "Provider spending")
    positive(price_multiplier, "Price multiplier")
    return (price_multiplier - 1) * provider_spend
