"""Certify finite-prevalence oracle gaps over continuous parameter boxes.

All accepted bounds use exact fractions and rational exponential enclosures.
Rate intervals cover every real rate in [0, 1]; analytic floors cover larger
rates. The rate partition bounds the oracle and does not restrict its search.
"""

import itertools
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache

import numpy as np

from checks.predictive_theorem import decimal, observation_operator, risk_at

RATE_BINS = 4096
MINOR_SIGNAL = F(1, 100)


@lru_cache(maxsize=8192)
def exponential_interval(x):
    """Enclose exp(-x) using a positive series after range reduction."""
    assert 0 <= x <= 16
    argument = x / 4
    term = partial = F(1)
    for degree in range(1, 19):
        term *= argument / degree
        partial += term
    tail = term * argument / (19 * (1 - argument / 20))
    return (1 / (partial + tail)) ** 4, (1 / partial) ** 4


def scaled_upper(q, tau):
    w = (1 - q) ** 2
    alpha = 2 / (tau + 4)
    plateau = alpha * (1 - q) / (2 - (1 - q) * alpha)
    exponent = tau * alpha * (2 - (1 - q) * alpha)
    return (
        plateau + (w + MINOR_SIGNAL / 4 - plateau) * exponential_interval(exponent)[1]
    ) / 2


def unscaled_upper(q_left, q_right, tau):
    """Bound the U candidate uniformly across a prevalence interval."""
    b = q_right * (1 - q_right)
    w = (1 - q_left) ** 2
    alpha = 8 * b / tau
    common_plateau = alpha / (2 - alpha / 4)
    feedback = tau * b * alpha**2 * common_plateau / 4
    assert 0 <= alpha <= 1 and 0 <= feedback < 1
    rare = (
        MINOR_SIGNAL
        + b * alpha / (2 - alpha / 4)
        + tau * alpha**2 * (1 + common_plateau / 4)
    ) / (1 - feedback)
    return (
        exponential_interval(F(4))[1] / 8
        + common_plateau / 8
        + (w / 2 + b * common_plateau / 8) * rare
    )


def rare_lower(left, right, q_right, tau):
    b = q_right * (1 - q_right)
    w = (1 - q_right) ** 2
    noise = min(w, w * left / (2 - left + 3 * b * left) + left / (8 - left))
    drift = right * (2 - right + 3 * b * right)
    decay = exponential_interval(tau * drift / (1 - b * drift))[0]
    bounded = (noise + (w - noise) * decay) / 2
    return min(bounded, w / (2 * (1 + 3 * b)))


def common_lower(left, right, q_left, q_right, tau):
    b_left = q_left * (1 - q_left)
    b_right = q_right * (1 - q_right)
    w = (1 - q_right) ** 2
    plateau = min(F(1, 8), w * left / (2 * (2 - b_left * left)))
    decay = exponential_interval(2 * tau * right / (1 - b_right * right))[0]
    bounded = plateau + (F(1, 8) - plateau) * decay
    return min(bounded, F(1, 8), w / (2 * (2 - b_left)))


def rectangle_margin(family, box):
    left, right, q_left, q_right, bottom, top = box
    if family == "rare":
        return rare_lower(left, right, q_right, top) - scaled_upper(q_left, bottom)
    assert family == "common"
    return common_lower(left, right, q_left, q_right, top) - unscaled_upper(
        q_left, q_right, bottom
    )


def certify_box(family, q_max, margin, tau_left=F(1), tau_right=F(4)):
    pending = [(F(0), F(1), F(0), q_max, tau_left, tau_right)]
    volume = F(0)
    minimum = F(1)
    leaves = visited = 0
    while pending:
        box = pending.pop()
        left, right, q_left, q_right, bottom, top = box
        gap = rectangle_margin(family, box)
        visited += 1
        if gap >= margin:
            volume += (right - left) * (q_right - q_left) * (top - bottom)
            minimum = min(minimum, gap)
            leaves += 1
            continue
        widths = [right - left, q_right - q_left, (top - bottom) / 3]
        if right - left == F(1, RATE_BINS):
            widths[0] = F(0)
        dimension = max(range(3), key=widths.__getitem__)
        assert widths[dimension] > F(1, 2**22), (family, box, float(gap))
        index = 2 * dimension
        midpoint = (box[index] + box[index + 1]) / 2
        lower, upper = list(box), list(box)
        lower[index + 1] = upper[index] = midpoint
        pending.extend([tuple(lower), tuple(upper)])
    assert volume == q_max * (tau_right - tau_left)
    print(
        f"{family}: q <= {q_max}, tau in [{tau_left}, {tau_right}], "
        f"gap >= {margin}; {leaves} leaves ({visited} boxes), "
        f"volume {volume}, smallest margin {float(minimum):.10f}.",
        flush=True,
    )


