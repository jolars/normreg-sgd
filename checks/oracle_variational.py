"""Diagnose the variational comparison in notes/oracle-variational.md.

Independent objective searches and numerical derivatives check the stationary
roots. These floating-point diagnostics are not finite-prevalence certificates.
"""

import itertools
import json
import platform

import numpy as np
import scipy
from scipy.optimize import brentq, minimize_scalar

from checks.oracle_limits import limiting_minimum, limiting_risk
from experiments.common.limiting_oracle import oracle_minimum


def grid_extremum(function, maximize=False):
    """Refine every grid-local extremum, including rates close to zero."""
    sign = -1 if maximize else 1
    rates = np.unique(np.r_[0, np.geomspace(1e-12, 1, 1025), np.linspace(0, 1, 1025)])
    values = sign * function(rates)
    candidates = [float(values.min())]
    indices = (
        np.flatnonzero((values[1:-1] < values[:-2]) & (values[1:-1] < values[2:])) + 1
    )
    for index in indices:
        result = minimize_scalar(
            lambda a: sign * function(a),
            bounds=(rates[index - 1], rates[index + 1]),
            method="bounded",
            options={"xatol": 1e-15},
        )
        assert result.success
        candidates.append(float(result.fun))
    return sign * min(candidates)


def check_stationary_roots():
    budgets = [0.001, 0.25, 2, 10, 100, 10000]
    signals = [(0, 1, 0.5), (1, 0, 0.5), (1, 1, 1), (0.1, 2, 3), (4, 0.001, 100)]
    signals.extend([(0, 0, 1), (2, 3, 0), (0, 0, 0)])
    maximum_error = maximum_derivative = 0.0
    cases = 0
    for scaled, tau, (s, r, noise) in itertools.product(
        (False, True), budgets, signals
    ):
        actual, alpha = oracle_minimum(scaled, tau, s, r, noise)
        reference = grid_extremum(lambda a: limiting_risk(a, scaled, tau, s, r, noise))
        error = abs(actual - reference)
        maximum_error = max(maximum_error, error)
        np.testing.assert_allclose(actual, reference, atol=2e-12, rtol=2e-11)
        if 0 < alpha < 1:
            # Complex-step differentiation uses the separate objective formula
            # without subtracting nearly equal floating-point risks.
            derivative = limiting_risk(alpha + 1e-20j, scaled, tau, s, r, noise).imag
            derivative /= 1e-20 * max(1, s, r, noise)
            maximum_derivative = max(maximum_derivative, abs(derivative))
            assert abs(derivative) < 2e-8, (scaled, tau, s, r, noise, alpha, derivative)
        if tau <= 10 and (s, r, noise) == (1, 1, 1):
            old, _ = limiting_minimum(scaled, tau, s, r, noise)
            np.testing.assert_allclose(actual, old, atol=1e-12, rtol=0)
        for factor in (0.01, 7.0):
            value, rate = oracle_minimum(
                scaled, tau, factor * s, factor * r, factor * noise
            )
            np.testing.assert_allclose(value, factor * actual, atol=1e-12, rtol=1e-11)
            np.testing.assert_allclose(rate, alpha, atol=1e-12, rtol=1e-10)
        cases += 1

    threshold_cases = 0
    for tau, noise, factor in itertools.product(
        (0.01, 1, 100), (0.1, 1, 10), (0, 0.99, 1, 1.01, 2)
    ):
        r = noise * factor / (16 * tau)
        value, rate = oracle_minimum(False, tau, 5, r, noise)
        assert (rate == 0) == (factor <= 1)
        if factor <= 1:
            assert value == r / 2
        else:
            assert value < r / 2
        threshold_cases += 1
    return {
        "cases": cases,
        "budgets": budgets,
        "signals_squared_common_rare_noise_variance": signals,
        "maximum_independent_search_error": maximum_error,
        "maximum_normalized_stationary_derivative": maximum_derivative,
        "homogeneity_factors": [0.01, 7.0],
        "rare_learning_threshold_cases": threshold_cases,
    }


