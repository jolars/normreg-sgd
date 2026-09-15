"""Independent finite-support checks for the fixed-data prediction pilot."""

import itertools
import json

import numpy as np
from check_sampling_schemes import empirical_operators
from run_rare_subgroup_pilot import (
    conditional_moments,
    make_design,
    mean_se,
    noise_cell_moments,
    prediction_risks,
    scaling_rules,
)

RTOL = 2e-10
ATOL = 2e-11


def check():
    largest_error = 0.0
    extreme = mean_se(np.array([1e307, 2e307]))
    assert np.isfinite(extreme["mcse"])
    np.testing.assert_allclose(extreme["mean"], 1.5e307, rtol=RTOL)
    np.testing.assert_allclose(extreme["mcse"], 5e306, rtol=RTOL)

    def close(actual, expected):
        nonlocal largest_error
        np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)
        largest_error = max(largest_error, float(np.max(np.abs(actual - expected))))

    for q, dependence in itertools.product(
        [0.01, 0.05], ["independent", "nested", "negative"]
    ):
        design = make_design(400, q, dependence)
        x, weights = design["centered_cells"], design["probabilities"]
        close(weights @ x, np.zeros(2))
        close(x.T @ (weights[:, None] * x), design["gram"])
        assert design["counts"].sum() == 400
        assert min(design["counts"]) >= 0
        for scales in scaling_rules(np.diag(design["gram"])).values():
            assert min(scales) > 0
            close((x / scales) @ (scales * np.array([0.7, -1.3])), x @ [0.7, -1.3])
        close(
            np.diag(
                (x / np.sqrt(np.diag(design["gram"]))).T
                @ (weights[:, None] * x / np.sqrt(np.diag(design["gram"])))
            ),
            np.ones(2),
        )
        rare_error = np.diag([0.0, 1.0])
        aggregate, rare = prediction_risks(rare_error[None], design)
        close(aggregate, np.array([q * (1 - q)]))
        close(rare, np.array([(1 - q) ** 2]))

    # Multiple observations per cell expose any lost within-cell noise variance.
    design = make_design(8, 0.25, "independent")
    x = np.repeat(design["centered_cells"], design["counts"], axis=0)
    noise = np.array([0.3, -0.8, 0.2, 1.1, -0.6, 0.4, -0.9, 0.7])
    noise_mean, noise_second = noise_cell_moments(noise[None], design["counts"])
    signal = np.array([0.7, -1.2])
    for scales, batch_size in itertools.product(
        scaling_rules(np.diag(design["gram"])).values(), [None, 1, 2]
    ):
        step = 0.025
        if batch_size is None:
            batches = np.arange(len(x))[None]
        else:
            batches = np.array(
                list(itertools.product(range(len(x)), repeat=batch_size))
            )
        beta = np.zeros((1, 2))
        for updates in range(3):
            mean, second = conditional_moments(
                design,
                scales,
                step,
                batch_size,
                updates,
                signal,
                noise_mean,
                noise_second,
            )
            error = beta - signal
            close(mean[0], error.mean(axis=0))
            close(second[0], error.T @ error / len(error))
            aggregate, rare = prediction_risks(second, design)
            test_error = error @ design["centered_cells"].T
            close(
                aggregate, np.array([np.mean(test_error**2 @ design["probabilities"])])
            )
            mask = design["cells"][:, 1] == 1
            close(
                rare,
                np.array(
                    [
                        np.mean(
                            test_error[:, mask] ** 2
                            @ (design["probabilities"][mask] / design["q"])
                        )
                    ]
                ),
            )
            if updates < 2:
                residual = np.einsum("pi,bni->pbn", beta, x[batches]) - (
                    x[batches] @ signal + noise[batches]
                )
                gradient = (
                    np.einsum("pbn,bni->pbi", residual, x[batches]) / batches.shape[1]
                )
                beta = (beta[:, None] - step * gradient / scales**2).reshape(-1, 2)

    # A reused response approaches OLS; its noise is not refreshed each update.
    scales = scaling_rules(np.diag(design["gram"]))["std"]
    mean, second = conditional_moments(
        design, scales, 0.5, None, 100, signal, noise_mean, noise_second
    )
    ols_error = np.linalg.solve(x.T @ x, x.T @ noise)
    close(mean[0], ols_error)
    close(second[0], np.outer(ols_error, ols_error))

    # Compare matrix powers at the largest pilot budget to the existing score,
    # curvature, and residual-cross-term recurrence applied one update at a time.
    design = make_design(400, 0.01, "nested")
    x = np.repeat(design["centered_cells"], design["counts"], axis=0)
    noise = np.random.default_rng(314159).normal(size=len(x))
    noise_mean, noise_second = noise_cell_moments(noise[None], design["counts"])
    for scale_name, batch_size in itertools.product(["std", "variance"], [1, 20]):
        scales = scaling_rules(np.diag(design["gram"]))[scale_name]
        curvature = np.linalg.eigvalsh(design["gram"] / np.outer(scales, scales))[-1]
        step = 0.003 / curvature
        updates = 8000 // batch_size
        mean, second = conditional_moments(
            design, scales, step, batch_size, updates, signal, noise_mean, noise_second
        )
        advance, *_ = empirical_operators(x, noise, scales, step, batch_size)
        direct_mean = -scales * signal
        direct_second = np.outer(direct_mean, direct_mean)
        for _ in range(updates):
            direct_mean, direct_second = advance(direct_mean, direct_second)
        close(mean[0], direct_mean / scales)
        close(second[0], direct_second / np.outer(scales, scales))
    print(json.dumps({"max_absolute_error": largest_error, "rtol": RTOL, "atol": ATOL}))


if __name__ == "__main__":
    check()
