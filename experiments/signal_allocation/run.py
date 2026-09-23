"""Explore intermediate signals with exact moments on nested finite search grids.

This post hoc illustration keeps the theorem's data model and varies signal
allocation, noise, and the observation cap. It supplies no continuous optimum
or additional uniform risk guarantee.
"""

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
from checks.predictive_theorem import observation_operator  # noqa: E402

OUTPUT = ROOT / "results/signal-allocation"
Q = Fraction(1, 10000)


def calculate():
    q = float(Q)
    b = q * (1 - q)
    fractions = np.unique(np.r_[np.linspace(0, 1, 41), 1 / 101, 100 / 101])
    variances = np.array([0.25, 1.0, 4.0])
    caps = np.rint(np.linspace(int(1 / b) + 1, int(4 / b), 21)).astype(int)
    rates = np.r_[0.0, np.geomspace(1e-6, 2, 1025)]
    coarse_rates = np.r_[0, np.arange(1, len(rates), 2)]
    checkpoints = np.rint(np.geomspace(1, caps[-1], 1025)).astype(int)
    coarse_stops = set(np.r_[0, checkpoints[::2], caps])
    stops = np.unique(np.r_[0, checkpoints, caps])
    signals = np.array(
        [[1.01 * (1 - f), 1.01 * f, v] for v in variances for f in fractions]
    )

    drift = np.array([rates / 4, b * rates])
    operator = np.zeros((2, len(rates), 3, 3))
    operator[..., 0, 0] = (1 - drift) ** 2
    operator[..., 0, 1] = 4 * drift**2 * b
    operator[..., 0, 2] = 4 * drift**2
    operator[..., 1, 0] = b * rates**2 / 4
    operator[..., 1, 1] = 1 - b * rates * (2 - rates + 3 * b * rates)
    operator[..., 1, 2] = b * rates**2
    operator[..., 2, 2] = 1
    transition = np.broadcast_to(np.eye(3), operator.shape).copy()
    weights = np.array([1 / 8, (1 - q) ** 2 / 2, 0])
    initial = signals @ weights
    best = np.broadcast_to(initial[:, None], (len(signals), 2)).copy()
    coarse_best = best.copy()
    selected_rate = np.zeros(best.shape, dtype=int)
    selected_stop = np.zeros(best.shape, dtype=int)
    snapshots = []
    previous = 0
    cap_index = 0
    for stop in stops[1:]:
        transition = np.linalg.matrix_power(operator, int(stop - previous)) @ transition
        coefficients = np.einsum("j,arjk->ark", weights, transition)
        risk = np.einsum("ark,sk->sar", coefficients, signals)
        assert np.isfinite(risk).all() and (risk >= 0).all()
        indices = risk.argmin(axis=-1)
        candidate = np.take_along_axis(risk, indices[..., None], axis=-1)[..., 0]
        improved = candidate < best
        best = np.minimum(best, candidate)
        selected_rate[improved] = indices[improved]
        selected_stop[improved] = stop
        if stop in coarse_stops:
            coarse_best = np.minimum(coarse_best, risk[..., coarse_rates].min(axis=-1))
        if stop == caps[cap_index]:
            snapshots.append(
                (
                    best.copy(),
                    coarse_best.copy(),
                    selected_rate.copy(),
                    selected_stop.copy(),
                )
            )
            cap_index += 1
        previous = stop

    risk, coarse, indices, selected_stops = map(np.array, zip(*snapshots, strict=True))
    assert (np.diff(risk, axis=0) <= 0).all()
    assert (selected_stops <= caps[:, None, None]).all()
    refinement = coarse - risk
    assert refinement.min() >= -1e-12
    assert refinement.max() < 3e-5, refinement.max()
    active = selected_stops > 0
    assert ((indices[active] > 1) & (indices[active] < len(rates) - 1)).all()

    # Tensor enumeration checks the reduced recurrence independently, including
    # pure signals, both theorem anchors, and selections across the whole grid.
    anchor_ids = [
        len(fractions) + int(np.argmin(abs(fractions - value)))
        for value in (0, 1 / 101, 100 / 101, 1)
    ]
    endpoints = {
        (cap, signal, scaling)
        for cap in (0, len(caps) - 1)
        for signal in anchor_ids
        for scaling in range(2)
    }
    generator = np.random.default_rng(20260923)
    for flat in generator.choice(risk.size, 96, replace=False):
        endpoints.add(tuple(int(i) for i in np.unravel_index(flat, risk.shape)))
    error = 0.0
    for cap, signal, scaling in sorted(endpoints):
        alpha = Fraction(float(rates[indices[cap, signal, scaling]]))
        tensor = np.asarray(observation_operator(Q, alpha, scaling == 1), dtype=float)
        s, r, variance = signals[signal]
        initial_tensor = np.array([s, np.sqrt(s * r), np.sqrt(s * r), r, variance])
        moment = (
            np.linalg.matrix_power(tensor, int(selected_stops[cap, signal, scaling]))
            @ initial_tensor
        )
        replay = moment[0] / 8 + (1 - q) ** 2 * moment[3] / 2
        error = max(error, abs(replay - risk[cap, signal, scaling]))
    assert error < 1e-9, error

    shape = (len(caps), len(variances), len(fractions), 2)
    report = dict(
        purpose="Post hoc finite-grid illustration; no continuous optimality claim.",
        model=dict(
            q=q,
            common_prevalence=0.5,
            independent=True,
            squared_coefficient_sum=1.01,
            noise_variances=variances.tolist(),
            rare_signal_fractions=fractions.tolist(),
            sampling="one fresh observation per update",
            preprocessing="known population centering and scales",
            initialization="zero coefficients and fixed zero intercept",
        ),
        search=dict(
            alpha=rates.tolist(),
            stops=stops.tolist(),
            coarse_alpha=rates[coarse_rates].tolist(),
            coarse_stops=sorted(int(k) for k in coarse_stops),
            max_risk_change_on_joint_refinement=float(refinement.max()),
            tensor_replays=len(endpoints),
            max_tensor_error=error,
            positive_stop_boundary_selections=0,
            continuous_optimality_certified=False,
        ),
        observation_caps=caps.tolist(),
        axes=["cap", "noise variance", "rare signal fraction", "scaling"],
        scalings=["Unscaled", "Standardized"],
        risk=risk.reshape(shape).tolist(),
        coarse_risk=coarse.reshape(shape).tolist(),
        selected_alpha=rates[indices].reshape(shape).tolist(),
        selected_stop=selected_stops.reshape(shape).tolist(),
    )
    print(
        f"Joint refinement: {refinement.max():.6g}; "
        f"{len(endpoints)} tensor replays, maximum error {error:.3g}."
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(calculate(), indent=2, allow_nan=False) + "\n"
    if args.check:
        assert (OUTPUT / "summary.json").read_text() == content
        print("Signal-allocation illustration numerical checks passed.")
    else:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "summary.json").write_text(content)
        print(f"Wrote {OUTPUT.relative_to(ROOT) / 'summary.json'}.")


if __name__ == "__main__":
    main()
