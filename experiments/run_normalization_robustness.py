"""Compute all declared moment endpoints, retaining numerical failures.

Run through ``make reproduce-normalization-robustness`` inside devenv shell.
The protocol is frozen; this driver never rewrites either preceding study.
"""

import argparse
import importlib.metadata
import platform
import sys
from pathlib import Path

import numpy as np
from robustness_spec import (
    ATOL,
    BATCHES,
    FAILURES,
    HC,
    HF,
    KC,
    KF,
    LC,
    MC,
    MF,
    OUTPUT,
    PANELS,
    PROTOCOL,
    QC,
    ROOT,
    RTOL,
    SIGN_TOL,
    STABILITY_TOL,
    grid,
    laws,
    model,
    preserved,
    sha256,
    write_json,
)
from run_joint_interactions import operators

BASIS = np.array([[1.0, 0, 0, 0], [0, 2**-0.5, 2**-0.5, 0], [0, 0, 0, 1]])


def parameters(m, scaling, h):
    scales = np.ones(2) if scaling == "U" else np.sqrt(np.diag(m["gram"]))
    step = (4 if scaling == "U" else 1) * h
    return scales, step


def stability(m, scales, step, batch):
    _, transition, _ = operators(m, scales, step, batch, 1.0)
    return float(np.max(np.abs(np.linalg.eigvalsh(BASIS @ transition @ BASIS.T))))


def boundary(m, scales, batch):
    curvature = float(np.linalg.eigvalsh(m["gram"] / np.outer(scales, scales))[-1])
    lo, hi = 1e-6 / curvature, 2.01 / curvature
    assert stability(m, scales, lo, batch) < 1 < stability(m, scales, hi, batch)
    while hi - lo > 1e-13:
        mid = (lo + hi) / 2
        if stability(m, scales, mid, batch) < 1:
            lo = mid
        else:
            hi = mid
    limit = (lo + hi) / 2
    below, above = [stability(m, scales, f * limit, batch) for f in (0.99, 1.01)]
    assert below < 1 < above
    return dict(
        bracket=[lo, hi],
        eta_ms=limit,
        tolerance=1e-13,
        curvature=curvature,
        radius_below=below,
        radius_above=above,
    )


def powers(matrix, counts):
    """Share binary powers while keeping overflowing endpoints independent."""
    exponents = np.array(counts, dtype=np.int64)
    result = np.broadcast_to(np.eye(len(matrix)), (len(counts), *matrix.shape)).copy()
    factor = matrix.copy()
    with np.errstate(over="ignore", invalid="ignore"):
        while np.any(exponents):
            selected = exponents % 2 == 1
            result[selected] = result[selected] @ factor
            exponents //= 2
            if np.any(exponents):
                factor = factor @ factor
    return result


def moment_path(m, scales, step, batch, counts, signal, sigma2):
    """Use the existing update operator, with explicit law-specific signal/noise."""
    signal = np.asarray(signal)
    counts = np.asarray(counts)
    r, transition, injection = operators(m, scales, step, batch, 1.0)
    augmented = np.eye(5)
    augmented[:4, :4] = transition
    augmented[:4, 4] = injection.ravel()
    initial = -scales * signal
    divisor = np.outer(scales, scales)
    with np.errstate(over="ignore", invalid="ignore"):
        power = powers(augmented, counts)
        bias = (powers(r, counts) @ initial) / scales
        homogeneous = (power[:, :4, :4] @ np.outer(initial, initial).ravel()).reshape(
            -1, 2, 2
        ) / divisor
        unit_noise = power[:, :4, 4].reshape(-1, 2, 2) / divisor
        if np.all(signal == 0):
            # An exploding unused propagator does not invalidate an exact zero state.
            bias[:] = 0
            homogeneous[:] = 0
        noise = sigma2 * unit_noise if sigma2 else np.zeros_like(unit_noise)
        design = homogeneous - np.einsum("ki,kj->kij", bias, bias)
        second = homogeneous + noise
        tensors = np.stack([second, design, noise], axis=1)
        symmetry = np.max(np.abs(tensors - tensors.swapaxes(-1, -2)), axis=(-1, -2))
        scale = np.maximum(1, np.max(abs(tensors), axis=(-1, -2)))
        finite = np.isfinite(tensors).all(axis=(1, 2, 3)) & np.isfinite(bias).all(
            axis=1
        )
        minimum = np.full((len(counts), 3), np.nan)
        minimum[finite] = (
            np.linalg.eigvalsh(tensors[finite] / scale[finite, :, None, None])[..., 0]
            * scale[finite]
        )
        code = np.zeros(len(counts), dtype=np.uint8)
        code[~finite] = 1
        code[finite & np.any(minimum < -ATOL - RTOL * scale, axis=1)] = 2
        code[finite & np.any(symmetry > ATOL + RTOL * scale, axis=1)] = 3
        weights = np.stack([m["gram"], m["rare_second"]])
        parts = np.stack(
            [
                0.5 * np.einsum("ki,wij,kj->kw", bias, weights, bias),
                0.5 * np.einsum("kij,wij->kw", design, weights),
                0.5 * np.einsum("kij,wij->kw", noise, weights),
            ],
            axis=-1,
        )
        risks = 0.5 * np.einsum("kij,wij->kw", second, weights)
        code[(code == 0) & ~np.isfinite(risks).all(axis=1)] = 4
    return dict(
        bias=bias,
        mean=signal + bias,
        second=second,
        design=design,
        noise=noise,
        noise_unit=unit_noise,
        risks=risks,
        risk_parts=parts,
        psd_minimum=minimum,
        symmetry_residual=symmetry,
        failure=code,
    )


