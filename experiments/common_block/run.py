"""Search every integer stop on nested grids of mean-square-stable rates.

The calculation is deterministic and uses exact moment recurrences evaluated in
floating point. The finite candidate family does not certify an oracle optimum.
"""

import json
import platform
import time

import numpy as np

from experiments.common_block.config import (
    COMMON_COUNTS,
    NOISE_VARIANCE,
    OUTPUT,
    PREVALENCES,
    RATE_FRACTIONS,
    SCALINGS,
    SIGNAL_NAMES,
    SIGNALS,
    TARGET_BUDGETS,
)
from experiments.common_block.engine import coefficients, stability_limit


def search(
    q, counts=COMMON_COUNTS, fractions=RATE_FRACTIONS, signals=SIGNALS, caps=None
):
    b = q * (1 - q)
    if caps is None:
        caps = np.rint(TARGET_BUDGETS / b).astype(int)
        # Keep the endpoint budgets inside the existing theorem's interval.
        caps[0] = int(np.ceil(TARGET_BUDGETS[0] / b))
        caps[-1] = int(np.floor(TARGET_BUDGETS[-1] / b))
    limits = np.array(
        [[stability_limit(m, q, bool(s)) for s in range(2)] for m in counts]
    )
    rates = limits[..., None] * fractions
    terms = np.array(
        [
            [coefficients(m, q, rates[j, s], bool(s)) for s in range(2)]
            for j, m in enumerate(counts)
        ]
    )
    cc, cr, rc, rr, nc, nr = np.moveaxis(terms, 2, 0)[:, :, None]
    shape = (len(counts), len(signals), 2, len(fractions))
    common = np.broadcast_to(signals[None, :, None, None, 0] / 4, shape).copy()
    rare = np.broadcast_to(signals[None, :, None, None, 1], shape).copy()
    best = (common + (1 - q) ** 2 * rare) / 2
    best_stop = np.zeros(shape, dtype=np.int32)
    saved_risk, saved_stop = [], []
    cap_index = 0
    for stop in range(1, int(caps[-1]) + 1):
        common, rare = cc * common + cr * rare + nc, rc * common + rr * rare + nr
        risk = (common + (1 - q) ** 2 * rare) / 2
        improved = risk < best
        best_stop[improved] = stop
        best = np.minimum(best, risk)
        if stop == caps[cap_index]:
            assert np.isfinite(risk).all() and (risk >= 0).all()
            saved_risk.append(best.copy())
            saved_stop.append(best_stop.copy())
            cap_index += 1
    return dict(
        caps=caps,
        limits=limits,
        alpha=rates,
        risk=np.array(saved_risk),
        stop=np.array(saved_stop),
    )


def main():
    started = time.monotonic()
    outputs = []
    for q in PREVALENCES:
        outputs.append(search(q))
        print(
            f"Completed q={q:g}, {len(COMMON_COUNTS)} common-feature counts.",
            flush=True,
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUTPUT / "search.npz",
        **{key: np.stack([out[key] for out in outputs]) for key in outputs[0]},
    )
    settings = dict(
        purpose="Exploratory dimension comparison; finite stable-rate search only.",
        common_counts=COMMON_COUNTS.tolist(),
        prevalences=PREVALENCES.tolist(),
        target_scaled_budgets=TARGET_BUDGETS.tolist(),
        cap_rounding="nearest integer, rounded inward at scaled budgets one and four",
        signals_common_squared_norm_rare_squared=SIGNALS.tolist(),
        signal_names=SIGNAL_NAMES,
        scalings=SCALINGS,
        noise_variance=NOISE_VARIANCE,
        rate_fractions=RATE_FRACTIONS.tolist(),
        coarse_indices=np.r_[0, np.arange(1, len(RATE_FRACTIONS), 2)].tolist(),
        candidate_axes=[
            "prevalence",
            "cap",
            "common count",
            "signal",
            "scaling",
            "rate",
        ],
        sampling="one fresh observation per update; no simulated training",
        preprocessing="known population centering and scales",
        initialization="zero coefficients; fixed zero intercept",
        stopping="every integer from zero through the observation cap",
        tuning="minimize risk averaged over training randomness",
        seed=None,
        numerical_failures=0,
        python=platform.python_version(),
        numpy=np.__version__,
        elapsed_seconds=time.monotonic() - started,
    )
    (OUTPUT / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")


if __name__ == "__main__":
    main()
