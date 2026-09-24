"""Plot Mushroom sensitivity to the rate search and prediction clipping."""

import json

import numpy as np
from style import OUTPUT, PAPER_WIDTH, ROOT, apply_style, plt, save

SCALES = ("none", "sd", "damped", "variance")


def plot(report, diagnostics):
    apply_style()
    figure, axes = plt.subplots(1, 2, figsize=(PAPER_WIDTH, 2.5), layout="constrained")
    search_axis, clipping_axis = axes
    for objective, (marker, color) in enumerate((("o", "#0072B2"), ("s", "#D55E00"))):
        rows = {
            row["search"]: row["rare"]
            for row in report["contrasts"]
            if row["arm"] == "centered_fitted"
            and row["cap"] == 8192
            and row["scale"] == "sd"
            and row["reference"] == "none"
            and row["objective"] == objective
            and row["stratum"] == "all"
        }
        searches = ("practical", "expanded")
        search_axis.errorbar(
            np.arange(2) + (objective - 0.5) * 0.08,
            [rows[search]["mean"] for search in searches],
            yerr=[rows[search]["mcse"] for search in searches],
            fmt=marker + "-",
            color=color,
            linewidth=1,
            capsize=3,
            label=f"{('Aggregate', 'Rare')[objective]} validation",
        )
    search_axis.axhline(0, color="0.45", linewidth=0.8, linestyle="--")
    search_axis.set(
        xticks=range(2),
        xticklabels=("5 rates\n$10M$ work", "25 rates\n$50M$ work"),
        xlim=(-0.3, 1.3),
        ylim=(-0.013, 0.0015),
        ylabel="SD minus U: rare test loss",
        title="(a) Expanding the rate search",
    )
    search_axis.legend(loc="lower right", frameon=False, fontsize=7)

    rows = {
        row["scale"]: row
        for row in diagnostics["clipping"]
        if row["case"] == 1 and row["objective"] == 1
    }
    assert set(rows) == set(SCALES)
    for i, scale in enumerate(SCALES):
        clipping_axis.plot(
            [i - 0.1, i + 0.1],
            [
                rows[scale][treatment]["aggregate"]["mean"]
                for treatment in ("raw", "clipped")
            ],
            color="0.75",
            linewidth=1,
            zorder=1,
        )
    for i, (treatment, label, marker, color) in enumerate(
        (("raw", "Raw", "o", "#555555"), ("clipped", "Clipped", "s", "#009E73"))
    ):
        clipping_axis.errorbar(
            np.arange(4) + (i - 0.5) * 0.2,
            [rows[scale][treatment]["aggregate"]["mean"] for scale in SCALES],
            yerr=[rows[scale][treatment]["aggregate"]["mcse"] for scale in SCALES],
            fmt=marker,
            color=color,
            capsize=3,
            label=label,
        )
    clipping_axis.set(
        xticks=range(4),
        xticklabels=("U", "SD", "Damped", "Variance"),
        yscale="log",
        ylabel="Aggregate test loss (log scale)",
        xlabel="Selected by rare validation; 25 rates",
        title="(b) Clipping selected predictions",
    )
    clipping_axis.legend(loc="upper left", frameon=False, fontsize=7)
    for axis in axes:
        axis.grid(axis="y", color="0.9", linewidth=0.6)
        axis.set_axisbelow(True)
    save(figure, OUTPUT / "mushroom-final", "selected-risks")


if __name__ == "__main__":
    plot(
        json.loads(
            (ROOT / "results/mushroom/rates25/mushroom-summary-c1.json").read_text()
        ),
        json.loads((ROOT / "results/diagnostics/summary.json").read_text()),
    )
