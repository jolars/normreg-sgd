"""Declared four-rule practical comparison with a common expanded rate search."""

import itertools
from functools import lru_cache

import numpy as np

from experiments.common.data import ARMS, MUSHROOM_M, SYNTHETIC_M
from experiments.common.data import FACTORS as PRACTICAL_FACTORS
from experiments.common.dynamics import candidates
from experiments.mushroom.rates17 import FACTORS as MUSHROOM_FACTORS

SCALES = ("none", "sd", "damped", "variance")
FACTORS = (0.00001, 0.0001, *MUSHROOM_FACTORS, 12.8, 25.6, 51.2, 102.4, 204.8, 409.6)
BATCHES = ((1, 16), (16, 128))
CHECKPOINTS = (
    (0, 128, 256, 512, 1024, 2048),
    (0, 128, 256, 512, 1024, 2048, 4096, 8192),
)
ORIGINAL_STOPS = (SYNTHETIC_M, MUSHROOM_M)


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
