"""Check the independent-design risk candidate without rewriting frozen results.

The reduced moments use explicit Bernoulli fourth moments. Short enumerated
updates and the existing full operator provide separate computational checks.
The parameter grid supports a conjecture; it does not certify its entire box.
"""

import itertools

import numpy as np
from check_joint_interactions import enumerate_paths
from run_joint_interactions import make_model, moment_path


def diagonal_parts(q, common_step, batch, delta, count, signal):
    assert 0 < q < 0.5 and common_step > 0 and batch >= 1
    assert delta in (0, 0.5) and count >= 0
    variances = np.array([0.25, q * (1 - q)])
    effective_step = (
        np.full(2, 4 * common_step) if delta == 0 else common_step / variances
    )
    fourth = np.array([variances[0] ** 2, variances[1] * (1 - 3 * variances[1])])
    transition = np.diag(
        (1 - effective_step * variances) ** 2
        + effective_step**2 * (fourth - variances**2) / batch
    )
    transition[0, 1] = effective_step[0] ** 2 * np.prod(variances) / batch
    transition[1, 0] = effective_step[1] ** 2 * np.prod(variances) / batch
    injection = effective_step**2 * variances / batch
    augmented = np.eye(3)
    augmented[:2, :2] = transition
    augmented[:2, 2] = injection
    power = np.linalg.matrix_power(augmented, count)
    return {
        "homogeneous": power[:2, :2] @ np.square(signal),
        "noise_unit": power[:2, 2],
        "mean_error": -((1 - effective_step * variances) ** count) * signal,
        "radius": float(max(abs(np.linalg.eigvals(transition)))),
    }


def contrast(q, common_step, batch, count, signal, objective="rare"):
    weight = 0.5 * np.array(
        [0.25, (1 - q) ** 2 if objective == "rare" else q * (1 - q)]
    )
    plain, scaled = [
        diagonal_parts(q, common_step, batch, delta, count, signal)
        for delta in (0, 0.5)
    ]
    homogeneous = weight @ (scaled["homogeneous"] - plain["homogeneous"])
    noise = weight @ (scaled["noise_unit"] - plain["noise_unit"])
    return homogeneous, noise, max(plain["radius"], scaled["radius"])


def check_reduction():
    signal = np.array([0.8, -1.1])
    sigma = 1.3
    cases = 0
    for q, common_step, batch, delta in itertools.product(
        [0.02, 0.13], [0.002, 0.03], [1, 2], [0, 0.5]
    ):
        model = make_model(q, "independent")
        scales = np.diag(model["gram"]) ** delta
        step = 4 * common_step if delta == 0 else common_step
        counts = [0, 1, 2, 1000, 10000]
        full = moment_path(model, scales, step, batch, counts, signal, sigma**2)
        means, seconds = enumerate_paths(model, scales, step, batch, signal, sigma, 2)
        for i, count in enumerate(counts):
            reduced = diagonal_parts(q, common_step, batch, delta, count, signal)
            diagonal = reduced["homogeneous"] + sigma**2 * reduced["noise_unit"]
            np.testing.assert_allclose(
                diagonal, np.diag(full["second"][i]), atol=2e-11, rtol=2e-10
            )
            np.testing.assert_allclose(
                sigma**2 * reduced["noise_unit"],
                np.diag(full["noise_covariance"][i]),
                atol=2e-11,
                rtol=2e-10,
            )
            np.testing.assert_allclose(
                reduced["mean_error"], full["bias"][i], atol=2e-11, rtol=2e-10
            )
            if count <= 2:
                np.testing.assert_allclose(diagonal, np.diag(seconds[i]), atol=2e-11)
                np.testing.assert_allclose(reduced["mean_error"], means[i], atol=2e-11)
            cases += 1
    print(f"Reduced moments agree with full moments at {cases} endpoints.")
    print("Short endpoints also agree with enumerated gradient updates.")


def check_candidate_grid():
    lower, upper, margins, radii = [], [], [], []
    for q, common_step, common_signal, rare_signal in itertools.product(
        np.linspace(0.019, 0.021, 5),
        np.linspace(0.0019, 0.0021, 5),
        [0.95, 1, 1.05],
        [0.95, 1, 1.05],
    ):
        thresholds = {}
        signal = np.array([common_signal, rare_signal])
        for batch, count in itertools.product([1, 10], [1000, 10000]):
            homogeneous, noise, radius = contrast(q, common_step, batch, count, signal)
            assert homogeneous < 0 < noise
            thresholds[batch, count] = -homogeneous / noise
            radii.append(radius)
            for noise_variance in [1.5, 5.0]:
                difference = homogeneous + noise_variance * noise
                margins.append(
                    difference if (batch, count) == (1, 10000) else -difference
                )
        lower.append(thresholds[1, 10000])
        upper.append(
            min(thresholds[1, 1000], thresholds[10, 1000], thresholds[10, 10000])
        )
    assert max(lower) < 1.5 and min(upper) > 5
    assert min(margins) > 0 and max(radii) < 1
    print(f"Exploratory grid: {len(lower)} parameter settings; noise endpoints 1.5, 5.")
    print(f"Largest lower noise threshold: {max(lower):.12f}")
    print(f"Smallest upper noise threshold: {min(upper):.12f}")
    print(f"Smallest signed rare-risk gap: {min(margins):.12f}")
    print(f"Largest reduced moment spectral radius: {max(radii):.12f}")
    print("These floating-point grid checks do not prove the continuous-box claim.")


def main():
    assert __debug__, "Run ordinary Python without -O."
    check_reduction()
    print("Anchor q=0.02, common step=0.002, signal=(1,1); SD minus no scaling:")
    print("batch updates objective homogeneous noise_coefficient noise_threshold")
    for batch, count, objective in itertools.product(
        [1, 10], [1000, 10000], ["rare", "aggregate"]
    ):
        homogeneous, noise, _ = contrast(
            0.02, 0.002, batch, count, np.ones(2), objective
        )
        assert homogeneous < 0 < noise
        print(
            f"{batch} {count} {objective} {homogeneous:.12f} "
            f"{noise:.12f} {-homogeneous / noise:.12f}"
        )
    check_candidate_grid()


if __name__ == "__main__":
    main()
