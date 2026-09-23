"""Plot the final matched Mushroom search from its frozen summary."""

import json

import numpy as np
from style import OUTPUT, PAPER_WIDTH, ROOT, apply_style, plt, save

SCALES = ("none", "sd", "damped", "variance")


def plot(report):
    apply_style()
    figure, axes = plt.subplots(1, 2, figsize=(PAPER_WIDTH, 2.5), layout="constrained")
    for objective, (marker, color) in enumerate((("o", "#0072B2"), ("s", "#D55E00"))):
        rows = {
            row["scale"]: row
            for row in report["selections"]
            if row["arm"] == "centered_fitted"
            and row["cap"] == 8192
            and row["search"] == "expanded"
            and row["objective"] == objective
            and row["stratum"] == "all"
        }
        assert set(rows) == set(SCALES)
        for axis, risk in zip(axes, ("aggregate", "rare"), strict=True):
            axis.errorbar(
                np.arange(4) + (objective - 0.5) * 0.22,
                [rows[scale][risk]["mean"] for scale in SCALES],
                yerr=[rows[scale][risk]["mcse"] for scale in SCALES],
                fmt=marker,
                color=color,
                capsize=3,
                label=f"{('Aggregate', 'Rare')[objective]} validation",
            )
            axis.set(
                xticks=range(4),
                xticklabels=("None", "SD", "Damped", "Variance"),
                yscale="log",
                title=f"{risk.capitalize()} test loss",
            )
            axis.grid(axis="y", color="0.9", linewidth=0.6)
            axis.set_axisbelow(True)
    axes[0].set_ylabel("Mean half squared loss (log scale)")
    axes[0].legend(loc="upper left", frameon=False, fontsize=7)
    save(figure, OUTPUT / "mushroom-final", "selected-risks")


if __name__ == "__main__":
    plot(
        json.loads(
            (
                ROOT / "results/variance-scaling-followup/mushroom-summary-c1.json"
            ).read_text()
        )
    )
