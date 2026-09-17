"""Reconstruct the predictive proof checks without importing project checkers.

Small batches are enumerated, the remainder is checked with exact fractions,
and a separate continuous certificate uses range reduction and ternary splits.
The review's unrestricted-rate addendum has exact algebraic checks as well.
These calculations are proof checks, not held-out prediction experiments.
"""

import itertools
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache

import numpy as np


def symmetric_map(update):
    a, b, c, d = update.ravel()
    return np.array(
        [
            [a * a, 2 * a * b, b * b],
            [a * c, a * d + b * c, b * d],
            [c * c, 2 * c * d, d * d],
        ],
        dtype=object,
    )


def cells(q, dependence):
    joint = q * (1 + dependence) / 2
    probabilities = [F(1, 2) - q + joint, q - joint, F(1, 2) - joint, joint]
    assert min(probabilities) >= 0 and sum(probabilities) == 1
    return [
        (probability, np.array([F(i) - F(1, 2), F(j) - q], dtype=object))
        for probability, (i, j) in zip(
            probabilities, itertools.product([0, 1], repeat=2), strict=True
        )
    ]


def cell_maps(q, dependence, u, v, batch, enumerate_batch=False):
    law = cells(q, dependence)
    step = np.diag([4 * u, v / (q * (1 - q))])
    identity = np.eye(2, dtype=object)
    gram_mean = sum(p * np.outer(x, x) for p, x in law)
    noise = (step @ gram_mean @ step)[[0, 0, 1], [0, 1, 1]] / batch
    exact = np.zeros((3, 3), dtype=object)
    surrogate = exact.copy()
    if enumerate_batch:
        for observations in itertools.product(law, repeat=batch):
            probability = F(1)
            gram = np.zeros((2, 2), dtype=object)
            for p, x in observations:
                probability *= p
                gram += np.outer(x, x) / batch
            update = identity - step @ gram
            exact += probability * symmetric_map(update)
            update[0, 1] = F(0)
            surrogate += probability * symmetric_map(update)
    else:
        # Distinct observations contribute the product of their means.
        for probability, x in law:
            update = identity - step @ np.outer(x, x)
            exact += probability * symmetric_map(update) / batch
            update[0, 1] = F(0)
            surrogate += probability * symmetric_map(update) / batch
        update = identity - step @ gram_mean
        exact += (1 - F(1, batch)) * symmetric_map(update)
        update[0, 1] = F(0)
        surrogate += (1 - F(1, batch)) * symmetric_map(update)
    weights = np.zeros((2, 3), dtype=object)
    for probability, x in law:
        row = np.array([x[0] ** 2 / 2, x[0] * x[1], x[1] ** 2 / 2])
        weights[0] += probability * row
        if x[1] == 1 - q:
            weights[1] += probability * row / q
    return exact, surrogate, noise, weights


def displayed_maps(q, dependence, u, v, batch):
    b, c = q * (1 - q), q * dependence / 2
    common, rare = 4 * u, v / b
    second = c**2 + (b / 4 - c**2) / batch
    mixed = c * (b + (1 - 4 * b) / batch)
    base = np.array(
        [
            [(1 - u) ** 2, 0, 0],
            [-rare * (1 - u) * c, (1 - u) * (1 - v), 0],
            [
                rare**2 * second,
                -2 * rare * c + 2 * rare**2 * mixed,
                (1 - v) ** 2 + rare**2 * b * (1 - 4 * b) / batch,
            ],
        ],
        dtype=object,
    )
    feedback = np.array(
        [
            [0, -2 * common * (1 - u) * c, common**2 * second],
            [0, common * rare * second, -common * c + common * rare * mixed],
            [0, 0, 0],
        ],
        dtype=object,
    )
    return base + feedback, base


