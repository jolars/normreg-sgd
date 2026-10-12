"""Independently check finite-update population GD and fresh-batch SGD moments.

Run ordinary Python inside ``devenv shell``. The checks enumerate feasible
binary supports, ordered independent batches, and every short training path.
They use population centering and fixed scales, and write no reference files.
"""

import itertools
import json

import numpy as np


def binary_support(rare_probability, dependence):
    common = np.array(list(itertools.product([0.0, 1.0], repeat=2)))
    absent = np.array([0.35, 0.20, 0.10, 0.35])
    present = {
        "independent": absent,
        "positive": np.array([0.05, 0.05, 0.25, 0.65]),
        "negative": np.array([0.70, 0.20, 0.10, 0.00]),
    }[dependence]
    cells = np.vstack(
        [np.column_stack([common, np.full(len(common), rare)]) for rare in [0, 1]]
    )
    probabilities = np.concatenate(
        [(1 - rare_probability) * absent, rare_probability * present]
    )
    assert 0 < rare_probability < 1 and np.all(probabilities >= 0)
    np.testing.assert_allclose(probabilities.sum(), 1)
    centered = cells - probabilities @ cells
    covariance = centered.T @ (probabilities[:, None] * centered)
    assert np.linalg.eigvalsh(covariance).min() > 0
    np.testing.assert_allclose(probabilities @ centered, 0, atol=1e-15)
    kappa = present @ common - absent @ common
    np.testing.assert_allclose(
        covariance[:-1, -1] / covariance[-1, -1], kappa, atol=1e-14
    )
    mean_absent = absent @ common
    common_covariance = (common - mean_absent).T @ (
        absent[:, None] * (common - mean_absent)
    )
    return cells, centered, probabilities, covariance, common_covariance, kappa


def observation_support(cells, centered, probabilities, noise_scale):
    if noise_scale == 0:
        return centered, np.zeros(len(centered)), probabilities
    # Asymmetric, feature-dependent noise checks conditional mean zero without
    # relying on symmetry or independence between the noise and the features.
    amplitude = noise_scale * (0.3 + cells @ np.array([0.2, 0.1, 0.7]))
    noise = (amplitude[:, None] * np.array([-1.0, 2.0])).ravel()
    noise_probabilities = np.array([2 / 3, 1 / 3])
    np.testing.assert_allclose(
        noise.reshape(-1, 2) @ noise_probabilities, 0, atol=1e-15
    )
    return (
        np.repeat(centered, 2, axis=0),
        noise,
        (probabilities[:, None] * noise_probabilities).ravel(),
    )


def enumerate_batches(features, noise, probabilities, batch_size, signal):
    indices = np.array(list(itertools.product(range(len(features)), repeat=batch_size)))
    weights = probabilities[indices].prod(axis=1)
    batch_features = features[indices]
    batch_response = batch_features @ signal + noise[indices]
    np.testing.assert_allclose(weights.sum(), 1)
    return batch_features, batch_response, weights


def empirical_moments(errors, probabilities):
    mean = probabilities @ errors
    centered = errors - mean
    covariance = centered.T @ (probabilities[:, None] * centered)
    second = errors.T @ (probabilities[:, None] * errors)
    return mean, covariance, second


