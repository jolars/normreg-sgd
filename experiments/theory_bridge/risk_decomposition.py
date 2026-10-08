"""Decompose saved fresh-arm rare risks and measure intercept cancellation."""

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.common.data import write_json
from experiments.common.reproduction import assert_reproduced
from experiments.common.statistics import statistics
from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.selection_gains import POLICIES

TERMS = ("common", "intercept", "rare", "intercept_rare_cross")
ERRORS = ("common", "intercept", "rare")


def decompose(coefficients, truth, q):
    common = coefficients[..., 1] - truth[:, None, 0]
    intercept = coefficients[..., 0] + 0.5 * coefficients[..., 1]
    intercept += q * coefficients[..., 2]
    # The fixed-intercept arm is exactly zero in centered coordinates; converting
    # its saved raw intercept back can otherwise create spurious sign counts.
    np.testing.assert_allclose(intercept[:, :, 0], 0, atol=5e-14)
    intercept[:, :, 0] = 0
    rare = (1 - q) * (coefficients[..., 2] - truth[:, None, 1])
    errors = np.stack((common, intercept, rare), axis=-1)
    terms = np.stack(
        (common**2 / 8, intercept**2 / 2, rare**2 / 2, intercept * rare),
        axis=-1,
    )
    return errors, terms


def cancellation_summary(errors, terms):
    squared = terms[:, 1] + terms[:, 2]
    cross = terms[:, 3]
    fraction = np.divide(-cross, squared, out=np.zeros_like(cross), where=squared > 0)
    return dict(
        opposing_sign_count=int(np.sum(cross < 0)),
        zero_product_count=int(np.sum(cross == 0)),
        fraction=statistics(fraction),
        pooled_fraction=float(-cross.mean() / squared.mean())
        if squared.mean() > 0
        else None,
        error_rms={
            name: float(np.sqrt(np.mean(errors[:, i] ** 2)))
            for i, name in enumerate(ERRORS)
        },
    )


def analyze(output):
    settings = json.loads((output / "settings.json").read_text())
    assert settings["completed"]
    policy_ids = [settings["policies"].index(p) for p in POLICIES]
    arrays, rows = {}, []
    for q_id, run in enumerate(settings["runs"]):
        chunks = []
        for record in run["evaluation"]:
            with np.load(output / record["file"]) as archive:
                chunks.append(archive["coefficients"][:, :, :2, :, :, policy_ids])
        coefficients = np.concatenate(chunks)
        assert len(coefficients) == settings["evaluation_reps"]
        assert np.isfinite(coefficients).all()
        errors, terms = decompose(
            coefficients, np.asarray(settings["signals"]), run["q"]
        )
        arrays[f"q{q_id}_errors"] = errors
        arrays[f"q{q_id}_terms"] = terms
        for cap, arm, signal, policy in np.ndindex(
            len(run["caps"]), 2, len(settings["signals"]), len(POLICIES)
        ):
            values = terms[:, cap, arm, :, signal, policy]
            gap = values[:, 1] - values[:, 0]
            calibrated = terms[:, cap, arm, :, signal, 0]
            gain = calibrated - values
            row = dict(
                q=run["q"],
                cap=run["caps"][cap],
                arm=settings["arms"][arm],
                signal=settings["signal_names"][signal],
                policy=POLICIES[policy],
                scaling={
                    name: dict(
                        terms={
                            term: statistics(values[:, s, i])
                            for i, term in enumerate(TERMS)
                        },
                        risk=statistics(values[:, s].sum(axis=-1)),
                        gain_terms={
                            term: statistics(gain[:, s, i])
                            for i, term in enumerate(TERMS)
                        },
                        cancellation=cancellation_summary(
                            errors[:, cap, arm, s, signal, policy], values[:, s]
                        ),
                    )
                    for s, name in enumerate(settings["scalings"])
                },
                gap_terms={term: statistics(gap[:, i]) for i, term in enumerate(TERMS)},
                gap=statistics(gap.sum(axis=-1)),
                gap_without_cross=statistics(gap[:, :3].sum(axis=-1)),
                gap_with_zero_intercept=statistics(gap[:, [0, 2]].sum(axis=-1)),
                gap_change_terms={
                    term: statistics(gain[:, 0, i] - gain[:, 1, i])
                    for i, term in enumerate(TERMS)
                },
            )
            rows.append(row)
    return arrays, dict(
        predictor="a + b_C (I - 1/2) + b_R (J - q)",
        error_definition={
            "common": "b_C - beta_C",
            "intercept": "a = raw_intercept + b_C/2 + q*b_R; true a is zero",
            "rare": "d = (1-q)*(b_R-beta_R)",
        },
        term_definition=dict(
            common="e_C^2/8",
            intercept="a^2/2",
            rare="d^2/2",
            intercept_rare_cross="a*d",
        ),
        cancellation_definition=(
            "-a*d / ((a^2+d^2)/2), zero for a=d=0. The pooled fraction uses "
            "means before division; 1 is complete cancellation, -1 reinforcement."
        ),
        interpretation=(
            "Descriptive decomposition of already selected saved predictors. "
            "Omitting the cross term is an accounting diagnostic, not a predictor "
            "risk. Setting a=0 is a predictor intervention without retraining or "
            "reselection; it does not estimate the fixed-intercept training arm."
        ),
        gap_definition="SD minus U; gap change is U gain minus SD gain",
        uncertainty="Paired MCSEs conditional on frozen calibration choices.",
        array_axes=["replication", "cap", "arm", "scaling", "signal", "policy"],
        error_axis=list(ERRORS),
        term_axis=list(TERMS),
        arms=settings["arms"][:2],
        scalings=settings["scalings"],
        signals=settings["signal_names"],
        policies=list(POLICIES),
        runs=[dict(q=run["q"], caps=run["caps"]) for run in settings["runs"]],
        evaluation_reps=settings["evaluation_reps"],
        rows=rows,
    )