def check_boundaries():
    common_rows, allocation_rows = [], []
    for tau, r, noise in itertools.product((0.1, 1, 4, 10), (0.1, 1, 3), (0.2, 1, 5)):
        unscaled = oracle_minimum(False, tau, 0, r, noise)[0]

        def gap(s):
            return oracle_minimum(True, tau, s, r, noise)[0] - unscaled

        crossing = brentq(gap, 0, 4 * r * np.expm1(tau), xtol=1e-13)

        def threshold(a):
            plateau = noise * a / (2 - a)
            return 4 * (
                (2 * unscaled - plateau) * np.exp(tau * a * (2 - a)) + plateau - r
            )

        variational = grid_extremum(threshold, maximize=True)
        np.testing.assert_allclose(crossing, variational, atol=2e-10, rtol=2e-10)
        assert crossing > 0 and gap(0.9 * crossing) < 0 < gap(1.1 * crossing)
        low, high = 0.9 * crossing, 1.1 * crossing
        difference = gap(high) - gap(low)
        assert np.exp(-tau) * (high - low) / 8 - 1e-12 <= difference
        assert difference <= (high - low) / 8 + 1e-12
        common_rows.append(
            {
                "tau": tau,
                "r": r,
                "noise": noise,
                "crossing_s": crossing,
                "variational_error": abs(crossing - variational),
            }
        )

    for tau, total, noise in itertools.product(
        (0.1, 1, 4, 10), (0.1, 1, 3), (0.2, 1, 5)
    ):
        scaled = oracle_minimum(True, tau, 0, total, noise)[0]

        def gap(r):
            return oracle_minimum(False, tau, 4 * (total - r), r, noise)[0] - scaled

        rare = brentq(gap, 0, total, xtol=1e-13)

        def threshold(a):
            decay = np.exp(-tau * a * (2 - a))
            common = noise * a / (8 - a)
            plateau = a * (noise + common) / (2 - a)
            return (2 * scaled - common - plateau * (1 - decay)) / decay

        variational = grid_extremum(threshold, maximize=True)
        np.testing.assert_allclose(rare, variational, atol=2e-10, rtol=2e-10)
        assert 0 < rare < total
        assert gap(rare / 2) < 0 < gap((rare + total) / 2)
        allocation_rows.append(
            {
                "tau": tau,
                "total_v": total,
                "noise": noise,
                "crossing_rare_fraction": rare / total,
                "variational_error": abs(rare - variational),
            }
        )
    return {
        "common_signal_crossings": common_rows,
        "fixed_total_allocation_crossings": allocation_rows,
    }


