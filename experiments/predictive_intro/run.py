"""Illustrate the two oracle signal families with exact finite-update moments.

This is a numerical illustration of an existing theorem, not a prospective
evaluation. Each curve minimizes population rare risk on a finite rate grid and
over every integer stop within the cap. It does not certify a continuous oracle.
"""

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

from checks.predictive_theorem import observation_operator
from experiments.common.data import write_json
from experiments.common.reproduction import assert_reproduced
from normreg.moments import make_model, moment_path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/predictive-intro"
Q = Fraction(1, 10000)
SIGNALS = np.array([[0.1, 1.0], [1.0, 0.1]])
SCALINGS = ("Unscaled", "Standardized")
COLORS = ("#0072B2", "#D55E00")
NAME = "tuned-rare-risk"


def rate_grid(intervals):
    return np.r_[0.0, np.geomspace(1e-6, 2.0, intervals + 1)]


def budget_caps():
    b = Q * (1 - Q)
    return np.rint(np.linspace(int(1 / b) + 1, int(4 / b), 61)).astype(int)


def envelopes(rates, caps):
    """Search all stops while retaining the selected rate and actual stop."""
    q = float(Q)
    b = q * (1 - q)
    drift = np.array([rates / 4, b * rates])
    cc = (1 - drift) ** 2
    cr = 4 * drift**2 * b
    rc = b * rates**2 / 4
    rr = 1 - b * rates * (2 - rates + 3 * b * rates)
    nc, nr = 4 * drift**2, b * rates**2
    shape = (len(SIGNALS), len(SCALINGS), len(rates))
    common = np.broadcast_to(SIGNALS[:, 0, None, None] ** 2, shape).copy()
    rare = np.broadcast_to(SIGNALS[:, 1, None, None] ** 2, shape).copy()
    initial = SIGNALS[:, 0] ** 2 / 8 + (1 - q) ** 2 * SIGNALS[:, 1] ** 2 / 2
    best = np.broadcast_to(initial[:, None], shape[:2]).copy()
    selected_rate = np.zeros(shape[:2], dtype=int)
    selected_stop = np.zeros(shape[:2], dtype=int)
    snapshots = []
    cap_index = 0
    for stop in range(1, int(caps[-1]) + 1):
        common, rare = cc * common + cr * rare + nc, rc * common + rr * rare + nr
        risk = common / 8 + (1 - q) ** 2 * rare / 2
        indices = risk.argmin(axis=-1)
        candidate = np.take_along_axis(risk, indices[..., None], axis=-1)[..., 0]
        improved = candidate < best
        best = np.minimum(best, candidate)
        selected_rate[improved] = indices[improved]
        selected_stop[improved] = stop
        if stop == caps[cap_index]:
            snapshots.append((best.copy(), selected_rate.copy(), selected_stop.copy()))
            cap_index += 1
    risks, indices, stops = map(np.array, zip(*snapshots, strict=True))
    assert np.isfinite(common).all() and np.isfinite(rare).all()
    assert (common >= 0).all() and (rare >= 0).all()
    assert (np.diff(risks, axis=0) <= 0).all()
    assert (stops <= caps[:, None, None]).all()
    assert (indices > 1).all() and (indices < len(rates) - 1).all()
    return risks, rates[indices], stops


def selected_components(rates, stops):
    """Weight each coordinate's error components by its rare-risk contribution."""
    q = float(Q)
    b = q * (1 - q)
    model = make_model(q, "independent")
    weights = np.diag(model["rare_second"]) / 2
    components = np.empty((*rates.shape, 2, 3))
    for cap, signal, scaling in np.ndindex(rates.shape):
        alpha = rates[cap, signal, scaling]
        scales = np.sqrt(np.diag(model["gram"])) if scaling else np.ones(2)
        step = b * alpha if scaling else alpha
        moments = moment_path(
            model, scales, step, 1, [stops[cap, signal, scaling]], SIGNALS[signal]
        )
        assert moments["valid"].all()
        parts = np.stack(
            [
                moments["bias"][0] ** 2,
                np.diag(moments["design_covariance"][0]),
                np.diag(moments["noise_covariance"][0]),
            ],
            axis=-1,
        )
        components[cap, signal, scaling] = weights[:, None] * parts
    assert np.isfinite(components).all() and (components >= 0).all()
    return components


