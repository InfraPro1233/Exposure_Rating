"""Supplied quarterly paths, not optimal workforce/adoption decisions.

Availability is NET of separately budgeted review work. Capability K is tracked
separately and is never set to 1-D. Agents fill the remaining output only when
the explicit agent-capacity and review assumptions permit it.
"""

from exposure.threshold import cost_crossing
from exposure.validation import nonnegative, positive, quarters, share


def _progress(time, delay, ramp):
    if ramp == 0:
        return float(time > delay)
    return max(0.0, min(1.0, (time - delay) / ramp))


def _average_progress(quarter, delay, ramp):
    # Integrate the continuous ramp over the quarter; an end-quarter hire does
    # not receive a full quarter's output.
    start, end = quarter - 1, quarter
    if ramp == 0:
        return max(0.0, min(1.0, end - max(start, delay)))
    def integral(time):
        elapsed = max(0.0, time - delay)
        if elapsed <= ramp:
            return elapsed * elapsed / (2 * ramp)
        return elapsed - ramp / 2
    return integral(end) - integral(start)


def simulate_path(
    volume, agent_share, retained_capacity, initial_availability,
    execution_cost, human_cost, *, restore=False, horizon=20,
    agent_other_cost=0, price_multiplier=1, total_restoration_cost=0,
    delay_quarters=0, ramp_quarters=4, carrying_cost_per_quarter=0,
    annual_discount_rate=0, review_hours_per_output=0,
    review_hours_available=None, agent_output_capacity=1,
):
    """Evaluate continuation or a linear restoration to K=A=1.

    Restoration is paid uniformly during the productive ramp, including only
    the portion reached within the horizon. A zero-length ramp is an explicit
    instantaneous limit; payment occurs in the first quarter after its delay.
    Delay and ramp are supplied, not inferred from K. Volume is per quarter.
    """
    positive(volume, "Quarterly volume")
    share(agent_share, "Initial agent share")
    share(retained_capacity, "Retained capability")
    share(initial_availability, "Initial human availability")
    share(agent_output_capacity, "Agent output capacity")
    for value, name in (
        (execution_cost, "Execution cost"), (human_cost, "Human cost"),
        (agent_other_cost, "Other agent cost"), (total_restoration_cost, "Restoration cost"),
        (carrying_cost_per_quarter, "Carrying cost"), (annual_discount_rate, "Discount rate"),
        (review_hours_per_output, "Review hours per output"),
    ):
        nonnegative(value, name)
    if review_hours_available is not None:
        nonnegative(review_hours_available, "Dedicated review hours")
    positive(price_multiplier, "Price multiplier")
    horizon = quarters(horizon, "Horizon")
    delay = quarters(delay_quarters, "Restoration delay", allow_zero=True)
    ramp = quarters(ramp_quarters, "Restoration ramp", allow_zero=True)
    if not restore and total_restoration_cost != 0:
        raise ValueError("Continuation cannot include restoration spending")
    initial_human_share = 1 - agent_share
    initial_valid = initial_availability + 1e-12 >= initial_human_share
    rows = []
    cumulative, fixed_total, spend_total, paid_restoration = 0, 0, 0, 0
    for quarter in range(1, horizon + 1):
        progress = _average_progress(quarter, delay, ramp) if restore else 0
        end_progress = _progress(quarter, delay, ramp) if restore else 0
        capability = retained_capacity + (1 - retained_capacity) * end_progress
        availability = initial_availability + (1 - initial_availability) * progress
        end_availability = initial_availability + (1 - initial_availability) * end_progress
        intended_human = 1 if restore else initial_human_share
        human_share = min(intended_human, availability)
        residual_agent_share = 1 - human_share
        required_review = volume * residual_agent_share * review_hours_per_output
        review_feasible = review_hours_available is None or (
            required_review <= review_hours_available + 1e-12
        )
        reasons = []
        if not initial_valid:
            reasons.append("initial_availability_below_initial_human_output")
        if residual_agent_share > agent_output_capacity + 1e-12:
            reasons.append("insufficient_agent_capacity")
        if not review_feasible:
            reasons.append("insufficient_dedicated_review_hours")
        if ramp == 0:
            payment_share = float(quarter == delay + 1)
        else:
            payment_share = max(
                0, min(quarter, delay + ramp) - max(quarter - 1, delay)
            ) / ramp
        restoration_spend = total_restoration_cost * payment_share if restore else 0
        human_spend = volume * human_share * human_cost
        agent_other = volume * residual_agent_share * agent_other_cost
        execution_spend = volume * residual_agent_share * execution_cost
        fixed = human_spend + agent_other + restoration_spend + carrying_cost_per_quarter
        weight = (1 + annual_discount_rate) ** (-quarter / 4)
        cost = weight * (fixed + price_multiplier * execution_spend)
        cumulative += cost
        fixed_total += weight * fixed
        spend_total += weight * execution_spend
        paid_restoration += restoration_spend
        rows.append({
            "quarter": quarter, "required_output": volume,
            "capability_end": capability,
            "human_availability_average": availability, "human_availability_end": end_availability,
            "human_share": human_share, "agent_share": residual_agent_share,
            "human_output": volume * human_share, "agent_output": volume * residual_agent_share,
            "review_hours_required": required_review,
            "review_status": "unverified" if review_hours_available is None else (
                "sufficient_supplied_budget" if review_feasible else "insufficient"
            ),
            "output_feasible": not reasons, "infeasibility_reason": ";".join(reasons),
            "human_cost": human_spend, "agent_other_cost": agent_other,
            "provider_spend_baseline": execution_spend,
            "restoration_spend": restoration_spend, "carrying_cost": carrying_cost_per_quarter,
            "discount_weight": weight, "fixed_cost": fixed,
            "planned_total_cost": cost, "cumulative_planned_cost": cumulative,
        })
    feasible = all(row["output_feasible"] for row in rows)
    target_time = 0 if retained_capacity == initial_availability == 1 else (
        delay + ramp if ramp > 0 else (0 if delay == 0 else delay + 1)
    )
    reached = restore and rows[-1]["capability_end"] == rows[-1]["human_availability_end"] == 1
    return {
        "quarters": rows,
        "summary": {
            "path": "restoration" if restore else "continuation",
            "horizon": horizon, "total_output": volume * horizon,
            "price_multiplier": price_multiplier, "annual_discount_rate": annual_discount_rate,
            "fixed_cost": fixed_total, "provider_spend_baseline": spend_total,
            "planned_total_cost": cumulative, "total_cost": cumulative if feasible else None,
            "output_feasible": feasible,
            "oversight_status": "unverified" if review_hours_available is None else "supplied_budget",
            "capability_end": rows[-1]["capability_end"],
            "availability_end": rows[-1]["human_availability_end"],
            "target_attained": bool(reached),
            "target_time_quarters": target_time if restore else None,
            "restoration_paid": paid_restoration,
            "restoration_planned": total_restoration_cost,
        },
    }


