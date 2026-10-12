"""Search nested rate and stop grids using exact finite-prevalence moments.

These attainable risks are upper bounds on the continuous oracle, not certified
optima. All comparisons use deterministic choices before observing training.
"""

import argparse
import platform

import numpy as np
import scipy

from experiments.common.data import write_json
from experiments.oracle_finite.config import (
    OUTPUT,
    PREVALENCES,
    RESOLUTION,
    cases,
    rate_grid,
    stop_grid,
)
from normreg.common_block import coefficients, stability_limit

SEARCHES = ["coarse", "fine-rates", "fine-stops", "fine"]


def search(q, rows, resolution=RESOLUTION):
    """Save the best risk, rate, and stop for all four grid combinations."""
    b = q * (1 - q)
    # Ceiling keeps the cap positive and the theorem's tau=1 endpoint admissible.
    caps = np.array([max(1, int(np.ceil(row["tau"] / b))) for row in rows])
    caps = np.array(
        [
            int(np.floor(row["tau"] / b)) if row["tau"] == 4 else cap
            for row, cap in zip(rows, caps, strict=True)
        ]
    )
    fractions, coarse_rate = rate_grid(resolution)
    rates = np.array(
        [stability_limit(1, q, scaled) * fractions for scaled in (False, True)]
    )
    stops, coarse_stop = stop_grid(caps, resolution)
    operators = np.zeros((2, len(fractions), 3, 3))
    for scaling in range(2):
        cc, cr, rc, rr, nc, nr = coefficients(1, q, rates[scaling], bool(scaling))
        operators[scaling, :, 0, :] = np.array([cc, cr, nc]).T
        operators[scaling, :, 1, :] = np.array([rc, rr, nr]).T
    operators[..., 2, 2] = 1
    initial = np.array([[row["s"] / 4, row["r"], row["noise"]] for row in rows])
    weights = np.array([0.5, (1 - q) ** 2 / 2, 0])
    best = np.broadcast_to((initial @ weights)[:, None, None], (len(rows), 4, 2)).copy()
    selected_rate = np.zeros(best.shape, dtype=int)
    selected_stop = np.zeros(best.shape, dtype=int)
    transition = np.broadcast_to(np.eye(3), operators.shape).copy()
    previous = 0
    for stop, is_coarse in zip(stops[1:], coarse_stop[1:], strict=True):
        transition = (
            np.linalg.matrix_power(operators, int(stop - previous)) @ transition
        )
        risk_coefficients = np.einsum("j,arjk->ark", weights, transition)
        risk = np.einsum("ark,ck->car", risk_coefficients, initial)
        if not np.isfinite(risk).all() or np.any(risk < 0):
            raise FloatingPointError(f"Invalid moments at q={q}, stop={stop}.")
        eligible = stop <= caps
        for grid in range(4):
            if grid < 2 and not is_coarse:
                continue
            indices = (
                np.arange(len(fractions)) if grid % 2 else np.flatnonzero(coarse_rate)
            )
            candidates = risk[..., indices]
            local = candidates.argmin(axis=-1)
            values = np.take_along_axis(candidates, local[..., None], axis=-1)[..., 0]
            improved = (values < best[:, grid]) & eligible[:, None]
            best[:, grid][improved] = values[improved]
            selected_rate[:, grid][improved] = indices[local][improved]
            selected_stop[:, grid][improved] = stop
        previous = stop
    selected_alpha = np.take_along_axis(
        np.broadcast_to(rates, (len(rows), 4, *rates.shape)),
        selected_rate[..., None],
        axis=-1,
    )[..., 0]
    return dict(
        cap=caps,
        risk=best,
        alpha=selected_alpha,
        stop=selected_stop,
        rate_index=selected_rate,
        rates=rates,
        stops=stops,
        coarse_rate=coarse_rate,
        coarse_stop=coarse_stop,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    rows = cases()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    saved = {}
    for qi, q in enumerate(PREVALENCES):
        result = search(q, rows)
        saved.update({f"q{qi}_{key}": value for key, value in result.items()})
        print(
            f"Completed q={q:g}: {len(rows)} cases, {len(result['stops'])} stops.",
            flush=True,
        )
    np.savez_compressed(OUTPUT / "search.npz", **saved)
    settings = dict(
        purpose="Finite-grid exact-moment comparison with limiting oracle predictions.",
        model="Independent binary features, fresh observations, "
        "population preprocessing; "
        "zero coefficients, fixed zero intercept, final iterates.",
        tuning="Separate deterministic rate and stop for each scaling and case.",
        risk="Half the mean squared prediction error conditional on rare presence, "
        "excluding irreducible test noise.",
        prevalences=PREVALENCES,
        cases=rows,
        searches=SEARCHES,
        scalings=["U", "S"],
        axes=["case", "search", "scaling"],
        cap_rounding="Ceiling, except floor at tau=4 to stay within the theorem range.",
        rate_search="Union of linear and logarithmic fractions of the stability limit; "
        "zero included, fractions from 1e-10 through 1-1e-6. "
        "No limiting rates injected.",
        stop_search="Rounded geometric stops, all integers through 64, initialization, "
        "and every cap; coarse grids take every second linear/geometric point.",
        resolution=RESOLUTION,
        continuous_optimality_certified=False,
        seed=None,
        numerical_failures=0,
        environment=dict(
            python=platform.python_version(),
            numpy=np.__version__,
            scipy=scipy.__version__,
        ),
    )
    write_json(OUTPUT / "settings.json", settings)


if __name__ == "__main__":
    main()
