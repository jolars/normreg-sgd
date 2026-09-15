"""Exact fresh-sample SGD paths and paired simulation for a declared joint grid.

Reproduce inside devenv shell with ``make reproduce-joint-interactions``.
The frozen fixed-data pilot is an independent experiment and is not rewritten.
"""

import argparse
import hashlib
import importlib.metadata
import itertools
import json
import platform
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
DELTAS = [0.0, 0.25, 0.5, 1.0]
BATCHES = [1, 10, 100]
FACTORS = np.unique(np.r_[np.geomspace(1e-4, 2.2, 41), 0.002, 0.02, 0.2])
COUNTS = np.unique(
    np.r_[
        0,
        np.rint(np.geomspace(1, 10000, 61)).astype(int),
        [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 10000],
    ]
)
Q = 0.02
SIGNAL = np.ones(2)
NOISE_VARIANCE = 1.0
MC_SEED = 20260915
MC_REPLICATES = 32768
FIELDS = ["bias", "second", "design_covariance", "noise_covariance", "valid"]


def make_model(q, dependence):
    p = 0.5
    joint = {"independent": p * q, "nested": q}[dependence]
    assert 0 < q < p and max(0, p + q - 1) <= joint <= min(p, q)
    cells = np.array(list(itertools.product([0.0, 1.0], repeat=2)))
    probabilities = np.array([1 - p - q + joint, q - joint, p - joint, joint])
    x = cells - [p, q]
    gram = x.T @ (probabilities[:, None] * x)
    rare_second = x.T @ ((probabilities * cells[:, 1] / q)[:, None] * x)
    assert np.linalg.eigvalsh(gram).min() > 0
    return {
        "q": q,
        "dependence": dependence,
        "cells": cells,
        "probabilities": probabilities,
        "x": x,
        "gram": gram,
        "rare_second": rare_second,
    }


def operators(model, scales, step, batch, noise_variance):
    z = model["x"] / scales
    h = model["gram"] / np.outer(scales, scales)
    r = np.eye(2) - step * h
    fourth = sum(
        w * np.kron(np.outer(v, v), np.outer(v, v))
        for w, v in zip(model["probabilities"], z, strict=True)
    )
    transition = np.kron(r, r) + step**2 / batch * (fourth - np.kron(h, h))
    injection = step**2 * noise_variance / batch * h
    return r, transition, injection


def stability_limit(model, scales, batch):
    curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]

    def residual(step):
        _, transition, _ = operators(model, scales, step, batch, 1)
        return max(abs(np.linalg.eigvalsh(transition))) - 1

    return float(brentq(residual, 1e-6 / curvature, 2.01 / curvature, xtol=1e-14))


def moment_path(model, scales, step, batch, counts, signal, noise_variance=1.0):
    """Return original-scale moments with separate sources of covariance."""
    counts = np.asarray(counts, dtype=int)
    assert np.all(counts >= 0) and batch >= 1 and noise_variance >= 0
    r, transition, injection = operators(model, scales, step, batch, noise_variance)
    # An affine power evaluates the finite noise sum without inverting I-T,
    # which becomes singular at a stability boundary and at zero step size.
    augmented = np.eye(5)
    augmented[:4, :4] = transition
    augmented[:4, 4] = injection.ravel()
    u0 = -scales * signal
    initial = np.outer(u0, u0).ravel()
    divisor = np.outer(scales, scales)
    bias = np.empty((len(counts), 2))
    homogeneous = np.empty((len(counts), 2, 2))
    noise = np.empty_like(homogeneous)
    with np.errstate(over="ignore", invalid="ignore"):
        for i, count in enumerate(counts):
            power = np.linalg.matrix_power(augmented, int(count))
            bias[i] = np.linalg.matrix_power(r, int(count)) @ u0 / scales
            homogeneous[i] = (power[:4, :4] @ initial).reshape(2, 2) / divisor
            noise[i] = power[:4, 4].reshape(2, 2) / divisor
        homogeneous = (homogeneous + homogeneous.swapaxes(1, 2)) / 2
        noise = (noise + noise.swapaxes(1, 2)) / 2
        design = homogeneous - np.einsum("ki,kj->kij", bias, bias)
        second = homogeneous + noise
    finite = (
        np.isfinite(bias).all(axis=1)
        & np.isfinite(second).all(axis=(1, 2))
        & np.isfinite(design).all(axis=(1, 2))
        & np.isfinite(noise).all(axis=(1, 2))
    )
    valid = finite.copy()
    for i in np.flatnonzero(finite):
        scale = max(1.0, float(np.max(abs(second[i]))))
        valid[i] = all(
            np.linalg.eigvalsh(v / scale).min() >= -1e-8
            for v in [second[i], design[i], noise[i]]
        )
    return {
        "bias": bias,
        "second": second,
        "design_covariance": design,
        "noise_covariance": noise,
        "valid": valid,
        "spectral_radius": float(max(abs(np.linalg.eigvalsh(transition)))),
    }


