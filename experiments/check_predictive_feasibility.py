"""Check the uniform remainder proof without changing frozen results.

Exact rational checks construct moment maps from the four possible observations,
independently of the formulas used by the development checker. The finite checks
support the analytic proof; they do not certify a continuous parameter domain.
"""

import itertools
from fractions import Fraction as F

import numpy as np
from check_predictive_claim import compare, recurrence, remainder, weights


def rational_operators(q, dependence, common, rare, batch):
    """Integrate random update matrices before taking their second moments."""
    half = F(1, 2)
    joint = q * (1 + dependence) / 2
    probabilities = [half - q + joint, q - joint, half - joint, joint]
    divisors = np.array([4 * common, rare / (q * (1 - q))], dtype=object)
    updates, surrogates = [], []
    injection = np.zeros((2, 2), dtype=object)
    for probability, cell in zip(
        probabilities, itertools.product([0, 1], repeat=2), strict=True
    ):
        x = np.array([cell[0] - half, cell[1] - q], dtype=object)
        update = np.eye(2, dtype=object) - np.outer(divisors * x, x)
        updates.append(update)
        surrogate = update.copy()
        surrogate[0, 1] = F(0)
        surrogates.append(surrogate)
        injection += probability * np.outer(divisors * x, divisors * x) / batch

    basis = [
        np.array(matrix, dtype=object)
        for matrix in [[[1, 0], [0, 0]], [[0, 1], [1, 0]], [[0, 0], [0, 1]]]
    ]
    maps = []
    for matrices in [updates, surrogates]:
        mean = sum(
            (p * matrix for p, matrix in zip(probabilities, matrices, strict=True)),
            np.zeros((2, 2), dtype=object),
        )
        columns = []
        for element in basis:
            single = sum(
                (
                    p * (matrix @ element @ matrix.T)
                    for p, matrix in zip(probabilities, matrices, strict=True)
                ),
                np.zeros((2, 2), dtype=object),
            )
            value = (1 - F(1, batch)) * (mean @ element @ mean.T) + single / batch
            columns.append(value[[0, 0, 1], [0, 1, 1]])
        maps.append(np.column_stack(columns))
    return *maps, injection[[0, 0, 1], [0, 1, 1]]


def check_rational_inequalities():
    initial = np.array([1, F(1, 2), 1], dtype=object)
    feedback = np.array([1, 1, 2], dtype=object)
    noise = np.array([1, F(1, 2), 2], dtype=object)
    cases = 0
    negative_chi = 0
    for q, dependence, batch, interpolation, fraction in itertools.product(
        [F(1, 16), F(1, 50), F(1, 1000), F(1, 10**6), F(1, 10**12)],
        [F(-1), F(-3, 5), F(0), F(3, 5), F(1)],
        [1, 2, 5, 100, 10**6],
        [F(0), F(1, 2), F(1)],
        [F(1, 10**6), F(1, 4), F(1)],
    ):
        b = q * (1 - q)
        ratio = 4 * b + interpolation * (1 - 4 * b)
        common = fraction * min(F(1, 4), b * batch / ratio)
        rare = common * ratio
        theta = rare / (b * batch)
        zeta = common / batch + theta
        decay = 1 - rare / 4
        exact, surrogate, injection = rational_operators(
            q, dependence, common, rare, batch
        )
        assert all(
            isinstance(value, F)
            for value in itertools.chain(exact.flat, surrogate.flat, injection.flat)
        )
        Q = abs(surrogate)
        J = abs(exact - surrogate)
        slack = decay * np.eye(3, dtype=object) - Q
        assert np.array_equal(abs(exact), Q + J)
        assert np.all(slack @ initial > 0)
        assert np.all(slack @ feedback > 0)
        assert np.all(J @ initial <= 2 * q * (slack @ feedback))
        assert np.all(J @ feedback <= 4 * q * (slack @ feedback))
        assert np.all((slack - J) @ feedback > 0)
        assert np.all(zeta * ((np.eye(3, dtype=object) - Q) @ noise) >= abs(injection))
        negative_chi += 1 - rare - theta * (1 - 4 * b) < 0
        cases += 1
    assert negative_chi > 0
    print(
        f"Checked {cases} exact rational operator cases, "
        f"including {negative_chi} with negative chi."
    )


def uniform_bound(q, dependence, common, rare, batch, signal, count):
    """Return the theorem's signal and unit-noise risk bounds."""
    mu = abs(weights(q, dependence)) @ [1, 1, 2]
    zeta = common / batch + rare / (q * (1 - q) * batch)
    scale = 8 * mu * q**2 / (1 - 4 * q)
    return np.outer(
        scale,
        [np.dot(signal, signal) * np.exp(-count * rare / 4), 2 * zeta],
    )


def check_finite_remainders():
    cases = 0
    maximum_ratio = 0.0
    for q, dependence, batch, exponent, fraction, signal in itertools.product(
        [1e-5, 0.002, 0.0625],
        [-1, 0, 0.7, 1],
        [1, 5, 10000],
        [0, 0.25, 0.5],
        [0.01, 1],
        [[1, 0], [0, 1], [1, 1], [1, -1], [2, 1]],
    ):
        b = q * (1 - q)
        ratio = (4 * b) ** (1 - 2 * exponent)
        common = fraction * min(0.25, b * batch / ratio)
        rare = common * ratio
        exact, surrogate, injection = recurrence(q, dependence, common, rare, batch)
        for count in sorted(
            {0, 1, 2, int(1 / common), int(1 / rare), int(10 / rare), int(100 / rare)}
        ):
            calculated = abs(weights(q, dependence)) @ remainder(
                exact, surrogate, injection, signal, count
            )
            bound = uniform_bound(q, dependence, common, rare, batch, signal, count)
            assert np.all(calculated <= bound * (1 + 2e-8))
            maximum_ratio = max(maximum_ratio, np.max(calculated / bound))
            cases += 1
    print(
        f"Checked {cases} finite remainders; "
        f"largest bound/envelope ratio {maximum_ratio:.6f}."
    )


def check_existing_anchors():
    print("Existing anchors only; floating-point margins are not certificates.")
    print("label objective corrected_gap uniform_envelope finite_bound resolved")
    rows = [
        ("C1-early", 0, [1, 1], 3, 1000, 0.002, 0.002),
        ("C1-late", 0, [1, 1], 3, 10000, 0.002, 0.002),
        ("C1-adjusted", 0, [1, 1], 3, 10000, 0.004, 0.0003125),
        ("C2-fixed", 1, [2, 1], 4, 100, 0.01, 0.01),
    ]
    for label, dependence, signal, sigma2, count, plain, scaled in rows:
        values = compare(0.02, dependence, signal, sigma2, 1, count, plain, scaled)
        bound = sum(
            uniform_bound(0.02, dependence, common, rare, 1, signal, count)
            @ [1, sigma2]
            for common, rare in [(plain, 4 * 0.02 * 0.98 * plain), (scaled, scaled)]
        )
        for index, objective in enumerate(["aggregate", "rare"]):
            resolved = abs(values[2][index]) > bound[index]
            if label in ["C1-early", "C1-late"] and objective == "rare":
                assert resolved
            print(
                label,
                objective,
                f"{values[2][index]:.9g}",
                f"{bound[index]:.9g}",
                f"{values[3][index]:.9g}",
                bool(resolved),
            )


def main():
    assert __debug__, "Run ordinary Python without -O."
    check_rational_inequalities()
    check_finite_remainders()
    check_existing_anchors()


if __name__ == "__main__":
    main()
