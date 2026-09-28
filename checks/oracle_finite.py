"""Independently replay finite-prevalence comparisons and search selections."""

import argparse
import json
from fractions import Fraction

import numpy as np

from checks.oracle_limits import reference_risk
from checks.predictive_theorem import observation_operator
from experiments.common.reproduction import assert_reproduced
from experiments.oracle_finite.config import OUTPUT, cases
from experiments.oracle_finite.run import search
from experiments.oracle_finite.summarize import summarize


def check_small_search():
    """Enumerate the full observation tensor at every candidate independently."""
    q = Fraction(1, 25)
    rows = [
        dict(s=0.01, r=1, noise=1, tau=1),
        dict(s=1, r=0.01, noise=1, tau=2),
        dict(s=1, r=0, noise=0, tau=2),
        dict(s=0, r=0, noise=1, tau=1),
    ]
    result = search(float(q), rows, resolution=16)
    expected = np.full_like(result["risk"], np.inf)
    for scaling in range(2):
        for ri, alpha in enumerate(result["rates"][scaling]):
            operator = np.asarray(
                observation_operator(q, Fraction(float(alpha)), bool(scaling)),
                dtype=float,
            )
            for ci, row in enumerate(rows):
                moment = np.array(
                    [
                        row["s"],
                        np.sqrt(row["s"] * row["r"]),
                        np.sqrt(row["s"] * row["r"]),
                        row["r"],
                        row["noise"],
                    ]
                )
                for stop in range(int(result["cap"][ci]) + 1):
                    match = np.flatnonzero(result["stops"] == stop)
                    if len(match):
                        risk = moment[0] / 8 + float((1 - q) ** 2) * moment[3] / 2
                        for grid in range(4):
                            if grid < 2 and not result["coarse_stop"][match[0]]:
                                continue
                            if grid % 2 == 0 and not result["coarse_rate"][ri]:
                                continue
                            expected[ci, grid, scaling] = min(
                                expected[ci, grid, scaling], risk
                            )
                    moment = operator @ moment
    np.testing.assert_allclose(result["risk"], expected, atol=3e-13, rtol=1e-12)
    print("All four nested search combinations match independent tensor enumeration.")


def check_saved(rerun=False):
    settings = json.loads((OUTPUT / "settings.json").read_text())
    assert_reproduced(cases(), settings["cases"])
    report = json.loads((OUTPUT / "summary.json").read_text())
    replays, max_error = 0, 0.0
    with np.load(OUTPUT / "search.npz") as archive:
        assert_reproduced(summarize(settings, archive), report)
        for qi, q in enumerate(settings["prevalences"]):
            risks, alphas, stops = [
                archive[f"q{qi}_{key}"] for key in ("risk", "alpha", "stop")
            ]
            caps = archive[f"q{qi}_cap"]
            assert (stops <= caps[:, None, None]).all()
            assert (stops >= 0).all()
            assert np.isin(stops, archive[f"q{qi}_stops"]).all()
            assert np.isfinite(risks).all() and (risks >= 0).all()
            active = stops[:, 3] > 0
            indices = archive[f"q{qi}_rate_index"][:, 3]
            assert (
                (indices[active] > 1)
                & (indices[active] < archive[f"q{qi}_rates"].shape[-1] - 1)
            ).all()
            assert (risks[:, :3] >= risks[:, 3, None] - 1e-12).all()
            assert (risks[:, 0] >= risks[:, 1:3].max(axis=1) - 1e-12).all()
            assert np.max(risks[:, :3] - risks[:, 3, None]) < 5e-5
            for ci, row in enumerate(settings["cases"]):
                for grid, scaling in np.ndindex(4, 2):
                    rate = float(alphas[ci, grid, scaling])
                    stop = int(stops[ci, grid, scaling])
                    index = archive[f"q{qi}_rate_index"][ci, grid, scaling]
                    assert rate == archive[f"q{qi}_rates"][scaling, index]
                    if grid % 2 == 0:
                        assert archive[f"q{qi}_coarse_rate"][index]
                    if grid < 2:
                        assert (
                            stop
                            in archive[f"q{qi}_stops"][archive[f"q{qi}_coarse_stop"]]
                        )
                    actual = reference_risk(
                        Fraction(str(q)),
                        rate,
                        bool(scaling),
                        stop,
                        row["s"],
                        row["r"],
                        row["noise"],
                    )
                    error = abs(actual - risks[ci, grid, scaling])
                    max_error = max(max_error, error)
                    np.testing.assert_allclose(
                        actual, risks[ci, grid, scaling], atol=2e-8, rtol=1e-8
                    )
                    replays += 1
            if rerun:
                replay = search(q, settings["cases"], settings["resolution"])
                for key, value in replay.items():
                    np.testing.assert_allclose(
                        value, archive[f"q{qi}_{key}"], rtol=1e-12, atol=1e-13
                    )
                print(
                    f"Recomputed every saved candidate selection at q={q:g}.",
                    flush=True,
                )
    errors = np.array(
        [row["maximum_absolute_risk_error_U_S"] for row in report["convergence"]]
    )
    # At coarse prevalences, a one-observation cap cannot approximate tau=0.01.
    # The predicted limit does not require monotone errors along those caps.
    assert (np.diff(errors[1:], axis=0) < 0).all()
    assert errors[-1].max() < 3e-4
    fine_rows = {
        row["name"]: row
        for row in report["rows"]
        if row["q"] == settings["prevalences"][-1]
    }
    assert [
        np.sign(fine_rows[f"noise-{nu:g}"]["finite_gap_S_minus_U"])
        for nu in (0, 0.1, 1, 100)
    ] == [1, -1, -1, 1]
    assert fine_rows["budget-1"]["finite_gap_S_minus_U"] > 0
    assert fine_rows["budget-10"]["finite_gap_S_minus_U"] < 0
    for tau in (1, 2, 4):
        assert fine_rows[f"common-crossing-{tau}-0.9"]["finite_gap_S_minus_U"] < 0
        assert fine_rows[f"common-crossing-{tau}-1.1"]["finite_gap_S_minus_U"] > 0
    for row in fine_rows.values():
        if abs(row["nominal_limiting_gap_S_minus_U"]) > 1e-8:
            assert row["finite_gap_S_minus_U"] * row["limiting_gap_S_minus_U"] > 0
    # The high-noise comparison remains reversed at moderate prevalence.
    # Retaining this mismatch prevents interpreting the limits as finite-q rules.
    for row in report["rows"]:
        if row["name"] == "noise-100" and row["q"] >= 0.0002:
            assert row["finite_gap_S_minus_U"] < -5e-4
            assert row["limiting_gap_S_minus_U"] > 0.002
    for row in report["rows"]:
        if row["group"] == "anchors":
            gap = row["finite_gap_S_minus_U"]
            assert gap < 0 if row["s"] < row["r"] else gap > 0
        if row["name"] in ("pure-noise", "zero"):
            assert row["finite_risk"] == [0, 0]
    print(
        f"{replays} independent long-double tensor replays; "
        f"maximum risk error {max_error:.3g}."
    )
    print(
        "Saved comparisons, convergence, transition signs, and degenerate cases passed."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rerun", action="store_true", help="Also recompute every saved search."
    )
    args = parser.parse_args()
    check_small_search()
    check_saved(args.rerun)


if __name__ == "__main__":
    main()
