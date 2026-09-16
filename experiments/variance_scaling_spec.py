"""Declared four-rule practical comparison with a common expanded rate search."""

import argparse
import itertools
import json
import subprocess
from datetime import datetime, timezone
from functools import lru_cache

import numpy as np
from mushroom_rate_spec import FACTORS as MUSHROOM_FACTORS
from practical_dynamics import candidates
from practical_spec import ARMS, MUSHROOM_M, ROOT, SYNTHETIC_M, sha256, write_json
from practical_spec import FACTORS as PRACTICAL_FACTORS

OUTPUT = ROOT / "results/variance-scaling-followup"
PROTOCOL = "notes/variance-scaling-followup.md"
SCALES = ("none", "sd", "damped", "variance")
FACTORS = (0.00001, 0.0001, *MUSHROOM_FACTORS, 12.8, 25.6, 51.2, 102.4, 204.8, 409.6)
BATCHES = ((1, 16), (16, 128))
CHECKPOINTS = (
    (0, 128, 256, 512, 1024, 2048),
    (0, 128, 256, 512, 1024, 2048, 4096, 8192),
)
ORIGINAL_STOPS = (SYNTHETIC_M, MUSHROOM_M)
SOURCES = (
    PROTOCOL,
    "experiments/variance_scaling_spec.py",
    "experiments/run_variance_scaling.py",
    "experiments/summarize_variance_scaling.py",
    "experiments/check_variance_scaling.py",
    "experiments/practical_spec.py",
    "experiments/practical_dynamics.py",
    "experiments/mushroom_rate_spec.py",
    "experiments/run_mushroom_rate_search.py",
    "experiments/check_mushroom_rate_search.py",
    "experiments/summarize_practical_selection.py",
    "uv.lock",
    "data/mushroom/agaricus-lepiota.data",
    "data/mushroom/agaricus-lepiota.names",
    "data/mushroom/README.md",
)


def configurations(stage):
    return [
        dict(arm=arm, scale=scale, factor=factor)
        for arm, scale, factor in itertools.product(
            ARMS if stage == 0 else ARMS[2:], SCALES, FACTORS
        )
    ]


def candidate_rows(stage):
    return candidates(configurations(stage), BATCHES[stage], CHECKPOINTS[stage])


def queries(stage):
    searches = ("practical", "expanded", "expanded_stops")
    if stage:
        searches = ("practical", "previous", "expanded", "expanded_stops")
    return [
        dict(arm=arm, scale=scale, objective=objective, cap=cap, search=search)
        for arm, scale, objective, cap, search in itertools.product(
            ARMS if stage == 0 else ARMS[2:],
            SCALES,
            (0, 1),
            ORIGINAL_STOPS[stage][1:],
            searches,
        )
    ]


def search_grid(stage, search):
    factors = {"practical": PRACTICAL_FACTORS, "previous": MUSHROOM_FACTORS}.get(
        search, FACTORS
    )
    stops = CHECKPOINTS[stage] if search == "expanded_stops" else ORIGINAL_STOPS[stage]
    return factors, stops


@lru_cache(maxsize=None)
def eligible_ids(stage, arm, scale, objective, cap, search):
    factors, stops = search_grid(stage, search)
    return np.array(
        [
            i
            for i, row in enumerate(candidate_rows(stage))
            if row["arm"] == arm
            and row["scale"] == scale
            and row["factor"] in factors
            and row["observations"] in stops
            and row["observations"] <= cap
        ]
    )


def select(validation, rows, query, rare_count, stage):
    effective = 0 if query["objective"] == 1 and rare_count == 0 else query["objective"]
    eligible = eligible_ids(stage, **query)
    flat = validation.reshape(-1, 2)

    def order(i):
        row = rows[i]
        value = flat[i, effective]
        return (
            float(value) if np.isfinite(value) else np.inf,
            row["observations"],
            row["batch"],
            row["factor"],
            i,
        )

    chosen = min(eligible, key=order)
    assert np.isfinite(order(chosen)[0]), "Initialization must remain eligible."
    return [int(chosen), int(effective != query["objective"]), 0]


def declaration():
    record = json.loads((OUTPUT / "declaration.json").read_text())
    for section in ("frozen", "preserved"):
        for name, digest in record[section].items():
            assert sha256(ROOT / name) == digest, name
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declare", action="store_true", required=True)
    parser.parse_args()
    target = OUTPUT / "declaration.json"
    if target.exists():
        declaration()
        print("Existing variance-scaling declaration verified.")
        return
    assert not list(OUTPUT.glob("*.npz"))
    tracked = subprocess.check_output(
        ["git", "ls-files"], cwd=ROOT, text=True
    ).splitlines()
    preserved = {
        p: sha256(ROOT / p)
        for p in tracked
        if (
            p.startswith(("experiments/", "results/", "data/"))
            or p in ("Makefile", "uv.lock")
            or p.startswith(
                (
                    "notes/practical-selection",
                    "notes/mushroom-",
                    "notes/normalization-robustness",
                )
            )
        )
        and "variance-scaling-followup" not in p
        and "variance_scaling" not in p
    }
    for name in ("paths.npz", "summary.json"):
        p = "results/normalization-robustness/" + name
        preserved[p] = sha256(ROOT / p)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(
        target,
        dict(
            declared_utc=datetime.now(timezone.utc).isoformat(),
            frozen={p: sha256(ROOT / p) for p in (PROTOCOL, SOURCES[1])},
            preserved=preserved,
        ),
    )
    print(f"Declared {target}")


if __name__ == "__main__":
    main()
