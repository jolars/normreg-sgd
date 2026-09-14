"""Check batch-rarity stability using finite binary supports and batch enumeration.

Run ordinary Python in the project devenv environment. These deterministic
checks use known population centering, standard-deviation scales, fresh IID
batches, and averaged squared loss. They write no reference results.
"""

import itertools
import json

import numpy as np
from scipy.linalg import eigh
from scipy.stats import binom


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


def binary_support(q, dependence):
    common = np.array(list(itertools.product([0.0, 1.0], repeat=2)))
    common_probabilities = np.array([0.35, 0.15, 0.2, 0.3])
    weights = {
        "independent": np.ones(4),
        "nested": np.array([0.0, 0.0, 0.0, 1.0]),
        "disjoint": np.array([1.0, 0.0, 0.0, 0.0]),
    }[dependence]
    conditional = q * weights / (common_probabilities @ weights)
    assert np.all((conditional >= 0) & (conditional <= 1))
    values = np.array([np.append(row, rare) for row in common for rare in [0, 1]])
    probabilities = (
        common_probabilities[:, None] * np.column_stack((1 - conditional, conditional))
    ).ravel()
    np.testing.assert_allclose(probabilities.sum(), 1)
    mean = probabilities @ values
    np.testing.assert_allclose(mean[-1], q)
    centered = values - mean
    covariance = centered.T @ (probabilities[:, None] * centered)
    assert np.linalg.eigvalsh(covariance).min() > 0
    scales = np.sqrt(np.diag(covariance))
    return centered / scales, probabilities, scales


def enumerate_batches(z, probabilities, batch_size):
    indices = np.array(list(itertools.product(range(len(z)), repeat=batch_size)))
    batches = z[indices]
    batch_probabilities = probabilities[indices].prod(axis=1)
    hessians = np.einsum("bki,bkj->bij", batches, batches) / batch_size
    np.testing.assert_allclose(batch_probabilities.sum(), 1)
    return hessians, batch_probabilities


def support_operators(z, probabilities, batch_size):
    hessian = z.T @ (probabilities[:, None] * z)

    def fourth_action(matrix):
        quadratic = np.einsum("ni,ij,nj->n", z, matrix, z)
        return z.T @ ((probabilities * quadratic)[:, None] * z)

    def batch_action(matrix):
        return (1 - 1 / batch_size) * hessian @ matrix @ hessian + fourth_action(
            matrix
        ) / batch_size

    basis = symmetric_basis(z.shape[1])
    linear = operator_matrix(lambda matrix: hessian @ matrix + matrix @ hessian, basis)
    quadratic = operator_matrix(batch_action, basis)
    critical = 1 / eigh(quadratic, linear, eigvals_only=True)[-1]
    energy = batch_action(np.eye(z.shape[1]))
    sufficient = 2 * np.linalg.eigvalsh(hessian)[0] / np.linalg.eigvalsh(energy)[-1]
    rare_fourth = probabilities @ z[:, -1] ** 4
    necessary = 2 / (1 + (rare_fourth - 1) / batch_size)
    return hessian, linear, quadratic, basis, critical, sufficient, necessary


def check_enumerated_operators():
    largest_error = 0.0
    smallest_threshold_ratio = 1.0
    for q, dependence, batch_size in itertools.product(
        [0.02, 0.1], ["independent", "nested", "disjoint"], [1, 2, 3]
    ):
        z, probabilities, _ = binary_support(q, dependence)
        batches, weights = enumerate_batches(z, probabilities, batch_size)
        hessian, linear, quadratic, basis, critical, sufficient, necessary = (
            support_operators(z, probabilities, batch_size)
        )
        assert sufficient <= critical + 1e-12 <= necessary + 2e-12
        smallest_threshold_ratio = min(smallest_threshold_ratio, critical / necessary)
        np.testing.assert_allclose(
            np.einsum("b,bij->ij", weights, batches), hessian, atol=2e-14
        )
        for multiple in [0.6, 1.0, 1.05]:
            step = multiple * critical
            updates = np.eye(z.shape[1]) - step * batches

            def enumerated_action(matrix):
                return np.einsum("b,bij,jk,bkl->il", weights, updates, matrix, updates)

            enumerated = operator_matrix(enumerated_action, basis)
            formula = np.eye(len(basis)) - step * linear + step**2 * quadratic
            np.testing.assert_allclose(formula, enumerated, rtol=2e-12, atol=2e-12)
            largest_error = max(largest_error, float(np.max(abs(formula - enumerated))))
            eigenvalues = np.linalg.eigvalsh(enumerated)
            np.testing.assert_allclose(
                max(abs(eigenvalues)), eigenvalues[-1], atol=1e-12
            )
            if multiple < 1:
                assert eigenvalues[-1] < 1 - 1e-6
            elif multiple > 1:
                assert eigenvalues[-1] > 1 + 1e-6
            else:
                np.testing.assert_allclose(eigenvalues[-1], 1, atol=2e-12)
            # Rank-one inputs independently check the scalar necessary restriction.
            rare = np.zeros((z.shape[1], z.shape[1]))
            rare[-1, -1] = 1
            factor = enumerated_action(rare)[-1, -1]
            fourth = probabilities @ z[:, -1] ** 4
            np.testing.assert_allclose(
                factor, 1 - 2 * step + step**2 * (1 + (fourth - 1) / batch_size)
            )
    assert smallest_threshold_ratio < 0.9
    return largest_error, smallest_threshold_ratio