def gap_bounds(q, budget):
    """Return certified lower bounds on both normalized family gaps."""
    q = F(q)
    tau = budget * q * (1 - q)
    assert 0 < q <= F(1, 16) and 1 <= tau <= 4
    rare = common = F(1)
    for index in range(RATE_BINS):
        left, right = F(index, RATE_BINS), F(index + 1, RATE_BINS)
        rare = min(rare, rare_lower(left, right, q, tau))
        common = min(common, common_lower(left, right, q, q, tau))
    return rare - scaled_upper(q, tau), common - unscaled_upper(q, q, tau)


def check_observation_bounds():
    """Compare envelopes with full observation-level tensor powers."""
    cases = 0
    tolerance = Decimal("1e-55")
    with localcontext() as context:
        context.prec = 80
        for q, target in itertools.product(
            [F(1, 10000), F(1, 50), F(1, 25), F(1, 16)], [1, 2, 4]
        ):
            b, w = q * (1 - q), (1 - q) ** 2
            budget = int(target / b) + (target == 1)
            tau = budget * b
            assert 1 <= tau <= 4
            for alpha, scaled in itertools.product(
                [F(0), F(1, 10**8), F(1, 4), F(1), F(5, 4), F(4), 1 / b, 2 / b, 3 / b],
                [False, True],
            ):
                operator = observation_operator(q, alpha, scaled)
                assert np.all(operator[np.ix_([0, 3], [1, 2])] == 0)
                if scaled:
                    weights = np.array([F(1, 4), w])
                    contraction = 1 - b * alpha * (2 - (1 - q) * alpha)
                    diagonal = operator[np.ix_([0, 3], [0, 3])]
                    assert np.all(weights @ diagonal <= contraction * weights)
                    assert weights @ operator[[0, 3], 4] == b * alpha**2 * (1 - q)
                if alpha <= 1:
                    index = min(RATE_BINS - 1, int(alpha * RATE_BINS))
                    left, right = F(index, RATE_BINS), F(index + 1, RATE_BINS)
                    lower = (
                        common_lower(left, right, q, q, tau)
                        if scaled
                        else rare_lower(left, right, q, tau)
                    )
                else:
                    lower = F(1, 8) if scaled else w / (2 * (1 + 3 * b))
                signal = (1, 0) if scaled else (0, 1)
                for stop in sorted({0, 1, budget // 2, budget}):
                    exact = risk_at(operator, stop, q, *signal)
                    assert exact + tolerance >= decimal(lower)
                    cases += 1
            for scaled, alpha, signal, upper in [
                (True, 2 / (tau + 4), (MINOR_SIGNAL, 1), scaled_upper(q, tau)),
                (False, 8 * b / tau, (1, MINOR_SIGNAL), unscaled_upper(q, q, tau)),
            ]:
                operator = observation_operator(q, alpha, scaled)
                assert np.all(operator[np.ix_([0, 3], [0, 3])].sum(axis=1) < 1)
                exact = risk_at(operator, budget, q, *signal)
                assert exact <= decimal(upper) + tolerance
                cases += 1
    print(
        f"Checked {cases} finite-prevalence bounds with 80-digit tensor powers.",
        flush=True,
    )


def certify_point():
    rare, common = gap_bounds(F(1, 50), 102)
    assert rare > F("0.0092472") and common > F("0.0641380")
    print(
        f"q = 1/50, M = 102: rounded family gap bounds {float(rare):.9f} "
        f"(rare), {float(common):.9f} (common).",
        flush=True,
    )


if __name__ == "__main__":
    assert __debug__, "Run ordinary Python without -O."
    check_observation_bounds()
    certify_point()
    for family, q_max, margin in [
        ("rare", F(1, 50), F(7, 1000)),
        ("common", F(1, 50), F(9, 200)),
        ("rare", F(1, 20), F(1, 1000)),
        ("common", F(1, 25), F(1, 50)),
        ("rare", F(1, 10000), F(11, 1000)),
        ("common", F(1, 10000), F(11, 200)),
    ]:
        certify_box(family, q_max, margin)
