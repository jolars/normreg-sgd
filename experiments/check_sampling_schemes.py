"""Check matched covariance, fixed-data replacement, and random reshuffling.

Reproduce with ``devenv shell -- python experiments/check_sampling_schemes.py``.
All supports, ordered batches, and short training paths are enumerated; no
Monte Carlo seeds or uncertainty intervals are needed. The loss is averaged
squared loss, centering and diagonal scales are known and fixed, and the
intercept is fixed at its population value. Errors and prediction risks are
reported on the original feature scale. No reference results are written.
The examples check ``notes/sampling-schemes.md``. They do not establish a
joint sampling limit, a proof, a novelty claim, or an optimizer ranking.
"""

import itertools
import json
from collections import defaultdict
from fractions import Fraction

import numpy as np

RTOL = 3e-12
ATOL = 3e-12


def assert_close(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)
    return float(np.max(np.abs(np.asarray(actual) - expected)))


def moments(values, weights):
    assert_close(weights.sum(), 1)
    mean = weights @ values
    centered = values - mean
    return (
        mean,
        values.T @ (weights[:, None] * values),
        centered.T @ (weights[:, None] * centered),
    )


def binary_support(q, dependence):
    """Use rational cell masses to check feasibility and covariance exactly."""
    cells = list(itertools.product([0, 1], repeat=3))
    weights = []
    for left, right, rare in cells:
        correlation = dependence if rare else -q * dependence / (1 - q)
        mass = q if rare else 1 - q
        weights.append(mass * (1 + correlation * (2 * left - 1) * (2 * right - 1)) / 4)
    assert all(weight >= 0 for weight in weights)
    assert sum(weights) == 1
    means = [sum(p * row[j] for p, row in zip(weights, cells)) for j in range(3)]
    assert means == [Fraction(1, 2), Fraction(1, 2), q]
    covariance = [
        [
            sum(
                p * (row[i] - means[i]) * (row[j] - means[j])
                for p, row in zip(weights, cells)
            )
            for j in range(3)
        ]
        for i in range(3)
    ]
    assert covariance == [
        [Fraction(1, 4), 0, 0],
        [0, Fraction(1, 4), 0],
        [0, 0, q * (1 - q)],
    ]
    centered = np.array(cells, dtype=float) - np.array(means, dtype=float)
    scales = np.sqrt(np.diag(np.array(covariance, dtype=float)))
    return centered, np.array(weights, dtype=float), scales


def symmetric_basis(dimension):
    basis = []
    for i in range(dimension):
        for j in range(i, dimension):
            matrix = np.zeros((dimension, dimension))
            matrix[i, j] = matrix[j, i] = 1 if i == j else 1 / np.sqrt(2)
            basis.append(matrix)
    return np.array(basis)


def operator_matrix(action, basis):
    return np.array(
        [[np.sum(left * action(right)) for right in basis] for left in basis]
    )


def enumerate_batches(features, noise, weights, batch_size, signal):
    indices = np.array(list(itertools.product(range(len(features)), repeat=batch_size)))
    return (
        features[indices],
        features[indices] @ signal + noise[indices],
        weights[indices].prod(axis=1),
    )


def direct_trajectories(
    batches, signal, scales, initial, step, count, initial_weights=None
):
    """Differentiate sampled losses rather than applying a moment recurrence."""
    features, response, batch_weights = batches
    coefficients = np.atleast_2d(initial).astype(float)
    weights = np.ones(1) if initial_weights is None else initial_weights.copy()
    results = [moments(coefficients - signal, weights)]
    for _ in range(count):
        residual = np.einsum("pi,bni->pbn", coefficients, features) - response
        gradient = np.einsum("pbn,bni->pbi", residual, features) / features.shape[1]
        coefficients = (coefficients[:, None] - step * gradient / scales**2).reshape(
            -1, len(scales)
        )
        weights = (weights[:, None] * batch_weights).ravel()
        results.append(moments(coefficients - signal, weights))
    return results


