"""Plot the saved finite-grid oracle illustration without rerunning its search."""

import json

import numpy as np
from style import (
    METHOD_LABELS,
    METHOD_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    ROOT,
    apply_style,
    plt,
    save,
)


def plot(report):
    apply_style()
    budgets = np.array(report["observation_caps"]) * report["model"]["q"]
    risk = np.array(report["risk"])
    figure, axes = plt.subplots(
        1, 2, figsize=(PAPER_WIDTH, 2.35), sharex=True, sharey=True
    )
    figure.subplots_adjust(left=0.095, right=0.98, bottom=0.23, top=0.78, wspace=0.16)
    for signal, (axis, title) in enumerate(
        zip(
            axes,
            ("(a) Rare signal dominates", "(b) Common signal dominates"),
            strict=True,
        )
    ):
        for scaling, scale in enumerate(("none", "sd")):
            style = METHOD_STYLES[scale]
            axis.plot(
                budgets,
                risk[:, signal, scaling],
                label=METHOD_LABELS[scale],
                color=style["color"],
                linestyle=style["linestyle"],
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
    axes[0].text(
        2.25,
        0.12,
        "Standardization helps",
        color=METHOD_STYLES["sd"]["color"],
        ha="center",
    )
    axes[1].text(
        2.5,
        0.14,
        "Unscaled training helps",
        color=METHOD_STYLES["none"]["color"],
        ha="center",
    )
    figure.supxlabel(r"Expected rare observations at the budget cap, $Mq$", y=0.025)
    figure.legend(
        *axes[0].get_legend_handles_labels(), loc="upper center", ncol=2, frameon=False
    )
    save(figure, OUTPUT / "predictive-intro", "tuned-rare-risk")


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/predictive-intro/summary.json").read_text()))
