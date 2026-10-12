"""Excess half squared loss for independent binary features."""

import numpy as np


def risks(errors, q):
    """Return population and rare-subgroup risks on the final axis.

    Errors are broadcastable (centered offset, common coefficient error, rare
    coefficient error). Features are independent with prevalences 0.5 and q.
    The excess half squared losses exclude irreducible test response noise.
    """
    offset, common, rare = errors
    aggregate = 0.5 * (offset**2 + 0.25 * common**2 + q * (1 - q) * rare**2)
    subgroup = 0.5 * (0.25 * common**2 + (offset + (1 - q) * rare) ** 2)
    return np.stack((aggregate, subgroup), axis=-1)


def predictor_risks(coefficients, q, signals):
    """Evaluate raw predictors with final axes (signal, candidate, coefficient).

    Coefficients are (intercept, common, rare); signals has shape (n_signals, 2)
    and contains the true coefficients for population-centered features.
    """
    signals = np.asarray(signals)
    signal_shape = (1,) * (coefficients.ndim - 3) + (len(signals), 1)
    offset = coefficients[..., 0] + 0.5 * coefficients[..., 1]
    offset += q * coefficients[..., 2]
    common = coefficients[..., 1] - signals[:, 0].reshape(signal_shape)
    rare = coefficients[..., 2] - signals[:, 1].reshape(signal_shape)
    return risks((offset, common, rare), q)
