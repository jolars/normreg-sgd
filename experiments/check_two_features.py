"""Check the two-feature weighted elastic-net formulas by independent methods.

Run with numpy and scipy installed (for example, inside ``devenv shell``):
    python experiments/check_two_features.py
    python experiments/check_two_features.py --draws 20000 --check-only

The objective is b'G b / 2 - z'b + lambda1 * w'|b|
                 + lambda2 * b'diag(v)b / 2,
where z ~ N(G beta, sigma**2 G). All coefficients are on the original scale.
Here G = X'X = n C is the unaveraged Gram matrix, whereas the manuscript
uses C = X'X / n and t = lambda1 / n. Its ridge parameter is lambda2 / n.
The simulation cases use v = w**2, corresponding to transforming each feature
by dividing it by its associated w before applying an ordinary elastic-net penalty.

The default JSON destination is relative to the repository root, independent
of the working directory. The --check-only flag leaves reference results alone.
"""

import argparse
import json
import platform
from functools import partial
from itertools import product
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad, quad_vec
from scipy.special import ndtr

SEED = 20260914
DEFAULT_DRAWS = 200_000
SIGNS = tuple(product((-1, 0, 1), repeat=2))
SQRT_2PI = np.sqrt(2 * np.pi)


def soft(value, threshold):
    return np.sign(value) * np.maximum(np.abs(value) - threshold, 0)


def region(hessian, thresholds, signs):
    """Return b = M z + r and the KKT halfspaces A z <= d."""
    signs = np.asarray(signs)
    active = np.flatnonzero(signs)
    matrix = np.zeros((2, 2))
    offset = np.zeros(2)
    if len(active):
        inverse = np.linalg.inv(hessian[np.ix_(active, active)])
        matrix[np.ix_(active, active)] = inverse
        offset[active] = -inverse @ (thresholds[active] * signs[active])
    rows, bounds = [], []
    for j in range(2):
        if signs[j]:
            rows.append(-signs[j] * matrix[j])
            bounds.append(signs[j] * offset[j])
        else:
            residual_row = np.eye(2)[j] - hessian[j] @ matrix
            residual_offset = -hessian[j] @ offset
            rows.extend((residual_row, -residual_row))
            bounds.extend(
                (thresholds[j] - residual_offset, thresholds[j] + residual_offset)
            )
    return matrix, offset, np.asarray(rows), np.asarray(bounds)


def exact_solution(scores, hessian, thresholds):
    scores = np.atleast_2d(scores)
    estimates = np.zeros_like(scores)
    labels = np.full(len(scores), -1, dtype=int)
    for label, signs in enumerate(SIGNS):
        matrix, offset, rows, bounds = region(hessian, thresholds, signs)
        inside = np.all(scores @ rows.T <= bounds + 1e-11, axis=1)
        estimates[inside] = scores[inside] @ matrix.T + offset
        labels[inside] = label
    assert np.all(labels >= 0), "The nine KKT regions must cover score space."
    return estimates, labels


def coordinate_descent(scores, hessian, thresholds):
    estimates = np.zeros_like(scores)
    for iteration in range(100_000):
        previous = estimates.copy()
        for j in range(2):
            k = 1 - j
            estimates[:, j] = (
                soft(scores[:, j] - hessian[j, k] * estimates[:, k], thresholds[j])
                / hessian[j, j]
            )
        if np.max(np.abs(estimates - previous)) < 1e-13:
            return estimates, iteration + 1
    raise AssertionError("Coordinate descent did not converge.")


def selection_probability(j, gram, hessian, thresholds, mean, sigma):
    k = 1 - j
    marginal_sd = sigma * np.sqrt(gram[k, k])
    conditional_sd = sigma * np.sqrt(gram[j, j] - gram[j, k] ** 2 / gram[k, k])

    def integrand(x):
        other_score = mean[k] + marginal_sd * x
        restricted = soft(other_score, thresholds[k]) / hessian[k, k]
        conditional_mean = mean[j] + gram[j, k] / gram[k, k] * (other_score - mean[k])
        residual_mean = conditional_mean - gram[j, k] * restricted
        probability = ndtr((-thresholds[j] - residual_mean) / conditional_sd)
        probability += ndtr((residual_mean - thresholds[j]) / conditional_sd)
        return probability * np.exp(-x * x / 2) / SQRT_2PI

    knots = [
        -np.inf,
        *sorted((np.array([-1, 1]) * thresholds[k] - mean[k]) / marginal_sd),
        np.inf,
    ]
    values = [
        quad(integrand, left, right, epsabs=2e-11, epsrel=2e-11)
        for left, right in zip(knots[:-1], knots[1:])
    ]
    return sum(value for value, _ in values), sum(error for _, error in values)


