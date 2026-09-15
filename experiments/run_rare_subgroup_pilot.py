"""Bounded fixed-data GD/replacement-SGD pilot with exact conditional moments.

Reproduce: devenv shell -- python experiments/run_rare_subgroup_pilot.py
Check: devenv shell -- python experiments/check_rare_subgroup_pilot.py
See notes/rare-subgroup-pilot.md for the predeclared design and limitations.
"""

import argparse
import hashlib
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
N = 400
DAMPING = 0.01
NOISE_VARIANCE = 1.0
BUDGETS = [N, 5 * N, 20 * N]
RATE_FACTORS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 0.7, 1.5, 2.5]
TUNING_SEEDS = list(range(10000, 10032))
EVALUATION_SEEDS = list(range(20000, 20256))
SIGNALS = {
    "common_only": [1.0, 0.0],
    "rare_only": [0.0, 1.0],
    "equal_sign": [1.0, 1.0],
    "opposite_sign": [1.0, -1.0],
}
METHODS = {"gd": None, "sgd_b1": 1, "sgd_b20": 20}


def make_design(n, q, dependence):
    """Construct actual binary counts before calculating any Gram matrix."""
    p, q_exact = Fraction(1, 2), Fraction(str(q))
    joint = {"independent": p * q_exact, "nested": q_exact, "negative": 0}[dependence]
    assert max(0, p + q_exact - 1) <= joint <= min(p, q_exact)
    masses = [1 - p - q_exact + joint, q_exact - joint, p - joint, joint]
    assert sum(masses) == 1 and min(masses) >= 0
    assert all(Fraction(n * mass).denominator == 1 for mass in masses)
    counts = np.array([int(n * mass) for mass in masses])
    cells = np.array(list(itertools.product([0, 1], repeat=2)))
    means = np.array([float(p), float(q_exact)])
    x = cells - means
    weights = counts / n
    gram = x.T @ (weights[:, None] * x)
    rare_weights = weights * cells[:, 1] / float(q_exact)
    rare_second = x.T @ (rare_weights[:, None] * x)
    np.testing.assert_allclose(weights @ x, 0, atol=1e-15)
    np.testing.assert_allclose(np.diag(gram), means * (1 - means), atol=1e-15)
    assert np.linalg.eigvalsh(gram)[0] > 0
    return {
        "n": n,
        "q": float(q_exact),
        "q_rational": str(q_exact),
        "dependence": dependence,
        "joint_probability_rational": str(joint),
        "cells": cells,
        "counts": counts,
        "probabilities": weights,
        "means": means,
        "centered_cells": x,
        "gram": gram,
        "rare_test_second_moment": rare_second,
    }


def scaling_rules(variances):
    return {
        "none": np.ones(2),
        "std": np.sqrt(variances),
        "variance": variances.copy(),
        "damped": np.sqrt(variances + DAMPING),
    }


def noise_cell_moments(noise, counts):
    means = np.zeros((len(noise), len(counts)))
    seconds = np.zeros_like(means)
    start = 0
    for cell, count in enumerate(counts):
        if count:
            values = noise[:, start : start + count]
            means[:, cell] = values.mean(axis=1)
            seconds[:, cell] = (values**2).mean(axis=1)
        start += count
    assert start == noise.shape[1]
    return means, seconds


def update_operators(design, scales, step, batch_size, noise_mean, noise_second):
    """Augment the scaled error with one to retain all affine cross terms."""
    z = design["centered_cells"] / scales
    weights = design["probabilities"]
    a = np.broadcast_to(np.eye(3), (len(noise_mean), 4, 3, 3)).copy()
    a[:, :, :2, :2] -= step * np.einsum("ci,cj->cij", z, z)
    a[:, :, :2, 2] = step * z[None] * noise_mean[:, :, None]
    mean_a = np.einsum("c,rcij->rij", weights, a)
    mean_outer = np.einsum("ria,rjb->rijab", mean_a, mean_a)
    if batch_size is None:
        return mean_a, mean_outer.reshape(-1, 9, 9)
    individual_outer = np.einsum("c,rcia,rcjb->rijab", weights, a, a)
    # Cell averages alone would discard the variance of reused observation noise.
    within_cell_variance = noise_second - noise_mean**2
    individual_outer[:, :2, :2, 2, 2] += step**2 * np.einsum(
        "c,rc,ci,cj->rij", weights, within_cell_variance, z, z
    )
    operator = mean_outer + (individual_outer - mean_outer) / batch_size
    return mean_a, operator.reshape(-1, 9, 9)


