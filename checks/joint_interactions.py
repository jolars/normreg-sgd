"""Check joint-interaction moments against exhaustive sampled gradient paths.

The finite-support noise has the same first two conditional moments as the
Gaussian noise used in the experiment. No moment recurrence constructs these
reference paths. Run ordinary Python inside devenv shell.
"""

import itertools
import json

import numpy as np

from experiments.common.moments import make_model, moment_path, stability_limit


def enumerate_paths(model, scales, step, batch, signal, sigma, updates):
    x = np.repeat(model["x"], 2, axis=0)
    noise = np.tile([-sigma, sigma], 4)
    probabilities = np.repeat(model["probabilities"] / 2, 2)
    indices = np.array(list(itertools.product(range(8), repeat=batch)))
    weights = probabilities[indices].prod(axis=1)
    features = x[indices] / scales
    responses = x[indices] @ signal + noise[indices]
    theta, path_weights = np.zeros((1, 2)), np.ones(1)
    means, seconds = [], []
    for k in range(updates + 1):
        error = theta / scales - signal
        means.append(path_weights @ error)
        seconds.append(error.T @ (path_weights[:, None] * error))
        if k < updates:
            residual = np.einsum("pi,bni->pbn", theta, features) - responses
            gradient = np.einsum("pbn,bni->pbi", residual, features) / batch
            theta = (theta[:, None] - step * gradient).reshape(-1, 2)
            path_weights = (path_weights[:, None] * weights).ravel()
    return np.array(means), np.array(seconds)


def check():
    assert __debug__, "Run without -O."
    signal = np.array([0.8, -1.1])
    largest = 0.0
    cases = 0

    def close(actual, expected):
        nonlocal largest
        np.testing.assert_allclose(actual, expected, atol=2e-11, rtol=2e-10)
        largest = max(largest, float(np.max(abs(actual - expected))))

    for dependence, delta, batch, sigma in itertools.product(
        ["independent", "nested"], [0, 0.25, 0.5, 1], [1, 2], [0, 1]
    ):
        model = make_model(0.13, dependence)
        scales = np.diag(model["gram"]) ** delta
        curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]
        step = 0.08 / curvature
        expected_mean, expected_second = enumerate_paths(
            model, scales, step, batch, signal, sigma, 2
        )
        actual = moment_path(model, scales, step, batch, [0, 1, 2], signal, sigma**2)
        close(actual["bias"], expected_mean)
        close(actual["second"], expected_second)
        close(
            actual["second"],
            np.einsum("ki,kj->kij", actual["bias"], actual["bias"])
            + actual["design_covariance"]
            + actual["noise_covariance"],
        )
        noiseless_mean, noiseless_second = enumerate_paths(
            model, scales, step, batch, signal, 0, 2
        )
        close(
            actual["design_covariance"],
            noiseless_second - np.einsum("ki,kj->kij", noiseless_mean, noiseless_mean),
        )
        # A global divisor change must preserve every original-scale moment.
        rescaled = moment_path(
            model, 3.7 * scales, 3.7**2 * step, batch, [0, 1, 2], signal, sigma**2
        )
        for name in ["bias", "second", "design_covariance", "noise_covariance"]:
            close(actual[name], rescaled[name])
        close(
            0.5 * np.einsum("kij,ij->k", actual["second"], model["rare_second"]),
            0.5
            * np.einsum(
                "kij,ci,cj,c->k",
                expected_second,
                model["x"],
                model["x"],
                model["probabilities"] * model["cells"][:, 1] / model["q"],
            ),
        )
        cases += 1

    model = make_model(0.02, "independent")
    for delta in [0, 0.25, 0.5, 1]:
        scales = np.diag(model["gram"]) ** delta
        curvature = max(np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales)))
        step = 0.002 / curvature
        paths = [
            moment_path(model, scales, step, b, [1, 20, 100], signal)
            for b in [1, 10, 100]
        ]
        for left, right in zip(paths[:-1], paths[1:], strict=True):
            close(left["bias"], right["bias"])
            assert np.linalg.eigvalsh(left["second"] - right["second"]).min() > -1e-10
        for b in [1, 10, 100]:
            limit = stability_limit(model, scales, b)
            below = moment_path(model, scales, 0.99 * limit, b, [0], signal)
            above = moment_path(model, scales, 1.01 * limit, b, [0], signal)
            assert below["spectral_radius"] < 1 < above["spectral_radius"]

    # Long-horizon extraction and a truly divergent configuration exercise the
    # artifact's distinction between finite endpoints and moment stability.
    scales = np.sqrt(np.diag(model["gram"]))
    path = moment_path(model, scales, 0.002, 10, [0, 100, 10000], np.ones(2))
    close(
        path["bias"], -((1 - 0.002) ** np.array([0, 100, 10000]))[:, None] * np.ones(2)
    )
    assert np.all(path["valid"])
    divergent = moment_path(model, scales, 2.2, 1, [0, 10000], np.ones(2))
    assert divergent["spectral_radius"] > 1
    assert not divergent["valid"][-1]

    # Apply the existing manuscript operator one update at a time, independently
    # of the new augmented powers, at the long endpoints used for interpretation.
    from checks.discrete_dynamics import moment_operators

    for dependence, delta, batch in itertools.product(
        ["independent", "nested"], [0, 0.5], [1, 10]
    ):
        model = make_model(0.02, dependence)
        scales = np.diag(model["gram"]) ** delta
        curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]
        step = 0.002 / curvature
        _, r, q, _, transition, _ = moment_operators(
            model["x"], np.ones(4), model["probabilities"], scales, step, batch
        )
        mean = -scales.copy()
        second = np.outer(mean, mean)
        for _ in range(10000):
            mean = r @ mean
            second = transition(second) + step**2 / batch * q
        actual = moment_path(model, scales, step, batch, [10000], np.ones(2))
        close(actual["bias"][0], mean / scales)
        close(actual["second"][0], second / np.outer(scales, scales))

    print(json.dumps({"enumerated_cases": cases, "maximum_absolute_error": largest}))


if __name__ == "__main__":
    check()
