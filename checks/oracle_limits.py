"""Check the working oracle-limit derivation against finite SGD moments.

These are deterministic mathematical diagnostics, not simulations or certified
finite-prevalence oracle searches. See notes/oracle-limits.md for the proof.
"""

import itertools
import json
import platform
from fractions import Fraction as F

import numpy as np
import scipy
from scipy.optimize import brentq, minimize_scalar

from checks.predictive_theorem import observation_operator
from experiments.common_block.engine import coefficients


def limiting_risk(alpha, standardized, tau, s, r, noise=1.0):
    """Evaluate the continuous extension on the limiting rate interval [0, 1].

    The unscaled value at zero represents b << alpha_q << 1, not zero updates.
    """
    alpha = np.asarray(alpha)
    assert np.all((0 <= alpha) & (alpha <= 1))
    assert tau > 0 and min(s, r, noise) >= 0
    exponent = -tau * alpha * (2 - alpha)
    decay = np.exp(exponent)
    learned = -np.expm1(exponent)
    if standardized:
        return ((s / 4 + r) * decay + noise * alpha / (2 - alpha) * learned) / 2
    common = noise * alpha / (8 - alpha)
    plateau = alpha * (noise + common) / (2 - alpha)
    return (common + r * decay + plateau * learned) / 2


def limiting_minimum(standardized, tau, s, r, noise=1.0):
    """Numerically refine each grid-local minimum, retaining both endpoints."""
    rates = np.linspace(0, 1, 1025)
    values = limiting_risk(rates, standardized, tau, s, r, noise)
    candidates = [(float(values[0]), 0.0), (float(values[-1]), 1.0)]
    if np.all(values == values[0]):
        return candidates[0]
    indices = (
        np.flatnonzero((values[1:-1] <= values[:-2]) & (values[1:-1] <= values[2:])) + 1
    )
    for index in indices:
        result = minimize_scalar(
            lambda alpha: limiting_risk(alpha, standardized, tau, s, r, noise),
            bounds=(rates[index - 1], rates[index + 1]),
            method="bounded",
            options={"xatol": 1e-13},
        )
        assert result.success
        candidates.append((float(values[index]), float(rates[index])))
        candidates.append((float(result.fun), float(result.x)))
    return min(candidates)


def reference_moments(q, alpha, standardized, stop, s, r, noise=1.0):
    """Return (G, H) from the full tensor map of individual observations."""
    operator = observation_operator(F(q), F(float(alpha)), standardized)
    operator = np.array(
        [
            [np.longdouble(x.numerator) / np.longdouble(x.denominator) for x in row]
            for row in operator
        ]
    )
    initial = np.array([s, 0, 0, r, noise], dtype=np.longdouble)
    endpoint = np.linalg.matrix_power(operator, int(stop)) @ initial
    return np.array([endpoint[0] / 4, endpoint[3]], dtype=np.longdouble)


def reference_risk(q, alpha, standardized, stop, s, r, noise=1.0):
    common, rare = reference_moments(q, alpha, standardized, stop, s, r, noise)
    prevalence = np.longdouble(q.numerator) / np.longdouble(q.denominator)
    return float((common + (1 - prevalence) ** 2 * rare) / 2)


def check_scalar_bound():
    cases = 0
    for q in (F(1, 5), F(1, 50), F(1, 10000)):
        b = q * (1 - q)
        cutoff = 2 / (1 - 3 * b + b**2)
        for alpha in (F(0), F(2, 5), F(1), F(2), cutoff, 2 * cutoff, F(100)):
            operator = observation_operator(q, alpha, True)
            common_column = operator[0, 0] + 4 * operator[3, 0]
            rare_column = operator[0, 3] / 4 + operator[3, 3]
            noise = operator[0, 4] / 4 + operator[3, 4]
            lower = 1 - 2 * b * alpha + b * alpha**2 * (1 - 3 * b + b**2)
            assert lower >= 0
            assert common_column - lower == b**2 * alpha**2 * (4 - b)
            assert rare_column == lower
            assert noise == b * alpha**2 * (1 + b)
            if alpha >= cutoff:
                assert lower >= 1
            cases += 1
        for alpha in (2 / (1 - 3 * b), 4 / (1 - 3 * b), F(100)):
            operator = observation_operator(q, alpha, False)
            assert operator[3, 3] >= 1
            cases += 1
    return cases