def check_batch_maps():
    count = 0
    for q, dependence, batch, ratio_end in itertools.product(
        [F(1, 16), F(1, 10000)], [F(-1), F(0), F(2, 3)], [1, 2, 3], [0, 1]
    ):
        b = q * (1 - q)
        ratio = F(1) if ratio_end else 4 * b
        u = min(F(1, 4), b * batch / ratio)
        v = u * ratio
        enumerated = cell_maps(q, dependence, u, v, batch, enumerate_batch=True)
        integrated = cell_maps(q, dependence, u, v, batch)
        for left, right in zip(enumerated, integrated, strict=True):
            assert np.array_equal(left, right)
        for left, right in zip(
            enumerated[:2], displayed_maps(q, dependence, u, v, batch), strict=True
        ):
            assert np.array_equal(left, right)
        expected_weights = np.array(
            [
                [F(1, 8), q * dependence / 2, b / 2],
                [F(1, 8), dependence * (1 - q) / 2, (1 - q) ** 2 / 2],
            ],
            dtype=object,
        )
        assert np.array_equal(enumerated[3], expected_weights)
        count += 1
    print(f"Review: {count} exact batch enumerations, moment maps, and risk weights.")


def check_comparison_vectors():
    p = np.array([F(1), F(1, 2), F(1)])
    h = np.array([F(1), F(1), F(2)])
    n = np.array([F(1), F(1, 2), F(2)])
    identity = np.eye(3, dtype=object)
    count = negative = 0
    for q, dependence, batch, mix, fraction in itertools.product(
        [F(1, 16), F(1, 10000), F(1, 10**12)],
        [F(-1), F(-2, 5), F(0), F(1)],
        [1, 3, 17, 10**8],
        [F(0), F(1, 2), F(1)],
        [F(1, 10**8), F(1, 3), F(1)],
    ):
        b = q * (1 - q)
        ratio = 4 * b + mix * (1 - 4 * b)
        u = fraction * min(F(1, 4), b * batch / ratio)
        v = u * ratio
        theta, decay = v / (b * batch), 1 - v / 4
        exact, base, noise, _ = cell_maps(q, dependence, u, v, batch)
        Q, J = abs(base), abs(exact - base)
        slack = decay * identity - Q
        assert np.array_equal(abs(exact), Q + J)
        assert np.all(slack @ p >= [3 * u / 2, 41 * u / 120, 41 * v / 900])
        assert np.all(slack @ h >= [3 * u / 2, u, 371 * v / 900])
        assert np.all(J @ p <= 2 * q * (slack @ h))
        assert np.all(J @ h <= 4 * q * (slack @ h))
        assert np.all((slack - J) @ h > 0)
        assert np.all((identity - Q) @ n >= [7 * u / 4, 7 * u / 15, 941 * v / 900])
        assert np.all(abs(noise) <= (u / batch + theta) * ((identity - Q) @ n))
        negative += 1 - v - theta * (1 - 4 * b) < 0
        count += 1
    assert negative
    print(
        f"Review: {count} rational vector checks, "
        f"including {negative} negative-chi cases."
    )


def check_exact_remainders():
    count = 0
    h = np.array([F(1), F(1), F(2)])
    for q, dependence, batch, scaled, signal, sigma2 in itertools.product(
        [F(1, 16), F(1, 1000)],
        [F(-1), F(0), F(1)],
        [1, 3],
        [False, True],
        [(1, 0), (0, 1), (1, -2)],
        [F(0), F(1)],
    ):
        b = q * (1 - q)
        ratio = F(1) if scaled else 4 * b
        u = min(F(1, 4), b * batch / ratio)
        v, decay = u * ratio, 1 - u * ratio / 4
        exact, base, noise, weights = cell_maps(q, dependence, u, v, batch)
        feedback = exact - base
        state = np.array(
            [F(signal[0] ** 2), F(signal[0] * signal[1]), F(signal[1] ** 2)]
        )
        leading, majorant = state.copy(), abs(state)
        correction = np.full(3, F(0))
        first = correction.copy()
        remainder = correction.copy()
        norm = sum(entry**2 for entry in signal)
        for stop in range(9):
            residual = state - leading - correction
            bound = abs(weights) @ remainder
            envelope = 8 * q**2 * (abs(weights) @ h) / (1 - 4 * q)
            envelope *= norm * decay**stop + 2 * sigma2 * (u / batch + v / (b * batch))
            assert np.all(abs(residual) <= remainder)
            assert np.all(abs(weights @ residual) <= bound)
            assert np.all(bound <= envelope)
            state, leading, correction, majorant, first, remainder = (
                exact @ state + sigma2 * noise,
                base @ leading + sigma2 * noise,
                base @ correction + feedback @ leading,
                abs(base) @ majorant + sigma2 * abs(noise),
                abs(base) @ first + abs(feedback) @ majorant,
                abs(exact) @ remainder + abs(feedback) @ first,
            )
            count += 1
    print(f"Review: {count} exact finite residual and uniform-envelope checks.")


