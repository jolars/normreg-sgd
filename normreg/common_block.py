"""Exact aggregate moments for independent balanced common features."""

import numpy as np


def coefficients(common_count, q, alpha, standardized):
    """Return the affine update for weighted common MSE and rare MSE."""
    b = q * (1 - q)
    u = b * alpha if standardized else alpha / 4
    common_noise = common_count * u**2
    rare_noise = b * alpha**2
    cc = (1 - u) ** 2 + (common_count - 1) * u**2
    rr = (1 - b * alpha) ** 2 + b * alpha**2 * (1 - 4 * b)
    return cc, common_noise * b, rare_noise, rr, common_noise, rare_noise


def stability_limit(common_count, q, standardized):
    """Find the first positive root of det(I-T), using its stable formula."""
    b = q * (1 - q)
    c = b if standardized else 0.25
    linear = 2 * (1 - 3 * b + common_count * c)
    quadratic = common_count * c * (1 - 4 * b)
    return 8 / (linear + np.sqrt(linear**2 - 16 * quadratic))


def risk_at(common_count, q, alpha, standardized, stop, common_signal, rare_signal):
    """Evaluate a unit-noise endpoint without summing a long trajectory."""
    cc, cr, rc, rr, nc, nr = coefficients(common_count, q, alpha, standardized)
    operator = np.array([[cc, cr, nc], [rc, rr, nr], [0, 0, 1]])
    initial = np.array([common_signal / 4, rare_signal, 1.0])
    endpoint = np.linalg.matrix_power(operator, int(stop)) @ initial
    return float((endpoint[0] + (1 - q) ** 2 * endpoint[1]) / 2)


def fixed_rate_limit(
    common_count, alpha, standardized, time, common_signal, rare_signal
):
    """Evaluate the fixed-dimension, positive-fixed-rate, unit-noise limit.

    This formula does not exchange a prevalence limit with an oracle infimum.
    The unscaled formula applies after the initial common-coordinate transient.
    """
    upper = 2 if standardized else min(2, 8 / common_count)
    assert 0 < alpha < upper
    assert time > 0
    decay = np.exp(-alpha * (2 - alpha) * time)
    if standardized:
        initial = common_signal / 4 + rare_signal
        plateau = alpha / (2 - alpha)
        return (initial * decay + plateau * (1 - decay)) / 2
    common = common_count * alpha / (8 - common_count * alpha)
    rare_plateau = alpha * (1 + common) / (2 - alpha)
    return (common + rare_signal * decay + rare_plateau * (1 - decay)) / 2
