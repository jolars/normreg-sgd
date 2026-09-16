"""Run all four scalings across the frozen practical samples and preprocessing arms."""

import platform
import time
from datetime import datetime, timezone

import numpy as np
import scipy
from practical_dynamics import losses
from practical_spec import (
    LAWS,
    REPS,
    ROOT,
    SIZES,
    load_mushroom,
    mushroom_data,
    rng,
    sha256,
    synthetic_data,
    write_json,
)
from run_mushroom_rate_search import path
from scipy import sparse
from variance_scaling_spec import (
    BATCHES,
    CHECKPOINTS,
    OUTPUT,
    SOURCES,
    candidate_rows,
    configurations,
    declaration,
    queries,
    select,
)


def prepare(x, y, configs, population_mean=None):
    n, d = x.shape
    mean = np.asarray(x.mean(axis=0)).ravel()
    raw = x.T @ x / n
    raw = raw.toarray() if sparse.issparse(raw) else raw
    variance = np.maximum(0, np.diag(raw) - mean**2)
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
        arm, scale = config["arm"], config["scale"]
        key = arm, scale
        if key not in cache:
            oracle = arm in ("known", "estimated_scale")
            mu = (
                population_mean
                if oracle
                else (np.zeros(d) if arm == "uncentered_fitted" else mean)
            )
            v = population_mean * (1 - population_mean) if arm == "known" else variance
            active = np.ones(d, dtype=bool) if arm == "known" else variance > 1e-14
            if scale == "none":
                divisor = np.ones(d)
            elif scale == "variance":
                divisor = v.copy()
            else:
                divisor = np.sqrt(v + (0.01 if scale == "damped" else 0))
            divisor = np.where(active, divisor, 1)
            inv = active / divisor
            # Keep the earlier arithmetic so shared paths remain a replication check.
            gram = raw - np.outer(mean, mu) - np.outer(mu, mean) + np.outer(mu, mu)
            gram = gram * np.outer(inv, inv)
            fitted = arm.endswith("fitted")
            if fitted:
                cross = (mean - mu) * inv
                gram = np.block(
                    [[gram, cross[:, None]], [cross[None, :], np.ones((1, 1))]]
                )
            curvature = max(float(np.linalg.eigvalsh(gram)[-1]), 1e-12)
            cache[key] = (
                mu,
                divisor,
                active,
                0.0 if oracle else float(y.mean()),
                fitted,
                curvature,
            )
        values = (*cache[key], config["factor"] / cache[key][-1])
        for name, value in zip(params, values, strict=True):
            params[name].append(value)
    return {k: np.asarray(v) for k, v in params.items()}


def dataset(stage, case, rep, raw=None):
    if stage == 0:
        parts, test, weights, mu = synthetic_data(case, rep)
        return [*parts, test], dict(names=["common", "rare"]), weights, mu
    parts, details = mushroom_data(raw, case, rep)
    return parts, details, None, None


def evaluate(stage, case, rep, raw=None):
    parts, meta, weights, mu = dataset(stage, case, rep, raw)
    configs, rows, qs = configurations(stage), candidate_rows(stage), queries(stage)
    params = prepare(*parts[0][:2], configs, mu)
    indices = rng(stage, case, rep, 2).integers(
        len(parts[0][1]), size=max(CHECKPOINTS[stage])
    )
    trajectories = [
        path(*parts[0][:2], params, indices, b, CHECKPOINTS[stage])
        for b in BATCHES[stage]
    ]
    coefficients, status, failures, centered = map(
        np.array, zip(*trajectories, strict=True)
    )
    validation = losses(*parts[1], coefficients)
    selections = [
        select(validation, rows, q, int(parts[1][2].sum()), stage) for q in qs
    ]
    arrays = dict(
        coefficients=coefficients,
        centered_intercepts=centered,
        status=status,
        failure_update=failures,
        indices=indices,
        validation=validation,
        train=losses(*parts[0], coefficients),
        test=losses(*parts[2], coefficients, weights),
        selections=np.array(selections, dtype=np.int32),
        **{f"parameter_{k}": v for k, v in params.items()},
    )
    if stage:
        for name, ids in zip(
            ("train", "validation", "test"), meta.pop("partitions"), strict=True
        ):
            arrays[f"partition_{name}"] = np.asarray(ids, dtype=np.int32)
    for name, part in zip(("train", "validation", "test"), parts, strict=True):
        meta[f"n_{name}"] = len(part[1])
        meta[f"{name}_rare"] = int(part[2].sum())
    meta.update(stage=stage, case=case, rep=rep, dimension=parts[0][0].shape[1])
    return arrays, meta


def main():
    declaration()
    raw = load_mushroom()
    for stage, label in enumerate(("synthetic", "mushroom")):
        started, utc = time.perf_counter(), datetime.now(timezone.utc).isoformat()
        archives, replications, store = {}, [], {}
        for case in range(len(LAWS) if stage == 0 else len(SIZES)):
            for rep in range(REPS[stage]):
                arrays, meta = evaluate(stage, case, rep, raw)
                shard = f"{label}-c{case}-r{8 * (rep // 8):03d}.npz"
                prefix = f"r{rep}_"
                store.update({prefix + k: v for k, v in arrays.items()})
                meta.update(archive=shard, prefix=prefix)
                replications.append(meta)
                if (rep + 1) % 8 == 0:
                    np.savez_compressed(OUTPUT / shard, **store)
                    archives[shard] = sha256(OUTPUT / shard)
                    store.clear()
            print(
                f"{label} case {case + 1}: {time.perf_counter() - started:.1f}s",
                flush=True,
            )
        write_json(
            OUTPUT / f"{label}.json",
            dict(
                stage=stage,
                declaration_sha256=sha256(OUTPUT / "declaration.json"),
                sources={p: sha256(ROOT / p) for p in SOURCES},
                archives=archives,
                started_utc=utc,
                seconds=time.perf_counter() - started,
                python=platform.python_version(),
                numpy=np.__version__,
                scipy=scipy.__version__,
                machine=platform.machine(),
                configurations=configurations(stage),
                candidates=candidate_rows(stage),
                queries=queries(stage),
                replications=replications,
                loss="half_squared_error; synthetic test excludes observation noise",
                selection_columns=[
                    "candidate",
                    "empty_rare_fallback",
                    "all_failed_fallback",
                ],
            ),
        )
    print("Saved both four-rule studies.", flush=True)


if __name__ == "__main__":
    main()
