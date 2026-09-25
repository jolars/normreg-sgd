"""Plot a saved signal-allocation slice as the second introduction panel."""

import json

import numpy as np
from style import (
    METHOD_LABELS,
    METHOD_STYLES,
    OUTPUT,
    ROOT,
    SINGLE_PANEL_WIDTH,
    apply_style,
    plt,
    save,
)


def plot(report):
    apply_style()
    model = report["model"]
    budgets = np.array(report["observation_caps"]) * model["q"]
    cap_index = int(np.argmin(abs(budgets - 2)))
    noise_index = model["noise_variances"].index(1.0)
    fractions = np.array(model["rare_signal_fractions"])
    risk = np.array(report["risk"])[cap_index, noise_index]
    gap = risk[:, 0] - risk[:, 1]
    figure, axis = plt.subplots(figsize=(SINGLE_PANEL_WIDTH, 2.45))
    figure.subplots_adjust(left=0.18, right=0.97, bottom=0.25, top=0.97)
    for scaling, scale in enumerate(("none", "sd")):
        style = METHOD_STYLES[scale]
        axis.plot(
            fractions,
            risk[:, scaling],
            label=METHOD_LABELS[scale],
            color=style["color"],
            linestyle=style["linestyle"],
            linewidth=1.8,
        )
    axis.fill_between(
        fractions,
        risk[:, 0],
        risk[:, 1],
        where=gap < 0,
        interpolate=True,
        color=METHOD_STYLES["none"]["color"],
        alpha=0.1,
    )
    axis.fill_between(
        fractions,
        risk[:, 0],
        risk[:, 1],
        where=gap > 0,
        interpolate=True,
        color=METHOD_STYLES["sd"]["color"],
        alpha=0.1,
    )
    axis.text(
        0.22, 0.21, "Unscaled\nhelps", color=METHOD_STYLES["none"]["color"], fontsize=8
    )
    axis.text(
        0.62,
        0.11,
        "Standardization\nhelps",
        color=METHOD_STYLES["sd"]["color"],
        fontsize=8,
    )
    axis.set(
        xlim=(0, 1),
        ylim=(0, 0.28),
        xticks=[0, 0.5, 1],
        xticklabels=["Common\nonly", "Equal\neffects", "Rare\nonly"],
        yticks=[0, 0.1, 0.2],
        ylabel="Rare-subgroup excess risk",
        xlabel="Signal allocation",
    )
    axis.grid(axis="y", color="0.9", linewidth=0.6)
    axis.set_axisbelow(True)
    # Equal canvases keep the axes aligned when LaTeX pairs the two panels.
    save(figure, OUTPUT / "signal-crossing", "risk-crossing", tight=False)


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/signal-allocation/summary.json").read_text()))
