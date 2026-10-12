"""Diagnose the uniform control used in the oracle-infimum proof.

Exact rational checks validate the U tracking inequalities at sampled controls.
Observation-level tensor powers independently test the uniform approximations
and recovery choices. These diagnostics do not certify continuous oracle searches.
"""

import itertools
import json
import platform
from fractions import Fraction as F

import numpy as np
import scipy
from scipy.linalg import expm

from checks.oracle_limits import limiting_minimum, reference_moments, reference_risk
from checks.predictive_theorem import observation_operator


def continuous_moments(alpha, scaled, time, s, r, noise):
    """Evaluate the limiting flows without quotients singular at rate two."""
    d = alpha * (2 - alpha)
    if scaled:
        generator = np.array([[-2 * alpha, 0, 0], [alpha**2, -d, alpha**2], [0, 0, 0]])
        return (expm(time * generator) @ [s / 4, r, noise])[:2]
    common = noise * alpha / (8 - alpha)
    generator = np.array([[-d, alpha**2], [0, 0]])
    rare = (expm(time * generator) @ [r, noise + common])[0]
    return np.array([common, rare])


def tracking_terms(b, alpha, time, common, rare, noise):
    """Keep the absorption and geometric bounds exact for rational inputs."""
    a = (1 - alpha / 4) ** 2
    h = alpha / (8 - alpha)
    g = noise * h
    denominator = 1 - time * alpha**2 * b * h
    assert denominator > 0
    upper = (rare + time * alpha**2 * (common + g + noise)) / denominator
    common_error = b * h * upper
    rare_error = b * (16 * h * abs(common - g) + time * alpha**2 * h * upper)
    return a, g, upper, common_error, rare_error


def check_exact_tracking():
    cases = 0
    for q in (F(1, 50), F(1, 1000)):
        b = q * (1 - q)
        cap = 17
        for alpha in (F(0), b**2, b, F(1, 4), F(1), F(2), 2 / (1 - 3 * b)):
            operator = observation_operator(q, alpha, False)
            d = 1 - 2 * b * alpha + b * alpha**2 * (1 - 3 * b)
            assert 0 <= d <= 1
            for stop in (0, 1, 5, cap):
                power = np.linalg.matrix_power(operator, stop)
                for signal in ((4, 0, 0), (0, 1, 0), (0, 0, 1)):
                    s, r, noise = map(F, signal)
                    a, g, upper, common_error, rare_error = tracking_terms(
                        b, alpha, cap * b, s / 4, r, noise
                    )
                    endpoint = power @ [s, 0, 0, r, noise]
                    common, rare = endpoint[0] / 4, endpoint[3]
                    transient = a**stop * (s / 4) + (1 - a**stop) * g
                    frozen = d**stop * r + b * alpha**2 * (noise + g) * sum(
                        (d**j for j in range(stop)), F(0)
                    )
                    assert 0 <= common - transient <= common_error
                    assert 0 <= rare <= upper
                    assert abs(rare - frozen) <= rare_error
                    cases += 1
    return cases