def compare_paths(continuation, restoration, price_range=None):
    """Roots are available for feasible partial paths; target attainment is separate."""
    left, right = continuation["summary"], restoration["summary"]
    if left["horizon"] != right["horizon"] or left["total_output"] != right["total_output"]:
        raise ValueError("Paths must have the same output and horizon")
    if left["annual_discount_rate"] != right["annual_discount_rate"]:
        raise ValueError("Paths must use the same discount convention")
    if left["price_multiplier"] != right["price_multiplier"]:
        raise ValueError("Paths must be evaluated at the same price")
    if not left["output_feasible"] or not right["output_feasible"]:
        return {
            "root": None, "status": "infeasible_path", "range_status": "not_applicable",
            "restoration_target_attained": right["target_attained"],
        }
    crossing = cost_crossing(
        (left["fixed_cost"], left["provider_spend_baseline"]),
        (right["fixed_cost"], right["provider_spend_baseline"]), price_range,
    )
    return {**crossing, "restoration_target_attained": right["target_attained"]}


def path_price_exposure(path, price_multiplier):
    positive(price_multiplier, "Price multiplier")
    summary = path["summary"]
    if not summary["output_feasible"]:
        return {"absolute_exposure": None, "relative_exposure": None}
    baseline = summary["fixed_cost"] + summary["provider_spend_baseline"]
    exposure = (price_multiplier - 1) * summary["provider_spend_baseline"]
    return {
        "absolute_exposure": exposure,
        "relative_exposure": exposure / baseline if baseline > 0 else None,
    }
