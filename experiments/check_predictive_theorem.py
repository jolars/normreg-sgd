"""Check the direct oracle-separation proof without importing earlier checkers.

The continuous certificate uses positive exponential series and four-way
subdivision. Observation-level moment checks use a full tensor operator and
70-digit arithmetic. Neither computation is a held-out prediction test.
"""

import itertools
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache

import numpy as np

Q_MAX = F(1, 10000)
MINOR_SIGNAL = F(1, 100)


@lru_cache(maxsize=None)
def exponential_interval(x):
    """Enclose exp(-x) by reciprocating a positive series for exp(x)."""
    assert 0 <= x <= 4
    term = partial = F(1)
    for degree in range(1, 19):
        term *= x / degree
        partial += term
    tail = (term * x / 19) / (1 - x / 20)
    return 1 / (partial + tail), 1 / partial


def candidate_upper(tau):
    plateau = 1 / (tau + 3)
    exponent = 4 * tau * (tau + 3) / (tau + 4) ** 2
    _, upper = exponential_interval(exponent)
    return (plateau + (1 + MINOR_SIGNAL / 4 - plateau) * upper) / 2


def rectangle_margin(left, right, bottom, top):
    noise = left / (2 - left) + left / (8 - left)
    low_exp, _ = exponential_interval(top * right * (2 - right))
    _, high_exp = exponential_interval(bottom * left * (2 - left))
    product = min((1 - noise) * low_exp, (1 - noise) * high_exp)
    unscaled = min(F(1, 2), (noise + product) / 2)
    return unscaled - candidate_upper(bottom)


def certify_continuous_comparison():
    pending = [(F(0), F(1), F(1), F(4), 0)]
    area = F(0)
    smallest = F(1)
    leaves = deepest = 0
    while pending:
        left, right, bottom, top, depth = pending.pop()
        margin = rectangle_margin(left, right, bottom, top)
        if margin >= F(1, 100):
            area += (right - left) * (top - bottom)
            smallest = min(smallest, margin)
            leaves += 1
            deepest = max(deepest, depth)
            continue
        assert depth < 15, "The continuous separation was not certified."
        middle_x, middle_y = (left + right) / 2, (bottom + top) / 2
        pending.extend(
            (lo_x, hi_x, lo_y, hi_y, depth + 1)
            for (lo_x, hi_x), (lo_y, hi_y) in itertools.product(
                [(left, middle_x), (middle_x, right)],
                [(bottom, middle_y), (middle_y, top)],
            )
        )
    assert area == 3
    print(
        f"Separate rational certificate: {leaves} rectangles, depth {deepest}, "
        f"area {area}, gap >= {float(smallest):.9f}."
    )


def certify_transfer_constants():
    q, h = Q_MAX, F(1, 100)
    assert 3 + (1 + 3 * q) ** 2 / (2 * (1 - q * (1 + 3 * q))) < 4
    assert (5 + 16) / F(2) < 11
    scaled_error = (
        (1 + MINOR_SIGNAL / 4) * 4 * (1 + 1 / (2 * (1 - q))) + 2 / (1 - q)
    ) / 2
    assert scaled_error < 5
    assert F(1, 100) - 16 * q > F(7, 1000)

    rare_numerator = MINOR_SIGNAL + 68 * h**3 / (2 - h) + 64 * h**2
    rare_upper = rare_numerator / (1 - 64 * h**5 / (2 - h))
    common_upper = F(1, 8 * 2**200) + h / (2 * (2 - h))
    common_upper += h**3 * rare_upper / (2 * (2 - h))
    risk_upper = common_upper + rare_upper / 2
    assert risk_upper < F(11, 1000)
    lower_exp, _ = exponential_interval(2 / (1 - q / 4))
    assert lower_exp / 8 > F(1, 60)
    assert (1 - q) ** 2 / 16 >= F(3, 50)
    assert F(3, 50) - 2 * F(3, 50) ** 2 > F(1, 60)
    assert F(1, 60) - F(11, 1000) > F(1, 200)
    print(
        "Direct transfer constants certified: U lower error <= 11q, "
        f"S upper error <= 5q, common-signal U < {float(risk_upper):.9f}."
    )


def observation_operator(q, theta, scaled):
    """Average full tensor updates before reducing to diagonal moments."""
    b = q * (1 - q)
    common = b * theta if scaled else theta / 4
    step = np.diag([4 * common, theta])
    operator = np.full((5, 5), F(0), dtype=object)
    operator[4, 4] = F(1)
    for common_bit, rare_bit in itertools.product([0, 1], repeat=2):
        probability = (q if rare_bit else 1 - q) / 2
        x = np.array([F(common_bit) - F(1, 2), F(rare_bit) - q])
        update = np.eye(2, dtype=object) - step @ np.outer(x, x)
        operator[:4, :4] += probability * np.kron(update, update)
        operator[:4, 4] += probability * np.outer(step @ x, step @ x).ravel()
    return operator


