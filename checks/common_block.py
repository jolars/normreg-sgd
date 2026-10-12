"""Check the dimension reduction against independent observation-level updates."""

import argparse
import itertools
import json
from fractions import Fraction as F
from random import Random

import numpy as np

from experiments.common_block.config import OUTPUT
from experiments.common_block.run import search
from normreg.common_block import (
    coefficients,
    fixed_rate_limit,
    risk_at,
    stability_limit,
)


def check_reduction():
    rng = Random(743)
    cases = 0
    for m, q in itertools.product(range(1, 6), (F(1, 20), F(1, 5))):
        d = m + 1
        matrix = [[F(rng.randint(-4, 4), 5) for _ in range(d)] for _ in range(d)]
        second = [
            [sum(matrix[i][k] * matrix[j][k] for k in range(d)) for j in range(d)]
            for i in range(d)
        ]
        common = sum(second[j][j] for j in range(m)) / 4
        rare = second[-1][-1]
        for standardized, alpha in itertools.product(
            (False, True), (F(0), F(2, 5), F(3))
        ):
            step = [4 * q * (1 - q) * alpha if standardized else alpha] * m + [alpha]
            enumerated = [F(0)] * d
            for cell in itertools.product((0, 1), repeat=d):
                probability = (q if cell[-1] else 1 - q) / 2**m
                x = [F(bit) - F(1, 2) for bit in cell[:-1]] + [F(cell[-1]) - q]
                for j in range(d):
                    row = [F(j == k) - step[j] * x[j] * x[k] for k in range(d)]
                    value = sum(
                        row[k] * second[k][column] * row[column]
                        for k in range(d)
                        for column in range(d)
                    )
                    enumerated[j] += probability * (value + step[j] ** 2 * x[j] ** 2)
            cc, cr, rc, rr, nc, nr = coefficients(m, q, alpha, standardized)
            assert sum(enumerated[:-1]) / 4 == cc * common + cr * rare + nc
            assert enumerated[-1] == rc * common + rr * rare + nr
            cases += 1
    return cases


def observation_reference(m, q, alpha, standardized):
    """Enumerate SGD maps before constructing the full second-moment operator."""
    d = m + 1
    cells = np.array(list(itertools.product((0, 1), repeat=d)))
    probabilities = np.where(cells[:, -1], q, 1 - q) / 2**m
    x = cells - np.r_[np.full(m, 0.5), q]
    step = np.r_[np.full(m, 4 * q * (1 - q) * alpha if standardized else alpha), alpha]
    maps = np.eye(d) - step[None, :, None] * x[:, :, None] * x[:, None, :]
    operator = np.eye(d * d + 1)
    operator[:-1, :-1] = sum(p * np.kron(a, a) for p, a in zip(probabilities, maps))
    noise = x * step
    operator[:-1, -1] = (noise.T @ (probabilities[:, None] * noise)).ravel()
    target = x.T @ ((probabilities * cells[:, -1] / q)[:, None] * x)
    return operator, target


def check_paths_and_search():
    error = 0.0
    for m, scaled in itertools.product((1, 2, 4), (False, True)):
        q, alpha = 0.02, 0.07
        operator, target = observation_reference(m, q, alpha, scaled)
        signals = [
            np.r_[1.0, np.zeros(m - 1), 0.1],
            np.r_[np.full(m, 1 / np.sqrt(m)), -0.1],
        ]
        for beta, stop in itertools.product(signals, (0, 1, 7, 83)):
            moment = (
                np.linalg.matrix_power(operator, stop)
                @ np.r_[np.outer(beta, beta).ravel(), 1]
            )
            expected = np.sum(target * moment[:-1].reshape(m + 1, m + 1)) / 2
            actual = risk_at(m, q, alpha, scaled, stop, 1, 0.01)
            error = max(error, abs(expected - actual))
            np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=1e-11)

    out = search(
        0.02,
        counts=[2],
        fractions=np.array([0, 0.01, 0.2, 0.9]),
        signals=np.array([[1, 0.01]]),
        caps=np.array([5, 17]),
    )
    for scaled, index in itertools.product(range(2), range(4)):
        operator, target = observation_reference(
            2, 0.02, out["alpha"][0, scaled, index], scaled
        )
        beta = np.array([1.0, 0.0, 0.1])
        moment = np.r_[np.outer(beta, beta).ravel(), 1]
        trajectory = []
        for _ in range(18):
            trajectory.append(np.sum(target * moment[:-1].reshape(3, 3)) / 2)
            moment = operator @ moment
        for cap_index, cap in enumerate(out["caps"]):
            expected = min(trajectory[: cap + 1])
            np.testing.assert_allclose(
                out["risk"][cap_index, 0, 0, scaled, index],
                expected,
                atol=1e-12,
                rtol=1e-11,
            )
    return error


def check_limits():
    maximum_error = 0.0
    for m, scaled in itertools.product((1, 4, 16, 64), (False, True)):
        for q in (0.02, 0.005, 0.0001):
            limit = stability_limit(m, q, scaled)
            for factor in (0.999, 1.001):
                cc, cr, rc, rr, _, _ = coefficients(m, q, factor * limit, scaled)
                radius = max(abs(np.linalg.eigvals([[cc, cr], [rc, rr]])))
                assert (radius < 1) == (factor < 1)
        alpha = 0.25 if scaled else min(0.25, 2 / m)
        for s, r in ((0.01, 1), (1, 0.01)):
            target = fixed_rate_limit(m, alpha, scaled, 2, s, r)
            errors = []
            for q in (1e-4, 1e-6):
                stop = round(2 / (q * (1 - q)))
                errors.append(abs(risk_at(m, q, alpha, scaled, stop, s, r) - target))
            assert errors[1] < errors[0]
            assert errors[1] < 2e-5, errors
            maximum_error = max(maximum_error, errors[1])
    for scaled, alpha, stop in itertools.product(
        (False, True), (0.01, 0.4, 3.0), (0, 1, 11)
    ):
        risks = [risk_at(m, 0.02, alpha, scaled, stop, 0.4, 0.7) for m in (1, 2, 4, 16)]
        assert (np.diff(risks) >= 0).all()
    return maximum_error


def check_saved():
    settings = json.loads((OUTPUT / "settings.json").read_text())
    maximum = 0.0
    with np.load(OUTPUT / "search.npz") as arrays:
        indices = arrays["risk"].argmin(axis=-1)
        for qi, ci, mi, si, scaling in np.ndindex(indices.shape):
            index = indices[qi, ci, mi, si, scaling]
            q = settings["prevalences"][qi]
            s, r = settings["signals_common_squared_norm_rare_squared"][si]
            actual = risk_at(
                settings["common_counts"][mi],
                q,
                arrays["alpha"][qi, mi, scaling, index],
                bool(scaling),
                arrays["stop"][qi, ci, mi, si, scaling, index],
                s,
                r,
            )
            expected = arrays["risk"][qi, ci, mi, si, scaling, index]
            maximum = max(maximum, abs(actual - expected))
        assert maximum < 1e-9, maximum
    print(f"Saved selected risks replayed with maximum discrepancy {maximum:.3g}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            dict(
                exact_rational_cases=check_reduction(),
                full_tensor_maximum_error=check_paths_and_search(),
                fixed_rate_limit_maximum_error_at_q_1e_6=check_limits(),
            )
        )
    )
    if args.saved:
        check_saved()


if __name__ == "__main__":
    main()