@lru_cache(maxsize=None)
def decay_interval(x):
    """Enclose exp(-x/4) by signed Taylor remainders, then take fourth powers."""
    assert 0 <= x <= 4
    argument = x / 4
    term = upper = F(1)
    for degree in range(1, 13):
        term *= -argument / degree
        upper += term
    lower = upper - argument * term / 13
    assert 0 <= lower <= upper <= 1
    return lower**4, upper**4


def candidate_upper(tau):
    plateau = 1 / (tau + 3)
    exponent = 4 * tau * (tau + 3) / (tau + 4) ** 2
    return (plateau + (F(401, 400) - plateau) * decay_interval(exponent)[1]) / 2


def certify_continuum():
    queue = [(F(0), F(1), F(1), F(4), 0)]
    area, minimum = F(0), F(1)
    leaves = deepest = 0
    while queue:
        left, right, bottom, top, depth = queue.pop()
        noise = left / (2 - left) + left / (8 - left)
        lower_decay = decay_interval(top * right * (2 - right))[0]
        upper_decay = decay_interval(bottom * left * (2 - left))[1]
        unscaled = (
            noise + min((1 - noise) * lower_decay, (1 - noise) * upper_decay)
        ) / 2
        gap = min(F(1, 2), unscaled) - candidate_upper(bottom)
        if gap >= F(1, 100):
            area += (right - left) * (top - bottom)
            minimum = min(minimum, gap)
            deepest = max(deepest, depth)
            leaves += 1
            continue
        assert depth < 24, "The independent continuous certificate did not close."
        if right - left >= (top - bottom) / 3:
            cuts = [left + (right - left) * F(j, 3) for j in range(4)]
            queue.extend(
                (a, b, bottom, top, depth + 1)
                for a, b in zip(cuts[:-1], cuts[1:], strict=True)
            )
        else:
            cuts = [bottom + (top - bottom) * F(j, 3) for j in range(4)]
            queue.extend(
                (left, right, a, b, depth + 1)
                for a, b in zip(cuts[:-1], cuts[1:], strict=True)
            )
    assert area == 3
    print(
        f"Review certificate: {leaves} ternary leaves, depth {deepest}, "
        f"area {area}, margin >= {float(minimum):.9f}."
    )


