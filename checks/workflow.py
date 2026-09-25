"""Exercise a small experiment outside Git and check its saved numerical results."""

import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import numpy as np
from numpy.testing import assert_allclose

from checks.practical_selection import reference_path
from experiments.common import data, five_rates, matched, rates25
from experiments.signal_allocation import run as signal_allocation


def check_signal_allocation_summary():
    """Allow floating-point rounding while rejecting changed saved results."""
    report = dict(
        model=dict(q=0.0001, independent=True),
        search=dict(
            alpha=[0.0, 1e-6, 0.4],
            coarse_alpha=[0.0, 0.4],
            stops=[0, 1, 100],
            coarse_stops=[0, 100],
            max_risk_change_on_joint_refinement=2e-5,
            max_tensor_error=3e-13,
            tensor_replays=112,
            continuous_optimality_certified=False,
        ),
        observation_caps=[100],
        axes=["cap", "noise variance", "rare signal fraction", "scaling"],
        scalings=["Unscaled", "Standardized"],
        risk=[[[[0.1, 0.2]]]],
        coarse_risk=[[[[0.10002, 0.20001]]]],
        selected_alpha=[[[[1e-6, 0.4]]]],
        selected_stop=[[[[100, 100]]]],
    )

    def changed(path, value):
        candidate = deepcopy(report)
        target = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return candidate

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        summary = output / "summary.json"
        content = json.dumps(report, indent=2) + "\n"
        summary.write_text(content)

        def check(candidate):
            with (
                patch.object(signal_allocation, "OUTPUT", output),
                patch.object(signal_allocation, "calculate", return_value=candidate),
                patch.object(sys, "argv", ["signal-allocation", "--check"]),
            ):
                signal_allocation.main()
            assert summary.read_text() == content

        for path, value in (
            (("risk", 0, 0, 0, 0), 0.1),
            (("coarse_risk", 0, 0, 0, 0), 0.10002),
            (("selected_alpha", 0, 0, 0, 0), 1e-6),
            (("search", "alpha", 1), 1e-6),
            (("search", "coarse_alpha", 1), 0.4),
            (("search", "max_tensor_error"), 3e-13),
            (("search", "max_risk_change_on_joint_refinement"), 2e-5),
        ):
            check(changed(path, float(np.nextafter(value, np.inf))))

        content = json.dumps(report, sort_keys=True)
        summary.write_text(content)
        check(report)
        for path, value in (
            (("risk", 0, 0, 0, 0), 0.1000001),
            (("coarse_risk", 0, 0, 0, 0), 0.10003),
            (("selected_alpha", 0, 0, 0, 0), 1e-6 + 1e-13),
            (("selected_stop", 0, 0, 0, 0), 99),
            (("model", "q"), 0.00010000000001),
            (("model", "independent"), False),
            (("search", "alpha", 0), 1e-20),
            (("search", "coarse_stops", 1), 99),
            (("search", "tensor_replays"), 111),
            (("search", "max_tensor_error"), 1e-8),
            (("search", "max_risk_change_on_joint_refinement"), 3e-5),
            (("observation_caps", 0), 101),
            (("axes", 0), "signal"),
            (("risk",), 0.1),
            (("risk", 0, 0, 0, 0), float("nan")),
            (("risk", 0, 0, 0, 0), float("inf")),
        ):
            with np.testing.assert_raises(AssertionError):
                check(changed(path, value))
        for candidate in (
            {**report, "unexpected": 1},
            {k: v for k, v in report.items() if k != "risk"},
        ):
            with np.testing.assert_raises(AssertionError):
                check(candidate)
    print("Signal-allocation checks tolerate rounding and reject changed results.")


def check_small_run():
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        checkpoints = (0, 16, 32)
        with (
            patch.object(five_rates, "LAWS", data.LAWS[:1]),
            patch.object(five_rates, "REPS", (1, 0)),
            patch.object(five_rates, "SYNTHETIC_M", checkpoints),
            patch.object(five_rates, "load_mushroom", side_effect=AssertionError),
        ):
            five_rates.run(0, output / "rates5")
        manifest = json.loads((output / "rates5/synthetic.json").read_text())
        assert len(manifest["replications"]) == 1
        parts, _, _, _ = data.synthetic_data(0, 0)
        with np.load(output / "rates5/synthetic.npz") as archive:
            params = {
                key.removeprefix("c0_r0_parameter_"): archive[key]
                for key in archive.files
                if key.startswith("c0_r0_parameter_")
            }
            for batch_id, batch in enumerate((1, 16)):
                expected = reference_path(
                    *parts[0][:2], params, archive["c0_r0_indices"], batch, checkpoints
                )
                assert_allclose(
                    archive["c0_r0_coefficients"][batch_id], expected, atol=1e-12
                )
        # A single replication also exercises the final incomplete output shard.
        with (
            patch.object(matched, "LAWS", data.LAWS[:1]),
            patch.object(matched, "REPS", (1, 0)),
            patch.object(matched, "CHECKPOINTS", (checkpoints, checkpoints)),
            patch.object(rates25, "CHECKPOINTS", (checkpoints, checkpoints)),
            patch.object(rates25, "ORIGINAL_STOPS", (checkpoints, checkpoints)),
            patch.object(matched, "load_mushroom", side_effect=AssertionError),
        ):
            rates25.eligible_ids.cache_clear()
            matched.run(0, output / "rates25")
            rates25.eligible_ids.cache_clear()
        manifest = json.loads((output / "rates25/synthetic.json").read_text())
        assert len(manifest["replications"]) == 1
        assert len(manifest["archives"]) == 1
        for name in manifest["archives"]:
            with np.load(output / "rates25" / name) as archive:
                assert archive["r0_coefficients"].shape[:2] == (2, 3)
                assert np.isfinite(archive["r0_validation"][:, 0]).all()


def check_entry_points():
    for module in (
        "experiments.mushroom.run",
        "experiments.mushroom.summarize",
        "experiments.synthetic.run",
        "experiments.synthetic.summarize",
        "experiments.exact_risk.run",
        "experiments.exact_risk.simulate",
        "experiments.exact_risk.summarize",
        "experiments.predictive_intro.run",
        "experiments.signal_allocation.run",
        "experiments.oracle_finite.run",
        "experiments.oracle_finite.summarize",
        "experiments.diagnostics.run",
        "experiments.precision.run",
        "experiments.theory_bridge.run",
        "experiments.theory_bridge.summarize",
    ):
        subprocess.run(
            [sys.executable, "-m", module, "--help"],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    check_small_run()
    check_signal_allocation_summary()
    check_entry_points()
    print("Independent experiment entry points and small saved runs: passed.")
