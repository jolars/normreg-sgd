"""Plot saved rare-risk components at separately selected rates and stops."""

import json

import numpy as np
from style import (
    BAR_EDGE_COLOR,
    COMPONENT_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    ROOT,
    apply_style,
    plt,
    save,
)

CAP = 20503
COMPONENTS = (
    ("incomplete_learning", "Incomplete learning"),
    ("feature_sampling", "Feature sampling"),
    ("observation_noise", "Observation noise"),
)


def plot(report):
    apply_style()
    cap = report["observation_caps"].index(CAP)
    parts = np.array(report["decomposition"]["weighted_risk_components"])[cap]
    positions = np.array([[0.0, 0.85], [2.1, 2.95]])
    figure, axes = plt.subplots(1, 2, figsize=(PAPER_WIDTH, 3.05), sharey=True)
    figure.subplots_adjust(left=0.085, right=0.985, bottom=0.34, top=0.78, wspace=0.17)
    for signal, (axis, title) in enumerate(
        zip(
            axes,
            ("Rare signal dominates", "Common signal dominates"),
            strict=True,
        )
    ):
        bottom = np.zeros((2, 2))
        for component, (key, label) in enumerate(COMPONENTS):
            heights = parts[signal, :, :, component]
            axis.bar(
                positions.ravel(),
                heights.ravel(),
                bottom=bottom.ravel(),
                width=0.62,
                **COMPONENT_STYLES[key],
                edgecolor=BAR_EDGE_COLOR,
                linewidth=0.35,
                label=label,
            )
            bottom += heights
        for scaling, name in enumerate(("Unscaled", "Standardized")):
            axis.text(
                positions[scaling].mean(),
                -0.20,
                name,
                transform=axis.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=8,
            )
        axis.set(
            title=title,
            xlim=(-0.5, 3.45),
            ylim=(0, 0.25),
            xticks=positions.ravel(),
            xticklabels=["Common", "Rare"] * 2,
            yticks=[0, 0.05, 0.1, 0.15, 0.2, 0.25],
        )
        axis.tick_params(axis="x", length=0)
        axis.grid(axis="y", color="0.9", linewidth=0.6)
        axis.set_axisbelow(True)
    axes[0].set_ylabel("Contribution to rare-subgroup risk")
    figure.legend(
        *axes[0].get_legend_handles_labels(), loc="upper center", ncol=3, frameon=False
    )
    save(figure, OUTPUT / "tuned-decomposition", "risk-components")


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/predictive-intro/summary.json").read_text()))
