"""Exact fresh-sample SGD moments and risk decompositions."""

import itertools

import numpy as np
from scipy.optimize import brentq


def make_model(q, dependence):
    """Center binary features with prevalences 0.5 and q, where 0 < q < 0.5.

    Dependence is either independent or nested (rare implies common presence).
    The returned gram and rare_second matrices weight population and conditional
    rare-subgroup prediction errors, respectively.
    """
    p = 0.5
    joint = {"independent": p * q, "nested": q}[dependence]
    assert 0 < q < p and max(0, p + q - 1) <= joint <= min(p, q)
    cells = np.array(list(itertools.product([0.0, 1.0], repeat=2)))
    probabilities = np.array([1 - p - q + joint, q - joint, p - joint, joint])
    x = cells - [p, q]
    gram = x.T @ (probabilities[:, None] * x)
    rare_second = x.T @ ((probabilities * cells[:, 1] / q)[:, None] * x)
    assert np.linalg.eigvalsh(gram).min() > 0
    return {
        "q": q,
        "dependence": dependence,
        "cells": cells,
        "probabilities": probabilities,
        "x": x,
        "gram": gram,
        "rare_second": rare_second,
    }


def operators(model, scales, step, batch, noise_variance):
    """Return mean and second-moment transitions and noise injection.

    Features are divided by scales. Each SGD update averages batch independent
    fresh observations with zero-mean response noise of the given variance.
    """
    z = model["x"] / scales
    h = model["gram"] / np.outer(scales, scales)
    r = np.eye(2) - step * h
    fourth = sum(
        w * np.kron(np.outer(v, v), np.outer(v, v))
        for w, v in zip(model["probabilities"], z, strict=True)
    )
    transition = np.kron(r, r) + step**2 / batch * (fourth - np.kron(h, h))
    injection = step**2 * noise_variance / batch * h
    return r, transition, injection


def stability_limit(model, scales, batch):
    """Return the positive step boundary for fresh-sample second-moment stability."""
    curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]

    def residual(step):
        _, transition, _ = operators(model, scales, step, batch, 1)
        return max(abs(np.linalg.eigvalsh(transition))) - 1

    return float(brentq(residual, 1e-6 / curvature, 2.01 / curvature, xtol=1e-14))


def moment_path(model, scales, step, batch, counts, signal, noise_variance=1.0):
    """Return coefficient error moments from zero initialization at update counts.

    Bias is the mean error, and second is its uncentered second moment, both in
    original feature coordinates. Design and response-noise covariance are
    returned separately. Signal contains the true centered-feature coefficients.
    """
    counts = np.asarray(counts, dtype=int)
    assert np.all(counts >= 0) and batch >= 1 and noise_variance >= 0
    r, transition, injection = operators(model, scales, step, batch, noise_variance)
    # An affine power evaluates the finite noise sum without inverting I-T,
    # which becomes singular at a stability boundary and at zero step size.
    augmented = np.eye(5)
    augmented[:4, :4] = transition
    augmented[:4, 4] = injection.ravel()
    u0 = -scales * signal
    initial = np.outer(u0, u0).ravel()
    divisor = np.outer(scales, scales)
    bias = np.empty((len(counts), 2))
    homogeneous = np.empty((len(counts), 2, 2))
    noise = np.empty_like(homogeneous)
    with np.errstate(over="ignore", invalid="ignore"):
        for i, count in enumerate(counts):
            power = np.linalg.matrix_power(augmented, int(count))
            bias[i] = np.linalg.matrix_power(r, int(count)) @ u0 / scales
            homogeneous[i] = (power[:4, :4] @ initial).reshape(2, 2) / divisor
            noise[i] = power[:4, 4].reshape(2, 2) / divisor
        homogeneous = (homogeneous + homogeneous.swapaxes(1, 2)) / 2
        noise = (noise + noise.swapaxes(1, 2)) / 2
        design = homogeneous - np.einsum("ki,kj->kij", bias, bias)
        second = homogeneous + noise
    finite = (
        np.isfinite(bias).all(axis=1)
        & np.isfinite(second).all(axis=(1, 2))
        & np.isfinite(design).all(axis=(1, 2))
        & np.isfinite(noise).all(axis=(1, 2))
    )
    valid = finite.copy()
    for i in np.flatnonzero(finite):
        scale = max(1.0, float(np.max(abs(second[i]))))
        valid[i] = all(
            np.linalg.eigvalsh(v / scale).min() >= -1e-8
            for v in [second[i], design[i], noise[i]]
        )
    return {
        "bias": bias,
        "second": second,
        "design_covariance": design,
        "noise_covariance": noise,
        "valid": valid,
        "spectral_radius": float(max(abs(np.linalg.eigvalsh(transition)))),
    }