def decomposition_table(report):
    lines = [
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"Selection & Scaling & Common & Intercept & Rare & Cross & Total \\",
        r"\midrule",
    ]
    for arm, label in (
        ("fresh_intercept", "Fitted intercept"),
        ("fresh", "Fixed zero intercept (baseline)"),
    ):
        lines.append(r"\multicolumn{7}{l}{" + label + r"} \\")
        for policy, label in (
            ("calibrated", "Calibrated"),
            ("path_oracle", "Exact risk"),
            ("validation_2048", "Validation (2048)"),
        ):
            row = next(
                r
                for r in report["rows"]
                if r["arm"] == arm
                and r["policy"] == policy
                and r["q"] == 0.02
                and r["cap"] == 204
                and r["signal"] == "rare"
            )
            for name, scaling in (("none", "U"), ("sd", "SD")):
                data = row["scaling"][name]
                numbers = [data["terms"][t]["mean"] for t in TERMS]
                numbers.append(data["risk"]["mean"])
                values = " & ".join(f"${v:.4f}$" for v in numbers)
                lines.append(f"{label} & {scaling} & {values} " + r"\\")
        lines.append(r"\midrule" if arm == "fresh_intercept" else r"\bottomrule")
    lines.append(r"\end{tabular}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=cfg.OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    arrays, report = analyze(args.output)
    destination = args.output / "risk-decomposition"
    table = cfg.ROOT / "paper/generated/risk-decomposition.tex"
    if args.check:
        assert_reproduced(
            report, json.loads(destination.with_suffix(".json").read_text())
        )
        with np.load(destination.with_suffix(".npz")) as saved:
            assert set(saved.files) == set(arrays)
            for name, values in arrays.items():
                np.testing.assert_array_equal(saved[name], values)
        assert table.read_text() == decomposition_table(report)
        print(
            "Saved risk decompositions, cancellation summaries, and table reconstruct."
        )
    else:
        np.savez_compressed(destination.with_suffix(".npz"), **arrays)
        write_json(destination.with_suffix(".json"), report)
        table.parent.mkdir(parents=True, exist_ok=True)
        table.write_text(decomposition_table(report))
        print(destination)


if __name__ == "__main__":
    main()