def conditional_moments(
    design, scales, step, batch_size, updates, signal, noise_mean, noise_second
):
    mean_a, operator = update_operators(
        design, scales, step, batch_size, noise_mean, noise_second
    )
    initial = np.r_[-scales * signal, 1.0]
    with np.errstate(over="ignore", invalid="ignore"):
        if batch_size is None:
            error = (np.linalg.matrix_power(mean_a, updates) @ initial)[:, :2] / scales
            return error, np.einsum("ri,rj->rij", error, error)
        second = (
            np.linalg.matrix_power(operator, updates)
            @ np.outer(initial, initial).ravel()
        ).reshape(-1, 3, 3)
        mean = second[:, :2, 2] / scales
        second = second[:, :2, :2] / np.outer(scales, scales)
    return mean, (second + second.transpose(0, 2, 1)) / 2


def homogeneous_radius(design, scales, step, batch_size):
    zeros = np.zeros((1, 4))
    _, operator = update_operators(design, scales, step, batch_size, zeros, zeros)
    indices = [0, 1, 3, 4]
    return float(max(abs(np.linalg.eigvals(operator[0][np.ix_(indices, indices)]))))


def prediction_risks(second, design):
    """Squared prediction excess, without a factor of one half or test noise."""
    return (
        np.einsum("rij,ij->r", second, design["gram"]),
        np.einsum("rij,ij->r", second, design["rare_test_second_moment"]),
    )


def mean_se(values):
    values = np.asarray(values)
    with np.errstate(over="ignore", invalid="ignore"):
        # Unstable but finite endpoints can overflow an unscaled sum or variance.
        scale = np.max(abs(values), axis=0)
        scale = np.where(scale == 0, 1.0, scale)
        normalized = values / scale
        return {
            "mean": normalized.mean(axis=0) * scale,
            "mcse": normalized.std(axis=0, ddof=1) / np.sqrt(len(values)) * scale,
        }


def valid_moments(mean, second):
    finite = np.isfinite(mean).all(axis=1) & np.isfinite(second).all(axis=(1, 2))
    valid = finite.copy()
    with np.errstate(over="ignore", invalid="ignore"):
        for index in np.flatnonzero(finite):
            covariance = second[index] - np.outer(mean[index], mean[index])
            tolerance = 1e-8 * max(1.0, float(np.max(abs(second[index]))))
            valid[index] = (
                np.isfinite(covariance).all()
                and np.linalg.eigvalsh(covariance)[0] >= -tolerance
            )
    return valid, finite


def summarize(mean, second, design):
    aggregate, rare = prediction_risks(second, design)
    valid, finite = valid_moments(mean, second)
    if not valid.all():
        return {
            "status": "nonfinite_or_invalid_moments",
            "nonfinite_replicates": int((~finite).sum()),
            "invalid_finite_replicates": int((finite & ~valid).sum()),
        }
    average_mean = mean.mean(axis=0)
    conditional_covariance = second - np.einsum("ri,rj->rij", mean, mean)
    centered_mean = mean - average_mean
    between_noise = centered_mean.T @ centered_mean / len(mean)
    covariance = conditional_covariance.mean(axis=0) + between_noise
    return {
        "status": "finite",
        "replications": len(mean),
        "coefficient_bias": mean_se(mean),
        "coefficient_second_moment": mean_se(second),
        "coefficient_mse": mean_se(np.diagonal(second, axis1=1, axis2=2)),
        "coefficient_total_mse": mean_se(np.trace(second, axis1=1, axis2=2)),
        "coefficient_covariance_plugin": covariance,
        "mean_conditional_sampling_covariance": mean_se(conditional_covariance),
        "training_noise_covariance_of_conditional_mean_plugin": between_noise,
        "aggregate_risk": mean_se(aggregate),
        "rare_risk": mean_se(rare),
        "conditional_on_first_evaluation_dataset": {
            "seed": EVALUATION_SEEDS[0],
            "coefficient_mean_error": mean[0],
            "coefficient_covariance": conditional_covariance[0],
            "coefficient_second_moment": second[0],
            "aggregate_risk": aggregate[0],
            "rare_risk": rare[0],
        },
    }


def paired_contrast(left, right, design):
    left_risks = prediction_risks(left[1], design)
    right_risks = prediction_risks(right[1], design)
    return {
        name: mean_se(lhs - rhs)
        for name, lhs, rhs in zip(
            ["aggregate_risk", "rare_risk"], left_risks, right_risks
        )
    }


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serializable(value):
    if isinstance(value, np.ndarray):
        return serializable(value.tolist())
    if isinstance(value, np.generic):
        return serializable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value


