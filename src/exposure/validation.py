"""Small shared input checks; no scientific-computing dependency."""

import math


def nonnegative(value, name):
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def positive(value, name):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def share(value, name):
    nonnegative(value, name)
    if value > 1:
        raise ValueError(f"{name} must be between zero and one")
    return value


def quarters(value, name, allow_zero=False):
    nonnegative(value, name)
    if isinstance(value, bool) or int(value) != value or (not allow_zero and value == 0):
        raise ValueError(f"{name} must be an integer {'>= 0' if allow_zero else '> 0'}")
    return int(value)
