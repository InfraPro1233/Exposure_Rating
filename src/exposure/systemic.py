"""Conditional common-AI-price exposure floor under shared human capacity.

No workforce allocation is optimized. Spending floors, equivalent productive
hours and available shared capacity must be supplied and independently justified.
"""

from exposure.validation import nonnegative, positive


def shared_capacity_floor(sectors, available_human_hours):
    """One-quarter lower bound; sector workloads remain separate units."""
    sectors = list(sectors)
    if not sectors:
        raise ValueError("At least one sector workload is required")
    available = nonnegative(available_human_hours, "Shared productive human hours")
    names = set()
    hours, spending, ratios = [], [], []
    for sector in sectors:
        name = sector["name"]
        if not name or name in names:
            raise ValueError("Sector names must be nonempty and unique")
        names.add(name)
        effort = positive(sector["human_hours_for_full_workload"], "Full-workload human hours")
        floor = nonnegative(sector["ai_spending_floor_per_quarter"], "AI spending floor")
        hours.append(effort)
        spending.append(floor)
        ratios.append(nonnegative(floor / effort, "Spending per productive replacement hour"))
    total_hours = positive(sum(hours), "Total human effort")
    total_spending = nonnegative(sum(spending), "Total AI spending floor")
    low, high = min(ratios), max(ratios)
    shortfall = max(0, total_hours - available)
    spending_bound = max(0, total_spending - high * available)
    hours_bound = low * shortfall
    return {
        "required_human_hours": total_hours,
        "available_human_hours": available,
        "human_hours_shortfall": shortfall,
        "ai_spending_floor_without_humans": total_spending,
        "minimum_spending_per_replacement_hour": low,
        "maximum_spending_per_replacement_hour": high,
        "spending_based_floor": spending_bound,
        "hours_based_floor": hours_bound,
        "residual_ai_spending_floor": max(spending_bound, hours_bound),
    }


def shared_capacity_path_bound(sectors, available_hours_by_quarter, annual_discount_rate=0):
    """Sum quarter-specific floors under fixed, price-independent capacity."""
    sectors = list(sectors)
    capacities = list(available_hours_by_quarter)
    if not capacities:
        raise ValueError("At least one quarter of shared capacity is required")
    rate = nonnegative(annual_discount_rate, "Annual discount rate")
    rows = []
    for quarter, available in enumerate(capacities, 1):
        row = shared_capacity_floor(sectors, available)
        weight = (1 + rate) ** (-quarter / 4)
        rows.append({
            "quarter": quarter, "discount_weight": weight, **row,
            "discounted_residual_spending_floor": weight * row["residual_ai_spending_floor"],
        })
    total_floor = nonnegative(sum(row["discounted_residual_spending_floor"] for row in rows),
                              "Discounted horizon spending floor")
    return {
        "summary": {
            "horizon_quarters": len(rows), "annual_discount_rate": rate,
            "discounted_residual_ai_spending_floor": total_floor,
            "end_quarter_spending_floor": rows[-1]["residual_ai_spending_floor"],
            "end_quarter_human_hours_shortfall": rows[-1]["human_hours_shortfall"],
        },
        "quarters": rows,
    }


def price_change_bound(residual_spending_floor, price_before, price_after):
    """One-sided change bound for the SAME fixed feasible cost envelope.

For an increase, minimum feasible cost rises by at least delta*floor.
For a cut, its change is at most delta*floor (at least that much saving).
These are pooled common-shock costs, not a selected supplier's revenue.
"""
    floor = nonnegative(residual_spending_floor, "Residual spending floor")
    before = positive(price_before, "Initial price multiplier")
    after = positive(price_after, "Final price multiplier")
    bound = (after - before) * floor
    nonnegative(abs(bound), "Price-change bound magnitude")
    return {
        "price_before": before, "price_after": after,
        "cost_change_lower_bound": bound if after >= before else None,
        "cost_change_upper_bound": bound if after <= before else None,
        "bound_direction": "equality" if after == before else (
            "lower_bound_on_increase" if after > before else "upper_bound_on_change"
        ),
    }
