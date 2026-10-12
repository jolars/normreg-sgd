"""Run a named experiment and summarize its outputs from the repository root."""

import argparse
import os
import subprocess
import sys

RUN_MODULES = {
    "predictive-intro": ("experiments.predictive_intro.run",),
    "coefficient-paths": ("experiments.coefficient_paths.run",),
    "oracle-finite": ("experiments.oracle_finite.run",),
    "common-block": ("experiments.common_block.run",),
    "theory-bridge": ("experiments.theory_bridge.run",),
    "calibration-sensitivity": ("experiments.theory_bridge.calibration_sensitivity",),
    "selection-gains": ("experiments.theory_bridge.selection_gains",),
    "exact-calibration": ("experiments.theory_bridge.exact_calibration",),
    "risk-decomposition": ("experiments.theory_bridge.risk_decomposition",),
}
SUMMARY_MODULES = {
    name.replace("_", "-"): (f"experiments.{name}.summarize",)
    for name in (
        "oracle_finite",
        "common_block",
        "theory_bridge",
    )
}


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m experiments",
        description=__doc__,
        epilog="Available experiments and analyses:\n  " + "\n  ".join(RUN_MODULES),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("experiment", choices=RUN_MODULES, metavar="NAME")
    parser.add_argument(
        "--stage",
        choices=("all", "run", "summarize"),
        default="all",
        help="Run and summarize (default), run only, or summarize saved outputs only.",
    )
    args = parser.parse_args(argv)
    if args.stage == "summarize" and args.experiment not in SUMMARY_MODULES:
        parser.error("This experiment computes its summary in the run step.")

    modules = () if args.stage == "summarize" else RUN_MODULES[args.experiment]
    if args.stage != "run":
        modules += SUMMARY_MODULES.get(args.experiment, ())
    # Match the saved experiments' thread setting independently of Task.
    env = os.environ | {"OPENBLAS_NUM_THREADS": "1"}
    for module in modules:
        command = [sys.executable, "-m", module]
        result = subprocess.run(command, env=env)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
