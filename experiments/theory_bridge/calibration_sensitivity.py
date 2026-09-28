"""Recalibrate on disjoint halves of saved shards and evaluate on held-out halves."""

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.common.data import write_json
from experiments.common.reproduction import assert_reproduced
from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.engine import choose_fixed

SEED = 20260928
PARTITIONS = 100


def selected_risks(profile, choices):
    arm, scaling, signal = np.indices(choices.shape[1:-1])
    return profile[choices[..., 0], arm, scaling, signal, choices[..., 1], 1]


def recalibrate(sums, counts, exact, q, partitions):
    """Return both orientations of each split without sharing selection data."""
    choices, risks, training_counts = [], [], []
    for left in partitions:
        assert len(set(left)) == len(left) and 0 < len(left) < len(counts)
        right = np.setdiff1d(np.arange(len(counts)), left)
        left_sum = sums[left].sum(axis=0)
        left_count = counts[left].sum()
        halves = (
            left_sum / left_count,
            sums[right].sum(axis=0) / counts[right].sum(),
        )
        for profile in halves:
            # The original study calibrates this arm from exact expected moments.
            profile[:, 0] = exact
        for train, test, count in (
            (halves[0], halves[1], left_count),
            (halves[1], halves[0], counts.sum() - left_count),
        ):
            selected = choose_fixed(train, q)
            choices.append(selected)
            risks.append(selected_risks(test, selected))
            training_counts.append(count)
    return np.array(choices), np.array(risks), np.array(training_counts)


def analyze(output, partitions=PARTITIONS, seed=SEED):
    settings = json.loads((output / "settings.json").read_text())
    assert settings["completed"]
    assert partitions > 0
    rows, arrays, run_records = [], {}, []
    for q_id, run in enumerate(settings["runs"]):
        q = run["q"]
        sums, counts = [], []
        for record in run["calibration"]:
            with np.load(output / record["file"]) as archive:
                sums.append(archive["sum_risk"])
            counts.append(record["count"])
        sums, counts = np.array(sums), np.array(counts)
        assert len(counts) >= 2 and np.all(counts > 0) and np.isfinite(sums).all()
        with np.load(output / f"q{q_id}-calibration.npz") as archive:
            exact = archive["exact_baseline"]
            original = archive["fixed"][..., 0, :]
            np.testing.assert_allclose(
                sums.sum(axis=0) / counts.sum(), archive["mean_risk"], rtol=1e-13
            )
        generator = np.random.default_rng(np.random.SeedSequence([seed, q_id]))
        left = np.array(
            [
                generator.permutation(len(counts))[: len(counts) // 2]
                for _ in range(partitions)
            ]
        )
        choices, risks, training_counts = recalibrate(sums, counts, exact, q, left)
        assert np.isfinite(risks).all()
        arrays.update(
            {
                f"q{q_id}_left_shards": left,
                f"q{q_id}_choices": choices,
                f"q{q_id}_heldout_risk": risks,
                f"q{q_id}_training_counts": training_counts,
            }
        )
        run_records.append(
            dict(
                q=q,
                shard_files=[record["file"] for record in run["calibration"]],
                shard_counts=counts.tolist(),
                training_reps_range=[
                    int(training_counts.min()),
                    int(training_counts.max()),
                ],
                heldout_reps_range=[
                    int(counts.sum() - training_counts.max()),
                    int(counts.sum() - training_counts.min()),
                ],
            )
        )
        gaps = risks[:, :, :, 1] - risks[:, :, :, 0]
        changed = (choices != original[None]).any(axis=-1).any(axis=3)
        for cap, arm, signal in np.ndindex(*gaps.shape[1:]):
            values = gaps[:, cap, arm, signal]
            matching = values < 0 if signal == 0 else values > 0
            rows.append(
                dict(
                    q=q,
                    cap=run["caps"][cap],
                    arm=cfg.ARMS[arm],
                    signal=cfg.SIGNAL_NAMES[signal],
                    splits=len(values),
                    matching_sign_count=int(matching.sum()),
                    changed_choice_count=int(changed[:, cap, arm, signal].sum()),
                    mean_gap=float(values.mean()),
                    minimum_gap=float(values.min()),
                    maximum_gap=float(values.max()),
                    gap_quantiles_10_50_90=np.quantile(
                        values, [0.1, 0.5, 0.9]
                    ).tolist(),
                )
            )
        print(f"q={q:g}: evaluated {2 * partitions} calibration halves.", flush=True)
    return dict(
        purpose=(
            "Post-review sensitivity to calibration using saved candidate risk sums."
        ),
        seed=seed,
        partitions=partitions,
        orientations_per_partition=2,
        selection="Same fine candidate family and tie rule as the original study.",
        evaluation="Each choice is evaluated only on its disjoint held-out half.",
        exact_baseline="Fresh fixed-intercept arm uses exact calibration and risk.",
        interpretation=(
            "Descriptive repeated-split sensitivity at reduced calibration size; "
            "overlapping splits are not independent replications "
            "or confidence intervals. "
            "The original evaluation sample and frozen-choice MCSEs are unchanged."
        ),
        risk_axes=["split", "cap", "arm", "scaling", "signal"],
        choice_fields=["stopping-checkpoint index", "rate-factor index"],
        runs=run_records,
        rows=rows,
    ), arrays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=cfg.OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report, arrays = analyze(args.output)
    summary = args.output / "calibration-sensitivity.json"
    archive_path = args.output / "calibration-sensitivity.npz"
    if args.check:
        assert_reproduced(report, json.loads(summary.read_text()))
        with np.load(archive_path) as archive:
            assert set(archive.files) == set(arrays)
            for key, value in arrays.items():
                if np.issubdtype(value.dtype, np.integer):
                    np.testing.assert_array_equal(value, archive[key])
                else:
                    np.testing.assert_allclose(
                        value, archive[key], rtol=1e-12, atol=1e-14
                    )
        print("Saved calibration splits, choices, and held-out risks reconstruct.")
    else:
        np.savez_compressed(archive_path, **arrays)
        write_json(summary, report)
        print(summary)


if __name__ == "__main__":
    main()
