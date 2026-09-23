"""Compare four scalings on sampled synthetic or Mushroom data."""

import platform
import time
from datetime import datetime, timezone

import numpy as np
import scipy

from experiments.common.data import (
    LAWS,
    REPS,
    SIZES,
    load_mushroom,
    mushroom_data,
    result_dir,
    rng,
    synthetic_data,
    write_json,
)
from experiments.common.dynamics import losses
from experiments.common.dynamics import prepare_scalings as prepare
from experiments.common.dynamics import recorded_path as path
from experiments.common.rates25 import (
    BATCHES,
    CHECKPOINTS,
    candidate_rows,
    configurations,
    queries,
    select,
)


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


def run(stage, output=None):
    label = ("synthetic", "mushroom")[stage]
    output = result_dir(label, "rates25") if output is None else output
    output.mkdir(parents=True, exist_ok=True)
    raw = load_mushroom() if stage else None
    started, utc = time.perf_counter(), datetime.now(timezone.utc).isoformat()
    archives, replications, store = [], [], {}
    for case in range(len(LAWS) if stage == 0 else len(SIZES)):
        for rep in range(REPS[stage]):
            arrays, meta = evaluate(stage, case, rep, raw)
            shard = f"{label}-c{case}-r{8 * (rep // 8):03d}.npz"
            prefix = f"r{rep}_"
            store.update({prefix + k: v for k, v in arrays.items()})
            meta.update(archive=shard, prefix=prefix)
            replications.append(meta)
            if (rep + 1) % 8 == 0 or rep + 1 == REPS[stage]:
                np.savez_compressed(output / shard, **store)
                archives.append(shard)
                store.clear()
        print(
            f"{label} case {case + 1}: {time.perf_counter() - started:.1f}s",
            flush=True,
        )
    write_json(
        output / f"{label}.json",
        dict(
            stage=stage,
            seed=[20260916, "stage", "case", "replication", "stream"],
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
