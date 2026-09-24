"""Plot a saved signal-allocation slice as a single-column introduction figure."""

import json

import numpy as np
from style import COLUMN_WIDTH, OUTPUT, ROOT, apply_style, plt, save

COLORS = ("#0072B2", "#D55E00")
LABELS = ("Unscaled", "Standardized")


def plot(report):
    apply_style()
    model = report["model"]
    budgets = np.array(report["observation_caps"]) * model["q"]
    cap_index = int(np.argmin(abs(budgets - 2)))
    noise_index = model["noise_variances"].index(1.0)
    fractions = np.array(model["rare_signal_fractions"])
    risk = np.array(report["risk"])[cap_index, noise_index]
    gap = risk[:, 0] - risk[:, 1]
    figure, axis = plt.subplots(figsize=(COLUMN_WIDTH, 2.75))
    figure.subplots_adjust(left=0.18, right=0.96, bottom=0.24, top=0.84)
    for scaling, (label, color, linestyle) in enumerate(
        zip(LABELS, COLORS, ("--", "-"), strict=True)
    ):
        axis.plot(
            fractions,
            risk[:, scaling],
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=1.8,
        )
    axis.fill_between(
        fractions,
        risk[:, 0],
        risk[:, 1],
        where=gap < 0,
        interpolate=True,
        color=COLORS[0],
        alpha=0.1,
    )
    axis.fill_between(
        fractions,
        risk[:, 0],
        risk[:, 1],
        where=gap > 0,
        interpolate=True,
        color=COLORS[1],
        alpha=0.1,
    )
    axis.text(0.05, 0.19, "Unscaled\nhelps", color=COLORS[0], fontsize=8)
    axis.text(0.62, 0.07, "Standardization\nhelps", color=COLORS[1], fontsize=8)
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
    figure.legend(
        *axis.get_legend_handles_labels(),
        loc="upper center",
        ncol=2,
        bbox_to_anchor=(0.56, 1.0),
        frameon=False,
        handlelength=2.2,
        columnspacing=1.2,
    )
    save(figure, OUTPUT / "signal-crossing", "risk-crossing")


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/signal-allocation/summary.json").read_text()))
