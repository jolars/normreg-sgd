"""Deterministic settings for the finite-prevalence comparison."""

from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from experiments.common.limiting_oracle import oracle_minimum

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/oracle-finite"
PREVALENCES = [0.04, 0.02, 0.002, 0.0002, 0.00002, 0.000002]
RESOLUTION = 1024


def cases():
    """Include the theorem anchors, transition neighborhoods, and endpoints."""
    rows = []

    def add(name, group, tau, s, r, noise=1.0):
        rows.append(dict(name=name, group=group, tau=tau, s=s, r=r, noise=noise))

    for tau in (1, 2, 4):
        add(f"rare-anchor-{tau}", "anchors", tau, 0.01, 1)
        add(f"common-anchor-{tau}", "anchors", tau, 1, 0.01)
        crossing = brentq(
            lambda s: (
                oracle_minimum(True, tau, s, 1)[0] - oracle_minimum(False, tau, s, 1)[0]
            ),
            0,
            4 * np.expm1(tau),
        )
        for factor in (0.9, 1.0, 1.1):
            add(
                f"common-crossing-{tau}-{factor:g}",
                "common-crossing",
                tau,
                factor * crossing,
                1,
            )

    theta = brentq(
        lambda r: (
            oracle_minimum(False, 2, 4 * (1 - r), r)[0]
            - oracle_minimum(True, 2, 4 * (1 - r), r)[0]
        ),
        0,
        1,
    )
    for fraction in sorted([0, 0.25, 0.5, 0.75, 1, theta - 0.02, theta, theta + 0.02]):
        add(f"allocation-{fraction:.8f}", "allocation", 2, 4 * (1 - fraction), fraction)
    for noise in (0, 0.1, 1, 100):
        add(f"noise-{noise:g}", "noise", 2, 0.1, 1, noise)
    for factor in (0.9, 1, 1.1):
        add(f"threshold-{factor:g}", "threshold", 2, 1, factor / 32)
    for tau in (0.01, 0.1, 1, 10, 100, 1000):
        add(f"budget-{tau:g}", "budget", tau, 1, 1)
    for s in (0, 1, 4):
        add(f"common-dependence-{s:g}", "common-dependence", 2, s, 1)
    for name, s, r, noise in (
        ("no-rare", 1, 0, 1),
        ("noiseless-common", 1, 0, 0),
        ("pure-noise", 0, 0, 1),
        ("zero", 0, 0, 0),
    ):
        add(name, "endpoints", 2, s, r, noise)
    return rows


def rate_grid(resolution=RESOLUTION):
    """Return nested fractions of each scaling's mean-square stability limit."""
    linear = np.linspace(0, 1 - 1e-6, resolution + 1)
    logarithmic = np.geomspace(1e-10, 1 - 1e-6, resolution + 1)
    fine = np.unique(np.r_[linear, logarithmic])
    coarse = np.isin(fine, np.r_[linear[::2], logarithmic[::2]])
    return fine, coarse


def stop_grid(caps, resolution=RESOLUTION):
    """Include early integer stops and every cap in both nested grids."""
    checkpoints = np.rint(np.geomspace(1, max(caps), resolution + 1)).astype(int)
    mandatory = np.r_[np.arange(min(64, max(caps)) + 1), caps]
    fine = np.unique(np.r_[mandatory, checkpoints])
    coarse = np.isin(fine, np.r_[mandatory, checkpoints[::2]])
    return fine, coarse
