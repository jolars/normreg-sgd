"""Exercise current experiment entry points and a small saved bridge run."""

import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
from numpy.testing import assert_allclose

from checks.theory_bridge import cell_risks, reference_paths
from experiments import __main__ as experiments_cli
from experiments.theory_bridge import config as cfg
from experiments.theory_bridge import run as bridge_run
from experiments.theory_bridge.engine import choose_fixed, predictor_risks


def check_small_run():
    with (
        tempfile.TemporaryDirectory() as directory,
        patch.object(cfg, "TRAIN_SIZE", 8),
        patch.object(cfg, "rates", return_value=np.array([0.0, 0.1, 0.5])),
        patch.object(cfg, "budgets", return_value=np.array([1, 2, 4])),
        patch.object(cfg, "stops", return_value=np.array([0, 1, 2, 4])),
    ):
        output = Path(directory)
        q = cfg.PREVALENCES[0]
        calibration = bridge_run.worker(output, 0, 0, 0, 2, None)
        profile = bridge_run.mean_profile(output, [calibration])
        fixed = np.stack(
            (choose_fixed(profile, q), choose_fixed(profile, q, True)), axis=-2
        )
        evaluation = bridge_run.worker(output, 0, 1, 0, 2, fixed)
        assert calibration["failed_candidates"] == 0
        assert evaluation["failed_candidates"] == 0
        with np.load(output / evaluation["file"]) as archive:
            data = {key: archive[key] for key in archive.files}
        assert "sum_risk" not in data
        coefficients = data["coefficients"]
        assert_allclose(predictor_risks(coefficients, q), cell_risks(coefficients, q))
        for rep in range(2):
            reference = reference_paths(data, q, rep)
            selected = data["selected"][rep]
            for cap, arm, scaling, signal, policy in np.ndindex(*selected.shape[:-1]):
                stop, rate = selected[cap, arm, scaling, signal, policy]
                assert_allclose(
                    coefficients[rep, cap, arm, scaling, signal, policy],
                    reference[stop, arm, scaling, signal, rate],
                    atol=1e-12,
                )
    print("Small calibration and evaluation archives pass independent path checks.")


def check_entry_points():
    for module in (
        "experiments",
        "experiments.coefficient_paths.run",
        "experiments.predictive_intro.run",
        "experiments.oracle_finite.run",
        "experiments.oracle_finite.summarize",
        "experiments.theory_bridge.run",
        "experiments.theory_bridge.summarize",
        "experiments.theory_bridge.calibration_sensitivity",
        "experiments.theory_bridge.selection_gains",
        "experiments.theory_bridge.exact_calibration",
        "experiments.theory_bridge.risk_decomposition",
    ):
        subprocess.run(
            [sys.executable, "-m", module, "--help"],
            check=True,
            capture_output=True,
            text=True,
        )


def check_named_experiments():
    """Check stage isolation and failure handling without running full studies."""
    with patch.object(experiments_cli.subprocess, "run") as run:
        run.return_value = Mock(returncode=0)
        assert experiments_cli.main(["theory-bridge"]) == 0
        assert [call.args[0] for call in run.call_args_list] == [
            [sys.executable, "-m", module]
            for module in (
                "experiments.theory_bridge.run",
                "experiments.theory_bridge.summarize",
            )
        ]
        assert all(
            call.kwargs["env"]["OPENBLAS_NUM_THREADS"] == "1"
            for call in run.call_args_list
        )
        for stage, module in (
            ("run", "experiments.theory_bridge.run"),
            ("summarize", "experiments.theory_bridge.summarize"),
        ):
            run.reset_mock()
            assert experiments_cli.main(["theory-bridge", "--stage", stage]) == 0
            assert run.call_args.args[0] == [sys.executable, "-m", module]
            assert run.call_count == 1

        run.reset_mock()
        assert experiments_cli.main(["risk-decomposition"]) == 0
        assert run.call_args.args[0] == [
            sys.executable,
            "-m",
            "experiments.theory_bridge.risk_decomposition",
        ]
        assert run.call_count == 1

        run.reset_mock()
        run.return_value = Mock(returncode=7)
        assert experiments_cli.main(["theory-bridge"]) == 7
        assert run.call_count == 1

        for arguments in (
            ["missing"],
            ["theory-bridge", "--config", "missing"],
            ["predictive-intro", "--stage", "summarize"],
        ):
            run.reset_mock()
            with (
                redirect_stderr(StringIO()),
                np.testing.assert_raises(SystemExit) as raised,
            ):
                experiments_cli.main(arguments)
            assert raised.exception.code == 2
            run.assert_not_called()
    print("Named experiments isolate stages and stop after failed runs.")


if __name__ == "__main__":
    check_small_run()
    check_entry_points()
    check_named_experiments()
    print("Independent experiment entry points and small saved runs: passed.")