def integrate_region(gram, mean, sigma, rows, bounds):
    """Integrate P, E[z 1_R], and E[zz' 1_R] using normal truncation."""
    marginal_sd = sigma * np.sqrt(gram[0, 0])
    conditional_sd = sigma * np.sqrt(gram[1, 1] - gram[1, 0] ** 2 / gram[0, 0])
    lower, upper = [], []
    left, right = -np.inf, np.inf
    for row, bound in zip(rows, bounds):
        if abs(row[1]) < 1e-13:
            if abs(row[0]) < 1e-13:
                assert bound >= -1e-13
                continue
            cutoff = (bound / row[0] - mean[0]) / marginal_sd
            if row[0] > 0:
                right = min(right, cutoff)
            else:
                left = max(left, cutoff)
        else:
            line = (-row[0] * marginal_sd / row[1], (bound - row[0] * mean[0]) / row[1])
            (upper if row[1] > 0 else lower).append(line)
    if left >= right:
        return np.zeros(6), 0.0

    # Splitting at line intersections prevents quadrature from skipping thin regions.
    knots = [left, right]
    lines = lower + upper
    for i, (slope, intercept) in enumerate(lines):
        for other_slope, other_intercept in lines[i + 1 :]:
            if abs(slope - other_slope) > 1e-13:
                crossing = (other_intercept - intercept) / (slope - other_slope)
                if left < crossing < right:
                    knots.append(crossing)
    knots = sorted(set(knots))

    def integrand(x):
        z1 = mean[0] + marginal_sd * x
        conditional_mean = mean[1] + gram[1, 0] / gram[0, 0] * (z1 - mean[0])
        low = max(
            (slope * x + intercept for slope, intercept in lower), default=-np.inf
        )
        high = min(
            (slope * x + intercept for slope, intercept in upper), default=np.inf
        )
        if low >= high:
            return np.zeros(6)
        alpha = (low - conditional_mean) / conditional_sd
        omega = (high - conditional_mean) / conditional_sd
        probability = (
            ndtr(-alpha) - ndtr(-omega) if alpha > 0 else ndtr(omega) - ndtr(alpha)
        )
        phi_alpha = np.exp(-alpha * alpha / 2) / SQRT_2PI
        phi_omega = np.exp(-omega * omega / 2) / SQRT_2PI
        density_difference = phi_alpha - phi_omega
        boundary_term = (alpha * phi_alpha if np.isfinite(alpha) else 0) - (
            omega * phi_omega if np.isfinite(omega) else 0
        )
        first = conditional_mean * probability + conditional_sd * density_difference
        second = (conditional_mean**2 + conditional_sd**2) * probability
        second += 2 * conditional_mean * conditional_sd * density_difference
        second += conditional_sd**2 * boundary_term
        values = np.array(
            [
                probability,
                z1 * probability,
                first,
                z1**2 * probability,
                z1 * first,
                second,
            ]
        )
        return values * np.exp(-x * x / 2) / SQRT_2PI

    integral, error = np.zeros(6), 0.0
    for start, end in zip(knots[:-1], knots[1:]):
        value, interval_error = quad_vec(
            integrand, start, end, epsabs=1e-9, epsrel=1e-10
        )
        integral += value
        error += interval_error
    return integral, error


def moments(gram, hessian, thresholds, mean, sigma):
    probabilities, first, second = [], np.zeros(2), np.zeros((2, 2))
    quadrature_error = 0.0
    for signs in SIGNS:
        matrix, offset, rows, bounds = region(hessian, thresholds, signs)
        integral, error = integrate_region(gram, mean, sigma, rows, bounds)
        probability, score_mean = integral[0], integral[1:3]
        score_second = np.array(
            [[integral[3], integral[4]], [integral[4], integral[5]]]
        )
        affine_mean = matrix @ score_mean
        first += affine_mean + offset * probability
        second += matrix @ score_second @ matrix.T
        second += np.outer(affine_mean, offset) + np.outer(offset, affine_mean)
        second += np.outer(offset, offset) * probability
        probabilities.append(probability)
        quadrature_error += error
    covariance = second - np.outer(first, first)
    return np.array(probabilities), first, covariance, quadrature_error