def check_large_rate_stops():
    """Check the geometric lower bounds with exact observation-level powers."""
    cases = 0
    for q, scaled in itertools.product((F(1, 2), F(1, 50), F(1, 10000)), (False, True)):
        b = q * (1 - q)
        weight = (1 - q) ** 2
        coefficient = 1 - 3 * b + (b**2 if scaled else 0)
        cutoff = 2 / coefficient
        for alpha in (cutoff, (1 + b) * cutoff, cutoff / b):
            operator = observation_operator(q, alpha, scaled)
            multiplier = 1 - 2 * b * alpha + b * alpha**2 * coefficient
            assert multiplier >= 1
            for stop in (0, 1, 3, 7):
                power = np.linalg.matrix_power(operator, stop)
                # At stop zero, NumPy's object identity contains integers.
                risk = F(1, 8) * power[0] + (weight / 2) * power[3]
                geometric_sum = sum(multiplier**j for j in range(stop))
                lower = (
                    weight
                    / 2
                    * np.array(
                        [
                            multiplier**stop / 4 if scaled else F(0),
                            multiplier**stop,
                            b * alpha**2 * geometric_sum,
                        ],
                        dtype=object,
                    )
                )
                # Coefficient bounds cover all nonnegative signals and noise.
                assert np.all(risk[[0, 3, 4]] >= lower)
                assert np.all(risk[[1, 2]] == 0)
                cases += 1
    return cases


def check_fixed_rate_limits():
    errors_by_q = np.zeros(3)
    cases = 0
    for scaled, alpha, tau, (s, r), noise in itertools.product(
        (False, True),
        (0.1, 0.7, 1.0),
        (0.4, 2.0, 6.0),
        ((0.01, 1.0), (1.0, 0.01), (3.0, 2.0)),
        (0.0, 0.5, 2.0),
    ):
        for index, q in enumerate((F(1, 1000), F(1, 100000), F(1, 10000000))):
            b = q * (1 - q)
            stop = round(tau / b)
            target = limiting_risk(alpha, scaled, float(stop * b), s, r, noise)
            actual = reference_risk(q, alpha, scaled, stop, s, r, noise)
            errors_by_q[index] = max(errors_by_q[index], abs(actual - target))
            cases += 1
    assert (np.diff(errors_by_q) < 0).all(), errors_by_q
    assert errors_by_q[-1] < 2e-6, errors_by_q
    return {
        "cases": cases,
        "prevalences": [1e-3, 1e-5, 1e-7],
        "rates": [0.1, 0.7, 1.0],
        "target_scaled_times": [0.4, 2.0, 6.0],
        "signals_squared_common_rare": [[0.01, 1.0], [1.0, 0.01], [3.0, 2.0]],
        "noise_variances": [0.0, 0.5, 2.0],
        "maximum_errors": errors_by_q.tolist(),
    }


def check_boundary_sequences():
    s, r, noise, tau = 1.3, 0.7, 0.8, 2.0
    errors = {}
    q = F(1, 10**8)
    b = float(q * (1 - q))
    stop = round(tau / b)
    cases = [
        ("U intermediate rate", False, b**0.5, stop, r / 2, 2e-4),
        ("U slower intermediate rate", False, b**0.75, stop, r / 2, 2e-5),
        (
            "U rate proportional to b",
            False,
            b,
            stop,
            (s / 4 * np.exp(-tau / 2) + r) / 2,
            2e-7,
        ),
        ("U rate smaller than b", False, b**2, stop, (s / 4 + r) / 2, 2e-7),
        ("S vanishing rate", True, b**0.5, stop, (s / 4 + r) / 2, 3e-4),
        ("S zero rate", True, 0.0, stop, (s / 4 + r) / 2, 2e-8),
    ]
    alpha = 0.4
    common = noise * alpha / (8 - alpha)
    multiplier = (1 - alpha / 4) ** 2
    cases.extend(
        [
            (
                "U short rescaled time",
                False,
                alpha,
                round(b**-0.5),
                (common + r) / 2,
                5e-5,
            ),
            (
                "U fixed stop",
                False,
                alpha,
                3,
                (multiplier**3 * s / 4 + common * (1 - multiplier**3) + r) / 2,
                2e-8,
            ),
            ("S rate two", True, 2.0, stop, (s / 4 + r + 4 * noise * tau) / 2, 2e-6),
            (
                "U rate two",
                False,
                2.0,
                stop,
                (noise / 3 + r + 4 * (noise + noise / 3) * tau) / 2,
                2e-6,
            ),
        ]
    )
    for name, scaled, alpha, count, target, tolerance in cases:
        actual = reference_risk(q, alpha, scaled, count, s, r, noise)
        errors[name] = abs(actual - target)
        assert errors[name] < tolerance, (name, actual, target)
    for scaled, alpha, count in itertools.product(
        (False, True), (3.0, b**-0.25, b**-0.5), (1, 3)
    ):
        baseline = ((s / 4 if scaled else 0) + r) / 2
        actual = reference_risk(q, alpha, scaled, count, s, r, noise)
        assert actual >= (1 - float(q)) ** 2 * baseline - 1e-12
    return errors


