"""Affine, equal-output path comparisons. Supply feasible paths only."""

import math
from fractions import Fraction

from exposure.validation import nonnegative, positive, share


def _number(value):
    # Exact comparisons on the decimal inputs also make ties at crossings reproducible.
    return value if isinstance(value, Fraction) else Fraction(str(value))


def _paths(paths):
    paths = list(paths)
    if not paths:
        raise ValueError("At least one feasible path is required")
    for fixed, spend in paths:
        nonnegative(fixed, "Fixed cost")
        nonnegative(spend, "Provider spending")
    return paths


def outside_option_threshold(incumbent_fixed, incumbent_provider_spend, alternatives):
    """First weakly competitive alternative at theta >= 1; infinity if absent."""
    nonnegative(incumbent_fixed, "Incumbent fixed cost")
    nonnegative(incumbent_provider_spend, "Incumbent provider spending")
    alternatives = list(alternatives)
    if not alternatives:
        return math.inf
    alternatives = _paths(alternatives)
    fixed, spend = map(_number, (incumbent_fixed, incumbent_provider_spend))
    threshold = math.inf
    for alt_fixed, alt_spend in alternatives:
        alt_fixed, alt_spend = map(_number, (alt_fixed, alt_spend))
        if alt_fixed + alt_spend <= fixed + spend:
            return 1.0
        if alt_spend < spend:
            crossing = (alt_fixed - fixed) / (spend - alt_spend)
            threshold = min(threshold, float(crossing))
    return threshold


def cost_crossing(incumbent, alternative, price_range=None):
    """Equality root, NOT clipped to one. Non-positive/non-unique roots stay explicit."""
    _paths([incumbent, alternative])
    fixed, spend = map(_number, incumbent)
    alt_fixed, alt_spend = map(_number, alternative)
    numerator, denominator = alt_fixed - fixed, spend - alt_spend
    if denominator == 0:
        return {
            "root": None,
            "status": "non_unique" if numerator == 0 else "no_crossing",
            "range_status": "not_applicable",
        }
    root = float(numerator / denominator)
    status = "positive_root" if root > 0 else "no_positive_root"
    range_status = "not_tested"
    if price_range is not None:
        low, high = price_range
        positive(low, "Lower price bound")
        positive(high, "Upper price bound")
        if low > high:
            raise ValueError("Price range must be ordered")
        range_status = "below_range" if root < low else (
            "above_range" if root > high else "within_range"
        )
    return {"root": root, "status": status, "range_status": range_status}


def adoption_threshold(execution_cost, human_cost, agent_other_cost=0, price_range=None):
    return cost_crossing((agent_other_cost, execution_cost), (human_cost, 0), price_range)


def path_cost(fixed_cost, provider_spend, price_multiplier):
    _paths([(fixed_cost, provider_spend)])
    positive(price_multiplier, "Price multiplier")
    return fixed_cost + price_multiplier * provider_spend


def human_path_cost(production_cost, restoration_cost):
    nonnegative(production_cost, "Human production cost")
    nonnegative(restoration_cost, "Restoration cost")
    return production_cost + restoration_cost


def restoration_cost(retained_capacity, full_restoration_cost):
    """Explicit linear scenario assumption, not an estimated capacity-cost law."""
    share(retained_capacity, "Retained capacity")
    nonnegative(full_restoration_cost, "Full restoration cost")
    return full_restoration_cost * (1 - retained_capacity)


def cheapest_path(paths, price_multiplier):
    """Ties select the FIRST listed path. A cost threshold need not mean actual switching."""
    paths = _paths(paths)
    positive(price_multiplier, "Price multiplier")
    price = _number(price_multiplier)
    return min(paths, key=lambda path: _number(path[0]) + price * _number(path[1]))