def risk_parts(model, moments, index=0):
    bias = moments["bias"][index]
    result = {
        "coefficient_mean": SIGNAL + bias,
        "coefficient_bias": bias,
        "coefficient_mse": np.diag(moments["second"][index]),
    }
    for name, gram in [("aggregate", model["gram"]), ("rare", model["rare_second"])]:
        result[name] = {
            "risk": 0.5 * np.sum(gram * moments["second"][index]),
            "squared_bias": 0.5 * bias @ gram @ bias,
            "design_variance": 0.5 * np.sum(gram * moments["design_covariance"][index]),
            "noise_variance": 0.5 * np.sum(gram * moments["noise_covariance"][index]),
        }
    return result


def paired_simulation(replicates):
    """Use the same observation stream across scalings and batch sizes."""
    model = make_model(Q, "independent")
    rng = np.random.default_rng(MC_SEED)
    configurations = []
    for delta, batch in itertools.product([0.0, 0.5], [1, 10]):
        scales = np.diag(model["gram"]) ** delta
        curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]
        configurations.append((delta, batch, scales, 0.002 / curvature))
    beta = np.zeros((4, replicates, 2))
    snapshots = {}
    for block in range(1, 101):
        indices = rng.choice(4, size=(replicates, 10), p=model["probabilities"])
        x = model["x"][indices]
        y = x @ SIGNAL + rng.normal(size=(replicates, 10))
        for i, (_, batch, scales, step) in enumerate(configurations):
            if batch == 1:
                for j in range(10):
                    residual = y[:, j] - np.sum(x[:, j] * beta[i], axis=1)
                    beta[i] += step / scales**2 * x[:, j] * residual[:, None]
            else:
                residual = y - np.einsum("rbi,ri->rb", x, beta[i])
                beta[i] += step / scales**2 * np.mean(x * residual[:, :, None], axis=1)
        if block in [10, 100]:
            for i, (delta, batch, _, _) in enumerate(configurations):
                snapshots[(delta, batch, 10 * block // batch)] = beta[i].copy()
    records, samples = [], {}
    for (delta, batch, count), coefficients in snapshots.items():
        scales = np.diag(model["gram"]) ** delta
        curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]
        step = 0.002 / curvature
        exact = moment_path(model, scales, step, batch, [count], SIGNAL)
        error = coefficients - SIGNAL
        sample = np.column_stack(
            [
                error,
                error[:, 0] ** 2,
                error[:, 0] * error[:, 1],
                error[:, 1] ** 2,
                0.5 * np.einsum("ri,ij,rj->r", error, model["gram"], error),
                0.5 * np.einsum("ri,ij,rj->r", error, model["rare_second"], error),
            ]
        )
        samples[(delta, batch, count)] = sample
        second = exact["second"][0]
        target = np.r_[
            exact["bias"][0],
            second[0, 0],
            second[0, 1],
            second[1, 1],
            0.5 * np.sum(model["gram"] * second),
            0.5 * np.sum(model["rare_second"] * second),
        ]
        mean, se = sample.mean(axis=0), sample.std(axis=0, ddof=1) / np.sqrt(replicates)
        z = abs(mean - target) / np.maximum(se, 1e-15)
        assert np.all(abs(mean - target) <= 6 * se + 1e-10), (delta, batch, count, z)
        records.append(
            {
                "delta": delta,
                "batch": batch,
                "updates": count,
                "observations": batch * count,
                "step": step,
                "exact": target,
                "simulation_mean": mean,
                "mcse": se,
                "absolute_z": z,
            }
        )
    contrasts = []
    for comparison, left, right in [
        ("fixed_updates_100", (0.5, 1, 100), (0.5, 10, 100)),
        ("fixed_observations_1000", (0.5, 1, 1000), (0.5, 10, 100)),
    ]:
        difference = samples[left][:, -1] - samples[right][:, -1]
        contrasts.append(
            {
                "comparison": comparison,
                "direction": "B1 minus B10 rare risk",
                "mean": difference.mean(),
                "mcse": difference.std(ddof=1) / np.sqrt(replicates),
            }
        )
    return {
        "seed": MC_SEED,
        "replicates": replicates,
        "noise": "independent N(0,1)",
        "fields": [
            "bias_common",
            "bias_rare",
            "mse_common",
            "error_cross_moment",
            "mse_rare",
            "aggregate_risk",
            "rare_risk",
        ],
        "records": records,
        "paired_contrasts": contrasts,
        "max_absolute_z": max(float(np.max(r["absolute_z"])) for r in records),
    }


def serializable(value):
    if isinstance(value, np.ndarray):
        return serializable(value.tolist())
    if isinstance(value, np.generic):
        return serializable(value.item())
    if isinstance(value, dict):
        return {k: serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(v) for v in value]
    return value


def local_sensitivity():
    """Check a neighborhood of the primary comparison after the initial grid."""
    model = make_model(Q, "independent")
    scales = np.sqrt(np.diag(model["gram"]))
    curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]
    records = []
    for factor, budget in itertools.product([0.001, 0.002, 0.004], [500, 1000, 2000]):
        step = factor / curvature
        for comparison in ["updates", "observations"]:
            risks = []
            for batch in [1, 10]:
                count = 100 if comparison == "updates" else budget // batch
                path = moment_path(model, scales, step, batch, [count], SIGNAL)
                risks.append(risk_parts(model, path)["rare"]["risk"])
            records.append(
                {
                    "rate_factor": factor,
                    "observation_budget": budget,
                    "comparison": comparison,
                    "rare_risk_B1_B10": risks,
                    "difference_B1_minus_B10": risks[0] - risks[1],
                }
            )
    return records