def check_rate_stop_sequences():
    """Check both moments along joint rate-and-stop sequences, including zeros."""
    prevalences = [F(1, 10**power) for power in (3, 5, 7, 9)]
    signals = [(1.3, 0.7, 0.8), (1.3, 0.7, 0), (1.3, 0, 0.8), (0, 0.7, 0.8)]
    signals.extend([(0, 0, 0.8), (0, 0, 0)])
    tau = 2.0
    reports = {}
    cases = 0
    for q in prevalences:
        b = float(q * (1 - q))
        cap = int(tau / b)
        for s, r, noise in signals:
            initial = s / 4
            sequences = []

            def add(name, scaled, alpha, stop, common, rare):
                sequences.append((name, scaled, alpha, stop, [common, rare]))

            for scaled in (False, True):
                add("initialization with divergent rate", scaled, 1 / b, 0, initial, r)
                add("literal zero rate", scaled, 0.0, cap, initial, r)
                for exponent in (0.5, 0.75, 1.0, 2.0):
                    if scaled or exponent > 1:
                        target = initial
                    elif exponent == 1:
                        target = initial * np.exp(-tau / 2)
                    else:
                        target = 0.0
                    add(
                        f"rate b^{exponent}, full cap",
                        scaled,
                        b**exponent,
                        cap,
                        target,
                        r,
                    )

            for multiple in (0.25, 3.0):
                add(
                    f"rate {multiple}b, full cap",
                    False,
                    multiple * b,
                    cap,
                    initial * np.exp(-multiple * tau / 2),
                    r,
                )
            add("rate b log(1/b)", False, b * np.log(1 / b), cap, 0, r)
            add(
                "vanishing rate, k alpha to zero",
                False,
                b**0.75,
                int(b**-0.25),
                initial,
                r,
            )
            add(
                "vanishing rate, k alpha to 0.7",
                False,
                b**0.5,
                int(0.7 / b**0.5),
                initial * np.exp(-0.7 / 2),
                r,
            )
            add("vanishing rate, short recovery", False, b**0.5, int(b**-0.75), 0, r)

            a = 0.6
            g = noise * a / (8 - a)
            for stop in (1, 5):
                common = (1 - a / 4) ** (2 * stop)
                for scaled in (False, True):
                    target = initial if scaled else common * initial + (1 - common) * g
                    add(
                        f"positive rate, fixed stop {stop}",
                        scaled,
                        a + b**0.5,
                        stop,
                        target,
                        r,
                    )
            for scaled in (False, True):
                add(
                    "positive rate, diverging short stop",
                    scaled,
                    a + b**0.5,
                    int(b**-0.5),
                    initial if scaled else g,
                    r,
                )
                for fraction in (1 / 3, 1.0):
                    time = tau * fraction
                    decay = np.exp(-a * (2 - a) * time)
                    if scaled:
                        common = initial * np.exp(-2 * a * time)
                        total = (initial + r) * decay + noise * a / (2 - a) * (
                            1 - decay
                        )
                        rare = total - common
                    else:
                        common = g
                        rare = r * decay + a * (noise + g) / (2 - a) * (1 - decay)
                    add(
                        f"positive rate, cap fraction {fraction:g}",
                        scaled,
                        a + b**0.5,
                        int(time / b),
                        common,
                        rare,
                    )
                for direction in (-1, 1):
                    common = initial * np.exp(-4 * tau) if scaled else noise / 3
                    total = initial + r + 4 * noise * tau
                    rare = total - common if scaled else r + 4 * (noise + common) * tau
                    side = "below" if direction < 0 else "above"
                    add(
                        f"rate approaching two from {side}",
                        scaled,
                        2 + direction * b**0.5,
                        cap,
                        common,
                        rare,
                    )

            for name, scaled, alpha, stop, target in sequences:
                assert 0 <= stop <= cap
                actual = reference_moments(q, alpha, scaled, stop, s, r, noise)
                error = np.asarray(abs(actual - target), dtype=float)
                key = (name, scaled)
                if key not in reports:
                    reports[key] = {
                        "sequence": name,
                        "scaling": "S" if scaled else "U",
                        "rates": [],
                        "stops": [],
                        "maximum_moment_errors": [],
                    }
                report = reports[key]
                if (s, r, noise) == signals[0]:
                    report["rates"].append(float(alpha))
                    report["stops"].append(stop)
                    report["maximum_moment_errors"].append([0.0, 0.0])
                report["maximum_moment_errors"][-1] = np.maximum(
                    report["maximum_moment_errors"][-1], error
                ).tolist()
                cases += 1
    for report in reports.values():
        errors = np.max(report["maximum_moment_errors"], axis=1)
        assert np.isfinite(errors).all(), report
        assert errors[-1] < 1e-3, report
        assert np.all(errors[1:] <= 0.3 * errors[:-1] + 1e-9), report
    return {
        "cases": cases,
        "prevalences": [float(q) for q in prevalences],
        "scaled_budget": tau,
        "signals_squared_common_rare_noise_variance": signals,
        "moment_order": ["G", "H"],
        "sequences": list(reports.values()),
    }


