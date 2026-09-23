"""Mushroom searches over five and 17 learning-rate factors."""

import itertools

from experiments.common.data import ROOT, SCALES
from experiments.common.dynamics import candidates, choose

OUTPUT = ROOT / "results/mushroom/rates17"
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
