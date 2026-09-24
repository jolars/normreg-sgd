"""Independent updates, exact risks, and selections for the bridge experiment."""

import argparse
import json
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose

from experiments.common.moments import make_model, moment_path
from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.engine import (
    CELLS,
    choose_fixed,
    exact_baseline,
    parameters,
    predictor_risks,
    sample,
    simulate,
)


def reference_paths(data, q, rep=0):
    """Update transformed coefficients, independently of the production recurrence."""
    factors, checkpoints = cfg.rates(), cfg.stops(q)
    pool = CELLS[data["cells"][rep, : cfg.TRAIN_SIZE]]
    population = np.array([0.5, q])
    empirical_mean = pool.mean(axis=0)
    empirical_variance = pool.var(axis=0)
    result = np.empty((len(checkpoints), len(cfg.ARMS), 2, 2, len(factors), 3))
    for a, arm in enumerate(cfg.ARMS):
        mean = empirical_mean if cfg.ESTIMATE_CENTER[a] else population
        variance = (
            empirical_variance
            if cfg.ESTIMATE_SCALE[a]
            else population * (1 - population)
        )
        for s in range(2):
            divisor = np.where(variance > 0, np.sqrt(variance), 1) if s else np.ones(2)
            transformed_cells = (CELLS - mean) / divisor
            bound = max(np.dot(z, z) + cfg.FIT_INTERCEPT[a] for z in transformed_cells)
            eta = factors / bound
            theta = np.zeros((2, len(factors), 2))
            intercept = np.zeros((2, len(factors)))
            if cfg.INITIALIZE_MEAN[a]:
                response = (pool - population) @ cfg.SIGNALS.T
                response += data["noise"][rep, : cfg.TRAIN_SIZE, None]
                intercept[:] = response.mean(axis=0)[:, None]
            checkpoint = 0
            for stop in range(int(checkpoints[-1]) + 1):
                if stop == checkpoints[checkpoint]:
                    beta = theta / divisor
                    result[checkpoint, a, s, ..., 0] = intercept - beta @ mean
                    result[checkpoint, a, s, ..., 1:] = beta
                    checkpoint += 1
                    if checkpoint == len(checkpoints):
                        break
                idx = int(data["indices"][rep, stop]) if cfg.REUSE[a] else stop
                cell = CELLS[data["cells"][rep, idx]]
                z = (cell - mean) / divisor
                y = cfg.SIGNALS @ (cell - population) + data["noise"][rep, idx]
                residual = theta @ z + intercept - y[:, None]
                theta -= eta[None, :, None] * residual[..., None] * z
                if cfg.FIT_INTERCEPT[a]:
                    intercept -= eta * residual
    return result


def cell_risks(coefficients, q, signal_axis=-3):
    """Enumerate test cells rather than using the diagonal risk formula."""
    signal_axis %= coefficients.ndim
    truth_shape = [1] * coefficients.ndim
    truth_shape[signal_axis] = 2
    truth_shape[-1] = 4
    truth = (cfg.SIGNALS @ (CELLS - [0.5, q]).T).reshape(truth_shape)
    prediction = coefficients[..., :1] + coefficients[..., 1:] @ CELLS.T
    error = 0.5 * (prediction - truth) ** 2
    weights = np.array([(1 - q) / 2, q / 2, (1 - q) / 2, q / 2])
    return np.stack((error @ weights, error[..., [1, 3]].mean(axis=-1)), axis=-1)


def reference_scores(paths, data, q, validation_size):
    cells = data["validation_cells"][0, :validation_size]
    noise = data["validation_noise"][0, :validation_size]
    eligible = cells % 2 == 1
    if not eligible.any():
        eligible[:] = True
    score = np.zeros(paths.shape[:-1])
    for cell_id, cell in enumerate(CELLS):
        mask = eligible & (cells == cell_id)
        signal = cfg.SIGNALS @ (cell - [0.5, q])
        error = (
            paths[..., 0] + paths[..., 1:] @ cell - signal[None, None, None, :, None]
        )
        score += 0.5 * (
            mask.sum() * error**2
            - 2 * noise[mask].sum() * error
            + np.sum(noise[mask] ** 2)
        )
    return score / eligible.sum()


def check_small():
    maximum = 0.0
    for q_id, q in enumerate(cfg.PREVALENCES):
        data = sample(q_id, 1, 0, 1)
        # Explicit absence checks the fallback and the empirical zero-variance rule.
        if q_id == 1:
            data["cells"][:, : cfg.TRAIN_SIZE] &= np.uint8(2)
            data["validation_cells"] &= np.uint8(2)
        paths = reference_paths(data, q)
        reference = cell_risks(paths, q)
        fixed = np.stack(
            (choose_fixed(reference, q), choose_fixed(reference, q, True)), axis=-2
        )
        observed = simulate(data, q, fixed)
        error = float(np.max(abs(observed["sum_risk"] - reference)))
        maximum = max(maximum, error)
        assert_allclose(observed["sum_risk"], reference, atol=2e-12, rtol=2e-12)
        assert not observed["failure_checkpoint"].any()
        scores = [reference[..., 1]] + [
            reference_scores(paths, data, q, n) for n in cfg.VALIDATION_SIZES
        ]
        for cap_id, cap in enumerate(cfg.budgets(q)):
            limit = np.searchsorted(cfg.stops(q), cap, side="right")
            for arm, scaling, signal, policy in np.ndindex(
                len(cfg.ARMS), 2, 2, len(cfg.POLICIES)
            ):
                stop, rate = observed["selected"][
                    0, cap_id, arm, scaling, signal, policy
                ]
                expected = paths[stop, arm, scaling, signal, rate]
                assert_allclose(
                    observed["coefficients"][0, cap_id, arm, scaling, signal, policy],
                    expected,
                    atol=2e-12,
                    rtol=2e-12,
                )
                if policy >= 2:
                    score = scores[policy - 2][:limit, arm, scaling, signal]
                    assert_allclose(
                        score[stop, rate], score.min(), atol=2e-12, rtol=2e-12
                    )
        params = parameters(data, q, cfg.rates())
        for arm in range(len(cfg.ARMS)):
            z = (CELLS[None, None] - params["mean"][:, arm, None, None]) / params[
                "divisor"
            ][:, arm, :, None]
            norm = np.sum(z**2, axis=-1) + cfg.FIT_INTERCEPT[arm]
            assert (
                np.max(params["eta"][:, arm, :, -1] * norm.max(axis=-1)) <= 1.9 + 1e-14
            )
    print(
        "Independent transformed paths, four-cell risks, and selections: "
        f"max error {maximum:.3g}."
    )


