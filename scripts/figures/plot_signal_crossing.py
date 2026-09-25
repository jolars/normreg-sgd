"""Plot limiting allocation risks with saved finite-prevalence selections."""

import json

import numpy as np

from experiments.common.limiting_oracle import oracle_minimum
from scripts.figures.style import (
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
    fractions = np.linspace(0, 1, 401)
    risk = np.array(
        [
            [
                oracle_minimum(scaled, tau=2, s=4 * (1 - theta), r=theta)[0]
                for scaled in (False, True)
            ]
            for theta in fractions
        ]
    )
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
        for prevalence, marker in ((0.02, "o"), (0.000002, "x")):
            rows = sorted(
                (
                    row
                    for row in report["rows"]
                    if row["group"] == "allocation" and row["q"] == prevalence
                ),
                key=lambda row: row["r"],
            )
            axis.plot(
                [row["r"] / (row["s"] / 4 + row["r"]) for row in rows],
                [row["finite_risk"][scaling] for row in rows],
                color=style["color"],
                linestyle="none",
                marker=marker,
                markerfacecolor="white",
                markersize=3.5,
                markeredgewidth=0.8,
                clip_on=False,
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
        0.18, 0.17, "Unscaled\nhelps", color=METHOD_STYLES["none"]["color"], fontsize=8
    )
    axis.text(
        0.86,
        0.16,
        "SD\nhelps",
        color=METHOD_STYLES["sd"]["color"],
        fontsize=8,
        ha="center",
    )
    axis.set(
        xlim=(0, 1),
        ylim=(0, 0.28),
        xticks=[0, 0.5, 1],
        xticklabels=["0", "0.5", "1"],
        yticks=[0, 0.1, 0.2],
        ylabel="Rare-subgroup excess risk",
        xlabel=r"Rare signal share $\theta=r/(s/4+r)$",
    )
    axis.grid(axis="y", color="0.9", linewidth=0.6)
    axis.set_axisbelow(True)
    # Equal canvases keep the axes aligned when LaTeX pairs the two panels.
    save(figure, OUTPUT / "signal-crossing", "risk-crossing", tight=False)


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/oracle-finite/summary.json").read_text()))
