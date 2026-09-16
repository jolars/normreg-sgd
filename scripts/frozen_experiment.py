"""Run frozen experiments using recorded file hashes after history cleanup."""

import argparse
import hashlib
import importlib
import json
import runpy
import sys
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = {
    "run_practical_selection": "results/practical-selection/synthetic.json",
    "mushroom_rate_spec": "results/mushroom-rate-search/declaration.json",
    "mushroom_sensitivity_spec": (
        "results/mushroom-scaling-sensitivity/declaration.json"
    ),
}


def preserved_hashes(record):
    expected = json.loads((ROOT / record).read_text())["preserved"]
    actual = {}
    for name, digest in expected.items():
        with (ROOT / name).open("rb") as stream:
            actual[name] = hashlib.file_digest(stream, "sha256").hexdigest()
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
