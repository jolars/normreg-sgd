"""Screen a proposed risk approximation without certifying the proposed theorem.

The surrogate removes rare-error feedback into the common-coordinate update.
Checks compare its scalar recurrences with enumerated batch updates, and compare
the exact dynamics with the existing four-moment implementation. No frozen
study or reference artifact is rewritten.
"""

import itertools

import numpy as np
from robustness_spec import model
from run_joint_interactions import moment_path


def recurrence(q, dependence, common, rare, batch):
    """Return the exact and surrogate second-moment maps and unit-noise input."""
    a, b, c = 0.25, q * (1 - q), q * dependence / 2
    dc, dr = common / a, rare / b
    cross_square = c**2 + (a * b - c**2) / batch
    mixed = c * (b + (1 - 4 * b) / batch)
    surrogate = np.array(
        [
            [(1 - common) ** 2, 0, 0],
            [-dr * (1 - common) * c, (1 - common) * (1 - rare), 0],
            [
                dr**2 * cross_square,
                -2 * dr * c + 2 * dr**2 * mixed,
                (1 - rare) ** 2 + dr**2 * b * (1 - 4 * b) / batch,
            ],
        ]
    )
    exact = surrogate.copy()
    exact[0, 1] = -2 * dc * (1 - common) * c
    exact[0, 2] = dc**2 * cross_square
    exact[1, 1] += dc * dr * cross_square
    exact[1, 2] = -dc * c + dc * dr * mixed
    injection = np.array([dc**2 * a, dc * dr * c, dr**2 * b]) / batch
    return exact, surrogate, injection


def parts(transition, injection, signal, count):
    augmented = np.eye(4)
    augmented[:3, :3] = transition
    augmented[:3, 3] = injection
    power = np.linalg.matrix_power(augmented, int(count))
    initial = np.array([signal[0] ** 2, np.prod(signal), signal[1] ** 2])
    return np.column_stack([power[:3, :3] @ initial, power[:3, 3]])


def corrected_parts(exact, surrogate, injection, signal, count):
    augmented = np.eye(7)
    augmented[:3, :3] = surrogate
    augmented[:3, 3:6] = exact - surrogate
    augmented[3:6, 3:6] = surrogate
    augmented[3:6, 6] = injection
    power = np.linalg.matrix_power(augmented, int(count))
    initial = np.array([signal[0] ** 2, np.prod(signal), signal[1] ** 2])
    return np.column_stack(
        [
            (power[:3, 3:6] + power[3:6, 3:6]) @ initial,
            power[:3, 6] + power[3:6, 6],
        ]
    )


def remainder(exact, surrogate, injection, signal, count):
    """Bound the omitted second feedback, separately for signal and noise."""
    augmented = np.eye(10)
    augmented[:3, :3] = abs(exact)
    augmented[:3, 3:6] = abs(exact - surrogate)
    augmented[3:6, 3:6] = abs(surrogate)
    augmented[3:6, 6:9] = abs(exact - surrogate)
    augmented[6:9, 6:9] = abs(surrogate)
    augmented[6:9, 9] = abs(injection)
    power = np.linalg.matrix_power(augmented, int(count))
    initial = np.array([signal[0] ** 2, abs(np.prod(signal)), signal[1] ** 2])
    return np.column_stack([power[:3, 6:9] @ initial, power[:3, 9]])


def weights(q, dependence):
    return 0.5 * np.array(
        [
            [0.25, q * dependence, q * (1 - q)],
            [0.25, dependence * (1 - q), (1 - q) ** 2],
        ]
    )