def check_case(
    rng,
    name,
    covariance,
    beta,
    weights,
    draws,
    cd_draws,
    lambda1=10,
    lambda2=0,
    n=100,
    sigma=1,
):
    gram = n * np.asarray(covariance, dtype=float)
    beta, weights = np.asarray(beta, dtype=float), np.asarray(weights, dtype=float)
    hessian = gram + lambda2 * np.diag(weights**2)
    thresholds = lambda1 * weights
    mean = gram @ beta
    scores = rng.multivariate_normal(mean, sigma**2 * gram, size=draws)
    estimates, labels = exact_solution(scores, hessian, thresholds)
    cd_estimates, iterations = coordinate_descent(
        scores[:cd_draws], hessian, thresholds
    )
    solver_error = np.max(np.abs(estimates[:cd_draws] - cd_estimates))
    assert solver_error < 1e-9
    selection = np.array(
        [
            selection_probability(j, gram, hessian, thresholds, mean, sigma)[0]
            for j in range(2)
        ]
    )
    probabilities, exact_mean, exact_covariance, integration_error = moments(
        gram, hessian, thresholds, mean, sigma
    )
    selected_by_region = np.array(probabilities) @ (np.array(SIGNS) != 0)
    assert abs(probabilities.sum() - 1) < 1e-8
    assert np.max(np.abs(selection - selected_by_region)) < 1e-8
    mc_selection = np.mean(estimates != 0, axis=0)
    selection_se = np.sqrt(selection * (1 - selection) / draws)
    assert np.all(np.abs(mc_selection - selection) <= 6 * selection_se + 2 / draws)
    mc_mean, mc_covariance = estimates.mean(axis=0), np.cov(estimates, rowvar=False)
    mean_se = np.sqrt(np.diag(exact_covariance) / draws)
    assert np.all(np.abs(mc_mean - exact_mean) <= 6 * mean_se)
    centered = estimates - exact_mean
    covariance_se = np.std(centered[:, :, None] * centered[:, None, :], axis=0)
    covariance_se /= np.sqrt(draws)
    assert np.all(np.abs(mc_covariance - exact_covariance) <= 6 * covariance_se)
    return {
        "name": name,
        "n": n,
        "sigma": sigma,
        "gram": gram.tolist(),
        "beta": beta.tolist(),
        "weights": weights.tolist(),
        "ridge_weights": (weights**2).tolist(),
        "lambda1": lambda1,
        "lambda2": lambda2,
        "solver_max_absolute_difference": float(solver_error),
        "coordinate_descent_iterations": iterations,
        "selection_quadrature": selection.tolist(),
        "selection_from_regions": selected_by_region.tolist(),
        "selection_monte_carlo": mc_selection.tolist(),
        "selection_monte_carlo_standard_error": selection_se.tolist(),
        "region_probabilities": probabilities.tolist(),
        "region_frequencies": (np.bincount(labels, minlength=9) / draws).tolist(),
        "region_integral_error_estimate": float(integration_error),
        "mean_quadrature": exact_mean.tolist(),
        "mean_monte_carlo": mc_mean.tolist(),
        "mean_monte_carlo_standard_error": mean_se.tolist(),
        "covariance_quadrature": exact_covariance.tolist(),
        "covariance_monte_carlo": mc_covariance.tolist(),
        "covariance_monte_carlo_standard_error": covariance_se.tolist(),
        "noiseless_solution": exact_solution(mean, hessian, thresholds)[0][0].tolist(),
    }


def check_deterministic_examples():
    """Check the binary single-signal result and ridge-dependent selection."""
    t, n = 0.1, 100
    signals = np.array([-1, -0.1, -0.05, 0, 0.05, 0.1, 1])
    beta = np.concatenate(
        [
            np.column_stack((signals, np.zeros_like(signals))),
            np.column_stack((np.zeros_like(signals), signals)),
        ]
    )
    expected = soft(beta, t)
    max_error, designs = 0.0, 0
    for q1, q2 in product((0.1, 0.3, 0.5, 0.8), repeat=2):
        lower, upper = max(0, q1 + q2 - 1), min(q1, q2)
        for joint in np.linspace(lower, upper, 5):
            covariance = np.array(
                [[q1 * (1 - q1), joint - q1 * q2], [joint - q1 * q2, q2 * (1 - q2)]]
            )
            # Singular boundary designs do not have a unique lasso minimizer.
            if np.linalg.eigvalsh(covariance)[0] < 1e-12:
                continue
            gram = n * covariance
            thresholds = n * t * covariance.diagonal()
            estimates, _ = exact_solution(beta @ gram, gram, thresholds)
            error = float(np.max(np.abs(estimates - expected)))
            max_error = max(max_error, error)
            assert error < 1e-10
            designs += 1

    gram = np.array([[1, 0.8], [0.8, 1]])
    scores = np.array([0.8, 1.0])
    thresholds = np.array([0.2, 0.2])
    lasso = exact_solution(scores, gram, thresholds)[0][0]
    elastic_net = exact_solution(scores, gram + np.eye(2), thresholds)[0][0]
    np.testing.assert_allclose(lasso, [0, 0.8], atol=1e-12, rtol=0)
    np.testing.assert_allclose(elastic_net, [1 / 6, 1 / 3], atol=1e-12, rtol=0)
    return {
        "binary_single_signal": {
            "positive_definite_designs": designs,
            "coefficient_vectors_per_design": len(beta),
            "t": t,
            "n": n,
            "max_absolute_difference_from_soft_thresholding": max_error,
        },
        "ridge_induced_selection": {
            "gram": gram.tolist(),
            "scores": scores.tolist(),
            "lambda1": 0.2,
            "weights": [1, 1],
            "lasso_solution": lasso.tolist(),
            "elastic_net_lambda2": 1,
            "elastic_net_solution": elastic_net.tolist(),
        },
    }


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--draws",
        type=int,
        default=DEFAULT_DRAWS,
        help="Monte Carlo draws per case (at least 1,000; default: 200,000).",
    )
    parser.add_argument(
        "--cd-draws",
        type=int,
        help="Draws checked by coordinate descent (default: min(5,000, draws)).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/two-feature-check.json"),
        help="JSON destination, relative to the repository root unless absolute.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run all checks without writing a result file.",
    )
    args = parser.parse_args()
    if args.draws < 1000:
        parser.error("--draws must be at least 1,000 for the Monte Carlo checks.")
    if args.cd_draws is None:
        args.cd_draws = min(5000, args.draws)
    if not 1 <= args.cd_draws <= args.draws:
        parser.error("--cd-draws must be between 1 and --draws.")
    return args