def check_selected(risks, rates, stops, components):
    """Replay selections using independently enumerated full tensor updates."""
    maximum_error = 0.0
    maximum_component_error = 0.0
    q = float(Q)
    b = q * (1 - q)
    weights = np.array([1 / 8, (1 - q) ** 2 / 2])
    for cap, signal, scaling in np.ndindex(risks.shape):
        operator = np.asarray(
            observation_operator(
                Q, Fraction(rates[cap, signal, scaling]), scaling == 1
            ),
            dtype=float,
        )
        beta = SIGNALS[signal]
        initial = np.r_[np.outer(beta, beta).ravel(), 1.0]
        endpoint = np.linalg.matrix_power(operator, int(stops[cap, signal, scaling]))
        moment = endpoint @ initial
        risk = moment[0] / 8 + (1 - float(Q)) ** 2 * moment[3] / 2
        error = abs(risk - risks[cap, signal, scaling])
        maximum_error = max(maximum_error, error)
        alpha = rates[cap, signal, scaling]
        drift = np.array([b * alpha if scaling else alpha / 4, b * alpha])
        squared_bias = beta**2 * (1 - drift) ** (2 * stops[cap, signal, scaling])
        noiseless = (endpoint[:4, :4] @ initial[:4])[[0, 3]]
        parts = weights[:, None] * np.stack(
            [squared_bias, noiseless - squared_bias, endpoint[[0, 3], 4]], axis=-1
        )
        maximum_component_error = max(
            maximum_component_error,
            float(np.max(abs(parts - components[cap, signal, scaling]))),
        )
    assert maximum_error < 1e-10, maximum_error
    assert maximum_component_error < 1e-10, maximum_component_error
    np.testing.assert_allclose(components.sum(axis=(-2, -1)), risks, atol=1e-10, rtol=0)
    return maximum_error, maximum_component_error


def calculate():
    caps = budget_caps()
    coarse, _, _ = envelopes(rate_grid(2048), caps)
    risks, rates, stops = envelopes(rate_grid(4096), caps)
    refinement = coarse - risks
    assert np.all(refinement >= -1e-14)
    assert refinement.max() < 2e-6, refinement.max()
    components = selected_components(rates, stops)
    tensor_error, component_error = check_selected(risks, rates, stops, components)
    gaps = np.stack((risks[:, 0, 0] - risks[:, 0, 1], risks[:, 1, 1] - risks[:, 1, 0]))
    assert (gaps[0] >= 0.007).all() and (gaps[1] >= 0.005).all()
    report = {
        "purpose": "Numerical illustration of the theorem; not a held-out evaluation.",
        "model": {
            "q": float(Q),
            "common_prevalence": 0.5,
            "independent_features": True,
            "signal_common_rare": SIGNALS.tolist(),
            "noise_variance": 1.0,
            "batch_size": 1,
            "sampling": "fresh observations",
            "preprocessing": "known population centering and scales",
            "initialization": "zero coefficients and fixed zero intercept",
            "risk": "conditional excess half squared loss given rare presence",
        },
        "search": {
            "parameterization": "eta_U = alpha; eta_S = q(1-q) alpha",
            "alpha_grid": "zero and 4097 geometric points from 1e-6 to 2",
            "coarse_alpha_grid": "zero and every second positive fine-grid point",
            "stops": "every integer from zero through the observation cap",
            "selection": "population rare risk, averaged over training randomness",
            "max_risk_change_on_rate_refinement": float(refinement.max()),
            "max_selected_risk_tensor_replay_error": float(tensor_error),
            "max_selected_component_tensor_replay_error": component_error,
            "continuous_optimality_certified": False,
        },
        "array_axes": ["budget cap", "signal family", "scaling"],
        "scalings": list(SCALINGS),
        "observation_caps": caps.tolist(),
        "risk": risks.tolist(),
        "selected_alpha": rates.tolist(),
        "selected_stop": stops.tolist(),
        "decomposition": {
            "array_axes": [
                "budget cap",
                "signal family",
                "scaling",
                "coordinate",
                "component",
            ],
            "coordinates": ["common", "rare"],
            "components": [
                "squared_mean_error",
                "feature_sampling_variation",
                "observation_noise",
            ],
            "risk_weights": [1 / 8, (1 - float(Q)) ** 2 / 2],
            "weighted_risk_components": components.tolist(),
        },
    }
    print(
        f"Checked all integer stops, {risks.size} tensor replays, and nested grids; "
        f"maximum risk change {refinement.max():.3g}, replay error {tensor_error:.3g}, "
        f"component error {component_error:.3g}."
    )
    print(
        f"Minimum plotted gaps: rare signal {gaps[0].min():.6f}, "
        f"common {gaps[1].min():.6f}."
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = calculate()
    if args.check:
        assert_reproduced(report, json.loads((OUTPUT / "summary.json").read_text()))
        print("Introduction illustration numerical checks passed.")
    else:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT / "summary.json", report)


if __name__ == "__main__":
    main()
