"""Summarize the saved bridge study without training or changing selections."""

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.common.data import jsonable, write_json
from experiments.common.reproduction import assert_reproduced
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
                losses.append(
                    predictor_risks(archive["coefficients"], q, settings["signals"])
                )
                selections.append(archive["selected"])
                coverage.append(archive["validation_rare_count"])
                train_counts.append(
                    (archive["cells"][:, : settings["train_size"]] % 2).sum(-1)
                )
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
                arm=settings["arms"][arm],
                signal=settings["signal_names"][signal],
                policy=settings["policies"][policy],
                gap=statistics(gap[:, cap, arm, signal, policy]),
                scaling={},
            )
            if policy >= 3:
                present = coverage[:, policy - 3] > 0
                row["validation_coverage"] = {
                    label: statistics(gap[mask, cap, arm, signal, policy])
                    for label, mask in (("absent", ~present), ("present", present))
                }
            for scaling, name in enumerate(settings["scalings"]):
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
                        np.sum(
                            positive
                            & (choice[:, 1] == len(settings["rate_factors"]) - 1)
                        )
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
            for cap, signal in np.ndindex(len(run["caps"]), len(settings["signals"])):
                contrasts.append(
                    dict(
                        q=q,
                        cap=run["caps"][cap],
                        signal=settings["signal_names"][signal],
                        reference=settings["arms"][base],
                        intervention=settings["arms"][changed],
                        gap_change=statistics(
                            gap[:, cap, changed, signal, 0]
                            - gap[:, cap, base, signal, 0]
                        ),
                        risk_change={
                            name: statistics(
                                loss[:, cap, changed, s, signal, 0, 1]
                                - loss[:, cap, base, s, signal, 0, 1]
                            )
                            for s, name in enumerate(settings["scalings"])
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
        for cap, scaling, signal in np.ndindex(
            len(run["caps"]), len(settings["scalings"]), len(settings["signals"])
        ):
            stop, rate = fixed[cap, 0, scaling, signal, 0]
            expected = float(exact[stop, scaling, signal, rate, 1])
            observed = statistics(loss[:, cap, 0, scaling, signal, 0, 1])
            baseline.append(
                dict(
                    cap=run["caps"][cap],
                    scaling=settings["scalings"][scaling],
                    signal=settings["signal_names"][signal],
                    exact_risk=expected,
                    evaluation=observed,
                    z_score=(observed["mean"] - expected) / observed["mcse"]
                    if observed["mcse"] is not None and observed["mcse"] > 0
                    else None,
                    grid_excess=expected - float(dense[cap, scaling, signal]),
                )
            )
        for cap, arm, scaling, signal in np.ndindex(
            len(run["caps"]),
            len(settings["arms"]),
            len(settings["scalings"]),
            len(settings["signals"]),
        ):
            stop, rate = fixed[cap, arm, scaling, signal, 0]
            optimism.append(
                dict(
                    cap=run["caps"][cap],
                    arm=settings["arms"][arm],
                    scaling=settings["scalings"][scaling],
                    signal=settings["signal_names"][signal],
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
                    for v, n in enumerate(settings["validation_sizes"])
                ],
                failed_evaluation_candidates=failed,
                failed_calibration_candidates=sum(
                    r["failed_candidates"] for r in run["calibration"]
                ),
                exact_baseline=baseline,
                calibration_comparison=optimism,
                fine_calibrated_upper_boundaries=int(
                    np.sum(fixed[..., 0, 1] == len(settings["rate_factors"]) - 1)
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
        arms=settings["arms"],
        arm_labels=settings["arm_labels"],
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
        assert_reproduced(
            jsonable(report), json.loads((args.output / "summary.json").read_text())
        )
        print("Saved bridge summaries reconstruct within numerical tolerance.")
    else:
        write_json(args.output / "summary.json", report)
        print(args.output / "summary.json")


if __name__ == "__main__":
    main()
