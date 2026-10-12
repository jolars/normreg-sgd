"""Analyze paired selection gains and errors from saved fresh-arm predictors."""

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.common.data import write_json
from experiments.common.reproduction import assert_arrays_reproduced, assert_reproduced
from experiments.common.statistics import statistics
from experiments.theory_bridge import config as cfg


def selection_policies(settings):
    return ("calibrated", "path_oracle", *settings["policies"][3:])


def distribution(values):
    return {
        **statistics(values),
        "p05": float(np.quantile(values, 0.05)),
        "p25": float(np.quantile(values, 0.25)),
        "p75": float(np.quantile(values, 0.75)),
        "minimum": float(np.min(values)),
        "positive_count": int(np.sum(values > 0)),
        "negative_count": int(np.sum(values < 0)),
        "zero_count": int(np.sum(values == 0)),
    }


def error_summary(errors):
    return {
        name: dict(
            signed=statistics(errors[:, i]),
            absolute=distribution(np.abs(errors[:, i])),
            rms=float(np.sqrt(np.mean(errors[:, i] ** 2))),
        )
        for i, name in enumerate(("common_coefficient", "rare_mean_prediction"))
    }


def analyze(output):
    settings = json.loads((output / "settings.json").read_text())
    assert settings["completed"]
    rows, arrays = [], {}
    policies = selection_policies(settings)
    policy_ids = [settings["policies"].index(policy) for policy in policies]
    for q_id, run in enumerate(settings["runs"]):
        chunks = []
        for record in run["evaluation"]:
            with np.load(output / record["file"]) as archive:
                chunks.append(archive["coefficients"][:, :, :2, :, :, policy_ids])
        coefficients = np.concatenate(chunks)
        assert len(coefficients) == settings["evaluation_reps"]
        assert np.isfinite(coefficients).all()
        q = run["q"]
        truth = np.asarray(settings["signals"])
        common = coefficients[..., 1] - truth[None, None, None, None, :, None, 0]
        # Averaging the two rare cells preserves their signed prediction error.
        rare_mean = coefficients[..., 0] + 0.5 * coefficients[..., 1]
        rare_mean += (
            coefficients[..., 2] - (1 - q) * truth[None, None, None, None, :, None, 1]
        )
        errors = np.stack((common, rare_mean), axis=-1)
        risk = common**2 / 8 + rare_mean**2 / 2
        gains = risk[..., :1] - risk[..., 1:]
        arrays[f"q{q_id}_risk"] = risk
        arrays[f"q{q_id}_gain"] = gains
        arrays[f"q{q_id}_errors"] = errors
        for cap, arm, signal, policy in np.ndindex(
            len(run["caps"]), 2, len(settings["signals"]), len(policies) - 1
        ):
            gain = gains[:, cap, arm, :, signal, policy]
            advantage = gain[:, 0] - gain[:, 1]
            scaling = {}
            for s, name in enumerate(settings["scalings"]):
                values = gain[:, s]
                positive = np.maximum(values, 0)
                tail_size = int(np.ceil(0.1 * len(values)))
                scaling[name] = dict(
                    gain=distribution(values),
                    positive_gain_top_decile_share=(
                        float(np.sort(positive)[-tail_size:].sum() / positive.sum())
                        if positive.sum() > 0
                        else None
                    ),
                    calibrated_error=error_summary(errors[:, cap, arm, s, signal, 0]),
                    selected_error=error_summary(
                        errors[:, cap, arm, s, signal, policy + 1]
                    ),
                )
            rows.append(
                dict(
                    q=q,
                    cap=run["caps"][cap],
                    arm=settings["arms"][arm],
                    signal=settings["signal_names"][signal],
                    policy=policies[policy + 1],
                    scaling=scaling,
                    unscaled_minus_sd_gain=distribution(advantage),
                    calibrated_gap=statistics(
                        risk[:, cap, arm, 1, signal, 0]
                        - risk[:, cap, arm, 0, signal, 0]
                    ),
                    selected_gap=statistics(
                        risk[:, cap, arm, 1, signal, policy + 1]
                        - risk[:, cap, arm, 0, signal, policy + 1]
                    ),
                )
            )
    return arrays, dict(
        gain_definition="Calibrated minus selected population rare excess half loss.",
        interpretation=(
            "Descriptive per-run finite-family selection gains, conditional on frozen "
            "calibration choices. Exact-selection mean gains combine theoretical "
            "finite-family adaptation gains with calibration suboptimality; the "
            "latter is zero only when calibration chooses the true expected-risk "
            "minimum, as in the baseline. The theorem optimizes deterministic "
            "rates and stops, not adaptive selection."
        ),
        error_definition={
            "common_coefficient": "b_C - beta_C",
            "rare_mean_prediction": "Mean signed prediction error over two rare cells.",
            "risk": "common_coefficient^2 / 8 + rare_mean_prediction^2 / 2",
        },
        array_axes=["replication", "cap", "arm", "scaling", "signal", "policy"],
        error_axis=["common_coefficient", "rare_mean_prediction"],
        policies=list(policies),
        gain_policies=list(policies[1:]),
        arms=settings["arms"][:2],
        scalings=settings["scalings"],
        signals=settings["signal_names"],
        runs=[dict(q=run["q"], caps=run["caps"]) for run in settings["runs"]],
        evaluation_reps=settings["evaluation_reps"],
        uncertainty="Paired MCSEs exclude calibration uncertainty.",
        rows=rows,
    )


def gain_table(report):
    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Selection & Scaling & Median & 5th pct. & 95th pct. & Worse (\%) \\",
        r"\midrule",
    ]
    for arm, label in (
        ("fresh_intercept", "Fitted intercept"),
        ("fresh", "Fixed zero intercept (baseline)"),
    ):
        lines.append(r"\multicolumn{6}{l}{\emph{" + label + r"}} \\")
        for policy, label in (
            ("path_oracle", "Exact risk"),
            ("validation_2048", "Validation (2048)"),
        ):
            row = next(
                row
                for row in report["rows"]
                if row["arm"] == arm
                and row["policy"] == policy
                and row["q"] == 0.02
                and row["cap"] == 204
                and row["signal"] == "rare"
            )
            for name, scaling in (("none", "U"), ("sd", "SD")):
                gain = row["scaling"][name]["gain"]
                numbers = " & ".join(
                    f"${gain[k]:.4f}$" for k in ("median", "p05", "p95")
                )
                worse = 100 * gain["negative_count"] / gain["n"]
                lines.append(
                    f"{label} & {scaling} & {numbers} & ${worse:.1f}$ " + r"\\"
                )
        lines.append(r"\midrule" if arm == "fresh_intercept" else r"\bottomrule")
    lines.append(r"\end{tabular}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=cfg.OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    arrays, report = analyze(args.output)
    destination = args.output / "selection-gains"
    table = cfg.ROOT / "paper/generated/selection-gains.tex"
    if args.check:
        assert_reproduced(
            report, json.loads(destination.with_suffix(".json").read_text())
        )
        with np.load(destination.with_suffix(".npz")) as saved:
            assert_arrays_reproduced(arrays, saved)
        assert table.read_text() == gain_table(report)
        print("Saved selection gains and errors reconstruct within tolerance.")
    else:
        np.savez_compressed(destination.with_suffix(".npz"), **arrays)
        write_json(destination.with_suffix(".json"), report)
        table.parent.mkdir(parents=True, exist_ok=True)
        table.write_text(gain_table(report))
        print(destination)


if __name__ == "__main__":
    main()
