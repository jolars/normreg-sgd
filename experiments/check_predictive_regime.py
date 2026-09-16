"""Certify a continuous tuning comparison and check its finite-moment bounds.

The rational certificate covers rate and observation-budget intervals, rather
than treating a numerical optimizer or a grid minimum as an oracle. Floating
point moment checks are separate development checks, not held-out experiments.
"""

import itertools
from fractions import Fraction as F
from functools import lru_cache

import numpy as np
from check_predictive_claim import corrected_parts, parts, recurrence, weights
from check_predictive_feasibility import rational_operators, uniform_bound

Q_MAX = F(1, 10000)
MINOR_SIGNAL = F(1, 100)


@lru_cache(maxsize=None)
def exp_bounds(x):
    """Enclose exp(-x) by exact Taylor polynomials with signed remainders."""
    assert 0 <= x <= 4
    term = total = F(1)
    for degree in range(1, 25):
        term *= -x / degree
        total += term
    lower = total + term * (-x / 25)
    return max(F(0), lower), min(F(1), total)


def decay(theta):
    return theta * (2 - theta)


def noise_floor(theta):
    return theta / (2 - theta) + theta / (8 - theta)


def scaled_upper(tau):
    """Bound the candidate limiting risk with the largest allowed common signal."""
    theta = 2 / (tau + 4)
    _, exponential = exp_bounds(decay(theta) * tau)
    plateau = theta / (2 - theta)
    initial = 1 + MINOR_SIGNAL / 4
    return (plateau + (initial - plateau) * exponential) / 2


def plain_lower(theta_lo, theta_hi, tau_lo, tau_hi):
    """Bound the limiting lower envelope over a closed parameter rectangle."""
    plateau = noise_floor(theta_lo)
    if plateau <= 1:
        exponential, _ = exp_bounds(decay(theta_hi) * tau_hi)
    else:
        _, exponential = exp_bounds(decay(theta_lo) * tau_lo)
    return (plateau + (1 - plateau) * exponential) / 2


def certify_rate_budget_rectangle():
    """Exhaust [0, 1] x [1, 4] using rational interval subdivision."""
    pending = [(F(0), F(1), F(1), F(4), 0)]
    margin = F(1, 100)
    leaves, maximum_depth = 0, 0
    covered_area = F(0)
    smallest_bound = F(1)
    while pending:
        theta_lo, theta_hi, tau_lo, tau_hi, depth = pending.pop()
        bound = plain_lower(theta_lo, theta_hi, tau_lo, tau_hi) - scaled_upper(tau_lo)
        if bound >= margin:
            leaves += 1
            maximum_depth = max(maximum_depth, depth)
            covered_area += (theta_hi - theta_lo) * (tau_hi - tau_lo)
            smallest_bound = min(smallest_bound, bound)
            continue
        assert depth < 30, "The declared continuous margin was not certified."
        if theta_hi - theta_lo >= (tau_hi - tau_lo) / 3:
            middle = (theta_lo + theta_hi) / 2
            pending.extend(
                [
                    (theta_lo, middle, tau_lo, tau_hi, depth + 1),
                    (middle, theta_hi, tau_lo, tau_hi, depth + 1),
                ]
            )
        else:
            middle = (tau_lo + tau_hi) / 2
            pending.extend(
                [
                    (theta_lo, theta_hi, tau_lo, middle, depth + 1),
                    (theta_lo, theta_hi, middle, tau_hi, depth + 1),
                ]
            )
    assert covered_area == 3
    assert F(1, 2) - scaled_upper(F(1)) >= margin
    assert margin - 20 * Q_MAX >= F(7, 1000)
    print(
        f"Certified {leaves} rational rectangles, depth {maximum_depth}; "
        f"area {covered_area}; limiting gap >= {float(smallest_bound):.9f}."
    )


def certify_common_signal_constants():
    """Verify the numerical constants in the common-signal proof exactly."""
    q = Q_MAX
    root = F(1, 100)
    norm = 1 + MINOR_SIGNAL
    mu = F(9, 8)
    zeta = 5 * root
    # exp(-200) <= 2^-200, since e > 2.
    common = F(1, 8 * 2**200) + root / (2 * (2 - root))
    rare = (
        MINOR_SIGNAL + 4 * root**3 / (2 - root) + 64 * root**3 / (2 - root) + 64 * q
    ) / 2
    correction = mu * q * (2 * norm + 4 * zeta)
    remainder = 8 * mu * q**2 / (1 - 4 * q) * (norm + 2 * zeta)
    upper = common + rare + correction + remainder
    assert upper < F(11, 1000)
    lower_exp, _ = exp_bounds(2 / (1 - q / 4))
    assert lower_exp / 8 > F(1, 60)
    assert (1 - q) ** 2 / 16 > F(3, 50)
    assert F(3, 50) - 2 * F(3, 50) ** 2 > F(1, 60)
    assert F(1, 60) - upper > F(1, 200)
    print(
        "Certified common-signal bounds: "
        f"U < {float(upper):.9f}, S > 1/60, gap > 1/200."
    )


