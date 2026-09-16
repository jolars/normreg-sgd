"""Paired Gaussian simulations with the protocol's fixed independent RNG blocks."""

import argparse
import concurrent.futures
import json
from pathlib import Path

import numpy as np
from robustness_spec import ATOL, OUTPUT, PANELS, RTOL, model, sha256, write_json
from run_normalization_robustness import moment_path, parameters


def quantities(error, m):
    return np.column_stack(
        [
            error,
            error[:, 0] ** 2,
            error[:, 0] * error[:, 1],
            error[:, 1] ** 2,
            0.5 * np.einsum("ri,ij,rj->r", error, m["gram"], error),
            0.5 * np.einsum("ri,ij,rj->r", error, m["rare_second"], error),
        ]
    )


def sample_summary(values, exact, failed=None):
    if failed is not None and np.any(failed):
        return dict(complete=False, failed_replicates=np.flatnonzero(failed))
    mean = values.mean(axis=0)
    mcse = values.std(axis=0, ddof=1) / np.sqrt(len(values))
    difference = mean - exact
    return dict(
        complete=True,
        mean=mean,
        mcse=mcse,
        exact=exact,
        interval=np.stack([mean - 1.96 * mcse, mean + 1.96 * mcse], axis=-1),
        residual=difference,
        gate=np.abs(difference) <= 6 * mcse + 1e-10,
    )


def simulate_block(task):
    panel, block = task
    q, ell, signal, sigma2, h, stops = PANELS[panel]
    m = model(q, ell)
    signal = np.array(signal)
    features_rng = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence([20260916, panel, block, 0]))
    )
    noise_rng = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence([20260916, panel, block, 1]))
    )
    g = np.array([1.0, 0.1, 10.0])
    scales = np.stack([parameters(m, s, h)[0] for s in ("U", "S")])
    eta = np.array([4 * h, h])
    divisors = g[:, None, None] * scales[None]
    steps = g[:, None] ** 2 * eta[None]
    # Scaled coefficients ensure the global controls exercise actual preprocessing.
    theta = np.zeros((2, 3, 2, 2, 256, 2))
    snapshots = np.full((2, 2, 3, 2, 256, 2), np.nan)
    failure_mask = np.zeros((2, 3, 2, 2, 256), dtype=bool)
    failures = []
    maximum = dict(
        iterate_absolute=0.0,
        iterate_tolerance_ratio=0.0,
        prediction_absolute=0.0,
        prediction_tolerance_ratio=0.0,
    )
    counts = np.zeros(2, dtype=int)
    for start in range(0, max(stops) * 10, 100):
        length = min(100, max(stops) * 10 - start)
        indices = np.searchsorted(
            np.cumsum(m["probabilities"]), features_rng.random((length, 256))
        )
        x = m["x"][indices]
        noise = noise_rng.standard_normal((length, 256)) * np.sqrt(sigma2)
        response = np.stack([x @ signal + noise, x @ signal], axis=1)
        for bi, batch in enumerate((1, 10)):
            for j in range(0, length, batch):
                if counts[bi] == max(stops):
                    break
                xx = x[j : j + batch]
                yy = response[j : j + batch]
                covariance = np.einsum("bri,brj->rij", xx, xx) / batch
                xy = np.einsum("bri,bcr->cri", xx, yy) / batch
                beta = theta[bi] / divisors[:, :, None, None, :]
                gradient = xy[None, None] - np.einsum(
                    "rij,gsc rj->gscri", covariance, beta
                )
                previous = theta[bi].copy()
                with np.errstate(over="ignore", invalid="ignore"):
                    theta[bi] += (
                        steps[:, :, None, None, None] / divisors[:, :, None, None, :]
                    ) * gradient
                counts[bi] += 1
                newly_failed = (~np.isfinite(theta[bi]).all(axis=-1)) & ~failure_mask[
                    bi
                ]
                for gi, si, companion, replicate in np.argwhere(newly_failed):
                    failures.append(
                        dict(
                            panel=panel,
                            block=block,
                            scaling=int(si),
                            g=float(g[gi]),
                            batch=batch,
                            companion=int(companion),
                            replicate=block * 256 + int(replicate),
                            k=int(counts[bi]),
                            reason="nonfinite_update",
                            last_finite_theta=previous[
                                gi, si, companion, replicate
                            ].tolist(),
                        )
                    )
                failure_mask[bi] |= newly_failed
                beta = theta[bi] / divisors[:, :, None, None, :]
                delta = beta[1:] - beta[0]
                difference = np.abs(delta)
                maximum["iterate_absolute"] = max(
                    maximum["iterate_absolute"], float(np.nanmax(difference))
                )
                maximum["iterate_tolerance_ratio"] = max(
                    maximum["iterate_tolerance_ratio"],
                    float(np.nanmax(difference / (ATOL + RTOL * np.abs(beta[0])))),
                )
                predictions = np.einsum("ci,gsnri->gsnrc", m["x"], beta)
                difference = np.abs(predictions[1:] - predictions[0])
                maximum["prediction_absolute"] = max(
                    maximum["prediction_absolute"], float(np.nanmax(difference))
                )
                maximum["prediction_tolerance_ratio"] = max(
                    maximum["prediction_tolerance_ratio"],
                    float(
                        np.nanmax(difference / (ATOL + RTOL * np.abs(predictions[0])))
                    ),
                )
                if counts[bi] in stops:
                    snapshots[bi, :, list(stops).index(counts[bi])] = beta[0]
    return panel, block, snapshots, failure_mask, failures, maximum


