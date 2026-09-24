"""Summarize the saved bridge study without training or changing selections."""

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.common.data import write_json
from experiments.common.statistics import statistics
from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.engine import predictor_risks

EDGES = ((0, 1), (0, 2), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6), (6, 7))


def summarize(output):
    settings = json.loads((output / "settings.json").read_text())
    if not settings["completed"]:
        raise ValueError("The experiment has not finished.")
    rows, contrasts, diagnostics = [], [], []
    for q_id, run in enumerate(settings["runs"]):
        q = run["q"]
        losses, selections, coverage, train_counts = [], [], [], []
        failed = 0
        for record in run["evaluation"]:
            with np.load(output / record["file"]) as archive:
                losses.append(predictor_risks(archive["coefficients"], q))
                selections.append(archive["selected"])
                coverage.append(archive["validation_rare_count"])
                train_counts.append((archive["cells"][:, : cfg.TRAIN_SIZE] % 2).sum(-1))
                failed += int(np.count_nonzero(archive["failure_checkpoint"]))
        loss = np.concatenate(losses)
        selected = np.concatenate(selections)
        coverage = np.concatenate(coverage)
        train_counts = np.concatenate(train_counts)
        gap = loss[:, :, :, 1, :, :, 1] - loss[:, :, :, 0, :, :, 1]
        for cap, arm, signal, policy in np.ndindex(*gap.shape[1:]):
            row = dict(
                q=q,
                cap=run["caps"][cap],
                expected_rare=run["caps"][cap] * q,
                arm=cfg.ARMS[arm],
                signal=cfg.SIGNAL_NAMES[signal],
                policy=cfg.POLICIES[policy],
                gap=statistics(gap[:, cap, arm, signal, policy]),
                scaling={},
            )
            if policy >= 3:
                present = coverage[:, policy - 3] > 0
                row["validation_coverage"] = {
                    label: statistics(gap[mask, cap, arm, signal, policy])
                    for label, mask in (("absent", ~present), ("present", present))
                }
            for scaling, name in enumerate(cfg.SCALINGS):
                risk = loss[:, cap, arm, scaling, signal, policy]
                oracle = loss[:, cap, arm, scaling, signal, 2, 1]
                reference = loss[:, cap, arm, scaling, signal, 0, 1]
                choice = selected[:, cap, arm, scaling, signal, policy]
                positive = np.asarray(run["checkpoints"])[choice[:, 0]] > 0
                row["scaling"][name] = dict(
                    aggregate=statistics(risk[:, 0]),
                    rare=statistics(risk[:, 1]),
                    selection_regret=statistics(risk[:, 1] - oracle),
                    minus_calibrated=statistics(risk[:, 1] - reference),
                    positive_stop_count=int(positive.sum()),
                    lower_rate_boundary=int(np.sum(positive & (choice[:, 1] == 1))),
                    upper_rate_boundary=int(
                        np.sum(positive & (choice[:, 1] == len(cfg.rates()) - 1))
                    ),
                    median_stop=float(
                        np.median(np.asarray(run["checkpoints"])[choice[:, 0]])
                    ),
                )
                if policy >= 3:
                    row["scaling"][name]["validation_coverage"] = {
                        label: statistics(risk[mask, 1])
                        for label, mask in (("absent", ~present), ("present", present))
                    }
            rows.append(row)
        for base, changed in EDGES:
            for cap, signal in np.ndindex(len(run["caps"]), 2):
                contrasts.append(
                    dict(
                        q=q,
                        cap=run["caps"][cap],
                        signal=cfg.SIGNAL_NAMES[signal],
                        reference=cfg.ARMS[base],
                        intervention=cfg.ARMS[changed],
                        gap_change=statistics(
                            gap[:, cap, changed, signal, 0]
                            - gap[:, cap, base, signal, 0]
                        ),
                        risk_change={
                            name: statistics(
                                loss[:, cap, changed, s, signal, 0, 1]
                                - loss[:, cap, base, s, signal, 0, 1]
                            )
                            for s, name in enumerate(cfg.SCALINGS)
                        },
                    )
                )
        with np.load(output / f"q{q_id}-calibration.npz") as archive:
            fixed = archive["fixed"]
            exact = archive["exact_baseline"]
            dense = archive["dense_baseline_risk"]
            calibration = archive["mean_risk"]
        baseline = []
        optimism = []
        for cap, scaling, signal in np.ndindex(len(run["caps"]), 2, 2):
            stop, rate = fixed[cap, 0, scaling, signal, 0]
            expected = float(exact[stop, scaling, signal, rate, 1])
            observed = statistics(loss[:, cap, 0, scaling, signal, 0, 1])
            baseline.append(
                dict(
                    cap=run["caps"][cap],
                    scaling=cfg.SCALINGS[scaling],
                    signal=cfg.SIGNAL_NAMES[signal],
                    exact_risk=expected,
                    evaluation=observed,
                    z_score=(observed["mean"] - expected) / observed["mcse"],
                    grid_excess=expected - float(dense[cap, scaling, signal]),
                )
            )
        for cap, arm, scaling, signal in np.ndindex(
            len(run["caps"]), len(cfg.ARMS), 2, 2
        ):
            stop, rate = fixed[cap, arm, scaling, signal, 0]
            optimism.append(
                dict(
                    cap=run["caps"][cap],
                    arm=cfg.ARMS[arm],
                    scaling=cfg.SCALINGS[scaling],
                    signal=cfg.SIGNAL_NAMES[signal],
                    calibration_risk=float(
                        calibration[stop, arm, scaling, signal, rate, 1]
                    ),
                    evaluation=statistics(loss[:, cap, arm, scaling, signal, 0, 1]),
                )
            )
        diagnostics.append(
            dict(
                q=q,
                missing_training=int(np.sum(train_counts == 0)),
                validation=[
                    dict(
                        size=n,
                        expected_count=n * q,
                        empty=int(np.sum(coverage[:, v] == 0)),
                        probability_empty=(1 - q) ** n,
                    )
                    for v, n in enumerate(cfg.VALIDATION_SIZES)
                ],
                failed_evaluation_candidates=failed,
                failed_calibration_candidates=sum(
                    r["failed_candidates"] for r in run["calibration"]
                ),
                exact_baseline=baseline,
                calibration_comparison=optimism,
                fine_calibrated_upper_boundaries=int(
                    np.sum(fixed[..., 0, 1] == len(cfg.rates()) - 1)
                ),
                fine_calibrated_lower_boundaries=int(np.sum(fixed[..., 0, 1] == 1)),
            )
        )
    return dict(
        purpose=settings["purpose"],
        calibration_reps=settings["calibration_reps"],
        evaluation_reps=settings["evaluation_reps"],
        gap_definition="SD minus unscaled rare excess half squared loss",
        uncertainty="Paired MCSE conditional on the saved calibration choices.",
        candidate_family="Conservative stable finite rate and stopping grids.",
        arms=cfg.ARMS,
        arm_labels=cfg.ARM_LABELS,
        rows=rows,
        matched_interventions=contrasts,
        diagnostics=diagnostics,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=cfg.OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = summarize(args.output)
    if args.check:
        assert json.loads((args.output / "summary.json").read_text()) == json.loads(
            json.dumps(report)
        )
        print("Saved bridge summaries reconstruct exactly.")
    else:
        write_json(args.output / "summary.json", report)
        print(args.output / "summary.json")


if __name__ == "__main__":
    main()