def check_vanishing_rate_bounds():
    """Test the uniform bounds before taking a limit, using both moments."""
    cases = 0
    for q, alpha, (s, r, noise) in itertools.product(
        (F(1, 50), F(1, 10000), F(1, 10**7)),
        (0.0, 1e-5, 0.02, 0.2),
        ((1.3, 0.7, 0.8), (1.3, 0.7, 0), (1.3, 0, 0.8), (0, 0, 0.8)),
    ):
        b = float(q * (1 - q))
        cap = int(2 / b)
        time = cap * b
        g = noise * alpha / (8 - alpha)
        feedback = b * alpha / (8 - alpha)
        denominator = 1 - time * alpha**2 * feedback
        assert denominator > 0
        upper = (r + time * alpha**2 * (s / 4 + g + noise)) / denominator
        for stop in (0, 1, int(cap**0.5), cap // 2, cap):
            common, rare = reference_moments(q, alpha, False, stop, s, r, noise)
            transient = np.exp(2 * stop * np.log1p(-alpha / 4)) * s / 4
            assert (
                transient - 1e-10 <= common <= transient + g + feedback * upper + 1e-10
            )
            assert r - 2 * r * time * alpha - 1e-10 <= rare <= upper + 1e-10
            cases += 1
    return cases


def check_signal_consequences():
    cases = 0
    for tau, noise in itertools.product((0.25, 1.0, 4.0), (0.2, 1.0, 3.0)):
        threshold = noise / (16 * tau)
        for factor in (0.0, 0.5, 1.0, 1.1, 4.0):
            r = threshold * factor
            value, alpha = limiting_minimum(False, tau, 2, r, noise)
            if factor <= 1:
                np.testing.assert_allclose(value, r / 2, atol=1e-13, rtol=0)
                assert alpha == 0
            else:
                assert value < r / 2 and 0 < alpha < 1
            if r:
                scaled, _ = limiting_minimum(True, tau, 0, r, noise)
                assert scaled < value
            cases += 1
    for scaled, tau in itertools.product((False, True), (0.5, 2.0, 6.0)):
        value, alpha = limiting_minimum(scaled, tau, 1.3, 0.7, 0)
        initial = 0.7 + (1.3 / 4 if scaled else 0)
        np.testing.assert_allclose(value, initial * np.exp(-tau) / 2, atol=1e-13)
        assert alpha == 1
        cases += 1
    return cases


def finite_grid(q, tau, signals, rates):
    """Search every integer stop; this is not a continuous-rate certificate."""
    b = float(q * (1 - q))
    cap = round(tau / b)
    terms = np.array(
        [coefficients(1, float(q), rates, scaled) for scaled in (False, True)]
    )
    cc, cr, rc, rr, nc, nr = np.moveaxis(terms, 1, 0)
    shape = (len(signals), 2, len(rates))
    common = np.broadcast_to(signals[:, 0, None, None] / 4, shape).copy()
    rare = np.broadcast_to(signals[:, 1, None, None], shape).copy()
    best = (common + (1 - float(q)) ** 2 * rare) / 2
    best_stop = np.zeros(shape, dtype=int)
    for stop in range(1, cap + 1):
        common, rare = cc * common + cr * rare + nc, rc * common + rr * rare + nr
        risk = (common + (1 - float(q)) ** 2 * rare) / 2
        improved = risk < best
        best_stop[improved] = stop
        best = np.minimum(best, risk)
    assert np.isfinite(common).all() and np.isfinite(rare).all()
    indices = best.argmin(axis=-1)
    selected = np.take_along_axis(best, indices[..., None], axis=-1)[..., 0]
    stops = np.take_along_axis(best_stop, indices[..., None], axis=-1)[..., 0]
    refinement = best[..., ::2].min(axis=-1) - selected
    assert refinement.min() >= -1e-12
    assert refinement.max() < 2e-5, refinement
    for i, scaled in np.ndindex(selected.shape):
        actual = reference_risk(
            q, rates[indices[i, scaled]], bool(scaled), stops[i, scaled], *signals[i]
        )
        np.testing.assert_allclose(actual, selected[i, scaled], atol=2e-11, rtol=0)
    return {
        "q": float(q),
        "cap": cap,
        "rate_count": len(rates),
        "risk": selected.tolist(),
        "alpha": rates[indices].tolist(),
        "stop": stops.tolist(),
        "maximum_rate_refinement_change": float(refinement.max()),
    }


def check_optimized_limits():
    signals = np.array([[0.01, 1.0], [1.0, 0.01], [1.0, 1.0], [1.0, 0.0]])
    tau = 2.0
    limits = np.array(
        [
            [limiting_minimum(scaled, tau, s, r) for scaled in (False, True)]
            for s, r in signals
        ]
    )
    reports = []
    for q in (F(1, 50), F(1, 500), F(1, 5000)):
        b = float(q * (1 - q))
        rates = np.unique(
            np.r_[
                0, np.geomspace(1e-6, 3, 2049), limits[..., 1].ravel(), b**0.5, b**0.75
            ]
        )
        report = finite_grid(q, tau, signals, rates)
        error = np.max(abs(np.array(report["risk"]) - limits[..., 0]))
        report["maximum_error_from_limiting_oracle"] = float(error)
        reports.append(report)
    errors = [report["maximum_error_from_limiting_oracle"] for report in reports]
    assert (np.diff(errors) < 0).all(), errors
    assert errors[-1] < 1e-3, errors
    return {
        "noise_variance": 1,
        "scaled_budget": tau,
        "signals_squared_common_rare": signals.tolist(),
        "scalings": ["U", "S"],
        "limiting_risk": limits[..., 0].tolist(),
        "limiting_alpha": limits[..., 1].tolist(),
        "finite_grid_diagnostics": reports,
    }


def numerical_examples():
    rows = []
    for tau in (1.0, 2.0, 4.0):
        unscaled, _ = limiting_minimum(False, tau, 0, 1)
        crossing = brentq(
            lambda s: limiting_minimum(True, tau, s, 1)[0] - unscaled, 0, 10
        )

        # Check the variational crossing against the root of the optimized risks.
        def crossing_objective(alpha):
            plateau = alpha / (2 - alpha)
            return -4 * (
                (2 * unscaled - plateau) * np.exp(tau * alpha * (2 - alpha))
                + plateau
                - 1
            )

        rates = np.linspace(0, 1, 1025)
        values = crossing_objective(rates)
        index = values.argmin()
        assert 0 < index < len(rates) - 1
        optimum = minimize_scalar(
            crossing_objective,
            bounds=(rates[index - 1], rates[index + 1]),
            method="bounded",
        )
        assert optimum.success
        np.testing.assert_allclose(-optimum.fun, crossing, atol=1e-9, rtol=0)
        for s, r in ((0.01, 1.0), (1.0, 0.01)):
            rows.append(
                {
                    "tau": tau,
                    "s": s,
                    "r": r,
                    "U_risk_alpha": limiting_minimum(False, tau, s, r),
                    "S_risk_alpha": limiting_minimum(True, tau, s, r),
                }
            )
        rows.append({"tau": tau, "r": 1, "crossing_s": crossing})
    return rows


def main():
    print(
        json.dumps(
            {
                "purpose": (
                    "Diagnostics of notes/oracle-limits.md; not finite-q certificates."
                ),
                "environment": {
                    "python": platform.python_version(),
                    "numpy": np.__version__,
                    "scipy": scipy.__version__,
                    "tensor_power_decimal_precision": np.finfo(np.longdouble).precision,
                },
                "exact_scalar_bound_cases": check_scalar_bound(),
                "exact_large_rate_stop_cases": check_large_rate_stops(),
                "fixed_rate_limits": check_fixed_rate_limits(),
                "boundary_sequence_errors": check_boundary_sequences(),
                "rate_stop_sequences": check_rate_stop_sequences(),
                "vanishing_rate_bound_cases": check_vanishing_rate_bounds(),
                "signal_consequence_cases": check_signal_consequences(),
                "optimized_limits": check_optimized_limits(),
                "numerical_examples_unit_noise": numerical_examples(),
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