def trajectory_moments(batches, scales, signal, initial, initial_weights, steps):
    features, response, batch_weights = batches
    coefficients = initial.copy()
    theta = initial * scales
    weights = initial_weights.copy()
    scaled_features = features / scales
    moments = []
    coordinate_error = 0.0
    for step in steps:
        moments.append(empirical_moments(coefficients - signal, weights))
        # These are direct gradients of the sampled losses in each coordinate
        # system, rather than applications of a moment or Hessian recurrence.
        residual = np.einsum("si,abi->sab", coefficients, features) - response
        gradients = np.einsum("sab,abi->sai", residual, features) / features.shape[1]
        coefficients = (
            coefficients[:, None, :] - step * gradients / scales**2
        ).reshape(-1, len(scales))
        scaled_residual = np.einsum("si,abi->sab", theta, scaled_features) - response
        scaled_gradients = (
            np.einsum("sab,abi->sai", scaled_residual, scaled_features)
            / features.shape[1]
        )
        theta = (theta[:, None, :] - step * scaled_gradients).reshape(-1, len(scales))
        weights = (weights[:, None] * batch_weights).ravel()
        np.testing.assert_allclose(weights.sum(), 1, atol=1e-13)
        np.testing.assert_allclose(theta / scales, coefficients, atol=1e-12)
        coordinate_error = max(
            coordinate_error, float(np.max(abs(theta / scales - coefficients)))
        )
    moments.append(empirical_moments(coefficients - signal, weights))
    return moments, coordinate_error


def moment_operators(features, noise, probabilities, scales, step, batch_size):
    scaled = features / scales
    hessian = scaled.T @ (probabilities[:, None] * scaled)
    mean_update = np.eye(len(scales)) - step * hessian
    noise_moment = scaled.T @ ((probabilities * noise**2)[:, None] * scaled)
    outer_products = np.einsum("ai,aj->aij", scaled, scaled)

    def fluctuation(matrix):
        fourth = np.einsum(
            "a,aij,jk,akl->il", probabilities, outer_products, matrix, outer_products
        )
        return fourth - hessian @ matrix @ hessian

    def transition(matrix):
        return mean_update @ matrix @ mean_update + step**2 / batch_size * fluctuation(
            matrix
        )

    kronecker = np.kron(mean_update, mean_update) + step**2 / batch_size * (
        sum(
            weight * np.kron(outer, outer)
            for weight, outer in zip(probabilities, outer_products, strict=True)
        )
        - np.kron(hessian, hessian)
    )
    return hessian, mean_update, noise_moment, fluctuation, transition, kronecker


def apply_power(operator, count, matrix):
    result = matrix.copy()
    for _ in range(count):
        result = operator(result)
    return result