def main():
    args = parse_args()
    rng = np.random.default_rng(SEED)
    run_case = partial(check_case, rng, draws=args.draws, cd_draws=args.cd_draws)
    binary_covariance = [[0.25, 0.05], [0.05, 0.09]]
    cases = [
        run_case(
            "binary_variance_lasso_same_sign", binary_covariance, [1, 1], [0.25, 0.09]
        ),
        run_case(
            "binary_variance_lasso_opposite_sign",
            binary_covariance,
            [1, -1],
            [0.25, 0.09],
        ),
        run_case(
            "binary_std_elastic_net",
            binary_covariance,
            [0.3, -0.4],
            [0.5, 0.3],
            lambda2=30,
        ),
        run_case(
            "negative_correlation_elastic_net",
            [[1, -0.7], [-0.7, 1]],
            [0.2, 0.1],
            [1, 1],
            lambda1=15,
            lambda2=10,
        ),
        run_case("high_correlation_lasso", [[1, 0.95], [0.95, 1]], [0.2, -0.1], [1, 1]),
        run_case(
            "orthogonal_elastic_net",
            [[0.25, 0], [0, 0.09]],
            [0.4, 0.2],
            [0.25, 0.09],
            lambda2=30,
        ),
    ]
    np.testing.assert_allclose(
        cases[0]["noiseless_solution"], [0.91, 0.95], atol=1e-12, rtol=0
    )
    np.testing.assert_allclose(
        cases[1]["noiseless_solution"], [0.865, -0.825], atol=1e-12, rtol=0
    )
    deterministic_examples = check_deterministic_examples()
    result = {
        "seed": SEED,
        "monte_carlo_draws_per_case": args.draws,
        "coordinate_descent_draws_per_case": args.cd_draws,
        "software_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameterization": {
            "gram": "G = X.T @ X = n * C",
            "score_distribution": "N(G @ beta, sigma**2 * G)",
            "averaged_lasso_penalty": "t = lambda1 / n",
            "averaged_ridge_penalty": "lambda2 / n",
            "ridge_weights": "v = weights**2",
            "coefficient_scale": "original",
        },
        "sign_pattern_order": SIGNS,
        "checks_passed": True,
        "checks": [
            "Nine-region solution equals independent coordinate descent.",
            "Region probabilities sum to one.",
            "Residual-tail and region selection integrals agree.",
            "Selection probabilities, means, and covariances agree with Monte Carlo "
            "within six standard errors (with a two-draw allowance for selection).",
            "Binary noiseless same-sign and opposite-sign examples match the algebra.",
            "Variance-scaled binary single-signal solutions equal soft thresholding.",
            "A ridge penalty changes the selected support in a correlated design.",
        ],
        "deterministic_examples": deterministic_examples,
        "cases": cases,
    }
    destination = None
    if not args.check_only:
        destination = args.output
        if not destination.is_absolute():
            destination = Path(__file__).resolve().parents[1] / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "checks_passed": True,
                "check_only": args.check_only,
                "result_file": str(destination) if destination else None,
                "cases": len(cases),
                "monte_carlo_draws_per_case": args.draws,
                "coordinate_descent_draws_per_case": args.cd_draws,
                "max_solver_error": max(
                    case["solver_max_absolute_difference"] for case in cases
                ),
                "deterministic_examples": deterministic_examples,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