def produce(output):
    output.mkdir(parents=True, exist_ok=True)
    preservation = preserved()
    law_list = laws()
    boundaries = []
    boundary_map = {}
    for q in QC:
        for ell in LC:
            m = model(q, ell)
            for scaling in ("U", "S"):
                scales, _ = parameters(m, scaling, 1.0)
                for batch in BATCHES:
                    info = dict(
                        q=q,
                        ell=ell,
                        scaling=scaling,
                        batch=batch,
                        **boundary(m, scales, batch),
                    )
                    boundary_map[q, ell, scaling, batch] = info
                    boundaries.append(info)
    configurations, chunks = [], []
    offset = 0
    for law in law_list:
        m = model(law["q"], law["ell"])
        law.update(
            probabilities=m["probabilities"],
            gram=m["gram"],
            rare_second=m["rare_second"],
            signal_variance=np.asarray(law["signal"]) @ m["gram"] @ law["signal"],
        )
        for scaling in ("U", "S"):
            for batch in BATCHES:
                rates, counts, labels = grid(law, batch)
                info = boundary_map[law["q"], law["ell"], scaling, batch]
                for h in rates:
                    scales, step = parameters(m, scaling, h)
                    rho = stability(m, scales, step, batch)
                    status = (
                        "zero"
                        if h == 0
                        else "stable"
                        if rho < 1 - STABILITY_TOL
                        else "unstable"
                        if rho > 1 + STABILITY_TOL
                        else "boundary"
                    )
                    cid = len(configurations)
                    configurations.append(
                        dict(
                            id=cid,
                            law=law["id"],
                            scaling=scaling,
                            batch=batch,
                            h=h,
                            coarse_rate=bool(h in HC),
                            scales=scales,
                            eta=step,
                            effective_step=step / scales**2,
                            curvature=info["curvature"],
                            curvature_scaled_rate=step * info["curvature"],
                            radius=rho,
                            stability=status,
                            bq=batch * law["q"],
                            offset=offset,
                            size=len(counts),
                        )
                    )
                    path = moment_path(
                        m, scales, step, batch, counts, law["signal"], law["sigma2"]
                    )
                    path.update(
                        configuration=np.full(len(counts), cid, dtype=np.int32),
                        k=counts.astype(np.int32),
                        M=(counts * batch).astype(np.int32),
                        grid_labels=labels,
                    )
                    chunks.append(path)
                    offset += len(counts)
        if (law["id"] + 1) % 12 == 0:
            print(
                f"Moments: {law['id'] + 1}/{len(law_list)} laws, {offset} endpoints",
                flush=True,
            )
    data = {name: np.concatenate([p[name] for p in chunks]) for name in chunks[0]}
    assert len(configurations) == 51048 and len(data["k"]) == 2571800
    np.savez_compressed(output / "paths.npz", **data)
    probes = []
    for info in boundaries:
        m = model(info["q"], info["ell"])
        scales, _ = parameters(m, info["scaling"], 1.0)
        for label, step in [
            (str(f), f * info["eta_ms"]) for f in (0.5, 0.99, 1, 1.01)
        ] + [("mean_boundary", 2 / info["curvature"])]:
            counts = np.array([0, 1, 2, 100, 1000, 10000])
            path = moment_path(m, scales, step, info["batch"], counts, [1, 1], 3)
            probes.append(
                dict(
                    q=info["q"],
                    ell=info["ell"],
                    scaling=info["scaling"],
                    batch=info["batch"],
                    factor=label,
                    eta=step,
                    k=counts,
                    radius=stability(m, scales, step, info["batch"]),
                    **path,
                )
            )
    sources = [PROTOCOL, "uv.lock", "devenv.lock"]
    sources += [
        str(p.relative_to(ROOT))
        for p in sorted((ROOT / "experiments").glob("*robustness*"))
        if p.is_file()
    ]
    sources += [
        "experiments/run_joint_interactions.py",
        "experiments/check_joint_interactions.py",
        "experiments/plot_joint_interactions.py",
        "Makefile",
    ]
    spec = dict(
        protocol_version=1,
        protocol=PROTOCOL,
        sha256={s: sha256(ROOT / s) for s in sources},
        preserved_baseline="a47cbfb",
        preserved_sha256=preservation,
        software={
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "matplotlib")
        },
        python=platform.python_version(),
        command=sys.argv,
        reproduction_command="devenv shell -- make reproduce-normalization-robustness",
        laws=law_list,
        configurations=configurations,
        grids=dict(HC=HC, HF=HF, KC=KC, KF=KF, MC=MC, MF=MF),
        tolerances=dict(
            absolute=ATOL, relative=RTOL, sign=SIGN_TOL, stability=STABILITY_TOL
        ),
        panels=PANELS,
        simulation=dict(
            replicates=8192,
            blocks=32,
            block_size=256,
            seed=[20260916, "panel", "block", "stream"],
            streams={0: "features", 1: "noise"},
            order="observation first, replication second",
            global_rescaling=[0.1, 10],
        ),
        failure_codes=FAILURES,
        paths_sha256=sha256(output / "paths.npz"),
        counts=dict(laws=228, refined_laws=16, configurations=51048, endpoints=2571800),
        boundaries=boundaries,
    )
    write_json(output / "specification.json", spec)
    write_json(output / "boundary-probes.json", probes)
    print(
        f"Saved {len(data['k'])} endpoints; "
        f"invalid: {np.count_nonzero(data['failure'])}",
        flush=True,
    )


if __name__ == "__main__":
    assert __debug__, "Run ordinary Python without -O."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    produce(parser.parse_args().output)