def check_moments():
    maximum = 0.0
    for q in cfg.PREVALENCES:
        factors = np.array([0.0, 0.03, 0.4, 1.9])
        checkpoints = np.array([0, 1, 7, int(cfg.budgets(q)[-1])])
        observed = exact_baseline(q, factors, checkpoints)
        model = make_model(q, "independent")
        for scaling, signal, rate in np.ndindex(2, 2, len(factors)):
            scales = np.ones(2) if scaling == 0 else np.sqrt([0.25, q * (1 - q)])
            bound = np.max(np.sum(((CELLS - [0.5, q]) / scales) ** 2, axis=-1))
            moments = moment_path(
                model,
                scales,
                factors[rate] / bound,
                1,
                checkpoints,
                cfg.SIGNALS[signal],
            )
            for objective, gram in enumerate((model["gram"], model["rare_second"])):
                expected = 0.5 * np.einsum("ij,kij->k", gram, moments["second"])
                actual = observed[:, scaling, signal, rate, objective]
                maximum = max(maximum, float(np.max(abs(expected - actual))))
                assert_allclose(actual, expected, atol=2e-12, rtol=2e-12)
    print(f"Independent full moment operators: max error {maximum:.3g}.")


def check_saved(output):
    settings = json.loads((output / "settings.json").read_text())
    assert settings["completed"]
    maximum = 0.0
    count = 0
    for q_id, run in enumerate(settings["runs"]):
        q = run["q"]
        with np.load(output / f"q{q_id}-calibration.npz") as calibration:
            profile = calibration["mean_risk"].copy()
            fixed = calibration["fixed"]
            profile[:, 0] = calibration["exact_baseline"]
            expected = np.stack(
                (choose_fixed(profile, q), choose_fixed(profile, q, True)), axis=-2
            )
            assert np.array_equal(fixed, expected)
        for record in run["evaluation"]:
            with np.load(output / record["file"]) as archive:
                coefficients = archive["coefficients"]
                selected = archive["selected"]
                assert np.isfinite(coefficients).all()
                assert not archive["failure_checkpoint"].any()
                assert (
                    np.asarray(run["checkpoints"])[selected[..., 0]]
                    <= np.asarray(run["caps"])[None, :, None, None, None, None]
                ).all()
                risks = cell_risks(coefficients, q)
                assert_allclose(predictor_risks(coefficients, q), risks, atol=2e-11)
                assert (
                    risks[..., 1][:, :, :, :, :, 2, None] <= risks[..., 1] + 1e-12
                ).all()
                # Replay one complete replication from every independently seeded shard.
                data = {
                    key: archive[key]
                    for key in (
                        "cells",
                        "noise",
                        "indices",
                        "validation_cells",
                        "validation_noise",
                    )
                }
                paths = reference_paths(data, q)
                scores = [cell_risks(paths, q)[..., 1]] + [
                    reference_scores(paths, data, q, n) for n in cfg.VALIDATION_SIZES
                ]
                for cap, arm, scaling, signal, policy in np.ndindex(
                    *selected.shape[1:-1]
                ):
                    stop, rate = selected[0, cap, arm, scaling, signal, policy]
                    expected = paths[stop, arm, scaling, signal, rate]
                    actual = coefficients[0, cap, arm, scaling, signal, policy]
                    maximum = max(maximum, float(np.max(abs(expected - actual))))
                    assert_allclose(actual, expected, atol=2e-11, rtol=2e-11)
                    if policy < 2:
                        assert np.array_equal(
                            [stop, rate], fixed[cap, arm, scaling, signal, policy]
                        )
                    else:
                        limit = np.searchsorted(
                            run["checkpoints"], run["caps"][cap], side="right"
                        )
                        score = scores[policy - 2][:limit, arm, scaling, signal]
                        assert_allclose(score[stop, rate], score.min(), atol=2e-11)
                    count += 1
    print(
        f"Saved selected predictors: {count} independent endpoint replays, "
        f"max error {maximum:.3g}."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved", action="store_true")
    parser.add_argument("--output", type=Path, default=cfg.OUTPUT)
    args = parser.parse_args()
    check_small()
    check_moments()
    if args.saved:
        check_saved(args.output)


if __name__ == "__main__":
    main()