def covariance_diagnostics(noisy, noiseless, target_design, target_noise):
    def statistic(a, b):
        noise = a - b
        design = np.cov(b, rowvar=False, ddof=1)
        propagated = noise.T @ noise / len(noise)
        cross = (b.T @ noise + noise.T @ b) / len(noise)
        return np.concatenate(
            [matrix[[0, 0, 1], [0, 1, 1]] for matrix in (design, propagated, cross)]
        )

    mean = statistic(noisy, noiseless)
    leave_one = []
    ids = np.arange(len(noisy)) // 256
    for block in range(32):
        keep = ids != block
        leave_one.append(statistic(noisy[keep], noiseless[keep]))
    leave_one = np.array(leave_one)
    mcse = np.sqrt(31 / 32 * np.sum((leave_one - leave_one.mean(axis=0)) ** 2, axis=0))
    target = np.r_[
        target_design[[0, 0, 1], [0, 1, 1]],
        target_noise[[0, 0, 1], [0, 1, 1]],
        [0, 0, 0],
    ]
    return dict(
        mean=mean,
        mcse=mcse,
        exact=target,
        residual=mean - target,
        gate=np.abs(mean - target) <= 6 * mcse + 1e-10,
        method="delete-one-block jackknife; unbiased noiseless covariance",
    )


def summarize(errors, noiseless, failed):
    endpoints, contrasts = [], []
    for panel, (q, ell, signal, sigma2, h, stops) in enumerate(PANELS):
        m = model(q, ell)
        exact, samples = {}, {}
        for bi, batch in enumerate((1, 10)):
            for si, scaling in enumerate(("U", "S")):
                scales, step = parameters(m, scaling, h)
                path = moment_path(m, scales, step, batch, stops, signal, sigma2)
                for ki, k in enumerate(stops):
                    second = path["second"][ki]
                    target = np.r_[
                        path["bias"][ki],
                        second[[0, 0, 1], [0, 1, 1]],
                        path["risks"][ki],
                    ]
                    value = quantities(errors[panel, bi, si, ki], m)
                    key = (bi, si, ki)
                    exact[key], samples[key] = target, value
                    endpoint = dict(
                        panel=panel,
                        scaling=scaling,
                        batch=batch,
                        k=k,
                        M=k * batch,
                        **sample_summary(value, target, failed[panel, bi, si, ki]),
                    )
                    if endpoint["complete"]:
                        endpoint["covariance_diagnostics"] = covariance_diagnostics(
                            errors[panel, bi, si, ki],
                            noiseless[panel, bi, si, ki],
                            path["design"][ki],
                            path["noise"][ki],
                        )
                    endpoints.append(endpoint)
        pairs = []
        for bi, batch in enumerate((1, 10)):
            for ki, k in enumerate(stops):
                pairs.append(("S_minus_U", "fixed_updates", (bi, 1, ki), (bi, 0, ki)))
        for si in (0, 1):
            for left, right in itertools_product_stops(stops):
                for convention in ("fixed_updates", "fixed_observations"):
                    if (
                        stops[left] == stops[right]
                        if convention == "fixed_updates"
                        else stops[left] == 10 * stops[right]
                    ):
                        pairs.append(
                            ("B1_minus_B10", convention, (0, si, left), (1, si, right))
                        )
        for direction, convention, left, right in pairs:
            contrasts.append(
                dict(
                    panel=panel,
                    direction=direction,
                    budget=convention,
                    left=left,
                    right=right,
                    left_k=stops[left[2]],
                    right_k=stops[right[2]],
                    **sample_summary(
                        samples[left] - samples[right],
                        exact[left] - exact[right],
                        failed[(panel, *left)] | failed[(panel, *right)],
                    ),
                )
            )
    return dict(
        fields=[
            "bias_common",
            "bias_rare",
            "mse_common",
            "cross_moment",
            "mse_rare",
            "aggregate",
            "rare",
        ],
        covariance_fields=[
            f"{part}_{entry}"
            for part in ("design", "noise", "cross")
            for entry in ("CC", "CR", "RR")
        ],
        endpoints=endpoints,
        contrasts=contrasts,
    )


