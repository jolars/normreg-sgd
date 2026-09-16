"""Declared fixed-offset comparisons on the primary Mushroom preprocessing arm."""

import argparse
import itertools
import json
import subprocess
from datetime import datetime, timezone

import numpy as np
from mushroom_rate_spec import (
    BATCHES,
    CHECKPOINTS,
    FACTORS,
    ORIGINAL_STOPS,
)
from mushroom_rate_spec import REPS as REPS
from mushroom_rate_spec import SIZES as SIZES
from practical_dynamics import candidates
from practical_spec import ROOT, sha256, write_json

OUTPUT = ROOT / "results/mushroom-scaling-sensitivity"
PROTOCOL = "notes/mushroom-scaling-sensitivity.md"
BASELINE = "94ed9b4931c8b648ce6ec3aab3f32e4cb53041f0"
TAUS = (0.001, 0.003, 0.01, 0.03, 0.1)
SCALES = ("none", "sd", "variance", *(f"damped_{t:g}" for t in TAUS))
ARM = "centered_fitted"
SOURCES = (
    PROTOCOL,
    "experiments/mushroom_sensitivity_spec.py",
    "experiments/run_mushroom_sensitivity.py",
    "experiments/summarize_mushroom_sensitivity.py",
    "experiments/check_mushroom_sensitivity.py",
    "experiments/practical_spec.py",
    "experiments/practical_dynamics.py",
    "experiments/mushroom_rate_spec.py",
    "experiments/run_mushroom_rate_search.py",
    "experiments/check_mushroom_rate_search.py",
    "experiments/summarize_mushroom_rate_search.py",
    "experiments/summarize_practical_selection.py",
    "uv.lock",
    "data/mushroom/agaricus-lepiota.data",
    "data/mushroom/agaricus-lepiota.names",
    "data/mushroom/README.md",
)


def configurations():
    return [
        dict(arm=ARM, scale=s, factor=f) for s, f in itertools.product(SCALES, FACTORS)
    ]


def candidate_rows():
    return candidates(configurations(), BATCHES, CHECKPOINTS)


def queries():
    return [
        dict(arm=ARM, scale=s, objective=o, cap=m, search=search, rule="joint")
        for s, o, m, search in itertools.product(
            SCALES, (0, 1), ORIGINAL_STOPS[1:], ("expanded", "expanded_stops")
        )
    ]


def select(validation, rows, query, rare_count):
    effective = 0 if query["objective"] == 1 and rare_count == 0 else query["objective"]
    stops = CHECKPOINTS if query["search"] == "expanded_stops" else ORIGINAL_STOPS
    eligible = [
        i
        for i, r in enumerate(rows)
        if r["scale"] == query["scale"]
        and r["observations"] <= query["cap"]
        and r["observations"] in stops
    ]

    def key(i):
        r = rows[i]
        score = validation[tuple(r["index"])][effective]
        return (
            float(score) if np.isfinite(score) else np.inf,
            r["observations"],
            r["batch"],
            r["factor"],
            i,
        )

    chosen = min(eligible, key=key)
    assert np.isfinite(key(chosen)[0]), (
        "Initialization must have finite validation loss."
    )
    return [chosen, int(effective != query["objective"]), 0], eligible


def preserved_hashes():
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASELINE], cwd=ROOT, text=True
    ).splitlines()
    paths = [
        p
        for p in paths
        if p.startswith(("experiments/", "results/", "data/mushroom/"))
        or p in ("Makefile", "uv.lock")
        or p.startswith(
            (
                "notes/practical-selection",
                "notes/mushroom-rate-search",
                "notes/rare-subgroup",
            )
        )
    ]
    subprocess.run(
        ["git", "diff", "--exit-code", BASELINE, "--", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return {p: sha256(ROOT / p) for p in paths}


def declaration():
    data = json.loads((OUTPUT / "declaration.json").read_text())
    assert data["baseline"] == BASELINE
    assert all(sha256(ROOT / p) == h for p, h in data["frozen"].items())
    assert data["preserved"] == preserved_hashes()
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declare", action="store_true", required=True)
    parser.parse_args()
    target = OUTPUT / "declaration.json"
    if target.exists():
        declaration()
        print("Existing sensitivity declaration verified.")
        return
    assert not list(OUTPUT.glob("*.npz"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(
        target,
        dict(
            declared_utc=datetime.now(timezone.utc).isoformat(),
            baseline=BASELINE,
            frozen={p: sha256(ROOT / p) for p in (PROTOCOL, SOURCES[1])},
            preserved=preserved_hashes(),
        ),
    )
    print(f"Declared {target}")


if __name__ == "__main__":
    main()
