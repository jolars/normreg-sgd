"""Illustrate the two oracle signal families with exact finite-update moments.

This is a numerical illustration of an existing theorem, not a prospective
evaluation. Each curve minimizes population rare risk on a finite rate grid and
over every integer stop within the cap. It does not certify a continuous oracle.
"""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from check_predictive_theorem import observation_operator
from plot_joint_interactions import save

ROOT = Path(__file__).resolve().parents[1]
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


def check_selected(risks, rates, stops):
    """Replay selections using independently enumerated full tensor updates."""
    maximum_error = 0.0
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
    assert maximum_error < 1e-10, maximum_error
    return maximum_error


def calculate():
    caps = budget_caps()
    coarse, _, _ = envelopes(rate_grid(2048), caps)
    risks, rates, stops = envelopes(rate_grid(4096), caps)
    refinement = coarse - risks
    assert np.all(refinement >= -1e-14)
    assert refinement.max() < 2e-6, refinement.max()
    tensor_error = check_selected(risks, rates, stops)
    gaps = np.stack((risks[:, 0, 0] - risks[:, 0, 1], risks[:, 1, 1] - risks[:, 1, 0]))
    assert (gaps[0] >= 0.007).all() and (gaps[1] >= 0.005).all()
    sources = [
        Path(__file__).relative_to(ROOT),
        Path("experiments/check_predictive_theorem.py"),
        Path("experiments/plot_joint_interactions.py"),
        Path("uv.lock"),
    ]
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
            "max_selected_risk_tensor_replay_error": tensor_error,
            "continuous_optimality_certified": False,
        },
        "array_axes": ["budget cap", "signal family", "scaling"],
        "scalings": list(SCALINGS),
        "observation_caps": caps.tolist(),
        "risk": risks.tolist(),
        "selected_alpha": rates.tolist(),
        "selected_stop": stops.tolist(),
        "source_sha256": {
            str(path): hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sources
        },
    }
    print(
        f"Checked all integer stops, {risks.size} tensor replays, and nested grids; "
        f"maximum risk change {refinement.max():.3g}, replay error {tensor_error:.3g}."
    )
    print(
        f"Minimum plotted gaps: rare signal {gaps[0].min():.6f}, "
        f"common {gaps[1].min():.6f}."
    )
    return report


def plot(report):
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.fonttype": "none",
            "svg.hashsalt": "normreg-predictive-intro-v1",
            "pdf.fonttype": 42,
        }
    )
    budgets = np.array(report["observation_caps"]) * float(Q)
    risk = np.array(report["risk"])
    figure, axes = plt.subplots(1, 2, figsize=(6.75, 2.35), sharex=True, sharey=True)
    figure.subplots_adjust(left=0.095, right=0.98, bottom=0.23, top=0.78, wspace=0.16)
    for signal, (axis, title) in enumerate(
        zip(
            axes,
            ("(a) Rare signal dominates", "(b) Common signal dominates"),
            strict=True,
        )
    ):
        for scaling, (label, color, linestyle) in enumerate(
            zip(SCALINGS, COLORS, ("--", "-"), strict=True)
        ):
            axis.plot(
                budgets,
                risk[:, signal, scaling],
                label=label,
                color=color,
                linestyle=linestyle,
                linewidth=1.8,
            )
        axis.fill_between(
            budgets, risk[:, signal, 0], risk[:, signal, 1], color="0.5", alpha=0.10
        )
        axis.set(
            title=title, xlim=(1, budgets[-1]), ylim=(0, 0.36), xticks=[1, 2, 3, 4]
        )
        axis.set_yticks([0, 0.1, 0.2, 0.3])
        axis.grid(axis="y", color="0.9", linewidth=0.6)
        axis.set_axisbelow(True)
    axes[0].set_ylabel("Rare-subgroup excess risk")
    axes[0].text(2.25, 0.12, "Standardization helps", color=COLORS[1], ha="center")
    axes[1].text(2.5, 0.18, "Unscaled training helps", color=COLORS[0], ha="center")
    figure.supxlabel(r"Expected rare observations at the budget cap, $Mq$", y=0.025)
    figure.legend(
        *axes[0].get_legend_handles_labels(), loc="upper center", ncol=2, frameon=False
    )
    preview = ROOT / "build/predictive-intro.png"
    preview.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(preview, dpi=180)
    save(figure, OUTPUT, NAME)


def main():
    assert __debug__, "Run ordinary Python without -O."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Verify without rewriting artifacts."
    )
    arguments = parser.parse_args()
    report = calculate()
    if arguments.check:
        saved = json.loads((OUTPUT / "summary.json").read_text())
        figures = saved.pop("figure_sha256")
        assert saved == report, (
            "Regenerate the introduction figure after changing its inputs."
        )
        for name, digest in figures.items():
            assert hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest() == digest
        print("Introduction figure data, provenance, and artifact hashes match.")
    else:
        plot(report)
        report["figure_sha256"] = {
            f"{NAME}.{extension}": hashlib.sha256(
                (OUTPUT / f"{NAME}.{extension}").read_bytes()
            ).hexdigest()
            for extension in ("pdf", "svg")
        }
        (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        print(f"Wrote {OUTPUT.relative_to(ROOT)} and build/predictive-intro.png.")


if __name__ == "__main__":
    main()
