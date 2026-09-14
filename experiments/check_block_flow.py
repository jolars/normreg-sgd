"""Check common-block population flow using feasible binary support and ODEs.

Run ordinary Python inside ``devenv shell``; assertions are part of validation.
Population centering and scales are known and fixed throughout each trajectory.
All coefficients and deterministic initial values use the original feature scale.
The checks are deterministic and do not write reference results.
"""

import json
from itertools import product

import numpy as np
from scipy.integrate import quad_vec, solve_ivp
from scipy.linalg import expm


def binary_support(common_probabilities, rare_conditional, prevalence):
    """Keep the common marginal law and specify its law given rare presence."""
    common = np.array(list(product([0.0, 1.0], repeat=3)))
    np.testing.assert_allclose(common_probabilities.sum(), 1)
    np.testing.assert_allclose(rare_conditional.sum(), 1)
    assert np.all(common_probabilities > 0)
    assert np.all(rare_conditional >= 0)
    assert 0 < prevalence < 1
    absent = common_probabilities - prevalence * rare_conditional
    assert np.all(absent >= 0), "The full joint binary law must be feasible."
    cells = np.vstack(
        [np.column_stack([common, np.zeros(8)]), np.column_stack([common, np.ones(8)])]
    )
    probabilities = np.concatenate([absent, prevalence * rare_conditional])
    np.testing.assert_allclose(probabilities.sum(), 1)
    means = probabilities @ cells
    centered = cells - means
    covariance = centered.T @ (probabilities[:, None] * centered)
    assert np.linalg.eigvalsh(covariance).min() > 0

    # Conditional means independently check the coupling and centering identity.
    conditional_difference = rare_conditional @ common - absent @ common / (
        1 - prevalence
    )
    np.testing.assert_allclose(
        covariance[:-1, -1] / covariance[-1, -1],
        conditional_difference,
        atol=2e-15,
    )
    return centered, probabilities, covariance


def finite_flow(covariance, scales, signal, initial, times):
    generator = covariance / scales[:, None] ** 2
    return np.array(
        [signal + expm(-time * generator) @ (initial - signal) for time in times]
    )


def support_flow(centered, probabilities, scales, signal, initial, times):
    scaled = centered / scales
    response = centered @ signal

    # Enumerating observation gradients avoids constructing the covariance ODE.
    def gradient(_, theta):
        return scaled.T @ (probabilities * (response - scaled @ theta))

    ode = solve_ivp(
        gradient,
        (0, times[-1]),
        scales * initial,
        t_eval=times,
        method="DOP853",
        rtol=2e-12,
        atol=2e-14 * scales,
    )
    assert ode.success
    return ode.y.T / scales


def spectral_limit(
    common_covariance, common_scales, kappa, rate, signal, initial, times
):
    symmetric = common_covariance / np.outer(common_scales, common_scales)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    assert eigenvalues.min() > 0 and rate >= 0
    deficit = signal - initial
    common_modes = eigenvectors.T @ (common_scales * deficit[:-1])
    transfer_modes = (kappa / common_scales) @ eigenvectors * common_modes
    trajectories = []
    for time in times:
        common = (
            signal[:-1]
            - (eigenvectors @ (np.exp(-eigenvalues * time) * common_modes))
            / common_scales
        )
        # This integral form remains accurate when a common rate equals the rare rate.
        gaps = np.abs(eigenvalues - rate)
        kernels = np.empty_like(gaps)
        repeated = gaps < 1e-14
        kernels[repeated] = time * np.exp(-rate * time)
        kernels[~repeated] = (
            np.exp(-np.minimum(eigenvalues[~repeated], rate) * time)
            * -np.expm1(-gaps[~repeated] * time)
            / gaps[~repeated]
        )
        rare = (
            signal[-1]
            - np.exp(-rate * time) * deficit[-1]
            + rate * (transfer_modes @ kernels)
        )
        trajectories.append(np.append(common, rare))
    return np.array(trajectories)


def convolution_limit(
    common_covariance, common_scales, kappa, rate, signal, initial, times
):
    generator = common_covariance / common_scales[:, None] ** 2
    deficit = signal - initial
    trajectories = []
    for time in times:
        common = signal[:-1] - expm(-time * generator) @ deficit[:-1]
        integral, _ = quad_vec(
            lambda u: (
                np.exp(-rate * (time - u))
                * (kappa @ expm(-u * generator) @ deficit[:-1])
            ),
            0,
            time,
            epsabs=1e-12,
            epsrel=1e-12,
        )
        rare = signal[-1] - np.exp(-rate * time) * deficit[-1] + rate * integral
        trajectories.append(np.append(common, rare))
    return np.array(trajectories)


def common_laws():
    marginal = np.array([0.22, 0.08, 0.06, 0.14, 0.05, 0.10, 0.15, 0.20])
    return marginal, [
        marginal.copy(),
        np.eye(8)[7],
        np.eye(8)[0],
        0.4 * np.eye(8)[2] + 0.6 * np.eye(8)[5],
    ]


