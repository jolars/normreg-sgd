"""Benchmark frozen calibration against exact expected risks in both fresh arms."""

import argparse
import json
from pathlib import Path

import numpy as np

from experiments.common.data import write_json
from experiments.common.reproduction import assert_reproduced
from experiments.theory_bridge import config as cfg

ARMS = ("fresh", "fresh_intercept")


def expected_risks(q, factors, checkpoints, signals, fit_intercept):
    """Propagate full second moments, retaining intercept--feature cross terms."""
    cells = np.array([[i - 0.5, j - q] for i in (0, 1) for j in (0, 1)])
    probabilities = np.array([(1 - q) / 2, q / 2, (1 - q) / 2, q / 2])
    divisors = (np.ones(2), np.sqrt([0.25, q * (1 - q)]))
    profile = np.empty((len(checkpoints), 2, len(signals), len(factors), 2))
    learning_rates = np.empty((2, len(factors)))
    for scaling, divisor in enumerate(divisors):
        design = cells / divisor
        initial = -np.asarray(signals) * divisor
        if fit_intercept:
            design = np.column_stack((np.ones(4), design))
            initial = np.column_stack((np.zeros(len(signals)), initial))
        outer = np.einsum("ci,cj->cij", design, design)
        gram = np.einsum("c,cij->ij", probabilities, outer)
        targets = np.stack((gram, (outer[1] + outer[3]) / 2))
        eta = factors / np.max(np.sum(design**2, axis=1))
        learning_rates[scaling] = eta
        transitions = np.eye(design.shape[1]) - eta[:, None, None, None] * outer
        operator = np.einsum(
            "c,rcik,rcjl->rijkl", probabilities, transitions, transitions
        )
        noise = eta[:, None, None] ** 2 * gram
        second = np.broadcast_to(
            np.einsum("si,sj->sij", initial, initial)[:, None],
            (len(signals), len(factors), *gram.shape),
        ).copy()
        checkpoint = 0
        for stop in range(int(checkpoints[-1]) + 1):
            if stop == checkpoints[checkpoint]:
                profile[checkpoint, scaling] = (
                    np.einsum("oij,srji->sro", targets, second) / 2
                )
                checkpoint += 1
                if checkpoint == len(checkpoints):
                    break
            # Fresh observations make the next feature and noise independent of
            # the current error, so this recursion needs no simulated paths.
            second = np.einsum("rijkl,srkl->srij", operator, second) + noise
    return profile, learning_rates


def analyze(output):
    settings = json.loads((output / "settings.json").read_text())
    assert settings["completed"]
    assert settings["scalings"] == ["none", "sd"]
    assert settings["policies"][:2] == ["calibrated", "coarse_calibrated"]
    factors = np.asarray(settings["rate_factors"])
    signals = np.asarray(settings["signals"])
    arm_ids = [settings["arms"].index(arm) for arm in ARMS]
    rows, arrays, runs = [], {}, []
    for q_id, run in enumerate(settings["runs"]):
        q = run["q"]
        checkpoints = np.asarray(run["checkpoints"])
        calculated = [
            expected_risks(q, factors, checkpoints, signals, fit_intercept)
            for fit_intercept in (False, True)
        ]
        profile = np.stack([values[0] for values in calculated], axis=1)
        learning_rates = np.stack([values[1] for values in calculated])
        assert np.isfinite(profile).all()
        with np.load(output / f"q{q_id}-calibration.npz") as archive:
            fixed = np.take(archive["fixed"][..., 0, :], arm_ids, axis=1)
        optimal = np.empty_like(fixed)
        for cap_id, cap in enumerate(run["caps"]):
            eligible = checkpoints <= cap
            for arm, signal in np.ndindex(2, len(signals)):
                scalings = {}
                for scaling, name in enumerate(settings["scalings"]):
                    risk = profile[:, arm, scaling, signal, :, 1]
                    # Flattening keeps the study's earlier-stop, smaller-rate
                    # tie rule when more than one candidate attains the minimum.
                    optimum = np.unravel_index(
                        np.where(eligible[:, None], risk, np.inf).argmin(), risk.shape
                    )
                    optimal[cap_id, arm, scaling, signal] = optimum
                    calibrated = fixed[cap_id, arm, scaling, signal]
                    assert eligible[calibrated[0]]

                    def candidate(indices):
                        stop, rate = (int(index) for index in indices)
                        return dict(
                            checkpoint_index=stop,
                            stop=int(checkpoints[stop]),
                            rate_index=rate,
                            rate_factor=float(factors[rate]),
                            learning_rate=float(learning_rates[arm, scaling, rate]),
                            expected_rare_risk=float(risk[stop, rate]),
                        )

                    scalings[name] = dict(
                        calibrated=candidate(calibrated),
                        optimum=candidate(optimum),
                        calibration_excess=float(
                            risk[tuple(calibrated)] - risk[optimum]
                        ),
                    )
                rows.append(
                    dict(
                        q=q,
                        cap=cap,
                        arm=ARMS[arm],
                        signal=settings["signal_names"][signal],
                        scaling=scalings,
                        calibrated_gap=(
                            scalings["sd"]["calibrated"]["expected_rare_risk"]
                            - scalings["none"]["calibrated"]["expected_rare_risk"]
                        ),
                        optimal_gap=(
                            scalings["sd"]["optimum"]["expected_rare_risk"]
                            - scalings["none"]["optimum"]["expected_rare_risk"]
                        ),
                    )
                )
        arrays[f"q{q_id}_expected_risk"] = profile
        arrays[f"q{q_id}_learning_rates"] = learning_rates
        arrays[f"q{q_id}_calibrated"] = fixed
        arrays[f"q{q_id}_optimal"] = optimal
        runs.append({key: run[key] for key in ("q", "caps", "checkpoints")})
    return arrays, dict(
        method="Exact second-moment recurrence, evaluated in float64 arithmetic.",
        scope=(
            "Minimum expected population rare excess half loss over the saved "
            "finite rate-and-stop family. Fresh observations, population "
            "preprocessing, unit noise variance, and zero initialization. "
            "Frozen calibration choices are retained; no paths are retrained."
        ),
        uncertainty=(
            "Deterministic expectations over training randomness, conditional on "
            "the saved calibration choices. No Monte Carlo error. This is not an "
            "optimization over all real rates and integer stops."
        ),
        arms=list(ARMS),
        scalings=settings["scalings"],
        signals=settings["signals"],
        signal_names=settings["signal_names"],
        rate_factors=settings["rate_factors"],
        risk_objectives=["aggregate", "rare"],
        profile_axes=["stop", "arm", "scaling", "signal", "rate", "risk objective"],
        learning_rate_axes=["arm", "scaling", "rate"],
        selection_axes=["cap", "arm", "scaling", "signal", "selection field"],
        selection_fields=["stopping-checkpoint index", "rate-factor index"],
        runs=runs,
        rows=rows,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=cfg.OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    arrays, report = analyze(args.output)
    archive = args.output / "exact-calibration.npz"
    summary = args.output / "exact-calibration.json"
    if args.check:
        assert_reproduced(report, json.loads(summary.read_text()))
        with np.load(archive) as saved:
            assert set(saved.files) == arrays.keys()
            for name, values in arrays.items():
                np.testing.assert_allclose(values, saved[name], rtol=1e-12, atol=1e-14)
        print("Exact expected-risk calibration benchmark reproduces.")
    else:
        np.savez_compressed(archive, **arrays)
        write_json(summary, report)
        print(f"Saved exact calibration benchmarks for {len(report['rows'])} settings.")


if __name__ == "__main__":
    main()
