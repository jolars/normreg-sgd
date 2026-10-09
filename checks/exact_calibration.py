"""Check expected-risk calibration by path enumeration and baseline moments."""

import json
from itertools import product

import numpy as np
from numpy.testing import assert_allclose

from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.exact_calibration import ARMS, expected_risks


def enumerated_risks(q, factors, signals, fit_intercept):
    """Enumerate short raw-coordinate SGD paths, including observation noise."""
    cells = np.array(list(product((0.0, 1.0), repeat=2)))
    probability = np.array([(1 - q) / 2, q / 2, (1 - q) / 2, q / 2])
    centered = cells - [0.5, q]
    design = np.column_stack((np.ones(4), centered))
    result = np.zeros((4, 2, len(signals), len(factors), 2))
    for scaling, signal, rate in np.ndindex(2, len(signals), len(factors)):
        variance = np.array([0.25, q * (1 - q)]) if scaling else np.ones(2)
        bound = np.max(np.sum(centered**2 / variance, axis=1)) + fit_intercept
        eta = factors[rate] / bound
        steps = eta * np.r_[float(fit_intercept), 1 / variance]
        truth = centered @ signals[signal]
        paths = [(1.0, np.zeros(3))]
        for stop in range(4):
            for weight, coefficients in paths:
                loss = 0.5 * (design @ coefficients - truth) ** 2
                result[stop, scaling, signal, rate] += weight * np.array(
                    [probability @ loss, loss[[1, 3]].mean()]
                )
            if stop == 3:
                break
            next_paths = []
            for weight, coefficients in paths:
                for cell, noise in product(range(4), (-1.0, 1.0)):
                    # Symmetric two-point noise has the Gaussian's first two
                    # moments, which suffice for the expected quadratic loss.
                    residual = design[cell] @ coefficients - truth[cell] - noise
                    updated = coefficients - steps * design[cell] * residual
                    next_paths.append((weight * probability[cell] / 2, updated))
            paths = next_paths
    return result


def check_enumeration():
    factors = np.array([0.0, 0.37, 1.9])
    signals = np.array([[0.1, 1.0], [1.0, 0.1], [-0.4, 0.8]])
    for q, fit_intercept in product((0.02, 0.005, 0.5), (False, True)):
        expected = enumerated_risks(q, factors, signals, fit_intercept)
        actual, _ = expected_risks(q, factors, np.arange(4), signals, fit_intercept)
        assert_allclose(actual, expected, rtol=2e-13, atol=2e-14)
    print("Full second moments agree with exhaustive three-step SGD paths.")


def check_saved():
    settings = json.loads((cfg.OUTPUT / "settings.json").read_text())
    report = json.loads((cfg.OUTPUT / "exact-calibration.json").read_text())
    assert report["arms"] == list(ARMS)
    arm_ids = [settings["arms"].index(arm) for arm in ARMS]
    comparisons = 0
    with np.load(cfg.OUTPUT / "exact-calibration.npz") as benchmark:
        for q_id, run in enumerate(settings["runs"]):
            profile = benchmark[f"q{q_id}_expected_risk"]
            fixed = benchmark[f"q{q_id}_calibrated"]
            optimal = benchmark[f"q{q_id}_optimal"]
            with np.load(cfg.OUTPUT / f"q{q_id}-calibration.npz") as calibration:
                # The study's baseline used a separate two-coordinate recurrence.
                assert_allclose(
                    profile[:, 0], calibration["exact_baseline"], rtol=3e-12, atol=1e-14
                )
                np.testing.assert_array_equal(
                    fixed, np.take(calibration["fixed"][..., 0, :], arm_ids, axis=1)
                )
            np.testing.assert_array_equal(optimal[:, 0], fixed[:, 0])
            for cap, arm, scaling, signal in np.ndindex(*optimal.shape[:-1]):
                risk = profile[:, arm, scaling, signal, :, 1]
                eligible = np.asarray(run["checkpoints"]) <= run["caps"][cap]
                chosen = tuple(optimal[cap, arm, scaling, signal])
                calibrated = tuple(fixed[cap, arm, scaling, signal])
                assert eligible[chosen[0]] and eligible[calibrated[0]]
                assert risk[chosen] == risk[eligible].min()
                assert risk[calibrated] >= risk[chosen]
                comparisons += 1
    print(f"Saved baseline moments and {comparisons} finite-family optima verified.")


def main():
    check_enumeration()
    check_saved()


if __name__ == "__main__":
    main()
