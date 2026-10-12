"""Exercise current experiment entry points and a small saved bridge run."""

import json
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
from experiments.common.data import write_json
from experiments.common.reproduction import assert_reproduced
from experiments.common_block import summarize as common_summary
from experiments.theory_bridge import config as cfg
from experiments.theory_bridge import risk_decomposition, selection_gains
from experiments.theory_bridge import run as bridge_run
from experiments.theory_bridge import summarize as bridge_summary
from experiments.theory_bridge.engine import choose_fixed, predictor_risks


def check_saved_summary_settings():
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        q = 0.02
        settings = dict(
            purpose="Small saved-summary regression.",
            completed=True,
            calibration_reps=4,
            evaluation_reps=4,
            train_size=2,
            signals=cfg.SIGNALS.tolist(),
            signal_names=list(cfg.SIGNAL_NAMES),
            scalings=list(cfg.SCALINGS),
            arms=list(cfg.ARMS),
            arm_labels=list(cfg.ARM_LABELS),
            policies=list(cfg.POLICIES[:3]) + ["validation_3"],
            validation_sizes=[3],
            rate_factors=[0.0, 0.1, 0.5],
            runs=[
                dict(
                    q=q,
                    caps=[2],
                    checkpoints=[0, 2],
                    calibration=[dict(failed_candidates=0)],
                    evaluation=[dict(file="evaluation.npz", count=4)],
                )
            ],
        )
        write_json(output / "settings.json", settings)
        shape = (4, 1, 8, 2, 2, 4)
        coefficients = np.zeros((*shape, 3))
        coefficients[..., 1] = np.arange(4).reshape(4, 1, 1, 1, 1, 1) / 10
        coefficients[..., 0] = -0.5 * coefficients[..., 1]
        selected = np.ones((*shape, 2), dtype=int)
        selected[..., 1] = 2
        np.savez_compressed(
            output / "evaluation.npz",
            coefficients=coefficients,
            selected=selected,
            cells=np.tile([0, 2, 1, 3], (4, 1)),
            validation_rare_count=np.array([[0], [1], [0], [1]]),
            failure_checkpoint=np.zeros(4, dtype=int),
        )
        np.savez_compressed(
            output / "q0-calibration.npz",
            fixed=np.ones((1, 8, 2, 2, 2, 2), dtype=int),
            exact_baseline=np.zeros((2, 2, 2, 3, 2)),
            dense_baseline_risk=np.zeros((1, 2, 2)),
            mean_risk=np.zeros((2, 8, 2, 2, 3, 2)),
        )
        report = bridge_summary.summarize(output)
        assert report["diagnostics"][0]["missing_training"] == 4
        assert report["diagnostics"][0]["validation"][0]["size"] == 3
        assert report["rows"][0]["scaling"]["none"]["upper_rate_boundary"] == 4
        gains, gain_report = selection_gains.analyze(output)
        terms, term_report = risk_decomposition.analyze(output)
        assert gain_report["policies"] == ["calibrated", "path_oracle", "validation_3"]
        with (
            patch.object(cfg, "TRAIN_SIZE", 1),
            patch.object(cfg, "SIGNALS", np.array([[7.0, 8.0]])),
            patch.object(cfg, "SIGNAL_NAMES", ("changed",)),
            patch.object(cfg, "ARMS", ("changed",)),
            patch.object(cfg, "ARM_LABELS", ("changed",)),
            patch.object(cfg, "SCALINGS", ("changed",)),
            patch.object(cfg, "POLICIES", ("changed",)),
            patch.object(cfg, "VALIDATION_SIZES", (1,)),
            patch.object(cfg, "rates", side_effect=AssertionError("Live rate grid")),
        ):
            assert_reproduced(bridge_summary.summarize(output), report)
            new_gains, new_gain_report = selection_gains.analyze(output)
            new_terms, new_term_report = risk_decomposition.analyze(output)
            assert_reproduced(new_gain_report, gain_report)
            assert_reproduced(new_term_report, term_report)
            for name in gains:
                np.testing.assert_array_equal(new_gains[name], gains[name])
            for name in terms:
                np.testing.assert_array_equal(new_terms[name], terms[name])
        write_json(output / "summary.json", report)
        rounded = json.loads((output / "summary.json").read_text())
        rounded["rows"][0]["gap"]["mean"] = float(
            np.nextafter(rounded["rows"][0]["gap"]["mean"], np.inf)
        )
        write_json(output / "summary.json", rounded)
        with patch.object(
            sys, "argv", ["summarize", "--output", str(output), "--check"]
        ):
            bridge_summary.main()
        with np.load(output / "evaluation.npz") as archive:
            data = {key: archive[key] for key in archive.files}
        data["coefficients"][:] = 0
        np.savez_compressed(output / "evaluation.npz", **data)
        constant = bridge_summary.summarize(output)
        assert all(
            row["z_score"] is None
            for row in constant["diagnostics"][0]["exact_baseline"]
        )
        write_json(output / "summary.json", constant)
    print("Saved bridge settings survive configuration changes and numerical roundoff.")


def check_common_summary():
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        write_json(
            output / "settings.json",
            dict(
                coarse_indices=[0, 2],
                rate_fractions=[0.0, 0.1, 0.5],
                prevalences=[0.02],
            ),
        )
        np.savez_compressed(
            output / "search.npz",
            risk=np.array([3.0, 1.0, 2.0, 3.0, 2.0, 1.0]).reshape(1, 1, 1, 1, 2, 3),
            stop=np.array([0, 2, 1, 0, 1, 2]).reshape(1, 1, 1, 1, 2, 3),
            alpha=np.array([0.0, 0.1, 0.5, 0.0, 0.2, 1.0]).reshape(1, 1, 2, 3),
            caps=np.array([[2]]),
        )
        report = common_summary.summarize(output)
        assert report["selected_alpha"] == [[[[[0.1, 1.0]]]]]
        write_json(output / "summary.json", report)
        saved = (output / "summary.json").read_bytes()
        arguments = ["summarize", "--output", str(output), "--check"]
        with patch.object(sys, "argv", arguments):
            common_summary.main()
        assert (output / "summary.json").read_bytes() == saved
        report["selected_stop"][0][0][0][0][0] = 1
        write_json(output / "summary.json", report)
        with (
            patch.object(sys, "argv", arguments),
            np.testing.assert_raises(AssertionError),
        ):
            common_summary.main()
    print("Common-block summary checks replay choices without writing results.")


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
        "experiments.common_block.summarize",
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
    check_saved_summary_settings()
    check_common_summary()
    check_small_run()
    check_entry_points()
    check_named_experiments()
    print("Independent experiment entry points and small saved runs: passed.")
