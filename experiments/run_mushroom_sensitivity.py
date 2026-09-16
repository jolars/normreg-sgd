"""Evaluate fixed damping offsets and variance scaling on paired Mushroom splits."""

import platform
import time
from datetime import datetime, timezone

import numpy as np
import scipy
from mushroom_sensitivity_spec import (
    BATCHES,
    CHECKPOINTS,
    OUTPUT,
    REPS,
    SIZES,
    SOURCES,
    candidate_rows,
    configurations,
    declaration,
    queries,
    select,
)
from practical_dynamics import losses
from practical_spec import ROOT, load_mushroom, mushroom_data, rng, sha256, write_json
from run_mushroom_rate_search import path
from scipy import sparse


def prepare(x, y, configs):
    n, d = x.shape
    mean = np.asarray(x.mean(axis=0)).ravel()
    raw = x.T @ x / n
    raw = raw.toarray() if sparse.issparse(raw) else raw
    variance = np.maximum(0, np.diag(raw) - mean**2)
    active = variance > 1e-14
    params = {
        k: []
        for k in (
            "mu",
            "divisor",
            "active",
            "initial",
            "fit_intercept",
            "curvature",
            "eta",
        )
    }
    cache = {}
    for config in configs:
        scale = config["scale"]
        if scale not in cache:
            if scale == "none":
                divisor = np.ones(d)
            elif scale == "variance":
                divisor = variance.copy()
            else:
                tau = 0.0 if scale == "sd" else float(scale.removeprefix("damped_"))
                divisor = np.sqrt(variance + tau)
            divisor = np.where(active, divisor, 1)
            inv = active / divisor
            # Match the frozen algebra so common candidates can be replayed exactly.
            gram = (
                raw - np.outer(mean, mean) - np.outer(mean, mean) + np.outer(mean, mean)
            )
            gram *= np.outer(inv, inv)
            gram = np.block(
                [[gram, np.zeros((d, 1))], [np.zeros((1, d)), np.ones((1, 1))]]
            )
            curvature = max(float(np.linalg.eigvalsh(gram)[-1]), 1e-12)
            cache[scale] = (mean, divisor, active, float(y.mean()), True, curvature)
        values = (*cache[scale], config["factor"] / cache[scale][-1])
        for key, value in zip(params, values, strict=True):
            params[key].append(value)
    return {k: np.asarray(v) for k, v in params.items()}


def evaluate(raw, case, rep):
    parts, meta = mushroom_data(raw, case, rep)
    params = prepare(*parts[0][:2], configurations())
    indices = rng(1, case, rep, 2).integers(len(parts[0][1]), size=max(CHECKPOINTS))
    trajectories = [
        path(*parts[0][:2], params, indices, b, CHECKPOINTS) for b in BATCHES
    ]
    coefficients, status, failure_update, centered = map(
        np.array, zip(*trajectories, strict=True)
    )
    validation = losses(*parts[1], coefficients)
    rows = candidate_rows()
    selections = [
        select(validation, rows, q, int(parts[1][2].sum()))[0] for q in queries()
    ]
    arrays = dict(
        coefficients=coefficients,
        centered_intercepts=centered,
        status=status,
        failure_update=failure_update,
        indices=indices,
        validation=validation,
        train=losses(*parts[0], coefficients),
        test=losses(*parts[2], coefficients),
        selections=np.array(selections, dtype=np.int32),
        **{f"parameter_{k}": v for k, v in params.items()},
    )
    for name, ids, part in zip(
        ("train", "validation", "test"), meta.pop("partitions"), parts, strict=True
    ):
        arrays[f"partition_{name}"] = np.asarray(ids, dtype=np.int32)
        meta[f"n_{name}"] = len(part[1])
        meta[f"{name}_rare"] = int(part[2].sum())
    meta.update(case=case, rep=rep, dimension=parts[0][0].shape[1])
    return arrays, meta


def main():
    declaration()
    started, utc = time.perf_counter(), datetime.now(timezone.utc).isoformat()
    raw = load_mushroom()
    archives, replications = {}, []
    for case in range(len(SIZES)):
        for rep in range(REPS):
            arrays, meta = evaluate(raw, case, rep)
            name = f"paths-c{case}-r{rep:02d}.npz"
            np.savez_compressed(OUTPUT / name, **arrays)
            archives[name] = sha256(OUTPUT / name)
            meta["archive"] = name
            replications.append(meta)
            if (rep + 1) % 4 == 0:
                print(
                    f"n={SIZES[case][0]}, {rep + 1}/{REPS}: "
                    f"{time.perf_counter() - started:.1f}s",
                    flush=True,
                )
    write_json(
        OUTPUT / "manifest.json",
        dict(
            declaration_sha256=sha256(OUTPUT / "declaration.json"),
            sources={p: sha256(ROOT / p) for p in SOURCES},
            archives=archives,
            started_utc=utc,
            seconds=time.perf_counter() - started,
            python=platform.python_version(),
            numpy=np.__version__,
            scipy=scipy.__version__,
            machine=platform.machine(),
            configurations=configurations(),
            candidates=candidate_rows(),
            queries=queries(),
            replications=replications,
        ),
    )
    print(f"Saved {len(archives)} sensitivity archives.", flush=True)


if __name__ == "__main__":
    main()
