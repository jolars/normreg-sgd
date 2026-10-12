"""Plot saved limiting risks along the corollary's signal-allocation path."""

import json

import numpy as np

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
    prevalence = min(row["q"] for row in report["rows"])
    rows = sorted(
        [
            row
            for row in report["rows"]
            if row["group"] == "allocation" and row["q"] == prevalence
        ],
        key=lambda row: row["r"],
    )
    assert all(row["tau"] == 2 and row["noise"] == 1 for row in rows)
    np.testing.assert_allclose([row["s"] / 4 + row["r"] for row in rows], 1)
    fractions = np.array([row["r"] for row in rows])
    risk = np.array([row["nominal_limiting_risk"] for row in rows])
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
        0.12, 0.14, "Unscaled\nhelps", color=METHOD_STYLES["none"]["color"], fontsize=9
    )
    axis.annotate(
        "Standardization\nhelps",
        xy=(0.96, float(np.interp(0.96, fractions, risk.mean(axis=1)))),
        xytext=(0.65, 0.08),
        color=METHOD_STYLES["sd"]["color"],
        fontsize=9,
        arrowprops=dict(
            arrowstyle="->",
            color=METHOD_STYLES["sd"]["color"],
            linewidth=0.7,
            connectionstyle="arc3,rad=0.15",
        ),
    )
    axis.set(
        xlim=(0, 1),
        ylim=(0, 0.28),
        xticks=[0, 0.5, 1],
        xticklabels=["Common\nonly", "Equal risk\ncontributions", "Rare\nonly"],
        yticks=[0, 0.1, 0.2],
        ylabel="Limiting rare-subgroup risk",
        xlabel=r"Rare signal share $\theta$",
    )
    # Keep the right endpoint label inside the fixed canvas shared by both panels.
    axis.get_xticklabels()[-1].set_ha("right")
    axis.grid(axis="y", color="0.9", linewidth=0.6)
    axis.set_axisbelow(True)
    # Equal canvases keep the axes aligned when LaTeX pairs the two panels.
    save(figure, OUTPUT / "signal-crossing", "risk-crossing", tight=False)


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/oracle-finite/summary.json").read_text()))