def run():
    records, designs = [], []
    grid_risks = {}
    for design_id, (q, dependence) in enumerate(
        itertools.product([0.05, 0.01], ["independent", "nested", "negative"])
    ):
        design = make_design(N, q, dependence)
        design["id"] = design_id
        scales_by_name = scaling_rules(np.diag(design["gram"]))
        design["scales"] = scales_by_name
        design["scaled_grams"] = {
            key: design["gram"] / np.outer(scales, scales)
            for key, scales in scales_by_name.items()
        }
        noise_moments = {}
        design["noise_sha256"] = {}
        for stage, seeds in [
            ("tuning", TUNING_SEEDS),
            ("evaluation", EVALUATION_SEEDS),
        ]:
            noise = np.array(
                [
                    np.random.default_rng(
                        np.random.SeedSequence([seed, design_id])
                    ).normal(scale=np.sqrt(NOISE_VARIANCE), size=N)
                    for seed in seeds
                ]
            )
            noise_moments[stage] = noise_cell_moments(noise, design["counts"])
            design["noise_sha256"][stage] = hashlib.sha256(
                noise.astype("<f8").tobytes()
            ).hexdigest()
        designs.append(design)
        for signal_name, signal_values in SIGNALS.items():
            signal = np.array(signal_values)
            evaluations = {}
            scenario_records = []
            for method, batch_size in METHODS.items():
                cost = N if batch_size is None else batch_size
                for scale_name, scales in scales_by_name.items():
                    curvature = np.linalg.eigvalsh(design["scaled_grams"][scale_name])[
                        -1
                    ]
                    rates = np.array(RATE_FACTORS) / curvature
                    candidates_by_budget = {budget: [] for budget in BUDGETS}
                    for step in rates:
                        radius = homogeneous_radius(design, scales, step, batch_size)
                        for budget in BUDGETS:
                            assert budget % cost == 0
                            mean, second = conditional_moments(
                                design,
                                scales,
                                step,
                                batch_size,
                                budget // cost,
                                signal,
                                *noise_moments["tuning"],
                            )
                            valid, finite = valid_moments(mean, second)
                            aggregate, rare = prediction_risks(second, design)
                            candidates_by_budget[budget].append(
                                {
                                    "step": step,
                                    "homogeneous_second_moment_radius": radius,
                                    "asymptotically_unstable": radius >= 1,
                                    "status": "finite"
                                    if valid.all()
                                    else "nonfinite_or_invalid_moments",
                                    "nonfinite_replicates": int((~finite).sum()),
                                    "invalid_finite_replicates": int(
                                        (finite & ~valid).sum()
                                    ),
                                    "aggregate_risk": mean_se(aggregate)
                                    if valid.all()
                                    else None,
                                    "rare_risk": mean_se(rare) if valid.all() else None,
                                }
                            )
                    for budget in BUDGETS:
                        candidates = candidates_by_budget[budget]
                        scores = [
                            item["rare_risk"]["mean"]
                            if item["status"] == "finite"
                            else np.inf
                            for item in candidates
                        ]
                        selected_index = int(np.argmin(scores))
                        assert np.isfinite(scores[selected_index])
                        step = rates[selected_index]
                        mean, second = conditional_moments(
                            design,
                            scales,
                            step,
                            batch_size,
                            budget // cost,
                            signal,
                            *noise_moments["evaluation"],
                        )
                        evaluations[method, scale_name, budget] = (mean, second)
                        grid_risks.setdefault((method, scale_name, budget), []).append(
                            np.array(prediction_risks(second, design))
                        )
                        scenario_records.append(
                            {
                                "design_id": design_id,
                                "signal": signal_name,
                                "method": method,
                                "batch_size": batch_size,
                                "scaling": scale_name,
                                "budget": budget,
                                "updates": budget // cost,
                                "processed_observations": cost * (budget // cost),
                                "tuning_processed_observations": len(TUNING_SEEDS)
                                * len(rates)
                                * budget,
                                "tuning_candidates": candidates,
                                "selected_rate_index": selected_index,
                                "selected_step": step,
                                "evaluation": summarize(mean, second, design),
                            }
                        )
            for record in scenario_records:
                method, scale, budget = (
                    record["method"],
                    record["scaling"],
                    record["budget"],
                )
                record["paired_difference_from_no_scaling"] = paired_contrast(
                    evaluations[method, scale, budget],
                    evaluations[method, "none", budget],
                    design,
                )
                record["paired_difference_from_gd"] = paired_contrast(
                    evaluations[method, scale, budget],
                    evaluations["gd", scale, budget],
                    design,
                )
            records.extend(scenario_records)
        print(f"Completed q={q}, dependence={dependence}.", flush=True)
    average_risks = {key: np.mean(values, axis=0) for key, values in grid_risks.items()}
    grid_summary = []
    for (method, scale, budget), values in average_risks.items():
        baseline = average_risks[method, "none", budget]
        grid_summary.append(
            {
                "method": method,
                "scaling": scale,
                "budget": budget,
                "aggregate_risk": mean_se(values[0]),
                "rare_risk": mean_se(values[1]),
                "paired_difference_from_no_scaling": {
                    "aggregate_risk": mean_se(values[0] - baseline[0]),
                    "rare_risk": mean_se(values[1] - baseline[1]),
                },
            }
        )
    return {
        "schema_version": 1,
        "provenance": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "source_sha256": {
                str(path.relative_to(ROOT)): sha256(path)
                for path in [
                    Path(__file__),
                    ROOT / "experiments/check_rare_subgroup_pilot.py",
                    ROOT / "uv.lock",
                ]
            },
            "reproduction_command": (
                "devenv shell -- python experiments/run_rare_subgroup_pilot.py"
            ),
            "validation_command": (
                "devenv shell -- python experiments/check_rare_subgroup_pilot.py"
            ),
        },
        "protocol": {
            "n": N,
            "budgets": BUDGETS,
            "signals": SIGNALS,
            "methods": METHODS,
            "damping": DAMPING,
            "scales": "none: 1; std: sqrt(v); variance: v; damped: sqrt(v+0.01)",
            "loss": "half the averaged training squared loss",
            "risk": "excess squared prediction error without 1/2; test noise excluded",
            "intercept": "known fixed zero in population-centered coordinates",
            "initial_coefficients": [0, 0],
            "preprocessing": (
                "known population means/scales used unchanged for training and test"
            ),
            "noise": "iid Gaussian per fixed observation, reused on every draw",
            "noise_variance": NOISE_VARIANCE,
            "tuning_seeds": TUNING_SEEDS,
            "evaluation_seeds": EVALUATION_SEEDS,
            "rng": (
                "NumPy default_rng(SeedSequence([seed, design_id])); "
                "cell order 00,01,10,11"
            ),
            "rate_factors": RATE_FACTORS,
            "step_rule": "eta = factor / lambda_max(S^-1 C S^-1)",
            "tuning_objective": (
                "oracle mean exact conditional rare-presence risk at each budget, "
                "separately per design/signal/method/scaling"
            ),
            "tie_rule": "first minimum in increasing rate grid",
            "invalid_rule": (
                "nonfinite or covariance below -1e-8*max(1,max(abs(second))) "
                "=> infinite tuning objective, retained record"
            ),
            "unstable_rule": (
                "homogeneous second-moment radius >= 1 reported; "
                "finite-horizon finite outcomes remain eligible"
            ),
            "uncertainty": (
                "MCSE across training-noise datasets, conditional on fixed design "
                "and selected rates; sampled-index and test-support moments "
                "integrated exactly"
            ),
            "covariance": (
                "finite-replication mixture plug-in using denominator R, decomposed "
                "into conditional sampling covariance and covariance of conditional "
                "means across noise"
            ),
            "pairing": (
                "same realized noisy datasets for all signals/scalings/methods "
                "within each design and stage; risk differences paired "
                "across noise seeds"
            ),
            "scope": (
                "fixed count designs, fixed data replacement, final constant-step "
                "iterates; no fresh-data SGD or validation-based tuning"
            ),
            "grid_summary": (
                "equal weight on all 24 design/signal cases; average paired "
                "conditional risks within each noise replication before computing MCSE"
            ),
        },
        "designs": designs,
        "grid_summary": grid_summary,
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results/rare-subgroup-pilot.json"
    )
    args = parser.parse_args()
    result = run()
    # One record per line keeps the generated artifact and diffs bounded.
    result = serializable(result)
    records = result.pop("records")
    metadata = json.dumps(result, indent=2, allow_nan=False)
    body = ",\n".join(json.dumps(row, allow_nan=False) for row in records)
    args.output.write_text(metadata[:-2] + ',\n  "records": [\n' + body + "\n  ]\n}\n")
    print(f"Wrote {len(records)} matched-budget outcomes to {args.output}.")


if __name__ == "__main__":
    main()