def certify_constants_and_unrestricted_rates():
    q, h = F(1, 10000), F(1, 100)
    assert 3 + (1 + 3 * q) ** 2 / (2 * (1 - q * (1 + 3 * q))) < 4
    assert (max(F(2), F(5)) + 16) / 2 < 11
    assert (F(401, 400) * 4 * (1 + 1 / (2 * (1 - q))) + 2 / (1 - q)) / 2 < 5
    assert F(1, 100) - 16 * q > F(7, 1000)
    assert decay_interval(2 / (1 - q / 4))[0] / 8 > F(1, 60)
    assert (1 - q) ** 2 / 16 >= F(3, 50)
    assert F(3, 50) - 2 * F(3, 50) ** 2 == F(33, 625)
    rare = (F(1, 100) + 68 * h**3 / (2 - h) + 64 * h**2) / (1 - 64 * h**5 / (2 - h))
    unscaled = (
        F(1, 8 * 2**200) + h / (2 * (2 - h)) + (F(1, 2) + h**3 / (2 * (2 - h))) * rare
    )
    assert unscaled < F(11, 1000)
    assert F(1, 60) - unscaled > F(1, 200)
    assert (1 - q) ** 2 / (2 * (1 + 3 * q)) > F(49, 100)
    assert candidate_upper(F(1)) + 5 * q < F(1, 3)
    assert F(49, 100) - F(1, 3) > F(7, 1000)
    assert (1 - q) ** 2 / 4 > F(1, 8)
    assert F(1, 8) - unscaled > F(1, 200)
    count = 0
    for prevalence in [q, F(1, 10**8), F(1, 10**12)]:
        b = prevalence * (1 - prevalence)
        for theta in [F(1), F(5, 4), F(2), F(4), 1 / b, 2 / b, 3 / b]:
            plain, _, noise, _ = cell_maps(prevalence, F(0), theta / 4, b * theta, 1)
            scaled, _, _, _ = cell_maps(prevalence, F(0), b * theta, b * theta, 1)
            floor = 1 / (1 + 3 * b)
            assert plain[2, 2] * floor + noise[2] - floor == 2 * b * theta * (
                theta - 1
            ) / (1 + 3 * b)
            assert scaled[2, 2] - scaled[0, 0] == b * theta**2 * (1 - 4 * b)
            if 0 < b * theta < 2:
                assert (1 - prevalence) ** 2 * theta / (2 * (2 - b * theta)) > F(1, 8)
            else:
                assert scaled[0, 0] >= 1
            count += 1
    print(
        f"Review: transfer constants and {count} "
        "unrestricted-rate algebra checks passed."
    )


def decimal(value):
    value = F(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def finite_risk(q, theta, scaled, stop, signal):
    b = q * (1 - q)
    u = b * theta if scaled else theta / 4
    exact, _, noise, _ = cell_maps(q, F(0), u, b * theta, 1)
    transition = np.full((3, 3), Decimal(0))
    transition[2, 2] = Decimal(1)
    for i, source in enumerate([0, 2]):
        for j, target in enumerate([0, 2]):
            transition[i, j] = decimal(exact[source, target])
        transition[i, 2] = decimal(noise[source])
    initial = np.array([decimal(signal[0]), decimal(signal[1]), Decimal(1)])
    result = np.linalg.matrix_power(transition, stop) @ initial
    return result[0] / 8 + (1 - decimal(q)) ** 2 * result[1] / 2


def check_long_paths():
    count = 0
    with localcontext() as context:
        context.prec = 85
        for q, target in itertools.product(
            [F(1, 10000), F(1, 10**7), F(1, 10**12)], [F(1), F(5, 2), F(4)]
        ):
            b = q * (1 - q)
            budget = target // b + (target == 1)
            tau = budget * b
            assert 1 <= tau <= 4
            scaled_candidate = finite_risk(
                q, 2 / (tau + 4), True, budget, (F(1, 100), F(1))
            )
            unscaled_candidate = finite_risk(
                q, F(4 * decimal(b).sqrt()), False, budget, (F(1), F(1, 100))
            )
            for theta, stop in itertools.product(
                [F(0), F(1, 10**6), F(1, 4), F(3, 4), F(1), F(5, 4), F(2), F(4)],
                sorted({0, 1, budget // 5, budget}),
            ):
                rare_signal = finite_risk(q, theta, False, stop, (F(0), F(1)))
                common_signal = finite_risk(q, theta, True, stop, (F(1), F(0)))
                assert rare_signal - scaled_candidate > decimal(F(7, 1000))
                assert common_signal - unscaled_candidate > decimal(F(1, 200))
                count += 2
    print(
        f"Review: {count} finite comparisons at 85 digits, including rates above one."
    )


if __name__ == "__main__":
    assert __debug__, "Run ordinary Python without -O."
    check_batch_maps()
    check_comparison_vectors()
    check_exact_remainders()
    certify_continuum()
    certify_constants_and_unrestricted_rates()
    check_long_paths()
