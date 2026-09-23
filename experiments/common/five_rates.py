"""Reproduce the practical-preprocessing and sparse categorical experiments."""

import platform
import time

import numpy as np
import scipy

from experiments.common.data import (
    ARMS,
    LAWS,
    MUSHROOM_M,
    REPS,
    SCALES,
    SIZES,
    SYNTHETIC_M,
    configurations,
    load_mushroom,
    mushroom_data,
    result_dir,
    rng,
    synthetic_data,
    write_json,
)
from experiments.common.dynamics import candidates, choose, losses, path, prepare


def queries(stage):
    result = []
    for arm in ARMS if stage == 0 else ARMS[2:]:
        for cap in (SYNTHETIC_M if stage == 0 else MUSHROOM_M)[1:]:
            for objective in range(2):
                for scale in SCALES:
                    for rule in ("fixed", "rate_batch", "joint"):
                        result.append(
                            dict(
                                arm=arm,
                                cap=cap,
                                objective=objective,
                                scale=scale,
                                rule=rule,
                            )
                        )
                result.append(
                    dict(
                        arm=arm,
                        cap=cap,
                        objective=objective,
                        scale="all",
                        rule="joint_scaling",
                    )
                )
    return result


def evaluate(stage, case, rep, raw=None):
    configs = configurations(stage)
    checkpoints = SYNTHETIC_M if stage == 0 else MUSHROOM_M
    batches = (1, 16) if stage == 0 else (16, 128)
    if stage == 0:
        parts, test, weights, mu = synthetic_data(case, rep)
        details = dict(names=["common", "rare"])
    else:
        partitions, details = mushroom_data(raw, case, rep)
        parts, test = partitions[:2], partitions[2]
        weights, mu = None, None
    x, y, rare = parts[0]
    params = prepare(x, y, configs, mu)
    indices = rng(stage, case, rep, 2).integers(len(y), size=max(checkpoints))
    paths, statuses = zip(
        *(path(x, y, params, indices, b, checkpoints) for b in batches), strict=True
    )
    coefficients, status = np.array(paths), np.array(statuses)
    validation = losses(*parts[1], coefficients)
    test_loss = losses(*test, coefficients, weights)
    train_loss = losses(x, y, rare, coefficients)
    rows = candidates(configs, batches, checkpoints)
    selections = []
    for query in queries(stage):
        selected, fallback, failure, eligible = choose(
            validation, rows, **query, validation_rare_count=int(parts[1][2].sum())
        )
        objective = query["objective"]
        finite = [
            i
            for i in eligible
            if np.isfinite(test_loss[tuple(rows[i]["index"])][objective])
        ]
        oracle = (
            min(finite, key=lambda i: test_loss[tuple(rows[i]["index"])][objective])
            if finite
            else -1
        )
        selections.append([selected, int(fallback), int(failure), oracle])
    details.update(
        stage=stage,
        case=case,
        rep=rep,
        n=len(y),
        n_validation=len(parts[1][1]),
        n_test=len(test[1]),
        train_rare=int(rare.sum()),
        validation_rare=int(parts[1][2].sum()),
        test_rare=int(test[2].sum()),
        dimension=x.shape[1],
        nnz=int(x.nnz) if scipy.sparse.issparse(x) else int(np.count_nonzero(x)),
    )
    arrays = dict(
        coefficients=coefficients,
        status=status,
        validation=validation,
        test=test_loss,
        train=train_loss,
        selections=np.array(selections, dtype=np.int32),
        indices=indices,
    )
    arrays.update({f"parameter_{k}": v for k, v in params.items()})
    if "partitions" in details:
        for name, idx in zip(
            ("train", "validation", "test"), details.pop("partitions"), strict=True
        ):
            arrays[f"partition_{name}"] = np.array(idx, dtype=np.int32)
    return arrays, details


def run(stage, output=None):
    label = ("synthetic", "mushroom")[stage]
    output = result_dir(label, "rates5") if output is None else output
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    raw = load_mushroom() if stage else None
    store, details = {}, []
    for case in range(len(LAWS) if stage == 0 else len(SIZES)):
        for rep in range(REPS[stage]):
            arrays, meta = evaluate(stage, case, rep, raw)
            prefix = f"c{case}_r{rep}_"
            store.update({prefix + key: value for key, value in arrays.items()})
            details.append(meta)
        print(
            f"{label}: case {case + 1} completed "
            f"({time.perf_counter() - started:.1f}s)",
            flush=True,
        )
    target = output / f"{label}.npz"
    np.savez_compressed(target, **store)
    checkpoints = SYNTHETIC_M if stage == 0 else MUSHROOM_M
    batches = (1, 16) if stage == 0 else (16, 128)
    manifest = dict(
        stage=stage,
        seed=[20260916, "stage", "case", "replication", "stream"],
        label=label,
        python=platform.python_version(),
        numpy=np.__version__,
        scipy=scipy.__version__,
        configurations=configurations(stage),
        candidates=candidates(configurations(stage), batches, checkpoints),
        queries=queries(stage),
        replications=details,
        seconds=time.perf_counter() - started,
        loss="half_squared_error; synthetic test excludes observation noise",
        selection_columns=[
            "candidate",
            "empty_rare_fallback",
            "all_failed_fallback",
            "hindsight_candidate",
        ],
    )
    write_json(output / f"{label}.json", manifest)
    print(f"Saved {target}", flush=True)
