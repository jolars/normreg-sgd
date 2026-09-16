"""Recreate missing large outputs without changing the frozen study records."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/normalization-robustness"


def verify(path, expected):
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise ValueError(f"Frozen hash mismatch: {path}. Existing files were retained.")


def run(script, output):
    subprocess.run(
        [sys.executable, f"experiments/{script}.py", "--output", str(output)],
        cwd=ROOT,
        check=True,
    )


def main():
    spec = json.loads((OUTPUT / "specification.json").read_text())
    figures = json.loads((OUTPUT / "figures.json").read_text())
    expected = {
        "paths.npz": spec["paths_sha256"],
        "summary.json": figures["summary_sha256"],
    }
    for name, digest in spec["sha256"].items():
        verify(ROOT / name, digest)
    missing = []
    for name, digest in expected.items():
        if (OUTPUT / name).exists():
            verify(OUTPUT / name, digest)
        else:
            missing.append(name)
    if missing:
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="results-", dir=ROOT / "build") as tmp:
            temporary = Path(tmp)
            if "paths.npz" in missing:
                print("Recreating the frozen robustness moment archive.", flush=True)
                run("run_normalization_robustness", temporary)
                verify(temporary / "paths.npz", expected["paths.npz"])
                (temporary / "paths.npz").replace(OUTPUT / "paths.npz")
            if "summary.json" in missing:
                # Reuse the recorded simulation, including its failed covariance gate.
                for name in (
                    "specification.json",
                    "boundary-probes.json",
                    "paired-simulation.npz",
                    "simulation-summary.json",
                ):
                    shutil.copyfile(OUTPUT / name, temporary / name)
                os.link(OUTPUT / "paths.npz", temporary / "paths.npz")
                print("Recreating the frozen robustness summary.", flush=True)
                run("summarize_normalization_robustness", temporary)
                verify(temporary / "summary.json", expected["summary.json"])
                (temporary / "summary.json").replace(OUTPUT / "summary.json")
    print("Local robustness artifacts match their frozen SHA-256 hashes.", flush=True)


if __name__ == "__main__":
    main()
