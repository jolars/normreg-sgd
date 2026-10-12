"""Run a named experiment and summarize its outputs from the repository root."""

import argparse
import os
import subprocess
import sys

from experiments.mushroom.config import CONFIGS as MUSHROOM_CONFIGS
from experiments.synthetic.config import CONFIGS as SYNTHETIC_CONFIGS

RUN_MODULES = {
    "mushroom": ("experiments.mushroom.run",),
    "synthetic": ("experiments.synthetic.run",),
    "exact-risk": ("experiments.exact_risk.run", "experiments.exact_risk.simulate"),
    "predictive-intro": ("experiments.predictive_intro.run",),
    "coefficient-paths": ("experiments.coefficient_paths.run",),
    "signal-allocation": ("experiments.signal_allocation.run",),
    "oracle-finite": ("experiments.oracle_finite.run",),
    "common-block": ("experiments.common_block.run",),
    "theory-bridge": ("experiments.theory_bridge.run",),
    "diagnostics": ("checks.variance_scaling", "experiments.diagnostics.run"),
    "precision": ("experiments.precision.run",),
    "calibration-sensitivity": ("experiments.theory_bridge.calibration_sensitivity",),
    "selection-gains": ("experiments.theory_bridge.selection_gains",),
    "exact-calibration": ("experiments.theory_bridge.exact_calibration",),
    "risk-decomposition": ("experiments.theory_bridge.risk_decomposition",),
}
SUMMARY_MODULES = {
    name.replace("_", "-"): (f"experiments.{name}.summarize",)
    for name in (
        "mushroom",
        "synthetic",
        "exact_risk",
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
    parser.add_argument("--config", help="Configuration for mushroom or synthetic.")
    parser.add_argument(
        "--stage",
        choices=("all", "run", "summarize"),
        default="all",
        help="Run and summarize (default), run only, or summarize saved outputs only.",
    )
    args = parser.parse_args(argv)
    if args.config is not None and args.experiment not in {"mushroom", "synthetic"}:
        parser.error("--config is supported only for mushroom and synthetic.")
    if args.config is not None:
        configs = (
            MUSHROOM_CONFIGS if args.experiment == "mushroom" else SYNTHETIC_CONFIGS
        )
        if args.config not in ("all", *configs):
            parser.error(f"--config must be one of: all, {', '.join(configs)}.")
    if args.stage == "summarize" and args.experiment not in SUMMARY_MODULES:
        parser.error("This experiment computes its summary in the run step.")

    modules = () if args.stage == "summarize" else RUN_MODULES[args.experiment]
    if args.stage != "run":
        modules += SUMMARY_MODULES.get(args.experiment, ())
    # Match the saved experiments' thread setting independently of Task.
    env = os.environ | {"OPENBLAS_NUM_THREADS": "1"}
    for module in modules:
        command = [sys.executable, "-m", module]
        if args.config is not None:
            command.extend(("--config", args.config))
        if module == "checks.variance_scaling":
            command.append("--write-audit")
        result = subprocess.run(command, env=env)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
