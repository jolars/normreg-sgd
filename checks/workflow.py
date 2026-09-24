"""Exercise a small experiment outside Git and check its saved numerical results."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from numpy.testing import assert_allclose

from checks.practical_selection import reference_path
from experiments.common import data, five_rates, matched, rates25


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
    check_entry_points()
    print("Independent experiment entry points and small saved runs: passed.")
