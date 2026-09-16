"""Declared, nested rate searches without modifying the frozen practical study."""

import argparse
import itertools
import json
import subprocess
from datetime import datetime, timezone

from practical_dynamics import candidates, choose
from practical_spec import ROOT, SCALES, sha256, write_json

OUTPUT = ROOT / "results/mushroom-rate-search"
PROTOCOL = "notes/mushroom-rate-search.md"
BASELINE = "7c6d331ba661c7161030411cdb86bca8105666a8"
ARMS = ("centered_fixed", "centered_fitted", "uncentered_fitted")
ORIGINAL_FACTORS = (0.001, 0.01, 0.05, 0.2, 0.8)
FACTORS = (
    0.001,
    0.01,
    0.05,
    0.2,
    0.4,
    0.6,
    0.8,
    1.0,
    1.2,
    1.4,
    1.6,
    1.8,
    2.0,
    2.4,
    3.2,
    4.8,
    6.4,
)
BATCHES = (16, 128)
CHECKPOINTS = (0, 128, 256, 512, 1024, 2048, 4096, 8192)
ORIGINAL_STOPS = (0, 512, 2048, 8192)
SIZES = ((256, 128), (2048, 1024))
REPS = 32
SOURCES = (
    PROTOCOL,
    "experiments/mushroom_rate_spec.py",
    "experiments/run_mushroom_rate_search.py",
    "experiments/summarize_mushroom_rate_search.py",
    "experiments/check_mushroom_rate_search.py",
    "experiments/practical_spec.py",
    "experiments/practical_dynamics.py",
    "experiments/summarize_practical_selection.py",
    "uv.lock",
    "data/mushroom/agaricus-lepiota.data",
    "data/mushroom/agaricus-lepiota.names",
    "data/mushroom/README.md",
)


def configurations():
    return [
        dict(arm=arm, scale=scale, factor=factor)
        for arm, scale, factor in itertools.product(ARMS, SCALES, FACTORS)
    ]


def candidate_rows():
    return candidates(configurations(), BATCHES, CHECKPOINTS)


def queries():
    return [
        dict(
            arm=arm, scale=scale, objective=objective, cap=cap, search=search, rule=rule
        )
        for arm, scale, objective, cap in itertools.product(
            ARMS, SCALES, range(2), ORIGINAL_STOPS[1:]
        )
        for search, rule in (
            ("fixed", "fixed"),
            ("original", "rate_batch"),
            ("original", "joint"),
            ("expanded", "rate_batch"),
            ("expanded", "joint"),
            ("expanded_stops", "joint"),
        )
    ]


def pool(rows, search):
    factors = ORIGINAL_FACTORS if search in ("fixed", "original") else FACTORS
    stops = CHECKPOINTS if search == "expanded_stops" else ORIGINAL_STOPS
    return [
        i
        for i, row in enumerate(rows)
        if row["factor"] in factors and row["observations"] in stops
    ]


def select(validation, rows, query, rare_count):
    ids = pool(rows, query["search"])
    selected, fallback, failed, eligible = choose(
        validation,
        [rows[i] for i in ids],
        **{k: v for k, v in query.items() if k != "search"},
        validation_rare_count=rare_count,
    )
    return [ids[selected], int(fallback), int(failed)], [ids[i] for i in eligible]


def preserved_hashes():
    tracked = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASELINE], cwd=ROOT, text=True
    ).splitlines()
    paths = [
        p
        for p in tracked
        if p.startswith(("experiments/", "results/", "data/mushroom/"))
        or p
        in (
            "notes/practical-selection.md",
            "notes/practical-selection-results.md",
            "Makefile",
            "uv.lock",
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
    declared = json.loads((OUTPUT / "declaration.json").read_text())
    assert declared["baseline"] == BASELINE
    for name, digest in declared["frozen"].items():
        assert sha256(ROOT / name) == digest, f"Changed declaration: {name}"
    assert declared["preserved"] == preserved_hashes()
    return declared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declare", action="store_true", required=True)
    parser.parse_args()
    target = OUTPUT / "declaration.json"
    if target.exists():
        declaration()
        print("Existing declaration verified; not rewritten.")
        return
    assert not list(OUTPUT.glob("*.npz")), "Cannot declare after producing results."
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(
        target,
        dict(
            declared_utc=datetime.now(timezone.utc).isoformat(),
            baseline=BASELINE,
            frozen={
                name: sha256(ROOT / name)
                for name in (PROTOCOL, "experiments/mushroom_rate_spec.py")
            },
            preserved=preserved_hashes(),
        ),
    )
    print(f"Declared {target}")


if __name__ == "__main__":
    main()
