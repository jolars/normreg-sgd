"""Run frozen experiments using recorded file hashes after history cleanup."""

import argparse
import importlib
import json
import runpy
import sys
from functools import partial
from pathlib import Path

from frozen_inputs import sha256

ROOT = Path(__file__).resolve().parents[1]
RECORDS = {
    "run_practical_selection": "results/practical-selection/synthetic.json",
    "mushroom_rate_spec": "results/mushroom-rate-search/declaration.json",
    "mushroom_sensitivity_spec": (
        "results/mushroom-scaling-sensitivity/declaration.json"
    ),
}


def preserved_hashes(record, key="preserved"):
    expected = json.loads((ROOT / record).read_text())[key]
    actual = {}
    for name, digest in expected.items():
        actual[name] = sha256(ROOT / name)
        if actual[name] != digest:
            raise ValueError(f"Preserved study changed: {name}")
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", help="Experiment module name, without .py")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    script = ROOT / "experiments" / f"{args.script}.py"
    if script.parent != ROOT / "experiments" or not script.is_file():
        parser.error("Choose a script in experiments/.")
    sys.path.insert(0, str(ROOT / "experiments"))
    # Patch before importing consumers so their hash aliases use the same policy.
    for name in ("practical_spec", "robustness_spec"):
        importlib.import_module(name).sha256 = sha256
    importlib.import_module("robustness_spec").preserved = partial(
        preserved_hashes,
        "results/normalization-robustness/specification.json",
        "preserved_sha256",
    )
    modules = {}
    # Preserve the hashed sources and declarations while replacing obsolete Git lookups.
    for name, record in RECORDS.items():
        module = importlib.import_module(name)
        module.preserved_hashes = partial(preserved_hashes, record)
        modules[name] = module
    sys.argv = [str(script.relative_to(ROOT)), *args.arguments]
    if args.script in modules:
        modules[args.script].main()
    else:
        runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
