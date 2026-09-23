"""Evaluate fixed damping offsets and variance scaling on paired Mushroom splits."""

import platform
import time
from datetime import datetime, timezone

import numpy as np
import scipy

from experiments.common.data import load_mushroom, mushroom_data, rng, write_json
from experiments.common.dynamics import losses
from experiments.common.dynamics import prepare_damping as prepare
from experiments.common.dynamics import recorded_path as path
from experiments.mushroom.damping import (
    BATCHES,
    CHECKPOINTS,
    OUTPUT,
    REPS,
    SIZES,
    candidate_rows,
    configurations,
    queries,
    select,
)


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
    OUTPUT.mkdir(parents=True, exist_ok=True)
    started, utc = time.perf_counter(), datetime.now(timezone.utc).isoformat()
    raw = load_mushroom()
    archives, replications = [], []
    for case in range(len(SIZES)):
        for rep in range(REPS):
            arrays, meta = evaluate(raw, case, rep)
            name = f"paths-c{case}-r{rep:02d}.npz"
            np.savez_compressed(OUTPUT / name, **arrays)
            archives.append(name)
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
            archives=archives,
            seed=[20260916, "stage", "case", "replication", "stream"],
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