def certify_transfer_constants():
    """Check monotone endpoint bounds used in the finite-prevalence transfer."""
    q = Q_MAX
    norm = 1 + MINOR_SIGNAL
    mu = F(9, 8)
    zeta = F(2, 5) * (1 + q)
    assert 3 + (1 + 3 * q) ** 2 / (2 * (1 - q * (1 + 3 * q))) < 4
    assert F(5, 2) + 8 < 11
    scalar_error = (norm * 4 * (1 + 1 / (2 * (1 - q))) + 2 / (1 - q)) / 2
    correction = mu * (2 * norm + 4 * zeta)
    remainder = 8 * mu * q / (1 - 4 * q) * (norm + 2 * zeta)
    assert scalar_error < F(41, 10)
    assert correction < F(41, 10)
    assert remainder < F(1, 500)
    assert scalar_error + correction + remainder < 9
    print("Certified the 11q lower and 9q upper transfer constants.")


def limit_scaled(theta, tau, common_square, rare_square):
    exponential = np.exp(-decay(theta) * tau)
    return (
        (rare_square + common_square / 4) * exponential
        + theta / (2 - theta) * (1 - exponential)
    ) / 2


def limit_plain_lower(theta, tau):
    exponential = np.exp(-decay(theta) * tau)
    return (exponential + noise_floor(theta) * (1 - exponential)) / 2


def check_independent_operators():
    """Check the scalar reduction against actual rational random updates."""
    cases = 0
    for q, theta, scaled in itertools.product(
        [Q_MAX, F(1, 10**6)], [F(1, 1000), F(1, 4), F(1)], [False, True]
    ):
        b = q * (1 - q)
        common = b * theta if scaled else theta / 4
        exact, surrogate, injection = rational_operators(q, F(0), common, b * theta, 1)
        indices = [0, 2]
        expected = np.array(
            [
                [(1 - common) ** 2, 4 * common**2 * b],
                [b * theta**2 / 4, 1 - b * theta * (2 - theta + 3 * b * theta)],
            ],
            dtype=object,
        )
        assert np.array_equal(exact[np.ix_(indices, indices)], expected)
        assert injection[0] == 4 * common**2
        assert injection[2] == b * theta**2
        assert surrogate[0, 2] == 0
        assert np.all(expected >= 0)
        cases += 1
    print(f"Checked {cases} scalar reductions against rational observation operators.")


def check_finite_bounds():
    """Check the analytic envelopes at interior, boundary, and tiny-rate cases."""
    cases = 0
    for q, target_tau in itertools.product([1e-6, 1e-5, float(Q_MAX)], [1, 2, 4]):
        b = q * (1 - q)
        count = int(np.ceil(target_tau / b)) if target_tau == 1 else int(target_tau / b)
        tau = count * b
        for theta, fraction, signal in itertools.product(
            [1e-8, 0.01, 0.25, 0.4, 0.7, 1],
            [0, 1e-5, 0.1, 0.5, 1],
            [[0, 1], [0.1, 1], [-0.1, 1], [1, 0], [1, 0.1]],
        ):
            stop = int(count * fraction)
            for scaled in [False, True]:
                common = b * theta if scaled else theta / 4
                exact, surrogate, injection = recurrence(q, 0, common, b * theta, 1)
                value = (
                    weights(q, 0)[1] @ parts(exact, injection, signal, stop) @ [1, 1]
                )
                corrected = (
                    weights(q, 0)[1]
                    @ corrected_parts(exact, surrogate, injection, signal, stop)
                    @ [1, 1]
                )
                error = uniform_bound(q, 0, common, b * theta, 1, signal, stop)[1] @ [
                    1,
                    1,
                ]
                assert abs(value - corrected) <= error + 2e-9
                if not scaled and signal[1] == 1:
                    lower = min(0.5, limit_plain_lower(theta, tau)) - 11 * q
                    assert value >= lower - 2e-9
                if scaled and signal[0] == 1:
                    assert value >= 1 / 60 - 2e-9
                cases += 1

        theta = 2 / (tau + 4)
        exact, surrogate, injection = recurrence(q, 0, b * theta, b * theta, 1)
        risk = weights(q, 0)[1] @ parts(exact, injection, [0.1, 1], count) @ [1, 1]
        assert risk <= limit_scaled(theta, tau, 0.01, 1) + 9 * q
        root = np.sqrt(b)
        exact, _, injection = recurrence(q, 0, root, 4 * b * root, 1)
        risk = weights(q, 0)[1] @ parts(exact, injection, [1, 0.1], count) @ [1, 1]
        assert risk < 11 / 1000
        cases += 2
    print(
        f"Checked {cases} finite endpoints and candidate bounds; no artifacts written."
    )


def main():
    assert __debug__, "Run ordinary Python without -O."
    certify_rate_budget_rectangle()
    certify_transfer_constants()
    certify_common_signal_constants()
    check_independent_operators()
    check_finite_bounds()


if __name__ == "__main__":
    main()
