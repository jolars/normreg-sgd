"""Check the joint-budget claim by direct original-scale support moments."""

import argparse
import itertools
import json
import math

import numpy as np


def check(n, dependence, q=None):
    if q is None:
        q = n**-0.5
    p = 0.5
    joint = q * dependence
    weights = np.array([1 - p - q + joint, q - joint, p - joint, joint])
    x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]]) - [p, q]
    a, b = p * (1 - p), q * (1 - q)
    assert q <= a / 64
    assert min(weights) >= 0
    aa, ab, ba, bb = (
        (x[:, :, None] * x[:, None, :] / np.array([a, b])[None, :, None])
        .reshape(4, 4)
        .T
    )
    g12, g21 = float(weights @ ab), float(weights @ ba)

    def moment(v):
        return float(weights @ v)

    r00, r01, r02 = moment(aa * aa), 2 * moment(aa * ab), moment(ab * ab)
    r10, r11, r12 = moment(aa * ba), moment(aa * bb + ab * ba), moment(ab * bb)
    r20, r21, r22 = moment(ba * ba), 2 * moment(ba * bb), moment(bb * bb)
    noise00, noise01, noise22 = 1 / a, g12 / b, 1 / b
    tau = math.ceil(16 / q)
    # The first trajectory is noiseless with beta*=(1,-1); the second starts at truth.
    d00, d01, d22 = 1.0, -1.0, 1.0
    v00 = v01 = v22 = w00 = w01 = w22 = 0.0
    m0, m1 = -1.0, 1.0
    for j in range(n):
        eta = 2 / (tau + j)
        e2 = eta * eta
        t00, t01, t02 = 1 - 2 * eta + e2 * r00, -2 * eta * g12 + e2 * r01, e2 * r02
        t10, t11, t12 = (
            -eta * g21 + e2 * r10,
            1 - 2 * eta + e2 * r11,
            -eta * g12 + e2 * r12,
        )
        t20, t21, t22 = e2 * r20, -2 * eta * g21 + e2 * r21, 1 - 2 * eta + e2 * r22
        d00, d01, d22 = (
            t00 * d00 + t01 * d01 + t02 * d22,
            t10 * d00 + t11 * d01 + t12 * d22,
            t20 * d00 + t21 * d01 + t22 * d22,
        )
        v00, v01, v22 = (
            t00 * v00 + t01 * v01 + t02 * v22 + e2 * noise00,
            t10 * v00 + t11 * v01 + t12 * v22 + e2 * noise01,
            t20 * v00 + t21 * v01 + t22 * v22 + e2 * noise22,
        )
        f00, f01, f10, f11 = 1 - eta, -eta * g12, -eta * g21, 1 - eta
        w00, w01, w22 = (
            f00 * f00 * w00 + 2 * f00 * f01 * w01 + f01 * f01 * w22 + e2 * noise00,
            f00 * f10 * w00
            + (f00 * f11 + f01 * f10) * w01
            + f01 * f11 * w22
            + e2 * noise01,
            f10 * f10 * w00 + 2 * f10 * f11 * w01 + f11 * f11 * w22 + e2 * noise22,
        )
        m0, m1 = f00 * m0 + f01 * m1, f10 * m0 + f11 * m1
    difference = np.array(
        [
            [a * (v00 - w00), math.sqrt(a * b) * (v01 - w01)],
            [math.sqrt(a * b) * (v01 - w01), b * (v22 - w22)],
        ]
    )
    assert np.linalg.eigvalsh(difference).min() > -1e-12
    assert np.trace(difference) <= 32 * n / (q * (tau + n - 3) ** 3) + 1e-12
    assert a * v00 + b * v22 <= 4 / (tau + n) + 1e-12
    factor = tau / (tau + n)
    assert m1 * m1 <= (a + b) / b * factor**3.5 + 1e-12
    assert d22 - m1 * m1 <= (a + b) / b * factor**3 + 1e-12
    return {
        "n": n,
        "q": q,
        "conditional_common_given_rare": dependence,
        "nq_bias_squared": n * q * m1 * m1,
        "nq_design_variance": n * q * (d22 - m1 * m1),
        "nq_noise_variance": n * q * v22,
        "n_noise_amplification_trace": n * float(np.trace(difference)),
        "noise_limit": 4 / 3,
        "mean": [m0, m1],
        "noiseless_second": [[d00, d01], [d01, d22]],
        "noise_second": [[v00, v01], [v01, v22]],
    }


def check_short_paths():
    """Enumerate actual observations and noise, independently of moment operators."""
    q = 1 / 256
    cells = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    variances = np.array([0.25, q * (1 - q)])
    points = cells - [0.5, q]
    largest_error = 0.0
    for dependence in [0, 0.5, 1]:
        joint = q * dependence
        probabilities = [0.5 - q + joint, q - joint, 0.5 - joint, joint]
        mean = np.zeros(2)
        design = np.zeros((2, 2))
        noise = np.zeros((2, 2))
        combined = np.zeros((2, 2))
        for path in itertools.product(range(8), repeat=3):
            bias_error = np.array([-1.0, 1.0])
            noise_error = np.zeros(2)
            probability = 1.0
            for j, outcome in enumerate(path):
                cell, sign = divmod(outcome, 2)
                x = points[cell]
                probability *= probabilities[cell] / 2
                step = 2 / (math.ceil(16 / q) + j)
                bias_error -= step * x / variances * (x @ bias_error)
                noise_error += step * x / variances * (2 * sign - 1 - x @ noise_error)
            mean += probability * bias_error
            design += probability * np.outer(bias_error, bias_error)
            noise += probability * np.outer(noise_error, noise_error)
            total = bias_error + noise_error
            combined += probability * np.outer(total, total)
        moments = check(3, dependence, q=q)
        for actual, expected in [
            (mean, moments["mean"]),
            (design, moments["noiseless_second"]),
            (noise, moments["noise_second"]),
            (combined, design + noise),
        ]:
            error = float(np.max(np.abs(actual - expected)))
            assert error < 2e-12
            largest_error = max(largest_error, error)
    return largest_error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--large", action="store_true", help="Include budgets up to 2**20."
    )
    args = parser.parse_args()
    short_error = check_short_paths()
    rows = []
    for dependence in [0, 0.5, 1]:
        powers = [16, 18, 20] if args.large else [16, 18]
        sequence = [check(2**power, dependence) for power in powers]
        assert abs(sequence[-1]["nq_noise_variance"] - 4 / 3) < abs(
            sequence[0]["nq_noise_variance"] - 4 / 3
        )
        assert sequence[-1]["nq_bias_squared"] < sequence[0]["nq_bias_squared"]
        assert sequence[-1]["nq_design_variance"] < sequence[0]["nq_design_variance"]
        rows.extend(sequence)
    print(
        json.dumps({"short_path_max_error": short_error, "rate_checks": rows}, indent=2)
    )


if __name__ == "__main__":
    main()