def check_trajectories_and_noise():
    largest_error = 0.0
    for dependence in ["independent", "nested", "disjoint"]:
        z, probabilities, scales = binary_support(0.08, dependence)
        batches, weights = enumerate_batches(z, probabilities, 2)
        hessian, linear, quadratic, basis, critical, _, _ = support_operators(
            z, probabilities, 2
        )
        step = 0.6 * critical
        updates = np.eye(3) - step * batches
        operator = np.eye(len(basis)) - step * linear + step**2 * quadratic
        initial_original = np.array([0.7, -0.4, 1.1])
        initial = scales * initial_original
        first = updates @ initial
        second = np.einsum("bij,cj->bci", updates, first)
        second_weights = weights[:, None] * weights[None, :]
        enumerated = np.einsum("bc,bci,bcj->ij", second_weights, second, second)
        initial_coordinates = np.einsum("aij,i,j->a", basis, initial, initial)
        formula = np.einsum(
            "a,aij->ij", operator @ operator @ initial_coordinates, basis
        )
        np.testing.assert_allclose(formula, enumerated, atol=2e-13)
        # Direct original-coordinate updates verify the fixed change of coordinates.
        original_updates = updates * scales[None, None, :] / scales[None, :, None]
        original_first = original_updates @ initial_original
        original_second = np.einsum("bij,cj->bci", original_updates, original_first)
        original_moment = np.einsum(
            "bc,bci,bcj->ij", second_weights, original_second, original_second
        )
        np.testing.assert_allclose(
            original_moment, formula / np.outer(scales, scales), atol=2e-12
        )
        noise_scale = 0.3
        noisy_support = [
            (row, sign * noise_scale, p / 2)
            for row, p in zip(z, probabilities)
            for sign in [-1, 1]
        ]
        noisy_next = np.zeros((3, 3))
        for left, right in itertools.product(noisy_support, repeat=2):
            rows = np.array([left[0], right[0]])
            errors = np.array([left[1], right[1]])
            batch_hessian = rows.T @ rows / 2
            score = rows.T @ errors / 2
            next_error = (np.eye(3) - step * batch_hessian) @ initial + step * score
            noisy_next += left[2] * right[2] * np.outer(next_error, next_error)
        forcing = step**2 * noise_scale**2 * hessian / 2
        one_step = (
            np.einsum("a,aij->ij", operator @ initial_coordinates, basis) + forcing
        )
        np.testing.assert_allclose(noisy_next, one_step, atol=2e-13)
        forcing_coordinates = np.einsum("aij,ij->a", basis, forcing)
        floor_coordinates = np.linalg.solve(
            np.eye(len(basis)) - operator, forcing_coordinates
        )
        floor = np.einsum("a,aij->ij", floor_coordinates, basis)
        direct_floor_update = np.einsum(
            "b,bij,jk,bkl->il", weights, updates, floor, updates
        )
        np.testing.assert_allclose(direct_floor_update + forcing, floor, atol=2e-13)
        assert np.linalg.eigvalsh(floor).min() > 0
        largest_error = max(largest_error, float(np.max(abs(formula - enumerated))))
    return largest_error


def check_mixed_moments():
    largest_error = 0.0
    p = 0.3
    for q in [0.1, 0.01, 1e-4, 1e-6]:
        cells = np.array([[0, 0], [1, 0], [1, 1]], dtype=float)
        probabilities = np.array([1 - p, p - q, q])
        scaled = (cells - [p, q]) / np.sqrt([p * (1 - p), q * (1 - q)])
        mixed = probabilities @ (scaled[:, 0] * scaled[:, 1] ** 3)
        formula = (
            (1 - p)
            * ((1 - q) ** 3 + q**3)
            / (np.sqrt(p * (1 - p)) * np.sqrt(q) * (1 - q) ** 1.5)
        )
        np.testing.assert_allclose(mixed, formula, rtol=2e-13)
        largest_error = max(largest_error, float(abs(mixed - formula)))
        if q == 1e-6:
            even_mixed = probabilities @ (scaled[:, 0] ** 2 * scaled[:, 1] ** 2)
            np.testing.assert_allclose(even_mixed, (1 - p) / p, rtol=2e-6)
    return largest_error


