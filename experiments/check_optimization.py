"""Check the elementary gradient-flow and fresh-batch SGD calculations.

Run ordinary Python inside ``devenv shell``; assertions are part of validation.
These deterministic checks write no reference files and are not a comparative
optimizer experiment. Covariances and losses use the manuscript's averaged
convention. Gradient-flow coefficients are reported on the original scale.
"""

import json

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from scipy.stats import binom


def binary_covariance(q1, q2, p11):
    assert 0 < q1 < 1 and 0 < q2 < 1
    assert max(0, q1 + q2 - 1) <= p11 <= min(q1, q2)
    cells = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    probabilities = np.array([1 - q1 - q2 + p11, q2 - p11, q1 - p11, p11])
    centered = cells - np.array([q1, q2])
    covariance = centered.T @ (probabilities[:, None] * centered)
    assert np.linalg.eigvalsh(covariance).min() > 0
    return covariance


def gradient_flow(covariance, score, scales, time):
    generator = covariance / scales[:, None] ** 2
    return (np.eye(len(scales)) - expm(-time * generator)) @ np.linalg.solve(
        covariance, score
    )


def check_flow_coordinates():
    largest_error = 0.0
    for q1, q2, p11 in [(0.5, 0.1, 0.05), (0.5, 0.1, 0.1), (0.5, 0.1, 0.0)]:
        covariance = binary_covariance(q1, q2, p11)
        for signal in [np.array([1.0, 0.0]), np.array([1.0, -0.7])]:
            # A perturbed score checks the empirical formula beyond population flow.
            score = covariance @ signal + np.array([0.02, -0.01])
            for exponent in [0, 0.5, 1]:
                scales = np.diag(covariance) ** exponent
                scaled_covariance = covariance / np.outer(scales, scales)
                scaled_score = score / scales
                times = np.array([0.0, 0.1, 1.0, 3.0])
                ode = solve_ivp(
                    lambda _, theta: scaled_score - scaled_covariance @ theta,
                    (0, times[-1]),
                    np.zeros(2),
                    t_eval=times,
                    rtol=1e-11,
                    atol=1e-13,
                )
                assert ode.success
                original_coefficients = ode.y.T / scales
                closed_form = np.array(
                    [gradient_flow(covariance, score, scales, time) for time in times]
                )
                np.testing.assert_allclose(
                    closed_form, original_coefficients, rtol=1e-9, atol=1e-10
                )
                largest_error = max(
                    largest_error,
                    float(np.max(abs(closed_form - original_coefficients))),
                )
                slowest_rate = np.linalg.eigvalsh(scaled_covariance).min()
                converged = gradient_flow(covariance, score, scales, 40 / slowest_rate)
                np.testing.assert_allclose(
                    converged, np.linalg.solve(covariance, score), atol=1e-10
                )
    return largest_error


def check_rare_flow():
    largest_final_error = 0.0
    times = np.linspace(0, 5, 21)
    for q1 in [0.3, 0.5]:
        for dependence in ["independent", "nested", "disjoint"]:
            kappa = {"independent": 0, "nested": 1 - q1, "disjoint": -q1}[dependence]
            for signal in [np.array([1.0, 0.0]), np.array([1.0, -0.7])]:
                limit = (1 - np.exp(-times[:, None])) * signal
                limit[:, 1] += kappa * times * np.exp(-times) * signal[0]
                errors = []
                for q2 in [1e-2, 1e-4, 1e-6]:
                    p11 = {"independent": q1 * q2, "nested": q2, "disjoint": 0}[
                        dependence
                    ]
                    covariance = binary_covariance(q1, q2, p11)
                    scales = np.sqrt(np.diag(covariance))
                    coefficients = np.array(
                        [
                            gradient_flow(covariance, covariance @ signal, scales, time)
                            for time in times
                        ]
                    )
                    errors.append(float(np.max(abs(coefficients - limit))))
                assert errors[-1] < 2e-6
                if dependence != "independent":
                    assert errors[1] < errors[0] / 50
                    assert errors[2] < errors[1] / 50
                largest_final_error = max(largest_final_error, errors[-1])
    return largest_final_error


def check_batch_stability():
    largest_error = 0.0
    for q in [1e-4, 0.01, 0.1, 0.5, 0.9]:
        values = (np.array([0.0, 1.0]) - q) / np.sqrt(q * (1 - q))
        probabilities = np.array([1 - q, q])
        fourth_moment = ((1 - q) ** 3 + q**3) / (q * (1 - q))
        np.testing.assert_allclose(probabilities @ values**2, 1)
        np.testing.assert_allclose(probabilities @ values**4, fourth_moment)
        for batch_size in [1, 8, 128]:
            counts = np.arange(batch_size + 1)
            batch_probabilities = binom.pmf(counts, batch_size, q)
            hessians = (
                counts * values[1] ** 2 + (batch_size - counts) * values[0] ** 2
            ) / batch_size
            second_moment = 1 + (fourth_moment - 1) / batch_size
            critical_step = 2 / second_moment
            # Enumerating batch counts checks the moment formula at both sides
            # of the stability boundary without unreliable rare-event Monte Carlo.
            for multiple in [0.5, 1.0, 1.1]:
                step = multiple * critical_step
                factors = (1 - step * hessians) ** 2
                enumerated = batch_probabilities @ factors
                formula = 1 - 2 * step + step**2 * second_moment
                np.testing.assert_allclose(enumerated, formula, atol=1e-12)
                if multiple < 1:
                    assert enumerated < 1
                elif multiple > 1:
                    assert enumerated > 1
                largest_error = max(largest_error, float(abs(enumerated - formula)))
    return largest_error


def main():
    assert __debug__, "Run without -O: these checks depend on assertions."
    summary = {
        "flow_ode_max_error": check_flow_coordinates(),
        "rare_flow_max_error_at_q_1e_minus_6": check_rare_flow(),
        "batch_second_moment_max_error": check_batch_stability(),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
