"""Summarize saved dimension comparisons without running new trajectories."""

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.common.data import write_json
from experiments.common.reproduction import assert_reproduced
from experiments.common_block.config import OUTPUT


def summarize(output=OUTPUT):
    settings = json.loads((output / "settings.json").read_text())
    with np.load(output / "search.npz") as arrays:
        indices = arrays["risk"].argmin(axis=-1)
        risk = np.take_along_axis(arrays["risk"], indices[..., None], axis=-1)[..., 0]
        stops = np.take_along_axis(arrays["stop"], indices[..., None], axis=-1)[..., 0]
        coarse = arrays["risk"][..., settings["coarse_indices"]].min(axis=-1)
        all_rates = np.broadcast_to(
            arrays["alpha"][:, None, :, None], arrays["risk"].shape
        )
        alpha = np.take_along_axis(all_rates, indices[..., None], axis=-1)[..., 0]
        boundary = (stops > 0) & (
            (indices == 1) | (indices == len(settings["rate_fractions"]) - 1)
        )
        assert (coarse >= risk - 1e-14).all()
        assert (np.diff(risk, axis=1) <= 1e-14).all()
        report = dict(
            settings=settings,
            caps=arrays["caps"].tolist(),
            scaled_budgets=(
                arrays["caps"]
                * np.array(settings["prevalences"])[:, None]
                * (1 - np.array(settings["prevalences"])[:, None])
            ).tolist(),
            risk=risk.tolist(),
            coarse_risk=coarse.tolist(),
            selected_alpha=alpha.tolist(),
            selected_stop=stops.tolist(),
            sd_minus_unscaled=(risk[..., 1] - risk[..., 0]).tolist(),
            maximum_refinement_change=float((coarse - risk).max()),
            positive_stop_rate_boundary_selections=int(boundary.sum()),
            ordering_changes_on_refinement=int(
                (
                    np.sign(coarse[..., 1] - coarse[..., 0])
                    != np.sign(risk[..., 1] - risk[..., 0])
                ).sum()
            ),
            continuous_optimality_certified=False,
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = summarize(args.output)
    if args.check:
        assert_reproduced(
            report, json.loads((args.output / "summary.json").read_text())
        )
        print("Saved common-block summary matches the search outputs.")
    else:
        write_json(args.output / "summary.json", report)
    print(
        f"Maximum refinement change: {report['maximum_refinement_change']:.3g}; "
        f"rate boundary selections: {report['positive_stop_rate_boundary_selections']}."
    )


if __name__ == "__main__":
    main()