def check_operators():
    signal = np.array([0.8, -1.1])
    cases, operator_cases = 0, 0
    for q, dependence, batch, exponent in itertools.product(
        [0.002, 0.02, 0.06], [-1, 0, 0.7, 1], [1, 2], [0, 0.25, 0.5]
    ):
        m = model(q, dependence)
        b = q * (1 - q)
        common = min(0.03, b * batch / (4 * b) ** (1 - 2 * exponent))
        rare = common * (4 * b) ** (1 - 2 * exponent)
        exact, surrogate, injection = recurrence(q, dependence, common, rare, batch)
        scales = np.diag(m["gram"]) ** exponent
        step = common * 0.25 ** (2 * exponent - 1)
        counts = [0, 1, 2, 100, 10000]
        full = moment_path(m, scales, step, batch, counts, signal, 1.3)
        for index, count in enumerate(counts):
            calculated = parts(exact, injection, signal, count) @ [1, 1.3]
            expected = full["second"][index][[0, 0, 1], [0, 1, 1]]
            np.testing.assert_allclose(calculated, expected, atol=2e-11, rtol=2e-10)
            difference = abs(
                parts(exact, injection, signal, count)
                - corrected_parts(exact, surrogate, injection, signal, count)
            )
            bound = remainder(exact, surrogate, injection, signal, count)
            assert np.all(difference <= bound + 2e-11 + 2e-10 * difference)
            cases += 1

        # Enumerating batches checks the surrogate as an actual random update,
        # including correlated response-noise inputs, without its moment formula.
        cells = list(itertools.product(range(4), repeat=batch))
        basis = [np.diag([1, 0]), np.array([[0, 1], [1, 0]]), np.diag([0, 1])]
        enumerated, noise = np.zeros((3, 3)), np.zeros(3)
        for indices in cells:
            probability = np.prod(m["probabilities"][list(indices)])
            x = m["x"][list(indices)]
            gram = x.T @ x / batch
            update = np.eye(2) - np.diag([4 * common, rare / b]) @ gram
            update[0, 1] = 0
            for column, matrix in enumerate(basis):
                value = update @ matrix @ update.T
                enumerated[:, column] += probability * value[[0, 0, 1], [0, 1, 1]]
            d = np.diag([4 * common, rare / b])
            value = d @ gram @ d / batch
            noise += probability * value[[0, 0, 1], [0, 1, 1]]
        np.testing.assert_allclose(enumerated, surrogate, atol=2e-15, rtol=2e-13)
        np.testing.assert_allclose(noise, injection, atol=2e-15, rtol=2e-13)
        operator_cases += 1
    print(f"Checked {cases} endpoints and {operator_cases} enumerated batch operators.")


def compare(q, dependence, signal, sigma2, batch, count, plain_rate, scaled_rate):
    exact_risks, proxy_risks, corrected_risks, errors = [], [], [], []
    for common, rare in [
        (plain_rate, 4 * q * (1 - q) * plain_rate),
        (scaled_rate, scaled_rate),
    ]:
        exact, surrogate, injection = recurrence(q, dependence, common, rare, batch)
        assert max(abs(np.linalg.eigvals(exact))) < 1
        exact_risks.append(
            weights(q, dependence)
            @ parts(exact, injection, signal, count)
            @ [1, sigma2]
        )
        proxy_risks.append(
            weights(q, dependence)
            @ parts(surrogate, injection, signal, count)
            @ [1, sigma2]
        )
        corrected_risks.append(
            weights(q, dependence)
            @ corrected_parts(exact, surrogate, injection, signal, count)
            @ [1, sigma2]
        )
        errors.append(
            abs(weights(q, dependence))
            @ remainder(exact, surrogate, injection, signal, count)
            @ [1, sigma2]
        )
    return (
        np.array(exact_risks)[1] - exact_risks[0],
        np.array(proxy_risks)[1] - proxy_risks[0],
        np.array(corrected_risks)[1] - corrected_risks[0],
        np.sum(errors, axis=0),
    )