def check_sgd_trajectories():
    max_error = 0.0
    max_coordinate_error = 0.0
    case_count = 0
    signal = np.array([0.8, -0.6, 0.4])
    initializations = [
        (np.array([[0.2, -0.1, -0.3]]), np.ones(1)),
        (np.array([[0.2, -0.1, -0.3], [-0.4, 0.3, 0.1]]), np.array([0.4, 0.6])),
        (signal[None, :], np.ones(1)),
    ]
    for dependence in ["independent", "positive", "negative"]:
        cells, centered, probabilities, covariance, _, _ = binary_support(
            0.13, dependence
        )
        for exponent, noise_scale, batch_size in itertools.product(
            [0, 0.5, 1], [0, 0.35], [1, 2]
        ):
            scales = np.diag(covariance) ** exponent
            features, noise, weights = observation_support(
                cells, centered, probabilities, noise_scale
            )
            scaled = features / scales
            hessian = scaled.T @ (weights[:, None] * scaled)
            step = 0.24 / np.linalg.eigvalsh(hessian).max()
            batches = enumerate_batches(features, noise, weights, batch_size, signal)
            _, mean_update, noise_moment, fluctuation, transition, kronecker = (
                moment_operators(features, noise, weights, scales, step, batch_size)
            )
            injection = step**2 / batch_size * noise_moment
            # A nonscalar test matrix detects missing mixed fourth moments.
            test_matrix = np.array(
                [[1.0, -0.3, 0.2], [-0.3, 0.5, 0.1], [0.2, 0.1, 0.8]]
            )
            batch_scaled = batches[0] / scales
            batch_hessians = (
                np.einsum("abi,abj->aij", batch_scaled, batch_scaled) / batch_size
            )
            updates = np.eye(3) - step * batch_hessians
            enumerated_transition = np.einsum(
                "a,aij,jk,alk->il", batches[2], updates, test_matrix, updates
            )
            np.testing.assert_allclose(transition(test_matrix), enumerated_transition)
            for initial, initial_weights in initializations:
                updates_count = 3 if batch_size == 1 else 2
                moments, coordinate_error = trajectory_moments(
                    batches,
                    scales,
                    signal,
                    initial,
                    initial_weights,
                    [step] * updates_count,
                )
                max_coordinate_error = max(max_coordinate_error, coordinate_error)
                mean0, covariance0, second0 = empirical_moments(
                    (initial - signal) * scales, initial_weights
                )
                current_second = second0.copy()
                current_covariance = covariance0.copy()
                for count, (mean, centered_covariance, second) in enumerate(moments):
                    mean_formula = np.linalg.matrix_power(mean_update, count) @ mean0
                    noise_sum = sum(
                        (apply_power(transition, j, injection) for j in range(count)),
                        np.zeros((3, 3)),
                    )
                    second_formula = apply_power(transition, count, second0) + noise_sum
                    design_sum = np.zeros((3, 3))
                    for j in range(count):
                        mean_j = np.linalg.matrix_power(mean_update, j) @ mean0
                        design_sum += apply_power(
                            transition,
                            count - 1 - j,
                            step**2
                            / batch_size
                            * fluctuation(np.outer(mean_j, mean_j)),
                        )
                    initial_sum = apply_power(transition, count, covariance0)
                    covariance_formula = initial_sum + design_sum + noise_sum
                    for contribution in [initial_sum, design_sum, noise_sum]:
                        assert np.linalg.eigvalsh(contribution).min() > -1e-12
                    np.testing.assert_allclose(
                        current_second, second_formula, atol=2e-12
                    )
                    np.testing.assert_allclose(
                        current_covariance, covariance_formula, atol=2e-12
                    )
                    vector_formula = np.linalg.matrix_power(
                        kronecker, count
                    ) @ second0.ravel(order="F") + sum(
                        (
                            np.linalg.matrix_power(kronecker, j)
                            @ injection.ravel(order="F")
                            for j in range(count)
                        ),
                        np.zeros(9),
                    )
                    np.testing.assert_allclose(
                        vector_formula.reshape(3, 3, order="F"),
                        second_formula,
                        atol=2e-12,
                    )
                    for actual, expected in [
                        (mean, mean_formula / scales),
                        (
                            centered_covariance,
                            covariance_formula / np.outer(scales, scales),
                        ),
                        (second, second_formula / np.outer(scales, scales)),
                    ]:
                        np.testing.assert_allclose(
                            actual, expected, atol=2e-12, rtol=1e-10
                        )
                        max_error = max(
                            max_error, float(np.max(abs(actual - expected)))
                        )
                    np.testing.assert_allclose(
                        np.trace(covariance @ second),
                        mean_formula @ hessian @ mean_formula
                        + np.trace(hessian @ covariance_formula),
                        atol=2e-12,
                    )
                    current_second = transition(current_second) + injection
                    current_covariance = (
                        transition(current_covariance)
                        + step**2
                        / batch_size
                        * fluctuation(np.outer(mean_formula, mean_formula))
                        + injection
                    )
                if noise_scale == 0 and np.array_equal(initial, signal[None, :]):
                    np.testing.assert_allclose(moments[-1][2], 0, atol=1e-28)
                case_count += 1
    return case_count, max_error, max_coordinate_error


def check_population_gd():
    maximum_error = 0.0
    signal = np.array([1.2, -0.7, 0.3])
    initial = np.array([-0.2, 0.4, -0.5])
    for dependence, exponent, step_factor in itertools.product(
        ["independent", "positive", "negative"], [0, 0.5, 1], [0.3, 2.1]
    ):
        _, centered, probabilities, covariance, _, _ = binary_support(0.09, dependence)
        scales = np.diag(covariance) ** exponent
        scaled_covariance = covariance / np.outer(scales, scales)
        step = step_factor / np.linalg.eigvalsh(scaled_covariance).max()
        generator = covariance / scales[:, None] ** 2
        coefficients = initial.copy()
        for count in range(8):
            formula = signal + np.linalg.matrix_power(
                np.eye(3) - step * generator, count
            ) @ (initial - signal)
            np.testing.assert_allclose(coefficients, formula, atol=2e-12)
            maximum_error = max(
                maximum_error, float(np.max(abs(coefficients - formula)))
            )
            residual = centered @ coefficients - centered @ signal
            coefficients -= step / scales**2 * (centered.T @ (probabilities * residual))
    return maximum_error