def empirical_operators(features, residuals, scales, step, batch_size):
    z = features / scales
    hessian = z.T @ z / len(z)
    score = z.T @ residuals / len(z)
    noise = z.T @ (residuals[:, None] ** 2 * z) / len(z)
    mean_update = np.eye(len(scales)) - step * hessian

    def fourth(matrix):
        quadratic = np.einsum("ni,ij,nj->n", z, matrix, z)
        return z.T @ (quadratic[:, None] * z) / len(z)

    def transition(matrix):
        return mean_update @ matrix @ mean_update + step**2 / batch_size * (
            fourth(matrix) - hessian @ matrix @ hessian
        )

    def cross(mean):
        mixed = z.T @ ((residuals * (z @ mean))[:, None] * z) / len(z)
        return np.outer(mean_update @ mean, score) - step / batch_size * (
            mixed - np.outer(hessian @ mean, score)
        )

    injection = step**2 * (
        noise / batch_size + (1 - 1 / batch_size) * np.outer(score, score)
    )

    def advance(mean, second):
        mixed = cross(mean)
        return (
            mean_update @ mean + step * score,
            transition(second) + step * (mixed + mixed.T) + injection,
        )

    return advance, transition, cross, injection, score


def check_matched_covariance():
    largest_error = 0.0
    # Include the feasibility boundary and both signs of dependence.
    for q, dependence in itertools.product(
        [Fraction(1, 100), Fraction(1, 10), Fraction(1, 2)],
        [Fraction(-1), Fraction(0), Fraction(1)],
    ):
        features, weights, scales = binary_support(q, dependence)
        z = features / scales
        largest_error = max(
            largest_error, assert_close(z.T @ (weights[:, None] * z), np.eye(3))
        )
        mixed = weights @ (z[:, 0] * z[:, 1] * z[:, 2] ** 2)
        largest_error = max(
            largest_error,
            assert_close(mixed, float(dependence * (1 - 2 * q) / (1 - q))),
        )
        delta = float(dependence * (1 - 2 * q) / (1 - q))
        mu = float(((1 - q) ** 3 + q**3) / (q * (1 - q)))
        enumerated_operator = []
        for matrix in symmetric_basis(3):
            left, middle, rare = matrix.diagonal()
            common_cross, left_rare, right_rare = (
                matrix[0, 1],
                matrix[0, 2],
                matrix[1, 2],
            )
            formula = np.array(
                [
                    [
                        left + middle + rare,
                        2 * common_cross + delta * rare,
                        2 * left_rare + 2 * delta * right_rare,
                    ],
                    [
                        2 * common_cross + delta * rare,
                        left + middle + rare,
                        2 * right_rare + 2 * delta * left_rare,
                    ],
                    [
                        2 * left_rare + 2 * delta * right_rare,
                        2 * right_rare + 2 * delta * left_rare,
                        left + middle + mu * rare + 2 * delta * common_cross,
                    ],
                ]
            )
            enumerated = z.T @ (
                (weights * np.einsum("ni,ij,nj->n", z, matrix, z))[:, None] * z
            )
            largest_error = max(largest_error, assert_close(enumerated, formula))
            enumerated_operator.append(
                np.einsum("aij,ij->a", symmetric_basis(3), enumerated)
            )
        expected_max = max(
            (mu + 2 + np.sqrt((mu - 2) ** 2 + 8 * (1 + delta**2))) / 2,
            2 + 2 * abs(delta),
        )
        largest_error = max(
            largest_error,
            assert_close(np.linalg.eigvalsh(enumerated_operator)[-1], expected_max),
        )

    q = Fraction(1, 4)
    basis = symmetric_basis(3)
    signal = np.array([0.4, -0.7, 1.2])
    initial = np.zeros(3)
    cases = []
    for dependence in [Fraction(0), Fraction(1)]:
        features, weights, scales = binary_support(q, dependence)
        z = features / scales

        def fourth(matrix):
            return z.T @ (
                (weights * np.einsum("ni,ij,nj->n", z, matrix, z))[:, None] * z
            )

        largest_fourth = np.linalg.eigvalsh(operator_matrix(fourth, basis))[-1]
        critical = 2 / largest_fourth
        cases.append((features, weights, scales, largest_fourth, critical))

    assert_close(cases[0][-1], 12 / (13 + np.sqrt(73)))
    assert_close(cases[1][-1], 12 / (13 + np.sqrt(105)))
    assert cases[1][-1] < 8 / 15 < cases[0][-1]
    step = 8 / 15
    output = []
    rare_only_second = {}
    for dependence, (features, weights, scales, fourth_max, critical) in enumerate(
        cases
    ):
        z = features / scales
        updates = np.eye(3) - step * np.einsum("ni,nj->nij", z, z)

        def update_action(matrix):
            return np.einsum("n,nij,jk,nkl->il", weights, updates, matrix, updates)

        radius = max(abs(np.linalg.eigvalsh(operator_matrix(update_action, basis))))
        assert (radius > 1) == bool(dependence)
        for batch_size in [1, 2]:
            batches = enumerate_batches(
                features, np.zeros(len(z)), weights, batch_size, signal
            )
            count = 4 // batch_size
            direct = direct_trajectories(batches, signal, scales, initial, step, count)
            mean = scales * (initial - signal)
            second = np.outer(mean, mean)
            for actual_mean, actual_second, _ in direct:
                largest_error = max(
                    largest_error,
                    assert_close(actual_mean, mean / scales),
                    assert_close(actual_second, second / np.outer(scales, scales)),
                )
                fourth = z.T @ (
                    (weights * np.einsum("ni,ij,nj->n", z, second, z))[:, None] * z
                )
                second = (1 - step) ** 2 * second + step**2 / batch_size * (
                    fourth - second
                )
                mean = (1 - step) * mean
            rare_only = direct_trajectories(
                batches, signal, scales, signal + [0, 0, 1], step, 2
            )[-1]
            rare_only_second[dependence, batch_size] = rare_only[1][-1, -1]
            original_second = direct[-1][1]
            covariance = features.T @ (weights[:, None] * features)
            present = features[:, -1] > 0
            rare_moment = (
                features[present].T
                @ (weights[present, None] * features[present])
                / float(q)
            )
            output.append(
                {
                    "dependence": dependence,
                    "q": float(q),
                    "batch_size": batch_size,
                    "updates": count,
                    "processed_observations": count * batch_size,
                    "step": step,
                    "batch_one_critical_step": critical,
                    "largest_fourth_eigenvalue": fourth_max,
                    "batch_one_spectral_radius": radius,
                    "original_coefficient_mse": np.diag(original_second).tolist(),
                    "prediction_mse": float(np.trace(covariance @ original_second)),
                    "rare_prediction_mse": float(
                        np.trace(rare_moment @ original_second)
                    ),
                }
            )
    assert (
        abs(output[0]["rare_prediction_mse"] - output[2]["rare_prediction_mse"]) > 0.01
    )
    for batch_size in [1, 2]:
        delta = float((1 - 2 * q) / (1 - q))
        largest_error = max(
            largest_error,
            assert_close(
                rare_only_second[1, batch_size] - rare_only_second[0, batch_size],
                2 * step**4 * delta**2 / batch_size**2,
            ),
        )
    return {
        "largest_error": largest_error,
        "initial": initial.tolist(),
        "signal": signal.tolist(),
        "scales": scales.tolist(),
        "step_selection": "theory counterexample 8/15; no optimizer tuning",
        "cases": output,
    }