def check_exact_reduction():
    cases = 0
    for q, theta, scaled in itertools.product(
        [Q_MAX, F(1, 10**6), F(1, 10**12)],
        [F(0), F(1, 10**8), F(1, 4), F(2, 5), F(1)],
        [False, True],
    ):
        b = q * (1 - q)
        u = b * theta if scaled else theta / 4
        operator = observation_operator(q, theta, scaled)
        diagonal = operator[np.ix_([0, 3], [0, 3])]
        expected = np.array(
            [
                [(1 - u) ** 2, 4 * u**2 * b],
                [b * theta**2 / 4, 1 - b * theta * (2 - theta + 3 * b * theta)],
            ],
            dtype=object,
        )
        assert np.array_equal(diagonal, expected)
        assert np.all(operator[np.ix_([0, 3], [1, 2])] == 0)
        assert np.array_equal(operator[[0, 3], 4], [4 * u**2, b * theta**2])
        assert np.all(diagonal >= 0)
        if theta:
            assert np.all(diagonal.sum(axis=1) < 1)
        if scaled:
            weights = np.array([F(1, 4), F(1)])
            contraction = 1 - b * theta * (2 - theta) + b**2 * theta**2
            assert np.all(weights @ diagonal <= contraction * weights)
            assert weights @ operator[[0, 3], 4] == b * theta**2 * (1 + b)
        cases += 1
    print(f"Checked {cases} exact tensor reductions and contraction inequalities.")


def decimal(value):
    value = F(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def risk_at(operator, stop, q, common_square, rare_square):
    converted = np.array([[decimal(entry) for entry in row] for row in operator])
    initial = np.array(
        list(map(decimal, [common_square, 0, 0, rare_square, 1])), dtype=object
    )
    # Cross moments have zero influence on either diagonal for this law.
    endpoint = np.linalg.matrix_power(converted, stop) @ initial
    return endpoint[0] / 8 + (1 - decimal(q)) ** 2 * endpoint[3] / 2


def limiting_scaled(theta, tau):
    theta, tau = decimal(theta), decimal(tau)
    plateau = theta / (2 - theta)
    exponential = (-tau * theta * (2 - theta)).exp()
    return (plateau + (1 + decimal(MINOR_SIGNAL) / 4 - plateau) * exponential) / 2


def check_finite_bounds():
    cases = 0
    tolerance = Decimal("1e-50")
    with localcontext() as context:
        context.prec = 70
        for q, target_tau in itertools.product(
            [Q_MAX, F(1, 10**5), F(1, 10**6)], [1, 2, 4]
        ):
            b = q * (1 - q)
            budget = int(target_tau / b) + (target_tau == 1)
            tau = budget * b
            assert 1 <= tau <= 4
            for theta, fraction in itertools.product(
                [F(0), F(1, 10**8), F(1, 4), F(2, 5), F(3, 4), F(1)],
                [F(0), F(1, 10**5), F(1, 2), F(1)],
            ):
                stop = int(budget * fraction)
                plain = observation_operator(q, theta, False)
                scaled = observation_operator(q, theta, True)
                noise = decimal(theta / (2 - theta) + theta / (8 - theta))
                exponential = (-decimal(tau * theta * (2 - theta))).exp()
                lower = min(Decimal("0.5"), (noise + (1 - noise) * exponential) / 2)
                for minor in [F(0), MINOR_SIGNAL]:
                    rare_signal = risk_at(plain, stop, q, minor, 1)
                    assert rare_signal + tolerance >= lower - 11 * decimal(q)
                    common_signal = risk_at(scaled, stop, q, 1, minor)
                    assert common_signal > decimal(F(1, 60))
                    cases += 2

            theta = 2 / (tau + 4)
            candidate = risk_at(
                observation_operator(q, theta, True), budget, q, MINOR_SIGNAL, 1
            )
            assert candidate <= limiting_scaled(theta, tau) + 5 * decimal(q)

            # The square-root rate is approximated to 70 digits in this diagnostic.
            h = decimal(b).sqrt()
            rational_theta = F(4 * h)
            candidate = risk_at(
                observation_operator(q, rational_theta, False),
                budget,
                q,
                1,
                MINOR_SIGNAL,
            )
            assert candidate < decimal(F(11, 1000))
            cases += 2
    print(f"Checked {cases} finite bounds using 70-digit full tensor powers.")


if __name__ == "__main__":
    certify_continuous_comparison()
    certify_transfer_constants()
    check_exact_reduction()
    check_finite_bounds()
