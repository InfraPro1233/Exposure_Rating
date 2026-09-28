"""Conditional single-supplier pricing with fixed output and exogenous feasible paths."""

import math

from exposure.threshold import _number, _paths, cheapest_path
from exposure.validation import nonnegative, positive


def _sectors(sectors):
    sectors = [_paths(paths) for paths in sectors]
    if not sectors:
        raise ValueError("At least one sector is required")
    return sectors


def _selected_provider_spend(sectors, price_multiplier):
    positive(price_multiplier, "Price multiplier")
    return sum(cheapest_path(paths, price_multiplier)[1] for paths in _sectors(sectors))


def provider_revenue(sectors, price_multiplier):
    return price_multiplier * _selected_provider_spend(sectors, price_multiplier)


def provider_profit(sectors, price_multiplier, marginal_cost_multiplier):
    """Profit before fixed costs; marginal cost is in BASELINE price units."""
    nonnegative(marginal_cost_multiplier, "Marginal cost multiplier")
    return (price_multiplier - marginal_cost_multiplier) * _selected_provider_spend(
        sectors, price_multiplier
    )


def _breakpoints(sectors, minimum_price):
    points = {minimum_price}
    for paths in sectors:
        for index, (fixed, spend) in enumerate(paths):
            for alt_fixed, alt_spend in paths[index + 1:]:
                if spend != alt_spend:
                    point = (alt_fixed - fixed) / (spend - alt_spend)
                    if point >= minimum_price:
                        points.add(point)
    return sorted(points)


def _boundary_spend(sectors, price, side):
    spend = 0
    for paths in sectors:
        costs = [fixed + price * volume for fixed, volume in paths]
        cheapest = min(costs)
        tied = [path for path, cost in zip(paths, costs) if cost == cheapest]
        if side == "left":
            chosen = max(tied, key=lambda path: path[1])
        elif side == "right":
            chosen = min(tied, key=lambda path: path[1])
        else:
            chosen = tied[0]
        spend += chosen[1]
    return spend


def optimal_provider_price(sectors, marginal_cost_multiplier, minimum_price=1):
    """Exact finite-path maximum or supremum on theta >= minimum_price.

    All pairwise intersections partition the lower envelopes. Profit is linear
    within each interval, so boundaries and one-sided limits suffice. If demand
    persists at arbitrarily high prices, report unbounded rather than a grid maximum.
    """
    sectors = _sectors(sectors)
    nonnegative(marginal_cost_multiplier, "Marginal cost multiplier")
    positive(minimum_price, "Minimum price")
    sectors = [[tuple(map(_number, path)) for path in paths] for paths in sectors]
    floor, marginal_cost = map(_number, (minimum_price, marginal_cost_multiplier))
    residual = sum(min(spend for _, spend in paths) for paths in sectors)
    if residual > 0:
        return {
            "status": "unbounded", "price": None, "profit": math.inf,
            "price_exact": None, "profit_exact": None,
            "selected_provider_spend": None, "boundary_side": "not_applicable",
            "tie_policy": "first_listed_path",
        }
    candidates = []
    points = _breakpoints(sectors, floor)
    for index, price in enumerate(points):
        for side in ("at", "left"):
            if side == "left" and price == floor:
                continue
            spend = _boundary_spend(sectors, price, side)
            candidates.append(((price - marginal_cost) * spend, price, spend, side))
        # A flat interval (especially zero demand after the final crossing)
        # can attain its maximum even if a boundary tie selects a losing path.
        interior = (price + points[index + 1]) / 2 if index + 1 < len(points) else price + 1
        spend = _boundary_spend(sectors, interior, "at")
        candidates.append(((interior - marginal_cost) * spend, interior, spend, "at"))
    best_profit = max(item[0] for item in candidates)
    # Prefer an attained maximum, then the lowest price among equal maxima.
    best = min(
        (item for item in candidates if item[0] == best_profit),
        key=lambda item: (item[3] != "at", item[1]),
    )
    profit, price, spend, side = best
    return {
        "status": "maximum" if side == "at" else "supremum_not_attained",
        "price": float(price), "profit": float(profit),
        "price_exact": str(price), "profit_exact": str(profit),
        "selected_provider_spend": float(spend), "boundary_side": side,
        "tie_policy": "first_listed_path",
    }