def run(output, replicates):
    configurations, paths, witnesses = [], [], []
    models = [make_model(Q, name) for name in ["independent", "nested"]]
    for model, delta, batch in itertools.product(models, DELTAS, BATCHES):
        scales = np.diag(model["gram"]) ** delta
        curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]
        limit = stability_limit(model, scales, batch)
        for factor in FACTORS:
            step = factor / curvature
            path = moment_path(model, scales, step, batch, COUNTS, SIGNAL)
            configurations.append(
                {
                    "dependence": model["dependence"],
                    "delta": delta,
                    "batch": batch,
                    "batch_rarity": batch * Q,
                    "rate_factor": factor,
                    "step": step,
                    "scales": scales,
                    "curvature": curvature,
                    "stability_step": limit,
                    "spectral_radius": path["spectral_radius"],
                }
            )
            paths.append(path)
    arrays = {field: np.array([path[field] for path in paths]) for field in FIELDS}
    arrays["updates"] = COUNTS
    for delta, batch, comparison in itertools.product(
        [0.0, 0.5], BATCHES, ["updates", "observations"]
    ):
        model = models[0]
        scales = np.diag(model["gram"]) ** delta
        curvature = np.linalg.eigvalsh(model["gram"] / np.outer(scales, scales))[-1]
        step = 0.002 / curvature
        count = 100 if comparison == "updates" else 1000 // batch
        path = moment_path(model, scales, step, batch, [count], SIGNAL)
        witnesses.append(
            {
                "delta": delta,
                "batch": batch,
                "comparison": comparison,
                "updates": count,
                "observations": batch * count,
                "step": step,
                **risk_parts(model, path),
            }
        )
    source_paths = [
        "experiments/run_joint_interactions.py",
        "experiments/check_joint_interactions.py",
        "experiments/plot_joint_interactions.py",
        "uv.lock",
    ]
    result = {
        "schema_version": 1,
        "sampling": "fresh iid observations at every update",
        "centering_scales_intercept": "known population; intercept fixed at zero",
        "signal": SIGNAL,
        "noise_variance": NOISE_VARIANCE,
        "risk_factor": 0.5,
        "q": Q,
        "models": models,
        "configurations": configurations,
        "updates": COUNTS,
        "witnesses": witnesses,
        "simulation": paired_simulation(replicates),
        "post_grid_local_sensitivity": local_sensitivity(),
        "nonfinite_or_invalid_endpoints": int((~arrays["valid"]).sum()),
        "provenance": {
            "python": platform.python_version(),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ["numpy", "scipy", "matplotlib"]
            },
            "sha256": {
                p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                for p in source_paths
            },
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output.with_suffix(".npz"), **arrays)
    result["arrays_sha256"] = hashlib.sha256(
        output.with_suffix(".npz").read_bytes()
    ).hexdigest()
    output.write_text(
        json.dumps(serializable(result), indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "configurations": len(configurations),
                "stopping_counts": len(COUNTS),
                "invalid_endpoints": result["nonfinite_or_invalid_endpoints"],
                "simulation_max_z": result["simulation"]["max_absolute_z"],
            }
        )
    )


if __name__ == "__main__":
    assert __debug__, "Run without -O."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results/joint-interactions.json"
    )
    parser.add_argument("--replicates", type=int, default=MC_REPLICATES)
    arguments = parser.parse_args()
    assert arguments.replicates > 1
    run(arguments.output, arguments.replicates)