def itertools_product_stops(stops):
    return [(i, j) for i in range(len(stops)) for j in range(len(stops))]


def investigate_gates(gates):
    """Retain the observed failure and measure a tail event absent from this MC run."""
    if not gates:
        return []
    assert gates == [(29, "covariance")], "Investigate any new diagnostic gate failure."
    q, ell, signal, sigma2, h, stops = PANELS[2]
    m = model(q, ell)
    scales, step = parameters(m, "S", h)
    k = max(stops)
    conditional = dict(m)
    conditional["probabilities"] = (
        m["probabilities"] * (m["cells"][:, 1] == 0) / (1 - q)
    )
    conditional["gram"] = m["x"].T @ (conditional["probabilities"][:, None] * m["x"])
    full = moment_path(m, scales, step, 1, [k], signal, sigma2)
    absent = moment_path(conditional, scales, step, 1, [k], signal, 0)
    probability = float(np.exp(k * np.log1p(-q)))
    contribution = probability * (
        absent["second"][0, 1, 1]
        - 2 * full["bias"][0, 1] * absent["bias"][0, 1]
        + full["bias"][0, 1] ** 2
    )
    observed_absent = 0
    for block in range(32):
        rng = np.random.Generator(
            np.random.PCG64(np.random.SeedSequence([20260916, 2, block, 0]))
        )
        seen = np.zeros(256, dtype=bool)
        for _ in range(k // 100):
            cells = np.searchsorted(
                np.cumsum(m["probabilities"]), rng.random((100, 256))
            )
            seen |= np.any(m["cells"][cells, 1] == 1, axis=0)
        observed_absent += int(np.count_nonzero(~seen))
    return [
        dict(
            endpoint=29,
            component="design_RR",
            status="retained_MC_precision_failure",
            explanation=(
                "The noiseless covariance is dominated by events too rare for the "
                "declared replication count. The fixed simulation and six-MCSE gate "
                "are retained; no additional replications are used."
            ),
            no_rare_probability=probability,
            expected_absent_replicates=8192 * probability,
            observed_absent_replicates=observed_absent,
            conditional_bias=absent["bias"][0],
            conditional_second=absent["second"][0],
            absent_contribution_to_design_RR=contribution,
            exact_design_RR=full["design"][0, 1, 1],
            fraction_from_absence=contribution / full["design"][0, 1, 1],
        )
    ]


def produce(output, workers):
    errors = np.empty((6, 2, 2, 3, 8192, 2))
    noiseless = np.empty_like(errors)
    failed = np.zeros(errors.shape[:-1], dtype=bool)
    failures, controls = [], []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        tasks = [(p, b) for p in range(6) for b in range(32)]
        for completed, result in enumerate(pool.map(simulate_block, tasks), 1):
            panel, block, snapshots, masks, ledger, maximum = result
            sl = slice(block * 256, (block + 1) * 256)
            signal = np.array(PANELS[panel][2])
            errors[panel, :, :, :, sl] = snapshots[:, :, :, 0] - signal
            noiseless[panel, :, :, :, sl] = snapshots[:, :, :, 1] - signal
            failed[panel, :, :, :, sl] = np.any(masks, axis=(1, 3))[:, :, None, :]
            failures.extend(ledger)
            controls.append(dict(panel=panel, block=block, **maximum))
            if completed % 8 == 0:
                print(f"Simulation: {completed}/192 blocks", flush=True)
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output / "paired-simulation.npz",
        error=errors,
        noiseless_error=noiseless,
        failed=failed,
        replicate_id=np.arange(8192),
        block_id=np.arange(8192) // 256,
    )
    summary = summarize(errors, noiseless, failed)
    gates = [
        (i, "moments")
        for i, e in enumerate(summary["endpoints"])
        if e["complete"] and not all(e["gate"])
    ]
    gates += [
        (i, "covariance")
        for i, e in enumerate(summary["endpoints"])
        if e["complete"] and not all(e["covariance_diagnostics"]["gate"])
    ]
    gates += [
        (i, "contrast")
        for i, e in enumerate(summary["contrasts"])
        if e["complete"] and not all(e["gate"])
    ]
    summary.update(
        failures=failures,
        global_rescaling=controls,
        diagnostic_gate_failures=gates,
        diagnostic_investigations=investigate_gates(gates),
        sha256=sha256(output / "paired-simulation.npz"),
        replicates=8192,
    )
    write_json(output / "simulation-summary.json", summary)
    print(
        json.dumps(
            dict(failed_replicates=len(failures), diagnostic_gate_failures=gates)
        ),
        flush=True,
    )


if __name__ == "__main__":
    assert __debug__, "Run ordinary Python without -O."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--workers", type=int, default=4)
    arguments = parser.parse_args()
    produce(arguments.output, arguments.workers)
