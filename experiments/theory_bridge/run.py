"""Run independent calibration and evaluation for the controlled bridge study."""

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import scipy

from experiments.common.data import write_json
from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.engine import (
    choose_fixed,
    exact_baseline,
    sample,
    simulate,
)


def worker(output, q_id, stage, first, count, fixed):
    started = time.perf_counter()
    data = sample(q_id, stage, first, count)
    result = simulate(data, cfg.PREVALENCES[q_id], fixed)
    if stage == 1:
        # Evaluation retains selected predictors and raw draws; only calibration
        # needs the full candidate risk sums to reconstruct its frozen choices.
        del result["sum_risk"]
    name = f"q{q_id}-{('calibration', 'evaluation')[stage]}-{first:05d}.npz"
    np.savez_compressed(output / name, **data, **result)
    return dict(
        file=name,
        first=first,
        count=count,
        seconds=time.perf_counter() - started,
        failed_candidates=int(np.count_nonzero(result["failure_checkpoint"])),
    )


def stage_run(output, q_id, stage, reps, chunk_size, workers, fixed):
    tasks = [
        (first, min(chunk_size, reps - first)) for first in range(0, reps, chunk_size)
    ]
    records = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(worker, output, q_id, stage, first, count, fixed)
            for first, count in tasks
        ]
        for future in as_completed(futures):
            records.append(future.result())
            print(
                f"q={cfg.PREVALENCES[q_id]:g}, "
                f"{('calibration', 'evaluation')[stage]}: "
                f"{len(records)}/{len(tasks)} chunks",
                flush=True,
            )
    return sorted(records, key=lambda r: r["first"])


def mean_profile(output, records):
    total = None
    count = 0
    for record in records:
        with np.load(output / record["file"]) as archive:
            value = archive["sum_risk"]
        total = value.copy() if total is None else total + value
        count += record["count"]
    return total / count


def manifest(args):
    return dict(
        purpose="Matched departures from the fresh-sample oracle setting.",
        seed=cfg.SEED,
        prevalences=cfg.PREVALENCES,
        signals=cfg.SIGNALS,
        signal_names=cfg.SIGNAL_NAMES,
        scalings=cfg.SCALINGS,
        arms=cfg.ARMS,
        arm_labels=cfg.ARM_LABELS,
        policies=cfg.POLICIES,
        train_size=cfg.TRAIN_SIZE,
        validation_sizes=cfg.VALIDATION_SIZES,
        rate_factors=cfg.rates(),
        learning_rate="factor / maximum squared transformed norm over four cells",
        calibration_reps=args.calibration_reps,
        evaluation_reps=args.evaluation_reps,
        coefficient_order=["raw intercept", "common", "rare"],
        coefficient_axes=[
            "replication",
            "cap",
            "arm",
            "scaling",
            "signal",
            "policy",
            "coefficient",
        ],
        selection_fields=["stopping-checkpoint index", "rate-factor index"],
        profile_axes=["stop", "arm", "scaling", "signal", "rate", "risk objective"],
        evaluation_profile_sums_saved=False,
        risk_objectives=["aggregate", "rare"],
        selection=(
            "Independent calibration; validation uses rare loss "
            "with aggregate fallback."
        ),
        initialization="Zero except the final arm's training-mean intercept.",
        failure_rule="Nonfinite coefficients or magnitude above 1e100 at a checkpoint.",
        protocol="experiments/theory_bridge/PROTOCOL.md",
        software=dict(
            python=platform.python_version(),
            numpy=np.__version__,
            scipy=scipy.__version__,
        ),
        workers=args.workers,
        chunk_size=args.chunk_size,
        openblas_threads=os.environ.get("OPENBLAS_NUM_THREADS"),
        completed=False,
        runs=[],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=cfg.OUTPUT)
    parser.add_argument("--calibration-reps", type=int, default=cfg.CALIBRATION_REPS)
    parser.add_argument("--evaluation-reps", type=int, default=cfg.EVALUATION_REPS)
    parser.add_argument("--chunk-size", type=int, default=cfg.CHUNK_SIZE)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if (
        min(args.calibration_reps, args.evaluation_reps, args.chunk_size, args.workers)
        < 1
    ):
        parser.error("Replication counts, chunk size, and workers must be positive.")
    args.output.mkdir(parents=True, exist_ok=True)
    report = manifest(args)
    write_json(args.output / "settings.json", report)
    started = time.perf_counter()
    for q_id, q in enumerate(cfg.PREVALENCES):
        records = stage_run(
            args.output,
            q_id,
            0,
            args.calibration_reps,
            args.chunk_size,
            args.workers,
            None,
        )
        profile = mean_profile(args.output, records)
        baseline = exact_baseline(q, cfg.rates(), cfg.stops(q))
        calibrated_profile = profile.copy()
        calibrated_profile[:, 0] = baseline
        fixed = np.stack(
            (
                choose_fixed(calibrated_profile, q),
                choose_fixed(calibrated_profile, q, True),
            ),
            axis=-2,
        )
        dense = exact_baseline(q, cfg.rates(1024), np.arange(cfg.budgets(q)[-1] + 1))
        dense_risk = np.array(
            [dense[: cap + 1, ..., 1].min(axis=(0, 3)) for cap in cfg.budgets(q)]
        )
        np.savez_compressed(
            args.output / f"q{q_id}-calibration.npz",
            mean_risk=profile,
            exact_baseline=baseline,
            fixed=fixed,
            dense_baseline_risk=dense_risk,
        )
        run = dict(
            q=q,
            caps=cfg.budgets(q),
            checkpoints=cfg.stops(q),
            calibration=records,
            evaluation=[],
        )
        report["runs"].append(run)
        write_json(args.output / "settings.json", report)
        run["evaluation"] = stage_run(
            args.output,
            q_id,
            1,
            args.evaluation_reps,
            args.chunk_size,
            args.workers,
            fixed,
        )
        write_json(args.output / "settings.json", report)
    report["seconds"] = time.perf_counter() - started
    report["completed"] = True
    write_json(args.output / "settings.json", report)
    print(json.dumps(dict(completed=True, seconds=report["seconds"])), flush=True)


if __name__ == "__main__":
    main()