def check_noise_and_budget():
    noise_rows = []
    for noise in (0, 0.1, 1, 100):
        u, _ = oracle_minimum(False, 2, 0.1, 1, noise)
        s, _ = oracle_minimum(True, 2, 0.1, 1, noise)
        noise_rows.append(
            {"noise_variance": noise, "U": u, "S": s, "gap_S_minus_U": s - u}
        )
    assert [np.sign(row["gap_S_minus_U"]) for row in noise_rows] == [1, -1, -1, 1]
    noise_crossings = [
        brentq(
            lambda nu: (
                oracle_minimum(True, 2, 0.1, 1, nu)[0]
                - oracle_minimum(False, 2, 0.1, 1, nu)[0]
            ),
            lo,
            hi,
        )
        for lo, hi in ((0, 0.1), (1, 100))
    ]
    budget_rows = []
    for tau in (0.001, 0.01, 0.1, 1, 10, 100, 1000):
        u, _ = oracle_minimum(False, tau, 1, 1, 1)
        s, _ = oracle_minimum(True, tau, 1, 1, 1)
        budget_rows.append({"tau": tau, "U": u, "S": s, "gap_S_minus_U": s - u})
    assert budget_rows[3]["gap_S_minus_U"] > 0 > budget_rows[4]["gap_S_minus_U"]
    for scaling in ("U", "S"):
        assert np.all(np.diff([row[scaling] for row in budget_rows]) <= 0)

    for scaled in (False, True):
        for tau, s, r in itertools.product((0.1, 2, 10), (0, 0.1, 2), (0, 0.1, 2)):
            noises = np.r_[0, np.geomspace(1e-4, 1e5, 31)]
            values = np.array(
                [oracle_minimum(scaled, tau, s, r, nu)[0] for nu in noises]
            )
            assert np.all(np.diff(values) >= -1e-12)
            slopes = np.diff(values) / np.diff(noises)
            assert np.all(np.diff(slopes) <= 1e-10)
            for nu in (0.1, 1, 10):
                u, _ = oracle_minimum(False, tau, s, r, nu)
                standard, _ = oracle_minimum(True, tau, s, r, nu)
                if s == 0 and r > 0:
                    assert standard < u
                if r == 0:
                    assert u == 0 <= standard
    high_noise = [oracle_minimum(True, 2, 0.1, 1, nu)[0] for nu in (1e3, 1e5, 1e7)]
    assert np.all(np.diff(high_noise) > 0)
    assert abs(high_noise[-1] - 1.025 / 2) < 2e-7
    return {
        "noise_example": {
            "s": 0.1,
            "r": 1,
            "tau": 2,
            "rows": noise_rows,
            "two_bracketed_noise_crossings": noise_crossings,
        },
        "budget_example": {"s": 1, "r": 1, "noise_variance": 1, "rows": budget_rows},
        "high_noise_S_risks": high_noise,
    }


def check_budget_expansions():
    small_budgets = [1e-2, 1e-3, 1e-4]
    large_budgets = [1e2, 1e3, 1e4, 1e5, 1e7, 1e9]
    rows = []
    for s, r, noise in ((0, 1, 1), (1, 1, 1), (10, 0.1, 2), (0.1, 3, 0.2)):
        v = s / 4 + r
        small_errors = []
        for tau in small_budgets:
            value, rate = oracle_minimum(True, tau, s, r, noise)
            target = v / 2 - tau * v**2 / (2 * (v + noise))
            small_errors.append(abs(value - target))
            assert abs(rate - v / (v + noise)) < tau
        assert np.all(np.array(small_errors[1:]) < 0.02 * np.array(small_errors[:-1]))
        scaled_errors, ratios = [], []
        for tau in large_budgets:
            u, _ = oracle_minimum(False, tau, s, r, noise)
            standard, _ = oracle_minimum(True, tau, s, r, noise)
            target_s = noise / (8 * tau) * (1 + np.log(4 * tau * v / noise))
            target_u = 5 * noise / (32 * tau) * (1 + np.log(16 * tau * r / (5 * noise)))
            scaled_errors.append(
                [tau * abs(standard - target_s), tau * abs(u - target_u)]
            )
            ratios.append(standard / u)
        assert np.all(np.diff(scaled_errors, axis=0) < 0)
        assert np.max(scaled_errors[-1]) < 0.001
        # The logarithmic convergence of the ratio can be slow when v/r is large.
        assert standard < u
        rows.append(
            {
                "s": s,
                "r": r,
                "noise": noise,
                "small_budget_errors": small_errors,
                "large_budget_tau_times_errors_S_U": scaled_errors,
                "risk_ratios_S_over_U": ratios,
            }
        )
    return {
        "small_budgets": small_budgets,
        "large_budgets": large_budgets,
        "rows": rows,
    }


def main():
    print(
        json.dumps(
            {
                "purpose": (
                    "Diagnostics of notes/oracle-variational.md; "
                    "not finite-q certificates."
                ),
                "environment": {
                    "python": platform.python_version(),
                    "numpy": np.__version__,
                    "scipy": scipy.__version__,
                },
                "stationary_roots": check_stationary_roots(),
                "variational_boundaries": check_boundaries(),
                "noise_and_budget": check_noise_and_budget(),
                "budget_expansions": check_budget_expansions(),
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