def screen_comparisons():
    print("Exploratory comparisons; each pair shares B, k, signal, and test law.")
    print("label B k M objective exact_gap leading_gap corrected_gap finite_bound")
    for batch, count in itertools.product([1, 10], [1000, 10000]):
        values = compare(0.02, 0, [1, 1], 3, batch, count, 0.002, 0.002)
        print(
            f"C1-fixed {batch} {count} {batch * count} rare",
            *(f"{v[1]:.9g}" for v in values),
        )
    rows = [
        ("C1-adjusted", 0, [1, 1], 3, 10000, 0.004, 0.0003125),
        ("C2-fixed", 1, [2, 1], 4, 100, 0.01, 0.01),
        ("C2-aggregate-adjusted", 1, [2, 1], 4, 100, 0.02, 0.016),
        ("C2-rare-adjusted", 1, [2, 1], 4, 100, 0.04, 0.008),
    ]
    for label, dependence, signal, sigma2, count, plain, scaled in rows:
        values = compare(0.02, dependence, signal, sigma2, 1, count, plain, scaled)
        for index, objective in enumerate(["aggregate", "rare"]):
            print(
                f"{label} 1 {count} {count} {objective}",
                *(f"{v[index]:.9g}" for v in values),
            )
    print("Beyond the certified boxes: independent law, signal=(1,1), sigma2=3, B=1.")
    print("q calibration k M h_U h_S exact_gap corrected_gap finite_bound")
    for q in [0.006, 0.04, 0.06]:
        b = q * (1 - q)
        common = 0.1 * b
        for calibration, count, scaled in [
            ("early-fixed", round(2 / common), common),
            ("late-fixed", round(0.4 / (common * b)), common),
            (
                "late-S-adjusted",
                round(0.4 / (common * b)),
                3 / round(0.4 / (common * b)),
            ),
        ]:
            values = compare(q, 0, [1, 1], 3, 1, count, common, scaled)
            print(
                q,
                calibration,
                count,
                count,
                common,
                scaled,
                *(f"{values[index][1]:.9g}" for index in [0, 2, 3]),
            )


def screen_rarity():
    print(
        "Development screen, not a proof or held-out test: "
        "corrected error / proposed scale."
    )
    print(
        "q endpoints max_homogeneous_ratio max_noise_ratio "
        "max_bound_signal_ratio max_bound_noise_ratio"
    )
    for q in [0.0625, 0.06, 0.02, 0.006, 0.002, 0.0006]:
        b = q * (1 - q)
        maxima = np.zeros(2)
        bound_maxima = np.zeros(2)
        count_cases = 0
        for dependence, batch, exponent, fraction, signal in itertools.product(
            [-1, 0, 0.7, 1],
            [1, 10, 100],
            [0, 0.25, 0.5],
            [0.1, 0.5, 1],
            [[1, 1], [2, 1], [1, -1], [0, 1]],
        ):
            common = fraction * min(0.25, b * batch / (4 * b) ** (1 - 2 * exponent))
            rare = common * (4 * b) ** (1 - 2 * exponent)
            exact, surrogate, injection = recurrence(q, dependence, common, rare, batch)
            for count in sorted(
                {0, 1, int(1 / common), int(1 / rare), int(10 / rare), int(100 / rare)}
            ):
                difference = abs(
                    weights(q, dependence)
                    @ (
                        parts(exact, injection, signal, count)
                        - corrected_parts(exact, surrogate, injection, signal, count)
                    )
                )
                scale = q**2 * np.array(
                    [
                        np.dot(signal, signal) * np.exp(-count * rare / 4),
                        common / batch + rare / (b * batch),
                    ]
                )
                maxima = np.maximum(maxima, np.max(difference / scale, axis=0))
                bound = abs(weights(q, dependence)) @ remainder(
                    exact, surrogate, injection, signal, count
                )
                bound_maxima = np.maximum(bound_maxima, np.max(bound / scale, axis=0))
                count_cases += 1
        print(q, count_cases, *(f"{v:.6f}" for v in [*maxima, *bound_maxima]))


def main():
    assert __debug__, "Run ordinary Python without -O."
    check_operators()
    screen_comparisons()
    screen_rarity()


if __name__ == "__main__":
    main()