def check_scalar_rates():
    largest_error = 0.0
    for q, batch_size in itertools.product([0.001, 0.03, 0.2], [1, 4, 32]):
        values = (np.array([0.0, 1.0]) - q) / np.sqrt(q * (1 - q))
        counts = np.arange(batch_size + 1)
        weights = binom.pmf(counts, batch_size, q)
        hessians = (
            counts * values[1] ** 2 + (batch_size - counts) * values[0] ** 2
        ) / batch_size
        fourth = (1 - q) * values[0] ** 4 + q * values[1] ** 4
        second = 1 + (fourth - 1) / batch_size
        optimal = 1 / second
        enumerated = weights @ (1 - optimal * hessians) ** 2
        expected = 1 - optimal
        np.testing.assert_allclose(enumerated, expected, atol=2e-13)
        for multiple in [0.8, 1.2]:
            assert weights @ (1 - multiple * optimal * hessians) ** 2 > enumerated
        exponent = np.log1p(batch_size / (fourth - 1)) / batch_size
        np.testing.assert_allclose(np.exp(-batch_size * exponent), enumerated)
        largest_error = max(largest_error, float(abs(enumerated - expected)))
    for regime in ["small", "intermediate", "large"]:
        relative_errors = []
        for q in [1e-3, 1e-5, 1e-7]:
            batch_size = {
                "small": 1,
                "intermediate": round(2 / q),
                "large": round(q**-1.5),
            }[regime]
            fourth = ((1 - q) ** 3 + q**3) / (q * (1 - q))
            second = 1 + (fourth - 1) / batch_size
            rate = np.log1p(batch_size / (fourth - 1)) / batch_size
            targets = {
                "small": (batch_size * q, q),
                "intermediate": (2 / 3, q * np.log(3) / 2),
                "large": (1, np.log(batch_size * q) / batch_size),
            }[regime]
            relative_errors.append(
                max(abs((1 / second) / targets[0] - 1), abs(rate / targets[1] - 1))
            )
        assert relative_errors[-1] < relative_errors[0] / 50
        assert relative_errors[-1] < 4e-4
    return largest_error


def check_block_orders():
    threshold_ratios = []
    limit_errors = {}
    regimes = [
        "small_fixed",
        "small_growing",
        "gamma_0.4",
        "gamma_2",
        "gamma_10",
        "large",
    ]
    for dependence in ["independent", "nested", "disjoint"]:
        for q in [1e-2, 1e-4, 1e-6]:
            z, probabilities, _ = binary_support(q, dependence)
            for regime in regimes:
                batch_size = {
                    "small_fixed": 1,
                    "small_growing": round(q**-0.5),
                    "gamma_0.4": round(0.4 / q),
                    "gamma_2": round(2 / q),
                    "gamma_10": round(10 / q),
                    "large": round(q**-1.5),
                }[regime]
                hessian, linear, quadratic, basis, critical, sufficient, necessary = (
                    support_operators(z, probabilities, batch_size)
                )
                assert sufficient <= critical + 1e-10 <= necessary + 2e-10
                threshold_ratios.append(critical / min(1, batch_size * q))
                common_maximum = np.linalg.eigvalsh(hessian[:-1, :-1])[-1]
                if regime.startswith("small"):
                    target = 2 * batch_size * q
                elif regime.startswith("gamma"):
                    gamma = float(regime.split("_")[1])
                    target = min(2 / common_maximum, 2 * gamma / (1 + gamma))
                else:
                    target = 2 / max(1, common_maximum)
                limit_errors.setdefault((dependence, regime), []).append(
                    abs(critical / target - 1)
                )
                if regime.startswith("small"):
                    step = 0.5 * critical
                    assert step <= necessary
                    initial = np.array([1.0, -0.3, 0.0])
                    updates = 7
                    mean = (
                        np.linalg.matrix_power(np.eye(3) - step * hessian, updates)
                        @ initial
                    )
                    bound = (
                        updates
                        * step
                        * np.linalg.norm(hessian, 2)
                        * np.linalg.norm(initial)
                    )
                    assert np.linalg.norm(mean[:-1] - initial[:-1]) <= bound + 1e-12
                    operator = np.eye(len(basis)) - step * linear + step**2 * quadratic
                    assert np.linalg.eigvalsh(operator)[-1] < 1
    assert min(threshold_ratios) > 0.8
    assert max(threshold_ratios) < 2.1
    for errors in limit_errors.values():
        assert errors[-1] < 4e-3
        assert errors[-1] < errors[0] / 20
    return [float(min(threshold_ratios)), float(max(threshold_ratios))]


def main():
    assert __debug__, "Run without -O: these checks depend on assertions."
    operator_error, scalar_threshold_ratio = check_enumerated_operators()
    summary = {
        "batch_operator_max_error": operator_error,
        "smallest_matrix_to_scalar_threshold_ratio": scalar_threshold_ratio,
        "trajectory_max_error": check_trajectories_and_noise(),
        "mixed_fourth_moment_max_error": check_mixed_moments(),
        "scalar_optimal_factor_max_error": check_scalar_rates(),
        "block_threshold_to_min_1_Bq_range": check_block_orders(),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
