"""Run the separately declared Mushroom rate expansion on paired fixed datasets."""

import platform
import time
from datetime import datetime, timezone

import numpy as np
import scipy
from mushroom_rate_spec import (
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
from practical_dynamics import losses, prepare
from practical_spec import ROOT, load_mushroom, mushroom_data, rng, sha256, write_json


def path(x, y, parameters, indices, batch, checkpoints):
    """Record failures at their first update as well as at saved checkpoints."""
    mu = parameters["mu"]
    beta = np.zeros_like(mu)
    intercept = parameters["initial"].copy()
    step = (
        parameters["eta"][:, None] * parameters["active"] / parameters["divisor"] ** 2
    )
    failure_update = np.zeros(len(beta), dtype=np.int32)
    coefficients, statuses, centered_intercepts = [], [], []

    def record():
        values = np.column_stack((intercept - np.sum(mu * beta, axis=1), beta))
        values[failure_update > 0] = np.nan
        coefficients.append(values)
        statuses.append((failure_update > 0).astype(np.uint8))
        saved_intercept = intercept.copy()
        saved_intercept[failure_update > 0] = np.nan
        # Recovering this state from a divergent raw predictor loses precision.
        centered_intercepts.append(saved_intercept)

    record()
    for processed in range(batch, max(checkpoints) + 1, batch):
        ids = indices[processed - batch : processed]
        xb = x[ids]
        raw_intercept = intercept - np.sum(mu * beta, axis=1)
        with np.errstate(over="ignore", invalid="ignore"):
            residual = xb @ beta.T + raw_intercept - y[ids, None]
            average = residual.mean(axis=0)
            gradient = (xb.T @ residual).T / batch - mu * average[:, None]
            beta -= step * gradient
            intercept -= parameters["eta"] * parameters["fit_intercept"] * average
        bad = (
            ~np.isfinite(beta).all(axis=1)
            | ~np.isfinite(intercept)
            | (np.max(np.abs(beta), axis=1) > 1e100)
            | (np.abs(intercept) > 1e100)
        )
        failure_update[(failure_update == 0) & bad] = processed // batch
        # Dead columns are zeroed so they cannot contaminate live paths.
        beta[failure_update > 0] = 0
        intercept[failure_update > 0] = 0
        if processed in checkpoints:
            record()
    return (
        np.array(coefficients),
        np.array(statuses),
        failure_update,
        np.array(centered_intercepts),
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
    declared = declaration()
    started = time.perf_counter()
    started_utc = datetime.now(timezone.utc).isoformat()
    raw = load_mushroom()
    store, replications, archives = {}, [], {}
    for case in range(len(SIZES)):
        for rep in range(REPS):
            arrays, meta = evaluate(raw, case, rep)
            shard = f"paths-c{case}-r{8 * (rep // 8):02d}.npz"
            meta["archive"] = shard
            prefix = f"c{case}_r{rep}_"
            store.update({prefix + key: value for key, value in arrays.items()})
            replications.append(meta)
            if (rep + 1) % 8 == 0:
                target = OUTPUT / shard
                np.savez_compressed(target, **store)
                archives[shard] = sha256(target)
                store.clear()
                print(
                    f"Mushroom size {SIZES[case]}, replication {rep + 1}/{REPS}: "
                    f"{time.perf_counter() - started:.1f}s",
                    flush=True,
                )
    write_json(
        OUTPUT / "manifest.json",
        dict(
            declaration_sha256=sha256(OUTPUT / "declaration.json"),
            baseline=declared["baseline"],
            sources={p: sha256(ROOT / p) for p in SOURCES},
            archives=archives,
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