def check_uniform_approximations():
    prevalences = [F(1, 10**power) for power in (3, 5, 7)]
    budgets = (0.25, 2.0, 6.0)
    signals = ((4, 0, 0), (0, 1, 0), (0, 0, 1))
    errors = np.zeros((len(prevalences), 2))
    scaled_errors = errors.copy()
    cases = 0
    for qi, q in enumerate(prevalences):
        b = float(q * (1 - q))
        for budget, scaled in itertools.product(budgets, (False, True)):
            cap = int(budget / b)
            time = cap * b
            cutoff = 2 / (1 - 3 * b + (b**2 if scaled else 0))
            rates = [0, b**2, b, b**0.5, 2 * np.log(1 / b) / cap]
            rates.extend([0.5, 1, 1.7, 2, cutoff * (1 - b), cutoff])
            for alpha in rates:
                stops = {0, 1, cap // 2, cap}
                if alpha:
                    for boundary in (1, 2 * np.log(1 / b)):
                        count = int(boundary / alpha)
                        stops.update(
                            min(cap, max(0, k)) for k in (count - 1, count + 1)
                        )
                for stop, (s, r, noise) in itertools.product(sorted(stops), signals):
                    actual = reference_moments(q, alpha, scaled, stop, s, r, noise)
                    target = continuous_moments(alpha, scaled, stop * b, s, r, noise)
                    if not scaled:
                        _, g, upper, common_error, rare_error = tracking_terms(
                            b, alpha, time, s / 4, r, noise
                        )
                        # Forming A first loses small rates over millions of steps.
                        exponent = 2 * stop * np.log1p(-alpha / 4)
                        target[0] = np.exp(exponent) * s / 4 - np.expm1(exponent) * g
                        d = alpha * (2 - alpha)
                        forcing = alpha**2 * (noise + g)
                        flow_upper = np.exp(time * max(-d, 0)) * (r + time * forcing)
                        remainder = np.exp(b * abs(d)) / 2
                        rare_error += (
                            time
                            * b
                            * (
                                (3 * alpha**2 + d**2 * remainder) * flow_upper
                                + abs(d) * remainder * forcing
                            )
                        )
                        tolerance = 2e-9
                        assert -tolerance <= actual[0] - target[0]
                        assert actual[0] - target[0] <= common_error + tolerance, (
                            q,
                            alpha,
                            stop,
                            s,
                            r,
                            noise,
                            actual[0],
                            target[0],
                            common_error,
                        )
                        assert abs(actual[1] - target[1]) <= rare_error + tolerance
                        assert actual[1] <= upper + tolerance
                    error = float(np.max(abs(actual - target)))
                    errors[qi, int(scaled)] = max(errors[qi, int(scaled)], error)
                    scaled_errors[qi, int(scaled)] = max(
                        scaled_errors[qi, int(scaled)], error / b
                    )
                    cases += 1
    # A hundredfold reduction in prevalence should expose loss of uniformity.
    assert np.all(errors[1:] < 0.02 * errors[:-1]), errors
    return {
        "cases": cases,
        "prevalences": [float(q) for q in prevalences],
        "target_scaled_budgets": budgets,
        "signals_squared_common_rare_noise_variance": signals,
        "scalings": ["U", "S"],
        "maximum_moment_errors": errors.tolist(),
        "maximum_moment_errors_divided_by_b": scaled_errors.tolist(),
        "U_explicit_tracking_and_flow_bounds_checked": True,
    }


def check_trajectory_reduction():
    cases = 0
    signals = ((1.3, 0.7, 0.8), (1.3, 0.7, 0), (1.3, 0, 0.8), (0, 0.7, 0.8))
    signals += ((0, 0, 0.8), (0, 0, 0))
    for scaled, budget, (s, r, noise) in itertools.product(
        (False, True), (0.25, 2.0, 6.0), signals
    ):
        minimum, _ = limiting_minimum(scaled, budget, s, r, noise)
        for alpha, fraction in itertools.product(
            (0, 0.1, 0.7, 1, 1.3, 1.9, 2), (0, 0.3, 1)
        ):
            value = (
                sum(continuous_moments(alpha, scaled, budget * fraction, s, r, noise))
                / 2
            )
            assert value >= minimum - 1e-12
            if 1 < alpha < 2:
                reflected = (
                    sum(
                        continuous_moments(
                            2 - alpha, scaled, budget * fraction, s, r, noise
                        )
                    )
                    / 2
                )
                assert reflected <= value + 1e-12
            cases += 1
    return cases


def check_recovery_choices():
    prevalences = [F(1, 10**power) for power in (3, 5, 7)]
    signals = ((1.3, 0.7, 0.8), (1.3, 0.7, 0), (1.3, 0, 0.8), (0, 0.7, 0.8))
    signals += ((0, 0, 0.8), (0, 0, 0), (4, 0.001, 1))
    errors = np.zeros((len(prevalences), 2))
    reports = []
    for qi, q in enumerate(prevalences):
        b = float(q * (1 - q))
        for scaled, budget, (s, r, noise) in itertools.product(
            (False, True), (0.25, 2.0, 6.0), signals
        ):
            cap = int(budget / b)
            time = cap * b
            target, minimizer = limiting_minimum(scaled, time, s, r, noise)
            alpha = minimizer if scaled else max(minimizer, 2 * np.log(1 / b) / cap)
            assert 0 <= alpha <= 1
            actual = reference_risk(q, alpha, scaled, cap, s, r, noise)
            error = abs(actual - target)
            errors[qi, int(scaled)] = max(errors[qi, int(scaled)], error)
            reports.append(
                {
                    "q": float(q),
                    "scaling": "S" if scaled else "U",
                    "s_r_noise": [s, r, noise],
                    "cap": cap,
                    "scaled_budget": time,
                    "limiting_minimizer": minimizer,
                    "recovery_rate": alpha,
                    "risk": actual,
                    "limiting_minimum": target,
                    "absolute_error": error,
                    "error_divided_by_proved_order": error
                    / (b if scaled else b * np.log(1 / b)),
                }
            )
    assert np.all(errors[1:] < 0.03 * errors[:-1]), errors
    assert errors[-1].max() < 3e-6, errors
    return {
        "cases": len(reports),
        "prevalences": [float(q) for q in prevalences],
        "scalings": ["U", "S"],
        "maximum_risk_errors": errors.tolist(),
        "comparisons": reports,
    }


def check_zero_budget_boundary():
    reports = []
    for q in (F(1, 1000), F(1, 100000), F(1, 10000000)):
        b = float(q * (1 - q))
        weight = (1 - float(q)) ** 2
        optimum = 2 / (1 + 16 * b * weight)
        one_step = reference_risk(q, optimum, False, 1, 4, 0, 1)
        np.testing.assert_allclose(one_step, 0.5 - 1 / (4 * (1 + 16 * b * weight)))
        cap = int(b**-0.5)
        growing_cap = reference_risk(q, cap**-0.5, False, cap, 4, 0, 1)
        reports.append(
            {
                "q": float(q),
                "one_step_oracle": one_step,
                "growing_cap": cap,
                "growing_cap_scaled_budget": cap * b,
                "growing_cap_recovery_risk": growing_cap,
            }
        )
    assert abs(reports[-1]["one_step_oracle"] - 0.25) < 1e-6
    growing_risks = [row["growing_cap_recovery_risk"] for row in reports]
    assert np.all(np.diff(growing_risks) < 0)
    assert growing_risks[-1] < 0.002
    return reports


def main():
    print(
        json.dumps(
            {
                "purpose": (
                    "Diagnostics of uniform oracle-infimum control; "
                    "not finite-q certificates."
                ),
                "environment": {
                    "python": platform.python_version(),
                    "numpy": np.__version__,
                    "scipy": scipy.__version__,
                },
                "exact_U_tracking_cases": check_exact_tracking(),
                "uniform_approximations": check_uniform_approximations(),
                "trajectory_reduction_cases": check_trajectory_reduction(),
                "recovery_choices": check_recovery_choices(),
                "zero_budget_boundary": check_zero_budget_boundary(),
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
