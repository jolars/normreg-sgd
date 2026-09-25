"""Plot finite-grid risk contrasts across intermediate signal allocations."""

import json

import numpy as np
from matplotlib.colors import TwoSlopeNorm
from style import OUTPUT, PAPER_WIDTH, RISK_COLORMAP, ROOT, apply_style, plt, save


def plot(report):
    apply_style()
    model = report["model"]
    fractions = np.array(model["rare_signal_fractions"])
    budgets = np.array(report["observation_caps"]) * model["q"]
    risk = np.array(report["risk"])
    gap = (risk[..., 0] - risk[..., 1]) / np.array(model["noise_variances"])[
        None, :, None
    ]
    limit = float(abs(gap).max())
    figure, axes = plt.subplots(
        1, 3, figsize=(PAPER_WIDTH, 2.5), sharex=True, sharey=True, layout="constrained"
    )
    for index, (axis, variance) in enumerate(
        zip(axes, model["noise_variances"], strict=True)
    ):
        mesh = axis.pcolormesh(
            fractions,
            budgets,
            gap[:, index],
            shading="nearest",
            cmap=RISK_COLORMAP,
            norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit),
            rasterized=True,
        )
        axis.contour(
            fractions, budgets, gap[:, index], levels=[0], colors="0.2", linewidths=1
        )
        axis.set(
            title=rf"$\sigma^2={variance:g}$",
            xlim=(0, 1),
            ylim=(budgets[0], budgets[-1]),
            xticks=[0, 0.5, 1],
            yticks=[1, 2, 3, 4],
        )
    axes[0].set_ylabel(r"Expected rare observations, $Mq$")
    figure.supxlabel(r"Rare share of squared coefficients, $f$", fontsize=9)
    colorbar = figure.colorbar(mesh, ax=axes, fraction=0.035, pad=0.025)
    colorbar.set_label(r"$(R_U^{\mathrm{grid}}-R_S^{\mathrm{grid}})/\sigma^2$")
    colorbar.ax.set_title("SD lower\nrisk", fontsize=7, pad=5)
    colorbar.ax.text(
        0.5,
        -0.08,
        "U lower\nrisk",
        transform=colorbar.ax.transAxes,
        ha="center",
        va="top",
        fontsize=7,
    )
    save(figure, OUTPUT / "signal-allocation", "risk-map")


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/signal-allocation/summary.json").read_text()))