def check_fixed_replacement():
    features = np.array([[-0.5, -0.2], [0.5, -0.2], [0.5, 0.8]])
    scales = np.array([0.5, 0.4])
    signal = np.array([0.7, -0.3])
    initial = np.array([[-0.2, 0.1], [0.4, -0.3]])
    initial_weights = np.array([0.25, 0.75])
    noise = np.array([-0.2, 0.6, -0.1])
    weights = np.full(3, 1 / 3)
    step = 0.17
    largest_error = 0.0
    omitted_cross_discrepancy = 0.0
    # OLS centering removes the empirical score, but not the mixed third moment.
    ols_shift = np.linalg.lstsq(features, noise, rcond=None)[0]
    output = []
    for center_at_ols in [False, True]:
        target = signal + ols_shift if center_at_ols else signal
        residuals = noise - features @ ols_shift if center_at_ols else noise
        for batch_size in [1, 2]:
            batches = enumerate_batches(
                features, residuals, weights, batch_size, target
            )
            count = 6 // batch_size
            direct = direct_trajectories(
                batches, target, scales, initial, step, count, initial_weights
            )
            advance, transition, cross, injection, score = empirical_operators(
                features, residuals, scales, step, batch_size
            )
            if center_at_ols:
                assert_close(score, 0)
            else:
                assert np.linalg.norm(score) > 0.1
            mean, second, covariance = moments(
                scales * (initial - target), initial_weights
            )
            z = features / scales
            hessian = z.T @ z / len(z)
            individual_hessians = np.einsum("ni,nj->nij", z, z)
            individual_scores = z * residuals[:, None]
            if center_at_ols:
                omitted = transition(second) + injection
                full = advance(mean, second)[1]
                discrepancy = np.linalg.norm(full - omitted)
                assert discrepancy > 1e-4
                assert np.linalg.norm(cross(mean)) > 1e-4
                omitted_cross_discrepancy = max(omitted_cross_discrepancy, discrepancy)
            for actual_mean, actual_second, actual_covariance in direct:
                largest_error = max(
                    largest_error,
                    assert_close(actual_mean, mean / scales),
                    assert_close(actual_second, second / np.outer(scales, scales)),
                    assert_close(
                        actual_covariance, covariance / np.outer(scales, scales)
                    ),
                )
                centered_gradient = (individual_hessians - hessian) @ mean - (
                    individual_scores - score
                )
                forcing = centered_gradient.T @ centered_gradient / len(z)
                covariance = transition(covariance) + step**2 / batch_size * forcing
                mean, second = advance(mean, second)
                largest_error = max(
                    largest_error,
                    assert_close(covariance, second - np.outer(mean, mean)),
                )
            output.append(
                {
                    "center_at_ols": center_at_ols,
                    "batch_size": batch_size,
                    "updates": count,
                    "processed_observations": count * batch_size,
                    "original_coefficient_mse": np.diag(direct[-1][1]).tolist(),
                }
            )
    return {
        "largest_error": largest_error,
        "omitted_cross_discrepancy": omitted_cross_discrepancy,
        "features": features.tolist(),
        "scales": scales.tolist(),
        "noise": noise.tolist(),
        "signal": signal.tolist(),
        "initial": initial.tolist(),
        "initial_weights": initial_weights.tolist(),
        "step": step,
        "cases": output,
    }


