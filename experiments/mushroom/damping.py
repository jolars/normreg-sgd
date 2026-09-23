"""Declared fixed-offset comparisons on the primary Mushroom preprocessing arm."""

import itertools

import numpy as np

from experiments.common.data import ROOT
from experiments.common.dynamics import candidates
from experiments.mushroom.rates17 import (
    BATCHES,
    CHECKPOINTS,
    FACTORS,
    ORIGINAL_STOPS,
)
from experiments.mushroom.rates17 import REPS as REPS
from experiments.mushroom.rates17 import SIZES as SIZES

OUTPUT = ROOT / "results/mushroom/damping"
TAUS = (0.001, 0.003, 0.01, 0.03, 0.1)
SCALES = ("none", "sd", "variance", *(f"damped_{t:g}" for t in TAUS))
ARM = "centered_fitted"


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