def check_support_ode():
    marginal, conditional_laws = common_laws()
    times = np.linspace(0, 6, 41)
    largest_error = 0.0
    for conditional in conditional_laws:
        for prevalence in [0.04, 0.002, 1e-5]:
            centered, probabilities, covariance = binary_support(
                marginal, conditional, prevalence
            )
            for scales in [
                np.sqrt(np.diag(covariance)),
                np.array([0.6, 0.9, 0.7, np.sqrt(covariance[-1, -1] / 1.7)]),
                np.ones(4),
            ]:
                for signal, initial in [
                    (np.array([1.0, -0.4, 0.8, 0.0]), np.zeros(4)),
                    (np.array([-0.2, 0.9, 0.5, -0.7]), np.array([0.3, -0.6, 0.2, 0.4])),
                ]:
                    formula = finite_flow(covariance, scales, signal, initial, times)
                    ode = support_flow(
                        centered, probabilities, scales, signal, initial, times
                    )
                    np.testing.assert_allclose(formula, ode, rtol=2e-9, atol=2e-10)
                    largest_error = max(
                        largest_error, float(np.max(abs(formula - ode)))
                    )
    return largest_error


def check_block_limit():
    marginal, conditional_laws = common_laws()
    common = np.array(list(product([0.0, 1.0], repeat=3)))
    centered_common = common - marginal @ common
    common_covariance = centered_common.T @ (marginal[:, None] * centered_common)
    assert abs(common_covariance[0, 1]) > 0.05
    times = np.linspace(0, 6, 61)
    signal = np.array([1.2, -0.8, 0.3, -0.4])
    initial = np.array([-0.3, 0.2, 0.5, 0.7])
    largest_error = 0.0
    for conditional in conditional_laws:
        kappa = (conditional - marginal) @ common
        for rate in [0.0, 0.7, 1.0, 2.0]:
            common_scales = np.sqrt(np.diag(common_covariance))
            if rate != 1:
                common_scales = np.array([0.6, 0.9, 0.7])
            limit = spectral_limit(
                common_covariance, common_scales, kappa, rate, signal, initial, times
            )
            errors = []
            for prevalence in [1e-2, 1e-4, 1e-6]:
                # Vary covariance, scales, and initialization along the limit.
                marginal_n = (1 - prevalence) * marginal + prevalence / 8
                centered, probabilities, covariance = binary_support(
                    marginal_n, conditional, prevalence
                )
                rare_scale = 1.0 if rate == 0 else np.sqrt(covariance[-1, -1] / rate)
                common_scales_n = (
                    np.sqrt(np.diag(covariance)[:-1])
                    if rate == 1
                    else common_scales * (1 + prevalence * np.array([1.0, -0.5, 0.2]))
                )
                scales = np.append(common_scales_n, rare_scale)
                initial_n = initial + prevalence * np.array([0.2, 0.3, -0.1, 0.4])
                ode = support_flow(
                    centered, probabilities, scales, signal, initial_n, times
                )
                errors.append(float(np.max(abs(ode - limit))))
            assert errors[1] < errors[0] / 50
            assert errors[2] < errors[1] / 50
            assert errors[-1] < 2e-5
            largest_error = max(largest_error, errors[-1])
    return largest_error


def check_convolution_and_resonance():
    covariance = np.array(
        [[0.24, 0.06, -0.02], [0.06, 0.21, 0.03], [-0.02, 0.03, 0.25]]
    )
    scales = np.array([0.7, 0.4, 0.6])
    kappa = np.array([0.3, -0.2, 0.4])
    signal = np.array([0.8, -0.5, 0.2, 0.0])
    initial = np.array([-0.1, 0.2, 0.3, 0.7])
    times = np.linspace(0, 5, 13)
    eigenvalues = np.linalg.eigvalsh(covariance / np.outer(scales, scales))
    largest_error = 0.0
    for rate in [0.0, 1.0, eigenvalues[0], eigenvalues[1] + 1e-10]:
        spectral = spectral_limit(
            covariance, scales, kappa, rate, signal, initial, times
        )
        convolution = convolution_limit(
            covariance, scales, kappa, rate, signal, initial, times
        )
        np.testing.assert_allclose(spectral, convolution, rtol=2e-11, atol=2e-12)
        largest_error = max(largest_error, float(np.max(abs(spectral - convolution))))

    # The scalar common block must recover the existing two-feature proposition.
    signal = np.array([1.2, -0.7])
    kappa = np.array([0.65])
    limit = spectral_limit(
        np.array([[0.35 * 0.65]]),
        np.array([np.sqrt(0.35 * 0.65)]),
        kappa,
        1.0,
        signal,
        np.zeros(2),
        times,
    )
    elementary = (1 - np.exp(-times[:, None])) * signal
    elementary[:, 1] += kappa[0] * times * np.exp(-times) * signal[0]
    np.testing.assert_allclose(limit, elementary, atol=2e-15)
    return largest_error


def main():
    assert __debug__, "Run without -O: these checks depend on assertions."
    summary = {
        "block_flow_support_ode_max_error": check_support_ode(),
        "block_limit_ode_max_error_at_q_1e_minus_6": check_block_limit(),
        "spectral_convolution_max_error": check_convolution_and_resonance(),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