def check_reshuffling_epochs():
    features = np.array([[-0.5, -0.2], [0.5, -0.2], [0.5, 0.8]])
    scales = np.array([0.5, 0.4])
    signal = np.array([0.7, -0.3])
    initial = np.array([-0.2, 0.1])
    noise = np.array([-0.2, 0.6, -0.1])
    response = features @ signal + noise
    step = 0.17
    permutations = list(itertools.permutations(range(3)))
    affine_epochs = []
    z = features / scales
    for order in permutations:
        epoch = np.eye(3)
        for index in order:
            observation = np.eye(3)
            observation[:2, :2] -= step * np.outer(z[index], z[index])
            observation[:2, 2] = step * z[index] * noise[index]
            epoch = observation @ epoch
        affine_epochs.append(epoch)
    affine_epochs = np.array(affine_epochs)
    augmented = np.append(scales * (initial - signal), 1)
    second = np.outer(augmented, augmented)
    largest_error = 0.0
    results = []
    for epochs in [1, 2]:
        second = np.einsum(
            "nij,jk,nlk->il", affine_epochs, second, affine_epochs
        ) / len(permutations)
        coefficients = []
        for orders in itertools.product(permutations, repeat=epochs):
            coefficient = initial.copy()
            for order in orders:
                for index in order:
                    residual = features[index] @ coefficient - response[index]
                    coefficient -= step * features[index] * residual / scales**2
            coefficients.append(coefficient)
        errors = np.array(coefficients) - signal
        actual_mean, actual_second, _ = moments(
            errors, np.full(len(errors), 1 / len(errors))
        )
        largest_error = max(
            largest_error,
            assert_close(actual_mean, second[:2, 2] / scales),
            assert_close(actual_second, second[:2, :2] / np.outer(scales, scales)),
        )
        results.append(
            {
                "epochs": epochs,
                "updates": 3 * epochs,
                "processed_observations": 3 * epochs,
                "original_coefficient_mse": np.diag(actual_second).tolist(),
            }
        )

    # The note's feasible q=1/3 sample has curvatures 2 and 1/2.
    scalar_step = 2.0
    scalar_features = np.array([[np.sqrt(2)], [-1 / np.sqrt(2)]])
    scalar_signal = np.array([-1.0])
    scalar_initial = np.zeros(1)
    scalar_batches = enumerate_batches(
        scalar_features, np.zeros(2), np.full(2, 0.5), 1, scalar_signal
    )
    replacement_moments = direct_trajectories(
        scalar_batches, scalar_signal, np.ones(1), scalar_initial, scalar_step, 2
    )[-1]
    shuffled_errors = []
    for order in itertools.permutations(range(2)):
        coefficient = scalar_initial.copy()
        for index in order:
            residual = scalar_features[index] @ (coefficient - scalar_signal)
            coefficient -= scalar_step * scalar_features[index] * residual
        shuffled_errors.append((coefficient - scalar_signal)[0])
    shuffled = np.mean(shuffled_errors)
    replacement = replacement_moments[0][0]
    largest_error = max(
        largest_error,
        assert_close(shuffled_errors, 0),
        assert_close(replacement, (1 - 5 * scalar_step / 4) ** 2),
        assert_close(replacement - shuffled, 9 * scalar_step**2 / 16),
        assert_close(replacement_moments[1][0, 0], (9 / 2) ** 2),
    )
    return {
        "largest_error": largest_error,
        "epoch_permutations": len(permutations),
        "scalar_step": float(scalar_step),
        "scalar_reshuffled_mean": float(shuffled),
        "scalar_replacement_mean": float(replacement),
        "scalar_replacement_second_moment": float(replacement_moments[1][0, 0]),
        "scalar_processed_observations": 2,
        "cases": results,
    }