def rare_mean_limit(common_generator, kappa, rare_rate, step, count, signal, initial):
    common_update = np.eye(len(kappa)) - step * common_generator
    rare_update = 1 - step * rare_rate
    deficit = signal - initial
    result = np.empty_like(signal)
    result[:-1] = (
        signal[:-1] - np.linalg.matrix_power(common_update, count) @ deficit[:-1]
    )
    result[-1] = signal[-1] - rare_update**count * deficit[-1]
    for j in range(count):
        result[-1] += (
            step
            * rare_rate
            * rare_update ** (count - 1 - j)
            * kappa
            @ np.linalg.matrix_power(common_update, j)
            @ deficit[:-1]
        )
    return result


def check_rare_mean():
    largest_final_error = 0.0
    signal = np.array([1.1, -0.8, 0.0])
    initial_limit = np.array([0.2, 0.3, -0.4])
    for dependence, rare_rate in itertools.product(
        ["independent", "positive", "negative"], [0.0, 0.6, 1.0]
    ):
        errors = []
        for rare_probability in [1e-2, 1e-4, 1e-6]:
            _, centered, weights, covariance, common_limit, kappa = binary_support(
                rare_probability, dependence
            )
            common_scales_limit = np.sqrt(np.diag(common_limit))
            common_generator = common_limit / common_scales_limit[:, None] ** 2
            scales = np.sqrt(np.diag(covariance))
            scales[-1] = (
                1.0 if rare_rate == 0 else np.sqrt(covariance[-1, -1] / rare_rate)
            )
            initial = initial_limit + rare_probability * np.array([0.3, -0.1, 0.2])
            coefficients = initial.copy()
            step = 0.3
            largest = 0.0
            for count in range(9):
                limit = rare_mean_limit(
                    common_generator,
                    kappa,
                    rare_rate,
                    step,
                    count,
                    signal,
                    initial_limit,
                )
                largest = max(largest, float(np.max(abs(coefficients - limit))))
                residual = centered @ coefficients - centered @ signal
                coefficients -= step / scales**2 * (centered.T @ (weights * residual))
            errors.append(largest)
        assert errors[1] < errors[0] / 50
        assert errors[2] < errors[1] / 50
        assert errors[-1] < 5e-6
        largest_final_error = max(largest_final_error, errors[-1])
    # The repeated eigenvalue case also checks the zero base at eta=1, k=1.
    for step, count in itertools.product([0.2, 1.0, 1.4], range(6)):
        signal_two = np.array([1.3, -0.4])
        limit = rare_mean_limit(
            np.ones((1, 1)), np.array([0.35]), 1.0, step, count, signal_two, np.zeros(2)
        )
        expected = (1 - (1 - step) ** count) * signal_two
        if count:
            expected[-1] += (
                step * 0.35 * count * (1 - step) ** (count - 1) * signal_two[0]
            )
        np.testing.assert_allclose(limit, expected, atol=1e-14)
    return largest_final_error


def main():
    assert __debug__, "Run without -O: these checks depend on assertions."
    cases, moment_error, coordinate_error = check_sgd_trajectories()
    print(
        json.dumps(
            {
                "enumerated_sgd_cases": cases,
                "sgd_moment_max_error": moment_error,
                "trajectory_coordinate_max_error": coordinate_error,
                "population_gd_max_error": check_population_gd(),
                "rare_mean_max_error_at_q_1e_minus_6": check_rare_mean(),
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
