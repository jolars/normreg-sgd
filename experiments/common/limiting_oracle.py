"""Solve the scalar oracle problems in notes/oracle-variational.md.

These floating-point roots describe the small-prevalence limit, not certified
finite-prevalence risks. S denotes population standardization and U no scaling.
"""

import numpy as np
from scipy.optimize import brentq


def oracle_minimum(standardized, tau, s, r, noise=1.0):
    """Return (risk, rare-coordinate rate) using the unique stationary root.

    Under U, rate zero represents a vanishing-rate sequence that learns the
    common coordinate. It does not represent literal zero-rate training.
    """
    if not np.isfinite([tau, s, r, noise]).all():
        raise ValueError("Budget, squared signals, and noise variance must be finite.")
    if tau <= 0 or min(s, r, noise) < 0:
        raise ValueError(
            "Budget must be positive; squared signals and noise nonnegative."
        )
    initial = s / 4 + r if standardized else r
    if initial == 0:
        return 0.0, 0.0
    if noise == 0:
        return initial * np.exp(-tau) / 2, 1.0
    if not standardized and r <= noise / (16 * tau):
        return r / 2, 0.0

    def terms(alpha):
        exponent = -tau * alpha * (2 - alpha)
        decay, learned = np.exp(exponent), -np.expm1(exponent)
        p = noise * alpha / (2 - alpha)
        dp = 2 * noise / (2 - alpha) ** 2
        if standardized:
            return decay, learned, 0.0, 0.0, p, dp
        h = alpha / (8 - alpha)
        dh = 8 / (8 - alpha) ** 2
        return (
            decay,
            learned,
            noise * h,
            noise * dh,
            p * (1 + h),
            (dp * (1 + h) + p * dh),
        )

    def derivative(alpha):
        decay, learned, _, dg, plateau, dp = terms(alpha)
        # Multiplication by decay avoids the exponential growth in the inverse
        # stationary equation when the rescaled budget is large.
        return dg + dp * learned - 2 * tau * (1 - alpha) * (initial - plateau) * decay

    alpha = brentq(derivative, 0.0, 1.0, xtol=1e-14)
    decay, learned, common, _, plateau, _ = terms(alpha)
    return float((common + initial * decay + plateau * learned) / 2), float(alpha)