def scalar_path(observations, step, batch_size=1):
    error = Fraction(0)
    path = []
    assert len(observations) % batch_size == 0
    for offset in range(0, len(observations), batch_size):
        gradient = (
            sum(
                feature * (feature * error - noise)
                for feature, noise in observations[offset : offset + batch_size]
            )
            / batch_size
        )
        error -= step * gradient
        path.append(error)
    return tuple(path)


def check_reused_observations():
    support = [(Fraction(x), Fraction(e, 2)) for x in [-1, 1] for e in [-1, 1]]
    variance = Fraction(1, 4)
    largest_noise_difference = Fraction(0)
    for step, count in itertools.product(
        [Fraction(1, 10), Fraction(1), Fraction(3, 2)], [1, 2, 4]
    ):
        reused = sum(scalar_path([row] * count, step)[-1] ** 2 for row in support) / 4
        fresh = (
            sum(
                scalar_path(observations, step)[-1] ** 2
                for observations in itertools.product(support, repeat=count)
            )
            / 4**count
        )
        assert reused == variance * (1 - (1 - step) ** count) ** 2
        assert fresh == step**2 * variance * sum(
            (1 - step) ** (2 * j) for j in range(count)
        )
        if count == 2:
            assert reused - fresh == 2 * step**2 * (1 - step) * variance
            largest_noise_difference = max(
                largest_noise_difference, abs(reused - fresh)
            )
        for batch_size in [1, 3]:
            for row in support:
                assert scalar_path(
                    [row] * count * batch_size, step, batch_size
                ) == scalar_path([row] * count, step)

    # Original-scale gradients keep the Bernoulli counterexample rational.
    q = Fraction(1, 3)
    features = [-q, 1 - q]
    probabilities = [1 - q, q]
    scale_squared = q * (1 - q)
    step = Fraction(1, 5)

    def noiseless_error(observations):
        error = Fraction(1)
        for feature in observations:
            error -= step * feature * (feature * error) / scale_squared
        return error

    reused_mean = sum(
        p * noiseless_error([x, x]) for x, p in zip(features, probabilities)
    )
    fresh_mean = sum(
        probabilities[left]
        * probabilities[right]
        * noiseless_error([features[left], features[right]])
        for left, right in itertools.product(range(2), repeat=2)
    )
    curvature_variance = sum(
        p * (x**2 / scale_squared - 1) ** 2 for x, p in zip(features, probabilities)
    )
    assert reused_mean - fresh_mean == step**2 * curvature_variance > 0
    assert fresh_mean == (1 - step) ** 2

    # Zero empirical score alone does not remove the update/noise correlation.
    residual_features = np.array([[1.0], [2.0]])
    residuals = np.array([2.0, -1.0])
    _, _, cross, _, score = empirical_operators(
        residual_features, residuals, np.ones(1), 0.1, 2
    )
    assert_close(score, 0)
    assert_close(cross(np.array([0.7])), [[3 * 0.1 * 0.7 / 2]])
    return {
        "persistent_noise_formulas_exact": True,
        "largest_checked_noise_second_moment_difference": float(
            largest_noise_difference
        ),
        "noise_variance": float(variance),
        "bernoulli_q": float(q),
        "bernoulli_step": float(step),
        "two_fresh_observations_mean": float(fresh_mean),
        "one_observation_reused_twice_mean": float(reused_mean),
    }


