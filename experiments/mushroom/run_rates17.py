"""Run the 17-factor Mushroom search on paired data partitions."""

import platform
import time
from datetime import datetime, timezone

import numpy as np
import scipy

from experiments.common.data import load_mushroom, mushroom_data, rng, write_json
from experiments.common.dynamics import losses, prepare
from experiments.common.dynamics import recorded_path as path
from experiments.mushroom.rates17 import (
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
    parameters = prepare(*parts[0][:2], configurations())
    indices = rng(1, case, rep, 2).integers(len(parts[0][1]), size=max(CHECKPOINTS))
    trajectories = [
        path(*parts[0][:2], parameters, indices, batch, CHECKPOINTS)
        for batch in BATCHES
    ]
    coefficients, status, failures, centered_intercepts = map(
        np.array, zip(*trajectories, strict=True)
    )
    validation = losses(*parts[1], coefficients)
    rows = candidate_rows()
    selections = [
        select(validation, rows, q, int(parts[1][2].sum()))[0] for q in queries()
    ]
    arrays = dict(
        coefficients=coefficients,
        centered_intercepts=centered_intercepts,
        status=status,
        failure_update=failures,
        indices=indices,
        validation=validation,
        test=losses(*parts[2], coefficients),
        train=losses(*parts[0], coefficients),
        selections=np.array(selections, dtype=np.int32),
    )
    arrays.update({f"parameter_{k}": v for k, v in parameters.items()})
    for name, ids in zip(
        ("train", "validation", "test"), meta.pop("partitions"), strict=True
    ):
        arrays[f"partition_{name}"] = np.array(ids, dtype=np.int32)
    meta.update(case=case, rep=rep, dimension=parts[0][0].shape[1])
    for name, (x, y, rare) in zip(("train", "validation", "test"), parts, strict=True):
        meta[f"n_{name}"] = len(y)
        meta[f"{name}_rare"] = int(rare.sum())
        meta[f"{name}_nnz"] = int(x.nnz)
    return arrays, meta


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    started_utc = datetime.now(timezone.utc).isoformat()
    raw = load_mushroom()
    store, replications, archives = {}, [], []
    for case in range(len(SIZES)):
        for rep in range(REPS):
            arrays, meta = evaluate(raw, case, rep)
            shard = f"paths-c{case}-r{8 * (rep // 8):02d}.npz"
            meta["archive"] = shard
            prefix = f"c{case}_r{rep}_"
            store.update({prefix + key: value for key, value in arrays.items()})
            replications.append(meta)
            if (rep + 1) % 8 == 0 or rep + 1 == REPS:
                target = OUTPUT / shard
                np.savez_compressed(target, **store)
                archives.append(shard)
                store.clear()
                print(
                    f"Mushroom size {SIZES[case]}, replication {rep + 1}/{REPS}: "
                    f"{time.perf_counter() - started:.1f}s",
                    flush=True,
                )
    write_json(
        OUTPUT / "manifest.json",
        dict(
            archives=archives,
            seed=[20260916, "stage", "case", "replication", "stream"],
            started_utc=started_utc,
            seconds=time.perf_counter() - started,
            python=platform.python_version(),
            numpy=np.__version__,
            scipy=scipy.__version__,
            machine=platform.machine(),
            configurations=configurations(),
            candidates=candidate_rows(),
            queries=queries(),
            replications=replications,
            coefficient_coordinates=(
                "raw_intercept, training-vocabulary original-scale coefficients"
            ),
            failure_update=(
                "zero if live through 8192 observations; first failed update otherwise"
            ),
            selection_columns=[
                "candidate",
                "empty_rare_fallback",
                "all_failed_fallback",
            ],
            loss="half_squared_error_on_observed_labels",
        ),
    )
    print(f"Saved {len(archives)} path archives in {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