def check_unconditional_first_pass():
    # The joint path law, including fixed observation noise, is checked exactly.
    support = [(Fraction(x), Fraction(e, 2)) for x in [-1, 2] for e in [-1, 1]]
    probabilities = [Fraction(1, 3), Fraction(1, 3), Fraction(1, 6), Fraction(1, 6)]
    step = Fraction(1, 10)
    n = 3
    permutations = list(itertools.permutations(range(n)))
    fresh = defaultdict(Fraction)
    shuffled = defaultdict(Fraction)
    second_epoch = defaultdict(Fraction)
    for indices in itertools.product(range(len(support)), repeat=n):
        probability = np.prod([probabilities[index] for index in indices])
        dataset = [support[index] for index in indices]
        fresh[scalar_path(dataset, step)] += probability
        for first_order in permutations:
            first = [dataset[index] for index in first_order]
            shuffled[scalar_path(first, step)] += probability / len(permutations)
            for second_order in permutations:
                observations = first + [dataset[index] for index in second_order]
                second_epoch[scalar_path(observations, step)[-1]] += (
                    probability / len(permutations) ** 2
                )
    assert dict(fresh) == dict(shuffled)
    assert sum(fresh.values()) == sum(second_epoch.values()) == 1
    # Disjoint minibatches also have the fresh path law before data reuse.
    batch_size = 2
    batch_n = 4
    batch_permutations = list(itertools.permutations(range(batch_n)))
    batch_fresh = defaultdict(Fraction)
    batch_shuffled = defaultdict(Fraction)
    for indices in itertools.product(range(len(support)), repeat=batch_n):
        probability = np.prod([probabilities[index] for index in indices])
        dataset = [support[index] for index in indices]
        batch_fresh[scalar_path(dataset, step, batch_size)] += probability
        for order in batch_permutations:
            observations = [dataset[index] for index in order]
            batch_shuffled[scalar_path(observations, step, batch_size)] += (
                probability / len(batch_permutations)
            )
    assert dict(batch_fresh) == dict(batch_shuffled)
    assert sum(batch_fresh.values()) == 1
    fresh_second = Fraction(0)
    for indices in itertools.product(range(len(support)), repeat=2 * n):
        probability = np.prod([probabilities[index] for index in indices])
        last = scalar_path([support[index] for index in indices], step)[-1]
        fresh_second += probability * last**2
    reused_second = sum(
        probability * error**2 for error, probability in second_epoch.items()
    )
    assert abs(fresh_second - reused_second) > Fraction(1, 1000)
    return {
        "dataset_size": n,
        "batch_size": 1,
        "step": float(step),
        "first_pass_updates": n,
        "first_pass_path_laws_equal_exactly": True,
        "batch_two_first_pass_path_laws_equal_exactly": True,
        "batch_two_dataset_size": batch_n,
        "batch_two_updates": batch_n // batch_size,
        "six_fresh_observations_mse": float(fresh_second),
        "two_passes_three_observations_mse": float(reused_second),
    }


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: these checks depend on assertions.")
    results = {
        "method": "exact rational support/path enumeration; floating matrix checks",
        "rtol": RTOL,
        "atol": ATOL,
        "matched_covariance": check_matched_covariance(),
        "fixed_replacement": check_fixed_replacement(),
        "reshuffling_epochs": check_reshuffling_epochs(),
        "reused_observations": check_reused_observations(),
        "unconditional_first_pass": check_unconditional_first_pass(),
    }
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
